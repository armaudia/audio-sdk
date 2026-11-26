# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, standard-library-only evidence for SDK-IRCAM-SUPERVP.

This module never loads a vendor engine, imports a SuperVP SDK, reads audio,
runs time-scale modification, scores quality, performs listening, measures a
device or produces a release claim. The exact IRCAM SuperVP source, build,
runtime, licence and commercial terms are absent. The module pins stable
read-only inputs, proves fixed absence probes, exercises a fail-closed
caller-supplied-asset admission schema and a synthetic rate-accounting
control, and emits canonical JSON.

Nothing in this package qualifies the candidate. The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT",
                                  str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/ircam-supervp/"

TASK = "SDK-IRCAM-SUPERVP"
TITLE = "IRCAM SuperVP"
COMPONENT = "ircam-supervp"
COMPONENT_ID = "ircam-supervp"
REPOSITORY = "audio-sdk"
MODE = "external-adapter"
PROFILE = "rate"
PROFILE_KEY = "Rate"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_external_adapter_exposure"
QUALIFICATION_STATUS = "not_qualified"
FORMAT = "sdk-task-evidence/0.1"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/ircam-supervp-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/ircam-supervp-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/ircam-supervp-report/0.1"
BASE_COMMIT = "f006454da9a72fbfd394e2b5bd05105201a9cd29"
BRANCH = "swarm/SDK-IRCAM-SUPERVP"
CLAIM_WORKTREE = ("/Users/htsakanyan/workspace/audio/audioml/worktrees/"
                  "audio-sdk/SDK-IRCAM-SUPERVP")
REVIEWER = "reviewer-IRCAM-SUPERVP"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+){0,3}(?:[-+][A-Za-z0-9.]{1,32})?$")
PLATFORM = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")
SCOPE_TOKEN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
COMMIT_PATTERN = HEX40

# ---------------------------------------------------------------------------
# Stable, read-only pins. Source paths are relative to SOURCE_ROOT; SDK paths
# are worktree relative. Nothing here is executed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
}

BOUNDARY_PINS = {
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

# Only stable, non-mutable identity fields are projected. ``status``, ``owner``,
# ``claim``, ``review``, ``handoff``, ``blocked_reason`` and
# ``dispatch_priority`` never enter canonical bytes and never gate this package.
STABLE_TASK_FIELDS = ("acceptance", "component", "deliverable", "depends_on",
                      "evidence", "id", "mode", "repository", "title",
                      "write_scope")
MUTABLE_FIELDS_EXCLUDED = ("blocked_reason", "dispatch_priority", "handoff",
                           "owner", "review", "status")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "source/output mapping",
    "duration",
    "pitch",
    "transient audibility",
    "playback buffering",
    "1×",
    "rate changes",
    "unfamiliar speech",
    "music",
    "silence",
    "rebuffer",
    "drift",
    "final partial window",
    "source timestamps",
    "speech preservation",
)

# ---------------------------------------------------------------------------
# Upstream identity. Only the public product description is recorded. No
# public source, licensable SDK, revision, build digest, API, geometry, price
# or commercial grant was observed in this pass.
# ---------------------------------------------------------------------------

UPSTREAM_NAME = "IRCAM SuperVP"
UPSTREAM_RECORD_NAME = "IRCAM SuperVP"
UPSTREAM_VENDOR = "IRCAM"
PRODUCT_URL = "http://anasynth.ircam.fr/home/english/software/supervp"
FORUM_TS2_URL = "https://forum.ircam.fr/projects/detail/ts2/"
RECORD_PATH = "cpp-library/pipeline-validation/playback-speed-candidates.md"
RECORD_LINE = 68
TASK_KIND = "commercial_extended_phase_vocoder_time_scale_modification"
TASK_SCOPE = "time_scale_modification_actuator"
TASK_CONDITION = "vendor_supplied_tsm_engine_under_ircam_agreement"
GEOMETRY_STATUS = "unestablished"
COMMERCIAL_LICENSE_STATUS = "unresolved_requires_ircam_agreement"
PUBLIC_SOURCE_AVAILABLE = False
PUBLIC_BINARY_AVAILABLE = False
EMBEDDING_REQUIRES_SEPARATE_AGREEMENT = True
SOURCE_REVISION_PIN_AVAILABLE = False
UPSTREAM_REVISION: str | None = None
PRICE_RECORDED = False
CURRENT_SDK_AVAILABILITY_VERIFIED = False

SOURCE_REPORTED_CONTEXT = {
    "label": "source_reported_not_measured_here",
    "source": RECORD_PATH,
    "source_sha256": SOURCE_PINS[RECORD_PATH],
    "record_name": UPSTREAM_RECORD_NAME,
    "evidence_line": RECORD_LINE,
    "product_url": PRODUCT_URL,
    "forum_ts2_url": FORUM_TS2_URL,
    "recorded_finding": "**Research/premium option**",
    "recorded_licence": (
        "commercial/research access through the IRCAM Forum software suite; "
        "no public open-source licence; terms must be negotiated with IRCAM"),
    "recorded_commercial_use": "possible under an agreement; not verified",
    "recorded_limits": (
        "heavy integration, research-grade API, procurement; TS2 is "
        "distributed as an application and embedding it needs a separate "
        "agreement with IRCAM"),
    "recorded_verdict": "premium/research fallback; not a first prototype",
    "recorded_evidence_status": (
        "product description verified from the IRCAM/Anasynth page; current "
        "SDK availability and pricing not verified"),
    "notes": (
        "This package reads only the recorded research note. It does not "
        "contact IRCAM, download a trial, read a price list, accept terms or "
        "treat public product documentation as a redistribution grant."),
}

# ---------------------------------------------------------------------------
# Fixed absence probes. No recursive walk and no download. Every probe must
# stay absent.
# ---------------------------------------------------------------------------

SOURCE_PROBE_PATHS = (
    "vendor/ircam-supervp",
    "vendor/ircam",
    "vendor/supervp",
    "third_party/supervp",
    "deps/supervp",
    "data/checkouts/supervp",
    "data/checkouts/ircam-supervp",
    "research/ircam-supervp",
)
RUNTIME_PROBE_PATHS = (
    "data/vendor/ircam-supervp",
    "data/models/ircam-supervp",
    "data/runtime/ircam-supervp",
    "data/envs/ircam-supervp",
    "data/envs/ircam-supervp/requirements.lock",
)
RIGHTS_PROBE_PATHS = (
    "data/rights/ircam-supervp-rights.json",
    "data/rights/ircam-supervp-commercial-terms.pdf",
)
COHORT_PROBE_PATHS = (
    "data/runs/ircam-supervp-rate-cohort/manifest.json",
    "data/runs/ircam-supervp-parity/manifest.json",
)
ABSENCE_PROBE_PATHS = (SOURCE_PROBE_PATHS + RUNTIME_PROBE_PATHS
                       + RIGHTS_PROBE_PATHS + COHORT_PROBE_PATHS)

# ---------------------------------------------------------------------------
# Canonical JSON and strict parsing.
# ---------------------------------------------------------------------------


