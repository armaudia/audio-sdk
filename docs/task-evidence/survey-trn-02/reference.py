# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence map for SDK-SURVEY-TRN-02.

This module builds a bounded taxonomy/comparison map for the pitch and limited
prosody control category (inventory category ``TRN-02``, legacy family ``F13``).
It reads only pinned, read-only documents from the enclosing ``audioml``
workspace and the SDK worktree. It does not load audio, weights, models,
runtimes, media or the network, and it does not register, expose, enable or
qualify any pitch, formant or prosody processor.

Every historical rate-change F0 figure below is transcribed from a pinned
research report and keeps its original rate-change scope. A rate-change
pitch-preservation proxy is not a designated pitch-shift control, a formant
preservation measurement, a prosody editor or a listening result. The map
therefore never promotes a missing or adjacent result to a TRN-02 outcome.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-TRN-02"
TITLE = "Review coverage for Pitch and limited prosody control"
CATEGORY_ID = "TRN-02"
LEGACY_FAMILY = "F13"
BRANCH = "swarm/SDK-SURVEY-TRN-02"
BASE_COMMIT = "b4ccacaff0e82dbfc027404fbb7ac81d4885f768"
PROFILE = "Voice"
COMPONENT = "pitch-prosody-control-evidence-map"
STATUS = "proposal_only_survey_incomplete"
QUALIFICATION_STATUS = "not_qualified"
READINESS = "incomplete"
DECISION = "DEFER"

ALLOWED_LINK_MODES = (
    "feasibility",
    "research-control",
    "foundation",
    "external-adapter",
    "implementation",
    "taxonomy",
)

# REUSE-IgnoreStart
LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-Identifier: Apache-2.0\n"
)
# REUSE-IgnoreEnd

# Workspace-relative document pins. Every entry is a read-only document or
# metadata ledger consulted by this survey; a pin never grants rights or
# verifies media, weights, transcripts or pitches that are not present in this
# task directory.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "cpp-library/pipeline-validation/playback-speed-candidates.md": "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/tsm-followup-20261101/README.md": "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# SDK-worktree-relative boundary and task-local evidence pins. They are read
# only to prove that no public surface was touched and to ground the cited
# task-local synthetic evidence.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/psola-praat/README.md": "7e64ec614937533168ef31c34d4c8ec4aa7d6d52670e663f0f88ce5f4ec7a6ef",
    "docs/task-evidence/sonic/README.md": "40f2fdcf708a75fbc3e0df296fabfecd296118e6a9eaee67fc34f8dec0e419cb",
    "docs/task-evidence/rubber-band-r3-offline/README.md": "de528246089b9f0d2a1ea597ac0cbbb119d5541b2b22a0a383b4d03b7a85aeab",
    "docs/task-evidence/rubber-band-r3-streaming/README.md": "04583e07678079f1ed179a1b15f50599693a7bc6f6a813237a71d0005d810d97",
    "docs/task-evidence/soundtouch/README.md": "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
    "docs/task-evidence/phase-vocoder-baseline/README.md": "915bd51e7de4b223bdd61bb5ff823e7a0558f03e324f154d7d3d4c77d14f9790",
    "docs/task-evidence/survey-trn-01/README.md": "20503c685e57ba2b6d15a677cfad1ea7e6f22b391010af61bb4fd6dc63ea8972",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Playback and voice transformations",
    "name": "Pitch and limited prosody control",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Modify designated pitch, duration or energy attributes.",
    "method_families": {
        "classic": "Pitch-synchronous overlap-add; source-filter/vocoder processing",
        "ml": "Disentangled neural analysis/resynthesis",
    },
    "input_output": "Audio + pitch/other controls \u2192 modified speech",
    "live_or_comparison_boundary": (
        "Pitch shift, formant preservation and full prosody editing differ. "
        "Emotion manipulation is not added to scope."
    ),
    "source_ids": ["S34", "S35"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "TRN",
    "meaning": "Playback and voice transformations",
    "category_id": CATEGORY_ID,
    "designated_pitch_duration_or_energy_attributes_only": True,
    "pitch_shift_formant_preservation_and_full_prosody_differ": True,
    "emotion_manipulation_out_of_scope": True,
    "rate_change_is_not_designated_pitch_shift": True,
    "f0_distribution_shift_is_not_perceptual_pitch": True,
    "formant_preservation_is_not_a_pitch_shift": True,
    "not_time_scale_modification": "TRN-01",
    "not_accent_conversion": "TRN-03",
    "not_voice_conversion_or_cloning": "boundary",
    "not_emotion_manipulation": "out_of_scope",
    "not_listening_quality_assessment": "OBS-01",
    "not_speech_enhancement": "CLN-01",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S34",
        "title": "WORLD vocoder implementation",
        "url": "https://github.com/mmorise/World",
        "access_scope": "direct",
        "mapped_components": ["world-vocoder"],
        "gap_ids": ["G01", "G04", "G10"],
        "finding": (
            "Direct documentation lead for a source-filter analysis/synthesis "
            "vocoder family that separates F0, spectral envelope and aperiodicity. "
            "The pinned inventory records it as considered with no local execution; "
            "no upstream revision, binary, weight, licence bundle or task-matched "
            "pitch/formant control is present in this task. It is never loaded here."
        ),
    },
    {
        "source_id": "S35",
        "title": "NANSY analysis and resynthesis paper",
        "url": "https://proceedings.neurips.cc/paper_files/paper/2021/file/87682805257e619d49b8e0dfdc14affa-Paper.pdf",
        "access_scope": "direct",
        "mapped_components": ["nansy-analysis-resynthesis", "hifi-gan-vocoder", "vocos-vocoder"],
        "gap_ids": ["G04", "G07", "G08"],
        "finding": (
            "Direct paper lead for disentangled neural analysis/resynthesis with "
            "separate pitch, content and timbre paths. No checkpoint, configuration, "
            "weight terms, decoder runtime or consent-cleared target reference is "
            "staged; the family is documentation-only and no substitute model is used."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": (
            "Pitch-synchronous overlap-add (PSOLA/TD-PSOLA) with pitch marks and "
            "grain repetition or excision"
        ),
        "components": ["psola-praat", "td-psola", "sonic"],
        "gap_ids": ["G02", "G04", "G11"],
        "status": "task_local_rate_fixture_only_no_designated_pitch_shift",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": (
            "Source-filter/vocoder processing and analysis/resynthesis pitch "
            "engines (WORLD lead, phase vocoder, formant-preserving stretcher, "
            "platform rate/pitch unit)"
        ),
        "components": [
            "world-vocoder",
            "phase-vocoder-baseline",
            "rubber-band-r3-offline",
            "rubber-band-r3-streaming",
            "avaudiounittimepitch-rate-pitch-overlap",
        ],
        "gap_ids": ["G01", "G03", "G04", "G10", "G11"],
        "status": "documented_or_rate_change_proxy_no_pitch_control_execution",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Limited F0-contour prosody control and bounded energy shaping",
        "components": ["f0-contour-smoothing"],
        "gap_ids": ["G05", "G09", "G12"],
        "status": "blocked_no_smoother_desired_contour_or_voicing_reference",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": (
            "Disentangled neural analysis/resynthesis with separate pitch, "
            "content and timbre representations (NANSY lead)"
        ),
        "components": [
            "nansy-analysis-resynthesis",
            "hifi-gan-vocoder",
            "vocos-vocoder",
        ],
        "gap_ids": ["G04", "G07", "G08"],
        "status": "blocked_no_checkpoint_decoder_runtime_or_target_reference",
    },
]

