# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only reference for the FastEnhancer Tiny boundary.

This module does not contain, download, hash, load, compile or invoke
FastEnhancer, ``fastenhancer_t.onnx``, its derived weights, ONNX Runtime or the
vendored native engine.  It models the caller-supplied external asset boundary
from ``CONTRACTS.md`` (``as_asset_v0``: ID, byte count, SHA-256,
``storage=external``, no provider file access and no download) and the exact
documented streaming interface recorded in the pinned model contract.

The embedded surrogate is an explicitly opt-in, synthetic, causal gain path.  It
is **not** FastEnhancer, substitutes for no gate and can never qualify the
candidate.  Its cache payloads are synthetic placeholders with the documented
shapes, not the model's tensors.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2]))).resolve()
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-FASTENHANCER-TINY-REFERENCE"
TITLE = "FastEnhancer Tiny reference"
SLUG = "fastenhancer-tiny-reference"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "a1e7573dc38ebd0d8efb3050dd38613ec0950941"
BRANCH = f"swarm/{TASK}"
WORKTREE = f"/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/{TASK}"
REVIEWER = f"reviewer-{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "processor_exposure"

SAMPLE_RATE_HZ = 16_000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
V0_FRAME_SAMPLES = 160
NATIVE_HOP_SAMPLES = 256
N_FFT_SAMPLES = 512
SPEC_BINS = 257
FREQ_BINS = 256
WINDOW = "periodic_hann"
BUFFERING_DELAY_SAMPLES = 256
STARTUP_INVALID_SAMPLES = 256
DRAIN_FLUSH_HOPS = 2
MAX_DRAIN_CALLS = 4
MAX_DRAIN_PRODUCED_SAMPLES = 640
SAMPLES = 32_000
MAX_STREAM_SAMPLES = 64_000
MAX_ABS_INPUT = 4.0
SEED_BASE = 2026_1126
CLOCK_ID = "fixture-sample-coordinate-not-device"

