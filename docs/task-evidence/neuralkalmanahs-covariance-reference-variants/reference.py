# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility gate for the NeuralKalmanAHS variants.

This module is NOT NeuralKalmanAHS. It contains no upstream source, model code,
checkpoint, weight, configuration, license text, runtime, corpus recording or
candidate output. A bounded read-only search of named workspace paths finds no
local ``NeuralKalmanAHS`` or ``AHS_2023`` checkout, no trained covariance or
reference variant, no pinned deep-learning runtime, no matched closed-loop
cohort and no locally approved license text. The pinned research note records
that the public repositories expose README/demo HTML, CSS and audio only, with
no source implementation or checkpoints, and that no release assets were listed
for NeuralKalmanAHS.

The module therefore builds a fail-closed feasibility blocker report:

* strict caller-supplied-asset request validation at the only locally pinned
  geometry, the installed-v0 16 kHz / mono / 160-sample harness format;
* explicit source, checkpoint, runtime, license, cohort and rights probes;
* a covariance/reference integration-variant split that is never collapsed;
* an admission gate that rejects every structurally valid request because the
  required artifacts and rights are absent;
* analytic or seeded synthetic harness stimuli for rejection and identity
  controls only;
* author-reported closed-loop results retained as provenance only, never as a
  local measurement or a qualification;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

Nothing is downloaded, cloned, installed, extracted, ported, reconstructed or
simulated. No candidate audio output is produced. No result qualifies either
integration variant, and no author-reported score is reproduced.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
from typing import Any, Iterable, Sequence

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", str(HERE.parents[5]))).resolve()
TASK_PREFIX = (
    "docs/task-evidence/neuralkalmanahs-covariance-reference-variants/")

TASK = "SDK-NEURALKALMANAHS-COVARIANCE-REFERENCE-VARIANTS"
TITLE = "NeuralKalmanAHS covariance/reference variants"
COMPONENT = "neuralkalmanahs-covariance-reference-variants"
COMPONENT_ID = "neuralkalmanahs-covariance-reference-variants"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "dsp"
PROFILE_KEY = "DSP"
STATUS = "proposal_only_not_qualified"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
QUALIFICATION_STATUS = "not_qualified"
FORMAT = "sdk-task-evidence/0.1"
WRITE_SCOPE = TASK_PREFIX + " only"
CONTRACT_ID = (
    "audio-sdk/neuralkalmanahs-covariance-reference-variants-readiness/0.1")
CONTRACT_SCHEMA_ID = (
    "audio-sdk/neuralkalmanahs-covariance-reference-variants-contract/0.1")
REPORT_SCHEMA_ID = (
    "audio-sdk/neuralkalmanahs-covariance-reference-variants-report/0.1")
BASE_COMMIT = "feb342c735740f32d64a668cf2234e488cdcdbfe"
BRANCH = "swarm/SDK-NEURALKALMANAHS-COVARIANCE-REFERENCE-VARIANTS"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-NEURALKALMANAHS-COVARIANCE-REFERENCE-VARIANTS")
REVIEWER = "reviewer-NEURALKALMANAHS-COVARIANCE-REFERENCE-VARIANTS"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

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
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
STABLE_TASK_FIELDS = (
    "id", "title", "component", "mode", "repository", "depends_on")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "write_scope", "deliverable", "acceptance",
    "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)
PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
INVENTORY_REL = "audio-benchmark-platform/plan/INVENTORY.json"
PLAN_NOTE = (
    "Distinguish covariance and reference integration. The local source review "
    "found demo materials only.")

GATE_IDS = tuple("RG-%02d" % index for index in range(1, 9))
ARTIFACT_IDS = tuple("ART-%02d" % index for index in range(1, 8))
BLOCKER_IDS = tuple("BLK-%02d" % index for index in range(1, 7))

# Installed v0 format. This is the unchanged public baseline and the only
# locally pinned harness geometry. It is not evidence of candidate geometry.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
ABI_MAJOR = 0
ABI_MINOR = 1

HARNESS_FRAME_VALUES = CHANNELS * FRAME_SAMPLES
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0
MAX_EXTERNAL_ASSET_BYTES = 536870912

SOURCE_REPOSITORIES = (
    "https://github.com/YIXUANZ/NeuralKalmanAHS",
    "https://github.com/YIXUANZ/AHS_2023",
)
PAPER_URL = "https://www.isca-archive.org/interspeech_2023/zhang23q_interspeech.html"
RESEARCH_URL = "https://www.isca-archive.org/interspeech_2024/zhang24_interspeech.html"
JOURNAL_URL = "https://haozhang6720.github.io/doc/papers/AHS_journal_2024.pdf"
PROJECT_URL = "https://yixuanz.github.io/NeuralKalmanAHS/"
COMPARISON_STATUS = (
    "blocked_source_checkpoint_runtime_rights_and_cohort_absent")

VARIANT_IDS = ("covariance", "reference")
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)
REQUEST_KEYS = frozenset({
    "candidate", "integration_variant", "sample_rate_hz", "channels",
    "frame_samples", "samples", "epoch", "first_input_sample", "lifecycle",
    "execution_mode", "checkpoint_sha256", "runtime_lock_sha256", "asset_bytes",
})

LOCAL_MANIFEST_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})

NON_CLAIMS = [
    "No NeuralKalmanAHS source, model code, configuration, checkpoint, weight or license text is included.",
    "No covariance-integration or reference-integration model, Kalman filter, neural network or adapter is implemented, approximated, simulated or run.",
    "No author-reported SDR, PESQ or other paper value is reproduced, rescaled or presented as a local measurement.",
    "No installed v0, public API, C ABI, descriptor, registry or default change exists.",
    "No provider is registered or enabled by default, and there is no automatic discovery or fallback.",
    "No real corpus, checkpoint, fixture, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No source-reported characteristic is presented as a local measurement.",
    "No missing, rejected or source-reported result qualifies either integration variant.",
]

INVARIANTS = [
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only " + TASK_PREFIX + " is touched.",
    "The reference is a task-local feasibility gate, not NeuralKalmanAHS.",
    "Covariance and reference integration variants stay separate and neither is inferred.",
    "No candidate sample rate, frame, hop, channel, Kalman state or network structure is inferred.",
    "All harness stimuli are analytic or seeded synthetic; no model or corpus is used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Author-reported results are provenance only and never qualify either variant.",
    "Only stable linked-row identity enters canonical bytes or gates.",
]

SOURCE_CANDIDATE_PATHS = (
    "data/checkouts/NeuralKalmanAHS",
    "data/checkouts/AHS_2023",
    "data/checkouts/neuralkalmanahs",
    "third_party/NeuralKalmanAHS",
    "third_party/AHS_2023",
    "research/NeuralKalmanAHS",
    "research/AHS_2023",
    "research/repos/NeuralKalmanAHS",
    "research/repos/AHS_2023",
    "~/code/NeuralKalmanAHS",
    "~/projects/NeuralKalmanAHS",
)
SOURCE_MARKERS = (".py", ".md")

CHECKPOINT_CANDIDATE_PATHS = (
    "data/models/NeuralKalmanAHS",
    "data/checkpoints/NeuralKalmanAHS",
    "data/weights/NeuralKalmanAHS",
    "data/models/covariance-variant",
    "data/models/reference-variant",
    "research/NeuralKalmanAHS/checkpoints",
    "research/repos/NeuralKalmanAHS/checkpoints",
    "~/models/NeuralKalmanAHS",
)
CHECKPOINT_MARKERS = (
    ".pt", ".pth", ".ckpt", ".onnx", ".safetensors", ".bin", ".pkl",
)

RUNTIME_CANDIDATE_PATHS = (
    "data/envs/NeuralKalmanAHS",
    "data/envs/neuralkalmanahs",
    "data/runtime/NeuralKalmanAHS",
    "research/NeuralKalmanAHS/runtime",
)
RUNTIME_LOCK_CANDIDATES = (
    "data/envs/NeuralKalmanAHS/requirements.lock",
    "data/envs/neuralkalmanahs/requirements.lock",
    "data/runtime/NeuralKalmanAHS/requirements.lock",
    "research/NeuralKalmanAHS/runtime/requirements.lock",
)

COHORT_CANDIDATE_PATHS = (
    "data/corpora/NeuralKalmanAHS",
    "data/corpora/neuralkalmanahs",
    "data/fixtures/NeuralKalmanAHS",
    "research/NeuralKalmanAHS/cohort",
    "research/NeuralKalmanAHS/closed-loop",
)
COHORT_MARKERS = (".wav", ".flac", ".npy", ".json")

