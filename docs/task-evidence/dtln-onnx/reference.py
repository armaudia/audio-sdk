# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local synthetic reference for SDK-DTLN-ONNX.

This package evaluates a stdlib two-stage scalar-gain envelope proxy at the
documented DTLN ONNX stream geometry (16 kHz mono, 512-sample block,
128-sample hop, measured 384-sample output delay). It is not DTLN source, does
not contain or load an ONNX graph, weight, audio file or vendor runtime, and
makes no device-timing, listening, benchmark or release claim. The evaluation
fixture and any future production callback path are distinct; no production
callback is implemented.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from scorer import SCORER_ID, si_sdr, stoi

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-DTLN-ONNX"
TITLE = "DTLN ONNX"
SLUG = "dtln-onnx"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "6f58f3d721908806f8c4a0a1e0dc6de846cef54c"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
EVIDENCE_INTERPRETER = "3.12.16"

SAMPLE_RATE_HZ = 16000
BLOCK_SAMPLES = 512
HOP_SAMPLES = 128
DELAY_SAMPLES = 384
DELAY_HOPS = DELAY_SAMPLES // HOP_SAMPLES
MAGNITUDE_BINS = BLOCK_SAMPLES // 2 + 1
WINDOW_SAMPLES = 15360
TAIL_SAMPLES = 15323
CLIP_THRESHOLD = 0.98
MAX_ABS_INPUT = 2.0

UPSTREAM_REPOSITORY = "https://github.com/breizhn/DTLN"
UPSTREAM_COMMIT = "1de1f15a8b5b7e1c44905618ff2ef70ca8277fbc"
UPSTREAM_LICENSE = "MIT"
UPSTREAM_LICENSE_COPYRIGHT = "Copyright (c) 2020 Nils L. Westhausen"
UPSTREAM_SNAPSHOT = "data/checkouts/DTLN"
UPSTREAM_LICENSE_PATH = UPSTREAM_SNAPSHOT + "/LICENSE"
UPSTREAM_ADAPTER_IDENTITY = f"DTLN-{UPSTREAM_COMMIT}"

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/selected_audio_enhancement_candidates.md":
        "0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "adapters/dtln-onnx/adapter.json":
        "d048fc48252c47b11598dfd1e881878868676434cc7ab6f2a505e34015d60c69",
    "adapters/dtln-onnx/README.md":
        "77853cc7606cd789bd0b65df469f98bfc2b9e082540bed115501bc0b89e91a95",
    "adapters/dtln-onnx/run.py":
        "a12d90df72d1bdafe8d2a204741227ecd7c2ca8d410829e2f2f912256168fdd6",
    "adapters/dtln-onnx/requirements.lock":
        "1195f7e838fd20dc1fff30b3808324131c9f7acbedf63f9bf4084de78aa6a86c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    UPSTREAM_LICENSE_PATH:
        "aa95acd8c8a7341bfcdb2823694dcbb27a2a4143e860bb52db1ff0f29c85e5a1",
    UPSTREAM_SNAPSHOT + "/README.md":
        "1f518d30bc8fbd4cdd0cfa5735630162852a33510ad149fd3204f124d3ad51d2",
    UPSTREAM_SNAPSHOT + "/DTLN_model.py":
        "cb5fc13f9d24ff5b98c65ba0a9f814ed4943048526acf310aebef0d4cdf47d55",
    UPSTREAM_SNAPSHOT + "/real_time_processing_onnx.py":
        "e15f0fc092f03f372dff34770a9a7d1f4b664337f514bf6f0880c0b87f3a2016",
    UPSTREAM_SNAPSHOT + "/convert_weights_to_onnx.py":
        "a222ff4207a769d2e9d7c2764b2996d76aeb83e10c4ec93c49ac1a4999e4b97b",
    UPSTREAM_SNAPSHOT + "/pretrained_model/model_1.onnx":
        "22b91cae3855e5a0620e66a917ca6c82c58db0e842c770f58d86751c5e8d4ae3",
    UPSTREAM_SNAPSHOT + "/pretrained_model/model_2.onnx":
        "e20c92f9233fccf29cddf86970d0d0161a03aebccc26d6f4d5639c4d5ec2e639",
}
BOUNDARY_PINS: Dict[str, str] = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}
SCORER_PINS: Dict[str, str] = {
    "docs/task-evidence/online-multichannel-wpe/scorer.py":
        "a0c1ba9ff21b0d0125c792053f0acefe1eda9266ab276aa370838c0f42dd55a1",
    "docs/task-evidence/online-multichannel-wpe/crosscheck_vectors.json":
        "7bdd131858306648b4f24b1544a6afb4da2660b3f2d3edcdfb3b715e574a18a2",
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
    "scorer.py",
    "test_reference.py",
    "verify.py",
)

ASSET_SPECS: Tuple[Dict[str, Any], ...] = (
    {
        "role": "mask_estimation_graph",
        "path": UPSTREAM_SNAPSHOT + "/pretrained_model/model_1.onnx",
        "relative_path": "pretrained_model/model_1.onnx",
        "sha256": SOURCE_PINS[UPSTREAM_SNAPSHOT + "/pretrained_model/model_1.onnx"],
        "bytes": 1_458_237,
    },
    {
        "role": "signal_estimation_graph",
        "path": UPSTREAM_SNAPSHOT + "/pretrained_model/model_2.onnx",
        "relative_path": "pretrained_model/model_2.onnx",
        "sha256": SOURCE_PINS[UPSTREAM_SNAPSHOT + "/pretrained_model/model_2.onnx"],
        "bytes": 2_510_010,
    },
)
RUNTIME_LOCK = {
    "path": "adapters/dtln-onnx/requirements.lock",
    "sha256": SOURCE_PINS["adapters/dtln-onnx/requirements.lock"],
    "target": "CPython 3.10, macOS arm64",
    "python": "3.10",
    "onnxruntime": "1.20.1",
    "numpy": "1.26.4",
    "soundfile": "0.13.1",
}

FORMAT = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "hop_samples": 160,
    "content_delay_samples": 0,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}
