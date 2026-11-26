# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for SDK-NEURAL-KALMAN-FILTERING-NKF.

This module is NOT a Neural Kalman filtering (NKF) implementation. It contains
no echo-path model, learned adaptation controller, covariance or gain update,
checkpoint loader, training code, streaming harness or inference path. A
bounded, read-only search finds no exact NKF source revision, no trained
checkpoint, no model card or parameter set, no paired far-end/microphone room
fixture and no hash-pinned runtime in the workspace. The module therefore
builds a fail-closed readiness report:

* strict request validation for a caller-supplied NKF bundle;
* explicit source, model, checkpoint, fixture, runtime and rights probes;
* an admission gate that defers every structurally valid bundle because the
  required external artifacts are absent;
* synthetic harness stimuli for rejection/characterisation controls only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

Nothing is downloaded, cloned, installed, reconstructed, trained, fitted or
simulated as a candidate. No candidate audio output is produced. No result
qualifies the catalogued ``neural-kalman-filtering-nkf`` component.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import struct
import subprocess
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/neural-kalman-filtering-nkf/"

TASK = "SDK-NEURAL-KALMAN-FILTERING-NKF"
TITLE = "Neural Kalman filtering (NKF)"
COMPONENT = "neural-kalman-filtering-nkf"
COMPONENT_ID = "neural-kalman-filtering-nkf"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "room"
PROFILE_KEY = "Room"
STATUS = "proposal_only_not_qualified"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
QUALIFICATION_STATUS = "not_qualified"
FORMAT = "sdk-task-evidence/0.1"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/neural-kalman-filtering-nkf-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/neural-kalman-filtering-nkf-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/neural-kalman-filtering-nkf-report/0.1"
BASE_COMMIT = "9074704819a6af4168f8c9cf3bbe8da50484c29a"
BRANCH = "swarm/SDK-NEURAL-KALMAN-FILTERING-NKF"
CLAIM_WORKTREE = ("/Users/htsakanyan/workspace/audio/audioml/worktrees/"
                  "audio-sdk/SDK-NEURAL-KALMAN-FILTERING-NKF")
REVIEWER = "reviewer-NEURAL-KALMAN-FILTERING-NKF"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

# ---------------------------------------------------------------------------
# Stable, read-only pins. Source paths are relative to SOURCE_ROOT; SDK paths
# are worktree relative. Nothing here is executed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
    "research/aec_research_20261028.md":
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180",
    "research/feedback_control_20261028.md":
        "47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c",
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
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

# Only stable, non-mutable identity fields are projected. status, owner,
# claim, review, handoff, blocked_reason and dispatch_priority never enter
# canonical bytes and never gate this package.
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
STABLE_TASK_FIELDS = ("id", "title", "component", "mode", "repository",
                      "depends_on")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "evidence", "deliverable", "acceptance",
    "write_scope",
)
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
INVENTORY_REL = "audio-benchmark-platform/plan/INVENTORY.json"
PROFILE_PHRASES = (
    "Freeze render/reference or measured RIRs",
    "channel/rate/hop",
    "excitation, delay, movement, noise and reset schedule",
    "echo-only, near-end-only, overlap and no-reference cases",
    "echo attenuation, near-end damage, nonfinite failures and alignments",
    "delayed/missing render",
    "no-reference suppressor gets its own independent comparison",
)
PLAN_NOTE = ("Pin the model and compare reset, reconvergence, double-talk and "
             "reference timing.")

GATE_IDS = tuple("RG-%02d" % index for index in range(1, 9))
ARTIFACT_IDS = tuple("ART-%02d" % index for index in range(1, 8))
BLOCKER_IDS = tuple("BLK-%02d" % index for index in range(1, 7))
ROOM_ITEM_IDS = tuple("ROOM-%02d" % index for index in range(1, 10))

# Installed public v0 baseline. This is the unchanged SDK format, not an NKF
# geometry and not a model frame or hop.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
ABI_MAJOR = 0
ABI_MINOR = 1

SCOPE_BASE_REFS = ("origin/main", "main")
NON_CLAIMS = [
    "No Neural Kalman filtering implementation, echo-path model, learned "
    "adaptation controller, covariance or gain update is present or evaluated.",
    "No exact upstream NKF source revision, license, entry point or per-file "
    "digest is admitted.",
    "No trained checkpoint, weight file, model card, training metadata or "
    "parameter count is present, opened or loaded.",
    "No authoritative sample rate, frame, hop, STFT size, state dimension, "
    "network structure, delay alignment, precision or reset policy is declared.",
    "No paired far-end/microphone room fixture, measured RIR, render set, "
    "movement segment, noise condition or held-out split is present.",
    "No reset, reconvergence, double-talk, reference-timing, echo-attenuation "
    "or near-end-preservation value is measured.",
    "No real audio is opened, decoded, played or listened to, and no device, "
    "callback, wall-clock or target timing is measured.",
    "No provider, descriptor, registry, default, public API/ABI, "
    "CONTRACTS.md, shared build or CI change exists.",
    "No benchmark, product, release or qualification claim is made.",
]

REQUIRED_ARTIFACTS_SPEC = (
    ("ART-01", "exact_source_revision_and_license",
     "The exact NKF implementation at an immutable 40-hex commit, with the "
     "echo-path plus learned-adaptation entry point, reviewed upstream license "
     "text, per-file SHA-256 manifest, file count and tree digest."),
    ("ART-02", "exact_checkpoint_model_card_and_config",
     "The trained checkpoint bytes and SHA-256, byte count, model card, "
     "training-data provenance, architecture, STFT/frame/hop geometry, state "
     "dimension, parameter count, precision and reset/reconvergence policy, "
     "with a canonical model/config digest."),
    ("ART-03", "matched_room_fixture",
     "A rights-cleared fixture pairing the far-end playback reference with the "
     "microphone capture, or a frozen measured RIR/render set, including "
     "channel/rate/hop, excitation, delay, movement, noise, reset schedule and "
     "a held-out room/device split."),
    ("ART-04", "pinned_runtime_and_harness",
     "A hash-pinned inference runtime and streaming harness with "
     "install/import parity, a checkpoint loader, finite drain, reset and exact "
     "sample-rate/frame/hop geometry."),
    ("ART-05", "frozen_room_protocol",
     "A frozen protocol that measures reset, reconvergence, double-talk and "
     "reference timing on the exact pinned model, including echo-only, "
     "near-end-only, overlap, delayed-render and missing-render cases."),
    ("ART-06", "source_checkpoint_fixture_and_output_rights",
     "Reviewed source, checkpoint, training-data, corpus and derived-output "
     "rights, including redistribution scope and any participant or device "
     "terms."),
    ("ART-07", "room_result_bundle_and_review",
     "A complete room result bundle for the exact candidate plus an opt-in, "
     "default-off adapter decision and independent exact-head review."),
)

