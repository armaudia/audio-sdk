# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence map for SDK-SURVEY-ENG-04.

This module only reads frozen catalog/component evidence and emits a canonical
coverage report. It does not load an audio file, codec, model, network trace or
device; it does not benchmark, listen, qualify or change the installed SDK.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
TASK = "SDK-SURVEY-ENG-04"
TITLE = "Coverage review for Codec/packetization, FEC, DTX and comfort noise"
SLUG = "survey-eng-04"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "c9296ae96a2b58efae559bd22e7760122c886df8"
BRANCH = "swarm/SDK-SURVEY-ENG-04"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
CATEGORY_ID = "ENG-04"
STATUS = "proposal_only_coverage_map_incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
PROJECT_ROOT = "/Users/htsakanyan/workspace/audio/audioml"
PINNED_PYTHON = "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12"

SOURCE_PINS: Dict[str, str] = {
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/task_backlog.json":
        "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/category_survey/search_log.jsonl":
        "61f95809f956537bea9b878cd544f8e997d6c13a24d2e9ea947795f653847b09",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-PIPE-RECEIVE.md":
        "06ad422cf2c528d34a7821706fa2b1ffba0632ae72e35142e98e5612329d3fa8",
    "research/distortion_restoration_20261028.md":
        "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md":
        "79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b",
    "adapters/opus-plc/adapter.json":
        "a36dd6798d3e9f273c7705fea6d11d888680e633a4b4c41c00e20242f45765ae",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

COMPONENT_EVIDENCE_PINS: Dict[str, str] = {
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "docs/task-evidence/elastic-pcm-packets/README.md":
        "15ebaa6b2b7768faa5c1bd2fc45b900db7f71d49b7ad1292685263555953e742",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md":
        "ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/report.json":
        "ec4c9ea5e46e02d9866920458b4d6365d300d8bcd626d2e05bf7f4c4955a080e",
    "docs/task-evidence/zero-fill-plc/README.md":
        "f1e702efd42ee93ae5402d42ec9f5498f759deb01fa3cb08f6b436f6f92998c4",
    "docs/task-evidence/linear-interpolation-plc/README.md":
        "5102676797554c3e6bc83207a848d35b72783bead5eac13ad60c5a16bd940742",
    "docs/task-evidence/pitch-period-repeat-plc/README.md":
        "8fb323ffd7ce59c361ac1078d7c434b1b3c0b5f088d9a7d07ae5b2278cfa3ea9",
    "docs/task-evidence/autoregressive-plc/README.md":
        "a391565993a4f2439b6e2d584923dd0a812ceeef75c9954c08215df108ff79df",
}

LOCAL_PIN_PATHS: List[str] = [
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "followups/FEASIBILITY-ENG-04-01.md",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
]

SCOPE: Dict[str, bool] = {
    "evidence_map_only": True,
    "real_audio": False,
    "codec_runtime": False,
    "codec_weights": False,
    "network_capture": False,
    "device_timing": False,
    "listening": False,
    "rendered_playback": False,
    "public_benchmark": False,
    "quality_claim": False,
    "release_claim": False,
    "provider_enablement": False,
    "registered_provider": False,
    "assets_generated": False,
    "task_local_only": True,
}

BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "shared_cmakelists_change": False,
    "shared_ci_change": False,
    "build_option_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "public_v0_geometry": {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "sdk_callback_invoked": False,
    },
}