class InvalidInput(ValueError):
    """Fail-closed rejection for malformed or unsupported input."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    payload = report if report is not None else build_report()
    text = canonical_text(payload) + "\n"
    return text, sha256_bytes(text.encode("ascii"))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidInput("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise InvalidInput("non_finite_json:" + token)


def loads_strict(payload: str) -> dict:
    value = json.loads(payload, object_pairs_hook=_reject_duplicates,
                       parse_constant=_reject_constant)
    if not isinstance(value, dict):
        raise InvalidInput("expected_json_object")
    return value


def read_strict_json(path: Path) -> dict:
    return loads_strict(path.read_text(encoding="utf-8"))


def assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise InvalidInput("float_value_not_permitted")
    if isinstance(value, dict):
        for item in value.values():
            assert_no_float(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_float(item)


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


# ---------------------------------------------------------------------------
# Board identity and profile provenance. The mutable full TASKS.json is never
# hashed; only the linked-row stable identity enters canonical bytes.
# ---------------------------------------------------------------------------


def _board_tasks(path: Path | None = None) -> list[dict]:
    target = path if path is not None else SOURCE_ROOT / BOARD_TASK_ROW
    if not target.is_file():
        raise InvalidInput("task_board_unavailable")
    document = read_strict_json(target)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise InvalidInput("task_board_tasks_missing")
    return [row for row in tasks if isinstance(row, dict)]


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    rows = tuple(row for row in _board_tasks(path) if row.get("id") == TASK)
    if len(rows) != 1:
        raise InvalidInput("expected_exactly_one_linked_task_row")
    return rows


def board_row_projection(path: Path | None = None) -> dict:
    row = linked_rows(path)[0]
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK or stable["component"] != COMPONENT:
        raise InvalidInput("linked_task_row_identity_mismatch")
    if stable["repository"] != REPOSITORY or stable["mode"] != MODE:
        raise InvalidInput("linked_task_row_repository_or_mode_mismatch")
    claim = row.get("claim")
    if not isinstance(claim, dict):
        raise InvalidInput("linked_task_row_claim_missing")
    expected = {
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
    }
    for key, value in expected.items():
        if claim.get(key) != value:
            raise InvalidInput("linked_task_row_claim_mismatch:" + key)
    return {
        "source": BOARD_TASK_ROW,
        "stable_fields": stable,
        "stable_sha256": sha256_bytes(canonical_bytes(stable)),
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_FIELDS_EXCLUDED),
        "claim": expected,
    }


def task_row_identity() -> dict:
    projection = board_row_projection()
    projection["stable_fields"] = dict(projection["stable_fields"])
    projection["claim"] = dict(projection["claim"])
    return projection


def linked_row_identity() -> dict:
    identity = task_row_identity()
    return {
        "source": identity["source"],
        "stable_sha256": identity["stable_sha256"],
        "whole_file_hashed": False,
        "mutable_fields_never_gate": list(MUTABLE_FIELDS_EXCLUDED),
    }


def profile_source() -> dict:
    path = SOURCE_ROOT / PROFILE_SOURCE_REL
    if not path.is_file():
        raise InvalidInput("profile_source_missing")
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| Rate |")]
    if len(rows) != 1:
        raise InvalidInput("rate_profile_row_count")
    row = rows[0]
    for phrase in PROFILE_PHRASES:
        if phrase not in row:
            raise InvalidInput("rate_profile_phrase_missing:" + phrase)
    return {
        "profile": PROFILE_KEY,
        "key": PROFILE,
        "row": row,
        "source": PROFILE_SOURCE_REL,
        "source_sha256": SOURCE_PINS[PROFILE_SOURCE_REL],
    }


# ---------------------------------------------------------------------------
# Fixed absence and asset audit.
# ---------------------------------------------------------------------------


def _workspace_rows(paths: Iterable[str], kind: str) -> list[dict]:
    rows: list[dict] = []
    for relative in paths:
        present = ((SOURCE_ROOT / relative).exists()
                   or (WORKTREE / relative).exists())
        if present:
            raise InvalidInput("artifact_present_reopen_required:" + relative)
        rows.append({
            "path": relative,
            "kind": kind,
            "present": False,
            "searched_workspace": True,
            "searched_sdk_worktree": True,
        })
    return rows


def absence_probes() -> list[dict]:
    rows: list[dict] = []
    rows.extend(_workspace_rows(SOURCE_PROBE_PATHS, "source"))
    rows.extend(_workspace_rows(RUNTIME_PROBE_PATHS, "runtime"))
    rows.extend(_workspace_rows(RIGHTS_PROBE_PATHS, "rights"))
    rows.extend(_workspace_rows(COHORT_PROBE_PATHS, "cohort"))
    return rows


def absence_summary(rows: list[dict]) -> dict:
    return {
        "probe_count": len(rows),
        "present_count": sum(1 for row in rows
                             if row.get("present") is not False),
        "all_probes_absent": all(row.get("present") is False for row in rows),
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "home_cache_scanned": False,
        "network_used": False,
        "download_attempted": False,
    }


def source_probe() -> dict:
    return {
        "status": "blocked_licensed_vendor_sdk_absent",
        "present": False,
        "executed": False,
        "revision_verified": False,
        "license_verified": False,
        "public_source_available": PUBLIC_SOURCE_AVAILABLE,
        "public_binary_available": PUBLIC_BINARY_AVAILABLE,
        "product_url": PRODUCT_URL,
        "forum_ts2_url": FORUM_TS2_URL,
        "candidates": _workspace_rows(SOURCE_PROBE_PATHS, "source"),
    }


def runtime_probe() -> dict:
    return {
        "status": "blocked_licensed_runtime_and_platform_absent",
        "pinned_runtime_present": False,
        "pinned_runtime_complete": False,
        "pinned_runtime_version_verified": False,
        "runtime_lock_present": False,
        "imported_or_executed": False,
        "required_runtime": (
            "licensed IRCAM SuperVP SDK or host runtime at a pinned version "
            "and build with a recorded platform, per-file SHA-256, reviewed "
            "terms and an offline load path"),
        "candidates": _workspace_rows(RUNTIME_PROBE_PATHS, "runtime"),
    }


def rights_probe() -> dict:
    return {
        "status": "blocked_commercial_terms_unresolved",
        "commercial_license_verified": False,
        "redistribution_grant": False,
        "output_use_grant": False,
        "price_recorded": PRICE_RECORDED,
        "current_sdk_availability_verified":
            CURRENT_SDK_AVAILABILITY_VERIFIED,
        "embedding_requires_separate_agreement":
            EMBEDDING_REQUIRES_SEPARATE_AGREEMENT,
        "candidates": _workspace_rows(RIGHTS_PROBE_PATHS, "rights"),
    }


def cohort_probe() -> dict:
    return {
        "status": "blocked_rate_cohort_and_parity_absent",
        "rate_cohort_present": False,
        "parity_vector_present": False,
        "frozen_references": False,
        "candidates": _workspace_rows(COHORT_PROBE_PATHS, "cohort"),
    }


# ---------------------------------------------------------------------------
# Caller-supplied-asset admission contract. Validation hashes caller files but
# never imports or executes the vendor runtime.
# ---------------------------------------------------------------------------

CALLER_ASSET_FIELDS = (
    "channels",
    "commercial_terms_acknowledged",
    "license_record_path",
    "license_record_sha256",
    "max_rate_bp",
    "min_rate_bp",
    "parity_vector_path",
    "parity_vector_sha256",
    "platform",
    "rate_cohort_manifest_path",
    "rate_cohort_manifest_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "sample_rate_input_hz",
    "sample_rate_output_hz",
    "scope",
    "vendor_sdk_manifest_path",
    "vendor_sdk_manifest_sha256",
    "vendor_sdk_path",
    "vendor_version",
    "variant",
)
CALLER_FILE_PAIRS = (
    ("license_record_path", "license_record_sha256"),
    ("parity_vector_path", "parity_vector_sha256"),
    ("rate_cohort_manifest_path", "rate_cohort_manifest_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("vendor_sdk_manifest_path", "vendor_sdk_manifest_sha256"),
)
CALLER_DIR_FIELDS = ("runtime_path", "vendor_sdk_path")
CALLER_SCOPE = TASK_SCOPE
CALLER_VARIANT = "offline_whole_clip"
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000
MIN_CHANNELS = 1
MAX_CHANNELS = 8
MIN_RATE_BP = 2500
MAX_RATE_BP = 40000
MAX_MANIFEST_BYTES = 8 * 1024 ** 3

CALLER_ASSET_CONTRACT = {
    "contract_id": f"audio-sdk/{COMPONENT}/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_vendor_version_platform_geometry_"
        "rate_range_scope_and_offline_variant_only; do_not_import_or_execute_"
        "in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_scope": CALLER_SCOPE,
    "required_source_revision": UPSTREAM_REVISION,
    "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
    "required_geometry": {
        "channels": None,
        "sample_rate_input_hz": None,
        "sample_rate_output_hz": None,
        "status": GEOMETRY_STATUS,
    },
    "required_commercial_terms_acknowledged": True,
    "required_rate_basis_points": {
        "min": MIN_RATE_BP,
        "max": MAX_RATE_BP,
        "unity": 10000,
        "note": (
            "Rates are integer basis points of playback speed: 10000 is 1x, "
            "12500 is 1.25x faster and 7500 is 0.75x slower. No float is "
            "admitted so the contract stays byte-deterministic."),
    },
    "notes": (
        "A caller may validate a manifest only when the licensed vendor SDK, "
        "runtime, commercial terms, rights record, locked runtime, rate "
        "cohort, parity vector and reviewed platform are all present at "
        "absolute paths and match their declared SHA-256. The package never "
        "imports, executes or redistributes the vendor engine. No upstream "
        "revision is pinned because no public source or licensable revision "
        "is recorded. Streaming and rate automation remain unverified."),
}

CALLER_ASSET_REQUIREMENTS = (
    {
        "id": "licensed_vendor_sdk_or_runtime",
        "required": True,
        "status": "absent",
        "sha256": None,
        "note": "No SuperVP SDK, binary, host plug-in or trial is present.",
    },
    {
        "id": "vendor_version_and_build_pin",
        "required": True,
        "status": "absent",
        "revision": None,
        "note": (
            "No vendor version, build number, per-file digest or platform "
            "build is recorded beyond a public product description."),
    },
    {
        "id": "commercial_license_and_terms",
        "required": True,
        "status": "absent",
        "note": (
            "No IRCAM agreement, forum entitlement, commercial price, "
            "redistribution grant, output-use right or indemnity is present "
            "or recorded."),
    },
    {
        "id": "api_reference_and_geometry",
        "required": True,
        "status": "absent",
        "note": (
            "No licensed API reference establishes rate semantics, sample "
            "rate, channels, hop, latency, flush or reset behaviour."),
    },
    {
        "id": "runtime_and_platform_lock",
        "required": True,
        "status": "absent",
        "sha256": None,
        "note": "No isolated runtime, platform lock or offline load path.",
    },
    {
        "id": "rate_cohort_and_references",
        "required": True,
        "status": "absent",
        "note": (
            "No rights-cleared frozen rate cohort covers 1x, rate changes, "
            "unfamiliar speech, music, silence, rebuffer and the final "
            "partial window."),
    },
    {
        "id": "parity_vector",
        "required": True,
        "status": "absent",
        "sha256": None,
        "note": "No approved exact-runtime parity vector exists.",
    },
    {
        "id": "redistribution_and_output_rights",
        "required": True,
        "status": "absent",
        "note": (
            "No corpus, reference, output-use, redistribution or patent "
            "terms are cleared."),
    },
)

# ---------------------------------------------------------------------------
# Rate acceptance profile. Every item remains blocked or not measured.
# ---------------------------------------------------------------------------

RATE_REQUIREMENTS = (
    ("source_output_mapping",
     "Measure the exact source-to-output mapping without drift.",
     "blocked"),
    ("duration",
     "Measure output duration and rate accuracy for 1x and changed rates.",
     "blocked"),
    ("pitch",
     "Measure pitch preservation separately from duration.",
     "not_measured"),
    ("transient_audibility",
     "Measure transient audibility and artifacts at rate changes.",
     "not_measured"),
    ("playback_buffering",
     "Measure playback buffering, first output and availability for the "
     "exact runtime.",
     "blocked"),
    ("unity_and_rate_changes",
     "Include 1x, rate changes, unfamiliar speech, music and silence.",
     "blocked"),
    ("rebuffer_drift_final_partial_window",
     "Include rebuffer, long-run drift and the final partial window.",
     "blocked"),
    ("source_timestamp_policy",
     "Keep pause or filler decisions tied to source timestamps.",
     "blocked"),
    ("speech_preservation",
     "Measure speech preservation alongside rate and timing.",
     "not_measured"),
)

# ---------------------------------------------------------------------------
# Synthetic rate accounting control. This is structural accounting at the
# public v0 geometry, not a SuperVP output and not a TSM quality result.
# ---------------------------------------------------------------------------

CONTROL_SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
CONTROL_SOURCE_SAMPLES = CONTROL_SAMPLE_RATE_HZ * 3
CONTROL_CHUNK_SAMPLES = SDK_FRAME_SAMPLES
CONTROL_RATES_BP = (7500, 10000, 12500, 15000)
PCM_SAMPLE_CAP = 10_000_000
CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_rate_accounting_control_not_tsm_output")


def _triangle(index: int, period: int, scale: float) -> float:
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_source_pcm() -> list[float]:
    samples: list[float] = []
    state = 0x1C4A5EED
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 37, 0.30) + 0.01 * noise)
    return samples


def validate_pcm(signal: Any, sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ,
                 channels: int = CHANNELS) -> list[float]:
    if sample_rate_hz != CONTROL_SAMPLE_RATE_HZ:
        raise InvalidInput("unsupported_control_sample_rate")
    if channels != CHANNELS:
        raise InvalidInput("control_is_mono_only")
    if not isinstance(signal, (list, tuple)):
        raise InvalidInput("signal_must_be_a_sample_sequence")
    if not signal:
        raise InvalidInput("signal_must_be_nonempty")
    if len(signal) > PCM_SAMPLE_CAP:
        raise InvalidInput("signal_exceeds_evidence_cap")
    checked: list[float] = []
    for index, sample in enumerate(signal):
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise InvalidInput(f"sample_{index}_is_not_numeric")
        value = float(sample)
        if value != value or value in (float("inf"), float("-inf")):
            raise InvalidInput(f"sample_{index}_is_not_finite")
        if value < -1.0 or value > 1.0:
            raise InvalidInput(f"sample_{index}_is_outside_minus_one_one")
        checked.append(value)
    return checked


def pcm_summary(signal: Iterable[float], sample_rate_hz: int) -> dict:
    values = validate_pcm(list(signal), sample_rate_hz)
    peak = max(abs(value) for value in values)
    return {
        "samples": len(values),
        "sample_rate_hz": sample_rate_hz,
        "channels": CHANNELS,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs_scaled_1e6": int(round(peak * 1_000_000)),
        "peak_scale": 1_000_000,
        "nonfinite_samples": 0,
        "sha256": sha256_bytes(canonical_bytes(values)),
    }


def output_samples_for_rate(source_samples: int, rate_bp: int) -> int:
    if (not isinstance(source_samples, int)
            or isinstance(source_samples, bool) or source_samples <= 0):
        raise InvalidInput("source_samples_must_be_a_positive_integer")
    if (not isinstance(rate_bp, int) or isinstance(rate_bp, bool)
            or rate_bp < MIN_RATE_BP or rate_bp > MAX_RATE_BP):
        raise InvalidInput("rate_bp_outside_admitted_range")
    return (source_samples * 10000) // rate_bp


def rate_mapping(source_samples: int, rate_bp: int) -> dict:
    output = output_samples_for_rate(source_samples, rate_bp)
    source_duration = Fraction(source_samples, CONTROL_SAMPLE_RATE_HZ)
    output_duration = Fraction(output, CONTROL_SAMPLE_RATE_HZ)
    ratio = output_duration / source_duration
    return {
        "rate_bp": rate_bp,
        "rate_text": fraction_text(Fraction(rate_bp, 10000)),
        "source_samples": source_samples,
        "output_samples": output,
        "source_duration_s": fraction_text(source_duration),
        "output_duration_s": fraction_text(output_duration),
        "duration_ratio": fraction_text(ratio),
        "rounding_policy": "floor",
        "interpretation": "output_duration_divided_by_source_duration",
    }


def chunked_accounting(source_samples: int, rate_bp: int,
                       chunk_samples: int) -> dict:
    if chunk_samples <= 0:
        raise InvalidInput("chunk_samples_must_be_positive")
    emitted = 0
    accumulated = 0
    chunks = 0
    while accumulated < source_samples:
        take = min(chunk_samples, source_samples - accumulated)
        accumulated += take
        chunks += 1
        target = (accumulated * 10000) // rate_bp
        emitted = target
    whole = output_samples_for_rate(source_samples, rate_bp)
    return {
        "rate_bp": rate_bp,
        "chunk_samples": chunk_samples,
        "chunks": chunks,
        "chunked_output_samples": emitted,
        "whole_clip_output_samples": whole,
        "drift_samples": emitted - whole,
        "policy": "fractional_source_accumulator_with_floor",
    }


def final_partial_window_accounting(rate_bp: int) -> dict:
    source_samples = CONTROL_CHUNK_SAMPLES * 3 + 37
    output = output_samples_for_rate(source_samples, rate_bp)
    return {
        "rate_bp": rate_bp,
        "source_samples": source_samples,
        "partial_tail_samples": 37,
        "output_samples": output,
        "final_window_flushed": True,
        "tail_policy": "whole_final_partial_window_accounted_once",
        "measured": False,
    }


def run_adverse_controls() -> list[dict]:
    good_source = synthetic_source_pcm()
    good_manifest = _shape_only_manifest()
    existing = _existing_file_manifest()

    def case(case_id: str, action) -> dict:
        try:
            action()
        except InvalidInput as error:
            return {"case": case_id, "result": "rejected",
                    "reason": str(error)}
        except Exception as error:  # noqa: BLE001 - recorded, never swallowed
            return {"case": case_id, "result": "unexpected_error",
                    "reason": type(error).__name__ + ": " + str(error)}
        return {"case": case_id, "result": "accepted", "reason": ""}

    def wrong(key: str, value: Any):
        manifest = dict(good_manifest)
        manifest[key] = value
        return lambda: validate_caller_manifest(manifest)

    def drop(key: str):
        manifest = {key2: value for key2, value in good_manifest.items()
                    if key2 != key}
        return lambda: validate_caller_manifest(manifest)

    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_source, 8000)),
        ("pcm_nan", lambda: validate_pcm([0.0, float("nan")])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, float("inf")])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, float("-inf")])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("vendor_sdk_manifest_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "vendor_sdk_path", "vendor/supervp")),
        ("manifest_bad_sha", wrong("license_record_sha256", "ABC")),
        ("manifest_wrong_scope", wrong("scope", "voice_conversion")),
        ("manifest_wrong_variant", wrong("variant", "caller_clocked_streaming")),
        ("manifest_channels_zero", wrong("channels", 0)),
        ("manifest_channels_bool", wrong("channels", True)),
        ("manifest_rate_below_range", wrong("sample_rate_output_hz", 4000)),
        ("manifest_rate_above_range", wrong(
            "sample_rate_output_hz", 384000)),
        ("manifest_rate_bool", wrong("sample_rate_output_hz", True)),
        ("manifest_min_above_max", lambda: validate_caller_manifest(
            dict(good_manifest, min_rate_bp=15000, max_rate_bp=7500))),
        ("manifest_rate_bp_out_of_range", wrong("max_rate_bp", 100000)),
        ("manifest_empty_version", wrong("vendor_version", "")),
        ("manifest_bad_platform", wrong("platform", "Mac OS X")),
        ("manifest_terms_not_acknowledged", wrong(
            "commercial_terms_acknowledged", False)),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, vendor_sdk_manifest_path=(
                "/nonexistent/ircam-supervp-fixtures/manifest.json")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, runtime_path=(
                "/nonexistent/ircam-supervp-fixtures/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, license_record_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise InvalidInput("adverse_case_count_mismatch")
    good = pcm_summary(good_source, CONTROL_SAMPLE_RATE_HZ)
    if good["samples"] != CONTROL_SOURCE_SAMPLES:
        raise InvalidInput("synthetic_source_control_mismatch")
    return results


ADVERSE_CASE_IDS = (
    "pcm_empty",
    "pcm_not_sequence",
    "pcm_none",
    "pcm_wrong_rate",
    "pcm_nan",
    "pcm_pos_inf",
    "pcm_neg_inf",
    "pcm_out_of_range",
    "pcm_bool",
    "pcm_string",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_wrong_scope",
    "manifest_wrong_variant",
    "manifest_channels_zero",
    "manifest_channels_bool",
    "manifest_rate_below_range",
    "manifest_rate_above_range",
    "manifest_rate_bool",
    "manifest_min_above_max",
    "manifest_rate_bp_out_of_range",
    "manifest_empty_version",
    "manifest_bad_platform",
    "manifest_terms_not_acknowledged",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
)


def _shape_only_manifest() -> dict:
    root = "/nonexistent/ircam-supervp-evidence-fixture"
    digest = "0" * 64
    return {
        "channels": CHANNELS,
        "commercial_terms_acknowledged": True,
        "license_record_path": root + "/license.json",
        "license_record_sha256": digest,
        "max_rate_bp": 15000,
        "min_rate_bp": 7500,
        "parity_vector_path": root + "/parity.json",
        "parity_vector_sha256": digest,
        "platform": "macos_arm64",
        "rate_cohort_manifest_path": root + "/cohort.json",
        "rate_cohort_manifest_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "runtime_lock_path": root + "/runtime.lock",
        "runtime_lock_sha256": digest,
        "runtime_path": root + "/runtime",
        "sample_rate_input_hz": CONTROL_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": CONTROL_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "vendor_sdk_manifest_path": root + "/sdk-manifest.json",
        "vendor_sdk_manifest_sha256": digest,
        "vendor_sdk_path": root + "/sdk",
        "vendor_version": "0.0.0",
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> dict:
    assignments = {
        "license_record_path": HERE / "LICENSES.md",
        "parity_vector_path": HERE / "README.md",
        "rate_cohort_manifest_path": HERE / "contract.json.license",
        "rights_record_path": HERE / "LICENSES.md",
        "runtime_lock_path": HERE / "SOURCES.sha256.license",
        "vendor_sdk_manifest_path": HERE / "reference.py",
    }
    manifest: dict[str, Any] = {
        "channels": CHANNELS,
        "commercial_terms_acknowledged": True,
        "max_rate_bp": 15000,
        "min_rate_bp": 7500,
        "platform": "macos_arm64",
        "runtime_path": str(WORKTREE),
        "sample_rate_input_hz": CONTROL_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": CONTROL_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "vendor_sdk_path": str(HERE),
        "vendor_version": "0.0.0",
        "variant": CALLER_VARIANT,
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = sha256_file(path)
    return manifest


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_MANIFEST_BYTES:
                raise InvalidInput("asset_exceeds_evidence_cap")
            digest.update(chunk)
    return digest.hexdigest()


def _bounded_int(manifest: dict, field: str, low: int, high: int) -> int:
    value = manifest[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidInput("manifest_" + field + "_must_be_an_integer")
    if value < low or value > high:
        raise InvalidInput("manifest_" + field + "_outside_admitted_range")
    return value


def _path_field(manifest: dict, field: str) -> Path:
    value = manifest[field]
    if not isinstance(value, str) or not value:
        raise InvalidInput("manifest_" + field + "_must_be_a_path_string")
    path = Path(value)
    if not path.is_absolute():
        raise InvalidInput("manifest_" + field + "_must_be_absolute")
    return path


def validate_caller_manifest(manifest: Any) -> dict:
    if not isinstance(manifest, dict):
        raise InvalidInput("manifest_must_be_an_object")
    expected = set(CALLER_ASSET_FIELDS)
    present = set(manifest)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing:
        raise InvalidInput("manifest_missing_fields:" + ",".join(missing))
    if extra:
        raise InvalidInput("manifest_has_unknown_fields:" + ",".join(extra))
    for _, sha_field in CALLER_FILE_PAIRS:
        value = manifest[sha_field]
        if not isinstance(value, str) or not HEX64.fullmatch(value):
            raise InvalidInput(
                "manifest_" + sha_field + "_is_not_a_lowercase_sha256")
    for path_field, _ in CALLER_FILE_PAIRS:
        _path_field(manifest, path_field)
    for field in CALLER_DIR_FIELDS:
        _path_field(manifest, field)
    version = manifest["vendor_version"]
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise InvalidInput("manifest_vendor_version_is_invalid")
    platform = manifest["platform"]
    if not isinstance(platform, str) or not PLATFORM.fullmatch(platform):
        raise InvalidInput("manifest_platform_is_invalid")
    scope = manifest["scope"]
    if not isinstance(scope, str) or not SCOPE_TOKEN.fullmatch(scope):
        raise InvalidInput("manifest_scope_is_invalid")
    if scope != CALLER_SCOPE:
        raise InvalidInput("manifest_scope_must_be_" + CALLER_SCOPE)
    if manifest["variant"] != CALLER_VARIANT:
        raise InvalidInput("manifest_variant_must_be_" + CALLER_VARIANT)
    if manifest["commercial_terms_acknowledged"] is not True:
        raise InvalidInput("manifest_commercial_terms_not_acknowledged")
    channels = _bounded_int(manifest, "channels", MIN_CHANNELS, MAX_CHANNELS)
    sample_in = _bounded_int(manifest, "sample_rate_input_hz",
                             MIN_SAMPLE_RATE_HZ, MAX_SAMPLE_RATE_HZ)
    sample_out = _bounded_int(manifest, "sample_rate_output_hz",
                              MIN_SAMPLE_RATE_HZ, MAX_SAMPLE_RATE_HZ)
    min_rate = _bounded_int(manifest, "min_rate_bp", MIN_RATE_BP, MAX_RATE_BP)
    max_rate = _bounded_int(manifest, "max_rate_bp", MIN_RATE_BP, MAX_RATE_BP)
    if min_rate > max_rate:
        raise InvalidInput("manifest_min_rate_exceeds_max_rate")
    for field in CALLER_DIR_FIELDS:
        if not Path(manifest[field]).is_dir():
            raise InvalidInput("manifest_" + field + "_directory_is_missing")
    total_bytes = 0
    for path_field, sha_field in CALLER_FILE_PAIRS:
        path = Path(manifest[path_field])
        if not path.is_file():
            raise InvalidInput("manifest_" + path_field + "_file_is_missing")
        actual = _hash_file(path)
        if actual != manifest[sha_field]:
            raise InvalidInput("manifest_" + path_field + "_sha256_mismatch")
        total_bytes += path.stat().st_size
    return {
        "accepted": True,
        "vendor_version": version,
        "platform": platform,
        "variant": CALLER_VARIANT,
        "scope": CALLER_SCOPE,
        "commercial_terms_acknowledged": True,
        "sample_rate_input_hz": sample_in,
        "sample_rate_output_hz": sample_out,
        "channels": channels,
        "min_rate_bp": min_rate,
        "max_rate_bp": max_rate,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "engine_executed": False,
    }


def build_control() -> dict:
    source = synthetic_source_pcm()
    source_summary = pcm_summary(source, CONTROL_SAMPLE_RATE_HZ)
    mappings = [rate_mapping(len(source), rate_bp)
                for rate_bp in CONTROL_RATES_BP]
    unity = rate_mapping(len(source), 10000)
    chunked = [chunked_accounting(len(source), rate_bp,
                                  CONTROL_CHUNK_SAMPLES)
               for rate_bp in CONTROL_RATES_BP]
    partial = [final_partial_window_accounting(rate_bp)
               for rate_bp in CONTROL_RATES_BP]
    adverse = run_adverse_controls()
    positive = validate_caller_manifest(_existing_file_manifest())
    return {
        "engine_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_sample_format": "f32",
            "control_mode": "offline_whole_clip",
            "control_incremental_streaming": False,
            "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
            "supervp_geometry_status": GEOMETRY_STATUS,
            "supervp_geometry_asserted": False,
            "task_scope": TASK_SCOPE,
            "task_kind": TASK_KIND,
        },
        "source_pcm": source_summary,
        "rate_mappings": mappings,
        "unity_mapping": unity,
        "chunked_accounting": chunked,
        "final_partial_window": partial,
        "accepted_control": {
            "id": "synthetic_structure_only_manifest",
            "accepted": positive["accepted"],
            "vendor_version": positive["vendor_version"],
            "platform": positive["platform"],
            "scope": positive["scope"],
            "variant": positive["variant"],
            "files_checked": positive["files_checked"],
            "directories_checked": positive["directories_checked"],
            "engine_executed": positive["engine_executed"],
            "qualification_effect": "none",
            "note": (
                "The manifest hashes files inside this evidence package only. "
                "It is a structural positive control, not a licensed IRCAM "
                "asset set, and it cannot qualify the candidate."),
        },
        "acceptance_outcomes": [
            {"id": "source_output_mapping", "measured": False, "value": None,
             "reason": "structural integer count only; no engine"},
            {"id": "duration", "measured": False, "value": None,
             "reason": "exact rational accounting only; no engine output"},
            {"id": "pitch", "measured": False, "value": None,
             "reason": "no vendor engine, audio or pitch analysis"},
            {"id": "transient_audibility", "measured": False, "value": None,
             "reason": "no vendor engine, audio or listening"},
            {"id": "playback_buffering", "measured": False, "value": None,
             "reason": "no runtime, device clock or queue"},
            {"id": "unity_and_rate_changes", "measured": False, "value": None,
             "reason": "structural rate table only; no streaming automation"},
            {"id": "rebuffer_drift_final_partial_window", "measured": False,
             "value": None,
             "reason": "structural accumulator only; no rebuffer or device"},
            {"id": "speech_preservation", "measured": False, "value": None,
             "reason": "no real speech, reference transcript or scorer"},
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": ["pcm_nan", "pcm_pos_inf", "pcm_neg_inf"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range", "pcm_wrong_rate",
                "manifest_channels_zero", "manifest_channels_bool",
                "manifest_rate_below_range", "manifest_rate_above_range",
                "manifest_rate_bool", "manifest_min_above_max",
                "manifest_rate_bp_out_of_range", "manifest_empty_version",
                "manifest_bad_platform", "manifest_wrong_scope",
                "manifest_wrong_variant",
                "manifest_terms_not_acknowledged",
            ],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "manifest_missing_field", "manifest_missing_asset",
                "manifest_missing_directory",
            ],
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic PCM validity and integer rate accounting at the public "
            "v0 geometry only. It is not IRCAM SuperVP output, not real TSM, "
            "not real audio, not a pitch or transient result and not a "
            "quality, timing or release claim."),
    }


# ---------------------------------------------------------------------------
# Gates, blockers and artifacts.
# ---------------------------------------------------------------------------

GATE_REQUIREMENTS = (
    ("RG-01", "exact_vendor_engine_identity",
     "The licensed IRCAM SuperVP SDK or host runtime, exact version, build "
     "number, platform and per-file SHA-256 are pinned and reviewed."),
    ("RG-02", "runtime_and_platform_admission",
     "An isolated, locked runtime with a recorded platform and offline load "
     "path is admitted."),
    ("RG-03", "commercial_license_and_redistribution_rights",
     "A signed IRCAM agreement covers commercial embedding, redistribution, "
     "output use, attribution, price and indemnity with complete notices."),
    ("RG-04", "exact_reference_parity",
     "An approved exact-runtime output matches the reference on a frozen "
     "caller-supplied rate vector for one frozen configuration."),
    ("RG-05", "rate_cohort_and_scoring",
     "A rights-cleared held-out rate cohort measures mapping, duration, "
     "pitch, transient audibility, buffering and speech preservation."),
    ("RG-06", "task_scope_and_geometry",
     "The TSM scope, rate semantics, sample rate, channels, hop, latency, "
     "reset, flush and final partial-window behaviour are established."),
    ("RG-07", "opt_in_external_adapter_intake",
     "Explicit opt-in external-adapter intake, licence review, API review and "
     "an independent public-surface decision are complete."),
    ("RG-08", "public_default_and_release",
     "Explicit default selection, resource/deadline evidence and release or "
     "public-benchmark approval are recorded; this package is off by "
     "default."),
)

EXACT_BLOCKERS = (
    ("BLK-01", "RG-01", "licensed_vendor_sdk_absent",
     "Supply the licensed IRCAM SuperVP SDK or host runtime at an exact "
     "version and build; no vendor SDK, binary, plug-in, trial or checkout is "
     "present in the workspace."),
    ("BLK-02", "RG-01", "vendor_build_identity_unpinned",
     "Publish the exact vendor version, build number, platform artifact and "
     "per-file SHA-256; the merged evidence records only a public product "
     "description and no artifact identity."),
    ("BLK-03", "RG-03", "commercial_terms_unresolved",
     "Obtain the IRCAM Forum or direct commercial agreement that grants "
     "embedding, redistribution, output use and patent/indemnity terms; no "
     "licence text, price, quote or grant is present or recorded."),
    ("BLK-04", "RG-02", "runtime_and_platform_absent",
     "Provide a locked runtime, exact platform and offline load path; no "
     "runtime environment, lock file or platform build exists."),
    ("BLK-05", "RG-06", "api_and_geometry_unverified",
     "Provide the licensed API reference that fixes rate semantics, sample "
     "rate, channels, hop, latency, reset, flush and final-partial-window "
     "behaviour; the product description does not establish geometry."),
    ("BLK-06", "RG-05", "rate_cohort_and_references_absent",
     "Freeze a rights-cleared rate cohort covering 1x, rate changes, "
     "unfamiliar speech, music, silence, rebuffer, drift and the final "
     "partial window with permitted references."),
    ("BLK-07", "RG-04", "parity_vector_absent",
     "Approve an exact-runtime parity vector on a frozen caller-supplied "
     "input and configuration; no vendor output or parity vector exists."),
    ("BLK-08", "RG-07", "integration_default_and_release_absent",
     "Complete opt-in adapter intake, resource/deadline evidence and release "
     "or public-benchmark approval; none is present and this package is off "
     "by default."),
)

REQUIRED_ARTIFACTS = (
    ("ART-01", "licensed_vendor_engine",
     "The exact licensed IRCAM SuperVP SDK or host runtime at an immutable "
     "version and build, with reviewed terms and per-file SHA-256."),
    ("ART-02", "commercial_agreement",
     "The signed commercial agreement covering embedding, redistribution, "
     "output use, attribution, price and indemnity."),
    ("ART-03", "runtime_and_platform_lock",
     "A locked runtime, offline load path and recorded platform."),
    ("ART-04", "api_and_geometry_reference",
     "The licensed API reference for rate semantics, geometry, latency, "
     "reset, flush and final partial-window behaviour."),
    ("ART-05", "rate_cohort",
     "A rights-cleared frozen rate cohort with permitted source and reference "
     "material and held-out splits."),
    ("ART-06", "parity_vector",
     "An approved exact-runtime parity vector for one frozen configuration."),
    ("ART-07", "rate_scoring",
     "Paired and unpaired rate outcomes covering mapping, duration, pitch, "
     "transient audibility, buffering, rebuffer, drift and speech "
     "preservation."),
    ("ART-08", "review_and_release",
     "Independent exact-head review, opt-in intake, default decision and "
     "release or public-benchmark approval."),
)

DISPOSITION = {
    "decision": DECISION,
    "status": "incomplete",
    "qualification_status": QUALIFICATION_STATUS,
    "proposal_only": True,
    "incomplete": True,
    "not_qualified": True,
    "missing_result_qualifies": False,
    "default_enabled": False,
    "registered": False,
    "expose_as_processor": False,
    "production_exposure": "DEFER",
    "promotion": "defer",
    "defer_before": DEFER_BEFORE,
}

SCOPE = {
    "task_local_only": True,
    "real_audio": False,
    "real_corpus": False,
    "vendor_engine_loaded": False,
    "vendor_engine_executed": False,
    "tsm_output_generated": False,
    "network_used": False,
    "download_attempted": False,
    "binary_committed": False,
    "device_timing": False,
    "listening": False,
    "public_benchmark": False,
    "release_claim": False,
}

BOUNDARY = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "public_api_abi_change": False,
    "provider_registration": False,
    "production_callback_registered": False,
    "descriptor_registry_change": False,
    "shared_build_or_ci_change": False,
    "installed_v0_behavior_change": False,
    "asset_bundled": False,
    "binary_vendored": False,
    "sdk_callback_invoked": False,
    "network_used": False,
    "descriptor_settings": {},
    "adapter_json_added": False,
    "provider_json_added": False,
}

PUBLIC_V0_GEOMETRY = {
    "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": "f32",
    "frame_samples": SDK_FRAME_SAMPLES,
    "unchanged": True,
}

NON_CLAIMS = (
    "No IRCAM SuperVP SDK, binary, host plug-in, trial or checkout is "
    "loaded, imported or executed.",
    "No vendor source, build, licence text or commercial term is downloaded, "
    "mirrored, accepted or redistributed.",
    "No network request, price lookup, trial registration or procurement "
    "action occurs.",
    "No real audio, corpus, speech, music, silence fixture or reference is "
    "consumed or produced.",
    "No time-scale modification output is generated; the control is integer "
    "rate accounting only.",
    "No pitch, transient, buffering, latency, memory, RTF or device timing is "
    "measured.",
    "No listening, public benchmark, quality score or release result is "
    "claimed.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI "
    "changed.",
    "Missing evidence never qualifies the candidate; the decision remains "
    "DEFER and the qualification remains not_qualified.",
)

RIGHTS_GAP = {
    "status": "blocked",
    "commercial_license_verified": False,
    "license_text_present": False,
    "price_or_quote_present": False,
    "redistribution_grant": False,
    "output_use_grant": False,
    "attribution_terms": None,
    "patent_or_indemnity_terms": None,
    "forum_entitlement_present": False,
    "note": (
        "The recorded research note says SuperVP is commercial/research access "
        "through the IRCAM Forum suite, that no public open-source licence "
        "exists, that terms must be negotiated with IRCAM, and that embedding "
        "TS2 needs a separate agreement. Those statements are provenance, not "
        "a grant. No agreement, quote or entitlement was obtained."),
}


# ---------------------------------------------------------------------------
# Merge-base scope helpers (used by verify.py and the regression tests).
# ---------------------------------------------------------------------------

SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base between HEAD and an available PR base ref.

    Returns None only when no base ref exists, which the verifier treats as a
    fail-closed condition rather than a silent pass.
    """
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
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]


