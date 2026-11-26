# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence map for ENG-03 only.

ENG-03 is "Jitter buffering and adaptive playout" in
``research/category_registry.json``. This builder reads pinned registry,
companion taxonomy, legacy backlog, inventory, board and component evidence
records. It performs no audio, codec, network, device, listening, benchmark or
release action. Output is canonical stdlib-only JSON.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", str(SDK_ROOT.parents[2])))

TASK = "SDK-SURVEY-ENG-03"
TITLE = "Jitter buffering and adaptive playout evidence map"
TASK_TITLE = "Review coverage for Jitter buffering and adaptive playout"
SLUG = "survey-eng-03"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "c9296ae96a2b58efae559bd22e7760122c886df8"
BRANCH = "swarm/SDK-SURVEY-ENG-03"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.2"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
PROFILE = "evidence"
MODE = "taxonomy"
STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
CATEGORY_ID = "ENG-03"

SOURCE_PINS: Dict[str, str] = {
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/task_backlog.json":
        "0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/TASKS.json":
        "b583d08dd6ac063bf1885fcf921ebea8c5927ed1a9a70fad78c4998d84e247ca",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-FND-ELASTIC.md":
        "8f7aec856f92d7090935c86ba89fa99e1f5b3ebb6e6a67c081eed9d2c9c94b5c",
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-BUFFER-OCCUPANCY-CONTROLLER.md":
        "0a0d92d52990f851b96cf38e4c010276136c28d620bc7d6db72c38e8506bb12a",
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-RUBBER-BAND-R3-OFFLINE.md":
        "df84500595acf96bb07808334c3f2bc6101b4f3f0c8a3179a06cfd15f9c60792",
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-RUBBER-BAND-R3-STREAMING.md":
        "b70f9ed4dd2625894c6ba24ca8bd308c2c9cf0584b5d322c58ef8c52ad42c024",
}
SOURCE_PIN_SELECTORS = {
    "audio-benchmark-platform/plan/swarm/TASKS.json":
        "selected-board-task-records/0.2:id,mode,repository,title,component",
}
BOARD_PIN_TASK_IDS = [
    "SDK-SURVEY-ENG-03",
    "SDK-BUFFER-OCCUPANCY-CONTROLLER",
    "SDK-CAPSC-BUFFER-OCCUPANCY-PACING",
    "SDK-WEBRTC-NETEQ",
    "SDK-FND-ELASTIC",
    "SDK-PIPE-RECEIVE",
    "SDK-RUBBER-BAND-R3-OFFLINE",
    "SDK-RUBBER-BAND-R3-STREAMING",
    "SDK-FFMPEG-ATEMPO",
    "SDK-LINEAR-INTERPOLATION-PLC",
    "SDK-PITCH-PERIOD-REPEAT-PLC",
    "SDK-ZERO-FILL-PLC",
    "SDK-OPUS-1-4-STANDARD-DECODER-PLC",
    "SDK-AUTOREGRESSIVE-PLC",
    "SDK-SONIC",
    "SDK-SOUNDTOUCH",
    "SDK-PSOLA-PRAAT",
    "SDK-SIGNALSMITH-STRETCH",
    "SDK-GRANULAR-TSM",
    "SDK-OLA-SOLA",
    "SDK-PHASE-VOCODER-BASELINE",
]
BOARD_PIN_FIELDS = ("id", "mode", "repository", "title", "component")
# Frozen observations at report generation; board status is not a pin.
BOARD_STATUS_SNAPSHOT = {
    "SDK-SURVEY-ENG-03": "review",
    "SDK-BUFFER-OCCUPANCY-CONTROLLER": "done",
    "SDK-CAPSC-BUFFER-OCCUPANCY-PACING": "queued",
    "SDK-WEBRTC-NETEQ": "queued",
    "SDK-FND-ELASTIC": "done",
    "SDK-PIPE-RECEIVE": "blocked",
    "SDK-RUBBER-BAND-R3-OFFLINE": "done",
    "SDK-RUBBER-BAND-R3-STREAMING": "done",
    "SDK-FFMPEG-ATEMPO": "done",
    "SDK-LINEAR-INTERPOLATION-PLC": "done",
    "SDK-PITCH-PERIOD-REPEAT-PLC": "done",
    "SDK-ZERO-FILL-PLC": "done",
    "SDK-OPUS-1-4-STANDARD-DECODER-PLC": "done",
    "SDK-AUTOREGRESSIVE-PLC": "done",
    "SDK-SONIC": "done",
    "SDK-SOUNDTOUCH": "done",
    "SDK-PSOLA-PRAAT": "done",
    "SDK-SIGNALSMITH-STRETCH": "done",
    "SDK-GRANULAR-TSM": "done",
    "SDK-OLA-SOLA": "done",
    "SDK-PHASE-VOCODER-BASELINE": "done",
}
BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    ".github/workflows/release.yml":
        "6fee1576bf3517cf8aa2a9f963988ea7aac41e16d32df506336a0ee408a4ebfc",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/buffer-occupancy-controller/README.md":
        "862a94c9add8ecd5e15f09a543ff17100dc5680da00f8a0635a884509cb51a33",
    "docs/task-evidence/elastic-pcm-packets/README.md":
        "15ebaa6b2b7768faa5c1bd2fc45b900db7f71d49b7ad1292685263555953e742",
    "docs/task-evidence/rubber-band-r3-offline/README.md":
        "de528246089b9f0d2a1ea597ac0cbbb119d5541b2b22a0a383b4d03b7a85aeab",
    "docs/task-evidence/rubber-band-r3-streaming/README.md":
        "04583e07678079f1ed179a1b15f50599693a7bc6f6a813237a71d0005d810d97",
    "docs/task-evidence/ffmpeg-atempo/README.md":
        "11773a543c6dab54ff4754989501a0a70a29b247612e51aee5fb54c0050457b8",
    "docs/task-evidence/linear-interpolation-plc/README.md":
        "5102676797554c3e6bc83207a848d35b72783bead5eac13ad60c5a16bd940742",
    "docs/task-evidence/pitch-period-repeat-plc/README.md":
        "8fb323ffd7ce59c361ac1078d7c434b1b3c0b5f088d9a7d07ae5b2278cfa3ea9",
    "docs/task-evidence/zero-fill-plc/README.md":
        "f1e702efd42ee93ae5402d42ec9f5498f759deb01fa3cb08f6b436f6f92998c4",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md":
        "ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df",
    "docs/task-evidence/autoregressive-plc/README.md":
        "a391565993a4f2439b6e2d584923dd0a812ceeef75c9954c08215df108ff79df",
    "docs/task-evidence/sonic/README.md":
        "40f2fdcf708a75fbc3e0df296fabfecd296118e6a9eaee67fc34f8dec0e419cb",
    "docs/task-evidence/soundtouch/README.md":
        "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
    "docs/task-evidence/signalsmith-stretch/README.md":
        "446398e0c3aa27528e5ceacf1d4d0b6102f8c8e541c76aa6ac2a8abe62691934",
    "docs/task-evidence/psola-praat/README.md":
        "7e64ec614937533168ef31c34d4c8ec4aa7d6d52670e663f0f88ce5f4ec7a6ef",
    "docs/task-evidence/granular-tsm/README.md":
        "d97f06911fd90667288fe571c7a3f4210ece629f7e839c1d41200ceec48ec0a0",
    "docs/task-evidence/ola-sola/README.md":
        "5d7de4612ad4d04cad544e4060aba607916f0fd013471388cc74fb55168bd731",
    "docs/task-evidence/phase-vocoder-baseline/README.md":
        "915bd51e7de4b223bdd61bb5ff823e7a0558f03e324f154d7d3d4c77d14f9790",
}
LOCAL_PIN_PATHS = [
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
]

