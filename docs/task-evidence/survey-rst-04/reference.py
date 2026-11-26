# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-RST-04.

This module builds a bounded taxonomy/comparison evidence map for the
packet-loss concealment and gap-recovery category (inventory category
``RST-04``). It reads only pinned, read-only documents from the enclosing
``audioml`` workspace and the SDK worktree. It does not load audio, weights,
codecs, runtimes, media or the network, and it does not register, expose,
enable or qualify any processor.

All curated records below are documentation mappings, not new measurements.
Historical local-screen, pilot or source-reported values are transcribed
verbatim from the pinned documents and labelled with their original scope.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

SCHEMA_ID = "audio-sdk/task-evidence-survey-map/0.1"
TASK = "SDK-SURVEY-RST-04"
TITLE = "Review coverage for Packet-loss concealment and gap recovery"
CATEGORY_ID = "RST-04"
LEGACY_FAMILY = "F10"
BRANCH = "swarm/SDK-SURVEY-RST-04"
BASE_COMMIT = "39b8885da4fc3ef8e27becf5df5f0658da3baf65"
PROFILE = "Restoration"
COMPONENT = "packet-loss-concealment-evidence-map"
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
# verifies media/codec assets that are not present in this task directory.
SOURCE_PINS: Dict[str, str] = {
    "REALTIME_COMPONENT_CANDIDATES.md": "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "adapters/opus-plc/adapter.json": "a36dd6798d3e9f273c7705fea6d11d888680e633a4b4c41c00e20242f45765ae",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md": "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "reports/distortion-restoration/20261028-synthetic-screen.json": "87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece",
    "research/category_registry.json": "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md": "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/distortion_restoration_20261028.md": "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md": "79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "src/audioml_eval/distortion_restoration.py": "c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f",
}

# SDK-worktree-relative public-boundary and evidence pins. They are read only
# to prove that no public surface was touched and that historical rows remain
# grounded in the merged task-local packages.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/autoregressive-plc/README.md": "a391565993a4f2439b6e2d584923dd0a812ceeef75c9954c08215df108ff79df",
    "docs/task-evidence/elastic-pcm-packets/README.md": "15ebaa6b2b7768faa5c1bd2fc45b900db7f71d49b7ad1292685263555953e742",
    "docs/task-evidence/linear-interpolation-plc/README.md": "5102676797554c3e6bc83207a848d35b72783bead5eac13ad60c5a16bd940742",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md": "ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df",
    "docs/task-evidence/pitch-period-repeat-plc/README.md": "8fb323ffd7ce59c361ac1078d7c434b1b3c0b5f088d9a7d07ae5b2278cfa3ea9",
    "docs/task-evidence/survey-rst-01/README.md": "5888f8745720a90a6926ccbd158597e5804c0fc1fb937918f26da495b053d68a",
    "docs/task-evidence/survey-rst-03/README.md": "8b7262eacdeec26dab1e311ac5ceefcc2e4aef116176073dba13e555a866fc12",
    "docs/task-evidence/zero-fill-plc/README.md": "f1e702efd42ee93ae5402d42ec9f5498f759deb01fa3cb08f6b436f6f92998c4",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Distortion restoration",
    "name": "Packet-loss concealment and gap recovery",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Estimate missing temporal content.",
    "method_families": {
        "classic": "Prediction, extrapolation and repetition",
        "ml": "Neural prediction/resynthesis; redundancy-assisted recovery as a separate group",
    },
    "input_output": "Audio history + loss state, optionally redundancy/future packets \u2192 recovered audio",
    "live_or_comparison_boundary": (
        "Track which information is available. Plausible gap filling does not "
        "prove recovery of the original words."
    ),
    "source_ids": ["S30", "S41"],
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
            "opus-deep-plc",
            "opus-dred",
            "opus-1-5-lace",
            "opus-1-5-nolace",
        ],
        "gap_ids": ["G02", "G04"],
        "finding": (
            "The official Opus 1.5 material documents neural loss recovery and "
            "redundancy features (deep PLC, DRED and LACE/NoLACE enhancement), "
            "none enabled by default. It defines candidate scope only: no "
            "compatible Opus 1.5 build, decoder feature stream, pinned encoder "
            "settings, packet trace, redundancy/bitrate budget, checkpoint "
            "review or local output exists in the reviewed records. The "
            "evaluated Opus 1.4 standard decoder PLC row is a distinct baseline "
            "with its own pinned runtime and limits."
        ),
    },
    {
        "source_id": "S41",
        "title": "WebRTC NetEq documentation",
        "url": "https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_coding/neteq/g3doc/index.md",
        "access_scope": "direct",
        "mapped_components": [
            "webrtc-neteq",
            "opus-packetization-fec-dtx-and-comfort-noise",
        ],
        "gap_ids": ["G01", "G05"],
        "finding": (
            "The NetEq documentation describes receive-side jitter buffering, "
            "adaptive playout, reordering/duplication handling and "
            "expand/merge/accelerate concealment decisions. No NetEq source, "
            "build, captured packet trace, playout decision log, device timing "
            "or integrated receive path exists in the reviewed records. The "
            "local elastic-parity fixture is a separate bounded packet model, "
            "not NetEq."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": "Conventional waveform baselines: zero-fill, hold and linear interpolation",
        "components": ["zero-fill-plc", "linear-interpolation-plc"],
        "gap_ids": ["G06", "G07"],
        "status": "evaluated_synthetic_local_only",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": "Pitch-period repetition and waveform extrapolation",
        "components": ["pitch-period-repeat-plc"],
        "gap_ids": ["G06"],
        "status": "evaluated_synthetic_local_only",
    },
    {
        "family_id": "MF-C3",
        "branch": "classic",
        "family": "Autoregressive forward prediction from received history",
        "components": ["autoregressive-plc"],
        "gap_ids": ["G06", "G08"],
        "status": "evaluated_synthetic_local_only",
    },
    {
        "family_id": "MF-C4",
        "branch": "classic",
        "family": "Codec-native decoder concealment (Opus 1.4 standard decoder PLC)",
        "components": ["opus-1-4-standard-decoder-plc"],
        "gap_ids": ["G01", "G06", "G08"],
        "status": "evaluated_historical_codec_screen_plus_synthetic_surrogate",
    },
    {
        "family_id": "MF-C5",
        "branch": "classic",
        "family": "Redundancy-assisted recovery and receive-side gap recovery (separate group)",
        "components": [
            "opus-dred",
            "opus-packetization-fec-dtx-and-comfort-noise",
            "webrtc-neteq",
        ],
        "gap_ids": ["G01", "G04", "G05", "G08"],
        "status": "source_reported_or_considered_not_run_locally",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": "Neural prediction/resynthesis PLC (generative or codec-latent)",
        "components": ["complex-bin2bin-generative-plc", "lyra-ii-v2-codec-plc"],
        "gap_ids": ["G02", "G03", "G06"],
        "status": "blocked_or_considered_not_staged",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": "Codec-integrated neural loss recovery (Opus deep PLC, DRED and LACE/NoLACE)",
        "components": ["opus-deep-plc", "opus-1-5-lace", "opus-1-5-nolace"],
        "gap_ids": ["G02", "G04", "G06"],
        "status": "source_reported_only_not_built_or_run",
    },
]

COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "zero-fill-plc", "evidence_status": "evaluated", "task": "SDK-ZERO-FILL-PLC"},
    {"component_id": "linear-interpolation-plc", "evidence_status": "evaluated", "task": "SDK-LINEAR-INTERPOLATION-PLC"},
    {"component_id": "pitch-period-repeat-plc", "evidence_status": "evaluated", "task": "SDK-PITCH-PERIOD-REPEAT-PLC"},
    {"component_id": "autoregressive-plc", "evidence_status": "evaluated", "task": "SDK-AUTOREGRESSIVE-PLC"},
    {"component_id": "opus-1-4-standard-decoder-plc", "evidence_status": "evaluated", "task": "SDK-OPUS-1-4-STANDARD-DECODER-PLC"},
    {"component_id": "complex-bin2bin-generative-plc", "evidence_status": "blocked", "task": "SDK-COMPLEX-BIN2BIN-GENERATIVE-PLC"},
    {"component_id": "lyra-ii-v2-codec-plc", "evidence_status": "blocked", "task": "SDK-LYRA-II-V2-CODEC-PLC"},
    {"component_id": "opus-deep-plc", "evidence_status": "considered", "task": "SDK-OPUS-DEEP-PLC"},
    {"component_id": "opus-dred", "evidence_status": "considered", "task": "SDK-OPUS-DRED"},
    {"component_id": "opus-packetization-fec-dtx-and-comfort-noise", "evidence_status": "considered", "task": "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE"},
    {"component_id": "webrtc-neteq", "evidence_status": "considered", "task": "SDK-WEBRTC-NETEQ"},
    {"component_id": "opus-1-5-lace", "evidence_status": "considered", "task": "SDK-OPUS-1-5-LACE"},
    {"component_id": "opus-1-5-nolace", "evidence_status": "considered", "task": "SDK-OPUS-1-5-NOLACE"},
]

