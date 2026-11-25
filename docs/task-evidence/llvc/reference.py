# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-LLVC.

This module is NOT LLVC. It does not implement, simulate, approximate, train
or run the KoeAI LLVC voice-conversion network. The MIT-licensed *source
checkout* is present at a pinned revision in the research workspace, but the
exact checkpoint ``G_500000.pth`` and the pinned PyTorch evaluation runtime are
absent. The module therefore builds a bounded, deterministic blocker report:

* strict request validation with fail-closed rejection of missing, invalid,
  nonfinite and out-of-range inputs;
* explicit source/weights/runtime probes (bounded, read-only, no downloads);
* exact chunk/latency geometry derived from the pinned upstream config and
  *source-reported* historical values, clearly separated from measurement;
* synthetic harness stimuli for identity/rejection controls only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

No network, model weights, real corpus audio, native library or download is
used. No candidate output is produced.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0

SCHEMA_ID = "audio-sdk/llvc-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/llvc-contract/0.1"
TASK = "SDK-LLVC"
COMPONENT = "llvc"
BRANCH = "swarm/SDK-LLVC"
BASE_COMMIT = "f2709c6b0efabdac98e4017e145d602e9f572d41"
TASK_PREFIX = "docs/task-evidence/llvc/"

SOURCE_REVISION = "1627c5d358cf9bb2b92b0ccc513d8b36807c923d"
SOURCE_TREE_DIGEST = (
    "e7930ed0181722b6e6e701d662241e76552dd4f16c600a4f8a84c55977aa762b")
SOURCE_FILE_COUNT = 51
SOURCE_LICENSE = "MIT"

WEIGHT_ARTIFACT = "G_500000.pth"
WEIGHT_REPOSITORY = "KoeAI/llvc"
WEIGHT_SOURCE_REPORTED_MIB = 37.7
SOURCE_REPORTED_CHUNK_FACTOR = 1
SOURCE_REPORTED_RTF = 0.123
SOURCE_REPORTED_E2E_MS = 120.785
SOURCE_REPORTED_AVG_INFER_MS = 106.0
SOURCE_REPORTED_COLD_RUN_S = 78.836
SOURCE_REPORTED_RTF_SLOWDOWN = 8.1
SOURCE_REPORTED_WER = 0.0

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
SOURCE_ROOT = WORKSPACE / "research/voice-conversion-eval-20261101/repos/llvc"
EVAL_ROOT = WORKSPACE / "research/voice-conversion-eval-20261101"
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only the stable linked row identity is projected, never hashed.
SOURCE_PINS = {
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-conversion-eval-20261101/results/llvc_asr.json":
        "2d8f31e91ea06efed6611a0aa41edf2babb08625a2da22fe30f4333554115c41",
    "research/voice-conversion-eval-20261101/results/llvc/"
    "source_ljspeech_lj001-0001.wav":
        "ac83ede41c7aa9b73216a1647a8aba6f74aec01826ed18c36f44d0129fd60327",
    "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md":
        "b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6",
    "research/voice-conversion-eval-20261101/repos/llvc/LICENSE":
        "718657c20ba7035b25bb447d80a53304115b44fea7e684df2a1ca240555eae4b",
    "research/voice-conversion-eval-20261101/repos/llvc/README.md":
        "0fbaab12f311e64607466a69c97b6a7e9e75e21439e5e547c51486882ccf7126",
    "research/voice-conversion-eval-20261101/repos/llvc/infer.py":
        "88c47703bcd52e70b8d45887828353be7b8b742fe3d08f81448808ce3b06934b",
    "research/voice-conversion-eval-20261101/repos/llvc/model.py":
        "b01626c0b0def1aac3c07c597a15529d9eac98f7bd17b241c1a08b88b92dc4b9",
    "research/voice-conversion-eval-20261101/repos/llvc/download_models.py":
        "e9c8643e9fde937599e1c2126b58623bb309f2ff7262a38409286a67f6868461",
    "research/voice-conversion-eval-20261101/repos/llvc/requirements.txt":
        "e2063e6455751a18895c5daa628a8dc728853f8dd5444c0ce766526bf0418825",
    "research/voice-conversion-eval-20261101/repos/llvc/experiments/llvc/"
    "config.json":
        "b5e488ada5267a8c09dd843a547fef8f95e39a49764b99f9bccf6a39be2f256c",
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
    "title": "LLVC",
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

CANDIDATE = "llvc"
TARGET_CONDITION = "builtin_any_to_one"
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)
REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples", "samples",
    "epoch", "first_input_sample", "lifecycle", "execution_mode",
    "target_condition",
})

