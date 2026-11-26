# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, standard-library-only evidence for SDK-FULLSUBNET.

This module never loads a model, imports an upstream package, reads audio, runs
inference, scores quality, performs listening, measures a device or produces a
release claim. The exact FullSubNet+ source checkout, checkpoint and runtime are
absent. The module pins stable read-only inputs, proves the fixed absence
probes, exercises a fail-closed synthetic cohort-admission contract and emits
canonical JSON.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT", str(HERE.parents[5]))).resolve()
TASK_PREFIX = "docs/task-evidence/fullsubnet/"

TASK = "SDK-FULLSUBNET"
TASK_TITLE = "FullSubNet+"
COMPONENT_ID = "fullsubnet"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "enhancement"
PROFILE_KEY = "Enhancement"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = "audio-sdk/fullsubnet-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/fullsubnet-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/fullsubnet-report/0.1"
BASE_COMMIT = "77d7800cac82899eb02a8aa55535d00e4faa8946"
BRANCH = "swarm/SDK-FULLSUBNET"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

# ---------------------------------------------------------------------------
# Stable, read-only pins. Source paths are relative to AUDIO_ROOT; boundary
# paths are SDK-worktree relative. Nothing here is executed.
# ---------------------------------------------------------------------------

SOURCE_PINS = {
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-fullsubnet-readiness/REPORT.md":
        "f40029de2299f0042143f7bf5603d874cfc248b36e41aeb08b162e0b051a47c0",
    "research/selected_audio_enhancement_candidates.md":
        "0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946",
    "adapters/fullsubnet-plus/adapter.json":
        "1cc6ffa001f5d73f0f36b64bef3aed9bb0c1ef5d171e684c0c379eb12c64ec66",
    "adapters/fullsubnet-plus/README.md":
        "d7295a4423b899989e5c4ebdf8d8afa7a4928857e3c879fbb99f0be1005a8eee",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
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
}

# Only stable, non-mutable identity fields are projected. ``status``, ``owner``,
# ``claim``, ``review``, ``handoff``, ``blocked_reason`` and
# ``dispatch_priority`` never enter canonical bytes and never gate this package.
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "evidence", "deliverable", "acceptance",
    "write_scope",
)
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "identity/noisy control",
    "established task-matched baseline",
    "paired SI-SDR and STOI",
    "clean-speech preservation, peaks and invalid outputs",
    "authorized listening",
    "alignment, state, memory and measured content/availability timing",
)

# ---------------------------------------------------------------------------
# Exact upstream identity. The code revision is the workspace adapter's pinned
# reference; the model artifact is a Google Drive file with no verified terms,
# immutable revision or digest. Nothing is asserted as locally present.
# ---------------------------------------------------------------------------

SOURCE_REPOSITORY = "https://github.com/RookieJunChen/FullSubNet-plus"
SOURCE_REVISION = "b115416d6e2a983c3724fc77d0cdc3d8896a2855"
SOURCE_LICENSE_SPDX = "Apache-2.0"
SOURCE_LICENSE_TEXT_VERIFIED = False
PAPER_CONTEXT = "ICASSP 2022 FullSubNet+ channel-attention complex-spectrum SE"
CHECKPOINT_HOST = "Google Drive"
CHECKPOINT_FILE_ID = "1UJSt1G0P_aXry-u79LLU_l9tCnNa2u7C"
CHECKPOINT_FILENAME = "best_model.tar"
CHECKPOINT_REVISION = None
CHECKPOINT_SHA256 = None
CHECKPOINT_TERMS = "unresolved"
UPSTREAM_SAMPLE_RATE_HZ = 16_000
N_FFT = 512
WIN_LENGTH = 512
HOP_LENGTH = 256
FREQ_BINS = 257
LOOKAHEAD_FRAMES = 2
MASK_KIND = "complex_crm"
UPSTREAM_RUNTIME = "PyTorch 1.7.1 / torchaudio 0.7 / librosa 0.8 (README sample environment)"
UPSTREAM_CPU_SUPPORT = "source reported, not measured here"
BASELINES = ("DeepFilterNet3", "FastEnhancer")

SOURCE_PROBE_PATHS = (
    "research/voice-enhancement-20261101/repos/fullsubnet-plus",
    "research/voice-enhancement-20261101/repos/FullSubNet-plus",
    "research/fullsubnet-plus",
    "research/FullSubNet-plus",
)
WEIGHTS_PROBE_PATHS = (
    "research/voice-enhancement-20261101/models/fullsubnet-plus",
    "research/voice-enhancement-20261101/models/FullSubNet-plus",
    "research/models/fullsubnet-plus",
)
RUNTIME_PROBE_PATHS = (
    "research/voice-enhancement-20261101/envs/fullsubnet-plus",
    "research/voice-enhancement-20261101/.venv-fullsubnet-plus",
    ".venv-fullsubnet-plus",
)
HOME_PROBE_PATHS = (
    "~/.cache/huggingface/hub/models--RookieJunChen--FullSubNet-plus",
    "~/.venvs/fullsubnet-plus",
    "~/.local/share/fullsubnet-plus",
)
SOURCE_ROOT_REL = "research/voice-enhancement-20261101/repos"
SCOPE_BASE_REFS = ("origin/main", "main")

NON_CLAIMS = [
    "No FullSubNet+ source copy, best_model.tar checkpoint, weight fragment, "
    "config, runtime, corpus, clean reference, enhanced waveform or vendor "
    "result is present, loaded, linked or executed by this package.",
    "No model inference, audio read, audio write, listening, paired SI-SDR or "
    "STOI scoring, clean-speech preservation, peak, alignment, content-delay, "
    "first-output or device-timing measurement is performed.",
    "No real corpus, noisy/clean pair, manual reference, language or speaker "
    "group, condition or held-out split is used here; the local DNS2020 "
    "30-pair set named by the readiness record is not opened or admitted.",
    "No missing, invalid, nonfinite or adverse manifest case qualifies; the "
    "single accepted synthetic schema control is not evidence.",
    "No adjacent DeepFilterNet3, FastEnhancer, CMGAN, GTCRN, DTLN, CoF, "
    "Spiking-FullSubNet, FullSubNet-original or survey result is inherited, "
    "pooled or promoted to FullSubNet+.",
    "No benchmark, quality, latency, resource, streaming, GPU or release claim "
    "is made; DEFER remains in force.",
    "No provider, descriptor, registry, default, public header, ABI, shared "
    "CMake, CI workflow, installed-v0 behavior, board or handoff is changed.",
    "No network access or download is attempted; the absent artifacts and the "
    "Google Drive checkpoint are not fabricated, reconstructed, mirrored or "
    "substituted.",
]

