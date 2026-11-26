# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SoX ``noisered``.

This package is proposal-only feasibility evidence. It models a caller-supplied
noise-profile asset boundary and the installed 16 kHz mono float32 160-sample
geometry with synthetic, in-memory values. It does not implement, vendor,
download, load or execute SoX or any caller asset. No real audio, listening,
device timing, benchmark or release result is included. The enhancement
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
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/sox-noisered/caller-supplied/0.1"
TASK_ID = "SDK-SOX-NOISERED"
TITLE = "SoX `noisered`"
COMPONENT = "sox-noisered"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "022a7ad3cedf35aba70ef93b32b71ae51e1e30ca"
BRANCH = "swarm/SDK-SOX-NOISERED"
REVIEWER = "reviewer-SOX-NOISERED"
PROFILE = "Enhancement"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_geometry_incomplete"
CONFIGURATION_ID = "sox.noisered.caller-profile/0.1"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
PROFILE_SAMPLES = 160
PROFILE_BYTES = PROFILE_SAMPLES * 4

SOURCE_PINS: Dict[str, str] = {
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
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
    "108409639958143e3bc399c2f4688639832fc6b2f6c0fa4e2cfe7551dac90011"
)
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence", "quality"
)

TASK_PREFIX = "docs/task-evidence/sox-noisered/"
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
        "id": "census-noisered-row",
        "path": "research/noise_suppression_candidate_census.md",
        "line": 49,
        "text": (
            "| **SoX `noisered`** | Classical profile-based spectral reduction, no weights "
            "| Official SoX source; requires a representative noise-only segment/profile. "
            "| Conditional baseline. Use only when profile provenance is supplied; "
            "verify build licensing configuration. |"
        ),
    },
)

ABSENT_CANDIDATES: Tuple[str, ...] = (
    "research/voice-enhancement-20261101/repos/sox",
    "research/noise_suppression_20261027/repos/sox",
    "research/noise_suppression_assets/sox/noisered.profile",
    "third_party/sox",
    "deps/sox",
    "data/checkouts/sox",
    "data/packages/sox",
    "audio-benchmark-platform/audio-sdk/third_party/sox",
    "audio-benchmark-platform/audio-sdk/deps/sox",
)
SDK_ABSENT_CANDIDATES: Tuple[str, ...] = (
    "third_party/sox",
    "deps/sox",
    "data/assets/sox-noisered",
    "adapters/sox-noisered",
    "build/install/bin/sox",
    "docs/task-evidence/sox-noisered/assets",
)

REQUIRED_ASSETS: Tuple[Dict[str, str], ...] = (
    {"id": "noise_profile", "artifact": "caller-supplied SoX noise profile"},
    {"id": "sox_runtime", "artifact": "pinned SoX build with recorded license configuration"},
)

ASSET_LEDGER: Dict[str, Any] = {
    "status": "absent_exact_sox_source_and_noise_profile",
    "sox_source": {
        "revision": None,
        "archive_sha256": None,
        "installed_executable": None,
        "build_id": None,
        "license_configuration": None,
        "present_locally": False,
    },
    "noise_profile": {
        "path": None,
        "byte_count": None,
        "sha256": None,
        "provenance": None,
        "present_locally": False,
    },
    "noise_only_segment": {
        "path": None,
        "byte_count": None,
        "sha256": None,
        "rights_status": None,
        "present_locally": False,
    },
    "paired_cohort": {
        "path": None,
        "sha256": None,
        "clean_reference_status": None,
        "present_locally": False,
    },
    "downloaded": False,
    "vendored": False,
    "loaded": False,
    "executed": False,
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
    "benchmark": False,
    "descriptor_registration": False,
    "device_timing": False,
    "download_attempted": False,
    "external_executable_invoked": False,
    "listening": False,
    "network_used": False,
    "provider_registered": False,
    "real_audio": False,
    "release_claim": False,
    "sox_executed": False,
}