COMPARISON_INPUTS: List[Dict[str, Any]] = [
    {
        "id": "CI-1",
        "class": "historical_local_real_audio_screen_not_reproduced",
        "input": "12 EARS clips packetized as stateful 20 ms Opus frames at 24 kbit/s with deterministic 10% isolated and ~16.7% two-packet burst erasures and same-mask waveform controls",
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
        "boundary": "Real EARS audio under a synthetic deterministic loss script; no captured network trace, FEC, DRED, stereo, reordering, jitter buffer, longer burst or listening; not rerun by this survey.",
    },
    {
        "id": "CI-2",
        "class": "historical_local_paired_synthetic_clean_transparency",
        "input": "Frozen 250-frame (40,000-sample) zero-fill/hold/linear synthetic cohort with a 17-frame explicit erasure mask and clean identity reference",
        "source_pin": "docs/task-evidence/zero-fill-plc/README.md",
        "boundary": "Generated stimuli at 16 kHz/160-sample frames; exact supplied mask; identity is bit-exact on valid content only; not rerun by this survey.",
    },
    {
        "id": "CI-3",
        "class": "historical_local_paired_synthetic",
        "input": "Frozen 250-frame linear-interpolation synthetic cohort with a 9-frame explicit erasure mask and zero-fill baseline",
        "source_pin": "docs/task-evidence/linear-interpolation-plc/README.md",
        "boundary": "Generated stimuli at 16 kHz/160-sample frames; 5-frame host scheduling buffer; exact supplied mask; not rerun by this survey.",
    },
    {
        "id": "CI-4",
        "class": "historical_local_paired_synthetic",
        "input": "Frozen 250-frame pitch-period-repeat synthetic cohort with an 11-frame explicit erasure mask, voiced/unvoiced/silence strata and zero-fill/linear/AR baselines",
        "source_pin": "docs/task-evidence/pitch-period-repeat-plc/README.md",
        "boundary": "Generated stimuli at 16 kHz/160-sample frames; causal pitch estimator; fallback zero-fill counted explicitly; not rerun by this survey.",
    },
    {
        "id": "CI-5",
        "class": "historical_local_paired_synthetic",
        "input": "Frozen 250-frame autoregressive synthetic cohort with a 9-frame explicit erasure mask and zero-fill/linear baselines",
        "source_pin": "docs/task-evidence/autoregressive-plc/README.md",
        "boundary": "Generated stimuli at 16 kHz/160-sample frames; order-16 all-pole predictor; clamped-sample and solver fallback counted; not rerun by this survey.",
    },
    {
        "id": "CI-6",
        "class": "historical_local_paired_synthetic",
        "input": "Frozen 250-frame synthetic decoder-PLC-style surrogate cohort with a 17-frame explicit erasure mask and zero-fill/hold/linear baselines",
        "source_pin": "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md",
        "boundary": "Synthetic waveform surrogate only; no Opus library, binary, weight, codec stream or vendor result is invoked; not rerun by this survey.",
    },
    {
        "id": "CI-7",
        "class": "historical_local_packet_parity_synthetic",
        "input": "Task-local timestamped packet fixture with one XOR parity packet: a single erasure is recovered and a two-packet burst is rejected as unrecoverable",
        "source_pin": "docs/task-evidence/elastic-pcm-packets/README.md",
        "boundary": "Model-only packet/parity fixture; PCM push/pull and packet recovery stay separate; no codec, network, jitter buffer or device path; not rerun by this survey.",
    },
    {
        "id": "CI-8",
        "class": "historical_local_pilot_not_reproduced",
        "input": "12-clip EARS RST-04 pilot at isolated 10% and 17% burst packet loss with zero-fill, linear, pitch-repeat and AR controls",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Pilot means transcribed with original scoring and scope; distinct from the codec-matched agent-opus screen and not pooled with it; not rerun by this survey.",
    },
    {
        "id": "CI-9",
        "class": "source_reported_only",
        "input": "Opus 1.5 neural enhancement and loss-recovery documentation (deep PLC, DRED, LACE/NoLACE)",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documented candidate scope only; no compatible build, checkpoint, packet stream, redundancy budget or local output.",
    },
    {
        "id": "CI-10",
        "class": "source_reported_not_run",
        "input": "WebRTC NetEq receive-side jitter-buffer, adaptive-playout and concealment documentation",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Documentation scope only; no NetEq source/build, trace replay, playout log or device timing.",
    },
]

CONTROLS: List[Dict[str, Any]] = [
    {
        "id": "CT-1",
        "name": "clean identity / no-loss delivery",
        "role": "Task-matched identity control; valid content is bit-exact and SI-SDR is undefined with reason exact_reconstruction, never invented.",
        "source_pin": "docs/task-evidence/zero-fill-plc/README.md",
    },
    {
        "id": "CT-2",
        "name": "zero-fill and hold baselines",
        "role": "Degraded/adverse controls on the same erasure masks; the 12-clip screen found zero fill competitive on SI-SDR, so no method is assumed superior.",
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
    },
    {
        "id": "CT-3",
        "name": "linear interpolation baseline",
        "role": "Established task-matched waveform baseline bridging the last good sample to the next good frame.",
        "source_pin": "docs/task-evidence/linear-interpolation-plc/README.md",
    },
    {
        "id": "CT-4",
        "name": "pitch-period repetition",
        "role": "Causal extrapolation control that repeats a detected period with decay; explicit zero-fill fallback when unvoiced or silent.",
        "source_pin": "docs/task-evidence/pitch-period-repeat-plc/README.md",
    },
    {
        "id": "CT-5",
        "name": "autoregressive prediction",
        "role": "Causal all-pole forward-prediction control with explicit fallback and clamped-sample accounting.",
        "source_pin": "docs/task-evidence/autoregressive-plc/README.md",
    },
    {
        "id": "CT-6",
        "name": "synthetic decoder-PLC-style surrogate",
        "role": "Waveform surrogate with fixed decay gains; deliberately not Opus, DRED, Lyra or any codec runtime.",
        "source_pin": "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md",
    },
    {
        "id": "CT-7",
        "name": "admission and adverse rejection envelope",
        "role": "Missing, short, wrong-shape, zero-length, nonfinite, bad-padding, stale-epoch, duplicate, out-of-order, future, after-final and over-burst frames are rejected without changing stream state.",
        "source_pin": "docs/task-evidence/zero-fill-plc/README.md",
    },
    {
        "id": "CT-8",
        "name": "single-erasure XOR parity and explicit multi-erasure failure",
        "role": "Redundancy-assisted control: a single packet is recovered with its original timestamp; a two-packet burst is rejected rather than guessed.",
        "source_pin": "docs/task-evidence/elastic-pcm-packets/README.md",
    },
    {
        "id": "CT-9",
        "name": "concealed-slot validity accounting",
        "role": "Concealed output slots carry result flag 4 and valid_count=0 and are excluded from valid content and sample conservation.",
        "source_pin": "docs/task-evidence/zero-fill-plc/README.md",
    },
    {
        "id": "CT-10",
        "name": "supplied erasure mask and packet timeline",
        "role": "Every local cohort supplies the exact loss mask; loss detection from arrivals, late packets or redundancy is untested.",
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
    },
]

