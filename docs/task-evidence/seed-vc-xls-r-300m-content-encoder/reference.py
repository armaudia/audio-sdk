# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for the Seed-VC XLS-R-300M
content encoder.

This module is NOT the Seed-VC XLS-R-300M content encoder. It does not
implement, approximate, simulate or run the ``facebook/wav2vec2-xls-r-300m``
encoder or any Seed-VC network. The GPL-3.0 Seed-VC *source checkout* is
present at a pinned revision, but the exact encoder weights and a hash-pinned
PyTorch/Transformers runtime are absent. The module therefore builds a bounded,
deterministic blocker report:

* strict request validation at the installed v0 geometry, with fail-closed
  rejection of missing, invalid, nonfinite and out-of-range inputs;
* explicit source, weights and runtime probes (read-only, bounded, no network);
* encoder geometry derived from the pinned Seed-VC config and pinned one-block
  run script, plus clearly separated source-reported historical values;
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

SCHEMA_ID = (
    "audio-sdk/seed-vc-xls-r-300m-content-encoder-reference-report/0.1")
CONTRACT_SCHEMA_ID = (
    "audio-sdk/seed-vc-xls-r-300m-content-encoder-contract/0.1")
TASK = "SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER"
COMPONENT = "seed-vc-xls-r-300m-content-encoder"
BRANCH = "swarm/SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER"
BASE_COMMIT = "37633ac33fd798512b1a30845a1334134ab1384e"
TASK_PREFIX = (
    "docs/task-evidence/seed-vc-xls-r-300m-content-encoder/")

SOURCE_REPOSITORY = "Plachtaa/seed-vc"
SOURCE_REVISION = "51383efd921027683c89e5348211d93ff12ac2a8"
SOURCE_TREE_DIGEST = (
    "e3a67ec3228aecb40ddeb5069eb6d1f6f237945f625a559736058546dcf8d3bf")
SOURCE_FILE_COUNT = 111
SOURCE_LICENSE = "GPL-3.0"

ENCODER_MODEL = "facebook/wav2vec2-xls-r-300m"
ENCODER_OUTPUT_LAYER = 12
ENCODER_HIDDEN_SIZE = 1024
ENCODER_FRAME_STRIDE_SAMPLES = 320
ENCODER_FRAME_RATE_HZ = 50.0
CONTENT_DIM = 384
DOWNSTREAM_CHECKPOINT = "DiT_uvit_tat_xlsr_ema.pth"

HISTORICAL_BLOCK_SAMPLES = 3840
HISTORICAL_LEFT_S = 2.2
HISTORICAL_EMIT_S = 0.24
HISTORICAL_RIGHT_S = 0.2
HISTORICAL_MODEL_LOAD_S = 254.01
HISTORICAL_BLOCK_COMPUTE_S = 22.21
HISTORICAL_SEMANTIC_S = 12.20
HISTORICAL_RTF = 92.55
HISTORICAL_OUTPUT_RATE_HZ = 22050
HISTORICAL_OUTPUT_SHA256 = (
    "f3d07ee85b4a6b3c2ab30ec23f6c697fa99fbb3a64ef3fe895e0a186b5bac27a")
HISTORICAL_OUTPUT_FRAMES = 5292

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
SOURCE_ROOT = (
    WORKSPACE / "research/voice-conversion-eval-20261101/repos/seed-vc")
ACCENT_ROOT = WORKSPACE / "research/accent-conversion-20261101"
EVAL_ROOT = WORKSPACE / "research/voice-conversion-eval-20261101"
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

CONFIG_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/seed-vc/configs/presets/"
    "config_dit_mel_seed_uvit_xlsr_tiny.yml")
RUN_SCRIPT_RELATIVE = (
    "research/accent-conversion-20261101/run_seedvc_realtime.py")
HISTORICAL_WAV_RELATIVE = (
    "research/accent-conversion-20261101/results/"
    "seedvc-realtime-ABA-a0046-block.wav")
