# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for the BIC segmentation task.

Task ``SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION`` is a
feasibility investigation for inventory component
``bayesian-information-criterion-speaker-segmentation`` (category ``SPK-03``,
legacy family ``F06``, verification profile ``spatial``).

The workspace contains **no** approved implementation, source checkout,
runtime, build record, rights record, annotated-meeting change corpus or
exact-parity vector for BIC speaker-change segmentation.  The merged evidence
is a paper lead (``S04``) and a sibling evidence map that records the row as
``considered`` only.  This module therefore never imports, builds, links or
executes an upstream segmenter, never reads audio or a corpus, never downloads
anything and never measures a speaker-change, segment-purity or diarization
result.

What it does implement is a bounded, declared **synthetic feature-domain**
arithmetic control for the classical adjacent-window BIC comparison.  It is a
task-local reference formula, not an upstream implementation and not audio
segmentation.  Its synthetic change points never qualify the candidate.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(
    os.environ.get("AUDIOML_WORKSPACE_ROOT", str(SDK_ROOT.parents[2]))
).resolve()

TASK = "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION"
TITLE = "Bayesian information criterion speaker segmentation"
SLUG = "bayesian-information-criterion-speaker-segmentation"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "72a52fc65f0b6db703d22714b8f7305642e4b412"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    + TASK
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "spatial"
MODE = "feasibility"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_provider_intake"

# REUSE-IgnoreStart
LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-Identifier: Apache-2.0\n"
)
# REUSE-IgnoreEnd

# Deterministic synthetic geometry.  These values describe the task-local
# control only; the real component's window/hop/penalty/feature geometry is
# unestablished and remains blocked.
CONTROL_SAMPLE_RATE_HZ = 16000
CONTROL_CHANNELS = 1
SDK_FRAME_SAMPLES = 160
CONTROL_FRAME_HOP_SAMPLES = 160
CONTROL_WINDOW_FRAMES = 15
CONTROL_HOP_FRAMES = 1
CONTROL_MIN_SEGMENT_FRAMES = 15
CONTROL_STREAM_FRAMES = 90
CONTROL_SEGMENT_FRAMES = 30
CONTROL_PLANTED_BOUNDARIES = (30, 60)
CONTROL_FEATURE_DIM = 2
CONTROL_SEED = 20261126
CONTROL_LOOKAHEAD_FRAMES = CONTROL_WINDOW_FRAMES
CONTROL_LOOKAHEAD_SAMPLES = CONTROL_LOOKAHEAD_FRAMES * CONTROL_FRAME_HOP_SAMPLES
CONTROL_LOOKAHEAD_MS = Fraction(
    CONTROL_LOOKAHEAD_SAMPLES * 1000, CONTROL_SAMPLE_RATE_HZ
)
CONTROL_PENALTY_WEIGHT = Fraction(1, 1)
CONTROL_THRESHOLD = Fraction(0, 1)
BIC_FORMULA_ID = "adjacent-window-covariance-bic/0.1"
BIC_SELECTION_POLICY = (
    "score-descending-then-earliest-with-min-segment-separation/0.1"
)
BIC_DECIMAL_PRECISION = 60
SCORE_PLACES = 12
SCORE_QUANTUM = Decimal(1).scaleb(-SCORE_PLACES)
MAX_ABS_FEATURE = 1_000_000
MAX_FEATURE_DIM = 64
MAX_WINDOW_FRAMES = 100_000

ABSENCE_PROBES: Tuple[str, ...] = (
    "research/repos/bic-speaker-segmentation",
    "research/repos/bayesian-information-criterion-speaker-segmentation",
    "research/repos/sivakumaran-bic",
    "research/repos/pyannote-segmentation",
    "data/checkouts/bic-speaker-segmentation",
    "data/checkouts/bayesian-information-criterion-speaker-segmentation",
    "data/models/bic-speaker-segmentation",
    "data/weights/bic-speaker-segmentation",
    "data/envs/bic-speaker-segmentation",
    "data/build-records/bic-speaker-segmentation.json",
    "data/rights/bic-speaker-segmentation-rights.json",
    "data/annotations/speaker-change-ami",
    "data/runs/bic-speaker-change-cohort/manifest.json",
    "data/runs/bic-speaker-change-parity/manifest.json",
    "third_party/bic-speaker-segmentation",
    "third_party/pyannote-segmentation",
    "deps/bic-speaker-segmentation",
)

STABLE_TASK_FIELDS = (
    "acceptance",
    "component",
    "deliverable",
    "depends_on",
    "evidence",
    "id",
    "mode",
    "repository",
    "title",
    "write_scope",
)
MUTABLE_TASK_FIELDS = (
    "blocked_reason",
    "dispatch_priority",
    "handoff",
    "owner",
    "review",
    "status",
)

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/PIPELINES.md":
        "4d950978277dff9c562059d25d43ad5d2a85a46bb7a97aabb8518edaa0faea47",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/revisions/v1/audio_categories.md":
        "24411d808836d89b730ba3522e6b5ade34d0acd70df235f043cd36155974c265",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/plans/F02/vad_accuracy_contract.md":
        "f6650aa3206cb694dffc4b429e0fe1f34c5ecd097cbfda7e522083cad7be1cec",
    "research/voice-enhancement-20261101/agent-hush-ami/REPORT.md":
        "f25be2b5e5e09fe3aacc9bece33e5e9ec56a548f1349871e916d46f4ba2a5acf",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md":
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/acceptance-matrix.md":
        "2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/adaptive-energy-vad/README.md":
        "2de4b185d679f031c80625bd64e195cbabb69c62ea9499ef99f9868752ed86a2",
    "docs/task-evidence/survey-det-01/README.md":
        "88430878409af7a5cdb74dbc4422724b78f4c0610463fed9d5d4f29d16fffacb",
    "docs/task-evidence/survey-spk-03/README.md":
        "23ce702da0e193d693a089fd157bcdb58ea485db09859bf291c2f1ce746967b6",
    "docs/task-evidence/survey-spk-04/README.md":
        "40ee3de6cb3683ab1abf87e21a41ff807b50c5a16220bb9242156e725ae45112",
    "docs/task-evidence/webrtc-vad/README.md":
        "1b3c5968c187b97bd67dcf2006581bd111d3cddc03911d5530d9e14325dfbc65",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"
INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"
CATEGORY_REGISTRY_PATH = "research/category_registry.json"
CATEGORY_ID = "SPK-03"
SOURCE_ID = "S04"

BOUNDARY_FALSE_FLAGS: Tuple[str, ...] = (
    "abi_change",
    "adapter_json_added",
    "annotation_events_added",
    "asset_bundled",
    "benchmark_claim",
    "ci_change",
    "default_selected",
    "descriptor_registry_change",
    "diarization_enabled",
    "enabled_by_default",
    "handoff_changed",
    "installed_v0_behavior_change",
    "network_used",
    "processor_exposure",
    "provider_registration",
    "public_api_abi_change",
    "registered",
    "release_approval",
    "segmenter_compiled",
    "segmenter_executed",
    "shared_build_or_ci_change",
    "speaker_identity_claim",
    "weights_vendored",
)
BOUNDARY: Dict[str, Any] = {flag: False for flag in BOUNDARY_FALSE_FLAGS}

SCOPE_FALSE_FLAGS: Tuple[str, ...] = (
    "annotated_meeting_corpus",
    "benchmark_claim",
    "change_point_label_set",
    "device_timing",
    "diarization_claim",
    "external_runtime_invoked",
    "false_alarm_rate_measured",
    "listening",
    "network_used",
    "numeric_parity_claim",
    "real_audio",
    "real_corpus",
    "release_claim",
    "segment_purity_measured",
    "speaker_change_execution",
    "speaker_identity_claim",
    "upstream_source_present",
    "upstream_runtime_invoked",
    "weights_loaded",
)
SCOPE_TRUE_FLAGS: Tuple[str, ...] = (
    "feature_domain_synthetic_control",
    "proposal_only",
    "task_local_only",
)
SCOPE: Dict[str, Any] = {
    **{flag: False for flag in SCOPE_FALSE_FLAGS},
    **{flag: True for flag in SCOPE_TRUE_FLAGS},
}

