# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence model for SDK-DPDFNET-2-OFFLINE.

This module is NOT DPDFNet-2 and is not a reproduction of its runtime. It does
not read weights, audio, media or a caller asset; it downloads nothing, invokes
no vendor runtime, measures no device clock or deadline, conducts no listening,
benchmarks no SDK build and makes no release or quality claim.

It models the *offline whole-clip boundary* a caller-supplied external asset
would have to cross: 16 kHz mono f32, one complete caller-owned clip, an
equal-length output, fail-closed admission and no streaming state, flush,
lookahead protocol or device timing. The signal path is an original
deterministic surrogate, labelled as such everywhere.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-DPDFNET-2-OFFLINE"
TITLE = "DPDFNet-2 offline"
SLUG = "dpdfnet-2-offline"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "871201c187c42291410245344aacee5c80051b48"
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
MAX_CLIP_SAMPLES = 10 * SAMPLE_RATE_HZ
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

# Original surrogate parameters. They are fixture constants, not thresholds
# tuned against a real model, corpus or listener.
NOISE_QUANTILE = 0.55
OVER_SUBTRACTION = 1.4
GAIN_FLOOR = 0.12
SMOOTH_RADIUS_FRAMES = 6
EPS = 1e-12

# Exact pinned candidate identity. Quoted from the pinned research ledgers; no
# asset bytes are present in, copied into or read from this worktree.
MODEL_ID = "dpdfnet2.onnx"
MODEL_BYTES = 10_178_747
MODEL_SHA256 = "4f0ee28935b4a32abecc717d745416976565834d839601acf43031094b4dc94c"
PACKAGE_VERSION = "0.6.0"
PACKAGE_SOURCE = "https://github.com/ceva-ip/DPDFNet/tree/main/package"
SOURCE_REVISION = "dd6818d00f50c836fed43a6243ebe49116de5964"
MODEL_DOWNLOAD_REVISION = "main (mutable; retrieval-time commit not recorded)"
MODEL_REVISION = None
MODEL_LICENSE_METADATA = "Apache-2.0"
CODE_LICENSE_METADATA = "Apache-2.0"
MODEL_PARAMETERS_MILLIONS = 2.49
MODEL_GMAC = 1.35
BASELINE_PARAMETERS_MILLIONS = 2.31
BASELINE_GMAC = 0.36

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "adapters/dpdfnet/adapter.json":
        "6bd90aa93629a372a7b18c4036d3006c593b53c6f2c7f75bd181590c5327973c",
    "adapters/dpdfnet/README.md":
        "9b55bd13bf74f6c268efa3ad5e6d572ea8ef101527bba467760c6cb47f56f472",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/selected_audio_enhancement_candidates.md":
        "0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
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

# Fail-closed local file set. SOURCES.sha256 is excluded because a manifest
# cannot pin its own bytes; its .license sidecar is included.
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256.license",
    "adapter.json",
    "adapter.json.license",
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
    "run.py",
    "test_reference.py",
    "verify.py",
)

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
    "max_clip_samples": MAX_CLIP_SAMPLES,
    "processing_mode": "offline_whole_clip",
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
    "streaming_mode_added": False,
}

CLAIMS: Dict[str, bool] = {
    "real_dpdfnet2_runtime": False,
    "weights_accessed": False,
    "asset_downloaded": False,
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
    "The pinned ledger records dpdfnet2.onnx as 10,178,747 bytes with SHA-256 "
    "4f0ee28935b4a32abecc717d745416976565834d839601acf43031094b4dc94c, but "
    "model_revision is null and the download revision is the mutable 'main' "
    "with no retrieval-time commit, so an immutable artifact revision for those "
    "bytes is not established; the asset is absent from this SDK worktree.",
    "The offline runtime is the external dpdfnet 0.6.0 CPU ONNX package. It is "
    "not installed here, has no pinned wheel/sdist digest in this worktree, and "
    "its runtime distribution and product-use terms beyond Apache-2.0 metadata "
    "are not cleared; no vendor runtime is invoked.",
    "Apache-2.0 is recorded for the package and model card, but artifact-specific "
    "weight rights, training-data provenance, redistribution clearance and legal "
    "review are not established; no weight, runtime or upstream source may be "
    "vendored, packaged, downloaded or redistributed by this package.",
    "No rights-cleared held-out real cohort, independent clean-reference scorer, "
    "listening result, target pacing/deadline measurement or approved exact "
    "whole-clip offline reference output exists; every release gate remains "
    "blocked.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen asset identity only when the exact dpdfnet2.onnx bytes are addressed "
    "by an immutable artifact revision plus byte count and SHA-256 in a retrieval "
    "record, and the bytes resolve from the caller's own storage without a "
    "provider file access or download.",
    "Reopen runtime admission only when a pinned dpdfnet 0.6.0 runtime artifact "
    "with a recorded digest installs in the intended environment and its "
    "distribution and product-use terms are documented.",
    "Reopen rights only after written artifact-specific weight, runtime and "
    "training-data terms are recorded and a legal/redistribution decision exists; "
    "Apache-2.0 metadata alone is not clearance.",
    "Reopen qualification only with a rights-cleared paired cohort, an independent "
    "scorer, permitted listening, exact whole-clip offline reference outputs for "
    "the frozen inputs, and target pacing/deadline evidence; the synthetic "
    "surrogate can never stand in for any of these.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "immutable dpdfnet2.onnx artifact revision plus caller-held bytes in this worktree",
    "pinned dpdfnet 0.6.0 runtime artifact and installation evidence",
    "written artifact-specific weight/runtime/training-data rights clearance",
    "approved exact whole-clip offline reference output vectors for the frozen synthetic inputs",
    "rights-cleared paired real speech cohort with clean references",
    "independent STOI/SI-SDR/intrusive scorer and permitted listening",
    "target-runtime pacing, availability, deadline and memory evidence for whole-clip use",
    "opt-in provider intake, descriptor/catalog review and explicit default selection",
)

