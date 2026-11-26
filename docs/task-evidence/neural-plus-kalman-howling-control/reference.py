# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for the neural-plus-Kalman row.

This module is NOT a neural/Kalman howling suppressor. It contains no neural
network, no weight loader, no inference path, no Kalman filter, no covariance
update, no feedback-path estimator, no closed-loop simulator and no candidate
audio output. A bounded, read-only search of named workspace paths finds no
exact NeuralKalmanAHS source revision, no architecture/parameter set, no
checkpoint, no rights-cleared closed-loop proxy with held-out physical paths and
no hash-pinned runtime.

The module therefore builds a fail-closed readiness report:

* strict request validation for a caller-supplied hybrid bundle;
* explicit source, algorithm, checkpoint, fixture, runtime and rights probes;
* an admission gate that defers every structurally valid bundle because the
  required external artifacts are absent;
* synthetic harness stimuli for rejection and characterisation controls only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

Nothing is downloaded, cloned, installed, reconstructed, trained, fitted or
simulated as a candidate. No weight is opened. No result qualifies the
catalogued ``neural-plus-kalman-howling-control`` component.
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
TASK_PREFIX = "docs/task-evidence/neural-plus-kalman-howling-control/"

TASK = "SDK-NEURAL-PLUS-KALMAN-HOWLING-CONTROL"
TITLE = "Neural plus Kalman howling control"
COMPONENT = "neural-plus-kalman-howling-control"
COMPONENT_ID = "neural-plus-kalman-howling-control"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "dsp"
PROFILE_KEY = "DSP"
STATUS = "proposal_only_not_qualified"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
QUALIFICATION_STATUS = "not_qualified"
FORMAT = "sdk-task-evidence/0.1"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/neural-plus-kalman-howling-control-readiness/0.1"
CONTRACT_SCHEMA_ID = ("audio-sdk/neural-plus-kalman-howling-control-contract/"
                      "0.1")
REPORT_SCHEMA_ID = "audio-sdk/neural-plus-kalman-howling-control-report/0.1"
BASE_COMMIT = "9074704819a6af4168f8c9cf3bbe8da50484c29a"
BRANCH = "swarm/SDK-NEURAL-PLUS-KALMAN-HOWLING-CONTROL"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/"
    "audio-sdk/SDK-NEURAL-PLUS-KALMAN-HOWLING-CONTROL")
REVIEWER = "reviewer-NEURAL-PLUS-KALMAN-HOWLING-CONTROL"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

# ---------------------------------------------------------------------------
# Stable, read-only pins. Source paths are relative to SOURCE_ROOT; SDK paths
# are worktree relative. Nothing here is executed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
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
    "docs/task-evidence/adaptive-notch-with-gain-margin/report.json":
        "b6732740cab7fafd9e270953d7b8f72b6d7951ee5e6d08c1e344a6e9ed228645",
    "docs/task-evidence/afc-spex/report.json":
        "b94ac1cc9fb6209a302ce1e6054befe715479d6cec9c2473cd53ba7827b2868d",
    "docs/task-evidence/fixed-feedback-gain-margin/report.json":
        "c7cd3a0518c315a4871b011bd89d74d09207d2d5bf84105c5877a76bf158b2bf",
    "docs/task-evidence/kalman-afc/report.json":
        "23c346db59373b6528276cc737b5b9457653d74d2920828ea5f20939a07ddb76",
    "docs/task-evidence/survey-cln-11/report.json":
        "5e997cf8a4838750aafc29ab650ee95a321311dd17c9588ed952e8e04500c93a",
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
    "sweeps, steps, impulses, silence",
    "clean speech",
    "intelligibility or load-specific control",
    "gain, response, attack/release",
    "headroom, delay",
    "numerical behavior",
    "state transitions",
    "interacting nonlinear configurations",
)
PLAN_NOTE = ("Require exact algorithm/checkpoint and a closed-loop proxy with "
             "held-out physical paths.")

GATE_IDS = tuple("RG-%02d" % index for index in range(1, 9))
ARTIFACT_IDS = tuple("ART-%02d" % index for index in range(1, 9))
BLOCKER_IDS = tuple("BLK-%02d" % index for index in range(1, 8))
DSP_ITEM_IDS = tuple("DSP-%02d" % index for index in range(1, 11))

# Installed public v0 baseline. This is the unchanged SDK format, not a hybrid
# neural/Kalman geometry.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
ABI_MAJOR = 0
ABI_MINOR = 1

SCOPE_BASE_REFS = ("origin/main", "main")
NON_CLAIMS = [
    "No neural network, weight loader, inference path, Kalman filter, "
    "covariance update, feedback-path estimate or adaptive gain is present "
    "or evaluated.",
    "No exact NeuralKalmanAHS or other hybrid source revision, license, entry "
    "point or per-file digest is admitted.",
    "No exact checkpoint, tensor digest, byte count, format or weight terms "
    "is present, opened, loaded or executed.",
    "No authoritative neural architecture, layer/context window, output "
    "activation, FFT/hop, covariance, forgetting, regularization, update "
    "order, delay alignment or reset policy is declared.",
    "No rights-cleared closed-loop proxy with held-out physical paths exists "
    "locally, and no microphone, playback reference or path impulse response "
    "is opened or decoded.",
    "No closed-loop stability, gain-before-feedback, maximum stable gain, "
    "detection, recovery, residual tone, speech preservation or ablation "
    "value is measured.",
    "No identity, Kalman-only, neural-only or fixed-margin comparison at "
    "equal output gain is performed.",
    "No real audio is opened, decoded, played or listened to, and no device, "
    "callback, wall-clock or target timing is measured.",
    "No provider, descriptor, registry, default, public API/ABI, "
    "CONTRACTS.md, shared build or CI change exists.",
    "No benchmark, product, release or qualification claim is made.",
]

