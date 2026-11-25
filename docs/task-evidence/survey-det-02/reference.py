# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-DET-02.

This module builds a bounded taxonomy/comparison evidence map for the
utterance-endpointing and turn-completion category (inventory category
``DET-02``, legacy family ``F11``). It reads only pinned, read-only documents
from the enclosing ``audioml`` workspace and the SDK worktree. It does not load
audio, weights, runtimes, media or the network, and it does not register,
expose, enable or qualify any endpointing or turn detector.

All curated records below are documentation mappings, not new measurements.
Historical local or source-reported values are transcribed verbatim from the
pinned documents and labelled with their original scope. A pause timer is not a
turn-completion model; a VAD activity decision is not an endpoint.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-DET-02"
TITLE = "Review coverage for Utterance endpointing and turn completion"
CATEGORY_ID = "DET-02"
LEGACY_FAMILY = "F11"
BRANCH = "swarm/SDK-SURVEY-DET-02"
BASE_COMMIT = "f2811bda1d07660fa5a98c538bfa9c845d0e1b0f"
PROFILE = "Analysis"
COMPONENT = "utterance-endpointing-turn-completion-evidence-map"
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
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "reports/vad-research/chaining-evaluation.md": "f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/tsm-followup-20261101/README.md": "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
}

# SDK-worktree-relative boundary pins. They are read only to prove that no
# public surface was touched and to ground the cited task-local evidence.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/d1-whole-clip-duration-planner/README.md": "4015900d23ad2bbceef0b44f4a3ae954a3adc6ada60398e303ace82dc0545418",
    "docs/task-evidence/silero-vad-pause-duration-rules/README.md": "b6e422c591364dffa8b6ab0d3c9c78a579a6c85c88f831d86ee8c9d27593ab1f",
    "docs/task-evidence/silero-vad-pause-duration-rules/report.json": "9aebd32c6dc61cf4c5d3d5e0b38fd82a2f083792a453bf9db9548e52cfa5b22d",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Detection and control",
    "name": "Utterance endpointing and turn completion",
    "scope": "discovered_extension",
    "output_kind": "control",
    "purpose": "Estimate when an utterance or conversational turn has ended.",
    "method_families": {
        "classic": "Silence timers and state machines",
        "ml": "Acoustic/prosodic and semantic turn models",
    },
    "input_output": "Audio activity, optionally text/context \u2192 completion decision",
    "live_or_comparison_boundary": (
        "Useful for optional recognition or voice-agent workflows; not a required "
        "filter on ordinary human calls. Pauses can occur within a turn."
    ),
    "source_ids": ["S03"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S03",
        "title": "LiveKit turn detection documentation",
        "url": "https://docs.livekit.io/agents/logic/turns/",
        "access_scope": "direct",
        "mapped_components": ["livekit-turn-detection", "livekit-python-host-adapter"],
        "gap_ids": ["G03", "G04", "G06", "G11"],
        "finding": (
            "Direct documentation lead for model-based turn detection that may "
            "combine audio with semantic or transcript context. No local "
            "runtime, model weights, exact revision, endpoint configuration, "
            "turn-labelled cohort or numeric result is present; no endpoint "
            "decision is reproduced from the documentation."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": (
            "Fixed or adaptive silence timers with hangover and state-machine "
            "completion"
        ),
        "components": ["silero-vad-pause-duration-rules"],
        "gap_ids": ["G01", "G02", "G07", "G08"],
        "status": "historical_local_synthetic_pause_controller_only",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": (
            "Framewise VAD activity suppliers used as timer input; activity is "
            "not a turn boundary"
        ),
        "components": [
            "webrtc-vad",
            "silero-vad-6-2-3-reference",
            "adaptive-energy-vad",
            "speexdsp-vad",
            "fixed-rms-vad",
        ],
        "gap_ids": ["G01", "G07"],
        "status": "historical_local_activity_only_no_turn_labels",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "VAD-conditioned pause trimming and playback policy",
        "components": [
            "source-vad-conditioning-for-playback",
            "d1-whole-clip-duration-planner",
        ],
        "gap_ids": ["G09"],
        "status": "considered_and_adjacent_rate_planner",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": (
            "Acoustic/prosodic end-of-turn detection with optional semantic "
            "context (named source lead S03)"
        ),
        "components": ["livekit-turn-detection", "livekit-python-host-adapter"],
        "gap_ids": ["G03", "G04", "G06", "G11"],
        "status": "documented_lead_no_local_execution",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": (
            "Acoustic disfluency or pause predictors used as adjacent turn cues"
        ),
        "components": [
            "speechbrain-disfluency-pause-predictor",
            "wavlm-acoustic-disfluency-model",
        ],
        "gap_ids": ["G05"],
        "status": "blocked_or_smoke_only_no_turn_labels",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": (
            "Transcript or text-conditioned semantic completion and filler "
            "annotation"
        ),
        "components": [
            "speech-recognition-translation-controls",
            "text-aware-filler-and-stutter-annotation",
            "waveform-only-filler-stutter-deletion",
        ],
        "gap_ids": ["G04", "G09"],
        "status": "no_local_transcript_or_completion_execution",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "Streaming ASR segmentation and utterance endpointing",
        "components": [
            "whisper-streaming",
            "simulstreaming",
            "streaming-conformer-ted",
            "fastconformer-streaming-asr",
        ],
        "gap_ids": ["G06"],
        "status": "blocked_no_runtime_or_checkpoint",
    },
    {
        "family_id": "MF-M5",
        "branch": "ml",
        "family": (
            "Prosodic feature regression head with a speech-rate target "
            "(adjacent, not end-of-turn)"
        ),
        "components": ["silero-vad-opensmile-small-regression-head"],
        "gap_ids": ["G02", "G05"],
        "status": "historical_local_synthetic_rate_head_only",
    },
]

