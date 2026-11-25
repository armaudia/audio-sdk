# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-01.

This module builds a bounded taxonomy/comparison evidence map for the
cleaning/restoration category (inventory category ``CLN-01``). It reads only
pinned, read-only documents from the enclosing ``audioml`` workspace and the
SDK worktree. It does not load audio, weights, runtimes, media or the network,
and it does not register, expose, enable or qualify any processor.

All curated records below are documentation mappings, not new measurements.
Historical local or source-reported values are transcribed verbatim from the
pinned documents and labelled with their original scope.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-CLN-01"
TITLE = "Review coverage for Background noise suppression"
CATEGORY_ID = "CLN-01"
LEGACY_FAMILY = "F01"
BRANCH = "swarm/SDK-SURVEY-CLN-01"
BASE_COMMIT = "c9296ae96a2b58efae559bd22e7760122c886df8"
PROFILE = "Enhancement"
COMPONENT = "background-noise-suppression-evidence-map"
STATUS = "proposal_only_survey_incomplete"
QUALIFICATION_STATUS = "not_qualified"
READINESS = "incomplete"
DECISION = "DEFER"

LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-" + "Identifier: Apache-2.0\n"
)

# Workspace-relative document pins. Every entry is a read-only document or
# metadata ledger consulted by this survey; a pin never grants rights or
# verifies media/weights that are not present in this task directory.
SOURCE_PINS: Dict[str, str] = {
    "REALTIME_COMPONENT_CANDIDATES.md": "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/clean_speech_diagnostics_20261027.md": "c0b39bc33e2a5d9c7ca6a48a1f778de79c7c3e0a52b047beeaa43b09d5253460",
    "research/dereverberation_candidates_20261028.md": "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "research/distortion_restoration_20261028.md": "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "research/evidence/pilot-discovery-20261027/source.txt": "3591d17581fb9c9168f10d3816f42a9c6178d6168ea386de6eafc6280c18c590",
    "research/noise_suppression_assets_20261027.json": "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/noise_suppression_pilot_20261027.md": "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# SDK-worktree-relative public-boundary pins. They are read only to prove that
# no public surface was touched; no header is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/quality-impairment-taxonomy/README.md": "77ad10fae3e41a06adad6cee377616c73dd8d7d458a76c9297aa55d837afcbe5",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Acoustic cleanup and spatial processing",
    "name": "Background noise suppression",
    "scope": "requested",
    "output_kind": "waveform",
    "purpose": "Reduce additive noise while preserving wanted speech.",
    "method_families": {
        "classic": "Spectral subtraction; Wiener filtering; subspace methods",
        "ml": "Band-gain networks; complex masks; deep filtering; neural restoration",
    },
    "input_output": "Mono or multichannel audio \u2192 enhanced waveform",
    "live_or_comparison_boundary": (
        "Separate stationary noise, changing noise, and competing speech scenarios; "
        "current speed is not an admission gate."
    ),
    "source_ids": ["S16", "S17", "S18"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S16",
        "title": "Pyroomacoustics classical denoising implementations",
        "url": "https://pyroomacoustics.readthedocs.io/en/stable/pyroomacoustics.denoise.html",
        "access_scope": "direct",
        "mapped_components": ["classical-spectral-subtraction", "classical-wiener-denoising"],
        "gap_ids": ["G02"],
        "finding": (
            "Registry names spectral subtraction, Wiener filtering and subspace methods. "
            "The 30-pair DNS pilot executed spectral subtraction and Wiener locally; "
            "the tested noise estimates used the whole clip and are noncausal. No local "
            "subspace-method execution or exact pinned revision of the S16 URL was found."
        ),
    },
    {
        "source_id": "S17",
        "title": "RNNoise implementation",
        "url": "https://github.com/xiph/rnnoise",
        "access_scope": "search excerpt; also inspected in prior brainstorm searches",
        "mapped_components": ["rnnoise-v0-2", "rnnoise-speech-probability"],
        "gap_ids": ["G03"],
        "finding": (
            "Pilot ΔSI-SDR +3.139 dB and ΔSTOI +0.0215 on 30 synthetic pairs; clean-input "
            "distortion SNR median 17.32 dB. Worker RTF 0.0662 covers "
            "rnnoise_process_frame only, excluding resampling/setup/I/O. The local adapter "
            "is offline at 48 kHz; no 16 kHz frame-causal native path was executed here."
        ),
    },
    {
        "source_id": "S18",
        "title": "DeepFilterNet implementation",
        "url": "https://github.com/Rikorose/DeepFilterNet",
        "access_scope": "direct in prior brainstorm",
        "mapped_components": ["deepfilternet3-v0-5-6"],
        "gap_ids": ["G04"],
        "finding": (
            "Pilot ΔSI-SDR +6.660 dB and ΔSTOI +0.0258 on the 30-pair synthetic cohort; "
            "743-item EARS DNSMOS predictions favored it on SIG/BAK/OVL but are not human "
            "MOS. Exact checkpoint terms remain unresolved and the board row is blocked."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Spectral subtraction",
        "components": ["classical-spectral-subtraction"],
        "gap_ids": ["G01"],
        "status": "historical_local_synthetic_only",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Wiener filtering",
        "components": ["classical-wiener-denoising"],
        "gap_ids": ["G01"],
        "status": "historical_local_synthetic_only",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Subspace methods",
        "components": [],
        "gap_ids": ["G02"],
        "status": "no_mapped_component_or_local_execution",
    },
    {
        "family_id": "MF-C4",
        "branch": "classic",
        "family": "Conventional baselines (SpeexDSP NS, WebRTC APM NS, FFmpeg afftdn/afwtdn)",
        "components": [
            "speexdsp-ns-reference",
            "webrtc-apm-ns",
            "ffmpeg-afwtdn",
        ],
        "gap_ids": ["G09"],
        "status": "historical_local_synthetic_only",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Band-gain networks (FastEnhancer family)",
        "components": [
            "fastenhancer-tiny-reference",
            "fastenhancer-small-reference",
            "fastenhancer-source-linked-onnx-wrapper",
        ],
        "gap_ids": ["G05"],
        "status": "historical_local_synthetic_only",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Complex masks / complex-domain filtering (DeepFilterNet3, GTCRN, CMGAN)",
        "components": ["deepfilternet3-v0-5-6", "gtcrn-dns3-offline", "cmgan"],
        "gap_ids": ["G04", "G06"],
        "status": "historical_local_and_cited",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Deep filtering / recurrent masking (DPFN, DPCRN, DTLN)",
        "components": [
            "dpdfnet-baseline-offline",
            "dpdfnet-baseline-streaming",
            "dtln-onnx",
        ],
        "gap_ids": ["G06"],
        "status": "historical_local_synthetic_only",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "Neural restoration / generative postfilters",
        "components": ["speechbrain-sgmse-voicebank"],
        "gap_ids": ["G07"],
        "status": "no_local_execution_in_reviewed_records",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "classical-spectral-subtraction", "evidence_status": "evaluated", "task": "SDK-CLASSICAL-SPECTRAL-SUBTRACTION"},
    {"component_id": "classical-wiener-denoising", "evidence_status": "evaluated", "task": "SDK-CLASSICAL-WIENER-DENOISING"},
    {"component_id": "speexdsp-ns-reference", "evidence_status": "integrated", "task": "SDK-SPEEXDSP-NS-REFERENCE"},
    {"component_id": "webrtc-apm-ns", "evidence_status": "evaluated", "task": "SDK-WEBRTC-APM-NS"},
    {"component_id": "ffmpeg-afwtdn", "evidence_status": "evaluated", "task": "SDK-FFMPEG-AFWTDN"},
    {"component_id": "rnnoise-v0-2", "evidence_status": "evaluated", "task": "SDK-RNNOISE-V0-2"},
    {"component_id": "rnnoise-speech-probability", "evidence_status": "partial", "task": "SDK-RNNOISE-SPEECH-PROBABILITY"},
    {"component_id": "deepfilternet3-v0-5-6", "evidence_status": "evaluated", "task": "SDK-DEEPFILTERNET3-V0-5-6"},
    {"component_id": "gtcrn-dns3-offline", "evidence_status": "evaluated", "task": "SDK-GTCRN-DNS3-OFFLINE"},
    {"component_id": "cmgan", "evidence_status": "blocked", "task": "SDK-CMGAN"},
    {"component_id": "fastenhancer-tiny-reference", "evidence_status": "evaluated", "task": "SDK-FASTENHANCER-TINY-REFERENCE"},
    {"component_id": "fastenhancer-small-reference", "evidence_status": "evaluated", "task": "SDK-FASTENHANCER-SMALL-REFERENCE"},
    {"component_id": "fastenhancer-source-linked-onnx-wrapper", "evidence_status": "source-local", "task": "SDK-FASTENHANCER-SOURCE-LINKED-ONNX-WRAPPER"},
    {"component_id": "dpdfnet-baseline-offline", "evidence_status": "evaluated", "task": "SDK-DPDFNET-BASELINE-OFFLINE"},
    {"component_id": "dpdfnet-baseline-streaming", "evidence_status": "evaluated", "task": "SDK-DPDFNET-BASELINE-STREAMING"},
    {"component_id": "dtln-onnx", "evidence_status": "evaluated", "task": "SDK-DTLN-ONNX"},
    {"component_id": "speechbrain-sgmse-voicebank", "evidence_status": "considered", "task": "SDK-SPEECHBRAIN-SGMSE-VOICEBANK"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "30 paired DNS2020 no-reverb synthetic clips (engineering subset)",
        "class": "historical_local_paired_synthetic",
        "source_pin": "research/noise_suppression_pilot_20261027.md",
        "boundary": "Not a frozen benchmark and not a representative sample.",
    },
    {
        "id": "CI-2",
        "input": "Same 30 clean references passed through each candidate as if noisy",
        "class": "historical_local_clean_preservation_diagnostic",
        "source_pin": "research/clean_speech_diagnostics_20261027.md",
        "boundary": "Distortion diagnostic only; not a recognition or listening result.",
    },
    {
        "id": "CI-3",
        "input": "743 unpaired EARS inputs with saved FastEnhancer/DeepFilterNet3 outputs",
        "class": "historical_local_unpaired_predictive",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "boundary": "DNSMOS predictions, not human MOS; EARS CC BY-NC not cleared here.",
    },
    {
        "id": "CI-4",
        "input": "VCTK v3 +5 dB pink-noise prepared listening comparison",
        "class": "prepared_only_no_ratings",
        "source_pin": "docs/task-evidence/quality-impairment-taxonomy/README.md",
        "boundary": "Privacy/publicity and artifact provenance unresolved; prepared items are not collected ratings.",
    },
    {
        "id": "CI-5",
        "input": "Vendor or source-reported denoiser claims",
        "class": "source_reported_only",
        "source_pin": "research/category_registry.json",
        "boundary": "No local runtime, matched cohort or numeric parity follows from a claim.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "identity / noisy input", "role": "Paired baseline for noisy mixtures.", "source_pin": "research/noise_suppression_pilot_20261027.md"},
    {"id": "CT-2", "name": "clean speech as input", "role": "Clean-preservation distortion diagnostic.", "source_pin": "research/clean_speech_diagnostics_20261027.md"},
    {"id": "CT-3", "name": "spectral subtraction and Wiener", "role": "Classical task-matched baselines; noncausal whole-clip noise estimate.", "source_pin": "REALTIME_COMPONENT_CANDIDATES.md"},
    {"id": "CT-4", "name": "SpeexDSP NS / WebRTC APM NS levels 0-3", "role": "Conventional strengths compared on the same pilot.", "source_pin": "research/noise_suppression_pilot_20261027.md"},
    {"id": "CT-5", "name": "ROSE-CD input-RMS-matched", "role": "Separates level change from SI-SDR change on one candidate.", "source_pin": "research/noise_suppression_pilot_20261027.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "DNS2020 no-reverb 30-pair engineering subset",
        "class": "research_audio",
        "status": "described_in_pinned_report; bytes not present or verified in this task",
        "source_pin": "research/noise_suppression_pilot_20261027.md",
    },
    {
        "asset": "EARS blind archive (743 inputs and enhancer outputs)",
        "class": "research_audio",
        "status": "CC BY-NC in cited records; no redistribution or listening clearance here",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
    },
    {
        "asset": "VCTK v3 prepared listening items",
        "class": "research_audio",
        "status": "prepared only; no ratings and no playback clearance",
        "source_pin": "docs/task-evidence/quality-impairment-taxonomy/README.md",
    },
    {
        "asset": "Candidate code/model manifests and digests",
        "class": "metadata_only",
        "status": "hashes transcribed from research/noise_suppression_assets_20261027.json; no weight bytes loaded",
        "source_pin": "research/noise_suppression_assets_20261027.json",
    },
    {
        "asset": "FFmpeg 7.1 afftdn/afwtdn binaries",
        "class": "external_tool",
        "status": "source-reported GPL provenance; no binary or invocation in this task",
        "source_pin": "research/noise_suppression_pilot_20261027.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "DNS2020 no-reverb 30-pair screen",
        "outcome_class": "historical_local_synthetic",
        "source_pin": "research/noise_suppression_pilot_20261027.md",
        "values": {
            "spectral_subtraction_mean_delta_si_sdr_db": 1.3068,
            "wiener_mean_delta_si_sdr_db": 0.4269,
            "speexdsp_mean_delta_si_sdr_db": 1.0608,
            "rnnoise_mean_delta_si_sdr_db": 3.1387,
            "deepfilternet3_mean_delta_si_sdr_db": 6.6596,
            "fastenhancer_small_mean_delta_si_sdr_db": 8.1120,
            "ffmpeg_afwtdn_mean_delta_si_sdr_db": -2.2115,
        },
        "scope": "Transcribed from the pinned report; not rerun by this survey and not a qualification.",
    },
    {
        "id": "HE-2",
        "label": "Clean-speech-as-input preservation diagnostic",
        "outcome_class": "historical_local_synthetic",
        "source_pin": "research/clean_speech_diagnostics_20261027.md",
        "values": {
            "wiener_median_clean_distortion_snr_db": 50.58,
            "spectral_subtraction_median_clean_distortion_snr_db": 38.42,
            "fastenhancer_small_median_clean_distortion_snr_db": 38.53,
            "ffmpeg_afftdn_median_clean_distortion_snr_db": -2.95,
        },
        "scope": "Same 30 clean references; intrusive diagnostic only, no blinded listening.",
    },
    {
        "id": "HE-3",
        "label": "743-item EARS DNSMOS predictive screen",
        "outcome_class": "historical_local_unpaired_predictive",
        "source_pin": "docs/task-evidence/quality-impairment-taxonomy/README.md",
        "values": {
            "deepfilternet3_predicted_sigma_delta": -0.063,
            "deepfilternet3_predicted_ovl_delta": 0.386,
        },
        "scope": "Predictions on unpaired speech; Unicode minus in the source is transcribed as ASCII; no clean references, no human MOS and no rights transfer.",
    },
    {
        "id": "HE-4",
        "label": "WebRTC APM NS strength sweep",
        "outcome_class": "historical_local_synthetic",
        "source_pin": "research/noise_suppression_pilot_20261027.md",
        "values": {
            "level0_mean_delta_stoi": -0.0056,
            "level1_mean_delta_stoi": -0.0202,
            "level2_mean_delta_stoi": -0.0360,
            "level3_mean_delta_stoi": -0.0466,
        },
        "scope": "Stronger settings increased distortion on this cohort; not a device or listening result.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "Vendor noise-cancellation quality and WER claims",
        "class": "source_reported",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "boundary": "No local vendor runtime, matched cohort or head-to-head result is created here.",
    },
    {
        "id": "RO-2",
        "claim": "Historical CPU/wall/RTF values for candidate adapters",
        "class": "source_reported_runtime_context",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "boundary": "Batch/worker timing under contention is not callback availability or target-device timing.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "identity_control": "CT-1; historical local 30-pair synthetic only",
        "matched_noisy_baseline": "CT-1; noisy input no processing",
        "classical_task_matched_baseline": "CT-3; spectral subtraction and Wiener",
        "paired_si_sdr_and_stoi": "HE-1; pinned report values, not rerun",
        "clean_speech_preservation": "HE-2; clean-input diagnostic only",
        "peaks_and_invalid_outputs": "HE-2 records clipped-sample fractions; no new invalid-output run",
        "unpaired_predictive_screen": "HE-3; DNSMOS predictions only",
        "listening": "CI-4 prepared only; no ratings",
        "alignment_state_memory_timing": "Adapter lag and batch RTF transcribed as context, not measured here",
    },
    "blocked": [
        "Rights-qualified real paired cohort with frozen candidate outputs",
        "Independent authorized listening with declared analysis plan",
        "Exact target-runtime content/availability timing, memory and deadline evidence",
        "Task-matched external baseline under a locked runtime",
        "Independent provider intake and exact-head review",
        "Explicit public default selection approval",
        "Exact approved reference parity at frozen revision and settings",
    ],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Frame-causal noise estimation for spectral subtraction and Wiener filtering",
        "evidence_gap": "Only whole-clip noncausal noise estimates were screened locally.",
        "follow_up_ids": ["SDK-SOX-NOISERED"],
        "feasibility_task_exists": True,
        "owner_note": "SDK-CLASSICAL-SPECTRAL-SUBTRACTION and SDK-CLASSICAL-WIENER-DENOISING own the existing classical references.",
    },
    {
        "id": "G02",
        "actionable_gap": "Validate the S16 subspace-method family with a pinned source and frozen controls",
        "evidence_gap": "No mapped component, exact pinned revision or local execution was found for subspace denoising.",
        "follow_up_ids": ["SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS", "SDK-SOX-NOISERED"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner existed at inspection; these are existing board tasks, not newly filed work.",
    },
    {
        "id": "G03",
        "actionable_gap": "Frame-causal 16 kHz native RNNoise path and quantized optional runtime",
        "evidence_gap": "Local adapter is offline at 48 kHz; measured RTF excludes resampling/setup/I/O.",
        "follow_up_ids": ["SDK-RNNOISE-INT8-ARM-ML-MODEL-ZOO"],
        "feasibility_task_exists": True,
        "owner_note": "SDK-RNNOISE-V0-2 is an implementation row; the ARM INT8 row is the existing feasibility follow-up.",
    },
    {
        "id": "G04",
        "actionable_gap": "Resolve DeepFilterNet source/checkpoint rights and scope successor variants",
        "evidence_gap": "Blocked implementation row; exact checkpoint terms unresolved despite local pilot scores.",
        "follow_up_ids": ["SDK-DEEPFILTERGAN"],
        "feasibility_task_exists": True,
        "owner_note": "SDK-DEEPFILTERNET3-V0-5-6 is blocked; no rights conclusion is produced by this survey.",
    },
    {
        "id": "G05",
        "actionable_gap": "Exact pinned FastEnhancer Base/Medium/Large checkpoints and streaming boundaries",
        "evidence_gap": "Only Tiny and Small were scored on the pilot; larger variants remain considered rows.",
        "follow_up_ids": [
            "SDK-FASTENHANCER-BASE-REFERENCE",
            "SDK-FASTENHANCER-MEDIUM-REFERENCE",
            "SDK-FASTENHANCER-LARGE-REFERENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "Existing feasibility rows; no weights or runtime are resolved here.",
    },
    {
        "id": "G06",
        "actionable_gap": "Complex-mask and TFLite/LiteRT streaming paths under a frozen runtime",
        "evidence_gap": "CMGAN is blocked; DPCRN TFLite and GTCRN streaming remain unmapped to local runtime evidence.",
        "follow_up_ids": ["SDK-CMGAN-LITERT-COMMUNITY-PORT", "SDK-DPCRN-DNS3-TFLITE"],
        "feasibility_task_exists": True,
        "owner_note": "SDK-GTCRN-STREAMING-ONNX is an implementation row, not a substitute for these feasibility gates.",
    },
    {
        "id": "G07",
        "actionable_gap": "Neural restoration / diffusion-family feasibility with scoped assets",
        "evidence_gap": "Family is named in the registry but no local execution or rights-cleared asset was found.",
        "follow_up_ids": [
            "SDK-SPEECHBRAIN-SGMSE-VOICEBANK",
            "SDK-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "Adjacent restoration families remain outside the CLN-01 release boundary.",
    },
    {
        "id": "G08",
        "actionable_gap": "Separate competing-speech cases from additive-noise suppression",
        "evidence_gap": "The registry requires this split; the 30-pair synthetic cohort does not resolve source identity or preservation policy.",
        "follow_up_ids": ["SDK-CONV-TASNET", "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY"],
        "feasibility_task_exists": True,
        "owner_note": "These links are boundary controls for SPK-01/SPK-02; they do not move separation into CLN-01.",
    },
    {
        "id": "G09",
        "actionable_gap": "Rights-qualified paired/no-reference cohorts and clean-preservation screen",
        "evidence_gap": "DNS/EARS/VCTK rights and per-source terms are unresolved; no listening playback clearance exists.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated feasibility row was found on the board; these existing research-control rows own the gate.",
    },
    {
        "id": "G10",
        "actionable_gap": "Target-device content/availability timing, memory and deadline evidence",
        "evidence_gap": "Batch RTF and worker wall time are historical context only; no callback-path measurement exists here.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "Existing foundation rows own the acceptance rules; no feasibility task was invented for this survey.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-SOX-NOISERED", "title": "SoX `noisered`", "mode": "feasibility"},
    {"task_id": "SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS", "title": "Pyroomacoustics candidate tools", "mode": "feasibility"},
    {"task_id": "SDK-RNNOISE-INT8-ARM-ML-MODEL-ZOO", "title": "RNNoise INT8 (Arm ML Model Zoo)", "mode": "feasibility"},
    {"task_id": "SDK-DEEPFILTERGAN", "title": "DeepFilterGAN", "mode": "feasibility"},
    {"task_id": "SDK-FASTENHANCER-BASE-REFERENCE", "title": "FastEnhancer Base reference", "mode": "feasibility"},
    {"task_id": "SDK-FASTENHANCER-MEDIUM-REFERENCE", "title": "FastEnhancer Medium reference", "mode": "feasibility"},
    {"task_id": "SDK-FASTENHANCER-LARGE-REFERENCE", "title": "FastEnhancer Large reference", "mode": "feasibility"},
    {"task_id": "SDK-CMGAN-LITERT-COMMUNITY-PORT", "title": "CMGAN-LiteRT community port", "mode": "feasibility"},
    {"task_id": "SDK-DPCRN-DNS3-TFLITE", "title": "DPCRN DNS3 / TFLite", "mode": "feasibility"},
    {"task_id": "SDK-SPEECHBRAIN-SGMSE-VOICEBANK", "title": "SpeechBrain SGMSE-VoiceBank", "mode": "feasibility"},
    {"task_id": "SDK-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE", "title": "SNR-Aligned Consistent Diffusion (DiffSE)", "mode": "feasibility"},
    {"task_id": "SDK-CONV-TASNET", "title": "Conv-TasNet", "mode": "feasibility"},
    {"task_id": "SDK-TARGET-SPEAKER-EXTRACTION-FAMILY", "title": "Target-speaker extraction family", "mode": "feasibility"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified real paired cohort with frozen candidate outputs"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent authorized listening with declared analysis plan"},
    {"id": "RG-03", "blocked": True, "requirement": "Pinned target-device content/availability timing, memory and deadline evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Task-matched external baseline under locked code, settings and runtime"},
    {"id": "RG-05", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-06", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-07", "blocked": True, "requirement": "Exact approved reference parity at frozen revision and settings"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "research/noise_suppression_pilot_20261027.md": [
        "| spectral_subtraction | 12.303 | 0.998 | 1.307 | 0.9469 |",
        "| fastenhancer_small | 18.456 | 7.301 | 8.112 | 0.9705 |",
        "| ffmpeg_afwtdn | 8.655 | -1.022 | -2.211 | 0.9080 |",
        "| spectral_subtraction | si_sdr_db | 1.3068 |",
        "| wiener | si_sdr_db | 0.4269 |",
        "| speexdsp | si_sdr_db | 1.0608 |",
        "| rnnoise | si_sdr_db | 3.1387 |",
        "| deepfilternet3 | si_sdr_db | 6.6596 |",
        "| fastenhancer_small | si_sdr_db | 8.1120 |",
        "| ffmpeg_afwtdn | si_sdr_db | -2.2115 |",
        "| webrtc_ns_level0 | stoi | -0.0056 |",
        "| webrtc_ns_level3 | stoi | -0.0466 |",
    ],
    "research/clean_speech_diagnostics_20261027.md": [
        "| wiener | 50.58 |",
        "| spectral_subtraction | 38.42 |",
        "| fastenhancer_small | 38.53 |",
        "| ffmpeg_afftdn | -2.95 |",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "The tested noise estimate uses the whole clip and is noncausal.",
        "scores are not human MOS",
        "100/30,210 frames exceeded 10 ms in one chain screen",
    ],
    "audio_categories.md": [
        "| **CLN-01 — Background noise suppression** |",
        "Separate stationary noise, changing noise, and competing speech scenarios; current speed is not an admission gate.",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/quality-impairment-taxonomy/README.md": [
        "zero collected ratings",
        "−0.063",
        "+0.386",
    ],
}

BOUNDARY: Dict[str, bool] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "provider_registration": False,
    "processor_exposure": False,
    "descriptor_registry_changed": False,
    "public_api_abi_changed": False,
    "installed_v0_changed": False,
    "shared_cmakelists_changed": False,
    "ci_changed": False,
    "board_changed": False,
    "handoff_changed": False,
    "provider_intake_complete": False,
    "release_approval": False,
}

SCOPE: Dict[str, bool] = {
    "task_local_only": True,
    "documentation_and_metadata_only": True,
    "no_new_execution": True,
    "synthetic_only_where_cited": True,
    "real_speech": False,
    "real_corpus": False,
    "weights": False,
    "runtime_invocation": False,
    "listening": False,
    "device_timing": False,
    "benchmark_claim": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
}

ADVERSE_REJECTIONS: Dict[str, str] = {
    "duplicate_json_key": "rejected; state unchanged",
    "nonfinite_json_number": "rejected; state unchanged",
    "missing_pinned_file": "rejected; state unchanged",
    "tampered_pin": "rejected; state unchanged",
    "unknown_board_task": "rejected; state unchanged",
    "gap_without_link_or_reason": "rejected; state unchanged",
    "invalid_payload_type": "rejected; state unchanged",
}


class MapError(ValueError):
    """Raised when a pin, input, mapping record or scope rule fails closed."""


def _reject_constant(token: str) -> None:
    raise MapError("nonfinite JSON constant is not allowed: " + token)


def _object_pairs(pairs: Iterable[tuple]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if not isinstance(key, str):
            raise MapError("non-string JSON key")
        if key in result:
            raise MapError("duplicate JSON key: " + key)
        result[key] = value
    return result


def strict_json_loads(text: str) -> Any:
    """Parse JSON with duplicate keys and NaN/Infinity rejected."""
    if not isinstance(text, str):
        raise MapError("JSON text must be str")
    return json.loads(text, object_pairs_hook=_object_pairs, parse_constant=_reject_constant)


def strict_json_load(path: Path) -> Any:
    """Read and strict-parse a UTF-8 JSON file."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MapError("cannot read JSON: %s" % path) from exc
    return strict_json_loads(text)


def canonical_bytes(value: Any) -> bytes:
    """Canonical JSON bytes: sorted keys, minimal separators, trailing LF."""
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise MapError("value is not canonical JSON: %s" % exc) from exc
    return (text + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
    except OSError as exc:
        raise MapError("cannot hash file: %s" % path) from exc
    return digest.hexdigest()


def task_dir() -> Path:
    return Path(__file__).resolve().parent


def find_workspace(explicit: Optional[str] = None) -> Path:
    """Locate the enclosing audioml workspace without writing to it."""
    if explicit:
        root = Path(explicit).resolve()
    else:
        env = os.environ.get("AUDIOML_WORKSPACE_ROOT")
        if env:
            root = Path(env).resolve()
        else:
            here = Path(__file__).resolve()
            candidates = [here.parent] + list(here.parents)
            root = None
            for candidate in candidates:
                if (
                    (candidate / "research/category_registry.json").is_file()
                    and (candidate / "audio-benchmark-platform/plan/INVENTORY.json").is_file()
                ):
                    root = candidate
                    break
            if root is None:
                raise MapError("workspace root not found; set AUDIOML_WORKSPACE_ROOT")
    if not (root / "research/category_registry.json").is_file():
        raise MapError("workspace marker missing: research/category_registry.json")
    if not (root / "audio-benchmark-platform/plan/INVENTORY.json").is_file():
        raise MapError("workspace marker missing: audio-benchmark-platform/plan/INVENTORY.json")
    return root


def find_sdk_root(explicit: Optional[str] = None) -> Path:
    """Locate the SDK worktree containing this task directory."""
    if explicit:
        root = Path(explicit).resolve()
    else:
        here = Path(__file__).resolve()
        root = None
        for candidate in [here.parent] + list(here.parents):
            if (candidate / "CONTRACTS.md").is_file() and (candidate / "REUSE.toml").is_file():
                root = candidate
                break
        if root is None:
            raise MapError("SDK worktree root not found")
    if not (root / "CONTRACTS.md").is_file():
        raise MapError("SDK marker missing: CONTRACTS.md")
    return root


def _validate_pin_map(pins: Mapping[str, str], label: str) -> None:
    if not isinstance(pins, Mapping):
        raise MapError(label + " pins must be a mapping")
    for path, digest in pins.items():
        if not isinstance(path, str) or not path or Path(path).is_absolute():
            raise MapError(label + " pin path is invalid")
        if ".." in Path(path).parts:
            raise MapError(label + " pin path traverses: " + path)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise MapError(label + " pin digest is invalid: " + path)


def _check_document_pins(workspace: Path, sdk_root: Path) -> None:
    _validate_pin_map(SOURCE_PINS, "source")
    _validate_pin_map(WORKTREE_PINS, "worktree")
    for relative, expected in SOURCE_PINS.items():
        actual = sha256_file(workspace / relative)
        if actual != expected:
            raise MapError("source pin mismatch: %s" % relative)
    for relative, expected in WORKTREE_PINS.items():
        actual = sha256_file(sdk_root / relative)
        if actual != expected:
            raise MapError("worktree pin mismatch: %s" % relative)


def _check_anchors(workspace: Path, sdk_root: Path) -> None:
    for relative, anchors in DOC_ANCHORS.items():
        text = (workspace / relative).read_text(encoding="utf-8")
        for anchor in anchors:
            if anchor not in text:
                raise MapError("pinned document anchor missing: %s :: %s" % (relative, anchor))
    for relative, anchors in WORKTREE_DOC_ANCHORS.items():
        text = (sdk_root / relative).read_text(encoding="utf-8")
        for anchor in anchors:
            if anchor not in text:
                raise MapError("worktree document anchor missing: %s :: %s" % (relative, anchor))


def _check_taxonomy(workspace: Path) -> None:
    registry = strict_json_load(workspace / "research/category_registry.json")
    inventory = strict_json_load(workspace / "audio-benchmark-platform/plan/INVENTORY.json")
    registry_hit = [c for c in registry["categories"] if c.get("id") == CATEGORY_ID]
    inventory_hit = [c for c in inventory["taxonomy"] if c.get("id") == CATEGORY_ID]
    if len(registry_hit) != 1 or len(inventory_hit) != 1:
        raise MapError("CLN-01 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-01 taxonomy mismatch: %s" % key)
    source_index = {s["id"]: s for s in registry["sources"]}
    for lead in SOURCE_LEADS:
        source = source_index.get(lead["source_id"])
        if source is None:
            raise MapError("registry source lead is missing: " + lead["source_id"])
        for key in ("title", "url", "access_scope"):
            if source.get(key) != lead[key]:
                raise MapError("source lead mismatch: %s/%s" % (lead["source_id"], key))


def _check_backlog(workspace: Path) -> None:
    backlog = strict_json_load(workspace / "research/task_backlog.json")
    hits = [e for e in backlog["entries"] if e.get("family_id") == LEGACY_FAMILY]
    if len(hits) != 1:
        raise MapError("legacy family F01 is not unique")
    entry = hits[0]
    expected = {
        "category_id": CATEGORY_ID,
        "activation_state": "catalogued",
        "state": "catalogued",
        "scope": "requested",
        "next_action": "Plan discovery across required source buckets",
        "blockers": [],
        "dependencies": [],
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise MapError("legacy backlog mismatch: F01/%s" % key)


def _check_component_census(workspace: Path) -> None:
    inventory = strict_json_load(workspace / "audio-benchmark-platform/plan/INVENTORY.json")
    by_id = {c["id"]: c for c in inventory["components"]}
    for row in COMPONENT_CENSUS:
        component = by_id.get(row["component_id"])
        if component is None:
            raise MapError("inventory component missing: " + row["component_id"])
        if component.get("task") != row["task"]:
            raise MapError("inventory task mismatch: " + row["component_id"])
        if component.get("evidence_status") != row["evidence_status"]:
            raise MapError("inventory evidence_status mismatch: " + row["component_id"])
    mapped = {c for lead in SOURCE_LEADS for c in lead["mapped_components"]}
    mapped.update(c for family in METHOD_FAMILIES for c in family["components"])
    missing = sorted(mapped - set(by_id))
    if missing:
        raise MapError("mapped component missing from inventory: " + ",".join(missing))


def _board_projection(board: Mapping[str, Any]) -> str:
    rows = [
        {"id": task["id"], "mode": task["mode"], "title": task["title"]}
        for task in board["tasks"]
        if task.get("id") in {link["task_id"] for link in BOARD_LINKS}
    ]
    rows.sort(key=lambda row: row["id"])
    return sha256_bytes(canonical_bytes(rows))


def _check_board(workspace: Path) -> str:
    board = strict_json_load(workspace / BOARD_PATH)
    if not isinstance(board.get("tasks"), list):
        raise MapError("board tasks is not a list")
    by_id = {t["id"]: t for t in board["tasks"]}
    for link in BOARD_LINKS:
        task = by_id.get(link["task_id"])
        if task is None:
            raise MapError("linked board task is missing: " + link["task_id"])
        if task.get("title") != link["title"] or task.get("mode") != link["mode"]:
            raise MapError("linked board task identity changed: " + link["task_id"])
    known = {link["task_id"] for link in BOARD_LINKS}
    link_ids = {gap["id"] for gap in GAPS}
    for gap in GAPS:
        if not isinstance(gap.get("follow_up_ids"), list) or not gap["follow_up_ids"]:
            raise MapError("gap has no linked board task: " + gap["id"])
        for task_id in gap["follow_up_ids"]:
            if task_id not in known:
                raise MapError("gap links an unlisted board task: %s/%s" % (gap["id"], task_id))
        if gap.get("feasibility_task_exists"):
            modes = {next(t["mode"] for t in BOARD_LINKS if t["task_id"] == tid) for tid in gap["follow_up_ids"]}
            if "feasibility" not in modes:
                raise MapError("gap claims a feasibility follow-up without one: " + gap["id"])
        elif not gap.get("owner_note"):
            raise MapError("gap without feasibility task has no owner note: " + gap["id"])
    for source in SOURCE_LEADS:
        for gap_id in source["gap_ids"]:
            if gap_id not in link_ids:
                raise MapError("source lead links unknown gap: " + gap_id)
    for family in METHOD_FAMILIES:
        for gap_id in family["gap_ids"]:
            if gap_id not in link_ids:
                raise MapError("method family links unknown gap: " + gap_id)
    return _board_projection(board)


def _build_report(workspace: Optional[str] = None, sdk_root: Optional[str] = None) -> Dict[str, Any]:
    ws = find_workspace(workspace)
    sdk = find_sdk_root(sdk_root)
    _check_document_pins(ws, sdk)
    _check_anchors(ws, sdk)
    _check_taxonomy(ws)
    _check_backlog(ws)
    _check_component_census(ws)
    board_digest = _check_board(ws)

    board = strict_json_load(ws / BOARD_PATH)
    by_id = {t["id"]: t for t in board["tasks"]}
    links: List[Dict[str, Any]] = []
    for link in BOARD_LINKS:
        task = by_id[link["task_id"]]
        linked_gaps = sorted(g["id"] for g in GAPS if link["task_id"] in g["follow_up_ids"])
        links.append(
            {
                "task_id": link["task_id"],
                "title": link["title"],
                "mode": link["mode"],
                "linked_gaps": linked_gaps,
            }
        )

    report: Dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "category_id": CATEGORY_ID,
        "legacy_family": LEGACY_FAMILY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "readiness": READINESS,
        "decision": DECISION,
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "legacy_backlog": {
            "family_id": LEGACY_FAMILY,
            "activation_state": "catalogued",
            "state": "catalogued",
            "next_action": "Plan discovery across required source buckets",
            "source_pin": "research/task_backlog.json",
        },
        "source_leads": [dict(lead) for lead in SOURCE_LEADS],
        "method_families": [dict(family) for family in METHOD_FAMILIES],
        "component_census": [dict(row) for row in COMPONENT_CENSUS],
        "comparison_inputs": [dict(row) for row in COMPARISON_INPUTS],
        "controls": [dict(row) for row in CONTROLS],
        "assets": [dict(row) for row in ASSETS],
        "historical_executions": [dict(row) for row in HISTORICAL_EXECUTIONS],
        "reported_outcomes": [dict(row) for row in REPORTED_OUTCOMES],
        "evidence_classes": {
            "paired_synthetic_historical_local": True,
            "unpaired_predictive_historical_local": True,
            "clean_preservation_diagnostic_historical_local": True,
            "prepared_listening_without_ratings": True,
            "human_listening_result": False,
            "vendor_or_source_reported": True,
            "new_execution_in_this_survey": False,
            "parity_or_qualification_claim": False,
        },
        "acceptance_profile": dict(ACCEPTANCE_PROFILE),
        "gaps": [dict(gap) for gap in GAPS],
        "board_links": links,
        "board_link_projection_sha256": board_digest,
        "mutable_provenance": {
            "gate": False,
            "path": BOARD_PATH,
            "sha256_at_read": sha256_file(ws / BOARD_PATH),
            "note": "Board status is mutable; only id/title/mode of linked rows are gated by board_link_projection_sha256.",
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(WORKTREE_PINS),
        "release_gates": [dict(gate) for gate in RELEASE_GATES],
        "adverse_rejections": dict(ADVERSE_REJECTIONS),
        "reproduction": {
            "comparison": "exact SHA-256 over canonical JSON; no tolerance; three byte-identical cold-start repeats",
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py",
            "report": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py report",
            "sources": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py sources",
            "contract": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py contract",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
        },
    }
    # Final fail-closed disposition checks; no gate may be weakened.
    if report["decision"] != DECISION or report["qualification_status"] != QUALIFICATION_STATUS:
        raise MapError("disposition changed")
    if report["readiness"] != READINESS or report["status"] != STATUS:
        raise MapError("status changed")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for key, value in report["boundary"].items() if key != "release_approval"):
        raise MapError("boundary is not closed")
    if report["boundary"]["release_approval"] is not False:
        raise MapError("release approval is not false")
    canonical_bytes(report)
    return report


class EvidenceMap:
    """Atomic holder for the built map; rejected input never changes state."""

    def __init__(self) -> None:
        self.state: Optional[Dict[str, Any]] = None

    def snapshot(self) -> Optional[Dict[str, Any]]:
        return copy.deepcopy(self.state)

    def build(
        self,
        workspace: Optional[str] = None,
        sdk_root: Optional[str] = None,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build the report; validate an optional caller payload atomically."""
        if payload is not None:
            if not isinstance(payload, Mapping):
                raise MapError("payload must be a mapping")
            for key, value in payload.items():
                if not isinstance(key, str) or not isinstance(value, (str, int, float, bool, type(None))):
                    raise MapError("invalid payload entry: %s" % key)
                if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
                    raise MapError("nonfinite payload value: %s" % key)
        candidate = _build_report(workspace=workspace, sdk_root=sdk_root)
        self.state = candidate
        return candidate


def build_report(workspace: Optional[str] = None, sdk_root: Optional[str] = None) -> Dict[str, Any]:
    """Return a fresh canonical report without mutating any module state."""
    return _build_report(workspace=workspace, sdk_root=sdk_root)