EXACT_BLOCKERS_SPEC = (
    ("BLK-01", "ART-01", ("RG-01",),
     "The pinned AEC census names the Neural Kalman filtering family in one "
     "row but records no NKF repository, 40-hex revision, license or per-file "
     "SHA-256 manifest. No local NKF source, checkout or entry point exists.",
     "Stage and pin the exact NKF source at a 40-hex commit with reviewed "
     "license text and a per-file SHA-256 manifest; do not reconstruct source "
     "from the paper description."),
    ("BLK-02", "ART-02", ("RG-02", "RG-05"),
     "No trained NKF checkpoint, weight file, model card, training metadata or "
     "exact architecture/parameter set is available. STFT size, hop, state "
     "dimension, network structure, learned control target, precision and "
     "reset/reconvergence policy are unrecorded, so no model digest exists.",
     "Stage the exact checkpoint with SHA-256 and byte count plus a model card "
     "and citable parameter/config set; never invent weights or a controller."),
    ("BLK-03", "ART-03", ("RG-03", "RG-06"),
     "No matched room fixture exists. The paired far-end reference and "
     "microphone capture, frozen render set or measured RIR, channel/rate/hop "
     "geometry, excitation, delay, movement, noise, reset schedule and "
     "held-out room/device split are absent, and the AEC-Challenge material is "
     "neither staged nor rights-cleared for this package.",
     "Supply a rights-cleared paired far-end/microphone room fixture with "
     "frozen RIR or render material, delay, movement, noise, reset schedule "
     "and held-out splits."),
    ("BLK-04", "ART-04", ("RG-05",),
     "No hash-pinned NKF runtime or streaming harness exists. There is no "
     "checkpoint loader, interpreter lock, framework version, import-parity "
     "vector or finite drain/reset path, and scripts/ci.py is the SDK CI, not "
     "an NKF runtime.",
     "Pin the runtime and harness with a lockfile, checkpoint loader, "
     "install/import parity and the exact installed geometry."),
    ("BLK-05", "ART-05", ("RG-06",),
     "The required measurements cannot be established: reset, reconvergence, "
     "double-talk and reference timing need a pinned model and a frozen room "
     "fixture. Synthetic analytic stimuli alone cannot measure echo "
     "attenuation, near-end damage, delayed/missing render or reset behavior.",
     "Run the frozen room protocol on the exact candidate and matched fixture "
     "with echo-only, near-end-only, overlap, delayed-render and "
     "missing-render controls."),
    ("BLK-06", "ART-06", ("RG-04", "RG-07", "RG-08"),
     "Rights and independent review are unrecorded. No source license, "
     "checkpoint or training-data terms, fixture corpus permission, "
     "output-use grant or exact-head review exists, and no real audio, "
     "listening, device timing, benchmark or release claim is permitted by "
     "this task.",
     "Record reviewed source, checkpoint, training-data, fixture and output "
     "rights; then open an opt-in adapter and independent exact-head review."),
)
BLOCKER_TOKENS = (
    "Neural Kalman filtering", "NKF", "source", "40-hex", "SHA-256",
    "checkpoint", "model card", "matched", "far-end", "microphone", "room",
    "delay", "double-talk", "reconvergence", "reset", "reference timing",
    "rights", "runtime", "review",
)

# Fixed-path probes. Existence checks only; no directory walk, no network, no
# audio decode and no package import.
SOURCE_PROBE_PATHS = (
    "src/audioml_eval/neural_kalman.py",
    "src/audioml_eval/nkf.py",
    "adapters/nkf/run.py",
    "adapters/neural-kalman/run.py",
    "scripts/evaluate_nkf.py",
    "reports/aec/nkf-room-screen.json",
    "data/checkouts/NKF",
    "data/checkouts/NeuralKalmanAHS",
    "data/checkouts/AHS_2023",
    "research/plans/neural-kalman-filtering",
    "data/fixtures/nkf-room",
)
FIXTURE_PROBE_PATHS = (
    "data/fixtures/nkf-room",
    "data/fixtures/neural-kalman-filtering-nkf",
    "data/tmp/nkf-room-pilot",
    "reports/aec/nkf-room-screen.json",
    "reports/aec/nkf-double-talk.json",
    "reports/aec/nkf-reference-timing.json",
)
RUNTIME_PROBE_PATHS = (
    "requirements-nkf.lock",
    "nkf-runtime.lock",
    "data/tmp/nkf-runtime",
    "build/nkf",
    "conformance/nkf",
)
CHECKPOINT_PROBE_PATHS = (
    "data/checkouts/NeuralKalmanAHS/checkpoints",
    "data/checkouts/AHS_2023/checkpoints",
    "data/tmp/nkf-weights",
    "models/nkf",
    "reports/aec/nkf-checkpoint",
    "data/tmp/neural-kalman-filtering-nkf",
)
LOCAL_MANIFEST_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
LOCAL_PIN_FILES = (
    "LICENSES.md",
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)

README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}


# ---------------------------------------------------------------------------
# Strict JSON and canonical bytes.
# ---------------------------------------------------------------------------


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise ValueError("nonfinite_json:" + token)


def assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed")
    if isinstance(value, dict):
        for item in value.values():
            assert_no_float(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_float(item)


def loads_strict(payload: str) -> dict:
    try:
        value = json.loads(payload, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def parse_strict_json_text(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("invalid_utf8") from error
    return loads_strict(text)


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))


# ---------------------------------------------------------------------------
# Stable board identity. The mutable board file is read, never pinned.
# ---------------------------------------------------------------------------


def _project(row: dict, require_component: bool = False) -> dict:
    required = ("id", "title", "mode", "repository", "depends_on")
    missing = [field for field in required if field not in row]
    if require_component and "component" not in row:
        missing.append("component")
    if missing:
        raise ValueError("board_row_missing_field:" + missing[0])
    depends_on = row.get("depends_on")
    if not isinstance(depends_on, list):
        raise ValueError("board_depends_on_not_list")
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "component": row.get("component"),
        "mode": row.get("mode"),
        "repository": row.get("repository"),
        "depends_on": list(depends_on),
    }


def _board_tasks(path: Path | None = None) -> list[dict]:
    board = SOURCE_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    document = read_strict_json(board)
    rows = document.get("tasks")
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
    return rows


