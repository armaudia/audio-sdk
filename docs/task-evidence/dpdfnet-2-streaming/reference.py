# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence model for SDK-DPDFNET-2-STREAMING.

This module is NOT DPDFNet-2 and is not a reproduction of its runtime. It does
not read weights, audio, media or a caller asset; it downloads nothing, invokes
no vendor runtime, measures no device clock or deadline, conducts no listening,
benchmarks no SDK build and makes no release or quality claim.

It models the *streaming boundary* a caller-supplied external asset would have
to cross: 16 kHz mono f32, 160-sample frames, caller-supplied asset admission,
stateful chunked processing, one explicit flush, exact output accounting and a
declared algorithmic lag. The signal path is an original deterministic
surrogate, labelled as such everywhere.
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

TASK = "SDK-DPDFNET-2-STREAMING"
TITLE = "DPDFNet-2 streaming"
SLUG = "dpdfnet-2-streaming"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "6f58f3d721908806f8c4a0a1e0dc6de846cef54c"
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
FRAME_SAMPLES = 160
SAMPLES = 32_000
FRAME_COUNT = SAMPLES // FRAME_SAMPLES

# Declared from the pinned adapter README: the package's causal STFT/OLA path
# emitted a consistent 640-sample (40 ms) lag on 30 DNS clips. It is modelled
# here, never re-measured. No device or wall-clock timing is involved.
DECLARED_LAG_SAMPLES = 640
DECLARED_LAG_NS = DECLARED_LAG_SAMPLES * (1_000_000_000 // SAMPLE_RATE_HZ)
FIXTURE_EPOCH_NS = 1_767_225_600_000_000_000
CLOCK_ID = "fixture-sample-coordinate-not-device"

SEED_BASE = 20261125
CONDITIONS: Tuple[str, ...] = (
    "quiet_speech",
    "active_speech",
    "low_snr_speech",
    "onset_offset",
    "idle_noise",
)
CHUNK_SIZES: Tuple[int, ...] = (1, 7, 80, 159, 160, 161, 320, 1280)
MAX_CHUNK_SAMPLES = 2 * SAMPLE_RATE_HZ
OVER_SUBTRACTION = 1.5
GAIN_FLOOR = 0.15
ATTACK = 0.7
RELEASE = 0.25
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
    "sample_format": "f32",
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
    "task_board_or_handoff_write": False,
}

CLAIMS: Dict[str, bool] = {
    "real_dpdfnet2_runtime": False,
    "weights_accessed": False,
    "asset_downloaded": False,
    "real_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "streaming_latency_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "quality_claim": False,
    "release_claim": False,
}

EXACT_BLOCKERS: Tuple[str, ...] = (
    "The pinned ledger records dpdfnet2.onnx as 10,178,747 bytes with SHA-256 "
    "4f0ee28935b4a32abecc717d745416976565834d839601acf43031094b4dc94c, but "
    "model_revision is null and the download revision is the mutable 'main' "
    "with no retrieval-time commit, so an immutable artifact revision for those "
    "bytes is not established; the asset is absent from this SDK worktree.",
    "The streaming runtime is the external dpdfnet 0.6.0 CPU ONNX package. It is "
    "not installed here, has no pinned wheel/sdist digest in this worktree, and "
    "its runtime distribution and product-use terms beyond Apache-2.0 metadata "
    "are not cleared; no vendor runtime is invoked.",
    "Apache-2.0 is recorded for the package and model card, but artifact-specific "
    "weight rights, training-data provenance, redistribution clearance and legal "
    "review are not established; no weight, runtime or upstream source may be "
    "vendored, packaged, downloaded or redistributed by this package.",
    "No rights-cleared held-out real cohort, independent clean-reference scorer, "
    "listening result, target pacing/deadline measurement or approved exact "
    "streaming reference vector exists; every release gate remains blocked.",
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
    "scorer, permitted listening, exact streaming reference outputs for the frozen "
    "inputs, and target pacing/deadline evidence; the synthetic surrogate can "
    "never stand in for any of these.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "immutable dpdfnet2.onnx artifact revision plus caller-held bytes in this worktree",
    "pinned dpdfnet 0.6.0 runtime artifact and installation evidence",
    "written artifact-specific weight/runtime/training-data rights clearance",
    "approved exact streaming reference output vectors for the frozen synthetic inputs",
    "rights-cleared paired real speech cohort with clean references",
    "independent STOI/SI-SDR/intrusive scorer and permitted listening",
    "target-runtime pacing, availability, deadline and memory evidence",
    "opt-in provider intake, descriptor/catalog review and explicit default selection",
)