PEER_EVIDENCE = (
    {
        "component": "fastenhancer-base-reference",
        "task": "SDK-FASTENHANCER-BASE-REFERENCE",
        "path": "docs/task-evidence/fastenhancer-base-reference/report.json",
        "class": "named_task_matched_baseline_blocker",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A named comparison baseline in the census/matrix; it has "
                    "its own absent assets and supplies no FullSubNet+ weight, "
                    "runtime or score.",
    },
    {
        "component": "gtcrn-dns3-offline",
        "task": "SDK-GTCRN-DNS3-OFFLINE",
        "path": "docs/task-evidence/gtcrn-dns3-offline/report.json",
        "class": "adjacent_16khz_offline_enhancement_blocker",
        "decision": "DEFER",
        "status": "proposal_only_synthetic_offline_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A separate 16 kHz offline denoiser with its own checkpoint "
                    "and terms; no metric or state behavior transfers.",
    },
    {
        "component": "dtln-onnx",
        "task": "SDK-DTLN-ONNX",
        "path": "docs/task-evidence/dtln-onnx/report.json",
        "class": "adjacent_16khz_streaming_enhancement_blocker",
        "decision": "DEFER",
        "status": "proposal_only_synthetic_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A frame-causal DTLN candidate; its geometry is not the "
                    "FullSubNet+ complex-spectrum 512/256 configuration.",
    },
    {
        "component": "cmgan",
        "task": "SDK-CMGAN",
        "path": "docs/task-evidence/cmgan/report.json",
        "class": "adjacent_enhancement_blocker",
        "decision": "DEFER",
        "status": "proposal_only_synthetic_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A different 16 kHz enhancement model with synthetic "
                    "mechanism evidence only.",
    },
    {
        "component": "cof-denoising-checkpoints",
        "task": "SDK-COF-DENOISING-CHECKPOINTS",
        "path": "docs/task-evidence/cof-denoising-checkpoints/report.json",
        "class": "adjacent_checkpoint_blocker",
        "decision": "DEFER",
        "status": "incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "A merged unverified-checkpoint blocker; its source "
                    "supplies the merge-base scope-gate pattern only, not any "
                    "FullSubNet+ asset or result.",
    },
    {
        "component": "survey-cln-01",
        "task": "SDK-SURVEY-CLN-01",
        "path": "docs/task-evidence/survey-cln-01/report.json",
        "class": "merged_survey_map",
        "decision": "DEFER",
        "status": "proposal_only_survey_incomplete",
        "admitted_as_result": False,
        "inherited_metrics": False,
        "boundary": "The merged survey records background-noise suppression "
                    "coverage only; it supplies no FullSubNet+ checkpoint, "
                    "runtime, cohort or measured result.",
    },
)

ENHANCEMENT_REQUIREMENTS = (
    {
        "id": "ENH-01",
        "requirement": "Run an identity/noisy control and an established "
                       "task-matched baseline.",
        "status": "blocked",
        "evidence": "No deterministic identity/noisy control or DeepFilterNet3/"
                    "FastEnhancer baseline output exists on the exact "
                    "FullSubNet+ source, checkpoint and runtime.",
    },
    {
        "id": "ENH-02",
        "requirement": "Score paired SI-SDR and STOI where permitted clean "
                       "references exist.",
        "status": "blocked",
        "evidence": "No rights-cleared paired noisy/clean cohort and no "
                    "SI-SDR/STOI measurement exists.",
    },
    {
        "id": "ENH-03",
        "requirement": "Measure clean-speech preservation.",
        "status": "blocked",
        "evidence": "No clean-input preservation measurement, spectral or "
                    "content diagnostic exists.",
    },
    {
        "id": "ENH-04",
        "requirement": "Measure peaks and invalid outputs.",
        "status": "blocked",
        "evidence": "No output peak, clipping, nonfinite or invalid-value "
                    "record exists; the upstream peak-normalized 16-bit export "
                    "is not copied into a float path here.",
    },
    {
        "id": "ENH-05",
        "requirement": "For unpaired speech use a separately labeled "
                       "predictive screen or authorized listening.",
        "status": "blocked",
        "evidence": "No predictive screen and no authorized listening "
                    "protocol or panel exists.",
    },
    {
        "id": "ENH-06",
        "requirement": "Report alignment and content delay.",
        "status": "blocked",
        "evidence": "No impulse, speech-alignment or content-delay "
                    "measurement exists for the exact runtime; the 2-frame "
                    "look-ahead is an upstream configuration value only.",
    },
    {
        "id": "ENH-07",
        "requirement": "Report state, memory and measured content/availability "
                       "timing for the exact runtime.",
        "status": "blocked",
        "evidence": "No chunk/state behavior, memory, content timing, "
                    "availability timing or resource record exists on the "
                    "reproduced runtime.",
    },
    {
        "id": "ENH-08",
        "requirement": "Keep corpus rights, clean-reference permission and "
                       "output use as independent gates.",
        "status": "blocked",
        "evidence": "Code, weight, training-data, corpus, clean-reference and "
                    "derivative-output terms are unresolved.",
    },
)


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


def parse_strict_json_text(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("invalid_utf8") from error
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


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
    board = AUDIO_ROOT / BOARD_TASK_ROW if path is None else Path(path)
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
        "title": TASK_TITLE,
        "mode": MODE,
        "repository": REPOSITORY,
        "component": COMPONENT_ID,
    }


# ---------------------------------------------------------------------------
# Fixed absence probes.
# ---------------------------------------------------------------------------


def _workspace_rows(paths: tuple[str, ...], kind: str) -> list[dict]:
    rows: list[dict] = []
    for relative in paths:
        present = ((AUDIO_ROOT / relative).exists()
                   or (WORKTREE / relative).exists())
        if present:
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({
            "path": relative,
            "kind": kind,
            "present": False,
            "searched_workspace": True,
            "searched_sdk_worktree": True,
        })
    return rows


def _home_rows(paths: tuple[str, ...]) -> list[dict]:
    rows: list[dict] = []
    for relative in paths:
        path = Path(os.path.expanduser(relative))
        if path.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({
            "path": relative,
            "kind": "home",
            "present": False,
            "searched_home_cache": True,
        })
    return rows


def source_probe() -> dict:
    return {
        "status": "blocked_exact_source_absent",
        "present": False,
        "executed": False,
        "official_repository": SOURCE_REPOSITORY,
        "pinned_revision": SOURCE_REVISION,
        "pinned_revision_reference": "adapters/fullsubnet-plus/adapter.json",
        "revision_is_reference_only": True,
        "independent_checkout_verified_here": False,
        "license_spdx_reported": SOURCE_LICENSE_SPDX,
        "license_text_present": False,
        "license_text_verified": False,
        "source_root": SOURCE_ROOT_REL,
        "source_root_present": (AUDIO_ROOT / SOURCE_ROOT_REL).is_dir(),
        "candidates": _workspace_rows(SOURCE_PROBE_PATHS, "source"),
    }


def weights_probe() -> dict:
    home_cache = ("~/.cache/huggingface/hub/"
                  "models--RookieJunChen--FullSubNet-plus")
    cache_path = Path(os.path.expanduser(home_cache))
    if cache_path.exists():
        raise ValueError("artifact_present_reopen_required:" + home_cache)
    return {
        "status": "blocked_exact_checkpoint_absent",
        "pinned_model_present": False,
        "admitted_model": None,
        "present_file_count": 0,
        "host": CHECKPOINT_HOST,
        "file_id": CHECKPOINT_FILE_ID,
        "filename": CHECKPOINT_FILENAME,
        "revision": CHECKPOINT_REVISION,
        "sha256": CHECKPOINT_SHA256,
        "bytes": None,
        "weight_terms": CHECKPOINT_TERMS,
        "download_attempted": False,
        "model_variant_requirement":
            "the caller-selected official best_model.tar from RookieJunChen/"
            "FullSubNet-plus at an immutable artifact identity; no substitute "
            "FullSubNet, Spiking-FullSubNet or converted third-party checkpoint "
            "is admissible",
        "candidates": _workspace_rows(WEIGHTS_PROBE_PATHS, "weights"),
        "hf_cache": {
            "path": home_cache,
            "present": False,
            "admitted": False,
            "opened": False,
        },
        "files": [
            {"kind": "checkpoint_best_model_tar", "present": False,
             "admitted": False},
            {"kind": "inference_config_toml", "present": False,
             "admitted": False},
            {"kind": "weight_terms_or_model_card", "present": False,
             "admitted": False},
            {"kind": "upstream_license_text", "present": False,
             "admitted": False},
        ],
    }


def runtime_probe() -> dict:
    return {
        "status": "blocked_pinned_runtime_absent",
        "pinned_runtime_present": False,
        "pinned_runtime_complete": False,
        "pinned_runtime_version_verified": False,
        "package_lock_present": False,
        "imported_or_executed": False,
        "upstream_runtime_reference": UPSTREAM_RUNTIME,
        "upstream_cpu_support": UPSTREAM_CPU_SUPPORT,
        "required_runtime": "caller-supplied locked interpreter and package "
                            "set matching the pinned FullSubNet+ revision, with "
                            "an offline load path; the exact torch/torchaudio "
                            "versions and host profile are not asserted here",
        "candidates": _workspace_rows(RUNTIME_PROBE_PATHS, "runtime"),
        "home_candidates": _home_rows(
            ("~/.venvs/fullsubnet-plus", "~/.local/share/fullsubnet-plus")),
    }