REQUIRED_ARTIFACTS_SPEC = (
    ("ART-01", "exact_source_revision_and_license",
     "The exact neural-plus-Kalman implementation at an immutable 40-hex "
     "commit, with the streaming inference entry point, reviewed upstream "
     "license text, per-file SHA-256 manifest, file count and tree digest."),
    ("ART-02", "exact_algorithm_and_parameter_set",
     "A citable algorithm and parameter set: neural architecture, layer and "
     "context window, output activation, Kalman FFT/hop/window, process and "
     "measurement covariance, forgetting factor, regularization, update "
     "order, delay alignment, precision and reset/reconvergence policy, with "
     "a canonical config digest."),
    ("ART-03", "exact_checkpoint_and_terms",
     "The exact trained checkpoint with SHA-256, byte count, format, tensor "
     "layout, producing revision, training-data provenance and reviewed "
     "weight terms."),
    ("ART-04", "closed_loop_proxy_with_held_out_physical_paths",
     "A rights-cleared recursive closed-loop proxy pairing target speech, "
     "microphone and actual playback reference, with path digest, loop gain, "
     "delay, saturation, initial state and development versus held-out "
     "physical path split."),
    ("ART-05", "pinned_runtime_and_harness",
     "A hash-pinned runtime, checkpoint loader and closed-loop harness with "
     "install/import parity, finite drain, reset and exact sample-rate/frame "
     "geometry."),
    ("ART-06", "frozen_comparison_and_ablation_protocol",
     "A frozen protocol comparing the exact hybrid with identity, "
     "Kalman-only, neural-only and fixed-margin controls at equal output gain "
     "on held-out physical paths, including adverse and nonfinite cases."),
    ("ART-07", "source_weights_fixture_output_and_loop_rights",
     "Reviewed source, weight, corpus, output-use and physical-loop rights "
     "with notices and an authorization record for the exact target."),
    ("ART-08", "dsp_result_bundle_adapter_and_review",
     "A complete DSP and closed-loop result bundle for the exact candidate "
     "plus an opt-in, default-off adapter decision and independent exact-head "
     "review."),
)

EXACT_BLOCKERS_SPEC = (
    ("BLK-01", "ART-01", ("RG-01",),
     "The pinned feedback-control census names the neural/Kalman hybrid "
     "family and cites NeuralKalmanAHS, HybridAHS and AHS_2023, but records "
     "no repository carrying source at a 40-hex revision, no license, no "
     "entry point and no per-file SHA-256 manifest. The named public "
     "repositories were observed to expose demo material only.",
     "Stage and pin the exact hybrid source at a 40-hex commit with reviewed "
     "license text and a per-file SHA-256 manifest."),
    ("BLK-02", "ART-02", ("RG-04",),
     "No authoritative hybrid algorithm or parameter set is available: the "
     "neural architecture, layer and context window, output activation, "
     "Kalman FFT/hop/window, process and measurement covariance, forgetting "
     "factor, regularization, update order, delay alignment, precision and "
     "reset policy are unrecorded.",
     "Pin a citable algorithm and parameter/config set with a canonical "
     "digest; do not substitute a self-invented architecture or tuning."),
    ("BLK-03", "ART-03", ("RG-02", "RG-04"),
     "No exact checkpoint is staged. The hybrid family requires trained "
     "weights, and no SHA-256, byte count, format, tensor layout, producing "
     "revision, training-data provenance or weight terms exists locally. No "
     "weight is opened, converted, reconstructed or downloaded.",
     "Supply the exact checkpoint with SHA-256, byte count, format, "
     "provenance and reviewed weight terms."),
    ("BLK-04", "ART-04", ("RG-03", "RG-07"),
     "No rights-cleared recursive closed-loop proxy with held-out physical "
     "paths exists. Target speech, microphone, actual playback reference, "
     "path digest, loop gain, delay, saturation, initial state and a "
     "development/held-out physical path split are absent. The historical "
     "AMI/SMARD pilot is a different controller screen without a neural "
     "row.",
     "Freeze a rights-cleared closed-loop proxy with explicit path metadata "
     "and a held-out physical path split."),
    ("BLK-05", "ART-05", ("RG-04",),
     "No hash-pinned hybrid runtime, checkpoint loader or closed-loop harness "
     "exists on the public adapter boundary. scripts/ci.py is the SDK CI, not "
     "this candidate's runtime, and no lockfile, wheel set or imported "
     "implementation is recorded.",
     "Pin the runtime, loader and harness with a lockfile, install/import "
     "parity and the exact installed geometry."),
    ("BLK-06", "ART-07", ("RG-03", "RG-05", "RG-06"),
     "Source, weight, corpus, output-use and physical-loop rights are "
     "unrecorded. No source license, weight terms, fixture corpus permission, "
     "output-use grant or closed-loop authorization exists, and the pinned "
     "research note uses AMI/SMARD only as cited research inputs.",
     "Record reviewed source, weight, corpus, output-use and loop rights "
     "before any candidate execution."),
    ("BLK-07", "ART-06", ("RG-05", "RG-06", "RG-07", "RG-08"),
     "The required task evidence cannot be produced: no exact algorithm or "
     "checkpoint and no held-out closed-loop proxy exist, so the hybrid, its "
     "ablations and the fixed-margin control cannot be measured. No DSP "
     "matrix, closed-loop failure/control result, listening result or "
     "independent review exists.",
     "Run the frozen DSP and closed-loop protocol on the exact candidate with "
     "identity, Kalman-only, neural-only and fixed-margin controls at equal "
     "output gain, then obtain independent exact-head review."),
)
BLOCKER_TOKENS = (
    "neural", "Kalman", "source", "40-hex", "SHA-256", "architecture",
    "checkpoint", "weights", "closed-loop", "held-out physical paths",
    "playback reference", "loop gain", "delay", "ablation", "fixed-margin",
    "equal output gain", "rights", "runtime", "review",
)

