# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local feasibility/blocker reference for SDK-DPCRN-DNS3-TFLITE.

The task asks whether the exact DPCRN DNS3 / TFLite model and runtime can be
reproduced as a caller-supplied-asset reference.  The pinned research record
locates only a public repository lead (``located_unverified``): no immutable
commit, no ``.tflite`` bytes, no pretrained-checkpoint identity, no byte count,
no SHA-256, no license terms and no pinned interpreter/delegate are available.
Nothing is downloaded, copied, hashed from a live checkout, loaded or executed
here.

Because the exact artifact cannot be admitted, this module does **not** model
the exact DPCRN DNS3 graph.  It supplies two strictly separated things:

1. a deterministic, stdlib-only **surrogate** at a declared DPCRN-family
   complex-STFT boundary (512/256, 257 bins, 16 frequency chunks) that exercises
   only geometry, sample accounting, chunking, finiteness and refusal
   mechanics; and
2. a fail-closed caller-supplied-artifact requirement whose canonical pins are
   deliberately absent, so every request is rejected as
   ``blocked_unpinned_artifact``.

The surrogate is opt-in, unregistered, disabled by default, is not DPCRN, is
not a TFLite inference, and substitutes for no release gate.  A missing result
never qualifies the candidate: decision ``DEFER``, evidence ``incomplete``,
qualification ``not_qualified``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import scorer
from scorer import SCORER_ID, si_sdr, stoi

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2])))
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK_ID = "SDK-DPCRN-DNS3-TFLITE"
TITLE = "DPCRN DNS3 / TFLite"
SLUG = "dpcrn-dns3-tflite"
COMPONENT_ID = "dpcrn-dns3-tflite"
REFERENCE_FAMILY = "dpcrn"
TASK_MODE = "feasibility"
BASE_COMMIT = "7c6653f5a7db7f6de34ad709a96a455a9ad3263a"
BRANCH = "swarm/SDK-DPCRN-DNS3-TFLITE"
TASK_REL = f"docs/task-evidence/{SLUG}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_blocker_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "artifact_admission"
EVIDENCE_INTERPRETER = "3.12.16"
ADAPTER_ID = "dpcrn-dns3-tflite-blocker-surrogate-v1"

UPSTREAM_REPOSITORY = "https://github.com/Le-Xiaohuai-speech/DPCRN_DNS3"
UPSTREAM_RESULTS_REPOSITORY = "https://github.com/Le-Xiaohuai-speech/DPCRN_DNS3_Results"
UPSTREAM_COMMIT: Optional[str] = None
UPSTREAM_LICENSE: Optional[str] = None
UPSTREAM_ARTIFACT_PATH: Optional[str] = None
UPSTREAM_ARTIFACT_SHA256: Optional[str] = None
UPSTREAM_ARTIFACT_BYTES: Optional[int] = None

CENSUS_PATH = "research/noise_suppression_candidate_census.md"
CENSUS_LINE = 20
CENSUS_RECORD_NAME = "DPCRN DNS3 / TFLite"
ACCOUNTING_PATH = (
    "reports/95d98095b79471cf92fdaf736d7296a14811147499fe76ed4076de5c39b8e30d/"
    "candidate_accounting.csv"
)
LOCATOR_STATUS = "located_unverified"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
N_FFT = 512
WINDOW_SAMPLES = 512
HOP_SAMPLES = 256
HOP_MS = 1000.0 * HOP_SAMPLES / SAMPLE_RATE_HZ
STFT_BINS = N_FFT // 2 + 1
PADDING_SAMPLES = N_FFT // 2
FREQUENCY_CHUNKS = 16
CONTENT_DELAY_SAMPLES = 0
CONTENT_DELAY_MS = 0.0
MIN_SAMPLES = 2
MAX_ABS_INPUT = 2.0
CLIPPING_THRESHOLD = 0.98
SIGNAL_SAMPLES = 8192
TAIL_SAMPLES = 8195
SEED_BASE = 20261126

SURROGATE_MODE = "offline_surrogate"
REAL_MODE = "caller_supplied_tflite"
ASSET_REFERENCE = "caller_supplied_dpcrn_dns3_tflite"
CONFIG = {"mode": SURROGATE_MODE, "asset": ASSET_REFERENCE}

SURROGATE_PARAMETERS = {
    "algorithm": "frequency_chunked_spectral_gain_surrogate",
    "frequency_chunks": FREQUENCY_CHUNKS,
    "oversubtraction": 1.25,
    "minimum_gain": 0.08,
    "noise_frame_fraction": 0.15,
    "temporal_smoothing": "centered_three_tap",
    "learned_weights": False,
    "tflite_invoked": False,
}

TASK_ROW_PROJECTION: Dict[str, Any] = {
    "task_id": TASK_ID,
    "component_id": COMPONENT_ID,
    "name": TITLE,
    "repository": "audio-sdk",
    "verification_profile": PROFILE,
    "disposition": "sdk-model",
    "evidence_status": "considered",
    "evidence_path": CENSUS_PATH,
    "evidence_line": CENSUS_LINE,
}
TASK_ROW_PROJECTION_SHA256 = hashlib.sha256(
    json.dumps(TASK_ROW_PROJECTION, sort_keys=True, separators=(",", ":"),
               allow_nan=False).encode("utf-8")).hexdigest()
TASK_BOARD_POLICY = {
    "full_tasks_json_pinned": False,
    "task_board_or_handoff_write": False,
    "linked_record": "audio-benchmark-platform/plan/INVENTORY.json#/components/dpcrn-dns3-tflite",
    "policy": (
        "The mutable full plan/swarm/TASKS.json is never read, hashed or pinned. "
        "Only the stable linked inventory row projection is gated."
    ),
}

MODEL_GEOMETRY = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": "f32",
    "processing_mode": "offline_whole_utterance",
    "n_fft": N_FFT,
    "window_samples": WINDOW_SAMPLES,
    "hop_samples": HOP_SAMPLES,
    "hop_ms": HOP_MS,
    "stft_bins": STFT_BINS,
    "frame_representation": "real_imag",
    "analysis_synthesis_window": "sqrt_periodic_hann_512",
    "stft_centered": True,
    "stft_padding_samples": PADDING_SAMPLES,
    "frame_count_formula": "T=1+floor(N/256)",
    "surrogate_model_input_shape": "[1,257,T,2]",
    "surrogate_model_output_shape": "[1,257,T,2]",
    "surrogate_frequency_chunks": FREQUENCY_CHUNKS,
    "istft_length": "input_sample_count",
    "output_samples": "input_sample_count",
    "source_time_mapping": "identity",
    "content_delay_samples": CONTENT_DELAY_SAMPLES,
    "content_delay_ms": CONTENT_DELAY_MS,
    "streaming_state": "none_offline_whole_utterance",
    "reset_behavior": "not_applicable_offline_stateless",
    "real_time_causal": False,
    "exact_artifact_geometry_verified": False,
    "exact_artifact_stream_delay_samples": None,
    "measured_timing": False,
    "geometry_basis": (
        "Published DPCRN-family complex-STFT convention (16 kHz, 512-point FFT, "
        "256-sample hop, 16 frequency chunks). It is a surrogate parameter set, "
        "not a verified property of the exact upstream or TFLite artifact."
    ),
    "note": (
        "Analytical sample-count geometry only. Offline whole-utterance STFT/ISTFT "
        "is centered and returns an output aligned sample-for-sample with the input. "
        "It is explicitly non-causal and makes no stream, device or deadline claim. "
        "The exact TFLite graph geometry and stream delay remain unresolved."
    ),
}

FORMAT = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "hop_samples": 160,
    "content_delay_samples": 0,
    "processing_mode": "unchanged_installed_v0_reference",
    "installed_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
    "native_model_geometry": "model_geometry",
}

ARTIFACT_REQUIREMENT = {
    "status": "unresolved",
    "locator_status": LOCATOR_STATUS,
    "required_model_artifact": (
        "An immutable .tflite graph for the exact DPCRN DNS3 model, addressed by "
        "repository commit + artifact path + byte count + SHA-256."
    ),
    "required_companion_artifacts": [
        "the exact pretrained checkpoint or conversion source used to produce the .tflite graph",
        "the exact conversion script and quantization parameters, including input/output tensor names",
    ],
    "required_runtime": (
        "A pinned TFLite interpreter version and ABI plus the exact CPU/edge delegate, "
        "with a recorded package or build digest; TensorFlow 1.x legacy paths are not sufficient."
    ),
    "required_rights": (
        "Written artifact-specific code, model-weight, training-data and TFLite-conversion "
        "terms plus a redistribution, product-use and legal decision."
    ),
    "unresolved_fields": [
        "source_revision",
        "artifact_path",
        "artifact_sha256",
        "artifact_byte_count",
        "upstream_license",
        "checkpoint_license",
        "runtime_version",
        "runtime_delegate",
        "training_data_provenance",
        "evaluation_overlap",
    ],
}