def board_row_projection(path: Path | None = None) -> dict:
    matches = [row for row in _board_tasks(path)
               if isinstance(row, dict) and row.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    projection = _project(matches[0], require_component=True)
    if projection["component"] != COMPONENT_ID:
        raise ValueError("board_component_mismatch")
    if projection["mode"] != MODE:
        raise ValueError("board_mode_mismatch")
    if projection["repository"] != REPOSITORY:
        raise ValueError("board_repository_mismatch")
    return projection


def linked_rows(path: Path | None = None) -> tuple[dict, ...]:
    rows = _board_tasks(path)
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    root = by_id.get(TASK)
    if root is None:
        raise ValueError("board_row_absent")
    projection = _project(root, require_component=True)
    result = [projection]
    for dependency in projection["depends_on"]:
        row = by_id.get(dependency)
        if row is None:
            raise ValueError("linked_row_absent:" + dependency)
        result.append(_project(row))
    return tuple(result)


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows_digest(rows: tuple[dict, ...] | None = None) -> str:
    value = linked_rows() if rows is None else rows
    return object_digest([dict(row) for row in value])


def _gate_link() -> dict:
    return {
        "task_id": TASK,
        "title": TITLE,
        "mode": MODE,
        "repository": REPOSITORY,
        "component": COMPONENT_ID,
    }


# ---------------------------------------------------------------------------
# Read-only probes and profile source.
# ---------------------------------------------------------------------------


def _probe(relative_paths: Iterable[str]) -> tuple[list[str], list[str]]:
    checked: list[str] = []
    found: list[str] = []
    for relative in relative_paths:
        checked.append(relative)
        path = SOURCE_ROOT / relative
        if path.exists():
            found.append(relative)
    return checked, found


def profile_source() -> dict:
    path = SOURCE_ROOT / PROFILE_SOURCE_REL
    expected = SOURCE_PINS[PROFILE_SOURCE_REL]
    if not path.is_file():
        raise ValueError("profile_source_missing")
    if sha256_file(path) != expected:
        raise ValueError("profile_source_digest_changed")
    row = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Room |"):
            row = line.strip()
            break
    if row is None:
        raise ValueError("room_profile_row_missing")
    for phrase in PROFILE_PHRASES:
        if phrase not in row:
            raise ValueError("room_profile_phrase_missing:" + phrase)

    inventory_path = SOURCE_ROOT / INVENTORY_REL
    if sha256_file(inventory_path) != SOURCE_PINS[INVENTORY_REL]:
        raise ValueError("inventory_digest_changed")
    inventory = read_strict_json(inventory_path)
    components = inventory.get("components")
    if not isinstance(components, list):
        raise ValueError("inventory_components_not_list")
    matches = [row for row in components
               if isinstance(row, dict) and row.get("id") == COMPONENT_ID]
    if len(matches) != 1:
        raise ValueError("inventory_row_not_unique")
    component = matches[0]
    if component.get("verification_profile") != PROFILE:
        raise ValueError("inventory_profile_mismatch")
    if component.get("plan_note") != PLAN_NOTE:
        raise ValueError("inventory_plan_note_mismatch")
    return {
        "profile": PROFILE_KEY,
        "key": PROFILE,
        "row": row,
        "plan_note": PLAN_NOTE,
        "source_path": PROFILE_SOURCE_REL,
        "source_sha256": expected,
        "inventory_path": INVENTORY_REL,
        "inventory_component_id": COMPONENT_ID,
        "inventory_disposition": component.get("disposition"),
        "inventory_evidence_status": component.get("evidence_status"),
    }


def source_probe() -> dict:
    note = (SOURCE_ROOT / "research/aec_research_20261028.md")
    text = note.read_text(encoding="utf-8")
    feedback = (SOURCE_ROOT / "research/feedback_control_20261028.md").read_text(
        encoding="utf-8")
    checked, found = _probe(SOURCE_PROBE_PATHS)
    return {
        "status": "blocked_exact_source_absent",
        "family_listed_in_pinned_note": "Neural Kalman filter" in text,
        "pinned_note_repository": None,
        "pinned_note_revision": None,
        "local_implementation_present": False,
        "candidate_checkouts_present": False,
        "checked_paths": checked,
        "found": found,
        "entry_point": None,
        "license": None,
        "license_file_present": False,
        "tree_digest": None,
        "file_count": None,
        "present": False,
        "executed": False,
        "digest_asserted": False,
        "related_named_leads_not_admitted": [
            {
                "name": "YIXUANZ/NeuralKalmanAHS",
                "repository": "https://github.com/YIXUANZ/NeuralKalmanAHS",
                "recorded_in": "research/feedback_control_20261028.md",
                "status": "research_reference_demo_materials_only",
                "admitted_as_source": False,
            },
            {
                "name": "YIXUANZ/AHS_2023",
                "repository": "https://github.com/YIXUANZ/AHS_2023",
                "recorded_in": "research/feedback_control_20261028.md",
                "status": "research_reference_demo_materials_only",
                "admitted_as_source": False,
            },
        ],
        "related_leads_recorded": ("NeuralKalmanAHS" in feedback
                                   and "AHS_2023" in feedback),
        "candidate_identity_note":
            "The pinned task note names the Neural Kalman filtering family in "
            "one row only and identifies no repository for this row. The "
            "related public NeuralKalmanAHS/AHS_2023 repositories are recorded "
            "in the sibling pinned feedback note as demo materials without "
            "source or checkpoints; they are cited as related leads, not "
            "admitted as this row's source.",
        "note": "Read-only existence checks only; no clone, fetch, archive "
                "extraction or download. The pinned note names the family but "
                "no exact repository, revision, license, entry point or "
                "parameter set.",
    }


def parameter_probe() -> dict:
    return {
        "status": "blocked_model_architecture_and_config_absent",
        "algorithm_update_equations_present": False,
        "architecture_present": False,
        "config_digest": None,
        "sample_rate_hz": None,
        "frame_samples": None,
        "hop_samples": None,
        "stft_size": None,
        "window": None,
        "state_dimension": None,
        "network_structure": None,
        "layer_count": None,
        "parameter_count": None,
        "learned_control_target": None,
        "delay_alignment_samples": None,
        "numerical_precision": None,
        "reset_policy": None,
        "reconvergence_policy": None,
        "verified": False,
        "invented_here": False,
        "note": "The pinned census describes a classical echo-path model plus "
                "learned adaptation/gain control and records no exact update "
                "equations, geometry or constants. A self-authored structure "
                "would be a new unspecified algorithm, not the catalogued "
                "candidate, so none is substituted.",
    }


def checkpoint_probe() -> dict:
    checked, found = _probe(CHECKPOINT_PROBE_PATHS)
    return {
        "status": "blocked_model_checkpoint_absent",
        "family_requires_pretrained_weights": True,
        "named_candidate_checkpoint_present": False,
        "pinned_model_present": False,
        "admitted_model": None,
        "present_file_count": 0,
        "checked_paths": checked,
        "found": found,
        "sha256": None,
        "byte_count": None,
        "model_card_sha256": None,
        "training_metadata_present": False,
        "terms_recorded": False,
        "opened_or_loaded": False,
        "note": "The neural Kalman family needs a trained checkpoint. No weight "
                "file is staged, opened, loaded or downloaded, and local "
                "possession alone would not be treated as rights evidence.",
    }


def fixture_probe() -> dict:
    checked, found = _probe(FIXTURE_PROBE_PATHS)
    return {
        "status": "blocked_matched_room_fixture_absent",
        "matched_room_fixture_present": False,
        "measured_physical_room_present": False,
        "required_signals": ["far_end_reference", "microphone"],
        "sample_rate_hz": None,
        "channels": None,
        "frame_samples": None,
        "hop_samples": None,
        "render_or_rir_frozen": False,
        "delay_measured": False,
        "movement_measured": False,
        "noise_condition_frozen": False,
        "reset_schedule_frozen": False,
        "path_digest": None,
        "echo_only_case_present": False,
        "near_end_only_case_present": False,
        "overlap_case_present": False,
        "no_reference_case_present": False,
        "delayed_or_missing_render_case_present": False,
        "held_out_room_or_device_split": False,
        "rights_cleared": False,
        "checked_paths": checked,
        "found": found,
        "present": False,
        "read": False,
        "decoded": False,
        "note": "Existence checks only; no audio is opened or decoded. The "
                "AEC-Challenge material cited by the pinned note is not staged "
                "or rights-cleared here, and no measured room response or "
                "paired far-end/microphone fixture is present.",
    }


def runtime_probe() -> dict:
    checked, found = _probe(RUNTIME_PROBE_PATHS)
    return {
        "status": "blocked_pinned_runtime_absent",
        "pinned_runtime_present": False,
        "pinned_runtime_complete": False,
        "pinned_runtime_version_verified": False,
        "streaming_harness_present": False,
        "checkpoint_loader_present": False,
        "lockfile": None,
        "python_requirement": None,
        "sha256": None,
        "checked_paths": checked,
        "found": found,
        "imported_or_executed": False,
        "note": "No package is installed, imported or downloaded. The present "
                "SDK CI script is not an NKF runtime, and no streaming "
                "harness, checkpoint loader, lockfile or wheel set exists.",
    }


def rights_probe() -> dict:
    return {
        "status": "blocked_rights_unrecorded",
        "source_license": None,
        "source_license_file_present": False,
        "checkpoint_terms": None,
        "checkpoint_terms_recorded": False,
        "training_data_rights": False,
        "fixture_corpus_rights": False,
        "redistribution_scope": None,
        "output_use_cleared": False,
        "review": "blocked",
        "reviewed_by": None,
        "note": "No source license, checkpoint or training-data terms, fixture "
                "corpus permission or output-use grant is recorded locally. "
                "The AEC-Challenge material is cited as a research input with "
                "its own terms, not redistributed, staged or admitted here.",
    }


def absence_probes() -> dict:
    source_checked, source_found = _probe(SOURCE_PROBE_PATHS)
    fixture_checked, fixture_found = _probe(FIXTURE_PROBE_PATHS)
    runtime_checked, runtime_found = _probe(RUNTIME_PROBE_PATHS)
    checkpoint_checked, checkpoint_found = _probe(CHECKPOINT_PROBE_PATHS)
    found = sorted(set(source_found + fixture_found + runtime_found +
                       checkpoint_found))
    return {
        "method": "fixed_path_existence_only",
        "recursive_walk": False,
        "download_attempted": False,
        "network_used": False,
        "source_paths": source_checked,
        "fixture_paths": fixture_checked,
        "runtime_paths": runtime_checked,
        "checkpoint_paths": checkpoint_checked,
        "found": found,
        "present_count": len(found),
        "all_probes_absent": not found,
        "source_or_runtime_imported": False,
    }


def absence_summary() -> dict:
    probes = absence_probes()
    return {
        "present_count": probes["present_count"],
        "all_probes_absent": probes["all_probes_absent"],
        "fixed_probe_list_only": True,
        "download_attempted": False,
        "recursive_workspace_walk": False,
        "source_or_runtime_imported": False,
    }


# ---------------------------------------------------------------------------
# Historical matched-evidence check.
# ---------------------------------------------------------------------------

HISTORICAL_TABLE_MARKER = ("| Candidate | Far-end-only ERLE (dB) | "
                           "Double-talk near-reference SNR (dB) | Runtime "
                           "RTF |")


def _pilot_controller_rows(text: str) -> list[str]:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == HISTORICAL_TABLE_MARKER:
            start = index
            break
    if start is None:
        raise ValueError("historical_table_missing")
    rows: list[str] = []
    for line in lines[start + 1:]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        if set(cells[0]) <= set("-: "):
            continue
        rows.append(cells[0])
    return rows


def historical_pilot_match() -> dict:
    text = (SOURCE_ROOT / "research/aec_research_20261028.md").read_text(
        encoding="utf-8")
    rows = _pilot_controller_rows(text)
    expected = ["NLMS, 128 taps", "NLMS, 192 taps", "NLMS, 256 taps",
                "NLMS, 512 taps", "SpeexDSP MDF, 4,000-sample tail (250 ms)"]
    if rows != expected:
        raise ValueError("historical_controller_rows_changed")
    return {
        "status": "present_unmatched_no_nkf_result",
        "research_note": "research/aec_research_20261028.md",
        "historical_pilot_reports_referenced": [
            "reports/aec_challenge_synthetic_pilot_20261028.csv",
            "reports/aec_challenge_real_pilot_20261028.csv",
        ],
        "reports_opened_here": False,
        "reports_staged_here": False,
        "controller_rows": rows,
        "expected_controller_rows": expected,
        "nkf_candidate_listed": "Neural Kalman filter" in text,
        "nkf_result_row_present": any("kalman" in row.lower() for row in rows),
        "matched_execution": False,
        "admitted_as_result": False,
        "inherited_metrics": False,
        "note": "The pinned local pilot ran five deterministic NLMS/SpeexDSP "
                "controls on a synthetic echo path; none is Neural Kalman "
                "filtering. Its values keep their original synthetic/pilot "
                "scope and are not reproduced, pooled or inherited here.",
    }


# ---------------------------------------------------------------------------
# Required artifacts, blockers, gates and room mapping.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    return [{
        "id": artifact_id,
        "kind": kind,
        "requirement": requirement,
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
    } for artifact_id, kind, requirement in REQUIRED_ARTIFACTS_SPEC]