# Fixed-path probes. Existence checks only; no directory walk, no network, no
# audio decode, no package import and no checkpoint open.
SOURCE_PROBE_PATHS = (
    "src/audioml_eval/neural_kalman_ahs.py",
    "src/audioml_eval/neural_kalman_feedback.py",
    "src/audioml_eval/feedback_control_neural_kalman.py",
    "scripts/evaluate_feedback_control_neural_kalman.py",
    "reports/feedback-control/neural-kalman-ahs-screen.json",
    "reports/feedback-control/neural-kalman-measured-loop.json",
    "NeuralKalmanAHS",
    "AHS_2023",
    "HybridAHS",
    "AFC-SPEX",
    "research/plans/neural-kalman-ahs",
    "data/fixtures/neural-kalman-ahs",
)
CHECKPOINT_PROBE_PATHS = (
    "NeuralKalmanAHS/checkpoints",
    "AHS_2023/checkpoints",
    "HybridAHS/checkpoints",
    "data/tmp/neural-kalman-ahs-weights",
    "data/fixtures/neural-kalman-ahs/weights",
    "reports/feedback-control/neural-kalman-ahs-checkpoint",
)
FIXTURE_PROBE_PATHS = (
    "data/fixtures/neural-kalman-ahs",
    "data/fixtures/neural-kalman-closed-loop",
    "data/fixtures/held-out-physical-paths",
    "data/tmp/smard/neural-kalman-ahs",
    "reports/feedback-control/neural-kalman-measured-loop.json",
)
RUNTIME_PROBE_PATHS = (
    "requirements-neural-kalman.lock",
    "neural-kalman-ahs-runtime.lock",
    "data/tmp/neural-kalman-ahs-runtime",
    "build/neural-kalman-ahs",
    "conformance/neural-kalman-ahs",
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
        if line.startswith("| DSP |"):
            row = line.strip()
            break
    if row is None:
        raise ValueError("dsp_profile_row_missing")
    for phrase in PROFILE_PHRASES:
        if phrase not in row:
            raise ValueError("dsp_profile_phrase_missing:" + phrase)

    inventory_path = SOURCE_ROOT / INVENTORY_REL
    if sha256_file(inventory_path) != SOURCE_PINS[INVENTORY_REL]:
        raise ValueError("inventory_digest_changed")
    inventory = read_strict_json(inventory_path)
    components = inventory.get("components")
    if not isinstance(components, list):
        raise ValueError("inventory_components_not_list")
    matches = [entry for entry in components
               if isinstance(entry, dict) and entry.get("id") == COMPONENT_ID]
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
    note = (SOURCE_ROOT / "research/feedback_control_20261028.md")
    text = note.read_text(encoding="utf-8")
    checked, found = _probe(SOURCE_PROBE_PATHS)
    return {
        "status": "blocked_exact_hybrid_source_absent",
        "family_listed_in_pinned_note": "Neural/Kalman hybrid" in text,
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
        "named_code_leads": [
            {
                "name": "YIXUANZ/NeuralKalmanAHS",
                "repository": "https://github.com/YIXUANZ/NeuralKalmanAHS",
                "status":
                    "demo_material_only_no_source_or_checkpoint_observed",
                "admitted_as_source": False,
            },
            {
                "name": "YIXUANZ/AHS_2023",
                "repository": "https://github.com/YIXUANZ/AHS_2023",
                "status":
                    "demo_material_only_no_source_or_checkpoint_observed",
                "admitted_as_source": False,
            },
            {
                "name": "ZLiNJU/AFC-SPEX",
                "repository": "https://github.com/ZLiNJU/AFC-SPEX",
                "status":
                    "different_multichannel_task_checkpoint_required",
                "admitted_as_source": False,
            },
        ],
        "note": "Read-only existence checks only; no clone, fetch, archive "
                "extraction or download. The pinned note names the "
                "neural/Kalman hybrid family and cites paper results, but "
                "records no runnable repository, revision, license, entry "
                "point or architecture.",
    }


def algorithm_probe() -> dict:
    return {
        "status": "blocked_authoritative_algorithm_and_parameter_set_absent",
        "update_equations_present": False,
        "config_digest": None,
        "neural_architecture": None,
        "neural_layer_count": None,
        "neural_context_samples": None,
        "neural_output_activation": None,
        "neural_output_role": None,
        "kalman_fft_size": None,
        "kalman_hop_samples": None,
        "kalman_window": None,
        "process_noise_covariance": None,
        "measurement_noise_covariance": None,
        "forgetting_factor": None,
        "regularization": None,
        "update_order": None,
        "delay_alignment_samples": None,
        "numerical_precision": None,
        "reset_policy": None,
        "verified": False,
        "invented_here": False,
        "note": "The pinned note states only that a frequency-domain Kalman "
                "filter is combined with a self-attentive RNN whose streaming "
                "output becomes the Kalman reference. No architecture, tensor "
                "shape, activation, update order, FFT/hop, covariance, "
                "forgetting, tuning or reset policy is recorded, so none is "
                "invented or substituted.",
    }


def checkpoint_probe() -> dict:
    checked, found = _probe(CHECKPOINT_PROBE_PATHS)
    return {
        "status": "blocked_exact_checkpoint_absent",
        "family_requires_pretrained_weights": True,
        "named_candidate_checkpoint_present": False,
        "pinned_model_present": False,
        "admitted_model": None,
        "present_file_count": len(found),
        "checked_paths": checked,
        "found": found,
        "sha256": None,
        "byte_count": None,
        "format": None,
        "tensor_layout": None,
        "producing_revision": None,
        "training_data_provenance": None,
        "terms_recorded": False,
        "opened_or_loaded": False,
        "note": "The hybrid family needs trained weights. No checkpoint is "
                "staged; the named public repositories were observed without "
                "released weights and no release asset was listed. No weight "
                "is opened, converted, reconstructed or downloaded, and local "
                "possession alone would not be treated as rights evidence.",
    }


def fixture_probe() -> dict:
    checked, found = _probe(FIXTURE_PROBE_PATHS)
    return {
        "status": "blocked_closed_loop_proxy_with_held_out_paths_absent",
        "matched_fixture_present": False,
        "closed_loop_proxy_present": False,
        "measured_physical_loop_present": False,
        "required_signals": ["target_speech", "microphone",
                             "playback_reference"],
        "sample_rate_hz": None,
        "channels": None,
        "frame_samples": None,
        "hop_samples": None,
        "loop_gain_measured": False,
        "delay_measured": False,
        "path_digest": None,
        "saturation_measured": False,
        "initial_state_frozen": False,
        "held_out_physical_paths": False,
        "path_split": None,
        "rights_cleared": False,
        "checked_paths": checked,
        "found": found,
        "present": False,
        "read": False,
        "decoded": False,
        "note": "Existence checks only; no audio or impulse response is "
                "opened or decoded. The historical AMI/SMARD material is "
                "speech plus measured-IR shapes behind pinned research "
                "reports, not a staged closed-loop proxy with a held-out "
                "physical path split, and it contains no hybrid row.",
    }


def runtime_probe() -> dict:
    checked, found = _probe(RUNTIME_PROBE_PATHS)
    return {
        "status": "blocked_pinned_runtime_absent",
        "pinned_runtime_present": False,
        "pinned_runtime_complete": False,
        "pinned_runtime_version_verified": False,
        "checkpoint_loader_present": False,
        "closed_loop_harness_present": False,
        "lockfile": None,
        "python_requirement": None,
        "sha256": None,
        "checked_paths": checked,
        "found": found,
        "imported_or_executed": False,
        "note": "No package or weight loader is installed, imported or "
                "downloaded. The present SDK CI script is not this "
                "candidate's runtime, and no closed-loop harness, lockfile or "
                "wheel set exists.",
    }


def rights_probe() -> dict:
    return {
        "status": "blocked_rights_unrecorded",
        "source_license": None,
        "source_license_file_present": False,
        "checkpoint_terms": None,
        "checkpoint_terms_recorded": False,
        "training_data_terms": None,
        "fixture_corpus_rights": False,
        "redistribution_scope": None,
        "output_use_cleared": False,
        "physical_loop_authorized": False,
        "review": "blocked",
        "reviewed_by": None,
        "note": "No source license, weight terms, fixture corpus permission, "
                "training-data terms, output-use grant or physical-loop "
                "authorization is recorded locally. AMI and SMARD are cited "
                "as research inputs with their own terms, not redistributed, "
                "staged or admitted here.",
    }


def absence_probes() -> dict:
    source_checked, source_found = _probe(SOURCE_PROBE_PATHS)
    checkpoint_checked, checkpoint_found = _probe(CHECKPOINT_PROBE_PATHS)
    fixture_checked, fixture_found = _probe(FIXTURE_PROBE_PATHS)
    runtime_checked, runtime_found = _probe(RUNTIME_PROBE_PATHS)
    found = sorted(set(source_found + checkpoint_found + fixture_found +
                       runtime_found))
    return {
        "method": "fixed_path_existence_only",
        "recursive_walk": False,
        "download_attempted": False,
        "network_used": False,
        "source_paths": source_checked,
        "checkpoint_paths": checkpoint_checked,
        "fixture_paths": fixture_checked,
        "runtime_paths": runtime_checked,
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
# Historical and source-reported evidence checks.
# ---------------------------------------------------------------------------


def _pilot_controller_rows(text: str) -> list[str]:
    marker = "| Candidate | Method | Median SDR, all runs |"
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith(marker):
            start = index
            break
    if start is None:
        raise ValueError("pilot_controller_table_missing")
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
    text = (SOURCE_ROOT / "research/feedback_control_20261028.md").read_text(
        encoding="utf-8")
    rows = _pilot_controller_rows(text)
    expected = ["Identity", "Fixed margin", "Adaptive notch", "Notch + margin",
                "Block-NLMS AFC", "AFC + 3 dB margin"]
    if rows != expected:
        raise ValueError("pilot_controller_rows_changed")
    if "NeuralKalmanAHS" not in text:
        raise ValueError("source_reported_hybrid_missing")
    return {
        "status": "present_unmatched_no_hybrid_result",
        "research_note": "research/feedback_control_20261028.md",
        "historical_pilot_reports_referenced": [
            "reports/feedback-control/ami-closed-loop-screen.json",
            "reports/feedback-control/smard-measured-ir-screen.json",
        ],
        "reports_opened_here": False,
        "reports_staged_here": False,
        "controller_rows": rows,
        "expected_controller_rows": expected,
        "neural_kalman_hybrid_candidate_listed":
            "Neural/Kalman hybrid" in text,
        "neural_kalman_result_row_present": any(
            "neural" in row.lower() or "kalman" in row.lower()
            for row in rows),
        "matched_execution": False,
        "admitted_as_result": False,
        "inherited_metrics": False,
        "source_reported_literature": {
            "status": "cited_paper_values_only_not_reproduced_or_comparable",
            "paper": "NeuralKalmanAHS journal study 2024",
            "utterance_count": 200,
            "loop_gain_milli": [2000, 2500, 3000],
            "sdr_micro_db": [2650000, 1980000, 1450000],
            "pesq_milli": [2330, 2170, 2040],
            "source_note": "research/feedback_control_20261028.md",
            "admitted_as_result": False,
            "reproduced_here": False,
            "comparable_here": False,
        },
        "note": "The pinned pilot ran six controllers on synthetic and "
                "measured-IR simulated loops; none is a neural/Kalman hybrid. "
                "The cited paper values keep their own dataset, loop-gain and "
                "metric scope. Neither is reproduced, pooled or inherited "
                "here.",
    }


# ---------------------------------------------------------------------------
# Required artifacts, blockers, gates and DSP mapping.
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
        ("RG-01", "exact licensed hybrid source pinned",
         "No exact neural/Kalman source repository, 40-hex revision, license "
         "or per-file SHA-256 manifest exists.",
         "Stage and pin the exact source with reviewed terms and per-file "
         "digests."),
        ("RG-02", "exact checkpoint and weight terms pinned",
         "No checkpoint SHA-256, byte count, format, provenance or reviewed "
         "weight terms exists.",
         "Pin the exact checkpoint and record reviewed weight terms."),
        ("RG-03", "rights-cleared closed-loop proxy with held-out paths",
         "No closed-loop proxy, path digest, loop gain, delay, saturation or "
         "held-out physical path split exists.",
         "Freeze a rights-cleared closed-loop proxy with held-out physical "
         "paths and exact metadata."),
        ("RG-04", "algorithm, parameter set, runtime and geometry pinned",
         "No exact neural/Kalman architecture, parameter set, update order, "
         "runtime lock or installed geometry is pinned.",
         "Pin the algorithm, parameter/config set, runtime and geometry with "
         "exact digests."),
        ("RG-05", "hybrid reproduced with identity and single-stage ablations",
         "No hybrid output, identity control, Kalman-only ablation or "
         "neural-only ablation exists.",
         "Reproduce the hybrid and its identity and single-stage ablations on "
         "the frozen proxy."),
        ("RG-06", "DSP matrix and closed-loop failure controls",
         "No gain, response, attack/release, headroom, delay, numerical, "
         "state-transition, nonlinear, path-change or nonfinite result "
         "exists.",
         "Run the full DSP and closed-loop adverse/control matrix on the "
         "exact candidate."),
        ("RG-07", "held-out physical path result and equal-gain comparison",
         "No held-out physical path result and no fixed-margin comparison at "
         "equal output gain exists.",
         "Evaluate on held-out physical paths against fixed margin at equal "
         "output gain."),
        ("RG-08", "adapter intake, review and release approval",
         "No opt-in adapter decision, authorized listening, benchmark "
         "validation, independent exact-head review or release approval "
         "exists; DEFER remains in force.",
         "Open a default-off adapter only after RG-01 to RG-07 pass, then "
         "complete review and release approval."),
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


def dsp_profile_block() -> dict:
    rows = (
        ("DSP-01", "sweeps, steps, impulses, silence",
         "partial_synthetic_harness_characterisation_only"),
        ("DSP-02", "clean speech and task-matched control",
         "blocked_no_permitted_cohort"),
        ("DSP-03", "gain and frequency response",
         "blocked_no_candidate_output"),
        ("DSP-04", "attack and release where applicable",
         "blocked_no_candidate_output"),
        ("DSP-05", "headroom and peaks",
         "blocked_no_candidate_output"),
        ("DSP-06", "delay and content mapping",
         "blocked_no_candidate_output"),
        ("DSP-07", "numerical behavior",
         "partial_local_harness_rejection_only"),
        ("DSP-08", "state transitions and reset",
         "blocked_no_candidate_instance"),
        ("DSP-09", "interacting nonlinear configurations",
         "blocked_no_candidate_instance"),
        ("DSP-10", "closed-loop proxy with held-out physical paths",
         "blocked_no_fixture_and_no_candidate_output"),
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
        "hybrid_reproduced": False,
        "checkpoint_loaded": False,
        "closed_loop_proxy_run": False,
        "held_out_physical_paths_evaluated": False,
        "gain_before_feedback_measured": False,
        "recovery_measured": False,
        "fixed_margin_equal_gain_compared": False,
        "identity_control_measured": False,
        "kalman_only_ablation_measured": False,
        "neural_only_ablation_measured": False,
        "clean_speech_measured": False,
        "headroom_measured": False,
        "delay_measured": False,
        "state_transitions_measured": False,
        "nonlinear_configurations_measured": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Synthetic harness stimuli. These characterise local analytic signals only;
# they are not candidate output and no hybrid model touches them.
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
            + 0.5 * math.sin(2.0 * math.pi * 440.0 * time))
            + 0.02 * noise[index])
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
        "purpose": "harness stimulus characterisation only; not a hybrid "
                   "result and not a candidate output",
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
        "closed_loop_proxy": {
            "status": "blocked_no_fixture_and_no_candidate_output",
            "held_out_physical_paths_evaluated": False,
            "loop_gain_measured": False,
            "delay_measured": False,
        },
        "ablation_comparison": {
            "status": "blocked_no_candidate_output",
            "identity_control_measured": False,
            "kalman_only_ablation_measured": False,
            "neural_only_ablation_measured": False,
            "fixed_margin_equal_gain_compared": False,
        },
    }