SCOPE: Dict[str, Any] = {
    "category_ids": [CATEGORY_ID],
    "source_and_board_record_mapping_only": True,
    "synthetic_state_controls_only": True,
    "real_corpus": False,
    "real_weights": False,
    "audio_runtime_executed": False,
    "model_runtime_executed": False,
    "codec_runtime_executed": False,
    "vendor_runtime_executed": False,
    "network_trace_used": False,
    "jitter_buffer_executed": False,
    "adaptive_playout_executed": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "release_claim": False,
    "registered_provider": False,
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
    "ci_workflow_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
}
FORMAT: Dict[str, Any] = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}
CLAIMS: Dict[str, bool] = {
    "device_timing": False,
    "listening": False,
    "benchmark": False,
    "release_claim": False,
    "codec_runtime_executed": False,
    "jitter_buffer_executed": False,
    "network_trace_used": False,
}
FOLLOW_UP_POLICY: Dict[str, Any] = {
    "invent_new_tasks": False,
    "board_only": True,
    "allowed_modes": ["feasibility"],
    "existing_feasibility_task_ids": [
        "SDK-BUFFER-OCCUPANCY-CONTROLLER",
        "SDK-CAPSC-BUFFER-OCCUPANCY-PACING",
        "SDK-WEBRTC-NETEQ",
    ],
}

# Component records with an inventory identity. ``relationship`` prevents
# adjacent user-selected speed control from being pooled with jitter buffering.
COMPONENT_LINKS: List[Dict[str, str]] = [
    {"component_id": "buffer-occupancy-controller",
     "relationship": "adaptive_buffer_control_law",
     "evidence_path": "docs/task-evidence/buffer-occupancy-controller/README.md",
     "family": "Adaptive buffers"},
    {"component_id": "capsc-buffer-occupancy-pacing",
     "relationship": "adaptive_buffer_pacing_lead",
     "evidence_path": "",
     "family": "Adaptive buffers"},
    {"component_id": "webrtc-neteq",
     "relationship": "reorder_delay_time_scale_source_lead",
     "evidence_path": "",
     "family": "Adaptive buffers"},
    {"component_id": "rubber-band-r3-offline",
     "relationship": "offline_time_scale_candidate",
     "evidence_path": "docs/task-evidence/rubber-band-r3-offline/README.md",
     "family": "Acceleration/deceleration"},
    {"component_id": "rubber-band-r3-streaming",
     "relationship": "streaming_time_scale_candidate",
     "evidence_path": "docs/task-evidence/rubber-band-r3-streaming/README.md",
     "family": "Acceleration/deceleration"},
    {"component_id": "ffmpeg-atempo",
     "relationship": "rational_rate_change_reference",
     "evidence_path": "docs/task-evidence/ffmpeg-atempo/README.md",
     "family": "Acceleration/deceleration"},
    {"component_id": "linear-interpolation-plc",
     "relationship": "plc_baseline",
     "evidence_path": "docs/task-evidence/linear-interpolation-plc/README.md",
     "family": "PLC integration"},
    {"component_id": "pitch-period-repeat-plc",
     "relationship": "plc_synthetic_candidate",
     "evidence_path": "docs/task-evidence/pitch-period-repeat-plc/README.md",
     "family": "PLC integration"},
    {"component_id": "zero-fill-plc",
     "relationship": "plc_degraded_baseline",
     "evidence_path": "docs/task-evidence/zero-fill-plc/README.md",
     "family": "PLC integration"},
    {"component_id": "opus-1-4-standard-decoder-plc",
     "relationship": "plc_decoder_style_surrogate",
     "evidence_path": "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md",
     "family": "PLC integration"},
    {"component_id": "autoregressive-plc",
     "relationship": "plc_statistical_baseline",
     "evidence_path": "docs/task-evidence/autoregressive-plc/README.md",
     "family": "PLC integration"},
]
FOUNDATION_LINKS: List[Dict[str, str]] = [
    {"component_id": "elastic-pcm-packets",
     "task_id": "SDK-FND-ELASTIC",
     "relationship": "variable_count_pcm_and_packet_timing_contract",
     "evidence_path": "docs/task-evidence/elastic-pcm-packets/README.md",
     "family": "Adaptive buffers"},
]
# Catalogued user-selected time-scale engines. They are audited for coverage but
# are not adaptive playout and are never counted as jitter-buffer evidence.
ADJACENT_SPEED_CONTROLS: List[Dict[str, str]] = [
    {"component_id": "sonic",
     "evidence_path": "docs/task-evidence/sonic/README.md"},
    {"component_id": "soundtouch",
     "evidence_path": "docs/task-evidence/soundtouch/README.md"},
    {"component_id": "signalsmith-stretch",
     "evidence_path": "docs/task-evidence/signalsmith-stretch/README.md"},
    {"component_id": "psola-praat",
     "evidence_path": "docs/task-evidence/psola-praat/README.md"},
    {"component_id": "granular-tsm",
     "evidence_path": "docs/task-evidence/granular-tsm/README.md"},
    {"component_id": "ola-sola",
     "evidence_path": "docs/task-evidence/ola-sola/README.md"},
    {"component_id": "phase-vocoder-baseline",
     "evidence_path": "docs/task-evidence/phase-vocoder-baseline/README.md"},
]

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "id": "S41",
        "mapped_components": [
            "webrtc-neteq",
            "buffer-occupancy-controller",
            "capsc-buffer-occupancy-pacing",
            "opus-1-4-standard-decoder-plc",
            "elastic-pcm-packets",
        ],
        "historical_executions": [
            "No local NetEq source, binary, trace replay or codec-integrated "
            "playout run appears in the reviewed pins.",
            "The closest local controls are synthetic: a virtual-clock "
            "buffer-occupancy controller, a model-free elastic PCM/packet "
            "fixture, and standalone host-adapter PLC fixtures.",
        ],
        "limits": [
            "S41 is a documentation URL without a pinned revision or checkout; "
            "it is a source lead, not local source evidence.",
            "API block size is not total latency, and receive-side packet "
            "arrival, reordering and device pacing remain unmeasured.",
        ],
    },
]

