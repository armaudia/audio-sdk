# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for StyleTTS 2.

Feasibility evidence only. Models caller-supplied-asset intake and a model-free
synthetic identity accounting control at the installed v0 geometry. Does not
import, load, link, execute, copy, vendor or download a StyleTTS 2
implementation, checkpoint, vocoder, text frontend, alignment model, dataset,
or listening panel. No real audio, listening, device timing, benchmark or
release result is claimed.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/styletts-2/caller-supplied/0.1"
SCHEMA_PLAN = "audio-sdk/styletts-2/plan/0.1"
TASK_ID = "SDK-STYLETTS-2"
TITLE = "StyleTTS 2"
COMPONENT = "styletts-2"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = "swarm/SDK-STYLETTS-2"
REVIEWER = "reviewer-STYLETTS-2"
PROFILE = "Voice"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_asset_intake_incomplete_not_qualified"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
FIXTURE_SAMPLES = 16000
MICRO_SCALE = 1_000_000
MAX_ASSET_BYTES = 512 * 1024 * 1024

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md":
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md":
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
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
}

SOURCE_LINES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "matrix-status",
        "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "line": 55,
        "text": "Voice transformation,StyleTTS 2,unavailable/blocked,No local model/checkpoint adapter; available task is expressive TTS rather than streaming source-speech enhancement.,Identity; explicit TTS/VC output task,research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md; research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
    },
    {
        "id": "space-audit",
        "path": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
        "line": 25,
        "text": "| StyleTTS 2 | researched but not run | No model/checkpoint/adaptor/results in this repo. | Authors publish research code and checkpoints; code MIT, while the README imposes voice-use/synthetic-speech conditions on pretrained models. Its published task is expressive TTS, not source-speech enhancement. [Official repo](https://github.com/yl4579/StyleTTS2), [paper](https://arxiv.org/abs/2306.07691). | No streaming input conversion established. Treat as TTS/VC research lead only; check model card and consent/voice rights, then measure full resynthesis quality and latency."
    },
    {
        "id": "trials-audit",
        "path": "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md",
        "line": 63,
        "text": "| StyleTTS 2 | No local model/checkpoint adapter; available task is expressive TTS, not streaming source-speech enhancement. | Not run; a task-matched TTS/VC benchmark and eligible checkpoint would be separate. |"
    },
    {
        "id": "voice-profile",
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "line": 22,
        "text": "| Voice | Freeze permitted input and target references, task and language/speaker groups. Preserve text and semantic content, identity/similarity and naturalness as separate outcomes. Record alignment, first-output/tail timing and the exact target condition. Consent, reference availability and output use are independent gates. |",
    },
)

BOARD_STABLE_SHA256 = "6b4e7f75379394a00da210418f3af735be6de42d44b773de055fcdc7d698f08f"
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)
TASK_PREFIX = "docs/task-evidence/styletts-2/"
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
    "network_used": False,
    "runtime_invoked": False,
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No StyleTTS 2 implementation, checkpoint, vocoder, text frontend, aligner or runtime is loaded or executed.",
    "No exact caller source, weights, runtime lock, rights record, consent record, cohort manifest or reference output is present.",
    "No real audio is read, written, rendered, played or listened to.",
    "No device timing, callback deadline, pacing, first-output or tail-latency result is measured.",
    "No source-reported StyleTTS 2 quality, naturalness, MOS, similarity or speed number is reproduced or promoted.",
    "No TTS/VC output is generated, and no streaming source-speech enhancement claim is made.",
    "No provider, descriptor, registry entry, default, ABI, shared-build or CI file is changed.",
    "No benchmark, release, public admission or qualification result is claimed.",
)