STREAM = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": 1,
    "sample_format": "f32",
    "block_samples": BLOCK_SAMPLES,
    "hop_samples": HOP_SAMPLES,
    "magnitude_bins": MAGNITUDE_BINS,
    "graphs_required": 2,
    "delay_samples": DELAY_SAMPLES,
    "delay_hops": DELAY_HOPS,
    "delay_source": "three-hop consistent lag measured against paired noisy input",
    "output_alignment": "caller compensates 384 samples; raw stream is scored uncompensated as a control",
    "installed_v0_geometry_preserved": True,
    "installed_v0_behavior_changed": False,
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
    "dtln_source_executed": False,
    "onnx_graph_loaded": False,
    "model_weights": False,
    "vendor_runtime_invoked": False,
    "real_audio": False,
    "real_corpus_scored": False,
    "real_labels": False,
    "device_timing": False,
    "listening_result": False,
    "benchmark_claim": False,
    "release_claim": False,
    "registered_provider": False,
    "installed_v0_change": False,
    "abi_registry_default_change": False,
    "shared_build_or_ci_change": False,
}
NEGATIVE_CLAIMS = {
    "dtln_source_executed": False,
    "onnx_graph_loaded": False,
    "model_weights": False,
    "onnx_runtime_invoked": False,
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

CONDITIONS = ("speech", "unfamiliar_speech", "music", "clipped", "tail_partial", "silence")
PATTERNS: Dict[str, Dict[str, Any]] = {
    "speech": {
        "segments": ((200, 3400), (4600, 8200), (9400, 13000), (13600, 15000)),
        "f0_hz": 113, "noise_scale": 0.16, "chord": False, "drive": 1.0,
    },
    "unfamiliar_speech": {
        "segments": ((100, 2200), (3400, 6900), (8100, 11700), (12900, 14800)),
        "f0_hz": 197, "noise_scale": 0.20, "chord": False, "drive": 1.0,
    },
    "music": {
        "segments": ((0, WINDOW_SAMPLES),),
        "f0_hz": 220, "noise_scale": 0.10, "chord": True, "drive": 1.0,
    },
    "clipped": {
        "segments": ((200, 3400), (4600, 8200), (9400, 13000), (13600, 15000)),
        "f0_hz": 113, "noise_scale": 0.16, "chord": False, "drive": 1.9,
    },
    "tail_partial": {
        "segments": ((200, 3400), (4600, 8200), (9400, 13000), (13600, 15000)),
        "f0_hz": 113, "noise_scale": 0.16, "chord": False, "drive": 1.0,
    },
    "silence": {
        "segments": (), "f0_hz": 0, "noise_scale": 0.0, "chord": False, "drive": 1.0,
    },
}
CONFIG_KEYS = {
    "profile", "block_samples", "hop_samples", "delay_samples",
    "noise_oversubtraction", "floor_gain",
}
DEFAULT_CONFIG: Dict[str, Any] = {
    "profile": "dtln_onnx_stream_surrogate_v0",
    "block_samples": BLOCK_SAMPLES,
    "hop_samples": HOP_SAMPLES,
    "delay_samples": DELAY_SAMPLES,
    "noise_oversubtraction": 1.8,
    "floor_gain": 0.10,
}

EXACT_BLOCKERS = [
    "Both pinned ONNX graphs are absent from this SDK worktree: model_1.onnx "
    "(1458237 bytes, sha256 22b91cae3855e5a0620e66a917ca6c82c58db0e842c770f58d86751c5e8d4ae3) "
    "and model_2.onnx (2510010 bytes, sha256 "
    "e20c92f9233fccf29cddf86970d0d0161a03aebccc26d6f4d5639c4d5ec2e639). The adapter lock "
    "targets CPython 3.10/macOS arm64 with onnxruntime 1.20.1, while the pinned evidence "
    "interpreter is CPython 3.12.16 and onnxruntime is not importable there; no graph, runtime "
    "or weight was downloaded, installed, built or executed.",
    "Product/redistribution rights and training-data provenance for the upstream pretrained "
    "checkpoints are not cleared. The pinned MIT LICENSE covers the repository snapshot as "
    "distributed but is not a product or redistribution clearance, and no legal review exists.",
    "No rights-cleared real paired cohort was scored, no real audio was read, and no independent "
    "listening or separately labeled authorized predictive screen was run. The 30-pair DNS2020 "
    "pilot values are source-reported provenance only.",
    "No target-runtime content/availability timing, memory, deadline or installed-provider "
    "evidence exists, and no provider intake, descriptor, catalog or public-default review was "
    "performed.",
]
MISSING_EVIDENCE = [
    "both pinned ONNX graphs present in an approved isolated runner, with hashes and bytes verified",
    "a pinned CPython 3.12.16-compatible onnxruntime environment (or a separately recorded 3.10 environment)",
    "product/redistribution and training-data rights clearance for the pretrained graphs",
    "rights-cleared held-out real paired cohort with clean references",
    "independent listening or a separately labeled authorized predictive screen",
    "target-runtime content/availability timing, memory and deadline evidence",
    "exact approved DTLN reference parity vector",
    "opt-in provider intake, descriptor and catalog review",
    "explicit public default selection",
]
GATE_NAMES = (
    "exact_graphs_runtime_and_rights",
    "real_paired_cohort",
    "independent_listening_or_predictive_screen",
    "target_runtime_timing_memory",
    "provider_intake",
    "public_default_selection",
    "exact_reference_parity",
)


class Rejected(Exception):
    """Fail-closed rejection with a stable reason code."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
    payload = json.loads(text, object_pairs_hook=_reject_duplicate,
                         parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise ValueError("root_not_object")
    return payload


def strict_json(path: Path) -> Dict[str, Any]:
    return strict_loads(path.read_text(encoding="utf-8"))


PIN_RE = re.compile(r"^([0-9a-f]{64})  (\S+)$")


def allowed_pin_keys() -> set:
    keys = {"source:" + path for path in SOURCE_PINS}
    keys.update(BOUNDARY_PINS)
    keys.update(SCORER_PINS)
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


def pin_path(raw: str) -> Path:
    if raw.startswith("source:"):
        return SOURCE_ROOT / raw.split(":", 1)[1]
    return SDK_ROOT / raw


def normalize_remote_url(url: str) -> str:
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
    """Resolve the pinned checkout's origin URL and HEAD offline."""
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


def rng(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def _envelope(index: int, segments: Sequence[Tuple[int, int]]) -> float:
    for first, last in segments:
        if first <= index < last:
            position = (index - first) / (last - first)
            return math.sin(math.pi * position) ** 2
    return 0.0


@lru_cache(maxsize=None)
def synth(condition: str) -> Tuple[List[float], List[float]]:
    """Return frozen paired clean target and observed input for one condition."""
    if condition not in PATTERNS:
        raise Rejected("unknown_condition")
    spec = PATTERNS[condition]
    count = TAIL_SAMPLES if condition == "tail_partial" else WINDOW_SAMPLES
    source = rng(20261125 + sum(ord(char) for char in condition))
    clean: List[float] = []
    observed: List[float] = []
    for index in range(count):
        if condition == "silence":
            clean.append(0.0)
            observed.append(0.0)
            continue
        envelope = _envelope(index, spec["segments"])
        tone = (0.30 * math.sin(2.0 * math.pi * spec["f0_hz"] * index / SAMPLE_RATE_HZ)
                + 0.16 * math.sin(2.0 * math.pi * 2.0 * spec["f0_hz"] * index / SAMPLE_RATE_HZ)
                + 0.09 * math.sin(2.0 * math.pi * 3.0 * spec["f0_hz"] * index / SAMPLE_RATE_HZ))
        if spec["chord"]:
            tone += (0.12 * math.sin(2.0 * math.pi * 1.5 * spec["f0_hz"] * index / SAMPLE_RATE_HZ)
                     + 0.08 * math.sin(2.0 * math.pi * 2.5 * spec["f0_hz"] * index / SAMPLE_RATE_HZ))
        value = tone * envelope
        clean.append(value)
        noise = (next(source) - 0.5) * 2.0 * spec["noise_scale"]
        noisy = value * spec["drive"] + noise
        if condition == "clipped":
            noisy = max(-1.0, min(1.0, noisy))
        observed.append(noisy)
    return clean, observed


def _window() -> List[float]:
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * index / BLOCK_SAMPLES)
            for index in range(BLOCK_SAMPLES)]


