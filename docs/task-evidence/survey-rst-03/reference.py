# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-RST-03.

This module builds a bounded taxonomy/comparison evidence map for the
codec-artifact restoration category (inventory category ``RST-03``). It reads
only pinned, read-only documents from the enclosing ``audioml`` workspace and
the SDK worktree. It does not load audio, weights, codecs, runtimes, media or
the network, and it does not register, expose, enable or qualify any
processor.

All curated records below are documentation mappings, not new measurements.
Historical local-pilot or source-reported values are transcribed verbatim from
the pinned documents and labelled with their original scope.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-RST-03"
TITLE = "Review coverage for Codec-artifact restoration"
CATEGORY_ID = "RST-03"
LEGACY_FAMILY = "F10"
BRANCH = "swarm/SDK-SURVEY-RST-03"
BASE_COMMIT = "2a475defe0d0d6ff4fed3c0044c1aa2566292552"
PROFILE = "Restoration"
COMPONENT = "codec-artifact-evidence-map"
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
    "reports/distortion-restoration/20261028-synthetic-screen.json": "87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/distortion_restoration_20261028.md": "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "research/noise_suppression_candidate_census.md": "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md": "79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b",
    "research/voice-enhancement-20261101/evaluation_records.md": "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a",
    "src/audioml_eval/distortion_restoration.py": "c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f",
}