EXPECTED_RUNTIME = {
    "id": "tflite-interpreter-unresolved",
    "kind": "pinned TFLite interpreter and delegate",
    "version": None,
    "abi": None,
    "python_binding": None,
    "delegate": None,
    "package_digest": None,
    "installed_in_sdk_worktree": False,
    "tflite_importable_in_evidence_interpreter": False,
    "tensorflow_importable_in_evidence_interpreter": False,
    "legacy_tensorflow_1x_path_verified": False,
}

SOURCE_PINS: Dict[str, str] = {
    "source:research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "source:audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "source:" + ACCOUNTING_PATH:
        "3ab7b404129737666c1e74c7e9a7107f45c8c0575018d2591bef75d3782473c5",
    "source:research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "source:research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
}

BOUNDARY_PINS: Dict[str, str] = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}

GATE_NAMES = (
    "exact_artifact_identity_and_hash_pinned",
    "exact_runtime_and_delegate_pinned",
    "weight_runtime_and_training_data_rights_cleared",
    "real_model_parity_and_alignment",
    "held_out_paired_denoising_cohort",
    "independent_listening_or_predictive_screen",
    "target_runtime_timing_memory_and_deadline",
    "provider_intake_descriptor_and_default_review",
)

GATE_REOPEN = {
    "exact_artifact_identity_and_hash_pinned": (
        "Reopen only when an immutable upstream commit and the exact .tflite graph plus "
        "conversion source/checkpoint are addressed by path, byte count and SHA-256 in a "
        "retrieval record that resolves from caller-owned storage."
    ),
    "exact_runtime_and_delegate_pinned": (
        "Reopen only when the exact TFLite interpreter version/ABI and CPU/edge delegate "
        "are pinned with a package or build digest and can run the graph in an approved "
        "isolated runner; TensorFlow 1.x legacy paths must be separately verified."
    ),
    "weight_runtime_and_training_data_rights_cleared": (
        "Reopen only when written code, model-weight, checkpoint, training-data, conversion "
        "and runtime terms plus a redistribution/product-use legal decision exist; repository "
        "metadata or an absent license is not clearance."
    ),
    "real_model_parity_and_alignment": (
        "Reopen only when the exact model and runtime produce finite, reproducible output on "
        "the frozen inputs and the exact geometry, content delay, state and alignment are "
        "verified against the upstream implementation."
    ),
    "held_out_paired_denoising_cohort": (
        "Reopen only with a predeclared held-out rights-cleared real paired denoising cohort, "
        "matched identity and noisy-input controls, and paired SI-SDR/STOI from an independent scorer."
    ),
    "independent_listening_or_predictive_screen": (
        "Reopen only with authorized independent listening or a separately labeled predictive "
        "screen; synthetic surrogate metrics can never substitute for either."
    ),
    "target_runtime_timing_memory_and_deadline": (
        "Reopen only after measuring content/availability timing, memory, CPU/edge throughput "
        "and deadline behavior for the exact runtime, delegate and workload."
    ),
    "provider_intake_descriptor_and_default_review": (
        "Reopen only after the artifact, runtime, rights and evidence gates clear and an opt-in, "
        "OFF-by-default provider intake with descriptor and explicit default-selection review is approved."
    ),
}

EXACT_BLOCKERS = [
    (
        "No exact DPCRN DNS3 source file, pretrained checkpoint or .tflite graph is present in "
        "this SDK worktree or in the available research checkouts. The pinned census and "
        "candidate-accounting record identify only the public repository lead with status "
        "located_unverified, and record no immutable commit, artifact path, byte count or SHA-256. "
        "Nothing was downloaded, copied, opened, hashed or loaded by this package."
    ),
    (
        "No exact TFLite runtime is pinned. The census describes a smaller uploaded TFLite model "
        "with single-file and streaming inference and calls the TensorFlow 1.x real-time path "
        "legacy, but no interpreter version, ABI, delegate, package digest or conversion recipe is "
        "recorded. tensorflow, tflite_runtime and ai_edge_litert are not importable in the pinned "
        "CPython 3.12.16 evidence interpreter."
    ),
    (
        "Weight licensing was not found. The census explicitly records that exact checkpoint hash "
        "and weight licensing were not found; the asset ledger contains no DPCRN DNS3 artifact "
        "entry and the candidate accounting marks pin/hash and checkpoint licensing as unresolved. "
        "No artifact-specific terms, DNS3 training-data provenance or evaluation-overlap assessment, "
        "redistribution/product-use clearance or legal decision exists."
    ),
    (
        "No qualification evidence exists: there is no real-model parity run, rights-cleared "
        "held-out paired real cohort, independent clean-reference scorer, permitted listening "
        "result, target-runtime timing/memory/deadline measurement, benchmark or release result. "
        "The synthetic surrogate cannot satisfy any of these gates."
    ),
]

MISSING_EVIDENCE = [
    "immutable upstream repository revision",
    "exact .tflite artifact path, byte count and SHA-256",
    "exact pretrained checkpoint or conversion source plus conversion script and quantization parameters",
    "pinned TFLite interpreter version/ABI and CPU/edge delegate with package digest",
    "artifact-specific code, weight, training-data and runtime terms plus a legal decision",
    "real-model parity and exact geometry/content-delay/state verification",
    "rights-cleared held-out paired real denoising cohort with clean references",
    "independent SI-SDR/STOI scorer and permitted listening or a separately labeled predictive screen",
    "target-runtime timing, memory, throughput, availability and deadline evidence",
    "benchmark and release adjudication",
]

SURROGATE_LIMITATIONS = [
    "The surrogate is a pure-Python frequency-chunked spectral-gain fixture, not DPCRN and not a TFLite graph.",
    "It has no convolutions, recurrent state, dual-path RNN, learned weights or quantized kernels.",
    "Synthetic harmonic signals are not speech, not DNS3 and not a listening proxy.",
    "The declared 512/256 and 16-chunk geometry is a DPCRN-family convention, not verified against the exact artifact.",
    "No TFLite interpreter, delegate, real stream delay, state transition, device clock or memory result is produced.",
]

NEGATIVE_CLAIMS = {
    "real_model_executed": False,
    "weights_accessed": False,
    "artifact_downloaded": False,
    "artifact_copied_or_vendored": False,
    "real_audio_read": False,
    "real_media_read": False,
    "listening_result_produced": False,
    "device_timing_measured": False,
    "content_latency_measured": False,
    "benchmark_result": False,
    "quality_claim": False,
    "release_claim": False,
    "provider_registered": False,
    "processor_exposed": False,
    "public_default_selected": False,
    "tflite_runtime_invoked": False,
    "tensorflow_runtime_invoked": False,
    "gpu_or_npu_delegate_invoked": False,
}

SCOPE = {
    "selection_made": False,
    "implementation_completed": False,
    "provider_added": False,
    "public_api_abi_changed": False,
    "installed_v0_behavior_changed": False,
    "shared_build_or_ci_changed": False,
    "board_or_handoff_written": False,
    "release_qualified": False,
    "benchmark_published": False,
}

BOUNDARY = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "installed_v0_behavior_change": False,
    "installed_v0_geometry_preserved": True,
    "shared_cmakelists_change": False,
    "shared_build_or_ci_change": False,
    "ci_change": False,
    "processor_exposure": False,
    "realtime_streaming_exposed": False,
    "task_board_or_handoff_write": False,
}

LICENSING_ANALYSIS = {
    "upstream_code_license": None,
    "upstream_code_license_pin": None,
    "checkpoint_specific_terms_recorded": False,
    "checkpoint_license_text_present_in_ledger": False,
    "tflite_conversion_terms_recorded": False,
    "training_data_provenance_established": False,
    "training_eval_overlap_assessed": False,
    "runtime_redistribution_terms_established": False,
    "redistribution_clearance": False,
    "product_use_clearance": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "weight_runtime_and_training_data_rights_cleared",
}