REQUIRED_ASSETS: Tuple[Dict[str, Any], ...] = (
    {"asset_id": "styletts-2.source-revision", "role": "runnable_source_revision", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "styletts-2.model-checkpoint", "role": "exact_model_checkpoint", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "styletts-2.vocoder-or-decoder", "role": "exact_vocoder_or_decoder_asset", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "styletts-2.runtime-lock", "role": "locked_runtime_and_dependencies", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "styletts-2.rights-consent", "role": "rights_and_consent_record", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "styletts-2.cohort-manifest", "role": "rights_cleared_voice_cohort_manifest", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "styletts-2.reference-output", "role": "matched_reference_output", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
)

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "schema_id", "task_id", "candidate_id", "candidate_family", "fixture_id",
    "source_revision", "source_license_id", "runtime_lock_id", "cohort_manifest_id",
    "reference_output_id", "attestation", "task_kind", "evidence_class",
    "credential_review_id", "counsel_review_id", "assets",
)
CALLER_ASSET_FIELDS: Tuple[str, ...] = (
    "asset_id", "path", "sha256", "byte_count", "storage", "license_id", "rights_attestation",
)
FIXED_ATTESTATION = (
    "caller-owned assets supplied by exact id, byte count and sha256; no SDK "
    "file access, download or default exposure"
)
ASSET_ROOT = "/caller-owned/styletts-2"
ABSENT_PREFIXES: Tuple[str, ...] = (
    "data/sources/styletts-2",
    "data/models/styletts-2",
    "data/envs/styletts-2",
    "data/reference/styletts-2",
    "data/rights/styletts-2",
    "data/runs/styletts-2",
)


class ReferenceRejection(ValueError):
    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=True)


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
    return tuple("source:" + path for path in sorted(SOURCE_PINS)) + tuple(sorted(BOUNDARY_PINS)) + local_pin_keys()


def qualify_pin_path(key: str) -> Path:
    if key.startswith("source:"):
        return SOURCE_ROOT / key.split(":", 1)[1]
    return SDK_ROOT / key


README_PATH = TASK_DIR / "README.md"


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
    for block in (text.split(start, 1)[1].split(end, 1)[0], text.split(middle, 1)[1].split(end, 1)[0]):
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
    rows = [row for row in payload["tasks"] if isinstance(row, dict) and row.get("id") == TASK_ID]
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
        payload = ("caller-supplied synthetic placeholder for " + item["asset_id"]).encode("utf-8")
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
        "candidate_family": "voice-and-synthesis",
        "fixture_id": "synthetic-16k-mono-160-frame-1s",
        "source_revision": "c" * 40,
        "source_license_id": "caller-declared-not-reviewed",
        "runtime_lock_id": "runtime-lock-shape-only",
        "cohort_manifest_id": "rights-cleared-cohort-shape-only",
        "reference_output_id": "matched-reference-output-shape-only",
        "attestation": FIXED_ATTESTATION,
        "task_kind": "offline_tts_or_vc_reference_only",
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
    if manifest["candidate_family"] != "voice-and-synthesis":
        raise ReferenceRejection("CANDIDATE_FAMILY_MISMATCH")
    for field in ("fixture_id", "source_license_id", "runtime_lock_id", "cohort_manifest_id", "reference_output_id", "credential_review_id", "counsel_review_id"):
        if not isinstance(manifest[field], str) or not manifest[field]:
            raise ReferenceRejection("IDENTIFIER_INVALID:" + field)
    if not isinstance(manifest["source_revision"], str) or re.fullmatch(r"[0-9a-f]{40}", manifest["source_revision"]) is None:
        raise ReferenceRejection("SOURCE_REVISION_INVALID")
    if manifest["attestation"] != FIXED_ATTESTATION:
        raise ReferenceRejection("ATTESTATION_INVALID")
    if manifest["task_kind"] != "offline_tts_or_vc_reference_only":
        raise ReferenceRejection("TASK_KIND_INVALID")
    if manifest["evidence_class"] != "caller_supplied_shape_only":
        raise ReferenceRejection("EVIDENCE_CLASS_INVALID")
    if manifest["credential_review_id"] == manifest["counsel_review_id"]:
        raise ReferenceRejection("EVIDENCE_CLASS_COLLISION")
    assets = manifest["assets"]
    if not isinstance(assets, list) or len(assets) != len(REQUIRED_ASSETS):
        raise ReferenceRejection("ASSET_SET_MISMATCH")
    expected_ids = [item["asset_id"] for item in REQUIRED_ASSETS]
    if sorted(asset.get("asset_id") for asset in assets if isinstance(asset, dict)) != sorted(expected_ids):
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
        checked.append({"asset_id": asset["asset_id"], "byte_count": asset["byte_count"], "sha256": asset["sha256"]})
    return {
        "assets": checked,
        "count": len(checked),
        "qualifies": False,
        "note": "Hash-matched bytes are shape-only; no source is parsed or executed.",
    }


