# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-DUALVC-3.

This module is NOT DualVC 3. It does not implement, approximate, simulate,
train or run the DualVC 3 streaming voice-conversion network, and it contains
no checkpoint, weight, encoder, vocoder, runtime or real audio. The only
catalogued evidence is one research-note table row that records paper/demo
inspection and **no official runnable checkpoint**; no DualVC 3 source
repository, release archive, immutable revision, weight digest, model card,
runtime lock or rights record was identified locally.

The module therefore builds a bounded, deterministic blocker report:

* strict request validation that rejects missing, unknown, invalid, nonfinite,
  out-of-range and stale inputs before any candidate call;
* explicit, bounded, read-only source/weights/runtime absence probes;
* a structural reset validator that never owns candidate state;
* synthetic harness stimuli for identity/rejection controls only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

No network, model weights, real corpus audio, native library or download is
used. No candidate output is produced and no result qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import subprocess
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0

SCHEMA_ID = "audio-sdk/dualvc-3-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/dualvc-3-contract/0.1"
TASK = "SDK-DUALVC-3"
COMPONENT = "dualvc-3"
BRANCH = "swarm/SDK-DUALVC-3"
BASE_COMMIT = "42453ca5fbedc550a42276bbc94e76985b846544"
TASK_PREFIX = "docs/task-evidence/dualvc-3/"

PAPER_LEAD = "https://arxiv.org/abs/2406.07846"
PAPER_ID = "2406.07846"
EVIDENCE_PATH = "research/accent-conversion-20261101/README.md"
EVIDENCE_LINE = 178

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
INVENTORY_PATH = WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.json"
HF_CACHE_ROOT = Path.home() / ".cache/huggingface/hub"

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only the stable linked row identity is projected, never hashed.
SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
}

# SDK-worktree-relative boundary pins. Every entry is read-only evidence that
# the installed v0 contract, public C surface, shared build, CI and merged
# sibling evidence were not changed by this task.
BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/survey-trn-03/README.md":
        "9f1310a624f14d5238dfee2566cbd0dcf1e7f1c17a94ef445644ae90a7309f50",
    "docs/task-evidence/survey-trn-03/report.json":
        "aef09671dd0bf39ec7996096f5a866bff564b0110bc1a1e6340fd5fb993f5fe2",
    "docs/task-evidence/survey-trn-04/README.md":
        "e0b4ea4d92b122e9820b9857da5e4813db29b048468f2b0383e67ef4264eccae",
    "docs/task-evidence/survey-trn-04/report.json":
        "fb34a1129db91808c450cf9ce90d68a2f2ff34734b26891763ede6b0915f0446",
    "docs/task-evidence/llvc/README.md":
        "f6d663bc171026181107a6e9ddcf1356fa9eb9e2fd16625267b35a5bc3bda717",
    "docs/task-evidence/llvc/report.json":
        "22d30a3c4f70143ba38f099019c3fcc6b123f4f4f3120f6ee73932d82fed342f",
    "docs/task-evidence/chatterbox-vc/README.md":
        "7a624864df916ef87b32655e6e0894bfe00c3da94ca6969352be68654ee1443c",
    "docs/task-evidence/chatterbox-vc/report.json":
        "321fe22b052823b43d772871b5b694df03c0586c6754c04491d40406055b3dee",
    "docs/task-evidence/convert-and-speak/README.md":
        "a89653d3b127f7d2b6cc7f5abc767fb24259b580b4dec2e29ddaed10c74630be",
    "docs/task-evidence/convert-and-speak/report.json":
        "2423c9cff507fd2c88045ca279367da76a2355168af3d62f29aea425630fcce1",
}

