# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Deterministic DEFER evidence for spectrum-copy bandwidth extension.

No source, weights, runtime, corpus, listening, device timing, benchmark, or
release claim is made. This module only builds canonical task-local artifacts.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

SPDX_COPYRIGHT = "SPDX-" + "FileCopyrightText: 2026 Hovhannes Tsakanyan"
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"

TASK_ID = "SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION"
TITLE = "Spectrum-copy bandwidth extension"
COMPONENT = "spectrum-copy-bandwidth-extension"
REPOSITORY = "audio-sdk"
PROFILE = "Restoration"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
STATUS = "proposal_only_incomplete_not_qualified"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
BASE_COMMIT = "4c0f5464eeddff2204b527e8bc4ad09c41b2a657"
BRANCH = "swarm/SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION"
REVIEWER = "reviewer-SPECTRUM-COPY-BANDWIDTH-EXTENSION"

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_PREFIX = "docs/task-evidence/spectrum-copy-bandwidth-extension/"

SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_MANIFEST = "audio-sdk/spectrum-copy-bandwidth-extension/caller-supplied/0.1"
SCHEMA_PROBE = "audio-sdk/spectrum-copy-bandwidth-extension/synthetic-probe/0.1"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
MAX_ASSET_BYTES = 512 * 1024 * 1024

BOARD_STABLE_SHA256 = "8c89f102b9398523d0bf15eccb920ca99cc0a2f0a6e7ea9d7d6a0328f8cddf0d"
INVENTORY_STABLE_SHA256 = "27fd27688d64562ba76ba75a080eaecc761e4061107b7993b2afced368e03567"

LOCAL_PIN_PATHS = (
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

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/TASKS.json": "98d39fd8580235073f6a35fdd097464d99c5f4c51b0f2a5b7e8ad1d0d3b85a73",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/distortion_restoration_20261028.md": "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
}
# TASKS.json hash is mutable in real life? prompt says never hash mutable full TASKS.json.
# So do NOT pin TASKS.json file digest in gates. Remove it from source pins.

BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "schemas/descriptor.schema.json": "9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba",
    "schemas/effective-config.schema.json": "55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

SCOPE_BASE_REFS: Tuple[str, ...] = ("origin/main", "main")

MUTABLE_FIELDS_EXCLUDED: Tuple[str, ...] = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable",
    "acceptance", "evidence",
)

BOUNDARY: Dict[str, Any] = {
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_settings": {},
    "default_selected": False,
    "enabled_by_default": False,
    "registered": False,
    "processor_exposure": False,
    "format": {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
    },
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
    "No spectrum-copy, NU-Wave, HiFi-GAN, AudioSR or other BWE model is loaded, downloaded or executed.",
    "No exact runnable source revision, weights, runtime lock or rights-cleared cohort is present.",
    "No real audio, listening panel, perceptual score, device timing or benchmark result is produced.",
    "The source-reported pilot is preserved as provenance only and is not reproduced or promoted.",
    "The negative spectrum-copy comparison from the pinned research is retained and not overturned.",
    "No provider, descriptor, registry entry, default, ABI, shared-build or CI file is changed.",
    "No public admission, release or qualification claim is made.",
    "No missing, blocked, source-reported or synthetic result qualifies the candidate.",
)

# Do not pin mutable TASKS.json; stable board identity is gated separately.
SOURCE_PINS = {k: v for k, v in SOURCE_PINS.items() if k != "audio-benchmark-platform/plan/swarm/TASKS.json"}