def valid_plan() -> Dict[str, Any]:
    # Synthetic 1s control at installed v0 geometry. Not speech, not StyleTTS 2 output.
    # Fixed deterministic micro-quantized sequence: 4000 silence, 16000 voiced-like
    # periodic ramp, 4000 silence, 8000 tail silence.
    return {
        "schema_id": SCHEMA_PLAN,
        "fixture_id": "synthetic-16k-mono-160-frame-1s",
        "source_end": FIXTURE_SAMPLES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "task_kind": "offline_tts_or_vc_reference_only",
        "is_synthetic_control": True,
        "is_candidate_result": False,
        "segments": [
            {"id": "seg-00-silence", "start": 0, "end": 4000, "class": "silence"},
            {"id": "seg-01-voiced", "start": 4000, "end": 12000, "class": "voiced_synthetic"},
            {"id": "seg-02-silence", "start": 12000, "end": 16000, "class": "silence"},
        ],
    }


PLAN_FIELDS = (
    "schema_id", "fixture_id", "source_end", "sample_rate_hz", "channels",
    "frame_samples", "sample_format", "task_kind", "is_synthetic_control",
    "is_candidate_result", "segments",
)
SEGMENT_FIELDS = ("id", "start", "end", "class")


def synthetic_pcm_micro() -> List[int]:
    samples: List[int] = []
    for i in range(FIXTURE_SAMPLES):
        if i < 4000 or i >= 12000:
            samples.append(0)
        else:
            phase = (i - 4000) % 80
            # deterministic bounded ramp in [-300000, 300000] micro units
            value = ((phase * 7500) - 300000)
            samples.append(value)
    return samples


def pcm_digest(samples: List[int]) -> str:
    return sha256_bytes(canonical_bytes(samples))


