# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-SMALL-LOG-MEL-GRU.

This module is standard-library only and deterministic. It contains no complete
trained GRU weight set, PyTorch/librosa runtime, audio signal, transcript,
syllable label, log-mel feature cache, inference path or new model result. It
records the exact historical recipe, hashes the one final-fold checkpoint file
that exists without loading or decoding it, probes a fixed list of workspace,
environment and home-cache paths to evidence that the remaining weights,
feature cache and runtime are absent, validates a caller-supplied rate-cohort
manifest with a fail-closed admission boundary, and builds the canonical report.

The historical pilot trained a 6,113-parameter causal log-mel GRU with PyTorch
2.2.2 on 210 four-second AMI EN2003a windows. That result is provenance only.
This package does not reproduce, confirm or extend it, and no result here
qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import posixpath
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

TASK = "SDK-SMALL-LOG-MEL-GRU"
COMPONENT_ID = "small-log-mel-gru"
TASK_TITLE = "Small log-mel GRU"
CONTRACT_ID = "audio-sdk/small-log-mel-gru-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/small-log-mel-gru-rate-cohort/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "implementation"
BASE_COMMIT = "d50bf1d324bf2a98607b56c2dccbc72d7f143932"
BRANCH = "swarm/SDK-SMALL-LOG-MEL-GRU"
WRITE_SCOPE = "docs/task-evidence/small-log-mel-gru/ only"
TASK_PREFIX = "docs/task-evidence/small-log-mel-gru/"
DISPOSITION = (
    "Caller-supplied TinyRateGRU log-mel rate-regressor readiness blocker; "
    "no complete weights, runtime, feature cache, adapter or result.")

MODEL_NAME = "TinyRateGRU"
MODEL_CLASS = "TinyRateGRU"
GRU_INPUT_SIZE = 24
GRU_HIDDEN_SIZE = 32
GRU_LAYERS = 1
GRU_BIDIRECTIONAL = False
HEAD_HIDDEN_SIZE = 16
HEAD_OUTPUT_SIZE = 1
PARAMETER_COUNT = 6113
SEED = 20261101
EPOCHS_PER_FOLD = 30
BATCH_SIZE = 16
FOLDS = 5
CPU_THREADS = 1
INTEROP_THREADS = 1
COHORT_WINDOW_COUNT = 210
COHORT_WINDOW_SECONDS = "4.0"
WINDOW_SAMPLES = 64000
SAMPLE_RATE_HZ = 16000
N_FFT = 400
HOP_LENGTH = 160
N_MELS = 24
FRAMES_PER_WINDOW = 1 + WINDOW_SAMPLES // HOP_LENGTH
FFT_BINS = N_FFT // 2 + 1
VALUES_PER_WINDOW = FRAMES_PER_WINDOW * N_MELS
COHORT_MEL_VALUES = COHORT_WINDOW_COUNT * VALUES_PER_WINDOW
RUNTIME_PYTHON = "3.10.13"
RUNTIME_TORCH = "2.2.2"
CHECKPOINT_FILENAME = "small_gru_last_fold.pt"
CHECKPOINT_SHA256 = (
    "8740b3078433f758c9d0b3106d5de40beae8653a1c9cc3ac49edb1a65a114e7f")
CHECKPOINT_BYTE_COUNT = 27792

PROFILE_PHRASES = (
    "Measure source/output mapping, duration, pitch, transient audibility "
    "and playback buffering.",
    "Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, "
    "drift and the final partial window.",
    "Keep pause or filler decisions tied to source timestamps and measure "
    "speech preservation.",
)

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml workspace without a recursive walk or network use."""
    override = os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

# Immutable read-only inputs. `source:` rows are workspace-relative; the rest
# are SDK-worktree-relative. The mutable shared board is deliberately excluded
# from the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-neural/REPORT.md":
        "f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73",
    "research/tsm-followup-20261101/agent-neural/run/train_small_gru.py":
        "dba40141ca2a6d74f98a814e8c5fa8e3762b550e4d42233394978f1508e37291",
    "research/tsm-followup-20261101/agent-neural/run/small_gru_results.json":
        "9206b6ff1fff8dd25ec511b88c2227178f67f95d603521370c460427f7cf15ef",
    "research/tsm-followup-20261101/agent-neural/run/"
    "syl_eval_manifest.json":
        "3c7b3731cf6d2312e42e3333cae03bc631f6d1dbf557b773e134468c867897e2",
    "research/tsm-followup-20261101/agent-neural/run/"
    + CHECKPOINT_FILENAME:
        CHECKPOINT_SHA256,
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
    "docs/task-evidence/mobilenetv3-small-on-log-mels/README.md":
        "6d45f0d27be9e0d461181bfa3c9e23ca6c955a15dda08527b46f15eadfd8f510",
    "docs/task-evidence/mobilenetv3-small-on-log-mels/report.json":
        "2f179b4b49afcf9fd866e0a6339f0ede60a85192d04ba5d2629984b3d6828f50",
    "docs/task-evidence/distil-wav2vec2-adult-child-ridge/README.md":
        "adb751885024bcaab88a373602f3d19326cee356559d62b0cc334cbc25afceca",
    "docs/task-evidence/distil-wav2vec2-adult-child-ridge/report.json":
        "ff7b70f389b8c7908c917aa2488728d7f972a8acd22bf66c56d9a671cd5a65d4",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/README.md":
        "3da6772383eb9b44ccd8eeab4272bf69e4dbd2640f045e42c4fa6ed24f275533",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/report.json":
        "6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9",
}

# Only stable, non-mutable identity fields are projected. `status`, `owner`,
# `claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` never
# enter canonical bytes and never gate this package.
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                  "SDK-FND-PROVIDER")

CHECKPOINT_PROBES = (
    "research/tsm-followup-20261101/agent-neural/run/small_gru_fold0.pt",
    "research/tsm-followup-20261101/agent-neural/run/small_gru_fold1.pt",
    "research/tsm-followup-20261101/agent-neural/run/small_gru_fold2.pt",
    "research/tsm-followup-20261101/agent-neural/run/small_gru_fold3.pt",
    "research/tsm-followup-20261101/agent-neural/run/small_gru_fold4.pt",
    "research/tsm-followup-20261101/agent-neural/run/small_gru_folds.pt",
)
WORKSPACE_PROBES = CHECKPOINT_PROBES + (
    "research/tsm-followup-20261101/agent-neural/run/small_gru_features.npz",
    "research/tsm-followup-20261101/agent-neural/run/small_gru_features.npy",
    "research/tsm-followup-20261101/agent-neural/run/"
    "small_gru_logmel_cache.npz",
    "data/models/small-log-mel-gru",
    "data/models/small_gru",
    "data/checkouts/small-log-mel-gru",
    "data/envs/sylnet-py310",
    "data/envs/small-log-mel-gru-py310",
    "data/runs/small_log_mel_gru",
    "data/runs/small_gru",
)
HOME_PROBES = (
    ("torch_runtime",
     ".pyenv/versions/3.10.13/lib/python3.10/site-packages/torch/__init__.py"),
    ("librosa_runtime",
     ".pyenv/versions/3.10.13/lib/python3.10/site-packages/librosa/"
     "__init__.py"),
    ("soundfile_runtime",
     ".pyenv/versions/3.10.13/lib/python3.10/site-packages/soundfile/"
     "__init__.py"),
    ("torch_cache", ".cache/torch"),
)

NON_CLAIMS = [
    "No complete five-fold GRU weight set is present; only one final-fold "
    "torch checkpoint file is hashed, never loaded or decoded.",
    "No PyTorch or librosa runtime is imported or executed.",
    "No audio signal is decoded and no log-mel feature array or model weight "
    "is loaded or executed.",
    "No transcript text or syllable label is extracted or used; no new model "
    "prediction is produced or scored.",
    "Published OOF prediction rows are checked only for aggregate arithmetic "
    "consistency; that check is provenance, not a reproduced CV result.",
    "No listening, device timing, benchmark, pipeline or release claim is made.",
    "No provider, registry, descriptor, public ABI, shared build or CI change "
    "exists.",
    "A syllables/second estimate is not a preferred speed factor or a TSM "
    "setting.",
    "The historical weak result is provenance context, not a local result or a "
    "product decision.",
]

REQUIRED_RESULTS = [
    "The exact TinyRateGRU training source and a complete license/notice bundle "
    "with a reviewed trained-weight and product-use decision.",
    "All five fold checkpoints (or one checkpoint plus a bit-exact retraining "
    "recipe) with SHA-256 and byte counts.",
    "A locked offline Python 3.10.13 / torch 2.2.2 / librosa runtime with "
    "wheel hashes, install/import digest and deterministic algorithms.",
    "The exact persisted log-mel feature cache or a pinned front-end whose "
    "output digest is recorded.",
    "A rights-cleared, multi-meeting rate cohort with checked syllable labels "
    "and source timestamps.",
    "A reproduced five-fold CV result with baseline, fold stability, "
    "finite-output and adverse controls.",
    "Exact Rate-profile mapping, buffering, condition and speech-preservation "
    "evidence.",
    "Target-device p95/p99 timing, resource and deadline behavior.",
    "A separate OFF-by-default versioned provider intake and independent "
    "exact-head review.",
]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def loads_strict(text: str) -> dict[str, Any]:
    """Parse a JSON object, rejecting duplicates, BOM, NaN and Infinity."""
    if not isinstance(text, str):
        raise ValueError("json_text_type")
    if text.startswith("\ufeff"):
        raise ValueError("json_bom")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("json_duplicate_key:" + key)
            result[key] = value
        return result

    def constant_hook(name: str) -> Any:
        raise ValueError("json_nonfinite:" + name)

    try:
        parsed = json.loads(text, object_pairs_hook=pairs_hook,
                            parse_constant=constant_hook)
    except ValueError:
        raise
    except Exception as error:  # pragma: no cover - defensive
        raise ValueError("json_parse:" + str(error)) from error
    if not isinstance(parsed, dict):
        raise ValueError("json_root_not_object")
    return parsed


def read_strict_json(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("json_not_utf8:" + str(error)) from error
    return loads_strict(text)


def _no_floats(value: Any, where: str = "$") -> None:
    if isinstance(value, float):
        raise ValueError("canonical_float:" + where)
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("canonical_nonstring_key:" + where)
            _no_floats(item, where + "." + key)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _no_floats(item, where + "[" + str(index) + "]")


def canonical_bytes(value: Any) -> bytes:
    _no_floats(value)
    text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return (text + "\n").encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _decimal_string(value: Any) -> str:
    """Return a finite, locale-independent decimal string without -0."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("decimal_type")
    if not math.isfinite(value):
        raise ValueError("decimal_nonfinite")
    if value == 0:
        return "0"
    return repr(float(value))


def _is_number(value: Any) -> bool:
    return (not isinstance(value, bool)
            and isinstance(value, (int, float))
            and math.isfinite(value))


def _require_exact_keys(value: Any, keys: tuple[str, ...], code: str) -> None:
    if not isinstance(value, dict):
        raise AdmissionError(code)
    if set(value) != set(keys):
        raise AdmissionError(code)