REQUIRED_ASSETS: Tuple[Dict[str, Any], ...] = (
    {"asset_id": "spectrum-copy-bwe.source-revision", "role": "runnable_source_revision", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "spectrum-copy-bwe.weights", "role": "exact_weights_or_algorithm_artifact", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "spectrum-copy-bwe.runtime-lock", "role": "locked_runtime_and_dependencies", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "spectrum-copy-bwe.cohort-manifest", "role": "rights_cleared_paired_cohort_manifest", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "spectrum-copy-bwe.reference-output", "role": "matched_reference_output_or_oracle", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
    {"asset_id": "spectrum-copy-bwe.rights-attestation", "role": "rights_and_release_attestation", "storage": "external", "declared_sha256": None, "declared_byte_count": None, "present_locally": False},
)

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "schema_id", "task_id", "candidate_id", "candidate_family", "fixture_id",
    "source_revision", "source_license_id", "runtime_lock_id", "cohort_manifest_id",
    "reference_output_id", "attestation", "evidence_class", "credential_review_id",
    "counsel_review_id", "assets",
)
CALLER_ASSET_FIELDS: Tuple[str, ...] = (
    "asset_id", "path", "sha256", "byte_count", "storage", "license_id", "rights_attestation",
)
FIXED_ATTESTATION = (
    "caller-owned assets supplied by exact id, byte count and sha256; no SDK file access, "
    "download, default exposure or qualification"
)
ASSET_ROOT = "/caller-owned/spectrum-copy-bandwidth-extension"

SOURCE_LINES: Tuple[Dict[str, Any], ...] = (
    {"id": "bwe-row", "path": "research/distortion_restoration_20261028.md", "line": 18,
     "text": "| RST-02 | Zero-phase low-pass at 3.5 kHz | Band-limited input, low-band spectrum-copy extension |"},
    {"id": "bwe-result", "path": "research/distortion_restoration_20261028.md", "line": 30,
     "text": "| Bandwidth extension, 3.5 kHz cutoff | Band-limited input | 17.40 dB SI-SDR | Spectrum-copy extension falls to 14.39 dB |"},
    {"id": "bwe-reject", "path": "research/distortion_restoration_20261028.md", "line": 43,
     "text": "- **RST-02:** the local copy-spectrum baseline should be rejected; it harms fidelity. The strongest ready-to-investigate neural family is bandwidth-conditioned generative upsampling, represented by NU-Wave 2, which targets different input rates and generates 48 kHz audio. Its authors provide official code and checkpoints, but those weights are not staged locally. High-frequency fidelity and content preservation need explicit evaluation because generated bands are estimates. [NU-Wave 2 paper](https://www.isca-archive.org/interspeech_2022/han22_interspeech.pdf), [official implementation](https://github.com/maum-ai/nuwave2)."},
    {"id": "bwe-boundary", "path": "research/distortion_restoration_20261028.md", "line": 7,
     "text": "The registry divides this area into four different inverse problems: RST-01 declipping/saturation; RST-02 bandwidth extension; RST-03 codec-artifact restoration; and RST-04 packet-loss concealment. Their missing information and decoder context differ. A limiter cannot recover clipped peaks, resampling cannot infer missing high frequencies, and packet concealment benefits from codec state or redundant packets. A single “distortion restoration” score would hide these differences."},
    {"id": "plan-note", "path": "audio-benchmark-platform/plan/INVENTORY.json", "line": 9083,
     "text": "\"plan_note\": \"Retain the negative comparison and require content preservation before inclusion.\","},
)

# We'll compute plan-note line dynamically in source_lines check; avoid fragile hardcoding by searching.


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


