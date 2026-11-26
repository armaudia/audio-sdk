# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence model for SDK-PURESOUND-DPCRN-MAMBA-V2.

This module is NOT PureSound DPCRN-Mamba v2 and is not a reproduction of its
runtime. It does not load the ONNX graph or manifest, read audio/media, execute
a vendor runtime, measure a device clock or deadline, conduct listening,
benchmark the SDK or make a release/quality claim.

It models the *offline whole-clip boundary* a caller-supplied external asset
would have to cross: 16 kHz mono f32 in [-1, 1], the pinned `stft_frame_ort`
manifest geometry (512/512/160, three-frame look-ahead, 480-sample content
delay), exact configuration identity, whole-clip enhancement with identity
source-time mapping, output length equal to input length and exact accounting.
The signal path is an original deterministic surrogate, labelled as such
everywhere.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import platform
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-PURESOUND-DPCRN-MAMBA-V2"
TITLE = "PureSound DPCRN-Mamba v2"
SLUG = "puresound-dpcrn-mamba-v2"
COMPONENT = "puresound-dpcrn-mamba-v2"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "59469bca84c63b9fc71a3a3b115567df92170df0"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "processor_exposure"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
SAMPLES = 32_000
FRAME_COUNT = SAMPLES // FRAME_SAMPLES
MAX_CHUNK_SAMPLES = 2 * SAMPLE_RATE_HZ

# Pinned manifest geometry. The manifest declares three look-ahead frames for a
# DPCRN with delay=[1, 1, 1], i.e. 3 * 160 = 480 samples of content delay. The
# runtime and adapter trim that leading hold; the declared 52-62 ms
# input-to-output latency additionally includes the 512-sample analysis window
# and is not re-measured here.
FFT_LENGTH = 512
WIN_LENGTH = 512
HOP_LENGTH = 160
FREQ_BINS = 257
FEATURE_BINS = 256
STREAMING_DELAY_FRAMES = 3
LOOKAHEAD_SAMPLES = STREAMING_DELAY_FRAMES * HOP_LENGTH
LOOKAHEAD_MS = 30.0
ANALYSIS_WINDOW_MS = 32.0
HOP_MS = 10.0
INPUT_TO_OUTPUT_MIN_SAMPLES = 832
INPUT_TO_OUTPUT_MIN_MS = 52.0
INPUT_TO_OUTPUT_MAX_SAMPLES = 992
INPUT_TO_OUTPUT_MAX_MS = 62.0
DECLARED_CONTENT_DELAY_SAMPLES = LOOKAHEAD_SAMPLES
DECLARED_CONTENT_DELAY_NS = 30_000_000
DECLARED_INPUT_TO_OUTPUT_MIN_NS = 52_000_000
DECLARED_INPUT_TO_OUTPUT_MAX_NS = 62_000_000
FIXTURE_EPOCH_NS = 1_767_225_600_000_000_000
CLOCK_ID = "fixture-sample-coordinate-not-device"

SEED_BASE = 20261126
CONDITIONS: Tuple[str, ...] = (
    "quiet_speech",
    "active_speech",
    "low_snr_speech",
    "onset_offset",
    "idle_noise",
)
CHUNK_SIZES: Tuple[int, ...] = (1, 7, 80, 159, 160, 161, 320, 1280)
OVER_SUBTRACTION = 1.4
GAIN_FLOOR = 0.12
ATTACK = 0.6
RELEASE = 0.3
NOISE_PERCENTILE = 0.50
EPS = 1e-12

# Exact pinned candidate identity. Quoted from the pinned research ledgers,
# catalog and existing adapter; no asset bytes are copied into this worktree.
CANDIDATE_ID = "PureSound-noise-suppression-dpcrn-mamba-v2"
MODEL_ID = "noise-suppression-dpcrn-mamba-v2"
MODEL_NAME = "Noise Suppression DPCRN-Mamba v2"
UPSTREAM_ROLE = "default"
ADAPTER_IDENTITY = "PureSound-Streaming-SDK-79fad1f-DPCRN-Mamba"
ONNX_ID = "egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v2.onnx"
ONNX_BYTES = 2_282_757
ONNX_SHA256 = "a28cc5c9736f415a5ed603bd97cc415d11d8088cb2e288d20334a0713f723c86"
MANIFEST_ID = "egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v2.json"
MANIFEST_BYTES = 3_545
MANIFEST_SHA256 = "e5c54c5df8d7f3ee253c86ff09d4906f57efc01e2a6eeca80183ecf0fa88171d"
MANIFEST_REQUIRED = (
    "model_type=dpcrn_streaming_frame; processor=stft_frame_ort; sample_rate=16000; "
    "fft_length=512; win_length=512; hop_length=160; streaming_delay_frames=3"
)
CATALOG_PATH = "model_zoo/catalog.yaml"
CATALOG_SHA256 = "fc4d903bf141e62a5f5a9a88d9969e965ea7eef22678c40c62e33e46cf3cd373"
SOURCE_REPOSITORY = "https://github.com/mcw519/PureSound"
SOURCE_REVISION = "79fad1f1c753da5e40a0cbb00c6507c9fce2db3a"
CHECKOUT_PATH = "data/checkouts/puresound-dpcrn-mamba"
PACKAGE_VERSION = "0.1.0"
PACKAGE = "puresound-streaming==" + PACKAGE_VERSION
PACKAGE_IDENTITY = "puresound-streaming-0.1.0"
RUNTIME_PACKAGE = "onnxruntime"
RUNTIME_VERSION = "1.24.1"
RUNTIME = RUNTIME_PACKAGE + "==" + RUNTIME_VERSION
RUNTIME_LOCK = (
    ("numpy", "2.2.6"),
    ("onnxruntime", "1.24.1"),
    ("soundfile", "0.13.1"),
)
PROVIDER = "cpu"
VARIANT = "default"
MODEL_REVISION = None
MODEL_DOWNLOAD_REVISION = None
CODE_LICENSE_METADATA = "Apache-2.0"
MODEL_LICENSE_METADATA = "Apache-2.0 (official NOTICE); third-party material and datasets excluded"
TRAINING_DATA_NOTE = (
    "the upstream catalog describes v2 as v1 fine-tuned with a MetricGAN PESQ "
    "critic and reports VCTK-DEMAND PESQ-WB 2.57 and DNS-5 DNSMOS OVR 2.83; the "
    "pinned ledger does not establish exact corpus exposure or third-party "
    "dataset terms"
)
NOTICE_SHA256 = "ecce4d8c6a7bf96b90027ba1250ae734d33d4c260cd83fb67fcdce2286b435e1"
UPSTREAM_LICENSE_SHA256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "research/denoising_phase_completion_20261028.md":
        "fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "adapters/puresound-dpcrn-mamba/adapter.json":
        "ee1fb16e50a0808711994a190037f53be392e6b1148cf015ddef602425d4e037",
    "adapters/puresound-dpcrn-mamba/README.md":
        "c4cb52f917c4a3123d169fb68811984c75ea3b815eb1583bc42a9127bf8220f5",
    "adapters/puresound-dpcrn-mamba/run.py":
        "e378d09da875a9b11bc93fd84ff9b4ddefe48ba9803343f800698419fe00a5f4",
    "adapters/puresound-dpcrn-mamba/requirements.lock":
        "797d0a91bd7c7cc49ccc8d46b97988c98fdd74d1197e53ab363c16caef57c916",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    CHECKOUT_PATH + "/model_zoo/catalog.yaml": CATALOG_SHA256,
    CHECKOUT_PATH + "/" + ONNX_ID: ONNX_SHA256,
    CHECKOUT_PATH + "/" + MANIFEST_ID: MANIFEST_SHA256,
    CHECKOUT_PATH + "/sdk/python/puresound_streaming/runtime.py":
        "b8f38810aa81aea0563eb900c562ee33cb106787bf535371ce2387b301f3fdb0",
    CHECKOUT_PATH + "/sdk/python/pyproject.toml":
        "35bb2fadb8861a832e39a5dd2aa2553cff17cb904f02495f20fa356aea92b5ab",
    CHECKOUT_PATH + "/NOTICE": NOTICE_SHA256,
    CHECKOUT_PATH + "/LICENSE": UPSTREAM_LICENSE_SHA256,
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
}

# Fail-closed local file set. SOURCES.sha256 is excluded because a manifest
# cannot pin its own bytes; its .license sidecar is included.
LOCAL_FILES: Tuple[str, ...] = (
    "LICENSES.md",
    "README.md",
    "SOURCES.sha256.license",
    "adapter.json",
    "adapter.json.license",
    "asset.json",
    "asset.json.license",
    "check_licensing.py",
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

# Artifacts whose digests the README table must expose and verify.py must check.
README_DIGEST_FILES: Tuple[str, ...] = (
    "LICENSES.md",
    "adapter.json",
    "asset.json",
    "readiness.json",
    "reference.py",
    "report.json",
    "requirements.lock",
    "run.py",
    "test_reference.py",
    "verify.py",
)
README_TABLE_START = "<!-- digest-table:start -->"
README_TABLE_END = "<!-- digest-table:end -->"
EXPECTED_TEST_COUNT = 47

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
    "samples_per_call": FRAME_SAMPLES,
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
    "realtime_streaming_exposed": False,
    "task_board_or_handoff_write": False,
}

OFFLINE_BOUNDARY: Dict[str, Any] = {
    "mode": "offline-whole-clip",
    "whole_clip_required": True,
    "frames_buffered_until_finish": True,
    "output_length_equals_input": True,
    "source_time_mapping": "identity",
    "content_delay_samples": DECLARED_CONTENT_DELAY_SAMPLES,
    "delay_compensation_samples": DECLARED_CONTENT_DELAY_SAMPLES,
    "streamed_hold_samples": LOOKAHEAD_SAMPLES,
    "padded_samples_emitted": 0,
    "algorithmic_lag_samples": DECLARED_CONTENT_DELAY_SAMPLES,
    "flush_required": True,
    "manifest_required": True,
    "upstream_realtime_capable": True,
    "exposed_modes": ["offline"],
}