def _require_hex64(value: Any, code: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise AdmissionError(code)
    return value


def _require_version(value: Any, code: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise AdmissionError(code)
    return value


class AdmissionError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for relative, expected in sorted(pins.items()):
        path = root / relative
        if not path.is_file():
            raise ValueError("pin_missing:" + relative)
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError("pin_mismatch:" + relative)
        rows[relative] = {"sha256": expected, "actual": actual,
                          "verified": actual == expected}
    return rows


def input_inventory() -> list[dict[str, Any]]:
    roles = {
        "README.md": "candidate scorecard and weak-rate finding",
        "REPORT.md": "detailed GRU recipe, result and checkpoint reference",
        "train_small_gru.py": "exact training and fold recipe",
        "small_gru_results.json": "recorded CV, timing and OOF predictions",
        CHECKPOINT_FILENAME:
            "final-fold checkpoint bytes; hashed only, not decoded",
        "syl_eval_manifest.json": "cohort metadata, labels and declared audio "
                                  "digest",
        "INVENTORY.json": "component row and Rate profile",
        "VERIFICATION.md": "Rate acceptance profile",
        "README.md#audio-sdk": "SDK delivery boundary",
    }
    rows: list[dict[str, Any]] = []
    for relative, digest in sorted(SOURCE_PINS.items()):
        name = relative.rsplit("/", 1)[-1]
        role = roles.get(name, "pinned input")
        if relative.endswith("plan/audio-sdk/README.md"):
            role = roles["README.md#audio-sdk"]
        rows.append({
            "path": "source:" + relative,
            "byte_count": (AUDIO_ROOT / relative).stat().st_size,
            "sha256": digest,
            "role": role,
        })
    for relative, digest in sorted(BOUNDARY_PINS.items()):
        rows.append({
            "path": relative,
            "byte_count": (WORKTREE / relative).stat().st_size,
            "sha256": digest,
            "role": "unchanged shared boundary",
        })
    return rows


def _project_row(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in BOARD_ROW_FIELDS}


def _board_rows(path: Path | None = None) -> dict[str, dict[str, Any]]:
    document = read_strict_json(path or (AUDIO_ROOT / BOARD_TASK_ROW))
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_not_list")
    rows: dict[str, dict[str, Any]] = {}
    for row in tasks:
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            rows[row["id"]] = row
    return rows


def board_row_projection(path: Path | None = None) -> dict[str, Any]:
    rows = _board_rows(path)
    row = rows.get(TASK)
    if row is None:
        raise ValueError("linked_task_row_missing")
    return _project_row(row)


def linked_rows(path: Path | None = None) -> list[dict[str, Any]]:
    rows = _board_rows(path)
    result = []
    for task_id in LINKED_ROW_IDS:
        row = rows.get(task_id)
        if row is None:
            raise ValueError("linked_row_missing:" + task_id)
        result.append(_project_row(row))
    return result


def linked_rows_digest(rows: list[dict[str, Any]] | None = None) -> str:
    return object_digest(rows if rows is not None else linked_rows())


def _probe(root: Path, relative: str, kind: str) -> dict[str, Any]:
    present = (root / relative).exists()
    if present:
        raise ValueError("unexpected_artifact_present:" + relative)
    return {"kind": kind, "path": relative, "present": False}


def absence_probes(root: Path,
                   selection: tuple[str, ...] | None = None
                   ) -> list[dict[str, Any]]:
    paths = selection if selection is not None else WORKSPACE_PROBES
    return [_probe(root, relative, "workspace") for relative in paths]


def home_absence_probes() -> list[dict[str, Any]]:
    home = Path.home()
    return [_probe(home, relative, kind) for kind, relative in HOME_PROBES]


def absence_summary(workspace: list[dict[str, Any]],
                    home: list[dict[str, Any]]) -> dict[str, Any]:
    rows = workspace + home
    return {
        "probe_count": len(rows),
        "workspace_probe_count": len(workspace),
        "home_probe_count": len(home),
        "present_count": sum(1 for row in rows if row["present"]),
        "all_probes_absent": all(not row["present"] for row in rows),
        "download_attempted": False,
        "network_used": False,
        "recursive_workspace_walk": False,
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
    }


def _read_manifest() -> dict[str, Any]:
    return read_strict_json(
        AUDIO_ROOT
        / "research/tsm-followup-20261101/agent-neural/run/"
          "syl_eval_manifest.json")


def license_presence() -> dict[str, Any]:
    base = AUDIO_ROOT / "research/tsm-followup-20261101"
    candidates = [
        "LICENSE", "LICENSE.txt", "NOTICE",
        "agent-neural/LICENSE", "agent-neural/LICENSE.txt",
        "agent-neural/NOTICE",
        "agent-neural/run/LICENSE", "agent-neural/run/LICENSE.txt",
        "agent-neural/run/NOTICE",
    ]
    present = [relative for relative in candidates
               if (base / relative).is_file()]
    return {
        "checked_paths": candidates,
        "license_files_present": bool(present),
        "present_paths": present,
        "trained_weight_terms_recorded": False,
        "runtime_license_bundle_present": False,
        "product_use_decision_present": False,
    }


def source_presence() -> dict[str, Any]:
    run = (AUDIO_ROOT / "research/tsm-followup-20261101/agent-neural/run")
    manifest = _read_manifest()
    scripts = [run / "train_small_gru.py"]
    results = [run / "small_gru_results.json"]
    checkpoint = run / CHECKPOINT_FILENAME
    feature_caches = [
        run / "small_gru_features.npz",
        run / "small_gru_features.npy",
        run / "small_gru_logmel_cache.npz",
    ]
    runtime_paths = [
        Path.home() / HOME_PROBES[0][1],
        Path.home() / HOME_PROBES[1][1],
        Path.home() / HOME_PROBES[2][1],
    ]
    records = manifest.get("records")
    if not isinstance(records, list):
        raise ValueError("manifest_records_not_list")
    clip_paths = [AUDIO_ROOT / row["wav"] for row in records
                  if isinstance(row, dict) and isinstance(row.get("wav"), str)]
    clip_present = [path.is_file() for path in clip_paths]
    scripts_present = all(path.is_file() for path in scripts)
    results_present = all(path.is_file() for path in results)
    manifest_present = (run / "syl_eval_manifest.json").is_file()
    report_present = (
        AUDIO_ROOT / "research/tsm-followup-20261101/agent-neural/REPORT.md"
    ).is_file()
    checkpoint_present = checkpoint.is_file()
    fold_checkpoints_present = any(
        (run / f"small_gru_fold{fold}.pt").is_file()
        for fold in range(FOLDS))
    feature_cache_present = any(path.is_file() for path in feature_caches)
    runtime_present = any(path.is_file() for path in runtime_paths)
    licenses = license_presence()
    return {
        "research_scripts_present": scripts_present,
        "recorded_results_present": results_present,
        "detailed_report_present": report_present,
        "cohort_manifest_present": manifest_present,
        "final_fold_checkpoint_present": checkpoint_present,
        "fold_checkpoints_present": fold_checkpoints_present,
        "feature_cache_present": feature_cache_present,
        "runtime_present": runtime_present,
        "license_files_present": licenses["license_files_present"],
        "corpus_clip_count": len(clip_paths),
        "corpus_clip_files_present_count": sum(1 for value in clip_present
                                               if value),
        "corpus_clip_files_present": bool(clip_present)
                                     and all(clip_present),
        "exact_source_weights_runtime_conjunction_present": bool(
            scripts_present and checkpoint_present and fold_checkpoints_present
            and feature_cache_present and runtime_present
            and licenses["license_files_present"]),
        "weights_used": False,
        "runtime_imported": False,
        "audio_read": False,
        "audio_decoded": False,
        "model_executed": False,
        "declared_recording": manifest.get("recording"),
        "declared_recording_sha256": manifest.get("recording_sha256"),
        "declared_annotation_archive_sha256": manifest.get(
            "annotation_archive_sha256"),
        "declared_recording_digest_verified_here": False,
        "cohort_window_count": manifest.get("count"),
        "cohort_meeting_count": 1,
        "license": licenses,
    }


def documented_checkpoint() -> dict[str, Any]:
    run = (AUDIO_ROOT / "research/tsm-followup-20261101/agent-neural/run")
    report = (AUDIO_ROOT
              / "research/tsm-followup-20261101/agent-neural/REPORT.md")
    text = report.read_text(encoding="utf-8")
    path = run / CHECKPOINT_FILENAME
    present = path.is_file()
    actual = sha256_file(path) if present else None
    byte_count = path.stat().st_size if present else None
    return {
        "filename": CHECKPOINT_FILENAME,
        "path": "research/tsm-followup-20261101/agent-neural/run/"
                + CHECKPOINT_FILENAME,
        "documented_in_report": CHECKPOINT_FILENAME in text,
        "documented_scope": "final fold only, not all five folds",
        "present": present,
        "sha256": actual,
        "byte_count": byte_count,
        "all_five_fold_checkpoints_present": False,
        "contradiction": (CHECKPOINT_FILENAME in text and not present),
        "loaded": False,
        "decoded": False,
    }


def _script_text() -> str:
    return (AUDIO_ROOT
            / "research/tsm-followup-20261101/agent-neural/run/"
              "train_small_gru.py").read_text(encoding="utf-8")


def gru_parameter_count(input_size: int, hidden_size: int,
                        layers: int = 1) -> int:
    """Exact PyTorch GRU parameter count, excluding any head."""
    for value in (input_size, hidden_size, layers):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("gru_parameter_type")
        if value <= 0:
            raise ValueError("gru_parameter_nonpositive")
    total = 0
    layer_input = input_size
    gates = 3
    for _ in range(layers):
        total += gates * hidden_size * layer_input
        total += gates * hidden_size * hidden_size
        total += 2 * gates * hidden_size
        layer_input = hidden_size
    return total


def linear_parameter_count(input_size: int, output_size: int) -> int:
    for value in (input_size, output_size):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("linear_parameter_type")
        if value <= 0:
            raise ValueError("linear_parameter_nonpositive")
    return input_size * output_size + output_size


def architecture_reference() -> dict[str, Any]:
    text = _script_text()
    gru = gru_parameter_count(GRU_INPUT_SIZE, GRU_HIDDEN_SIZE, GRU_LAYERS)
    head_1 = linear_parameter_count(GRU_HIDDEN_SIZE, HEAD_HIDDEN_SIZE)
    head_2 = linear_parameter_count(HEAD_HIDDEN_SIZE, HEAD_OUTPUT_SIZE)
    total = gru + head_1 + head_2
    breakdown = {
        "gru_weight_ih_l0":
            GRU_HIDDEN_SIZE * 3 * GRU_INPUT_SIZE,
        "gru_weight_hh_l0":
            GRU_HIDDEN_SIZE * 3 * GRU_HIDDEN_SIZE,
        "gru_bias_ih_l0": GRU_HIDDEN_SIZE * 3,
        "gru_bias_hh_l0": GRU_HIDDEN_SIZE * 3,
        "head_linear_1_weight": GRU_HIDDEN_SIZE * HEAD_HIDDEN_SIZE,
        "head_linear_1_bias": HEAD_HIDDEN_SIZE,
        "head_linear_2_weight": HEAD_HIDDEN_SIZE * HEAD_OUTPUT_SIZE,
        "head_linear_2_bias": HEAD_OUTPUT_SIZE,
    }
    checks = {
        "class_tiny_rate_gru": "class TinyRateGRU(nn.Module)" in text,
        "gru_geometry": (
            "nn.GRU(input_size=24, hidden_size=32, num_layers=1, "
            "batch_first=True, bidirectional=False)" in text),
        "unidirectional": "bidirectional=False" in text,
        "head_linear_32_16": "nn.Linear(32, 16)" in text,
        "head_relu": "nn.ReLU()" in text,
        "head_linear_16_1": "nn.Linear(16, 1)" in text,
        "softplus_output": "nn.Softplus()" in text,
        "last_hidden_state": "self.head(h[-1]).squeeze(-1)" in text,
        "seed_locked": "SEED = 20261101" in text
                       and "torch.manual_seed(SEED)" in text,
        "threads_locked": "torch.set_num_threads(1)" in text
                          and "torch.set_num_interop_threads(1)" in text,
        "thirty_epochs": "for epoch in range(30)" in text,
        "batch_16": "len(perm) / 16" in text,
        "adam_recipe": (
            "Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)" in text),
        "five_chronological_folds": "np.array_split(order, 5)" in text,
        "checkpoint_save": (
            "torch.save(last_model.state_dict()" in text
            and CHECKPOINT_FILENAME in text),
        "no_pretrained_weights": (
            "pretrained" not in text and "from_pretrained" not in text
            and "weights=" not in text),
    }
    return {
        "model": MODEL_CLASS,
        "initialization": "random; no pretrained weights",
        "pretrained_weights_used": False,
        "input_shape": [FRAMES_PER_WINDOW, GRU_INPUT_SIZE],
        "gru": {
            "input_size": GRU_INPUT_SIZE,
            "hidden_size": GRU_HIDDEN_SIZE,
            "num_layers": GRU_LAYERS,
            "bidirectional": GRU_BIDIRECTIONAL,
            "batch_first": True,
            "gates": 3,
        },
        "head": {
            "hidden": HEAD_HIDDEN_SIZE,
            "activation": "relu",
            "output": HEAD_OUTPUT_SIZE,
            "output_activation": "softplus",
        },
        "classes": 1,
        "parameter_breakdown": breakdown,
        "computed_parameter_count": total,
        "recorded_parameter_count": PARAMETER_COUNT,
        "matches_recorded": total == PARAMETER_COUNT,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "script_sha256": SOURCE_PINS[
            "research/tsm-followup-20261101/agent-neural/run/"
            "train_small_gru.py"],
        "executed_here": False,
        "weights_loaded": False,
    }


def frontend_geometry() -> dict[str, Any]:
    padded = WINDOW_SAMPLES + N_FFT
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "window_samples": WINDOW_SAMPLES,
        "window_seconds": COHORT_WINDOW_SECONDS,
        "n_fft": N_FFT,
        "n_fft_ms": N_FFT * 1000 // SAMPLE_RATE_HZ,
        "hop_length": HOP_LENGTH,
        "hop_ms": HOP_LENGTH * 1000 // SAMPLE_RATE_HZ,
        "n_mels": N_MELS,
        "power": "2.0",
        "log_offset": "1e-10",
        "center": True,
        "padded_samples": padded,
        "frames": FRAMES_PER_WINDOW,
        "fft_bins": FFT_BINS,
        "values_per_window": VALUES_PER_WINDOW,
        "cohort_values": COHORT_MEL_VALUES,
        "resize_stage": False,
    }


def frontend_reference() -> dict[str, Any]:
    geometry = frontend_geometry()
    manifest = _read_manifest()
    script = _script_text()
    checks = {
        "sample_rate_matches_manifest":
            manifest.get("sample_rate_hz") == SAMPLE_RATE_HZ,
        "window_matches_manifest":
            Decimal(str(manifest.get("window_s"))) == Decimal(
                COHORT_WINDOW_SECONDS),
        "n_fft_is_25ms": geometry["n_fft_ms"] == 25,
        "hop_is_10ms": geometry["hop_ms"] == 10,
        "frames_are_401": geometry["frames"] == 401,
        "fft_bins_are_201": geometry["fft_bins"] == 201,
        "mel_bands_are_24": geometry["n_mels"] == 24,
        "values_per_window_are_9624": geometry["values_per_window"] == 9624,
        "cohort_values_are_2021040": geometry["cohort_values"] == 2021040,
        "script_has_melspectrogram":
            "librosa.feature.melspectrogram" in script,
        "script_has_n_fft_400": "n_fft=400" in script,
        "script_has_hop_160": "hop_length=160" in script,
        "script_has_n_mels_24": "n_mels=24" in script,
        "script_has_power_2": "power=2.0" in script,
        "script_has_log_offset": "np.log(mel + 1e-10)" in script,
        "script_has_transpose": '.T.astype("float32")' in script,
        "script_uses_librosa_center_default": "center=" not in script,
        "script_has_fold_normalization":
            "X[train_idx].reshape(-1, X.shape[-1]).mean(axis=0, "
            "keepdims=True)" in script
            and "X[train_idx].reshape(-1, X.shape[-1]).std(axis=0, "
                "keepdims=True) + 1e-5" in script,
        "script_has_no_resize_stage":
            "resize" not in script and "interpolate" not in script,
    }
    return {
        "geometry": geometry,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "executed_here": False,
        "is_feature_reproduction": False,
        "feature_cache_present": False,
        "frontend_runtime_pinned": False,
    }


def _recorded_results() -> dict[str, Any]:
    return read_strict_json(
        AUDIO_ROOT
        / "research/tsm-followup-20261101/agent-neural/run/"
          "small_gru_results.json")


def documented_metrics() -> dict[str, Any]:
    result = _recorded_results()
    cv = result["cross_validation"]
    baseline = result["training_fold_mean_baseline"]
    expected = {
        "mae": "1.1418471336364746",
        "rmse": "1.4151802062988281",
        "bias": "-0.06459982693195343",
        "pearson": "0.12446770109689413",
        "spearman": "0.08822100920951738",
        "baseline_mae": "1.1604056358337402",
        "baseline_rmse": "1.430286169052124",
    }
    observed = {
        "mae": _decimal_string(cv["mae_syllables_per_second"]),
        "rmse": _decimal_string(cv["rmse_syllables_per_second"]),
        "bias": _decimal_string(cv["bias_syllables_per_second"]),
        "pearson": _decimal_string(cv["pearson_r"]),
        "spearman": _decimal_string(cv["spearman_rho"]),
        "baseline_mae": _decimal_string(
            baseline["mae_syllables_per_second"]),
        "baseline_rmse": _decimal_string(
            baseline["rmse_syllables_per_second"]),
    }
    if observed != expected:
        raise ValueError("recorded_metric_mismatch")
    if int(cv["n"]) != COHORT_WINDOW_COUNT:
        raise ValueError("recorded_cohort_size_mismatch")
    if int(result["model"]["parameter_count"]) != PARAMETER_COUNT:
        raise ValueError("recorded_parameter_count_mismatch")
    fold_mae = [_decimal_string(row["mae_syllables_per_second"])
                for row in result["folds"]]
    fold_pearson = [_decimal_string(row["pearson_r"])
                    for row in result["folds"]]
    if len(fold_mae) != FOLDS:
        raise ValueError("recorded_fold_count_mismatch")
    timing = result["inference_timing"]
    per_fold_ms = [_decimal_string(row["ms_per_clip"])
                   for row in timing["per_fold"]]
    return {
        "provenance_only": True,
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
        "candidate": result["candidate"],
        "dataset_recorded": result["dataset"],
        "feature_recorded": result["feature"],
        "model_recorded": {
            "gru_hidden": result["model"]["gru_hidden"],
            "head": result["model"]["head"],
            "parameter_count": result["model"]["parameter_count"],
            "directionality": result["model"]["directionality"],
        },
        "training_recorded": {
            "seed": result["training"]["seed"],
            "optimizer": result["training"]["optimizer"],
            "epochs": result["training"]["epochs"],
            "batch_size": result["training"]["batch_size"],
            "split": result["training"]["split"],
        },
        "cv_recorded": {
            "n": cv["n"],
            **observed,
            "fold_mae": fold_mae,
            "fold_pearson": fold_pearson,
        },
        "timing_recorded": {
            "median_ms_per_clip": _decimal_string(
                timing["median_ms_per_clip"]),
            "per_fold_ms_per_clip": per_fold_ms,
            "scope": timing["device"],
        },
        "limitations_recorded": result["limitations"],
        "conclusion_recorded": (
            "The tiny GRU was cheap but weakly ranked rate on the pilot set; "
            "1.142 syllables/second error is not a preferred speed factor and "
            "this is not a product validation."),
    }


def recorded_prediction_reference() -> dict[str, Any]:
    """Check published OOF prediction rows for aggregate arithmetic only."""
    result = _recorded_results()
    rows = result.get("predictions")
    if not isinstance(rows, list) or len(rows) != COHORT_WINDOW_COUNT:
        raise ValueError("prediction_row_count")
    references: list[float] = []
    predictions: list[float] = []
    fold_counts = [0] * FOLDS
    nonfinite = 0
    for row in rows:
        reference = row.get("reference_sps")
        prediction = row.get("prediction_sps")
        fold = row.get("fold")
        if not _is_number(reference) or not _is_number(prediction):
            nonfinite += 1
            continue
        if isinstance(fold, bool) or not isinstance(fold, int) \
                or fold not in range(FOLDS):
            raise ValueError("prediction_fold")
        references.append(float(reference))
        predictions.append(float(prediction))
        fold_counts[fold] += 1
    if nonfinite:
        raise ValueError("prediction_nonfinite")
    n = len(references)
    mae = math.fsum(abs(p - y) for p, y in zip(predictions, references)) / n
    rmse = math.sqrt(
        math.fsum((p - y) ** 2 for p, y in zip(predictions, references)) / n)
    bias = math.fsum(p - y for p, y in zip(predictions, references)) / n
    mean_y = math.fsum(references) / n
    mean_p = math.fsum(predictions) / n
    covariance = math.fsum(
        (y - mean_y) * (p - mean_p)
        for y, p in zip(references, predictions))
    variance_y = math.fsum((y - mean_y) ** 2 for y in references)
    variance_p = math.fsum((p - mean_p) ** 2 for p in predictions)
    pearson = covariance / math.sqrt(variance_y * variance_p)
    cv = result["cross_validation"]
    tolerance = 1e-6
    checks = {
        "row_count": n == COHORT_WINDOW_COUNT,
        "finite_rows": n == COHORT_WINDOW_COUNT,
        "fold_counts": fold_counts == [42] * FOLDS,
        "mae": abs(mae - cv["mae_syllables_per_second"]) <= tolerance,
        "rmse": abs(rmse - cv["rmse_syllables_per_second"]) <= tolerance,
        "bias": abs(bias - cv["bias_syllables_per_second"]) <= tolerance,
        "pearson": abs(pearson - cv["pearson_r"]) <= tolerance,
    }
    return {
        "provenance_only": True,
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
        "row_count": n,
        "fold_counts": fold_counts,
        "nonfinite_count": nonfinite,
        "tolerance": "1e-6",
        "recomputed_matches_recorded": all(checks.values()),
        "checks": checks,
        "recorded_mae": _decimal_string(
            cv["mae_syllables_per_second"]),
        "recorded_rmse": _decimal_string(
            cv["rmse_syllables_per_second"]),
        "recorded_bias": _decimal_string(
            cv["bias_syllables_per_second"]),
        "recorded_pearson": _decimal_string(cv["pearson_r"]),
        "note": (
            "Aggregate arithmetic from published OOF prediction rows; no "
            "model, feature, fold split or training step was reproduced."),
    }


def recipe_provenance() -> dict[str, Any]:
    metrics = documented_metrics()
    predictions = recorded_prediction_reference()
    return {
        "executed_here": False,
        "checkpoint_saved_by_recipe": True,
        "checkpoint_scope": "final fold only",
        "checkpoint_present": False,
        "last_fold_checkpoint_present": True,
        "last_fold_checkpoint_sha256": CHECKPOINT_SHA256,
        "last_fold_checkpoint_byte_count": CHECKPOINT_BYTE_COUNT,
        "last_fold_checkpoint_loaded": False,
        "pretrained_weights_used": False,
        "feature_cache_persisted": False,
        "runtime_pinned": False,
        "recorded_seed": SEED,
        "recorded_epochs_per_fold": EPOCHS_PER_FOLD,
        "recorded_batch_size": BATCH_SIZE,
        "recorded_folds": FOLDS,
        "recorded_threads": CPU_THREADS,
        "recorded_interop_threads": INTEROP_THREADS,
        "recorded_parameter_count": PARAMETER_COUNT,
        "recorded_metrics_digest": object_digest(metrics),
        "recorded_prediction_check_digest": object_digest(predictions),
        "source_script_sha256": SOURCE_PINS[
            "research/tsm-followup-20261101/agent-neural/run/"
            "train_small_gru.py"],
        "source_results_sha256": SOURCE_PINS[
            "research/tsm-followup-20261101/agent-neural/run/"
            "small_gru_results.json"],
    }


ADMISSION_FIELDS = (
    "schema_id", "cohort_id", "architecture", "checkpoints", "runtime",
    "frontend", "audio", "labels", "controls", "outcomes", "rights")
ARCHITECTURE_FIELDS = (
    "model", "initialization", "pretrained", "input_shape", "classes",
    "activation", "parameter_count")
CHECKPOINT_FIELDS = ("fold", "sha256", "byte_count")
RUNTIME_FIELDS = (
    "python", "torch", "librosa", "numpy", "scipy", "soundfile", "device",
    "intra_op_threads", "interop_op_threads", "deterministic_algorithms",
    "offline", "seed")
FRONTEND_FIELDS = (
    "sample_rate_hz", "window_samples", "n_fft", "hop_length", "n_mels",
    "power", "log_offset", "center", "normalization", "cache_sha256")
AUDIO_FIELDS = (
    "id", "path", "sha256", "language", "meeting_id", "speaker_group",
    "start_s", "end_s", "active_s", "reference_rate_sps")
LABEL_FIELDS = (
    "source", "dictionary", "dictionary_version", "dictionary_sha256",
    "human_syllable_nuclei", "coverage_min")
OUTCOME_FIELDS = (
    "mae_syllables_per_second", "rmse_syllables_per_second",
    "bias_syllables_per_second", "pearson_r", "spearman_rho",
    "baseline_mae_syllables_per_second", "nonfinite_count", "sample_count")
RIGHTS_FIELDS = (
    "dataset_terms_reference", "model_terms_reference",
    "frontend_terms_reference", "output_use_reference",
    "review_reference", "claims_qualified")
CONTROL_KINDS = (
    "cv_candidate", "constant_fold_mean_baseline", "featureless_mean_baseline")
RUNTIME_EXPECTED = {
    "python": RUNTIME_PYTHON,
    "torch": RUNTIME_TORCH,
    "device": "cpu",
    "intra_op_threads": CPU_THREADS,
    "interop_op_threads": INTEROP_THREADS,
    "deterministic_algorithms": True,
    "offline": True,
    "seed": SEED,
}
FRONTEND_EXPECTED = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "window_samples": WINDOW_SAMPLES,
    "n_fft": N_FFT,
    "hop_length": HOP_LENGTH,
    "n_mels": N_MELS,
    "power": 2.0,
    "log_offset": 1e-10,
    "center": True,
    "normalization": "fold_train_mean_std",
}


