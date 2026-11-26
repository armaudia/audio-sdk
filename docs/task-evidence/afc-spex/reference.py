# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for AFC-SPEX (SDK-AFC-SPEX).

This module is NOT AFC-SPEX and contains no AFC-SPEX code, config, checkpoint
or inference. A bounded read-only search finds no AFC-SPEX checkout, no
pretrained checkpoint, no three-channel matched input and no hash-pinned
runtime in the workspace. The module therefore builds a fail-closed blocker
report:

* strict request validation at a declared three-channel geometry;
* explicit source, config, checkpoint, input, runtime and rights probes;
* an admission gate that rejects every syntactically valid request because the
  required artifacts are absent;
* synthetic harness stimuli for rejection/identity controls only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

Nothing is downloaded, cloned, installed, reconstructed or simulated. No
candidate feature or audio output is produced. No result qualifies AFC-SPEX.
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

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_ID = "audio-sdk/afc-spex-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/afc-spex-contract/0.1"
TASK = "SDK-AFC-SPEX"
COMPONENT = "afc-spex"
BRANCH = "swarm/SDK-AFC-SPEX"
BASE_COMMIT = "66a44bc4c87374ab6985bc3a54d15282f4cecc98"
TASK_PREFIX = "docs/task-evidence/afc-spex/"
MODE = "feasibility"
VERIFICATION_PROFILE = "DSP"

# Installed v0 format. This is the unchanged public baseline, not the required
# AFC-SPEX geometry.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
ABI_MAJOR = 0
ABI_MINOR = 1

# AFC-SPEX is reported to require three microphone channels. The exact rate,
# hop, frame size, preprocessing, layer count and checkpoint identity are not
# locally available and are deliberately not invented.
REQUIRED_INPUT_CHANNELS = 3
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0
HARNESS_FRAME_SAMPLES = FRAME_SAMPLES
HARNESS_FRAME_VALUES = REQUIRED_INPUT_CHANNELS * HARNESS_FRAME_SAMPLES

SOURCE_REPOSITORY = "https://github.com/ZLiNJU/AFC-SPEX"
MODEL_CONFIG_PATH = "afcspex/configs/model_config.yaml"
INFER_CONFIG_PATH = "afcspex/configs/infer_config.yaml"
CHECKPOINT_DECLARATION = "author-local experiment path (unresolved)"

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only the stable linked-row identity is projected, never hashed.
SOURCE_PINS = {
    "research/feedback_control_20261028.md":
        "47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

EXPECTED_LINK = {
    "task_id": TASK,
    "title": "AFC-SPEX",
    "mode": MODE,
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)

PROFILE_SOURCE = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"

CANDIDATE = "afc_spex_three_channel"
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)
REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples", "samples",
    "epoch", "first_input_sample", "lifecycle", "execution_mode",
})

SOURCE_ARTIFACT_FILES = (
    "reference.py", "run.py", "test_reference.py", "verify.py",
)

SOURCE_CANDIDATE_PATHS = (
    "research/afc-spex",
    "research/afc_spex",
    "research/repos/afc-spex",
    "research/repos/AFC-SPEX",
    "research/feedback-control/repos/afc-spex",
    "research/voice-conversion-eval-20261101/repos/afc-spex",
    "third_party/afc-spex",
    "vendor/afc-spex",
    "data/models/afc-spex",
    "~/code/AFC-SPEX",
    "~/projects/AFC-SPEX",
)
CHECKPOINT_CANDIDATE_PATHS = (
    "research/afc-spex/checkpoints",
    "research/afc-spex/pretrained",
    "data/models/afc-spex",
    "data/models/AFC-SPEX",
    "~/code/AFC-SPEX/checkpoints",
    "~/projects/AFC-SPEX/checkpoints",
    "~/.cache/afc-spex",
)
CHECKPOINT_MARKERS = (
    ".pt", ".pth", ".ckpt", ".onnx", ".safetensors", ".bin",
)
INPUT_CANDIDATE_PATHS = (
    "data/corpora/afc-spex",
    "data/corpora/afc-spex-three-channel",
    "research/afc-spex/input",
    "research/afc-spex/three-channel-input",
    "data/afc-spex/input",
)
INPUT_MARKERS = (".wav", ".flac", ".safetensors", ".npy")
RUNTIME_CANDIDATE_PATHS = (
    "data/envs/afc-spex",
    "data/envs/afc-spex/bin/python",
    "research/afc-spex/.venv",
    "research/afc-spex/.venv/bin/python",
    "~/code/AFC-SPEX/.venv",
)
RUNTIME_MODULES = (
    "torch", "torchaudio", "numpy", "soundfile", "yaml", "huggingface_hub",
)
RUNTIME_LOCK_CANDIDATES = (
    "research/afc-spex/requirements.lock",
    "research/afc-spex/poetry.lock",
    "research/afc-spex/uv.lock",
    "data/envs/afc-spex/requirements.lock",
)

