# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence-map reference for SDK-SURVEY-RST-02.

This module builds a bounded taxonomy/comparison evidence map for the bandwidth
extension and audio super-resolution category (inventory category ``RST-02``).
It reads only pinned, read-only documents from the enclosing ``audioml``
workspace and the SDK worktree. It does not load audio, weights, runtimes,
media or the network, and it does not register, expose, enable or qualify any
processor.

All curated records below are documentation mappings, not new measurements.
Historical local-pilot or source-reported values are transcribed verbatim from
the pinned documents and labelled with their original scope. Resampling and
rate conversion are mapped only as an adjacent boundary: they do not recover
missing high-frequency content and are never counted as bandwidth extension.
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
TASK = "SDK-SURVEY-RST-02"
TITLE = "Review coverage for Bandwidth extension and audio super-resolution"
CATEGORY_ID = "RST-02"
LEGACY_FAMILY = "F10"
BRANCH = "swarm/SDK-SURVEY-RST-02"
BASE_COMMIT = "2a475defe0d0d6ff4fed3c0044c1aa2566292552"
PROFILE = "Restoration"
COMPONENT = "bandwidth-extension-super-resolution-evidence-map"
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
    "research/task_backlog.json": "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "src/audioml_eval/distortion_restoration.py": "c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f",
}

# SDK-worktree-relative public-boundary pins. They are read only to prove that
# no public surface was touched; no header is copied, edited or generated.
WORKTREE_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md": "9f91d406909fe2f9fa7cfd4b954639d081a12ab16005be761707b6f5c998f40c",
    "docs/task-evidence/quality-impairment-taxonomy/README.md": "77ad10fae3e41a06adad6cee377616c73dd8d7d458a76c9297aa55d837afcbe5",
    "docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md": "7bcf299b29fee342daa7bae0f141e59d86680e16189e88c34a71d2c0e4fa2e75",
}

BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"

CATEGORY_FACTS: Dict[str, Any] = {
    "id": CATEGORY_ID,
    "group": "Distortion restoration",
    "name": "Bandwidth extension and audio super-resolution",
    "scope": "discovered_extension",
    "output_kind": "waveform",
    "purpose": "Estimate missing frequency content in bandwidth-limited speech.",
    "method_families": {
        "classic": "Envelope/excitation extension; classical family code search pending",
        "ml": "Vocoder and generative/diffusion restoration",
    },
    "input_output": "Band-limited audio \u2192 broader-band estimate",
    "live_or_comparison_boundary": (
        "Resampling alone does not recover missing information; generated "
        "content must be checked for fidelity."
    ),
    "source_ids": ["S29", "S45"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
}

CATEGORY_SCOPE: Dict[str, Any] = {
    "code": "RST",
    "meaning": "Distortion restoration",
    "category_id": CATEGORY_ID,
    "bandwidth_extension_and_super_resolution_only": True,
    "not_declipping_category": "RST-01",
    "not_codec_artifact_category": "RST-03",
    "not_packet_loss_concealment_category": "RST-04",
    "resampling_is_not_bandwidth_extension": True,
    "rate_conversion_is_not_super_resolution": True,
    "generated_high_band_is_estimated_not_recovered": True,
    "note": (
        "Declipping is RST-01, codec-artifact restoration is RST-03 and "
        "packet-loss concealment is RST-04. Resampling and rate conversion "
        "change sample rate or bandwidth without recovering missing "
        "high-frequency information, so they are named only as an adjacent "
        "boundary and are not pooled into an RST-02 bandwidth-extension claim."
    ),
}

BWE_BOUNDARY: Dict[str, Any] = {
    "bandwidth_limited_input_to_broader_band_estimate": True,
    "resampling_alone_recovers_missing_high_band": False,
    "rate_conversion_is_not_bandwidth_extension": True,
    "generated_content_must_be_checked_for_fidelity": True,
    "high_band_fidelity_established": False,
    "content_preservation_established": False,
    "blind_cutoff_estimation_present": False,
    "ml_weights_present": False,
    "ml_runtime_present": False,
    "codec_integration_present": False,
    "human_listening_result_present": False,
    "independent_heldout_benchmark_present": False,
    "target_device_timing_present": False,
    "universal_restoration_is_not_bandwidth_extension": True,
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S29",
        "title": "NU-Wave 2 bandwidth extension implementation",
        "url": "https://github.com/maum-ai/nuwave2",
        "access_scope": "direct",
        "mapped_components": ["nu-wave-2"],
        "gap_ids": ["G01"],
        "finding": (
            "The catalogued source is a direct link to the NU-Wave 2 project, "
            "a bandwidth-conditioned generative upsampling family that targets "
            "different input rates and generates 48 kHz audio. The pinned "
            "research record states that the authors provide official code and "
            "checkpoints but those weights are not staged locally. No pinned "
            "revision, checkpoint digest, rights review, matched band-limited "
            "cohort or local high-band fidelity result exists in this task."
        ),
    },
    {
        "source_id": "S45",
        "title": "URGENT 2026 distortion taxonomy",
        "url": "https://urgent-challenge.github.io/urgent2026/track1/",
        "access_scope": "direct",
        "mapped_components": [
            "gap-urgenet",
            "urgent-bsrnn",
            "urgent-bsrnn-flow",
            "tf-gridnet-urgent-2025-baseline",
        ],
        "gap_ids": ["G06"],
        "finding": (
            "The catalogued source is a direct challenge taxonomy page, not a "
            "runnable candidate, pinned implementation, checkpoint or matched "
            "dataset. It places bandwidth restoration among several universal "
            "enhancement distortions, so it provides challenge-level context "
            "only. The local records state that no URGENT source, checkpoint or "
            "runtime is staged and the large GPU-oriented checkpoint is not "
            "available for this M1 CPU evaluation."
        ),
    },
]

