# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local offline surrogate for SDK-GTCRN-DNS3-OFFLINE.

This module models the documented GTCRN DNS3 **offline** boundary from
``adapters/gtcrn/run.py``.  No checkpoint, torch runtime or redistribution
right is available to this task, so the candidate path here is a deterministic
pure-Python whole-utterance STFT/ISTFT spectral-gain surrogate, not GTCRN, not
torch and not a model inference.  The caller-supplied-asset path is declared,
pinned and fails closed; it never falls back to the surrogate.  Nothing here is
real audio, a listening result, a device measurement, a benchmark or a release
qualification.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import scorer
from scorer import SCORER_ID, si_sdr, stoi

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2])))
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK_ID = "SDK-GTCRN-DNS3-OFFLINE"
TITLE = "GTCRN DNS3 offline"
SLUG = "gtcrn-dns3-offline"
COMPONENT_ID = "gtcrn-dns3-offline"
REFERENCE_FAMILY = "gtcrn"
BASE_COMMIT = "c7cb12877fb8dce8620ba4963f0496a8061d9f7b"
BRANCH = "swarm/SDK-GTCRN-DNS3-OFFLINE"
TASK_REL = f"docs/task-evidence/{SLUG}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_offline_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "provider_registration"
EVIDENCE_INTERPRETER = "3.12.16"
ADAPTER_ID = "gtcrn-dns3-offline-caller-asset-surrogate-v1"

UPSTREAM_REPOSITORY = "https://github.com/Xiaobin-Rong/gtcrn"
UPSTREAM_COMMIT = "502ebfab64da7c4a9af78dcb9c6ceef1ebb01c73"
UPSTREAM_LICENSE = "MIT"
UPSTREAM_LICENSE_COPYRIGHT = "Copyright (c) 2024 Rong Xiaobin"
UPSTREAM_SNAPSHOT = "data/checkouts/GTCRN"
UPSTREAM_ADAPTER_IDENTITY = f"GTCRN-official-{UPSTREAM_COMMIT}"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
N_FFT = 512
WINDOW_SAMPLES = 512
HOP_SAMPLES = 256
HOP_MS = 1000.0 * HOP_SAMPLES / SAMPLE_RATE_HZ
STFT_BINS = N_FFT // 2 + 1
PADDING_SAMPLES = N_FFT // 2
CONTENT_DELAY_SAMPLES = 0
CONTENT_DELAY_MS = 0.0
MIN_SAMPLES = 2
MAX_ABS_INPUT = 2.0
CLIPPING_THRESHOLD = 0.98
SIGNAL_SAMPLES = 9728
TAIL_SAMPLES = 9819
SEED_BASE = 20261126

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
    "model_input_shape": "[1,257,T,2]",
    "model_output_shape": "[1,257,T,2]",
    "frame_count_formula": "T=1+floor(N/256)",
    "istft_length": "input_sample_count",
    "output_samples": "input_sample_count",
    "source_time_mapping": "identity",
    "content_delay_samples": CONTENT_DELAY_SAMPLES,
    "content_delay_ms": CONTENT_DELAY_MS,
    "streaming_state": "none_offline_whole_utterance",
    "reset_behavior": "not_applicable_offline_stateless",
    "real_time_causal": False,
    "measured_timing": False,
    "note": (
        "Analytical sample-count geometry only. Offline whole-utterance STFT/ISTFT "
        "uses centered framing and returns an output aligned sample-for-sample with "
        "the input. It is explicitly non-causal and makes no stream, device or "
        "deadline claim."
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

BOUNDARY = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "processor_exposure": False,
    "c_public_boundary": False,
    "descriptor_registry_change": False,
    "shared_cmakelists_change": False,
    "installed_v0_behavior_change": False,
    "ci_change": False,
    "installed_v0_geometry_preserved": True,
    "evaluation_path": "task_local_python_offline_surrogate",
    "production_callback_path": "not_implemented",
    "real_asset_required": True,
    "real_asset_present": False,
    "real_runtime_invoked": False,
    "silent_fallback_to_surrogate": False,
}

SCOPE = {
    "provider_registered": False,
    "descriptor_changed": False,
    "registry_changed": False,
    "default_changed": False,
    "public_api_abi_changed": False,
    "shared_build_changed": False,
    "ci_changed": False,
    "contracts_changed": False,
    "board_changed": False,
    "handoff_changed": False,
    "reviewer_dispatched": False,
    "release_changed": False,
    "real_audio_used": False,
    "weights_downloaded": False,
    "asset_vendored": False,
}

NEGATIVE_CLAIMS = {
    "real_model_weights": False,
    "real_media": False,
    "device_timing": False,
    "listening_result": False,
    "benchmark_claim": False,
    "release_claim": False,
    "torch_runtime_invoked": False,
    "onnx_runtime_invoked": False,
    "real_inference_executed": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "installed_v0_behavior_change": False,
    "weights_downloaded": False,
    "asset_vendored": False,
    "training_data_rights_cleared": False,
}

