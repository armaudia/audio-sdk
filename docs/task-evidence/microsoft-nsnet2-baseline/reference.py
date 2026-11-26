# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for SDK-MICROSOFT-NSNET2-BASELINE.

This module is NOT Microsoft NSNet2 and NOT the DNS-Challenge code base. It
contains no vendor source, official model weights, graph, conversion recipe,
license text, runtime, cohort or candidate output. A bounded read-only search
finds no official DNS-Challenge checkout that still ships NSNet2, no official
48 kHz ONNX artifact, no artifact-specific model terms, no pinned ONNX Runtime
and no rights-cleared matched cohort in the workspace.

The pinned research census records only that the ICASSP 2022 DNS baseline is a
frequency-mask DNN, 48 kHz and 20 ms, that the official 48 kHz ONNX model was
linked from the paper, that the code/model were removed from the current
DNS-Challenge branch in commit ``d1bcd6927beed89774e50404d4da2fa46b0d8f47``
after being added in ``ff23e198ba7ee97893ad0e73ee7e8cfeef9b7a79``, and that the
current repository notice separates MIT code from CC BY 4.0 documentation
without stating model-artifact terms. No digest or checkpoint-specific terms
were confirmed, and surviving copies are forks or mirrors.

A third-party ``eco8-neaixt`` checkout that reimplements an NSNet2 architecture
is present under ``data/checkouts``. It is a 16 kHz VoiceBank-DEMAND training
recipe with no staged weights, is not the official 48 kHz DNS baseline, and is
explicitly rejected as a substitute. Nothing was cloned, downloaded, ported,
converted, reverse-engineered or simulated.

The module therefore builds a fail-closed model-feasibility blocker report:

* strict request validation at the single source-reported 48 kHz rate using the
  arithmetic 960-sample 20 ms frame; the hop is unrecorded and is not invented;
* explicit official source, official weights, license/terms, runtime, runner,
  configuration, cohort, scorer, rights and third-party-substitute probes;
* an admission gate that rejects every structurally valid request because the
  required official artifacts and rights are absent;
* synthetic harness stimuli and an identity control for rejection and harness
  characterisation only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

No candidate audio output is produced. No result qualifies the candidate and no
source-reported quality or performance value is reproduced.
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

SCHEMA_ID = "audio-sdk/microsoft-nsnet2-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/microsoft-nsnet2-contract/0.1"
TASK = "SDK-MICROSOFT-NSNET2-BASELINE"
COMPONENT = "microsoft-nsnet2-baseline"
BRANCH = "swarm/SDK-MICROSOFT-NSNET2-BASELINE"
BASE_COMMIT = "0cc1e79e592d7fc25f054fcd98824053be281f5e"
TASK_PREFIX = "docs/task-evidence/microsoft-nsnet2-baseline/"
MODE = "feasibility"
VERIFICATION_PROFILE = "Enhancement"

# Installed v0 format. This is the unchanged public baseline, not the DNS
# baseline geometry and not a model configuration.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
ABI_MAJOR = 0
ABI_MINOR = 1

# Only the 48 kHz rate and the 20 ms frame duration are recorded by the pinned
# census. 960 samples is arithmetic at 48 kHz. The hop is not recorded and is
# deliberately absent instead of being guessed.
DECLARED_SAMPLE_RATES_HZ = (48000,)
DECLARED_FRAME_MS = 20
DECLARED_FRAME_SAMPLES = 960
GEOMETRY_DERIVATION = (
    "20 ms x 48000 Hz = 960 samples; derived arithmetically from the "
    "source-reported 20 ms duration only. The hop is not recorded and no "
    "sample hop is claimed")
VENDOR = "Microsoft"
COMPONENT_NAME = "Microsoft NSNet2 baseline"
DOC_URL = (
    "https://www.microsoft.com/en-us/research/wp-content/uploads/2022/07/"
    "0009271.pdf")
SOURCE_REPOSITORY = "https://github.com/microsoft/DNS-Challenge"
MODEL_ARTIFACT = "Microsoft NSNet2 official 48 kHz ONNX model artifact"
SDK_DISPOSITION = "sdk-model"
REMOVAL_COMMIT = "d1bcd6927beed89774e50404d4da2fa46b0d8f47"
ADDITION_COMMIT = "ff23e198ba7ee97893ad0e73ee7e8cfeef9b7a79"
GENERAL_CODE_LICENSE = "MIT (repository general legal notice, source-reported)"
GENERAL_DOC_LICENSE = (
    "CC BY 4.0 (repository general legal notice, source-reported)")
THIRD_PARTY_PATH = "data/checkouts/eco8-neaixt"
THIRD_PARTY_PROBE_PATHS = (THIRD_PARTY_PATH,)

# Local harness geometry. The frame is the arithmetic value above and is used
# only to exercise validation and rejection. The hop is intentionally absent.
HARNESS_SAMPLE_RATE_HZ = 48000
HARNESS_CHANNELS = 1
HARNESS_FRAME_SAMPLES = DECLARED_FRAME_SAMPLES
HARNESS_HOP_SAMPLES = None
HARNESS_FRAME_VALUES = HARNESS_CHANNELS * HARNESS_FRAME_SAMPLES
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0
MAX_CHANNELS_GUARD = 64

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only the stable linked-row identity is projected, never hashed.
SOURCE_PINS = {
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
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
    "title": "Microsoft NSNet2 baseline",
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

CANDIDATE = "microsoft_nsnet2"
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
    "third_party/DNS-Challenge",
    "third_party/DNS-Challenge-master",
    "components/DNS-Challenge",
    "vendor/microsoft/DNS-Challenge",
    "research/microsoft-nsnet2",
    "research/nsnet2",
    "research/repos/DNS-Challenge",
    "data/checkouts/DNS-Challenge",
    "data/models/microsoft-nsnet2",
    "~/DNS-Challenge",
    "~/code/DNS-Challenge",
    "~/projects/DNS-Challenge",
)
SOURCE_MARKERS = (
    "nsnet2", "nsnet2_model.py", "inference.py", "DNS-Challenge",
)
MODEL_MARKERS = (
    ".onnx", ".pt", ".pth", ".ckpt", ".safetensors", ".bin", ".tflite",
    ".gguf", ".params",
)

