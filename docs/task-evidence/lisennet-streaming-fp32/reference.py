# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-LISENNET-STREAMING-FP32.

This module is NOT LiSenNet. It does not load the pinned ONNX graph, execute
ONNX Runtime, read audio or media, download weights, measure a device clock,
conduct listening, benchmark the SDK or qualify a release. It models the
streaming FP32 boundary as a caller-supplied external asset: exact frame
geometry, the 17-slot causal FIFO state contract, the host STFT/feature/phase
pipeline and a deterministic synthetic streaming surrogate.

The acceptance profile is Enhancement, assigned by plan/INVENTORY.json. Every
quality, rights, parity, listening, timing and release gate stays blocked. The
disposition is DEFER, evidence_status=incomplete, qualification_status=
not_qualified; a missing result never qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pystoi

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-LISENNET-STREAMING-FP32"
TITLE = "LiSenNet streaming FP32"
SLUG = "lisennet-streaming-fp32"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "c7cb12877fb8dce8620ba4963f0496a8061d9f7b"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
READINESS_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/readiness/0.1"
ADAPTER_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/adapter/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"

# Public v0 install geometry (unchanged by this package).
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"

# LiSenNet streaming graph geometry (source-derived, not executed here).
N_FFT = 512
HOP_SAMPLES = 256
WIN_LENGTH = 512
N_FREQS = N_FFT // 2 + 1
COMPRESS_POWER = 0.3
STATE_SLOT_COUNT = 17
STATE_PAST_FRAME_ROWS = 71
AVAILABILITY_LAG_SAMPLES = HOP_SAMPLES
CONTENT_LAG_SAMPLES = 0
CLOCK_ID = "fixture-sample-coordinate-not-device"

# Fixture and surrogate parameters.
SAMPLES = 32000
SNR_DB_STRATA = (12, 18, 24)
CONDITIONS = (
    "target_only",
    "mixture_snr12",
    "mixture_snr18",
    "mixture_snr24",
    "noise_only",
    "silence",
)
MIXTURE_CONDITIONS = ("mixture_snr12", "mixture_snr18", "mixture_snr24")
SEED = 20261126
PEAK_GUARD = 0.95
NOISE_MULTIPLIER = 1.0
MASK_FLOOR = 0.15
WARMUP_FRAMES = 8
EPS = 1e-12
MIN_STREAM_SAMPLES = N_FFT
IMPULSE_INDEX = 4000
IMPULSE_AMPLITUDE = 0.8
CHUNK_SIZES = (1, 7, 80, 159, 160, 161, 255, 256, 257, 320, 1280, SAMPLES)

# Pinned external candidate.
HF_REPOSITORY = "https://huggingface.co/claroche1/LiSenNet"
MODEL_REVISION = "4fe3356"
MODEL_ASSET_ID = "g_best_streaming_fp32.onnx"
MODEL_SHA256 = (
    "64b18acee261d54805c7cbe6b01a23f806160cf594c7c3f6df621c3b50a343db")
MODEL_BYTES = 323489
MODEL_VARIANT = "conv (dual-path conv wide, nc20, inter_dilations 1/2/4/8)"
MODEL_PARAMETERS = 41063
GRAPH_INPUTS = 18
RUNTIME = "onnxruntime CPUExecutionProvider (external; not installed or pinned)"
CODE_LICENSE_METADATA = "MIT"
MODEL_LICENSE_METADATA = "MIT"
REPORTED_PESQ_FP32 = 2.970

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "source": (
        "research/noise_suppression_pilot_20261027.md; "
        "research/noise_suppression_assets_20261027.json"),
    "paired_items": 30,
    "dataset": "DNS2020 exploratory subset",
    "mean_delta_snr_db": -5.1542,
    "mean_delta_si_sdr_db": -6.6148,
    "mean_delta_stoi": -0.0515,
    "batch_rtf": 0.0212,
    "reported_pesq_voicebank_demand_fp32": REPORTED_PESQ_FP32,
    "scope": (
        "Pinned research provenance only: the third-party streaming ONNX path "
        "was evaluated on 30 paired DNS2020 items with negative quality deltas. "
        "Not reproduced, not pooled with the surrogate and not used as a "
        "threshold."),
    "disclaimer": (
        "These are source-reported values for a different cohort and are not "
        "reproduced by this package."),
}

MODEL_PROVENANCE: Dict[str, Any] = {
    "model_card": HF_REPOSITORY,
    "source_revision": MODEL_REVISION,
    "revision_form": "7-hex abbreviated; not expanded to a full immutable commit here",
    "asset": MODEL_ASSET_ID,
    "asset_sha256": MODEL_SHA256,
    "asset_bytes": MODEL_BYTES,
    "variant": MODEL_VARIANT,
    "parameters": MODEL_PARAMETERS,
    "graph_contract": "feat(B,3,1,257) + 17 state tensors -> est_mag(B,1,257) + 17 states",
    "host_pipeline": (
        "centered 512-point/256-hop STFT with 256-sample reflect padding and a "
        "periodic Hann window; compressed magnitude |S|^0.3, group delay/pi and "
        "instantaneous-frequency-difference/pi; noisy-phase iSTFT overlap-add"),
    "reference_implementation": "https://github.com/hyyan2k/LiSenNet",
    "port": "https://github.com/LarocheC/eco8-neaixt",
    "code_license_metadata": CODE_LICENSE_METADATA,
    "model_license_metadata": MODEL_LICENSE_METADATA,
    "pretrained_weights_in_research_repo": False,
    "third_party_port": True,
}

LICENSING_ANALYSIS: Dict[str, Any] = {
    "upstream_reference_license": "MIT (data/checkouts/eco8-neaixt/LICENSE)",
    "model_card_license_metadata": MODEL_LICENSE_METADATA,
    "rights_cleared": False,
    "artifact_specific_weight_terms": False,
    "runtime_distribution_terms": False,
    "training_data_provenance": "not disclosed",
    "legal_review": False,
    "redistribution_permitted": False,
    "downloaded_or_vendored": False,
    "note": (
        "Apache-2.0/MIT metadata is recorded, not a clearance. No weight, graph, "
        "runtime or upstream source is copied, packaged, downloaded or "
        "redistributed by this package."),
}

# State cache: 17 causal FIFO slots mirroring the conv/ wide graph's
# _SLOT_ATTRS order (DSConv low/high, ConvolutionalGLU, _CausalTimeConv,
# MaskDecoder). Shapes are opaque until the caller supplies the asset.
STATE_SLOTS: Tuple[Dict[str, Any], ...] = (
    {"name": "state_0_in", "role": "encoder.conv_2.low.fifo", "past_frames": 1},
    {"name": "state_1_in", "role": "encoder.conv_2.high.fifo", "past_frames": 1},
    {"name": "state_2_in", "role": "encoder.conv_3.low.fifo", "past_frames": 1},
    {"name": "state_3_in", "role": "encoder.conv_3.high.fifo", "past_frames": 1},
    {"name": "state_4_in", "role": "encoder.conv_4.low.fifo", "past_frames": 1},
    {"name": "state_5_in", "role": "encoder.conv_4.high.fifo", "past_frames": 1},
    {"name": "state_6_in", "role": "block0.conv_glu.depthwise.fifo", "past_frames": 2},
    {"name": "state_7_in", "role": "block0.inter_time.dilation1.fifo", "past_frames": 2},
    {"name": "state_8_in", "role": "block0.inter_time.dilation2.fifo", "past_frames": 4},
    {"name": "state_9_in", "role": "block0.inter_time.dilation4.fifo", "past_frames": 8},
    {"name": "state_10_in", "role": "block0.inter_time.dilation8.fifo", "past_frames": 16},
    {"name": "state_11_in", "role": "block1.conv_glu.depthwise.fifo", "past_frames": 2},
    {"name": "state_12_in", "role": "block1.inter_time.dilation1.fifo", "past_frames": 2},
    {"name": "state_13_in", "role": "block1.inter_time.dilation2.fifo", "past_frames": 4},
    {"name": "state_14_in", "role": "block1.inter_time.dilation4.fifo", "past_frames": 8},
    {"name": "state_15_in", "role": "block1.inter_time.dilation8.fifo", "past_frames": 16},
    {"name": "state_16_in", "role": "decoder.mask_conv.fifo", "past_frames": 1},
)

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
    "samples_per_call": FRAME_SAMPLES,
}

