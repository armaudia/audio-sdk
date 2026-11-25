# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-11.

This module builds a bounded taxonomy/comparison evidence map for the feedback
and howling control category (inventory category ``CLN-11``). It reads only
pinned, read-only documents from the enclosing ``audioml`` workspace and the
SDK worktree. It does not load audio, weights, runtimes, media or the network,
and it does not register, expose, enable or qualify any processor.

All curated records below are documentation mappings, not new measurements.
Merged task-local component values and historical survey-pilot values are
transcribed verbatim from pinned merged evidence/reports and labelled with
their original synthetic scope; none of them is a physical-loop, listening,
device, benchmark or release result.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-CLN-11"
TITLE = "Review coverage for Feedback and howling control"
CATEGORY_ID = "CLN-11"
LEGACY_FAMILY = "F08"
BRANCH = "swarm/SDK-SURVEY-CLN-11"
BASE_COMMIT = "9536dbef4a8c150702ef2be9a34ab360c45c1039"
PROFILE = "DSP"
COMPONENT = "feedback-howling-control-evidence-map"
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
)

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
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/feedback_control_20261028.md": "47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "reports/feedback-control/ami-closed-loop-screen.json": "bf6cdcaa96939d13572c470c521f2a0d38c578621f316cd5c493676f51a195f8",
    "reports/feedback-control/ml-heldout-path-screen.json": "8b93b346ed6c69a6d086bde9cb1dc8eebc3cb54b74c8874f1c00ded5e5a0f087",
    "reports/feedback-control/smard-measured-ir-screen.json": "22f0285e4debb9c9c2687694c234f846be734cb112be03d833b6ad72da66d140",
}

# SDK-worktree-relative public-boundary and merged-evidence pins. They are read
# only to prove that no public surface was touched and to ground curated values;
# no header, report or component is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/adaptive-feedback-notch/report.json": "7ac0a069736bd8d14212c3cbbcc288a632524d75a95b3f1afd9e73572118ff73",
    "docs/task-evidence/adaptive-notch-with-gain-margin/report.json": "b6732740cab7fafd9e270953d7b8f72b6d7951ee5e6d08c1e344a6e9ed228645",
    "docs/task-evidence/block-nlms-afc-with-margin/report.json": "f7326732ffea56f5c8a156df5087ac33b1204e28421350470d4338cdf249c1de",
    "docs/task-evidence/fixed-feedback-gain-margin/report.json": "c7cd3a0518c315a4871b011bd89d74d09207d2d5bf84105c5877a76bf158b2bf",
    "docs/task-evidence/logistic-feedback-gain-controller/report.json": "73445d3ef8c79b9ec34f56d81797310d5a53366289a52824b325e726083ff23e",
    "docs/task-evidence/narrow-biquad-notch/report.json": "c80db3087434ed0e8d5755b037e052ff3dfa5ae03d582f858ba76526253e99dd",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Acoustic cleanup and spatial processing",
    "name": "Feedback and howling control",
    "scope": "discovered_extension",
    "output_kind": "waveform/control",
    "purpose": "Control an amplifying microphone\u2013speaker feedback loop.",
    "method_families": {
        "classic": "Gain reduction; adaptive notches; feedback cancellation",
        "ml": "Neural-assisted Kalman filtering; hybrid feedback suppression",
    },
    "input_output": "Audio and method-specific loop/reference information \u2192 waveform/control",
    "live_or_comparison_boundary": (
        "Relevant only to affected loop configurations; not interchangeable with "
        "ordinary AEC. Code/weights eligibility unverified."
    ),
    "source_ids": ["S48", "S49"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "CLN",
    "meaning": "Acoustic cleanup and spatial processing",
    "category_id": CATEGORY_ID,
    "feedback_loop_control_only": True,
    "not_ordinary_acoustic_echo_cancellation_category": "CLN-05",
    "not_residual_echo_suppression_category": "CLN-06",
    "not_background_noise_suppression_category": "CLN-01",
    "not_gain_loudness_or_dynamic_range_category": "CLN-09",
    "not_tonal_correction_or_interference_filtering_category": "CLN-10",
    "not_beamforming_category": "CLN-07",
    "not_source_localization_category": "CLN-08",
    "reference_and_clock_alignment_is_engineering_boundary": "ENG-02",
    "note": (
        "Ordinary AEC (CLN-05), residual echo suppression (CLN-06), background "
        "noise suppression (CLN-01), gain/loudness/DRC (CLN-09), tonal correction "
        "or interference filtering (CLN-10), beamforming (CLN-07), source "
        "localization (CLN-08) and reference/clock alignment (ENG-02) are separate "
        "catalogued categories. They are named only to prevent scope inflation; "
        "their results are not pooled into a CLN-11 feedback-control claim."
    ),
}

FEEDBACK_BOUNDARY: Dict[str, Any] = {
    "feedback_loop_only": True,
    "not_interchangeable_with_ordinary_aec": True,
    "requires_recursive_loop_or_explicit_reference_facet": True,
    "closed_loop_stability_is_first_order": True,
    "fixed_gain_margin_is_a_baseline_not_a_selection": True,
    "notch_false_activation_on_tonal_speech_music_and_silence_is_a_material_stratum": True,
    "path_change_and_saturation_are_material_strata": True,
    "author_reported_numbers_are_not_local": True,
    "espressif_howl_license_restricted_to_espressif_products": True,
    "code_and_weights_eligibility_unverified": True,
    "measured_physical_loop_staged": False,
    "physical_gain_before_feedback_measured": False,
    "labelled_howl_corpus_staged": False,
    "neural_checkpoint_or_weights_staged": False,
    "device_timing_or_drift_measured": False,
    "listening_or_human_validation_result": False,
    "benchmark_or_release_qualification_present": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S48",
        "title": "Acoustic howling suppression vendor documentation",
        "url": "https://github.com/espressif/esp-adf-libs/blob/master/esp_audio_effects/docs/README_HOWL.md",
        "access_scope": "direct",
        "mapped_components": [
            "espressif-howl-1-4-2",
            "adaptive-feedback-notch",
            "adaptive-notch-with-gain-margin",
        ],
        "gap_ids": ["G01", "G06", "G09"],
        "finding": (
            "Vendor documentation for Espressif esp_audio_effects HOWL 1.4.2 "
            "names FFT peak criteria (PAPR, PHPR, PNPR and optional IMSD), "
            "dynamic biquad notches and a loop-margin gain controller. It is an "
            "ESP-IDF/SoC component under an Espressif-restricted licence, not a "
            "portable host library, and no package, runtime, weights or local "
            "execution is staged in this task; the source remains a design lead "
            "only."
        ),
    },
    {
        "source_id": "S49",
        "title": "Hybrid acoustic howling suppression paper",
        "url": "https://www.isca-archive.org/interspeech_2023/zhang23q_interspeech.html",
        "access_scope": "search excerpt",
        "mapped_components": [
            "hybrid-ahs-self-attentive-rnn-and-kalman",
            "neural-plus-kalman-howling-control",
            "neuralkalmanahs-covariance-reference-variants",
            "neural-direct-howling-suppression",
        ],
        "gap_ids": ["G02", "G03", "G08"],
        "finding": (
            "The Interspeech 2023 Hybrid AHS paper pairs a frequency-domain "
            "Kalman filter with a self-attentive RNN and reports a teacher-forced "
            "offline-training versus streaming-inference mismatch caused by the "
            "recursive loop. Only a search excerpt and author-reported results "
            "are reviewed; the public repositories expose demo material without "
            "source or checkpoints, so no local execution is staged."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Gain reduction and fixed feedback gain margin",
        "components": [
            "fixed-feedback-gain-margin",
            "adaptive-notch-with-gain-margin",
            "logistic-feedback-gain-controller",
        ],
        "gap_ids": ["G01", "G06", "G07"],
        "status": "evaluated_on_synthetic_fixtures_minus5db_baseline_only_no_measured_loop_or_selection",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Adaptive notch detection with dynamic biquad notches",
        "components": [
            "adaptive-feedback-notch",
            "adaptive-notch-with-gain-margin",
            "narrow-biquad-notch",
        ],
        "gap_ids": ["G01", "G06", "G07"],
        "status": "evaluated_on_synthetic_fixtures_false_activation_on_tonal_speech_and_music_remains",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Adaptive feedback cancellation (block-NLMS with playback reference)",
        "components": ["block-nlms-afc", "block-nlms-afc-with-margin"],
        "gap_ids": ["G01", "G04", "G06", "G07"],
        "status": "evaluated_on_synthetic_fixtures_reference_required_no_prediction_error_decorrelator_or_path_change_detector",
    },
    {
        "family_id": "MF-C4",
        "branch": "classic",
        "family": "Kalman adaptive feedback cancellation",
        "components": ["kalman-afc"],
        "gap_ids": ["G03", "G04", "G06"],
        "status": "catalogued_considered_no_local_implementation_execution_or_checkpoint",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Neural-assisted Kalman filtering",
        "components": [
            "hybrid-ahs-self-attentive-rnn-and-kalman",
            "neuralkalmanahs-covariance-reference-variants",
        ],
        "gap_ids": ["G02", "G03", "G08"],
        "status": "catalogued_candidates_blocked_no_source_checkpoint_weights_or_runtime",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Hybrid feedback suppression",
        "components": [
            "neural-plus-kalman-howling-control",
            "hybrid-ahs-self-attentive-rnn-and-kalman",
            "afc-spex",
        ],
        "gap_ids": ["G02", "G03", "G08"],
        "status": "catalogued_considered_or_blocked_no_runnable_hybrid_or_multichannel_checkpoint",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Neural direct howling suppression",
        "components": ["neural-direct-howling-suppression", "afc-spex"],
        "gap_ids": ["G02", "G03", "G08"],
        "status": "catalogued_considered_no_published_model_selected_no_weights",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "Learned feedback-risk gain control (ML-adjacent local baseline)",
        "components": ["logistic-feedback-gain-controller"],
        "gap_ids": ["G06", "G07"],
        "status": "evaluated_small_supervised_logistic_baseline_on_simulator_labels_not_a_published_neural_ahs",
    },
]