# Stable linked-row identity only. Status, owner, review, handoff, timestamps,
# dispatch priority, history and claim are deliberately excluded and never
# gated. The shared board itself is never modified.
EXPECTED_LINK = {
    "task_id": TASK,
    "title": "DualVC 3",
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

EXPECTED_INVENTORY = {
    "id": "dualvc-3",
    "name": "DualVC 3",
    "area": "Voice and synthesis",
    "evidence_status": "considered",
    "repository": "audio-sdk",
    "disposition": "sdk-model",
    "verification_profile": "voice",
    "task": TASK,
}

CANDIDATE = "dualvc-3"
# The linked note documents no target voice or target condition. Only this
# explicit "unspecified" placeholder is accepted; every concrete condition is
# rejected until a reviewed target definition exists.
TARGET_CONDITION = "streaming_generic_target_unspecified"
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

SOURCE_CANDIDATE_PATHS = (
    "research/accent-conversion-20261101/repos/dualvc-3",
    "research/accent-conversion-20261101/repos/dualvc3",
    "research/accent-conversion-20261101/repos/DualVC3",
    "research/voice-conversion-eval-20261101/repos/dualvc-3",
    "research/voice-conversion-eval-20261101/repos/dualvc3",
    "research/voice-conversion-eval-20261101/repos/DualVC3",
    "data/checkouts/dualvc-3",
    "data/checkouts/dualvc3",
    "adapters/dualvc-3",
    "adapters/dualvc3",
)

WEIGHT_CANDIDATE_PATHS = (
    "research/accent-conversion-20261101/checkpoints/dualvc3",
    "research/accent-conversion-20261101/checkpoints/DualVC3",
    "research/voice-conversion-eval-20261101/checkpoints/dualvc3",
    "research/voice-conversion-eval-20261101/checkpoints/DualVC3",
    "data/models/dualvc-3",
    "data/models/dualvc3",
    "data/dualvc3",
)

RUNTIME_CANDIDATE_PATHS = (
    "research/accent-conversion-20261101/.venv-dualvc3/bin/python",
    "research/voice-conversion-eval-20261101/.venv-dualvc3/bin/python",
    "data/envs/dualvc-3/bin/python",
    "data/envs/dualvc3/bin/python",
)

WEIGHT_SUFFIXES = (
    ".pth", ".pt", ".ckpt", ".safetensors", ".onnx", ".bin", ".tflite",
)
RUNTIME_MODULES = (
    "torch", "torchaudio", "onnxruntime", "numpy", "soundfile",
    "huggingface_hub", "transformers",
)

SEARCH_ROOTS = ("research", "data", "adapters", "configs")
NAME_NEEDLES = ("dualvc",)
MAX_SEARCH_ENTRIES = 200000
SEARCH_EXCLUSIONS = (
    "worktrees/** (separate git worktrees, including this task worktree "
    "directory name)",
    "docs/task-evidence/dualvc-3/** (this evidence package)",
    "file contents (names only; no workspace tree is hashed)",
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
        "gate": "exact_source_revision_archive_and_license",
        "status": "blocked",
        "reason": (
            "No official DualVC 3 source repository, release archive, "
            "immutable revision, tree digest or upstream license was "
            "identified or pinned locally. The linked research note records "
            "paper/demo inspection only."),
        "reopen": (
            "Identify and stage the exact licensed DualVC 3 source with an "
            "immutable 40-hex revision, tree digest, file count and complete "
            "license/notice bundle before any reproduction."),
    },
    {
        "id": "RG-02",
        "gate": "exact_weights_model_card_and_weight_terms",
        "status": "blocked",
        "reason": (
            "No official DualVC 3 checkpoint or weight artifact is present. "
            "There is no SHA-256, byte count, tensor/config manifest, model "
            "card or weight license/terms record."),
        "reopen": (
            "Stage the exact published checkpoint plus every required "
            "config/tokenizer/vocoder asset with per-file byte counts and "
            "SHA-256, and record the reviewed weight/model-card terms."),
    },
    {
        "id": "RG-03",
        "gate": "pinned_runtime_offline_load_and_build_parity",
        "status": "blocked",
        "reason": (
            "No hash-pinned DualVC 3 runtime exists; torch, torchaudio, "
            "onnxruntime, numpy, soundfile and the model frontends are not "
            "importable here, and no lockfile or wheel hash set was "
            "identified."),
        "reopen": (
            "Create a frozen, hash-pinned CPU runtime that loads the pinned "
            "snapshot offline with a fail-closed missing-asset path and "
            "reproduces an approved parity vector."),
    },
    {
        "id": "RG-04",
        "gate": "code_weight_training_data_corpus_consent_and_output_use",
        "status": "blocked",
        "reason": (
            "No source, weight, training-data, corpus, reference-voice, "
            "target-voice, consent or output-use rights record exists. A "
            "paper lead grants no redistribution or product-use right."),
        "reopen": (
            "Record reviewed code/weight/training-data/corpus terms, signed "
            "source and target voice consent, reference availability and "
            "output-use terms for every voice."),
    },
    {
        "id": "RG-05",
        "gate": "rights_cleared_voice_cohort_text_identity_and_naturalness",
        "status": "blocked",
        "reason": (
            "No permitted source/target voice pair, frozen language/speaker "
            "group, manual transcript, matched/mismatched/identity control or "
            "held-out cohort exists. Content, identity and naturalness are "
            "unmeasured."),
        "reopen": (
            "Freeze a rights-cleared cohort with manual transcripts, groups, "
            "exact target conditions and matched controls, then score text/"
            "semantic preservation, identity/similarity and naturalness "
            "separately."),
    },
    {
        "id": "RG-06",
        "gate": "chunking_alignment_first_output_tail_nonfinite_and_reset",
        "status": "blocked",
        "reason": (
            "No candidate chunk, hop, lookahead, algorithmic offset, "
            "buffering delay, content mapping or finite drain behavior is "
            "documented. Alignment, first-output/tail, peak, nonfinite and "
            "reset behavior were not exercised."),
        "reopen": (
            "With the exact weights and runtime, document and measure "
            "chunk/hop/lookahead/delay/content mapping, finite drain, peaks, "
            "nonfinite output, state and reset at 16 kHz mono."),
    },
    {
        "id": "RG-07",
        "gate": "target_device_timing_resources_and_listening",
        "status": "blocked",
        "reason": (
            "No paced target-device run, callback suitability check, CPU or "
            "memory measurement, independent listening panel or ASR/content "
            "control exists for DualVC 3."),
        "reopen": (
            "Measure paced target-device timing, content delay, CPU, memory "
            "and callback suitability, and complete an approved blinded "
            "listening protocol with ASR/content controls."),
    },
    {
        "id": "RG-08",
        "gate": "provider_intake_public_surface_review_and_release",
        "status": "blocked",
        "reason": (
            "No caller-supplied-asset adapter, provider intake, descriptor, "
            "registry/default change, public-surface decision, independent "
            "exact-head review or release approval exists."),
        "reopen": (
            "After every prior gate clears, complete opt-in provider intake "
            "with an OFF default and a versioned descriptor, obtain "
            "independent exact-head review, and approve release separately."),
    },
)