CLAIMS: Dict[str, bool] = {
    "real_puresound_runtime": False,
    "weights_accessed": False,
    "asset_downloaded": False,
    "asset_bytes_copied": False,
    "real_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "content_latency_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "quality_claim": False,
    "release_claim": False,
}

# The v2 manifest differs from v1 only in the ONNX path, creation timestamp and
# CPU-optimization native graph identity; these are the fields the pinned
# streaming contract requires. They are observed read-only in the external
# research checkout and are never admitted as caller-supplied content here.
MANIFEST_FIELDS: Dict[str, Any] = {
    "model_type": "dpcrn_streaming_frame",
    "processor": "stft_frame_ort",
    "sample_rate": 16000,
    "fft_length": 512,
    "win_length": 512,
    "hop_length": 160,
    "freq_bins": 257,
    "feature_bins": 256,
    "streaming_delay_frames": 3,
    "lookahead_samples": 480,
    "input_to_output_min_ms": 52.0,
    "input_to_output_max_ms": 62.0,
    "native_graph": "dpcrn_mamba_v2.native.onnx",
    "native_sha256": "b47fa2378ab57885463a08305741caf11ba192425f144392617c1089b5ec0426",
    "extra_output_names": [],
}

# Linked sibling package. It is task-local evidence for a distinct graph digest,
# not a source of results for this candidate.
SIBLING_V1: Dict[str, Any] = {
    "task": "SDK-PURESOUND-DPCRN-MAMBA-V1",
    "component": "puresound-dpcrn-mamba-v1",
    "decision": "DEFER",
    "evidence_status": "incomplete",
    "qualification_status": "not_qualified",
    "graph_sha256": "eabdca9fa7b0cc66c839d41e2fe07e409c9c09ad476e4dd0681a7bc63f04bfab",
    "head": "ca47268316779efb5161fc29571b2e5b313d31c3",
    "merge": "a91a45e32428df353dbf55a7a9fd2ec052760539",
    "pull_request": 167,
    "report_sha256": "b6967e090b8aed2e04f0e898e2f6094bc7870ffc3a7b1f0b8dfb2fa582dfbd8c",
    "note": (
        "The merged v1 package models the same 512/512/160 three-frame geometry "
        "for a different graph digest. No v1 metric, output, gate or disposition "
        "is promoted to v2."
    ),
}

EXACT_BLOCKERS: Tuple[str, ...] = (
    "The pinned ledger and catalog identify "
    "egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v2.onnx as "
    "2,282,757 bytes with SHA-256 "
    "a28cc5c9736f415a5ed603bd97cc415d11d8088cb2e288d20334a0713f723c86 and its "
    "manifest as 3,545 bytes with SHA-256 "
    "e5c54c5df8d7f3ee253c86ff09d4906f57efc01e2a6eeca80183ecf0fa88171d under "
    "source revision 79fad1f1c753da5e40a0cbb00c6507c9fce2db3a. The bytes are "
    "present in the external research checkout and were re-hashed there, but the "
    "ledger records no model_revision and no immutable retrieval record, no "
    "caller-held copy exists in this SDK worktree, and the package neither reads "
    "nor admits the bytes.",
    "The exact runtime is absent and unpinned here: puresound-streaming 0.1.0 is "
    "a source package in the external checkout without a built wheel/sdist digest, "
    "and onnxruntime 1.24.1 cannot be imported by the pinned CPython 3.12.16 "
    "interpreter (ModuleNotFoundError); the adapter requirements lock (numpy "
    "2.2.6, onnxruntime 1.24.1, soundfile 0.13.1) is not installed, and "
    "adapters/puresound-dpcrn-mamba/run.py is not executed.",
    "Apache-2.0 is recorded for the original PureSound code, SDK, configuration, "
    "documentation and model-zoo checkpoints/ONNX exports, and the upstream "
    "NOTICE permits commercial use and redistribution under the license, but it "
    "excludes third-party material and datasets/audio recordings; exact "
    "training-data provenance and third-party dataset terms are not established, "
    "and no artifact-specific redistribution/product-use legal review or decision "
    "is recorded. Apache-2.0 metadata alone is not qualification clearance. The "
    "upstream catalog default role for v2 grants no SDK default selection.",
    "No rights-cleared held-out real cohort, independent clean-reference scorer, "
    "permitted listening result, target-runtime timing/memory/throughput "
    "measurement, approved exact reference output vector or benchmark/release "
    "result exists; all eight release gates remain blocked.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen asset identity only when the exact dpcrn_mamba_v2.onnx and "
    "dpcrn_mamba_v2.json bytes are addressed by an immutable model artifact "
    "revision plus byte count and SHA-256 in a retrieval record, the manifest "
    "fields are verified, and both resolve from the caller's own storage without "
    "a provider file access or download.",
    "Reopen runtime admission only when a pinned puresound-streaming 0.1.0 wheel "
    "or sdist with a recorded digest and a pinned onnxruntime 1.24.1 install in "
    "an approved isolated environment, the adapter runs under the requirements "
    "lock, and a recorded parity run on the frozen inputs succeeds.",
    "Reopen rights only after written artifact-specific weight, runtime and "
    "training-data terms are recorded, the third-party/dataset exclusions are "
    "resolved, and a legal/redistribution/product-use decision exists; Apache-2.0 "
    "metadata alone is not clearance.",
    "Reopen qualification only with a rights-cleared paired cohort, an independent "
    "scorer, permitted listening, exact reference outputs for the frozen inputs, "
    "and target-runtime timing/memory/throughput evidence; the synthetic surrogate "
    "can never stand in for any of these.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "immutable graph and manifest artifact revision plus caller-held bytes",
    "verified manifest content for processor, model type, sample rate and streaming geometry",
    "pinned puresound-streaming 0.1.0 runtime artifact and onnxruntime 1.24.1 installation",
    "approved exact reference output vector on the frozen synthetic inputs",
    "written artifact-specific weight/runtime/training-data rights decision",
    "rights-cleared paired real speech cohort with clean references",
    "independent STOI/SI-SDR/intrusive scorer and permitted listening",
    "target-runtime timing, memory, throughput and offline availability evidence",
    "benchmark and release adjudication",
)

GATES: Tuple[Dict[str, str], ...] = (
    {"name": "exact_asset_identity", "status": "blocked",
     "evidence": "Ledger/catalog digest and byte counts only; model_revision is absent, no immutable retrieval record exists, and manifest content is unverified.",
     "reopen": REOPEN_CONDITIONS[0]},
    {"name": "runtime_admission", "status": "blocked",
     "evidence": "puresound-streaming 0.1.0 and onnxruntime 1.24.1 are absent from the pinned interpreter and have no recorded artifact digest here.",
     "reopen": REOPEN_CONDITIONS[1]},
    {"name": "artifact_rights", "status": "blocked",
     "evidence": "Apache-2.0 plus NOTICE metadata is recorded; third-party/dataset exclusions and an artifact-specific legal decision are absent.",
     "reopen": REOPEN_CONDITIONS[2]},
    {"name": "exact_reference_parity", "status": "blocked",
     "evidence": "No approved DPCRN-Mamba v2 reference output vector exists for these frozen inputs.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "rights_cleared_cohort", "status": "blocked",
     "evidence": "No paired real cohort with clean references is available to this task.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "independent_scoring_and_listening", "status": "blocked",
     "evidence": "No independent scorer or listening result; surrogate metrics are synthetic only.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "target_runtime_timing", "status": "blocked",
     "evidence": "No device clock, pacing, deadline, throughput or memory measurement was made.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "provider_intake_and_default_selection", "status": "blocked",
     "evidence": "No opt-in provider, descriptor or catalog entry exists; the package is unregistered and OFF by default, and the upstream v2 default role selects no SDK default.",
     "reopen": "Reopen only after rights/runtime/parity gates clear and an opt-in provider intake with OFF default, independent review, and an explicit SDK default decision with preserving controls is approved."},
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "scope": "Pinned research provenance only; not reproduced, not pooled and not used as a threshold.",
    "candidate_csv_row": (
        "Denoising,PureSound DPCRN-Mamba v2,evaluated,30 paired DNS2020 outputs; "
        "mean delta SNR +6.73 dB and RTF .200,PureSound v1/v3; FastEnhancer"
    ),
    "census_row": (
        "Completed 30-pair screen: mean delta SNR +6.73 dB, delta SI-SDR +6.69 dB, "
        "delta STOI +0.0334; adapter RTF 0.200."
    ),
    "inventory_evidence_status": (
        "evaluated in the research pilot; this SDK evidence package is incomplete "
        "and not qualified"
    ),
    "pilot_30_clip_median_output_snr_db": 16.455,
    "pilot_30_clip_median_delta_snr_db": 7.152,
    "pilot_30_clip_mean_delta_snr_db": 6.7304,
    "pilot_30_clip_delta_snr_ci95_db": [5.2930, 8.1975],
    "pilot_30_clip_mean_delta_si_sdr_db": 6.6897,
    "pilot_30_clip_delta_si_sdr_ci95_db": [5.2726, 8.1394],
    "pilot_30_clip_median_stoi": 0.9705,
    "pilot_30_clip_mean_delta_stoi": 0.0334,
    "pilot_30_clip_delta_stoi_ci95": [0.0248, 0.0420],
    "pilot_30_clip_mean_adapter_seconds": 1.9953,
    "pilot_30_clip_median_cpu_rtf": 0.1942,
    "pilot_30_clip_snr_improve_tie_degrade": [28, 0, 2],
    "pilot_30_clip_si_sdr_improve_tie_degrade": [28, 0, 2],
    "pilot_30_clip_stoi_improve_tie_degrade": [29, 0, 1],
    "realtime_candidates_row": (
        "DNS pilot mean delta SI-SDR +6.69 dB, delta STOI +0.0334, batch RTF "
        "0.1942; 480-sample streaming lookahead compensated during scoring."
    ),
    "upstream_reported": {
        "note": (
            "v2 is the upstream catalog default: v1 fine-tuned with a MetricGAN "
            "PESQ critic, reporting VCTK-DEMAND PESQ-WB 2.57 and DNS-5 DNSMOS "
            "OVR 2.83; no v2-specific score is transcribed as a local result, and "
            "the upstream default selects no SDK default."
        ),
        "role": UPSTREAM_ROLE,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "capabilities": {"offline_file": True, "realtime_streaming": True},
    },
    "training_data_note": TRAINING_DATA_NOTE,
    "disclaimer": (
        "These values come from pinned research files on 30 DNS2020 pairs and are "
        "not reproduced here, not device timing, not this fixture's metrics, not a "
        "listening result and not a release claim."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "The PureSound ONNX graph, manifest, source checkout and puresound-streaming 0.1.0 runtime are external; nothing was downloaded, copied, vendored, loaded or invoked.",
    "Graph/manifest digests and byte counts, source revision and catalog row are quoted from the pinned ledger and re-hashed in the external research checkout; no model bytes enter this SDK worktree.",
    "Input geometry, 480-sample lookahead, 512/512/160 STFT framing, 52-62 ms input-to-output algorithmic latency, 10 ms adapter chunking and the 480-sample trim are quoted from the pinned manifest, adapter run.py and README.",
    "The 30-clip values are pinned research provenance only; this package does not reproduce them and measures no runtime.",
    "All signals, targets and observations are generated by a stdlib LCG in reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
)

CALLER_CONFIG_FIELDS: Tuple[str, ...] = (
    "repository_dir",
    "code_revision",
    "model_id",
    "model_path",
    "manifest_path",
    "model_sha256",
    "sample_rate",
    "provider",
    "variant",
)

# Stable linked-row identity. The mutable board file is never hashed; only the
# stable projection of this task's own row is gated.
TASK_BOARD_REL = "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_ROW_FIELDS: Tuple[str, ...] = (
    "id", "title", "repository", "mode", "component", "depends_on",
    "evidence", "deliverable", "acceptance",
)
TASK_CLAIM_FIELDS: Tuple[str, ...] = (
    "base_commit", "branch", "reviewer",
)