ASSETS: List[Dict[str, Any]] = [
    {
        "asset": "EARS 12-clip packet-erasure research audio",
        "class": "research_audio",
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
        "status": "Marked CC BY-NC 4.0 in the local dataset record; bytes not staged or re-verified in this task.",
    },
    {
        "asset": "Task-local frozen synthetic PLC fixtures (zero-fill, linear, pitch, AR and decoder-style surrogate)",
        "class": "generated_fixture",
        "source_pin": "docs/task-evidence/zero-fill-plc/README.md",
        "status": "Generated stimuli and explicit masks at 16 kHz/160-sample frames; no external media or download.",
    },
    {
        "asset": "Task-local elastic PCM and single-erasure parity fixture",
        "class": "generated_fixture",
        "source_pin": "docs/task-evidence/elastic-pcm-packets/README.md",
        "status": "Model-only packet/parity fixture; no codec stream or network capture.",
    },
    {
        "asset": "Bundled libopus 1.4 dylib provenance",
        "class": "external_binary_provenance",
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
        "status": "Historical provenance only; the exact path is absent at authoring time and nothing is vendored, linked, invoked or reused here.",
    },
    {
        "asset": "Opus 1.5 and WebRTC NetEq documentation leads (S30, S41)",
        "class": "source_and_metadata_only",
        "source_pin": "research/category_survey/sources.md",
        "status": "Direct documentation access only; no code, checkpoint, runtime, trace or rights review staged.",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "12-clip EARS codec-matched packet-erasure screen (Opus 1.4 PLC versus four waveform controls)",
        "outcome_class": "historical_local_real_audio_screen_not_reproduced",
        "component_ids": [
            "opus-1-4-standard-decoder-plc",
            "zero-fill-plc",
            "linear-interpolation-plc",
            "pitch-period-repeat-plc",
            "autoregressive-plc",
        ],
        "scope": (
            "12 EARS anechoic clips, stateful 20 ms Opus frames at 24 kbit/s, "
            "deterministic 10% isolated and ~16.7% two-packet bursts starting "
            "at packet 3, FEC disabled, 104-sample codec delay compensated for "
            "offline scoring; no network trace, reordering, jitter buffer, "
            "DRED, listening or phone measurement; not rerun by this survey."
        ),
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
        "values": {
            "clips": 12,
            "codec_bitrate_kbit_s": 24,
            "isolated_loss_fraction": 0.10,
            "burst_loss_fraction_approx": 0.167,
            "codec_delay_samples": 104,
            "intact_opus_si_sdr_db": 5.44,
            "intact_opus_si_sdr_ci_low_db": 3.03,
            "intact_opus_si_sdr_ci_high_db": 7.98,
            "intact_opus_stoi": 0.998,
            "isolated_opus_plc_si_sdr_db": 2.39,
            "isolated_opus_plc_stoi": 0.913,
            "isolated_opus_plc_concealed_rmse": 0.1272,
            "isolated_zero_fill_si_sdr_db": 3.37,
            "isolated_zero_fill_stoi": 0.872,
            "isolated_zero_fill_concealed_rmse": 0.1022,
            "isolated_linear_si_sdr_db": 2.42,
            "isolated_linear_stoi": 0.860,
            "isolated_linear_concealed_rmse": 0.1270,
            "isolated_pitch_si_sdr_db": 2.70,
            "isolated_pitch_stoi": 0.927,
            "isolated_pitch_concealed_rmse": 0.1283,
            "isolated_ar_si_sdr_db": 3.48,
            "isolated_ar_stoi": 0.875,
            "isolated_ar_concealed_rmse": 0.1021,
            "burst_opus_plc_si_sdr_db": 0.92,
            "burst_opus_plc_stoi": 0.848,
            "burst_opus_plc_concealed_rmse": 0.1388,
            "burst_zero_fill_si_sdr_db": 2.15,
            "burst_zero_fill_stoi": 0.760,
            "burst_zero_fill_concealed_rmse": 0.1137,
            "burst_linear_si_sdr_db": 0.64,
            "burst_linear_stoi": 0.755,
            "burst_linear_concealed_rmse": 0.1441,
            "burst_pitch_si_sdr_db": 0.64,
            "burst_pitch_stoi": 0.875,
            "burst_pitch_concealed_rmse": 0.1511,
            "burst_ar_si_sdr_db": 2.23,
            "burst_ar_stoi": 0.763,
            "burst_ar_concealed_rmse": 0.1136,
            "opus_plc_median_rtf": 0.00153,
            "zero_fill_median_rtf": 0.000019,
            "linear_median_rtf": 0.000084,
            "pitch_median_rtf": 0.00258,
            "ar_median_rtf": 0.00574,
            "worker_peak_rss_median_mb": 144.0,
        },
    },
    {
        "id": "HE-2",
        "label": "12-clip EARS RST-04 pilot means (AR and pitch-repeat controls)",
        "outcome_class": "historical_local_pilot_not_reproduced",
        "component_ids": ["autoregressive-plc", "pitch-period-repeat-plc"],
        "scope": (
            "12 clips per task; isolated 10% and 17% burst loss; pilot means "
            "with the report's original scoring and no human evaluation; "
            "distinct from the codec-matched Opus screen and not pooled with "
            "it; not rerun by this survey."
        ),
        "source_pin": "research/distortion_restoration_20261028.md",
        "values": {
            "isolated_loss_fraction": 0.10,
            "burst_loss_fraction": 0.17,
            "isolated_ar_si_sdr_db": 10.35,
            "isolated_ar_damaged_region_rmse": 0.1136,
            "isolated_pitch_stoi": 0.9207,
            "burst_ar_si_sdr_db": 7.43,
            "burst_ar_damaged_region_rmse": 0.1185,
            "burst_pitch_stoi": 0.8690,
        },
    },
    {
        "id": "HE-3",
        "label": "Zero-fill synthetic cohort with hold and linear controls",
        "outcome_class": "historical_local_paired_synthetic_clean_transparency",
        "component_ids": ["zero-fill-plc"],
        "scope": (
            "250 frames = 40,000 samples, seed 20261126, 17 erased frames "
            "(2,720 samples), exact supplied mask, generated stimuli at "
            "16 kHz/160-sample frames; no real speech, codec, listening or "
            "device timing; not rerun by this survey."
        ),
        "source_pin": "docs/task-evidence/zero-fill-plc/README.md",
        "values": {
            "cohort_frames": 250,
            "cohort_samples": 40000,
            "erased_frames": 17,
            "erased_samples": 2720,
            "valid_content_samples": 37280,
            "zero_fill_si_sdr_db": 11.79041,
            "zero_fill_stoi": 0.876922,
            "zero_fill_concealed_rmse": 0.020877,
            "hold_si_sdr_db": 11.907973,
            "hold_stoi": 0.876645,
            "hold_concealed_rmse": 0.020525,
            "linear_si_sdr_db": 11.692601,
            "linear_stoi": 0.874788,
            "linear_concealed_rmse": 0.021025,
            "identity_bit_identical_valid_content": True,
        },
    },
    {
        "id": "HE-4",
        "label": "Linear-interpolation synthetic cohort with zero-fill baseline",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["linear-interpolation-plc", "zero-fill-plc"],
        "scope": (
            "250 frames = 40,000 samples, 9 erased frames (1,440 samples), "
            "exact supplied mask, generated stimuli at 16 kHz/160-sample "
            "frames; no real speech, codec, listening or device timing; not "
            "rerun by this survey."
        ),
        "source_pin": "docs/task-evidence/linear-interpolation-plc/README.md",
        "values": {
            "cohort_frames": 250,
            "cohort_samples": 40000,
            "erased_frames": 9,
            "erased_samples": 1440,
            "valid_content_samples": 38560,
            "linear_si_sdr_db": 11.820617,
            "linear_stoi": 0.949594,
            "linear_concealed_rmse": 0.027524,
            "zero_fill_si_sdr_db": 10.983909,
            "zero_fill_stoi": 0.95102,
            "zero_fill_concealed_rmse": 0.030219,
            "paired_delta_si_sdr_db": 0.836708,
            "paired_delta_stoi": -0.001426,
        },
    },
    {
        "id": "HE-5",
        "label": "Pitch-period-repeat synthetic cohort with three baselines",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": [
            "pitch-period-repeat-plc",
            "zero-fill-plc",
            "linear-interpolation-plc",
            "autoregressive-plc",
        ],
        "scope": (
            "250 frames = 40,000 samples, 11 erased frames (1,760 samples), "
            "voiced/unvoiced/silence strata, exact supplied mask, generated "
            "stimuli at 16 kHz/160-sample frames; no real speech, codec, "
            "listening or device timing; not rerun by this survey."
        ),
        "source_pin": "docs/task-evidence/pitch-period-repeat-plc/README.md",
        "values": {
            "cohort_frames": 250,
            "cohort_samples": 40000,
            "erased_frames": 11,
            "erased_samples": 1760,
            "valid_content_samples": 38240,
            "pitch_si_sdr_db": 22.139532,
            "pitch_stoi": 0.851298,
            "pitch_concealed_rmse": 0.101429,
            "zero_fill_si_sdr_db": 13.589343,
            "zero_fill_stoi": 0.807333,
            "linear_si_sdr_db": 12.7835,
            "linear_stoi": 0.859246,
            "ar_si_sdr_db": 13.781399,
            "ar_stoi": 0.83635,
            "pitch_minus_zero_fill_si_sdr_db": 8.550189,
        },
    },
    {
        "id": "HE-6",
        "label": "Autoregressive synthetic cohort with zero-fill and linear baselines",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": ["autoregressive-plc", "zero-fill-plc", "linear-interpolation-plc"],
        "scope": (
            "250 frames = 40,000 samples, 9 erased frames (1,440 samples), "
            "exact supplied mask, generated stimuli at 16 kHz/160-sample "
            "frames; no real speech, codec, listening or device timing; not "
            "rerun by this survey."
        ),
        "source_pin": "docs/task-evidence/autoregressive-plc/README.md",
        "values": {
            "cohort_frames": 250,
            "cohort_samples": 40000,
            "erased_frames": 9,
            "erased_samples": 1440,
            "valid_content_samples": 38560,
            "ar_si_sdr_db": 13.145847,
            "ar_stoi": 0.953606,
            "ar_concealed_rmse": 0.023853,
            "zero_fill_si_sdr_db": 11.891468,
            "zero_fill_stoi": 0.95201,
            "linear_si_sdr_db": 12.157196,
            "linear_stoi": 0.950965,
            "ar_minus_zero_fill_si_sdr_db": 1.254379,
        },
    },
    {
        "id": "HE-7",
        "label": "Synthetic decoder-PLC-style surrogate cohort with waveform controls",
        "outcome_class": "historical_local_paired_synthetic",
        "component_ids": [
            "opus-1-4-standard-decoder-plc",
            "zero-fill-plc",
            "linear-interpolation-plc",
        ],
        "scope": (
            "250 frames = 40,000 samples, 17 erased frames (2,720 samples), "
            "exact supplied mask, generated stimuli at 16 kHz/160-sample "
            "frames; the candidate is a waveform surrogate, not Opus; no "
            "codec runtime, real speech, listening or device timing; not "
            "rerun by this survey."
        ),
        "source_pin": "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md",
        "values": {
            "cohort_frames": 250,
            "cohort_samples": 40000,
            "erased_frames": 17,
            "erased_samples": 2720,
            "valid_content_samples": 37280,
            "surrogate_si_sdr_db": 11.089522,
            "surrogate_stoi": 0.946857,
            "surrogate_concealed_rmse": 0.021665,
            "zero_fill_si_sdr_db": 11.417861,
            "zero_fill_stoi": 0.854584,
            "hold_si_sdr_db": 11.576436,
            "hold_stoi": 0.853881,
            "linear_si_sdr_db": 11.165178,
            "linear_stoi": 0.842026,
            "opus_runtime_invoked": False,
        },
    },
]

