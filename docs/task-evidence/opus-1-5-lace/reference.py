# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-OPUS-1-5-LACE (Opus 1.5 LACE).

This module is standard-library only and deterministic. It contains no Opus
1.5 source, libopus binary, OSCE/LACE model data, weights, decoder runtime,
codec stream, real speech corpus or vendor result. It records the exact
external blocker, probes a fixed list of task-local paths to evidence the
absence, validates a caller-supplied restoration cohort manifest with a
fail-closed admission boundary, and builds the canonical report.

Nothing here is a LACE implementation, an upstream-parity result, a quality
measurement, a listening result, a device-timing result, a benchmark or a
release claim.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-OPUS-1-5-LACE"
COMPONENT_ID = "opus-1-5-lace"
TASK_TITLE = "Opus 1.5 LACE"
CONTRACT_ID = "audio-sdk/opus-1-5-lace-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "restoration"
MODE = "feasibility"
BASE_COMMIT = "c7b157247be6e4ceea0ab5b04ff4463de1566146"
BRANCH = "swarm/SDK-OPUS-1-5-LACE"
WRITE_SCOPE = "docs/task-evidence/opus-1-5-lace/ only"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
DEFAULT_AUDIO_ROOT = HERE.parents[5]
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT", str(DEFAULT_AUDIO_ROOT))).resolve()
TASK_PREFIX = "docs/task-evidence/opus-1-5-lace/"

# Immutable inputs. `source:` rows are workspace-relative; the rest are
# SDK-worktree-relative. The mutable shared board is deliberately excluded from
# the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/distortion_restoration_20261028.md":
        "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
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
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md":
        "ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/report.json":
        "ec4c9ea5e46e02d9866920458b4d6365d300d8bcd626d2e05bf7f4c4955a080e",
}