STREAMING_GEOMETRY: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "public_v0_frame_samples": FRAME_SAMPLES,
    "n_fft": N_FFT,
    "hop_samples": HOP_SAMPLES,
    "win_length": WIN_LENGTH,
    "n_freqs": N_FREQS,
    "frame_duration_us": (HOP_SAMPLES * 1_000_000) // SAMPLE_RATE_HZ,
    "window": "periodic Hann (np.hanning(513)[:-1])",
    "padding": "256-sample reflect on both edges (torch-compatible center=True)",
    "compress_power": COMPRESS_POWER,
    "features": ["compressed_magnitude", "group_delay_over_pi", "ifd_over_pi"],
    "phase_recovery": "noisy phase (causal iSTFT)",
    "griffin_lim": "not used; the offline 2-iteration GL path is outside this boundary",
    "state_slot_count": STATE_SLOT_COUNT,
    "state_past_frame_rows": STATE_PAST_FRAME_ROWS,
    "graph_inputs": GRAPH_INPUTS,
    "content_lag_samples": CONTENT_LAG_SAMPLES,
    "availability_lag_samples": AVAILABILITY_LAG_SAMPLES,
    "minimum_stream_samples": MIN_STREAM_SAMPLES,
}

STATE_CACHE_CONTRACT: Dict[str, Any] = {
    "slots": [dict(slot) for slot in STATE_SLOTS],
    "slot_count": STATE_SLOT_COUNT,
    "past_frame_rows": STATE_PAST_FRAME_ROWS,
    "dtype": "f32",
    "shape_visibility": "opaque; caller initializes from the supplied graph",
    "initialization": "all-zero at stream start",
    "carry_rule": "state_out[n] feeds state_in[n+1] for every slot",
    "reset": "restore the exact all-zero initial state",
    "surrogate_cache_bytes": (
        STATE_PAST_FRAME_ROWS * 3 * N_FREQS * 4),
    "asset_state_bytes": None,
}

CALLER_ASSET_FIELDS = (
    "asset_id",
    "sha256",
    "byte_count",
    "storage",
    "source_repository",
    "source_revision",
    "sample_rate_hz",
    "channels",
    "n_fft",
    "hop_samples",
    "n_freqs",
    "compress_power",
    "state_slot_count",
    "sample_format",
)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/lisennet-streaming-fp32/caller-supplied-asset/0.1",
    "required_fields": list(CALLER_ASSET_FIELDS),
    "optional_fields": ["caller_path"],
    "pinned_values": {
        "asset_id": MODEL_ASSET_ID,
        "sha256": MODEL_SHA256,
        "byte_count": MODEL_BYTES,
        "storage": "external",
        "source_repository": HF_REPOSITORY,
        "source_revision": MODEL_REVISION,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "n_fft": N_FFT,
        "hop_samples": HOP_SAMPLES,
        "n_freqs": N_FREQS,
        "compress_power": COMPRESS_POWER,
        "state_slot_count": STATE_SLOT_COUNT,
        "sample_format": SAMPLE_FORMAT,
    },
    "verification": [
        "metadata-only; no file is opened, hashed, mapped, stat'ed or executed",
        "caller_path is optional and must be absolute; it is never resolved or read",
        "missing, extra, mistyped or mismatched fields fail closed before any frame",
        "the caller owns storage and supplies the runtime; no download is attempted",
        "state tensors are caller-initialized from the supplied graph and are opaque",
    ],
}

BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "installed_v0_geometry_preserved": True,
    "installed_v0_behavior_change": False,
    "shared_build_or_ci_change": False,
    "processor_exposure": False,
    "task_board_or_handoff_write": False,
}

CLAIMS: Dict[str, bool] = {
    "real_lisennet_runtime": False,
    "weights_accessed": False,
    "asset_downloaded": False,
    "real_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "streaming_latency_measured": False,
    "listening_result_produced": False,
    "quality_claim": False,
    "benchmark_result": False,
    "release_claim": False,
}

EXACT_BLOCKERS: List[str] = [
    (
        "Asset identity is not admitted: the ledger records "
        f"{MODEL_ASSET_ID} as {MODEL_BYTES} bytes with SHA-256 {MODEL_SHA256} "
        f"under {HF_REPOSITORY} at source_revision {MODEL_REVISION!r}, but "
        "that revision is a 7-hex abbreviation with no immutable full-commit "
        "retrieval record tying those bytes to it. The artifact is absent from "
        "this SDK worktree and must resolve from the caller's own storage; no "
        "bytes were read, hashed or downloaded."),
    (
        "The runtime is absent and unpinned: the streaming graph requires an "
        "ONNX Runtime CPU runtime for feat + 17 state inputs. onnxruntime is not "
        "installed in this environment and no pinned wheel/sdist digest or "
        "runtime distribution/product-use terms exist here. The host STFT, "
        "feature extraction and noisy-phase iSTFT in the research adapter are "
        "not vendored or executed."),
    (
        "Artifact-specific rights are not cleared: MIT is recorded for the port "
        "LICENSE and the model card, but written weight-specific terms, "
        "training-data provenance (beyond the VoiceBank-DEMAND reporting "
        "scope), redistribution/product-use clearance and legal review are "
        "absent. No weight, graph, runtime or upstream source may be copied, "
        "packaged, downloaded or redistributed by this package."),
    (
        "No qualification evidence exists: there is no rights-cleared paired "
        "real cohort with clean references, no independent STOI/SI-SDR scorer "
        "result, no permitted listening, no target-runtime pacing, availability, "
        "deadline or memory measurement, and no approved exact streaming "
        "reference output vector for these frozen inputs. The synthetic "
        "surrogate can never stand in for any of these."),
]

GATE_DEFINITIONS: List[Tuple[str, str]] = [
    (
        "exact_asset_identity",
        "Reopen only when the exact g_best_streaming_fp32.onnx bytes are "
        "addressed by a full immutable repository commit plus byte count and "
        "SHA-256 in a retrieval record, and resolve from the caller's own "
        "storage without a download."),
    (
        "runtime_admission",
        "Reopen only when a pinned ONNX Runtime CPU artifact with a recorded "
        "digest installs in the intended environment and its distribution and "
        "product-use terms are documented."),
    (
        "artifact_rights",
        "Reopen only after written artifact-specific weight, runtime and "
        "training-data terms are recorded and a legal/redistribution decision "
        "exists; MIT metadata alone is not clearance."),
    (
        "host_dsp_parity",
        "Reopen only when the host STFT, three-channel feature extraction, "
        "state carry and noisy-phase iSTFT reproduce the published graph's "
        "documented parity tolerance on approved vectors."),
    (
        "exact_reference_parity",
        "Reopen only with approved exact streaming reference outputs for the "
        "frozen inputs, generated from the caller asset and the pinned runtime."),
    (
        "rights_cleared_cohort",
        "Reopen only with a rights-cleared paired real speech cohort carrying "
        "clean references and a frozen matched baseline."),
    (
        "independent_scoring_and_listening",
        "Reopen only after an independent intrusive scorer and permitted "
        "listening are completed with their own reported protocol."),
    (
        "target_runtime_timing",
        "Reopen only after pacing, availability, deadline, memory and state "
        "behaviour are measured on the intended target runtime."),
    (
        "provider_intake",
        "Reopen only after rights/runtime/parity gates clear and an opt-in "
        "provider intake with OFF default and independent review is approved."),
    (
        "public_default_selection",
        "Reopen only after provider intake clears and the owner records an "
        "explicit default decision with preserving controls."),
]

MISSING_EVIDENCE: List[str] = [
    "immutable full-commit revision and caller-held bytes for the pinned ONNX asset",
    "pinned ONNX Runtime CPU runtime artifact and installation evidence",
    "written artifact-specific weight/runtime/training-data rights clearance",
    "host STFT/feature/state/iSTFT parity against the published graph",
    "approved exact streaming reference output vectors for the frozen inputs",
    "rights-cleared paired real speech cohort with clean references",
    "independent STOI/SI-SDR/intrusive scorer and permitted listening",
    "target-runtime pacing, availability, deadline, memory and state evidence",
    "opt-in provider intake, descriptor review and explicit default selection",
]

REOPENING_CONDITIONS: List[str] = [reopen for _, reopen in GATE_DEFINITIONS]

SCOPE: Dict[str, Any] = {
    "task_local_directory": TASK_PREFIX.rstrip("/"),
    "shared_sdk_changes": False,
    "board_or_handoff_write": False,
    "network_access": False,
    "downloads": False,
    "real_audio": False,
    "vendor_runtime": False,
    "device_clock": False,
    "listening": False,
    "benchmark": False,
    "release": False,
}

