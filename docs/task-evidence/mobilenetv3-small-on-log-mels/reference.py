# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-MOBILENETV3-SMALL-ON-LOG-MELS.

This module is standard-library only and deterministic. It contains no
MobileNetV3 weight, trained checkpoint, PyTorch/torchvision/librosa runtime,
audio signal, transcript, syllable label, inference path or model result. It
records the exact historical recipe, probes a fixed list of workspace,
environment and home-cache paths to evidence that the trained checkpoints,
feature cache and runtime are absent, validates a caller-supplied MobileNetV3
rate-cohort manifest with a fail-closed admission boundary, and builds the
canonical report.

The historical pilot trained a one-channel log-mel MobileNetV3-small from
scratch with torchvision 0.17.2 on 210 four-second AMI EN2003a windows. That
result is recorded as provenance only. This package does not reproduce,
confirm or extend it, and no result here qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import posixpath
import re
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-MOBILENETV3-SMALL-ON-LOG-MELS"
COMPONENT_ID = "mobilenetv3-small-on-log-mels"
TASK_TITLE = "MobileNetV3-small on log-mels"
CONTRACT_ID = "audio-sdk/mobilenetv3-small-on-log-mels-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/mobilenetv3-small-rate-cohort/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "implementation"
BASE_COMMIT = "82c0a6e6ee5811190588fe5d17254b494d42cd2c"
BRANCH = "swarm/SDK-MOBILENETV3-SMALL-ON-LOG-MELS"
WRITE_SCOPE = "docs/task-evidence/mobilenetv3-small-on-log-mels/ only"
TASK_PREFIX = "docs/task-evidence/mobilenetv3-small-on-log-mels/"
DISPOSITION = (
    "Caller-supplied MobileNetV3-small log-mel rate-regressor readiness "
    "blocker; no implementation, adapter, checkpoint or result.")

MODEL_NAME = "MobileNetV3-small"
TORCHVISION_MODEL = "torchvision.models.mobilenet_v3_small"
PARAMETER_COUNT = 1518593
SEED = 20261101
EPOCHS_PER_FOLD = 20
BATCH_SIZE = 42
FOLDS = 5
CPU_THREADS = 4
INTEROP_THREADS = 1
COHORT_WINDOW_COUNT = 210
COHORT_WINDOW_SECONDS = "4.0"
WINDOW_SAMPLES = 64000
SAMPLE_RATE_HZ = 16000
N_FFT = 400
HOP_LENGTH = 160
N_MELS = 24
RESIZE_HEIGHT = 24
RESIZE_WIDTH = 64
COHORT_MEL_VALUES = COHORT_WINDOW_COUNT * RESIZE_HEIGHT * RESIZE_WIDTH
RUNTIME_PYTHON = "3.10.13"
RUNTIME_TORCH = "2.2.2"
RUNTIME_TORCHVISION = "0.17.2"
CHECKPOINT_FILENAME = "mobilenet_rate_optimized_last_fold.pt"

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
    "research/tsm-followup-20261101/agent-neural/run/"
    "train_mobilenet_rate_optimized.py":
        "9e998642fe167437291bd3bbba538202c3e0056edd7c8483a4a8e53d68db768a",
    "research/tsm-followup-20261101/agent-neural/run/"
    "train_mobilenet_rate.py":
        "f8149f0158308f1cb2d267610f95fa522bf90d2f425249fd6b0ecdb67707acff",
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_optimized_results.json":
        "97389d23235bd853036f12c048b6e61e2b019f11aa42651a22be54f7dd7b69d8",
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_results.json":
        "848f727771102bab83265034cf6acdd46bc8b78209e8fb1e0ef827bbf7cac146",
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_optimized_progress.jsonl":
        "2a1d7a236c94d0da1e6835eda0543a03efe9d1f99e3c65aac7a7b8ee67c74ffe",
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_original_run_interrupt.txt":
        "6dcbe0bed125b92b1fa955f562922a46ec2b824c3bce09febdc72af33d47dfaf",
    "research/tsm-followup-20261101/agent-neural/run/syl_eval_manifest.json":
        "3c7b3731cf6d2312e42e3333cae03bc631f6d1dbf557b773e134468c867897e2",
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
    "research/tsm-followup-20261101/agent-neural/run/" + CHECKPOINT_FILENAME,
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_optimized_fold0.pt",
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_optimized_fold1.pt",
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_optimized_fold2.pt",
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_optimized_fold3.pt",
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_optimized_fold4.pt",
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_last_fold.pt",
)
WORKSPACE_PROBES = CHECKPOINT_PROBES + (
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_optimized_features.npz",
    "research/tsm-followup-20261101/agent-neural/run/"
    "mobilenet_rate_optimized_features.npy",
    "data/models/mobilenetv3-small-on-log-mels",
    "data/models/mobilenet_v3_small",
    "data/checkouts/mobilenetv3-small-on-log-mels",
    "data/checkouts/mobilenet-v3-small",
    "data/envs/sylnet-py310",
    "data/envs/mobilenetv3-rate-py310",
    "data/runs/mobilenet_rate_optimized",
)
HOME_PROBES = (
    ("pretrained_imagenet_checkpoint",
     ".cache/torch/hub/checkpoints/mobilenet_v3_small-047dcff8.pth"),
    ("torch_runtime",
     ".pyenv/versions/3.10.13/lib/python3.10/site-packages/torch/__init__.py"),
    ("torchvision_runtime",
     ".pyenv/versions/3.10.13/lib/python3.10/site-packages/torchvision/"
     "__init__.py"),
    ("librosa_runtime",
     ".pyenv/versions/3.10.13/lib/python3.10/site-packages/librosa/__init__.py"),
)

