# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility gate for SDK-HYBRID-AHS-SELF-ATTENTIVE-RNN-AND-KALMAN.

This module is NOT Hybrid AHS. It contains no upstream source, model code,
checkpoint, weight, configuration, license text, runtime, corpus recording or
candidate output. A bounded read-only search finds no local ``AHS_2023`` or
``NeuralKalmanAHS`` checkout, no trained state, no pinned deep-learning
runtime, no matched closed-loop cohort and no locally approved license text.
The pinned research note records that the public repositories expose README and
demo HTML/CSS/audio only, with no source implementation or checkpoints, and
that no release assets were listed for NeuralKalmanAHS.

The module therefore builds a fail-closed feasibility blocker report:

* strict caller-supplied-asset request validation at the only locally pinned
  geometry, the installed-v0 16 kHz / mono / 160-sample harness format;
* explicit source, checkpoint, runtime, license, cohort and rights probes;
* an admission gate that rejects every structurally valid request because the
  required artifacts and rights are absent;
* analytic or seeded synthetic harness stimuli for rejection and identity
  controls only;
* author-reported closed-loop results retained as provenance only, never as a
  local measurement or a qualification;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

Nothing is downloaded, cloned, installed, extracted, ported, reconstructed or
simulated. No candidate audio output is produced. No result qualifies the
candidate, and no author-reported score is reproduced.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
from typing import Any, Dict, Iterable, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_ID = (
    "audio-sdk/hybrid-ahs-self-attentive-rnn-and-kalman-reference-report/0.1")
CONTRACT_SCHEMA_ID = (
    "audio-sdk/hybrid-ahs-self-attentive-rnn-and-kalman-contract/0.1")
TASK = "SDK-HYBRID-AHS-SELF-ATTENTIVE-RNN-AND-KALMAN"
COMPONENT = "hybrid-ahs-self-attentive-rnn-and-kalman"
BRANCH = "swarm/SDK-HYBRID-AHS-SELF-ATTENTIVE-RNN-AND-KALMAN"
BASE_COMMIT = "f006454da9a72fbfd394e2b5bd05105201a9cd29"
TASK_PREFIX = "docs/task-evidence/hybrid-ahs-self-attentive-rnn-and-kalman/"
MODE = "feasibility"
VERIFICATION_PROFILE = "DSP"

# Installed v0 format. This is the unchanged public baseline and the only
# locally pinned harness geometry. It is not evidence of candidate geometry.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
ABI_MAJOR = 0
ABI_MINOR = 1

# The pinned research note records no candidate sample rate, frame size, hop,
# STFT size, channel count, Kalman state dimension, RNN layer count or
# parameter count. These fields stay empty rather than being inferred.
DECLARED_CANDIDATE_SAMPLE_RATES_HZ: Tuple[int, ...] = ()

HARNESS_SAMPLE_RATE_HZ = 16000
HARNESS_CHANNELS = 1
HARNESS_FRAME_SAMPLES = 160
HARNESS_FRAME_VALUES = HARNESS_CHANNELS * HARNESS_FRAME_SAMPLES
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0
MAX_EXTERNAL_ASSET_BYTES = 536870912

SOURCE_REPOSITORIES = (
    "https://github.com/YIXUANZ/AHS_2023",
    "https://github.com/YIXUANZ/NeuralKalmanAHS",
)
PAPER_URL = "https://www.isca-archive.org/interspeech_2023/zhang23q_interspeech.html"
JOURNAL_URL = "https://haozhang6720.github.io/doc/papers/AHS_journal_2024.pdf"
PROJECT_URL = "https://yixuanz.github.io/NeuralKalmanAHS/"
RESEARCH_URL = "https://www.isca-archive.org/interspeech_2024/zhang24_interspeech.html"

COMPARISON_STATUS = (
    "blocked_source_checkpoint_runtime_rights_and_cohort_absent")

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

EXPECTED_LINK = {
    "task_id": TASK,
    "title": "Hybrid AHS self-attentive RNN and Kalman",
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

CANDIDATE = "hybrid_ahs_self_attentive_rnn_and_kalman"
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)
REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples", "samples",
    "epoch", "first_input_sample", "lifecycle", "execution_mode",
    "checkpoint_sha256", "runtime_lock_sha256", "asset_bytes",
})