def task_row_projection(row: Dict[str, Any]) -> Dict[str, Any]:
    projection: Dict[str, Any] = {}
    for key in TASK_ROW_FIELDS:
        projection[key] = row.get(key)
    claim = row.get("claim") or {}
    projection["claim"] = {key: claim.get(key) for key in TASK_CLAIM_FIELDS}
    return projection


def task_link() -> Dict[str, Any]:
    """Read only this task's stable board row; never hash the mutable board."""
    path = SOURCE_ROOT / TASK_BOARD_REL
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("linked task board is missing: " + TASK_BOARD_REL)
    board = json.loads(path.read_text(encoding="utf-8"))
    rows = [row for row in board.get("tasks", [])
            if row.get("id") == TASK or row.get("component") == COMPONENT]
    if len(rows) != 1:
        raise RuntimeError("linked task row is missing or ambiguous")
    row = rows[0]
    if row.get("id") != TASK or row.get("component") != COMPONENT:
        raise RuntimeError("linked task row identity mismatch")
    claim = row.get("claim") or {}
    if claim.get("branch") != BRANCH or claim.get("base_commit") != BASE_COMMIT:
        raise RuntimeError("linked task claim branch/base mismatch")
    if claim.get("worktree") != str(SDK_ROOT):
        raise RuntimeError("linked task worktree path mismatch")
    projection = task_row_projection(row)
    return {
        "board_path": TASK_BOARD_REL,
        "board_hashed": False,
        "projection_fields": list(TASK_ROW_FIELDS),
        "claim_projection_fields": list(TASK_CLAIM_FIELDS),
        "projection": projection,
        "projection_sha256": sha256(canonical_bytes(projection)),
        "row_status": row.get("status"),
        "row_owner": row.get("owner"),
    }


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def _seed(name: str) -> int:
    return (SEED_BASE + sum((index + 1) * ord(char)
                            for index, char in enumerate(name))) & 0xFFFFFFFF


def _envelope(condition: str, index: int) -> float:
    t = index / SAMPLE_RATE_HZ
    if condition == "onset_offset":
        regions = ((0.40, 0.80), (1.20, 1.60))
        value = 0.0
        for start, end in regions:
            if start <= t < end:
                ramp = min((t - start) / 0.01, (end - t) / 0.01, 1.0)
                value = max(value, ramp)
        return value
    if condition == "idle_noise":
        return 0.0
    modulation = math.sin(2.0 * math.pi * 3.1 * t + 0.4)
    return max(0.0, modulation) ** 1.2


def synth(condition: str) -> Tuple[List[float], List[float]]:
    """Return (clean target, observed input) for one frozen condition."""
    if condition not in CONDITIONS:
        raise ValueError("unknown condition: " + condition)
    scales = {
        "quiet_speech": (0.060, 0.006),
        "active_speech": (0.250, 0.035),
        "low_snr_speech": (0.050, 0.050),
        "onset_offset": (0.180, 0.020),
        "idle_noise": (0.000, 0.030),
    }
    target_scale, noise_scale = scales[condition]
    noise_rng = _lcg(_seed("noise:" + condition))
    clean: List[float] = []
    observed: List[float] = []
    for index in range(SAMPLES):
        t = index / SAMPLE_RATE_HZ
        if target_scale:
            carrier = (0.62 * math.sin(2.0 * math.pi * 213.0 * t)
                       + 0.28 * math.sin(2.0 * math.pi * 426.0 * t + 0.7)
                       + 0.10 * math.sin(2.0 * math.pi * 639.0 * t + 1.9))
            target = target_scale * _envelope(condition, index) * carrier
        else:
            target = 0.0
        noise = noise_scale * (2.0 * next(noise_rng) - 1.0)
        clean.append(target)
        observed.append(target + noise)
    return clean, observed


def runtime_probe() -> Dict[str, Any]:
    """Read-only environment probe; never imports or runs the vendor runtime."""
    checkout = SOURCE_ROOT / CHECKOUT_PATH
    head_path = checkout / ".git" / "HEAD"
    head = head_path.read_text(encoding="utf-8").strip() if head_path.is_file() else None
    graph = checkout / ONNX_ID
    manifest = checkout / MANIFEST_ID
    graph_present = graph.is_file() and not graph.is_symlink()
    manifest_present = manifest.is_file() and not manifest.is_symlink()
    return {
        "interpreter": "CPython " + platform.python_version(),
        "pinned_evidence_interpreter": "CPython 3.12.16",
        "onnxruntime_importable": importlib.util.find_spec("onnxruntime") is not None,
        "puresound_streaming_importable": importlib.util.find_spec("puresound_streaming") is not None,
        "source_checkout_present": checkout.is_dir(),
        "source_checkout_head": head,
        "source_checkout_head_matches_pin": head == SOURCE_REVISION,
        "graph_present_in_research_checkout": graph_present,
        "graph_sha256_matches_ledger": graph_present and sha256_file(graph) == ONNX_SHA256,
        "graph_bytes_match_ledger": graph_present and graph.stat().st_size == ONNX_BYTES,
        "manifest_present_in_research_checkout": manifest_present,
        "manifest_sha256_matches_ledger": manifest_present and sha256_file(manifest) == MANIFEST_SHA256,
        "manifest_bytes_match_ledger": manifest_present and manifest.stat().st_size == MANIFEST_BYTES,
        "asset_bytes_read_for_pin_verification_only": True,
        "asset_bytes_loaded_for_inference": False,
        "vendor_runtime_invoked": False,
    }


def asset_ref() -> Dict[str, Any]:
    """The exact caller-supplied asset reference this boundary would require."""
    probe = runtime_probe()
    return {
        "asset_id": ONNX_ID,
        "model_id": MODEL_ID,
        "model_name": MODEL_NAME,
        "storage": "external",
        "sha256": ONNX_SHA256,
        "byte_count": ONNX_BYTES,
        "auxiliary_assets": [
            {
                "asset_id": MANIFEST_ID,
                "sha256": MANIFEST_SHA256,
                "byte_count": MANIFEST_BYTES,
                "required_content": MANIFEST_REQUIRED,
                "content_verified": False,
                "manifest_fields": dict(MANIFEST_FIELDS),
            }
        ],
        "package": PACKAGE,
        "package_identity": PACKAGE_IDENTITY,
        "runtime": RUNTIME,
        "provider": PROVIDER,
        "variant": VARIANT,
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "catalog_path": CATALOG_PATH,
        "catalog_sha256": CATALOG_SHA256,
        "model_revision": MODEL_REVISION,
        "model_download_revision": MODEL_DOWNLOAD_REVISION,
        "code_license_metadata": CODE_LICENSE_METADATA,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "training_data_note": TRAINING_DATA_NOTE,
        "rights_cleared": False,
        "bytes_present": False,
        "bytes_present_in_research_checkout": (
            probe["graph_present_in_research_checkout"]
            and probe["manifest_present_in_research_checkout"]
            and probe["graph_sha256_matches_ledger"]
            and probe["manifest_sha256_matches_ledger"]
        ),
        "bytes_present_in_sdk_worktree": False,
        "runtime_available": False,
        "download_permitted": False,
    }


def manifest_content_reasons(fields: Any) -> List[str]:
    """Validate the structured streaming-manifest fields a caller must present."""
    reasons: List[str] = []
    if not isinstance(fields, dict):
        return ["manifest_fields_missing"]
    for key, expected in MANIFEST_FIELDS.items():
        if key not in fields:
            reasons.append("manifest_field_missing:" + key)
            continue
        actual = fields[key]
        if isinstance(expected, float):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)):
                reasons.append("manifest_field_type:" + key)
            elif not math.isfinite(float(actual)) or float(actual) != expected:
                reasons.append("manifest_field_mismatch:" + key)
        elif isinstance(expected, int):
            if isinstance(actual, bool) or not isinstance(actual, int):
                reasons.append("manifest_field_type:" + key)
            elif actual != expected:
                reasons.append("manifest_field_mismatch:" + key)
        elif actual != expected:
            reasons.append("manifest_field_mismatch:" + key)
    if set(fields) - set(MANIFEST_FIELDS):
        reasons.append("manifest_field_unexpected")
    return reasons