CONFIG = {"mode": "offline_surrogate", "asset": "caller_supplied_asset"}
SURROGATE_MODE = "offline_surrogate"
REAL_MODE = "caller_supplied_gtcrn"
ASSET_REFERENCE = "caller_supplied_asset"

SURROGATE_PARAMETERS = {
    "noise_frame_fraction": 0.2,
    "oversubtraction": 1.0,
    "minimum_gain": 0.08,
    "frequency_smoothing": "three_point_binomial_1_2_1",
    "magnitude_subtraction": True,
    "tuned_on_results": False,
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

EXPECTED_ASSET_FILES = (
    {"path": "gtcrn.py", "bytes": 13504,
     "sha256": "20bf0610702506fa45cd543454b84bbeb862d73c7c20a3f8d820fdc04da6099b"},
    {"path": "checkpoints/model_trained_on_dns3.tar", "bytes": 579819,
     "sha256": "a630d992cf792daf4ce2bb5bcf9c4d389f740a8f09c6e0971184697fe6371b79"},
)
EXPECTED_ASSET_PATHS = tuple(item["path"] for item in EXPECTED_ASSET_FILES)
EXPECTED_RUNTIME_ID = "cpython-3.10-macos-arm64-torch-1.13.1-torchaudio-0.13.1"
EXPECTED_RUNTIME = {
    "id": EXPECTED_RUNTIME_ID,
    "python": "CPython 3.10",
    "platform": "macOS arm64",
    "torch": "1.13.1",
    "torchaudio": "0.13.1",
    "numpy": "1.26.4",
    "soundfile": "0.12.1",
    "einops": "0.7.0",
    "lock": "adapters/gtcrn/requirements.lock",
    "evidence_interpreter": f"CPython {EVIDENCE_INTERPRETER}",
    "installed_in_sdk_worktree": False,
    "torch_importable_in_evidence_interpreter": False,
}

ASSET_PINS = {f"asset:{item['path']}": item["sha256"] for item in EXPECTED_ASSET_FILES}

SOURCE_PINS: Dict[str, str] = {
    "source:adapters/gtcrn/run.py":
        "fe1b9874e0fc24976fd00488905260566226d0e542f07e2123e98a1b4b6f61b4",
    "source:adapters/gtcrn/adapter.json":
        "4b9ea400e16af24ec10641c41aec01fcec54d4238f97dc26b655e394d0df58f6",
    "source:adapters/gtcrn/README.md":
        "ee780b086f8de55aede490cda930711187bb08e5d7696cad929070a5486fab73",
    "source:adapters/gtcrn/requirements.lock":
        "cabd5f6fe7baa1bde6eff7a136173061b284b83046fa8615508179e217d7dabb",
    "source:adapters/deepfilternet3-python/requirements.lock":
        "7e3135f4211dbb57004f8f93b49be94db3f3b0bf23cbf5b4476ad67a0bc2be95",
    "source:data/checkouts/GTCRN/LICENSE":
        "c467165e5860b4a7494ef4a6e2788e4115d95b5b8989bb5f86287089adddf794",
    "source:data/checkouts/GTCRN/README.md":
        "7f890b7a9b1d7b49613733878e104233a3a3019854b3105007be69db37e33413",
    "source:data/checkouts/GTCRN/requirements.txt":
        "c026bf264c0eefd4249c9c88380ccda331cb453c55228a6ba43fe44f12dd8428",
    "source:research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "source:research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "source:research/selected_audio_enhancement_candidates.md":
        "0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946",
    "source:research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "source:research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "source:REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "source:audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
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
    "exact_assets_and_runtime_present",
    "weight_and_runtime_rights_cleared",
    "real_offline_parity_and_alignment",
    "held_out_paired_denoising_cohort",
    "independent_listening_or_predictive_screen",
    "target_runtime_timing_and_memory",
    "provider_intake_descriptor_and_default_review",
)

GATE_REOPEN = {
    "exact_assets_and_runtime_present":
        "Supply both hash-pinned caller assets and a pinned CPython 3.10 torch 1.13.1 runtime in an approved isolated runner.",
    "weight_and_runtime_rights_cleared":
        "Record checkpoint-specific terms, DNS3 training-data provenance and overlap, torch redistribution/product terms, and a positive legal decision.",
    "real_offline_parity_and_alignment":
        "Run the exact GTCRN offline model and compare output length, identity alignment, finiteness and numerical parity against the pinned source.",
    "held_out_paired_denoising_cohort":
        "Run a predeclared held-out real paired denoising cohort with matched identity and noisy-input controls and paired SI-SDR/STOI.",
    "independent_listening_or_predictive_screen":
        "Collect authorized independent listening or a separately labeled predictive screen; never substitute synthetic scores for either.",
    "target_runtime_timing_and_memory":
        "Measure content/availability timing, memory and deadline behavior for the exact target runtime and workload.",
    "provider_intake_descriptor_and_default_review":
        "Complete provider intake, descriptor review and explicit default-selection review before any registry or catalog change.",
}

EXACT_BLOCKERS = [
    "No caller-supplied GTCRN DNS3 asset (gtcrn.py plus checkpoints/model_trained_on_dns3.tar) is present in the SDK worktree; the external research checkout was not read, loaded or redistributed by this package.",
    "The pinned runtime (CPython 3.10, macOS arm64, torch 1.13.1, torchaudio 0.13.1) is not installed in the pinned CPython 3.12.16 evidence interpreter, where torch is not importable.",
    "Checkpoint-specific terms, DNS3 training-data provenance/overlap, redistribution and product-use clearance are not established; only upstream source code MIT is recorded, with no legal review.",
    "No real offline parity, held-out paired real-audio cohort, listening or target-device timing exists; no benchmark or release claim is made.",
]

MISSING_EVIDENCE = [
    "exact caller-supplied GTCRN weight and source asset present and loaded",
    "pinned CPython 3.10 torch 1.13.1 runtime installed and verified",
    "checkpoint-specific terms, training-data provenance and legal clearance",
    "real offline GTCRN parity and exact output alignment",
    "held-out real paired denoising cohort",
    "real clean-speech preservation diagnostics",
    "independent listening or separately labeled predictive screen",
    "target-runtime content timing, memory and deadlines",
    "provider intake, descriptor and default-selection review",
    "training/evaluation overlap assessment",
]

SURROGATE_LIMITATIONS = [
    "The surrogate is pure-Python offline STFT magnitude subtraction, not the GTCRN network or torch.",
    "It has no recurrent cache, no learned weights, no phase model and no ONNX graph.",
    "Synthetic harmonic signals are not speech, not DNS2020 and not a listening proxy.",
    "Offline whole-utterance noise statistics are unavailable to any causal/streaming path.",
    "No device clock, memory, deadline, benchmark, provider or release result is produced.",
]

INDEPENDENT_TIMING_EVIDENCE = {
    "status": "source_reported_proposal_only",
    "measured_here": False,
    "target_device": False,
    "used_for_qualification": False,
    "sources": ["research/noise_suppression_pilot_20261027.md",
                "REALTIME_COMPONENT_CANDIDATES.md"],
    "reported": {
        "median_batch_rtf": 0.0124,
        "mean_adapter_seconds": 0.1250,
        "mean_worker_wall_seconds": 0.846,
        "scope": "30-pair exploratory DNS2020 subset, offline adapter, batch worker",
    },
    "note": "Source-reported batch timing is provenance only; it is not reproduced, pooled, assigned to the surrogate or used as an acceptance threshold.",
}

PRIOR_PILOT_PROVENANCE = {
    "status": "source_reported_not_reproduced",
    "measured_here": False,
    "used_for_qualification": False,
    "source": "research/noise_suppression_pilot_20261027.md",
    "cohort": "30 paired DNS2020 no-reverb synthetic engineering clips; not a frozen benchmark or representative sample",
    "reported": {
        "median_output_snr_db": 15.891,
        "median_snr_gain_db": 5.381,
        "mean_si_sdr_gain_db": 5.412,
        "median_stoi": 0.9484,
        "paired_snr_gain_db": {"mean": 5.4670, "median": 5.3814,
                               "ci95": [4.0863, 6.9354], "wins_ties_losses": [29, 0, 1]},
        "paired_si_sdr_gain_db": {"mean": 5.4124, "median": 5.2300,
                                  "ci95": [4.0401, 6.8695], "wins_ties_losses": [29, 0, 1]},
        "paired_stoi_delta": {"mean": 0.0078, "median": 0.0070,
                              "ci95": [-0.0011, 0.0165], "wins_ties_losses": [18, 0, 12]},
        "median_rtf": 0.0124,
        "official_dns3_dnsmos_p808_bak_sig_ovrl": [3.44, 3.90, 2.70],
    },
    "note": "Prior pilot and upstream table values are provenance only. They are not measured here, not pooled with this surrogate and not used to qualify the candidate.",
}

LICENSING_ANALYSIS = {
    "upstream_code_license": UPSTREAM_LICENSE,
    "upstream_code_license_pin": f"source:{UPSTREAM_SNAPSHOT}/LICENSE",
    "checkpoint_specific_terms_recorded": False,
    "checkpoint_license_text_present_in_ledger": False,
    "training_data_provenance_established": False,
    "training_eval_overlap_assessed": False,
    "runtime_redistribution_terms_established": False,
    "redistribution_clearance": False,
    "product_use_clearance": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "weight_and_runtime_rights_cleared",
}

RIGHTS_GAP = {
    "blocked": True,
    "exact_upstream_source_verified": True,
    "model_weight_terms_verified": False,
    "training_data_provenance_verified": False,
    "torch_redistribution_terms_verified": False,
    "evidence": "Only source-code MIT is pinned. The asset ledger records code_license for GTCRN-DNS3 but no separate model/checkpoint terms; DNS3 training-data provenance and evaluation overlap are unassessed.",
    "consequence": "No vendoring, build, installed provider, descriptor, default or release claim until checkpoint, runtime and training-data rights are cleared.",
}

EVIDENCE_CLASSES = [
    "synthetic_paired_metrics",
    "analytical_geometry_and_alignment",
    "pinned_source_inspection",
    "source_reported_prior_pilot_provenance",
    "deterministic_bytes_and_digests",
]


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


def _noise_magnitude(magnitudes: Sequence[Sequence[float]]) -> List[float]:
    count = len(magnitudes)
    energies = [math.fsum(value * value for value in frame) for frame in magnitudes]
    take = max(2, int(count * SURROGATE_PARAMETERS["noise_frame_fraction"]))
    order = sorted(range(count), key=lambda item: (energies[item], item))[:take]
    return [math.fsum(magnitudes[item][band] for item in order) / take
            for band in range(STFT_BINS)]


def _smooth_gains(gains: Sequence[Sequence[float]]) -> List[List[float]]:
    smoothed: List[List[float]] = []
    for frame in gains:
        row: List[float] = []
        for band in range(STFT_BINS):
            left = frame[band - 1] if band > 0 else frame[band]
            right = frame[band + 1] if band + 1 < STFT_BINS else frame[band]
            row.append((left + 2.0 * frame[band] + right) / 4.0)
        smoothed.append(row)
    return smoothed


def enhance_spectrum(frames: Sequence[Sequence[complex]]
                     ) -> Tuple[List[List[complex]], Dict[str, Any]]:
    magnitudes = [[abs(value) for value in frame] for frame in frames]
    noise = _noise_magnitude(magnitudes)
    raw_gains: List[List[float]] = []
    for frame in magnitudes:
        row: List[float] = []
        for band, value in enumerate(frame):
            if value <= 1e-12:
                row.append(0.0)
                continue
            ratio = noise[band] / value
            gain = math.sqrt(max(0.0, 1.0
                                 - SURROGATE_PARAMETERS["oversubtraction"] * ratio * ratio))
            row.append(min(1.0, max(SURROGATE_PARAMETERS["minimum_gain"], gain)))
        raw_gains.append(row)
    gains = _smooth_gains(raw_gains)
    shaped = [[frame[band] * gains[index][band] for band in range(STFT_BINS)]
              for index, frame in enumerate(frames)]
    return shaped, {
        "frames": len(frames),
        "stft_bins": STFT_BINS,
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
        return None, "rejected_asset_unavailable"
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
    """Strict offline admission; the real path fails closed without assets."""
    config = dict(CONFIG) if config is None else config
    admitted, status = validate_config(config)
    if admitted is None:
        return None, {"status": status, "mode": None, "samples": None,
                      "rejections": 1, "inference_executed": False,
                      "model_loaded": False, "runtime_invoked": False}
    values, signal_status = _validate_signal(waveform)
    if values is None:
        return None, {"status": signal_status, "mode": admitted["mode"],
                      "samples": None, "rejections": 1,
                      "inference_executed": False, "model_loaded": False,
                      "runtime_invoked": False}
    output, info = _transform(values, enhance=True)
    return output, {
        "status": "ok",
        "mode": admitted["mode"],
        "samples": len(output),
        "rejections": 0,
        "frames": info["frames"],
        "stft_padding_samples": PADDING_SAMPLES,
        "delay_compensation_samples": CONTENT_DELAY_SAMPLES,
        "source_time_mapping": "identity",
        "model_input_shape": [1, STFT_BINS, info["frames"], 2],
        "inference_executed": False,
        "model_loaded": False,
        "runtime_invoked": False,
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
            "note": "Established task-matched baseline is plain noisy input, not a GTCRN run.",
        },
        "candidate": {
            "name": "offline_whole_utterance_spectral_subtraction_surrogate",
            "status": "measured_synthetic",
            "metrics": scored(speech_target, speech_output),
            "note": "Synthetic surrogate only; not GTCRN and not a model inference.",
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
        ("not_a_dict", ["offline_surrogate", "caller_supplied_asset"]),
        ("missing_key", {"mode": SURROGATE_MODE}),
        ("extra_key", {"mode": SURROGATE_MODE, "asset": ASSET_REFERENCE, "x": 1}),
        ("real_mode_without_asset", {"mode": REAL_MODE, "asset": ASSET_REFERENCE}),
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
        "source_commit": UPSTREAM_COMMIT,
        "sample_rate": SAMPLE_RATE_HZ,
        "n_fft": N_FFT,
        "hop_samples": HOP_SAMPLES,
        "runtime": EXPECTED_RUNTIME_ID,
        "files": [dict(item) for item in EXPECTED_ASSET_FILES],
    }
    request.update(overrides)
    return request


def validate_asset_request(request: Any, *, asset_present: bool,
                           runtime_available: bool,
                           runtime_id: str = EXPECTED_RUNTIME_ID) -> Dict[str, Any]:
    """Declared caller-asset gate. It never opens, hashes or executes the asset."""
    def blocked(reason: str) -> Dict[str, Any]:
        return {"status": "blocked", "reason": reason,
                "inference_executed": False, "asset_opened": False}

    if not isinstance(request, dict) or set(request) != {
            "source_commit", "sample_rate", "n_fft", "hop_samples", "runtime", "files"}:
        return blocked("blocked_invalid_request")
    if request["source_commit"] != UPSTREAM_COMMIT:
        return blocked("blocked_wrong_commit")
    if (request["sample_rate"] != SAMPLE_RATE_HZ or request["n_fft"] != N_FFT
            or request["hop_samples"] != HOP_SAMPLES):
        return blocked("blocked_wrong_geometry")
    if request["runtime"] != runtime_id:
        return blocked("blocked_runtime_unavailable")
    files = request["files"]
    if not isinstance(files, list) or len(files) != len(EXPECTED_ASSET_FILES):
        return blocked("blocked_wrong_file_count")
    declared: Dict[str, Dict[str, Any]] = {}
    for item in files:
        if (not isinstance(item, dict) or set(item) != {"path", "bytes", "sha256"}
                or not isinstance(item["path"], str)):
            return blocked("blocked_invalid_request")
        if item["path"] in declared:
            return blocked("blocked_path_mismatch")
        declared[item["path"]] = item
    if set(declared) != set(EXPECTED_ASSET_PATHS):
        return blocked("blocked_path_mismatch")
    for expected in EXPECTED_ASSET_FILES:
        actual = declared[expected["path"]]
        if actual["bytes"] != expected["bytes"]:
            return blocked("blocked_size_mismatch")
        if actual["sha256"] != expected["sha256"]:
            return blocked("blocked_hash_mismatch")
    if not asset_present:
        return blocked("blocked_asset_absent")
    if not runtime_available:
        return blocked("blocked_runtime_unavailable")
    return {"status": "ready_for_caller_execution",
            "reason": "caller_asset_and_runtime_ready",
            "inference_executed": False, "asset_opened": False}


def asset_gate() -> Dict[str, Any]:
    return {
        "status": "blocked",
        "asset_present_in_sdk_worktree": False,
        "asset_present_in_research_checkout": True,
        "asset_loaded_or_hashed_by_package": False,
        "asset_files": [dict(item) for item in EXPECTED_ASSET_FILES],
        "source_commit": UPSTREAM_COMMIT,
        "runtime": EXPECTED_RUNTIME,
        "runtime_available": False,
        "torch_importable_in_evidence_interpreter": False,
        "inference_executed": False,
        "real_path_status": "rejected_asset_unavailable",
        "validation_asset_absent": validate_asset_request(
            _asset_request(), asset_present=False, runtime_available=False),
        "validation_runtime_unavailable": validate_asset_request(
            _asset_request(), asset_present=True, runtime_available=False),
        "positive_control": validate_asset_request(
            _asset_request(), asset_present=True, runtime_available=True),
        "note": "The external research checkout is listed by the pinned ledger but was not read, loaded or redistributed here. The real path never falls back to the surrogate.",
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
        "hash_mismatch": validate_asset_request(
            _asset_request(files=[
                dict(EXPECTED_ASSET_FILES[0]),
                {**EXPECTED_ASSET_FILES[1], "sha256": "0" * 64}]),
            asset_present=True, runtime_available=False),
        "size_mismatch": validate_asset_request(
            _asset_request(files=[
                dict(EXPECTED_ASSET_FILES[0]),
                {**EXPECTED_ASSET_FILES[1], "bytes": 1}]),
            asset_present=True, runtime_available=False),
        "wrong_commit": validate_asset_request(
            _asset_request(source_commit="0" * 40),
            asset_present=True, runtime_available=False),
        "wrong_geometry": validate_asset_request(
            _asset_request(hop_samples=128),
            asset_present=True, runtime_available=False),
        "one_file": validate_asset_request(
            _asset_request(files=[dict(EXPECTED_ASSET_FILES[0])]),
            asset_present=True, runtime_available=False),
        "unknown_key": validate_asset_request(
            {**_asset_request(), "extra": 1},
            asset_present=True, runtime_available=False),
        "wrong_runtime": validate_asset_request(
            _asset_request(runtime="onnxruntime-1.20.1"),
            asset_present=True, runtime_available=False),
        "runtime_unavailable": validate_asset_request(
            _asset_request(), asset_present=True, runtime_available=False),
    }
    all_rejected = (
        all(item["status"].startswith("rejected")
            for item in config_rejections.values())
        and config_rejections["real_mode_without_asset"]["status"]
            == "rejected_asset_unavailable"
        and all(item["status"].startswith("rejected")
                for item in signal_rejections.values())
        and all(item["status"] == "blocked" for item in gate_cases.values())
        and valid_run["status"] == "ok")
    return {
        "config_rejections": config_rejections,
        "signal_rejections": signal_rejections,
        "lifecycle": {
            "valid_run": valid_run["status"],
            "real_mode": config_rejections["real_mode_without_asset"]["status"],
        },
        "asset_gate": gate_cases,
        "asset_gate_control": validate_asset_request(
            _asset_request(), asset_present=True, runtime_available=True),
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
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_license": UPSTREAM_LICENSE,
        "upstream_license_copyright": UPSTREAM_LICENSE_COPYRIGHT,
        "upstream_license_pin": f"source:{UPSTREAM_SNAPSHOT}/LICENSE",
        "upstream_adapter_identity": UPSTREAM_ADAPTER_IDENTITY,
        "source_file": {
            "path": EXPECTED_ASSET_FILES[0]["path"],
            "bytes": EXPECTED_ASSET_FILES[0]["bytes"],
            "sha256": EXPECTED_ASSET_FILES[0]["sha256"],
            "present_in_sdk_worktree": False,
            "present_in_research_checkout": True,
            "loaded_or_executed": False,
        },
        "checkpoint": {
            "path": EXPECTED_ASSET_FILES[1]["path"],
            "bytes": EXPECTED_ASSET_FILES[1]["bytes"],
            "sha256": EXPECTED_ASSET_FILES[1]["sha256"],
            "present_in_sdk_worktree": False,
            "present_in_research_checkout": True,
            "loaded_or_executed": False,
            "license_terms": "not_separately_recorded",
        },
        "runtime_lock": {
            "path": "adapters/gtcrn/requirements.lock",
            "sha256": SOURCE_PINS["source:adapters/gtcrn/requirements.lock"],
            "id": EXPECTED_RUNTIME_ID,
            "installed_in_sdk_worktree": False,
        },
        "adapter_contract": {
            "path": "adapters/gtcrn/run.py",
            "sha256": SOURCE_PINS["source:adapters/gtcrn/run.py"],
            "entrypoint": ["python", "adapters/gtcrn/run.py"],
            "mode": "offline",
            "tasks": ["CLN-01"],
            "identity": UPSTREAM_ADAPTER_IDENTITY,
        },
        "note": "Pins are copied from the pinned asset ledger and source manifest. The package does not read, hash or load the model weight or source checkpoint.",
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
                "reason": "analytical identity mapping and zero offline delay; no measured timing or memory"},
        },
        "remaining_gates": list(GATE_NAMES),
    }