def exact_blockers() -> list[dict]:
    return [{
        "id": blocker_id,
        "artifact_id": artifact_id,
        "linked_gates": list(linked_gates),
        "statement": statement,
        "required_action": action,
        "status": "open",
        "qualifies": False,
    } for blocker_id, artifact_id, linked_gates, statement, action
        in EXACT_BLOCKERS_SPEC]


def release_gates() -> list[dict]:
    rows = (
        ("RG-01", "exact licensed source pinned",
         "No exact NKF source repository, 40-hex revision, license or "
         "per-file SHA-256 manifest exists.",
         "Stage and pin the exact source with reviewed terms and per-file "
         "digests."),
        ("RG-02", "exact checkpoint, model card and config pinned",
         "No trained checkpoint, byte count, model card, training provenance "
         "or architecture/parameter digest exists.",
         "Pin the checkpoint and model/config digest with reviewed terms."),
        ("RG-03", "rights-cleared matched room fixture",
         "No paired far-end/microphone fixture, frozen RIR or render set, "
         "delay, movement, noise, reset schedule or held-out split exists.",
         "Freeze a rights-cleared matched room fixture with held-out "
         "rooms/devices and exact metadata."),
        ("RG-04", "source, checkpoint, fixture and output rights",
         "Source, checkpoint, training-data, corpus and output-use rights are "
         "unresolved.",
         "Record reviewed source, checkpoint, fixture and output-use rights "
         "with notices."),
        ("RG-05", "model, runtime and geometry pinned",
         "No exact geometry, model digest, runtime lock, checkpoint loader or "
         "installed adapter geometry is pinned.",
         "Pin the model, runtime, loader and geometry with exact digests."),
        ("RG-06", "reset, reconvergence, double-talk and reference timing "
         "measured",
         "No candidate reset, reconvergence, double-talk, reference-timing, "
         "echo-attenuation or near-end-damage value exists.",
         "Measure reset, reconvergence, double-talk and reference timing on "
         "the frozen matched room fixture."),
        ("RG-07", "default-off adapter intake and independent review",
         "No opt-in adapter decision, descriptor or independent exact-head "
         "review exists.",
         "Open an opt-in, default-off adapter only after RG-01 to RG-06 pass "
         "and obtain independent review."),
        ("RG-08", "product, benchmark and release approval",
         "No benchmark validation, product decision or release approval "
         "exists; DEFER remains in force.",
         "Complete benchmark and release review with explicit approval; no "
         "missing result may qualify the candidate."),
    )
    return [{
        "id": gate_id,
        "name": name,
        "status": "blocked",
        "qualifies": False,
        "reason": reason,
        "reopen_condition": reopen,
        "linked_row": _gate_link(),
    } for gate_id, name, reason, reopen in rows]