# ---------------------------------------------------------------------------
# README digest tables. Every digest is machine-checked.
# ---------------------------------------------------------------------------

README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})


def local_manifest_paths() -> list[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name != "SOURCES.sha256")


PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  (source:[A-Za-z0-9_./-]+|"
    r"sdk:[A-Za-z0-9_./-]+|docs/task-evidence/ircam-supervp/"
    r"[A-Za-z0-9_./-]+)$")


def parse_pin_lines(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        match = PIN_LINE.fullmatch(line)
        if match is None:
            raise ValueError("malformed_pin_line:" + str(number))
        digest, path = match.groups()
        if path in seen:
            raise ValueError("duplicate_pin:" + str(number))
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def allowed_pin_keys() -> set[str]:
    return ({"source:" + name for name in SOURCE_PINS}
            | {"sdk:" + name for name in BOUNDARY_PINS}
            | {TASK_PREFIX + name for name in local_manifest_paths()})


def expected_readme_keys() -> dict[str, set[str]]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {name for name in local_manifest_paths()
                      if name not in ARTIFACT_TABLE_EXCLUDED},
    }


def _section_text(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if text.count(start) != 1:
        raise ValueError("readme_marker_count:" + section)
    start_index = text.index(start) + len(start)
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise ValueError("readme_marker_missing:" + section)
    return text[start_index:end_index]


def parse_readme_digest_tables(text: str) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for section in README_SECTIONS:
        rows: list[tuple[str, str]] = []
        for line in _section_text(text, section).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or re.fullmatch(r"[0-9]+", cells[2]) is None:
                    raise ValueError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ValueError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if not HEX64.fullmatch(digest):
                raise ValueError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({key for key, _ in rows}) != len(rows):
            raise ValueError("duplicate_readme_row:" + section)
        result[section] = rows
    return result


def verify_readme_digests(text: str) -> dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            missing = sorted(expected[section] - actual_keys)
            extra = sorted(actual_keys - expected[section])
            raise ValueError(
                f"readme_key_mismatch:{section}:missing={missing}:"
                f"extra={extra}")
        for key, digest in parsed[section]:
            if section == "source":
                relative = key[len("source:"):]
                expected_digest = SOURCE_PINS[relative]
                path = SOURCE_ROOT / relative
            elif section == "boundary":
                relative = key[len("sdk:"):]
                expected_digest = BOUNDARY_PINS[relative]
                path = WORKTREE / relative
            else:
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if not path.is_file():
                raise ValueError("readme_pin_target_missing:" + key)
            if sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = f"| `{key}` | `{sha256_file(HERE / key)}` | {size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_artifact_table() -> str:
    rows = [
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->",
        "| Path | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
    ]
    for name in local_manifest_paths():
        if name in ARTIFACT_TABLE_EXCLUDED:
            continue
        path = HERE / name
        rows.append(f"| `{name}` | `{sha256_file(path)}` | "
                    f"{path.stat().st_size} |")
    rows.append("<!-- DIGEST_TABLE_ARTIFACTS_END -->")
    return "\n".join(rows)


def update_readme_artifact_table(text: str) -> str:
    block = render_artifact_table()
    start_marker, end_marker = README_MARKERS["artifacts"]
    start = text.index(start_marker)
    end = text.index(end_marker, start) + len(end_marker)
    return text[:start] + block + text[end:]


# ---------------------------------------------------------------------------
# Report and contract.
# ---------------------------------------------------------------------------


def _rate_profile_block() -> dict:
    items = [
        {
            "id": item,
            "requirement": requirement,
            "package_status": status,
            "satisfied_for_qualification": False,
            "qualification_effect": "none",
        }
        for item, requirement, status in RATE_REQUIREMENTS
    ]
    return {
        "name": PROFILE,
        "key": PROFILE_KEY,
        "source": PROFILE_SOURCE_REL,
        "source_sha256": SOURCE_PINS[PROFILE_SOURCE_REL],
        "required_items": items,
        "satisfied_for_qualification": [],
        "unsatisfied_for_qualification": [item["id"] for item in items],
        "real_engine_metrics": None,
        "note": (
            "Structural rate accounting passes on synthetic integers, but no "
            "licensed engine, real audio, pitch or transient measurement, "
            "buffering measurement, device clock or rights-cleared cohort "
            "exists, so the Rate profile is not satisfied for "
            "qualification."),
    }


def _qualification_block(gates: list[dict]) -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "blocked_gate_count": len(gates),
        "blocked_gate_ids": [gate["id"] for gate in gates],
        "reason": (
            "The licensed IRCAM SuperVP SDK or host runtime, exact build, "
            "commercial agreement, runtime/platform lock, API geometry, "
            "rights-cleared rate cohort and parity vector are absent. The "
            "public product description records a commercial research option "
            "whose embedding terms require a separate IRCAM agreement; no "
            "price, redistribution grant or output-use right is recorded."),
    }