def _validate_architecture(value: Any) -> None:
    _require_exact_keys(value, ARCHITECTURE_FIELDS, "architecture_fields")
    if value["model"] != MODEL_CLASS:
        raise AdmissionError("architecture_model")
    if value["initialization"] != "random":
        raise AdmissionError("architecture_initialization")
    if value["pretrained"] is not False:
        raise AdmissionError("architecture_pretrained")
    if value["input_shape"] != [FRAMES_PER_WINDOW, GRU_INPUT_SIZE]:
        raise AdmissionError("architecture_shape")
    if value["classes"] != 1:
        raise AdmissionError("architecture_classes")
    if value["activation"] != "softplus":
        raise AdmissionError("architecture_activation")
    if (isinstance(value["parameter_count"], bool)
            or not isinstance(value["parameter_count"], int)
            or value["parameter_count"] != PARAMETER_COUNT):
        raise AdmissionError("architecture_parameter_count")


def _validate_checkpoints(value: Any) -> None:
    if not isinstance(value, list) or len(value) != FOLDS:
        raise AdmissionError("checkpoint_count")
    folds: set[int] = set()
    digests: set[str] = set()
    for row in value:
        _require_exact_keys(row, CHECKPOINT_FIELDS, "checkpoint_fields")
        if isinstance(row["fold"], bool) or not isinstance(row["fold"], int):
            raise AdmissionError("checkpoint_fold")
        if row["fold"] not in range(FOLDS) or row["fold"] in folds:
            raise AdmissionError("checkpoint_fold")
        folds.add(row["fold"])
        digest = _require_hex64(row["sha256"], "checkpoint_digest")
        if digest in digests:
            raise AdmissionError("checkpoint_duplicate")
        digests.add(digest)
        if (isinstance(row["byte_count"], bool)
                or not isinstance(row["byte_count"], int)
                or row["byte_count"] <= 0):
            raise AdmissionError("checkpoint_bytes")
    if folds != set(range(FOLDS)):
        raise AdmissionError("checkpoint_fold")