CATALOG: Dict[str, Any] = {
    "category_id": CATEGORY_ID,
    "name": "Codec/packetization, FEC, DTX and comfort noise",
    "group": "Delivery and audio interface support",
    "scope": "support",
    "output_kind": "engineering",
    "purpose": "Define delivery formats, loss redundancy and silence handling.",
    "method_families": {
        "classic": "Codec negotiation; packet duration; FEC; silence suppression/comfort noise",
        "ml": "Neural codec/redundancy variants are conditional leads",
    },
    "input_output": "PCM/session controls ↔ encoded packets and playback state",
    "live_or_comparison_boundary": (
        "Separate network/codec behavior from generic enhancement. Keep "
        "redundancy-assisted and blind recovery in different groups."),
    "source_ids": ["S43", "S44", "S30"],
    "discovery_status": "catalogued",
    "candidate_census_status": "not_started",
    "benchmark_status": "not_started",
    "backlog_family_id": "F16",
    "backlog_state": "catalogued",
    "backlog_activation_state": "catalogued",
    "backlog_next_action": "Plan discovery across required source buckets",
    "catalog_source_sha256": SOURCE_PINS["research/category_registry.json"],
    "backlog_source_sha256": SOURCE_PINS["research/task_backlog.json"],
    "readable_catalog_sha256": SOURCE_PINS["audio_categories.md"],
}

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "id": "S43",
        "title": "Opus RTP specification, RFC 7587",
        "url": "https://www.rfc-editor.org/info/rfc7587/",
        "researcher": "transformations",
        "access_scope": "search excerpt",
        "component_ids": ["opus-packetization-fec-dtx-and-comfort-noise"],
        "match_basis": (
            "Named catalog lead for RTP payload/packetization; matched to the "
            "registered Opus packetization/FEC/DTX/CNG component plan note."),
        "outcome_class": "source_reported_not_reproduced",
        "limits": [
            "RFC body is not vendored, parsed or reproduced here.",
            "No offer/answer negotiation, RTP trace or packet trace is executed.",
        ],
    },
    {
        "id": "S44",
        "title": "WebRTC audio requirements, RFC 7874",
        "url": "https://www.rfc-editor.org/rfc/rfc7874.txt",
        "researcher": "transformations",
        "access_scope": "direct",
        "component_ids": [
            "webrtc-neteq",
            "opus-packetization-fec-dtx-and-comfort-noise",
        ],
        "match_basis": (
            "Named catalog lead for WebRTC audio requirements; matched to the "
            "receive-side NetEq component and the transmit/receive packet "
            "component boundary."),
        "outcome_class": "source_reported_not_reproduced",
        "limits": [
            "No WebRTC runtime, NetEq instance or codec is loaded.",
            "Requirements text is provenance only, not a tested configuration.",
        ],
    },
    {
        "id": "S30",
        "title": "Opus 1.5 neural enhancement and loss recovery",
        "url": "https://opus-codec.org/demo/opus-1.5/",
        "researcher": "acoustics",
        "access_scope": "direct",
        "component_ids": [
            "opus-1-5-lace",
            "opus-1-5-nolace",
            "opus-deep-plc",
            "opus-dred",
        ],
        "match_basis": (
            "Named catalog lead for neural codec/redundancy variants; matched "
            "to catalogued ML conditional leads, not to a local execution."),
        "outcome_class": "source_reported_not_reproduced",
        "limits": [
            "No Opus 1.5 build, LACE/NoLACE, deep PLC, DRED or SE-NAC asset is staged.",
            "The pinned restoration note states these ML candidates were researched but not run.",
        ],
    },
]