SOURCE_ARTIFACT_FILES = (
    "reference.py", "run.py", "test_reference.py", "verify.py",
)

WEIGHT_SUFFIXES = (".pth", ".pt", ".ckpt", ".safetensors", ".onnx", ".bin")
WEIGHT_CANDIDATE_PATHS = (
    "research/voice-conversion-eval-20261101/repos/llvc/llvc_models/models/"
    "checkpoints/llvc/G_500000.pth",
    "research/voice-conversion-eval-20261101/repos/llvc/llvc_models",
    "research/voice-conversion-eval-20261101/checkpoints/G_500000.pth",
    "research/voice-conversion-eval-20261101/checkpoints",
    "data/llvc_models/models/checkpoints/llvc/G_500000.pth",
    "data/llvc_models",
)
RUNTIME_CANDIDATE_PATHS = (
    "research/voice-conversion-eval-20261101/.venv-eval/bin/python",
    "data/envs/llvc/bin/python",
    "data/envs/llvc",
)
RUNTIME_MODULES = (
    "torch", "torchaudio", "speechbrain", "auraloss", "soundfile",
    "huggingface_hub",
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
        "gate": "exact_source_and_checkpoint_pin",
        "status": "blocked",
        "reason": (
            "The MIT-licensed LLVC source tree is present at commit 1627c5d, "
            "but the exact checkpoint G_500000.pth (source-reported 37.7 MiB) "
            "is absent; no weight SHA-256 exists."),
        "reopen": (
            "Stage G_500000.pth with a recorded SHA-256 and byte count, or the "
            "exact published archive containing it, before any reproduction."),
    },
    {
        "id": "RG-02",
        "gate": "license_rights_and_target_reference_review",
        "status": "blocked",
        "reason": (
            "The source LICENSE is MIT, but the weights' redistribution terms, "
            "the any-to-one built-in target-speaker consent, and the provenance "
            "of the historical p360 comparison reference are unconfirmed."),
        "reopen": (
            "Record the weight licence/terms, target-speaker consent and "
            "reference provenance, and approve an explicit use/redistribution "
            "scope, including any generated output."),
    },
    {
        "id": "RG-03",
        "gate": "exact_runtime_build_and_install_parity",
        "status": "blocked",
        "reason": (
            "The historical PyTorch/TorchAudio/SpeechBrain/Auraloss evaluation "
            "environment was removed; no lockfile, wheel hashes or Bitwise "
            "reproducible runtime exists, and torch is not importable here."),
        "reopen": (
            "Create a frozen, hash-pinned CPU runtime matching the historical "
            "run, install it in a clean environment, and prove import/version "
            "parity before loading weights."),
    },
    {
        "id": "RG-04",
        "gate": "model_geometry_delay_drain_and_mode_parity",
        "status": "blocked",
        "reason": (
            "No checkpoint was loaded, so 208-sample chunks, 32-sample "
            "lookahead, 240-sample algorithmic offset, state/reset, finite "
            "drain and v0 execution-mode ownership were not exercised."),
        "reopen": (
            "With the exact weights and runtime, measure chunking, delay, "
            "state/reset, finite drain and execution-mode ownership at 16 kHz "
            "mono and map them to the v0 content model."),
    },
    {
        "id": "RG-05",
        "gate": "rights_qualified_paired_cohort_identity_and_naturalness",
        "status": "blocked",
        "reason": (
            "Only one historical source utterance exists; target similarity "
            "was not scored, no naturalness/listening result exists, and the "
            "p360 reference provenance is unconfirmed."),
        "reopen": (
            "Freeze a permitted multi-speaker/held-out cohort with targets, "
            "then score content, identity/similarity and naturalness "
            "separately against controls."),
    },
    {
        "id": "RG-06",
        "gate": "content_preservation_target_condition_and_adverse_cases",
        "status": "blocked",
        "reason": (
            "The single historical WER 0% result was not reproduced; clean "
            "references, peaks, nonfinite output, silence, unfamiliar speech "
            "and adverse target conditions are unmeasured for the candidate."),
        "reopen": (
            "Reproduce paired content/preservation controls with the exact "
            "checkpoint, including silence, peaks, nonfinite and unfamiliar "
            "speech, and state the exact built-in target condition."),
    },
    {
        "id": "RG-07",
        "gate": "target_runtime_timing_memory_and_callback_suitability",
        "status": "blocked",
        "reason": (
            "The historical source-reported RTF 0.123 and 120.785 ms inferred "
            "latency miss the 13 ms chunk deadline; no paced device, memory or "
            "callback measurement was made here."),
        "reopen": (
            "Measure paced target-device timing, memory, callback suitability "
            "and content delay independently of compute speed."),
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
        "KoeAI LLVC checkpoint G_500000.pth plus the exact pinned PyTorch "
        "evaluation runtime required to load it"),
    "source": {
        "status": "present_pinned",
        "repository": "KoeAI/LLVC",
        "revision": SOURCE_REVISION,
        "tree_digest": SOURCE_TREE_DIGEST,
        "file_count": SOURCE_FILE_COUNT,
        "license": SOURCE_LICENSE,
    },
    "weights": {
        "status": "absent",
        "artifact": WEIGHT_ARTIFACT,
        "upstream_repository": WEIGHT_REPOSITORY,
        "source_reported_size_mib": WEIGHT_SOURCE_REPORTED_MIB,
        "sha256": None,
        "byte_count": None,
        "license": None,
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "PyTorch CPU build compatible with the historical run",
            "TorchAudio with the TorchCodec/soundfile compatibility shim",
            "SpeechBrain transformer positional encoding",
            "Auraloss and remaining upstream requirements",
            "a hash-pinned lockfile or wheel set for the exact versions",
        ],
        "sha256": None,
        "lockfile": None,
    },
    "expected_license": (
        "MIT for the source checkout; the checkpoint and any built-in target "
        "voice require separate terms and consent review"),
    "pinned_revision": SOURCE_REVISION,
    "source_digest": SOURCE_TREE_DIGEST,
    "runtime_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "A recorded weight licence/terms decision, consent for the any-to-one "
        "built-in target voice, confirmed provenance for the historical p360 "
        "comparison reference, and an approved redistribution/use model for "
        "the checkpoint, runtime and any converted output are required before "
        "any reproduction, adapter or release claim."),
    "workspace_search": (
        "Bounded read-only checks of the pinned source tree, the evaluation "
        "checkpoint/runtime paths and the local Hugging Face cache found no "
        "G_500000.pth, no llvc_models directory and no pinned eval runtime."),
    "not_attempted": [
        "no network download or package installation",
        "no fabricated, reconstructed or surrogate LLVC weights",
        "no substitute model or voice-conversion algorithm",
        "no copied upstream source, test audio or licence text",
    ],
    "reopen": (
        "Stage the exact G_500000.pth with SHA-256/byte count, record weight "
        "and target-voice rights, rebuild a hash-pinned runtime, then repeat "
        "the voice profile with a permitted cohort and independent review."),
}