METHOD_FAMILIES: List[Dict[str, Any]] = [
    {
        "family_id": "MF-C1",
        "branch": "classic",
        "family": (
            "Classical envelope/excitation extension and low-band spectrum-copy "
            "proxy (exact envelope/excitation code search pending)"
        ),
        "components": ["spectrum-copy-bandwidth-extension"],
        "gap_ids": ["G07"],
        "status": "historical_local_pilot_negative_baseline_only",
    },
    {
        "family_id": "MF-C2",
        "branch": "classic",
        "family": (
            "Rate conversion, interpolation and resampling boundary (adjacent, "
            "not bandwidth extension and not super-resolution)"
        ),
        "components": [
            "numpy-scipy-soundfile-wav-and-resampling",
            "typed-frame-resample-and-drift-diagnostics",
            "speex-resampler",
            "libsamplerate",
            "libsoxr",
        ],
        "gap_ids": ["G12"],
        "status": "adjacent_local_tooling_not_bandwidth_extension",
    },
    {
        "family_id": "MF-M1",
        "branch": "ml",
        "family": (
            "Bandwidth-conditioned generative upsampling and diffusion "
            "super-resolution (named source lead S29 NU-Wave 2)"
        ),
        "components": ["nu-wave-2"],
        "gap_ids": ["G01"],
        "status": "source_reported_direct_access_weights_not_staged",
    },
    {
        "family_id": "MF-M2",
        "branch": "ml",
        "family": (
            "Codec-integrated neural band extension inside the decoder "
            "(Opus 1.5 LACE and NoLACE)"
        ),
        "components": ["opus-1-5-lace", "opus-1-5-nolace"],
        "gap_ids": ["G05"],
        "status": "catalogued_codec_integrated_not_run",
    },
    {
        "family_id": "MF-M3",
        "branch": "ml",
        "family": (
            "Diffusion and generative audio super-resolution models "
            "(AudioSR, Vocos-BWE, additional VM-ASR)"
        ),
        "components": [
            "audiosr",
            "vocos-bwe",
            "additional-vm-asr-audio-super-resolution",
        ],
        "gap_ids": ["G02", "G03", "G04"],
        "status": "blocked_no_staged_source_checkpoint_or_adapter",
    },
    {
        "family_id": "MF-M4",
        "branch": "ml",
        "family": (
            "Universal multi-distortion generative enhancement including "
            "bandwidth restoration (named source lead S45 URGENT family)"
        ),
        "components": [
            "gap-urgenet",
            "urgent-bsrnn",
            "urgent-bsrnn-flow",
            "tf-gridnet-urgent-2025-baseline",
        ],
        "gap_ids": ["G06"],
        "status": "challenge_context_not_bandwidth_specific_no_local_material",
    },
    {
        "family_id": "MF-M5",
        "branch": "ml",
        "family": (
            "General neural restoration/resynthesis and vocoder boundary "
            "(not bandwidth-specific, adjacent)"
        ),
        "components": [
            "voicefixer",
            "hifi-gan-vocoder",
            "vocos-vocoder",
            "world-vocoder",
        ],
        "gap_ids": ["G13", "G14"],
        "status": "adjacent_not_bandwidth_specific_not_run",
    },
]

# component_id, evidence_status and inventory task are checked against
# plan/INVENTORY.json. Board status is intentionally excluded: it is mutable.
COMPONENT_CENSUS: List[Dict[str, str]] = [
    {"component_id": "spectrum-copy-bandwidth-extension", "evidence_status": "evaluated", "task": "SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION"},
    {"component_id": "nu-wave-2", "evidence_status": "considered", "task": "SDK-NU-WAVE-2"},
    {"component_id": "opus-1-5-lace", "evidence_status": "considered", "task": "SDK-OPUS-1-5-LACE"},
    {"component_id": "opus-1-5-nolace", "evidence_status": "considered", "task": "SDK-OPUS-1-5-NOLACE"},
    {"component_id": "audiosr", "evidence_status": "blocked", "task": "SDK-AUDIOSR"},
    {"component_id": "vocos-bwe", "evidence_status": "blocked", "task": "SDK-VOCOS-BWE"},
    {"component_id": "additional-vm-asr-audio-super-resolution", "evidence_status": "blocked", "task": "SDK-ADDITIONAL-VM-ASR-AUDIO-SUPER-RESOLUTION"},
    {"component_id": "gap-urgenet", "evidence_status": "blocked", "task": "SDK-GAP-URGENET"},
    {"component_id": "urgent-bsrnn", "evidence_status": "blocked", "task": "SDK-URGENT-BSRNN"},
    {"component_id": "urgent-bsrnn-flow", "evidence_status": "considered", "task": "SDK-URGENT-BSRNN-FLOW"},
    {"component_id": "tf-gridnet-urgent-2025-baseline", "evidence_status": "considered", "task": "SDK-TF-GRIDNET-URGENT-2025-BASELINE"},
    {"component_id": "voicefixer", "evidence_status": "considered", "task": "SDK-VOICEFIXER"},
    {"component_id": "hifi-gan-vocoder", "evidence_status": "considered", "task": "SDK-HIFI-GAN-VOCODER"},
    {"component_id": "vocos-vocoder", "evidence_status": "considered", "task": "SDK-VOCOS-VOCODER"},
    {"component_id": "world-vocoder", "evidence_status": "considered", "task": "SDK-WORLD-VOCODER"},
    {"component_id": "numpy-scipy-soundfile-wav-and-resampling", "evidence_status": "evaluated", "task": "SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING"},
    {"component_id": "typed-frame-resample-and-drift-diagnostics", "evidence_status": "source-local", "task": "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS"},
    {"component_id": "speex-resampler", "evidence_status": "considered", "task": "SDK-SPEEX-RESAMPLER"},
    {"component_id": "libsamplerate", "evidence_status": "considered", "task": "SDK-LIBSAMPLERATE"},
    {"component_id": "libsoxr", "evidence_status": "considered", "task": "SDK-LIBSOXR"},
]