NEGATIVE_CLAIMS: List[str] = [
    "No SoX source, binary, header, archive, noise profile or optional library bundle is vendored, downloaded, loaded or executed.",
    "The caller-supplied asset validator is metadata-only and fails closed before any asset load or SoX invocation.",
    "Synthetic in-memory float32 frames and profile bytes are not real audio and are not SoX output.",
    "No rights-cleared paired cohort, clean reference, listening panel or predictive score is present.",
    "No target-runtime content/availability timing, memory, deadline or device measurement is made.",
    "No provider, descriptor, default, ABI, CONTRACTS, registry, shared build or CI behavior is changed.",
    "No benchmark, qualification, upstream-parity or release claim is made.",
    "No missing, blocked or synthetic result qualifies the candidate.",
]

GATES: List[Dict[str, Any]] = [
    {
        "id": "RG-01",
        "title": "exact_sox_source_build_and_license_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "No exact SoX revision, archive digest, build ID or build licensing configuration is pinned.",
        "reopen_condition": "Stage the exact upstream source revision and archive with SHA-256, notices and a reproducible pinned build ID.",
    },
    {
        "id": "RG-02",
        "title": "noise_profile_provenance_and_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "No rights-cleared noise-only segment or generated profile has a recorded path, byte count and SHA-256.",
        "reopen_condition": "Supply the noise-only segment and resulting profile with rights provenance, immutable byte count and SHA-256.",
    },
    {
        "id": "RG-03",
        "title": "matched_paired_cohort_and_controls",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "No frozen paired noisy/clean cohort, identity control or established task-matched baseline exists.",
        "reopen_condition": "Freeze a rights-cleared cohort with clean references, identity/noisy controls and a task-matched baseline.",
    },
    {
        "id": "RG-04",
        "title": "independent_quality_or_listening_protocol",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "No listening panel or authorized predictive scorer is agreed for the exact conditions.",
        "reopen_condition": "Record an approved listening or predictive protocol before scoring any real candidate output.",
    },
    {
        "id": "RG-05",
        "title": "paired_metrics_and_preservation",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "No paired SI-SDR, STOI, clean-speech preservation, peak or invalid-output result exists for real SoX output.",
        "reopen_condition": "Score pinned real outputs against clean references with agreed metrics and preservation gates.",
    },
    {
        "id": "RG-06",
        "title": "alignment_state_memory_and_target_timing",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "No measured content mapping, state behavior, memory use or content/availability timing exists at a target runtime.",
        "reopen_condition": "Run a paced target harness with agreed coverage, margins, deadlines and resource limits.",
    },
    {
        "id": "RG-07",
        "title": "opt_in_intake_and_public_default",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "No separate opt-in provider intake, OFF-default decision or registration review exists.",
        "reopen_condition": "Complete a separate provider intake with OFF default and an explicit public default decision.",
    },
    {
        "id": "RG-08",
        "title": "independent_exact_head_review",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "No independent reviewer has approved the exact head and no board transition is recorded.",
        "reopen_condition": "Obtain independent exact-head approval and a coordinator-recorded board transition.",
    },
]