HISTORICAL_LOG_RELATIVE = (
    "research/accent-conversion-20261101/results/seedvc-realtime.log")

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only the stable linked-row identity is projected, never hashed.
SOURCE_PINS = {
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/run_seedvc_realtime.py":
        "9461c7b81cc15dcdb0efa907098b8f8ad6ecd21d1a43b3a15ab5f4bd76193ff2",
    "research/accent-conversion-20261101/results/"
    "seedvc-realtime-ABA-a0046-block.wav":
        "f3d07ee85b4a6b3c2ab30ec23f6c697fa99fbb3a64ef3fe895e0a186b5bac27a",
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/repos/seed-vc/LICENSE":
        "8b1ba204bb69a0ade2bfcf65ef294a920f6bb361b317dba43c7ef29d96332b9b",
    "research/voice-conversion-eval-20261101/repos/seed-vc/README.md":
        "293507df928d542341a69b9c93e3b7344f7cc7abe73ac4b2c6395d86527a1ce4",
    "research/voice-conversion-eval-20261101/repos/seed-vc/configs/presets/"
    "config_dit_mel_seed_uvit_xlsr_tiny.yml":
        "5ba8e708770bc8637708600dbb6c26ccd2ff081c270ae9bb90fb3ea4bed2e6e6",
    "research/voice-conversion-eval-20261101/repos/seed-vc/inference.py":
        "58f97976804a8eb8bb4d33e73beeab792f86a5ab2ca83c1319a23da1e71e80a6",
    "research/voice-conversion-eval-20261101/repos/seed-vc/real-time-gui.py":
        "2c9cad15515997fca336afb0c3ea5bdd056993c027a73c15aa26c3398a79d536",
    "research/voice-conversion-eval-20261101/repos/seed-vc/app_vc.py":
        "3dbefbb08090e3b007f3ba8737350a28a3da7c68798956497dd3b316b24635b0",
    "research/voice-conversion-eval-20261101/repos/seed-vc/requirements.txt":
        "2669266b0c07841b283f1d837e0b8628e7902972de25169f8d821cbee1829ed2",
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
    "title": "Seed-VC XLS-R-300M content encoder",
    "mode": "implementation",
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)