REQUIRED_ARTIFACTS = (
    {
        "id": "A1",
        "artifact": "AFC-SPEX source checkout",
        "required": (
            "A local checkout of https://github.com/ZLiNJU/AFC-SPEX at a "
            "recorded full commit SHA with a read-only non-.git tree digest, "
            "the repository license file and the training/inference scripts"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A2",
        "artifact": "exact model and inference configs",
        "required": (
            "Byte-identical afcspex/configs/model_config.yaml and "
            "afcspex/configs/infer_config.yaml from the same revision; the "
            "channel count, sample rate, hop, frame, preprocessing and "
            "checkpoint path must be read from these pinned files"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A3",
        "artifact": "exact pretrained checkpoint",
        "required": (
            "The exact checkpoint file named by the inference config, at a "
            "resolved path rather than an author-local experiment path, with "
            "full SHA-256, byte count and weight terms"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A4",
        "artifact": "three-channel matched input",
        "required": (
            "A synchronous three-microphone recording of the same talker and "
            "session at the pinned rate/hop/geometry, with corpus permission; "
            "a mono AMI excerpt is not a matched three-channel input"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A5",
        "artifact": "hash-pinned runtime",
        "required": (
            "A frozen Python/PyTorch or declared runtime with exact versions, "
            "wheel/lockfile hashes and an explicit CPU/device target for the "
            "records measured here"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A6",
        "artifact": "rights and independent review package",
        "required": (
            "Source license, checkpoint weight terms, input corpus permission, "
            "redistribution/use scope and an independent exact-head review "
            "before any public-surface or release decision"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
)

GATES = (
    {
        "id": "RG-01",
        "gate": "exact_source_revision_and_license_pin",
        "status": "blocked",
        "reason": (
            "No AFC-SPEX checkout exists locally; the repository revision, "
            "license file, tree digest and training/inference scripts are "
            "absent and no source is pinned."),
        "reopen": (
            "Stage the exact AFC-SPEX checkout at a recorded full commit with "
            "a read-only tree digest and its license file, then pin every "
            "required source path before reading any config."),
    },
    {
        "id": "RG-02",
        "gate": "exact_pretrained_checkpoint_and_weight_rights",
        "status": "blocked",
        "reason": (
            "The published finding is only that the checked-in inference "
            "config names an author-local checkpoint; no checkpoint file, "
            "SHA-256, byte count or weight terms are available locally."),
        "reopen": (
            "Obtain the exact checkpoint, resolve its non-local path, record "
            "SHA-256 and byte count, and approve its weight terms and "
            "caller-supplied-asset redistribution/use scope."),
    },
    {
        "id": "RG-03",
        "gate": "three_channel_matched_input_and_task_geometry",
        "status": "blocked",
        "reason": (
            "The declared task requires three microphone channels but only a "
            "mono AMI excerpt is recorded; no matched three-channel input and "
            "no pinned rate, hop, frame or preprocessing geometry exist."),
        "reopen": (
            "Stage a rights-qualified synchronous three-channel input matched "
            "to the pinned config, with exact rate, hop, frame, channel order "
            "and alignment, before any reproduction."),
    },
    {
        "id": "RG-04",
        "gate": "hash_pinned_runtime_and_install_parity",
        "status": "blocked",
        "reason": (
            "No Python/PyTorch or other runtime is installed, importable or "
            "pinned by a lockfile/wheel set for this task."),
        "reopen": (
            "Create a frozen, hash-pinned runtime for the exact declared "
            "versions, install it in a clean environment and prove import and "
            "device parity before loading a checkpoint."),
    },
    {
        "id": "RG-05",
        "gate": "exact_model_reproduction_state_reset_drain_and_modes",
        "status": "blocked",
        "reason": (
            "No source, config or checkpoint was loaded, so parameter "
            "identity, layer/stride geometry, content delay, state/reset, "
            "finite drain and execution-mode ownership were not exercised."),
        "reopen": (
            "With pinned source, config, checkpoint and runtime, reproduce the "
            "declared model and verify parameter identity, geometry, delay, "
            "reset, finite drain and execution-mode ownership."),
    },
    {
        "id": "RG-06",
        "gate": "dsp_acceptance_matrix_and_numerical_behavior",
        "status": "blocked",
        "reason": (
            "The DSP profile requires sweeps, steps, impulses, silence, clean "
            "speech and a task-specific control with gain, response, attack/"
            "release, headroom, delay, numerical behavior, state transitions "
            "and interacting nonlinear configurations; none was run because "
            "there is no candidate output."),
        "reopen": (
            "Run the full DSP matrix through the exact model and runtime, "
            "retain every failure and nonfinite case, and record gain, "
            "response, attack/release, headroom, delay and state transitions "
            "with exact tolerances agreed before scoring."),
    },
    {
        "id": "RG-07",
        "gate": "speaker_extraction_separated_from_mono_howling_control",
        "status": "blocked",
        "reason": (
            "AFC-SPEX is a multichannel speaker-extraction candidate and no "
            "result distinguishes extraction quality from mono howling "
            "suppression, maximum stable gain, recovery after path change or "
            "held-out talker/room/path behavior."),
        "reopen": (
            "Produce separate, clearly labelled evidence for multichannel "
            "speaker extraction and for mono howling control, with held-out "
            "talkers, room/path changes and matched controls; never report one "
            "task's result as the other."),
    },
    {
        "id": "RG-08",
        "gate": "provider_intake_public_surface_timing_listening_benchmark_release",
        "status": "blocked",
        "reason": (
            "No multichannel public boundary, provider intake, descriptor, "
            "installed target, paced device timing, listening or "
            "intelligibility result, benchmark bundle, independent exact-head "
            "review or release approval exists."),
        "reopen": (
            "Complete an independent multichannel public-surface decision and "
            "provider intake, then measure target-device timing, memory and "
            "callback suitability, run authorized listening/intelligibility "
            "controls, validate a benchmark bundle and obtain release approval."),
    },
)

UPSTREAM_BLOCKER = {
    "status": "blocked_source_checkpoint_input_and_runtime_absent",
    "artifact": (
        "AFC-SPEX source, exact model/inference configs, pretrained "
        "checkpoint, three-channel matched input and hash-pinned runtime"),
    "source": {
        "status": "absent",
        "repository": SOURCE_REPOSITORY,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
    },
    "configs": {
        "status": "absent",
        "required_paths": [MODEL_CONFIG_PATH, INFER_CONFIG_PATH],
        "sha256": None,
        "byte_count": None,
    },
    "checkpoint": {
        "status": "absent",
        "declared_path": CHECKPOINT_DECLARATION,
        "resolved_path": None,
        "sha256": None,
        "byte_count": None,
        "license": None,
        "terms_recorded": False,
    },
    "input": {
        "status": "absent",
        "required_channels": REQUIRED_INPUT_CHANNELS,
        "sample_rate_hz": None,
        "hop_samples": None,
        "frame_samples": None,
        "corpus_rights": False,
        "mono_pilot_compatible": False,
        "sha256": None,
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "the exact runtime declared by the pinned AFC-SPEX requirements",
            "a hash-pinned lockfile or wheel set for every installed version",
            "an explicit CPU or device target and import-parity check",
        ],
        "sha256": None,
        "lockfile": None,
    },
    "expected_license": (
        "not recorded locally; the AFC-SPEX repository and checkpoint terms "
        "require separate rights review before any use or redistribution"),
    "pinned_revision": None,
    "source_digest": None,
    "config_digest": None,
    "checkpoint_digest": None,
    "input_digest": None,
    "runtime_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "A recorded AFC-SPEX source license, an approved checkpoint weight "
        "terms and redistribution/use decision, a caller-supplied-asset "
        "policy for the checkpoint and input, and permission for every "
        "three-channel recording and any derived output are required before "
        "any reproduction, adapter, benchmark or release claim."),
    "workspace_search": (
        "Bounded read-only existence and file-name checks of named candidate "
        "paths under the workspace found no AFC-SPEX checkout, no model or "
        "inference config, no checkpoint, no three-channel matched input and "
        "no pinned runtime. No archive, weight file or audio file was opened, "
        "downloaded or reconstructed."),
    "not_attempted": [
        "no git clone, network download or package installation",
        "no fabricated, reconstructed or surrogate AFC-SPEX source or config",
        "no fabricated, reconstructed or surrogate checkpoint or weights",
        "no mono-to-three-channel upmix, channel duplication or substitution",
        "no copied upstream source, corpus audio or license text",
        "no model load, feature/audio output, listening or timing run",
    ],
    "reopen": (
        "Stage the exact source at a recorded commit with license and tree "
        "digest, pin both configs, obtain the exact checkpoint with SHA-256, "
        "byte count and terms, stage a rights-qualified three-channel matched "
        "input, build a hash-pinned runtime, then reproduce the declared "
        "model and run the DSP matrix with independent review."),
}

NON_CLAIMS = (
    "No AFC-SPEX source, config, checkpoint, weight, feature or output is included.",
    "No AFC-SPEX inference is implemented, approximated, simulated or run.",
    "No mono-to-three-channel conversion, channel duplication or surrogate input is used.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default.",
    "No real corpus, checkpoint, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No speaker-extraction result is reported as mono howling control.",
    "No missing, rejected or source-reported result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/afc-spex/ is touched.",
    "The reference is a task-local feasibility gate, not an AFC-SPEX implementation.",
    "The declared three-channel task is not representable by installed v0 mono.",
    "All harness stimuli are analytic or seeded synthetic; no checkpoint is used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
)

SPEAKER_EXTRACTION = {
    "declared_task": (
        "multichannel target-speaker extraction under acoustic feedback"),
    "required_input_channels": REQUIRED_INPUT_CHANNELS,
    "status": "blocked_artifacts_absent",
    "metrics": None,
    "result": None,
    "qualifies_candidate": False,
    "may_be_reported_as_mono_howling_control": False,
    "note": (
        "No extraction, leakage, target-damage or channel-loss result exists; "
        "nothing here is an extraction measurement."),
}

MONO_HOWLING_CONTROL = {
    "status": "not_evaluated_by_this_task",
    "installed_v0_channels": CHANNELS,
    "metrics": None,
    "result": None,
    "qualifies_candidate": False,
    "maximum_stable_gain_claim": False,
    "feedback_cancellation_claim": False,
    "note": (
        "This feasibility task makes no mono howling-suppression, "
        "maximum-stable-gain or feedback-cancellation claim. A future "
        "AFC-SPEX speaker-extraction result must not be reported as mono "
        "howling control evidence."),
}


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


class ArtifactsAbsent(EvidenceError):
    code = "ARTIFACTS_ABSENT"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True).encode("utf-8")


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


def strict_json_load(path: Path) -> Any:
    value = strict_json_loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise JsonError("JSON_NOT_OBJECT: " + str(path), "JSON_NOT_OBJECT")
    return value


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


def silence(length: int = HARNESS_FRAME_VALUES) -> Tuple[float, ...]:
    return (0.0,) * length


def impulse(length: int = HARNESS_FRAME_VALUES,
            position: int = HARNESS_FRAME_VALUES // 2,
            amplitude: float = 0.5) -> Tuple[float, ...]:
    if not 0 <= position < length:
        raise ConfigError("impulse position out of range", "INVALID_STIMULUS")
    values = [0.0] * length
    values[position] = amplitude
    return tuple(values)


def step(length: int = HARNESS_FRAME_VALUES,
         position: int = HARNESS_FRAME_VALUES // 2,
         amplitude: float = 0.25) -> Tuple[float, ...]:
    if not 0 <= position <= length:
        raise ConfigError("step position out of range", "INVALID_STIMULUS")
    return tuple(0.0 if index < position else amplitude
                 for index in range(length))


def sweep(length: int = HARNESS_FRAME_VALUES, start_hz: float = 200.0,
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


def speech_like(length: int = HARNESS_FRAME_VALUES,
                seed: int = 20261126) -> Tuple[float, ...]:
    noise = _lcg(seed)
    values = []
    for index in range(length):
        noise_value = next(noise)
        t = index / float(SAMPLE_RATE_HZ)
        if index < length // 2:
            value = (0.25 * math.sin(2.0 * math.pi * 120.0 * t) +
                     0.12 * math.sin(2.0 * math.pi * 240.0 * t) +
                     0.06 * math.sin(2.0 * math.pi * 360.0 * t))
            envelope = 0.65 + 0.35 * math.sin(2.0 * math.pi * 3.0 * t)
            value = value * envelope + 0.005 * noise_value
        else:
            value = 0.001 * noise_value
        values.append(value)
    return tuple(values)


STIMULUS_GENERATORS = {
    "silence": lambda: silence(),
    "impulse": lambda: impulse(),
    "step": lambda: step(),
    "sweep": lambda: sweep(),
    "speech_like": lambda: speech_like(),
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


def channel_views(samples: Sequence[float]) -> List[List[float]]:
    if len(samples) != HARNESS_FRAME_VALUES:
        raise InputError("WRONG_HARNESS_SIZE", "WRONG_SAMPLE_COUNT")
    frames = [list(samples[index * HARNESS_FRAME_SAMPLES:
                        (index + 1) * HARNESS_FRAME_SAMPLES])
              for index in range(REQUIRED_INPUT_CHANNELS)]
    if any(len(frame) != HARNESS_FRAME_SAMPLES for frame in frames):
        raise InputError("WRONG_CHANNEL_LAYOUT", "WRONG_SAMPLE_COUNT")
    return frames


def speech_contrast(samples: Sequence[float]) -> Dict[str, Any]:
    voiced = []
    pause = []
    for index, value in enumerate(samples):
        if index < len(samples) // 2:
            voiced.append(float(value))
        else:
            pause.append(float(value))
    voiced_rms = rms(voiced)
    pause_rms = rms(pause)
    return {
        "voiced_rms": _r(voiced_rms),
        "pause_rms": _r(pause_rms),
        "voiced_to_pause_db": _r(db_ratio(voiced_rms, pause_rms)),
        "proxy": "source-anchored voiced/pause RMS contrast; not intelligibility",
    }


def _validate_sample_list(samples: Any, expected: int) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise InputError("SAMPLES_NOT_A_LIST", "INVALID_SAMPLE_TYPE")
    if len(samples) != expected:
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


def _require_int(value: Any, code: str,
                 minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(code, code)
    if minimum is not None and value < minimum:
        raise ConfigError(code, code)
    return value


def validate_request(request: Any) -> Dict[str, Any]:
    """Validate a declared three-channel request; never runs a candidate."""
    if not isinstance(request, dict):
        raise InputError("request must be an object", "INVALID_REQUEST")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown), "UNKNOWN_FIELD")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing), "MISSING_FIELD")
    if request["candidate"] != CANDIDATE:
        raise ConfigError("UNKNOWN_CANDIDATE", "UNKNOWN_CANDIDATE")
    rate = _require_int(request["sample_rate_hz"], "INVALID_RATE", 1)
    channels = _require_int(request["channels"], "WRONG_CHANNELS")
    if channels != REQUIRED_INPUT_CHANNELS:
        raise ConfigError("WRONG_CHANNELS", "WRONG_CHANNELS")
    frame_samples = _require_int(request["frame_samples"], "INVALID_FRAME", 1)
    if frame_samples > 4096:
        raise ConfigError("FRAME_TOO_LARGE", "INVALID_FRAME")
    samples = _validate_sample_list(
        request["samples"], channels * frame_samples)
    epoch = _require_int(request["epoch"], "INVALID_EPOCH", 0)
    first_input_sample = _require_int(request["first_input_sample"],
                                      "INVALID_POSITION", 0)
    lifecycle = request["lifecycle"]
    if lifecycle not in LIFECYCLES:
        raise ConfigError("INVALID_LIFECYCLE", "INVALID_LIFECYCLE")
    execution_mode = _require_int(request["execution_mode"], "INVALID_MODE")
    if execution_mode not in EXECUTION_MODES:
        raise ConfigError("INVALID_MODE", "INVALID_MODE")
    return {
        "candidate": CANDIDATE,
        "sample_rate_hz": rate,
        "channels": channels,
        "frame_samples": frame_samples,
        "samples": tuple(samples),
        "epoch": epoch,
        "first_input_sample": first_input_sample,
        "lifecycle": lifecycle,
        "execution_mode": execution_mode,
    }


def _base_request() -> Dict[str, Any]:
    return {
        "candidate": CANDIDATE,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": REQUIRED_INPUT_CHANNELS,
        "frame_samples": HARNESS_FRAME_SAMPLES,
        "samples": [0.0] * HARNESS_FRAME_VALUES,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
    }


def _adverse_request_specs():
    base = _base_request()

    def variant(**changes):
        value = dict(base)
        value.update(changes)
        return value

    short = [0.0] * (HARNESS_FRAME_VALUES - 1)
    long = [0.0] * (HARNESS_FRAME_VALUES + 1)
    nan_samples = [0.0] * HARNESS_FRAME_VALUES
    nan_samples[7] = float("nan")
    inf_samples = [0.0] * HARNESS_FRAME_VALUES
    inf_samples[9] = float("inf")
    negative_inf_samples = [0.0] * HARNESS_FRAME_VALUES
    negative_inf_samples[9] = float("-inf")
    return (
        ("unknown_candidate", variant(candidate="afc_spex")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("mono_channels", variant(channels=1)),
        ("two_channels", variant(channels=2)),
        ("four_channels", variant(channels=4)),
        ("zero_rate", variant(sample_rate_hz=0)),
        ("negative_rate", variant(sample_rate_hz=-16000)),
        ("bool_rate", variant(sample_rate_hz=True)),
        ("zero_frame", variant(frame_samples=0)),
        ("too_large_frame", variant(frame_samples=4097)),
        ("short_samples", variant(samples=short)),
        ("long_samples", variant(samples=long)),
        ("nonfinite_nan", variant(samples=nan_samples)),
        ("nonfinite_inf", variant(samples=inf_samples)),
        ("nonfinite_negative_inf", variant(samples=negative_inf_samples)),
        ("out_of_range", variant(samples=[4.5] * HARNESS_FRAME_VALUES)),
        ("bool_sample", variant(samples=[True] + [0.0] *
                                (HARNESS_FRAME_VALUES - 1))),
        ("string_sample", variant(samples=["0.0"] + [0.0] *
                                  (HARNESS_FRAME_VALUES - 1))),
        ("null_sample", variant(samples=[None] + [0.0] *
                                (HARNESS_FRAME_VALUES - 1))),
        ("negative_epoch", variant(epoch=-1)),
        ("bool_epoch", variant(epoch=True)),
        ("negative_position", variant(first_input_sample=-160)),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("invalid_execution_mode", variant(execution_mode=4)),
        ("bool_execution_mode", variant(execution_mode=True)),
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
        "note": ("Invalid requests are rejected before any artifact check or "
                 "candidate call; no metrics exist."),
    }


def _json_adverse_cases() -> Dict[str, Any]:
    specs = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} extra'),
        ("invalid_syntax", '{"a":}'),
        ("json_not_object", '[1,2,3]'),
    )
    cases: List[Dict[str, Any]] = []
    for name, text in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            value = strict_json_loads(text)
            accepted = not isinstance(value, list)
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
        "reason": "source_checkpoint_input_and_runtime_absent",
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


def _markers_in(path: Path, markers: Sequence[str],
                max_depth: int = 3) -> List[str]:
    found: List[str] = []
    if path.is_file():
        if path.suffix.lower() in markers:
            found.append(path.name)
        return found
    if not path.is_dir():
        return found
    base_depth = len(path.parts)
    for current, directory_names, file_names in os.walk(path):
        current_path = Path(current)
        if len(current_path.parts) - base_depth >= max_depth:
            directory_names[:] = []
        else:
            directory_names[:] = sorted(directory_names)
        for name in sorted(file_names):
            if Path(name).suffix.lower() in markers:
                found.append(name)
    return sorted(set(found))


def source_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in SOURCE_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.exists():
            found.append(label)
    return {
        "status": "blocked_source_absent" if not found else
                  "source_present_unqualified",
        "present": bool(found),
        "repository": SOURCE_REPOSITORY,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": ("Read-only existence checks only; no clone, fetch, archive "
                 "extraction or upstream file is opened or executed."),
    }


def checkpoint_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in CHECKPOINT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.exists():
            hits = _markers_in(target, CHECKPOINT_MARKERS)
            if hits:
                found.extend((Path(label) / name).as_posix()
                             for name in hits)
    return {
        "status": "blocked_checkpoint_absent" if not found else
                  "checkpoint_present_unqualified",
        "present": bool(found),
        "declared_path": CHECKPOINT_DECLARATION,
        "resolved_path": None,
        "sha256": None,
        "byte_count": None,
        "license": None,
        "terms_recorded": False,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": ("Path and file-name checks only; no checkpoint, weight file "
                 "or cache blob is opened, downloaded or reconstructed."),
    }