def validate_config(config: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        raise Rejected("rejected_invalid")
    keys = set(config)
    if not keys:
        raise Rejected("rejected_missing")
    if keys != CONFIG_KEYS:
        raise Rejected("rejected_invalid")
    for key in ("block_samples", "hop_samples", "delay_samples"):
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, int):
            raise Rejected("rejected_invalid")
    if (config["block_samples"], config["hop_samples"], config["delay_samples"]) != (
            BLOCK_SAMPLES, HOP_SAMPLES, DELAY_SAMPLES):
        raise Rejected("rejected_geometry")
    for key in ("noise_oversubtraction", "floor_gain"):
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Rejected("rejected_invalid")
        if not math.isfinite(value):
            raise Rejected("rejected_nonfinite")
    if config["profile"] != DEFAULT_CONFIG["profile"]:
        raise Rejected("rejected_profile")
    if not 1.0 <= config["noise_oversubtraction"] <= 4.0:
        raise Rejected("rejected_range")
    if not 0.0 <= config["floor_gain"] <= 1.0:
        raise Rejected("rejected_range")
    return dict(config)


class Controller:
    """Causal two-stage scalar-gain envelope proxy at 512/128 geometry.

    Stage 1 estimates a hop gain from a 512-sample buffer energy against a slow
    noise floor. Stage 2 smooths the gain and overlap-adds the windowed block.
    The emitted stream carries the documented three-hop (384-sample) delay.
    """

    def __init__(self, config: Any = None) -> None:
        self.config = validate_config(DEFAULT_CONFIG if config is None else config)
        self.window = _window()
        self.epoch = 1
        self.next_position = 0
        self.hop_index = 0
        self.buffer = [0.0] * BLOCK_SAMPLES
        self.overlap = [0.0] * BLOCK_SAMPLES
        self.weight = [0.0] * BLOCK_SAMPLES
        self.noise_floor = 0.0
        self.gain = 1.0
        self.finished = False
        self.closed = False
        self.state_hash = self._state()

    def _state(self) -> str:
        return sha256(canonical_bytes({
            "epoch": self.epoch,
            "next_position": self.next_position,
            "hop_index": self.hop_index,
            "noise_floor": round(self.noise_floor, 12),
            "gain": round(self.gain, 12),
            "finished": self.finished,
            "closed": self.closed,
        }))

    def _reject(self, reason: str) -> Dict[str, Any]:
        return {"status": "rejected", "reason": reason, "samples": None,
                "state_digest": self.state_hash}

    def process(self, frame: Any, epoch: int = 1,
                first_sample: Optional[int] = None) -> Dict[str, Any]:
        if self.closed or self.finished:
            return self._reject("rejected_session")
        if not isinstance(frame, (list, tuple)) or len(frame) != HOP_SAMPLES:
            return self._reject("rejected_tensor")
        if any(isinstance(value, bool) for value in frame):
            return self._reject("rejected_invalid")
        if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in frame):
            return self._reject("rejected_nonfinite")
        if any(abs(value) > MAX_ABS_INPUT for value in frame):
            return self._reject("rejected_invalid")
        if epoch != self.epoch:
            return self._reject("rejected_epoch")
        position = self.next_position if first_sample is None else first_sample
        if position != self.next_position:
            return self._reject("rejected_position")

        self.buffer = self.buffer[HOP_SAMPLES:] + list(frame)
        energy = math.fsum(value * value for value in self.buffer) / BLOCK_SAMPLES
        level = math.sqrt(energy)
        if self.noise_floor == 0.0:
            self.noise_floor = level
        elif level < self.noise_floor:
            self.noise_floor = 0.80 * self.noise_floor + 0.20 * level
        else:
            self.noise_floor = 0.998 * self.noise_floor + 0.002 * level
        denominator = self.config["noise_oversubtraction"] * self.noise_floor ** 2
        ratio = energy / denominator if denominator > 0.0 else 1.0e9
        estimated_snr = max(0.0, ratio - 1.0)
        target = estimated_snr / (1.0 + estimated_snr) if estimated_snr > 0.0 else 0.0
        target = max(self.config["floor_gain"], target)
        if target < self.gain:
            self.gain = 0.55 * target + 0.45 * self.gain
        else:
            self.gain = 0.35 * target + 0.65 * self.gain

        for index in range(BLOCK_SAMPLES):
            self.overlap[index] += self.window[index] * self.gain * self.buffer[index]
            self.weight[index] += self.window[index]
        samples = []
        for index in range(HOP_SAMPLES):
            if self.weight[index] > 1.0e-9:
                samples.append(self.overlap[index] / self.weight[index])
            else:
                samples.append(0.0)
        self.overlap = self.overlap[HOP_SAMPLES:] + [0.0] * HOP_SAMPLES
        self.weight = self.weight[HOP_SAMPLES:] + [0.0] * HOP_SAMPLES
        self.next_position += HOP_SAMPLES
        self.hop_index += 1
        self.state_hash = self._state()
        return {"status": "accepted", "reason": "none", "samples": samples,
                "state_digest": self.state_hash}

    def finish(self) -> str:
        if self.closed or self.finished:
            raise Rejected("rejected_session")
        if self.next_position == 0:
            raise Rejected("rejected_empty")
        self.finished = True
        self.state_hash = self._state()
        return "ok"

    def close(self) -> None:
        self.closed = True
        self.state_hash = self._state()

    def reset(self, epoch: int, first_sample: int) -> str:
        if self.closed:
            raise Rejected("rejected_session")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch <= self.epoch:
            raise Rejected("rejected_epoch")
        if isinstance(first_sample, bool) or not isinstance(first_sample, int) or first_sample < 0:
            raise Rejected("rejected_position")
        self.epoch = epoch
        self.next_position = first_sample
        self.hop_index = 0
        self.buffer = [0.0] * BLOCK_SAMPLES
        self.overlap = [0.0] * BLOCK_SAMPLES
        self.weight = [0.0] * BLOCK_SAMPLES
        self.noise_floor = 0.0
        self.gain = 1.0
        self.finished = False
        self.state_hash = self._state()
        return "ok"