TOOLCHAIN_COMMANDS = ("python3", "onnxruntime")
RUNTIME_CANDIDATE_PATHS = (
    "data/envs/microsoft-nsnet2",
    "data/runtime/onnxruntime",
    "research/microsoft-nsnet2/runtime",
)
RUNTIME_LOCK_CANDIDATES = (
    "research/microsoft-nsnet2/runtime.lock",
    "data/envs/microsoft-nsnet2/requirements.lock",
)

COHORT_CANDIDATE_PATHS = (
    "data/corpora/microsoft-nsnet2",
    "data/fixtures/microsoft-nsnet2",
    "research/microsoft-nsnet2/cohort",
    "research/microsoft-nsnet2/paired",
)
COHORT_MARKERS = (".wav", ".flac", ".npy", ".json")

SCORER_CANDIDATE_PATHS = (
    "research/microsoft-nsnet2/scorer",
    "data/scorers/microsoft-nsnet2",
)

REQUIRED_ARTIFACTS = (
    {
        "id": "A1",
        "artifact": (
            "official DNS-Challenge checkout at the recorded NSNet2 revision"),
        "required": (
            "A local checkout at the recorded addition commit (or an "
            "authoritatively republished revision) with a read-only non-.git "
            "tree digest, the NSNet2 source files and the repository license "
            "file"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A2",
        "artifact": "official Microsoft NSNet2 48 kHz ONNX artifact",
        "required": (
            "The exact official 48 kHz ONNX model bytes with path, byte count "
            "and SHA-256, plus the conversion/export recipe, operator set, "
            "precision and quantization description"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A3",
        "artifact": "code, model and training-data terms with rights decision",
        "required": (
            "Byte-identical license and model terms with SHA-256 plus a "
            "written decision approving or rejecting use, redistribution and "
            "derived-output publication for this host target"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A4",
        "artifact": "pinned ONNX Runtime and reproducible host runner",
        "required": (
            "A hash-pinned ONNX Runtime build, Python or native runner, package "
            "lock, reproducible artifact and install/import parity record"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A5",
        "artifact": "pinned geometry, features and configuration",
        "required": (
            "The exact configuration declaring sample rate, frame, hop, "
            "channel handling, STFT window and features, mask output mapping, "
            "buffering delay, reset/drain and quantization"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A6",
        "artifact": "rights-cleared matched cohort and approved scorer",
        "required": (
            "A rights-cleared paired noisy/clean 48 kHz speech cohort with "
            "consent and metadata, an approved SI-SDR/STOI implementation, "
            "and authorized listening or a separately labeled predictive "
            "screen"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A7",
        "artifact": "state, memory and paced host-timing harness",
        "required": (
            "A measured harness for state transitions, reset/drain, memory, "
            "callback behavior, content delay and paced availability on the "
            "pinned runner"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A8",
        "artifact": "independent review and release package",
        "required": (
            "An independent exact-head review, an approved opt-in adapter "
            "intake decision and a complete release package before any "
            "support, quality or benchmark claim"),
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
        "gate": "exact_official_dns_challenge_source_revision_and_tree_pin",
        "status": "blocked",
        "reason": (
            "No official DNS-Challenge checkout exists locally. The recorded "
            "addition commit is known only from the census, the code was "
            "removed upstream, and no revision, tree digest, NSNet2 source "
            "file set or license file is pinned."),
        "reopen": (
            "Stage the exact official DNS-Challenge revision that contains "
            "NSNet2 at a recorded full commit with a read-only tree digest and "
            "its license file, then pin every required NSNet2 source path "
            "before reading any configuration."),
    },
    {
        "id": "RG-02",
        "gate": "exact_official_model_artifact_and_conversion_identity",
        "status": "blocked",
        "reason": (
            "No official NSNet2 48 kHz ONNX bytes, path, byte count, SHA-256, "
            "conversion recipe, operator set, precision or quantization "
            "description exists locally. The official download path is gone "
            "and surviving copies are forks or mirrors."),
        "reopen": (
            "Provide the official 48 kHz ONNX artifact by path, byte count and "
            "SHA-256 with its export recipe and precision or quantization "
            "parameters, or a verifiable Microsoft republication. Do not "
            "substitute a fork, mirror or unrelated NSNet2 reimplementation."),
    },
    {
        "id": "RG-03",
        "gate": "code_model_and_training_data_terms_with_rights_decision",
        "status": "blocked",
        "reason": (
            "The pinned census records a general MIT code notice and a CC BY "
            "4.0 documentation notice, but no artifact-specific model terms, "
            "training-data terms, local license text or written rights "
            "decision for this host target or for derived output."),
        "reopen": (
            "Obtain the byte-identical code and official model terms with "
            "SHA-256 and secure a written rights decision that explicitly "
            "permits this use, adapter distribution and output publication, "
            "or record a final rejection and close the task."),
    },
    {
        "id": "RG-04",
        "gate": "pinned_onnx_runtime_and_reproducible_runner",
        "status": "blocked",
        "reason": (
            "No hash-pinned ONNX Runtime build, package lock, reproducible "
            "runner artifact or install/import parity record exists locally."),
        "reopen": (
            "Provide a licensed, hash-pinned ONNX Runtime and runner with a "
            "package lock, build a reproducible artifact, and prove "
            "install/import parity before any measurement."),
    },
    {
        "id": "RG-05",
        "gate": "pinned_geometry_features_and_configuration",
        "status": "blocked",
        "reason": (
            "Only the 48 kHz rate and 20 ms frame duration are source-"
            "reported. The 960-sample count is arithmetic, and the hop, "
            "channel handling, STFT window and features, output mapping, "
            "buffering delay, reset/drain and quantization are unpinned."),
        "reopen": (
            "Pin the exact configuration and verify the frame, hop, channel "
            "handling, STFT/features, output mapping, delay, finite drain and "
            "reset semantics; never infer an unpinned value from the reported "
            "duration."),
    },
    {
        "id": "RG-06",
        "gate": "caller_supplied_reference_and_state_parity",
        "status": "blocked",
        "reason": (
            "No caller-supplied official asset path or instance exists, so no "
            "reset, drain, state transition, chunk-boundary or output-mapping "
            "parity was reproduced."),
        "reopen": (
            "With pinned official source, model, runtime and configuration, "
            "reproduce the exact model as a caller-supplied-asset reference, "
            "including reset, finite drain, independent state, chunk "
            "boundaries and exact output mapping."),
    },
    {
        "id": "RG-07",
        "gate": "enhancement_acceptance_matrix_and_matched_evidence",
        "status": "blocked",
        "reason": (
            "The Enhancement profile requires identity/noisy control, an "
            "established task-matched baseline, paired SI-SDR and STOI where "
            "permitted clean references exist, clean-speech preservation, "
            "peaks, invalid outputs, alignment, state, memory and measured "
            "timing; none was run because no permitted candidate or cohort "
            "exists."),
        "reopen": (
            "Run the full Enhancement matrix on a rights-cleared 48 kHz "
            "matched cohort with an approved scorer, retain every failure, "
            "nonfinite and adverse case, and report paired quality, "
            "preservation, alignment, state, memory and paced timing with "
            "tolerances agreed before scoring."),
    },
    {
        "id": "RG-08",
        "gate": "opt_in_adapter_intake_benchmark_and_release_review",
        "status": "blocked",
        "reason": (
            "No approved adapter, provider intake, opt-in registration, "
            "public-surface decision, authorized listening, benchmark "
            "validation, independent exact-head review or release approval "
            "exists."),
        "reopen": (
            "Complete the rights, runtime and evidence gates, implement any "
            "adapter only behind explicit caller opt-in with no default or "
            "fallback registration, validate a benchmark bundle, run "
            "authorized listening where permitted, and obtain independent "
            "review and release approval."),
    },
)

UPSTREAM_BLOCKER = {
    "status": (
        "blocked_official_artifact_terms_runtime_and_matched_cohort_absent"),
    "artifact": (
        "official DNS-Challenge NSNet2 source, official 48 kHz ONNX artifact, "
        "terms decision, pinned runtime, geometry and rights-cleared matched "
        "cohort"),
    "source": {
        "status": "absent",
        "repository": SOURCE_REPOSITORY,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
        "documented_addition_commit": ADDITION_COMMIT,
        "documented_removal_commit": REMOVAL_COMMIT,
        "official_download_path_available": False,
    },
    "weights": {
        "status": "absent",
        "artifact": MODEL_ARTIFACT,
        "path": None,
        "sha256": None,
        "byte_count": None,
        "conversion_recipe": None,
        "precision": None,
        "quantization": None,
        "operator_set": None,
    },
    "license": {
        "status": "blocked_model_terms_not_recorded",
        "reported_name": None,
        "reported_code_license": GENERAL_CODE_LICENSE,
        "reported_documentation_license": GENERAL_DOC_LICENSE,
        "general_repository_notice_recorded": True,
        "artifact_specific_model_terms_recorded": False,
        "reported_terms_recorded_in_pinned_evidence": False,
        "license_text_present": False,
        "license_text_sha256": None,
        "model_terms_present": False,
        "training_data_terms_present": False,
        "use_approved": False,
        "redistribution_approved": False,
        "derived_output_publication_approved": False,
        "host_target_approved": False,
        "review": "blocked",
    },
    "hardware": {
        "status": "absent",
        "eligible_target": "pinned CPU ONNX Runtime execution host",
        "runner": None,
        "hardware_attached": None,
        "firmware_sha256": None,
        "vendor_resource_figures_generalizable": False,
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "a hash-pinned ONNX Runtime version and operator set",
            "a recorded Python or native runner and package lock",
            "a reproducible runner artifact with a recorded SHA-256",
            "an explicit runner identity and install/import parity check",
            "an approved host target and execution profile",
        ],
        "onnxruntime_version": None,
        "python_version": None,
        "lockfile": None,
        "portable_host_runtime": None,
        "sha256": None,
    },
    "config": {
        "status": "absent",
        "required_paths": [
            "DNS-Challenge NSNet2 inference entry point",
            "NSNet2 48 kHz STFT, feature and mask-reconstruction configuration",
        ],
        "sha256": None,
        "byte_count": None,
    },
    "cohort": {
        "status": "absent",
        "required": (
            "rights-cleared paired noisy/clean 48 kHz speech with consent, "
            "speaker/language metadata, noise conditions and matched "
            "quiet/active and onset/offset cases"),
        "corpus_rights": False,
        "clean_references_present": False,
        "sha256": None,
    },
    "scorer": {
        "status": "unapproved",
        "approved_si_sdr": False,
        "approved_stoi": False,
        "authorized_listening": False,
        "predictive_screen_labeled": False,
        "sha256": None,
    },
    "third_party": {
        "path": THIRD_PARTY_PATH,
        "accepted_as_official_artifact": False,
        "accepted_as_substitute": False,
        "weights_present_locally": False,
        "note": (
            "A third-party NSNet2 reimplementation checkout was observed. It "
            "is a 16 kHz VoiceBank-DEMAND training recipe without staged "
            "weights, is not the official 48 kHz DNS baseline, and is not "
            "used for any result."),
    },
    "pinned_revision": None,
    "source_digest": None,
    "weights_digest": None,
    "license_digest": None,
    "hardware_digest": None,
    "runtime_digest": None,
    "config_digest": None,
    "cohort_digest": None,
    "scorer_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "The exact official DNS-Challenge code license text and NSNet2 model "
        "terms with SHA-256, permission for code use, official model use, "
        "redistribution, host runtime scope and derived-output publication, "
        "approval for every cohort recording and consent, and an approved "
        "scorer are required before any reproduction, adapter, benchmark or "
        "release claim."),
    "workspace_search": (
        "Bounded read-only existence and file-name checks of named candidate "
        "paths under the workspace found no official DNS-Challenge checkout, "
        "no official NSNet2 48 kHz ONNX artifact, no pinned ONNX Runtime or "
        "lock, no rights-cleared matched cohort and no approved scorer. A "
        "third-party eco8-neaixt NSNet2 reimplementation checkout is present "
        "but was rejected as a substitute. No archive, binary, model, audio "
        "file or vendor file was opened, downloaded or reconstructed."),
    "not_attempted": [
        "no git clone, network download, package installation or archive extraction",
        "no fabricated, ported, reverse-engineered or surrogate official NSNet2 source, header or configuration",
        "no fabricated official model weights, ONNX graph, conversion recipe or checksum",
        "no fabricated license text, model terms decision or rights approval",
        "no ONNX Runtime inference, build, benchmark or host execution",
        "no substitution of a fork, mirror or third-party NSNet2 reimplementation",
        "no copied vendor source, official model, audio or score",
        "no candidate audio, listening, device-timing or benchmark run",
    ],
    "reopen": (
        "Stage the official DNS-Challenge source and NSNet2 48 kHz ONNX "
        "artifact at recorded digests, secure a written code/model/"
        "redistribution/output decision, provide a hash-pinned ONNX Runtime "
        "and runner, pin the geometry and configuration, stage a "
        "rights-cleared 48 kHz matched cohort with an approved scorer, then "
        "reproduce the model and run the Enhancement matrix with independent "
        "review."),
}

NON_CLAIMS = (
    "No official DNS-Challenge source, NSNet2 ONNX graph, header, configuration or license text is included.",
    "No NSNet2 inference, port, surrogate, approximation or simulation is implemented or run.",
    "No model parameter count, frame, hop or platform characteristic is presented as a local measurement.",
    "No SI-SDR, STOI, DNSMOS, PESQ or listening score is produced, reproduced or implied.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default, and there is no automatic discovery or fallback.",
    "No real corpus, clean reference, listening panel, benchmark or quality claim exists.",
    "No host timing, callback, CPU, memory or release claim is made.",
    "No third-party NSNet2 reimplementation is substituted for the official baseline.",
    "No source-reported vendor or census characteristic is presented as a local measurement.",
    "No missing, rejected or source-reported result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/microsoft-nsnet2-baseline/ is touched.",
    "The reference is a task-local feasibility gate, not Microsoft NSNet2.",
    "The declared 48 kHz model geometry is not representable by installed v0 without an adapter.",
    "The 960-sample frame is arithmetic from the reported 20 ms at 48 kHz, not a pinned API constant; the hop is unrecorded.",
    "The third-party eco8-neaixt NSNet2 checkout is not an official artifact and is never substituted.",
    "All harness stimuli are analytic or seeded synthetic; no vendor runtime is used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
)

MODEL_BOUNDARY = {
    "documented": True,
    "vendor": VENDOR,
    "component": COMPONENT_NAME,
    "component_version": "NSNet2 (official artifact unpinned)",
    "sdk_disposition": SDK_DISPOSITION,
    "documentation": DOC_URL,
    "repository": SOURCE_REPOSITORY,
    "distribution_model": "official 48 kHz ONNX DNS Challenge baseline",
    "declared_target": "pinned CPU ONNX Runtime execution host",
    "host_target": "macOS / Python 3 workspace",
    "host_target_eligible": False,
    "portable_adapter_present": False,
    "reported_parameter_count": None,
    "reported_parameter_count_is_local_measurement": False,
    "license_reported": None,
    "general_repository_notice_recorded": True,
    "code_license_reported": GENERAL_CODE_LICENSE,
    "documentation_license_reported": GENERAL_DOC_LICENSE,
    "artifact_specific_model_terms_recorded": False,
    "license_terms_recorded_in_pinned_evidence": False,
    "license_text_present": False,
    "model_terms_present": False,
    "use_approved": False,
    "redistribution_approved": False,
    "local_runtime_present": False,
    "weights_present": False,
    "official_download_path_available": False,
    "third_party_reimplementation_present": True,
    "third_party_accepted_as_official": False,
    "vendor_output_present": False,
    "adapter_implemented": False,
    "adapter_default_registration": False,
    "automatic_discovery": False,
    "fallback": "none",
    "vendor_claims_separate_from_local_measurements": True,
    "note": (
        "The model boundary is documented from the pinned research census and "
        "the official paper locator only. The official code and weights were "
        "removed upstream and are not present. A third-party reimplementation "
        "is present but is not official and is rejected as a substitute. No "
        "source, official model, artifact-specific terms, runtime, cohort or "
        "measurement is present, and this host target is not approved."),
}

ENHANCEMENT_CONTROL = {
    "status": "not_evaluated_by_this_task",
    "installed_v0_frame_samples": FRAME_SAMPLES,
    "identity_noisy_control": None,
    "established_task_matched_baseline": None,
    "paired_si_sdr_db": None,
    "paired_stoi": None,
    "clean_speech_preservation": None,
    "peak_and_invalid_outputs": None,
    "alignment_and_content_delay": None,
    "state_and_reset": None,
    "memory": None,
    "measured_availability_timing": None,
    "metrics": None,
    "result": None,
    "qualifies_candidate": False,
    "quality_claim": False,
    "intelligibility_claim": False,
    "listening_claim": False,
    "timing_claim": False,
    "note": (
        "No denoising, preservation, alignment, state, memory or timing result "
        "exists. The Enhancement profile is recorded as unexecuted and no "
        "source-reported value is promoted into a metric."),
}

SCORER_PROBE_BLOCK = {
    "status": "unapproved_no_scorer_implemented",
    "si_sdr": None,
    "stoi": None,
    "dnsmos": None,
    "pesq": None,
    "listening_panel": None,
    "approved_scorer_sha256": None,
    "calibrated_here": False,
    "note": (
        "No approved SI-SDR, STOI, DNSMOS or listening protocol exists in this "
        "package; no scorer is implemented, calibrated or applied."),
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
          end_hz: float = 6000.0, amplitude: float = 0.3) -> Tuple[float, ...]:
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


def noise_like(length: int = HARNESS_FRAME_VALUES,
               seed: int = 20261127) -> Tuple[float, ...]:
    noise = _lcg(seed)
    return tuple(0.2 * next(noise) for _ in range(length))


STIMULUS_GENERATORS = {
    "silence": lambda: silence(),
    "impulse": lambda: impulse(),
    "step": lambda: step(),
    "sweep": lambda: sweep(),
    "speech_like": lambda: speech_like(),
    "noise_like": lambda: noise_like(),
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


def identity_transfer(samples: Sequence[float]) -> Tuple[float, ...]:
    """Harness identity control only; never a candidate or a metric."""
    return tuple(float(value) for value in samples)


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
    """Validate a declared-geometry request; never runs a candidate."""
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
    if request["candidate"] != CANDIDATE:
        raise ConfigError("UNKNOWN_CANDIDATE", "UNKNOWN_CANDIDATE")
    rate = _require_int(request["sample_rate_hz"], "INVALID_RATE", 1)
    if rate not in DECLARED_SAMPLE_RATES_HZ:
        raise ConfigError("RATE_NOT_RECORDED", "RATE_NOT_RECORDED")
    channels = _require_int(request["channels"], "WRONG_CHANNELS", 1)
    if channels > MAX_CHANNELS_GUARD:
        raise ConfigError("CHANNELS_OVER_LOCAL_GUARD",
                          "CHANNELS_OVER_LOCAL_GUARD")
    if channels != HARNESS_CHANNELS:
        raise ConfigError("LOCAL_HARNESS_CHANNELS_ONLY",
                          "LOCAL_HARNESS_CHANNELS_ONLY")
    frame_samples = _require_int(request["frame_samples"], "INVALID_FRAME", 1)
    if frame_samples > 4096:
        raise ConfigError("FRAME_TOO_LARGE", "INVALID_FRAME")
    if frame_samples != DECLARED_FRAME_SAMPLES:
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
        ("unknown_candidate", variant(candidate="microsoft_nsnet3")),
        ("unknown_field", variant(extra=True)),
        ("unexpected_hop_field", variant(hop_samples=480)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("missing_frame", {key: value for key, value in base.items()
                           if key != "frame_samples"}),
        ("zero_channels", variant(channels=0)),
        ("negative_channels", variant(channels=-1)),
        ("bool_channels", variant(channels=True)),
        ("stereo_channels", variant(channels=2)),
        ("channels_over_local_guard", variant(channels=65)),
        ("zero_rate", variant(sample_rate_hz=0)),
        ("negative_rate", variant(sample_rate_hz=-48000)),
        ("bool_rate", variant(sample_rate_hz=True)),
        ("undeclared_rate_8k", variant(sample_rate_hz=8000)),
        ("undeclared_rate_16k", variant(sample_rate_hz=16000)),
        ("undeclared_rate_44k", variant(sample_rate_hz=44100)),
        ("zero_frame", variant(frame_samples=0)),
        ("too_large_frame", variant(frame_samples=4097)),
        ("v0_160_frame", variant(frame_samples=160)),
        ("reported_512_frame", variant(frame_samples=512)),
        ("short_samples", variant(samples=short)),
        ("long_samples", variant(samples=long)),
        ("wrong_multichannel_count", variant(channels=2,
                                             samples=[0.0] * 960)),
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
        ("negative_position", variant(first_input_sample=-960)),
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
        "note": ("Invalid, missing, nonfinite or unrecorded-geometry requests "
                 "are rejected before any artifact check or candidate call; "
                 "no metrics exist."),
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
            "official_artifact_terms_runtime_and_matched_cohort_absent"),
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
    skip = {".git", "node_modules", "__pycache__"}
    for current, directory_names, file_names in os.walk(path):
        current_path = Path(current)
        directory_names[:] = sorted(
            name for name in directory_names if name not in skip)
        if len(current_path.parts) - base_depth >= max_depth:
            directory_names[:] = []
        for name in sorted(file_names):
            if (Path(name).suffix.lower() in markers or name in markers):
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
        "status": "blocked_official_source_absent" if not found else
                  "source_present_unqualified",
        "present": bool(found),
        "vendor": VENDOR,
        "component": COMPONENT_NAME,
        "version": "NSNet2 (official artifact unpinned)",
        "repository": SOURCE_REPOSITORY,
        "documentation": DOC_URL,
        "documented_addition_commit": ADDITION_COMMIT,
        "documented_removal_commit": REMOVAL_COMMIT,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
        "official_download_path_available": False,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": ("Read-only existence checks only; no clone, fetch, archive "
                 "extraction or vendor file is opened or executed. The "
                 "recorded addition/removal commits are provenance from the "
                 "pinned census, not a local source pin."),
    }


def weights_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in SOURCE_CANDIDATE_PATHS + COHORT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.exists():
            hits = _markers_in(target, MODEL_MARKERS)
            found.extend((Path(label) / name).as_posix() for name in hits)
    return {
        "status": "blocked_official_model_artifact_absent" if not found else
                  "model_artifact_present_unqualified",
        "present": bool(found),
        "artifact": MODEL_ARTIFACT,
        "path": None,
        "sha256": None,
        "byte_count": None,
        "conversion_recipe": None,
        "precision": None,
        "quantization": None,
        "operator_set": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": ("Existence and file-name checks only; no model, graph or "
                 "binary is opened, loaded, converted or executed. A file "
                 "name match is not an artifact identity. The third-party "
                 "eco8-neaixt checkout is outside these official paths and is "
                 "recorded separately."),
    }


def license_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_model_terms_not_recorded",
        "reported_name": None,
        "reported_code_license": GENERAL_CODE_LICENSE,
        "reported_documentation_license": GENERAL_DOC_LICENSE,
        "general_repository_notice_recorded": True,
        "artifact_specific_model_terms_recorded": False,
        "reported_terms_recorded_in_pinned_evidence": False,
        "license_text_present": False,
        "license_text_sha256": None,
        "license_file": None,
        "model_terms_present": False,
        "training_data_terms_present": False,
        "use_approved": False,
        "redistribution_approved": False,
        "derived_output_publication_approved": False,
        "host_target_approved": False,
        "review": "blocked",
        "reviewed_by": None,
        "note": ("The pinned census records a general MIT code notice and a CC "
                 "BY 4.0 documentation notice, but no artifact-specific model "
                 "or training-data terms. Neither model terms text nor a "
                 "written rights decision is present, and upstream presence is "
                 "not a right to use or redistribute."),
    }


def hardware_probe() -> Dict[str, Any]:
    toolchain = {
        command: shutil.which(command) is not None
        for command in TOOLCHAIN_COMMANDS
    }
    return {
        "status": "blocked_eligible_runner_absent",
        "eligible_target": "pinned CPU ONNX Runtime execution host",
        "runner": None,
        "hardware_attached": None,
        "firmware_sha256": None,
        "toolchain_commands": toolchain,
        "toolchain_present": any(toolchain.values()),
        "serial_device_probed": False,
        "vendor_resource_figures_generalizable": False,
        "note": ("Host command discovery only. No pinned runner, ONNX Runtime "
                 "identity, firmware or hardware measurement is present or "
                 "claimed; command presence is not eligibility or approval."),
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
        "onnxruntime_version": None,
        "python_version": None,
        "operator_set": None,
        "firmware_sha256": None,
        "portable_host_runtime": None,
        "present": bool(found),
        "pinned": pinned,
        "sha256": None,
        "note": ("No hash-pinned ONNX Runtime, runner or package lock is "
                 "installed, executed or pinned. Path checks are read-only; "
                 "no import, build or inference is attempted."),
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
            "rights-cleared paired noisy/clean 48 kHz speech with consent, "
            "speaker/language metadata, noise conditions and matched "
            "quiet/active and onset/offset cases"),
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "corpus_rights": False,
        "clean_references_present": False,
        "sha256": None,
        "note": ("Existence checks only; no audio file is opened or decoded. "
                 "A synthetic harness frame is not a matched cohort."),
    }


def scorer_probe() -> Dict[str, Any]:
    present = [path for path in SCORER_CANDIDATE_PATHS
               if _resolve_workspace_path(path).exists()]
    return {
        "status": "unapproved_no_scorer_implemented",
        "approved_si_sdr": False,
        "approved_stoi": False,
        "authorized_listening": False,
        "predictive_screen_labeled": False,
        "candidate_paths_present": sorted(present),
        "sha256": None,
        "calibrated_here": False,
        "note": ("No approved SI-SDR, STOI, DNSMOS or listening protocol is "
                 "present. This package implements no scorer and reports no "
                 "quality metric."),
    }


def rights_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_rights_unrecorded",
        "source_license": None,
        "license_text_present": False,
        "license_text_sha256": None,
        "model_terms_present": False,
        "training_data_terms_present": False,
        "use_approved": False,
        "redistribution_approved": False,
        "derived_output_publication_approved": False,
        "host_target_approved": False,
        "input_corpus_rights": False,
        "redistribution_scope": None,
        "review": "blocked",
        "reviewed_by": None,
        "note": ("No artifact-specific model terms, rights decision, "
                 "distribution scope or cohort permission is recorded "
                 "locally. The general repository notice does not establish "
                 "official model-artifact terms."),
    }