NON_CLAIMS = [
    "No MobileNetV3 weight, trained fold checkpoint or state dict is present.",
    "No PyTorch, torchvision or librosa runtime is imported or executed.",
    "No audio signal, feature array, model weight or log-mel cache is read or decoded.",
    "No transcript text, syllable label or prediction is extracted, used or scored.",
    "No cross-validation, accuracy, timing or baseline result is reproduced.",
    "No listening, device timing, benchmark, pipeline or release claim is made.",
    "No provider, registry, descriptor, public ABI, shared build or CI change exists.",
    "A syllables/second estimate is not a preferred speed factor or a TSM setting.",
    "The historical negative result is provenance context, not a local result or a product decision.",
]

REQUIRED_RESULTS = [
    "The exact torchvision 0.17.2 MobileNetV3-small source tree and a complete license/notice bundle.",
    "All five fold checkpoints (or one checkpoint plus a bit-exact retraining recipe) with SHA-256 and byte counts.",
    "A locked offline Python 3.10.13 / torch 2.2.2 / torchvision 0.17.2 / librosa runtime with wheel hashes.",
    "The exact persisted log-mel feature cache or a pinned front-end whose output digest is recorded.",
    "A rights-cleared, multi-meeting rate cohort with checked syllable labels and source timestamps.",
    "A reproduced five-fold CV result with baseline, fold stability, finite-output and adverse controls.",
    "Exact Rate-profile mapping, buffering, condition and speech-preservation evidence.",
    "Target-device p95/p99 timing, resource and deadline behavior.",
    "A separate OFF-by-default versioned provider intake and independent exact-head review.",
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
        "README.md": "candidate scorecard and negative finding",
        "REPORT.md": "detailed MobileNetV3 recipe and recorded result",
        "train_mobilenet_rate_optimized.py": "exact optimized training recipe",
        "train_mobilenet_rate.py": "original full-resolution recipe and interrupt history",
        "mobilenet_rate_optimized_results.json": "recorded CV, timing and checkpoint reference",
        "mobilenet_rate_results.json": "older two-epoch screen, history only",
        "mobilenet_rate_optimized_progress.jsonl": "per-epoch loss/time trace",
        "mobilenet_original_run_interrupt.txt": "interrupted original run history",
        "syl_eval_manifest.json": "cohort metadata and declared audio digest",
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


def source_presence() -> dict[str, Any]:
    run = (AUDIO_ROOT / "research/tsm-followup-20261101/agent-neural/run")
    manifest = _read_manifest()
    scripts = [
        run / "train_mobilenet_rate_optimized.py",
        run / "train_mobilenet_rate.py",
    ]
    results = [
        run / "mobilenet_rate_optimized_results.json",
        run / "mobilenet_rate_results.json",
    ]
    checkpoint = run / CHECKPOINT_FILENAME
    feature_caches = [
        run / "mobilenet_rate_optimized_features.npz",
        run / "mobilenet_rate_optimized_features.npy",
    ]
    runtime_paths = [
        Path.home() / HOME_PROBES[1][1],
        Path.home() / HOME_PROBES[2][1],
        Path.home() / HOME_PROBES[3][1],
    ]
    scripts_present = all(path.is_file() for path in scripts)
    results_present = all(path.is_file() for path in results)
    progress_present = (run / "mobilenet_rate_optimized_progress.jsonl").is_file()
    interrupt_present = (run / "mobilenet_original_run_interrupt.txt").is_file()
    manifest_present = (run / "syl_eval_manifest.json").is_file()
    report_present = (
        AUDIO_ROOT / "research/tsm-followup-20261101/agent-neural/REPORT.md"
    ).is_file()
    checkpoint_present = checkpoint.is_file()
    fold_checkpoints_present = any(
        (run / f"mobilenet_rate_optimized_fold{fold}.pt").is_file()
        for fold in range(FOLDS))
    feature_cache_present = any(path.is_file() for path in feature_caches)
    runtime_present = any(path.is_file() for path in runtime_paths)
    return {
        "research_scripts_present": scripts_present,
        "recorded_results_present": results_present,
        "progress_trace_present": progress_present,
        "interrupt_note_present": interrupt_present,
        "cohort_manifest_present": manifest_present,
        "detailed_report_present": report_present,
        "documented_checkpoint_present": checkpoint_present,
        "fold_checkpoints_present": fold_checkpoints_present,
        "feature_cache_present": feature_cache_present,
        "runtime_present": runtime_present,
        "exact_source_weights_runtime_conjunction_present": bool(
            scripts_present and checkpoint_present and feature_cache_present
            and runtime_present),
        "weights_used": False,
        "runtime_imported": False,
        "audio_read": False,
        "model_executed": False,
        "declared_recording": manifest.get("recording"),
        "declared_recording_sha256": manifest.get("recording_sha256"),
        "declared_annotation_archive_sha256": manifest.get(
            "annotation_archive_sha256"),
        "declared_recording_digest_verified_here": False,
        "cohort_window_count": manifest.get("count"),
        "cohort_meeting_count": 1,
    }


def documented_checkpoint() -> dict[str, Any]:
    run = (AUDIO_ROOT / "research/tsm-followup-20261101/agent-neural/run")
    report = (AUDIO_ROOT
              / "research/tsm-followup-20261101/agent-neural/REPORT.md")
    text = report.read_text(encoding="utf-8")
    return {
        "filename": CHECKPOINT_FILENAME,
        "path": "research/tsm-followup-20261101/agent-neural/run/"
                + CHECKPOINT_FILENAME,
        "documented_in_report": CHECKPOINT_FILENAME in text,
        "documented_scope": "final fold only, not all five folds",
        "all_five_fold_checkpoints_present": False,
        "present": (run / CHECKPOINT_FILENAME).is_file(),
        "contradiction": (CHECKPOINT_FILENAME in text
                          and not (run / CHECKPOINT_FILENAME).is_file()),
    }


def _script_text() -> str:
    return (AUDIO_ROOT
            / "research/tsm-followup-20261101/agent-neural/run/"
              "train_mobilenet_rate_optimized.py").read_text(encoding="utf-8")


def architecture_recipe() -> dict[str, Any]:
    text = _script_text()
    checks = {
        "torchvision_mobilenet_v3_small": "mobilenet_v3_small(" in text,
        "random_initialization": "mobilenet_v3_small(weights=None)" in text,
        "no_pretrained_flag": ("pretrained=True" not in text
                               and 'weights="IMAGENET' not in text),
        "one_channel_first_conv": (
            "nn.Conv2d(1, first.out_channels" in text),
        "single_output_classifier": (
            "self.net.classifier[-1] = nn.Linear(" in text
            and "self.net.classifier[-1].in_features, 1" in text),
        "softplus_output": "F.softplus(self.net(x))" in text,
        "seed_locked": "SEED = 20261101" in text
                       and "torch.manual_seed(SEED)" in text,
        "threads_locked": "THREADS = 4" in text
                          and "torch.set_num_threads(THREADS)" in text
                          and "torch.set_num_interop_threads(1)" in text,
        "twenty_epochs": "EPOCHS = 20" in text,
        "batch_42": "BATCH = 42" in text,
        "adam_recipe": (
            "Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)" in text),
        "channels_last": (
            "memory_format=torch.channels_last" in text),
        "five_chronological_folds": (
            "np.array_split(np.argsort(starts), 5)" in text),
        "checkpoint_save": (
            "torch.save(last_model.state_dict()" in text
            and CHECKPOINT_FILENAME in text),
    }
    return {
        "model": TORCHVISION_MODEL,
        "initialization": "random; no ImageNet weights",
        "pretrained_weights_used": False,
        "input_channels": 1,
        "input_shape": [1, RESIZE_HEIGHT, RESIZE_WIDTH],
        "classes": 1,
        "activation": "softplus",
        "parameter_count": PARAMETER_COUNT,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "checkpoint_filename": CHECKPOINT_FILENAME,
        "checkpoint_saved_by_recipe": True,
        "checkpoint_present": False,
        "script_sha256": SOURCE_PINS[
            "research/tsm-followup-20261101/agent-neural/run/"
            "train_mobilenet_rate_optimized.py"],
        "executed_here": False,
    }


def frontend_geometry() -> dict[str, Any]:
    frames = 1 + WINDOW_SAMPLES // HOP_LENGTH
    padded = WINDOW_SAMPLES + N_FFT
    fft_bins = N_FFT // 2 + 1
    values = RESIZE_HEIGHT * RESIZE_WIDTH
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
        "frames": frames,
        "fft_bins": fft_bins,
        "resize": [RESIZE_HEIGHT, RESIZE_WIDTH],
        "values_per_window": values,
        "cohort_values": COHORT_MEL_VALUES,
    }