def readiness() -> Dict[str, Any]:
    return {
        "status": "blocked",
        "conclusion": "not_ready",
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "asset_available": False,
        "runtime_available": False,
        "rights_cleared": False,
        "synthetic_surrogate_only": True,
        "no_missing_result_qualifies_candidate": True,
        "exact_external_blocker": (
            "No rights-cleared caller-supplied GTCRN DNS3 asset and no pinned CPython 3.10 "
            "torch 1.13.1 runtime are available to this task; checkpoint terms, DNS3 "
            "training-data provenance/overlap and redistribution/product clearance are "
            "unestablished, and torch is not importable in the pinned CPython 3.12.16 "
            "evidence interpreter."
        ),
        "reopen_condition": (
            "An authorized caller supplies both immutable hash-pinned assets with a "
            "recorded SHA-256, byte size and checkpoint-specific terms, installs the pinned "
            "CPython 3.10 torch 1.13.1 runtime in an approved isolated runner, and records "
            "positive training-data/redistribution/product legal clearance; only then rerun "
            "real offline parity, a held-out real paired denoising cohort, independent "
            "listening or a separately labeled predictive screen, and target-runtime "
            "timing/memory before provider intake."
        ),
        "next_action": "Obtain the exact rights-cleared assets and pinned runtime; do not register, expose or select this component.",
    }


