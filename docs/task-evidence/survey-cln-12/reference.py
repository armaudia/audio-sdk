# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-12.

This module builds a bounded taxonomy/comparison evidence map for the
near-end listening / intelligibility-enhancement category (inventory category
``CLN-12``, legacy family ``F09``). It reads only pinned, read-only documents
from the enclosing ``audioml`` workspace and the SDK worktree. It does not load
audio, maskers, weights, runtimes, media or the network, and it does not
register, expose, enable or qualify any processor.

All curated records below are documentation mappings, not new measurements.
Historical local or source-reported values are transcribed verbatim from the
pinned documents and labelled with their original scope.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-CLN-12"
TITLE = "Review coverage for Near-end listening / intelligibility enhancement"
CATEGORY_ID = "CLN-12"
LEGACY_FAMILY = "F09"
BRANCH = "swarm/SDK-SURVEY-CLN-12"
BASE_COMMIT = "c0be8f341cb14cf1ad7f93d4a171543b2f99a6e4"
PROFILE = "DSP"
COMPONENT = "near-end-listening-intelligibility-evidence-map"
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
    "reports/listening-intelligibility/20261028-objective-screen.json": "f9a41f8e63a0ee4b4690e94792694d80d986cf881eee1fb9d958b579d67f967e",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/omissions_review.md": "9a62fbce90afe84b9d0a9d248f5b72a9b168783533d5cfd8fa3d82d2dea01147",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/level_tone_control_20261028.md": "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
    "research/listening_intelligibility_20261028.md": "f29de5cdb58676b6f61ac8489ff5af44a88b2125c2022920436a6f064405992a",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/agent-drc-noisy-dns/REPORT.md": "b134970b687ca22f90deb50b5d3dcb175580f90607d6b130f41e03e495ee2b43",
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
    "docs/task-evidence/ab-blind-listening-and-mushra-style-design/README.md": "3652b07cb7bee17ffcd2b21d37b3505c4cdaebe42119f0b79e2c738bfcbcb0c9",
    "docs/task-evidence/ebu-r128-ffmpeg-loudnorm/README.md": "04c3100ce7aa392b74c7d11cde3fdc9910f24a78a9afee1d8fc17e3e3e9b2f8b",
    "docs/task-evidence/envelope-agc/README.md": "66499930d48784005a026ed2b67e57d05c02b5c9b4917bdf73cabfec2c9bc62b",
    "docs/task-evidence/feed-forward-compressor/README.md": "ce7770db630a3c6863e9362d45de2b0c733bb1ceeed366d410084e659f9ee241",
    "docs/task-evidence/feed-forward-compressor/report.json": "72841527b1736e09cd96fd2e3d8efd609e4e2f9a75bb2f4e5b8e417a67343eb9",
    "docs/task-evidence/fixed-six-band-spectral-tilt/README.md": "70b2edcd154821445a5ff24f430b19fc42dac3cec8273a9baae896e3245f56de",
    "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json": "2673433a9db9ac348d3624b73a739196815374ccb68aa4427aee53b94702826c",
    "docs/task-evidence/full-band-receive-drc/README.md": "16caec5cecb021b193505d6017dce9e73368c5db9d2a18de3c3822362189d167",
    "docs/task-evidence/full-band-receive-drc/report.json": "9a685e1868e8290aa99131d810aa919df5c64712f3eebba40ab754788624d3f9",
    "docs/task-evidence/static-target-gain-with-peak-ceiling/README.md": "692acca143160e9506cde6e40a0b692c2f400751f79734b8a8cbeb1410bd47d8",
    "docs/task-evidence/stoi-estoi/README.md": "a09db6355c4c54046322b194fea71697aac76c0d111fa5aeca193ead367dee72",
    "docs/task-evidence/stoi-estoi/report.json": "a74820ff3e42f80d5ab06038de6ec70989876c6d91b98b34dc059ed2a6858f82",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Acoustic cleanup and spatial processing",
    "name": "Near-end listening / intelligibility enhancement",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Adjust received speech to counter acoustic masking around the listener.",
    "method_families": {
        "classic": "Spectral energy redistribution; intelligibility-index optimization; adaptive dynamic-range compression",
        "ml": "ML/hybrid family search remains open; no family verified in this pass",
    },
    "input_output": "Received speech + optional local-noise estimate \u2192 speech adapted for listening conditions",
    "live_or_comparison_boundary": (
        "Different from capture denoising or simple gain. Compare intelligibility/listening "
        "effort under an output-power constraint; noise sensing is method-specific."
    ),
    "source_ids": ["S54", "S55", "S56"],
    "related_category_ids": ["CLN-01", "CLN-09", "CLN-10", "OBS-01"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "CLN",
    "meaning": "Acoustic cleanup and spatial processing",
    "category_id": CATEGORY_ID,
    "near_end_listening_only": True,
    "not_capture_denoising_category": "CLN-01",
    "not_gain_loudness_or_drc_category": "CLN-09",
    "not_tonal_correction_category": "CLN-10",
    "not_assessment_category": "OBS-01",
    "near_end_adaptation_is_not_capture_denoising": True,
    "near_end_adaptation_is_not_simple_gain": True,
    "output_power_constraint_is_material": True,
    "listener_side_noise_sensing_is_method_specific": True,
    "note": (
        "Capture denoising is CLN-01, gain/loudness/dynamic-range control is "
        "CLN-09, tonal correction is CLN-10 and assessment is OBS-01. Those rows "
        "are named only as boundaries; their results are not pooled into a "
        "CLN-12 near-end-listening claim."
    ),
}

