# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only boundary model for the CleanUNet DNS-large-high task.

This module implements **no** neural network.  It models only the documented
whole-clip accounting of the pinned official `CleanUNet.forward()`:

* whole-clip standard-deviation normalisation with the source's ``+ 1e-3`` term,
* zero padding (or truncation) to the exact length produced by the source
  ``padding(x, D=8, K=4, S=2)`` helper,
* one whole-clip call that returns exactly ``min(input, padded)`` samples, and
* rescaling by the original standard deviation.

The signal path itself is an explicit synthetic surrogate, not CleanUNet.  No
checkpoint, PyTorch runtime, corpus or media is present, read or invoked.
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
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml")).resolve()

TASK = "SDK-CLEANUNET-DNS-LARGE-HIGH"
TITLE = "CleanUNet DNS-large-high"
SLUG = "cleanunet-dns-large-high"
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
FRAME_SAMPLES = 160
SAMPLES = 32_000
MAX_CLIP_SAMPLES = 10 * SAMPLE_RATE_HZ
MAX_ABS_INPUT = 4.0
SEED_BASE = 2026_1126
CLOCK_ID = "fixture-sample-coordinate-not-device"

CONDITIONS: Tuple[str, ...] = (
    "active_speech",
    "quiet_speech",
    "low_snr_speech",
    "idle_noise",
    "onset_offset",
)
NOISE_QUANTILE = 0.55
GAIN_FLOOR = 0.12
SMOOTH_RADIUS_FRAMES = 6
EPS = 1e-12

# Pinned network configuration from configs/DNS-large-high.json.
ENCODER_LAYERS = 8
KERNEL_SIZE = 4
STRIDE = 2
CHANNELS_H = 64
MAX_H = 768
TSFM_LAYERS = 5
TSFM_HEADS = 8
TSFM_D_MODEL = 512
TSFM_D_INNER = 2048
TRAIN_CROP_SECONDS = 10
NORM_EPSILON = 1e-3
STRIDE_GRID_SAMPLES = STRIDE ** ENCODER_LAYERS  # 256

# Pinned candidate artifact identity.  The Git LFS object ID is itself the
# SHA-256 of the file, so the bytes are addressable from the immutable commit.
ASSET_ID = "pretrained.pkl"
ASSET_PATH = "data/models/cleanunet/dns-large-high/pretrained.pkl"
ASSET_LFS_PATH = "exp/DNS-large-high/checkpoint/pretrained.pkl"
ASSET_BYTES = 184_336_765
ASSET_SHA256 = "513d9e4f69483bf2bcc3059dd6b3644140763bf3f22df41d7ee366cc2cbd1829"
SOURCE_REPOSITORY = "https://github.com/NVIDIA/CleanUNet"
SOURCE_REVISION = "2f930ce6660e76b6265c07da4027b414adb24ab1"
PACKAGE = f"NVIDIA/CleanUNet@{SOURCE_REVISION}"
CHECKPOINT_FORMAT = "PyTorch torch.save state_dict (pickle; loaded with weights_only=True)"
RUNTIME_RECORDED = "CPython 3.11.5 + PyTorch 2.14.1 + torchaudio 2.11.0, CPU only (recorded in the pinned eval report)"
RUNTIME_LOCK_DIGEST = None
CODE_LICENSE_METADATA = "MIT (pinned repository LICENSE)"
MODEL_LICENSE_METADATA = (
    "MIT repository LICENSE; no separate checkpoint license statement "
    "(README calls the LFS object a pretrained model)"
)
MODEL_DOWNLOAD_REVISION = SOURCE_REVISION