def third_party_probe() -> Dict[str, Any]:
    root = _resolve_workspace_path(THIRD_PARTY_PATH)
    present = root.is_dir()
    license_file = root / "LICENSE"
    license_text_present = license_file.is_file()
    reported_license = None
    if license_text_present:
        first_line = license_file.read_text(
            encoding="utf-8", errors="replace").splitlines()[:1]
        if first_line and "MIT License" in first_line[0]:
            reported_license = "MIT"
    weight_candidates = (_markers_in(root, MODEL_MARKERS) if present else [])
    source_dir = root / "nsnet2"
    return {
        "status": "third_party_reimplementation_present_not_official"
                  if present else "third_party_reimplementation_absent",
        "path": THIRD_PARTY_PATH,
        "present": present,
        "official_microsoft_nsnet2": False,
        "accepted_as_official_artifact": False,
        "accepted_as_substitute": False,
        "source_dir_present": source_dir.is_dir(),
        "reported_license": reported_license,
        "license_file_present": license_text_present,
        "license_scope": (
            "third-party repository code only; not official model terms"
            if present else None),
        "weights_present_locally": bool(weight_candidates),
        "weight_candidates": sorted(set(weight_candidates)),
        "geometry_note": (
            "third-party 16 kHz VoiceBank-DEMAND training recipe documented "
            "by that project; not the official 48 kHz DNS baseline"),
        "note": (
            "The checkout is a third-party NSNet2 reimplementation. It has no "
            "staged weights, a different sample rate and training recipe, and "
            "no official artifact identity or terms. It is recorded only to "
            "show it was considered and rejected, never used as a substitute."),
    }


