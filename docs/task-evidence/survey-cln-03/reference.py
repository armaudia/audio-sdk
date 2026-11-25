# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-03.

This module builds a bounded taxonomy/comparison evidence map for the
wind-and-microphone-disturbance category (inventory category ``CLN-03``). It
reads only pinned, read-only documents from the enclosing ``audioml`` workspace
and the SDK worktree. It does not load audio, weights, runtimes, media or the
network, and it does not register, expose, enable or qualify any processor.

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
TASK = "SDK-SURVEY-CLN-03"
TITLE = "Review coverage for Wind and microphone disturbance reduction"
CATEGORY_ID = "CLN-03"
LEGACY_FAMILY = "F08"
BRANCH = "swarm/SDK-SURVEY-CLN-03"
BASE_COMMIT = "d507634052555c08f10aa9a3b344576c7429076a"
PROFILE = "Enhancement"
COMPONENT = "wind-microphone-disturbance-evidence-map"
STATUS = "proposal_only_survey_incomplete"
QUALIFICATION_STATUS = "not_qualified"
READINESS = "incomplete"
DECISION = "DEFER"

# REUSE-IgnoreStart
LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-Identifier: Apache-2.0\n"
)
# REUSE-IgnoreEnd

# Workspace-relative document pins. Every entry is a read-only document or
# metadata ledger consulted by this survey; a pin never grants rights or
# verifies media/weights that are not present in this task directory.
SOURCE_PINS: Dict[str, str] = {
    "REALTIME_COMPONENT_CANDIDATES.md": "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/cpp-library-voicebank-demand-20261109.md": "7f512f27530cab4262b9901f733ac1c6a396d062fa7f0d8c3bb04423a8c3ecf5",
    "research/level_tone_control_20261028.md": "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
    "research/noise_suppression_pilot_20261027.md": "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "research/pilot_source_research.md": "c9db16172ffaa1bcf8b5cc334d9401173528c31d1ec966176d6e99a0bbe52fe5",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# SDK-worktree-relative public-boundary pins. They are read only to prove that
# no public surface was touched; no header or component is copied, edited or
# generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/narrow-biquad-notch/README.md": "188d9bb3ec63ea1904701e00ff156967ec8fba9b58019a247cd5fb6b56f03015",
    "docs/task-evidence/sdk-high-pass-80-hz/README.md": "0a4578ccecf75d14d487f8ef0d9bbcdc6dcd7e187c40375c9e16579a76950bc7",
    "docs/task-evidence/sdk-high-pass-80-hz/report.json": "741babd8aff0e886f10041002213c5556b3a8b11bc69d2028a25c118ffd00d5b",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Acoustic cleanup and spatial processing",
    "name": "Wind and microphone disturbance reduction",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Address wind/turbulence and related capture interference.",
    "method_families": {
        "classic": "Detection and frequency-dependent attenuation; channel selection",
        "ml": "Wind-aware or general enhancement models",
    },
    "input_output": "Audio, optional extra microphones \u2192 enhanced waveform",
    "live_or_comparison_boundary": (
        "Keep separate stress tests. Dedicated wind candidates and their weights "
        "still require discovery."
    ),
    "source_ids": ["S45"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "CLN",
    "meaning": "Acoustic cleanup and spatial processing",
    "category_id": CATEGORY_ID,
    "wind_and_microphone_disturbance_only": True,
    "not_general_beamforming_category": "CLN-07",
    "not_tonal_correction_or_hum_category": "CLN-10",
    "high_pass_is_partial_low_frequency_control_only": True,
    "note": (
        "Beamforming and tonal/hum correction are separate catalogued "
        "categories. They are named only to prevent scope inflation; their "
        "results are not pooled into a CLN-03 wind claim."
    ),
}

WIND_BOUNDARY: Dict[str, Any] = {
    "wind_noise_is_broadband_and_nonstationary": True,
    "fixed_high_pass_is_partial_low_frequency_control": True,
    "wind_on_microphone_is_not_digital_disturbance": True,
    "handling_pops_and_gust_events_are_separate_subcases": True,
    "dedicated_wind_candidates_and_weights_discovered": False,
    "wind_specific_audio_staged": False,
    "wind_specific_execution_performed": False,
    "wind_specific_benchmark_or_listening_result": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S45",
        "title": "URGENT 2026 distortion taxonomy",
        "url": "https://urgent-challenge.github.io/urgent2026/track1/",
        "access_scope": "direct",
        "mapped_components": [
            "gap-urgenet",
            "urgent-bsrnn",
            "urgent-bsrnn-flow",
            "tf-gridnet-urgent-2025-baseline",
        ],
        "gap_ids": ["G01", "G09"],
        "finding": (
            "The catalogued source is a challenge taxonomy, not a runnable "
            "candidate or dataset. It provides a wind-noise condition and "
            "universal-enhancement context. No URGENT source, checkpoint, "
            "training data, evaluation audio or runtime is staged in this "
            "task; the challenge rules also restrict training data and "
            "pretrained enhancement models, so reported challenge results are "
            "not a neutral local comparison."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Wind/turbulence detection and frequency-dependent attenuation (high-pass/rumble filtering)",
        "components": [
            "sdk-high-pass-80-hz",
            "native-variable-cutoff-high-pass",
            "narrow-biquad-notch",
        ],
        "gap_ids": ["G02"],
        "status": "historical_local_synthetic_dsp_only_no_wind_execution",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Classical spectral suppression and adaptive noise estimation as general attenuation baselines",
        "components": [
            "webrtc-apm-ns",
            "speexdsp-ns-reference",
            "classical-spectral-subtraction",
            "classical-wiener-denoising",
        ],
        "gap_ids": ["G04"],
        "status": "historical_local_adjacent_noise_suppression_only",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Channel selection and multi-microphone combination for capture disturbance",
        "components": [
            "3d-microphone-spatial-time-alignment",
            "delay-and-sum-beamformer",
            "mvdr-beamforming",
            "source-localization-direction-of-arrival",
        ],
        "gap_ids": ["G03"],
        "status": "catalogued_only_no_local_wind_or_spatial_execution",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Wind-aware universal enhancement models (URGENT family)",
        "components": [
            "gap-urgenet",
            "urgent-bsrnn",
            "urgent-bsrnn-flow",
            "tf-gridnet-urgent-2025-baseline",
        ],
        "gap_ids": ["G01", "G04", "G09"],
        "status": "catalogued_or_blocked_no_local_execution_no_weights",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "General speech-enhancement models applied to capture disturbance",
        "components": [
            "rnnoise-v0-2",
            "deepfilternet3-v0-5-6",
            "fastenhancer-small-reference",
            "clearvoice-frcrn-16-khz",
        ],
        "gap_ids": ["G04"],
        "status": "historical_local_adjacent_noise_suppression_only",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Neural spatial filtering and beamforming",
        "components": ["neural-beamforming", "spatialnet"],
        "gap_ids": ["G03"],
        "status": "catalogued_or_blocked_no_local_execution",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "sdk-high-pass-80-hz", "evidence_status": "integrated", "task": "SDK-SDK-HIGH-PASS-80-HZ"},
    {"component_id": "native-variable-cutoff-high-pass", "evidence_status": "source-local", "task": "PRO-NATIVE-VARIABLE-CUTOFF-HIGH-PASS"},
    {"component_id": "narrow-biquad-notch", "evidence_status": "partial", "task": "SDK-NARROW-BIQUAD-NOTCH"},
    {"component_id": "webrtc-apm-ns", "evidence_status": "evaluated", "task": "SDK-WEBRTC-APM-NS"},
    {"component_id": "speexdsp-ns-reference", "evidence_status": "integrated", "task": "SDK-SPEEXDSP-NS-REFERENCE"},
    {"component_id": "classical-spectral-subtraction", "evidence_status": "evaluated", "task": "SDK-CLASSICAL-SPECTRAL-SUBTRACTION"},
    {"component_id": "classical-wiener-denoising", "evidence_status": "evaluated", "task": "SDK-CLASSICAL-WIENER-DENOISING"},
    {"component_id": "3d-microphone-spatial-time-alignment", "evidence_status": "considered", "task": "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT"},
    {"component_id": "delay-and-sum-beamformer", "evidence_status": "considered", "task": "SDK-DELAY-AND-SUM-BEAMFORMER"},
    {"component_id": "mvdr-beamforming", "evidence_status": "considered", "task": "SDK-MVDR-BEAMFORMING"},
    {"component_id": "source-localization-direction-of-arrival", "evidence_status": "considered", "task": "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL"},
    {"component_id": "gap-urgenet", "evidence_status": "blocked", "task": "SDK-GAP-URGENET"},
    {"component_id": "urgent-bsrnn", "evidence_status": "blocked", "task": "SDK-URGENT-BSRNN"},
    {"component_id": "urgent-bsrnn-flow", "evidence_status": "considered", "task": "SDK-URGENT-BSRNN-FLOW"},
    {"component_id": "tf-gridnet-urgent-2025-baseline", "evidence_status": "considered", "task": "SDK-TF-GRIDNET-URGENT-2025-BASELINE"},
    {"component_id": "rnnoise-v0-2", "evidence_status": "evaluated", "task": "SDK-RNNOISE-V0-2"},
    {"component_id": "deepfilternet3-v0-5-6", "evidence_status": "evaluated", "task": "SDK-DEEPFILTERNET3-V0-5-6"},
    {"component_id": "fastenhancer-small-reference", "evidence_status": "evaluated", "task": "SDK-FASTENHANCER-SMALL-REFERENCE"},
    {"component_id": "clearvoice-frcrn-16-khz", "evidence_status": "evaluated", "task": "SDK-CLEARVOICE-FRCRN-16-KHZ"},
    {"component_id": "neural-beamforming", "evidence_status": "blocked", "task": "SDK-NEURAL-BEAMFORMING"},
    {"component_id": "spatialnet", "evidence_status": "blocked", "task": "SDK-SPATIALNET"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Installed 80 Hz high-pass synthetic tones, DC steps, chirp, harmonic speech proxy and 20 Hz rumble plus speech proxy",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/sdk-high-pass-80-hz/README.md",
        "boundary": "Deterministic DSP control for low-frequency attenuation only; no wind, turbulence, real speech, listening or device timing.",
    },
    {
        "id": "CI-2",
        "input": "Optional synthetic RBJ notch fixture at 1000 Hz center with 100 Hz bandwidth plus four center/bandwidth controls",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/narrow-biquad-notch/README.md",
        "boundary": "Narrow tonal attenuation control; not broadband wind suppression, real speech or listening.",
    },
    {
        "id": "CI-3",
        "input": "30 paired DNS2020 clips used for RNNoise and SpeexDSP noise-suppression pilots",
        "class": "historical_local_adjacent_noise_suppression",
        "source_pin": "research/noise_suppression_pilot_20261027.md",
        "boundary": "Adjacent additive-noise context only; not a wind, gust, handling or microphone-disturbance cohort.",
    },
    {
        "id": "CI-4",
        "input": "824 paired VoiceBank+DEMAND utterances comparing basic.v1 with voice_focus.v1, which adds an 80 Hz high-pass",
        "class": "historical_local_adjacent_chain",
        "source_pin": "research/cpp-library-voicebank-demand-20261109.md",
        "boundary": "Chain-level preset comparison; high-pass is not isolated from Speex NS and limiting, and the corpus is not wind.",
    },
    {
        "id": "CI-5",
        "input": "URGENT 2025/2026 challenge wind-noise condition and distortion taxonomy",
        "class": "source_reported_only",
        "source_pin": "research/pilot_source_research.md",
        "boundary": "Challenge-level documentation only; no local runtime, checkpoint, evaluation audio or neutral leaderboard comparison.",
    },
    {
        "id": "CI-6",
        "input": "Dedicated wind/turbulence and microphone-disturbance recordings with clean reference",
        "class": "missing_no_local_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "The registry explicitly says dedicated wind candidates and weights require discovery; none is staged here.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "analytic biquad reference", "role": "Exact analytic high-pass/notch response and identity control for synthetic DSP fixtures.", "source_pin": "docs/task-evidence/sdk-high-pass-80-hz/report.json"},
    {"id": "CT-2", "name": "DC step and exact silence", "role": "Checks rumble/DC settling without treating a high-pass as a wind detector.", "source_pin": "docs/task-evidence/sdk-high-pass-80-hz/README.md"},
    {"id": "CT-3", "name": "noisy-input identity", "role": "Paired baseline for adjacent DNS noise-suppression records.", "source_pin": "research/noise_suppression_pilot_20261027.md"},
    {"id": "CT-4", "name": "preset ablation basic.v1 versus voice_focus.v1", "role": "Chain-level high-pass addition context; not a component-isolated wind control.", "source_pin": "research/cpp-library-voicebank-demand-20261109.md"},
    {"id": "CT-5", "name": "clean-speech and speech-band preservation control", "role": "Registry boundary for wind mitigation; no executed wind or real-speech preservation result is mapped here.", "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md"},
    {"id": "CT-6", "name": "synthetic harmonic speech proxy", "role": "Synthetic-only preservation proxy; not STOI, real speech or a listening result.", "source_pin": "docs/task-evidence/sdk-high-pass-80-hz/README.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Installed SDK high-pass 80 Hz provider and deterministic DSP fixtures",
        "class": "sdk_installed_component",
        "status": "Integrated reference control; no wind recordings, weights or corpus staged",
        "source_pin": "docs/task-evidence/sdk-high-pass-80-hz/README.md",
    },
    {
        "asset": "Optional narrow biquad notch synthetic fixture",
        "class": "synthetic_dsp_fixture",
        "status": "Synthetic-only; not installed or registered by default",
        "source_pin": "docs/task-evidence/narrow-biquad-notch/README.md",
    },
    {
        "asset": "URGENT 2026 distortion taxonomy and URGENT 2025 challenge context",
        "class": "external_documentation",
        "status": "Documentation only; no audio, weights or runtime acquired and no rights transfer",
        "source_pin": "research/pilot_source_research.md",
    },
    {
        "asset": "RNNoise and general enhancement model weights",
        "class": "research_model_assets",
        "status": "Pinned only by cited research ledgers; per-weight rights and wind-condition suitability unresolved, not staged here",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
    },
    {
        "asset": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests",
        "class": "research_metadata",
        "status": "Prepared evidence manifests; none is a wind/turbulence cohort and no new listening result exists",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Installed 80 Hz high-pass deterministic DSP conformance",
        "outcome_class": "historical_local_synthetic",
        "component_ids": ["sdk-high-pass-80-hz"],
        "source_pin": "docs/task-evidence/sdk-high-pass-80-hz/README.md",
        "values": {
            "scenarios": 25,
            "processed_frames": 2376,
            "processed_samples": 380160,
            "checks_passed": 128,
            "checks_failed": 0,
            "installed_conformance_checks": 40,
            "invalid_missing_nonfinite_controls": 20,
            "gain_80_hz_db": -3.01,
            "rumble_20_hz_attenuation_db": 24.10,
            "speech_proxy_band_gain_db": 0.0181,
            "speech_proxy_envelope_correlation": 0.9989,
            "dc_settle_mean_abs": 1.9e-15,
            "content_delay_samples": 0,
        },
        "scope": "Installed 16 kHz mono f32 160-sample high-pass provider on synthetic tones, DC, chirp, harmonic speech proxy and 20 Hz rumble; no wind, real speech, listening or device timing; not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Narrow biquad notch synthetic frequency sweep",
        "outcome_class": "historical_local_synthetic",
        "component_ids": ["narrow-biquad-notch"],
        "source_pin": "docs/task-evidence/narrow-biquad-notch/README.md",
        "values": {
            "sweep_frequencies": 78,
            "conditions": 16,
            "center_bandwidth_pairs": 4,
            "processed_frames": 8168,
            "processed_samples": 1306880,
            "center_measured_gain_1000_hz": 0.004751,
            "max_sweep_gain_error_db": 0.006,
            "clean_proxy_rms_delta_db": -0.056,
            "clean_proxy_envelope_correlation": 0.999763,
            "adverse_config_cases": 12,
        },
        "scope": "Optional synthetic RBJ notch at 1000 Hz center and 100 Hz bandwidth, 16 kHz; narrow frequency-dependent attenuation control only, not broadband wind, real speech or listening; not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "RNNoise general noise-suppression pilot",
        "outcome_class": "historical_local_adjacent_noise_suppression",
        "component_ids": ["rnnoise-v0-2"],
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "values": {
            "mean_delta_sisdr_db": 3.14,
            "mean_delta_stoi": 0.0215,
            "process_frame_rtf": 0.0662,
        },
        "scope": "30 paired DNS2020 items through an offline 48 kHz adapter; adjacent additive-noise context, not wind/turbulence; RTF excludes resampling, setup and I/O; not rerun by this survey.",
    },
    {
        "id": "HE-4",
        "label": "SpeexDSP general noise-suppression pilot",
        "outcome_class": "historical_local_adjacent_noise_suppression",
        "component_ids": ["speexdsp-ns-reference"],
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "values": {
            "mean_delta_sisdr_db": 1.06,
            "mean_delta_stoi": -0.0057,
            "batch_rtf": 0.0006,
        },
        "scope": "30 paired DNS2020 items with 16 kHz NS-only 20 ms frames; adjacent additive-noise context, not wind/turbulence; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "URGENT 2026 distortion taxonomy includes a wind-noise condition",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Direct taxonomy documentation only; no local audio, weights, runtime or matched cohort is created here.",
    },
    {
        "id": "RO-2",
        "claim": "URGENT 2025 challenge covers wind noise and released a 1,000-sample synthetic validation set under restricted rules",
        "class": "source_reported",
        "source_pin": "research/pilot_source_research.md",
        "boundary": "Challenge-level research lead; rules restrict training data and pretrained models, so reported results are not a neutral local comparison.",
    },
    {
        "id": "RO-3",
        "claim": "VoiceBank+DEMAND chain-level preset with a high-pass: voice_focus.v1 PESQ 2.233, STOI 0.9086, SI-SDR 5.72 dB versus basic.v1 2.160, 0.9086, 9.44 dB",
        "class": "historical_local_adjacent_chain_reported",
        "source_pin": "research/cpp-library-voicebank-demand-20261109.md",
        "boundary": "High-pass is confounded with Speex NS and limiting; corpus is not wind; not a component-isolated or CLN-03 result.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "identity_control": "CT-3 / CT-2; noisy-input and DC/silence controls, not a wind condition",
        "matched_baseline": "CT-1 / CT-3; analytic DSP and noisy identity baselines",
        "modality_split": "Wind/turbulence, handling/pops and digital disturbance remain separate; no wind cohort exists",
        "paired_objective_scores": "HE-1..HE-4; transcribed synthetic or adjacent DNS values, not rerun here",
        "clean_preservation": "CT-5 / CT-6; required, but no executed wind or real-speech preservation result",
        "peaks_and_invalid_outputs": "HE-1 finite/invalid controls only; no wind-chain peak or invalid-output study",
        "unpaired_predictive_screen": "No CLN-03-specific predictive score in reviewed records",
        "listening": "No wind listening items, ratings or playback clearance",
        "alignment_state_memory_timing": "HE-1 zero-delay DSP context; no wind-chain or device timing",
    },
    "blocked": [
        "Annotated wind/turbulence and microphone-disturbance cohort with clean reference",
        "Separate gust, handling/pop and digital-disturbance protocols with frozen metadata",
        "Clean-speech preservation control and independent listening under wind conditions",
        "Target-device content/availability timing, memory and deadline evidence",
        "Task-matched external baseline under a locked runtime",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval",
        "Exact approved reference parity at frozen revision and settings",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "paired_synthetic_historical_local": True,
    "adjacent_noise_suppression_historical_local": True,
    "unpaired_predictive_historical_local": False,
    "clean_preservation_diagnostic_historical_local": False,
    "prepared_listening_without_ratings": False,
    "human_listening_result": False,
    "vendor_or_source_reported": True,
    "wind_specific_execution": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Acquire a dedicated wind/turbulence and microphone-disturbance cohort with annotated events and clean reference",
        "evidence_gap": "No wind-specific audio, event labels, clean reference or matched cohort is staged; the category is catalogued with candidate census and benchmark not_started.",
        "follow_up_ids": [
            "SDK-GAP-URGENET",
            "SDK-URGENT-BSRNN",
            "SDK-URGENT-BSRNN-FLOW",
            "SDK-TF-GRIDNET-URGENT-2025-BASELINE",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "URGENT-family feasibility rows and the evidence-manifest control are scoping leads only; no component owner has a wind-specific cohort or runnable candidate.",
    },
    {
        "id": "G02",
        "actionable_gap": "Evaluate high-pass/rumble attenuation against wind and speech preservation instead of synthetic tones alone",
        "evidence_gap": "The installed 80 Hz high-pass has deterministic synthetic conformance and 24.10 dB attenuation at 20 Hz, but no wind, turbulence or real-speech preservation result; the native variable-cutoff stage is source-local and unbenchmarked for this category.",
        "follow_up_ids": [
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-03 feasibility row was found for a wind-specific high-pass study; the linked research-control and foundation rows own cohort, preservation and evidence rules, not a wind capability.",
    },
    {
        "id": "G03",
        "actionable_gap": "Evaluate channel selection and multi-microphone combination on wind-disturbed captures",
        "evidence_gap": "Delay-and-sum, MVDR, source localization and 3D alignment are catalogued only; neural beamforming and SpatialNet are blocked. No wind, geometry, channel-mismatch or array execution was found.",
        "follow_up_ids": [
            "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
            "SDK-DELAY-AND-SUM-BEAMFORMER",
            "SDK-MVDR-BEAMFORMING",
            "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked spatial feasibility rows are scoping leads for geometry and array evaluation; none is a wind-mitigation component or executed result.",
    },
    {
        "id": "G04",
        "actionable_gap": "Establish wind-condition evidence for general and wind-aware enhancement models",
        "evidence_gap": "RNNoise and SpeexDSP have adjacent DNS2020 noise-suppression values only; URGENT-family candidates are blocked or considered and no local checkpoint, runtime or wind-condition result exists.",
        "follow_up_ids": [
            "SDK-GAP-URGENET",
            "SDK-URGENT-BSRNN",
            "SDK-URGENT-BSRNN-FLOW",
            "SDK-TF-GRIDNET-URGENT-2025-BASELINE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked URGENT-family rows are bounded feasibility leads, not enabled processors, staged weights or a wind-specific quality claim.",
    },
    {
        "id": "G05",
        "actionable_gap": "Separate gust/turbulence, handling/pop and digital-disturbance stress protocols with frozen metadata",
        "evidence_gap": "The registry requires separate stress tests, but reviewed records do not freeze wind speed, gust schedule, microphone placement, handling events or capture geometry.",
        "follow_up_ids": [
            "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The spatial feasibility row can declare geometry, but no CLN-03-specific protocol or component owner exists; the foundation row owns frozen evidence rules.",
    },
    {
        "id": "G06",
        "actionable_gap": "Collect target-device content/availability timing, memory and deadline evidence for a wind-mitigation chain",
        "evidence_gap": "Only offline synthetic DSP and adjacent batch RTF are documented; no callback-path, memory, deadline or device measurement exists for wind mitigation.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-03 timing feasibility row was found; the foundation rows own lifecycle, acceptance and timing-evidence rules.",
    },
    {
        "id": "G07",
        "actionable_gap": "Secure rights-qualified wind audio and model weights with provenance",
        "evidence_gap": "URGENT data and checkpoints are not acquired; general enhancement weights have unresolved per-weight terms and are not staged; no wind playback or derived-output clearance exists.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-GAP-URGENET",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The evidence-manifest control owns rights metadata, while the URGENT feasibility row is a candidate-discovery lead; neither grants rights or stages wind assets.",
    },
    {
        "id": "G08",
        "actionable_gap": "Run independent listening and clean-speech preservation analysis under wind conditions",
        "evidence_gap": "No wind listening items, ratings, playback clearance or real-speech preservation diagnostic was found; synthetic speech proxies are not listening evidence.",
        "follow_up_ids": [
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-03 listening feasibility row was found; the research-control rows own preservation and control design, not a listening result.",
    },
    {
        "id": "G09",
        "actionable_gap": "Discover and pin a dedicated wind-aware model, checkpoint and runtime before any comparison",
        "evidence_gap": "The S45 lead is a taxonomy; GAP-URGENet and URGENT BSRNN are blocked, BSRNN-Flow and TF-GridNet are considered, and no exact wind-aware checkpoint, revision or runtime is pinned.",
        "follow_up_ids": [
            "SDK-GAP-URGENET",
            "SDK-URGENT-BSRNN",
            "SDK-URGENT-BSRNN-FLOW",
            "SDK-TF-GRIDNET-URGENT-2025-BASELINE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked rows are discovery feasibility leads only; no candidate is installed, enabled or promoted by this map.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-GAP-URGENET", "title": "GAP-URGENet", "mode": "feasibility"},
    {"task_id": "SDK-URGENT-BSRNN", "title": "URGENT BSRNN", "mode": "feasibility"},
    {"task_id": "SDK-URGENT-BSRNN-FLOW", "title": "URGENT BSRNN-Flow", "mode": "feasibility"},
    {"task_id": "SDK-TF-GRIDNET-URGENT-2025-BASELINE", "title": "TF-GridNet URGENT 2025 baseline", "mode": "feasibility"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS", "title": "CCF AATC unified restoration controls", "mode": "research-control"},
    {"task_id": "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT", "title": "3D microphone spatial / time alignment", "mode": "feasibility"},
    {"task_id": "SDK-DELAY-AND-SUM-BEAMFORMER", "title": "Delay-and-sum beamformer", "mode": "feasibility"},
    {"task_id": "SDK-MVDR-BEAMFORMING", "title": "MVDR beamforming", "mode": "feasibility"},
    {"task_id": "SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL", "title": "Source localization / direction-of-arrival", "mode": "feasibility"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified wind/turbulence and microphone-disturbance cohort with annotated events and clean reference"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent authorized listening with declared speech-preservation analysis under wind conditions"},
    {"id": "RG-03", "blocked": True, "requirement": "Pinned target-device content/availability timing, memory and deadline evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Task-matched external baseline with gust, handling and digital subcases separated under a locked runtime"},
    {"id": "RG-05", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-06", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-07", "blocked": True, "requirement": "Exact approved reference parity at frozen revision and settings"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-03 — Wind and microphone disturbance reduction** | Address wind/turbulence and related capture interference.",
        "Keep separate stress tests. Dedicated wind candidates and their weights still require discovery.",
    ],
    "research/category_survey/sources.md": [
        "| S45 | [URGENT 2026 distortion taxonomy](https://urgent-challenge.github.io/urgent2026/track1/) | root | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Enhancement | Run identity/noisy control and an established task-matched baseline.",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "| High-pass filter | Rumble/DC removal | Two-pole code exists locally; no dedicated quality benchmark. |",
        "DNS pilot mean \u0394SI-SDR +3.14 dB, \u0394STOI +0.0215, RTF 0.0662 for `rnnoise_process_frame` only (excludes resampling/setup/I/O).",
        "DNS pilot mean \u0394SI-SDR +1.06 dB, \u0394STOI \u22120.0057, batch RTF about 0.0006.",
    ],
    "research/level_tone_control_20261028.md": [
        "Two-pole high-pass and narrow notch filters for rumble/DC-adjacent content and mains hum.",
    ],
    "research/cpp-library-voicebank-demand-20261109.md": [
        "`voice_focus.v1` adds an 80 Hz high-pass filter and requires the experimental opt-in flag.",
        "The experimental `voice_focus.v1` improves PESQ more, but loses SI-SDR and has the same STOI reduction.",
    ],
    "research/pilot_source_research.md": [
        "The Interspeech 2025 URGENT challenge covers additive noise, reverberation, clipping, bandwidth limitation, codec artifacts, packet loss, and wind noise",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/sdk-high-pass-80-hz/README.md": [
        "80 Hz is \u22123.01 dB",
        "rumble attenuation `24.10 dB`",
        "records no dedicated quality benchmark",
    ],
    "docs/task-evidence/narrow-biquad-notch/README.md": [
        "**proposal-only / synthetic**",
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
    "real_wind_audio": False,
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
    "unknown_component": "rejected; state unchanged",
    "wind_claim_without_wind_execution": "rejected; state unchanged",
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
        raise MapError("CLN-03 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-03 taxonomy mismatch: %s" % key)
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
    hits = [
        e
        for e in backlog["entries"]
        if e.get("family_id") == LEGACY_FAMILY and e.get("category_id") == CATEGORY_ID
    ]
    if len(hits) != 1:
        raise MapError("legacy family F08 / CLN-03 is not unique")
    entry = hits[0]
    expected = {
        "category_id": CATEGORY_ID,
        "activation_state": "catalogued",
        "state": "catalogued",
        "scope": "discovered_extension",
        "next_action": "Plan discovery across required source buckets",
        "blockers": [],
        "dependencies": [],
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise MapError("legacy backlog mismatch: F08/CLN-03/%s" % key)


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


def _check_historical_execution_components() -> None:
    known = {row["component_id"] for row in COMPONENT_CENSUS}
    for row in HISTORICAL_EXECUTIONS:
        ids = row.get("component_ids")
        if not ids:
            raise MapError("historical execution has no component link: " + row["id"])
        missing = sorted(set(ids) - known)
        if missing:
            raise MapError(
                "historical execution links an uncensused component: %s/%s"
                % (row["id"], ",".join(missing))
            )


def _check_evidence_classes() -> None:
    comparison = [row["class"] for row in COMPARISON_INPUTS]
    labels = [row["label"].lower() for row in HISTORICAL_EXECUTIONS]
    text = " ".join(comparison + labels)
    checks = {
        "paired_synthetic_historical_local": "paired_synthetic" in text,
        "adjacent_noise_suppression_historical_local": "adjacent" in text,
        "unpaired_predictive_historical_local": "predictive" in text,
        "clean_preservation_diagnostic_historical_local": "preservation" in text,
        "prepared_listening_without_ratings": "prepared_listening" in text,
        "wind_specific_execution": "wind" in text or "turbulence" in text,
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    if EVIDENCE_CLASSES["human_listening_result"] is not False:
        raise MapError("human listening result is not backed by a mapped rating record")
    if EVIDENCE_CLASSES["new_execution_in_this_survey"] is not False:
        raise MapError("new-execution claim is not allowed")
    if EVIDENCE_CLASSES["parity_or_qualification_claim"] is not False:
        raise MapError("parity or qualification claim is not allowed")


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
    _check_historical_execution_components()
    _check_evidence_classes()
    board_digest = _check_board(ws)

    board = strict_json_load(ws / BOARD_PATH)
    by_id = {t["id"]: t for t in board["tasks"]}
    links: List[Dict[str, Any]] = []
    for link in BOARD_LINKS:
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
        "category_scope": dict(CATEGORY_SCOPE),
        "wind_boundary": dict(WIND_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "wind_specific_component_ids": [],
            "wind_specific_weights_present": False,
            "wind_specific_corpus_present": False,
            "note": "Dedicated wind candidates and weights remain undiscovered; mapped components are adjacent, partial or catalogued only.",
        },
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
        "evidence_classes": dict(EVIDENCE_CLASSES),
        "acceptance_profile": dict(ACCEPTANCE_PROFILE),
        "gaps": [dict(gap) for gap in GAPS],
        "board_links": links,
        "board_link_projection_sha256": board_digest,
        "mutable_provenance": {
            "gate": False,
            "path": BOARD_PATH,
            "note": "Board status is mutable and the file is never hashed into canonical bytes; only id/title/mode of linked rows are gated by board_link_projection_sha256.",
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
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count changed")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for key, value in report["boundary"].items() if key != "release_approval"):
        raise MapError("boundary is not closed")
    if report["boundary"]["release_approval"] is not False:
        raise MapError("release approval is not false")
    if report["wind_boundary"]["dedicated_wind_candidates_and_weights_discovered"] is not False:
        raise MapError("wind candidate discovery is not closed")
    if report["discovery"]["wind_specific_component_ids"]:
        raise MapError("a wind-specific component is claimed")
    if BOARD_PATH in report["source_pins"]:
        raise MapError("mutable board file is pinned")
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
