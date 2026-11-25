# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-TRN-05.

This module builds a bounded taxonomy/comparison evidence map for the
reference-conditioned voice cloning / text-to-speech category (inventory
category ``TRN-05``, legacy family ``F14``). It reads only pinned, read-only
documents from the enclosing ``audioml`` workspace and the SDK worktree. It does
not load audio, media, weights, runtimes or the network, and it does not
register, expose, enable or qualify any synthesizer, voice-cloning model or
processor.

All curated records below are documentation mappings, not new measurements.
Adjacent historical local values and source-reported candidate claims are
transcribed from the pinned documents and labelled with their original scope.
Cloning via speech-to-speech conversion (TRN-04), accent conversion (TRN-03),
pitch/prosody control (TRN-02), time-scale modification (TRN-01), ASR (REC-01),
speaker identification (SPK-05), enhancement (CLN-01) and quality assessment
(OBS-01) are mapped only as boundaries: none of them is reference-conditioned
TTS.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-TRN-05"
TITLE = "Review coverage for Reference-conditioned voice cloning / TTS"
CATEGORY_ID = "TRN-05"
LEGACY_FAMILY = "F14"
BRANCH = "swarm/SDK-SURVEY-TRN-05"
CLAIM_BASE_COMMIT = "39b8885da4fc3ef8e27becf5df5f0658da3baf65"
BASE_COMMIT = "62923ffa7dd992da3cea0f6683fab320fb37e6c0"
PROFILE = "Voice"
COMPONENT = "reference-conditioned-voice-cloning-tts-evidence-map"
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
# verifies media, weights, transcripts, voices or consent that are not present
# in this task directory.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-conversion-eval-20261101/README.md": "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/agent-chatterbox-breadth/REPORT.md": "0ff66ba53399c495106c21c43072ff17292c9ac0be00a04fde06c312bcd73ce8",
    "research/voice-conversion-eval-20261101/results/chatterbox-nano/asr.json": "cf47cb1fdc672f96fcfb153edbcd4706c3f6273cd40b40c641d3d76e813bafbe",
    "research/voice-conversion-eval-20261101/results/chatterbox-nano/metrics.json": "9fa032896246041794b3c37533206ef0b51ab226e97ccfbab7db33348ff17fce",
    "research/voice-conversion-eval-20261101/results/cosyvoice2/asr.json": "71ce950cabfc2a5273dd969a48e5a1ba6df743c5b47c39b9efb7a39a0445f228",
    "research/voice-conversion-eval-20261101/results/cosyvoice2/metrics.json": "b2465f3cbb2f52ce2e538e7d52f24f26861a22e8ce7defbf17953d9f9a3cf1ee",
    "research/voice-conversion-eval-20261101/results/kokoro/metrics.json": "e96da8bd48e9e22063f8329fe16b5328916b9fd0024f50ae5a7fd7da59335850",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