def resize_axis(in_size: int, out_size: int) -> list[tuple[int, int,
                                                         Fraction, Fraction]]:
    """Exact PyTorch bilinear source indices/weights, align_corners=False.

    Only integer sizes are accepted. The arithmetic uses `Fraction`, so the
    result is independent of floating-point rounding and platform math
    libraries. This is a documented resize-arithmetic reference, not a feature
    extraction or a model execution.
    """
    if isinstance(in_size, bool) or isinstance(out_size, bool):
        raise ValueError("resize_bool")
    if not isinstance(in_size, int) or not isinstance(out_size, int):
        raise ValueError("resize_not_int")
    if in_size <= 0 or out_size <= 0:
        raise ValueError("resize_nonpositive")
    scale = Fraction(in_size, out_size)
    rows: list[tuple[int, int, Fraction, Fraction]] = []
    for dst in range(out_size):
        source = Fraction(2 * dst + 1, 2) * scale - Fraction(1, 2)
        if source < 0:
            source = Fraction(0)
        lower = int(source)
        if lower > in_size - 1:
            lower = in_size - 1
        upper = min(lower + 1, in_size - 1)
        if upper == lower:
            weight_upper = Fraction(0)
        else:
            weight_upper = source - lower
        weight_lower = Fraction(1) - weight_upper
        if weight_lower < 0 or weight_upper < 0:
            raise ValueError("resize_negative_weight")
        if weight_lower + weight_upper != 1:
            raise ValueError("resize_mass")
        if not (0 <= lower < in_size and 0 <= upper < in_size):
            raise ValueError("resize_index")
        rows.append((lower, upper, weight_lower, weight_upper))
    return rows


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    getcontext().prec = 60
    decimal = Decimal(value.numerator) / Decimal(value.denominator)
    text = format(decimal, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in ("-0", ""):
        return "0"
    return text


def _axis_digest(rows: list[tuple[int, int, Fraction, Fraction]]) -> str:
    lines = []
    for dst, (lower, upper, weight_lower, weight_upper) in enumerate(rows):
        lines.append(
            f"{dst}:{lower}:{upper}:"
            f"{weight_lower.numerator}/{weight_lower.denominator}:"
            f"{weight_upper.numerator}/{weight_upper.denominator}")
    return sha256_bytes("\n".join(lines).encode("ascii"))


def resize_summary() -> dict[str, Any]:
    height = resize_axis(RESIZE_HEIGHT, RESIZE_HEIGHT)
    width = resize_axis(401, RESIZE_WIDTH)
    height_identity = all(lower == dst and weight_lower == 1
                          and weight_upper == 0
                          for dst, (lower, upper, weight_lower, weight_upper)
                          in enumerate(height))
    if not height_identity:
        raise ValueError("resize_height_not_identity")
    if any(weight_lower + weight_upper != 1
           for _, _, weight_lower, weight_upper in width):
        raise ValueError("resize_width_mass")
    weights = [weight for _, _, weight_lower, weight_upper in width
               for weight in (weight_lower, weight_upper)]
    scale = Fraction(401, RESIZE_WIDTH)
    positions = [
        max(Fraction(0), Fraction(2 * dst + 1, 2) * scale - Fraction(1, 2))
        for dst in range(RESIZE_WIDTH)
    ]
    # The 2-D grid is an outer product of the two axes. Digest every output
    # cell and its four source corners to pin the exact bilinear mapping.
    cells = []
    for row_index, (h0, h1, hw0, hw1) in enumerate(height):
        for column_index, (w0, w1, ww0, ww1) in enumerate(width):
            cells.append(
                f"{row_index}:{column_index}:"
                f"{h0}:{h1}:{w0}:{w1}:"
                f"{hw0.numerator}/{hw0.denominator}:"
                f"{hw1.numerator}/{hw1.denominator}:"
                f"{ww0.numerator}/{ww0.denominator}:"
                f"{ww1.numerator}/{ww1.denominator}")
    return {
        "input_shape": [RESIZE_HEIGHT, 401],
        "output_shape": [RESIZE_HEIGHT, RESIZE_WIDTH],
        "height_axis_identity": True,
        "width_source_min": _fraction_text(min(positions)),
        "width_source_max": _fraction_text(max(positions)),
        "weight_min": _fraction_text(min(weights)),
        "weight_max": _fraction_text(max(weights)),
        "weight_sum_per_axis_row": "1",
        "height_axis_sha256": _axis_digest(height),
        "width_axis_sha256": _axis_digest(width),
        "cell_grid_sha256": sha256_bytes("\n".join(cells).encode("ascii")),
        "cell_count": len(cells),
        "align_corners": False,
        "mode": "bilinear",
    }


def frontend_reference() -> dict[str, Any]:
    geometry = frontend_geometry()
    resize = resize_summary()
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
        "resize_is_24x64": geometry["resize"] == [24, 64],
        "cohort_values_are_322560": geometry["cohort_values"] == 322560,
        "resize_mass_conserved": resize["weight_sum_per_axis_row"] == "1",
        "resize_height_identity": resize["height_axis_identity"] is True,
        "script_has_n_fft_400": "n_fft=400" in script,
        "script_has_hop_160": "hop_length=160" in script,
        "script_has_n_mels_24": "n_mels=24" in script,
        "script_has_power_2": "power=2.0" in script,
        "script_has_log_offset": "np.log(mel + 1e-10)" in script,
        "script_has_resize": 'size=(24, 64)' in script
                             and 'mode="bilinear"' in script
                             and "align_corners=False" in script,
        "script_has_fold_normalization":
            "X[train_idx].mean(axis=(0, 2, 3), keepdims=True)" in script
            and "X[train_idx].std(axis=(0, 2, 3), keepdims=True)" in script,
    }
    return {
        "geometry": geometry,
        "resize": resize,
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
          "mobilenet_rate_optimized_results.json")