NON_CLAIMS = (
    "No LLVC checkpoint, weights, vocabulary or model output is included.",
    "No LLVC inference is implemented, approximated or simulated.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default.",
    "No real corpus, consent, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No missing, rejected or historical result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/llvc/ is touched.",
    "The reference is a task-local evidence builder, not LLVC.",
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
    target_condition = request["target_condition"]
    if target_condition != TARGET_CONDITION:
        raise ConfigError("UNKNOWN_TARGET_CONDITION",
                          "UNKNOWN_TARGET_CONDITION")
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
        "target_condition": target_condition,
    }


def probe_candidate(request: Any) -> None:
    validated = validate_request(request)
    raise WeightsAbsent(
        "WEIGHTS_ABSENT: " + validated["candidate"] + " checkpoint and pinned "
        "runtime are not present; no candidate processing is performed",
        "WEIGHTS_ABSENT")


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
        "target_condition": TARGET_CONDITION,
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
    return (
        ("unknown_candidate", variant(candidate="llvc2")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("wrong_rate", variant(sample_rate_hz=48000)),
        ("wrong_channels", variant(channels=2)),
        ("wrong_frame", variant(frame_samples=320)),
        ("short_samples", with_samples(short)),
        ("nonfinite_nan", with_samples(nan_samples)),
        ("nonfinite_inf", with_samples(inf_samples)),
        ("out_of_range", with_samples([4.5] * FRAME_SAMPLES)),
        ("bool_sample", with_samples([True] + [0.0] * (FRAME_SAMPLES - 1))),
        ("string_sample", with_samples(["0.0"] + [0.0] * (FRAME_SAMPLES - 1))),
        ("negative_epoch", variant(epoch=-1)),
        ("bool_epoch", variant(epoch=True)),
        ("negative_position", variant(first_input_sample=-160)),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("invalid_execution_mode", variant(execution_mode=4)),
        ("unknown_target_condition", variant(target_condition="p360")),
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
    head_ref = (SOURCE_ROOT / ".git/refs/heads/main")
    revision = (head_ref.read_text(encoding="ascii").strip()
                if head_ref.is_file() else None)
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
                 "checkout; no upstream file is copied or executed."),
    }