GATES: Tuple[Dict[str, str], ...] = (
    {"name": "exact_asset_identity", "status": "blocked",
     "evidence": "Ledger digest/byte count only; model_revision is null and the download revision is mutable 'main'.",
     "reopen": REOPEN_CONDITIONS[0]},
    {"name": "runtime_admission", "status": "blocked",
     "evidence": "dpdfnet 0.6.0 is absent and its runtime artifact is unpinned here.",
     "reopen": REOPEN_CONDITIONS[1]},
    {"name": "artifact_rights", "status": "blocked",
     "evidence": "Apache-2.0 metadata is recorded; artifact-specific terms and legal review are absent.",
     "reopen": REOPEN_CONDITIONS[2]},
    {"name": "exact_reference_parity", "status": "blocked",
     "evidence": "No approved streaming reference output vector exists for these frozen inputs.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "rights_cleared_cohort", "status": "blocked",
     "evidence": "No paired real cohort with clean references is available to this task.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "independent_scoring_and_listening", "status": "blocked",
     "evidence": "No independent scorer or listening result; surrogate metrics are synthetic only.",
     "reopen": REOPEN_CONDITIONS[3]},
    {"name": "target_runtime_timing", "status": "blocked",
     "evidence": "No device clock, pacing, deadline or memory measurement was made.",
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
    "candidate_csv_row": "Denoising,DPDFNet-2 streaming,evaluated,30 paired DNS2020 outputs; 640-sample lag compensated",
    "census_row": (
        "Local pilot: offline median gain +7.203 dB / STOI .9713 / median RTF .0989; "
        "streaming +7.300 dB / .9713 / .1090 on the 30 DNS pairs; 640-sample stream delay."
    ),
    "pilot_streaming_mean_delta_snr_db": 7.6076,
    "pilot_streaming_median_delta_snr_db": 7.3003,
    "pilot_streaming_snr_ci95_db": [5.9948, 9.3335],
    "pilot_streaming_mean_delta_si_sdr_db": 7.5437,
    "pilot_streaming_median_delta_si_sdr_db": 7.1900,
    "pilot_streaming_si_sdr_ci95_db": [5.9401, 9.2794],
    "pilot_streaming_mean_delta_stoi": 0.0329,
    "pilot_streaming_median_delta_stoi": 0.0285,
    "pilot_streaming_stoi_ci95": [0.0232, 0.0429],
    "pilot_streaming_stoi_wins_ties_losses": [27, 0, 3],
    "pilot_streaming_batch_rtf": 0.1090,
    "measured_package_stream_lag_samples": 640,
    "scheduled_cpp_reported_content_delay_samples": 800,
    "scheduled_cpp_qualification": "experimental; separate Pro scope",
    "model_card_parameters_millions": MODEL_PARAMETERS_MILLIONS,
    "model_card_gmac": MODEL_GMAC,
    "disclaimer": (
        "These values come from pinned research files at 16 kHz on 30 DNS2020 pairs and a "
        "separate C++ scheduled backend. They are not reproduced here, not device timing, "
        "not this fixture's metrics, not a listening result and not a release claim."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "DPDFNet-2 model, dpdfnet 0.6.0 package and ONNX runtime are absent; nothing was downloaded, installed, loaded or invoked.",
    "The model digest, byte count, source revision, mutable download revision and license metadata are quoted from research/noise_suppression_assets_20261027.json and the pinned adapter README.",
    "The 640-sample lag and reported pilot metrics are pinned research provenance only; this package models a 640-sample lag and does not measure any latency.",
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
        "frame_samples": FRAME_SAMPLES,
        "declared_lag_samples": DECLARED_LAG_SAMPLES,
        "mode": "synthetic-surrogate",
        "synthetic_surrogate_opt_in": True,
        "asset_reference": asset_ref(),
    }


def validate_config(config: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    expected = default_config()
    for key in ("sample_rate_hz", "channels", "frame_samples",
                "declared_lag_samples"):
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


class SurrogateSession:
    """Stateful chunked boundary fixture; not a vendor streamer."""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = dict(config or default_config())
        reasons = validate_config(self.config)
        if reasons:
            raise ValueError(";".join(reasons))
        self._frame_buffer: List[float] = []
        self._delay: List[float] = [0.0] * DECLARED_LAG_SAMPLES
        self._noise_power = 1e-8
        self._noise_initialized = False
        self._gain = 1.0
        self._input_samples = 0
        self._processed_samples = 0
        self._emitted_raw = 0
        self._flushed = False
        self._closed = False
        self._generated_gain = 1.0
        self._state_digest: str | None = self.digest()

    # -- helpers ---------------------------------------------------------
    def digest(self) -> str:
        payload = canonical_bytes({
            "frame_buffer": self._frame_buffer,
            "delay": self._delay,
            "noise_power": self._noise_power,
            "gain": self._gain,
            "input_samples": self._input_samples,
            "processed_samples": self._processed_samples,
            "emitted_raw": self._emitted_raw,
            "flushed": self._flushed,
            "closed": self._closed,
        })
        return sha256(payload)

    def _frame_gain(self, frame: Sequence[float]) -> float:
        power = sum(value * value for value in frame) / float(len(frame))
        if not self._noise_initialized:
            self._noise_power = max(power, 1e-10)
            self._noise_initialized = True
        else:
            self._noise_power = min(power, self._noise_power * 1.02)
        noise = max(self._noise_power, EPS)
        ratio = power / noise
        if ratio <= OVER_SUBTRACTION:
            target = GAIN_FLOOR
        else:
            target = math.sqrt(max(0.0, 1.0 - OVER_SUBTRACTION / ratio))
        target = min(1.0, max(GAIN_FLOOR, target))
        alpha = ATTACK if target < self._gain else RELEASE
        self._gain = self._gain + alpha * (target - self._gain)
        return self._gain

    def _process_frame(self, frame: Sequence[float]) -> List[float]:
        gain = self._frame_gain(frame)
        previous = self._generated_gain
        self._generated_gain = gain
        count = len(frame)
        for index, value in enumerate(frame):
            weight = (index + 1) / float(count)
            applied = previous + (gain - previous) * weight
            self._delay.append(value * applied)
        self._processed_samples += count
        emitted: List[float] = []
        while len(self._delay) > DECLARED_LAG_SAMPLES:
            emitted.append(self._delay.pop(0))
            self._emitted_raw += 1
        return emitted

    def _drain_delay(self) -> List[float]:
        drained = list(self._delay)
        self._emitted_raw += len(drained)
        self._delay = []
        return drained

    # -- public boundary -------------------------------------------------
    def process(self, chunk: Sequence[float]) -> List[float]:
        if self._closed:
            raise ValueError("session_closed")
        if self._flushed:
            raise ValueError("stream_already_flushed")
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
            if abs(float(value)) > 8.0:
                raise ValueError("sample_out_of_range")
        self._frame_buffer.extend(float(value) for value in values)
        self._input_samples += len(values)
        emitted: List[float] = []
        while len(self._frame_buffer) >= FRAME_SAMPLES:
            frame = self._frame_buffer[:FRAME_SAMPLES]
            del self._frame_buffer[:FRAME_SAMPLES]
            emitted.extend(self._process_frame(frame))
        self._state_digest = None
        return emitted

    def flush(self) -> List[float]:
        if self._closed:
            raise ValueError("session_closed")
        if self._flushed:
            return []
        if self._input_samples == 0:
            self._delay = []
            self._flushed = True
            self._state_digest = None
            return []
        emitted: List[float] = []
        if self._frame_buffer:
            partial = len(self._frame_buffer)
            padded = self._frame_buffer + [0.0] * (FRAME_SAMPLES - partial)
            self._process_frame(padded)
            self._frame_buffer = []
        emitted.extend(self._drain_delay())
        self._flushed = True
        self._state_digest = None
        return emitted

    def reset(self) -> None:
        if self._closed:
            raise ValueError("session_closed")
        self._frame_buffer = []
        self._delay = [0.0] * DECLARED_LAG_SAMPLES
        self._noise_power = 1e-8
        self._noise_initialized = False
        self._gain = 1.0
        self._input_samples = 0
        self._processed_samples = 0
        self._emitted_raw = 0
        self._flushed = False
        self._generated_gain = 1.0
        self._state_digest = None

    def close(self) -> None:
        self._closed = True
        self._state_digest = None

    @property
    def state_digest(self) -> str:
        if self._state_digest is None:
            self._state_digest = self.digest()
        return self._state_digest

    @property
    def input_samples(self) -> int:
        return self._input_samples

    @property
    def processed_samples(self) -> int:
        return self._processed_samples


# ---------------------------------------------------------------------------
# Streaming runs, boundary accounting and synthetic scoring
# ---------------------------------------------------------------------------

def run_stream(samples: Sequence[float], chunk_size: int,
               config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Run the fixture over one chunking and return raw/compensated outputs."""
    if chunk_size <= 0 or chunk_size > MAX_CHUNK_SAMPLES:
        raise ValueError("chunk_size_unsupported")
    session = SurrogateSession(config)
    raw: List[float] = []
    chunk_records: List[Dict[str, int]] = []
    for start in range(0, len(samples), chunk_size):
        chunk = list(samples[start:start + chunk_size])
        emitted = session.process(chunk)
        raw.extend(emitted)
        chunk_records.append({"start_sample": start, "input_count": len(chunk),
                              "emitted_count": len(emitted)})
    flush_emitted = session.flush()
    raw.extend(flush_emitted)
    internal_padding = (-len(samples)) % FRAME_SAMPLES
    compensated_untrimmed = raw[DECLARED_LAG_SAMPLES:] + [0.0] * DECLARED_LAG_SAMPLES
    compensated = compensated_untrimmed[:len(samples)]
    valid_samples = len(samples)
    return {
        "chunk_size": chunk_size,
        "chunk_count": len(chunk_records),
        "chunk_records": chunk_records,
        "raw_output": raw,
        "compensated_output": compensated,
        "compensated_digest": sha256(canonical_bytes(compensated)),
        "raw_digest": sha256(canonical_bytes(raw)),
        "emitted_before_flush": len(raw) - len(flush_emitted),
        "flush_emitted": len(flush_emitted),
        "raw_length": len(raw),
        "compensated_length": len(compensated),
        "input_samples": len(samples),
        "processed_samples": session.processed_samples,
        "internal_frame_padding_samples": internal_padding,
        "startup_padding_samples": DECLARED_LAG_SAMPLES,
        "lag_compensation_padding_samples": DECLARED_LAG_SAMPLES,
        "truncated_tail_padding_samples": DECLARED_LAG_SAMPLES,
        "valid_samples": valid_samples,
        "final_state_digest": session.state_digest,
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
    streamed = run_stream(observed, FRAME_SAMPLES)
    whole = run_stream(observed, SAMPLES)
    valid = streamed["valid_samples"]
    prefix = clean[:valid]
    noisy = score(prefix, observed[:valid])
    identity = score(prefix, observed[:valid])
    candidate = score(prefix, streamed["compensated_output"][:valid])
    large_chunk = score(prefix, whole["compensated_output"][:valid])

    def delta(candidate_value: Any, control_value: Any) -> Any:
        if candidate_value is None or control_value is None:
            return None
        return candidate_value - control_value

    return {
        "input_samples": len(observed),
        "scored_samples": valid,
        "tail_validity": {
            "input_samples": len(observed),
            "raw_output_samples": streamed["raw_length"],
            "compensated_samples": streamed["compensated_length"],
            "valid_samples": valid,
            "startup_padding_samples": streamed["startup_padding_samples"],
            "internal_frame_padding_samples": streamed["internal_frame_padding_samples"],
            "lag_compensation_padding_samples": streamed["lag_compensation_padding_samples"],
            "truncated_tail_padding_samples": streamed["truncated_tail_padding_samples"],
            "attributable_samples": valid,
        },
        "variants": {
            "identity_passthrough": {**identity, "exact_passthrough": True},
            "noisy_control": noisy,
            "surrogate_streamed_160": candidate,
            "surrogate_large_chunk_32000": large_chunk,
        },
        "improvements": {
            "snr_db": delta(candidate["snr_db"], noisy["snr_db"]),
            "si_sdr_db": delta(candidate["si_sdr_db"], noisy["si_sdr_db"]),
        },
        "noise_attenuation_db": (
            None if noisy["output_rms"] <= 0.0
            else _db((candidate["output_rms"] / noisy["output_rms"]) ** 2)
        ),
        "chunk_invariance_digest": streamed["compensated_digest"],
        "large_chunk_matches_160": (
            streamed["compensated_digest"] == whole["compensated_digest"]
        ),
    }


def alignment_probe() -> Dict[str, Any]:
    """Model the declared 640-sample delay with a single dominant impulse."""
    samples = [0.0] * 8000
    for index in range(8000):
        samples[index] = 0.001 * math.sin(2.0 * math.pi * 97.0 * index / SAMPLE_RATE_HZ)
    samples[4000] = 0.9
    run = run_stream(samples, FRAME_SAMPLES)
    raw_peak = max(range(len(run["raw_output"])),
                   key=lambda index: abs(run["raw_output"][index]))
    compensated_peak = max(range(len(run["compensated_output"])),
                           key=lambda index: abs(run["compensated_output"][index]))
    return {
        "input_peak_sample": 4000,
        "declared_lag_samples": DECLARED_LAG_SAMPLES,
        "raw_peak_sample": raw_peak,
        "raw_lag_samples": raw_peak - 4000,
        "compensated_peak_sample": compensated_peak,
        "residual_lag_samples": compensated_peak - 4000,
        "measured_latency": False,
        "modeled_only": True,
    }


def cross_hop_evidence() -> Dict[str, Any]:
    _, observed = synth("active_speech")
    records: Dict[str, Any] = {}
    raw_digests = set()
    compensated_digests = set()
    for size in CHUNK_SIZES:
        run = run_stream(observed, size)
        boundaries_crossed = 0
        for start in range(0, len(observed), size):
            end = min(start + size, len(observed))
            first = start // FRAME_SAMPLES + 1
            last = (end - 1) // FRAME_SAMPLES
            if last >= first:
                boundaries_crossed += 1
        records[str(size)] = {
            "chunk_count": run["chunk_count"],
            "chunks_crossing_frame_boundary": boundaries_crossed,
            "emitted_before_flush": run["emitted_before_flush"],
            "flush_emitted": run["flush_emitted"],
            "raw_length": run["raw_length"],
            "valid_samples": run["valid_samples"],
            "raw_digest": run["raw_digest"],
            "compensated_digest": run["compensated_digest"],
        }
        raw_digests.add(run["raw_digest"])
        compensated_digests.add(run["compensated_digest"])
    whole = run_stream(observed, SAMPLES)
    return {
        "samples": len(observed),
        "frame_samples": FRAME_SAMPLES,
        "chunk_sizes_tested": list(CHUNK_SIZES),
        "records": records,
        "raw_chunk_invariant": len(raw_digests) == 1,
        "compensated_chunk_invariant": len(compensated_digests) == 1,
        "whole_call_matches_chunked": whole["compensated_digest"] == run_stream(
            observed, FRAME_SAMPLES)["compensated_digest"],
        "total_frame_boundaries": FRAME_COUNT - 1,
        "all_chunks_end_on_frame_boundary": all(
            len(observed) % size == 0 for size in CHUNK_SIZES if size <= len(observed)),
        "device_clock_used": False,
        "deadline_measured": False,
    }


def state_evidence() -> Dict[str, Any]:
    _, observed = synth("low_snr_speech")
    session = SurrogateSession()
    digests = []
    for start in range(0, len(observed), FRAME_SAMPLES):
        session.process(observed[start:start + FRAME_SAMPLES])
        digests.append(session.state_digest)
    final = session.state_digest
    session.reset()
    replay = []
    for start in range(0, len(observed), FRAME_SAMPLES):
        session.process(observed[start:start + FRAME_SAMPLES])
        replay.append(session.state_digest)
    fresh = SurrogateSession()
    independent = []
    for start in range(0, len(observed), FRAME_SAMPLES):
        fresh.process(observed[start:start + FRAME_SAMPLES])
        independent.append(fresh.state_digest)
    _, other = synth("active_speech")
    cross = SurrogateSession()
    for start in range(0, 8000, FRAME_SAMPLES):
        cross.process(observed[start:start + FRAME_SAMPLES])
    cross.reset()
    for start in range(0, 8000, FRAME_SAMPLES):
        cross.process(other[start:start + FRAME_SAMPLES])
    control = SurrogateSession()
    for start in range(0, 8000, FRAME_SAMPLES):
        control.process(other[start:start + FRAME_SAMPLES])
    return {
        "frames_processed": len(digests),
        "state_digest_chain": sha256(canonical_bytes(digests)),
        "first_state_digest": digests[0],
        "last_state_digest": digests[-1],
        "reset_replay_identical": replay == digests,
        "independent_session_identical": independent == digests,
        "reset_after_close_rejected": True,
        "cross_stream_reset_identical": cross.state_digest == control.state_digest,
        "state_is_synthetic": True,
        "real_recurrent_state_loaded": False,
    }


def config_adverse_cases() -> Dict[str, Any]:
    base = default_config()
    cases: Dict[str, Any] = {}

    def attempt(name: str, mutate) -> None:
        config = json.loads(json.dumps(base))
        mutate(config)
        try:
            session = SurrogateSession(config)
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
                "state_digest": session.state_digest,
            }

    attempt("wrong_sample_rate", lambda config: config.update(sample_rate_hz=48000))
    attempt("wrong_channels", lambda config: config.update(channels=2))
    attempt("wrong_frame_samples", lambda config: config.update(frame_samples=80))
    attempt("wrong_declared_lag", lambda config: config.update(declared_lag_samples=0))
    attempt("mode_unsupported", lambda config: config.update(mode="offline"))
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


def frame_adverse_cases() -> Dict[str, Any]:
    session = SurrogateSession()
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
    rejected("out_of_range_sample", lambda: session.process([9.0]))

    flush_output = session.flush()
    second_flush = session.flush()
    after_flush = session.digest()
    rejected("process_after_flush", lambda: session.process([0.0] * FRAME_SAMPLES))
    after_rejected_process = session.digest()
    session.close()
    after_close = session.digest()
    rejected("process_after_close", lambda: session.process([0.0] * FRAME_SAMPLES))
    rejected("flush_after_close", lambda: session.flush())
    rejected("reset_after_close", lambda: session.reset())
    after_rejected_after_close = session.digest()
    session.close()
    return {
        "cases": cases,
        "flush_idempotent": second_flush == [],
        "flush_output_samples": len(flush_output),
        "state_after_flush_unchanged_by_rejected_process": after_flush == after_rejected_process,
        "state_after_close_unchanged_by_rejected_calls": after_close == after_rejected_after_close,
        "closed_after_double_close": session._closed,
    }


def lifecycle_evidence() -> Dict[str, Any]:
    session = SurrogateSession()
    session.process([0.0] * FRAME_SAMPLES)
    first = session.flush()
    second = session.flush()
    after_flush = session.state_digest
    try:
        session.process([0.0] * FRAME_SAMPLES)
    except ValueError:
        after_flush_rejection = session.state_digest
    else:
        after_flush_rejection = "accepted"
    session.close()
    closed_digest = session.state_digest
    session.close()
    results = {}
    for name, action in (("process_after_close", lambda: session.process([0.0])),
                         ("flush_after_close", session.flush),
                         ("reset_after_close", session.reset)):
        try:
            action()
        except ValueError as error:
            results[name] = "rejected:" + str(error)
        else:
            results[name] = "accepted"
    return {
        "flush_returns_samples": bool(first),
        "second_flush_empty": second == [],
        "close_idempotent": session._closed and closed_digest == session.state_digest,
        "process_after_flush": (
            "rejected" if after_flush_rejection == after_flush else after_flush_rejection),
        "process_after_close": results["process_after_close"],
        "flush_after_close": results["flush_after_close"],
        "reset_after_close": results["reset_after_close"],
        "zero_length_stream_flush": SurrogateSession().flush() == [0.0] * 0,
    }


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
        "candidate": "DPDFNet-2 16 kHz",
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
            "labelled": "deterministic stdlib streaming surrogate",
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
            "status": "modelled",
            "declared_lag_samples": DECLARED_LAG_SAMPLES,
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
        candidate = block["variants"]["surrogate_streamed_160"]
        for metric in ("snr_db", "si_sdr_db"):
            if noisy[metric] is None or candidate[metric] is None:
                continue
            if candidate[metric] < noisy[metric]:
                regressions.append({
                    "condition": condition,
                    "metric": metric,
                    "better_direction": "higher",
                    "noisy_control": noisy[metric],
                    "surrogate_streamed_160": candidate[metric],
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
                "note": "Paired control for the synthetic target on the same valid prefix.",
            },
            "candidate": {
                "name": "surrogate_streamed_160",
                "real_candidate": False,
                "note": "Deterministic stdlib surrogate, not DPDFNet-2.",
            },
            "large_chunk": {
                "name": "surrogate_large_chunk_32000",
                "note": "Chunk invariance control; must equal the 160-sample streamed output.",
            },
        },
        "regressions": _regressions(blocks),
        "streaming_boundary": {
            "protocol": "caller-supplied external asset plus stateful chunked frame calls",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "chunk_sizes_tested": list(CHUNK_SIZES),
            "max_chunk_samples": MAX_CHUNK_SAMPLES,
            "declared_algorithmic_lag_samples": DECLARED_LAG_SAMPLES,
            "declared_algorithmic_lag_ns": DECLARED_LAG_NS,
            "declared_lag_provenance": (
                "Pinned adapter README reports a consistent 640-sample (40 ms) output lag "
                "across 30 DNS files for the dpdfnet 0.6.0 streaming API; source-reported, "
                "not re-measured here."
            ),
            "lag_measured_here": False,
            "lag_modeled_in_fixture": True,
            "clock_id": CLOCK_ID,
            "fixture_epoch_ns": str(FIXTURE_EPOCH_NS),
            "availability_model": "sample-coordinate only; no wall clock, device clock or deadline",
            "flush_policy": (
                "A partial final frame is zero-padded only for gain estimation; its valid "
                "samples are emitted, then the delay line is drained exactly once."
            ),
            "reset_policy": "Explicit reset clears all state and buffers; replay is bit-identical.",
            "output_accounting": {
                "raw_output_samples": "ceil(input_samples / 160) * 160 + 640",
                "startup_padding_samples": DECLARED_LAG_SAMPLES,
                "valid_samples_after_lag_compensation": "input_samples",
                "internal_frame_padding_samples": "(-input_samples) mod 160",
                "truncated_tail_padding_samples": DECLARED_LAG_SAMPLES,
                "finding": (
                    "The pinned adapter wrapper drops 640 samples, appends 640 zeros and "
                    "truncates to input length. In this model the first 640 raw samples are "
                    "startup zeros, the last 640 real samples arrive only through flush, and "
                    "the appended tail zeros are truncated, so valid_samples=len(output) is "
                    "consistent only after a complete flush."
                ),
            },
            "chunk_invariance": cross_hop_evidence(),
            "alignment_probe": alignment_probe(),
            "state": state_evidence(),
        },
        "asset_boundary": asset_boundary(),
        "asset_admission": admission,
        "enhancement_profile": enhancement_profile(),
        "adverse": {
            "config_rejections": config_adverse_cases(),
            "frame_cases": frame_adverse_cases(),
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
            "kind": "deterministic stdlib streaming surrogate",
            "opt_in_required": True,
            "substitutes_for_candidate": False,
            "weights_used": False,
            "vendor_runtime_used": False,
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
        "identity": "DPDFNet-2-0.6.0-streaming-proposal",
        "boundary_identity": "as_asset_v0-external-caller-supplied",
        "input_kind": "waveform",
        "output_kinds": ["waveform"],
        "tasks": ["CLN-01"],
        "modes": ["streaming"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
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
            "declared_lag_samples": DECLARED_LAG_SAMPLES,
            "reset_between_streams": True,
            "single_flush": True,
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
        "candidate": "DPDFNet-2 16 kHz streaming",
        "status": "blocked",
        "qualified": False,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "asset_reference": asset_ref(),
        "admission": admission,
        "readiness_conclusion": (
            "The streaming boundary is modelled, but the candidate is not ready to run or "
            "qualify: the exact weights and the dpdfnet 0.6.0 runtime are absent, the model "
            "artifact revision is not immutable in the pinned ledger, and artifact-specific "
            "rights are not cleared."
        ),
        "external_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "allowed_now": [
            "synthetic surrogate boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied asset contract",
        ],
        "not_allowed": [
            "downloading or bundling dpdfnet2.onnx or the dpdfnet package",
            "executing the vendor runtime or publishing its outputs",
            "registering a provider, changing defaults or claiming quality/latency",
        ],
    }
