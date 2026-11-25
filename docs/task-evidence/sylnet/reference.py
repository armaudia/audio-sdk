# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only surrogate for SDK-SYLNET task-local evidence.

This module is NOT SylNet source. It does not load a checkpoint, read audio,
download anything, invoke a vendor runtime, measure a device clock, conduct
listening, benchmark the SDK or qualify a release. It consumes caller-supplied
frozen synthetic feature frames over exact 64,000-sample windows and produces a
bounded, reproducible syllable-count proxy with strict fail-closed validation.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, Iterator, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-SYLNET"
TITLE = "SylNet"
SLUG = "sylnet"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "66b9f8d8724ed95e80ff2598781ff80fb5359988"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
STATUS = "proposal_only_synthetic_incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"

SAMPLE_RATE_HZ = 16000
WINDOW_SAMPLES = 64000
FRAME_SAMPLES = 160
FRAME_COUNT = WINDOW_SAMPLES // FRAME_SAMPLES
FINAL_PARTIAL_SAMPLES = 37
BANDS = 19
NS_PER_SAMPLE = 1_000_000_000 // SAMPLE_RATE_HZ
FIXTURE_EPOCH_NS = 1_767_225_600_000_000_000
CLOCK_ID = "fixture-monotonic-not-device"

CONDITIONS = (
    "speech",
    "unfamiliar_speech",
    "music",
    "silence",
    "rebuffer",
    "drift",
    "tail_partial",
)
RATE_CASES: Dict[str, Fraction] = {
    "rate_1x": Fraction(1, 1),
    "rate_0_8x": Fraction(4, 5),
    "rate_1_25x": Fraction(5, 4),
}

UPSTREAM_REPOSITORY = "https://github.com/shreyas253/SylNet"
UPSTREAM_REPOSITORY_STALE = "https://github.com/shjang-97/SylNet"
UPSTREAM_COMMIT = "29eb34d614907073735f9c2d8c31da22c1be2282"
UPSTREAM_LICENSE = "MIT"
UPSTREAM_SNAPSHOT = "data/checkouts/sylnet-evaluation"
UPSTREAM_LICENSE_PATH = UPSTREAM_SNAPSHOT + "/LICENSE"
UPSTREAM_CHECKPOINT_PATH = (
    UPSTREAM_SNAPSHOT + "/trained_models/model_trained.ckpt.data-00000-of-00001")
UPSTREAM_CHECKPOINT_BYTES = 33_806_412
UPSTREAM_REPORT_PATH = "research/tsm-followup-20261101/agent-neural/REPORT.md"
UPSTREAM_PREDICTIONS_PATH = (
    "research/tsm-followup-20261101/agent-neural/run/sylnet-predictions.txt")
UPSTREAM_PREDICTIONS_FILES_PATH = (
    "research/tsm-followup-20261101/agent-neural/run/sylnet-predictions_files.txt")

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/root-baselines/REPORT.md":
        "63ea22bd4d027467a1abe97639f7c9ff6e00cdc2c6c753a52c2bd5e4028bab85",
    UPSTREAM_REPORT_PATH:
        "f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73",
    UPSTREAM_PREDICTIONS_PATH:
        "28b4291e1adb1197735278a2a9c602aa6e4fc371acad34fe3b0d13c9be11b76f",
    UPSTREAM_PREDICTIONS_FILES_PATH:
        "b2787d4498b69430707741ed8d096edbb2e2ff563f876ff25a91b0f8e29ef77d",
    UPSTREAM_LICENSE_PATH:
        "d1442b2f494e4b639e8561912717c8082cef4989401f359a8134857fc514915c",
    UPSTREAM_SNAPSHOT + "/README.md":
        "7581fb7f5d6986dc2c2ff8e0542673451bb72394edcacab4784220f170849405",
    UPSTREAM_SNAPSHOT + "/run_SylNet_tf2.py":
        "d588b38a8bd38ce7b143e0e37660e22adaa9d295250b0248e15e086618683eb2",
    UPSTREAM_SNAPSHOT + "/SylNet_model_tf2.py":
        "663b4c4b0984b86c378601ab1887dd4751859329b016ed0e6933d60b5f943f1e",
    UPSTREAM_CHECKPOINT_PATH:
        "90aabcf981a8a68ce9a8003565c51bb576e8787461d841af9c61d47f7d7ba1e3",
    UPSTREAM_SNAPSHOT + "/trained_models/model_trained.ckpt.index":
        "6076f70f9175ea35ed77fdb8f106053b6cad8aee7f2299a75e53ae44e31ae1a2",
    UPSTREAM_SNAPSHOT + "/trained_models/model_trained.ckpt.meta":
        "0577000a8dc3f48ff97c9f61012bfdfe44bc7bd006c58c1fcb74156efed86894",
    UPSTREAM_SNAPSHOT + "/trained_models/means.npy":
        "52813c80049b322b3224c9afa1c6e05fe30109520f528e2d9685fb0567ae3e01",
    UPSTREAM_SNAPSHOT + "/trained_models/stds.npy":
        "3ce79025350250bd423c8992b7e0148f9eb4d24c0166f15bd4c2d50cd8c31cca",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
LOCAL_PIN_PATHS = (
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

FORMAT = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
    "window_samples": WINDOW_SAMPLES,
    "final_partial_samples": FINAL_PARTIAL_SAMPLES,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}