def validate_plan(plan: Any) -> Dict[str, Any]:
    if not isinstance(plan, dict):
        raise ReferenceRejection("PLAN_NOT_OBJECT")
    if set(plan) != set(PLAN_FIELDS):
        raise ReferenceRejection("PLAN_FIELD_SET")
    if plan["schema_id"] != SCHEMA_PLAN:
        raise ReferenceRejection("PLAN_SCHEMA_MISMATCH")
    if plan["fixture_id"] != "synthetic-16k-mono-160-frame-1s":
        raise ReferenceRejection("FIXTURE_ID_MISMATCH")
    for field in ("source_end", "sample_rate_hz", "channels", "frame_samples"):
        if not _is_int(plan[field]):
            raise ReferenceRejection("GEOMETRY_TYPE_INVALID:" + field)
    if (plan["sample_rate_hz"], plan["channels"], plan["frame_samples"], plan["source_end"]) != (
            SAMPLE_RATE_HZ, CHANNELS, FRAME_SAMPLES, FIXTURE_SAMPLES):
        raise ReferenceRejection("GEOMETRY_MISMATCH")
    if plan["sample_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("FORMAT_MISMATCH")
    if plan["task_kind"] != "offline_tts_or_vc_reference_only":
        raise ReferenceRejection("TASK_KIND_INVALID")
    if plan["is_synthetic_control"] is not True:
        raise ReferenceRejection("SYNTHETIC_FLAG_INVALID")
    if plan["is_candidate_result"] is not False:
        raise ReferenceRejection("CANDIDATE_CLAIM")
    segments = plan["segments"]
    if not isinstance(segments, list) or not segments:
        raise ReferenceRejection("SEGMENTS_INVALID")
    rows: List[Dict[str, Any]] = []
    cursor = 0
    ids: List[str] = []
    for segment in segments:
        if not isinstance(segment, dict) or set(segment) != set(SEGMENT_FIELDS):
            raise ReferenceRejection("SEGMENT_FIELD_SET")
        seg_id = segment["id"]
        if not isinstance(seg_id, str) or not seg_id:
            raise ReferenceRejection("SEGMENT_ID_INVALID")
        if seg_id in ids:
            raise ReferenceRejection("SEGMENT_ID_DUPLICATE")
        ids.append(seg_id)
        start, end = segment["start"], segment["end"]
        if not _is_int(start) or not _is_int(end):
            raise ReferenceRejection("INTERVAL_TYPE_INVALID")
        if start != cursor:
            raise ReferenceRejection("INTERVAL_GAP_OR_OVERLAP")
        if start < 0 or end <= start or end > plan["source_end"]:
            raise ReferenceRejection("INTERVAL_RANGE_INVALID")
        label = segment["class"]
        if label not in ("silence", "voiced_synthetic"):
            raise ReferenceRejection("CONTENT_CLASS_INVALID")
        rows.append({"id": seg_id, "start": start, "end": end, "class": label, "source_samples": end - start})
        cursor = end
    if cursor != plan["source_end"]:
        raise ReferenceRejection("UNCOVERED_TAIL")
    pcm = synthetic_pcm_micro()
    digest = pcm_digest(pcm)
    return {
        "schema_id": SCHEMA_PLAN,
        "fixture_id": plan["fixture_id"],
        "task_kind": plan["task_kind"],
        "segments": rows,
        "source_end": plan["source_end"],
        "output_end": plan["source_end"],
        "duration_ratio": "1",
        "alignment": {
            "first_output_delay_samples": 0,
            "tail_samples": plan["source_end"],
            "mode": "offline_whole_utterance",
            "streaming_supported": False,
            "network_inclusive_latency_measured": False,
            "measured": False,
            "note": "Structural accounting only; no vendor/runtime/model output exists.",
        },
        "identity_control": {
            "label": "local_identity",
            "sample_count_equal": True,
            "duration_equal": True,
            "byte_digest_equal": True,
            "pcm_sha256": digest,
            "qualifies": False,
        },
        "qualifies": False,
    }


def identity_control() -> Dict[str, Any]:
    pcm = synthetic_pcm_micro()
    digest = pcm_digest(pcm)
    out = list(pcm)
    return {
        "label": "synthetic identity accounting control, not StyleTTS 2 output",
        "input_sha256": digest,
        "output_sha256": pcm_digest(out),
        "alternating_or_fixed_integer_sequence_byte_identical": digest == pcm_digest(out),
        "sample_count": FIXTURE_SAMPLES,
        "duration_ratio": "1",
        "qualifies": False,
    }


def plan_adverse_cases() -> Dict[str, Any]:
    cases: List[Tuple[str, Any, str]] = []

    def add(name: str, mutate: Any, code: str) -> None:
        cases.append((name, mutate, code))

    add("boolean_source_end", lambda p: p.update(source_end=True), "GEOMETRY_TYPE_INVALID:source_end")
    add("wrong_sample_rate", lambda p: p.update(sample_rate_hz=48000), "GEOMETRY_MISMATCH")
    add("candidate_claim", lambda p: p.update(is_candidate_result=True), "CANDIDATE_CLAIM")
    add("not_synthetic", lambda p: p.update(is_synthetic_control=False), "SYNTHETIC_FLAG_INVALID")
    add("extra_field", lambda p: p.update(extra="x"), "PLAN_FIELD_SET")
    add("missing_field", lambda p: p.pop("task_kind"), "PLAN_FIELD_SET")
    add("bad_task_kind", lambda p: p.update(task_kind="streaming_enhancement"), "TASK_KIND_INVALID")
    add("empty_segments", lambda p: p.update(segments=[]), "SEGMENTS_INVALID")
    add("gap", lambda p: p["segments"][1].update(start=4100), "INTERVAL_GAP_OR_OVERLAP")
    add("overlap", lambda p: p["segments"][2].update(start=11900), "INTERVAL_GAP_OR_OVERLAP")
    add("uncovered_tail", lambda p: p.update(segments=p["segments"][:2]), "UNCOVERED_TAIL")
    add("zero_length", lambda p: p["segments"][1].update(end=4000), "INTERVAL_RANGE_INVALID")
    add("duplicate_id", lambda p: p["segments"][1].update(id="seg-00-silence"), "SEGMENT_ID_DUPLICATE")
    add("unsupported_class", lambda p: p["segments"][1].update(**{"class": "speech_real"}), "CONTENT_CLASS_INVALID")

    results: List[Dict[str, Any]] = []
    for name, mutate, expected in cases:
        candidate = valid_plan()
        mutate(candidate)
        actual = "NOT_REJECTED"
        try:
            validate_plan(candidate)
        except ReferenceRejection as error:
            actual = error.code
        results.append({"id": name, "expected_code": expected, "actual_code": actual, "rejected": actual != "NOT_REJECTED"})
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
    add("short_revision", lambda m: m.update(source_revision="c" * 39), "SOURCE_REVISION_INVALID")
    add("bad_attestation", lambda m: m.update(attestation="unchecked"), "ATTESTATION_INVALID")
    add("bad_task_kind", lambda m: m.update(task_kind="streaming_enhancement"), "TASK_KIND_INVALID")
    add("wrong_evidence_class", lambda m: m.update(evidence_class="benchmark"), "EVIDENCE_CLASS_INVALID")
    add("colliding_review_ids", lambda m: m.update(counsel_review_id=m["credential_review_id"]), "EVIDENCE_CLASS_COLLISION")
    add("missing_asset", lambda m: m["assets"].pop(), "ASSET_SET_MISMATCH")
    add("extra_asset", lambda m: m["assets"].append(dict(m["assets"][0])), "ASSET_SET_MISMATCH")
    add("relative_path", lambda m: m["assets"][0].update(path="relative/file.bin"), "ASSET_PATH_NOT_ABSOLUTE")
    add("traversal_path", lambda m: m["assets"][0].update(path="/caller-owned/../escape.bin"), "ASSET_PATH_TRAVERSAL")
    add("duplicate_path", lambda m: m["assets"][1].update(path=m["assets"][0]["path"]), "ASSET_PATH_DUPLICATE")
    add("uppercase_hash", lambda m: m["assets"][0].update(sha256="C" * 64), "ASSET_SHA256_INVALID")
    add("short_hash", lambda m: m["assets"][0].update(sha256="c" * 63), "ASSET_SHA256_INVALID")
    add("zero_byte_count", lambda m: m["assets"][0].update(byte_count=0), "ASSET_BYTE_COUNT_INVALID")
    add("oversize_byte_count", lambda m: m["assets"][0].update(byte_count=MAX_ASSET_BYTES + 1), "ASSET_BYTE_COUNT_INVALID")
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
        results.append({"id": name, "expected_code": expected, "actual_code": actual, "rejected": actual != "NOT_REJECTED"})
    for row in results:
        if row["actual_code"] != row["expected_code"]:
            raise ReferenceRejection("ADVERSE_CODE_MISMATCH:" + row["id"])
    manifest = valid_manifest()
    absent_code = mismatch_code = size_code = "NOT_REJECTED"
    try:
        verify_assets(manifest, {})
    except ReferenceRejection as error:
        absent_code = error.code
    payloads = {asset["path"]: b"x" * asset["byte_count"] for asset in manifest["assets"]}
    try:
        verify_assets(manifest, payloads)
    except ReferenceRejection as error:
        mismatch_code = error.code
    matched = {asset["path"]: ("caller-supplied synthetic placeholder for " + asset["asset_id"]).encode("utf-8") for asset in manifest["assets"]}
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
    samples = ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1} extra', "")
    results = []
    for index, text in enumerate(samples):
        rejected = False
        try:
            strict_loads(text)
        except ValueError:
            rejected = True
        results.append({"id": "json-" + str(index), "rejected": rejected})
    return {"cases": results, "case_count": len(results), "accepted_count": sum(1 for row in results if not row["rejected"]), "all_rejected": all(row["rejected"] for row in results)}


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
    return {"cases": results, "case_count": len(results), "accepted_count": sum(1 for row in results if not row["rejected"]), "all_rejected": all(row["rejected"] for row in results)}