def room_profile_block() -> dict:
    rows = (
        ("ROOM-01", "frozen render/reference or measured RIRs",
         "blocked_no_frozen_room_set"),
        ("ROOM-02", "channel, rate and hop geometry",
         "blocked_no_candidate_geometry"),
        ("ROOM-03", "excitation, delay, movement, noise and reset schedule",
         "blocked_no_fixture_schedule"),
        ("ROOM-04", "echo-only, near-end-only, overlap and no-reference cases",
         "blocked_no_candidate_or_fixture"),
        ("ROOM-05", "echo attenuation", "blocked_no_candidate_output"),
        ("ROOM-06", "near-end damage", "blocked_no_candidate_output"),
        ("ROOM-07", "nonfinite failures and alignments including "
         "delayed/missing render", "partial_local_harness_rejection_only"),
        ("ROOM-08", "reset, reconvergence and double-talk",
         "blocked_no_candidate_instance"),
        ("ROOM-09", "no-reference suppressor independent comparison",
         "not_applicable_candidate_requires_reference"),
    )
    return {
        "name": PROFILE,
        "profile": PROFILE_KEY,
        "status": "blocked",
        "source_path": PROFILE_SOURCE_REL,
        "plan_note": PLAN_NOTE,
        "required_items": [{
            "id": item_id,
            "requirement": requirement,
            "status": "blocked",
            "evidence": evidence,
            "qualification_effect": "none",
            "satisfied_for_qualification": False,
        } for item_id, requirement, evidence in rows],
        "satisfied_for_qualification": [],
        "real_candidate_metrics": None,
        "echo_attenuation_measured": False,
        "near_end_damage_measured": False,
        "reset_measured": False,
        "reconvergence_measured": False,
        "double_talk_measured": False,
        "reference_timing_measured": False,
        "nonfinite_failures_measured": False,
        "delayed_or_missing_render_tested": False,
        "no_reference_comparison_run": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Synthetic harness stimuli. These characterise local analytic signals only;
# they are not candidate output and no NKF process touches them.
# ---------------------------------------------------------------------------


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state


def _unit(seed: int, length: int) -> list[float]:
    generator = _lcg(seed)
    return [((next(generator) >> 8) / 8388608.0) - 1.0
            for _ in range(length)]


def silence(length: int = FRAME_SAMPLES) -> list[float]:
    return [0.0] * length


def impulse(length: int = FRAME_SAMPLES, index: int = 0) -> list[float]:
    values = [0.0] * length
    values[index] = 1.0
    return values


def step(length: int = FRAME_SAMPLES, boundary: int = 80) -> list[float]:
    return [0.5 if index >= boundary else -0.5 for index in range(length)]


def sweep(length: int = FRAME_SAMPLES, start_hz: float = 200.0,
          end_hz: float = 3000.0, rate: int = SAMPLE_RATE_HZ) -> list[float]:
    total = length / rate
    values: list[float] = []
    for index in range(length):
        time = index / rate
        phase = 2.0 * math.pi * (
            start_hz * time
            + (end_hz - start_hz) * time * time / (2.0 * total))
        values.append(0.4 * math.sin(phase))
    return values


def speech_like(length: int = FRAME_SAMPLES,
                rate: int = SAMPLE_RATE_HZ) -> list[float]:
    noise = _unit(0x5EED, length)
    values: list[float] = []
    for index in range(length):
        time = index / rate
        envelope = 0.5 + 0.5 * math.sin(2.0 * math.pi * 3.0 * time)
        values.append(0.3 * envelope * (
            math.sin(2.0 * math.pi * 220.0 * time)
            + 0.5 * math.sin(2.0 * math.pi * 440.0 * time)) + 0.02 * noise[index])
    return values


STIMULUS_GENERATORS = {
    "silence": lambda: silence(),
    "impulse": lambda: impulse(),
    "step": lambda: step(),
    "sweep": lambda: sweep(),
    "speech_like": lambda: speech_like(),
}


def _metrics(samples: list[float]) -> dict:
    peak = max(abs(value) for value in samples)
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    mean_abs = sum(abs(value) for value in samples) / len(samples)
    return {
        "length": len(samples),
        "peak_milli": int(round(peak * 1000)),
        "rms_micro": int(round(rms * 1_000_000)),
        "mean_abs_micro": int(round(mean_abs * 1_000_000)),
        "sha256": sha256_bytes(struct.pack("<%df" % len(samples), *samples)),
    }


def stimulus_probe() -> dict:
    stimuli = {name: _metrics(generator())
               for name, generator in sorted(STIMULUS_GENERATORS.items())}
    source = silence()
    identity = list(source)
    identity_metrics = _metrics(identity)
    return {
        "purpose": "harness stimulus characterisation only; not an NKF result "
                   "and not a candidate output",
        "candidate_processing": False,
        "harness_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "reference_channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "frame_values": FRAME_SAMPLES,
        },
        "stimuli": stimuli,
        "identity_control": {
            "input_sha256": _metrics(source)["sha256"],
            "output_sha256": identity_metrics["sha256"],
            "bit_exact": identity_metrics["sha256"] == _metrics(source)["sha256"],
            "changed_values": sum(1 for left, right in zip(source, identity)
                                  if left != right),
        },
        "speech_contrast": {
            "speech_rms_micro": stimuli["speech_like"]["rms_micro"],
            "silence_rms_micro": stimuli["silence"]["rms_micro"],
            "impulse_peak_milli": stimuli["impulse"]["peak_milli"],
            "note": "Analytic contrast only; no intelligibility or speech "
                    "quality result.",
        },
        "room_comparison": {
            "status": "blocked_no_candidate_output",
            "model_pinned": False,
            "equal_alignment_matched": False,
            "reset_measured": False,
            "reconvergence_measured": False,
            "double_talk_measured": False,
            "reference_timing_measured": False,
        },
    }


# ---------------------------------------------------------------------------
# Fail-closed admission for a caller-supplied NKF bundle.
# ---------------------------------------------------------------------------

BUNDLE_SCHEMA = "audio-sdk/neural-kalman-filtering-nkf-caller-bundle/0.1"
BUNDLE_KEYS = frozenset({"schema", "source", "model", "fixture", "runtime",
                         "compare"})
SOURCE_KEYS = frozenset({"repository", "revision", "license"})
MODEL_KEYS = frozenset({
    "weights_sha256", "weights_bytes", "model_card_sha256", "sample_rate_hz",
    "frame_samples", "hop_samples", "state_dimension",
})
FIXTURE_KEYS = frozenset({
    "class", "far_end_sha256", "mic_sha256", "sample_rate_hz", "channels",
    "frame_samples", "delay_samples", "movement_segments", "rights",
})
RUNTIME_KEYS = frozenset({"lock_sha256", "python", "streaming_harness"})
COMPARE_KEYS = frozenset({"reset_measured", "reconvergence_measured",
                          "double_talk_measured", "reference_timing_measured"})
MAX_WEIGHT_BYTES = 536870912


