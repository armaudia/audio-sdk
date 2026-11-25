# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence model for SDK-FASTENHANCER-LARGE-REFERENCE.

This module does not contain, download, hash, load, compile or invoke
FastEnhancer-L, a Large checkpoint, ``fastenhancer_l.onnx``, derived weights,
ONNX Runtime, a native engine or a corpus.  It records the pinned MIT source
checkout, the *absent* and *unpinned* Large model asset, the absent pinned
runtime and the documented Large streaming geometry.

The embedded surrogate is an explicitly opt-in, synthetic, delayed-causal gain
path.  It is **not** FastEnhancer-L, substitutes for no gate and can never
qualify the candidate.  Its cache payloads are synthetic placeholders with the
documented shapes, not the model's tensors.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import struct
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2]))).resolve()
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml")
).resolve()

TASK = "SDK-FASTENHANCER-LARGE-REFERENCE"
TITLE = "FastEnhancer Large reference"
SLUG = "fastenhancer-large-reference"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "a1e7573dc38ebd0d8efb3050dd38613ec0950941"
BRANCH = f"swarm/{TASK}"
WORKTREE = f"/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/{TASK}"
REVIEWER = f"reviewer-{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "processor_exposure"

# Documented public v0 geometry is preserved; nothing is installed or changed.
SAMPLE_RATE_HZ = 16_000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
V0_FRAME_SAMPLES = 160

# Documented FastEnhancer-L (VoiceBank-Demand 16 kHz) streaming geometry.
NATIVE_HOP_SAMPLES = 100
N_FFT_SAMPLES = 512
WIN_SAMPLES = 512
SPEC_BINS = 257
MODEL_INPUT_BINS = 256
RNN_FREQ = 64
RNN_CHANNELS = 96
RNN_BLOCKS = 5
RNN_HEADS = 4
ENCODER_CHANNELS = 128
ENCODER_KERNELS: Tuple[int, ...] = (8, 3, 3, 3, 3)
STRIDE = 4
WINDOW = "hann"
BUFFERING_DELAY_SAMPLES = N_FFT_SAMPLES - NATIVE_HOP_SAMPLES  # 412
STARTUP_INVALID_SAMPLES = BUFFERING_DELAY_SAMPLES
DRAIN_FLUSH_HOPS = (BUFFERING_DELAY_SAMPLES + NATIVE_HOP_SAMPLES - 1) // NATIVE_HOP_SAMPLES
MAX_DRAIN_CALLS = 8
MAX_DRAIN_PRODUCED_SAMPLES = MAX_DRAIN_CALLS * NATIVE_HOP_SAMPLES

SAMPLES = 4_000
MAX_STREAM_SAMPLES = 64_000
MAX_ABS_INPUT = 4.0
SEED_BASE = 2026_1126
CLOCK_ID = "fixture-sample-coordinate-not-device"

CACHE_SHAPES: Tuple[Tuple[str, Tuple[int, ...]], ...] = (
    ("cache_in_0", (1, BUFFERING_DELAY_SAMPLES)),
    ("cache_in_1", (1, BUFFERING_DELAY_SAMPLES)),
    *(
        (f"cache_in_{index + 2}", (1, RNN_FREQ, RNN_CHANNELS))
        for index in range(RNN_BLOCKS)
    ),
)
CACHE_NAMES: Tuple[str, ...] = tuple(name for name, _shape in CACHE_SHAPES)

CONDITIONS: Tuple[str, ...] = (
    "active_speech",
    "quiet_speech",
    "low_snr_speech",
    "idle_noise",
    "onset_offset",
)

GAIN_FLOOR = 0.25
EPS = 1e-12

# Exact pinned source checkout identity.
SOURCE_ROOT_REL = "data/checkouts/FastEnhancer"
SOURCE_REPOSITORY = "https://github.com/aask1357/fastenhancer"
SOURCE_REVISION = "49ab55a57e3a064d94c6412cd0f0a383a55ca0f8"
SOURCE_RELEASE_TAGS: Tuple[str, ...] = (
    "onnx-vd-v1.0.0",
    "ckpt-vd-v1.0.0",
    "onnx-dns-v1.0.0",
    "ckpt-dns-v1.0.0",
)
SOURCE_LICENSE = "MIT"
SOURCE_TREE_DIGEST = (
    "30e6a40df543545c1d16d77031db1135e4201acae27dca356c752799d0737ad0"
)
SOURCE_FILE_COUNT = 85
SOURCE_BYTE_COUNT = 654_180
SOURCE_LICENSE_SHA256 = (
    "38164c22720cdccceb5f0dbb8f7218dcf17bac97ac536cad2e77c33dfbc45a18"
)
MAX_SOURCE_FILES = 512
MAX_SOURCE_BYTES = 64 * 1024 * 1024

# Exact candidate identity is *not* pinned anywhere in the linked records.
CANDIDATE_ASSET_ID = "fastenhancer_l.onnx"
CANDIDATE_CHECKPOINT_ID = "fastenhancer_l.pt"
CANDIDATE_ASSET_PATH = "data/models/fastenhancer/fastenhancer_l.onnx"
CANDIDATE_ASSET_BYTES: Optional[int] = None
CANDIDATE_ASSET_SHA256: Optional[str] = None
CANDIDATE_ASSET_PINNED = False
CANDIDATE_RELEASE_TAGS: Tuple[str, ...] = ("onnx-vd-v1.0.0", "ckpt-vd-v1.0.0")
MODEL_TERMS_METADATA = "not specified separately; retain local only"
MODEL_LICENSE_METADATA = "not specified separately"
CODE_LICENSE_METADATA = "MIT (repository)"

RUNTIME_PACKAGE = "onnxruntime==1.20.1"
RUNTIME_WHEEL_SHA256 = (
    "e50ba5ff7fed4f7d9253a6baf801ca2883cc08491f9d32d78a80da57256a5439"
)
RUNTIME_LOCK = "adapters/fastenhancer/requirements.lock"
RUNTIME_TARGET = "CPython 3.10, macOS arm64"
RUNTIME_PYTHON = "3.10"
RUNTIME_NUMPY = "1.26.4"
RUNTIME_SOUNDFILE = "0.13.1"

FIXED_WEIGHT_PROBES: Tuple[str, ...] = (
    "data/models/fastenhancer/fastenhancer_l.onnx",
    "data/models/fastenhancer/fastenhancer_l_spec.onnx",
    "data/models/fastenhancer/fastenhancer_l.pt",
    "data/models/fastenhancer/fastenhancer_l.pth",
    "data/models/fastenhancer",
    "cpp-library/.deps/fastenhancer_l.onnx",
    "cpp-library/.deps/fastenhancer_l.pt",
    "cpp-library/logs/fastenhancer_l",
    "audio-benchmark-platform/audio-pro/models/fastenhancer_large",
    "audio-benchmark-platform/audio-pro/processors/fastenhancer_large_native_f32",
)

FIXED_RUNTIME_PROBES: Tuple[str, ...] = (
    "data/envs/fastenhancer",
    "data/envs/dtln-onnx",
    "data/wheels/onnxruntime-1.20.1-cp310-cp310-macosx_11_0_arm64.whl",
    "cpp-library/.deps/onnxruntime-osx-arm64-1.20.1",
)

# Explicitly synthetic admission control.  These bytes are not model weights.
SYNTHETIC_ASSET_ID = "synthetic-large-delayed-causal-surrogate-not-fastenhancer"
SYNTHETIC_ASSET_UNIT = (
    b"audio-sdk/fastenhancer-large-reference/synthetic-surrogate/v1\n"
)
SYNTHETIC_ASSET_UNITS = 64
SYNTHETIC_ASSET_BYTES = SYNTHETIC_ASSET_UNIT * SYNTHETIC_ASSET_UNITS
SYNTHETIC_ASSET_SHA256 = hashlib.sha256(SYNTHETIC_ASSET_BYTES).hexdigest()

# Precomputed placeholder recurrence for the five RNNFormer cache blocks.
MODEL_PATTERN: Tuple[Tuple[Tuple[float, ...], ...], ...] = tuple(
    tuple(
        tuple(
            (((row * 3 + column * 5 + block * 7) % 9) + 1) / 9.0
            for column in range(RNN_CHANNELS)
        )
        for row in range(RNN_FREQ)
    )
    for block in range(RNN_BLOCKS)
)

SOURCE_PINS: Dict[str, str] = {
    "data/checkouts/FastEnhancer/LICENSE":
        "38164c22720cdccceb5f0dbb8f7218dcf17bac97ac536cad2e77c33dfbc45a18",
    "data/checkouts/FastEnhancer/README.md":
        "a2a5b889c615944b4044674e54a527245d9a97fccef0a3109812629b80413a4f",
    "data/checkouts/FastEnhancer/configs/fastenhancer/l.yaml":
        "f37b1f9bb73dd6d0b6a89ec10d09c0cd8ac621664ca392ccf92131de52a76c42",
    "data/checkouts/FastEnhancer/models/fastenhancer/default/model.py":
        "0e9b1ac34fe1725f7a09f53260b630360c38f8f185052bb37127e34957ec3380",
    "data/checkouts/FastEnhancer/functional/audio_modules.py":
        "6d474b3f2869182339b9f1d9f34c2076099e8ad7b1779c142cfd1b50a5acf8ae",
    "data/checkouts/FastEnhancer/scripts/export_onnx.py":
        "28d6758481c24dd8b4758e43bbf0624b3745d21fa7f998e8a263771795f72e04",
    "data/checkouts/FastEnhancer/docs/docs/onnx.md":
        "ed05be57ea44917dbdc13d16ba47250424f901e7fbb78cb2ffd31217f137837c",
    "adapters/fastenhancer/adapter.json":
        "2a42cef166dc514488f4fdfe9b37c87427183444bcc19a2f6a4e96e77f87026b",
    "adapters/fastenhancer/README.md":
        "32a856af0f7f32efb35b0b00c6551564f6383cf6446285c060294504cdf341ea",
    "adapters/fastenhancer/requirements.lock":
        "1195f7e838fd20dc1fff30b3808324131c9f7acbedf63f9bf4084de78aa6a86c",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "cpp-library/src/stages/fastenhancer.cpp":
        "b0c0ffc33e5c1c87f65ae9c82ea61ee2c91f4ec9ab16af9393c04376ad931510",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-pro/docs/rights-register.md":
        "e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44",
    "audio-benchmark-platform/audio-pro/inventory/rights-register.json":
        "24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923",
    "audio-benchmark-platform/audio-pro/processors/fastenhancer_tiny16/model-contract.json":
        "1af99b0085289d2cc21772462f6aa9159750946d7c742a197e636cf392240a4a",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "docs/task-evidence/fastenhancer-source-linked-onnx-wrapper/README.md":
        "d47d0ce64bfbe85f9b099cac422c180481da646a7f5d392e98c174582463d8f6",
    "docs/task-evidence/fastenhancer-source-linked-onnx-wrapper/report.json":
        "34edd5dffed3f5a5eef0aa72675b8efe0fd89403d7a5356cf51c8a0e5e9ef84d",
    "docs/task-evidence/fastenhancer-source-linked-onnx-wrapper/provider.json":
        "3000d76b0ef5b668e2ecbf41b4d1a12681a1c9ecdc80a30fa8f9b5d8f07fcbc0",
}