# component_id, task and evidence_status are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "psola-praat", "role": "pitch_synchronous_ola_rate_reference", "evidence_status": "evaluated", "task": "SDK-PSOLA-PRAAT"},
    {"component_id": "td-psola", "role": "designated_pitch_synchronous_shift_lead", "evidence_status": "considered", "task": "SDK-TD-PSOLA"},
    {"component_id": "sonic", "role": "pitch_synchronous_ola_rate_reference", "evidence_status": "partial", "task": "SDK-SONIC"},
    {"component_id": "phase-vocoder-baseline", "role": "analysis_resynthesis_pitch_preservation_proxy", "evidence_status": "considered", "task": "SDK-PHASE-VOCODER-BASELINE"},
    {"component_id": "world-vocoder", "role": "source_filter_vocoder_lead", "evidence_status": "considered", "task": "SDK-WORLD-VOCODER"},
    {"component_id": "avaudiounittimepitch-rate-pitch-overlap", "role": "platform_rate_pitch_unit_lead", "evidence_status": "considered", "task": "SDK-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP"},
    {"component_id": "rubber-band-r3-offline", "role": "formant_preserving_phase_vocoder_reference", "evidence_status": "evaluated", "task": "SDK-RUBBER-BAND-R3-OFFLINE"},
    {"component_id": "rubber-band-r3-streaming", "role": "streaming_phase_vocoder_reference", "evidence_status": "evaluated", "task": "SDK-RUBBER-BAND-R3-STREAMING"},
    {"component_id": "soundtouch", "role": "wsola_rate_pitch_preservation_control", "evidence_status": "evaluated", "task": "SDK-SOUNDTOUCH"},
    {"component_id": "ffmpeg-atempo", "role": "classical_ola_rate_pitch_preservation_control", "evidence_status": "evaluated", "task": "SDK-FFMPEG-ATEMPO"},
    {"component_id": "nansy-analysis-resynthesis", "role": "disentangled_neural_analysis_resynthesis_lead", "evidence_status": "considered", "task": "SDK-NANSY-ANALYSIS-RESYNTHESIS"},
    {"component_id": "f0-contour-smoothing", "role": "limited_prosody_control_lead", "evidence_status": "blocked", "task": "SDK-F0-CONTOUR-SMOOTHING"},
    {"component_id": "emotion-expressive-prosody-transformation", "role": "out_of_scope_emotion_manipulation", "evidence_status": "blocked", "task": "SDK-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION"},
    {"component_id": "hifi-gan-vocoder", "role": "neural_resynthesis_decoder_lead", "evidence_status": "considered", "task": "SDK-HIFI-GAN-VOCODER"},
    {"component_id": "vocos-vocoder", "role": "neural_resynthesis_decoder_lead", "evidence_status": "considered", "task": "SDK-VOCOS-VOCODER"},
]

EXCLUDED_BOUNDARIES: List[Dict[str, str]] = [
    {
        "boundary": "Time-scale modification and pitch-preserving speed (TRN-01)",
        "reason": "A rate engine's F0-distribution shift is not a designated pitch control, a formant measurement or a prosody edit.",
    },
    {
        "boundary": "Accent conversion (TRN-03)",
        "reason": "Accent change targets pronunciation and phonetic mapping; it is not a bounded pitch/formant/energy control on the same content.",
    },
    {
        "boundary": "Voice conversion, cloning and speaker identity replacement",
        "reason": "A disentangled pitch path is not consent-cleared identity replacement, and no target speaker or reference voice is staged.",
    },
    {
        "boundary": "Emotion and expressive prosody manipulation",
        "reason": "The catalogued boundary excludes emotion manipulation; a bounded F0 contour smoother is not an emotion classifier or target style model.",
    },
    {
        "boundary": "Listening quality, naturalness and speech enhancement (OBS-01 / CLN-01)",
        "reason": "A frequency proxy, synthetic formant probe or sample map is not perceived pitch, audibility, naturalness or an enhanced waveform.",
    },
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Ten 4 s AMI speech-heavy windows rendered at 0.5x, 0.8x, 1x, 1.25x, 1.5x and 2.5x, with median F0-distribution shift reported per engine",
        "class": "historical_research_rate_f0_proxy",
        "source_pin": "research/tsm-followup-20261101/README.md",
        "boundary": "Historical source-reported rate screen; not rerun here. F0-distribution shift is a pitch-preservation proxy under rate change, not a designated pitch shift or a listening result.",
    },
    {
        "id": "CI-2",
        "input": "Task-local synthetic PSOLA fixture with explicit pitch marks and a 220 Hz tonal stimulus",
        "class": "task_local_synthetic_pitch_proxy",
        "source_pin": "docs/task-evidence/psola-praat/README.md",
        "boundary": "Rate-change fixture only. Identity and PSOLA keep the tone at 220 Hz; a varispeed adverse control must shift pitch. No designated pitch-shift, formant or prosody result.",
    },
    {
        "id": "CI-3",
        "input": "Task-local synthetic Sonic pitch-synchronous Hann OLA fixture across five rate cases",
        "class": "task_local_synthetic_pitch_proxy",
        "source_pin": "docs/task-evidence/sonic/README.md",
        "boundary": "A 220 Hz analytic tone is scored by a grid Goertzel proxy; a varispeed adverse control is excluded. Frequency proxy only, not perceived pitch.",
    },
    {
        "id": "CI-4",
        "input": "Task-local Rubber Band offline synthetic pitch, transient and formant-probe cases",
        "class": "task_local_synthetic_pitch_proxy",
        "source_pin": "docs/task-evidence/rubber-band-r3-offline/README.md",
        "boundary": "Pitch proxy is octave-equivariant on a synthetic tone; music's raw octave ratio is normalized before interpretation. No real speaker, listening or formant-preservation gold.",
    },
    {
        "id": "CI-5",
        "input": "Task-local Rubber Band streaming synthetic dynamic-rate case with pitch sampled after output-window mapping",
        "class": "task_local_synthetic_pitch_proxy",
        "source_pin": "docs/task-evidence/rubber-band-r3-streaming/README.md",
        "boundary": "Candidate and identity remain at 220 Hz while the varispeed control shifts. Duration error is recorded, not waived; no device pacing or listening.",
    },
    {
        "id": "CI-6",
        "input": "Task-local SoundTouch synthetic dynamic and varispeed cases on a 220 Hz tonal stimulus",
        "class": "task_local_synthetic_pitch_proxy",
        "source_pin": "docs/task-evidence/soundtouch/README.md",
        "boundary": "Identity stays at 220 Hz; the varispeed adverse control shifts to 274 Hz by design. The fixture is a frequency proxy, not a pitch-control or naturalness result.",
    },
    {
        "id": "CI-7",
        "input": "Task-local phase-vocoder baseline on synthetic 437 Hz and impulse cases",
        "class": "task_local_synthetic_pitch_proxy",
        "source_pin": "docs/task-evidence/phase-vocoder-baseline/README.md",
        "boundary": "Preserves one synthetic tone but smears the transient and displaces the tail. This is an analysis/resynthesis pitch-preservation proxy, not a pitch shift.",
    },
    {
        "id": "CI-8",
        "input": "WORLD vocoder implementation (S34) and NANSY analysis/resynthesis paper (S35)",
        "class": "source_reported_vocoder_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation leads describe families only; no local source tree, revision, checkpoint, weight terms, runtime or numeric parity follows.",
    },
    {
        "id": "CI-9",
        "input": "F0 contour smoothing and emotion/expressive prosody rows from the candidate matrix and transformation audit",
        "class": "source_reported_prosody_audit",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Both rows are unavailable/blocked; no smoother, desired contour, voicing reference, target emotion label or consent-cleared reference voice exists.",
    },
    {
        "id": "CI-10",
        "input": "Platform AVAudioUnitTimePitch (rate, pitch, overlap) candidate note",
        "class": "source_reported_platform_caveat",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "boundary": "Source is unavailable and behaviour can change between OS versions; there is no pinned binary, setting or local platform execution.",
    },
    {
        "id": "CI-11",
        "input": "Rights-cleared speech cohort with independent designated pitch, formant and prosody targets",
        "class": "missing_required_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Not present in this task or the pinned research; no input asset, consent-cleared target, split, label or scorer is staged.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "identity / 1x pitch and duration", "role": "Paired no-change baseline; exact identity only where the synthetic fixture supports it, never a quality result.", "source_pin": "docs/task-evidence/psola-praat/README.md"},
    {"id": "CT-2", "name": "varispeed adverse control", "role": "Rate change that must shift pitch; it is non-qualifying and is not a designated pitch-shift control.", "source_pin": "docs/task-evidence/soundtouch/README.md"},
    {"id": "CT-3", "name": "autocorrelation / Goertzel F0 proxy", "role": "Frequency-scale proxy; octave-equivariant and explicitly not perceived pitch, naturalness or audibility.", "source_pin": "docs/task-evidence/rubber-band-r3-offline/README.md"},
    {"id": "CT-4", "name": "synthetic formant probe", "role": "Fixed synthetic formant-style probe only; it is not a formant-preservation gold reference.", "source_pin": "docs/task-evidence/rubber-band-r3-offline/README.md"},
    {"id": "CT-5", "name": "exact source/output sample map", "role": "Separates time-scale mapping from pitch modification; it does not measure pitch accuracy or latency.", "source_pin": "docs/task-evidence/psola-praat/README.md"},
    {"id": "CT-6", "name": "blocked rows without substitution", "role": "Candidate identity is preserved; no other pitch shifter, vocoder or acoustic model is silently substituted.", "source_pin": "research/voice-enhancement-20261101/agent-transform-space/REPORT.md"},
]