# component_id and task/evidence_status are checked against plan/INVENTORY.json.
# Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "silero-vad-pause-duration-rules", "role": "endpoint_timer", "evidence_status": "partial", "task": "SDK-SILERO-VAD-PAUSE-DURATION-RULES"},
    {"component_id": "webrtc-vad", "role": "activity_input_boundary", "evidence_status": "evaluated", "task": "SDK-WEBRTC-VAD"},
    {"component_id": "silero-vad-6-2-3-reference", "role": "activity_input_boundary", "evidence_status": "evaluated", "task": "SDK-SILERO-VAD-6-2-3-REFERENCE"},
    {"component_id": "adaptive-energy-vad", "role": "activity_input_boundary", "evidence_status": "evaluated", "task": "SDK-ADAPTIVE-ENERGY-VAD"},
    {"component_id": "speexdsp-vad", "role": "activity_input_boundary", "evidence_status": "evaluated", "task": "SDK-SPEEXDSP-VAD"},
    {"component_id": "fixed-rms-vad", "role": "activity_input_boundary", "evidence_status": "evaluated", "task": "SDK-FIXED-RMS-VAD"},
    {"component_id": "source-vad-conditioning-for-playback", "role": "playback_boundary", "evidence_status": "considered", "task": "SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK"},
    {"component_id": "d1-whole-clip-duration-planner", "role": "adjacent_rate_planner", "evidence_status": "partial", "task": "SDK-D1-WHOLE-CLIP-DURATION-PLANNER"},
    {"component_id": "livekit-turn-detection", "role": "turn_model_lead", "evidence_status": "considered", "task": "SDK-LIVEKIT-TURN-DETECTION"},
    {"component_id": "livekit-python-host-adapter", "role": "host_adapter_lead", "evidence_status": "considered", "task": "SDK-LIVEKIT-PYTHON-HOST-ADAPTER"},
    {"component_id": "speechbrain-disfluency-pause-predictor", "role": "adjacent_disfluency_lead", "evidence_status": "blocked", "task": "SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR"},
    {"component_id": "wavlm-acoustic-disfluency-model", "role": "adjacent_disfluency_lead", "evidence_status": "partial", "task": "SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL"},
    {"component_id": "speech-recognition-translation-controls", "role": "transcript_boundary", "evidence_status": "considered", "task": "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS"},
    {"component_id": "text-aware-filler-and-stutter-annotation", "role": "adjacent_text_annotation", "evidence_status": "blocked", "task": "SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION"},
    {"component_id": "waveform-only-filler-stutter-deletion", "role": "adjacent_waveform_edit", "evidence_status": "considered", "task": "SDK-WAVEFORM-ONLY-FILLER-STUTTER-DELETION"},
    {"component_id": "whisper-streaming", "role": "asr_endpointing_lead", "evidence_status": "blocked", "task": "SDK-WHISPER-STREAMING"},
    {"component_id": "simulstreaming", "role": "asr_endpointing_lead", "evidence_status": "blocked", "task": "SDK-SIMULSTREAMING"},
    {"component_id": "streaming-conformer-ted", "role": "asr_endpointing_lead", "evidence_status": "blocked", "task": "SDK-STREAMING-CONFORMER-TED"},
    {"component_id": "fastconformer-streaming-asr", "role": "asr_endpointing_lead", "evidence_status": "blocked", "task": "SDK-FASTCONFORMER-STREAMING-ASR"},
    {"component_id": "silero-vad-opensmile-small-regression-head", "role": "adjacent_prosody_head", "evidence_status": "evaluated", "task": "SDK-SILERO-VAD-OPENSMILE-SMALL-REGRESSION-HEAD"},
]

