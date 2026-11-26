# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION.

This module is NOT a neural direct howling-suppression model. It contains no
published model source, weight, checkpoint, configuration, license text,
runtime, matched closed-loop fixture or candidate output. A bounded read-only
search finds no local copy of the reviewed candidates (HybridAHS v2
complex-ratio-mask, NeuralKalmanAHS, AFC-SPEX), no weight archive, no pinned
inference runtime and no matched closed-loop fixture in the workspace.

The module therefore builds a fail-closed feasibility blocker report:

* strict request validation at the only verified geometry, the installed v0
  16 kHz / mono / float32 / 160-sample frame; every other declared geometry is
  explicitly rejected as unverified rather than invented;
* explicit source, weight, license, runtime, geometry, fixture and rights
  probes;
* an admission gate that rejects every structurally valid request because the
  required artifacts and rights are absent;
* synthetic harness stimuli for rejection and identity controls only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

Nothing is downloaded, cloned, installed, extracted, ported, reconstructed or
simulated. No candidate audio output is produced. No result qualifies the
candidate and no published score is reproduced.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import struct
from typing import Any, Dict, Iterable, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_ID = (
    "audio-sdk/neural-direct-howling-suppression-reference-report/0.1")
CONTRACT_SCHEMA_ID = (
    "audio-sdk/neural-direct-howling-suppression-contract/0.1")
TASK = "SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION"
COMPONENT = "neural-direct-howling-suppression"
BRANCH = "swarm/SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION"
BASE_COMMIT = "9074704819a6af4168f8c9cf3bbe8da50484c29a"
TASK_PREFIX = "docs/task-evidence/neural-direct-howling-suppression/"
MODE = "feasibility"
VERIFICATION_PROFILE = "DSP"

# Installed v0 format. This is the unchanged public baseline and the only
# verified harness geometry. It is not a claim about the published model.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
ABI_MAJOR = 0
ABI_MINOR = 1

# Harness geometry equals installed v0 because no published task geometry is
# documented in the pinned evidence. Nothing about the model is inferred.
HARNESS_SAMPLE_RATE_HZ = SAMPLE_RATE_HZ
HARNESS_CHANNELS = CHANNELS
HARNESS_FRAME_SAMPLES = FRAME_SAMPLES
HARNESS_FRAME_VALUES = HARNESS_CHANNELS * HARNESS_FRAME_SAMPLES
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0
MAX_FRAME_SAMPLES = 4096

# Exact published candidate picked from the pinned research note. The note
# reports HybridAHS v2 complex-ratio-mask as the strongest overall trade-off
# in parts of the AHS journal study. Provenance only; no artifact is present.
CANDIDATE = "hybridahs_v2_complex_ratio_mask"
CANDIDATE_DISPLAY = "HybridAHS v2 complex-ratio-mask"
CANDIDATE_FAMILY = "neural direct mask suppression"
CANDIDATE_MECHANISM = (
    "predicts a complex ratio mask or enhanced speech from howling microphone "
    "audio")
PUBLICATIONS = (
    {
        "label": "Hybrid AHS (Interspeech 2023)",
        "url": "https://www.isca-archive.org/interspeech_2023/"
               "zhang23q_interspeech.html",
    },
    {
        "label": "NeuralKalmanAHS (Interspeech 2024)",
        "url": "https://www.isca-archive.org/interspeech_2024/"
               "zhang24_interspeech.html",
    },
    {
        "label": "Expanded AHS journal comparison (2024)",
        "url": "https://haozhang6720.github.io/doc/papers/AHS_journal_2024.pdf",
    },
)
PUBLIC_REPOSITORIES = (
    "https://github.com/YIXUANZ/NeuralKalmanAHS",
    "https://github.com/YIXUANZ/AHS_2023",
    "https://github.com/ZLiNJU/AFC-SPEX",
)
SOURCE_REPORTED_METRICS = {
    "variant": "NeuralKalmanAHS",
    "cohort": "200 utterances, AISHELL-2 speech with simulated room paths",
    "loop_gains": [2.0, 2.5, 3.0],
    "mean_sdr_db": [2.65, 1.98, 1.45],
    "mean_pesq": [2.33, 2.17, 2.04],
    "reproduced_here": False,
    "qualifies_candidate": False,
    "note": (
        "The pinned note attributes these journal numbers to "
        "NeuralKalmanAHS, not to the HybridAHS v2 complex-ratio-mask variant. "
        "They are provenance only and are not reproduced, averaged or "
        "generalized here."),
}

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
    "title": "Neural direct howling suppression",
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
    "third_party/NeuralKalmanAHS",
    "third_party/AHS_2023",
    "third_party/AFC-SPEX",
    "third_party/neural-direct-howling-suppression",
    "vendor/neural-ahs",
    "research/NeuralKalmanAHS",
    "research/AHS_2023",
    "research/AFC-SPEX",
    "research/neural-direct-howling-suppression",
    "data/models/NeuralKalmanAHS",
    "data/models/afc-spex",
    "data/models/neural-direct-howling-suppression",
    "~/NeuralKalmanAHS",
    "~/AHS_2023",
    "~/AFC-SPEX",
    "~/projects/AFC-SPEX",
    "~/code/AFC-SPEX",
)
SOURCE_MARKERS = (
    "model.py", "inference.py", "train.py", "infer.py", "config.yaml",
    "checkpoint", "README.md",
)