ASSETS: List[Dict[str, str]] = [
    {"asset": "Ten 4 s AMI speech-heavy windows and 136 reference words", "class": "historical_research_audio", "status": "Described in the pinned rate report; bytes are not present or verified here and redistribution/listening rights are not cleared.", "source_pin": "research/tsm-followup-20261101/README.md"},
    {"asset": "Task-local PSOLA analytic pitch-mark fixture", "class": "generated_synthetic", "status": "Generated deterministically from silence, tonal, speech-like, unfamiliar-speech and music-like surrogates; no real audio is stored or played.", "source_pin": "docs/task-evidence/psola-praat/README.md"},
    {"asset": "Task-local Sonic pitch-synchronous OLA fixture", "class": "generated_synthetic", "status": "Analytic 220 Hz tone, impulse train and synthetic speech-like signal; no corpus, WAV, model or listening test.", "source_pin": "docs/task-evidence/sonic/README.md"},
    {"asset": "Task-local Rubber Band offline pitch/transient/formant fixture", "class": "generated_synthetic", "status": "Synthetic tone, music proxy, click and formant-style fields only; no upstream code, binary, model or real corpus.", "source_pin": "docs/task-evidence/rubber-band-r3-offline/README.md"},
    {"asset": "Task-local Rubber Band streaming dynamic-rate fixture", "class": "generated_synthetic", "status": "Synthetic dynamic schedule with source-anchored maps; no device playout, real speech or listening.", "source_pin": "docs/task-evidence/rubber-band-r3-streaming/README.md"},
    {"asset": "Task-local SoundTouch dynamic and varispeed fixture", "class": "generated_synthetic", "status": "Synthetic tonal/speech-like/music-like surrogates and a deliberate varispeed adverse control; not an upstream SoundTouch runtime.", "source_pin": "docs/task-evidence/soundtouch/README.md"},
    {"asset": "Task-local phase-vocoder baseline fixture", "class": "generated_synthetic", "status": "A 437 Hz sine, an isolated impulse and silence generated in-process; no recording or generated audio file is stored.", "source_pin": "docs/task-evidence/phase-vocoder-baseline/README.md"},
    {"asset": "WORLD and NANSY source code / checkpoints / weights", "class": "absent", "status": "Documentation leads only; no source tree, checkpoint, weight file, runtime, model terms or consent-cleared target reference is staged.", "source_pin": "research/category_survey/sources.md"},
    {"asset": "Rights-cleared designated pitch/formant/prosody cohort", "class": "missing_asset", "status": "No rights-cleared input speech, consent-cleared target voice, designated pitch contour, formant target or prosody label is staged.", "source_pin": "audio_categories.md"},
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Four classical rate engines' median F0-distribution shift on ten AMI windows",
        "outcome_class": "historical_research_rate_f0_proxy",
        "component_ids": [
            "soundtouch",
            "rubber-band-r3-offline",
            "rubber-band-r3-streaming",
            "psola-praat",
        ],
        "source_pin": "research/tsm-followup-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "rate_change_pitch_preservation_proxy",
        "values": {
            "clips": 10,
            "clip_duration_s": 4,
            "rate_factors": 6,
            "soundtouch_f0_shift_0_5_semitones": -0.03,
            "soundtouch_f0_shift_2_5_semitones": 0.21,
            "rubber_band_f0_shift_0_5_semitones": 0.0,
            "rubber_band_f0_shift_2_5_semitones": 0.16,
            "psola_f0_shift_0_5_semitones": 0.21,
            "psola_f0_shift_2_5_semitones": 0.54,
        },
        "scope": (
            "Ten four-second AMI windows at six constant rate factors in one research "
            "pilot. The median F0-distribution shift is a pitch-preservation proxy "
            "under rate change, not a designated pitch shift, formant measurement, "
            "prosody edit or listening result. The single Rubber Band row maps to both "
            "offline and streaming components and is not split into invented per-mode "
            "values. Audio, engine builds and rights are not present here; not rerun "
            "by this survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "FFmpeg 7.1 atempo classical control F0 shift on ten held-out AMI windows",
        "outcome_class": "historical_research_rate_f0_proxy",
        "component_ids": ["ffmpeg-atempo"],
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "classical_rate_control_pitch_proxy",
        "values": {
            "clips": 10,
            "rate_low": 0.8,
            "rate_high": 1.25,
            "f0_shift_1_25_semitones": 0.17,
            "f0_shift_0_8_semitones": 0.05,
        },
        "scope": (
            "Measured classical rate control at 1.25x and 0.8x. The autocorrelation "
            "F0-distribution shift is a source-reported pitch-preservation proxy, "
            "not a designated pitch-shift, formant or prosody result, and the exact "
            "FFmpeg build and GPL configuration are not reproduced here; not rerun "
            "by this survey."
        ),
    },
]