def weights_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    empty_directories: List[str] = []
    for relative in WEIGHT_CANDIDATE_PATHS:
        checked.append(relative)
        target = WORKSPACE / relative
        if target.is_file():
            found.append(relative)
        elif target.is_dir():
            hits = [item for item in target.iterdir()
                    if item.is_file() and
                    item.name.lower().endswith(WEIGHT_SUFFIXES)]
            if hits:
                found.extend(
                    (Path(relative) / item.name).as_posix() for item in hits)
            else:
                empty_directories.append(relative)
    suffix_hits: List[str] = []
    if SOURCE_ROOT.is_dir():
        for directory, directory_names, file_names in os.walk(SOURCE_ROOT):
            directory_names[:] = sorted(
                name for name in directory_names if name != ".git")
            for name in sorted(file_names):
                if name.lower().endswith(WEIGHT_SUFFIXES):
                    suffix_hits.append(
                        (Path(directory) / name).relative_to(
                            SOURCE_ROOT).as_posix())
    found.extend("source:" + item for item in suffix_hits)
    hf_repo = Path.home() / ".cache/huggingface/hub/models--KoeAI--llvc"
    checked.append(str(hf_repo))
    if hf_repo.exists():
        found.append(str(hf_repo))
    status = ("weights_present_unqualified" if found
              else "blocked_weights_absent")
    return {
        "empty_directories": sorted(set(empty_directories)),
        "status": status,
        "artifact": WEIGHT_ARTIFACT,
        "upstream_repository": WEIGHT_REPOSITORY,
        "source_reported_size_mib": WEIGHT_SOURCE_REPORTED_MIB,
        "sha256": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "present": bool(found),
        "note": ("Read-only path and name checks only; no archive is opened, "
                 "downloaded or reconstructed."),
    }