def absence_probes() -> list[dict]:
    rows = []
    rows.extend(_workspace_rows(SOURCE_PROBE_PATHS, "source"))
    rows.extend(_workspace_rows(WEIGHTS_PROBE_PATHS, "weights"))
    rows.extend(_workspace_rows(RUNTIME_PROBE_PATHS, "runtime"))
    rows.extend(_home_rows(HOME_PROBE_PATHS))
    return rows


def absence_summary(probes: list[dict]) -> dict:
    return {
        "probe_count": len(probes),
        "present_count": sum(1 for row in probes
                             if row.get("present") is not False),
        "all_probes_absent": all(row.get("present") is False for row in probes),
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "source_or_runtime_imported": False,
    }


# ---------------------------------------------------------------------------
# Fail-closed synthetic enhancement-cohort admission contract.
# ---------------------------------------------------------------------------

MANIFEST_SCHEMA_ID = "audio-sdk/fullsubnet-enhancement-cohort/0.1"
MANIFEST_TOP_KEYS = (
    "schema_id", "cohort_id", "source", "weights", "runtime", "geometry",
    "corpus", "conditions", "outcomes", "rights",
)
MAX_MANIFEST_FILES = 32
MAX_MANIFEST_FILE_BYTES = 8 * 1024 * 1024 * 1024
MAX_CORPUS_ITEMS = 10_000
MAX_PACKAGES = 128
MAX_DURATION_MS = 3_600_000
ADMISSIBLE_SAMPLE_RATES = (16_000,)
GEOMETRY_FIELDS = (
    "sample_rate_hz", "n_fft", "win_length", "hop_length", "lookahead_frames",
    "mask_kind",
)
GEOMETRY_EXPECTED = {
    "sample_rate_hz": UPSTREAM_SAMPLE_RATE_HZ,
    "n_fft": N_FFT,
    "win_length": WIN_LENGTH,
    "hop_length": HOP_LENGTH,
    "lookahead_frames": LOOKAHEAD_FRAMES,
    "mask_kind": MASK_KIND,
}
CONDITION_KEYS = (
    "identity_noisy_control", "task_matched_baseline", "clean_preservation",
    "peaks_and_invalid_outputs", "unpaired_screen", "authorized_listening",
    "alignment", "content_delay", "availability_timing",
)
OUTCOME_KEYS = (
    "si_sdr", "stoi", "clean_preservation", "peak_and_invalid", "listening",
    "alignment", "timing", "memory", "uncertainty",
)
RIGHT_KEYS = (
    "weights_terms", "training_data_provenance", "corpus_rights",
    "clean_reference_permission", "output_use", "redistribution",
)
UNRESOLVED_VALUES = {
    "unknown", "pending", "unspecified", "not specified", "not-specified",
    "tbd", "none", "null", "n/a", "noassertion",
}