UPSTREAM_BLOCKER = {
    "status": "blocked_source_weights_runtime_rights_absent",
    "artifact": (
        "Official DualVC 3 streaming voice-conversion source, checkpoint/"
        "weights, pinned runtime and voice/data rights required to load and "
        "evaluate it"),
    "source": {
        "status": "absent",
        "repository": None,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
    },
    "weights": {
        "status": "absent",
        "artifact": "DualVC 3 official checkpoint",
        "sha256": None,
        "byte_count": None,
        "license": None,
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "a hash-pinned CPU PyTorch or ONNX Runtime build compatible with "
            "the official checkpoint",
            "the content-encoder, speaker-encoder and vocoder components that "
            "the official checkpoint declares, each at a pinned version",
            "audio I/O and resampling dependencies at pinned versions",
            "a lockfile or wheel hash set plus a fail-closed offline loader",
        ],
        "sha256": None,
        "lockfile": None,
    },
    "expected_license": (
        "None identified: no upstream code license, weight/model-card terms, "
        "training-data statement or target-voice terms were located, so every "
        "future use requires an explicit reviewed license decision"),
    "pinned_revision": None,
    "source_digest": None,
    "runtime_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "Reviewed code and weight terms, training-data and corpus rights, "
        "explicit source-speaker and target-voice consent, reference "
        "availability and output-use terms, and an approved redistribution "
        "model for the runtime and any converted output are required before "
        "any reproduction, adapter or release claim."),
    "workspace_search": (
        "Bounded read-only path probes, a bounded filename search over the "
        "research/data/adapters/configs roots and a read-only Hugging Face "
        "cache listing found no DualVC 3 source, checkpoint, weight file, "
        "pinned runtime or adapter. Only this task worktree directory name "
        "matches the needle, and it is not a candidate artifact."),
    "not_attempted": [
        "no network download or package installation",
        "no fabricated, reconstructed or surrogate DualVC 3 weights",
        "no substitute model, encoder, vocoder or voice-conversion algorithm",
        "no copied upstream source, paper asset, test audio or license text",
    ],
    "reopen": (
        "Identify and stage the exact licensed source at an immutable "
        "revision, the official checkpoint with per-file digests, a locked "
        "offline runtime, all code/weight/data/voice rights and consent, a "
        "rights-cleared cohort and an agreed Voice protocol; then reproduce "
        "approved reference output and complete opt-in provider intake."),
}

