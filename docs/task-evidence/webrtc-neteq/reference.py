# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-WEBRTC-NETEQ (WebRTC NetEq).

This module is stdlib-only and deterministic. It does not contain, import,
build, link, download or execute WebRTC, NetEq, Opus or any other runtime, and
it reads no audio. It records the exact external blocker for receive-side
jitter/playout evidence, probes a fixed list of task-local paths for the absent
artifacts, validates caller-supplied manifest and trace documents with a
fail-closed admission boundary, and builds the canonical report.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

TASK = "SDK-WEBRTC-NETEQ"
COMPONENT_ID = "webrtc-neteq"
TASK_TITLE = "WebRTC NetEq"
CONTRACT_ID = "audio-sdk/webrtc-neteq-readiness/0.1"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
PROFILE = "tool"
MODE = "feasibility"
BASE_COMMIT = "a91a45e32428df353dbf55a7a9fd2ec052760539"
BRANCH = "swarm/SDK-WEBRTC-NETEQ"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
DEFAULT_AUDIO_ROOT = HERE.parents[5]
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT", str(DEFAULT_AUDIO_ROOT))).resolve()
TASK_PREFIX = "docs/task-evidence/webrtc-neteq/"

WRITE_SCOPE = "docs/task-evidence/webrtc-neteq/ only"

# Immutable inputs. `source:` rows are workspace-relative, the rest are
# SDK-worktree-relative. The mutable shared board is deliberately excluded from
# the pin set; only its stable row projection may gate anything.
SOURCE_PINS = {
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/task_backlog.json":
        "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/buffer-occupancy-controller/README.md":
        "862a94c9add8ecd5e15f09a543ff17100dc5680da00f8a0635a884509cb51a33",
    "docs/task-evidence/elastic-pcm-packets/README.md":
        "15ebaa6b2b7768faa5c1bd2fc45b900db7f71d49b7ad1292685263555953e742",
    "docs/task-evidence/elastic-pcm-packets/contract.json":
        "2ce960fb63a3ee2e1a888f33a990ce15da1804b0550aa3ad637c941222955e85",
    "docs/task-evidence/granular-tsm/README.md":
        "d97f06911fd90667288fe571c7a3f4210ece629f7e839c1d41200ceec48ec0a0",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md":
        "ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df",
    "docs/task-evidence/survey-eng-03/README.md":
        "d09dc8f09e16c7af0a1898d7c73bda8fc7002fa35cd49c5d8f5b21152fb6d6d9",
    "docs/task-evidence/survey-eng-03/contract.json":
        "1957fa53a5e74b8ea1bc612ef0c06e440a5213077021fd1f52b0361c090bb6c7",
    "docs/task-evidence/survey-eng-03/report.json":
        "d7ff9ea111bf3ca8da8915b2bbda58a65143ec51f00620ed63b423424cb35ddf",
}

# Only stable, non-mutable fields of the shared board row are used for identity
# gating. `status`, `owner`, `claim`, `review`, `handoff`, `blocked_reason` and
# `dispatch_priority` are observed by neither this package nor its verifier.
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_PROJECTION = {
    "id": "SDK-WEBRTC-NETEQ",
    "title": "WebRTC NetEq",
    "component": "webrtc-neteq",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
}