# SDK-worktree-relative public-boundary pins. They are read only to prove that
# no public surface was touched; no header is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md": "ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df",
    "docs/task-evidence/quality-impairment-taxonomy/README.md": "77ad10fae3e41a06adad6cee377616c73dd8d7d458a76c9297aa55d837afcbe5",
    "docs/task-evidence/speex-mdf-residual-postfilter/README.md": "16c7643cc5550cd7358ee48f7dec62eb4045a3384364246cd357269ce0c28da9",
    "docs/task-evidence/survey-rst-01/README.md": "5888f8745720a90a6926ccbd158597e5804c0fc1fb937918f26da495b053d68a",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Distortion restoration",
    "name": "Codec-artifact restoration",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Reduce artifacts in decoded speech.",
    "method_families": {
        "classic": "Decoder postfilters and noise shaping",
        "ml": "Adaptive neural postfilters/nonlinear enhancement",
    },
    "input_output": "Decoded PCM, sometimes decoder features \u2192 improved PCM",
    "live_or_comparison_boundary": (
        "A codec-integrated method may require information unavailable to a "
        "generic PCM filter."
    ),
    "source_ids": ["S30", "S45"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S30",
        "title": "Opus 1.5 neural enhancement and loss recovery",
        "url": "https://opus-codec.org/demo/opus-1.5/",
        "access_scope": "direct",
        "mapped_components": [
            "opus-1-5-lace",
            "opus-1-5-nolace",
            "opus-deep-plc",
            "opus-dred",
        ],
        "gap_ids": ["G01", "G06"],
        "finding": (
            "The official Opus 1.5 material documents codec-integrated "
            "LACE/NoLACE neural postfilters plus deep PLC and DRED redundancy, "
            "none enabled by default. The documented claims define candidate "
            "scope only: no compatible Opus build, decoder feature stream, "
            "pinned encoder settings, packet trace, checkpoint review or local "
            "output exists in the reviewed records."
        ),
    },
    {
        "source_id": "S45",
        "title": "URGENT 2026 distortion taxonomy",
        "url": "https://urgent-challenge.github.io/urgent2026/track1/",
        "access_scope": "direct",
        "mapped_components": [
            "urgent-bsrnn",
            "urgent-bsrnn-flow",
            "tf-gridnet-urgent-2025-baseline",
        ],
        "gap_ids": ["G05"],
        "finding": (
            "The URGENT 2026 challenge taxonomy covers multiple distortions, "
            "including codec degradation, for universal speech enhancement. "
            "Its BSRNN/BSRNN-Flow and TF-GridNet baselines are catalogued as "
            "general enhancement models, not as codec-artifact restorers; no "
            "challenge data, checkpoint, locked runtime or codec-stratified "
            "score was staged locally."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Decoder-side low-pass postfilter on companded narrowband PCM (\u00b5-law proxy)",
        "components": ["law-codec-proxy-and-low-pass-postfilter"],
        "gap_ids": ["G01", "G02", "G03"],
        "status": "historical_local_proxy_only_no_real_codec_postfilter",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Adjacent decoder/redundancy and packet-feature path (not codec-artifact restoration)",
        "components": [
            "opus-1-4-standard-decoder-plc",
            "opus-dred",
            "opus-packetization-fec-dtx-and-comfort-noise",
        ],
        "gap_ids": ["G06"],
        "status": "adjacent_rst04_screen_or_considered_not_rst03",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Decoder noise shaping, deemphasis and residual postfilter boundary (adjacent, not executed for codec artifacts)",
        "components": ["speex-mdf-residual-postfilter"],
        "gap_ids": ["G03", "G06"],
        "status": "adjacent_echo_residual_evidence_not_codec_artifact_restoration",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Codec-integrated neural postfilters in the decoder (Opus 1.5 LACE/NoLACE)",
        "components": ["opus-1-5-lace", "opus-1-5-nolace"],
        "gap_ids": ["G01"],
        "status": "source_reported_only_not_staged_or_run",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Codec-latent neural enhancement (SE-NAC family)",
        "components": ["se-nac-codec-latent-enhancement-family"],
        "gap_ids": ["G04"],
        "status": "census_candidate_not_staged_or_run",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": "Universal multi-distortion neural baselines (URGENT 2026 BSRNN/BSRNN-Flow, TF-GridNet 2025)",
        "components": [
            "urgent-bsrnn",
            "urgent-bsrnn-flow",
            "tf-gridnet-urgent-2025-baseline",
        ],
        "gap_ids": ["G05"],
        "status": "blocked_or_considered_not_run",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": "Adjacent neural packet-loss concealment and codec I/O tooling boundary (not codec-artifact restoration)",
        "components": [
            "opus-deep-plc",
            "lyra-ii-v2-codec-plc",
            "torchaudio-torchcodec-and-soundfile-compatibility-for-llvc",
        ],
        "gap_ids": ["G06", "G11"],
        "status": "adjacent_rst04_or_tool_scope_not_rst03",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "law-codec-proxy-and-low-pass-postfilter", "evidence_status": "evaluated", "task": "SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER"},
    {"component_id": "speex-mdf-residual-postfilter", "evidence_status": "evaluated", "task": "SDK-SPEEX-MDF-RESIDUAL-POSTFILTER"},
    {"component_id": "opus-1-4-standard-decoder-plc", "evidence_status": "evaluated", "task": "SDK-OPUS-1-4-STANDARD-DECODER-PLC"},
    {"component_id": "opus-1-5-lace", "evidence_status": "considered", "task": "SDK-OPUS-1-5-LACE"},
    {"component_id": "opus-1-5-nolace", "evidence_status": "considered", "task": "SDK-OPUS-1-5-NOLACE"},
    {"component_id": "opus-deep-plc", "evidence_status": "considered", "task": "SDK-OPUS-DEEP-PLC"},
    {"component_id": "opus-dred", "evidence_status": "considered", "task": "SDK-OPUS-DRED"},
    {"component_id": "opus-packetization-fec-dtx-and-comfort-noise", "evidence_status": "considered", "task": "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE"},
    {"component_id": "lyra-ii-v2-codec-plc", "evidence_status": "blocked", "task": "SDK-LYRA-II-V2-CODEC-PLC"},
    {"component_id": "se-nac-codec-latent-enhancement-family", "evidence_status": "considered", "task": "SDK-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY"},
    {"component_id": "urgent-bsrnn", "evidence_status": "blocked", "task": "SDK-URGENT-BSRNN"},
    {"component_id": "urgent-bsrnn-flow", "evidence_status": "considered", "task": "SDK-URGENT-BSRNN-FLOW"},
    {"component_id": "tf-gridnet-urgent-2025-baseline", "evidence_status": "considered", "task": "SDK-TF-GRIDNET-URGENT-2025-BASELINE"},
    {"component_id": "torchaudio-torchcodec-and-soundfile-compatibility-for-llvc", "evidence_status": "partial", "task": "SDK-TORCHAUDIO-TORCHCODEC-AND-SOUNDFILE-COMPATIBILITY-FOR-LLVC"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "12 EARS clips through 8-bit \u00b5-law at 8 kHz and a 4-bit \u00b5-law stress proxy, scored against the same narrowband signal before companding",
        "class": "historical_local_codec_proxy_pilot_not_reproduced",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Transcribed pilot means from the pinned ledger; bytes, encoder objects and per-clip rows are provenance only and were not rerun by this survey.",
    },
    {
        "id": "CI-2",
        "input": "Frozen task-local Speex MDF paired synthetic echo fixture with the optional residual postfilter OFF and ON",
        "class": "adjacent_echo_residual_historical_local",
        "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/README.md",
        "boundary": "AEC residual suppression is not codec-artifact restoration; the row is an adjacent boundary control only.",
    },
    {
        "id": "CI-3",
        "input": "12-clip EARS packet-erasure screen with bundled libopus 1.4 standard decoder PLC and same-codec waveform controls",
        "class": "adjacent_packet_loss_historical_local",
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
        "boundary": "Packet-loss concealment belongs to RST-04; no post-decode codec-artifact condition was isolated or scored.",
    },
    {
        "id": "CI-4",
        "input": "Opus 1.5 codec-integrated LACE/NoLACE neural postfilters and deep PLC/DRED (named source lead S30)",
        "class": "source_reported_only",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Official technical notes and demo scope; no compatible build, decoder feature stream, checkpoint or local output.",
    },
    {
        "id": "CI-5",
        "input": "SE-NAC codec-latent neural enhancement family with released checkpoints (census lead)",
        "class": "source_reported_census",
        "source_pin": "research/noise_suppression_candidate_census.md",
        "boundary": "Census metadata only; no weight, license, task data, decoded-speech cohort or local inference.",
    },
    {
        "id": "CI-6",
        "input": "URGENT 2026 challenge taxonomy and BSRNN/BSRNN-Flow/TF-GridNet universal baselines (named source lead S45)",
        "class": "external_registration_gated_not_run",
        "source_pin": "research/noise_suppression_candidate_census.md",
        "boundary": "Challenge framing and checkpoint notes only; no registered data, locked runtime, codec stratum or score.",
    },
    {
        "id": "CI-7",
        "input": "Decoded-input identity versus the same narrowband signal before companding at 8-bit and 4-bit \u00b5-law",
        "class": "codec_proxy_reference_baseline_historical_local",
        "source_pin": "reports/distortion-restoration/20261028-synthetic-screen.json",
        "boundary": "The decoded input is the task-matched damaged baseline, not a restored or enhanced output.",
    },
    {
        "id": "CI-8",
        "input": "4-bit \u00b5-law proxy labelled as a stress condition rather than a standard codec",
        "class": "historical_local_stress_proxy_not_standard_codec",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "No MP3/AAC/Opus transform coding, tandem coding or jitter is represented.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "decoded-input identity",
        "role": "Task-matched damaged-input baseline for both companded narrowband conditions.",
        "source_pin": "reports/distortion-restoration/20261028-synthetic-screen.json",
    },
    {
        "id": "CT-2",
        "name": "low-pass decoder postfilter",
        "role": "Classic comparator: it lowers 8-bit SI-SDR from 37.99 to 33.12 dB and gains only 0.28 dB on the 4-bit stress proxy.",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "id": "CT-3",
        "name": "bit-depth sweep, 8-bit versus 4-bit \u00b5-law",
        "role": "Separates a standard 8-bit companding condition from a non-standard 4-bit stress proxy; descriptive, not a codec ranking.",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "id": "CT-4",
        "name": "pre-companding narrowband reference",
        "role": "Isolates coding distortion from bandwidth loss by scoring decoded output against the same narrowband signal.",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "id": "CT-5",
        "name": "Opus 1.5 codec-integrated postfilter disabled state",
        "role": "LACE/NoLACE are documented as not enabled by default; any future run must record the exact decoder flag and quality setting.",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "id": "CT-6",
        "name": "nonfinite-input adverse case",
        "role": "NaN/Inf input produces no serialized output and cannot count as a pass.",
        "source_pin": "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md",
    },
    {
        "id": "CT-7",
        "name": "Opus standard PLC same-codec waveform controls",
        "role": "Adjacent RST-04 comparison against zero-fill, linear, pitch-repeat and autoregressive controls; it does not test codec-artifact postfilters.",
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
    },
    {
        "id": "CT-8",
        "name": "Speex MDF residual postfilter OFF/ON",
        "role": "Adjacent room-profile boundary showing near-end preservation loss; not a codec postfilter.",
        "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/README.md",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "EARS 12-clip \u00b5-law pilot media",
        "class": "research_audio",
        "status": "CC BY-NC 4.0 research media in the cited record; bytes not staged or verified in this task",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "asset": "Deterministic \u00b5-law proxy fixtures generated from the EARS subset",
        "class": "generated_fixture",
        "status": "Derived companding plus low-pass postfilter; no external media or download in this task",
        "source_pin": "reports/distortion-restoration/20261028-synthetic-screen.json",
    },
    {
        "asset": "Opus 1.5 reference software, demo material and codec-integrated features (S30)",
        "class": "external_code_and_runtime",
        "status": "No compatible build, decoder flag, packet trace, checkpoint or rights review staged",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "asset": "URGENT 2026 challenge data and BSRNN/TF-GridNet checkpoints (S45)",
        "class": "external_code_data_and_weights",
        "status": "Registration and large-checkpoint gate; nothing downloaded, staged or scored",
        "source_pin": "research/noise_suppression_candidate_census.md",
    },
    {
        "asset": "SE-NAC source and checkpoints",
        "class": "source_and_metadata_only",
        "status": "Census record only; no checkpoint, runtime, license clearance or task data staged",
        "source_pin": "research/noise_suppression_candidate_census.md",
    },
    {
        "asset": "VCTK v3 prepared listening items",
        "class": "research_audio",
        "status": "Prepared only; zero collected ratings and no playback clearance",
        "source_pin": "docs/task-evidence/quality-impairment-taxonomy/README.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "12-clip \u00b5-law codec pilot at 8-bit and 4-bit proxies",
        "outcome_class": "historical_local_codec_proxy_pilot_not_reproduced",
        "component_ids": ["law-codec-proxy-and-low-pass-postfilter"],
        "source_pin": "research/distortion_restoration_20261028.md",
        "values": {
            "clips": 12,
            "conditions": 2,
            "methods": 2,
            "codec_rows": 48,
            "decoded_input_si_sdr_8bit_db": 37.99,
            "lowpass_postfilter_si_sdr_8bit_db": 33.12,
            "postfilter_delta_8bit_db": -4.87,
            "decoded_input_si_sdr_4bit_db": 16.43,
            "lowpass_postfilter_si_sdr_4bit_db": 16.71,
            "postfilter_delta_4bit_db": 0.28,
            "decoded_input_stoi_8bit": 0.9984,
            "lowpass_postfilter_stoi_8bit": 0.9977,
            "decoded_input_stoi_4bit": 0.8751,
            "lowpass_postfilter_stoi_4bit": 0.8749,
            "decoded_input_rmse_8bit": 0.00153079,
            "lowpass_postfilter_rmse_8bit": 0.00290263,
            "decoded_input_rmse_4bit": 0.01812955,
            "lowpass_postfilter_rmse_4bit": 0.01752512,
        },
        "scope": "12 clips per condition, 8 kHz \u00b5-law proxy; the 4-bit case is a stress proxy, not a standard codec; no transform codec, jitter, mobile channel or human evaluation; pilot means transcribed, not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Adjacent Opus 1.4 standard decoder PLC 12-clip packet-erasure screen",
        "outcome_class": "adjacent_packet_loss_historical_local",
        "component_ids": ["opus-1-4-standard-decoder-plc"],
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
        "values": {
            "clips": 12,
            "output_rows": 132,
            "isolated_loss_pct": 10.0,
            "burst_loss_pct": 16.7,
            "opus_plc_si_sdr_isolated_db": 2.39,
            "opus_plc_stoi_isolated": 0.913,
            "opus_plc_lost_region_rmse_isolated": 0.1272,
            "opus_plc_median_rtf_isolated": 0.00153,
            "opus_plc_si_sdr_burst_db": 0.92,
            "opus_plc_stoi_burst": 0.848,
            "opus_plc_lost_region_rmse_burst": 0.1388,
            "intact_decode_si_sdr_db": 5.44,
            "intact_decode_stoi": 0.998,
            "codec_alignment_samples": 104,
            "codec_alignment_ms": 6.5,
        },
        "scope": "Deterministic synthetic packet erasure at 24 kbit/s on 12 EARS clips; bundled libopus 1.4, no FEC, DRED, network trace, phone or Opus 1.5 feature; adjacent RST-04 evidence and not rerun by this survey.",
    },
    {
        "id": "HE-3",
        "label": "Adjacent Speex MDF residual postfilter paired synthetic screen",
        "outcome_class": "adjacent_echo_residual_historical_local",
        "component_ids": ["speex-mdf-residual-postfilter"],
        "source_pin": "docs/task-evidence/speex-mdf-residual-postfilter/README.md",
        "values": {
            "near_ratio_postfilter_off": 0.968517,
            "near_ratio_postfilter_on": 0.687357,
            "far_erle_postfilter_off_db": 15.675997,
            "far_erle_postfilter_on_db": 15.590018,
            "repeat_count": 3,
        },
        "scope": "Optional 20 ms paired synthetic AEC boundary; near-end preservation is not recovered; adjacent room-profile evidence only and not codec-artifact restoration; not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "Opus 1.5 provides codec-integrated LACE/NoLACE neural postfilters plus deep PLC and DRED",
        "class": "source_reported",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Official technical-note scope; features are documented as not enabled by default and were not built, invoked or scored here.",
    },
    {
        "id": "RO-2",
        "claim": "URGENT 2026 defines a multi-distortion universal enhancement taxonomy that includes codec degradation",
        "class": "source_reported",
        "source_pin": "research/noise_suppression_candidate_census.md",
        "boundary": "Challenge and census framing only; no registered data, model output or codec-stratified metric.",
    },
    {
        "id": "RO-3",
        "claim": "SE-NAC is a neural audio-codec-representation enhancement family with released variants",
        "class": "source_reported_census",
        "source_pin": "research/noise_suppression_candidate_census.md",
        "boundary": "Census metadata only; checkpoint availability is not a local result or capability.",
    },
    {
        "id": "RO-4",
        "claim": "Avoid generic postfiltering when the codec is unknown; codec-integrated features have information unavailable to a PCM filter",
        "class": "source_reported_pilot_conclusion",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Small proxy pilot conclusion with no listening; not a general best-method or release claim.",
    },
    {
        "id": "RO-5",
        "claim": "The pinned per-clip ledger records the RST-03 codec-proxy rows behind the pilot means",
        "class": "source_reported_provenance_ledger",
        "source_pin": "reports/distortion-restoration/20261028-synthetic-screen.json",
        "boundary": "Provenance only; the ledger was not rerun, re-scored or pooled with any adjacent task.",
    },
    {
        "id": "RO-6",
        "claim": "Bundled libopus 1.4 standard decoder PLC was locally evaluated for RST-04 packet erasure",
        "class": "source_reported_adjacent_result",
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
        "boundary": "Adjacent packet-loss evidence; not Opus 1.5 deep PLC/DRED and not a codec-artifact postfilter.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "frozen_corruption_and_metadata": "CI-1/CI-7/CI-8: \u00b5-law bit depth, 8 kHz rate and pre-companding reference are recorded; no transform codec or encoder setting exists",
        "matched_damaged_baseline": "CT-1 decoded-input identity and CT-4 pre-companding narrowband reference",
        "degradation_strata": "CT-3 8-bit standard proxy versus non-standard 4-bit stress proxy; no bitrate, tandem or jitter stratum",
        "bandwidth_strata": "Fixed 8 kHz narrowband proxy; no wider-band or codec-specific band split",
        "task_specific_quality": "HE-1 SI-SDR/RMSE/STOI pilot means; no new perceptual or intelligibility score",
        "validity_and_peak_bounds": "CT-6 nonfinite adverse case; no output-peak or decoded-interval bound was published for the proxy",
        "missing_result_accounting": "No neural or codec-integrated candidate has a local result; absence is recorded, not promoted",
        "listening": "VCTK items prepared with zero ratings; no RST-03 listening result exists",
        "timing": "No decoder-plus-postfilter content delay, availability, memory or deadline measurement is mapped",
    },
    "blocked": [
        "Rights-qualified paired decoded-speech cohort across real codecs with frozen encoder settings and clean reference",
        "Codec-integrated postfilter run with decoder features, exact flags, bitrate and quality settings",
        "Real transform-codec coverage including tandem coding, jitter and packet-trace conditions",
        "Codec-latent and universal neural baselines with pinned weights, rights and a matched cohort",
        "Independent blinded listening and intelligibility/content analysis",
        "Target-device decoder-plus-postfilter timing, memory and deadline evidence",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval and release approval",
    ],
}