FAMILY_AUDIT: List[Dict[str, Any]] = [
    {
        "family_id": "classic.codec_negotiation",
        "catalog_text": "Codec negotiation",
        "status": "missing_component_owner",
        "component_ids": [],
        "component_owner": None,
        "local_outcome": "not_measured_here",
        "reported_outcome": (
            "Catalog and RFC leads only; no offer/answer or payload-parameter "
            "execution is present in the SDK evidence."),
        "missing_evidence": [
            "pinned negotiated capability/payload-parameter contract",
            "matched offer/answer and packet-trace pair",
            "component owner assignment before implementation",
        ],
        "followup_id": "FEASIBILITY-ENG-04-01",
    },
    {
        "family_id": "classic.packet_duration",
        "catalog_text": "packet duration",
        "status": "component_registered_not_executed",
        "component_ids": ["opus-packetization-fec-dtx-and-comfort-noise"],
        "component_owner": "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE",
        "local_outcome": (
            "Existing elastic PCM fixture admits 80/160/240-sample chunks and "
            "timestamped packet blocks; recorded in repo, not rerun here."),
        "reported_outcome": (
            "RFC 7587 is a catalog lead only; no negotiated ptime or captured "
            "RTP trace is reproduced."),
        "missing_evidence": [
            "exact codec packet-duration contract tied to a captured trace",
            "rights-cleared codec runtime and license notice",
        ],
        "followup_id": None,
    },
    {
        "family_id": "classic.fec",
        "catalog_text": "FEC",
        "status": "component_registered_partial_synthetic_control",
        "component_ids": ["opus-packetization-fec-dtx-and-comfort-noise", "opus-dred"],
        "component_owner": "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE",
        "local_outcome": (
            "Existing elastic fixture: one packet erasure recovered from XOR "
            "parity with exact timestamp; two-packet burst rejected_unrecoverable. "
            "No codec FEC/DRED was exercised."),
        "reported_outcome": (
            "DRED is catalogued as redundancy-assisted and requiring a matching "
            "encoder/decoder, extra bitrate/latency and a trace; not run here."),
        "missing_evidence": [
            "codec-native FEC/DRED packet trace with bitrate and delay accounting",
            "separate redundancy-assisted and blind-recovery groups",
        ],
        "followup_id": None,
    },
    {
        "family_id": "classic.silence_suppression_comfort_noise",
        "catalog_text": "silence suppression/comfort noise",
        "status": "component_registered_not_executed",
        "component_ids": ["opus-packetization-fec-dtx-and-comfort-noise"],
        "component_owner": "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE",
        "local_outcome": "not_measured_here",
        "reported_outcome": "Catalog/RFC leads only; no DTX/CNG trace or decoded comfort noise is reproduced.",
        "missing_evidence": [
            "DTX/CNG state machine and decoded silence output under a pinned trace",
            "clipping/onset and continuity controls for silence transitions",
        ],
        "followup_id": None,
    },
    {
        "family_id": "ml.neural_codec_redundancy_variants",
        "catalog_text": "Neural codec/redundancy variants are conditional leads",
        "status": "conditional_leads_researched_not_run",
        "component_ids": [
            "opus-1-5-lace",
            "opus-1-5-nolace",
            "opus-deep-plc",
            "opus-dred",
            "se-nac-codec-latent-enhancement-family",
            "lyra-ii-v2-codec-plc",
            "complex-bin2bin-generative-plc",
        ],
        "component_owner": "multiple queued component records; none executed in this task",
        "local_outcome": "not_measured_here",
        "reported_outcome": (
            "Pinned restoration note records neural/codec-integrated candidates "
            "as researched but not run; adapter provenance is context only."),
        "missing_evidence": [
            "exact compatible codec build and packet-level integration",
            "pinned weights/runtime with preserved notices where required",
            "source-reported values are not promoted to local outcomes",
        ],
        "followup_id": None,
    },
]