def documented_metrics() -> dict[str, Any]:
    result = _recorded_results()
    cv = result["cross_validation"]
    baseline = cv["training_fold_mean_baseline"]
    expected = {
        "mae": "2.7566285133361816",
        "rmse": "3.0773868560791016",
        "bias": "-2.728549003601074",
        "pearson": "-0.19302583407184123",
        "spearman": "-0.23494190136006463",
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
                for row in cv["folds"]]
    if len(fold_mae) != FOLDS:
        raise ValueError("recorded_fold_count_mismatch")
    return {
        "provenance_only": True,
        "reproduced_here": False,
        "used_for_evidence": False,
        "qualifies": False,
        "candidate": result["candidate"],
        "runtime_recorded": {
            "python": RUNTIME_PYTHON,
            "torch": result["runtime"]["torch"],
            "torchvision": result["runtime"]["torchvision"],
            "device": result["runtime"]["device"],
            "threads": result["runtime"]["threads"],
            "mps_available": result["runtime"]["mps_available"],
        },
        "model_recorded": {
            "initialization": result["model"]["initialization"],
            "parameter_count": result["model"]["parameter_count"],
            "epochs_per_fold": result["model"]["epochs_per_fold"],
            "batch_size": result["model"]["batch_size"],
            "optimizer": result["model"]["optimizer"],
            "training_seconds": _decimal_string(
                result["model"]["training_seconds"]),
        },
        "cv_recorded": {
            "n": cv["n"],
            **observed,
            "fold_mae": fold_mae,
        },
        "timing_recorded": {
            "median_ms_per_clip": _decimal_string(
                result["inference_timing"]["median_ms_per_clip"]),
            "scope": result["inference_timing"]["scope"],
        },
        "feature_cache_recorded_seconds": _decimal_string(
            result["features"]["feature_cache_seconds"]),
        "conclusion_recorded": (
            "The full five-fold run underperformed the constant-fold-mean "
            "baseline on every aggregate metric; this is a poor fit on this "
            "single-meeting cohort, not a product validation."),
    }