# Evidence classes are claims about what the reviewed records contain. A class
# is true only when a mapped row backs it; absence is recorded as false instead
# of being inherited from an adjacent survey.
EVIDENCE_CLASSES: Dict[str, bool] = {
    "paired_synthetic_historical_local": True,
    "historical_pilot_means_not_reproduced": True,
    "codec_proxy_reference_identity_historical_local": True,
    "historical_local_stress_proxy_not_standard_codec": True,
    "adjacent_packet_loss_historical_local": True,
    "adjacent_echo_residual_historical_local": True,
    "unpaired_predictive_historical_local": False,
    "codec_integrated_neural_postfilter_local": False,
    "prepared_listening_without_ratings": True,
    "human_listening_result": False,
    "vendor_or_source_reported": True,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Evaluate codec-integrated neural postfilters (Opus 1.5 LACE/NoLACE) with decoder features instead of a generic PCM filter",
        "evidence_gap": "The only local codec-postfilter row is a generic low-pass on \u00b5-law-decoded PCM; LACE/NoLACE are source-reported and were not staged, built, invoked, rights-reviewed or scored.",
        "follow_up_ids": ["SDK-OPUS-1-5-LACE", "SDK-OPUS-1-5-NOLACE"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a codec-integrated postfilter execution; the linked feasibility rows are bounded scoping leads, not capabilities.",
    },
    {
        "id": "G02",
        "actionable_gap": "Cover real transform codecs (MP3/AAC/Opus), tandem coding and jitter artifacts",
        "evidence_gap": "The pilot isolates 8-bit \u00b5-law and a non-standard 4-bit stress proxy at 8 kHz; no transform codec, tandem encode or jitter condition exists.",
        "follow_up_ids": ["SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers real transform-codec artifacts; the linked \u00b5-law research-control row owns only the proxy and the foundation row owns evidence rules.",
    },
    {
        "id": "G03",
        "actionable_gap": "Establish whether classic decoder noise shaping, deemphasis or state-aware postfilters help beyond a fixed low-pass",
        "evidence_gap": "The classic family is represented by one low-pass postfilter; no noise-shaping, deemphasis or decoder-state-aware filter was executed, and the low-pass harms 8-bit output while gaining only 0.28 dB on the 4-bit proxy.",
        "follow_up_ids": ["SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers decoder noise shaping or deemphasis; the linked research-control row owns the existing low-pass proxy only.",
    },
    {
        "id": "G04",
        "actionable_gap": "Stage and evaluate the codec-latent SE-NAC enhancement family",
        "evidence_gap": "SE-NAC is a census entry with released checkpoints; no code, weights, license review, decoded-speech cohort or local output exists.",
        "follow_up_ids": ["SDK-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a locally evaluated codec-latent enhancer; the linked feasibility row is a scoping lead, not an enabled processor or checkpoint.",
    },
    {
        "id": "G05",
        "actionable_gap": "Evaluate URGENT 2026 universal enhancement baselines on a codec-degraded stratum",
        "evidence_gap": "URGENT BSRNN is blocked for local CPU and checkpoint reasons; BSRNN-Flow and TF-GridNet URGENT 2025 are considered only, and no codec-artifact stratum was scored.",
        "follow_up_ids": ["SDK-URGENT-BSRNN", "SDK-URGENT-BSRNN-FLOW", "SDK-TF-GRIDNET-URGENT-2025-BASELINE"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a codec-stratified URGENT result; the linked feasibility rows own general enhancement scoping only.",
    },
    {
        "id": "G06",
        "actionable_gap": "Keep packet-loss concealment and redundancy separate from codec-artifact restoration",
        "evidence_gap": "The evaluated Opus 1.4 PLC and considered deep PLC/DRED/Lyra rows solve erasure concealment; no overlap with post-decode artifact reduction was measured, and the \u00b5-law condition has no packet loss.",
        "follow_up_ids": ["SDK-OPUS-DEEP-PLC", "SDK-OPUS-DRED", "SDK-LYRA-II-V2-CODEC-PLC"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner mixes concealment with artifact restoration; the linked feasibility rows own the adjacent RST-04 scope, not this category.",
    },
    {
        "id": "G07",
        "actionable_gap": "Freeze a rights-qualified paired decoded-speech cohort across real codecs and bitrates",
        "evidence_gap": "Fixtures are deterministic \u00b5-law proxies on 12 CC BY-NC EARS clips; no rights-qualified paired cohort with real encodes, held-out speakers or encoder-setting manifests exists.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers a rights-qualified codec cohort; linked research-control and foundation rows own manifests and evidence rules.",
    },
    {
        "id": "G08",
        "actionable_gap": "Run independent blinded listening and intelligibility/content analysis",
        "evidence_gap": "No human rating exists; the pilot reports SI-SDR, RMSE and STOI only, so intelligibility and naturalness after codec-artifact processing remain unmeasured.",
        "follow_up_ids": [
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-DNSMOS-P-835-AND-DNSMOS-C",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner collected RST-03 ratings; linked research-control rows own listening design, preservation scoring and model-free quality proxies, not a result.",
    },
    {
        "id": "G09",
        "actionable_gap": "Measure decoder-plus-postfilter content, availability, latency and memory on the target runtime",
        "evidence_gap": "Only offline block metrics exist; no callback-path, decoder-buffer, algorithmic-delay, memory or device timing was measured for a codec postfilter.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has device or decoder timing evidence; linked foundation rows own lifecycle/timing and exact-head acceptance rules.",
    },
    {
        "id": "G10",
        "actionable_gap": "Define an opt-in provider intake and public exposure path for a codec postfilter",
        "evidence_gap": "The \u00b5-law proxy is a research-control adapter; no provider descriptor, installed-archive comparison, default selection or independent review exists.",
        "follow_up_ids": ["SDK-FND-PROVIDER", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has provider intake; linked foundation rows own provider boundaries and exact-head evidence.",
    },
    {
        "id": "G11",
        "actionable_gap": "Verify codec I/O, container and sample-format compatibility for the evaluation harness",
        "evidence_gap": "Codec reads and writes rely on external libraries; TorchAudio/TorchCodec compatibility for the LLVC path is partial, and no frozen codec I/O matrix backs the pilot.",
        "follow_up_ids": [
            "SDK-TORCHAUDIO-TORCHCODEC-AND-SOUNDFILE-COMPATIBILITY-FOR-LLVC",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner covers a codec I/O compatibility matrix for this survey; the linked implementation row owns the LLVC tooling boundary only.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-OPUS-1-5-LACE", "title": "Opus 1.5 LACE", "mode": "feasibility"},
    {"task_id": "SDK-OPUS-1-5-NOLACE", "title": "Opus 1.5 NoLACE", "mode": "feasibility"},
    {"task_id": "SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER", "title": "\u00b5-law codec proxy and low-pass postfilter", "mode": "research-control"},
    {"task_id": "SDK-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY", "title": "SE-NAC codec-latent enhancement family", "mode": "feasibility"},
    {"task_id": "SDK-URGENT-BSRNN", "title": "URGENT BSRNN", "mode": "feasibility"},
    {"task_id": "SDK-URGENT-BSRNN-FLOW", "title": "URGENT BSRNN-Flow", "mode": "feasibility"},
    {"task_id": "SDK-TF-GRIDNET-URGENT-2025-BASELINE", "title": "TF-GridNet URGENT 2025 baseline", "mode": "feasibility"},
    {"task_id": "SDK-OPUS-DEEP-PLC", "title": "Opus deep PLC", "mode": "feasibility"},
    {"task_id": "SDK-OPUS-DRED", "title": "Opus DRED", "mode": "feasibility"},
    {"task_id": "SDK-LYRA-II-V2-CODEC-PLC", "title": "Lyra II / V2 codec PLC", "mode": "feasibility"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-DNSMOS-P-835-AND-DNSMOS-C", "title": "DNSMOS P.835 and DNSMOS-C", "mode": "research-control"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "mode": "foundation"},
    {"task_id": "SDK-TORCHAUDIO-TORCHCODEC-AND-SOUNDFILE-COMPATIBILITY-FOR-LLVC", "title": "TorchAudio, TorchCodec and SoundFile compatibility for LLVC", "mode": "implementation"},
]

ALLOWED_LINK_MODES = (
    "feasibility",
    "research-control",
    "foundation",
    "external-adapter",
    "implementation",
)

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified paired decoded-speech cohort across real codecs with frozen encoder settings, metadata and clean reference"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent blinded listening and intelligibility/content analysis, not SI-SDR/STOI only"},
    {"id": "RG-03", "blocked": True, "requirement": "Pinned target-device decoder-plus-postfilter content/availability timing, memory, latency and deadline evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Task-matched codec-integrated neural postfilters and generic neural baselines under a locked runtime"},
    {"id": "RG-05", "blocked": True, "requirement": "Exact approved reference parity at a frozen codec revision and settings"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **RST-03 — Codec-artifact restoration** |",
        "A codec-integrated method may require information unavailable to a generic PCM filter.",
    ],
    "research/category_survey/sources.md": [
        "| S30 | [Opus 1.5 neural enhancement and loss recovery](https://opus-codec.org/demo/opus-1.5/) | acoustics | direct |",
        "| S45 | [URGENT 2026 distortion taxonomy](https://urgent-challenge.github.io/urgent2026/track1/) | root | direct |",
    ],
    "research/distortion_restoration_20261028.md": [
        "| RST-03 | 8-bit µ-law at 8 kHz and a stronger 4-bit µ-law proxy | Decoded input, low-pass decoder postfilter |",
        "| 8-bit µ-law codec proxy | Decoded input | 37.99 dB SI-SDR | Postfilter falls to 33.12 dB |",
        "| 4-bit µ-law stress proxy | Low-pass decoder postfilter | 16.71 dB SI-SDR | +0.28 dB vs decoded input; STOI is effectively unchanged (0.8749 vs 0.8751) |",
        "The 4-bit µ-law case is a stress proxy, not a standard codec. The codec run does not cover MP3/AAC/Opus transform coding, tandem coding or jitter.",
        "avoid generic postfiltering when the codec is unknown. For Opus, evaluate the codec-integrated LACE/NoLACE neural postfilters",
        "The neural and codec-integrated candidates were researched but not run.",
    ],
    "research/noise_suppression_candidate_census.md": [
        "| **SE-NAC codec-latent enhancement family** |",
        "| **URGENT BSRNN / BSRNN-Flow** |",
        "| **TF-GridNet URGENT 2025 baseline** |",
    ],
    "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md": [
        "Status: **evaluated**, as a bounded RST-04 engineering screen.",
        "| Isolated 10% | Opus PLC | 2.39 (0.97, 3.91) | 0.913 | 0.1272 | 0.00153 |",
        "The intact 24-kbit/s Opus decode averaged SI-SDR 5.44 dB",
    ],
    "research/voice-enhancement-20261101/evaluation_records.md": [
        "µ-law proxy and packet-loss corruption",
        "Lyra II and learned/generative PLC/BWE candidates remain unevaluated or blocked.",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Restoration | Freeze corruption, metadata and corresponding clean/audio packet baseline. Stratify by degradation, erasure burst and bandwidth. Report discrete concealment/validity, decoded intervals, task-specific quality and bounds on output peaks and timing. |",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md": [
        "> **No Opus claim.**",
        "a waveform surrogate of the *idea* of decoder erasure concealment, not",
    ],
    "docs/task-evidence/speex-mdf-residual-postfilter/README.md": [
        "postfilter stays optional, default OFF and",
        "0.968517` to `0.687357`",
        "15.675997 dB` to `15.590018 dB`",
    ],
    "docs/task-evidence/quality-impairment-taxonomy/README.md": [
        "At threshold 0.35 the reported clip occupancy was 2.74% and POCS gained only 0.25 dB SI-SDR",
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
        raise MapError("RST-03 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("RST-03 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F10 / RST-03 is not unique")
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
            raise MapError("legacy backlog mismatch: F10/RST-03/%s" % key)


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
    classes = [row["class"] for row in COMPARISON_INPUTS]
    classes += [row["outcome_class"] for row in HISTORICAL_EXECUTIONS]
    pilot = any("pilot_not_reproduced" in c for c in classes)
    reference = any("codec_proxy_reference_baseline" in c for c in classes)
    stress = any("stress_proxy_not_standard_codec" in c for c in classes)
    adjacent_plc = any("adjacent_packet_loss" in c for c in classes)
    adjacent_echo = any("adjacent_echo_residual" in c for c in classes)
    predictive = any("predictive" in c for c in classes)
    prepared = any("prepared" in row["status"].lower() for row in ASSETS)
    reported = any(c.startswith(("source_reported", "external_")) for c in classes)
    if EVIDENCE_CLASSES["historical_pilot_means_not_reproduced"] != pilot:
        raise MapError("pilot-means evidence class does not match mapped records")
    if EVIDENCE_CLASSES["codec_proxy_reference_identity_historical_local"] != reference:
        raise MapError("codec-reference evidence class does not match mapped records")
    if EVIDENCE_CLASSES["historical_local_stress_proxy_not_standard_codec"] != stress:
        raise MapError("stress-proxy evidence class does not match mapped records")
    if EVIDENCE_CLASSES["adjacent_packet_loss_historical_local"] != adjacent_plc:
        raise MapError("adjacent-PLC evidence class does not match mapped records")
    if EVIDENCE_CLASSES["adjacent_echo_residual_historical_local"] != adjacent_echo:
        raise MapError("adjacent-echo evidence class does not match mapped records")
    if EVIDENCE_CLASSES["unpaired_predictive_historical_local"] != predictive:
        raise MapError("unpaired-predictive evidence class does not match mapped records")
    if EVIDENCE_CLASSES["prepared_listening_without_ratings"] != prepared:
        raise MapError("prepared-listening evidence class does not match assets")
    if EVIDENCE_CLASSES["vendor_or_source_reported"] != reported:
        raise MapError("source-reported evidence class does not match records")
    if EVIDENCE_CLASSES["codec_integrated_neural_postfilter_local"] is not False:
        raise MapError("codec-integrated neural postfilter was not locally executed")
    if EVIDENCE_CLASSES["human_listening_result"] is not False:
        raise MapError("no RST-03 human listening result exists")


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
    link_ids = {gap["id"] for gap in GAPS}
    used = set()
    for gap in GAPS:
        if not isinstance(gap.get("follow_up_ids"), list) or not gap["follow_up_ids"]:
            raise MapError("gap has no linked board task: " + gap["id"])
        for task_id in gap["follow_up_ids"]:
            if task_id not in known:
                raise MapError("gap links an unlisted board task: %s/%s" % (gap["id"], task_id))
            used.add(task_id)
        if gap.get("feasibility_task_exists"):
            modes = {next(t["mode"] for t in BOARD_LINKS if t["task_id"] == tid) for tid in gap["follow_up_ids"]}
            if "feasibility" not in modes:
                raise MapError("gap claims a feasibility follow-up without one: " + gap["id"])
        elif not gap.get("owner_note"):
            raise MapError("gap without feasibility task has no owner note: " + gap["id"])
        if not gap.get("owner_note"):
            raise MapError("gap has no owner note: " + gap["id"])
    orphan = sorted(known - used)
    if orphan:
        raise MapError("board link is not referenced by any gap: " + ",".join(orphan))
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
        if not linked_gaps:
            raise MapError("board link is not referenced by any gap: " + link["task_id"])
        if by_id[link["task_id"]].get("title") != link["title"]:
            raise MapError("linked board title changed: " + link["task_id"])
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
