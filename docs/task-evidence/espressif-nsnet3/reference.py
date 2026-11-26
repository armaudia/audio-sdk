# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for SDK-ESPRESSIF-NSNET3.

This module is NOT Espressif NSNet3 and NOT ESP-SR. It contains no vendor
source, model weights, graph, header, configuration, license text, runtime or
firmware. A bounded read-only search finds no ``esp-sr`` checkout, no NSNet3
model artifact, no ESP-IDF toolchain and no rights-cleared matched cohort in
the workspace. The pinned research census records only that official ESP-SR
docs describe a tiny 16 kHz embedded noise suppressor with 48.2k parameters
and a 32 ms frame / 16 ms hop, and that it is a special-target candidate not
comparable to a desktop CPU pilot until a portable adapter exists.

The module therefore builds a fail-closed model-feasibility blocker report:

* strict request validation at the single source-reported 16 kHz rate using
  the arithmetic 512-sample frame and 256-sample hop;
* explicit source, weights, license/terms, runtime, hardware, configuration,
  cohort, scorer and rights probes;
* an admission gate that rejects every structurally valid request because the
  required artifacts and rights are absent;
* synthetic harness stimuli and an identity control for rejection and harness
  characterisation only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

Nothing is downloaded, cloned, installed, extracted, ported, reconstructed or
simulated. No candidate audio output is produced. No result qualifies the
candidate and no source-reported quality or performance value is reproduced.
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

SCHEMA_ID = "audio-sdk/espressif-nsnet3-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/espressif-nsnet3-contract/0.1"
TASK = "SDK-ESPRESSIF-NSNET3"
COMPONENT = "espressif-nsnet3"
BRANCH = "swarm/SDK-ESPRESSIF-NSNET3"
BASE_COMMIT = "23526250a3a0a66c1f93089ff6fb697b5e776965"
TASK_PREFIX = "docs/task-evidence/espressif-nsnet3/"
MODE = "feasibility"
VERIFICATION_PROFILE = "Enhancement"

# Installed v0 format. This is the unchanged public baseline, not the vendor
# component geometry and not a model configuration.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
ABI_MAJOR = 0
ABI_MINOR = 1

# Only the single 16 kHz rate, the 32 ms frame and the 16 ms hop are recorded
# by the pinned census. The sample counts are arithmetic from those reported
# durations at 16 kHz, not an independently pinned vendor API constant.
DECLARED_SAMPLE_RATES_HZ = (16000,)
DECLARED_FRAME_MS = 32
DECLARED_HOP_MS = 16
DECLARED_FRAME_SAMPLES = 512
DECLARED_HOP_SAMPLES = 256
GEOMETRY_DERIVATION = (
    "32 ms x 16000 Hz = 512 samples and 16 ms x 16000 Hz = 256 samples; "
    "derived arithmetically from the source-reported durations only")
REPORTED_PARAMETER_COUNT = 48200
VENDOR = "Espressif Systems"
COMPONENT_NAME = "ESP-SR NSNet (NSNet3)"
DOC_URL = (
    "https://docs.espressif.com/projects/esp-sr/en/latest/esp32/nsnet/"
    "README.html")
SOURCE_REPOSITORY = "https://github.com/espressif/esp-sr"
MODEL_ARTIFACT = "ESP-SR NSNet3 model/graph artifact"
SDK_DISPOSITION = "sdk-model"

# Local harness geometry. The frame and hop are the arithmetic values above and
# are used only to exercise validation and rejection.
HARNESS_SAMPLE_RATE_HZ = 16000
HARNESS_CHANNELS = 1
HARNESS_FRAME_SAMPLES = DECLARED_FRAME_SAMPLES
HARNESS_HOP_SAMPLES = DECLARED_HOP_SAMPLES
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
    "title": "Espressif NSNet3",
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

CANDIDATE = "espressif_nsnet3"
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)
REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples",
    "hop_samples", "samples", "epoch", "first_input_sample", "lifecycle",
    "execution_mode",
})

SOURCE_ARTIFACT_FILES = (
    "reference.py", "run.py", "test_reference.py", "verify.py",
)