class _Invalid(Exception):
    def __init__(self, code: str, field: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.field = field


def _field(prefix: str, name: str) -> str:
    return prefix + "." + name if prefix else name


def _exact_object(value: Any, fields: tuple[str, ...], prefix: str) -> dict:
    if not isinstance(value, dict):
        raise _Invalid("not_object", prefix or "root")
    missing = [name for name in fields if name not in value]
    if missing:
        raise _Invalid("missing_field", _field(prefix, missing[0]))
    unknown = sorted(name for name in value if name not in fields)
    if unknown:
        raise _Invalid("unknown_field", _field(prefix, unknown[0]))
    return value


def _text(value: Any, field: str, limit: int = 240) -> None:
    if not isinstance(value, str):
        raise _Invalid("invalid_text", field)
    if not value.strip():
        raise _Invalid("empty_text", field)
    if len(value) > limit:
        raise _Invalid("out_of_range", field)
    if any(ord(character) < 32 for character in value):
        raise _Invalid("invalid_text", field)
    if value.strip().lower() in UNRESOLVED_VALUES:
        raise _Invalid("unresolved_value", field)


def _slug(value: Any, field: str) -> None:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise _Invalid("invalid_slug", field)


def _sha(value: Any, field: str) -> None:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise _Invalid("invalid_sha256", field)


def _hex40(value: Any, field: str) -> None:
    if not isinstance(value, str) or not HEX40.fullmatch(value):
        raise _Invalid("invalid_revision", field)


def _version(value: Any, field: str) -> None:
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        raise _Invalid("invalid_version", field)


def _safe_relative(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 240:
        raise _Invalid("unsafe_path", field)
    if value.startswith("/") or "\\" in value or ":" in value:
        raise _Invalid("unsafe_path", field)
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise _Invalid("unsafe_path", field)


def _bounded_int(value: Any, low: int, high: int, field: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise _Invalid("invalid_integer", field)
    if value < low or value > high:
        raise _Invalid("out_of_range", field)


def _boolean(value: Any, field: str) -> None:
    if not isinstance(value, bool):
        raise _Invalid("invalid_boolean", field)


def _list(value: Any, field: str, low: int, high: int) -> list:
    if not isinstance(value, list):
        raise _Invalid("not_list", field)
    if len(value) < low:
        raise _Invalid("missing_required_value", field)
    if len(value) > high:
        raise _Invalid("out_of_range", field)
    return value


def _sorted_unique(items: list[dict], key: str, field: str) -> None:
    keys = [item[key] for item in items]
    if len(set(keys)) != len(keys):
        raise _Invalid("duplicate_value", field)
    if keys != sorted(keys):
        raise _Invalid("noncanonical_order", field)


def _reject(code: str, field: str = "") -> dict:
    return {"status": "rejected", "code": code, "field": field}


def _accept(checks: int) -> dict:
    return {"status": "accepted", "checks": checks, "qualifies": False}


def _require_true_map(document: Any, keys: tuple[str, ...],
                      prefix: str) -> int:
    value = _exact_object(document, keys, prefix)
    checks = 0
    for name in keys:
        _boolean(value[name], prefix + "." + name)
        if not value[name]:
            code = "rights_not_cleared" if prefix == "rights" else \
                "missing_required_value"
            raise _Invalid(code, prefix + "." + name)
        checks += 1
    return checks


def _validate_geometry(document: Any) -> int:
    geometry = _exact_object(document, GEOMETRY_FIELDS, "geometry")
    for name in GEOMETRY_FIELDS:
        value = geometry[name]
        if name == "mask_kind":
            _text(value, "geometry.mask_kind", 40)
        else:
            _bounded_int(value, 0, 1_000_000, "geometry." + name)
        if value != GEOMETRY_EXPECTED[name]:
            raise _Invalid("geometry_mismatch", "geometry." + name)
    return len(GEOMETRY_FIELDS)


def validate_manifest(document: Any) -> dict:
    checks = 0
    if not isinstance(document, dict):
        return _reject("manifest_not_object", "")
    try:
        _exact_object(document, MANIFEST_TOP_KEYS, "")
        checks += 1
        if document["schema_id"] != MANIFEST_SCHEMA_ID:
            raise _Invalid("invalid_schema_id", "schema_id")
        checks += 1
        _slug(document["cohort_id"], "cohort_id")
        checks += 1

        source_fields = ("repository", "revision", "license_spdx",
                         "license_sha256")
        source = _exact_object(document["source"], source_fields, "source")
        _text(source["repository"], "source.repository")
        _hex40(source["revision"], "source.revision")
        _text(source["license_spdx"], "source.license_spdx", 80)
        _sha(source["license_sha256"], "source.license_sha256")
        checks += 5

        weights_fields = ("model_id", "revision", "files", "terms_reviewed")
        weights = _exact_object(document["weights"], weights_fields, "weights")
        _text(weights["model_id"], "weights.model_id")
        _hex40(weights["revision"], "weights.revision")
        _boolean(weights["terms_reviewed"], "weights.terms_reviewed")
        files = _list(weights["files"], "weights.files", 1,
                      MAX_MANIFEST_FILES)
        for index, item in enumerate(files):
            prefix = "weights.files[" + str(index) + "]"
            _exact_object(item, ("path", "sha256", "bytes"), prefix)
            _safe_relative(item["path"], prefix + ".path")
            _sha(item["sha256"], prefix + ".sha256")
            _bounded_int(item["bytes"], 1, MAX_MANIFEST_FILE_BYTES,
                         prefix + ".bytes")
            checks += 3
        _sorted_unique(files, "path", "weights.files")
        checks += 4
        if not weights["terms_reviewed"]:
            raise _Invalid("rights_not_cleared", "weights.terms_reviewed")

        runtime_fields = ("python_version", "device", "lock_sha256",
                          "offline_load", "packages")
        runtime = _exact_object(document["runtime"], runtime_fields, "runtime")
        _version(runtime["python_version"], "runtime.python_version")
        _text(runtime["device"], "runtime.device", 120)
        _sha(runtime["lock_sha256"], "runtime.lock_sha256")
        _boolean(runtime["offline_load"], "runtime.offline_load")
        packages = _list(runtime["packages"], "runtime.packages", 1,
                         MAX_PACKAGES)
        for index, item in enumerate(packages):
            prefix = "runtime.packages[" + str(index) + "]"
            _exact_object(item, ("name", "version"), prefix)
            _text(item["name"], prefix + ".name", 120)
            _text(item["version"], prefix + ".version", 120)
            checks += 2
        _sorted_unique(packages, "name", "runtime.packages")
        checks += 4
        if not runtime["offline_load"]:
            raise _Invalid("non_offline_runtime", "runtime.offline_load")

        checks += _validate_geometry(document["geometry"])

        corpus = _list(document["corpus"], "corpus", 1, MAX_CORPUS_ITEMS)
        for index, item in enumerate(corpus):
            prefix = "corpus[" + str(index) + "]"
            _exact_object(item, ("id", "noisy_sha256", "clean_sha256",
                                 "sample_rate_hz", "duration_ms", "consent",
                                 "permitted_use", "split"), prefix)
            _slug(item["id"], prefix + ".id")
            _sha(item["noisy_sha256"], prefix + ".noisy_sha256")
            _sha(item["clean_sha256"], prefix + ".clean_sha256")
            _bounded_int(item["sample_rate_hz"], 8_000, 192_000,
                         prefix + ".sample_rate_hz")
            if item["sample_rate_hz"] not in ADMISSIBLE_SAMPLE_RATES:
                raise _Invalid("out_of_range", prefix + ".sample_rate_hz")
            _bounded_int(item["duration_ms"], 1, MAX_DURATION_MS,
                         prefix + ".duration_ms")
            _boolean(item["consent"], prefix + ".consent")
            _text(item["permitted_use"], prefix + ".permitted_use", 120)
            if item["split"] not in ("dev", "test", "heldout"):
                raise _Invalid("invalid_split", prefix + ".split")
            if not item["consent"]:
                raise _Invalid("rights_not_cleared", prefix + ".consent")
            checks += 8
        _sorted_unique(corpus, "id", "corpus")
        checks += 1

        checks += _require_true_map(document["conditions"], CONDITION_KEYS,
                                    "conditions")
        checks += _require_true_map(document["outcomes"], OUTCOME_KEYS,
                                    "outcomes")
        checks += _require_true_map(document["rights"], RIGHT_KEYS, "rights")
    except _Invalid as error:
        return _reject(error.code, error.field)
    return _accept(checks)


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "fullsubnet-synthetic-schema-control",
        "source": {
            "repository": SOURCE_REPOSITORY,
            "revision": SOURCE_REVISION,
            "license_spdx": SOURCE_LICENSE_SPDX,
            "license_sha256": "1" * 64,
        },
        "weights": {
            "model_id": "fullsubnet-plus-synthetic-control",
            "revision": "2" * 40,
            "files": [
                {
                    "path": "controls/best_model.tar",
                    "sha256": "3" * 64,
                    "bytes": 1024,
                }
            ],
            "terms_reviewed": True,
        },
        "runtime": {
            "python_version": "3.12.16",
            "device": "synthetic-cpu-control",
            "lock_sha256": "4" * 64,
            "offline_load": True,
            "packages": [{"name": "torch", "version": "1.7.1"}],
        },
        "geometry": dict(GEOMETRY_EXPECTED),
        "corpus": [
            {
                "id": "pair-01",
                "noisy_sha256": "5" * 64,
                "clean_sha256": "6" * 64,
                "sample_rate_hz": 16_000,
                "duration_ms": 1000,
                "consent": True,
                "permitted_use": "synthetic-schema-control",
                "split": "dev",
            }
        ],
        "conditions": {name: True for name in CONDITION_KEYS},
        "outcomes": {name: True for name in OUTCOME_KEYS},
        "rights": {name: True for name in RIGHT_KEYS},
    }


def _mutation_case(case_id: str, mutate: Any, code: str) -> dict:
    manifest = copy.deepcopy(_manifest_control())
    mutate(manifest)
    result = validate_manifest(manifest)
    if result["status"] != "rejected" or result["code"] != code:
        raise ValueError("mutation_case_did_not_reject:" + case_id + ":" +
                         str(result))
    return _case_row(case_id, result, False)


def _raw_case(case_id: str, raw: str, code: str) -> dict:
    try:
        loads_strict(raw)
    except ValueError as error:
        observed = str(error).split(":", 1)[0]
        if observed != code:
            raise ValueError("raw_case_code_mismatch:" + case_id + ":" +
                             observed) from error
        return _case_row(case_id, _reject(observed), False)
    raise ValueError("raw_case_did_not_reject:" + case_id)


def _case_row(case_id: str, result: dict, synthetic: bool,
              accepted: bool = False) -> dict:
    return {
        "id": case_id,
        "status": "accepted" if accepted else result["status"],
        "code": result.get("code", "none") if not accepted else "none",
        "field": result.get("field", ""),
        "qualifies": False,
        "state_unchanged": not accepted,
        "synthetic_schema_control": synthetic,
    }


def admission_controls() -> dict:
    accepted = _case_row("accepted-schema-control",
                         validate_manifest(_manifest_control()), True,
                         accepted=True)
    cases = [accepted]
    cases.append(_case_row("root-list",
                           validate_manifest(["not", "a", "manifest"]), False))
    cases.append(_case_row("root-null", validate_manifest(None), False))
    cases.append(_raw_case(
        "duplicate-json-key",
        '{"schema_id":"audio-sdk/fullsubnet-enhancement-cohort/0.1",'
        '"schema_id":"duplicate"}',
        "duplicate_json_key"))
    cases.append(_raw_case(
        "nonfinite-nan",
        '{"schema_id":"audio-sdk/fullsubnet-enhancement-cohort/0.1",'
        '"value":NaN}',
        "nonfinite_json"))
    cases.append(_raw_case(
        "nonfinite-infinity",
        '{"schema_id":"audio-sdk/fullsubnet-enhancement-cohort/0.1",'
        '"value":Infinity}',
        "nonfinite_json"))
    cases.append(_mutation_case(
        "missing-source", lambda m: m.pop("source"), "missing_field"))
    cases.append(_mutation_case(
        "unknown-top-key", lambda m: m.update({"extra": True}),
        "unknown_field"))
    cases.append(_mutation_case(
        "invalid-source-revision",
        lambda m: m["source"].update({"revision": "abc"}), "invalid_revision"))
    cases.append(_mutation_case(
        "invalid-license-sha",
        lambda m: m["source"].update({"license_sha256": "xyz"}),
        "invalid_sha256"))
    cases.append(_mutation_case(
        "empty-weight-files",
        lambda m: m["weights"].update({"files": []}),
        "missing_required_value"))
    cases.append(_mutation_case(
        "unsorted-weight-files",
        lambda m: m["weights"].update({"files": [
            {"path": "b/model.tar", "sha256": "6" * 64, "bytes": 2},
            {"path": "a/model.tar", "sha256": "7" * 64, "bytes": 1},
        ]}),
        "noncanonical_order"))
    cases.append(_mutation_case(
        "duplicate-weight-path",
        lambda m: m["weights"]["files"].append(
            dict(m["weights"]["files"][0])),
        "duplicate_value"))
    cases.append(_mutation_case(
        "traversal-weight-path",
        lambda m: m["weights"]["files"][0].update(
            {"path": "../best_model.tar"}),
        "unsafe_path"))
    cases.append(_mutation_case(
        "boolean-byte-count",
        lambda m: m["weights"]["files"][0].update({"bytes": True}),
        "invalid_integer"))
    cases.append(_mutation_case(
        "zero-byte-count",
        lambda m: m["weights"]["files"][0].update({"bytes": 0}),
        "out_of_range"))
    cases.append(_mutation_case(
        "missing-runtime-lock",
        lambda m: m["runtime"].pop("lock_sha256"), "missing_field"))
    cases.append(_mutation_case(
        "empty-runtime-device",
        lambda m: m["runtime"].update({"device": "  "}), "empty_text"))
    cases.append(_mutation_case(
        "non-offline-runtime",
        lambda m: m["runtime"].update({"offline_load": False}),
        "non_offline_runtime"))
    cases.append(_mutation_case(
        "missing-geometry",
        lambda m: m.pop("geometry"), "missing_field"))
    cases.append(_mutation_case(
        "wrong-sample-rate-geometry",
        lambda m: m["geometry"].update({"sample_rate_hz": 48_000}),
        "geometry_mismatch"))
    cases.append(_mutation_case(
        "wrong-hop-geometry",
        lambda m: m["geometry"].update({"hop_length": 128}),
        "geometry_mismatch"))
    cases.append(_mutation_case(
        "wrong-mask-geometry",
        lambda m: m["geometry"].update({"mask_kind": "magnitude_irm"}),
        "geometry_mismatch"))
    cases.append(_mutation_case(
        "empty-corpus", lambda m: m["corpus"].clear(),
        "missing_required_value"))
    cases.append(_mutation_case(
        "unsorted-corpus",
        lambda m: m["corpus"].append(dict(
            m["corpus"][0], id="pair-00", noisy_sha256="8" * 64)),
        "noncanonical_order"))
    cases.append(_mutation_case(
        "duplicate-corpus-id",
        lambda m: m["corpus"].append(dict(
            m["corpus"][0], noisy_sha256="8" * 64)),
        "duplicate_value"))
    cases.append(_mutation_case(
        "invalid-corpus-sample-rate",
        lambda m: m["corpus"][0].update({"sample_rate_hz": 44100}),
        "out_of_range"))
    cases.append(_mutation_case(
        "zero-duration",
        lambda m: m["corpus"][0].update({"duration_ms": 0}),
        "out_of_range"))
    cases.append(_mutation_case(
        "invalid-clean-sha",
        lambda m: m["corpus"][0].update({"clean_sha256": "xyz"}),
        "invalid_sha256"))
    cases.append(_mutation_case(
        "unconsented-corpus-item",
        lambda m: m["corpus"][0].update({"consent": False}),
        "rights_not_cleared"))
    cases.append(_mutation_case(
        "unresolved-permitted-use",
        lambda m: m["corpus"][0].update({"permitted_use": "unknown"}),
        "unresolved_value"))
    cases.append(_mutation_case(
        "invalid-split",
        lambda m: m["corpus"][0].update({"split": "train"}),
        "invalid_split"))
    cases.append(_mutation_case(
        "missing-condition",
        lambda m: m["conditions"].pop("identity_noisy_control"),
        "missing_field"))
    cases.append(_mutation_case(
        "false-condition",
        lambda m: m["conditions"].update({"task_matched_baseline": False}),
        "missing_required_value"))
    cases.append(_mutation_case(
        "missing-outcome",
        lambda m: m["outcomes"].pop("si_sdr"), "missing_field"))
    cases.append(_mutation_case(
        "false-right",
        lambda m: m["rights"].update({"output_use": False}),
        "rights_not_cleared"))
    cases.append(_mutation_case(
        "duplicate-package-name",
        lambda m: m["runtime"]["packages"].append(
            {"name": "torch", "version": "1.7.2"}),
        "duplicate_value"))
    cases.append(_mutation_case(
        "unreviewed-weight-terms",
        lambda m: m["weights"].update({"terms_reviewed": False}),
        "rights_not_cleared"))

    rejected = [case for case in cases if case["status"] == "rejected"]
    accepted_cases = [case for case in cases if case["status"] == "accepted"]
    summary = {
        "case_count": len(cases),
        "rejected_count": len(rejected),
        "accepted_schema_controls": len(accepted_cases),
        "qualifying_results": 0,
        "state_advanced_on_rejection": False,
        "accepted_control_qualifies": False,
        "all_adverse_cases_rejected": len(rejected) == len(cases) -
        len(accepted_cases),
        "runtime_invoked": False,
        "weights_loaded": False,
        "audio_read": False,
        "inference_performed": False,
    }
    return {"cases": cases, "controls": admission_contract_block(),
            "summary": summary}


def admission_contract_block() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "contract_id": "audio-sdk/fullsubnet-enhancement-cohort-contract/0.1",
        "required_top_level_fields": list(MANIFEST_TOP_KEYS),
        "condition_keys": list(CONDITION_KEYS),
        "outcome_keys": list(OUTCOME_KEYS),
        "right_keys": list(RIGHT_KEYS),
        "geometry_fields": list(GEOMETRY_FIELDS),
        "geometry_expected": dict(GEOMETRY_EXPECTED),
        "admissible_sample_rates_hz": list(ADMISSIBLE_SAMPLE_RATES),
        "max_files": MAX_MANIFEST_FILES,
        "max_file_bytes": MAX_MANIFEST_FILE_BYTES,
        "max_corpus_items": MAX_CORPUS_ITEMS,
        "max_duration_ms": MAX_DURATION_MS,
        "unknown_fields_rejected": True,
        "duplicate_keys_rejected": True,
        "nonfinite_rejected": True,
        "floats_rejected": True,
        "sorted_unique_required": True,
        "unresolved_values_rejected": True,
        "accepted_control_is_synthetic_only": True,
        "accepted_control_qualifies": False,
        "runtime_or_weights_invoked": False,
    }


# ---------------------------------------------------------------------------
# Report blocks.
# ---------------------------------------------------------------------------


def required_artifacts() -> list[dict]:
    rows = [
        ("ART-01", "source_snapshot",
         "The exact RookieJunChen/FullSubNet-plus source checkout at immutable "
         "40-hex commit b115416d6e2a983c3724fc77d0cdc3d8896a2855, with the "
         "reviewed Apache-2.0 license text bytes and a per-file SHA-256 "
         "manifest from a reviewable local tree."),
        ("ART-02", "checkpoint_bundle",
         "The official best_model.tar checkpoint from the authors' Google "
         "Drive link (file ID 1UJSt1G0P_aXry-u79LLU_l9tCnNa2u7C) at an "
         "immutable artifact identity, with byte count and SHA-256, the "
         "config/inference.toml and separately reviewed weight terms or model "
         "card. No substitute FullSubNet variant is admissible."),
        ("ART-03", "runtime_lock",
         "A reproducible isolated runtime with exact interpreter and package "
         "versions, an offline load path, a lock SHA-256 and a recorded host "
         "profile; the upstream sample environment is PyTorch 1.7.1, "
         "torchaudio 0.7 and librosa 0.8."),
        ("ART-04", "rights_bundle",
         "Reviewed weight terms, training-data provenance, corpus rights, "
         "clean-reference permission, output use and redistribution for the "
         "exact source and checkpoint."),
        ("ART-05", "enhancement_cohort",
         "A frozen rights-cleared paired noisy/clean 16 kHz cohort with exact "
         "durations, language and speaker groups, held-out splits and "
         "identity/noisy, DeepFilterNet3 or FastEnhancer task-matched "
         "baseline, clean-preservation, peak/invalid and unpaired controls."),
        ("ART-06", "enhancement_results",
         "Independent Enhancement results for paired SI-SDR and STOI, "
         "clean-speech preservation, peaks and invalid outputs, authorized "
         "listening or predictive screen, alignment, content delay, "
         "chunk/state behavior, memory, availability timing, resources and "
         "uncertainty."),
    ]
    return [{
        "id": artifact_id,
        "kind": kind,
        "requirement": requirement,
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "bytes": None,
    } for artifact_id, kind, requirement in rows]


def exact_blockers() -> list[dict]:
    rows = [
        ("BLK-01", "ART-01", ["RG-01", "RG-04"],
         "The exact RookieJunChen/FullSubNet-plus source checkout is absent. "
         "The adapter and readiness record reference commit b115416, but no "
         "reviewable local tree at a 40-hex revision, upstream Apache-2.0 "
         "license text bytes or per-file SHA-256 pin exists in the workspace.",
         "Supply the RookieJunChen/FullSubNet-plus source at the immutable "
         "40-hex revision b115416 with its reviewed Apache-2.0 license text "
         "and per-file SHA-256 pins; do not substitute a mirror."),
        ("BLK-02", "ART-02", ["RG-01", "RG-04", "RG-07"],
         "The official best_model.tar checkpoint is absent and unverified. It "
         "is linked only from Google Drive file ID "
         "1UJSt1G0P_aXry-u79LLU_l9tCnNa2u7C; no weight terms, immutable "
         "artifact revision, byte size or SHA-256 is published or locally "
         "reviewable, so it was not downloaded. The intended inference "
         "configuration is the pinned 16 kHz n_fft=512, win_length=512, "
         "hop_length=256, 257-bin complex CRM with look-ahead 2.",
         "Obtain from the authors or a clearly authorized official "
         "distribution: applicable weight license/terms, an immutable or "
         "versioned artifact identity, the exact byte size and SHA-256, and "
         "confirmation that best_model.tar is the intended inference "
         "checkpoint for the pinned config."),
        ("BLK-03", "ART-03", ["RG-04", "RG-07"],
         "The pinned isolated runtime is absent. No interpreter, torch or "
         "torchaudio package lock, host profile or offline load path matching "
         "the upstream PyTorch 1.7.1 / torchaudio 0.7 sample environment is "
         "present; CPU compatibility and throughput are unmeasured.",
         "Supply a locked, reproducible runtime with exact versions, a lock "
         "SHA-256, an offline load path and a recorded host profile, then run "
         "a bounded CPU smoke with weights-only deserialization."),
        ("BLK-04", "ART-04", ["RG-01", "RG-06"],
         "Weight terms, training-data provenance, corpus rights, "
         "clean-reference permission, output use and redistribution are "
         "unresolved. The repository's reported Apache-2.0 code license is "
         "not evidence for the externally hosted best_model.tar weights.",
         "Provide reviewed weight terms or a model card, training-data "
         "provenance, corpus rights, explicit clean-reference permission, "
         "output use and redistribution approval."),
        ("BLK-05", "ART-05", ["RG-02", "RG-03", "RG-05"],
         "No rights-cleared, consented frozen paired noisy/clean cohort is "
         "admitted here. The readiness record names a local 30-pair mono "
         "16 kHz DNS2020 set, but this package does not open, verify or admit "
         "it, and no identity/noisy control, DeepFilterNet3 or FastEnhancer "
         "baseline, clean-preservation, peak/invalid or unpaired control is "
         "frozen.",
         "Supply the frozen permitted cohort with exact geometry, language "
         "and speaker groups, held-out splits and matched controls."),
        ("BLK-06", "ART-06", ["RG-02", "RG-03", "RG-05", "RG-07", "RG-08"],
         "No Enhancement evidence exists. Paired SI-SDR and STOI, "
         "clean-speech preservation, peaks and invalid (including nonfinite) "
         "outputs, authorized listening, alignment, content delay, "
         "chunk/state behavior, memory, availability timing, resources and "
         "uncertainty are all unmeasured for FullSubNet+.",
         "Run and preserve the independent Enhancement protocol, authorized "
         "listening or predictive screen, and target-runtime timing on the "
         "exact pinned source, checkpoint and runtime."),
    ]
    return [{
        "id": blocker_id,
        "artifact_id": artifact_id,
        "linked_gates": linked_gates,
        "statement": statement,
        "required_action": action,
        "status": "open",
        "qualifies": False,
    } for blocker_id, artifact_id, linked_gates, statement, action in rows]


def release_gates() -> list[dict]:
    rows = [
        ("RG-01", "exact licensed source and checkpoint pinned",
         "The source revision is referenced but not locally verified, and the "
         "official checkpoint has no terms, immutable identity or digest.",
         "Supply and pin the exact source checkout and caller-selected "
         "best_model.tar bundle with reviewed terms and digests."),
        ("RG-02", "rights-cleared frozen paired cohort and clean references",
         "No rights-cleared paired noisy/clean cohort, held-out partition or "
         "permitted clean reference is admitted.",
         "Freeze the permitted paired cohort and record clean-reference "
         "permission."),
        ("RG-03", "identity/noisy control, task-matched baseline and "
                  "uncertainty",
         "No identity/noisy control, DeepFilterNet3 or FastEnhancer baseline "
         "or uncertainty result exists.",
         "Run matched controls with uncertainty on the frozen cohort."),
        ("RG-04", "pinned source, checkpoint, runtime and per-weight terms",
         "No exact source checkout, model revision, runtime lock, host "
         "profile or per-weight terms are pinned.",
         "Pin the source, checkpoint, runtime, host profile and terms with "
         "exact digests."),
        ("RG-05", "alignment, content delay, state, memory, availability "
                  "timing and numerical behavior",
         "No content delay, alignment, chunk/state, memory, availability "
         "timing, nonfinite, peak or target-runtime measurement exists.",
         "Measure alignment, content delay, numerical behavior and resource "
         "timing on the exact target."),
        ("RG-06", "authorized listening or labeled predictive screen",
         "No authorized listening protocol and no separately labeled "
         "predictive screen exists.",
         "Complete authorized listening or a declared predictive screen."),
        ("RG-07", "opt-in provider intake and independent review",
         "No adapter, descriptor, default-off intake decision or independent "
         "exact-head review exists.",
         "Add a task-local opt-in adapter only after RG-01 to RG-06 pass, "
         "then obtain independent exact-head review."),
        ("RG-08", "release approval",
         "Release approval is absent and DEFER remains in force.",
         "Close every preceding gate and obtain release approval."),
    ]
    return [{
        "id": gate_id,
        "name": name,
        "status": "blocked",
        "qualifies": False,
        "reason": reason,
        "reopen_condition": reopen,
        "linked_row": _gate_link(),
    } for gate_id, name, reason, reopen in rows]


def historical_evidence_block() -> dict:
    return {
        "status": "no_local_historical_execution_found",
        "qualifies": False,
        "candidate": "FullSubNet+",
        "entries": [],
        "searched_pins": [
            "research/noise_suppression_candidate_census.md",
            "research/voice-enhancement-20261101/candidate_matrix.csv",
            "research/voice-enhancement-20261101/agent-fullsubnet-readiness/"
            "REPORT.md",
            "audio-benchmark-platform/plan/INVENTORY.json",
        ],
        "source_reported_context": {
            "task_kind": "16 kHz single-channel complex-spectrum "
                         "channel-attention speech enhancement",
            "sample_rate_hz": UPSTREAM_SAMPLE_RATE_HZ,
            "n_fft": N_FFT,
            "win_length": WIN_LENGTH,
            "hop_length": HOP_LENGTH,
            "freq_bins": FREQ_BINS,
            "lookahead_frames": LOOKAHEAD_FRAMES,
            "mask_kind": MASK_KIND,
            "reported_baselines": list(BASELINES),
            "reproduced_here": False,
            "admitted_as_result": False,
        },
        "not_reproduced_here": True,
        "no_values_inferred_from_adjacent_tasks": True,
        "note": "The pinned records contain a verified source/revision "
                "reference, a Google Drive checkpoint link and a 16 kHz "
                "inference config only. No FullSubNet+ run, output, metric, "
                "corpus or runtime is recorded locally, and no adjacent "
                "enhancement value is inherited.",
    }


def enhancement_profile_block() -> dict:
    return {
        "profile": PROFILE_KEY,
        "status": "blocked",
        "rows": [dict(row) for row in ENHANCEMENT_REQUIREMENTS],
        "identity_or_noisy_control_measured": False,
        "task_matched_baseline_measured": False,
        "paired_si_sdr_measured": False,
        "paired_stoi_measured": False,
        "clean_speech_preservation_measured": False,
        "peaks_measured": False,
        "invalid_outputs_measured": False,
        "unpaired_predictive_screen_present": False,
        "authorized_listening_present": False,
        "alignment_measured": False,
        "content_delay_measured": False,
        "state_measured": False,
        "memory_measured": False,
        "availability_timing_measured": False,
        "clean_reference_rights_cleared": False,
        "corpus_rights_cleared": False,
        "output_use_cleared": False,
        "qualifies": False,
    }


def profile_source() -> dict:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    expected = SOURCE_PINS[PROFILE_SOURCE_REL]
    if not path.is_file():
        raise ValueError("profile_source_missing")
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError("profile_source_unpinned")
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| Enhancement |")]
    if len(rows) != 1:
        raise ValueError("enhancement_profile_row_not_unique")
    row = rows[0]
    for phrase in PROFILE_PHRASES:
        if phrase not in row:
            raise ValueError("enhancement_profile_phrase_missing:" + phrase)
    return {
        "profile": PROFILE_KEY,
        "key": PROFILE,
        "path": PROFILE_SOURCE_REL,
        "sha256": actual,
        "row": row,
        "phrases": list(PROFILE_PHRASES),
    }


def disposition_block() -> dict:
    return {
        "promotion": "defer",
        "production_exposure": "DEFER",
        "status": "incomplete",
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "not_qualified": True,
        "defer_before": "opt_in_adapter_exposure",
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
        "missing_result_qualifies": False,
    }


def boundary_block() -> dict:
    return {
        "provider_registration": False,
        "registered": False,
        "default_enabled": False,
        "descriptor_registry_change": False,
        "public_api_abi_change": False,
        "shared_cmakelists_change": False,
        "installed_v0_behavior_change": False,
        "ci_workflow_change": False,
        "board_changed": False,
        "handoff_changed": False,
        "files_outside_task_directory_written": False,
        "task_local_only": True,
    }


def scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "source_present": False,
        "source_executed": False,
        "weights_present": False,
        "weights_read": False,
        "runtime_present": False,
        "runtime_executed": False,
        "inference_performed": False,
        "real_corpus": False,
        "audio_read": False,
        "enhancement_performed": False,
        "quality_scored": False,
        "si_sdr_scored": False,
        "stoi_scored": False,
        "clean_preservation_scored": False,
        "listening": False,
        "device_timing": False,
        "first_output_timing": False,
        "benchmark": False,
        "release_claim": False,
        "network_used": False,
        "download_attempted": False,
        "historical_output_admitted": False,
    }