BOUNDARY = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "shared_cmakelists_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "ci_change": False,
}
SCOPE = {
    "synthetic_feature_trace_only": True,
    "task_local_only": True,
    "caller_supplied_frozen_features": True,
    "sylnet_source": False,
    "sylnet_checkpoint_loaded": False,
    "model_weights": False,
    "real_audio": False,
    "real_labels": False,
    "vendor_runtime_invoked": False,
    "device_timing": False,
    "listening_result": False,
    "rendered_playback": False,
    "benchmark_claim": False,
    "release_claim": False,
    "registered_provider": False,
}
NEGATIVE_CLAIMS = {
    "sylnet_source_executed": False,
    "checkpoint_or_weights_loaded": False,
    "network_download": False,
    "real_audio_read": False,
    "real_corpus_scored": False,
    "device_timing_measured": False,
    "listening_or_preference_result": False,
    "benchmark_or_release_claim": False,
    "provider_registration": False,
    "installed_v0_change": False,
    "abi_registry_default_change": False,
    "shared_build_or_ci_change": False,
}
EXACT_BLOCKERS = [
    "The exact upstream repository, commit, MIT LICENSE, source files and checkpoint bytes are pinned by SHA-256 from the external research checkout, but no SylNet source, checkpoint, config or weights asset is present in this SDK worktree; the model cannot be loaded or reproduced here.",
    "No SylNet runtime is installed in this worktree; the surrogate is an original thresholded feature proxy, not SylNet, and no exact approved reference output vector is available for parity.",
    "MIT covers the pinned upstream snapshot, but product/redistribution rights, training-data provenance and any separate model/weights terms are not established; no legal review exists and no asset may be vendored, built, packaged or redistributed.",
    "No rights-cleared real cohort, device timing, listening, benchmark or target-runtime evidence exists; every release gate remains blocked.",
]
MISSING_EVIDENCE = [
    "SylNet checkpoint, config and weights present in this worktree (hashes are pinned; assets are absent)",
    "installed SylNet runtime and canonical feature extraction in this worktree",
    "product/redistribution and training-data rights clearance; MIT source license is pinned but not sufficient",
    "rights-cleared held-out real speech cohort with exact labels",
    "independent listening or user-preference labels for desired playback rate",
    "target-device content/availability timing, memory and deadline evidence",
    "exact approved SylNet reference parity vector",
    "opt-in provider intake, descriptor and catalog review",
    "explicit public default selection",
]
GATE_NAMES = (
    "exact_checkpoint_config_rights",
    "real_cohort",
    "independent_listening_or_preference",
    "target_runtime_timing_memory",
    "provider_intake",
    "public_default_selection",
    "exact_reference_parity",
)
TOOL_PROVENANCE = [
    "No SylNet source, checkpoint, config, weight, audio file, device or vendor asset is present in this SDK worktree.",
    "Upstream repository, commit, MIT LICENSE, source files and checkpoint bytes are pinned by SHA-256 from an external research checkout; nothing is copied, vendored, built, downloaded or redistributed here.",
    "Only deterministic Python standard-library feature frames and a thresholded count proxy are executed.",
    "All real-model metrics quoted here are source-reported provenance and are never reproduced, pooled or used as thresholds.",
]
MODEL_PROVENANCE = {
    "candidate": "SylNet",
    "upstream_repository": UPSTREAM_REPOSITORY,
    "upstream_commit": UPSTREAM_COMMIT,
    "identity_correction": {
        "source_reported_repository": UPSTREAM_REPOSITORY_STALE,
        "source_reported_repository_status": "404_not_found",
        "corrected_repository": UPSTREAM_REPOSITORY,
        "corrected_repository_resolves_pinned_commit": True,
        "corrected_repository_resolves_pinned_bytes": True,
        "correction_reason": (
            "The pinned research report records the stale URL; the pinned "
            "commit and all pinned bytes resolve under the corrected repository."
        ),
    },
    "repository_resolution": {
        "snapshot": UPSTREAM_SNAPSHOT,
        "expected_remote": UPSTREAM_REPOSITORY,
        "expected_commit": UPSTREAM_COMMIT,
        "method": (
            "git config --get remote.origin.url and git rev-parse HEAD in the "
            "pinned external checkout"
        ),
    },
    "upstream_license": UPSTREAM_LICENSE,
    "upstream_license_copyright": "Copyright (c) 2019 Shreyas Seshadri",
    "upstream_license_file": UPSTREAM_LICENSE_PATH,
    "upstream_license_sha256": SOURCE_PINS[UPSTREAM_LICENSE_PATH],
    "primary_provenance_report": UPSTREAM_REPORT_PATH,
    "primary_provenance_report_sha256": SOURCE_PINS[UPSTREAM_REPORT_PATH],
    "source_snapshot": UPSTREAM_SNAPSHOT,
    "source_snapshot_in_sdk_worktree": False,
    "source_files": {
        "README.md": SOURCE_PINS[UPSTREAM_SNAPSHOT + "/README.md"],
        "run_SylNet_tf2.py": SOURCE_PINS[UPSTREAM_SNAPSHOT + "/run_SylNet_tf2.py"],
        "SylNet_model_tf2.py": SOURCE_PINS[UPSTREAM_SNAPSHOT + "/SylNet_model_tf2.py"],
    },
    "checkpoint": {
        "file": UPSTREAM_CHECKPOINT_PATH,
        "sha256": SOURCE_PINS[UPSTREAM_CHECKPOINT_PATH],
        "bytes": UPSTREAM_CHECKPOINT_BYTES,
        "index_sha256": SOURCE_PINS[
            UPSTREAM_SNAPSHOT + "/trained_models/model_trained.ckpt.index"],
        "meta_sha256": SOURCE_PINS[
            UPSTREAM_SNAPSHOT + "/trained_models/model_trained.ckpt.meta"],
        "tracked_in_upstream_commit": True,
        "present_in_sdk_worktree": False,
        "loaded_or_executed": False,
    },
    "feature_normalization": {
        "means_sha256": SOURCE_PINS[UPSTREAM_SNAPSHOT + "/trained_models/means.npy"],
        "stds_sha256": SOURCE_PINS[UPSTREAM_SNAPSHOT + "/trained_models/stds.npy"],
    },
    "runtime_source_reported": {
        "python": "3.10.13",
        "tensorflow": "2.12.0 tensorflow-macos",
        "frontend": (
            "16000 Hz mono; librosa melspectrogram n_mels=24, n_fft=400, "
            "hop_length=160; 20*log10; z-normalized; maximum output 91 syllables"
        ),
        "pilot_wall_seconds_210_clips": 88.03,
        "installed_in_sdk_worktree": False,
    },
    "pilot_artifacts": {
        "predictions": UPSTREAM_PREDICTIONS_PATH,
        "predictions_sha256": SOURCE_PINS[UPSTREAM_PREDICTIONS_PATH],
        "file_mapping": UPSTREAM_PREDICTIONS_FILES_PATH,
        "file_mapping_sha256": SOURCE_PINS[UPSTREAM_PREDICTIONS_FILES_PATH],
        "approved_reference_vector": False,
    },
    "asset_policy": (
        "Hash-pinned provenance only; no upstream source, checkpoint, config or "
        "weights asset is copied, vendored, built, downloaded or redistributed by "
        "this package."
    ),
}
LICENSING_ANALYSIS = {
    "task_files_license": "Apache-2.0",
    "upstream_repository_license": UPSTREAM_LICENSE,
    "upstream_license_text_pinned": True,
    "upstream_license_sha256": SOURCE_PINS[UPSTREAM_LICENSE_PATH],
    "upstream_license_scope": (
        "Pinned MIT LICENSE for the exact repository snapshot, including tracked "
        "checkpoint files as distributed at that commit; no separate model-card "
        "or weights terms were found in that snapshot."
    ),
    "mit_notice_obligation": (
        "Preserve the copyright and permission notice in copies or substantial "
        "portions; this package copies no upstream portion."
    ),
    "training_data_provenance_established": False,
    "separate_weights_terms_established": False,
    "redistribution_clearance": False,
    "product_use_clearance": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "exact_checkpoint_config_rights",
    "conclusion": (
        "MIT source licensing is pinned, but product/redistribution rights, "
        "training-data provenance and any separate model/weights terms are not "
        "cleared. The rights gate remains blocked; this package distributes no "
        "upstream asset."
    ),
}
SOURCE_REPORTED = {
    "status": "source_reported_not_reproduced",
    "used_for_qualification": False,
    "sources": [
        "research/tsm-followup-20261101/README.md",
        "research/tsm-followup-20261101/root-baselines/REPORT.md",
        UPSTREAM_REPORT_PATH,
    ],
    "scope": (
        "210 non-overlapping four-second EN2003a windows, CMUdict-derived syllable "
        "labels, one meeting, legacy-stack runtime overhead; no target-device or "
        "listening result."
    ),
    "findings": [
        {"metric": "count_mae", "value": 2.64},
        {"metric": "count_rmse", "value": 3.23},
        {"metric": "rate_mae_syllables_per_second", "value": 0.69},
        {"metric": "rate_rmse_syllables_per_second", "value": 0.85},
        {"metric": "rate_pearson_r", "value": 0.894},
    ],
    "detailed_pilot": {
        "source": UPSTREAM_REPORT_PATH,
        "status": "source_reported_not_reproduced",
        "used_for_qualification": False,
        "findings": [
            {"metric": "count_mae_syllables_per_window", "value": 2.643},
            {"metric": "count_rmse_syllables_per_window", "value": 3.226},
            {"metric": "count_bias_syllables_per_window", "value": 2.091},
            {"metric": "rate_mae_syllables_per_second", "value": 0.661},
            {"metric": "rate_pearson_r", "value": 0.896},
            {"metric": "pilot_wall_seconds_210_clips", "value": 88.03},
            {"metric": "checkpoint_size_mb", "value": 32},
            {"metric": "checkout_size_mb", "value": 69},
        ],
        "note": (
            "Transcribed from the pinned neural report only. Its rate MAE/r "
            "(0.661/0.896) differ from the pinned top-level README (0.69/0.894) "
            "for the same pilot; both are retained as source-reported values and "
            "neither is reproduced or used as a threshold."
        ),
    },
    "note": (
        "These numbers are transcribed from the pinned research reports only. "
        "This package neither reproduces nor claims them."
    ),
}