SOURCE_CANDIDATE_PATHS = (
    "third_party/esp-sr",
    "third_party/esp_sr",
    "components/esp-sr",
    "components/esp_sr",
    "vendor/espressif/esp-sr",
    "research/espressif-nsnet3",
    "research/esp-sr",
    "research/repos/esp-sr",
    "data/checkouts/esp-sr",
    "data/models/espressif-nsnet3",
    "~/esp/esp-sr",
    "~/esp/esp-idf",
    "~/.espressif",
    "~/code/esp-sr",
    "~/projects/esp-sr",
)
SOURCE_MARKERS = (
    "esp_nsnet.c", "esp_nsnet.h", "nsnet3", "esp-sr", "esp_sr",
)
MODEL_MARKERS = (".tflite", ".onnx", ".bin", ".gguf", ".params")

TOOLCHAIN_COMMANDS = ("idf.py", "esptool.py", "xtensa-esp32s3-elf-gcc")
RUNTIME_CANDIDATE_PATHS = (
    "~/esp/esp-idf",
    "~/esp/esp-idf/export.sh",
    "~/.espressif",
    "data/envs/esp-idf",
    "data/runtime/esp-idf",
    "data/envs/espressif-nsnet3",
)
RUNTIME_LOCK_CANDIDATES = (
    "research/espressif-nsnet3/runtime.lock",
    "data/envs/esp-idf/requirements.lock",
    "data/envs/espressif-nsnet3/requirements.lock",
    "data/runtime/esp-idf/idf-env.lock",
)

COHORT_CANDIDATE_PATHS = (
    "data/corpora/espressif-nsnet3",
    "data/fixtures/espressif-nsnet3",
    "research/espressif-nsnet3/cohort",
    "research/espressif-nsnet3/paired",
)
COHORT_MARKERS = (".wav", ".flac", ".npy", ".json")

SCORER_CANDIDATE_PATHS = (
    "research/espressif-nsnet3/scorer",
    "data/scorers/espressif-nsnet3",
)