COMPARISON_INPUTS: List[Dict[str, str]] = [
    {
        "id": "CI-1",
        "input": "12 EARS clips degraded by a zero-phase low-pass at 3.5 kHz, 16 kHz mono, at most 4 s, compared as band-limited input versus low-band spectrum-copy extension against the full-band clean waveform",
        "class": "historical_local_pilot_not_reproduced",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Transcribed pilot means only; bytes, per-clip rows and the hidden high band were not rerun by this survey and no listening was performed.",
    },
    {
        "id": "CI-2",
        "input": "Per-clip RST-02 synthetic screen ledger: 12 clips x 2 methods at cutoff=3.5 kHz",
        "class": "historical_local_ledger_provenance_not_reproduced",
        "source_pin": "reports/distortion-restoration/20261028-synthetic-screen.json",
        "boundary": "Provenance ledger only; the rows were not rerun, re-scored or pooled with any other cohort.",
    },
    {
        "id": "CI-3",
        "input": "NU-Wave 2 official code and checkpoints (named source lead S29)",
        "class": "source_reported_direct_access_weights_not_staged",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Direct access to a project page, not a pinned checkout or staged checkpoint; no local output, high-band fidelity or content-preservation result.",
    },
    {
        "id": "CI-4",
        "input": "URGENT 2026 Track 1 universal distortion taxonomy and challenge material (named source lead S45)",
        "class": "source_reported_challenge_context_not_bandwidth_specific",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Challenge-level context only; bandwidth restoration is one distortion among several and no local material, split, runtime or score exists.",
    },
    {
        "id": "CI-5",
        "input": "Opus 1.5 LACE and NoLACE decoder-integrated neural postfilters on genuine low-bitrate traffic",
        "class": "source_reported_codec_integrated_not_run",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Requires a compatible Opus build and packet-level integration; no local codec run or packet evidence is staged.",
    },
    {
        "id": "CI-6",
        "input": "AudioSR, Vocos-BWE and additional VM-ASR super-resolution candidates",
        "class": "external_blocked_no_asset",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Inventory-censused blocked candidates; no pinned code, checkpoint, adapter, candidate output or timing exists.",
    },
    {
        "id": "CI-7",
        "input": "Rate-conversion and resampling tooling fixtures (NumPy/SciPy/SoundFile and typed-frame drift diagnostics)",
        "class": "historical_local_adjacent_rate_conversion",
        "source_pin": "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md",
        "boundary": "Adjacent tooling only; rate conversion changes sample rate or bandwidth and cannot recover missing high-frequency information.",
    },
    {
        "id": "CI-8",
        "input": "Rights-qualified paired band-limited/full-band speech cohort with frozen cutoff and clean high-band reference",
        "class": "missing_required_input_not_present",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "boundary": "Required by the Restoration profile and absent; the 12-clip EARS pilot is small CC BY-NC research media, not a rights-qualified held-out cohort.",
    },
]

CONTROLS: List[Dict[str, str]] = [
    {
        "id": "CT-1",
        "name": "band-limited input identity",
        "role": "Task-matched damaged-input baseline: the 3.5 kHz low-passed signal scored 17.40 dB SI-SDR and 0.9868 STOI in the local pilot.",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "id": "CT-2",
        "name": "low-band spectrum-copy extension (negative control)",
        "role": "Deterministic classical proxy that copies low-band spectrum into the missing high band; it fell to 14.39 dB SI-SDR and 0.9725 STOI on all 12 clips and is rejected.",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "id": "CT-3",
        "name": "full-band clean reference",
        "role": "Upper-bound paired target for BWE scoring; it is the clean waveform, not a generated or band-limited estimate.",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "id": "CT-4",
        "name": "known zero-phase 3.5 kHz cutoff", "role": "Frozen corruption metadata: 2.56% of high-band energy is removed; the cutoff is supplied to the methods and blind cutoff estimation is untested.",
        "source_pin": "reports/distortion-restoration/20261028-synthetic-screen.json",
    },
    {
        "id": "CT-5",
        "name": "resampling / rate conversion alone",
        "role": "Adjacent negative demonstration: changing sample rate or bandwidth does not infer missing high frequencies and is never counted as BWE.",
        "source_pin": "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md",
    },
    {
        "id": "CT-6",
        "name": "nonfinite input adverse case",
        "role": "NaN/Inf input is rejected with no serialized output and cannot count as a pass.",
        "source_pin": "docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md",
    },
    {
        "id": "CT-7",
        "name": "missing, invalid, malformed and empty input",
        "role": "Empty audio, wrong rate/channel, truncated container and missing bytes are explicit rejections; no fallback is written.",
        "source_pin": "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md",
    },
    {
        "id": "CT-8",
        "name": "normative pilot BWE baselines",
        "role": "Defines degrade_bandlimit (zero-phase 8th-order Butterworth at 3.5 kHz) and bwe_spectral_copy (tiled low-band copy with edge taper); read as context, not executed here.",
        "source_pin": "src/audioml_eval/distortion_restoration.py",
    },
]

