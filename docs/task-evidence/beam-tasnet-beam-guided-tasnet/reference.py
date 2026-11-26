# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local spatial-boundary evidence for SDK-BEAM-TASNET-BEAM-GUIDED-TASNET.

This module is NOT Beam-TasNet and NOT Beam-Guided TasNet. It is not a
beamformer, separator, mask estimator, localizer or steering implementation. It
does not read weights, audio, media, a checkpoint, a caller asset or the
network; it invokes no vendor runtime, measures no device clock or channel
calibration and conducts no listening.

It models the *spatial admission boundary* the catalogued candidate family
would have to cross: synchronized multichannel f32 input, a declared linear
array geometry, an explicit reference channel, a caller-supplied external
weight/checkpoint asset and a fail-closed whole-clip boundary. The signal path
is an original deterministic geometry fixture (a reference-channel passthrough,
an alternate-channel passthrough and an unsteered channel mean), labelled as
such everywhere and never presented as a candidate result.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-BEAM-TASNET-BEAM-GUIDED-TASNET"
TITLE = "Beam-TasNet / Beam-Guided TasNet"
SLUG = "beam-tasnet-beam-guided-tasnet"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "72a52fc65f0b6db703d22714b8f7305642e4b412"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "spatial"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "processor_exposure"
COMPONENT = SLUG

SAMPLE_RATE_HZ = 16000
CHANNELS = 2
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
SAMPLES = 16000
MAX_CLIP_SAMPLES = 16000
REFERENCE_CHANNEL = 0

SPEED_OF_SOUND_MPS = 343.0
MIC_SPACING_M = 0.08
ARRAY_LAYOUT = "linear_uniform_axis_x"
TARGET_AZIMUTH_DEG = 30.0
INTERFERER_AZIMUTH_DEG = -45.0
CLOCK_ID = "fixture-sample-coordinate-not-device"
FIXTURE_EPOCH_NS = 1_767_225_600_000_000_000

SEED_BASE = 20261126
CONDITIONS: Tuple[str, ...] = (
    "target_only",
    "interference_only",
    "target_plus_interference",
    "channel_dropout",
)
VARIANTS: Dict[str, List[float]] = {
    "identity_passthrough": [1.0, 0.0],
    "alternate_reference_channel": [0.0, 1.0],
    "naive_channel_mean": [0.5, 0.5],
}
EPS = 1e-30

# Exact catalogued candidate identity, quoted from the pinned research ledgers.
# Neither architecture is selected, and no source, checkpoint, weight or
# runtime byte is present in, copied into or read from this worktree.
CANDIDATE_LABEL = "Beam-TasNet / Beam-Guided TasNet"
ARCHITECTURES: Tuple[Dict[str, Any], ...] = (
    {
        "name": "Beam-TasNet",
        "family": "multichannel Conv-TasNet separation followed by an MVDR beamformer",
        "source_revision": None,
        "checkpoint_id": None,
        "checkpoint_sha256": None,
        "checkpoint_bytes": None,
        "license": None,
        "source_or_weights_present": False,
    },
    {
        "name": "Beam-Guided TasNet",
        "family": "distinct iterative beam-guided target-separation framework",
        "source_lead": "https://github.com/hangtingchen/Beam-Guided-TasNet",
        "source_revision": None,
        "checkpoint_id": None,
        "checkpoint_sha256": None,
        "checkpoint_bytes": None,
        "license": None,
        "source_or_weights_present": False,
    },
)
SYNTHETIC_CONTROL_ARCH = "synthetic-admission-control-not-the-candidate"
ARCHITECTURE_NAMES: Tuple[str, ...] = tuple(item["name"] for item in ARCHITECTURES)

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md":
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md":
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/pilot_source_research.md":
        "c9db16172ffaa1bcf8b5cc334d9401173528c31d1ec966176d6e99a0bbe52fe5",
    "research/task_backlog.json":
        "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "docs/task-evidence/survey-cln-07/README.md":
        "b748f2fda2ffebf10ea5f00923dc1dc1110f0712bada2ded074def53ef682d34",
    "docs/task-evidence/survey-cln-07/report.json":
        "aad53c0a3e6d90c4d27fea6abb4001d40168700a8fa2d717f53b03091a9c5a6a",
    "docs/task-evidence/survey-spk-01/README.md":
        "554a9fcc044e89c35ba761bf1fa8f7fed172ba22f797e44bdd64a753c00adc9d",
    "docs/task-evidence/survey-spk-01/report.json":
        "04f17e36954b792bcba59b59fef537f6e699654cc6fd71c39e46567809a6ff2f",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_LINKS: Tuple[Dict[str, str], ...] = (
    {"task_id": TASK, "title": TITLE, "mode": "feasibility"},
    {
        "task_id": "SDK-FND-AUDIT",
        "title": "Public provider intake and asset boundary",
        "mode": "foundation",
    },
    {
        "task_id": "SDK-FND-EVIDENCE",
        "title": "Task-matched conformance and reproducible benchmark evidence",
        "mode": "foundation",
    },
    {
        "task_id": "SDK-FND-PROVIDER",
        "title": "Provider integration boundaries and build fragments",
        "mode": "foundation",
    },
)

# Fail-closed local file set. SOURCES.sha256 is excluded because a manifest
# cannot pin its own bytes; its .license sidecar is included.
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256.license",
    "adapter.json",
    "adapter.json.license",
    "check_licensing.py",
    "contract.json",
    "contract.json.license",
    "readiness.json",
    "readiness.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
    "max_clip_samples": MAX_CLIP_SAMPLES,
    "reference_channel": REFERENCE_CHANNEL,
    "processing_mode": "offline_multichannel_whole_clip",
}

BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "installed_v0_geometry_preserved": True,
    "installed_v0_behavior_change": False,
    "shared_build_or_ci_change": False,
    "processor_exposure": False,
    "task_board_or_handoff_write": False,
    "streaming_mode_added": False,
}

CLAIMS: Dict[str, bool] = {
    "real_beam_tasnet_runtime": False,
    "real_beam_guided_tasnet_runtime": False,
    "weights_accessed": False,
    "asset_downloaded": False,
    "real_array_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "channel_calibration_measured": False,
    "localization_or_steering_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "quality_claim": False,
    "release_claim": False,
    "separation_behavior_claimed": False,
}

PUBLIC_SURFACE: Dict[str, bool] = {
    "provider_registration": False,
    "installed_v0_geometry_change": False,
    "installed_v0_behavior_change": False,
    "api_or_abi_change": False,
    "descriptor_or_registry_change": False,
    "default_selection": False,
    "shared_build_or_ci_change": False,
    "task_board_or_handoff_change": False,
}