EXCLUDED_BOUNDARIES: List[Dict[str, str]] = [
    {
        "boundary": "Speech activity detection (DET-01)",
        "reason": "Framewise speech/nonspeech activity is an input to a timer, never an utterance or turn boundary.",
    },
    {
        "boundary": "Rate and pause trimming (RATE)",
        "reason": "Typed silence/filler labels may drive playback budgeting; they do not decide that a turn has ended.",
    },
    {
        "boundary": "Speech recognition and translation controls",
        "reason": "Transcript text can supply semantic context, but ASR segmentation alone is not a turn-completion result.",
    },
    {
        "boundary": "Disfluency and filler editing",
        "reason": "Detecting a filler or stutter is not detecting the end of a turn and must never gate or delete audio.",
    },
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Nine synthetic conditions x three rate cases from the merged pause-duration package",
        "class": "historical_local_synthetic_pause_controller",
        "source_pin": "docs/task-evidence/silero-vad-pause-duration-rules/README.md",
        "boundary": "Exact half-open 160-sample intervals on a deterministic fixture; silence, pause and unknown validity only; no real speech, turn label, semantic context or endpoint accuracy.",
    },
    {
        "id": "CI-2",
        "input": "Three speaker-disjoint held-out AMI Mix-Headset meetings scored for framewise activity (DET-01)",
        "class": "historical_local_adjacent_activity_only",
        "source_pin": "reports/vad-research/chaining-evaluation.md",
        "boundary": "Speech/nonspeech activity labels only; no utterance or turn boundary labels, so cutoff delay, end-of-turn delay and endpoint accuracy are not computable.",
    },
    {
        "id": "CI-3",
        "input": "Source-reported 500 ms pause-trim sweep over reused AMI VAD timelines",
        "class": "source_reported_pause_overlap",
        "source_pin": "research/tsm-followup-20261101/README.md",
        "boundary": "1,172 s removed with 282 s overlapping word-labeled speech; a word-span overlap proxy, not rendered or listened-to audio, and not reproduced here.",
    },
    {
        "id": "CI-4",
        "input": "LiveKit turn detection documentation (S03)",
        "class": "source_reported_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation describes model-based audio/semantic turn detection; no runtime, weights, revision, configuration, cohort or numeric parity follows.",
    },
    {
        "id": "CI-5",
        "input": "Rights-qualified conversational turn and endpoint corpus",
        "class": "missing_required_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Not present in this task or the pinned research; no local asset, annotation, speaker split or turn definition is staged.",
    },
    {
        "id": "CI-6",
        "input": "D1 whole-clip planner over typed silence/filler labels",
        "class": "historical_local_adjacent_rate_planner",
        "source_pin": "docs/task-evidence/d1-whole-clip-duration-planner/README.md",
        "boundary": "Typed labels support exact playback-budget arithmetic; no end-of-turn decision, real-time inference, conversational context or device timing.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "identity/no pause action", "role": "Source interval maps exactly to output; proves the synthetic fixture does not hide changes.", "source_pin": "docs/task-evidence/silero-vad-pause-duration-rules/README.md"},
    {"id": "CT-2", "name": "unguarded 500 ms pause trim", "role": "Named baseline with recorded word-span overlap; not a product candidate.", "source_pin": "research/tsm-followup-20261101/README.md"},
    {"id": "CT-3", "name": "guarded 120/360 ms thresholds with 200 ms retention", "role": "Conservative local synthetic candidate; retains more pause than the unguarded baseline.", "source_pin": "docs/task-evidence/silero-vad-pause-duration-rules/README.md"},
    {"id": "CT-4", "name": "unknown-validity retention", "role": "Unknown time is never relabelled nonspeech or treated as a completed turn.", "source_pin": "docs/task-evidence/silero-vad-pause-duration-rules/README.md"},
    {"id": "CT-5", "name": "fixed-timer-only completion", "role": "Classic silence-timer baseline with no acoustic or semantic model; cannot distinguish a mid-turn pause.", "source_pin": "audio_categories.md"},
    {"id": "CT-6", "name": "upstream framewise VAD activity", "role": "Activity control only; a speech/nonspeech decision is not turn truth.", "source_pin": "reports/vad-research/chaining-evaluation.md"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Merged task-local synthetic pause-duration fixture",
        "class": "task_local_synthetic",
        "status": "Deterministic synthetic probability trace and interval controller; no real audio, model, weights or turn labels",
        "source_pin": "docs/task-evidence/silero-vad-pause-duration-rules/README.md",
    },
    {
        "asset": "Pause-overlap source report",
        "class": "source_reported_document",
        "status": "Documents 1,172 s removed and 282 s word-span overlap; provenance only, not reproduced",
        "source_pin": "research/tsm-followup-20261101/README.md",
    },
    {
        "asset": "LiveKit turn detection documentation (S03)",
        "class": "external_documentation",
        "status": "Direct documentation scope; no runtime, weights, exact revision or configuration",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "AMI held-out framewise activity reference",
        "class": "research_audio",
        "status": "CC BY 4.0 per the cited manifest; local only and not redistributed; no turn boundary labels",
        "source_pin": "reports/vad-research/chaining-evaluation.md",
    },
    {
        "asset": "Conversational turn corpus, endpoint annotations and turn-model weights",
        "class": "missing_asset",
        "status": "No rights-qualified corpus, annotation, split, checkpoint or runtime is staged",
        "source_pin": "audio_categories.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Guarded pause-duration controller on the merged synthetic fixture",
        "outcome_class": "historical_local_synthetic_pause_controller",
        "component_ids": ["silero-vad-pause-duration-rules"],
        "source_pin": "docs/task-evidence/silero-vad-pause-duration-rules/README.md",
        "values": {
            "conditions": 9,
            "rate_cases": 3,
            "total_case_variants": 27,
            "candidate_start_threshold_ms": 120,
            "candidate_end_threshold_ms": 360,
            "retention_ms": 200,
            "long_pause_candidate_output_samples": 12837,
            "long_pause_candidate_retained_pause_samples": 3237,
            "long_pause_candidate_speech_preservation_fraction": 1.0,
            "long_pause_candidate_word_span_overlap_samples": 0,
            "long_pause_baseline_output_samples": 9637,
            "long_pause_baseline_word_span_overlap_samples": 1280,
            "published_pause_removed_s": 1172,
            "published_word_overlap_s": 282,
            "unknown_validity_cases": 3,
        },
        "scope": (
            "Nine deterministic synthetic conditions at three rate cases; exact "
            "half-open 160-sample intervals and a fixture clock; no real speech, "
            "Silero runtime, weights, turn label, rendered playback, listening or "
            "device timing; not rerun by this survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "Upstream held-out AMI framewise activity comparison (no turn labels)",
        "outcome_class": "historical_local_adjacent_activity_only",
        "component_ids": [
            "webrtc-vad",
            "silero-vad-6-2-3-reference",
            "adaptive-energy-vad",
            "speexdsp-vad",
            "fixed-rms-vad",
        ],
        "source_pin": "reports/vad-research/chaining-evaluation.md",
        "values": {
            "heldout_meetings": 3,
            "scored_frame_ms": 20,
            "web_rtc_fn_percent": 7.31,
            "web_rtc_fp_percent": 49.54,
            "silero_fn_percent": 19.43,
            "silero_fp_percent": 8.20,
            "adaptive_energy_fn_percent": 33.15,
            "adaptive_energy_fp_percent": 21.58,
            "speexdsp_fn_percent": 2.45,
            "speexdsp_fp_percent": 77.03,
            "rms_fn_percent": 62.95,
            "rms_fp_percent": 25.35,
        },
        "scope": (
            "Three speaker-disjoint held-out AMI meetings scored for speech and "
            "nonspeech activity; there are no utterance or turn boundary labels, "
            "so no cutoff, end-of-turn delay or endpoint accuracy is derived. "
            "not rerun by this survey."
        ),
    },
    {
        "id": "HE-3",
        "label": "D1 whole-clip planner over typed silence/filler labels",
        "outcome_class": "historical_local_adjacent_rate_planner",
        "component_ids": ["d1-whole-clip-duration-planner"],
        "source_pin": "docs/task-evidence/d1-whole-clip-duration-planner/README.md",
        "values": {
            "case_variants": 23,
            "adverse_controls": 21,
            "identity_passes": 18,
            "nonidentity_controls": 5,
            "rate_bounds_passes": 22,
            "rate_bounds_failures": 1,
            "bounds_failure_case": "fixed_125",
            "rejected_adverse_controls": 20,
            "reported_infeasible_oracle_controls": 1,
            "missing_results": 0,
            "qualified_candidates": 0,
        },
        "scope": (
            "Typed silence and filler blocks feed an exact-rational playback "
            "budget; the planner makes no end-of-turn decision, uses no "
            "conversational context and measures no device timing. "
            "not rerun by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "LiveKit turn detection documentation and model-based turn claims",
        "class": "source_reported_documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Direct documentation scope; no local runtime, weights, revision, endpoint setting, turn-labelled cohort or numeric parity.",
    },
    {
        "id": "RO-2",
        "claim": "SpeechBrain disfluency/pause predictor candidate",
        "class": "source_reported_blocked_candidate",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Inventory row is blocked with no runnable source, checkpoint, licence, aligned label or local execution.",
    },
    {
        "id": "RO-3",
        "claim": "500 ms unguarded pause-trim overlap over reused AMI VAD timelines",
        "class": "source_reported_pause_overlap",
        "source_pin": "research/tsm-followup-20261101/README.md",
        "boundary": "Word-span overlap proxy only; not rendered audio, listening, endpoint accuracy or a reproduced sweep.",
    },
    {
        "id": "RO-4",
        "claim": "Whisper-Streaming, SimulStreaming, Streaming Conformer-TED and FastConformer ASR leads",
        "class": "source_reported_runtime_context",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Blocked rows with no local checkpoint, streaming runtime or adapter; ASR endpointing is not conversational turn completion.",
    },
    {
        "id": "RO-5",
        "claim": "WavLM acoustic disfluency inference smoke",
        "class": "source_reported_inference_smoke",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Loaded checkpoint keys and emitted positive outputs on a 4 s AMI crop; no aligned labels, no licence and no turn-completion score.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "timestamped_probabilities_and_events": "HE-1 transcribes exact pause/speech intervals from a synthetic fixture; no endpoint probability calibration is claimed",
        "quiet_and_active_speech": "CI-1 covers synthetic speech, short/long pause, silence and unfamiliar-speech conditions; real quiet speech is unavailable",
        "known_positives_and_negatives": "CI-1 has synthetic known regions; CI-2 has activity labels but no turn boundaries; CI-5 records the missing turn-labelled cohort",
        "onset_offset_delay": "HE-1 gives retained pause and trim intervals; cutoff delay and end-of-turn delay require labels that are not present",
        "stratified_fn_fp": "Not computable: no turn-labelled positives or negatives exist in the reviewed records",
        "validity_vs_nonspeech": "CT-4 and HE-1 unknown_validity; unknown time is never treated as nonspeech or a completed turn",
        "exact_source_intervals": "HE-1 uses exact half-open 160-sample intervals with a fixture clock",
        "independent_state": "Historical runs used fresh synthetic state; live pause/resume and turn-state preservation are untested",
        "availability_and_dropped_stale_events": "Synthetic event availability exists; no device availability, dropped-event or stale-event measurement",
        "cross_hop_behavior": "Upstream 20 ms activity frames and 160-sample v0 geometry differ; no cross-hop parity or live cadence is claimed",
    },
    "blocked": [
        "Rights-qualified conversational corpus with utterance and turn boundaries plus explicit unknown regions",
        "Frozen speaker/session-disjoint development and held-out partitions with independent label review",
        "Endpoint and turn metrics: cutoff delay, end-of-turn delay, false-cutoff rate and stratified uncertainty",
        "Matched identity, fixed-timer, VAD-only and human-endpoint controls",
        "Pinned real acoustic/prosodic and semantic turn runtimes, weights and exact revisions",
        "Paced live streaming state, maximum-wait fallback, overlap/barge-in and target-device timing",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "synthetic_pause_controller_local": True,
    "activity_only_upstream_local": True,
    "rate_planner_adjacent_local": True,
    "source_reported_only": True,
    "turn_labelled_real_corpus": False,
    "semantic_turn_model_execution": False,
    "human_listening_result": False,
    "device_timing": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "endpoint_accuracy_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Obtain a rights-qualified conversational corpus with utterance and turn boundaries and explicit unknown regions",
        "evidence_gap": "The synthetic pause fixture has no real speech or turn truth; AMI activity labels stop at speech/nonspeech; no turn-labelled corpus or split is staged.",
        "follow_up_ids": [
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner or rights-cleared turn corpus exists; the linked research-control and foundation rows own scoring tooling and evidence rules, not a new corpus.",
    },
    {
        "id": "G02",
        "actionable_gap": "Define and score endpoint versus turn completion, including cutoff delay and mid-turn pauses",
        "evidence_gap": "No reviewed record defines turn truth, false cutoff, delayed completion, maximum-wait fallback or overlap/barge-in; a VAD boundary is not a turn boundary.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner defines endpoint/turn truth; the linked evidence and scoring rows own acceptance rules and reference tooling.",
    },
    {
        "id": "G03",
        "actionable_gap": "Verify the LiveKit turn-detection source lead as a runnable external reference",
        "evidence_gap": "S03 documents model-based turn detection but no local runtime, exact revision, weights, endpoint configuration or turn-labelled execution exists.",
        "follow_up_ids": [
            "SDK-LIVEKIT-TURN-DETECTION",
            "SDK-LIVEKIT-PYTHON-HOST-ADAPTER",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked LiveKit feasibility and host-adapter rows own the external runtime lead; neither is runnable or qualified here.",
    },
    {
        "id": "G04",
        "actionable_gap": "Supply transcript/context conditioning without conflating ASR output with turn completion",
        "evidence_gap": "The semantic branch has no transcript source, language handling, typed context or semantic-completion execution; the candidate is catalogued only.",
        "follow_up_ids": [
            "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS",
            "SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked transcript-control and text-aware rows own typed text and semantic annotation; no ASR or semantic turn model runs here.",
    },
    {
        "id": "G05",
        "actionable_gap": "Evaluate acoustic disfluency and prosodic models against aligned turn labels with clear licensing",
        "evidence_gap": "SpeechBrain is blocked and WavLM has only an inference smoke without aligned labels or a licence; the local prosodic head targets speech rate, not turn completion.",
        "follow_up_ids": [
            "SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR",
            "SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL",
            "SDK-SILERO-VAD-OPENSMILE-SMALL-REGRESSION-HEAD",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked SpeechBrain and WavLM rows own the acoustic disfluency leads; neither supplies aligned turn labels or licensed weights here.",
    },
    {
        "id": "G06",
        "actionable_gap": "Keep streaming ASR segmentation and endpointing separate from conversational turn completion",
        "evidence_gap": "Whisper-Streaming, SimulStreaming, Streaming Conformer-TED and FastConformer are blocked; no checkpoint, runtime or endpoint execution is present.",
        "follow_up_ids": [
            "SDK-WHISPER-STREAMING",
            "SDK-SIMULSTREAMING",
            "SDK-STREAMING-CONFORMER-TED",
            "SDK-FASTCONFORMER-STREAMING-ASR",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked streaming-ASR rows own segmentation and endpointing leads; ASR endpointing is not a conversational turn result.",
    },
    {
        "id": "G07",
        "actionable_gap": "Pin and run a real framewise activity detector instead of the synthetic probability trace",
        "evidence_gap": "The pause controller consumes a synthetic probability trace, not a real Silero or other VAD runtime; the queued real reference has no merged endpoint evidence.",
        "follow_up_ids": [
            "SDK-SILERO-VAD-6-2-3-REFERENCE",
            "SDK-SURVEY-DET-01",
            "SDK-WEBRTC-VAD",
            "SDK-ADAPTIVE-ENERGY-VAD",
            "SDK-SPEEXDSP-VAD",
            "SDK-FIXED-RMS-VAD",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner provides a real activity runtime in this survey; the linked Silero and DET-01 rows own the upstream detector and its activity evidence.",
    },
    {
        "id": "G08",
        "actionable_gap": "Validate live timer state, partial frames, pause/resume and maximum-wait fallback",
        "evidence_gap": "HE-1 exercises an offline synthetic state machine; live callback state, late frames, unavailable intervals, timer reset and forced completion are untested.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-SILERO-VAD-PAUSE-DURATION-RULES",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner owns a live endpoint lifecycle; the linked timing foundation and pause-controller row own lifecycle rules and the synthetic state machine.",
    },
    {
        "id": "G09",
        "actionable_gap": "Keep endpoint decisions separate from pause trimming, playback gating and audio deletion",
        "evidence_gap": "Pause trim and the D1 planner use typed silence/filler labels for playback policy; neither is allowed to turn a pause or completion decision into deletion.",
        "follow_up_ids": [
            "SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK",
            "SDK-D1-WHOLE-CLIP-DURATION-PLANNER",
            "SDK-WAVEFORM-ONLY-FILLER-STUTTER-DELETION",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked source-conditioning and D1 rows own playback policy; neither turns a pause label into a completion decision.",
    },
    {
        "id": "G10",
        "actionable_gap": "Collect target-device availability, resource, maximum-wait and deadline evidence",
        "evidence_gap": "Only offline synthetic or accelerated desktop context exists; no phone callback path, memory ceiling, energy or deadline-miss distribution is measured for an endpoint detector.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No device-timing owner for endpointing exists; the linked foundation rows own the timing and evidence rules.",
    },
    {
        "id": "G11",
        "actionable_gap": "Resolve licence, weights, exact revisions and external parity for every ML family claimed",
        "evidence_gap": "No reviewed ML row has both a permitted weight/licence and an exact local revision; the LiveKit lead and the openSMILE context are documentation only.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-LIVEKIT-TURN-DETECTION",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked audit foundation and LiveKit lead own licensing and external comparison; no weights or exact parity are present.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING", "title": "VADToolkit and AMI scoring tooling", "mode": "research-control"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-LIVEKIT-TURN-DETECTION", "title": "LiveKit turn detection", "mode": "feasibility"},
    {"task_id": "SDK-LIVEKIT-PYTHON-HOST-ADAPTER", "title": "LiveKit Python host adapter", "mode": "feasibility"},
    {"task_id": "SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS", "title": "Speech recognition / translation controls", "mode": "feasibility"},
    {"task_id": "SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION", "title": "Text-aware filler and stutter annotation", "mode": "feasibility"},
    {"task_id": "SDK-WAVEFORM-ONLY-FILLER-STUTTER-DELETION", "title": "Waveform-only filler/stutter deletion", "mode": "research-control"},
    {"task_id": "SDK-SPEECHBRAIN-DISFLUENCY-PAUSE-PREDICTOR", "title": "SpeechBrain disfluency/pause predictor", "mode": "feasibility"},
    {"task_id": "SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL", "title": "WavLM acoustic disfluency model", "mode": "implementation"},
    {"task_id": "SDK-WHISPER-STREAMING", "title": "Whisper-Streaming", "mode": "feasibility"},
    {"task_id": "SDK-SIMULSTREAMING", "title": "SimulStreaming", "mode": "feasibility"},
    {"task_id": "SDK-STREAMING-CONFORMER-TED", "title": "Streaming Conformer-TED", "mode": "feasibility"},
    {"task_id": "SDK-FASTCONFORMER-STREAMING-ASR", "title": "FastConformer streaming ASR", "mode": "feasibility"},
    {"task_id": "SDK-SILERO-VAD-6-2-3-REFERENCE", "title": "Silero VAD 6.2.3 reference", "mode": "implementation"},
    {"task_id": "SDK-SURVEY-DET-01", "title": "Review coverage for Speech activity detection (VAD/SAD)", "mode": "taxonomy"},
    {"task_id": "SDK-SILERO-VAD-PAUSE-DURATION-RULES", "title": "Silero VAD + pause-duration rules", "mode": "implementation"},
    {"task_id": "SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK", "title": "Source/VAD conditioning for playback", "mode": "feasibility"},
    {"task_id": "SDK-D1-WHOLE-CLIP-DURATION-PLANNER", "title": "D1 whole-clip duration planner", "mode": "implementation"},
    {"task_id": "SDK-WEBRTC-VAD", "title": "WebRTC VAD", "mode": "implementation"},
    {"task_id": "SDK-ADAPTIVE-ENERGY-VAD", "title": "Adaptive-energy VAD", "mode": "implementation"},
    {"task_id": "SDK-SPEEXDSP-VAD", "title": "SpeexDSP VAD", "mode": "implementation"},
    {"task_id": "SDK-FIXED-RMS-VAD", "title": "Fixed RMS VAD", "mode": "implementation"},
    {"task_id": "SDK-SILERO-VAD-OPENSMILE-SMALL-REGRESSION-HEAD", "title": "Silero VAD + openSMILE + small regression head", "mode": "implementation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified conversational corpus with utterance and turn boundaries and explicit unknown regions"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen speaker/session-disjoint development and held-out partitions with independent label review"},
    {"id": "RG-03", "blocked": True, "requirement": "Matched identity, fixed-timer, VAD-only and human-endpoint controls with cutoff and end-of-turn delay distributions"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned real acoustic/prosodic and semantic turn runtimes, weights and exact revisions"},
    {"id": "RG-05", "blocked": True, "requirement": "Paced live state, maximum-wait fallback, overlap/barge-in and target-device availability evidence"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **DET-02 \u2014 Utterance endpointing and turn completion** |",
        "Pauses can occur within a turn.",
    ],
    "research/category_survey/sources.md": [
        "| S03 | [LiveKit turn detection documentation](https://docs.livekit.io/agents/logic/turns/) | analysis | direct |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Analysis | Score timestamped probabilities, event boundaries and detections.",
    ],
    "research/tsm-followup-20261101/README.md": [
        "At 500 ms, Silero would remove 1,172 s, of which 282 s overlapped word-labeled speech.",
        "Do not use an unguarded trim rule.",
    ],
    "reports/vad-research/chaining-evaluation.md": [
        "| WebRTC | 7.31% | 49.54% | 226.0s | 486.6s | 6.38\u00b5s | 20 / 70ms |",
        "| Silero | 19.43% | 8.20% | 601.0s | 80.5s | 68.35\u00b5s | 280 / -220ms |",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/silero-vad-pause-duration-rules/README.md": [
        "guarded 120/360 ms thresholds with 200 ms retention",
        "is never treated as nonspeech and is always retained",
        "For every one of the nine synthetic conditions and all three rate cases",
        "1172 s / 282 s",
    ],
    "docs/task-evidence/d1-whole-clip-duration-planner/README.md": [
        "All 23 case variants and 21 adverse controls",
        "the sole bounds failure is `fixed_125`",
        "0 qualified candidates",
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
    "real_conversation_audio": False,
    "real_corpus": False,
    "turn_labelled_real_corpus": False,
    "weights": False,
    "runtime_invocation": False,
    "semantic_context_model": False,
    "listening": False,
    "device_timing": False,
    "latency_claim": False,
    "benchmark_claim": False,
    "release_claim": False,
    "numeric_parity_claim": False,
    "processor_exposure": False,
    "public_default": False,
    "network_access": False,
}

NON_CLAIMS: List[str] = [
    "no endpoint or turn-completion accuracy is measured",
    "no cutoff or end-of-turn delay is measured",
    "no semantic turn model is executed",
    "no real conversation audio, corpus or turn label is used",
    "no listening, device timing or target playback result exists",
    "no latency, throughput or deadline result exists",
    "no provider, default, ABI, build, CI, board or release change is made",
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
        raise MapError("DET-02 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("DET-02 taxonomy mismatch: %s" % key)
    if inventory_hit[0].get("task") != TASK:
        raise MapError("DET-02 inventory task mismatch")
    if inventory_hit[0].get("legacy_family") != LEGACY_FAMILY:
        raise MapError("DET-02 legacy family mismatch")
    if inventory_hit[0].get("legacy_backlog_state") != "catalogued":
        raise MapError("DET-02 legacy backlog state mismatch")
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
        raise MapError("legacy family F11 / DET-02 is not unique")
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
            raise MapError("legacy backlog mismatch: F11/DET-02/%s" % key)


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
            raise MapError("historical execution scope is not bounded: " + row["id"])


def _check_evidence_classes() -> None:
    blob = " ".join(
        [row["class"] for row in COMPARISON_INPUTS]
        + [row["outcome_class"] for row in HISTORICAL_EXECUTIONS]
        + [row["class"] for row in REPORTED_OUTCOMES]
    )
    expected = {
        "synthetic_pause_controller_local": "historical_local_synthetic_pause_controller" in blob,
        "activity_only_upstream_local": "historical_local_adjacent_activity_only" in blob,
        "rate_planner_adjacent_local": "historical_local_adjacent_rate_planner" in blob,
        "source_reported_only": "source_reported_" in blob,
        "turn_labelled_real_corpus": "turn_labelled_real" in blob,
        "semantic_turn_model_execution": "semantic_turn_model" in blob,
        "human_listening_result": "human_listening" in blob or "listening_result" in blob,
        "device_timing": "device_timing" in blob,
        "new_execution_in_this_survey": "new_execution" in blob,
        "parity_or_qualification_claim": "qualification" in blob or "parity" in blob,
        "endpoint_accuracy_claim": "endpoint_accuracy" in blob,
    }
    if set(expected) != set(EVIDENCE_CLASSES):
        raise MapError("evidence-class keys do not match the checked set")
    for key, value in expected.items():
        if EVIDENCE_CLASSES[key] is not value:
            raise MapError("evidence class does not match mapped records: " + key)


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
        "real_speech",
        "real_conversation_audio",
        "real_corpus",
        "turn_labelled_real_corpus",
        "weights",
        "runtime_invocation",
        "semantic_context_model",
        "listening",
        "device_timing",
        "latency_claim",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "network_access",
    ):
        if SCOPE.get(key) is not False:
            raise MapError("scope must stay closed: " + key)
    if SCOPE.get("no_new_execution") is not True:
        raise MapError("survey must not create an execution")
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
    known = {link["task_id"] for link in BOARD_LINKS}
    gap_ids = {gap["id"] for gap in GAPS}
    if len(gap_ids) != len(GAPS):
        raise MapError("duplicate gap id")
    for gap in GAPS:
        if not isinstance(gap.get("follow_up_ids"), list) or not gap["follow_up_ids"]:
            raise MapError("gap has no linked board task: " + gap["id"])
        for task_id in gap["follow_up_ids"]:
            if task_id not in known:
                raise MapError("gap links an unlisted board task: %s/%s" % (gap["id"], task_id))
        if gap.get("feasibility_task_exists"):
            modes = {link["mode"] for link in BOARD_LINKS if link["task_id"] in gap["follow_up_ids"]}
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
    _check_scope_integrity()
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
            "turn_labelled_real_execution_present": False,
            "semantic_turn_model_execution_present": False,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
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