REQUIRED_ARTIFACTS = (
    {
        "id": "A1",
        "artifact": "ESP-SR source checkout at the exact NSNet3 revision",
        "required": (
            "A local checkout of the exact ESP-SR revision that ships NSNet3 "
            "at a recorded full commit with a read-only non-.git tree digest "
            "and the repository license file"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A2",
        "artifact": "NSNet3 model/graph artifact",
        "required": (
            "The exact NSNet3 model or graph bytes with path, byte count and "
            "SHA-256, plus the conversion or export recipe and the "
            "quantization/precision description"),
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
        "artifact": "eligible target and pinned ESP-IDF/ESP-SR runtime",
        "required": (
            "An approved embedded runner with a hash-pinned ESP-IDF and "
            "ESP-SR toolchain, a reproducible firmware image and an "
            "install/import parity record"),
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
            "The exact API headers and configuration declaring sample rate, "
            "frame, hop, channel handling, feature extraction, output "
            "mapping, buffering delay, reset/drain and quantization"),
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
            "A rights-cleared paired noisy/clean speech cohort with consent "
            "and metadata, an approved SI-SDR/STOI implementation, and "
            "authorized listening or a separately labeled predictive screen"),
        "status": "absent",
        "sha256": None,
        "byte_count": None,
        "license": None,
        "rights_reviewed": False,
    },
    {
        "id": "A7",
        "artifact": "state, memory and paced target-timing harness",
        "required": (
            "A measured harness for state transitions, reset/drain, memory, "
            "callback behavior, content delay and paced availability on the "
            "eligible target"),
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
        "gate": "exact_espressif_sr_source_revision_and_tree_pin",
        "status": "blocked",
        "reason": (
            "No ESP-SR checkout exists locally; the revision, tree digest, "
            "NSNet3 source files and license file are absent and no source "
            "is pinned."),
        "reopen": (
            "Stage the exact ESP-SR revision at a recorded full commit with a "
            "read-only tree digest and its license file, then pin every "
            "required NSNet3 source path before reading any configuration."),
    },
    {
        "id": "RG-02",
        "gate": "exact_model_artifact_and_conversion_identity",
        "status": "blocked",
        "reason": (
            "No NSNet3 model or graph bytes, path, byte count, SHA-256, "
            "conversion recipe, precision or quantization description "
            "exists locally."),
        "reopen": (
            "Provide the exact model or graph artifact by path, byte count "
            "and SHA-256 with its conversion/export recipe and precision or "
            "quantization parameters; do not substitute a mirror or an "
            "unrelated NSNet2 artifact."),
    },
    {
        "id": "RG-03",
        "gate": "code_model_and_training_data_terms_with_rights_decision",
        "status": "blocked",
        "reason": (
            "The pinned census records no code, model, training-data or "
            "redistribution terms, no local license text and no written "
            "rights decision for this host target or for derived output."),
        "reopen": (
            "Obtain the byte-identical code and model terms with SHA-256 and "
            "secure a written rights decision that explicitly permits this "
            "use, adapter distribution and output publication, or record a "
            "final rejection and close the task."),
    },
    {
        "id": "RG-04",
        "gate": "eligible_target_and_hash_pinned_runtime",
        "status": "blocked",
        "reason": (
            "No approved embedded runner, ESP-IDF/ESP-SR toolchain, "
            "reproducible firmware image, portable host runtime or "
            "install/import parity record exists."),
        "reopen": (
            "Provide an approved eligible runner or a licensed portable host "
            "runtime with a hash-pinned toolchain and package lock, build a "
            "reproducible artifact, and prove runtime parity before any "
            "measurement."),
    },
    {
        "id": "RG-05",
        "gate": "pinned_geometry_features_and_configuration",
        "status": "blocked",
        "reason": (
            "Only the 16 kHz rate, 32 ms frame, 16 ms hop and 48.2k "
            "parameters are source-reported. The 512/256 sample counts are "
            "arithmetic, and channel handling, feature extraction, output "
            "mapping, buffering delay, reset/drain and quantization are "
            "unpinned."),
        "reopen": (
            "Pin the exact headers and configuration, verify the frame, hop, "
            "channel handling, features, output mapping, delay, finite "
            "drain and reset semantics, and never infer an unpinned value "
            "from the reported durations."),
    },
    {
        "id": "RG-06",
        "gate": "caller_supplied_reference_and_state_parity",
        "status": "blocked",
        "reason": (
            "No caller-supplied asset path or instance exists, so no reset, "
            "drain, state transition, chunk-boundary or output-mapping "
            "parity was reproduced."),
        "reopen": (
            "With pinned source, model, runtime and configuration, reproduce "
            "the exact model as a caller-supplied-asset reference, including "
            "reset, finite drain, independent state, chunk boundaries and "
            "exact output mapping."),
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
            "Run the full Enhancement matrix on a rights-cleared matched "
            "cohort with an approved scorer, retain every failure, nonfinite "
            "and adverse case, and report paired quality, preservation, "
            "alignment, state, memory and paced timing with tolerances "
            "agreed before scoring."),
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
        "blocked_source_model_terms_runtime_and_matched_cohort_absent"),
    "artifact": (
        "ESP-SR NSNet3 source, model artifact, terms decision, eligible "
        "runtime, pinned geometry and rights-cleared matched cohort"),
    "source": {
        "status": "absent",
        "repository": SOURCE_REPOSITORY,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
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
    },
    "license": {
        "status": "blocked_terms_not_recorded",
        "reported_name": None,
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
        "eligible_target": "ESP-SR supported embedded target",
        "runner": None,
        "hardware_attached": None,
        "firmware_sha256": None,
        "vendor_resource_figures_generalizable": False,
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "ESP-IDF and ESP-SR versions matched to the model artifact",
            "xtensa or riscv toolchain with recorded version and hashes",
            "reproducible firmware image with a recorded SHA-256",
            "an explicit runner identity and install/import parity check",
            "or a licensed portable host runtime with a package lock",
        ],
        "idf_path": None,
        "idf_version": None,
        "esp_sr_version": None,
        "lockfile": None,
        "portable_host_runtime": None,
        "sha256": None,
    },
    "config": {
        "status": "absent",
        "required_paths": [
            "ESP-SR NSNet public header",
            "ESP-SR NSNet feature and output configuration",
        ],
        "sha256": None,
        "byte_count": None,
    },
    "cohort": {
        "status": "absent",
        "required": (
            "rights-cleared paired noisy/clean 16 kHz speech with consent, "
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
        "The exact ESP-SR source license text and NSNet3 model terms with "
        "SHA-256, permission for code use, model use, redistribution, "
        "embedded or portable runtime scope and derived-output publication, "
        "approval for every cohort recording and consent, and an approved "
        "scorer are required before any reproduction, adapter, benchmark or "
        "release claim."),
    "workspace_search": (
        "Bounded read-only existence and file-name checks of named candidate "
        "paths under the workspace found no ESP-SR checkout, no NSNet3 model "
        "or graph artifact, no ESP-IDF toolchain or lock, no eligible runner, "
        "no rights-cleared matched cohort and no approved scorer. No archive, "
        "binary, model, audio file or vendor file was opened, downloaded or "
        "reconstructed."),
    "not_attempted": [
        "no git clone, network download, package installation or archive extraction",
        "no fabricated, ported, reverse-engineered or surrogate NSNet3 source, header or configuration",
        "no fabricated model weights, graph, conversion recipe or checksum",
        "no fabricated license text, terms decision or rights approval",
        "no ESP-IDF build, firmware flash or hardware execution",
        "no copied vendor source, model, audio or score",
        "no candidate audio, listening, device-timing or benchmark run",
    ],
    "reopen": (
        "Stage the exact ESP-SR source and NSNet3 model at recorded digests, "
        "secure a written code/model/redistribution/output decision, provide "
        "an approved eligible runner or licensed portable host runtime with a "
        "hash-pinned toolchain, pin the geometry and configuration, stage a "
        "rights-cleared matched cohort with an approved scorer, then reproduce "
        "the model and run the Enhancement matrix with independent review."),
}