EXACT_BLOCKERS: List[Dict[str, Any]] = [
    {
        "id": "XB-01",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-01", "RG-07"],
        "statement": "No permitted SoX source tree, exact revision, archive digest, installed executable, build ID or build licensing configuration is present. `shutil.which('sox')` found no executable and no source or binary appears at the fixed absence probes.",
        "reopen": "Stage an exact licensed SoX revision with archive SHA-256, notices, a reproducible build ID and a reviewed build-license configuration.",
    },
    {
        "id": "XB-02",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-02", "RG-05"],
        "statement": "No representative noise-only segment or SoX-generated noise profile has provenance, byte count or SHA-256. The census explicitly gates this candidate on profile provenance.",
        "reopen": "Supply a rights-cleared noise-only segment, generate its profile with the pinned SoX build, and record the exact mode, amount, byte count and SHA-256.",
    },
    {
        "id": "XB-03",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-03", "RG-04", "RG-05"],
        "statement": "No rights-cleared paired cohort, clean references, identity/noisy control, established baseline, scorer or listening protocol is staged.",
        "reopen": "Freeze the cohort and controls with rights clearance, agree the metric margins and analysis plan, then score real candidate outputs.",
    },
    {
        "id": "XB-04",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-06", "RG-07", "RG-08"],
        "statement": "No target-runtime alignment/state/memory/deadline evidence, opt-in intake, OFF-default decision or independent exact-head review exists.",
        "reopen": "Run the paced target harness, complete separate opt-in intake with default OFF, and obtain independent exact-head approval.",
    },
]

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "sample_rate_hz", "channels",
    "sample_format", "frame_samples", "profile_path", "profile_sha256",
    "profile_byte_count", "profile_provenance", "sox_source_revision",
    "sox_build_id", "sox_license_configuration", "amount", "runtime_path",
    "runtime_sha256", "runtime_byte_count",
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
    """Parse the two fenced SHA-256 tables embedded in README.md."""

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


def synthetic_float_samples(count: int, seed: int = 0x5EED5045) -> List[float]:
    state = seed
    values: List[float] = []
    for _ in range(count):
        state, draw = _next_u32(state)
        values.append(((draw >> 8) / 0xFFFFFF - 0.5) * 0.5)
    return values


def synthetic_profile_bytes() -> bytes:
    """In-memory float32 proxy; explicitly not a SoX noise-profile file."""

    return struct.pack("<" + str(PROFILE_SAMPLES) + "f",
                       *synthetic_float_samples(PROFILE_SAMPLES))


def synthetic_frame(index: int) -> List[float]:
    return synthetic_float_samples(FRAME_SAMPLES, 0x5EED5045 + index)


def valid_manifest(profile_path: str = "/absent/noise.profile") -> Dict[str, Any]:
    return {
        "adapter": SCHEMA_MANIFEST,
        "configuration_id": CONFIGURATION_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "profile_path": profile_path,
        "profile_sha256": "0" * 64,
        "profile_byte_count": PROFILE_BYTES,
        "profile_provenance": "caller-declared-unverified",
        "sox_source_revision": "caller-declared-unverified",
        "sox_build_id": "caller-declared-unverified",
        "sox_license_configuration": "caller-declared-unverified",
        "amount": "0",
        "runtime_path": "/absent/sox",
        "runtime_sha256": "0" * 64,
        "runtime_byte_count": 1,
    }


