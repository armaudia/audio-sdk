# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-TRN-04.

This module builds a bounded taxonomy/comparison evidence map for the
speech-to-speech voice conversion category (inventory category ``TRN-04``,
legacy family ``F14``). It reads only pinned, read-only documents from the
enclosing ``audioml`` workspace and the SDK worktree. It does not load audio,
weights, models, runtimes, media or the network, and it does not register,
expose, enable or qualify any voice converter.

All curated records below are documentation mappings, not new measurements.
Historical research values are transcribed from the pinned voice-conversion
report, its crosswalk and the pinned vocoder timing JSON, and are labelled with
their original scope. A speaker-embedding cosine is not an independent identity
rating; a warm file RTF is not microphone-to-output latency; one 240 ms block is
not sustained streaming; and a decoder-only timing is not end-to-end conversion.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-TRN-04"
TITLE = "Review coverage for Speech-to-speech voice conversion"
CATEGORY_ID = "TRN-04"
LEGACY_FAMILY = "F14"
BRANCH = "swarm/SDK-SURVEY-TRN-04"
BASE_COMMIT = "39b8885da4fc3ef8e27becf5df5f0658da3baf65"
PROFILE = "Voice"
COMPONENT = "speech-to-speech-voice-conversion-evidence-map"
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
    "pipeline",
)

# REUSE-IgnoreStart
LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-Identifier: Apache-2.0\n"
)
# REUSE-IgnoreEnd

# Workspace-relative document pins. Every entry is a read-only document or
# metadata ledger consulted by this survey; a pin never grants rights or
# verifies media, weights, transcripts or consent that are not present in this
# task directory.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/accent-conversion-20261101/README.md": "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json": "1948ef27a8ff6f1ddeb24312b0a75ff0303dc6ef05bb2c659c014651cb480741",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-conversion-eval-20261101/README.md": "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/agent-breadth-audit/REPORT.md": "ef093eee8c8cd68984d3a7f5602fcc44c9a0262990e7c90c9bd34ecc3d8fadc2",
    "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md": "b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6",
}

# SDK-worktree-relative boundary pins. They are read only to prove that no
# public surface was touched and to ground the cited adjacent task-local
# evidence. Sibling survey READMEs are pinned as templates, not as results.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/survey-spk-01/README.md": "554a9fcc044e89c35ba761bf1fa8f7fed172ba22f797e44bdd64a753c00adc9d",
    "docs/task-evidence/survey-trn-01/README.md": "20503c685e57ba2b6d15a677cfad1ea7e6f22b391010af61bb4fd6dc63ea8972",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Playback and voice transformations",
    "name": "Speech-to-speech voice conversion",
    "scope": "requested_optional",
    "output_kind": "waveform",
    "purpose": "Change designated speaker/timbre attributes while retaining the spoken content.",
    "method_families": {
        "classic": "Statistical spectral mapping with vocoders; GMM family to search",
        "ml": "Content/speaker-disentangled decoders; streaming and flow/diffusion variants",
    },
    "input_output": "Source audio + target voice cue \u2192 converted speech",
    "live_or_comparison_boundary": (
        "Evaluate target similarity separately from words, prosody and delay; "
        "available implementation and weights are required."
    ),
    "source_ids": ["S38", "S39"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "TRN",
    "meaning": "Playback and voice transformations",
    "category_id": CATEGORY_ID,
    "waveform_transformation_only": True,
    "designated_speaker_or_timbre_change_only": True,
    "content_preservation_is_separate_from_target_similarity": True,
    "target_similarity_is_not_speaker_identity_gold": True,
    "prosody_and_delay_are_separate_outcomes": True,
    "streaming_label_is_not_low_conversational_delay": True,
    "not_accent_conversion": "TRN-03",
    "not_tts_or_voice_cloning": "TRN-05",
    "not_time_scale_modification": "TRN-01",
    "not_pitch_or_prosody_only": "TRN-02",
    "not_source_separation": "SPK-01",
    "not_target_speaker_extraction": "SPK-02",
    "not_quality_assessment": "OBS-01",
    "not_speech_enhancement": "CLN-01",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S38",
        "title": "StreamVC paper",
        "url": "https://arxiv.org/html/2401.03078v1",
        "access_scope": "direct",
        "mapped_components": ["streamvc"],
        "gap_ids": ["G07"],
        "finding": (
            "Direct paper lead for mobile streaming voice conversion. The pinned "
            "local evaluation says the available unofficial repository has no "
            "trained checkpoint and does not implement the paper-style streaming "
            "inference, so the lead cannot be run as a pretrained converter and no "
            "local converted audio or latency result exists."
        ),
    },
    {
        "source_id": "S39",
        "title": "Seed-VC upstream implementation",
        "url": "https://github.com/Plachtaa/seed-vc/blob/main/README.md",
        "access_scope": "direct",
        "mapped_components": [
            "seed-vc-25m",
            "seed-vc-xls-r-300m-content-encoder",
        ],
        "gap_ids": ["G05", "G06", "G07"],
        "finding": (
            "Direct upstream implementation lead for zero-shot streaming voice "
            "conversion. The pinned local screen converted one fixed source/target "
            "pair with the public 25M real-time preset in file mode on CPU; the "
            "streaming GUI/device path was not exercised, the warm file RTF was "
            "0.244, and the weights and XLS-R encoder were removed after the run. "
            "A separate 240 ms Realtime block exists but is one first block, not a "
            "sustained stream."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": (
            "Statistical spectral mapping with vocoders; GMM family to search "
            "(no catalogued component supplies the statistical mapping stage)"
        ),
        "components": ["vocos-vocoder", "hifi-gan-vocoder", "ms-istft-generator"],
        "gap_ids": ["G08", "G09"],
        "status": "catalogued_classic_family_vocoder_boundary_only_no_gmm_component",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": (
            "Neural resynthesis/vocoder boundary for a spectral conversion stage, "
            "not a complete statistical or GMM voice converter"
        ),
        "components": ["univnet", "micro-hifi-gan", "fregan"],
        "gap_ids": ["G09"],
        "status": "component_only_no_acoustic_converter_or_paired_features",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": (
            "Content/speaker-disentangled decoders for zero-shot and "
            "target-trained voice conversion"
        ),
        "components": [
            "meanvc2",
            "meanvc",
            "seed-vc-25m",
            "seed-vc-xls-r-300m-content-encoder",
            "llvc",
            "openvoice-v2",
            "chatterbox-vc",
            "rvc-v2-vctk-p226",
            "rvc-faiss-retrieval",
            "rvc-mlx-realtime",
            "contentvec",
            "hubert-conversion-encoder",
            "wavlm-conversion-encoder",
            "quickvc",
        ],
        "gap_ids": ["G03", "G04", "G05", "G06", "G07", "G12"],
        "status": "historical_one_pair_screens_and_blocked_or_considered_rows",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": (
            "Streaming and flow/diffusion variants of voice conversion"
        ),
        "components": [
            "streamvc",
            "x-vc",
            "rt-vc",
            "dualvc-3",
            "vits-streaming-adaptation",
            "vocos",
        ],
        "gap_ids": ["G05", "G06", "G07"],
        "status": "blocked_or_considered_no_sustained_stream_or_device_run",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml-adjacent",
        "family": (
            "Reference-conditioned TTS and voice-cloning boundary (TRN-05), "
            "not speech-to-speech conversion of the supplied utterance"
        ),
        "components": [
            "cosyvoice-2-0-5b",
            "chatterbox-nano",
            "kokoro-82m",
            "neutts-nano-q4",
            "yourtts",
        ],
        "gap_ids": ["G07", "G10"],
        "status": "adjacent_tts_or_cloning_not_speech_to_speech_conversion",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml-adjacent",
        "family": (
            "Accent-conversion boundary (TRN-03), not designated-speaker/timbre "
            "conversion"
        ),
        "components": [
            "tokan",
            "seed-vc-v2-accent-aware-path",
            "streaming-non-autoregressive-accent-conversion",
            "psdn-zero-shot-ac",
            "convert-and-speak",
            "voice-preserving-zero-shot-multiple-accent-conversion",
            "ppg-foreign-accent-conversion",
        ],
        "gap_ids": ["G10", "G11"],
        "status": "adjacent_accent_conversion_evidence_not_timbre_conversion",
    },
]