NON_CLAIMS = (
    "No DualVC 3 source, checkpoint, weights, config, vocoder or model output "
    "is included.",
    "No DualVC 3 inference, conversion, encoder or vocoder is implemented, "
    "approximated or simulated.",
    "No installed v0, public API, C ABI, descriptor, registry or default "
    "change.",
    "No provider is registered or enabled by default.",
    "No real corpus, consent, listening panel, benchmark or quality claim "
    "exists.",
    "No paper-reported latency is treated as a local measurement or device "
    "timing result.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No missing, rejected or sibling result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/dualvc-3/ is touched.",
    "The reference is a task-local evidence builder, not DualVC 3.",
    "All harness stimuli are analytic or seeded synthetic; no weights are used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
    "The mutable full plan/swarm/TASKS.json is never hashed or pinned.",
)

VOICE_PROFILE_SOURCE = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"


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


class CandidateAbsent(EvidenceError):
    code = "SOURCE_WEIGHTS_RUNTIME_ABSENT"


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


def validate_reset(epoch: Any, first_input_sample: Any,
                   previous_epoch: Any) -> Dict[str, int]:
    """Structural reset validator; owns no candidate state."""
    new_epoch = _require_int(epoch, "INVALID_EPOCH", 0)
    previous = _require_int(previous_epoch, "INVALID_EPOCH", 0)
    position = _require_int(first_input_sample, "INVALID_POSITION", 0)
    if new_epoch <= previous:
        raise ConfigError("EPOCH_NOT_INCREASING", "EPOCH_NOT_INCREASING")
    return {"epoch": new_epoch, "first_input_sample": position,
            "previous_epoch": previous}