def validate_caller_manifest(manifest: Any,
                             profile_bytes: bytes | None = None,
                             runtime_bytes: bytes | None = None) -> None:
    """Validate metadata and supplied bytes, then fail closed on identity."""

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
    for path_key in ("profile_path", "runtime_path"):
        value = manifest[path_key]
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise ReferenceRejection("RELATIVE_ASSET_PATH", path_key + " must be absolute")
    for digest_key in ("profile_sha256", "runtime_sha256"):
        if not _hex_digest(manifest[digest_key]):
            raise ReferenceRejection("BAD_ASSET_DIGEST", digest_key + " malformed")
    for count_key in ("profile_byte_count", "runtime_byte_count"):
        if not _positive_int(manifest[count_key]):
            raise ReferenceRejection("BAD_BYTE_COUNT", count_key + " malformed")
    amount = manifest["amount"]
    if not isinstance(amount, str) or re.fullmatch(
            r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", amount) is None:
        raise ReferenceRejection("BAD_AMOUNT", "amount must be a canonical decimal string")
    for text_key in ("profile_provenance", "sox_source_revision", "sox_build_id",
                     "sox_license_configuration"):
        value = manifest[text_key]
        if not isinstance(value, str) or not value.strip():
            raise ReferenceRejection("MISSING_IDENTITY", text_key + " required")
    if profile_bytes is None:
        raise ReferenceRejection("ASSET_ABSENT", "caller profile bytes were not supplied")
    if len(profile_bytes) != manifest["profile_byte_count"]:
        raise ReferenceRejection("ASSET_SIZE_MISMATCH", "profile byte count mismatch")
    if sha256_bytes(profile_bytes) != manifest["profile_sha256"]:
        raise ReferenceRejection("ASSET_HASH_MISMATCH", "profile SHA-256 mismatch")
    if len(profile_bytes) % 4 != 0 or len(profile_bytes) < PROFILE_BYTES:
        raise ReferenceRejection("PROFILE_GEOMETRY_MISMATCH", "profile length mismatch")
    profile_values = struct.unpack("<" + str(len(profile_bytes) // 4) + "f",
                                   profile_bytes)
    if any(not math.isfinite(value) for value in profile_values):
        raise ReferenceRejection("NONFINITE_PROFILE", "profile contains a nonfinite sample")
    if runtime_bytes is not None:
        if len(runtime_bytes) != manifest["runtime_byte_count"]:
            raise ReferenceRejection("RUNTIME_SIZE_MISMATCH", "runtime byte count mismatch")
        if sha256_bytes(runtime_bytes) != manifest["runtime_sha256"]:
            raise ReferenceRejection("RUNTIME_HASH_MISMATCH", "runtime SHA-256 mismatch")
    raise ReferenceRejection(
        "SOX_PROFILE_IDENTITY_UNPINNED",
        "hash-matched bytes are still not a pinned SoX build and rights-cleared profile")


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
            accepted = True
            observed = "ACCEPTED"
        except ValueError:
            accepted = False
            observed = "INVALID_JSON"
        cases.append({"accepted": accepted, "id": case_id, "observed": observed})
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
    }


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
            accepted = True
            observed = "ACCEPTED"
        except ValueError:
            accepted = False
            observed = "INVALID_PIN"
        cases.append({"accepted": accepted, "id": case_id, "observed": observed})
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
    }