NELE_BOUNDARY: Dict[str, Any] = {
    "modifies_received_speech_before_playback": True,
    "requires_listener_side_masking_or_noise_estimate": True,
    "output_power_constraint_is_material": True,
    "capture_denoising_is_not_nele": True,
    "simple_gain_is_not_nele": True,
    "tonal_correction_is_not_nele": True,
    "human_listening_result_present": False,
    "listening_effort_or_hearing_profile_present": False,
    "independent_heldout_benchmark_present": False,
    "intelligibility_benefit_established": False,
    "published_method_reproduction_present": False,
    "ml_family_verified": False,
    "category_specific_weights_present": False,
    "listener_panel_present": False,
    "target_device_timing_present": False,
    "output_power_constraint_protocol_present": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S54",
        "title": "Near-end listening enhancement analysis",
        "url": "https://www.isca-archive.org/interspeech_2025/villani25_interspeech.html",
        "access_scope": "direct abstract",
        "mapped_components": [
            "optfractasii-approximation",
            "noise-aware-shaping-plus-drc",
            "fixed-six-band-spectral-tilt",
        ],
        "gap_ids": ["G01", "G03", "G04"],
        "finding": (
            "The catalogued source is a direct abstract for a near-end listening "
            "enhancement analysis, not a runnable candidate, pinned implementation, "
            "model weights or listener cohort. It motivates the local OptFractASII "
            "approximation and shaping/DRC screen, but the local report states that "
            "the published findings are not treated as an independent validation of "
            "the local approximation. No published code, checkpoint or listener "
            "panel is staged in this task."
        ),
    },
    {
        "source_id": "S55",
        "title": "Fraunhofer receiver-side intelligibility enhancement",
        "url": "https://www.idmt.fraunhofer.de/en/institute/projects-products/adaptdrc.html",
        "access_scope": "direct",
        "mapped_components": ["adaptdrc-ssdrc", "noise-aware-shaping-plus-drc"],
        "gap_ids": ["G04", "G05", "G09"],
        "finding": (
            "The catalogued source is a Fraunhofer project description of "
            "receiver-side intelligibility enhancement and AdaptDRC/SSDRC. The "
            "inventory records AdaptDRC/SSDRC as considered only; no source, "
            "binary, weights, runtime or configuration was obtained, and the local "
            "compressor is explicitly a small research baseline rather than "
            "AdaptDRC/SSDRC."
        ),
    },
    {
        "source_id": "S56",
        "title": "Author near-end enhancement software lead",
        "url": "https://sps.ewi.tudelft.nl/Repository/repitem.php?id=5&ti=2",
        "access_scope": "search excerpt; direct open timed out",
        "mapped_components": ["adaptdrc-ssdrc"],
        "gap_ids": ["G04", "G09"],
        "finding": (
            "The catalogued source is a search excerpt for an author near-end "
            "enhancement software page that advertised a MATLAB archive. The direct "
            "open timed out and the archive was not obtained in the omissions "
            "review; no runnable candidate is established by that claim. It is "
            "mapped only as an unresolved published-software lead adjacent to the "
            "AdaptDRC/SSDRC row, not as a local implementation."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Spectral energy redistribution via fixed or signal-dependent spectral tilt",
        "components": ["fixed-six-band-spectral-tilt", "optfractasii-approximation"],
        "gap_ids": ["G01", "G03", "G08"],
        "status": "historical_local_objective_screen_and_synthetic_masking_no_listener_result",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Intelligibility-index optimization and noise-aware water-filling (OptFractASII-style)",
        "components": ["optfractasii-approximation", "noise-aware-shaping-plus-drc"],
        "gap_ids": ["G03", "G04"],
        "status": "local_approximation_screened_published_method_not_reproduced",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Adaptive dynamic-range compression for receiver-side listening",
        "components": [
            "full-band-receive-drc-control",
            "feed-forward-compressor",
            "adaptdrc-ssdrc",
        ],
        "gap_ids": ["G04", "G05", "G08"],
        "status": "historical_local_synthetic_controls_and_considered_adaptdrc_no_adaptdrc_execution",
    },
    {
        "family_id": "MF-C4",
        "branch": "classic",
        "family": "Adjacent simple gain or loudness normalization boundary, not near-end listening enhancement",
        "components": [
            "static-target-gain-with-peak-ceiling",
            "envelope-agc",
            "ebu-r128-ffmpeg-loudnorm",
        ],
        "gap_ids": ["G08"],
        "status": "adjacent_boundary_only_not_nele_no_quality_claim",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Learned or hybrid near-end listening enhancement family search remains open",
        "components": [
            "se-agcnet",
            "self-supervised-neural-multiband-eq-and-dynamics",
            "differentiable-biquad-neural-parametric-eq",
        ],
        "gap_ids": ["G05"],
        "status": "catalogued_lead_only_no_verified_ml_family_no_local_execution",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "fixed-six-band-spectral-tilt", "evidence_status": "evaluated", "task": "SDK-FIXED-SIX-BAND-SPECTRAL-TILT"},
    {"component_id": "optfractasii-approximation", "evidence_status": "evaluated", "task": "SDK-OPTFRACTASII-APPROXIMATION"},
    {"component_id": "noise-aware-shaping-plus-drc", "evidence_status": "evaluated", "task": "SDK-NOISE-AWARE-SHAPING-PLUS-DRC"},
    {"component_id": "full-band-receive-drc-control", "evidence_status": "evaluated", "task": "SDK-FULL-BAND-RECEIVE-DRC-CONTROL"},
    {"component_id": "feed-forward-compressor", "evidence_status": "partial", "task": "SDK-FEED-FORWARD-COMPRESSOR"},
    {"component_id": "adaptdrc-ssdrc", "evidence_status": "considered", "task": "SDK-ADAPTDRC-SSDRC"},
    {"component_id": "stoi-estoi", "evidence_status": "evaluated", "task": "SDK-STOI-ESTOI"},
    {"component_id": "ears-preservation-screen-and-scorer-harness", "evidence_status": "evaluated", "task": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS"},
    {"component_id": "ab-blind-listening-and-mushra-style-design", "evidence_status": "partial", "task": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN"},
    {"component_id": "static-target-gain-with-peak-ceiling", "evidence_status": "evaluated", "task": "SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING"},
    {"component_id": "envelope-agc", "evidence_status": "partial", "task": "SDK-ENVELOPE-AGC"},
    {"component_id": "ebu-r128-ffmpeg-loudnorm", "evidence_status": "partial", "task": "SDK-EBU-R128-FFMPEG-LOUDNORM"},
    {"component_id": "se-agcnet", "evidence_status": "considered", "task": "SDK-SE-AGCNET"},
    {"component_id": "self-supervised-neural-multiband-eq-and-dynamics", "evidence_status": "considered", "task": "SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS"},
    {"component_id": "differentiable-biquad-neural-parametric-eq", "evidence_status": "considered", "task": "SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "Twelve deterministic EARS anechoic utterances paired with three locally staged VADToolkit ambient scenes at -5, 0 and +5 dB SNR, comparing identity, fixed six-band tilt, noise-aware OptFractASII approximation, shaping plus DRC and DRC alone",
        "class": "historical_local_objective_screen",
        "source_pin": "research/listening_intelligibility_20261028.md",
        "boundary": "108 pairs per method at 16 kHz with target speech RMS restored before mixing; STOI/ESTOI are objective predictors, not word recognition, listening effort or listener benefit; 12 utterance clusters and reused ambient scenes are not an independent cohort.",
    },
    {
        "id": "CI-2",
        "input": "Deterministic synthetic receiver-side masking fixture for fixed six-band tilt, identity, an energy-matched scalar gain and a deliberate +1 dB level-confound control",
        "class": "historical_local_synthetic_masking_control",
        "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json",
        "boundary": "Nine target/masker conditions at -5, 0 and +5 dB target-to-masker ratio; band-energy redistribution only, explicitly not STOI/ESTOI, intelligibility, MOS or listening benefit.",
    },
    {
        "id": "CI-3",
        "input": "Full-band receive DRC on analytic and seeded-noise speech-like signals across five input levels and three target-to-masker ratios",
        "class": "historical_local_synthetic_receive_drc_control",
        "source_pin": "docs/task-evidence/full-band-receive-drc/report.json",
        "boundary": "Synthetic level/masker control only; excluded from qualification; no real speech, listeners, STOI/ESTOI, target-device timing or release claim.",
    },
    {
        "id": "CI-4",
        "input": "Feed-forward DRC on thirty paired noisy DNS2020 pilot clips under deterministic -9/+9 dB gain trajectories every 400 ms",
        "class": "historical_local_synthetic_gain_ramp_control",
        "source_pin": "research/voice-enhancement-20261101/agent-drc-noisy-dns/REPORT.md",
        "boundary": "Synthetic gain-ramp and noisy-speech engineering control; not a learned DRC, natural microphone test, speech-intelligibility result or listener study.",
    },
    {
        "id": "CI-5",
        "input": "Task-local STOI/ESTOI scorer cross-check on six paired synthetic target/masker items with steady and modulated maskers",
        "class": "historical_local_scorer_crosscheck",
        "source_pin": "docs/task-evidence/stoi-estoi/report.json",
        "boundary": "Scorer behavior on generated signals; not evidence of speech intelligibility, listening benefit, enhancement quality or processor superiority; no acceptance tolerance.",
    },
    {
        "id": "CI-6",
        "input": "Published near-end listening enhancement, OptFractASII, AdaptDRC/SSDRC and author-software claims",
        "class": "source_reported_only",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "No exact source archive, reversible build, checkpoint, revision, runtime, cohort or numeric parity was verified locally; S56 direct access timed out and no archive was obtained.",
    },
    {
        "id": "CI-7",
        "input": "Rights-qualified held-out near-end listening cohort with listener-side maskers, target speech, output-power constraint and listener hearing profiles",
        "class": "missing_no_local_cohort",
        "source_pin": "research/listening_intelligibility_20261028.md",
        "boundary": "Not present; the category remains catalogued with candidate census and benchmark not_started, and the local screen is a small reused screening set rather than a disjoint benchmark split.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "identity / pass-through", "role": "Exact baseline for every candidate; a NELE candidate must beat identity on a valid listener-side comparison without an output-power confound.", "source_pin": "research/listening_intelligibility_20261028.md"},
    {"id": "CT-2", "name": "target-speech RMS restoration before mixing", "role": "Partial output-power control: each candidate's speech RMS is restored to the unprocessed speech RMS before the masker is added; not a full output-power-constraint protocol.", "source_pin": "reports/listening-intelligibility/20261028-objective-screen.json"},
    {"id": "CT-3", "name": "energy-matched scalar gain and +1 dB level confound", "role": "Separates spectral redistribution from level; the deliberate level confound verifies that the fixture detects output-power changes.", "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json"},
    {"id": "CT-4", "name": "fixed six-band spectral tilt", "role": "Classic finalist in the local screen; aggregate-mean leader but its utterance-clustered ESTOI interval crosses zero.", "source_pin": "research/listening_intelligibility_20261028.md"},
    {"id": "CT-5", "name": "DRC alone and shaping plus DRC", "role": "Separates dynamic-range compression from spectral shaping; DRC alone has the only local interval above zero versus identity, but only 12 clusters and no listener benefit.", "source_pin": "reports/listening-intelligibility/20261028-objective-screen.json"},
    {"id": "CT-6", "name": "listener-side masker at -5, 0 and +5 dB SNR/TMR", "role": "Mixes the masker after target processing; keeps the near-end masking condition explicit and stratified.", "source_pin": "research/listening_intelligibility_20261028.md"},
    {"id": "CT-7", "name": "STOI/ESTOI predicted-score separation", "role": "Keeps objective predictors out of human listening, listening-effort and intelligibility-benefit claims.", "source_pin": "docs/task-evidence/stoi-estoi/README.md"},
    {"id": "CT-8", "name": "headroom, peak guard and nonfinite controls", "role": "Records unity-peak exceedances and numerical failure behavior; a headroom waiver is not a quality pass.", "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/README.md"},
    {"id": "CT-9", "name": "missing, invalid, short and nonfinite scorer controls", "role": "Missing or invalid items are blocked, not scored; no missing result may qualify a candidate.", "source_pin": "docs/task-evidence/stoi-estoi/report.json"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "Locally staged EARS anechoic speech subset (12 deterministic target utterances)",
        "class": "local_research_corpus",
        "status": "Not loaded by this survey; rights, speaker consent and redistribution terms remain unresolved; only 12 targets were used in the historical screen.",
        "source_pin": "research/listening_intelligibility_20261028.md",
    },
    {
        "asset": "Locally staged VADToolkit ambient scenes (park, bus_stop, construction_site)",
        "class": "local_research_corpus",
        "status": "GPLv3 recordings, reused across utterances and not a disjoint participant-level masker corpus; not redistributed and not loaded by this survey.",
        "source_pin": "research/listening_intelligibility_20261028.md",
    },
    {
        "asset": "Local NELE research code and deterministic runner (src/audioml_eval/nele.py, scripts/evaluate_nele.py, tests/test_nele.py)",
        "class": "local_research_code",
        "status": "Source-local research baseline only; not an SDK provider and not executed by this survey.",
        "source_pin": "research/listening_intelligibility_20261028.md",
    },
    {
        "asset": "Fixed six-band spectral tilt task-local provider, synthetic fixtures and receiver-side masking report",
        "class": "sdk_task_local_provider",
        "status": "Default OFF and unregistered; synthetic band-energy evidence only, no STOI/ESTOI or listening result.",
        "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/README.md",
    },
    {
        "asset": "Full-band receive DRC task-local synthetic reference and level/masker control",
        "class": "sdk_task_local_provider",
        "status": "Default OFF and unregistered; synthetic control excluded from qualification; not a NELE result.",
        "source_pin": "docs/task-evidence/full-band-receive-drc/README.md",
    },
    {
        "asset": "Feed-forward compressor DRC screen and paired noisy-DNS synthetic gain-ramp report",
        "class": "sdk_task_local_evidence",
        "status": "Engineering control only; no natural microphone, listener preference or speech-intelligibility result.",
        "source_pin": "research/voice-enhancement-20261101/agent-drc-noisy-dns/REPORT.md",
    },
    {
        "asset": "Task-local STOI/ESTOI scorer reference and cross-check vectors",
        "class": "sdk_task_local_scorer",
        "status": "Synthetic developer evidence; an objective predictor, not a listener study or NELE quality result.",
        "source_pin": "docs/task-evidence/stoi-estoi/README.md",
    },
    {
        "asset": "AdaptDRC/SSDRC and author near-end enhancement software",
        "class": "published_software_lead",
        "status": "No source archive, build, configuration, weights or runtime obtained; S56 direct access timed out; considered only.",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "SE-AGCNet, self-supervised neural multiband EQ/dynamics and differentiable-biquad parametric EQ",
        "class": "research_model_assets",
        "status": "Catalogued leads only; no exact code, checkpoint, weights, training data or runtime staged; no ML candidate executed.",
        "source_pin": "research/level_tone_control_20261028.md",
    },
    {
        "asset": "AB blind listening and MUSHRA-style design record",
        "class": "listening_design_only",
        "status": "Design and registration evidence only; no near-end listening panel, ratings or playback clearance for this category.",
        "source_pin": "docs/task-evidence/ab-blind-listening-and-mushra-style-design/README.md",
    },
    {
        "asset": "Rights-qualified listener-side masker and hearing-profile cohort",
        "class": "missing_no_local_cohort",
        "status": "Not present; the category remains catalogued with candidate census and benchmark not_started.",
        "source_pin": "audio_categories.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "CLN-12 local objective near-end listening screen on EARS targets and VADToolkit maskers",
        "outcome_class": "historical_local_objective_screen",
        "component_ids": [
            "fixed-six-band-spectral-tilt",
            "optfractasii-approximation",
            "noise-aware-shaping-plus-drc",
            "feed-forward-compressor",
        ],
        "source_pin": "research/listening_intelligibility_20261028.md",
        "values": {
            "utterances": 12,
            "maskers": 3,
            "snr_levels": 3,
            "pairs_per_method": 108,
            "methods": 5,
            "rows": 540,
            "identity_stoi": 0.6896785488310864,
            "identity_estoi": 0.5719274307725402,
            "fixed_tilt_stoi": 0.7005949639097403,
            "fixed_tilt_estoi": 0.5759644767419412,
            "fixed_tilt_delta_stoi": 0.01091641507865393,
            "fixed_tilt_delta_estoi": 0.004037045969401021,
            "fixed_tilt_delta_estoi_ci_low": -0.00477282414373955,
            "fixed_tilt_delta_estoi_ci_high": 0.01262824906938469,
            "noise_aware_optfract_stoi": 0.687611450065672,
            "noise_aware_optfract_estoi": 0.562735806601076,
            "noise_aware_optfract_delta_estoi": -0.00919162417146413,
            "noise_aware_optfract_delta_estoi_ci_low": -0.015654145029942664,
            "noise_aware_optfract_delta_estoi_ci_high": -0.0023348321712812906,
            "noise_aware_plus_drc_stoi": 0.6898120029384116,
            "noise_aware_plus_drc_estoi": 0.5683308143600633,
            "noise_aware_plus_drc_delta_estoi": -0.003596616412476883,
            "noise_aware_plus_drc_delta_estoi_ci_low": -0.012945391038474413,
            "noise_aware_plus_drc_delta_estoi_ci_high": 0.00647392406357877,
            "drc_only_stoi": 0.6872879245337501,
            "drc_only_estoi": 0.575183494192491,
            "drc_only_delta_estoi": 0.003256063419950883,
            "drc_only_delta_estoi_ci_low": 0.00037583021328668287,
            "drc_only_delta_estoi_ci_high": 0.007178051544650001,
            "max_mean_absolute_speech_power_error_db": 8.0360622212773905e-16,
        },
        "scope": "Twelve deterministic EARS anechoic targets and three reused VADToolkit ambient scenes at 16 kHz and -5/0/+5 dB SNR; 108 pairs per method; target speech RMS restored before mixing; STOI/ESTOI are objective predictors, not word recognition, listening effort or listener benefit; 12 utterance clusters do not form an independent benchmark; not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Fixed six-band spectral tilt receiver-side masking fixture",
        "outcome_class": "historical_local_synthetic_masking_control",
        "component_ids": ["fixed-six-band-spectral-tilt"],
        "source_pin": "docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json",
        "values": {
            "conditions": 9,
            "methods": 4,
            "snr_db_min": -5,
            "snr_db_max": 5,
            "tilt_mean_high_band_delta_db": 0.122789,
            "tilt_mean_low_band_delta_db": -0.288839,
            "tilt_rms_ratio_mean": 1.000697,
            "energy_matched_mean_high_band_delta_db": 6.9e-05,
            "energy_matched_mean_low_band_delta_db": 0.003286,
            "energy_matched_rms_ratio_mean": 1.000697,
            "level_confound_mean_high_band_delta_db": 0.012627,
            "level_confound_mean_low_band_delta_db": 0.562822,
            "level_confound_rms_ratio_mean": 1.122018,
            "level_confound_control_db": 1.0,
        },
        "scope": "Nine synthetic target/masker conditions at -5, 0 and +5 dB target-to-masker ratio with the masker added after processing; band-energy redistribution only, not STOI/ESTOI, intelligibility, MOS or listening benefit; not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Full-band receive DRC synthetic level and masker control",
        "outcome_class": "historical_local_synthetic_receive_drc_control",
        "component_ids": ["full-band-receive-drc-control"],
        "source_pin": "docs/task-evidence/full-band-receive-drc/report.json",
        "values": {
            "conditions": 15,
            "level_count": 5,
            "tmr_count": 3,
            "input_level_dbfs_min": -30,
            "input_level_dbfs_max": 0,
            "rms_gain_db_at_minus12_dbfs": -4.10049,
            "peak_gain_db_at_minus12_dbfs": -5.941841,
            "correlation_at_minus12_dbfs": 0.972179,
            "rms_gain_db_at_0_dbfs": -11.932559,
            "peak_gain_db_at_0_dbfs": -10.534135,
            "output_peak_abs_at_0_dbfs": 0.95,
            "zero_content_delay_samples": 0,
        },
        "scope": "Five input levels and three target-to-masker ratios on analytic and seeded-noise speech-like signals; synthetic level/masker control excluded from qualification; no real speech, listeners, STOI/ESTOI or target-device timing; not rerun by this survey.",
    },
    {
        "id": "HE-4",
        "label": "Feed-forward DRC on paired noisy DNS speech under deterministic gain ramps",
        "outcome_class": "historical_local_synthetic_gain_ramp_control",
        "component_ids": ["feed-forward-compressor"],
        "source_pin": "research/voice-enhancement-20261101/agent-drc-noisy-dns/REPORT.md",
        "values": {
            "pairs": 30,
            "clip_seconds": 10,
            "sample_rate_hz": 16000,
            "identity_rms_error_400ms_db": 8.807,
            "static_gain_rms_error_400ms_db": 8.390,
            "envelope_agc_rms_error_400ms_db": 6.488,
            "drc_rms_error_400ms_db": 6.287,
            "identity_si_sdr_vs_noisy_db": 2.715,
            "drc_si_sdr_vs_noisy_db": 3.660,
            "drc_delta_si_sdr_vs_identity_db": 0.945,
            "drc_delta_rms_vs_identity_db": -2.519,
            "drc_delta_rms_vs_identity_ci_low_db": -2.823,
            "drc_delta_rms_vs_identity_ci_high_db": -2.229,
            "drc_delta_rms_vs_agc_db": -0.200,
            "drc_delta_rms_vs_agc_ci_low_db": -0.580,
            "drc_delta_rms_vs_agc_ci_high_db": 0.195,
            "drc_delta_si_sdr_vs_agc_db": 1.927,
            "drc_transform_rtf": 0.000534,
        },
        "scope": "Thirty paired noisy/clean DNS2020 pilot clips at 16 kHz with deterministic -9/+9 dB blocks every 400 ms; synthetic gain-ramp engineering control, not a learned DRC, natural microphone test or speech-intelligibility result; not rerun by this survey.",
    },
    {
        "id": "HE-5",
        "label": "DRC-only intelligibility screen and synthetic gain-law tracking",
        "outcome_class": "historical_local_synthetic_gain_law",
        "component_ids": ["feed-forward-compressor"],
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "values": {
            "gain_law_rmse_db": 2.613,
            "identity_gain_law_rmse_db": 5.795,
            "mean_transform_rtf": 0.000408,
        },
        "scope": "Existing DRC-only intelligibility screen plus synthetic gain-law tracking; synthetic controls only, no live speech preference, MOS, listener study or natural microphone acceptance; not rerun by this survey.",
    },
    {
        "id": "HE-6",
        "label": "STOI/ESTOI task-local scorer cross-check on paired synthetic maskers",
        "outcome_class": "historical_local_scorer_crosscheck",
        "component_ids": ["stoi-estoi"],
        "source_pin": "docs/task-evidence/stoi-estoi/report.json",
        "values": {
            "paired_items": 6,
            "sample_rate_hz": 16000,
            "samples_per_item": 9600,
            "masker_realizations": 2,
            "less_masker_delta_stoi": 0.147642,
            "less_masker_delta_estoi": 0.054286,
            "more_masker_delta_stoi": -0.082749,
            "more_masker_delta_estoi": -0.026072,
            "tilt_delta_stoi": 0.001623,
            "tilt_delta_estoi": 0.001005,
            "gain_only_delta_stoi": -0.022182,
            "gain_only_delta_estoi": -0.007044,
            "crosscheck_abs_delta_stoi": 2.1510571102112408e-15,
            "crosscheck_abs_delta_estoi": 1.0075273948473296e-14,
        },
        "scope": "Six paired synthetic target/masker items at 16 kHz with steady and modulated maskers; scorer behavior on generated signals, not evidence of speech intelligibility, listening benefit or enhancement quality; no acceptance tolerance; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "Villani et al. report that noise-dependent spectral redistribution can beat conventional spectral shaping in simulation and that adding DRC generally improves results",
        "class": "source_reported",
        "source_pin": "research/listening_intelligibility_20261028.md",
        "boundary": "Direct abstract and literature claim only; the local report explicitly does not treat it as independent validation of the local OptFractASII approximation and no published code or listener data is staged.",
    },
    {
        "id": "RO-2",
        "claim": "Fraunhofer describes receiver-side intelligibility enhancement with AdaptDRC/SSDRC",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Project description only; no source archive, build, weights, runtime, configuration or numeric parity was verified locally.",
    },
    {
        "id": "RO-3",
        "claim": "An author near-end enhancement software page advertised a MATLAB archive",
        "class": "source_reported",
        "source_pin": "research/category_survey/omissions_review.md",
        "boundary": "Search excerpt only; direct access timed out and the archive was not obtained, so no runnable candidate is established.",
    },
    {
        "id": "RO-4",
        "claim": "Fixed spectral tilt ranked first by aggregate mean STOI/ESTOI in the local screen, but the ESTOI interval versus identity crosses zero and no deployment candidate was selected",
        "class": "historical_local_reported",
        "source_pin": "research/listening_intelligibility_20261028.md",
        "boundary": "Small 108-pair objective screen on 12 EARS targets and three reused ambient scenes; objective predictors, not word recognition, listening effort or listener benefit; not rerun by this survey.",
    },
    {
        "id": "RO-5",
        "claim": "The local compressor is a small research baseline, not AdaptDRC/SSDRC; DRC-only synthetic tracking measured 2.613 dB RMSE versus 5.795 dB for identity",
        "class": "historical_local_reported",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Synthetic gain-law tracking only; no live speech preference, MOS, natural microphone acceptance or listener study; not a published-method reproduction.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "sweeps_steps_impulses": "HE-2/HE-3 synthetic sweeps, steps, impulses and silence; no NELE chain at a real playback boundary",
        "clean_speech": "HE-2 uses synthetic clean-speech-like signals; HE-1 used a local EARS subset but this survey does not load or redistribute it",
        "intelligibility_or_load_control": "HE-1 STOI/ESTOI objective screen and HE-6 scorer cross-check; no word recognition, listening effort or listener benefit",
        "gain_response_attack_release": "HE-2/HE-3/HE-4 measure gain, response, attack/release and headroom on synthetic controls",
        "headroom_peaks": "HE-2 records unity-peak exceedances and HE-3 enforces a peak guard; no limiter or release configuration is qualified",
        "delay": "HE-3 reports zero content delay on its synthetic grid; no target-device playback availability or deadline timing",
        "numerical_behavior": "HE-2/HE-3/HE-6 reject nonfinite or invalid items; no long-duration NELE chain nonfinite sweep",
        "state_transitions": "HE-3 exercises compressor/limiter state; no stateful NELE candidate was executed",
        "output_power_constraint": "HE-1 restores target-speech RMS before mixing and HE-2 has an energy-matched control; no full output-power-constraint protocol",
        "listening": "No near-end listening panel, listening-effort rating, hearing-profile result or playback clearance",
        "target_device": "No target-device content availability, memory, deadline, battery or thermal evidence",
    },
    "blocked": [
        "Rights-qualified held-out near-end listening cohort with listener-side maskers and target speech",
        "Independent authorized listening, listening-effort and hearing-profile evidence under an output-power constraint",
        "Validated intelligibility objective or scorer calibrated for near-end listening enhancement",
        "Pinned target-device playback availability, memory, deadline and latency evidence",
        "Faithful published NELE/AdaptDRC/SSDRC reproduction or task-matched external baseline under a locked runtime",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval",
        "Release approval at an exact approved reference revision and settings",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "local_objective_screen_historical_local": True,
    "local_synthetic_masking_control": True,
    "local_synthetic_drc_control": True,
    "local_scorer_crosscheck": True,
    "source_reported_only": True,
    "human_listening_result": False,
    "listening_effort_or_hearing_profile": False,
    "independent_heldout_benchmark": False,
    "intelligibility_benefit": False,
    "published_method_reproduction": False,
    "ml_local_execution": False,
    "target_device_timing": False,
    "output_power_constraint_full_protocol": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Acquire a rights-qualified, held-out near-end listening cohort with target speech, listener-side maskers, output-power constraint and listener metadata",
        "evidence_gap": "The only local screen uses 12 EARS targets and three reused VADToolkit ambient scenes; it is a small screening set, not a disjoint benchmark split, and rights remain unresolved.",
        "follow_up_ids": [
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-12 cohort feasibility row exists; the linked preservation and foundation rows own evidence/scorer rules and asset boundaries, not a near-end listening cohort.",
    },
    {
        "id": "G02",
        "actionable_gap": "Establish independent authorized listening, listening effort and hearing-profile evidence under a declared output-power constraint",
        "evidence_gap": "No subjective listener study, listening-effort measure or hearing-profile result exists; the local screen and AEC-style listening design are not a near-end listening panel.",
        "follow_up_ids": [
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
            "SDK-STOI-ESTOI",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-12 listening feasibility row exists; the linked rows own listening design and objective scorer evidence, not a listener result.",
    },
    {
        "id": "G03",
        "actionable_gap": "Validate an intelligibility objective or scorer for near-end listening enhancement against listener outcomes and a held-out cohort",
        "evidence_gap": "STOI/ESTOI are objective predictors; the local screen has only 12 utterance clusters and no word recognition, listening effort or calibrated near-end interpretation.",
        "follow_up_ids": [
            "SDK-STOI-ESTOI",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-12 objective-validation row exists; the linked scorer and foundation rows own scorer evidence and acceptance rules, not a validated NELE objective.",
    },
    {
        "id": "G04",
        "actionable_gap": "Reproduce a published NELE, OptFractASII or AdaptDRC/SSDRC method faithfully with exact source, configuration, revision and runtime",
        "evidence_gap": "The local OptFractASII candidate is deliberately an approximation, and the local compressor is explicitly not AdaptDRC/SSDRC; no published archive, build or runtime was obtained.",
        "follow_up_ids": [
            "SDK-OPTFRACTASII-APPROXIMATION",
            "SDK-ADAPTDRC-SSDRC",
            "SDK-NOISE-AWARE-SHAPING-PLUS-DRC",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked research-control and feasibility rows are discovery leads only; none is a published-method reproduction or a NELE quality claim.",
    },
    {
        "id": "G05",
        "actionable_gap": "Acquire and pin a learned or hybrid NELE candidate with weights, training data, controlled train/test split and listener-profile-compatible objective",
        "evidence_gap": "The ML/hybrid family search remains open; SE-AGCNet, self-supervised neural multiband EQ/dynamics and differentiable-biquad parametric EQ are considered only, with no exact code, checkpoint, weights or runtime staged.",
        "follow_up_ids": [
            "SDK-SE-AGCNET",
            "SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS",
            "SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked ML feasibility rows are catalogued leads only; none is enabled, installed, executed or a learned NELE claim.",
    },
    {
        "id": "G06",
        "actionable_gap": "Measure target-device playback content availability, memory, deadline, latency, battery and thermal behavior for a near-end listening chain",
        "evidence_gap": "Only offline batch RTF values exist; no callback-path, playback availability, memory, deadline or device timing was measured for a NELE chain.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-12 timing feasibility row exists; the foundation rows own lifecycle, acceptance and timing evidence rules, not a playback implementation.",
    },
    {
        "id": "G07",
        "actionable_gap": "Secure rights-qualified EARS/VADToolkit audio, model weights, listener data and output-redistribution terms",
        "evidence_gap": "The ambient recordings are GPLv3, reused and not an independent participant-level corpus; EARS rights and any model-weight terms are unresolved, and nothing is redistributed.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-12 rights feasibility row exists; the linked foundation and preservation rows own public-boundary and rights-aware manifests, not a rights grant.",
    },
    {
        "id": "G08",
        "actionable_gap": "Declare and enforce an output-power/level-confound protocol with headroom, peak and gain constraints for every candidate",
        "evidence_gap": "The local screen restores target-speech RMS before mixing and the tilt fixture has an energy-matched control, but there is no full output-power-constraint protocol, limiter/release qualification or NELE gain boundary.",
        "follow_up_ids": [
            "SDK-OPTFRACTASII-APPROXIMATION",
            "SDK-NOISE-AWARE-SHAPING-PLUS-DRC",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-12 power-protocol feasibility row exists; the linked research-control and foundation rows own DSP ablations and evidence rules, not a category-wide output-power contract.",
    },
    {
        "id": "G09",
        "actionable_gap": "Establish an independent external NELE baseline and exact-head reference parity under a locked runtime",
        "evidence_gap": "Published claims and the AdaptDRC/SSDRC software lead are source-reported only; no external baseline, archive, configuration or numeric parity was verified locally.",
        "follow_up_ids": [
            "SDK-ADAPTDRC-SSDRC",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility and foundation rows are scoping leads only; no external baseline is reproduced, pinned or promoted by this map.",
    },
    {
        "id": "G10",
        "actionable_gap": "Complete opt-in provider intake, independent exact-head review and explicit default-selection approval before any exposure",
        "evidence_gap": "No provider registration, installed-v0/ABI/registry/default/shared-build/CI change, release approval or independent review was performed for this category.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-12 provider-intake row exists; the foundation rows own public intake and evidence review rules, not a provider or default decision.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-OPTFRACTASII-APPROXIMATION", "title": "OptFractASII approximation", "mode": "research-control"},
    {"task_id": "SDK-NOISE-AWARE-SHAPING-PLUS-DRC", "title": "Noise-aware shaping plus DRC", "mode": "research-control"},
    {"task_id": "SDK-ADAPTDRC-SSDRC", "title": "AdaptDRC / SSDRC", "mode": "feasibility"},
    {"task_id": "SDK-STOI-ESTOI", "title": "STOI / ESTOI", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-SE-AGCNET", "title": "SE-AGCNet", "mode": "feasibility"},
    {"task_id": "SDK-SELF-SUPERVISED-NEURAL-MULTIBAND-EQ-AND-DYNAMICS", "title": "Self-supervised neural multiband EQ and dynamics", "mode": "feasibility"},
    {"task_id": "SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ", "title": "Differentiable-biquad neural parametric EQ", "mode": "feasibility"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified held-out near-end listening cohort with target speech, listener-side maskers and declared output-power constraint"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent authorized listening, listening-effort and hearing-profile evidence for a declared near-end listening benefit"},
    {"id": "RG-03", "blocked": True, "requirement": "Validated intelligibility objective or scorer calibrated for near-end listening enhancement on a held-out cohort"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned target-device playback content availability, memory, deadline and latency evidence"},
    {"id": "RG-05", "blocked": True, "requirement": "Faithful published NELE/AdaptDRC/SSDRC reproduction or task-matched external baseline under a locked runtime"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-12 \u2014 Near-end listening / intelligibility enhancement** | Adjust received speech to counter acoustic masking around the listener.",
        "Different from capture denoising or simple gain. Compare intelligibility/listening effort under an output-power constraint; noise sensing is method-specific.",
    ],
    "research/category_survey/sources.md": [
        "| S54 | [Near-end listening enhancement analysis](https://www.isca-archive.org/interspeech_2025/villani25_interspeech.html) | omissions reviewer and root | direct abstract |",
        "| S55 | [Fraunhofer receiver-side intelligibility enhancement](https://www.idmt.fraunhofer.de/en/institute/projects-products/adaptdrc.html) | omissions reviewer and root | direct |",
        "| S56 | [Author near-end enhancement software lead](https://sps.ewi.tudelft.nl/Repository/repitem.php?id=5&ti=2) | omissions reviewer | search excerpt; direct open timed out |",
    ],
    "research/category_survey/omissions_review.md": [
        "Noise around the listener can mask received speech even when the remote recording is clean.",
        "No runnable candidate is established by that claim.",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| DSP | Use sweeps, steps, impulses, silence, clean speech and an intelligibility or load-specific control.",
    ],
    "research/listening_intelligibility_20261028.md": [
        "Fixed tilt is the top candidate **by aggregate mean** for both metrics, but its utterance-clustered paired-bootstrap ESTOI interval versus identity crosses zero",
        "There is no subjective listener study, listener hearing profile, listening-effort measure, or broad held-out benchmark.",
        "No ML candidate was evaluated.",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "Existing DRC-only intelligibility screen plus new synthetic gain-law tracking: RMSE 2.613 dB vs 5.795 identity",
    ],
    "reports/listening-intelligibility/20261028-objective-screen.json": [
        "This is an objective proxy screen (STOI/ESTOI), not a human listening test.",
    ],
    "research/voice-enhancement-20261101/agent-drc-noisy-dns/REPORT.md": [
        "Against envelope AGC, the level-error difference is inconclusive",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "Local causal reference implementation; synthetic gain-law RMSE 2.613 dB vs 5.795 dB for identity, batch RTF 0.000408. No live preference evaluation.",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/fixed-six-band-spectral-tilt/README.md": [
        "They are not STOI/ESTOI, intelligibility, MOS or listening-benefit scores",
    ],
    "docs/task-evidence/full-band-receive-drc/README.md": [
        "The near-end listening baseline is reproduced **only** as a SYNTHETIC,",
    ],
    "docs/task-evidence/stoi-estoi/README.md": [
        "not evidence of speech intelligibility",
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
    "historical_real_speech_transcribed_only": True,
    "historical_real_masker_transcribed_only": True,
    "real_speech": False,
    "real_corpus": False,
    "real_masker_audio": False,
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
    "nele_claim_without_listening_result": "rejected; state unchanged",
    "nele_claim_without_output_power_constraint": "rejected; state unchanged",
    "ml_nele_claim_without_weights": "rejected; state unchanged",
    "human_listening_claim_without_panel": "rejected; state unchanged",
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
        raise MapError("CLN-12 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-12 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F09 / CLN-12 is not unique")
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
            raise MapError("legacy backlog mismatch: F09/CLN-12/%s" % key)


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
    mapped.update(c for row in HISTORICAL_EXECUTIONS for c in row["component_ids"])
    missing = sorted(mapped - set(by_id))
    if missing:
        raise MapError("mapped component missing from inventory: " + ",".join(missing))
    outer = sorted(mapped - {row["component_id"] for row in COMPONENT_CENSUS})
    if outer:
        raise MapError("mapped component is not in the component census: " + ",".join(outer))


def _check_source_leads() -> None:
    known_gaps = {gap["id"] for gap in GAPS}
    known_components = {row["component_id"] for row in COMPONENT_CENSUS}
    for lead in SOURCE_LEADS:
        if not lead.get("mapped_components"):
            raise MapError("source lead has no mapped component: " + lead["source_id"])
        for component_id in lead["mapped_components"]:
            if component_id not in known_components:
                raise MapError("source lead maps an uncensused component: %s/%s" % (lead["source_id"], component_id))
        for gap_id in lead["gap_ids"]:
            if gap_id not in known_gaps:
                raise MapError("source lead links unknown gap: " + gap_id)


def _check_method_families() -> None:
    branches = {row["branch"] for row in METHOD_FAMILIES}
    if branches != {"classic", "ml"}:
        raise MapError("both catalogued branches are not covered")
    known_components = {row["component_id"] for row in COMPONENT_CENSUS}
    known_gaps = {gap["id"] for gap in GAPS}
    for family in METHOD_FAMILIES:
        if not family.get("components"):
            raise MapError("method family has no component: " + family["family_id"])
        if not set(family["components"]) <= known_components:
            raise MapError("method family maps an uncensused component: " + family["family_id"])
        if not set(family["gap_ids"]) <= known_gaps:
            raise MapError("method family links unknown gap: " + family["family_id"])
    adjacent = [row for row in METHOD_FAMILIES if row["family_id"] == "MF-C4"]
    if len(adjacent) != 1:
        raise MapError("adjacent non-NELE family is missing")
    if "adjacent" not in adjacent[0]["family"].lower() or "not near-end listening" not in adjacent[0]["family"].lower():
        raise MapError("simple-gain boundary family is not labelled adjacent and non-NELE")
    ml = [row for row in METHOD_FAMILIES if row["branch"] == "ml"]
    if len(ml) != 1 or "open" not in ml[0]["family"].lower():
        raise MapError("the catalogued ML family search is not represented as open")


def _check_historical_execution_components() -> None:
    known = {row["component_id"] for row in COMPONENT_CENSUS}
    seen = set()
    for row in HISTORICAL_EXECUTIONS:
        if row["id"] in seen:
            raise MapError("duplicate historical execution id: " + row["id"])
        seen.add(row["id"])
        ids = row.get("component_ids")
        if not ids:
            raise MapError("historical execution has no component link: " + row["id"])
        missing = sorted(set(ids) - known)
        if missing:
            raise MapError(
                "historical execution links an uncensused component: %s/%s"
                % (row["id"], ",".join(missing))
            )
        for value in row.get("values", {}).values():
            if isinstance(value, float) and not math.isfinite(value):
                raise MapError("nonfinite historical value: " + row["id"])


def _check_evidence_classes() -> None:
    outcome_classes = " ".join(row["outcome_class"] for row in HISTORICAL_EXECUTIONS).lower()
    comparison_classes = " ".join(row["class"] for row in COMPARISON_INPUTS).lower()
    ml_components = {
        "se-agcnet",
        "self-supervised-neural-multiband-eq-and-dynamics",
        "differentiable-biquad-neural-parametric-eq",
    }
    checks = {
        "local_objective_screen_historical_local": "objective_screen" in outcome_classes
        or "objective_screen" in comparison_classes,
        "local_synthetic_masking_control": "synthetic_masking" in outcome_classes
        or "synthetic_masking" in comparison_classes,
        "local_synthetic_drc_control": "synthetic_receive_drc" in outcome_classes
        or "synthetic_gain_ramp" in outcome_classes
        or "synthetic_gain_law" in outcome_classes,
        "local_scorer_crosscheck": "scorer_crosscheck" in outcome_classes
        or "scorer_crosscheck" in comparison_classes,
        "source_reported_only": any(row["class"] == "source_reported" for row in REPORTED_OUTCOMES),
        "human_listening_result": "listener_result" in outcome_classes
        or "human_listening" in outcome_classes,
        "listening_effort_or_hearing_profile": "listening_effort" in outcome_classes,
        "independent_heldout_benchmark": "heldout_benchmark" in outcome_classes
        or "heldout_benchmark" in comparison_classes,
        "intelligibility_benefit": "intelligibility_benefit" in outcome_classes
        or "listener_benefit" in outcome_classes,
        "published_method_reproduction": "published_method" in outcome_classes,
        "ml_local_execution": any(
            set(row.get("component_ids", ())) & ml_components for row in HISTORICAL_EXECUTIONS
        ),
        "target_device_timing": "device_timing" in outcome_classes,
        "output_power_constraint_full_protocol": "output_power_protocol" in outcome_classes,
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in (
        "human_listening_result",
        "listening_effort_or_hearing_profile",
        "independent_heldout_benchmark",
        "intelligibility_benefit",
        "published_method_reproduction",
        "ml_local_execution",
        "target_device_timing",
        "output_power_constraint_full_protocol",
    ):
        if EVIDENCE_CLASSES[key] is not False:
            raise MapError("claim is not backed by a mapped record: " + key)
    if EVIDENCE_CLASSES["new_execution_in_this_survey"] is not False:
        raise MapError("new-execution claim is not allowed")
    if EVIDENCE_CLASSES["parity_or_qualification_claim"] is not False:
        raise MapError("parity or qualification claim is not allowed")


def _check_controls_assets() -> None:
    pins = set(SOURCE_PINS) | set(WORKTREE_PINS)
    for row in CONTROLS + ASSETS + COMPARISON_INPUTS + REPORTED_OUTCOMES:
        if row["source_pin"] not in pins:
            raise MapError("row source pin is not pinned: " + row["source_pin"])
    for row in HISTORICAL_EXECUTIONS:
        if row["source_pin"] not in pins:
            raise MapError("historical execution source pin is not pinned: " + row["source_pin"])


def _check_discovery() -> None:
    census = {row["component_id"]: row for row in COMPONENT_CENSUS}
    for component_id in DISCOVERY["category_specific_component_ids"]:
        if component_id not in census:
            raise MapError("category-specific component is not censused: " + component_id)
    for component_id in DISCOVERY["learned_candidate_ids"]:
        row = census.get(component_id)
        if row is None or row["evidence_status"] != "considered":
            raise MapError("learned candidate is not a considered row: " + component_id)
    for key in (
        "weights_present",
        "runtime_present",
        "listener_panel_present",
        "heldout_benchmark_present",
        "published_method_archive_present",
    ):
        if DISCOVERY[key] is not False:
            raise MapError("discovery claim is not closed: " + key)


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
    return _board_projection(board)


DISCOVERY: Dict[str, Any] = {
    "category_specific_component_ids": [
        "fixed-six-band-spectral-tilt",
        "optfractasii-approximation",
        "noise-aware-shaping-plus-drc",
        "full-band-receive-drc-control",
        "feed-forward-compressor",
    ],
    "learned_candidate_ids": [
        "se-agcnet",
        "self-supervised-neural-multiband-eq-and-dynamics",
        "differentiable-biquad-neural-parametric-eq",
    ],
    "weights_present": False,
    "runtime_present": False,
    "listener_panel_present": False,
    "heldout_benchmark_present": False,
    "published_method_archive_present": False,
    "note": (
        "Classic category-specific components have local synthetic or objective "
        "screen evidence. The ML/hybrid family remains an open catalogued search: "
        "no learned NELE weights, runtime, listener panel, held-out benchmark or "
        "published-method archive is staged, and no ML candidate was executed."
    ),
}


def _build_report(workspace: Optional[str] = None, sdk_root: Optional[str] = None) -> Dict[str, Any]:
    ws = find_workspace(workspace)
    sdk = find_sdk_root(sdk_root)
    _check_document_pins(ws, sdk)
    _check_anchors(ws, sdk)
    _check_taxonomy(ws)
    _check_backlog(ws)
    _check_component_census(ws)
    _check_source_leads()
    _check_method_families()
    _check_historical_execution_components()
    _check_evidence_classes()
    _check_controls_assets()
    _check_discovery()
    board_digest = _check_board(ws)

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
            "proposal_only": True,
        },
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "taxonomy": dict(CATEGORY_FACTS),
        "category_scope": dict(CATEGORY_SCOPE),
        "nele_boundary": dict(NELE_BOUNDARY),
        "discovery": dict(DISCOVERY),
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
    if report["qualification"]["status"] != QUALIFICATION_STATUS:
        raise MapError("qualification status changed")
    if report["qualification"]["decision"] != DECISION:
        raise MapError("qualification decision changed")
    if report["qualification"]["qualifies"] is not False:
        raise MapError("qualification is claimed")
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count changed")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in report["boundary"].values()):
        raise MapError("boundary is not closed")
    for key in (
        "human_listening_result_present",
        "listening_effort_or_hearing_profile_present",
        "independent_heldout_benchmark_present",
        "intelligibility_benefit_established",
        "published_method_reproduction_present",
        "ml_family_verified",
        "category_specific_weights_present",
        "listener_panel_present",
        "target_device_timing_present",
        "output_power_constraint_protocol_present",
    ):
        if report["nele_boundary"][key] is not False:
            raise MapError("NELE boundary claim is not closed: " + key)
    if report["discovery"]["weights_present"] is not False:
        raise MapError("category-specific weights are claimed")
    if report["discovery"]["runtime_present"] is not False:
        raise MapError("category-specific runtime is claimed")
    if report["discovery"]["listener_panel_present"] is not False:
        raise MapError("listener panel is claimed")
    if report["discovery"]["heldout_benchmark_present"] is not False:
        raise MapError("held-out benchmark is claimed")
    if report["discovery"]["published_method_archive_present"] is not False:
        raise MapError("published method archive is claimed")
    if EVIDENCE_CLASSES["human_listening_result"] is not False:
        raise MapError("a human listening result is claimed")
    if EVIDENCE_CLASSES["intelligibility_benefit"] is not False:
        raise MapError("an intelligibility benefit is claimed")
    if EVIDENCE_CLASSES["ml_local_execution"] is not False:
        raise MapError("an ML NELE execution is claimed")
    if EVIDENCE_CLASSES["independent_heldout_benchmark"] is not False:
        raise MapError("an independent held-out benchmark is claimed")
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