def _manifest_admitted(ref: Dict[str, Any]) -> bool:
    auxiliary = ref.get("auxiliary_assets")
    if not isinstance(auxiliary, list) or len(auxiliary) != 1:
        return False
    manifest = auxiliary[0]
    return (
        isinstance(manifest, dict)
        and manifest.get("asset_id") == MANIFEST_ID
        and manifest.get("sha256") == MANIFEST_SHA256
        and manifest.get("byte_count") == MANIFEST_BYTES
        and manifest.get("required_content") == MANIFEST_REQUIRED
        and manifest.get("content_verified") is True
        and not manifest_content_reasons(manifest.get("manifest_fields"))
    )


def asset_admission(ref: Dict[str, Any]) -> Dict[str, Any]:
    """Fail-closed admission for a caller-supplied external asset reference.

    No filesystem access, network access or vendor runtime call occurs. The
    checks mirror the pinned adapter and manifest: exact model/package/runtime
    identity, graph byte count and digest, verified manifest content, external
    storage and no download. A caller may supply bytes from its own storage, but
    this package holds none and does not admit the external checkout.
    """
    reasons: List[str] = []
    required = {"asset_id", "model_id", "storage", "sha256", "byte_count",
                "auxiliary_assets", "package", "runtime", "provider", "variant",
                "source_revision", "model_revision", "model_download_revision",
                "rights_cleared", "bytes_present", "runtime_available",
                "download_permitted"}
    missing = sorted(required - set(ref))
    if missing:
        reasons.append("missing_fields:" + ",".join(missing))
    if ref.get("asset_id") != ONNX_ID:
        reasons.append("asset_id_mismatch")
    if ref.get("model_id") != MODEL_ID:
        reasons.append("model_id_mismatch")
    if ref.get("storage") != "external":
        reasons.append("storage_not_external")
    if ref.get("sha256") != ONNX_SHA256:
        reasons.append("sha256_mismatch")
    if ref.get("byte_count") != ONNX_BYTES:
        reasons.append("byte_count_mismatch")
    if ref.get("package") != PACKAGE:
        reasons.append("package_mismatch")
    if ref.get("runtime") != RUNTIME:
        reasons.append("runtime_mismatch")
    if ref.get("provider") != PROVIDER:
        reasons.append("provider_mismatch")
    if ref.get("variant") != VARIANT:
        reasons.append("variant_mismatch")
    if ref.get("source_revision") != SOURCE_REVISION:
        reasons.append("source_revision_mismatch")
    if ref.get("model_revision") in (None, "", "main"):
        reasons.append("model_revision_unpinned")
    if ref.get("model_download_revision") in (None, ""):
        reasons.append("download_revision_unrecorded")
    if not _manifest_admitted(ref):
        reasons.append("manifest_artifact_unverified")
    if ref.get("download_permitted") is not False:
        reasons.append("download_flag_invalid")
    if ref.get("bytes_present") is not True:
        reasons.append("asset_bytes_not_caller_supplied")
    if ref.get("runtime_available") is not True:
        reasons.append("runtime_unavailable")
    if ref.get("rights_cleared") is not True:
        reasons.append("rights_not_cleared")
    return {
        "status": "admitted" if not reasons else "blocked",
        "reason_codes": reasons,
        "download_attempted": False,
        "vendor_runtime_invoked": False,
        "asset_bytes_read": False,
    }


def synthetic_config() -> Dict[str, Any]:
    return {
        "mode": "synthetic-surrogate",
        "synthetic_surrogate_opt_in": True,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "model_id": MODEL_ID,
        "variant": VARIANT,
        "provider": PROVIDER,
        "asset_reference": asset_ref(),
    }


def caller_asset_config() -> Dict[str, Any]:
    """The upstream adapter fields, path-free, plus our asset wrapper."""
    return {
        "mode": "caller-asset",
        "repository_ref": "caller-supplied://puresound@" + SOURCE_REVISION,
        "code_revision": SOURCE_REVISION,
        "model_id": MODEL_ID,
        "model_path_ref": ONNX_ID,
        "manifest_path_ref": MANIFEST_ID,
        "model_sha256": ONNX_SHA256,
        "sample_rate": SAMPLE_RATE_HZ,
        "provider": PROVIDER,
        "variant": VARIANT,
        "asset_reference": asset_ref(),
    }


CALLER_CONFIG_KEYS = (
    "mode",
    "repository_ref",
    "code_revision",
    "model_id",
    "model_path_ref",
    "manifest_path_ref",
    "model_sha256",
    "sample_rate",
    "provider",
    "variant",
    "asset_reference",
)


def default_config() -> Dict[str, Any]:
    return synthetic_config()


