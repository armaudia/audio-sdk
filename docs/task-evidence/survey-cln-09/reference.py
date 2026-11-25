# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-09.

This module builds a bounded taxonomy/comparison evidence map for the gain,
loudness and dynamic-range-control category (inventory category ``CLN-09``). It
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
TASK = "SDK-SURVEY-CLN-09"
TITLE = "Review coverage for Gain, loudness and dynamic-range control"
CATEGORY_ID = "CLN-09"
LEGACY_FAMILY = "F09"
BRANCH = "swarm/SDK-SURVEY-CLN-09"
BASE_COMMIT = "d5b11912cd09e87296cd9d4654f1917c9cb94258"
PROFILE = "DSP"
COMPONENT = "gain-loudness-dynamics-evidence-map"
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
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/level_tone_control_20261028.md": "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# SDK-worktree-relative public-boundary and evidence pins. They are read only
# to prove that no public surface was touched and to ground curated values; no
# header, report or component is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/ebu-r128-ffmpeg-loudnorm/report.json": "186639e731d78ea00939c5491311c599fb63d1c563777588ff186320aa311e4d",
    "docs/task-evidence/envelope-agc/fixtures/report.json": "f4bdf1862c75ed89cb1ca8c3bc8ee21aeb7831495410a210d4ca6d3e81950fe3",
    "docs/task-evidence/feed-forward-compressor/report.json": "72841527b1736e09cd96fd2e3d8efd609e4e2f9a75bb2f4e5b8e417a67343eb9",
    "docs/task-evidence/full-band-receive-drc/report.json": "9a685e1868e8290aa99131d810aa919df5c64712f3eebba40ab754788624d3f9",
    "docs/task-evidence/peak-limiter-reference/fixtures/report.json": "693890fed7e069fedfe240954c6b005251c60575462e44e9291afcdae4e7fad4",
    "docs/task-evidence/ridge-static-gain/report.json": "a0a81ae8ff9d7d966b1a47d6ac001f14fc0c4a7a82be316c8f5522ed06c37e2a",
    "docs/task-evidence/speex-agc-and-activity-output/evidence/report.json": "690da975dff985cd91126cb42400b3ab28df5cabf7435cc551028fd57723671e",
    "docs/task-evidence/static-target-gain-with-peak-ceiling/fixtures/report.json": "09500a0414822caef99d1146157b293eea9ebab70e9cf03b2d665c15cea0a3eb",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Acoustic cleanup and spatial processing",
    "name": "Gain, loudness and dynamic-range control",
    "scope": "discovered_extension",
    "output_kind": "waveform/control",
    "purpose": "Keep speech audible and manage peaks.",
    "method_families": {
        "classic": "AGC; compression; peak limiting; streaming loudness control",
        "ml": "Learned control is an open family search, not required to populate the task",
    },
    "input_output": "Audio, optionally device gain controls \u2192 leveled waveform/control",
    "live_or_comparison_boundary": (
        "Capture gain, digital leveling, limiting and whole-file normalization "
        "are separate subcases; track clipping and noise amplification."
    ),
    "source_ids": ["S27", "S19", "S46"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "CLN",
    "meaning": "Acoustic cleanup and spatial processing",
    "category_id": CATEGORY_ID,
    "gain_loudness_and_dynamic_range_only": True,
    "not_tonal_correction_category": "CLN-10",
    "not_declipping_category": "RST-01",
    "not_noise_suppression_category": "CLN-01",
    "not_echo_cancellation_category": "CLN-05",
    "note": (
        "Tonal correction, declipping/saturation restoration, noise suppression "
        "and echo cancellation are separate catalogued categories. They are "
        "named only to prevent scope inflation; their results are not pooled "
        "into a CLN-09 gain/loudness/dynamics claim."
    ),
}