def _gates() -> list[dict]:
    return [
        {"id": gate_id, "gate": name, "requirement": requirement,
         "status": "blocked"}
        for gate_id, name, requirement in GATE_REQUIREMENTS
    ]


def _blockers() -> list[dict]:
    return [
        {"id": blocker_id, "gate_id": gate_id, "state": "open",
         "requirement": requirement}
        for blocker_id, gate_id, _, requirement in EXACT_BLOCKERS
    ]


def _artifacts() -> list[dict]:
    return [
        {"id": artifact_id, "kind": kind, "requirement": requirement,
         "status": "absent"}
        for artifact_id, kind, requirement in REQUIRED_ARTIFACTS
    ]


def _reopen_conditions() -> list[dict]:
    return [
        {"gate_id": gate_id, "condition": requirement}
        for gate_id, _, requirement in GATE_REQUIREMENTS
    ]


def _profile_source_block() -> dict:
    return profile_source()


def _asset_audit_block() -> dict:
    probes = absence_probes()
    summary = absence_summary(probes)
    return {
        "qualified": False,
        "audit_result": "absent",
        "source": source_probe(),
        "runtime": runtime_probe(),
        "rights": rights_probe(),
        "cohort": cohort_probe(),
        "absence": summary,
        "observed_absence_probes": probes,
        "note": (
            "No licensed IRCAM SuperVP source, SDK, binary, runtime, "
            "commercial terms, rights record, rate cohort or parity vector "
            "was observed. Public product documentation is provenance, not "
            "an asset or a grant."),
    }