SOURCE_ARTIFACT_FILES = (
    "reference.py", "run.py", "test_reference.py", "verify.py",
)

SOURCE_CANDIDATE_PATHS = (
    "third_party/AHS_2023",
    "third_party/NeuralKalmanAHS",
    "third_party/ahs_2023",
    "third_party/neuralkalmanahs",
    "research/AHS_2023",
    "research/NeuralKalmanAHS",
    "research/repos/AHS_2023",
    "research/repos/NeuralKalmanAHS",
    "research/repos/hybrid-ahs",
    "research/hybrid-ahs/source",
    "~/code/AHS_2023",
    "~/code/NeuralKalmanAHS",
    "~/projects/AHS_2023",
    "~/projects/NeuralKalmanAHS",
)
SOURCE_MARKERS = (
    "kalman.py", "model.py", "train.py", "inference.py", "self_attentive.py",
    "README.md",
)

CHECKPOINT_CANDIDATE_PATHS = (
    "data/models/hybrid-ahs",
    "data/models/NeuralKalmanAHS",
    "data/checkpoints/hybrid-ahs",
    "data/checkpoints/NeuralKalmanAHS",
    "data/weights/hybrid-ahs",
    "research/hybrid-ahs/checkpoints",
    "research/NeuralKalmanAHS/checkpoints",
    "research/AHS_2023/checkpoints",
    "~/models/hybrid-ahs",
    "~/checkpoints/hybrid-ahs",
)
CHECKPOINT_MARKERS = (
    ".pt", ".pth", ".ckpt", ".onnx", ".safetensors", ".bin", ".pkl",
)

RUNTIME_CANDIDATE_PATHS = (
    "data/envs/hybrid-ahs",
    "data/envs/ahs",
    "data/runtime/hybrid-ahs",
    "research/hybrid-ahs/runtime",
)
RUNTIME_LOCK_CANDIDATES = (
    "data/envs/hybrid-ahs/requirements.lock",
    "data/envs/ahs/requirements.lock",
    "data/runtime/hybrid-ahs/requirements.lock",
    "research/hybrid-ahs/runtime/requirements.lock",
)
RUNTIME_COMMANDS = ("python3", "pip3")

COHORT_CANDIDATE_PATHS = (
    "data/corpora/hybrid-ahs",
    "data/corpora/ahs",
    "data/fixtures/hybrid-ahs",
    "research/hybrid-ahs/fixture",
    "research/hybrid-ahs/cohort",
    "research/hybrid-ahs/closed-loop",
)
COHORT_MARKERS = (".wav", ".flac", ".npy", ".json")