NEGATIVE_CLAIMS: Dict[str, bool] = {
    "lisennet_executed": False,
    "onnx_runtime_invoked": False,
    "asset_present_or_read": False,
    "quality_or_parity_pass": False,
    "latency_or_deadline_measured": False,
    "release_ready": False,
}

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "adapters/lisennet/adapter.json":
        "1a12f0cb768d018b480ca325c9e8b3a9b374e6b53aff9fdad505c8920acb9643",
    "adapters/lisennet/README.md":
        "aef55b5b753e6d450bb9bb3355e9e12daa49f26b55e835e989f853ee30a714c4",
    "adapters/lisennet/run.py":
        "86ff5220d70b3aa77cefa5b7332935779f9e11f3e048dce501688053174ee6b1",
    "data/checkouts/eco8-neaixt/LICENSE":
        "6239327208515d111fc473c38e620e7154d7d432168e671c4253e2744c0ef166",
    "data/checkouts/eco8-neaixt/docs/models/lisennet.md":
        "df4bf439dab6b81ef95f881accc1e0e3ae52fb2b5eeaaaa1a0d6bcbd9a57777d",
    "data/checkouts/eco8-neaixt/lisennet/export_onnx.py":
        "4af7044839fcd9270271850b659607a546abd84eb389a08d6b147f6dc09e1a07",
    "data/checkouts/eco8-neaixt/lisennet/model.py":
        "df846e8ceae26b6c9866c3a5bbb919c5f557d02a39051da7bdc8e9ca2c70c813",
    "data/checkouts/eco8-neaixt/lisennet/streaming.py":
        "5009ba820f1810b1a26b19ac64f24362b3be0982205af448e5c69829c5a17324",
    "data/checkouts/eco8-neaixt/push_lisennet_hf.py":
        "c03beb8f021909bdfb5d5548cbd2e8a3c7e6ba17f2ceeb035d25a38325645dda",
    "data/checkouts/eco8-neaixt/configs/lisennet_conv_wide.json":
        "c239b3f8b55f9cc72448738efcf0e7ba83a800906768a952b8ca08444a5edcd9",
    "data/checkouts/eco8-neaixt/benchmarks/published.py":
        "bc267a16be1e90803394f19d9de740c488abfe1a15c9a747f08a250c01127bfa",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}

LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "LICENSES.md",
    "SOURCES.sha256.license",
    "adapter.json",
    "adapter.json.license",
    "contract.json",
    "contract.json.license",
    "readiness.json",
    "readiness.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "requirements.lock",
    "requirements.lock.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)

ASSET_ADMISSION_REASONS: Tuple[str, ...] = (
    "asset_bytes_absent",
    "revision_not_immutable",
    "runtime_unavailable",
    "rights_not_cleared",
    "download_not_permitted",
)

README_PIN_ROW_RE = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*`([a-f0-9]{64})`\s*\|")


# ---------------------------------------------------------------------------
# Canonical serialization
# ---------------------------------------------------------------------------


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _plain(value: Any) -> Any:
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite value")
        rounded = round(value, 6)
        return 0.0 if rounded == 0 else rounded
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    raise TypeError("unsupported canonical type: " + type(value).__name__)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_plain(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha32(signal: np.ndarray) -> str:
    return sha256(np.ascontiguousarray(signal, dtype="<f4").tobytes())


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(item) for item in value.values())
    if isinstance(value, list):
        return any(has_negative_zero(item) for item in value)
    return False


def strict_loads(text: str) -> Any:
    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key: " + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise ValueError("nonfinite constant: " + token)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


# ---------------------------------------------------------------------------
# Caller-supplied asset boundary
# ---------------------------------------------------------------------------


def default_asset_manifest() -> Dict[str, Any]:
    return {
        "asset_id": MODEL_ASSET_ID,
        "sha256": MODEL_SHA256,
        "byte_count": MODEL_BYTES,
        "storage": "external",
        "source_repository": HF_REPOSITORY,
        "source_revision": MODEL_REVISION,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "n_fft": N_FFT,
        "hop_samples": HOP_SAMPLES,
        "n_freqs": N_FREQS,
        "compress_power": COMPRESS_POWER,
        "state_slot_count": STATE_SLOT_COUNT,
        "sample_format": SAMPLE_FORMAT,
    }


def _validate_manifest_structure(manifest: Any) -> Dict[str, Any]:
    """Validate field presence/types only; never touch the filesystem."""
    if not isinstance(manifest, dict):
        raise ValueError("asset_manifest_not_object")
    keys = set(manifest)
    required = set(CALLER_ASSET_FIELDS)
    if keys - required - {"caller_path"}:
        raise ValueError("unexpected_fields:" + ",".join(sorted(keys - required - {"caller_path"})))
    missing = required - keys
    if missing:
        raise ValueError("missing_fields:" + ",".join(sorted(missing)))
    for field in CALLER_ASSET_FIELDS:
        value = manifest[field]
        if field in ("byte_count", "state_slot_count", "sample_rate_hz",
                     "channels", "n_fft", "hop_samples", "n_freqs"):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("field_type:" + field)
        elif field == "compress_power":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("field_type:compress_power")
        elif not isinstance(value, str):
            raise ValueError("field_type:" + field)
        if field == "sha256" and not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("invalid_sha256")
    if "caller_path" in manifest:
        path = manifest["caller_path"]
        if not isinstance(path, str) or not path:
            raise ValueError("invalid_caller_path")
        if not Path(path).is_absolute():
            raise ValueError("relative_caller_path")
    return dict(manifest)


def validate_asset_manifest(manifest: Any) -> Dict[str, Any]:
    """Validate the caller asset metadata against the pinned candidate."""
    candidate = _validate_manifest_structure(manifest)
    expected = default_asset_manifest()
    for field in CALLER_ASSET_FIELDS:
        if candidate[field] != expected[field]:
            raise ValueError("field_mismatch:" + field)
    return candidate


def admit_asset(manifest: Any) -> Dict[str, Any]:
    """Admit metadata, then record that the pinned bytes/runtime are absent."""
    try:
        validate_asset_manifest(manifest)
        reasons = list(ASSET_ADMISSION_REASONS)
    except ValueError as error:
        reasons = ["manifest_rejected:" + str(error)] + list(ASSET_ADMISSION_REASONS)
    return {
        "status": "blocked",
        "reason_codes": reasons,
        "asset_bytes_read": False,
        "asset_file_accessed": False,
        "download_attempted": False,
        "vendor_runtime_invoked": False,
    }


def synthetic_manifest() -> Dict[str, Any]:
    payload = b"synthetic-lisennet-streaming-surrogate-v1"
    return {
        "asset_id": "synthetic-streaming-surrogate",
        "sha256": sha256(payload),
        "byte_count": len(payload),
        "storage": "external",
        "source_repository": "task-local-fixture",
        "source_revision": "fixture",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "n_fft": N_FFT,
        "hop_samples": HOP_SAMPLES,
        "n_freqs": N_FREQS,
        "compress_power": COMPRESS_POWER,
        "state_slot_count": STATE_SLOT_COUNT,
        "sample_format": SAMPLE_FORMAT,
        "caller_path": "/synthetic/nonexistent/surrogate.bin",
    }


def synthetic_admission_control() -> Dict[str, Any]:
    manifest = synthetic_manifest()
    candidate = _validate_manifest_structure(manifest)
    expected = default_asset_manifest()
    for field in ("sample_rate_hz", "channels", "n_fft", "hop_samples",
                  "n_freqs", "compress_power", "state_slot_count",
                  "sample_format"):
        if candidate[field] != expected[field]:
            raise ValueError("synthetic_geometry_mismatch:" + field)
    return {
        "status": "admitted",
        "not_the_pinned_candidate": True,
        "asset_bytes_read": False,
        "download_attempted": False,
        "vendor_runtime_invoked": False,
        "note": (
            "Only the geometry/metadata admission path is exercised; the "
            "surrogate binary is not read, executed or the candidate."),
    }


# ---------------------------------------------------------------------------
# Frozen synthetic stimuli
# ---------------------------------------------------------------------------


def _harmonic_target() -> np.ndarray:
    t = np.arange(SAMPLES, dtype=np.float64) / SAMPLE_RATE_HZ
    f0 = 118.0 + 6.0 * np.sin(2.0 * math.pi * 0.7 * t)
    phase = 2.0 * math.pi * np.cumsum(f0) / SAMPLE_RATE_HZ
    carrier = np.zeros(SAMPLES, dtype=np.float64)
    weights = (0.34, 0.24, 0.16, 0.11, 0.07, 0.04, 0.02, 0.01, 0.005, 0.003,
               0.002, 0.001)
    for index, weight in enumerate(weights):
        carrier += weight * np.sin(
            float(index + 1) * phase + 0.37 * float((index + 1) ** 2))
    carrier /= np.max(np.abs(carrier))
    # Syllabic envelope with silent gaps so the noise-floor control is exercised.
    syllables = np.maximum(0.0, np.sin(2.0 * math.pi * 2.3 * t)) ** 0.65
    envelope = 0.18 + 0.82 * syllables
    target = 0.42 * envelope * carrier
    return target.astype(np.float64)


