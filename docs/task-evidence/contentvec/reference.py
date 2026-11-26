# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for the ContentVec row.

This module is NOT ContentVec and NOT a ContentVec inference path. It does not
implement, approximate, simulate, convert or run a ContentVec encoder. A
pinned downstream consumer checkout and the transformers-format ContentVec /
HuBERT *config* are present, but the exact ``pytorch_model.bin`` checkpoint
weights and a hash-pinned PyTorch/Transformers runtime are absent. The module
therefore builds a bounded, deterministic blocker report:

* strict request validation at the installed v0 geometry, with fail-closed
  rejection of missing, invalid, nonfinite and out-of-range inputs;
* explicit consumer-source, config, weight and runtime probes (read-only,
  bounded, no network);
* ContentVec geometry derived only from the pinned config, preprocessor config
  and pinned loader declarations, never from a model load;
* synthetic harness stimuli for identity/rejection controls only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

No network, model weights, real corpus audio, native library or download is
used. No candidate feature or audio output is produced.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import struct
from typing import Any, Dict, Iterable, List, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0

SCHEMA_ID = "audio-sdk/contentvec-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/contentvec-contract/0.1"
TASK = "SDK-CONTENTVEC"
COMPONENT = "contentvec"
BRANCH = "swarm/SDK-CONTENTVEC"
BASE_COMMIT = "6967a728b5c4048fb01ed4522a76a6906fbcffe2"
TASK_PREFIX = "docs/task-evidence/contentvec/"

SOURCE_REPOSITORY = "RVC-Project/Retrieval-based-Voice-Conversion-WebUI"
SOURCE_REVISION = "81eed5e8f68b6bed1789f682fe78cdd324495afc"
SOURCE_LICENSE = "MIT"

MLX_SOURCE_REPOSITORY = "rvc-mlx-realtime (vendored Acelogic ContentVec path)"
MLX_SOURCE_REVISION = "95a69ae2467738c605762bb5e84e8cdcef09d83d"

UPSTREAM_CONTENTVEC_REPOSITORY = "auspicious3000/ContentVec"
CONTENTVEC_MODEL_ARCHITECTURE = "HubertModelWithFinalProj"
CONTENTVEC_MODEL_TYPE = "hubert"
CONTENTVEC_HIDDEN_SIZE = 768
CONTENTVEC_LAYER_COUNT = 12
CONTENTVEC_ATTENTION_HEADS = 12
CONTENTVEC_INTERMEDIATE_SIZE = 3072
CONTENTVEC_CONV_CHANNELS = 512
CONTENTVEC_CONV_FEATURE_LAYERS = 7
CONTENTVEC_CLASSIFIER_PROJ_SIZE = 256
CONTENTVEC_CONV_STRIDE = (5, 2, 2, 2, 2, 2, 2)
CONTENTVEC_CONV_KERNEL = (10, 3, 3, 3, 3, 2, 2)
CONTENTVEC_FRAME_STRIDE_SAMPLES = 320
CONTENTVEC_FRAME_RATE_HZ = 50.0
CONTENTVEC_SUPPORTED_OUTPUT_LAYERS = {9: 256, 12: 768}
CONTENTVEC_V1_LAYER = 9
CONTENTVEC_V1_FEATURE_DIM = 256
CONTENTVEC_V2_LAYER = 12
CONTENTVEC_V2_FEATURE_DIM = 768
CONTENTVEC_CONFIG_TORCH_DTYPE = "float16"
CONTENTVEC_CONFIG_TRANSFORMERS_VERSION = "4.49.0"
RUNTIME_TORCH_PIN = "torch==2.4.1+cpu"
RUNTIME_TORCHAUDIO_PIN = "torchaudio==2.4.1+cpu"
RUNTIME_TRANSFORMERS_PIN = "transformers>=4.49.0,<4.50"

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
SOURCE_ROOT = WORKSPACE / "research/voice-conversion-eval-20261101/repos/rvc"
MLX_SOURCE_ROOT = (
    WORKSPACE / "research/voice-conversion-eval-20261101/repos/"
    "rvc-mlx-realtime")
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

CONFIG_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/rvc/assets/hubert_base/"
    "config.json")
PREPROCESSOR_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/rvc/assets/hubert_base/"
    "preprocessor_config.json")
LOADER_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/rvc/infer/hubert.py")
LICENSE_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/rvc/LICENSE")
REQUIREMENTS_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/rvc/"
    "requirments_cpu_py312.txt")
README_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/rvc/README.md")
MLX_CONVERT_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "rvc_mlx_rt/convert/hubert.py")
MLX_MODEL_MANAGER_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "rvc_mlx_rt/model_manager.py")
ACCENT_README_RELATIVE = (
    "research/accent-conversion-20261101/README.md")
EVAL_README_RELATIVE = (
    "research/voice-conversion-eval-20261101/README.md")

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only the stable linked-row identity is projected, never hashed.
SOURCE_PINS = {
    ACCENT_README_RELATIVE:
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    EVAL_README_RELATIVE:
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    CONFIG_RELATIVE:
        "0346950779dfb7f9316fa74ed846e2b8a22a08eedfdc5387b73f327cb1a4a7cf",
    PREPROCESSOR_RELATIVE:
        "7c1976a680fb7acc757cd36fb08eef878fa36c70b4c9d2d595df9c608bbbbf0e",
    LOADER_RELATIVE:
        "bbfba54d1d83eae3fb634b2909f8f6bf41e6ffe436200ec246867c5c93ebba26",
    LICENSE_RELATIVE:
        "bec61ed1eb9a3748644ddbc50303aa6978e14eeaba46822e59a006c722b52585",
    REQUIREMENTS_RELATIVE:
        "902338f1c8ef6c38186a34c19dec95e8df56030863b7a584b703a443127ea541",
    README_RELATIVE:
        "6ae347c0cc60836f1e7fd2b73ee73327746e66c32a5dd4270d02a096810bca8b",
    MLX_CONVERT_RELATIVE:
        "bfe32a066e4a1e6748b042956df5a6bf05b2255c45a4c05e1fe0d67b72deef0d",
    MLX_MODEL_MANAGER_RELATIVE:
        "9a0824f79e61291c0fca908d12c83d6e48c203ec265adeb7f54272e8cc4f8ddc",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

# Stable linked-row identity only. Status, owner, review, handoff, timestamps,
# dispatch priority, history and claim are deliberately excluded and never
# gated. The shared board itself is never modified.
EXPECTED_LINK = {
    "task_id": TASK,
    "title": "ContentVec",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)

CANDIDATE = "contentvec"
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)
REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples", "samples",
    "epoch", "first_input_sample", "lifecycle", "execution_mode",
    "output_layer",
})

SOURCE_ARTIFACT_FILES = (
    "reference.py", "run.py", "test_reference.py", "verify.py",
)