def recipe_provenance() -> dict[str, Any]:
    metrics = documented_metrics()
    return {
        "executed_here": False,
        "checkpoint_saved_by_recipe": True,
        "checkpoint_present": False,
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
        "source_script_sha256": SOURCE_PINS[
            "research/tsm-followup-20261101/agent-neural/run/"
            "train_mobilenet_rate_optimized.py"],
        "source_results_sha256": SOURCE_PINS[
            "research/tsm-followup-20261101/agent-neural/run/"
            "mobilenet_rate_optimized_results.json"],
    }


ADMISSION_FIELDS = (
    "schema_id", "cohort_id", "architecture", "checkpoints", "runtime",
    "frontend", "audio", "labels", "controls", "outcomes", "rights")
ARCHITECTURE_FIELDS = (
    "model", "initialization", "pretrained", "input_channels", "input_shape",
    "classes", "activation", "parameter_count")
CHECKPOINT_FIELDS = ("fold", "sha256", "byte_count")
RUNTIME_FIELDS = (
    "python", "torch", "torchvision", "librosa", "numpy", "scipy",
    "soundfile", "device", "intra_op_threads", "interop_op_threads",
    "channels_last", "deterministic_algorithms", "offline", "seed")
FRONTEND_FIELDS = (
    "sample_rate_hz", "window_samples", "n_fft", "hop_length", "n_mels",
    "power", "log_offset", "center", "resize", "resize_mode",
    "align_corners", "normalization", "cache_sha256")
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
    "torchvision": RUNTIME_TORCHVISION,
    "device": "cpu",
    "intra_op_threads": CPU_THREADS,
    "interop_op_threads": INTEROP_THREADS,
    "channels_last": True,
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
    "resize": [RESIZE_HEIGHT, RESIZE_WIDTH],
    "resize_mode": "bilinear",
    "align_corners": False,
    "normalization": "fold_train_mean_std",
}