RIGHTS_GAP = {
    "blocked": True,
    "exact_upstream_source_verified": False,
    "model_weight_terms_verified": False,
    "training_data_provenance_verified": False,
    "tflite_redistribution_terms_verified": False,
    "evidence": (
        "The census records that exact checkpoint hash and weight licensing were not found; "
        "the asset ledger has no DPCRN DNS3 entry and the candidate accounting marks pin/hash "
        "and checkpoint licensing as unresolved. No code, weight, conversion or runtime terms "
        "are established here."
    ),
    "consequence": (
        "No vendoring, build, installed provider, descriptor, default, benchmark or release "
        "claim until artifact identity and code/weight/training-data/runtime rights are cleared."
    ),
}

EVIDENCE_CLASSES = [
    "synthetic_paired_metrics",
    "analytical_geometry_and_alignment",
    "pinned_source_inventory_and_census",
    "deterministic_bytes_and_digests",
    "explicit_missing_artifact_blocker",
]

LOCATOR_EVIDENCE = {
    "census": {
        "path": CENSUS_PATH,
        "line": CENSUS_LINE,
        "record_name": CENSUS_RECORD_NAME,
        "evidence_status": "considered",
        "finding": (
            "Dual-path convolutional recurrent network; real-time and quantized edge reference"
        ),
        "detail": (
            "Author repository identifies official DNS3 implementation, third-place DNS3 "
            "result, pretrained-model directory, and a smaller uploaded TFLite model with "
            "single-file and streaming inference."
        ),
        "gaps": (
            "Medium priority; compare TFLite on CPU/edge. TensorFlow 1.x real-time path is "
            "legacy; exact checkpoint hash and weight licensing were not found."
        ),
    },
    "candidate_accounting": {
        "path": ACCOUNTING_PATH,
        "candidate": "candidate-dpcrn-dns3",
        "status": "blocked",
        "locator": LOCATOR_STATUS,
        "note": (
            "official implementation describes pretrained-model directory and smaller TFLite "
            "model; pin/hash, checkpoint licensing, TensorFlow 1.x compatibility and runtime "
            "remain to verify"
        ),
    },
    "inventory": {
        "path": "audio-benchmark-platform/plan/INVENTORY.json",
        "component_id": COMPONENT_ID,
        "disposition": "sdk-model",
        "evidence_status": "considered",
    },
    "upstream_repository": UPSTREAM_REPOSITORY,
    "upstream_results_repository": UPSTREAM_RESULTS_REPOSITORY,
    "upstream_commit": UPSTREAM_COMMIT,
    "upstream_license": UPSTREAM_LICENSE,
}

RELATED_MODELS_NOT_POOLED = {
    "status": "different_artifacts_not_evidence",
    "note": (
        "The merged PureSound DPCRN-Mamba v1/v2/v3 packages are separate upstream models that "
        "share only the DPCRN name. Their measured DNS pilot metrics and streaming delays are "
        "not transferable to DPCRN DNS3 / TFLite and are not used, pooled or cited as a result here."
    ),
    "models": [
        "puresound-dpcrn-mamba-v1",
        "puresound-dpcrn-mamba-v2",
        "puresound-dpcrn-mamba-v3",
    ],
    "metrics_used_for_qualification": False,
}

PRIOR_PILOT_PROVENANCE = {
    "status": "not_available",
    "measured_here": False,
    "used_for_qualification": False,
    "source": "research/noise_suppression_pilot_20261027.md",
    "cohort": None,
    "reported": {},
    "note": (
        "The pinned DNS pilot contains no DPCRN DNS3 / TFLite row. No prior quality, throughput "
        "or timing value exists for this candidate and none is invented here."
    ),
}