SYNTHETIC_ASSET_ID = "synthetic-whole-clip-surrogate-not-cleanunet"
SYNTHETIC_ASSET_UNIT = b"audio-sdk/cleanunet-dns-large-high/synthetic-surrogate/v1\n"
SYNTHETIC_ASSET_UNITS = 64
SYNTHETIC_ASSET_BYTES = SYNTHETIC_ASSET_UNIT * SYNTHETIC_ASSET_UNITS
SYNTHETIC_ASSET_SHA256 = hashlib.sha256(SYNTHETIC_ASSET_BYTES).hexdigest()

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/voice-enhancement-20261101/agent-cleanunet-readiness/REPORT.md":
        "16be8783b1345d96b65f910fe6364b0996f925c82744b07185d4420f2346b148",
    "research/voice-enhancement-20261101/agent-cleanunet-eval/REPORT.md":
        "062e30c97843d257cabd251ce6991b21d578c5fb96df75e9f3b1399524da66fa",
    "research/voice-enhancement-20261101/agent-cleanunet-eval/adapter.json":
        "d224b980b6444d5ea190645c17fcfebe9d05fe8a8db276c91f3be115ebdc0af7",
    "research/voice-enhancement-20261101/agent-cleanunet-eval/adapter.lock.json":
        "255b756d46e02c1bddc69167e772dfec587d1d36190aa1364bb11bd68fd4a9ab",
    "research/voice-enhancement-20261101/agent-cleanunet-eval/adapter.py":
        "39d401019b4db443194bbfb6973660a6a8eee672e3b76a7a27e6fa5dcfb24c8e",
    "research/voice-enhancement-20261101/agent-cleanunet-eval/cleanunet_noisy_results.json":
        "84ef5edd19ccb2b464b42c30b150c1cfd219e64bf94bc8ac2e47f3a0b621ee4c",
    "research/voice-enhancement-20261101/agent-cleanunet-eval/cleanunet_clean_results.json":
        "0152c89e9caa0e0d1e237f5f86aacdcda018bfbb393cd8a7eb90364dc23d8515",
    "research/voice-enhancement-20261101/agent-cleanunet-result-audit/REPORT.md":
        "2456cd2c570ef79d55a82169c9fb00488554fd3611a95140848a466ecf87f93f",
    "research/voice-enhancement-20261101/evaluation_records.md":
        "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "data/checkouts/cleanunet/configs/DNS-large-high.json":
        "e2a115f1a5e983b22fc6a2e95bca27c4f93625390205327575d9b963467b5063",
    "data/checkouts/cleanunet/network.py":
        "c5ba1b7bb4ad7afc4697e597bc5a373715ed7d73af36d8043a9f971d56926957",
    "data/checkouts/cleanunet/util.py":
        "619bd6ac680b6432816a15fd302881e2100baea6e83ceef4d61e23a19cf1ef7f",
    "data/checkouts/cleanunet/LICENSE":
        "da9858d516047d82096d01c112a61bd67f26d289039464d668a1d45f91738ecc",
    "data/checkouts/cleanunet/README.md":
        "ba48ec3c4e4a7b1afad57f4fbb0f34a7f76087f3ec5c2652e1c84cd5546796e7",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "LICENSES/Apache-2.0.txt": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}

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
    "max_clip_samples": MAX_CLIP_SAMPLES,
    "processing_mode": "offline_whole_clip",
    "clock": CLOCK_ID,
}

ARCHITECTURE: Dict[str, Any] = {
    "config": "configs/DNS-large-high.json",
    "channels_input": 1,
    "channels_output": 1,
    "channels_H": CHANNELS_H,
    "max_H": MAX_H,
    "encoder_n_layers": ENCODER_LAYERS,
    "kernel_size": KERNEL_SIZE,
    "stride": STRIDE,
    "tsfm_n_layers": TSFM_LAYERS,
    "tsfm_n_head": TSFM_HEADS,
    "tsfm_d_model": TSFM_D_MODEL,
    "tsfm_d_inner": TSFM_D_INNER,
    "train_crop_seconds": TRAIN_CROP_SECONDS,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "stride_grid_samples": STRIDE_GRID_SAMPLES,
    "normalization": "whole-clip sample std (Bessel correction) + 1e-3",
    "bottleneck_attention": "causal mask in the official forward",
    "waveform_convolutions": "strided encoder/transposed decoder, not phase-aligned",
    "streaming_contract": "none; only a whole-utterance offline path is published",
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
    "real_cleanunet_runtime": False,
    "weights_accessed": False,
    "checkpoint_deserialized": False,
    "asset_downloaded": False,
    "asset_bytes_read": False,
    "real_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "offline_latency_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "quality_claim": False,
    "release_claim": False,
    "streaming_behavior_claimed": False,
}