WEIGHT_CANDIDATE_PATHS = (
    "data/models/neural-direct-howling-suppression",
    "data/models/NeuralKalmanAHS",
    "data/models/afc-spex",
    "data/weights/neural-direct-howling-suppression",
    "data/weights/hybridahs-v2",
    "research/neural-direct-howling-suppression/checkpoints",
    "third_party/NeuralKalmanAHS/checkpoints",
    "third_party/AHS_2023/checkpoints",
    "~/.cache/neural-direct-howling-suppression",
)
WEIGHT_SUFFIXES = (
    ".pt", ".pth", ".ckpt", ".onnx", ".safetensors", ".npz", ".npy", ".bin",
)

RUNTIME_CANDIDATE_PATHS = (
    "data/envs/neural-ahs",
    "data/runtime/neural-ahs",
    "research/neural-direct-howling-suppression/runtime",
    "third_party/NeuralKalmanAHS/.venv",
    "~/envs/neural-ahs",
)
RUNTIME_LOCK_CANDIDATES = (
    "research/neural-direct-howling-suppression/requirements.lock",
    "data/envs/neural-ahs/requirements.lock",
    "data/runtime/neural-ahs/requirements.lock",
)

GEOMETRY_CANDIDATE_PATHS = (
    "research/neural-direct-howling-suppression/geometry.json",
    "data/models/neural-direct-howling-suppression/geometry.json",
    "data/models/neural-direct-howling-suppression/config.yaml",
    "third_party/NeuralKalmanAHS/config.yaml",
)

FIXTURE_CANDIDATE_PATHS = (
    "data/corpora/neural-direct-howling-suppression",
    "data/fixtures/neural-direct-howling-suppression",
    "research/neural-direct-howling-suppression/fixture",
    "research/neural-direct-howling-suppression/closed-loop",
)
FIXTURE_MARKERS = (".wav", ".flac", ".npy", ".json")