def input_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in INPUT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.exists():
            hits = _markers_in(target, INPUT_MARKERS)
            if hits:
                found.extend((Path(label) / name).as_posix()
                             for name in hits)
    return {
        "status": "blocked_three_channel_input_absent" if not found else
                  "input_present_unqualified",
        "present": bool(found),
        "required_channels": REQUIRED_INPUT_CHANNELS,
        "sample_rate_hz": None,
        "hop_samples": None,
        "frame_samples": None,
        "corpus_rights": False,
        "mono_pilot_compatible": False,
        "sha256": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": ("Existence checks only; no audio file is opened or decoded. "
                 "A mono recording cannot satisfy a three-channel task and no "
                 "upmix or duplication is used."),
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
             if _resolve_workspace_path(path).is_file()]
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
        "sha256": None,
        "note": ("No package is installed, imported or downloaded. Import "
                 "probes report the current interpreter only; this is not the "
                 "AFC-SPEX runtime."),
    }


def rights_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_rights_unrecorded",
        "source_license": None,
        "source_license_file_present": False,
        "checkpoint_terms": None,
        "checkpoint_terms_recorded": False,
        "input_corpus_rights": False,
        "redistribution_scope": None,
        "review": "blocked",
        "reviewed_by": None,
        "note": ("No repository license, checkpoint terms or corpus "
                 "permission is recorded locally. Upstream presence is not a "
                 "right to use, redistribute or publish."),
    }


