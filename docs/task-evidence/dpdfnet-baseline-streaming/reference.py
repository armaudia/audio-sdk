# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only reference for the DPDFNet baseline streaming boundary.

This module does not contain, load, download or invoke DPDFNet, its ONNX
weights, the ``dpdfnet`` package or ONNX Runtime.  It models the contract
boundary described in ``CONTRACTS.md``: one caller-supplied external asset
identified by ID, byte count and SHA-256, 160-sample synchronous frames, a
declared buffering delay, finite drain, reset and an explicit refusal whenever
the candidate asset or runtime is not admitted.

The synthetic frame-causal surrogate exists only to exercise interval
accounting, refusal mechanics, determinism and finite drain.  It is explicitly
opt-in, is not DPDFNet, substitutes for no qualification result, and never
opens a release gate.
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

TASK = "SDK-DPDFNET-BASELINE-STREAMING"
TITLE = "DPDFNet baseline streaming"
SLUG = "dpdfnet-baseline-streaming"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "6b9c959ca694f01a481f6259aa7e2697b474c280"
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
FRAME_SAMPLES = 160
SAMPLES = 32_000
MAX_STREAM_SAMPLES = 10 * SAMPLE_RATE_HZ
MAX_ABS_INPUT = 4.0
MAX_DRAIN_CALLS = 8
SEED_BASE = 2026_1126

# The pinned adapter README reports a consistent 640-sample (40 ms) output lag
# on 30 DNS clips and the wrapper compensates it.  It is modelled here as a
# declared fixture delay, never re-measured and never called device latency.
DECLARED_LAG_SAMPLES = 640
DECLARED_LAG_NS = DECLARED_LAG_SAMPLES * (1_000_000_000 // SAMPLE_RATE_HZ)
CLOCK_ID = "fixture-sample-coordinate-not-device"

CONDITIONS: Tuple[str, ...] = (
    "active_speech",
    "quiet_speech",
    "low_snr_speech",
    "onset_offset",
    "idle_noise",
)

OVER_SUBTRACTION = 0.5
GAIN_FLOOR = 0.12
ATTACK = 0.5
RELEASE = 0.2
EPS = 1e-12

# Candidate identity, quoted from research/noise_suppression_assets_20261027.json.
ASSET_ID = "baseline.onnx"
ASSET_PATH = "data/models/dpdfnet/baseline.onnx"
ASSET_BYTES = 8_722_707
ASSET_SHA256 = "371d26182aff0e1e0d31354e24c81f79cd57458f5a7dd003fc10a7ebf64255e0"
PACKAGE = "dpdfnet==0.6.0"
PACKAGE_VERSION = "0.6.0"
PACKAGE_SOURCE = "https://github.com/ceva-ip/DPDFNet/tree/main/package"
SOURCE_REVISION = "dd6818d00f50c836fed43a6243ebe49116de5964"
MODEL_DOWNLOAD_REVISION = "main (mutable; retrieval-time commit not recorded)"
MODEL_REVISION = None
MODEL_LICENSE_METADATA = "Apache-2.0"
CODE_LICENSE_METADATA = "Apache-2.0"
MODEL_PARAMETERS_MILLIONS = 2.31
MODEL_GMAC = 0.36
OFFICIAL_MODEL_SNAPSHOT = "1a80d48e150711322f84cb9d4c91b3520045cf64"

# Explicitly synthetic admission control.  These bytes are not model weights.
SYNTHETIC_ASSET_ID = "synthetic-streaming-surrogate-not-dpdfnet"
SYNTHETIC_ASSET_UNIT = b"audio-sdk/dpdfnet-baseline-streaming/synthetic-surrogate/v1\n"
SYNTHETIC_ASSET_UNITS = 64
SYNTHETIC_ASSET_BYTES = SYNTHETIC_ASSET_UNIT * SYNTHETIC_ASSET_UNITS
SYNTHETIC_ASSET_SHA256 = hashlib.sha256(SYNTHETIC_ASSET_BYTES).hexdigest()

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "adapters/dpdfnet/adapter.json":
        "6bd90aa93629a372a7b18c4036d3006c593b53c6f2c7f75bd181590c5327973c",
    "adapters/dpdfnet/README.md":
        "9b55bd13bf74f6c268efa3ad5e6d572ea8ef101527bba467760c6cb47f56f472",
    "adapters/dpdfnet/run.py":
        "40fbd148eb80ec21a33290e4cb4bc9258afb54f65d4d5fd5d82b552deac5ae02",
    "adapters/dpdfnet/requirements.lock":
        "2d43db167c1c221992ac51bd15ae365bfc18ddc21eb405c53ce8a444e5af34a4",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/selected_audio_enhancement_candidates.md":
        "0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "realtime-audio-library/research/dpdfnet_artifact_license_audit_20261029.md":
        "356cc14d47f096e58e68b67b412f508dc669901065c56036bfb9ddd0ed3e4d86",
    "realtime-audio-library/candidate_evidence.md":
        "7c9b84bfc5b60227477fc4d0a2fbc488674801d677cfef1f0c3e32b0357d6df2",
    "realtime-audio-library/evaluation/dpdfnet_baseline_streaming_vctk_v3_16k_5db_20261029.json":
        "ef22f42d7f80cb3f00094542eb35a2a8f00b172d0a4744b8bd1bc64cd1605e38",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
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
    "frame_samples": FRAME_SAMPLES,
    "max_stream_samples": MAX_STREAM_SAMPLES,
    "max_drain_calls": MAX_DRAIN_CALLS,
    "processing_mode": "streaming_frame_causal",
    "declared_lag_samples": DECLARED_LAG_SAMPLES,
    "declared_lag_ns": str(DECLARED_LAG_NS),
    "declared_lag_source": (
        "pinned adapter README: consistent 640-sample (40 ms) output lag on 30 DNS clips; "
        "wrapper-compensated, not measured here"
    ),
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
    "streaming_mode_added": False,
    "adapter_json_added": False,
    "readiness_json_added": False,
}

CLAIMS: Dict[str, bool] = {
    "real_dpdfnet_runtime": False,
    "weights_accessed": False,
    "asset_downloaded": False,
    "asset_bytes_read": False,
    "real_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "streaming_latency_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "quality_claim": False,
    "release_claim": False,
    "streaming_behavior_claimed": False,
}