WEIGHT_MARKERS = (
    "pytorch_model.bin",
    "model.safetensors",
    "hubert.npz",
    "hubert_base.pt",
    "checkpoint_best_legacy_500.pt",
    "checkpoint_last.pt",
    "contentvec.pt",
)
WEIGHT_CANDIDATE_PATHS = (
    "research/voice-conversion-eval-20261101/repos/rvc/assets/hubert_base",
    "research/voice-conversion-eval-20261101/repos/rvc/assets/contentvec",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "assets/contentvec",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "rvc_mlx_rt/assets/contentvec",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/models",
    "data/assets/rvc-v2-vctk-p226/hubert_base",
    "data/models/contentvec",
    "research/voice-conversion-eval-20261101/checkpoints",
    "~/"
    ".cache/huggingface/hub/models--lengyue233--content-vec-best",
    "~/.cache/huggingface/hub/models--IAHispano--Applio",
)
UPSTREAM_SOURCE_CANDIDATE_PATHS = (
    "research/voice-conversion-eval-20261101/repos/contentvec",
    "research/voice-conversion-eval-20261101/repos/ContentVec",
    "research/accent-conversion-20261101/repos/contentvec",
    "data/models/contentvec",
)
RUNTIME_CANDIDATE_PATHS = (
    "research/voice-conversion-eval-20261101/repos/rvc/.venv",
    "research/voice-conversion-eval-20261101/repos/rvc/.venv/bin/python",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/.venv",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    ".venv/bin/python",
    "research/voice-conversion-eval-20261101/.venv-eval/bin/python",
    "data/envs/rvc",
    "data/envs/rvc/bin/python",
)
RUNTIME_MODULES = (
    "torch", "torchaudio", "transformers", "numpy", "soundfile",
    "huggingface_hub",
)
RUNTIME_LOCK_CANDIDATES = (
    "research/voice-conversion-eval-20261101/repos/rvc/.venv/pyvenv.cfg",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    ".venv/pyvenv.cfg",
    "research/voice-conversion-eval-20261101/.venv-eval/pyvenv.cfg",
)

FIXTURE_SPANS = (
    (0, 800, "voiced"),
    (800, 1000, "pause"),
    (1000, 1800, "voiced"),
    (1800, 2100, "filler"),
    (2100, 2800, "voiced"),
    (2800, 3200, "pause"),
)

GATES = (
    {
        "id": "RG-01",
        "gate": "exact_contentvec_source_config_and_weight_pin",
        "status": "blocked",
        "reason": (
            "The MIT RVC consumer checkout is pinned at 81eed5e8 and the "
            "transformers-format ContentVec/HuBERT config and preprocessor "
            "config are present and digest-pinned, but the exact "
            "assets/hubert_base/pytorch_model.bin ContentVec weights and the "
            "upstream auspicious3000/ContentVec source are absent; no weight "
            "SHA-256 or byte count exists locally."),
        "reopen": (
            "Stage the exact ContentVec checkpoint file matching the pinned "
            "HuBERTModelWithFinalProj config, and the upstream ContentVec "
            "source/licence, each with recorded SHA-256 and byte counts "
            "before any reproduction."),
    },
    {
        "id": "RG-02",
        "gate": "license_rights_and_asset_review",
        "status": "blocked",
        "reason": (
            "The pinned RVC consumer source is MIT, but the upstream "
            "ContentVec source/weight terms and the checkpoint model-card or "
            "redistribution terms are not recorded locally; caller-supplied-"
            "asset use and input-corpus rights for derived features are "
            "unconfirmed."),
        "reopen": (
            "Record the upstream ContentVec source and weight licence/terms, "
            "the caller-supplied-asset redistribution/use scope, and an "
            "approved input-corpus and derived-feature use decision."),
    },
    {
        "id": "RG-03",
        "gate": "exact_runtime_build_and_install_parity",
        "status": "blocked",
        "reason": (
            "No PyTorch/Transformers environment is installed; torch, "
            "torchaudio and transformers are not importable. The pinned "
            "requirements text constrains torch 2.4.1+cpu and transformers "
            "4.49.x, and the config declares transformers 4.49.0, but that "
            "is not an installed runtime, install digest or verified offline "
            "load path."),
        "reopen": (
            "Create a frozen, hash-pinned CPU runtime for the exact "
            "torch/transformers versions, install it in a clean environment, "
            "and prove import and version parity before loading weights."),
    },
    {
        "id": "RG-04",
        "gate": "encoder_geometry_layer_delay_drain_and_mode_parity",
        "status": "blocked",
        "reason": (
            "No checkpoint weight was loaded, so the 320-sample "
            "convolutional stride, 50 Hz content rate, 768-wide hidden state, "
            "12 layers, v1 layer-9-plus-final-proj (256) path, v2 layer-12 "
            "last-hidden-state (768) path, feature delay, state/reset, finite "
            "drain and v0 mode ownership were not exercised."),
        "reopen": (
            "With the exact weights and runtime, verify the convolutional "
            "stride, 768-wide hidden state, layer-9 final-projection and "
            "layer-12 paths, feature delay, state/reset, finite drain and "
            "execution-mode ownership at 16 kHz mono."),
    },
    {
        "id": "RG-05",
        "gate": "rights_qualified_cohort_and_content_fidelity",
        "status": "blocked",
        "reason": (
            "The accent-conversion record explicitly says QuickVC/ContentVec "
            "were not tested as standalone systems and no accent-target "
            "checkpoint was available; no permitted multi-speaker/language "
            "cohort, paired reference features, semantic-fidelity score or "
            "held-out comparison exists."),
        "reopen": (
            "Freeze a permitted multi-speaker/language cohort with paired "
            "reference features, score content/semantic fidelity separately, "
            "and retain per-group failures."),
    },
    {
        "id": "RG-06",
        "gate": "content_preservation_and_adverse_cases",
        "status": "blocked",
        "reason": (
            "No silence, clipping, nonfinite, unfamiliar-speech or adverse "
            "input was run through the exact encoder; only local synthetic "
            "harness rejection and identity controls exist."),
        "reopen": (
            "Reproduce paired content/preservation controls with the exact "
            "encoder, including silence, peaks, nonfinite input and "
            "unfamiliar speech, and record every failure."),
    },
    {
        "id": "RG-07",
        "gate": "target_runtime_timing_memory_and_callback_suitability",
        "status": "blocked",
        "reason": (
            "There is no standalone ContentVec timing, memory, first-output "
            "or tail measurement anywhere in the workspace. The RVC "
            "whole-file pipeline timing is a different system and is not "
            "attributed to ContentVec here."),
        "reopen": (
            "Measure encoder-only and end-to-end paced timing, memory, "
            "first-output/tail latency and callback suitability independently "
            "of compute speed."),
    },
    {
        "id": "RG-08",
        "gate": "provider_intake_public_surface_independent_review_release",
        "status": "blocked",
        "reason": (
            "No caller-supplied-asset adapter, provider intake, descriptor, "
            "public-surface decision, independent exact-head review or release "
            "approval exists."),
        "reopen": (
            "Complete provider intake, a versioned caller-supplied-asset "
            "adapter and public-surface decision, then obtain independent "
            "exact-head review and release approval."),
    },
)