# Frozen caller-supplied synthetic window patterns. No audio is generated or read.
PATTERNS: Dict[str, Dict[str, Any]] = {
    "speech": {"period": 9, "level": 0.72, "gap": None, "unknown": (), "drift": 0.0},
    "unfamiliar_speech": {"period": 13, "level": 0.68, "gap": None,
                          "unknown": (120, 121, 122), "drift": 0.0},
    "music": {"period": 17, "level": 0.42, "gap": None, "unknown": (), "drift": 0.0},
    "silence": {"period": 400, "level": 0.03, "gap": None, "unknown": (), "drift": 0.0},
    "rebuffer": {"period": 11, "level": 0.70, "gap": (180, 205),
                 "unknown": (180, 181), "drift": 0.0},
    "drift": {"period": 10, "level": 0.66, "gap": None, "unknown": (), "drift": 0.15},
    "tail_partial": {"period": 8, "level": 0.74, "gap": None, "unknown": (), "drift": 0.0},
}
WEIGHTS = tuple(round(0.03 + 0.01 * index, 6) for index in range(BANDS))

CONFIG_KEYS = {
    "sample_rate_hz", "window_samples", "frame_samples", "bands",
    "threshold", "refractory_frames", "unknown_validity_policy",
}
DEFAULT_CONFIG: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "window_samples": WINDOW_SAMPLES,
    "frame_samples": FRAME_SAMPLES,
    "bands": BANDS,
    "threshold": 0.42,
    "refractory_frames": 6,
    "unknown_validity_policy": "retain_not_counted",
}