CLASSICAL: List[Dict[str, Any]] = [
    {
        "family": "Adaptive buffers",
        "catalogued_text": "Adaptive buffers",
        "component_ids": [
            "webrtc-neteq",
            "buffer-occupancy-controller",
            "capsc-buffer-occupancy-pacing",
            "elastic-pcm-packets",
        ],
        "comparison_inputs": [
            "Twelve matched virtual-clock traces at nominal, +/-1000 ppm, a "
            "400 ms delivery hold and release, +60,000 ppm and a 1 s hold; "
            "source coordinates are millionths of a source sample and output "
            "coordinates are nominal 16 kHz playout samples.",
            "Variable-count elastic fixture chunks of 80/160/240 samples with "
            "exact Fraction source-to-output maps, a bounded pending-input "
            "limit and a finite drain.",
            "No RTP timestamp sequence, receive-side arrival log or NetEq "
            "trace is present in the reviewed pins.",
        ],
        "controls": [
            "Controller target is 3200 source samples (200 ms), capacity is "
            "9600 (600 ms), the proportional law is quantized to integer ppm, "
            "clamped to [0.95, 1.05] and slewed by at most 50 ppm/tick "
            "(0.5 percentage points/s); fixed 1x playback is the matched "
            "control.",
            "Playback starts at target; a queue that cannot cover a full "
            "nonfinal block enters rebuffer with no source consumption, "
            "output content or new rate command, and an over-capacity arrival "
            "is rejected whole.",
            "The elastic fixture rejects invalid ratios and noncontiguous "
            "starts with zero consumption, rejects full-queue input as "
            "rejected_backpressure without dropping older input, and exposes "
            "no jitter-buffer reordering.",
        ],
        "assets": [
            "Task-local synthetic traces and virtual clocks only; no PCM, "
            "corpus, weights, network capture, device or licensed runtime is "
            "added by this survey.",
        ],
        "local_outcomes": [
            {"status": "local_historical_synthetic",
             "finding": "Mean absolute live queue error was 12.569 versus "
                        "240.800 source samples at +1000 ppm and 17.806 versus "
                        "133.483 at -1000 ppm; a 400 ms delivery hold produced "
                        "one 3360-sample (210 ms) rebuffer in both runs; "
                        "+60,000 ppm overflowed at virtual sample 241280 "
                        "versus 109280. These are non-qualifying virtual-clock "
                        "controls, not device results.",
             "pin": "docs/task-evidence/buffer-occupancy-controller/README.md"},
            {"status": "local_historical_model",
             "finding": "The elastic fixture maps 80/160/240-sample chunks "
                        "exactly at ratio 1, changes only later chunks after a "
                        "1 -> 2 ratio update, produces a finite 320-sample tail "
                        "at ratio 0.5 and separates single-erasure parity from "
                        "PCM; it does not implement a jitter buffer or playout "
                        "pacing.",
             "pin": "docs/task-evidence/elastic-pcm-packets/README.md"},
        ],
        "reported_outcomes": [
            {"status": "reported_only",
             "finding": "S41 documents NetEq reordering, delay and time-scaling "
                        "concepts; the registry pins no NetEq revision, trace "
                        "or measured result.",
             "pin": "research/category_registry.json"},
        ],
        "limits": [
            "No receive timestamp domain, sequence reordering, loss-driven "
            "delay target, concealment decision or codec integration is "
            "executed by an adaptive buffer.",
            "Virtual ticks are not wall time; no device underrun, callback "
            "deadline, buffer fill/flush or availability measurement exists.",
        ],
    },
    {
        "family": "Acceleration/deceleration",
        "catalogued_text": "Acceleration/deceleration",
        "component_ids": [
            "buffer-occupancy-controller",
            "rubber-band-r3-offline",
            "rubber-band-r3-streaming",
            "ffmpeg-atempo",
        ],
        "comparison_inputs": [
            "Synthetic source-timestamped schedules at 1x, 1.25x, 1.5x, 0.8x "
            "and 0.9x for the offline OLA/WSOLA fixture; rational atempo "
            "schedules including 5/4, 4/5, 3/2, 3/4 and 11/10; controller "
            "speed commands within +/-5%.",
            "Synthetic 512-sample-grain streaming frames at the fixed "
            "160-sample v0 boundary, plus whole-clip feeds.",
            "Rebuffer, drift, final-partial and transient locations are "
            "synthetic and source-timestamped.",
        ],
        "controls": [
            "Identity 1x passthrough; fixed 1x against the occupancy "
            "controller; unsmoothed rate step and varispeed are explicit "
            "adverse controls, never substitutes.",
            "Declared rate domain, monotone source maps, bounded FIFO, finite "
            "drain and exact target-length checks.",
            "Controller output is capped at +/-5% and slewed; these are "
            "automatic playout corrections, not user-selected speed changes.",
        ],
        "assets": [
            "Generated synthetic stimuli only; no recording, corpus, model, "
            "third-party binary, licensed runtime or device is used.",
        ],
        "local_outcomes": [
            {"status": "local_historical_synthetic",
             "finding": "Offline OLA/WSOLA cases mapped identity 19200 -> "
                        "19200, 1.25x -> 15360, 1.5x -> 12800, 0.8x -> 24000 "
                        "and 0.9x -> 21333 with zero duration error; a "
                        "1600-sample uncompensated rebuffer deficit and a "
                        "transient proxy of 102 versus 40 samples remain "
                        "recorded gates.",
             "pin": "docs/task-evidence/rubber-band-r3-offline/README.md"},
            {"status": "local_historical_synthetic",
             "finding": "Streaming OLA/WSOLA passed 32/32 tests but its "
                        "duration relative error +0.0367552310 fails the "
                        "proposed 1 ms/s gate; an 800-sample input "
                        "interruption drained 32 buffered samples and refilled "
                        "128, and first output appeared at input frame 3 "
                        "(30 ms).",
             "pin": "docs/task-evidence/rubber-band-r3-streaming/README.md"},
            {"status": "local_historical_synthetic",
             "finding": "The atempo reference reached exact target output "
                        "length with zero duration error for every rational "
                        "schedule; rebuffer and final-partial behavior are "
                        "synthetic tick models, not FFmpeg parity or device "
                        "timing.",
             "pin": "docs/task-evidence/ffmpeg-atempo/README.md"},
        ],
        "reported_outcomes": [
            {"status": "reported_only",
             "finding": "S41 supplies the NetEq time-scaling lead; no local "
                        "NetEq acceleration, deceleration or stretch execution "
                        "is recorded.",
             "pin": "research/category_registry.json"},
        ],
        "limits": [
            "No adaptive playout controller is wired to a real "
            "packet-arrival process; no device clock, underrun or recovery "
            "measurement exists.",
            "Fixed-rate and user-selected time-scale evidence cannot be "
            "pooled with automatic jitter or drift correction.",
        ],
    },
    {
        "family": "PLC integration",
        "catalogued_text": "PLC integration",
        "component_ids": [
            "linear-interpolation-plc",
            "pitch-period-repeat-plc",
            "zero-fill-plc",
            "opus-1-4-standard-decoder-plc",
            "autoregressive-plc",
            "elastic-pcm-packets",
        ],
        "comparison_inputs": [
            "Frozen synthetic 16 kHz mono f32 160-sample frames; 250-frame / "
            "40,000-sample cohorts with fixed erasure masks and a 2.5 s "
            "stream.",
            "Erasure masks include isolated, two-frame and four-frame bursts "
            "across voiced, unvoiced and silence strata.",
        ],
        "controls": [
            "Identity clean delivery, zero fill, hold and linear "
            "interpolation; the decoder-style candidate is never substituted "
            "for a codec output.",
            "Concealed slots carry result flag 4 with valid_count=0 and "
            "cannot satisfy sample conservation; stale, duplicate, "
            "out-of-order, nonfinite, short, missing and bad-shape frames are "
            "rejected.",
            "Maximum four-frame burst; the 800-sample host buffer is an "
            "adapter scheduling choice, not intrinsic candidate delay.",
        ],
        "assets": [
            "Generated surrogate signals only; no Opus library, packet trace, "
            "network capture, weights, corpus or listening panel is used.",
        ],
        "local_outcomes": [
            {"status": "local_historical_synthetic",
             "finding": "Linear interpolation scored 11.820617 dB SI-SDR and "
                        "0.949594 STOI versus zero fill at 10.983909 dB and "
                        "0.951020 on one frozen synthetic cohort; this "
                        "improves SI-SDR but not STOI and is not a perceptual "
                        "result.",
             "pin": "docs/task-evidence/linear-interpolation-plc/README.md"},
            {"status": "local_historical_synthetic",
             "finding": "Pitch-period repeat scored 22.139532 dB SI-SDR and "
                        "0.851298 STOI versus zero fill at 13.589343 / "
                        "0.807333; it remained a synthetic candidate with no "
                        "held-out or listening result.",
             "pin": "docs/task-evidence/pitch-period-repeat-plc/README.md"},
            {"status": "local_historical_synthetic",
             "finding": "Zero fill scored 11.790410 dB SI-SDR and 0.876922 "
                        "STOI and regressed against hold by 0.117563 dB "
                        "SI-SDR and 0.000352 lost-region RMSE, recorded as an "
                        "explicit gate.",
             "pin": "docs/task-evidence/zero-fill-plc/README.md"},
            {"status": "local_historical_synthetic",
             "finding": "The decoder-PLC-style surrogate scored 11.089522 dB "
                        "SI-SDR and 0.946857 STOI; it lost SI-SDR and "
                        "lost-region RMSE to all three controls while gaining "
                        "STOI, and no Opus codec or packet trace was "
                        "executed.",
             "pin": "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md"},
        ],
        "reported_outcomes": [
            {"status": "reported_only",
             "finding": "S41 names PLC as part of NetEq playout; no local "
                        "codec-native PLC integration or jitter-buffer "
                        "concealment decision is recorded.",
             "pin": "research/category_registry.json"},
        ],
        "limits": [
            "All PLC fixtures run at the host delivery-adapter boundary; none "
            "is integrated with a reordering jitter buffer, loss-driven delay "
            "target or codec decoder.",
            "No rights-cleared speech, independent listening or held-out "
            "generalization is available.",
        ],
    },
]
ML_AUDIT: Dict[str, Any] = {
    "catalogued_text": "No ML requirement",
    "audited": True,
    "component_ids": [],
    "result": "no_ml_family_catalogued",
    "findings": [
        "The registry records 'No ML requirement' for ENG-03; no learned "
        "jitter-buffer, delay estimator or playout policy is catalogued.",
        "Neural PLC and codec variants belong to the conditional "
        "codec/packetization category; they are not an ENG-03 method family.",
        "No ML asset, weight, runtime or evaluation is present, so there is "
        "no missing ML result to promote.",
    ],
    "missing_evidence": [
        "No catalogued ML family exists to evaluate; any future learned "
        "playout policy needs its own category record, rights scope and "
        "matched cohort.",
    ],
}