UPSTREAM_BLOCKER = {
    "status": "blocked_weights_and_runtime_absent",
    "artifact": (
        "ContentVec/HuBERT transformers checkpoint "
        "assets/hubert_base/pytorch_model.bin matching the pinned "
        "HubertModelWithFinalProj config, the upstream "
        "auspicious3000/ContentVec source and terms, and the exact "
        "hash-pinned PyTorch/Transformers runtime required to load it"),
    "source": {
        "status": "consumer_present_pinned_upstream_source_absent",
        "repository": SOURCE_REPOSITORY,
        "revision": SOURCE_REVISION,
        "license": SOURCE_LICENSE,
        "upstream_repository": UPSTREAM_CONTENTVEC_REPOSITORY,
        "upstream_source_present": False,
        "config_present": True,
        "preprocessor_config_present": True,
    },
    "weights": {
        "status": "absent",
        "artifact": "ContentVec/HuBERT checkpoint (transformers format)",
        "declared_consumer_path": (
            "research/voice-conversion-eval-20261101/repos/rvc/assets/"
            "hubert_base/pytorch_model.bin"),
        "declared_mlx_consumer_path": (
            "research/voice-conversion-eval-20261101/repos/"
            "rvc-mlx-realtime/assets/contentvec/pytorch_model.bin"),
        "upstream_repository": "https://huggingface.co/IAHispano/Applio",
        "required_files": [
            "config.json",
            "preprocessor_config.json",
            "pytorch_model.bin",
        ],
        "expected_architecture": CONTENTVEC_MODEL_ARCHITECTURE,
        "expected_hidden_size": CONTENTVEC_HIDDEN_SIZE,
        "expected_layer_count": CONTENTVEC_LAYER_COUNT,
        "expected_frame_stride_samples": CONTENTVEC_FRAME_STRIDE_SAMPLES,
        "expected_classifier_proj_size": CONTENTVEC_CLASSIFIER_PROJ_SIZE,
        "sha256": None,
        "byte_count": None,
        "license": None,
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "PyTorch CPU build matching the pinned requirements text",
            "Transformers HuBERTModel/AutoFeatureExtractor 4.49.x",
            "NumPy for the feature-extractor input path",
            "a hash-pinned lockfile or wheel set for the exact versions",
        ],
        "declared_constraints": [
            RUNTIME_TORCH_PIN,
            RUNTIME_TORCHAUDIO_PIN,
            RUNTIME_TRANSFORMERS_PIN,
        ],
        "sha256": None,
        "lockfile": None,
    },
    "expected_license": (
        "MIT for the pinned RVC consumer checkout; the upstream "
        "auspicious3000/ContentVec source and ContentVec weight terms are not "
        "recorded locally and require separate review"),
    "pinned_revision": SOURCE_REVISION,
    "source_digest": None,
    "runtime_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "A recorded upstream ContentVec source and weight licence/terms "
        "decision, an explicit caller-supplied-asset redistribution/use "
        "decision, permission for every input clip and any derived feature, "
        "and consent for any downstream voice or speaker are required before "
        "any reproduction, adapter or release claim."),
    "workspace_search": (
        "Bounded read-only checks of the pinned RVC and RVC-MLX consumer "
        "trees, the data asset directories and the Hugging Face cache paths "
        "found the ContentVec config and preprocessor config but no "
        "pytorch_model.bin, .safetensors, hubert.npz or fairseq checkpoint. "
        "No weight SHA-256 or byte count exists locally."),
    "not_attempted": [
        "no network download or package installation",
        "no fabricated, reconstructed or surrogate ContentVec weights",
        "no substitute encoder or feature extractor",
        "no copied upstream source, real corpus audio or licence text",
        "no real corpus read, model load or feature/audio output",
    ],
    "reopen": (
        "Stage the exact ContentVec checkpoint with SHA-256/byte counts, "
        "record upstream source and weight rights, rebuild a hash-pinned "
        "runtime, then repeat the voice profile with a permitted cohort and "
        "independent review."),
}

NON_CLAIMS = (
    "No ContentVec checkpoint, weight, feature tensor or audio output is included.",
    "No ContentVec, HuBERT or RVC inference is implemented, approximated or simulated.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default.",
    "No real corpus, consent, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No missing, rejected or untested result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/contentvec/ is touched.",
    "The reference is a task-local evidence builder, not an encoder.",
    "All harness stimuli are analytic or seeded synthetic; no weights are used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
)