# component_id, role, task and evidence_status are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "vocos-vocoder", "role": "vocoder_boundary_control", "evidence_status": "considered", "task": "SDK-VOCOS-VOCODER"},
    {"component_id": "hifi-gan-vocoder", "role": "vocoder_boundary_control", "evidence_status": "considered", "task": "SDK-HIFI-GAN-VOCODER"},
    {"component_id": "ms-istft-generator", "role": "vocoder_boundary_component", "evidence_status": "considered", "task": "SDK-MS-ISTFT-GENERATOR"},
    {"component_id": "univnet", "role": "vocoder_boundary_component", "evidence_status": "considered", "task": "SDK-UNIVNET"},
    {"component_id": "micro-hifi-gan", "role": "vocoder_boundary_component", "evidence_status": "considered", "task": "SDK-MICRO-HIFI-GAN"},
    {"component_id": "fregan", "role": "vocoder_boundary_component", "evidence_status": "considered", "task": "SDK-FREGAN"},
    {"component_id": "meanvc2", "role": "zero_shot_streaming_vc_historical_screen", "evidence_status": "partial", "task": "SDK-MEANVC2"},
    {"component_id": "meanvc", "role": "previous_generation_streaming_vc_candidate", "evidence_status": "considered", "task": "SDK-MEANVC"},
    {"component_id": "seed-vc-25m", "role": "zero_shot_streaming_vc_historical_screen", "evidence_status": "partial", "task": "SDK-SEED-VC-25M"},
    {"component_id": "seed-vc-xls-r-300m-content-encoder", "role": "content_encoder_in_seed_vc_path", "evidence_status": "partial", "task": "SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER"},
    {"component_id": "llvc", "role": "low_latency_any_to_one_vc_historical_screen", "evidence_status": "partial", "task": "SDK-LLVC"},
    {"component_id": "openvoice-v2", "role": "offline_tone_color_vc_historical_screen", "evidence_status": "partial", "task": "SDK-OPENVOICE-V2"},
    {"component_id": "chatterbox-vc", "role": "offline_audio_to_audio_vc_historical_screen", "evidence_status": "partial", "task": "SDK-CHATTERBOX-VC"},
    {"component_id": "rvc-v2-vctk-p226", "role": "target_trained_vc_historical_screen", "evidence_status": "partial", "task": "SDK-RVC-V2-VCTK-P226"},
    {"component_id": "rvc-faiss-retrieval", "role": "rvc_retrieval_component_blocked_by_native_crash", "evidence_status": "partial", "task": "SDK-RVC-FAISS-RETRIEVAL"},
    {"component_id": "rvc-mlx-realtime", "role": "rvc_realtime_source_local_wrapper", "evidence_status": "source-local", "task": "SDK-RVC-MLX-REALTIME"},
    {"component_id": "contentvec", "role": "content_encoder_component_lead", "evidence_status": "considered", "task": "SDK-CONTENTVEC"},
    {"component_id": "hubert-conversion-encoder", "role": "content_encoder_component_blocked", "evidence_status": "blocked", "task": "SDK-HUBERT-CONVERSION-ENCODER"},
    {"component_id": "wavlm-conversion-encoder", "role": "content_encoder_component_blocked", "evidence_status": "blocked", "task": "SDK-WAVLM-CONVERSION-ENCODER"},
    {"component_id": "quickvc", "role": "generic_vc_component_lead", "evidence_status": "considered", "task": "SDK-QUICKVC"},
    {"component_id": "streamvc", "role": "mobile_streaming_vc_paper_lead_blocked", "evidence_status": "blocked", "task": "SDK-STREAMVC"},
    {"component_id": "x-vc", "role": "experimental_zero_shot_vc_lead_blocked", "evidence_status": "blocked", "task": "SDK-X-VC"},
    {"component_id": "rt-vc", "role": "streaming_vc_lead_blocked_no_checkpoint", "evidence_status": "blocked", "task": "SDK-RT-VC"},
    {"component_id": "dualvc-3", "role": "streaming_generic_vc_lead", "evidence_status": "considered", "task": "SDK-DUALVC-3"},
    {"component_id": "vits-streaming-adaptation", "role": "streaming_synthesis_boundary_lead", "evidence_status": "considered", "task": "SDK-VITS-STREAMING-ADAPTATION"},
    {"component_id": "vocos", "role": "decoder_only_timing_component", "evidence_status": "partial", "task": "SDK-VOCOS"},
    {"component_id": "cosyvoice-2-0-5b", "role": "tts_cloning_boundary_partial", "evidence_status": "partial", "task": "SDK-COSYVOICE-2-0-5B"},
    {"component_id": "chatterbox-nano", "role": "tts_cloning_boundary_partial", "evidence_status": "partial", "task": "SDK-CHATTERBOX-NANO"},
    {"component_id": "kokoro-82m", "role": "fixed_voice_tts_boundary_partial", "evidence_status": "partial", "task": "SDK-KOKORO-82M"},
    {"component_id": "neutts-nano-q4", "role": "gated_tts_boundary_partial", "evidence_status": "partial", "task": "SDK-NEUTTS-NANO-Q4"},
    {"component_id": "yourtts", "role": "tts_cloning_boundary_blocked", "evidence_status": "blocked", "task": "SDK-YOURTTS"},
    {"component_id": "tokan", "role": "accent_conversion_boundary_partial", "evidence_status": "partial", "task": "SDK-TOKAN"},
    {"component_id": "seed-vc-v2-accent-aware-path", "role": "accent_aware_vc_boundary_lead", "evidence_status": "considered", "task": "SDK-SEED-VC-V2-ACCENT-AWARE-PATH"},
    {"component_id": "streaming-non-autoregressive-accent-conversion", "role": "streaming_accent_conversion_boundary_lead", "evidence_status": "considered", "task": "SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION"},
    {"component_id": "psdn-zero-shot-ac", "role": "zero_shot_accent_conversion_boundary_lead", "evidence_status": "considered", "task": "SDK-PSDN-ZERO-SHOT-AC"},
    {"component_id": "convert-and-speak", "role": "accent_conversion_boundary_lead", "evidence_status": "considered", "task": "SDK-CONVERT-AND-SPEAK"},
    {"component_id": "voice-preserving-zero-shot-multiple-accent-conversion", "role": "multi_accent_conversion_boundary_lead", "evidence_status": "considered", "task": "SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION"},
    {"component_id": "ppg-foreign-accent-conversion", "role": "classical_accent_conversion_boundary_lead", "evidence_status": "considered", "task": "SDK-PPG-FOREIGN-ACCENT-CONVERSION"},
]