def voice_profile() -> Dict[str, Any]:
    rows = [
        ("permitted_references", "Freeze permitted input and target references, task and language/speaker groups", "not_present"),
        ("text_semantic_preservation", "Preserve text and semantic content as a separate outcome", "not_measured"),
        ("identity_similarity", "Measure identity/similarity as a separate outcome", "not_measured"),
        ("naturalness", "Measure naturalness as a separate outcome", "not_measured"),
        ("alignment_timing", "Record alignment, first-output/tail timing and exact target condition", "structural_only_not_measured"),
        ("consent_reference_output_use", "Consent, reference availability and output use are independent gates", "not_cleared"),
    ]
    return {
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md:22",
        "items": [
            {"id": item_id, "requirement": requirement, "status": "blocked", "synthetic_control": control, "qualifies": False}
            for item_id, requirement, control in rows
        ],
        "item_count": len(rows),
        "qualifies": False,
    }


GATES: Tuple[Dict[str, Any], ...] = (
    {"id": "RG-01", "name": "exact_runnable_source", "status": "blocked", "qualifies": False, "missing": "exact StyleTTS 2 source revision and build/runtime lock"},
    {"id": "RG-02", "name": "exact_assets_and_rights", "status": "blocked", "qualifies": False, "missing": "seven caller assets with SHA-256, byte count, license, consent and output-use review"},
    {"id": "RG-03", "name": "installed_v0_boundary", "status": "blocked", "qualifies": False, "missing": "opt-in intake without ABI, registry or default change"},
    {"id": "RG-04", "name": "permitted_voice_cohort", "status": "blocked", "qualifies": False, "missing": "rights-cleared permitted input/target references and cohort manifest"},
    {"id": "RG-05", "name": "text_semantic_identity_naturalness", "status": "blocked", "qualifies": False, "missing": "separate text/semantic, identity/similarity and naturalness results"},
    {"id": "RG-06", "name": "alignment_and_timing", "status": "blocked", "qualifies": False, "missing": "alignment, first-output/tail timing and exact target condition evidence"},
    {"id": "RG-07", "name": "streaming_source_speech_claim_gate", "status": "blocked", "qualifies": False, "missing": "no streaming source-speech enhancement claim allowed without a separate task-matched benchmark"},
    {"id": "RG-08", "name": "public_admission_review", "status": "blocked", "qualifies": False, "missing": "rights, consent, counsel and opt-in release decision"},
)