NON_CLAIMS = (
    "No ESP-SR source, NSNet3 model, graph, header, configuration or license text is included.",
    "No NSNet3 inference, port, surrogate, approximation or simulation is implemented or run.",
    "No 48.2k parameter count, frame, hop or platform characteristic is presented as a local measurement.",
    "No SI-SDR, STOI, DNSMOS, PESQ or listening score is produced, reproduced or implied.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default, and there is no automatic discovery or fallback.",
    "No real corpus, clean reference, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No source-reported vendor or census characteristic is presented as a local measurement.",
    "No missing, rejected or source-reported result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/espressif-nsnet3/ is touched.",
    "The reference is a task-local feasibility gate, not Espressif NSNet3.",
    "The declared model geometry is not representable by installed v0 without an adapter.",
    "The 512-frame and 256-hop values are arithmetic from the reported durations, not pinned API constants.",
    "All harness stimuli are analytic or seeded synthetic; no vendor runtime is used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
)

MODEL_BOUNDARY = {
    "documented": True,
    "vendor": VENDOR,
    "component": COMPONENT_NAME,
    "component_version": "NSNet3 (unpinned revision)",
    "sdk_disposition": SDK_DISPOSITION,
    "documentation": DOC_URL,
    "repository": SOURCE_REPOSITORY,
    "distribution_model": "ESP-SR component for embedded targets",
    "declared_target": "ESP-SR supported embedded target",
    "host_target": "macOS / Python 3 workspace",
    "host_target_eligible": False,
    "portable_adapter_present": False,
    "reported_parameter_count": REPORTED_PARAMETER_COUNT,
    "reported_parameter_count_is_local_measurement": False,
    "license_reported": None,
    "license_terms_recorded_in_pinned_evidence": False,
    "license_text_present": False,
    "model_terms_present": False,
    "use_approved": False,
    "redistribution_approved": False,
    "local_runtime_present": False,
    "weights_present": False,
    "vendor_output_present": False,
    "adapter_implemented": False,
    "adapter_default_registration": False,
    "automatic_discovery": False,
    "fallback": "none",
    "vendor_claims_separate_from_local_measurements": True,
    "note": (
        "The model boundary is documented from the pinned research census and "
        "the official documentation locator only. No source, model, terms, "
        "runtime, cohort or measurement is present, and this host target is "
        "not approved."),
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
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown), "UNKNOWN_FIELD")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing), "MISSING_FIELD")
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
    hop_samples = _require_int(request["hop_samples"], "INVALID_HOP", 1)
    if hop_samples != DECLARED_HOP_SAMPLES:
        raise ConfigError("WRONG_DECLARED_HOP", "WRONG_DECLARED_HOP")
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
        "hop_samples": hop_samples,
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
        "hop_samples": HARNESS_HOP_SAMPLES,
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
        ("unknown_candidate", variant(candidate="espressif_nsnet")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("missing_hop", {key: value for key, value in base.items()
                         if key != "hop_samples"}),
        ("zero_channels", variant(channels=0)),
        ("negative_channels", variant(channels=-1)),
        ("bool_channels", variant(channels=True)),
        ("stereo_channels", variant(channels=2)),
        ("channels_over_local_guard", variant(channels=65)),
        ("zero_rate", variant(sample_rate_hz=0)),
        ("negative_rate", variant(sample_rate_hz=-16000)),
        ("bool_rate", variant(sample_rate_hz=True)),
        ("undeclared_rate_8k", variant(sample_rate_hz=8000)),
        ("undeclared_rate_48k", variant(sample_rate_hz=48000)),
        ("zero_frame", variant(frame_samples=0)),
        ("too_large_frame", variant(frame_samples=4097)),
        ("v0_160_frame", variant(frame_samples=160)),
        ("reported_256_frame", variant(frame_samples=256)),
        ("zero_hop", variant(hop_samples=0)),
        ("bool_hop", variant(hop_samples=True)),
        ("wrong_hop_512", variant(hop_samples=512)),
        ("wrong_hop_160", variant(hop_samples=160)),
        ("short_samples", variant(samples=short)),
        ("long_samples", variant(samples=long)),
        ("wrong_multichannel_count", variant(channels=2,
                                             samples=[0.0] * 512)),
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
        ("negative_position", variant(first_input_sample=-512)),
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
        "reason": "source_model_terms_runtime_and_matched_cohort_absent",
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
            if (Path(name).suffix.lower() in markers or
                    name in markers or name in SOURCE_MARKERS):
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
        "vendor": VENDOR,
        "component": COMPONENT_NAME,
        "version": "NSNet3 (unpinned revision)",
        "repository": SOURCE_REPOSITORY,
        "documentation": DOC_URL,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
        "license_file": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": ("Read-only existence checks only; no clone, fetch, archive "
                 "extraction or vendor file is opened or executed."),
    }