def exact_scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "allowed_write_prefix": TASK_PREFIX,
        "provider_registration": False,
        "installed_v0_change": False,
        "public_api_abi_change": False,
        "shared_build_change": False,
        "ci_change": False,
        "board_or_handoff_change": False,
        "real_corpus": False,
        "weights": False,
        "runtime": False,
        "network": False,
        "release_claim": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16_000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "preserved": True,
        "sdk_callback_invoked": False,
    }


def model_geometry() -> dict:
    return {
        "task_kind": "complex_spectrum_channel_attention_speech_enhancement",
        "inputs": ["noisy_waveform_16khz_mono"],
        "output": "enhanced_waveform_16khz_mono",
        "sample_rate_hz": UPSTREAM_SAMPLE_RATE_HZ,
        "channels": 1,
        "sample_format": "f32",
        "candidate_family": "FullSubNet+ channel-attention complex-spectrum SE",
        "n_fft": N_FFT,
        "win_length": WIN_LENGTH,
        "hop_length": HOP_LENGTH,
        "freq_bins": FREQ_BINS,
        "mask_kind": MASK_KIND,
        "lookahead_frames": LOOKAHEAD_FRAMES,
        "parameter_count": None,
        "parameter_count_asserted": False,
        "reported_baselines": list(BASELINES),
        "upstream_runtime": UPSTREAM_RUNTIME,
        "upstream_cpu_support": UPSTREAM_CPU_SUPPORT,
        "offline_whole_utterance": True,
        "chunk_state_pinned": False,
        "output_scaling_inherited": False,
        "installed_v0": False,
        "provider_registered": False,
        "local_metric_claimed": False,
    }