def _exact_keys(value: Any, expected: frozenset, code: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(code)
    if set(value) != set(expected):
        raise ValueError("unknown_field" if set(value) - set(expected)
                         else code)
    return value


def _require_int(value: Any, code: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(code)
    if not minimum <= value <= maximum:
        raise ValueError(code)
    return value


def _require_hex64(value: Any, code: str) -> str:
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise ValueError(code)
    return value


def validate_bundle(request: Any) -> dict:
    bundle = _exact_keys(request, BUNDLE_KEYS, "invalid_bundle")
    if bundle["schema"] != BUNDLE_SCHEMA:
        raise ValueError("invalid_schema")

    source = _exact_keys(bundle["source"], SOURCE_KEYS, "invalid_source")
    if not isinstance(source["repository"], str) or not source["repository"]:
        raise ValueError("invalid_source")
    if not isinstance(source["revision"], str) or \
            HEX40.fullmatch(source["revision"]) is None:
        raise ValueError("unsafe_path_revision")
    if not isinstance(source["license"], str) or not source["license"].strip():
        raise ValueError("invalid_source")

    model = _exact_keys(bundle["model"], MODEL_KEYS, "invalid_model")
    _require_hex64(model["weights_sha256"], "invalid_model")
    _require_int(model["weights_bytes"], "invalid_model_type", 1,
                 MAX_WEIGHT_BYTES)
    _require_hex64(model["model_card_sha256"], "invalid_model")
    if _require_int(model["sample_rate_hz"], "invalid_model_geometry",
                    8000, 48000) != SAMPLE_RATE_HZ:
        raise ValueError("invalid_model_geometry")
    if _require_int(model["frame_samples"], "invalid_model_geometry",
                    1, 4096) != FRAME_SAMPLES:
        raise ValueError("invalid_model_geometry")
    hop = _require_int(model["hop_samples"], "invalid_model_geometry", 1,
                       FRAME_SAMPLES)
    state_dimension = _require_int(model["state_dimension"],
                                  "invalid_model_geometry", 1, 65536)

    fixture = _exact_keys(bundle["fixture"], FIXTURE_KEYS,
                          "invalid_fixture_geometry")
    if fixture["class"] != "measured_room_pair":
        raise ValueError("fixture_class_not_matched")
    _require_hex64(fixture["far_end_sha256"], "invalid_fixture_geometry")
    _require_hex64(fixture["mic_sha256"], "invalid_fixture_geometry")
    if _require_int(fixture["sample_rate_hz"], "invalid_fixture_geometry",
                    8000, 48000) != SAMPLE_RATE_HZ:
        raise ValueError("invalid_fixture_geometry")
    if _require_int(fixture["channels"], "invalid_fixture_geometry",
                    1, 1) != CHANNELS:
        raise ValueError("invalid_fixture_geometry")
    if _require_int(fixture["frame_samples"], "invalid_fixture_geometry",
                    1, 4096) != FRAME_SAMPLES:
        raise ValueError("invalid_fixture_geometry")
    _require_int(fixture["delay_samples"], "invalid_fixture_geometry",
                 0, 8000)
    _require_int(fixture["movement_segments"], "invalid_fixture_geometry",
                 0, 1024)
    if fixture["rights"] != "cleared":
        raise ValueError("rights_not_cleared")

    runtime = _exact_keys(bundle["runtime"], RUNTIME_KEYS, "invalid_runtime")
    _require_hex64(runtime["lock_sha256"], "invalid_runtime")
    if runtime["python"] != "3.12.16":
        raise ValueError("invalid_runtime")
    if runtime["streaming_harness"] is not True:
        raise ValueError("invalid_runtime")

    compare = _exact_keys(bundle["compare"], COMPARE_KEYS, "invalid_comparison")
    if any(compare[key] is not True for key in COMPARE_KEYS):
        raise ValueError("invalid_comparison")

    return {
        "schema": BUNDLE_SCHEMA,
        "source_revision": source["revision"],
        "source_repository": source["repository"],
        "weights_bytes": model["weights_bytes"],
        "hop_samples": hop,
        "state_dimension": state_dimension,
        "fixture_class": fixture["class"],
        "sample_rate_hz": fixture["sample_rate_hz"],
        "channels": fixture["channels"],
        "frame_samples": fixture["frame_samples"],
        "rights": fixture["rights"],
        "python": runtime["python"],
        "streaming_harness": runtime["streaming_harness"],
    }


def _base_bundle() -> dict:
    return {
        "schema": BUNDLE_SCHEMA,
        "source": {
            "repository": "https://example.invalid/neural-kalman-filtering",
            "revision": "0" * 40,
            "license": "caller-declared-license",
        },
        "model": {
            "weights_sha256": "1" * 64,
            "weights_bytes": 1048576,
            "model_card_sha256": "2" * 64,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "frame_samples": FRAME_SAMPLES,
            "hop_samples": FRAME_SAMPLES,
            "state_dimension": 64,
        },
        "fixture": {
            "class": "measured_room_pair",
            "far_end_sha256": "3" * 64,
            "mic_sha256": "4" * 64,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "delay_samples": 320,
            "movement_segments": 4,
            "rights": "cleared",
        },
        "runtime": {
            "lock_sha256": "5" * 64,
            "python": "3.12.16",
            "streaming_harness": True,
        },
        "compare": {
            "reset_measured": True,
            "reconvergence_measured": True,
            "double_talk_measured": True,
            "reference_timing_measured": True,
        },
    }


def admit_bundle(request: Any) -> dict:
    validate_bundle(request)
    missing = ["ART-01 exact source", "ART-02 checkpoint and model card",
               "ART-03 matched room fixture", "ART-04 runtime"]
    return {
        "status": "deferred_required_artifacts_absent",
        "missing_artifacts": missing,
        "present_artifacts": [],
        "qualifies": False,
        "runtime_invoked": False,
        "audio_read": False,
    }


def _json_case(payload: str) -> str:
    try:
        loads_strict(payload)
    except ValueError as error:
        return str(error).split(":", 1)[0]
    return "accepted"


def strictness_controls() -> dict:
    duplicate = '{"a":1,"a":2}'
    nonfinite = '{"a":NaN}'
    float_value = '{"a":1.5}'
    json_codes = [_json_case(duplicate), _json_case(nonfinite),
                  _json_case(float_value)]
    pin_texts = (
        "0" * 63 + "  source:research/x.md\n",
        "0" * 64 + "  docs/task-evidence/neural-kalman-filtering-nkf/a\n" +
        "0" * 64 + "  docs/task-evidence/neural-kalman-filtering-nkf/a\n",
        "0" * 64 + "  unknown:label\n",
    )
    pin_codes = []
    for text in pin_texts:
        try:
            parse_pin_lines(text)
            pin_codes.append("accepted")
        except ValueError as error:
            pin_codes.append(str(error).split(":", 1)[0])
    readme_bad = [
        "# no tables",
        README_MARKERS["source"][0] + "\n| `source:x` | `zz` |\n" +
        README_MARKERS["source"][1],
        README_MARKERS["artifacts"][0] + "\n| `a` | `" + "0" * 64 +
        "` |\n" + README_MARKERS["artifacts"][1],
    ]
    readme_codes = []
    for text in readme_bad:
        try:
            parse_readme_digest_tables(text)
            readme_codes.append("accepted")
        except ValueError as error:
            readme_codes.append(str(error).split(":", 1)[0])
    return {
        "json_cases": len(json_codes),
        "json_rejected": sum(code != "accepted" for code in json_codes),
        "pin_cases": len(pin_codes),
        "pin_rejected": sum(code != "accepted" for code in pin_codes),
        "readme_cases": len(readme_codes),
        "readme_rejected": sum(code != "accepted" for code in readme_codes),
        "json_codes": json_codes,
        "pin_codes": pin_codes,
        "readme_codes": readme_codes,
        "all_adverse_parsers_rejected": all(
            code != "accepted" for code in json_codes + pin_codes +
            readme_codes),
    }


def admission_controls() -> dict:
    base = _base_bundle()
    cases: list[dict] = []

    def add(case_id: str, kind: str, code: str, request: Any,
            accepted: bool, admission: str | None) -> None:
        cases.append({
            "id": case_id,
            "kind": kind,
            "code": code,
            "accepted_by_schema": accepted,
            "admission": admission,
            "qualifies": False,
            "state_advanced": False,
            "runtime_invoked": False,
            "audio_read": False,
        })

    add("CASE-01", "schema_control", "none", base, True,
        "deferred_required_artifacts_absent")

    def mutated(mutator) -> Any:
        value = json.loads(json.dumps(base))
        mutator(value)
        return value

    def expect(case_id: str, code: str, request: Any) -> None:
        try:
            validate_bundle(request)
            actual = "accepted"
        except ValueError as error:
            actual = str(error).split(":", 1)[0]
        if actual != code:
            raise ValueError("admission_case_code_mismatch:" + case_id + ":" +
                             actual)
        add(case_id, "adverse", code, request, False, None)

    def expect_json(case_id: str, code: str, payload: str) -> None:
        try:
            validate_bundle(loads_strict(payload))
            actual = "accepted"
        except ValueError as error:
            actual = str(error).split(":", 1)[0]
        if actual != code:
            raise ValueError("admission_json_code_mismatch:" + case_id + ":" +
                             actual)
        add(case_id, "adverse", code, payload, False, None)

    expect_json("CASE-02", "invalid_json", "{not json")
    expect_json("CASE-03", "duplicate_json_key",
                '{"schema":"a","schema":"b"}')
    expect_json("CASE-04", "nonfinite_json", '{"value":Infinity}')

    def missing_source(value):
        value["source"].pop("revision")
    expect("CASE-05", "invalid_source", mutated(missing_source))

    def unsafe_revision(value):
        value["source"]["revision"] = "../../etc/passwd"
    expect("CASE-06", "unsafe_path_revision", mutated(unsafe_revision))

    def bad_frame(value):
        value["model"]["frame_samples"] = 256
    expect("CASE-07", "invalid_model_geometry", mutated(bad_frame))

    def float_bytes(value):
        value["model"]["weights_bytes"] = 1.5
    expect("CASE-08", "invalid_model_type", mutated(float_bytes))

    def wrong_geometry(value):
        value["fixture"]["channels"] = 2
    expect("CASE-09", "invalid_fixture_geometry", mutated(wrong_geometry))

    def synthetic_proxy(value):
        value["fixture"]["class"] = "synthetic_proxy"
    expect("CASE-10", "fixture_class_not_matched", mutated(synthetic_proxy))

    def unresolved_rights(value):
        value["fixture"]["rights"] = "unresolved"
    expect("CASE-11", "rights_not_cleared", mutated(unresolved_rights))

    def unknown(value):
        value["source"]["mirror"] = "x"
    expect("CASE-12", "unknown_field", mutated(unknown))

    def bad_runtime(value):
        value["runtime"]["streaming_harness"] = False
    expect("CASE-13", "invalid_runtime", mutated(bad_runtime))

    def bad_compare(value):
        value["compare"]["double_talk_measured"] = False
    expect("CASE-14", "invalid_comparison", mutated(bad_compare))

    control = admit_bundle(base)
    controls = {
        "schema_control_admission": control["status"],
        "schema_control_qualifies": control["qualifies"],
        "schema_control_present_artifacts": control["present_artifacts"],
        "runtime_invoked": False,
        "audio_read": False,
        "inference_performed": False,
    }
    return {"cases": cases, "controls": controls}


# ---------------------------------------------------------------------------
# Pins and README digest tables.
# ---------------------------------------------------------------------------


def local_manifest_paths() -> list[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name not in LOCAL_MANIFEST_EXCLUDED)


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for relative, expected in SOURCE_PINS.items():
        actual = sha256_file(SOURCE_ROOT / relative)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + relative)
        rows.append((actual, "source:" + relative))
    for relative, expected in BOUNDARY_PINS.items():
        actual = sha256_file(WORKTREE / relative)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + relative)
        rows.append((actual, "sdk:" + relative))
    for name in local_manifest_paths():
        path = HERE / name
        if not path.is_file():
            raise ValueError("local_pin_missing:" + name)
        rows.append((sha256_file(path), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        "# SHA-256 pins for SDK-NEURAL-KALMAN-FILTERING-NKF task-local evidence.",
        "# source: paths are relative to the pinned research workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable full plan/swarm/TASKS.json is never hashed; only the "
        "stable row identity gates.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {path}" for digest, path in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  (source:[A-Za-z0-9_./-]+|"
    r"sdk:[A-Za-z0-9_./-]+|"
    r"docs/task-evidence/neural-kalman-filtering-nkf/[A-Za-z0-9_./-]+)$")


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
                      if name not in LOCAL_MANIFEST_EXCLUDED},
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
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
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
                expected_digest = SOURCE_PINS[key[len("source:"):]]
                path = SOURCE_ROOT / key[len("source:"):]
            elif section == "boundary":
                expected_digest = BOUNDARY_PINS[key[len("sdk:"):]]
                path = WORKTREE / key[len("sdk:"):]
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
        path = HERE / key
        line = f"| `{key}` | `{sha256_file(path)}` | {path.stat().st_size} |"
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
        if name in LOCAL_MANIFEST_EXCLUDED:
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
# Contract and report.
# ---------------------------------------------------------------------------


def build_contract() -> dict:
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
        "format": FORMAT,
        "verification_profile": PROFILE_KEY,
        "evidence_status": EVIDENCE_STATUS,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "depends_on": list(DEPENDS_ON),
        "write_scope": TASK_PREFIX,
        "plan_note": PLAN_NOTE,
        "upstream_blocker": {
            "status": "blocked_source_model_checkpoint_fixture_runtime_and_"
                      "rights_absent",
            "source_revision": None,
            "source_sha256": None,
            "checkpoint_sha256": None,
            "checkpoint_bytes": None,
            "model_card_sha256": None,
            "parameter_config_digest": None,
            "fixture_sha256": None,
            "runtime_sha256": None,
            "rights_review": "blocked",
            "matched_room_fixture": False,
            "reopen_condition":
                "Stage the exact NKF source at a 40-hex commit with reviewed "
                "license and per-file SHA-256 manifest; pin the trained "
                "checkpoint, model card, architecture and parameter/config "
                "digest; provide a rights-cleared paired far-end/microphone "
                "room fixture with frozen RIR or render set, delay, movement, "
                "noise, reset schedule and held-out splits; pin the runtime "
                "and streaming harness; then measure reset, reconvergence, "
                "double-talk and reference timing on the exact model and "
                "obtain independent exact-head review.",
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "non_claims": list(NON_CLAIMS),
        "prohibited_actions": [
            "download, clone, reconstruct, train or substitute the candidate",
            "invent weights, an architecture or a learned controller",
            "read, decode or listen to real audio",
            "measure device, callback or wall-clock timing",
            "change provider, descriptor, registry, default, ABI, "
            "CONTRACTS.md, shared build or CI",
            "change board or handoff state",
            "make a benchmark, product or release claim",
        ],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
    }


def validate_contract(contract: dict) -> None:
    expected = build_contract()
    for key, value in expected.items():
        if contract.get(key) != value:
            raise ValueError("contract_field_mismatch:" + key)


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "candidate_qualified": False,
        "all_release_gates_blocked": True,
        "blocked_gate_count": len(GATE_IDS),
        "blocked_gate_ids": list(GATE_IDS),
        "no_missing_result_qualifies_candidate": True,
        "not_qualified": True,
        "reason": "Exact source, checkpoint, model card, matched room "
                  "fixture, runtime, rights and review are absent; no "
                  "candidate output or reset/reconvergence/double-talk/"
                  "reference-timing measurement exists.",
    }