def geometry() -> Dict[str, Any]:
    return {
        "vendor": VENDOR,
        "component": COMPONENT_NAME,
        "component_version": "NSNet2 (official artifact unpinned)",
        "declared_sample_rates_hz": list(DECLARED_SAMPLE_RATES_HZ),
        "declared_frame_ms": DECLARED_FRAME_MS,
        "declared_hop_ms": None,
        "derived_frame_samples_at_48k": DECLARED_FRAME_SAMPLES,
        "derived_hop_samples_at_48k": None,
        "derivation": GEOMETRY_DERIVATION,
        "derived_sample_counts_are_api_constants": False,
        "reported_parameter_count": None,
        "declared_channels": None,
        "local_channel_guard": MAX_CHANNELS_GUARD,
        "declared_feature_extraction": None,
        "declared_output_mapping": None,
        "declared_buffering_delay_samples": None,
        "declared_reset_drain_semantics": None,
        "declared_quantization": None,
        "declared_target": "pinned CPU ONNX Runtime execution host",
        "vendor_resource_figures_generalizable": False,
        "official_download_path_available": False,
        "v0_can_represent_declared_input": False,
        "verified_here": False,
        "measured_here": False,
        "candidate_output": False,
        "note": (
            "Only the 48 kHz rate and 20 ms frame duration are recorded from "
            "the pinned census. The 960-sample count is arithmetic from the "
            "reported duration at 48 kHz and is not a pinned API constant. "
            "The hop, channel handling, feature extraction, output mapping, "
            "delay, reset/drain and quantization are absent and were not "
            "inferred. The 1..64 channel guard is a local evidence bound, not "
            "a vendor limit."),
    }