EXACT_BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "B-01",
        "blocker": "No exact runnable StyleTTS 2 implementation exists locally. The pinned research records identify StyleTTS 2 as expressive TTS with no local model/checkpoint adapter or streaming source-speech enhancement task match.",
        "reopen": "Supply a 40-hex source revision, exact source archive hash, build/runtime lock and caller attestation through the manifest; verify hashes without downloading or executing source here.",
    },
    {
        "id": "B-02",
        "blocker": "No exact rights-cleared assets exist: source, model checkpoint, vocoder/decoder, runtime lock, rights/consent record, cohort manifest and matched reference output each lack byte count, SHA-256, licence and consent/output-use review.",
        "reopen": "Caller supplies all seven external assets by id, byte count and SHA-256 with reviewed licence, voice consent and output-use sidecars and verified bytes; no embedded asset or SDK file access is accepted.",
    },
    {
        "id": "B-03",
        "blocker": "No matched Voice-profile evidence exists. The package has no real audio, no TTS/VC output, no text/semantic, identity/similarity or naturalness result, no listening and no alignment/first-output/tail timing measurement.",
        "reopen": "Run a rights-cleared matched cohort for the exact declared task kind and report text/semantic preservation, identity/similarity, naturalness, alignment and first-output/tail timing as separate outcomes.",
    },
    {
        "id": "B-04",
        "blocker": "No opt-in adapter intake or release decision exists, and StyleTTS 2 cannot be treated as a streaming source-speech enhancement component without a separate task-matched benchmark.",
        "reopen": "Obtain credential review, counsel posture and an application-local opt-in decision with no default, public registry or ABI change; keep public admission a separate later gate and do not claim streaming enhancement.",
    },
)