def _validate_architecture(value: Any) -> None:
    _require_exact_keys(value, ARCHITECTURE_FIELDS, "architecture_fields")
    if value["model"] != TORCHVISION_MODEL:
        raise AdmissionError("architecture_model")
    if value["initialization"] != "random":
        raise AdmissionError("architecture_initialization")
    if value["pretrained"] is not False:
        raise AdmissionError("architecture_pretrained")
    if value["input_channels"] != 1 or value["input_shape"] != [24, 64]:
        raise AdmissionError("architecture_shape")
    if value["classes"] != 1:
        raise AdmissionError("architecture_classes")
    if value["activation"] != "softplus":
        raise AdmissionError("architecture_activation")
    if value["parameter_count"] != PARAMETER_COUNT:
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
    for key in ("python", "torch", "torchvision"):
        if value[key] != RUNTIME_EXPECTED[key]:
            raise AdmissionError("runtime_version:" + key)
    for key in ("librosa", "numpy", "scipy", "soundfile"):
        _require_version(value[key], "runtime_version:" + key)
    for key in ("device", "intra_op_threads", "interop_op_threads",
                "channels_last", "deterministic_algorithms", "offline",
                "seed"):
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
        "cohort_id": "synthetic-schema-control",
        "architecture": {
            "model": TORCHVISION_MODEL,
            "initialization": "random",
            "pretrained": False,
            "input_channels": 1,
            "input_shape": [24, 64],
            "classes": 1,
            "activation": "softplus",
            "parameter_count": PARAMETER_COUNT,
        },
        "checkpoints": checkpoints,
        "runtime": {
            "python": RUNTIME_PYTHON,
            "torch": RUNTIME_TORCH,
            "torchvision": RUNTIME_TORCHVISION,
            "librosa": "0.10.1",
            "numpy": "1.26.4",
            "scipy": "1.11.4",
            "soundfile": "0.12.1",
            "device": "cpu",
            "intra_op_threads": CPU_THREADS,
            "interop_op_threads": INTEROP_THREADS,
            "channels_last": True,
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
            "resize": [RESIZE_HEIGHT, RESIZE_WIDTH],
            "resize_mode": "bilinear",
            "align_corners": False,
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

    def pretrained(doc: dict[str, Any]) -> None:
        doc["architecture"]["pretrained"] = True

    def wrong_params(doc: dict[str, Any]) -> None:
        doc["architecture"]["parameter_count"] = PARAMETER_COUNT + 1

    def wrong_channels(doc: dict[str, Any]) -> None:
        doc["architecture"]["input_channels"] = 3

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
        doc["runtime"]["intra_op_threads"] = 1

    def offline_false(doc: dict[str, Any]) -> None:
        doc["runtime"]["offline"] = False

    def wrong_n_fft(doc: dict[str, Any]) -> None:
        doc["frontend"]["n_fft"] = 512

    def wrong_mel_count(doc: dict[str, Any]) -> None:
        doc["frontend"]["n_mels"] = 40

    def wrong_resize(doc: dict[str, Any]) -> None:
        doc["frontend"]["resize"] = [64, 96]

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

    return (
        ("ADM-01", "runtime_fields", drop_runtime_torch),
        ("ADM-02", "admission_fields", add_extra_field),
        ("ADM-03", "schema_id", wrong_schema),
        ("ADM-04", "cohort_id", bad_cohort),
        ("ADM-05", "architecture_pretrained", pretrained),
        ("ADM-06", "architecture_parameter_count", wrong_params),
        ("ADM-07", "architecture_shape", wrong_channels),
        ("ADM-08", "checkpoint_count", missing_fold),
        ("ADM-09", "checkpoint_fold", duplicate_fold),
        ("ADM-10", "checkpoint_duplicate", duplicate_checkpoint),
        ("ADM-11", "checkpoint_bytes", zero_checkpoint_bytes),
        ("ADM-12", "runtime_version:torch", wrong_torch),
        ("ADM-13", "runtime_version:librosa", unpinned_librosa),
        ("ADM-14", "runtime_value:intra_op_threads", wrong_threads),
        ("ADM-15", "runtime_value:offline", offline_false),
        ("ADM-16", "frontend_value:n_fft", wrong_n_fft),
        ("ADM-17", "frontend_value:n_mels", wrong_mel_count),
        ("ADM-18", "frontend_value:resize", wrong_resize),
        ("ADM-19", "frontend_cache", bad_cache),
        ("ADM-20", "audio_count", drop_audio),
        ("ADM-21", "audio_path", duplicate_audio_path),
        ("ADM-22", "audio_id", duplicate_audio_id),
        ("ADM-23", "audio_digest", bad_audio_digest),
        ("ADM-24", "audio_span", wrong_span),
        ("ADM-25", "audio_rate", wrong_rate),
        ("ADM-26", "audio_meeting_count", one_meeting),
        ("ADM-27", "audio_language", wrong_language),
        ("ADM-28", "label_human", human_labels),
        ("ADM-29", "controls", missing_control),
        ("ADM-30", "outcome_nonfinite:mae_syllables_per_second", nan_outcome),
        ("ADM-31", "outcome_nonfinite:rmse_syllables_per_second",
         infinite_outcome),
        ("ADM-32", "outcome_range:pearson_r", outcome_range),
        ("ADM-33", "outcome_nonfinite_count", nonfinite_count),
        ("ADM-34", "rights_reference:review_reference", empty_rights),
        ("ADM-35", "rights_claims_qualified", claims_qualified),
        ("ADM-36", "audio_number:active_s", bool_as_number),
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
        "exact_model": TORCHVISION_MODEL,
        "exact_parameter_count": PARAMETER_COUNT,
        "exact_runtime": dict(RUNTIME_EXPECTED),
        "exact_frontend": {
            key: (
                list(value) if isinstance(value, list)
                else "2.0" if key == "power"
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
                "exists for a MobileNetV3 rate estimate."),
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
                "The recorded negative fold correlations are not recomputed; "
                "no per-fold predictions exist locally."),
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
            "evidence": "No MobileNetV3 inference was performed.",
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
            "The historical training script is pinned, but no torchvision "
            "0.17.2 source tree, complete license/notice bundle or reviewed "
            "product-use decision is staged.",
            "Stage the exact torchvision and dependency source/license/notice "
            "bundles, record the script revision and terms, and complete an "
            "independent license review."),
        _gate(
            "RG-02", "trained_weights_and_fold_checkpoints",
            "The report names mobilenet_rate_optimized_last_fold.pt, but the "
            "file is absent and only one final-fold checkpoint was ever saved; "
            "no fold checkpoint or state dict exists.",
            "Supply all five fold state dicts with SHA-256/byte counts, or a "
            "single checkpoint plus a bit-exact retraining recipe, and verify "
            "them against the recorded architecture and parameter count."),
        _gate(
            "RG-03", "pinned_deterministic_runtime",
            "The exact Python 3.10.13/torch 2.2.2/torchvision 0.17.2 runtime "
            "is absent. Librosa, NumPy, SciPy and SoundFile versions and wheel "
            "hashes are not recorded, and deterministic algorithms were not "
            "enabled in the script.",
            "Provide a locked offline environment with every wheel hash, one "
            "install/import digest, deterministic algorithms, the recorded "
            "seed and 4/1 threads, then reproduce one training step."),
        _gate(
            "RG-04", "logmel_frontend_and_feature_cache",
            "The 24x64 log-mel front end is documented, but no cache was "
            "persisted and no exact librosa/mel implementation, padding, "
            "normalization order or output digest is pinned.",
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
            "adverse/missing control was reproduced. The recorded run was "
            "worse than the constant baseline, which is context only.",
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
                "The report references mobilenet_rate_optimized_last_fold.pt, "
                "but the file is absent. The recipe saves only the final fold; "
                "checkpoints for folds 0-4 do not exist, so the OOF predictions "
                "cannot be reproduced from stored weights."),
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
                "data/envs/sylnet-py310 is absent; the available Python 3.10.13 "
                "interpreter has no torch, torchvision or librosa. Librosa, "
                "NumPy, SciPy and SoundFile versions and wheel hashes are not "
                "recorded, and torch.use_deterministic_algorithms was not set."),
            "required_action": (
                "Provide a locked offline runtime with exact versions, wheel "
                "hashes, install/import digest, deterministic settings, seed "
                "20261101 and 4/1 threads, and record a clean import."),
        },
        {
            "id": "BLK-03",
            "artifact_id": "ART-04",
            "status": "open",
            "qualifies": False,
            "linked_gates": ["RG-04"],
            "statement": (
                "The log-mel cache was held in memory and never persisted. The "
                "documented front end depends on the exact librosa version and "
                "defaults; no cache bytes or output digest are available."),
            "required_action": (
                "Persist the 24x64 log-mel cache with SHA-256/byte count, or "
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
                "No local CV or control result exists. The recorded full run "
                "gave MAE 2.757 against a 1.160 constant baseline with four "
                "negative fold correlations; that is provenance context, not a "
                "reproduced result."),
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
                "release evidence exists. The historical 5.37 ms/clip is "
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
            "kind": "research_recipe_and_recorded_results",
            "present": True,
            "verified": True,
            "blocked": False,
            "sha256": None,
            "revision": None,
            "requirement": (
                "The exact optimized/original MobileNetV3 training scripts, "
                "recorded CV results, progress trace, interrupt note, cohort "
                "manifest and detailed report pinned by SHA-256."),
        },
        {
            "id": "ART-02",
            "kind": "trained_fold_checkpoints",
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
                "A locked offline Python 3.10.13, torch 2.2.2, torchvision "
                "0.17.2 and librosa/NumPy/SciPy/SoundFile runtime with wheel "
                "hashes, install/import digest and deterministic settings."),
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
                "The exact persisted 24x64 log-mel feature cache with digest, "
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
        "feature_cache_present": False,
        "runtime_present": False,
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