GAP_DEFINITIONS: List[Dict[str, Optional[str]]] = [
    {"id": "ENG-03-G1",
     "statement": "No local NetEq jitter-buffer trace replay, timestamp-domain "
                  "reordering run or codec-integrated playout execution exists "
                  "for the S41 lead.",
     "follow_up_task_id": "SDK-WEBRTC-NETEQ",
     "no_task_reason": None,
     "reopen_condition": "Pin a permitted NetEq source/version, a "
                         "timestamped packet trace, loss-driven delay policy "
                         "and target playout evidence."},
    {"id": "ENG-03-G2",
     "statement": "No matched buffer-occupancy controller and fixed-1x run "
                  "exists on a pinned variable-count actuator with "
                  "instrumented playout; virtual-clock traces add no device "
                  "underrun evidence.",
     "follow_up_task_id": "SDK-CAPSC-BUFFER-OCCUPANCY-PACING",
     "no_task_reason": None,
     "reopen_condition": "Pin a permitted variable-count actuator, target "
                         "clock and instrumented FIFO; record queue debt, "
                         "underruns, recovery and pace under a frozen "
                         "workload."},
    {"id": "ENG-03-G3",
     "statement": "PLC fixtures are standalone host-adapter controls with no "
                  "reordering jitter buffer, loss-driven delay target or "
                  "codec-native concealment decision.",
     "follow_up_task_id": None,
     "no_task_reason": "Board PLC tasks are done implementation tasks under "
                       "the Enhancement profile and SDK-PIPE-RECEIVE is a "
                       "blocked pipeline task; no feasibility follow-up owns "
                       "PLC/jitter-buffer integration.",
     "reopen_condition": "Pin a permitted codec-native PLC and a jitter-buffer "
                         "integration scope under the Restoration or Pipeline "
                         "profile, with loss-driven delay and concealment "
                         "decisions recorded separately."},
]

QUOTE_CHECKS: Dict[str, List[Tuple[str, str]]] = {
    "source:audio_categories.md": [
        ("ENG-03 — Jitter buffering and adaptive playout",
         "catalogued category name"),
        ("Adaptive buffers; acceleration/deceleration; PLC integration",
         "classical method families"),
        ("API block size is not total latency; distinguish adaptive playout "
         "from user-selected speed control.",
         "comparison boundary"),
    ],
    "sdk:docs/task-evidence/buffer-occupancy-controller/README.md": [
        ("Mean absolute live queue error: **12.569 vs 240.800** source samples",
         "positive drift outcome"),
        ("**17.806 vs 133.483**", "negative drift outcome"),
        ("3360 playout samples (210 ms)", "rebuffer outcome"),
        ("Overflow at virtual sample **241280 vs 109280**",
         "overflow outcome"),
        ("clamped to `[0.95, 1.05]`", "rate clamp"),
        ("at most 50 ppm/tick (0.5 percentage points/s)", "rate slew"),
        ("These limits are not device specs.", "device boundary"),
    ],
    "sdk:docs/task-evidence/elastic-pcm-packets/README.md": [
        ("Ratio `1 → 2`", "ratio update"),
        ("finite 320-sample tail", "finite drain"),
        ("rejected_backpressure", "bounded queue"),
    ],
    "sdk:docs/task-evidence/rubber-band-r3-offline/README.md": [
        ("`1.25×` `19200 → 15360`", "rate mapping"),
        ("records a `1600`-sample", "rebuffer control"),
        ("candidate click width `102` versus identity", "transient gate"),
    ],
    "sdk:docs/task-evidence/rubber-band-r3-streaming/README.md": [
        ("+0.0367552310", "duration gate"),
        ("interrupts input for `800` samples", "rebuffer interruption"),
        ("`10,294` delivered content samples", "delivered content"),
    ],
    "sdk:docs/task-evidence/ffmpeg-atempo/README.md": [
        ("duration error is 0 samples in all scenarios", "exact duration"),
    ],
    "sdk:docs/task-evidence/linear-interpolation-plc/README.md": [
        ("11.820617", "candidate SI-SDR"),
        ("0.949594", "candidate STOI"),
        ("800-sample buffering delay", "adapter buffer"),
    ],
    "sdk:docs/task-evidence/pitch-period-repeat-plc/README.md": [
        ("22.139532", "candidate SI-SDR"),
        ("0.851298", "candidate STOI"),
    ],
    "sdk:docs/task-evidence/zero-fill-plc/README.md": [
        ("11.790410", "candidate SI-SDR"),
        ("0.876922", "candidate STOI"),
        ("-0.117563", "hold regression"),
    ],
    "sdk:docs/task-evidence/opus-1-4-standard-decoder-plc/README.md": [
        ("11.089522", "candidate SI-SDR"),
        ("0.946857", "candidate STOI"),
        ("No Opus claim.", "no Opus claim"),
    ],
    "source:audio-benchmark-platform/plan/swarm/handoffs/SDK-FND-ELASTIC.md": [
        ("no codec, device, network, paced-load or release qualification",
         "elastic boundary"),
    ],
    "source:audio-benchmark-platform/plan/swarm/handoffs/SDK-BUFFER-OCCUPANCY-CONTROLLER.md": [
        ("non-qualifying controls, not device results", "buffer boundary"),
    ],
    "source:audio-benchmark-platform/plan/swarm/handoffs/SDK-RUBBER-BAND-R3-OFFLINE.md": [
        ("proposal_only_not_qualified", "offline disposition"),
    ],
    "source:audio-benchmark-platform/plan/swarm/handoffs/SDK-RUBBER-BAND-R3-STREAMING.md": [
        ("synthetic, `incomplete` / `DEFER`", "streaming disposition"),
    ],
}