# ---------------------------------------------------------------------------
# Fail-closed admission for a caller-supplied hybrid bundle.
# ---------------------------------------------------------------------------

BUNDLE_SCHEMA = ("audio-sdk/neural-plus-kalman-howling-control-caller-bundle/"
                 "0.1")
BUNDLE_KEYS = frozenset({"schema", "source", "algorithm", "checkpoint",
                         "fixture", "runtime", "compare"})
SOURCE_KEYS = frozenset({"repository", "revision", "license"})
ALGORITHM_KEYS = frozenset({
    "architecture", "update_order", "fft_size", "hop_samples",
    "forgetting_micro", "regularization_micro", "delay_alignment_samples",
    "reset_policy",
})
CHECKPOINT_KEYS = frozenset({"sha256", "byte_count", "format", "terms"})
FIXTURE_KEYS = frozenset({
    "class", "target_sha256", "mic_sha256", "reference_sha256",
    "sample_rate_hz", "channels", "frame_samples", "loop_gain_micro",
    "delay_samples", "held_out_paths", "split", "rights",
})
RUNTIME_KEYS = frozenset({"lock_sha256", "python", "closed_loop_harness"})
COMPARE_KEYS = frozenset({"identity_control", "kalman_only_ablation",
                          "neural_only_ablation",
                          "fixed_margin_at_equal_output_gain",
                          "held_out_paths_evaluated"})