# Adjacent components are named to keep scope boundaries explicit. They are not
# CLN-11 feedback controls and none of their results is pooled here.
ADJACENT_BOUNDARIES: List[Dict[str, str]] = [
    {
        "component_id": "nlms-aec",
        "category_boundary": "CLN-05 reference-based acoustic echo cancellation",
        "relation": "Subtracts a known independent far-end playback reference from the microphone signal; a recursive feedback loop is not that open-loop AEC model.",
        "not_howling_control_evidence": True,
    },
    {
        "component_id": "webrtc-aec3",
        "category_boundary": "CLN-05 reference-based acoustic echo cancellation",
        "relation": "Production AEC with an explicit render reference; echo attenuation does not measure howl onset, stable gain or loop recovery.",
        "not_howling_control_evidence": True,
    },
    {
        "component_id": "fixed-rls-to-nlms-aec",
        "category_boundary": "CLN-05 reference-based acoustic echo cancellation",
        "relation": "AEC adaptation-family transition; no feedback-path estimation, notch policy or closed-loop controller.",
        "not_howling_control_evidence": True,
    },
    {
        "component_id": "speex-mdf-residual-postfilter",
        "category_boundary": "CLN-06 residual echo suppression",
        "relation": "Suppresses residual echo after AEC; it does not detect a narrow growing howl tone or stabilize a recursive loop.",
        "not_howling_control_evidence": True,
    },
    {
        "component_id": "webrtc-apm-ns",
        "category_boundary": "CLN-01 background noise suppression",
        "relation": "Stationary-noise suppression; sustained feedback tones are a different signal model and the component makes no loop-stability claim.",
        "not_howling_control_evidence": True,
    },
    {
        "component_id": "narrow-biquad-notch",
        "category_boundary": "CLN-10 tonal correction and interference filtering",
        "relation": "A fixed narrow notch primitive with an explicit frequency and bandwidth; it is partial local code, has no howl detector, gain policy or loop result, and is not relabelled here.",
        "not_howling_control_evidence": True,
    },
    {
        "component_id": "feed-forward-compressor",
        "category_boundary": "CLN-09 gain, loudness and dynamic-range control",
        "relation": "Ordinary level control; gain reduction in a feedback controller depends on loop-aware detection and recovery, not on a generic compressor curve.",
        "not_howling_control_evidence": True,
    },
    {
        "component_id": "envelope-agc",
        "category_boundary": "CLN-09 gain, loudness and dynamic-range control",
        "relation": "Slow automatic gain control; it neither estimates a feedback path nor guarantees loop stability.",
        "not_howling_control_evidence": True,
    },
    {
        "component_id": "neural-kalman-filtering-nkf",
        "category_boundary": "echo and room boundary (NKF for AEC)",
        "relation": "Neural Kalman filtering is catalogued for echo/path tracking under a room profile; it is not a catalogued CLN-11 howling-control candidate.",
        "not_howling_control_evidence": True,
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "adaptive-feedback-notch", "evidence_status": "evaluated", "task": "SDK-ADAPTIVE-FEEDBACK-NOTCH"},
    {"component_id": "adaptive-notch-with-gain-margin", "evidence_status": "evaluated", "task": "SDK-ADAPTIVE-NOTCH-WITH-GAIN-MARGIN"},
    {"component_id": "fixed-feedback-gain-margin", "evidence_status": "evaluated", "task": "SDK-FIXED-FEEDBACK-GAIN-MARGIN"},
    {"component_id": "block-nlms-afc", "evidence_status": "evaluated", "task": "SDK-BLOCK-NLMS-AFC"},
    {"component_id": "block-nlms-afc-with-margin", "evidence_status": "evaluated", "task": "SDK-BLOCK-NLMS-AFC-WITH-MARGIN"},
    {"component_id": "logistic-feedback-gain-controller", "evidence_status": "evaluated", "task": "SDK-LOGISTIC-FEEDBACK-GAIN-CONTROLLER"},
    {"component_id": "narrow-biquad-notch", "evidence_status": "partial", "task": "SDK-NARROW-BIQUAD-NOTCH"},
    {"component_id": "espressif-howl-1-4-2", "evidence_status": "considered", "task": "SDK-ESPRESSIF-HOWL-1-4-2"},
    {"component_id": "kalman-afc", "evidence_status": "considered", "task": "SDK-KALMAN-AFC"},
    {"component_id": "neural-direct-howling-suppression", "evidence_status": "considered", "task": "SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION"},
    {"component_id": "neural-plus-kalman-howling-control", "evidence_status": "considered", "task": "SDK-NEURAL-PLUS-KALMAN-HOWLING-CONTROL"},
    {"component_id": "hybrid-ahs-self-attentive-rnn-and-kalman", "evidence_status": "blocked", "task": "SDK-HYBRID-AHS-SELF-ATTENTIVE-RNN-AND-KALMAN"},
    {"component_id": "neuralkalmanahs-covariance-reference-variants", "evidence_status": "blocked", "task": "SDK-NEURALKALMANAHS-COVARIANCE-REFERENCE-VARIANTS"},
    {"component_id": "afc-spex", "evidence_status": "blocked", "task": "SDK-AFC-SPEX"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Merged task-local deterministic DSP fixtures for adaptive notch, notch plus margin, fixed gain margin, block-NLMS AFC plus margin, logistic gain control and the narrow biquad primitive",
        "class": "historical_local_component_fixture",
        "source_pin": "docs/task-evidence/fixed-feedback-gain-margin/report.json",
        "boundary": "Synthetic analytic fixtures with frozen seeds and explicit FIR feedback paths; no real speech, measured room, physical loudspeaker loop, listening or release result. Not rerun by this survey.",
    },
    {
        "id": "CI-2",
        "input": "AMI ES2004a closed-loop synthetic feedback pilot over 12 utterance crops, three loop gains/delays and six controllers",
        "class": "historical_local_survey_pilot",
        "source_pin": "reports/feedback-control/ami-closed-loop-screen.json",
        "boundary": "AMI supplies desired speech only and contains no acoustic-feedback ground truth; the loop, path and howl are simulated. One meeting/session, no speaker or room split, and thresholds were not tuned on development material. Not rerun by this survey.",
    },
    {
        "id": "CI-3",
        "input": "SMARD measured impulse-response shapes with AMI speech, six utterances, eight measured paths and three normalized loop gains",
        "class": "historical_local_survey_pilot",
        "source_pin": "reports/feedback-control/smard-measured-ir-screen.json",
        "boundary": "Real measured IR shapes shape the simulated path, but the loop is still simulated and each path peak is normalized to one; results are not calibrated physical gain-before-feedback and not a product PA measurement. Not rerun by this survey.",
    },
    {
        "id": "CI-4",
        "input": "Held-out-loudspeaker logistic howl-risk detector screen trained on SMARD configuration 0000 and evaluated on configurations 1000/2000",
        "class": "historical_local_survey_pilot",
        "source_pin": "reports/feedback-control/ml-heldout-path-screen.json",
        "boundary": "Labels are simulated feedback-dominance labels, not human howl annotations; one room, six clips, one training loudspeaker type and no music/background/path-change coverage. The detector is a small logistic baseline, not a published neural AHS. Not rerun by this survey.",
    },
    {
        "id": "CI-5",
        "input": "Espressif HOWL 1.4.2 vendor documentation and Interspeech 2023 Hybrid AHS paper excerpt",
        "class": "source_only_frozen_protocol",
        "source_pin": "research/feedback_control_20261028.md",
        "boundary": "Documentation and author-reported method names only; no pinned host package, runtime, checkpoint, weights, physical loop or numeric result executed or verified locally.",
    },
    {
        "id": "CI-6",
        "input": "Instrumented physical loudspeaker-to-microphone loop with measured path, loop gain/delay, amplifier/speaker saturation and calibrated gain-before-feedback",
        "class": "missing_measured_physical_loop",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Explicitly missing. The DSP profile requires real headroom, delay and numerical behavior; a product howling claim additionally needs a measured closed loop, not a simulator-only proxy.",
    },
    {
        "id": "CI-7",
        "input": "Rights-qualified real howl recordings and held-out speech/music corpus with path/gain metadata, labels and permissions",
        "class": "missing_labelled_howl_corpus",
        "source_pin": "audio_categories.md",
        "boundary": "Missing. AMI is speech, not feedback ground truth; SMARD supplies IRs, not howl labels. No recording consent, label protocol, permissions or independent development/evaluation split is staged.",
    },
    {
        "id": "CI-8",
        "input": "Exact runnable Kalman/neural/hybrid howling-suppression candidate with licensed weights, runtime, input contract and closed-loop-safe fallback",
        "class": "missing_neural_checkpoint",
        "source_pin": "research/feedback_control_20261028.md",
        "boundary": "Missing. Catalogued hybrid and AFC-SPEX rows are considered/blocked; public listings expose demo material or author-local checkpoints, and no weights are staged or licensed for this task.",
    },
    {
        "id": "CI-9",
        "input": "Frozen task-matched closed-loop benchmark protocol and held-out scorer for stable gain, detection/suppression time, residual tone, speech attenuation, false triggers, clipping and recovery",
        "class": "missing_benchmark_protocol",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Missing. No independent metric implementation, thresholds, subgroup split, failed-item accounting or submission policy is applied by this survey.",
    },
    {
        "id": "CI-10",
        "input": "Catalogued Kalman, neural-direct, neural-plus-Kalman, Hybrid AHS, NeuralKalmanAHS and AFC-SPEX candidate rows",
        "class": "source_reported_candidate_gap",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Plan metadata and source-reported candidates only; no selected ML howling controller, licensed checkpoint, runtime or local execution exists, so the ML candidate census remains not_started.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "identity / no control", "role": "A recursive loop must be shown to grow or ring; identity is an instability control, never a pass.", "source_pin": "reports/feedback-control/ami-closed-loop-screen.json"},
    {"id": "CT-2", "name": "fixed -5 dB gain margin", "role": "Conservative no-reference baseline comparator only; attenuation is scored separately from howl reduction and is not a selection.", "source_pin": "docs/task-evidence/fixed-feedback-gain-margin/report.json"},
    {"id": "CT-3", "name": "notch only versus notch plus margin", "role": "Separates tone detection from global gain reduction so neither is credited for the other.", "source_pin": "docs/task-evidence/adaptive-notch-with-gain-margin/report.json"},
    {"id": "CT-4", "name": "AFC only versus AFC plus margin", "role": "Separates playback-reference path estimation from fixed attenuation; AFC must not be credited when its gain is supplied by the margin.", "source_pin": "docs/task-evidence/block-nlms-afc-with-margin/report.json"},
    {"id": "CT-5", "name": "clean speech false activation", "role": "A howl detector must not fire on ordinary speech; tonal vowels and sustained vowels are a required stress stratum.", "source_pin": "docs/task-evidence/adaptive-feedback-notch/report.json"},
    {"id": "CT-6", "name": "silence and no-loop passthrough", "role": "Silence must stay silent and a no-loop path must remain passthrough; a forced notch or gain event is a false positive.", "source_pin": "docs/task-evidence/narrow-biquad-notch/report.json"},
    {"id": "CT-7", "name": "music and sustained-tone false trigger", "role": "Music, harmonics and sustained notes are tonal but not feedback; detector precision and speech damage are scored separately.", "source_pin": "research/feedback_control_20261028.md"},
    {"id": "CT-8", "name": "loop-gain and delay sweep", "role": "Stable, marginal and unstable loop gains plus delay changes expose onset detection and recovery; one gain is not a stability result.", "source_pin": "reports/feedback-control/smard-measured-ir-screen.json"},
    {"id": "CT-9", "name": "pre-tanh and post-clip saturation", "role": "Amplifier/loudspeaker nonlinearity changes the feedback path; linear-only results do not cover clipping cases.", "source_pin": "docs/task-evidence/fixed-feedback-gain-margin/report.json"},
    {"id": "CT-10", "name": "path change, reference mismatch and recovery", "role": "A changed path or shifted playback reference must adapt or fail closed; a residual or sustained howl is a failure, not a slow pass.", "source_pin": "docs/task-evidence/block-nlms-afc-with-margin/report.json"},
    {"id": "CT-11", "name": "double-talk-like and abrupt level change", "role": "Near-end speech and abrupt level changes must not be suppressed as feedback; near-end damage is a first-order outcome.", "source_pin": "docs/task-evidence/block-nlms-afc-with-margin/report.json"},
    {"id": "CT-12", "name": "adverse config and frame rejection", "role": "Missing, nonfinite, out-of-range, wrong-shape, stale-epoch and wrong-position inputs must fail closed with unchanged state.", "source_pin": "docs/task-evidence/adaptive-notch-with-gain-margin/report.json"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Merged task-local synthetic DSP fixtures and reports for six evaluated feedback components",
        "class": "sdk_synthetic_fixture",
        "status": "Merged task-local evidence only; deterministic analytic fixtures with no real speech, room, physical loop, weights or listening result",
        "source_pin": "docs/task-evidence/adaptive-feedback-notch/report.json",
    },
    {
        "asset": "AMI Meeting Corpus ES2004a Mix-Headset speech used by the historical pilot",
        "class": "research_speech_corpus_reference",
        "status": "Referenced through pinned research reports; not staged, redistributed or rerun here, and it contains no acoustic-feedback ground truth",
        "source_pin": "reports/feedback-control/ami-closed-loop-screen.json",
    },
    {
        "asset": "SMARD measured loudspeaker-to-microphone impulse responses used by the historical pilot",
        "class": "research_measured_ir_reference",
        "status": "Referenced through pinned research reports; audio files are not staged here and the simulated loop is not a calibrated physical PA measurement",
        "source_pin": "reports/feedback-control/smard-measured-ir-screen.json",
    },
    {
        "asset": "Espressif HOWL 1.4.2 documentation and Interspeech 2023 Hybrid AHS paper excerpt",
        "class": "external_documentation",
        "status": "Design/author-reported references only; no host runtime, source, checkpoint, weight licence or executed result is staged",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "Neural / hybrid howling-suppression checkpoints and licensed weights",
        "class": "missing_model_assets",
        "status": "Not staged; Hybrid AHS, NeuralKalmanAHS and AFC-SPEX rows are considered/blocked and no usable checkpoint is attached",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
    },
    {
        "asset": "Instrumented physical loudspeaker-microphone loop and calibrated gain-before-feedback measurement",
        "class": "missing_physical_loop_assets",
        "status": "Not present; synthetic loop and normalized measured-IR proxies are not a physical device or room measurement",
        "source_pin": "research/feedback_control_20261028.md",
    },
    {
        "asset": "Rights-qualified labelled howl corpus and frozen held-out scoring protocol",
        "class": "missing_corpus_assets",
        "status": "Not present; no real howl labels, permissions, development/evaluation split or metric implementation is staged",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "AMI closed-loop synthetic feedback pilot, six controllers (no physical loop)",
        "outcome_class": "historical_local_survey_pilot",
        "component_ids": [
            "fixed-feedback-gain-margin",
            "adaptive-feedback-notch",
            "adaptive-notch-with-gain-margin",
            "block-nlms-afc",
            "block-nlms-afc-with-margin",
        ],
        "source_pin": "reports/feedback-control/ami-closed-loop-screen.json",
        "values": {
            "n_candidates": 6,
            "runs_per_candidate": 36,
            "total_runs": 216,
            "utterances": 12,
            "loop_gains": [1.1, 1.25, 1.4],
            "delays_ms": [128, 160, 192],
            "identity_median_sdr_db": -6.511,
            "fixed_margin_minus_5db_median_sdr_db": 5.193,
            "adaptive_notch_median_sdr_db": -6.377,
            "notch_plus_margin_median_sdr_db": 0.17,
            "block_nlms_afc_median_sdr_db": -2.387,
            "afc_plus_3db_margin_median_sdr_db": 4.958,
            "fixed_margin_median_tail_feedback_to_speech_db": -10.651,
            "adaptive_notch_no_loop_false_notch_events": 19,
        },
        "scope": (
            "Historical survey pilot on one AMI meeting with a simulated recursive "
            "loop and short synthetic path; median values are transcribed with "
            "their original pilot scope. It is not a physical-loop result, not a "
            "product PA measurement, not a selection and not rerun by this survey."
        ),
    },
    {
        "id": "HE-2",
        "label": "SMARD measured-IR-shape closed-loop pilot, six controllers (no physical loop)",
        "outcome_class": "historical_local_survey_pilot",
        "component_ids": [
            "fixed-feedback-gain-margin",
            "adaptive-feedback-notch",
            "adaptive-notch-with-gain-margin",
            "block-nlms-afc",
            "block-nlms-afc-with-margin",
        ],
        "source_pin": "reports/feedback-control/smard-measured-ir-screen.json",
        "values": {
            "n_candidates": 6,
            "runs_per_candidate": 144,
            "utterances": 6,
            "measured_paths": 8,
            "loop_gains": [0.95, 1.05, 1.15],
            "identity_median_sdr_db": 5.671,
            "fixed_margin_minus_5db_median_sdr_db": 6.887,
            "adaptive_notch_median_sdr_db": 5.751,
            "notch_plus_margin_median_sdr_db": 6.259,
            "block_nlms_afc_median_sdr_db": 8.427,
            "afc_plus_3db_margin_median_sdr_db": 8.429,
            "fixed_margin_median_tail_feedback_to_speech_db": -25.626,
            "afc_plus_margin_median_tail_feedback_to_speech_db": -24.023,
        },
        "scope": (
            "Historical survey pilot using measured SMARD IR shapes with "
            "per-path peak normalization and a simulated loop; it is not a "
            "calibrated gain-before-feedback measurement, not a physical-loop "
            "result, not a selection and not rerun by this survey."
        ),
    },
    {
        "id": "HE-3",
        "label": "Held-out-loudspeaker logistic howl-risk detector pilot (ML baseline, no physical loop)",
        "outcome_class": "historical_local_survey_pilot",
        "component_ids": [
            "logistic-feedback-gain-controller",
            "fixed-feedback-gain-margin",
        ],
        "source_pin": "reports/feedback-control/ml-heldout-path-screen.json",
        "values": {
            "n_candidates": 7,
            "runs_per_candidate": 72,
            "train_configuration": "0000",
            "heldout_configurations": ["1000", "2000"],
            "heldout_paths": 4,
            "heldout_precision": 0.6443,
            "heldout_recall": 0.652,
            "heldout_false_positive_rate": 0.2641,
            "ml_median_sdr_db": 5.138,
            "ml_median_tail_feedback_to_speech_db": -34.385,
            "clean_speech_detection_events": 38,
            "fixed_margin_median_sdr_db": 7.076,
            "identity_median_sdr_db": 12.963,
        },
        "scope": (
            "Historical survey pilot of a small supervised logistic baseline on "
            "simulated feedback-dominance labels; it is not a published neural "
            "AHS, not a holdout for howling-control quality, not a physical-loop "
            "result, not a selection and not rerun by this survey."
        ),
    },
    {
        "id": "HE-4",
        "label": "Merged adaptive-feedback-notch deterministic DSP fixture",
        "outcome_class": "historical_local_component_fixture",
        "component_ids": ["adaptive-feedback-notch"],
        "source_pin": "docs/task-evidence/adaptive-feedback-notch/report.json",
        "values": {
            "frames": 300,
            "attack_frames": 3,
            "release_frames": 23,
            "activations": 1,
            "clean_speech_false_activations": 0,
            "loop_gain_1_05_identity_tail_db_relative_to_program": 31.513817951222443,
            "loop_gain_1_05_fixed_margin_tail_db_relative_to_program": -208.58809447854273,
            "nonfinite_frames": 0,
        },
        "scope": (
            "Merged synthetic model-free DSP fixture with a declared tone and "
            "clean-speech control. It is not a physical-loop result, not real "
            "speech or a room measurement, not a selection and not rerun by this "
            "survey."
        ),
    },
    {
        "id": "HE-5",
        "label": "Merged adaptive-notch-with-gain-margin deterministic DSP fixture",
        "outcome_class": "historical_local_component_fixture",
        "component_ids": ["adaptive-notch-with-gain-margin"],
        "source_pin": "docs/task-evidence/adaptive-notch-with-gain-margin/report.json",
        "values": {
            "frames": 300,
            "clean_speech_false_activations": 0,
            "g1_05_linear_fixed_gain_program_sdr_db": 7.19356175141994,
            "g1_05_linear_notch_plus_margin_program_sdr_db": -0.5980693136678471,
            "g1_05_linear_identity_nonfinite_frames": 0,
            "g1_05_linear_notch_plus_margin_releases": 1,
            "state_unchanged_after_rejection": True,
        },
        "scope": (
            "Merged synthetic model-free DSP fixture with explicit closed-loop "
            "cases and adverse controls. It is not a physical-loop result, not a "
            "measured PA path, not a selection and not rerun by this survey."
        ),
    },
    {
        "id": "HE-6",
        "label": "Merged fixed-feedback-gain-margin deterministic DSP fixture",
        "outcome_class": "historical_local_component_fixture",
        "component_ids": ["fixed-feedback-gain-margin"],
        "source_pin": "docs/task-evidence/fixed-feedback-gain-margin/report.json",
        "values": {
            "clean_speech_identity_program_sdr_db": 566.734,
            "clean_speech_minus5_program_sdr_db": 7.177,
            "minus5_rms_ratio": 0.562341325,
            "feedback_path_trial_cases": 6,
            "qualification_selected_is_null": True,
            "all_candidates_eligible_for_selection": False,
        },
        "scope": (
            "Merged synthetic model-free DSP fixture with explicit FIR feedback "
            "paths and bounded gain. It is not a physical-loop result, not a "
            "measured room, not a selection and not rerun by this survey."
        ),
    },
    {
        "id": "HE-7",
        "label": "Merged block-NLMS-AFC-with-margin deterministic DSP fixture",
        "outcome_class": "historical_local_component_fixture",
        "component_ids": ["block-nlms-afc-with-margin"],
        "source_pin": "docs/task-evidence/block-nlms-afc-with-margin/report.json",
        "values": {
            "frames": 200,
            "taps": 48,
            "loop_delay_samples": 160,
            "closed_loop_cases": 6,
            "identity_g1_05_program_sdr_db": -13.873780813769994,
            "afc_only_g1_05_program_sdr_db": 2.6383754719828794,
            "afc_plus_margin_g1_05_program_sdr_db": 6.276636320898361,
            "fixed_gain_g1_05_program_sdr_db": 16.34550704005723,
            "afc_only_g1_15_dual_paths_stability_class": "sustained_feedback",
            "missing_results_qualify_candidate": False,
        },
        "scope": (
            "Merged synthetic optional-task-local reference with explicit "
            "playback reference, delay alignment and saturation cases. It is not "
            "a physical-loop result, not a real-runtime measurement, not a "
            "selection and not rerun by this survey."
        ),
    },
    {
        "id": "HE-8",
        "label": "Merged logistic-feedback-gain-controller deterministic DSP fixture",
        "outcome_class": "historical_local_component_fixture",
        "component_ids": ["logistic-feedback-gain-controller"],
        "source_pin": "docs/task-evidence/logistic-feedback-gain-controller/report.json",
        "values": {
            "heldout_frames": 4050,
            "heldout_precision": 0.9731,
            "heldout_recall": 0.9968,
            "heldout_false_positive_rate": 0.0612,
            "runs_per_candidate": 27,
            "logistic_median_sdr_db": 20.775,
            "logistic_median_tail_feedback_to_speech_db": -29.631,
            "fixed_gain_median_sdr_db": 7.164,
            "identity_median_sdr_db": 10.825,
            "static_fallback_gain_db": -5.0,
            "invalid_model_fallback_reason": "missing_or_invalid_model",
        },
        "scope": (
            "Merged synthetic dependency-free port of the logistic detector on "
            "generated paths and a fixed-v0 frame boundary. Its coefficients are "
            "fixture-trained, not production weights; it is not a physical-loop "
            "result, not a published neural AHS and not rerun by this survey."
        ),
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "Espressif HOWL documents FFT peak criteria (PAPR, PHPR, PNPR, optional IMSD), dynamic biquad notches and a loop-margin gain controller for 1.4.2",
        "class": "source_reported",
        "source_pin": "research/feedback_control_20261028.md",
        "boundary": "Vendor documentation only; the ESP-IDF/SoC component is under an Espressif-restricted licence, is not a portable host library and was not run or validated locally.",
    },
    {
        "id": "RO-2",
        "claim": "The Interspeech 2023 Hybrid AHS pairs a frequency-domain Kalman filter with a self-attentive RNN and reports offline/streaming mismatch",
        "class": "source_reported",
        "source_pin": "research/feedback_control_20261028.md",
        "boundary": "Search excerpt plus author-reported method description; no source, checkpoint or numeric result is reproduced locally.",
    },
    {
        "id": "RO-3",
        "claim": "The 2024 journal study reports NeuralKalmanAHS SDR 2.65/1.98/1.45 dB and PESQ 2.33/2.17/2.04 at loop gains 2/2.5/3 on 200 utterances",
        "class": "source_reported",
        "source_pin": "research/feedback_control_20261028.md",
        "boundary": "Author-reported paper numbers on that setup; they are not repository results and are not comparable to the local synthetic screens or to CLN-01 DNS evidence.",
    },
    {
        "id": "RO-4",
        "claim": "AFC-SPEX is a current multichannel neural AFC candidate whose checked-in inference config expects three microphone channels and an author-local checkpoint",
        "class": "source_reported",
        "source_pin": "research/feedback_control_20261028.md",
        "boundary": "Repository review only; no checkpoint is included, the mono pilot input is incompatible and no execution or comparison is claimed.",
    },
    {
        "id": "RO-5",
        "claim": "The historical pilot names fixed -5 dB gain as the conservative no-reference fallback and AFC plus 3 dB margin as the quality-preserving pilot lead, with no production selection",
        "class": "source_reported",
        "source_pin": "research/feedback_control_20261028.md",
        "boundary": "Pilot recommendation on simulated loops, explicitly not a product safety or production sign-off; the ML gain controller and notch-only controller were not selected.",
    },
    {
        "id": "RO-6",
        "claim": "AMI ES2004a supplies desired meeting speech but contains no acoustic-feedback ground truth; SMARD supplies measured IRs, not howl labels",
        "class": "source_reported",
        "source_pin": "research/feedback_control_20261028.md",
        "boundary": "Dataset-characterisation statement; neither dataset is staged, cleared for redistribution here or promoted to a feedback benchmark.",
    },
    {
        "id": "RO-7",
        "claim": "The narrow biquad notch has local biquad code but no dedicated real-speech benchmark and no howl detector",
        "class": "source_reported",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Inventory plan note for a CLN-10 tonal primitive; it is a component of a howling controller at most, never a feedback result on its own.",
    },
    {
        "id": "RO-8",
        "claim": "Neural Kalman filtering (NKF) is catalogued for echo and room path tracking, not as a CLN-11 howling-control row",
        "class": "source_reported",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
        "boundary": "Plan metadata boundary only; no NKF model, weights or AEC result is pooled into this feedback map.",
    },
]

