# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-CLN-05.

This module builds a bounded taxonomy/comparison evidence map for the
reference-based acoustic-echo-cancellation category (inventory category
``CLN-05``). It reads only pinned, read-only documents from the enclosing
``audioml`` workspace and the SDK worktree. It does not load audio, weights,
runtimes, media or the network, and it does not register, expose, enable or
qualify any processor.

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
TASK = "SDK-SURVEY-CLN-05"
TITLE = "Review coverage for Reference-based acoustic echo cancellation (AEC)"
CATEGORY_ID = "CLN-05"
LEGACY_FAMILY = "F04"
BRANCH = "swarm/SDK-SURVEY-CLN-05"
BASE_COMMIT = "6f58f3d721908806f8c4a0a1e0dc6de846cef54c"
PROFILE = "Room"
COMPONENT = "reference-based-aec-evidence-map"
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
    "adapters/dtln-aec/README.md": "d19deb34e849fdb19fa3bf942ccb285397252fb233e67ce23a41bc1eda0524c5",
    "adapters/localvqe-aec/README.md": "61240419dc9d46af2056316f2a7167b833fb80e9d6a4ce8470b94a8cde488cd1",
    "adapters/webrtc-aec/README.md": "c074f84c859dcfb2ac7414a775dbcddcf2f2646deca66810c9241fcf7adec050",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "reports/aec_challenge_real_pilot_summary_20261028.csv": "4784755161aa0fa4027b2b6524f8dd34b7ccc9390ecd785103dda95b65bb27e7",
    "reports/aec_challenge_synthetic_pilot_20261028.csv": "f5da248a22a632e7221464c03c2de25386e3c7091ca68c1644f18a34dec39ef5",
    "research/aec_challenge_real_pilot_manifest.json": "7fd467330537107873759cdab2b63e59ff0f77e9aca324f8249c7801b109079f",
    "research/aec_challenge_real_pilot_selection.csv": "840caee9487c1480cd9b68bd87a3b36233464e706759465d374372cd0ab19585",
    "research/aec_challenge_synthetic_pilot_manifest.json": "38b6bb4939a254d702d2ab12e95fde641957e1ced2b752eb9fb2dd8b215202b6",
    "research/aec_challenge_synthetic_pilot_selection.csv": "f3d69044e8040613fc31ba0e7438e790289a41f1ac2170582a09e38a0c1322a7",
    "research/aec_research_20261028.md": "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
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
    "docs/task-evidence/erle-and-double-talk-preservation/README.md": "0f8ddc78f41459734f4ed096eb71789ecf5bcc809d833c5b65f63319ef11db2e",
    "docs/task-evidence/erle-and-double-talk-preservation/report.json": "6860139e8c1a9f5c01fa219f81b6b8f5ee3f43160dd139d00e45cfb853d63b50",
    "docs/task-evidence/fixed-rls-to-nlms-aec/README.md": "0ada2d29857d1143fd8599b7317907e319644944922f12efbb1e84c4d365ec0f",
    "docs/task-evidence/fixed-rls-to-nlms-aec/report.json": "94cc863242f8b7b0320ae670cd24722ce197e6c588bfe8bb498bfa8ae0684fce",
    "docs/task-evidence/nlms-aec/README.md": "83084ed97c02e21764f9a41daa2184e23afc13d86466dd40e0dfb0fc670bb9e0",
    "docs/task-evidence/nlms-aec/report.json": "2910e9e986259a9de738822c35a2908e47a836a9daabc292118f6c7389988f6a",
    "docs/task-evidence/rls-aec/README.md": "b1d1f72ca9d4c10f16374434a5c55a95076ed69bc15518296f2f55a834e7c49b",
    "docs/task-evidence/rls-aec/report.json": "3fd2611c1b4619fab5858a78ee62920b66fd7acfb6aaac79b613dffd169e3b25",
    "docs/task-evidence/speex-mdf-residual-postfilter/README.md": "16c7643cc5550cd7358ee48f7dec62eb4045a3384364246cd357269ce0c28da9",
    "docs/task-evidence/speex-mdf-residual-postfilter/report.json": "ad15c446442058b82c003f15527637edae02a819a2033b0f289bc89042b170b6",
    "docs/task-evidence/speexdsp-mdf-reference/README.md": "3104b4c880eb6d99bbdff2bf9f73793d60278978442000a9c67f1f9c3ae64b83",
    "docs/task-evidence/speexdsp-mdf-reference/evidence/oracle.json": "c1e1c232cb80d344fe6a1131ebf80caf112cd68e2baad9a2543ee8ccc1e08411",
    "docs/task-evidence/webrtc-aec3/report.json": "da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283",
}

# The board file is referenced by path only. It is deliberately NOT pinned and
# never hashed into canonical bytes; only id/title/mode of linked rows form the
# stable gate projection in report.json.
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Acoustic cleanup and spatial processing",
    "name": "Reference-based acoustic echo cancellation (AEC)",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Remove loudspeaker playback leaking into the microphone.",
    "method_families": {
        "classic": "Adaptive FIR, NLMS, frequency-domain and Kalman filters",
        "ml": "Neural-assisted adaptation or reference-conditioned estimation",
    },
    "input_output": "Microphone + playback reference \u2192 near-end estimate",
    "live_or_comparison_boundary": (
        "Reference timing, double talk, drift and changing echo paths are part "
        "of the contract."
    ),
    "source_ids": ["S21", "S22"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "CLN",
    "meaning": "Acoustic cleanup and spatial processing",
    "category_id": CATEGORY_ID,
    "reference_based_aec_only": True,
    "not_residual_echo_suppression_category": "CLN-06",
    "not_feedback_or_howling_category": "CLN-11",
    "not_dereverberation_category": "CLN-04",
    "blind_one_input_suppression_is_not_reference_aec": True,
    "note": (
        "Residual echo suppression, feedback/howling control and "
        "dereverberation are separate catalogued categories. They are named "
        "only to prevent scope inflation; their results are not pooled into a "
        "CLN-05 reference-AEC claim."
    ),
}