LOCAL_EVIDENCE: List[Dict[str, Any]] = [
    {
        "id": "LE-1",
        "component_id": "psola-praat",
        "path": "docs/task-evidence/psola-praat/README.md",
        "sha256": WORKTREE_PINS["docs/task-evidence/psola-praat/README.md"],
        "evidence_class": "task_local_synthetic_pitch_proxy",
        "evidence_role": "pitch_synchronous_ola_rate_reference",
        "observed": {
            "identity_pitch_hz": 220,
            "identity_output_hz": 220,
            "identity_scale": 1.0,
            "varispeed_adverse_scale": 1.2455,
            "mismarked_adverse_scale": 2.0,
        },
        "not_measured": [
            "designated_pitch_shift",
            "formant_preservation",
            "prosody_editing",
            "perceptual_pitch",
            "listening",
        ],
        "qualifies_candidate": False,
        "scope": (
            "Task-local synthetic rate fixture. Pitch marks and a frequency proxy are "
            "recorded for identity and adverse controls only; this is not a designated "
            "pitch-shift, formant-preservation or prosody-control result."
        ),
    },
    {
        "id": "LE-2",
        "component_id": "sonic",
        "path": "docs/task-evidence/sonic/README.md",
        "sha256": WORKTREE_PINS["docs/task-evidence/sonic/README.md"],
        "evidence_class": "task_local_synthetic_pitch_proxy",
        "evidence_role": "pitch_synchronous_ola_rate_reference",
        "observed": {"analytic_tone_hz": 220},
        "not_measured": [
            "designated_pitch_shift",
            "formant_preservation",
            "prosody_editing",
            "perceived_pitch",
            "listening",
        ],
        "qualifies_candidate": False,
        "scope": (
            "Task-local synthetic pitch-synchronous OLA rate fixture. A grid Goertzel "
            "proxy scores one analytic tone, and a varispeed adverse control is "
            "excluded; this is not a designated pitch-shift, formant-preservation or "
            "prosody-control result."
        ),
    },
    {
        "id": "LE-3",
        "component_id": "rubber-band-r3-offline",
        "path": "docs/task-evidence/rubber-band-r3-offline/README.md",
        "sha256": WORKTREE_PINS["docs/task-evidence/rubber-band-r3-offline/README.md"],
        "evidence_class": "task_local_synthetic_pitch_proxy",
        "evidence_role": "formant_preserving_phase_vocoder_rate_reference",
        "observed": {
            "identity_pitch_hz": 220,
            "identity_output_hz": 220,
            "identity_scale": 1.0,
            "music_raw_scale": 2.018,
            "music_octave_normalized_scale": 1.009,
            "varispeed_source_hz": 219.2,
            "varispeed_output_hz": 275.9,
            "varispeed_scale": 1.259,
        },
        "not_measured": [
            "designated_pitch_shift",
            "formant_preservation_gold",
            "prosody_editing",
            "perceived_pitch",
            "listening",
        ],
        "qualifies_candidate": False,
        "scope": (
            "Task-local synthetic rate fixture with an octave-equivariant pitch proxy "
            "and a fixed synthetic formant-style probe. It is not a designated "
            "pitch-shift, formant-preservation gold or prosody-control result."
        ),
    },
    {
        "id": "LE-4",
        "component_id": "rubber-band-r3-streaming",
        "path": "docs/task-evidence/rubber-band-r3-streaming/README.md",
        "sha256": WORKTREE_PINS["docs/task-evidence/rubber-band-r3-streaming/README.md"],
        "evidence_class": "task_local_synthetic_pitch_proxy",
        "evidence_role": "streaming_phase_vocoder_rate_reference",
        "observed": {
            "identity_pitch_hz": 220,
            "identity_output_hz": 220,
            "varispeed_output_hz": 276,
            "varispeed_shift_percent": 25.45,
        },
        "not_measured": [
            "designated_pitch_shift",
            "formant_preservation",
            "prosody_editing",
            "perceived_pitch",
            "device_timing",
            "listening",
        ],
        "qualifies_candidate": False,
        "scope": (
            "Task-local synthetic dynamic-rate fixture. Pitch is sampled after mapping "
            "the output analysis window, and the duration error is retained; this is "
            "not a designated pitch-shift, formant-preservation or prosody-control "
            "result and not device pacing."
        ),
    },
    {
        "id": "LE-5",
        "component_id": "soundtouch",
        "path": "docs/task-evidence/soundtouch/README.md",
        "sha256": WORKTREE_PINS["docs/task-evidence/soundtouch/README.md"],
        "evidence_class": "task_local_synthetic_pitch_proxy",
        "evidence_role": "wsola_rate_pitch_preservation_control",
        "observed": {
            "identity_pitch_hz": 220,
            "identity_output_hz": 220,
            "identity_scale": 1.0,
            "fixed_1_25_output_hz": 226,
            "fixed_1_25_scale": 1.027273,
            "varispeed_output_hz": 274,
            "varispeed_scale": 1.245455,
        },
        "not_measured": [
            "designated_pitch_shift",
            "formant_preservation",
            "prosody_editing",
            "perceived_pitch",
            "listening",
        ],
        "qualifies_candidate": False,
        "scope": (
            "Task-local synthetic rate fixture. A 220 Hz tone is tracked across an "
            "identity, fixed-rate and varispeed adverse case; this is not a designated "
            "pitch-shift, formant-preservation or prosody-control result."
        ),
    },
    {
        "id": "LE-6",
        "component_id": "phase-vocoder-baseline",
        "path": "docs/task-evidence/phase-vocoder-baseline/README.md",
        "sha256": WORKTREE_PINS["docs/task-evidence/phase-vocoder-baseline/README.md"],
        "evidence_class": "task_local_synthetic_pitch_proxy",
        "evidence_role": "analysis_resynthesis_pitch_preservation_proxy",
        "observed": {"tone_hz": 437.0},
        "not_measured": [
            "designated_pitch_shift",
            "formant_preservation",
            "prosody_editing",
            "perceived_pitch",
            "listening",
        ],
        "qualifies_candidate": False,
        "scope": (
            "Task-local synthetic analysis/resynthesis fixture that preserves one "
            "synthetic tone but smears the transient and displaces the tail; this is "
            "not a designated pitch-shift, formant-preservation or prosody-control "
            "result."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "WORLD source-filter vocoder family (S34)",
        "class": "source_reported_vocoder_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation lead only; no local WORLD source, revision, binary, weight terms or execution.",
    },
    {
        "id": "RO-2",
        "claim": "NANSY disentangled neural analysis/resynthesis family (S35)",
        "class": "source_reported_vocoder_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Paper lead only; no checkpoint, configuration, decoder runtime, weight terms or target reference.",
    },
    {
        "id": "RO-3",
        "claim": "F0 contour smoothing for limited prosody control",
        "class": "source_reported_prosody_audit",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Unavailable/blocked: no exact smoother, desired contour or voicing reference is specified, so no accuracy can be calculated.",
    },
    {
        "id": "RO-4",
        "claim": "Emotion and expressive prosody transformation",
        "class": "source_reported_prosody_audit",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Unavailable/blocked and excluded from category scope: no input-speech model, target emotion labels or consent-cleared target voices are staged.",
    },
    {
        "id": "RO-5",
        "claim": "AVAudioUnitTimePitch rate, pitch and overlap unit",
        "class": "source_reported_platform_caveat",
        "source_pin": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "boundary": "Platform candidate only; source is unavailable, behaviour can change between OS versions and no pinned settings or local execution exist.",
    },
    {
        "id": "RO-6",
        "claim": "Pitch shift, formant preservation and full prosody editing are distinct",
        "class": "source_reported_boundary_statement",
        "source_pin": "audio_categories.md",
        "boundary": "Catalogued boundary only; emotion manipulation is excluded and no adjacent pitch-preservation result is promoted.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "permitted_input_and_target_references": "Historical rate rows cite AMI speech; no task-local designated pitch target, formant target, desired contour or consent-cleared reference voice exists",
        "task_and_language_speaker_groups": "One English meeting and synthetic surrogates only; no language, speaker, age, accent or domain group is defined",
        "text_and_semantic_content_preserved": "Not assessed; no transcript, semantic probe or intelligibility scorer is run",
        "identity_and_similarity": "Not measured; no speaker embedding, reference voice or identity control is staged",
        "naturalness": "Not measured; no listening panel or naturalness scorer exists",
        "alignment_first_output_and_tail_timing": "Only synthetic sample maps and a final partial window exist; no device first-output, tail or callback timing",
        "exact_target_condition": "No designated pitch ratio, formant policy, energy target or prosody contour is frozen for evaluation",
        "pitch_and_formant_accuracy": "Only autocorrelation/Goertzel frequency proxies on synthetic tones; no perceptual pitch or formant-preservation measurement",
        "voiced_unvoiced_and_nonfinite_handling": "Synthetic fixtures record invalid, nonfinite and missing cases, but no task-matched designated-pitch controller is tested",
    },
    "blocked": [
        "Rights-cleared, consent-covered speech corpus with designated pitch, formant and limited-prosody targets and exact labels",
        "Independent blind listening for pitch shift, formant preservation and prosody naturalness",
        "Task-matched pitch/formant accuracy protocol with voiced/unvoiced, nonfinite and missing-value handling",
        "Pinned PSOLA, WORLD, NANSY and neural-vocoder runtimes with exact revisions and per-weight licence terms",
        "Target-device real-time timing, buffering, content delay and resource evidence",
        "Formant-preservation and full-prosody separation with identity and content preservation",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection and release approval; DEFER remains until every gate closes",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class is
# true only when a mapped row backs it; absence is recorded as false instead of
# being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "historical_research_rate_f0_proxy": True,
    "task_local_synthetic_pitch_proxy": True,
    "source_reported_vocoder_documentation": True,
    "source_reported_prosody_audit": True,
    "source_reported_platform_caveat": True,
    "source_reported_boundary_statement": True,
    "designated_pitch_shift_execution": False,
    "formant_preservation_measurement": False,
    "full_prosody_editing_execution": False,
    "emotion_manipulation": False,
    "perceptual_pitch_accuracy": False,
    "human_listening_result": False,
    "real_speech_used_here": False,
    "real_corpus_benchmark": False,
    "weights_loaded_here": False,
    "runtime_invoked_here": False,
    "model_inference_here": False,
    "device_timing": False,
    "latency_claim": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "release_claim": False,
    "benchmark_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
}

CLASS_BACKING: Dict[str, List[str]] = {
    "historical_research_rate_f0_proxy": ["historical_research_rate_f0_proxy"],
    "task_local_synthetic_pitch_proxy": ["task_local_synthetic_pitch_proxy"],
    "source_reported_vocoder_documentation": ["source_reported_vocoder_documentation"],
    "source_reported_prosody_audit": ["source_reported_prosody_audit"],
    "source_reported_platform_caveat": ["source_reported_platform_caveat"],
    "source_reported_boundary_statement": ["source_reported_boundary_statement"],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Obtain a pinned WORLD source-filter/vocoder runtime with an exact revision, build settings and licence terms, then measure bounded pitch and formant controls",
        "evidence_gap": "S34 is a documentation lead; the inventory row is considered and no local source tree, binary, weight or execution exists.",
        "follow_up_ids": ["SDK-WORLD-VOCODER", "SDK-FND-AUDIT"],
        "feasibility_task_exists": True,
        "owner_note": "The linked WORLD feasibility row owns the candidate intake; the audit foundation owns the asset and licence boundary. No source is fetched or built here.",
    },
    {
        "id": "G02",
        "actionable_gap": "Evaluate a designated pitch-shift control on TD-PSOLA-class methods with exact pitch ratios and voiced/unvoiced handling",
        "evidence_gap": "PSOLA/Praat and Sonic have task-local rate fixtures only; TD-PSOLA is considered with no local evidence and no designated pitch-shift case.",
        "follow_up_ids": ["SDK-TD-PSOLA", "SDK-PSOLA-PRAAT", "SDK-SONIC"],
        "feasibility_task_exists": True,
        "owner_note": "The linked TD-PSOLA feasibility row owns the open candidate; PSOLA/Praat and Sonic own adjacent rate references, not a designated pitch-shift result.",
    },
    {
        "id": "G03",
        "actionable_gap": "Establish whether a platform pitch/rate unit can be pinned and measured on the target OS without a source-available fallback",
        "evidence_gap": "AVAudioUnitTimePitch is considered; its source is unavailable and behaviour can change between OS versions, with no local execution or settings.",
        "follow_up_ids": ["SDK-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP", "SDK-FND-AUDIT"],
        "feasibility_task_exists": True,
        "owner_note": "The linked platform feasibility row owns the candidate; the audit foundation owns the boundary. This survey records no platform run.",
    },
    {
        "id": "G04",
        "actionable_gap": "Measure formant preservation separately from pitch shift and from rate-change pitch preservation",
        "evidence_gap": "Only a fixed synthetic formant-style probe exists; no real-speech formant target, independent formant estimate or preservation margin is present.",
        "follow_up_ids": ["SDK-WORLD-VOCODER", "SDK-NANSY-ANALYSIS-RESYNTHESIS", "SDK-PHASE-VOCODER-BASELINE", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": True,
        "owner_note": "The linked WORLD, NANSY and phase-vocoder feasibility rows own the candidate paths; the evidence foundation owns the task-matched protocol. No formant result is claimed.",
    },
    {
        "id": "G05",
        "actionable_gap": "Define a bounded limited-prosody control with an explicit desired F0 contour, voicing policy and duration-preserving constraint",
        "evidence_gap": "The F0 contour smoothing row is blocked: no exact smoother, desired contour or voicing reference is specified and no accuracy can be calculated.",
        "follow_up_ids": ["SDK-F0-CONTOUR-SMOOTHING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": True,
        "owner_note": "The linked F0-contour feasibility row owns the method; the evidence foundation owns the acceptance rules. Blanket smoothing is not treated as a result.",
    },
    {
        "id": "G06",
        "actionable_gap": "Keep emotion and expressive prosody manipulation out of TRN-02 and separate it from accent conversion and bounded energy control",
        "evidence_gap": "The emotion/expressive prosody row is unavailable/blocked and excluded; no input-speech model, target labels or consent-cleared voices exist.",
        "follow_up_ids": ["SDK-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION", "SDK-SURVEY-TRN-03"],
        "feasibility_task_exists": True,
        "owner_note": "The linked emotion feasibility row owns the blocked candidate; the TRN-03 taxonomy owns the accent boundary. Neither is promoted into this category.",
    },
    {
        "id": "G07",
        "actionable_gap": "Pin a disentangled neural analysis/resynthesis checkpoint and reproduce one bounded pitch/content/timbre separation run",
        "evidence_gap": "NANSY is a paper lead with a considered inventory row; no checkpoint, configuration, decoder, weight terms or local inference exists.",
        "follow_up_ids": ["SDK-NANSY-ANALYSIS-RESYNTHESIS", "SDK-HIFI-GAN-VOCODER", "SDK-VOCOS-VOCODER"],
        "feasibility_task_exists": True,
        "owner_note": "The linked NANSY feasibility row owns the candidate; the vocoder research controls own decoder leads. No model or weight is downloaded or loaded here.",
    },
    {
        "id": "G08",
        "actionable_gap": "Establish a reproducible neural resynthesis decoder path with staged weights and a fixed upstream feature contract",
        "evidence_gap": "HiFi-GAN and Vocos are considered research controls only; no checkpoint, runtime, streaming chunk behaviour or upstream feature contract is staged.",
        "follow_up_ids": ["SDK-HIFI-GAN-VOCODER", "SDK-VOCOS-VOCODER"],
        "feasibility_task_exists": False,
        "owner_note": "No feasibility row owns a neural decoder intake; the linked research-control rows own the two decoder leads and neither supplies a runnable bundle.",
    },
    {
        "id": "G09",
        "actionable_gap": "Add independent perceptual pitch, formant-preservation and naturalness listening before any quality claim",
        "evidence_gap": "Only autocorrelation/Goertzel frequency proxies exist; no listener study, naturalness score or audibility result is present.",
        "follow_up_ids": ["SDK-FND-EVIDENCE", "SDK-FND-TIMING"],
        "feasibility_task_exists": False,
        "owner_note": "No listening owner exists; the linked evidence and timing foundations own protocol and timing rules, not a perceptual result.",
    },
    {
        "id": "G10",
        "actionable_gap": "Collect target-device first-output, tail, buffering and deadline evidence for any pitch or prosody processor",
        "evidence_gap": "Only synthetic sample maps and a symbolic rebuffer trace exist; no device callback, content delay or resource measurement is staged.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP", "SDK-RUBBER-BAND-R3-STREAMING"],
        "feasibility_task_exists": True,
        "owner_note": "The linked timing foundation owns lifecycle and timing evidence; the platform and streaming rows own the candidates. No device timing is claimed.",
    },
    {
        "id": "G11",
        "actionable_gap": "Replace rate-change pitch-preservation proxies with a task-matched designated pitch-shift protocol and exact expected pitch ratios",
        "evidence_gap": "PSOLA, Sonic, SoundTouch, Rubber Band, FFmpeg atempo and the phase-vocoder baseline report F0 preservation under rate change; none is a designated pitch-shift control.",
        "follow_up_ids": [
            "SDK-SURVEY-TRN-01",
            "SDK-PSOLA-PRAAT",
            "SDK-TD-PSOLA",
            "SDK-SONIC",
            "SDK-RUBBER-BAND-R3-OFFLINE",
            "SDK-RUBBER-BAND-R3-STREAMING",
            "SDK-SOUNDTOUCH",
            "SDK-FFMPEG-ATEMPO",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked TRN-01 taxonomy owns the rate boundary; the engine rows own adjacent references. All F0 numbers remain rate-change proxies, not pitch-shift results.",
    },
    {
        "id": "G12",
        "actionable_gap": "Obtain rights-cleared input speech and consent-cleared target references for designated pitch, formant and energy controls",
        "evidence_gap": "Historical rows cite AMI audio without local bytes or rights; synthetic surrogates cannot establish speaker, content or consent conditions.",
        "follow_up_ids": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-F0-CONTOUR-SMOOTHING"],
        "feasibility_task_exists": True,
        "owner_note": "The linked audit and evidence foundations own rights and protocol; the F0-contour feasibility row owns one candidate. No corpus or consent clearing is performed here.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-WORLD-VOCODER", "title": "WORLD vocoder", "mode": "feasibility"},
    {"task_id": "SDK-TD-PSOLA", "title": "TD-PSOLA", "mode": "feasibility"},
    {"task_id": "SDK-PSOLA-PRAAT", "title": "PSOLA / Praat", "mode": "implementation"},
    {"task_id": "SDK-SONIC", "title": "Sonic", "mode": "implementation"},
    {"task_id": "SDK-PHASE-VOCODER-BASELINE", "title": "Phase vocoder baseline", "mode": "feasibility"},
    {"task_id": "SDK-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP", "title": "AVAudioUnitTimePitch (rate, pitch, overlap)", "mode": "feasibility"},
    {"task_id": "SDK-RUBBER-BAND-R3-OFFLINE", "title": "Rubber Band R3 offline", "mode": "implementation"},
    {"task_id": "SDK-RUBBER-BAND-R3-STREAMING", "title": "Rubber Band R3 streaming", "mode": "implementation"},
    {"task_id": "SDK-SOUNDTOUCH", "title": "SoundTouch", "mode": "implementation"},
    {"task_id": "SDK-FFMPEG-ATEMPO", "title": "FFmpeg atempo", "mode": "implementation"},
    {"task_id": "SDK-NANSY-ANALYSIS-RESYNTHESIS", "title": "NANSY analysis/resynthesis", "mode": "feasibility"},
    {"task_id": "SDK-F0-CONTOUR-SMOOTHING", "title": "F0 contour smoothing", "mode": "feasibility"},
    {"task_id": "SDK-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION", "title": "Emotion / expressive prosody transformation", "mode": "feasibility"},
    {"task_id": "SDK-HIFI-GAN-VOCODER", "title": "HiFi-GAN vocoder", "mode": "research-control"},
    {"task_id": "SDK-VOCOS-VOCODER", "title": "Vocos vocoder", "mode": "research-control"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-SURVEY-TRN-01", "title": "Review coverage for Pitch-preserving speed / time-scale modification", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-TRN-03", "title": "Review coverage for Accent conversion", "mode": "taxonomy"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-cleared, consent-covered speech corpus with designated pitch, formant and limited-prosody targets and exact labels"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent blind listening for pitch shift, formant preservation and prosody naturalness"},
    {"id": "RG-03", "blocked": True, "requirement": "Task-matched pitch/formant accuracy protocol with voiced/unvoiced, nonfinite and missing-value handling"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned PSOLA, WORLD, NANSY and neural-vocoder runtimes with exact revisions and per-weight licence terms"},
    {"id": "RG-05", "blocked": True, "requirement": "Target-device real-time timing, buffering, content delay and resource evidence"},
    {"id": "RG-06", "blocked": True, "requirement": "Formant-preservation and full-prosody separation with identity and content preservation"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-08", "blocked": True, "requirement": "Explicit public default selection and release approval; DEFER remains until every gate closes"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded in
# the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "TRN-02 \u2014 Pitch and limited prosody control",
        "Pitch-synchronous overlap-add; source-filter/vocoder processing",
        "Disentangled neural analysis/resynthesis",
        "Pitch shift, formant preservation and full prosody editing differ. Emotion manipulation is not added to scope.",
    ],
    "research/category_survey/sources.md": [
        "| S34 | [WORLD vocoder implementation](https://github.com/mmorise/World) | transformations | direct |",
        "| S35 | [NANSY analysis and resynthesis paper](https://proceedings.neurips.cc/paper_files/paper/2021/file/87682805257e619d49b8e0dfdc14affa-Paper.pdf) | transformations | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Voice | Freeze permitted input and target references, task and language/speaker groups.",
        "Preserve text and semantic content, identity/similarity and naturalness as separate outcomes.",
    ],
    "research/tsm-followup-20261101/README.md": [
        "median F0-distribution shift 0.00 / +0.37 semitones",
        "median F0-distribution shift \u22120.03/+0.21 semitones",
        "median F0-distribution shift 0.00/+0.16 semitones",
        "median F0-distribution shift +0.21/+0.54 semitones",
        "No listener study compared stretched outputs.",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "autocorrelation F0-distribution shift +.17/+.05 semitones",
        "No exact smoother or desired contour/voicing reference is specified; no task accuracy can be calculated.",
        "No input-speech conversion model, target emotion labels or consent-cleared target voices are staged.",
    ],
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": [
        "No local evaluation covers voice/accent/prosody transformation or personal speaker isolation.",
        "blanket smoothing may erase expressive prosody.",
        "A pitch-contour postprocessor is a DSP/algorithm family",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/psola-praat/README.md": [
        "Pitch marks: silence `0`; tonal `172`",
        "`220 -> 220` Hz (ratio `1.0`, pitch preserved); varispeed adverse `1.2455`",
        "mismarked adverse `2.0`",
    ],
    "docs/task-evidence/sonic/README.md": [
        "pitch-synchronous grains are repeated or dropped",
        "A varispeed adverse control intentionally shifts pitch and is",
        "These are frequency proxies, not perceived pitch.",
    ],
    "docs/task-evidence/rubber-band-r3-offline/README.md": [
        "Pitch proxy on the 220 Hz tone: `220 \u2192 220` Hz (scale `1.0`)",
        "Varispeed adverse control shifts `219.2 \u2192 275.9` Hz (scale `1.259`) and does",
    ],
    "docs/task-evidence/rubber-band-r3-streaming/README.md": [
        "Pitch is sampled after mapping the output analysis window back through each",
        "Candidate and identity remain `220 \u2192 220 Hz`; the varispeed adverse",
        "control shifts to `276 Hz` (`+25.45%`).",
    ],
    "docs/task-evidence/soundtouch/README.md": [
        "Frequency scale on the 220 Hz tonal stimulus: identity and dynamic candidate",
        "`220 -> 220` Hz (ratio `1.0`); fixed `1.25x` reference `220 -> 226` Hz",
        "`1.245455`, must shift pitch).",
    ],
    "docs/task-evidence/phase-vocoder-baseline/README.md": [
        "preserves the pitch of one synthetic tone but smears the transient",
        "Pitch is measured by interpolated positive zero crossings",
    ],
    "docs/task-evidence/survey-trn-01/README.md": [
        "pitch preservation, transient audibility, listening, device timing",
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
    "historical_citations_include_real_speech": True,
    "historical_citations_include_synthetic_proxies": True,
    "real_speech_used_here": False,
    "real_corpus_used_here": False,
    "weights_loaded_here": False,
    "runtime_invoked_here": False,
    "model_inference_here": False,
    "designated_pitch_shift_here": False,
    "formant_preservation_measured_here": False,
    "prosody_editing_here": False,
    "emotion_manipulation_here": False,
    "listening_here": False,
    "device_timing_here": False,
    "latency_claim": False,
    "benchmark_claim": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "perceptual_pitch_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
}

NON_CLAIMS: List[str] = [
    "no designated pitch shift, formant-preservation measurement or prosody edit is performed by this survey",
    "no perceptual pitch, naturalness, audibility or listening result exists",
    "no real corpus, weights, model, runtime or audio is loaded in this task",
    "no emotion or expressive prosody manipulation is added to scope",
    "no WORLD, NANSY, PSOLA or neural-vocoder execution is performed or reproduced",
    "no device timing, latency or resource result is produced",
    "no provider, default, ABI, build, CI, board, handoff or shared-repo change is made",
    "no benchmark, numeric-parity, qualification or release claim is made",
]

ADVERSE_REJECTIONS: Dict[str, str] = {
    "duplicate_json_key": "rejected; state unchanged",
    "nonfinite_json_number": "rejected; state unchanged",
    "missing_pinned_file": "rejected; state unchanged",
    "tampered_pin": "rejected; state unchanged",
    "unknown_board_task": "rejected; state unchanged",
    "gap_without_link_or_reason": "rejected; state unchanged",
    "invalid_payload_type": "rejected; state unchanged",
    "designated_pitch_shift_promoted": "rejected; state unchanged",
    "formant_preservation_promoted": "rejected; state unchanged",
    "prosody_editing_promoted": "rejected; state unchanged",
    "human_listening_promoted": "rejected; state unchanged",
    "open_release_gate": "rejected; state unchanged",
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
        raise MapError("TRN-02 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("TRN-02 taxonomy mismatch: %s" % key)
    if inventory_hit[0].get("task") != TASK:
        raise MapError("TRN-02 inventory task mismatch")
    if inventory_hit[0].get("legacy_family") != LEGACY_FAMILY:
        raise MapError("TRN-02 legacy family mismatch")
    if inventory_hit[0].get("legacy_backlog_state") != "catalogued":
        raise MapError("TRN-02 legacy backlog state mismatch")
    source_index = {s["id"]: s for s in registry["sources"]}
    for lead in SOURCE_LEADS:
        source = source_index.get(lead["source_id"])
        if source is None:
            raise MapError("registry source lead is missing: " + lead["source_id"])
        for key in ("title", "url", "access_scope"):
            if source.get(key) != lead[key]:
                raise MapError("source lead mismatch: %s/%s" % (lead["source_id"], key))
    if set(CATEGORY_FACTS["source_ids"]) != {lead["source_id"] for lead in SOURCE_LEADS}:
        raise MapError("category source ids and mapped source leads differ")


def _check_backlog(workspace: Path) -> None:
    backlog = strict_json_load(workspace / "research/task_backlog.json")
    hits = [
        e
        for e in backlog["entries"]
        if e.get("family_id") == LEGACY_FAMILY and e.get("category_id") == CATEGORY_ID
    ]
    if len(hits) != 1:
        raise MapError("legacy family F13 / TRN-02 is not unique")
    entry = hits[0]
    expected = {
        "category_id": CATEGORY_ID,
        "family_id": LEGACY_FAMILY,
        "activation_state": "catalogued",
        "state": "catalogued",
        "scope": "discovered_extension",
        "next_action": "Plan discovery across required source buckets",
        "blockers": [],
        "dependencies": [],
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise MapError("legacy backlog mismatch: F13/TRN-02/%s" % key)


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
        if not row.get("role"):
            raise MapError("census row has no role: " + row["component_id"])
    mapped = {c for lead in SOURCE_LEADS for c in lead["mapped_components"]}
    mapped.update(c for family in METHOD_FAMILIES for c in family["components"])
    mapped.update(c for row in HISTORICAL_EXECUTIONS for c in row["component_ids"])
    mapped.update(row["component_id"] for row in LOCAL_EVIDENCE)
    missing = sorted(mapped - set(by_id))
    if missing:
        raise MapError("mapped component missing from inventory: " + ",".join(missing))
    census_ids = {row["component_id"] for row in COMPONENT_CENSUS}
    uncensused = sorted(mapped - census_ids)
    if uncensused:
        raise MapError("mapped component missing from census: " + ",".join(uncensused))


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
        if row.get("scope_class") != "historical_research_execution":
            raise MapError("historical execution is not labelled research: " + row["id"])
        if row.get("merged_task_evidence") is not False:
            raise MapError("historical execution is promoted to merged evidence: " + row["id"])
        if row.get("not_rerun") is not True:
            raise MapError("historical execution is not marked unrerun: " + row["id"])
        if not row.get("evidence_role"):
            raise MapError("historical execution has no evidence role: " + row["id"])
        if "not rerun by this survey" not in row.get("scope", ""):
            raise MapError("historical execution scope is not bounded: " + row["id"])
        if not isinstance(row.get("values"), dict) or not row["values"]:
            raise MapError("historical execution has no recorded values: " + row["id"])
        for key, value in row["values"].items():
            if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
                raise MapError("historical execution has a nonfinite value: %s/%s" % (row["id"], key))


def _check_local_evidence() -> None:
    known = {row["component_id"] for row in COMPONENT_CENSUS}
    seen = set()
    for row in LOCAL_EVIDENCE:
        if row["id"] in seen:
            raise MapError("duplicate local evidence id: " + row["id"])
        seen.add(row["id"])
        path = row.get("path")
        if path not in WORKTREE_PINS:
            raise MapError("local evidence path is not pinned: " + str(path))
        if row.get("sha256") != WORKTREE_PINS[path]:
            raise MapError("local evidence digest mismatch: " + str(path))
        if row.get("component_id") not in known:
            raise MapError("local evidence links an uncensused component: " + str(row.get("component_id")))
        if row.get("evidence_class") != "task_local_synthetic_pitch_proxy":
            raise MapError("local evidence class is not bounded: " + row["id"])
        if row.get("qualifies_candidate") is not False:
            raise MapError("local evidence qualifies a candidate: " + row["id"])
        if not row.get("not_measured"):
            raise MapError("local evidence hides its missing measurements: " + row["id"])
        if "not a designated pitch-shift" not in row.get("scope", ""):
            raise MapError("local evidence scope is not bounded: " + row["id"])
        if not isinstance(row.get("observed"), dict) or not row["observed"]:
            raise MapError("local evidence has no observed record: " + row["id"])


def _check_evidence_classes() -> None:
    observed = set()
    for row in COMPARISON_INPUTS:
        observed.add(row["class"])
    for row in HISTORICAL_EXECUTIONS:
        observed.add(row["outcome_class"])
    for row in LOCAL_EVIDENCE:
        observed.add(row["evidence_class"])
    for row in REPORTED_OUTCOMES:
        observed.add(row["class"])
    for key, value in EVIDENCE_CLASSES.items():
        backed = bool(observed & set(CLASS_BACKING.get(key, [])))
        if value is True and not backed:
            raise MapError("supported evidence class has no mapped row: " + key)
        if value is False and backed:
            raise MapError("evidence class is contradicted by a mapped row: " + key)
    critical_false = {
        "designated_pitch_shift_execution",
        "formant_preservation_measurement",
        "full_prosody_editing_execution",
        "emotion_manipulation",
        "perceptual_pitch_accuracy",
        "human_listening_result",
        "real_speech_used_here",
        "real_corpus_benchmark",
        "weights_loaded_here",
        "runtime_invoked_here",
        "model_inference_here",
        "device_timing",
        "latency_claim",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "release_claim",
        "benchmark_claim",
        "processor_exposure",
        "public_default",
        "network_access",
    }
    for key in critical_false:
        if EVIDENCE_CLASSES.get(key) is not False:
            raise MapError("unsupported evidence class is not false: " + key)


def _check_scope_integrity() -> None:
    if DECISION != "DEFER" or STATUS != "proposal_only_survey_incomplete":
        raise MapError("disposition constants changed")
    if QUALIFICATION_STATUS != "not_qualified" or READINESS != "incomplete":
        raise MapError("qualification constants changed")
    if len(RELEASE_GATES) != 8:
        raise MapError("release gate count is not eight")
    if [gate["id"] for gate in RELEASE_GATES] != ["RG-0%d" % k for k in range(1, 9)]:
        raise MapError("release gate ids changed")
    if any(gate["blocked"] is not True for gate in RELEASE_GATES):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in BOUNDARY.values()):
        raise MapError("boundary is not closed")
    for key in (
        "real_speech_used_here",
        "real_corpus_used_here",
        "weights_loaded_here",
        "runtime_invoked_here",
        "model_inference_here",
        "designated_pitch_shift_here",
        "formant_preservation_measured_here",
        "prosody_editing_here",
        "emotion_manipulation_here",
        "listening_here",
        "device_timing_here",
        "latency_claim",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "perceptual_pitch_claim",
        "processor_exposure",
        "public_default",
        "network_access",
    ):
        if SCOPE.get(key) is not False:
            raise MapError("scope must stay closed: " + key)
    for key in (
        "task_local_only",
        "documentation_and_metadata_only",
        "no_new_execution",
        "historical_citations_include_real_speech",
        "historical_citations_include_synthetic_proxies",
    ):
        if SCOPE.get(key) is not True:
            raise MapError("scope must stay true: " + key)
    if not NON_CLAIMS:
        raise MapError("non-claims are missing")


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
        if link["mode"] not in ALLOWED_LINK_MODES:
            raise MapError("linked board task has an unexpected mode: " + link["task_id"])
    known = {link["task_id"] for link in BOARD_LINKS}
    gap_ids = {gap["id"] for gap in GAPS}
    if len(gap_ids) != len(GAPS):
        raise MapError("duplicate gap id")
    linked_gaps = set()
    for gap in GAPS:
        if not isinstance(gap.get("follow_up_ids"), list) or not gap["follow_up_ids"]:
            raise MapError("gap has no linked board task: " + gap["id"])
        for task_id in gap["follow_up_ids"]:
            if task_id not in known:
                raise MapError("gap links an unlisted board task: %s/%s" % (gap["id"], task_id))
            linked_gaps.add(task_id)
        if gap.get("feasibility_task_exists"):
            modes = {next(t["mode"] for t in BOARD_LINKS if t["task_id"] == tid) for tid in gap["follow_up_ids"]}
            if "feasibility" not in modes:
                raise MapError("gap claims a feasibility follow-up without one: " + gap["id"])
        elif not gap.get("owner_note"):
            raise MapError("gap without feasibility task has no owner note: " + gap["id"])
    for source in SOURCE_LEADS:
        for gap_id in source["gap_ids"]:
            if gap_id not in gap_ids:
                raise MapError("source lead links unknown gap: " + gap_id)
    for family in METHOD_FAMILIES:
        for gap_id in family["gap_ids"]:
            if gap_id not in gap_ids:
                raise MapError("method family links unknown gap: " + gap_id)
    for link in BOARD_LINKS:
        if link["task_id"] not in linked_gaps:
            raise MapError("board link has no gap: " + link["task_id"])
    return _board_projection(board)


def outcome_ledger(
    historical: List[Dict[str, Any]],
    local: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    reported_by: Dict[str, List[Dict[str, Any]]] = {}
    for item in historical:
        for component_id in item["component_ids"]:
            reported_by.setdefault(component_id, []).append(item)
    local_by = {item["component_id"]: item for item in local}
    rows = []
    for component_id in sorted(set(reported_by) | set(local_by)):
        reported = reported_by.get(component_id, [])
        local_item = local_by.get(component_id)
        rows.append({
            "component_id": component_id,
            "reported": {
                "recorded": bool(reported),
                "classification": ("source_reported_not_reproduced"
                                   if reported else "no_reported_outcome"),
                "row_ids": sorted(item["id"] for item in reported),
            },
            "local": {
                "recorded": local_item is not None,
                "classification": ("task_local_synthetic_reference_only"
                                   if local_item else "no_task_local_execution"),
                "row_id": local_item["id"] if local_item else None,
                "evidence_pin": local_item["path"] if local_item else None,
            },
            "comparison_performed": False,
            "qualifies_candidate": False,
        })
    return rows


def local_vs_reported_outcomes() -> Dict[str, Any]:
    historical = [dict(row) for row in HISTORICAL_EXECUTIONS]
    local = [dict(row) for row in LOCAL_EVIDENCE]
    reported_components = sorted({c for row in historical for c in row["component_ids"]})
    local_components = sorted({row["component_id"] for row in local})
    return {
        "reported": {
            "recorded_in": "historical_executions",
            "classification": "source_reported_not_reproduced",
            "count": len(historical),
            "component_ids": reported_components,
            "qualifies_candidate": False,
        },
        "local": {
            "recorded_in": "local_evidence",
            "classification": "task_local_synthetic_reference_only",
            "count": len(local),
            "component_ids": local_components,
            "qualifies_candidate": False,
        },
        "cross_comparison": {
            "performed": False,
            "numeric_parity_claimed": False,
            "reason": (
                "No matched frozen asset, exact ratio, formant target, runtime, settings "
                "or listening protocol is shared between the source-reported rate-change "
                "F0 proxy and the task-local synthetic pitch proxies; no numeric parity "
                "or outcome promotion is performed."
            ),
        },
        "ledger": outcome_ledger(historical, local),
    }


def _build_report(workspace: Optional[str] = None, sdk_root: Optional[str] = None) -> Dict[str, Any]:
    ws = find_workspace(workspace)
    sdk = find_sdk_root(sdk_root)
    _check_document_pins(ws, sdk)
    _check_anchors(ws, sdk)
    _check_taxonomy(ws)
    _check_backlog(ws)
    _check_component_census(ws)
    _check_historical_execution_components()
    _check_local_evidence()
    _check_evidence_classes()
    _check_scope_integrity()
    board_digest = _check_board(ws)

    links: List[Dict[str, Any]] = []
    for link in BOARD_LINKS:
        linked = sorted(g["id"] for g in GAPS if link["task_id"] in g["follow_up_ids"])
        links.append(
            {
                "task_id": link["task_id"],
                "title": link["title"],
                "mode": link["mode"],
                "linked_gaps": linked,
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
        "decision": DECISION,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualification_status": QUALIFICATION_STATUS,
            "readiness": READINESS,
            "survey_status": "incomplete",
            "proposal_only": True,
            "qualifies": False,
            "decision": DECISION,
            "processor_exposure": False,
            "missing_result_promoted": False,
            "release_qualification_present": False,
            "designated_pitch_shift_execution_present": False,
            "formant_preservation_measurement_present": False,
            "prosody_editing_execution_present": False,
            "human_listening_result_present": False,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "category_scope": dict(CATEGORY_SCOPE),
        "non_claims": list(NON_CLAIMS),
        "taxonomy": dict(CATEGORY_FACTS),
        "legacy_backlog": {
            "family_id": LEGACY_FAMILY,
            "activation_state": "catalogued",
            "state": "catalogued",
            "next_action": "Plan discovery across required source buckets",
            "source_pin": "research/task_backlog.json",
        },
        "source_leads": [copy.deepcopy(lead) for lead in SOURCE_LEADS],
        "method_families": [copy.deepcopy(family) for family in METHOD_FAMILIES],
        "component_census": [dict(row) for row in COMPONENT_CENSUS],
        "excluded_boundaries": [dict(row) for row in EXCLUDED_BOUNDARIES],
        "comparison_inputs": [dict(row) for row in COMPARISON_INPUTS],
        "controls": [dict(row) for row in CONTROLS],
        "assets": [dict(row) for row in ASSETS],
        "historical_executions": [copy.deepcopy(row) for row in HISTORICAL_EXECUTIONS],
        "local_evidence": [copy.deepcopy(row) for row in LOCAL_EVIDENCE],
        "reported_outcomes": [dict(row) for row in REPORTED_OUTCOMES],
        "local_vs_reported_outcomes": local_vs_reported_outcomes(),
        "evidence_classes": dict(EVIDENCE_CLASSES),
        "acceptance_profile": copy.deepcopy(ACCEPTANCE_PROFILE),
        "gaps": [copy.deepcopy(gap) for gap in GAPS],
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
            "check": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py check",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
        },
    }

    # Final fail-closed disposition checks; no gate may be weakened.
    if report["decision"] != DECISION:
        raise MapError("decision changed")
    if report["status"] != STATUS or report["qualification"]["survey_status"] != "incomplete":
        raise MapError("status changed")
    if report["qualification"]["status"] != QUALIFICATION_STATUS:
        raise MapError("qualification changed")
    if report["qualification"]["readiness"] != READINESS:
        raise MapError("readiness changed")
    if report["qualification"]["qualification_status"] != QUALIFICATION_STATUS:
        raise MapError("qualification_status changed")
    if report["qualification"]["designated_pitch_shift_execution_present"] is not False:
        raise MapError("designated pitch-shift execution promoted")
    if report["qualification"]["formant_preservation_measurement_present"] is not False:
        raise MapError("formant preservation promoted")
    if report["qualification"]["prosody_editing_execution_present"] is not False:
        raise MapError("prosody editing promoted")
    if report["qualification"]["human_listening_result_present"] is not False:
        raise MapError("human listening promoted")
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count is not eight")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in report["boundary"].values()):
        raise MapError("boundary is not closed")
    if report["scope"]["no_new_execution"] is not True:
        raise MapError("survey claims a new execution")
    if report["scope"]["designated_pitch_shift_here"] is not False:
        raise MapError("a designated pitch shift is claimed")
    if {row["branch"] for row in report["method_families"]} != {"classic", "ml"}:
        raise MapError("both catalogued method branches are not covered")
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