def _validate_runtime(value: Any) -> None:
    _require_exact_keys(value, RUNTIME_FIELDS, "runtime_fields")
    if value["python"] != RUNTIME_EXPECTED["python"]:
        raise AdmissionError("runtime_version:python")
    if value["torch"] != RUNTIME_EXPECTED["torch"]:
        raise AdmissionError("runtime_version:torch")
    for key in ("librosa", "numpy", "scipy", "soundfile"):
        _require_version(value[key], "runtime_version:" + key)
    for key in ("device", "intra_op_threads", "interop_op_threads",
                "deterministic_algorithms", "offline", "seed"):
        if value[key] != RUNTIME_EXPECTED[key]:
            raise AdmissionError("runtime_value:" + key)


def _validate_frontend(value: Any) -> None:
    _require_exact_keys(value, FRONTEND_FIELDS, "frontend_fields")
    for key, expected in FRONTEND_EXPECTED.items():
        if value[key] != expected:
            raise AdmissionError("frontend_value:" + key)
    _require_hex64(value["cache_sha256"], "frontend_cache")


def _validate_audio(value: Any) -> None:
    if not isinstance(value, list) or len(value) != COHORT_WINDOW_COUNT:
        raise AdmissionError("audio_count")
    ids: set[str] = set()
    paths: set[str] = set()
    meetings: set[str] = set()
    for row in value:
        _require_exact_keys(row, AUDIO_FIELDS, "audio_fields")
        identifier = row["id"]
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            raise AdmissionError("audio_id")
        ids.add(identifier)
        path = row["path"]
        if (not isinstance(path, str) or not posixpath.isabs(path)
                or posixpath.normpath(path) != path or ".." in path
                or path in paths):
            raise AdmissionError("audio_path")
        paths.add(path)
        _require_hex64(row["sha256"], "audio_digest")
        if row["language"] != "en":
            raise AdmissionError("audio_language")
        meeting = row["meeting_id"]
        if not isinstance(meeting, str) or not meeting:
            raise AdmissionError("audio_meeting")
        meetings.add(meeting)
        speaker = row["speaker_group"]
        if not isinstance(speaker, str) or not speaker:
            raise AdmissionError("audio_speaker_group")
        for key in ("start_s", "end_s", "active_s", "reference_rate_sps"):
            if not _is_number(row[key]):
                raise AdmissionError("audio_number:" + key)
        if (Decimal(str(row["end_s"])) - Decimal(str(row["start_s"]))
                != Decimal(COHORT_WINDOW_SECONDS)):
            raise AdmissionError("audio_span")
        if not (Decimal(0) < Decimal(str(row["active_s"]))
                <= Decimal(COHORT_WINDOW_SECONDS)):
            raise AdmissionError("audio_active")
        if not (Decimal(0) <= Decimal(str(row["reference_rate_sps"]))
                <= Decimal(20)):
            raise AdmissionError("audio_rate")
    if len(meetings) < 2:
        raise AdmissionError("audio_meeting_count")


def _validate_labels(value: Any) -> None:
    _require_exact_keys(value, LABEL_FIELDS, "label_fields")
    if value["source"] != "cmudict-first-pronunciation":
        raise AdmissionError("label_source")
    if value["dictionary"] != "cmudict":
        raise AdmissionError("label_dictionary")
    if value["dictionary_version"] != "1.1.1":
        raise AdmissionError("label_version")
    _require_hex64(value["dictionary_sha256"], "label_digest")
    if value["human_syllable_nuclei"] is not False:
        raise AdmissionError("label_human")
    if value["coverage_min"] != 0.75:
        raise AdmissionError("label_coverage")


def _validate_controls(value: Any) -> None:
    if not isinstance(value, list):
        raise AdmissionError("controls_type")
    kinds = [row.get("kind") if isinstance(row, dict) else None
             for row in value]
    if sorted(kind for kind in kinds if isinstance(kind, str)) != sorted(
            CONTROL_KINDS) or len(kinds) != len(CONTROL_KINDS):
        raise AdmissionError("controls")


def _validate_outcomes(value: Any) -> None:
    _require_exact_keys(value, OUTCOME_FIELDS, "outcome_fields")
    bounds = {
        "mae_syllables_per_second": (0, 10),
        "rmse_syllables_per_second": (0, 10),
        "bias_syllables_per_second": (-10, 10),
        "pearson_r": (-1, 1),
        "spearman_rho": (-1, 1),
        "baseline_mae_syllables_per_second": (0, 10),
    }
    for key, (low, high) in bounds.items():
        if not _is_number(value[key]):
            raise AdmissionError("outcome_nonfinite:" + key)
        if not (low <= value[key] <= high):
            raise AdmissionError("outcome_range:" + key)
    if value["nonfinite_count"] != 0:
        raise AdmissionError("outcome_nonfinite_count")
    if value["sample_count"] != COHORT_WINDOW_COUNT:
        raise AdmissionError("outcome_sample_count")


def _validate_rights(value: Any) -> None:
    _require_exact_keys(value, RIGHTS_FIELDS, "rights_fields")
    for key in RIGHTS_FIELDS[:-1]:
        if not isinstance(value[key], str) or not value[key].strip():
            raise AdmissionError("rights_reference:" + key)
    if value["claims_qualified"] is not False:
        raise AdmissionError("rights_claims_qualified")