NON_CLAIMS: Tuple[str, ...] = (
    "No BIC or other speaker-change implementation, source checkout, header or binary is loaded, built, linked or executed.",
    "No upstream repository URL, revision, release, artifact hash, build record or licence grant is invented.",
    "The S04 paper lead is a method citation, not a source checkout or a licence grant.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, annotated meeting, change-point label set, RTTM/UEM reference or corpus is read.",
    "The task-local control operates on deterministic synthetic feature vectors and is not audio segmentation.",
    "No speaker-change boundary, false-alarm, miss, segment-purity, diarization or identity result is measured or claimed.",
    "The synthetic planted-boundary check is not a segmentation accuracy, generalization or benchmark result.",
    "No provider, descriptor, registry, installed v0 path, analysis event surface, shared build or CI changed.",
    "No listening, device timing, resource, deadline or release qualification is performed.",
    "Missing source, runtime, rights, cohort or parity evidence never qualifies the candidate; the decision remains DEFER.",
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_asset_identity",
        "The exact approved BIC implementation source, canonical upstream URL, full 40-hex revision, per-file SHA-256 values and source licence match immutable pins.",
    ),
    (
        "runtime_admission",
        "An isolated, hash-pinned runtime and reproducible build record execute the exact implementation on a recorded platform.",
    ),
    (
        "artifact_rights_and_licence",
        "The implementation licence, notices, source/output use and annotated-meeting corpus rights are verified with dated evidence.",
    ),
    (
        "exact_reference_parity",
        "An approved exact-runtime BIC output matches a frozen caller-supplied input, feature configuration and annotation schema.",
    ),
    (
        "spatial_cohort_and_scoring",
        "A rights-cleared, speaker/session-disjoint annotated-meeting cohort scores speaker-change boundaries, false alarms, misses, boundary deviation and segment purity under the spatial profile.",
    ),
    (
        "task_geometry_and_adapter_boundary",
        "The feature front end, window, hop, lookahead, penalty, threshold, minimum segment, merge policy, annotation schema and offline analysis adapter boundary are fixed and documented.",
    ),
    (
        "opt_in_provider_intake",
        "Explicit opt-in intake, licence review, descriptor review, optional-runtime absence behaviour and an independent public-surface decision are complete.",
    ),
    (
        "public_default_and_release",
        "Explicit default selection, paced resource/deadline evidence and release or public-benchmark approval are recorded; this package is off by default.",
    ),
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "source_checkout_absent",
        "requirement": "Supply the exact approved BIC segmentation implementation under research/repos/bic-speaker-segmentation or data/checkouts/bic-speaker-segmentation at an immutable 40-hex revision with a per-file SHA-256 manifest; no BIC or speaker-segmentation checkout exists anywhere in the workspace.",
        "state": "absent",
    },
    {
        "id": "upstream_identity_unpinned",
        "requirement": "Record the canonical upstream repository and project URLs, a full 40-hex commit, release or tag, and per-file SHA-256 values; the merged registry records only the S04 paper title and ISCA URL, with no code URL, commit or digest.",
        "state": "absent",
    },
    {
        "id": "runtime_and_build_record_absent",
        "requirement": "Provide an isolated hash-pinned runtime with a dependency lock and a reproducible build/execution record at data/build-records/bic-speaker-segmentation.json; no environment, lock or build record exists.",
        "state": "absent",
    },
    {
        "id": "source_license_and_rights_unverified",
        "requirement": "Supply the exact implementation licence, notice text, source/output-use terms and a dated rights decision; the S04 paper citation is not a licence grant and no rights record exists at data/rights/bic-speaker-segmentation-rights.json.",
        "state": "absent",
    },
    {
        "id": "speaker_change_corpus_and_rights_absent",
        "requirement": "Supply a rights-cleared annotated-meeting corpus with speaker-change truth, scored regions, RTTM/UEM or equivalent labels, a declared collar/unknown policy and a speaker/session-disjoint frozen split under data/annotations/speaker-change-ami; none exists.",
        "state": "absent",
    },
    {
        "id": "task_geometry_and_adapter_absent",
        "requirement": "Fix the feature front end, window, hop, lookahead, BIC penalty, threshold, minimum segment length, merge policy, annotation schema, availability policy and offline analysis adapter boundary in a reviewed configuration; none is selected.",
        "state": "absent",
    },
    {
        "id": "exact_reference_parity_absent",
        "requirement": "Provide an approved exact-runtime output on a frozen caller input and configuration at data/runs/bic-speaker-change-parity/manifest.json; the task-local synthetic arithmetic is not parity with any upstream implementation.",
        "state": "absent",
    },
    {
        "id": "benchmark_and_release_absent",
        "requirement": "Provide a held-out annotated-meeting benchmark for boundary precision/recall, false-alarm and miss rates, boundary deviation and segment purity, plus paced resource/deadline evidence and release approval; no benchmark or release record exists.",
        "state": "absent",
    },
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "source_checkout",
        "path": "research/repos/bic-speaker-segmentation",
        "required": True,
        "revision": None,
        "recorded_name": "Bayesian information criterion speaker segmentation",
        "recorded_source_id": SOURCE_ID,
        "status": "absent",
    },
    {
        "id": "upstream_identity",
        "project_url": None,
        "repository_url": None,
        "required": True,
        "sha256": None,
        "status": "absent",
    },
    {
        "id": "runtime_and_build",
        "path": "data/envs/bic-speaker-segmentation",
        "runtime_lock_path": "data/envs/bic-speaker-segmentation/requirements.lock",
        "runtime_lock_sha256": None,
        "build_record_path": "data/build-records/bic-speaker-segmentation.json",
        "build_record_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "source_license_record",
        "path": "data/rights/bic-speaker-segmentation-license.json",
        "required": True,
        "recorded_license": None,
        "status": "absent",
    },
    {
        "id": "speaker_change_corpus_and_rights",
        "cohort_path": "data/annotations/speaker-change-ami/manifest.json",
        "rights_path": "data/rights/bic-speaker-segmentation-rights.json",
        "required": True,
        "status": "absent",
    },
    {
        "id": "task_geometry_and_adapter",
        "config_path": "data/plans/bic-speaker-segmentation-adapter.json",
        "required": True,
        "task_geometry_status": "unestablished",
        "status": "absent",
    },
    {
        "id": "exact_parity_vector",
        "parity_path": "data/runs/bic-speaker-change-parity/manifest.json",
        "required": True,
        "status": "absent",
    },
    {
        "id": "benchmark_and_release",
        "benchmark_path": "data/runs/bic-speaker-change-cohort/manifest.json",
        "release_path": "data/runs/bic-speaker-change-release.json",
        "required": True,
        "status": "absent",
    },
)

MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter_config_path",
    "adapter_config_sha256",
    "benchmark_record_path",
    "benchmark_record_sha256",
    "build_record_path",
    "build_record_sha256",
    "channels",
    "claimed_bic_segmentation_capability",
    "corpus_manifest_path",
    "corpus_manifest_sha256",
    "feature_dim",
    "frame_samples",
    "hop_frames",
    "license_record_path",
    "license_record_sha256",
    "lookahead_frames",
    "min_segment_frames",
    "parity_vector_path",
    "parity_vector_sha256",
    "penalty_weight",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "sample_rate_hz",
    "source_checkout_path",
    "source_manifest_path",
    "source_manifest_sha256",
    "source_revision",
    "threshold",
    "variant",
    "window_frames",
)
MANIFEST_PATH_FIELDS: Tuple[str, ...] = tuple(
    field for field in MANIFEST_FIELDS
    if field.endswith("_path") and field != "source_revision"
)
MANIFEST_SHA_FIELDS: Tuple[str, ...] = tuple(
    field for field in MANIFEST_FIELDS if field.endswith("_sha256")
)
REQUIRED_VARIANT = "bic_offline_annotation_adapter"
CANONICAL_DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class Reject(ValueError):
    """Fail-closed rejection for malformed, unsupported or unqualified input."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            _normalize_negzero(value),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise Reject("value is not canonical-JSON serializable") from error


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def strict_loads(text: str) -> Dict[str, Any]:
    """Parse strict JSON, rejecting duplicate keys and non-finite constants."""

    def reject(value: str) -> Any:
        raise Reject("non-finite JSON: " + value)

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Reject("duplicate JSON key: " + key)
            result[key] = value
        return result

    value = json.loads(text, parse_constant=reject, object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise Reject("expected JSON object")
    return value


def strict_load(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise Reject("missing JSON file: " + str(path))
    try:
        return strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        raise Reject("unreadable JSON file: " + str(path)) from error


def _file_digest(relative: str, root: Path) -> str:
    path = root / relative
    if not path.is_file():
        raise Reject("pinned file missing: " + relative)
    return sha256_file(path)


def verify_document_pins() -> None:
    for relative, digest in SOURCE_PINS.items():
        actual = _file_digest(relative, SOURCE_ROOT)
        if actual != digest:
            raise Reject("source pin changed: " + relative)
    for relative, digest in BOUNDARY_PINS.items():
        actual = _file_digest(relative, SDK_ROOT)
        if actual != digest:
            raise Reject("boundary pin changed: " + relative)
    if BOARD_PATH in SOURCE_PINS or BOARD_PATH in BOUNDARY_PINS:
        raise Reject("mutable board file must never be pinned")


def _task_board() -> Dict[str, Any]:
    return strict_load(SOURCE_ROOT / BOARD_PATH)


def task_row_identity() -> Dict[str, Any]:
    document = _task_board()
    rows = [
        row
        for row in document.get("tasks", [])
        if isinstance(row, dict) and row.get("id") == TASK
    ]
    if len(rows) != 1:
        raise Reject("expected exactly one linked task row")
    row = rows[0]
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK or stable["component"] != COMPONENT:
        raise Reject("linked task row identity mismatch")
    if stable["repository"] != "audio-sdk" or stable["mode"] != MODE:
        raise Reject("linked task row repository/mode mismatch")
    if "spatial acceptance profile" not in str(stable["acceptance"]):
        raise Reject("linked task row acceptance profile mismatch")
    if "Record a concrete blocker if feasibility fails" not in str(
        stable["deliverable"]
    ):
        raise Reject("linked task row deliverable mismatch")
    if "research/category_registry.json" not in (stable["evidence"] or []):
        raise Reject("linked task row evidence mismatch")
    if "SDK-FND-PROVIDER" not in (stable["depends_on"] or []):
        raise Reject("linked task row dependency mismatch")
    claim = row.get("claim")
    if not isinstance(claim, dict):
        raise Reject("linked task row claim missing")
    if claim.get("base_commit") != BASE_COMMIT:
        raise Reject("claim base commit mismatch")
    if claim.get("branch") != BRANCH:
        raise Reject("claim branch mismatch")
    if claim.get("worktree") != CLAIM_WORKTREE:
        raise Reject("claim worktree mismatch")
    if claim.get("reviewer") != REVIEWER:
        raise Reject("claim reviewer mismatch")
    return {
        "source": BOARD_PATH,
        "stable_fields": stable,
        "stable_sha256": sha256(canonical_bytes(stable)),
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "claim": {
            "base_commit": claim["base_commit"],
            "branch": claim["branch"],
            "worktree": claim["worktree"],
            "reviewer": claim["reviewer"],
        },
    }


def _check_inventory_and_registry() -> Dict[str, Any]:
    inventory = strict_load(SOURCE_ROOT / INVENTORY_PATH)
    rows = [
        row
        for row in inventory.get("components", [])
        if isinstance(row, dict) and row.get("id") == COMPONENT
    ]
    if len(rows) != 1:
        raise Reject("inventory component row missing or duplicated")
    row = rows[0]
    if row.get("task") != TASK:
        raise Reject("inventory task mismatch")
    if row.get("verification_profile") != PROFILE:
        raise Reject("inventory verification profile mismatch")
    if row.get("disposition") != "sdk-reference":
        raise Reject("inventory disposition mismatch")
    if row.get("evidence") != [{"path": CATEGORY_REGISTRY_PATH}]:
        raise Reject("inventory evidence mismatch")

    registry = strict_load(SOURCE_ROOT / CATEGORY_REGISTRY_PATH)
    categories = [
        value
        for value in registry.get("categories", [])
        if isinstance(value, dict) and value.get("id") == CATEGORY_ID
    ]
    if len(categories) != 1:
        raise Reject("category row missing or duplicated")
    category = categories[0]
    if category.get("name") != "Speaker change detection and segmentation":
        raise Reject("category name mismatch")
    if SOURCE_ID not in (category.get("source_ids") or []):
        raise Reject("category source lead missing")
    if "Bayesian information criterion" not in str(
        (category.get("method_families") or {}).get("classic", "")
    ):
        raise Reject("category classic method family mismatch")
    sources = [
        value
        for value in registry.get("sources", [])
        if isinstance(value, dict) and value.get("id") == SOURCE_ID
    ]
    if len(sources) != 1:
        raise Reject("S04 source row missing or duplicated")
    source = sources[0]
    if source.get("title") != (
        "Speaker segmentation using the Bayesian information criterion"
    ):
        raise Reject("S04 title mismatch")
    return {
        "category_id": CATEGORY_ID,
        "category_name": category["name"],
        "classic_method_family": category["method_families"]["classic"],
        "source_id": SOURCE_ID,
        "source_title": source["title"],
        "source_url": source["url"],
        "inventory_evidence_status": row.get("evidence_status"),
        "inventory_disposition": row.get("disposition"),
        "inventory_profile": row.get("verification_profile"),
        "inventory_plan_note": row.get("plan_note"),
    }


def probe_absence() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for relative in ABSENCE_PROBES:
        rows.append(
            {
                "path": relative,
                "source_exists": (SOURCE_ROOT / relative).exists(),
                "sdk_exists": (SDK_ROOT / relative).exists(),
                "exists": (SOURCE_ROOT / relative).exists()
                or (SDK_ROOT / relative).exists(),
            }
        )
    return rows


def _assert_absent(probes: Sequence[Mapping[str, Any]]) -> None:
    present = [row["path"] for row in probes if row.get("exists")]
    if present:
        raise Reject(
            "unexpected component artifact present without review: "
            + ", ".join(present)
        )


def _audit_assets() -> Dict[str, Any]:
    probes = probe_absence()
    _assert_absent(probes)
    return {
        "audit_result": "absent",
        "all_absence_probes_absent": True,
        "source_checkout_present": False,
        "runtime_present": False,
        "runtime_lock_present": False,
        "build_record_present": False,
        "license_record_present": False,
        "rights_record_present": False,
        "corpus_manifest_present": False,
        "parity_manifest_present": False,
        "benchmark_record_present": False,
        "source_revision": None,
        "source_revision_pin_available": False,
        "recorded_source_id": SOURCE_ID,
        "recorded_source_url": (
            "https://www.isca-archive.org/icslp_2002/"
            "sivakumaran02_icslp.html"
        ),
        "observed": {"absence_probes": probes},
        "note": (
            "No BIC implementation, runtime, build record, licence record, "
            "rights record, annotated-meeting corpus, parity vector or "
            "benchmark record was observed. The S04 paper lead is not a "
            "source checkout and is not executed."
        ),
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic feature-domain BIC arithmetic.
# ---------------------------------------------------------------------------

def _as_fraction(value: Any, field: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise Reject(field + " is not numeric")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise Reject(field + " is not finite")
        return Fraction(value)
    return Fraction(value)


def _validate_positive_int(value: Any, field: str, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject(field + " is not an integer")
    if value <= 0 or value > maximum:
        raise Reject(field + " is outside the admitted range")
    return value


def _validate_penalty(value: Any) -> Fraction:
    fraction = _as_fraction(value, "penalty_weight")
    if fraction < 0:
        raise Reject("penalty_weight must be nonnegative")
    if fraction > 1000:
        raise Reject("penalty_weight is outside the admitted range")
    return fraction


def _validate_threshold(value: Any) -> Fraction:
    fraction = _as_fraction(value, "threshold")
    if abs(fraction) > 10 ** 12:
        raise Reject("threshold is outside the admitted range")
    return fraction


def validate_feature_stream(
    stream: Any, feature_dim: int
) -> Tuple[Tuple[Fraction, ...], ...]:
    if isinstance(stream, (str, bytes)) or not isinstance(stream, Sequence):
        raise Reject("feature stream must be a sequence")
    if not stream:
        raise Reject("feature stream must be nonempty")
    dim = _validate_positive_int(feature_dim, "feature_dim", MAX_FEATURE_DIM)
    frames: List[Tuple[Fraction, ...]] = []
    for index, frame in enumerate(stream):
        if isinstance(frame, (str, bytes)) or not isinstance(frame, Sequence):
            raise Reject("frame %d is not a sequence" % index)
        if len(frame) != dim:
            raise Reject("frame %d has the wrong dimension" % index)
        values: List[Fraction] = []
        for column, value in enumerate(frame):
            fraction = _as_fraction(
                value, "frame %d column %d" % (index, column)
            )
            if abs(fraction) > MAX_ABS_FEATURE:
                raise Reject(
                    "frame %d column %d is outside the admitted range"
                    % (index, column)
                )
            values.append(fraction)
        frames.append(tuple(values))
    return tuple(frames)


def _mean_vector(window: Sequence[Sequence[Fraction]]) -> List[Fraction]:
    count = len(window)
    dim = len(window[0])
    return [
        sum((frame[column] for frame in window), Fraction(0)) / count
        for column in range(dim)
    ]


def covariance_matrix(
    window: Sequence[Sequence[Fraction]],
) -> List[List[Fraction]]:
    count = len(window)
    dim = len(window[0])
    mean = _mean_vector(window)
    return [
        [
            sum(
                (
                    (frame[row] - mean[row]) * (frame[column] - mean[column])
                    for frame in window
                ),
                Fraction(0),
            )
            / count
            for column in range(dim)
        ]
        for row in range(dim)
    ]


def determinant(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise Reject("determinant requires a square nonempty matrix")
    work = [list(row) for row in matrix]
    sign = 1
    previous = Fraction(1)
    for pivot in range(size - 1):
        if work[pivot][pivot] == 0:
            for candidate in range(pivot + 1, size):
                if work[candidate][pivot] != 0:
                    work[pivot], work[candidate] = (
                        work[candidate],
                        work[pivot],
                    )
                    sign = -sign
                    break
            else:
                return Fraction(0)
        for row in range(pivot + 1, size):
            for column in range(pivot + 1, size):
                work[row][column] = (
                    work[row][column] * work[pivot][pivot]
                    - work[row][pivot] * work[pivot][column]
                ) / previous
        previous = work[pivot][pivot]
    return Fraction(sign) * work[size - 1][size - 1]


def _ln_fraction(value: Fraction) -> Decimal:
    if value <= 0:
        raise Reject("logarithm requires a positive value")
    with localcontext() as context:
        context.prec = BIC_DECIMAL_PRECISION
        return Decimal(value.numerator).ln() - Decimal(value.denominator).ln()


def bic_delta(
    left: Sequence[Sequence[Fraction]],
    right: Sequence[Sequence[Fraction]],
    penalty_weight: Any = CONTROL_PENALTY_WEIGHT,
) -> Decimal:
    """Return the adjacent-window BIC delta; positive favours one change."""
    if not left or not right:
        raise Reject("BIC windows must be nonempty")
    dim = len(left[0])
    if dim == 0 or len(right[0]) != dim:
        raise Reject("BIC windows have inconsistent dimensions")
    if any(len(frame) != dim for frame in left):
        raise Reject("left BIC window has inconsistent dimensions")
    if any(len(frame) != dim for frame in right):
        raise Reject("right BIC window has inconsistent dimensions")
    if len(left) < 2 or len(right) < 2:
        raise Reject("BIC windows require at least two frames")
    penalty = _validate_penalty(penalty_weight)
    pooled = list(left) + list(right)
    pooled_det = determinant(covariance_matrix(pooled))
    left_det = determinant(covariance_matrix(left))
    right_det = determinant(covariance_matrix(right))
    if pooled_det <= 0 or left_det <= 0 or right_det <= 0:
        raise Reject("BIC covariance is singular or not positive")
    left_count = len(left)
    right_count = len(right)
    total = left_count + right_count
    free_parameters = Fraction(dim) + Fraction(dim * (dim + 1), 2)
    with localcontext() as context:
        context.prec = BIC_DECIMAL_PRECISION
        score = (
            Decimal(total) * _ln_fraction(pooled_det)
            - Decimal(left_count) * _ln_fraction(left_det)
            - Decimal(right_count) * _ln_fraction(right_det)
        )
        score -= (
            Decimal(penalty.numerator)
            / Decimal(penalty.denominator)
            * Decimal(free_parameters.numerator)
            / Decimal(2)
            * Decimal(total).ln()
        )
    if not score.is_finite():
        raise Reject("BIC score is not finite")
    return score


def score_text(score: Decimal, places: int = SCORE_PLACES) -> str:
    if not isinstance(score, Decimal) or not score.is_finite():
        raise Reject("score is not a finite Decimal")
    with localcontext() as context:
        context.prec = BIC_DECIMAL_PRECISION
        quantized = score.quantize(
            Decimal(1).scaleb(-places), rounding=ROUND_HALF_EVEN
        )
    text = format(quantized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in ("-0", ""):
        text = "0"
    return text


def _lcg(state: int) -> int:
    return (1103515245 * state + 12345) % (2 ** 31)


def _jitter(state: int) -> Tuple[int, Fraction]:
    state = _lcg(state)
    return state, Fraction(state, 2 ** 31) - Fraction(1, 2)


def synthetic_feature_stream() -> Tuple[Tuple[Fraction, Fraction], ...]:
    """Deterministic three-segment 2-D stream; not audio and not speech."""
    means = ((Fraction(0), Fraction(0)),
             (Fraction(3), Fraction(1)),
             (Fraction(0), Fraction(3)))
    state = CONTROL_SEED
    frames: List[Tuple[Fraction, Fraction]] = []
    for mean in means:
        for _ in range(CONTROL_SEGMENT_FRAMES):
            state, first = _jitter(state)
            state, second = _jitter(state)
            frames.append(
                (mean[0] + first / 5, mean[1] + second / 5)
            )
    return tuple(frames)


def constant_feature_stream(
    value: Fraction = Fraction(1, 1)
) -> Tuple[Tuple[Fraction, Fraction], ...]:
    """A one-segment stream with deterministic jitter (not singular)."""
    state = CONTROL_SEED
    frames: List[Tuple[Fraction, Fraction]] = []
    for _ in range(CONTROL_STREAM_FRAMES):
        state, first = _jitter(state)
        state, second = _jitter(state)
        frames.append((value + first / 5, value + second / 5))
    return tuple(frames)


def feature_stream_digest(
    stream: Sequence[Sequence[Fraction]],
) -> str:
    payload = [
        [[value.numerator, value.denominator] for value in frame]
        for frame in stream
    ]
    return sha256(canonical_bytes(payload))


def segments_from_boundaries(
    boundaries: Sequence[int], total_frames: int
) -> List[Dict[str, int]]:
    if not isinstance(total_frames, int) or isinstance(total_frames, bool):
        raise Reject("total_frames must be an integer")
    if total_frames <= 0:
        raise Reject("total_frames must be positive")
    previous = 0
    segments: List[Dict[str, int]] = []
    for boundary in boundaries:
        if isinstance(boundary, bool) or not isinstance(boundary, int):
            raise Reject("boundary is not an integer")
        if not previous < boundary < total_frames:
            raise Reject("boundary is not strictly inside the stream")
        segments.append(
            {
                "start_frame": previous,
                "end_frame": boundary,
                "start_sample": previous * CONTROL_FRAME_HOP_SAMPLES,
                "end_sample": boundary * CONTROL_FRAME_HOP_SAMPLES,
            }
        )
        previous = boundary
    segments.append(
        {
            "start_frame": previous,
            "end_frame": total_frames,
            "start_sample": previous * CONTROL_FRAME_HOP_SAMPLES,
            "end_sample": total_frames * CONTROL_FRAME_HOP_SAMPLES,
        }
    )
    return segments


def detect_change_points(
    stream: Any,
    *,
    feature_dim: int = CONTROL_FEATURE_DIM,
    window_frames: int = CONTROL_WINDOW_FRAMES,
    hop_frames: int = CONTROL_HOP_FRAMES,
    min_segment_frames: int = CONTROL_MIN_SEGMENT_FRAMES,
    penalty_weight: Any = CONTROL_PENALTY_WEIGHT,
    threshold: Any = CONTROL_THRESHOLD,
) -> Dict[str, Any]:
    """Run the declared BIC scan and deterministic non-maximum suppression."""
    window = _validate_positive_int(
        window_frames, "window_frames", MAX_WINDOW_FRAMES
    )
    hop = _validate_positive_int(hop_frames, "hop_frames", MAX_WINDOW_FRAMES)
    minimum = _validate_positive_int(
        min_segment_frames, "min_segment_frames", MAX_WINDOW_FRAMES
    )
    if window < 2:
        raise Reject("window_frames must be at least two")
    if minimum < window:
        raise Reject("min_segment_frames must be at least window_frames")
    penalty = _validate_penalty(penalty_weight)
    cutoff = _validate_threshold(threshold)
    frames = validate_feature_stream(stream, feature_dim)
    total = len(frames)
    if total < 2 * minimum:
        raise Reject("feature stream is too short for the declared geometry")
    candidates: List[Tuple[Decimal, int]] = []
    evaluated = 0
    first = minimum
    last = total - minimum
    for boundary in range(first, last + 1, hop):
        left = frames[boundary - window:boundary]
        right = frames[boundary:boundary + window]
        score = bic_delta(left, right, penalty)
        evaluated += 1
        if score > cutoff:
            candidates.append((score, boundary))
    ordered = sorted(candidates, key=lambda row: (-row[0], row[1]))
    accepted: List[int] = []
    for _score, boundary in ordered:
        if all(abs(boundary - taken) >= minimum for taken in accepted):
            accepted.append(boundary)
    accepted.sort()
    segments = segments_from_boundaries(accepted, total)
    top = [
        {"frame": boundary, "score": score_text(score)}
        for score, boundary in ordered[:5]
    ]
    return {
        "formula_id": BIC_FORMULA_ID,
        "selection_policy": BIC_SELECTION_POLICY,
        "feature_dim": feature_dim,
        "window_frames": window,
        "hop_frames": hop,
        "min_segment_frames": minimum,
        "penalty_weight": score_text(Decimal(
            penalty.numerator) / Decimal(penalty.denominator)),
        "threshold": score_text(Decimal(
            cutoff.numerator) / Decimal(cutoff.denominator)),
        "lookahead_frames": window,
        "lookahead_samples": window * CONTROL_FRAME_HOP_SAMPLES,
        "causal": False,
        "total_frames": total,
        "evaluated_candidates": evaluated,
        "positive_candidates": len(candidates),
        "top_candidates": top,
        "change_points": accepted,
        "segments": segments,
    }


def synthetic_control() -> Dict[str, Any]:
    stream = synthetic_feature_stream()
    result = detect_change_points(stream)
    planted = list(CONTROL_PLANTED_BOUNDARIES)
    detected = list(result["change_points"])
    matches = [value for value in detected if value in planted]
    false_alarms = [value for value in detected if value not in planted]
    misses = [value for value in planted if value not in detected]
    offsets = sorted(value - planted[index]
                     for index, value in enumerate(matches))
    negative_stream = constant_feature_stream()
    negative = detect_change_points(negative_stream)
    singular = {
        "case": "identical_frames_singular_covariance",
        "result": "rejected",
        "reason": "",
    }
    try:
        detect_change_points(
            tuple((Fraction(0), Fraction(0))
                  for _ in range(CONTROL_STREAM_FRAMES))
        )
    except Reject as error:
        singular["reason"] = str(error)
    else:
        singular["result"] = "accepted"
    return {
        "control_id": "bic-synthetic-feature-domain/0.1",
        "control_scope": (
            "deterministic synthetic 2-D feature vectors only; no audio, no "
            "speech, no speaker, no annotated meeting and no upstream runtime"
        ),
        "qualifies_candidate": False,
        "not_audio": True,
        "not_speaker_evidence": True,
        "metric_scope": "synthetic_feature_domain_not_a_segmentation_result",
        "stream_frames": len(stream),
        "feature_dim": CONTROL_FEATURE_DIM,
        "segment_frames": CONTROL_SEGMENT_FRAMES,
        "planted_boundaries": planted,
        "detected_boundaries": detected,
        "exact_matches": matches,
        "false_alarms": false_alarms,
        "misses": misses,
        "matched_boundary_offsets_frames": offsets,
        "detection_result": result,
        "feature_stream_sha256": feature_stream_digest(stream),
        "negative_control": {
            "stream": "constant mean with deterministic jitter",
            "planted_boundaries": [],
            "detected_boundaries": negative["change_points"],
            "expected_no_change": True,
            "result": (
                "no_change"
                if not negative["change_points"]
                else "unexpected_change"
            ),
            "qualifies_candidate": False,
        },
        "singular_control": singular,
        "failure_envelope": (
            "A perfect planted-boundary match on a synthetic feature stream "
            "proves only that the local arithmetic scan and suppression policy "
            "are deterministic. It does not measure audio segmentation, "
            "false alarms on meetings, speaker-change accuracy, segment "
            "purity, generalization or upstream parity."
        ),
    }


# ---------------------------------------------------------------------------
# Adverse, missing, invalid and non-finite rejection controls.
# ---------------------------------------------------------------------------

def _expect_reject(case: str, action: Any) -> Dict[str, str]:
    try:
        action()
    except Reject as error:
        return {"case": case, "result": "rejected", "reason": str(error)}
    raise Reject("adverse case was accepted: " + case)


def _base_manifest() -> Dict[str, Any]:
    return {
        "adapter_config_path": "/approved/bic/adapter.json",
        "adapter_config_sha256": "1" * 64,
        "benchmark_record_path": "/approved/bic/benchmark.json",
        "benchmark_record_sha256": "2" * 64,
        "build_record_path": "/approved/bic/build.json",
        "build_record_sha256": "3" * 64,
        "channels": 1,
        "claimed_bic_segmentation_capability": True,
        "corpus_manifest_path": "/approved/bic/corpus.json",
        "corpus_manifest_sha256": "4" * 64,
        "feature_dim": 2,
        "frame_samples": 160,
        "hop_frames": 1,
        "license_record_path": "/approved/bic/license.json",
        "license_record_sha256": "5" * 64,
        "lookahead_frames": 15,
        "min_segment_frames": 15,
        "parity_vector_path": "/approved/bic/parity.json",
        "parity_vector_sha256": "6" * 64,
        "penalty_weight": "1",
        "rights_record_path": "/approved/bic/rights.json",
        "rights_record_sha256": "7" * 64,
        "runtime_lock_path": "/approved/bic/requirements.lock",
        "runtime_lock_sha256": "8" * 64,
        "runtime_path": "/approved/bic/runtime",
        "sample_rate_hz": 16000,
        "source_checkout_path": "/approved/bic/source",
        "source_manifest_path": "/approved/bic/source.sha256",
        "source_manifest_sha256": "9" * 64,
        "source_revision": "a" * 40,
        "threshold": "0",
        "variant": REQUIRED_VARIANT,
        "window_frames": 15,
    }


def _validate_absolute_path(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise Reject(field + " is not a nonempty string")
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts:
        raise Reject(field + " must be an absolute path without traversal")
    return value


def _validate_manifest_int(
    value: Any, field: str, minimum: int, maximum: int
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject(field + " is not an integer")
    if value < minimum or value > maximum:
        raise Reject(field + " is outside the admitted range")
    return value


def validate_caller_asset_manifest(manifest: Any) -> Dict[str, Any]:
    """Structurally validate a caller-supplied manifest, never qualify it."""
    if not isinstance(manifest, Mapping):
        raise Reject("manifest must be an object")
    missing = sorted(set(MANIFEST_FIELDS) - set(manifest))
    if missing:
        raise Reject("manifest missing fields: " + ",".join(missing))
    extra = sorted(set(manifest) - set(MANIFEST_FIELDS))
    if extra:
        raise Reject("manifest has unknown fields: " + ",".join(extra))
    normalized: Dict[str, Any] = {}
    for field in MANIFEST_PATH_FIELDS:
        normalized[field] = _validate_absolute_path(manifest[field], field)
    for field in MANIFEST_SHA_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
            raise Reject(field + " is not a lowercase SHA-256")
        normalized[field] = value
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not COMMIT_PATTERN.fullmatch(revision):
        raise Reject("source_revision must be a full 40-hex commit")
    if revision == "0" * 40:
        raise Reject("source_revision must be nonzero")
    normalized["source_revision"] = revision
    if manifest["variant"] != REQUIRED_VARIANT:
        raise Reject("variant must be " + REQUIRED_VARIANT)
    normalized["variant"] = REQUIRED_VARIANT
    if manifest["claimed_bic_segmentation_capability"] is not True:
        raise Reject("manifest must claim the BIC segmentation capability")
    normalized["claimed_bic_segmentation_capability"] = True
    for field, minimum, maximum in (
        ("channels", 1, 8),
        ("feature_dim", 1, MAX_FEATURE_DIM),
        ("frame_samples", SDK_FRAME_SAMPLES, SDK_FRAME_SAMPLES),
        ("hop_frames", 1, MAX_WINDOW_FRAMES),
        ("lookahead_frames", 0, MAX_WINDOW_FRAMES),
        ("min_segment_frames", 2, MAX_WINDOW_FRAMES),
        ("sample_rate_hz", CONTROL_SAMPLE_RATE_HZ, CONTROL_SAMPLE_RATE_HZ),
        ("window_frames", 2, MAX_WINDOW_FRAMES),
    ):
        normalized[field] = _validate_manifest_int(
            manifest[field], field, minimum, maximum
        )
    if normalized["channels"] != 1:
        raise Reject("channels must be 1 for the v0 boundary")
    if normalized["min_segment_frames"] < normalized["window_frames"]:
        raise Reject("min_segment_frames must be at least window_frames")
    if normalized["lookahead_frames"] < normalized["window_frames"]:
        raise Reject("lookahead_frames must be at least window_frames")
    penalty = manifest["penalty_weight"]
    if not isinstance(penalty, str) or not CANONICAL_DECIMAL.fullmatch(penalty):
        raise Reject("penalty_weight is not a canonical decimal string")
    penalty_value = Fraction(penalty)
    if penalty_value <= 0:
        raise Reject("penalty_weight must be positive")
    normalized["penalty_weight"] = penalty
    threshold = manifest["threshold"]
    if not isinstance(threshold, str) or not CANONICAL_DECIMAL.fullmatch(
        threshold
    ):
        raise Reject("threshold is not a canonical decimal string")
    normalized["threshold"] = threshold
    return {
        "accepted": True,
        "qualification": QUALIFICATION,
        "reason": (
            "structural manifest validation is not qualification; no exact "
            "runtime, rights review, corpus, parity result or benchmark is "
            "supplied by this package"
        ),
        "normalized": normalized,
    }


def qualification_gate(manifest: Any = None) -> Dict[str, Any]:
    if manifest is None:
        return {
            "qualifies": False,
            "qualification": QUALIFICATION,
            "reason": "no approved caller manifest, runtime, rights record, corpus or parity vector is supplied",
        }
    try:
        validated = validate_caller_asset_manifest(manifest)
    except Reject as error:
        return {
            "qualifies": False,
            "qualification": QUALIFICATION,
            "reason": "manifest rejected: " + str(error),
        }
    return {
        "qualifies": False,
        "qualification": QUALIFICATION,
        "reason": validated["reason"],
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    base = _base_manifest()
    singular = tuple((Fraction(0), Fraction(0)) for _ in range(40))
    cases = [
        _expect_reject(
            "feature_stream_empty",
            lambda: detect_change_points([]),
        ),
        _expect_reject(
            "feature_stream_not_sequence",
            lambda: detect_change_points("not-a-stream"),
        ),
        _expect_reject(
            "feature_stream_none",
            lambda: detect_change_points(None),
        ),
        _expect_reject(
            "feature_frame_not_sequence",
            lambda: detect_change_points([1, 2, 3]),
        ),
        _expect_reject(
            "feature_wrong_dimension",
            lambda: detect_change_points([(0, 0, 0)] * 40, feature_dim=2),
        ),
        _expect_reject(
            "feature_nan",
            lambda: detect_change_points([(0.0, float("nan"))] * 40),
        ),
        _expect_reject(
            "feature_pos_inf",
            lambda: detect_change_points([(0.0, float("inf"))] * 40),
        ),
        _expect_reject(
            "feature_neg_inf",
            lambda: detect_change_points([(0.0, float("-inf"))] * 40),
        ),
        _expect_reject(
            "feature_bool",
            lambda: detect_change_points([(True, 0)] * 40),
        ),
        _expect_reject(
            "feature_string",
            lambda: detect_change_points([("0", 0)] * 40),
        ),
        _expect_reject(
            "feature_out_of_range",
            lambda: detect_change_points([(10 ** 9, 0)] * 40),
        ),
        _expect_reject(
            "singular_covariance",
            lambda: detect_change_points(singular),
        ),
        _expect_reject(
            "window_too_short",
            lambda: detect_change_points(
                synthetic_feature_stream(), window_frames=1
            ),
        ),
        _expect_reject(
            "window_not_integer",
            lambda: detect_change_points(
                synthetic_feature_stream(), window_frames=15.5
            ),
        ),
        _expect_reject(
            "hop_zero",
            lambda: detect_change_points(
                synthetic_feature_stream(), hop_frames=0
            ),
        ),
        _expect_reject(
            "min_segment_below_window",
            lambda: detect_change_points(
                synthetic_feature_stream(),
                window_frames=20,
                min_segment_frames=10,
            ),
        ),
        _expect_reject(
            "stream_too_short_for_geometry",
            lambda: detect_change_points(
                synthetic_feature_stream()[:20]
            ),
        ),
        _expect_reject(
            "negative_penalty",
            lambda: detect_change_points(
                synthetic_feature_stream(), penalty_weight=-1
            ),
        ),
        _expect_reject(
            "nonfinite_penalty",
            lambda: detect_change_points(
                synthetic_feature_stream(), penalty_weight=float("inf")
            ),
        ),
        _expect_reject(
            "nonfinite_threshold",
            lambda: detect_change_points(
                synthetic_feature_stream(), threshold=float("nan")
            ),
        ),
        _expect_reject(
            "manifest_not_object",
            lambda: validate_caller_asset_manifest([]),
        ),
        _expect_reject(
            "manifest_missing_field",
            lambda: validate_caller_asset_manifest(
                {key: value for key, value in base.items()
                 if key != "build_record_sha256"}
            ),
        ),
        _expect_reject(
            "manifest_extra_field",
            lambda: validate_caller_asset_manifest(
                dict(base, extra_field="value")
            ),
        ),
        _expect_reject(
            "manifest_relative_path",
            lambda: validate_caller_asset_manifest(
                dict(base, source_checkout_path="relative/path")
            ),
        ),
        _expect_reject(
            "manifest_bad_sha",
            lambda: validate_caller_asset_manifest(
                dict(base, build_record_sha256="not-a-digest")
            ),
        ),
        _expect_reject(
            "manifest_short_revision",
            lambda: validate_caller_asset_manifest(
                dict(base, source_revision="a" * 12)
            ),
        ),
        _expect_reject(
            "manifest_nonhex_revision",
            lambda: validate_caller_asset_manifest(
                dict(base, source_revision="z" * 40)
            ),
        ),
        _expect_reject(
            "manifest_wrong_variant",
            lambda: validate_caller_asset_manifest(
                dict(base, variant="generic_segmenter")
            ),
        ),
        _expect_reject(
            "manifest_capability_false",
            lambda: validate_caller_asset_manifest(
                dict(base, claimed_bic_segmentation_capability=False)
            ),
        ),
        _expect_reject(
            "manifest_wrong_channels",
            lambda: validate_caller_asset_manifest(
                dict(base, channels=2)
            ),
        ),
        _expect_reject(
            "manifest_wrong_sample_rate",
            lambda: validate_caller_asset_manifest(
                dict(base, sample_rate_hz=8000)
            ),
        ),
        _expect_reject(
            "manifest_wrong_frame_samples",
            lambda: validate_caller_asset_manifest(
                dict(base, frame_samples=320)
            ),
        ),
        _expect_reject(
            "manifest_window_not_integer",
            lambda: validate_caller_asset_manifest(
                dict(base, window_frames=15.5)
            ),
        ),
        _expect_reject(
            "manifest_negative_min_segment",
            lambda: validate_caller_asset_manifest(
                dict(base, min_segment_frames=-1)
            ),
        ),
        _expect_reject(
            "manifest_penalty_exponent",
            lambda: validate_caller_asset_manifest(
                dict(base, penalty_weight="1e0")
            ),
        ),
        _expect_reject(
            "manifest_penalty_zero",
            lambda: validate_caller_asset_manifest(
                dict(base, penalty_weight="0")
            ),
        ),
        _expect_reject(
            "manifest_threshold_exponent",
            lambda: validate_caller_asset_manifest(
                dict(base, threshold="0e0")
            ),
        ),
        _expect_reject(
            "json_duplicate_key",
            lambda: strict_loads('{"a":1,"a":2}'),
        ),
        _expect_reject(
            "json_nan",
            lambda: strict_loads('{"a":NaN}'),
        ),
        _expect_reject(
            "json_infinity",
            lambda: strict_loads('{"a":Infinity}'),
        ),
    ]
    return cases


# ---------------------------------------------------------------------------
# Report construction.
# ---------------------------------------------------------------------------

def _gate_rows() -> List[Dict[str, Any]]:
    return [
        {
            "id": gate_id,
            "requirement": requirement,
            "status": "blocked",
            "blocked": True,
        }
        for gate_id, requirement in GATE_REQUIREMENTS
    ]


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "requirements": [
            {
                "id": "geometry_layout_and_timestamp_calibration",
                "requirement": "Record geometry, layout, timestamp calibration, source/target/reference conditions and permissions.",
                "measured": False,
                "reason": "no microphone array, meeting layout, annotation clock, RTTM/UEM reference or permission record is staged.",
            },
            {
                "id": "task_matched_heldout_labels",
                "requirement": "Compare segmentation with task-matched held-out speaker-change labels.",
                "measured": False,
                "reason": "no annotated-meeting speaker-change labels or frozen held-out split exists.",
            },
            {
                "id": "boundary_and_false_alarm_scoring",
                "requirement": "Score speaker-change boundaries and false alarms on annotated meetings.",
                "measured": False,
                "reason": "candidate_metrics are null; the synthetic planted-boundary check is not a meeting result.",
            },
            {
                "id": "leakage_target_damage_and_channel_loss",
                "requirement": "Report leakage, target damage and channel loss where the spatial task requires them.",
                "measured": False,
                "reason": "BIC change points do not separate or alter a target channel; no target-damage or channel-loss measurement is applicable without real audio and a declared task.",
            },
            {
                "id": "room_and_reference_condition_changes",
                "requirement": "Report changes in room/reference conditions.",
                "measured": False,
                "reason": "no room, session, channel or reference-condition cohort is staged.",
            },
            {
                "id": "segment_purity",
                "requirement": "Report locally homogeneous segment purity against reference speaker segments.",
                "measured": False,
                "reason": "no speaker segment labels or purity scorer exists.",
            },
            {
                "id": "availability_and_device_timing",
                "requirement": "Report content delay, availability and device timing for the exact runtime.",
                "measured": False,
                "reason": "the offline reference is not a deployed runtime; no device timing was run.",
            },
        ],
        "spatial_scope_note": (
            "The inventory assigns the spatial profile to this speaker-analysis "
            "row. Single-channel BIC change detection has no array geometry, "
            "but the profile still requires explicit geometry/clock/permission "
            "records and task-matched held-out labels; those are absent."
        ),
    }


def _candidate_metrics() -> Dict[str, Any]:
    return {
        "boundary_precision": {
            "value": None,
            "measured": False,
            "reason": "no annotated-meeting change-point truth",
        },
        "boundary_recall": {
            "value": None,
            "measured": False,
            "reason": "no annotated-meeting change-point truth",
        },
        "false_alarm_rate": {
            "value": None,
            "measured": False,
            "reason": "no annotated-meeting scored regions",
        },
        "miss_rate": {
            "value": None,
            "measured": False,
            "reason": "no annotated-meeting scored regions",
        },
        "boundary_deviation_ms": {
            "value": None,
            "measured": False,
            "reason": "no reference boundary timestamps or collar policy",
        },
        "segment_purity": {
            "value": None,
            "measured": False,
            "reason": "no reference speaker segments",
        },
        "derived_from_synthetic_control": False,
        "note": (
            "Every candidate metric is null. Synthetic planted-boundary "
            "matches are reported separately and are excluded from these rows."
        ),
    }


def _merged_sibling_evidence() -> Dict[str, Any]:
    return {
        "packages": [
            {
                "task": "SDK-SURVEY-SPK-03",
                "path": "docs/task-evidence/survey-spk-03/README.md",
                "finding": "The merged speaker-change evidence map records the BIC row as considered only, with no BIC implementation, configuration, annotated change-point cohort or boundary score.",
                "attributed_to_this_task": False,
            },
            {
                "task": "SDK-SURVEY-SPK-04",
                "path": "docs/task-evidence/survey-spk-04/README.md",
                "finding": "The merged diarization evidence map records BIC segmentation as considered only and does not produce anonymous speaker labels or a DER/JER result.",
                "attributed_to_this_task": False,
            },
            {
                "task": "SDK-SURVEY-DET-01",
                "path": "docs/task-evidence/survey-det-01/README.md",
                "finding": "Adjacent any-speech VAD evidence exists, but activity boundaries are not speaker-change boundaries.",
                "attributed_to_this_task": False,
            },
            {
                "task": "SDK-ADAPTIVE-ENERGY-VAD",
                "path": "docs/task-evidence/adaptive-energy-vad/README.md",
                "finding": "An adjacent energy VAD reference exists, but it does not emit speaker-change points or segments.",
                "attributed_to_this_task": False,
            },
            {
                "task": "SDK-WEBRTC-VAD",
                "path": "docs/task-evidence/webrtc-vad/README.md",
                "finding": "An adjacent VAD implementation exists, but any-speech decisions are not speaker-change truth.",
                "attributed_to_this_task": False,
            },
        ],
        "adjacent_any_speech_history_present": True,
        "speaker_change_execution_present": False,
        "bic_execution_present": False,
        "diarization_execution_present": False,
        "not_pooled": True,
        "note": (
            "Merged sibling packages establish only adjacent context. None is "
            "a BIC segmentation result and none is attributed to this task."
        ),
    }


def _build_report() -> Dict[str, Any]:
    verify_document_pins()
    identity = task_row_identity()
    inventory = _check_inventory_and_registry()
    probes = probe_absence()
    _assert_absent(probes)
    assets = _audit_assets()
    control = synthetic_control()
    adverse = run_adverse_controls()
    if control["detected_boundaries"] != list(CONTROL_PLANTED_BOUNDARIES):
        raise Reject("synthetic control did not detect the planted boundaries")
    if control["false_alarms"] or control["misses"]:
        raise Reject("synthetic control false alarm or miss changed")
    if control["negative_control"]["result"] != "no_change":
        raise Reject("synthetic negative control changed")
    if control["singular_control"]["result"] != "rejected":
        raise Reject("singular control was not rejected")
    if any(row["result"] != "rejected" for row in adverse):
        raise Reject("an adverse control was accepted")
    if qualification_gate(_base_manifest())["qualifies"] is not False:
        raise Reject("structural manifest validation qualified the candidate")

    report: Dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "category_id": CATEGORY_ID,
        "profile": PROFILE,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "evidence_status": EVIDENCE_STATUS,
        "status": STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION,
        "proposal_only": True,
        "defer_before": DEFER_BEFORE,
        "generated_by": "reference.py",
        "task_row_identity": identity,
        "inventory_record": inventory,
        "format": {
            "control_mode": "offline_feature_domain_bic_accounting",
            "control_sample_format": "exact rational feature vectors",
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CONTROL_CHANNELS,
            "control_feature_dim": CONTROL_FEATURE_DIM,
            "control_frame_hop_samples": CONTROL_FRAME_HOP_SAMPLES,
            "control_window_frames": CONTROL_WINDOW_FRAMES,
            "control_hop_frames": CONTROL_HOP_FRAMES,
            "control_lookahead_frames": CONTROL_LOOKAHEAD_FRAMES,
            "control_lookahead_samples": CONTROL_LOOKAHEAD_SAMPLES,
            "control_lookahead_ms": score_text(
                Decimal(CONTROL_LOOKAHEAD_MS.numerator)
                / Decimal(CONTROL_LOOKAHEAD_MS.denominator)
            ),
            "control_min_segment_frames": CONTROL_MIN_SEGMENT_FRAMES,
            "control_penalty_weight": score_text(Decimal(
                CONTROL_PENALTY_WEIGHT.numerator)
                / Decimal(CONTROL_PENALTY_WEIGHT.denominator)),
            "control_threshold": score_text(Decimal(
                CONTROL_THRESHOLD.numerator)
                / Decimal(CONTROL_THRESHOLD.denominator)),
            "control_causal": False,
            "control_incremental_streaming": False,
            "control_performs_audio_segmentation": False,
            "control_performs_speaker_labelling": False,
            "control_extracts_audio_features": False,
            "sdk_v0_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "sdk_v0_channels": CONTROL_CHANNELS,
            "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
            "sdk_v0_sample_format": "f32",
            "sdk_v0_geometry_preserved": True,
            "task_geometry_asserted": False,
            "task_geometry_status": "unestablished",
        },
        "task_geometry": {
            "status": "unestablished",
            "upstream_feature_front_end": None,
            "upstream_window_frames": None,
            "upstream_hop_frames": None,
            "upstream_lookahead_frames": None,
            "upstream_penalty_weight": None,
            "upstream_threshold": None,
            "upstream_min_segment_frames": None,
            "upstream_merge_policy": None,
            "annotation_schema": None,
            "availability_policy": None,
            "control_geometry": {
                "feature_front_end": "caller-supplied deterministic 2-D vectors",
                "window_frames": CONTROL_WINDOW_FRAMES,
                "hop_frames": CONTROL_HOP_FRAMES,
                "lookahead_frames": CONTROL_LOOKAHEAD_FRAMES,
                "penalty_weight": "1",
                "threshold": "0",
                "min_segment_frames": CONTROL_MIN_SEGMENT_FRAMES,
                "merge_policy": BIC_SELECTION_POLICY,
                "annotation_schema": "half-open frame and sample intervals",
                "causal": False,
            },
            "note": (
                "The control geometry is declared for reproducibility only. "
                "The real component's feature front end, window/hop/lookahead, "
                "penalty, threshold, segment merge and annotation schema are "
                "not established."
            ),
        },
        "upstream_identity": {
            "name": "Bayesian information criterion speaker segmentation (S04 method lead)",
            "recorded_source_id": SOURCE_ID,
            "project_url": (
                "https://www.isca-archive.org/icslp_2002/"
                "sivakumaran02_icslp.html"
            ),
            "repository_url": None,
            "revision": None,
            "release_or_tag": None,
            "revision_pin_available": False,
            "source_checkout_present": False,
            "implementation_present": False,
            "runtime_present": False,
            "recorded_license": None,
            "license_verified": False,
            "note": (
                "The merged registry supplies a paper title and URL only. It "
                "supplies no code repository, commit, release, artifact "
                "digest, licence grant or build record."
            ),
        },
        "source_lead": {
            "source_id": SOURCE_ID,
            "title": "Speaker segmentation using the Bayesian information criterion",
            "url": (
                "https://www.isca-archive.org/icslp_2002/"
                "sivakumaran02_icslp.html"
            ),
            "recorded_use": "method lead only",
            "implementation_acquired": False,
            "revision_pinned": False,
            "license_grant_verified": False,
            "local_output_present": False,
        },
        "bic_reference": {
            "formula_id": BIC_FORMULA_ID,
            "implementation_origin": "task-local reference arithmetic, not an upstream implementation",
            "formula": (
                "D = N*ln|Sigma_pooled| - N1*ln|Sigma_left| - "
                "N2*ln|Sigma_right| - lambda*0.5*(d + d*(d+1)/2)*ln(N)"
            ),
            "sign_convention": "D > threshold favours a change point",
            "covariance": "population covariance with denominator N",
            "penalty_weight": "1",
            "threshold": "0",
            "selection_policy": BIC_SELECTION_POLICY,
            "upstream_parity_target": None,
            "qualifies_candidate": False,
            "note": (
                "This is a declared classical adjacent-window BIC comparison "
                "with a deterministic non-maximum-suppression policy. It is "
                "not copied from, checked against or represented as any "
                "specific upstream implementation."
            ),
        },
        "synthetic_control": control,
        "candidate_metrics": _candidate_metrics(),
        "matched_evidence": {
            "present": False,
            "annotated_meetings": 0,
            "speaker_change_labels": 0,
            "scored_regions": 0,
            "held_out_split": None,
            "collar_policy": None,
            "rights_record": None,
            "reason": "no rights-cleared annotated-meeting speaker-change corpus is staged",
        },
        "merged_sibling_evidence": _merged_sibling_evidence(),
        "acceptance_profile": _acceptance_profile(),
        "asset_requirements": [dict(row) for row in ASSET_REQUIREMENTS],
        "asset_audit": assets,
        "missing_historical_artifacts": [
            "research/repos/bic-speaker-segmentation",
            "data/envs/bic-speaker-segmentation",
            "data/envs/bic-speaker-segmentation/requirements.lock",
            "data/build-records/bic-speaker-segmentation.json",
            "data/rights/bic-speaker-segmentation-license.json",
            "data/rights/bic-speaker-segmentation-rights.json",
            "data/annotations/speaker-change-ami/manifest.json",
            "data/plans/bic-speaker-segmentation-adapter.json",
            "data/runs/bic-speaker-change-parity/manifest.json",
            "data/runs/bic-speaker-change-cohort/manifest.json",
        ],
        "controls": {
            "adverse": adverse,
            "adverse_case_count": len(adverse),
            "all_adverse_rejected": True,
            "absence_probes": probes,
            "absence_probes_all_absent": True,
            "structural_manifest_validation_is_not_qualification": True,
            "qualification_gate_without_manifest": qualification_gate(),
        },
        "qualification": {
            "decision": DECISION,
            "status": QUALIFICATION,
            "qualification_status": QUALIFICATION,
            "evidence_status": EVIDENCE_STATUS,
            "candidate_qualified": False,
            "proposal_only": True,
            "defer_before": DEFER_BEFORE,
            "implementation_present": False,
            "runtime_invoked": False,
            "parity_present": False,
            "corpus_present": False,
            "benchmark_present": False,
            "release_qualification_present": False,
            "no_missing_result_qualifies_candidate": True,
            "synthetic_control_is_not_candidate_evidence": True,
            "reason": (
                "No approved BIC implementation, source revision, runtime, "
                "licence/rights record, annotated-meeting change corpus, "
                "exact-parity vector, task geometry or benchmark exists. The "
                "synthetic feature-domain control does not qualify the row."
            ),
        },
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "gates": _gate_rows(),
        "exact_blockers": [dict(row) for row in EXACT_BLOCKERS],
        "reopen_conditions": [
            {"gate_id": gate_id, "condition": requirement}
            for gate_id, requirement in GATE_REQUIREMENTS
        ],
        "non_claims": list(NON_CLAIMS),
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, allow_nan=False, trailing newline",
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
            "report_json_sha256_sidecar": "report.json.sha256",
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "mutable_provenance": {
            "gate": False,
            "path": BOARD_PATH,
            "note": (
                "Board status is mutable and the full file is never hashed. "
                "Only stable linked-row identity is gated in task_row_identity; "
                "status/owner/review/handoff changes cannot alter report bytes."
            ),
        },
        "reproduction": {
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py",
            "all": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            "compare": "exact SHA-256 over canonical JSON; no tolerance; three byte-identical cold-start repeats",
        },
    }

    return _finalize_report(report)


def _finalize_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """Fail closed on any weakened gate or overclaiming field."""
    if report["decision"] != DECISION:
        raise Reject("decision changed")
    if report["qualification_status"] != QUALIFICATION:
        raise Reject("qualification changed")
    if report["status"] != STATUS:
        raise Reject("status changed")
    if report["qualification"]["status"] != QUALIFICATION:
        raise Reject("nested qualification changed")
    if report["qualification"]["candidate_qualified"] is not False:
        raise Reject("candidate qualification claimed")
    if report["qualification"]["no_missing_result_qualifies_candidate"] is not True:
        raise Reject("missing-result rule changed")
    if len(report["gates"]) != 8:
        raise Reject("release gate count changed")
    if any(gate["blocked"] is not True for gate in report["gates"]):
        raise Reject("a release gate is not blocked")
    if any(value is not False for value in report["boundary"].values()):
        raise Reject("boundary is not closed")
    for flag in SCOPE_FALSE_FLAGS:
        if report["scope"][flag] is not False:
            raise Reject("scope claim is not closed: " + flag)
    for flag in SCOPE_TRUE_FLAGS:
        if report["scope"][flag] is not True:
            raise Reject("scope rule is not enforced: " + flag)
    if report["candidate_metrics"]["derived_from_synthetic_control"] is not False:
        raise Reject("synthetic control was promoted to candidate metrics")
    for name in (
        "boundary_precision",
        "boundary_recall",
        "false_alarm_rate",
        "miss_rate",
        "boundary_deviation_ms",
        "segment_purity",
    ):
        row = report["candidate_metrics"][name]
        if row["value"] is not None or row["measured"] is not False:
            raise Reject("candidate metric is not null: " + name)
    if report["synthetic_control"]["qualifies_candidate"] is not False:
        raise Reject("synthetic control qualified the candidate")
    if report["synthetic_control"]["not_audio"] is not True:
        raise Reject("synthetic control is represented as audio")
    if report["synthetic_control"]["not_speaker_evidence"] is not True:
        raise Reject("synthetic control is represented as speaker evidence")
    if report["merged_sibling_evidence"]["speaker_change_execution_present"] is not False:
        raise Reject("a sibling speaker-change execution is claimed")
    if BOARD_PATH in report["source_pins"]:
        raise Reject("mutable board file is pinned")
    if BOARD_PATH in report["boundary_pins"]:
        raise Reject("mutable board file is pinned as boundary")
    canonical_bytes(report)
    return report


class EvidenceReport:
    """Atomic holder; rejected input never changes the committed state."""

    def __init__(self) -> None:
        self.state: Optional[Dict[str, Any]] = None

    def snapshot(self) -> Optional[Dict[str, Any]]:
        return copy.deepcopy(self.state)

    def build(
        self,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if payload is not None:
            if not isinstance(payload, Mapping):
                raise Reject("payload must be a mapping")
            for key, value in payload.items():
                if not isinstance(key, str):
                    raise Reject("payload key must be a string")
                if not isinstance(value, (str, int, float, bool, type(None))):
                    raise Reject("invalid payload entry: " + key)
                if isinstance(value, float) and not math.isfinite(value):
                    raise Reject("nonfinite payload value: " + key)
                if isinstance(value, int) and not isinstance(value, bool):
                    if abs(value) > 2 ** 53 - 1:
                        raise Reject("payload integer is outside the exact range: " + key)
        candidate = _build_report()
        self.state = candidate
        return candidate


def build_report() -> Dict[str, Any]:
    """Return a fresh canonical report without mutating module state."""
    return _build_report()