EXCLUDED_BOUNDARIES: List[Dict[str, str]] = [
    {
        "boundary": "Time-scale and pitch-preserving speed modification (TRN-01)",
        "reason": "A rate change with preserved pitch is not a change of speaker or timbre and does not convert the target voice.",
    },
    {
        "boundary": "Pitch and limited prosody control (TRN-02)",
        "reason": "Pitch, duration and energy controls alone do not implement content/speaker-disentangled voice conversion.",
    },
    {
        "boundary": "Accent conversion (TRN-03)",
        "reason": "Changing pronunciation toward a target accent is not changing the designated speaker's timbre or identity.",
    },
    {
        "boundary": "Reference-conditioned voice cloning and TTS (TRN-05)",
        "reason": "Text-to-speech or cloning generates speech from text; it is not conversion of the supplied source utterance.",
    },
    {
        "boundary": "Generic speech/source separation (SPK-01)",
        "reason": "Recovering multiple source waveforms from a mixture is not converting one source speaker to a target voice.",
    },
    {
        "boundary": "Target-speaker extraction and personalized enhancement (SPK-02)",
        "reason": "Extracting or enhancing a known speaker in a mixture is not generating the same content in another voice.",
    },
    {
        "boundary": "Quality and impairment assessment (OBS-01) and enhancement (CLN-01)",
        "reason": "A converted waveform is not a quality score, and denoising or suppression is not voice conversion.",
    },
    {
        "boundary": "Recognition, translation and language identification (REC)",
        "reason": "A transcript, translation or language label is not converted speech or a target-voice result.",
    },
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": (
            "Fixed 9.655 s LJ Speech source LJ001-0001 and 3.562 s RT-VC upstream "
            "p360 target reference used across the zero-shot candidates"
        ),
        "class": "historical_local_fixed_source_target_pair",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": (
            "One English source utterance and one target reference; the target "
            "reference is an upstream demo whose dataset/license provenance is not "
            "confirmed and no consent or output-use record is staged."
        ),
    },
    {
        "id": "CI-2",
        "input": (
            "MeanVC2 40+40 ms and 120+40 ms streaming configurations fed in file "
            "mode on CPU with the fixed source and p360 target"
        ),
        "class": "historical_local_meanvc2_file_conversion",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": (
            "File-mode runs through the streaming chunk runner; no physical "
            "microphone, device buffering, first-output/tail distribution or "
            "sustained stream was measured."
        ),
    },
    {
        "id": "CI-3",
        "input": (
            "Seed-VC 25M real-time preset file conversion with four diffusion "
            "steps and guidance rate 0.0 on the fixed source and p360 target"
        ),
        "class": "historical_local_seedvc_file_conversion",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": (
            "Warm file RTF only; the streaming GUI/device path was not exercised, "
            "the XLS-R encoder and weights were removed after the run, and no "
            "sustained-stream result exists."
        ),
    },
    {
        "id": "CI-4",
        "input": (
            "LLVC upstream infer.py streaming simulation, chunk factor 1, 13 ms "
            "chunks, on the fixed 9.655 s source"
        ),
        "class": "historical_local_llvc_streaming_simulation",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": (
            "A CPU stream simulation that misses the 13 ms chunk deadline; the "
            "reported 120.785 ms is an upstream estimate, not an observed "
            "device-to-device call latency, and target similarity was not scored."
        ),
    },
    {
        "id": "CI-5",
        "input": (
            "OpenVoice V2 offline tone-color conversion and Chatterbox VC "
            "offline audio-to-audio conversion on the fixed pair"
        ),
        "class": "historical_local_offline_vc_conversion",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": (
            "Whole-file offline converters; the OpenVoice cosine is an in-model "
            "diagnostic and Chatterbox VC is a third-party offline package with "
            "CPU RTF 2.63, so neither establishes live-call behaviour."
        ),
    },
    {
        "id": "CI-6",
        "input": (
            "RVC v2 VCTK p226 checkpoint through the official RVC PyTorch file "
            "pipeline with RMVPE F0 and retrieval disabled"
        ),
        "class": "historical_local_rvc_target_conversion",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": (
            "The speaker id 1 to p226 mapping is presumed and unverified, the "
            "FAISS retrieval index crashes in native code, and the MLX realtime "
            "fork cannot initialize without Metal; no live path exists."
        ),
    },
    {
        "id": "CI-7",
        "input": (
            "One 240 ms Seed-VC Realtime block with 2.2 s left context, 0.2 s "
            "right context and 10 diffusion steps"
        ),
        "class": "historical_local_seedvc_single_block",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "boundary": (
            "One first block on a generic VC path; the output is too short for "
            "meaningful ASR or identity comparison, and the 92.55x real-time "
            "block time is not a warmed-up sustained stream."
        ),
    },
    {
        "id": "CI-8",
        "input": (
            "Synthetic 1 s 80-bin mel through the MeanVC2-bundled Vocos JIT "
            "decoder on CPU"
        ),
        "class": "historical_local_vocos_decoder_timing",
        "source_pin": "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json",
        "boundary": (
            "Decoder-only timing on synthetic features; it is not an end-to-end "
            "converter, not a quality result and not a pipeline latency result."
        ),
    },
    {
        "id": "CI-9",
        "input": (
            "StreamVC paper (S38) and Seed-VC upstream implementation (S39) "
            "source leads"
        ),
        "class": "source_reported_streamvc_lead",
        "source_pin": "research/category_survey/sources.md",
        "boundary": (
            "Documentation and paper leads only; StreamVC has no trained "
            "checkpoint and Seed-VC's upstream GPU GUI profile is not reproduced "
            "here."
        ),
    },
    {
        "id": "CI-10",
        "input": (
            "Rights-cleared multi-speaker, multi-target voice-conversion cohort "
            "with consented references, manual transcripts and independent "
            "listening labels"
        ),
        "class": "missing_rights_cleared_vc_cohort",
        "source_pin": "audio_categories.md",
        "boundary": (
            "Not present in this task or the pinned research; no consent, split, "
            "target reference, manual transcript or listening label is staged."
        ),
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "source/identity clip",
        "role": "The unmodified source utterance is the content reference for every historical pair; it is not a converted output or a target-voice control.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-2",
        "name": "Whisper Tiny ASR transcript preservation",
        "role": "Same-transcript WER proxy on one short English utterance; it is not comprehension, manual transcription or prosody preservation.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-3",
        "name": "target speaker-embedding cosine",
        "role": "In-model target-similarity diagnostic; it is not an independent identity rating or a perceptual naturalness result.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-4",
        "name": "target reference provenance check",
        "role": "The p360 reference is an upstream demo whose dataset/license provenance and consent are not confirmed, so it remains a research-only condition.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-5",
        "name": "input/output duration ratio",
        "role": "Duration change exposes shortening or expansion; it is not a content, prosody or identity measure.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-6",
        "name": "blocked-row no-substitution gate",
        "role": "StreamVC, RT-VC and X-VC are not replaced by unverified or differently licensed mirrors; candidate identity is preserved.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-7",
        "name": "offline-versus-streaming separation",
        "role": "File RTF and whole-file conversion are never reported as microphone-to-output or first-audio latency.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-8",
        "name": "decoder-only synthetic mel",
        "role": "Vocos timing uses synthetic features and cannot stand in for an end-to-end voice converter.",
        "source_pin": "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "LJ Speech 1.1 source clip LJ001-0001",
        "class": "research_audio",
        "status": "Public-domain dataset description in the cited report; bytes are not staged or played in this task.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "RT-VC upstream p360 target reference",
        "class": "research_audio",
        "status": "Upstream demo reference; dataset/license provenance and consent are not confirmed, so it is research-only.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "MeanVC2, Seed-VC, LLVC, OpenVoice and Chatterbox VC weight bundles",
        "class": "external_weights_metadata_only",
        "status": "Metadata only; weights were downloaded, run historically and removed; exact revisions and terms are not staged here.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "RVC v2 VCTK p226 checkpoint and 137 MB FAISS index",
        "class": "external_weights_metadata_only",
        "status": "Metadata only; the 109-embedding checkpoint has no speaker_info map, speaker_id 1 is presumed p226, and the FAISS search crashes natively.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "Vocos JIT decoder bundled with MeanVC2",
        "class": "external_model_metadata_only",
        "status": "Metadata only; decoder-level timing on synthetic mel, not an end-to-end converter.",
        "source_pin": "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json",
    },
    {
        "asset": "CosyVoice 2, Chatterbox Nano, Kokoro and NeuTTS TTS bundles",
        "class": "external_weights_metadata_only",
        "status": "TTS/cloning boundary metadata only; none is a speech-to-speech converter and no weight is staged here.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "TokAN and L2-ARCTIC accent-conversion bundle",
        "class": "external_weights_metadata_only",
        "status": "TRN-03 boundary metadata only; the accent smoke run used same-clip references and is not a TRN-04 timbre-conversion result.",
        "source_pin": "research/accent-conversion-20261101/README.md",
    },
    {
        "asset": "Rights-cleared multi-speaker, multi-target conversion cohort",
        "class": "missing_asset",
        "status": "No rights-cleared cohort, consent record, target-reference set, speaker/language split or listening label is staged.",
        "source_pin": "audio_categories.md",
    },
    {
        "asset": "Installed v0 headers and contracts",
        "class": "read_only_boundary",
        "status": "Pinned provenance only; 16 kHz mono float32 160-sample geometry is unchanged and no SDK callback is invoked.",
        "source_pin": "CONTRACTS.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "MeanVC2 40+40 ms file-mode conversion",
        "outcome_class": "historical_local_meanvc2_file_conversion",
        "component_ids": ["meanvc2"],
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "zero_shot_streaming_vc_file_mode_screen",
        "values": {
            "config_ms": "40+40",
            "model_init_s": 14.4,
            "file_process_s": 9.35,
            "output_duration_s": 9.75,
            "file_rtf": 0.959,
            "wer": 0.0,
            "clipped_sample_fraction": 0.0,
            "target_encoder_cosine": 0.669,
            "output_sha256": "e0aa57f7870e70c6a7d7fc52fb1250e387458ec90b2840847b0dfe6cf2721f3b",
            "physical_microphone_measured": False,
            "sustained_stream": False,
            "single_source_target_pair": True,
        },
        "scope": (
            "One fixed English source utterance and one p360 target reference, "
            "file mode through the streaming chunk runner on one Apple M1 CPU. "
            "Whisper-tiny WER and the in-model target-encoder cosine are proxies; "
            "there is no physical microphone, device timing, listening or "
            "multi-speaker result. not rerun by this survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "MeanVC2 120+40 ms file-mode conversion",
        "outcome_class": "historical_local_meanvc2_file_conversion",
        "component_ids": ["meanvc2"],
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "zero_shot_streaming_vc_file_mode_screen",
        "values": {
            "config_ms": "120+40",
            "model_init_s": 15.2,
            "file_process_s": 3.79,
            "output_duration_s": 9.59,
            "file_rtf": 0.396,
            "wer": 0.0,
            "clipped_sample_fraction": 0.0,
            "target_encoder_cosine": 0.702,
            "output_sha256": "e0c7a64655f2d86feddb007cb676d8482eca48c8c54d09b520ea5bda8a556d59",
            "physical_microphone_measured": False,
            "sustained_stream": False,
            "single_source_target_pair": True,
        },
        "scope": (
            "The same fixed source/target pair and host as HE-1, with the 120+40 "
            "ms configuration in file mode. The faster file RTF is not a "
            "microphone-to-output or first-audio latency result. not rerun by "
            "this survey."
        ),
    },
    {
        "id": "HE-3",
        "label": "Seed-VC 25M file conversion",
        "outcome_class": "historical_local_seedvc_file_conversion",
        "component_ids": ["seed-vc-25m", "seed-vc-xls-r-300m-content-encoder"],
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "zero_shot_streaming_vc_file_mode_screen",
        "values": {
            "preset": "seed-uvit-tat-xlsr-tiny 25M",
            "diffusion_steps": 4,
            "guidance_rate": 0.0,
            "first_run_rtf": 1.32,
            "warm_file_rtf": 0.244,
            "output_duration_s": 9.648,
            "wer": 0.0,
            "clipped_sample_fraction": 0.0,
            "output_sha256": "493f8413de8f597a4344fc62d7cda26792223b36e69375df5f503f4242e6d62a",
            "streaming_gui_exercised": False,
            "sustained_stream": False,
            "single_source_target_pair": True,
        },
        "scope": (
            "Public 25M real-time preset, fixed source and p360 target, CPU file "
            "inference with four diffusion steps. The warm RTF is file "
            "throughput; the GUI/device path was not exercised and the weights "
            "were removed after the run. not rerun by this survey."
        ),
    },
    {
        "id": "HE-4",
        "label": "LLVC CPU streaming simulation",
        "outcome_class": "historical_local_llvc_streaming_simulation",
        "component_ids": ["llvc"],
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "low_latency_any_to_one_stream_simulation",
        "values": {
            "commit": "1627c5d",
            "chunk_ms": 13,
            "mean_inference_ms_per_chunk": 106,
            "reported_rtf": 0.123,
            "reported_estimated_latency_ms": 120.785,
            "cold_run_s": 78.836,
            "input_duration_s": 9.655,
            "output_duration_s": 9.655,
            "source_wer": 0.037,
            "output_wer": 0.0,
            "output_sha256": "ac83ede41c7aa9b73216a1647a8aba6f74aec01826ed18c36f44d0129fd60327",
            "target_similarity_scored": False,
            "device_latency_measured": False,
            "any_to_one": True,
        },
        "scope": (
            "Upstream infer.py streaming simulation, chunk factor 1, 16 kHz, on "
            "one fixed source. It misses the 13 ms chunk deadline by a wide "
            "margin; 120.785 ms is the upstream estimate and not a measured "
            "device-to-device latency. Target similarity is unscored. not rerun "
            "by this survey."
        ),
    },
    {
        "id": "HE-5",
        "label": "OpenVoice V2 offline tone-color conversion",
        "outcome_class": "historical_local_offline_vc_conversion",
        "component_ids": ["openvoice-v2"],
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "offline_tone_color_vc_screen",
        "values": {
            "model_init_s": 0.38,
            "speaker_embedding_s": 0.90,
            "conversion_s": 3.29,
            "input_duration_s": 9.648,
            "file_rtf": 0.341,
            "wer": 0.0,
            "clipped_sample_fraction": 0.0,
            "in_model_speaker_cosine": 0.890,
            "output_sample_rate_hz": 22050,
            "output_sha256": "1e1fac98e38da71999f6bfe0ca65879c82f7be104dd958f27eb5a0d2bb2709f7",
            "offline_whole_utterance": True,
            "causal_streaming_path": False,
        },
        "scope": (
            "Whole-file offline tone-color conversion on one fixed pair. The "
            "cosine is OpenVoice's own in-model diagnostic, not an independent "
            "or perceptual identity score; no causal streaming path exists. "
            "not rerun by this survey."
        ),
    },
    {
        "id": "HE-6",
        "label": "Chatterbox VC offline audio-to-audio conversion",
        "outcome_class": "historical_local_offline_vc_conversion",
        "component_ids": ["chatterbox-vc"],
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "offline_audio_to_audio_vc_screen",
        "values": {
            "model_init_s": 129.6,
            "conversion_s": 25.47,
            "output_duration_s": 9.68,
            "file_rtf": 2.63,
            "wer": 0.0,
            "clipped_sample_fraction": 0.0,
            "output_sha256": "946f3e02ba25df3511f6ca548121b9304196dcffd39a63b52dd7a1c6e7aa262c",
            "offline_whole_file": True,
            "streaming": False,
        },
        "scope": (
            "Third-party offline audio-to-audio converter on one fixed pair, CPU "
            "RTF 2.63. It is whole-file and far slower than real time on the "
            "historical host, so it is not a live-call result. not rerun by this "
            "survey."
        ),
    },
    {
        "id": "HE-7",
        "label": "RVC v2 VCTK p226 file conversion",
        "outcome_class": "historical_local_rvc_target_conversion",
        "component_ids": ["rvc-v2-vctk-p226"],
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "target_trained_vc_file_screen",
        "values": {
            "checkpoint": "Nekochu/RVC-VCTK_Voice-sample p226 path",
            "device": "cpu",
            "threads": 4,
            "f0_method": "RMVPE",
            "retrieval": False,
            "init_plus_hubert_s": 0.35,
            "conversion_s": 7.75,
            "output_duration_s": 9.64,
            "file_rtf": 0.804,
            "wer": 0.0,
            "clipped_sample_fraction": 0.0,
            "output_sample_rate_hz": 40000,
            "speaker_id": 1,
            "speaker_map_present": False,
            "target_mapping_verified": False,
            "faiss_index_enabled": False,
            "faiss_native_crash": True,
            "output_sha256": "7fa0516e7475b6870267da9f4a894d0d18e67714e1081cd9d3c7d63db30bd8c7",
            "real_time_device_path": False,
        },
        "scope": (
            "Official RVC PyTorch file pipeline with RMVPE F0 and retrieval "
            "disabled. The 109-embedding checkpoint has no speaker_info map, "
            "speaker_id 1 is presumed p226 and unverified, the FAISS index "
            "crashes, and no real-time/device path was run. not rerun by this "
            "survey."
        ),
    },
    {
        "id": "HE-8",
        "label": "Seed-VC Realtime one 240 ms block",
        "outcome_class": "historical_local_seedvc_single_block",
        "component_ids": ["seed-vc-xls-r-300m-content-encoder", "seed-vc-25m"],
        "source_pin": "research/accent-conversion-20261101/README.md",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "generic_vc_streaming_block_smoke",
        "values": {
            "block_ms": 240,
            "left_context_s": 2.2,
            "right_context_s": 0.2,
            "diffusion_steps": 10,
            "model_load_s": 254.01,
            "block_compute_s": 22.21,
            "block_realtime_factor": 92.55,
            "output_sample_rate_hz": 22050,
            "finite_output": True,
            "asr_comparison_meaningful": False,
            "accent_aware_v2_path": False,
            "sustained_stream": False,
            "device_latency_measured": False,
        },
        "scope": (
            "One first 240 ms block through upstream Seed-VC Realtime custom_infer "
            "on CPU. It is a generic VC path, not the accent-aware V2 path; the "
            "output is too short for meaningful ASR or identity comparison and "
            "the block is not a warmed-up sustained stream. not rerun by this "
            "survey."
        ),
    },
    {
        "id": "HE-9",
        "label": "Vocos JIT decoder CPU timing on synthetic mel",
        "outcome_class": "historical_local_vocos_decoder_timing",
        "component_ids": ["vocos"],
        "source_pin": "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "decoder_only_timing_component",
        "values": {
            "device": "cpu",
            "input_mel_shape": [1, 80, 100],
            "output_shape": [1, 15840],
            "output_duration_s": 0.99,
            "mean_decode_s": 0.17284687500214205,
            "rtf": 0.17459280303246671,
            "finite_output": True,
            "end_to_end_conversion": False,
            "quality_assessed": False,
        },
        "scope": (
            "Decoder-only CPU timing on a synthetic 1 s 80-bin mel input, mean "
            "over five post-warm-up calls. It is not voice conversion, not an "
            "end-to-end pipeline latency and not a quality assessment. not rerun "
            "by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, Any]] = [
    {
        "id": "RO-1",
        "claim": "StreamVC studies low-latency streaming voice conversion for mobile use",
        "class": "source_reported_streamvc_lead",
        "source_pin": "research/category_survey/sources.md",
        "component_ids": ["streamvc"],
        "boundary": "Paper lead only; the available unofficial repository has no trained checkpoint and does not implement paper-style streaming inference.",
    },
    {
        "id": "RO-2",
        "claim": "Seed-VC provides a zero-shot streaming voice-conversion implementation with a 25M real-time preset",
        "class": "source_reported_seedvc_upstream",
        "source_pin": "research/category_survey/sources.md",
        "component_ids": ["seed-vc-25m", "seed-vc-xls-r-300m-content-encoder"],
        "boundary": "Upstream implementation and README scope; local file conversion is separate and the GUI/device path was not reproduced.",
    },
    {
        "id": "RO-3",
        "claim": "MeanVC2 reports an 80 ms chunk-plus-lookahead streaming design figure",
        "class": "source_reported_design_or_model_claim",
        "source_pin": "research/accent-conversion-20261101/README.md",
        "component_ids": ["meanvc2"],
        "boundary": "A design-latency claim, not a measured microphone-to-output latency; the local runs are file mode only.",
    },
    {
        "id": "RO-4",
        "claim": "LLVC reports RTF 0.123 and an estimated streaming end-to-end latency of 120.785 ms",
        "class": "source_reported_design_or_model_claim",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "component_ids": ["llvc"],
        "boundary": "Upstream estimate; the local CPU simulation averaged about 106 ms per 13 ms chunk and is not a device-to-device measurement.",
    },
    {
        "id": "RO-5",
        "claim": "The public RVC VCTK checkpoint is Apache-2.0 and contains 109 speaker embeddings",
        "class": "source_reported_design_or_model_claim",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "component_ids": ["rvc-v2-vctk-p226"],
        "boundary": "Checkpoint metadata only; there is no speaker_info map and the speaker_id 1 to p226 relation is presumed.",
    },
    {
        "id": "RO-6",
        "claim": "OpenVoice V2's published converter processes whole files with no causal streaming path",
        "class": "source_reported_design_or_model_claim",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "component_ids": ["openvoice-v2"],
        "boundary": "Upstream implementation scope; the local run is offline and does not establish first-audio latency.",
    },
    {
        "id": "RO-7",
        "claim": "Seed-VC's published GPU GUI profile uses a 180 ms block and reports 430 ms latency on an RTX 3060 Laptop",
        "class": "source_reported_design_or_model_claim",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "component_ids": ["seed-vc-25m"],
        "boundary": "Upstream GPU report only; the local CPU run exercised file conversion and not the GUI/device path.",
    },
    {
        "id": "RO-8",
        "claim": "The X-VC official HF checkpoint is 5.01 GB and requires GLM-4-Voice and ERes2Net encoders",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "component_ids": ["x-vc"],
        "boundary": "Checkpoint alone exceeds the historical 8 GB host budget; no weight was acquired, loaded or substituted.",
    },
    {
        "id": "RO-9",
        "claim": "StreamVC's unofficial repository has no trained checkpoint and incomplete paper-style streaming inference",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "component_ids": ["streamvc"],
        "boundary": "Cannot run as a pretrained converter; no local audio, score or latency exists.",
    },
    {
        "id": "RO-10",
        "claim": "CosyVoice 2 and Chatterbox Nano are reference-conditioned TTS/cloning systems, not speech-to-speech converters",
        "class": "source_reported_design_or_model_claim",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "component_ids": ["cosyvoice-2-0-5b", "chatterbox-nano"],
        "boundary": "TRN-05 boundary only; their streaming or whole-utterance TTS results are not voice-conversion results.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "permitted_input_and_target_references": "One public-domain-described LJ Speech source and one upstream p360 reference exist historically; the target reference's dataset/license provenance and consent are unconfirmed.",
        "task_and_language_speaker_groups": "One English source utterance and one target speaker form a single pair; no multi-speaker, multi-target or multi-language partition exists.",
        "preserve_text_and_semantic_content": "Whisper-tiny WER 0.00% on one short utterance is a proxy; no manual transcript, comprehension or semantic check exists.",
        "identity_and_similarity": "In-model target-encoder cosine 0.669-0.890 is a diagnostic; no independent identity rating, target-similarity gold or speaker confusion audit exists.",
        "naturalness": "No blinded listening, naturalness rating or prosody-preservation panel was run.",
        "alignment": "No sample-level alignment, duration-policy or first-output/tail measurement exists; file-mode durations are recorded only.",
        "first_output_and_tail_timing": "No first-output/tail distribution exists; one Seed-VC 240 ms block took 22.21 s after 254.01 s model load.",
        "exact_target_condition": "The target condition is one p360 upstream demo reference; no target-voice specification, consent or output-use policy exists.",
        "consent_reference_availability_output_use": "The target reference is an upstream demo with unconfirmed provenance; no consent, redistribution or output-use clearance is staged.",
        "missing_result_accounting": "No rights-cleared multi-speaker conversion cohort, independent listening or device measurement exists; absence is recorded, not promoted.",
    },
    "blocked": [
        "Rights-cleared multi-speaker, multi-target conversion cohort with consented references, manual transcripts and explicit output-use terms",
        "Frozen speaker/language/target partitions with independent blinded listening, naturalness and manual transcript review",
        "Independent target-speaker similarity, content/prosody preservation and duration metrics with uncertainty",
        "Pinned exact model bundles, revisions, per-weight terms and locked runtimes for every compared family",
        "Causal streaming chunk/lookahead, first-output/tail, sustained CPU/accelerator and target-device timing evidence",
        "Explicit target-voice condition and consent policy separating timbre from content, prosody, accent and identity",
        "Opt-in provider or external-adapter intake with independent exact-head review",
        "Release approval; DEFER remains in force until every gate is closed",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class is
# true only when a mapped row backs it; absence is recorded as false instead of
# being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "historical_local_fixed_source_target_pair": True,
    "historical_local_meanvc2_file_conversion": True,
    "historical_local_seedvc_file_conversion": True,
    "historical_local_llvc_streaming_simulation": True,
    "historical_local_offline_vc_conversion": True,
    "historical_local_rvc_target_conversion": True,
    "historical_local_seedvc_single_block": True,
    "historical_local_vocos_decoder_timing": True,
    "source_reported_streamvc_lead": True,
    "source_reported_seedvc_upstream": True,
    "source_reported_design_or_model_claim": True,
    "source_reported_blocked_candidate": True,
    "missing_rights_cleared_vc_cohort": True,
    "real_vc_benchmark": False,
    "human_listening_result": False,
    "independent_speaker_identity_gold": False,
    "target_similarity_gold": False,
    "content_preservation_certificate": False,
    "prosody_preservation_metric": False,
    "sustained_stream_latency": False,
    "device_timing": False,
    "cpu_accelerator_parity": False,
    "latency_claim": False,
    "quality_claim": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "provider_enablement": False,
    "release_approval": False,
    "real_corpus_used_here": False,
    "weights_loaded_here": False,
    "runtime_invoked_here": False,
}

CLASS_BACKING: Dict[str, List[str]] = {
    "historical_local_fixed_source_target_pair": [
        "historical_local_fixed_source_target_pair"
    ],
    "historical_local_meanvc2_file_conversion": [
        "historical_local_meanvc2_file_conversion"
    ],
    "historical_local_seedvc_file_conversion": [
        "historical_local_seedvc_file_conversion"
    ],
    "historical_local_llvc_streaming_simulation": [
        "historical_local_llvc_streaming_simulation"
    ],
    "historical_local_offline_vc_conversion": [
        "historical_local_offline_vc_conversion"
    ],
    "historical_local_rvc_target_conversion": [
        "historical_local_rvc_target_conversion"
    ],
    "historical_local_seedvc_single_block": [
        "historical_local_seedvc_single_block"
    ],
    "historical_local_vocos_decoder_timing": [
        "historical_local_vocos_decoder_timing"
    ],
    "source_reported_streamvc_lead": ["source_reported_streamvc_lead"],
    "source_reported_seedvc_upstream": ["source_reported_seedvc_upstream"],
    "source_reported_design_or_model_claim": ["source_reported_design_or_model_claim"],
    "source_reported_blocked_candidate": ["source_reported_blocked_candidate"],
    "missing_rights_cleared_vc_cohort": ["missing_rights_cleared_vc_cohort"],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Obtain a rights-cleared multi-speaker, multi-target voice-conversion cohort with consented references, manual transcripts and explicit output-use terms",
        "evidence_gap": "The historical evidence is one LJ Speech source and one upstream p360 demo reference; consent, target-reference provenance and output-use clearance are absent.",
        "follow_up_ids": [
            "SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS",
            "SDK-PIPE-VOICE",
            "SDK-FND-EVIDENCE",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner supplies a rights-cleared conversion cohort or consent record here; the linked manifest, pipeline, evidence and dataset rows own manifests and acceptance rules.",
    },
    {
        "id": "G02",
        "actionable_gap": "Run independent blinded listening and manual transcript review for content, naturalness, target similarity and prosody",
        "evidence_gap": "No listening panel, naturalness rating, manual transcript review or prosody comparison exists; Whisper-tiny WER and an in-model cosine are proxies.",
        "follow_up_ids": [
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner collected a listening result; the linked listening-design and evidence-foundation rows own protocols and acceptance rules, and no result is inherited from an adjacent survey.",
    },
    {
        "id": "G03",
        "actionable_gap": "Establish independent target-speaker similarity and identity metrics rather than an in-model encoder cosine",
        "evidence_gap": "MeanVC2 and OpenVoice cosines come from each model's own encoder and are not comparable across candidates; no human rating or independent embedding audit exists.",
        "follow_up_ids": [
            "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY",
            "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has an independent target-similarity result; the linked speaker-similarity proxy and ECAPA research-control rows own proxy metrics, not a target-voice gold.",
    },
    {
        "id": "G04",
        "actionable_gap": "Define content, prosody, duration and alignment preservation metrics beyond one Whisper-tiny transcript check",
        "evidence_gap": "Only same-transcript WER, duration ratios and a zero-clipping check exist; manual words, prosody, alignment and semantic preservation are unmeasured.",
        "follow_up_ids": [
            "SDK-WHISPER-TRANSCRIPTION",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has a prosody or alignment metric; the linked transcription-control and evidence-foundation rows own ASR and acceptance rules.",
    },
    {
        "id": "G05",
        "actionable_gap": "Expand the one-source/one-target screens to multiple source utterances, speakers, languages and target references",
        "evidence_gap": "Every historical conversion is one English source and one p360 target; no cross-speaker, cross-language or cross-target generalization result exists.",
        "follow_up_ids": [
            "SDK-MEANVC2",
            "SDK-SEED-VC-25M",
            "SDK-LLVC",
            "SDK-PIPE-VOICE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has a multi-utterance cohort or completed expansion run; the linked implementation and pipeline rows own the candidates and experiment path.",
    },
    {
        "id": "G06",
        "actionable_gap": "Pin exact revisions, weight terms and locked runtimes for MeanVC2, Seed-VC, LLVC, RVC, OpenVoice and Chatterbox VC",
        "evidence_gap": "Weights were removed after the historical runs; exact revisions, per-weight terms and a locked runtime are not staged, and RVC's speaker map is unverified.",
        "follow_up_ids": [
            "SDK-MEANVC2",
            "SDK-SEED-VC-25M",
            "SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER",
            "SDK-LLVC",
            "SDK-RVC-V2-VCTK-P226",
            "SDK-OPENVOICE-V2",
            "SDK-CHATTERBOX-VC",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has pinned exact weights and terms for these candidates; the linked implementation rows and audit foundation own provenance, and no weight is downloaded or cleared here.",
    },
    {
        "id": "G07",
        "actionable_gap": "Measure causal streaming chunk/lookahead, first-output/tail, sustained-stream and target-device timing",
        "evidence_gap": "MeanVC2 and Seed-VC are file-mode runs, Seed-VC Realtime is one 240 ms block at 92.55x real-time, and no first-output/tail or device measurement exists.",
        "follow_up_ids": [
            "SDK-STREAMVC",
            "SDK-X-VC",
            "SDK-RT-VC",
            "SDK-DUALVC-3",
            "SDK-VITS-STREAMING-ADAPTATION",
            "SDK-FND-TIMING",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked streaming-VC feasibility rows and timing foundation own candidate scoping and the fixed-frame clock; no sustained stream was executed.",
    },
    {
        "id": "G08",
        "actionable_gap": "Build or acquire a runnable classical statistical/GMM spectral-mapping voice converter",
        "evidence_gap": "The catalogued classic family names statistical spectral mapping with vocoders and a GMM search, but no inventory component supplies that mapping stage; only vocoder controls exist.",
        "follow_up_ids": [
            "SDK-PIPE-VOICE",
            "SDK-FND-EVIDENCE",
            "SDK-VOCOS-VOCODER",
            "SDK-HIFI-GAN-VOCODER",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner supplies a classical GMM converter; the linked pipeline and evidence rows own experiments and acceptance, and the vocoder-control rows are components only.",
    },
    {
        "id": "G09",
        "actionable_gap": "Evaluate a neural vocoder/resynthesis component only inside a complete converter with matched acoustic features",
        "evidence_gap": "Vocos timing uses synthetic mel and shape checks; UnivNet, Micro-HiFi-GAN, MS-iSTFT and FreGAN have no matched acoustic model or checkpoint.",
        "follow_up_ids": [
            "SDK-VOCOS",
            "SDK-MS-ISTFT-GENERATOR",
            "SDK-UNIVNET",
            "SDK-MICRO-HIFI-GAN",
            "SDK-FREGAN",
            "SDK-VOCOS-VOCODER",
            "SDK-HIFI-GAN-VOCODER",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked vocoder implementation, feasibility and research-control rows own components; a decoder-only timing is not an end-to-end converter.",
    },
    {
        "id": "G10",
        "actionable_gap": "Keep reference-conditioned TTS and voice cloning (TRN-05) separate from speech-to-speech conversion",
        "evidence_gap": "CosyVoice 2, Chatterbox Nano, Kokoro and NeuTTS are TTS/cloning systems with text or voice prompts; none converts the supplied source waveform to a target timbre.",
        "follow_up_ids": [
            "SDK-COSYVOICE-2-0-5B",
            "SDK-CHATTERBOX-NANO",
            "SDK-KOKORO-82M",
            "SDK-NEUTTS-NANO-Q4",
            "SDK-YOURTTS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked TTS/cloning implementation and feasibility rows own synthesis scope; TTS or cloning is never promoted to a TRN-04 result.",
    },
    {
        "id": "G11",
        "actionable_gap": "Keep accent conversion (TRN-03) separate from designated-speaker/timbre conversion",
        "evidence_gap": "TokAN, Seed-VC V2 accent-aware, streaming accent conversion, PSDN, Convert-and-Speak, multi-accent and PPG rows target pronunciation, not timbre conversion.",
        "follow_up_ids": [
            "SDK-TOKAN",
            "SDK-SEED-VC-V2-ACCENT-AWARE-PATH",
            "SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION",
            "SDK-PSDN-ZERO-SHOT-AC",
            "SDK-CONVERT-AND-SPEAK",
            "SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION",
            "SDK-PPG-FOREIGN-ACCENT-CONVERSION",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked accent-conversion feasibility and implementation rows own pronunciation scope; no accent result is inherited as a voice-conversion result.",
    },
    {
        "id": "G12",
        "actionable_gap": "Resolve RVC's speaker map, FAISS retrieval and accelerator path before any target-similarity comparison",
        "evidence_gap": "The RVC checkpoint has no speaker_info map, speaker_id 1 is presumed p226, the FAISS index crashes natively and the MLX fork cannot initialize without Metal.",
        "follow_up_ids": [
            "SDK-RVC-FAISS-RETRIEVAL",
            "SDK-RVC-MLX-REALTIME",
            "SDK-RVC-V2-VCTK-P226",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has a verified RVC speaker map or successful real-time device path; the linked RVC implementation rows own the candidate, retrieval and wrapper.",
    },
    {
        "id": "G13",
        "actionable_gap": "Define an opt-in provider intake and public exposure path for a voice converter",
        "evidence_gap": "No TRN-04 provider descriptor, installed-archive comparison, default selection or independent review exists.",
        "follow_up_ids": [
            "SDK-FND-PROVIDER",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has provider intake; the linked provider and audit foundation rows own intake boundaries and exact-head evidence, and no converter is registered or exposed.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS", "title": "LJ Speech and consented accent evaluation manifests", "mode": "research-control"},
    {"task_id": "SDK-PIPE-VOICE", "title": "Consented offline voice and accent experiments", "mode": "pipeline"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY", "title": "Resemblyzer speaker-similarity proxy", "mode": "research-control"},
    {"task_id": "SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY", "title": "SpeechBrains ECAPA / speaker similarity", "mode": "research-control"},
    {"task_id": "SDK-WHISPER-TRANSCRIPTION", "title": "Whisper transcription", "mode": "research-control"},
    {"task_id": "SDK-MEANVC2", "title": "MeanVC2", "mode": "implementation"},
    {"task_id": "SDK-SEED-VC-25M", "title": "Seed-VC 25M", "mode": "implementation"},
    {"task_id": "SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER", "title": "Seed-VC XLS-R-300M content encoder", "mode": "implementation"},
    {"task_id": "SDK-LLVC", "title": "LLVC", "mode": "implementation"},
    {"task_id": "SDK-RVC-V2-VCTK-P226", "title": "RVC v2 VCTK p226", "mode": "implementation"},
    {"task_id": "SDK-OPENVOICE-V2", "title": "OpenVoice V2", "mode": "implementation"},
    {"task_id": "SDK-CHATTERBOX-VC", "title": "Chatterbox VC", "mode": "implementation"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-STREAMVC", "title": "StreamVC", "mode": "feasibility"},
    {"task_id": "SDK-X-VC", "title": "X-VC", "mode": "feasibility"},
    {"task_id": "SDK-RT-VC", "title": "RT-VC", "mode": "feasibility"},
    {"task_id": "SDK-DUALVC-3", "title": "DualVC 3", "mode": "feasibility"},
    {"task_id": "SDK-VITS-STREAMING-ADAPTATION", "title": "VITS streaming adaptation", "mode": "feasibility"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-VOCOS", "title": "Vocos", "mode": "implementation"},
    {"task_id": "SDK-MS-ISTFT-GENERATOR", "title": "MS-iSTFT-Generator", "mode": "feasibility"},
    {"task_id": "SDK-UNIVNET", "title": "UnivNet", "mode": "feasibility"},
    {"task_id": "SDK-MICRO-HIFI-GAN", "title": "Micro-HiFi-GAN", "mode": "feasibility"},
    {"task_id": "SDK-FREGAN", "title": "FreGAN", "mode": "feasibility"},
    {"task_id": "SDK-VOCOS-VOCODER", "title": "Vocos vocoder", "mode": "research-control"},
    {"task_id": "SDK-HIFI-GAN-VOCODER", "title": "HiFi-GAN vocoder", "mode": "research-control"},
    {"task_id": "SDK-COSYVOICE-2-0-5B", "title": "CosyVoice 2 0.5B", "mode": "implementation"},
    {"task_id": "SDK-CHATTERBOX-NANO", "title": "Chatterbox Nano", "mode": "implementation"},
    {"task_id": "SDK-KOKORO-82M", "title": "Kokoro 82M", "mode": "implementation"},
    {"task_id": "SDK-NEUTTS-NANO-Q4", "title": "NeuTTS Nano Q4", "mode": "implementation"},
    {"task_id": "SDK-YOURTTS", "title": "YourTTS", "mode": "feasibility"},
    {"task_id": "SDK-TOKAN", "title": "TokAN", "mode": "implementation"},
    {"task_id": "SDK-SEED-VC-V2-ACCENT-AWARE-PATH", "title": "Seed-VC V2 accent-aware path", "mode": "feasibility"},
    {"task_id": "SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION", "title": "Streaming non-autoregressive Accent Conversion", "mode": "feasibility"},
    {"task_id": "SDK-PSDN-ZERO-SHOT-AC", "title": "PSDN zero-shot AC", "mode": "feasibility"},
    {"task_id": "SDK-CONVERT-AND-SPEAK", "title": "Convert and Speak", "mode": "feasibility"},
    {"task_id": "SDK-VOICE-PRESERVING-ZERO-SHOT-MULTIPLE-ACCENT-CONVERSION", "title": "Voice-Preserving Zero-Shot Multiple Accent Conversion", "mode": "feasibility"},
    {"task_id": "SDK-PPG-FOREIGN-ACCENT-CONVERSION", "title": "PPG foreign-accent conversion", "mode": "feasibility"},
    {"task_id": "SDK-RVC-FAISS-RETRIEVAL", "title": "RVC FAISS retrieval", "mode": "implementation"},
    {"task_id": "SDK-RVC-MLX-REALTIME", "title": "RVC-MLX realtime", "mode": "implementation"},
    {"task_id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-cleared multi-speaker, multi-target voice-conversion cohort with consented references, manual transcripts and explicit output-use terms"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen source/target/speaker/language partitions with independent blinded listening, naturalness and manual transcript review"},
    {"id": "RG-03", "blocked": True, "requirement": "Independent target-speaker similarity, content/prosody preservation and duration metrics with uncertainty"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned exact model bundles, revisions, per-weight terms and locked runtimes for every compared family"},
    {"id": "RG-05", "blocked": True, "requirement": "Causal streaming chunk/lookahead, first-output/tail, sustained CPU/accelerator and target-device timing evidence"},
    {"id": "RG-06", "blocked": True, "requirement": "Explicit target-voice condition and consent policy separating timbre from content, prosody, accent and identity"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider or external-adapter intake with independent exact-head review"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded in
# the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "TRN-04 \u2014 Speech-to-speech voice conversion",
        "Change designated speaker/timbre attributes while retaining the spoken content. Scope: requested_optional.",
        "Evaluate target similarity separately from words, prosody and delay; available implementation and weights are required.",
    ],
    "research/category_survey/sources.md": [
        "| S38 | [StreamVC paper](https://arxiv.org/html/2401.03078v1) | transformations | direct |",
        "| S39 | [Seed-VC upstream implementation](https://github.com/Plachtaa/seed-vc/blob/main/README.md) | transformations | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Voice | Freeze permitted input and target references, task and language/speaker groups.",
        "Preserve text and semantic content, identity/similarity and naturalness as separate outcomes.",
        "Consent, reference availability and output use are independent gates.",
    ],
    "research/voice-conversion-eval-20261101/README.md": [
        "The fixed pair gives a shared zero-shot conversion input and reference.",
        "its dataset/license provenance is not yet confirmed",
        "Whisper Tiny English WER was 0.00% for both, no clipped samples.",
        "This is offline whole-utterance processing and does not demonstrate low first-audio latency or live-call streaming.",
        "This is whole-file conversion, not streaming.",
        "that mapping is unverified",
        "The streaming GUI path was not exercised on this CPU-only host.",
        "upstream reports RTF `0.123` and estimated streaming end-to-end latency `120.785 ms`",
        "Upstream author states there is no trained checkpoint and the paper's streaming inference is not implemented.",
        "This is an in-model diagnostic, not an independent or perceptual identity score.",
        "The published 110 ms pipeline latency is an upstream result, not a measurement from this host.",
    ],
    "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md": [
        "All six requested result WAVs below exist",
        "They are not denoising candidates or evidence for an enhancement stage.",
    ],
    "research/voice-conversion-eval-20261101/agent-breadth-audit/REPORT.md": [
        "The expansion was not runnable without restoring exact candidate weights.",
        "one source utterance, one target reference",
    ],
    "research/accent-conversion-20261101/README.md": [
        "This is a streaming voice-conversion path smoke test",
        "254.01 s; conversion of the first block took 22.21 s, or 92.55\u00d7 real-time.",
    ],
    "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json": [
        "Synthetic input; decoder-only timing, not end-to-end voice quality or latency.",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/survey-trn-01/README.md": [
        "read-only survey map",
        "pitch preservation, transient audibility, listening, device timing, public",
    ],
    "docs/task-evidence/survey-spk-01/README.md": [
        "bounded, deterministic **taxonomy and comparison map**",
        "generic speech/source separation",
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
    "historical_citations_include_research_outputs": True,
    "real_speech_used_here": False,
    "real_corpus_used_here": False,
    "weights_loaded_here": False,
    "runtime_invoked_here": False,
    "model_inference_here": False,
    "streaming_inference_here": False,
    "listening_here": False,
    "device_timing_here": False,
    "latency_claim": False,
    "benchmark_claim": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "voice_conversion_quality_claim": False,
    "target_similarity_claim": False,
    "content_preservation_claim": False,
    "identity_preservation_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
}

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}

NON_CLAIMS: List[str] = [
    "no voice-conversion quality, target-similarity or model-ranking result is measured by this survey",
    "no independent listening panel, manual transcript review or target-voice gold exists",
    "no sustained streaming, first-output/tail or device timing is measured",
    "no speaker identity rating, content-preservation certificate or consent clearance is produced",
    "no real corpus, weights or runtime is loaded in this task",
    "no benchmark, latency, quality or release claim is made",
    "no provider, default, ABI, build, CI, board or handoff change is made",
]

ADVERSE_REJECTIONS: Dict[str, str] = {
    "duplicate_json_key": "rejected; state unchanged",
    "nonfinite_json_number": "rejected; state unchanged",
    "missing_pinned_file": "rejected; state unchanged",
    "tampered_pin": "rejected; state unchanged",
    "unknown_board_task": "rejected; state unchanged",
    "gap_without_link_or_reason": "rejected; state unchanged",
    "invalid_payload_type": "rejected; state unchanged",
    "missing_required_cohort_promoted": "rejected; state unchanged",
    "streaming_execution_promoted": "rejected; state unchanged",
    "listening_or_identity_result_promoted": "rejected; state unchanged",
    "tts_or_accent_result_promoted": "rejected; state unchanged",
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
        raise MapError("TRN-04 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("TRN-04 taxonomy mismatch: %s" % key)
    if inventory_hit[0].get("task") != TASK:
        raise MapError("TRN-04 inventory task mismatch")
    if inventory_hit[0].get("legacy_family") != LEGACY_FAMILY:
        raise MapError("TRN-04 legacy family mismatch")
    if inventory_hit[0].get("legacy_backlog_state") != "catalogued":
        raise MapError("TRN-04 legacy backlog state mismatch")
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
        raise MapError("legacy family F14 / TRN-04 is not unique")
    entry = hits[0]
    expected = {
        "category_id": CATEGORY_ID,
        "family_id": LEGACY_FAMILY,
        "activation_state": "catalogued",
        "state": "catalogued",
        "scope": "requested_optional",
        "next_action": "Plan discovery across required source buckets",
        "blockers": [],
        "dependencies": [],
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise MapError("legacy backlog mismatch: F14/TRN-04/%s" % key)


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
    missing = sorted(mapped - set(by_id))
    if missing:
        raise MapError("mapped component missing from inventory: " + ",".join(missing))
    uncensused = sorted(mapped - {row["component_id"] for row in COMPONENT_CENSUS})
    if uncensused:
        raise MapError("mapped component is not censused: " + ",".join(uncensused))


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


def _check_evidence_classes() -> None:
    observed = set()
    for row in COMPARISON_INPUTS:
        observed.add(row["class"])
    for row in HISTORICAL_EXECUTIONS:
        observed.add(row["outcome_class"])
    for row in REPORTED_OUTCOMES:
        observed.add(row["class"])
    for key, value in EVIDENCE_CLASSES.items():
        backed = bool(observed & set(CLASS_BACKING.get(key, [])))
        if value is True and not backed:
            raise MapError("supported evidence class has no mapped row: " + key)
        if value is False and backed:
            raise MapError("evidence class is contradicted by a mapped row: " + key)
    critical_false = {
        "real_vc_benchmark",
        "human_listening_result",
        "independent_speaker_identity_gold",
        "target_similarity_gold",
        "content_preservation_certificate",
        "prosody_preservation_metric",
        "sustained_stream_latency",
        "device_timing",
        "cpu_accelerator_parity",
        "latency_claim",
        "quality_claim",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "provider_enablement",
        "release_approval",
        "real_corpus_used_here",
        "weights_loaded_here",
        "runtime_invoked_here",
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
        "streaming_inference_here",
        "listening_here",
        "device_timing_here",
        "latency_claim",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "voice_conversion_quality_claim",
        "target_similarity_claim",
        "content_preservation_claim",
        "identity_preservation_claim",
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
        "historical_citations_include_research_outputs",
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
        if not gap.get("owner_note"):
            raise MapError("gap has no owner note: " + gap["id"])
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


def _local_component_ids() -> List[str]:
    result = set()
    for row in HISTORICAL_EXECUTIONS:
        result.update(row["component_ids"])
    return sorted(result)


def _reported_component_ids() -> List[str]:
    result = set()
    for row in REPORTED_OUTCOMES:
        result.update(row["component_ids"])
    return sorted(result)


def local_vs_reported_outcomes() -> Dict[str, Any]:
    local = _local_component_ids()
    reported = _reported_component_ids()
    ledger = []
    for component_id in sorted(set(local) | set(reported)):
        local_rows = sorted(
            row["id"] for row in HISTORICAL_EXECUTIONS if component_id in row["component_ids"]
        )
        reported_rows = sorted(
            row["id"] for row in REPORTED_OUTCOMES if component_id in row["component_ids"]
        )
        ledger.append(
            {
                "component_id": component_id,
                "local_rows": local_rows,
                "reported_rows": reported_rows,
                "local_classification": (
                    "historical_local_not_rerun" if local_rows else "no_historical_local_screen"
                ),
                "reported_classification": (
                    "source_reported_not_reproduced" if reported_rows else "no_source_reported_claim"
                ),
                "comparison_performed": False,
                "qualifies_candidate": False,
            }
        )
    return {
        "local": {
            "recorded_in": "historical_executions",
            "classification": "historical_local_not_rerun",
            "count": len(HISTORICAL_EXECUTIONS),
            "component_ids": local,
            "qualifies_candidate": False,
        },
        "reported": {
            "recorded_in": "reported_outcomes",
            "classification": "source_reported_not_reproduced",
            "count": len(REPORTED_OUTCOMES),
            "component_ids": reported,
            "qualifies_candidate": False,
        },
        "cross_comparison": {
            "performed": False,
            "numeric_parity_claimed": False,
            "reason": (
                "No matched frozen asset, runtime, settings or listening protocol is shared "
                "between the historical local screens and the upstream reported claims; no "
                "numeric parity or outcome promotion is performed."
            ),
        },
        "ledger": ledger,
    }


def release_boundary() -> Dict[str, Any]:
    return {
        "release_allowed": False,
        "release_claim": False,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "status": STATUS,
        "installed_v0_geometry": copy.deepcopy(FORMAT),
        "provider_registration": False,
        "enabled_by_default": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "board_write": False,
        "handoff_write": False,
        "gated_claims": [
            "content_preservation",
            "target_similarity",
            "prosody_preservation",
            "naturalness",
            "listening",
            "device_timing",
            "public_benchmark",
            "release",
        ],
        "blocked_gates": [gate["id"] for gate in RELEASE_GATES],
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
    _check_evidence_classes()
    _check_scope_integrity()
    board_digest = _check_board(ws)

    board = strict_json_load(ws / BOARD_PATH)
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
        "no_missing_result_qualifies_candidate": True,
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
            "voice_conversion_benchmark_present": False,
            "streaming_vc_execution_present_here": False,
            "independent_listening_present": False,
            "identity_gold_present": False,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "format": dict(FORMAT),
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
        "source_leads": [dict(lead) for lead in SOURCE_LEADS],
        "method_families": [dict(family) for family in METHOD_FAMILIES],
        "component_census": [dict(row) for row in COMPONENT_CENSUS],
        "excluded_boundaries": [dict(row) for row in EXCLUDED_BOUNDARIES],
        "comparison_inputs": [dict(row) for row in COMPARISON_INPUTS],
        "controls": [dict(row) for row in CONTROLS],
        "assets": [dict(row) for row in ASSETS],
        "historical_executions": [dict(row) for row in HISTORICAL_EXECUTIONS],
        "reported_outcomes": [dict(row) for row in REPORTED_OUTCOMES],
        "local_vs_reported_outcomes": local_vs_reported_outcomes(),
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
        "release_boundary": release_boundary(),
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
    if report["qualification"]["qualification_status"] != QUALIFICATION_STATUS:
        raise MapError("qualification_status changed")
    if report["qualification"]["readiness"] != READINESS:
        raise MapError("readiness changed")
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count is not eight")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in report["boundary"].values()):
        raise MapError("boundary is not closed")
    if report["scope"]["no_new_execution"] is not True:
        raise MapError("survey claims a new execution")
    if report["scope"]["voice_conversion_quality_claim"] is not False:
        raise MapError("voice conversion quality is claimed")
    if report["release_boundary"]["release_allowed"] is not False:
        raise MapError("release is allowed")
    if report["release_boundary"]["release_claim"] is not False:
        raise MapError("release is claimed")
    if report["local_vs_reported_outcomes"]["cross_comparison"]["performed"] is not False:
        raise MapError("cross comparison is claimed")
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