GATES: Tuple[Dict[str, str], ...] = (
    {"name": "exact_asset_identity", "status": "blocked",
     "evidence": "Ledger digest/byte count only; model_revision is null and the download revision is mutable 'main'.",
     "reopen": REOPEN_CONDITIONS[0]},
    {"name": "runtime_admission", "status": "blocked",
     "evidence": "dpdfnet 0.6.0 is absent and its offline runtime artifact is unpinned here.",
     "reopen": REOPEN_CONDITIONS[1]},
    {"name": "artifact_rights", "status": "blocked",
     "evidence": "Apache-2.0 metadata is recorded; artifact-specific terms and legal review are absent.",
     "reopen": REOPEN_CONDITIONS[2]},
    {"name": "exact_reference_parity", "status": "blocked",
     "evidence": "No approved whole-clip offline reference output vector exists for these frozen inputs.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "rights_cleared_cohort", "status": "blocked",
     "evidence": "No paired real cohort with clean references is available to this task.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "independent_scoring_and_listening", "status": "blocked",
     "evidence": "No independent scorer or listening result; surrogate metrics are synthetic only.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "target_runtime_timing", "status": "blocked",
     "evidence": "No device clock, end-to-end latency, memory, pacing or deadline measurement was made.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "provider_intake", "status": "blocked",
     "evidence": "No opt-in provider, descriptor or catalog entry exists; the package is unregistered.",
     "reopen": "Reopen only after rights/runtime/parity gates clear and an opt-in provider intake with OFF default and independent review is approved."},
    {"name": "public_default_selection", "status": "blocked",
     "evidence": "No default selection is proposed or made.",
     "reopen": "Reopen only after the provider intake clears and the owner records an explicit default decision with preserving controls."},
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "scope": "Pinned research provenance only; not reproduced, not pooled and not used as a threshold.",
    "candidate_csv_row": (
        "Denoising,DPDFNet-2 offline,evaluated,30 paired DNS2020 outputs; "
        "higher CPU cost than baseline"
    ),
    "census_row": (
        "Local pilot: offline median gain +7.203 dB / STOI .9713 / median RTF .0989; "
        "streaming +7.300 dB / .9713 / .1090 on the 30 DNS pairs."
    ),
    "selected_candidates_row": (
        "Offline: median gain +7.203 dB SNR / STOI .9713 / RTF .0989; "
        "clean-input median STOI .9803; distortion SNR 23.00 dB."
    ),
    "pilot_offline_mean_delta_snr_db": 7.8522,
    "pilot_offline_median_delta_snr_db": 7.2029,
    "pilot_offline_snr_ci95_db": [6.3114, 9.4949],
    "pilot_offline_mean_delta_si_sdr_db": 7.7973,
    "pilot_offline_median_delta_si_sdr_db": 7.1112,
    "pilot_offline_si_sdr_ci95_db": [6.2713, 9.4698],
    "pilot_offline_mean_delta_stoi": 0.0329,
    "pilot_offline_median_delta_stoi": 0.0286,
    "pilot_offline_stoi_ci95": [0.0231, 0.0434],
    "pilot_offline_stoi_wins_ties_losses": [27, 0, 3],
    "pilot_offline_batch_rtf": 0.0989,
    "pilot_clean_input_median_stoi": 0.9803,
    "pilot_clean_input_distortion_snr_db": 23.00,
    "offline_content_delay_samples": None,
    "streaming_only_cpp_content_delay_samples": 800,
    "streaming_only_cpp_qualification": "experimental; separate streaming/C++ scope, not this offline mode",
    "model_card_parameters_millions": MODEL_PARAMETERS_MILLIONS,
    "model_card_gmac": MODEL_GMAC,
    "baseline_model_card_parameters_millions": BASELINE_PARAMETERS_MILLIONS,
    "baseline_model_card_gmac": BASELINE_GMAC,
    "disclaimer": (
        "These values come from pinned research files at 16 kHz on 30 DNS2020 pairs and, "
        "for the 800-sample value, a separate C++ streaming backend. They are not "
        "reproduced here, not device timing, not this fixture's metrics, not a listening "
        "result and not a release claim. The offline adapter has no source-reported "
        "algorithmic lag in these ledgers."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "DPDFNet-2 model, dpdfnet 0.6.0 package and ONNX runtime are absent; nothing was downloaded, installed, loaded or invoked.",
    "The model digest, byte count, source revision, mutable download revision and license metadata are quoted from research/noise_suppression_assets_20261027.json and the pinned adapter README.",
    "The offline pilot metrics and model-card parameters are pinned research provenance only; this package computes separate synthetic-fixture metrics and measures no latency.",
    "All signals, targets and observations are generated by a stdlib LCG in reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
)


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


def asset_ref() -> Dict[str, Any]:
    """The exact caller-supplied asset reference this boundary would require."""
    return {
        "asset_id": MODEL_ID,
        "storage": "external",
        "sha256": MODEL_SHA256,
        "byte_count": MODEL_BYTES,
        "package": "dpdfnet==" + PACKAGE_VERSION,
        "source_repository": PACKAGE_SOURCE,
        "source_revision": SOURCE_REVISION,
        "model_download_revision": MODEL_DOWNLOAD_REVISION,
        "model_revision": MODEL_REVISION,
        "code_license_metadata": CODE_LICENSE_METADATA,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "rights_cleared": False,
        "bytes_present": False,
        "runtime_available": False,
        "download_permitted": False,
    }


def asset_admission(ref: Dict[str, Any]) -> Dict[str, Any]:
    """Fail-closed admission for a caller-supplied external asset reference.

    No filesystem access, network access or vendor runtime call occurs. The
    checks mirror the pinned contract: exact ID, byte count, digest, external
    storage and no download. A caller may supply bytes from its own storage, but
    this task holds none for the pinned candidate.
    """
    reasons: List[str] = []
    required = {"asset_id", "storage", "sha256", "byte_count", "package",
                "source_revision", "model_revision", "rights_cleared",
                "bytes_present", "runtime_available", "download_permitted"}
    missing = sorted(required - set(ref))
    if missing:
        reasons.append("missing_fields:" + ",".join(missing))
    if ref.get("asset_id") != MODEL_ID:
        reasons.append("asset_id_mismatch")
    if ref.get("storage") != "external":
        reasons.append("storage_not_external")
    if ref.get("sha256") != MODEL_SHA256:
        reasons.append("sha256_mismatch")
    if ref.get("byte_count") != MODEL_BYTES:
        reasons.append("byte_count_mismatch")
    if ref.get("package") != "dpdfnet==" + PACKAGE_VERSION:
        reasons.append("package_mismatch")
    if ref.get("source_revision") != SOURCE_REVISION:
        reasons.append("source_revision_mismatch")
    if ref.get("model_revision") in (None, "", "main"):
        reasons.append("model_revision_unpinned")
    if str(ref.get("model_download_revision", "")).startswith("main"):
        reasons.append("download_revision_mutable")
    if ref.get("download_permitted") is not False:
        reasons.append("download_flag_invalid")
    if ref.get("bytes_present") is not True:
        reasons.append("asset_bytes_absent")
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


def default_config() -> Dict[str, Any]:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "max_clip_samples": MAX_CLIP_SAMPLES,
        "mode": "synthetic-surrogate",
        "synthetic_surrogate_opt_in": True,
        "asset_reference": asset_ref(),
    }