def build_report() -> dict:
    profile = profile_source()
    contract = build_contract()
    admission = admission_controls()
    strictness = strictness_controls()
    probes = absence_probes()
    row_identity = board_row_projection()
    rows = linked_rows()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "format": FORMAT,
        "generated_by": "run.py",
        "task": TASK,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "component_id": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "verification_profile": PROFILE_KEY,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "depends_on": list(DEPENDS_ON),
        "write_scope": TASK_PREFIX,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "plan_note": PLAN_NOTE,
        "profile_source": profile,
        "room_profile": room_profile_block(),
        "profile_mapping": {
            "frozen_render_reference_or_measured_rir":
                "blocked_no_frozen_room_set",
            "channel_rate_hop_geometry": "blocked_no_candidate_geometry",
            "excitation_delay_movement_noise_and_reset_schedule":
                "blocked_no_fixture_schedule",
            "echo_only_near_end_only_overlap_and_no_reference_cases":
                "blocked_no_candidate_or_fixture",
            "echo_attenuation": "blocked_no_candidate_output",
            "near_end_damage": "blocked_no_candidate_output",
            "nonfinite_failures_and_alignments":
                "partial_local_harness_rejection_only",
            "delayed_or_missing_render":
                "blocked_no_candidate_output_and_no_fixture",
            "reset_reconvergence_and_double_talk":
                "blocked_no_candidate_instance",
            "reference_timing": "blocked_no_candidate_output",
            "no_reference_suppressor_comparison":
                "not_applicable_candidate_requires_reference",
            "candidate_output":
                "blocked_source_model_checkpoint_fixture_runtime_and_rights_"
                "absent",
        },
        "public_v0_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "frame_samples": FRAME_SAMPLES,
            "abi_major": ABI_MAJOR,
            "abi_minor": ABI_MINOR,
            "preserved": True,
            "sdk_callback_invoked": False,
        },
        "geometry": {
            "task_kind": "acoustic_echo_cancellation_with_paired_reference",
            "candidate_family":
                "neural_kalman_filter_with_learned_adaptation_control",
            "suppressed_quantity": "loudspeaker_echo_in_microphone_capture",
            "requires_paired_far_end_reference": True,
            "requires_synchronized_reference_and_microphone": True,
            "requires_learned_model_weights": True,
            "stateful_recursive": True,
            "classical_path_model_plus_learned_control": True,
            "declared_sample_rate_hz": None,
            "declared_frame_samples": None,
            "declared_hop_samples": None,
            "declared_state_dimension": None,
            "declared_network_structure": None,
            "declared_checkpoint_sha256": None,
            "declared_algorithmic_delay": None,
            "declared_reset_policy": None,
            "geometry_verified": False,
            "candidate_output_measured": False,
            "installed_v0": False,
            "provider_registered": False,
            "note": "The pinned census names a classical echo-path model plus "
                    "learned adaptation/gain control but records no "
                    "architecture, geometry, checkpoint, tuning, delay "
                    "alignment or reset policy. No local implementation "
                    "exists.",
        },
        "task_requirement": {
            "plan_note": PLAN_NOTE,
            "required_comparison": "reset, reconvergence, double-talk and "
                                   "reference timing on the exact pinned "
                                   "model",
            "required_measurements": ["reset", "reconvergence", "double_talk",
                                      "reference_timing"],
            "paired_reference_required": True,
            "model_pinned": False,
            "reset_measured": False,
            "reconvergence_measured": False,
            "double_talk_measured": False,
            "reference_timing_measured": False,
            "echo_attenuation_measured": False,
            "near_end_preservation_measured": False,
            "status": "blocked_no_pinned_model_and_no_matched_room_fixture",
            "reason": "Candidate source, checkpoint and matched room fixture "
                      "are absent; synthetic analytic stimuli cannot establish "
                      "reset, reconvergence, double-talk or reference timing.",
        },
        "source_probe": source_probe(),
        "parameter_probe": parameter_probe(),
        "checkpoint_probe": checkpoint_probe(),
        "fixture_probe": fixture_probe(),
        "runtime_probe": runtime_probe(),
        "rights_probe": rights_probe(),
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(),
        },
        "historical_evidence": historical_pilot_match(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "gates": release_gates(),
        "remaining_gates": list(GATE_IDS),
        "qualification": qualification_block(),
        "disposition": {
            "promotion": "defer",
            "production_exposure": "DEFER",
            "status": "incomplete",
            "decision": "DEFER",
            "qualification_status": QUALIFICATION_STATUS,
            "proposal_only": True,
            "incomplete": True,
            "not_qualified": True,
            "defer_before": DEFER_BEFORE,
            "expose_as_processor": False,
            "registered": False,
            "default_enabled": False,
            "missing_result_qualifies": False,
        },
        "boundary": {
            "task_local_only": True,
            "installed_v0_unchanged": True,
            "provider_registered": False,
            "enabled_by_default": False,
            "public_api_abi_changed": False,
            "contracts_md_changed": False,
            "registry_changed": False,
            "shared_cmake_changed": False,
            "ci_changed": False,
            "board_or_handoff_changed": False,
            "real_corpus_or_weights": False,
            "real_audio_read": False,
            "downloads": False,
            "listening": False,
            "device_timing": False,
            "benchmark_claim": False,
            "release_claim": False,
            "descriptor_default_changed": False,
        },
        "scope": {
            "task_local_evidence_only": True,
            "provider_change": False,
            "default_change": False,
            "abi_change": False,
            "contracts_change": False,
            "registry_change": False,
            "shared_build_change": False,
            "ci_change": False,
            "board_or_handoff_change": False,
            "real_audio_read": False,
            "downloads": False,
            "listening": False,
            "device_timing": False,
            "benchmark_claim": False,
            "release_claim": False,
        },
        "admission": admission,
        "strictness": strictness,
        "stimulus_probe": stimulus_probe(),
        "prohibited_claims": list(NON_CLAIMS),
        "linked_row_identity": {
            "projection": row_identity,
            "sha256": board_row_digest(row_identity),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "linked_rows": [dict(row) for row in rows],
            "linked_rows_sha256": linked_rows_digest(rows),
        },
        "task_row_identity": {
            "source": BOARD_TASK_ROW,
            "whole_file_hashed": False,
            "stable_fields": row_identity,
            "stable_sha256": board_row_digest(row_identity),
        },
        "source_pins": {
            path: {
                "sha256": digest,
                "actual": sha256_file(SOURCE_ROOT / path),
                "verified": sha256_file(SOURCE_ROOT / path) == digest,
            } for path, digest in SOURCE_PINS.items()
        },
        "boundary_pins": {
            path: {
                "sha256": digest,
                "actual": sha256_file(WORKTREE / path),
                "verified": sha256_file(WORKTREE / path) == digest,
            } for path, digest in BOUNDARY_PINS.items()
        },
    }
    assert_no_float(report)
    return report


# ---------------------------------------------------------------------------
# Git scope helpers: newest merge-base, fail closed.
# ---------------------------------------------------------------------------


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