COMPONENT_MATCHES: List[Dict[str, Any]] = [
    {
        "id": "opus-packetization-fec-dtx-and-comfort-noise",
        "task": "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE",
        "repository": "audio-sdk",
        "board_status": "queued",
        "evidence_status": "considered",
        "matched_families": [
            "classic.packet_duration",
            "classic.fec",
            "classic.silence_suppression_comfort_noise",
        ],
        "matched_source_ids": ["S43", "S44"],
        "basis": "Registered component with receive/transmit packet contract plan note.",
        "local_evidence": "No task-local evidence directory at this base.",
    },
    {
        "id": "webrtc-neteq",
        "task": "SDK-WEBRTC-NETEQ",
        "repository": "audio-sdk",
        "board_status": "queued",
        "evidence_status": "considered",
        "matched_families": ["classic.packet_duration", "classic.fec"],
        "matched_source_ids": ["S44"],
        "basis": "Receive-side jitter/playout with trace replay and codec integration plan note.",
        "local_evidence": "No task-local evidence directory at this base.",
    },
    {
        "id": "opus-1-4-standard-decoder-plc",
        "task": "SDK-OPUS-1-4-STANDARD-DECODER-PLC",
        "repository": "audio-sdk",
        "board_status": "done",
        "evidence_status": "evaluated",
        "matched_families": ["classic.fec"],
        "matched_source_ids": [],
        "basis": (
            "Classical blind waveform PLC control; the committed evidence is a "
            "synthetic pitch-repeat surrogate, not native Opus, deep PLC, DRED "
            "or FEC, and S30 covers Opus 1.5 rather than this 1.4 record."),
        "local_evidence": "docs/task-evidence/opus-1-4-standard-decoder-plc/ (synthetic pitch-repeat control).",
    },
    {
        "id": "opus-dred",
        "task": "SDK-OPUS-DRED",
        "repository": "audio-sdk",
        "board_status": "queued",
        "evidence_status": "considered",
        "matched_families": ["classic.fec", "ml.neural_codec_redundancy_variants"],
        "matched_source_ids": ["S30"],
        "basis": "Redundancy-assisted recovery lead, separate from blind concealment.",
        "local_evidence": "No task-local evidence directory at this base.",
    },
    {
        "id": "opus-deep-plc",
        "task": "SDK-OPUS-DEEP-PLC",
        "repository": "audio-sdk",
        "board_status": "queued",
        "evidence_status": "considered",
        "matched_families": ["ml.neural_codec_redundancy_variants"],
        "matched_source_ids": ["S30"],
        "basis": "Neural concealment conditional lead; explicit missing-packet events required.",
        "local_evidence": "No task-local evidence directory at this base.",
    },
    {
        "id": "opus-1-5-lace",
        "task": "SDK-OPUS-1-5-LACE",
        "repository": "audio-sdk",
        "board_status": "queued",
        "evidence_status": "considered",
        "matched_families": ["ml.neural_codec_redundancy_variants"],
        "matched_source_ids": ["S30"],
        "basis": "Decoder-integrated neural postfilter conditional lead.",
        "local_evidence": "No task-local evidence directory at this base.",
    },
    {
        "id": "opus-1-5-nolace",
        "task": "SDK-OPUS-1-5-NOLACE",
        "repository": "audio-sdk",
        "board_status": "queued",
        "evidence_status": "considered",
        "matched_families": ["ml.neural_codec_redundancy_variants"],
        "matched_source_ids": ["S30"],
        "basis": "Decoder postfilter isolation conditional lead.",
        "local_evidence": "No task-local evidence directory at this base.",
    },
    {
        "id": "se-nac-codec-latent-enhancement-family",
        "task": "SDK-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY",
        "repository": "audio-sdk",
        "board_status": "queued",
        "evidence_status": "considered",
        "matched_families": ["ml.neural_codec_redundancy_variants"],
        "matched_source_ids": [],
        "basis": (
            "Codec-latent neural enhancement family from the local noise-suppression "
            "census; not one of the ENG-04 catalog source leads and not executed."),
        "local_evidence": "No task-local evidence directory at this base.",
    },
    {
        "id": "lyra-ii-v2-codec-plc",
        "task": "SDK-LYRA-II-V2-CODEC-PLC",
        "repository": "audio-sdk",
        "board_status": "queued",
        "evidence_status": "blocked",
        "matched_families": ["ml.neural_codec_redundancy_variants"],
        "matched_source_ids": [],
        "basis": (
            "Codec PLC lead from candidate-matrix row 27, blocked without a "
            "pinned codec/runtime/loss-trace adapter; not an S30 Opus lead."),
        "local_evidence": "No task-local evidence directory at this base.",
    },
    {
        "id": "complex-bin2bin-generative-plc",
        "task": "SDK-COMPLEX-BIN2BIN-GENERATIVE-PLC",
        "repository": "audio-sdk",
        "board_status": "queued",
        "evidence_status": "blocked",
        "matched_families": ["ml.neural_codec_redundancy_variants"],
        "matched_source_ids": [],
        "basis": (
            "Generative PLC lead from candidate-matrix row 28, blocked without an "
            "exact checkpoint and codec-aligned loss benchmark; not an S30 Opus lead."),
        "local_evidence": "No task-local evidence directory at this base.",
    },
]