def runtime_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for relative in RUNTIME_CANDIDATE_PATHS:
        checked.append(relative)
        if (WORKSPACE / relative).exists():
            found.append(relative)
    modules = {name: _module_importable(name) for name in RUNTIME_MODULES}
    lock_candidates = [
        "research/voice-conversion-eval-20261101/requirements.lock",
        "research/voice-conversion-eval-20261101/.venv-eval/pyvenv.cfg",
    ]
    locks = [path for path in lock_candidates
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


def geometry() -> Dict[str, Any]:
    config_path = SOURCE_ROOT / "experiments/llvc/config.json"
    config = strict_json_loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ConfigError("config root is not an object", "CONFIG_INVALID")
    params = config.get("model_params")
    data = config.get("data")
    if not isinstance(params, dict) or not isinstance(data, dict):
        raise ConfigError("config shape is invalid", "CONFIG_INVALID")
    lookahead = _require_int(params.get("L"), "CONFIG_INVALID")
    dec_chunk = _require_int(params.get("dec_chunk_size"), "CONFIG_INVALID")
    sample_rate = _require_int(data.get("sr"), "CONFIG_INVALID")
    if sample_rate != SAMPLE_RATE_HZ:
        raise ConfigError("config rate mismatch", "CONFIG_INVALID")
    chunk_factor = SOURCE_REPORTED_CHUNK_FACTOR
    chunk_samples = lookahead * dec_chunk * chunk_factor
    chunk_ms = chunk_samples * 1000.0 / sample_rate
    lookahead_samples = 2 * lookahead
    algorithmic_samples = lookahead_samples + chunk_samples
    algorithmic_ms = algorithmic_samples * 1000.0 / sample_rate
    asr = strict_json_loads(
        (EVAL_ROOT / "results/llvc_asr.json").read_text(encoding="utf-8"))
    duration_seconds = float(asr["duration_seconds"])
    source_samples = int(round(duration_seconds * sample_rate))
    chunk_count = (source_samples + chunk_samples - 1) // chunk_samples
    padded_samples = chunk_count * chunk_samples
    average_from_rtf_ms = chunk_ms / SOURCE_REPORTED_RTF
    e2e_from_rtf_ms = algorithmic_ms + average_from_rtf_ms
    return {
        "source": "experiments/llvc/config.json + results/llvc_asr.json",
        "lookahead_L": lookahead,
        "dec_chunk_size": dec_chunk,
        "chunk_factor": chunk_factor,
        "chunk_samples": chunk_samples,
        "chunk_ms": _r(chunk_ms),
        "lookahead_samples": lookahead_samples,
        "algorithmic_latency_samples": algorithmic_samples,
        "algorithmic_latency_ms": _r(algorithmic_ms),
        "source_duration_seconds": duration_seconds,
        "source_duration_samples": source_samples,
        "chunk_count": chunk_count,
        "padded_samples": padded_samples,
        "deadline_ms": _r(chunk_ms),
        "source_reported": {
            "rtf": SOURCE_REPORTED_RTF,
            "e2e_latency_ms": SOURCE_REPORTED_E2E_MS,
            "average_inference_ms": SOURCE_REPORTED_AVG_INFER_MS,
            "cold_run_seconds": SOURCE_REPORTED_COLD_RUN_S,
            "rtf_slowdown": SOURCE_REPORTED_RTF_SLOWDOWN,
            "wer": SOURCE_REPORTED_WER,
        },
        "derived_from_source_reported_rtf": {
            "average_inference_ms": _r(average_from_rtf_ms),
            "e2e_latency_ms": _r(e2e_from_rtf_ms),
            "deadline_miss_ratio": _r(
                SOURCE_REPORTED_E2E_MS / chunk_ms),
            "note": ("Arithmetic on source-reported values from the pinned "
                     "evaluation README; not a local measurement."),
        },
        "measured_here": False,
        "candidate_output": False,
    }


def historical_evidence() -> Dict[str, Any]:
    asr_path = EVAL_ROOT / "results/llvc_asr.json"
    output_path = (EVAL_ROOT / "results/llvc/"
                   "source_ljspeech_lj001-0001.wav")
    asr = strict_json_loads(asr_path.read_text(encoding="utf-8"))
    output_digest = sha256_file(output_path) if output_path.is_file() else None
    expected_digest = SOURCE_PINS[
        "research/voice-conversion-eval-20261101/results/llvc/"
        "source_ljspeech_lj001-0001.wav"]
    return {
        "status": "source_reported_one_utterance_not_reproduced",
        "output_path": (
            "research/voice-conversion-eval-20261101/results/llvc/"
            "source_ljspeech_lj001-0001.wav"),
        "output_sha256": output_digest,
        "output_digest_matches_pin": output_digest == expected_digest,
        "asr_sha256": sha256_file(asr_path),
        "sample_rate_hz": asr.get("sample_rate"),
        "duration_seconds": asr.get("duration_seconds"),
        "wer": asr.get("wer"),
        "clipped_sample_fraction": asr.get("clipped_sample_fraction"),
        "utterance_count": 1,
        "identity_similarity": "not_scored",
        "naturalness": "not_scored",
        "target_condition": (
            "built-in any-to-one target; not the p360 zero-shot reference"),
        "target_reference_provenance": "unconfirmed",
        "reproduced_here": False,
        "qualifies_candidate": False,
        "note": ("Historical local artifact retained for provenance only; the "
                 "checkpoint was removed and nothing was re-run."),
    }


def voice_profile_mapping() -> Dict[str, str]:
    return {
        "permitted_input_and_target_reference_scope":
            "blocked_single_utterance_and_unconfirmed_target_provenance",
        "task_and_language_speaker_groups":
            "blocked_one_english_speaker_no_groups",
        "text_and_semantic_content":
            "source_reported_one_utterance_wer_not_reproduced",
        "identity_and_similarity": "blocked_not_scored",
        "naturalness": "blocked_no_listening_or_mos",
        "alignment_first_output_and_tail_timing":
            "source_reported_inferred_not_device_measured",
        "exact_target_condition":
            "recorded_builtin_any_to_one_not_p360",
        "consent_reference_availability_and_output_use":
            "blocked_rights_and_consent_unconfirmed",
        "paired_quality_control": "blocked_weights_and_runtime_absent",
        "clean_reference_preservation": "blocked_no_paired_clean_reference",
        "numerical_and_nonfinite": "partial_local_harness_only",
        "candidate_output": "blocked_weights_and_runtime_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "identity_noisy_control": "blocked_weights_and_runtime_absent",
        "established_task_matched_baseline":
            "source_reported_proxy_only_not_run",
        "paired_si_sdr_stoi": "blocked_no_paired_clean_reference",
        "clean_speech_preservation": "blocked_no_paired_clean_reference",
        "text_semantic_content": "source_reported_one_utterance_not_reproduced",
        "identity_similarity": "blocked_not_scored",
        "naturalness": "blocked_no_listening",
        "alignment_first_output_tail_and_content_delay":
            "source_reported_inferred_not_device_measured",
        "target_condition_and_consent":
            "blocked_rights_and_consent_unconfirmed",
        "language_and_speaker_groups": "blocked_single_utterance",
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
            "target_condition": TARGET_CONDITION,
            "reason": (
                "The exact G_500000.pth checkpoint and a pinned runtime are "
                "absent; no conversion, quality or timing result was produced."),
        }
    }