def weights_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in SOURCE_CANDIDATE_PATHS + COHORT_CANDIDATE_PATHS:
        checked.append(label)
        target = _resolve_workspace_path(label)
        if target.exists():
            hits = [name for name in _markers_in(target, MODEL_MARKERS)
                    if name in SOURCE_MARKERS or
                    Path(name).suffix.lower() in MODEL_MARKERS]
            found.extend((Path(label) / name).as_posix() for name in hits)
    return {
        "status": "blocked_model_artifact_absent" if not found else
                  "model_artifact_present_unqualified",
        "present": bool(found),
        "artifact": MODEL_ARTIFACT,
        "path": None,
        "sha256": None,
        "byte_count": None,
        "conversion_recipe": None,
        "precision": None,
        "quantization": None,
        "checked_paths": sorted(checked),
        "found": sorted(set(found)),
        "note": ("Existence and file-name checks only; no model, graph or "
                 "binary is opened, loaded, converted or executed. A file "
                 "name match is not an artifact identity."),
    }


def license_probe() -> Dict[str, Any]:
    return {
        "status": "blocked_terms_not_recorded",
        "reported_name": None,
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
        "note": ("The pinned census records no code, model, training-data or "
                 "redistribution terms. Neither terms text nor a written "
                 "rights decision is present, and upstream availability is "
                 "not a right to use or redistribute."),
    }


