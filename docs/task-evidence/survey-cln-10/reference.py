# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-10.

This module builds a bounded taxonomy/comparison evidence map for the tonal
correction and interference-filtering category (inventory category ``CLN-10``).
It reads only pinned, read-only documents from the enclosing ``audioml``
workspace and the SDK worktree. It does not load audio, weights, runtimes,
media or the network, and it does not register, expose, enable or qualify any
processor.

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
TASK = "SDK-SURVEY-CLN-10"
TITLE = "Review coverage for Tonal correction and interference filtering"
CATEGORY_ID = "CLN-10"
LEGACY_FAMILY = "F08"
BRANCH = "swarm/SDK-SURVEY-CLN-10"
BASE_COMMIT = "d5b11912cd09e87296cd9d4654f1917c9cb94258"
PROFILE = "DSP"
COMPONENT = "tonal-correction-evidence-map"
STATUS = "proposal_only_survey_incomplete"
QUALIFICATION_STATUS = "not_qualified"
READINESS = "incomplete"
DECISION = "DEFER"
TASK_DEPENDENCIES = ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"]

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
    "cpp-library/PIPELINE_DESIGN_REPORT.md": "f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093",
    "reports/level-tone/20261028-synthetic-evaluation.json": "1054a0b6d22dac695e17dfa84ab21f9f2a1677838285fb746834010424b91c34",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/distortion_restoration_20261028.md": "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "research/level_tone_control_20261028.md": "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
    "research/listening_intelligibility_20261028.md": "f29de5cdb58676b6f61ac8489ff5af44a88b2125c2022920436a6f064405992a",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
}

# SDK-worktree-relative public-boundary and evidence pins. They are read only
# to prove that no public surface was touched and to ground curated values; no
# header, report or component is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "core/providers/highpass/highpass_provider.c": "051b423d078835ff1ab23d7303c8e0c8f876d3d4211339682f366797ef7fffef",
    "docs/task-evidence/de-esser/README.md": "5de172557677f79d97852ea127f2bb10a1968331da8b8922c070500fd5ff6090",
    "docs/task-evidence/de-esser/report.json": "66f5a0d1a0778ec771842162aa38635cd96cbfd8a77b8ad24313304aff67b297",
    "docs/task-evidence/fixed-six-band-spectral-tilt/README.md": "70b2edcd154821445a5ff24f430b19fc42dac3cec8273a9baae896e3245f56de",
    "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json": "2673433a9db9ac348d3624b73a739196815374ccb68aa4427aee53b94702826c",
    "docs/task-evidence/learned-inverse-eq/README.md": "719910254b5399b79e20208cff40ff6920fe12b77813731b70c0c6abd833b20e",
    "docs/task-evidence/learned-inverse-eq/report.json": "2ee8271a3b08c989fe037f2753d013b8e6dcafb6881e5b0e59bb6724eff9e0dc",
    "docs/task-evidence/narrow-biquad-notch/README.md": "188d9bb3ec63ea1904701e00ff156967ec8fba9b58019a247cd5fb6b56f03015",
    "docs/task-evidence/narrow-biquad-notch/report.json": "c80db3087434ed0e8d5755b037e052ff3dfa5ae03d582f858ba76526253e99dd",
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
    "name": "Tonal correction and interference filtering",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Correct coloration, hum, rumble and unwanted DC.",
    "method_families": {
        "classic": "High-pass/notch filters; biquad/FIR equalization",
        "ml": "Adaptive/learned correction is an open family search",
    },
    "input_output": "Audio, optional calibration \u2192 filtered waveform",
    "live_or_comparison_boundary": (
        "Keep frequency-response correction separate from generating absent "
        "bandwidth. Boosts and filtering can alter speech."
    ),
    "source_ids": ["S19", "S46"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "CLN",
    "meaning": "Acoustic cleanup and spatial processing",
    "category_id": CATEGORY_ID,
    "tonal_correction_only": True,
    "not_background_noise_suppression_category": "CLN-01",
    "not_transient_click_repair_category": "CLN-02",
    "not_wind_or_microphone_disturbance_category": "CLN-03",
    "not_level_or_loudness_control_category": "CLN-09",
    "not_feedback_or_howling_category": "CLN-11",
    "not_bandwidth_extension_category": "RST-02",
    "not_codec_artifact_restoration_category": "RST-03",
    "note": (
        "Broadband noise suppression, transient click repair, wind handling, "
        "level/dynamics control, feedback notch control, bandwidth extension "
        "and codec-artifact restoration are separate catalogued categories. "
        "They are named only to prevent scope inflation; their results are not "
        "pooled into a CLN-10 tonal-correction claim."
    ),
}