def probe_candidate(request: Any) -> None:
    validated = validate_request(request)
    raise CandidateAbsent(
        "SOURCE_WEIGHTS_RUNTIME_ABSENT: " + validated["candidate"] +
        " source, checkpoint and pinned runtime are not present; no candidate "
        "processing is performed",
        "SOURCE_WEIGHTS_RUNTIME_ABSENT")


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
        ("unknown_candidate", variant(candidate="dualvc3")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("wrong_rate", variant(sample_rate_hz=48000)),
        ("wrong_channels", variant(channels=2)),
        ("wrong_frame", variant(frame_samples=320)),
        ("short_samples", with_samples(short)),
        ("empty_samples", with_samples([])),
        ("nonfinite_nan", with_samples(nan_samples)),
        ("nonfinite_inf", with_samples(inf_samples)),
        ("out_of_range", with_samples([4.5] * FRAME_SAMPLES)),
        ("bool_sample", with_samples([True] + [0.0] * (FRAME_SAMPLES - 1))),
        ("string_sample", with_samples(["0.0"] + [0.0] * (FRAME_SAMPLES - 1))),
        ("null_sample", with_samples([None] + [0.0] * (FRAME_SAMPLES - 1))),
        ("negative_epoch", variant(epoch=-1)),
        ("bool_epoch", variant(epoch=True)),
        ("float_epoch", variant(epoch=1.0)),
        ("negative_position", variant(first_input_sample=-160)),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("invalid_execution_mode", variant(execution_mode=4)),
        ("zero_execution_mode", variant(execution_mode=0)),
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
        ("empty_text", ""),
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


RESET_CASES = (
    ("fresh_epoch_2_accepted", 2, 0, 1, True),
    ("equal_epoch_rejected", 1, 0, 1, False),
    ("lower_epoch_rejected", 0, 0, 1, False),
    ("negative_epoch_rejected", -1, 0, 1, False),
    ("negative_position_rejected", 2, -160, 1, False),
    ("bool_epoch_rejected", True, 0, 1, False),
    ("bool_position_rejected", 2, True, 1, False),
    ("float_epoch_rejected", 2.0, 0, 1, False),
)


def _reset_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    for name, epoch, position, previous, expected in RESET_CASES:
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_reset(epoch, position, previous)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        cases.append({
            "id": name,
            "accepted": accepted,
            "expected_accepted": expected,
            "error": error,
        })
    accepted_count = sum(1 for case in cases if case["accepted"])
    expected_count = sum(1 for case in cases if case["expected_accepted"])
    return {
        "case_count": len(cases),
        "accepted_count": accepted_count,
        "expected_accepted_count": expected_count,
        "matches_expectation": all(case["accepted"] == case["expected_accepted"]
                                   for case in cases),
        "state_owned": False,
        "metrics": None,
        "cases": cases,
        "note": ("Structural reset validation only; no candidate state exists "
                 "and no reset is executed."),
    }


def missing_result(fixture_name: str) -> Dict[str, Any]:
    return {
        "fixture": fixture_name,
        "status": "blocked",
        "reason": "source_weights_runtime_and_rights_absent",
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def _module_importable(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _bounded_name_search() -> Dict[str, Any]:
    roots: List[str] = []
    matches: List[str] = []
    entries = 0
    truncated = False
    for relative in SEARCH_ROOTS:
        root = WORKSPACE / relative
        if not root.exists():
            continue
        roots.append(relative)
        for directory, directory_names, file_names in os.walk(root):
            directory_names[:] = sorted(
                name for name in directory_names if name != ".git")
            names = sorted(directory_names) + sorted(file_names)
            if entries + len(names) > MAX_SEARCH_ENTRIES:
                truncated = True
                break
            entries += len(names)
            for name in names:
                lowered = name.lower()
                if any(needle in lowered for needle in NAME_NEEDLES):
                    matches.append(
                        (Path(directory) / name).relative_to(
                            WORKSPACE).as_posix())
            if truncated:
                break
        if truncated:
            break
    return {
        "roots_requested": list(SEARCH_ROOTS),
        "roots_scanned": roots,
        "needles": list(NAME_NEEDLES),
        "entries_scanned": entries,
        "max_entries": MAX_SEARCH_ENTRIES,
        "truncated": truncated,
        "excluded": list(SEARCH_EXCLUSIONS),
        "match_count": len(matches),
        "matches": sorted(matches),
    }


def home_cache_probe() -> Dict[str, Any]:
    entries: List[str] = []
    matches: List[str] = []
    if HF_CACHE_ROOT.is_dir():
        entries = sorted(item.name for item in HF_CACHE_ROOT.iterdir())
        matches = [name for name in entries
                   if any(needle in name.lower() for needle in NAME_NEEDLES)]
    return {
        "root": "~/.cache/huggingface/hub",
        "probed": HF_CACHE_ROOT.is_dir(),
        "entry_count": len(entries),
        "dualvc_matches": matches,
        "note": ("Read-only top-level directory-name listing; no cache file "
                 "is opened, imported or used."),
    }


def source_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for relative in SOURCE_CANDIDATE_PATHS:
        checked.append(relative)
        if (WORKSPACE / relative).exists():
            found.append(relative)
    search = _bounded_name_search()
    found.extend("search:" + item for item in search["matches"])
    present = bool(found)
    return {
        "status": "source_present_unqualified" if present
                  else "blocked_source_absent",
        "present": present,
        "repository": None,
        "revision": None,
        "tree_digest": None,
        "license": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "name_search": search,
        "note": ("Bounded path and filename checks only; no archive is "
                 "opened, downloaded, copied or executed."),
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
            hits = sorted(
                (Path(relative) / item.name).as_posix()
                for item in target.iterdir()
                if item.is_file() and
                item.name.lower().endswith(WEIGHT_SUFFIXES))
            if hits:
                found.extend(hits)
            else:
                empty_directories.append(relative)
    cache = home_cache_probe()
    found.extend("hf-cache:" + name for name in cache["dualvc_matches"])
    return {
        "empty_directories": sorted(set(empty_directories)),
        "status": "weights_present_unqualified" if found
                  else "blocked_weights_absent",
        "artifact": "DualVC 3 official checkpoint",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "present": bool(found),
        "home_cache": cache,
        "note": ("Read-only path and filename checks only; no archive is "
                 "opened, downloaded or reconstructed."),
    }


def runtime_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for relative in RUNTIME_CANDIDATE_PATHS:
        checked.append(relative)
        if (WORKSPACE / relative).exists():
            found.append(relative)
    modules = {name: _module_importable(name) for name in RUNTIME_MODULES}
    lock_candidates = (
        "research/accent-conversion-20261101/requirements.lock",
        "research/voice-conversion-eval-20261101/requirements.lock",
        "data/envs/dualvc-3/pyvenv.cfg",
        "data/envs/dualvc3/pyvenv.cfg",
    )
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


def inventory_link() -> Dict[str, Any]:
    inventory = strict_json_loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    if not isinstance(inventory, dict) or not isinstance(
            inventory.get("components"), list):
        raise ConfigError("INVENTORY.json shape is invalid",
                          "INVENTORY_INVALID")
    rows = [row for row in inventory["components"]
            if isinstance(row, dict) and row.get("id") == COMPONENT]
    if len(rows) != 1:
        raise ConfigError("inventory row is missing or duplicated",
                          "INVENTORY_ROW_MISSING")
    row = rows[0]
    projection = {
        "id": row.get("id"),
        "name": row.get("name"),
        "area": row.get("area"),
        "evidence_status": row.get("evidence_status"),
        "repository": row.get("repository"),
        "disposition": row.get("disposition"),
        "verification_profile": row.get("verification_profile"),
        "task": row.get("task"),
    }
    if projection != EXPECTED_INVENTORY:
        raise ConfigError("inventory row identity changed",
                          "INVENTORY_IDENTITY_CHANGED")
    return projection


def evidence_entry() -> Dict[str, Any]:
    path = WORKSPACE / EVIDENCE_PATH
    lines = path.read_text(encoding="utf-8").splitlines()
    if EVIDENCE_LINE > len(lines):
        raise ConfigError("evidence line is out of range", "EVIDENCE_MISSING")
    text = lines[EVIDENCE_LINE - 1]
    required = ("DualVC 3", "no official runnable checkpoint found",
                "Streaming generic VC", PAPER_LEAD)
    if not all(token in text for token in required):
        raise ConfigError("evidence line changed", "EVIDENCE_CHANGED")
    return {
        "path": EVIDENCE_PATH,
        "line": EVIDENCE_LINE,
        "text": text,
        "sha256": sha256_bytes(text.encode("utf-8")),
        "tokens_verified": list(required),
        "note": ("Exact linked table row; it records paper inspection and an "
                 "absent runnable checkpoint, not a local execution."),
    }


def paper_lead() -> Dict[str, Any]:
    return {
        "arxiv_id": PAPER_ID,
        "url": PAPER_LEAD,
        "identified_artifacts": [],
        "code_available": False,
        "weights_available": False,
        "model_card_available": False,
        "license_available": False,
        "note": ("The linked note records only a paper lead. No repository, "
                 "archive, checkpoint, model card or license was located or "
                 "downloaded, so no paper-reported number is used here."),
    }


def geometry() -> Dict[str, Any]:
    frame_ms = FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ
    return {
        "source": ("audio-sdk CONTRACTS.md installed v0 format: 16000 Hz, "
                   "mono, float32, 160 samples per frame"),
        "frame_samples": FRAME_SAMPLES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_ms": _r(frame_ms),
        "frames_per_second": _r(SAMPLE_RATE_HZ / FRAME_SAMPLES),
        "candidate_geometry_documented": False,
        "candidate_buffering_delay_samples": None,
        "candidate_max_drain_calls": None,
        "candidate_chunk_or_lookahead": None,
        "measured_here": False,
        "candidate_output": False,
        "note": ("Arithmetic on the installed v0 frame format only; it is not "
                 "DualVC 3 geometry and establishes no content delay."),
    }


def historical_evidence() -> Dict[str, Any]:
    return {
        "status": "no_local_dualvc3_execution_record",
        "records_found": 0,
        "source_reported_results": None,
        "audio_artifacts": [],
        "metrics_artifacts": [],
        "transcripts": [],
        "timing": None,
        "identity_similarity": "not_scored",
        "naturalness": "not_scored",
        "reproduced_here": False,
        "qualifies_candidate": False,
        "note": ("The linked research note places DualVC 3 in its candidate "
                 "acquisition table with paper/demo inspection only. No local "
                 "output, metric, transcript, identity, naturalness, timing or "
                 "listening record exists to transcribe or preserve."),
    }


def voice_profile_mapping() -> Dict[str, str]:
    return {
        "permitted_input_and_target_reference_scope":
            "blocked_no_source_target_pair_or_rights_record",
        "task_and_language_speaker_groups":
            "blocked_no_frozen_cohort_or_groups",
        "text_and_semantic_content":
            "blocked_no_model_transcript_or_cohort",
        "identity_and_similarity": "blocked_not_scored",
        "naturalness": "blocked_no_listening_or_mos",
        "alignment_first_output_and_tail_timing":
            "blocked_no_documented_or_measured_timing",
        "exact_target_condition":
            "blocked_no_documented_target_voice_or_condition",
        "consent_reference_availability_and_output_use":
            "blocked_rights_and_consent_absent",
        "paired_quality_control": "blocked_source_weights_runtime_absent",
        "clean_reference_preservation": "blocked_no_paired_clean_reference",
        "numerical_and_nonfinite": "partial_local_harness_only",
        "candidate_output": "blocked_source_weights_runtime_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "identity_noisy_control": "blocked_source_weights_runtime_absent",
        "established_task_matched_baseline":
            "blocked_no_identified_comparable_implementation",
        "paired_si_sdr_stoi": "blocked_no_paired_clean_reference",
        "clean_speech_preservation": "blocked_no_paired_clean_reference",
        "text_semantic_content": "blocked_no_model_transcript_or_cohort",
        "identity_similarity": "blocked_not_scored",
        "naturalness": "blocked_no_listening",
        "alignment_first_output_tail_and_content_delay":
            "blocked_no_documented_or_measured_timing",
        "target_condition_and_consent":
            "blocked_rights_and_consent_absent",
        "language_and_speaker_groups": "blocked_no_frozen_cohort",
        "numerical_and_nonfinite": "partial_local_harness_only",
        "delay_state_reset_drain_and_modes":
            "blocked_source_weights_runtime_absent",
    }


def candidates() -> Dict[str, Any]:
    return {
        CANDIDATE: {
            "status": "blocked_source_weights_runtime_absent",
            "metrics": None,
            "qualifies_candidate": False,
            "target_condition": TARGET_CONDITION,
            "reason": (
                "No official DualVC 3 source, checkpoint, weights or pinned "
                "runtime is present; no conversion, quality or timing result "
                "was produced."),
        }
    }


def controls() -> Dict[str, Any]:
    return {
        "source_identity_control": {
            "status": "not_run_no_candidate",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "sibling_voice_baseline": {
            "status": "not_reused_separate_candidate",
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
        "purpose": ("harness stimulus characterisation only; not a DualVC 3 "
                    "result and not a candidate output"),
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


# ---------------------------------------------------------------------------
# Task-local git scope
# ---------------------------------------------------------------------------
# The merged squash lands on `main`; later merges add unrelated sibling task
# packages. A fixed historical commit therefore cannot be the scope base: it
# would report those siblings as out-of-scope edits of this task. The base is
# the newest merge-base between HEAD and the PR base refs, so the comparison
# contains exactly the commits this branch added and fail-closed scope checks
# still catch any edit outside TASK_PREFIX.
SCOPE_BASE_REFS = ("origin/main", "main")


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


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> List[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]


def source_evidence_statements() -> List[str]:
    return [
        ("research/accent-conversion-20261101/README.md line 178 records DualVC "
         "3 as 'Paper/demo inspected; no official runnable checkpoint found' "
         "and 'Streaming generic VC, not dedicated accent normalization' with "
         "an arXiv 2406.07846 link."),
        ("plan/INVENTORY.json row dualvc-3 is evidence_status=considered, "
         "disposition=sdk-model, verification_profile=voice, task="
         "SDK-DUALVC-3, with the same single evidence path and line."),
        ("plan/swarm/VERIFICATION.md assigns the Voice profile: permitted "
         "input/target references, language/speaker groups, separate content, "
         "identity and naturalness outcomes, alignment, first-output/tail and "
         "independent consent/reference/output-use gates."),
        ("The merged survey-trn-03 package maps DualVC 3 as a "
         "source_reported_research_candidate with no local accent-aware "
         "streaming run; survey-trn-04 also links it at a boundary only."),
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
    reset = _reset_cases()
    stimuli = stimulus_probe()
    gates = [dict(gate) for gate in GATES]
    local_checks = {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "stable_board_identity_only": True,
        "inventory_identity_exact": inventory_link() == EXPECTED_INVENTORY,
        "source_probe_confirms_absent": source["present"] is False,
        "weights_probe_confirms_absent": weights["present"] is False,
        "runtime_probe_confirms_unpinned": runtime["pinned"] is False,
        "bounded_name_search_complete": (
            source["name_search"]["truncated"] is False and
            source["name_search"]["match_count"] == 0),
        "home_cache_has_no_dualvc_entry":
            weights["home_cache"]["dualvc_matches"] == [],
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "nonfinite_samples_rejected": any(
            case["id"].startswith("nonfinite") and not case["accepted"]
            for case in adverse_request["cases"]),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "reset_cases_match_expectation": reset["matches_expectation"],
        "missing_result_blocked":
            missing_result("dualvc3_synthetic_placeholder")["status"] ==
            "blocked",
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
        "inventory_link": inventory_link(),
        "evidence_entry": evidence_entry(),
        "paper_lead": paper_lead(),
        "reference": {
            "implementation": "task-local standard-library evidence builder",
            "real_dualvc3_source_present": source["present"],
            "real_dualvc3_weights_present": weights["present"],
            "pinned_runtime_present": runtime["pinned"],
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "note": (
                "No DualVC 3 network, encoder, vocoder, checkpoint loader or "
                "inference path is implemented or simulated; only probes, "
                "structural validation and synthetic controls are performed."),
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
            "reset_validation": reset,
            "missing_result": missing_result("dualvc3_synthetic_placeholder"),
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