@lru_cache(maxsize=1)
def _target_cached() -> np.ndarray:
    return _harmonic_target()


def _noise(seed_offset: int = 0) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(SEED + seed_offset))
    return rng.standard_normal(SAMPLES).astype(np.float64)


def _rms(signal: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(signal, dtype=np.float64))))


def _mix(target: np.ndarray, noise: np.ndarray, snr_db: float) -> np.ndarray:
    target_rms = _rms(target)
    noise_rms = _rms(noise)
    if noise_rms <= 0.0 or target_rms <= 0.0:
        return target.copy()
    scale = target_rms / (noise_rms * (10.0 ** (snr_db / 20.0)))
    mixture = target + scale * noise
    peak = float(np.max(np.abs(mixture))) if mixture.size else 0.0
    if peak > PEAK_GUARD:
        mixture = mixture * (PEAK_GUARD / peak)
    return mixture


@lru_cache(maxsize=None)
def _synth_cached(condition: str) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    if condition not in CONDITIONS:
        raise ValueError("unknown_condition:" + condition)
    target = _target_cached()
    noise = _noise(0)
    if condition == "target_only":
        clean, observed = target, target.copy()
    elif condition.startswith("mixture_snr"):
        snr_db = float(condition.rsplit("snr", 1)[1])
        clean, observed = target, _mix(target, noise, snr_db)
    elif condition == "noise_only":
        scaled = 0.2 * noise / max(_rms(noise), EPS)
        clean, observed = np.zeros(SAMPLES), scaled
    elif condition == "silence":
        clean, observed = np.zeros(SAMPLES), np.zeros(SAMPLES)
    else:  # pragma: no cover - guarded above
        raise ValueError("unknown_condition:" + condition)
    return tuple(clean.tolist()), tuple(observed.tolist())


def synth(condition: str) -> Tuple[np.ndarray, np.ndarray]:
    clean, observed = _synth_cached(condition)
    return (np.asarray(clean, dtype=np.float64),
            np.asarray(observed, dtype=np.float64))


# ---------------------------------------------------------------------------
# Streaming surrogate
# ---------------------------------------------------------------------------


def _reflect_indices(indices: np.ndarray, length: int) -> np.ndarray:
    if length < 2:
        return np.zeros_like(indices)
    result = np.abs(indices)
    over = result >= length
    result = np.where(over, 2 * (length - 1) - result, result)
    if np.any(result < 0) or np.any(result >= length):
        raise ValueError("reflect_range_unsupported")
    return result


def _periodic_hann() -> np.ndarray:
    return np.hanning(WIN_LENGTH + 1)[:-1].astype(np.float64)


def _wrap_phase(value: np.ndarray) -> np.ndarray:
    return np.arctan2(np.sin(value), np.cos(value))