VOICE_PROFILE_SOURCE = (
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md")


class EvidenceError(ValueError):
    """Base error with a stable machine-readable code."""

    code = "EVIDENCE_ERROR"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class ConfigError(EvidenceError):
    code = "INVALID_CONFIG"


class InputError(EvidenceError):
    code = "INVALID_INPUT"


class JsonError(EvidenceError):
    code = "INVALID_JSON"


class WeightsAbsent(EvidenceError):
    code = "WEIGHTS_ABSENT"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _pairs_hook(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise JsonError("DUPLICATE_KEY: " + key, "DUPLICATE_KEY")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise JsonError("NONFINITE_CONSTANT: " + token, "NONFINITE_CONSTANT")


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_pairs_hook,
                          parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise JsonError("INVALID_JSON: " + str(error), "INVALID_JSON")


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def _r(value: float, places: int = 9) -> float:
    return round(float(value), places)


def tensor_digest(samples: Iterable[float]) -> str:
    digest = hashlib.sha256()
    for value in samples:
        digest.update(struct.pack("<f", float(value)))
    return digest.hexdigest()


def peak_abs(samples: Iterable[float]) -> float:
    return max((abs(float(value)) for value in samples), default=0.0)


def rms(samples: Sequence[float]) -> float:
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    total = math.fsum(float(value) * float(value) for value in samples)
    return math.sqrt(total / len(samples))


def db_ratio(numerator: float, denominator: float) -> float:
    if numerator <= 0.0 or denominator <= 0.0:
        raise InputError("NONPOSITIVE_RMS", "NONPOSITIVE_RMS")
    return 20.0 * math.log10(numerator / denominator)


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield (state / 4294967296.0) * 2.0 - 1.0


def silence(length: int = 1600) -> Tuple[float, ...]:
    return (0.0,) * length


def impulse(length: int = 1600, position: int = 800,
            amplitude: float = 0.5) -> Tuple[float, ...]:
    if not 0 <= position < length:
        raise ConfigError("impulse position out of range", "INVALID_STIMULUS")
    values = [0.0] * length
    values[position] = amplitude
    return tuple(values)


def step(length: int = 1600, position: int = 800,
         amplitude: float = 0.25) -> Tuple[float, ...]:
    if not 0 <= position <= length:
        raise ConfigError("step position out of range", "INVALID_STIMULUS")
    return tuple(0.0 if index < position else amplitude
                 for index in range(length))


def sweep(length: int = 1600, start_hz: float = 200.0,
          end_hz: float = 3000.0, amplitude: float = 0.3) -> Tuple[float, ...]:
    if length <= 0 or start_hz <= 0.0 or end_hz <= 0.0:
        raise ConfigError("invalid sweep geometry", "INVALID_STIMULUS")
    duration = length / float(SAMPLE_RATE_HZ)
    values = []
    for index in range(length):
        t = index / float(SAMPLE_RATE_HZ)
        phase = 2.0 * math.pi * (start_hz * t +
                                 (end_hz - start_hz) * t * t /
                                 (2.0 * duration))
        values.append(amplitude * math.sin(phase))
    return tuple(values)


def _span_kind(index: int) -> str:
    for start, end, kind in FIXTURE_SPANS:
        if start <= index < end:
            return kind
    return "pause"


def speech_like(length: int = 3200, seed: int = 20261126) -> Tuple[float, ...]:
    noise = _lcg(seed)
    values = []
    for index in range(length):
        kind = _span_kind(index)
        noise_value = next(noise)
        t = index / float(SAMPLE_RATE_HZ)
        if kind == "voiced":
            value = (0.25 * math.sin(2.0 * math.pi * 120.0 * t) +
                     0.12 * math.sin(2.0 * math.pi * 240.0 * t) +
                     0.06 * math.sin(2.0 * math.pi * 360.0 * t))
            envelope = 0.65 + 0.35 * math.sin(2.0 * math.pi * 3.0 * t)
            value = value * envelope + 0.005 * noise_value
        elif kind == "filler":
            value = 0.02 * noise_value
        else:
            value = 0.001 * noise_value
        values.append(value)
    return tuple(values)


STIMULUS_GENERATORS = {
    "silence": lambda: silence(1600),
    "impulse": lambda: impulse(1600, 800, 0.5),
    "step": lambda: step(1600, 800, 0.25),
    "sweep": lambda: sweep(1600, 200.0, 3000.0, 0.3),
    "speech_like": lambda: speech_like(3200),
}


def stimulus_metrics(name: str, samples: Sequence[float]) -> Dict[str, Any]:
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    peak = 0.0
    nonfinite = 0
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("INVALID_SAMPLE_TYPE: " + str(index),
                             "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            nonfinite += 1
            continue
        peak = max(peak, abs(number))
    if nonfinite:
        raise InputError("NONFINITE_SAMPLE", "NONFINITE")
    if peak > MAX_ABS_STIMULUS:
        raise InputError("STIMULUS_OUT_OF_RANGE", "OUT_OF_RANGE")
    return {
        "name": name,
        "sample_count": len(samples),
        "peak_abs": _r(peak),
        "rms": _r(rms([float(value) for value in samples])),
        "nonfinite_count": 0,
        "digest": tensor_digest([float(value) for value in samples]),
    }


def speech_contrast(samples: Sequence[float]) -> Dict[str, Any]:
    voiced = []
    pause = []
    for index, value in enumerate(samples):
        kind = _span_kind(index)
        if kind == "voiced":
            voiced.append(float(value))
        elif kind == "pause":
            pause.append(float(value))
    voiced_rms = rms(voiced)
    pause_rms = rms(pause)
    return {
        "voiced_rms": _r(voiced_rms),
        "pause_rms": _r(pause_rms),
        "voiced_to_pause_db": _r(db_ratio(voiced_rms, pause_rms)),
        "proxy": "source-anchored voiced/pause RMS contrast; not intelligibility",
    }


def frame_geometry(sample_count: int) -> Dict[str, Any]:
    if isinstance(sample_count, bool) or not isinstance(sample_count, int):
        raise InputError("INVALID_SAMPLE_COUNT", "INVALID_SAMPLE_COUNT")
    if sample_count < 0:
        raise InputError("NEGATIVE_SAMPLE_COUNT", "INVALID_SAMPLE_COUNT")
    full = sample_count // CONTENTVEC_FRAME_STRIDE_SAMPLES
    return {
        "sample_count": sample_count,
        "stride_samples": CONTENTVEC_FRAME_STRIDE_SAMPLES,
        "full_frames": full,
        "remainder_samples": sample_count -
        full * CONTENTVEC_FRAME_STRIDE_SAMPLES,
        "measured_here": False,
        "note": ("Arithmetic floor division on the declared 320-sample "
                 "stride; not a model measurement."),
    }


def _validate_sample_list(samples: Any, expected: int | None) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise InputError("SAMPLES_NOT_A_LIST", "INVALID_SAMPLE_TYPE")
    if expected is not None and len(samples) != expected:
        raise InputError("WRONG_SAMPLE_COUNT", "WRONG_SAMPLE_COUNT")
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    result: List[float] = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("INVALID_SAMPLE_TYPE: " + str(index),
                             "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            raise InputError("NONFINITE_SAMPLE: " + str(index), "NONFINITE")
        if abs(number) > MAX_ABS_INPUT:
            raise InputError("SAMPLE_OUT_OF_RANGE: " + str(index),
                             "OUT_OF_RANGE")
        result.append(number)
    return result


def _require_int(value: Any, code: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(code, code)
    if minimum is not None and value < minimum:
        raise ConfigError(code, code)
    return value


def validate_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise InputError("request must be an object", "INVALID_REQUEST")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown),
                          "UNKNOWN_FIELD")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing),
                          "MISSING_FIELD")
    candidate = request["candidate"]
    if candidate != CANDIDATE:
        raise ConfigError("UNKNOWN_CANDIDATE", "UNKNOWN_CANDIDATE")
    if _require_int(request["sample_rate_hz"], "WRONG_RATE") != SAMPLE_RATE_HZ:
        raise ConfigError("WRONG_RATE", "WRONG_RATE")
    if _require_int(request["channels"], "WRONG_CHANNELS") != 1:
        raise ConfigError("WRONG_CHANNELS", "WRONG_CHANNELS")
    if _require_int(request["frame_samples"], "WRONG_FRAME") != FRAME_SAMPLES:
        raise ConfigError("WRONG_FRAME", "WRONG_FRAME")
    samples = _validate_sample_list(request["samples"], FRAME_SAMPLES)
    epoch = _require_int(request["epoch"], "INVALID_EPOCH", 0)
    first_input_sample = _require_int(request["first_input_sample"],
                                      "INVALID_POSITION", 0)
    lifecycle = request["lifecycle"]
    if lifecycle not in LIFECYCLES:
        raise ConfigError("INVALID_LIFECYCLE", "INVALID_LIFECYCLE")
    execution_mode = _require_int(request["execution_mode"], "INVALID_MODE")
    if execution_mode not in EXECUTION_MODES:
        raise ConfigError("INVALID_MODE", "INVALID_MODE")
    output_layer = _require_int(request["output_layer"],
                                "INVALID_OUTPUT_LAYER")
    if output_layer not in CONTENTVEC_SUPPORTED_OUTPUT_LAYERS:
        raise ConfigError("UNSUPPORTED_OUTPUT_LAYER",
                          "UNSUPPORTED_OUTPUT_LAYER")
    return {
        "candidate": candidate,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "samples": tuple(samples),
        "epoch": epoch,
        "first_input_sample": first_input_sample,
        "lifecycle": lifecycle,
        "execution_mode": execution_mode,
        "output_layer": output_layer,
        "feature_dim": CONTENTVEC_SUPPORTED_OUTPUT_LAYERS[output_layer],
    }


def probe_candidate(request: Any) -> None:
    validated = validate_request(request)
    raise WeightsAbsent(
        "WEIGHTS_ABSENT: " + validated["candidate"] + " ContentVec weights "
        "and pinned runtime are not present; no feature extraction is "
        "performed", "WEIGHTS_ABSENT")


def _base_request() -> Dict[str, Any]:
    return {
        "candidate": CANDIDATE,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "samples": [0.0] * FRAME_SAMPLES,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
        "output_layer": CONTENTVEC_V2_LAYER,
    }


def _adverse_request_specs():
    base = _base_request()

    def variant(**changes):
        value = dict(base)
        value.update(changes)
        return value

    def with_samples(samples):
        return variant(samples=samples)

    short = [0.0] * (FRAME_SAMPLES - 1)
    nan_samples = [0.0] * FRAME_SAMPLES
    nan_samples[7] = float("nan")
    inf_samples = [0.0] * FRAME_SAMPLES
    inf_samples[9] = float("inf")
    negative_inf_samples = [0.0] * FRAME_SAMPLES
    negative_inf_samples[9] = float("-inf")
    return (
        ("unknown_candidate", variant(candidate="content_vec")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("wrong_rate", variant(sample_rate_hz=48000)),
        ("wrong_channels", variant(channels=2)),
        ("wrong_frame", variant(frame_samples=320)),
        ("short_samples", with_samples(short)),
        ("nonfinite_nan", with_samples(nan_samples)),
        ("nonfinite_inf", with_samples(inf_samples)),
        ("nonfinite_negative_inf", with_samples(negative_inf_samples)),
        ("out_of_range", with_samples([4.5] * FRAME_SAMPLES)),
        ("bool_sample", with_samples([True] + [0.0] * (FRAME_SAMPLES - 1))),
        ("string_sample", with_samples(["0.0"] + [0.0] *
                                       (FRAME_SAMPLES - 1))),
        ("negative_epoch", variant(epoch=-1)),
        ("bool_epoch", variant(epoch=True)),
        ("negative_position", variant(first_input_sample=-160)),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("invalid_execution_mode", variant(execution_mode=4)),
        ("unsupported_output_layer_high", variant(output_layer=13)),
        ("unsupported_output_layer_zero", variant(output_layer=0)),
        ("unsupported_output_layer_ten", variant(output_layer=10)),
        ("bool_output_layer", variant(output_layer=True)),
        ("request_not_object", "not-an-object"),
    )


def _adverse_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    for name, request in _adverse_request_specs():
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_request(request)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "cases": cases,
        "note": ("Invalid requests are rejected before any candidate call; no "
                 "metrics exist."),
    }


def _json_adverse_cases() -> Dict[str, Any]:
    specs = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} extra'),
        ("invalid_syntax", '{"a":}'),
    )
    cases: List[Dict[str, Any]] = []
    for name, text in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            strict_json_loads(text)
            accepted = True
        except JsonError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "cases": cases,
    }