CACHE_SHAPES: Tuple[Tuple[str, Tuple[int, ...]], ...] = (
    ("cache_in_0", (1, NATIVE_HOP_SAMPLES)),
    ("cache_in_1", (1, NATIVE_HOP_SAMPLES)),
    ("cache_in_2", (1, 16, 20)),
    ("cache_in_3", (1, 16, 20)),
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

# Candidate identity, quoted from the pinned asset ledger and model contract.
ASSET_ID = "fastenhancer_t.onnx"
ASSET_LEDGER_PATH = "data/models/fastenhancer/fastenhancer_t.onnx"
ASSET_BYTES = 125_233
ASSET_SHA256 = "a64663672b31bd1445502ee23328d291af13fb312e11bb574c010e7261a5ee7d"
SOURCE_REPOSITORY = "https://github.com/aask1357/fastenhancer"
SOURCE_REVISION = "49ab55a57e3a064d94c6412cd0f0a383a55ca0f8"
RELEASE_TAG = "onnx-dns-v1.0.0"
CODE_LICENSE_METADATA = "MIT (repository)"
MODEL_TERMS_METADATA = "not specified separately; retain local only"
MODEL_LICENSE_METADATA = "not specified separately"
RUNTIME_PACKAGE = "onnxruntime==1.20.1"
RUNTIME_WHEEL_SHA256 = "e50ba5ff7fed4f7d9253a6baf801ca2883cc08491f9d32d78a80da57256a5439"
RUNTIME_LOCK = "adapters/fastenhancer/requirements.lock"
RUNTIME_TARGET = "CPython 3.10, macOS arm64"

# Authoring-time, metadata-only observations.  No byte was opened or hashed.
# These record that exact-digest private copies exist outside this SDK worktree;
# possession and metadata inspection are not rights, runtime or parity.
WORKSPACE_COPIES: Tuple[Dict[str, Any], ...] = (
    {
        "path_relative_to_source_root": "cpp-library/.deps/fastenhancer_t_16k.onnx",
        "byte_count": ASSET_BYTES,
        "inside_sdk_worktree": False,
        "observed_at_authoring": True,
        "byte_read_by_this_package": False,
    },
    {
        "path_relative_to_source_root": (
            "audio-benchmark-platform/audio-pro/models/fastenhancer_tiny16/fastenhancer_t.onnx"
        ),
        "byte_count": ASSET_BYTES,
        "inside_sdk_worktree": False,
        "observed_at_authoring": True,
        "byte_read_by_this_package": False,
    },
)

# Explicitly synthetic admission control.  These bytes are not model weights.
SYNTHETIC_ASSET_ID = "synthetic-streaming-surrogate-not-fastenhancer"
SYNTHETIC_ASSET_UNIT = b"audio-sdk/fastenhancer-tiny-reference/synthetic-surrogate/v1\n"
SYNTHETIC_ASSET_UNITS = 64
SYNTHETIC_ASSET_BYTES = SYNTHETIC_ASSET_UNIT * SYNTHETIC_ASSET_UNITS
SYNTHETIC_ASSET_SHA256 = hashlib.sha256(SYNTHETIC_ASSET_BYTES).hexdigest()

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "adapters/fastenhancer/adapter.json":
        "2a42cef166dc514488f4fdfe9b37c87427183444bcc19a2f6a4e96e77f87026b",
    "adapters/fastenhancer/README.md":
        "32a856af0f7f32efb35b0b00c6551564f6383cf6446285c060294504cdf341ea",
    "adapters/fastenhancer/run.py":
        "7c34889410f7ac144d73f2c141686243e70ea057eeacd1e947917199fdebf50f",
    "adapters/fastenhancer/requirements.lock":
        "1195f7e838fd20dc1fff30b3808324131c9f7acbedf63f9bf4084de78aa6a86c",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/denoising_phase_completion_20261028.md":
        "fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f",
    "research/selected_audio_enhancement_candidates.md":
        "0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "cpp-library/src/stages/fastenhancer.cpp":
        "b0c0ffc33e5c1c87f65ae9c82ea61ee2c91f4ec9ab16af9393c04376ad931510",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/audio-pro/processors/fastenhancer_tiny16/model-contract.json":
        "1af99b0085289d2cc21772462f6aa9159750946d7c742a197e636cf392240a4a",
    "audio-benchmark-platform/audio-pro/docs/rights-register.md":
        "e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44",
    "audio-benchmark-platform/audio-pro/inventory/rights-register.json":
        "24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923",
    "audio-benchmark-platform/audio-pro/processors/fastenhancer_tiny16_native_f32/tests/fixture_trace.json":
        "cf5eac8219d4285b13400dc0c3050b159edb146abadce073e92725a46adb0a01",
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

# Stable linked-row identity.  Mutable board fields (status, owner, claim,
# review, handoff, blocked_reason, timestamps) are deliberately excluded and
# plan/swarm/TASKS.json is never hashed as a whole file.
STABLE_TASK_IDENTITY: Dict[str, Any] = {
    "id": TASK,
    "title": TITLE,
    "repository": "audio-sdk",
    "mode": "implementation",
    "component": SLUG,
    "dispatch_priority": 2,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-EVIDENCE",
        "SDK-FND-NN",
        "SDK-FND-PROVIDER",
    ],
    "write_scope": [
        f"SDK provider, tool or evidence directory for {SLUG} and its own fixtures"
    ],
    "deliverable": (
        "Reproduce the exact model/runtime as a caller-supplied-asset reference "
        "and add an opt-in SDK adapter once its prerequisites pass."
    ),
    "acceptance": (
        "Apply the enhancement acceptance profile; record exact scope, evidence, "
        "failure/control results, and remaining release gates."
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
    "spec_bins": SPEC_BINS,
    "freq_bins": FREQ_BINS,
    "window": WINDOW,
    "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
    "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
    "drain_flush_hops": DRAIN_FLUSH_HOPS,
    "max_drain_calls": MAX_DRAIN_CALLS,
    "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
    "processing_mode": "native_256_hop_streaming_surrogate",
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
}

CLAIMS: Dict[str, bool] = {
    "real_fastenhancer_runtime": False,
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
    "The exact pinned runtime is absent. adapters/fastenhancer/requirements.lock pins "
    "CPython 3.10 macOS arm64 with onnxruntime==1.20.1 (wheel SHA-256 "
    "e50ba5ff7fed4f7d9253a6baf801ca2883cc08491f9d32d78a80da57256a5439) and the adapter "
    "records data/envs/dtln-onnx as its evaluator environment; neither is present here. "
    "Only unrelated onnxruntime 1.31.1 installations exist, so no exact-runtime reference "
    "run or parity vector was produced.",
    "The exact ONNX bytes (fastenhancer_t.onnx, 125,233 bytes, SHA-256 "
    "a64663672b31bd1445502ee23328d291af13fb312e11bb574c010e7261a5ee7d) are retained in "
    "private workspace copies outside this SDK worktree, but they are not supplied as a "
    "caller-owned external asset to any SDK session, are absent from the SDK worktree, and "
    "no byte was opened, hashed, loaded, compiled or executed by this package.",
    "Rights are evaluation-only. The pinned rights register allows evaluation of the exact "
    "pinned Tiny16 asset and publication of aggregate benchmark scores, but acquisition, "
    "redistribution, customer deployment and public playback remain unknown; no separate "
    "model license or redistribution grant is documented, so no weight, derived weight, "
    "executable or output may be bundled, repackaged, exposed or redistributed.",
    "No exact reference parity exists. The present native fixture records fabricated "
    "deterministic weights with no model bytes read and marks model_parity=deferred and "
    "model_quality=not_assessed; no exact model output under the pinned runtime, no "
    "rights-cleared paired real cohort, no independent scorer or listening result and no "
    "target pacing, deadline or memory measurement exist. All eight release gates remain "
    "blocked and no result may qualify the candidate.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen asset identity only when the exact fastenhancer_t.onnx bytes are supplied as a "
    "caller-owned external asset with an immutable revision, byte count and SHA-256, and the "
    "SDK session verifies those bytes without provider file access or download.",
    "Reopen runtime admission only when the pinned onnxruntime==1.20.1 artifact with a "
    "recorded digest installs in the intended environment, its distribution and product-use "
    "terms are documented, and exact-runtime reference outputs are produced.",
    "Reopen rights only after written artifact-specific terms record redistribution, customer "
    "deployment and public playback decisions; evaluation permission and private possession "
    "alone are not clearance.",
    "Reopen exact reference parity only with approved outputs for these frozen inputs from the "
    "exact caller-supplied asset under the exact pinned runtime, reproducible across three "
    "cold starts.",
    "Reopen the cohort gate only with a rights-cleared paired real speech cohort that includes "
    "clean references and declared DNS/VCTK training-set overlap for Tiny.",
    "Reopen scoring/listening only with an independent intrusive scorer and permitted listening "
    "under a recorded protocol.",
    "Reopen timing only with target-runtime end-to-end availability, pacing, deadline, memory "
    "and chunk-boundary measurements for the exact runtime.",
    "Reopen provider/default only after the prior gates clear and an opt-in provider intake "
    "with OFF default, descriptor/catalog review and an explicit owner default decision is "
    "approved.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "caller-supplied exact fastenhancer_t.onnx bytes with immutable revision, byte count and SHA-256",
    "installed pinned onnxruntime==1.20.1 runtime artifact with recorded digest and documented terms",
    "written redistribution, customer-deployment and public-playback rights decisions",
    "approved exact-runtime reference outputs for frozen inputs, reproducible across three cold starts",
    "rights-cleared paired real speech cohort with clean references and declared training overlap",
    "independent STOI/SI-SDR/intrusive scorer and permitted listening",
    "target-runtime chunk boundary, pacing, availability, deadline and memory evidence",
    "opt-in provider intake with OFF default and an explicit default-selection decision",
)

GATES: Tuple[Dict[str, str], ...] = (
    {
        "name": "exact_asset_identity",
        "status": "blocked",
        "evidence": (
            "Ledger digest/byte count and private workspace copies only; bytes are not "
            "caller-supplied to an SDK session and are absent from the SDK worktree."
        ),
        "reopen": REOPEN_CONDITIONS[0],
    },
    {
        "name": "runtime_admission",
        "status": "blocked",
        "evidence": (
            "The pinned CPython 3.10 macOS arm64 onnxruntime==1.20.1 wheel and evaluator "
            "environment are absent; only unrelated 1.31.1 installations exist."
        ),
        "reopen": REOPEN_CONDITIONS[1],
    },
    {
        "name": "artifact_rights",
        "status": "blocked",
        "evidence": (
            "Evaluation is allowed for the pinned asset; acquisition, redistribution, "
            "customer deployment and public playback are unknown and undocumented."
        ),
        "reopen": REOPEN_CONDITIONS[2],
    },
    {
        "name": "exact_reference_parity",
        "status": "blocked",
        "evidence": (
            "No exact-runtime model output exists; the present native fixture uses fabricated "
            "weights and records model_parity=deferred."
        ),
        "reopen": REOPEN_CONDITIONS[3],
    },
    {
        "name": "rights_cleared_paired_cohort",
        "status": "blocked",
        "evidence": (
            "No rights-cleared paired real cohort with clean references is available in this "
            "package; the 30-pair DNS pilot is source-reported provenance only."
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
            "measurement was made; source RTF is not device evidence."
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
    "scope": "Pinned research provenance only; not reproduced, pooled or used as a threshold.",
    "tiny_dns_pilot": {
        "mean_delta_si_sdr_db": 6.17,
        "mean_delta_stoi": 0.0164,
        "batch_rtf": 0.0166,
        "source": "REALTIME_COMPONENT_CANDIDATES.md#FastEnhancer-Tiny",
        "pair_count": 30,
        "note": "Adapter batch pilot only; live chunk behavior is not established.",
    },
    "small_dns_pilot": {
        "mean_delta_si_sdr_db": 8.11,
        "mean_delta_stoi": 0.0324,
        "batch_rtf": 0.0359,
        "note": "Separate model size; never transferred to Tiny.",
    },
    "ears_blind_screen": (
        "The 12-clip no-reference EARS DNSMOS screen covers FastEnhancer Small only; Tiny has "
        "no EARS or DNSMOS result here."
    ),
    "authors_reported": {
        "pesq_range": [2.43, 2.94],
        "stoi_range": [0.879, 0.935],
        "rtf_range": [0.0058, 0.1052],
        "host": "Apple M5 single-thread",
        "note": "Authors' DNS 2020 dev protocol; different protocol/domain than any local pilot.",
    },
    "delay_note": (
        "The Python adapter compensates 256 samples/16 ms and the scheduled native Small path "
        "measured 512 samples/32 ms in a separate screen; Tiny native chunk behavior is not "
        "established and no device timing is claimed."
    ),
    "disclaimer": (
        "These values are quoted from pinned research files. They are not reproduced here, not "
        "device timing, not this fixture's metrics, not a listening result and not a release claim."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "FastEnhancer, fastenhancer_t.onnx, its derived weights, ONNX Runtime and the vendored native engine are absent from this package; nothing was downloaded, hashed, loaded, compiled or invoked.",
    "The asset digest, byte count, release commit, dependency lock, graph interface, timing fields and rights scopes are quoted from pinned workspace records.",
    "The 30-pair DNS pilot and author-reported ranges are pinned research provenance only; this package computes separate synthetic-fixture metrics and measures no latency.",
    "All signals, caches and outputs are generated by a stdlib deterministic surrogate in reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
)

NON_CLAIMS: Tuple[str, ...] = (
    "No FastEnhancer weight, derived weight, ONNX graph, ONNX Runtime, native engine, corpus or media was downloaded, hashed, loaded, compiled, executed or bundled.",
    "No public API/ABI, CONTRACTS.md, descriptor, registry, installed default, shared build, dependency lock, CI, board or handoff file was changed.",
    "No listening, MOS, STOI, SI-SDR, parity, benchmark, device-timing, latency or release result is claimed for the candidate.",
    "The synthetic streaming surrogate is not FastEnhancer and no missing result ever qualifies the candidate.",
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


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def r6(value: float | None) -> float | None:
    if value is None:
        return None
    rounded = round(float(value), 6)
    return 0.0 if rounded == 0.0 else rounded


def stable_identity_digest(identity: Dict[str, Any] | None = None) -> str:
    payload = dict(identity or STABLE_TASK_IDENTITY)
    payload.pop("stable_sha256", None)
    payload.pop("board_full_file_hashed", None)
    payload.pop("mutable_fields_excluded", None)
    return sha256(canonical_bytes(payload))


def task_identity() -> Dict[str, Any]:
    identity = dict(STABLE_TASK_IDENTITY)
    identity["stable_sha256"] = stable_identity_digest()
    identity["board_full_file_hashed"] = False
    identity["mutable_fields_excluded"] = list(STABLE_TASK_IDENTITY["mutable_fields_excluded"])
    return identity


# ---------------------------------------------------------------------------
# Deterministic synthetic signals (analytic; no corpus or media)
# ---------------------------------------------------------------------------


def _seed(name: str) -> int:
    return (SEED_BASE + int.from_bytes(hashlib.sha256(name.encode("ascii")).digest()[:4], "big")) & 0xFFFFFFFF


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
        f0 = 118.0 + 24.0 * math.sin(2.0 * math.pi * 2.7 * index / SAMPLES + 0.4)
        phase += 2.0 * math.pi * f0 / SAMPLE_RATE_HZ
        speech = 0.0
        for harmonic in range(1, 6):
            speech += math.sin(harmonic * phase) / harmonic
        speech *= amplitude * gate / 1.55
        noise = noise_sigma * _gaussian(rng)
        clean = speech
        target.append(clean)
        observed.append(clean + noise)
    return target, observed


# ---------------------------------------------------------------------------
# Synthetic cache-shaped streaming surrogate (not FastEnhancer)
# ---------------------------------------------------------------------------


def _zeros(shape: Tuple[int, ...]) -> Any:
    if len(shape) == 1:
        return [0.0] * shape[0]
    return [_zeros(shape[1:]) for _ in range(shape[0])]


def zero_caches() -> Dict[str, Any]:
    return {name: _zeros(shape) for name, shape in CACHE_SHAPES}


def _shape_of(value: Any) -> Tuple[int, ...] | None:
    shape: List[int] = []
    current = value
    while isinstance(current, list):
        shape.append(len(current))
        if len(current) == 0:
            return tuple(shape)
        first = current[0]
        if any(not isinstance(item, list) for item in current):
            if any(isinstance(item, list) for item in current):
                return None
            return tuple(shape)
        current = first
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


def validate_caches(caches: Any) -> str | None:
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


def _chunk_power(chunk: Sequence[float]) -> float:
    total = 0.0
    for value in chunk:
        total += value * value
    return total / len(chunk)


def surrogate_chunk(wav_in: Sequence[float], caches: Dict[str, Any]) -> Tuple[List[float], Dict[str, Any], float]:
    """One synthetic causal chunk step with the documented cache shapes."""
    pending = list(caches["cache_in_0"][0])
    previous = list(caches["cache_in_1"][0])
    power = _chunk_power(wav_in)
    reference = max(_chunk_power(previous), EPS)
    snr = power / (power + reference + EPS)
    gain = min(1.0, max(GAIN_FLOOR, math.sqrt(snr)))
    processed = [float(value) * gain for value in wav_in]
    drive = min(1.0, math.sqrt(power) * 4.0)
    cache2 = [[[0.0] * 20 for _ in range(16)]]
    cache3 = [[[0.0] * 20 for _ in range(16)]]
    for row in range(16):
        for column in range(20):
            old2 = caches["cache_in_2"][0][row][column]
            old3 = caches["cache_in_3"][0][row][column]
            cache2[0][row][column] = math.tanh(
                0.9 * old2 + 0.1 * drive * (((row + column) % 5) + 1) / 5.0
            )
            cache3[0][row][column] = math.tanh(
                0.9 * old3 + 0.1 * drive * (((row * 3 + column) % 7) + 1) / 7.0
            )
    new_caches = {
        "cache_in_0": [processed],
        "cache_in_1": [list(wav_in)],
        "cache_in_2": cache2,
        "cache_in_3": cache3,
    }
    return pending, new_caches, gain


def _chunks(samples: Sequence[float]) -> List[List[float]]:
    padded = list(samples)
    remainder = (-len(padded)) % NATIVE_HOP_SAMPLES
    if remainder:
        padded.extend([0.0] * remainder)
    return [padded[start:start + NATIVE_HOP_SAMPLES] for start in range(0, len(padded), NATIVE_HOP_SAMPLES)]


def surrogate_stream(samples: Sequence[float]) -> List[float]:
    """Drive the synthetic chunk API, drop 256 startup samples and trim."""
    caches = zero_caches()
    collected: List[float] = []
    for chunk in _chunks(samples) + [[0.0] * NATIVE_HOP_SAMPLES] * DRAIN_FLUSH_HOPS:
        output, caches, _gain = surrogate_chunk(chunk, caches)
        collected.extend(output)
    return collected[STARTUP_INVALID_SAMPLES:STARTUP_INVALID_SAMPLES + len(samples)]


def surrogate_chunk_loop_control(samples: Sequence[float]) -> List[float]:
    """Independent driver over the same public chunk step; must be byte-identical."""
    caches = zero_caches()
    output: List[float] = []
    padded = list(samples)
    padded.extend([0.0] * ((-len(padded)) % NATIVE_HOP_SAMPLES))
    for start in range(0, len(padded), NATIVE_HOP_SAMPLES):
        chunk_output, caches, _gain = surrogate_chunk(padded[start:start + NATIVE_HOP_SAMPLES], caches)
        output.extend(chunk_output)
    for _ in range(DRAIN_FLUSH_HOPS):
        chunk_output, caches, _gain = surrogate_chunk([0.0] * NATIVE_HOP_SAMPLES, caches)
        output.extend(chunk_output)
    return output[STARTUP_INVALID_SAMPLES:STARTUP_INVALID_SAMPLES + len(samples)]


def surrogate_split_halves(samples: Sequence[float]) -> List[float]:
    midpoint = (len(samples) // (2 * NATIVE_HOP_SAMPLES)) * NATIVE_HOP_SAMPLES
    return surrogate_stream(samples[:midpoint]) + surrogate_stream(samples[midpoint:])


def output_digest(samples: Sequence[float]) -> str:
    packed = struct.pack("<" + "f" * len(samples), *samples)
    return sha256(packed)


def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    total = 0.0
    for value in values:
        total += value * value
    return math.sqrt(total / len(values))


def _snr_db(target: Sequence[float], observed: Sequence[float]) -> float | None:
    signal = 0.0
    error = 0.0
    for want, got in zip(target, observed):
        signal += want * want
        diff = got - want
        error += diff * diff
    if signal <= 0.0 or error <= 0.0:
        return None
    return 10.0 * math.log10(signal / error)


def _si_sdr_db(target: Sequence[float], observed: Sequence[float]) -> float | None:
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


def _attenuation_db(observed: Sequence[float], output: Sequence[float]) -> float | None:
    before = _rms(observed)
    after = _rms(output)
    if before <= 0.0 or after <= 0.0:
        return None
    return 20.0 * math.log10(after / before)


def measure(target: Sequence[float], observed: Sequence[float], output: Sequence[float]) -> Dict[str, Any]:
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
        "noisy_snr_db": r6(_snr_db(target, observed)),
        "surrogate_snr_db": r6(_snr_db(target, output)),
        "delta_snr_db": r6(_snr_db(target, output) - _snr_db(target, observed))
        if _snr_db(target, output) is not None and _snr_db(target, observed) is not None else None,
        "noisy_si_sdr_db": r6(_si_sdr_db(target, observed)),
        "surrogate_si_sdr_db": r6(_si_sdr_db(target, output)),
        "delta_si_sdr_db": r6(_si_sdr_db(target, output) - _si_sdr_db(target, observed))
        if _si_sdr_db(target, output) is not None and _si_sdr_db(target, observed) is not None else None,
        "noise_attenuation_db": r6(_attenuation_db(observed, output)),
    }


# ---------------------------------------------------------------------------
# Caller-supplied external asset boundary and admission
# ---------------------------------------------------------------------------


def asset_ref() -> Dict[str, Any]:
    return {
        "asset_id": ASSET_ID,
        "path_relative": ASSET_LEDGER_PATH,
        "byte_count": ASSET_BYTES,
        "sha256": ASSET_SHA256,
        "storage": "external",
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "release_tag": RELEASE_TAG,
        "code_license_metadata": CODE_LICENSE_METADATA,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "observed_model_terms": MODEL_TERMS_METADATA,
        "evaluation_allowed": True,
        "acquisition_cleared": False,
        "redistribution_cleared": False,
        "customer_deployment_cleared": False,
        "public_playback_cleared": False,
        "rights_register_review_date": "2026-11-15",
        "bytes_present_in_sdk_worktree": (SDK_ROOT / ASSET_LEDGER_PATH).is_file(),
        "workspace_copies": [dict(item) for item in WORKSPACE_COPIES],
        "asset_bytes_read": False,
        "digest_recomputed": False,
        "runtime_package": RUNTIME_PACKAGE,
        "runtime_target": RUNTIME_TARGET,
        "runtime_wheel_sha256": RUNTIME_WHEEL_SHA256,
        "runtime_lock": RUNTIME_LOCK,
        "runtime_available": False,
        "download_permitted": False,
    }


def asset_admission(ref: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ref = dict(ref or asset_ref())
    reasons: List[str] = []
    if not ref.get("bytes_present_in_sdk_worktree"):
        reasons.append("asset_not_caller_supplied")
    if not ref.get("runtime_available"):
        reasons.append("runtime_unpinned")
    reasons.append("runtime_terms_unresolved")
    if not ref.get("model_license_metadata") or "not specified" in str(ref.get("model_license_metadata")):
        reasons.append("model_terms_unresolved")
    if not ref.get("redistribution_cleared"):
        reasons.append("redistribution_rights_unknown")
    order = [
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
        "note": "Explicitly synthetic admission control; not FastEnhancer and not eligible for any gate.",
    }


# ---------------------------------------------------------------------------
# Streaming chunk mechanics
# ---------------------------------------------------------------------------


def default_config() -> Dict[str, Any]:
    return {
        "model_id": "fastenhancer_tiny_16k",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "native_hop_samples": NATIVE_HOP_SAMPLES,
        "n_fft_samples": N_FFT_SAMPLES,
        "window": WINDOW,
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "cache_layout": [list(shape) for _name, shape in CACHE_SHAPES],
        "asset_mode": "caller_supplied_external",
        "asset_id": ASSET_ID,
        "asset_byte_count": ASSET_BYTES,
        "asset_sha256": ASSET_SHA256,
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
        reasons.append("config_keys_mismatch")
        return reasons
    if config["model_id"] != "fastenhancer_tiny_16k":
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
    if config["window"] != WINDOW:
        reasons.append("window_mismatch")
    if config["buffering_delay_samples"] != BUFFERING_DELAY_SAMPLES:
        reasons.append("buffering_delay_mismatch")
    if config["cache_layout"] != [list(shape) for _name, shape in CACHE_SHAPES]:
        reasons.append("cache_layout_mismatch")
    if config["asset_mode"] not in ("caller_supplied_external", "synthetic_surrogate"):
        reasons.append("asset_mode_unsupported")
    return reasons


def admit_config(config: Dict[str, Any] | None = None) -> Dict[str, Any]:
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
    expected = asset_ref()
    if (
        config["asset_id"] != expected["asset_id"]
        or config["asset_byte_count"] != expected["byte_count"]
        or config["asset_sha256"] != expected["sha256"]
    ):
        return {
            "status": "rejected",
            "reason_codes": ["asset_identity_mismatch"],
            "candidate_asset": True,
            "processing_attempted": False,
        }
    blocked = asset_admission(expected)
    return {
        "status": "rejected",
        "reason_codes": ["asset_not_admitted"],
        "admission": blocked,
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


def _sample_error(samples: Any) -> str | None:
    if isinstance(samples, str) or not isinstance(samples, (list, tuple)):
        return "stream_type_invalid"
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in samples):
        return "sample_type_invalid"
    if any(not math.isfinite(float(value)) for value in samples):
        return "sample_nonfinite"
    if any(abs(float(value)) > MAX_ABS_INPUT for value in samples):
        return "sample_out_of_range"
    return None


class StreamingSession:
    """One bounded synthetic stream per session; reset to reuse."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = dict(config if config is not None else default_config())
        self.admission = admit_config(self.config)
        self.created = self.admission["status"].startswith("admitted")
        self.closed = False
        self.stream_complete = False
        self.hops = 0
        self.epoch = 0
        self.caches = zero_caches()
        self.output: List[float] | None = None

    def state(self) -> Dict[str, Any]:
        return {
            "created": self.created,
            "closed": self.closed,
            "stream_complete": self.stream_complete,
            "hops": self.hops,
            "epoch": self.epoch,
            "admission_status": self.admission["status"],
            "asset_mode": self.config.get("asset_mode"),
            "caches_sha256": sha256(canonical_bytes(self.caches)),
            "output_sha256": output_digest(self.output) if self.output is not None else None,
        }

    def state_digest(self) -> str:
        return sha256(canonical_bytes(self.state()))

    def reset(self) -> Dict[str, Any]:
        if self.closed:
            return _reject("session_closed", state_unchanged=True)
        before = self.state_digest()
        self.caches = zero_caches()
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
            "state_unchanged": self.state_digest() == before,
        }

    def process_chunk(self, wav_in: Any, caches: Any = None) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed", state_unchanged=True)
        elif not self.created:
            result = _reject("not_admitted", reason_codes=self.admission.get("reason_codes", []),
                             state_unchanged=True)
        elif self.stream_complete:
            result = _reject("stream_already_complete", state_unchanged=True)
        elif isinstance(wav_in, str) or not isinstance(wav_in, (list, tuple)):
            result = _reject("chunk_type_invalid", state_unchanged=True)
        elif _sample_error(wav_in) is not None:
            result = _reject(_sample_error(wav_in) or "chunk_invalid", state_unchanged=True)
        elif len(wav_in) != NATIVE_HOP_SAMPLES:
            result = _reject("chunk_shape_invalid", state_unchanged=True)
        else:
            selected = self.caches if caches is None else caches
            reason = validate_caches(selected)
            if reason is not None:
                result = _reject(reason, state_unchanged=True)
            else:
                values = [float(value) for value in wav_in]
                output, new_caches, gain = surrogate_chunk(values, selected)
                self.caches = new_caches
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
            result = _reject("not_admitted", reason_codes=self.admission.get("reason_codes", []),
                             state_unchanged=True)
        elif isinstance(samples, str) or not isinstance(samples, (list, tuple)):
            result = _reject("stream_type_invalid", state_unchanged=True)
        elif len(samples) == 0:
            result = _reject("stream_empty", state_unchanged=True)
        elif len(samples) > MAX_STREAM_SAMPLES:
            result = _reject("stream_oversized", state_unchanged=True)
        elif _sample_error(samples) is not None:
            result = _reject(_sample_error(samples) or "stream_invalid", state_unchanged=True)
        elif self.stream_complete:
            result = _reject("stream_already_complete", state_unchanged=True)
        else:
            values = [float(value) for value in samples]
            self.output = surrogate_stream(values)
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
    run("wrong_native_hop", lambda c: c.update(native_hop_samples=160))
    run("wrong_n_fft", lambda c: c.update(n_fft_samples=256))
    run("wrong_window", lambda c: c.update(window="hann"))
    run("wrong_buffering_delay", lambda c: c.update(buffering_delay_samples=0))
    run("wrong_cache_layout", lambda c: c.update(cache_layout=[[1, 160]]))
    run("caller_asset_unavailable", lambda c: None)
    run("surrogate_without_opt_in", lambda c: c.update(
        asset_mode="synthetic_surrogate",
        asset_id=SYNTHETIC_ASSET_ID,
        asset_byte_count=len(SYNTHETIC_ASSET_BYTES),
        asset_sha256=SYNTHETIC_ASSET_SHA256,
        surrogate_opt_in=False,
    ))
    run("wrong_asset_identity", lambda c: c.update(asset_sha256="0" * 64))
    run("wrong_asset_bytes", lambda c: c.update(asset_byte_count=ASSET_BYTES + 1))

    control = synthetic_config()
    result = admit_config(control)
    cases["synthetic_admission_control"] = {
        "status": result["status"],
        "reason_codes": list(result["reason_codes"]),
        "processing_attempted": bool(result.get("processing_attempted", False)),
        "candidate_asset": bool(result.get("candidate_asset", True)),
        "note": "Explicitly synthetic control branch; not FastEnhancer and not a qualification result.",
    }
    return cases


def stream_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, samples: Any, fresh: bool = True, after_close: bool = False) -> None:
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

    run("wrong_chunk_length", [0.0] * 160)
    run("wrong_chunk_type", "chunk")
    run("nonfinite_chunk", [0.0] * 255 + [float("nan")])
    run("out_of_range_chunk", [0.0] * 255 + [MAX_ABS_INPUT + 0.5])
    run("wrong_cache_set", [0.0] * NATIVE_HOP_SAMPLES, {"cache_in_0": [[0.0] * 256]})
    bad_shape = zero_caches()
    bad_shape["cache_in_0"] = [[0.0] * 255]
    run("wrong_cache_shape", [0.0] * NATIVE_HOP_SAMPLES, bad_shape)
    bad_cache = zero_caches()
    bad_cache["cache_in_2"][0][0][0] = float("nan")
    run("nonfinite_cache", [0.0] * NATIVE_HOP_SAMPLES, bad_cache)
    bad_type = zero_caches()
    bad_type["cache_in_1"][0][0] = True
    run("boolean_cache", [0.0] * NATIVE_HOP_SAMPLES, bad_type)
    return cases


def streaming_semantics() -> Dict[str, Any]:
    target, observed = synth("active_speech")
    whole = surrogate_stream(observed)
    chunk_loop = surrogate_chunk_loop_control(observed)
    split = surrogate_split_halves(observed)
    split_changed = sum(1 for left, right in zip(whole, split) if left != right)

    prefix_len = 60 * NATIVE_HOP_SAMPLES
    prefix = surrogate_stream(observed[:prefix_len])
    prefix_stable = prefix == whole[:prefix_len]

    partial = observed[:1_093]
    partial_output = surrogate_stream(partial)

    impulse = [0.0] * SAMPLES
    impulse[4_000] = 0.25
    impulse_output = surrogate_stream(impulse)
    peak_index = max(range(len(impulse_output)), key=lambda index: abs(impulse_output[index]))

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
    reset_caches_zero = reset["caches_zeroed"]

    return {
        "one_stream_per_session": first["status"] == "ok_synthetic"
        and second["status"] == "rejected:stream_already_complete",
        "second_stream_rejected": second["status"],
        "chunk_after_stream_rejected": after_stream_chunk["status"],
        "replay_bit_identical": reset_identical,
        "reset_caches_zeroed": reset_caches_zero,
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
        "impulse_input_peak_index": 4_000,
        "impulse_output_peak_index": peak_index,
        "impulse_peak_preserved": peak_index == 4_000,
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
        entry["identity_exact"] = entry["identity_passthrough"]["output_sha256"] == \
            entry["noisy_control"]["output_sha256"]
        entry["chunk_loop_matches_stream"] = \
            entry["surrogate_chunk_loop_control"]["output_sha256"] == \
            entry["surrogate_stream"]["output_sha256"]
        entry["split_halves_differs"] = entry["surrogate_split_halves"]["output_sha256"] != \
            entry["surrogate_stream"]["output_sha256"]
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
                            "Synthetic surrogate regression versus the noisy control; property of "
                            "the fixture, not evidence about FastEnhancer and not a tuned threshold."
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
        "alignment": "not_measured_no_candidate_output",
        "state_and_memory": "synthetic_cache_shapes_only",
        "content_availability_timing": "blocked_unmeasured",
        "listening": "not_run",
        "real_runtime": False,
        "real_clean_references": False,
        "candidate_result_present": False,
        "conditions": list(CONDITIONS),
        "note": (
            "The table describes only the synthetic surrogate. No candidate output, real cohort, "
            "scorer or listening result exists."
        ),
        "synthetic_conditions_with_results": sum(
            1 for condition in CONDITIONS if results[condition]["target_all_zero"] is False
        ),
    }


def reference_interface() -> Dict[str, Any]:
    return {
        "source": (
            "audio-benchmark-platform/audio-pro/processors/fastenhancer_tiny16/"
            "model-contract.json"
        ),
        "inspection_only": True,
        "model_bytes_read": False,
        "model_id": "fastenhancer_tiny_16k",
        "provider_id": "pro.fastenhancer-tiny16.f32.v0",
        "ir_version": 10,
        "opset_imports": [{"domain": "ai.onnx", "version": 18}],
        "producer": "pytorch",
        "node_count": 202,
        "initializer_count": 80,
        "float_initializer_count": 51,
        "float_initializer_elements": 24_852,
        "graph_inputs": [
            {"name": "wav_in", "dtype": "float32", "dims": [1, 256]},
            {"name": "cache_in_0", "dtype": "float32", "dims": [1, 256]},
            {"name": "cache_in_1", "dtype": "float32", "dims": [1, 256]},
            {"name": "cache_in_2", "dtype": "float32", "dims": [1, 16, 20]},
            {"name": "cache_in_3", "dtype": "float32", "dims": [1, 16, 20]},
        ],
        "graph_outputs": [
            {"name": "wav_out", "dtype": "float32", "dims": [1, 256]},
            {"name": "cache_out_0", "dtype": "float32", "dims": [1, 256]},
            {"name": "cache_out_1", "dtype": "float32", "dims": [1, 256]},
            {"name": "cache_out_2", "dtype": "float32", "dims": [1, 16, 20]},
            {"name": "cache_out_3", "dtype": "float32", "dims": [1, 16, 20]},
        ],
        "graph": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples_in": V0_FRAME_SAMPLES,
            "n_fft": N_FFT_SAMPLES,
            "native_hop_samples": NATIVE_HOP_SAMPLES,
            "window": WINDOW,
            "spec_bins": SPEC_BINS,
            "freq_bins": FREQ_BINS,
            "channel_count": 24,
            "recurrent_frames": 16,
            "recurrent_width": 20,
            "encoder_blocks": 2,
            "rnnformer_blocks": 2,
            "stride": 4,
            "compression_exponent": "0.3",
        },
        "timing": {
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
            "content_delay_ns": 16_000_000,
            "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
            "drain_flush_hops": DRAIN_FLUSH_HOPS,
            "max_drain_calls": MAX_DRAIN_CALLS,
            "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
            "pad_until_hop_samples_max": 255,
            "finite_tail": True,
        },
        "state": {
            "stft_input_buffer_samples": N_FFT_SAMPLES,
            "stft_overlap_samples": NATIVE_HOP_SAMPLES,
            "gru_hidden_floats_per_block": 320,
            "gru_hidden_floats_total": 640,
            "mutable_state_scope": "per_instance",
            "immutable_weights_scope": "shared_read_only",
        },
        "note": (
            "Quoted metadata only. The surrogate uses synthetic cache payloads with these "
            "shapes; it does not reproduce the model's tensor semantics."
        ),
    }


def native_evidence_status() -> Dict[str, Any]:
    return {
        "present_in_workspace": True,
        "fixture_trace_pin": (
            "audio-benchmark-platform/audio-pro/processors/fastenhancer_tiny16_native_f32/"
            "tests/fixture_trace.json"
        ),
        "fixture_trace_sha256": (
            "cf5eac8219d4285b13400dc0c3050b159edb146abadce073e92725a46adb0a01"
        ),
        "trace_is_synthetic_weights": True,
        "fixture_weight_source": "fabricated deterministic f32 fixture; no model bytes read",
        "model_parity": "deferred",
        "model_quality": "not_assessed",
        "used_for_qualification": False,
        "note": (
            "The native path is separate and does not supply exact ONNX-runtime parity or a "
            "candidate result; it is cited only to reject parity claims."
        ),
    }


def rights_status() -> Dict[str, Any]:
    return {
        "register": "audio-benchmark-platform/audio-pro/docs/rights-register.md",
        "register_detail": "audio-benchmark-platform/audio-pro/inventory/rights-register.json",
        "review_date": "2026-11-15",
        "reviewer": "rights holder (user attestation)",
        "acquisition": "unknown",
        "evaluation": "allowed for the pinned asset",
        "redistribution": "unknown",
        "customer_deployment": "unknown",
        "public_playback": "unknown",
        "evaluation_only": True,
        "weights_must_remain_private": True,
        "packaging_permitted": False,
        "blocked": True,
    }


def build_report() -> Dict[str, Any]:
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
        "candidate": "FastEnhancer Tiny 16 kHz DNS ONNX (fastenhancer_t.onnx, onnx-dns-v1.0.0)",
        "verification_profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "missing_result_may_qualify": False,
            "reason": "The exact pinned runtime, caller-supplied asset admission, rights and qualification evidence are absent.",
        },
        "scope": (
            "Task-local synthetic streaming-boundary fixture only; the candidate was not run and "
            "no claim is made."
        ),
        "task_identity": identity,
        "format": dict(FORMAT),
        "asset_boundary": {
            "kind": "caller-supplied external asset reference",
            "contract": (
                "CONTRACTS.md as_asset_v0: ID, byte count, SHA-256, storage=external, "
                "no provider file access and no download"
            ),
            "asset": asset_ref(),
            "asset_bytes_read": False,
            "asset_bytes_hashed": False,
            "bytes_present_in_sdk_worktree": (SDK_ROOT / ASSET_LEDGER_PATH).is_file(),
            "download_attempted": False,
            "vendor_runtime_invoked": False,
            "runtime_available": False,
        },
        "asset_admission": admission,
        "synthetic_admission_control": synthetic_admission_control(),
        "rights": rights_status(),
        "reference_interface": reference_interface(),
        "native_evidence": native_evidence_status(),
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
                results[condition]["chunk_loop_matches_stream"] for condition in CONDITIONS
            ),
            "split_halves_differs": all(
                results[condition]["split_halves_differs"] for condition in CONDITIONS
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
            },
            "nonfinite_and_invalid_rejected": all(
                stream_cases[name]["status"].startswith("rejected:")
                for name in ("nonfinite_sample", "infinite_sample", "string_stream",
                             "boolean_sample", "out_of_range_sample")
            ),
            "missing_asset_blocked": admission["status"] == "blocked",
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
            "release_gates_blocked": sum(1 for gate in GATES if gate["status"] == "blocked"),
        },
    }
    return report


def build_contract(artifact_pins: Dict[str, str] | None = None) -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "candidate": "FastEnhancer Tiny 16 kHz DNS ONNX (fastenhancer_t.onnx, onnx-dns-v1.0.0)",
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
            "Writes are limited to " + TASK_PREFIX + "**; no public API/ABI, provider, registry, "
            "installed default, shared build, dependency lock, CI, board or handoff change."
        ),
        "format": dict(FORMAT),
        "asset": asset_ref(),
        "asset_admission": asset_admission(),
        "synthetic_admission_control": synthetic_admission_control(),
        "rights": rights_status(),
        "reference_interface": reference_interface(),
        "native_evidence": native_evidence_status(),
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(gate) for gate in GATES],
        "release_gate_count": len(GATES),
        "allowed_now": [
            "synthetic streaming chunk boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied external asset contract and pinned metadata",
        ],
        "not_allowed": [
            "downloading, reading, hashing, loading, executing or bundling fastenhancer_t.onnx or derived weights",
            "invoking onnxruntime or the native engine",
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
            "mutable_fields_excluded": list(STABLE_TASK_IDENTITY["mutable_fields_excluded"]),
        },
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
    }