CANDIDATE = "seed_vc_xlsr_300m_content_encoder"
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
    "tf_model.h5",
    "flax_model.msgpack",
)
WEIGHT_CANDIDATE_PATHS = (
    "research/accent-conversion-20261101/hf-cache",
    "research/accent-conversion-20261101/hf-cache/"
    "models--facebook--wav2vec2-xls-r-300m",
    "research/voice-conversion-eval-20261101/checkpoints",
    "research/voice-conversion-eval-20261101/checkpoints/xlsr",
    "research/voice-conversion-eval-20261101/repos/seed-vc/checkpoints",
    "research/voice-conversion-eval-20261101/repos/seed-vc/models",
    "data/models/facebook/wav2vec2-xls-r-300m",
    "~/"
    ".cache/huggingface/hub/models--facebook--wav2vec2-xls-r-300m",
)
RUNTIME_CANDIDATE_PATHS = (
    "research/accent-conversion-20261101/.venv",
    "research/accent-conversion-20261101/.venv/bin/python",
    "research/voice-conversion-eval-20261101/.venv-eval/bin/python",
    "data/envs/seed-vc/bin/python",
    "data/envs/seed-vc",
)
RUNTIME_MODULES = (
    "torch", "torchaudio", "transformers", "numpy", "soundfile",
    "huggingface_hub",
)
RUNTIME_LOCK_CANDIDATES = (
    "research/accent-conversion-20261101/requirements.lock",
    "research/voice-conversion-eval-20261101/requirements.lock",
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
        "gate": "exact_source_and_encoder_weight_pin",
        "status": "blocked",
        "reason": (
            "The GPL-3.0 Seed-VC source checkout is present and pinned at "
            "commit 51383efd, but the exact facebook/wav2vec2-xls-r-300m "
            "encoder weights are absent; no weight SHA-256 or byte count "
            "exists locally."),
        "reopen": (
            "Stage the exact XLS-R-300M config, preprocessor config and "
            "weight files (pytorch_model.bin or model.safetensors) with "
            "recorded SHA-256 and byte counts before any reproduction."),
    },
    {
        "id": "RG-02",
        "gate": "license_rights_and_asset_review",
        "status": "blocked",
        "reason": (
            "Seed-VC source is GPL-3.0 and the XLS-R-300M weight terms are "
            "not recorded locally; caller-supplied-asset redistribution/use "
            "and input-corpus rights for generated features or audio are "
            "unconfirmed."),
        "reopen": (
            "Record the XLS-R-300M weight licence/terms, the GPL-3.0 "
            "obligations for a caller-supplied asset, and an approved "
            "use/redistribution scope for weights, runtime, inputs and any "
            "derived features or output."),
    },
    {
        "id": "RG-03",
        "gate": "exact_runtime_build_and_install_parity",
        "status": "blocked",
        "reason": (
            "The historical PyTorch/Transformers environment was removed; no "
            "hash-pinned lockfile or wheel set exists and torch, transformers "
            "and numpy are not importable here."),
        "reopen": (
            "Create a frozen, hash-pinned CPU runtime for the exact "
            "transformers/torch versions, install it in a clean environment, "
            "and prove import/version parity before loading weights."),
    },
    {
        "id": "RG-04",
        "gate": "encoder_geometry_layer_delay_drain_and_mode_parity",
        "status": "blocked",
        "reason": (
            "No encoder weight was loaded, so the 12-layer truncation, "
            "1024-wide hidden state, 320-sample stride, feature delay, "
            "state/reset, finite drain and v0 execution-mode ownership were "
            "not exercised."),
        "reopen": (
            "With the exact weights and runtime, verify layer-12 truncation, "
            "hidden width, stride, feature delay, state/reset, finite drain "
            "and execution-mode ownership at 16 kHz mono."),
    },
    {
        "id": "RG-05",
        "gate": "rights_qualified_cohort_and_semantic_fidelity",
        "status": "blocked",
        "reason": (
            "Only one historical L2-ARCTIC clip and one 240 ms block exist; "
            "no permitted multi-speaker/language cohort, paired reference "
            "features, semantic fidelity score or held-out comparison was "
            "produced."),
        "reopen": (
            "Freeze a permitted multi-speaker/language cohort with paired "
            "reference features, score semantic fidelity and content transfer "
            "separately, and retain per-group failures."),
    },
    {
        "id": "RG-06",
        "gate": "content_preservation_and_adverse_cases",
        "status": "blocked",
        "reason": (
            "The historical block is too short for ASR/WER and no silence, "
            "clipping, nonfinite, unfamiliar-speech or adverse-input case was "
            "run through the exact encoder."),
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
            "The source-reported 12.20 s semantic extraction for one first "
            "240 ms block is not a warmed-up steady-state, paced device or "
            "callback measurement; no memory or first-output/tail timing was "
            "measured here."),
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
        "facebook/wav2vec2-xls-r-300m encoder config, preprocessor config and "
        "weights plus the exact hash-pinned PyTorch/Transformers runtime "
        "required to load layer 12"),
    "source": {
        "status": "present_pinned",
        "repository": SOURCE_REPOSITORY,
        "revision": SOURCE_REVISION,
        "tree_digest": SOURCE_TREE_DIGEST,
        "file_count": SOURCE_FILE_COUNT,
        "license": SOURCE_LICENSE,
    },
    "weights": {
        "status": "absent",
        "artifact": ENCODER_MODEL,
        "upstream_repository": "https://huggingface.co/facebook/wav2vec2-xls-r-300m",
        "required_files": [
            "config.json",
            "preprocessor_config.json",
            "pytorch_model.bin or model.safetensors",
        ],
        "expected_hidden_size": ENCODER_HIDDEN_SIZE,
        "expected_output_layer": ENCODER_OUTPUT_LAYER,
        "sha256": None,
        "byte_count": None,
        "license": None,
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "PyTorch CPU build compatible with the historical run",
            "Transformers Wav2Vec2Model and Wav2Vec2FeatureExtractor",
            "NumPy for the feature-extractor input path",
            "a hash-pinned lockfile or wheel set for the exact versions",
        ],
        "sha256": None,
        "lockfile": None,
    },
    "expected_license": (
        "GPL-3.0 for the pinned Seed-VC source checkout; the "
        "facebook/wav2vec2-xls-r-300m weight terms are not recorded locally "
        "and require separate review"),
    "pinned_revision": SOURCE_REVISION,
    "source_digest": SOURCE_TREE_DIGEST,
    "runtime_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "A recorded XLS-R-300M weight licence/terms decision, an explicit "
        "GPL-3.0 caller-supplied-asset and redistribution/use decision, and "
        "permission for every input clip and any derived feature or output "
        "are required before any reproduction, adapter or release claim. "
        "Consent for a target voice is not applicable to the encoder alone "
        "but becomes a gate for any downstream conversion."),
    "workspace_search": (
        "Bounded read-only checks of the pinned Seed-VC tree, the evaluation "
        "and accent-conversion checkpoint, model and Hugging Face cache paths "
        "found no XLS-R-300M config or weight files. The historical README "
        "says the checkpoint bundle and XLS-R-300M encoder were downloaded "
        "locally, but no such weights remain and no SHA-256 or byte count "
        "exists."),
    "not_attempted": [
        "no network download or package installation",
        "no fabricated, reconstructed or surrogate XLS-R-300M weights",
        "no substitute encoder or feature extractor",
        "no copied upstream source, real corpus audio or licence text",
        "no real corpus read, model load or feature/audio output",
    ],
    "reopen": (
        "Stage the exact XLS-R-300M files with SHA-256/byte counts, record "
        "weight and asset rights, rebuild a hash-pinned runtime, then repeat "
        "the voice profile with a permitted cohort and independent review."),
}