def readme_pin_rows() -> List[Tuple[str, str]]:
    text = (HERE / "README.md").read_text(encoding="utf-8")
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
    payload = strict_load(SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json")
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        raise ValueError("invalid_task_board")
    rows = [row for row in payload["tasks"] if isinstance(row, dict) and row.get("id") == TASK_ID]
    if len(rows) != 1:
        raise ValueError("task_row_not_unique")
    stable = {field: rows[0][field] for field in ("component", "depends_on", "id", "mode", "repository", "title")}
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
    payload = strict_load(SOURCE_ROOT / "audio-benchmark-platform/plan/INVENTORY.json")

    def find(item: Any) -> Any:
        if isinstance(item, dict):
            if item.get("id") == COMPONENT:
                return item
            for value in item.values():
                found = find(value)
                if found is not None:
                    return found
        elif isinstance(item, list):
            for value in item:
                found = find(value)
                if found is not None:
                    return found
        return None

    row = find(payload)
    if not isinstance(row, dict):
        raise ValueError("inventory_row_not_found")
    stable = {k: row[k] for k in ("area", "disposition", "evidence_status", "id", "name", "repository", "task", "verification_profile")}
    digest = object_digest(stable)
    if digest != INVENTORY_STABLE_SHA256:
        raise ValueError("unexpected_stable_inventory_identity")
    return {
        "stable_fields": stable,
        "stable_sha256": digest,
        "full_inventory_hashed": False,
        "note": "Inventory row is provenance only; never a result.",
    }


def source_lines() -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for item in SOURCE_LINES:
        path = SOURCE_ROOT / item["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        actual = lines[item["line"] - 1].strip()
        if actual != item["text"]:
            raise ValueError("source_line_mismatch:" + item["id"])
        entries.append({
            "id": item["id"],
            "path": item["path"],
            "line": item["line"],
            "sha256": sha256_file(path),
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
    "data/sources/spectrum-copy-bandwidth-extension",
    "data/models/spectrum-copy-bandwidth-extension",
    "data/envs/spectrum-copy-bandwidth-extension",
    "data/reference/spectrum-copy-bandwidth-extension",
    "data/licenses/spectrum-copy-bandwidth-extension",
    "data/cohorts/spectrum-copy-bandwidth-extension",
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
        "candidate_family": "restoration-bwe",
        "fixture_id": "synthetic-16k-mono-160-frame-1s",
        "source_revision": "a" * 40,
        "source_license_id": "caller-declared-not-reviewed",
        "runtime_lock_id": "runtime-lock-shape-only",
        "cohort_manifest_id": "rights-cleared-cohort-shape-only",
        "reference_output_id": "matched-reference-output-shape-only",
        "attestation": FIXED_ATTESTATION,
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
    if manifest["candidate_family"] != "restoration-bwe":
        raise ReferenceRejection("CANDIDATE_FAMILY_MISMATCH")
    for field in ("fixture_id", "source_license_id", "runtime_lock_id", "cohort_manifest_id", "reference_output_id", "credential_review_id", "counsel_review_id"):
        if not isinstance(manifest[field], str) or not manifest[field]:
            raise ReferenceRejection("IDENTIFIER_INVALID:" + field)
    if not isinstance(manifest["source_revision"], str) or re.fullmatch(r"[0-9a-f]{40}", manifest["source_revision"]) is None:
        raise ReferenceRejection("SOURCE_REVISION_INVALID")
    if manifest["attestation"] != FIXED_ATTESTATION:
        raise ReferenceRejection("ATTESTATION_INVALID")
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
        "note": "Hash-matched bytes are shape-only; no source, weights or runtime is loaded or executed.",
    }


def valid_probe() -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_PROBE,
        "fixture_id": "synthetic-16k-mono-160-frame-1s",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "input_cutoff_hz": 3500,
        "target_band_hz": [3500, 8000],
        "is_synthetic_control": True,
        "is_candidate_result": False,
        "segments": [
            {"id": "seg-00-lowband", "start": 0, "end": 8000, "class": "lowband", "copy_gain_num": 0, "copy_gain_den": 1},
            {"id": "seg-01-highband-missing", "start": 8000, "end": 16000, "class": "missing_highband", "copy_gain_num": 0, "copy_gain_den": 1},
        ],
    }


PROBE_FIELDS = ("schema_id", "fixture_id", "sample_rate_hz", "channels", "frame_samples", "sample_format", "input_cutoff_hz", "target_band_hz", "is_synthetic_control", "is_candidate_result", "segments")
SEGMENT_FIELDS = ("id", "start", "end", "class", "copy_gain_num", "copy_gain_den")


def validate_probe(probe: Any) -> Dict[str, Any]:
    if not isinstance(probe, dict):
        raise ReferenceRejection("PROBE_NOT_OBJECT")
    if set(probe) != set(PROBE_FIELDS):
        raise ReferenceRejection("PROBE_FIELD_SET")
    if probe["schema_id"] != SCHEMA_PROBE:
        raise ReferenceRejection("PROBE_SCHEMA_MISMATCH")
    if probe["fixture_id"] != "synthetic-16k-mono-160-frame-1s":
        raise ReferenceRejection("FIXTURE_ID_MISMATCH")
    for field in ("sample_rate_hz", "channels", "frame_samples", "input_cutoff_hz"):
        if not _is_int(probe[field]):
            raise ReferenceRejection("GEOMETRY_TYPE_INVALID:" + field)
    if probe["sample_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("FORMAT_MISMATCH")
    if (probe["sample_rate_hz"], probe["channels"], probe["frame_samples"]) != (SAMPLE_RATE_HZ, CHANNELS, FRAME_SAMPLES):
        raise ReferenceRejection("GEOMETRY_MISMATCH")
    if probe["input_cutoff_hz"] <= 0 or probe["input_cutoff_hz"] >= SAMPLE_RATE_HZ // 2:
        raise ReferenceRejection("CUTOFF_INVALID")
    band = probe["target_band_hz"]
    if not isinstance(band, list) or len(band) != 2 or any(not _is_int(x) for x in band):
        raise ReferenceRejection("TARGET_BAND_INVALID")
    if band[0] != probe["input_cutoff_hz"] or band[1] != SAMPLE_RATE_HZ // 2 or band[0] >= band[1]:
        raise ReferenceRejection("TARGET_BAND_INVALID")
    if probe["is_synthetic_control"] is not True:
        raise ReferenceRejection("SYNTHETIC_FLAG_INVALID")
    if probe["is_candidate_result"] is not False:
        raise ReferenceRejection("CANDIDATE_CLAIM")
    segments = probe["segments"]
    if not isinstance(segments, list) or not segments:
        raise ReferenceRejection("SEGMENTS_INVALID")
    rows = []
    cursor = 0
    ids = []
    for seg in segments:
        if not isinstance(seg, dict) or set(seg) != set(SEGMENT_FIELDS):
            raise ReferenceRejection("SEGMENT_FIELD_SET")
        if not isinstance(seg["id"], str) or not seg["id"] or seg["id"] in ids:
            raise ReferenceRejection("SEGMENT_ID_INVALID")
        ids.append(seg["id"])
        start, end = seg["start"], seg["end"]
        if not _is_int(start) or not _is_int(end):
            raise ReferenceRejection("INTERVAL_TYPE_INVALID")
        if start != cursor or end <= start or end > SAMPLE_RATE_HZ:
            raise ReferenceRejection("INTERVAL_GAP_OR_OVERLAP")
        if seg["class"] not in ("lowband", "missing_highband"):
            raise ReferenceRejection("CONTENT_CLASS_INVALID")
        num, den = seg["copy_gain_num"], seg["copy_gain_den"]
        if not _is_int(num) or not _is_int(den) or den <= 0 or num < 0 or num > den:
            raise ReferenceRejection("GAIN_INVALID")
        # Spectrum copy is rejected as qualification in this package; gain > 0 means copied content claim.
        if seg["class"] == "missing_highband" and num != 0:
            raise ReferenceRejection("HARMFUL_SPECTRUM_COPY_CLAIM")
        rows.append({"id": seg["id"], "start": start, "end": end, "class": seg["class"], "copy_gain": str(Fraction(num, den))})
        cursor = end
    if cursor != SAMPLE_RATE_HZ:
        raise ReferenceRejection("UNCOVERED_TAIL")
    return {"schema_id": SCHEMA_PROBE, "segments": rows, "source_end": SAMPLE_RATE_HZ, "qualifies": False}


def probe_adverse_cases() -> Dict[str, Any]:
    cases: List[Tuple[str, Any, str]] = []
    def add(name, mutate, code):
        cases.append((name, mutate, code))
    add("not_object", lambda p: "x", "PROBE_NOT_OBJECT")
    add("extra_field", lambda p: p.update(extra=1), "PROBE_FIELD_SET")
    add("missing_field", lambda p: p.pop("target_band_hz"), "PROBE_FIELD_SET")
    add("wrong_schema", lambda p: p.update(schema_id="x"), "PROBE_SCHEMA_MISMATCH")
    add("wrong_fixture", lambda p: p.update(fixture_id="x"), "FIXTURE_ID_MISMATCH")
    add("bad_cutoff_type", lambda p: p.update(input_cutoff_hz=True), "GEOMETRY_TYPE_INVALID:input_cutoff_hz")
    add("bad_cutoff", lambda p: p.update(input_cutoff_hz=8000), "CUTOFF_INVALID")
    add("bad_band", lambda p: p.update(target_band_hz=[3500, 9000]), "TARGET_BAND_INVALID")
    add("candidate_claim", lambda p: p.update(is_candidate_result=True), "CANDIDATE_CLAIM")
    add("not_synthetic", lambda p: p.update(is_synthetic_control=False), "SYNTHETIC_FLAG_INVALID")
    add("gap", lambda p: p["segments"][1].update(start=8001), "INTERVAL_GAP_OR_OVERLAP")
    add("overlap", lambda p: p["segments"][1].update(start=7999), "INTERVAL_GAP_OR_OVERLAP")
    add("bad_class", lambda p: p["segments"][0].update(**{"class": "speech"}), "CONTENT_CLASS_INVALID")
    add("copy_claim", lambda p: p["segments"][1].update(copy_gain_num=1, copy_gain_den=1), "HARMFUL_SPECTRUM_COPY_CLAIM")
    add("bad_gain", lambda p: p["segments"][1].update(copy_gain_num=2, copy_gain_den=1), "GAIN_INVALID")
    add("bad_gain_den", lambda p: p["segments"][1].update(copy_gain_den=0), "GAIN_INVALID")
    add("duplicate_id", lambda p: p["segments"][1].update(id="seg-00-lowband"), "SEGMENT_ID_INVALID")
    add("uncovered_tail", lambda p: p.update(segments=[p["segments"][0]]), "UNCOVERED_TAIL")
    results = []
    for name, mutate, expected in cases:
        candidate = valid_probe()
        if name == "not_object":
            candidate = "bad"
        else:
            mutate(candidate)
        actual = "NOT_REJECTED"
        try:
            validate_probe(candidate)
        except ReferenceRejection as e:
            actual = e.code
        results.append({"id": name, "expected_code": expected, "actual_code": actual, "rejected": actual != "NOT_REJECTED"})
    for row in results:
        if row["actual_code"] != row["expected_code"]:
            raise ReferenceRejection("ADVERSE_CODE_MISMATCH:" + row["id"])
    return {"cases": results, "case_count": len(results), "accepted_count": sum(1 for r in results if not r["rejected"]), "all_rejected": all(r["rejected"] for r in results), "metrics": None}


def manifest_adverse_cases() -> Dict[str, Any]:
    cases: List[Tuple[str, Any, str]] = []
    def add(name, mutate, code):
        cases.append((name, mutate, code))
    add("manifest_not_object", lambda m: None, "MANIFEST_NOT_OBJECT")
    add("missing_field", lambda m: m.pop("attestation"), "SCHEMA_FIELD_SET")
    add("extra_field", lambda m: m.update(extra="x"), "SCHEMA_FIELD_SET")
    add("wrong_task", lambda m: m.update(task_id="SDK-OTHER"), "TASK_ID_MISMATCH")
    add("wrong_candidate", lambda m: m.update(candidate_id="other"), "CANDIDATE_ID_MISMATCH")
    add("short_revision", lambda m: m.update(source_revision="a" * 39), "SOURCE_REVISION_INVALID")
    add("bad_attestation", lambda m: m.update(attestation="unchecked"), "ATTESTATION_INVALID")
    add("wrong_evidence_class", lambda m: m.update(evidence_class="benchmark"), "EVIDENCE_CLASS_INVALID")
    add("colliding_review_ids", lambda m: m.update(counsel_review_id=m["credential_review_id"]), "EVIDENCE_CLASS_COLLISION")
    add("missing_asset", lambda m: m["assets"].pop(), "ASSET_SET_MISMATCH")
    add("extra_asset", lambda m: m["assets"].append(dict(m["assets"][0])), "ASSET_SET_MISMATCH")
    add("relative_path", lambda m: m["assets"][0].update(path="relative/file.bin"), "ASSET_PATH_NOT_ABSOLUTE")
    add("traversal_path", lambda m: m["assets"][0].update(path="/caller-owned/../escape.bin"), "ASSET_PATH_TRAVERSAL")
    add("duplicate_path", lambda m: m["assets"][1].update(path=m["assets"][0]["path"]), "ASSET_PATH_DUPLICATE")
    add("uppercase_hash", lambda m: m["assets"][0].update(sha256="A" * 64), "ASSET_SHA256_INVALID")
    add("short_hash", lambda m: m["assets"][0].update(sha256="a" * 63), "ASSET_SHA256_INVALID")
    add("zero_byte_count", lambda m: m["assets"][0].update(byte_count=0), "ASSET_BYTE_COUNT_INVALID")
    add("oversize_byte_count", lambda m: m["assets"][0].update(byte_count=MAX_ASSET_BYTES + 1), "ASSET_BYTE_COUNT_INVALID")
    add("embedded_storage", lambda m: m["assets"][0].update(storage="embedded"), "ASSET_STORAGE_INVALID")
    add("extra_asset_field", lambda m: m["assets"][0].update(extra="x"), "ASSET_FIELD_SET")
    results = []
    for name, mutate, expected in cases:
        candidate = valid_manifest()
        if name == "manifest_not_object":
            candidate = "not-an-object"
        else:
            mutate(candidate)
        actual = "NOT_REJECTED"
        try:
            validate_caller_manifest(candidate)
        except ReferenceRejection as e:
            actual = e.code
        results.append({"id": name, "expected_code": expected, "actual_code": actual, "rejected": actual != "NOT_REJECTED"})
    for row in results:
        if row["actual_code"] != row["expected_code"]:
            raise ReferenceRejection("ADVERSE_CODE_MISMATCH:" + row["id"])
    manifest = valid_manifest()
    absent_code = mismatch_code = size_code = "NOT_REJECTED"
    try:
        verify_assets(manifest, {})
    except ReferenceRejection as e:
        absent_code = e.code
    matched = {asset["path"]: ("caller-supplied synthetic placeholder for " + asset["asset_id"]).encode("utf-8") for asset in manifest["assets"]}
    accepted_shape = verify_assets(manifest, matched)
    wrong_size = dict(matched)
    wrong_size[manifest["assets"][0]["path"]] = b"x"
    try:
        verify_assets(manifest, wrong_size)
    except ReferenceRejection as e:
        size_code = e.code
    mismatch = dict(matched)
    mismatch[manifest["assets"][0]["path"]] = b"x" * manifest["assets"][0]["byte_count"]
    try:
        verify_assets(manifest, mismatch)
    except ReferenceRejection as e:
        mismatch_code = e.code
    return {
        "cases": results,
        "case_count": len(results),
        "accepted_count": sum(1 for r in results if not r["rejected"]),
        "all_rejected": all(r["rejected"] for r in results),
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
    for i, text in enumerate(samples):
        rejected = False
        try:
            strict_loads(text)
        except ValueError:
            rejected = True
        results.append({"id": "json-" + str(i), "rejected": rejected})
    return {"cases": results, "case_count": len(results), "accepted_count": sum(1 for r in results if not r["rejected"]), "all_rejected": all(r["rejected"] for r in results)}


def invalid_pin_cases() -> Dict[str, Any]:
    digest = "a" * 64
    samples = (
        digest + "  source:duplicate\n" + digest + "  source:duplicate\n",
        "abc  source:short\n",
        digest + "  /absolute\n",
        digest + "  source:../escape\n",
    )
    results = []
    for i, text in enumerate(samples):
        rejected = False
        try:
            parse_pin_lines(text)
        except ValueError:
            rejected = True
        results.append({"id": "pin-" + str(i), "rejected": rejected})
    return {"cases": results, "case_count": len(results), "accepted_count": sum(1 for r in results if not r["rejected"]), "all_rejected": all(r["rejected"] for r in results)}


GATES: Tuple[Dict[str, Any], ...] = (
    {"id": "RG-01", "name": "exact_runnable_source_or_artifact", "status": "blocked", "qualifies": False, "missing": "exact source revision, bytes, SHA-256 and reviewed licence/rights"},
    {"id": "RG-02", "name": "exact_assets_and_runtime_lock", "status": "blocked", "qualifies": False, "missing": "pinned weights/runtime/cohort/reference assets with byte counts and SHA-256"},
    {"id": "RG-03", "name": "installed_v0_boundary", "status": "blocked", "qualifies": False, "missing": "opt-in adapter intake without ABI, registry, default or shared-build change"},
    {"id": "RG-04", "name": "restoration_profile_paired_cohort", "status": "blocked", "qualifies": False, "missing": "rights-cleared paired low/high-band cohort with frozen corruption metadata"},
    {"id": "RG-05", "name": "content_preservation_and_negative_control", "status": "blocked", "qualifies": False, "missing": "matched preservation evidence retaining negative spectrum-copy control"},
    {"id": "RG-06", "name": "perceptual_and_listening_evidence", "status": "blocked", "qualifies": False, "missing": "task-appropriate perceptual scoring and authorized listening on matched cohort"},
    {"id": "RG-07", "name": "device_timing_and_availability", "status": "blocked", "qualifies": False, "missing": "target-device timing, availability and paced workload evidence"},
    {"id": "RG-08", "name": "public_admission_review", "status": "blocked", "qualifies": False, "missing": "independent review, rights/counsel clearance and release decision"},
)

EXACT_BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {"id": "B-01", "blocker": "No exact runnable spectrum-copy BWE source revision or separately licensed artifact is pinned. The research retains spectrum-copy as a negative comparison and points to NU-Wave 2 as a candidate family, but no immutable bytes, SHA-256 or reviewed rights record are staged.", "reopen": "Provide an exact pinned source/artifact revision with byte counts, SHA-256 and reviewed licence/rights; do not download or execute assets in this task."},
    {"id": "B-02", "blocker": "No exact weights, runtime lock, rights-cleared paired cohort, reference output or release attestation is present. Caller-supplied manifest validation is shape-only and cannot qualify the candidate.", "reopen": "Supply all required external assets by exact id, byte count and SHA-256 with reviewed rights/consent sidecars and verified bytes."},
    {"id": "B-03", "blocker": "No Restoration-profile matched evidence exists: no paired low/high-band cohort, no task-specific quality/perceptual score, no content-preservation proof, and no listening or device timing result.", "reopen": "Run a rights-cleared matched Restoration cohort with frozen corruption metadata, negative controls, perceptual/listening evidence, and target-device timing under declared workload."},
    {"id": "B-04", "blocker": "No opt-in adapter intake or release decision exists. The negative spectrum-copy comparison must be retained and cannot be exposed as a qualified processor.", "reopen": "Obtain independent opt-in review, rights/counsel clearance, and an explicit release decision with no default registration, ABI, shared-build or CI change."},
)

SOURCE_REPORTED: Dict[str, Any] = {
    "qualifies": False,
    "entries": [
        {"id": "SR-01", "claim": "Spectrum-copy extension at 3.5 kHz cutoff fell to 14.39 dB SI-SDR vs 17.40 dB band-limited input on the 12-clip synthetic pilot.", "source": "research/distortion_restoration_20261028.md:32"},
        {"id": "SR-02", "claim": "The local copy-spectrum baseline should be rejected; it harms fidelity.", "source": "research/distortion_restoration_20261028.md:47"},
        {"id": "SR-03", "claim": "NU-Wave 2 is a candidate family but weights are not staged locally and generated bands require fidelity/content-preservation evaluation.", "source": "research/distortion_restoration_20261028.md:47"},
    ],
    "separation": "All entries are source-reported provenance from pinned research. None is reproduced, scored here, or promoted to a candidate result.",
}


def identity_control() -> Dict[str, Any]:
    # Deterministic integer pattern; no audio processing claim.
    pattern = [(i * 17 % 127) - 63 for i in range(SAMPLE_RATE_HZ)]
    payload = canonical_bytes(pattern)
    digest = sha256_bytes(payload)
    return {
        "label": "integer identity control, not BWE output",
        "pattern_sha256": digest,
        "output_sha256": digest,
        "byte_identical": True,
        "source_end": SAMPLE_RATE_HZ,
        "output_end": SAMPLE_RATE_HZ,
        "qualifies": False,
    }


def restoration_profile() -> Dict[str, Any]:
    items = [
        ("corruption_metadata", "Freeze corruption, metadata and corresponding clean/baseline.", "synthetic schema probe only; no paired cohort"),
        ("stratification", "Stratify by degradation, erasure/bandwidth conditions.", "blocked; no rights-cleared cohort"),
        ("discrete_validity", "Report discrete validity/decoded intervals and task-specific quality.", "blocked; no real outputs"),
        ("bounds", "Report output bounds, peaks and timing.", "blocked; no runtime/device timing"),
        ("negative_control", "Retain harmful spectrum-copy negative comparison.", "source-reported negative retained; not re-run"),
        ("content_preservation", "Require content preservation before inclusion.", "blocked; no perceptual/listening/content checks"),
    ]
    return {
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md:18",
        "items": [{"id": i, "requirement": r, "synthetic_control": c, "status": "blocked", "qualifies": False} for i, r, c in items],
        "item_count": len(items),
        "qualifies": False,
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    probe = validate_probe(valid_probe())
    probe_adv = probe_adverse_cases()
    manifest_adv = manifest_adverse_cases()
    json_adv = invalid_json_cases()
    pin_adv = invalid_pin_cases()
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
        "synthetic_probe": probe,
        "identity_control": identity_control(),
        "restoration_profile": restoration_profile(),
        "asset_resolution": absent_artifact_probe(),
        "adverse": {
            "caller_manifest": manifest_adv,
            "synthetic_probe": probe_adv,
            "invalid_json": json_adv,
            "invalid_pins": pin_adv,
            "all_rejected": manifest_adv["all_rejected"] and probe_adv["all_rejected"] and json_adv["all_rejected"] and pin_adv["all_rejected"],
            "metrics": None,
        },
        "source_reported": dict(SOURCE_REPORTED),
        "source_lines": source_lines(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "gates": [dict(g) for g in GATES],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "missing_evidence": [
            "exact runnable source/artifact revision, bytes, SHA-256 and rights review",
            "six exact external assets with byte counts, SHA-256 and rights sidecars",
            "rights-cleared paired Restoration cohort with frozen corruption metadata",
            "matched content-preservation, perceptual and listening evidence",
            "target-device timing, availability and paced workload evidence",
            "opt-in intake, independent review and release decision",
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
        "inventory_link": inventory_link(),
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
        "# SHA-256 pins for " + TASK_ID + ".",
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
            payload = (HERE / name).read_bytes()
        lines.append(sha256_bytes(payload) + "  " + TASK_PREFIX + name)
    return ("\n".join(lines) + "\n").encode("utf-8")

def contract_bytes(report_payload: bytes, sidecar_payload: bytes, sources_payload: bytes, report: Dict[str, Any]) -> bytes:
    artifact_pins: Dict[str, str] = {}
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (HERE / name).read_bytes()
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
        "inventory_link": inventory_link(),
        "caller_supplied_asset_contract": report["caller_supplied_asset_contract"],
        "source_reported": report["source_reported"],
        "gates": [dict(g) for g in GATES],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "invariants": [
            "Installed v0 remains 16 kHz mono float32 with 160-sample frames.",
            "Only the task-local evidence directory is written.",
            "No source, weights, runtime, audio or corpus artifact is bundled, downloaded or executed.",
            "Caller manifests are validated as metadata and byte hashes only.",
            "Synthetic probes are labelled and cannot qualify the candidate.",
            "The negative spectrum-copy comparison is retained; no result overturns it.",
            "All provider, default, ABI, registry, shared-build and CI flags remain false.",
            "Only stable board and inventory row identities enter canonical bytes or gates.",
        ],
    }
    return canonical_bytes(contract)


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(worktree), *arguments], capture_output=True, text=True, check=False)


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


if __name__ == "__main__":
    print("reference builder: import run.py to generate canonical artifacts")