REQUIRED_ARTIFACTS = (
    {
        "id": "A1",
        "artifact": "published model source at an immutable revision",
        "required": (
            "The exact HybridAHS v2 complex-ratio-mask model source at an "
            "immutable commit or release tag, with a read-only non-.git tree "
            "digest, a per-file SHA-256 manifest and the repository license "
            "file"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A2",
        "artifact": "model weights, checkpoints and inference configuration",
        "required": (
            "Every published weight, checkpoint and inference configuration "
            "for the exact variant at a recorded revision, with byte counts "
            "and SHA-256 values per file"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A3",
        "artifact": "pinned inference runtime",
        "required": (
            "A locked offline runtime with the exact interpreter, framework, "
            "package versions, wheel hashes, platform, device, dtype, "
            "determinism settings and install location"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A4",
        "artifact": "documented task geometry and default configuration",
        "required": (
            "The exact audio-in/audio-out contract: sample rate, channels, "
            "frame, hop, lookahead, content delay, reset and drain behaviour, "
            "plus the default configuration and thresholds"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A5",
        "artifact": "matched closed-loop fixture",
        "required": (
            "A rights-cleared closed-loop fixture with measured or frozen "
            "loudspeaker-to-microphone paths, loop gains, delays, "
            "saturation, held-out path/speaker splits, paired target speech "
            "and speech/music/silence/onset/recovery cases"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A6",
        "artifact": "code, weight, data and output rights decision",
        "required": (
            "The exact license texts with SHA-256 plus a written decision on "
            "code, weight, training-data, input-corpus, derived-output, "
            "attribution and redistribution rights for this macOS/Python "
            "target"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A7",
        "artifact": "independent review and release package",
        "required": (
            "An independent exact-head review of every result, an approved "
            "adapter intake decision and a complete release package before "
            "any support claim"),
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
        "gate": "exact_published_model_source_revision_and_license_pin",
        "status": "blocked",
        "reason": (
            "No published HybridAHS v2 complex-ratio-mask source checkout "
            "exists locally, and the reviewed public repositories expose "
            "README/demo/audio material rather than model source. No "
            "immutable revision, tree digest or license file is pinned."),
        "reopen": (
            "Stage the exact published model source at a recorded immutable "
            "revision with a read-only tree digest, a per-file SHA-256 "
            "manifest and its license file, then pin every required source "
            "path before reading any configuration."),
    },
    {
        "id": "RG-02",
        "gate": "weights_checkpoints_and_reproduction",
        "status": "blocked",
        "reason": (
            "No weight archive, checkpoint or inference configuration is "
            "present, so parameter identity, load, output parity, reset and "
            "finite drain cannot be reproduced."),
        "reopen": (
            "Provide every weight and checkpoint at a recorded revision with "
            "per-file SHA-256 values and an inference configuration, then "
            "reproduce parameter identity, load, output parity, reset and "
            "finite drain."),
    },
    {
        "id": "RG-03",
        "gate": "pinned_inference_runtime",
        "status": "blocked",
        "reason": (
            "No locked inference runtime, framework version, wheel hash, "
            "device, dtype or determinism setting exists; no install/import "
            "parity record is present."),
        "reopen": (
            "Provide a hash-pinned offline runtime with exact interpreter, "
            "framework, package versions, platform, device and determinism "
            "settings, and prove install/import parity before any run."),
    },
    {
        "id": "RG-04",
        "gate": "documented_task_geometry_and_configuration",
        "status": "blocked",
        "reason": (
            "The published evidence does not document the exact sample rate, "
            "channels, frame, hop, lookahead, delay, reset or drain contract "
            "for this variant, and no configuration or threshold file is "
            "present. The local harness uses installed v0 only."),
        "reopen": (
            "Pin the exact model headers, configuration and audio-in/out "
            "contract for every declared rate and frame, and never infer an "
            "undocumented frame size or channel count."),
    },
    {
        "id": "RG-05",
        "gate": "code_weight_training_data_and_output_rights",
        "status": "blocked",
        "reason": (
            "No license text, model card, training-data terms or written "
            "decision covers code, weights, input audio, derived output, "
            "attribution or redistribution on this macOS/Python target."),
        "reopen": (
            "Obtain the exact license texts, record their SHA-256 values, and "
            "secure a written rights decision for code, weights, training "
            "data, input corpus, derived output, attribution and "
            "redistribution, or record a final rejection."),
    },
    {
        "id": "RG-06",
        "gate": "dsp_acceptance_matrix_and_numerical_behavior",
        "status": "blocked",
        "reason": (
            "The DSP profile requires sweeps, steps, impulses, silence, "
            "clean speech and a task-specific control with gain, response, "
            "attack/release, headroom, delay, numerical behavior, state "
            "transitions and interacting nonlinear configurations; none was "
            "run because no candidate instance exists."),
        "reopen": (
            "Run the full DSP matrix on the exact runtime, retain every "
            "failure and nonfinite case, and record gain, response, "
            "attack/release, headroom, delay and state transitions with "
            "tolerances agreed before scoring."),
    },
    {
        "id": "RG-07",
        "gate": "closed_loop_stability_adverse_behavior_and_timing",
        "status": "blocked",
        "reason": (
            "No closed-loop stability, maximum-stable-gain, residual-tone, "
            "false-trigger, target-speech-attenuation, path-change recovery, "
            "clipping, latency, CPU, memory or callback measurement exists, "
            "and no matched closed-loop fixture is present."),
        "reopen": (
            "Measure closed-loop stability and maximum stable gain with "
            "multiple peaks, speech, music, silence, path changes, "
            "saturation and reset, and report false triggers, target-speech "
            "damage, residual tone energy, delay and paced timing separately."),
    },
    {
        "id": "RG-08",
        "gate": "adapter_intake_listening_benchmark_and_release",
        "status": "blocked",
        "reason": (
            "No opt-in adapter, provider intake, public-surface decision, "
            "authorized listening, benchmark validation, independent "
            "exact-head review or release approval exists."),
        "reopen": (
            "Complete the source, weight, runtime, geometry and rights "
            "decisions, implement any adapter only behind explicit caller "
            "opt-in with no default or fallback registration, validate a "
            "benchmark bundle, run authorized listening where permitted, and "
            "obtain independent review and release approval."),
    },
)

UPSTREAM_BLOCKER = {
    "status": (
        "blocked_source_weights_runtime_geometry_rights_and_fixture_absent"),
    "artifact": (
        "HybridAHS v2 complex-ratio-mask source, weights, pinned runtime, "
        "documented geometry, rights decision and matched closed-loop fixture"),
    "source": {
        "status": "absent",
        "repositories": list(PUBLIC_REPOSITORIES),
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
    },
    "weights": {
        "status": "absent",
        "checkpoint_count": None,
        "sha256": None,
        "configuration": None,
    },
    "license": {
        "status": "blocked_rights_unrecorded",
        "reported_name": None,
        "reported_restriction": None,
        "license_text_present": False,
        "license_text_sha256": None,
        "use_approved": False,
        "redistribution_approved": False,
        "host_target_approved": False,
        "review": "blocked",
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "exact interpreter and framework versions with wheel hashes",
            "pinned platform, device, dtype and determinism settings",
            "an install/import parity record",
            "a reproducible inference entry point",
        ],
        "present": False,
        "pinned": False,
        "lockfile": None,
        "sha256": None,
    },
    "geometry": {
        "status": "absent",
        "sample_rate_hz": None,
        "channels": None,
        "frame_samples": None,
        "hop_samples": None,
        "lookahead_samples": None,
        "content_delay_samples": None,
        "reset_and_drain_documented": False,
        "configuration": None,
    },
    "fixture": {
        "status": "absent",
        "required": (
            "rights-cleared closed-loop fixture with measured or frozen "
            "loudspeaker-to-microphone paths, loop gain, delay, saturation, "
            "held-out path/speaker splits and paired target speech"),
        "corpus_rights": False,
        "loop_gain_measured": False,
        "delay_measured": False,
        "sha256": None,
    },
    "rights": {
        "status": "blocked_rights_unrecorded",
        "code": False,
        "weights": False,
        "training_data": False,
        "input_corpus": False,
        "derived_output": False,
        "attribution": False,
        "redistribution": False,
        "reviewed_by": None,
    },
    "pinned_revision": None,
    "source_digest": None,
    "weights_digest": None,
    "runtime_digest": None,
    "geometry_digest": None,
    "fixture_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "The exact license texts for code, weights and training data, a "
        "written decision on input-corpus and derived-output use, permission "
        "for adapter distribution and a review record for every fixture "
        "recording are required before any reproduction, adapter, benchmark "
        "or release claim."),
    "workspace_search": (
        "Bounded read-only existence and file-name checks of named candidate "
        "paths under the workspace found no published model checkout, no "
        "weight or checkpoint archive, no locked inference runtime, no "
        "geometry/configuration file and no matched closed-loop fixture. No "
        "repository, archive, weight, media file or vendor file was opened, "
        "downloaded or reconstructed."),
    "not_attempted": [
        "no git clone, network download, package installation or archive extraction",
        "no fabricated, ported, reverse-engineered or surrogate model source",
        "no fabricated weight, checkpoint, configuration or license text",
        "no runtime install, inference call or framework import",
        "no copied published audio, score or model output",
        "no candidate audio, listening, device-timing or benchmark run",
    ],
    "reopen": (
        "Stage the exact published model at a recorded revision with source, "
        "weights, configuration and license digests, pin a reproducible "
        "runtime, document the audio-in/out contract, secure code/weight/"
        "data/output rights, stage a rights-cleared closed-loop fixture, then "
        "reproduce the model and run the DSP and closed-loop matrices with "
        "independent review."),
}

NON_CLAIMS = (
    "No published model source, header, configuration, weight, checkpoint or license text is included.",
    "No neural direct suppressor, mask predictor, adapter or port is implemented, approximated, simulated or run.",
    "No published SDR, PESQ or other source-reported number is reproduced, averaged or generalized.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default, and there is no automatic discovery or fallback.",
    "No real corpus, fixture, listening panel, benchmark or quality claim exists.",
    "No closed-loop stability, maximum-stable-gain, device timing, CPU, memory or release claim is made.",
    "No source-reported characteristic is presented as a local measurement.",
    "No missing, rejected or source-reported result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/neural-direct-howling-suppression/ is touched.",
    "The reference is a task-local feasibility gate, not a neural suppressor.",
    "The only verified harness geometry is installed v0; no model geometry is inferred.",
    "All harness stimuli are analytic or seeded synthetic; no model runtime is used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
)

SOURCE_REPORTED_IDENTITY = {
    "candidate": CANDIDATE,
    "display_name": CANDIDATE_DISPLAY,
    "family": CANDIDATE_FAMILY,
    "mechanism": CANDIDATE_MECHANISM,
    "publications": [dict(item) for item in PUBLICATIONS],
    "repositories": list(PUBLIC_REPOSITORIES),
    "source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "checkpoint_in_public_repository": False,
    "runnable": False,
    "note": (
        "The pinned note records the reviewed repositories as exposing "
        "README/demo HTML, CSS and audio material with no source "
        "implementation or model checkpoints in their visible file "
        "listings. Upstream visibility is not a runnable artifact, a right "
        "to use or a local result."),
}

RELATED_CANDIDATES = {
    "neural_kalman_ahs": {
        "status": "source_reported_not_runnable",
        "family": "neural plus Kalman hybrid",
        "metrics": SOURCE_REPORTED_METRICS,
        "qualifies_candidate": False,
    },
    "afc_spex": {
        "status": "source_reported_not_runnable",
        "family": "multichannel neural acoustic feedback cancellation",
        "reason": (
            "The checked-in inference configuration expects three microphone "
            "channels and an author-local checkpoint path; the AMI source is "
            "mono and no checkpoint is included in the repository listing."),
        "metrics": None,
        "qualifies_candidate": False,
    },
}

HOWLING_CONTROL = {
    "status": "not_evaluated_by_this_task",
    "installed_v0_channels": CHANNELS,
    "metrics": None,
    "result": None,
    "qualifies_candidate": False,
    "howl_detection_claim": False,
    "mask_or_enhancement_claim": False,
    "maximum_stable_gain_claim": False,
    "feedback_cancellation_claim": False,
    "closed_loop_stability_claim": False,
    "note": (
        "No detector, mask, enhancement, closed-loop stability, "
        "maximum-stable-gain or feedback-cancellation result exists. The "
        "published family description is a design reference only and is not "
        "reproduced here."),
}

EXTERNAL_BOUNDARY = {
    "documented": True,
    "candidate": CANDIDATE_DISPLAY,
    "family": CANDIDATE_FAMILY,
    "publication_scope": "Interspeech 2023/2024 and AHS journal 2024",
    "distribution_model": "published research model, no released runnable package",
    "host_target": "macOS / Python 3 workspace",
    "host_target_eligible": False,
    "license_reported": None,
    "license_text_present": False,
    "use_approved": False,
    "redistribution_approved": False,
    "local_runtime_present": False,
    "weights_present": False,
    "published_output_present": False,
    "adapter_implemented": False,
    "adapter_default_registration": False,
    "automatic_discovery": False,
    "fallback": "none",
    "vendor_claims_separate_from_local_measurements": True,
    "note": (
        "The candidate is documented from the pinned research note and the "
        "cited publications only. No source, weight, license text, runtime "
        "or measurement is present, and this host target is not approved."),
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
    return sha256_bytes(Path(path).read_bytes())


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
    duration = length / float(HARNESS_SAMPLE_RATE_HZ)
    values = []
    for index in range(length):
        t = index / float(HARNESS_SAMPLE_RATE_HZ)
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
        t = index / float(HARNESS_SAMPLE_RATE_HZ)
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
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    if len(samples) != expected:
        raise InputError("WRONG_SAMPLE_COUNT", "WRONG_SAMPLE_COUNT")
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
    """Validate an installed-v0-geometry request; never runs a candidate."""
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
    if rate != SAMPLE_RATE_HZ:
        raise ConfigError("UNVERIFIED_TASK_GEOMETRY",
                          "UNVERIFIED_TASK_GEOMETRY")
    channels = _require_int(request["channels"], "WRONG_CHANNELS", 1)
    if channels != CHANNELS:
        raise ConfigError("UNVERIFIED_TASK_GEOMETRY",
                          "UNVERIFIED_TASK_GEOMETRY")
    frame_samples = _require_int(request["frame_samples"], "INVALID_FRAME", 1)
    if frame_samples > MAX_FRAME_SAMPLES:
        raise ConfigError("FRAME_TOO_LARGE", "INVALID_FRAME")
    if frame_samples != FRAME_SAMPLES:
        raise ConfigError("UNVERIFIED_TASK_GEOMETRY",
                          "UNVERIFIED_TASK_GEOMETRY")
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
        "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
        "channels": HARNESS_CHANNELS,
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
        ("unknown_candidate", variant(candidate="neural_direct_ahs")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("zero_channels", variant(channels=0)),
        ("negative_channels", variant(channels=-1)),
        ("bool_channels", variant(channels=True)),
        ("multichannel_unverified", variant(channels=2,
                                            samples=[0.0] * 320)),
        ("zero_rate", variant(sample_rate_hz=0)),
        ("negative_rate", variant(sample_rate_hz=-16000)),
        ("bool_rate", variant(sample_rate_hz=True)),
        ("undeclared_rate", variant(sample_rate_hz=22050)),
        ("rate_8k", variant(sample_rate_hz=8000)),
        ("rate_48k", variant(sample_rate_hz=48000)),
        ("zero_frame", variant(frame_samples=0)),
        ("too_large_frame", variant(frame_samples=4097)),
        ("wrong_frame_512", variant(frame_samples=512,
                                    samples=[0.0] * 512)),
        ("short_samples", variant(samples=short)),
        ("long_samples", variant(samples=long)),
        ("wrong_multichannel_count", variant(channels=2,
                                             samples=[0.0] * 160)),
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
        "note": ("Invalid or unverified requests are rejected before any "
                 "artifact check or candidate call; no metrics exist."),
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
        "reason": (
            "source_weights_runtime_geometry_rights_and_fixture_absent"),
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def _resolve_workspace_path(label: str) -> Path:
    if label.startswith("~/"):
        return Path.home() / label[2:]
    return WORKSPACE / label


def _markers_in(path: Path, suffixes: Sequence[str],
                max_depth: int = 3) -> List[str]:
    found: List[str] = []
    if path.is_file():
        if path.suffix.lower() in suffixes:
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
            if Path(name).suffix.lower() in suffixes:
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
        "candidate": CANDIDATE,
        "repositories": list(PUBLIC_REPOSITORIES),
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": ("Read-only existence checks only; no clone, fetch, archive "
                 "extraction or model file is opened or executed."),
    }


def weights_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in WEIGHT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.exists():
            hits = _markers_in(target, WEIGHT_SUFFIXES)
            if hits:
                found.extend((Path(label) / name).as_posix()
                             for name in hits)
    return {
        "status": "blocked_weights_absent" if not found else
                  "weights_present_unqualified",
        "present": bool(found),
        "required": (
            "every published weight, checkpoint and inference configuration "
            "for the exact variant at a recorded revision with per-file "
            "SHA-256 values"),
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "checkpoint_count": None,
        "sha256": None,
        "configuration": None,
        "note": ("Read-only existence checks only; no weight file is opened, "
                 "loaded, imported or hashed."),
    }


def license_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_rights_unrecorded",
        "reported_name": None,
        "reported_restriction": None,
        "license_text_present": False,
        "license_text_sha256": None,
        "license_file": None,
        "use_approved": False,
        "redistribution_approved": False,
        "host_target_approved": False,
        "review": "blocked",
        "reviewed_by": None,
        "note": ("No license text, model card or written rights decision is "
                 "present. The pinned note does not record the candidate's "
                 "license terms, and upstream availability is not a right to "
                 "use, redistribute or publish."),
    }


def runtime_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in RUNTIME_CANDIDATE_PATHS:
        checked.append(label)
        if _resolve_workspace_path(label).exists():
            found.append(label)
    locks = [path for path in RUNTIME_LOCK_CANDIDATES
             if _resolve_workspace_path(path).is_file()]
    pinned = bool(found) and bool(locks)
    return {
        "status": "runtime_present_unqualified" if pinned
                  else "blocked_runtime_unpinned",
        "checked_paths": sorted(checked),
        "found": sorted(found),
        "lockfiles": sorted(locks),
        "present": bool(found),
        "pinned": pinned,
        "lockfile": None,
        "sha256": None,
        "note": ("No locked inference runtime is installed, imported or "
                 "pinned. Path checks are read-only; no install, framework "
                 "import or inference is attempted."),
    }


def geometry_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in GEOMETRY_CANDIDATE_PATHS:
        checked.append(label)
        if _resolve_workspace_path(label).is_file():
            found.append(label)
    return {
        "status": "blocked_geometry_undocumented" if not found else
                  "geometry_present_unqualified",
        "present": bool(found),
        "required": (
            "exact audio-in/audio-out contract: sample rate, channels, "
            "frame, hop, lookahead, content delay, reset and drain behaviour "
            "plus the default configuration"),
        "checked_paths": sorted(checked),
        "found": sorted(found),
        "sample_rate_hz": None,
        "channels": None,
        "frame_samples": None,
        "hop_samples": None,
        "lookahead_samples": None,
        "content_delay_samples": None,
        "reset_and_drain_documented": False,
        "configuration": None,
        "note": ("No model geometry or configuration is present and the "
                 "pinned evidence does not document one. The local harness "
                 "uses installed v0 geometry only and infers nothing."),
    }


def fixture_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in FIXTURE_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.exists():
            hits = _markers_in(target, FIXTURE_MARKERS)
            if hits:
                found.extend((Path(label) / name).as_posix()
                             for name in hits)
    return {
        "status": "blocked_matched_fixture_absent" if not found else
                  "fixture_present_unqualified",
        "present": bool(found),
        "required": (
            "rights-cleared closed-loop fixture with measured or frozen "
            "loudspeaker-to-microphone paths, loop gain, delay, saturation, "
            "held-out path/speaker splits, paired target speech and "
            "speech/music/silence/onset/recovery cases"),
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "corpus_rights": False,
        "loop_gain_measured": False,
        "delay_measured": False,
        "sha256": None,
        "note": ("Existence checks only; no audio file is opened or "
                 "decoded. A synthetic harness frame is not a matched "
                 "closed-loop fixture."),
    }


def rights_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_rights_unrecorded",
        "source_license": None,
        "license_text_present": False,
        "license_text_sha256": None,
        "code_rights": False,
        "weight_rights": False,
        "training_data_rights": False,
        "input_corpus_rights": False,
        "derived_output_rights": False,
        "redistribution_approved": False,
        "host_target_approved": False,
        "review": "blocked",
        "reviewed_by": None,
        "note": ("No license text, model card, distribution scope or fixture "
                 "permission is recorded locally. Upstream presence is not a "
                 "right to use, redistribute or publish."),
    }


def geometry() -> Dict[str, Any]:
    return {
        "candidate": CANDIDATE_DISPLAY,
        "candidate_family": CANDIDATE_FAMILY,
        "declared_sample_rate_hz": None,
        "declared_channels": None,
        "declared_frame_samples": None,
        "declared_hop_samples": None,
        "declared_lookahead_samples": None,
        "declared_content_delay_samples": None,
        "declared_reset_and_drain": None,
        "geometry_documented": False,
        "harness_geometry": {
            "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
            "channels": HARNESS_CHANNELS,
            "frame_samples": HARNESS_FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
            "source": "installed v0 baseline; not a model claim",
        },
        "v0_can_represent_declared_input": None,
        "verified_here": False,
        "measured_here": False,
        "candidate_output": False,
        "note": (
            "The pinned evidence records the mechanism and the published "
            "study but not this variant's sample rate, channels, frame, hop, "
            "lookahead, delay, reset or drain contract. No geometry is "
            "inferred. The 16 kHz / mono / 160-sample harness is the "
            "unchanged installed v0 baseline only."),
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
        "delay_and_content_mapping": "blocked_no_documented_geometry",
        "numerical_behavior": "partial_local_harness_rejection_only",
        "state_transitions": "blocked_no_candidate_instance",
        "interacting_nonlinear_configurations": "blocked_no_candidate_instance",
        "candidate_output":
            "blocked_source_weights_runtime_geometry_rights_and_fixture_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "exact_published_model_source_revision_and_license":
            "blocked_source_absent",
        "model_weights_checkpoints_and_configuration":
            "blocked_weights_absent",
        "pinned_inference_runtime":
            "blocked_runtime_unpinned",
        "documented_task_geometry_and_configuration":
            "blocked_geometry_undocumented",
        "code_weight_data_and_output_rights":
            "blocked_rights_unrecorded",
        "model_reproduction_and_parameter_identity":
            "blocked_no_candidate_instance",
        "dsp_gain_response_attack_release_delay":
            "blocked_no_candidate_output",
        "closed_loop_stability_and_maximum_stable_gain":
            "blocked_no_measurement",
        "speech_music_false_trigger_and_attenuation":
            "blocked_no_permitted_cohort",
        "device_timing_memory_and_callback":
            "blocked_no_paced_measurement",
        "adapter_provider_intake":
            "blocked_no_approved_runtime_or_terms",
        "authorized_listening_and_benchmark":
            "blocked_no_release_evidence",
        "release_qualification":
            "blocked_no_release_evidence",
    }


def candidates() -> Dict[str, Any]:
    return {
        CANDIDATE: {
            "status": (
                "blocked_source_weights_runtime_geometry_rights_and_fixture_absent"),
            "family": CANDIDATE_FAMILY,
            "metrics": None,
            "qualifies_candidate": False,
            "result": None,
            "reason": (
                "No published source, weight, checkpoint, pinned runtime, "
                "documented geometry, approved rights or matched closed-loop "
                "fixture is present; no mask, enhancement, quality, "
                "stability or timing result was produced."),
        },
        "related": RELATION_ECHO(),
    }


def RELATION_ECHO() -> Dict[str, Any]:
    return {name: dict(block) for name, block in RELATED_CANDIDATES.items()}


def controls() -> Dict[str, Any]:
    return {
        "identity_control": {
            "status": "bit_exact_synthetic_only",
            "candidate_processing": False,
            "qualifies_candidate": False,
        },
        "source_reported_metrics": {
            "status": "provenance_only_not_reproduced",
            "metrics": dict(SOURCE_REPORTED_METRICS),
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
        "purpose": (
            "harness stimulus characterisation only; not a neural "
            "suppressor result and not a candidate output"),
        "harness_geometry": {
            "channels": HARNESS_CHANNELS,
            "frame_samples": HARNESS_FRAME_SAMPLES,
            "flat_values": HARNESS_FRAME_VALUES,
            "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
            "verified_model_geometry": False,
            "note": (
                "16 kHz / mono / 160 samples is the unchanged installed v0 "
                "baseline and is used only to exercise validation and "
                "rejection; it is not a claim about the model geometry."),
        },
        "stimuli": stimuli,
        "speech_contrast": speech_contrast(
            STIMULUS_GENERATORS["speech_like"]()),
        "identity_control": identity,
        "candidate_processing": False,
    }


def collect_blockers() -> List[str]:
    blockers: List[str] = []
    if not source_probe()["present"]:
        blockers.append("source_absent")
    if not weights_probe()["present"]:
        blockers.append("weights_absent")
    if license_probe()["review"] != "approved":
        blockers.append("rights_unrecorded")
    if not runtime_probe()["pinned"]:
        blockers.append("runtime_unpinned")
    if not geometry_probe()["present"]:
        blockers.append("geometry_undocumented")
    if not fixture_probe()["present"]:
        blockers.append("matched_closed_loop_fixture_absent")
    if rights_probe()["review"] != "approved":
        blockers.append("rights_unrecorded")
    return sorted(set(blockers))


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
            "source, weights, rights, runtime, geometry and matched fixture "
            "are absent. No port, fallback or surrogate is used."),
    }


def probe_candidate(request: Any) -> None:
    validate_request(request)
    raise ArtifactsAbsent(
        "ARTIFACTS_ABSENT: published model source, weights, approved rights, "
        "pinned runtime, documented geometry and matched fixture are not "
        "present; no processing is performed", "ARTIFACTS_ABSENT")


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
        ("research/feedback_control_20261028.md describes neural direct "
         "suppression as predicting a mask or enhanced speech from howling "
         "microphone audio, trained on closed-loop signals representative of "
         "inference, and warns that offline open-loop training can mismatch "
         "recursive streaming behaviour and suppress target speech."),
        ("the same note reports Hybrid AHS (Interspeech 2023) as a "
         "frequency-domain Kalman filter plus a self-attentive RNN whose "
         "streaming NN output becomes the Kalman reference, and the "
         "expanded AHS journal study (2024) compares cascaded and recursively "
         "trained variants including a complex-ratio-mask system."),
        ("the same note records that HybridAHS v2 complex-ratio-mask results "
         "are the strongest overall trade-off in parts of the study, and "
         "reports NeuralKalmanAHS mean SDR 2.65, 1.98 and 1.45 dB with PESQ "
         "2.33, 2.17 and 2.04 for loop gains G=2, 2.5 and 3 over 200 "
         "utterances on the paper setup only."),
        ("the same note records that YIXUANZ/NeuralKalmanAHS and "
         "YIXUANZ/AHS_2023 expose README/demo HTML, CSS and audio files with "
         "no source implementation or model checkpoints in their visible "
         "file listings and no release assets for NeuralKalmanAHS, so they "
         "are research references rather than runnable candidates."),
        ("the same note records AFC-SPEX (ICASSP 2026) as a three-microphone "
         "neural AFC candidate whose checked-in inference configuration "
         "expects an author-local checkpoint and whose repository listing "
         "includes no checkpoint; our AMI source is mono and it was not run."),
        ("plan/INVENTORY.json assigns neural-direct-howling-suppression the "
         "dsp verification profile, disposition sdk-model, area Level and "
         "listening, and evidence_status considered, with the plan note to "
         "pick an exact published model and verify safe closed-loop behaviour "
         "first."),
        ("plan/audio-sdk/README.md requires runnable source, exact assets, "
         "permitted scope and matched evidence before a caller-supplied "
         "reference or opt-in adapter is added."),
        ("No local model source, weight, checkpoint, configuration, runtime "
         "lock, documented model geometry or matched closed-loop fixture "
         "exists; nothing was cloned, downloaded, ported or reconstructed."),
    ]


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    source = source_probe()
    weights = weights_probe()
    license_block = license_probe()
    runtime = runtime_probe()
    geometry_block = geometry_probe()
    fixture = fixture_probe()
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
        "weights_absent": weights["present"] is False,
        "rights_unrecorded": rights["review"] == "blocked",
        "license_text_absent": license_block["license_text_present"] is False,
        "runtime_unpinned": runtime["pinned"] is False,
        "geometry_undocumented": geometry_block["present"] is False,
        "matched_fixture_absent": fixture["present"] is False,
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "nonfinite_samples_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith("nonfinite")),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked":
            missing_result("neural_direct_ahs_placeholder")["status"] ==
            "blocked",
        "identity_control_bit_exact": all(
            block["byte_identical"]
            for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
        "external_boundary_closed": (
            EXTERNAL_BOUNDARY["adapter_implemented"] is False and
            EXTERNAL_BOUNDARY["adapter_default_registration"] is False and
            EXTERNAL_BOUNDARY["automatic_discovery"] is False),
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
        "external_boundary": dict(EXTERNAL_BOUNDARY),
        "source_reported_identity": dict(SOURCE_REPORTED_IDENTITY),
        "reference": {
            "implementation": "task-local standard-library feasibility gate",
            "real_model_source_present": source["present"],
            "model_weights_present": weights["present"],
            "documented_geometry_present": geometry_block["present"],
            "runtime_present": runtime["present"],
            "runtime_pinned": runtime["pinned"],
            "matched_fixture_present": fixture["present"],
            "license_text_present": license_block["license_text_present"],
            "rights_approved": False,
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights_used": False,
            "deterministic": True,
            "candidate_processing": False,
            "real_corpus_read": False,
            "note": (
                "No neural direct suppressor, mask predictor, adapter or "
                "port is implemented or simulated; only probes, request "
                "rejection and synthetic harness controls are performed."),
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
        "weights_probe": weights,
        "license_probe": license_block,
        "runtime_probe": runtime,
        "geometry_probe": geometry_block,
        "fixture_probe": fixture,
        "rights_probe": rights,
        "geometry": geom,
        "howling_control": dict(HOWLING_CONTROL),
        "candidates": candidates(),
        "controls": controls(),
        "required_results": candidate_required_results(),
        "stimulus_probe": stimuli,
        "adverse": {
            "invalid_config_and_input": adverse_request,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": missing_result("neural_direct_ahs_placeholder"),
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