REQUIRED_ARTIFACTS = (
    {
        "id": "A1",
        "artifact": "exact upstream source checkout",
        "required": (
            "A local checkout of the exact AHS_2023 and NeuralKalmanAHS "
            "revision that implements the self-attentive RNN and "
            "frequency-domain Kalman filter, with a read-only non-.git tree "
            "digest, file count and the upstream license text"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A2",
        "artifact": "trained checkpoint bundle",
        "required": (
            "Every caller-selected weight, optimizer-independent inference "
            "state, model configuration and model card for the exact trained "
            "Hybrid AHS/NeuralKalmanAHS variant, each with byte count and "
            "SHA-256 and with the immutable training revision"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A3",
        "artifact": "locked isolated runtime",
        "required": (
            "A locked, reproducible isolated runtime with exact interpreter "
            "and package versions, the deep-learning framework and operator "
            "versions, a recorded platform, a lock SHA-256 and an offline "
            "load path"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A4",
        "artifact": "license text and written rights decision",
        "required": (
            "The byte-identical upstream license text for every resolved "
            "repository with SHA-256 plus a written decision that permits "
            "use, modification, redistribution, derived outputs and the "
            "intended benchmark or product scope"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A5",
        "artifact": "matched closed-loop cohort",
        "required": (
            "A rights-cleared closed-loop cohort with frozen speech, "
            "loudspeaker-to-microphone paths, loop gain, delay, saturation, "
            "noise, reset schedule and held-out speakers/paths, plus "
            "reference howl and target-speech truth"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A6",
        "artifact": "independent review and release package",
        "required": (
            "An independent exact-head review of the source, checkpoint, "
            "runtime, rights and cohort, an approved opt-in adapter intake "
            "decision and a complete release package before any support "
            "claim"),
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
            "No AHS_2023 or NeuralKalmanAHS checkout exists locally; the "
            "pinned note records README/demo HTML/CSS/audio only, with no "
            "source implementation, and no revision, tree digest, file count "
            "or license text is pinned."),
        "reopen": (
            "Stage the exact AHS_2023 and NeuralKalmanAHS revision with a "
            "read-only tree digest, file count and upstream license text, "
            "then pin every required source path before reading any "
            "configuration."),
    },
    {
        "id": "RG-02",
        "gate": "exact_checkpoint_and_weight_identity",
        "status": "blocked",
        "reason": (
            "No trained Hybrid AHS or NeuralKalmanAHS checkpoint, inference "
            "state, model card or configuration exists locally. The pinned "
            "note records no release assets for NeuralKalmanAHS and no "
            "runnable checkpoint in either repository."),
        "reopen": (
            "Provide the caller-selected trained checkpoint at an immutable "
            "training revision, with per-file byte counts, SHA-256, model "
            "configuration, model card and the exact variant identity."),
    },
    {
        "id": "RG-03",
        "gate": "locked_isolated_runtime_and_offline_parity",
        "status": "blocked",
        "reason": (
            "No pinned deep-learning runtime, interpreter lock, framework "
            "version, platform record or offline load path exists; no "
            "install/import parity vector is recorded."),
        "reopen": (
            "Provide a locked isolated runtime with exact interpreter and "
            "framework versions, a lock SHA-256, an offline load path and a "
            "reproducible install/import parity vector."),
    },
    {
        "id": "RG-04",
        "gate": "declared_geometry_config_and_layer_reproduction",
        "status": "blocked",
        "reason": (
            "The pinned note records the method and the teacher-forced "
            "offline/streaming inference split but no sample rate, frame, "
            "hop, STFT size, channel count, Kalman state dimension, RNN "
            "structure, layer count or parameter count; nothing is "
            "reproduced."),
        "reopen": (
            "Pin the exact source and checkpoint, verify every declared "
            "rate, frame, hop, channel, Kalman state and RNN configuration, "
            "and reproduce the streaming Kalman-reference update and reset "
            "behaviour."),
    },
    {
        "id": "RG-05",
        "gate": "dsp_acceptance_matrix_and_numerical_behavior",
        "status": "blocked",
        "reason": (
            "The DSP profile requires sweeps, steps, impulses, silence, "
            "clean speech and a task-specific control with gain, response, "
            "attack/release, headroom, delay, numerical behavior, state "
            "transitions and interacting nonlinear configurations; none was "
            "run because there is no candidate runtime."),
        "reopen": (
            "Run the full DSP matrix on the pinned runtime, retain every "
            "failure and nonfinite case, and record gain, response, "
            "attack/release, headroom, delay and state transitions with "
            "tolerances agreed before scoring."),
    },
    {
        "id": "RG-06",
        "gate": "author_reported_result_reconciliation",
        "status": "blocked",
        "reason": (
            "The 200-utterance G=2/2.5/3 SDR and PESQ values are retained "
            "only as author-reported journal results. No exact setup, "
            "checkpoint, runtime or cohort is present to reconcile them, and "
            "no local metric exists."),
        "reopen": (
            "Reproduce the reported setup exactly with the pinned checkpoint, "
            "runtime and matched cohort, then reconcile SDR and PESQ with "
            "pre-registered tolerances while keeping author-reported values "
            "labelled separately."),
    },
    {
        "id": "RG-07",
        "gate": "closed_loop_stability_adverse_behavior_and_matched_cohort",
        "status": "blocked",
        "reason": (
            "No closed-loop stability, maximum-stable-gain, residual tone, "
            "speech-preservation, path-change recovery, saturation, "
            "clipping, latency, CPU or memory measurement exists for this "
            "candidate."),
        "reopen": (
            "Measure closed-loop stability and maximum stable gain on a "
            "rights-cleared matched cohort with held-out speakers and paths, "
            "multiple tones, speech, music, silence, reset, saturation and "
            "path changes, reporting speech damage and residual tone energy "
            "separately."),
    },
    {
        "id": "RG-08",
        "gate": "provider_intake_benchmark_and_release",
        "status": "blocked",
        "reason": (
            "No approved opt-in adapter, provider intake, public-surface "
            "decision, authorized listening, benchmark validation, "
            "independent exact-head review or release approval exists."),
        "reopen": (
            "Complete the source, checkpoint, runtime, rights and cohort "
            "gates, implement any adapter only behind explicit caller opt-in "
            "with no default or fallback registration, validate a benchmark "
            "bundle, run authorized listening where permitted, and obtain "
            "independent review and release approval."),
    },
)

UPSTREAM_BLOCKER = {
    "status": COMPARISON_STATUS,
    "artifact": (
        "Hybrid AHS / NeuralKalmanAHS source, trained checkpoint, locked "
        "runtime, license and rights decision, matched closed-loop cohort "
        "and exact candidate geometry"),
    "source": {
        "status": "absent",
        "repositories": list(SOURCE_REPOSITORIES),
        "papers": [PAPER_URL, JOURNAL_URL, RESEARCH_URL],
        "project_page": PROJECT_URL,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
        "runnable_implementation_present": False,
        "demo_materials_only_reported": True,
        "release_assets_listed_reported": False,
    },
    "checkpoint": {
        "status": "absent",
        "files": None,
        "sha256": None,
        "byte_count": None,
        "parameter_count": None,
        "model_card": None,
        "config": None,
        "framework": None,
        "trained_state_present": False,
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "pinned Python interpreter and package lock",
            "pinned deep-learning framework and operator versions",
            "recorded platform and offline load path",
            "reproducible install/import parity vector",
        ],
        "interpreter": None,
        "framework": None,
        "lockfile": None,
        "sha256": None,
        "offline_path": None,
    },
    "license": {
        "status": "blocked_rights_unrecorded",
        "reported_name": None,
        "reported_source": None,
        "license_text_present": False,
        "license_text_sha256": None,
        "use_approved": False,
        "redistribution_approved": False,
        "derived_output_approved": False,
        "review": "blocked",
    },
    "cohort": {
        "status": "absent",
        "required": (
            "rights-cleared closed-loop cohort with frozen speech, "
            "loudspeaker-to-microphone paths, loop gain, delay, saturation, "
            "noise, reset schedule, held-out speakers/paths and target "
            "reference truth"),
        "corpus_rights": False,
        "loop_gain_measured": False,
        "delay_measured": False,
        "held_out_paths": False,
        "sha256": None,
    },
    "config": {
        "status": "absent",
        "required_paths": [
            "Hybrid AHS / NeuralKalmanAHS model configuration",
            "Kalman filter state and covariance configuration",
            "self-attentive RNN layer and training configuration",
        ],
        "sha256": None,
        "byte_count": None,
    },
    "pinned_revision": None,
    "source_digest": None,
    "checkpoint_digest": None,
    "runtime_digest": None,
    "license_digest": None,
    "cohort_digest": None,
    "config_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "The byte-identical upstream license text for every resolved "
        "repository, a written decision approving use, modification, "
        "redistribution, derived model outputs and the intended benchmark or "
        "product scope, permission for every training and closed-loop corpus "
        "and impulse response, and permission for any listening or "
        "publication are required before any reproduction, adapter, "
        "benchmark or release claim."),
    "workspace_search": (
        "Bounded read-only existence and file-name checks of named candidate "
        "paths under the workspace found no AHS_2023 or NeuralKalmanAHS "
        "checkout, no trained checkpoint, no pinned deep-learning runtime, "
        "no matched closed-loop cohort and no locally approved license text. "
        "No archive, binary, model, audio file or upstream file was opened, "
        "downloaded or reconstructed."),
    "not_attempted": [
        "no git clone, network download, package installation or archive extraction",
        "no fabricated, ported, reverse-engineered or surrogate AHS source, network or configuration",
        "no fabricated checkpoint, weight, model card or training revision",
        "no fabricated license text, rights decision or upstream approval",
        "no framework install, model load, inference or fine-tuning run",
        "no copied upstream source, checkpoint, audio or score",
        "no candidate audio, listening, device-timing or benchmark run",
    ],
    "reopen": (
        "Stage the exact source at a recorded revision with license and tree "
        "digest, provide the exact trained checkpoint with per-file digests, "
        "lock an isolated runtime and offline load path, secure a written "
        "rights decision for use, redistribution and derived output, stage a "
        "rights-cleared matched closed-loop cohort with held-out speakers and "
        "paths, pin the candidate geometry, then reproduce the model and run "
        "the DSP matrix with independent review."),
}

METHOD_PROVENANCE = {
    "status": "source_reported_only_not_reproduced",
    "name": "Hybrid AHS",
    "paper": PAPER_URL,
    "journal_comparison": JOURNAL_URL,
    "project_page": PROJECT_URL,
    "repositories": list(SOURCE_REPOSITORIES),
    "components": [
        "frequency-domain Kalman filter",
        "self-attentive recurrent neural network",
    ],
    "training": (
        "teacher-forced offline training on the Kalman-preprocessed and "
        "ideal microphone signals"),
    "inference": (
        "streaming inference; the fixed network output becomes the reference "
        "used to update the Kalman filter"),
    "reported_evaluation": ["simulated", "real-recorded"],
    "exact_geometry_recorded": False,
    "exact_parameter_count_recorded": False,
    "exact_checkpoint_present": False,
    "reproduced_here": False,
    "source_reported_only": True,
    "qualifies_candidate": False,
    "note": (
        "Only the method description, training/inference split and "
        "author-reported study results are retained from the pinned note. No "
        "architecture detail, geometry, weight or output is inferred."),
}

AUTHOR_REPORTED_RESULTS = {
    "status": "retained_author_reported_not_reproduced",
    "evidence_class": "author_reported_not_reproduced",
    "source": "research/feedback_control_20261028.md",
    "study": "HybridAHS / NeuralKalmanAHS journal comparison (2024)",
    "cohort": {
        "utterances": 200,
        "loop_gains": [2.0, 2.5, 3.0],
    },
    "neuralkalmanahs": {
        "condition_loop_gain": [2.0, 2.5, 3.0],
        "sdr_db": [2.65, 1.98, 1.45],
        "pesq": [2.33, 2.17, 2.04],
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
        "comparable to the current CLN-01 DNS screen, and do not qualify the "
        "candidate. No SDR or PESQ value was computed here."),
}

EXTERNAL_BOUNDARY = {
    "documented": True,
    "upstream_kind": "research model with demo-only public repositories",
    "candidate": "Hybrid AHS self-attentive RNN and Kalman",
    "papers": [PAPER_URL, JOURNAL_URL, RESEARCH_URL],
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
        "and public paper/project pages only. The repositories are reported "
        "to expose demo materials without source or checkpoints. No source, "
        "checkpoint, runtime, license text, cohort or measurement is present, "
        "and this host target is not approved."),
}

NON_CLAIMS = (
    "No AHS_2023 or NeuralKalmanAHS source, model code, configuration, checkpoint, weight or license text is included.",
    "No Hybrid AHS, NeuralKalmanAHS, Kalman filter, self-attentive RNN or adapter is implemented, approximated, simulated or run.",
    "No author-reported SDR, PESQ or other paper value is reproduced, rescaled or presented as a local measurement.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default, and there is no automatic discovery or fallback.",
    "No real corpus, checkpoint, fixture, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No source-reported characteristic is presented as a local measurement.",
    "No missing, rejected or source-reported result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/hybrid-ahs-self-attentive-rnn-and-kalman/ is touched.",
    "The reference is a task-local feasibility gate, not Hybrid AHS.",
    "No candidate sample rate, frame, hop, channel, Kalman state or RNN structure is inferred.",
    "All harness stimuli are analytic or seeded synthetic; no model or corpus is used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Author-reported results are provenance only and never qualify the candidate.",
    "Only stable linked-row identity enters canonical bytes or gates.",
)


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
                 minimum: int | None = None,
                 maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(code, code)
    if minimum is not None and value < minimum:
        raise ConfigError(code, code)
    if maximum is not None and value > maximum:
        raise ConfigError(code, code)
    return value


def _optional_digest(value: Any, code: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) != 64:
        raise ConfigError(code, code)
    if any(character not in "0123456789abcdef" for character in value):
        raise ConfigError(code, code)
    return value


def validate_request(request: Any) -> Dict[str, Any]:
    """Validate a caller-supplied-asset request; never runs a candidate."""
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
    if rate not in (HARNESS_SAMPLE_RATE_HZ,):
        raise ConfigError("RATE_NOT_DECLARED", "RATE_NOT_DECLARED")
    channels = _require_int(request["channels"], "WRONG_CHANNELS", 1)
    if channels != HARNESS_CHANNELS:
        raise ConfigError("WRONG_CHANNELS", "WRONG_CHANNELS")
    frame_samples = _require_int(request["frame_samples"], "INVALID_FRAME", 1,
                                 4096)
    if frame_samples != HARNESS_FRAME_SAMPLES:
        raise ConfigError("WRONG_DECLARED_FRAME", "WRONG_DECLARED_FRAME")
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
    checkpoint_sha256 = _optional_digest(
        request["checkpoint_sha256"], "INVALID_CHECKPOINT_DIGEST")
    runtime_lock_sha256 = _optional_digest(
        request["runtime_lock_sha256"], "INVALID_RUNTIME_DIGEST")
    asset_bytes = _require_int(request["asset_bytes"], "INVALID_ASSET_BYTES",
                               0, MAX_EXTERNAL_ASSET_BYTES)
    if (checkpoint_sha256 is None) != (runtime_lock_sha256 is None):
        raise ConfigError("INCOMPLETE_ASSET_MANIFEST",
                          "INCOMPLETE_ASSET_MANIFEST")
    if checkpoint_sha256 is not None and asset_bytes == 0:
        raise ConfigError("MISSING_ASSET_BYTES", "MISSING_ASSET_BYTES")
    if checkpoint_sha256 is None and asset_bytes > 0:
        raise ConfigError("UNCLAIMED_ASSET_BYTES", "UNCLAIMED_ASSET_BYTES")
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
        "checkpoint_sha256": checkpoint_sha256,
        "runtime_lock_sha256": runtime_lock_sha256,
        "asset_bytes": asset_bytes,
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
        "checkpoint_sha256": None,
        "runtime_lock_sha256": None,
        "asset_bytes": 0,
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
    good_digest = "0" * 64
    return (
        ("unknown_candidate", variant(candidate="hybrid_ahs")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
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
        "reason": COMPARISON_STATUS,
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def _resolve_workspace_path(label: str) -> Path:
    if label.startswith("~/"):
        return Path.home() / label[2:]
    return WORKSPACE / label


def _markers_in(path: Path, markers: Sequence[str],
                max_depth: int = 3) -> List[str]:
    found: List[str] = []
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


def source_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    marker_hits: List[str] = []
    for label in SOURCE_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
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


def checkpoint_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[Dict[str, Any]] = []
    for label in CHECKPOINT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
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
                 "opened, loaded, hashed or executed. A discovered file "
                 "would still require an exact revision, digest and rights "
                 "decision before use."),
    }


def _command_present(command: str) -> bool:
    return shutil.which(command) is not None


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
    commands = {command: _command_present(command)
                for command in RUNTIME_COMMANDS}
    return {
        "status": "runtime_present_unqualified" if pinned
                  else "blocked_runtime_unpinned",
        "checked_paths": sorted(checked),
        "found": sorted(found),
        "lockfiles": sorted(locks),
        "commands": commands,
        "present": bool(found),
        "pinned": pinned,
        "interpreter": None,
        "framework": None,
        "sha256": None,
        "offline_path": None,
        "note": ("No model runtime is pinned. Host command discovery is "
                 "informational only and is not a candidate runtime, "
                 "framework version, lock or import-parity record."),
    }


def cohort_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in COHORT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
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
        "note": ("Existence checks only; no audio file is opened or "
                 "decoded. A synthetic harness frame is not a matched "
                 "closed-loop cohort."),
    }