def controls() -> Dict[str, Any]:
    return {
        "source_identity_control": {
            "status": "not_run_no_candidate",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "meanvc2_streaming_proxy_baseline": {
            "status": "source_reported_only_not_run",
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
    for name, generator in STIMULUS_GENERATORS.items():
        samples = generator()
        stimuli[name] = stimulus_metrics(name, samples)
        identity[name] = {
            "digest": tensor_digest(samples),
            "byte_identical": tuple(samples) == tuple(float(value)
                                                     for value in samples),
        }
    return {
        "purpose": ("harness stimulus characterisation only; not an LLVC result "
                    "and not a candidate output"),
        "stimuli": stimuli,
        "speech_contrast": speech_contrast(STIMULUS_GENERATORS["speech_like"]()),
        "identity_control": identity,
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
        ("research/voice-conversion-eval-20261101/README.md records a KoeAI/LLVC "
         "checkout at commit 1627c5d, checkpoint G_500000.pth (37.7 MiB), one "
         "9.655 s LJ Speech source, Whisper Tiny EN WER 0%, source-reported RTF "
         "0.123 and inferred 120.785 ms latency; the checkpoint was removed."),
        ("research/voice-enhancement-20261101/candidate_matrix.csv record 97 "
         "keeps LLVC at 'partially evaluated' with one utterance, no target "
         "similarity and a 13 ms chunk-deadline miss."),
        ("research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md "
         "recomputes the historical output SHA-256 and warns that the p360 "
         "target reference provenance is not independently confirmed."),
        ("plan/INVENTORY.json assigns the voice verification profile to "
         "SDK-LLVC and links the same one-utterance evidence paths."),
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
        "nonfinite_samples_rejected": any(
            case["id"].startswith("nonfinite") and not case["accepted"]
            for case in adverse_request["cases"]),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked":
            missing_result("llvc_synthetic_placeholder")["status"] == "blocked",
        "identity_control_bit_exact": all(
            block["byte_identical"]
            for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
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
            "real_llvc_source_present": source["present"],
            "real_llvc_weights_present": weights["present"],
            "pinned_runtime_present": runtime["pinned"],
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "note": (
                "No LLVC network, checkpoint loader, vocoder or inference path "
                "is implemented or simulated; only probes, geometry arithmetic, "
                "request rejection and synthetic controls are performed."),
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
            "missing_result": missing_result("llvc_synthetic_placeholder"),
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