def _validate_cohort_id(value: Any) -> None:
    if (not isinstance(value, str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", value)):
        raise AdmissionError("cohort_id")


def validate_admission(document: Any) -> None:
    """Validate one caller-supplied cohort manifest with fail-closed rules."""
    _require_exact_keys(document, ADMISSION_FIELDS, "admission_fields")
    if document["schema_id"] != ADMISSION_SCHEMA_ID:
        raise AdmissionError("schema_id")
    _validate_cohort_id(document["cohort_id"])
    _validate_architecture(document["architecture"])
    _validate_checkpoints(document["checkpoints"])
    _validate_runtime(document["runtime"])
    _validate_frontend(document["frontend"])
    _validate_audio(document["audio"])
    _validate_labels(document["labels"])
    _validate_controls(document["controls"])
    _validate_outcomes(document["outcomes"])
    _validate_rights(document["rights"])


def admit(document: Any) -> dict[str, Any]:
    """Return an admission result; acceptance never means qualification."""
    try:
        validate_admission(document)
    except AdmissionError as error:
        return {
            "accepted": False,
            "qualifies": False,
            "code": error.code,
            "state_advanced": False,
            "runtime_invoked": False,
            "audio_read": False,
            "weights_loaded": False,
            "model_executed": False,
            "network_used": False,
        }
    return {
        "accepted": True,
        "qualifies": False,
        "code": "accepted_schema_control",
        "reason": "admission_only_no_qualified_result",
        "state_advanced": False,
        "runtime_invoked": False,
        "audio_read": False,
        "weights_loaded": False,
        "model_executed": False,
        "network_used": False,
    }


def _synthetic_control() -> dict[str, Any]:
    checkpoints = [{
        "fold": fold,
        "sha256": sha256_bytes(f"checkpoint:{fold}".encode("ascii")),
        "byte_count": PARAMETER_COUNT * 4,
    } for fold in range(FOLDS)]
    audio = []
    for index in range(COHORT_WINDOW_COUNT):
        identifier = f"SYN-{index:04d}"
        meeting = "SYN-A" if index < COHORT_WINDOW_COUNT // 2 else "SYN-B"
        start = float(index * 4)
        audio.append({
            "id": identifier,
            "path": f"/synthetic/cohort/{identifier}.wav",
            "sha256": sha256_bytes(f"audio:{identifier}".encode("ascii")),
            "language": "en",
            "meeting_id": meeting,
            "speaker_group": "SYN-SPK",
            "start_s": start,
            "end_s": start + 4.0,
            "active_s": 3.5,
            "reference_rate_sps": 4.0,
        })
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "cohort_id": "synthetic-small-gru-rate-control",
        "architecture": {
            "model": MODEL_CLASS,
            "initialization": "random",
            "pretrained": False,
            "input_shape": [FRAMES_PER_WINDOW, GRU_INPUT_SIZE],
            "classes": 1,
            "activation": "softplus",
            "parameter_count": PARAMETER_COUNT,
        },
        "checkpoints": checkpoints,
        "runtime": {
            "python": RUNTIME_PYTHON,
            "torch": RUNTIME_TORCH,
            "librosa": "0.10.1",
            "numpy": "1.26.4",
            "scipy": "1.11.4",
            "soundfile": "0.12.1",
            "device": "cpu",
            "intra_op_threads": CPU_THREADS,
            "interop_op_threads": INTEROP_THREADS,
            "deterministic_algorithms": True,
            "offline": True,
            "seed": SEED,
        },
        "frontend": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "window_samples": WINDOW_SAMPLES,
            "n_fft": N_FFT,
            "hop_length": HOP_LENGTH,
            "n_mels": N_MELS,
            "power": 2.0,
            "log_offset": 1e-10,
            "center": True,
            "normalization": "fold_train_mean_std",
            "cache_sha256": sha256_bytes(b"synthetic-feature-cache"),
        },
        "audio": audio,
        "labels": {
            "source": "cmudict-first-pronunciation",
            "dictionary": "cmudict",
            "dictionary_version": "1.1.1",
            "dictionary_sha256": sha256_bytes(b"synthetic-cmudict"),
            "human_syllable_nuclei": False,
            "coverage_min": 0.75,
        },
        "controls": [{"kind": kind} for kind in CONTROL_KINDS],
        "outcomes": {
            "mae_syllables_per_second": 1.0,
            "rmse_syllables_per_second": 1.2,
            "bias_syllables_per_second": 0.0,
            "pearson_r": 1.0,
            "spearman_rho": 1.0,
            "baseline_mae_syllables_per_second": 1.1,
            "nonfinite_count": 0,
            "sample_count": COHORT_WINDOW_COUNT,
        },
        "rights": {
            "dataset_terms_reference": "synthetic://dataset-terms",
            "model_terms_reference": "synthetic://model-terms",
            "frontend_terms_reference": "synthetic://frontend-terms",
            "output_use_reference": "synthetic://output-use",
            "review_reference": "synthetic://review",
            "claims_qualified": False,
        },
    }


def _mutated(mutation: Any) -> dict[str, Any]:
    document = _synthetic_control()
    mutation(document)
    return document


def _admission_mutations() -> tuple[tuple[str, str, Any], ...]:
    def drop_runtime_torch(doc: dict[str, Any]) -> None:
        del doc["runtime"]["torch"]

    def add_extra_field(doc: dict[str, Any]) -> None:
        doc["extra"] = True

    def wrong_schema(doc: dict[str, Any]) -> None:
        doc["schema_id"] = "audio-sdk/other/0.1"

    def bad_cohort(doc: dict[str, Any]) -> None:
        doc["cohort_id"] = "BAD COHORT"

    def wrong_model(doc: dict[str, Any]) -> None:
        doc["architecture"]["model"] = "other-model"

    def pretrained(doc: dict[str, Any]) -> None:
        doc["architecture"]["pretrained"] = True

    def wrong_params(doc: dict[str, Any]) -> None:
        doc["architecture"]["parameter_count"] = PARAMETER_COUNT + 1

    def wrong_shape(doc: dict[str, Any]) -> None:
        doc["architecture"]["input_shape"] = [24, 401]

    def wrong_activation(doc: dict[str, Any]) -> None:
        doc["architecture"]["activation"] = "relu"

    def missing_fold(doc: dict[str, Any]) -> None:
        doc["checkpoints"].pop()

    def duplicate_fold(doc: dict[str, Any]) -> None:
        doc["checkpoints"][1]["fold"] = 0

    def duplicate_checkpoint(doc: dict[str, Any]) -> None:
        doc["checkpoints"][1]["sha256"] = doc["checkpoints"][0]["sha256"]

    def zero_checkpoint_bytes(doc: dict[str, Any]) -> None:
        doc["checkpoints"][0]["byte_count"] = 0

    def wrong_torch(doc: dict[str, Any]) -> None:
        doc["runtime"]["torch"] = "2.2.1"

    def unpinned_librosa(doc: dict[str, Any]) -> None:
        doc["runtime"]["librosa"] = "latest"

    def wrong_threads(doc: dict[str, Any]) -> None:
        doc["runtime"]["intra_op_threads"] = 4

    def offline_false(doc: dict[str, Any]) -> None:
        doc["runtime"]["offline"] = False

    def wrong_n_fft(doc: dict[str, Any]) -> None:
        doc["frontend"]["n_fft"] = 512

    def wrong_mel_count(doc: dict[str, Any]) -> None:
        doc["frontend"]["n_mels"] = 40

    def wrong_center(doc: dict[str, Any]) -> None:
        doc["frontend"]["center"] = False

    def bad_cache(doc: dict[str, Any]) -> None:
        doc["frontend"]["cache_sha256"] = "not-a-digest"

    def drop_audio(doc: dict[str, Any]) -> None:
        doc["audio"].pop()

    def duplicate_audio_path(doc: dict[str, Any]) -> None:
        doc["audio"][1]["path"] = doc["audio"][0]["path"]

    def duplicate_audio_id(doc: dict[str, Any]) -> None:
        doc["audio"][1]["id"] = doc["audio"][0]["id"]

    def bad_audio_digest(doc: dict[str, Any]) -> None:
        doc["audio"][0]["sha256"] = "0" * 63

    def wrong_span(doc: dict[str, Any]) -> None:
        doc["audio"][0]["end_s"] = 3.5

    def wrong_rate(doc: dict[str, Any]) -> None:
        doc["audio"][0]["reference_rate_sps"] = 25.0

    def one_meeting(doc: dict[str, Any]) -> None:
        for row in doc["audio"]:
            row["meeting_id"] = "SYN-A"

    def wrong_language(doc: dict[str, Any]) -> None:
        doc["audio"][0]["language"] = "hy"

    def human_labels(doc: dict[str, Any]) -> None:
        doc["labels"]["human_syllable_nuclei"] = True

    def missing_control(doc: dict[str, Any]) -> None:
        doc["controls"].pop()

    def nan_outcome(doc: dict[str, Any]) -> None:
        doc["outcomes"]["mae_syllables_per_second"] = float("nan")

    def infinite_outcome(doc: dict[str, Any]) -> None:
        doc["outcomes"]["rmse_syllables_per_second"] = float("inf")

    def outcome_range(doc: dict[str, Any]) -> None:
        doc["outcomes"]["pearson_r"] = 1.5

    def nonfinite_count(doc: dict[str, Any]) -> None:
        doc["outcomes"]["nonfinite_count"] = 1

    def empty_rights(doc: dict[str, Any]) -> None:
        doc["rights"]["review_reference"] = ""

    def claims_qualified(doc: dict[str, Any]) -> None:
        doc["rights"]["claims_qualified"] = True

    def bool_as_number(doc: dict[str, Any]) -> None:
        doc["audio"][0]["active_s"] = True

    def nan_frontend(doc: dict[str, Any]) -> None:
        doc["frontend"]["power"] = float("nan")

    def bool_checkpoint_fold(doc: dict[str, Any]) -> None:
        doc["checkpoints"][0]["fold"] = True

    return (
        ("ADM-01", "runtime_fields", drop_runtime_torch),
        ("ADM-02", "admission_fields", add_extra_field),
        ("ADM-03", "schema_id", wrong_schema),
        ("ADM-04", "cohort_id", bad_cohort),
        ("ADM-05", "architecture_model", wrong_model),
        ("ADM-06", "architecture_pretrained", pretrained),
        ("ADM-07", "architecture_parameter_count", wrong_params),
        ("ADM-08", "architecture_shape", wrong_shape),
        ("ADM-09", "architecture_activation", wrong_activation),
        ("ADM-10", "checkpoint_count", missing_fold),
        ("ADM-11", "checkpoint_fold", duplicate_fold),
        ("ADM-12", "checkpoint_duplicate", duplicate_checkpoint),
        ("ADM-13", "checkpoint_bytes", zero_checkpoint_bytes),
        ("ADM-14", "runtime_version:torch", wrong_torch),
        ("ADM-15", "runtime_version:librosa", unpinned_librosa),
        ("ADM-16", "runtime_value:intra_op_threads", wrong_threads),
        ("ADM-17", "runtime_value:offline", offline_false),
        ("ADM-18", "frontend_value:n_fft", wrong_n_fft),
        ("ADM-19", "frontend_value:n_mels", wrong_mel_count),
        ("ADM-20", "frontend_value:center", wrong_center),
        ("ADM-21", "frontend_cache", bad_cache),
        ("ADM-22", "audio_count", drop_audio),
        ("ADM-23", "audio_path", duplicate_audio_path),
        ("ADM-24", "audio_id", duplicate_audio_id),
        ("ADM-25", "audio_digest", bad_audio_digest),
        ("ADM-26", "audio_span", wrong_span),
        ("ADM-27", "audio_rate", wrong_rate),
        ("ADM-28", "audio_meeting_count", one_meeting),
        ("ADM-29", "audio_language", wrong_language),
        ("ADM-30", "label_human", human_labels),
        ("ADM-31", "controls", missing_control),
        ("ADM-32", "outcome_nonfinite:mae_syllables_per_second",
         nan_outcome),
        ("ADM-33", "outcome_nonfinite:rmse_syllables_per_second",
         infinite_outcome),
        ("ADM-34", "outcome_range:pearson_r", outcome_range),
        ("ADM-35", "outcome_nonfinite_count", nonfinite_count),
        ("ADM-36", "rights_reference:review_reference", empty_rights),
        ("ADM-37", "rights_claims_qualified", claims_qualified),
        ("ADM-38", "audio_number:active_s", bool_as_number),
        ("ADM-39", "frontend_value:power", nan_frontend),
        ("ADM-40", "checkpoint_fold", bool_checkpoint_fold),
    )