class Rejected(Exception):
    """Fail-closed surrogate rejection with a stable reason code."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_remote_url(url: str) -> str:
    """Normalize GitHub remote spelling so identity checks are stable."""
    value = url.strip()
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    elif value.startswith("ssh://git@github.com/"):
        value = "https://github.com/" + value.split("github.com/", 1)[1]
    if value.endswith(".git"):
        value = value[:-4]
    return value.rstrip("/")


@lru_cache(maxsize=1)
def upstream_git_identity() -> Dict[str, Any]:
    """Resolve the pinned checkout's origin URL and HEAD offline.

    This proves the pinned URL and commit agree in the checkout that supplies
    every pinned byte. It performs no network access and writes nothing.
    """
    snapshot = SOURCE_ROOT / UPSTREAM_SNAPSHOT

    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(snapshot), *args], capture_output=True,
            text=True, check=False)
        if result.returncode != 0:
            raise ValueError("git_upstream_failed:" + " ".join(args) + ":"
                             + result.stderr.strip())
        return result.stdout.strip()

    remote = git("config", "--get", "remote.origin.url")
    commit = git("rev-parse", "HEAD")
    git("cat-file", "-e", UPSTREAM_COMMIT + "^{commit}")
    return {
        "snapshot": str(snapshot),
        "remote": remote,
        "normalized_remote": normalize_remote_url(remote),
        "commit": commit,
        "pinned_commit_present": True,
    }


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
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def _reject_duplicate(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json_constant:" + token)


def strict_loads(text: str) -> Dict[str, Any]:
    """Strict JSON: reject duplicate keys, NaN/Infinity and non-object roots."""
    payload = json.loads(text, object_pairs_hook=_reject_duplicate,
                         parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise ValueError("root_not_object")
    return payload


PIN_RE = re.compile(r"^([0-9a-f]{64})  (\S+)$")


def allowed_pin_keys() -> set:
    keys = {"source:" + path for path in SOURCE_PINS}
    keys.update(BOUNDARY_PINS)
    keys.update(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)
    return keys


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Strict manifest parser: malformed, duplicate or unknown lines fail closed."""
    allowed = allowed_pin_keys()
    result: List[Tuple[str, str]] = []
    seen = set()
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith("#"):
            if not (line.startswith("# SHA-256 pins") or line.startswith("# source:")):
                raise ValueError("unexpected_comment:" + repr(line))
            continue
        match = PIN_RE.fullmatch(line)
        if not match:
            raise ValueError("malformed_pin:" + repr(line))
        digest, raw = match.groups()
        if raw in seen:
            raise ValueError("duplicate_pin:" + raw)
        relative = raw.split(":", 1)[1] if raw.startswith("source:") else raw
        if any(part in ("", ".", "..") for part in relative.split("/")):
            raise ValueError("traversing_pin:" + raw)
        if raw not in allowed:
            raise ValueError("unexpected_pin:" + raw)
        seen.add(raw)
        result.append((digest, raw))
    return result