def profile_mapping() -> Dict[str, str]:
    return {
        "identity_and_noisy_control": "blocked_no_candidate_output",
        "established_task_matched_baseline": "blocked_no_permitted_baseline",
        "paired_si_sdr_stoi": "blocked_no_candidate_output_and_no_approved_scorer",
        "clean_speech_preservation": "blocked_no_permitted_cohort",
        "peaks_and_invalid_outputs": "partial_local_harness_rejection_only",
        "unpaired_predictive_screen_or_authorized_listening":
            "blocked_no_permitted_cohort_or_panel",
        "alignment_and_state": "blocked_no_candidate_instance",
        "memory_and_measured_content_availability_timing":
            "blocked_no_paced_measurement",
        "candidate_output":
            "blocked_official_artifact_terms_runtime_and_matched_cohort_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "exact_official_source_revision_and_tree_digest":
            "blocked_official_source_absent",
        "exact_official_model_artifact_and_conversion_identity":
            "blocked_official_model_absent",
        "code_model_and_training_data_terms":
            "blocked_rights_not_recorded",
        "pinned_onnx_runtime_and_reproducible_runner":
            "blocked_runtime_absent",
        "pinned_geometry_features_and_delay": "blocked_config_absent",
        "caller_supplied_reference_and_state_parity":
            "blocked_no_candidate_instance",
        "identity_and_noisy_control": "blocked_no_candidate_output",
        "paired_si_sdr_and_stoi": "blocked_no_approved_scorer_or_cohort",
        "clean_speech_preservation": "blocked_no_permitted_cohort",
        "unpaired_screen_or_authorized_listening":
            "blocked_no_permitted_cohort_or_panel",
        "memory_state_and_paced_timing": "blocked_no_paced_measurement",
        "opt_in_adapter_intake": "blocked_no_approved_runtime_or_terms",
        "release_qualification": "blocked_no_release_evidence",
    }