REPORTED_OUTCOMES: List[Dict[str, Any]] = [
    {
        "id": "RO-1",
        "class": "source_reported",
        "claim": "Opus 1.5 documents deep PLC, DRED redundancy and LACE/NoLACE neural enhancement for loss recovery",
        "boundary": "Official documentation only; no compatible build, checkpoint, packet trace, redundancy budget, local output or parity result exists.",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "id": "RO-2",
        "class": "source_reported",
        "claim": "WebRTC NetEq provides receive-side jitter buffering, adaptive playout and packet-loss concealment decisions",
        "boundary": "Documentation only; no NetEq source/build, trace replay, playout log, device timing or integrated path was run.",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "id": "RO-3",
        "class": "source_reported_local_screen",
        "claim": "On the 12-clip EARS screen, Opus 1.4 PLC did not dominate zero-fill or AR on SI-SDR and traded STOI differently by loss pattern",
        "boundary": "n=12 exploratory screen with overlapping CIs; codec-plus-loss scores are not denoising-style quality scores; no captured trace, phone or listening result.",
        "source_pin": "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md",
    },
    {
        "id": "RO-4",
        "class": "source_reported_pilot_conclusion",
        "claim": "The RST-04 pilot found AR best by SI-SDR/RMSE and pitch repeat best by STOI, with no method dominating every measure",
        "boundary": "Small pilot means with original scoring and no human evaluation; not pooled with the codec-matched screen.",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "id": "RO-5",
        "class": "source_reported_local_parity",
        "claim": "A single packet erasure is recoverable from one XOR parity packet while a two-packet burst is an explicit failure",
        "boundary": "Bounded model fixture; not codec FEC/DRED, not a network trace and not an integrated jitter-buffer result.",
        "source_pin": "docs/task-evidence/elastic-pcm-packets/README.md",
    },
    {
        "id": "RO-6",
        "class": "source_reported_inventory_blocked",
        "claim": "Complex-Bin2bin and Lyra II codec PLC candidates are blocked for exact checkpoint/runtime and packetized loss-trace reasons",
        "boundary": "Inventory disposition only; waveform proxies are not these candidates and no local output exists.",
        "source_pin": "audio-benchmark-platform/plan/INVENTORY.json",
    },
]