# Fixed, bounded absence probes. No recursive workspace walk is performed.
ABSENCE_PROBES = (
    "data/checkouts/webrtc",
    "data/checkouts/WebRTC",
    "data/checkouts/webrtc-src",
    "data/checkouts/libwebrtc",
    "data/checkouts/neteq",
    "adapters/webrtc-neteq",
    "adapters/neteq",
    "third_party/webrtc",
    "third_party/libwebrtc",
    "deps/webrtc",
    "audio-benchmark-platform/audio-sdk/third_party/webrtc",
    "audio-benchmark-platform/audio-sdk/third_party/libwebrtc",
    "audio-benchmark-platform/audio-sdk/deps/webrtc",
    "audio-benchmark-platform/audio-sdk/core/neteq",
    "audio-benchmark-platform/audio-sdk/modules/audio_coding/neteq",
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "permitted_source",
        "requirement": (
            "Exact permitted WebRTC NetEq source snapshot pinned by an "
            "immutable 40-hex revision and an immutable archive SHA-256."),
    },
    {
        "id": "ART-02",
        "kind": "license_and_notices",
        "requirement": (
            "The upstream license text, copyright notices and complete "
            "third-party notice bundle that apply to the pinned revision."),
    },
    {
        "id": "ART-03",
        "kind": "built_runtime",
        "requirement": (
            "A reproducible, pinned built NetEq runtime with its exact "
            "toolchain, build configuration and artifact SHA-256."),
    },
    {
        "id": "ART-04",
        "kind": "receive_trace_cohort",
        "requirement": (
            "A rights-cleared frozen receive trace cohort with per-packet "
            "sequence numbers, RTP timestamps, arrival microseconds, payload "
            "byte counts and payload SHA-256 digests."),
    },
    {
        "id": "ART-05",
        "kind": "codec_runtime",
        "requirement": (
            "The matching codec payload format and pinned decoder/PLC runtime "
            "for the trace codec, with exact revision and license."),
    },
    {
        "id": "ART-06",
        "kind": "playout_harness",
        "requirement": (
            "A target playout device/clock harness and an agreed measurement "
            "protocol for pacing, rebuffer, deadline and resource evidence."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-01",
        "statement": (
            "No permitted WebRTC NetEq source snapshot exists in this "
            "workspace. Every fixed absence probe is missing, and no revision "
            "or archive digest can be pinned from a local artifact."),
        "required_action": (
            "Supply the exact source revision and immutable archive with "
            "matching SHA-256, from a source root that permits local review."),
        "linked_gates": ["G2", "G4"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-02",
        "statement": (
            "The upstream license, copyright and third-party notice bundle is "
            "absent, so no redistribution or product-use scope can be "
            "reviewed."),
        "required_action": (
            "Supply the license/notices bundle for the pinned revision and "
            "record an explicit review decision."),
        "linked_gates": ["G1", "G2"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-03",
        "statement": (
            "No built libwebrtc/NetEq runtime, installed location or "
            "reproducible build recipe is present. The Tool acceptance "
            "profile cannot record a version, install location or provenance."),
        "required_action": (
            "Supply a reproducible pinned build and its artifact digest, or "
            "record an explicit build-and-measure plan on an approved host."),
        "linked_gates": ["G2", "G4"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-04",
        "statement": (
            "No timestamped receive trace or rights-cleared cohort is "
            "available, so no reordering, loss, delay-target or playout replay "
            "can be admitted, and none is fabricated here."),
        "required_action": (
            "Supply rights-cleared traces with provenance, immutable digest "
            "and the exact timestamp domain."),
        "linked_gates": ["G1", "G4"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "statement": (
            "No codec payload set, decoder runtime or codec-native PLC "
            "configuration is available, so codec-integrated playout cannot be "
            "exercised."),
        "required_action": (
            "Supply the matching codec runtime and payload set with exact "
            "revision, license and PLC settings."),
        "linked_gates": ["G2", "G7"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "statement": (
            "No target playout device, clock harness or agreed deadline and "
            "resource budget exists, so no availability, latency or rebuffer "
            "measurement can be claimed."),
        "required_action": (
            "Supply the target device/clock harness and agree coverage, "
            "margins, deadlines and resource limits before collecting results."),
        "linked_gates": ["G3", "G4", "G8"],
    },
)

RELEASE_GATES = (
    {
        "id": "G1",
        "title": "rights_cleared_frozen_packet_traces",
        "statement": (
            "Rights-cleared frozen receive traces and media cohort before any "
            "quality or replay result."),
        "reopen_condition": (
            "A rights-cleared, immutable receive trace cohort with declared "
            "provenance and timestamp domain is supplied and reviewed."),
    },
    {
        "id": "G2",
        "title": "permitted_source_runtime_and_assets",
        "statement": (
            "Pinned permitted NetEq source/runtime, codec and license notices "
            "before any implementation claim."),
        "reopen_condition": (
            "Exact source revision, built runtime, codec runtime and license "
            "bundle are pinned by digest and their use is permitted."),
    },
    {
        "id": "G3",
        "title": "independent_listening",
        "statement": (
            "Independent listening before any intelligibility, naturalness or "
            "speech-preservation claim."),
        "reopen_condition": (
            "An approved listening protocol and panel exist for the exact "
            "conditions and rights scope."),
    },
    {
        "id": "G4",
        "title": "target_device_pacing_and_resources",
        "statement": (
            "Target-device pacing, clock, rebuffer, deadline and resource "
            "evidence before any availability claim."),
        "reopen_condition": (
            "Paced runs on the target device with instrumented clocks, "
            "deadlines and resource limits are recorded and reviewed."),
    },
    {
        "id": "G5",
        "title": "opt_in_provider_intake",
        "statement": (
            "Opt-in provider intake and licensing clearance before "
            "registration."),
        "reopen_condition": (
            "A separate versioned intake task accepts the adapter with an "
            "OFF default and independent review."),
    },
    {
        "id": "G6",
        "title": "public_default_selection",
        "statement": (
            "Explicit public default selection before any enabled-by-default "
            "claim."),
        "reopen_condition": (
            "The owner records an explicit default decision after intake, "
            "separately from this feasibility task."),
    },
    {
        "id": "G7",
        "title": "exact_external_reference_parity",
        "statement": (
            "Exact parity with an approved external NetEq or codec reference "
            "before any parity claim."),
        "reopen_condition": (
            "The same timestamped inputs are replayed through the approved "
            "reference and this boundary with exact accounting."),
    },
    {
        "id": "G8",
        "title": "independent_review_and_board_transition",
        "statement": (
            "Independent review and a board transition before any component "
            "acceptance claim."),
        "reopen_condition": (
            "The named reviewer verifies this package from its pinned revision "
            "and the coordinator records the board transition."),
    },
)

PROHIBITED_CLAIMS = (
    "No NetEq, libwebrtc or codec implementation, build or runtime is present, "
    "reproduced or executed.",
    "No packet trace, RTP sequence, arrival log or playout timeline is replayed "
    "or synthesized as evidence.",
    "No jitter, delay, latency, reordering, rebuffer, pacing, availability or "
    "resource measurement is made.",
    "No audio is rendered, played, scored or listened to; no quality, "
    "intelligibility, naturalness or speech-preservation result is produced.",
    "No provider is registered, exposed, enabled by default or selected as a "
    "descriptor default.",
    "No benchmark, install, CTest, ABI or release qualification result is "
    "claimed.",
)

TOOL_PROFILE_ROWS = (
    {
        "id": "TOOL-01",
        "requirement": "Record version, install location and provenance.",
        "status": "blocked",
        "evidence": "No NetEq source, runtime or installed location exists.",
    },
    {
        "id": "TOOL-02",
        "requirement": "Verify a clean checkout or extracted package.",
        "status": "blocked",
        "evidence": "No checkout or package archive is present.",
    },
    {
        "id": "TOOL-03",
        "requirement": "One typical CLI/API use.",
        "status": "blocked",
        "evidence": "No CLI or API exists to invoke.",
    },
    {
        "id": "TOOL-04",
        "requirement": "Caller-owned inputs.",
        "status": "blocked",
        "evidence": (
            "The caller-asset manifest and receive trace are declared and "
            "admission-checked only; none is supplied."),
    },
    {
        "id": "TOOL-05",
        "requirement": "Malformed inputs.",
        "status": "verified_task_local_only",
        "evidence": (
            "The task-local admission validator rejects every malformed, "
            "missing, invalid and nonfinite control before any state change; "
            "this is not runtime error behavior."),
    },
    {
        "id": "TOOL-06",
        "requirement": "Missing optional selections.",
        "status": "blocked",
        "evidence": (
            "No optional runtime selection can be exercised without a "
            "runtime."),
    },
)

# Manifest admission contract (task-local; not an SDK or WebRTC contract).
MANIFEST_FIELDS = (
    "source_path",
    "source_revision",
    "source_sha256",
    "license_path",
    "license_sha256",
    "runtime_path",
    "runtime_sha256",
    "trace_path",
    "trace_sha256",
    "internal_sample_rate_hz",
    "packet_duration_ms",
    "sdk_sample_rate_hz",
    "sdk_channels",
    "sdk_frame_samples",
)
MANIFEST_PATH_FIELDS = ("source_path", "license_path", "runtime_path",
                        "trace_path")
MANIFEST_DIGEST_FIELDS = ("source_sha256", "license_sha256", "runtime_sha256",
                          "trace_sha256")

TRACE_FIELDS = ("trace_id", "codec", "sample_rate_hz", "packet_duration_ms",
                "packets")
PACKET_FIELDS = ("seq", "rtp_timestamp", "arrival_us", "duration_samples",
                 "payload_bytes", "payload_sha256", "status")
PACKET_STATUSES = ("received", "lost")
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
TRACE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
CODEC_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,31}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

MAX_TRACE_PACKETS = 100000
MAX_SAMPLE_RATE_HZ = 192000
MIN_SAMPLE_RATE_HZ = 8000
MAX_PACKET_MS = 120


# --------------------------------------------------------------------------
# Strict JSON and digests
# --------------------------------------------------------------------------
def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def loads_strict(text: str) -> dict:
    """Parse a strict JSON object; reject duplicate keys, NaN and Infinity."""
    if text.startswith("\ufeff"):
        raise ValueError("json_byte_order_mark")
    parsed = json.loads(text, object_pairs_hook=_unique_object,
                        parse_constant=_reject_constant)
    if not isinstance(parsed, dict):
        raise ValueError("json_root_not_object")
    return parsed


def read_strict_json(path: Path) -> dict:
    return loads_strict(Path(path).read_text(encoding="utf-8"))


def canonical_text(document: object) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def canonical_bytes(document: object) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: object) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# Pins, board identity and absence probes
# --------------------------------------------------------------------------
def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for relative in sorted(pins):
        path = root / relative
        if not path.is_file():
            raise ValueError("pin_target_missing:" + relative)
        actual = sha256_file(path)
        if actual != pins[relative]:
            raise ValueError("pin_digest_mismatch:" + relative)
        rows[relative] = {"sha256": pins[relative], "actual": actual,
                          "verified": True}
    return rows


def board_row_projection(path: Path) -> dict:
    board = read_strict_json(path)
    rows = [row for row in board.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ValueError("board_row_not_unique:" + TASK)
    row = rows[0]
    return {field: row.get(field) for field in BOARD_ROW_FIELDS}


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def absence_probes(audio_root: Path, probes: tuple[str, ...] = ABSENCE_PROBES,
                   worktree: Path | None = None) -> list[dict]:
    """Return the fixed probe inventory. Any present path must block shipping."""
    sdk_root = WORKTREE if worktree is None else worktree
    rows: list[dict] = []
    for relative in probes:
        workspace_path = Path(audio_root) / relative
        sdk_candidate = sdk_root / relative
        if workspace_path.exists() or sdk_candidate.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_workspace": True,
                     "searched_sdk_worktree": True, "present": False})
    return rows


def absence_summary(rows: list[dict]) -> dict:
    return {
        "probe_count": len(rows),
        "present_count": sum(1 for row in rows if row["present"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "source_or_runtime_imported": False,
        "all_probes_absent": all(not row["present"] for row in rows),
    }


# --------------------------------------------------------------------------
# Admission validators (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _reject(code: str, field: str = "") -> dict:
    return {"accepted": False, "code": code, "field": field,
            "checks": 0, "state_unchanged": True}


def _accept(code: str, checks: int) -> dict:
    return {"accepted": True, "code": code, "field": "", "checks": checks,
            "state_unchanged": True}


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed caller-asset manifest admission. No file is loaded."""
    checks = 0
    if not isinstance(document, dict):
        return _reject("manifest_not_object")
    checks += 1
    unknown = sorted(set(document) - set(MANIFEST_FIELDS))
    if unknown:
        return _reject("unexpected_field", unknown[0])
    missing = [field for field in MANIFEST_FIELDS if field not in document]
    if missing:
        return _reject("missing_field", missing[0])
    checks += 1
    for field in MANIFEST_PATH_FIELDS:
        value = document[field]
        if not isinstance(value, str):
            return _reject("path_not_string", field)
        if not value or not os.path.isabs(value):
            return _reject("path_not_absolute", field)
        if os.path.normpath(value) != value:
            return _reject("path_not_normalized", field)
    checks += 1
    revision = document["source_revision"]
    if not isinstance(revision, str) or not HEX40.match(revision):
        return _reject("revision_not_lower_hex40", "source_revision")
    checks += 1
    for field in MANIFEST_DIGEST_FIELDS:
        value = document[field]
        if not isinstance(value, str) or not HEX64.match(value):
            return _reject("digest_not_lower_hex64", field)
    checks += 1
    for field in ("internal_sample_rate_hz", "packet_duration_ms",
                  "sdk_sample_rate_hz", "sdk_channels", "sdk_frame_samples"):
        if not _is_int(document[field]):
            return _reject("not_integer", field)
    checks += 1
    if not (MIN_SAMPLE_RATE_HZ <= document["internal_sample_rate_hz"]
            <= MAX_SAMPLE_RATE_HZ):
        return _reject("sample_rate_out_of_range", "internal_sample_rate_hz")
    if not 1 <= document["packet_duration_ms"] <= MAX_PACKET_MS:
        return _reject("packet_duration_out_of_range", "packet_duration_ms")
    if document["sdk_sample_rate_hz"] != 16000:
        return _reject("sdk_geometry_unsupported", "sdk_sample_rate_hz")
    if document["sdk_channels"] != 1:
        return _reject("sdk_geometry_unsupported", "sdk_channels")
    if document["sdk_frame_samples"] != 160:
        return _reject("sdk_geometry_unsupported", "sdk_frame_samples")
    checks += 1
    if (document["internal_sample_rate_hz"] * document["packet_duration_ms"]
            % 1000) != 0:
        return _reject("packet_geometry_not_integral", "packet_duration_ms")
    checks += 1
    if probe_paths:
        for field in MANIFEST_PATH_FIELDS:
            if not Path(document[field]).is_file():
                return _reject("artifact_absent", field)
        checks += 1
        for path_field, digest_field in zip(MANIFEST_PATH_FIELDS,
                                            MANIFEST_DIGEST_FIELDS):
            if sha256_file(Path(document[path_field])) != document[digest_field]:
                return _reject("artifact_digest_mismatch", digest_field)
        checks += 1
    return _accept("manifest_admitted", checks)


def validate_trace(document: object) -> dict:
    """Fail-closed timestamped receive-trace admission. No replay is performed."""
    checks = 0
    if not isinstance(document, dict):
        return _reject("trace_not_object")
    unknown = sorted(set(document) - set(TRACE_FIELDS))
    if unknown:
        return _reject("unexpected_field", unknown[0])
    missing = [field for field in TRACE_FIELDS if field not in document]
    if missing:
        return _reject("missing_field", missing[0])
    checks += 1
    if not isinstance(document["trace_id"], str) or not TRACE_ID.match(
            document["trace_id"]):
        return _reject("trace_id_invalid", "trace_id")
    if not isinstance(document["codec"], str) or not CODEC_ID.match(
            document["codec"]):
        return _reject("codec_invalid", "codec")
    checks += 1
    rate = document["sample_rate_hz"]
    duration_ms = document["packet_duration_ms"]
    if not _is_int(rate):
        return _reject("not_integer", "sample_rate_hz")
    if not _is_int(duration_ms):
        return _reject("not_integer", "packet_duration_ms")
    if not (MIN_SAMPLE_RATE_HZ <= rate <= MAX_SAMPLE_RATE_HZ):
        return _reject("sample_rate_out_of_range", "sample_rate_hz")
    if not 1 <= duration_ms <= MAX_PACKET_MS:
        return _reject("packet_duration_out_of_range", "packet_duration_ms")
    if (rate * duration_ms % 1000) != 0:
        return _reject("packet_geometry_not_integral", "packet_duration_ms")
    expected_samples = rate * duration_ms // 1000
    checks += 1
    packets = document["packets"]
    if not isinstance(packets, list):
        return _reject("packets_not_list", "packets")
    if not 1 <= len(packets) <= MAX_TRACE_PACKETS:
        return _reject("packet_count_out_of_range", "packets")
    checks += 1
    previous_seq: int | None = None
    first_seq: int | None = None
    first_timestamp: int | None = None
    previous_arrival: int | None = None
    seen_seq: set[int] = set()
    seen_timestamp: set[int] = set()
    for index, packet in enumerate(packets):
        prefix = "packets[%d]." % index
        if not isinstance(packet, dict):
            return _reject("packet_not_object", prefix[:-1])
        unknown = sorted(set(packet) - set(PACKET_FIELDS))
        if unknown:
            return _reject("unexpected_field", prefix + unknown[0])
        missing = [field for field in PACKET_FIELDS if field not in packet]
        if missing:
            return _reject("missing_field", prefix + missing[0])
        for field in ("seq", "rtp_timestamp", "arrival_us",
                      "duration_samples", "payload_bytes"):
            if not _is_int(packet[field]):
                return _reject("not_integer", prefix + field)
        status = packet["status"]
        if not isinstance(status, str) or status not in PACKET_STATUSES:
            return _reject("status_invalid", prefix + "status")
        digest = packet["payload_sha256"]
        if not isinstance(digest, str) or not HEX64.match(digest):
            return _reject("payload_digest_invalid", prefix + "payload_sha256")
        seq = packet["seq"]
        if not 0 <= seq <= 65535:
            return _reject("seq_out_of_range", prefix + "seq")
        if seq in seen_seq:
            return _reject("seq_duplicate", prefix + "seq")
        timestamp = packet["rtp_timestamp"]
        if timestamp < 0:
            return _reject("timestamp_negative", prefix + "rtp_timestamp")
        if timestamp in seen_timestamp:
            return _reject("timestamp_duplicate", prefix + "rtp_timestamp")
        if packet["duration_samples"] != expected_samples:
            return _reject("duration_mismatch", prefix + "duration_samples")
        if first_seq is None:
            first_seq = seq
            first_timestamp = timestamp
        else:
            expected_timestamp = (first_timestamp
                                  + ((seq - first_seq) % 65536)
                                  * expected_samples) % (1 << 32)
            if timestamp != expected_timestamp:
                return _reject("timestamp_seq_mismatch",
                               prefix + "rtp_timestamp")
        arrival = packet["arrival_us"]
        if arrival < 0:
            return _reject("arrival_negative", prefix + "arrival_us")
        if previous_arrival is not None and arrival < previous_arrival:
            return _reject("arrival_regression", prefix + "arrival_us")
        if status == "lost":
            if packet["payload_bytes"] != 0:
                return _reject("lost_payload_present", prefix + "payload_bytes")
            if digest != EMPTY_SHA256:
                return _reject("lost_payload_digest", prefix + "payload_sha256")
        else:
            if packet["payload_bytes"] <= 0:
                return _reject("received_payload_empty",
                               prefix + "payload_bytes")
            if digest == EMPTY_SHA256:
                return _reject("received_payload_digest",
                               prefix + "payload_sha256")
        seen_seq.add(seq)
        seen_timestamp.add(timestamp)
        previous_seq = seq
        previous_arrival = arrival
        checks += 1
    return _accept("trace_admitted", checks)


# --------------------------------------------------------------------------
# Synthetic admission controls (never evidence)
# --------------------------------------------------------------------------
def _manifest_control() -> dict:
    synthetic = "d" * 64
    return {
        "source_path": "/caller/neteq/source",
        "source_revision": "0" * 40,
        "source_sha256": synthetic,
        "license_path": "/caller/neteq/LICENSE",
        "license_sha256": synthetic,
        "runtime_path": "/caller/neteq/libneteq.a",
        "runtime_sha256": synthetic,
        "trace_path": "/caller/neteq/trace.json",
        "trace_sha256": synthetic,
        "internal_sample_rate_hz": 48000,
        "packet_duration_ms": 10,
        "sdk_sample_rate_hz": 16000,
        "sdk_channels": 1,
        "sdk_frame_samples": 160,
    }


def _trace_control() -> dict:
    return {
        "trace_id": "synthetic-schema-control",
        "codec": "synthetic",
        "sample_rate_hz": 48000,
        "packet_duration_ms": 10,
        "packets": [
            {"seq": 100, "rtp_timestamp": 0, "arrival_us": 1000,
             "duration_samples": 480, "payload_bytes": 120,
             "payload_sha256": "1" * 64, "status": "received"},
            {"seq": 102, "rtp_timestamp": 960, "arrival_us": 11000,
             "duration_samples": 480, "payload_bytes": 118,
             "payload_sha256": "2" * 64, "status": "received"},
            {"seq": 101, "rtp_timestamp": 480, "arrival_us": 12000,
             "duration_samples": 480, "payload_bytes": 121,
             "payload_sha256": "3" * 64, "status": "received"},
            {"seq": 103, "rtp_timestamp": 1440, "arrival_us": 21000,
             "duration_samples": 480, "payload_bytes": 0,
             "payload_sha256": EMPTY_SHA256, "status": "lost"},
        ],
    }


def admission_controls() -> dict:
    """Build the frozen adverse matrix plus two structural controls."""
    cases: list[dict] = []

    def manifest_case(case_id: str, mutate, kind: str = "manifest") -> None:
        document = _manifest_control()
        result = mutate(document)
        if result["accepted"]:
            raise ValueError("control_not_rejected:" + case_id)
        cases.append({
            "id": case_id,
            "kind": kind,
            "status": "rejected",
            "code": result["code"],
            "field": result["field"],
            "state_unchanged": result["state_unchanged"],
            "qualifies": False,
            "evidence_class": "synthetic_admission_control",
        })

    def trace_case(case_id: str, mutate) -> None:
        document = _trace_control()
        result = mutate(document)
        if result["accepted"]:
            raise ValueError("control_not_rejected:" + case_id)
        cases.append({
            "id": case_id,
            "kind": "trace",
            "status": "rejected",
            "code": result["code"],
            "field": result["field"],
            "state_unchanged": result["state_unchanged"],
            "qualifies": False,
            "evidence_class": "synthetic_admission_control",
        })

    def drop(document, field):
        del document[field]
        return validate_manifest(document, probe_paths=False)

    def put(document, field, value):
        document[field] = value
        return validate_manifest(document, probe_paths=False)

    def tput(document, field, value):
        document[field] = value
        return validate_trace(document)

    def tpacket(document, index, field, value):
        document["packets"][index][field] = value
        return validate_trace(document)

    # Manifest adverse cases.
    cases.append({
        "id": "MISS-01", "kind": "manifest", "status": "rejected",
        "code": validate_manifest(None, probe_paths=False)["code"],
        "field": "", "state_unchanged": True, "qualifies": False,
        "evidence_class": "synthetic_admission_control"})
    manifest_case("INV-01", lambda doc: drop(doc, "source_sha256"))
    manifest_case("INV-02", lambda doc: put(doc, "source_path", "neteq/src"))
    manifest_case("INV-03", lambda doc: put(doc, "license_path",
                                            "/caller/../neteq/LICENSE"))
    manifest_case("INV-04", lambda doc: put(doc, "extra", "value"))
    manifest_case("INV-05", lambda doc: put(doc, "source_revision", "A" * 40))
    manifest_case("INV-06", lambda doc: put(doc, "source_sha256", "0" * 63))
    manifest_case("INV-07", lambda doc: put(doc, "internal_sample_rate_hz",
                                            44101))
    manifest_case("INV-08", lambda doc: put(doc, "sdk_sample_rate_hz", 48000))
    manifest_case("INV-09", lambda doc: put(doc, "sdk_channels", 2))
    manifest_case("INV-10", lambda doc: put(doc, "sdk_frame_samples", 480))
    manifest_case("INV-11", lambda doc: put(doc, "packet_duration_ms", True))
    manifest_case("INV-12", lambda doc: put(doc, "packet_duration_ms", 0))
    manifest_case("INV-13", lambda doc: put(doc, "runtime_sha256", "x" * 64))
    manifest_case("INV-14", lambda doc: put(doc, "trace_path", 7))
    manifest_case("INV-15", lambda doc: put(doc, "internal_sample_rate_hz",
                                            999999))
    manifest_case("INV-16", lambda doc: put(doc, "source_revision", None))
    manifest_case("PRS-01", lambda doc: validate_manifest(doc,
                                                          probe_paths=True))

    # Trace adverse cases.
    cases.append({
        "id": "TRC-01", "kind": "trace", "status": "rejected",
        "code": tput(_trace_control(), "packets", [])["code"],
        "field": "", "state_unchanged": True, "qualifies": False,
        "evidence_class": "synthetic_admission_control"})
    trace_case("TRC-02", lambda doc: tpacket(doc, 2, "seq", 102))
    trace_case("TRC-03", lambda doc: tpacket(doc, 1, "rtp_timestamp", 1440))
    trace_case("TRC-04", lambda doc: tpacket(doc, 1, "duration_samples", 160))
    trace_case("TRC-05", lambda doc: tpacket(doc, 3, "payload_bytes", 42))
    trace_case("TRC-06", lambda doc: tpacket(doc, 0, "payload_sha256",
                                             EMPTY_SHA256))
    trace_case("TRC-07", lambda doc: tpacket(doc, 2, "arrival_us", 900))
    trace_case("TRC-08", lambda doc: tpacket(doc, 1, "arrival_us", 11000.5))
    trace_case("TRC-09", lambda doc: tput(doc, "packet_duration_ms", 7))
    trace_case("TRC-10", lambda doc: tput(doc, "trace_id", "Not An Id"))
    trace_case("TRC-11", lambda doc: tput(doc, "codec", ""))
    trace_case("TRC-12", lambda doc: tpacket(doc, 1, "status", "missing"))
    trace_case("TRC-13", lambda doc: tpacket(doc, 1, "seq", 65536))
    trace_case("TRC-14", lambda doc: tpacket(doc, 1, "payload_sha256",
                                             "Z" * 64))
    trace_case("TRC-15", lambda doc: tpacket(doc, 3, "status", "received"))
    trace_case("TRC-16", lambda doc: tput(doc, "packets", {}))
    trace_case("TRC-17", lambda doc: tpacket(doc, 1, "payload_bytes", True))
    trace_case("TRC-18", lambda doc: tpacket(doc, 0, "rtp_timestamp", -1))
    trace_case("TRC-19", lambda doc: tpacket(doc, 2, "rtp_timestamp", 960))

    # Strict JSON adverse cases.
    for case_id, text, code in (
            ("JSON-01", '{"a":1,"a":2}', "duplicate_json_key:a"),
            ("JSON-02", '{"a":NaN}', "nonfinite_json_constant:NaN"),
            ("JSON-03", '{"a":Infinity}', "nonfinite_json_constant:Infinity"),
            ("JSON-04", '[]', "json_root_not_object")):
        try:
            loads_strict(text)
        except ValueError as error:
            message = str(error)
        else:  # pragma: no cover - the fixtures are malformed by design
            message = "accepted"
        cases.append({
            "id": case_id, "kind": "strict_json", "status": "rejected",
            "code": code, "field": "",
            "message_matches": message == code,
            "state_unchanged": True, "qualifies": False,
            "evidence_class": "synthetic_admission_control"})

    manifest_control = validate_manifest(_manifest_control(),
                                         probe_paths=False)
    trace_control = validate_trace(_trace_control())
    controls = [
        {"id": "CTL-01", "kind": "manifest",
         "status": "accepted_schema_control",
         "code": manifest_control["code"],
         "checks": manifest_control["checks"],
         "artifacts_probed": False,
         "evidence_class": "synthetic_schema_control_not_evidence",
         "qualifies": False,
         "runtime_loaded": False},
        {"id": "CTL-02", "kind": "trace",
         "status": "accepted_schema_control",
         "code": trace_control["code"],
         "checks": trace_control["checks"],
         "packets_admitted": len(_trace_control()["packets"]),
         "reordering_performed": False,
         "playout_performed": False,
         "timing_analysis_performed": False,
         "evidence_class": "synthetic_schema_control_not_evidence",
         "qualifies": False},
    ]
    return {"cases": cases, "controls": controls}


# --------------------------------------------------------------------------
# Canonical report
# --------------------------------------------------------------------------
def _artifact_rows() -> list[dict]:
    return [{
        "id": artifact["id"],
        "kind": artifact["kind"],
        "requirement": artifact["requirement"],
        "present": False,
        "verified": False,
        "sha256": None,
        "blocked": True,
    } for artifact in REQUIRED_ARTIFACTS]


def _blocker_rows() -> list[dict]:
    return [{
        "id": blocker["id"],
        "artifact_id": blocker["artifact_id"],
        "statement": blocker["statement"],
        "required_action": blocker["required_action"],
        "linked_gates": list(blocker["linked_gates"]),
        "status": "open",
        "qualifies": False,
    } for blocker in EXACT_BLOCKERS]


def _gate_rows() -> list[dict]:
    identity = {"task_id": TASK, "component_id": COMPONENT_ID, "mode": MODE}
    return [{
        "id": gate["id"],
        "title": gate["title"],
        "statement": gate["statement"],
        "reopen_condition": gate["reopen_condition"],
        "status": "blocked",
        "qualifies": False,
        "linked_row": identity,
    } for gate in RELEASE_GATES]


def linked_row_identity() -> dict:
    projection = {field: BOARD_ROW_PROJECTION[field]
                  for field in BOARD_ROW_FIELDS}
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "selector": "stable-row-identity/0.1:" + ",".join(BOARD_ROW_FIELDS),
        "gating": "stable_identity_only",
        "mutable_fields_excluded": ["status", "owner", "claim", "review",
                                    "handoff", "blocked_reason",
                                    "dispatch_priority"],
        "board_file_pinned": False,
        "board_status_gates_anything": False,
    }


def build_report() -> dict:
    contract = read_strict_json(HERE / "contract.json")
    probes = absence_probes(AUDIO_ROOT)
    controls = admission_controls()
    rejected = [case for case in controls["cases"]
                if case["status"] == "rejected"]
    accepted_controls = [case for case in controls["controls"]
                         if case["status"] == "accepted_schema_control"]
    gates = _gate_rows()
    artifacts = _artifact_rows()
    blockers = _blocker_rows()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "task_id": TASK,
        "task_title": TASK_TITLE,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "decision": "DEFER",
        "disposition": {
            "status": "incomplete",
            "decision": "DEFER",
            "qualification_status": "not_qualified",
            "promotion": "defer",
            "production_exposure": "DEFER",
            "proposal_only": True,
            "incomplete": True,
            "not_qualified": True,
            "expose_as_processor": False,
            "registered": False,
            "default_enabled": False,
            "missing_result_qualifies": False,
        },
        "boundary": {
            "registered": False,
            "enabled_by_default": False,
            "default_selected": False,
            "public_api_abi_change": False,
            "provider_registration": False,
            "descriptor_registry_change": False,
            "shared_cmakelists_change": False,
            "ci_workflow_change": False,
            "installed_v0_behavior_change": False,
            "processor_exposure": False,
            "task_local_only": True,
            "files_outside_task_directory_written": False,
        },
        "public_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
            "preserved": True,
            "sdk_callback_invoked": False,
        },
        "scope": {
            "source_present": False,
            "runtime_present": False,
            "runtime_executed": False,
            "codec_runtime_executed": False,
            "real_corpus": False,
            "real_trace": False,
            "reordering_performed": False,
            "playout_performed": False,
            "jitter_measured": False,
            "latency_measured": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
            "release_claim": False,
            "network_used": False,
            "download_attempted": False,
        },
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
            "conclusion": (
                "No WebRTC NetEq source, runtime, adapter, trace or codec "
                "asset exists at any fixed probe location."),
        },
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "tool_profile": {
            "profile": "tool",
            "rows": [dict(row) for row in TOOL_PROFILE_ROWS],
            "runtime_version": None,
            "install_location": None,
            "provenance": None,
            "clean_checkout_verified": False,
            "typical_use_performed": False,
            "caller_owned_inputs_admitted": False,
            "malformed_inputs_checked": True,
            "missing_optional_selection_exercised": False,
            "compile_build_evidence": False,
            "synthetic_runtime_evidence": False,
            "measured_workload_support": False,
            "status": "blocked",
        },
        "admission": {
            "policy": "task_local_fail_closed_admission_not_runtime_behavior",
            "cases": controls["cases"],
            "schema_controls": controls["controls"],
            "summary": {
                "case_count": len(controls["cases"]),
                "rejected_count": len(rejected),
                "accepted_schema_controls": len(accepted_controls),
                "qualifying_results": 0,
                "state_advanced_on_rejection": any(
                    case["state_unchanged"] is not True for case in rejected),
                "runtime_invoked": False,
                "replay_performed": False,
            },
        },
        "qualification": {
            "all_release_gates_blocked": True,
            "real_source_present": False,
            "real_runtime_present": False,
            "real_trace_present": False,
            "real_result_present": False,
            "reordering_or_playout_result": False,
            "codec_integration_result": False,
            "listening_result": False,
            "timing_result": False,
            "benchmark_result": False,
            "missing_result_promoted": False,
            "not_qualified": True,
        },
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "gates": gates,
        "linked_row_identity": linked_row_identity(),
        "exact_scope": {
            "task_local_evidence_only": True,
            "single_component": COMPONENT_ID,
            "provider_work": False,
            "runtime_work": False,
            "release_work": False,
            "write_scope": WRITE_SCOPE,
        },
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "regeneration": {
            "runs": 3,
            "byte_identical": True,
            "cold_start_processes": True,
            "canonical_json": True,
            "sorted_keys": True,
            "compact_separators": True,
            "trailing_newline": True,
        },
        "reproduction": {
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
            "report": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
        },
    }
    return report


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_id")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("component") != COMPONENT_ID:
        raise ValueError("contract_component")
    if contract.get("profile") != PROFILE or contract.get("mode") != MODE:
        raise ValueError("contract_profile_or_mode")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != "incomplete":
        raise ValueError("contract_status")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification_status")
    if len(contract.get("release_gates", [])) != 8:
        raise ValueError("contract_gate_count")
    if any(gate.get("status") != "blocked" for gate in contract["release_gates"]):
        raise ValueError("contract_gate_not_blocked")
    if contract.get("board_row_projection") != BOARD_ROW_PROJECTION:
        raise ValueError("contract_board_row_projection")
    for key, value in (("source_pins", SOURCE_PINS),
                       ("boundary_pins", BOUNDARY_PINS)):
        if contract.get(key) != value:
            raise ValueError("contract_pin_table:" + key)