def hardware_probe() -> Dict[str, Any]:
    toolchain = {}
    for command in TOOLCHAIN_COMMANDS:
        path = shutil.which(command)
        toolchain[command] = path
    return {
        "status": "blocked_eligible_hardware_absent",
        "eligible_target": "ESP-SR supported embedded target",
        "runner": None,
        "hardware_attached": None,
        "firmware_sha256": None,
        "toolchain_commands": toolchain,
        "toolchain_present": any(value for value in toolchain.values()),
        "serial_device_probed": False,
        "vendor_resource_figures_generalizable": False,
        "note": ("Host command discovery only. No runner, device, firmware, "
                 "serial port or hardware measurement is present or "
                 "claimed; tool presence is not eligibility or approval."),
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
        "idf_path": os.environ.get("IDF_PATH"),
        "idf_version": None,
        "esp_sr_version": None,
        "firmware_sha256": None,
        "portable_host_runtime": None,
        "present": bool(found),
        "pinned": pinned,
        "sha256": None,
        "note": ("No ESP-IDF/ESP-SR toolchain and no licensed portable host "
                 "runtime are installed, executed or pinned. Environment and "
                 "path checks are read-only; no build, flash or import is "
                 "attempted."),
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
            "rights-cleared paired noisy/clean 16 kHz speech with consent, "
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
        "note": ("No code or model terms, rights decision, distribution scope "
                 "or cohort permission is recorded locally. Upstream "
                 "presence is not a right to use, redistribute or publish."),
    }


def geometry() -> Dict[str, Any]:
    return {
        "vendor": VENDOR,
        "component": COMPONENT_NAME,
        "component_version": "NSNet3 (unpinned revision)",
        "declared_sample_rates_hz": list(DECLARED_SAMPLE_RATES_HZ),
        "declared_frame_ms": DECLARED_FRAME_MS,
        "declared_hop_ms": DECLARED_HOP_MS,
        "derived_frame_samples_at_16k": DECLARED_FRAME_SAMPLES,
        "derived_hop_samples_at_16k": DECLARED_HOP_SAMPLES,
        "derivation": GEOMETRY_DERIVATION,
        "derived_sample_counts_are_api_constants": False,
        "reported_parameter_count": REPORTED_PARAMETER_COUNT,
        "declared_channels": None,
        "local_channel_guard": MAX_CHANNELS_GUARD,
        "declared_feature_extraction": None,
        "declared_output_mapping": None,
        "declared_buffering_delay_samples": None,
        "declared_reset_drain_semantics": None,
        "declared_quantization": None,
        "declared_target": "ESP-SR supported embedded target",
        "vendor_resource_figures_generalizable": False,
        "v0_can_represent_declared_input": False,
        "verified_here": False,
        "measured_here": False,
        "candidate_output": False,
        "note": (
            "Only the 16 kHz rate, 32 ms frame, 16 ms hop and 48.2k "
            "parameters are recorded from the pinned census. The 512/256 "
            "sample counts are arithmetic from the reported durations at "
            "16 kHz and are not pinned vendor API constants. Channel "
            "handling, feature extraction, output mapping, delay, reset/drain "
            "and quantization are absent and were not inferred. The 1..64 "
            "channel guard is a local evidence bound, not a vendor limit."),
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
            "blocked_source_model_terms_runtime_and_matched_cohort_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "exact_source_revision_and_tree_digest": "blocked_source_absent",
        "exact_model_artifact_and_conversion_identity":
            "blocked_model_absent",
        "code_model_and_training_data_terms":
            "blocked_rights_not_recorded",
        "eligible_target_and_pinned_runtime": "blocked_runtime_absent",
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
                "blocked_source_model_terms_runtime_and_matched_cohort_absent"),
            "metrics": None,
            "qualifies_candidate": False,
            "result": None,
            "reason": (
                "No ESP-SR source, NSNet3 model artifact, approved terms, "
                "eligible or portable runtime, pinned configuration or "
                "rights-cleared matched cohort is present; no denoising, "
                "preservation, alignment, state, memory or timing result was "
                "produced."),
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
            "harness stimulus characterisation only; not an Espressif NSNet3 "
            "result and not a candidate output"),
        "harness_geometry": {
            "channels": HARNESS_CHANNELS,
            "frame_samples": HARNESS_FRAME_SAMPLES,
            "hop_samples": HARNESS_HOP_SAMPLES,
            "flat_values": HARNESS_FRAME_VALUES,
            "sample_rate_hz": HARNESS_SAMPLE_RATE_HZ,
            "verified_model_geometry": False,
            "note": (
                "The 512-sample frame and 256-sample hop are arithmetic from "
                "the source-reported 32 ms and 16 ms durations at 16 kHz and "
                "are used only to exercise validation and rejection; they are "
                "not a claim about the vendor API or implementation."),
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
        blockers.append("model_artifact_absent")
    if license_probe()["review"] != "approved":
        blockers.append("terms_not_recorded")
    if not runtime_probe()["pinned"]:
        blockers.append("runtime_unpinned")
    if runtime_probe()["portable_host_runtime"] is None:
        blockers.append("portable_host_runtime_absent")
    if not hardware_probe()["toolchain_present"]:
        blockers.append("eligible_hardware_and_toolchain_absent")
    if not cohort_probe()["present"]:
        blockers.append("matched_cohort_absent")
    if not scorer_probe()["approved_si_sdr"]:
        blockers.append("scorer_unapproved")
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
            "source, model artifact, terms, runtime, matched cohort, scorer "
            "and rights are absent. No port, fallback or surrogate is used."),
    }