def run_frames(samples: Sequence[float], config: Any = None
               ) -> Tuple[Optional[List[float]], Optional[List[float]], Dict[str, Any]]:
    """Return raw (384-sample-delayed) and aligned streams plus run accounting."""
    controller = Controller(config)
    raw: List[float] = []
    hop_count = (len(samples) + HOP_SAMPLES - 1) // HOP_SAMPLES
    rejections = 0
    for index in range(hop_count):
        frame = list(samples[index * HOP_SAMPLES:(index + 1) * HOP_SAMPLES])
        if len(frame) < HOP_SAMPLES:
            frame = frame + [0.0] * (HOP_SAMPLES - len(frame))
        outcome = controller.process(frame, controller.epoch, index * HOP_SAMPLES)
        if outcome["samples"] is None:
            rejections += 1
            return None, None, {
                "status": "rejected", "reason": outcome["reason"],
                "hops": controller.hop_index, "rejections": rejections,
            }
        raw.extend(outcome["samples"])
    try:
        controller.finish()
    except Rejected as error:
        return None, None, {"status": "rejected", "reason": error.reason,
                            "hops": controller.hop_index, "rejections": rejections + 1}
    raw = raw[:len(samples)]
    aligned = raw[DELAY_SAMPLES:] + [0.0] * min(DELAY_SAMPLES, len(raw))
    aligned = aligned[:len(samples)]
    final_valid = len(samples) % HOP_SAMPLES or HOP_SAMPLES
    return raw, aligned, {
        "status": "ok",
        "hops": controller.hop_index,
        "rejections": rejections,
        "block_samples": BLOCK_SAMPLES,
        "hop_samples": HOP_SAMPLES,
        "delay_samples": DELAY_SAMPLES,
        "valid_samples": len(samples),
        "padded_samples": hop_count * HOP_SAMPLES - len(samples),
        "final_hop": {
            "source": [len(samples) - final_valid, len(samples)],
            "valid_count": final_valid,
            "padded_count": (HOP_SAMPLES - len(samples) % HOP_SAMPLES) % HOP_SAMPLES,
            "final_flag": True,
        },
    }


def scored(target: Sequence[float], actual: Optional[Sequence[float]],
           observed: Optional[Sequence[float]] = None) -> Dict[str, Any]:
    if actual is None:
        return {"status": "rejected", "si_sdr_db": None, "stoi": None,
                "peak_abs_output": None, "nonfinite_count": None,
                "clipping_count": None, "input_peak_abs": None,
                "input_clipping_count": None, "si_sdr_reason": "invalid_input",
                "stoi_reason": "invalid_input"}
    si_value, si_reason = si_sdr(target, actual)
    stoi_value, stoi_reason = stoi(target, actual, SAMPLE_RATE_HZ)
    measured = si_value is not None and stoi_value is not None
    return {
        "status": "measured_synthetic" if measured else "excluded",
        "si_sdr_db": round(si_value, 6) if si_value is not None and math.isfinite(si_value) else None,
        "stoi": round(stoi_value, 6) if stoi_value is not None and math.isfinite(stoi_value) else None,
        "peak_abs_output": round(max(abs(value) for value in actual), 9),
        "nonfinite_count": sum(1 for value in actual if not math.isfinite(value)),
        "clipping_count": sum(1 for value in actual if abs(value) >= CLIP_THRESHOLD),
        "input_peak_abs": round(max(abs(value) for value in observed), 9) if observed is not None else None,
        "input_clipping_count": (sum(1 for value in observed if abs(value) >= 1.0)
                                 if observed is not None else None),
        "si_sdr_reason": si_reason,
        "stoi_reason": stoi_reason,
    }


def evaluate(condition: str) -> Dict[str, Any]:
    target, observed = synth(condition)
    baseline = scored(target, observed, observed)
    raw, aligned, run = run_frames(observed)
    raw_metrics = scored(target, raw, observed)
    aligned_metrics = scored(target, aligned, observed)
    worse = (aligned is not None
             and baseline["si_sdr_db"] is not None
             and aligned_metrics["si_sdr_db"] is not None
             and aligned_metrics["si_sdr_db"] < baseline["si_sdr_db"])
    return {
        "condition": condition,
        "status": ("excluded_no_reference" if aligned is not None
                   and aligned_metrics["status"] == "excluded"
                   else "measured_synthetic" if aligned is not None
                   else "rejected_adverse"),
        "samples": len(observed),
        "seed": 20261125 + sum(ord(char) for char in condition),
        "baseline_metrics": baseline,
        "candidate_raw_metrics": raw_metrics,
        "candidate_metrics": aligned_metrics,
        "candidate_worse_than_baseline": worse,
        "delay_compensation_samples": DELAY_SAMPLES,
        "frame_run": run,
    }


def conditions() -> Dict[str, Any]:
    return {condition: evaluate(condition) for condition in CONDITIONS}


def controls() -> Dict[str, Any]:
    target, observed = synth("speech")
    raw, aligned, _ = run_frames(observed)
    identity = scored(target, observed, observed)
    candidate = scored(target, aligned, observed)
    clean_raw, clean_aligned, _ = run_frames(target)
    return {
        "identity": {
            "name": "identity_no_processing",
            "status": "measured_synthetic",
            "metrics": identity,
            "note": "Exact echo of the observed speech frame; zero improvement is trivial.",
        },
        "named_baseline": {
            "name": "noisy_input_no_processing",
            "status": "measured_synthetic",
            "metrics": identity,
            "note": "Established task-matched control is plain noisy input, not a DTLN run.",
        },
        "candidate": {
            "name": "two_stage_scalar_gain_envelope_proxy",
            "status": "measured_synthetic",
            "metrics": candidate,
            "raw_metrics": scored(target, raw, observed),
        },
        "clean_speech_preservation": {
            "name": "surrogate_on_clean_target",
            "clean_reference": "speech condition synthetic clean target",
            "status": "measured_synthetic",
            "metrics": scored(target, clean_aligned, target),
            "raw_metrics": scored(target, clean_raw, target),
        },
        "mismatch": mismatch_control(),
        "all_present": True,
        "excluded_from_qualification": True,
        "note": ("Identity, noisy-input and candidate controls are paired synthetic comparisons "
                 "only; no real model or listening result is represented."),
    }


def mismatch_control() -> Dict[str, Any]:
    controller = Controller()
    before = controller.state_hash
    cases = {
        "wrong_shape": controller.process([0.0] * (HOP_SAMPLES - 1), 1, 0),
        "nonfinite": controller.process([float("nan")] * HOP_SAMPLES, 1, 0),
        "stale_epoch": controller.process([0.0] * HOP_SAMPLES, 0, 0),
        "stale_position": controller.process([0.0] * HOP_SAMPLES, 1, HOP_SAMPLES),
        "oversized": controller.process([MAX_ABS_INPUT + 1.0] * HOP_SAMPLES, 1, 0),
    }
    return {
        "all_rejected": all(value["status"] == "rejected" for value in cases.values()),
        "all_state_unchanged": all(value["state_digest"] == before for value in cases.values()),
        "cases": {name: value["reason"] for name, value in cases.items()},
    }