AEC_BOUNDARY: Dict[str, Any] = {
    "explicit_playback_reference_required": True,
    "reference_timing_and_drift_in_contract": True,
    "double_talk_preservation_is_separate_from_echo_attenuation": True,
    "changing_echo_path_is_a_material_stratum": True,
    "blind_one_input_suppression_is_not_reference_aec": True,
    "residual_echo_suppression_belongs_to_cln_06": True,
    "real_webrtc_aec3_source_or_runtime_staged": False,
    "independent_licensed_dev_or_test_corpus_staged": False,
    "neural_reference_weights_staged": False,
    "device_clock_drift_or_loop_timing_measured": False,
    "human_listening_result": False,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S21",
        "title": "NKF acoustic echo cancellation implementation",
        "url": "https://github.com/fjiang9/NKF-AEC",
        "access_scope": "direct",
        "mapped_components": [
            "neural-kalman-filtering-nkf",
            "cagcrn-joint-aec-and-ns",
        ],
        "gap_ids": ["G04", "G06"],
        "finding": (
            "The catalogued source is a neural-Kalman-filtering AEC "
            "implementation lead, not a pinned checkpoint, runtime or licence "
            "grant. No source tree, weight file, reference-timing contract or "
            "evaluation audio is staged in this task; the candidate remains "
            "considered only."
        ),
    },
    {
        "source_id": "S22",
        "title": "Speex echo cancellation documentation",
        "url": "https://www.speex.org/docs/manual/speex-manual/node7.html",
        "access_scope": "search excerpt",
        "mapped_components": [
            "speexdsp-mdf-reference",
            "speex-mdf-residual-postfilter",
        ],
        "gap_ids": ["G05", "G07"],
        "finding": (
            "The catalogued source is API documentation for a "
            "frequency-domain MDF echo canceller with an explicit far-end "
            "reference and optional residual suppression. Documentation alone "
            "is not a local parity, corpus, double-talk, drift or device-timing "
            "result; the pinned vendored source is the only executed base."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Sample-domain adaptive FIR: NLMS, RLS and fixed RLS-to-NLMS hybrid",
        "components": ["nlms-aec", "rls-aec", "fixed-rls-to-nlms-aec"],
        "gap_ids": ["G01", "G07", "G10"],
        "status": "historical_local_synthetic_paired_only_no_recorded_cohort",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Frequency-domain partitioned-block adaptive filtering: MDF and PBFDAF/AUMDF",
        "components": ["speexdsp-mdf-reference", "pbfdaf-aumdf"],
        "gap_ids": ["G05", "G07"],
        "status": "mdf_reference_synthetic_executed_pbfdaf_considered_only",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Production AEC with delay estimation and optional residual attenuation",
        "components": ["webrtc-aec3", "speex-mdf-residual-postfilter"],
        "gap_ids": ["G02", "G07"],
        "status": "aec3_shaped_synthetic_reference_only_no_real_runtime_parity",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Neural-assisted adaptation or neural Kalman filtering (S21)",
        "components": ["neural-kalman-filtering-nkf"],
        "gap_ids": ["G04"],
        "status": "catalogued_only_no_source_checkpoint_runtime_or_execution",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Reference-conditioned streaming neural AEC and joint AEC plus noise suppression",
        "components": [
            "dtln-aec-128-256-512",
            "localvqe-compact-echo-only",
            "localvqe-compact-full",
            "cagcrn-joint-aec-and-ns",
            "deepaec",
            "dual-path-echo-net",
        ],
        "gap_ids": ["G03", "G06"],
        "status": "localvqe_historical_local_execution_dtln_blocked_others_considered_or_blocked",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Neural residual echo suppression attached to a canceller (adjacent CLN-06 boundary)",
        "components": ["dual-branch-residual-echo-suppressor"],
        "gap_ids": ["G06"],
        "status": "catalogued_only_adjacent_boundary_not_pooled_with_cln05",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "nlms-aec", "evidence_status": "evaluated", "task": "SDK-NLMS-AEC"},
    {"component_id": "rls-aec", "evidence_status": "partial", "task": "SDK-RLS-AEC"},
    {"component_id": "fixed-rls-to-nlms-aec", "evidence_status": "partial", "task": "SDK-FIXED-RLS-TO-NLMS-AEC"},
    {"component_id": "speexdsp-mdf-reference", "evidence_status": "evaluated", "task": "SDK-SPEEXDSP-MDF-REFERENCE"},
    {"component_id": "pbfdaf-aumdf", "evidence_status": "considered", "task": "SDK-PBFDAF-AUMDF"},
    {"component_id": "webrtc-aec3", "evidence_status": "evaluated", "task": "SDK-WEBRTC-AEC3"},
    {"component_id": "speex-mdf-residual-postfilter", "evidence_status": "evaluated", "task": "SDK-SPEEX-MDF-RESIDUAL-POSTFILTER"},
    {"component_id": "neural-kalman-filtering-nkf", "evidence_status": "considered", "task": "SDK-NEURAL-KALMAN-FILTERING-NKF"},
    {"component_id": "dtln-aec-128-256-512", "evidence_status": "blocked", "task": "SDK-DTLN-AEC-128-256-512"},
    {"component_id": "localvqe-compact-echo-only", "evidence_status": "evaluated", "task": "SDK-LOCALVQE-COMPACT-ECHO-ONLY"},
    {"component_id": "localvqe-compact-full", "evidence_status": "evaluated", "task": "SDK-LOCALVQE-COMPACT-FULL"},
    {"component_id": "cagcrn-joint-aec-and-ns", "evidence_status": "considered", "task": "SDK-CAGCRN-JOINT-AEC-AND-NS"},
    {"component_id": "deepaec", "evidence_status": "blocked", "task": "SDK-DEEPAEC"},
    {"component_id": "dual-path-echo-net", "evidence_status": "blocked", "task": "SDK-DUAL-PATH-ECHO-NET"},
    {"component_id": "dual-branch-residual-echo-suppressor", "evidence_status": "considered", "task": "SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR"},
    {"component_id": "aec-challenge-paired-render-capture-fixtures", "evidence_status": "evaluated", "task": "SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES"},
    {"component_id": "aecmos", "evidence_status": "evaluated", "task": "SDK-AECMOS"},
    {"component_id": "erle-and-double-talk-preservation", "evidence_status": "evaluated", "task": "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "51,200-sample 16 kHz paired synthetic fixture with sparse 96-tap echo path, delay change, delayed render and reference dropout",
        "class": "historical_local_paired_synthetic",
        "source_pin": "docs/task-evidence/nlms-aec/report.json",
        "boundary": "Seeded synthetic fixture only; no room, real speech, device loop, drift or listening result.",
    },
    {
        "id": "CI-2",
        "input": "Twelve AEC Challenge synthetic TRAIN scenarios covering clean linear, clean nonlinear and noisy far-end/near-end strata",
        "class": "historical_local_training_split",
        "source_pin": "research/aec_challenge_synthetic_pilot_manifest.json",
        "boundary": "Official train split only at source revision 8f861f0f8ffca26a3d1d16f17f2594ea89abe7ac; no held-out audio and no independent benchmark.",
    },
    {
        "id": "CI-3",
        "input": "Twelve complete AEC Challenge real TRAIN device groups (108 mono 16 kHz WAV files) with far-end, near-end, double-talk and movement scenarios",
        "class": "historical_local_training_split",
        "source_pin": "research/aec_challenge_real_pilot_manifest.json",
        "boundary": "Training corpus only; recorded-microphone consent/privacy and component rights unresolved; no clock-drift or device-timing measurement.",
    },
    {
        "id": "CI-4",
        "input": "Short 16 kHz paired TTS fixture with a deterministic five-tap echo path and a 256-sample LocalVQE output delay",
        "class": "historical_local_paired_synthetic",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "One synthetic voice and artificial echo path; not a room, corpus, listening or production-selection result.",
    },
    {
        "id": "CI-5",
        "input": "Microsoft AEC Challenge official train/dev/test suites, AECMOS/P.808 assets and the 20 ms latency track",
        "class": "source_only_frozen_protocol",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "Protocol and dataset documentation only; no dev/test audio, model or scorer is staged in this task.",
    },
    {
        "id": "CI-6",
        "input": "Independent licensed AEC development/test corpus with device capture, clock drift, reference dropout, path changes and clean near-end reference",
        "class": "missing_no_local_cohort",
        "source_pin": "audio_categories.md",
        "boundary": "Explicitly missing; the registry requires reference timing, double talk, drift and changing echo paths as part of the contract.",
    },
    {
        "id": "CI-7",
        "input": "AECMOS v4 predicted echo and degradation scores on the real training pilot",
        "class": "historical_local_predicted_metric",
        "source_pin": "reports/aec_challenge_real_pilot_summary_20261028.csv",
        "boundary": "Learned MOS-like predictions, not human listening; model licence and exact input-track applicability remain separate gates.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {"id": "CT-1", "name": "identity microphone passthrough", "role": "Paired baseline with no cancellation; required to expose near-end damage and peak behavior.", "source_pin": "docs/task-evidence/erle-and-double-talk-preservation/report.json"},
    {"id": "CT-2", "name": "fixed attenuation", "role": "Non-adaptive attenuation control separated from adaptive-reference metrics.", "source_pin": "docs/task-evidence/erle-and-double-talk-preservation/report.json"},
    {"id": "CT-3", "name": "no-reference passthrough", "role": "Withheld render must pass through without adaptation or weight change; no-reference is not reference AEC.", "source_pin": "docs/task-evidence/nlms-aec/README.md"},
    {"id": "CT-4", "name": "delayed and misaligned render", "role": "Checks explicit reference alignment and rejects silent trimming; measured fixture lag is not device latency.", "source_pin": "docs/task-evidence/nlms-aec/report.json"},
    {"id": "CT-5", "name": "far-end-only valid window for ERLE", "role": "ERLE is reported only on sufficiently quiet far-end-only windows, not during double talk.", "source_pin": "docs/task-evidence/erle-and-double-talk-preservation/README.md"},
    {"id": "CT-6", "name": "double-talk near-end reference preservation", "role": "Separate near-end preservation metric; echo attenuation alone cannot pass a duplex claim.", "source_pin": "docs/task-evidence/erle-and-double-talk-preservation/report.json"},
    {"id": "CT-7", "name": "path-change and reset schedule", "role": "Abrupt echo-path change and reset behavior are frozen; reconvergence is reported separately.", "source_pin": "docs/task-evidence/nlms-aec/report.json"},
    {"id": "CT-8", "name": "optional residual postfilter OFF", "role": "SpeexDSP residual suppression is compared against MDF alone and stays OFF when near-end preservation is not recovered.", "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/report.json"},
    {"id": "CT-9", "name": "predicted versus human score separation", "role": "AECMOS echo/degradation predictions are labelled as predicted and never relabelled as human ratings.", "source_pin": "reports/aec_challenge_real_pilot_summary_20261028.csv"},
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "AEC Challenge synthetic and real TRAIN manifests, selection rows and per-file hashes",
        "class": "research_metadata",
        "status": "Pinned metadata only; media remains outside this task, not staged, not redistributed and not cleared for release evidence",
        "source_pin": "research/aec_challenge_synthetic_pilot_manifest.json",
    },
    {
        "asset": "Microsoft AEC Challenge source revision and dataset rights audit",
        "class": "external_documentation",
        "status": "Documentation only; participant-level consent/privacy and component source mapping remain unresolved",
        "source_pin": "research/aec_research_20261028.md",
    },
    {
        "asset": "LocalVQE compact echo-only and full-enhancement GGUF weights",
        "class": "research_model_assets",
        "status": "Hashes recorded by prior research only; no weight file is staged or licensed by this task",
        "source_pin": "research/aec_research_20261028.md",
    },
    {
        "asset": "AECMOS v4 16 kHz scenario-aware ONNX scorer",
        "class": "research_model_assets",
        "status": "Predicted-score tool only; not staged here and not a human listening result",
        "source_pin": "research/aec_research_20261028.md",
    },
    {
        "asset": "Vendored SpeexDSP 1.2.1 MDF and optional residual suppressor source",
        "class": "sdk_vendored_source",
        "status": "Exact source pinned by merged SDK evidence; task-local synthetic oracle only, postfilter unregistered and OFF",
        "source_pin": "docs/task-evidence/speexdsp-mdf-reference/README.md",
    },
    {
        "asset": "DTLN-AEC 128/256/512 paired-reference checkpoints and TFLite runtime",
        "class": "missing_model_assets",
        "status": "Not staged; local generic DTLN enhancement weights are not substitutes for paired-reference DTLN-AEC",
        "source_pin": "adapters/dtln-aec/README.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "NLMS sample-domain adaptive reference on a paired synthetic 96-tap path",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["nlms-aec"],
        "source_pin": "docs/task-evidence/nlms-aec/report.json",
        "values": {
            "fixture_samples": 51200,
            "frames": 320,
            "single_talk_erle_db": 35.17011745522603,
            "double_talk_near_snr_db": 10.548298393394273,
            "peak_abs": 0.4441923128017083,
            "reconvergence_delta_db": 3.1239172829714263,
            "nonfinite_count": 0,
        },
        "scope": "16 kHz mono 160-sample v0 grid, seeded synthetic sparse 96-tap echo path with delay change; no real room, corpus, drift, listening or device timing; not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Guarded RLS synthetic reference with legacy nonfinite reproduction",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["rls-aec"],
        "source_pin": "docs/task-evidence/rls-aec/report.json",
        "values": {
            "fixture_samples": 51200,
            "single_talk_erle_db": 40.54805767441976,
            "double_talk_near_snr_db": 12.987628025946108,
            "peak_abs": 0.4345938833376424,
            "historical_first_nonfinite_sample": 140683,
            "historical_first_nonfinite_seconds": 8.793,
            "guard_extension_samples": 160000,
            "nonfinite_count": 0,
        },
        "scope": "Guarded task-local synthetic RLS with explicit playback reference; the pinned legacy recursion is reproduced analytically as a control; no recorded, device or listening result; not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Fixed RLS-to-NLMS hybrid synthetic 128-tap screen",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["fixed-rls-to-nlms-aec"],
        "source_pin": "docs/task-evidence/fixed-rls-to-nlms-aec/report.json",
        "values": {
            "fixture_samples": 51200,
            "single_talk_erle_db": 40.27389813607851,
            "double_talk_near_snr_db": 43.82091196289032,
            "peak_abs": 0.378834867804335,
            "reconvergence_delta_db": 7.336112789473038,
            "nonfinite_count": 0,
        },
        "scope": "Task-local synthetic fixed RLS warmup handing weights to NLMS; proposes no processor and carries no room, corpus or device result; not rerun by this survey.",
    },
    {
        "id": "HE-4",
        "label": "Historical fixed-hybrid recorded AEC Challenge training pilot",
        "outcome_class": "historical_local_adjacent_recorded_training_pilot",
        "component_ids": ["fixed-rls-to-nlms-aec"],
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "values": {
            "synthetic_train_scenarios": 12,
            "delta_near_snr_db": -17.74,
            "max_peak": 715.78,
            "double_talk_echo_mos_delta": 0.764,
            "double_talk_degradation_mos_delta": -1.793,
            "movement_echo_mos_delta": 1.048,
            "movement_degradation_mos_delta": -2.152,
            "hybrid_peak_abs_double_talk": 14.72,
            "hybrid_peak_abs_movement_double_talk": 48.12,
            "full_rls_nonfinite_near_only_count": 12,
        },
        "scope": "AEC Challenge synthetic TRAIN clips plus 12 GUID times 5 real TRAIN scenarios; AECMOS predicted, output WAVs not retained, rights unresolved, one configuration; no human or independent result; not rerun by this survey.",
    },
    {
        "id": "HE-5",
        "label": "SpeexDSP MDF with optional residual postfilter on paired synthetic conditions",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["speexdsp-mdf-reference", "speex-mdf-residual-postfilter"],
        "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/report.json",
        "values": {
            "far_end_erle_db_mdf_only": 15.675997,
            "far_end_erle_db_postfilter": 15.590018,
            "overlap_near_ratio_mdf_only": 0.968517,
            "overlap_near_ratio_postfilter": 0.687357,
            "nonfinite_count": 0,
            "missing_result_count": 20,
        },
        "scope": "Paired synthetic five-condition 48,000-sample oracle against vendored SpeexDSP 1.2.1; residual postfilter stays OFF and unregistered because near-end preservation was not recovered; not rerun by this survey.",
    },
    {
        "id": "HE-6",
        "label": "Task-local AEC3-shaped synthetic reference (not real WebRTC AEC3)",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["webrtc-aec3"],
        "source_pin": "docs/task-evidence/webrtc-aec3/report.json",
        "values": {
            "fixed_attenuation_erle_db": 6.0206,
            "identity_erle_db": 0.0,
            "identity_overlap_near_snr_db": -5.289827,
            "fixed_attenuation_overlap_near_snr_db": -0.330516,
            "algorithmic_delay_samples": 0,
        },
        "scope": "AEC3-shaped shadow-filter delay tracker plus NLMS and residual gain on synthetic paired signals; no pinned WebRTC source, binary, runtime or weights and no parity claim; not rerun by this survey.",
    },
    {
        "id": "HE-7",
        "label": "AEC Challenge synthetic TRAIN pilot (12 scenarios)",
        "outcome_class": "historical_local_training_split",
        "component_ids": ["localvqe-compact-echo-only", "localvqe-compact-full", "webrtc-aec3", "speexdsp-mdf-reference"],
        "source_pin": "research/aec_research_20261028.md",
        "values": {
            "scenarios": 12,
            "localvqe_full_median_erle_db": 18.11,
            "localvqe_full_median_double_talk_near_snr_db": 9.34,
            "localvqe_echo_only_median_erle_db": 13.87,
            "localvqe_echo_only_median_near_snr_db": 8.48,
            "webrtc_aec3_median_erle_db": 20.97,
            "webrtc_aec3_median_near_snr_db": 2.0,
            "speexdsp_mdf_median_erle_db": 7.22,
            "speexdsp_mdf_median_near_snr_db": 4.74,
        },
        "scope": "Official AEC Challenge synthetic TRAIN split only at revision 8f861f0f8ffca26a3d1d16f17f2594ea89abe7ac; media not staged, no held-out data, no human listening; not rerun by this survey.",
    },
    {
        "id": "HE-8",
        "label": "AEC Challenge real TRAIN pilot (12 device groups, AECMOS predicted)",
        "outcome_class": "historical_local_training_split",
        "component_ids": ["localvqe-compact-echo-only", "localvqe-compact-full", "webrtc-aec3", "speexdsp-mdf-reference", "aecmos"],
        "source_pin": "reports/aec_challenge_real_pilot_summary_20261028.csv",
        "values": {
            "device_groups": 12,
            "wav_files": 108,
            "localvqe_full_double_talk_echo_mos": 4.1768,
            "localvqe_full_double_talk_degradation_mos": 3.337,
            "webrtc_aec3_ns3_double_talk_echo_mos": 4.5053,
            "webrtc_aec3_ns3_double_talk_degradation_mos": 2.3808,
            "speexdsp_mdf_res_double_talk_echo_mos": 3.2259,
            "speexdsp_mdf_res_double_talk_degradation_mos": 3.91,
        },
        "scope": "Twelve complete training-corpus device groups scored with AECMOS v4 predicted echo/degradation, not human ratings; no clean near-end reference, drift or device-timing result; media and rights not staged; not rerun by this survey.",
    },
    {
        "id": "HE-9",
        "label": "LocalVQE compact paired TTS inference check",
        "outcome_class": "historical_local_neural_reference_model",
        "component_ids": ["localvqe-compact-echo-only", "localvqe-compact-full", "speexdsp-mdf-reference"],
        "source_pin": "research/aec_research_20261028.md",
        "values": {
            "fixture_seconds": 7.55,
            "localvqe_echo_only_erle_db": 32.69,
            "localvqe_echo_only_double_talk_near_snr_db": 14.56,
            "localvqe_full_erle_db": 51.12,
            "localvqe_full_double_talk_near_snr_db": 13.66,
            "speexdsp_mdf_erle_db": 12.77,
            "speexdsp_mdf_near_snr_db": 6.98,
            "output_delay_samples": 256,
        },
        "scope": "One 7.55-second synthetic TTS far-end/near-end fixture with a deterministic five-tap path and measured 16 ms LocalVQE output delay; no noise, room, corpus, listening or selection result; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "LocalVQE upstream reports an 800-clip AEC Challenge 2022 blind-set evaluation for its larger models",
        "class": "source_reported",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "Upstream claim only; the local compact checkpoints and TTS fixture do not reproduce it, and no blind-set audio is staged here.",
    },
    {
        "id": "RO-2",
        "claim": "An independent Swift port reports numerical parity against upstream LocalVQE output but only a partially reproduced quality benchmark and an ambiguous ERLE protocol",
        "class": "source_reported",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "Third-party source report; not a measurement from this checkout and not a local parity or qualification result.",
    },
    {
        "id": "RO-3",
        "claim": "S21 NKF-AEC publishes a neural Kalman filtering AEC implementation",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Repository lead only; no checkpoint, revision, rights grant or reference-timing contract is verified or staged.",
    },
    {
        "id": "RO-4",
        "claim": "S22 Speex documentation describes a frequency-domain MDF echo canceller with explicit far-end reference and optional residual suppression",
        "class": "source_reported",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "API documentation only; local SpeexDSP evidence is task-local synthetic and does not establish production or corpus parity.",
    },
    {
        "id": "RO-5",
        "claim": "CAGCRN reports a 0.07M-parameter cross-attention gated CRN for joint AEC and noise suppression",
        "class": "source_reported",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "Paper-level claim; runnable source, checkpoint compatibility and licensed weights were not verified.",
    },
    {
        "id": "RO-6",
        "claim": "DTLN-AEC upstream publishes 128/256/512-unit paired-reference checkpoints and reports third place in the 2021 challenge",
        "class": "source_reported",
        "source_pin": "research/aec_research_20261028.md",
        "boundary": "Upstream claim; local generic DTLN enhancement weights are not paired-reference DTLN-AEC and no AEC checkpoint is staged.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "identity_control": "CT-1 / CT-3; identity and no-reference passthrough, not a duplex result",
        "matched_baseline": "HE-1..HE-6 paired synthetic controls; HE-7/HE-8 historical training-split comparisons",
        "modality_split": "Echo-only, near-only, double talk, delay change, movement and no-reference stay separate",
        "paired_objective_scores": "HE-1..HE-9; transcribed and not rerun here",
        "clean_preservation": "CT-5 / CT-6; synthetic near-end preservation only, no real clean reference or listening",
        "peaks_and_invalid_outputs": "HE-1..HE-5 finite/peak and invalid-case controls; no target-device peak or deadline study",
        "unpaired_predictive_screen": "HE-8 AECMOS predicted echo/degradation, explicitly not human",
        "listening": "No CLN-05 listening items, ratings or playback clearance",
        "alignment_state_memory_timing": "CT-4 / CT-7 fixture alignment and path change; no clock drift, loop or device timing",
    },
    "blocked": [
        "Rights-qualified independent AEC development/test corpus with paired render/capture and clean near-end reference",
        "Frozen reference timing, clock-drift, dropout, path-change and movement protocol on recorded devices",
        "Real provider/runtime parity at exact source revision and settings, including WebRTC AEC3 and SpeexDSP",
        "Runnable neural AEC checkpoints and licensed weights for DTLN-AEC, NKF and joint AEC plus NS candidates",
        "Human listening and near-end preservation under double talk, not only predicted AECMOS",
        "Target-device content/availability timing, memory, deadline and resource evidence",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "paired_synthetic_historical_local": True,
    "recorded_training_split_historical_local": True,
    "predicted_metric_not_human": True,
    "neural_reference_model_execution": True,
    "source_reported_upstream_claim": True,
    "human_listening_result": False,
    "independent_heldout_benchmark": False,
    "clock_drift_or_device_timing": False,
    "device_loop_or_loudspeaker_measurement": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "release_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Acquire a rights-qualified independent AEC development/test corpus with paired render/capture, frozen reference timing and clean near-end reference",
        "evidence_gap": "Only AEC Challenge TRAIN subsets and seeded synthetic fixtures are reviewed; no held-out or independent corpus, device clock, drift or clean near-end reference is staged.",
        "follow_up_ids": [
            "SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES",
            "SDK-FND-AUDIT",
            "SDK-FND-DUPLEX",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-05 feasibility row was found for corpus acquisition; the research-control and foundation rows own fixture, asset and clock rules, not a recorded AEC corpus.",
    },
    {
        "id": "G02",
        "actionable_gap": "Establish real provider parity for WebRTC AEC3 and SpeexDSP at frozen source revision and settings",
        "evidence_gap": "The WebRTC row is an AEC3-shaped synthetic reference with no pinned WebRTC source, binary, runtime or weights; the SpeexDSP row is a task-local synthetic oracle.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-05 feasibility row was found for source parity; the existing SDK-WEBRTC-AEC3 implementation row is outside this survey's allowed link modes.",
    },
    {
        "id": "G03",
        "actionable_gap": "Stage a runnable DTLN-AEC paired-reference checkpoint and TFLite runtime and evaluate reference alignment and double-talk preservation",
        "evidence_gap": "DTLN-AEC is blocked; only mock adapter coverage and generic speech-enhancement weights exist, which are not paired-reference DTLN-AEC substitutes.",
        "follow_up_ids": [
            "SDK-DTLN-AEC-128-256-512",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The DTLN-AEC feasibility row is a candidate-discovery lead only; no checkpoint, runtime or quality result is created by this map.",
    },
    {
        "id": "G04",
        "actionable_gap": "Verify and pin the S21 neural Kalman filter source, checkpoint, runtime and reference-timing contract before any execution",
        "evidence_gap": "The S21 lead is a repository name; no source tree, checkpoint, licence, runtime or reset/reconvergence behavior is verified or staged.",
        "follow_up_ids": [
            "SDK-NEURAL-KALMAN-FILTERING-NKF",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The NKF feasibility row is a scoping lead for source and checkpoint verification; it does not enable a processor or establish a result.",
    },
    {
        "id": "G05",
        "actionable_gap": "Prototype PBFDAF/AUMDF and compare long-tail convergence, path-change reconvergence and cost with MDF",
        "evidence_gap": "PBFDAF/AUMDF is catalogued only; the merged SpeexDSP MDF evidence is a synthetic oracle and does not cover long-tail room behavior.",
        "follow_up_ids": [
            "SDK-PBFDAF-AUMDF",
            "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The PBFDAF feasibility row is a bounded comparison lead; the research-control row supplies measurement rules, not a new result.",
    },
    {
        "id": "G06",
        "actionable_gap": "Resolve source, checkpoint and licence availability for end-to-end neural AEC candidates (CAGCRN, DeepAEC, Dual-Path Echo Net and dual-branch residual suppression)",
        "evidence_gap": "CAGCRN and dual-branch residual suppression are considered; DeepAEC and Dual-Path Echo Net are blocked because exact identities or checkpoints are unresolved.",
        "follow_up_ids": [
            "SDK-CAGCRN-JOINT-AEC-AND-NS",
            "SDK-DEEPAEC",
            "SDK-DUAL-PATH-ECHO-NET",
            "SDK-FND-AUDIT",
        ],
        "feasibility_task_exists": True,
        "owner_note": "All linked feasibility rows are discovery leads only; no candidate is installed, enabled, pooled with CLN-06 or promoted by this map.",
    },
    {
        "id": "G07",
        "actionable_gap": "Measure clock drift, reference dropouts, path changes, movement and target-device timing on a real capture/playback loop",
        "evidence_gap": "Only fixture alignment and synthetic delay changes are recorded; no real loop, callback path, clock drift, deadline or resource measurement exists.",
        "follow_up_ids": [
            "SDK-FND-TIMING",
            "SDK-FND-DUPLEX",
            "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-05 timing feasibility row was found; the foundation rows own lifecycle, clock and timing-evidence rules, not a measured loop.",
    },
    {
        "id": "G08",
        "actionable_gap": "Replace predicted AECMOS-only ranking with human listening and near-end preservation under double talk",
        "evidence_gap": "AECMOS v4 predictions are the only duplex quality signal on recorded training data; no human ratings, playback clearance or ASR result exists.",
        "follow_up_ids": [
            "SDK-AECMOS",
            "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-05 listening feasibility row was found; the research-control rows own scorer and preservation design, not a listening result.",
    },
    {
        "id": "G09",
        "actionable_gap": "Clear rights for recorded AEC audio, participant privacy and model weights before any release evidence",
        "evidence_gap": "AEC Challenge component terms, recorded-microphone consent/privacy and LocalVQE/AECMOS per-weight terms remain unresolved; media is not staged.",
        "follow_up_ids": [
            "SDK-FND-AUDIT",
            "SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-05 rights feasibility row was found; the foundation and research-control rows own asset and fixture rules, not a rights grant.",
    },
    {
        "id": "G10",
        "actionable_gap": "Establish guarded RLS and fixed-hybrid stability and double-talk behavior beyond one synthetic fixture",
        "evidence_gap": "Guarded RLS avoids the historical nonfinite path in-fixture and the hybrid passes one synthetic screen, but the recorded pilot showed severe degradation and large peaks.",
        "follow_up_ids": [
            "SDK-RLS-AEC",
            "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated CLN-05 feasibility row was found; the RLS research-control row and preservation scorer own bounded stability and preservation rules, not a promotion.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES", "title": "AEC Challenge paired render/capture fixtures", "mode": "research-control"},
    {"task_id": "SDK-AECMOS", "title": "AECMOS", "mode": "research-control"},
    {"task_id": "SDK-ERLE-AND-DOUBLE-TALK-PRESERVATION", "title": "ERLE and double-talk preservation", "mode": "research-control"},
    {"task_id": "SDK-RLS-AEC", "title": "RLS AEC", "mode": "research-control"},
    {"task_id": "SDK-DTLN-AEC-128-256-512", "title": "DTLN-AEC 128/256/512", "mode": "feasibility"},
    {"task_id": "SDK-PBFDAF-AUMDF", "title": "PBFDAF / AUMDF", "mode": "feasibility"},
    {"task_id": "SDK-NEURAL-KALMAN-FILTERING-NKF", "title": "Neural Kalman filtering (NKF)", "mode": "feasibility"},
    {"task_id": "SDK-CAGCRN-JOINT-AEC-AND-NS", "title": "CAGCRN joint AEC and NS", "mode": "feasibility"},
    {"task_id": "SDK-DEEPAEC", "title": "DeepAEC", "mode": "feasibility"},
    {"task_id": "SDK-DUAL-PATH-ECHO-NET", "title": "Dual-Path Echo Net", "mode": "feasibility"},
    {"task_id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-DUPLEX", "title": "Reference, multichannel and clock contracts", "mode": "foundation"},
]

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified independent AEC development/test corpus with paired render/capture, frozen reference timing and clean near-end reference"},
    {"id": "RG-02", "blocked": True, "requirement": "Real provider parity for WebRTC AEC3 and SpeexDSP at frozen source revision and settings"},
    {"id": "RG-03", "blocked": True, "requirement": "Runnable neural AEC checkpoints, licensed weights and stated reference-timing contracts for DTLN-AEC, NKF and joint AEC plus NS candidates"},
    {"id": "RG-04", "blocked": True, "requirement": "Human listening and near-end preservation under double talk; predicted AECMOS alone is insufficient"},
    {"id": "RG-05", "blocked": True, "requirement": "Measured clock drift, reference dropout, path-change, movement and target-device timing evidence"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **CLN-05 \u2014 Reference-based acoustic echo cancellation (AEC)** | Remove loudspeaker playback leaking into the microphone. Scope: discovered_extension. | Adaptive FIR, NLMS, frequency-domain and Kalman filters | Neural-assisted adaptation or reference-conditioned estimation | Microphone + playback reference \u2192 near-end estimate | Reference timing, double talk, drift and changing echo paths are part of the contract. | [S21](https://github.com/fjiang9/NKF-AEC), [S22](https://www.speex.org/docs/manual/speex-manual/node7.html) |",
        "| **CLN-06 \u2014 Residual echo suppression** | Reduce echo remaining after cancellation.",
    ],
    "research/category_survey/sources.md": [
        "| S21 | [NKF acoustic echo cancellation implementation](https://github.com/fjiang9/NKF-AEC) | acoustics | direct |",
        "| S22 | [Speex echo cancellation documentation](https://www.speex.org/docs/manual/speex-manual/node7.html) | acoustics | search excerpt |",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Room | Freeze render/reference or measured RIRs, channel/rate/hop, excitation, delay, movement, noise and reset schedule. Include echo-only, near-end-only, overlap and no-reference cases. Report echo attenuation, near-end damage, nonfinite failures and alignments, including delayed/missing render. A no-reference suppressor gets its own independent comparison. |",
        "Recorded AEC pilots found nonfinite RLS output on near-end-only cases and",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "| WebRTC AEC3 | Acoustic echo cancellation | Synthetic and 12-device-group recorded training-corpus pilots; about 8 ms measured content alignment.",
        "| SpeexDSP MDF | Acoustic echo cancellation | Synthetic and recorded training-corpus pilots; 20 ms frames.",
        "| NLMS adaptive filter | Acoustic echo cancellation | Local recorded AEC screen, median compute RTF about 0.072.",
        "| RLS adaptive filter | Acoustic echo cancellation | Local screen, median compute RTF about 0.446; became nonfinite on all near-end-only clips in the recorded pilot.",
    ],
    "research/aec_research_20261028.md": [
        "The large ERLE for filters covering the exact synthetic path is a near-perfect linear simulation artifact, not evidence of real-room performance.",
        "This is a small pilot drawn from a training split, not an independent benchmark:",
        "No human listening, ASR, real-recording clock-drift tests, or target-device latency/energy tests have been run.",
        "The local real pilot manifest does not include participant-level consent/privacy or intended-use terms for its recorded microphone streams.",
    ],
    "reports/aec_challenge_real_pilot_summary_20261028.csv": [
        "doubletalk,WebRTC-AEC3+NS3,12,4.5053,4.2681,4.6497,2.3808,2.2321,2.5438,121.17,8.0,10.0",
    ],
    "adapters/dtln-aec/README.md": [
        "The upstream project publishes 128-, 256-, and 512-unit models.",
    ],
    "adapters/localvqe-aec/README.md": [
        "This adapter sends aligned 16 kHz mono microphone and far-end playback reference frames to LocalVQE's native stateful API.",
    ],
    "research/task_backlog.json": [
        "{\"activation_state\":\"catalogued\",\"blockers\":[],\"category_id\":\"CLN-05\",\"dependencies\":[],\"family_id\":\"F04\"",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/nlms-aec/README.md": [
        "Task-local, deterministic, synthetic/model-free evidence for a sample-domain",
    ],
    "docs/task-evidence/rls-aec/README.md": [
        "**proposal-only, deterministic, task-local synthetic",
    ],
    "docs/task-evidence/fixed-rls-to-nlms-aec/README.md": [
        "Task-local, deterministic, synthetic-only evidence for a causal RLS warmup that",
    ],
    "docs/task-evidence/speexdsp-mdf-reference/README.md": [
        "A **paired synthetic reference tool**, not an AEC, double-talk, quality, device,",
    ],
    "docs/task-evidence/speex-mdf-residual-postfilter/README.md": [
        "Near-end preservation against MDF alone was **not recovered**",
    ],
    "docs/task-evidence/erle-and-double-talk-preservation/README.md": [
        "The adapter reproduces the *shape* of the research comparison on frozen seeded",
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
    "reference_claim_without_reference_execution": "rejected; state unchanged",
    "heldout_benchmark_claim_without_test_split": "rejected; state unchanged",
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
        raise MapError("CLN-05 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("CLN-05 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F04 / CLN-05 is not unique")
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
            raise MapError("legacy backlog mismatch: F04/CLN-05/%s" % key)


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
        "recorded_training_split_historical_local": "historical_local_training_split" in classes,
        "predicted_metric_not_human": "historical_local_predicted_metric" in classes,
        "neural_reference_model_execution": any(
            row["outcome_class"] == "historical_local_neural_reference_model"
            for row in HISTORICAL_EXECUTIONS
        ),
        "source_reported_upstream_claim": any(row["class"] == "source_reported" for row in REPORTED_OUTCOMES),
        "human_listening_result": "human_listening_result" in classes,
        "independent_heldout_benchmark": "independent_heldout_benchmark" in classes,
        "clock_drift_or_device_timing": "device_clock_drift" in classes,
        "device_loop_or_loudspeaker_measurement": "device_loop" in classes,
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
        "aec_boundary": dict(AEC_BOUNDARY),
        "discovery": {
            "catalogued_source_leads": [lead["source_id"] for lead in SOURCE_LEADS],
            "reference_based_component_ids": [
                "nlms-aec",
                "rls-aec",
                "fixed-rls-to-nlms-aec",
                "speexdsp-mdf-reference",
                "webrtc-aec3",
                "localvqe-compact-echo-only",
                "localvqe-compact-full",
            ],
            "independent_heldout_test_split_present": False,
            "licensed_public_corpus_staged": False,
            "neural_reference_weights_present": False,
            "real_provider_runtime_parity_present": False,
            "note": "Reference-based components are mapped, but no independent licensed dev/test split, neural reference weights or real provider parity is staged; candidates remain adjacent, partial, considered or blocked.",
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
        "explicit_playback_reference_required",
        "reference_timing_and_drift_in_contract",
        "double_talk_preservation_is_separate_from_echo_attenuation",
        "changing_echo_path_is_a_material_stratum",
        "blind_one_input_suppression_is_not_reference_aec",
        "residual_echo_suppression_belongs_to_cln_06",
    ):
        if report["aec_boundary"][key] is not True:
            raise MapError("AEC boundary rule is not enforced: " + key)
    for key in (
        "real_webrtc_aec3_source_or_runtime_staged",
        "independent_licensed_dev_or_test_corpus_staged",
        "neural_reference_weights_staged",
        "device_clock_drift_or_loop_timing_measured",
        "human_listening_result",
    ):
        if report["aec_boundary"][key] is not False:
            raise MapError("AEC boundary claim is not closed: " + key)
    for key in (
        "independent_heldout_test_split_present",
        "licensed_public_corpus_staged",
        "neural_reference_weights_present",
        "real_provider_runtime_parity_present",
    ):
        if report["discovery"][key] is not False:
            raise MapError("discovery claim is not closed: " + key)
    if report["evidence_classes"]["independent_heldout_benchmark"] is not False:
        raise MapError("held-out benchmark is claimed without a test split")
    if report["evidence_classes"]["human_listening_result"] is not False:
        raise MapError("human listening is claimed without ratings")
    if report["evidence_classes"]["clock_drift_or_device_timing"] is not False:
        raise MapError("device timing is claimed without a device loop")
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