EXECUTION_COVERAGE: Dict[str, Any] = {
    "dedicated_howling_control_component_count": 13,
    "locally_evaluated_howling_control_component_count": 6,
    "classical_local_execution_count": 5,
    "ml_adjacent_local_execution_count": 1,
    "neural_howling_execution_count": 0,
    "physical_loop_execution_count": 0,
    "measured_physical_path_execution_count": 0,
    "labelled_howl_benchmark_execution_count": 0,
    "local_component_fixture_execution_count": 5,
    "historical_survey_pilot_execution_count": 3,
    "note": (
        "Six dedicated CLN-11 components have merged synthetic DSP execution "
        "reports; one is an ML-adjacent logistic baseline, not a neural model. "
        "Three historical survey pilots used AMI speech and/or measured SMARD IR "
        "shapes inside a simulated loop. No neural howling controller, physical "
        "loudspeaker-microphone loop, calibrated gain-before-feedback or labelled "
        "howl benchmark has been executed."
    ),
}

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "sweeps_steps_impulses": "HE-4 to HE-8 use deterministic sweeps, steps and impulses with frozen seeds and reported digests",
        "silence_and_clean_speech": "CT-5 and CT-6 require zero false activations on clean speech, tonal vowels and silence",
        "gain_and_response": "HE-6 records bounded gain, program SDR and RMS ratio; HE-7 records AFC and margin separately",
        "attack_release": "HE-4 reports 3-frame attack and 23-frame release; HE-5 records margin reduction and release events",
        "headroom_and_nonlinearity": "CT-9 covers pre-tanh and post-clip saturation; HE-7 reports peak output and sustained-feedback cases",
        "delay_and_numerical_behavior": "HE-7 records loop delay taps and reference latency offsets; all fixtures reject nonfinite input",
        "state_transitions_and_interactions": "CT-3, CT-4, CT-10 and CT-12 separate notch, margin, AFC and rejection behavior",
        "reference_conditions": "AFC rows require an explicit playback reference; no independent physical reference is measured",
        "closed_loop_conditions": "Survey pilots cover stable/marginal/unstable gains and delays inside a simulator, not a physical loop",
        "human_validation": "No listening panel, howl annotation adjudication or human validation exists",
    },
    "blocked": [
        "Instrumented physical loudspeaker-microphone loop with calibrated gain-before-feedback, path change and saturation",
        "Rights-qualified real howl recording and held-out speech/music corpus with labels and permissions",
        "Exact runnable Kalman/neural/hybrid candidate with licensed checkpoint, runtime and safe fallback",
        "Target-device latency, CPU/memory, deadline and device clock measurement",
        "Frozen task-matched metrics for stable gain, detection/suppression time, residual tone, speech attenuation, false triggers, clipping and recovery",
        "Separate comparison from AEC, residual echo, noise suppression, DRC and tonal filtering with no pooled result",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "local_synthetic_component_fixture": True,
    "historical_local_survey_pilot": True,
    "source_only_frozen_protocol": True,
    "source_reported_candidate_gap": True,
    "missing_measured_physical_loop": True,
    "missing_labelled_howl_corpus": True,
    "missing_neural_checkpoint": True,
    "missing_benchmark_protocol": True,
    "local_classical_howling_control_execution": True,
    "local_ml_adjacent_baseline_execution": True,
    "neural_howling_execution": False,
    "physical_loop_execution": False,
    "measured_physical_gain_before_feedback": False,
    "labelled_heldout_howl_benchmark": False,
    "device_timing_or_drift": False,
    "human_validation_result": False,
    "listening_result": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "release_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Build a bounded instrumented physical loudspeaker-microphone loop harness with measured path, delay, loop gain, saturation and calibrated gain-before-feedback",
        "evidence_gap": "All local executions are synthetic analytic fixtures or simulated loops over AMI speech and normalized SMARD IR shapes; no physical loop, measured gain-before-feedback or room result exists.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-DUPLEX",
            "SDK-FIXED-FEEDBACK-GAIN-MARGIN",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-11 measured-loop feasibility row was found; the timing/duplex foundations and the fixed-margin implementation row own scoping only, not a loop measurement.",
    },
    {
        "id": "G02",
        "actionable_gap": "Acquire a rights-qualified real howl recording and held-out speech/music corpus with path/gain metadata, labels, permissions and a development/evaluation split",
        "evidence_gap": "AMI is desired speech with no feedback ground truth and SMARD supplies IRs without howl labels; no real howl labels, consent or split is staged.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-11 corpus feasibility row was found; the asset-boundary and evidence foundations own intake and protocol rules, not a rights grant or corpus.",
    },
    {
        "id": "G03",
        "actionable_gap": "Pin one exact neural/Kalman/hybrid howling-suppression candidate with licensed checkpoint, runtime, input contract, safe fallback and closed-loop behavior",
        "evidence_gap": "Catalogued ML rows are considered or blocked; public listings expose demo material or author-local checkpoints and no weights are staged or evaluated.",
        "follow_up_ids": [
            "SDK-HYBRID-AHS-SELF-ATTENTIVE-RNN-AND-KALMAN",
            "SDK-NEURALKALMANAHS-COVARIANCE-REFERENCE-VARIANTS",
            "SDK-AFC-SPEX",
            "SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION",
            "SDK-NEURAL-PLUS-KALMAN-HOWLING-CONTROL",
        ],
        "feasibility_task_exists": True,
        "owner_note": "All five linked ML rows are feasibility scoping leads; none enables a model, stages weights or establishes an ML howling-control result.",
    },
    {
        "id": "G04",
        "actionable_gap": "Implement and qualify a bounded Kalman AFC reference with explicit playback reference, delay alignment, reset, reconvergence and path-change behavior",
        "evidence_gap": "Kalman AFC is considered only; the local AFC evidence is a block-NLMS baseline without a prediction-error decorrelator or path-change detector.",
        "follow_up_ids": [
            "SDK-KALMAN-AFC",
            "SDK-BLOCK-NLMS-AFC-WITH-MARGIN",
            "SDK-FND-DUPLEX",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The Kalman AFC feasibility row owns the scoping lead; the AFC-with-margin implementation row and duplex foundation supply reference/clock context only.",
    },
    {
        "id": "G05",
        "actionable_gap": "Measure target-device latency, CPU, memory, deadline and clock/drift behavior for the intended host while the loop is active",
        "evidence_gap": "Every local execution is a stdlib/Python synthetic fixture; no target-device runtime, deadline, buffer or device timing measurement exists.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-DUPLEX",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-11 device-runtime feasibility row was found; the timing and duplex foundations own lifecycle/clock contracts, not a device measurement.",
    },
    {
        "id": "G06",
        "actionable_gap": "Define a frozen task-matched closed-loop protocol and scorer for maximum stable gain, detection/suppression time, residual tone, speech attenuation, false triggers, clipping, latency and recovery",
        "evidence_gap": "Reports record candidate-specific medians on different synthetic fixtures; no shared metric implementation, threshold, stratification or held-out scorer is applied.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-ADAPTIVE-FEEDBACK-NOTCH",
            "SDK-ADAPTIVE-NOTCH-WITH-GAIN-MARGIN",
            "SDK-LOGISTIC-FEEDBACK-GAIN-CONTROLLER",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-11 benchmark-feasibility row was found; the evidence foundation and the three implementation rows own protocol and fixture scope only, not a benchmark result.",
    },
    {
        "id": "G07",
        "actionable_gap": "Keep feedback control separate from ordinary AEC, residual echo suppression, noise suppression, DRC and tonal notch filtering and require an independent control for each output",
        "evidence_gap": "CLN-01, CLN-05, CLN-06, CLN-09 and CLN-10 are catalogued neighbors; no component declares a loop-aware output and no cross-category ablation is staged.",
        "follow_up_ids": [
            "SDK-NLMS-AEC",
            "SDK-WEBRTC-AEC3",
            "SDK-NARROW-BIQUAD-NOTCH",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-11 separation-of-categories feasibility row was found; the linked AEC, notch and evidence rows are adjacent owners only, not feedback-control results.",
    },
    {
        "id": "G08",
        "actionable_gap": "Establish safe closed-loop inference and fallback for neural direct and neural-plus-Kalman suppression, including speech-preservation and residual-howl failure cases",
        "evidence_gap": "Neural direct suppression and neural-plus-Kalman control are considered only; no model, checkpoint, streaming inference, fallback or failure-envelope evidence exists.",
        "follow_up_ids": [
            "SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION",
            "SDK-NEURAL-PLUS-KALMAN-HOWLING-CONTROL",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The two neural feasibility rows own the scoping lead; the evidence foundation owns protocol rules, not a model or safety result.",
    },
    {
        "id": "G09",
        "actionable_gap": "Resolve code and weight licence eligibility for Espressif HOWL and every neural/hybrid candidate before any adapter, redistribution or release evidence",
        "evidence_gap": "HOWL 1.4.2 is restricted to Espressif products and prohibits non-Espressif redistribution; model weights are unstaged and unlicensed for this task.",
        "follow_up_ids": [
            "SDK-ESPRESSIF-HOWL-1-4-2",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-11 rights feasibility row was found; the external-adapter and asset-boundary rows own intake scoping, not a licence grant.",
    },
    {
        "id": "G10",
        "actionable_gap": "Require independent exact-head review before any benchmark, public default or release claim",
        "evidence_gap": "This proposal-only map has no independent reviewer, no benchmark result and no default-selection approval.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-11 review feasibility row was found; the evidence and asset-boundary foundations own protocol and intake rules, not independent approval.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-ADAPTIVE-FEEDBACK-NOTCH", "title": "Adaptive feedback notch", "mode": "implementation"},
    {"task_id": "SDK-ADAPTIVE-NOTCH-WITH-GAIN-MARGIN", "title": "Adaptive notch with gain margin", "mode": "implementation"},
    {"task_id": "SDK-AFC-SPEX", "title": "AFC-SPEX", "mode": "feasibility"},
    {"task_id": "SDK-BLOCK-NLMS-AFC-WITH-MARGIN", "title": "Block-NLMS AFC with margin", "mode": "implementation"},
    {"task_id": "SDK-ESPRESSIF-HOWL-1-4-2", "title": "Espressif HOWL 1.4.2", "mode": "external-adapter"},
    {"task_id": "SDK-FIXED-FEEDBACK-GAIN-MARGIN", "title": "Fixed feedback gain margin", "mode": "implementation"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-FND-DUPLEX", "title": "Reference, multichannel and clock contracts", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-HYBRID-AHS-SELF-ATTENTIVE-RNN-AND-KALMAN", "title": "Hybrid AHS self-attentive RNN and Kalman", "mode": "feasibility"},
    {"task_id": "SDK-KALMAN-AFC", "title": "Kalman AFC", "mode": "feasibility"},
    {"task_id": "SDK-LOGISTIC-FEEDBACK-GAIN-CONTROLLER", "title": "Logistic feedback gain controller", "mode": "implementation"},
    {"task_id": "SDK-NARROW-BIQUAD-NOTCH", "title": "Narrow biquad notch", "mode": "implementation"},
    {"task_id": "SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION", "title": "Neural direct howling suppression", "mode": "feasibility"},
    {"task_id": "SDK-NEURAL-PLUS-KALMAN-HOWLING-CONTROL", "title": "Neural plus Kalman howling control", "mode": "feasibility"},
    {"task_id": "SDK-NEURALKALMANAHS-COVARIANCE-REFERENCE-VARIANTS", "title": "NeuralKalmanAHS covariance/reference variants", "mode": "feasibility"},
    {"task_id": "SDK-NLMS-AEC", "title": "NLMS AEC", "mode": "implementation"},
    {"task_id": "SDK-WEBRTC-AEC3", "title": "WebRTC AEC3", "mode": "implementation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Instrumented physical loudspeaker-microphone loop with calibrated gain-before-feedback, measured path/delay and saturation"},
    {"id": "RG-02", "blocked": True, "requirement": "Rights-qualified real howl recordings and held-out speech/music corpus with labels, permissions and a development/evaluation split"},
    {"id": "RG-03", "blocked": True, "requirement": "Exact runnable Kalman/neural/hybrid candidate with licensed checkpoint, runtime, input contract and safe closed-loop fallback"},
    {"id": "RG-04", "blocked": True, "requirement": "Target-device latency, CPU, memory, deadline and device clock/drift measurement while the loop is active"},
    {"id": "RG-05", "blocked": True, "requirement": "Frozen task-matched protocol and scorer for stable gain, detection/suppression time, residual tone, speech attenuation, false triggers, clipping and recovery"},
    {"id": "RG-06", "blocked": True, "requirement": "Separate comparison from AEC, residual echo, noise suppression, DRC and tonal filtering; no adjacent result is pooled"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-08", "blocked": True, "requirement": "Explicit public default selection approval and release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated facts and caveats are grounded in
# the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-11 \u2014 Feedback and howling control** | Control an amplifying microphone\u2013speaker feedback loop. Scope: discovered_extension. | Gain reduction; adaptive notches; feedback cancellation | Neural-assisted Kalman filtering; hybrid feedback suppression |",
        "| **CLN-05 \u2014 Reference-based acoustic echo cancellation (AEC)**",
        "| **CLN-10 \u2014 Tonal correction and interference filtering**",
    ],
    "research/category_survey/sources.md": [
        "| S48 | [Acoustic howling suppression vendor documentation](https://github.com/espressif/esp-adf-libs/blob/master/esp_audio_effects/docs/README_HOWL.md) | root | direct |",
        "| S49 | [Hybrid acoustic howling suppression paper](https://www.isca-archive.org/interspeech_2023/zhang23q_interspeech.html) | root | search excerpt |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| DSP | Use sweeps, steps, impulses, silence, clean speech and an intelligibility or load-specific control. Measure gain, response, attack/release where applicable, headroom, delay and numerical behavior. Capture state transitions and interacting nonlinear configurations. |",
    ],
    "audio-benchmark-platform/plan/INVENTORY.json": [
        '"id": "CLN-11",',
        '"id": "adaptive-feedback-notch",',
        '"id": "afc-spex",',
    ],
    "research/category_registry.json": [
        '"id": "CLN-11",',
        '"id": "S48",',
        '"id": "S49",',
    ],
    "research/task_backlog.json": [
        '"category_id":"CLN-11","dependencies":[],"family_id":"F08"',
    ],
    "research/feedback_control_20261028.md": [
        "This differs from ordinary AEC. In AEC, a known far-end playback reference is subtracted from an independent near-end microphone signal.",
        "The library is an ESP-IDF/SoC component rather than a portable host library.",
        "These are paper results on that setup, not results from this repository or comparable to the current CLN-01 DNS screen.",
        "**Current screen leader: fixed gain margin as a baseline comparator only. No production selection.**",
        "The current recommendation is a pilot choice, not a product safety or production sign-off.",
    ],
    "reports/feedback-control/ami-closed-loop-screen.json": [
        '"protocol": "AMI ES2004a annotated speech, synthetic closed-loop acoustic feedback; pilot screen, not a public feedback benchmark"',
        '"median_sdr_db": 5.193,',
    ],
    "reports/feedback-control/smard-measured-ir-screen.json": [
        '"protocol": "Closed-loop screening on real measured SMARD IR shapes with AMI speech; loop gain normalized by each measured path frequency-response peak."',
        '"median_sdr_db": 8.427,',
    ],
    "reports/feedback-control/ml-heldout-path-screen.json": [
        '"protocol": "ML howl-risk detector trained on measured-path closed-loop simulations from SMARD loudspeaker 0000; evaluated on held-out loudspeakers 1000 and 2000."',
        '"precision": 0.6443,',
        '"clean_speech_detection_events": 38,',
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/adaptive-feedback-notch/report.json": [
        '"scope":"synthetic model-free DSP fixture; no real audio, device or release claim"',
    ],
    "docs/task-evidence/adaptive-notch-with-gain-margin/report.json": [
        '"scope":"synthetic model-free DSP; no real audio, device, model or release claim"',
    ],
    "docs/task-evidence/fixed-feedback-gain-margin/report.json": [
        '"scope":"synthetic model-free DSP; explicit FIR feedback paths only; no room, physical loop, device, model or release claim"',
        '"selected":null',
    ],
    "docs/task-evidence/block-nlms-afc-with-margin/report.json": [
        '"scope":"optional-task-local-reference"',
        '"missing_results_qualify_candidate":false',
    ],
    "docs/task-evidence/logistic-feedback-gain-controller/report.json": [
        '"protocol":"Synthetic, dependency-free port of the pinned logistic howl-risk screen',
        '"static_fallback"',
    ],
    "docs/task-evidence/narrow-biquad-notch/report.json": [
        '"scope":"Deterministic model-free DSP fixture; no real audio, device, listening or release qualification."',
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
    "real_loop_audio": False,
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
    "physical_loop_claim_without_physical_loop_execution": "rejected; state unchanged",
    "open_loop_overlay_promoted_to_closed_loop": "rejected; state unchanged",
    "synthetic_fixture_relabelled_physical": "rejected; state unchanged",
    "fixed_margin_baseline_promoted_to_selection": "rejected; state unchanged",
    "author_reported_promoted_to_local_execution": "rejected; state unchanged",
    "notch_without_detector_claimed_as_howling_control": "rejected; state unchanged",
    "heldout_benchmark_claim_without_labelled_split": "rejected; state unchanged",
    "release_claim_without_closed_gates": "rejected; state unchanged",
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
        raise MapError("CLN-11 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-11 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F08 / CLN-11 is not unique")
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
            raise MapError("legacy backlog mismatch: F08/CLN-11/%s" % key)


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
        if component.get("verification_profile") != "dsp":
            raise MapError("component profile is not dsp: " + row["component_id"])
    mapped = {c for lead in SOURCE_LEADS for c in lead["mapped_components"]}
    mapped.update(c for family in METHOD_FAMILIES for c in family["components"])
    mapped.update(row["component_id"] for row in ADJACENT_BOUNDARIES)
    mapped.update(c for row in HISTORICAL_EXECUTIONS for c in row["component_ids"])
    missing = sorted(mapped - set(by_id))
    if missing:
        raise MapError("mapped component missing from inventory: " + ",".join(missing))
    census_ids = {row["component_id"] for row in COMPONENT_CENSUS}
    if "adaptive-feedback-notch" not in census_ids or "fixed-feedback-gain-margin" not in census_ids:
        raise MapError("dedicated feedback components are not censused")


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
        if row.get("outcome_class") not in (
            "historical_local_component_fixture",
            "historical_local_survey_pilot",
        ):
            raise MapError("historical execution is not explicitly local/adjacent: " + row["id"])
        scope = row.get("scope", "")
        if "not a physical-loop result" not in scope:
            raise MapError("historical execution is not labelled not-a-physical-loop: " + row["id"])
        if "not rerun by this survey" not in scope:
            raise MapError("historical execution is not labelled not-rerun: " + row["id"])
        if not row.get("values"):
            raise MapError("historical execution has no values: " + row["id"])
        if row["outcome_class"] == "historical_local_component_fixture":
            if not str(row.get("source_pin", "")).startswith("docs/task-evidence/"):
                raise MapError("component fixture is not pinned to local evidence: " + row["id"])
        else:
            if row.get("source_pin") not in SOURCE_PINS:
                raise MapError("survey pilot is not pinned to a source report: " + row["id"])


def _check_evidence_classes() -> None:
    input_classes = {row["class"] for row in COMPARISON_INPUTS}
    checks = {
        "local_synthetic_component_fixture": "historical_local_component_fixture" in input_classes,
        "historical_local_survey_pilot": "historical_local_survey_pilot" in input_classes,
        "source_only_frozen_protocol": "source_only_frozen_protocol" in input_classes,
        "source_reported_candidate_gap": "source_reported_candidate_gap" in input_classes,
        "missing_measured_physical_loop": "missing_measured_physical_loop" in input_classes,
        "missing_labelled_howl_corpus": "missing_labelled_howl_corpus" in input_classes,
        "missing_neural_checkpoint": "missing_neural_checkpoint" in input_classes,
        "missing_benchmark_protocol": "missing_benchmark_protocol" in input_classes,
        "local_classical_howling_control_execution": any(
            row["outcome_class"] == "historical_local_component_fixture"
            and row["id"] in ("HE-4", "HE-5", "HE-6", "HE-7")
            for row in HISTORICAL_EXECUTIONS
        ),
        "local_ml_adjacent_baseline_execution": any(
            row["id"] == "HE-8" for row in HISTORICAL_EXECUTIONS
        ),
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in (
        "neural_howling_execution",
        "physical_loop_execution",
        "measured_physical_gain_before_feedback",
        "labelled_heldout_howl_benchmark",
        "device_timing_or_drift",
        "human_validation_result",
        "listening_result",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "release_claim",
    ):
        if EVIDENCE_CLASSES[key] is not False:
            raise MapError("unsupported claim is not closed: " + key)
    if not any(row["class"] == "source_reported" for row in REPORTED_OUTCOMES):
        raise MapError("source-reported class has no backing row")


def _check_execution_coverage() -> None:
    zero_counts = (
        "neural_howling_execution_count",
        "physical_loop_execution_count",
        "measured_physical_path_execution_count",
        "labelled_howl_benchmark_execution_count",
    )
    for key in zero_counts:
        if EXECUTION_COVERAGE.get(key) != 0:
            raise MapError("execution coverage claim changed: " + key)
    if EXECUTION_COVERAGE.get("local_component_fixture_execution_count") != 5:
        raise MapError("component fixture count changed")
    if EXECUTION_COVERAGE.get("historical_survey_pilot_execution_count") != 3:
        raise MapError("survey pilot count changed")
    fixtures = [r for r in HISTORICAL_EXECUTIONS if r["outcome_class"] == "historical_local_component_fixture"]
    pilots = [r for r in HISTORICAL_EXECUTIONS if r["outcome_class"] == "historical_local_survey_pilot"]
    if len(fixtures) != EXECUTION_COVERAGE["local_component_fixture_execution_count"]:
        raise MapError("component fixture count is inconsistent")
    if len(pilots) != EXECUTION_COVERAGE["historical_survey_pilot_execution_count"]:
        raise MapError("survey pilot count is inconsistent")
    if EXECUTION_COVERAGE.get("classical_local_execution_count") != 5:
        raise MapError("classical execution count changed")
    if EXECUTION_COVERAGE.get("ml_adjacent_local_execution_count") != 1:
        raise MapError("ML-adjacent execution count changed")
    if any("physical" in row["outcome_class"] for row in HISTORICAL_EXECUTIONS):
        raise MapError("an adjacent execution is relabelled as a physical loop")
    if not any(lead["access_scope"] == "search excerpt" for lead in SOURCE_LEADS):
        raise MapError("S49 access scope is not a search excerpt")
    if not any(lead["access_scope"] == "direct" for lead in SOURCE_LEADS):
        raise MapError("S48 access scope is not direct")


def _check_feedback_boundary() -> None:
    required_true = (
        "feedback_loop_only",
        "not_interchangeable_with_ordinary_aec",
        "requires_recursive_loop_or_explicit_reference_facet",
        "closed_loop_stability_is_first_order",
        "fixed_gain_margin_is_a_baseline_not_a_selection",
        "notch_false_activation_on_tonal_speech_music_and_silence_is_a_material_stratum",
        "path_change_and_saturation_are_material_strata",
        "author_reported_numbers_are_not_local",
        "espressif_howl_license_restricted_to_espressif_products",
        "code_and_weights_eligibility_unverified",
    )
    required_false = (
        "measured_physical_loop_staged",
        "physical_gain_before_feedback_measured",
        "labelled_howl_corpus_staged",
        "neural_checkpoint_or_weights_staged",
        "device_timing_or_drift_measured",
        "listening_or_human_validation_result",
        "benchmark_or_release_qualification_present",
    )
    if set(FEEDBACK_BOUNDARY) != set(required_true) | set(required_false):
        raise MapError("feedback boundary keys changed")
    for key in required_true:
        if FEEDBACK_BOUNDARY[key] is not True:
            raise MapError("feedback boundary rule is not enforced: " + key)
    for key in required_false:
        if FEEDBACK_BOUNDARY[key] is not False:
            raise MapError("feedback boundary claim is not closed: " + key)


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
    for row in COMPONENT_CENSUS:
        if row["task"] not in by_id:
            raise MapError("census task is not on the board: " + row["task"])
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
    _check_execution_coverage()
    _check_feedback_boundary()
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
        "qualification": {
            "decision": DECISION,
            "status": QUALIFICATION_STATUS,
            "qualification_status": QUALIFICATION_STATUS,
            "readiness": READINESS,
            "qualifies": False,
            "processor_exposure": False,
            "missing_result_promoted": False,
            "local_synthetic_execution_present": True,
            "physical_loop_execution_present": False,
            "neural_howling_execution_present": False,
            "release_qualification_present": False,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "category_scope": dict(CATEGORY_SCOPE),
        "feedback_boundary": dict(FEEDBACK_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "dedicated_howling_control_component_ids": [
                row["component_id"]
                for row in COMPONENT_CENSUS
                if row["component_id"] != "narrow-biquad-notch"
            ],
            "local_synthetic_fixture_present": True,
            "physical_loop_present": False,
            "calibrated_gain_before_feedback_present": False,
            "licensed_howl_corpus_present": False,
            "ml_howling_candidate_selected": False,
            "neural_checkpoint_or_weights_present": False,
            "independent_heldout_howl_split_present": False,
            "runnable_host_adapter_present": False,
            "note": "Thirteen dedicated CLN-11 components are catalogued; six have merged synthetic local reports but no physical loop, licensed corpus, selected ML candidate, neural checkpoint, host adapter or held-out split is staged.",
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
        "adjacent_boundaries": [dict(row) for row in ADJACENT_BOUNDARIES],
        "component_census": [dict(row) for row in COMPONENT_CENSUS],
        "comparison_inputs": [dict(row) for row in COMPARISON_INPUTS],
        "controls": [dict(row) for row in CONTROLS],
        "assets": [dict(row) for row in ASSETS],
        "historical_executions": [dict(row) for row in HISTORICAL_EXECUTIONS],
        "execution_coverage": dict(EXECUTION_COVERAGE),
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
    if report["qualification"]["status"] != QUALIFICATION_STATUS:
        raise MapError("nested qualification status changed")
    if report["qualification"]["physical_loop_execution_present"] is not False:
        raise MapError("a physical loop execution is claimed")
    if report["qualification"]["neural_howling_execution_present"] is not False:
        raise MapError("a neural howling execution is claimed")
    if report["qualification"]["release_qualification_present"] is not False:
        raise MapError("release qualification is claimed")
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
        "real_loop_audio",
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
        "local_synthetic_fixture_present",
    ):
        if report["discovery"][key] is not True:
            raise MapError("local fixture presence is not recorded: " + key)
    for key in (
        "physical_loop_present",
        "calibrated_gain_before_feedback_present",
        "licensed_howl_corpus_present",
        "ml_howling_candidate_selected",
        "neural_checkpoint_or_weights_present",
        "independent_heldout_howl_split_present",
        "runnable_host_adapter_present",
    ):
        if report["discovery"][key] is not False:
            raise MapError("discovery claim is not closed: " + key)
    for key in (
        "neural_howling_execution",
        "physical_loop_execution",
        "measured_physical_gain_before_feedback",
        "labelled_heldout_howl_benchmark",
        "device_timing_or_drift",
        "human_validation_result",
        "listening_result",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "release_claim",
    ):
        if report["evidence_classes"][key] is not False:
            raise MapError("unsupported evidence class is open: " + key)
    if report["evidence_classes"]["local_classical_howling_control_execution"] is not True:
        raise MapError("local classical execution is not recorded")
    if report["evidence_classes"]["local_ml_adjacent_baseline_execution"] is not True:
        raise MapError("local ML-adjacent execution is not recorded")
    if BOARD_PATH in report["source_pins"]:
        raise MapError("mutable board file is pinned")
    if BOARD_PATH in report["boundary_pins"]:
        raise MapError("mutable board file is pinned as boundary")
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