def _invalid_configs() -> List[Tuple[str, Any]]:
    return [
        ("missing_key", {key: value for key, value in DEFAULT_CONFIG.items()
                         if key != "floor_gain"}),
        ("empty", {}),
        ("unknown_key", {**DEFAULT_CONFIG, "unexpected": 1}),
        ("wrong_type", {**DEFAULT_CONFIG, "block_samples": "512"}),
        ("boolean", {**DEFAULT_CONFIG, "hop_samples": True}),
        ("nonfinite", {**DEFAULT_CONFIG, "floor_gain": float("nan")}),
        ("wrong_geometry", {**DEFAULT_CONFIG, "block_samples": 256}),
        ("wrong_profile", {**DEFAULT_CONFIG, "profile": "dtln_real"}),
        ("out_of_range", {**DEFAULT_CONFIG, "noise_oversubtraction": 9.0}),
    ]


def _invalid_frames() -> List[Tuple[str, Any, int, int]]:
    return [
        ("wrong_shape", [0.0] * (HOP_SAMPLES - 1), 1, 0),
        ("missing_samples", None, 1, 0),
        ("bool_sample", [True] * HOP_SAMPLES, 1, 0),
        ("nonfinite", [float("inf")] * HOP_SAMPLES, 1, 0),
        ("out_of_range", [MAX_ABS_INPUT + 1.0] * HOP_SAMPLES, 1, 0),
        ("stale_epoch", [0.0] * HOP_SAMPLES, 0, 0),
        ("stale_position", [0.0] * HOP_SAMPLES, 1, HOP_SAMPLES),
    ]


def _asset_request(**overrides: Any) -> Dict[str, Any]:
    request: Dict[str, Any] = {
        "root": UPSTREAM_SNAPSHOT,
        "source_commit": UPSTREAM_COMMIT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "block_samples": BLOCK_SAMPLES,
        "hop_samples": HOP_SAMPLES,
        "graphs": [
            {"role": spec["role"], "path": spec["relative_path"],
             "sha256": spec["sha256"], "bytes": spec["bytes"]}
            for spec in ASSET_SPECS
        ],
        "runtime": {
            "package": "onnxruntime",
            "version": RUNTIME_LOCK["onnxruntime"],
            "python": RUNTIME_LOCK["python"],
            "lock_sha256": RUNTIME_LOCK["sha256"],
            "available": False,
        },
        "interpreter": EVIDENCE_INTERPRETER,
    }
    request.update(overrides)
    return request


def validate_asset_request(request: Any,
                           reader: Optional[Callable[[str], Optional[bytes]]] = None
                           ) -> Dict[str, Any]:
    """Fail-closed caller-supplied-asset intake; never executes a graph.

    ``reader`` maps a graph-relative path to bytes (or ``None`` when absent).
    The default reader cannot see any asset, so an unqualified request is
    reported as blocked rather than silently accepted.
    """
    required = {"root", "source_commit", "sample_rate_hz", "block_samples",
                "hop_samples", "graphs", "runtime", "interpreter"}
    if not isinstance(request, dict):
        return {"status": "rejected", "reason": "rejected_invalid"}
    if set(request) != required:
        return {"status": "rejected", "reason": "rejected_invalid"}
    if request["source_commit"] != UPSTREAM_COMMIT:
        return {"status": "rejected", "reason": "rejected_source_commit"}
    if (request["sample_rate_hz"], request["block_samples"], request["hop_samples"]) != (
            SAMPLE_RATE_HZ, BLOCK_SAMPLES, HOP_SAMPLES):
        return {"status": "rejected", "reason": "rejected_geometry"}
    runtime = request["runtime"]
    if not isinstance(runtime, dict) or set(runtime) != {
            "package", "version", "python", "lock_sha256", "available"}:
        return {"status": "rejected", "reason": "rejected_runtime"}
    if (runtime["package"] != "onnxruntime"
            or runtime["version"] != RUNTIME_LOCK["onnxruntime"]
            or runtime["python"] != RUNTIME_LOCK["python"]
            or runtime["lock_sha256"] != RUNTIME_LOCK["sha256"]
            or not isinstance(runtime["available"], bool)):
        return {"status": "rejected", "reason": "rejected_runtime"}
    graphs = request["graphs"]
    if not isinstance(graphs, list) or len(graphs) != 2:
        return {"status": "rejected", "reason": "rejected_graph_count"}
    verified = []
    for spec, graph in zip(ASSET_SPECS, graphs):
        if not isinstance(graph, dict) or set(graph) != {"role", "path", "sha256", "bytes"}:
            return {"status": "rejected", "reason": "rejected_graph_descriptor"}
        if graph["role"] != spec["role"] or graph["path"] != spec["relative_path"]:
            return {"status": "rejected", "reason": "rejected_graph_identity"}
        if graph["sha256"] != spec["sha256"]:
            return {"status": "rejected", "reason": "rejected_hash_pin"}
        if isinstance(graph["bytes"], bool) or graph["bytes"] != spec["bytes"]:
            return {"status": "rejected", "reason": "rejected_size_pin"}
        payload = None if reader is None else reader(graph["path"])
        if payload is None:
            return {"status": "blocked", "reason": "blocked_asset_absent",
                    "role": spec["role"]}
        if len(payload) != spec["bytes"]:
            return {"status": "blocked", "reason": "blocked_size_mismatch",
                    "role": spec["role"]}
        if sha256(payload) != spec["sha256"]:
            return {"status": "blocked", "reason": "blocked_hash_mismatch",
                    "role": spec["role"]}
        verified.append({"role": spec["role"], "sha256": spec["sha256"],
                         "bytes": spec["bytes"], "verified": True})
    if runtime["available"] is not True:
        return {"status": "blocked", "reason": "blocked_runtime_unavailable",
                "graphs_verified": True, "verified": verified}
    if request["interpreter"] != runtime["python"]:
        return {"status": "blocked", "reason": "blocked_interpreter_mismatch",
                "graphs_verified": True, "verified": verified}
    return {"status": "ready_for_caller_execution",
            "reason": "assets_verified_runtime_available",
            "graphs_verified": True, "verified": verified}


def asset_gate() -> Dict[str, Any]:
    root = SOURCE_ROOT / UPSTREAM_SNAPSHOT

    def reader(relative: str) -> Optional[bytes]:
        path = root / relative
        return path.read_bytes() if path.is_file() else None

    available = importlib.util.find_spec("onnxruntime") is not None
    request = _asset_request()
    request["runtime"] = dict(request["runtime"], available=available)
    result = validate_asset_request(request, reader)
    return {
        "request_scope": "caller-supplied read-only asset intake; no graph is opened or executed",
        "asset_root_relative": UPSTREAM_SNAPSHOT,
        "asset_root_in_sdk_worktree": False,
        "required_graphs": [
            {"role": spec["role"], "path": spec["path"], "sha256": spec["sha256"],
             "bytes": spec["bytes"]} for spec in ASSET_SPECS
        ],
        "runtime_lock": dict(RUNTIME_LOCK),
        "evidence_interpreter": EVIDENCE_INTERPRETER,
        "onnxruntime_importable": available,
        "validation": result,
        "status": "blocked" if result["status"] == "blocked" else result["status"],
        "inference_executed": False,
        "exact_blocker": (
            "Assets verify by hash but no pinned CPython 3.12.16-compatible "
            "onnxruntime is installed and the graphs are absent from this SDK "
            "worktree; execution is refused until the reopen condition is met."
        ),
        "reopen_condition": (
            "Place both hash-pinned graphs in an approved isolated runner, install "
            "and pin a 3.12.16-compatible onnxruntime (or record a new 3.10 lock), "
            "clear product/redistribution and training-data rights, and record the "
            "approved positive-rights decision before any graph is opened."
        ),
    }