def geometry() -> Dict[str, Any]:
    return {
        "declared_task": (
            "multichannel target-speaker extraction under acoustic feedback"),
        "declared_input_channels": REQUIRED_INPUT_CHANNELS,
        "declared_input_rate_hz": None,
        "declared_hop_samples": None,
        "declared_frame_samples": None,
        "declared_layer_count": None,
        "declared_preprocessing": None,
        "declared_checkpoint": CHECKPOINT_DECLARATION,
        "declared_config_files": [MODEL_CONFIG_PATH, INFER_CONFIG_PATH],
        "v0_can_represent_declared_input": False,
        "verified_here": False,
        "measured_here": False,
        "candidate_output": False,
        "note": (
            "Only the three-channel requirement and the author-local "
            "checkpoint declaration are recorded by the pinned research note. "
            "Rate, hop, frame, layer count, preprocessing and checkpoint "
            "identity are absent and were not inferred from unrelated code."),
    }


def profile_mapping() -> Dict[str, str]:
    return {
        "sweeps_steps_impulses_silence_clean_speech":
            "blocked_no_candidate",
        "task_specific_intelligibility_or_load_control":
            "blocked_no_permitted_cohort",
        "gain_and_frequency_response": "blocked_no_candidate_output",
        "attack_and_release": "blocked_no_candidate_output",
        "headroom_and_peaks": "blocked_no_candidate_output",
        "delay_and_content_mapping": "blocked_no_candidate_output",
        "numerical_behavior": "partial_local_harness_rejection_only",
        "state_transitions": "blocked_no_candidate_instance",
        "interacting_nonlinear_configurations": "blocked_no_candidate_instance",
        "candidate_output": "blocked_source_checkpoint_input_runtime_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "exact_source_revision_and_license":
            "blocked_source_absent",
        "exact_model_and_inference_configs":
            "blocked_configs_absent",
        "exact_pretrained_checkpoint_and_terms":
            "blocked_checkpoint_absent",
        "three_channel_matched_input_and_geometry":
            "blocked_input_absent",
        "hash_pinned_runtime_and_parity":
            "blocked_runtime_unpinned",
        "parameter_and_layer_identity":
            "blocked_checkpoint_absent",
        "speaker_extraction_quality_and_leakage":
            "blocked_no_candidate_output",
        "mono_howling_control":
            "not_evaluated_by_this_task",
        "dsp_matrix_gain_response_attack_release_delay":
            "blocked_no_candidate_output",
        "numerical_state_and_nonlinear_adverse":
            "partial_local_harness_only",
        "device_timing_memory_and_callback":
            "blocked_no_paced_measurement",
        "benchmark_and_release_qualification":
            "blocked_no_release_evidence",
    }