UPDATE_ORDER = "neural_reference_then_kalman_update"
FIXTURE_CLASS = "closed_loop_proxy_with_physical_paths"
PATH_SPLIT = "held_out_physical_paths"
RESET_POLICIES = ("hard", "soft")


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


def _require_text(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(code)
    return value


def validate_bundle(request: Any) -> dict:
    bundle = _exact_keys(request, BUNDLE_KEYS, "invalid_bundle")
    if bundle["schema"] != BUNDLE_SCHEMA:
        raise ValueError("invalid_schema")

    source = _exact_keys(bundle["source"], SOURCE_KEYS, "invalid_source")
    _require_text(source["repository"], "invalid_source")
    if not isinstance(source["revision"], str) or \
            HEX40.fullmatch(source["revision"]) is None:
        raise ValueError("unsafe_path_revision")
    _require_text(source["license"], "invalid_source")

    algorithm = _exact_keys(bundle["algorithm"], ALGORITHM_KEYS,
                            "invalid_algorithm")
    _require_text(algorithm["architecture"], "invalid_algorithm")
    if algorithm["update_order"] != UPDATE_ORDER:
        raise ValueError("invalid_update_order")
    fft_size = _require_int(algorithm["fft_size"],
                            "invalid_algorithm_geometry", 64, 16384)
    if fft_size & (fft_size - 1):
        raise ValueError("invalid_algorithm_geometry")
    hop = _require_int(algorithm["hop_samples"], "invalid_algorithm_geometry",
                       1, fft_size // 2)
    _require_int(algorithm["forgetting_micro"], "invalid_algorithm_type",
                 1, 1_000_000)
    _require_int(algorithm["regularization_micro"], "invalid_algorithm_type",
                 0, 1_000_000)
    _require_int(algorithm["delay_alignment_samples"],
                 "invalid_algorithm_type", 0, 8000)
    if algorithm["reset_policy"] not in RESET_POLICIES:
        raise ValueError("invalid_algorithm")

    checkpoint = _exact_keys(bundle["checkpoint"], CHECKPOINT_KEYS,
                             "invalid_checkpoint")
    _require_hex64(checkpoint["sha256"], "invalid_checkpoint")
    _require_int(checkpoint["byte_count"], "invalid_checkpoint", 1,
                 1 << 31)
    _require_text(checkpoint["format"], "invalid_checkpoint")
    if not _require_text(checkpoint["terms"], "checkpoint_terms_unrecorded"):
        raise ValueError("checkpoint_terms_unrecorded")

    fixture = _exact_keys(bundle["fixture"], FIXTURE_KEYS,
                          "invalid_fixture_geometry")
    if fixture["class"] != FIXTURE_CLASS:
        raise ValueError("fixture_class_not_matched")
    _require_hex64(fixture["target_sha256"], "invalid_fixture_geometry")
    _require_hex64(fixture["mic_sha256"], "invalid_fixture_geometry")
    _require_hex64(fixture["reference_sha256"], "invalid_fixture_geometry")
    if _require_int(fixture["sample_rate_hz"], "invalid_fixture_geometry",
                    8000, 48000) != SAMPLE_RATE_HZ:
        raise ValueError("invalid_fixture_geometry")
    if _require_int(fixture["channels"], "invalid_fixture_geometry",
                    1, 1) != CHANNELS:
        raise ValueError("invalid_fixture_geometry")
    if _require_int(fixture["frame_samples"], "invalid_fixture_geometry",
                    1, 4096) != FRAME_SAMPLES:
        raise ValueError("invalid_fixture_geometry")
    _require_int(fixture["loop_gain_micro"], "invalid_fixture_geometry",
                 500_000, 3_000_000)
    _require_int(fixture["delay_samples"], "invalid_fixture_geometry",
                 0, 8000)
    held_out_paths = _require_int(fixture["held_out_paths"],
                                  "held_out_paths_missing", 1, 64)
    if held_out_paths < 2:
        raise ValueError("held_out_paths_missing")
    if fixture["split"] != PATH_SPLIT:
        raise ValueError("held_out_paths_missing")
    if fixture["rights"] != "cleared":
        raise ValueError("rights_not_cleared")

    runtime = _exact_keys(bundle["runtime"], RUNTIME_KEYS, "invalid_runtime")
    _require_hex64(runtime["lock_sha256"], "invalid_runtime")
    if runtime["python"] != "3.12.16":
        raise ValueError("invalid_runtime")
    if runtime["closed_loop_harness"] is not True:
        raise ValueError("invalid_runtime")

    compare = _exact_keys(bundle["compare"], COMPARE_KEYS,
                          "invalid_comparison")
    for key in COMPARE_KEYS:
        if compare[key] is not True:
            raise ValueError("invalid_comparison")

    return {
        "schema": BUNDLE_SCHEMA,
        "source_revision": source["revision"],
        "source_repository": source["repository"],
        "architecture": algorithm["architecture"],
        "update_order": algorithm["update_order"],
        "fft_size": fft_size,
        "hop_samples": hop,
        "checkpoint_sha256": checkpoint["sha256"],
        "checkpoint_byte_count": checkpoint["byte_count"],
        "fixture_class": fixture["class"],
        "held_out_paths": held_out_paths,
        "path_split": fixture["split"],
        "sample_rate_hz": fixture["sample_rate_hz"],
        "channels": fixture["channels"],
        "frame_samples": fixture["frame_samples"],
        "rights": fixture["rights"],
        "python": runtime["python"],
        "closed_loop_harness": runtime["closed_loop_harness"],
    }


def _base_bundle() -> dict:
    return {
        "schema": BUNDLE_SCHEMA,
        "source": {
            "repository": "https://example.invalid/neural-kalman-ahs",
            "revision": "0" * 40,
            "license": "caller-declared-license",
        },
        "algorithm": {
            "architecture": "caller-declared-self-attentive-rnn-plus-kalman",
            "update_order": UPDATE_ORDER,
            "fft_size": 512,
            "hop_samples": 160,
            "forgetting_micro": 990000,
            "regularization_micro": 1000,
            "delay_alignment_samples": 0,
            "reset_policy": "soft",
        },
        "checkpoint": {
            "sha256": "1" * 64,
            "byte_count": 1048576,
            "format": "caller-declared-torch-state-dict",
            "terms": "caller-declared-research-use",
        },
        "fixture": {
            "class": FIXTURE_CLASS,
            "target_sha256": "2" * 64,
            "mic_sha256": "3" * 64,
            "reference_sha256": "4" * 64,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "loop_gain_micro": 1_250_000,
            "delay_samples": 1280,
            "held_out_paths": 4,
            "split": PATH_SPLIT,
            "rights": "cleared",
        },
        "runtime": {
            "lock_sha256": "5" * 64,
            "python": "3.12.16",
            "closed_loop_harness": True,
        },
        "compare": {
            "identity_control": True,
            "kalman_only_ablation": True,
            "neural_only_ablation": True,
            "fixed_margin_at_equal_output_gain": True,
            "held_out_paths_evaluated": True,
        },
    }


def admit_bundle(request: Any) -> dict:
    validate_bundle(request)
    missing = ["ART-01 exact source", "ART-02 algorithm/parameter set",
               "ART-03 exact checkpoint", "ART-04 closed-loop proxy",
               "ART-05 pinned runtime"]
    return {
        "status": "deferred_required_artifacts_absent",
        "missing_artifacts": missing,
        "present_artifacts": [],
        "qualifies": False,
        "runtime_invoked": False,
        "checkpoint_opened": False,
        "audio_read": False,
        "inference_performed": False,
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
        "0" * 64 + "  docs/task-evidence/neural-plus-kalman-howling-control/a\n"
        + "0" * 64 +
        "  docs/task-evidence/neural-plus-kalman-howling-control/a\n",
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
            "checkpoint_opened": False,
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

    def missing_architecture(value):
        value["algorithm"].pop("architecture")
    expect("CASE-07", "invalid_algorithm", mutated(missing_architecture))

    def bad_order(value):
        value["algorithm"]["update_order"] = "kalman_then_neural"
    expect("CASE-08", "invalid_update_order", mutated(bad_order))

    def bad_fft(value):
        value["algorithm"]["fft_size"] = 500
    expect("CASE-09", "invalid_algorithm_geometry", mutated(bad_fft))

    def float_forgetting(value):
        value["algorithm"]["forgetting_micro"] = 0.99
    expect("CASE-10", "invalid_algorithm_type", mutated(float_forgetting))

    def bad_checkpoint(value):
        value["checkpoint"]["sha256"] = "not-a-digest"
    expect("CASE-11", "invalid_checkpoint", mutated(bad_checkpoint))

    def missing_terms(value):
        value["checkpoint"]["terms"] = " "
    expect("CASE-12", "checkpoint_terms_unrecorded", mutated(missing_terms))

    def wrong_geometry(value):
        value["fixture"]["channels"] = 2
    expect("CASE-13", "invalid_fixture_geometry", mutated(wrong_geometry))

    def synthetic_proxy(value):
        value["fixture"]["class"] = "synthetic_proxy"
    expect("CASE-14", "fixture_class_not_matched", mutated(synthetic_proxy))

    def no_held_out(value):
        value["fixture"]["held_out_paths"] = 1
    expect("CASE-15", "held_out_paths_missing", mutated(no_held_out))

    def unresolved_rights(value):
        value["fixture"]["rights"] = "unresolved"
    expect("CASE-16", "rights_not_cleared", mutated(unresolved_rights))

    def unknown(value):
        value["source"]["mirror"] = "x"
    expect("CASE-17", "unknown_field", mutated(unknown))

    def bad_runtime(value):
        value["runtime"]["closed_loop_harness"] = False
    expect("CASE-18", "invalid_runtime", mutated(bad_runtime))

    def missing_ablation(value):
        value["compare"]["neural_only_ablation"] = False
    expect("CASE-19", "invalid_comparison", mutated(missing_ablation))

    control = admit_bundle(base)
    controls = {
        "schema_control_admission": control["status"],
        "schema_control_qualifies": control["qualifies"],
        "schema_control_present_artifacts": control["present_artifacts"],
        "runtime_invoked": False,
        "checkpoint_opened": False,
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
        "# SHA-256 pins for SDK-NEURAL-PLUS-KALMAN-HOWLING-CONTROL evidence.",
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
    r"docs/task-evidence/neural-plus-kalman-howling-control/"
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
            "status": "blocked_source_algorithm_checkpoint_fixture_runtime_"
                      "and_rights_absent",
            "source_revision": None,
            "source_sha256": None,
            "algorithm_config_digest": None,
            "checkpoint_sha256": None,
            "checkpoint_byte_count": None,
            "checkpoint_terms": None,
            "fixture_sha256": None,
            "runtime_sha256": None,
            "rights_review": "blocked",
            "held_out_physical_paths": False,
            "measured_loop": False,
            "reopen_condition":
                "Stage the exact neural-plus-Kalman source at a 40-hex commit "
                "with reviewed license and per-file SHA-256 manifest; pin the "
                "exact neural architecture/output and Kalman FFT/hop/"
                "covariance/forgetting/regularization/update-order/delay/"
                "reset parameter set; supply the exact checkpoint with "
                "SHA-256, byte count, provenance and weight terms; freeze a "
                "rights-cleared closed-loop proxy with a held-out physical "
                "path split; pin the runtime and loader; then reproduce the "
                "hybrid and its identity, Kalman-only, neural-only and "
                "fixed-margin controls at equal output gain and obtain "
                "independent exact-head review.",
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "non_claims": list(NON_CLAIMS),
        "prohibited_actions": [
            "download, clone, reconstruct, train or substitute the candidate",
            "open, convert, load or execute any checkpoint or weight",
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
        "reason": "Exact source, algorithm/parameter set, checkpoint, "
                  "closed-loop proxy with held-out physical paths, runtime, "
                  "rights and review are absent; no candidate output, "
                  "ablation or closed-loop result exists.",
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
        "dsp_profile": dsp_profile_block(),
        "profile_mapping": {
            "sweeps_steps_impulses_silence_clean_speech":
                "partial_synthetic_harness_characterisation_only",
            "task_specific_intelligibility_or_load_control":
                "blocked_no_permitted_cohort",
            "gain_and_frequency_response": "blocked_no_candidate_output",
            "attack_and_release": "blocked_no_candidate_output",
            "headroom_and_peaks": "blocked_no_candidate_output",
            "delay_and_content_mapping": "blocked_no_candidate_output",
            "numerical_behavior": "partial_local_harness_rejection_only",
            "state_transitions": "blocked_no_candidate_instance",
            "interacting_nonlinear_configurations":
                "blocked_no_candidate_instance",
            "exact_algorithm_and_checkpoint":
                "blocked_no_source_parameter_or_checkpoint",
            "closed_loop_proxy_with_held_out_physical_paths":
                "blocked_no_fixture",
            "candidate_output":
                "blocked_source_algorithm_checkpoint_fixture_runtime_and_"
                "rights_absent",
            "ablation_and_fixed_margin_comparison":
                "blocked_no_candidate_output_and_no_held_out_paths",
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
            "task_kind":
                "acoustic_feedback_cancellation_with_neural_kalman_hybrid",
            "candidate_family":
                "neural_reference_refinement_with_frequency_domain_kalman_"
                "update",
            "suppressed_quantity":
                "loudspeaker_to_microphone_feedback_path",
            "requires_playback_reference": True,
            "requires_synchronized_mic_and_reference": True,
            "requires_pretrained_weights": True,
            "stateful_recursive": True,
            "per_bin_covariance_update": True,
            "neural_output_feeds_kalman_reference": True,
            "declared_neural_architecture": None,
            "declared_neural_context_samples": None,
            "declared_neural_output_activation": None,
            "declared_fft_size": None,
            "declared_hop_samples": None,
            "declared_process_noise": None,
            "declared_measurement_noise": None,
            "declared_forgetting_factor": None,
            "declared_regularization": None,
            "declared_update_order": None,
            "declared_delay_alignment": None,
            "declared_reset_policy": None,
            "geometry_verified": False,
            "candidate_output_measured": False,
            "installed_v0": False,
            "provider_registered": False,
            "note": "The pinned note describes a frequency-domain Kalman "
                    "filter plus a self-attentive RNN whose streaming output "
                    "becomes the Kalman reference, but records no "
                    "architecture, weights, update equations, tuning or "
                    "reset policy. The installed v0 path has one channel and "
                    "no playback reference, so it cannot represent this "
                    "geometry.",
        },
        "task_requirement": {
            "plan_note": PLAN_NOTE,
            "required_prerequisites": [
                "exact_neural_architecture_and_parameter_set",
                "exact_checkpoint_with_terms",
                "closed_loop_proxy",
                "held_out_physical_paths",
            ],
            "required_comparison": "exact hybrid versus identity, Kalman-only, "
                                   "neural-only and fixed-margin controls at "
                                   "equal output gain on held-out physical "
                                   "paths",
            "fixed_margin_reference":
                "docs/task-evidence/fixed-feedback-gain-margin/report.json",
            "kalman_reference":
                "docs/task-evidence/kalman-afc/report.json",
            "afc_spex_reference":
                "docs/task-evidence/afc-spex/report.json",
            "equal_output_gain_normalization_required": True,
            "exact_algorithm_present": False,
            "exact_checkpoint_present": False,
            "closed_loop_proxy_present": False,
            "held_out_physical_paths_present": False,
            "hybrid_reproduced": False,
            "identity_control_measured": False,
            "kalman_only_ablation_measured": False,
            "neural_only_ablation_measured": False,
            "fixed_margin_comparison_run_here": False,
            "status": "blocked_no_algorithm_checkpoint_or_held_out_proxy",
            "reason": "Source, algorithm, checkpoint, closed-loop proxy, "
                      "held-out physical paths and runtime are absent; "
                      "synthetic analytic stimuli cannot establish loop "
                      "stability or define the candidate.",
        },
        "source_probe": source_probe(),
        "algorithm_probe": algorithm_probe(),
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
            "checkpoint_opened": False,
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
            "checkpoint_opened": False,
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
# Branch scope helpers used by verify.py.
# ---------------------------------------------------------------------------


def _git(worktree: Path, *arguments: str,
         ) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base between HEAD and an available PR base ref."""
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