EXACT_BLOCKERS: Tuple[str, ...] = (
    "The candidate checkpoint is pinned but absent. The Git LFS object "
    "exp/DNS-large-high/checkpoint/pretrained.pkl at immutable commit "
    "2f930ce6660e76b6265c07da4027b414adb24ab1 has oid sha256:"
    "513d9e4f69483bf2bcc3059dd6b3644140763bf3f22df41d7ee366cc2cbd1829 and size "
    "184,336,765 bytes, but the staged copy data/models/cleanunet/dns-large-high/"
    "pretrained.pkl is not present in this workspace and no bytes were downloaded or read.",
    "The PyTorch CPU runtime is absent and unpinned. The pinned evaluation records CPython "
    "3.11.5 with PyTorch 2.14.1 and torchaudio 2.11.0 in data/envs/clearvoice, but that "
    "environment is gone, no PyTorch is installed for the available interpreters, and no "
    "wheel, hash lock or distribution digest is pinned in this package. The official "
    "denoise.py hard-codes .cuda(); CPU placement is an adapter-local change, not upstream.",
    "Artifact rights are not cleared. MIT covers the repository source, but the LFS checkpoint "
    "has no separate written artifact terms in the pinned files, DNS2020 training-data "
    "provenance is not stated for redistribution or product use, legal review is absent, and "
    "loading a 177 MB external pickle with torch.load requires a trusted-origin decision; no "
    "weight, source or runtime may be vendored, packaged, downloaded or redistributed here.",
    "No qualification evidence exists for this task: there is no rights-cleared paired real "
    "cohort, independent clean-reference scorer, permitted listening result, target "
    "pacing/deadline measurement or approved exact whole-clip reference output vector for "
    "these frozen inputs; all eight release gates remain blocked.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen asset identity only when caller-held bytes at "
    "data/models/cleanunet/dns-large-high/pretrained.pkl match 184,336,765 bytes and SHA-256 "
    "513d9e4f69483bf2bcc3059dd6b3644140763bf3f22df41d7ee366cc2cbd1829 and are tied to the "
    "immutable LFS oid at commit 2f930ce6660e76b6265c07da4027b414adb24ab1 in a retrieval record.",
    "Reopen runtime admission only when a pinned CPython/PyTorch CPU runtime with a recorded "
    "wheel or environment digest installs in the intended environment, the CPU placement and "
    "weights_only load path are documented, and distribution/product-use terms are recorded.",
    "Reopen rights only after written checkpoint-specific and runtime terms plus DNS2020 "
    "training-data provenance are recorded and a legal/redistribution decision exists; MIT "
    "source metadata alone is not artifact clearance.",
    "Reopen exact reference parity only with approved whole-clip outputs for these frozen inputs "
    "under the pinned checkpoint, configuration and runtime.",
    "Reopen the cohort gate only with a rights-cleared paired real speech cohort that includes "
    "clean references and a declared DNS2020 training/test overlap statement.",
    "Reopen scoring/listening only with an independent intrusive scorer and permitted listening "
    "under a recorded protocol.",
    "Reopen timing only with target-runtime end-to-end availability, whole-clip latency, memory, "
    "pacing and deadline measurements.",
    "Reopen provider/default only after the prior gates clear and an opt-in provider intake with "
    "OFF default, descriptor/catalog review and explicit owner default decision is approved.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "caller-held pretrained.pkl bytes matching the pinned LFS oid, byte count and SHA-256",
    "pinned CPython/PyTorch CPU runtime artifact and installation evidence",
    "written checkpoint/runtime/training-data rights clearance and pickle-trust decision",
    "approved exact whole-clip reference output vectors for the frozen synthetic inputs",
    "rights-cleared paired real speech cohort with clean references",
    "independent STOI/SI-SDR/intrusive scorer and permitted listening",
    "target-runtime whole-clip latency, memory, pacing and deadline evidence",
    "opt-in provider intake with OFF default and an explicit default-selection decision",
)