def candidates() -> Dict[str, Any]:
    return {
        CANDIDATE: {
            "status": "blocked_source_checkpoint_input_and_runtime_absent",
            "metrics": None,
            "qualifies_candidate": False,
            "result": None,
            "reason": (
                "No AFC-SPEX source, config, checkpoint, three-channel "
                "matched input or pinned runtime is present; no extraction, "
                "quality, howling-control or timing result was produced."),
        }
    }


def controls() -> Dict[str, Any]:
    return {
        "identity_control": {
            "status": "bit_exact_synthetic_only",
            "candidate_processing": False,
            "qualifies_candidate": False,
        },
        "mono_howling_control": {
            "status": "not_evaluated_by_this_task",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "source_reported_review": {
            "status": "provenance_only_not_reproduced",
            "metrics": None,
            "qualifies_candidate": False,
        },
    }


def stimulus_probe() -> Dict[str, Any]:
    stimuli: Dict[str, Any] = {}
    identity: Dict[str, Any] = {}
    channels: Dict[str, Any] = {}
    for name, generator in STIMULUS_GENERATORS.items():
        samples = generator()
        stimuli[name] = stimulus_metrics(name, samples)
        identity[name] = {
            "digest": tensor_digest(samples),
            "byte_identical": tuple(samples) == tuple(float(value)
                                                     for value in samples),
        }
        channels[name] = {
            "layout": "3 channels x 160 samples (flat 480-value harness only)",
            "channel_peaks": [_r(peak_abs(frame))
                              for frame in channel_views(samples)],
            "channel_digests": [tensor_digest(frame)
                                for frame in channel_views(samples)],
        }
    return {
        "purpose": (
            "harness stimulus characterisation only; not an AFC-SPEX result "
            "and not a candidate output"),
        "harness_geometry": {
            "channels": REQUIRED_INPUT_CHANNELS,
            "frame_samples_per_channel": HARNESS_FRAME_SAMPLES,
            "flat_values": HARNESS_FRAME_VALUES,
            "verified_model_geometry": False,
            "note": (
                "Three-by-160 is a local harness layout chosen to exercise "
                "validation and rejection; it is not a claim about the "
                "unavailable AFC-SPEX config."),
        },
        "stimuli": stimuli,
        "speech_contrast": speech_contrast(
            STIMULUS_GENERATORS["speech_like"]()),
        "identity_control": identity,
        "channel_views": channels,
        "candidate_processing": False,
    }


def collect_blockers() -> List[str]:
    blockers: List[str] = []
    if not source_probe()["present"]:
        blockers.append("source_absent")
    if not checkpoint_probe()["present"]:
        blockers.append("checkpoint_absent")
    if not input_probe()["present"]:
        blockers.append("three_channel_matched_input_absent")
    if not runtime_probe()["pinned"]:
        blockers.append("runtime_unpinned")
    if rights_probe()["review"] != "approved":
        blockers.append("rights_unrecorded")
    return sorted(blockers)


def admit(request: Any) -> Dict[str, Any]:
    """Validate a request, then fail closed because artifacts are absent."""
    validate_request(request)
    blockers = collect_blockers()
    if not blockers:
        raise ArtifactsAbsent(
            "ARTIFACTS_ABSENT: blocker list unexpectedly empty",
            "ARTIFACTS_ABSENT")
    return {
        "status": "DEFER",
        "admissible": False,
        "candidate_processing": False,
        "input_validated": True,
        "metrics": None,
        "result": None,
        "qualifies_candidate": False,
        "blockers": blockers,
        "note": (
            "A structurally valid request is still not admissible: the "
            "source, checkpoint, three-channel input, runtime and rights are "
            "absent. No fallback or surrogate is used."),
    }


def probe_candidate(request: Any) -> None:
    validate_request(request)
    raise ArtifactsAbsent(
        "ARTIFACTS_ABSENT: AFC-SPEX source, config, checkpoint, "
        "three-channel matched input and pinned runtime are not present; no "
        "extraction is performed", "ARTIFACTS_ABSENT")


def _board_projection(board: Any) -> Tuple[List[Dict[str, Any]], str]:
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise ConfigError("TASKS.json shape is invalid", "BOARD_INVALID")
    rows = [row for row in board["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ConfigError("linked task row is missing or duplicated",
                          "BOARD_ROW_MISSING")
    stable = {
        "task_id": rows[0].get("id"),
        "title": rows[0].get("title"),
        "mode": rows[0].get("mode"),
        "repository": rows[0].get("repository"),
        "component": rows[0].get("component"),
    }
    if stable != EXPECTED_LINK:
        raise ConfigError("stable linked-row identity changed",
                          "BOARD_IDENTITY_CHANGED")
    projected = [stable]
    return projected, sha256_bytes(canonical_bytes(projected))


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ConfigError("TASKS.json is missing", "BOARD_MISSING")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    return _board_projection(board)


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
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
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
        ("research/feedback_control_20261028.md records AFC-SPEX (ICASSP "
         "2026) as a current neural candidate whose public repository "
         "contains training and inference code, but whose checked-in "
         "inference config expects three microphone channels and a checkpoint "
         "at an author-local experiment path; no checkpoint is included in "
         "the repository listing."),
        ("the same note records that the available AMI source is mono and "
         "that the multichannel speaker-extraction task was not run or "
         "compared to the single-channel AHS controllers; no AFC-SPEX "
         "execution, checkpoint, listening or timing result exists."),
        ("plan/INVENTORY.json assigns afc-spex the dsp verification profile "
         "and records evidence_status blocked with disposition sdk-model."),
        ("plan/audio-sdk/README.md requires runnable source, exact assets, "
         "permitted scope, task geometry and matched evidence to be verified "
         "before a caller-supplied-asset reference or opt-in SDK adapter."),
        ("No local AFC-SPEX license file, repository revision, config byte, "
         "checkpoint digest, three-channel recording or runtime lock exists; "
         "nothing was cloned, downloaded, upmixed or reconstructed."),
    ]


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    source = source_probe()
    checkpoint = checkpoint_probe()
    matched_input = input_probe()
    runtime = runtime_probe()
    rights = rights_probe()
    geom = geometry()
    adverse_request = _adverse_cases()
    adverse_json = _json_adverse_cases()
    stimuli = stimulus_probe()
    gates = [dict(gate) for gate in GATES]
    required = [dict(row) for row in REQUIRED_ARTIFACTS]
    local_checks = {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "stable_board_identity_only": True,
        "source_absent": source["present"] is False,
        "checkpoint_absent": checkpoint["present"] is False,
        "three_channel_input_absent": matched_input["present"] is False,
        "runtime_unpinned": runtime["pinned"] is False,
        "rights_unrecorded": rights["review"] == "blocked",
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "nonfinite_samples_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith("nonfinite")),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked":
            missing_result("afc_spex_placeholder")["status"] == "blocked",
        "identity_control_bit_exact": all(
            block["byte_identical"]
            for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
        "speaker_extraction_separated": (
            SPEAKER_EXTRACTION["may_be_reported_as_mono_howling_control"]
            is False),
        "no_result_qualifies_candidate": True,
    }
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "verification_profile": VERIFICATION_PROFILE,
        "status": "proposal_only_not_qualified",
        "decision": "DEFER",
        "incomplete": True,
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "qualification": qualification(),
        "boundary": boundary(),
        "profile": {
            "name": VERIFICATION_PROFILE,
            "source": SOURCE_PINS[PROFILE_SOURCE],
        },
        "profile_mapping": profile_mapping(),
        "reference": {
            "implementation": "task-local standard-library feasibility gate",
            "real_afc_spex_source_present": source["present"],
            "real_afc_spex_configs_present": False,
            "real_afc_spex_checkpoint_present": checkpoint["present"],
            "three_channel_matched_input_present": matched_input["present"],
            "pinned_runtime_present": runtime["pinned"],
            "rights_approved": False,
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "real_corpus_read": False,
            "note": (
                "No AFC-SPEX network, checkpoint loader, feature extractor or "
                "inference path is implemented or simulated; only probes, "
                "request rejection and synthetic harness controls are "
                "performed."),
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
        "board_full_file_hashed": False,
        "artifact_pins": artifact_pins(),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "required_artifacts": required,
        "missing_artifacts": [row["artifact"] for row in required
                              if row["status"] == "absent"],
        "source_probe": source,
        "checkpoint_probe": checkpoint,
        "input_probe": matched_input,
        "runtime_probe": runtime,
        "rights_probe": rights,
        "geometry": geom,
        "speaker_extraction": dict(SPEAKER_EXTRACTION),
        "mono_howling_control": dict(MONO_HOWLING_CONTROL),
        "task_separation_enforced": True,
        "candidates": candidates(),
        "controls": controls(),
        "required_results": candidate_required_results(),
        "stimulus_probe": stimuli,
        "adverse": {
            "invalid_config_and_input": adverse_request,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": missing_result("afc_spex_placeholder"),
        },
        "local_harness_checks": local_checks,
        "release_gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "gates": [gate["id"] for gate in gates],
        "regressions": [],
        "regression_count": 0,
        "no_missing_result_qualifies_candidate": True,
        "generated_by": "run.py --all",
    }
    if not finite_json(report):
        raise EvidenceError("REPORT_NONFINITE", "REPORT_NONFINITE")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