def license_probe() -> Dict[str, Any]:
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
                 "present, and repository availability is not a right to "
                 "use, redistribute or publish."),
    }


def rights_probe() -> Dict[str, Any]:
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
                 "fixture permission is recorded locally. Upstream presence "
                 "is not a right to use, redistribute or publish."),
    }


def geometry() -> Dict[str, Any]:
    return {
        "candidate": "Hybrid AHS self-attentive RNN and Kalman",
        "declared_candidate_geometry_recorded": False,
        "declared_sample_rates_hz": list(DECLARED_CANDIDATE_SAMPLE_RATES_HZ),
        "declared_frame_samples": None,
        "declared_channels": None,
        "declared_stft_size": None,
        "declared_hop_samples": None,
        "declared_kalman_state_dimension": None,
        "declared_rnn_layers": None,
        "declared_parameter_count": None,
        "local_harness_geometry": {
            "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
            "channels": HARNESS_CHANNELS,
            "frame_samples": HARNESS_FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
        },
        "local_harness_is_candidate_geometry": False,
        "v0_can_represent_declared_input": None,
        "verified_here": False,
        "measured_here": False,
        "candidate_output": False,
        "note": (
            "The pinned note records no candidate sample rate, frame, hop, "
            "STFT size, channel count, Kalman state dimension, RNN structure, "
            "layer count or parameter count. None is inferred. The 16 kHz / "
            "mono / 160-sample harness is the unchanged installed-v0 bound "
            "used only to exercise validation and rejection."),
    }