def _geometry_block() -> dict:
    return {
        "supervp_geometry_status": GEOMETRY_STATUS,
        "supervp_geometry_asserted": False,
        "task_kind": TASK_KIND,
        "task_scope": TASK_SCOPE,
        "condition": TASK_CONDITION,
        "rate_actuator": True,
        "playback_clock_owner": "caller",
        "sample_rate_hz": None,
        "channels": None,
        "hop_samples": None,
        "latency_samples": None,
        "rate_semantics_verified": False,
        "streaming_supported": None,
        "reset_flush_verified": False,
        "final_partial_window_policy": None,
        "note": (
            "No licensed API reference establishes sample rate, channels, "
            "hop, latency, rate semantics, streaming, reset, flush or the "
            "final partial window. The package does not assert vendor "
            "geometry."),
    }


def build_report() -> dict:
    identity = task_row_identity()
    gates = _gates()
    control = build_control()
    audit = _asset_audit_block()
    profile = _rate_profile_block()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "task_id": TASK,
        "component": COMPONENT,
        "component_id": COMPONENT_ID,
        "title": TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_source": _profile_source_block(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION_STATUS,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": WRITE_SCOPE,
        "disposition": dict(DISPOSITION),
        "qualification": _qualification_block(gates),
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "task_row_identity": identity,
        "linked_row_identity": linked_row_identity(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "upstream_record": {
            "name": UPSTREAM_NAME,
            "record_name": UPSTREAM_RECORD_NAME,
            "vendor": UPSTREAM_VENDOR,
            "product_url": PRODUCT_URL,
            "forum_ts2_url": FORUM_TS2_URL,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "public_source_available": PUBLIC_SOURCE_AVAILABLE,
            "public_binary_available": PUBLIC_BINARY_AVAILABLE,
            "embedding_requires_separate_agreement":
                EMBEDDING_REQUIRES_SEPARATE_AGREEMENT,
            "commercial_license_status": COMMERCIAL_LICENSE_STATUS,
            "price_recorded": PRICE_RECORDED,
            "current_sdk_availability_verified":
                CURRENT_SDK_AVAILABILITY_VERIFIED,
            "task_kind": TASK_KIND,
            "task_scope": TASK_SCOPE,
            "condition": TASK_CONDITION,
            "geometry_status": GEOMETRY_STATUS,
        },
        "source_reported_context": dict(SOURCE_REPORTED_CONTEXT),
        "geometry": _geometry_block(),
        "rate_profile": profile,
        "asset_requirements": [dict(item) for item in CALLER_ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_evidence": audit["absence"],
        "absence_probes": audit["observed_absence_probes"],
        "caller_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "reference_protocol": control,
        "controls": {
            "adverse_all_rejected": all(
                item["result"] == "rejected" for item in control["adverse"]),
            "adverse": control["adverse"],
            "adverse_case_count": len(control["adverse"]),
            "nonfinite_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "scope_mismatch_rejected": True,
            "streaming_variant_rejected": True,
            "commercial_terms_required": True,
            "validator_accepts_well_formed_manifest": True,
            "absence_probes_all_absent":
                audit["absence"]["all_probes_absent"],
            "engine_never_executed": True,
        },
        "required_artifacts": _artifacts(),
        "gates": gates,
        "remaining_gates": [
            {"id": gate["id"], "requirement": gate["requirement"],
             "status": "blocked"} for gate in gates],
        "exact_blockers": _blockers(),
        "reopen_conditions": _reopen_conditions(),
        "rights_gap": dict(RIGHTS_GAP),
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            "vendor/ircam-supervp",
            "data/vendor/ircam-supervp",
            "data/envs/ircam-supervp/requirements.lock",
            "data/rights/ircam-supervp-rights.json",
            "data/runs/ircam-supervp-rate-cohort/manifest.json",
            "data/runs/ircam-supervp-parity/manifest.json",
        ],
        "non_claims": list(NON_CLAIMS),
        "prohibited_claims": list(NON_CLAIMS),
        "exact_scope": {
            "write_scope": TASK_PREFIX,
            "task_local_only": True,
            "adapter_added": False,
            "provider_added": False,
            "binary_added": False,
            "asset_added": False,
        },
        "reproduction": {
            "tests": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "-m unittest -v test_reference.py"),
            "regenerate": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "run.py"),
            "verify": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "verify.py"),
            "cold_start_regenerations": 3,
            "comparison": (
                "canonical JSON bytes, SHA-256 sidecar, README digest table "
                "and source manifest only; no tolerance"),
        },
        "tool_provenance": [
            "Python standard library only; no vendor SDK, engine or audio "
            "runtime is imported.",
            "Fixed workspace paths are probed for source, runtime, rights and "
            "cohort presence; no recursive walk is performed.",
            "No source checkout is executed and no binary byte is read.",
            "No network request, download, price lookup, audio device, engine "
            "load or timing run occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, ensure_ascii=True, "
                "allow_nan=False, trailing newline"),
            "integers_only": True,
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
        "licensing": {
            "package_license": "Apache-2.0",
            "spdx_file_copyright": "2026 Tsakanyan Hovhannes",
            "spdx_license_identifier": "Apache-2.0",
            "generated_json_sidecars": True,
            "vendor_license": (
                "unverified; no IRCAM agreement, licence text, price or "
                "redistribution grant is present or recorded"),
        },
    }