def gates() -> List[Dict[str, str]]:
    return [{"name": name, "status": "blocked", "reopen_condition": GATE_REOPEN[name]}
            for name in GATE_NAMES]


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
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "model_geometry": dict(MODEL_GEOMETRY),
        "asset_boundary": {
            "mode": "caller_supplied_asset_reference",
            "expected_root": "caller_supplied/GTCRN",
            "expected_files": [dict(item) for item in EXPECTED_ASSET_FILES],
            "source_commit": UPSTREAM_COMMIT,
            "asset_present": False,
            "asset_loaded_or_hashed": False,
            "asset_rights_verified": False,
            "runtime_available": False,
            "torch_invoked": False,
            "real_path_status": "rejected_asset_unavailable",
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
        "asset_pins": dict(ASSET_PINS),
        "artifact_pins": report_artifact_pins(),
        "contract_sha256": sha256(contract_bytes()),
        "acceptance_profile": acceptance_profile(),
        "conditions": condition_map,
        "controls": controls(),
        "identity_reconstruction": identity_reconstruction(),
        "adverse": adverse(),
        "regressions": regressions(condition_map),
        "independent_timing_evidence": dict(INDEPENDENT_TIMING_EVIDENCE),
        "prior_pilot_provenance": dict(PRIOR_PILOT_PROVENANCE),
        "readiness": readiness(),
        "rights_gap": dict(RIGHTS_GAP),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "model_provenance": model_provenance(),
        "caller_supplied_asset_gate": asset_gate(),
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


def adapter() -> Dict[str, Any]:
    return {
        "adapter_id": ADAPTER_ID,
        "asset_contract": "caller_supplied_asset",
        "asset_present": False,
        "c_public_boundary": "not_used",
        "channels": CHANNELS,
        "component_id": COMPONENT_ID,
        "configuration_keys": ["mode", "asset"],
        "configuration_values": dict(CONFIG),
        "content_delay_samples": CONTENT_DELAY_SAMPLES,
        "content_delay_status": "analytical_offline_alignment_only",
        "controls": ["identity_no_processing", "noisy_input_no_processing",
                     "offline_whole_utterance_spectral_subtraction_surrogate"],
        "decision": DECISION,
        "default_enabled": False,
        "enabled_by_default": False,
        "entrypoint": ["python3", f"{TASK_REL}/run.py", "--all"],
        "evaluation_path": "task_local_python_offline_surrogate",
        "hop_ms": HOP_MS,
        "hop_samples": HOP_SAMPLES,
        "input_kind": "waveform_utterance",
        "input_shape": "[N]",
        "installed_v0_note": "installed v0 stays 16 kHz mono f32 at 160 samples per frame and is unchanged",
        "modes": [SURROGATE_MODE, REAL_MODE],
        "model_input_shape": "[1,257,T,2]",
        "n_fft": N_FFT,
        "output_kind": "waveform_utterance",
        "output_shape": "[N]",
        "processor_exposure": False,
        "production_callback_path": "not_implemented",
        "protocol_version": 1,
        "real_asset_required": True,
        "real_runtime_invoked": False,
        "realtime_v0_provider": False,
        "reference_family": REFERENCE_FAMILY,
        "registered": False,
        "registration": "unregistered-developer-only",
        "sample_format": "f32",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "source_identity": "adapters/gtcrn/run.py",
        "source_sha256": SOURCE_PINS["source:adapters/gtcrn/run.py"],
        "stft_bins": STFT_BINS,
        "task": TASK_ID,
        "window_samples": WINDOW_SAMPLES,
    }


def provider() -> Dict[str, Any]:
    return {
        "asset_dependency": True,
        "asset_present": False,
        "c_boundary_included": False,
        "c_provider": False,
        "decision": DECISION,
        "default_enabled": False,
        "default_selected": False,
        "descriptor_settings": {},
        "enabled_by_default": False,
        "identity": "gtcrn-dns3-offline-synthetic-provider/0.1",
        "input_kind": "waveform_utterance",
        "installed_v0_behavior_changed": False,
        "manifest": "task-local-only",
        "model_input_shape": "[1,257,T,2]",
        "opt_in_required": True,
        "processor_exposure": False,
        "public_api_abi_changed": False,
        "purpose": "documents an opt-in, unregistered, disabled-by-default caller-supplied-asset offline boundary and synthetic surrogate; never selected by the SDK registry, defaults, build or installed behavior",
        "real_model_weights": False,
        "reference_family": REFERENCE_FAMILY,
        "registered": False,
        "runtime_dependency": EXPECTED_RUNTIME_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "schema_id": f"audio-sdk/{SLUG}/provider/0.1",
        "torch_runtime_invoked": False,
        "vendor_runtime_invoked": False,
    }


def asset() -> Dict[str, Any]:
    return {
        "asset_id": "gtcrn-dns3-offline-caller-supplied-asset-v0",
        "asset_present": False,
        "assets": [dict(item) for item in EXPECTED_ASSET_FILES],
        "contract": "caller_supplied_asset_reference",
        "expected_root": "caller_supplied/GTCRN",
        "license": "unverified_absent",
        "model_license_terms_recorded": False,
        "note": "No weight or source file is present, downloaded, vendored or redistributed. The caller must supply both pinned files with an immutable URI and a recorded SHA-256 before the real path may run.",
        "real_path_status": "rejected_asset_unavailable",
        "runtime": dict(EXPECTED_RUNTIME),
        "silent_fallback_to_surrogate": False,
        "source_commit": UPSTREAM_COMMIT,
        "source_uri": UPSTREAM_REPOSITORY,
        "task": TASK_ID,
        "unverified": True,
    }


def base_artifact_pins() -> Dict[str, str]:
    return {
        f"{TASK_REL}/adapter.json": sha256(canonical_bytes(adapter()) + b"\n"),
        f"{TASK_REL}/provider.json": sha256(canonical_bytes(provider()) + b"\n"),
        f"{TASK_REL}/asset.json": sha256(canonical_bytes(asset()) + b"\n"),
        f"{TASK_REL}/scorer.py": sha256((HERE / "scorer.py").read_bytes()),
    }


def report_artifact_pins() -> Dict[str, str]:
    pins = base_artifact_pins()
    pins[f"{TASK_REL}/contract.json"] = sha256(contract_bytes())
    return pins


def contract() -> Dict[str, Any]:
    return {
        "schema_id": f"audio-sdk/task-evidence/{SLUG}/contract/0.1",
        "contract_version": "0.1",
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT_ID,
        "repository": "audio-sdk",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "verification_profile": PROFILE,
        "reference_family": REFERENCE_FAMILY,
        "adapter_id": ADAPTER_ID,
        "scope": "Deterministic synthetic offline fixture at the documented GTCRN DNS3 PyTorch offline boundary with a caller-supplied-asset reference; no selection, real-model, device, listening, benchmark, provider or release claim.",
        "source_identity": {
            "path": "adapters/gtcrn/run.py",
            "sha256": SOURCE_PINS["source:adapters/gtcrn/run.py"],
            "upstream_commit": UPSTREAM_COMMIT,
            "upstream_repository": UPSTREAM_REPOSITORY,
            "documented_constraints": [
                "offline mode only; waveform input at 16 kHz mono f32",
                "configuration must pin model_dir, model_files, sample_rate, n_fft=512 and hop_size=256",
                "request must pin gtcrn.py and checkpoints/model_trained_on_dns3.tar by SHA-256",
                "torch.stft with n_fft=512, hop=256, win_length=512, sqrt periodic Hann and centered framing",
                "model GTCRN().eval() loaded from checkpoint key 'model'",
                "torch.istft with length equal to the input sample count and identity source mapping",
                "wrong rate, channels, nonfinite samples or invalid length raise",
                "the adapter explicitly does not claim streaming support",
            ],
            "note": "Source inspection is a boundary anchor only. No torch runtime, checkpoint or model weight is loaded here.",
        },
        "frontend_contract": dict(FORMAT),
        "model_geometry": dict(MODEL_GEOMETRY),
        "asset_boundary": {
            "mode": "caller_supplied_asset_reference",
            "expected_root": "caller_supplied/GTCRN",
            "expected_files": [dict(item) for item in EXPECTED_ASSET_FILES],
            "asset_present": False,
            "asset_rights_verified": False,
            "runtime_available": False,
            "torch_invoked": False,
            "real_path_status": "rejected_asset_unavailable",
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
                         "offline_whole_utterance_spectral_subtraction_surrogate"],
            "candidate": "offline_whole_utterance_spectral_subtraction_surrogate",
            "control": "noisy_input_no_processing",
            "configuration_keys": ["mode", "asset"],
            "configuration_value": dict(CONFIG),
            "signal_samples": SIGNAL_SAMPLES,
            "causal": False,
            "model_weights": False,
            "downloads": False,
            "real_speech": False,
            "licensed_runtime": False,
            "torch_invoked": False,
            "device_or_timing_claim": False,
            "registered_in_bench": False,
            "produces_bench_bundle": False,
            "opt_in_manifest": "provider.json",
            "default_enabled": False,
        },
        "source_pins": {path.split(":", 1)[1]: digest
                        for path, digest in SOURCE_PINS.items()},
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_pins": dict(ASSET_PINS),
        "artifact_pins": base_artifact_pins(),
        "acceptance_profile": acceptance_profile(),
        "independent_timing_evidence": dict(INDEPENDENT_TIMING_EVIDENCE),
        "prior_pilot_provenance": dict(PRIOR_PILOT_PROVENANCE),
        "rights_gap": dict(RIGHTS_GAP),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "model_provenance": model_provenance(),
        "exact_blockers": list(EXACT_BLOCKERS),
        "gates": list(GATE_NAMES),
        "invariants": [
            "Only this task directory is written; no shared SDK file, CMake, contract, public header, registry, default, board, handoff or CI file changes.",
            "The fixture is opt-in, unregistered and disabled by default with no C provider or production callback.",
            "The caller-supplied-asset path fails closed and never silently falls back to the surrogate.",
            "All signals are frozen deterministic synthetic floats; no model, media, weight or runtime asset is read or produced.",
            "Configuration, signal, geometry and caller-supplied-asset rejection cases fail closed without producing output.",
            "Identity and noisy-input controls are reported with the candidate; regressions are recorded verbatim.",
            "Three cold-start passes are byte-identical; canonical JSON and digest sidecars are regenerated deterministically.",
            "Prior pilot metrics and source-reported timing are provenance only, never measured results or thresholds.",
            "Missing evidence never qualifies the candidate; decision remains DEFER and conclusion not_ready.",
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
    "adapter.json",
    "provider.json",
    "asset.json",
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
              "other paths are SDK-worktree-relative. Lines are <sha256>  <path>.\n")
    return (header + "\n".join(lines) + "\n").encode("utf-8")


def interpreter_is_pinned() -> bool:
    return sys_version() == EVIDENCE_INTERPRETER


def sys_version() -> str:
    import platform
    return platform.python_version()