GATES: List[Tuple[str, str]] = [
    ("rights_cleared_corpus",
     "Rights-cleared frozen packet traces and media cohort for the intended "
     "workload."),
    ("pinned_runtime_and_assets",
     "Pinned permitted NetEq/PLC/actuator revision, assets and license "
     "notices with exact scope."),
    ("independent_listening",
     "Independent listening for intelligibility, naturalness and pitch; "
     "synthetic proxies cannot qualify."),
    ("target_device_pacing",
     "Measured target-device pacing, clock, rebuffer, deadline and resource "
     "evidence."),
    ("provider_intake",
     "Licensing review and opt-in provider intake; no registration before "
     "approval."),
    ("public_default_selection",
     "Explicit public default decision; currently off and unregistered."),
    ("exact_reference_parity",
     "Exact parity with an approved NetEq or codec reference for the same "
     "timestamped inputs."),
    ("independent_review_and_board",
     "Independent review and board transition after task-local evidence."),
]


class Rejected(Exception):
    """Raised before any state change when an input fails validation."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    """Canonical JSON: sorted keys, compact separators, no NaN/Infinity."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def _reject_duplicate(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise Rejected("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise Rejected("nonfinite_json_constant:" + token)


def strict_json_bytes(raw: bytes) -> Dict[str, Any]:
    try:
        payload = json.loads(raw.decode("utf-8"),
                             object_pairs_hook=_reject_duplicate,
                             parse_constant=_reject_constant)
    except Rejected:
        raise
    except (UnicodeError, ValueError) as error:
        raise Rejected("invalid_json:" + type(error).__name__) from error
    if not isinstance(payload, dict):
        raise Rejected("root_not_object")
    return payload


def strict_json_path(path: Path) -> Dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise Rejected("missing_file:" + str(path)) from error
    return strict_json_bytes(raw)


def board_snapshot_bytes(board: Dict[str, Any]) -> bytes:
    """Stable identity/mode fields only; mutable board status is not pinned."""
    tasks = _index_by_id(board.get("tasks"), "tasks")
    selected: Dict[str, Any] = {}
    for task_id in BOARD_PIN_TASK_IDS:
        task = tasks.get(task_id)
        if task is None:
            raise Rejected("board_snapshot_task_missing:" + task_id)
        selected[task_id] = {field: task.get(field) for field in BOARD_PIN_FIELDS}
    return canonical_bytes(selected) + b"\n"