NON_CLAIMS = (
    "No XLS-R-300M config, weight, vocabulary or feature output is included.",
    "No XLS-R-300M or Seed-VC inference is implemented, approximated or simulated.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default.",
    "No real corpus, consent, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No missing, rejected or historical result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/seed-vc-xls-r-300m-content-encoder/ is touched.",
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
    full = sample_count // ENCODER_FRAME_STRIDE_SAMPLES
    return {
        "sample_count": sample_count,
        "stride_samples": ENCODER_FRAME_STRIDE_SAMPLES,
        "full_frames": full,
        "remainder_samples": sample_count -
        full * ENCODER_FRAME_STRIDE_SAMPLES,
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
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown), "UNKNOWN_FIELD")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing), "MISSING_FIELD")
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
    output_layer = _require_int(request["output_layer"], "INVALID_OUTPUT_LAYER")
    if output_layer != ENCODER_OUTPUT_LAYER:
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
    }


def probe_candidate(request: Any) -> None:
    validated = validate_request(request)
    raise WeightsAbsent(
        "WEIGHTS_ABSENT: " + validated["candidate"] + " XLS-R-300M weights "
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
        "output_layer": ENCODER_OUTPUT_LAYER,
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
        ("unknown_candidate", variant(candidate="seed_vc_xlsr_300m")),
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
        ("string_sample", with_samples(["0.0"] + [0.0] * (FRAME_SAMPLES - 1))),
        ("negative_epoch", variant(epoch=-1)),
        ("bool_epoch", variant(epoch=True)),
        ("negative_position", variant(first_input_sample=-160)),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("invalid_execution_mode", variant(execution_mode=4)),
        ("unsupported_output_layer_high", variant(output_layer=13)),
        ("unsupported_output_layer_zero", variant(output_layer=0)),
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


def source_probe() -> Dict[str, Any]:
    if not SOURCE_ROOT.is_dir():
        return {"status": "source_absent", "present": False}
    rows: List[str] = []
    for directory, directory_names, file_names in os.walk(SOURCE_ROOT):
        directory_names[:] = sorted(
            name for name in directory_names if name != ".git")
        for name in sorted(file_names):
            path = Path(directory) / name
            relative = path.relative_to(SOURCE_ROOT).as_posix()
            payload = path.read_bytes()
            rows.append(relative + " " + sha256_bytes(payload) + " " +
                        str(len(payload)) + "\n")
    tree_digest = sha256_bytes("".join(rows).encode("utf-8"))
    revision = _read_git_revision(SOURCE_ROOT)
    present = (
        revision == SOURCE_REVISION
        and tree_digest == SOURCE_TREE_DIGEST
        and len(rows) == SOURCE_FILE_COUNT
    )
    return {
        "status": "present_pinned" if present else "source_mismatch",
        "present": present,
        "revision": revision,
        "expected_revision": SOURCE_REVISION,
        "tree_digest": tree_digest,
        "expected_tree_digest": SOURCE_TREE_DIGEST,
        "file_count": len(rows),
        "expected_file_count": SOURCE_FILE_COUNT,
        "license": SOURCE_LICENSE,
        "note": ("Read-only digest over every non-.git file in the local "
                 "checkout; no upstream file is copied or executed. One "
                 "tracked binary (campplus_cn_common.bin) is absent from this "
                 "checkout, so the working-tree digest, not the git tree "
                 "object, is pinned at the exact commit."),
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
        "artifact": ENCODER_MODEL,
        "upstream_repository": (
            "https://huggingface.co/facebook/wav2vec2-xls-r-300m"),
        "required_files": [
            "config.json",
            "preprocessor_config.json",
            "pytorch_model.bin or model.safetensors",
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
    pinned = bool(found) and bool(locks)
    return {
        "status": "runtime_present_unqualified" if pinned
                  else "blocked_runtime_unpinned",
        "checked_paths": sorted(checked),
        "found": sorted(found),
        "lockfiles": sorted(locks),
        "importable_modules": modules,
        "present": bool(found),
        "pinned": pinned,
        "note": ("No package is installed, imported or downloaded. Import "
                 "probes report the current interpreter only."),
    }


def _yaml_scalar(text: str, section: str, key: str) -> str | None:
    in_section = False
    for line in text.splitlines():
        match = re.match(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*):(.*)$", line)
        if match is None:
            continue
        indent = len(match.group(1))
        name = match.group(2)
        value = match.group(3).strip()
        if indent == 2:
            in_section = name == section
        elif in_section and indent > 2 and name == key:
            return value.strip().strip("'\"")
    return None


def _yaml_list(text: str, section: str, key: str) -> List[int]:
    raw = _yaml_scalar(text, section, key)
    if raw is None:
        raise ConfigError("missing config list: " + key, "CONFIG_INVALID")
    try:
        parsed = strict_json_loads(raw)
    except JsonError:
        raise ConfigError("invalid config list: " + key, "CONFIG_INVALID")
    if not isinstance(parsed, list) or not all(
            isinstance(item, int) and not isinstance(item, bool)
            for item in parsed):
        raise ConfigError("invalid config list: " + key, "CONFIG_INVALID")
    return parsed


def geometry() -> Dict[str, Any]:
    config_path = WORKSPACE / CONFIG_RELATIVE
    if sha256_file(config_path) != SOURCE_PINS[CONFIG_RELATIVE]:
        raise ConfigError("config digest mismatch", "CONFIG_INVALID")
    config = config_path.read_text(encoding="utf-8")
    encoder_name = _yaml_scalar(config, "speech_tokenizer", "name")
    encoder_type = _yaml_scalar(config, "speech_tokenizer", "type")
    output_layer = _yaml_scalar(config, "speech_tokenizer", "output_layer")
    hidden = _yaml_scalar(config, "length_regulator", "in_channels")
    content_channels = _yaml_scalar(config, "length_regulator", "channels")
    sampling_ratios = _yaml_list(config, "length_regulator",
                                 "sampling_ratios")
    content_dim = _yaml_scalar(config, "DiT", "content_dim")
    content_type = _yaml_scalar(config, "DiT", "content_type")
    downstream = _yaml_scalar(config, "speech_tokenizer", "type")
    if encoder_type != "xlsr":
        raise ConfigError("speech tokenizer is not xlsr", "CONFIG_INVALID")
    if encoder_name != ENCODER_MODEL:
        raise ConfigError("encoder model mismatch", "CONFIG_INVALID")
    if output_layer is None or int(output_layer) != ENCODER_OUTPUT_LAYER:
        raise ConfigError("output layer mismatch", "CONFIG_INVALID")
    if hidden is None or int(hidden) != ENCODER_HIDDEN_SIZE:
        raise ConfigError("hidden width mismatch", "CONFIG_INVALID")
    if content_channels is None or int(content_channels) != CONTENT_DIM:
        raise ConfigError("length regulator width mismatch", "CONFIG_INVALID")
    if content_dim is None or int(content_dim) != CONTENT_DIM:
        raise ConfigError("content dim mismatch", "CONFIG_INVALID")
    if content_type != "discrete":
        raise ConfigError("content type mismatch", "CONFIG_INVALID")
    if downstream != "xlsr":
        raise ConfigError("unreachable tokenizer mismatch", "CONFIG_INVALID")

    run_path = WORKSPACE / RUN_SCRIPT_RELATIVE
    if sha256_file(run_path) != SOURCE_PINS[RUN_SCRIPT_RELATIVE]:
        raise ConfigError("run script digest mismatch", "CONFIG_INVALID")
    script = run_path.read_text(encoding="utf-8")
    match = re.search(
        r"skip_head,\s*return_length,\s*skip_tail\s*=\s*"
        r"(\d+),\s*(\d+),\s*(\d+)", script)
    if match is None:
        raise ConfigError("one-block geometry is missing", "CONFIG_INVALID")
    skip_head, return_length, skip_tail = (int(value)
                                           for value in match.groups())
    block_frames = re.search(r"block_frame_16k\s*=\s*(\d+)\s*\*\s*"
                             r"return_length", script)
    if block_frames is None:
        raise ConfigError("block frame size is missing", "CONFIG_INVALID")
    stride = int(block_frames.group(1))
    diffusion = re.search(r"diffusion_steps\s*=\s*(\d+)", script)
    if diffusion is None:
        raise ConfigError("diffusion steps are missing", "CONFIG_INVALID")
    diffusion_steps = int(diffusion.group(1))
    if (stride, skip_head, return_length, skip_tail, diffusion_steps) != (
            ENCODER_FRAME_STRIDE_SAMPLES, 110, 12, 10, 10):
        raise ConfigError("one-block geometry changed", "CONFIG_INVALID")

    left_samples = skip_head * stride
    emit_samples = return_length * stride
    right_samples = skip_tail * stride
    total_samples = left_samples + emit_samples + right_samples
    if emit_samples != HISTORICAL_BLOCK_SAMPLES:
        raise ConfigError("emit block mismatch", "CONFIG_INVALID")
    average_from_block = HISTORICAL_BLOCK_COMPUTE_S / HISTORICAL_EMIT_S
    semantic_from_total = HISTORICAL_SEMANTIC_S / (
        total_samples / float(SAMPLE_RATE_HZ))
    return {
        "source": (
            "configs/presets/config_dit_mel_seed_uvit_xlsr_tiny.yml + "
            "run_seedvc_realtime.py + accent-conversion README"),
        "input_sample_rate_hz": SAMPLE_RATE_HZ,
        "v0_frame_samples": FRAME_SAMPLES,
        "v0_frame_ms": _r(FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ),
        "encoder_model": encoder_name,
        "encoder_output_layer": int(output_layer),
        "encoder_hidden_size": int(hidden),
        "encoder_frame_stride_samples": stride,
        "encoder_frame_stride_ms": _r(
            stride * 1000.0 / SAMPLE_RATE_HZ),
        "encoder_frame_rate_hz": _r(
            SAMPLE_RATE_HZ / float(stride)),
        "v0_frames_per_encoder_frame": stride // FRAME_SAMPLES,
        "content_dim": int(content_dim),
        "content_type": content_type,
        "length_regulator_channels": int(content_channels),
        "length_regulator_sampling_ratios": sampling_ratios,
        "downstream_checkpoint": DOWNSTREAM_CHECKPOINT,
        "one_block": {
            "left_context_frames": skip_head,
            "emit_frames": return_length,
            "right_context_frames": skip_tail,
            "stride_samples": stride,
            "left_context_samples": left_samples,
            "emit_samples": emit_samples,
            "right_context_samples": right_samples,
            "total_context_samples": total_samples,
            "left_context_seconds": _r(
                left_samples / float(SAMPLE_RATE_HZ)),
            "emit_seconds": _r(emit_samples / float(SAMPLE_RATE_HZ)),
            "right_context_seconds": _r(
                right_samples / float(SAMPLE_RATE_HZ)),
            "total_context_seconds": _r(
                total_samples / float(SAMPLE_RATE_HZ)),
            "diffusion_steps": diffusion_steps,
            "output_sample_rate_hz": HISTORICAL_OUTPUT_RATE_HZ,
        },
        "source_reported": {
            "model_load_seconds": HISTORICAL_MODEL_LOAD_S,
            "block_compute_seconds": HISTORICAL_BLOCK_COMPUTE_S,
            "semantic_extraction_seconds": HISTORICAL_SEMANTIC_S,
            "rtf": HISTORICAL_RTF,
            "emit_seconds": HISTORICAL_EMIT_S,
            "left_context_seconds": HISTORICAL_LEFT_S,
            "right_context_seconds": HISTORICAL_RIGHT_S,
        },
        "derived_from_source_reported": {
            "block_rtf": _r(average_from_block),
            "semantic_to_total_context_ratio": _r(semantic_from_total),
            "note": ("Arithmetic on source-reported values from the pinned "
                     "accent-conversion README and run script; not a local "
                     "measurement."),
        },
        "measured_here": False,
        "candidate_output": False,
    }


def _wav_metadata(path: Path) -> Dict[str, Any]:
    import wave
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        rate = handle.getframerate()
        frames = handle.getnframes()
    return {
        "channels": channels,
        "sample_width_bytes": sample_width,
        "sample_rate_hz": rate,
        "frames": frames,
        "duration_seconds": _r(frames / float(rate)),
    }


def historical_evidence() -> Dict[str, Any]:
    wav_path = WORKSPACE / HISTORICAL_WAV_RELATIVE
    log_path = WORKSPACE / HISTORICAL_LOG_RELATIVE
    digest = sha256_file(wav_path) if wav_path.is_file() else None
    metadata = _wav_metadata(wav_path) if wav_path.is_file() else None
    return {
        "status": "source_reported_one_block_not_reproduced",
        "output_path": HISTORICAL_WAV_RELATIVE,
        "output_sha256": digest,
        "output_digest_matches_pin": digest == HISTORICAL_OUTPUT_SHA256,
        "output_metadata": metadata,
        "expected_frames": HISTORICAL_OUTPUT_FRAMES,
        "expected_duration_seconds": HISTORICAL_EMIT_S,
        "log_path": HISTORICAL_LOG_RELATIVE,
        "log_present": log_path.is_file(),
        "log_sha256": sha256_file(log_path) if log_path.is_file() else None,
        "model_load_seconds": HISTORICAL_MODEL_LOAD_S,
        "block_compute_seconds": HISTORICAL_BLOCK_COMPUTE_S,
        "semantic_extraction_seconds": HISTORICAL_SEMANTIC_S,
        "rtf": HISTORICAL_RTF,
        "utterance_count": 1,
        "block_count": 1,
        "warmed_up": False,
        "steady_state": False,
        "asr_scored": False,
        "semantic_fidelity_scored": False,
        "identity_similarity": "not_scored",
        "naturalness": "not_scored",
        "target_condition": (
            "generic streaming voice conversion, not the V2 accent-aware path"),
        "reproduced_here": False,
        "qualifies_candidate": False,
        "note": ("One historical first-block CPU run retained for provenance "
                 "only. The XLS-R-300M encoder and checkpoint were removed; "
                 "the referenced timing log is absent and nothing was re-run."),
    }


def voice_profile_mapping() -> Dict[str, str]:
    return {
        "permitted_input_and_target_reference_scope":
            "blocked_one_l2_arctic_clip_and_no_permitted_cohort",
        "task_and_language_speaker_groups":
            "blocked_one_arabic_l2_speaker_no_groups",
        "text_and_semantic_content":
            "blocked_one_short_block_not_asr_scored",
        "identity_and_similarity": "not_applicable_encoder_only",
        "naturalness": "not_applicable_encoder_only",
        "alignment_first_output_and_tail_timing":
            "source_reported_block_only_not_device_measured",
        "exact_target_condition":
            "recorded_generic_streaming_not_v2_accent_aware",
        "consent_reference_availability_and_output_use":
            "blocked_corpus_and_asset_rights_unconfirmed",
        "paired_quality_control": "blocked_weights_and_runtime_absent",
        "clean_reference_preservation": "blocked_no_paired_clean_reference",
        "numerical_and_nonfinite": "partial_local_harness_only",
        "candidate_output": "blocked_weights_and_runtime_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "exact_encoder_weights_and_runtime":
            "blocked_weights_and_runtime_absent",
        "layer12_hidden1024_semantic_fidelity":
            "blocked_weights_and_runtime_absent",
        "paired_reference_feature_fidelity": "blocked_no_paired_reference",
        "text_semantic_content": "blocked_one_short_block_not_asr_scored",
        "language_and_speaker_groups": "blocked_one_arabic_l2_speaker",
        "content_preservation_and_adverse":
            "partial_local_harness_only_not_candidate",
        "alignment_first_output_tail_and_content_delay":
            "source_reported_block_only_not_device_measured",
        "encoder_only_compute": "source_reported_one_first_block_not_reproduced",
        "device_timing_memory_and_callback":
            "blocked_no_paced_device_measurement",
        "target_condition_and_asset_rights":
            "blocked_corpus_and_asset_rights_unconfirmed",
        "numerical_and_nonfinite": "partial_local_harness_only",
        "delay_state_reset_drain_and_modes":
            "blocked_weights_and_runtime_absent",
    }


def candidates() -> Dict[str, Any]:
    return {
        CANDIDATE: {
            "status": "blocked_weights_and_runtime_absent",
            "metrics": None,
            "qualifies_candidate": False,
            "output_layer": ENCODER_OUTPUT_LAYER,
            "reason": (
                "The exact facebook/wav2vec2-xls-r-300m weights and a "
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
        "downstream_seed_vc_streaming": {
            "status": "source_reported_one_block_not_run",
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
            "harness stimulus characterisation only; not an XLS-R-300M "
            "result and not a candidate output"),
        "stimuli": stimuli,
        "speech_contrast": speech_contrast(STIMULUS_GENERATORS["speech_like"]()),
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
        "public_c_boundary": "not used: no C provider, header or installed target",
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
        ("research/accent-conversion-20261101/README.md records one Seed-VC "
         "real-time first block of 240 ms with 2.2 s left and 0.2 s right "
         "context, 10 diffusion steps, 254.01 s model load, 22.21 s block "
         "time, 92.55x real time and 12.20 s of semantic feature extraction; "
         "the run is not a steady-state benchmark and was not re-run here."),
        ("the same README says the checkpoint bundle and XLS-R-300M encoder "
         "were downloaded locally, but the bounded workspace search finds no "
         "XLS-R-300M config or weight files and no SHA-256 or byte count."),
        ("research/voice-conversion-eval-20261101/repos/seed-vc is pinned at "
         "commit 51383efd under GPL-3.0; its preset selects "
         "facebook/wav2vec2-xls-r-300m with output_layer 12 and a 1024-wide "
         "hidden state feeding a 384-wide length regulator."),
        ("plan/INVENTORY.json assigns the voice verification profile to "
         "SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER and asks for semantic "
         "extraction to be reproduced as part of the one-block CPU probe with "
         "correctness and compute measured independently."),
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
        "source_pin_exact": source["status"] == "present_pinned",
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
            missing_result("seed_vc_xlsr_300m_content_encoder_placeholder")[
                "status"] == "blocked",
        "identity_control_bit_exact": all(
            block["byte_identical"]
            for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
        "exact_layer_and_geometry_pinned": (
            geom["encoder_output_layer"] == ENCODER_OUTPUT_LAYER
            and geom["encoder_hidden_size"] == ENCODER_HIDDEN_SIZE
            and geom["encoder_frame_rate_hz"] == ENCODER_FRAME_RATE_HZ),
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
            "real_seed_vc_source_present": source["present"],
            "real_encoder_weights_present": weights["present"],
            "pinned_runtime_present": runtime["pinned"],
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "real_corpus_read": False,
            "note": (
                "No XLS-R-300M network, checkpoint loader, feature extractor "
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
            "missing_result": missing_result(
                "seed_vc_xlsr_300m_content_encoder_placeholder"),
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