def admission_cases() -> list[dict[str, Any]]:
    cases = []
    for identifier, expected, mutation in _admission_mutations():
        result = admit(_mutated(mutation))
        cases.append({
            "id": identifier,
            "mutation": expected,
            "status": "rejected" if not result["accepted"] else "accepted",
            "code": result["code"],
            "qualifies": result["qualifies"],
            "state_unchanged": not result["state_advanced"],
        })
        if result["accepted"]:
            raise ValueError("admission_case_accepted:" + identifier)
        if result["code"] != expected:
            raise ValueError("admission_case_code:" + identifier + ":"
                             + result["code"])
    return cases


def admission_control() -> dict[str, Any]:
    document = _synthetic_control()
    result = admit(document)
    if not result["accepted"]:
        raise ValueError("admission_control_rejected:" + result["code"])
    return {
        "accepted": True,
        "qualifies": False,
        "synthetic_schema_control_not_evidence": True,
        "reason": result["reason"],
        "cohort_id": document["cohort_id"],
        "audio_window_count": len(document["audio"]),
        "meeting_count": len({row["meeting_id"]
                              for row in document["audio"]}),
        "checkpoint_count": len(document["checkpoints"]),
        "feature_cache_pinned": True,
        "state_advanced": False,
        "runtime_invoked": False,
        "audio_read": False,
        "weights_loaded": False,
        "model_executed": False,
        "network_used": False,
    }


def admission_schema() -> dict[str, Any]:
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "admission_only": True,
        "qualifies": False,
        "fields": list(ADMISSION_FIELDS),
        "architecture_fields": list(ARCHITECTURE_FIELDS),
        "checkpoint_fields": list(CHECKPOINT_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "frontend_fields": list(FRONTEND_FIELDS),
        "audio_fields": list(AUDIO_FIELDS),
        "label_fields": list(LABEL_FIELDS),
        "outcome_fields": list(OUTCOME_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "control_kinds": list(CONTROL_KINDS),
        "exact_model": MODEL_CLASS,
        "exact_parameter_count": PARAMETER_COUNT,
        "exact_input_shape": [FRAMES_PER_WINDOW, GRU_INPUT_SIZE],
        "exact_runtime": dict(RUNTIME_EXPECTED),
        "exact_frontend": {
            key: (
                "2.0" if key == "power"
                else "1e-10" if key == "log_offset"
                else value)
            for key, value in FRONTEND_EXPECTED.items()
        },
        "exact_window_count": COHORT_WINDOW_COUNT,
        "exact_window_seconds": COHORT_WINDOW_SECONDS,
        "minimum_meeting_count": 2,
        "label_source": "cmudict-first-pronunciation",
        "label_dictionary": "cmudict",
        "label_dictionary_version": "1.1.1",
        "label_coverage_min": "0.75",
    }


def rate_profile_requirements() -> list[dict[str, Any]]:
    return [
        {
            "id": "RATE-01",
            "requirement": "Measure source/output mapping and duration.",
            "status": "blocked",
            "evidence": (
                "The candidate is a rate estimator, not a TSM renderer; no "
                "source/output mapping or duration result exists."),
        },
        {
            "id": "RATE-02",
            "requirement": "Measure pitch and transient audibility.",
            "status": "blocked",
            "evidence": (
                "No rendered output, F0/transient metric or listening result "
                "exists for a GRU rate estimate."),
        },
        {
            "id": "RATE-03",
            "requirement": "Measure playback buffering.",
            "status": "blocked",
            "evidence": (
                "No playback chain, queue, fill/flush or buffering "
                "measurement exists."),
        },
        {
            "id": "RATE-04",
            "requirement": "Include 1x and rate changes.",
            "status": "blocked",
            "evidence": (
                "No 1x or rate-change comparison exists; syllables/second "
                "is not a speed factor."),
        },
        {
            "id": "RATE-05",
            "requirement": "Include unfamiliar speech, music and silence.",
            "status": "blocked",
            "evidence": (
                "The historical pilot is one AMI meeting of speech; no "
                "unfamiliar speech, music, silence or language coverage was "
                "tested."),
        },
        {
            "id": "RATE-06",
            "requirement": "Include rebuffer, drift and the final partial window.",
            "status": "blocked",
            "evidence": (
                "No stream, rebuffer, clock-drift or partial-window behavior "
                "was measured."),
        },
        {
            "id": "RATE-07",
            "requirement": (
                "Keep pause or filler decisions tied to source timestamps and "
                "measure speech preservation."),
            "status": "blocked",
            "evidence": (
                "No pause/filler controller, source-timestamp mapping or "
                "speech-preservation measurement exists."),
        },
        {
            "id": "RATE-08",
            "requirement": (
                "Map estimated rate to a reviewed preferred-speed policy."),
            "status": "blocked",
            "evidence": (
                "No preference/acceptability labels or rate-to-speed policy "
                "exists; none is inferred from the historical score."),
        },
    ]


def quality_outcomes() -> list[dict[str, Any]]:
    return [
        {
            "id": "QUAL-01",
            "outcome": "cv_accuracy",
            "status": "blocked",
            "value": None,
            "evidence": (
                "The recorded OOF MAE/RMSE/bias is provenance only; no local "
                "score was reproduced."),
        },
        {
            "id": "QUAL-02",
            "outcome": "fold_stability",
            "status": "blocked",
            "value": None,
            "evidence": (
                "Recorded fold metrics are not recomputed from stored model "
                "weights; folds 0-3 checkpoints are absent."),
        },
        {
            "id": "QUAL-03",
            "outcome": "constant_fold_mean_baseline",
            "status": "blocked",
            "value": None,
            "evidence": (
                "The recorded baseline is not reproduced or compared locally."),
        },
        {
            "id": "QUAL-04",
            "outcome": "finite_adverse_and_missing_controls",
            "status": "blocked",
            "value": None,
            "evidence": (
                "No model was executed, so finite-output, adverse, missing "
                "and nonfinite-input controls do not exist."),
        },
    ]


def timing_requirements() -> list[dict[str, Any]]:
    return [
        {
            "id": "TIME-01",
            "metric": "feature_extraction",
            "status": "blocked",
            "value": None,
            "evidence": "No log-mel extraction was performed.",
        },
        {
            "id": "TIME-02",
            "metric": "model_only_ms_per_clip",
            "status": "blocked",
            "value": None,
            "evidence": "No GRU inference was performed.",
        },
        {
            "id": "TIME-03",
            "metric": "end_to_end_p95",
            "status": "blocked",
            "value": None,
            "evidence": "No end-to-end rate path exists.",
        },
        {
            "id": "TIME-04",
            "metric": "device_deadline_and_resources",
            "status": "blocked",
            "value": None,
            "evidence": (
                "No device, pacing, callback, CPU/memory, thermal or energy "
                "measurement exists."),
        },
    ]


def _gate(identifier: str, title: str, statement: str,
          reopen: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "title": title,
        "statement": statement,
        "reopen_condition": reopen,
        "status": "blocked",
        "qualifies": False,
        "linked_row": board_row_projection(),
    }


def release_gates() -> list[dict[str, Any]]:
    return [
        _gate(
            "RG-01", "source_revision_and_license_provenance",
            "The training script is pinned, but no license/notice bundle for "
            "the script, trained weights or dependencies is staged, and no "
            "reviewed product-use decision exists.",
            "Stage the exact source, license/notice bundle and trained-weight "
            "terms, record the script revision and complete an independent "
            "license review."),
        _gate(
            "RG-02", "complete_fold_weights_and_architecture",
            "Only the final-fold file small_gru_last_fold.pt exists. "
            "Checkpoints for folds 0-3 are absent, so the five-fold OOF "
            "predictions cannot be reproduced from stored weights.",
            "Supply all five fold state dicts with SHA-256/byte counts, or a "
            "single checkpoint plus a bit-exact retraining recipe, and verify "
            "them against the recorded architecture and 6,113 parameters."),
        _gate(
            "RG-03", "pinned_deterministic_runtime",
            "The Python 3.10.13/torch 2.2.2/librosa runtime is absent. The "
            "available interpreters expose no torch or librosa, wheel hashes "
            "are not recorded and deterministic algorithms were not enabled.",
            "Provide a locked offline environment with every wheel hash, one "
            "install/import digest, deterministic algorithms, seed 20261101 "
            "and 1/1 threads, then reproduce one training step."),
        _gate(
            "RG-04", "logmel_frontend_and_feature_cache",
            "The 24-bin log-mel front end is documented, but no feature cache "
            "was persisted and no exact librosa/mel implementation, padding, "
            "normalization byte order or output digest is pinned.",
            "Persist the exact feature cache with SHA-256/byte count, or pin "
            "the front-end implementation and reproduce the cache digest from "
            "the qualified corpus."),
        _gate(
            "RG-05", "rights_cleared_rate_cohort_and_labels",
            "The historical cohort is one AMI EN2003a meeting with "
            "CMUdict-derived labels. AMI, annotation and CMUdict terms are "
            "unreviewed, and no independent meeting/accent/language coverage "
            "exists.",
            "Freeze a permitted, multi-meeting, speaker-disjoint cohort with "
            "reviewed corpus/dictionary terms, checked syllable labels, "
            "language groups and source timestamps."),
        _gate(
            "RG-06", "reproduced_quality_and_control_results",
            "No five-fold CV, baseline comparison, finite-output scan or "
            "adverse/missing control was reproduced. The recorded run barely "
            "beat the constant baseline and had r=.124, which is context only.",
            "Reproduce the fixed five-fold protocol on the qualified cohort "
            "with a frozen scorer, baseline, fold stability, finite-output "
            "checks and adverse/missing/nonfinite controls."),
        _gate(
            "RG-07", "rate_profile_and_target_device_timing",
            "No Rate-profile mapping, buffering, rate-change, unfamiliar "
            "speech/music/silence, rebuffer/drift, final-window, pause/filler "
            "or target-device timing evidence exists.",
            "Score the exact Rate-profile cases and measure target-device "
            "p95/p99, resource, thermal/energy and deadline behavior under "
            "paced playback."),
        _gate(
            "RG-08", "off_by_default_provider_intake_and_release",
            "No provider, adapter, descriptor, registry/default/shared-build "
            "or CI change exists, and no release decision is available.",
            "Open a separate versioned OFF-by-default provider intake with an "
            "exact asset descriptor, clean-install proof and independent "
            "exact-head review after every prior gate clears."),
    ]


def exact_blockers() -> list[dict[str, Any]]:
    return [
        {
            "id": "BLK-01",
            "artifact_id": "ART-02",
            "status": "open",
            "qualifies": False,
            "linked_gates": ["RG-02"],
            "statement": (
                "Only small_gru_last_fold.pt exists (SHA-256 "
                "8740b3078433f758c9d0b3106d5de40beae8653a1c9cc3ac49edb1a65a114e7f, "
                "27,792 bytes). The recipe saves only the final fold; "
                "checkpoints for folds 0-3 do not exist, so the OOF "
                "predictions cannot be reproduced from stored weights."),
            "required_action": (
                "Supply five fold state dicts (or one checkpoint plus a "
                "bit-exact retraining recipe) with SHA-256, byte counts and an "
                "explicit license/terms decision for the trained weights."),
        },
        {
            "id": "BLK-02",
            "artifact_id": "ART-03",
            "status": "open",
            "qualifies": False,
            "linked_gates": ["RG-03"],
            "statement": (
                "No pinned runtime exists. The historical environment "
                "data/envs/sylnet-py310 is absent; the available Python "
                "3.10.13/3.11.5/3.12.16 interpreters expose no torch or "
                "librosa. Exact librosa/NumPy/SciPy/SoundFile versions and "
                "wheel hashes are not recorded, and "
                "torch.use_deterministic_algorithms was not set."),
            "required_action": (
                "Provide a locked offline runtime with exact versions, wheel "
                "hashes, install/import digest, deterministic settings, seed "
                "20261101 and 1/1 threads, and record a clean import."),
        },
        {
            "id": "BLK-03",
            "artifact_id": "ART-04",
            "status": "open",
            "qualifies": False,
            "linked_gates": ["RG-04"],
            "statement": (
                "The log-mel feature tensor was held in memory and never "
                "persisted. The documented front end depends on the exact "
                "librosa version and defaults; no cache bytes or output digest "
                "are available."),
            "required_action": (
                "Persist the 401x24 log-mel cache with SHA-256/byte count, or "
                "pin the exact front-end implementation and reproduce the "
                "cache digest from the qualified corpus."),
        },
        {
            "id": "BLK-04",
            "artifact_id": "ART-05",
            "status": "open",
            "qualifies": False,
            "linked_gates": ["RG-05"],
            "statement": (
                "The historical cohort is one AMI EN2003a meeting with 210 "
                "four-second windows. Its syllable labels are CMUdict first "
                "pronunciations, not human nuclei; AMI, annotation and CMUdict "
                "terms are unreviewed."),
            "required_action": (
                "Freeze a rights-cleared, multi-meeting, speaker-disjoint rate "
                "cohort with checked labels, language/speaker groups, "
                "source-timestamp provenance and reviewed corpus/dictionary "
                "terms."),
        },
        {
            "id": "BLK-05",
            "artifact_id": "ART-06",
            "status": "open",
            "qualifies": False,
            "linked_gates": ["RG-06"],
            "statement": (
                "No local CV or control result exists. The recorded run gave "
                "MAE 1.142 against a 1.160 constant baseline with r=.124; that "
                "is provenance context, not a reproduced result."),
            "required_action": (
                "Reproduce the fixed five-fold protocol on the qualified "
                "cohort with a frozen scorer, baseline, fold stability, "
                "finite-output scan and adverse/missing/nonfinite controls."),
        },
        {
            "id": "BLK-06",
            "artifact_id": "ART-07",
            "status": "open",
            "qualifies": False,
            "linked_gates": ["RG-07", "RG-08"],
            "statement": (
                "No Rate-profile, listening, target-device timing, provider or "
                "release evidence exists. The historical 0.732 ms/clip is "
                "model-only CPU batch context on another host, not a device "
                "deadline or product claim."),
            "required_action": (
                "Complete the Rate profile, measure target-device paced "
                "timing/resources/deadlines, and open a separate OFF-by-default "
                "provider intake after all prior gates clear."),
        },
    ]


def required_artifacts() -> list[dict[str, Any]]:
    return [
        {
            "id": "ART-01",
            "kind": "research_recipe_recorded_results_and_final_checkpoint",
            "present": True,
            "verified": True,
            "blocked": False,
            "sha256": None,
            "revision": None,
            "requirement": (
                "The exact training script, recorded CV/timing/prediction "
                "results, cohort manifest, detailed report and the one "
                "final-fold checkpoint file, all pinned by SHA-256."),
        },
        {
            "id": "ART-02",
            "kind": "complete_trained_fold_checkpoints",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "revision": None,
            "requirement": (
                "Five fold state dicts, or one checkpoint plus a bit-exact "
                "retraining recipe, each with SHA-256 and byte count and a "
                "reviewed trained-weight license/terms decision."),
        },
        {
            "id": "ART-03",
            "kind": "pinned_runtime",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "revision": None,
            "requirement": (
                "A locked offline Python 3.10.13, torch 2.2.2 and "
                "librosa/NumPy/SciPy/SoundFile runtime with wheel hashes, "
                "install/import digest and deterministic settings."),
        },
        {
            "id": "ART-04",
            "kind": "feature_cache_or_pinned_frontend",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "revision": None,
            "requirement": (
                "The exact persisted 401x24 log-mel feature cache with digest, "
                "or a pinned front-end that reproduces the cache digest."),
        },
        {
            "id": "ART-05",
            "kind": "rights_cleared_rate_cohort",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "revision": None,
            "requirement": (
                "A rights-cleared, multi-meeting rate cohort with reviewed "
                "AMI/annotation/CMUdict terms, checked syllable labels, "
                "language/speaker groups and source timestamps."),
        },
        {
            "id": "ART-06",
            "kind": "reproduced_quality_results",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "revision": None,
            "requirement": (
                "A reproduced five-fold CV with baseline, fold stability, "
                "finite-output, adverse/missing and nonfinite controls."),
        },
        {
            "id": "ART-07",
            "kind": "rate_profile_and_device_timing",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "revision": None,
            "requirement": (
                "Exact Rate-profile mapping, duration, pitch/transient, "
                "buffering, condition, rebuffer/drift, final-window, "
                "pause/filler and target-device timing evidence."),
        },
        {
            "id": "ART-08",
            "kind": "provider_intake",
            "present": False,
            "verified": False,
            "blocked": True,
            "sha256": None,
            "revision": None,
            "requirement": (
                "A separate versioned OFF-by-default SDK provider intake with "
                "empty descriptor settings, no registry/default/shared-build "
                "change and independent exact-head review."),
        },
    ]


def public_v0_geometry() -> dict[str, Any]:
    return {
        "changed": False,
        "channels": 1,
        "frame_samples": 160,
        "sample_format": "float32",
        "sample_rate_hz": 16000,
    }


def qualification() -> dict[str, Any]:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "not_qualified": True,
        "all_release_gates_blocked": True,
        "source_present": True,
        "weights_present": False,
        "checkpoint_present": False,
        "last_fold_checkpoint_present": True,
        "feature_cache_present": False,
        "runtime_present": False,
        "license_present": False,
        "real_result_present": False,
        "cv_result": False,
        "rate_profile_result": False,
        "device_timing_result": False,
        "listening_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
    }