HISTORICAL_EXECUTIONS: List[Dict[str, Any]] = [
    {
        "id": "SDK-FND-ELASTIC",
        "status": "done",
        "evidence_class": "existing_local_fixture_recorded_in_repo_not_rerun",
        "path": "docs/task-evidence/elastic-pcm-packets/",
        "component_ids": ["opus-packetization-fec-dtx-and-comfort-noise"],
        "match_basis": (
            "Foundation fixture supplies the PCM/packet separation and "
            "single-erasure parity control the packet contract requires; it is "
            "not a codec execution."),
        "matched_families": ["classic.packet_duration", "classic.fec"],
        "comparison_inputs": [
            "80/160/240-sample PCM chunks",
            "timestamped packet blocks",
            "single-erasure XOR parity packet",
        ],
        "controls": ["identity", "bounded queue", "single erasure", "two-packet burst"],
        "local_outcome": (
            "Recorded 9/9 fixture tests; one erasure recovered with exact "
            "timestamp; two-packet burst rejected_unrecoverable; PCM and packet "
            "recovery kept separate."),
        "reported_outcome": None,
        "not_covered": ["Opus codec", "RTP negotiation", "DTX/CNG", "network trace", "device timing"],
    },
    {
        "id": "SDK-OPUS-1-4-STANDARD-DECODER-PLC",
        "status": "done",
        "evidence_class": "existing_local_fixture_recorded_in_repo_not_rerun",
        "path": "docs/task-evidence/opus-1-4-standard-decoder-plc/",
        "component_ids": ["opus-1-4-standard-decoder-plc"],
        "match_basis": (
            "Task-local synthetic surrogate for the registered 1.4 PLC record; "
            "the native historical screen is reported, not reproduced."),
        "matched_families": ["classic.fec"],
        "comparison_inputs": [
            "synthetic voiced/unvoiced/silence waveform",
            "deterministic erasure masks",
            "stateful 20 ms packet framing proxy",
        ],
        "controls": ["zero-fill", "linear", "pitch/AR", "identity"],
        "local_outcome": (
            "Synthetic pitch-repetition-with-decay reference only; explicitly "
            "not Opus output, deep PLC, DRED or FEC."),
        "reported_outcome": (
            "Pinned historical report records a native 12-clip EARS screen and "
            "median decoder RTF about 0.0015; not reproduced here and not the "
            "committed surrogate."),
        "not_covered": ["native Opus", "captured network trace", "FEC/DRED", "DTX/CNG", "listening"],
    },
    {
        "id": "SDK-ZERO-FILL-PLC",
        "status": "done",
        "evidence_class": "existing_local_fixture_recorded_in_repo_not_rerun",
        "path": "docs/task-evidence/zero-fill-plc/",
        "component_ids": ["opus-1-4-standard-decoder-plc"],
        "match_basis": "Blind waveform control used by the registered PLC comparison; not linkable to a codec.",
        "matched_families": ["classic.fec"],
        "comparison_inputs": ["synthetic erasure bursts", "final partial window", "stale/duplicate packets"],
        "controls": ["hold", "linear", "identity"],
        "local_outcome": "Blind waveform concealment control; no codec-native recovery.",
        "reported_outcome": None,
        "not_covered": ["codec state", "FEC", "RTP", "DTX/CNG", "real speech"],
    },
    {
        "id": "SDK-PIPE-RECEIVE",
        "status": "blocked",
        "evidence_class": "recorded_blocked_attempt_not_rerun",
        "path": "audio-benchmark-platform/plan/swarm/handoffs/SDK-PIPE-RECEIVE.md",
        "component_ids": ["opus-1-4-standard-decoder-plc", "webrtc-neteq"],
        "match_basis": (
            "Blocked receive path would combine the registered 1.4 PLC record "
            "with receive-side playout; neither is accepted here."),
        "matched_families": ["classic.fec", "classic.packet_duration"],
        "comparison_inputs": [
            "timestamped Opus PLC receive proposal",
            "expected Opus 1.4 runtime digest",
            "peak-limiter receive recipe",
        ],
        "controls": ["no-loss", "silence", "repeat", "native PLC", "limiter ablation"],
        "local_outcome": (
            "Blocked: exact runtime and notice absent, limiter reproduction "
            "digit mismatch unresolved; no native receive acceptance."),
        "reported_outcome": None,
        "not_covered": ["installed native receive path", "FEC/DTX/CNG", "device timing"],
    },
    {
        "id": "research-candidate-matrix-26-30",
        "status": "reported_only",
        "evidence_class": "source_reported_not_reproduced",
        "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "component_ids": [
            "opus-1-4-standard-decoder-plc",
            "lyra-ii-v2-codec-plc",
            "complex-bin2bin-generative-plc",
        ],
        "match_basis": (
            "Matrix rows name the registered 1.4 PLC, Lyra and Complex-Bin2bin "
            "records; only the blocked/unavailable statuses are reused."),
        "matched_families": ["classic.fec", "ml.neural_codec_redundancy_variants"],
        "comparison_inputs": [
            "candidate matrix rows 26-30 (WaveFit out of scope, Lyra II/V2 row 27, "
            "Complex-Bin2bin row 28, conventional PLC controls row 29, Opus 1.4 "
            "row 30)",
        ],
        "controls": ["Opus PLC", "identity codec", "pitch/AR controls"],
        "local_outcome": None,
        "reported_outcome": (
            "WaveFit is out of scope; Lyra II/V2 and Complex-Bin2bin rows are "
            "unavailable/blocked; conventional waveform controls and the Opus "
            "1.4 row are evaluated as a bounded 12-clip EARS screen; context only."),
        "not_covered": ["exact codec/runtime parity", "network traces", "DTX/CNG"],
    },
    {
        "id": "research-historical-chain-73",
        "status": "reported_only",
        "evidence_class": "source_reported_not_reproduced",
        "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "component_ids": [],
        "match_basis": (
            "No ENG-04 codec/packet component owns this enhancement chain; it is "
            "recorded only to show why it is not packet-loss evidence."),
        "matched_families": ["classic.packet_duration"],
        "comparison_inputs": ["proposed chained mobile VAD-FastEnhancer-WPE pipeline"],
        "controls": ["FastEnhancer-only", "constituent stages", "identity"],
        "local_outcome": None,
        "reported_outcome": (
            "Historical chain completed on six pinned recordings with load "
            "distortion and aborted retries; no PLC/FEC/DTX integration, phone, "
            "power or thermal result."),
        "not_covered": ["codec/packet integration", "FEC/DTX/CNG", "network capture"],
    },
]