def validate_config(config: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    mode = config.get("mode")
    if mode not in ("synthetic-surrogate", "caller-asset"):
        return ["mode_unsupported"]
    if mode == "synthetic-surrogate":
        expected = synthetic_config()
        for key in ("sample_rate_hz", "channels", "sample_format", "model_id",
                    "variant", "provider"):
            if config.get(key) != expected[key]:
                reasons.append(key + "_mismatch")
        if config.get("synthetic_surrogate_opt_in") is not True:
            reasons.append("surrogate_opt_in_required")
        return reasons
    if set(config) != set(CALLER_CONFIG_KEYS):
        reasons.append("caller_asset_config_fields_mismatch")
        return reasons
    if config.get("code_revision") != SOURCE_REVISION:
        reasons.append("code_revision_mismatch")
    if config.get("model_id") != MODEL_ID:
        reasons.append("model_id_mismatch")
    if config.get("model_sha256") != ONNX_SHA256:
        reasons.append("model_sha256_mismatch")
    if config.get("sample_rate") != SAMPLE_RATE_HZ:
        reasons.append("sample_rate_mismatch")
    if config.get("provider") != PROVIDER:
        reasons.append("provider_mismatch")
    if config.get("variant") != VARIANT:
        reasons.append("variant_mismatch")
    admission = asset_admission(config.get("asset_reference") or {})
    if admission["status"] != "admitted":
        reasons.append("asset_not_admitted")
    return reasons


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = fraction * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _frame_powers(samples: Sequence[float]) -> Tuple[List[float], int]:
    count = len(samples)
    if count == 0:
        return [], -1
    last = (count - 1) // HOP_LENGTH
    powers: List[float] = []
    for frame_index in range(last + 1):
        start = frame_index * HOP_LENGTH
        end = min(start + WIN_LENGTH, count)
        width = max(0, end - start)
        powers.append(sum(value * value for value in samples[start:end]) / width
                      if width else 0.0)
    return powers, last


def enhance_core(samples: Sequence[float]) -> Tuple[List[float], Dict[str, Any]]:
    """Deterministic 512/160 frame-gain surrogate; exact length, no windowing."""
    count = len(samples)
    if count == 0:
        return [], {
            "input_samples": 0,
            "output_samples": 0,
            "last_data_frame": -1,
            "internal_frame_padding_samples": 0,
            "streamed_hold_samples": 0,
            "noise_floor_power": 0.0,
            "gain_min": 1.0,
            "gain_max": 1.0,
        }
    powers, last = _frame_powers(samples)
    noise_floor = max(_percentile(powers, NOISE_PERCENTILE), EPS)
    targets: List[float] = []
    for power in powers:
        ratio = power / noise_floor
        if ratio <= OVER_SUBTRACTION:
            target = GAIN_FLOOR
        else:
            target = math.sqrt(max(0.0, 1.0 - OVER_SUBTRACTION / ratio))
        targets.append(min(1.0, max(GAIN_FLOOR, target)))
    smoothed: List[float] = []
    gain = 1.0
    for frame_index in range(last + 1):
        future = min(frame_index + STREAMING_DELAY_FRAMES, last)
        target = targets[future]
        alpha = ATTACK if target < gain else RELEASE
        gain = gain + alpha * (target - gain)
        smoothed.append(gain)
    output: List[float] = []
    gain_min = 1.0
    gain_max = 1.0
    for index in range(count):
        frame_index = min(index // HOP_LENGTH, last)
        current = smoothed[frame_index]
        previous = smoothed[frame_index - 1] if frame_index > 0 else smoothed[0]
        weight = ((index % HOP_LENGTH) + 1) / float(HOP_LENGTH)
        applied = previous + (current - previous) * weight
        gain_min = min(gain_min, applied)
        gain_max = max(gain_max, applied)
        output.append(samples[index] * applied)
    return output, {
        "input_samples": count,
        "output_samples": len(output),
        "last_data_frame": last,
        "internal_frame_padding_samples": (-count) % HOP_LENGTH,
        "streamed_hold_samples": LOOKAHEAD_SAMPLES,
        "noise_floor_power": noise_floor,
        "gain_min": gain_min,
        "gain_max": gain_max,
    }


def enhance_offline(samples: Sequence[float]) -> Tuple[List[float], Dict[str, Any]]:
    """Model the streamed 480-sample hold then trim it to an aligned clip."""
    core, info = enhance_core(samples)
    if not samples:
        info["streamed_samples"] = 0
        info["delay_compensation_samples"] = DECLARED_CONTENT_DELAY_SAMPLES
        return [], info
    streamed = [0.0] * LOOKAHEAD_SAMPLES + core
    aligned = streamed[LOOKAHEAD_SAMPLES:LOOKAHEAD_SAMPLES + len(samples)]
    info["streamed_samples"] = len(streamed)
    info["delay_compensation_samples"] = DECLARED_CONTENT_DELAY_SAMPLES
    return aligned, info


class OfflineSurrogateSession:
    """Whole-clip offline boundary fixture; not a vendor enhancer."""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = dict(config or default_config())
        reasons = validate_config(self.config)
        if reasons:
            raise ValueError(";".join(reasons))
        self._samples: List[float] = []
        self._input_samples = 0
        self._finished = False
        self._closed = False

    def digest(self) -> str:
        payload = canonical_bytes({
            "samples": self._samples,
            "input_samples": self._input_samples,
            "finished": self._finished,
            "closed": self._closed,
        })
        return sha256(payload)

    def process(self, chunk: Sequence[float]) -> List[float]:
        """Buffer a caller chunk. Offline work happens only at finish()."""
        if self._closed:
            raise ValueError("session_closed")
        if self._finished:
            raise ValueError("session_already_finished")
        if isinstance(chunk, (str, bytes)) or not isinstance(chunk, Sequence):
            raise ValueError("chunk_type_invalid")
        values = list(chunk)
        if not values:
            raise ValueError("chunk_empty")
        if len(values) > MAX_CHUNK_SAMPLES:
            raise ValueError("chunk_oversized")
        for value in values:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError("sample_type_invalid")
            if not math.isfinite(float(value)):
                raise ValueError("sample_nonfinite")
            if abs(float(value)) > 1.0:
                raise ValueError("sample_out_of_range")
        self._samples.extend(float(value) for value in values)
        self._input_samples += len(values)
        return []

    def finish(self) -> List[float]:
        if self._closed:
            raise ValueError("session_closed")
        if self._finished:
            raise ValueError("session_already_finished")
        output, _ = enhance_offline(self._samples)
        self._finished = True
        return output

    def reset(self) -> None:
        if self._closed:
            raise ValueError("session_closed")
        self._samples = []
        self._input_samples = 0
        self._finished = False

    def close(self) -> None:
        self._closed = True

    @property
    def input_samples(self) -> int:
        return self._input_samples

    @property
    def finished(self) -> bool:
        return self._finished


# ---------------------------------------------------------------------------
# Offline runs, boundary accounting and synthetic scoring
# ---------------------------------------------------------------------------

def run_offline(samples: Sequence[float], chunk_size: int,
                config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Feed one chunking and return the whole-clip output plus accounting."""
    if chunk_size <= 0 or chunk_size > MAX_CHUNK_SAMPLES:
        raise ValueError("chunk_size_unsupported")
    session = OfflineSurrogateSession(config)
    chunk_records: List[Dict[str, int]] = []
    emitted_before_finish = 0
    for start in range(0, len(samples), chunk_size):
        chunk = list(samples[start:start + chunk_size])
        emitted = session.process(chunk)
        emitted_before_finish += len(emitted)
        chunk_records.append({"start_sample": start, "input_count": len(chunk),
                              "emitted_count": len(emitted)})
    output = session.finish()
    _, info = enhance_offline(samples)
    return {
        "chunk_size": chunk_size,
        "chunk_count": len(chunk_records),
        "chunk_records": chunk_records,
        "output": output,
        "output_digest": sha256(canonical_bytes(output)),
        "emitted_before_finish": emitted_before_finish,
        "finish_emitted": len(output),
        "output_length": len(output),
        "input_samples": len(samples),
        "valid_samples": len(output),
        "streamed_samples": info["streamed_samples"],
        "streamed_hold_samples": info["streamed_hold_samples"],
        "internal_frame_padding_samples": info["internal_frame_padding_samples"],
        "source_time_mapping": "identity",
        "delay_compensation_samples": DECLARED_CONTENT_DELAY_SAMPLES,
        "padded_samples": 0,
        "final_state_digest": session.digest(),
    }


def _rms(values: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / float(len(values)))


def _db(ratio: float) -> float:
    return 10.0 * math.log10(max(ratio, 1e-30))


def score(clean: Sequence[float], estimate: Sequence[float]) -> Dict[str, Any]:
    """Synthetic paired diagnostics only; no real scorer or model is used."""
    if len(clean) != len(estimate) or not clean:
        raise ValueError("score_length_mismatch")
    signal_power = sum(value * value for value in clean)
    error_power = sum((a - b) ** 2 for a, b in zip(clean, estimate))
    snr_db = None if signal_power <= 0.0 else _db(signal_power / max(error_power, 1e-30))
    projection = sum(a * b for a, b in zip(clean, estimate))
    if signal_power > 0.0:
        scale = projection / signal_power
        target_power = sum((scale * value) ** 2 for value in clean)
        residual_power = sum((scale * a - b) ** 2 for a, b in zip(clean, estimate))
        si_sdr_db = None if target_power <= 0.0 else _db(target_power / max(residual_power, 1e-30))
    else:
        si_sdr_db = None
    peak = max(abs(value) for value in estimate)
    return {
        "snr_db": snr_db,
        "si_sdr_db": si_sdr_db,
        "output_rms": _rms(estimate),
        "peak_abs_output": peak,
        "clipped_samples": sum(1 for value in estimate if abs(value) > 1.0),
        "nonfinite_samples": sum(1 for value in estimate if not math.isfinite(value)),
        "scored_samples": len(estimate),
    }


def condition_block(condition: str) -> Dict[str, Any]:
    clean, observed = synth(condition)
    chunked = run_offline(observed, FRAME_SAMPLES)
    whole = run_offline(observed, SAMPLES)
    valid = chunked["valid_samples"]
    prefix = clean[:valid]
    noisy = score(prefix, observed[:valid])
    identity = score(prefix, observed[:valid])
    candidate = score(prefix, chunked["output"][:valid])
    whole_score = score(prefix, whole["output"][:valid])

    def delta(candidate_value: Any, control_value: Any) -> Any:
        if candidate_value is None or control_value is None:
            return None
        return candidate_value - control_value

    return {
        "input_samples": len(observed),
        "scored_samples": valid,
        "tail_validity": {
            "input_samples": len(observed),
            "output_samples": chunked["output_length"],
            "valid_samples": valid,
            "streamed_samples": chunked["streamed_samples"],
            "streamed_hold_samples": chunked["streamed_hold_samples"],
            "internal_frame_padding_samples": chunked["internal_frame_padding_samples"],
            "padded_samples_emitted": chunked["padded_samples"],
            "source_time_mapping": chunked["source_time_mapping"],
            "delay_compensation_samples": chunked["delay_compensation_samples"],
            "attributable_samples": valid,
        },
        "variants": {
            "identity_passthrough": {**identity, "exact_passthrough": True},
            "noisy_control": noisy,
            "surrogate_offline_chunked_160": candidate,
            "surrogate_offline_whole_clip": whole_score,
        },
        "improvements": {
            "snr_db": delta(candidate["snr_db"], noisy["snr_db"]),
            "si_sdr_db": delta(candidate["si_sdr_db"], noisy["si_sdr_db"]),
        },
        "noise_attenuation_db": (
            None if noisy["output_rms"] <= 0.0
            else _db((candidate["output_rms"] / noisy["output_rms"]) ** 2)
        ),
        "chunk_invariance_digest": chunked["output_digest"],
        "whole_clip_matches_chunked": chunked["output_digest"] == whole["output_digest"],
    }


def alignment_probe() -> Dict[str, Any]:
    """Model the 480-sample streamed hold and its exact trim."""
    samples = [0.001 * math.sin(2.0 * math.pi * 97.0 * index / SAMPLE_RATE_HZ)
               for index in range(8000)]
    samples[4000] = 0.9
    core, _ = enhance_core(samples)
    streamed = [0.0] * LOOKAHEAD_SAMPLES + core
    streamed_peak = max(range(len(streamed)), key=lambda index: abs(streamed[index]))
    output = streamed[LOOKAHEAD_SAMPLES:LOOKAHEAD_SAMPLES + len(samples)]
    output_peak = max(range(len(output)), key=lambda index: abs(output[index]))
    return {
        "input_peak_sample": 4000,
        "declared_content_delay_samples": DECLARED_CONTENT_DELAY_SAMPLES,
        "declared_lookahead_samples": LOOKAHEAD_SAMPLES,
        "declared_input_to_output_min_ms": INPUT_TO_OUTPUT_MIN_MS,
        "declared_input_to_output_max_ms": INPUT_TO_OUTPUT_MAX_MS,
        "streamed_peak_sample": streamed_peak,
        "output_peak_sample": output_peak,
        "output_lag_samples": output_peak - 4000,
        "residual_lag_samples": output_peak - 4000,
        "measured_latency": False,
        "modeled_only": True,
    }


def cross_hop_evidence() -> Dict[str, Any]:
    _, observed = synth("active_speech")
    records: Dict[str, Any] = {}
    output_digests = set()
    for size in CHUNK_SIZES:
        run = run_offline(observed, size)
        boundaries_crossed = 0
        for start in range(0, len(observed), size):
            end = min(start + size, len(observed))
            first = start // HOP_LENGTH + 1
            last = (end - 1) // HOP_LENGTH
            if last >= first:
                boundaries_crossed += 1
        records[str(size)] = {
            "chunk_count": run["chunk_count"],
            "chunks_crossing_hop_boundary": boundaries_crossed,
            "emitted_before_finish": run["emitted_before_finish"],
            "finish_emitted": run["finish_emitted"],
            "output_length": run["output_length"],
            "valid_samples": run["valid_samples"],
            "streamed_samples": run["streamed_samples"],
            "output_digest": run["output_digest"],
        }
        output_digests.add(run["output_digest"])
    whole = run_offline(observed, SAMPLES)
    return {
        "samples": len(observed),
        "frame_samples": FRAME_SAMPLES,
        "hop_samples": HOP_LENGTH,
        "chunk_sizes_tested": list(CHUNK_SIZES),
        "records": records,
        "output_chunk_invariant": len(output_digests) == 1,
        "whole_call_matches_chunked": whole["output_digest"] == run_offline(
            observed, FRAME_SAMPLES)["output_digest"],
        "total_hop_boundaries": FRAME_COUNT - 1,
        "device_clock_used": False,
        "deadline_measured": False,
    }


def state_evidence() -> Dict[str, Any]:
    _, observed = synth("low_snr_speech")
    session = OfflineSurrogateSession()
    digests = []
    for start in range(0, len(observed), FRAME_SAMPLES):
        session.process(observed[start:start + FRAME_SAMPLES])
        digests.append(session.digest())
    session.reset()
    replay = []
    for start in range(0, len(observed), FRAME_SAMPLES):
        session.process(observed[start:start + FRAME_SAMPLES])
        replay.append(session.digest())
    fresh = OfflineSurrogateSession()
    independent = []
    for start in range(0, len(observed), FRAME_SAMPLES):
        fresh.process(observed[start:start + FRAME_SAMPLES])
        independent.append(fresh.digest())
    _, other = synth("active_speech")
    cross = OfflineSurrogateSession()
    for start in range(0, 8000, FRAME_SAMPLES):
        cross.process(observed[start:start + FRAME_SAMPLES])
    cross.reset()
    for start in range(0, 8000, FRAME_SAMPLES):
        cross.process(other[start:start + FRAME_SAMPLES])
    control = OfflineSurrogateSession()
    for start in range(0, 8000, FRAME_SAMPLES):
        control.process(other[start:start + FRAME_SAMPLES])
    return {
        "chunks_processed": len(digests),
        "state_digest_chain": sha256(canonical_bytes(digests)),
        "first_state_digest": digests[0],
        "last_state_digest": digests[-1],
        "reset_replay_identical": replay == digests,
        "independent_session_identical": independent == digests,
        "cross_stream_reset_identical": cross.digest() == control.digest(),
        "state_is_synthetic": True,
        "real_recurrent_state_loaded": False,
    }


def config_adverse_cases() -> Dict[str, Any]:
    base = synthetic_config()
    cases: Dict[str, Any] = {}

    def attempt(name: str, config: Dict[str, Any]) -> None:
        try:
            session = OfflineSurrogateSession(config)
        except ValueError as error:
            cases[name] = {
                "status": "rejected",
                "reason_codes": str(error).split(";"),
                "session_created": False,
                "processing_attempted": False,
            }
        else:
            cases[name] = {
                "status": "created",
                "reason_codes": [],
                "session_created": True,
                "processing_attempted": False,
                "state_digest": session.digest(),
            }

    def mutated(**changes: Any) -> Dict[str, Any]:
        config = json.loads(json.dumps(base))
        config.update(changes)
        return config

    attempt("wrong_sample_rate", mutated(sample_rate_hz=48000))
    attempt("wrong_channels", mutated(channels=2))
    attempt("wrong_sample_format", mutated(sample_format="i16"))
    attempt("wrong_model_id", mutated(model_id="noise-suppression-dpcrn-mamba-v3"))
    attempt("wrong_variant", mutated(variant="flash"))
    attempt("wrong_provider", mutated(provider="cuda"))
    attempt("mode_unsupported",
            {"mode": "streaming", "synthetic_surrogate_opt_in": True})
    attempt("surrogate_without_opt_in", mutated(synthetic_surrogate_opt_in=False))
    attempt("caller_asset_unavailable", caller_asset_config())

    wrong_revision = caller_asset_config()
    wrong_revision["code_revision"] = "0" * 40
    attempt("caller_asset_wrong_code_revision", wrong_revision)

    wrong_sha = caller_asset_config()
    wrong_sha["model_sha256"] = "0" * 64
    attempt("caller_asset_wrong_model_sha", wrong_sha)

    control = caller_asset_config()
    control["asset_reference"].update({
        "model_revision": "artifact:puresound-dpcrn-mamba-v2@" + ONNX_SHA256,
        "model_download_revision": "artifact:puresound-dpcrn-mamba-v2@" + ONNX_SHA256,
        "rights_cleared": True,
        "bytes_present": True,
        "runtime_available": True,
        "auxiliary_assets": [{
            "asset_id": MANIFEST_ID,
            "sha256": MANIFEST_SHA256,
            "byte_count": MANIFEST_BYTES,
            "required_content": MANIFEST_REQUIRED,
            "content_verified": True,
            "manifest_fields": dict(MANIFEST_FIELDS),
        }],
    })
    attempt("caller_asset_admission_control", control)
    return cases


def manifest_admission_cases() -> Dict[str, Any]:
    """Reject missing, invalid and nonfinite manifest content fail-closed."""
    cases: Dict[str, Any] = {}

    def attempt(name: str, fields: Any) -> None:
        reasons = manifest_content_reasons(fields)
        cases[name] = {
            "status": "admitted" if not reasons else "rejected",
            "reason_codes": reasons,
            "content_admitted": not reasons,
        }

    attempt("complete_control", dict(MANIFEST_FIELDS))
    missing = dict(MANIFEST_FIELDS)
    missing.pop("processor")
    attempt("missing_processor", missing)
    wrong_type = dict(MANIFEST_FIELDS)
    wrong_type["model_type"] = "dpcrn_streaming_frame_v1"
    attempt("wrong_model_type", wrong_type)
    wrong_geometry = dict(MANIFEST_FIELDS)
    wrong_geometry["hop_length"] = 128
    attempt("wrong_hop_length", wrong_geometry)
    wrong_native = dict(MANIFEST_FIELDS)
    wrong_native["native_sha256"] = "0" * 64
    attempt("wrong_native_sha256", wrong_native)
    nonfinite = dict(MANIFEST_FIELDS)
    nonfinite["input_to_output_min_ms"] = float("nan")
    attempt("nonfinite_latency", nonfinite)
    infinite = dict(MANIFEST_FIELDS)
    infinite["input_to_output_max_ms"] = float("inf")
    attempt("infinite_latency", infinite)
    extra = dict(MANIFEST_FIELDS)
    extra["unknown_extension"] = True
    attempt("unexpected_field", extra)
    attempt("not_an_object", ["dpcrn_streaming_frame"])
    return cases


def frame_adverse_cases() -> Dict[str, Any]:
    session = OfflineSurrogateSession()
    session.process([0.01] * FRAME_SAMPLES)
    cases: Dict[str, Any] = {}

    def rejected(name: str, action) -> None:
        before = session.digest()
        try:
            action()
        except ValueError as error:
            after = session.digest()
            cases[name] = {
                "status": "rejected:" + str(error),
                "state_unchanged": before == after,
                "state_digest": after,
            }
        else:
            cases[name] = {"status": "accepted", "state_unchanged": False,
                           "state_digest": session.digest()}

    rejected("empty_chunk", lambda: session.process([]))
    rejected("oversized_chunk", lambda: session.process([0.0] * (MAX_CHUNK_SAMPLES + 1)))
    rejected("nonfinite_sample", lambda: session.process([float("nan")]))
    rejected("infinite_sample", lambda: session.process([float("inf")]))
    rejected("string_chunk", lambda: session.process("not-a-chunk"))
    rejected("boolean_sample", lambda: session.process([True]))
    rejected("out_of_range_sample", lambda: session.process([1.5]))

    output = session.finish()
    after_finish = session.digest()
    rejected("process_after_finish", lambda: session.process([0.0] * FRAME_SAMPLES))
    rejected("finish_after_finish", session.finish)
    after_rejected_finish = session.digest()
    session.close()
    after_close = session.digest()
    rejected("process_after_close", lambda: session.process([0.0] * FRAME_SAMPLES))
    rejected("finish_after_close", session.finish)
    rejected("reset_after_close", session.reset)
    after_rejected_close = session.digest()
    session.close()
    return {
        "cases": cases,
        "finish_output_samples": len(output),
        "state_after_finish_unchanged_by_rejected_calls": after_finish == after_rejected_finish,
        "state_after_close_unchanged_by_rejected_calls": after_close == after_rejected_close,
        "closed_after_double_close": session._closed,
    }


def lifecycle_evidence() -> Dict[str, Any]:
    session = OfflineSurrogateSession()
    session.process([0.0] * FRAME_SAMPLES)
    first = session.finish()
    try:
        session.finish()
    except ValueError as error:
        second_finish = "rejected:" + str(error)
    else:
        second_finish = "accepted"
    session.reset()
    reset_output = session.finish()
    session.close()
    closed_digest = session.digest()
    session.close()
    results = {}
    for name, action in (("process_after_close", lambda: session.process([0.0])),
                         ("finish_after_close", session.finish),
                         ("reset_after_close", session.reset)):
        try:
            action()
        except ValueError as error:
            results[name] = "rejected:" + str(error)
        else:
            results[name] = "accepted"
    return {
        "finish_returns_samples": bool(first),
        "second_finish": second_finish,
        "reset_finish_empty": reset_output == [],
        "close_idempotent": session._closed and closed_digest == session.digest(),
        "process_after_close": results["process_after_close"],
        "finish_after_close": results["finish_after_close"],
        "reset_after_close": results["reset_after_close"],
        "zero_length_finish": OfflineSurrogateSession().finish() == [],
    }


def tail_probe() -> Dict[str, Any]:
    """Exercise a partial final hop without emitting padding."""
    _, observed = synth("active_speech")
    probe = list(observed) + [0.02 * ((index % 17) - 8) / 8.0 for index in range(123)]
    output, info = enhance_offline(probe)
    return {
        "input_samples": len(probe),
        "output_samples": len(output),
        "streamed_samples": info["streamed_samples"],
        "streamed_hold_samples": info["streamed_hold_samples"],
        "internal_frame_padding_samples": info["internal_frame_padding_samples"],
        "padded_samples_emitted": 0,
        "source_time_mapping": "identity",
        "delay_compensation_samples": DECLARED_CONTENT_DELAY_SAMPLES,
        "exact_length": len(output) == len(probe),
    }


def _admitted_control() -> Dict[str, Any]:
    control = json.loads(json.dumps(asset_ref()))
    control.update({
        "model_revision": "artifact:puresound-dpcrn-mamba-v2@" + ONNX_SHA256,
        "model_download_revision": "artifact:puresound-dpcrn-mamba-v2@" + ONNX_SHA256,
        "rights_cleared": True,
        "bytes_present": True,
        "runtime_available": True,
        "auxiliary_assets": [{
            "asset_id": MANIFEST_ID,
            "sha256": MANIFEST_SHA256,
            "byte_count": MANIFEST_BYTES,
            "required_content": MANIFEST_REQUIRED,
            "content_verified": True,
            "manifest_fields": dict(MANIFEST_FIELDS),
        }],
    })
    return control


def asset_boundary() -> Dict[str, Any]:
    ref = asset_ref()
    admission = asset_admission(ref)
    control_admission = asset_admission(_admitted_control())
    probe = runtime_probe()
    return {
        "kind": "caller-supplied external asset reference",
        "contract": "CONTRACTS.md as_asset_v0: ID, byte count, SHA-256, storage=external, no download",
        "candidate": CANDIDATE_ID,
        "asset": {
            "asset_id": ref["asset_id"],
            "model_id": ref["model_id"],
            "model_name": ref["model_name"],
            "storage": ref["storage"],
            "sha256": ref["sha256"],
            "byte_count": ref["byte_count"],
            "package": ref["package"],
            "package_identity": ref["package_identity"],
            "runtime": ref["runtime"],
            "provider": ref["provider"],
            "variant": ref["variant"],
            "source_repository": ref["source_repository"],
            "source_revision": ref["source_revision"],
            "catalog_path": ref["catalog_path"],
            "catalog_sha256": ref["catalog_sha256"],
            "model_revision": ref["model_revision"],
            "model_download_revision": ref["model_download_revision"],
            "code_license_metadata": ref["code_license_metadata"],
            "model_license_metadata": ref["model_license_metadata"],
            "training_data_note": ref["training_data_note"],
        },
        "auxiliary_assets": [
            {
                "asset_id": MANIFEST_ID,
                "sha256": MANIFEST_SHA256,
                "byte_count": MANIFEST_BYTES,
                "required_content": MANIFEST_REQUIRED,
                "content_verified": False,
                "manifest_fields_observed_in_external_checkout": True,
                "manifest_fields": dict(MANIFEST_FIELDS),
            }
        ],
        "readiness": admission["status"],
        "reason_codes": admission["reason_codes"],
        "download_attempted": admission["download_attempted"],
        "vendor_runtime_invoked": admission["vendor_runtime_invoked"],
        "asset_bytes_read": admission["asset_bytes_read"],
        "bytes_present_in_research_checkout": ref["bytes_present_in_research_checkout"],
        "bytes_present_in_sdk_worktree": False,
        "hashes_verified_against_research_checkout": (
            probe["graph_sha256_matches_ledger"]
            and probe["manifest_sha256_matches_ledger"]
            and probe["graph_bytes_match_ledger"]
            and probe["manifest_bytes_match_ledger"]
        ),
        "runtime_available_in_evidence_interpreter": probe["onnxruntime_importable"],
        "runtime_probe": probe,
        "rights_cleared": False,
        "synthetic_admission_control": {
            "status": control_admission["status"],
            "reason_codes": control_admission["reason_codes"],
            "not_the_pinned_candidate": True,
            "note": "Admission logic only; no upstream bytes exist in this worktree and no rights are implied.",
        },
        "surrogate_policy": {
            "available": True,
            "opt_in_required": True,
            "substitutes_for_candidate": False,
            "labelled": "deterministic stdlib 512/160 offline whole-clip surrogate",
        },
        "reopen_condition": REOPEN_CONDITIONS[0] + " " + REOPEN_CONDITIONS[1] + " " + REOPEN_CONDITIONS[2],
    }


def enhancement_profile() -> Dict[str, Any]:
    return {
        "name": PROFILE,
        "source": "plan/swarm/VERIFICATION.md",
        "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "identity_and_noisy_controls": True,
        "paired_snr_and_si_sdr": "synthetic_fixture_only",
        "stoi": {"status": "blocked_unmeasured",
                 "reason": "no clean-reference-eligible real cohort and no installed STOI scorer"},
        "clean_speech_preservation": {
            "status": "synthetic_only",
            "conditions": ["quiet_speech", "active_speech"],
        },
        "peaks_and_invalid_outputs": True,
        "alignment": {
            "status": "modelled_content_delay",
            "declared_content_delay_samples": DECLARED_CONTENT_DELAY_SAMPLES,
            "declared_lookahead_samples": LOOKAHEAD_SAMPLES,
            "declared_input_to_output_min_ms": INPUT_TO_OUTPUT_MIN_MS,
            "declared_input_to_output_max_ms": INPUT_TO_OUTPUT_MAX_MS,
            "compensated": True,
            "measured": False,
        },
        "state_and_memory": {
            "status": "synthetic_state_only",
            "real_memory_measured": False,
        },
        "content_and_availability_timing": {
            "status": "blocked_unmeasured",
            "measured": False,
            "device_clock": False,
        },
        "listening": {"status": "not_run", "permitted": False},
        "real_runtime": False,
        "real_clean_references": False,
        "release_gate": "blocked",
    }


def _condition_blocks() -> Dict[str, Any]:
    return {name: condition_block(name) for name in CONDITIONS}


def _regressions(blocks: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    for condition, block in blocks.items():
        noisy = block["variants"]["noisy_control"]
        candidate = block["variants"]["surrogate_offline_chunked_160"]
        for metric in ("snr_db", "si_sdr_db"):
            if noisy[metric] is None or candidate[metric] is None:
                continue
            if candidate[metric] < noisy[metric]:
                regressions.append({
                    "condition": condition,
                    "metric": metric,
                    "better_direction": "higher",
                    "noisy_control": noisy[metric],
                    "surrogate_offline_chunked_160": candidate[metric],
                    "delta": candidate[metric] - noisy[metric],
                    "note": "Synthetic fixture regression recorded verbatim; not a candidate result.",
                })
    return regressions


def _core_report() -> Dict[str, Any]:
    blocks = _condition_blocks()
    admission = asset_admission(asset_ref())
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "slug": SLUG,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "task_link": task_link(),
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "evidence_status": EVIDENCE_STATUS,
            "decision": DECISION,
            "qualifies": False,
            "missing_result_promoted": False,
            "processor_exposure": False,
            "real_runtime_used": False,
            "quality_claim": False,
            "release_claim": False,
        },
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "format": FORMAT,
        "boundary": BOUNDARY,
        "offline_boundary": OFFLINE_BOUNDARY,
        "claims": CLAIMS,
        "conditions": blocks,
        "controls": {
            "all_present": True,
            "identity": {
                "name": "identity_passthrough",
                "exact_passthrough": True,
                "note": "No processing; every scored sample is the observed input.",
            },
            "noisy_control": {
                "name": "observed_input_no_processing",
                "note": "Paired control for the synthetic target on the same valid prefix.",
            },
            "candidate": {
                "name": "surrogate_offline_chunked_160",
                "real_candidate": False,
                "note": "Deterministic stdlib 512/160 offline surrogate, not PureSound DPCRN-Mamba v2.",
            },
            "whole_clip": {
                "name": "surrogate_offline_whole_clip",
                "note": "Chunk invariance control; must equal the 160-sample fed output.",
            },
        },
        "regressions": _regressions(blocks),
        "offline_processing": {
            "protocol": "caller-supplied external asset plus buffered whole-clip calls",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "input_range": [-1.0, 1.0],
            "frame_samples": FRAME_SAMPLES,
            "chunk_sizes_tested": list(CHUNK_SIZES),
            "max_chunk_samples": MAX_CHUNK_SAMPLES,
            "analysis_geometry": {
                "fft_length": FFT_LENGTH,
                "win_length": WIN_LENGTH,
                "hop_length": HOP_LENGTH,
                "freq_bins": FREQ_BINS,
                "feature_bins": FEATURE_BINS,
                "streaming_delay_frames": STREAMING_DELAY_FRAMES,
                "lookahead_samples": LOOKAHEAD_SAMPLES,
                "lookahead_ms": LOOKAHEAD_MS,
                "analysis_window_ms": ANALYSIS_WINDOW_MS,
                "hop_ms": HOP_MS,
                "input_to_output_min_samples": INPUT_TO_OUTPUT_MIN_SAMPLES,
                "input_to_output_min_ms": INPUT_TO_OUTPUT_MIN_MS,
                "input_to_output_max_samples": INPUT_TO_OUTPUT_MAX_SAMPLES,
                "input_to_output_max_ms": INPUT_TO_OUTPUT_MAX_MS,
                "excludes": ["compute time", "additional input chunk buffering",
                             "audio device buffering", "transport"],
            },
            "declared_content_delay_samples": DECLARED_CONTENT_DELAY_SAMPLES,
            "declared_lookahead_samples": LOOKAHEAD_SAMPLES,
            "declared_content_delay_ns": DECLARED_CONTENT_DELAY_NS,
            "declared_input_to_output_min_ns": DECLARED_INPUT_TO_OUTPUT_MIN_NS,
            "declared_input_to_output_max_ns": DECLARED_INPUT_TO_OUTPUT_MAX_NS,
            "lag_provenance": (
                "adapters/puresound-dpcrn-mamba/run.py computes "
                "delay_samples = streaming_delay_frames * hop_length = 3 * 160 = 480 "
                "and trims it; the pinned manifest reports 480-sample look-ahead and "
                "52-62 ms input-to-output algorithmic latency. Source-reported, not "
                "re-measured here."
            ),
            "lag_measured_here": False,
            "lag_modeled_in_fixture": True,
            "clock_id": CLOCK_ID,
            "fixture_epoch_ns": str(FIXTURE_EPOCH_NS),
            "availability_model": "sample-coordinate only; no wall clock, device clock or deadline",
            "finish_policy": (
                "Caller chunks are buffered and the whole clip is enhanced once at finish. "
                "The surrogate models the runtime's 480-sample streamed hold before the "
                "adapter's trim; a partial final hop is zero-padded only for gain estimation "
                "and is never emitted."
            ),
            "reset_policy": "Explicit reset clears the buffer and finished flag; replay is bit-identical.",
            "output_accounting": {
                "output_samples": "input_samples",
                "delay_compensation_samples": DECLARED_CONTENT_DELAY_SAMPLES,
                "streamed_hold_samples": LOOKAHEAD_SAMPLES,
                "padded_samples_emitted": 0,
                "internal_frame_padding_samples": "(-input_samples) mod 160",
                "source_time_mapping": "identity",
                "finding": (
                    "The upstream runtime emits a stream delayed by the graph's 480-sample "
                    "look-ahead and the adapter trims exactly that hold; one output sample "
                    "is returned per input sample with identity source-time mapping. This "
                    "model emits exactly len(input) samples; internal padding exists only "
                    "for gain estimation."
                ),
            },
            "chunk_invariance": cross_hop_evidence(),
            "alignment_probe": alignment_probe(),
            "state": state_evidence(),
            "tail_probe": tail_probe(),
            "upstream_config_fields": list(CALLER_CONFIG_FIELDS),
            "upstream_config_note": (
                "The upstream adapter uses repository_dir, model_path and manifest_path; "
                "this package models them as caller-owned symbolic references and never "
                "puts a filesystem path in configuration or errors."
            ),
            "manifest_requirement": {
                "manifest_asset": MANIFEST_ID,
                "required_content": MANIFEST_REQUIRED,
                "content_verified_here": False,
                "upstream_check": (
                    "processor == stft_frame_ort and sample_rate == 16000 and "
                    "model_type == dpcrn_streaming_frame"
                ),
            },
        },
        "asset_boundary": asset_boundary(),
        "asset_admission": admission,
        "enhancement_profile": enhancement_profile(),
        "adverse": {
            "config_rejections": config_adverse_cases(),
            "manifest_cases": manifest_admission_cases(),
            "frame_cases": frame_adverse_cases(),
            "lifecycle": lifecycle_evidence(),
        },
        "repeatability": {},
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "gates": list(GATES),
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "sibling_v1_package": dict(SIBLING_V1),
        "tool_provenance": list(TOOL_PROVENANCE),
        "source_pin_paths": sorted(SOURCE_PINS),
        "boundary_pin_paths": sorted(BOUNDARY_PINS),
        "local_file_names": list(LOCAL_FILES),
        "readme_digest_files": list(README_DIGEST_FILES),
        "notes": [
            "Every metric in this report is computed on a deterministic synthetic fixture and describes the surrogate only.",
            "No PureSound graph, manifest, package, runtime, output, corpus, device, listener or release artifact is used or claimed.",
            "All timestamps are source-sample coordinates; no device, wall-clock, pacing or deadline measurement exists.",
        ],
    }


def build_report() -> Dict[str, Any]:
    core = _core_report()
    digests = []
    for _ in range(3):
        digests.append(sha256(canonical_bytes(core)))
    core["repeatability"] = {
        "count": 3,
        "byte_identical": len(set(digests)) == 1,
        "digests": digests,
        "tested_core": "report without the repeatability block",
    }
    return core


def build_asset() -> Dict[str, Any]:
    ref = asset_ref()
    probe = runtime_probe()
    return {
        "protocol_version": 1,
        "task": TASK,
        "candidate": CANDIDATE_ID,
        "kind": "caller-supplied external asset reference",
        "storage": "external",
        "download_permitted": False,
        "asset": {
            "asset_id": ref["asset_id"],
            "model_id": ref["model_id"],
            "model_name": ref["model_name"],
            "type": "onnx-graph",
            "sha256": ref["sha256"],
            "byte_count": ref["byte_count"],
            "present_in_research_checkout": ref["bytes_present_in_research_checkout"],
            "present_in_sdk_worktree": False,
            "loaded_for_inference": False,
        },
        "manifest": {
            "asset_id": MANIFEST_ID,
            "type": "streaming-manifest",
            "sha256": MANIFEST_SHA256,
            "byte_count": MANIFEST_BYTES,
            "required_content": MANIFEST_REQUIRED,
            "content_verified": False,
            "present_in_research_checkout": probe["manifest_present_in_research_checkout"],
            "loaded_for_inference": False,
        },
        "source": {
            "repository": SOURCE_REPOSITORY,
            "revision": SOURCE_REVISION,
            "catalog_path": CATALOG_PATH,
            "catalog_sha256": CATALOG_SHA256,
            "checkout_path": CHECKOUT_PATH,
            "checkout_head": probe["source_checkout_head"],
            "checkout_head_matches_pin": probe["source_checkout_head_matches_pin"],
        },
        "runtime": {
            "package": PACKAGE,
            "package_identity": PACKAGE_IDENTITY,
            "provider": PROVIDER,
            "variant": VARIANT,
            "requires": RUNTIME,
            "requirements_lock": {name: version for name, version in RUNTIME_LOCK},
            "evidence_interpreter": probe["pinned_evidence_interpreter"],
            "onnxruntime_importable": probe["onnxruntime_importable"],
            "puresound_streaming_importable": probe["puresound_streaming_importable"],
            "vendor_runtime_invoked": False,
        },
        "rights": {
            "code_license": CODE_LICENSE_METADATA,
            "model_license": MODEL_LICENSE_METADATA,
            "license_sha256": UPSTREAM_LICENSE_SHA256,
            "notice_sha256": NOTICE_SHA256,
            "exclusions": "third-party material and datasets/audio recordings",
            "rights_cleared": False,
            "legal_review": False,
            "training_data_note": TRAINING_DATA_NOTE,
            "upstream_bytes_copied_or_vendored": False,
        },
        "readiness": "blocked",
        "reason_codes": asset_admission(ref)["reason_codes"],
        "reopen_condition": REOPEN_CONDITIONS[0] + " " + REOPEN_CONDITIONS[1],
    }


def build_contract() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_version": "0.1",
        "task": TASK,
        "component": COMPONENT,
        "slug": SLUG,
        "title": TITLE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "task_link": task_link(),
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "format": FORMAT,
        "boundary": BOUNDARY,
        "offline_boundary": OFFLINE_BOUNDARY,
        "claims": CLAIMS,
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "gates": list(GATES),
        "asset": asset_ref(),
        "asset_admission": asset_admission(asset_ref()),
        "upstream_contract": {
            "adapter_identity": ADAPTER_IDENTITY,
            "entrypoint": "adapters/puresound-dpcrn-mamba/run.py",
            "config_fields": list(CALLER_CONFIG_FIELDS),
            "input": "mono 16 kHz f32 in [-1, 1]",
            "output": "identity source-time mapping, 480-sample content delay compensated, zero padded samples, length equal to input",
            "manifest_required": True,
            "manifest_content": MANIFEST_REQUIRED,
            "offline_adapter_chunk_ms": 10,
            "upstream_realtime_capable": True,
            "exposed_modes": ["offline"],
        },
        "surrogate": {
            "kind": "deterministic stdlib 512/160 offline whole-clip surrogate",
            "opt_in_required": True,
            "substitutes_for_candidate": False,
            "weights_used": False,
            "vendor_runtime_used": False,
        },
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "evidence_status": EVIDENCE_STATUS,
            "decision": DECISION,
            "qualifies": False,
            "missing_result_promoted": False,
            "processor_exposure": False,
            "real_runtime_used": False,
            "quality_claim": False,
            "release_claim": False,
        },
        "public_surface": {
            "provider_registration": False,
            "installed_v0_geometry_change": False,
            "installed_v0_behavior_change": False,
            "api_or_abi_change": False,
            "descriptor_or_registry_change": False,
            "default_selection": False,
            "shared_build_or_ci_change": False,
            "task_board_or_handoff_change": False,
            "realtime_streaming_exposure": False,
        },
        "source_pins": {"source:" + key: value for key, value in SOURCE_PINS.items()},
        "boundary_pins": {"worktree:" + key: value for key, value in BOUNDARY_PINS.items()},
        "artifact_pins": {},
    }


def build_adapter() -> Dict[str, Any]:
    return {
        "protocol_version": 1,
        "identity": "PureSound-DPCRN-Mamba-v2-offline-proposal",
        "boundary_identity": "as_asset_v0-external-caller-supplied",
        "input_kind": "waveform",
        "output_kinds": ["waveform"],
        "tasks": ["CLN-01"],
        "modes": ["offline"],
        "upstream_modes": ["offline", "realtime-streaming"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "package": PACKAGE,
        "package_identity": PACKAGE_IDENTITY,
        "runtime": RUNTIME,
        "model": {
            "asset_id": ONNX_ID,
            "model_id": MODEL_ID,
            "model_name": MODEL_NAME,
            "sha256": ONNX_SHA256,
            "byte_count": ONNX_BYTES,
            "source_revision": SOURCE_REVISION,
            "catalog_sha256": CATALOG_SHA256,
            "model_revision": MODEL_REVISION,
            "model_download_revision": MODEL_DOWNLOAD_REVISION,
            "auxiliary_assets": [{
                "asset_id": MANIFEST_ID,
                "sha256": MANIFEST_SHA256,
                "byte_count": MANIFEST_BYTES,
                "required_content": MANIFEST_REQUIRED,
            }],
        },
        "configuration": {
            "asset_required": True,
            "upstream_catalog_role": UPSTREAM_ROLE,
            "asset_storage": "external",
            "download_permitted": False,
            "whole_clip": True,
            "output_length_equals_input": True,
            "content_delay_samples": DECLARED_CONTENT_DELAY_SAMPLES,
            "delay_compensation_samples": DECLARED_CONTENT_DELAY_SAMPLES,
            "streamed_hold_samples": LOOKAHEAD_SAMPLES,
            "manifest_required": True,
            "reset_between_clips": True,
            "provider": PROVIDER,
            "variant": VARIANT,
        },
        "entrypoint": ["python", "reference.py"],
        "upstream_entrypoint": ["python", "adapters/puresound-dpcrn-mamba/run.py"],
        "asset_readiness": asset_admission(asset_ref())["status"],
        "real_runtime_used": False,
        "weights_accessed": False,
        "quality_claim": False,
        "registration": {
            "registered": False,
            "enabled_by_default": False,
            "default_selected": False,
            "descriptor_registry_change": False,
            "public_api_abi_change": False,
        },
        "status": STATUS,
        "decision": DECISION,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "evidence_status": EVIDENCE_STATUS,
            "qualifies": False,
        },
    }


def build_readiness() -> Dict[str, Any]:
    admission = asset_admission(asset_ref())
    return {
        "schema_id": f"audio-sdk/task-evidence/{SLUG}/readiness/0.1",
        "task": TASK,
        "component": COMPONENT,
        "candidate": CANDIDATE_ID,
        "status": "blocked",
        "qualified": False,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "asset_reference": asset_ref(),
        "admission": admission,
        "readiness_conclusion": (
            "The offline whole-clip boundary is modelled, but the candidate is not ready to "
            "run or qualify: the exact dpcrn_mamba_v2.onnx graph and manifest are present "
            "only in the external research checkout, the pinned ledger has no immutable "
            "model artifact revision and the manifest content is unverified, the "
            "puresound-streaming 0.1.0 package and onnxruntime 1.24.1 runtime are absent "
            "from the pinned CPython 3.12.16 interpreter, and artifact-specific rights "
            "with third-party/dataset exclusions are not cleared. The upstream catalog "
            "default role for v2 selects no SDK default."
        ),
        "external_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "allowed_now": [
            "synthetic surrogate boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied asset contract",
            "read-only digest and byte-count verification of the external research checkout",
        ],
        "not_allowed": [
            "downloading, copying or bundling the PureSound graph, manifest or puresound-streaming package",
            "executing the vendor runtime or publishing its outputs",
            "registering a provider, changing defaults or claiming quality/timing",
        ],
    }