def _reason(call: Callable[[], Any]) -> str:
    try:
        call()
    except Rejected as error:
        return error.reason
    return "not_rejected"


def adverse() -> Dict[str, Any]:
    config_cases = {}
    for name, config in _invalid_configs():
        try:
            Controller(config)
            config_cases[name] = {"status": "not_rejected", "controller_created": True}
        except Rejected as error:
            config_cases[name] = {"status": "rejected", "reason": error.reason,
                                  "controller_created": False}

    controller = Controller()
    before = controller.state_hash
    frame_cases = {}
    for name, frame, epoch, position in _invalid_frames():
        outcome = controller.process(frame, epoch, position)
        frame_cases[name] = {"status": outcome["status"], "reason": outcome["reason"],
                             "state_unchanged": outcome["state_digest"] == before}
    frame_cases["dsp_state_unchanged"] = all(
        case["state_unchanged"] for name, case in frame_cases.items()
        if name != "dsp_state_unchanged")

    closed = Controller()
    closed.close()
    after_close = closed.process([0.0] * HOP_SAMPLES)
    finished = Controller()
    for index in range(2):
        assert finished.process([0.0] * HOP_SAMPLES, 1, index * HOP_SAMPLES)["status"] == "accepted"
    finished.finish()
    after_finish = finished.process([0.0] * HOP_SAMPLES)

    reset_controller = Controller()
    stale_reset_epoch = _reason(lambda: reset_controller.reset(1, 0))
    stale_reset_position = _reason(lambda: reset_controller.reset(2, -1))
    valid_reset = reset_controller.reset(2, 0)

    absent = validate_asset_request(_asset_request())
    payloads = {"pretrained_model/model_1.onnx": b"x" * ASSET_SPECS[0]["bytes"],
                "pretrained_model/model_2.onnx": b"y" * ASSET_SPECS[1]["bytes"]}

    def real_reader(relative: str) -> Optional[bytes]:
        path = SOURCE_ROOT / UPSTREAM_SNAPSHOT / relative
        return path.read_bytes() if path.is_file() else None

    mismatch = validate_asset_request(
        _asset_request(), lambda relative: payloads.get(relative))
    wrong_commit = validate_asset_request(_asset_request(source_commit="0" * 40), real_reader)
    wrong_geometry = validate_asset_request(_asset_request(hop_samples=160), real_reader)
    one_graph = validate_asset_request(
        _asset_request(graphs=_asset_request()["graphs"][:1]), real_reader)
    duplicate_graph = validate_asset_request(
        _asset_request(graphs=[_asset_request()["graphs"][0]] * 2), real_reader)
    unknown_key = validate_asset_request(
        {**_asset_request(), "extra": True}, real_reader)
    runtime_unavailable = validate_asset_request(_asset_request(), real_reader)
    ready_request = _asset_request(interpreter=RUNTIME_LOCK["python"])
    ready_request["runtime"] = dict(ready_request["runtime"], available=True)
    ready = validate_asset_request(ready_request, real_reader)

    asset_cases = {
        "absent": absent,
        "hash_mismatch": mismatch,
        "wrong_source_commit": wrong_commit,
        "wrong_geometry": wrong_geometry,
        "one_graph": one_graph,
        "duplicate_graph": duplicate_graph,
        "unknown_key": unknown_key,
        "runtime_unavailable": runtime_unavailable,
    }
    result = {
        "config_rejections": config_cases,
        "frame_rejections": frame_cases,
        "lifecycle": {
            "close_then_process": {"status": after_close["status"],
                                   "reason": after_close["reason"]},
            "finish_then_process": {"status": after_finish["status"],
                                    "reason": after_finish["reason"]},
            "stale_reset_epoch": {"status": "rejected", "reason": stale_reset_epoch},
            "stale_reset_position": {"status": "rejected", "reason": stale_reset_position},
            "valid_reset": valid_reset,
        },
        "asset_gate": {name: {"status": value["status"], "reason": value["reason"]}
                       for name, value in asset_cases.items()},
        "asset_gate_control": {
            "status": ready["status"],
            "reason": ready["reason"],
            "verified_graphs": len(ready.get("verified", [])),
        },
        "validity": {
            "nonfinite_never_counted_as_output": True,
            "invalid_excluded": True,
            "invalid_never_advances_dsp_state": frame_cases["dsp_state_unchanged"],
        },
    }
    result["all_rejected"] = (
        all(value["status"] == "rejected" for value in config_cases.values())
        and all(value["status"] == "rejected" for key, value in frame_cases.items()
                if key != "dsp_state_unchanged")
        and all(value["status"] != "not_rejected"
                for name, value in result["lifecycle"].items() if name != "valid_reset")
        and all(value["status"] in ("rejected", "blocked")
                for value in asset_cases.values())
        and ready["status"] == "ready_for_caller_execution"
    )
    return result


def gates() -> List[Dict[str, str]]:
    reopen = {
        "exact_graphs_runtime_and_rights": (
            "Place both hash-pinned graphs in an approved isolated runner, install and pin a "
            "3.12.16-compatible onnxruntime or a new 3.10 environment, and clear "
            "product/redistribution and training-data rights with a recorded positive decision."),
        "real_paired_cohort": (
            "Score a rights-cleared held-out real paired cohort with clean references and "
            "complete output accounting."),
        "independent_listening_or_predictive_screen": (
            "Collect independent listening or a separately labeled authorized predictive "
            "screen; synthetic scores cannot qualify."),
        "target_runtime_timing_memory": (
            "Measure content/availability timing, memory and deadlines on the exact target "
            "runtime."),
        "provider_intake": (
            "Complete licensing review and opt-in provider intake before any registration."),
        "public_default_selection": (
            "Record an explicit public default decision; the candidate is OFF and unregistered."),
        "exact_reference_parity": (
            "Demonstrate parity against an exact approved DTLN reference vector."),
    }
    return [{"name": name, "status": "blocked", "reopen_condition": reopen[name]}
            for name in GATE_NAMES]