COMPARISON_INPUTS: Dict[str, Any] = {
    "catalog_input_output": CATALOG["input_output"],
    "session_controls": [
        "16 kHz mono float32 160-sample public v0 PCM boundary (unchanged)",
        "timestamp and sequence metadata for a separate packet object",
        "negotiated packet duration and payload parameters (catalog lead only)",
        "DTX/CNG state and silence-transition markers (catalog lead only)",
    ],
    "packet_fields": [
        "sequence",
        "timestamp",
        "payload type",
        "FEC/redundancy marker",
        "DTX/CNG marker",
    ],
    "erasure_masks": [
        "no_loss_identity",
        "single_packet_single_erasure",
        "two_packet_burst",
        "stale_duplicate_out_of_order_future",
    ],
    "not_present_local": [
        "RTP offer/answer negotiation",
        "captured network trace",
        "Opus library, dylib, CLI or runtime",
        "decoded comfort-noise output",
        "real speech or listening data",
        "target-device timing",
    ],
    "separation_rules": [
        "PCM/session controls are distinct from encoded packets and playback state.",
        "Redundancy-assisted recovery and blind recovery are recorded in different groups.",
        "Source-reported values are never pooled with local fixture outcomes.",
    ],
}

CONTROLS: List[Dict[str, Any]] = [
    {
        "id": "identity_no_loss",
        "purpose": "Show exact packet/PCM passage without recovery.",
        "local_status": "existing elastic fixture records identity for variable PCM chunks.",
        "codec_claim": False,
    },
    {
        "id": "blind_plc",
        "purpose": "Estimate missing content from history only.",
        "local_status": "zero-fill/linear/pitch/AR and synthetic Opus-PLC control fixtures exist; not codec-native.",
        "codec_claim": False,
    },
    {
        "id": "redundancy_assisted_fec",
        "purpose": "Recover using transmitted parity/redundancy information.",
        "local_status": "existing elastic fixture recovers one erasure from XOR parity; two-packet burst rejected.",
        "codec_claim": False,
    },
    {
        "id": "silence_cng_transition",
        "purpose": "Exercise DTX/CNG onset, hold and resume boundaries.",
        "local_status": "not_measured_here",
        "codec_claim": False,
    },
    {
        "id": "invalid_state_rejection",
        "purpose": "Reject stale, duplicate, out-of-order and noncontiguous input explicitly.",
        "local_status": "recorded in existing PLC fixtures; not rerun here.",
        "codec_claim": False,
    },
]

ASSETS: Dict[str, Any] = {
    "audio_files": [],
    "codec_runtime": [],
    "model_weights": [],
    "captured_network_traces": [],
    "generated_binary_assets": [],
    "synthetic_descriptors": [
        "packet sequence/timestamp fields (described, not instantiated as an asset)",
        "erasure-mask labels (described, not instantiated as an asset)",
    ],
    "license_sidecars": [
        "contract.json.license",
        "report.json.license",
        "report.json.sha256.license",
        "SOURCES.sha256.license",
    ],
}

LOCAL_OUTCOMES: List[Dict[str, Any]] = [
    {
        "id": "this_task",
        "class": "not_measured_here",
        "statement": (
            "This task executed only catalog/pin analysis and deterministic "
            "report generation; no codec, audio, network or perceptual outcome "
            "was measured."),
    },
    {
        "id": "elastic_packet_fixture",
        "class": "existing_local_fixture_recorded_in_repo_not_rerun",
        "statement": (
            "One XOR-parity erasure recovered with exact timestamp; two-packet "
            "burst rejected; PCM and packet objects separated."),
    },
    {
        "id": "plc_fixtures",
        "class": "existing_local_fixture_recorded_in_repo_not_rerun",
        "statement": (
            "Blind synthetic concealment controls and metrics are recorded in "
            "separate task-local packages; none is codec-native FEC/DTX/CNG."),
    },
]