TONAL_BOUNDARY: Dict[str, Any] = {
    "frequency_response_correction_is_not_bandwidth_generation": True,
    "boosts_and_filtering_can_alter_speech": True,
    "hum_rumble_and_dc_are_not_broadband_noise": True,
    "response_accuracy_is_separate_from_speech_preservation": True,
    "adaptive_feedback_notch_belongs_to_cln_11": True,
    "level_and_dynamics_belong_to_cln_09": True,
    "real_speech_or_device_response_staged": False,
    "independent_licensed_speech_cohort_staged": False,
    "neural_eq_weights_staged": False,
    "real_device_response_calibration_measured": False,
    "human_listening_result": False,
    "device_timing_measured": False,
    "bandwidth_extension_claim": False,
    "release_qualified": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S19",
        "title": "FFmpeg audio filters",
        "url": "https://ffmpeg.org/ffmpeg-filters.html",
        "access_scope": "direct",
        "mapped_components": [
            "sdk-high-pass-80-hz",
            "narrow-biquad-notch",
            "fixed-six-band-spectral-tilt",
        ],
        "gap_ids": ["G01", "G02", "G03"],
        "finding": (
            "The catalogued source documents conventional high-pass, notch and "
            "parametric/equalizer filters. It is a reference document, not a "
            "local port, corpus or measured device response; the task-local "
            "filters do not reproduce FFmpeg filters or their standards."
        ),
    },
    {
        "source_id": "S46",
        "title": "Speech Signal Improvement challenge findings",
        "url": "https://www.microsoft.com/en-us/research/publication/icassp-2024-speech-signal-improvement-challenge-2/",
        "access_scope": "search excerpt",
        "mapped_components": [
            "learned-inverse-eq",
            "differentiable-biquad-neural-parametric-eq",
            "self-supervised-neural-multiband-eq-and-dynamics",
        ],
        "gap_ids": ["G04", "G05", "G06"],
        "finding": (
            "The catalogued source is a challenge-findings excerpt for learned "
            "speech improvement, not a pinned model, checkpoint, licence grant "
            "or local execution. The local ridge inverse-EQ reference is not "
            "the challenge model and establishes no natural spectral balance."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "High-pass filtering for rumble, mains-adjacent low frequency and unwanted DC",
        "components": ["sdk-high-pass-80-hz", "native-variable-cutoff-high-pass"],
        "gap_ids": ["G02", "G07"],
        "status": "installed_fixed_80hz_control_source_local_variable_cutoff_unbenchmarked",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Narrow-band notch and biquad tone removal for mains hum and narrow interference",
        "components": ["narrow-biquad-notch"],
        "gap_ids": ["G02", "G06"],
        "status": "synthetic_rbj_notch_executed_no_real_hum_or_listening_result",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Biquad/FIR spectral equalization and band-selective tilt or de-essing",
        "components": ["fixed-six-band-spectral-tilt", "de-esser"],
        "gap_ids": ["G03", "G06"],
        "status": "synthetic_tilt_and_split_band_de_esser_no_device_eq_or_natural_balance_target",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Learned static inverse-EQ or ridge tone correction from labelled perturbations (S46)",
        "components": ["learned-inverse-eq"],
        "gap_ids": ["G01", "G03", "G05"],
        "status": "frozen_synthetic_ridge_baseline_executed_no_real_model_or_heldout_real_split",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Neural parametric EQ with differentiable biquads (S46)",
        "components": ["differentiable-biquad-neural-parametric-eq"],
        "gap_ids": ["G03", "G04"],
        "status": "catalogued_only_no_source_checkpoint_runtime_or_execution",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Self-supervised neural multiband EQ and dynamics (adjacent CLN-09 boundary)",
        "components": ["self-supervised-neural-multiband-eq-and-dynamics"],
        "gap_ids": ["G05"],
        "status": "catalogued_only_adjacent_dynamics_boundary_not_pooled_with_cln10",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "sdk-high-pass-80-hz", "evidence_status": "integrated", "task": "SDK-SDK-HIGH-PASS-80-HZ"},
    {"component_id": "native-variable-cutoff-high-pass", "evidence_status": "source-local", "task": "PRO-NATIVE-VARIABLE-CUTOFF-HIGH-PASS"},
    {"component_id": "narrow-biquad-notch", "evidence_status": "partial", "task": "SDK-NARROW-BIQUAD-NOTCH"},
    {"component_id": "fixed-six-band-spectral-tilt", "evidence_status": "evaluated", "task": "SDK-FIXED-SIX-BAND-SPECTRAL-TILT"},
    {"component_id": "learned-inverse-eq", "evidence_status": "evaluated", "task": "SDK-LEARNED-INVERSE-EQ"},
    {"component_id": "de-esser", "evidence_status": "considered", "task": "SDK-DE-ESSER"},
    {"component_id": "differentiable-biquad-neural-parametric-eq", "evidence_status": "considered", "task": "SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ"},
    {"component_id": "self-supervised-neural-multiband-eq-and-dynamics", "evidence_status": "considered", "task": "SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS"},
    {"component_id": "noise-aware-shaping-plus-drc", "evidence_status": "evaluated", "task": "SDK-NOISE-AWARE-SHAPING-PLUS-DRC"},
    {"component_id": "law-codec-proxy-and-low-pass-postfilter", "evidence_status": "evaluated", "task": "SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER"},
    {"component_id": "spectrum-copy-bandwidth-extension", "evidence_status": "evaluated", "task": "SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION"},
    {"component_id": "speex-one-preprocessor-optimization", "evidence_status": "partial", "task": "SDK-SPEEX-ONE-PREPROCESSOR-OPTIMIZATION"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Installed 80 Hz high-pass synthetic tones from 20 Hz to 7.8 kHz, chirp, positive and negative steps, DC, silence, impulse and a speech-plus-rumble proxy",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/sdk-high-pass-80-hz/report.json",
        "boundary": "25 seeded scenarios and 128 checks against an analytic two-pole reference; no real speech, corpus, device, listening or alternate cutoff.",
    },
    {
        "id": "CI-2",
        "input": "RBJ notch synthetic grid: 78 frequencies around 100 Hz-4 kHz centers, four center/bandwidth pairs, impulse, chirp, level step, silence and a formant proxy",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/narrow-biquad-notch/report.json",
        "boundary": "Task-local biquad fixture and optional unregistered provider; no mains-hum tracking, real speech, corpus or listening result.",
    },
    {
        "id": "CI-3",
        "input": "Fixed six-band spectral tilt synthetic fixtures: two-tone sweeps, impulse, step, clean/masker/near-clip/pre-clipped stimuli and a tilt-tanh-tilt interaction",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json",
        "boundary": "Receiver-side band-energy redistribution only; not STOI/ESTOI, intelligibility, MOS, listening benefit or real device equalization.",
    },
    {
        "id": "CI-4",
        "input": "Frozen six-band inverse-EQ synthetic 16 kHz clean, perturbed, step, impulse, near-clip and deliberately clipped signals",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/learned-inverse-eq/report.json",
        "boundary": "Task-local frozen-coefficient replay with an unregistered Python adapter; no learned weights, real device response or speech-quality metric.",
    },
    {
        "id": "CI-5",
        "input": "240 one-second deterministic harmonic/formant-like signals at 16 kHz with six EQ control points at independent -8 to +8 dB gains, split 180 train / 60 held-out",
        "class": "historical_local_synthetic_holdout",
        "source_pin": "research/level_tone_control_20261028.md",
        "boundary": "Synthetic held-out split only; 60 clips are not an independent real-speech benchmark and the source study is not rerun here.",
    },
    {
        "id": "CI-6",
        "input": "De-esser synthetic harmonic/burst program, sibilance bursts and frequency/level sweeps, low-band step, mixed noise and near-clip inputs",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/de-esser/report.json",
        "boundary": "Synthetic split-band detector and task-local optional provider; no recorded speech, sibilance perception, corpus or listening panel.",
    },
    {
        "id": "CI-7",
        "input": "Rights-qualified real-speech cohort with known device/room coloration, calibrated response, hum, rumble, DC and clean references, split by speaker and session",
        "class": "missing_no_local_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Explicitly missing; the registry requires this correction be kept separate from generating absent bandwidth.",
    },
    {
        "id": "CI-8",
        "input": "FFmpeg documented high-pass, notch and parametric/equalizer filter references",
        "class": "source_only_conventional_reference",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation only; no FFmpeg build, filter invocation, parity test or corpus is staged in this task.",
    },
    {
        "id": "CI-9",
        "input": "ICASSP 2024 Speech Signal Improvement challenge findings for learned enhancement and correction",
        "class": "source_only_challenge_protocol",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Excerpt only; no challenge data, submission, model, checkpoint or scorer is staged.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "identity bypass", "role": "Unprocessed input is the matched control; a correction must be compared against it before any benefit is claimed.", "source_pin": "docs/task-evidence/learned-inverse-eq/report.json"},
    {"id": "CT-2", "name": "frozen analytic biquad response", "role": "High-pass and notch outputs are compared against an analytic double-precision reference waveform, not against themselves.", "source_pin": "docs/task-evidence/sdk-high-pass-80-hz/report.json"},
    {"id": "CT-3", "name": "energy-matched scalar-only gain", "role": "Equalizes output energy without spectral redistribution so a tilt result cannot pass as a level effect.", "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json"},
    {"id": "CT-4", "name": "deliberate level confound", "role": "A +1 dB unmatched scalar control must be detected as a confound, not accepted as tonal correction.", "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json"},
    {"id": "CT-5", "name": "missing clean reference not scored", "role": "A missing reference is recorded as missing and cannot qualify the candidate.", "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json"},
    {"id": "CT-6", "name": "DC and rumble attenuation versus speech-band preservation", "role": "Low-frequency rejection and wanted-band preservation are reported as separate outcomes.", "source_pin": "docs/task-evidence/sdk-high-pass-80-hz/report.json"},
    {"id": "CT-7", "name": "near-clip and soft-clip interaction", "role": "Near-unity peaks, pre-clipped input and a tilt-tanh-tilt cascade expose headroom and nonlinear risk.", "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json"},
    {"id": "CT-8", "name": "ill-conditioned out-of-band amplification", "role": "Clustered probes and out-of-band noise amplification are reported as explicitly non-qualifying.", "source_pin": "docs/task-evidence/learned-inverse-eq/report.json"},
    {"id": "CT-9", "name": "matched-gain split-band versus broadband attenuation", "role": "The de-esser is compared with the same per-sample gains applied broadband so low-band preservation is visible.", "source_pin": "docs/task-evidence/de-esser/report.json"},
    {"id": "CT-10", "name": "synthetic and predicted-only separation", "role": "Synthetic fixtures and response measurements are labelled as such; no listening, real-speech or device claim is inherited.", "source_pin": "docs/task-evidence/de-esser/report.json"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Installed fixed 80 Hz high-pass provider source",
        "class": "sdk_installed_source",
        "status": "Read-only pin only; the installed provider, descriptor, registry and default behavior are unchanged",
        "source_pin": "core/providers/highpass/highpass_provider.c",
    },
    {
        "asset": "Task-local RBJ narrow-notch fixture and optional unregistered C provider",
        "class": "sdk_task_local_source",
        "status": "Opt-in only; never installed, registered by default or added to a catalog",
        "source_pin": "docs/task-evidence/narrow-biquad-notch/README.md",
    },
    {
        "asset": "Task-local fixed six-band spectral tilt fixtures and optional provider",
        "class": "sdk_task_local_source",
        "status": "Opt-in task-local consumer with AS_ENABLE_SIXBAND_PROVIDER=OFF by default; no assets required",
        "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/README.md",
    },
    {
        "asset": "Task-local frozen six-band inverse-EQ adapter and crosscheck vectors",
        "class": "sdk_task_local_source",
        "status": "Unregistered Python reference only; no learned weights, checkpoint or public API change",
        "source_pin": "docs/task-evidence/learned-inverse-eq/README.md",
    },
    {
        "asset": "Task-local de-esser synthetic fixtures and optional unregistered provider",
        "class": "sdk_task_local_source",
        "status": "Compiled only with task-local AS_ENABLE_DE_ESSER=ON; not linked into the installed library",
        "source_pin": "docs/task-evidence/de-esser/README.md",
    },
    {
        "asset": "Rights-qualified real speech, calibrated device/room response and neural EQ weights",
        "class": "missing_assets",
        "status": "Not staged; no corpus media, device measurement, checkpoint or weight file exists in this task",
        "source_pin": "research/level_tone_control_20261028.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "Installed 80 Hz high-pass control on synthetic tones, steps, DC and a rumble proxy",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["sdk-high-pass-80-hz"],
        "source_pin": "docs/task-evidence/sdk-high-pass-80-hz/report.json",
        "values": {
            "scenarios": 25,
            "checks_passed": 128,
            "checks_failed": 0,
            "tone_gain_20hz": 0.0625749764572181,
            "tone_gain_80hz": 0.7060655440441553,
            "tone_gain_1000hz": 0.9999798502757483,
            "cutoff_gain_80hz": 0.7071067811865868,
            "rumble_attenuation_db": 24.09884281011856,
            "rumble_speech_band_preservation": 0.018127391023017785,
            "dc_rejection": 1.942890289999999e-15,
            "content_delay_samples": 0,
            "nonfinite_count": 0,
        },
        "scope": "Installed dsp.highpass80.v0 at fixed 16 kHz mono float32, 160-sample frames; analytic two-pole reference and synthetic stimuli only; no real speech, corpus, listening, alternate cutoff, device loop or timing; not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Task-local RBJ narrow notch on a synthetic frequency grid",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["narrow-biquad-notch"],
        "source_pin": "docs/task-evidence/narrow-biquad-notch/report.json",
        "values": {
            "sweep_frequencies": 78,
            "max_sweep_gain_error_db": 0.006,
            "center_gain_1000hz_bw100": 0.00462,
            "skirt_gain_1500hz": 0.993461,
            "conditions": 16,
            "adverse_config_cases": 12,
            "clean_envelope_correlation": 0.999763,
            "clean_rms_delta_db": -0.056,
            "attack_frames": 0,
            "release_frames": 1,
        },
        "scope": "Task-local synthetic biquad fixture with an optional unregistered provider; injected width of 100 Hz at 1 kHz; no mains-hum tracking, recorded speech, listening or device result; not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Fixed six-band spectral tilt with receiver-side masking controls",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["fixed-six-band-spectral-tilt"],
        "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json",
        "values": {
            "bands": 6,
            "probes": 11,
            "max_abs_gain_error": 0.039834,
            "band0_measured_gain": 0.722494,
            "band5_measured_gain": 1.584844,
            "clean_max_relative_gain_error": 0.017855,
            "clean_rms_ratio": 1.001003,
            "output_max_abs_peak": 1.526155,
            "unity_peak_exceedances": 4,
            "nonlinear_cascade_final_headroom_db": -1.636717,
            "nonfinite_samples": 0,
        },
        "scope": "Task-local causal sqrt-Hann WOLA tilt at fixed 16 kHz mono float32 with seeded synthetic fixtures; receiver-side band-energy redistribution only, not STOI/ESTOI, MOS, listening or real device equalization; not rerun by this survey.",
    },
    {
        "id": "HE-4",
        "label": "Frozen six-band inverse-EQ reference on synthetic clean and perturbed signals",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["learned-inverse-eq"],
        "source_pin": "docs/task-evidence/learned-inverse-eq/report.json",
        "values": {
            "clean_learned_snr_db": 55.658313323,
            "clean_learned_max_abs_error": 0.000432263715,
            "clean_learned_gain_error_db": -0.012670658,
            "clean_identity_snr_db": 7.843217096,
            "clean_fixed_eq_snr_db": 3.268945596,
            "ill_conditioned_out_of_band_amplification_db": 8.833982678,
            "clean_headroom_db": 13.477123943,
            "nonfinite_count": 0,
        },
        "scope": "Task-local frozen-coefficient synthetic replay with an unregistered Python adapter; ill-conditioned out-of-band amplification is non-qualifying; no learned weights, real device response, speech cohort or listening; not rerun by this survey.",
    },
    {
        "id": "HE-5",
        "label": "Task-local split-band de-esser with matched broadband control",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["de-esser"],
        "source_pin": "docs/task-evidence/de-esser/report.json",
        "values": {
            "split_band_high_attenuation_db": 5.398077,
            "split_band_low_attenuation_db": 0.094067,
            "broadband_high_attenuation_db": 7.627361,
            "broadband_low_attenuation_db": 8.343217,
            "clean_envelope_correlation": 1.0,
            "boosted_peak": 1.944443311,
            "samples_above_full_scale": 20,
            "max_frame_to_frame_delta_db": 5.729657,
            "nonfinite_output_samples": 0,
        },
        "scope": "Task-local synthetic harmonic/burst program and optional unregistered provider; exact synthetic identity only, no recorded sibilance, intelligibility, listening, corpus or device result; not rerun by this survey.",
    },
    {
        "id": "HE-6",
        "label": "Historical synthetic ridge inverse-EQ screen",
        "outcome_class": "historical_local_synthetic_holdout",
        "component_ids": ["learned-inverse-eq"],
        "source_pin": "research/level_tone_control_20261028.md",
        "values": {
            "synthetic_clips": 240,
            "train_clips": 180,
            "heldout_clips": 60,
            "eq_control_points": 6,
            "eq_gain_min_db": -8.0,
            "eq_gain_max_db": 8.0,
            "identity_eq_rmse_db": 4.414,
            "learned_inverse_eq_rmse_db": 2.577,
        },
        "scope": "Historical local research screen on one-second synthetic harmonic/formant-like signals with a 180/60 split; content, room and speaker variation were not represented and the study is not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "S19 FFmpeg documents high-pass, notch and parametric/equalizer audio filters as conventional reference implementations",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation only; the repo baselines are not claimed to reproduce FFmpeg filters or any audio standard.",
    },
    {
        "id": "RO-2",
        "claim": "S46 reports the ICASSP 2024 Speech Signal Improvement challenge findings for learned enhancement",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Challenge excerpt only; no challenge audio, model, checkpoint, scorer or local execution is staged.",
    },
    {
        "id": "RO-3",
        "claim": "Neural parametric EQ matching with differentiable biquads predicts EQ parameters for a learned tone-control family",
        "class": "source_reported",
        "source_pin": "research/level_tone_control_20261028.md",
        "boundary": "Paper lead from the source study; no source, checkpoint, rights grant or local run.",
    },
    {
        "id": "RO-4",
        "claim": "A later neural multiband processor proposes self-supervised automatic EQ plus dynamics processing",
        "class": "source_reported",
        "source_pin": "research/level_tone_control_20261028.md",
        "boundary": "Paper lead only; no code, weights, revision or execution; dynamics belongs to CLN-09.",
    },
    {
        "id": "RO-5",
        "claim": "The candidate catalogue records local two-pole high-pass and biquad notch code with no dedicated quality or real-speech benchmark",
        "class": "source_reported",
        "source_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "boundary": "Catalogue finding only; the task-local synthetic fixtures are deterministic controls, not the missing benchmarks.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "identity_control": "CT-1 identity bypass plus the notebook CT-2 analytic filter reference",
        "matched_baseline": "CT-3 energy-matched scalar gain and CT-4 deliberate level confound; no real-speech task-matched baseline",
        "modality_split": "Tones, sweeps, steps, DC, silence, impulses, clean/masker/near-clip and nonlinear cascades stay separate",
        "paired_objective_scores": "HE-1..HE-6; transcribed and not rerun here",
        "clean_preservation": "CT-6 and HE-3/HE-5 synthetic preservation only; no real clean reference or listening",
        "peaks_and_invalid_outputs": "HE-3 near-clip peaks, HE-5 boost overshoot and adversarial rejection; no target-device headroom study",
        "spectral_response": "HE-1..HE-4 analytic or frozen response and gain error; no calibrated device or room response",
        "state_and_delay": "HE-1 zero content delay, HE-2 state rejection, HE-3 kernel delay; no device loop or clock drift",
        "listening": "No CLN-10 listening items, ratings, naturalness or playback clearance",
    },
    "blocked": [
        "Rights-qualified real-speech corpus with known device/room coloration, hum, rumble, DC and clean references",
        "Frozen held-out speaker/session split with an agreed desired-response definition and matched baseline",
        "Calibrated device/room response and bounded-boost EQ with headroom and peak limits",
        "Human listening and speech-preservation evidence under filtering, boosting and de-essing",
        "Runnable neural EQ source, checkpoint, licence and exact revision",
        "Measured target-device timing, CPU, memory, deadline and availability for the exact runtime",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "paired_synthetic_historical_local": True,
    "historical_local_synthetic_holdout": True,
    "learned_static_correction_execution": True,
    "source_reported_upstream_claim": True,
    "predicted_metric_not_human": False,
    "neural_reference_model_execution": False,
    "human_listening_result": False,
    "independent_heldout_benchmark": False,
    "clock_drift_or_device_timing": False,
    "device_loop_or_loudspeaker_measurement": False,
    "real_speech_result": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "release_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Acquire a rights-qualified real-speech cohort with known device/room coloration and clean references, split by speaker and session",
        "evidence_gap": "Only seeded synthetic fixtures and one synthetic 180/60 research split are reviewed; no real speech, device coloration, held-out real split or clean reference is staged.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-10 feasibility row was found for corpus acquisition; the existing research-control and foundation rows own manifests and scoring rules, not a recorded tonal-correction cohort.",
    },
    {
        "id": "G02",
        "actionable_gap": "Validate mains-hum tracking, alternate high-pass cutoffs, notch stability and DC/rumble behavior on recorded and calibrated signals",
        "evidence_gap": "The installed high-pass is fixed at 80 Hz and the notch is exercised on a synthetic grid only; no 50/60 Hz hum tracking, alternate cutoff or rumble/DC real-signal result exists.",
        "follow_up_ids": [
            "SDK-FND-EVIDENCE",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-10 feasibility row was found for hum/rumble/cutoff validation; the foundation rows own evidence and asset rules, not a measured filter study.",
    },
    {
        "id": "G03",
        "actionable_gap": "Define a desired-response and calibration for device/room coloration and measure bounded-boost equalization without generating absent bandwidth",
        "evidence_gap": "The tilt and inverse-EQ rows correct synthetic perturbations only; there is no calibrated device response, desired-response definition or bounded-boost real-signal result.",
        "follow_up_ids": [
            "SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ",
            "SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The differentiable-biquad feasibility row is a discovery lead for parametric response recovery; the bandwidth-extension row is a boundary control, not a tonal-correction result.",
    },
    {
        "id": "G04",
        "actionable_gap": "Verify and pin the S46 neural parametric EQ source, checkpoint, runtime and licence before any execution",
        "evidence_gap": "Differentiable-biquad neural parametric EQ is catalogued only; no source tree, checkpoint, weight file, licence or runtime is verified or staged.",
        "follow_up_ids": [
            "SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The feasibility row is a source/checkpoint verification lead only; it does not enable a processor or establish a tonal result.",
    },
    {
        "id": "G05",
        "actionable_gap": "Separate learned multiband tone correction from dynamics control and stage a runnable self-supervised neural EQ candidate",
        "evidence_gap": "Self-supervised neural multiband EQ and dynamics is catalogued only; no source, checkpoint or execution exists, and its dynamics half belongs to CLN-09.",
        "follow_up_ids": [
            "SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS",
            "SDK-NOISE-AWARE-SHAPING-PLUS-DRC",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The neural-EQ feasibility row is a discovery lead; the shaping-plus-DRC row supplies an adjacent CLN-09 ablation and is not pooled into a CLN-10 claim.",
    },
    {
        "id": "G06",
        "actionable_gap": "Measure real-speech preservation, naturalness and sibilance outcomes under filtering, boosting and de-essing with a consented listening protocol",
        "evidence_gap": "Synthetic envelope, band-preservation and peak controls exist, but no human ratings, naturalness result, sibilance perception or rights-cleared listening cohort exists.",
        "follow_up_ids": [
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-DE-ESSER",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The de-esser feasibility row is a synthetic prototype lead; the research-control row owns preservation scoring, not a listening result.",
    },
    {
        "id": "G07",
        "actionable_gap": "Measure target-device timing, CPU, memory, deadline and availability for the exact filter runtime",
        "evidence_gap": "Only single-stream fixture execution and analytic response are recorded; no paced device run, deadline, availability, memory or power measurement exists.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-10 timing feasibility row was found; the foundation rows own lifecycle and timing-evidence rules, not a measured runtime.",
    },
    {
        "id": "G08",
        "actionable_gap": "Clear rights for recorded speech, device/room measurements and neural EQ weights before any release evidence",
        "evidence_gap": "No recorded audio, device measurement, corpus manifest or weight licence is staged; participant and component rights remain unresolved.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-10 rights feasibility row was found; the foundation and research-control rows own asset boundaries, not a rights grant.",
    },
    {
        "id": "G09",
        "actionable_gap": "Keep bandwidth extension separate: never fill, copy or hallucinate absent bands under a tonal-correction label",
        "evidence_gap": "Bandwidth-extension research controls exist, but no CLN-10 evidence separates response correction from absent-band generation on the same signal.",
        "follow_up_ids": [
            "SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-10 feasibility row was found; the restoration research-control row is a boundary comparison only and its results are not pooled here.",
    },
    {
        "id": "G10",
        "actionable_gap": "Keep receiver codec low-pass postfiltering separate from tonal correction and do not pool restoration results",
        "evidence_gap": "The known 4/8-bit codec proxy and low-pass postfilter are restoration evidence, not a calibrated tonal response or a device-EQ correction.",
        "follow_up_ids": [
            "SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-10 feasibility row was found; the codec research-control row is an adjacent restoration boundary only.",
    },
    {
        "id": "G11",
        "actionable_gap": "Complete opt-in provider intake, registration/default selection and release approval for any tonal-correction processor",
        "evidence_gap": "Every reviewed provider is unregistered, optional and default-off; no provider intake, public default, independent approval or release decision exists.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-10 promotion feasibility row was found; the foundation rows own intake and evidence rules, not release approval.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-DE-ESSER", "title": "De-esser", "mode": "feasibility"},
    {"task_id": "SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ", "title": "Differentiable-biquad neural parametric EQ", "mode": "feasibility"},
    {"task_id": "SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS", "title": "Self-supervised neural multiband EQ and dynamics", "mode": "feasibility"},
    {"task_id": "SDK-NOISE-AWARE-SHAPING-PLUS-DRC", "title": "Noise-aware shaping plus DRC", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION", "title": "Spectrum-copy bandwidth extension", "mode": "research-control"},
    {"task_id": "SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER", "title": "\u00b5-law codec proxy and low-pass postfilter", "mode": "research-control"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified real-speech corpus with known device/room coloration, hum, rumble, DC and clean references"},
    {"id": "RG-02", "blocked": True, "requirement": "Frozen held-out speaker/session split, agreed desired-response definition and a matched baseline"},
    {"id": "RG-03", "blocked": True, "requirement": "Calibrated device/room response and bounded-boost equalization without generating absent bandwidth"},
    {"id": "RG-04", "blocked": True, "requirement": "Human listening and speech preservation under filtering, boosting and de-essing; synthetic response accuracy is insufficient"},
    {"id": "RG-05", "blocked": True, "requirement": "Runnable neural EQ source, checkpoint, licence and exact revision"},
    {"id": "RG-06", "blocked": True, "requirement": "Measured target-device timing, CPU, memory, deadline and availability evidence"},
    {"id": "RG-07", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-10 \u2014 Tonal correction and interference filtering** | Correct coloration, hum, rumble and unwanted DC. Scope: discovered_extension. | High-pass/notch filters; biquad/FIR equalization | Adaptive/learned correction is an open family search | Audio, optional calibration \u2192 filtered waveform | Keep frequency-response correction separate from generating absent bandwidth. Boosts and filtering can alter speech. | [S19](https://ffmpeg.org/ffmpeg-filters.html), [S46](https://www.microsoft.com/en-us/research/publication/icassp-2024-speech-signal-improvement-challenge-2/) |",
        "| **CLN-02 \u2014 Transient interference and click repair** |",
        "| **CLN-09 \u2014 Gain, loudness and dynamic-range control** |",
        "| **CLN-11 \u2014 Feedback and howling control** |",
    ],
    "research/category_survey/sources.md": [
        "| S19 | [FFmpeg audio filters](https://ffmpeg.org/ffmpeg-filters.html) | acoustics | direct |",
        "| S46 | [Speech Signal Improvement challenge findings](https://www.microsoft.com/en-us/research/publication/icassp-2024-speech-signal-improvement-challenge-2/) | root | search excerpt |",
    ],
    "research/level_tone_control_20261028.md": [
        "Two-pole high-pass and narrow notch filters for rumble/DC-adjacent content and mains hum.",
        "| Identity, EQ-response estimate | 4.414 dB RMSE |",
        "| Learned inverse-EQ estimate | 2.577 dB RMSE |",
        "The deterministic screen generated 240 one-second harmonic/formant-like signals at 16 kHz; 180 trained the ridge baselines and 60 were held out.",
        "The ML tone model corrects synthetic, known EQ perturbations.",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "| High-pass filter | Rumble/DC removal | Two-pole code exists locally; no dedicated quality benchmark. |",
        "| Narrow notch filter | Hum/tone removal | Biquad code exists locally; no dedicated real-speech benchmark. |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| DSP | Use sweeps, steps, impulses, silence, clean speech and an intelligibility or load-specific control.",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "core/providers/highpass/highpass_provider.c": [
        "const double q = 0.7071067811865476;",
    ],
    "docs/task-evidence/sdk-high-pass-80-hz/README.md": [
        "This directory is task-local evidence for the pinned installed provider",
        "The frozen source implements a two-pole 80 Hz high-pass with",
    ],
    "docs/task-evidence/narrow-biquad-notch/README.md": [
        "Task-local, model-free, synthetic-only DSP evidence for an explicitly configured",
    ],
    "docs/task-evidence/fixed-six-band-spectral-tilt/README.md": [
        "The receiver-side numbers are band-energy redistribution measurements only.",
    ],
    "docs/task-evidence/learned-inverse-eq/README.md": [
        "**Status: `proposal_only_not_qualified` / `incomplete`.**",
    ],
    "docs/task-evidence/de-esser/README.md": [
        "The reference is a causal split-band design. A second-order Butterworth",
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
    "real_device_response": False,
    "weights": False,
    "runtime_invocation": False,
    "listening": False,
    "device_timing": False,
    "bandwidth_extension": False,
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
    "response_claim_without_response_execution": "rejected; state unchanged",
    "real_speech_claim_without_staged_cohort": "rejected; state unchanged",
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
            root = None
            for candidate in [here.parent] + list(here.parents):
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
        raise MapError("CLN-10 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-10 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F08 / CLN-10 is not unique")
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
            raise MapError("legacy backlog mismatch: F08/CLN-10/%s" % key)


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
        if "not rerun by this survey" not in row.get("scope", ""):
            raise MapError("historical execution is not labelled not-rerun: " + row["id"])


def _check_evidence_classes() -> None:
    classes = {row["class"] for row in COMPARISON_INPUTS}
    checks = {
        "paired_synthetic_historical_local": "historical_local_paired_synthetic" in classes,
        "historical_local_synthetic_holdout": "historical_local_synthetic_holdout" in classes,
        "learned_static_correction_execution": any(
            row["outcome_class"] == "historical_local_synthetic_holdout"
            or "learned-inverse-eq" in row["component_ids"]
            for row in HISTORICAL_EXECUTIONS
        ),
        "source_reported_upstream_claim": any(row["class"] == "source_reported" for row in REPORTED_OUTCOMES),
        "predicted_metric_not_human": "historical_local_predicted_metric" in classes,
        "neural_reference_model_execution": any(
            row["outcome_class"] == "historical_local_neural_reference_model"
            for row in HISTORICAL_EXECUTIONS
        ),
        "human_listening_result": "human_listening_result" in classes,
        "independent_heldout_benchmark": "independent_heldout_benchmark" in classes,
        "clock_drift_or_device_timing": "device_clock_drift" in classes,
        "device_loop_or_loudspeaker_measurement": "device_loop" in classes,
        "real_speech_result": "real_speech_paired" in classes,
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in ("new_execution_in_this_survey", "parity_or_qualification_claim", "release_claim"):
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
        "dependencies": list(TASK_DEPENDENCIES),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "category_scope": dict(CATEGORY_SCOPE),
        "tonal_boundary": dict(TONAL_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "mapped_component_ids": [
                "sdk-high-pass-80-hz",
                "native-variable-cutoff-high-pass",
                "narrow-biquad-notch",
                "fixed-six-band-spectral-tilt",
                "learned-inverse-eq",
                "de-esser",
            ],
            "real_speech_cohort_present": False,
            "device_response_calibration_present": False,
            "neural_eq_weights_present": False,
            "independent_heldout_real_benchmark_present": False,
            "note": "Tonal-correction components are mapped, but no real-speech cohort, device response calibration, neural EQ weights or independent real held-out benchmark is staged; candidates remain partial, considered, source-local or integrated only.",
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
        "real_device_response",
        "weights",
        "runtime_invocation",
        "listening",
        "device_timing",
        "bandwidth_extension",
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
        "frequency_response_correction_is_not_bandwidth_generation",
        "boosts_and_filtering_can_alter_speech",
        "hum_rumble_and_dc_are_not_broadband_noise",
        "response_accuracy_is_separate_from_speech_preservation",
        "adaptive_feedback_notch_belongs_to_cln_11",
        "level_and_dynamics_belong_to_cln_09",
    ):
        if report["tonal_boundary"][key] is not True:
            raise MapError("tonal boundary rule is not enforced: " + key)
    for key in (
        "real_speech_or_device_response_staged",
        "independent_licensed_speech_cohort_staged",
        "neural_eq_weights_staged",
        "real_device_response_calibration_measured",
        "human_listening_result",
        "device_timing_measured",
        "bandwidth_extension_claim",
        "release_qualified",
    ):
        if report["tonal_boundary"][key] is not False:
            raise MapError("tonal boundary claim is not closed: " + key)
    for key in (
        "real_speech_cohort_present",
        "device_response_calibration_present",
        "neural_eq_weights_present",
        "independent_heldout_real_benchmark_present",
    ):
        if report["discovery"][key] is not False:
            raise MapError("discovery claim is not closed: " + key)
    if report["evidence_classes"]["independent_heldout_benchmark"] is not False:
        raise MapError("held-out benchmark is claimed without a test split")
    if report["evidence_classes"]["human_listening_result"] is not False:
        raise MapError("human listening is claimed without ratings")
    if report["evidence_classes"]["clock_drift_or_device_timing"] is not False:
        raise MapError("device timing is claimed without a device loop")
    if report["evidence_classes"]["real_speech_result"] is not False:
        raise MapError("real speech is claimed without a staged cohort")
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