SCOPE: Dict[str, bool] = {
    "task_local_only": True,
    "documentation_and_synthetic_fixture_only": True,
    "real_array_audio": False,
    "real_weights": False,
    "runtime_invocation": False,
    "network_access": False,
    "device_timing": False,
    "channel_calibration": False,
    "listening": False,
    "processor_exposure": False,
    "public_default": False,
    "benchmark_claim": False,
    "quality_claim": False,
    "release_claim": False,
}

def qualification_block() -> Dict[str, Any]:
    return {
        "status": QUALIFICATION_STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualifies": False,
        "missing_result_promoted": False,
        "processor_exposure": False,
        "real_runtime_used": False,
        "real_weights_used": False,
        "quality_claim": False,
        "release_claim": False,
    }


EXACT_BLOCKERS: Tuple[str, ...] = (
    "The catalogued label Beam-TasNet / Beam-Guided TasNet covers two distinct "
    "architectures: Beam-TasNet combines multichannel Conv-TasNet separation "
    "with MVDR, while Beam-Guided TasNet is a separate iterative framework. The "
    "pinned research records neither an exact selected implementation nor an "
    "immutable source revision, checkpoint digest or weight licence, and no "
    "source, checkpoint or runtime for either architecture exists in this "
    "worktree.",
    "No rights-cleared synchronized microphone-array corpus with declared "
    "geometry, channel calibration, timestamp alignment, reference channel, "
    "target/reference directions and clean target images is present. Adjacent "
    "offline and online multichannel WPE fixtures are two-channel synthetic "
    "dereverberation controls, not array recordings and not beamforming or "
    "separation evidence.",
    "No pinned runnable framework or vendor runtime exists in this worktree (no "
    "torch, asteroid, speechbrain, onnxruntime or equivalent is installed), so "
    "even a caller-supplied checkpoint could not be executed here; nothing was "
    "downloaded, installed, loaded or invoked.",
    "No held-out task-matched array scoring, independent scorer, permitted "
    "listening result, measured channel synchronization or geometry "
    "calibration, target-device timing, benchmark or release artifact exists; "
    "therefore no result, including the synthetic fixture diagnostics, may "
    "qualify the candidate.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen architecture identity only after one exact implementation is "
    "selected, its immutable source revision and checkpoint SHA-256/byte count "
    "are recorded, and the checkpoint's weight licence and redistribution terms "
    "are cleared.",
    "Reopen array data only with a rights-cleared synchronized microphone-array "
    "corpus that declares geometry, channel calibration, timestamp alignment, "
    "reference channel, target/reference directions and clean target images.",
    "Reopen runtime admission only with a pinned runnable runtime artifact and "
    "checkpoint whose digests install in the intended environment and whose "
    "distribution and product-use terms are documented.",
    "Reopen qualification only with task-matched held-out array scoring, an "
    "independent scorer, permitted listening, measured channel/geometry and "
    "target-device timing evidence; the synthetic fixture diagnostics can never "
    "substitute for any of these.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "one selected exact architecture identity for the two-name catalogue label",
    "immutable source revision plus checkpoint SHA-256 and byte count",
    "written weight/runtime/training-data and redistribution rights clearance",
    "rights-cleared synchronized microphone-array corpus with geometry and channel calibration",
    "clean target/reference images and a held-out array evaluation split",
    "independent SI-SDR/STOI/leakage scorer and permitted listening",
    "measured channel synchronization, geometry mismatch, channel loss and target-device timing",
    "opt-in provider intake, OFF default, independent review and explicit default/release approval",
)

GATES: Tuple[Dict[str, str], ...] = (
    {
        "id": "RG-01",
        "name": "exact_architecture_identity",
        "status": "blocked",
        "evidence": "The label maps to two architectures and no exact implementation, immutable revision or checkpoint is selected.",
        "reopen": REOPEN_CONDITIONS[0],
    },
    {
        "id": "RG-02",
        "name": "source_and_weights",
        "status": "blocked",
        "evidence": "No source tree, checkpoint, weight digest, byte count, runtime artifact or licence is present or pinned for either architecture.",
        "reopen": REOPEN_CONDITIONS[0],
    },
    {
        "id": "RG-03",
        "name": "array_corpus_and_rights",
        "status": "blocked",
        "evidence": "No synchronized rights-cleared microphone-array corpus, geometry/calibration declaration or clean target images exist.",
        "reopen": REOPEN_CONDITIONS[1],
    },
    {
        "id": "RG-04",
        "name": "task_matched_scoring_and_listening",
        "status": "blocked",
        "evidence": "No held-out array score, independent scorer, leakage/target-damage result or permitted listening exists.",
        "reopen": REOPEN_CONDITIONS[3],
    },
    {
        "id": "RG-05",
        "name": "channel_and_device_timing",
        "status": "blocked",
        "evidence": "Channel synchronization, geometry mismatch, channel loss and target-device timing are unmeasured.",
        "reopen": REOPEN_CONDITIONS[3],
    },
    {
        "id": "RG-06",
        "name": "provider_intake",
        "status": "blocked",
        "evidence": "No opt-in provider, descriptor or catalog entry exists; the package is unregistered and OFF.",
        "reopen": "Reopen only after rights/runtime/parity gates clear and an opt-in provider intake with OFF default and independent exact-head review is approved.",
    },
    {
        "id": "RG-07",
        "name": "public_default_selection",
        "status": "blocked",
        "evidence": "No default selection is proposed or made.",
        "reopen": "Reopen only after provider intake clears and the owner records an explicit default decision with preserving controls.",
    },
    {
        "id": "RG-08",
        "name": "release_approval",
        "status": "blocked",
        "evidence": "No benchmark or release artifact exists; DEFER remains in force until every earlier gate closes.",
        "reopen": "Reopen release only after RG-01 through RG-07 close and a separate release decision records the exact scope, cohort, runtime and rights.",
    },
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "scope": "Pinned research provenance only; not reproduced, not pooled and not used as a threshold.",
    "candidate_matrix_row": (
        "Spatial and speaker,Beam-TasNet / Beam-Guided TasNet,unavailable/blocked,"
        "Exact architecture/checkpoint is unresolved and no synchronized "
        "multichannel target data is staged.,Multichannel WPE; target-speaker "
        "metrics,research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md; "
        "research/voice-enhancement-20261101/agent-transform-space/REPORT.md"
    ),
    "transform_space_row": (
        "Beam-TasNet combines multichannel Conv-TasNet separation and MVDR; "
        "Beam-Guided TasNet is a distinct iterative framework."
    ),
    "spatial_trials_row": (
        "No exact named model resolution/checkpoint/adapter and no local aligned "
        "array mixtures."
    ),
    "survey_cln_07_outcome": (
        "Beam-TasNet combines multichannel Conv-TasNet separation with MVDR, "
        "while Beam-Guided TasNet is a distinct iterative framework"
    ),
    "reported_metric_values": None,
    "disclaimer": (
        "No source-reported numeric quality, array or timing value exists for "
        "this candidate in the pinned ledgers; none is invented or transcribed. "
        "The synthetic fixture numbers below describe this package only."
    ),
}