REPORTED_OUTCOMES: List[Dict[str, Any]] = [
    {
        "id": "opus_1_4_screen",
        "class": "source_reported_not_reproduced",
        "statement": "Pinned 12-clip EARS packet-erasure screen and RTF about 0.0015; context only.",
        "pin": SOURCE_PINS["REALTIME_COMPONENT_CANDIDATES.md"],
    },
    {
        "id": "ml_codec_leads",
        "class": "source_reported_not_reproduced",
        "statement": "Opus 1.5 LACE/NoLACE/deep PLC/DRED and neural codec leads researched but not run.",
        "pin": SOURCE_PINS["research/distortion_restoration_20261028.md"],
    },
    {
        "id": "adapter_provenance",
        "class": "source_reported_not_reproduced",
        "statement": "Opus adapter identity and documented historical dylib path are provenance only; no binary loaded here.",
        "pin": SOURCE_PINS["adapters/opus-plc/adapter.json"],
    },
]

FOLLOWUPS: List[Dict[str, Any]] = [
    {
        "id": "FEASIBILITY-ENG-04-01",
        "path": "followups/FEASIBILITY-ENG-04-01.md",
        "gap": "Classic codec negotiation has no registered component owner in the component inventory.",
        "component_owner": None,
        "status": "open_bounded_feasibility_followup",
        "implemented": False,
        "linked_from_family_ids": ["classic.codec_negotiation"],
        "bounded_scope": (
            "Determine whether a negotiation/parameter-agreement state model can "
            "be specified at the existing PCM/packet boundary; no codec, RTP, "
            "network or provider implementation."),
        "reopen_condition": (
            "Assign a component owner, pin an exact RFC-derived packet contract "
            "and matched trace, obtain rights/licensing clearance and independent "
            "review before any execution."),
    },
]

GATES: List[Dict[str, str]] = [
    {
        "name": "component_owner_assignment",
        "status": "blocked",
        "reopen_condition": "Assign an owner for codec negotiation; no component record exists.",
    },
    {
        "name": "codec_runtime_rights",
        "status": "blocked",
        "reopen_condition": "Stage a rights-cleared pinned codec runtime with preserved notices.",
    },
    {
        "name": "captured_packet_trace",
        "status": "blocked",
        "reopen_condition": "Pin a matched negotiation/packet/erasure trace with exact timestamps.",
    },
    {
        "name": "fec_dtx_cng_execution",
        "status": "blocked",
        "reopen_condition": "Execute packet-level FEC, DTX/CNG and redundancy-assisted controls separately.",
    },
    {
        "name": "independent_listening",
        "status": "blocked",
        "reopen_condition": "Run authorized blind listening on rights-cleared speech; no proxy qualifies.",
    },
    {
        "name": "target_timing_and_release",
        "status": "blocked",
        "reopen_condition": "Measure pinned target runtime timing and obtain explicit public default/release decision.",
    },
]

TOOL_PROVENANCE: List[str] = [
    "Only category registry, readable catalog, backlog, pinned research notes and pinned SDK evidence files were read.",
    "No RFC body, codec source/binary, model weight, audio, device capture or network trace was fetched or generated.",
    "No SDK build, provider, descriptor, ABI, default or CI configuration was changed.",
]