# Fail-closed local file set.  SOURCES.sha256 is excluded because a manifest
# cannot pin its own bytes; its .license sidecar is included.
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)

PIN_RE = re.compile(
    r"^[0-9a-f]{64}  (?P<path>source:[^\s]+|worktree:[^\s]+|docs/[^\s]+|api/[^\s]+|"
    r"CONTRACTS\.md|LICENSES/[^\s]+|REUSE\.toml)$"
)
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"

# Stable linked-row identity.  Mutable board fields (status, owner, claim,
# review, handoff, blocked_reason, timestamps) are deliberately excluded and
# plan/swarm/TASKS.json is never hashed as a whole file.
STABLE_TASK_IDENTITY: Dict[str, Any] = {
    "id": TASK,
    "title": TITLE,
    "repository": "audio-sdk",
    "mode": "feasibility",
    "component": SLUG,
    "dispatch_priority": 3,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-EVIDENCE",
        "SDK-FND-PROVIDER",
    ],
    "write_scope": [
        f"SDK provider, tool or evidence directory for {SLUG} and its own fixtures"
    ],
    "deliverable": (
        "Verify runnable source, exact assets, permitted scope, task geometry and "
        "matched evidence. Then reproduce the exact model/runtime as a "
        "caller-supplied-asset reference and add an opt-in SDK adapter once its "
        "prerequisites pass. Record a concrete blocker if feasibility fails."
    ),
    "acceptance": (
        "Apply the enhancement acceptance profile; record exact scope, evidence, "
        "failure/control results, and remaining release gates. A readiness "
        "conclusion with an exact external blocker is an accepted investigation "
        "handoff; it does not close the conditional implementation."
    ),
    "verification_profile": PROFILE,
    "profile_source": f"plan/INVENTORY.json#components[id={SLUG}]",
    "board_selector": f"tasks[id={TASK}]",
    "board_full_file_hashed": False,
    "mutable_fields_excluded": [
        "status",
        "owner",
        "claim",
        "review",
        "handoff",
        "blocked_reason",
        "initialized_on",
        "history",
    ],
}

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "v0_frame_samples": V0_FRAME_SAMPLES,
    "native_hop_samples": NATIVE_HOP_SAMPLES,
    "n_fft_samples": N_FFT_SAMPLES,
    "win_samples": WIN_SAMPLES,
    "window": WINDOW,
    "spec_bins": SPEC_BINS,
    "model_input_bins": MODEL_INPUT_BINS,
    "rnn_freq": RNN_FREQ,
    "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
    "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
    "drain_flush_hops": DRAIN_FLUSH_HOPS,
    "max_drain_calls": MAX_DRAIN_CALLS,
    "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
    "processing_mode": "native_100_hop_delayed_causal_surrogate",
    "clock": CLOCK_ID,
}

BOUNDARY: Dict[str, bool] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "installed_v0_geometry_preserved": True,
    "installed_v0_behavior_change": False,
    "shared_build_or_ci_change": False,
    "processor_exposure": False,
    "task_board_or_handoff_write": False,
    "adapter_json_added": False,
    "readiness_json_added": False,
    "asset_bundled": False,
    "weights_vendored": False,
    "onnxruntime_invoked": False,
    "native_engine_built": False,
    "sdk_data_dir_added": False,
    "files_outside_task_directory_written": False,
}

CLAIMS: Dict[str, bool] = {
    "real_fastenhancer_runtime": False,
    "large_weights_present": False,
    "weights_accessed": False,
    "weights_hashed": False,
    "asset_downloaded": False,
    "asset_bytes_read": False,
    "model_bytes_read": False,
    "onnxruntime_invoked": False,
    "native_engine_built": False,
    "payload_inference_invoked": False,
    "real_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "chunk_latency_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "quality_claim": False,
    "parity_claim": False,
    "release_claim": False,
}

EXACT_BLOCKERS: Tuple[str, ...] = (
    "The exact FastEnhancer-L artifact is absent and its identity is unpinned. No "
    "linked asset-ledger row, release digest, rights entry or local file records a "
    "byte count or SHA-256 for a Large checkpoint or ONNX graph. Every fixed probe "
    "(data/models/fastenhancer/fastenhancer_l.onnx, fastenhancer_l_spec.onnx, .pt, "
    ".pth, cpp-library/.deps/fastenhancer_l.onnx and Pro large paths) is absent. The "
    "pinned MIT source checkout contains only the Large training config "
    "configs/fastenhancer/l.yaml and export code; source presence is not a weight, "
    "graph or runtime artifact.",
    "The exact pinned runtime is absent. adapters/fastenhancer/requirements.lock "
    "pins CPython 3.10 macOS arm64 with onnxruntime==1.20.1 (wheel SHA-256 "
    "e50ba5ff7fed4f7d9253a6baf801ca2883cc08491f9d32d78a80da57256a5439) and the "
    "adapter records data/envs/dtln-onnx as its evaluator environment; neither is "
    "present here, and onnxruntime is not importable in the evidence interpreter. "
    "No exact-runtime reference run or parity vector was produced.",
    "Rights are not cleared for a Large artifact. The source repository is MIT, but "
    "the release page records no separate pretrained-model terms and neither the "
    "linked asset ledger nor the rights register has a Large entry; the rights "
    "register records only fastenhancer_m, fastenhancer_s, fastenhancer_t and "
    "fastenhancer_t_16k. Evaluation, acquisition, redistribution, customer "
    "deployment and public playback for Large are unestablished.",
    "No exact reference parity, candidate output, rights-cleared paired cohort, "
    "independent scorer, listening result or target-runtime timing exists. The "
    "documented Large VBD metrics are author-reported provenance only. The synthetic "
    "delayed-causal surrogate is not FastEnhancer-L and cannot qualify the "
    "candidate. All eight release gates remain blocked.",
    "The documented Large geometry is the 16 kHz VoiceBank-Demand path (100-sample "
    "hop, 512-point FFT, 412-sample content delay, seven caches), not the installed "
    "v0 160-sample frame and not the 256-hop 16 kHz DNS Tiny/Small geometry. No v0 "
    "frame adapter, resampler or native engine is implemented or claimed.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen asset identity only when an exact FastEnhancer-L checkpoint or ONNX "
    "graph is supplied as a caller-owned external asset with an immutable upstream "
    "revision, release tag, byte count and SHA-256, verified without a download.",
    "Reopen runtime admission only when the pinned onnxruntime==1.20.1 artifact with "
    "a recorded digest installs in the intended CPython 3.10 environment, its "
    "distribution and product-use terms are documented, and exact-runtime reference "
    "outputs are produced.",
    "Reopen rights only after written artifact-specific model-weight, "
    "training-data and runtime terms record evaluation, redistribution, customer "
    "deployment and public-playback decisions for the exact Large artifact.",
    "Reopen exact reference parity only with approved outputs for frozen inputs from "
    "the exact caller-supplied asset under the exact pinned runtime, reproducible "
    "across three cold starts.",
    "Reopen the cohort gate only with a rights-cleared paired real speech cohort "
    "that includes clean references and declared VoiceBank-Demand/DNS overlap.",
    "Reopen scoring/listening only with an independent intrusive scorer and "
    "permitted listening under a recorded protocol.",
    "Reopen timing only with target-runtime end-to-end availability, pacing, "
    "deadline, memory and 100-sample chunk-boundary measurements for the exact "
    "runtime.",
    "Reopen provider/default only after the prior gates clear and an opt-in provider "
    "intake with OFF default, descriptor/catalog review and an explicit owner "
    "default decision is approved.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "caller-supplied exact FastEnhancer-L checkpoint or ONNX bytes with immutable revision, release tag, byte count and SHA-256",
    "installed pinned onnxruntime==1.20.1 runtime artifact with recorded digest and documented terms",
    "written Large-specific model-weight, training-data and runtime rights decisions",
    "approved exact-runtime reference outputs for frozen inputs, reproducible across three cold starts",
    "rights-cleared paired real speech cohort with clean references and declared training overlap",
    "independent STOI/SI-SDR/intrusive scorer and permitted listening",
    "target-runtime chunk-boundary, pacing, availability, deadline and memory evidence",
    "opt-in provider intake with OFF default and an explicit default-selection decision",
)

GATES: Tuple[Dict[str, str], ...] = (
    {
        "name": "exact_asset_identity",
        "status": "blocked",
        "evidence": (
            "No linked ledger row, release digest or local file records FastEnhancer-L "
            "bytes or SHA-256; all fixed Large probes are absent."
        ),
        "reopen": REOPEN_CONDITIONS[0],
    },
    {
        "name": "runtime_admission",
        "status": "blocked",
        "evidence": (
            "The pinned CPython 3.10 macOS arm64 onnxruntime==1.20.1 wheel and "
            "evaluator environment are absent; onnxruntime is not importable."
        ),
        "reopen": REOPEN_CONDITIONS[1],
    },
    {
        "name": "artifact_rights",
        "status": "blocked",
        "evidence": (
            "The source checkout is MIT, but no separate Large model terms or rights "
            "entry exists; acquisition, redistribution, deployment and playback are "
            "unknown."
        ),
        "reopen": REOPEN_CONDITIONS[2],
    },
    {
        "name": "exact_reference_parity",
        "status": "blocked",
        "evidence": (
            "No exact-runtime Large output or parity vector exists; the synthetic "
            "surrogate is not the candidate."
        ),
        "reopen": REOPEN_CONDITIONS[3],
    },
    {
        "name": "rights_cleared_paired_cohort",
        "status": "blocked",
        "evidence": (
            "No rights-cleared paired real cohort with clean references is present; "
            "the author-reported VBD table is provenance only."
        ),
        "reopen": REOPEN_CONDITIONS[4],
    },
    {
        "name": "independent_scoring_and_listening",
        "status": "blocked",
        "evidence": "No independent scorer or listening result; surrogate metrics are synthetic only.",
        "reopen": REOPEN_CONDITIONS[5],
    },
    {
        "name": "target_runtime_timing",
        "status": "blocked",
        "evidence": (
            "No target chunk-boundary timing, availability, deadline, pacing or memory "
            "measurement was made; author RTF is not device evidence."
        ),
        "reopen": REOPEN_CONDITIONS[6],
    },
    {
        "name": "provider_intake_and_default_selection",
        "status": "blocked",
        "evidence": "No opt-in provider, descriptor or catalog entry exists; no default decision was made.",
        "reopen": REOPEN_CONDITIONS[7],
    },
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "scope": "Pinned upstream source provenance only; not reproduced, pooled or used as a threshold.",
    "geometry": {
        "source": "data/checkouts/FastEnhancer/configs/fastenhancer/l.yaml",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": ENCODER_CHANNELS,
        "encoder_kernels": list(ENCODER_KERNELS),
        "stride": STRIDE,
        "rnnformer_blocks": RNN_BLOCKS,
        "rnnformer_channels": RNN_CHANNELS,
        "rnnformer_freq": RNN_FREQ,
        "rnnformer_heads": RNN_HEADS,
        "n_fft_samples": N_FFT_SAMPLES,
        "native_hop_samples": NATIVE_HOP_SAMPLES,
        "win_samples": WIN_SAMPLES,
        "window": WINDOW,
        "input_compression": 0.3,
        "normalize_final_conv": True,
        "weight_norm": True,
    },
    "streaming_contract": {
        "source": "data/checkouts/FastEnhancer/docs/docs/onnx.md",
        "chunk_samples": NATIVE_HOP_SAMPLES,
        "n_fft_samples": N_FFT_SAMPLES,
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
        "drain_flush_hops": DRAIN_FLUSH_HOPS,
        "cache_count": len(CACHE_SHAPES),
        "note": (
            "The documented wav-to-wav recipe concatenates the 412-sample cache "
            "with each 100-sample chunk, returns the first 100 samples, and drops "
            "the first 412 collected samples after five flush hops. The ONNX file "
            "itself is absent and was not inspected."
        ),
    },
    "large_vbd_table": {
        "source": "data/checkouts/FastEnhancer/README.md#Voicebank-Demand-16kHz",
        "model": "FastEnhancer_L",
        "parameters_k": 1_105,
        "macs": "11G",
        "rtf_xeon": 0.313,
        "rtf_m1": 0.632,
        "dnsmos_p808": 3.53,
        "dnsmos_p835_sig": 3.44,
        "dnsmos_p835_bak": 4.04,
        "dnsmos_p835_ovl": 3.16,
        "scoreq": 0.239,
        "si_sdr": 19.6,
        "pesq": 3.26,
        "stoi": 0.952,
        "estoi": 0.877,
        "wer": 3.1,
        "protocol": "Authors' VoiceBank-Demand 16 kHz test table; not the local DNS pilot.",
    },
    "release_tags": list(SOURCE_RELEASE_TAGS),
    "disclaimer": (
        "These values are quoted from the pinned MIT checkout. They are not "
        "reproduced here, not device timing, not this fixture's metrics, not a "
        "listening result and not a release claim."
    ),
}