def adverse_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    profile = synthetic_profile_bytes()
    nonfinite = struct.pack("<f", float("nan")) + profile[4:]

    def probe(case_id: str, mutate: Any, candidate: Any = None,
              supplied: bytes | None = profile) -> None:
        manifest = valid_manifest() if candidate is None else candidate
        mutate(manifest)
        try:
            validate_caller_manifest(manifest, supplied)
            observed = "ACCEPTED"
        except ReferenceRejection as error:
            observed = error.code
        cases.append({"accepted": observed == "ACCEPTED", "id": case_id,
                      "observed": observed})

    probe("missing_field", lambda m: m.pop("sample_rate_hz"))
    probe("unknown_field", lambda m: m.update({"unexpected": 1}))
    probe("wrong_adapter", lambda m: m.update({"adapter": "other"}))
    probe("wrong_configuration", lambda m: m.update({"configuration_id": "other"}))
    probe("wrong_sample_rate", lambda m: m.update({"sample_rate_hz": 48000}))
    probe("wrong_channels", lambda m: m.update({"channels": 2}))
    probe("wrong_sample_format", lambda m: m.update({"sample_format": "int16"}))
    probe("wrong_frame_samples", lambda m: m.update({"frame_samples": 320}))
    probe("relative_profile_path",
          lambda m: m.update({"profile_path": "relative/noise.profile"}))
    probe("absent_profile", lambda m: None, supplied=None)
    probe("bad_profile_digest",
          lambda m: m.update({"profile_sha256": "f" * 64}))
    probe("bad_profile_byte_count",
          lambda m: m.update({"profile_byte_count": 1}))
    probe("short_profile",
          lambda m: m.update({"profile_byte_count": 320,
                              "profile_sha256": sha256_bytes(profile[:320])}),
          supplied=profile[:320])
    probe("nonfinite_profile",
          lambda m: m.update({"profile_sha256": sha256_bytes(nonfinite)}),
          supplied=nonfinite)
    probe("bad_amount", lambda m: m.update({"amount": "+0.5"}))
    probe("missing_identity", lambda m: m.update({"sox_build_id": ""}))
    probe("manifest_not_object", lambda m: None, candidate=["not", "an", "object"])
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "note": "All cases fail closed before any SoX invocation or quality metric.",
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
    partition_ok = covered == list(range(accepted_samples))
    all_values = [value for frame in frames for value in frame]
    frame_bytes = [struct.pack("<" + str(FRAME_SAMPLES) + "f", *frame)
                   for frame in frames]
    profile = synthetic_profile_bytes()
    profile_values = struct.unpack("<" + str(PROFILE_SAMPLES) + "f", profile)
    same = synthetic_frame(0) == synthetic_frame(0)
    return {
        "label": "model-free 16 kHz mono float32 160-sample geometry; not SoX output",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "frame_count": len(frames),
        "accepted_samples": accepted_samples,
        "final_valid_samples": len(final_valid),
        "final_zero_padding_samples": FRAME_SAMPLES - len(final_valid),
        "source_intervals": intervals,
        "partition_ok": partition_ok,
        "frame_sha256": [sha256_bytes(payload) for payload in frame_bytes],
        "nonfinite_count": sum(1 for value in all_values if not math.isfinite(value)),
        "peak_abs": max(abs(value) for value in all_values),
        "profile_proxy": {
            "byte_count": len(profile),
            "sha256": sha256_bytes(profile),
            "float32_samples": len(profile_values),
            "finite_count": sum(1 for value in profile_values if math.isfinite(value)),
            "not_a_sox_profile": True,
        },
        "identity_control": {
            "repeat_frame_byte_identical": same,
            "qualifies": False,
        },
        "declared_task_local_buffering_delay_samples": 0,
        "sox_content_delay_claimed": False,
        "note": (
            "Exact integer intervals and in-memory float32 values only. No SoX "
            "effect, profile file, audio decode, device clock or listening is used."
        ),
    }


def asset_pins_absent() -> bool:
    for group in ("sox_source", "noise_profile", "noise_only_segment", "paired_cohort"):
        for key, value in ASSET_LEDGER[group].items():
            if key.endswith("present_locally"):
                if value is not False:
                    return False
            elif value is not None:
                return False
    return not any(ASSET_LEDGER[key] for key in
                   ("downloaded", "vendored", "loaded", "executed"))


def absent_artifact_probe() -> Dict[str, Any]:
    workspace_found = [path for path in ABSENT_CANDIDATES
                       if (SOURCE_ROOT / path).exists()]
    sdk_found = [path for path in SDK_ABSENT_CANDIDATES
                 if (SDK_ROOT / path).exists()]
    executable = shutil.which("sox")
    return {
        "note": "Bounded read-only path probes; no download, import or load attempted.",
        "present": bool(workspace_found or sdk_found or executable),
        "workspace_candidates": list(ABSENT_CANDIDATES),
        "sdk_worktree_candidates": list(SDK_ABSENT_CANDIDATES),
        "workspace_found": workspace_found,
        "sdk_worktree_found": sdk_found,
        "sox_executable_found": executable,
        "method": "explicit candidate paths plus PATH lookup; no recursive filesystem walk",
    }