VERIFICATION: Dict[str, Any] = {
    "verifier": "verify.py",
    "tests": "test_reference.py",
    "installed_package_check": "scripts/ci.py --output <scratch-outside-worktree>",
    "licensing_check": "reuse lint",
    "diff_check": "git diff --check",
    "board_read_only_check": (
        "python3 audio-benchmark-platform/plan/swarm/check.py --task SDK-SURVEY-ENG-04"),
    "pinned_python": PINNED_PYTHON,
    "notes": [
        "The verifier is read-only and never rewrites evidence.",
        "The installed-package check is executed outside the verifier and writes only to scratch.",
    ],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def catalog_entry() -> Dict[str, Any]:
    """Return the frozen ENG-04 record from the pinned structured catalog."""
    registry = json.loads((SOURCE_ROOT / "research/category_registry.json").read_text(encoding="utf-8"))
    matches = [item for item in registry["categories"] if item["id"] == CATEGORY_ID]
    if len(matches) != 1:
        raise ValueError("catalog_entry_not_unique")
    return matches[0]


def backlog_entry() -> Dict[str, Any]:
    backlog = json.loads((SOURCE_ROOT / "research/task_backlog.json").read_text(encoding="utf-8"))
    matches = [item for item in backlog["entries"] if item["category_id"] == CATEGORY_ID]
    if len(matches) != 1:
        raise ValueError("backlog_entry_not_unique")
    return matches[0]


def source_lead_lines() -> List[str]:
    text = (SOURCE_ROOT / "research/category_survey/sources.md").read_text(encoding="utf-8")
    return [line for line in text.splitlines()
            if line.startswith("| S43 ") or line.startswith("| S44 ") or line.startswith("| S30 ")]


def core_report() -> Dict[str, Any]:
    entry = catalog_entry()
    backlog = backlog_entry()
    catalog = dict(CATALOG)
    catalog.update({
        "name": entry["name"],
        "group": entry["group"],
        "scope": entry["scope"],
        "output_kind": entry["output_kind"],
        "purpose": entry["purpose"],
        "method_families": dict(entry["method_families"]),
        "input_output": entry["input_output"],
        "live_or_comparison_boundary": entry["live_or_comparison_boundary"],
        "source_ids": list(entry["source_ids"]),
        "discovery_status": entry["discovery_status"],
        "candidate_census_status": entry["candidate_census_status"],
        "benchmark_status": entry["benchmark_status"],
        "backlog_family_id": backlog["family_id"],
        "backlog_state": backlog["state"],
        "backlog_activation_state": backlog["activation_state"],
        "backlog_next_action": backlog["next_action"],
    })
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "mode": "taxonomy_evidence_map",
        "status": STATUS,
        "qualification_status": QUALIFICATION,
        "no_missing_result_qualifies_candidate": True,
        "decision": DECISION,
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "catalog": catalog,
        "named_source_leads": SOURCE_LEADS,
        "method_family_audit": FAMILY_AUDIT,
        "component_matches": COMPONENT_MATCHES,
        "historical_executions": HISTORICAL_EXECUTIONS,
        "comparison_inputs": COMPARISON_INPUTS,
        "controls": CONTROLS,
        "assets": ASSETS,
        "local_outcomes": LOCAL_OUTCOMES,
        "reported_outcomes": REPORTED_OUTCOMES,
        "release_boundary": dict(BOUNDARY),
        "missing_evidence": [item for family in FAMILY_AUDIT for item in family["missing_evidence"]],
        "gates": GATES,
        "followups": FOLLOWUPS,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "component_evidence_pins": dict(COMPONENT_EVIDENCE_PINS),
        "contract_id": f"{CONTRACT_SCHEMA_ID}:{TASK}",
        "contract_sha256": sha256((HERE / "contract.json").read_bytes()),
        "tool_provenance": TOOL_PROVENANCE,
        "verification": VERIFICATION,
        "evidence_classes": [
            "catalog_crosswalk",
            "component_registration_match",
            "existing_fixture_provenance",
            "bounded_gap_followup",
        ],
    }


def repeatability() -> Dict[str, Any]:
    """Three cold-start processes hashing the canonical core report."""
    code = ("import hashlib,sys;sys.path.insert(0,sys.argv[1]);import reference;"
            "print(hashlib.sha256(reference.canonical_report_bytes("
            "reference.core_report())).hexdigest())")
    digests = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code, str(HERE)],
                                capture_output=True, text=True, check=True, env=env)
        digests.append(result.stdout.strip())
    return {"count": 3, "method": "three_fresh_interpreters_canonical_core",
            "digests": digests, "byte_identical": len(set(digests)) == 1}


def build_report() -> Dict[str, Any]:
    report = core_report()
    report["repeatability"] = repeatability()
    return report


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for SDK-SURVEY-ENG-04.",
        "# source: paths are relative to SOURCE_ROOT; other paths are SDK-worktree relative.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in sorted(BOUNDARY_PINS):
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for path in sorted(COMPONENT_EVIDENCE_PINS):
        lines.append(f"{COMPONENT_EVIDENCE_PINS[path]}  {path}")
    for name in LOCAL_PIN_PATHS:
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")