def build_contract() -> dict:
    identity = task_row_identity()
    gates = _gates()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "component_id": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "profile_source": profile_source(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": dict(DISPOSITION),
        "qualification": _qualification_block(gates),
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": WRITE_SCOPE,
        "task_row_identity": identity,
        "linked_row_identity": linked_row_identity(),
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "upstream_record": {
            "name": UPSTREAM_NAME,
            "record_name": UPSTREAM_RECORD_NAME,
            "vendor": UPSTREAM_VENDOR,
            "product_url": PRODUCT_URL,
            "forum_ts2_url": FORUM_TS2_URL,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "public_source_available": PUBLIC_SOURCE_AVAILABLE,
            "public_binary_available": PUBLIC_BINARY_AVAILABLE,
            "embedding_requires_separate_agreement":
                EMBEDDING_REQUIRES_SEPARATE_AGREEMENT,
            "commercial_license_status": COMMERCIAL_LICENSE_STATUS,
            "price_recorded": PRICE_RECORDED,
            "current_sdk_availability_verified":
                CURRENT_SDK_AVAILABILITY_VERIFIED,
            "task_kind": TASK_KIND,
            "task_scope": TASK_SCOPE,
            "condition": TASK_CONDITION,
            "geometry_status": GEOMETRY_STATUS,
        },
        "geometry": _geometry_block(),
        "rate_profile_requirements": [
            {"id": item, "requirement": requirement, "status": status}
            for item, requirement, status in RATE_REQUIREMENTS
        ],
        "asset_requirements": [dict(item) for item in CALLER_ASSET_REQUIREMENTS],
        "caller_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "required_artifacts": _artifacts(),
        "gates": gates,
        "exact_blockers": _blockers(),
        "reopen_conditions": _reopen_conditions(),
        "rights_gap": dict(RIGHTS_GAP),
        "missing_historical_artifacts": [
            "vendor/ircam-supervp",
            "data/vendor/ircam-supervp",
            "data/envs/ircam-supervp/requirements.lock",
            "data/rights/ircam-supervp-rights.json",
            "data/runs/ircam-supervp-rate-cohort/manifest.json",
            "data/runs/ircam-supervp-parity/manifest.json",
        ],
        "reproduction": {
            "tests": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "-m unittest -v test_reference.py"),
            "regenerate": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "run.py"),
            "verify": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "verify.py"),
            "cold_start_regenerations": 3,
            "comparison": (
                "canonical JSON bytes, SHA-256 sidecar, README digest table "
                "and source manifest only; no tolerance"),
        },
        "licensing": {
            "spdx_file_copyright": "2026 Tsakanyan Hovhannes",
            "spdx_license_identifier": "Apache-2.0",
            "generated_json_sidecars": True,
            "vendor_license": (
                "unverified; no IRCAM agreement, licence text, price or "
                "redistribution grant is present or recorded"),
        },
    }