SIBLING_EVIDENCE: Dict[str, Any] = {
    "survey_cln_07": {
        "path": "docs/task-evidence/survey-cln-07/report.json",
        "component": "beamforming-spatial-filtering-evidence-map",
        "decision": "DEFER",
        "results_pooled": False,
        "use": "Beamforming/spatial-filtering category map and blocked candidate census only.",
    },
    "survey_spk_01": {
        "path": "docs/task-evidence/survey-spk-01/report.json",
        "component": "source-separation-evidence-map",
        "decision": "DEFER",
        "results_pooled": False,
        "use": "Separation category map and blocked neural-separation leads only.",
    },
    "adjacent_wpe": {
        "paths": [
            "docs/task-evidence/offline-multichannel-wpe/report.json",
            "docs/task-evidence/online-multichannel-wpe/report.json",
        ],
        "results_pooled": False,
        "use": "Adjacent two-channel synthetic dereverberation array fixtures only; not beamforming, separation or array-calibration evidence.",
    },
    "note": (
        "Sibling evidence is cited read-only. No sibling metric is copied into, "
        "pooled with or used to qualify this candidate."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "Beam-TasNet, Beam-Guided TasNet, their source trees, checkpoints, weights and runtimes are absent; nothing was downloaded, installed, loaded or invoked.",
    "The candidate label, architecture descriptions, source leads and blocked status are quoted from the pinned research ledgers and merged survey evidence.",
    "The synthetic array fixture, geometry, delays, signals, variants and metrics are generated by stdlib code in reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
    "No torch, asteroid, speechbrain, onnxruntime, numpy or equivalent numerical package is installed or called.",
)


class EvidenceError(ValueError):
    """Fail-closed evidence error."""


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
    if isinstance(value, tuple):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def strict_json_load(path: Path) -> Dict[str, Any]:
    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise EvidenceError("duplicate JSON key in " + path.name + ": " + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise EvidenceError("nonfinite JSON constant in " + path.name + ": " + token)

    try:
        value = json.loads(path.read_text(encoding="utf-8"),
                           object_pairs_hook=pairs, parse_constant=constant)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceError("cannot parse " + path.name + ": " + str(error))
    if not isinstance(value, dict):
        raise EvidenceError("JSON root is not an object: " + path.name)
    return value


# ---------------------------------------------------------------------------
# Board identity gate: stable linked rows only, never the mutable file.
# ---------------------------------------------------------------------------

def board_rows(board: Dict[str, Any]) -> List[Dict[str, str]]:
    wanted = {link["task_id"] for link in BOARD_LINKS}
    tasks = board.get("tasks")
    if not isinstance(tasks, list):
        raise EvidenceError("board tasks is not a list")
    rows = [
        {"id": task["id"], "title": task["title"], "mode": task["mode"]}
        for task in tasks
        if isinstance(task, dict) and task.get("id") in wanted
    ]
    rows.sort(key=lambda row: row["id"])
    if len(rows) != len(wanted):
        found = {row["id"] for row in rows}
        raise EvidenceError("linked board rows missing: " + ",".join(sorted(wanted - found)))
    return rows


def board_projection_sha256(board: Dict[str, Any]) -> str:
    return sha256(canonical_bytes(board_rows(board)))


def load_board() -> Dict[str, Any]:
    return strict_json_load(SOURCE_ROOT / BOARD_PATH)


def check_board(board: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    board = load_board() if board is None else board
    rows = {row["id"]: row for row in board_rows(board)}
    for link in BOARD_LINKS:
        row = rows[link["task_id"]]
        if row["title"] != link["title"] or row["mode"] != link["mode"]:
            raise EvidenceError("linked board identity changed: " + link["task_id"])
    self_row = next(task for task in board["tasks"] if task.get("id") == TASK)
    depends = list(self_row.get("depends_on") or [])
    expected = ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"]
    if sorted(depends) != sorted(expected):
        raise EvidenceError("task dependency identity changed: " + ",".join(depends))
    return {
        "path": BOARD_PATH,
        "mutable_source_hashed": False,
        "projected_fields": ["id", "title", "mode"],
        "depends_on": sorted(depends),
        "rows": board_rows(board),
        "projection_sha256": board_projection_sha256(board),
        "note": (
            "The mutable board file is never hashed into canonical bytes. Only "
            "id/title/mode of the linked rows, plus the stable dependency ids, "
            "are gated here."
        ),
    }


# ---------------------------------------------------------------------------
# Caller-supplied external weight/checkpoint asset boundary.
# ---------------------------------------------------------------------------

def weight_asset_ref(architecture: Optional[str] = None) -> Dict[str, Any]:
    return {
        "architecture": architecture,
        "storage": "external",
        "source_revision": None,
        "checkpoint_id": None,
        "checkpoint_sha256": None,
        "checkpoint_bytes": None,
        "license": None,
        "rights_cleared": False,
        "weights_present": False,
        "runtime_available": False,
        "array_corpus_cleared": False,
        "download_permitted": False,
        "bytes_present": False,
    }


def synthetic_control_ref() -> Dict[str, Any]:
    payload = b"synthetic-admission-control"
    return {
        "architecture": SYNTHETIC_CONTROL_ARCH,
        "storage": "external",
        "source_revision": "0" * 40,
        "checkpoint_id": "synthetic-control.bin",
        "checkpoint_sha256": sha256(payload),
        "checkpoint_bytes": len(payload),
        "license": "Apache-2.0",
        "rights_cleared": True,
        "weights_present": True,
        "runtime_available": True,
        "array_corpus_cleared": True,
        "download_permitted": False,
        "bytes_present": True,
        "not_the_pinned_candidate": True,
    }


def weight_admission(ref: Dict[str, Any]) -> Dict[str, Any]:
    """Fail-closed admission for a caller-supplied external candidate asset."""
    reasons: List[str] = []
    architecture = ref.get("architecture")
    if architecture not in ARCHITECTURE_NAMES + (SYNTHETIC_CONTROL_ARCH,):
        reasons.append("architecture_not_selected")
    revision = ref.get("source_revision")
    if not isinstance(revision, str) or re.fullmatch(r"[0-9a-f]{40}", revision) is None:
        reasons.append("source_revision_unpinned")
    digest = ref.get("checkpoint_sha256")
    size = ref.get("checkpoint_bytes")
    if (not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None
            or not isinstance(size, int) or isinstance(size, bool) or size <= 0):
        reasons.append("checkpoint_unpinned")
    if ref.get("storage") != "external":
        reasons.append("storage_not_external")
    if ref.get("download_permitted") is not False:
        reasons.append("download_flag_invalid")
    if ref.get("bytes_present") is not True or ref.get("weights_present") is not True:
        reasons.append("weights_absent")
    if ref.get("runtime_available") is not True:
        reasons.append("runtime_unavailable")
    if ref.get("rights_cleared") is not True:
        reasons.append("rights_not_cleared")
    if ref.get("array_corpus_cleared") is not True:
        reasons.append("array_corpus_absent")
    return {
        "status": "admitted" if not reasons else "blocked",
        "reason_codes": reasons,
        "download_attempted": False,
        "vendor_runtime_invoked": False,
        "asset_bytes_read": False,
    }


def candidate_architecture_block() -> Dict[str, Any]:
    return {
        "label": CANDIDATE_LABEL,
        "distinct_architectures": [copy.deepcopy(item) for item in ARCHITECTURES],
        "count": len(ARCHITECTURES),
        "selection": None,
        "ambiguous": True,
        "no_architecture_chosen": True,
        "component_evidence_status": "blocked",
    }


# ---------------------------------------------------------------------------
# Deterministic geometry fixture.
# ---------------------------------------------------------------------------

def geometry() -> Dict[str, Any]:
    return {
        "layout": ARRAY_LAYOUT,
        "channels": CHANNELS,
        "reference_channel": REFERENCE_CHANNEL,
        "mic_spacing_m": MIC_SPACING_M,
        "speed_of_sound_mps": SPEED_OF_SOUND_MPS,
        "synchronized": True,
        "target_azimuth_deg": TARGET_AZIMUTH_DEG,
        "interferer_azimuth_deg": INTERFERER_AZIMUTH_DEG,
        "declared": True,
        "measured": False,
        "calibrated": False,
        "device_verified": False,
    }


def channel_delays_samples(azimuth_deg: float) -> List[float]:
    sine = math.sin(math.radians(azimuth_deg))
    return [
        (index * MIC_SPACING_M * sine / SPEED_OF_SOUND_MPS) * SAMPLE_RATE_HZ
        for index in range(CHANNELS)
    ]


def _fractional_delay(signal: Sequence[float], delay_samples: float) -> List[float]:
    n_samples = len(signal)
    output: List[float] = []
    for index in range(n_samples):
        position = index - delay_samples
        base = math.floor(position)
        frac = position - base
        left = signal[base] if 0 <= base < n_samples else 0.0
        right = signal[base + 1] if 0 <= base + 1 < n_samples else 0.0
        output.append(left * (1.0 - frac) + right * frac)
    return output


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def _seed(name: str) -> int:
    return (SEED_BASE + sum((index + 1) * ord(char)
                            for index, char in enumerate(name))) & 0xFFFFFFFF


def _gate(t: float, start: float, end: float, ramp: float) -> float:
    if not (start <= t < end):
        return 0.0
    return max(0.0, min((t - start) / ramp, (end - t) / ramp, 1.0))


def _target_wave(index: int) -> float:
    t = index / SAMPLE_RATE_HZ
    return _gate(t, 0.20, 0.80, 0.02) * (
        0.62 * math.sin(2.0 * math.pi * 213.0 * t)
        + 0.28 * math.sin(2.0 * math.pi * 426.0 * t + 0.7)
        + 0.10 * math.sin(2.0 * math.pi * 639.0 * t + 1.9)
    )


def _interferer_wave(index: int) -> float:
    t = index / SAMPLE_RATE_HZ
    return _gate(t, 0.05, 0.95, 0.05) * (
        0.55 * math.sin(2.0 * math.pi * 317.0 * t + 0.3)
        + 0.30 * math.sin(2.0 * math.pi * 634.0 * t + 1.1)
        + 0.15 * math.sin(2.0 * math.pi * 951.0 * t + 2.3)
    )


def synth_scene(condition: str) -> Dict[str, Any]:
    """Deterministic synchronized two-channel fixture with declared geometry."""
    if condition not in CONDITIONS:
        raise EvidenceError("unknown condition: " + condition)
    target_active = condition in ("target_only", "target_plus_interference", "channel_dropout")
    interferer_active = condition in ("interference_only", "target_plus_interference", "channel_dropout")
    target_base = [0.24 * _target_wave(i) if target_active else 0.0 for i in range(SAMPLES)]
    interferer_base = [
        0.20 * _interferer_wave(i) if interferer_active else 0.0 for i in range(SAMPLES)
    ]
    target_delays = channel_delays_samples(TARGET_AZIMUTH_DEG)
    interferer_delays = channel_delays_samples(INTERFERER_AZIMUTH_DEG)
    target_images = [_fractional_delay(target_base, delay) for delay in target_delays]
    interferer_images = [
        _fractional_delay(interferer_base, delay) for delay in interferer_delays
    ]
    noise_images: List[List[float]] = []
    for channel in range(CHANNELS):
        rng = _lcg(_seed("noise:" + condition + ":" + str(channel)))
        noise_images.append([0.012 * (2.0 * next(rng) - 1.0) for _ in range(SAMPLES)])
    mixtures = [
        [target_images[c][n] + interferer_images[c][n] + noise_images[c][n]
         for n in range(SAMPLES)]
        for c in range(CHANNELS)
    ]
    available = list(range(CHANNELS))
    if condition == "channel_dropout":
        available = [0]
        for images in (target_images, interferer_images, noise_images):
            images[1] = [0.0] * SAMPLES
        mixtures = [
            [target_images[c][n] + interferer_images[c][n] + noise_images[c][n]
             for n in range(SAMPLES)]
            for c in range(CHANNELS)
        ]
    return {
        "condition": condition,
        "channels": CHANNELS,
        "samples": SAMPLES,
        "available_channels": available,
        "reference_channel": REFERENCE_CHANNEL,
        "target_images": target_images,
        "interferer_images": interferer_images,
        "noise_images": noise_images,
        "mixtures": mixtures,
        "target_delays_samples": target_delays,
        "interferer_delays_samples": interferer_delays,
        "geometry": geometry(),
    }


def _linear_combination(scene: Dict[str, Any], key: str, weights: Sequence[float]) -> List[float]:
    images = scene[key]
    return [
        sum(weights[c] * images[c][n] for c in range(CHANNELS))
        for n in range(len(images[0]))
    ]


def _mean_square(values: Sequence[float]) -> float:
    return sum(value * value for value in values) / float(len(values))


def _db(ratio: float) -> float:
    return 10.0 * math.log10(max(ratio, 1e-30))


def _ratio_db(numerator: float, denominator: float) -> Optional[float]:
    if numerator <= 0.0:
        return None
    return _db(numerator / max(denominator, 1e-30))


def _si_sdr_db(target: Sequence[float], estimate: Sequence[float]) -> Optional[float]:
    signal_power = sum(value * value for value in target)
    if signal_power <= 0.0:
        return None
    projection = sum(a * b for a, b in zip(target, estimate))
    scale = projection / signal_power
    target_power = sum((scale * value) ** 2 for value in target)
    residual_power = sum((scale * a - b) ** 2 for a, b in zip(target, estimate))
    if target_power <= 0.0:
        return None
    return _db(target_power / max(residual_power, 1e-30))


def _variant_available(weights: Sequence[float], available: Sequence[int]) -> bool:
    return any(weights[c] != 0.0 for c in available if c < len(weights))


def score_variant(scene: Dict[str, Any], name: str) -> Dict[str, Any]:
    weights = VARIANTS[name]
    if not _variant_available(weights, scene["available_channels"]):
        return {
            "name": name,
            "weights": list(weights),
            "status": "rejected",
            "reason": "channel_unavailable",
            "si_sdr_db": None,
            "target_preservation_db": None,
            "interference_leakage_db": None,
            "noise_gain_db": None,
            "output_rms": 0.0,
            "peak_abs_output": 0.0,
            "clipped_samples": 0,
            "nonfinite_samples": 0,
            "scored_samples": 0,
            "output_digest": None,
        }
    target_component = _linear_combination(scene, "target_images", weights)
    interferer_component = _linear_combination(scene, "interferer_images", weights)
    noise_component = _linear_combination(scene, "noise_images", weights)
    output = [
        target_component[n] + interferer_component[n] + noise_component[n]
        for n in range(scene["samples"])
    ]
    reference = scene["reference_channel"]
    target_reference = scene["target_images"][reference]
    interferer_reference = scene["interferer_images"][reference]
    noise_reference = scene["noise_images"][reference]
    peak = max(abs(value) for value in output)
    return {
        "name": name,
        "weights": list(weights),
        "status": "scored",
        "reason": None,
        "si_sdr_db": _si_sdr_db(target_reference, output),
        "target_preservation_db": _ratio_db(_mean_square(target_component),
                                             _mean_square(target_reference)),
        "interference_leakage_db": _ratio_db(_mean_square(interferer_component),
                                             _mean_square(interferer_reference)),
        "noise_gain_db": _ratio_db(_mean_square(noise_component),
                                   _mean_square(noise_reference)),
        "output_rms": math.sqrt(_mean_square(output)),
        "peak_abs_output": peak,
        "clipped_samples": sum(1 for value in output if abs(value) > 1.0),
        "nonfinite_samples": sum(1 for value in output if not math.isfinite(value)),
        "scored_samples": len(output),
        "output_digest": sha256(canonical_bytes(output)),
    }


def score_variants(scene: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {name: score_variant(scene, name) for name in VARIANTS}


# ---------------------------------------------------------------------------
# Whole-clip multichannel admission boundary.
# ---------------------------------------------------------------------------

def default_config() -> Dict[str, Any]:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "max_clip_samples": MAX_CLIP_SAMPLES,
        "reference_channel": REFERENCE_CHANNEL,
        "array_geometry": geometry(),
        "mode": "synthetic-surrogate",
        "synthetic_surrogate_opt_in": True,
        "weight_reference": weight_asset_ref(),
    }


def validate_config(config: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    expected = default_config()
    for key in ("sample_rate_hz", "channels", "sample_format", "frame_samples",
                "max_clip_samples", "reference_channel"):
        if config.get(key) != expected[key]:
            reasons.append(key + "_mismatch")
    array = config.get("array_geometry")
    if not isinstance(array, dict):
        reasons.append("geometry_missing")
    else:
        if array.get("layout") != ARRAY_LAYOUT:
            reasons.append("geometry_layout_mismatch")
        if array.get("channels") != CHANNELS:
            reasons.append("geometry_channels_mismatch")
        if array.get("mic_spacing_m") != MIC_SPACING_M or not (
                isinstance(array.get("mic_spacing_m"), (int, float))
                and not isinstance(array.get("mic_spacing_m"), bool)
                and array.get("mic_spacing_m") > 0.0):
            reasons.append("geometry_spacing_invalid")
        if array.get("speed_of_sound_mps") != SPEED_OF_SOUND_MPS:
            reasons.append("geometry_speed_of_sound_mismatch")
        if array.get("synchronized") is not True:
            reasons.append("geometry_not_synchronized")
    mode = config.get("mode")
    if mode not in ("synthetic-surrogate", "caller-asset", "synthetic-admission-control"):
        reasons.append("mode_unsupported")
    if mode == "synthetic-surrogate" and config.get("synthetic_surrogate_opt_in") is not True:
        reasons.append("surrogate_opt_in_required")
    if mode in ("caller-asset", "synthetic-admission-control"):
        admission = weight_admission(config.get("weight_reference") or {})
        if admission["status"] != "admitted":
            reasons.append("asset_not_admitted")
    return reasons


def _validate_scene(channels: Any) -> List[List[float]]:
    if isinstance(channels, (str, bytes)) or not isinstance(channels, Sequence):
        raise EvidenceError("scene_type_invalid")
    if len(channels) != CHANNELS:
        raise EvidenceError("channel_count_mismatch")
    lengths = set()
    values: List[List[float]] = []
    for channel in channels:
        if isinstance(channel, (str, bytes)) or not isinstance(channel, Sequence):
            raise EvidenceError("channel_type_invalid")
        items = list(channel)
        if not items:
            raise EvidenceError("scene_empty")
        lengths.add(len(items))
        converted: List[float] = []
        for value in items:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise EvidenceError("sample_type_invalid")
            number = float(value)
            if not math.isfinite(number):
                raise EvidenceError("sample_nonfinite")
            if abs(number) > 8.0:
                raise EvidenceError("sample_out_of_range")
            converted.append(number)
        values.append(converted)
    if len(lengths) != 1:
        raise EvidenceError("ragged_channels")
    length = lengths.pop()
    if length > MAX_CLIP_SAMPLES:
        raise EvidenceError("scene_oversized")
    return values


def _apply_weights(channels: Sequence[Sequence[float]], weights: Sequence[float]) -> List[float]:
    length = len(channels[0])
    return [
        sum(weights[c] * channels[c][n] for c in range(len(channels)))
        for n in range(length)
    ]


def process_scene(channels: Sequence[Sequence[float]]) -> Dict[str, Any]:
    values = _validate_scene(channels)
    # A declared channel is available even when it is silent; channel loss is an
    # explicit fixture/scene declaration, never inferred from zero content.
    available = list(range(len(values)))
    variants: Dict[str, Dict[str, Any]] = {}
    for name, weights in VARIANTS.items():
        if not _variant_available(weights, available):
            variants[name] = {
                "name": name,
                "weights": list(weights),
                "status": "rejected",
                "reason": "channel_unavailable",
                "output_digest": None,
                "output_samples": 0,
            }
            continue
        output = _apply_weights(values, weights)
        variants[name] = {
            "name": name,
            "weights": list(weights),
            "status": "scored",
            "reason": None,
            "output_digest": sha256(canonical_bytes(output)),
            "output_samples": len(output),
        }
    return {
        "input_channels": len(values),
        "input_samples_per_channel": len(values[0]),
        "output_channels": 1,
        "output_samples": len(values[0]),
        "identity_output_digest": variants["identity_passthrough"]["output_digest"],
        "input_digest": sha256(canonical_bytes(values)),
        "variants": variants,
    }


class SpatialSession:
    """One-shot whole-clip multichannel boundary fixture; not a candidate adapter."""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = copy.deepcopy(config or default_config())
        reasons = validate_config(self.config)
        if reasons:
            raise EvidenceError(";".join(reasons))
        self._closed = False
        self._completed = False
        self._calls = 0
        self._last_output_digest: Optional[str] = None

    def process_scene(self, channels: Sequence[Sequence[float]]) -> Dict[str, Any]:
        if self._closed:
            raise EvidenceError("session_closed")
        if self._completed:
            raise EvidenceError("scene_already_complete")
        result = process_scene(channels)
        self._calls += 1
        self._completed = True
        self._last_output_digest = result["identity_output_digest"]
        return result

    def close(self) -> None:
        self._closed = True

    def status_digest(self) -> str:
        return sha256(canonical_bytes({
            "closed": self._closed,
            "completed": self._completed,
            "calls": self._calls,
            "last_output_digest": self._last_output_digest,
        }))

    @property
    def completed(self) -> bool:
        return self._completed

    @property
    def calls(self) -> int:
        return self._calls


def fixture_scene(condition: str = "target_plus_interference") -> List[List[float]]:
    return copy.deepcopy(synth_scene(condition)["mixtures"])


# ---------------------------------------------------------------------------
# Evidence blocks.
# ---------------------------------------------------------------------------

def condition_block(condition: str) -> Dict[str, Any]:
    scene = synth_scene(condition)
    variants = score_variants(scene)
    return {
        "condition": condition,
        "channels": CHANNELS,
        "samples": SAMPLES,
        "reference_channel": REFERENCE_CHANNEL,
        "available_channels": list(scene["available_channels"]),
        "geometry": scene["geometry"],
        "declared_delays_samples": {
            "target": list(scene["target_delays_samples"]),
            "interferer": list(scene["interferer_delays_samples"]),
        },
        "mixture_digest": sha256(canonical_bytes(scene["mixtures"])),
        "reference_channel_digest": sha256(canonical_bytes(
            scene["mixtures"][REFERENCE_CHANNEL])),
        "target_reference_digest": sha256(canonical_bytes(
            scene["target_images"][REFERENCE_CHANNEL])),
        "variants": variants,
        "output_accounting": {
            "input_channels": CHANNELS,
            "input_samples_per_channel": SAMPLES,
            "output_channels": 1,
            "output_samples": SAMPLES,
            "scored_samples": SAMPLES,
            "startup_padding_samples": 0,
            "tail_padding_emitted_samples": 0,
            "flush_required": False,
            "channel_loss_control": condition == "channel_dropout",
            "finding": (
                "Exactly one mono output sample per declared reference-channel "
                "input sample. No streaming, flush or padding behavior is "
                "modelled, and no channel is silently substituted."
            ),
        },
    }


def condition_blocks() -> Dict[str, Dict[str, Any]]:
    return {condition: condition_block(condition) for condition in CONDITIONS}


def config_adverse_cases() -> Dict[str, Dict[str, Any]]:
    cases: Dict[str, Dict[str, Any]] = {}

    def attempt(name: str, mutate) -> None:
        config = default_config()
        mutate(config)
        try:
            session = SpatialSession(config)
            session.close()
            cases[name] = {
                "status": "created",
                "session_created": True,
                "reasons": [],
            }
        except EvidenceError as error:
            cases[name] = {
                "status": "rejected",
                "session_created": False,
                "reasons": str(error).split(";"),
            }

    attempt("wrong_sample_rate", lambda c: c.update(sample_rate_hz=8000))
    attempt("wrong_channels", lambda c: c.update(channels=1))
    attempt("wrong_sample_format", lambda c: c.update(sample_format="s16"))
    attempt("wrong_frame_samples", lambda c: c.update(frame_samples=256))
    attempt("wrong_max_clip_samples", lambda c: c.update(max_clip_samples=8000))
    attempt("reference_channel_out_of_range", lambda c: c.update(reference_channel=2))
    attempt("geometry_missing", lambda c: c.pop("array_geometry"))
    attempt("geometry_not_synchronized",
            lambda c: c["array_geometry"].update(synchronized=False))
    attempt("geometry_spacing_invalid",
            lambda c: c["array_geometry"].update(mic_spacing_m=0.0))
    attempt("surrogate_without_opt_in", lambda c: c.update(synthetic_surrogate_opt_in=False))
    attempt("caller_weights_unavailable", lambda c: c.update(
        mode="caller-asset", weight_reference=weight_asset_ref()))
    attempt("synthetic_weight_admission_control", lambda c: c.update(
        mode="synthetic-admission-control", weight_reference=synthetic_control_ref()))
    return cases


def scene_adverse_cases() -> Dict[str, Any]:
    def attempt(session: SpatialSession, name: str, channels: Any) -> Dict[str, Any]:
        before = session.status_digest()
        try:
            session.process_scene(channels)
            status = "accepted"
        except EvidenceError as error:
            status = "rejected:" + str(error)
        after = session.status_digest()
        return {"status": status, "state_unchanged": before == after}

    cases: Dict[str, Dict[str, Any]] = {}
    session = SpatialSession()
    valid = fixture_scene()
    bad_inputs = {
        "empty_scene": [[], []],
        "channel_count_mismatch": [[0.0] * SAMPLES],
        "ragged_channels": [[0.0] * SAMPLES, [0.0] * (SAMPLES - 1)],
        "oversized_scene": [[0.0] * (MAX_CLIP_SAMPLES + 1) for _ in range(CHANNELS)],
        "nonfinite_sample": [[float("nan")] + [0.0] * (SAMPLES - 1),
                             [0.0] * SAMPLES],
        "infinite_sample": [[float("inf")] + [0.0] * (SAMPLES - 1),
                            [0.0] * SAMPLES],
        "string_sample": [["0.0"] + [0.0] * (SAMPLES - 1), [0.0] * SAMPLES],
        "boolean_sample": [[True] + [0.0] * (SAMPLES - 1), [0.0] * SAMPLES],
        "out_of_range_sample": [[9.0] + [0.0] * (SAMPLES - 1), [0.0] * SAMPLES],
    }
    for name, channels in bad_inputs.items():
        cases[name] = attempt(session, name, channels)

    completed = SpatialSession()
    completed.process_scene(valid)
    cases["second_scene"] = attempt(completed, "second_scene", valid)

    closed = SpatialSession()
    closed.close()
    cases["after_close"] = attempt(closed, "after_close", valid)
    return {
        "cases": cases,
        "state_after_close_unchanged_by_rejected_call":
            cases["after_close"]["state_unchanged"],
    }


def lifecycle_evidence() -> Dict[str, Any]:
    session = SpatialSession()
    first = session.process_scene(fixture_scene())
    second_status = "accepted"
    try:
        session.process_scene(fixture_scene("target_only"))
    except EvidenceError as error:
        second_status = "rejected:" + str(error)
    session.close()
    session.close()
    closed_status = "accepted"
    try:
        session.process_scene(fixture_scene())
    except EvidenceError as error:
        closed_status = "rejected:" + str(error)
    empty_status = "accepted"
    try:
        SpatialSession().process_scene([[], []])
    except EvidenceError as error:
        empty_status = "rejected:" + str(error)
    return {
        "one_scene_completed": first["output_samples"] == SAMPLES,
        "one_call_only": second_status == "rejected:scene_already_complete",
        "close_idempotent": True,
        "zero_length_scene_rejected": empty_status == "rejected:scene_empty",
        "process_after_close": closed_status,
        "incremental_process_api_absent": not hasattr(session, "process"),
        "flush_api_absent": not hasattr(session, "flush"),
        "reset_api_absent": not hasattr(session, "reset"),
        "calls": session.calls,
    }


def spatial_profile() -> Dict[str, Any]:
    return {
        "name": "spatial",
        "profile_source": "plan/swarm/VERIFICATION.md",
        "verification_profile_from_inventory": PROFILE,
        "geometry": geometry(),
        "channel_layout": {
            "channels": CHANNELS,
            "reference_channel": REFERENCE_CHANNEL,
            "layout": ARRAY_LAYOUT,
            "declared_spacing_m": MIC_SPACING_M,
            "synchronized": True,
            "measured": False,
            "calibrated": False,
        },
        "timestamp_calibration": {
            "measured": False,
            "status": "blocked_unmeasured",
            "note": "Only a fixture sample coordinate exists; no device timestamp, drift, offset or channel-sync measurement is made.",
        },
        "source_target_reference_conditions": {
            "target_direction_deg": TARGET_AZIMUTH_DEG,
            "interferer_direction_deg": INTERFERER_AZIMUTH_DEG,
            "reference_channel": REFERENCE_CHANNEL,
            "clean_target_images_synthetic_only": True,
            "real_conditions_present": False,
        },
        "localization_or_activity": {
            "performed": False,
            "status": "not_applicable_no_candidate",
            "note": "Localization is a separate catalogued category and is not estimated here.",
        },
        "extraction": {
            "performed": False,
            "status": "not_performed_no_candidate",
            "note": "That synthetic outputs are linear channel maps is not target extraction.",
        },
        "task_matched_heldout_labels": {
            "present": False,
            "status": "blocked_missing_array_cohort",
        },
        "leakage": "synthetic_fixture_only_not_qualified",
        "target_damage": "synthetic_fixture_only_not_qualified",
        "channel_loss": "synthetic_fixture_only_not_qualified",
        "room_reference_changes": "synthetic_fixture_only_not_qualified",
        "listening": {"status": "not_run"},
        "real_array_corpus": False,
        "real_runtime": False,
        "real_weights": False,
        "device_timing": {
            "measured": False,
            "status": "blocked_unmeasured",
        },
        "whole_clip_requirement": True,
        "note": (
            "The Spatial profile is applied as a blocked checklist. Geometry, "
            "directions and delays are declared fixture constants, not measured "
            "array calibration, and none of the synthetic diagnostics qualifies "
            "the candidate."
        ),
    }


def asset_boundary() -> Dict[str, Any]:
    candidate = weight_asset_ref()
    control = synthetic_control_ref()
    return {
        "readiness": "blocked",
        "reason_codes": weight_admission(candidate)["reason_codes"],
        "asset": candidate,
        "architectures": candidate_architecture_block(),
        "download_attempted": False,
        "asset_bytes_read": False,
        "runtime_available": False,
        "synthetic_admission_control": {
            "status": weight_admission(control)["status"],
            "not_the_pinned_candidate": True,
            "note": (
                "A fully pinned synthetic reference exercises the admission "
                "branch only. It is not Beam-TasNet or Beam-Guided TasNet and "
                "carries no candidate weight."
            ),
        },
    }


def controls_block() -> Dict[str, Any]:
    return {
        "all_present": True,
        "identity": {
            "name": "identity_passthrough",
            "exact_passthrough": True,
            "note": "Reference-channel passthrough; every scored sample is the observed reference channel.",
        },
        "reference_channel": {
            "name": "alternate_reference_channel",
            "note": "Reference-condition control over the non-declared channel; rejected when that channel is absent.",
        },
        "naive_mix": {
            "name": "naive_channel_mean",
            "note": "Unsteered equal channel mean with no delays, steering or beamforming; comb and leakage are recorded, not hidden.",
        },
        "candidate": {
            "name": "synthetic_geometry_fixture",
            "real_candidate": False,
            "note": "Deterministic geometry fixture only; not Beam-TasNet, not Beam-Guided TasNet, not a beamformer or separator.",
        },
    }


def _regressions(blocks: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    for condition, block in blocks.items():
        identity = block["variants"]["identity_passthrough"]
        naive = block["variants"]["naive_channel_mean"]
        for metric in ("si_sdr_db", "target_preservation_db"):
            if identity.get(metric) is None or naive.get(metric) is None:
                continue
            if naive[metric] < identity[metric]:
                regressions.append({
                    "condition": condition,
                    "metric": metric,
                    "better_direction": "higher",
                    "identity_passthrough": identity[metric],
                    "naive_channel_mean": naive[metric],
                    "delta": naive[metric] - identity[metric],
                    "note": "Synthetic fixture regression recorded verbatim; not a candidate result.",
                })
    return regressions


def _core_report() -> Dict[str, Any]:
    blocks = condition_blocks()
    board = check_board()
    candidate_admission = weight_admission(weight_asset_ref())
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "format": copy.deepcopy(FORMAT),
        "boundary": copy.deepcopy(BOUNDARY),
        "claims": copy.deepcopy(CLAIMS),
        "scope": copy.deepcopy(SCOPE),
        "qualification": qualification_block(),
        "candidate_identity": candidate_architecture_block(),
        "spatial_profile": spatial_profile(),
        "conditions": blocks,
        "controls": controls_block(),
        "regressions": _regressions(blocks),
        "regression_assessment": {
            "performed": True,
            "conditions": list(CONDITIONS),
            "finding": (
                "Every paired synthetic delta is reported verbatim. Negative "
                "target-preservation or SI-SDR deltas are listed under "
                "regressions; they describe the fixture only and never a "
                "candidate."
            ),
        },
        "spatial_boundary": {
            "protocol": "caller-supplied external checkpoint plus one complete synchronized multichannel whole clip",
            "processing_mode": "offline_multichannel_whole_clip",
            "incremental_calls_supported": False,
            "streaming_supported": False,
            "flush_required": False,
            "algorithmic_lag_samples": 0,
            "lag_modelled": False,
            "lag_measured": False,
            "clock_id": CLOCK_ID,
            "fixture_epoch_ns": str(FIXTURE_EPOCH_NS),
            "availability_model": "sample-coordinate only; no wall clock, device clock, deadline or channel-sync measurement",
            "geometry": geometry(),
            "reference_channel": REFERENCE_CHANNEL,
            "channel_dropout_control": "condition channel_dropout; alternate reference is rejected, never silently replaced",
            "device_clock_used": False,
            "deadline_measured": False,
            "channel_synchronization_measured": False,
            "geometry_calibration_measured": False,
        },
        "asset_boundary": asset_boundary(),
        "asset_admission": candidate_admission,
        "sibling_evidence": copy.deepcopy(SIBLING_EVIDENCE),
        "adverse": {
            "config_rejections": config_adverse_cases(),
            "scene_cases": scene_adverse_cases(),
            "lifecycle": lifecycle_evidence(),
        },
        "board_link": board,
        "repeatability": {},
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(gate) for gate in GATES],
        "source_reported_context": copy.deepcopy(SOURCE_REPORTED_CONTEXT),
        "tool_provenance": list(TOOL_PROVENANCE),
        "source_pin_paths": sorted(SOURCE_PINS),
        "boundary_pin_paths": sorted(BOUNDARY_PINS),
        "local_file_names": list(LOCAL_FILES),
        "notes": [
            "Every metric in this report is computed on a deterministic synthetic two-channel geometry fixture and describes the fixture only.",
            "No Beam-TasNet or Beam-Guided TasNet source, checkpoint, weight, runtime, array recording, listener or release artifact is used or claimed.",
            "All coordinates are fixture source-sample positions; no device clock, channel-sync, pacing or deadline measurement exists.",
            "The surrogate boundary is whole-clip only and performs no beamforming, steering, mask estimation or target extraction.",
        ],
    }


def build_report() -> Dict[str, Any]:
    digests: List[str] = []
    core: Dict[str, Any] = {}
    for _ in range(3):
        core = _core_report()
        digests.append(sha256(canonical_bytes(core)))
    core["repeatability"] = {
        "count": 3,
        "byte_identical": len(set(digests)) == 1,
        "digests": digests,
        "tested_core": "report without the repeatability block",
    }
    return core


def build_contract() -> Dict[str, Any]:
    board = check_board()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_version": "0.1",
        "task": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "format": copy.deepcopy(FORMAT),
        "boundary": copy.deepcopy(BOUNDARY),
        "claims": copy.deepcopy(CLAIMS),
        "scope": copy.deepcopy(SCOPE),
        "qualification": qualification_block(),
        "candidate_identity": candidate_architecture_block(),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(gate) for gate in GATES],
        "asset": weight_asset_ref(),
        "asset_admission": weight_admission(weight_asset_ref()),
        "surrogate": {
            "kind": "deterministic stdlib two-channel geometry fixture",
            "opt_in_required": True,
            "substitutes_for_candidate": False,
            "weights_used": False,
            "vendor_runtime_used": False,
            "beamforming_or_separation_modelled": False,
            "real_array_data_used": False,
        },
        "qualification": qualification_block(),
        "public_surface": copy.deepcopy(PUBLIC_SURFACE),
        "board_link_projection_sha256": board["projection_sha256"],
        "board_link_rows": board["rows"],
        "board_link": {
            "path": BOARD_PATH,
            "mutable_source_hashed": False,
            "projected_fields": ["id", "title", "mode"],
        },
        "source_pins": {"source:" + key: value for key, value in SOURCE_PINS.items()},
        "boundary_pins": {"worktree:" + key: value for key, value in BOUNDARY_PINS.items()},
        "artifact_pins": {},
    }


def build_adapter() -> Dict[str, Any]:
    return {
        "protocol_version": 1,
        "identity": "beam-tasnet-beam-guided-tasnet-proposal",
        "boundary_identity": "as_asset_v0-external-caller-supplied",
        "input_kind": "synchronized_multichannel_waveform",
        "output_kinds": ["waveform"],
        "tasks": ["CLN-07"],
        "modes": ["offline"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "max_clip_samples": MAX_CLIP_SAMPLES,
        "reference_channel": REFERENCE_CHANNEL,
        "geometry": {
            "layout": ARRAY_LAYOUT,
            "mic_spacing_m": MIC_SPACING_M,
            "synchronized_required": True,
        },
        "candidate_architectures": list(ARCHITECTURE_NAMES),
        "architecture_selected": None,
        "architecture_ambiguous": True,
        "configuration": {
            "asset_required": True,
            "asset_storage": "external",
            "download_permitted": False,
            "whole_clip_only": True,
            "incremental_calls": False,
            "output_length_equals_input": True,
            "streaming_supported": False,
            "beamforming_supported": False,
            "separation_supported": False,
            "channel_loss_fails_closed": True,
        },
        "entrypoint": ["python", "reference.py"],
        "asset_readiness": weight_admission(weight_asset_ref())["status"],
        "real_runtime_used": False,
        "weights_accessed": False,
        "quality_claim": False,
        "registration": {
            "registered": False,
            "enabled_by_default": False,
            "default_selected": False,
            "descriptor_registry_change": False,
            "public_api_abi_change": False,
        },
        "status": STATUS,
        "decision": DECISION,
    }


def build_readiness() -> Dict[str, Any]:
    admission = weight_admission(weight_asset_ref())
    return {
        "schema_id": f"audio-sdk/task-evidence/{SLUG}/readiness/0.1",
        "task": TASK,
        "component": COMPONENT,
        "candidate": CANDIDATE_LABEL,
        "status": "blocked",
        "qualified": False,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "asset_reference": weight_asset_ref(),
        "admission": admission,
        "architecture_ambiguity": candidate_architecture_block(),
        "readiness_conclusion": (
            "The spatial whole-clip boundary is modelled, but the candidate is "
            "not ready to run or qualify: the two-name label still covers two "
            "distinct architectures, no exact source revision, checkpoint, "
            "weight digest or licence is pinned, no synchronized "
            "rights-cleared microphone-array corpus exists, and no pinned "
            "runnable runtime is installed here."
        ),
        "external_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "allowed_now": [
            "synthetic two-channel geometry-boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied checkpoint contract",
        ],
        "not_allowed": [
            "downloading or bundling either architecture, source tree or checkpoint",
            "executing a vendor runtime or publishing its outputs",
            "registering a provider, changing defaults or claiming quality, separation, array or latency results",
        ],
    }