def source_reported() -> Dict[str, Any]:
    return {
        "status": "source_reported_not_reproduced",
        "used_for_qualification": False,
        "sources": [
            "research/noise_suppression_pilot_20261027.md",
            "research/voice-enhancement-20261101/candidate_matrix.csv",
            "research/selected_audio_enhancement_candidates.md",
            "REALTIME_COMPONENT_CANDIDATES.md",
            UPSTREAM_SNAPSHOT + "/README.md",
        ],
        "scope": (
            "30 paired DNS2020 items scored offline with the measured 384-sample stream lag "
            "compensated; the upstream README DNS-Challenge rank/MOS values and 32 ms model "
            "delay are separate source-reported conditions."
        ),
        "findings": [
            {"metric": "median_snr_gain_db", "value": 6.444},
            {"metric": "median_si_sdr_gain_db", "value": 6.529},
            {"metric": "stoi", "value": 0.9624},
            {"metric": "median_rtf", "value": 0.0324},
            {"metric": "measured_stream_lag_samples", "value": DELAY_SAMPLES},
        ],
        "upstream_reported": {
            "dns_challenge_real_time_rank": "8/17",
            "mos_gain_over_challenge_baseline": 0.24,
            "reported_model_delay_ms": 32,
            "note": "Transcribed from the pinned upstream README; not reproduced here.",
        },
        "note": ("Provenance only. These values are never reproduced, pooled, assigned to the "
                 "surrogate or used as an acceptance threshold."),
    }


def model_provenance() -> Dict[str, Any]:
    return {
        "candidate": "DTLN ONNX",
        "upstream_repository": UPSTREAM_REPOSITORY,
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_license": UPSTREAM_LICENSE,
        "upstream_license_copyright": UPSTREAM_LICENSE_COPYRIGHT,
        "upstream_license_file": UPSTREAM_LICENSE_PATH,
        "upstream_license_sha256": SOURCE_PINS[UPSTREAM_LICENSE_PATH],
        "source_snapshot": UPSTREAM_SNAPSHOT,
        "source_snapshot_in_sdk_worktree": False,
        "repository_resolution": {
            "snapshot": UPSTREAM_SNAPSHOT,
            "expected_remote": UPSTREAM_REPOSITORY,
            "expected_commit": UPSTREAM_COMMIT,
            "method": "git config --get remote.origin.url and git rev-parse HEAD in the pinned external checkout",
        },
        "source_files": {
            "README.md": SOURCE_PINS[UPSTREAM_SNAPSHOT + "/README.md"],
            "DTLN_model.py": SOURCE_PINS[UPSTREAM_SNAPSHOT + "/DTLN_model.py"],
            "real_time_processing_onnx.py":
                SOURCE_PINS[UPSTREAM_SNAPSHOT + "/real_time_processing_onnx.py"],
            "convert_weights_to_onnx.py":
                SOURCE_PINS[UPSTREAM_SNAPSHOT + "/convert_weights_to_onnx.py"],
        },
        "graphs": [
            {
                "role": spec["role"], "file": spec["path"], "sha256": spec["sha256"],
                "bytes": spec["bytes"], "tracked_in_upstream_commit": True,
                "present_in_sdk_worktree": False, "loaded_or_executed": False,
            }
            for spec in ASSET_SPECS
        ],
        "runtime_lock": {
            **RUNTIME_LOCK,
            "installed_in_sdk_worktree": False,
            "onnxruntime_importable": False,
        },
        "adapter": {
            "path": "adapters/dtln-onnx/adapter.json",
            "sha256": SOURCE_PINS["adapters/dtln-onnx/adapter.json"],
            "identity": UPSTREAM_ADAPTER_IDENTITY,
            "tasks": ["CLN-01"],
            "modes": ["offline"],
            "weights": "required_local",
            "entrypoint": ["python", "adapters/dtln-onnx/run.py"],
        },
        "asset_policy": (
            "Hash-pinned provenance only; no upstream source, graph, weight, runtime, "
            "audio or other asset is copied, vendored, built, packaged, downloaded or "
            "redistributed by this package."
        ),
    }


def licensing_analysis() -> Dict[str, Any]:
    return {
        "task_files_license": "Apache-2.0",
        "upstream_repository_license": UPSTREAM_LICENSE,
        "upstream_license_text_pinned": True,
        "upstream_license_sha256": SOURCE_PINS[UPSTREAM_LICENSE_PATH],
        "upstream_license_scope": (
            "Pinned MIT LICENSE for the exact repository snapshot, including tracked "
            "pretrained model files as distributed at that commit; no separate model-card, "
            "weights or runtime terms were found in that snapshot."
        ),
        "mit_notice_obligation": (
            "Preserve the copyright and permission notice in copies or substantial portions; "
            "this package copies no upstream portion."
        ),
        "training_data_provenance_established": False,
        "separate_weights_terms_established": False,
        "onnx_runtime_redistribution_terms_established": False,
        "redistribution_clearance": False,
        "product_use_clearance": False,
        "legal_review_completed": False,
        "asset_copied_vendored_built_or_downloaded": False,
        "blocked_gate": "exact_graphs_runtime_and_rights",
        "conclusion": (
            "MIT source licensing is pinned, but product/redistribution rights, training-data "
            "provenance and any separate model/weights or ONNX-runtime terms are not cleared. "
            "The rights gate remains blocked; this package distributes no upstream asset."
        ),
    }


def acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "mapped_cases": {
            "identity_noisy_control": {
                "evidence": ["controls.identity", "controls.named_baseline",
                             "conditions.speech"],
                "status": "measured_synthetic",
            },
            "established_task_matched_baseline": {
                "name": "noisy_input_no_processing",
                "evidence": ["controls.named_baseline"],
                "status": "measured_synthetic",
            },
            "paired_si_sdr_stoi": {
                "evidence": ["conditions.*.baseline_metrics", "conditions.*.candidate_metrics"],
                "status": "measured_synthetic",
                "scorer": SCORER_ID,
                "note": "Paired synthetic clean references only; no real-speech score.",
            },
            "clean_speech_preservation": {
                "evidence": ["controls.clean_speech_preservation"],
                "status": "measured_synthetic",
            },
            "peaks_and_invalid_outputs": {
                "evidence": ["conditions.*.candidate_metrics", "conditions.clipped",
                             "adverse"],
                "status": "measured_synthetic",
            },
            "unpaired_speech": {
                "status": "not_applicable",
                "reason": "No licensed unpaired speech, predictive screen or authorized listening was run.",
            },
            "alignment_state_memory_timing": {
                "status": "partial_synthetic",
                "alignment": "384-sample (three-hop) raw delay; aligned and raw scores recorded",
                "state": "causal hop state; invalid input never advances state",
                "memory": "host Python counts only; no target-device memory result",
                "timing": "no measured content/availability timing for an exact runtime",
            },
        },
        "not_reported": [
            "real paired cohort", "human listening or MOS", "target-device pacing or deadline",
            "installed runtime memory", "real ONNX inference", "release qualification",
        ],
    }