def build_contract() -> dict[str, Any]:
    rule = architecture_recipe()
    if not rule["all_checks_pass"]:
        raise ValueError("architecture_recipe_check_failed")
    metrics = documented_metrics()
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
            "torchvision_model": TORCHVISION_MODEL,
            "initialization": "random; no ImageNet weights",
            "pretrained_weights_used": False,
            "input_channels": 1,
            "input_shape": [1, RESIZE_HEIGHT, RESIZE_WIDTH],
            "classes": 1,
            "activation": "softplus",
            "parameter_count": PARAMETER_COUNT,
            "checkpoint_filename": CHECKPOINT_FILENAME,
            "checkpoint_present": False,
            "downloaded_or_reconstructed": False,
        },
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
            "resize": [RESIZE_HEIGHT, RESIZE_WIDTH],
            "resize_mode": "bilinear",
            "align_corners": False,
            "normalization": "fold_train_mean_std",
            "frames_per_window": 401,
            "fft_bins": 201,
            "values_per_window": 1536,
            "cohort_values": COHORT_MEL_VALUES,
        },
        "runtime_recorded": {
            "python": RUNTIME_PYTHON,
            "torch": RUNTIME_TORCH,
            "torchvision": RUNTIME_TORCHVISION,
            "librosa": None,
            "numpy": None,
            "scipy": None,
            "soundfile": None,
            "device": "cpu",
            "intra_op_threads": CPU_THREADS,
            "interop_op_threads": INTEROP_THREADS,
            "channels_last": True,
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
    if not frontend["all_checks_pass"]:
        raise ValueError("frontend_reference_check_failed")
    if checkpoint["present"] or not checkpoint["documented_in_report"]:
        raise ValueError("checkpoint_presence_contradiction")
    if presence["documented_checkpoint_present"]:
        raise ValueError("documented_checkpoint_present")
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
        "frontend_contract": contract["frontend_contract"],
        "runtime_recorded": contract["runtime_recorded"],
        "training_recipe_recorded": contract["training_recipe_recorded"],
        "documented_provenance": metrics,
        "recipe_provenance": recipe_provenance(),
        "frontend_reference": frontend,
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
    for key in ("not_qualified", "all_release_gates_blocked"):
        if qualification_block.get(key) is not True:
            raise ValueError("contract_qualification_true:" + key)
    for key in ("weights_present", "checkpoint_present", "feature_cache_present",
                "runtime_present", "real_result_present", "cv_result",
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
    if contract.get("frontend_contract", {}).get("values_per_window") != 1536:
        raise ValueError("contract_frontend_values")
    if contract.get("admission_schema", {}).get("schema_id") != ADMISSION_SCHEMA_ID:
        raise ValueError("contract_admission_schema")
    if contract.get("admission_schema", {}).get("exact_window_count") != 210:
        raise ValueError("contract_admission_windows")