ASSETS: List[Dict[str, str]] = [
    {
        "asset": "EARS 12-clip band-limited pilot media",
        "class": "research_audio",
        "status": "CC BY-NC 4.0 in the cited research records; bytes are not staged or verified in this task",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "asset": "Task-local generated RST-02 fixtures (zero-phase low-pass and spectrum-copy)",
        "class": "generated_fixture",
        "status": "Deterministic synthetic corruption from clean EARS clips; no external media download",
        "source_pin": "reports/distortion-restoration/20261028-synthetic-screen.json",
    },
    {
        "asset": "NU-Wave 2 source and checkpoints (S29)",
        "class": "source_and_metadata_only",
        "status": "Direct project access; no pinned revision, checkpoint digest, runtime or rights clearance staged",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "URGENT 2026 challenge material (S45)",
        "class": "external_challenge_material",
        "status": "Challenge registration and large GPU use; no local source, checkpoint or split staged",
        "source_pin": "research/category_survey/sources.md",
    },
    {
        "asset": "Opus 1.5 LACE/NoLACE decoder integration",
        "class": "external_codec_build",
        "status": "Requires compatible Opus build and packet-level integration; not staged",
        "source_pin": "research/distortion_restoration_20261028.md",
    },
    {
        "asset": "VCTK v3 prepared listening items",
        "class": "research_audio",
        "status": "Prepared only; zero collected ratings and no playback clearance",
        "source_pin": "docs/task-evidence/quality-impairment-taxonomy/README.md",
    },
    {
        "asset": "Rate-conversion tooling fixtures",
        "class": "generated_fixture",
        "status": "Seeded synthetic signals and pinned optional libraries; adjacent tooling, not bandwidth extension",
        "source_pin": "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "HE-1",
        "label": "12-clip bandwidth-extension pilot at a 3.5 kHz zero-phase cutoff",
        "outcome_class": "historical_local_pilot_not_reproduced",
        "component_ids": ["spectrum-copy-bandwidth-extension"],
        "source_pin": "research/distortion_restoration_20261028.md",
        "values": {
            "clips": 12,
            "methods": 2,
            "sample_rate_hz": 16000,
            "clip_seconds_max": 4,
            "cutoff_hz": 3500,
            "bandlimited_input_si_sdr_db": 17.40,
            "bandlimited_input_stoi": 0.986833,
            "bandlimited_input_rmse": 0.018027,
            "spectral_copy_si_sdr_db": 14.39,
            "spectral_copy_stoi": 0.972459,
            "spectral_copy_rmse": 0.024581,
            "spectral_copy_si_sdr_delta_db": -3.01,
            "removed_high_band_energy_fraction": 0.025621,
        },
        "scope": "12 clips per task, 3.5 kHz cutoff, 2.56% high-band energy removed, no listening; pilot means transcribed, not rerun by this survey.",
    },
    {
        "id": "HE-2",
        "label": "Per-clip RST-02 synthetic screen ledger behind the pilot means",
        "outcome_class": "historical_local_ledger_provenance_not_reproduced",
        "component_ids": ["spectrum-copy-bandwidth-extension"],
        "source_pin": "reports/distortion-restoration/20261028-synthetic-screen.json",
        "values": {
            "rows": 24,
            "clips": 12,
            "methods": 2,
            "severity": "cutoff=3.5kHz",
            "clips_where_copy_beats_bandlimited_input": 0,
            "per_clip_delta_min_db": -6.6233,
            "per_clip_delta_max_db": -0.9144,
        },
        "scope": "Ledger rows are provenance only and are not rerun by this survey; they are not re-scored or pooled with any other cohort.",
    },
    {
        "id": "HE-3",
        "label": "NumPy/SciPy/SoundFile WAV and resampling tooling boundary",
        "outcome_class": "historical_local_adjacent_rate_conversion",
        "component_ids": ["numpy-scipy-soundfile-wav-and-resampling"],
        "source_pin": "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md",
        "values": {
            "signals": 11,
            "wav_float_roundtrips": 11,
            "resampling_cases": 36,
            "target_rates": 6,
            "malformed_input_cases": 5,
            "missing_optional_selections": 3,
            "sdk_runtime_timing_excluded": 1,
        },
        "scope": "Synthetic offline tooling, adjacent rate conversion only; not bandwidth extension, not SDK runtime timing and not rerun by this survey.",
    },
    {
        "id": "HE-4",
        "label": "Typed frame, resample and drift diagnostics boundary",
        "outcome_class": "historical_local_adjacent_rate_conversion",
        "component_ids": ["typed-frame-resample-and-drift-diagnostics"],
        "source_pin": "docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md",
        "values": {
            "source_frames": 4,
            "produced_samples": 800,
            "delivered_valid_samples": 495,
            "declared_delay_samples": 173,
            "measured_delay_samples": 173,
            "controls_passed": 13,
            "max_abs_drift_ppm": 10000,
        },
        "scope": "Model-free synthetic conversion and drift fixture, adjacent rate conversion only; not bandwidth extension and not rerun by this survey.",
    },
]

REPORTED_OUTCOMES: List[Dict[str, str]] = [
    {
        "id": "RO-1",
        "claim": "NU-Wave 2 provides official code and checkpoints for bandwidth-conditioned generative 48 kHz upsampling",
        "class": "source_reported",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Project scope is documented, not locally executed; checkpoints are not staged and high-band fidelity is unmeasured.",
    },
    {
        "id": "RO-2",
        "claim": "URGENT 2026 Track 1 defines a universal distortion taxonomy that includes bandwidth restoration",
        "class": "source_reported_challenge_taxonomy",
        "source_pin": "research/category_survey/sources.md",
        "boundary": "Challenge context only; not bandwidth-specific and no local material, split or score exists.",
    },
    {
        "id": "RO-3",
        "claim": "The local copy-spectrum baseline should be rejected because it harms fidelity",
        "class": "source_reported_pilot_conclusion",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Small 12-clip pilot with one cutoff and no listening; not a general classical-BWE verdict.",
    },
    {
        "id": "RO-4",
        "claim": "AudioSR, Vocos-BWE and additional VM-ASR are identified super-resolution candidates",
        "class": "source_reported_inventory_census",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "Each is unavailable/blocked: no pinned code, checkpoint, adapter, output or timing.",
    },
    {
        "id": "RO-5",
        "claim": "Opus 1.5 LACE and NoLACE are decoder-integrated neural postfilters and are not enabled by default",
        "class": "source_reported",
        "source_pin": "research/distortion_restoration_20261028.md",
        "boundary": "Requires a compatible Opus build and genuine low-bitrate traffic; no local run or packet evidence.",
    },
    {
        "id": "RO-6",
        "claim": "GAP-URGENet and URGENT BSRNN include bandwidth restoration within universal enhancement",
        "class": "source_reported_inventory_census",
        "source_pin": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "boundary": "No URGENT source, checkpoint or runtime is staged; heavy GPU-oriented material is not available on this CPU host.",
    },
]

ACCEPTANCE_PROFILE: Dict[str, Any] = {
    "profile": PROFILE,
    "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    "mapped": {
        "frozen_corruption_and_metadata": "CI-1..CI-3: zero-phase 3.5 kHz low-pass, 16 kHz mono, 4 s maximum and full-band clean reference are recorded per cohort",
        "matched_damaged_baseline": "CT-1 band-limited input identity plus CT-2 low-band spectrum-copy proxy",
        "degradation_and_bandwidth_strata": "CI-1/CI-2 use one 3.5 kHz cutoff only; no multi-cutoff bandwidth matrix exists",
        "task_specific_quality": "HE-1 SI-SDR/STOI pilot means; no new perceptual or generated-band fidelity score",
        "generated_content_fidelity": "CT-3 clean full-band target and BWE boundary; high-band fidelity remains unmeasured",
        "content_preservation": "CT-2 shows the copy proxy loses fidelity; no neural content-preservation result exists",
        "validity_and_peak_bounds": "CT-6/CT-7 reject nonfinite and malformed inputs; the pilot serializes scores only and no task-local output peak bound is recorded",
        "missing_result_accounting": "Blocked and considered candidates are counted explicitly; no missing result qualifies a candidate",
        "listening": "VCTK items prepared with zero ratings; no RST-02 listening result exists",
        "timing": "No target-device content/availability, memory or deadline measurement is mapped",
    },
    "blocked": [
        "Rights-qualified paired band-limited/full-band speech cohort with frozen cutoff and clean high-band reference",
        "Pinned neural bandwidth-extension candidate (NU-Wave 2, AudioSR, Vocos-BWE or Opus LACE/NoLACE) with a locked runtime",
        "High-band fidelity and generated-content preservation analysis",
        "Independent blinded listening on prepared items",
        "Multi-cutoff bandwidth strata and blind cutoff estimation",
        "Target-device content/availability timing, memory and deadline evidence",
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
    "local_ledger_provenance_not_reproduced": True,
    "adjacent_rate_conversion_tooling_historical_local": True,
    "missing_rights_qualified_paired_speech_cohort": True,
    "prepared_listening_without_ratings": True,
    "source_reported_or_inventory_only": True,
    "human_listening_result": False,
    "high_band_fidelity_result": False,
    "content_preservation_result": False,
    "blind_cutoff_estimation_result": False,
    "ml_weights_or_runtime_present": False,
    "ml_local_execution": False,
    "unpaired_predictive_historical_local": False,
    "new_execution_in_this_survey": False,
    "parity_or_qualification_claim": False,
}