def rng(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


@lru_cache(maxsize=None)
def frozen_frames(condition: str) -> List[Dict[str, Any]]:
    """Frozen caller-supplied feature frames; 19 floats per 160-sample frame."""
    if condition not in PATTERNS:
        raise Rejected("unknown_condition")
    spec = PATTERNS[condition]
    source = rng(20261125 + sum(ord(char) for char in condition))
    frames: List[Dict[str, Any]] = []
    for index in range(FRAME_COUNT):
        width = FRAME_SAMPLES
        first = index * FRAME_SAMPLES
        last = first + width
        valid_count = (FINAL_PARTIAL_SAMPLES if condition == "tail_partial"
                       and index == FRAME_COUNT - 1 else width)
        in_gap = spec["gap"] is not None and spec["gap"][0] <= index < spec["gap"][1]
        pulsed = index % spec["period"] == 0 and not in_gap
        level = spec["level"] * (1.0 if pulsed else 0.18)
        if spec["drift"]:
            level += spec["drift"] * (index / FRAME_COUNT) - spec["drift"] / 2
        level = min(1.0, max(0.0, level))
        features = []
        for band in range(BANDS):
            profile = 0.55 + 0.45 * math.sin((band + 1) * 0.37 + index * 0.031)
            value = level * profile * (0.94 + 0.12 * next(source))
            features.append(round(min(1.0, max(0.0, value)), 6))
        features[BANDS - 1] = round(0.85 if pulsed else 0.12, 6)
        frames.append({
            "epoch": 1,
            "window_index": CONDITIONS.index(condition),
            "source_first": first,
            "source_last": last,
            "valid_count": valid_count,
            "validity": "unknown" if index in spec["unknown"] else "known",
            "final": index == FRAME_COUNT - 1,
            "features": features,
        })
    return frames


def frozen_target_count(condition: str) -> int:
    """Frozen synthetic target count, not a human or corpus label."""
    spec = PATTERNS[condition]
    count = 0
    for index in range(FRAME_COUNT):
        if index in spec["unknown"]:
            continue
        if spec["gap"] is not None and spec["gap"][0] <= index < spec["gap"][1]:
            continue
        if index % spec["period"] == 0:
            count += 1
    return count


def validate_config(config: Any) -> Dict[str, Any]:
    """Strict config gate; every rejection happens before any state exists."""
    if not isinstance(config, dict):
        raise Rejected("config_not_object")
    if set(config) != CONFIG_KEYS:
        if CONFIG_KEYS - set(config):
            raise Rejected("config_missing_key")
        raise Rejected("config_unknown_key")
    for key in ("sample_rate_hz", "window_samples", "frame_samples", "bands",
                "threshold", "refractory_frames"):
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Rejected("config_wrong_type")
        if not math.isfinite(value):
            raise Rejected("config_nonfinite")
    if (config["sample_rate_hz"], config["window_samples"], config["frame_samples"],
            config["bands"]) != (SAMPLE_RATE_HZ, WINDOW_SAMPLES, FRAME_SAMPLES, BANDS):
        raise Rejected("config_out_of_range")
    if isinstance(config["threshold"], int) or not 0.0 < config["threshold"] < 1.0:
        raise Rejected("config_out_of_range")
    if (isinstance(config["refractory_frames"], float)
            or not 1 <= config["refractory_frames"] <= 40):
        raise Rejected("config_out_of_range")
    if config["unknown_validity_policy"] != "retain_not_counted":
        raise Rejected("config_unknown_key")
    return dict(config)


class Surrogate:
    """Task-local surrogate with fail-closed frame validation and no audio/weights."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = validate_config(DEFAULT_CONFIG if config is None else config)
        self.position = 0
        self.expected_epoch = 1
        self.window_index: int | None = None
        self.events: List[Dict[str, Any]] = []
        self.closed = False
        self.finished = False
        # Order-sensitive chained digest: O(1) per accepted frame, unchanged on
        # every rejection, and still deterministic across fresh interpreters.
        self._digest = sha256(canonical_bytes({
            "position": 0,
            "window_index": None,
            "closed": False,
            "finished": False,
            "events": [],
        }))

    def _advance_digest(self, label: str, payload: Any) -> None:
        self._digest = sha256(
            self._digest.encode("ascii") + b"\x00" + label.encode("ascii")
            + b"\x00" + canonical_bytes(payload))

    def state_digest(self) -> str:
        return self._digest

    def process(self, frame: Any) -> Dict[str, Any]:
        try:
            return self._process(frame)
        except Rejected as error:
            return {"status": "rejected", "reason": error.reason,
                    "state_digest": self.state_digest()}

    def _process(self, frame: Any) -> Dict[str, Any]:
        if self.closed or self.finished:
            raise Rejected("rejected_session")
        if not isinstance(frame, dict) or set(frame) != {
                "epoch", "window_index", "source_first", "source_last",
                "valid_count", "validity", "final", "features"}:
            raise Rejected("rejected_tensor")
        epoch = frame["epoch"]
        index = frame["window_index"]
        first = frame["source_first"]
        last = frame["source_last"]
        count = frame["valid_count"]
        for value in (epoch, index, first, last, count):
            if isinstance(value, bool) or not isinstance(value, int):
                raise Rejected("rejected_tensor")
        if epoch != self.expected_epoch:
            raise Rejected("rejected_epoch")
        if index not in range(len(CONDITIONS)):
            raise Rejected("rejected_window")
        if self.window_index is not None and self.window_index != index:
            raise Rejected("rejected_window")
        if first != self.position or last <= first:
            raise Rejected("rejected_position")
        width = last - first
        if (last > self.config["window_samples"] or width != self.config["frame_samples"]
                or count <= 0 or count > width):
            raise Rejected("rejected_tensor")
        if not isinstance(frame["final"], bool):
            raise Rejected("rejected_tensor")
        if not isinstance(frame["validity"], str):
            raise Rejected("rejected_validity")
        if frame["final"] and last != self.config["window_samples"]:
            raise Rejected("rejected_tensor")
        if not frame["final"] and count != width:
            raise Rejected("rejected_tensor")
        if frame["validity"] not in ("known", "unknown"):
            raise Rejected("rejected_validity")
        features = frame["features"]
        if not isinstance(features, list):
            raise Rejected("rejected_tensor")
        if len(features) != self.config["bands"]:
            raise Rejected("rejected_missing_features")
        for value in features:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise Rejected("rejected_features")
            if not math.isfinite(value):
                raise Rejected("rejected_nonfinite")
            if value < 0.0 or value > 1.0:
                raise Rejected("rejected_features")
        activation = round(sum(weight * float(value)
                               for weight, value in zip(WEIGHTS, features)), 9)
        if self.window_index is None:
            self.window_index = index
        event = {
            "window_index": index,
            "source_first": first,
            "source_last": last,
            "valid_count": count,
            "validity": frame["validity"],
            "final": frame["final"],
            "available_ns": FIXTURE_EPOCH_NS + last * NS_PER_SAMPLE,
            "activation": activation,
        }
        self.events.append(event)
        self.position = last
        self._advance_digest("accepted_event", {"position": last, "event": event})
        return {"status": "accepted", "event": event, "state_digest": self.state_digest()}

    def finish(self) -> Dict[str, Any]:
        if self.closed or self.finished:
            raise Rejected("rejected_session")
        if self.position != self.config["window_samples"]:
            raise Rejected("rejected_incomplete_window")
        self.finished = True
        self._advance_digest("finished", {"position": self.position,
                                          "event_count": len(self.events)})
        return {"status": "finished", "event_count": len(self.events),
                "state_digest": self.state_digest()}

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        self._advance_digest("closed", {"position": self.position})


def nuclei(events: Sequence[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Thresholded onset proxy; explicitly not a SylNet decoding path."""
    result: List[Dict[str, Any]] = []
    last_first = -(config["refractory_frames"] + 1) * config["frame_samples"]
    for event in events:
        if event["validity"] != "known":
            continue
        if event["activation"] < config["threshold"]:
            continue
        if event["source_first"] - last_first < config["refractory_frames"] * config["frame_samples"]:
            continue
        result.append({"source_first": event["source_first"],
                       "source_last": event["source_last"],
                       "activation": event["activation"]})
        last_first = event["source_first"]
    return result


def run_window(condition: str) -> Tuple[Surrogate, List[Dict[str, Any]]]:
    surrogate = Surrogate()
    for frame in frozen_frames(condition):
        outcome = surrogate.process(frame)
        if outcome["status"] != "accepted":
            raise Rejected("frozen_frame_rejected:" + outcome["reason"])
    surrogate.finish()
    return surrogate, nuclei(surrogate.events, surrogate.config)


def evaluate(condition: str, case: str) -> Dict[str, Any]:
    """Score one frozen 64,000-sample window with one specified rate case."""
    surrogate, peaks = run_window(condition)
    stop = WINDOW_SAMPLES
    count = len(peaks)
    target = frozen_target_count(condition)
    ratio = RATE_CASES[case]
    rate = Fraction(count * SAMPLE_RATE_HZ, stop)
    target_rate = Fraction(target * SAMPLE_RATE_HZ, stop)
    full = [event for event in surrogate.events if not event["final"]]
    partial = surrogate.events[-1]
    unknown = [event for event in surrogate.events if event["validity"] == "unknown"]
    return {
        "condition": condition,
        "rate_case": case,
        "specified_ratio": str(ratio),
        "source_interval": [0, stop],
        "target_output_samples": str(Fraction(stop, 1) / ratio),
        "renderer_executed": False,
        "duration_measured": False,
        "source_frame_count": len(surrogate.events),
        "accepted_frame_count": len(surrogate.events),
        "rejections": [],
        "event_intervals": [[event["source_first"], event["source_last"]]
                            for event in surrogate.events],
        "available_ns_first": surrogate.events[0]["available_ns"],
        "available_ns_last": partial["available_ns"],
        "clock_id": CLOCK_ID,
        "full_frame_count": len(full),
        "nuclei_count": count,
        "nuclei_intervals": [[peak["source_first"], peak["source_last"]] for peak in peaks],
        "frozen_target_count": target,
        "count_abs_error": abs(count - target),
        "rate_estimate": str(rate),
        "frozen_target_rate": str(target_rate),
        "rate_abs_error": str(abs(rate - target_rate)),
        "unknown_frames": len(unknown),
        "unknown_counted": sum(1 for event in unknown
                               if any(peak["source_first"] == event["source_first"]
                                      for peak in peaks)),
        "final_partial": {
            "source": [partial["source_first"], partial["source_last"]],
            "valid_count": partial["valid_count"],
            "final_flag": partial["final"],
            "available_ns": partial["available_ns"],
            "status": "accepted_exact_coordinates",
        },
        "estimation": "thresholded_feature_nuclei_proxy_not_sylnet",
        "pitch_status": "not_measured_no_rendered_audio",
        "transient_audibility": "not_measured_no_listening",
    }


def identity_control() -> Dict[str, Any]:
    """No estimation: exact source-to-source echo control."""
    target = frozen_target_count("speech")
    return {
        "name": "identity_no_estimation",
        "status": "measured_synthetic_control",
        "source_interval": [0, WINDOW_SAMPLES],
        "output_interval": [0, WINDOW_SAMPLES],
        "frozen_target_count": target,
        "reported_count": target,
        "count_abs_error": 0,
        "renderer_executed": False,
        "note": "Count error is zero by construction because no estimator runs.",
    }


def constant_count_control() -> Dict[str, Any]:
    """Synthetic constant-count control computed from frozen targets only."""
    targets = {condition: frozen_target_count(condition) for condition in CONDITIONS}
    ordered = sorted(targets.values())
    median = ordered[len(ordered) // 2]
    errors = {condition: abs(value - median) for condition, value in targets.items()}
    total = Fraction(sum(errors.values()), len(errors))
    return {
        "name": "frozen_constant_count_control",
        "status": "measured_synthetic_control",
        "frozen_targets": targets,
        "constant_count": median,
        "count_abs_errors": errors,
        "mean_abs_error": str(total),
        "note": "Synthetic control only; no research baseline is reproduced.",
    }


def mismatch_control() -> Dict[str, Any]:
    """Wrong-window and malformed inputs are rejected without moving state."""
    surrogate = Surrogate()
    first = frozen_frames("speech")[0]
    assert surrogate.process(first)["status"] == "accepted"
    before = surrogate.state_digest()
    wrong_window = dict(first, window_index=99)
    nonfinite = dict(first, features=list(first["features"]))
    nonfinite["features"][0] = float("nan")
    cases = {
        "wrong_window": wrong_window,
        "stale_epoch": dict(first, epoch=2),
        "nonfinite_features": nonfinite,
    }
    results = {}
    for name, frame in cases.items():
        outcome = surrogate.process(frame)
        results[name] = {"status": outcome["status"], "reason": outcome["reason"],
                         "state_unchanged": outcome["state_digest"] == before}
    return {"name": "identity_mismatch_rejection", "status": "measured_synthetic_control",
            "cases": results,
            "all_rejected": all(value["status"] == "rejected" for value in results.values()),
            "all_state_unchanged": all(value["state_unchanged"] for value in results.values())}


def controls() -> Dict[str, Any]:
    return {
        "identity": identity_control(),
        "named_baseline": constant_count_control(),
        "mismatch": mismatch_control(),
        "all_present": True,
    }


def _invalid_configs() -> List[Tuple[str, Dict[str, Any]]]:
    return [
        ("missing_key", {key: value for key, value in DEFAULT_CONFIG.items()
                         if key != "threshold"}),
        ("unknown_key", {**DEFAULT_CONFIG, "unexpected": 1}),
        ("wrong_type", {**DEFAULT_CONFIG, "threshold": "0.42"}),
        ("nonfinite", {**DEFAULT_CONFIG, "threshold": float("nan")}),
        ("out_of_range", {**DEFAULT_CONFIG, "window_samples": 32000}),
        ("boolean", {**DEFAULT_CONFIG, "refractory_frames": True}),
    ]


def _invalid_frames() -> List[Tuple[str, Dict[str, Any]]]:
    template = frozen_frames("speech")[0]
    wrong_shape = dict(template, features=list(template["features"])[:-1])
    missing = dict(template, features=[])
    nonfinite = dict(template, features=list(template["features"]))
    nonfinite["features"][0] = float("nan")
    out_of_range = dict(template, features=list(template["features"]))
    out_of_range["features"][0] = 1.5
    return [
        ("wrong_shape", wrong_shape),
        ("missing_features", missing),
        ("nonfinite", nonfinite),
        ("out_of_range", out_of_range),
        ("stale_epoch", dict(template, epoch=2)),
        ("stale_position", dict(template, source_first=1)),
        ("invalid_validity", dict(template, validity="invalid")),
        ("premature_final", dict(template, final=True)),
        ("wrong_window", dict(template, window_index=99)),
        ("wrong_type", dict(template, source_first="0")),
    ]


def adverse() -> Dict[str, Any]:
    config_cases = {}
    for name, config in _invalid_configs():
        try:
            Surrogate(config)
            config_cases[name] = {"status": "not_rejected", "controller_created": True}
        except Rejected as error:
            config_cases[name] = {"status": "rejected", "reason": error.reason,
                                  "controller_created": False}

    surrogate = Surrogate()
    before = surrogate.state_digest()
    frame_cases = {}
    for name, frame in _invalid_frames():
        outcome = surrogate.process(frame)
        frame_cases[name] = {"status": outcome["status"], "reason": outcome["reason"],
                             "state_unchanged": outcome["state_digest"] == before}
    frame_cases["dsp_state_unchanged"] = all(
        case["state_unchanged"] for name, case in frame_cases.items()
        if name != "dsp_state_unchanged")

    incomplete = Surrogate()
    for frame in frozen_frames("speech")[:-1]:
        assert incomplete.process(frame)["status"] == "accepted"
    missing_before = incomplete.state_digest()
    try:
        incomplete.finish()
        missing_frame = {"status": "not_rejected", "state_unchanged": False,
                         "reason": "none"}
    except Rejected as error:
        missing_frame = {"status": "rejected", "reason": error.reason,
                         "state_unchanged": incomplete.state_digest() == missing_before}

    closed = Surrogate()
    closed.close()
    after_close = closed.process(frozen_frames("speech")[0])
    finished = Surrogate()
    for frame in frozen_frames("speech"):
        assert finished.process(frame)["status"] == "accepted"
    finished.finish()
    after_finish = finished.process(frozen_frames("speech")[0])

    unknown_case = evaluate("unfamiliar_speech", "rate_1x")
    result = {
        "config_rejections": config_cases,
        "frame_rejections": frame_cases,
        "missing_frame": missing_frame,
        "lifecycle": {
            "close_then_process": {"status": after_close["status"],
                                   "reason": after_close["reason"]},
            "finish_then_process": {"status": after_finish["status"],
                                    "reason": after_finish["reason"]},
        },
        "validity": {
            "unknown_frames": unknown_case["unknown_frames"],
            "unknown_counted": unknown_case["unknown_counted"],
            "unknown_retained_not_counted": unknown_case["unknown_counted"] == 0,
            "invalid_excluded": frame_cases["invalid_validity"]["status"] == "rejected",
        },
    }
    result["all_rejected"] = (
        all(value["status"] == "rejected" for value in config_cases.values())
        and all(value["status"] == "rejected" for key, value in frame_cases.items()
                if key != "dsp_state_unchanged")
        and missing_frame["status"] == "rejected"
        and all(value["status"] == "rejected" for value in result["lifecycle"].values())
    )
    return result


def buffering(condition: str) -> Dict[str, Any]:
    """Fixture queue accounting only; no renderer, device or deadline."""
    frames = frozen_frames(condition)
    spec = PATTERNS[condition]
    gap_frames = (spec["gap"][1] - spec["gap"][0]) if spec["gap"] is not None else 0
    return {
        "clock_id": CLOCK_ID,
        "initial_fill_frames": 3,
        "consume_frames_per_tick": 1,
        "frame_count": len(frames),
        "modeled_peak_queue_samples": 3 * FRAME_SAMPLES,
        "fixture_rebuffer_gap_frames": gap_frames,
        "synthetic_level_drift": spec["drift"],
        "stale_position_case_exercised_in_adverse": True,
        "tail_partial_samples": FINAL_PARTIAL_SAMPLES if condition == "tail_partial" else 0,
        "device_clock_drift_measured": False,
        "deadline_measured": False,
        "status": "fixture_accounting_only",
    }


def gates() -> List[Dict[str, str]]:
    reopen = {
        "exact_checkpoint_config_rights": (
            "Place the pinned checkpoint/config/runtime in the worktree and clear "
            "product/redistribution and training-data rights."),
        "real_cohort": "Score a rights-cleared held-out real speech cohort with exact labels.",
        "independent_listening_or_preference": (
            "Collect independent listening or user-preference labels; count proxies cannot qualify."),
        "target_runtime_timing_memory": (
            "Measure content/availability timing, memory and deadlines on the exact target runtime."),
        "provider_intake": "Complete licensing review and opt-in provider intake before registration.",
        "public_default_selection": "Record an explicit public default decision; currently OFF and unregistered.",
        "exact_reference_parity": "Demonstrate parity against an exact approved SylNet reference vector.",
    }
    return [{"name": name, "status": "blocked", "reopen_condition": reopen[name]}
            for name in GATE_NAMES]


def regressions(cases: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for case in cases:
        if case["rate_case"] != "rate_1x" or case["count_abs_error"] == 0:
            continue
        rows.append({
            "condition": case["condition"], "metric": "surrogate_count_abs_error",
            "candidate": case["count_abs_error"], "baseline": 0,
            "interpretation": ("Surrogate disagrees with the frozen synthetic target in this "
                               "condition; recorded verbatim as a regression control."),
        })
    constant = constant_count_control()
    rows.append({
        "condition": "all", "metric": "constant_count_control_mean_abs_error",
        "candidate": constant["mean_abs_error"], "baseline": "0",
        "interpretation": "Synthetic constant-count control is retained beside the surrogate.",
    })
    rate_row = next(row for row in SOURCE_REPORTED["findings"]
                    if row["metric"] == "rate_mae_syllables_per_second")
    rows.append({
        "condition": "silence", "metric": "source_reported_rate_mae_not_reproduced",
        "candidate": rate_row["value"], "baseline": None,
        "interpretation": "Source-reported pilot value is provenance only, never a reproduced result.",
    })
    return rows


def contract() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": "optional-task-local-developer-fixture",
        "evidence_status": "incomplete",
        "decision": DECISION,
        "defer_before": "processor_exposure",
        "verification_profile": PROFILE,
        "profile": PROFILE,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "format": FORMAT,
        "surrogate": {
            "identity": "stdlib-thresholded-feature-nuclei-proxy-v0",
            "is_sylnet_source": False,
            "window_samples": WINDOW_SAMPLES,
            "frame_samples": FRAME_SAMPLES,
            "bands": BANDS,
            "caller_supplied_frozen_features": True,
            "checkpoint": False,
            "weights": False,
            "audio_rendered": False,
            "device_clock": False,
        },
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "model_provenance": MODEL_PROVENANCE,
        "licensing_analysis": LICENSING_ANALYSIS,
        "source_reported": SOURCE_REPORTED,
        "exact_blockers": EXACT_BLOCKERS,
        "missing_evidence": MISSING_EVIDENCE,
        "acceptance_profile": {
            "name": PROFILE,
            "source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": [
                "source/output mapping and duration specified, not rendered",
                "rate cases 1x, 4/5x and 5/4x specified, not executed",
                "unfamiliar speech, music, silence, rebuffer, drift",
                "final partial window at exact coordinates",
                "identity and mismatch controls",
                "unmeasured pitch, transient audibility and listening",
                "fixture-only playback buffering",
            ],
            "not_applicable": [
                "no rendered audio, so pitch and transient audibility are not measured",
                "no target runtime, so device timing, memory and deadlines are not measured",
                "no real model, so no preferred-speed policy claim is made",
            ],
        },
        "gates": [gate["name"] for gate in gates()],
        "invariants": [
            "Only this task directory is written; no shared SDK file, CMake, contract, header, registry, default, board, handoff or CI file changes.",
            "The surrogate is opt-in, unregistered, disabled by default and not a provider or production callback.",
            "All feature frames are frozen deterministic synthetic floats; no model, media, weight or runtime asset is read or produced.",
            "Configuration, window, shape, missing, invalid, nonfinite, epoch, position and lifecycle rejections fail closed without advancing state.",
            "Source-reported SylNet metrics are provenance only and are never reproduced, pooled or used as thresholds.",
            "Three cold-start passes are byte-identical; canonical JSON and digest sidecars regenerate deterministically.",
            "Missing evidence never qualifies the candidate; decision remains DEFER.",
        ],
        "reopening_conditions": MISSING_EVIDENCE,
    }


def contract_bytes() -> bytes:
    return (json.dumps(_normalize_negzero(contract()), sort_keys=True, indent=2,
                       allow_nan=False).encode("utf-8") + b"\n")


def repeatability() -> Dict[str, Any]:
    """Three cold-start interpreter processes hashing the pure canonical core."""
    code = ("import hashlib,sys;sys.path.insert(0,sys.argv[1]);import reference;"
            "print(hashlib.sha256(reference.canonical_report_bytes("
            "reference.core_report())).hexdigest())")
    digests = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code, str(HERE)],
                                capture_output=True, text=True, check=True, env=env)
        digests.append(result.stdout.strip())
    return {"count": 3, "method": "three_fresh_interpreters_canonical_core",
            "digests": digests, "byte_identical": len(set(digests)) == 1}