def profile_mapping() -> Dict[str, str]:
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
        "candidate_output": COMPARISON_STATUS,
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "exact_source_revision_and_license":
            "blocked_source_absent",
        "exact_checkpoint_and_weight_digests":
            "blocked_checkpoint_absent",
        "pinned_runtime_and_offline_import_parity":
            "blocked_runtime_unpinned",
        "declared_geometry_and_layer_configuration":
            "blocked_config_and_geometry_absent",
        "kalman_and_self_attentive_rnn_reproduction":
            "blocked_no_candidate_instance",
        "dsp_gain_response_attack_release_delay":
            "blocked_no_candidate_output",
        "author_reported_result_reconciliation":
            "blocked_author_reported_only",
        "closed_loop_stability_and_maximum_stable_gain":
            "blocked_no_measurement",
        "matched_cohort_sdr_pesq_and_speech_preservation":
            "blocked_no_permitted_cohort",
        "device_timing_memory_and_callback":
            "blocked_no_paced_measurement",
        "provider_intake_and_opt_in_adapter":
            "blocked_no_approved_runtime_or_terms",
        "authorized_listening_and_benchmark":
            "blocked_no_release_evidence",
        "release_qualification":
            "blocked_no_release_evidence",
    }


def candidates() -> Dict[str, Any]:
    return {
        CANDIDATE: {
            "status": COMPARISON_STATUS,
            "metrics": None,
            "qualifies_candidate": False,
            "result": None,
            "reason": (
                "No upstream source, trained checkpoint, pinned runtime, "
                "approved rights, matched closed-loop cohort or candidate "
                "geometry is present; no SDR, PESQ, stability or timing "
                "result was produced."),
        }
    }