def enhancement_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "identity_noisy_control": {
                "status": "synthetic_control_only",
                "qualifies": False,
                "evidence": "Deterministic in-memory frames; no SoX effect applied.",
            },
            "established_task_matched_baseline": {
                "status": "blocked",
                "qualifies": False,
                "evidence": "No pinned SoX build or baseline output exists.",
            },
            "paired_si_sdr_and_stoi": {
                "status": "blocked",
                "qualifies": False,
                "evidence": "No clean references or real candidate outputs are present.",
            },
            "clean_speech_preservation": {
                "status": "blocked",
                "qualifies": False,
                "evidence": "No clean-speech run exists.",
            },
            "peaks_and_invalid_outputs": {
                "status": "synthetic_control_only",
                "qualifies": False,
                "evidence": "Finite synthetic values and strict manifest rejection only.",
            },
            "alignment_state_memory_timing": {
                "status": "blocked",
                "qualifies": False,
                "evidence": "No target runtime, device clock or memory harness is staged.",
            },
            "content_delay_claim": {
                "status": "blocked",
                "qualifies": False,
                "evidence": "Integer interval probe is not a measured SoX content delay.",
            },
            "unpaired_predictive_or_listening": {
                "status": "blocked",
                "qualifies": False,
                "evidence": "No listening panel or authorized predictive scorer is agreed.",
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
            "family": "classical profile-based spectral reduction",
            "weights": False,
            "representative_noise_only_profile_required": True,
            "build_licensing_configuration_must_be_verified": True,
            "status": "conditional_baseline",
        },
        "excluded_from_local_evidence": [
            "No source-reported SoX quality number is present in the pinned census row.",
            "No other denoiser score is treated as SoX noisered evidence.",
            "The synthetic profile proxy is not a SoX-generated profile.",
        ],
        "listening_performed_here": False,
        "qualifies": False,
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    probe = absent_artifact_probe()
    manifest_adverse = adverse_cases()
    json_adverse = invalid_json_cases()
    pin_adverse = invalid_pin_cases()
    geometry = geometry_probe()
    manifest = valid_manifest()
    manifest["profile_sha256"] = geometry["profile_proxy"]["sha256"]
    try:
        validate_caller_manifest(manifest, synthetic_profile_bytes())
        manifest_outcome = "ACCEPTED"
    except ReferenceRejection as error:
        manifest_outcome = error.code
    if manifest_outcome != "SOX_PROFILE_IDENTITY_UNPINNED":
        raise ValueError("unexpected_caller_manifest_outcome:" + manifest_outcome)
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
            "configuration_id": CONFIGURATION_ID,
            "required_fields": list(CALLER_MANIFEST_FIELDS),
            "required_assets": [dict(item) for item in REQUIRED_ASSETS],
            "validated_outcome": manifest_outcome,
            "loaded": False,
            "executed": False,
            "note": (
                "Metadata and in-memory byte validation only. Even a "
                "hash-matched synthetic proxy fails as SOX_PROFILE_IDENTITY_UNPINNED."
            ),
        },
        "geometry_probe": geometry,
        "enhancement_profile": enhancement_profile(),
        "asset_resolution": probe,
        "asset_ledger": dict(ASSET_LEDGER),
        "asset_pins_absent": asset_pins_absent(),
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
            "status": "blocked_no_pinned_sox_noise_profile_or_matched_cohort",
            "identity_control": "synthetic integer frame control only",
            "task_matched_baseline": "blocked",
            "qualifies_candidate": False,
        },
        "source_reported": source_reported(),
        "available_evidence": {
            "status": "synthetic_geometry_only",
            "clock": "no runtime clock",
            "real_sox_output": False,
            "device_timing": False,
            "content_delay_claim": False,
            "first_output_or_tail": "blocked_not_measured",
        },
        "licensing_analysis": {
            "expected_upstream": "SoX GPL-2.0-or-later is the common upstream term; exact build configuration is not verified here",
            "profile_and_noise_segment_rights": "unreviewed",
            "optional_library_terms": "unreviewed",
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
            "source_reported": True,
            "synthetic": True,
            "model_free_geometry": True,
            "real_local_sox_output": False,
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
        "# SHA-256 pins for SDK-SOX-NOISERED.",
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
            "The caller-supplied noise-profile reference is metadata-only and never executed.",
            "Only the task-local evidence directory is written.",
            "No SoX source, binary, profile, audio or runtime artifact is bundled.",
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