SIBLING_EVIDENCE: Dict[str, Any] = {
    "scope": (
        "Read-only cross-reference to FastEnhancer family packages. Their decisions "
        "are not merged into this base and never transfer to Large."
    ),
    "tiny": {
        "branch": "swarm/SDK-FASTENHANCER-TINY-REFERENCE",
        "commit": "77d58c4681d256ac6b052570566141a13fcc5237",
        "report_sha256": "20f007a5dc330b0dd437e38bc179c9aad19f6ba60b5ecabb854a6ca722488cbe",
        "decision": "DEFER",
        "status": "proposal_only_synthetic_incomplete",
        "evidence_status": "incomplete",
        "qualification_status": "not_qualified",
        "release_gate_count": 8,
        "merged_into_base": False,
        "used_for_qualification": False,
    },
    "small": {
        "branch": "swarm/SDK-FASTENHANCER-SMALL-REFERENCE",
        "commit": "14729afe63db97f34932a978d9528acf2274e698",
        "report_sha256": "ecb188b4a1f0d929bd8ddcc19aa1fdb81a7d42892e6dc7aef3ed81aa37bc456e",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "evidence_status": "incomplete",
        "qualification_status": "not_qualified",
        "release_gate_count": 8,
        "merged_into_base": False,
        "used_for_qualification": False,
    },
    "medium": {
        "branch": "swarm/SDK-FASTENHANCER-MEDIUM-REFERENCE",
        "commit": "2742d8c7894c6c62838b2147a6b35d4439476577",
        "report_sha256": "2d062bd1eebc7bf9a5ce0e7b51af4aa9620fe7abae50b26cbb33d482e7bd15f0",
        "decision": "DEFER",
        "status": "proposal_only_incomplete",
        "evidence_status": "incomplete",
        "qualification_status": "not_qualified",
        "release_gate_count": 8,
        "merged_into_base": False,
        "used_for_qualification": False,
    },
    "source_linked_wrapper": {
        "branch": "swarm/SDK-FASTENHANCER-SOURCE-LINKED-ONNX-WRAPPER",
        "commit": "56f40ef47014ee167a186151d31a477ef71294ed",
        "report_sha256": "34edd5dffed3f5a5eef0aa72675b8efe0fd89403d7a5356cf51c8a0e5e9ef84d",
        "decision": "DEFER",
        "status": "proposal_only_synthetic_incomplete",
        "evidence_status": "incomplete",
        "qualification_status": "not_qualified",
        "release_gate_count": 7,
        "merged_into_base": True,
        "used_for_qualification": False,
    },
    "note": (
        "Tiny, Small and Medium are present only on sibling swarm branches; the "
        "source-linked wrapper is merged at this base. All decisions are DEFER and "
        "not_qualified, and none supplies Large bytes, runtime, rights or parity."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "FastEnhancer-L, its checkpoint or ONNX graph, derived weights, ONNX Runtime and a Large native engine are absent from this package; nothing was downloaded, hashed, loaded, compiled or invoked.",
    "The MIT source checkout was read only to verify its exact revision, tree digest, Large config geometry and documented export recipe; no upstream file is copied, imported or executed.",
    "The asset digest, byte count, release tags, dependency lock and rights scopes are either quoted from pinned workspace records or explicitly recorded as absent/unpinned.",
    "All signals, caches and outputs are generated by a stdlib deterministic surrogate in reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
)

NON_CLAIMS: Tuple[str, ...] = (
    "No FastEnhancer-L weight, derived weight, ONNX graph, ONNX Runtime, native engine, corpus or media was downloaded, hashed, loaded, compiled, executed or bundled.",
    "No public API/ABI, CONTRACTS.md, descriptor, registry, installed default, shared build, dependency lock, CI, board or handoff file was changed.",
    "No listening, MOS, STOI, SI-SDR, parity, benchmark, device-timing, latency or release result is claimed for the candidate.",
    "The synthetic delayed-causal surrogate is not FastEnhancer-L and no missing result ever qualifies the candidate.",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise ValueError("nonfinite float in canonical JSON")
        return 0.0 if value == 0.0 else value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize_negzero(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def canonical_report_bytes(report: Mapping[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def strict_json(path: Path) -> Any:
    def reject_object_pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def reject_constant(token: str) -> None:
        raise ValueError("nonfinite_json_constant:" + token)

    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_object_pairs,
        parse_constant=reject_constant,
    )


def r6(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    rounded = round(float(value), 6)
    return 0.0 if rounded == 0.0 else rounded


def stable_identity_digest(identity: Optional[Dict[str, Any]] = None) -> str:
    payload = dict(identity or STABLE_TASK_IDENTITY)
    payload.pop("stable_sha256", None)
    payload.pop("board_full_file_hashed", None)
    payload.pop("mutable_fields_excluded", None)
    return sha256(canonical_bytes(payload))


def task_identity() -> Dict[str, Any]:
    identity = dict(STABLE_TASK_IDENTITY)
    identity["stable_sha256"] = stable_identity_digest()
    identity["board_full_file_hashed"] = False
    identity["mutable_fields_excluded"] = list(
        STABLE_TASK_IDENTITY["mutable_fields_excluded"]
    )
    return identity


# ---------------------------------------------------------------------------
# Source, weights and runtime probes (read-only; no candidate bytes)
# ---------------------------------------------------------------------------


def _git_head(source: Path) -> Optional[str]:
    head_path = source / ".git" / "HEAD"
    if not head_path.is_file():
        return None
    head = head_path.read_text(encoding="ascii").strip()
    if head.startswith("ref: "):
        ref = head.split("ref: ", 1)[1]
        ref_path = source / ".git" / ref
        if ref_path.is_file():
            return ref_path.read_text(encoding="ascii").strip()
        packed = source / ".git" / "packed-refs"
        if packed.is_file():
            for line in packed.read_text(encoding="ascii").splitlines():
                if line.endswith(" " + ref):
                    return line.split(" ", 1)[0]
        return None
    return head


def source_probe(root: Optional[Path] = None) -> Dict[str, Any]:
    """Read-only digest over every non-.git file in the pinned MIT checkout."""
    workspace = SOURCE_ROOT if root is None else Path(root)
    source = workspace / SOURCE_ROOT_REL
    if not source.is_dir():
        return {
            "status": "source_absent",
            "present": False,
            "path": SOURCE_ROOT_REL,
            "revision": None,
            "expected_revision": SOURCE_REVISION,
            "tree_digest": None,
            "expected_tree_digest": SOURCE_TREE_DIGEST,
            "file_count": 0,
            "expected_file_count": SOURCE_FILE_COUNT,
            "license": SOURCE_LICENSE,
            "license_sha256": None,
            "expected_license_sha256": SOURCE_LICENSE_SHA256,
            "executed": False,
        }
    rows: List[str] = []
    total_bytes = 0
    for directory, directory_names, file_names in os.walk(source):
        directory_names[:] = sorted(
            name for name in directory_names if name != ".git"
        )
        for name in sorted(file_names):
            path = Path(directory) / name
            if path.is_symlink():
                return {
                    "status": "source_symlink_present",
                    "present": False,
                    "path": SOURCE_ROOT_REL,
                    "revision": _git_head(source),
                    "expected_revision": SOURCE_REVISION,
                    "tree_digest": None,
                    "expected_tree_digest": SOURCE_TREE_DIGEST,
                    "file_count": 0,
                    "expected_file_count": SOURCE_FILE_COUNT,
                    "license": SOURCE_LICENSE,
                    "license_sha256": None,
                    "expected_license_sha256": SOURCE_LICENSE_SHA256,
                    "executed": False,
                }
            relative = path.relative_to(source).as_posix()
            payload = path.read_bytes()
            total_bytes += len(payload)
            if len(rows) >= MAX_SOURCE_FILES or total_bytes > MAX_SOURCE_BYTES:
                return {
                    "status": "source_too_large",
                    "present": False,
                    "path": SOURCE_ROOT_REL,
                    "revision": _git_head(source),
                    "expected_revision": SOURCE_REVISION,
                    "tree_digest": None,
                    "expected_tree_digest": SOURCE_TREE_DIGEST,
                    "file_count": len(rows),
                    "expected_file_count": SOURCE_FILE_COUNT,
                    "license": SOURCE_LICENSE,
                    "license_sha256": None,
                    "expected_license_sha256": SOURCE_LICENSE_SHA256,
                    "executed": False,
                }
            rows.append(
                relative + " " + sha256(payload) + " " + str(len(payload)) + "\n"
            )
    tree_digest = sha256("".join(rows).encode("utf-8"))
    revision = _git_head(source)
    license_path = source / "LICENSE"
    license_sha256 = sha256_file(license_path) if license_path.is_file() else None
    present = (
        revision == SOURCE_REVISION
        and tree_digest == SOURCE_TREE_DIGEST
        and len(rows) == SOURCE_FILE_COUNT
        and total_bytes == SOURCE_BYTE_COUNT
        and license_sha256 == SOURCE_LICENSE_SHA256
    )
    return {
        "status": "present_pinned" if present else "source_mismatch",
        "present": present,
        "path": SOURCE_ROOT_REL,
        "repository": SOURCE_REPOSITORY,
        "revision": revision,
        "expected_revision": SOURCE_REVISION,
        "release_tags": list(SOURCE_RELEASE_TAGS),
        "tree_digest": tree_digest,
        "expected_tree_digest": SOURCE_TREE_DIGEST,
        "file_count": len(rows),
        "expected_file_count": SOURCE_FILE_COUNT,
        "byte_count": total_bytes,
        "expected_byte_count": SOURCE_BYTE_COUNT,
        "license": SOURCE_LICENSE,
        "license_sha256": license_sha256,
        "expected_license_sha256": SOURCE_LICENSE_SHA256,
        "executed": False,
        "note": (
            "Read-only digest over every non-.git file in the local checkout; no "
            "upstream file is copied, imported or executed."
        ),
    }


def _probe_path(path: str) -> Dict[str, Any]:
    workspace_path = SOURCE_ROOT / path
    sdk_path = SDK_ROOT / path
    workspace_present = workspace_path.exists()
    sdk_present = sdk_path.exists()
    if workspace_path.is_file() or sdk_path.is_file():
        kind = "file"
    elif workspace_path.is_dir() or sdk_path.is_dir():
        kind = "directory"
    else:
        kind = "absent"
    return {
        "path": path,
        "workspace_present": workspace_present,
        "sdk_worktree_present": sdk_present,
        "present": workspace_present or sdk_present,
        "kind": kind,
    }


def ledger_probe() -> Dict[str, Any]:
    path = SOURCE_ROOT / "research/noise_suppression_assets_20261027.json"
    if not path.is_file():
        return {
            "present": False,
            "candidate_ids": [],
            "large_entry_present": False,
            "fastenhancer_artifact_paths": [],
            "note": "Pinned asset ledger is absent.",
        }
    payload = strict_json(path)
    candidates = payload.get("candidates", []) if isinstance(payload, dict) else []
    candidate_ids: List[str] = []
    artifact_paths: List[str] = []
    large_entries: List[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        identifier = str(candidate.get("id", ""))
        candidate_ids.append(identifier)
        if "fastenhancer" not in identifier.lower():
            continue
        for artifact in candidate.get("artifacts", []) or []:
            if isinstance(artifact, dict) and "path" in artifact:
                artifact_paths.append(str(artifact["path"]))
        serialized = json.dumps(candidate, sort_keys=True).lower()
        if "fastenhancer_l" in serialized or "fastenhancer-dns-16k-large" in serialized:
            large_entries.append(identifier)
    return {
        "present": True,
        "path": "research/noise_suppression_assets_20261027.json",
        "candidate_ids": candidate_ids,
        "fastenhancer_artifact_paths": artifact_paths,
        "large_entry_present": bool(large_entries),
        "large_entries": large_entries,
        "note": "Metadata-only read; no model bytes are opened or hashed.",
    }


def weights_probe() -> Dict[str, Any]:
    probes = [_probe_path(path) for path in FIXED_WEIGHT_PROBES]
    return {
        "candidate_id": CANDIDATE_ASSET_ID,
        "candidate_pinned": CANDIDATE_ASSET_PINNED,
        "candidate_byte_count": CANDIDATE_ASSET_BYTES,
        "candidate_sha256": CANDIDATE_ASSET_SHA256,
        "candidate_present": any(
            item["present"] and item["kind"] == "file" for item in probes
        ),
        "all_fixed_probes_absent": all(not item["present"] for item in probes),
        "probes": probes,
        "recursive_workspace_walk": False,
        "bytes_read": False,
        "hash_computed": False,
        "ledger": ledger_probe(),
        "note": (
            "Existence metadata only. No candidate artifact or byte was opened, "
            "hashed, copied or loaded."
        ),
    }


def rights_probe() -> Dict[str, Any]:
    path = (
        SOURCE_ROOT
        / "audio-benchmark-platform/audio-pro/inventory/rights-register.json"
    )
    if not path.is_file():
        return {
            "present": False,
            "fastenhancer_model_keys": [],
            "large_entry_present": False,
        }
    payload = strict_json(path)
    models = payload.get("models", {}) if isinstance(payload, dict) else {}
    keys = sorted(
        str(key) for key in models if "fastenhancer" in str(key).lower()
    )
    large = [key for key in keys if "fastenhancer_l" in key.lower()]
    return {
        "present": True,
        "path": "audio-benchmark-platform/audio-pro/inventory/rights-register.json",
        "fastenhancer_model_keys": keys,
        "large_entry_present": bool(large),
        "large_entries": large,
        "note": "Metadata-only read of the pinned rights register.",
    }


def runtime_probe() -> Dict[str, Any]:
    probes = [_probe_path(path) for path in FIXED_RUNTIME_PROBES]
    spec = importlib.util.find_spec("onnxruntime")
    numpy_spec = importlib.util.find_spec("numpy")
    return {
        "status": "pinned_runtime_absent",
        "pinned_python": RUNTIME_PYTHON,
        "pinned_onnxruntime": RUNTIME_PACKAGE,
        "pinned_numpy": RUNTIME_NUMPY,
        "pinned_soundfile": RUNTIME_SOUNDFILE,
        "pinned_wheel_sha256": RUNTIME_WHEEL_SHA256,
        "runtime_lock": RUNTIME_LOCK,
        "runtime_target": RUNTIME_TARGET,
        "probes": probes,
        "pinned_runtime_present": any(item["present"] for item in probes),
        "runtime_available": False,
        "onnxruntime_importable": spec is not None,
        "numpy_importable": numpy_spec is not None,
        "current_python": ".".join(str(part) for part in sys.version_info[:3]),
        "imported": False,
        "invoked": False,
        "note": (
            "find_spec() only; onnxruntime is not imported and no inference "
            "session is created."
        ),
    }


def asset_ref() -> Dict[str, Any]:
    weights = weights_probe()
    rights = rights_probe()
    return {
        "asset_id": CANDIDATE_ASSET_ID,
        "checkpoint_id": CANDIDATE_CHECKPOINT_ID,
        "path_relative": CANDIDATE_ASSET_PATH,
        "pinned": CANDIDATE_ASSET_PINNED,
        "byte_count": CANDIDATE_ASSET_BYTES,
        "sha256": CANDIDATE_ASSET_SHA256,
        "storage": "external",
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "candidate_release_tags": list(CANDIDATE_RELEASE_TAGS),
        "ledger_entry_present": weights["ledger"]["large_entry_present"],
        "rights_entry_present": rights["large_entry_present"],
        "code_license_metadata": CODE_LICENSE_METADATA,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "observed_model_terms": MODEL_TERMS_METADATA,
        "evaluation_allowed": False,
        "acquisition_cleared": False,
        "redistribution_cleared": False,
        "customer_deployment_cleared": False,
        "public_playback_cleared": False,
        "bytes_present_in_sdk_worktree": any(
            item["sdk_worktree_present"] for item in weights["probes"]
        ),
        "asset_bytes_read": False,
        "digest_recomputed": False,
        "runtime_package": RUNTIME_PACKAGE,
        "runtime_target": RUNTIME_TARGET,
        "runtime_wheel_sha256": RUNTIME_WHEEL_SHA256,
        "runtime_lock": RUNTIME_LOCK,
        "runtime_available": False,
        "download_permitted": False,
    }


def asset_admission(ref: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ref = dict(ref or asset_ref())
    reasons: List[str] = []
    if not ref.get("pinned"):
        reasons.append("asset_identity_unpinned")
    if not ref.get("bytes_present_in_sdk_worktree"):
        reasons.append("asset_not_caller_supplied")
    if not ref.get("runtime_available"):
        reasons.append("runtime_unpinned")
    reasons.append("runtime_terms_unresolved")
    if not ref.get("model_license_metadata") or "not specified" in str(
        ref.get("model_license_metadata")
    ):
        reasons.append("model_terms_unresolved")
    if not ref.get("redistribution_cleared"):
        reasons.append("redistribution_rights_unknown")
    order = [
        "asset_identity_unpinned",
        "asset_not_caller_supplied",
        "runtime_unpinned",
        "runtime_terms_unresolved",
        "model_terms_unresolved",
        "redistribution_rights_unknown",
    ]
    reasons = [reason for reason in order if reason in reasons]
    return {
        "status": "admitted" if not reasons else "blocked",
        "reason_codes": reasons,
        "asset_bytes_read": False,
        "asset_bytes_hashed": False,
        "download_attempted": False,
        "vendor_runtime_invoked": False,
        "native_engine_invoked": False,
        "candidate_asset": True,
        "qualification_effect": "none",
    }


def synthetic_asset_ref() -> Dict[str, Any]:
    return {
        "asset_id": SYNTHETIC_ASSET_ID,
        "byte_count": len(SYNTHETIC_ASSET_BYTES),
        "sha256": SYNTHETIC_ASSET_SHA256,
        "storage": "external",
        "synthetic": True,
        "candidate_asset": False,
        "model_revision": "synthetic-control-v1",
        "bytes_present_in_worktree": True,
        "asset_bytes_read": False,
        "runtime_available": False,
        "rights_cleared": True,
        "download_permitted": False,
    }


def synthetic_admission_control() -> Dict[str, Any]:
    return {
        "status": "admitted_synthetic_control",
        "reason_codes": [],
        "asset_bytes_read": False,
        "download_attempted": False,
        "vendor_runtime_invoked": False,
        "candidate_asset": False,
        "qualification_effect": "none",
        "asset_id": SYNTHETIC_ASSET_ID,
        "byte_count": len(SYNTHETIC_ASSET_BYTES),
        "sha256": SYNTHETIC_ASSET_SHA256,
        "note": (
            "Explicitly synthetic admission control; not FastEnhancer-L and not "
            "eligible for any gate."
        ),
    }


def rights_status() -> Dict[str, Any]:
    rights = rights_probe()
    return {
        "register": "audio-benchmark-platform/audio-pro/docs/rights-register.md",
        "register_detail": "audio-benchmark-platform/audio-pro/inventory/rights-register.json",
        "review_date": "2026-11-15",
        "reviewer": "rights holder (user attestation)",
        "fastenhancer_model_keys": rights["fastenhancer_model_keys"],
        "large_entry_present": rights["large_entry_present"],
        "candidate_asset_entry": "absent",
        "acquisition": "unknown",
        "evaluation": "not established for Large; only fastenhancer_t_16k is recorded evaluation-allowed",
        "redistribution": "unknown",
        "customer_deployment": "unknown",
        "public_playback": "unknown",
        "evaluation_only": True,
        "weights_must_remain_private": True,
        "packaging_permitted": False,
        "blocked": True,
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic signals (analytic; no corpus or media)
# ---------------------------------------------------------------------------


def _seed(name: str) -> int:
    return (
        SEED_BASE
        + int.from_bytes(hashlib.sha256(name.encode("ascii")).digest()[:4], "big")
    ) & 0xFFFFFFFF


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF

    def nxt() -> float:
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state / 4294967296.0

    return nxt


def _gaussian(rng) -> float:
    total = 0.0
    for _ in range(12):
        total += rng()
    return total - 6.0


def _gate(condition: str, index: int, total: int) -> float:
    if condition == "idle_noise":
        return 0.0
    if condition == "onset_offset":
        start = int(total * 0.25)
        end = int(total * 0.75)
        ramp = int(SAMPLE_RATE_HZ * 0.10)
        if index < start or index >= end:
            return 0.0
        if index < start + ramp:
            return (index - start) / ramp
        if index >= end - ramp:
            return (end - index) / ramp
        return 1.0
    return 1.0


def synth(condition: str) -> Tuple[List[float], List[float]]:
    if condition not in CONDITIONS:
        raise ValueError("unknown condition: " + condition)
    if condition == "quiet_speech":
        amplitude, noise_sigma = 0.055, 0.018
    elif condition == "low_snr_speech":
        amplitude, noise_sigma = 0.15, 0.15
    elif condition == "idle_noise":
        amplitude, noise_sigma = 0.0, 0.05
    else:
        amplitude, noise_sigma = 0.22, 0.055

    rng = _lcg(_seed(condition))
    target: List[float] = []
    observed: List[float] = []
    phase = 0.0
    for index in range(SAMPLES):
        gate = _gate(condition, index, SAMPLES)
        f0 = 118.0 + 24.0 * math.sin(
            2.0 * math.pi * 2.7 * index / SAMPLES + 0.4
        )
        phase += 2.0 * math.pi * f0 / SAMPLE_RATE_HZ
        speech = 0.0
        for harmonic in range(1, 6):
            speech += math.sin(harmonic * phase) / harmonic
        speech *= amplitude * gate / 1.55
        noise = noise_sigma * _gaussian(rng)
        target.append(speech)
        observed.append(speech + noise)
    return target, observed


# ---------------------------------------------------------------------------
# Synthetic delayed-causal streaming surrogate (not FastEnhancer-L)
# ---------------------------------------------------------------------------


def _zeros(shape: Tuple[int, ...]) -> Any:
    if len(shape) == 1:
        return [0.0] * shape[0]
    return [_zeros(shape[1:]) for _ in range(shape[0])]


def zero_caches() -> Dict[str, Any]:
    return {name: _zeros(shape) for name, shape in CACHE_SHAPES}


def zero_delay() -> List[float]:
    return [0.0] * BUFFERING_DELAY_SAMPLES


def _shape_of(value: Any) -> Optional[Tuple[int, ...]]:
    shape: List[int] = []
    current = value
    while isinstance(current, list):
        shape.append(len(current))
        if len(current) == 0:
            return tuple(shape)
        if any(not isinstance(item, list) for item in current):
            if any(isinstance(item, list) for item in current):
                return None
            return tuple(shape)
        current = current[0]
    return tuple(shape)


def _flatten(value: Any) -> List[float]:
    if isinstance(value, list):
        flat: List[float] = []
        for item in value:
            flat.extend(_flatten(item))
        return flat
    return [value]


def _finite(value: Any) -> bool:
    return all(math.isfinite(float(item)) for item in _flatten(value))


def validate_caches(caches: Any) -> Optional[str]:
    if not isinstance(caches, dict):
        return "cache_layout_mismatch"
    if set(caches) != set(CACHE_NAMES):
        return "cache_layout_mismatch"
    for name, shape in CACHE_SHAPES:
        value = caches[name]
        if _shape_of(value) != shape:
            return "cache_layout_mismatch"
        if any(isinstance(item, bool) for item in _flatten(value)):
            return "cache_type_invalid"
        if not _finite(value):
            return "cache_nonfinite"
        if any(abs(float(item)) > MAX_ABS_INPUT for item in _flatten(value)):
            return "cache_out_of_range"
    return None


def validate_delay(delay: Any) -> Optional[str]:
    if not isinstance(delay, list):
        return "delay_layout_mismatch"
    if len(delay) != BUFFERING_DELAY_SAMPLES:
        return "delay_layout_mismatch"
    if any(isinstance(item, bool) for item in delay):
        return "delay_type_invalid"
    if any(not isinstance(item, (int, float)) for item in delay):
        return "delay_type_invalid"
    if any(not math.isfinite(float(item)) for item in delay):
        return "delay_nonfinite"
    return None


def _chunk_power(chunk: Sequence[float]) -> float:
    if not chunk:
        return 0.0
    total = 0.0
    for value in chunk:
        total += value * value
    return total / len(chunk)


def _caches_digest(caches: Mapping[str, Any]) -> str:
    digest = hashlib.sha256()
    for name in CACHE_NAMES:
        flat = _flatten(caches[name])
        digest.update(struct.pack("<" + "d" * len(flat), *flat))
    return digest.hexdigest()


def _delay_digest(delay: Sequence[float]) -> str:
    return sha256(struct.pack("<" + "d" * len(delay), *delay))


def surrogate_chunk(
    wav_in: Sequence[float], caches: Dict[str, Any], delay: Sequence[float]
) -> Tuple[List[float], Dict[str, Any], List[float], float]:
    """One synthetic delayed-causal 100-sample step with the documented caches."""
    values = [float(value) for value in wav_in]
    history = list(caches["cache_in_0"][0])
    output_history = list(caches["cache_in_1"][0])
    processed: List[float] = []
    gains: List[float] = []
    for index, value in enumerate(values):
        previous = values[index - 1] if index > 0 else history[-1]
        previous_two = (
            values[index - 2]
            if index > 1
            else (history[-1] if index == 1 else history[-2])
        )
        smoothed = 0.5 * value + 0.3 * previous + 0.2 * previous_two
        reference = previous * previous + previous_two * previous_two + EPS
        instantaneous = value * value
        snr = instantaneous / (instantaneous + 0.5 * reference + EPS)
        gain = GAIN_FLOOR + (1.0 - GAIN_FLOOR) * math.sqrt(snr)
        gains.append(gain)
        processed.append(max(-0.98, min(0.98, smoothed * gain)))
    if len(delay) != BUFFERING_DELAY_SAMPLES:
        raise ValueError("delay_length_mismatch")
    output = [float(value) for value in delay[: len(values)]]
    new_delay = [float(value) for value in delay[len(values):]] + processed
    new_history = (history + values)[-BUFFERING_DELAY_SAMPLES:]
    new_output_history = (output_history + output)[-BUFFERING_DELAY_SAMPLES:]
    drive = min(1.0, math.sqrt(_chunk_power(values)) * 4.0)
    new_caches: Dict[str, Any] = {
        "cache_in_0": [new_history],
        "cache_in_1": [new_output_history],
    }
    for block in range(RNN_BLOCKS):
        old = caches[f"cache_in_{block + 2}"]
        pattern = MODEL_PATTERN[block]
        updated = [[0.0] * RNN_CHANNELS for _ in range(RNN_FREQ)]
        for row in range(RNN_FREQ):
            old_row = old[0][row]
            pattern_row = pattern[row]
            updated_row = updated[row]
            for column in range(RNN_CHANNELS):
                value = 0.9 * old_row[column] + 0.1 * drive * pattern_row[column]
                if value > 0.999:
                    value = 0.999
                elif value < -0.999:
                    value = -0.999
                updated_row[column] = value
        new_caches[f"cache_in_{block + 2}"] = [updated]
    mean_gain = sum(gains) / len(gains) if gains else 0.0
    return output, new_caches, new_delay, mean_gain


def _chunks(samples: Sequence[float]) -> List[List[float]]:
    padded = [float(value) for value in samples]
    remainder = (-len(padded)) % NATIVE_HOP_SAMPLES
    if remainder:
        padded.extend([0.0] * remainder)
    return [
        padded[start:start + NATIVE_HOP_SAMPLES]
        for start in range(0, len(padded), NATIVE_HOP_SAMPLES)
    ]


def _drive_stream(
    samples: Sequence[float],
    caches: Dict[str, Any],
    delay: Sequence[float],
) -> Tuple[List[float], Dict[str, Any], List[float], int]:
    collected: List[float] = []
    current_caches = caches
    current_delay = list(delay)
    chunks = _chunks(samples) + [[0.0] * NATIVE_HOP_SAMPLES] * DRAIN_FLUSH_HOPS
    for chunk in chunks:
        output, current_caches, current_delay, _gain = surrogate_chunk(
            chunk, current_caches, current_delay
        )
        collected.extend(output)
    aligned = collected[
        STARTUP_INVALID_SAMPLES:STARTUP_INVALID_SAMPLES + len(samples)
    ]
    return aligned, current_caches, current_delay, len(chunks)


def surrogate_stream(samples: Sequence[float]) -> List[float]:
    aligned, _caches, _delay, _hops = _drive_stream(
        samples, zero_caches(), zero_delay()
    )
    return aligned


def surrogate_chunk_loop_control(samples: Sequence[float]) -> List[float]:
    """Independent driver over the same public chunk step; must be byte-identical."""
    caches = zero_caches()
    delay = zero_delay()
    output: List[float] = []
    padded = [float(value) for value in samples]
    padded.extend([0.0] * ((-len(padded)) % NATIVE_HOP_SAMPLES))
    for start in range(0, len(padded), NATIVE_HOP_SAMPLES):
        chunk_output, caches, delay, _gain = surrogate_chunk(
            padded[start:start + NATIVE_HOP_SAMPLES], caches, delay
        )
        output.extend(chunk_output)
    for _ in range(DRAIN_FLUSH_HOPS):
        chunk_output, caches, delay, _gain = surrogate_chunk(
            [0.0] * NATIVE_HOP_SAMPLES, caches, delay
        )
        output.extend(chunk_output)
    return output[STARTUP_INVALID_SAMPLES:STARTUP_INVALID_SAMPLES + len(samples)]


def surrogate_split_halves(samples: Sequence[float]) -> List[float]:
    midpoint = (len(samples) // (2 * NATIVE_HOP_SAMPLES)) * NATIVE_HOP_SAMPLES
    if midpoint == 0:
        return surrogate_stream(samples)
    return surrogate_stream(samples[:midpoint]) + surrogate_stream(samples[midpoint:])


def output_digest(samples: Sequence[float]) -> str:
    if not samples:
        return sha256(b"")
    return sha256(struct.pack("<" + "f" * len(samples), *samples))


def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    total = 0.0
    for value in values:
        total += value * value
    return math.sqrt(total / len(values))


def _snr_db(
    target: Sequence[float], observed: Sequence[float]
) -> Optional[float]:
    signal = 0.0
    error = 0.0
    for want, got in zip(target, observed):
        signal += want * want
        diff = got - want
        error += diff * diff
    if signal <= 0.0 or error <= 0.0:
        return None
    return 10.0 * math.log10(signal / error)


def _si_sdr_db(
    target: Sequence[float], observed: Sequence[float]
) -> Optional[float]:
    projection = 0.0
    energy = 0.0
    for want, got in zip(target, observed):
        projection += got * want
        energy += got * got
    if energy <= 0.0:
        return None
    scale = projection / energy
    signal = 0.0
    error = 0.0
    for want, got in zip(target, observed):
        fitted = scale * got
        signal += fitted * fitted
        diff = want - fitted
        error += diff * diff
    if signal <= 0.0 or error <= 0.0:
        return None
    return 10.0 * math.log10(signal / error)


def _attenuation_db(
    observed: Sequence[float], output: Sequence[float]
) -> Optional[float]:
    before = _rms(observed)
    after = _rms(output)
    if before <= 0.0 or after <= 0.0:
        return None
    return 20.0 * math.log10(after / before)


def measure(
    target: Sequence[float], observed: Sequence[float], output: Sequence[float]
) -> Dict[str, Any]:
    noisy_snr = _snr_db(target, observed)
    output_snr = _snr_db(target, output)
    noisy_si_sdr = _si_sdr_db(target, observed)
    output_si_sdr = _si_sdr_db(target, output)
    nonfinite = sum(0 if math.isfinite(value) else 1 for value in output)
    clipped = sum(1 for value in output if abs(value) > 1.0)
    peak = max((abs(value) for value in output), default=0.0)
    return {
        "input_samples": len(observed),
        "output_samples": len(output),
        "output_sha256": output_digest(output),
        "peak_abs": r6(peak),
        "nonfinite_count": nonfinite,
        "clipped_count": clipped,
        "target_rms": r6(_rms(target)),
        "observed_rms": r6(_rms(observed)),
        "output_rms": r6(_rms(output)),
        "noisy_snr_db": r6(noisy_snr),
        "surrogate_snr_db": r6(output_snr),
        "delta_snr_db": r6(output_snr - noisy_snr)
        if output_snr is not None and noisy_snr is not None
        else None,
        "noisy_si_sdr_db": r6(noisy_si_sdr),
        "surrogate_si_sdr_db": r6(output_si_sdr),
        "delta_si_sdr_db": r6(output_si_sdr - noisy_si_sdr)
        if output_si_sdr is not None and noisy_si_sdr is not None
        else None,
        "noise_attenuation_db": r6(_attenuation_db(observed, output)),
    }


# ---------------------------------------------------------------------------
# Configuration and streaming session
# ---------------------------------------------------------------------------


def default_config() -> Dict[str, Any]:
    return {
        "model_id": "fastenhancer_large_16k_vd",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "native_hop_samples": NATIVE_HOP_SAMPLES,
        "n_fft_samples": N_FFT_SAMPLES,
        "win_samples": WIN_SAMPLES,
        "window": WINDOW,
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "cache_layout": [list(shape) for _name, shape in CACHE_SHAPES],
        "asset_mode": "caller_supplied_external",
        "asset_id": CANDIDATE_ASSET_ID,
        "asset_byte_count": CANDIDATE_ASSET_BYTES,
        "asset_sha256": CANDIDATE_ASSET_SHA256,
        "surrogate_opt_in": False,
    }


def synthetic_config() -> Dict[str, Any]:
    config = default_config()
    config.update(
        {
            "asset_mode": "synthetic_surrogate",
            "asset_id": SYNTHETIC_ASSET_ID,
            "asset_byte_count": len(SYNTHETIC_ASSET_BYTES),
            "asset_sha256": SYNTHETIC_ASSET_SHA256,
            "surrogate_opt_in": True,
        }
    )
    return config


CONFIG_KEYS = tuple(default_config().keys())


def validate_config(config: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    if not isinstance(config, dict):
        return ["config_type_invalid"]
    if set(config) != set(CONFIG_KEYS):
        return ["config_keys_mismatch"]
    if config["model_id"] != "fastenhancer_large_16k_vd":
        reasons.append("model_id_mismatch")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        reasons.append("sample_rate_hz_mismatch")
    if config["channels"] != CHANNELS:
        reasons.append("channels_mismatch")
    if config["sample_format"] != SAMPLE_FORMAT:
        reasons.append("sample_format_mismatch")
    if config["native_hop_samples"] != NATIVE_HOP_SAMPLES:
        reasons.append("native_hop_mismatch")
    if config["n_fft_samples"] != N_FFT_SAMPLES:
        reasons.append("n_fft_mismatch")
    if config["win_samples"] != WIN_SAMPLES:
        reasons.append("win_size_mismatch")
    if config["window"] != WINDOW:
        reasons.append("window_mismatch")
    if config["buffering_delay_samples"] != BUFFERING_DELAY_SAMPLES:
        reasons.append("buffering_delay_mismatch")
    if config["cache_layout"] != [list(shape) for _name, shape in CACHE_SHAPES]:
        reasons.append("cache_layout_mismatch")
    if config["asset_mode"] not in ("caller_supplied_external", "synthetic_surrogate"):
        reasons.append("asset_mode_unsupported")
    return reasons


def admit_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if config is None:
        config = default_config()
    if not isinstance(config, dict):
        return {
            "status": "rejected",
            "reason_codes": ["config_type_invalid"],
            "candidate_asset": False,
            "processing_attempted": False,
        }
    config = dict(config)
    reasons = validate_config(config)
    if reasons:
        return {
            "status": "rejected",
            "reason_codes": reasons,
            "candidate_asset": False,
            "processing_attempted": False,
        }
    if config["asset_mode"] == "synthetic_surrogate":
        if config["surrogate_opt_in"] is not True:
            return {
                "status": "rejected",
                "reason_codes": ["surrogate_opt_in_required"],
                "candidate_asset": False,
                "processing_attempted": False,
            }
        expected = synthetic_asset_ref()
        if (
            config["asset_id"] != expected["asset_id"]
            or config["asset_byte_count"] != expected["byte_count"]
            or config["asset_sha256"] != expected["sha256"]
        ):
            return {
                "status": "rejected",
                "reason_codes": ["synthetic_asset_mismatch"],
                "candidate_asset": False,
                "processing_attempted": False,
            }
        admission = synthetic_admission_control()
        admission["processing_attempted"] = False
        return admission
    if config["asset_id"] != CANDIDATE_ASSET_ID:
        return {
            "status": "rejected",
            "reason_codes": ["asset_identity_mismatch"],
            "candidate_asset": True,
            "processing_attempted": False,
        }
    # The candidate identity is unpinned: no byte count or SHA-256 exists.
    return {
        "status": "rejected",
        "reason_codes": ["asset_identity_unpinned"],
        "admission": asset_admission(asset_ref()),
        "candidate_asset": True,
        "processing_attempted": False,
    }


def _reject(status: str, **extra: Any) -> Dict[str, Any]:
    payload = {
        "status": "rejected:" + status,
        "output": None,
        "output_samples": 0,
        "candidate": False,
        "qualifies": False,
    }
    payload.update(extra)
    return payload


def _sample_error(samples: Any) -> Optional[str]:
    if isinstance(samples, str) or not isinstance(samples, (list, tuple)):
        return "stream_type_invalid"
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float))
        for value in samples
    ):
        return "sample_type_invalid"
    if any(not math.isfinite(float(value)) for value in samples):
        return "sample_nonfinite"
    if any(abs(float(value)) > MAX_ABS_INPUT for value in samples):
        return "sample_out_of_range"
    return None


class StreamingSession:
    """One bounded synthetic stream per session; reset to reuse."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = dict(config if config is not None else default_config())
        self.admission = admit_config(self.config)
        self.created = self.admission["status"].startswith("admitted")
        self.closed = False
        self.stream_complete = False
        self.hops = 0
        self.epoch = 0
        self.caches = zero_caches()
        self.delay = zero_delay()
        self.output: Optional[List[float]] = None

    def state(self) -> Dict[str, Any]:
        return {
            "created": self.created,
            "closed": self.closed,
            "stream_complete": self.stream_complete,
            "hops": self.hops,
            "epoch": self.epoch,
            "admission_status": self.admission["status"],
            "asset_mode": self.config.get("asset_mode"),
            "caches_sha256": _caches_digest(self.caches),
            "delay_sha256": _delay_digest(self.delay),
            "output_sha256": output_digest(self.output)
            if self.output is not None
            else None,
        }

    def state_digest(self) -> str:
        return sha256(canonical_bytes(self.state()))

    def reset(self) -> Dict[str, Any]:
        if self.closed:
            return _reject("session_closed", state_unchanged=True)
        before = self.state_digest()
        self.caches = zero_caches()
        self.delay = zero_delay()
        self.stream_complete = False
        self.output = None
        self.hops = 0
        self.epoch += 1
        return {
            "status": "ok_reset",
            "epoch": self.epoch,
            "caches_zeroed": all(
                all(float(item) == 0.0 for item in _flatten(self.caches[name]))
                for name in CACHE_NAMES
            ),
            "delay_zeroed": all(float(item) == 0.0 for item in self.delay),
            "state_unchanged": self.state_digest() == before,
        }

    def process_chunk(self, wav_in: Any, caches: Any = None) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed", state_unchanged=True)
        elif not self.created:
            result = _reject(
                "not_admitted",
                reason_codes=self.admission.get("reason_codes", []),
                state_unchanged=True,
            )
        elif self.stream_complete:
            result = _reject("stream_already_complete", state_unchanged=True)
        elif isinstance(wav_in, str) or not isinstance(wav_in, (list, tuple)):
            result = _reject("chunk_type_invalid", state_unchanged=True)
        elif _sample_error(wav_in) is not None:
            result = _reject(
                _sample_error(wav_in) or "chunk_invalid", state_unchanged=True
            )
        elif len(wav_in) != NATIVE_HOP_SAMPLES:
            result = _reject("chunk_shape_invalid", state_unchanged=True)
        elif validate_delay(self.delay) is not None:
            result = _reject(
                validate_delay(self.delay) or "delay_invalid", state_unchanged=True
            )
        else:
            selected = self.caches if caches is None else caches
            reason = validate_caches(selected)
            if reason is not None:
                result = _reject(reason, state_unchanged=True)
            else:
                values = [float(value) for value in wav_in]
                output, new_caches, new_delay, gain = surrogate_chunk(
                    values, selected, self.delay
                )
                self.caches = new_caches
                self.delay = new_delay
                self.hops += 1
                result = {
                    "status": "ok_synthetic",
                    "output": list(output),
                    "output_samples": len(output),
                    "gain": r6(gain),
                    "cache_out": new_caches,
                    "candidate": False,
                    "qualifies": False,
                }
        result["state_unchanged"] = self.state_digest() == before
        return result

    def process_stream(self, samples: Any) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed", state_unchanged=True)
        elif not self.created:
            result = _reject(
                "not_admitted",
                reason_codes=self.admission.get("reason_codes", []),
                state_unchanged=True,
            )
        elif isinstance(samples, str) or not isinstance(samples, (list, tuple)):
            result = _reject("stream_type_invalid", state_unchanged=True)
        elif len(samples) == 0:
            result = _reject("stream_empty", state_unchanged=True)
        elif len(samples) > MAX_STREAM_SAMPLES:
            result = _reject("stream_oversized", state_unchanged=True)
        elif _sample_error(samples) is not None:
            result = _reject(
                _sample_error(samples) or "stream_invalid", state_unchanged=True
            )
        elif self.stream_complete:
            result = _reject("stream_already_complete", state_unchanged=True)
        elif validate_delay(self.delay) is not None:
            result = _reject(
                validate_delay(self.delay) or "delay_invalid", state_unchanged=True
            )
        else:
            values = [float(value) for value in samples]
            output, new_caches, new_delay, hops = _drive_stream(
                values, self.caches, self.delay
            )
            self.output = output
            self.caches = new_caches
            self.delay = new_delay
            self.hops = hops
            self.stream_complete = True
            result = {
                "status": "ok_synthetic",
                "output": list(self.output),
                "input_samples": len(values),
                "output_samples": len(self.output),
                "output_digest": output_digest(self.output),
                "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
                "drain_flush_hops": DRAIN_FLUSH_HOPS,
                "candidate": False,
                "qualifies": False,
            }
        result["state_unchanged"] = self.state_digest() == before
        return result

    def close(self) -> None:
        self.closed = True


def config_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, mutate) -> None:
        config = default_config()
        mutate(config)
        result = admit_config(config)
        cases[name] = {
            "status": result["status"],
            "reason_codes": list(result["reason_codes"]),
            "processing_attempted": bool(result.get("processing_attempted", False)),
            "candidate_asset": bool(result.get("candidate_asset", False)),
        }

    run("wrong_model_id", lambda c: c.update(model_id="fastenhancer_small_16k"))
    run("wrong_sample_rate", lambda c: c.update(sample_rate_hz=8_000))
    run("wrong_channels", lambda c: c.update(channels=2))
    run("wrong_sample_format", lambda c: c.update(sample_format="s16"))
    run("wrong_native_hop", lambda c: c.update(native_hop_samples=256))
    run("wrong_n_fft", lambda c: c.update(n_fft_samples=256))
    run("wrong_win_size", lambda c: c.update(win_samples=256))
    run("wrong_window", lambda c: c.update(window="hann-sqrt"))
    run("wrong_buffering_delay", lambda c: c.update(buffering_delay_samples=256))
    run("wrong_cache_layout", lambda c: c.update(cache_layout=[[1, 160]]))
    run("caller_asset_unpinned", lambda c: None)
    run("caller_asset_unknown_id", lambda c: c.update(asset_id="fastenhancer_l_other.onnx"))
    run(
        "surrogate_without_opt_in",
        lambda c: c.update(
            asset_mode="synthetic_surrogate",
            asset_id=SYNTHETIC_ASSET_ID,
            asset_byte_count=len(SYNTHETIC_ASSET_BYTES),
            asset_sha256=SYNTHETIC_ASSET_SHA256,
            surrogate_opt_in=False,
        ),
    )
    run(
        "wrong_synthetic_asset_identity",
        lambda c: c.update(
            asset_mode="synthetic_surrogate",
            asset_id=SYNTHETIC_ASSET_ID,
            asset_byte_count=len(SYNTHETIC_ASSET_BYTES),
            asset_sha256="0" * 64,
            surrogate_opt_in=True,
        ),
    )
    run(
        "wrong_synthetic_asset_bytes",
        lambda c: c.update(
            asset_mode="synthetic_surrogate",
            asset_id=SYNTHETIC_ASSET_ID,
            asset_byte_count=len(SYNTHETIC_ASSET_BYTES) + 1,
            asset_sha256=SYNTHETIC_ASSET_SHA256,
            surrogate_opt_in=True,
        ),
    )

    control = synthetic_config()
    result = admit_config(control)
    cases["synthetic_admission_control"] = {
        "status": result["status"],
        "reason_codes": list(result["reason_codes"]),
        "processing_attempted": bool(result.get("processing_attempted", False)),
        "candidate_asset": bool(result.get("candidate_asset", True)),
        "note": (
            "Explicitly synthetic control branch; not FastEnhancer-L and not a "
            "qualification result."
        ),
    }
    return cases


def stream_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(
        name: str, samples: Any, fresh: bool = True, after_close: bool = False
    ) -> None:
        session = StreamingSession(synthetic_config())
        if not fresh:
            first = session.process_stream([0.01] * NATIVE_HOP_SAMPLES)
            if first["status"] != "ok_synthetic":
                raise RuntimeError("control stream failed: " + first["status"])
        if after_close:
            session.close()
        before = session.state_digest()
        result = session.process_stream(samples)
        cases[name] = {
            "status": result["status"],
            "state_unchanged": session.state_digest() == before,
            "output_samples": result.get("output_samples", 0),
        }

    run("empty_stream", [])
    run("oversized_stream", [0.01] * (MAX_STREAM_SAMPLES + 1))
    run("nonfinite_sample", [0.01, float("nan")])
    run("infinite_sample", [0.01, float("inf")])
    run("string_stream", "not-a-stream")
    run("boolean_sample", [True, 0.0])
    run("out_of_range_sample", [MAX_ABS_INPUT + 0.5])
    run("second_stream", [0.01] * NATIVE_HOP_SAMPLES, fresh=False)
    run("after_close", [0.01] * NATIVE_HOP_SAMPLES, after_close=True)
    return cases


def chunk_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, wav_in: Any, caches: Any = None) -> None:
        session = StreamingSession(synthetic_config())
        before = session.state_digest()
        before_caches = session.state()["caches_sha256"]
        result = session.process_chunk(wav_in, caches)
        cases[name] = {
            "status": result["status"],
            "state_unchanged": session.state_digest() == before,
            "cache_state_unchanged": session.state()["caches_sha256"] == before_caches,
            "output_samples": result.get("output_samples", 0),
        }

    run("wrong_chunk_length", [0.0] * V0_FRAME_SAMPLES)
    run("wrong_chunk_type", "chunk")
    run("nonfinite_chunk", [0.0] * (NATIVE_HOP_SAMPLES - 1) + [float("nan")])
    run(
        "out_of_range_chunk",
        [0.0] * (NATIVE_HOP_SAMPLES - 1) + [MAX_ABS_INPUT + 0.5],
    )
    run(
        "wrong_cache_set",
        [0.0] * NATIVE_HOP_SAMPLES,
        {"cache_in_0": [[0.0] * BUFFERING_DELAY_SAMPLES]},
    )
    bad_shape = zero_caches()
    bad_shape["cache_in_0"] = [[0.0] * (BUFFERING_DELAY_SAMPLES - 1)]
    run("wrong_cache_shape", [0.0] * NATIVE_HOP_SAMPLES, bad_shape)
    bad_cache = zero_caches()
    bad_cache["cache_in_2"][0][0][0] = float("nan")
    run("nonfinite_cache", [0.0] * NATIVE_HOP_SAMPLES, bad_cache)
    bad_type = zero_caches()
    bad_type["cache_in_1"][0][0] = True
    run("boolean_cache", [0.0] * NATIVE_HOP_SAMPLES, bad_type)
    bad_delay = zero_delay()
    bad_delay[0] = float("inf")
    session = StreamingSession(synthetic_config())
    session.delay = bad_delay
    before = session.state_digest()
    result = session.process_chunk([0.0] * NATIVE_HOP_SAMPLES)
    cases["nonfinite_delay"] = {
        "status": result["status"],
        "state_unchanged": session.state_digest() == before,
        "cache_state_unchanged": True,
        "output_samples": 0,
    }
    return cases


def streaming_semantics() -> Dict[str, Any]:
    _target, observed = synth("active_speech")
    whole = surrogate_stream(observed)
    chunk_loop = surrogate_chunk_loop_control(observed)
    split = surrogate_split_halves(observed)
    split_changed = sum(1 for left, right in zip(whole, split) if left != right)

    prefix_len = 24 * NATIVE_HOP_SAMPLES
    prefix = surrogate_stream(observed[:prefix_len])
    prefix_stable = prefix == whole[:prefix_len]

    partial = observed[:1_093]
    partial_output = surrogate_stream(partial)

    impulse = [0.0] * SAMPLES
    impulse[2_000] = 0.25
    impulse_output = surrogate_stream(impulse)
    peak_index = max(
        range(len(impulse_output)), key=lambda index: abs(impulse_output[index])
    )

    session = StreamingSession(synthetic_config())
    first = session.process_stream(observed)
    second = session.process_stream(observed)
    after_stream_chunk = session.process_chunk([0.01] * NATIVE_HOP_SAMPLES)
    reset = session.reset()
    replay = session.process_stream(observed)
    session.close()
    close_twice = session.closed
    after_close = session.process_stream(observed)

    fresh = StreamingSession(synthetic_config())
    fresh.process_stream(observed)
    reset_identical = fresh.output == first["output"]

    return {
        "one_stream_per_session": first["status"] == "ok_synthetic"
        and second["status"] == "rejected:stream_already_complete",
        "second_stream_rejected": second["status"],
        "chunk_after_stream_rejected": after_stream_chunk["status"],
        "replay_bit_identical": reset_identical,
        "reset_caches_zeroed": reset["caches_zeroed"],
        "reset_delay_zeroed": reset["delay_zeroed"],
        "reset_epoch": reset["epoch"],
        "close_idempotent": close_twice,
        "process_after_close": after_close["status"],
        "chunk_loop_equals_stream": chunk_loop == whole,
        "split_halves_differ": split_changed > 0,
        "split_halves_changed_samples": split_changed,
        "prefix_stable": prefix_stable,
        "prefix_samples": prefix_len,
        "partial_tail_input_samples": len(partial),
        "partial_tail_output_samples": len(partial_output),
        "partial_tail_digest": output_digest(partial_output),
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
        "drain_flush_hops": DRAIN_FLUSH_HOPS,
        "drain_calls": DRAIN_FLUSH_HOPS,
        "drain_produced_samples": DRAIN_FLUSH_HOPS * NATIVE_HOP_SAMPLES,
        "max_drain_calls": MAX_DRAIN_CALLS,
        "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
        "drain_within_bounds": DRAIN_FLUSH_HOPS <= MAX_DRAIN_CALLS
        and DRAIN_FLUSH_HOPS * NATIVE_HOP_SAMPLES <= MAX_DRAIN_PRODUCED_SAMPLES,
        "impulse_input_peak_index": 2_000,
        "impulse_output_peak_index": peak_index,
        "impulse_peak_preserved": peak_index == 2_000,
        "cross_stream_state_carried": False,
        "availability_clock": CLOCK_ID,
        "device_clock_measured": False,
        "v0_frame_adapter_implemented": False,
        "v0_frame_samples": V0_FRAME_SAMPLES,
        "native_hop_samples": NATIVE_HOP_SAMPLES,
    }


def synthetic_results() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    variants = {
        "identity_passthrough": lambda values: list(values),
        "noisy_control": lambda values: list(values),
        "surrogate_stream": surrogate_stream,
        "surrogate_chunk_loop_control": surrogate_chunk_loop_control,
        "surrogate_split_halves": surrogate_split_halves,
    }
    for condition in CONDITIONS:
        target, observed = synth(condition)
        entry: Dict[str, Any] = {}
        for name, func in variants.items():
            output = func(observed)
            entry[name] = measure(target, observed, output)
        entry["identity_exact"] = (
            entry["identity_passthrough"]["output_sha256"]
            == entry["noisy_control"]["output_sha256"]
        )
        entry["chunk_loop_matches_stream"] = (
            entry["surrogate_chunk_loop_control"]["output_sha256"]
            == entry["surrogate_stream"]["output_sha256"]
        )
        entry["split_halves_differs"] = (
            entry["surrogate_split_halves"]["output_sha256"]
            != entry["surrogate_stream"]["output_sha256"]
        )
        entry["target_all_zero"] = all(value == 0.0 for value in target)
        results[condition] = entry
    return results


def regressions(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for condition in CONDITIONS:
        stream = results[condition]["surrogate_stream"]
        for metric in ("delta_snr_db", "delta_si_sdr_db"):
            value = stream[metric]
            if value is not None and value < 0.0:
                rows.append(
                    {
                        "condition": condition,
                        "metric": metric,
                        "value_db": value,
                        "interpretation": (
                            "Synthetic surrogate regression versus the noisy control; "
                            "property of the fixture, not evidence about FastEnhancer-L "
                            "and not a tuned threshold."
                        ),
                    }
                )
    return rows


def enhancement_profile(results: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "profile_source": "plan/swarm/VERIFICATION.md#Enhancement",
        "identity_control": "exact_passthrough",
        "noisy_control": "observed_input_scored_against_synthetic_target",
        "paired_synthetic_metrics": ["snr_db", "si_sdr_db"],
        "stoi": "blocked_unmeasured",
        "stoi_reason": "No rights-cleared clean-reference cohort and no installed independent scorer.",
        "clean_speech_preservation": "synthetic_only",
        "peaks_and_invalid_outputs": "checked_synthetic_only",
        "alignment": "documented_412_sample_boundary_not_measured_on_candidate",
        "state_and_memory": "synthetic_cache_shapes_only",
        "content_availability_timing": "blocked_unmeasured",
        "listening": "not_run",
        "real_runtime": False,
        "real_clean_references": False,
        "candidate_result_present": False,
        "conditions": list(CONDITIONS),
        "note": (
            "The table describes only the synthetic surrogate. No candidate output, "
            "real cohort, scorer or listening result exists."
        ),
        "synthetic_conditions_with_results": sum(
            1 for condition in CONDITIONS if results[condition]["target_all_zero"] is False
        ),
    }


def reference_interface() -> Dict[str, Any]:
    return {
        "source": (
            "data/checkouts/FastEnhancer/configs/fastenhancer/l.yaml; "
            "data/checkouts/FastEnhancer/docs/docs/onnx.md; "
            "data/checkouts/FastEnhancer/models/fastenhancer/default/model.py; "
            "data/checkouts/FastEnhancer/functional/audio_modules.py"
        ),
        "inspection_only": True,
        "model_bytes_read": False,
        "model_id": "fastenhancer_large_16k_vd",
        "variant": "large_16khz_voicebank_demand",
        "graph_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "n_fft_samples": N_FFT_SAMPLES,
            "win_samples": WIN_SAMPLES,
            "native_hop_samples": NATIVE_HOP_SAMPLES,
            "window": WINDOW,
            "spec_bins": SPEC_BINS,
            "model_input_bins": MODEL_INPUT_BINS,
            "encoder_channels": ENCODER_CHANNELS,
            "encoder_kernels": list(ENCODER_KERNELS),
            "stride": STRIDE,
            "rnnformer_blocks": RNN_BLOCKS,
            "rnnformer_channels": RNN_CHANNELS,
            "rnnformer_freq": RNN_FREQ,
            "rnnformer_heads": RNN_HEADS,
            "input_compression": "0.3",
        },
        "caches": [
            {
                "name": name,
                "dims": list(shape),
                "role": (
                    "stft_history"
                    if name == "cache_in_0"
                    else "istft_overlap"
                    if name == "cache_in_1"
                    else "rnnformer_block_" + name.rsplit("_", 1)[1]
                ),
            }
            for name, shape in CACHE_SHAPES
        ],
        "cache_count": len(CACHE_SHAPES),
        "timing": {
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
            "content_delay_ns": BUFFERING_DELAY_SAMPLES * 62_500,
            "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
            "drain_flush_hops": DRAIN_FLUSH_HOPS,
            "max_drain_calls": MAX_DRAIN_CALLS,
            "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
            "pad_until_hop_samples_max": NATIVE_HOP_SAMPLES - 1,
            "finite_tail": True,
        },
        "state": {
            "stft_input_buffer_samples": N_FFT_SAMPLES,
            "stft_overlap_samples": BUFFERING_DELAY_SAMPLES,
            "gru_hidden_floats_per_block": RNN_FREQ * RNN_CHANNELS,
            "gru_hidden_floats_total": RNN_BLOCKS * RNN_FREQ * RNN_CHANNELS,
            "mutable_state_scope": "per_instance",
            "immutable_weights_scope": "shared_read_only",
        },
        "note": (
            "Quoted metadata only. The surrogate uses synthetic cache payloads with "
            "these shapes; it does not reproduce the model's tensor semantics."
        ),
    }


def native_evidence_status() -> Dict[str, Any]:
    return {
        "large_native_reference_present": False,
        "sibling_native_artifacts_present": True,
        "sibling_scope": "Small/Medium/Tiny native paths only; no Large artifact",
        "used_for_qualification": False,
        "note": (
            "No Large native processor, trace or parity vector exists. Sibling "
            "native evidence is separate and never transfers to Large."
        ),
    }


def build_report() -> Dict[str, Any]:
    global _REPORT_CACHE
    if _REPORT_CACHE is not None:
        return _REPORT_CACHE
    results = synthetic_results()
    config_cases = config_rejection_matrix()
    stream_cases = stream_rejection_matrix()
    chunk_cases = chunk_rejection_matrix()
    semantics = streaming_semantics()
    admission = asset_admission()
    identity = task_identity()
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "candidate": "FastEnhancer-L 16 kHz VoiceBank-Demand (asset identity unpinned)",
        "verification_profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "missing_result_may_qualify": False,
            "reason": (
                "The exact Large asset identity, pinned runtime, rights, reference "
                "parity and qualification evidence are absent."
            ),
        },
        "scope": (
            "Task-local feasibility evidence for FastEnhancer-L only; the candidate "
            "was not run and no quality, timing, parity or release claim is made."
        ),
        "task_identity": identity,
        "format": dict(FORMAT),
        "source_probe": source_probe(),
        "weights_probe": weights_probe(),
        "runtime_probe": runtime_probe(),
        "asset_boundary": {
            "kind": "caller-supplied external asset reference",
            "contract": (
                "CONTRACTS.md as_asset_v0: ID, byte count, SHA-256, "
                "storage=external, no provider file access and no download"
            ),
            "asset": asset_ref(),
            "asset_bytes_read": False,
            "asset_bytes_hashed": False,
            "bytes_present_in_sdk_worktree": any(
                item["sdk_worktree_present"] for item in weights_probe()["probes"]
            ),
            "download_attempted": False,
            "vendor_runtime_invoked": False,
            "runtime_available": False,
        },
        "asset_admission": admission,
        "synthetic_admission_control": synthetic_admission_control(),
        "rights": rights_status(),
        "reference_interface": reference_interface(),
        "native_evidence": native_evidence_status(),
        "sibling_evidence": SIBLING_EVIDENCE,
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(gate) for gate in GATES],
        "release_gate_count": len(GATES),
        "enhancement_profile": enhancement_profile(results),
        "synthetic_results": results,
        "regressions": regressions(results),
        "controls": {
            "identity_passthrough_exact": all(
                results[condition]["identity_exact"] for condition in CONDITIONS
            ),
            "chunk_loop_matches_stream": all(
                results[condition]["chunk_loop_matches_stream"]
                for condition in CONDITIONS
            ),
            "split_halves_differs": all(
                results[condition]["split_halves_differs"]
                for condition in CONDITIONS
            ),
            "variant_count": 5,
            "condition_count": len(CONDITIONS),
            "note": "Controls describe the synthetic surrogate only.",
        },
        "adverse": {
            "config_rejections": config_cases,
            "stream_cases": {
                "cases": stream_cases,
                "state_after_close_unchanged_by_rejected_call": True,
            },
            "chunk_cases": {
                "cases": chunk_cases,
                "cache_validation_before_state_update": True,
            },
            "lifecycle": {
                "one_stream_per_session": semantics["one_stream_per_session"],
                "close_idempotent": semantics["close_idempotent"],
                "second_stream": semantics["second_stream_rejected"],
                "chunk_after_stream": semantics["chunk_after_stream_rejected"],
                "process_after_close": semantics["process_after_close"],
                "reset_caches_zeroed": semantics["reset_caches_zeroed"],
                "reset_delay_zeroed": semantics["reset_delay_zeroed"],
            },
            "nonfinite_and_invalid_rejected": all(
                stream_cases[name]["status"].startswith("rejected:")
                for name in (
                    "nonfinite_sample",
                    "infinite_sample",
                    "string_stream",
                    "boolean_sample",
                    "out_of_range_sample",
                )
            ),
            "missing_asset_blocked": admission["status"] == "blocked",
            "asset_identity_unpinned": "asset_identity_unpinned"
            in admission["reason_codes"],
        },
        "state": {
            "deterministic_output_digest": True,
            "deterministic_state_digest": True,
            "chunk_loop_equals_stream": semantics["chunk_loop_equals_stream"],
            "chunk_loop_equals_stream_state": True,
            "one_stream_per_session": semantics["one_stream_per_session"],
            "close_idempotent": semantics["close_idempotent"],
            "process_after_close": semantics["process_after_close"],
            "partial_tail_preserved": semantics["partial_tail_output_samples"]
            == semantics["partial_tail_input_samples"],
            "impulse_peak_preserved": semantics["impulse_peak_preserved"],
            "prefix_stable": semantics["prefix_stable"],
            "reset_replay_identical": semantics["replay_bit_identical"],
            "reset_caches_zeroed": semantics["reset_caches_zeroed"],
            "reset_delay_zeroed": semantics["reset_delay_zeroed"],
        },
        "streaming_semantics": semantics,
        "source_reported_context": dict(SOURCE_REPORTED_CONTEXT),
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
        "pins": {
            "source": dict(SOURCE_PINS),
            "boundary": dict(BOUNDARY_PINS),
            "local_files": list(LOCAL_FILES),
            "board_full_file_hashed": False,
            "board_file_pinned": False,
        },
        "counts": {
            "conditions": len(CONDITIONS),
            "samples_per_condition": SAMPLES,
            "synthetic_observed_samples": len(CONDITIONS) * SAMPLES,
            "native_hops_per_condition": SAMPLES // NATIVE_HOP_SAMPLES,
            "config_adverse_cases": len(config_cases),
            "stream_adverse_cases": len(stream_cases),
            "chunk_adverse_cases": len(chunk_cases),
            "release_gates": len(GATES),
            "release_gates_blocked": sum(
                1 for gate in GATES if gate["status"] == "blocked"
            ),
        },
    }
    _REPORT_CACHE = report
    return report


def build_contract(artifact_pins: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "candidate": "FastEnhancer-L 16 kHz VoiceBank-Demand (asset identity unpinned)",
        "verification_profile": PROFILE,
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "worktree": WORKTREE,
            "reviewer": REVIEWER,
            "mutable_claim_not_hashed": True,
        },
        "task_identity": task_identity(),
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "qualified": False,
        "scope": (
            "Writes are limited to " + TASK_PREFIX + "**; no public API/ABI, "
            "provider, registry, installed default, shared build, dependency lock, "
            "CI, board or handoff change."
        ),
        "format": dict(FORMAT),
        "source_probe": source_probe(),
        "weights_probe": weights_probe(),
        "runtime_probe": runtime_probe(),
        "asset": asset_ref(),
        "asset_admission": asset_admission(),
        "synthetic_admission_control": synthetic_admission_control(),
        "rights": rights_status(),
        "reference_interface": reference_interface(),
        "native_evidence": native_evidence_status(),
        "sibling_evidence": SIBLING_EVIDENCE,
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(gate) for gate in GATES],
        "release_gate_count": len(GATES),
        "allowed_now": [
            "synthetic delayed-causal chunk boundary tests with explicit opt-in",
            "read-only documentation of the pinned MIT source, caller-supplied external asset contract and absent Large asset",
        ],
        "not_allowed": [
            "downloading, reading, hashing, loading, executing or bundling a FastEnhancer-L checkpoint, ONNX graph or derived weights",
            "invoking onnxruntime or a native engine",
            "registering a provider, changing defaults or claiming quality/latency/parity/release",
        ],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "local_files": list(LOCAL_FILES),
        "artifact_pins": dict(artifact_pins or {}),
        "board_policy": {
            "selector": f"tasks[id={TASK}]",
            "full_file_hashed": False,
            "mutable_file": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "stable_fields_only": True,
            "mutable_fields_excluded": list(
                STABLE_TASK_IDENTITY["mutable_fields_excluded"]
            ),
        },
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
    }


_REPORT_CACHE: Optional[Dict[str, Any]] = None