def scope() -> dict[str, Any]:
    return {
        "task_local_only": True,
        "write_scope": WRITE_SCOPE,
        "provider_registered": False,
        "adapter_implemented": False,
        "benchmark_run": False,
        "device_timing_measured": False,
        "listening_performed": False,
        "network_used": False,
        "real_assets_used": False,
        "public_abi_changed": False,
        "registry_or_default_changed": False,
        "shared_build_or_ci_changed": False,
        "release_claim": False,
    }


def boundary() -> dict[str, Any]:
    row = board_row_projection()
    rows = linked_rows()
    return {
        "linked_row": row,
        "linked_row_sha256": object_digest(row),
        "linked_rows": rows,
        "linked_rows_sha256": linked_rows_digest(rows),
        "linked_row_identity_only": True,
        "board_file_pinned": False,
        "mutable_board_fields_gate": False,
        "projected_fields": list(BOARD_ROW_FIELDS),
    }


def checkpoint_provenance() -> dict[str, Any]:
    checkpoint = documented_checkpoint()
    if not checkpoint["present"]:
        raise ValueError("final_fold_checkpoint_missing")
    if checkpoint["sha256"] != CHECKPOINT_SHA256:
        raise ValueError("final_fold_checkpoint_digest")
    if checkpoint["byte_count"] != CHECKPOINT_BYTE_COUNT:
        raise ValueError("final_fold_checkpoint_bytes")
    return {
        "filename": CHECKPOINT_FILENAME,
        "path": checkpoint["path"],
        "present": True,
        "sha256": CHECKPOINT_SHA256,
        "byte_count": CHECKPOINT_BYTE_COUNT,
        "scope": "final fold only",
        "all_five_fold_checkpoints_present": False,
        "loaded": False,
        "decoded": False,
        "pinned": True,
    }


def build_contract() -> dict[str, Any]:
    rule = architecture_reference()
    if not rule["all_checks_pass"]:
        raise ValueError("architecture_recipe_check_failed")
    if rule["computed_parameter_count"] != PARAMETER_COUNT:
        raise ValueError("architecture_parameter_count_mismatch")
    metrics = documented_metrics()
    checkpoint = checkpoint_provenance()
    return {
        "schema_id": CONTRACT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "disposition": DISPOSITION,
        "qualification": qualification(),
        "scope": scope(),
        "boundary": boundary(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_model": {
            "name": MODEL_NAME,
            "class": MODEL_CLASS,
            "initialization": "random; no pretrained weights",
            "pretrained_weights_used": False,
            "input_shape": [FRAMES_PER_WINDOW, GRU_INPUT_SIZE],
            "gru_hidden": GRU_HIDDEN_SIZE,
            "head": [HEAD_HIDDEN_SIZE, HEAD_OUTPUT_SIZE],
            "classes": 1,
            "activation": "softplus",
            "parameter_count": PARAMETER_COUNT,
            "checkpoint_filename": CHECKPOINT_FILENAME,
            "checkpoint_present": False,
            "last_fold_checkpoint_present": True,
            "downloaded_or_reconstructed": False,
        },
        "checkpoint_provenance": checkpoint,
        "frontend_contract": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "window_samples": WINDOW_SAMPLES,
            "window_seconds": COHORT_WINDOW_SECONDS,
            "n_fft": N_FFT,
            "hop_length": HOP_LENGTH,
            "n_mels": N_MELS,
            "power": "2.0",
            "log_offset": "1e-10",
            "center": True,
            "normalization": "fold_train_mean_std",
            "frames_per_window": FRAMES_PER_WINDOW,
            "fft_bins": FFT_BINS,
            "values_per_window": VALUES_PER_WINDOW,
            "cohort_values": COHORT_MEL_VALUES,
            "resize_stage": False,
        },
        "runtime_recorded": {
            "python": RUNTIME_PYTHON,
            "torch": RUNTIME_TORCH,
            "librosa": None,
            "numpy": None,
            "scipy": None,
            "soundfile": None,
            "device": "cpu",
            "intra_op_threads": CPU_THREADS,
            "interop_op_threads": INTEROP_THREADS,
            "deterministic_algorithms": False,
            "offline": False,
            "runtime_present": False,
        },
        "training_recipe_recorded": {
            "seed": SEED,
            "epochs_per_fold": EPOCHS_PER_FOLD,
            "batch_size": BATCH_SIZE,
            "folds": FOLDS,
            "optimizer": "adam",
            "learning_rate": "0.001",
            "weight_decay": "0.0001",
            "loss": "mse",
            "split": "five contiguous chronological folds",
            "checkpoint_saved": True,
            "checkpoint_scope": "final fold only",
            "checkpoint_present": False,
            "last_fold_checkpoint_present": True,
            "executed_here": False,
        },
        "documented_provenance": {
            key: metrics[key]
            for key in ("provenance_only", "reproduced_here",
                        "used_for_evidence", "qualifies", "conclusion_recorded")
        },
        "admission_schema": admission_schema(),
        "rate_profile_requirements": rate_profile_requirements(),
        "quality_outcomes": quality_outcomes(),
        "timing_requirements": timing_requirements(),
        "release_gates": release_gates(),
        "exact_blockers": exact_blockers(),
        "required_artifacts": required_artifacts(),
        "required_results": REQUIRED_RESULTS,
        "non_claims": NON_CLAIMS,
    }