def _index_by_id(items: Any, label: str) -> Dict[str, Dict[str, Any]]:
    if not isinstance(items, list):
        raise Rejected("bad_record_list:" + label)
    result: Dict[str, Dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise Rejected("bad_record:" + label)
        if item["id"] in result:
            raise Rejected("duplicate_record_id:" + item["id"])
        result[item["id"]] = item
    return result


def validate_pins() -> Dict[str, bool]:
    verified: Dict[str, bool] = {}
    for relative, expected in SOURCE_PINS.items():
        path = SOURCE_ROOT / relative
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise Rejected("source_pin_missing:" + relative) from error
        actual = sha256(board_snapshot_bytes(strict_json_bytes(raw))) if (
            relative in SOURCE_PIN_SELECTORS) else sha256(raw)
        if actual != expected:
            raise Rejected("source_pin_mismatch:" + relative)
        verified["source:" + relative] = True
    for relative, expected in BOUNDARY_PINS.items():
        path = SDK_ROOT / relative
        try:
            actual = sha256(path.read_bytes())
        except OSError as error:
            raise Rejected("boundary_pin_missing:" + relative) from error
        if actual != expected:
            raise Rejected("boundary_pin_mismatch:" + relative)
        verified[relative] = True
    return verified


def validate_quotes() -> Dict[str, bool]:
    """Every cited phrase must still appear in its pinned source bytes."""
    verified: Dict[str, bool] = {}
    for key, checks in QUOTE_CHECKS.items():
        namespace, relative = key.split(":", 1)
        root = SOURCE_ROOT if namespace == "source" else SDK_ROOT
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except OSError as error:
            raise Rejected("quote_pin_missing:" + key) from error
        for phrase, label in checks:
            if phrase not in text:
                raise Rejected("quote_drift:" + key + ":" + label)
        verified[key] = True
    return verified


def _catalogue() -> Dict[str, Any]:
    registry = strict_json_path(SOURCE_ROOT / "research/category_registry.json")
    inventory = strict_json_path(
        SOURCE_ROOT / "audio-benchmark-platform/plan/INVENTORY.json")
    backlog = strict_json_path(SOURCE_ROOT / "research/task_backlog.json")
    registry_categories = _index_by_id(registry.get("categories"),
                                       "registry.categories")
    registry_sources = _index_by_id(registry.get("sources"),
                                    "registry.sources")
    inventory_taxonomy = _index_by_id(inventory.get("taxonomy"),
                                      "inventory.taxonomy")
    category = registry_categories.get(CATEGORY_ID)
    inventory_row = inventory_taxonomy.get(CATEGORY_ID)
    if category is None or inventory_row is None:
        raise Rejected("category_missing:" + CATEGORY_ID)
    if category.get("name") != "Jitter buffering and adaptive playout":
        raise Rejected("category_name_mismatch")
    if category.get("source_ids") != ["S41"]:
        raise Rejected("category_source_ids_mismatch")
    for field in ("name", "group", "scope", "purpose", "output_kind",
                  "method_families", "input_output",
                  "live_or_comparison_boundary", "source_ids",
                  "discovery_status", "candidate_census_status",
                  "benchmark_status"):
        if category.get(field) != inventory_row.get(field):
            raise Rejected("registry_inventory_mismatch:" + field)
    entry = None
    for item in backlog.get("entries", []):
        if item.get("category_id") == CATEGORY_ID:
            if entry is not None:
                raise Rejected("duplicate_backlog_entry")
            entry = item
    if entry is None:
        raise Rejected("backlog_entry_missing")
    if entry.get("family_id") != "F16" or entry.get("state") != "catalogued":
        raise Rejected("backlog_entry_mismatch")
    if set(category.get("method_families", {})) != {"classic", "ml"}:
        raise Rejected("method_family_keys_mismatch")
    lead = registry_sources.get("S41")
    if lead is None:
        raise Rejected("source_lead_missing:S41")
    companion = ""
    for line in (SOURCE_ROOT / "audio_categories.md").read_text(
            encoding="utf-8").splitlines():
        if line.startswith("| **ENG-03 —"):
            companion = line
            break
    if not companion:
        raise Rejected("companion_row_missing")
    return {
        "registry_source": "research/category_registry.json",
        "companion_source": "audio_categories.md",
        "legacy_backlog_source": "research/task_backlog.json",
        "legacy_backlog_snapshot": backlog.get("snapshot"),
        "taxonomy_revision": registry.get("taxonomy_revision"),
        "survey_date": registry.get("survey_date"),
        "category": category,
        "companion_row": companion,
        "legacy_backlog_entry": entry,
        "inventory_record": {
            "id": CATEGORY_ID,
            "task": inventory_row.get("task"),
            "legacy_family": inventory_row.get("legacy_family"),
            "legacy_backlog_state": inventory_row.get("legacy_backlog_state"),
        },
    }


def build_component_matches(inventory: Dict[str, Any],
                            board: Dict[str, Any]) -> Dict[str, Any]:
    components = _index_by_id(inventory.get("components"), "components")
    tasks = _index_by_id(board.get("tasks"), "tasks")
    matches: List[Dict[str, Any]] = []
    for link in COMPONENT_LINKS:
        component_id = link["component_id"]
        component = components.get(component_id)
        if component is None:
            raise Rejected("component_missing:" + component_id)
        task_id = component.get("task", "")
        task = tasks.get(task_id)
        if task is None:
            raise Rejected("component_task_missing:" + component_id)
        evidence_path = link["evidence_path"]
        if evidence_path:
            if evidence_path not in BOUNDARY_PINS:
                raise Rejected("component_evidence_unpinned:" + evidence_path)
            evidence_sha = BOUNDARY_PINS[evidence_path]
            evidence_class = "pinned_task_local_readme"
        else:
            evidence_sha = None
            evidence_class = "board_record_only"
        matches.append({
            "component_id": component_id,
            "name": component.get("name"),
            "task_id": task_id,
            "task_mode": task.get("mode"),
            "board_status_observed": BOARD_STATUS_SNAPSHOT[task_id],
            "inventory_evidence_status": component.get("evidence_status"),
            "inventory_disposition": component.get("disposition"),
            "verification_profile": component.get("verification_profile"),
            "relationship": link["relationship"],
            "method_family": link["family"],
            "evidence_path": evidence_path or None,
            "evidence_sha256": evidence_sha,
            "evidence_class": evidence_class,
            "qualifies_candidate": False,
        })
    foundations: List[Dict[str, Any]] = []
    for link in FOUNDATION_LINKS:
        task = tasks.get(link["task_id"])
        if task is None:
            raise Rejected("foundation_task_missing:" + link["task_id"])
        evidence_path = link["evidence_path"]
        if evidence_path not in BOUNDARY_PINS:
            raise Rejected("foundation_evidence_unpinned:" + evidence_path)
        foundations.append({
            "component_id": link["component_id"],
            "task_id": link["task_id"],
            "task_mode": task.get("mode"),
            "board_status_observed": BOARD_STATUS_SNAPSHOT[link["task_id"]],
            "relationship": link["relationship"],
            "method_family": link["family"],
            "evidence_path": evidence_path,
            "evidence_sha256": BOUNDARY_PINS[evidence_path],
            "evidence_class": "pinned_task_local_readme",
            "qualifies_candidate": False,
        })
    adjacent: List[Dict[str, Any]] = []
    for link in ADJACENT_SPEED_CONTROLS:
        component_id = link["component_id"]
        component = components.get(component_id)
        if component is None:
            raise Rejected("adjacent_component_missing:" + component_id)
        task_id = component.get("task", "")
        task = tasks.get(task_id)
        if task is None:
            raise Rejected("adjacent_task_missing:" + component_id)
        evidence_path = link["evidence_path"]
        if evidence_path not in BOUNDARY_PINS and not (SDK_ROOT / evidence_path).is_file():
            raise Rejected("adjacent_evidence_missing:" + evidence_path)
        adjacent.append({
            "component_id": component_id,
            "name": component.get("name"),
            "task_id": task_id,
            "task_mode": task.get("mode"),
            "board_status_observed": BOARD_STATUS_SNAPSHOT[task_id],
            "relationship": "adjacent_user_selected_speed_control",
            "counted_as_jitter_buffer": False,
            "counted_as_adaptive_playout": False,
            "evidence_path": evidence_path,
            "qualifies_candidate": False,
        })
    return {"components": matches, "foundations": foundations,
            "adjacent_speed_controls": adjacent}


def build_gaps(board: Dict[str, Any]) -> List[Dict[str, Any]]:
    tasks = _index_by_id(board.get("tasks"), "tasks")
    gaps: List[Dict[str, Any]] = []
    for definition in GAP_DEFINITIONS:
        task_id = definition["follow_up_task_id"]
        if task_id is None:
            mode = None
            observed = "no_board_task"
        else:
            task = tasks.get(task_id)
            if task is None:
                raise Rejected("follow_up_missing:" + task_id)
            if task.get("mode") != "feasibility":
                raise Rejected("follow_up_not_feasibility:" + task_id)
            mode = task.get("mode")
            observed = BOARD_STATUS_SNAPSHOT[task_id]
        gaps.append({
            "id": definition["id"],
            "statement": definition["statement"],
            "actionable": True,
            "linked_source_ids": ["S41"],
            "follow_up_task_id": task_id,
            "follow_up_mode": mode,
            "follow_up_status_observed": observed,
            "no_task_reason": definition["no_task_reason"],
            "invented": False,
            "reopen_condition": definition["reopen_condition"],
        })
    return gaps


def build_map(catalogue: Dict[str, Any], inventory: Dict[str, Any],
              board: Dict[str, Any]) -> Dict[str, Any]:
    category = catalogue["category"]
    registry = strict_json_path(SOURCE_ROOT / "research/category_registry.json")
    sources = _index_by_id(registry.get("sources"), "registry.sources")
    source_leads: List[Dict[str, Any]] = []
    for source_id in category["source_ids"]:
        lead = sources.get(source_id)
        if lead is None:
            raise Rejected("source_lead_missing:" + source_id)
        template = SOURCE_LEADS[0]
        source_leads.append({
            "id": lead["id"],
            "title": lead.get("title"),
            "url": lead.get("url"),
            "researcher": lead.get("researcher"),
            "access_scope": lead.get("access_scope"),
            "mapped_components": template["mapped_components"],
            "historical_executions": template["historical_executions"],
            "limits": template["limits"],
        })
    links = build_component_matches(inventory, board)
    result = {
        "category_id": CATEGORY_ID,
        "owning_task": TASK,
        "name": category.get("name"),
        "group": category.get("group"),
        "scope": category.get("scope"),
        "purpose": category.get("purpose"),
        "input_output": category.get("input_output"),
        "live_or_comparison_boundary":
            category.get("live_or_comparison_boundary"),
        "source_ids": category.get("source_ids"),
        "source_leads": source_leads,
        "method_families": {
            "classic": {
                "catalogued_text": category.get("method_families", {}).get(
                    "classic"),
                "entries": copy.deepcopy(CLASSICAL),
            },
            "ml": copy.deepcopy(ML_AUDIT),
        },
        "component_matches": links["components"],
        "foundation_matches": links["foundations"],
        "adjacent_speed_controls": links["adjacent_speed_controls"],
        "gaps": build_gaps(board),
        "claims": copy.deepcopy(CLAIMS),
        "status": STATUS,
        "qualification_status": QUALIFICATION,
    }
    validate_map(result, _index_by_id(board.get("tasks"), "tasks"))
    return result


FAMILY_KEYS = {
    "family", "catalogued_text", "component_ids", "comparison_inputs",
    "controls", "assets", "local_outcomes", "reported_outcomes", "limits",
}
ML_KEYS = {"catalogued_text", "audited", "component_ids", "result",
           "findings", "missing_evidence"}
MAP_KEYS = {
    "category_id", "owning_task", "name", "group", "scope", "purpose",
    "input_output", "live_or_comparison_boundary", "source_ids",
    "source_leads", "method_families", "component_matches",
    "foundation_matches", "adjacent_speed_controls", "gaps", "claims",
    "status", "qualification_status",
}


def validate_map(payload: Any,
                 board_tasks: Dict[str, Dict[str, Any]]) -> None:
    """Validate the ENG-03 map before it is allowed to become state."""
    if not isinstance(payload, dict):
        raise Rejected("map_not_object")
    if set(payload) != MAP_KEYS:
        raise Rejected("map_key_set_mismatch")
    if payload.get("category_id") != CATEGORY_ID:
        raise Rejected("category_id_mismatch")
    if payload.get("owning_task") != TASK:
        raise Rejected("owning_task_mismatch")
    if payload.get("status") != STATUS or payload.get(
            "qualification_status") != QUALIFICATION:
        raise Rejected("map_status_mismatch")
    claims = payload.get("claims")
    if not isinstance(claims, dict) or set(claims) != set(CLAIMS):
        raise Rejected("claims_key_set_mismatch")
    for key, value in claims.items():
        if value is not False:
            raise Rejected("forbidden_claim:" + key)
    families = payload.get("method_families")
    if not isinstance(families, dict) or set(families) != {"classic", "ml"}:
        raise Rejected("method_family_mismatch")
    classic = families.get("classic")
    if not isinstance(classic, dict) or set(classic) != {
            "catalogued_text", "entries"}:
        raise Rejected("classic_family_shape_mismatch")
    entries = classic.get("entries")
    if not isinstance(entries, list) or len(entries) != 3:
        raise Rejected("classic_entry_count_mismatch")
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != FAMILY_KEYS:
            raise Rejected("classic_entry_keys_mismatch")
        if entry["family"] not in {"Adaptive buffers",
                                   "Acceleration/deceleration",
                                   "PLC integration"}:
            raise Rejected("unknown_method_family:" + str(entry["family"]))
        if not entry["component_ids"] or not entry["local_outcomes"]:
            raise Rejected("family_without_components_or_outcomes:" +
                           entry["family"])
    ml = families.get("ml")
    if not isinstance(ml, dict) or set(ml) != ML_KEYS:
        raise Rejected("ml_audit_shape_mismatch")
    if ml.get("audited") is not True:
        raise Rejected("ml_family_not_audited")
    if payload.get("source_ids") != ["S41"]:
        raise Rejected("invalid_source_ids")
    lead_ids = [lead.get("id") for lead in payload.get("source_leads", [])]
    if lead_ids != ["S41"]:
        raise Rejected("source_lead_mismatch")
    for collection in ("component_matches", "foundation_matches",
                       "adjacent_speed_controls"):
        items = payload.get(collection)
        if not isinstance(items, list):
            raise Rejected("bad_collection:" + collection)
        ids = [item.get("component_id") for item in items]
        if len(ids) != len(set(ids)):
            raise Rejected("duplicate_component_id:" + collection)
        for item in items:
            if item.get("qualifies_candidate") is not False:
                raise Rejected("component_claims_qualification:" +
                               str(item.get("component_id")))
        if collection == "adjacent_speed_controls":
            for item in items:
                if item.get("counted_as_jitter_buffer") is not False or item.get(
                        "counted_as_adaptive_playout") is not False:
                    raise Rejected("adjacent_speed_control_pooled")
    if any(key in payload for key in ("ENG-01", "ENG-02", "ENG-04",
                                      "categories", "category_scope")):
        raise Rejected("out_of_scope_category_present")
    gaps = payload.get("gaps")
    if not isinstance(gaps, list) or not gaps:
        raise Rejected("invalid_gaps")
    for gap in gaps:
        if not isinstance(gap, dict) or gap.get("invented") is not False:
            raise Rejected("invented_or_invalid_gap")
        if gap.get("actionable") is not True:
            raise Rejected("gap_not_actionable:" + str(gap.get("id")))
        task_id = gap.get("follow_up_task_id")
        if task_id is None:
            if not gap.get("no_task_reason"):
                raise Rejected("missing_no_task_reason:" +
                               str(gap.get("id", "?")))
            continue
        task = board_tasks.get(task_id)
        if task is None:
            raise Rejected("unknown_follow_up_task:" + task_id)
        if task.get("mode") != "feasibility":
            raise Rejected("follow_up_not_feasibility:" + task_id)
    for known in FOLLOW_UP_POLICY["existing_feasibility_task_ids"]:
        task = board_tasks.get(known)
        if task is None or task.get("mode") != "feasibility":
            raise Rejected("policy_task_not_feasibility:" + known)


class MapState:
    """Stable map state; rejected inputs never mutate it."""

    def __init__(self, payload: Dict[str, Any],
                 board_tasks: Dict[str, Dict[str, Any]]) -> None:
        self._payload = payload
        self._board_tasks = board_tasks

    def digest(self) -> str:
        return sha256(canonical_bytes(self._payload))

    def apply(self, raw: Any) -> Dict[str, Any]:
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        payload = strict_json_bytes(raw) if isinstance(raw, bytes) else raw
        validate_map(payload, self._board_tasks)
        self._payload = payload
        return {"status": "accepted", "state_digest": self.digest()}


def adverse(payload: Dict[str, Any],
            board_tasks: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    initial = copy.deepcopy(payload)
    state = MapState(copy.deepcopy(payload), board_tasks)
    before = state.digest()
    mutations: Dict[str, Any] = {}

    missing = copy.deepcopy(initial)
    del missing["gaps"]
    mutations["missing_required_key"] = missing

    wrong_category = copy.deepcopy(initial)
    wrong_category["category_id"] = "ENG-01"
    mutations["wrong_category"] = wrong_category

    extra_category = copy.deepcopy(initial)
    extra_category["categories"] = {"ENG-01": {}}
    mutations["out_of_scope_category"] = extra_category

    unknown = copy.deepcopy(initial)
    unknown["gaps"][0]["follow_up_task_id"] = "SDK-NOT-A-TASK"
    mutations["unknown_follow_up_task"] = unknown

    nonfeasible = copy.deepcopy(initial)
    nonfeasible["gaps"][0]["follow_up_task_id"] = "SDK-FND-ELASTIC"
    mutations["nonfeasibility_follow_up"] = nonfeasible

    invented = copy.deepcopy(initial)
    invented["gaps"][0]["invented"] = True
    mutations["invented_task_flag"] = invented

    families = copy.deepcopy(initial)
    del families["method_families"]["ml"]
    mutations["invalid_method_family"] = families

    ml_unaudited = copy.deepcopy(initial)
    ml_unaudited["method_families"]["ml"]["audited"] = False
    mutations["ml_family_not_audited"] = ml_unaudited

    source_ids = copy.deepcopy(initial)
    source_ids["source_ids"] = ["S999"]
    mutations["invalid_source_id"] = source_ids

    pooled = copy.deepcopy(initial)
    pooled["adjacent_speed_controls"][0]["counted_as_jitter_buffer"] = True
    mutations["adjacent_speed_control_pooled"] = pooled

    device_claim = copy.deepcopy(initial)
    device_claim["claims"]["device_timing"] = True
    mutations["forbidden_device_claim"] = device_claim

    qualifies = copy.deepcopy(initial)
    qualifies["component_matches"][0]["qualifies_candidate"] = True
    mutations["component_claims_qualification"] = qualifies

    mutations["duplicate_key"] = (
        b'{"category_id":"ENG-03","category_id":"ENG-03"}')
    mutations["nonfinite"] = b'{"category_id":"ENG-03","score":NaN}'
    mutations["infinity"] = b'{"category_id":"ENG-03","score":Infinity}'

    cases: Dict[str, Any] = {}
    for name, invalid in mutations.items():
        try:
            state.apply(invalid)
            cases[name] = {"status": "not_rejected", "reason": "none",
                           "state_unchanged": state.digest() == before}
        except Rejected as error:
            cases[name] = {"status": "rejected", "reason": error.reason,
                           "state_unchanged": state.digest() == before}
    after = state.digest()
    return {
        "cases": cases,
        "all_rejected": all(item["status"] == "rejected"
                            for item in cases.values()),
        "state_unchanged": all(item["state_unchanged"]
                               for item in cases.values()) and before == after,
        "state_digest_before": before,
        "state_digest_after": after,
        "valid_map_accepted": MapState(
            copy.deepcopy(initial), board_tasks).apply(
                canonical_bytes(initial))["status"] == "accepted",
    }


def repeatability() -> Dict[str, Any]:
    """Three cold-start processes hashing the canonical core report."""
    code = ("import hashlib,sys;sys.path.insert(0,sys.argv[1]);import reference;"
            "print(hashlib.sha256(reference.canonical_report_bytes("
            "reference.core_report())).hexdigest())")
    digests: List[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code, str(HERE)],
                                capture_output=True, text=True, check=True,
                                env=env)
        digests.append(result.stdout.strip())
    return {"count": 3, "method": "three_fresh_interpreters_canonical_core",
            "digests": digests, "byte_identical": len(set(digests)) == 1}


def gates() -> List[Dict[str, str]]:
    return [{"name": name, "status": "blocked", "reopen_condition": condition}
            for name, condition in GATES]


def core_report() -> Dict[str, Any]:
    pin_verification = validate_pins()
    quote_verification = validate_quotes()
    catalogue = _catalogue()
    inventory = strict_json_path(
        SOURCE_ROOT / "audio-benchmark-platform/plan/INVENTORY.json")
    board = strict_json_path(
        SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json")
    board_tasks = _index_by_id(board.get("tasks"), "tasks")
    payload = build_map(catalogue, inventory, board)
    controls = {
        "identity": {
            "category_id_is_eng_03": payload["category_id"] == CATEGORY_ID,
            "single_category_only": SCOPE["category_ids"] == [CATEGORY_ID],
            "method_family_keys_match_registry":
                set(payload["method_families"]) == {"classic", "ml"},
            "classic_families_complete": [
                entry["family"] for entry in
                payload["method_families"]["classic"]["entries"]] == [
                    "Adaptive buffers", "Acceleration/deceleration",
                    "PLC integration"],
            "source_lead_resolved": [lead["id"] for lead in
                                     payload["source_leads"]] == ["S41"],
            "component_tasks_resolved": all(
                item["task_id"] for item in payload["component_matches"]),
            "adjacent_speed_controls_not_pooled": all(
                item["counted_as_jitter_buffer"] is False and
                item["counted_as_adaptive_playout"] is False
                for item in payload["adjacent_speed_controls"]),
            "every_gap_linked_or_reasoned": all(
                gap["follow_up_task_id"] is not None or gap["no_task_reason"]
                for gap in payload["gaps"]),
        },
        "named_control": {
            "id": "fixed_1x_and_identity_and_zero_fill",
            "description": "Fixed 1x playback, identity delivery and zero-fill "
                           "are the matched controls; none is promoted.",
        },
        "candidate": {
            "id": "eng_03_category_evidence_map",
            "description": "Deterministic ENG-03 source/board/component map "
                           "with synthetic adverse controls.",
            "not_qualifying": True,
        },
        "all_present": True,
    }
    controls["all_present"] = all(controls["identity"].values())
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "task_title": TASK_TITLE,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": str(SDK_ROOT),
        "profile": PROFILE,
        "profile_application": {
            "profile": PROFILE,
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "status": "partial_synthetic_only",
            "scorer": "reference.py canonical report builder; not a corpus "
                      "scorer",
            "corpus": None,
            "cohort": None,
            "invalid_case": "adverse cases execute against a stateful "
                            "validator",
            "representative_valid_result": "ENG-03 map built from pinned "
                                           "registry, backlog, inventory and "
                                           "board records",
            "no_cohort_or_scorer_claim": True,
        },
        "status": STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "no_missing_result_qualifies_candidate": True,
        "catalogue": catalogue,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "format": FORMAT,
        "deliverable": "Task-local ENG-03 evidence map with matched method "
                       "families, components and linked feasibility "
                       "follow-ups.",
        "board_deliverable": "Match the original method families, named "
                             "source leads and historical executions to "
                             "existing components. File a linked feasibility "
                             "follow-up for any actionable gap without a "
                             "component owner.",
        "board_acceptance": "Record comparison inputs, controls, assets, "
                            "local vs reported outcomes and the release "
                            "boundary. Audit both classical and ML families "
                            "where catalogued and explain missing evidence.",
        "contract_id": f"{CONTRACT_SCHEMA_ID}:{TASK}",
        "contract_sha256": sha256((HERE / "contract.json").read_bytes()),
        "source_pins": SOURCE_PINS,
        "source_pin_selectors": SOURCE_PIN_SELECTORS,
        "boundary_pins": BOUNDARY_PINS,
        "source_pin_verification": pin_verification,
        "quote_verification": quote_verification,
        "board_status_is_observation_only": True,
        "follow_up_policy": FOLLOW_UP_POLICY,
        "controls": controls,
        "map": payload,
        "comparison_boundary": {
            "input_output": payload["input_output"],
            "live_or_comparison_boundary": payload[
                "live_or_comparison_boundary"],
            "local_evidence": "Synthetic, model-free fixtures and virtual "
                              "clocks only; no PCM, network trace, codec, "
                              "device or listening execution.",
            "reported_evidence": "S41 documentation, registry statuses, "
                                 "inventory evidence_status and board status "
                                 "are observations, not reproduced results.",
            "not_pooled": True,
            "denominators": "Exact source/output sample intervals, consumed "
                            "and produced counts, source timestamps, queue "
                            "occupancy and explicit rejection reasons must be "
                            "frozen before any later run.",
            "release_boundary": [
                "Local synthetic, reported-only and not-run outcomes remain "
                "separate; none is promoted to a component or benchmark.",
                "No quality, listening, device timing, availability, "
                "throughput or release result is claimed from this map.",
                "No audio, network trace, model, codec, scorer output or "
                "licensed asset is added, replayed or redistributed.",
                "No public SDK ABI, descriptor, provider default, engine "
                "routing, build or CI setting is changed.",
                "API block size is not total latency; adaptive playout is "
                "not user-selected speed control.",
            ],
        },
        "missing_evidence": [
            "Rights-cleared frozen packet traces and media cohort for the "
            "intended workload.",
            "Pinned permitted NetEq, PLC and actuator runtime with exact "
            "licenses.",
            "Independent listening for intelligibility, naturalness and "
            "pitch.",
            "Target-device pacing, rebuffer, clock, deadline and resource "
            "evidence.",
            "Opt-in provider intake and licensing clearance.",
            "Explicit public default selection.",
            "Exact parity with an approved external NetEq or codec "
            "reference.",
            "Independent review and board transition.",
        ],
        "adverse": adverse(payload, board_tasks),
        "evidence_classes": [
            "registry_and_companion_taxonomy",
            "legacy_backlog",
            "inventory_and_board_records",
            "pinned_task_local_component_evidence",
            "handoff_records",
            "synthetic_state_controls",
            "reported_source_lead",
        ],
        "prohibited_claims": {
            "public_benchmark_claim": "not_made",
            "quality_or_listening_claim": "not_made",
            "device_timing_or_availability_claim": "not_made",
            "release_or_publication_claim": "not_made",
            "provider_enablement": "not_made",
            "default_abi_build_or_ci_change": "not_made",
            "asset_trace_or_real_audio_added": "not_made",
            "implemented_jitter_buffer_or_adaptive_playout": "not_made",
            "opaque_pooling_of_adjacent_speed_control": "not_made",
        },
        "gates": gates(),
    }


def build_report() -> Dict[str, Any]:
    report = core_report()
    report["repeatability"] = repeatability()
    return report


def sources_bytes() -> bytes:
    """Deterministic manifest; local artifact digests come from current bytes."""
    lines = [
        "# SHA-256 pins for SDK-SURVEY-ENG-03 (ENG-03 only).",
        "# source: paths are relative to SOURCE_ROOT; other paths are "
        "SDK-worktree relative.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in sorted(BOUNDARY_PINS):
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for name in LOCAL_PIN_PATHS:
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")