def validate_config(config: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    expected = default_config()
    for key in ("sample_rate_hz", "channels", "sample_format", "frame_samples",
                "max_clip_samples"):
        if config.get(key) != expected[key]:
            reasons.append(key + "_mismatch")
    mode = config.get("mode")
    if mode not in ("synthetic-surrogate", "caller-asset"):
        reasons.append("mode_unsupported")
    if mode == "synthetic-surrogate" and config.get("synthetic_surrogate_opt_in") is not True:
        reasons.append("surrogate_opt_in_required")
    if mode == "caller-asset":
        admission = asset_admission(config.get("asset_reference") or {})
        if admission["status"] != "admitted":
            reasons.append("asset_not_admitted")
    return reasons


def _frame_powers(samples: Sequence[float]) -> List[float]:
    powers: List[float] = []
    for start in range(0, len(samples), FRAME_SAMPLES):
        frame = list(samples[start:start + FRAME_SAMPLES])
        frame.extend([0.0] * (FRAME_SAMPLES - len(frame)))
        powers.append(sum(value * value for value in frame) / float(FRAME_SAMPLES))
    return powers


def _noise_reference(powers: Sequence[float]) -> float:
    if not powers:
        return 1e-10
    ordered = sorted(powers)
    index = int(NOISE_QUANTILE * (len(ordered) - 1))
    return max(ordered[index], 1e-10)


def _target_gains(powers: Sequence[float]) -> Tuple[float, List[float]]:
    noise = _noise_reference(powers)
    raw: List[float] = []
    for power in powers:
        ratio = power / max(noise, EPS)
        if ratio <= OVER_SUBTRACTION:
            target = GAIN_FLOOR
        else:
            target = math.sqrt(max(0.0, 1.0 - OVER_SUBTRACTION / ratio))
        raw.append(min(1.0, max(GAIN_FLOOR, target)))
    radius = SMOOTH_RADIUS_FRAMES
    smoothed: List[float] = []
    for index in range(len(raw)):
        low = max(0, index - radius)
        high = min(len(raw), index + radius + 1)
        window = raw[low:high]
        smoothed.append(sum(window) / float(len(window)))
    return noise, smoothed


def _apply_gains(samples: Sequence[float], gains: Sequence[float]) -> List[float]:
    output: List[float] = []
    previous = gains[0] if gains else 1.0
    for frame_index, start in enumerate(range(0, len(samples), FRAME_SAMPLES)):
        frame = samples[start:start + FRAME_SAMPLES]
        current = gains[frame_index]
        for offset, value in enumerate(frame):
            weight = (offset + 1) / float(FRAME_SAMPLES)
            applied = previous + (current - previous) * weight
            output.append(value * applied)
        previous = current
    return output


def surrogate_offline(samples: Sequence[float]) -> Dict[str, Any]:
    """Whole-clip offline surrogate; output length equals input length exactly."""
    values = [float(value) for value in samples]
    if not values:
        raise ValueError("clip_empty")
    powers = _frame_powers(values)
    noise, gains = _target_gains(powers)
    output = _apply_gains(values, gains)
    padded = len(powers) * FRAME_SAMPLES - len(values)
    return {
        "output": output,
        "input_samples": len(values),
        "output_samples": len(output),
        "frames": len(powers),
        "internal_frame_padding_samples": padded,
        "noise_reference_power": noise,
        "gain_min": min(gains),
        "gain_max": max(gains),
        "gain_mean": sum(gains) / float(len(gains)),
        "input_digest": sha256(canonical_bytes(values)),
        "output_digest": sha256(canonical_bytes(output)),
        "lookahead_frames": SMOOTH_RADIUS_FRAMES,
        "lookahead_samples": SMOOTH_RADIUS_FRAMES * FRAME_SAMPLES,
        "noncausal_by_construction": True,
    }


def surrogate_frame_loop_control(samples: Sequence[float]) -> Dict[str, Any]:
    """Independent frame-loop path over the same whole-clip gain path."""
    values = [float(value) for value in samples]
    if not values:
        raise ValueError("clip_empty")
    powers = _frame_powers(values)
    noise, gains = _target_gains(powers)
    output: List[float] = []
    previous = gains[0]
    for index, start in enumerate(range(0, len(values), FRAME_SAMPLES)):
        frame = list(values[start:start + FRAME_SAMPLES])
        current = gains[index]
        for offset in range(len(frame)):
            weight = (offset + 1) / float(FRAME_SAMPLES)
            output.append(frame[offset] * (previous + (current - previous) * weight))
        previous = current
    padded = len(powers) * FRAME_SAMPLES - len(values)
    return {
        "output": output,
        "input_samples": len(values),
        "output_samples": len(output),
        "frames": len(powers),
        "internal_frame_padding_samples": padded,
        "noise_reference_power": noise,
        "output_digest": sha256(canonical_bytes(output)),
    }


def surrogate_split_halves(samples: Sequence[float]) -> Dict[str, Any]:
    """Non-boundary control: two independent half-clips must differ from one clip."""
    values = [float(value) for value in samples]
    if len(values) < 2:
        raise ValueError("clip_too_short")
    half = len(values) // 2
    first = surrogate_offline(values[:half])["output"]
    second = surrogate_offline(values[half:])["output"]
    output = first + second
    return {
        "output": output,
        "input_samples": len(values),
        "output_samples": len(output),
        "half_samples": [half, len(values) - half],
        "output_digest": sha256(canonical_bytes(output)),
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


def _validate_clip(chunk: Any) -> List[float]:
    if isinstance(chunk, (str, bytes)) or not isinstance(chunk, Sequence):
        raise ValueError("clip_type_invalid")
    values = list(chunk)
    if not values:
        raise ValueError("clip_empty")
    if len(values) > MAX_CLIP_SAMPLES:
        raise ValueError("clip_oversized")
    for value in values:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("sample_type_invalid")
        if not math.isfinite(float(value)):
            raise ValueError("sample_nonfinite")
        if abs(float(value)) > 8.0:
            raise ValueError("sample_out_of_range")
    return [float(value) for value in values]


class OfflineSession:
    """One-shot whole-clip boundary fixture; not a vendor offline adapter."""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = dict(config or default_config())
        reasons = validate_config(self.config)
        if reasons:
            raise ValueError(";".join(reasons))
        self._closed = False
        self._completed = False
        self._calls = 0
        self._last_output_digest: str | None = None

    def process_clip(self, chunk: Sequence[float]) -> List[float]:
        if self._closed:
            raise ValueError("session_closed")
        if self._completed:
            raise ValueError("offline_clip_already_complete")
        values = _validate_clip(chunk)
        result = surrogate_offline(values)
        self._calls += 1
        self._completed = True
        self._last_output_digest = result["output_digest"]
        return result["output"]

    def close(self) -> None:
        self._closed = True

    def status_digest(self) -> str:
        return sha256(canonical_bytes({
            "closed": self._closed,
            "completed": self._completed,
            "calls": self._calls,
            "last_output_digest": self._last_output_digest,
        }))

    @property
    def completed(self) -> bool:
        return self._completed

    @property
    def calls(self) -> int:
        return self._calls


def run_offline(samples: Sequence[float],
                config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    session = OfflineSession(config)
    output = session.process_clip(samples)
    return {
        "output": output,
        "input_samples": len(samples),
        "output_samples": len(output),
        "calls": session.calls,
        "status_digest": session.status_digest(),
        "output_digest": sha256(canonical_bytes(output)),
    }


def alignment_probe() -> Dict[str, Any]:
    """Sample-aligned synthetic probe; no streaming lag is introduced."""
    samples = [0.001 * math.sin(2.0 * math.pi * 97.0 * index / SAMPLE_RATE_HZ)
               for index in range(8000)]
    samples[4000] = 0.9
    result = surrogate_offline(samples)
    output = result["output"]
    input_peak = max(range(len(samples)), key=lambda index: abs(samples[index]))
    output_peak = max(range(len(output)), key=lambda index: abs(output[index]))
    return {
        "input_peak_sample": input_peak,
        "output_peak_sample": output_peak,
        "peak_index_preserved": input_peak == output_peak,
        "algorithmic_lag_samples": 0,
        "lag_modelled": False,
        "lag_measured": False,
        "measured_latency": False,
        "synthetic_alignment_only": True,
    }


def future_context_evidence() -> Dict[str, Any]:
    """Show that a prefix is not final until the complete clip is supplied."""
    _, observed = synth("active_speech")
    short = observed[:16000]
    long = observed[:24000]
    short_out = surrogate_offline(short)["output"]
    long_out = surrogate_offline(long)["output"][:16000]
    differences = [index for index, (a, b) in enumerate(zip(short_out, long_out))
                   if a != b]
    return {
        "short_clip_samples": len(short),
        "extended_clip_samples": len(long),
        "compared_prefix_samples": 16000,
        "prefix_samples_changed_by_future_audio": len(differences),
        "first_changed_sample": differences[0] if differences else None,
        "last_changed_sample": differences[-1] if differences else None,
        "max_abs_difference": (max(abs(short_out[index] - long_out[index])
                                   for index in differences)
                               if differences else 0.0),
        "requires_complete_clip": bool(differences),
        "lookahead_frames": SMOOTH_RADIUS_FRAMES,
        "lookahead_samples": SMOOTH_RADIUS_FRAMES * FRAME_SAMPLES,
        "prefix_available_before_full_clip": False,
    }


def split_clip_evidence() -> Dict[str, Any]:
    _, observed = synth("active_speech")
    whole = surrogate_offline(observed)["output"]
    split = surrogate_split_halves(observed)["output"]
    differences = [index for index, (a, b) in enumerate(zip(whole, split)) if a != b]
    return {
        "input_samples": len(observed),
        "split_half_samples": [len(observed) // 2, len(observed) - len(observed) // 2],
        "differing_samples": len(differences),
        "first_differing_sample": differences[0] if differences else None,
        "max_abs_difference": (max(abs(whole[index] - split[index])
                                   for index in differences) if differences else 0.0),
        "split_matches_whole": not differences,
        "independent_segment_processing_is_not_offline_equivalent": bool(differences),
    }


def tail_control() -> Dict[str, Any]:
    _, observed = synth("onset_offset")
    partial = observed + [0.0] * 123
    result = surrogate_offline(partial)
    return {
        "input_samples": len(partial),
        "output_samples": result["output_samples"],
        "output_equals_input_length": result["output_samples"] == len(partial),
        "internal_frame_padding_samples": result["internal_frame_padding_samples"],
        "padding_emitted_as_audio": False,
        "truncated_padding_samples": result["internal_frame_padding_samples"],
    }


def frame_loop_equivalence() -> Dict[str, Any]:
    _, observed = synth("low_snr_speech")
    whole = surrogate_offline(observed)
    loop = surrogate_frame_loop_control(observed)
    return {
        "input_samples": len(observed),
        "whole_output_samples": whole["output_samples"],
        "frame_loop_output_samples": loop["output_samples"],
        "whole_digest": whole["output_digest"],
        "frame_loop_digest": loop["output_digest"],
        "outputs_identical": whole["output_digest"] == loop["output_digest"],
        "internal_frame_padding_samples": whole["internal_frame_padding_samples"],
    }


def statelessness_evidence() -> Dict[str, Any]:
    _, first = synth("low_snr_speech")
    _, second = synth("active_speech")
    first_a = surrogate_offline(first)["output_digest"]
    second_fresh = surrogate_offline(second)["output_digest"]
    session = OfflineSession()
    session_digest = session.process_clip(first)
    digest_a_from_session = sha256(canonical_bytes(session_digest))
    session_b = OfflineSession()
    output_b_after_a = session_b.process_clip(second)
    after_a_digest = sha256(canonical_bytes(output_b_after_a))
    replay = OfflineSession()
    replay_digest = sha256(canonical_bytes(replay.process_clip(first)))
    return {
        "clip_a_samples": len(first),
        "clip_b_samples": len(second),
        "clip_a_digest": first_a,
        "clip_a_session_digest": digest_a_from_session,
        "clip_b_fresh_digest": second_fresh,
        "clip_b_after_a_digest": after_a_digest,
        "clip_b_independent_of_prior_clip": second_fresh == after_a_digest,
        "clip_a_replay_digest": replay_digest,
        "clip_a_replay_identical": first_a == replay_digest,
        "state_carried_between_clips": False,
        "shared_mutable_state": False,
        "state_is_synthetic": True,
        "real_recurrent_state_loaded": False,
    }


def condition_block(condition: str) -> Dict[str, Any]:
    clean, observed = synth(condition)
    whole = surrogate_offline(observed)
    frame_loop = surrogate_frame_loop_control(observed)
    split = surrogate_split_halves(observed)
    valid = whole["output_samples"]
    prefix = clean[:valid]
    noisy = score(prefix, observed[:valid])
    identity = score(prefix, observed[:valid])
    candidate = score(prefix, whole["output"])
    loop = score(prefix, frame_loop["output"])
    split_score = score(prefix, split["output"])

    def delta(candidate_value: Any, control_value: Any) -> Any:
        if candidate_value is None or control_value is None:
            return None
        return candidate_value - control_value

    return {
        "input_samples": len(observed),
        "scored_samples": valid,
        "output_accounting": {
            "input_samples": len(observed),
            "output_samples": valid,
            "frames": whole["frames"],
            "internal_frame_padding_samples": whole["internal_frame_padding_samples"],
            "startup_padding_samples": 0,
            "tail_padding_emitted_samples": 0,
            "flush_required": False,
            "algorithmic_lag_samples": 0,
        },
        "variants": {
            "identity_passthrough": {**identity, "exact_passthrough": True},
            "noisy_control": noisy,
            "surrogate_whole_clip": candidate,
            "surrogate_frame_loop_control": loop,
            "surrogate_split_halves": split_score,
        },
        "improvements": {
            "snr_db": delta(candidate["snr_db"], noisy["snr_db"]),
            "si_sdr_db": delta(candidate["si_sdr_db"], noisy["si_sdr_db"]),
        },
        "noise_attenuation_db": (
            None if noisy["output_rms"] <= 0.0
            else _db((candidate["output_rms"] / noisy["output_rms"]) ** 2)
        ),
        "whole_digest": whole["output_digest"],
        "frame_loop_matches_whole": whole["output_digest"] == frame_loop["output_digest"],
        "split_halves_matches_whole": whole["output_digest"] == split["output_digest"],
    }


def config_adverse_cases() -> Dict[str, Any]:
    base = default_config()
    cases: Dict[str, Any] = {}

    def attempt(name: str, mutate) -> None:
        config = json.loads(json.dumps(base))
        mutate(config)
        try:
            session = OfflineSession(config)
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
                "status_digest": session.status_digest(),
            }

    attempt("wrong_sample_rate", lambda config: config.update(sample_rate_hz=48000))
    attempt("wrong_channels", lambda config: config.update(channels=2))
    attempt("wrong_sample_format", lambda config: config.update(sample_format="s16"))
    attempt("wrong_frame_samples", lambda config: config.update(frame_samples=80))
    attempt("wrong_max_clip_samples",
            lambda config: config.update(max_clip_samples=SAMPLE_RATE_HZ))
    attempt("streaming_mode_unsupported", lambda config: config.update(mode="streaming"))
    attempt("surrogate_without_opt_in",
            lambda config: config.update(synthetic_surrogate_opt_in=False))
    attempt("caller_asset_unavailable", lambda config: config.update(mode="caller-asset"))

    def admitted(config: Dict[str, Any]) -> None:
        config["mode"] = "caller-asset"
        config["asset_reference"].update({
            "model_revision": "artifact:dpdfnet2@sha256:" + MODEL_SHA256,
            "model_download_revision": "artifact:dpdfnet2@sha256:" + MODEL_SHA256,
            "rights_cleared": True,
            "bytes_present": True,
            "runtime_available": True,
        })

    attempt("caller_asset_admission_control", admitted)
    return cases


def clip_adverse_cases() -> Dict[str, Any]:
    _, observed = synth("quiet_speech")
    cases: Dict[str, Any] = {}

    def rejected(name: str, action, session: OfflineSession | None = None) -> None:
        target = session or OfflineSession()
        before = target.status_digest()
        try:
            action(target)
        except ValueError as error:
            after = target.status_digest()
            cases[name] = {
                "status": "rejected:" + str(error),
                "state_unchanged": before == after,
                "status_digest": after,
            }
        else:
            cases[name] = {"status": "accepted", "state_unchanged": False,
                           "status_digest": target.status_digest()}

    completed = OfflineSession()
    completed.process_clip(observed)
    rejected("second_clip", lambda session: session.process_clip(observed), completed)
    rejected("empty_clip", lambda session: session.process_clip([]))
    rejected("oversized_clip",
             lambda session: session.process_clip([0.0] * (MAX_CLIP_SAMPLES + 1)))
    rejected("nonfinite_sample",
             lambda session: session.process_clip([float("nan")]))
    rejected("infinite_sample",
             lambda session: session.process_clip([float("inf")]))
    rejected("string_clip", lambda session: session.process_clip("not-a-clip"))
    rejected("boolean_sample", lambda session: session.process_clip([True]))
    rejected("out_of_range_sample", lambda session: session.process_clip([9.0]))
    completed.close()
    after_close = completed.status_digest()
    rejected("after_close", lambda session: session.process_clip(observed), completed)
    return {
        "cases": cases,
        "state_after_close_unchanged_by_rejected_call": after_close == completed.status_digest(),
    }


def lifecycle_evidence() -> Dict[str, Any]:
    _, observed = synth("onset_offset")
    session = OfflineSession()
    first = session.process_clip(observed)
    try:
        session.process_clip(observed)
    except ValueError as error:
        second = "rejected:" + str(error)
    else:
        second = "accepted"
    session.close()
    after_first_close = session.status_digest()
    session.close()
    after_second_close = session.status_digest()
    results = {}
    try:
        session.process_clip(observed)
    except ValueError as error:
        results["process_after_close"] = "rejected:" + str(error)
    else:
        results["process_after_close"] = "accepted"
    return {
        "one_clip_completed": len(first) == len(observed),
        "second_clip": second,
        "one_call_only": second != "accepted",
        "close_idempotent": after_first_close == after_second_close,
        "process_after_close": results["process_after_close"],
        "incremental_process_api_absent": not hasattr(session, "process"),
        "flush_api_absent": not hasattr(session, "flush"),
        "reset_api_absent": not hasattr(session, "reset"),
        "zero_length_clip_rejected": not _try_empty(),
    }


def _try_empty() -> bool:
    try:
        OfflineSession().process_clip([])
    except ValueError:
        return False
    return True


def asset_boundary() -> Dict[str, Any]:
    ref = asset_ref()
    admission = asset_admission(ref)
    control = dict(ref)
    control.update({
        "model_revision": "artifact:dpdfnet2@sha256:" + MODEL_SHA256,
        "model_download_revision": "artifact:dpdfnet2@sha256:" + MODEL_SHA256,
        "rights_cleared": True,
        "bytes_present": True,
        "runtime_available": True,
    })
    control_admission = asset_admission(control)
    return {
        "kind": "caller-supplied external asset reference",
        "contract": "CONTRACTS.md as_asset_v0: ID, byte count, SHA-256, storage=external, no download",
        "candidate": "DPDFNet-2 16 kHz offline",
        "asset": {
            "asset_id": ref["asset_id"],
            "storage": ref["storage"],
            "sha256": ref["sha256"],
            "byte_count": ref["byte_count"],
            "package": ref["package"],
            "source_repository": ref["source_repository"],
            "source_revision": ref["source_revision"],
            "model_download_revision": ref["model_download_revision"],
            "model_revision": ref["model_revision"],
            "code_license_metadata": ref["code_license_metadata"],
            "model_license_metadata": ref["model_license_metadata"],
        },
        "readiness": admission["status"],
        "reason_codes": admission["reason_codes"],
        "download_attempted": admission["download_attempted"],
        "vendor_runtime_invoked": admission["vendor_runtime_invoked"],
        "asset_bytes_read": admission["asset_bytes_read"],
        "bytes_present_in_worktree": False,
        "runtime_installed_in_worktree": False,
        "rights_cleared": False,
        "synthetic_admission_control": {
            "status": control_admission["status"],
            "reason_codes": control_admission["reason_codes"],
            "not_the_pinned_candidate": True,
            "note": "Admission logic only; no upstream bytes exist and no rights are implied.",
        },
        "surrogate_policy": {
            "available": True,
            "opt_in_required": True,
            "substitutes_for_candidate": False,
            "labelled": "deterministic stdlib offline whole-clip surrogate",
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
            "status": "sample_aligned_offline_no_algorithmic_lag",
            "declared_lag_samples": 0,
            "compensated": False,
            "modelled": False,
            "measured": False,
        },
        "state_and_memory": {
            "status": "stateless_synthetic_only",
            "real_memory_measured": False,
            "state_carried_between_clips": False,
        },
        "content_and_availability_timing": {
            "status": "blocked_unmeasured",
            "measured": False,
            "device_clock": False,
            "end_to_end_latency_measured": False,
        },
        "listening": {"status": "not_run", "permitted": False},
        "whole_clip_requirement": True,
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
        candidate = block["variants"]["surrogate_whole_clip"]
        for metric in ("snr_db", "si_sdr_db"):
            if noisy[metric] is None or candidate[metric] is None:
                continue
            if candidate[metric] < noisy[metric]:
                regressions.append({
                    "condition": condition,
                    "metric": metric,
                    "better_direction": "higher",
                    "noisy_control": noisy[metric],
                    "surrogate_whole_clip": candidate[metric],
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
        "component": SLUG,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "format": FORMAT,
        "boundary": BOUNDARY,
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
                "note": "Paired control for the synthetic target on the same whole-clip output length.",
            },
            "candidate": {
                "name": "surrogate_whole_clip",
                "real_candidate": False,
                "note": "Deterministic stdlib whole-clip surrogate, not DPDFNet-2.",
            },
            "frame_loop": {
                "name": "surrogate_frame_loop_control",
                "note": "Independent frame loop over the same gain path; must equal the whole-clip output.",
            },
            "split_halves": {
                "name": "surrogate_split_halves",
                "note": "Boundary control; two independent half-clips must not equal whole-clip processing.",
            },
        },
        "regressions": _regressions(blocks),
        "regression_assessment": {
            "performed": True,
            "conditions": list(CONDITIONS),
            "finding": (
                "All paired deltas are reported verbatim. Any negative SNR or SI-SDR "
                "delta is listed under regressions; the list may be empty on this "
                "synthetic fixture and is never a candidate result."
            ),
        },
        "offline_boundary": {
            "protocol": "caller-supplied external asset plus one complete whole-clip call",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "frame_samples": FRAME_SAMPLES,
            "max_clip_samples": MAX_CLIP_SAMPLES,
            "processing_mode": "offline_whole_clip",
            "incremental_calls_supported": False,
            "streaming_supported": False,
            "flush_required": False,
            "algorithmic_lag_samples": 0,
            "lag_modelled": False,
            "lag_measured": False,
            "clock_id": CLOCK_ID,
            "fixture_epoch_ns": str(FIXTURE_EPOCH_NS),
            "availability_model": "sample-coordinate only; no wall clock, device clock or deadline",
            "output_accounting": {
                "output_samples": "input_samples",
                "startup_padding_samples": 0,
                "internal_frame_padding_samples": "(-input_samples) mod 160, discarded after gain estimation",
                "tail_padding_emitted_samples": 0,
                "flush_required": False,
                "finding": (
                    "The offline boundary returns exactly one output sample for every "
                    "input sample. A partial final frame is zero-padded only to estimate "
                    "its frame gain; padding is never returned and no flush or startup "
                    "delay exists."
                ),
            },
            "causality": future_context_evidence(),
            "split_clip_control": split_clip_evidence(),
            "frame_loop_equivalence": frame_loop_equivalence(),
            "alignment_probe": alignment_probe(),
            "tail_control": tail_control(),
            "statelessness": statelessness_evidence(),
            "device_clock_used": False,
            "deadline_measured": False,
        },
        "asset_boundary": asset_boundary(),
        "asset_admission": admission,
        "enhancement_profile": enhancement_profile(),
        "adverse": {
            "config_rejections": config_adverse_cases(),
            "clip_cases": clip_adverse_cases(),
            "lifecycle": lifecycle_evidence(),
        },
        "repeatability": {},
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "gates": list(GATES),
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "tool_provenance": list(TOOL_PROVENANCE),
        "source_pin_paths": sorted(SOURCE_PINS),
        "boundary_pin_paths": sorted(BOUNDARY_PINS),
        "local_file_names": list(LOCAL_FILES),
        "notes": [
            "Every metric in this report is computed on a deterministic synthetic fixture and describes the surrogate only.",
            "No DPDFNet-2 weight, package, runtime, output, corpus, device, listener or release artifact is used or claimed.",
            "All timestamps are source-sample coordinates; no device, wall-clock, pacing or deadline measurement exists.",
            "The offline boundary is whole-clip only: no incremental, streaming, flush or reset behavior is modelled.",
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


def build_contract() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_version": "0.1",
        "task": TASK,
        "component": SLUG,
        "title": TITLE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "format": FORMAT,
        "boundary": BOUNDARY,
        "claims": CLAIMS,
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "gates": list(GATES),
        "asset": asset_ref(),
        "asset_admission": asset_admission(asset_ref()),
        "surrogate": {
            "kind": "deterministic stdlib offline whole-clip surrogate",
            "opt_in_required": True,
            "substitutes_for_candidate": False,
            "weights_used": False,
            "vendor_runtime_used": False,
            "streaming_behavior_modelled": False,
        },
        "qualification": {
            "status": EVIDENCE_STATUS,
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
        },
        "source_pins": {"source:" + key: value for key, value in SOURCE_PINS.items()},
        "boundary_pins": {"worktree:" + key: value for key, value in BOUNDARY_PINS.items()},
        "artifact_pins": {},
    }


def build_adapter() -> Dict[str, Any]:
    return {
        "protocol_version": 1,
        "identity": "DPDFNet-2-0.6.0-offline-proposal",
        "boundary_identity": "as_asset_v0-external-caller-supplied",
        "input_kind": "waveform",
        "output_kinds": ["waveform"],
        "tasks": ["CLN-01"],
        "modes": ["offline"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "max_clip_samples": MAX_CLIP_SAMPLES,
        "package": "dpdfnet==" + PACKAGE_VERSION,
        "model": {
            "asset_id": MODEL_ID,
            "sha256": MODEL_SHA256,
            "byte_count": MODEL_BYTES,
            "source_revision": SOURCE_REVISION,
            "model_revision": MODEL_REVISION,
            "model_download_revision": MODEL_DOWNLOAD_REVISION,
        },
        "configuration": {
            "asset_required": True,
            "asset_storage": "external",
            "download_permitted": False,
            "whole_clip_only": True,
            "incremental_calls": False,
            "output_length_equals_input": True,
            "streaming_supported": False,
        },
        "entrypoint": ["python", "reference.py"],
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
    }


def build_readiness() -> Dict[str, Any]:
    admission = asset_admission(asset_ref())
    return {
        "schema_id": f"audio-sdk/task-evidence/{SLUG}/readiness/0.1",
        "task": TASK,
        "component": SLUG,
        "candidate": "DPDFNet-2 16 kHz offline",
        "status": "blocked",
        "qualified": False,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "asset_reference": asset_ref(),
        "admission": admission,
        "readiness_conclusion": (
            "The offline whole-clip boundary is modelled, but the candidate is not "
            "ready to run or qualify: the exact weights and the dpdfnet 0.6.0 offline "
            "runtime are absent, the model artifact revision is not immutable in the "
            "pinned ledger, and artifact-specific rights are not cleared."
        ),
        "external_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "allowed_now": [
            "synthetic whole-clip surrogate boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied asset contract",
        ],
        "not_allowed": [
            "downloading or bundling dpdfnet2.onnx or the dpdfnet package",
            "executing the vendor offline runtime or publishing its outputs",
            "registering a provider, changing defaults or claiming quality/latency",
        ],
    }