def upstream_record() -> dict:
    return {
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "source_revision_reference_only": True,
        "source_revision_requirement":
            "immutable 40-hex upstream commit with a reviewable local checkout",
        "source_license_spdx_reported": SOURCE_LICENSE_SPDX,
        "source_license_text_verified": SOURCE_LICENSE_TEXT_VERIFIED,
        "paper_context": PAPER_CONTEXT,
        "checkpoint_host": CHECKPOINT_HOST,
        "checkpoint_file_id": CHECKPOINT_FILE_ID,
        "checkpoint_filename": CHECKPOINT_FILENAME,
        "checkpoint_revision": CHECKPOINT_REVISION,
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "checkpoint_terms": CHECKPOINT_TERMS,
        "sample_rate_hz": UPSTREAM_SAMPLE_RATE_HZ,
        "n_fft": N_FFT,
        "win_length": WIN_LENGTH,
        "hop_length": HOP_LENGTH,
        "freq_bins": FREQ_BINS,
        "lookahead_frames": LOOKAHEAD_FRAMES,
        "task_kind": "complex_spectrum_channel_attention_speech_enhancement",
        "reported_baselines": list(BASELINES),
        "present": False,
        "executed": False,
        "digest_asserted": False,
    }


def rights_gap() -> dict:
    return {
        "code_license": "Apache-2.0_reported_text_unverified",
        "weight_terms": "unresolved",
        "training_data_provenance": "unresolved",
        "corpus_rights": "unresolved",
        "clean_reference_permission": "unresolved",
        "output_use": "unresolved",
        "redistribution": "unresolved",
        "all_resolved": False,
    }


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "all_release_gates_blocked": True,
        "exact_source_present": False,
        "exact_weights_present": False,
        "exact_runtime_present": False,
        "exact_licensed_conjunction_present": False,
        "rights_cleared": False,
        "paired_cohort_present": False,
        "enhancement_evaluation_present": False,
        "identity_or_noisy_control_result": False,
        "task_matched_baseline_result": False,
        "paired_si_sdr_result": False,
        "paired_stoi_result": False,
        "clean_preservation_result": False,
        "peak_or_invalid_result": False,
        "listening_result": False,
        "alignment_result": False,
        "content_delay_result": False,
        "timing_or_memory_result": False,
        "benchmark_result": False,
        "release_qualification_present": False,
        "missing_result_promoted": False,
        "not_qualified": True,
    }