def core_report() -> Dict[str, Any]:
    cases = [evaluate(condition, case)
             for condition in CONDITIONS for case in RATE_CASES]
    by_condition: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for case in cases:
        by_condition.setdefault(case["condition"], {})[case["rate_case"]] = case
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component_id": SLUG,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": "incomplete",
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": "processor_exposure",
        "no_missing_result_qualifies_candidate": True,
        "scope": SCOPE,
        "negative_claims": NEGATIVE_CLAIMS,
        "boundary": BOUNDARY,
        "format": FORMAT,
        "contract_id": f"{CONTRACT_SCHEMA_ID}:{TASK}",
        "contract_sha256": sha256(contract_bytes()),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "model_provenance": MODEL_PROVENANCE,
        "licensing_analysis": LICENSING_ANALYSIS,
        "tool_provenance": TOOL_PROVENANCE,
        "surrogate": {
            "identity": "stdlib-thresholded-feature-nuclei-proxy-v0",
            "is_sylnet_source": False,
            "window_samples": WINDOW_SAMPLES,
            "frame_samples": FRAME_SAMPLES,
            "bands": BANDS,
            "caller_supplied_frozen_features": True,
        },
        "rate_profile": {
            "profile": PROFILE,
            "source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "rate_cases": {name: str(value) for name, value in RATE_CASES.items()},
            "renderer_executed": False,
            "duration_measured": False,
            "pitch": "not_measured_no_rendered_audio",
            "transient_audibility": "not_measured_no_listening",
            "covered": [
                "rate_1x", "rate changes", "unfamiliar speech", "music", "silence",
                "rebuffer", "synthetic level shift (device clock drift not measured)",
                "final partial window",
            ],
            "timestamps": "exact half-open source samples on a fixture clock",
            "unmeasured": [
                "rendered duration", "pitch", "transient audibility",
                "listening preference", "device clock drift", "callback deadline",
                "memory", "benchmark throughput",
            ],
        },
        "conditions": by_condition,
        "controls": controls(),
        "adverse": adverse(),
        "playback_buffering": {condition: buffering(condition) for condition in CONDITIONS},
        "regressions": regressions(cases),
        "source_reported": SOURCE_REPORTED,
        "exact_blockers": EXACT_BLOCKERS,
        "gates": gates(),
        "missing_evidence": MISSING_EVIDENCE,
        "evidence_classes": [
            "synthetic_feature_trace", "deterministic_surrogate",
            "upstream_provenance_hash_pinned", "source_reported_provenance_only",
            "proposal_only",
        ],
    }


def build_report() -> Dict[str, Any]:
    report = core_report()
    report["repeatability"] = repeatability()
    return report


def sources_bytes() -> bytes:
    """Deterministic manifest; local artifacts are digests of their current bytes."""
    lines = [
        "# SHA-256 pins for SDK-SYLNET.",
        "# source: paths are relative to SOURCE_ROOT; other paths are SDK-worktree relative.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in sorted(BOUNDARY_PINS):
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for name in sorted(LOCAL_PIN_PATHS):
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")