GATES: Tuple[Dict[str, str], ...] = (
    {
        "name": "exact_asset_identity",
        "status": "blocked",
        "evidence": (
            "LFS oid, byte count and commit are pinned, but the checkpoint bytes are absent "
            "from the workspace and were not admitted or read."
        ),
        "reopen": REOPEN_CONDITIONS[0],
    },
    {
        "name": "runtime_admission",
        "status": "blocked",
        "evidence": "No PyTorch CPU runtime is installed or pinned by digest in this worktree.",
        "reopen": REOPEN_CONDITIONS[1],
    },
    {
        "name": "artifact_rights",
        "status": "blocked",
        "evidence": "MIT covers source metadata; checkpoint-specific terms and legal review are absent.",
        "reopen": REOPEN_CONDITIONS[2],
    },
    {
        "name": "exact_reference_parity",
        "status": "blocked",
        "evidence": "No approved whole-clip reference output vector exists for these frozen inputs.",
        "reopen": REOPEN_CONDITIONS[3],
    },
    {
        "name": "rights_cleared_paired_cohort",
        "status": "blocked",
        "evidence": "No paired real cohort with clean references is available to this task.",
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
        "evidence": "No device clock, whole-clip latency, memory, pacing or deadline measurement was made.",
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
        "Pinned research provenance only; not reproduced here, not pooled with the synthetic "
        "fixture and not used as a threshold."
    ),
    "candidate_csv_row": (
        "Denoising,CleanUNet DNS-large-high,evaluated,30 DNS2020 pairs plus 30 clean "
        "diagnostics; dSNR +9.095 dB, dSI-SDR +9.195 dB, dSTOI +0.04436, CPU RTF .03976, "
        "peak RSS 1.02 GB; DNS2020 test-family overlap caveat."
    ),
    "census_row": (
        "Official MIT PyTorch repo provides DNS pretrained checkpoints (pretrained.pkl, "
        "~177 MB) requiring Git LFS; causal waveform encoder/decoder with self-attention."
    ),
    "realtime_component_row": (
        "DNS pilot mean dSI-SDR +9.20 dB, dSTOI +0.0444, batch RTF 0.0398, peak RSS about "
        "1.02 GB. Whole-utterance local path; DNS test-family overlap caveat."
    ),
    "eval_n": 30,
    "eval_total_seconds": 300,
    "eval_mean_delta_snr_db": 9.094705436675605,
    "eval_delta_snr_ci95_db": [7.7225440278312565, 10.583080513514544],
    "eval_mean_delta_si_sdr_db": 9.195098831986822,
    "eval_delta_si_sdr_ci95_db": [7.7723752774070665, 10.657225390910716],
    "eval_mean_delta_stoi": 0.04435978610474085,
    "eval_delta_stoi_ci95": [0.03436403849440236, 0.05520581915558431],
    "eval_stoi_wins_ties_losses": [30, 0, 0],
    "eval_mean_rtf": 0.03976213804329746,
    "eval_median_rtf": 0.039554452052107086,
    "eval_mean_inference_seconds": 0.39762138043297457,
    "eval_noisy_peak_child_rss_bytes": 1_021_964_288,
    "clean_mean_stoi": 0.9995826273917989,
    "clean_mean_delta_stoi": -0.00041737260820123113,
    "clean_delta_stoi_ci95": [-0.0007176044370118931, -0.00019379589422251426],
    "clean_stoi_wins_ties_losses": [0, 0, 30],
    "clean_mean_si_sdr_db": 37.3125478373573,
    "clean_mean_snr_db": 33.3629204289335,
    "clean_mean_rtf": 0.0396650865371339,
    "smoke_input_seconds": 10.0,
    "smoke_inference_seconds": 0.4436887089977972,
    "smoke_rtf": 0.04436887089977972,
    "smoke_peak_child_rss_bytes": 1_014_824_960,
    "recorded_runtime": RUNTIME_RECORDED,
    "recorded_runtime_lock_digest": RUNTIME_LOCK_DIGEST,
    "training_data": "DNS2020 (per pinned readiness/evaluation notes)",
    "overlap_caveat": (
        "The local 30-pair subset belongs to the DNS2020 no-reverb test family named upstream, "
        "so it is a reproduction/comparative screen, not independent generalization evidence."
    ),
    "streaming": (
        "The official model uses a causal attention mask at the bottleneck, but the published "
        "inference path is whole-utterance only; no streaming state, callback or delay is "
        "claimed or measured."
    ),
    "disclaimer": (
        "These values come from pinned research files at 16 kHz on 30 DNS2020 pairs and one "
        "10-second smoke clip. They are not reproduced by this package, not device timing, not "
        "this fixture's metrics, not a listening result and not a release claim."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "NVIDIA CleanUNet, pretrained.pkl, PyTorch and torchaudio are absent; nothing was downloaded, installed, deserialized, loaded or invoked.",
    "The checkpoint LFS oid, byte count, source revision and file hashes are quoted from the pinned adapter.lock.json and the pinned checkout; the LFS pointer was read from git metadata only.",
    "The evaluation metrics, clean diagnostics and recorded runtime versions are pinned research provenance only; this package computes separate synthetic-fixture metrics and measures no latency.",
    "All signals, targets and observations are generated by a stdlib LCG in reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
)

NON_CLAIMS: Tuple[str, ...] = (
    "No CleanUNet weight, pickle, PyTorch/torchaudio runtime, corpus or media was downloaded, deserialized, loaded, built, vendored or invoked.",
    "No public API/ABI, CONTRACTS.md, descriptor, registry, installed default, shared build, CI, board or handoff file was changed.",
    "No listening, MOS, STOI, SI-SDR, benchmark, device-timing, whole-clip latency or release result is claimed for the candidate.",
    "The synthetic surrogate is not CleanUNet and no missing result ever qualifies the candidate.",
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
# Pinned padding contract and the synthetic whole-clip surrogate
# ---------------------------------------------------------------------------


def official_padded_length(length: int) -> int:
    """Exact integer replica of the pinned network.py ``padding`` length.

    The source computes ``L = 1 + ceil((L - K) / S)`` for each of the eight
    encoder layers and then ``L = (L - 1) * S + K`` for each of the eight
    decoder layers.  Integer ceiling division is exact for these values.
    """
    size = int(length)
    if size < 0:
        raise ValueError("negative length")
    for _ in range(ENCODER_LAYERS):
        if size < KERNEL_SIZE:
            size = 1
        else:
            size = 1 + (size - KERNEL_SIZE + STRIDE - 1) // STRIDE
    for _ in range(ENCODER_LAYERS):
        size = (size - 1) * STRIDE + KERNEL_SIZE
    return int(size)


def _population_std(values: Sequence[float]) -> float:
    """Bessel-corrected standard deviation, matching torch.std(dim=..., correction=1)."""
    count = len(values)
    if count < 2:
        return 0.0
    mean = math.fsum(values) / count
    acc = 0.0
    for value in values:
        delta = value - mean
        acc += delta * delta
    return math.sqrt(acc / (count - 1))


def _frame_powers(samples: Sequence[float]) -> List[float]:
    powers: List[float] = []
    for start in range(0, len(samples), FRAME_SAMPLES):
        chunk = samples[start:start + FRAME_SAMPLES]
        total = 0.0
        for value in chunk:
            total += value * value
        powers.append(total / FRAME_SAMPLES)
    return powers


def _noise_reference(powers: Sequence[float]) -> float:
    ordered = sorted(powers)
    if not ordered:
        return 0.0
    index = int(NOISE_QUANTILE * (len(ordered) - 1))
    return ordered[index]


def _smoothed_gains(powers: Sequence[float]) -> List[float]:
    reference = _noise_reference(powers)
    raw: List[float] = []
    for power in powers:
        ratio = power / (power + reference + EPS)
        raw.append(min(1.0, max(GAIN_FLOOR, math.sqrt(ratio))))
    gains: List[float] = []
    for index in range(len(raw)):
        start = max(0, index - SMOOTH_RADIUS_FRAMES)
        end = min(len(raw), index + SMOOTH_RADIUS_FRAMES + 1)
        total = 0.0
        for value in raw[start:end]:
            total += value
        gains.append(total / (end - start))
    return gains


def surrogate_whole_clip(samples: Sequence[float]) -> List[float]:
    """Whole-clip synthetic surrogate; not CleanUNet.

    Mirrors the pinned forward contract: whole-clip std normalisation, pad or
    truncate to ``official_padded_length``, one whole-clip gain pass, crop to
    ``min(input, padded)`` and rescale by the original std.
    """
    values = [float(value) for value in samples]
    length = len(values)
    padded_length = official_padded_length(length)
    std = _population_std(values)
    scale = std + NORM_EPSILON
    normalized = [value / scale for value in values]
    if padded_length > length:
        normalized = normalized + [0.0] * (padded_length - length)
    else:
        normalized = normalized[:padded_length]
    gains = _smoothed_gains(_frame_powers(normalized))
    gated = [value * gains[index // FRAME_SAMPLES] for index, value in enumerate(normalized)]
    return [value * scale for value in gated[: min(length, padded_length)]]


def surrogate_frame_loop_control(samples: Sequence[float]) -> List[float]:
    """Independent frame loop over the same gain sequence; must be byte-identical."""
    values = [float(value) for value in samples]
    length = len(values)
    padded_length = official_padded_length(length)
    std = _population_std(values)
    scale = std + NORM_EPSILON
    normalized = [value / scale for value in values]
    if padded_length > length:
        normalized = normalized + [0.0] * (padded_length - length)
    else:
        normalized = normalized[:padded_length]
    gains = _smoothed_gains(_frame_powers(normalized))
    output: List[float] = []
    emitted = 0
    for start in range(0, len(normalized), FRAME_SAMPLES):
        if emitted >= min(length, padded_length):
            break
        gain = gains[start // FRAME_SAMPLES]
        for value in normalized[start:start + FRAME_SAMPLES]:
            if emitted >= min(length, padded_length):
                break
            output.append(value * gain * scale)
            emitted += 1
    return output


def surrogate_split_halves(samples: Sequence[float]) -> List[float]:
    midpoint = len(samples) // 2
    return surrogate_whole_clip(samples[:midpoint]) + surrogate_whole_clip(samples[midpoint:])


def scaled_copy(samples: Sequence[float], factor: float) -> List[float]:
    return [float(value) * factor for value in samples]


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
        if output_snr is not None and noisy_snr is not None else None,
        "noisy_si_sdr_db": r6(noisy_si_sdr),
        "surrogate_si_sdr_db": r6(output_si_sdr),
        "delta_si_sdr_db": r6(output_si_sdr - noisy_si_sdr)
        if output_si_sdr is not None and noisy_si_sdr is not None else None,
        "noise_attenuation_db": r6(_attenuation_db(observed, output)),
    }


# ---------------------------------------------------------------------------
# Caller-supplied external asset boundary and admission
# ---------------------------------------------------------------------------


def asset_ref() -> Dict[str, Any]:
    return {
        "asset_id": ASSET_ID,
        "path_relative": ASSET_PATH,
        "lfs_path": ASSET_LFS_PATH,
        "byte_count": ASSET_BYTES,
        "sha256": ASSET_SHA256,
        "storage": "external",
        "checkpoint_format": CHECKPOINT_FORMAT,
        "package": PACKAGE,
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "model_revision": SOURCE_REVISION,
        "model_download_revision": MODEL_DOWNLOAD_REVISION,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "code_license_metadata": CODE_LICENSE_METADATA,
        "runtime_recorded": RUNTIME_RECORDED,
        "runtime_lock_digest": RUNTIME_LOCK_DIGEST,
        "bytes_present_in_worktree": (SDK_ROOT / ASSET_PATH).is_file(),
        "asset_bytes_read": False,
        "runtime_available": False,
        "runtime_dependency_pinned": False,
        "rights_cleared": False,
        "download_permitted": False,
    }


ADMISSION_ORDER = [
    "asset_bytes_absent",
    "runtime_unavailable",
    "runtime_dependency_unpinned",
    "rights_not_cleared",
]


def asset_admission(ref: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ref = dict(ref or asset_ref())
    reasons: List[str] = []
    if not ref.get("bytes_present_in_worktree") or ref.get("asset_bytes_read") is False:
        reasons.append("asset_bytes_absent")
    if not ref.get("runtime_available"):
        reasons.append("runtime_unavailable")
    if not ref.get("runtime_dependency_pinned"):
        reasons.append("runtime_dependency_unpinned")
    if not ref.get("rights_cleared"):
        reasons.append("rights_not_cleared")
    reasons = [reason for reason in ADMISSION_ORDER if reason in reasons]
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
        "note": "Explicitly synthetic admission control; not CleanUNet and not eligible for any gate.",
    }


# ---------------------------------------------------------------------------
# Offline whole-clip session mechanics
# ---------------------------------------------------------------------------


def default_config() -> Dict[str, Any]:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "max_clip_samples": MAX_CLIP_SAMPLES,
        "processing_mode": "offline_whole_clip",
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
    if config["max_clip_samples"] != MAX_CLIP_SAMPLES:
        reasons.append("max_clip_samples_mismatch")
    if config["processing_mode"] != "offline_whole_clip":
        reasons.append("mode_unsupported")
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


class OfflineSession:
    """One-shot, stateless-across-clips whole-clip session (surrogate only)."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = dict(config or default_config())
        self.admission = admit_config(self.config)
        self.created = self.admission["status"].startswith("admitted")
        self.closed = False
        self.completed = False
        self.output: List[float] | None = None

    def state(self) -> Dict[str, Any]:
        return {
            "created": self.created,
            "closed": self.closed,
            "completed": self.completed,
            "admission_status": self.admission["status"],
            "asset_mode": self.config.get("asset_mode"),
            "output_sha256": output_digest(self.output) if self.output is not None else None,
        }

    def state_digest(self) -> str:
        return sha256(canonical_bytes(self.state()))

    def process_clip(self, samples: Any) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed", state_unchanged=True)
        elif not self.created:
            result = _reject("not_admitted", reason_codes=self.admission.get("reason_codes", []),
                             state_unchanged=True)
        elif isinstance(samples, str) or not isinstance(samples, (list, tuple)):
            result = _reject("clip_type_invalid", state_unchanged=True)
        elif len(samples) == 0:
            result = _reject("clip_empty", state_unchanged=True)
        elif len(samples) > self.config["max_clip_samples"]:
            result = _reject("clip_oversized", state_unchanged=True)
        elif any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in samples):
            result = _reject("sample_type_invalid", state_unchanged=True)
        elif any(not math.isfinite(float(value)) for value in samples):
            result = _reject("sample_nonfinite", state_unchanged=True)
        elif any(abs(float(value)) > MAX_ABS_INPUT for value in samples):
            result = _reject("sample_out_of_range", state_unchanged=True)
        elif self.completed:
            result = _reject("offline_clip_already_complete", state_unchanged=True)
        else:
            values = [float(value) for value in samples]
            self.output = surrogate_whole_clip(values)
            self.completed = True
            padded = official_padded_length(len(values))
            result = {
                "status": "ok_synthetic",
                "output": list(self.output),
                "input_samples": len(values),
                "output_samples": len(self.output),
                "official_padded_length": padded,
                "internal_padding_samples": padded - len(values),
                "length_preserved": len(self.output) == len(values),
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

    run("wrong_sample_rate", lambda c: c.update(sample_rate_hz=8_000))
    run("wrong_channels", lambda c: c.update(channels=2))
    run("wrong_sample_format", lambda c: c.update(sample_format="s16"))
    run("wrong_frame_samples", lambda c: c.update(frame_samples=320))
    run("wrong_max_clip_samples", lambda c: c.update(max_clip_samples=8_000))
    run("streaming_mode_unsupported", lambda c: c.update(processing_mode="streaming"))
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
        "note": "Explicitly synthetic control branch; not CleanUNet and not a qualification result.",
    }
    return cases


def clip_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, samples: Any, fresh: bool = True, after_close: bool = False) -> None:
        session = OfflineSession(synthetic_config())
        if not fresh:
            first = session.process_clip([0.01] * FRAME_SAMPLES)
            if first["status"] != "ok_synthetic":
                raise RuntimeError("control clip failed: " + first["status"])
        if after_close:
            session.close()
        before = session.state_digest()
        result = session.process_clip(samples)
        cases[name] = {
            "status": result["status"],
            "state_unchanged": session.state_digest() == before,
            "output_samples": result.get("output_samples", 0),
        }

    run("empty_clip", [])
    run("oversized_clip", [0.01] * (MAX_CLIP_SAMPLES + 1))
    run("nonfinite_sample", [0.01, float("nan")])
    run("infinite_sample", [0.01, float("inf")])
    run("string_clip", "not-a-clip")
    run("boolean_sample", [True, 0.0])
    run("out_of_range_sample", [MAX_ABS_INPUT + 0.5])
    run("second_clip", [0.01] * FRAME_SAMPLES, fresh=False)
    run("after_close", [0.01] * FRAME_SAMPLES, after_close=True)
    return cases


def padding_contract() -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for length in (160, 16_000, 31_999, 32_000, 32_001, 32_123, 160_000):
        padded = official_padded_length(length)
        rows.append(
            {
                "input_samples": length,
                "official_padded_length": padded,
                "pad_samples": padded - length,
                "padded_modulo_256": padded % STRIDE_GRID_SAMPLES,
            }
        )
    return {
        "source": "network.py:padding(x, D=8, K=4, S=2) followed by x[:, :, :L] in forward()",
        "stride_grid_samples": STRIDE_GRID_SAMPLES,
        "padded_length_formula": "256 * downsample_length + 510",
        "padded_length_residue_mod_256": 510 % STRIDE_GRID_SAMPLES,
        "rows": rows,
        "padded_always_at_least_input": all(row["pad_samples"] >= 0 for row in rows),
        "ten_second_clip_padded_to": official_padded_length(MAX_CLIP_SAMPLES),
        "ten_second_clip_padding_samples": official_padded_length(MAX_CLIP_SAMPLES) - MAX_CLIP_SAMPLES,
        "note": (
            "Each downsampling stage rounds up, so the reconstructed length is never below the "
            "input; the extra padding is discarded by the final crop and the emitted length is "
            "exactly the input length. The padded length is 254 modulo 256, not a 256 multiple. "
            "This is a source-derived length control, not a measured candidate output."
        ),
    }


def offline_semantics() -> Dict[str, Any]:
    target, observed = synth("active_speech")
    whole = surrogate_whole_clip(observed)
    frame_loop = surrogate_frame_loop_control(observed)
    split = surrogate_split_halves(observed)
    split_changed = sum(1 for left, right in zip(whole, split) if left != right)

    prefix_len = SAMPLE_RATE_HZ
    prefix = surrogate_whole_clip(observed[:prefix_len])
    extended = whole[:prefix_len]
    prefix_changed = sum(1 for left, right in zip(prefix, extended) if left != right)

    partial = observed + observed[:123]
    partial_output = surrogate_whole_clip(partial)

    doubled = surrogate_whole_clip(scaled_copy(observed, 2.0))
    expected_double = [value * 2.0 for value in whole]
    scale_exact = doubled == expected_double
    scale_max_abs_diff = max(
        (abs(left - right) for left, right in zip(doubled, expected_double)), default=0.0
    )
    peak_expected = max((abs(value) for value in expected_double), default=1.0)
    scale_rel_error = scale_max_abs_diff / peak_expected if peak_expected > 0.0 else 0.0

    silence = surrogate_whole_clip([0.0] * FRAME_SAMPLES)
    impulse = [0.0] * SAMPLES
    impulse[4_000] = 0.25
    impulse_output = surrogate_whole_clip(impulse)
    peak_index = max(range(len(impulse_output)), key=lambda index: abs(impulse_output[index]))

    session = OfflineSession(synthetic_config())
    first = session.process_clip(observed)
    second = session.process_clip(observed)
    replay = OfflineSession(synthetic_config()).process_clip(observed)
    session.close()
    close_twice = session.closed
    after_close = session.process_clip(observed)

    return {
        "one_call_only": first["status"] == "ok_synthetic" and second["status"]
        == "rejected:offline_clip_already_complete",
        "second_clip_rejected": second["status"],
        "replay_bit_identical": first["output"] == replay["output"],
        "close_idempotent": close_twice,
        "process_after_close": after_close["status"],
        "incremental_process_api_absent": True,
        "flush_api_absent": True,
        "reset_api_absent": True,
        "framewise_equals_samplewise": frame_loop == whole,
        "split_halves_differ": split_changed > 0,
        "split_halves_changed_samples": split_changed,
        "prefix_not_final_before_full_clip": prefix_changed > 0,
        "prefix_changed_samples": prefix_changed,
        "prefix_samples": prefix_len,
        "partial_tail_input_samples": len(partial),
        "partial_tail_output_samples": len(partial_output),
        "partial_tail_official_padded_length": official_padded_length(len(partial)),
        "partial_tail_padding_discarded_samples":
            official_padded_length(len(partial)) - len(partial),
        "partial_tail_digest": output_digest(partial_output),
        "scale_equivariance_factor": 2.0,
        "scale_equivariance_exact": scale_exact,
        "scale_equivariance_approx": scale_rel_error <= 1e-12,
        "scale_equivariance_max_abs_diff": scale_max_abs_diff,
        "scale_equivariance_rel_error": scale_rel_error,
        "silent_clip_peak": r6(max((abs(value) for value in silence), default=0.0)),
        "impulse_input_peak_index": 4_000,
        "impulse_output_peak_index": peak_index,
        "impulse_peak_preserved": peak_index == 4_000,
        "cross_clip_state_carried": False,
        "availability_clock": CLOCK_ID,
        "device_clock_measured": False,
    }


def synthetic_results() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    variants = {
        "identity_passthrough": lambda values: list(values),
        "noisy_control": lambda values: list(values),
        "surrogate_whole_clip": surrogate_whole_clip,
        "surrogate_frame_loop_control": surrogate_frame_loop_control,
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
        entry["frame_loop_matches_whole_clip"] = entry["surrogate_frame_loop_control"]["output_sha256"] == \
            entry["surrogate_whole_clip"]["output_sha256"]
        entry["split_halves_differs"] = entry["surrogate_split_halves"]["output_sha256"] != \
            entry["surrogate_whole_clip"]["output_sha256"]
        entry["target_all_zero"] = all(value == 0.0 for value in target)
        results[condition] = entry
    return results


def regressions(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for condition in CONDITIONS:
        whole = results[condition]["surrogate_whole_clip"]
        for metric in ("delta_snr_db", "delta_si_sdr_db"):
            value = whole[metric]
            if value is not None and value < 0.0:
                rows.append(
                    {
                        "condition": condition,
                        "metric": metric,
                        "value_db": value,
                        "interpretation": (
                            "Synthetic surrogate regression versus the noisy control; property of the "
                            "fixture, not evidence about CleanUNet and not a tuned threshold."
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
        "state_and_memory": "stateless_synthetic_only",
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


def build_report() -> Dict[str, Any]:
    results = synthetic_results()
    config_cases = config_rejection_matrix()
    clip_cases = clip_rejection_matrix()
    semantics = offline_semantics()
    admission = asset_admission()
    identity = task_identity()
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "candidate": f"NVIDIA CleanUNet DNS-large-high ({PACKAGE}, {ASSET_ID})",
        "verification_profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "missing_result_may_qualify": False,
            "reason": "The exact checkpoint bytes, pinned runtime, artifact rights and qualification evidence are absent.",
        },
        "scope": (
            "Task-local synthetic caller-supplied-asset whole-clip boundary only; the candidate "
            "was not run and no claim is made."
        ),
        "task_identity": identity,
        "format": dict(FORMAT),
        "architecture": dict(ARCHITECTURE),
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
        "padding_contract": padding_contract(),
        "synthetic_results": results,
        "regressions": regressions(results),
        "controls": {
            "identity_passthrough_exact": all(
                results[condition]["identity_exact"] for condition in CONDITIONS
            ),
            "frame_loop_matches_whole_clip": all(
                results[condition]["frame_loop_matches_whole_clip"] for condition in CONDITIONS
            ),
            "split_halves_differs": all(
                results[condition]["split_halves_differs"] for condition in CONDITIONS
            ),
            "scale_equivariance_approx": semantics["scale_equivariance_approx"],
            "variant_count": 5,
            "condition_count": len(CONDITIONS),
            "note": "Controls describe the synthetic surrogate only.",
        },
        "adverse": {
            "config_rejections": config_cases,
            "clip_cases": {"cases": clip_cases, "state_after_close_unchanged_by_rejected_call": True},
            "lifecycle": {
                "one_call_only": semantics["one_call_only"],
                "close_idempotent": semantics["close_idempotent"],
                "second_clip": semantics["second_clip_rejected"],
                "process_after_close": semantics["process_after_close"],
                "reset_api_absent": semantics["reset_api_absent"],
                "flush_api_absent": semantics["flush_api_absent"],
                "incremental_process_api_absent": semantics["incremental_process_api_absent"],
                "zero_length_clip_rejected": clip_cases["empty_clip"]["status"] == "rejected:clip_empty",
            },
            "nonfinite_and_invalid_rejected": all(
                clip_cases[name]["status"].startswith("rejected:")
                for name in ("nonfinite_sample", "infinite_sample", "string_clip",
                             "boolean_sample", "out_of_range_sample")
            ),
            "missing_asset_blocked": admission["status"] == "blocked",
            "padding_discarded_on_crop": padding_contract()["padded_always_at_least_input"],
        },
        "state": {
            "deterministic_output_digest": True,
            "deterministic_state_digest": True,
            "framewise_equals_samplewise": semantics["framewise_equals_samplewise"],
            "framewise_equals_samplewise_state": True,
            "one_call_only": semantics["one_call_only"],
            "close_idempotent": semantics["close_idempotent"],
            "process_after_close": semantics["process_after_close"],
            "partial_tail_preserved": semantics["partial_tail_output_samples"]
            == semantics["partial_tail_input_samples"],
            "impulse_peak_preserved": semantics["impulse_peak_preserved"],
            "scale_equivariance_exact": semantics["scale_equivariance_exact"],
        },
        "offline_semantics": semantics,
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
            "frames_per_condition": SAMPLES // FRAME_SAMPLES,
            "whole_clip_calls_per_condition": 5,
            "synthetic_variants": 5,
            "config_adverse_cases": len(config_cases),
            "clip_adverse_cases": len(clip_cases),
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
        "candidate": f"NVIDIA CleanUNet DNS-large-high ({PACKAGE}, {ASSET_ID})",
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
        "architecture": dict(ARCHITECTURE),
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
            "synthetic whole-clip surrogate boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied external asset contract",
        ],
        "not_allowed": [
            "downloading, reading, deserializing or bundling pretrained.pkl or PyTorch",
            "executing the CleanUNet runtime or publishing its outputs",
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
            "mutable_fields_excluded": list(STABLE_TASK_IDENTITY["mutable_fields_excluded"]),
            "stable_fields_only": True,
        },
    }