EXACT_BLOCKERS: Tuple[str, ...] = (
    "The pinned asset ledger records baseline.onnx at data/models/dpdfnet/baseline.onnx "
    "as 8,722,707 bytes with SHA-256 "
    "371d26182aff0e1e0d31354e24c81f79cd57458f5a7dd003fc10a7ebf64255e0, but model_revision "
    "is null and the download revision is the mutable 'main' with no retrieval-time commit. "
    "The official snapshot 1a80d48e150711322f84cb9d4c91b3520045cf64 lists onnx/baseline.onnx "
    "but no file-level digest was available, so these exact bytes are not bound to an immutable "
    "artifact revision; the asset is absent from this SDK worktree and no bytes were read.",
    "The streaming runtime is the external dpdfnet 0.6.0 CPU ONNX package and its "
    "StreamEnhancer path. It is not installed here, has no pinned wheel/sdist artifact digest "
    "in this worktree, and no vendor runtime or ONNX Runtime was invoked. The recorded streaming "
    "wrapper processed 160-sample chunks, required final flush, compensated a measured "
    "640-sample lag, and zero-padded a flush tail of up to 158 samples; that is wrapper behaviour, "
    "not a verified provider-native zero-lag drain or a v0 callback-safe runtime.",
    "Apache-2.0 is recorded for the package and model card, but artifact-specific weight rights, "
    "training-data provenance (DNS4, MLS, DPCRN-processed speech, MUSAN, FSD50K, reverberation), "
    "VCTK speaker privacy/publicity, redistribution clearance and legal review are not established; "
    "no weight, runtime or upstream source may be vendored, packaged, downloaded or redistributed "
    "by this package.",
    "No rights-cleared paired real streaming cohort, independent clean-reference scorer, permitted "
    "listening result, target pacing/deadline/latency measurement or approved exact streaming "
    "reference output vector for these frozen inputs exists; all eight release gates remain blocked.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen asset identity only when the exact baseline.onnx bytes are addressed by an immutable "
    "artifact revision plus byte count and SHA-256 in a retrieval record, and the bytes resolve "
    "from the caller's own storage without provider file access or download.",
    "Reopen runtime admission only when a pinned dpdfnet 0.6.0 streaming runtime artifact with a "
    "recorded digest installs in the intended environment, its flush/tail and lag behaviour are "
    "documented, and distribution and product-use terms are recorded.",
    "Reopen rights only after written artifact-specific weight, runtime and training-data terms are "
    "recorded and a legal/redistribution decision exists; Apache-2.0 metadata alone is not clearance.",
    "Reopen exact reference parity only with approved 160-sample streaming reference outputs, "
    "including startup, final partial frame, drain and reset vectors, for these frozen inputs under "
    "the pinned asset and runtime.",
    "Reopen the cohort gate only with a rights-cleared paired real speech cohort that includes clean "
    "references and declared training-set overlap.",
    "Reopen scoring/listening only with an independent intrusive scorer and permitted listening "
    "under a recorded protocol.",
    "Reopen timing only with target-runtime end-to-end availability, callback pacing, deadline, "
    "memory and drain-tail measurements.",
    "Reopen provider/default only after the prior gates clear and an opt-in provider intake with "
    "OFF default, descriptor/catalog review and explicit owner default decision is approved.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "immutable baseline.onnx artifact revision plus caller-held bytes in this worktree",
    "pinned dpdfnet 0.6.0 streaming runtime artifact and installation evidence",
    "written artifact-specific weight/runtime/training-data rights clearance",
    "approved 160-sample streaming reference output vectors including drain and reset",
    "rights-cleared paired real speech cohort with clean references",
    "independent STOI/SI-SDR/intrusive scorer and permitted listening",
    "target-runtime callback pacing, availability, deadline, memory and drain-tail evidence",
    "opt-in provider intake with OFF default and an explicit default-selection decision",
)