def build_report() -> dict[str, Any]:
    contract = build_contract()
    workspace = absence_probes(AUDIO_ROOT)
    home = home_absence_probes()
    summary = absence_summary(workspace, home)
    presence = source_presence()
    checkpoint = documented_checkpoint()
    frontend = frontend_reference()
    architecture = architecture_reference()
    predictions = recorded_prediction_reference()
    if not frontend["all_checks_pass"]:
        raise ValueError("frontend_reference_check_failed")
    if not architecture["all_checks_pass"]:
        raise ValueError("architecture_reference_check_failed")
    if not predictions["recomputed_matches_recorded"]:
        raise ValueError("recorded_prediction_check_failed")
    if checkpoint["present"] is not True or checkpoint["contradiction"]:
        raise ValueError("checkpoint_presence_contradiction")
    if checkpoint["all_five_fold_checkpoints_present"]:
        raise ValueError("all_fold_checkpoint_claim")
    if presence["fold_checkpoints_present"]:
        raise ValueError("fold_checkpoint_present")
    if presence["feature_cache_present"]:
        raise ValueError("feature_cache_present")
    if presence["runtime_present"]:
        raise ValueError("runtime_present")
    if presence["exact_source_weights_runtime_conjunction_present"]:
        raise ValueError("source_weights_runtime_present")
    cases = admission_cases()
    control = admission_control()
    metrics = documented_metrics()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "contract_sha256": object_digest(contract),
        "disposition": contract["disposition"],
        "qualification": contract["qualification"],
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "exact_model": contract["exact_model"],
        "checkpoint_provenance": contract["checkpoint_provenance"],
        "frontend_contract": contract["frontend_contract"],
        "runtime_recorded": contract["runtime_recorded"],
        "training_recipe_recorded": contract["training_recipe_recorded"],
        "documented_provenance": metrics,
        "recipe_provenance": recipe_provenance(),
        "architecture_reference": architecture,
        "frontend_reference": frontend,
        "recorded_prediction_reference": predictions,
        "absence_evidence": {
            "summary": summary,
            "workspace_probes": workspace,
            "home_probes": home,
            "documented_checkpoint": checkpoint,
        },
        "source_presence": presence,
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "exact_inputs": input_inventory(),
        "admission": {
            "summary": {
                "case_count": len(cases),
                "rejected_count": sum(1 for case in cases
                                      if case["status"] == "rejected"),
                "accepted_schema_controls": 1,
                "qualifying_results": 0,
                "state_advanced_on_rejection": False,
                "runtime_invoked": False,
                "audio_read": False,
                "weights_loaded": False,
                "model_executed": False,
                "network_used": False,
            },
            "cases": cases,
            "control": control,
        },
        "quality_outcomes": {"rows": contract["quality_outcomes"]},
        "timing": {"rows": contract["timing_requirements"]},
        "rate_profile": {"rows": contract["rate_profile_requirements"]},
        "gates": contract["release_gates"],
        "exact_blockers": contract["exact_blockers"],
        "required_artifacts": contract["required_artifacts"],
        "required_results": contract["required_results"],
        "non_claims": contract["non_claims"],
        "linked_row_identity": {
            "projection": contract["boundary"]["linked_row"],
            "sha256": contract["boundary"]["linked_row_sha256"],
            "linked_rows": contract["boundary"]["linked_rows"],
            "linked_rows_sha256": contract["boundary"]["linked_rows_sha256"],
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
        },
        "input_inventory_digest": object_digest(input_inventory()),
    }
    _no_floats(report)
    return report


def canonical_report(report: dict[str, Any] | None = None) -> tuple[str, str]:
    value = report if report is not None else build_report()
    _no_floats(value)
    payload = canonical_bytes(value)
    return payload.decode("ascii"), sha256_bytes(payload)


def validate_contract(contract: dict[str, Any]) -> None:
    """Structural validation of the committed contract, without file reads."""
    if contract.get("schema_id") != CONTRACT_ID:
        raise ValueError("contract_schema")
    if contract.get("contract_schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_parent_schema")
    if contract.get("task") != TASK or contract.get("component") != COMPONENT_ID:
        raise ValueError("contract_identity")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != "incomplete":
        raise ValueError("contract_status")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal_only")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification_status")
    if contract.get("mode") != MODE or contract.get("profile") != PROFILE:
        raise ValueError("contract_mode_profile")
    if contract.get("base_commit") != BASE_COMMIT:
        raise ValueError("contract_base_commit")
    if contract.get("branch") != BRANCH:
        raise ValueError("contract_branch")
    qualification_block = contract.get("qualification")
    if not isinstance(qualification_block, dict):
        raise ValueError("contract_qualification")
    if qualification_block.get("status") != "not_qualified":
        raise ValueError("contract_qualification_status_block")
    if qualification_block.get("readiness") != "incomplete":
        raise ValueError("contract_readiness")
    for key in ("not_qualified", "all_release_gates_blocked",
                "last_fold_checkpoint_present"):
        if qualification_block.get(key) is not True:
            raise ValueError("contract_qualification_true:" + key)
    for key in ("weights_present", "checkpoint_present",
                "feature_cache_present", "runtime_present", "license_present",
                "real_result_present", "cv_result",
                "rate_profile_result", "device_timing_result",
                "listening_result", "benchmark_result", "release_claim",
                "missing_result_promoted"):
        if qualification_block.get(key) is not False:
            raise ValueError("contract_qualification_false:" + key)
    scope_block = contract.get("scope")
    for key in ("provider_registered", "adapter_implemented", "benchmark_run",
                "device_timing_measured", "listening_performed",
                "network_used", "real_assets_used", "public_abi_changed",
                "registry_or_default_changed", "shared_build_or_ci_changed",
                "release_claim"):
        if not isinstance(scope_block, dict) or scope_block.get(key) is not False:
            raise ValueError("contract_scope_false:" + key)
    if scope_block.get("task_local_only") is not True:
        raise ValueError("contract_scope_task_local")
    if scope_block.get("write_scope") != WRITE_SCOPE:
        raise ValueError("contract_scope_write")
    checkpoint = contract.get("checkpoint_provenance")
    if not isinstance(checkpoint, dict):
        raise ValueError("contract_checkpoint")
    if checkpoint.get("present") is not True:
        raise ValueError("contract_checkpoint_present")
    if checkpoint.get("sha256") != CHECKPOINT_SHA256:
        raise ValueError("contract_checkpoint_digest")
    if checkpoint.get("byte_count") != CHECKPOINT_BYTE_COUNT:
        raise ValueError("contract_checkpoint_bytes")
    if checkpoint.get("all_five_fold_checkpoints_present") is not False:
        raise ValueError("contract_checkpoint_complete")
    for key in ("loaded", "decoded"):
        if checkpoint.get(key) is not False:
            raise ValueError("contract_checkpoint_use:" + key)
    gates = contract.get("release_gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}":
            raise ValueError("contract_gate_id")
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            raise ValueError("contract_gate_blocked")
        if not gate.get("reopen_condition") or not gate.get("statement"):
            raise ValueError("contract_gate_text")
        if gate.get("linked_row") != contract["boundary"]["linked_row"]:
            raise ValueError("contract_gate_linked_row")
    blockers = contract.get("exact_blockers")
    if not isinstance(blockers, list) or len(blockers) != 6:
        raise ValueError("contract_blocker_count")
    artifact_ids = {row.get("id") for row in contract.get("required_artifacts", [])}
    gate_ids = {row.get("id") for row in gates}
    for blocker in blockers:
        if blocker.get("status") != "open" or blocker.get("qualifies") is not False:
            raise ValueError("contract_blocker_open")
        if blocker.get("artifact_id") not in artifact_ids:
            raise ValueError("contract_blocker_artifact")
        if not blocker.get("required_action"):
            raise ValueError("contract_blocker_action")
        for gate_id in blocker.get("linked_gates", []):
            if gate_id not in gate_ids:
                raise ValueError("contract_blocker_gate")
    artifacts = contract.get("required_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 8:
        raise ValueError("contract_artifact_count")
    if not (artifacts[0].get("present") is True
            and artifacts[0].get("verified") is True
            and artifacts[0].get("blocked") is False):
        raise ValueError("contract_source_artifact")
    for artifact in artifacts[1:]:
        if (artifact.get("present") is not False
                or artifact.get("verified") is not False
                or artifact.get("blocked") is not True
                or artifact.get("sha256") is not None):
            raise ValueError("contract_blocked_artifact:" + str(artifact.get("id")))
    for section, count in (("rate_profile_requirements", 8),
                           ("quality_outcomes", 4),
                           ("timing_requirements", 4)):
        rows = contract.get(section)
        if not isinstance(rows, list) or len(rows) != count:
            raise ValueError("contract_rows:" + section)
        for row in rows:
            if row.get("status") != "blocked" or row.get("value", None) is not None:
                raise ValueError("contract_row_blocked:" + section)
    if contract.get("frontend_contract", {}).get("frames_per_window") != 401:
        raise ValueError("contract_frontend_frames")
    if contract.get("frontend_contract", {}).get("values_per_window") != 9624:
        raise ValueError("contract_frontend_values")
    if contract.get("admission_schema", {}).get("schema_id") != ADMISSION_SCHEMA_ID:
        raise ValueError("contract_admission_schema")
    if contract.get("admission_schema", {}).get("exact_window_count") != 210:
        raise ValueError("contract_admission_windows")
    if contract.get("admission_schema", {}).get(
            "exact_parameter_count") != PARAMETER_COUNT:
        raise ValueError("contract_admission_parameters")