def tool_provenance() -> List[str]:
    return [
        "No DTLN source, ONNX graph, weight, audio file, runtime environment or vendor asset is present in this SDK worktree.",
        "Upstream repository, commit, MIT LICENSE, runner/model source, graphs and runtime lock are pinned by SHA-256 from an external research checkout; nothing is copied, vendored, built, downloaded or redistributed here.",
        "Only a deterministic Python standard-library synthetic generator, scalar-gain envelope proxy and dependency-free paired scorers are executed.",
        "All real-model pilot values quoted here are source-reported provenance and are never reproduced, pooled or used as thresholds.",
    ]


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for SDK-DTLN-ONNX.",
        "# source: paths are relative to SOURCE_ROOT; other paths are SDK-worktree relative.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in sorted(BOUNDARY_PINS):
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for path in sorted(SCORER_PINS):
        lines.append(f"{SCORER_PINS[path]}  {path}")
    for name in sorted(LOCAL_PIN_PATHS):
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")


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
        "profile": PROFILE,
        "verification_profile": PROFILE,
        "scope": (
            "Deterministic synthetic enhancement evidence at a task-local caller-supplied-asset "
            "boundary for the pinned DTLN two-graph ONNX stream; no selection, superiority, "
            "real-model, device, listening, benchmark or release claim."
        ),
        "boundary": BOUNDARY,
        "format": FORMAT,
        "stream": STREAM,
        "caller_supplied_asset_contract": {
            "root": "caller-supplied read-only directory",
            "source_commit": UPSTREAM_COMMIT,
            "engine": "two ONNX graphs in fixed order: mask estimation then signal estimation",
            "graph_1_role": "mask estimation over a 257-bin magnitude block with recurrent state",
            "graph_2_role": "time-domain signal estimation over the masked 512-sample block with recurrent state",
            "inputs_outputs": "two inputs and two outputs per graph, matching the pinned runner's state hand-off; exact state shapes are runtime-derived and not asserted here",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "block_samples": BLOCK_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "delay_samples": DELAY_SAMPLES,
            "graphs": [
                {"role": spec["role"], "path": spec["path"],
                 "sha256": spec["sha256"], "bytes": spec["bytes"]}
                for spec in ASSET_SPECS
            ],
            "runtime_lock": RUNTIME_LOCK,
            "fail_closed": True,
        },
        "surrogate": {
            "identity": "two_stage_scalar_gain_envelope_proxy_v0",
            "is_dtln_source": False,
            "is_spectral_mask": False,
            "block_samples": BLOCK_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "delay_samples": DELAY_SAMPLES,
            "signal_samples": WINDOW_SAMPLES,
            "caller_supplied_frozen_signals": True,
            "graph": False,
            "weights": False,
            "audio_read": False,
            "device_clock": False,
        },
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "scorer_pins": SCORER_PINS,
        "model_provenance": model_provenance(),
        "licensing_analysis": licensing_analysis(),
        "source_reported": source_reported(),
        "exact_blockers": EXACT_BLOCKERS,
        "missing_evidence": MISSING_EVIDENCE,
        "acceptance_profile": {
            "name": PROFILE,
            "source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": [
                "identity and noisy-input controls",
                "paired synthetic SI-SDR and STOI",
                "clean-speech preservation",
                "peaks and invalid outputs",
                "critical synthetic adverse cases",
                "alignment, state, memory and timing boundary",
            ],
            "not_applicable": [
                "no real paired cohort, so no real-speech score is reported",
                "no target runtime, so device timing, memory and deadlines are not measured",
                "no authorized listening or predictive screen was run",
            ],
        },
        "gates": [gate["name"] for gate in gates()],
        "invariants": [
            "Only this task directory is written; no shared SDK file, CMake, contract, header, registry, default, board, handoff or CI file changes.",
            "The fixture is opt-in, unregistered, disabled by default and not a provider or production callback.",
            "All signals are frozen deterministic synthetic floats; no graph, model, media, weight or runtime asset is read or produced.",
            "Configuration, geometry, shape, missing, invalid, nonfinite, epoch, position and lifecycle rejections fail closed without advancing state.",
            "Caller-supplied asset, commit, size, hash and runtime checks fail closed and never open a graph.",
            "Source-reported DTLN pilot and upstream values are provenance only and never used as thresholds.",
            "Three cold-start passes are byte-identical; canonical JSON and digest sidecars regenerate deterministically.",
            "Missing evidence never qualifies the candidate; decision remains DEFER.",
        ],
        "reopening_conditions": MISSING_EVIDENCE,
    }


def contract_bytes() -> bytes:
    return (json.dumps(_normalize_negzero(contract()), sort_keys=True, indent=2,
                       allow_nan=False).encode("utf-8") + b"\n")


def repeatability() -> Dict[str, Any]:
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


def regressions(condition_map: Mapping[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for name, value in condition_map.items():
        baseline = value["baseline_metrics"]
        candidate = value["candidate_metrics"]
        if value["candidate_worse_than_baseline"]:
            rows.append({
                "condition": name, "metric": "si_sdr_db",
                "candidate": candidate["si_sdr_db"], "baseline": baseline["si_sdr_db"],
                "interpretation": (
                    "Aligned surrogate is worse than the named noisy-input baseline in this "
                    "synthetic condition; recorded verbatim."),
            })
        elif candidate["status"] == "excluded":
            rows.append({
                "condition": name, "metric": "score_undefined",
                "candidate": None, "baseline": baseline["si_sdr_db"],
                "interpretation": (
                    "Paired score is undefined on the all-zero synthetic reference (" +
                    str(candidate["si_sdr_reason"]) + "); not counted as a win."),
            })
        if value["candidate_raw_metrics"]["si_sdr_db"] is not None:
            rows.append({
                "condition": name, "metric": "raw_lag_penalty_db",
                "candidate": value["candidate_raw_metrics"]["si_sdr_db"],
                "baseline": candidate["si_sdr_db"],
                "interpretation": (
                    "Uncompensated 384-sample stream lag degrades the paired score; alignment "
                    "must be handled explicitly by the caller."),
            })
    return rows


def core_report() -> Dict[str, Any]:
    condition_map = conditions()
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
        "stream": STREAM,
        "contract_id": f"{CONTRACT_SCHEMA_ID}:{TASK}",
        "contract_sha256": sha256(contract_bytes()),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "scorer_pins": SCORER_PINS,
        "model_provenance": model_provenance(),
        "caller_supplied_asset_gate": asset_gate(),
        "licensing_analysis": licensing_analysis(),
        "tool_provenance": tool_provenance(),
        "surrogate": {
            "identity": "two_stage_scalar_gain_envelope_proxy_v0",
            "is_dtln_source": False,
            "is_spectral_mask": False,
            "block_samples": BLOCK_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "delay_samples": DELAY_SAMPLES,
            "caller_supplied_frozen_signals": True,
            "graph": False,
            "weights": False,
        },
        "acceptance_profile": acceptance_profile(),
        "conditions": condition_map,
        "controls": controls(),
        "adverse": adverse(),
        "regressions": regressions(condition_map),
        "source_reported": source_reported(),
        "exact_blockers": EXACT_BLOCKERS,
        "gates": gates(),
        "missing_evidence": MISSING_EVIDENCE,
        "evidence_classes": [
            "synthetic_signal", "deterministic_surrogate",
            "caller_supplied_asset_intake", "upstream_provenance_hash_pinned",
            "source_reported_provenance_only", "proposal_only",
        ],
    }


def build_report() -> Dict[str, Any]:
    report = core_report()
    report["repeatability"] = repeatability()
    return report


def interpreter_is_pinned() -> bool:
    return platform.python_version() == EVIDENCE_INTERPRETER