GAPS: List[Dict[str, Any]] = [
    {
        "id": "G01",
        "actionable_gap": "Stage NU-Wave 2 at an exact revision and checkpoint, then evaluate 48 kHz bandwidth extension against clean high-band references",
        "evidence_gap": "S29 is a direct project lead, but no pinned source, checkpoint digest, rights review, matched band-limited cohort, high-band fidelity or content-preservation result exists.",
        "follow_up_ids": ["SDK-NU-WAVE-2"],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility row is a scoping lead only; no processor, checkpoint or weight is enabled by this map.",
    },
    {
        "id": "G02",
        "actionable_gap": "Stage AudioSR with a pinned source, model asset and inference adapter",
        "evidence_gap": "The inventory census records AudioSR as blocked: no local checkout, model asset or adapter, and task-matched EARS BWE references have no candidate output.",
        "follow_up_ids": ["SDK-AUDIOSR"],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility row is a scoping lead for acquisition only; no local output or bandwidth-extension result exists.",
    },
    {
        "id": "G03",
        "actionable_gap": "Stage the exact Vocos-BWE model, checkpoint and adapter rather than substituting a generic vocoder",
        "evidence_gap": "No exact Vocos-BWE checkpoint exists locally, and generic vocoder evidence is explicitly not bandwidth extension.",
        "follow_up_ids": ["SDK-VOCOS-BWE"],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility row is a scoping lead bounded to exact model acquisition; no vocoder artifact is promoted to a BWE result.",
    },
    {
        "id": "G04",
        "actionable_gap": "Obtain pinned code, a checkpoint and an adapter for the additional VM-ASR super-resolution model",
        "evidence_gap": "The census records no pinned code, checkpoint or adapter and no local output or timing for the author-reported model.",
        "follow_up_ids": ["SDK-ADDITIONAL-VM-ASR-AUDIO-SUPER-RESOLUTION"],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility row is a scoping lead, not a verified model or an executed comparison.",
    },
    {
        "id": "G05",
        "actionable_gap": "Evaluate Opus 1.5 LACE and NoLACE on genuine low-bitrate traffic with a compatible decoder build",
        "evidence_gap": "Codec-integrated neural band extension needs packet-level integration and genuine low-bitrate traffic; no local codec run is mapped.",
        "follow_up_ids": ["SDK-OPUS-1-5-LACE", "SDK-OPUS-1-5-NOLACE"],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility rows are scoping leads for codec integration scope; no decoder feature is enabled by default here.",
    },
    {
        "id": "G06",
        "actionable_gap": "Stage URGENT 2026 material or pinned URGENT candidates and score bandwidth restoration as one distortion, not as a universal restorer",
        "evidence_gap": "S45 is a challenge taxonomy; no URGENT source, checkpoint or runtime is staged and the heavy GPU candidates are blocked on this CPU host.",
        "follow_up_ids": [
            "SDK-GAP-URGENET",
            "SDK-URGENT-BSRNN",
            "SDK-URGENT-BSRNN-FLOW",
            "SDK-TF-GRIDNET-URGENT-2025-BASELINE",
        ],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility rows are scoping leads only; challenge-level context is not a local BWE result.",
    },
    {
        "id": "G07",
        "actionable_gap": "Retain the negative spectrum-copy comparison and add a task-matched classical envelope/excitation baseline",
        "evidence_gap": "The only local classic BWE execution is a low-band spectrum-copy proxy that loses fidelity; the catalogued envelope/excitation family still has a pending code search and no matched implementation.",
        "follow_up_ids": ["SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated RST-02 classical BWE component owner exists; the linked research-control and foundation rows own the negative comparison and evidence rules only.",
    },
    {
        "id": "G08",
        "actionable_gap": "Freeze a rights-qualified paired band-limited/full-band speech cohort with manifests",
        "evidence_gap": "The local pilot uses 12 CC BY-NC EARS clips; no rights-qualified paired BWE manifest or held-out high-band reference exists.",
        "follow_up_ids": [
            "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
            "SDK-FND-EVIDENCE",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated RST-02 cohort owner exists; the linked research-control and foundation rows own manifest and evidence rules.",
    },
    {
        "id": "G09",
        "actionable_gap": "Run independent blinded listening plus high-band fidelity and generated-content preservation analysis",
        "evidence_gap": "No human rating exists and generated high bands are estimates; the pilot reports SI-SDR/STOI only and VCTK items have zero collected ratings.",
        "follow_up_ids": [
            "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN",
            "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated RST-02 listening owner exists; the linked research-control rows own listening design and preservation scoring, not a result.",
    },
    {
        "id": "G10",
        "actionable_gap": "Measure target-device content, availability, memory and deadline behavior",
        "evidence_gap": "Only offline pilot scores exist; no callback-path, device or paced workload timing is mapped for any BWE or super-resolution method.",
        "follow_up_ids": ["SDK-FND-TIMING", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated RST-02 timing owner exists; the linked foundation rows own acceptance and lifecycle rules.",
    },
    {
        "id": "G11",
        "actionable_gap": "Define an opt-in provider intake and public exposure path",
        "evidence_gap": "All mapped candidates are unregistered developer references; no provider descriptor, installed-archive comparison, default selection or independent review exists.",
        "follow_up_ids": ["SDK-FND-PROVIDER", "SDK-FND-EVIDENCE"],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated RST-02 provider owner exists; the linked foundation rows own provider boundaries and exact-head evidence.",
    },
    {
        "id": "G12",
        "actionable_gap": "Keep rate conversion and resampling outside the bandwidth-extension claim and verify no resampler is accepted as BWE",
        "evidence_gap": "The boundary note states resampling cannot infer missing high frequencies, yet rate-conversion components are the most available local tooling; no acceptance test rejects a resampler as a BWE result.",
        "follow_up_ids": [
            "SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING",
            "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS",
            "SDK-SPEEX-RESAMPLER",
            "SDK-LIBSAMPLERATE",
            "SDK-LIBSOXR",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated RST-02 boundary owner exists; the linked implementation and feasibility rows own rate conversion, which is adjacent and not bandwidth extension.",
    },
    {
        "id": "G13",
        "actionable_gap": "Stage VoiceFixer only as a fair bandwidth-extension comparison with explicit degradation labels",
        "evidence_gap": "VoiceFixer is a general neural restoration/resynthesis lead trained for multiple distortions; no checkpoint, runtime, band-limited cohort or BWE-specific result is mapped.",
        "follow_up_ids": ["SDK-VOICEFIXER"],
        "feasibility_task_exists": True,
        "owner_note": "The linked feasibility row is a scoping lead; general restoration evidence is not promoted to a BWE result.",
    },
    {
        "id": "G14",
        "actionable_gap": "Keep vocoder waveform synthesis distinct from bandwidth extension and require a genuine missing-band input",
        "evidence_gap": "HiFi-GAN, Vocos and WORLD vocoders synthesize waveforms from acoustic features; they do not by themselves estimate missing high-frequency content, and no matched BWE execution exists.",
        "follow_up_ids": [
            "SDK-HIFI-GAN-VOCODER",
            "SDK-VOCOS-VOCODER",
            "SDK-WORLD-VOCODER",
        ],
        "feasibility_task_exists": False,
        "owner_note": "No dedicated RST-02 vocoder owner exists; the linked research-control and feasibility rows own vocoder scope, not bandwidth extension.",
    },
]

# (task id, exact board title, exact board mode). Status is deliberately absent
# because board status is mutable and is not part of this read-only map.
BOARD_LINKS: List[Dict[str, str]] = [
    {"task_id": "SDK-NU-WAVE-2", "title": "NU-Wave 2", "mode": "feasibility"},
    {"task_id": "SDK-OPUS-1-5-LACE", "title": "Opus 1.5 LACE", "mode": "feasibility"},
    {"task_id": "SDK-OPUS-1-5-NOLACE", "title": "Opus 1.5 NoLACE", "mode": "feasibility"},
    {"task_id": "SDK-AUDIOSR", "title": "AudioSR", "mode": "feasibility"},
    {"task_id": "SDK-VOCOS-BWE", "title": "Vocos-BWE", "mode": "feasibility"},
    {"task_id": "SDK-ADDITIONAL-VM-ASR-AUDIO-SUPER-RESOLUTION", "title": "Additional VM-ASR audio super-resolution", "mode": "feasibility"},
    {"task_id": "SDK-GAP-URGENET", "title": "GAP-URGENet", "mode": "feasibility"},
    {"task_id": "SDK-URGENT-BSRNN", "title": "URGENT BSRNN", "mode": "feasibility"},
    {"task_id": "SDK-URGENT-BSRNN-FLOW", "title": "URGENT BSRNN-Flow", "mode": "feasibility"},
    {"task_id": "SDK-TF-GRIDNET-URGENT-2025-BASELINE", "title": "TF-GridNet URGENT 2025 baseline", "mode": "feasibility"},
    {"task_id": "SDK-VOICEFIXER", "title": "VoiceFixer", "mode": "feasibility"},
    {"task_id": "SDK-SPECTRUM-COPY-BANDWIDTH-EXTENSION", "title": "Spectrum-copy bandwidth extension", "mode": "research-control"},
    {"task_id": "SDK-HIFI-GAN-VOCODER", "title": "HiFi-GAN vocoder", "mode": "research-control"},
    {"task_id": "SDK-VOCOS-VOCODER", "title": "Vocos vocoder", "mode": "research-control"},
    {"task_id": "SDK-WORLD-VOCODER", "title": "WORLD vocoder", "mode": "feasibility"},
    {"task_id": "SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING", "title": "NumPy/SciPy/SoundFile WAV and resampling", "mode": "implementation"},
    {"task_id": "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS", "title": "Typed frame / resample and drift diagnostics", "mode": "implementation"},
    {"task_id": "SDK-SPEEX-RESAMPLER", "title": "Speex resampler", "mode": "feasibility"},
    {"task_id": "SDK-LIBSAMPLERATE", "title": "libsamplerate", "mode": "feasibility"},
    {"task_id": "SDK-LIBSOXR", "title": "libsoxr", "mode": "feasibility"},
    {"task_id": "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS", "title": "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests", "mode": "research-control"},
    {"task_id": "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS", "title": "EARS preservation screen and scorer harness", "mode": "research-control"},
    {"task_id": "SDK-AB-BLIND-LISTENING-AND-MUSHRA-STYLE-DESIGN", "title": "AB blind listening and MUSHRA-style design", "mode": "research-control"},
    {"task_id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-TIMING", "title": "Complete fixed-frame lifecycle and timing evidence", "mode": "foundation"},
    {"task_id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "mode": "foundation"},
]

ALLOWED_LINK_MODES = (
    "feasibility",
    "research-control",
    "foundation",
    "external-adapter",
    "implementation",
)

RELEASE_GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "blocked": True, "requirement": "Rights-qualified paired band-limited/full-band speech cohort with frozen cutoff, metadata and clean high-band reference"},
    {"id": "RG-02", "blocked": True, "requirement": "Independent blinded listening plus high-band fidelity and generated-content preservation analysis"},
    {"id": "RG-03", "blocked": True, "requirement": "Pinned target-device content/availability timing, memory and deadline evidence"},
    {"id": "RG-04", "blocked": True, "requirement": "Pinned task-matched neural BWE baseline (NU-Wave 2, AudioSR, Vocos-BWE or Opus LACE/NoLACE) under a locked runtime"},
    {"id": "RG-05", "blocked": True, "requirement": "Exact approved reference parity at a frozen revision and settings"},
    {"id": "RG-06", "blocked": True, "requirement": "Opt-in provider intake and independent exact-head review"},
    {"id": "RG-07", "blocked": True, "requirement": "Explicit public default selection approval"},
    {"id": "RG-08", "blocked": True, "requirement": "Release approval; DEFER remains in force until every gate is closed"},
]

# Literal anchors used to prove that curated numbers and caveats are grounded
# in the pinned documents. They are read, never executed or copied into code.
DOC_ANCHORS: Dict[str, List[str]] = {
    "audio_categories.md": [
        "| **RST-02 — Bandwidth extension and audio super-resolution** |",
        "Resampling alone does not recover missing information; generated content must be checked for fidelity.",
    ],
    "research/category_survey/sources.md": [
        "| S29 | [NU-Wave 2 bandwidth extension implementation](https://github.com/maum-ai/nuwave2) | acoustics | direct |",
        "| S45 | [URGENT 2026 distortion taxonomy](https://urgent-challenge.github.io/urgent2026/track1/) | root | direct |",
        "[2026 Track 1](https://urgent-challenge.github.io/urgent2026/track1/) was directly checked for distortion categories.",
    ],
    "research/distortion_restoration_20261028.md": [
        "A limiter cannot recover clipped peaks, resampling cannot infer missing high frequencies, and packet concealment benefits from codec state or redundant packets.",
        "| RST-02 | Zero-phase low-pass at 3.5 kHz | Band-limited input, low-band spectrum-copy extension |",
        "| Bandwidth extension, 3.5 kHz cutoff | Band-limited input | 17.40 dB SI-SDR | Spectrum-copy extension falls to 14.39 dB |",
        "the local copy-spectrum baseline should be rejected; it harms fidelity.",
        "High-frequency fidelity and content preservation need explicit evaluation because generated bands are estimates.",
    ],
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": [
        "| Restoration | Freeze corruption, metadata and corresponding clean/audio packet baseline. Stratify by degradation, erasure burst and bandwidth. Report discrete concealment/validity, decoded intervals, task-specific quality and bounds on output peaks and timing. |",
    ],
    "research/voice-enhancement-20261101/candidate_matrix.csv": [
        "No local source checkout, model asset or inference adapter",
        "No exact Vocos-BWE model/checkpoint/adapter; generic vocoder evidence is not bandwidth extension.",
        "No pinned code/checkpoint/adapter for the author-reported model",
        "No URGENT source/checkpoint/runtime staged",
    ],
}

WORKTREE_DOC_ANCHORS: Dict[str, List[str]] = {
    "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md": [
        "It is synthetic, optional,",
        "resampling=none",
        "36 resampling cases (6 signals × 6 target rates)",
    ],
    "docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md": [
        "The adapter adds **explicit conversions outside the fixed v0 provider ABI** and",
        "Integer buffering/content delay `D=173` samples (deliberately not a multiple",
        "800 produced = 495 valid + 173 startup non-content + 132 tail non-content.",
    ],
    "docs/task-evidence/quality-impairment-taxonomy/README.md": [
        "the distinct 12-speaker VCTK v3 +5 dB pink-noise packet randomizes raw/Speex/DPDFNet",
        "zero collected ratings",
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
    "historical_real_corpus_transcribed_only": True,
    "real_speech": False,
    "real_corpus": False,
    "real_audio_assets": False,
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
    "missing_document_anchor": "rejected; state unchanged",
    "unknown_board_task": "rejected; state unchanged",
    "gap_without_link_or_reason": "rejected; state unchanged",
    "invalid_payload_type": "rejected; state unchanged",
    "nonfinite_payload_value": "rejected; state unchanged",
}

DISCOVERY: Dict[str, Any] = {
    "classic_component_ids": [
        "spectrum-copy-bandwidth-extension",
        "numpy-scipy-soundfile-wav-and-resampling",
        "typed-frame-resample-and-drift-diagnostics",
        "speex-resampler",
        "libsamplerate",
        "libsoxr",
    ],
    "ml_candidate_ids": [
        "nu-wave-2",
        "opus-1-5-lace",
        "opus-1-5-nolace",
        "audiosr",
        "vocos-bwe",
        "additional-vm-asr-audio-super-resolution",
        "gap-urgenet",
        "urgent-bsrnn",
        "urgent-bsrnn-flow",
        "tf-gridnet-urgent-2025-baseline",
        "voicefixer",
        "hifi-gan-vocoder",
        "vocos-vocoder",
        "world-vocoder",
    ],
    "bandwidth_specific_ml_candidate_ids": [
        "nu-wave-2",
        "opus-1-5-lace",
        "opus-1-5-nolace",
        "audiosr",
        "vocos-bwe",
        "additional-vm-asr-audio-super-resolution",
    ],
    "classic_envelope_excitation_component_present": False,
    "weights_present": False,
    "runtime_present": False,
    "checkpoint_digest_present": False,
    "listener_panel_present": False,
    "heldout_benchmark_present": False,
    "published_method_archive_present": False,
    "codec_integration_present": False,
    "blind_cutoff_detector_present": False,
    "note": (
        "The classic branch has a local negative spectrum-copy proxy and "
        "adjacent rate-conversion tooling but no matched envelope/excitation "
        "implementation. The ML branch is catalogued and blocked or considered: "
        "no weights, runtime, checkpoint digest, codec integration, listener "
        "panel, held-out benchmark or published-method archive is staged, and no "
        "ML candidate was executed."
    ),
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
        raise MapError("RST-02 taxonomy record is not unique")
    for record in (registry_hit[0], inventory_hit[0]):
        for key, expected in CATEGORY_FACTS.items():
            if record.get(key) != expected:
                raise MapError("RST-02 taxonomy mismatch: %s" % key)
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
        raise MapError("legacy family F10 / RST-02 is not unique")
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
            raise MapError("legacy backlog mismatch: F10/RST-02/%s" % key)


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
    classic = next((row for row in METHOD_FAMILIES if row["family_id"] == "MF-C1"), None)
    if classic is None:
        raise MapError("classical envelope/excitation family is missing")
    text = classic["family"].lower()
    if "envelope" not in text or "excitation" not in text or "pending" not in text:
        raise MapError("classical family does not record the pending envelope/excitation search")
    adjacent = [row for row in METHOD_FAMILIES if row["family_id"] == "MF-C2"]
    if len(adjacent) != 1:
        raise MapError("adjacent rate-conversion boundary family is missing")
    adjacent_text = adjacent[0]["family"].lower()
    if "adjacent" not in adjacent_text or "not bandwidth extension" not in adjacent_text:
        raise MapError("rate-conversion family is not labelled adjacent and non-BWE")
    ml_text = " ".join(row["family"].lower() for row in METHOD_FAMILIES if row["branch"] == "ml")
    for token in ("generative", "diffusion", "vocoder", "codec-integrated", "universal"):
        if token not in ml_text:
            raise MapError("catalogued ML family text is incomplete: " + token)


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
    asset_status = " ".join(row["status"] for row in ASSETS).lower()
    reported_classes = " ".join(row["class"] for row in REPORTED_OUTCOMES).lower()
    ml_components = {
        "nu-wave-2",
        "opus-1-5-lace",
        "opus-1-5-nolace",
        "audiosr",
        "vocos-bwe",
        "additional-vm-asr-audio-super-resolution",
        "gap-urgenet",
        "urgent-bsrnn",
        "urgent-bsrnn-flow",
        "tf-gridnet-urgent-2025-baseline",
        "voicefixer",
        "hifi-gan-vocoder",
        "vocos-vocoder",
        "world-vocoder",
    }
    checks = {
        "paired_synthetic_historical_local": "paired_synthetic" in comparison_classes
        or "pilot_not_reproduced" in outcome_classes,
        "historical_pilot_means_not_reproduced": "pilot_not_reproduced" in comparison_classes
        or "pilot_not_reproduced" in outcome_classes,
        "local_ledger_provenance_not_reproduced": "ledger_provenance" in comparison_classes
        or "ledger_provenance" in outcome_classes,
        "adjacent_rate_conversion_tooling_historical_local": "adjacent_rate_conversion" in comparison_classes
        or "adjacent_rate_conversion" in outcome_classes,
        "missing_rights_qualified_paired_speech_cohort": "missing_required_input" in comparison_classes,
        "prepared_listening_without_ratings": "prepared" in asset_status and "zero collected ratings" in asset_status,
        "source_reported_or_inventory_only": "source_reported" in reported_classes
        or "inventory_census" in reported_classes,
        "human_listening_result": "human_listening" in outcome_classes or "listener_result" in outcome_classes,
        "high_band_fidelity_result": "high_band_fidelity" in outcome_classes,
        "content_preservation_result": "content_preservation" in outcome_classes,
        "blind_cutoff_estimation_result": "blind_cutoff" in outcome_classes,
        "ml_weights_or_runtime_present": False,
        "ml_local_execution": any(
            set(row.get("component_ids", ())) & ml_components for row in HISTORICAL_EXECUTIONS
        ),
        "unpaired_predictive_historical_local": "predictive" in outcome_classes
        or "predictive" in comparison_classes,
        "new_execution_in_this_survey": False,
        "parity_or_qualification_claim": False,
    }
    for key, observed in checks.items():
        if EVIDENCE_CLASSES[key] is not observed:
            raise MapError("evidence class does not match mapped records: " + key)
    for key in (
        "human_listening_result",
        "high_band_fidelity_result",
        "content_preservation_result",
        "blind_cutoff_estimation_result",
        "ml_weights_or_runtime_present",
        "ml_local_execution",
        "unpaired_predictive_historical_local",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
    ):
        if EVIDENCE_CLASSES[key] is not False:
            raise MapError("claim is not backed by a mapped record: " + key)


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
    for component_id in DISCOVERY["classic_component_ids"]:
        if component_id not in census:
            raise MapError("classic component is not censused: " + component_id)
    for component_id in DISCOVERY["ml_candidate_ids"]:
        row = census.get(component_id)
        if row is None or row["evidence_status"] not in ("considered", "blocked"):
            raise MapError("ML candidate is not a considered or blocked row: " + component_id)
    for component_id in DISCOVERY["bandwidth_specific_ml_candidate_ids"]:
        if component_id not in DISCOVERY["ml_candidate_ids"]:
            raise MapError("bandwidth-specific ML candidate is not an ML candidate: " + component_id)
    for key in (
        "classic_envelope_excitation_component_present",
        "weights_present",
        "runtime_present",
        "checkpoint_digest_present",
        "listener_panel_present",
        "heldout_benchmark_present",
        "published_method_archive_present",
        "codec_integration_present",
        "blind_cutoff_detector_present",
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
    _check_source_leads()
    _check_method_families()
    _check_historical_execution_components()
    _check_evidence_classes()
    _check_controls_assets()
    _check_discovery()
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
        "bwe_boundary": dict(BWE_BOUNDARY),
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
    if len(report["release_gates"]) != 8:
        raise MapError("release gate count changed")
    if any(gate["blocked"] is not True for gate in report["release_gates"]):
        raise MapError("a release gate is not blocked")
    if any(value is not False for value in report["boundary"].values()):
        raise MapError("boundary is not closed")
    if report["scope"]["task_local_only"] is not True:
        raise MapError("scope is not task-local")
    if report["scope"]["documentation_and_metadata_only"] is not True:
        raise MapError("scope is not documentation-only")
    for key, value in report["scope"].items():
        if key in (
            "task_local_only",
            "documentation_and_metadata_only",
            "no_new_execution",
            "synthetic_only_where_cited",
            "historical_real_speech_transcribed_only",
            "historical_real_corpus_transcribed_only",
        ):
            if value is not True:
                raise MapError("scope flag is not true: " + key)
        elif value is not False:
            raise MapError("scope flag is not false: " + key)
    if report["taxonomy"]["id"] != CATEGORY_ID:
        raise MapError("taxonomy id changed")
    boundary = report["bwe_boundary"]
    for key in (
        "high_band_fidelity_established",
        "content_preservation_established",
        "blind_cutoff_estimation_present",
        "ml_weights_present",
        "ml_runtime_present",
        "codec_integration_present",
        "human_listening_result_present",
        "independent_heldout_benchmark_present",
        "target_device_timing_present",
    ):
        if boundary[key] is not False:
            raise MapError("BWE boundary claim is not closed: " + key)
    if boundary["resampling_alone_recovers_missing_high_band"] is not False:
        raise MapError("resampling recovery claim is not allowed")
    if boundary["generated_content_must_be_checked_for_fidelity"] is not True:
        raise MapError("generated-content fidelity requirement is missing")
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
                if isinstance(value, float) and (
                    value != value or value in (float("inf"), float("-inf")) or not math.isfinite(value)
                ):
                    raise MapError("nonfinite payload value: %s" % key)
        candidate = _build_report(workspace=workspace, sdk_root=sdk_root)
        self.state = candidate
        return candidate


def build_report(workspace: Optional[str] = None, sdk_root: Optional[str] = None) -> Dict[str, Any]:
    """Return a fresh canonical report without mutating any module state."""
    return _build_report(workspace=workspace, sdk_root=sdk_root)