# Only stable, non-mutable identity fields are projected. `status`, `owner`,
# `claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` never
# enter canonical bytes and never gate this package.
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
}
LINKED_ROWS = (
    BOARD_ROW_PROJECTION,
    {
        "id": "SDK-OPUS-1-5-NOLACE",
        "title": "Opus 1.5 NoLACE",
        "component": "opus-1-5-nolace",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-OPUS-1-4-STANDARD-DECODER-PLC",
        "title": "Opus 1.4 standard decoder PLC",
        "component": "opus-1-4-standard-decoder-plc",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE",
        "title": "Opus packetization, FEC, DTX and comfort noise",
        "component": "opus-packetization-fec-dtx-and-comfort-noise",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
)

# Fixed, bounded absence probes. No recursive workspace walk is performed and
# no download is attempted. Any present path makes report generation fail.
ABSENCE_PROBES = (
    "data/checkouts/opus",
    "data/checkouts/opus-1.5",
    "data/checkouts/libopus",
    "data/checkouts/osce",
    "adapters/opus-1-5-lace",
    "adapters/osce",
    "third_party/opus",
    "third_party/libopus",
    "third_party/osce",
    "deps/opus",
    "deps/libopus",
    "modules/opus",
    "core/osce",
    "dnn/lace",
    "dnn/nolace",
    "src/opus_decoder.c",
    "include/opus.h",
    "data/envs/clearvoice/lib/python3.11/site-packages/cv2/.dylibs/libopus.0.dylib",
    "research/voice-enhancement-20261101/agent-opus-plc/weights",
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "permitted_source",
        "requirement": (
            "Exact permitted Opus 1.5 source tree, including the OSCE/LACE "
            "and NoLACE decoder paths, pinned by an immutable 40-hex revision "
            "and an immutable archive SHA-256."),
    },
    {
        "id": "ART-02",
        "kind": "license_and_model_terms",
        "requirement": (
            "The upstream license text, copyright notices, model-data terms "
            "and complete third-party notice bundle that apply to the pinned "
            "revision, with an explicit rights review."),
    },
    {
        "id": "ART-03",
        "kind": "built_decoder_runtime",
        "requirement": (
            "A reproducible pinned libopus 1.5 build with its exact decoder "
            "option name, accepted values, default state and build artifact "
            "SHA-256."),
    },
    {
        "id": "ART-04",
        "kind": "lace_assets_and_runtime",
        "requirement": (
            "The exact LACE/NoLACE model assets or compiled model blobs, "
            "their inference runtime, feature/state geometry and per-asset "
            "SHA-256, with redistribution and product-use terms."),
    },
    {
        "id": "ART-05",
        "kind": "low_bitrate_traffic_cohort",
        "requirement": (
            "A rights-cleared frozen cohort of genuine low-bitrate Opus "
            "traffic with packet metadata, erasure and bandwidth strata, and "
            "the corresponding clean/audio packet baseline."),
    },
    {
        "id": "ART-06",
        "kind": "quality_and_runtime_harness",
        "requirement": (
            "An agreed task-specific quality, independent listening, output "
            "peak and target-runtime timing/resource protocol with margins, "
            "deadlines and limits."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-01",
        "statement": (
            "No permitted Opus 1.5 source snapshot exists in this workspace. "
            "Every fixed absence probe is missing, and no revision or "
            "archive digest can be pinned from a local artifact."),
        "required_action": (
            "Supply the exact Opus 1.5 source revision and immutable archive "
            "with matching SHA-256, from a source root that permits review."),
        "linked_gates": ["RG-01", "RG-03"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-02",
        "statement": (
            "The upstream license, copyright, model-data terms and notice "
            "bundle are absent, so no redistribution or product-use scope "
            "for a LACE artifact can be reviewed."),
        "required_action": (
            "Supply the complete license/notices/model-terms bundle for the "
            "pinned revision and record an explicit rights decision."),
        "linked_gates": ["RG-02"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-03",
        "statement": (
            "No built libopus 1.5 runtime, installed location or reproducible "
            "build recipe is present. The exact decoder option that selects "
            "LACE and its default state cannot be exercised or verified."),
        "required_action": (
            "Supply a reproducible pinned build and identify the exact "
            "decoder option, accepted values, default state and artifact "
            "digest from the pinned source."),
        "linked_gates": ["RG-03", "RG-07"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-04",
        "statement": (
            "No LACE/NoLACE model asset, compiled model blob, inference "
            "runtime or feature/state geometry is present. Nothing was "
            "downloaded, reconstructed or substituted."),
        "required_action": (
            "Supply the exact model assets and inference runtime with "
            "per-asset SHA-256, geometry, provenance and permitted-use "
            "terms."),
        "linked_gates": ["RG-04", "RG-03"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "statement": (
            "No rights-cleared genuine low-bitrate Opus traffic, packet "
            "metadata, degradation/erasure/bandwidth strata or matching "
            "clean/audio packet baseline is present."),
        "required_action": (
            "Supply a rights-cleared immutable cohort with provenance, "
            "packet metadata, declared strata and a corresponding clean or "
            "packet baseline."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "statement": (
            "No task-specific quality, independent listening, output-peak or "
            "target-runtime timing/resource protocol and no agreed margins, "
            "deadlines or limits exist, so no result can qualify."),
        "required_action": (
            "Agree and staff the task-specific quality, listening, peak and "
            "target-runtime protocols, margins, deadlines and resource limits "
            "before collecting results."),
        "linked_gates": ["RG-06", "RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "upstream_source_and_revision_pin",
        "statement": (
            "An exact permitted Opus 1.5 source revision and immutable "
            "archive are pinned before any implementation claim."),
        "reopen_condition": (
            "The exact source revision, tree and archive digests are recorded "
            "and the source root permits local review."),
    },
    {
        "id": "RG-02",
        "title": "upstream_license_model_terms_and_notices",
        "statement": (
            "A reviewed license, model-data terms and notice bundle exists "
            "for the pinned revision."),
        "reopen_condition": (
            "The complete license/notices/model-terms bundle is supplied, "
            "reviewed and its approved scope recorded."),
    },
    {
        "id": "RG-03",
        "title": "exact_build_and_decoder_option_parity",
        "statement": (
            "A reproducible build and the exact LACE decoder option, value "
            "and default state are verified."),
        "reopen_condition": (
            "Build and install the pinned revision and map the exact decoder "
            "option and default behavior to this boundary."),
    },
    {
        "id": "RG-04",
        "title": "lace_asset_and_runtime_integrity",
        "statement": (
            "Every LACE/NoLACE model asset and its inference runtime are "
            "pinned and integrity-checked."),
        "reopen_condition": (
            "Pin each asset and runtime by SHA-256, verify geometry and "
            "provenance, and confirm permitted use."),
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_low_bitrate_cohort",
        "statement": (
            "A rights-cleared genuine low-bitrate traffic cohort and clean "
            "baseline are frozen before any quality result."),
        "reopen_condition": (
            "The immutable cohort, metadata, strata and corresponding clean "
            "or packet baseline are supplied and reviewed."),
    },
    {
        "id": "RG-06",
        "title": "task_specific_quality_and_independent_listening",
        "statement": (
            "Task-specific quality and independent listening are completed "
            "for the exact conditions and rights scope."),
        "reopen_condition": (
            "Pinned scorers and an approved listening protocol/panel produce "
            "reviewed results on the frozen cohort."),
    },
    {
        "id": "RG-07",
        "title": "target_runtime_timing_peaks_and_resources",
        "statement": (
            "Target-runtime timing, output-peak bounds and resource limits "
            "are measured, not inferred."),
        "reopen_condition": (
            "Paced target-runtime runs record timing, peaks, CPU, memory and "
            "deadline behavior against agreed limits."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "statement": (
            "Opt-in provider intake, an explicit public-surface decision, "
            "independent review and release approval are complete."),
        "reopen_condition": (
            "A separate versioned intake accepts the component with an OFF "
            "default, records the public-surface decision and passes "
            "independent exact-head review."),
    },
)

RESTORATION_PROFILE_ROWS = (
    {
        "id": "RST-01",
        "requirement": (
            "Freeze corruption, metadata and the corresponding clean/audio "
            "packet baseline."),
        "status": "blocked",
        "evidence": (
            "No genuine low-bitrate traffic, packet metadata or clean "
            "baseline is present; the manifest schema admits none."),
    },
    {
        "id": "RST-02",
        "requirement": (
            "Stratify by degradation, erasure burst and bandwidth."),
        "status": "blocked",
        "evidence": (
            "Strata are declared in the admission schema only; no real "
            "degradation, burst or bandwidth cohort exists."),
    },
    {
        "id": "RST-03",
        "requirement": (
            "Report discrete concealment/validity and decoded intervals."),
        "status": "blocked",
        "evidence": (
            "No decoder runs, so no received, lost, concealed, valid or "
            "decoded interval is observed or reported."),
    },
    {
        "id": "RST-04",
        "requirement": (
            "Report task-specific quality on genuine low-bitrate traffic."),
        "status": "blocked",
        "evidence": (
            "No LACE output, clean reference, pinned scorer or listening "
            "result exists."),
    },
    {
        "id": "RST-05",
        "requirement": "Bound output peaks and timing.",
        "status": "blocked",
        "evidence": (
            "No output samples and no runtime measurement exist, so no peak "
            "or timing bound can be reported."),
    },
)

NON_CLAIMS = (
    "No Opus 1.5, libopus, OSCE, LACE or NoLACE source, binary, model asset, "
    "weight, decoder runtime or vendor result is present or executed.",
    "No genuine low-bitrate Opus traffic, packet capture, clean reference, "
    "real corpus or media file is present or read.",
    "No LACE or NoLACE postfilter is implemented, approximated, substituted "
    "or compared; no generic postfilter stands in for it.",
    "No quality, intelligibility, naturalness, speech-preservation, "
    "listening, device-timing, benchmark or release result is produced.",
    "No provider is registered, exposed, enabled by default or selected as a "
    "descriptor default; no public API, ABI, registry, shared build or CI "
    "change is made.",
    "No missing, synthetic or schema-control result is promoted or treated as "
    "evidence for the candidate.",
)

PROFILE_PHRASES = (
    "Freeze corruption, metadata and corresponding clean/audio packet "
    "baseline.",
    "Stratify by degradation, erasure burst and bandwidth.",
    "Report discrete concealment/validity, decoded intervals, task-specific "
    "quality and bounds on output peaks and timing.",
)

# Admission manifest is a task-local schema, not an SDK or Opus contract.
MANIFEST_SCHEMA_ID = "audio-sdk/opus-1-5-lace-cohort/0.1"
MANIFEST_FIELDS = (
    "schema_id",
    "cohort_id",
    "source_revision",
    "source_sha256",
    "source_path",
    "license_path",
    "license_sha256",
    "runtime_path",
    "runtime_sha256",
    "decoder_option",
    "traffic",
    "clean_reference",
    "strata",
    "packets",
)
DECODER_OPTION_FIELDS = ("name", "value", "source_path", "source_sha256")
TRAFFIC_FIELDS = (
    "corpus_path",
    "corpus_sha256",
    "rights_reference",
    "codec",
    "codec_version",
    "sample_rate_hz",
    "channels",
    "packet_duration_us",
    "bitrate_bps",
)
CLEAN_REFERENCE_FIELDS = ("path", "sha256", "alignment", "offset_samples")
STRATUM_FIELDS = ("id", "degradation", "bandwidth_hz", "burst_frames")
PACKET_FIELDS = (
    "index",
    "status",
    "valid_samples",
    "decoded_samples",
    "payload_sha256",
)
PACKET_STATUSES = ("received", "lost", "concealed")
DEGRADATIONS = ("low_bitrate", "packet_loss", "bandwidth_limited", "mixed")
ALIGNMENTS = ("sample_exact", "declared_offset")
OPUS_SAMPLE_RATES = (8000, 12000, 16000, 24000, 48000)
MAX_PACKETS = 100000
MIN_PACKET_US = 2500
MAX_PACKET_US = 120000
MIN_BITRATE_BPS = 6000
MAX_BITRATE_BPS = 512000
MAX_BANDWIDTH_HZ = 48000
MAX_BURST_FRAMES = 1000
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


# --------------------------------------------------------------------------
# Strict JSON and digests
# --------------------------------------------------------------------------
def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
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


def canonical_text(document: Any) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def canonical_bytes(document: Any) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: Any) -> str:
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
    return {field: rows[0].get(field) for field in BOARD_ROW_FIELDS}


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows_digest(rows: tuple[dict, ...] = LINKED_ROWS) -> str:
    return object_digest([{field: row.get(field) for field in BOARD_ROW_FIELDS}
                          for row in rows])


def absence_probes(audio_root: Path, probes: tuple[str, ...] = ABSENCE_PROBES,
                   worktree: Path | None = None) -> list[dict]:
    """Return the fixed probe inventory; any present path blocks shipping."""
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
# Admission validator (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _reject(code: str, field: str = "") -> dict:
    return {"accepted": False, "code": code, "field": field,
            "checks": 0, "state_unchanged": True}


def _accept(checks: int) -> dict:
    return {"accepted": True, "code": "ok", "field": "", "checks": checks,
            "state_unchanged": True}


def _path_is_canonical(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    if not os.path.isabs(value):
        return False
    return os.path.normpath(value) == value


def _exact_object(value: Any, fields: tuple[str, ...]) -> str:
    if not isinstance(value, dict):
        return "invalid_object"
    if set(value) != set(fields):
        return ("missing_field" if set(fields) - set(value) else "unknown_field")
    return ""


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed cohort admission. No audio is read and no decoder runs."""
    checks = 0
    if not isinstance(document, dict):
        return _reject("manifest_not_object")

    if set(document) != set(MANIFEST_FIELDS):
        missing = sorted(set(MANIFEST_FIELDS) - set(document))
        extra = sorted(set(document) - set(MANIFEST_FIELDS))
        return _reject("missing_field" if missing else "unknown_field",
                       missing[0] if missing else extra[0])
    checks += 1

    if document["schema_id"] != MANIFEST_SCHEMA_ID:
        return _reject("invalid_schema", "schema_id")
    if not isinstance(document["cohort_id"], str) \
            or not SLUG.match(document["cohort_id"]):
        return _reject("invalid_value", "cohort_id")
    if not isinstance(document["source_revision"], str) \
            or not HEX40.match(document["source_revision"]):
        return _reject("invalid_value", "source_revision")
    for field in ("source_sha256", "license_sha256", "runtime_sha256"):
        if not isinstance(document[field], str) \
                or not HEX64.match(document[field]):
            return _reject("invalid_value", field)
    for field in ("source_path", "license_path", "runtime_path"):
        if not _path_is_canonical(document[field]):
            return _reject("invalid_path", field)
    checks += 7

    option = document["decoder_option"]
    code = _exact_object(option, DECODER_OPTION_FIELDS)
    if code:
        return _reject(code, "decoder_option")
    if not isinstance(option["name"], str) or not SLUG.match(option["name"]):
        return _reject("invalid_value", "decoder_option.name")
    value = option["value"]
    if not (isinstance(value, bool) or _is_int(value)
            or (isinstance(value, str) and bool(value))):
        return _reject("invalid_type", "decoder_option.value")
    if not _path_is_canonical(option["source_path"]):
        return _reject("invalid_path", "decoder_option.source_path")
    if not isinstance(option["source_sha256"], str) \
            or not HEX64.match(option["source_sha256"]):
        return _reject("invalid_value", "decoder_option.source_sha256")
    checks += 5

    traffic = document["traffic"]
    code = _exact_object(traffic, TRAFFIC_FIELDS)
    if code:
        return _reject(code, "traffic")
    if not _path_is_canonical(traffic["corpus_path"]):
        return _reject("invalid_path", "traffic.corpus_path")
    if not isinstance(traffic["corpus_sha256"], str) \
            or not HEX64.match(traffic["corpus_sha256"]):
        return _reject("invalid_value", "traffic.corpus_sha256")
    if not isinstance(traffic["rights_reference"], str) \
            or not traffic["rights_reference"].strip() \
            or len(traffic["rights_reference"]) > 200 \
            or any(ord(char) < 32 for char in traffic["rights_reference"]):
        return _reject("invalid_value", "traffic.rights_reference")
    if traffic["codec"] != "opus":
        return _reject("invalid_value", "traffic.codec")
    if traffic["codec_version"] != "1.5":
        return _reject("invalid_value", "traffic.codec_version")
    if not _is_int(traffic["sample_rate_hz"]) \
            or traffic["sample_rate_hz"] not in OPUS_SAMPLE_RATES:
        return _reject("invalid_value", "traffic.sample_rate_hz")
    if not _is_int(traffic["channels"]) or traffic["channels"] not in (1, 2):
        return _reject("invalid_value", "traffic.channels")
    if not _is_int(traffic["packet_duration_us"]) \
            or not MIN_PACKET_US <= traffic["packet_duration_us"] <= MAX_PACKET_US \
            or traffic["packet_duration_us"] % 250:
        return _reject("invalid_value", "traffic.packet_duration_us")
    if not _is_int(traffic["bitrate_bps"]) \
            or not MIN_BITRATE_BPS <= traffic["bitrate_bps"] <= MAX_BITRATE_BPS:
        return _reject("invalid_value", "traffic.bitrate_bps")
    checks += 9

    clean = document["clean_reference"]
    code = _exact_object(clean, CLEAN_REFERENCE_FIELDS)
    if code:
        return _reject(code, "clean_reference")
    if not _path_is_canonical(clean["path"]):
        return _reject("invalid_path", "clean_reference.path")
    if not isinstance(clean["sha256"], str) or not HEX64.match(clean["sha256"]):
        return _reject("invalid_value", "clean_reference.sha256")
    if clean["alignment"] not in ALIGNMENTS:
        return _reject("invalid_value", "clean_reference.alignment")
    if not _is_int(clean["offset_samples"]) or clean["offset_samples"] < 0:
        return _reject("invalid_value", "clean_reference.offset_samples")
    if clean["alignment"] == "sample_exact" and clean["offset_samples"] != 0:
        return _reject("invalid_value", "clean_reference.offset_samples")
    checks += 5

    strata = document["strata"]
    if not isinstance(strata, list) or not strata:
        return _reject("invalid_value", "strata")
    seen_ids: set[str] = set()
    for stratum in strata:
        code = _exact_object(stratum, STRATUM_FIELDS)
        if code:
            return _reject(code, "strata")
        if not isinstance(stratum["id"], str) or not SLUG.match(stratum["id"]):
            return _reject("invalid_value", "strata.id")
        if stratum["id"] in seen_ids:
            return _reject("invalid_value", "strata.id")
        seen_ids.add(stratum["id"])
        if stratum["degradation"] not in DEGRADATIONS:
            return _reject("invalid_value", "strata.degradation")
        if not _is_int(stratum["bandwidth_hz"]) \
                or not 0 <= stratum["bandwidth_hz"] <= MAX_BANDWIDTH_HZ:
            return _reject("invalid_value", "strata.bandwidth_hz")
        if not _is_int(stratum["burst_frames"]) \
                or not 0 <= stratum["burst_frames"] <= MAX_BURST_FRAMES:
            return _reject("invalid_value", "strata.burst_frames")
    checks += len(strata) * 4

    packets = document["packets"]
    if not isinstance(packets, list) or not packets:
        return _reject("invalid_value", "packets")
    if len(packets) > MAX_PACKETS:
        return _reject("invalid_value", "packets")
    received = 0
    for index, packet in enumerate(packets):
        code = _exact_object(packet, PACKET_FIELDS)
        if code:
            return _reject(code, "packets")
        if not _is_int(packet["index"]) or packet["index"] != index:
            return _reject("invalid_value", "packets.index")
        if packet["status"] not in PACKET_STATUSES:
            return _reject("invalid_value", "packets.status")
        for field in ("valid_samples", "decoded_samples"):
            if not _is_int(packet[field]) or packet[field] < 0:
                return _reject("invalid_type", "packets." + field)
        if not isinstance(packet["payload_sha256"], str) \
                or not HEX64.match(packet["payload_sha256"]):
            return _reject("invalid_value", "packets.payload_sha256")
        if packet["status"] == "received":
            received += 1
            if packet["valid_samples"] <= 0 \
                    or packet["decoded_samples"] != packet["valid_samples"] \
                    or packet["payload_sha256"] == EMPTY_SHA256:
                return _reject("invalid_value", "packets.received")
        else:
            if packet["valid_samples"] != 0 \
                    or packet["payload_sha256"] != EMPTY_SHA256:
                return _reject("invalid_value", "packets." + packet["status"])
    if received == 0:
        return _reject("invalid_value", "packets.received")
    checks += len(packets) * 5

    if probe_paths:
        probes = (
            ("source_path", "source_sha256"),
            ("license_path", "license_sha256"),
            ("runtime_path", "runtime_sha256"),
        )
        for path_field, digest_field in probes:
            path = Path(document[path_field])
            if not path.is_file():
                return _reject("probe_missing", path_field)
            if sha256_file(path) != document[digest_field]:
                return _reject("probe_digest_mismatch", path_field)
        option_path = Path(option["source_path"])
        if not option_path.is_file():
            return _reject("probe_missing", "decoder_option.source_path")
        if sha256_file(option_path) != option["source_sha256"]:
            return _reject("probe_digest_mismatch", "decoder_option.source_path")
        corpus_path = Path(traffic["corpus_path"])
        if not corpus_path.is_file():
            return _reject("probe_missing", "traffic.corpus_path")
        if sha256_file(corpus_path) != traffic["corpus_sha256"]:
            return _reject("probe_digest_mismatch", "traffic.corpus_path")
        clean_path = Path(clean["path"])
        if not clean_path.is_file():
            return _reject("probe_missing", "clean_reference.path")
        if sha256_file(clean_path) != clean["sha256"]:
            return _reject("probe_digest_mismatch", "clean_reference.path")
        checks += 7
    return _accept(checks)


def _manifest_control() -> dict:
    """Structural schema control. It is not evidence and never qualifies."""
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "schema_control",
        "source_revision": "0" * 40,
        "source_sha256": "0" * 64,
        "source_path": "/caller/opussrc",
        "license_path": "/caller/opussrc/COPYING",
        "license_sha256": "1" * 64,
        "runtime_path": "/caller/lib/libopus.dylib",
        "runtime_sha256": "2" * 64,
        "decoder_option": {
            "name": "lace_enable",
            "value": True,
            "source_path": "/caller/opussrc/src/opus_decoder.c",
            "source_sha256": "3" * 64,
        },
        "traffic": {
            "corpus_path": "/caller/cohort/low_bitrate",
            "corpus_sha256": "4" * 64,
            "rights_reference": "synthetic-schema-control-no-rights",
            "codec": "opus",
            "codec_version": "1.5",
            "sample_rate_hz": 48000,
            "channels": 1,
            "packet_duration_us": 20000,
            "bitrate_bps": 12000,
        },
        "clean_reference": {
            "path": "/caller/cohort/clean",
            "sha256": "5" * 64,
            "alignment": "sample_exact",
            "offset_samples": 0,
        },
        "strata": [
            {"id": "s1", "degradation": "low_bitrate",
             "bandwidth_hz": 8000, "burst_frames": 0},
            {"id": "s2", "degradation": "packet_loss",
             "bandwidth_hz": 8000, "burst_frames": 3},
        ],
        "packets": [
            {"index": 0, "status": "received", "valid_samples": 960,
             "decoded_samples": 960, "payload_sha256": "6" * 64},
            {"index": 1, "status": "lost", "valid_samples": 0,
             "decoded_samples": 960, "payload_sha256": EMPTY_SHA256},
            {"index": 2, "status": "concealed", "valid_samples": 0,
             "decoded_samples": 960, "payload_sha256": EMPTY_SHA256},
            {"index": 3, "status": "received", "valid_samples": 960,
             "decoded_samples": 960, "payload_sha256": "7" * 64},
        ],
    }


def admission_controls() -> dict:
    """Build the frozen adverse matrix plus one structural schema control."""
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

    def drop(document, field):
        del document[field]
        return validate_manifest(document, probe_paths=False)

    def put(document, field, value):
        document[field] = value
        return validate_manifest(document, probe_paths=False)

    def nested(document, section, field, value):
        document[section][field] = value
        return validate_manifest(document, probe_paths=False)

    cases.append({
        "id": "MISS-01", "kind": "manifest", "status": "rejected",
        "code": validate_manifest(None, probe_paths=False)["code"],
        "field": "", "state_unchanged": True, "qualifies": False,
        "evidence_class": "synthetic_admission_control"})
    manifest_case("INV-01", lambda doc: drop(doc, "source_sha256"))
    manifest_case("INV-02", lambda doc: put(doc, "extra", "value"))
    manifest_case("INV-03", lambda doc: put(doc, "schema_id", "wrong"))
    manifest_case("INV-04", lambda doc: put(doc, "cohort_id", "Bad Id"))
    manifest_case("INV-05", lambda doc: put(doc, "source_revision", "A" * 40))
    manifest_case("INV-06", lambda doc: put(doc, "source_sha256", "0" * 63))
    manifest_case("INV-07", lambda doc: put(doc, "source_path", "relative/src"))
    manifest_case("INV-08", lambda doc: put(doc, "license_path",
                                            "/caller/../COPYING"))
    manifest_case("INV-09", lambda doc: put(doc, "runtime_sha256", "x" * 64))
    manifest_case("INV-10", lambda doc: put(doc, "decoder_option", "lace"))
    manifest_case("INV-11", lambda _doc: validate_manifest(
        _without_nested("decoder_option", "name"), probe_paths=False))
    manifest_case("INV-12", lambda doc: nested(doc, "decoder_option", "value",
                                               1.5))
    manifest_case("INV-13", lambda doc: nested(doc, "decoder_option", "value",
                                               None))
    manifest_case("INV-14", lambda doc: nested(doc, "traffic", "codec", "aac"))
    manifest_case("INV-15", lambda doc: nested(doc, "traffic",
                                               "codec_version", "1.4"))
    manifest_case("INV-16", lambda doc: nested(doc, "traffic",
                                               "sample_rate_hz", 44100))
    manifest_case("INV-17", lambda doc: nested(doc, "traffic", "channels", 0))
    manifest_case("INV-18", lambda doc: nested(doc, "traffic",
                                               "packet_duration_us", 0))
    manifest_case("INV-19", lambda doc: nested(doc, "traffic",
                                               "packet_duration_us", 1001))
    manifest_case("INV-20", lambda doc: nested(doc, "traffic", "bitrate_bps",
                                               1000))
    manifest_case("INV-21", lambda doc: nested(doc, "traffic", "bitrate_bps",
                                               True))
    manifest_case("INV-22", lambda doc: nested(doc, "clean_reference",
                                               "alignment", "guess"))
    manifest_case("INV-23", lambda doc: nested(doc, "clean_reference",
                                               "offset_samples", 5))
    manifest_case("INV-24", lambda doc: put(doc, "strata", []))
    manifest_case("INV-25", lambda doc: put(
        doc, "strata", [dict(doc["strata"][0]), dict(doc["strata"][0])]))
    manifest_case("INV-26", lambda _doc: validate_manifest(
        _with_stratum_burst(-1), probe_paths=False))
    manifest_case("INV-27", lambda doc: put(doc, "packets", []))
    manifest_case("INV-28", lambda doc: put(
        doc, "packets", list(reversed(doc["packets"]))))
    manifest_case("INV-29", lambda _doc: validate_manifest(
        _with_packet_field(0, "status", "missing"), probe_paths=False))
    manifest_case("INV-30", lambda doc: validate_manifest(
        _with_packet_field(1, "valid_samples", 1), probe_paths=False))
    manifest_case("INV-31", lambda doc: validate_manifest(
        _with_packet_field(0, "payload_sha256", EMPTY_SHA256),
        probe_paths=False))
    manifest_case("INV-32", lambda doc: validate_manifest(
        _with_packet_field(0, "decoded_samples", 480), probe_paths=False))
    manifest_case("INV-33", lambda doc: validate_manifest(
        _with_packet_field(0, "valid_samples", True), probe_paths=False))
    manifest_case("INV-34", lambda doc: validate_manifest(
        _with_packet_field(0, "valid_samples", float("nan")),
        probe_paths=False))
    manifest_case("INV-35", lambda doc: put(doc, "packets", {}))
    manifest_case("PRS-01", lambda doc: validate_manifest(doc,
                                                          probe_paths=True))

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

    control = validate_manifest(_manifest_control(), probe_paths=False)
    controls = [{
        "id": "CTL-01",
        "kind": "manifest",
        "status": "accepted_schema_control",
        "code": control["code"],
        "checks": control["checks"],
        "artifacts_probed": False,
        "runtime_loaded": False,
        "audio_read": False,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "qualifies": False,
    }]
    return {"cases": cases, "controls": controls}


def _without_nested(section: str, field: str) -> dict:
    document = _manifest_control()
    del document[section][field]
    return document


def _with_stratum_burst(value: int) -> dict:
    document = _manifest_control()
    document["strata"][0]["burst_frames"] = value
    return document


def _with_packet_field(index: int, field: str, value: Any) -> dict:
    document = _manifest_control()
    document["packets"][index][field] = value
    return document


# --------------------------------------------------------------------------
# Canonical contract and report
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
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
    }


def qualification_block() -> dict:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "all_release_gates_blocked": True,
        "real_source_present": False,
        "real_runtime_present": False,
        "real_model_asset_present": False,
        "real_low_bitrate_traffic_present": False,
        "real_result_present": False,
        "lace_implementation_result": False,
        "decoder_option_verified": False,
        "concealment_or_validity_result": False,
        "quality_result": False,
        "listening_result": False,
        "timing_or_peak_result": False,
        "benchmark_result": False,
        "missing_result_promoted": False,
        "not_qualified": True,
    }


def disposition_block() -> dict:
    return {
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
    }


def boundary_block() -> dict:
    return {
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
    }


def scope_block() -> dict:
    return {
        "source_present": False,
        "runtime_present": False,
        "runtime_executed": False,
        "codec_runtime_executed": False,
        "lace_model_asset_present": False,
        "real_corpus": False,
        "real_traffic": False,
        "audio_read": False,
        "decoding_performed": False,
        "concealment_or_validity_result": False,
        "quality_scored": False,
        "listening": False,
        "device_timing": False,
        "peak_bound_measured": False,
        "benchmark": False,
        "release_claim": False,
        "network_used": False,
        "download_attempted": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "preserved": True,
        "sdk_callback_invoked": False,
    }


def exact_scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "single_component": COMPONENT_ID,
        "provider_work": False,
        "runtime_work": False,
        "release_work": False,
        "write_scope": WRITE_SCOPE,
    }


def profile_source_block() -> dict:
    return {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "row": "Restoration",
        "phrases": list(PROFILE_PHRASES),
    }


def admission_contract_block() -> dict:
    return {
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "manifest_schema_id": MANIFEST_SCHEMA_ID,
        "manifest_fields": list(MANIFEST_FIELDS),
        "decoder_option_fields": list(DECODER_OPTION_FIELDS),
        "traffic_fields": list(TRAFFIC_FIELDS),
        "clean_reference_fields": list(CLEAN_REFERENCE_FIELDS),
        "stratum_fields": list(STRATUM_FIELDS),
        "packet_fields": list(PACKET_FIELDS),
        "packet_statuses": list(PACKET_STATUSES),
        "degradations": list(DEGRADATIONS),
        "alignments": list(ALIGNMENTS),
        "opus_sample_rates_hz": list(OPUS_SAMPLE_RATES),
        "packet_duration_us_bounds": [MIN_PACKET_US, MAX_PACKET_US],
        "packet_duration_us_multiple": 250,
        "bitrate_bps_bounds": [MIN_BITRATE_BPS, MAX_BITRATE_BPS],
        "max_packets": MAX_PACKETS,
        "max_bandwidth_hz": MAX_BANDWIDTH_HZ,
        "max_burst_frames": MAX_BURST_FRAMES,
        "sdk_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
        },
        "empty_payload_sha256": EMPTY_SHA256,
        "audio_read": False,
        "runtime_invoked": False,
        "decoding_performed": False,
        "replay_performed": False,
    }


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "profile": PROFILE,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "status": "incomplete",
        "decision": "DEFER",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_scope": exact_scope_block(),
        "qualification": qualification_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_row_fields": list(BOARD_ROW_FIELDS),
        "board_row_projection": dict(BOARD_ROW_PROJECTION),
        "board_row_sha256": board_row_digest(BOARD_ROW_PROJECTION),
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "absence_policy": {
            "fixed_probe_list_only": True,
            "recursive_workspace_walk": False,
            "download_attempted": False,
            "any_present_probe_blocks_shipping": True,
        },
        "absence_probes": list(ABSENCE_PROBES),
        "required_artifacts": _artifact_rows(),
        "exact_blockers": _blocker_rows(),
        "release_gates": _gate_rows(),
        "admission_contract": admission_contract_block(),
        "restoration_profile_requirements": [dict(row)
                                             for row in RESTORATION_PROFILE_ROWS],
        "profile_source": profile_source_block(),
        "non_claims": list(NON_CLAIMS),
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
    return {
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
        "decision": "DEFER",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_scope": exact_scope_block(),
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
            "conclusion": (
                "No Opus 1.5 source, libopus runtime, OSCE/LACE model asset, "
                "decoder option, genuine low-bitrate traffic, clean baseline "
                "or vendor result exists at any fixed probe location."),
        },
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "restoration_profile": {
            "profile": PROFILE,
            "rows": [dict(row) for row in RESTORATION_PROFILE_ROWS],
            "corruption_frozen": False,
            "metadata_frozen": False,
            "clean_or_packet_baseline_frozen": False,
            "degradation_strata_present": False,
            "erasure_burst_strata_present": False,
            "bandwidth_strata_present": False,
            "discrete_concealment_validity_result": False,
            "decoded_interval_result": False,
            "task_specific_quality_result": False,
            "output_peak_bounds": False,
            "timing_bounds": False,
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
                "audio_read": False,
                "decoding_performed": False,
            },
        },
        "qualification": qualification_block(),
        "prohibited_claims": list(NON_CLAIMS),
        "gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "linked_row_identity": linked_row_identity(),
        "profile_source": profile_source_block(),
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
            "tests": ("PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v "
                      "test_reference.py"),
            "report": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
        },
    }


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
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal_only")
    if len(contract.get("release_gates", [])) != 8:
        raise ValueError("contract_gate_count")
    if any(gate.get("status") != "blocked"
           for gate in contract["release_gates"]):
        raise ValueError("contract_gate_not_blocked")
    if contract.get("board_row_projection") != BOARD_ROW_PROJECTION:
        raise ValueError("contract_board_row_projection")
    if contract.get("board_row_sha256") != board_row_digest(
            BOARD_ROW_PROJECTION):
        raise ValueError("contract_board_row_digest")
    if contract.get("linked_rows") != [dict(row) for row in LINKED_ROWS]:
        raise ValueError("contract_linked_rows")
    for key, value in (("source_pins", SOURCE_PINS),
                       ("boundary_pins", BOUNDARY_PINS)):
        if contract.get(key) != value:
            raise ValueError("contract_pin_table:" + key)