def candidates() -> Dict[str, Any]:
    return {
        CANDIDATE: {
            "status": (
                "blocked_official_artifact_terms_runtime_and_matched_cohort_absent"),
            "metrics": None,
            "qualifies_candidate": False,
            "result": None,
            "reason": (
                "No official DNS-Challenge source, official NSNet2 48 kHz "
                "ONNX artifact, artifact-specific terms, pinned runtime or "
                "runner, configuration or rights-cleared matched cohort is "
                "present; no denoising, preservation, alignment, state, "
                "memory or timing result was produced. The third-party "
                "eco8-neaixt reimplementation is not substituted."),
        }
    }


def controls() -> Dict[str, Any]:
    return {
        "identity_control": {
            "status": "bit_exact_synthetic_only",
            "candidate_processing": False,
            "qualifies_candidate": False,
        },
        "source_reported_census_characteristics": {
            "status": "provenance_only_not_reproduced",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "unapproved_scorer": {
            "status": "not_implemented_not_calibrated",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "third_party_substitute": {
            "status": "present_but_rejected",
            "official": False,
            "accepted": False,
            "metrics": None,
            "qualifies_candidate": False,
        },
        "model_fallback": {
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
        transferred = identity_transfer(samples)
        identity[name] = {
            "source_digest": tensor_digest(samples),
            "transfer_digest": tensor_digest(transferred),
            "byte_identical": tuple(samples) == transferred,
        }
    return {
        "purpose": (
            "harness stimulus characterisation only; not a Microsoft NSNet2 "
            "result and not a candidate output"),
        "harness_geometry": {
            "channels": HARNESS_CHANNELS,
            "frame_samples": HARNESS_FRAME_SAMPLES,
            "hop_samples": HARNESS_HOP_SAMPLES,
            "flat_values": HARNESS_FRAME_VALUES,
            "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
            "verified_model_geometry": False,
            "note": (
                "The 960-sample frame is arithmetic from the source-reported "
                "20 ms duration at 48 kHz and is used only to exercise "
                "validation and rejection. The hop is unrecorded and absent. "
                "These values are not a claim about the vendor API, model "
                "configuration or implementation."),
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
        blockers.append("official_source_absent")
    if not weights_probe()["present"]:
        blockers.append("official_model_artifact_absent")
    if license_probe()["review"] != "approved":
        blockers.append("model_terms_not_recorded")
    if not runtime_probe()["pinned"]:
        blockers.append("runtime_unpinned")
    if runtime_probe()["portable_host_runtime"] is None:
        blockers.append("portable_host_runtime_absent")
    if hardware_probe()["runner"] is None:
        blockers.append("eligible_runner_absent")
    if not cohort_probe()["present"]:
        blockers.append("matched_cohort_absent")
    if not scorer_probe()["approved_si_sdr"]:
        blockers.append("scorer_unapproved")
    if rights_probe()["review"] != "approved":
        blockers.append("rights_unrecorded")
    third_party = third_party_probe()
    if third_party["present"] and not third_party["accepted_as_substitute"]:
        blockers.append("third_party_reimplementation_not_accepted")
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
            "official source, official model artifact, artifact terms, "
            "runtime, runner, matched cohort, scorer and rights are absent. "
            "No port, fallback, mirror or surrogate is used."),
    }


def probe_candidate(request: Any) -> None:
    validate_request(request)
    raise ArtifactsAbsent(
        "ARTIFACTS_ABSENT: official DNS-Challenge source, official NSNet2 "
        "48 kHz ONNX artifact, model terms, pinned runtime and matched cohort "
        "are not present; no processing is performed", "ARTIFACTS_ABSENT")


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
        ("research/noise_suppression_candidate_census.md records Microsoft "
         "NSNet2 as a frequency-mask DNN and a 48 kHz, 20 ms DNS baseline."),
        ("the same note records that the ICASSP 2022 paper links the official "
         "48 kHz ONNX model and reports it as the non-personalized baseline."),
        ("the same note records that the code/model were removed from the "
         "current DNS-Challenge branch in commit " + REMOVAL_COMMIT +
         " after being added in " + ADDITION_COMMIT + "."),
        ("the same note records that the current general legal notice "
         "separates MIT code from CC BY 4.0 documentation/other content but "
         "does not state model-artifact-specific terms."),
        ("the same note records that the official current download path is "
         "gone, no authoritative artifact digest or checkpoint-specific "
         "terms were confirmed, and surviving copies are forks or mirrors; "
         "they must not be substituted as official weights."),
        ("plan/INVENTORY.json assigns microsoft-nsnet2-baseline the "
         "enhancement verification profile, disposition sdk-model and an "
         "evidence status of considered."),
        ("plan/audio-sdk/README.md requires runnable source, exact assets, "
         "permitted scope and matched evidence before a caller-supplied "
         "reference or opt-in SDK adapter is added."),
        ("No official DNS-Challenge source that still ships NSNet2, official "
         "48 kHz ONNX artifact, artifact-specific terms, pinned ONNX Runtime, "
         "configuration, matched cohort or approved scorer exists locally. A "
         "third-party eco8-neaixt reimplementation is present but rejected as "
         "a substitute; nothing was cloned, downloaded, ported or "
         "reconstructed."),
    ]


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    source = source_probe()
    weights = weights_probe()
    license_block = license_probe()
    hardware = hardware_probe()
    runtime = runtime_probe()
    cohort = cohort_probe()
    scorer = scorer_probe()
    rights = rights_probe()
    third_party = third_party_probe()
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
        "official_source_absent": source["present"] is False,
        "official_model_artifact_absent": weights["present"] is False,
        "model_terms_not_recorded": license_block["review"] == "blocked",
        "license_text_absent":
            license_block["license_text_present"] is False,
        "eligible_runner_absent": hardware["runner"] is None,
        "runtime_unpinned": runtime["pinned"] is False,
        "portable_host_runtime_absent":
            runtime["portable_host_runtime"] is None,
        "matched_cohort_absent": cohort["present"] is False,
        "scorer_unapproved": scorer["approved_si_sdr"] is False,
        "rights_unrecorded": rights["review"] == "blocked",
        "third_party_not_accepted": (
            third_party["accepted_as_official_artifact"] is False and
            third_party["accepted_as_substitute"] is False),
        "third_party_weights_absent":
            third_party["weights_present_locally"] is False,
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "missing_and_unrecorded_geometry_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith(("missing", "undeclared", "wrong_",
                                      "v0_", "reported_", "unexpected_"))),
        "nonfinite_samples_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith("nonfinite")),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked":
            missing_result("microsoft_nsnet2_placeholder")["status"] ==
            "blocked",
        "identity_control_bit_exact": all(
            block["byte_identical"]
            for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
        "model_boundary_closed": (
            MODEL_BOUNDARY["adapter_implemented"] is False and
            MODEL_BOUNDARY["adapter_default_registration"] is False and
            MODEL_BOUNDARY["automatic_discovery"] is False and
            MODEL_BOUNDARY["third_party_accepted_as_official"] is False),
        "no_scorer_or_metric_present": (
            ENHANCEMENT_CONTROL["metrics"] is None and
            ENHANCEMENT_CONTROL["result"] is None),
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
        "model_boundary": dict(MODEL_BOUNDARY),
        "evidence_classes": [
            "pinned_census_and_inventory_provenance",
            "explicit_missing_official_artifact_and_rights_blocker",
            "deterministic_bytes_and_digests",
            "synthetic_harness_controls_only",
            "third_party_substitute_rejected",
            "no_quality_or_timing_measurement",
        ],
        "reference": {
            "implementation": "task-local standard-library model-feasibility gate",
            "real_component_source_present": source["present"],
            "official_model_artifact_present": weights["present"],
            "component_config_present": False,
            "eligible_runner_present": hardware["runner"] is not None,
            "pinned_runtime_present": runtime["pinned"],
            "portable_host_runtime_present":
                runtime["portable_host_runtime"] is not None,
            "matched_cohort_present": cohort["present"],
            "approved_scorer_present": scorer["approved_si_sdr"],
            "license_text_present": license_block["license_text_present"],
            "rights_approved": False,
            "third_party_reimplementation_present": third_party["present"],
            "third_party_accepted_as_official":
                third_party["accepted_as_official_artifact"],
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "real_corpus_read": False,
            "note": (
                "No NSNet2 inference, port, surrogate, mirror substitution or "
                "approximation is implemented or simulated; only probes, "
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
        "weights_probe": weights,
        "license_probe": license_block,
        "hardware_probe": hardware,
        "runtime_probe": runtime,
        "cohort_probe": cohort,
        "scorer_probe": scorer,
        "rights_probe": rights,
        "third_party_probe": third_party,
        "geometry": geom,
        "enhancement_control": dict(ENHANCEMENT_CONTROL),
        "scorer": dict(SCORER_PROBE_BLOCK),
        "candidates": candidates(),
        "controls": controls(),
        "required_results": candidate_required_results(),
        "stimulus_probe": stimuli,
        "adverse": {
            "invalid_config_and_input": adverse_request,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": missing_result("microsoft_nsnet2_placeholder"),
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