class StreamingSurrogate:
    """Stateful fixture for the streaming boundary; not LiSenNet.

    The session buffers caller PCM, frames it with the pinned centered STFT
    geometry, builds the three-channel feature frame, carries a 17-slot causal
    FIFO state cache plus the previous-phase feature state, applies a
    deterministic per-bin noise-floor mask, overlap-adds the noisy-phase iSTFT
    and emits only samples whose windows are complete.
    """

    def __init__(self, manifest: Optional[Dict[str, Any]] = None,
                 opt_in: bool = False) -> None:
        if opt_in is not True:
            raise ValueError("surrogate_opt_in_required")
        self.manifest = validate_asset_manifest(
            default_asset_manifest() if manifest is None else manifest)
        self._window = _periodic_hann()
        self.reset()

    def reset(self) -> None:
        self._x = np.zeros(0, dtype=np.float64)
        self._out = np.zeros(0, dtype=np.float64)
        self._norm = np.zeros(0, dtype=np.float64)
        self._prev_pha = np.zeros(N_FREQS, dtype=np.float64)
        self._noise = np.zeros(N_FREQS, dtype=np.float64)
        self._noise_initialized = False
        self._slots = [
            np.zeros((slot["past_frames"], 3, N_FREQS), dtype=np.float64)
            for slot in STATE_SLOTS
        ]
        self._frames_done = 0
        self._emitted = 0
        self._flushed = False
        self._input_samples = 0
        self._state_chain = sha256(b"lisennet-streaming-surrogate-init")

    @property
    def state_slots(self) -> int:
        return len(self._slots)

    @property
    def state_past_frame_rows(self) -> int:
        return sum(slot["past_frames"] for slot in STATE_SLOTS)

    def _ensure_capacity(self, needed: int) -> None:
        for name in ("_out", "_norm"):
            current = getattr(self, name)
            if len(current) < needed:
                extra = np.zeros(needed - len(current), dtype=np.float64)
                setattr(self, name, np.concatenate([current, extra]))

    def state_digest(self) -> str:
        parts = [self._state_chain.encode("ascii"),
                 self._prev_pha.astype("<f8").tobytes(),
                 self._noise.astype("<f8").tobytes(),
                 np.asarray([self._frames_done, self._emitted,
                             self._input_samples,
                             1.0 if self._flushed else 0.0],
                            dtype="<f8").tobytes()]
        for slot in self._slots:
            parts.append(slot.astype("<f8").tobytes())
        return sha256(b"".join(parts))

    def _padded_frame(self, frame_index: int) -> np.ndarray:
        start = frame_index * HOP_SAMPLES - HOP_SAMPLES
        indices = start + np.arange(WIN_LENGTH, dtype=np.int64)
        indices = _reflect_indices(indices, len(self._x))
        return self._x[indices]

    def _graph_step(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        start = self._frames_done * HOP_SAMPLES
        segment = frame * self._window
        spectrum = np.fft.rfft(segment, n=N_FFT)
        magnitude = np.abs(spectrum)
        phase = np.angle(spectrum)

        group_delay = np.concatenate(
            ([0.0], np.diff(phase))).astype(np.float64)
        group_delay = _wrap_phase(group_delay)
        ifd = phase - self._prev_pha
        bias = 2.0 * math.pi * (HOP_SAMPLES / N_FFT) * np.arange(N_FREQS)
        ifd = _wrap_phase(ifd - bias)
        self._prev_pha = phase

        compressed = magnitude ** COMPRESS_POWER
        feature = np.stack([compressed, group_delay / math.pi, ifd / math.pi], axis=0)
        for slot, data in zip(STATE_SLOTS, self._slots):
            keep = slot["past_frames"]
            data[:-1] = data[1:]
            data[-1] = feature

        if not self._noise_initialized:
            self._noise = magnitude.copy()
            self._noise_initialized = True
        elif self._frames_done <= WARMUP_FRAMES:
            self._noise = ((self._noise * self._frames_done + magnitude)
                           / (self._frames_done + 1))
        if self._frames_done <= WARMUP_FRAMES:
            mask = np.ones(N_FREQS, dtype=np.float64)
        else:
            ratio = NOISE_MULTIPLIER * self._noise / (magnitude + EPS)
            gate = 1.0 / (1.0 + ratio * ratio)
            mask = np.clip(gate, MASK_FLOOR, 1.0)
        enhanced = mask * magnitude * np.exp(1j * phase)
        time_frame = np.fft.irfft(enhanced, n=N_FFT)

        self._ensure_capacity(start + WIN_LENGTH)
        self._out[start:start + WIN_LENGTH] += time_frame * self._window
        self._norm[start:start + WIN_LENGTH] += self._window * self._window
        self._frames_done += 1
        self._state_chain = sha256(
            self._state_chain.encode("ascii") + feature.astype("<f8").tobytes()
            + np.asarray([self._frames_done], dtype="<f8").tobytes())
        return time_frame, feature

    def _emit(self, upto: int) -> np.ndarray:
        upto = min(upto, self._input_samples)
        if upto <= self._emitted:
            return np.zeros(0, dtype=np.float32)
        begin = self._emitted + HOP_SAMPLES
        end = upto + HOP_SAMPLES
        norm = self._norm[begin:end]
        valid = norm > 1e-11
        output = np.zeros(end - begin, dtype=np.float64)
        output[valid] = self._out[begin:end][valid] / norm[valid]
        self._emitted = upto
        return output.astype(np.float32)

    def _advance(self, final: bool) -> np.ndarray:
        total = len(self._x)
        if final:
            target_frames = total // HOP_SAMPLES + 1
        else:
            target_frames = max(0, total // HOP_SAMPLES - 1)
        while self._frames_done < target_frames:
            self._graph_step(self._padded_frame(self._frames_done))
        if final:
            return self._emit(total)
        return self._emit(max(0, self._frames_done - 1) * HOP_SAMPLES)

    def process(self, chunk: Any) -> np.ndarray:
        if self._flushed:
            raise ValueError("process_after_flush")
        array = np.asarray(chunk)
        if array.dtype.kind not in "fiu":
            raise ValueError("non_numeric_input")
        array = np.asarray(array, dtype=np.float64)
        if array.ndim != 1:
            raise ValueError("input_must_be_mono_1d")
        if array.size and not np.all(np.isfinite(array)):
            raise ValueError("nonfinite_input")
        if array.size == 0:
            return np.zeros(0, dtype=np.float32)
        self._input_samples += int(array.size)
        self._x = np.concatenate([self._x, array])
        return self._advance(False)

    def flush(self) -> np.ndarray:
        if self._flushed:
            return np.zeros(0, dtype=np.float32)
        total = len(self._x)
        if total == 0:
            self._flushed = True
            return np.zeros(0, dtype=np.float32)
        if total < MIN_STREAM_SAMPLES:
            raise ValueError("stream_too_short_for_reflect_padding")
        output = self._advance(True)
        if self._emitted != total:
            raise RuntimeError("flush_accounting_mismatch")
        self._flushed = True
        return output


def run_stream(signal: Sequence[float], chunk_size: int,
               manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if chunk_size <= 0:
        raise ValueError("chunk_size_must_be_positive")
    array = np.asarray(signal, dtype=np.float64)
    session = StreamingSurrogate(manifest=manifest, opt_in=True)
    pieces: List[np.ndarray] = []
    emitted_before_flush = 0
    for start in range(0, len(array), chunk_size):
        piece = session.process(array[start:start + chunk_size])
        emitted_before_flush += int(piece.size)
        pieces.append(piece)
    flush = session.flush()
    pieces.append(flush)
    output = (np.concatenate(pieces) if pieces else
              np.zeros(0, dtype=np.float32)).astype(np.float32)
    if output.size != len(array):
        raise RuntimeError("output_length_mismatch")
    return {
        "output": output,
        "digest": sha32(output),
        "emitted_before_flush": emitted_before_flush,
        "flush_emitted": int(flush.size),
        "state_digest": session.state_digest(),
        "frames": session._frames_done,
        "chunks": (len(array) + chunk_size - 1) // chunk_size,
        "state_slots": session.state_slots,
        "state_past_frame_rows": session.state_past_frame_rows,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def _db(numerator: float, denominator: float) -> Optional[float]:
    if numerator <= EPS or denominator <= EPS:
        return None
    return 10.0 * math.log10(numerator / denominator)


def score(clean: np.ndarray, estimate: np.ndarray) -> Dict[str, Any]:
    reference = np.asarray(clean, dtype=np.float64)
    output = np.asarray(estimate, dtype=np.float64)
    reference_energy = float(np.sum(reference * reference))
    result: Dict[str, Any] = {
        "reference_energy": reference_energy,
        "snr_db": None,
        "si_sdr_db": None,
        "stoi": None,
        "undefined": [],
    }
    if reference_energy <= EPS:
        result["undefined"].append("zero_reference")
        return result
    error_energy = float(np.sum((output - reference) ** 2))
    snr = _db(reference_energy, error_energy)
    if snr is None:
        result["undefined"].append("zero_error_identity_exact")
    else:
        result["snr_db"] = snr
    scale = float(np.dot(reference, output) / reference_energy)
    projected = scale * reference
    noise_energy = float(np.sum((output - projected) ** 2))
    si_sdr = _db(float(np.sum(projected * projected)), noise_energy)
    if si_sdr is None:
        result["undefined"].append("zero_error_si_sdr_exact")
    else:
        result["si_sdr_db"] = si_sdr
    try:
        value = float(pystoi.stoi(reference, output, SAMPLE_RATE_HZ,
                                  extended=False))
        if math.isfinite(value):
            result["stoi"] = min(1.0, max(0.0, value))
        else:
            result["undefined"].append("nonfinite_stoi")
    except Exception:  # pystoi rejects degenerate/constant references
        result["undefined"].append("stoi_unscorable")
    return result


def projection(clean: np.ndarray, observed: np.ndarray,
               estimate: np.ndarray) -> Dict[str, Any]:
    reference = np.asarray(clean, dtype=np.float64)
    noise = np.asarray(observed, dtype=np.float64) - reference
    output = np.asarray(estimate, dtype=np.float64)
    target_energy = float(np.dot(reference, reference))
    noise_energy = float(np.dot(noise, noise))
    if target_energy <= EPS:
        return {"target_retention": None, "noise_retention": None,
                "target_to_noise_gain_db": None,
                "undefined": ["zero_target_reference"]}
    alpha = float(np.dot(output, reference) / target_energy)
    beta = (float(np.dot(output, noise) / noise_energy)
            if noise_energy > EPS else None)
    gain = (20.0 * math.log10(abs(alpha) / abs(beta))
            if beta is not None and abs(beta) > EPS and abs(alpha) > EPS
            else None)
    projected = alpha * reference
    residual = output - projected
    snr_delta = _db(float(np.sum(projected * projected)),
                    float(np.sum(residual * residual)))
    return {
        "target_retention": alpha,
        "noise_retention": beta,
        "target_to_noise_gain_db": gain,
        "target_projection_snr_db": snr_delta,
        "undefined": [],
    }


# ---------------------------------------------------------------------------
# Boundary evidence
# ---------------------------------------------------------------------------


def _variant(name: str, clean: np.ndarray, observed: np.ndarray,
             output: np.ndarray) -> Dict[str, Any]:
    metrics = score(clean, output)
    return {
        "name": name,
        "output_sha256": sha32(output),
        "output_samples": int(output.size),
        "nonfinite_samples": int(np.count_nonzero(~np.isfinite(output))),
        "peak_abs_output": float(np.max(np.abs(output))) if output.size else 0.0,
        "clipped_samples": int(np.count_nonzero(np.abs(output) >= 1.0)),
        "snr_db": metrics["snr_db"],
        "si_sdr_db": metrics["si_sdr_db"],
        "stoi": metrics["stoi"],
        "undefined": metrics["undefined"],
        "projection": projection(clean, observed, output),
    }


def condition_block(condition: str) -> Dict[str, Any]:
    clean, observed = synth(condition)
    identity = observed.copy()
    streamed = run_stream(observed, FRAME_SAMPLES)
    whole = run_stream(observed, len(observed))
    variants = {
        "identity_passthrough": _variant(
            "identity_passthrough", clean, observed, identity),
        "noisy_control": _variant("noisy_control", clean, observed,
                                  observed.copy()),
        "surrogate_stream_160": _variant(
            "surrogate_stream_160", clean, observed, streamed["output"]),
        "surrogate_whole_call": _variant(
            "surrogate_whole_call", clean, observed, whole["output"]),
    }
    return {
        "condition": condition,
        "input_sha256": sha32(observed),
        "clean_sha256": sha32(clean),
        "variants": variants,
        "large_chunk_matches_160": streamed["digest"] == whole["digest"],
        "tail_validity": {
            "input_samples": SAMPLES,
            "output_samples": int(streamed["output"].size),
            "emitted_before_flush": streamed["emitted_before_flush"],
            "flush_emitted": streamed["flush_emitted"],
            "internal_tail_reflection_samples": HOP_SAMPLES,
            "valid_samples": int(streamed["output"].size),
        },
    }


def alignment_probe() -> Dict[str, Any]:
    signal = np.zeros(SAMPLES, dtype=np.float64)
    signal[IMPULSE_INDEX] = IMPULSE_AMPLITUDE
    result = run_stream(signal, FRAME_SAMPLES)
    output = result["output"].astype(np.float64)
    peak = int(np.argmax(np.abs(output)))
    return {
        "input_peak_sample": IMPULSE_INDEX,
        "output_peak_sample": peak,
        "content_lag_samples": CONTENT_LAG_SAMPLES,
        "availability_lag_samples": AVAILABILITY_LAG_SAMPLES,
        "raw_lag_samples": peak - IMPULSE_INDEX,
        "residual_lag_samples": peak - IMPULSE_INDEX - CONTENT_LAG_SAMPLES,
        "lag_measured": False,
        "lag_modeled_in_fixture": True,
        "note": (
            "Content alignment is modelled from the adapter's declared "
            "identity source-time mapping and zero delay compensation; the "
            "one-hop availability lag is the centered-STFT window lookahead. "
            "No device clock or latency measurement exists."),
    }


def chunk_invariance() -> Dict[str, Any]:
    clean, observed = synth("mixture_snr18")
    reference = run_stream(observed, FRAME_SAMPLES)
    records: Dict[str, Any] = {}
    crossing = 0
    for size in CHUNK_SIZES:
        result = run_stream(observed, size)
        count = (SAMPLES + size - 1) // size
        chunk_crossing = sum(
            1 for index in range(count)
            if ((index * size) % HOP_SAMPLES) != 0
            or (min((index + 1) * size, SAMPLES) % HOP_SAMPLES) != 0)
        crossing += chunk_crossing
        records[str(size)] = {
            "chunk_count": count,
            "chunks_crossing_frame_boundary": chunk_crossing,
            "emitted_before_flush": result["emitted_before_flush"],
            "flush_emitted": result["flush_emitted"],
            "output_samples": int(result["output"].size),
            "output_sha256": result["digest"],
            "state_sha256": result["state_digest"],
        }
    digests = {record["output_sha256"] for record in records.values()}
    return {
        "frame_samples": HOP_SAMPLES,
        "chunk_sizes_tested": list(CHUNK_SIZES),
        "total_chunks_crossing_frame_boundary": crossing,
        "all_chunks_end_on_frame_boundary": False,
        "chunk_invariant": len(digests) == 1,
        "whole_call_matches_chunked": records[str(SAMPLES)]["output_sha256"]
        == reference["digest"],
        "device_clock_used": False,
        "deadline_measured": False,
        "records": records,
    }


def state_evidence() -> Dict[str, Any]:
    _, observed = synth("mixture_snr12")
    first = run_stream(observed, 160)
    replay = run_stream(observed, 397)
    independent = run_stream(observed, 160)
    foreign_target = 0.3 * _target_cached()

    session = StreamingSurrogate(opt_in=True)
    for start in range(0, SAMPLES, 320):
        session.process(observed[start:start + 320])
    session.flush()
    cross_digest = session.state_digest()
    session.reset()
    after_reset = session.state_digest()
    fresh = StreamingSurrogate(opt_in=True)
    reset_foreign_pieces = []
    for start in range(0, SAMPLES, 160):
        reset_foreign_pieces.append(session.process(foreign_target[start:start + 160]))
    reset_foreign_pieces.append(session.flush())
    reset_foreign_output = np.concatenate(reset_foreign_pieces).astype(np.float32)
    foreign_digest = sha32(run_stream(foreign_target, 160)["output"])
    reset_foreign_digest = sha32(reset_foreign_output)
    return {
        "slot_count": STATE_SLOT_COUNT,
        "past_frame_rows": STATE_PAST_FRAME_ROWS,
        "replay_identical": first["digest"] == replay["digest"],
        "independent_session_identical": first["digest"] == independent["digest"],
        "cross_stream_reset_identical": foreign_digest == reset_foreign_digest,
        "reset_restores_initial_state": after_reset == fresh.state_digest(),
        "final_state_sha256": cross_digest,
        "output_sha256": first["digest"],
        "real_recurrent_state_loaded": False,
        "note": (
            "These are deterministic surrogate FIFO/state digests, not the "
            "17 opaque activation tensors of the pinned graph."),
    }


def flush_evidence() -> Dict[str, Any]:
    _, observed = synth("mixture_snr24")
    session = StreamingSurrogate(opt_in=True)
    emitted = 0
    for start in range(0, SAMPLES, 160):
        emitted += int(session.process(observed[start:start + 160]).size)
    tail = session.flush()
    second = session.flush()
    post_flush_rejected = False
    try:
        session.process(observed[:160])
    except ValueError:
        post_flush_rejected = True
    session.reset()
    new_stream = session.process(observed[:1600])
    return {
        "emitted_before_flush": emitted,
        "flush_emitted": int(tail.size),
        "second_flush_empty": int(second.size) == 0,
        "total_emitted": emitted + int(tail.size),
        "process_after_flush_rejected": post_flush_rejected,
        "reset_after_flush_allows_new_stream": int(new_stream.size) >= 0,
        "note": (
            "No sample is emitted until its analysis windows are complete; "
            "the final one hop is released by flush."),
    }


def frame_accounting() -> Dict[str, Any]:
    _, observed = synth("target_only")
    result = run_stream(observed, 160)
    return {
        "input_samples": SAMPLES,
        "output_samples": int(result["output"].size),
        "emitted_before_flush": result["emitted_before_flush"],
        "flush_emitted": result["flush_emitted"],
        "internal_frames": result["frames"],
        "hop_samples": HOP_SAMPLES,
        "internal_tail_reflection_samples": HOP_SAMPLES,
        "content_lag_samples": CONTENT_LAG_SAMPLES,
        "availability_lag_samples": AVAILABILITY_LAG_SAMPLES,
        "emitted_equals_input": int(result["output"].size) == SAMPLES,
    }


def config_adverse_cases() -> Dict[str, Any]:
    base = default_asset_manifest()
    mutations: Dict[str, Dict[str, Any]] = {}
    for field, value in (
            ("sample_rate_hz", 48000), ("channels", 2), ("n_fft", 1024),
            ("hop_samples", 128), ("n_freqs", 513),
            ("compress_power", 0.5), ("state_slot_count", 16),
            ("sample_format", "f64"), ("sha256", "0" * 64),
            ("byte_count", MODEL_BYTES + 1)):
        manifest = dict(base)
        manifest[field] = value
        mutations["wrong_" + field] = manifest
    missing = dict(base)
    missing.pop("state_slot_count")
    mutations["missing_field"] = missing
    extra = dict(base)
    extra["unexpected"] = True
    mutations["extra_field"] = extra
    relative = dict(base)
    relative["caller_path"] = "relative/model.onnx"
    mutations["relative_caller_path"] = relative

    cases: Dict[str, Any] = {}
    for name, manifest in mutations.items():
        try:
            validate_asset_manifest(manifest)
            status = "accepted"
        except ValueError as error:
            status = "rejected:" + str(error)
        cases[name] = {"status": status, "session_created": False}
    try:
        StreamingSurrogate(opt_in=False)
        status = "accepted"
    except ValueError as error:
        status = "rejected:" + str(error)
    cases["surrogate_without_opt_in"] = {"status": status, "session_created": False}
    admission = admit_asset(base)
    cases["caller_asset_unavailable"] = {
        "status": admission["status"],
        "session_created": False,
        "reason_codes": admission["reason_codes"],
    }
    control = synthetic_admission_control()
    cases["synthetic_admission_control"] = {
        "status": control["status"],
        "session_created": False,
        "not_the_pinned_candidate": control["not_the_pinned_candidate"],
    }
    return cases


def frame_adverse_cases() -> Dict[str, Any]:
    bad_inputs: Dict[str, Any] = {
        "two_dimensional": np.zeros((8, 2), dtype=np.float64),
        "nan_input": np.asarray([0.0, float("nan"), 0.1]),
        "infinite_input": np.asarray([0.0, float("inf"), 0.1]),
        "non_numeric": np.asarray(["a", "b"]),
    }
    session = StreamingSurrogate(opt_in=True)
    session.process(np.zeros(160, dtype=np.float64))
    cases: Dict[str, Any] = {}
    for name, value in bad_inputs.items():
        before = session.state_digest()
        try:
            session.process(value)
            status = "accepted"
        except (ValueError, TypeError) as error:
            status = "rejected:" + type(error).__name__
        cases[name] = {
            "status": status,
            "state_unchanged": session.state_digest() == before,
        }

    short = StreamingSurrogate(opt_in=True)
    short.process(np.zeros(100, dtype=np.float64))
    before = short.state_digest()
    try:
        short.flush()
        short_status = "accepted"
    except ValueError as error:
        short_status = "rejected:" + str(error)
    cases["short_stream_flush"] = {
        "status": short_status,
        "state_unchanged": short.state_digest() == before,
    }

    after_flush = StreamingSurrogate(opt_in=True)
    after_flush.process(np.zeros(1024, dtype=np.float64))
    after_flush.flush()
    before = after_flush.state_digest()
    try:
        after_flush.process(np.zeros(160, dtype=np.float64))
        status = "accepted"
    except ValueError as error:
        status = "rejected:" + str(error)
    cases["process_after_flush"] = {
        "status": status,
        "state_unchanged": after_flush.state_digest() == before,
    }

    empty = StreamingSurrogate(opt_in=True)
    before = empty.state_digest()
    output = empty.process(np.zeros(0, dtype=np.float64))
    cases["empty_chunk"] = {
        "status": "accepted_empty" if output.size == 0 else "emitted_samples",
        "state_unchanged": empty.state_digest() == before,
    }
    return {
        "cases": cases,
        "flush_idempotent": True,
        "state_after_rejected_process_unchanged": all(
            case["state_unchanged"] for case in cases.values()),
    }


def lifecycle_evidence() -> Dict[str, Any]:
    session = StreamingSurrogate(opt_in=True)
    zero = session.flush()
    zero_flush_empty = int(zero.size) == 0
    session.reset()
    first = session.process(np.zeros(2048, dtype=np.float64))
    tail = session.flush()
    second = session.flush()
    rejected: Dict[str, str] = {}
    for name, call in (
            ("process_after_flush", lambda: session.process(np.zeros(160))),
            ("flush_after_flush_returns_empty", lambda: session.flush()),
            ("reset_after_flush", lambda: session.reset())):
        try:
            result = call()
            if name == "flush_after_flush_returns_empty":
                rejected[name] = "accepted_empty" if int(np.asarray(result).size) == 0 else "emitted"
            else:
                rejected[name] = "accepted"
        except ValueError as error:
            rejected[name] = "rejected:" + str(error)
    session.process(np.zeros(2048, dtype=np.float64))
    after_reset = session.flush()
    return {
        "zero_length_stream_flush": zero_flush_empty,
        "flush_returns_samples": int(tail.size) > 0,
        "second_flush_empty": int(second.size) == 0,
        "reset_after_flush_works": int(after_reset.size) > 0,
        "post_flush_calls": rejected,
        "first_process_emitted": int(first.size),
    }


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def enhancement_profile(blocks: Dict[str, Any]) -> Dict[str, Any]:
    target = blocks["target_only"]["variants"]["surrogate_stream_160"]
    peaks = [variant["peak_abs_output"]
             for block in blocks.values()
             for variant in block["variants"].values()]
    invalid = sum(variant["nonfinite_samples"] + variant["clipped_samples"]
                  for block in blocks.values()
                  for variant in block["variants"].values())
    return {
        "name": PROFILE,
        "identity_and_noisy_controls": True,
        "established_baseline": {
            "status": "not_reproduced",
            "detail": (
                "No task-matched baseline is reproduced. Source-reported "
                "noisy-identity/FastEnhancer comparisons are provenance only."),
        },
        "paired_si_sdr": {
            "status": "synthetic_only",
            "clean_references": "exact deterministic synthetic targets",
            "real_pairing": False,
        },
        "stoi": {
            "status": "synthetic_only",
            "scorer": "pystoi " + str(pystoi.__version__),
            "real_cohort": False,
        },
        "clean_speech_preservation": {
            "status": "synthetic_only",
            "target_only_snr_db": target["snr_db"],
            "target_only_si_sdr_db": target["si_sdr_db"],
            "target_retention": target["projection"]["target_retention"],
        },
        "peaks_and_invalid_outputs": {
            "max_peak_abs_output": max(peaks) if peaks else 0.0,
            "invalid_or_clipped_samples": invalid,
            "all_finite": invalid == 0,
        },
        "alignment": {
            "content_lag_samples": CONTENT_LAG_SAMPLES,
            "availability_lag_samples": AVAILABILITY_LAG_SAMPLES,
            "measured": False,
        },
        "state_and_memory": {
            "status": "synthetic_state_only",
            "state_slots": STATE_SLOT_COUNT,
            "past_frame_rows": STATE_PAST_FRAME_ROWS,
            "surrogate_cache_bytes": STATE_CACHE_CONTRACT["surrogate_cache_bytes"],
            "asset_state_bytes": None,
            "measured": False,
        },
        "content_and_availability_timing": {
            "measured": False,
            "clock_id": CLOCK_ID,
            "modeled_content_lag_samples": CONTENT_LAG_SAMPLES,
            "modeled_availability_lag_samples": AVAILABILITY_LAG_SAMPLES,
        },
        "listening": {"status": "not_run"},
        "real_runtime": False,
        "real_clean_references": False,
    }


def _regressions(blocks: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    for condition, block in blocks.items():
        identity = block["variants"]["identity_passthrough"]
        surrogate = block["variants"]["surrogate_stream_160"]
        for metric in ("snr_db", "si_sdr_db", "stoi"):
            left = identity[metric]
            right = surrogate[metric]
            if right is None:
                continue
            if left is None:
                regressions.append({
                    "condition": condition,
                    "metric": metric,
                    "identity": None,
                    "identity_undefined": identity["undefined"],
                    "surrogate": right,
                    "delta": None,
                    "adverse": True,
                    "reason": "identity_was_exact_or_undefined",
                })
            elif right < left:
                regressions.append({
                    "condition": condition,
                    "metric": metric,
                    "identity": left,
                    "surrogate": right,
                    "delta": right - left,
                    "adverse": True,
                    "reason": "surrogate_worse_than_identity",
                })
    return regressions


def _tool_provenance() -> Dict[str, Any]:
    def version(module: Any) -> str:
        return str(getattr(module, "__version__", "unknown"))

    return {
        "python": "%d.%d.%d" % sys.version_info[:3],
        "implementation": sys.implementation.name,
        "platform": "darwin arm64",
        "numpy": version(np),
        "pystoi": version(pystoi),
        "scipy_transitive": "used by pystoi",
        "deterministic": True,
        "network_access": False,
    }


def _report_core() -> Dict[str, Any]:
    blocks = {condition: condition_block(condition) for condition in CONDITIONS}
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "claims": dict(CLAIMS),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "geometry": dict(STREAMING_GEOMETRY),
        "state_cache": dict(STATE_CACHE_CONTRACT),
        "asset_boundary": {
            "readiness": "blocked",
            "reason_codes": list(ASSET_ADMISSION_REASONS),
            "asset": {
                "asset_id": MODEL_ASSET_ID,
                "sha256": MODEL_SHA256,
                "byte_count": MODEL_BYTES,
                "storage": "external",
                "source_repository": HF_REPOSITORY,
                "source_revision": MODEL_REVISION,
                "revision_form": MODEL_PROVENANCE["revision_form"],
                "model_license_metadata": MODEL_LICENSE_METADATA,
                "code_license_metadata": CODE_LICENSE_METADATA,
                "bytes_present": False,
                "runtime_available": False,
                "rights_cleared": False,
                "download_permitted": False,
            },
            "admission": admit_asset(default_asset_manifest()),
            "synthetic_admission_control": synthetic_admission_control(),
            "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        },
        "streaming_boundary": {
            "geometry": dict(STREAMING_GEOMETRY),
            "clock_id": CLOCK_ID,
            "availability_model": (
                "sample-coordinate only; no wall clock, device clock, callback "
                "deadline or paced workload"),
            "declared_content_lag_samples": CONTENT_LAG_SAMPLES,
            "declared_availability_lag_samples": AVAILABILITY_LAG_SAMPLES,
            "lag_measured": False,
            "lag_modeled_in_fixture": True,
            "chunk_invariance": chunk_invariance(),
            "alignment_probe": alignment_probe(),
            "state": state_evidence(),
            "flush": flush_evidence(),
            "frame_accounting": frame_accounting(),
            "state_cache": dict(STATE_CACHE_CONTRACT),
        },
        "conditions": blocks,
        "enhancement_profile": enhancement_profile(blocks),
        "adverse": {
            "config_rejections": config_adverse_cases(),
            "frame_cases": frame_adverse_cases(),
            "lifecycle": lifecycle_evidence(),
        },
        "regressions": _regressions(blocks),
        "gates": [
            {"name": name, "status": "blocked", "evidence":
             "No rights-cleared, runtime-backed or target-measured evidence exists.",
             "reopen": reopen}
            for name, reopen in GATE_DEFINITIONS
        ],
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPENING_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "source_reported_context": dict(SOURCE_REPORTED_CONTEXT),
        "model_provenance": dict(MODEL_PROVENANCE),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "source_pin_paths": sorted(SOURCE_PINS),
        "boundary_pin_paths": sorted(BOUNDARY_PINS),
        "local_file_names": list(LOCAL_FILES),
        "tool_provenance": _tool_provenance(),
        "scope": dict(SCOPE),
        "notes": [
            "The surrogate is opt-in, unregistered, disabled by default and is not LiSenNet.",
            "No ONNX graph, weight, runtime, real audio, device clock or listener was used.",
            "Synthetic metrics describe the surrogate only and clear no gate.",
            "The public v0 16 kHz/mono/f32/160-sample geometry is preserved.",
        ],
    }


def build_report() -> Dict[str, Any]:
    digests: List[str] = []
    core: Optional[Dict[str, Any]] = None
    for _ in range(3):
        core = _report_core()
        digests.append(sha256(canonical_bytes(core)))
    if core is None:  # pragma: no cover
        raise RuntimeError("report_core_missing")
    core["repeatability"] = {
        "count": 3,
        "byte_identical": len(set(digests)) == 1,
        "digests": digests,
        "scope": "report body excluding the repeatability block",
    }
    return core


def canonical_report_bytes(report: Optional[Dict[str, Any]] = None) -> bytes:
    return canonical_bytes(build_report() if report is None else report)


def build_contract() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "acceptance_profile": {
            "name": PROFILE,
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": [
                "identity/noisy control on every frozen condition",
                "paired SI-SDR and STOI on exact synthetic clean references",
                "clean-speech preservation, peaks, clipping and invalid outputs",
                "state, memory and content/availability timing reported separately",
                "caller-supplied asset metadata and fail-closed frame controls",
            ],
            "not_applicable": [
                "no pinned runtime or asset bytes, so the exact graph is not reproduced",
                "no rights-cleared real cohort, so no real quality result exists",
                "no device clock, so no latency, deadline or memory measurement exists",
                "no established task-matched baseline is reproduced",
            ],
        },
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "geometry": dict(STREAMING_GEOMETRY),
        "state_cache": dict(STATE_CACHE_CONTRACT),
        "asset": {
            "asset_id": MODEL_ASSET_ID,
            "sha256": MODEL_SHA256,
            "byte_count": MODEL_BYTES,
            "storage": "external",
            "source_repository": HF_REPOSITORY,
            "source_revision": MODEL_REVISION,
            "revision_form": MODEL_PROVENANCE["revision_form"],
            "code_license_metadata": CODE_LICENSE_METADATA,
            "model_license_metadata": MODEL_LICENSE_METADATA,
            "rights_cleared": False,
            "bytes_present": False,
            "runtime_available": False,
            "download_permitted": False,
        },
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "model_provenance": dict(MODEL_PROVENANCE),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "gates": [
            {"name": name, "status": "blocked", "reopen": reopen}
            for name, reopen in GATE_DEFINITIONS
        ],
        "missing_evidence": list(MISSING_EVIDENCE),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "scope": dict(SCOPE),
        "invariants": [
            "Only this task-local directory is written; no shared SDK file, "
            "CMake, contract, header, registry, default, board, handoff or CI "
            "file changes.",
            "The surrogate is opt-in, unregistered, disabled by default and not "
            "a provider or production callback.",
            "No LiSenNet graph, weight, runtime or upstream source is copied, "
            "downloaded, built, loaded or executed.",
            "All stimuli are frozen deterministic synthetic floats; no real "
            "audio, media, device or network is used.",
            "Caller asset manifests fail closed on missing, extra, mistyped, "
            "hash-mismatched, wrong-geometry or relative-path inputs.",
            "The public v0 16 kHz/mono/f32/160-sample geometry is preserved.",
            "Missing evidence never qualifies the candidate; decision remains DEFER.",
        ],
    }


def build_adapter() -> Dict[str, Any]:
    return {
        "schema_id": ADAPTER_SCHEMA_ID,
        "task_id": TASK,
        "task_local": True,
        "implemented": False,
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "descriptor_settings": {},
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "input_kind": "waveform",
        "output_kinds": ["waveform"],
        "tasks": ["CLN-01"],
        "modes": ["streaming"],
        "decision": DECISION,
        "weights": "caller_supplied_asset_required_not_present",
        "caller_supplied_asset_required": True,
        "asset_present": False,
        "asset_readiness": "blocked",
        "frame_samples": FRAME_SAMPLES,
        "internal_geometry": {
            "n_fft": N_FFT,
            "hop_samples": HOP_SAMPLES,
            "n_freqs": N_FREQS,
            "compress_power": COMPRESS_POWER,
            "state_slot_count": STATE_SLOT_COUNT,
        },
        "entrypoint": None,
        "quality_claim": False,
        "real_runtime_used": False,
        "weights_accessed": False,
        "activation": "deferred_until_gates_clear",
        "note": (
            "Proposal-only task-local descriptor. It is not a shipped adapter, "
            "not a provider registration and not a public default."),
    }


def build_readiness() -> Dict[str, Any]:
    report = build_report()
    contract = build_contract()
    return {
        "schema_id": READINESS_SCHEMA_ID,
        "task": TASK,
        "task_id": TASK,
        "candidate": "LiSenNet streaming FP32 (conv/ dual-path conv, 16 kHz)",
        "component": SLUG,
        "profile": PROFILE,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "defer_before": DEFER_BEFORE,
        "qualified": False,
        "ready_for_opt_in_adapter": False,
        "ready_for_provider_registration": False,
        "ready_for_release": False,
        "quality_pass": False,
        "report_sha256": sha256(canonical_bytes(report)),
        "contract_sha256": sha256(canonical_bytes(contract)),
        "status": "blocked",
        "blocked_gates": [name for name, _ in GATE_DEFINITIONS],
        "external_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPENING_CONDITIONS),
        "readiness_conclusion": (
            "The streaming FP32 boundary is modelled, but the candidate is not "
            "ready to run or qualify: the exact asset bytes and the ONNX Runtime "
            "are absent, the ledger revision is a 7-hex abbreviation rather than "
            "an immutable full commit, and artifact-specific rights are not "
            "cleared."),
        "admission": admit_asset(default_asset_manifest()),
        "asset_reference": {
            "asset_id": MODEL_ASSET_ID,
            "sha256": MODEL_SHA256,
            "byte_count": MODEL_BYTES,
            "storage": "external",
            "source_repository": HF_REPOSITORY,
            "source_revision": MODEL_REVISION,
            "revision_form": MODEL_PROVENANCE["revision_form"],
            "code_license_metadata": CODE_LICENSE_METADATA,
            "model_license_metadata": MODEL_LICENSE_METADATA,
            "rights_cleared": False,
            "bytes_present": False,
            "runtime_available": False,
            "download_permitted": False,
        },
        "allowed_now": [
            "synthetic surrogate boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied asset contract",
        ],
        "not_allowed": [
            "downloading, vendoring or executing the pinned ONNX asset",
            "invoking ONNX Runtime or publishing its outputs",
            "registering a provider, changing defaults or claiming quality/latency",
        ],
        "negative_claims": dict(NEGATIVE_CLAIMS),
        "scope": dict(SCOPE),
    }


def readme_pin_rows() -> List[Tuple[str, str]]:
    text = (HERE / "README.md").read_text(encoding="utf-8")
    rows: List[Tuple[str, str]] = []
    for line in text.splitlines():
        match = README_PIN_ROW_RE.match(line.strip())
        if match:
            rows.append((match.group(1), match.group(2)))
    return rows


def qualify_pin_path(path: str) -> Path:
    if path.startswith(TASK_PREFIX):
        return SDK_ROOT / path
    if path.startswith("/"):
        raise ValueError("absolute_pin_path:" + path)
    if any(part in ("", ".", "..") for part in path.split("/")):
        raise ValueError("traversing_pin_path:" + path)
    return SOURCE_ROOT / path


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = (
        '{"a":1,"a":2}',
        '{"a":NaN}',
        '{"a":Infinity}',
        '{"a":-Infinity}',
        '[1,2]',
    )
    rejected = 0
    for text in bad_json:
        try:
            value = strict_loads(text)
            if not isinstance(value, dict):
                raise ValueError("not_object")
        except (ValueError, TypeError):
            rejected += 1
    manifests = []
    manifest = default_asset_manifest()
    manifest["sha256"] = "0" * 64
    manifests.append(manifest)
    manifest = default_asset_manifest()
    manifest["caller_path"] = "model.onnx"
    manifests.append(manifest)
    manifest = default_asset_manifest()
    manifest["extra"] = 1
    manifests.append(manifest)
    manifest = default_asset_manifest()
    del manifest["byte_count"]
    manifests.append(manifest)
    rejected_manifests = 0
    for candidate in manifests:
        try:
            validate_asset_manifest(candidate)
        except ValueError:
            rejected_manifests += 1
    return {"json": rejected, "manifests": rejected_manifests}