SOURCE_REPORTED: Dict[str, Any] = {
    "qualifies": False,
    "entries": [
        {"id": "SR-01", "claim": "StyleTTS 2 is unavailable/blocked locally with no model/checkpoint adapter; available task is expressive TTS rather than streaming source-speech enhancement", "source": "research/voice-enhancement-20261101/candidate_matrix.csv:55"},
        {"id": "SR-02", "claim": "StyleTTS 2 has no local model/checkpoint/adaptor; published task is expressive TTS, not source-speech enhancement", "source": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md:29"},
        {"id": "SR-03", "claim": "StyleTTS 2 not run; a task-matched TTS/VC benchmark and eligible checkpoint would be separate", "source": "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md:67"},
    ],
    "separation": "All entries are source-reported provenance. None is reproduced, pooled with the synthetic control or promoted to a candidate result.",
}


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    plan = validate_plan(valid_plan())
    probe = absent_artifact_probe()
    manifest_adverse = manifest_adverse_cases()
    plan_adverse = plan_adverse_cases()
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
        "synthetic_plan": plan,
        "identity_control": identity_control(),
        "voice_profile": voice_profile(),
        "asset_resolution": probe,
        "adverse": {
            "caller_manifest": manifest_adverse,
            "synthetic_plan": plan_adverse,
            "invalid_json": json_adverse,
            "invalid_pins": pin_adverse,
            "all_rejected": manifest_adverse["all_rejected"] and plan_adverse["all_rejected"] and json_adverse["all_rejected"] and pin_adverse["all_rejected"],
            "metrics": None,
        },
        "source_reported": dict(SOURCE_REPORTED),
        "source_lines": source_lines(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "exact StyleTTS 2 source revision, archive hash and build/runtime lock",
            "seven exact external assets with byte counts, SHA-256 and rights/consent/output-use sidecars",
            "rights-cleared permitted input/target references and cohort manifest",
            "separate text/semantic preservation, identity/similarity and naturalness results",
            "alignment, first-output/tail timing and exact target condition evidence",
            "opt-in credential/counsel review and a separate streaming claim gate if ever proposed",
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


def contract_bytes(report_payload: bytes, sidecar_payload: bytes, sources_payload: bytes, report: Dict[str, Any] | None = None) -> bytes:
    report = report or strict_loads(report_payload.decode("utf-8"))
    contract = {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": report["task_id"],
        "title": report["title"],
        "component_id": report["component_id"],
        "repository": report["repository"],
        "base_commit": report["base_commit"],
        "branch": report["branch"],
        "profile": report["profile"],
        "decision": report["decision"],
        "defer_before": report["defer_before"],
        "evidence_status": report["evidence_status"],
        "qualification_status": report["qualification_status"],
        "status": report["status"],
        "format": report["format"],
        "boundary": report["boundary"],
        "scope": report["scope"],
        "gates": report["gates"],
        "exact_blockers": report["exact_blockers"],
        "negative_claims": report["negative_claims"],
        "board_link": report["board_link"],
        "caller_supplied_asset_contract": report["caller_supplied_asset_contract"],
        "source_reported": report["source_reported"],
        "report_sha256": sha256_bytes(report_payload),
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "sources_sha256": sha256_bytes(sources_payload),
        "source_pins": report["source_pins"],
        "boundary_pins": report["boundary_pins"],
        "artifact_pins": {
            "docs/task-evidence/styletts-2/" + path.name: (sha256_bytes(report_payload) if path.name == "report.json.sha256" else sha256_file(path))
            for path in sorted(TASK_DIR.iterdir())
            if path.is_file() and path.name not in {"report.json", "contract.json", "SOURCES.sha256"}
        },
    }
    return canonical_bytes(contract)


def sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    rows: List[Tuple[str, str]] = []
    for path in sorted(SOURCE_PINS):
        rows.append(("source:" + path, sha256_file(SOURCE_ROOT / path)))
    for path in sorted(BOUNDARY_PINS):
        rows.append((path, sha256_file(SDK_ROOT / path)))
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            rows.append((TASK_PREFIX + name, sha256_bytes(report_payload)))
        elif name == "report.json.sha256":
            rows.append((TASK_PREFIX + name, sha256_bytes(sidecar_payload)))
        elif name in {"contract.json", "SOURCES.sha256"}:
            continue
        else:
            rows.append((TASK_PREFIX + name, sha256_file(TASK_DIR / name)))
    return ("".join(digest + "  " + key + "\n" for key, digest in rows)).encode("ascii")


def scope_base(repo: Path, refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    newest: Tuple[int, str] | None = None
    for ref in refs:
        probe = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", ref], capture_output=True, text=True)
        if probe.returncode != 0:
            continue
        merge_base = subprocess.run(["git", "-C", str(repo), "merge-base", "HEAD", ref], capture_output=True, text=True)
        if merge_base.returncode != 0:
            continue
        base = merge_base.stdout.strip()
        count = subprocess.run(["git", "-C", str(repo), "rev-list", "--count", base + "..HEAD"], capture_output=True, text=True)
        if count.returncode != 0:
            continue
        rank = int(count.stdout.strip())
        if newest is None or rank < newest[0]:
            newest = (rank, base)
    return None if newest is None else newest[1]


def scope_changed_paths(repo: Path, base: str) -> List[str]:
    result = subprocess.run(["git", "-C", str(repo), "diff", "--name-only", base + "..HEAD"], capture_output=True, text=True, check=True)
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(changed: List[str], prefix: str = TASK_PREFIX) -> List[str]:
    return [path for path in changed if not path.startswith(prefix)]


def git_diff_check(repo: Path) -> List[str]:
    result = subprocess.run(["git", "-C", str(repo), "diff", "--check"], capture_output=True, text=True)
    if result.returncode == 0:
        return []
    return [line for line in (result.stdout + result.stderr).splitlines() if line.strip()]