EVIDENCE_CLASSES: Dict[str, bool] = {
    "paired_synthetic_historical_local": True,
    "historical_local_real_audio_screen_not_reproduced": True,
    "historical_pilot_means_not_reproduced": True,
    "clean_transparency_diagnostic_historical_local": True,
    "packet_parity_synthetic_historical_local": True,
    "vendor_or_source_reported": True,
    "unpaired_predictive_historical_local": False,
    "human_listening_result": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
    "prepared_listening_without_ratings": False,
}

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": "Restoration",
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "frozen_corruption_and_metadata": "CI-1..CI-8 freeze erasure masks, burst plans, clean references and 16 kHz/160-sample geometry; source-reported leads do not.",
        "erasure_strata": "CI-2..CI-6 isolate 9-17 frame erasures with voiced/unvoiced/silence and 2-4 frame bursts; CI-1 uses 10% isolated and ~16.7% two-packet patterns.",
        "matched_damaged_baseline": "zero-fill, hold and linear interpolation on the same masks; CI-7 adds single-erasure parity recovery and explicit multi-erasure failure.",
        "decoded_intervals_and_concealment": "fixtures report concealed frames, result flag 4, valid_count=0, finite drain and excluded valid content; no codec-native packet trace exists.",
        "task_specific_quality": "CI-1 SI-SDR/STOI/RMSE screen; CI-2..CI-6 local synthetic SI-SDR/STOI and lost-region RMSE; no listening or WER.",
        "validity_and_peak_bounds": "nonfinite, missing, short, duplicate, stale, reordered, future, over-burst and closed inputs are rejected; outputs are finite and bounded; no real-codec state is exercised.",
        "timing": "CI-1 unpaced median RTF and process RSS only; no target-device deadline, jitter buffer or end-to-end content/availability timing.",
        "listening": "none; no ratings, WER or consented listeners.",
    },
    "blocked": [
        "Rights-qualified paired real-speech loss cohort with captured or frozen packet traces and clean reference",
        "Independent blinded listening/WER and content-preservation analysis",
        "Pinned target-device content/availability timing, jitter-buffer, memory and deadline evidence",
        "Codec-native PLC and neural/redundancy baselines under a locked runtime",
        "Exact approved reference parity at a frozen revision and settings",
        "Opt-in provider intake and independent exact-head review",
        "Explicit public default selection approval",
        "Release approval; DEFER remains in force until every gate is closed",
    ],
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Exercise captured packet-loss traces with reordering, duplication, jitter and varied burst lengths",
        "evidence_gap": "All local cohorts use fixed synthetic erasure masks; the 12-clip screen uses deterministic 10% and two-packet bursts with no reordering, duplication, jitter or captured RTP trace.",
        "follow_up_ids": ["SDK-PIPE-RECEIVE", "SDK-WEBRTC-NETEQ", "SDK-FND-ELASTIC"],
        "feasibility_task_exists": True,
        "owner_note": "The linked pipeline, feasibility and foundation rows are scoping leads; none has a captured trace or a qualified receive path.",
    },
    {
        "id": "G02",
        "actionable_gap": "Evaluate codec-integrated neural loss recovery (Opus deep PLC, DRED, LACE/NoLACE) with a pinned compatible build",
        "evidence_gap": "S30 documents the methods, but no compatible Opus 1.5 build, decoder feature stream, packet trace, redundancy budget, checkpoint review or local output exists; Opus 1.4 standard PLC and the synthetic surrogate are different baselines.",
        "follow_up_ids": ["SDK-OPUS-DEEP-PLC", "SDK-OPUS-DRED", "SDK-OPUS-1-5-LACE", "SDK-OPUS-1-5-NOLACE"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a locally executed Opus 1.5 neural loss-recovery build; the linked feasibility rows are bounded scoping leads, not capabilities.",
    },
    {
        "id": "G03",
        "actionable_gap": "Stage neural generative or codec-latent PLC with an exact checkpoint and rights review",
        "evidence_gap": "Complex-Bin2bin and Lyra II are blocked or considered with no exact checkpoint, codec-aligned packet-loss benchmark, rights review or local output.",
        "follow_up_ids": ["SDK-COMPLEX-BIN2BIN-GENERATIVE-PLC", "SDK-LYRA-II-V2-CODEC-PLC"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a locally staged neural generative PLC; the linked feasibility rows are scoping leads, not enabled processors or checkpoints.",
    },
    {
        "id": "G04",
        "actionable_gap": "Measure redundancy-assisted recovery as a separate group with bitrate, redundancy and latency accounting",
        "evidence_gap": "The elastic packet fixture recovers only one erasure from XOR parity and rejects a two-packet burst; Opus FEC, DRED and LACE are source-reported or considered only, and no encoded stream, redundancy budget or extra-delay measurement exists.",
        "follow_up_ids": ["SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE", "SDK-OPUS-DRED", "SDK-FND-ELASTIC"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has an integrated encoded-stream redundancy measurement; the linked rows own contract, feasibility and packet-feature scope only.",
    },
    {
        "id": "G05",
        "actionable_gap": "Evaluate receive-side jitter buffering and adaptive playout (NetEq) separately from decoder PLC",
        "evidence_gap": "S41 documents NetEq, but no NetEq source/build, packet trace, playout decision, merge/expand/accelerate behavior or device timing exists; the local adapter uses a fixed 5-frame scheduling buffer, not a jitter buffer.",
        "follow_up_ids": ["SDK-WEBRTC-NETEQ", "SDK-PIPE-RECEIVE"],
        "feasibility_task_exists": True,
        "owner_note": "No component owner has a NetEq or playout execution; the linked feasibility and pipeline rows are scoping leads, not integrated receive behavior.",
    },
    {
        "id": "G06",
        "actionable_gap": "Freeze a rights-qualified paired real-speech cohort and collect listening/WER evidence",
        "evidence_gap": "The only real-audio execution is a 12-clip CC BY-NC EARS screen with no listening or WER; all other local scores are generated fixtures. Plausible gap filling is not recovery of the original words.",
        "follow_up_ids": [
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has a rights-qualified listening or WER result; the linked research-control rows own cohort manifests, preservation scoring and listening design only.",
    },
    {
        "id": "G07",
        "actionable_gap": "Measure target-device content/availability timing, memory and deadline behavior",
        "evidence_gap": "Only unpaced Python wall-clock RTF and process RSS are recorded; no phone, paced host, jitter-buffer delay or end-to-end deadline measurement exists.",
        "follow_up_ids": ["SDK-FND-TIMING"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has target-device timing evidence; the linked foundation row owns the timing acceptance rules, not a measured device result.",
    },
    {
        "id": "G08",
        "actionable_gap": "Carry end-to-end valid-versus-concealed accounting and source timestamps through an integrated receive path",
        "evidence_gap": "Local fixtures mark concealed slots with flag 4 and valid_count=0 and verify finite drain, but no integrated packet-to-PCM pipeline maps source timestamps, distinguishes concealed from valid decoded content end-to-end, or preserves sample conservation.",
        "follow_up_ids": ["SDK-PIPE-RECEIVE", "SDK-FND-ELASTIC", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has end-to-end concealed/valid accounting; the linked pipeline and foundation rows own implementation scope and evidence rules only.",
    },
    {
        "id": "G09",
        "actionable_gap": "Complete opt-in provider intake and independent exact-head review before any release",
        "evidence_gap": "No provider is compiled, registered, packaged or enabled, and no installed-v0, ABI, descriptor, registry, default, shared-build or CI change exists.",
        "follow_up_ids": ["SDK-FND-PROVIDER", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No component owner has provider intake; the linked foundation rows own provider boundaries and exact-head evidence.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-PIPE-RECEIVE", "title": "Packet loss recovery and receive conditioning", "mode": "pipeline"},
    {"task_id": "SDK-WEBRTC-NETEQ", "title": "WebRTC NetEq", "mode": "feasibility"},
    {"task_id": "SDK-FND-ELASTIC", "title": "Variable-count playback and packet timing", "mode": "foundation"},
    {"task_id": "SDK-OPUS-DEEP-PLC", "title": "Opus deep PLC", "mode": "feasibility"},
    {"task_id": "SDK-OPUS-DRED", "title": "Opus DRED", "mode": "feasibility"},
    {"task_id": "SDK-OPUS-1-5-LACE", "title": "Opus 1.5 LACE", "mode": "feasibility"},
    {"task_id": "SDK-OPUS-1-5-NOLACE", "title": "Opus 1.5 NoLACE", "mode": "feasibility"},
    {"task_id": "SDK-COMPLEX-BIN2BIN-GENERATIVE-PLC", "title": "Complex-Bin2bin generative PLC", "mode": "feasibility"},
    {"task_id": "SDK-LYRA-II-V2-CODEC-PLC", "title": "Lyra II / V2 codec PLC", "mode": "feasibility"},
    {"task_id": "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE", "title": "Opus packetization, FEC, DTX and comfort noise", "mode": "feasibility"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "mode": "foundation"},
]

ALLOWED_LINK_MODES = (
    "feasibility",
    "research-control",
    "foundation",
    "external-adapter",
    "implementation",
    "pipeline",
)

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified paired real-speech loss cohort with captured or frozen packet traces and clean reference"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent blinded listening/WER and content-preservation analysis, not plausibility only"},
    {"id": "RG-03", "blocked": True, "requirement": "Pinned target-device content/availability timing, jitter-buffer, memory and deadline evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Codec-native PLC and neural/redundancy baselines under a locked runtime"},
    {"id": "RG-05", "blocked": True, "requirement": "Exact approved reference parity at a frozen revision and settings"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **RST-04 — Packet-loss concealment and gap recovery** |",
        "Track which information is available. Plausible gap filling does not prove recovery of the original words.",
    ],
    "research/category_survey/sources.md": [
        "| S30 | [Opus 1.5 neural enhancement and loss recovery](https://opus-codec.org/demo/opus-1.5/) | acoustics | direct |",
        "| S41 | [WebRTC NetEq documentation](https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_coding/neteq/g3doc/index.md) | root | direct |",
    ],
    "research/distortion_restoration_20261028.md": [
        "| RST-04 | Isolated 10% packet loss and 17% burst loss | Zero fill, linear interpolation, pitch-period repetition, autoregressive prediction |",
        "AR: 10.35 dB SI-SDR, 0.1136 damaged-region RMSE; pitch repeat: 0.9207 STOI",
        "DRED specifically addresses burst losses using transmitted redundancy",
        "packet concealment benefits from codec state or redundant packets",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "Freeze corruption, metadata and corresponding clean/audio packet baseline. Stratify by degradation, erasure burst and bandwidth.",
    ],
    "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md": [
        "Status: **evaluated**, as a bounded RST-04 engineering screen.",
        "| Isolated 10% | Opus PLC | 2.39 (0.97, 3.91) | 0.913 | 0.1272 | 0.00153 |",
        "| Two-packet bursts | Opus PLC | 0.92 (-0.40, 2.25) | 0.848 | 0.1388 | 0.00159 |",
        "It processed 12 evenly spaced, 4-second-max mono EARS anechoic speech clips at 16 kHz",
    ],
    "REALTIME_COMPONENT_CANDIDATES.md": [
        "| Standard Opus 1.4 decoder PLC | Packet-loss concealment | Locally evaluated with stateful 20 ms packets and deterministic erasures; median RTF about 0.0015.",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/zero-fill-plc/README.md": [
        "Zero fill is the simplest deterministic baseline",
        "A 4-frame maximum burst and 8-call drain cap are",
    ],
    "docs/task-evidence/linear-interpolation-plc/README.md": [
        "a linear ramp from the last received good sample to the first sample of the next",
        "No SDK source file is changed to enable this; no new public flag is implied.",
    ],
    "docs/task-evidence/pitch-period-repeat-plc/README.md": [
        "when voiced, the last detected period is repeated cyclically",
    ],
    "docs/task-evidence/autoregressive-plc/README.md": [
        "The AR reference is a causal, model-free all-pole forward predictor",
    ],
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md": [
        "> **No Opus claim.**",
        "candidate is causal pitch-period repetition with a fixed decay envelope",
        "adapter/report/audit/inventory values are **provenance context only**",
    ],
    "docs/task-evidence/elastic-pcm-packets/README.md": [
        "One packet erasure is recovered from parity with the exact original timestamp",
        "a two-packet burst is `rejected_unrecoverable`",
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
        raise MapError("RST-04 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("RST-04 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F10 / RST-04 is not unique")
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
            raise MapError("legacy backlog mismatch: F10/RST-04/%s" % key)


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
            raise MapError("historical execution is not marked unrerun: " + row["id"])


def _check_evidence_classes() -> None:
    combined = [row["class"] for row in COMPARISON_INPUTS]
    combined += [row["outcome_class"] for row in HISTORICAL_EXECUTIONS]
    expected = {
        "paired_synthetic_historical_local": any("paired_synthetic" in c for c in combined),
        "historical_local_real_audio_screen_not_reproduced": any("real_audio_screen" in c for c in combined),
        "historical_pilot_means_not_reproduced": any("pilot_not_reproduced" in c for c in combined),
        "clean_transparency_diagnostic_historical_local": any("clean_transparency" in c for c in combined),
        "packet_parity_synthetic_historical_local": any("packet_parity" in c for c in combined),
        "vendor_or_source_reported": any(c.startswith("source_reported") for c in combined),
    }
    for key, value in expected.items():
        if EVIDENCE_CLASSES.get(key) is not value:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in (
        "unpaired_predictive_historical_local",
        "human_listening_result",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "prepared_listening_without_ratings",
    ):
        if EVIDENCE_CLASSES.get(key) is not False:
            raise MapError("unsupported evidence class is true: " + key)


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
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "decision": DECISION,
            "readiness": READINESS,
            "qualifies": False,
            "processor_exposure": False,
            "missing_result_promoted": False,
        },
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
    if report["qualification"]["status"] != QUALIFICATION_STATUS:
        raise MapError("qualification object changed")
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