LEVEL_BOUNDARY: Dict[str, Any] = {
    "capture_gain_is_not_digital_leveling": True,
    "digital_leveling_is_not_whole_file_normalization": True,
    "peak_limiting_is_not_loudness_normalization": True,
    "streaming_loudness_control_is_not_offline_mastering": True,
    "clipping_and_noise_amplification_are_tracked": True,
    "device_gain_control_contract_measured": False,
    "loudness_standard_conformance_measured": False,
    "rights_qualified_paired_cohort_staged": False,
    "human_listening_result": False,
    "target_device_timing_measured": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S27",
        "title": "WebRTC audio processing interface",
        "url": "https://webrtc.googlesource.com/src/+/refs/heads/main/api/audio/audio_processing.h",
        "access_scope": "direct",
        "mapped_components": [
            "webrtc-agc-agc2",
            "se-agcnet",
        ],
        "gap_ids": ["G03", "G05"],
        "finding": (
            "The catalogued source is the WebRTC audio-processing interface "
            "description, which motivates adaptive digital gain followed by a "
            "limiter with configurable headroom and bounded gain changes. Only "
            "documentation is reviewed here: no WebRTC source tree, binary, "
            "runtime, descriptor or parity result is staged, so the candidate "
            "remains considered only."
        ),
    },
    {
        "source_id": "S19",
        "title": "FFmpeg audio filters",
        "url": "https://ffmpeg.org/ffmpeg-filters.html",
        "access_scope": "direct",
        "mapped_components": [
            "ebu-r128-ffmpeg-loudnorm",
            "feed-forward-compressor",
        ],
        "gap_ids": ["G02", "G04"],
        "finding": (
            "The catalogued source documents EBU R128 integrated loudness, "
            "loudness range, true-peak control, lookahead limiting and "
            "compressor/limiter filters. Documentation is not a local FFmpeg "
            "invocation, version/config capture, standards-meter audit or "
            "two-pass loudnorm parity result; the local task fixtures are "
            "minimal Python references and do not claim to reproduce it."
        ),
    },
    {
        "source_id": "S46",
        "title": "Speech Signal Improvement challenge findings",
        "url": "https://www.microsoft.com/en-us/research/publication/icassp-2024-speech-signal-improvement-challenge-2/",
        "access_scope": "search excerpt",
        "mapped_components": [
            "noise-aware-shaping-plus-drc",
            "self-supervised-neural-multiband-eq-and-dynamics",
        ],
        "gap_ids": ["G01", "G06"],
        "finding": (
            "The catalogued source is a challenge-findings excerpt about "
            "speech-signal-improvement evaluation framing. It supplies no "
            "loudness/dynamic-range protocol, no graded level or noise-floor "
            "strata and no local listening or benchmark result; it is used only "
            "as evaluation context and never to rank gain or dynamics methods."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Static and whole-file level normalization: RMS target gain and loudness target",
        "components": [
            "static-target-gain-with-peak-ceiling",
            "ridge-static-gain",
            "ebu-r128-ffmpeg-loudnorm",
        ],
        "gap_ids": ["G01", "G02", "G04"],
        "status": "synthetic_local_references_only_no_real_cohort_or_standard_meter",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Envelope and automatic gain control: attack/release AGC and bounded adaptive digital gain",
        "components": [
            "envelope-agc",
            "speex-agc-and-activity-output",
            "webrtc-agc-agc2",
        ],
        "gap_ids": ["G03", "G05", "G06"],
        "status": "local_synthetic_agc_references_webrtc_candidate_considered_only",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Feed-forward compression and full-band dynamic-range control",
        "components": [
            "feed-forward-compressor",
            "full-band-receive-drc-control",
        ],
        "gap_ids": ["G01", "G06", "G07"],
        "status": "synthetic_local_references_only_no_live_preference_result",
    },
    {
        "family_id": "MF-C4",
        "branch": "classic",
        "family": "Peak limiting and true-peak ceiling",
        "components": [
            "peak-limiter-reference",
            "native-zero-latency-sample-peak-limiter",
        ],
        "gap_ids": ["G02", "G07", "G08"],
        "status": "sdk_source_local_python_reference_and_pro_native_source_no_parity",
    },
    {
        "family_id": "MF-C5",
        "branch": "classic",
        "family": "Auditory-model multiband compression and noise-aware shaping plus dynamics",
        "components": [
            "adaptdrc-ssdrc",
            "noise-aware-shaping-plus-drc",
        ],
        "gap_ids": ["G05", "G07"],
        "status": "catalogued_or_research_control_no_local_candidate_execution",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Learned joint speech enhancement and loudness control",
        "components": ["se-agcnet"],
        "gap_ids": ["G05"],
        "status": "catalogued_only_no_source_checkpoint_runtime_or_execution",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Learned multiband dynamics and neural parametric equalization",
        "components": [
            "self-supervised-neural-multiband-eq-and-dynamics",
            "differentiable-biquad-neural-parametric-eq",
        ],
        "gap_ids": ["G05", "G07"],
        "status": "catalogued_only_paper_level_leads_not_installed_or_pinned",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Trainable dynamic-compression feature frontend (adjacent CLN-10/DET-01 boundary)",
        "components": ["pcen-feature-frontend"],
        "gap_ids": ["G05"],
        "status": "catalogued_only_feature_frontend_not_a_waveform_loudness_controller",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "static-target-gain-with-peak-ceiling", "evidence_status": "evaluated", "task": "SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING"},
    {"component_id": "ridge-static-gain", "evidence_status": "evaluated", "task": "SDK-RIDGE-STATIC-GAIN"},
    {"component_id": "envelope-agc", "evidence_status": "partial", "task": "SDK-ENVELOPE-AGC"},
    {"component_id": "speex-agc-and-activity-output", "evidence_status": "partial", "task": "SDK-SPEEX-AGC-AND-ACTIVITY-OUTPUT"},
    {"component_id": "webrtc-agc-agc2", "evidence_status": "considered", "task": "SDK-WEBRTC-AGC-AGC2"},
    {"component_id": "feed-forward-compressor", "evidence_status": "partial", "task": "SDK-FEED-FORWARD-COMPRESSOR"},
    {"component_id": "full-band-receive-drc-control", "evidence_status": "evaluated", "task": "SDK-FULL-BAND-RECEIVE-DRC-CONTROL"},
    {"component_id": "peak-limiter-reference", "evidence_status": "source-local", "task": "SDK-PEAK-LIMITER-REFERENCE"},
    {"component_id": "native-zero-latency-sample-peak-limiter", "evidence_status": "source-local", "task": "PRO-NATIVE-ZERO-LATENCY-SAMPLE-PEAK-LIMITER"},
    {"component_id": "ebu-r128-ffmpeg-loudnorm", "evidence_status": "partial", "task": "SDK-EBU-R128-FFMPEG-LOUDNORM"},
    {"component_id": "adaptdrc-ssdrc", "evidence_status": "considered", "task": "SDK-ADAPTDRC-SSDRC"},
    {"component_id": "noise-aware-shaping-plus-drc", "evidence_status": "evaluated", "task": "SDK-NOISE-AWARE-SHAPING-PLUS-DRC"},
    {"component_id": "se-agcnet", "evidence_status": "considered", "task": "SDK-SE-AGCNET"},
    {"component_id": "self-supervised-neural-multiband-eq-and-dynamics", "evidence_status": "considered", "task": "SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS"},
    {"component_id": "differentiable-biquad-neural-parametric-eq", "evidence_status": "considered", "task": "SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ"},
    {"component_id": "pcen-feature-frontend", "evidence_status": "considered", "task": "SDK-PCEN-FEATURE-FRONTEND"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Frozen synthetic 16 kHz mono fixtures at the 160-sample v0 grid: chirps, level steps, impulses, silence, harmonic/formant speech surrogates, clipped and overloaded transients",
        "class": "historical_local_synthetic_fixture",
        "source_pin": "docs/task-evidence/static-target-gain-with-peak-ceiling/fixtures/report.json",
        "boundary": "Seeded synthetic stimuli only; no real speech, corpus, device capture, room or listening result.",
    },
    {
        "id": "CI-2",
        "input": "743 EARS recordings with synthetic gain steps and a 30-pair DNS2020 noisy extension for AGC level tracking",
        "class": "historical_local_recorded_research_screen",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Recorded research screen without clean references; SI-SDR/STOI declines are reported, no natural microphone acceptance or listening result exists.",
    },
    {
        "id": "CI-3",
        "input": "Thirty 10-second EARS excerpts normalized by FFmpeg 7.1 two-pass loudnorm at -23 LUFS, LRA 7 and -1 dBTP",
        "class": "historical_local_recorded_research_screen",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Self-measured by the same filter; no independent BS.1770/EBU Mode meter, EBU test set or complete programme is available, and FFmpeg is absent from this worktree.",
    },
    {
        "id": "CI-4",
        "input": "Synthetic gain-law tracking and noisy DNS2020 ramp screen for the research dynamic-range compressor",
        "class": "historical_local_synthetic_fixture",
        "source_pin": "research/level_tone_control_20261028.md",
        "boundary": "Synthetic controls only; no live speech preference, MOS, loudness-standard or chain-order result.",
    },
    {
        "id": "CI-5",
        "input": "Synthetic task-local R128 loudness-target fixture with a 2.5-second paired clean signal and an explicit EBU R128 / BS.1770-style estimator",
        "class": "historical_local_synthetic_fixture",
        "source_pin": "docs/task-evidence/ebu-r128-ffmpeg-loudnorm/report.json",
        "boundary": "Minimal Python reference, not an FFmpeg wrapper and not a standards meter; no EBU test set or independent meter is present.",
    },
    {
        "id": "CI-6",
        "input": "WebRTC AGC2, FFmpeg loudnorm, limiter and compressor documentation plus the DSP acceptance profile",
        "class": "source_only_frozen_protocol",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation and profile text only; no pinned source revision, binary, build string or runtime is staged in this task.",
    },
    {
        "id": "CI-7",
        "input": "EBU R128 / BS.1770 / EBU Mode loudness and true-peak measurement protocol with the EBU loudness test set",
        "class": "source_only_frozen_protocol",
        "source_pin": "research/level_tone_control_20261028.md",
        "boundary": "Protocol and dataset documentation only; no test set, licensed meter or standards-conformance measurement is staged.",
    },
    {
        "id": "CI-8",
        "input": "Rights-qualified paired level/loudness cohort with clean references, graded level trajectories, noise-floor and pause cases, clipped/overloaded inputs, known device gain and device colouration",
        "class": "missing_no_local_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Explicitly missing; the registry requires clipping and noise amplification to be tracked as separate subcases.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "identity passthrough", "role": "Bit-exact baseline on speech-like, silence and impulse stimuli; any gain stage must be compared against it.", "source_pin": "docs/task-evidence/envelope-agc/fixtures/report.json"},
    {"id": "CT-2", "name": "fixed and energy-matched static gain", "role": "Non-adaptive level control separated from target convergence and loudness-standard claims.", "source_pin": "docs/task-evidence/ridge-static-gain/report.json"},
    {"id": "CT-3", "name": "direct RMS/gain-law oracle", "role": "Deterministic dB rule or ideal gain law; a learned or adaptive stage must beat it before selection.", "source_pin": "research/level_tone_control_20261028.md"},
    {"id": "CT-4", "name": "silence floor and pause bypass", "role": "Undefined RMS must fall back to identity, and pauses must not be raised toward the target.", "source_pin": "docs/task-evidence/static-target-gain-with-peak-ceiling/fixtures/report.json"},
    {"id": "CT-5", "name": "clipped and overloaded input with peak ceiling", "role": "Pre-clipped and near-clip probes with an explicit ceiling; clipping counts and output peaks are reported, not hidden.", "source_pin": "docs/task-evidence/full-band-receive-drc/report.json"},
    {"id": "CT-6", "name": "hard-clip degraded anchor", "role": "A deliberately degraded control for load/intelligibility-shaped envelope proxies; never a listening or STOI substitute.", "source_pin": "docs/task-evidence/peak-limiter-reference/fixtures/report.json"},
    {"id": "CT-7", "name": "chain-order and interacting-nonlinear control", "role": "AGC, compressor and limiter ordering is exercised so smoothing, ceiling and gain-law interactions are observable.", "source_pin": "docs/task-evidence/envelope-agc/fixtures/report.json"},
    {"id": "CT-8", "name": "predicted or proxy versus human separation", "role": "Envelope correlation, windowed RMS error and gain-law RMSE are developer proxies, never STOI, MOS or preference ratings.", "source_pin": "docs/task-evidence/peak-limiter-reference/fixtures/report.json"},
    {"id": "CT-9", "name": "same-filter measurement versus independent meter", "role": "FFmpeg loudnorm self-measurement is labelled self-measured; an independent BS.1770/EBU Mode meter is a separate gate.", "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Frozen synthetic stimuli and per-case reports for static gain, envelope AGC, compressor, receive DRC, peak limiter and R128 fixtures",
        "class": "sdk_task_local_synthetic",
        "status": "Pinned metadata and canonical reports only; media is generated deterministically inside each task and nothing is pooled or redistributed",
        "source_pin": "docs/task-evidence/static-target-gain-with-peak-ceiling/fixtures/report.json",
    },
    {
        "asset": "Vendored SpeexDSP 1.2.1 preprocessor used by the Speex AGC + advisory activity reference",
        "class": "sdk_vendored_source",
        "status": "Exact vendored source pinned by merged evidence; opt-in build option OFF, unregistered and developer-only",
        "source_pin": "docs/task-evidence/speex-agc-and-activity-output/evidence/report.json",
    },
    {
        "asset": "Native zero-latency sample-peak limiter source in audio-pro",
        "class": "pro_native_source",
        "status": "Source-local only; no local SDK execution, cohort, parity, listening or rights clearance",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
    },
    {
        "asset": "EARS recordings and DNS2020 noisy pairs used by the historical AGC/DRC research screens",
        "class": "local_research_corpus",
        "status": "Research metadata only; media is not staged here, no clean references are available and rights are not cleared for release",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
    },
    {
        "asset": "FFmpeg 7.1 toolchain for EBU R128 two-pass loudnorm",
        "class": "missing_external_tool",
        "status": "Absent from this worktree; no exact version/configuration output, GPL dependency build string or invocation is captured",
        "source_pin": "research/level_tone_control_20261028.md",
    },
    {
        "asset": "WebRTC AGC2 source and runtime",
        "class": "missing_external_source",
        "status": "Not pinned or staged; only interface documentation is reviewed and no parity is claimed",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "SE-AGCNet, AdaptDRC/SSDRC, self-supervised multiband dynamics and neural parametric EQ checkpoints",
        "class": "missing_model_assets",
        "status": "No exact code, checkpoint, licence or runtime verified; considered only and never installed",
        "source_pin": "research/level_tone_control_20261028.md",
    },
    {
        "asset": "Rights-qualified paired level/loudness cohort with device gain and clean references",
        "class": "missing_no_local_cohort",
        "status": "Not present; the category remains catalogued with candidate census and benchmark not_started",
        "source_pin": "audio_categories.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Static target-RMS gain with hard peak ceiling on synthetic level stimuli",
        "outcome_class": "historical_local_synthetic_fixture",
        "component_ids": ["static-target-gain-with-peak-ceiling"],
        "source_pin": "docs/task-evidence/static-target-gain-with-peak-ceiling/fixtures/report.json",
        "values": {
            "fixture_samples": 6400,
            "frame_samples": 160,
            "target_dbfs": -24.0,
            "ceiling_dbfs": -1.0,
            "min_gain_db": -18.0,
            "max_gain_db": 18.0,
            "silence_floor_dbfs": -50.0,
            "content_delay_samples": 0,
            "lookahead_samples": 0,
            "ceiling_sweep_points": 6,
            "interaction_configurations": 6,
            "nonfinite_count": 0,
        },
        "scope": "Deterministic synthetic 16 kHz mono fixture with chirps, steps, impulses, silence and speech-like surrogates; no real speech, corpus, device gain, listening or loudness-standard result; not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Ridge static-gain synthetic held-out screen with envelope-AGC and direct-rule controls",
        "outcome_class": "historical_local_synthetic_fixture",
        "component_ids": ["ridge-static-gain", "static-target-gain-with-peak-ceiling"],
        "source_pin": "docs/task-evidence/ridge-static-gain/report.json",
        "values": {
            "train_clips": 180,
            "held_out_clips": 60,
            "envelope_agc_mean_abs_rms_error_db": 0.561937,
            "target_rms_mean_abs_rms_error_db": 2.290003,
            "ridge_mean_abs_rms_error_db": 4.234889,
            "no_gain_mean_abs_rms_error_db": 17.213793,
            "ridge_slope": -1.177793,
            "ridge_intercept": -1.681723,
            "nonfinite_samples": 0,
        },
        "scope": "Train and held-out splits are both synthetic harmonic/formant signals; the ridge model is worse than the direct rule it approximates; no real speech, listening or model-selection claim; not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Envelope AGC synthetic fixture with ceiling and interacting-nonlinear controls",
        "outcome_class": "historical_local_synthetic_fixture",
        "component_ids": ["envelope-agc"],
        "source_pin": "docs/task-evidence/envelope-agc/fixtures/report.json",
        "values": {
            "cases": 12,
            "interaction_configurations": 7,
            "distinct_interaction_outputs": 6,
            "agc_only_clipped_samples": 212,
            "agc_then_limiter_clipped_samples": 0,
            "windowed_rms_abs_error_db_agc": 10.646285748430714,
            "windowed_rms_abs_error_db_identity": 4.447048889694933,
            "content_delay_samples": 0,
            "lookahead_samples": 0,
            "nonfinite_output_count": 0,
        },
        "scope": "Deterministic synthetic AGC at 10 ms attack, 250 ms release, -18/+18 dB bounds, -24 dBFS target and 8 Hz gain smoothing; gain-step tracking was worse than identity and no listening or real-speech result exists; not rerun by this survey.",
    },
    {
        "id": "HE-4",
        "label": "Feed-forward compressor synthetic amplitude and frequency sweep",
        "outcome_class": "historical_local_synthetic_fixture",
        "component_ids": ["feed-forward-compressor"],
        "source_pin": "docs/task-evidence/feed-forward-compressor/report.json",
        "values": {
            "sweep_points": 100,
            "frequency_points": 39,
            "gain_law_rmse_db": 1.024914,
            "identity_rmse_db": 12.82719,
            "config_rejections": 18,
            "state_unchanged_after_all_rejects": True,
        },
        "scope": "Causal envelope detector, symmetric attack/release and static gain law at threshold -24 dBFS, ratio 4, 5 ms attack and 120 ms release; synthetic only, no lookahead, side-chain, model or listening result; not rerun by this survey.",
    },
    {
        "id": "HE-5",
        "label": "Full-band receive DRC synthetic gain, headroom and attack/release measurements",
        "outcome_class": "historical_local_synthetic_fixture",
        "component_ids": ["full-band-receive-drc-control"],
        "source_pin": "docs/task-evidence/full-band-receive-drc/report.json",
        "values": {
            "clean_speech_rms_gain_db": -0.286749,
            "clean_speech_peak_gain_db": -1.664257,
            "clean_speech_correlation": 0.98725,
            "headroom_to_ceiling_db": 9.546497,
            "near_clip_peak_reduction_db": -7.694893,
            "preclipped_peak_reduction_db": -8.725883,
            "measured_attack_ms": 16.1875,
            "measured_release_ms": 165.75,
            "content_delay_samples": 0,
            "regression_count": 16,
        },
        "scope": "Causal soft-knee full-band compressor at threshold -18 dB, ratio 3, ceiling 0.95 with optional limiter OFF by default; synthetic speech-like and analytic fixtures only, no listening or device timing; not rerun by this survey.",
    },
    {
        "id": "HE-6",
        "label": "Peak limiter reference synthetic clean-speech, impulse and nonfinite probes",
        "outcome_class": "historical_local_synthetic_fixture",
        "component_ids": ["peak-limiter-reference"],
        "source_pin": "docs/task-evidence/peak-limiter-reference/fixtures/report.json",
        "values": {
            "ceiling": 0.98,
            "release_ms": 50.0,
            "clean_speech_peak_in": 1.1070142984390259,
            "clean_speech_peak_out": 0.9800000190734863,
            "clean_speech_engaged_frames": 4,
            "clean_speech_fast_path_frames": 6,
            "impulse_engaged_frames": 66,
            "content_delay_samples": 0,
            "lookahead_samples": 0,
            "nonfinite_input_count": 2,
            "nonfinite_output_count": 0,
        },
        "scope": "Task-local Python model of a documented zero-lookahead limiter with per-sample ceiling/peak gain and one-pole release; the nonfinite probe records C++ std::min/std::max ordering as observed behavior, not a quality claim; not rerun by this survey.",
    },
    {
        "id": "HE-7",
        "label": "EBU R128 / loudnorm-style static loudness target on a synthetic paired fixture",
        "outcome_class": "historical_local_synthetic_fixture",
        "component_ids": ["ebu-r128-ffmpeg-loudnorm"],
        "source_pin": "docs/task-evidence/ebu-r128-ffmpeg-loudnorm/report.json",
        "values": {
            "fixture_samples": 40000,
            "frames": 250,
            "input_lufs": -33.846402,
            "output_lufs": -23.0,
            "target_error_lu": 0.0,
            "loudness_gain": 3.485942,
            "lra_estimate": 2.269318,
            "input_true_peak_dbtp": -17.16632,
            "output_true_peak_dbtp": -6.319918,
            "true_peak_headroom_db": 5.319918,
            "at_or_above_one_count": 0,
        },
        "scope": "Minimal Python offline loudness analyzer plus static-gain frame adapter on a 2.5-second synthetic paired fixture; not FFmpeg, not a BS.1770/EBU Mode meter, no EBU test set, LRA target not enforced; not rerun by this survey.",
    },
    {
        "id": "HE-8",
        "label": "Speex AGC with advisory activity output on synthetic native fixtures",
        "outcome_class": "historical_local_synthetic_fixture",
        "component_ids": ["speex-agc-and-activity-output"],
        "source_pin": "docs/task-evidence/speex-agc-and-activity-output/evidence/report.json",
        "values": {
            "cases": 23,
            "repeats": 3,
            "agc_gain_min_db_steps": -7,
            "agc_gain_max_db_steps": 17,
            "agc_gain_max_db_impulse": 23,
            "identity_speech_peak_abs": 0.435272,
            "max_peak_abs": 0.85556,
            "clipped_or_at_one": 0,
            "nonfinite_count": 0,
        },
        "scope": "One vendored SpeexDSP preprocessor per stream at 16 kHz with AGC ON and VAD advisory only; gain trajectory is byte-identical with the VAD flag and the activity output never gates audio; synthetic only, no real speech, listening or device result; not rerun by this survey.",
    },
    {
        "id": "HE-9",
        "label": "Historical AGC gain-step screen on 743 EARS recordings with a noisy DNS2020 extension",
        "outcome_class": "historical_local_recorded_research_screen",
        "component_ids": ["envelope-agc"],
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "values": {
            "clips": 743,
            "synthetic_gain_step_db": 9,
            "noisy_pairs": 30,
            "noisy_rms_error_improvement_db": 2.319,
            "noisy_si_sdr_delta_db": -0.982,
            "clipped_samples": 0,
        },
        "scope": "Recorded EARS audio with synthetic gain steps and a 30-pair DNS2020 noisy extension; level error improved while SI-SDR/STOI declined, with no clean reference, natural microphone capture, listening or live acceptance; not rerun by this survey.",
    },
    {
        "id": "HE-10",
        "label": "Historical FFmpeg 7.1 two-pass loudnorm screen on 30 EARS excerpts",
        "outcome_class": "historical_local_recorded_research_screen",
        "component_ids": ["ebu-r128-ffmpeg-loudnorm"],
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "values": {
            "excerpts": 30,
            "excerpt_seconds": 10.0,
            "target_lufs": -23.0,
            "target_lra": 7.0,
            "true_peak_cap_dbtp": -1.0,
            "within_0_2_lu": 29,
            "meet_true_peak_cap": 30,
            "independent_ebu_meter": False,
        },
        "scope": "Offline mastering screen self-measured by the same filter; no independent BS.1770/EBU Mode meter, EBU test set, complete programme or live-enhancement result exists, and FFmpeg is absent from this worktree; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "S27 documents WebRTC audio processing with adaptive digital gain followed by a limiter, configurable headroom and bounded gain changes",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Interface documentation only; no pinned WebRTC source revision, binary, build string, runtime, descriptor or local parity result is staged.",
    },
    {
        "id": "RO-2",
        "claim": "S19 documents FFmpeg EBU R128 integrated loudness, loudness range, true-peak control, lookahead limiting and compressor/limiter filters",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Filter documentation only; the local references are explicit Python models and are not claimed to reproduce FFmpeg or any standard.",
    },
    {
        "id": "RO-3",
        "claim": "S46 reports Speech Signal Improvement challenge findings for enhancement evaluation",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Search-excerpt context only; it supplies no loudness/dynamic-range protocol, cohort or local result and is never used to rank methods.",
    },
    {
        "id": "RO-4",
        "claim": "SE-AGCNet reports jointly trained speech enhancement and loudness control with a GPU-oriented runtime and bundled pretrained checkpoints",
        "class": "source_reported",
        "source_pin": "research/level_tone_control_20261028.md",
        "boundary": "Upstream project claim; not installed, pinned or executed, and no checkpoint, licence, hardware or input/output contract is verified.",
    },
    {
        "id": "RO-5",
        "claim": "Neural parametric EQ with differentiable biquads and a self-supervised multiband EQ-plus-dynamics processor are published learned tone/dynamics families",
        "class": "source_reported",
        "source_pin": "research/level_tone_control_20261028.md",
        "boundary": "Paper-level leads; no code, checkpoint, runtime, rights or local measurement exists, and tone correction belongs to CLN-10.",
    },
    {
        "id": "RO-6",
        "claim": "A native zero-latency sample-peak limiter stage exists in the private audio-pro source tree",
        "class": "source_reported",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Inventory record only; no local SDK execution, reference parity, cohort, listening or release clearance exists, and the private implementation is not copied.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "sweeps": "CI-1 / HE-4; synthetic chirps and frequency sweeps, response summaries are not a linear transfer function",
        "steps": "CI-1 / HE-3 / HE-5; level-step tracking and attack/release windows",
        "impulses": "CI-1 / HE-1 / HE-6; content delay and zero-lookahead mapping",
        "silence": "CI-1 / CT-4; silence floor and identity fallback instead of infinite gain",
        "clean_speech": "CI-1 synthetic speech-like surrogate with identity control; no real clean speech",
        "intelligibility_or_load_control": "CT-6 / CT-8; hard-clip anchor and envelope correlation proxy, never STOI or listening",
        "gain": "HE-1..HE-8; static, adaptive and bounded gain with identity and fixed-gain controls",
        "response": "HE-4 / HE-5; gain-law RMSE and band summaries on synthetic stimuli",
        "attack_release": "HE-3 / HE-5; measured 10/250 ms configured and 16.1875/165.75 ms observed windows",
        "headroom": "HE-1 / HE-5 / HE-6 / HE-7; explicit ceilings, clipped counts and true-peak headroom",
        "delay": "HE-1 / HE-3 / HE-6; zero content delay and zero lookahead in the reviewed fixtures",
        "numerical_behavior": "HE-4..HE-8; nonfinite rejection, state-unchanged and finite-output probes",
        "state_transitions": "HE-3 / HE-5 / HE-8; reset, epoch and session-isolation probes",
        "interacting_nonlinear_configurations": "HE-3 / HE-5 / CT-7; AGC, compressor and limiter chain orders",
    },
    "blocked": [
        "Rights-qualified paired level/loudness cohort with clean references, graded level trajectories, pause and clipping strata",
        "Independent BS.1770/EBU Mode loudness and true-peak meter plus EBU test-set conformance",
        "Pinned WebRTC AGC2 and FFmpeg source/version/config parity with exact runtime identity",
        "Authorized listening, speech-quality and intelligibility acceptance including noise amplification during pauses",
        "Measured gain slew, pumping, attack/release and chain-order behavior on a pinned native chain",
        "Target-device pacing, latency, CPU, memory and deadline evidence on the 160-sample grid",
        "Opt-in provider intake, descriptor/registry review and explicit public default selection approval",
        "Release approval and independent exact-head review",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "synthetic_historical_local": True,
    "recorded_research_pilot_historical_local": True,
    "source_reported_documentation": True,
    "human_listening_result": False,
    "independent_heldout_benchmark": False,
    "loudness_standard_conformance": False,
    "device_gain_control_or_loop": False,
    "target_device_timing": False,
    "real_speech_rights_qualified": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "release_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Acquire a rights-qualified paired level/loudness cohort with clean references, graded level trajectories, noise-floor and pause cases, clipped/overloaded inputs and known device gain",
        "evidence_gap": "Only synthetic fixtures and a recorded AGC research screen without clean references are reviewed; no independent paired cohort, device gain capture or natural microphone material is staged.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-09 feasibility row was found for cohort acquisition; the research-control manifest and foundation intake rows own evidence and asset rules, not a recorded level/dynamics cohort.",
    },
    {
        "id": "G02",
        "actionable_gap": "Pin an independent BS.1770/EBU Mode loudness and true-peak meter and freeze the EBU R128 measurement protocol before any loudness claim",
        "evidence_gap": "The local R128 fixture is a minimal Python estimator and the historical FFmpeg screen was self-measured by the same filter; no licensed meter, EBU test set or conformance run exists.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-09 metering feasibility row was found; the foundation evidence row owns reproducible conformance rules, not a licensed standards meter.",
    },
    {
        "id": "G03",
        "actionable_gap": "Pin WebRTC AGC2 source and runtime at an exact revision and establish adaptive-digital-gain plus limiter parity, including bounded gain changes and headroom",
        "evidence_gap": "S27 is interface documentation only; no WebRTC source tree, build string, binary, descriptor or local AGC2 measurement is staged.",
        "follow_up_ids": [
            "SDK-WEBRTC-AGC-AGC2",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The WebRTC AGC/AGC2 feasibility row is a candidate-discovery lead only; no source, runtime or quality result is created by this map.",
    },
    {
        "id": "G04",
        "actionable_gap": "Capture FFmpeg version/config/build string and run a task-matched loudnorm and limiter baseline under an approved licence",
        "evidence_gap": "FFmpeg is absent from this worktree; no exact version, configuration output, GPL dependency build string, synthetic two-pass invocation or independent meter is recorded here.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-FND-PROVIDER",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-09 FFmpeg parity row was found in an allowed link mode; the EBU R128 implementation row is implementation-mode and the foundation rows own provenance and provider-boundary rules.",
    },
    {
        "id": "G05",
        "actionable_gap": "Verify source, checkpoint, licence and runtime for learned gain/dynamics candidates (SE-AGCNet, AdaptDRC/SSDRC, self-supervised multiband dynamics, neural parametric EQ)",
        "evidence_gap": "All learned candidates are considered; no exact code, checkpoint, per-weight rights, runtime or measurement is verified, and PCEN is a feature frontend rather than a waveform controller.",
        "follow_up_ids": [
            "SDK-SE-AGCNET",
            "SDK-ADAPTDRC-SSDRC",
            "SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "All linked feasibility rows are discovery leads only; no candidate is installed, enabled, pooled into CLN-10 or promoted by this map.",
    },
    {
        "id": "G06",
        "actionable_gap": "Run authorized listening, speech-quality and intelligibility acceptance that tracks noise amplification during pauses and pumping, not only level error",
        "evidence_gap": "Envelope correlation and windowed RMS error are developer proxies; the recorded AGC screen shows SI-SDR/STOI declines and no human rating, preference or playback clearance exists.",
        "follow_up_ids": [
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-STOI-ESTOI",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-09 listening feasibility row was found; the research-control rows own protocol, preservation screening and objective scoring, not a listening result.",
    },
    {
        "id": "G07",
        "actionable_gap": "Measure gain-slew, pumping, attack/release and chain-order interaction on a pinned native chain rather than Python static chaining",
        "evidence_gap": "Interacting configurations are exercised only through task-local Python adapters; there is no matched native chain, production configuration or release gate.",
        "follow_up_ids": [
            "SDK-NOISE-AWARE-SHAPING-PLUS-DRC",
            "SDK-FND-GRAPH",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-09 chain feasibility row was found; the research-control and ordered-chain foundation rows own shaping and composition, not a measured native chain.",
    },
    {
        "id": "G08",
        "actionable_gap": "Measure target-device pacing, deadline, CPU and memory for causal streaming gain control on the 160-sample grid",
        "evidence_gap": "No target-device deadline, RTF, memory or thermal evidence exists for any reviewed implementation; only deterministic offline Python or private scratch native runs are recorded.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-DUPLEX",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-09 timing feasibility row was found; the foundation rows own lifecycle, clock and timing-evidence rules, not a paced device measurement.",
    },
    {
        "id": "G09",
        "actionable_gap": "Complete opt-in provider intake, descriptor/registry review and explicit public default selection before any exposure",
        "evidence_gap": "Every reviewed implementation is unregistered, OFF by default and carries empty descriptor settings; no intake review, catalog approval or default decision exists.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-FND-PROVIDER",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-09 exposure feasibility row was found; the foundation rows own provider intake, build fragments and asset-boundary rules, not a default selection.",
    },
    {
        "id": "G10",
        "actionable_gap": "Separate capture gain, digital leveling, whole-file normalization and limiting into independently measured subcases with an explicit device-gain contract",
        "evidence_gap": "The registry requires these to be separate subcases, but only digital leveling, offline normalization and limiting have synthetic fixtures; no capture or device gain control is measured.",
        "follow_up_ids": [
            "SDK-FND-DUPLEX",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-09 device-gain feasibility row was found; the foundation rows own reference/clock contracts and evidence rules, not a device gain-control measurement.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-STOI-ESTOI", "title": "STOI / ESTOI", "mode": "research-control"},
    {"task_id": "SDK-NOISE-AWARE-SHAPING-PLUS-DRC", "title": "Noise-aware shaping plus DRC", "mode": "research-control"},
    {"task_id": "SDK-WEBRTC-AGC-AGC2", "title": "WebRTC AGC / AGC2", "mode": "feasibility"},
    {"task_id": "SDK-ADAPTDRC-SSDRC", "title": "AdaptDRC / SSDRC", "mode": "feasibility"},
    {"task_id": "SDK-SE-AGCNET", "title": "SE-AGCNet", "mode": "feasibility"},
    {"task_id": "SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS", "title": "Self-supervised neural multiband EQ and dynamics", "mode": "feasibility"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-DUPLEX", "title": "Reference, multichannel and clock contracts", "mode": "foundation"},
    {"task_id": "SDK-FND-GRAPH", "title": "Public ordered chain reference executor", "mode": "foundation"},
    {"task_id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified paired level/loudness cohort with clean references, graded level trajectories, pause and clipping strata plus capture/device gain evidence"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent BS.1770/EBU Mode loudness and true-peak meter with EBU test-set conformance; self-measurement alone is insufficient"},
    {"id": "RG-03", "blocked": True, "requirement": "Pinned WebRTC AGC2 and FFmpeg source revision, build/configuration and runtime parity with exact settings"},
    {"id": "RG-04", "blocked": True, "requirement": "Authorized listening, speech-quality and intelligibility acceptance including noise amplification during pauses and pumping"},
    {"id": "RG-05", "blocked": True, "requirement": "Measured gain slew, attack/release, pumping and chain-order behavior on a pinned native chain"},
    {"id": "RG-06", "blocked": True, "requirement": "Target-device pacing, latency, CPU, memory and deadline evidence on the 160-sample grid"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider intake, descriptor/registry review and explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-09 \u2014 Gain, loudness and dynamic-range control** | Keep speech audible and manage peaks.",
        "| **CLN-10 \u2014 Tonal correction and interference filtering** |",
    ],
    "research/category_survey/sources.md": [
        "| S19 | [FFmpeg audio filters](https://ffmpeg.org/ffmpeg-filters.html) | acoustics | direct |",
        "| S27 | [WebRTC audio processing interface](https://webrtc.googlesource.com/src/+/refs/heads/main/api/audio/audio_processing.h) | acoustics | direct |",
        "| S46 | [Speech Signal Improvement challenge findings](https://www.microsoft.com/en-us/research/publication/icassp-2024-speech-signal-improvement-challenge-2/) | root | search excerpt |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| DSP | Use sweeps, steps, impulses, silence, clean speech and an intelligibility or load-specific control. Measure gain, response, attack/release where applicable, headroom, delay and numerical behavior. Capture state transitions and interacting nonlinear configurations. |",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "| Envelope AGC | Automatic gain control | Causal attack/release implementation; tested on synthetic gain changes and a noisy DNS extension. SI-SDR declined in the noisy extension despite improved short-window level error. |",
        "| Static target gain with peak ceiling | Level normalization | Locally implemented and evaluated on synthetic level changes. Use only with a defined target and guard against raising noise during pauses. |",
        "| Dynamic-range compressor | Speech dynamics control | Local causal reference implementation; synthetic gain-law RMSE 2.613 dB vs 5.795 dB for identity, batch RTF 0.000408. No live preference evaluation. |",
    ],
    "research/level_tone_control_20261028.md": [
        "- Static RMS target gain with a configurable peak ceiling.",
        "The static model's zero error is expected: its target is a deterministic function of the measured RMS, so a direct gain calculation is the preferable solution.",
        "Before ranking candidates, create a frozen paired set with clean speech, independent level trajectories, noise-floor cases, clipped/overloaded cases, known device EQ coloration, hum/rumble examples, and untouched controls.",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "Expanded controlled gain-step screen on all 743 EARS clips",
        "RMSE 2.613 dB vs 5.795 identity",
        "29/30 within",
    ],
    "research/task_backlog.json": [
        "{\"activation_state\":\"catalogued\",\"blockers\":[],\"category_id\":\"CLN-09\",\"dependencies\":[],\"family_id\":\"F09\"",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/ridge-static-gain/README.md": [
        "Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for",
    ],
    "docs/task-evidence/envelope-agc/README.md": [
        "**Status: proposal-only, synthetic, developer-only, optional/unregistered.",
    ],
    "docs/task-evidence/feed-forward-compressor/README.md": [
        "**Status: proposal-only / synthetic; `incomplete` where real qualification is",
    ],
    "docs/task-evidence/full-band-receive-drc/README.md": [
        "This directory contains **proposal-only, incomplete, not-qualified** evidence for",
    ],
    "docs/task-evidence/peak-limiter-reference/README.md": [
        "**SDK-PEAK-LIMITER-REFERENCE \u00b7 DSP acceptance profile \u00b7 status: opt-in,",
    ],
    "docs/task-evidence/static-target-gain-with-peak-ceiling/README.md": [
        "Real-speech, listening, loudness-standard, native-provider, target-device and",
    ],
    "docs/task-evidence/ebu-r128-ffmpeg-loudnorm/README.md": [
        "**minimal Python reference**, not an FFmpeg wrapper, not a BS.1770/EBU Mode",
    ],
    "docs/task-evidence/speex-agc-and-activity-output/README.md": [
        "A **deterministic, synthetic, opt-in developer reference**, not a product AGC,",
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
    "real_echo_audio": False,
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
    "loudness_conformance_claim_without_standards_meter": "rejected; state unchanged",
    "device_gain_claim_without_device_measurement": "rejected; state unchanged",
    "listening_or_quality_claim_without_ratings": "rejected; state unchanged",
    "release_or_parity_claim_without_pinned_provider": "rejected; state unchanged",
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
        raise MapError("CLN-09 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-09 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F09 / CLN-09 is not unique")
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
            raise MapError("legacy backlog mismatch: F09/CLN-09/%s" % key)


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
    known = {row["component_id"] for row in COMPONENT_CENSUS}
    as_sources = {c for lead in SOURCE_LEADS for c in lead["mapped_components"]}
    missing = sorted(mapped - set(by_id))
    if missing:
        raise MapError("mapped component missing from inventory: " + ",".join(missing))
    uncensused = sorted(as_sources - known)
    if uncensused:
        raise MapError("source lead maps an uncensused component: " + ",".join(uncensused))


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
        if "not rerun by this survey" not in row.get("scope", ""):
            raise MapError("historical execution is not labelled not-rerun: " + row["id"])


def _check_evidence_classes() -> None:
    classes = {row["class"] for row in COMPARISON_INPUTS}
    outcome_classes = {row["outcome_class"] for row in HISTORICAL_EXECUTIONS}
    checks = {
        "synthetic_historical_local": "historical_local_synthetic_fixture" in classes
        and "historical_local_synthetic_fixture" in outcome_classes,
        "recorded_research_pilot_historical_local": "historical_local_recorded_research_screen"
        in outcome_classes,
        "source_reported_documentation": any(row["class"] == "source_reported" for row in REPORTED_OUTCOMES),
        "human_listening_result": "human_listening_result" in classes,
        "independent_heldout_benchmark": "independent_heldout_benchmark" in classes,
        "loudness_standard_conformance": "independent_standards_conformance" in classes,
        "device_gain_control_or_loop": "device_loop" in classes,
        "target_device_timing": "device_timing" in classes,
        "real_speech_rights_qualified": "rights_qualified_real_speech" in classes,
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in (
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "release_claim",
    ):
        if EVIDENCE_CLASSES[key] is not False:
            raise MapError("unsupported claim is not closed: " + key)
    for row in HISTORICAL_EXECUTIONS:
        if not row.get("values"):
            raise MapError("historical execution has no values: " + row["id"])


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
        "level_boundary": dict(LEVEL_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "gain_and_dynamics_component_ids": [
                "static-target-gain-with-peak-ceiling",
                "ridge-static-gain",
                "envelope-agc",
                "speex-agc-and-activity-output",
                "feed-forward-compressor",
                "full-band-receive-drc-control",
                "peak-limiter-reference",
            ],
            "independent_heldout_test_split_present": False,
            "licensed_public_corpus_staged": False,
            "rights_qualified_real_speech_staged": False,
            "standards_loudness_meter_present": False,
            "pinned_provider_runtime_parity_present": False,
            "neural_weights_present": False,
            "note": "Local synthetic gain, loudness and dynamics references are mapped, but no rights-qualified paired cohort, standards meter, pinned provider parity, listening result or target-device timing is staged; learned candidates remain considered only.",
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
    if any(value is not False for value in report["boundary"].values()):
        raise MapError("boundary is not closed")
    for key in (
        "task_local_only",
        "documentation_and_metadata_only",
        "no_new_execution",
        "synthetic_only_where_cited",
    ):
        if report["scope"][key] is not True:
            raise MapError("scope rule is not enforced: " + key)
    for key in (
        "real_speech",
        "real_corpus",
        "real_echo_audio",
        "weights",
        "runtime_invocation",
        "listening",
        "device_timing",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "processor_exposure",
        "public_default",
        "network_access",
    ):
        if report["scope"][key] is not False:
            raise MapError("scope claim is not closed: " + key)
    for key in (
        "capture_gain_is_not_digital_leveling",
        "digital_leveling_is_not_whole_file_normalization",
        "peak_limiting_is_not_loudness_normalization",
        "streaming_loudness_control_is_not_offline_mastering",
        "clipping_and_noise_amplification_are_tracked",
    ):
        if report["level_boundary"][key] is not True:
            raise MapError("level boundary rule is not enforced: " + key)
    for key in (
        "device_gain_control_contract_measured",
        "loudness_standard_conformance_measured",
        "rights_qualified_paired_cohort_staged",
        "human_listening_result",
        "target_device_timing_measured",
    ):
        if report["level_boundary"][key] is not False:
            raise MapError("level boundary claim is not closed: " + key)
    for key in (
        "independent_heldout_test_split_present",
        "licensed_public_corpus_staged",
        "rights_qualified_real_speech_staged",
        "standards_loudness_meter_present",
        "pinned_provider_runtime_parity_present",
        "neural_weights_present",
    ):
        if report["discovery"][key] is not False:
            raise MapError("discovery claim is not closed: " + key)
    if report["evidence_classes"]["independent_heldout_benchmark"] is not False:
        raise MapError("held-out benchmark is claimed without a test split")
    if report["evidence_classes"]["human_listening_result"] is not False:
        raise MapError("human listening is claimed without ratings")
    if report["evidence_classes"]["loudness_standard_conformance"] is not False:
        raise MapError("loudness conformance is claimed without a standards meter")
    if report["evidence_classes"]["device_gain_control_or_loop"] is not False:
        raise MapError("device gain control is claimed without a device measurement")
    if report["evidence_classes"]["target_device_timing"] is not False:
        raise MapError("device timing is claimed without a device loop")
    if BOARD_PATH in report["source_pins"] or BOARD_PATH in report["boundary_pins"]:
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