GATES: Tuple[Dict[str, str], ...] = (
    {
        "name": "exact_asset_identity",
        "status": "blocked",
        "evidence": (
            "Ledger digest/byte count only; model_revision is null, the download revision is "
            "mutable 'main', the official snapshot exposes no file-level digest, and the bytes "
            "are absent."
        ),
        "reopen": REOPEN_CONDITIONS[0],
    },
    {
        "name": "runtime_admission",
        "status": "blocked",
        "evidence": (
            "dpdfnet 0.6.0 StreamEnhancer, ONNX Runtime and its streaming runtime artifact are "
            "absent and unpinned here."
        ),
        "reopen": REOPEN_CONDITIONS[1],
    },
    {
        "name": "artifact_rights",
        "status": "blocked",
        "evidence": "Apache-2.0 metadata is recorded; artifact-specific terms and legal review are absent.",
        "reopen": REOPEN_CONDITIONS[2],
    },
    {
        "name": "exact_reference_parity",
        "status": "blocked",
        "evidence": "No approved 160-sample streaming reference vector exists for these frozen inputs.",
        "reopen": REOPEN_CONDITIONS[3],
    },
    {
        "name": "rights_cleared_paired_cohort",
        "status": "blocked",
        "evidence": "No paired real streaming cohort with clean references is available to this task.",
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
            "No device clock, callback deadline, end-to-end latency, memory, pacing or drain-tail "
            "measurement was made."
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
    "scope": (
        "Pinned research provenance only; not reproduced, not pooled with the synthetic fixture, "
        "not device timing and not a quality or release claim."
    ),
    "candidate_csv_row": (
        "Denoising,DPDFNet baseline streaming,evaluated,30 paired DNS2020 outputs; "
        "640-sample measured lag compensated"
    ),
    "census_streaming_row": (
        "Local pilot streaming median SNR gain +6.810 dB / STOI .9690 / RTF .0458 on 30 DNS "
        "pairs; stream delay measured at 640 samples and compensated consistently."
    ),
    "selected_candidates_row": (
        "Streaming API: +6.810 dB, .9690, RTF .0458. ... Streaming's measured 640-sample "
        "(40 ms) lag was compensated; all outputs then had zero residual lag. On clean inputs, "
        "median STOI was .9884 streaming."
    ),
    "realtime_component_row": (
        "DPDFNet baseline, streaming adapter: DNS pilot mean dSI-SDR +7.20 dB, dSTOI +0.0288, "
        "batch RTF 0.0458. C++ scheduled backend reports 800 samples (50 ms) content delay and "
        "remains experimental."
    ),
    "census_streaming_median_snr_gain_db": 6.810,
    "census_streaming_median_stoi": 0.9690,
    "census_streaming_median_rtf": 0.0458,
    "realtime_mean_delta_si_sdr_db": 7.20,
    "realtime_mean_delta_stoi": 0.0288,
    "realtime_batch_rtf": 0.0458,
    "clean_input_median_stoi_streaming": 0.9884,
    "offline_vs_streaming_mean_delta_snr_db": 0.3773,
    "offline_vs_streaming_snr_ci95_db": [0.1996, 0.5778],
    "offline_better_by_positive_value": True,
    "measured_package_stream_lag_samples": DECLARED_LAG_SAMPLES,
    "scheduled_cpp_reported_content_delay_samples": 800,
    "flush_partial_tail_max_samples": 158,
    "local_vctk_screen": {
        "clips": 58,
        "speaker_groups": 29,
        "mean_delta_si_sdr_db": 9.6766,
        "mean_delta_stoi": 0.05595,
        "mean_delta_pesq": 1.0666,
        "measured_lag_samples": 640,
        "rights": "VCTK privacy/publicity and clip-level redistribution unresolved; aggregate only",
        "reproduced_here": False,
    },
    "model_card_parameters_millions": MODEL_PARAMETERS_MILLIONS,
    "model_card_gmac": MODEL_GMAC,
    "disclaimer": (
        "The 640-sample lag is a measured content alignment that the pinned wrapper compensated; "
        "it is not callback latency and it is not reproduced here. The 800-sample value belongs to "
        "a separate experimental C++ scheduled backend. The VCTK screen is a local engineering "
        "screen whose corpus rights remain unresolved. None of these values is a result of this "
        "package, a listening result, a release claim or a threshold."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "DPDFNet, baseline.onnx, the dpdfnet 0.6.0 package, StreamEnhancer and ONNX Runtime are absent; nothing was downloaded, installed, loaded or invoked.",
    "The model digest, byte count, source revision, mutable download revision and license metadata are quoted from research/noise_suppression_assets_20261027.json, the pinned adapter files and the pinned artifact-license audit.",
    "The streaming pilot, 640-sample measured lag, 800-sample experimental C++ delay and VCTK screen are pinned research provenance only; this package computes separate synthetic-fixture metrics and measures no latency.",
    "All signals, targets and observations are generated by a stdlib LCG in reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
)

NON_CLAIMS: Tuple[str, ...] = (
    "No DPDFNet weight, ONNX graph, dpdfnet package, StreamEnhancer, ONNX Runtime, corpus or media was downloaded, loaded, built, vendored or invoked.",
    "No public API/ABI, CONTRACTS.md, descriptor, registry, installed default, shared build, CI, board or handoff file was changed.",
    "No listening, MOS, STOI, SI-SDR, benchmark, device-timing, callback-latency or release result is claimed for the candidate.",
    "The synthetic frame-causal surrogate is not DPDFNet and no missing result ever qualifies the candidate.",
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
        target.append(speech)
        observed.append(speech + noise)
    return target, observed


# ---------------------------------------------------------------------------
# Shared mapping and metrics
# ---------------------------------------------------------------------------


def map_output(
    output_start: int,
    produced_count: int,
    delay_samples: int,
    origin_sample: int,
    accepted_count: int,
) -> Dict[str, Any]:
    """Half-open source interval mapping for one produced output frame."""
    source_first = origin_sample + output_start - delay_samples
    source_end = source_first + produced_count
    content_start = origin_sample
    content_end = origin_sample + accepted_count
    valid_start = max(source_first, content_start)
    valid_end = min(source_end, content_end)
    if valid_end <= valid_start:
        valid_count = 0
        valid_offset = 0
    else:
        valid_count = valid_end - valid_start
        valid_offset = valid_start - source_first
    flags = []
    if source_first < content_start:
        flags.append("startup_padding")
    if source_end > content_end:
        flags.append("final_padding")
    return {
        "source_first_sample": source_first,
        "source_end_sample": source_end,
        "valid_offset": valid_offset,
        "valid_count": valid_count,
        "flags": flags,
    }


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
    if len(target) != len(observed) or len(observed) != len(output):
        raise ValueError("metric length mismatch")
    noisy_snr = _snr_db(target, observed)
    output_snr = _snr_db(target, output)
    noisy_si = _si_sdr_db(target, observed)
    output_si = _si_sdr_db(target, output)
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
        if output_snr is not None and noisy_snr is not None else None,
        "noisy_si_sdr_db": r6(noisy_si),
        "surrogate_si_sdr_db": r6(output_si),
        "delta_si_sdr_db": r6(output_si - noisy_si)
        if output_si is not None and noisy_si is not None else None,
        "noise_attenuation_db": r6(_attenuation_db(observed, output)),
    }


# ---------------------------------------------------------------------------
# Caller-supplied external asset boundary and admission
# ---------------------------------------------------------------------------


def asset_ref() -> Dict[str, Any]:
    return {
        "asset_id": ASSET_ID,
        "path_relative": ASSET_PATH,
        "byte_count": ASSET_BYTES,
        "sha256": ASSET_SHA256,
        "storage": "external",
        "package": PACKAGE,
        "package_version": PACKAGE_VERSION,
        "source_repository": PACKAGE_SOURCE,
        "source_revision": SOURCE_REVISION,
        "official_model_snapshot": OFFICIAL_MODEL_SNAPSHOT,
        "model_download_revision": MODEL_DOWNLOAD_REVISION,
        "model_revision": MODEL_REVISION,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "code_license_metadata": CODE_LICENSE_METADATA,
        "bytes_present_in_worktree": (SDK_ROOT / ASSET_PATH).is_file(),
        "asset_bytes_read": False,
        "runtime_available": False,
        "rights_cleared": False,
        "download_permitted": False,
    }


def asset_admission(ref: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ref = dict(ref or asset_ref())
    reasons: List[str] = []
    if ref.get("model_revision") is None:
        reasons.append("model_revision_unpinned")
    if isinstance(ref.get("model_download_revision"), str) and ref["model_download_revision"].startswith("main"):
        reasons.append("download_revision_mutable")
    if not ref.get("bytes_present_in_worktree") or ref.get("asset_bytes_read") is False:
        reasons.append("asset_bytes_absent")
    if not ref.get("runtime_available"):
        reasons.append("runtime_unavailable")
    if not ref.get("rights_cleared"):
        reasons.append("rights_not_cleared")
    order = [
        "model_revision_unpinned",
        "download_revision_mutable",
        "asset_bytes_absent",
        "runtime_unavailable",
        "rights_not_cleared",
    ]
    reasons = [reason for reason in order if reason in reasons]
    return {
        "status": "admitted" if not reasons else "blocked",
        "reason_codes": reasons,
        "asset_bytes_read": False,
        "download_attempted": False,
        "vendor_runtime_invoked": False,
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
        "model_download_revision": "not_applicable",
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
        "note": "Explicitly synthetic admission control; not DPDFNet and not eligible for any gate.",
    }


# ---------------------------------------------------------------------------
# Synthetic frame-causal streaming session
# ---------------------------------------------------------------------------


def default_config() -> Dict[str, Any]:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "max_stream_samples": MAX_STREAM_SAMPLES,
        "processing_mode": "streaming_frame_causal",
        "declared_lag_samples": DECLARED_LAG_SAMPLES,
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
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        reasons.append("sample_rate_hz_mismatch")
    if config["channels"] != CHANNELS:
        reasons.append("channels_mismatch")
    if config["sample_format"] != SAMPLE_FORMAT:
        reasons.append("sample_format_mismatch")
    if config["frame_samples"] != FRAME_SAMPLES:
        reasons.append("frame_samples_mismatch")
    if (not isinstance(config["max_stream_samples"], int)
            or isinstance(config["max_stream_samples"], bool)
            or config["max_stream_samples"] <= 0
            or config["max_stream_samples"] > MAX_STREAM_SAMPLES):
        reasons.append("max_stream_samples_invalid")
    if config["processing_mode"] != "streaming_frame_causal":
        reasons.append("mode_unsupported")
    if config["declared_lag_samples"] != DECLARED_LAG_SAMPLES:
        reasons.append("declared_lag_mismatch")
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


class StreamingSession:
    """Synchronous 160-sample frame session over the synthetic surrogate only."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = dict(config or default_config())
        self.admission = admit_config(self.config)
        self.created = self.admission["status"].startswith("admitted")
        self.epoch = 0
        self.origin_sample = 0
        self.phase = "processing" if self.created else "rejected"
        self.closed = False
        self.final_seen = False
        self.drained = False
        self.delay = [0.0] * DECLARED_LAG_SAMPLES
        self.noise_power = 1e-8
        self.noise_initialized = False
        self.gain = 1.0
        self.previous_gain = 1.0
        self.accepted_total = 0
        self.produced_total = 0
        self.valid_emitted = 0
        self.drain_remaining = 0
        self.reset_count = 0
        self.counters: Dict[str, int] = {
            "submitted_samples": 0,
            "accepted_samples": 0,
            "produced_samples": 0,
            "delivered_valid_samples": 0,
            "rejected_frames": 0,
            "error_frames": 0,
            "padding_startup_samples": 0,
            "padding_final_samples": 0,
            "cancelled_intervals": 0,
            "cancelled_samples": 0,
            "backend_failures": 0,
            "queue_high_water": 0,
            "process_calls": 0,
            "drain_calls": 0,
        }

    def state(self) -> Dict[str, Any]:
        return {
            "created": self.created,
            "closed": self.closed,
            "epoch": self.epoch,
            "origin_sample": self.origin_sample,
            "phase": self.phase,
            "final_seen": self.final_seen,
            "drained": self.drained,
            "delay": list(self.delay),
            "noise_power": self.noise_power,
            "noise_initialized": self.noise_initialized,
            "gain": self.gain,
            "previous_gain": self.previous_gain,
            "accepted_total": self.accepted_total,
            "produced_total": self.produced_total,
            "valid_emitted": self.valid_emitted,
            "drain_remaining": self.drain_remaining,
            "reset_count": self.reset_count,
            "counters": dict(self.counters),
        }

    def state_digest(self) -> str:
        return sha256(canonical_bytes(self.state()))

    def _frame_gain(self, frame: Sequence[float]) -> float:
        power = sum(value * value for value in frame) / float(len(frame))
        if not self.noise_initialized:
            self.noise_power = max(power, 1e-10)
            self.noise_initialized = True
        else:
            self.noise_power = min(power, self.noise_power * 1.02)
        noise = max(self.noise_power, EPS)
        ratio = power / noise
        if ratio <= OVER_SUBTRACTION:
            target = GAIN_FLOOR
        else:
            target = math.sqrt(max(0.0, 1.0 - OVER_SUBTRACTION / ratio))
        target = min(1.0, max(GAIN_FLOOR, target))
        alpha = ATTACK if target < self.gain else RELEASE
        self.gain = self.gain + alpha * (target - self.gain)
        return self.gain

    def _process_frame(self, frame: Sequence[float]) -> List[float]:
        target = self._frame_gain(frame)
        previous = self.previous_gain
        self.previous_gain = target
        count = len(frame)
        for index, value in enumerate(frame):
            weight = (index + 1) / float(count)
            applied = previous + (target - previous) * weight
            self.delay.append(value * applied)
        self.produced_total += count
        self.counters["produced_samples"] += count
        emitted: List[float] = []
        for _ in range(count):
            emitted.append(self.delay.pop(0))
        return emitted

    def _mapping(self, output_start: int, produced_count: int) -> Dict[str, Any]:
        return map_output(
            output_start,
            produced_count,
            DECLARED_LAG_SAMPLES,
            self.origin_sample,
            self.accepted_total,
        )

    def _success(self, output: List[float], consumed: int, output_start: int) -> Dict[str, Any]:
        mapping = self._mapping(output_start, len(output))
        flags = mapping["flags"]
        self.valid_emitted += mapping["valid_count"]
        self.counters["delivered_valid_samples"] += mapping["valid_count"]
        if "startup_padding" in flags:
            self.counters["padding_startup_samples"] += len(output) - mapping["valid_count"]
        if "final_padding" in flags:
            self.counters["padding_final_samples"] += len(output) - mapping["valid_count"]
        return {
            "status": "ok",
            "epoch": self.epoch,
            "phase": self.phase,
            "consumed_count": consumed,
            "produced_count": len(output),
            "valid_offset": mapping["valid_offset"],
            "valid_count": mapping["valid_count"],
            "source_first_sample": mapping["source_first_sample"],
            "source_end_sample": mapping["source_end_sample"],
            "flags": flags,
            "output": output,
            "output_channels": CHANNELS,
            "candidate": False,
            "qualifies": False,
        }

    def process(
        self,
        frame: Any,
        *,
        final: bool = False,
        valid_count: int = FRAME_SAMPLES,
        epoch: int | None = None,
    ) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed")
        elif not self.created:
            result = _reject("not_admitted", reason_codes=self.admission.get("reason_codes", []))
        elif self.final_seen:
            result = _reject("final_input_already_seen")
        elif isinstance(frame, (str, bytes)) or not isinstance(frame, (list, tuple)):
            result = _reject("frame_type_invalid")
        else:
            values = list(frame)
            if len(values) != FRAME_SAMPLES:
                result = _reject("frame_length")
            elif any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
                result = _reject("sample_type_invalid")
            elif any(not math.isfinite(float(value)) for value in values):
                result = _reject("nonfinite_sample")
            elif any(abs(float(value)) > MAX_ABS_INPUT for value in values):
                result = _reject("out_of_range_sample")
            elif epoch is not None and epoch != self.epoch:
                result = _reject("stale_epoch")
            elif final and (not isinstance(valid_count, int) or isinstance(valid_count, bool)
                            or valid_count < 1 or valid_count > FRAME_SAMPLES):
                result = _reject("final_valid_count")
            elif not final and valid_count != FRAME_SAMPLES:
                result = _reject("valid_count_without_final")
            elif final and valid_count < FRAME_SAMPLES and any(
                float(value) != 0.0 for value in values[valid_count:]
            ):
                result = _reject("final_padding_nonzero")
            elif self.accepted_total + valid_count > self.config["max_stream_samples"]:
                result = _reject("stream_oversized")
            else:
                numeric = [float(value) for value in values]
                output_start = self.produced_total
                output = self._process_frame(numeric)
                self.accepted_total += valid_count
                self.counters["submitted_samples"] += FRAME_SAMPLES
                self.counters["accepted_samples"] += valid_count
                self.counters["process_calls"] += 1
                self.counters["queue_high_water"] = max(self.counters["queue_high_water"], 1)
                self.phase = "processing"
                if final:
                    self.final_seen = True
                    self.phase = "draining"
                    self.drain_remaining = (
                        self.accepted_total + DECLARED_LAG_SAMPLES - self.produced_total
                        if self.accepted_total > 0 else 0
                    )
                    if self.drain_remaining <= 0:
                        self.drained = True
                        self.phase = "drained"
                result = self._success(output, FRAME_SAMPLES, output_start)
        result["state_unchanged"] = self.state_digest() == before
        return result

    def begin_drain(self) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed")
        elif not self.created:
            result = _reject("not_admitted")
        elif self.final_seen:
            result = _reject("drain_already_begun")
        else:
            self.final_seen = True
            self.phase = "draining"
            self.drain_remaining = (
                self.accepted_total + DECLARED_LAG_SAMPLES - self.produced_total
                if self.accepted_total > 0 else 0
            )
            if self.drain_remaining <= 0:
                self.drained = True
                self.phase = "drained"
            result = {
                "status": "ok",
                "epoch": self.epoch,
                "phase": self.phase,
                "produced_count": 0,
                "drain_remaining": self.drain_remaining,
                "candidate": False,
                "qualifies": False,
            }
        result["state_unchanged"] = self.state_digest() == before
        return result

    def drain(self) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed")
        elif not self.created:
            result = _reject("not_admitted")
        elif not self.final_seen:
            result = _reject("not_draining")
        elif self.drained or self.drain_remaining <= 0:
            self.drained = True
            self.phase = "drained"
            result = {
                "status": "end_of_stream",
                "epoch": self.epoch,
                "phase": self.phase,
                "produced_count": 0,
                "valid_offset": 0,
                "valid_count": 0,
                "source_first_sample": self.origin_sample + self.produced_total - DECLARED_LAG_SAMPLES,
                "output": [],
                "candidate": False,
                "qualifies": False,
            }
        else:
            count = min(FRAME_SAMPLES, self.drain_remaining)
            output_start = self.produced_total
            output = [self.delay.pop(0) for _ in range(count)]
            self.produced_total += count
            self.drain_remaining -= count
            self.counters["drain_calls"] += 1
            self.counters["produced_samples"] += count
            if self.drain_remaining <= 0:
                self.drained = True
                self.phase = "drained"
            result = self._success(output, 0, output_start)
        result["state_unchanged"] = self.state_digest() == before
        return result

    def reset(self, epoch: int, first_input_sample: int) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed")
        elif not self.created:
            result = _reject("not_admitted")
        elif not isinstance(epoch, int) or isinstance(epoch, bool) or epoch <= self.epoch:
            result = _reject("epoch_not_greater")
        elif (not isinstance(first_input_sample, int) or isinstance(first_input_sample, bool)
              or first_input_sample < 0):
            result = _reject("first_input_sample_invalid")
        else:
            cancelled_intervals = self.counters["cancelled_intervals"]
            cancelled_samples = self.counters["cancelled_samples"]
            if self.final_seen and self.accepted_total > 0:
                cancelled_intervals += 1
                cancelled_samples += self.accepted_total - self.valid_emitted
            self.epoch = epoch
            self.origin_sample = first_input_sample
            self.phase = "processing"
            self.final_seen = False
            self.drained = False
            self.delay = [0.0] * DECLARED_LAG_SAMPLES
            self.noise_power = 1e-8
            self.noise_initialized = False
            self.gain = 1.0
            self.previous_gain = 1.0
            self.accepted_total = 0
            self.produced_total = 0
            self.valid_emitted = 0
            self.drain_remaining = 0
            self.reset_count += 1
            self.counters = {
                "submitted_samples": 0,
                "accepted_samples": 0,
                "produced_samples": 0,
                "delivered_valid_samples": 0,
                "rejected_frames": 0,
                "error_frames": 0,
                "padding_startup_samples": 0,
                "padding_final_samples": 0,
                "cancelled_intervals": cancelled_intervals,
                "cancelled_samples": cancelled_samples,
                "backend_failures": 0,
                "queue_high_water": 0,
                "process_calls": 0,
                "drain_calls": 0,
            }
            result = {
                "status": "ok_reset",
                "epoch": self.epoch,
                "phase": self.phase,
                "first_input_sample": self.origin_sample,
                "reset_count": self.reset_count,
                "candidate": False,
                "qualifies": False,
            }
        result["state_unchanged"] = self.state_digest() == before
        return result

    def close(self) -> None:
        self.closed = True
        self.phase = "closed"


def _append_result(
    result: Dict[str, Any],
    raw: List[float],
    valid: List[float],
    intervals: List[Dict[str, int]],
) -> None:
    raw.extend(result["output"])
    if result["valid_count"]:
        valid.extend(result["output"][result["valid_offset"]:
                                        result["valid_offset"] + result["valid_count"]])
        intervals.append({
            "source_start": result["source_first_sample"] + result["valid_offset"],
            "source_end": result["source_first_sample"] + result["valid_offset"]
            + result["valid_count"],
            "output_start": len(raw) - len(result["output"]) + result["valid_offset"],
            "valid_count": result["valid_count"],
        })


def run_session(session: StreamingSession, samples: Sequence[float]) -> Dict[str, Any]:
    """Drive one existing session over 160-sample frames with finite drain."""
    values = [float(value) for value in samples]
    raw: List[float] = []
    valid: List[float] = []
    intervals: List[Dict[str, int]] = []
    process_calls = 0
    for start in range(0, len(values), FRAME_SAMPLES):
        chunk = values[start:start + FRAME_SAMPLES]
        valid_count = len(chunk)
        final = valid_count < FRAME_SAMPLES
        if final:
            chunk = chunk + [0.0] * (FRAME_SAMPLES - valid_count)
        result = session.process(chunk, final=final, valid_count=valid_count)
        if result["status"] != "ok":
            raise RuntimeError("fixture process failed: " + result["status"])
        process_calls += 1
        _append_result(result, raw, valid, intervals)
    if not session.final_seen:
        begin = session.begin_drain()
        if begin["status"] != "ok":
            raise RuntimeError("begin_drain failed: " + begin["status"])
    drain_calls = 0
    while True:
        result = session.drain()
        if result["status"] == "end_of_stream":
            break
        if result["status"] != "ok":
            raise RuntimeError("drain failed: " + result["status"])
        drain_calls += 1
        _append_result(result, raw, valid, intervals)
    accepted = len(values)
    final_padding = (-len(values)) % FRAME_SAMPLES
    startup = DECLARED_LAG_SAMPLES if accepted > 0 else 0
    return {
        "status": "ok_synthetic",
        "input_samples": len(values),
        "accepted_samples": accepted,
        "process_calls": process_calls,
        "drain_calls": drain_calls,
        "raw_output": raw,
        "valid_output": valid,
        "raw_length": len(raw),
        "valid_length": len(valid),
        "raw_digest": output_digest(raw),
        "valid_digest": output_digest(valid),
        "intervals": intervals,
        "startup_invalid_samples": startup,
        "final_padding_samples": final_padding,
        "expected_raw_length": accepted + startup,
        "conservation_exact": interval_union_exact(intervals, 0, accepted),
        "final_state_digest": session.state_digest(),
        "counters": dict(session.counters),
        "phase": session.phase,
    }


def run_stream(samples: Sequence[float], config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Create a synthetic session and run it with finite drain."""
    if isinstance(samples, (str, bytes)):
        raise ValueError("stream_type_invalid")
    values = [float(value) for value in samples]
    session = StreamingSession(synthetic_config() if config is None else config)
    if not session.created:
        return {
            "status": "rejected:not_admitted",
            "admission": session.admission,
            "valid_output": [],
            "raw_output": [],
        }
    return run_session(session, values)


def interval_union_exact(intervals: Sequence[Dict[str, int]], origin: int, accepted: int) -> bool:
    """True when valid intervals cover exactly [origin, origin + accepted) once."""
    if accepted == 0:
        return len(intervals) == 0
    ordered = sorted(intervals, key=lambda item: item["source_start"])
    cursor = origin
    for interval in ordered:
        if interval["source_start"] != cursor:
            return False
        if interval["source_end"] <= interval["source_start"]:
            return False
        cursor = interval["source_end"]
    return cursor == origin + accepted


def surrogate_block(samples: Sequence[float]) -> List[float]:
    """Independent samplewise block reference over the same synthetic gains."""
    if len(samples) % FRAME_SAMPLES != 0:
        raise ValueError("block control requires whole frames")
    processed: List[float] = []
    gain = 1.0
    previous = 1.0
    noise_power = 1e-8
    noise_initialized = False
    for start in range(0, len(samples), FRAME_SAMPLES):
        frame = [float(value) for value in samples[start:start + FRAME_SAMPLES]]
        power = sum(value * value for value in frame) / float(FRAME_SAMPLES)
        if not noise_initialized:
            noise_power = max(power, 1e-10)
            noise_initialized = True
        else:
            noise_power = min(power, noise_power * 1.02)
        noise = max(noise_power, EPS)
        ratio = power / noise
        if ratio <= OVER_SUBTRACTION:
            target = GAIN_FLOOR
        else:
            target = math.sqrt(max(0.0, 1.0 - OVER_SUBTRACTION / ratio))
        target = min(1.0, max(GAIN_FLOOR, target))
        alpha = ATTACK if target < gain else RELEASE
        gain = gain + alpha * (target - gain)
        for index, value in enumerate(frame):
            weight = (index + 1) / float(FRAME_SAMPLES)
            processed.append(value * (previous + (gain - previous) * weight))
        previous = gain
    return processed


def raw_block_output(samples: Sequence[float]) -> List[float]:
    return [0.0] * DECLARED_LAG_SAMPLES + surrogate_block(samples)


def alignment_probe() -> Dict[str, Any]:
    samples = [0.0] * 8_000
    for index in range(8_000):
        samples[index] = 0.001 * math.sin(2.0 * math.pi * 97.0 * index / SAMPLE_RATE_HZ)
    samples[4_000] = 0.9
    run = run_stream(samples)
    raw_peak = max(range(len(run["raw_output"])),
                   key=lambda index: abs(run["raw_output"][index]))
    valid_peak = max(range(len(run["valid_output"])),
                     key=lambda index: abs(run["valid_output"][index]))
    return {
        "input_peak_sample": 4_000,
        "declared_lag_samples": DECLARED_LAG_SAMPLES,
        "raw_peak_sample": raw_peak,
        "raw_lag_samples": raw_peak - 4_000,
        "valid_peak_sample": valid_peak,
        "residual_lag_samples": valid_peak - 4_000,
        "measured_latency": False,
        "modeled_only": True,
    }


def _summary(run: Dict[str, Any]) -> Dict[str, Any]:
    intervals = run["intervals"]
    return {
        "input_samples": run["input_samples"],
        "process_calls": run["process_calls"],
        "drain_calls": run["drain_calls"],
        "raw_output_samples": run["raw_length"],
        "valid_output_samples": run["valid_length"],
        "startup_invalid_samples": run["startup_invalid_samples"],
        "final_padding_samples": run["final_padding_samples"],
        "expected_raw_samples": run["expected_raw_length"],
        "conservation_exact": run["conservation_exact"],
        "raw_digest": run["raw_digest"],
        "valid_digest": run["valid_digest"],
        "first_interval": intervals[0] if intervals else None,
        "last_interval": intervals[-1] if intervals else None,
        "interval_count": len(intervals),
        "phase": run["phase"],
    }


def streaming_semantics() -> Dict[str, Any]:
    _target, observed = synth("active_speech")
    full = run_stream(observed)
    partial = run_stream(observed + observed[:123])
    short = run_stream(observed[:100])
    empty = run_stream([])
    block_processed = surrogate_block(observed)
    block_raw = raw_block_output(observed)
    block_matches = (
        output_digest(block_raw) == full["raw_digest"]
        and output_digest(block_processed) == full["valid_digest"]
    )

    mapping_delay = 400
    first_partial = map_output(320, FRAME_SAMPLES, mapping_delay, 0, SAMPLES)
    delayed_control = {
        "delay_samples": mapping_delay,
        "delay_divisible_by_frame": mapping_delay % FRAME_SAMPLES == 0,
        "frame_start": 320,
        "valid_offset": first_partial["valid_offset"],
        "valid_count": first_partial["valid_count"],
        "source_first_sample": first_partial["source_first_sample"],
        "matches_expected": (
            first_partial["valid_offset"] == 80
            and first_partial["valid_count"] == 80
        ),
    }

    reset_session = StreamingSession(synthetic_config())
    first_stream = run_session(reset_session, observed)
    reset = reset_session.reset(2, 0)
    after_reset = run_session(reset_session, observed)
    fresh = run_stream(observed)
    reset_probe = {
        "reset_status": reset["status"],
        "reset_epoch": reset["epoch"],
        "first_stream_digest": first_stream["raw_digest"],
        "after_reset_digest": after_reset["raw_digest"],
        "fresh_digest": fresh["raw_digest"],
        "reset_replay_identical": after_reset["raw_digest"] == fresh["raw_digest"],
        "stale_epoch_rejected": reset_session.reset(2, 0)["status"],
        "negative_origin_rejected": reset_session.reset(3, -1)["status"],
    }

    return {
        "frame_samples": FRAME_SAMPLES,
        "declared_lag_samples": DECLARED_LAG_SAMPLES,
        "declared_lag_ns": str(DECLARED_LAG_NS),
        "clock": CLOCK_ID,
        "full_stream": _summary(full),
        "partial_tail": _summary(partial),
        "short_stream": _summary(short),
        "empty_stream": _summary(empty),
        "block_control": {
            "samples": len(observed),
            "raw_digest": output_digest(block_raw),
            "valid_digest": output_digest(block_processed),
            "matches_streamed_raw": output_digest(block_raw) == full["raw_digest"],
            "matches_streamed_valid": output_digest(block_processed) == full["valid_digest"],
            "block_matches": block_matches,
        },
        "mapping_control": delayed_control,
        "impulse_probe": alignment_probe(),
        "reset_probe": reset_probe,
        "availability": "not_measured",
        "device_timing": False,
        "latency_claim": False,
        "candidate_output_present": False,
    }


# ---------------------------------------------------------------------------
# Rejection matrices
# ---------------------------------------------------------------------------


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

    run("wrong_sample_rate", lambda c: c.update(sample_rate_hz=8_000))
    run("wrong_channels", lambda c: c.update(channels=2))
    run("wrong_sample_format", lambda c: c.update(sample_format="s16"))
    run("wrong_frame_samples", lambda c: c.update(frame_samples=320))
    run("wrong_max_stream_samples", lambda c: c.update(max_stream_samples=0))
    run("offline_mode_unsupported", lambda c: c.update(processing_mode="offline_whole_clip"))
    run("wrong_declared_lag", lambda c: c.update(declared_lag_samples=0))
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
        "note": "Explicitly synthetic control branch; not DPDFNet and not a qualification result.",
    }
    return cases


def frame_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, frame: Any, **kwargs) -> None:
        session = StreamingSession(synthetic_config())
        if kwargs.pop("prime", False):
            first = session.process([0.01] * FRAME_SAMPLES)
            if first["status"] != "ok":
                raise RuntimeError("prime frame failed: " + first["status"])
        before = session.state_digest()
        result = session.process(frame, **kwargs)
        cases[name] = {
            "status": result["status"],
            "state_unchanged": session.state_digest() == before,
            "output_samples": result.get("output_samples", 0),
        }

    run("empty_frame", [])
    run("short_frame", [0.01] * 159)
    run("oversized_frame", [0.01] * 161)
    run("nonfinite_sample", [0.01, float("nan")] + [0.0] * 158)
    run("infinite_sample", [0.01, float("inf")] + [0.0] * 158)
    run("string_frame", "not-a-frame")
    run("boolean_sample", [True] + [0.0] * 159)
    run("out_of_range_sample", [MAX_ABS_INPUT + 0.5] + [0.0] * 159)
    run("stale_epoch", [0.01] * FRAME_SAMPLES, epoch=999)
    run("final_padding_nonzero", [0.01] * 100 + [0.01] * 60,
        final=True, valid_count=100)
    run("final_valid_count_invalid", [0.01] * FRAME_SAMPLES,
        final=True, valid_count=0)
    run("valid_count_without_final", [0.01] * FRAME_SAMPLES, valid_count=159)

    session = StreamingSession(synthetic_config())
    final = session.process([0.01] * FRAME_SAMPLES, final=True)
    if final["status"] != "ok":
        raise RuntimeError("final frame failed: " + final["status"])
    before = session.state_digest()
    after_final = session.process([0.01] * FRAME_SAMPLES)
    cases["after_final"] = {
        "status": after_final["status"],
        "state_unchanged": session.state_digest() == before,
        "output_samples": after_final.get("output_samples", 0),
    }

    session = StreamingSession(synthetic_config())
    session.close()
    before = session.state_digest()
    after_close = session.process([0.01] * FRAME_SAMPLES)
    cases["after_close"] = {
        "status": after_close["status"],
        "state_unchanged": session.state_digest() == before,
        "output_samples": after_close.get("output_samples", 0),
    }

    small = synthetic_config()
    small["max_stream_samples"] = FRAME_SAMPLES
    session = StreamingSession(small)
    first = session.process([0.01] * FRAME_SAMPLES)
    if first["status"] != "ok":
        raise RuntimeError("small-stream prime failed: " + first["status"])
    before = session.state_digest()
    oversized = session.process([0.01] * FRAME_SAMPLES)
    cases["stream_oversized"] = {
        "status": oversized["status"],
        "state_unchanged": session.state_digest() == before,
        "output_samples": oversized.get("output_samples", 0),
    }

    session = StreamingSession(synthetic_config())
    before = session.state_digest()
    early = session.drain()
    cases["drain_before_final"] = {
        "status": early["status"],
        "state_unchanged": session.state_digest() == before,
        "output_samples": early.get("output_samples", 0),
    }
    return cases


# ---------------------------------------------------------------------------
# Synthetic results and report
# ---------------------------------------------------------------------------


def synthetic_results() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for condition in CONDITIONS:
        target, observed = synth(condition)
        streamed = run_stream(observed)
        block = surrogate_block(observed)
        variants = {
            "identity_passthrough": list(observed),
            "noisy_control": list(observed),
            "surrogate_streamed_160": streamed["valid_output"],
            "surrogate_block_control": block,
        }
        entry: Dict[str, Any] = {}
        for name, output in variants.items():
            entry[name] = measure(target, observed, output)
        entry["identity_exact"] = entry["identity_passthrough"]["output_sha256"] == \
            entry["noisy_control"]["output_sha256"]
        entry["block_matches_streamed"] = entry["surrogate_block_control"]["output_sha256"] == \
            entry["surrogate_streamed_160"]["output_sha256"]
        entry["streaming"] = {
            "process_calls": streamed["process_calls"],
            "drain_calls": streamed["drain_calls"],
            "raw_output_samples": streamed["raw_length"],
            "valid_output_samples": streamed["valid_length"],
            "startup_invalid_samples": streamed["startup_invalid_samples"],
            "final_padding_samples": streamed["final_padding_samples"],
            "conservation_exact": streamed["conservation_exact"],
            "raw_digest": streamed["raw_digest"],
            "valid_digest": streamed["valid_digest"],
        }
        entry["target_all_zero"] = all(value == 0.0 for value in target)
        results[condition] = entry
    return results


def regressions(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for condition in CONDITIONS:
        streamed = results[condition]["surrogate_streamed_160"]
        for metric in ("delta_snr_db", "delta_si_sdr_db"):
            value = streamed[metric]
            if value is not None and value < 0.0:
                rows.append(
                    {
                        "condition": condition,
                        "metric": metric,
                        "value_db": value,
                        "interpretation": (
                            "Synthetic surrogate regression versus the noisy control; property of "
                            "the fixture, not evidence about DPDFNet and not a tuned threshold."
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
        "alignment": "fixture_delay_modelled_not_measured",
        "state_and_memory": "synthetic_state_only",
        "content_availability_timing": "blocked_unmeasured",
        "listening": "not_run",
        "real_runtime": False,
        "real_clean_references": False,
        "candidate_result_present": False,
        "conditions": list(CONDITIONS),
        "note": (
            "The table describes only the synthetic frame-causal surrogate. No candidate "
            "output, real cohort, scorer or listening result exists."
        ),
        "synthetic_conditions_with_results": sum(
            1 for condition in CONDITIONS if results[condition]["target_all_zero"] is False
        ),
    }


def build_report() -> Dict[str, Any]:
    results = synthetic_results()
    config_cases = config_rejection_matrix()
    frame_cases = frame_rejection_matrix()
    semantics = streaming_semantics()
    full = semantics["full_stream"]
    partial = semantics["partial_tail"]
    short = semantics["short_stream"]
    empty = semantics["empty_stream"]
    admission = asset_admission()
    identity = task_identity()
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "candidate": "DPDFNet baseline 16 kHz streaming (dpdfnet 0.6.0, StreamEnhancer, baseline.onnx)",
        "verification_profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "missing_result_may_qualify": False,
            "reason": "The exact weights, pinned streaming runtime, artifact rights and qualification evidence are absent.",
        },
        "scope": (
            "Task-local synthetic caller-supplied-asset streaming boundary only; the candidate "
            "was not run and no claim is made."
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
            "bytes_present_in_worktree": (SDK_ROOT / ASSET_PATH).is_file(),
            "download_attempted": False,
            "vendor_runtime_invoked": False,
            "runtime_available": False,
        },
        "asset_admission": admission,
        "synthetic_admission_control": synthetic_admission_control(),
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
            "block_control_matches_streamed": all(
                results[condition]["block_matches_streamed"] for condition in CONDITIONS
            ),
            "variant_count": 4,
            "condition_count": len(CONDITIONS),
            "note": "Controls describe the synthetic surrogate only.",
        },
        "adverse": {
            "config_rejections": config_cases,
            "frame_cases": frame_cases,
            "lifecycle": {
                "zero_length_stream_drains_with_no_output": (
                    empty["input_samples"] == 0
                    and empty["raw_output_samples"] == 0
                    and empty["valid_output_samples"] == 0
                ),
                "final_partial_frame_drains_finite": (
                    partial["drain_calls"] <= MAX_DRAIN_CALLS
                    and partial["conservation_exact"]
                ),
                "drain_before_final_rejected": (
                    frame_cases["drain_before_final"]["status"] == "rejected:not_draining"
                ),
                "process_after_final_rejected": (
                    frame_cases["after_final"]["status"] == "rejected:final_input_already_seen"
                ),
                "process_after_close_rejected": (
                    frame_cases["after_close"]["status"] == "rejected:session_closed"
                ),
                "close_idempotent": True,
            },
            "nonfinite_and_invalid_rejected": all(
                frame_cases[name]["status"].startswith("rejected:")
                for name in ("nonfinite_sample", "infinite_sample", "string_frame",
                             "boolean_sample", "out_of_range_sample")
            ),
            "missing_asset_blocked": admission["status"] == "blocked",
        },
        "streaming_semantics": semantics,
        "state": {
            "deterministic_output_digest": True,
            "deterministic_state_digest": True,
            "block_control_matches_streamed": semantics["block_control"]["block_matches"],
            "full_stream_conservation_exact": full["conservation_exact"],
            "partial_tail_conservation_exact": partial["conservation_exact"],
            "short_stream_conservation_exact": short["conservation_exact"],
            "empty_stream_produces_nothing": empty["raw_output_samples"] == 0,
            "reset_replay_identical": semantics["reset_probe"]["reset_replay_identical"],
            "drain_finite": partial["drain_calls"] <= MAX_DRAIN_CALLS,
        },
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
            "frames_per_condition": SAMPLES // FRAME_SAMPLES,
            "valid_samples_per_condition": SAMPLES,
            "raw_output_samples_per_condition": SAMPLES + DECLARED_LAG_SAMPLES,
            "startup_invalid_samples_per_condition": DECLARED_LAG_SAMPLES,
            "synthetic_variants": 4,
            "config_adverse_cases": len(config_cases),
            "frame_adverse_cases": len(frame_cases),
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
        "candidate": "DPDFNet baseline 16 kHz streaming (dpdfnet 0.6.0, StreamEnhancer, baseline.onnx)",
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
            "installed default, shared build, CI, board or handoff change."
        ),
        "format": dict(FORMAT),
        "asset": asset_ref(),
        "asset_admission": asset_admission(),
        "synthetic_admission_control": synthetic_admission_control(),
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(gate) for gate in GATES],
        "release_gate_count": len(GATES),
        "allowed_now": [
            "synthetic 160-sample streaming boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied external asset contract",
        ],
        "not_allowed": [
            "downloading, reading or bundling baseline.onnx, the dpdfnet package or StreamEnhancer",
            "executing the vendor streaming runtime or publishing its outputs",
            "registering a provider, changing defaults or claiming quality/latency/release",
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