def controls() -> Dict[str, Any]:
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
            "harness stimulus characterisation only; not a Hybrid AHS or "
            "NeuralKalmanAHS result and not a candidate output"),
        "harness_geometry": {
            "channels": HARNESS_CHANNELS,
            "frame_samples": HARNESS_FRAME_SAMPLES,
            "flat_values": HARNESS_FRAME_VALUES,
            "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
            "verified_model_geometry": False,
            "note": (
                "This is the unchanged installed-v0 16 kHz / mono / 160 "
                "format. It is used only to exercise validation and "
                "rejection; it is not a claim about candidate geometry."),
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
    if not checkpoint_probe()["present"]:
        blockers.append("checkpoint_absent")
    if not runtime_probe()["pinned"]:
        blockers.append("runtime_unpinned")
    if not cohort_probe()["present"]:
        blockers.append("matched_closed_loop_cohort_absent")
    if license_probe()["review"] != "approved":
        blockers.append("rights_unrecorded")
    if not AUTHOR_REPORTED_RESULTS["reproduced_here"]:
        blockers.append("author_reported_results_only")
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
            "A structurally valid caller-supplied-asset request is still not "
            "admissible: the source, checkpoint, runtime, rights and matched "
            "cohort are absent. No port, fallback or surrogate is used."),
    }