# SDK-worktree-relative boundary pins. They are read only to prove that no
# public surface was touched and to ground the cited merged sibling surveys.
# Sibling READMEs are pinned as templates, not as results for this category.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/survey-rec-01/README.md": "01e54b306313f13f97e1c9f4a08f5ebd98cbf570617644a028ae2bca3d4f4acb",
    "docs/task-evidence/survey-spk-02/README.md": "071471d58c7bc1beffc881ff973702ace56e73febd88ccc965667a03d04d0c20",
    "docs/task-evidence/survey-trn-02/README.md": "be7c95ea532777b8fa45ad092d1d2651390e66bbed8574b01b2c061dc1de56e4",
    "docs/task-evidence/survey-trn-03/README.md": "9f1310a624f14d5238dfee2566cbd0dcf1e7f1c17a94ef445644ae90a7309f50",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Playback and voice transformations",
    "name": "Reference-conditioned voice cloning / TTS",
    "scope": "requested_optional_adjacent",
    "output_kind": "waveform",
    "purpose": "Generate speech in a reference voice when cloning means text-to-speech.",
    "method_families": {
        "classic": "Reference/adapted synthesis family search remains open",
        "ml": "Reference-conditioned flow/codec/generative synthesis",
    },
    "input_output": "Text + speaker reference, sometimes reference text \u2192 synthesized audio",
    "live_or_comparison_boundary": (
        "Cloning via conversion belongs to TRN-04. TTS is an optional branch, not "
        "a required ASR\u2192TTS replacement for a call."
    ),
    "source_ids": ["S40"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "TRN",
    "meaning": "Playback and voice transformations",
    "category_id": CATEGORY_ID,
    "synthesized_waveform_only": True,
    "cloning_via_conversion_is_not_tts": True,
    "tts_is_optional_not_required_call_replacement": True,
    "text_and_reference_audio_are_both_required_inputs": True,
    "reference_text_is_an_optional_conditioning_facet": True,
    "content_identity_and_naturalness_are_separate_outcomes": True,
    "consent_and_reference_availability_are_independent_gates": True,
    "streaming_label_is_not_low_conversational_delay": True,
    "not_voice_conversion": "TRN-04",
    "not_accent_conversion": "TRN-03",
    "not_pitch_or_prosody_only": "TRN-02",
    "not_time_scale_modification": "TRN-01",
    "not_asr_or_transcription": "REC-01",
    "not_speaker_identification_or_verification": "SPK-05",
    "not_quality_assessment": "OBS-01",
    "not_speech_enhancement": "CLN-01",
    "note": (
        "TRN-04 changes the timbre of supplied speech and is a different task; "
        "TRN-03 changes pronunciation; TRN-02 and TRN-01 modify an existing "
        "waveform; REC-01 produces text. This row generates a new waveform from "
        "text plus a reference voice and is optional for the call pipeline. No "
        "conversion, recognition or quality row is pooled into a TRN-05 cloning "
        "or naturalness claim."
    ),
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S40",
        "title": "F5-TTS official implementation",
        "url": "https://github.com/SWivid/F5-TTS",
        "access_scope": "direct",
        "mapped_components": ["f5-tts"],
        "gap_ids": ["G01", "G02"],
        "finding": (
            "Direct implementation lead for reference-conditioned flow-matching "
            "TTS that conditions synthesis on a reference voice and optional "
            "reference text. The census records the row as considered only: no "
            "checkpoint, exact revision, per-weight terms, consented reference "
            "voice or local synthesis result is staged here."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Reference/adapted synthesis family search (open)",
        "components": [],
        "gap_ids": ["G03"],
        "status": "no_local_component_or_execution_in_reviewed_records",
        "boundary": (
            "The catalogued classic string explicitly leaves the reference/"
            "adapted synthesis family search open. No classical pitch-synchronous "
            "or source-filter reference-adapted synthesizer, selected target "
            "voice, cohort or execution is catalogued, so the open search is "
            "recorded instead of being filled with a vocoder or a conversion row."
        ),
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Reference-conditioned flow-matching synthesis (F5-TTS, S40)",
        "components": ["f5-tts"],
        "gap_ids": ["G01", "G02"],
        "status": "candidate_only_considered_no_weights_or_execution",
        "boundary": (
            "F5-TTS is the only named source lead and its inventory row is "
            "considered. No checkpoint, exact revision, runtime, reference voice "
            "or synthesized-sample score is staged; the official repository is "
            "not a run on this host."
        ),
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Zero-shot codec/LLM and flow TTS conditioned on prompt audio (CosyVoice 2, Seed-TTS)",
        "components": ["cosyvoice-2-0-5b", "cosyvoice-family", "seed-tts"],
        "gap_ids": ["G04", "G05", "G12"],
        "status": "adjacent_local_generation_only_no_reference_similarity",
        "boundary": (
            "CosyVoice 2 ran one adjacent research prompt/text pair and emitted "
            "four streaming chunks; no reference-voice similarity, naturalness or "
            "device timing was scored. Seed-TTS and the CosyVoice family remain "
            "blocked. Adjacent generation is not a TRN-05 quality result."
        ),
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Autoregressive or whole-utterance neural TTS conditioned on a voice prompt (Chatterbox Nano, StyleTTS 2, YourTTS)",
        "components": ["chatterbox-nano", "styletts-2", "yourtts"],
        "gap_ids": ["G01", "G04", "G07"],
        "status": "adjacent_local_whole_utterance_generation_only",
        "boundary": (
            "Chatterbox Nano produced one whole-utterance reference-conditioned "
            "output with no streaming chunks, no similarity or naturalness score "
            "and one text. StyleTTS 2 and YourTTS are blocked candidates with no "
            "staged checkpoint or local run."
        ),
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "End-to-end VITS/adversarial and streaming VITS synthesis families",
        "components": ["vits2", "vits-streaming-adaptation"],
        "gap_ids": ["G07", "G12"],
        "status": "candidate_only_or_blocked_no_local_execution",
        "boundary": (
            "VITS2 is blocked with no canonical checkpoint; VITS streaming "
            "adaptation is considered but no official sub-100 ms streaming "
            "checkpoint was identified. A streaming label is not a measured "
            "first-audio or conversational delay."
        ),
    },
    {
        "family_id": "MF-M5",
        "branch": "ml",
        "family": "Streaming cloned-voice TTS with gated GGUF checkpoints (NeuTTS Nano/Air)",
        "components": ["neutts-nano-q4", "neutts-air-gated-checkpoint-lead"],
        "gap_ids": ["G05", "G12"],
        "status": "blocked_gated_checkpoint_no_inference",
        "boundary": (
            "The NeuTTS Nano/Air download returned HTTP 401 behind gated "
            "Hugging Face terms; no public authenticated route was used and no "
            "inference result exists. No substitute checkpoint or mirror is "
            "accepted."
        ),
    },
    {
        "family_id": "MF-M6",
        "branch": "ml",
        "family": "Adjacent fixed-voice TTS control and neural vocoder / analysis-resynthesis components",
        "components": [
            "kokoro-82m",
            "hifi-gan-vocoder",
            "vocos-vocoder",
            "world-vocoder",
            "nansy-analysis-resynthesis",
            "fastspeech-2-vits-duration-predictors",
        ],
        "gap_ids": ["G09"],
        "status": "adjacent_control_or_component_only_not_reference_cloning",
        "boundary": (
            "Kokoro 82M is a fixed-preset TTS control, explicitly not a zero-shot "
            "cloning model. HiFi-GAN, Vocos and WORLD are vocoder components; "
            "NANSY is analysis/resynthesis; FastSpeech 2 / VITS duration "
            "predictors require text/encoder representations. None is a "
            "reference-conditioned synthesizer."
        ),
    },
]

# component_id, task and evidence_status are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "f5-tts", "role": "named_reference_conditioned_flow_tts_lead", "evidence_status": "considered", "task": "SDK-F5-TTS"},
    {"component_id": "cosyvoice-2-0-5b", "role": "adjacent_zero_shot_streaming_tts_run", "evidence_status": "partial", "task": "SDK-COSYVOICE-2-0-5B"},
    {"component_id": "cosyvoice-family", "role": "adjacent_cosyvoice_family_control", "evidence_status": "blocked", "task": "SDK-COSYVOICE-FAMILY"},
    {"component_id": "seed-tts", "role": "blocked_zero_shot_tts_candidate", "evidence_status": "blocked", "task": "SDK-SEED-TTS"},
    {"component_id": "chatterbox-nano", "role": "adjacent_reference_conditioned_whole_utterance_tts_run", "evidence_status": "partial", "task": "SDK-CHATTERBOX-NANO"},
    {"component_id": "styletts-2", "role": "blocked_expressive_tts_candidate", "evidence_status": "blocked", "task": "SDK-STYLETTS-2"},
    {"component_id": "yourtts", "role": "blocked_multispeaker_tts_candidate", "evidence_status": "blocked", "task": "SDK-YOURTTS"},
    {"component_id": "vits2", "role": "blocked_end_to_end_tts_candidate", "evidence_status": "blocked", "task": "SDK-VITS2"},
    {"component_id": "vits-streaming-adaptation", "role": "considered_streaming_synthesis_lead", "evidence_status": "considered", "task": "SDK-VITS-STREAMING-ADAPTATION"},
    {"component_id": "neutts-nano-q4", "role": "gated_streaming_cloned_voice_tts_candidate", "evidence_status": "partial", "task": "SDK-NEUTTS-NANO-Q4"},
    {"component_id": "neutts-air-gated-checkpoint-lead", "role": "gated_checkpoint_lead_blocked", "evidence_status": "blocked", "task": "SDK-NEUTTS-AIR-GATED-CHECKPOINT-LEAD"},
    {"component_id": "kokoro-82m", "role": "fixed_voice_tts_control", "evidence_status": "partial", "task": "SDK-KOKORO-82M"},
    {"component_id": "hifi-gan-vocoder", "role": "neural_vocoder_component", "evidence_status": "considered", "task": "SDK-HIFI-GAN-VOCODER"},
    {"component_id": "vocos-vocoder", "role": "neural_vocoder_component", "evidence_status": "considered", "task": "SDK-VOCOS-VOCODER"},
    {"component_id": "world-vocoder", "role": "classical_vocoder_component", "evidence_status": "considered", "task": "SDK-WORLD-VOCODER"},
    {"component_id": "nansy-analysis-resynthesis", "role": "analysis_resynthesis_component", "evidence_status": "considered", "task": "SDK-NANSY-ANALYSIS-RESYNTHESIS"},
    {"component_id": "fastspeech-2-vits-duration-predictors", "role": "text_duration_predictor_component", "evidence_status": "considered", "task": "SDK-FASTSPEECH-2-VITS-DURATION-PREDICTORS"},
]