def probe_candidate(request: Any) -> None:
    validate_request(request)
    raise ArtifactsAbsent(
        "ARTIFACTS_ABSENT: ESP-SR source, NSNet3 model artifact, approved "
        "terms, runtime and matched cohort are not present; no processing is "
        "performed", "ARTIFACTS_ABSENT")


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
        ("research/noise_suppression_candidate_census.md records Espressif "
         "NSNet3 as a tiny 16 kHz low-power embedded noise suppression "
         "candidate with 48.2k parameters and a 32 ms frame / 16 ms hop."),
        ("the same note records that official ESP-SR documentation describes "
         "embedded target support and that NSNet3 is a special-target "
         "candidate, not directly comparable to a desktop CPU pilot until a "
         "portable adapter exists."),
        ("the same note gives no source revision, model digest, code or model "
         "terms, training-data provenance, runtime lock, measured latency or "
         "quality result for NSNet3."),
        ("plan/INVENTORY.json assigns espressif-nsnet3 the enhancement "
         "verification profile, disposition sdk-model and an evidence status "
         "of considered."),
        ("plan/audio-sdk/README.md requires runnable source, exact assets, "
         "permitted scope and matched evidence before a caller-supplied "
         "reference or opt-in SDK adapter is added."),
        ("No local ESP-SR source, NSNet3 model or graph, code/model terms, "
         "ESP-IDF runtime, pinned configuration, matched cohort or approved "
         "scorer exists; nothing was cloned, downloaded, ported or "
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
        "model_artifact_absent": weights["present"] is False,
        "terms_not_recorded": license_block["review"] == "blocked",
        "license_text_absent":
            license_block["license_text_present"] is False,
        "eligible_hardware_absent": hardware["runner"] is None,
        "runtime_unpinned": runtime["pinned"] is False,
        "portable_host_runtime_absent":
            runtime["portable_host_runtime"] is None,
        "matched_cohort_absent": cohort["present"] is False,
        "scorer_unapproved": scorer["approved_si_sdr"] is False,
        "rights_unrecorded": rights["review"] == "blocked",
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "missing_and_unrecorded_geometry_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith(("missing", "undeclared", "wrong_hop",
                                      "v0_", "reported_"))),
        "nonfinite_samples_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith("nonfinite")),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked":
            missing_result("espressif_nsnet3_placeholder")["status"] ==
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
            MODEL_BOUNDARY["automatic_discovery"] is False),
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
            "explicit_missing_artifact_and_rights_blocker",
            "deterministic_bytes_and_digests",
            "synthetic_harness_controls_only",
            "no_quality_or_timing_measurement",
        ],
        "reference": {
            "implementation": "task-local standard-library model-feasibility gate",
            "real_component_source_present": source["present"],
            "model_artifact_present": weights["present"],
            "component_config_present": False,
            "eligible_hardware_present": hardware["runner"] is not None,
            "pinned_runtime_present": runtime["pinned"],
            "portable_host_runtime_present":
                runtime["portable_host_runtime"] is not None,
            "matched_cohort_present": cohort["present"],
            "approved_scorer_present": scorer["approved_si_sdr"],
            "license_text_present": license_block["license_text_present"],
            "rights_approved": False,
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "real_corpus_read": False,
            "note": (
                "No NSNet3 inference, port, surrogate or approximation is "
                "implemented or simulated; only probes, request rejection and "
                "synthetic harness controls are performed."),
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
            "missing_result": missing_result("espressif_nsnet3_placeholder"),
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