INDEPENDENT_TIMING_EVIDENCE = {
    "status": "not_available",
    "measured_here": False,
    "target_device": False,
    "used_for_qualification": False,
    "sources": [CENSUS_PATH, ACCOUNTING_PATH],
    "reported": {},
    "note": (
        "No source-reported DPCRN DNS3 / TFLite latency, memory or RTF value exists in the "
        "pinned evidence, and no device clock or workload was measured here."
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Mapping[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def _reject_duplicate(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json_constant:" + token)


def strict_loads(text: str) -> Any:
    return json.loads(text, object_pairs_hook=_reject_duplicate,
                      parse_constant=_reject_constant)


def strict_json(path: Path) -> Any:
    return strict_loads(path.read_text(encoding="utf-8"))


PIN_RE = re.compile(
    r"^[0-9a-f]{64}  (?P<path>source:[^\s]+|docs/[^\s]+|api/[^\s]+|CONTRACTS\.md)$")
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_TEXT = f"{SPDX_COPYRIGHT_LINE}\n{SPDX_LICENSE_LINE}\n"


def pin_path(raw: str) -> Path:
    if raw.startswith("source:"):
        return SOURCE_ROOT / raw.split(":", 1)[1]
    return SDK_ROOT / raw


NEGATIVE_ZERO_RE = re.compile(rb"(?<![0-9.])-0\.0(?![0-9])")


def contains_negative_zero(payload: bytes) -> bool:
    """True only for a JSON negative-zero token, not for ordinary negative values."""
    return NEGATIVE_ZERO_RE.search(payload) is not None


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Fail closed on malformed, duplicated or out-of-scope manifest entries."""
    pins: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        match = PIN_RE.fullmatch(line)
        if match is None:
            raise ValueError("malformed_pin_line:" + repr(line))
        raw_path = match.group("path")
        if ".." in Path(raw_path.split(":", 1)[-1]).parts:
            raise ValueError("path_traversal_pin:" + raw_path)
        if raw_path.startswith("source:") or raw_path in BOUNDARY_PINS:
            pass
        elif raw_path.startswith(TASK_REL + "/"):
            name = raw_path[len(TASK_REL) + 1:]
            if "/" in name or not (HERE / name).is_file():
                raise ValueError("out_of_scope_pin:" + raw_path)
        else:
            raise ValueError("out_of_scope_pin:" + raw_path)
        if raw_path in seen:
            raise ValueError("duplicate_pin:" + raw_path)
        seen.add(raw_path)
        pins.append((line[:64], raw_path))
    return pins


def rng(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def _seed(condition: str) -> int:
    return SEED_BASE + sum(ord(char) for char in condition)


def synth(condition: str) -> Tuple[List[float], List[float]]:
    """Return frozen synthetic dry target and observed input for one condition."""
    length = TAIL_SAMPLES if condition == "tail_partial" else SIGNAL_SAMPLES
    random = rng(_seed(condition))
    base_f0 = 196.0 if condition == "unfamiliar_speech" else 118.0
    envelope_period = 3121.0 if condition == "unfamiliar_speech" else 2437.0
    clean: List[float] = []
    for index in range(length):
        envelope = 0.62 + 0.24 * math.sin(2.0 * math.pi * index / envelope_period)
        glide = 1.0 + 0.03 * math.sin(2.0 * math.pi * index / 7919.0)
        tone = 0.0
        for harmonic in range(1, 8):
            tone += (0.16 / harmonic) * math.sin(
                2.0 * math.pi * base_f0 * harmonic * glide * index / SAMPLE_RATE_HZ)
        sibilant = 0.05 * math.sin(2.0 * math.pi * 3600.0 * index / SAMPLE_RATE_HZ)
        clean.append((tone + sibilant) * envelope)
    if condition == "silence":
        return [0.0] * length, [0.0] * length
    if condition == "clipped":
        observed = [1.8 * value + (next(random) - 0.5) * 2.0 * 0.12 for value in clean]
        return clean, observed
    if condition == "clean_speech":
        observed = [value + (next(random) - 0.5) * 2.0 * 0.006 for value in clean]
        return clean, observed
    if condition == "nonstationary_noise":
        observed = []
        for index, value in enumerate(clean):
            scale = 0.16
            if 2800 <= index < 4096 or 6200 <= index < 7100:
                scale = 0.58
            observed.append(value + (next(random) - 0.5) * 2.0 * scale)
        return clean, observed
    observed = [value + (next(random) - 0.5) * 2.0 * 0.16 for value in clean]
    return clean, observed


def analysis_window() -> List[float]:
    """sqrt of the periodic Hann window of length 512, exactly sin(pi*n/512)."""
    return [math.sin(math.pi * index / WINDOW_SAMPLES) for index in range(WINDOW_SAMPLES)]


WINDOW = analysis_window()


def _fft(values: List[complex]) -> List[complex]:
    return scorer._fft(values)


def _ifft(values: List[complex]) -> List[complex]:
    return scorer._fft(values, inverse=True)


def frame_count(samples: int) -> int:
    return 1 + samples // HOP_SAMPLES


def _padded(samples: Sequence[float]) -> List[float]:
    return [0.0] * PADDING_SAMPLES + list(samples) + [0.0] * PADDING_SAMPLES


def stft(samples: Sequence[float]) -> List[List[complex]]:
    padded = _padded(samples)
    frames: List[List[complex]] = []
    for index in range(frame_count(len(samples))):
        start = index * HOP_SAMPLES
        frame = [complex(padded[start + offset] * WINDOW[offset], 0.0)
                 for offset in range(WINDOW_SAMPLES)]
        frames.append(_fft(frame)[:STFT_BINS])
    return frames


def _full_spectrum(bins: Sequence[complex]) -> List[complex]:
    full = list(bins)
    for index in range(STFT_BINS, WINDOW_SAMPLES):
        full.append(full[WINDOW_SAMPLES - index].conjugate())
    return full


def istft(frames: Sequence[Sequence[complex]], samples: int) -> List[float]:
    total = samples + 2 * PADDING_SAMPLES
    overlap = [0.0] * total
    norm = [0.0] * total
    for index, bins in enumerate(frames):
        time_frame = _ifft(_full_spectrum(bins))
        start = index * HOP_SAMPLES
        for offset in range(WINDOW_SAMPLES):
            overlap[start + offset] += time_frame[offset].real * WINDOW[offset]
            norm[start + offset] += WINDOW[offset] * WINDOW[offset]
    output: List[float] = []
    for index in range(samples):
        position = index + PADDING_SAMPLES
        output.append(overlap[position] / max(norm[position], 1e-12))
    return output


def chunk_bounds() -> List[Tuple[int, int]]:
    """Contiguous dual-path frequency chunks over all 257 real/imag bins."""
    return [(index * STFT_BINS // FREQUENCY_CHUNKS,
             (index + 1) * STFT_BINS // FREQUENCY_CHUNKS)
            for index in range(FREQUENCY_CHUNKS)]


def _noise_magnitude(magnitudes: Sequence[Sequence[float]]) -> List[float]:
    count = len(magnitudes)
    energies = [math.fsum(value * value for value in frame) for frame in magnitudes]
    take = max(2, int(count * SURROGATE_PARAMETERS["noise_frame_fraction"]))
    order = sorted(range(count), key=lambda item: (energies[item], item))[:take]
    return [math.fsum(magnitudes[item][band] for item in order) / take
            for band in range(STFT_BINS)]


def _smooth_time(gains: Sequence[Sequence[float]]) -> List[List[float]]:
    """Centered three-tap smoothing over time, deterministic at both edges."""
    smoothed: List[List[float]] = []
    count = len(gains)
    for index in range(count):
        previous = gains[index - 1] if index > 0 else gains[index]
        following = gains[index + 1] if index + 1 < count else gains[index]
        smoothed.append([(previous[band] + 2.0 * gains[index][band] + following[band]) / 4.0
                         for band in range(STFT_BINS)])
    return smoothed


def enhance_spectrum(frames: Sequence[Sequence[complex]]
                     ) -> Tuple[List[List[complex]], Dict[str, Any]]:
    """Chunk-wise spectral gain: a dual-path-shaped surrogate, not a network."""
    magnitudes = [[abs(value) for value in frame] for frame in frames]
    noise = _noise_magnitude(magnitudes)
    bounds = chunk_bounds()
    raw_gains: List[List[float]] = []
    for frame in magnitudes:
        row: List[float] = [0.0] * STFT_BINS
        for low, high in bounds:
            width = high - low
            signal_mean = math.fsum(frame[low:high]) / width
            noise_mean = math.fsum(noise[low:high]) / width
            if signal_mean <= 1e-12:
                gain = 0.0
            else:
                ratio = noise_mean / signal_mean
                gain = math.sqrt(max(0.0, 1.0
                                     - SURROGATE_PARAMETERS["oversubtraction"] * ratio * ratio))
                gain = min(1.0, max(SURROGATE_PARAMETERS["minimum_gain"], gain))
            for band in range(low, high):
                row[band] = gain
        raw_gains.append(row)
    gains = _smooth_time(raw_gains)
    shaped = [[frame[band] * gains[index][band] for band in range(STFT_BINS)]
              for index, frame in enumerate(frames)]
    return shaped, {
        "frames": len(frames),
        "stft_bins": STFT_BINS,
        "frequency_chunks": FREQUENCY_CHUNKS,
        "chunk_bounds": [[low, high] for low, high in bounds],
        "noise_frames_used": max(2, int(len(frames)
                                        * SURROGATE_PARAMETERS["noise_frame_fraction"])),
        "minimum_gain": SURROGATE_PARAMETERS["minimum_gain"],
        "mean_gain": round(math.fsum(math.fsum(row) for row in gains)
                           / (len(frames) * STFT_BINS), 9),
    }


def identity_spectrum(frames: Sequence[Sequence[complex]]) -> List[List[complex]]:
    return [list(frame) for frame in frames]


def _transform(samples: Sequence[float], enhance: bool
               ) -> Tuple[List[float], Dict[str, Any]]:
    frames = stft(samples)
    if enhance:
        shaped, info = enhance_spectrum(frames)
    else:
        shaped, info = identity_spectrum(frames), {"frames": len(frames)}
    output = istft(shaped, len(samples))
    info = dict(info)
    info.update({"input_samples": len(samples), "output_samples": len(output),
                 "padded_samples": 2 * PADDING_SAMPLES})
    return output, info


def validate_config(config: Any) -> Tuple[Optional[Dict[str, Any]], str]:
    if not isinstance(config, dict):
        return None, "rejected_invalid"
    keys = set(config)
    if keys != {"mode", "asset"}:
        return None, "rejected_missing" if keys < {"mode", "asset"} else "rejected_invalid"
    mode = config["mode"]
    asset = config["asset"]
    if isinstance(mode, float) and not math.isfinite(mode):
        return None, "rejected_nonfinite"
    if not isinstance(mode, str) or not isinstance(asset, str):
        return None, "rejected_invalid"
    if not asset or ".." in Path(asset).parts or Path(asset).is_absolute():
        return None, "rejected_invalid"
    if mode == REAL_MODE:
        return None, "rejected_unpinned_artifact"
    if mode != SURROGATE_MODE or asset != ASSET_REFERENCE:
        return None, "rejected_invalid"
    return {"mode": mode, "asset": asset}, "created"


def _validate_signal(waveform: Any) -> Tuple[Optional[List[float]], str]:
    if not isinstance(waveform, (list, tuple)):
        return None, "rejected_invalid"
    if len(waveform) < MIN_SAMPLES:
        return None, "rejected_duration"
    if any(isinstance(value, bool) for value in waveform):
        return None, "rejected_invalid"
    values: List[float] = []
    for value in waveform:
        if not isinstance(value, (int, float)):
            return None, "rejected_invalid"
        number = float(value)
        if not math.isfinite(number):
            return None, "rejected_nonfinite"
        if abs(number) > MAX_ABS_INPUT:
            return None, "rejected_invalid"
        values.append(number)
    return values, "ok"


def run_offline(waveform: Any, config: Any = None
                ) -> Tuple[Optional[List[float]], Dict[str, Any]]:
    """Strict offline admission; the real path fails closed without pins."""
    config = dict(CONFIG) if config is None else config
    admitted, status = validate_config(config)
    if admitted is None:
        return None, {"status": status, "mode": None, "samples": None,
                      "rejections": 1, "inference_executed": False,
                      "model_loaded": False, "runtime_invoked": False,
                      "asset_opened": False}
    values, signal_status = _validate_signal(waveform)
    if values is None:
        return None, {"status": signal_status, "mode": admitted["mode"],
                      "samples": None, "rejections": 1,
                      "inference_executed": False, "model_loaded": False,
                      "runtime_invoked": False, "asset_opened": False}
    output, info = _transform(values, enhance=True)
    return output, {
        "status": "ok",
        "mode": admitted["mode"],
        "samples": len(output),
        "rejections": 0,
        "frames": info["frames"],
        "frequency_chunks": FREQUENCY_CHUNKS,
        "stft_padding_samples": PADDING_SAMPLES,
        "delay_compensation_samples": CONTENT_DELAY_SAMPLES,
        "source_time_mapping": "identity",
        "model_input_shape": [1, STFT_BINS, info["frames"], 2],
        "exact_artifact_geometry_verified": False,
        "inference_executed": False,
        "model_loaded": False,
        "runtime_invoked": False,
        "asset_opened": False,
    }


def scored(target: Sequence[float], actual: Optional[Sequence[float]]) -> Dict[str, Any]:
    if actual is None:
        return {"status": "rejected", "si_sdr_db": None, "stoi": None,
                "reason": "invalid_input_rejected", "peak_abs_output": None,
                "nonfinite_count": None, "clipping_count": None}
    si_value, si_reason = si_sdr(target, actual)
    stoi_value, stoi_reason = stoi(target, actual, SAMPLE_RATE_HZ)
    measured = si_value is not None and stoi_value is not None
    return {
        "status": "measured_synthetic" if measured else "excluded",
        "si_sdr_db": round(si_value, 6) if si_value is not None
        and math.isfinite(si_value) else None,
        "stoi": round(stoi_value, 6) if stoi_value is not None
        and math.isfinite(stoi_value) else None,
        "peak_abs_output": round(max(abs(value) for value in actual), 9),
        "nonfinite_count": sum(1 for value in actual if not math.isfinite(value)),
        "clipping_count": sum(1 for value in actual
                              if abs(value) >= CLIPPING_THRESHOLD),
        "si_sdr_reason": si_reason,
        "stoi_reason": stoi_reason,
    }


CONDITIONS = (
    "speech",
    "unfamiliar_speech",
    "nonstationary_noise",
    "clean_speech",
    "clipped",
    "tail_partial",
    "silence",
)


def conditions() -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for condition in CONDITIONS:
        target, observed = synth(condition)
        baseline = scored(target, observed)
        candidate, run = run_offline(observed)
        candidate_metrics = scored(target, candidate)
        measured = (condition != "silence" and candidate is not None
                    and candidate_metrics["status"] == "measured_synthetic")
        result[condition] = {
            "status": "measured_synthetic" if measured else "excluded_no_reference",
            "samples": len(observed),
            "seed": _seed(condition),
            "baseline_metrics": baseline,
            "candidate_metrics": candidate_metrics,
            "candidate_worse_than_baseline_si_sdr": (
                candidate is not None
                and baseline["si_sdr_db"] is not None
                and candidate_metrics["si_sdr_db"] is not None
                and candidate_metrics["si_sdr_db"] < baseline["si_sdr_db"]),
            "offline_run": run,
            "alignment": {
                "mode": "offline_whole_utterance",
                "source_time_mapping": "identity",
                "delay_compensation_samples": CONTENT_DELAY_SAMPLES,
                "exact_artifact_delay_samples": None,
                "measured_timing": False,
            },
        }
    return result


def controls() -> Dict[str, Any]:
    identity_target, identity_input = synth("speech")
    speech_target, speech_input = synth("speech")
    speech_output, _ = run_offline(speech_input)
    clean_target, clean_input = synth("clean_speech")
    clean_output, _ = run_offline(clean_input)
    return {
        "identity": {
            "name": "identity_no_processing",
            "status": "measured_synthetic",
            "metrics": scored(identity_target, identity_input),
            "note": "Identity is the observed input; its gain is zero by construction.",
        },
        "named_baseline": {
            "name": "noisy_input_no_processing",
            "status": "measured_synthetic",
            "metrics": scored(speech_target, speech_input),
            "note": "Task-matched baseline is plain noisy input, not a DPCRN DNS3 run.",
        },
        "candidate": {
            "name": "frequency_chunked_spectral_gain_surrogate",
            "status": "measured_synthetic",
            "metrics": scored(speech_target, speech_output),
            "note": "Synthetic surrogate only; not DPCRN, not TFLite and not a model inference.",
        },
        "clean_speech_preservation": {
            "clean_reference": "clean_speech synthetic dry target",
            "status": "measured_synthetic",
            "metrics": scored(clean_target, clean_output),
            "baseline_metrics": scored(clean_target, clean_input),
            "note": "Synthetic clean-preservation diagnostic; not real clean speech.",
        },
        "all_present": True,
        "excluded_from_qualification": True,
    }


def identity_reconstruction() -> Dict[str, Any]:
    """Analytical check that unit gains reconstruct the input through centered WOLA."""
    probe = [math.sin(2.0 * math.pi * 173.0 * index / SAMPLE_RATE_HZ)
             for index in range(2048)]
    output, info = _transform(probe, enhance=False)
    error = max(abs(left - right) for left, right in zip(probe, output))
    return {
        "probe_samples": len(probe),
        "frames": frame_count(len(probe)),
        "method": "unit_gain_offline_stft_istft_sqrt_hann_512_hop_256",
        "max_abs_error": round(error, 15),
        "reconstruction_exact": error <= 1e-12,
        "output_length_matches": len(output) == len(probe),
        "padding_samples": info["padded_samples"],
    }


def _invalid_configs() -> List[Tuple[str, Any]]:
    return [
        ("not_a_dict", ["offline_surrogate", "caller_supplied_dpcrn_dns3_tflite"]),
        ("missing_key", {"mode": SURROGATE_MODE}),
        ("extra_key", {"mode": SURROGATE_MODE, "asset": ASSET_REFERENCE, "x": 1}),
        ("real_mode_without_pins", {"mode": REAL_MODE, "asset": ASSET_REFERENCE}),
        ("unknown_mode", {"mode": "streaming_surrogate", "asset": ASSET_REFERENCE}),
        ("unknown_asset", {"mode": SURROGATE_MODE, "asset": "other"}),
        ("absolute_asset", {"mode": SURROGATE_MODE, "asset": "/tmp/asset"}),
        ("traversal_asset", {"mode": SURROGATE_MODE, "asset": "../asset"}),
        ("nonfinite_mode", {"mode": float("inf"), "asset": ASSET_REFERENCE}),
        ("bool_mode", {"mode": True, "asset": ASSET_REFERENCE}),
    ]


def _invalid_signals() -> List[Tuple[str, Any]]:
    return [
        ("not_a_sequence", "not-a-waveform"),
        ("empty", []),
        ("one_sample", [0.0]),
        ("nonfinite", [0.0, float("nan"), 0.0]),
        ("bool_sample", [0.0, True, 0.0]),
        ("string_sample", [0.0, "x", 0.0]),
        ("oversized", [0.0, 2.5, 0.0]),
    ]


def _asset_request(**overrides: Any) -> Dict[str, Any]:
    request: Dict[str, Any] = {
        "source_repository": UPSTREAM_REPOSITORY,
        "source_commit": "0" * 40,
        "sample_rate": SAMPLE_RATE_HZ,
        "n_fft": N_FFT,
        "hop_samples": HOP_SAMPLES,
        "runtime": EXPECTED_RUNTIME["id"],
        "files": [{"path": "dpcrn_dns3.tflite", "bytes": 1,
                   "sha256": "0" * 64}],
    }
    request.update(overrides)
    return request


def validate_asset_request(request: Any, *, asset_present: bool,
                           runtime_available: bool,
                           runtime_id: str = EXPECTED_RUNTIME["id"]) -> Dict[str, Any]:
    """Fail-closed caller-artifact gate.

    The canonical upstream commit, artifact path, byte count, SHA-256 and license
    are deliberately unresolved, so even a syntactically perfect and physically
    present request cannot be admitted.  The gate never opens, hashes, loads or
    executes an asset.
    """
    def blocked(reason: str, codes: Optional[List[str]] = None) -> Dict[str, Any]:
        return {
            "status": "blocked",
            "reason": reason,
            "reason_codes": codes if codes is not None else list(
                ARTIFACT_REQUIREMENT["unresolved_fields"]),
            "inference_executed": False,
            "artifact_opened": False,
            "download_attempted": False,
        }

    if not isinstance(request, dict) or set(request) != {
            "source_repository", "source_commit", "sample_rate", "n_fft",
            "hop_samples", "runtime", "files"}:
        return blocked("blocked_invalid_request")
    if request["source_repository"] != UPSTREAM_REPOSITORY:
        return blocked("blocked_wrong_repository")
    if (request["sample_rate"] != SAMPLE_RATE_HZ or request["n_fft"] != N_FFT
            or request["hop_samples"] != HOP_SAMPLES):
        return blocked("blocked_wrong_geometry")
    if request["runtime"] != runtime_id:
        return blocked("blocked_runtime_unavailable")
    files = request["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= 16:
        return blocked("blocked_invalid_request")
    declared: set[str] = set()
    for item in files:
        if (not isinstance(item, dict) or set(item) != {"path", "bytes", "sha256"}
                or not isinstance(item["path"], str) or not item["path"]):
            return blocked("blocked_invalid_request")
        path = Path(item["path"])
        if path.is_absolute() or ".." in path.parts:
            return blocked("blocked_invalid_request")
        if item["path"] in declared:
            return blocked("blocked_duplicate_file")
        declared.add(item["path"])
        if (not isinstance(item["bytes"], int) or isinstance(item["bytes"], bool)
                or item["bytes"] <= 0):
            return blocked("blocked_invalid_request")
        if (not isinstance(item["sha256"], str)
                or re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is None):
            return blocked("blocked_invalid_request")
    if not asset_present:
        return blocked("blocked_asset_absent",
                       ["artifact_bytes_not_caller_supplied"])
    if not runtime_available:
        return blocked("blocked_runtime_unavailable",
                       ["runtime_absent", "runtime_version_unresolved",
                        "runtime_delegate_unresolved"])
    if UPSTREAM_COMMIT is None or UPSTREAM_ARTIFACT_SHA256 is None:
        return blocked("blocked_unpinned_artifact")
    return blocked("blocked_unpinned_artifact")


def asset_gate() -> Dict[str, Any]:
    return {
        "status": "blocked",
        "mode": "caller_supplied_artifact_reference",
        "expected_root": "caller_supplied/DPCRN_DNS3_TFLITE",
        "expected_files": [],
        "admitted_artifact_descriptor_exists": False,
        "pinned_source_commit": UPSTREAM_COMMIT,
        "pinned_artifact_path": UPSTREAM_ARTIFACT_PATH,
        "pinned_artifact_bytes": UPSTREAM_ARTIFACT_BYTES,
        "pinned_artifact_sha256": UPSTREAM_ARTIFACT_SHA256,
        "pinned_license": UPSTREAM_LICENSE,
        "asset_present_in_sdk_worktree": False,
        "asset_present_in_research_checkout": False,
        "asset_loaded_or_hashed_by_package": False,
        "runtime": dict(EXPECTED_RUNTIME),
        "runtime_available": False,
        "tflite_invoked": False,
        "tensorflow_invoked": False,
        "inference_executed": False,
        "real_path_status": "rejected_unpinned_artifact",
        "validation_asset_absent": validate_asset_request(
            _asset_request(), asset_present=False, runtime_available=False),
        "validation_runtime_unavailable": validate_asset_request(
            _asset_request(), asset_present=True, runtime_available=False),
        "validation_fabricated_pins": validate_asset_request(
            _asset_request(), asset_present=True, runtime_available=True),
        "positive_control": None,
        "positive_control_status": "unavailable_no_canonical_pins",
        "silent_fallback_to_surrogate": False,
        "note": (
            "No exact artifact descriptor, license or runtime exists, so there is no passing "
            "control. A fabricated but well-formed request is still rejected as "
            "blocked_unpinned_artifact; the real path never falls back to the surrogate."
        ),
    }


def adverse() -> Dict[str, Any]:
    valid_input, _ = synth("speech")
    config_rejections: Dict[str, Any] = {}
    for name, config in _invalid_configs():
        output, run = run_offline(valid_input, config)
        config_rejections[name] = {
            "status": run["status"],
            "output_created": output is not None,
            "inference_executed": run["inference_executed"],
        }
    signal_rejections: Dict[str, Any] = {}
    for name, signal in _invalid_signals():
        output, run = run_offline(signal)
        signal_rejections[name] = {
            "status": run["status"],
            "output_created": output is not None,
            "inference_executed": run["inference_executed"],
        }
    valid_output, valid_run = run_offline(valid_input)
    gate_cases = {
        "absent": validate_asset_request(
            _asset_request(), asset_present=False, runtime_available=False),
        "malformed_not_dict": validate_asset_request(
            "request", asset_present=True, runtime_available=True),
        "missing_key": validate_asset_request(
            {"source_repository": UPSTREAM_REPOSITORY},
            asset_present=True, runtime_available=True),
        "wrong_repository": validate_asset_request(
            _asset_request(source_repository="https://example.invalid/model"),
            asset_present=True, runtime_available=True),
        "wrong_geometry": validate_asset_request(
            _asset_request(hop_samples=128), asset_present=True, runtime_available=True),
        "wrong_runtime": validate_asset_request(
            _asset_request(runtime="tflite-runtime-2.14.0"),
            asset_present=True, runtime_available=True),
        "missing_files": validate_asset_request(
            _asset_request(files=[]), asset_present=True, runtime_available=True),
        "bad_hash_format": validate_asset_request(
            _asset_request(files=[{"path": "m.tflite", "bytes": 1, "sha256": "Z" * 64}]),
            asset_present=True, runtime_available=True),
        "bad_size": validate_asset_request(
            _asset_request(files=[{"path": "m.tflite", "bytes": 0, "sha256": "0" * 64}]),
            asset_present=True, runtime_available=True),
        "duplicate_file": validate_asset_request(
            _asset_request(files=[
                {"path": "m.tflite", "bytes": 1, "sha256": "0" * 64},
                {"path": "m.tflite", "bytes": 2, "sha256": "1" * 64}]),
            asset_present=True, runtime_available=True),
        "path_traversal": validate_asset_request(
            _asset_request(files=[{"path": "../m.tflite", "bytes": 1, "sha256": "0" * 64}]),
            asset_present=True, runtime_available=True),
        "runtime_unavailable": validate_asset_request(
            _asset_request(), asset_present=True, runtime_available=False),
        "fabricated_pins": validate_asset_request(
            _asset_request(), asset_present=True, runtime_available=True),
    }
    all_rejected = (
        all(item["status"].startswith("rejected")
            for item in config_rejections.values())
        and config_rejections["real_mode_without_pins"]["status"]
            == "rejected_unpinned_artifact"
        and all(item["status"].startswith("rejected")
                for item in signal_rejections.values())
        and all(item["status"] == "blocked" for item in gate_cases.values())
        and valid_run["status"] == "ok")
    return {
        "config_rejections": config_rejections,
        "signal_rejections": signal_rejections,
        "lifecycle": {
            "valid_run": valid_run["status"],
            "real_mode": config_rejections["real_mode_without_pins"]["status"],
        },
        "asset_gate": gate_cases,
        "asset_gate_control": None,
        "asset_gate_control_status": "unavailable_no_canonical_pins",
        "valid_signal": {"status": valid_run["status"],
                         "samples": valid_run["samples"],
                         "delay_compensation_samples": CONTENT_DELAY_SAMPLES},
        "all_rejected": all_rejected,
        "all_outputs_finite": all(
            math.isfinite(value) for value in (valid_output or [])),
    }


def model_provenance() -> Dict[str, Any]:
    return {
        "upstream_repository": UPSTREAM_REPOSITORY,
        "upstream_results_repository": UPSTREAM_RESULTS_REPOSITORY,
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_license": UPSTREAM_LICENSE,
        "upstream_license_pin": None,
        "locator_status": LOCATOR_STATUS,
        "artifact": {
            "path": UPSTREAM_ARTIFACT_PATH,
            "bytes": UPSTREAM_ARTIFACT_BYTES,
            "sha256": UPSTREAM_ARTIFACT_SHA256,
            "present_in_sdk_worktree": False,
            "present_in_research_checkout": False,
            "loaded_or_executed": False,
            "license_terms": None,
            "quantization_parameters_verified": False,
        },
        "checkpoint": {
            "path": None,
            "bytes": None,
            "sha256": None,
            "present_in_sdk_worktree": False,
            "present_in_research_checkout": False,
            "loaded_or_executed": False,
            "license_terms": None,
        },
        "runtime": dict(EXPECTED_RUNTIME),
        "census_provenance": dict(LOCATOR_EVIDENCE["census"]),
        "candidate_accounting": dict(LOCATOR_EVIDENCE["candidate_accounting"]),
        "note": (
            "The public repository lead is recorded by the pinned census and candidate "
            "accounting only. No immutable commit, artifact byte count, SHA-256, license, "
            "quantization recipe or runtime is established; nothing is read, hashed or loaded."
        ),
    }


def acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "mapped_cases": {
            "identity_noisy_control": {
                "status": "synthetic_only",
                "evidence": "controls.identity and controls.named_baseline"},
            "established_task_matched_baseline": {
                "status": "synthetic_only",
                "evidence": "named noisy_input_no_processing baseline"},
            "paired_si_sdr_stoi": {
                "status": "synthetic_only",
                "evidence": "per-condition paired synthetic clean references"},
            "clean_speech_preservation": {
                "status": "synthetic_only",
                "evidence": "controls.clean_speech_preservation"},
            "peaks_and_invalid_outputs": {
                "status": "synthetic_only",
                "evidence": "per-condition peaks and adverse rejections"},
            "unpaired_speech": {
                "status": "not_run",
                "reason": "no licensed real speech, predictive screen or listening result"},
            "alignment_state_memory_timing": {
                "status": "partial_analytical",
                "reason": (
                    "analytical identity mapping and zero offline delay; exact artifact delay, "
                    "state, memory and timing are unmeasured"
                )},
            "quantized_edge_runtime": {
                "status": "not_run",
                "reason": "no .tflite artifact, interpreter, delegate or target-edge measurement"},
        },
        "remaining_gates": list(GATE_NAMES),
    }


def readiness() -> Dict[str, Any]:
    return {
        "status": "blocked",
        "conclusion": "not_ready",
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "artifact_available": False,
        "exact_artifact_identity_pinned": False,
        "runtime_available": False,
        "rights_cleared": False,
        "synthetic_surrogate_only": True,
        "no_missing_result_qualifies_candidate": True,
        "exact_external_blocker": (
            "The exact DPCRN DNS3 / TFLite artifact and runtime cannot be admitted: the pinned "
            "census and candidate accounting locate only a public repository lead with status "
            "located_unverified and explicitly record that the exact checkpoint hash and weight "
            "licensing were not found; no immutable commit, .tflite bytes, byte count, SHA-256, "
            "conversion recipe or pinned TFLite interpreter/delegate exists, and no code, weight, "
            "training-data or redistribution terms are established."
        ),
        "reopen_condition": (
            "An authorized caller supplies an immutable upstream commit and the exact .tflite "
            "graph plus conversion source/checkpoint by path, byte count and SHA-256; a pinned "
            "TFLite interpreter version/ABI and CPU/edge delegate with a package digest in an "
            "approved isolated runner; written code, weight, training-data, conversion and "
            "runtime terms plus a positive legal/redistribution/product-use decision; and then "
            "real-model parity, a rights-cleared held-out paired cohort, independent listening or "
            "a separately labeled predictive screen, and target-runtime timing/memory/deadline "
            "evidence. Until then all eight release gates stay blocked."
        ),
        "next_action": (
            "Obtain the exact rights-cleared artifact and pinned runtime; do not register, expose, "
            "select or benchmark this component and do not treat the surrogate as a result."
        ),
    }


def gates() -> List[Dict[str, str]]:
    return [{"name": name, "status": "blocked", "reopen_condition": GATE_REOPEN[name]}
            for name in GATE_NAMES]


def qualification() -> Dict[str, Any]:
    return {
        "status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "qualifies": False,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "missing_result_promoted": False,
        "real_runtime_used": False,
        "real_model_used": False,
        "quality_claim": False,
        "benchmark_claim": False,
        "release_claim": False,
        "processor_exposure": False,
    }


def regressions(condition_map: Mapping[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for name in CONDITIONS:
        case = condition_map[name]
        if case["status"] == "excluded_no_reference":
            continue
        baseline = case["baseline_metrics"]
        candidate = case["candidate_metrics"]
        si_delta = (None if baseline["si_sdr_db"] is None or candidate["si_sdr_db"] is None
                    else round(candidate["si_sdr_db"] - baseline["si_sdr_db"], 6))
        stoi_delta = (None if baseline["stoi"] is None or candidate["stoi"] is None
                      else round(candidate["stoi"] - baseline["stoi"], 6))
        if ((si_delta is not None and si_delta < 0.0)
                or (stoi_delta is not None and stoi_delta < 0.0)):
            rows.append({"condition": name, "si_sdr_delta_db": si_delta,
                         "stoi_delta": stoi_delta})
    return rows


def core_report() -> Dict[str, Any]:
    condition_map = conditions()
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT_ID,
        "reference_family": REFERENCE_FAMILY,
        "task_mode": TASK_MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "qualification": qualification(),
        "task_identity": {
            "row_projection": dict(TASK_ROW_PROJECTION),
            "row_projection_sha256": TASK_ROW_PROJECTION_SHA256,
            "board_policy": dict(TASK_BOARD_POLICY),
        },
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "model_geometry": dict(MODEL_GEOMETRY),
        "artifact_requirement": dict(ARTIFACT_REQUIREMENT),
        "asset_boundary": {
            "mode": "caller_supplied_artifact_reference",
            "expected_root": "caller_supplied/DPCRN_DNS3_TFLITE",
            "expected_files": [],
            "admitted_artifact_descriptor_exists": False,
            "source_commit": UPSTREAM_COMMIT,
            "artifact_path": UPSTREAM_ARTIFACT_PATH,
            "artifact_sha256": UPSTREAM_ARTIFACT_SHA256,
            "artifact_bytes": UPSTREAM_ARTIFACT_BYTES,
            "asset_present": False,
            "asset_loaded_or_hashed": False,
            "asset_rights_verified": False,
            "runtime_available": False,
            "tflite_invoked": False,
            "real_path_status": "rejected_unpinned_artifact",
            "surrogate_path": SURROGATE_MODE,
            "silent_fallback_to_surrogate": False,
        },
        "public_boundary": {
            "header": "api/include/audio_sdk/provider_v0.h",
            "session_header": "api/include/audio_sdk/session_v0.h",
            "contract_file": "CONTRACTS.md",
            "abi_major": 0,
            "abi_minor": 1,
            "c_provider_added": False,
            "public_api_abi_changed": False,
            "registry_change": False,
            "default_change": False,
            "installed_v0_behavior_changed": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": report_artifact_pins(),
        "contract_sha256": sha256(contract_bytes()),
        "acceptance_profile": acceptance_profile(),
        "conditions": condition_map,
        "controls": controls(),
        "identity_reconstruction": identity_reconstruction(),
        "adverse": adverse(),
        "regressions": regressions(condition_map),
        "locator_evidence": dict(LOCATOR_EVIDENCE),
        "related_models_not_pooled": dict(RELATED_MODELS_NOT_POOLED),
        "independent_timing_evidence": dict(INDEPENDENT_TIMING_EVIDENCE),
        "prior_pilot_provenance": dict(PRIOR_PILOT_PROVENANCE),
        "readiness": readiness(),
        "rights_gap": dict(RIGHTS_GAP),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "model_provenance": model_provenance(),
        "caller_supplied_artifact_gate": asset_gate(),
        "surrogate_parameters": dict(SURROGATE_PARAMETERS),
        "surrogate_limitations": list(SURROGATE_LIMITATIONS),
        "scorer": {
            "scorer_id": SCORER_ID,
            "algorithm": "dependency-free zero-mean SI-SDR and non-extended pystoi 0.4.1 port",
            "used_as_oracle": False,
            "real_speech_claim": False,
        },
        "missing_evidence": list(MISSING_EVIDENCE),
        "negative_claims": dict(NEGATIVE_CLAIMS),
        "evidence_classes": list(EVIDENCE_CLASSES),
        "exact_blockers": list(EXACT_BLOCKERS),
        "gates": gates(),
    }


def repeatability() -> Dict[str, Any]:
    payloads = [canonical_report_bytes(core_report()) for _ in range(3)]
    digests = [sha256(payload) for payload in payloads]
    return {
        "count": 3,
        "scope": "core_report_without_repeatability",
        "byte_identical": len(set(payloads)) == 1,
        "digests": digests,
    }


def build_report() -> Dict[str, Any]:
    report = core_report()
    report["repeatability"] = repeatability()
    return report


def base_artifact_pins() -> Dict[str, str]:
    return {
        f"{TASK_REL}/reference.py": sha256((HERE / "reference.py").read_bytes()),
        f"{TASK_REL}/scorer.py": sha256((HERE / "scorer.py").read_bytes()),
        f"{TASK_REL}/run.py": sha256((HERE / "run.py").read_bytes()),
    }


def report_artifact_pins() -> Dict[str, str]:
    pins = base_artifact_pins()
    pins[f"{TASK_REL}/contract.json"] = sha256(contract_bytes())
    pins[f"{TASK_REL}/test_reference.py"] = sha256((HERE / "test_reference.py").read_bytes())
    pins[f"{TASK_REL}/verify.py"] = sha256((HERE / "verify.py").read_bytes())
    return pins


def contract() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_version": "0.1",
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT_ID,
        "repository": "audio-sdk",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "task_mode": TASK_MODE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "verification_profile": PROFILE,
        "reference_family": REFERENCE_FAMILY,
        "qualification_status": QUALIFICATION_STATUS,
        "qualification": qualification(),
        "adapter_id": ADAPTER_ID,
        "scope": (
            "Explicit missing-artifact blocker for the exact DPCRN DNS3 / TFLite candidate, "
            "with a deterministic synthetic surrogate at a declared DPCRN-family STFT boundary. "
            "No selection, real-model, runtime, device, listening, benchmark, provider or release claim."
        ),
        "task_identity": {
            "row_projection": dict(TASK_ROW_PROJECTION),
            "row_projection_sha256": TASK_ROW_PROJECTION_SHA256,
            "board_policy": dict(TASK_BOARD_POLICY),
        },
        "source_identity": {
            "upstream_repository": UPSTREAM_REPOSITORY,
            "upstream_results_repository": UPSTREAM_RESULTS_REPOSITORY,
            "upstream_commit": UPSTREAM_COMMIT,
            "upstream_license": UPSTREAM_LICENSE,
            "artifact_path": UPSTREAM_ARTIFACT_PATH,
            "artifact_sha256": UPSTREAM_ARTIFACT_SHA256,
            "artifact_bytes": UPSTREAM_ARTIFACT_BYTES,
            "locator_status": LOCATOR_STATUS,
            "census": dict(LOCATOR_EVIDENCE["census"]),
            "candidate_accounting": dict(LOCATOR_EVIDENCE["candidate_accounting"]),
            "note": (
                "Source location is a lead only. No upstream revision, artifact identity, license "
                "or runtime is verified; the package does not read, hash, download or execute it."
            ),
        },
        "frontend_contract": dict(FORMAT),
        "model_geometry": dict(MODEL_GEOMETRY),
        "artifact_requirement": dict(ARTIFACT_REQUIREMENT),
        "asset_boundary": {
            "mode": "caller_supplied_artifact_reference",
            "expected_root": "caller_supplied/DPCRN_DNS3_TFLITE",
            "expected_files": [],
            "admitted_artifact_descriptor_exists": False,
            "asset_present": False,
            "asset_rights_verified": False,
            "runtime_available": False,
            "tflite_invoked": False,
            "real_path_status": "rejected_unpinned_artifact",
            "surrogate_path": SURROGATE_MODE,
            "silent_fallback_to_surrogate": False,
        },
        "public_boundary": {
            "header": "api/include/audio_sdk/provider_v0.h",
            "session_header": "api/include/audio_sdk/session_v0.h",
            "contract_file": "CONTRACTS.md",
            "abi_major": 0,
            "abi_minor": 1,
            "c_provider_added": False,
            "public_api_abi_changed": False,
            "registry_change": False,
            "default_change": False,
            "installed_v0_behavior_changed": False,
        },
        "reference": {
            "adapter_id": ADAPTER_ID,
            "modes": [SURROGATE_MODE, REAL_MODE],
            "controls": ["identity_no_processing", "noisy_input_no_processing",
                         "frequency_chunked_spectral_gain_surrogate"],
            "candidate": "frequency_chunked_spectral_gain_surrogate",
            "control": "noisy_input_no_processing",
            "configuration_keys": ["mode", "asset"],
            "configuration_value": dict(CONFIG),
            "signal_samples": SIGNAL_SAMPLES,
            "causal": False,
            "model_weights": False,
            "downloads": False,
            "real_speech": False,
            "licensed_runtime": False,
            "tflite_invoked": False,
            "tensorflow_invoked": False,
            "device_or_timing_claim": False,
            "registered_in_bench": False,
            "produces_bench_bundle": False,
            "opt_in_required": True,
            "default_enabled": False,
        },
        "surrogate_parameters": dict(SURROGATE_PARAMETERS),
        "source_pins": {path.split(":", 1)[1]: digest
                        for path, digest in SOURCE_PINS.items()},
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": base_artifact_pins(),
        "acceptance_profile": acceptance_profile(),
        "locator_evidence": dict(LOCATOR_EVIDENCE),
        "related_models_not_pooled": dict(RELATED_MODELS_NOT_POOLED),
        "independent_timing_evidence": dict(INDEPENDENT_TIMING_EVIDENCE),
        "prior_pilot_provenance": dict(PRIOR_PILOT_PROVENANCE),
        "rights_gap": dict(RIGHTS_GAP),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "model_provenance": model_provenance(),
        "readiness": readiness(),
        "exact_blockers": list(EXACT_BLOCKERS),
        "gates": gates(),
        "invariants": [
            "Only this task directory is written; no shared SDK file, CMake, contract, public header, registry, default, board, handoff or CI file changes.",
            "The fixture is opt-in, unregistered and disabled by default with no C provider or production callback.",
            "The caller-supplied-artifact path fails closed and never silently falls back to the surrogate.",
            "No .tflite graph, checkpoint, source checkout, TensorFlow or TFLite runtime is downloaded, copied, opened or executed.",
            "All signals are frozen deterministic synthetic floats; no media, weight or runtime asset is read or produced.",
            "Configuration, signal, geometry, malformed artifact and fabricated-pin rejection cases fail closed without producing output.",
            "Identity and noisy-input controls are reported with the candidate; regressions are recorded verbatim.",
            "Three cold-start passes are byte-identical; canonical JSON and digest sidecars are regenerated deterministically.",
            "The mutable full plan/swarm/TASKS.json is never hashed; only the stable linked inventory-row projection is gated.",
            "Missing evidence never qualifies the candidate; decision remains DEFER and qualification not_qualified.",
        ],
        "blockers": list(EXACT_BLOCKERS),
        "reopening_conditions": [GATE_REOPEN[name] for name in GATE_NAMES],
    }


def contract_bytes() -> bytes:
    return canonical_bytes(contract()) + b"\n"


README_DIGEST_SECTION = "## Canonical artifacts and local digests"
README_GATES_SECTION = "## Remaining gates (all blocked)"
README_ARTIFACT_FILES = (
    "contract.json",
    "reference.py",
    "scorer.py",
    "run.py",
    "test_reference.py",
    "verify.py",
    "report.json",
    "report.json.sha256",
)
README_ROW_RE = re.compile(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \|$")
README_GATE_RE = re.compile(r"^(\d+)\. ")


def _readme_section(text: str, heading: str) -> str:
    if heading not in text:
        raise ValueError("readme_section_missing:" + heading)
    body = text.split(heading, 1)[1]
    if "\n## " in body:
        body = body.split("\n## ", 1)[0]
    return body


def readme_artifact_digests(text: str) -> Dict[str, str]:
    """Parse the README digest table; malformed or duplicate rows fail closed."""
    rows: Dict[str, str] = {}
    for line in _readme_section(text, README_DIGEST_SECTION).splitlines():
        if not line.startswith("|") or line in ("| File | SHA-256 |", "| --- | --- |"):
            continue
        match = README_ROW_RE.fullmatch(line)
        if match is None:
            raise ValueError("readme_digest_row_malformed:" + repr(line))
        name, digest = match.groups()
        if name in rows:
            raise ValueError("readme_digest_duplicate:" + name)
        rows[name] = digest
    return rows


def readme_gate_items(text: str) -> List[str]:
    """Parse the numbered remaining-gate list; numbering must be sequential."""
    items: List[str] = []
    for line in _readme_section(text, README_GATES_SECTION).splitlines():
        match = README_GATE_RE.match(line)
        if match is None:
            continue
        if int(match.group(1)) != len(items) + 1:
            raise ValueError("readme_gate_numbering:" + repr(line))
        items.append(line)
    return items


def sources_bytes() -> bytes:
    """Deterministic manifest; excludes SOURCES.sha256 itself to avoid self-reference."""
    pins: Dict[str, str] = dict(SOURCE_PINS)
    pins.update(BOUNDARY_PINS)
    for path in sorted(HERE.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "SOURCES.sha256":
            pins[f"{TASK_REL}/{path.name}"] = sha256(path.read_bytes())
    lines = [f"{digest}  {path}" for path, digest in sorted(pins.items())]
    header = (f"# SHA-256 pins for {TASK_ID}. source: paths are workspace-relative; "
              "other paths are SDK-worktree-relative. Lines are <sha256>  <path>. "
              "The mutable full plan/swarm/TASKS.json is deliberately not pinned.\n")
    return (header + "\n".join(lines) + "\n").encode("utf-8")


def interpreter_is_pinned() -> bool:
    return sys_version() == EVIDENCE_INTERPRETER


def sys_version() -> str:
    return platform.python_version()