README_MARKERS = {
    "source": ("<!-- DIGEST_TABLE_SOURCE_START -->",
               "<!-- DIGEST_TABLE_SOURCE_END -->"),
    "boundary": ("<!-- DIGEST_TABLE_BOUNDARY_START -->",
                 "<!-- DIGEST_TABLE_BOUNDARY_END -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}


class EvidenceError(ValueError):
    """Base error with a stable machine-readable code."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
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


def _reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError("DUPLICATE_KEY: " + key, "DUPLICATE_KEY")
        result[key] = value
    return result


def _reject_constant(token: str):
    raise EvidenceError("NONFINITE_CONSTANT: " + token, "NONFINITE_CONSTANT")


def assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise EvidenceError("FLOAT_NOT_ALLOWED", "FLOAT_NOT_ALLOWED")
    if isinstance(value, dict):
        for item in value.values():
            assert_no_float(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            assert_no_float(item)


def loads_strict(payload: str) -> dict:
    try:
        value = json.loads(payload, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise EvidenceError("INVALID_JSON: " + str(error), "INVALID_JSON")
    if not isinstance(value, dict):
        raise EvidenceError("JSON_NOT_OBJECT", "JSON_NOT_OBJECT")
    assert_no_float(value)
    return value


def read_strict_json(path: Path) -> dict:
    return loads_strict(Path(path).read_text(encoding="utf-8"))


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def fixed(value: float, places: int = 9) -> str:
    return format(float(value), "." + str(places) + "f")


def tensor_digest(samples: Iterable[float]) -> str:
    digest = hashlib.sha256()
    for value in samples:
        digest.update(struct.pack("<f", float(value)))
    return digest.hexdigest()


def peak_abs(samples: Iterable[float]) -> float:
    return max((abs(float(value)) for value in samples), default=0.0)


def rms(samples: Sequence[float]) -> float:
    if not samples:
        raise EvidenceError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    total = math.fsum(float(value) * float(value) for value in samples)
    return math.sqrt(total / len(samples))


def db_ratio(numerator: float, denominator: float) -> float:
    if numerator <= 0.0 or denominator <= 0.0:
        raise EvidenceError("NONPOSITIVE_RMS", "NONPOSITIVE_RMS")
    return 20.0 * math.log10(numerator / denominator)


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield (state / 4294967296.0) * 2.0 - 1.0


def silence(length: int = HARNESS_FRAME_VALUES) -> tuple:
    return (0.0,) * length


def impulse(length: int = HARNESS_FRAME_VALUES,
            position: int = HARNESS_FRAME_VALUES // 2,
            amplitude: float = 0.5) -> tuple:
    if not 0 <= position < length:
        raise EvidenceError("INVALID_STIMULUS", "INVALID_STIMULUS")
    values = [0.0] * length
    values[position] = amplitude
    return tuple(values)


def step(length: int = HARNESS_FRAME_VALUES,
         position: int = HARNESS_FRAME_VALUES // 2,
         amplitude: float = 0.25) -> tuple:
    if not 0 <= position <= length:
        raise EvidenceError("INVALID_STIMULUS", "INVALID_STIMULUS")
    return tuple(0.0 if index < position else amplitude
                 for index in range(length))


def sweep(length: int = HARNESS_FRAME_VALUES, start_hz: float = 200.0,
          end_hz: float = 3000.0, amplitude: float = 0.3) -> tuple:
    if length <= 0 or start_hz <= 0.0 or end_hz <= 0.0:
        raise EvidenceError("INVALID_STIMULUS", "INVALID_STIMULUS")
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
                seed: int = 20261126) -> tuple:
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


def stimulus_metrics(name: str, samples: Sequence[float]) -> dict:
    if not samples:
        raise EvidenceError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    peak = 0.0
    nonfinite = 0
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise EvidenceError("INVALID_SAMPLE_TYPE: " + str(index),
                                "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            nonfinite += 1
            continue
        peak = max(peak, abs(number))
    if nonfinite:
        raise EvidenceError("NONFINITE_SAMPLE", "NONFINITE_SAMPLE")
    if peak > MAX_ABS_STIMULUS:
        raise EvidenceError("STIMULUS_OUT_OF_RANGE", "OUT_OF_RANGE")
    return {
        "name": name,
        "sample_count": len(samples),
        "peak_abs": fixed(peak),
        "rms": fixed(rms([float(value) for value in samples])),
        "nonfinite_count": 0,
        "digest": tensor_digest([float(value) for value in samples]),
    }


def speech_contrast(samples: Sequence[float]) -> dict:
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
        "voiced_rms": fixed(voiced_rms),
        "pause_rms": fixed(pause_rms),
        "voiced_to_pause_db": fixed(db_ratio(voiced_rms, pause_rms)),
        "proxy": "source-anchored voiced/pause RMS contrast; not intelligibility",
    }


def _validate_sample_list(samples: Any, expected: int) -> list:
    if not isinstance(samples, (list, tuple)):
        raise EvidenceError("SAMPLES_NOT_A_LIST", "INVALID_SAMPLE_TYPE")
    if not samples:
        raise EvidenceError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    if len(samples) != expected:
        raise EvidenceError("WRONG_SAMPLE_COUNT", "WRONG_SAMPLE_COUNT")
    result = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise EvidenceError("INVALID_SAMPLE_TYPE: " + str(index),
                                "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            raise EvidenceError("NONFINITE_SAMPLE: " + str(index),
                                "NONFINITE_SAMPLE")
        if abs(number) > MAX_ABS_INPUT:
            raise EvidenceError("SAMPLE_OUT_OF_RANGE: " + str(index),
                                "OUT_OF_RANGE")
        result.append(number)
    return result


def _require_int(value: Any, code: str,
                 minimum: int | None = None,
                 maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise EvidenceError(code, code)
    if minimum is not None and value < minimum:
        raise EvidenceError(code, code)
    if maximum is not None and value > maximum:
        raise EvidenceError(code, code)
    return value


def _optional_digest(value: Any, code: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) != 64:
        raise EvidenceError(code, code)
    if any(character not in "0123456789abcdef" for character in value):
        raise EvidenceError(code, code)
    return value


def validate_request(request: Any) -> dict:
    """Validate a caller-supplied-asset request; never runs a candidate."""
    if not isinstance(request, dict):
        raise EvidenceError("INVALID_REQUEST", "INVALID_REQUEST")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise EvidenceError("UNKNOWN_FIELD: " + ",".join(unknown),
                            "UNKNOWN_FIELD")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise EvidenceError("MISSING_FIELD: " + ",".join(missing),
                            "MISSING_FIELD")
    if request["candidate"] != COMPONENT_ID:
        raise EvidenceError("UNKNOWN_CANDIDATE", "UNKNOWN_CANDIDATE")
    variant = request["integration_variant"]
    if not isinstance(variant, str) or variant not in VARIANT_IDS:
        raise EvidenceError("INVALID_INTEGRATION_VARIANT",
                            "INVALID_INTEGRATION_VARIANT")
    rate = _require_int(request["sample_rate_hz"], "INVALID_RATE", 1)
    if rate != SAMPLE_RATE_HZ:
        raise EvidenceError("RATE_NOT_DECLARED", "RATE_NOT_DECLARED")
    channels = _require_int(request["channels"], "WRONG_CHANNELS", 1)
    if channels != CHANNELS:
        raise EvidenceError("WRONG_CHANNELS", "WRONG_CHANNELS")
    frame_samples = _require_int(request["frame_samples"], "INVALID_FRAME", 1,
                                 4096)
    if frame_samples != FRAME_SAMPLES:
        raise EvidenceError("WRONG_DECLARED_FRAME", "WRONG_DECLARED_FRAME")
    samples = _validate_sample_list(
        request["samples"], channels * frame_samples)
    epoch = _require_int(request["epoch"], "INVALID_EPOCH", 0)
    first_input_sample = _require_int(
        request["first_input_sample"], "INVALID_POSITION", 0)
    lifecycle = request["lifecycle"]
    if lifecycle not in LIFECYCLES:
        raise EvidenceError("INVALID_LIFECYCLE", "INVALID_LIFECYCLE")
    execution_mode = _require_int(
        request["execution_mode"], "INVALID_MODE")
    if execution_mode not in EXECUTION_MODES:
        raise EvidenceError("INVALID_MODE", "INVALID_MODE")
    checkpoint_sha256 = _optional_digest(
        request["checkpoint_sha256"], "INVALID_CHECKPOINT_DIGEST")
    runtime_lock_sha256 = _optional_digest(
        request["runtime_lock_sha256"], "INVALID_RUNTIME_DIGEST")
    asset_bytes = _require_int(request["asset_bytes"], "INVALID_ASSET_BYTES",
                               0, MAX_EXTERNAL_ASSET_BYTES)
    if (checkpoint_sha256 is None) != (runtime_lock_sha256 is None):
        raise EvidenceError("INCOMPLETE_ASSET_MANIFEST",
                            "INCOMPLETE_ASSET_MANIFEST")
    if checkpoint_sha256 is not None and asset_bytes == 0:
        raise EvidenceError("MISSING_ASSET_BYTES", "MISSING_ASSET_BYTES")
    if checkpoint_sha256 is None and asset_bytes > 0:
        raise EvidenceError("UNCLAIMED_ASSET_BYTES", "UNCLAIMED_ASSET_BYTES")
    return {
        "candidate": COMPONENT_ID,
        "integration_variant": variant,
        "sample_rate_hz": rate,
        "channels": channels,
        "frame_samples": frame_samples,
        "samples": tuple(samples),
        "epoch": epoch,
        "first_input_sample": first_input_sample,
        "lifecycle": lifecycle,
        "execution_mode": execution_mode,
        "checkpoint_sha256": checkpoint_sha256,
        "runtime_lock_sha256": runtime_lock_sha256,
        "asset_bytes": asset_bytes,
    }


def base_request(variant: str = "reference") -> dict:
    return {
        "candidate": COMPONENT_ID,
        "integration_variant": variant,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "samples": [0.0] * HARNESS_FRAME_VALUES,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
        "checkpoint_sha256": None,
        "runtime_lock_sha256": None,
        "asset_bytes": 0,
    }


def _adverse_request_specs():
    base = base_request()

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
    good_digest = "0" * 64
    return (
        ("unknown_candidate", variant(candidate="NeuralKalmanAHS")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("missing_variant", {key: value for key, value in base.items()
                             if key != "integration_variant"}),
        ("unknown_variant", variant(integration_variant="cascaded")),
        ("uppercase_variant", variant(integration_variant="Reference")),
        ("bool_variant", variant(integration_variant=True)),
        ("null_variant", variant(integration_variant=None)),
        ("zero_channels", variant(channels=0)),
        ("negative_channels", variant(channels=-1)),
        ("bool_channels", variant(channels=True)),
        ("two_channels", variant(channels=2)),
        ("zero_rate", variant(sample_rate_hz=0)),
        ("negative_rate", variant(sample_rate_hz=-16000)),
        ("bool_rate", variant(sample_rate_hz=True)),
        ("undeclared_rate", variant(sample_rate_hz=8000)),
        ("zero_frame", variant(frame_samples=0)),
        ("negative_frame", variant(frame_samples=-160)),
        ("bool_frame", variant(frame_samples=True)),
        ("too_large_frame", variant(frame_samples=4097)),
        ("wrong_512_frame", variant(frame_samples=512,
                                    samples=[0.0] * 512)),
        ("wrong_1024_frame", variant(frame_samples=1024,
                                     samples=[0.0] * 1024)),
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
        ("bool_position", variant(first_input_sample=True)),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("invalid_execution_mode", variant(execution_mode=4)),
        ("bool_execution_mode", variant(execution_mode=True)),
        ("short_checkpoint_digest", variant(checkpoint_sha256="0" * 63,
                                            runtime_lock_sha256=good_digest,
                                            asset_bytes=1024)),
        ("uppercase_checkpoint_digest", variant(
            checkpoint_sha256="A" * 64, runtime_lock_sha256=good_digest,
            asset_bytes=1024)),
        ("nonhex_checkpoint_digest", variant(
            checkpoint_sha256="g" * 64, runtime_lock_sha256=good_digest,
            asset_bytes=1024)),
        ("bool_checkpoint_digest", variant(
            checkpoint_sha256=True, runtime_lock_sha256=good_digest,
            asset_bytes=1024)),
        ("short_runtime_digest", variant(
            checkpoint_sha256=good_digest, runtime_lock_sha256="0" * 63,
            asset_bytes=1024)),
        ("incomplete_asset_manifest", variant(
            checkpoint_sha256=good_digest, runtime_lock_sha256=None,
            asset_bytes=1024)),
        ("checkpoint_without_bytes", variant(
            checkpoint_sha256=good_digest, runtime_lock_sha256=good_digest,
            asset_bytes=0)),
        ("bytes_without_checkpoint", variant(asset_bytes=1024)),
        ("negative_asset_bytes", variant(asset_bytes=-1)),
        ("bool_asset_bytes", variant(asset_bytes=True)),
        ("asset_bytes_over_cap", variant(asset_bytes=536870913)),
        ("request_not_object", "not-an-object"),
    )


def adverse_cases() -> dict:
    cases = []
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
        "note": ("Invalid or unverified requests are rejected before any "
                 "artifact check or candidate call; no metrics exist."),
    }


def json_adverse_cases() -> dict:
    specs = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} extra'),
        ("invalid_syntax", '{"a":}'),
        ("json_not_object", '[1,2,3]'),
        ("float_value", '{"a":1.5}'),
    )
    cases = []
    for name, text in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            loads_strict(text)
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
    }


def missing_result(fixture_name: str) -> dict:
    return {
        "fixture": fixture_name,
        "status": "blocked",
        "reason": COMPARISON_STATUS,
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def _resolve_source_path(label: str) -> Path:
    if label.startswith("~/"):
        return Path.home() / label[2:]
    return SOURCE_ROOT / label


def _markers_in(path: Path, markers: Sequence[str],
                max_depth: int = 3) -> list:
    found = []
    if path.is_file():
        if path.suffix.lower() in markers or path.name in markers:
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
            if Path(name).suffix.lower() in markers or name in markers:
                found.append(name)
    return sorted(set(found))


def source_probe() -> dict:
    checked = []
    found = []
    marker_hits = []
    for label in SOURCE_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_source_path(label)
        if target.exists():
            found.append(label)
            marker_hits.extend(
                (Path(label) / name).as_posix()
                for name in _markers_in(target, SOURCE_MARKERS))
    return {
        "status": "blocked_source_absent" if not found else
                  "source_present_unqualified",
        "present": bool(found),
        "repositories": list(SOURCE_REPOSITORIES),
        "papers": [PAPER_URL, JOURNAL_URL, RESEARCH_URL],
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
        "runnable_implementation_present": False,
        "demo_materials_only_reported": True,
        "release_assets_listed_reported": False,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "marker_hits": sorted(set(marker_hits)),
        "note": ("Read-only existence checks only; no clone, fetch, archive "
                 "extraction or upstream file is opened or executed."),
    }


def checkpoint_probe() -> dict:
    checked = []
    found = []
    for label in CHECKPOINT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_source_path(label)
        if target.exists():
            hits = _markers_in(target, CHECKPOINT_MARKERS)
            for name in hits:
                candidate = target / name if target.is_dir() else target
                found.append({
                    "path": (Path(label) / name).as_posix(),
                    "byte_count": (candidate.stat().st_size
                                   if candidate.is_file() else None),
                    "sha256": None,
                })
    return {
        "status": "blocked_checkpoint_absent" if not found else
                  "checkpoint_present_unqualified",
        "present": bool(found),
        "found": sorted(found, key=lambda item: item["path"]),
        "sha256": None,
        "byte_count": None,
        "model_revision": None,
        "parameter_count": None,
        "model_card": None,
        "config": None,
        "framework": None,
        "checked_paths": sorted(checked),
        "markers": list(CHECKPOINT_MARKERS),
        "note": ("Existence and file-name checks only; no checkpoint is "
                 "opened, loaded, hashed or executed. A discovered file would "
                 "still require an exact revision, digest and rights decision "
                 "before use."),
    }


def runtime_probe() -> dict:
    checked = []
    found = []
    for label in RUNTIME_CANDIDATE_PATHS:
        checked.append(label)
        if _resolve_source_path(label).exists():
            found.append(label)
    locks = [path for path in RUNTIME_LOCK_CANDIDATES
             if _resolve_source_path(path).is_file()]
    pinned = bool(found) and bool(locks)
    return {
        "status": "runtime_present_unqualified" if pinned
                  else "blocked_runtime_unpinned",
        "checked_paths": sorted(checked),
        "found": sorted(found),
        "lockfiles": sorted(locks),
        "present": bool(found),
        "pinned": pinned,
        "interpreter": None,
        "framework": None,
        "sha256": None,
        "offline_path": None,
        "note": ("No candidate runtime is pinned. No host command discovery "
                 "is used as a runtime, framework version, lock or "
                 "import-parity record."),
    }


def cohort_probe() -> dict:
    checked = []
    found = []
    for label in COHORT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_source_path(label)
        if target.exists():
            hits = _markers_in(target, COHORT_MARKERS)
            if hits:
                found.extend((Path(label) / name).as_posix()
                             for name in hits)
    return {
        "status": "blocked_matched_cohort_absent" if not found else
                  "cohort_present_unqualified",
        "present": bool(found),
        "required": (
            "rights-cleared closed-loop cohort with frozen speech, "
            "loudspeaker-to-microphone paths, loop gain, delay, saturation, "
            "noise, reset schedule, held-out speakers/paths and target "
            "reference truth"),
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "corpus_rights": False,
        "loop_gain_measured": False,
        "delay_measured": False,
        "held_out_paths": False,
        "sha256": None,
        "note": ("Existence checks only; no audio file is opened or decoded. "
                 "A synthetic harness frame is not a matched closed-loop "
                 "cohort."),
    }


def license_probe() -> dict:
    return {
        "status": "blocked_rights_unrecorded",
        "reported_name": None,
        "reported_source": None,
        "license_text_present": False,
        "license_text_sha256": None,
        "license_file": None,
        "use_approved": False,
        "redistribution_approved": False,
        "derived_output_approved": False,
        "host_target_approved": False,
        "review": "blocked",
        "reviewed_by": None,
        "required": [
            "byte-identical upstream license text for every resolved repository",
            "written decision for use, modification and redistribution",
            "permission for derived model outputs and benchmark publication",
            "rights for every training and closed-loop corpus and impulse response",
        ],
        "note": ("The pinned note records no upstream license name or text. "
                 "Neither the license text nor a written rights decision is "
                 "present, and repository availability is not a right to use, "
                 "redistribute or publish."),
    }


def rights_probe() -> dict:
    return {
        "status": "blocked_rights_unrecorded",
        "source_license": None,
        "license_text_present": False,
        "license_text_sha256": None,
        "use_approved": False,
        "redistribution_approved": False,
        "derived_output_approved": False,
        "host_target_approved": False,
        "input_corpus_rights": False,
        "redistribution_scope": None,
        "review": "blocked",
        "reviewed_by": None,
        "note": ("No license text, use decision, distribution scope or "
                 "fixture permission is recorded locally. Upstream presence is "
                 "not a right to use, redistribute or publish."),
    }


def required_artifacts() -> list:
    specs = (
        ("ART-01", "exact_source_revision_and_license",
         "The exact NeuralKalmanAHS and AHS_2023 implementation at immutable "
         "40-hex revisions, including the covariance and reference "
         "integration entry points, reviewed upstream license text, per-file "
         "SHA-256 manifests, file counts and tree digests."),
        ("ART-02", "exact_checkpoint_model_card_and_variant_config",
         "The trained checkpoint bytes for each covariance and reference "
         "variant with SHA-256, byte count, model card, training provenance, "
         "architecture, STFT/frame/hop geometry, Kalman state and covariance "
         "configuration, parameter count, precision and reset policy, plus a "
         "canonical per-variant model/config digest."),
        ("ART-03", "pinned_runtime_and_harness",
         "A hash-pinned inference runtime and streaming harness with "
         "install/import parity, a checkpoint loader, finite drain, reset and "
         "the exact sample-rate/frame/hop geometry for both variants."),
        ("ART-04", "matched_closed_loop_cohort",
         "A rights-cleared closed-loop cohort with frozen speech, measured or "
         "frozen loudspeaker-to-microphone paths, loop gain, delay, "
         "saturation, noise, reset schedule, held-out speakers/paths and "
         "target-speech/reference truth."),
        ("ART-05", "frozen_dsp_protocol_and_results",
         "A frozen DSP protocol and result bundle for sweeps, steps, impulses, "
         "silence, clean speech, gain, response, attack/release, headroom, "
         "delay, numerical behavior, state transitions and interacting "
         "nonlinear configurations on the exact pinned candidate."),
        ("ART-06", "source_checkpoint_cohort_and_output_rights",
         "Reviewed source, checkpoint, training-data, corpus and derived-output "
         "rights, including redistribution scope and any participant or device "
         "terms."),
        ("ART-07", "independent_review_and_release_package",
         "An independent exact-head review of source, checkpoints, runtime, "
         "rights, cohort, covariance/reference distinction, an opt-in "
         "default-off adapter decision and a complete release package."),
    )
    return [{
        "id": artifact_id,
        "artifact": kind,
        "required": requirement,
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
        "blocked": True,
        "present": False,
        "verified": False,
    } for artifact_id, kind, requirement in specs]


def exact_blockers() -> list:
    specs = (
        ("BLK-01", "source_absent_demo_materials_only",
         ("The pinned note records README/demo HTML, CSS and audio only for "
          "the public repositories, with no source implementation, no "
          "revision, no tree digest, no file count and no license text."),
         ("Stage the exact NeuralKalmanAHS and AHS_2023 source at immutable "
          "40-hex revisions with reviewed license text and per-file SHA-256 "
          "manifests; never reconstruct source from the paper description."),
         "ART-01", ("RG-01",)),
        ("BLK-02", "checkpoint_and_variant_config_absent",
         ("No trained covariance-variant or reference-variant checkpoint, "
          "model card, Kalman covariance configuration, network structure or "
          "canonical model/config digest exists locally."),
         ("Provide each variant's exact trained checkpoint with byte count, "
          "SHA-256, model card, training revision and the covariance/reference "
          "configuration; never invent weights, a network or a controller."),
         "ART-02", ("RG-02", "RG-05")),
        ("BLK-03", "runtime_and_geometry_unpinned",
         ("No hash-pinned runtime, checkpoint loader, offline load path, "
          "interactive harness or declared candidate geometry exists."),
         ("Pin the runtime, loader, offline path and exact geometry for both "
          "variants with install/import parity and a finite drain/reset path."),
         "ART-03", ("RG-05",)),
        ("BLK-04", "matched_cohort_absent",
         ("No rights-cleared matched closed-loop cohort with loop gain, delay, "
          "saturation, noise, reset schedule and held-out speakers/paths "
          "exists; the local feedback pilot is a classical-controller screen, "
          "not a NeuralKalmanAHS cohort."),
         ("Freeze a rights-cleared matched cohort with held-out "
          "speakers/paths and exact loop metadata before any comparison."),
         "ART-04", ("RG-03", "RG-06")),
        ("BLK-05", "dsp_measurements_absent",
         ("The DSP profile requires sweeps, steps, impulses, silence, clean "
          "speech and a task-specific control with gain, response, "
          "attack/release, headroom, delay, numerical behavior, state "
          "transitions and interacting nonlinear configurations; none was run "
          "because no candidate instance exists."),
         ("Run the frozen DSP matrix on both pinned variants and retain every "
          "failure and nonfinite case."),
         "ART-05", ("RG-06",)),
        ("BLK-06", "rights_review_and_adapter_absent",
         ("Source, checkpoint, training-data, cohort and output rights are "
          "unrecorded, and no independent exact-head review or opt-in adapter "
          "decision exists."),
         ("Record reviewed rights and obtain independent exact-head review "
          "before opening any opt-in, default-off adapter."),
         "ART-06", ("RG-04", "RG-07", "RG-08")),
    )
    return [{
        "id": blocker_id,
        "statement": statement,
        "required_action": action,
        "artifact_id": artifact_id,
        "linked_gates": list(gates),
        "status": "open",
        "qualifies": False,
    } for blocker_id, _kind, statement, action, artifact_id, gates in specs]


def integration_variants() -> dict:
    return {
        "status": COMPARISON_STATUS,
        "variant_count": len(VARIANT_IDS),
        "variants": {
            "covariance": {
                "integration_point": "kalman_covariance_or_process_noise",
                "mechanism": (
                    "neural network embedded in Kalman covariance or "
                    "process-noise estimation"),
                "reported_in_note": True,
                "exact_variant_identity_recorded": False,
                "source_revision": None,
                "source_sha256": None,
                "checkpoint_sha256": None,
                "checkpoint_bytes": None,
                "model_card_sha256": None,
                "config_sha256": None,
                "runtime_sha256": None,
                "declared_geometry": None,
                "present": False,
                "implemented_here": False,
                "measured_here": False,
                "blocked_by": list(BLOCKER_IDS),
                "qualifies_candidate": False,
                "result": None,
                "metrics": None,
            },
            "reference": {
                "integration_point": "kalman_reference_estimate",
                "mechanism": (
                    "network output supplies the Kalman reference used by the "
                    "recursive update"),
                "reported_in_note": True,
                "exact_variant_identity_recorded": False,
                "source_revision": None,
                "source_sha256": None,
                "checkpoint_sha256": None,
                "checkpoint_bytes": None,
                "model_card_sha256": None,
                "config_sha256": None,
                "runtime_sha256": None,
                "declared_geometry": None,
                "present": False,
                "implemented_here": False,
                "measured_here": False,
                "blocked_by": list(BLOCKER_IDS),
                "qualifies_candidate": False,
                "result": None,
                "metrics": None,
            },
        },
        "distinction": {
            "same_upstream_family_reported": True,
            "distinct_integration_points": True,
            "distinguished_from_note": "partially",
            "separately_checkpointed": False,
            "separately_licensed": False,
            "separately_measured_here": False,
            "exact_variant_identity_recorded": False,
            "note": (
                "The pinned note names neural networks embedded in Kalman "
                "reference/covariance estimation but records no exact "
                "per-variant architecture, checkpoint, state vector, "
                "covariance parameterisation or runtime. The two integration "
                "points are kept separate and neither is inferred."),
        },
        "qualifies_candidate": False,
    }


def method_provenance() -> dict:
    return {
        "status": "source_reported_only_not_reproduced",
        "family": "NeuralKalmanAHS / Hybrid AHS",
        "papers": [PAPER_URL, RESEARCH_URL, JOURNAL_URL],
        "project_page": PROJECT_URL,
        "repositories": list(SOURCE_REPOSITORIES),
        "reported_components": [
            "frequency-domain Kalman filter",
            "self-attentive recurrent neural network",
            "neural network in Kalman reference estimation",
            "neural network in Kalman covariance estimation",
        ],
        "reported_variants": [
            "cascaded NN plus Kalman",
            "recursively trained variants",
            "NN embedded in Kalman reference estimation",
            "NN embedded in Kalman covariance estimation",
        ],
        "training": (
            "teacher-forced offline training on Kalman-preprocessed and ideal "
            "microphone signals (reported for the Hybrid AHS family)"),
        "inference": (
            "streaming inference; the fixed network output becomes the Kalman "
            "reference (reported for the Hybrid AHS family)"),
        "reported_evaluation": ["simulated", "real-recorded"],
        "exact_geometry_recorded": False,
        "exact_parameter_count_recorded": False,
        "exact_checkpoint_present": False,
        "reproduced_here": False,
        "source_reported_only": True,
        "qualifies_candidate": False,
        "note": (
            "Only the method family, reported variant names and "
            "author-reported study results are retained from the pinned note. "
            "No architecture detail, geometry, weight or output is inferred."),
    }


def author_reported_results() -> dict:
    return {
        "status": "retained_author_reported_not_reproduced",
        "evidence_class": "author_reported_not_reproduced",
        "source": "research/feedback_control_20261028.md",
        "study": "HybridAHS / NeuralKalmanAHS journal comparison (2024)",
        "cohort": {
            "utterances": 200,
            "loop_gains": ["2", "2.5", "3"],
        },
        "neuralkalmanahs": {
            "condition_loop_gain": ["2", "2.5", "3"],
            "sdr_db": ["2.65", "1.98", "1.45"],
            "pesq": ["2.33", "2.17", "2.04"],
            "variant_attribution": "not_disambiguated_in_note",
        },
        "hybridahs_v2": {
            "qualitative": (
                "complex-ratio-mask results reported as the strongest overall "
                "trade-off in parts of the study"),
            "metrics": None,
        },
        "local_metrics": None,
        "reproduced_here": False,
        "device_or_listening_result": False,
        "qualifies_candidate": False,
        "note": (
            "These are paper results on the author setup at loop gains 2, 2.5 "
            "and 3. They are not results from this repository, are not "
            "comparable to the current CLN-01 DNS screen, do not identify "
            "which covariance or reference variant produced each value, and "
            "do not qualify the candidate. No SDR or PESQ value was computed "
            "here."),
    }


def research_controls() -> dict:
    return {
        "status": "prior_pilot_retained_not_rerun",
        "evidence_class": "prior_pilot_author_reported_not_rerun",
        "source": "research/feedback_control_20261028.md",
        "candidate": "none: classical feedback controls, not NeuralKalmanAHS",
        "synthetic_proxy": {
            "source_intervals": 12,
            "loop_gain_and_delay_conditions": 3,
            "controllers": 6,
            "runs": 216,
            "columns": ["controller", "median_sdr_db",
                        "median_tail_feedback_to_speech_db"],
            "rows": [
                ["identity", "-6.511", "+6.961"],
                ["fixed_margin_5db", "+5.193", "-10.651"],
                ["adaptive_notch", "-6.377", "+6.838"],
                ["notch_plus_margin", "+0.170", "-0.612"],
                ["block_nlms_afc", "-2.387", "+0.012"],
                ["afc_plus_3db_margin", "+4.958", "-7.692"],
            ],
            "note": (
                "Short four-tap synthetic loop proxy; fixed margin led this "
                "screen. No row is NeuralKalmanAHS."),
        },
        "measured_path": {
            "utterances": 6,
            "mic_paths": 8,
            "loop_gains": ["0.95", "1.05", "1.15"],
            "runs_per_candidate": 144,
            "columns": ["controller", "median_sdr_db",
                        "median_tail_feedback_to_speech_db",
                        "median_tail_output_to_speech_db"],
            "rows": [
                ["identity", "5.671", "-12.159", "-12.159"],
                ["fixed_margin_5db", "6.887", "-25.626", "-30.626"],
                ["adaptive_notch", "5.751", "-13.740", "-13.682"],
                ["notch_plus_margin", "6.259", "-19.992", "-20.717"],
                ["block_nlms_afc", "8.427", "-20.100", "-16.948"],
                ["afc_plus_3db_margin", "8.429", "-24.023", "-20.045"],
            ],
            "note": (
                "SMARD measured IRs resampled to 16 kHz and cropped to 256 ms; "
                "controlled test settings, not measured physical "
                "gain-before-feedback. No row is NeuralKalmanAHS."),
        },
        "rerun_here": False,
        "metrics": None,
        "qualifies_candidate": False,
        "note": (
            "The prior pilot is a classical-controller screen on AMI speech "
            "and SMARD paths. It is retained as historical scope-matched "
            "context only, is not rerun, pooled, inherited or promoted, and "
            "cannot be used as matched evidence for either integration "
            "variant."),
    }


def external_boundary() -> dict:
    return {
        "documented": True,
        "upstream_kind": "research model with demo-only public repositories",
        "candidate": TITLE,
        "papers": [PAPER_URL, RESEARCH_URL, JOURNAL_URL],
        "project_page": PROJECT_URL,
        "repositories": list(SOURCE_REPOSITORIES),
        "source_present": False,
        "runnable_implementation_present": False,
        "public_demo_materials_only_reported": True,
        "checkpoint_present": False,
        "release_assets_present": False,
        "runtime_present": False,
        "host_target": "macOS / Python 3 workspace",
        "host_target_approved": False,
        "license_text_present": False,
        "license_review": "blocked",
        "use_approved": False,
        "redistribution_approved": False,
        "derived_output_approved": False,
        "cohort_present": False,
        "author_output_present": False,
        "local_output_present": False,
        "adapter_implemented": False,
        "adapter_default_registration": False,
        "automatic_discovery": False,
        "fallback": "none",
        "author_claims_separate_from_local_measurements": True,
        "note": (
            "The upstream boundary is documented from the pinned research note "
            "and public paper/project pages only. The repositories are "
            "reported to expose demo materials without source or checkpoints. "
            "No source, checkpoint, runtime, license text, cohort or "
            "measurement is present, and this host target is not approved."),
    }


def geometry() -> dict:
    return {
        "candidate": TITLE,
        "declared_candidate_geometry_recorded": False,
        "declared_sample_rates_hz": [],
        "declared_frame_samples": None,
        "declared_channels": None,
        "declared_stft_size": None,
        "declared_hop_samples": None,
        "declared_kalman_state_dimension": None,
        "declared_covariance_parameterisation": None,
        "declared_network_structure": None,
        "declared_parameter_count": None,
        "integration_points": {
            "reference": "kalman_reference_estimate",
            "covariance": "kalman_covariance_or_process_noise",
        },
        "local_harness_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
        },
        "local_harness_is_candidate_geometry": False,
        "v0_can_represent_declared_input": None,
        "verified_here": False,
        "measured_here": False,
        "candidate_output": False,
        "note": (
            "The pinned note records no per-variant sample rate, frame, hop, "
            "STFT size, channel count, Kalman state dimension, covariance "
            "parameterisation, network structure or parameter count. None is "
            "inferred. The 16 kHz / mono / 160-sample harness is the unchanged "
            "installed-v0 bound used only to exercise validation and "
            "rejection."),
    }


def profile_mapping() -> dict:
    return {
        "sweeps_steps_impulses_silence_clean_speech":
            "partial_local_harness_stimuli_only",
        "task_specific_intelligibility_or_load_control":
            "blocked_no_permitted_cohort",
        "gain_and_frequency_response": "blocked_no_candidate_output",
        "attack_and_release": "blocked_no_candidate_output",
        "headroom_and_peaks": "blocked_no_candidate_output",
        "delay_and_content_mapping": "blocked_no_candidate_output",
        "numerical_behavior": "partial_local_harness_rejection_only",
        "state_transitions": "blocked_no_candidate_instance",
        "interacting_nonlinear_configurations": "blocked_no_candidate_instance",
        "covariance_and_reference_integration_distinction":
            "recorded_variant_split_no_exact_config",
        "candidate_output": COMPARISON_STATUS,
    }


def required_results() -> dict:
    return {
        "exact_source_revision_and_license": "blocked_source_absent",
        "covariance_variant_checkpoint_and_config":
            "blocked_checkpoint_absent",
        "reference_variant_checkpoint_and_config":
            "blocked_checkpoint_absent",
        "pinned_runtime_and_offline_import_parity": "blocked_runtime_unpinned",
        "declared_geometry_and_variant_configuration":
            "blocked_config_and_geometry_absent",
        "covariance_and_reference_reproduction":
            "blocked_no_candidate_instance",
        "dsp_gain_response_attack_release_delay":
            "blocked_no_candidate_output",
        "author_reported_result_reconciliation":
            "blocked_author_reported_only",
        "matched_cohort_sdr_pesq_and_speech_preservation":
            "blocked_no_permitted_cohort",
        "device_timing_memory_and_callback":
            "blocked_no_paced_measurement",
        "provider_intake_and_opt_in_adapter":
            "blocked_no_approved_runtime_or_terms",
        "authorized_listening_and_benchmark":
            "blocked_no_release_evidence",
        "release_qualification": "blocked_no_release_evidence",
    }


def candidates() -> dict:
    variants = integration_variants()["variants"]
    return {
        "covariance": variants["covariance"],
        "reference": variants["reference"],
    }


def controls() -> dict:
    return {
        "identity_control": {
            "status": "bit_exact_synthetic_only",
            "candidate_processing": False,
            "qualifies_candidate": False,
        },
        "author_reported_reference": {
            "status": "provenance_only_not_reproduced",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "prior_classical_feedback_pilot": {
            "status": "prior_pilot_retained_not_rerun",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "external_fallback": {
            "status": "documented_no_runtime",
            "automatic_discovery": False,
            "default_registration": False,
            "fallback": "none",
            "metrics": None,
            "qualifies_candidate": False,
        },
    }


def stimulus_probe() -> dict:
    stimuli = {}
    identity = {}
    for name, generator in STIMULUS_GENERATORS.items():
        samples = generator()
        stimuli[name] = stimulus_metrics(name, samples)
        identity[name] = {
            "digest": tensor_digest(samples),
            "byte_identical": tuple(samples) == tuple(
                float(value) for value in samples),
        }
    return {
        "purpose": (
            "harness stimulus characterisation only; not a NeuralKalmanAHS "
            "result and not a candidate output"),
        "harness_geometry": {
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "flat_values": HARNESS_FRAME_VALUES,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "verified_model_geometry": False,
            "note": (
                "This is the unchanged installed-v0 16 kHz / mono / 160 "
                "format. It is used only to exercise validation and rejection; "
                "it is not a claim about candidate geometry."),
        },
        "stimuli": stimuli,
        "speech_contrast": speech_contrast(
            STIMULUS_GENERATORS["speech_like"]()),
        "identity_control": identity,
        "candidate_processing": False,
    }


def collect_blockers() -> list:
    blockers = []
    if not source_probe()["present"]:
        blockers.append("source_absent")
    if not checkpoint_probe()["present"]:
        blockers.append("covariance_and_reference_checkpoints_absent")
    if not runtime_probe()["pinned"]:
        blockers.append("runtime_unpinned")
    if not cohort_probe()["present"]:
        blockers.append("matched_closed_loop_cohort_absent")
    if license_probe()["review"] != "approved":
        blockers.append("rights_unrecorded")
    if not author_reported_results()["reproduced_here"]:
        blockers.append("author_reported_results_only")
    return sorted(blockers)


def admit(request: Any) -> dict:
    """Validate a request, then fail closed because artifacts are absent."""
    validated = validate_request(request)
    blockers = collect_blockers()
    if not blockers:
        raise EvidenceError(
            "ARTIFACTS_ABSENT: blocker list unexpectedly empty",
            "ARTIFACTS_ABSENT")
    return {
        "status": DECISION,
        "admissible": False,
        "candidate_processing": False,
        "input_validated": True,
        "integration_variant": validated["integration_variant"],
        "metrics": None,
        "result": None,
        "qualifies_candidate": False,
        "blockers": blockers,
        "note": (
            "A structurally valid caller-supplied-asset request is still not "
            "admissible: the source, covariance/reference checkpoints, "
            "runtime, rights and matched cohort are absent. No port, fallback "
            "or surrogate is used."),
    }


def probe_candidate(request: Any) -> None:
    validate_request(request)
    raise EvidenceError(
        "ARTIFACTS_ABSENT: NeuralKalmanAHS source, covariance/reference "
        "checkpoints, pinned runtime, approved rights and matched cohort are "
        "not present; no processing is performed", "ARTIFACTS_ABSENT")


def _project(row: dict, require_component: bool = False) -> dict:
    required = ("id", "title", "mode", "repository", "depends_on")
    missing = [field for field in required if field not in row]
    if require_component and "component" not in row:
        missing.append("component")
    if missing:
        raise EvidenceError("board_row_missing_field:" + missing[0],
                            "BOARD_INVALID")
    depends_on = row.get("depends_on")
    if not isinstance(depends_on, list):
        raise EvidenceError("board_depends_on_not_list", "BOARD_INVALID")
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "component": row.get("component"),
        "mode": row.get("mode"),
        "repository": row.get("repository"),
        "depends_on": list(depends_on),
    }


def _board_tasks(path: Path | None = None) -> list:
    board = SOURCE_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    document = read_strict_json(board)
    rows = document.get("tasks")
    if not isinstance(rows, list):
        raise EvidenceError("board_tasks_not_list", "BOARD_INVALID")
    return rows


def board_row_projection(path: Path | None = None) -> dict:
    matches = [row for row in _board_tasks(path)
               if isinstance(row, dict) and row.get("id") == TASK]
    if len(matches) != 1:
        raise EvidenceError("board_row_not_unique", "BOARD_ROW_MISSING")
    projection = _project(matches[0], require_component=True)
    if projection["component"] != COMPONENT_ID:
        raise EvidenceError("board_component_mismatch",
                            "BOARD_IDENTITY_CHANGED")
    if projection["mode"] != MODE:
        raise EvidenceError("board_mode_mismatch", "BOARD_IDENTITY_CHANGED")
    if projection["repository"] != REPOSITORY:
        raise EvidenceError("board_repository_mismatch",
                            "BOARD_IDENTITY_CHANGED")
    return projection


def linked_rows(path: Path | None = None) -> tuple:
    rows = _board_tasks(path)
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    root = by_id.get(TASK)
    if root is None:
        raise EvidenceError("board_row_absent", "BOARD_ROW_MISSING")
    projection = _project(root, require_component=True)
    result = [projection]
    for dependency in projection["depends_on"]:
        row = by_id.get(dependency)
        if row is None:
            raise EvidenceError("linked_row_absent:" + dependency,
                                "BOARD_ROW_MISSING")
        result.append(_project(row))
    return tuple(result)


def linked_rows_digest(rows: tuple | None = None) -> str:
    value = linked_rows() if rows is None else rows
    return object_digest([dict(row) for row in value])


def _gate_link() -> dict:
    return {
        "task_id": TASK,
        "title": TITLE,
        "mode": MODE,
        "repository": REPOSITORY,
        "component": COMPONENT_ID,
    }


def release_gates() -> list:
    specs = (
        ("RG-01", "exact_licensed_source_pinned",
         "No exact NeuralKalmanAHS/AHS_2023 source repository, 40-hex "
         "revision, license or per-file SHA-256 manifest exists; the pinned "
         "note records demo materials only.",
         "Stage and pin the exact source with reviewed terms and per-file "
         "digests; never reconstruct source from the paper description."),
        ("RG-02", "covariance_and_reference_checkpoints_pinned",
         "No trained covariance-variant or reference-variant checkpoint, byte "
         "count, model card, training provenance, architecture or "
         "parameter/config digest exists.",
         "Pin each variant's checkpoint and model/config digest with reviewed "
         "terms and an explicit variant identity."),
        ("RG-03", "rights_cleared_matched_closed_loop_cohort",
         "No rights-cleared closed-loop cohort with frozen speech, measured or "
         "frozen paths, loop gain, delay, saturation, noise, reset schedule or "
         "held-out speakers/paths exists.",
         "Freeze a rights-cleared matched cohort with held-out speakers/paths "
         "and exact loop metadata."),
        ("RG-04", "source_checkpoint_cohort_and_output_rights",
         "Source, checkpoint, training-data, corpus and output-use rights are "
         "unresolved.",
         "Record reviewed source, checkpoint, training-data, cohort and "
         "output-use rights with notices."),
        ("RG-05", "runtime_geometry_and_variant_integration_pinned",
         "No exact runtime lock, checkpoint loader, offline load path, "
         "declared geometry or covariance/reference configuration is pinned.",
         "Pin the runtime, loader, geometry and per-variant integration "
         "configuration with exact digests."),
        ("RG-06", "dsp_acceptance_matrix_and_numerical_behavior",
         "The DSP profile requires sweeps, steps, impulses, silence, clean "
         "speech and a task-specific control with gain, response, "
         "attack/release, headroom, delay, numerical behavior, state "
         "transitions and interacting nonlinear configurations; none was run.",
         "Run the frozen DSP matrix on both pinned variants and retain every "
         "failure and nonfinite case."),
        ("RG-07", "author_reported_reconciliation_and_variant_distinction",
         "The author-reported SDR/PESQ values cannot be attributed to a "
         "specific covariance or reference variant, and no local measurement "
         "exists to reconcile them.",
         "Reproduce each reported variant exactly with the pinned checkpoint "
         "and cohort, reconcile SDR/PESQ with pre-registered tolerances, and "
         "keep author-reported values labelled separately."),
        ("RG-08", "opt_in_adapter_independent_review_and_release",
         "No approved opt-in adapter, provider intake, benchmark validation, "
         "authorized listening, independent exact-head review or release "
         "approval exists.",
         "Open a default-off opt-in adapter only after RG-01 to RG-07 pass, "
         "validate a benchmark bundle, obtain independent review and release "
         "approval."),
    )
    link = _gate_link()
    return [{
        "id": gate_id,
        "name": name,
        "status": "blocked",
        "qualifies": False,
        "reason": reason,
        "reopen_condition": reopen,
        "linked_row": dict(link),
    } for gate_id, name, reason, reopen in specs]


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "candidate_qualified": False,
        "all_release_gates_blocked": True,
        "blocked_gate_count": len(GATE_IDS),
        "blocked_gate_ids": list(GATE_IDS),
        "no_missing_result_qualifies_candidate": True,
        "not_qualified": True,
        "covariance_variant_qualified": False,
        "reference_variant_qualified": False,
        "reason": (
            "Exact source, covariance/reference checkpoints, model cards, "
            "matched cohort, runtime, rights and review are absent; no "
            "candidate output or DSP measurement exists."),
    }


def boundary() -> dict:
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


def source_evidence_statements() -> list:
    return [
        ("research/feedback_control_20261028.md records Hybrid AHS "
         "(Interspeech 2023) as a frequency-domain Kalman filter plus a "
         "self-attentive RNN, with teacher-forced offline training and "
         "streaming inference where the fixed network output becomes the "
         "Kalman reference."),
        ("the same note records the HybridAHS/NeuralKalmanAHS journal study "
         "comparing cascaded NN plus Kalman, recursively trained variants, "
         "and neural networks embedded in Kalman reference/covariance "
         "estimation."),
        ("the same note records NeuralKalmanAHS results on 200 utterances at "
         "loop gains 2, 2.5 and 3: SDR 2.65, 1.98 and 1.45 dB and PESQ 2.33, "
         "2.17 and 2.04, with HybridAHS v2 complex-ratio-mask results "
         "reported as the strongest overall trade-off in parts of the study."),
        ("the same note records that the public YIXUANZ/NeuralKalmanAHS and "
         "YIXUANZ/AHS_2023 repositories expose README/demo HTML, CSS and "
         "audio files, with no source implementation or model checkpoints in "
         "their visible file listings and no release assets for "
         "NeuralKalmanAHS."),
        ("plan/INVENTORY.json assigns "
         "neuralkalmanahs-covariance-reference-variants the dsp verification "
         "profile, disposition sdk-model, evidence_status blocked and the plan "
         "note to distinguish covariance and reference integration because the "
         "local source review found demo materials only."),
        ("plan/audio-sdk/README.md requires runnable source, exact assets, "
         "permitted scope and matched evidence before a caller-supplied "
         "reference or opt-in adapter is added."),
        ("plan/swarm/VERIFICATION.md defines the DSP acceptance profile: "
         "sweeps, steps, impulses, silence, clean speech and a task-specific "
         "control with gain, response, attack/release, headroom, delay, "
         "numerical behavior, state transitions and interacting nonlinear "
         "configurations."),
        ("No local NeuralKalmanAHS or AHS_2023 source, covariance/reference "
         "checkpoint, runtime lock, license text, matched cohort or candidate "
         "geometry exists; nothing was cloned, downloaded, ported, "
         "reconstructed or simulated."),
    ]


def local_manifest_paths() -> list:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name not in LOCAL_MANIFEST_EXCLUDED)


def build_report() -> dict:
    source = source_probe()
    checkpoint = checkpoint_probe()
    runtime = runtime_probe()
    license_block = license_probe()
    cohort = cohort_probe()
    rights = rights_probe()
    gates = release_gates()
    artifacts = required_artifacts()
    blockers = exact_blockers()
    variants = integration_variants()
    rows = linked_rows()
    row = board_row_projection()
    adverse_request = adverse_cases()
    adverse_json = json_adverse_cases()
    stimuli = stimulus_probe()
    local_checks = {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "floats_absent_from_report": True,
        "stable_board_identity_only": True,
        "board_full_file_not_hashed": True,
        "source_absent": source["present"] is False,
        "runnable_source_reported_absent":
            source["runnable_implementation_present"] is False,
        "checkpoint_absent": checkpoint["present"] is False,
        "runtime_unpinned": runtime["pinned"] is False,
        "license_text_absent": license_block["license_text_present"] is False,
        "rights_not_approved": (
            license_block["use_approved"] is False and
            license_block["redistribution_approved"] is False),
        "matched_cohort_absent": cohort["present"] is False,
        "integration_variants_distinct":
            variants["distinction"]["distinct_integration_points"] is True,
        "both_variants_blocked": all(
            item["present"] is False and item["qualifies_candidate"] is False
            for item in variants["variants"].values()),
        "author_reported_results_only":
            author_reported_results()["reproduced_here"] is False,
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "nonfinite_samples_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith("nonfinite")),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked":
            missing_result("neuralkalmanahs_placeholder")["status"] == "blocked",
        "identity_control_bit_exact": all(
            block["byte_identical"]
            for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
        "external_boundary_closed": (
            external_boundary()["adapter_implemented"] is False and
            external_boundary()["adapter_default_registration"] is False and
            external_boundary()["automatic_discovery"] is False),
        "no_result_qualifies_candidate": True,
    }
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "format": FORMAT,
        "generated_by": "run.py",
        "task": TASK,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "component_id": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "verification_profile": PROFILE_KEY,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "incomplete": True,
        "proposal_only": True,
        "qualification_status": QUALIFICATION_STATUS,
        "qualification": qualification_block(),
        "boundary": boundary(),
        "profile": {
            "name": PROFILE_KEY,
            "source": SOURCE_PINS[PROFILE_SOURCE_REL],
        },
        "profile_mapping": profile_mapping(),
        "integration_variants": variants,
        "external_boundary": external_boundary(),
        "method_provenance": method_provenance(),
        "author_reported_results": author_reported_results(),
        "research_controls": research_controls(),
        "reference": {
            "implementation": "task-local standard-library feasibility gate",
            "upstream_source_present": source["present"],
            "runnable_implementation_present":
                source["runnable_implementation_present"],
            "checkpoint_present": checkpoint["present"],
            "pinned_runtime_present": runtime["pinned"],
            "license_text_present": license_block["license_text_present"],
            "rights_approved": False,
            "matched_cohort_present": cohort["present"],
            "author_reported_results_retained": True,
            "reproduced_here": False,
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "real_model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "real_corpus_read": False,
            "covariance_variant_present": False,
            "reference_variant_present": False,
            "note": (
                "No NeuralKalmanAHS model, Kalman filter, neural network, "
                "covariance or reference variant, adapter or port is "
                "implemented or simulated; only probes, request rejection, "
                "author-reported provenance and synthetic harness controls are "
                "performed."),
        },
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "source_evidence_statements": source_evidence_statements(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_links": [dict(item) for item in rows],
        "board_row": row,
        "board_link_projection_sha256": linked_rows_digest(rows),
        "board_link_fields": list(STABLE_TASK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "board_full_file_hashed": False,
        "upstream_blocker": {
            "status": COMPARISON_STATUS,
            "candidate": TITLE,
            "source_revision": None,
            "source_sha256": None,
            "tree_digest": None,
            "covariance_checkpoint_sha256": None,
            "reference_checkpoint_sha256": None,
            "model_card_sha256": None,
            "covariance_config_digest": None,
            "reference_config_digest": None,
            "runtime_sha256": None,
            "cohort_sha256": None,
            "rights_review": "blocked",
            "matched_closed_loop_cohort": False,
            "covariance_variant_present": False,
            "reference_variant_present": False,
            "no_upstream_parity_claim": True,
            "rights_requirement": (
                "The byte-identical upstream license text for every resolved "
                "repository, a written decision approving use, modification, "
                "redistribution, derived model outputs and the intended "
                "benchmark or product scope, permission for every training and "
                "closed-loop corpus and impulse response, and permission for "
                "any listening or publication are required before any "
                "reproduction, adapter, benchmark or release claim."),
            "reopen_condition": (
                "Stage the exact NeuralKalmanAHS and AHS_2023 source at 40-hex "
                "revisions with reviewed license and per-file SHA-256 "
                "manifests; pin the covariance and reference checkpoints, "
                "model cards, architecture covariance parameterisation and "
                "per-variant config digests; provide a rights-cleared matched "
                "closed-loop cohort with frozen paths, loop gain, delay, "
                "saturation, noise, reset schedule and held-out splits; pin "
                "the runtime and harness; run the DSP matrix; reconcile the "
                "author-reported SDR/PESQ per variant; then obtain independent "
                "exact-head review."),
        },
        "required_artifacts": artifacts,
        "missing_artifacts": [row["id"] for row in artifacts
                              if row["status"] == "absent"],
        "exact_blockers": blockers,
        "open_blockers": [row["id"] for row in blockers
                          if row["status"] == "open"],
        "source_probe": source,
        "checkpoint_probe": checkpoint,
        "runtime_probe": runtime,
        "license_probe": license_block,
        "cohort_probe": cohort,
        "rights_probe": rights,
        "geometry": geometry(),
        "candidates": candidates(),
        "controls": controls(),
        "required_results": required_results(),
        "stimulus_probe": stimuli,
        "adverse": {
            "invalid_config_and_input": adverse_request,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": missing_result("neuralkalmanahs_placeholder"),
        },
        "local_harness_checks": local_checks,
        "release_gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "gates": [gate["id"] for gate in gates],
        "regressions": [],
        "regression_count": 0,
        "no_missing_result_qualifies_candidate": True,
    }
    if not finite_json(report):
        raise EvidenceError("REPORT_NONFINITE", "REPORT_NONFINITE")
    assert_no_float(report)
    return report


def canonical_report(report: dict | None = None) -> tuple:
    value = build_report() if report is None else report
    text = canonical_text(value)
    return text, sha256_bytes(text.encode("ascii"))


def build_contract() -> dict:
    rows = linked_rows()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "component_id": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "format": FORMAT,
        "verification_profile": PROFILE_KEY,
        "evidence_status": EVIDENCE_STATUS,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "depends_on": list(DEPENDS_ON),
        "write_scope": WRITE_SCOPE,
        "plan_note": PLAN_NOTE,
        "qualification": qualification_block(),
        "upstream_blocker": {
            "status": COMPARISON_STATUS,
            "source_revision": None,
            "source_sha256": None,
            "tree_digest": None,
            "covariance_checkpoint_sha256": None,
            "reference_checkpoint_sha256": None,
            "model_card_sha256": None,
            "covariance_config_digest": None,
            "reference_config_digest": None,
            "runtime_sha256": None,
            "cohort_sha256": None,
            "rights_review": "blocked",
            "matched_closed_loop_cohort": False,
            "covariance_variant_present": False,
            "reference_variant_present": False,
            "reopen_condition": (
                "Stage the exact source at 40-hex revisions with reviewed "
                "license and per-file SHA-256 manifests; pin both variant "
                "checkpoints, model cards and config digests; provide a "
                "rights-cleared matched closed-loop cohort; pin the runtime "
                "and geometry; run the DSP matrix; reconcile author-reported "
                "results per variant; obtain independent exact-head review."),
        },
        "integration_variants": {
            "variant_ids": list(VARIANT_IDS),
            "distinct_integration_points": True,
            "covariance_present": False,
            "reference_present": False,
            "exact_variant_identity_recorded": False,
        },
        "required_artifacts": required_artifacts(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "non_claims": list(NON_CLAIMS),
        "prohibited_actions": [
            "download, clone, reconstruct, train or substitute the candidate",
            "invent weights, an architecture, a covariance parameterisation "
            "or a learned controller",
            "read, decode or listen to real audio",
            "measure device, callback or wall-clock timing",
            "change provider, descriptor, registry, default, ABI, "
            "CONTRACTS.md, shared build or CI",
            "change board or handoff state",
            "make a benchmark, product or release claim",
        ],
        "board_links": [dict(item) for item in rows],
        "board_link_projection_sha256": linked_rows_digest(rows),
        "board_link_fields": list(STABLE_TASK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "board_full_file_hashed": False,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
    }


def validate_contract(contract: dict) -> None:
    expected = build_contract()
    for key, value in expected.items():
        if contract.get(key) != value:
            raise EvidenceError("contract_field_mismatch:" + key,
                                "CONTRACT_MISMATCH")
    if set(contract) != set(expected):
        raise EvidenceError("contract_key_mismatch", "CONTRACT_MISMATCH")


PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  (source:[A-Za-z0-9_./-]+|"
    r"sdk:[A-Za-z0-9_./-]+|"
    r"docs/task-evidence/neuralkalmanahs-covariance-reference-variants/"
    r"[A-Za-z0-9_./-]+)$")


def sources_bytes() -> bytes:
    rows = []
    for relative, expected in SOURCE_PINS.items():
        actual = sha256_file(SOURCE_ROOT / relative)
        if actual != expected:
            raise EvidenceError("source_pin_mismatch:" + relative,
                                "SOURCE_PIN_MISMATCH")
        rows.append((actual, "source:" + relative))
    for relative, expected in BOUNDARY_PINS.items():
        actual = sha256_file(WORKTREE / relative)
        if actual != expected:
            raise EvidenceError("boundary_pin_mismatch:" + relative,
                                "BOUNDARY_PIN_MISMATCH")
        rows.append((actual, "sdk:" + relative))
    for name in local_manifest_paths():
        path = HERE / name
        if not path.is_file():
            raise EvidenceError("local_pin_missing:" + name,
                                "LOCAL_PIN_MISSING")
        rows.append((sha256_file(path), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        "# SHA-256 pins for " + TASK + " task-local evidence.",
        "# source: paths are relative to the pinned research workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable full plan/swarm/TASKS.json is never hashed; only the "
        "stable row identity gates.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
        "# README.md is excluded to avoid a digest-table self-reference; its "
        "tables are checked against live bytes.",
    ]
    lines.extend(digest + "  " + path for digest, path in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_pin_lines(text: str) -> list:
    rows = []
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        match = PIN_LINE.fullmatch(line)
        if match is None:
            raise EvidenceError("malformed_pin_line:" + str(number),
                                "PIN_MALFORMED")
        digest, path = match.groups()
        if path in seen:
            raise EvidenceError("duplicate_pin:" + str(number),
                                "PIN_DUPLICATE")
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise EvidenceError("empty_pin_manifest", "PIN_EMPTY")
    return rows


def allowed_pin_keys() -> set:
    return ({"source:" + name for name in SOURCE_PINS}
            | {"sdk:" + name for name in BOUNDARY_PINS}
            | {TASK_PREFIX + name for name in local_manifest_paths()})


def _section_text(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if text.count(start) != 1:
        raise EvidenceError("readme_marker_count:" + section,
                            "README_MARKER")
    start_index = text.index(start) + len(start)
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise EvidenceError("readme_marker_missing:" + section,
                            "README_MARKER")
    return text[start_index:end_index]


def parse_readme_digest_tables(text: str) -> dict:
    result = {}
    for section in README_MARKERS:
        rows = []
        for line in _section_text(text, section).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or re.fullmatch(r"[0-9]+", cells[2]) is None:
                    raise EvidenceError("malformed_artifact_row:" + key,
                                        "README_ROW")
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise EvidenceError("malformed_digest_row:" + key,
                                        "README_ROW")
                digest = cells[1].strip("`")
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise EvidenceError("malformed_digest:" + key, "README_DIGEST")
            rows.append((key, digest))
        if len({key for key, _ in rows}) != len(rows):
            raise EvidenceError("duplicate_readme_row:" + section,
                                "README_DUPLICATE")
        result[section] = rows
    return result


def expected_readme_keys() -> dict:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": set(local_manifest_paths()),
    }


def verify_readme_digests(text: str) -> dict:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_MARKERS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            missing = sorted(expected[section] - actual_keys)
            extra = sorted(actual_keys - expected[section])
            raise EvidenceError(
                "readme_key_mismatch:" + section + ":missing=" + str(missing) +
                ":extra=" + str(extra), "README_KEYS")
        for key, digest in parsed[section]:
            if section == "source":
                expected_digest = SOURCE_PINS[key[len("source:"):]]
                path = SOURCE_ROOT / key[len("source:"):]
            elif section == "boundary":
                expected_digest = BOUNDARY_PINS[key[len("sdk:"):]]
                path = WORKTREE / key[len("sdk:"):]
            else:
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
            if digest != expected_digest:
                raise EvidenceError("readme_digest_mismatch:" + key,
                                    "README_DIGEST")
            if not path.is_file():
                raise EvidenceError("readme_pin_target_missing:" + key,
                                    "README_TARGET")
            if sha256_file(path) != digest:
                raise EvidenceError("readme_live_digest_mismatch:" + key,
                                    "README_DIGEST")
    for key, _ in parsed["artifacts"]:
        path = HERE / key
        line = ("| `" + key + "` | `" + sha256_file(path) + "` | " +
                str(path.stat().st_size) + " |")
        if line not in text:
            raise EvidenceError("readme_artifact_size_mismatch:" + key,
                                "README_SIZE")
    return {section: len(rows) for section, rows in parsed.items()}


def _render_table(section: str) -> str:
    start, end = README_MARKERS[section]
    lines = [start]
    if section == "source":
        lines.append("| Key | SHA-256 |")
        lines.append("| --- | --- |")
        for name in sorted(SOURCE_PINS):
            lines.append("| `source:" + name + "` | `" +
                         SOURCE_PINS[name] + "` |")
    elif section == "boundary":
        lines.append("| Key | SHA-256 |")
        lines.append("| --- | --- |")
        for name in sorted(BOUNDARY_PINS):
            lines.append("| `sdk:" + name + "` | `" + BOUNDARY_PINS[name] +
                         "` |")
    else:
        lines.append("| Path | SHA-256 | Bytes |")
        lines.append("| --- | --- | ---: |")
        for name in local_manifest_paths():
            path = HERE / name
            lines.append("| `" + name + "` | `" + sha256_file(path) + "` | " +
                         str(path.stat().st_size) + " |")
    lines.append(end)
    return "\n".join(lines)


def update_readme_tables(text: str) -> str:
    for section in README_MARKERS:
        block = _render_table(section)
        start, end = README_MARKERS[section]
        start_index = text.index(start)
        end_index = text.index(end, start_index) + len(end)
        text = text[:start_index] + block + text[end_index:]
    return text