def pin_rows(pins: dict[str, str], root: Path) -> dict:
    rows = {}
    for relative, expected in sorted(pins.items()):
        path = root / relative
        if not path.is_file():
            raise ValueError("pin_target_missing:" + relative)
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError("pinned_bytes_changed:" + relative)
        rows[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": True,
        }
    return rows


def linked_identity_block() -> dict:
    projection = board_row_projection()
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "gating": "stable_identity_only",
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "linked_rows": [dict(row) for row in linked_rows()],
        "linked_rows_sha256": linked_rows_digest(),
    }


def _assert_absence(probes: list[dict]) -> None:
    if any(row.get("present") is not False for row in probes):
        raise ValueError("absence_probe_appeared")


# ---------------------------------------------------------------------------
# Merge-base scope helpers (used by verify.py).
# ---------------------------------------------------------------------------


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    """Return the commit SHA a ref resolves to, or None when it is absent."""
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
# README digest table.
# ---------------------------------------------------------------------------

README_DIGEST_SECTION = "## Canonical artifacts and local digests"
README_ARTIFACT_FILES = (
    "contract.json",
    "report.json",
    "report.json.sha256",
    "reference.py",
    "run.py",
    "verify.py",
    "test_reference.py",
)
README_ROW_RE = re.compile(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$")


def _readme_section(text: str, heading: str) -> str:
    if heading not in text:
        raise ValueError("readme_section_missing:" + heading)
    body = text.split(heading, 1)[1]
    if "\n## " in body:
        body = body.split("\n## ", 1)[0]
    return body


def readme_artifact_digests(text: str) -> dict[str, str]:
    """Parse the README digest table; malformed or duplicate rows fail closed."""
    rows: dict[str, str] = {}
    for line in _readme_section(text, README_DIGEST_SECTION).splitlines():
        if not line.startswith("|") or line in ("| File | SHA-256 |",
                                                "| --- | --- |"):
            continue
        match = README_ROW_RE.fullmatch(line)
        if match is None:
            raise ValueError("readme_digest_row_malformed:" + repr(line))
        name, digest = match.groups()
        if name in rows:
            raise ValueError("readme_digest_duplicate:" + name)
        rows[name] = digest
    return rows


def update_readme_artifact_table(text: str) -> str:
    start = text.index(README_DIGEST_SECTION)
    end = text.find("\n## ", start + len(README_DIGEST_SECTION))
    if end == -1:
        end = len(text)
    rows = "\n".join(
        f"| `{name}` | `{sha256_file(HERE / name)}` |"
        for name in README_ARTIFACT_FILES)
    body = (README_DIGEST_SECTION + "\n\n| File | SHA-256 |\n"
            "| --- | --- |\n" + rows + "\n")
    return text[:start] + body + text[end:]


# ---------------------------------------------------------------------------
# Contract and report.
# ---------------------------------------------------------------------------


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "profile_source": profile_source(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "geometry": model_geometry(),
        "upstream_record": upstream_record(),
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "linked_rows": [dict(row) for row in linked_rows()],
        "linked_rows_sha256": linked_rows_digest(),
        "board_row_projection": board_row_projection(),
        "board_row_sha256": board_row_digest(board_row_projection()),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "rights_gap": rights_gap(),
        "enhancement_profile": enhancement_profile_block(),
        "enhancement_profile_requirements":
            [dict(row) for row in ENHANCEMENT_REQUIREMENTS],
        "historical_evidence": historical_evidence_block(),
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "admission_contract": admission_contract_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "non_claims": list(NON_CLAIMS),
        "write_scope": WRITE_SCOPE,
        "qualification": qualification_block(),
    }


def build_report() -> dict:
    contract = build_contract()
    probes = absence_probes()
    _assert_absence(probes)
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task_id": TASK,
        "task": TASK,
        "component_id": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "profile": PROFILE,
        "profile_source": profile_source(),
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "exact_scope": exact_scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "geometry": model_geometry(),
        "upstream_record": upstream_record(),
        "source_probe": source_probe(),
        "weights_probe": weights_probe(),
        "runtime_probe": runtime_probe(),
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "gates": release_gates(),
        "remaining_gates": [row["id"] for row in release_gates()],
        "linked_row_identity": linked_identity_block(),
        "enhancement_profile": enhancement_profile_block(),
        "enhancement_profile_requirements":
            [dict(row) for row in ENHANCEMENT_REQUIREMENTS],
        "qualification": qualification_block(),
        "historical_evidence": historical_evidence_block(),
        "peer_evidence": [dict(row) for row in PEER_EVIDENCE],
        "rights_gap": rights_gap(),
        "admission": admission_controls(),
        "prohibited_claims": list(NON_CLAIMS),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "reproduction": {
            "interpreter": "Python " + REQUIRED_INTERPRETER +
                           ", standard library only",
            "pinned_interpreter": REQUIRED_INTERPRETER,
            "bytecode_disabled": True,
            "cold_start_repeats": 3,
            "network_required": False,
            "runtime_required": False,
            "commands": [
                "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all",
                "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v "
                "test_reference.py",
                "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            ],
            "repository_checks": [
                "python3.12 scripts/ci.py --output build/ci-fullsubnet",
                "python3 -m reuse lint",
                "git diff --check",
            ],
        },
        "write_scope": WRITE_SCOPE,
    }


def validate_contract(contract: dict) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_mismatch")
    if contract.get("contract_id") != CONTRACT_ID:
        raise ValueError("contract_id_mismatch")
    if contract.get("task") != TASK:
        raise ValueError("contract_task_mismatch")
    if contract.get("title") != TASK_TITLE:
        raise ValueError("contract_title_mismatch")
    if contract.get("component") != COMPONENT_ID:
        raise ValueError("contract_component_mismatch")
    if contract.get("mode") != MODE:
        raise ValueError("contract_mode_mismatch")
    if contract.get("branch") != BRANCH:
        raise ValueError("contract_branch_mismatch")
    if contract.get("base_commit") != BASE_COMMIT:
        raise ValueError("contract_base_mismatch")
    if contract.get("profile") != PROFILE:
        raise ValueError("contract_profile_mismatch")
    if contract.get("status") != STATUS:
        raise ValueError("contract_status_mismatch")
    if contract.get("decision") != DECISION:
        raise ValueError("contract_decision_mismatch")
    if contract.get("qualification_status") != QUALIFICATION_STATUS:
        raise ValueError("contract_qualification_mismatch")
    if contract.get("board_file_pinned") is not False:
        raise ValueError("contract_board_pinned")
    if contract.get("source_pins") != SOURCE_PINS:
        raise ValueError("contract_source_pins_mismatch")
    if contract.get("boundary_pins") != BOUNDARY_PINS:
        raise ValueError("contract_boundary_pins_mismatch")
    gates = contract.get("release_gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gate_count")
    if [row.get("id") for row in gates] != ["RG-0" + str(i)
                                             for i in range(1, 9)]:
        raise ValueError("contract_gate_ids")
    for row in gates:
        if row.get("status") != "blocked" or row.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked:" + str(row.get("id")))
        if row.get("linked_row") != _gate_link():
            raise ValueError("contract_gate_link")
    blockers = contract.get("exact_blockers")
    if not isinstance(blockers, list) or len(blockers) != 6:
        raise ValueError("contract_blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open:" + str(row.get("id")))
    artifacts = contract.get("required_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 6:
        raise ValueError("contract_artifact_count")
    for row in artifacts:
        if (row.get("present") is not False or row.get("verified") is not False
                or row.get("blocked") is not True):
            raise ValueError("contract_artifact_not_blocked:" +
                             str(row.get("id")))
    qualification = contract.get("qualification", {})
    if (qualification.get("status") != QUALIFICATION_STATUS
            or qualification.get("readiness") != "incomplete"
            or qualification.get("all_release_gates_blocked") is not True):
        raise ValueError("contract_qualification_invalid")
    assert_no_float(contract)