EXCLUDED_BOUNDARIES: List[Dict[str, str]] = [
    {
        "boundary": "Speech-to-speech voice conversion (TRN-04)",
        "reason": "Changing the timbre of supplied speech retains the input content and timing; it is not text-conditioned synthesis in a reference voice.",
    },
    {
        "boundary": "Accent conversion (TRN-03)",
        "reason": "A pronunciation change on an existing utterance is not a generated waveform from text plus a reference voice.",
    },
    {
        "boundary": "Pitch and limited prosody control (TRN-02) and time-scale modification (TRN-01)",
        "reason": "Pitch, duration and rate controls modify a supplied waveform; they do not generate speech from text.",
    },
    {
        "boundary": "Speech recognition / transcription (REC-01)",
        "reason": "A transcript is text, not a synthesized waveform, and ASR\u2192TTS is an optional composition rather than a required call replacement.",
    },
    {
        "boundary": "Speaker representation, identification and verification (SPK-05)",
        "reason": "An identity score or embedding is not a generated utterance; similarity scoring must stay separate from synthesis quality.",
    },
    {
        "boundary": "Background noise suppression (CLN-01) and quality assessment (OBS-01)",
        "reason": "A denoised signal or a perceptual score is not reference-conditioned TTS.",
    },
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "F5-TTS official reference-conditioned flow-matching implementation (S40)",
        "class": "source_only_reference_tts_protocol",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Direct implementation lead only: text plus reference audio (optionally reference text) conditions a flow-matching synthesizer; no checkpoint, revision, runtime or local sample is staged.",
    },
    {
        "id": "CI-2",
        "input": "F5-TTS considered inventory candidate row",
        "class": "source_reported_reference_tts_candidate",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Considered row with no local checkpoint, reference voice, cohort or execution; the plan note asks for consented conditioning, verified weights and first-audio/full-response measurement, none of which exists.",
    },
    {
        "id": "CI-3",
        "input": "Adjacent CosyVoice 2 0.5B zero-shot streaming TTS on one fixed prompt/text pair",
        "class": "historical_research_zero_shot_streaming_tts",
        "source_pin": "research/voice-conversion-eval-20261101/results/cosyvoice2/metrics.json",
        "boundary": "One prompt/text pair, CPU only: 10.0 s audio in four chunks, first chunk 23.81 s from call start, total 80.66 s, file RTF 8.07, WER 0%, no clipping. No reference-voice similarity, naturalness, multi-speaker cohort or device timing.",
    },
    {
        "id": "CI-4",
        "input": "Adjacent Chatterbox Nano official reference-conditioned whole-utterance TTS",
        "class": "historical_research_reference_conditioned_whole_utterance_tts",
        "source_pin": "research/voice-conversion-eval-20261101/results/chatterbox-nano/metrics.json",
        "boundary": "One whole-utterance generation on CPU: 8.92 s audio, 11.10 s model init, 11.47 s generation, file RTF 1.286, WER 0%, no clipping; no streaming chunks, reference-similarity score, naturalness rating or device timing.",
    },
    {
        "id": "CI-5",
        "input": "Adjacent Kokoro 82M fixed-preset TTS control",
        "class": "historical_research_fixed_voice_tts_control",
        "source_pin": "research/voice-conversion-eval-20261101/results/kokoro/metrics.json",
        "boundary": "A fixed `af_heart` preset with no reference voice; 9.025 s audio after 57.297 s, RTF 0.158. It is a control, never a cloning candidate or a reference-similarity result.",
    },
    {
        "id": "CI-6",
        "input": "NeuTTS Nano Q4 / Air gated GGUF checkpoint acquisition",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": "HTTP 401 behind gated Hugging Face terms with no authenticated access; no inference result is claimed and no alternate route or substitute checkpoint was used.",
    },
    {
        "id": "CI-7",
        "input": "Seed-TTS, StyleTTS 2, YourTTS and VITS2 blocked candidate rows",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "No accessible licensed checkpoint, canonical checkpoint or local adapter is available for any of the four rows; none is replaced by a different model or mirror.",
    },
    {
        "id": "CI-8",
        "input": "Adjacent HiFi-GAN, Vocos, WORLD, NANSY and FastSpeech 2 / VITS duration components",
        "class": "adjacent_vocoder_component_boundary",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Vocoders and duration predictors are components inside a synthesis pipeline; they do not independently generate reference-conditioned speech or measure cloning.",
    },
    {
        "id": "CI-9",
        "input": "Missing rights-cleared consented reference-voice TTS corpus with manual transcripts, speaker/language groups and output-use terms",
        "class": "missing_required_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Absence is recorded as missing, not as an empty cohort; no reference-similarity, naturalness, consent or output-use claim follows.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "fixed-preset TTS control",
        "role": "Kokoro 82M uses one `af_heart` preset with no reference voice; it shows what text-only fixed-voice synthesis costs and is not a cloning candidate.",
        "source_pin": "research/voice-conversion-eval-20261101/results/kokoro/metrics.json",
    },
    {
        "id": "CT-2",
        "name": "reference clip as identity ceiling",
        "role": "The unmodified reference clip is the identity ceiling; any synthesized-output similarity must be reported against it, not as an absolute quality score.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-3",
        "name": "wrong/mismatched reference control",
        "role": "A mismatched reference voice is required to expose whether output follows the reference or collapses to a generic voice; it was not run.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-4",
        "name": "content-preservation ASR control",
        "role": "Whisper Tiny English WER 0.00% on the fixed 27-word text is a one-utterance proxy for content, not comprehension, naturalness or pronunciation gold.",
        "source_pin": "research/voice-conversion-eval-20261101/results/chatterbox-nano/asr.json",
    },
    {
        "id": "CT-5",
        "name": "ignore-reference / degenerate voice control",
        "role": "A synthesizer that ignores the reference and emits a fixed voice must be distinguishable from a reference-conditioned one; no such ablation exists.",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
    {
        "id": "CT-6",
        "name": "sample-count, finite-output and clipping control",
        "role": "Historical outputs are finite, non-clipping 24 kHz waveforms with recorded durations; sample-count preservation and nonfinite handling are not exercised by this survey.",
        "source_pin": "research/voice-conversion-eval-20261101/results/cosyvoice2/metrics.json",
    },
    {
        "id": "CT-7",
        "name": "single vs multi-utterance and single vs multi-speaker stratification",
        "role": "Every historical run is one text and one reference; no multi-utterance, multi-speaker or language-group stratification exists.",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "id": "CT-8",
        "name": "optional TTS branch versus required ASR\u2192TTS replacement",
        "role": "TTS is an optional branch; it must not be presented as a required replacement for the call's speech path.",
        "source_pin": "audio_categories.md",
    },
    {
        "id": "CT-9",
        "name": "streaming chunks versus whole-utterance return",
        "role": "CosyVoice 2 exposes four chunks; Chatterbox Nano returns a whole utterance with no chunks. Chunked return is not the same as measured first-audio latency.",
        "source_pin": "research/voice-conversion-eval-20261101/results/cosyvoice2/metrics.json",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "F5-TTS official implementation and weight metadata",
        "class": "external_weights_metadata_only",
        "status": "Source lead only; no checkpoint, exact revision or per-weight terms are staged in this task",
        "source_pin": "research/category_registry.json",
    },
    {
        "asset": "CosyVoice 2 0.5B public weights",
        "class": "external_weights_metadata_only",
        "status": "Used in the historical research run and removed afterwards; output and metrics are retained, weights are not staged here",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "Chatterbox Nano public checkpoints (about 1.8 GB)",
        "class": "external_weights_metadata_only",
        "status": "Retained in the research workspace after the historical run; not staged, loaded or played in this task",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "Kokoro 82M fixed-preset weights",
        "class": "external_weights_metadata_only",
        "status": "Removed after the historical control run; output and metrics are retained, weights are not staged here",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "NeuTTS Nano Q4 / Air gated GGUF checkpoints",
        "class": "missing_restricted",
        "status": "Gated Hugging Face terms returned HTTP 401; no authenticated access and no inference result",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "LJ Speech 1.1 LJ001-0001 source clip",
        "class": "research_audio_public_domain",
        "status": "16 kHz / 9.655 s, SHA-256 adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b; dataset page describes public-domain recordings, local use only",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "RT-VC demo target reference target_rtvc_p360.flac",
        "class": "research_audio_provenance_unconfirmed",
        "status": "16 kHz / 3.562 s, SHA-256 fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44; dataset/licence provenance is not confirmed, so local research comparison only",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "Whisper Tiny English local scorer",
        "class": "external_model_metadata_only",
        "status": "Cached research ASR model used for WER proxies; one small English model, not a human transcript or comprehension check",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
    },
    {
        "asset": "Rights-cleared consented reference-voice corpus with manual transcripts and output-use terms",
        "class": "missing_asset",
        "status": "Not present; absence is explicit and is not an empty cohort",
        "source_pin": "audio_categories.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "CosyVoice 2 0.5B zero-shot streaming TTS on one prompt/text pair",
        "outcome_class": "historical_research_zero_shot_streaming_tts",
        "component_ids": ["cosyvoice-2-0-5b"],
        "source_pin": "research/voice-conversion-eval-20261101/results/cosyvoice2/metrics.json",
        "wer_source_pin": "research/voice-conversion-eval-20261101/results/cosyvoice2/asr.json",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "adjacent_zero_shot_streaming_generation_smoke",
        "values": {
            "text_prompts": 1,
            "reference_audio_seconds": 9.655,
            "reference_text_supplied": True,
            "sample_rate_hz": 24000,
            "audio_seconds": 10.0,
            "chunk_count": 4,
            "first_chunk_seconds_from_inference_call": 23.810076208028477,
            "model_init_seconds": 22.42115745897172,
            "generation_wall_seconds": 80.66152424999746,
            "file_rtf": 8.066152424999746,
            "peak_abs": 0.9900000095367432,
            "clipped_sample_fraction": 0.0,
            "wer": 0.0,
            "reference_similarity_measured": False,
            "naturalness_measured": False,
            "multi_speaker_cohort": False,
            "device_timing_measured": False,
            "first_audio_latency_claim": False,
        },
        "scope": (
            "One fixed LJ Speech prompt as both reference audio and reference "
            "text, CPU only, on the historical research host. It emits four "
            "chunks but the first-chunk time includes prompt loading and "
            "encoding; no reference-voice similarity, naturalness, multi-speaker "
            "cohort or device timing exists. It is adjacent generation, not a "
            "TRN-05 cloning result. not rerun by this survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "Chatterbox Nano official reference-conditioned whole-utterance TTS",
        "outcome_class": "historical_research_reference_conditioned_whole_utterance_tts",
        "component_ids": ["chatterbox-nano"],
        "source_pin": "research/voice-conversion-eval-20261101/results/chatterbox-nano/metrics.json",
        "wer_source_pin": "research/voice-conversion-eval-20261101/results/chatterbox-nano/asr.json",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "adjacent_reference_conditioned_whole_utterance_smoke",
        "values": {
            "text_prompts": 1,
            "reference_audio_seconds": 9.655,
            "reference_text_supplied": True,
            "sample_rate_hz": 24000,
            "audio_seconds": 8.92,
            "model_init_seconds": 11.101397958002053,
            "generation_wall_seconds": 11.46746112499386,
            "file_rtf": 1.2855898122190428,
            "peak_abs": 0.34220677614212036,
            "clipped_sample_fraction": 0.0,
            "wer": 0.0,
            "streaming_chunks_exposed": False,
            "first_audio_latency_seconds": None,
            "reference_similarity_measured": False,
            "naturalness_measured": False,
            "multi_speaker_cohort": False,
            "device_timing_measured": False,
            "first_audio_latency_claim": False,
        },
        "scope": (
            "One whole-utterance generation with the shared LJ Speech clip as a "
            "voice prompt on CPU. The official API exposes no streaming chunks, "
            "so call-to-return time is not first-audio latency; no "
            "reference-similarity, naturalness, multi-speaker or device measure "
            "exists. It is adjacent reference-conditioned generation, not a "
            "qualified cloning result. not rerun by this survey."
        ),
    },
    {
        "id": "HE-3",
        "label": "Kokoro 82M fixed-preset TTS control",
        "outcome_class": "historical_research_fixed_voice_tts_control",
        "component_ids": ["kokoro-82m"],
        "source_pin": "research/voice-conversion-eval-20261101/results/kokoro/metrics.json",
        "scope_class": "historical_research_execution",
        "merged_task_evidence": False,
        "not_rerun": True,
        "evidence_role": "fixed_voice_text_only_control",
        "values": {
            "text_prompts": 1,
            "reference_audio_seconds": 0.0,
            "preset_voice": "af_heart",
            "sample_rate_hz": 24000,
            "audio_seconds": 9.025,
            "chunk_count": 1,
            "first_chunk_after_start_seconds": 57.297223249974195,
            "first_chunk_after_pipeline_init_seconds": 3.841400207951665,
            "total_wall_seconds": 57.29795258399099,
            "rtf_audio_seconds_per_wall_second": 0.1575099910729023,
            "reference_voice_cloning": False,
            "reference_similarity_measured": False,
            "naturalness_measured": False,
            "device_timing_measured": False,
        },
        "scope": (
            "A fixed `af_heart` preset with no reference voice, on CPU. The "
            "pinned ledger explicitly says it is not a zero-shot voice cloning "
            "model, so it is a text-only control and never a TRN-05 candidate or "
            "similarity result. not rerun by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "F5-TTS is an official reference-conditioned flow-matching TTS implementation",
        "class": "source_reported_reference_tts_candidate",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Implementation lead only; no checkpoint, revision, runtime, consented reference voice or local sample is staged.",
    },
    {
        "id": "RO-2",
        "claim": "CosyVoice 2 0.5B official zero-shot streaming TTS is partially evaluated on one prompt/text pair",
        "class": "source_reported_candidate_documentation",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Ten seconds in four chunks, first chunk 23.81 s, total 80.66 s, RTF 8.07, WER 0%, no clipping; TTS is not source-speech transformation and the run is single-prompt CPU only.",
    },
    {
        "id": "RO-3",
        "claim": "NeuTTS Nano/Air GGUF checkpoints are gated and returned HTTP 401",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/voice-conversion-eval-20261101/README.md",
        "boundary": "No authenticated access, no alternate route and no inference result; no substitute checkpoint is accepted.",
    },
    {
        "id": "RO-4",
        "claim": "Seed-TTS has no accessible licensed checkpoint and verified input-conversion runtime",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Blocked candidate row only; no local model, revision or result.",
    },
    {
        "id": "RO-5",
        "claim": "StyleTTS 2 has no local model/checkpoint adapter and is an expressive TTS task",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Blocked candidate row only; expressive TTS is not a streaming call-path or cloning result.",
    },
    {
        "id": "RO-6",
        "claim": "YourTTS and VITS2 have no local checkpoint or conversion runtime",
        "class": "source_reported_blocked_candidate",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Blocked candidate rows only; VITS2's cited implementation is unofficial work in progress and YourTTS has no staged adapter.",
    },
    {
        "id": "RO-7",
        "claim": "HiFi-GAN and Vocos are vocoder components that do not independently transform voice",
        "class": "source_reported_candidate_documentation",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Out-of-scope component rows; a vocoder needs acoustic features and is not a reference-conditioned synthesizer.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "permitted_input_and_target_references": "One public-domain LJ Speech prompt and one demo reference with unconfirmed provenance exist historically; no rights-cleared reference voice or consent record is staged.",
        "task_and_language_speaker_groups": "Every historical run is one English text and one reference; no language group, speaker group, multi-speaker cohort or held-out voice exists.",
        "preserve_text_and_semantic_content": "Whisper Tiny English WER 0.00% is a one-utterance proxy; no manual transcript, comprehension check or semantic-content gold exists.",
        "identity_and_similarity": "No reference-voice similarity metric was computed for any historical TTS output; in-model voice-conversion cosines are a different task and are not inherited.",
        "naturalness": "No blinded listening, naturalness rating or reference-voice preference panel was run.",
        "alignment": "Only whole-output duration and sample rate are recorded; there is no word/phoneme alignment, onset alignment or reference-content alignment.",
        "first_output_and_tail_timing": "CosyVoice 2 first chunk 23.81 s; Chatterbox Nano exposes no chunks and reports 11.47 s call-to-return; Kokoro 57.297 s. None is first-audio latency on a call device.",
        "exact_target_condition": "The target is one fixed reference clip; no declared target-voice specification, reference-text policy or multi-reference conditioning exists.",
        "consent_reference_availability_output_use": "LJ Speech is described as public domain but the demo reference provenance is unconfirmed; voice consent, reference availability and output-use terms are independent gates and remain uncleared.",
    },
    "blocked": [
        "Rights-cleared consented reference-voice corpus with manual transcripts, speaker/language groups and explicit output-use terms",
        "Frozen development/held-out text and reference-voice partitions with independent blinded naturalness and identity listening",
        "Matched fixed-voice, mismatched-reference, ignore-reference and content-preservation ASR controls with uncertainty",
        "Pinned checkpoints, exact revisions, runtimes and per-weight/per-voice terms for F5-TTS, CosyVoice 2, Chatterbox Nano and any streaming path",
        "Causal streaming chunk/lookahead, first-audio/tail, sample-count and nonfinite behavior on the target device",
        "Explicit consent, reference-availability and output-use policy independent of model quality",
        "Explicit public default or opt-in provider intake approval",
        "Release approval; DEFER remains in force until every gate is closed",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "historical_research_zero_shot_streaming_tts": True,
    "historical_research_reference_conditioned_whole_utterance_tts": True,
    "historical_research_fixed_voice_tts_control": True,
    "source_only_reference_tts_protocol": True,
    "source_reported_reference_tts_candidate": True,
    "source_reported_blocked_candidate": True,
    "source_reported_candidate_documentation": True,
    "adjacent_vocoder_component_boundary": True,
    "reference_cloning_execution": False,
    "reference_similarity_measured": False,
    "naturalness_measured": False,
    "human_listening_result": False,
    "content_preservation_gold": False,
    "multi_utterance_or_multi_speaker_cohort": False,
    "rights_qualified_reference_voice_corpus": False,
    "streaming_first_audio_claim": False,
    "device_timing": False,
    "cpu_accelerator_parity": False,
    "tts_quality_claim": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "provider_enablement": False,
    "release_approval": False,
}

CLASS_BACKING: Dict[str, List[str]] = {
    "historical_research_zero_shot_streaming_tts": [
        "historical_research_zero_shot_streaming_tts"
    ],
    "historical_research_reference_conditioned_whole_utterance_tts": [
        "historical_research_reference_conditioned_whole_utterance_tts"
    ],
    "historical_research_fixed_voice_tts_control": [
        "historical_research_fixed_voice_tts_control"
    ],
    "source_only_reference_tts_protocol": ["source_only_reference_tts_protocol"],
    "source_reported_reference_tts_candidate": [
        "source_reported_reference_tts_candidate"
    ],
    "source_reported_blocked_candidate": ["source_reported_blocked_candidate"],
    "source_reported_candidate_documentation": [
        "source_reported_candidate_documentation"
    ],
    "adjacent_vocoder_component_boundary": [
        "adjacent_vocoder_component_boundary"
    ],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Select and pin one concrete reference-conditioned TTS with an exact checkpoint, reference-conditioning protocol and runtime",
        "evidence_gap": "F5-TTS is considered only; CosyVoice 2 and Chatterbox Nano are partial adjacent runs; no row has a frozen reference-conditioning protocol, exact revision and staged runtime.",
        "follow_up_ids": ["SDK-F5-TTS", "SDK-COSYVOICE-2-0-5B", "SDK-CHATTERBOX-NANO"],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility and implementation rows are scoping leads; none is enabled, staged or qualified by this map.",
    },
    {
        "id": "G02",
        "actionable_gap": "Resolve F5-TTS checkpoint availability, exact revision and per-weight terms",
        "evidence_gap": "The F5-TTS row is considered and its official implementation is a source lead, but no checkpoint digest, revision, runtime or licence record is staged in this task.",
        "follow_up_ids": ["SDK-F5-TTS", "SDK-FND-AUDIT"],
        "feasibility_task_exists": True,
        "owner_note": "The linked F5-TTS and audit rows own provenance; a future substitute would be a distinct candidate with its own identity and terms.",
    },
    {
        "id": "G03",
        "actionable_gap": "Acquire a rights-cleared consented reference-voice corpus with manual transcripts, speaker/language groups and output-use terms",
        "evidence_gap": "Only one public-domain source clip and one demo reference with unconfirmed provenance exist; no consent record, transcript set or multi-voice cohort is staged.",
        "follow_up_ids": [
            "SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS",
            "SDK-VOICEBANK-DEMAND-VOICES-AND-DNS5-EVIDENCE",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated TRN-05 reference-voice corpus owner exists; the linked manifest and audit rows own evaluation manifests and asset boundaries, not a consented TTS cohort.",
    },
    {
        "id": "G04",
        "actionable_gap": "Measure reference-voice similarity and naturalness independently of content preservation",
        "evidence_gap": "No reference-similarity or naturalness score exists for any TTS output; in-model voice-conversion cosines are a different task and are not inherited.",
        "follow_up_ids": ["SDK-SURVEY-SPK-05", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated TRN-05 similarity or naturalness owner exists; the linked identity taxonomy and evidence foundation rows own scoring scope, not a TTS result.",
    },
    {
        "id": "G05",
        "actionable_gap": "Close the gated NeuTTS checkpoint path without substituting a mirror or a different model",
        "evidence_gap": "The NeuTTS Nano/Air download returned HTTP 401 behind gated terms; no inference, checkpoint digest or approved access exists.",
        "follow_up_ids": ["SDK-NEUTTS-NANO-Q4", "SDK-NEUTTS-AIR-GATED-CHECKPOINT-LEAD", "SDK-FND-AUDIT"],
        "feasibility_task_exists": True,
        "owner_note": "The linked NeuTTS and audit rows own gated access and asset clearance; no substitute is used here.",
    },
    {
        "id": "G06",
        "actionable_gap": "Run independent blinded listening for naturalness, reference similarity and content on frozen cohorts",
        "evidence_gap": "No listening panel, naturalness rating or reference-voice preference test exists; the WER proxy is not a listening result.",
        "follow_up_ids": ["SDK-FND-EVIDENCE", "SDK-PIPE-VOICE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated TRN-05 listening owner exists; the evidence and pipeline rows own protocol and acceptance, and no listening result is inherited from an adjacent survey.",
    },
    {
        "id": "G07",
        "actionable_gap": "Resolve blocked Seed-TTS, StyleTTS 2, YourTTS and VITS2 candidate availability before any comparison",
        "evidence_gap": "All four rows are blocked with no accessible or canonical checkpoint, local adapter or runtime.",
        "follow_up_ids": ["SDK-SEED-TTS", "SDK-STYLETTS-2", "SDK-YOURTTS", "SDK-VITS2"],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility rows are scoping leads; none is replaced by a different model or mirror.",
    },
    {
        "id": "G08",
        "actionable_gap": "Measure first-audio/tail, chunking, sample-count and nonfinite behavior on the target device",
        "evidence_gap": "CosyVoice 2 reports first chunk 23.81 s, Chatterbox Nano exposes no chunks, and Kokoro reports 57.297 s; none is a call-device or sample-count measurement.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-COSYVOICE-2-0-5B", "SDK-CHATTERBOX-NANO"],
        "feasibility_task_exists": False,
        "owner_note": "The linked timing foundation and synthesis implementation rows own the clock and candidate; none is a dedicated TRN-05 device-timing owner, and no device timing or streaming claim is made here.",
    },
    {
        "id": "G09",
        "actionable_gap": "Keep fixed-voice controls and vocoder/analysis-resynthesis components out of the cloning claim",
        "evidence_gap": "Kokoro 82M is a fixed preset explicitly not a cloning model; HiFi-GAN, Vocos, WORLD, NANSY and FastSpeech 2 duration predictors are components with no reference-conditioned synthesis.",
        "follow_up_ids": [
            "SDK-KOKORO-82M",
            "SDK-HIFI-GAN-VOCODER",
            "SDK-VOCOS-VOCODER",
            "SDK-WORLD-VOCODER",
            "SDK-NANSY-ANALYSIS-RESYNTHESIS",
            "SDK-FASTSPEECH-2-VITS-DURATION-PREDICTORS",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked control and component rows are scoping leads; a vocoder, duration predictor or fixed-preset control is never a cloning result.",
    },
    {
        "id": "G10",
        "actionable_gap": "Keep TTS optional and separate from TRN-04 conversion, TRN-02 prosody and REC-01 ASR",
        "evidence_gap": "The category boundary says cloning via conversion belongs to TRN-04 and TTS is optional; no component owns both generation and a conversion or ASR replacement decision.",
        "follow_up_ids": [
            "SDK-SURVEY-TRN-04",
            "SDK-SURVEY-TRN-02",
            "SDK-SURVEY-REC-01",
            "SDK-PIPE-VOICE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No single component owns both TTS and a conversion/ASR replacement decision; the linked taxonomy and pipeline rows keep the tasks separate and no new task is invented.",
    },
    {
        "id": "G11",
        "actionable_gap": "Make consent, reference availability and output-use policy explicit and independent of model quality",
        "evidence_gap": "The demo reference provenance is unconfirmed and no voice consent or output-use term exists; consent is an independent gate per the Voice acceptance profile.",
        "follow_up_ids": ["SDK-FND-AUDIT", "SDK-PIPE-VOICE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated TRN-05 consent owner exists; the audit and pipeline rows own asset and experiment boundaries, not a voice-specific consent grant.",
    },
    {
        "id": "G12",
        "actionable_gap": "Mark streaming chunks versus whole-utterance return and avoid live-call latency claims",
        "evidence_gap": "CosyVoice 2 emits four chunks, Chatterbox Nano returns a whole utterance and Kokoro one segment; first-chunk times include prompt loading and none is a live-call latency.",
        "follow_up_ids": ["SDK-COSYVOICE-2-0-5B", "SDK-CHATTERBOX-NANO", "SDK-VITS-STREAMING-ADAPTATION", "SDK-FND-TIMING"],
        "feasibility_task_exists": True,
        "owner_note": "The linked synthesis and timing rows own candidate and clock scope; a streaming label or chunked return is not a first-audio latency result.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-F5-TTS", "title": "F5-TTS", "mode": "feasibility"},
    {"task_id": "SDK-COSYVOICE-2-0-5B", "title": "CosyVoice 2 0.5B", "mode": "implementation"},
    {"task_id": "SDK-CHATTERBOX-NANO", "title": "Chatterbox Nano", "mode": "implementation"},
    {"task_id": "SDK-KOKORO-82M", "title": "Kokoro 82M", "mode": "implementation"},
    {"task_id": "SDK-NEUTTS-NANO-Q4", "title": "NeuTTS Nano Q4", "mode": "implementation"},
    {"task_id": "SDK-NEUTTS-AIR-GATED-CHECKPOINT-LEAD", "title": "NeuTTS Air / gated checkpoint lead", "mode": "feasibility"},
    {"task_id": "SDK-SEED-TTS", "title": "Seed-TTS", "mode": "feasibility"},
    {"task_id": "SDK-STYLETTS-2", "title": "StyleTTS 2", "mode": "feasibility"},
    {"task_id": "SDK-YOURTTS", "title": "YourTTS", "mode": "feasibility"},
    {"task_id": "SDK-VITS2", "title": "VITS2", "mode": "feasibility"},
    {"task_id": "SDK-VITS-STREAMING-ADAPTATION", "title": "VITS streaming adaptation", "mode": "feasibility"},
    {"task_id": "SDK-HIFI-GAN-VOCODER", "title": "HiFi-GAN vocoder", "mode": "research-control"},
    {"task_id": "SDK-VOCOS-VOCODER", "title": "Vocos vocoder", "mode": "research-control"},
    {"task_id": "SDK-WORLD-VOCODER", "title": "WORLD vocoder", "mode": "feasibility"},
    {"task_id": "SDK-FASTSPEECH-2-VITS-DURATION-PREDICTORS", "title": "FastSpeech 2 / VITS duration predictors", "mode": "feasibility"},
    {"task_id": "SDK-NANSY-ANALYSIS-RESYNTHESIS", "title": "NANSY analysis/resynthesis", "mode": "feasibility"},
    {"task_id": "SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS", "title": "LJ Speech and consented accent evaluation manifests", "mode": "research-control"},
    {"task_id": "SDK-VOICEBANK-DEMAND-VOICES-AND-DNS5-EVIDENCE", "title": "VoiceBank+DEMAND, VOiCES and DNS5 evidence", "mode": "research-control"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-SURVEY-TRN-04", "title": "Review coverage for Speech-to-speech voice conversion", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-TRN-02", "title": "Review coverage for Pitch and limited prosody control", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-SPK-05", "title": "Review coverage for Speaker representation, identification and verification", "mode": "taxonomy"},
    {"task_id": "SDK-SURVEY-REC-01", "title": "Review coverage for Speech recognition / transcription (ASR/STT)", "mode": "taxonomy"},
    {"task_id": "SDK-PIPE-VOICE", "title": "Consented offline voice and accent experiments", "mode": "pipeline"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {
        "id": "RG-01",
        "blocked": True,
        "requirement": "Rights-cleared consented reference-voice corpus with manual transcripts, speaker/language groups and explicit output-use terms",
    },
    {
        "id": "RG-02",
        "blocked": True,
        "requirement": "Frozen development/held-out text and reference-voice partitions with independent blinded naturalness and identity listening",
    },
    {
        "id": "RG-03",
        "blocked": True,
        "requirement": "Matched fixed-voice, mismatched-reference, ignore-reference and content-preservation ASR controls with uncertainty",
    },
    {
        "id": "RG-04",
        "blocked": True,
        "requirement": "Pinned checkpoints, exact revisions, runtimes and per-weight/per-voice terms for F5-TTS, CosyVoice 2, Chatterbox Nano and any streaming path",
    },
    {
        "id": "RG-05",
        "blocked": True,
        "requirement": "Causal streaming chunk/lookahead, first-audio/tail, sample-count, nonfinite handling and target-device timing",
    },
    {
        "id": "RG-06",
        "blocked": True,
        "requirement": "Explicit consent, reference-availability and output-use policy independent of model quality",
    },
    {
        "id": "RG-07",
        "blocked": True,
        "requirement": "Explicit public default or opt-in provider/external-adapter intake with independent exact-head review",
    },
    {
        "id": "RG-08",
        "blocked": True,
        "requirement": "Release approval; DEFER remains in force until every gate is closed",
    },
]

# Literal anchors used to prove that curated numbers and caveats are grounded in
# the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "TRN-05 \u2014 Reference-conditioned voice cloning / TTS",
        "Cloning via conversion belongs to TRN-04.",
        "TTS is an optional branch, not a required ASR\u2192TTS replacement for a call.",
    ],
    "research/category_survey/sources.md": [
        "| S40 | [F5-TTS official implementation](https://github.com/SWivid/F5-TTS) | transformations | direct |",
    ],
    "research/category_registry.json": [
        '"id": "TRN-05"',
        "Reference-conditioned voice cloning / TTS",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Voice | Freeze permitted input and target references, task and language/speaker groups.",
        "Consent, reference availability and output use are independent gates.",
    ],
    "research/voice-conversion-eval-20261101/README.md": [
        "### Chatterbox Nano (official reference-conditioned TTS)",
        "### CosyVoice 2 0.5B (zero-shot streaming TTS)",
        "### NeuTTS Nano Q4 (streaming cloned-voice TTS)",
        "### Kokoro 82M (fixed-voice TTS control)",
        "returned HTTP 401 because the Hugging Face repository is gated",
        "No inference result is claimed.",
        "Not a zero-shot voice cloning model.",
        "Whole-utterance generation took 11.47 s for 8.92 s audio (RTF 1.286), with no clipping.",
        "first chunk arrived 23.81 s after the inference call started; total generation took 80.66 s (file RTF 8.07\u00d7).",
        "first and only audio segment arrived after `57.297 s`; produced `9.025 s` of audio, real-time factor `0.158\u00d7`.",
        "The reference belongs to an upstream demo; its dataset/license provenance is not yet confirmed",
    ],
    "research/voice-conversion-eval-20261101/agent-chatterbox-breadth/REPORT.md": [
        "Chatterbox Nano TTS weights are a different model and are not a valid substitute.",
        "Do not trigger auto-download from the converter API or reuse Chatterbox Nano TTS files to bridge the first gate.",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        'Voice transformation,YourTTS,unavailable/blocked,"No local checkpoint, source checkout or speech-conversion adapter; no paired content/speaker test.",Identity; other TTS/VC pipelines,',
        "Voice transformation,VITS2,unavailable/blocked,No canonical checkpoint; cited implementation is unofficial WIP and no local conversion runtime exists.,YourTTS; identity,",
        "Voice transformation,Seed-TTS,unavailable/blocked,No accessible licensed checkpoint and input-conversion runtime verified,Identity; locally runnable TTS/VC,",
        "Voice transformation,StyleTTS 2,unavailable/blocked,No local model/checkpoint adapter; available task is expressive TTS rather than streaming source-speech enhancement.,Identity; explicit TTS/VC output task,",
        "Voice transformation,HiFi-GAN / Vocos vocoders,out of scope,Vocoder components do not independently transform input voice/accent,Fixed acoustic features / end-to-end VC,",
        "Voice transformation / TTS alternative,CosyVoice 2 0.5B zero-shot streaming TTS alternative,partially evaluated,",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/survey-trn-02/README.md": [
        "**Disposition: `DEFER` / `proposal_only_survey_incomplete` / `not_qualified`.**",
    ],
    "docs/task-evidence/survey-trn-03/README.md": [
        "**Disposition: `DEFER` / `proposal_only_survey_incomplete` / `not_qualified`.**",
        "speech-to-speech voice conversion (`TRN-04`), TTS/voice cloning",
    ],
    "docs/task-evidence/survey-rec-01/README.md": [
        "**Disposition: `DEFER` / `incomplete` / `not_qualified`.**",
    ],
    "docs/task-evidence/survey-spk-02/README.md": [
        "**Disposition: `DEFER` / `incomplete` / `not_qualified`.**",
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
    "tts_quality_claim": False,
    "voice_cloning_claim": False,
    "reference_similarity_claim": False,
    "naturalness_claim": False,
    "content_preservation_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
}

NON_CLAIMS: List[str] = [
    "no reference-conditioned TTS quality, cloning-fidelity or model-ranking result is measured by this survey",
    "no reference-voice similarity, naturalness or independent listening result exists",
    "no manual transcript, semantic-content gold or comprehension result exists",
    "no sustained streaming, first-audio/tail or device timing is measured",
    "no voice consent, reference provenance or output-use clearance is produced",
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
    "fixed_voice_tts_promoted_to_cloning": "rejected; state unchanged",
    "whole_utterance_return_promoted_to_streaming": "rejected; state unchanged",
    "listening_or_similarity_result_promoted": "rejected; state unchanged",
    "conversion_or_asr_promoted_to_tts": "rejected; state unchanged",
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


def _check_commit_ids() -> None:
    if len(BASE_COMMIT) != 40 or any(c not in "0123456789abcdef" for c in BASE_COMMIT):
        raise MapError("base commit is not a 40-hex id")
    if len(CLAIM_BASE_COMMIT) != 40 or any(c not in "0123456789abcdef" for c in CLAIM_BASE_COMMIT):
        raise MapError("claim base commit is not a 40-hex id")


def _check_taxonomy(workspace: Path) -> None:
    registry = strict_json_load(workspace / "research/category_registry.json")
    inventory = strict_json_load(workspace / "audio-benchmark-platform/plan/INVENTORY.json")
    registry_hit = [c for c in registry["categories"] if c.get("id") == CATEGORY_ID]
    inventory_hit = [c for c in inventory["taxonomy"] if c.get("id") == CATEGORY_ID]
    if len(registry_hit) != 1 or len(inventory_hit) != 1:
        raise MapError("TRN-05 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("TRN-05 taxonomy mismatch: %s" % key)
    if inventory_hit[0].get("task") != TASK:
        raise MapError("TRN-05 inventory task mismatch")
    if inventory_hit[0].get("legacy_family") != LEGACY_FAMILY:
        raise MapError("TRN-05 legacy family mismatch")
    if inventory_hit[0].get("legacy_backlog_state") != "catalogued":
        raise MapError("TRN-05 legacy backlog state mismatch")
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
        raise MapError("legacy family F14 / TRN-05 is not unique")
    entry = hits[0]
    expected = {
        "category_id": CATEGORY_ID,
        "family_id": LEGACY_FAMILY,
        "activation_state": "catalogued",
        "state": "catalogued",
        "scope": "requested_optional_adjacent",
        "next_action": "Plan discovery across required source buckets",
        "blockers": [],
        "dependencies": [],
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise MapError("legacy backlog mismatch: F14/TRN-05/%s" % key)


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
    source_paths = set(SOURCE_PINS)
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
        if row.get("source_pin") not in source_paths:
            raise MapError("historical execution pin is not a source pin: " + row["id"])
        if "wer_source_pin" in row and row["wer_source_pin"] not in source_paths:
            raise MapError("historical execution WER pin is not a source pin: " + row["id"])


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
        "reference_cloning_execution",
        "reference_similarity_measured",
        "naturalness_measured",
        "human_listening_result",
        "content_preservation_gold",
        "multi_utterance_or_multi_speaker_cohort",
        "rights_qualified_reference_voice_corpus",
        "streaming_first_audio_claim",
        "device_timing",
        "cpu_accelerator_parity",
        "tts_quality_claim",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "provider_enablement",
        "release_approval",
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
        "tts_quality_claim",
        "voice_cloning_claim",
        "reference_similarity_claim",
        "naturalness_claim",
        "content_preservation_claim",
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


def _build_report(workspace: Optional[str] = None, sdk_root: Optional[str] = None) -> Dict[str, Any]:
    ws = find_workspace(workspace)
    sdk = find_sdk_root(sdk_root)
    _check_commit_ids()
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
        "claim_base_commit": CLAIM_BASE_COMMIT,
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
            "reference_conditioned_tts_evaluation_present": False,
            "reference_similarity_present": False,
            "naturalness_listening_present": False,
            "streaming_first_audio_present": False,
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
        "provenance": {
            "claim_base_commit": CLAIM_BASE_COMMIT,
            "integration_base_commit": BASE_COMMIT,
            "board_claim_edited": False,
            "note": "The board claim recorded 39b8885 before three sibling survey merges; the branch was fast-forwarded to current origin/main 62923ff before authoring without editing any board row.",
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
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count is not eight")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in report["boundary"].values()):
        raise MapError("boundary is not closed")
    if report["scope"]["no_new_execution"] is not True:
        raise MapError("survey claims a new execution")
    if report["scope"]["voice_cloning_claim"] is not False:
        raise MapError("voice cloning is claimed")
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