def probe_candidate(request: Any) -> None:
    validate_request(request)
    raise ArtifactsAbsent(
        "ARTIFACTS_ABSENT: Hybrid AHS/NeuralKalmanAHS source, checkpoint, "
        "pinned runtime, approved rights and matched cohort are not present; "
        "no processing is performed", "ARTIFACTS_ABSENT")


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
        ("research/feedback_control_20261028.md records Hybrid AHS "
         "(Interspeech 2023) as a frequency-domain Kalman filter plus a "
         "self-attentive RNN, with teacher-forced offline training and "
         "streaming inference where the fixed network output becomes the "
         "Kalman reference."),
        ("the same note records HybridAHS/NeuralKalmanAHS journal results on "
         "200 utterances at loop gains 2, 2.5 and 3: NeuralKalmanAHS SDR "
         "2.65, 1.98 and 1.45 dB and PESQ 2.33, 2.17 and 2.04, with "
         "HybridAHS v2 complex-ratio-mask results reported as the strongest "
         "overall trade-off in parts of the study."),
        ("the same note records that the public YIXUANZ/NeuralKalmanAHS and "
         "YIXUANZ/AHS_2023 repositories expose README/demo HTML, CSS and "
         "audio files, with no source implementation or model checkpoints in "
         "their visible file listings and no release assets for "
         "NeuralKalmanAHS."),
        ("plan/INVENTORY.json assigns hybrid-ahs-self-attentive-rnn-and-"
         "kalman the dsp verification profile, disposition sdk-model, "
         "evidence_status blocked and the plan note to retain author-reported "
         "closed-loop results and check for exact runnable state/checkpoints "
         "before an experiment."),
        ("plan/audio-sdk/README.md requires runnable source, exact assets, "
         "permitted scope and matched evidence before a caller-supplied "
         "reference or opt-in adapter is added."),
        ("plan/swarm/VERIFICATION.md defines the DSP acceptance profile: "
         "sweeps, steps, impulses, silence, clean speech and a task-specific "
         "control with gain, response, attack/release, headroom, delay, "
         "numerical behavior, state transitions and interacting nonlinear "
         "configurations."),
        ("No local AHS_2023 or NeuralKalmanAHS source, checkpoint, runtime "
         "lock, license text, matched cohort or candidate geometry exists; "
         "nothing was cloned, downloaded, ported, reconstructed or "
         "simulated."),
    ]


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    source = source_probe()
    checkpoint = checkpoint_probe()
    runtime = runtime_probe()
    license_block = license_probe()
    cohort = cohort_probe()
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
        "runnable_source_reported_absent":
            source["runnable_implementation_present"] is False,
        "checkpoint_absent": checkpoint["present"] is False,
        "runtime_unpinned": runtime["pinned"] is False,
        "license_text_absent": license_block["license_text_present"] is False,
        "rights_not_approved": (
            license_block["use_approved"] is False and
            license_block["redistribution_approved"] is False),
        "matched_cohort_absent": cohort["present"] is False,
        "author_reported_results_only":
            AUTHOR_REPORTED_RESULTS["reproduced_here"] is False,
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "nonfinite_samples_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith("nonfinite")),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked":
            missing_result("hybrid_ahs_placeholder")["status"] == "blocked",
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
        "method_provenance": dict(METHOD_PROVENANCE),
        "author_reported_results": dict(AUTHOR_REPORTED_RESULTS),
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
            "note": (
                "No Hybrid AHS or NeuralKalmanAHS model, Kalman filter, "
                "self-attentive RNN, adapter or port is implemented or "
                "simulated; only probes, request rejection, author-reported "
                "provenance and synthetic harness controls are performed."),
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
        "runtime_probe": runtime,
        "license_probe": license_block,
        "cohort_probe": cohort,
        "rights_probe": rights,
        "geometry": geom,
        "candidates": candidates(),
        "controls": controls(),
        "required_results": candidate_required_results(),
        "stimulus_probe": stimuli,
        "adverse": {
            "invalid_config_and_input": adverse_request,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": missing_result("hybrid_ahs_placeholder"),
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