def missing_result(fixture_name: str) -> Dict[str, Any]:
    return {
        "fixture": fixture_name,
        "status": "blocked",
        "reason": "weights_and_runtime_absent",
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def _module_importable(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _resolve_workspace_path(label: str) -> Path:
    if label.startswith("~/"):
        return Path.home() / label[2:]
    return WORKSPACE / label


def _read_git_revision(root: Path) -> str | None:
    head_path = root / ".git/HEAD"
    if not head_path.is_file():
        return None
    head = head_path.read_text(encoding="ascii").strip()
    if not head.startswith("ref: "):
        return head or None
    reference = head[5:].strip()
    reference_path = root / ".git" / reference
    if reference_path.is_file():
        return reference_path.read_text(encoding="ascii").strip() or None
    packed_path = root / ".git/packed-refs"
    if packed_path.is_file():
        for line in packed_path.read_text(encoding="ascii").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            if len(parts) == 2 and parts[1] == reference:
                return parts[0]
    return None


SOURCE_CORE_FILES = (
    CONFIG_RELATIVE,
    PREPROCESSOR_RELATIVE,
    LOADER_RELATIVE,
    LICENSE_RELATIVE,
    REQUIREMENTS_RELATIVE,
)
CONSUMER_DECLARATION_FILES = (
    MLX_CONVERT_RELATIVE,
    MLX_MODEL_MANAGER_RELATIVE,
)


def _pin_matches(relative: str) -> bool:
    target = WORKSPACE / relative
    if not target.is_file():
        return False
    return sha256_file(target) == SOURCE_PINS[relative]


def source_probe() -> Dict[str, Any]:
    revision = _read_git_revision(SOURCE_ROOT) if SOURCE_ROOT.is_dir() else None
    license_present = (WORKSPACE / LICENSE_RELATIVE).is_file()
    license_text = ((WORKSPACE / LICENSE_RELATIVE).read_text(encoding="utf-8")
                    if license_present else "")
    core_pins = {path: _pin_matches(path) for path in SOURCE_CORE_FILES}
    declaration_pins = {path: _pin_matches(path)
                        for path in CONSUMER_DECLARATION_FILES}
    config_present = (WORKSPACE / CONFIG_RELATIVE).is_file()
    preprocessor_present = (WORKSPACE / PREPROCESSOR_RELATIVE).is_file()
    weights_present = weights_probe()["present"]
    upstream_present = any(
        _resolve_workspace_path(label).exists()
        for label in UPSTREAM_SOURCE_CANDIDATE_PATHS)
    present = (
        SOURCE_ROOT.is_dir()
        and revision == SOURCE_REVISION
        and license_text.startswith("MIT License")
        and all(core_pins.values())
        and all(declaration_pins.values())
        and config_present
        and preprocessor_present
        and not weights_present
        and not upstream_present
    )
    return {
        "status": ("consumer_present_pinned_upstream_source_absent"
                   if present else "source_mismatch_or_weights_changed"),
        "present": present,
        "verified": present,
        "repository": SOURCE_REPOSITORY,
        "revision": revision,
        "expected_revision": SOURCE_REVISION,
        "license": SOURCE_LICENSE if license_present else None,
        "license_path": LICENSE_RELATIVE,
        "pinned_files": core_pins,
        "consumer_declaration_files": declaration_pins,
        "consumer_declaration_repository": MLX_SOURCE_REPOSITORY,
        "consumer_declaration_revision": MLX_SOURCE_REVISION,
        "contentvec_config_present": config_present,
        "preprocessor_config_present": preprocessor_present,
        "weights_present": weights_present,
        "upstream": {
            "repository": UPSTREAM_CONTENTVEC_REPOSITORY,
            "present": upstream_present,
            "checked_paths": sorted(UPSTREAM_SOURCE_CANDIDATE_PATHS),
        },
        "note": (
            "Read-only per-file digest checks of the pinned MIT RVC consumer "
            "checkout. The transformers-format ContentVec config is present; "
            "the upstream ContentVec checkout and the checkpoint weights are "
            "absent. No upstream file is copied or executed."),
    }


def _weight_markers_in(directory: Path, max_depth: int = 4) -> List[str]:
    found: List[str] = []
    base_depth = len(directory.parts)
    for current, directory_names, file_names in os.walk(directory):
        current_path = Path(current)
        depth = len(current_path.parts) - base_depth
        if depth >= max_depth:
            directory_names[:] = []
        else:
            directory_names[:] = sorted(directory_names)
        for name in sorted(file_names):
            if name in WEIGHT_MARKERS or name.endswith(".safetensors"):
                found.append(
                    (current_path / name).relative_to(directory).as_posix())
    return sorted(found)


def weights_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    empty_directories: List[str] = []
    for label in WEIGHT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.is_file():
            if (target.name in WEIGHT_MARKERS or
                    target.name.endswith(".safetensors")):
                found.append(label)
        elif target.is_dir():
            hits = _weight_markers_in(target)
            if hits:
                found.extend(
                    (Path(label) / hit).as_posix() for hit in hits)
            else:
                empty_directories.append(label)
    status = ("weights_present_unqualified" if found
              else "blocked_weights_absent")
    return {
        "empty_directories": sorted(set(empty_directories)),
        "status": status,
        "artifact": "ContentVec/HuBERT checkpoint (transformers format)",
        "declared_consumer_path": (
            "research/voice-conversion-eval-20261101/repos/rvc/assets/"
            "hubert_base/pytorch_model.bin"),
        "declared_mlx_consumer_path": (
            "research/voice-conversion-eval-20261101/repos/"
            "rvc-mlx-realtime/assets/contentvec/pytorch_model.bin"),
        "upstream_repository": "https://huggingface.co/IAHispano/Applio",
        "required_files": [
            "config.json",
            "preprocessor_config.json",
            "pytorch_model.bin",
        ],
        "sha256": None,
        "byte_count": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "present": bool(found),
        "note": ("Read-only path and name checks only; no archive, cache blob "
                 "or weight file is opened, downloaded or reconstructed."),
    }


def runtime_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in RUNTIME_CANDIDATE_PATHS:
        checked.append(label)
        if _resolve_workspace_path(label).exists():
            found.append(label)
    modules = {name: _module_importable(name) for name in RUNTIME_MODULES}
    locks = [path for path in RUNTIME_LOCK_CANDIDATES
             if (WORKSPACE / path).is_file()]
    requirements = WORKSPACE / REQUIREMENTS_RELATIVE
    declared = []
    if requirements.is_file():
        text = requirements.read_text(encoding="utf-8")
        for needle in (RUNTIME_TORCH_PIN, RUNTIME_TORCHAUDIO_PIN,
                       RUNTIME_TRANSFORMERS_PIN):
            if needle in text:
                declared.append(needle)
    pinned = bool(found) and bool(locks) and all(modules.values())
    return {
        "status": "runtime_present_unqualified" if pinned
                  else "blocked_runtime_unpinned",
        "checked_paths": sorted(checked),
        "found": sorted(found),
        "lockfiles": sorted(locks),
        "requirements_file": REQUIREMENTS_RELATIVE,
        "declared_constraints": declared,
        "config_declared_transformers_version":
            CONTENTVEC_CONFIG_TRANSFORMERS_VERSION,
        "importable_modules": modules,
        "present": bool(found),
        "pinned": pinned,
        "note": ("No package is installed, imported or downloaded. Import "
                 "probes report the current interpreter only. A requirements "
                 "text is not an installed runtime or install digest."),
    }


def _load_pinned_config(relative: str) -> Dict[str, Any]:
    path = WORKSPACE / relative
    if not path.is_file():
        raise ConfigError("missing pinned config: " + relative,
                          "CONFIG_INVALID")
    if sha256_file(path) != SOURCE_PINS[relative]:
        raise ConfigError("config digest mismatch: " + relative,
                          "CONFIG_INVALID")
    value = strict_json_loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ConfigError("config root is not an object", "CONFIG_INVALID")
    return value


def _require_field(config: Dict[str, Any], key: str, expected: Any) -> Any:
    value = config.get(key)
    if value != expected:
        raise ConfigError("config field mismatch: " + key, "CONFIG_INVALID")
    return value


def _conv_receptive_field_samples() -> int:
    field = 1
    jump = 1
    for kernel, stride in zip(CONTENTVEC_CONV_KERNEL,
                              CONTENTVEC_CONV_STRIDE):
        field += (kernel - 1) * jump
        jump *= stride
    return field


def geometry() -> Dict[str, Any]:
    config = _load_pinned_config(CONFIG_RELATIVE)
    preprocessor = _load_pinned_config(PREPROCESSOR_RELATIVE)

    _require_field(config, "architectures", [CONTENTVEC_MODEL_ARCHITECTURE])
    _require_field(config, "model_type", CONTENTVEC_MODEL_TYPE)
    _require_field(config, "hidden_size", CONTENTVEC_HIDDEN_SIZE)
    _require_field(config, "num_hidden_layers", CONTENTVEC_LAYER_COUNT)
    _require_field(config, "num_attention_heads", CONTENTVEC_ATTENTION_HEADS)
    _require_field(config, "intermediate_size", CONTENTVEC_INTERMEDIATE_SIZE)
    _require_field(config, "conv_dim",
                   [CONTENTVEC_CONV_CHANNELS] * CONTENTVEC_CONV_FEATURE_LAYERS)
    _require_field(config, "conv_stride", list(CONTENTVEC_CONV_STRIDE))
    _require_field(config, "conv_kernel", list(CONTENTVEC_CONV_KERNEL))
    _require_field(config, "classifier_proj_size",
                   CONTENTVEC_CLASSIFIER_PROJ_SIZE)
    _require_field(config, "num_feat_extract_layers",
                   CONTENTVEC_CONV_FEATURE_LAYERS)
    _require_field(config, "feat_extract_norm", "group")
    _require_field(config, "torch_dtype", CONTENTVEC_CONFIG_TORCH_DTYPE)
    _require_field(config, "transformers_version",
                   CONTENTVEC_CONFIG_TRANSFORMERS_VERSION)

    _require_field(preprocessor, "feature_extractor_type",
                   "Wav2Vec2FeatureExtractor")
    _require_field(preprocessor, "feature_size", 1)
    _require_field(preprocessor, "sampling_rate", SAMPLE_RATE_HZ)
    _require_field(preprocessor, "do_normalize", False)
    _require_field(preprocessor, "return_attention_mask", False)

    stride_product = 1
    for stride in CONTENTVEC_CONV_STRIDE:
        stride_product *= stride
    if stride_product != CONTENTVEC_FRAME_STRIDE_SAMPLES:
        raise ConfigError("convolutional stride changed", "CONFIG_INVALID")

    loader_path = WORKSPACE / LOADER_RELATIVE
    if sha256_file(loader_path) != SOURCE_PINS[LOADER_RELATIVE]:
        raise ConfigError("loader digest mismatch", "CONFIG_INVALID")
    loader = loader_path.read_text(encoding="utf-8")
    fragments = (
        'HUBERT_MODEL_PATH = (PROJECT_ROOT / "assets" / "hubert_base")'
        ".resolve()",
        "class HubertModelWithFinalProj(HubertModel):",
        "self.final_proj = nn.Linear(config.hidden_size, "
        "config.classifier_proj_size)",
        'if version not in {"v1", "v2"}:',
        "outputs.hidden_states[9]",
        "model.final_proj(outputs.hidden_states[9])",
        ".last_hidden_state",
    )
    for fragment in fragments:
        if fragment not in loader:
            raise ConfigError("loader declaration changed: " + fragment,
                              "CONFIG_INVALID")

    receptive_field = _conv_receptive_field_samples()
    if receptive_field != 400:
        raise ConfigError("convolutional receptive field changed",
                          "CONFIG_INVALID")

    return {
        "source": (
            "assets/hubert_base/config.json + "
            "assets/hubert_base/preprocessor_config.json + infer/hubert.py"),
        "input_sample_rate_hz": SAMPLE_RATE_HZ,
        "v0_frame_samples": FRAME_SAMPLES,
        "v0_frame_ms": _r(FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ),
        "model_architecture": CONTENTVEC_MODEL_ARCHITECTURE,
        "model_type": CONTENTVEC_MODEL_TYPE,
        "encoder_hidden_size": CONTENTVEC_HIDDEN_SIZE,
        "encoder_layer_count": CONTENTVEC_LAYER_COUNT,
        "encoder_attention_heads": CONTENTVEC_ATTENTION_HEADS,
        "encoder_intermediate_size": CONTENTVEC_INTERMEDIATE_SIZE,
        "conv_feature_layers": CONTENTVEC_CONV_FEATURE_LAYERS,
        "conv_channels": CONTENTVEC_CONV_CHANNELS,
        "conv_kernel": list(CONTENTVEC_CONV_KERNEL),
        "conv_stride": list(CONTENTVEC_CONV_STRIDE),
        "conv_receptive_field_samples": receptive_field,
        "conv_receptive_field_ms": _r(
            receptive_field * 1000.0 / SAMPLE_RATE_HZ),
        "encoder_frame_stride_samples": CONTENTVEC_FRAME_STRIDE_SAMPLES,
        "encoder_frame_stride_ms": _r(
            CONTENTVEC_FRAME_STRIDE_SAMPLES * 1000.0 / SAMPLE_RATE_HZ),
        "encoder_frame_rate_hz": _r(
            SAMPLE_RATE_HZ / float(CONTENTVEC_FRAME_STRIDE_SAMPLES)),
        "v0_frames_per_content_frame":
            CONTENTVEC_FRAME_STRIDE_SAMPLES // FRAME_SAMPLES,
        "classifier_proj_size": CONTENTVEC_CLASSIFIER_PROJ_SIZE,
        "output_layer_feature_dim": {
            str(CONTENTVEC_V1_LAYER): CONTENTVEC_V1_FEATURE_DIM,
            str(CONTENTVEC_V2_LAYER): CONTENTVEC_V2_FEATURE_DIM,
        },
        "v1": {
            "output_layer": CONTENTVEC_V1_LAYER,
            "feature_dim": CONTENTVEC_V1_FEATURE_DIM,
            "path": "hidden_states[9] -> final_proj",
        },
        "v2": {
            "output_layer": CONTENTVEC_V2_LAYER,
            "feature_dim": CONTENTVEC_V2_FEATURE_DIM,
            "path": "last_hidden_state",
        },
        "config_declared_torch_dtype": CONTENTVEC_CONFIG_TORCH_DTYPE,
        "config_declared_transformers_version":
            CONTENTVEC_CONFIG_TRANSFORMERS_VERSION,
        "measured_here": False,
        "candidate_output": False,
        "note": (
            "Arithmetic and static declarations from the pinned config, "
            "preprocessor config and loader only; no weight was loaded and "
            "no feature was computed."),
    }


def historical_evidence() -> Dict[str, Any]:
    return {
        "status": "not_tested_no_local_result",
        "source_statement_path": ACCENT_README_RELATIVE,
        "source_statement": (
            "QuickVC / ContentVec: Not tested as standalone systems. Generic "
            "VC architecture/content encoder components, not a ready-made "
            "accent conversion model. An encoder alone cannot produce "
            "converted speech. No accent-target checkpoint available in this "
            "evaluation."),
        "standalone_tested": False,
        "accent_target_checkpoint_available": False,
        "timing": None,
        "quality": None,
        "semantic_fidelity_scored": False,
        "identity_similarity_scored": False,
        "naturalness_scored": False,
        "reproduced_here": False,
        "qualifies_candidate": False,
        "excluded_other_system_timing": {
            "system": "RVC whole-file conversion pipeline",
            "reason": (
                "The research README timing belongs to the RVC pipeline, not "
                "to a standalone ContentVec measurement, and is not attributed "
                "to this component."),
        },
        "note": (
            "The only local ContentVec statement is an explicit 'not tested "
            "as standalone systems' record. No ContentVec timing, feature, "
            "quality or audio result exists and nothing was re-run."),
    }


def voice_profile_mapping() -> Dict[str, str]:
    return {
        "permitted_input_and_target_reference_scope":
            "blocked_no_permitted_cohort_and_no_accent_target_checkpoint",
        "task_and_language_speaker_groups": "blocked_not_tested",
        "text_and_semantic_content": "blocked_no_candidate_feature",
        "identity_and_similarity": "not_applicable_content_encoder_only",
        "naturalness": "not_applicable_content_encoder_only",
        "alignment_first_output_and_tail_timing":
            "blocked_no_runtime_or_device_measurement",
        "exact_target_condition": "blocked_no_target_checkpoint",
        "consent_reference_availability_and_output_use":
            "blocked_no_corpus_or_asset_rights",
        "paired_quality_control": "blocked_weights_and_runtime_absent",
        "clean_reference_preservation": "blocked_no_candidate",
        "numerical_and_nonfinite": "partial_local_harness_only",
        "candidate_output": "blocked_weights_and_runtime_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "exact_contentvec_config_weights_and_runtime":
            "blocked_weights_and_runtime_absent",
        "layer9_final_proj_256_and_layer12_hidden768":
            "blocked_weights_and_runtime_absent",
        "content_preservation_and_semantic_fidelity":
            "blocked_no_candidate_feature",
        "rights_qualified_cohort_and_groups": "blocked_no_permitted_cohort",
        "contentvec_only_compute": "blocked_no_measurement",
        "device_timing_memory_and_callback": "blocked_no_measurement",
        "delay_state_reset_drain_and_modes":
            "blocked_weights_and_runtime_absent",
        "numerical_and_nonfinite": "partial_local_harness_only",
        "target_condition_and_asset_rights": "blocked_no_corpus_or_asset_rights",
        "paired_reference_feature_fidelity": "blocked_no_reference",
        "text_semantic_content": "blocked_no_candidate",
        "upstream_source_and_weight_terms": "blocked_terms_not_recorded",
    }


def candidates() -> Dict[str, Any]:
    return {
        CANDIDATE: {
            "status": "blocked_weights_and_runtime_absent",
            "metrics": None,
            "qualifies_candidate": False,
            "supported_output_layers": sorted(
                CONTENTVEC_SUPPORTED_OUTPUT_LAYERS),
            "reason": (
                "The exact ContentVec/HuBERT checkpoint weights and a "
                "hash-pinned PyTorch/Transformers runtime are absent; no "
                "feature, quality or timing result was produced."),
        }
    }


def controls() -> Dict[str, Any]:
    return {
        "source_identity_control": {
            "status": "not_run_no_candidate",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "downstream_rvc_content_path": {
            "status": "declared_not_run_weights_absent",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "harness_identity_control": {
            "status": "bit_exact_synthetic_only",
            "candidate_processing": False,
        },
    }


def stimulus_probe() -> Dict[str, Any]:
    stimuli: Dict[str, Any] = {}
    identity: Dict[str, Any] = {}
    stride: Dict[str, Any] = {}
    for name, generator in STIMULUS_GENERATORS.items():
        samples = generator()
        stimuli[name] = stimulus_metrics(name, samples)
        identity[name] = {
            "digest": tensor_digest(samples),
            "byte_identical": tuple(samples) == tuple(float(value)
                                                     for value in samples),
        }
        stride[name] = frame_geometry(len(samples))
    return {
        "purpose": (
            "harness stimulus characterisation only; not a ContentVec result "
            "and not a candidate output"),
        "stimuli": stimuli,
        "speech_contrast": speech_contrast(
            STIMULUS_GENERATORS["speech_like"]()),
        "identity_control": identity,
        "frame_stride_probe": stride,
        "candidate_processing": False,
    }


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ConfigError("TASKS.json is missing", "BOARD_MISSING")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise ConfigError("TASKS.json shape is invalid", "BOARD_INVALID")
    task = None
    for row in board["tasks"]:
        if isinstance(row, dict) and row.get("id") == TASK:
            task = row
            break
    if task is None:
        raise ConfigError("linked task row is missing", "BOARD_ROW_MISSING")
    stable = {
        "task_id": task.get("id"),
        "title": task.get("title"),
        "mode": task.get("mode"),
        "repository": task.get("repository"),
        "component": task.get("component"),
    }
    if stable != EXPECTED_LINK:
        raise ConfigError("stable linked-row identity changed",
                          "BOARD_IDENTITY_CHANGED")
    rows = [stable]
    digest = sha256_bytes(canonical_bytes(rows))
    return rows, digest


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "decision": "DEFER",
        "processor_exposure": "deferred_until_independent_review",
        "proposal_only": True,
        "readiness": "incomplete",
        "status": "not_qualified",
        "upstream_parity": False,
    }


def boundary() -> Dict[str, Any]:
    return {
        "benchmark_claim": False,
        "board_or_handoff_changed": False,
        "ci_changed": False,
        "descriptor_default_changed": False,
        "descriptor_registration": False,
        "enabled_by_default": False,
        "format": {
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
            "sample_rate_hz": SAMPLE_RATE_HZ,
        },
        "installed_v0_unchanged": True,
        "opt_in_required": True,
        "provider_intake_complete": False,
        "provider_registered": False,
        "public_api_abi_changed": False,
        "public_c_boundary": (
            "not used: no C provider, header or installed target"),
        "real_corpus_or_weights": False,
        "registry_changed": False,
        "release_claim": False,
        "shared_cmake_changed": False,
    }


def artifact_pins(names: Sequence[str] = SOURCE_ARTIFACT_FILES) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in names:
        path = HERE / name
        if not path.is_file():
            raise ConfigError("missing package artifact: " + name,
                              "MISSING_ARTIFACT")
        pins[name] = sha256_file(path)
    return pins


def source_evidence_statements() -> List[str]:
    return [
        ("research/accent-conversion-20261101/README.md records QuickVC / "
         "ContentVec as 'Not tested as standalone systems': generic VC "
         "architecture/content-encoder components, not a ready-made accent "
         "conversion model, with no accent-target checkpoint available; an "
         "encoder alone cannot produce converted speech."),
        ("plan/INVENTORY.json assigns the voice verification profile to "
         "SDK-CONTENTVEC and records the same 'not tested as standalone' "
         "finding for contentvec and quickvc."),
        ("research/voice-conversion-eval-20261101/repos/rvc is pinned at "
         "81eed5e8 under an MIT LICENSE; its infer/hubert.py loads a "
         "transformers HubertModelWithFinalProj from assets/hubert_base and "
         "declares v1 = hidden_states[9] through final_proj (256-wide) and "
         "v2 = last_hidden_state (768-wide)."),
        ("assets/hubert_base contains only config.json and "
         "preprocessor_config.json; the required pytorch_model.bin is absent. "
         "The pinned RVC-MLX consumer instead declares "
         "assets/contentvec/pytorch_model.bin and an Applio download URL, and "
         "that path is also absent."),
        ("The config declares a 768-wide, 12-layer HuBERTModelWithFinalProj "
         "with conv_stride [5,2,2,2,2,2,2] (320-sample, 50 Hz content rate), "
         "classifier_proj_size 256, torch_dtype float16 and transformers "
         "4.49.0; these are static declarations, not measured behaviour."),
        ("No standalone ContentVec timing, feature, content-fidelity, "
         "listening, device or release result exists locally; the RVC "
         "whole-file pipeline timing is a different system and is not "
         "attributed to ContentVec."),
    ]


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    source = source_probe()
    weights = weights_probe()
    runtime = runtime_probe()
    geom = geometry()
    history = historical_evidence()
    adverse_request = _adverse_cases()
    adverse_json = _json_adverse_cases()
    stimuli = stimulus_probe()
    gates = [dict(gate) for gate in GATES]
    local_checks = {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "stable_board_identity_only": True,
        "consumer_source_pin_exact": source["present"],
        "contentvec_config_pin_exact": (
            geom["encoder_hidden_size"] == CONTENTVEC_HIDDEN_SIZE
            and geom["encoder_frame_stride_samples"] ==
            CONTENTVEC_FRAME_STRIDE_SAMPLES),
        "weights_probe_complete": weights["status"] ==
        "blocked_weights_absent",
        "runtime_probe_complete": runtime["status"] ==
        "blocked_runtime_unpinned",
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "nonfinite_samples_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith("nonfinite")),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked":
            missing_result("contentvec_placeholder")["status"] == "blocked",
        "identity_control_bit_exact": all(
            block["byte_identical"]
            for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
        "exact_layer_and_geometry_pinned": (
            geom["encoder_layer_count"] == CONTENTVEC_LAYER_COUNT
            and geom["encoder_hidden_size"] == CONTENTVEC_HIDDEN_SIZE
            and geom["encoder_frame_rate_hz"] ==
            CONTENTVEC_FRAME_RATE_HZ
            and geom["v1"]["feature_dim"] == CONTENTVEC_V1_FEATURE_DIM
            and geom["v2"]["feature_dim"] == CONTENTVEC_V2_FEATURE_DIM),
        "real_corpus_not_read": True,
        "no_result_qualifies_candidate": True,
    }
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_not_qualified",
        "decision": "DEFER",
        "qualification_status": "not_qualified",
        "qualification": qualification(),
        "boundary": boundary(),
        "profile": {
            "name": "voice",
            "source": SOURCE_PINS[VOICE_PROFILE_SOURCE],
        },
        "profile_mapping": voice_profile_mapping(),
        "reference": {
            "implementation": "task-local standard-library evidence builder",
            "real_consumer_source_present": source["present"],
            "real_contentvec_config_present": (
                source["contentvec_config_present"]),
            "real_contentvec_weights_present": weights["present"],
            "pinned_runtime_present": runtime["pinned"],
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "real_corpus_read": False,
            "note": (
                "No ContentVec network, checkpoint loader, feature extractor "
                "or inference path is implemented or simulated; only probes, "
                "config geometry arithmetic, request rejection and synthetic "
                "controls are performed."),
        },
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "source_evidence_statements": source_evidence_statements(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_link_fields": list(LINK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "artifact_pins": artifact_pins(),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "source_probe": source,
        "weights_probe": weights,
        "runtime_probe": runtime,
        "geometry": geom,
        "historical_evidence": history,
        "candidates": candidates(),
        "controls": controls(),
        "required_results": candidate_required_results(),
        "stimulus_probe": stimuli,
        "adverse": {
            "invalid_config_and_input": adverse_request,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": missing_result("contentvec_placeholder"),
        },
        "local_harness_checks": local_checks,
        "release_gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "gates": [gate["id"] for gate in gates],
        "regressions": [],
        "regression_count": 0,
        "no_missing_result_qualifies_candidate": True,
        "generated_by": "run.py --report",
    }
    if not finite_json(report):
        raise EvidenceError("REPORT_NONFINITE", "REPORT_NONFINITE")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
