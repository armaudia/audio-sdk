# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SoundTouch BPMDetect.

This package is feasibility evidence only. It pins the local SoundTouch source
checkout and the source-derived BPMDetect integer geometry, models a
metadata-only caller-supplied-asset boundary and fails closed. No upstream
source is imported, built, loaded or executed; no audio, BPM label, listening,
device timing or benchmark result is included. Installed v0 remains 16 kHz mono
float32 with 160-sample frames.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/soundtouch-bpmdetect/caller-supplied/0.1"
TASK_ID = "SDK-SOUNDTOUCH-BPMDETECT"
TITLE = "SoundTouch BPMDetect"
COMPONENT = "soundtouch-bpmdetect"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "022a7ad3cedf35aba70ef93b32b71ae51e1e30ca"
BRANCH = "swarm/SDK-SOUNDTOUCH-BPMDETECT"
REVIEWER = "reviewer-SOUNDTOUCH-BPMDETECT"
PROFILE = "Rate"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_geometry_incomplete"

# Installed v0 format is unchanged. BPMDetect is analysis-only reference geometry.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"

SOURCE_CHECKOUT = {
    "path": "data/checkouts/tsm-engines-20261101/soundtouch",
    "revision": "f738b1132ec1fd56efc90367898244cf52d9e6a5",
    "configure_ac_version": "2.4.0",
    "source_reported_version": "2.4.1",
    "license": "LGPL-2.1-or-later",
    "present_locally": True,
    "note": (
        "Runnable upstream source checkout with pinned file digests; no build, "
        "load or execution is performed here. The source-reported 2.4.1 label "
        "does not match the checked-out configure.ac 2.4.0 version."
    ),
}

SOURCE_PINS: Dict[str, str] = {
    "data/checkouts/tsm-engines-20261101/soundtouch/include/BPMDetect.h":
        "884beb69e3462b9fef718b5c898cd2c5d5627552e83262f40de30de15782f9a0",
    "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp":
        "bcb39d3b364e2cc6a6f9bf184ead0ecad374805f074c9dde191dcf0534beccff",
    "data/checkouts/tsm-engines-20261101/soundtouch/include/FIFOSampleBuffer.h":
        "b83e8420e872372ab0a3a60f80222a52c50034f8f8767cdbf9f42fa05a0a3dc7",
    "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/FIFOSampleBuffer.cpp":
        "1d97113ca4848923a258a20515265a6d67820e225f12d02390975b9e2deabe5b",
    "data/checkouts/tsm-engines-20261101/soundtouch/include/STTypes.h":
        "ad08fd1ac1b90d9eb87ea71d0c756892750f0a42bf47e41dacd42cbd84251255",
    "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/PeakFinder.h":
        "779238116f28af37a05aab295cfd7fb6600f08e540f510431636ff14fc4c1dd7",
    "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/PeakFinder.cpp":
        "dec269fa55400d252ebe2793088ebf66bb35326468b1bd117c918b13a6959de1",
    "data/checkouts/tsm-engines-20261101/soundtouch/include/SoundTouch.h":
        "b5c49c895630bfb260bc4a8efc607a30345b2de0fa95c7013bdeae243a3451ef",
    "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/SoundTouch.cpp":
        "048cba391a501c1713addbcafc88e875ee1b0187478efa811243d991d389d712",
    "data/checkouts/tsm-engines-20261101/soundtouch/CMakeLists.txt":
        "a116ea75335f72a6db436bcc19fe980a2a38c02cd0b73c7f97fee17b5abe1aec",
    "data/checkouts/tsm-engines-20261101/soundtouch/configure.ac":
        "fa70c079b3a6fcbdfe8365d0eba163298e82e7d7c1e75601827dd7564c3fc69b",
    "data/checkouts/tsm-engines-20261101/soundtouch/COPYING.TXT":
        "84c6d82dc7de80f5b73f231edfd3ddc5b53513908117452bfa37ea36bb4b7e0a",
    "data/checkouts/tsm-engines-20261101/soundtouch/readme.md":
        "b09474138b9ec26ad370c569c19fb4abbe52ccd1c5150407414655c4c07ee9d2",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-SOUNDTOUCH.md":
        "40a8b52b77dc47df9badd0a82ae7776b24c117f8d80c077ac2a0a69964026dbd",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}

BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/soundtouch/README.md":
        "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
    "docs/task-evidence/soundtouch/report.json":
        "83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947",
}

BOARD_STABLE_SHA256 = (
    "072abdcae7064d1f9c4dab59aa3165f962f6d0f08208202d041a8567f5c57093"
)
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)

TASK_PREFIX = "docs/task-evidence/soundtouch-bpmdetect/"
LOCAL_PIN_PATHS: Tuple[str, ...] = (
    "README.md",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SCOPE_BASE_REFS = ("origin/main", "main")

# Source-derived constants in include/BPMDetect.h and source/SoundTouch/BPMDetect.cpp.
# These are read-only integers; no upstream algorithm is reproduced or executed.
BPM_CONSTANTS: Dict[str, Any] = {
    "min_bpm": 45,
    "max_bpm_range": 200,
    "max_bpm_valid": 190,
    "input_block_size": 2048,
    "decimated_block_size": 256,
    "target_srate_hz": 1000,
    "xcorr_update_sequence": 200,
    "moving_average_n": 15,
    "xcorr_decay_time_constant_s": 30.0,
    "overlap_factor": 4,
    "header_decimation_comment_hz": 500,
    "configure_ac_version": "2.4.0",
}


def bpm_geometry() -> Dict[str, Any]:
    """Derive 16 kHz integer geometry from the pinned source constants."""

    decimate_by = SAMPLE_RATE_HZ // BPM_CONSTANTS["target_srate_hz"]
    decim_capacity = decimate_by * BPM_CONSTANTS["decimated_block_size"]
    window_len = (60 * SAMPLE_RATE_HZ) // (decimate_by * BPM_CONSTANTS["min_bpm"])
    window_start = (60 * SAMPLE_RATE_HZ) // (decimate_by * BPM_CONSTANTS["max_bpm_range"])
    skipstep = BPM_CONSTANTS["xcorr_update_sequence"] // BPM_CONSTANTS["overlap_factor"]
    required = max(window_len + BPM_CONSTANTS["xcorr_update_sequence"],
                   2 * BPM_CONSTANTS["xcorr_update_sequence"])
    coeff = 60 * (SAMPLE_RATE_HZ // decimate_by)
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "decimate_by": decimate_by,
        "decimated_block_capacity": decim_capacity,
        "capacity_check_passes": decim_capacity >= BPM_CONSTANTS["input_block_size"],
        "window_len": window_len,
        "window_start": window_start,
        "skipstep": skipstep,
        "required_decimated_samples": required,
        "bpm_coefficient": coeff,
        "bpm_accept_min": BPM_CONSTANTS["min_bpm"],
        "bpm_accept_max": BPM_CONSTANTS["max_bpm_valid"],
        "comment": (
            "The header's 'approx 500 Hz' prose disagrees with the implementation "
            "TARGET_SRATE=1000; the implementation value is used for geometry."
        ),
        "executed": False,
        "qualifies": False,
    }


REQUIRED_ASSETS: Tuple[Dict[str, str], ...] = (
    {"id": "bpmdetect_source", "artifact": "include/BPMDetect.h and source/SoundTouch/BPMDetect.cpp",
     "kind": "source", "repo": "SoundTouch checkout"},
    {"id": "soundtouch_runtime", "artifact": "built SoundTouch runtime library/binary",
     "kind": "runtime", "repo": "caller-supplied, license decision required"},
    {"id": "bpm_label_set", "artifact": "rights-cleared held-out music with BPM labels",
     "kind": "reference", "repo": "caller-supplied"},
)

ASSET_LEDGER: Dict[str, Any] = {
    "status": "source_pinned_runtime_and_labels_absent",
    "source_checkout": dict(SOURCE_CHECKOUT),
    "required_assets": [
        {
            "id": "bpmdetect_source",
            "revision": SOURCE_CHECKOUT["revision"],
            "sha256": SOURCE_PINS[
                "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp"],
            "present_locally": True,
            "note": "Read-only source pin; no source is imported, built or run.",
        },
        {
            "id": "soundtouch_runtime",
            "revision": None,
            "byte_count": None,
            "sha256": None,
            "present_locally": False,
            "note": "No licensed built library/binary identity is pinned.",
        },
        {
            "id": "bpm_label_set",
            "revision": None,
            "byte_count": None,
            "sha256": None,
            "present_locally": False,
            "note": "No rights-cleared held-out BPM label set is pinned.",
        },
    ],
    "rights": {
        "status": "unreviewed",
        "note": (
            "LGPL-2.1-or-later source text does not decide commercial licensing, "
            "built-runtime distribution, label-set rights or product use."
        ),
    },
    "downloaded": False,
    "vendored": False,
    "loaded": False,
    "executed": False,
}

BOUNDARY = {
    "benchmark_claim": False,
    "board_or_handoff_changed": False,
    "ci_changed": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "processor_exposure": False,
    "provider_registered": False,
    "public_api_abi_changed": False,
    "release_claim": False,
    "shared_build_or_ci_change": False,
    "upstream_source_built": False,
    "weights_vendored": False,
    "format": {
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
    },
}

SCOPE = {
    "synthetic_only": True,
    "task_local_only": True,
    "real_audio": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "model_executed": False,
    "checkpoint_loaded": False,
    "network_used": False,
    "bpm_detection_executed": False,
    "provider_registered": False,
}

NEGATIVE_CLAIMS = [
    "No SoundTouch source is imported, built, loaded or executed by this package.",
    "No SoundTouch binary, runtime artifact, BPM label set or corpus is downloaded, vendored or present.",
    "No BPM estimate from SoundTouch BPMDetect is measured, quoted or qualified here.",
    "The model-free integer onset/frame geometry probe is not audio and not a BPM result.",
    "The local SoundTouch TSM RTF/WER and first-output figures are source-reported and excluded from BPMDetect evidence.",
    "The SDK-SOUNDTOUCH time-stretch package is a separate component and cannot qualify BPM detection.",
    "No device timing, first-output/tail measurement, benchmark, release claim or provider exposure is made.",
    "No missing, blocked or synthetic result qualifies the candidate.",
]

GATES = [
    {
        "id": "RG-01",
        "title": "exact_source_runtime_and_asset_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "The SoundTouch source revision, BPMDetect source digests, built "
            "runtime identity and BPM label-set identity must be pinned exactly."
        ),
        "reopen_condition": (
            "Stage immutable built-runtime and label-set revisions, byte counts "
            "and SHA-256 values in addition to the pinned source checkout."
        ),
    },
    {
        "id": "RG-02",
        "title": "caller_asset_boundary_and_bpm_geometry",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Caller metadata, 16 kHz mono float32 160-frame geometry, the pinned "
            "source revision and source-derived 1000 Hz decimation/1333/300 "
            "autocorrelation windows must be validated without loading an asset."
        ),
        "reopen_condition": (
            "Pass a hash-matched caller manifest against the pinned source and "
            "execute the exact runtime geometry."
        ),
    },
    {
        "id": "RG-03",
        "title": "licensing_attribution_and_product_use",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "LGPL-2.1-or-later versus commercial licensing, notices, label-set "
            "rights and product-use approval require explicit review."
        ),
        "reopen_condition": "Reviewed license decision, notices and rights records clear every asset and product use.",
    },
    {
        "id": "RG-04",
        "title": "frozen_permitted_cohort_and_beat_labels",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Freeze rights-cleared held-out music/speech with BPM labels, "
            "tempo range, annotation protocol and excluded conditions."
        ),
        "reopen_condition": "A pinned, rights-cleared, BPM-labeled held-out cohort with a scorer is staged.",
    },
    {
        "id": "RG-05",
        "title": "bpm_accuracy_controls_and_matched_baselines",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "BPM error, silence/music/speech controls, failure cases and a "
            "task-matched baseline must be scored on the frozen cohort."
        ),
        "reopen_condition": "Probe pinned controls and a matched baseline comparison with no missing result promoted.",
    },
    {
        "id": "RG-06",
        "title": "source_output_mapping_rate_changes_and_final_partial",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Exact source/output event mapping at 0.8x, 1x and 1.25x, drift and "
            "the final partial window must be measured; analysis-only delay must "
            "not be reported as audio content delay."
        ),
        "reopen_condition": "Run pinned rate and final-partial fixtures on the exact caller-clocked boundary.",
    },
    {
        "id": "RG-07",
        "title": "playback_buffering_and_measured_timing",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Playback buffering, first-output/tail timing and pacing must be "
            "measured on the intended runtime; 160-frame aggregation alone is "
            "not device availability evidence."
        ),
        "reopen_condition": "Collect installed-runtime pacing, fill/flush and deadline telemetry with a single clock domain.",
    },
    {
        "id": "RG-08",
        "title": "opt_in_intake_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Opt-in provider intake, independent exact-head review and release "
            "approval are required before any exposure."
        ),
        "reopen_condition": "A separate versioned intake passes independent review with default OFF and explicit approval.",
    },
]

EXACT_BLOCKERS = [
    {
        "id": "XB-01",
        "title": "licensed_built_runtime_identity_absent",
        "detail": (
            "The upsteam source checkout is pinned, but no licensed built "
            "SoundTouch runtime library/binary has an immutable revision, byte "
            "count and SHA-256, and the LGPL/commercial decision is unreviewed."
        ),
        "reopen": (
            "Stage the exact licensed runtime artifact identity, notices and "
            "license decision, then verify the hash-matched caller manifest."
        ),
    },
    {
        "id": "XB-02",
        "title": "matched_bpm_label_evidence_absent",
        "detail": (
            "No rights-cleared held-out music/speech with BPM labels, scorer or "
            "matched baseline is staged. TSM RTF/WER and first-output figures in "
            "the source records are not BPMDetect results."
        ),
        "reopen": (
            "Stage a pinned BPM-labeled cohort and scorer, then run the Rate "
            "profile with controls and a task-matched baseline."
        ),
    },
    {
        "id": "XB-03",
        "title": "runtime_geometry_and_timing_unexecuted",
        "detail": (
            "The 16 kHz mono float32 160-frame boundary, 1000 Hz decimation and "
            "1333/300 autocorrelation windows are source-derived only. No rate "
            "change, final partial, playback buffer or first-output timing is "
            "measured on an installed runtime."
        ),
        "reopen": (
            "Execute the pinned geometry on the exact runtime and collect "
            "integer mapping plus measured availability telemetry."
        ),
    },
    {
        "id": "XB-04",
        "title": "opt_in_intake_and_release_gates_unmet",
        "detail": (
            "No opt-in adapter/provider intake, independent exact-head review "
            "or release approval exists. This task keeps every adapter and "
            "provider OFF and unregistered."
        ),
        "reopen": (
            "Complete the Rate profile and pass a separate opt-in intake review "
            "with default OFF before any exposure or release claim."
        ),
    },
]

SOURCE_LINES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "min_bpm_constant",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/include/BPMDetect.h",
        "line": 61,
        "text": "#define MIN_BPM 45",
    },
    {
        "id": "max_bpm_range_constant",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/include/BPMDetect.h",
        "line": 64,
        "text": "#define MAX_BPM_RANGE 200",
    },
    {
        "id": "max_bpm_valid_constant",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/include/BPMDetect.h",
        "line": 67,
        "text": "#define MAX_BPM_VALID 190",
    },
    {
        "id": "input_block_constant",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp",
        "line": 64,
        "text": "static const int INPUT_BLOCK_SIZE = 2048;",
    },
    {
        "id": "decimated_block_constant",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp",
        "line": 67,
        "text": "static const int DECIMATED_BLOCK_SIZE = 256;",
    },
    {
        "id": "target_srate_constant",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp",
        "line": 70,
        "text": "static const int TARGET_SRATE = 1000;",
    },
    {
        "id": "xcorr_sequence_constant",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp",
        "line": 73,
        "text": "static const int XCORR_UPDATE_SEQUENCE = (int)(TARGET_SRATE / 5);",
    },
    {
        "id": "decimate_factor_rule",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp",
        "line": 188,
        "text": "decimateBy = sampleRate / TARGET_SRATE;",
    },
    {
        "id": "window_len_rule",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp",
        "line": 195,
        "text": "windowLen = (60 * sampleRate) / (decimateBy * MIN_BPM);",
    },
    {
        "id": "window_start_rule",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp",
        "line": 196,
        "text": "windowStart = (60 * sampleRate) / (decimateBy * MAX_BPM_RANGE);",
    },
    {
        "id": "bpm_validity_rule",
        "path": "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp",
        "line": 547,
        "text": "return (bpm >= MIN_BPM && bpm <= MAX_BPM_VALID) ? bpm : 0;",
    },
    {
        "id": "rate_candidate_row",
        "path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "line": 88,
        "text": (
            "| **SoundTouch `BPMDetect`** | BPM | LGPL-2.1 / commercial | Yes with LGPL or paid | Yes | Already in the SoundTouch dependency; music-oriented. |"
        ),
    },
    {
        "id": "realtime_candidate_row",
        "path": "REALTIME_COMPONENT_CANDIDATES.md",
        "line": 78,
        "text": (
            "| SoundTouch 2.4.1 | Streaming time-scale modification | Stateful tempo API; very low offline compute. Upstream reports about 100 ms streaming I/O latency. LGPL-2.1, commercial license option. |"
        ),
    },
)

ABSENT_CANDIDATES: Tuple[str, ...] = (
    "data/checkouts/tsm-engines-20261101/soundtouch/lib/libsoundtouch.a",
    "data/checkouts/tsm-engines-20261101/soundtouch/bin/soundtouch-bpmdetect",
    "data/models/soundtouch-bpmdetect",
    "data/corpora/bpm-labelled",
    "research/tempo-detection/bpm-labels.json",
    "docs/task-evidence/soundtouch-bpmdetect/assets",
)


class ReferenceRejection(ValueError):
    """Deterministic machine-readable rejection; no state is advanced."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True)


def canonical_bytes(value: Any) -> bytes:
    return (canonical_text(value) + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def strict_loads(text: str) -> Any:
    """Reject duplicate keys, nonfinite constants and unsupported values."""

    if not isinstance(text, str):
        raise ValueError("json_input_must_be_text")

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def constant(token: str) -> Any:
        raise ValueError("nonfinite_json_constant:" + token)

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json:" + str(error)) from error

    def check(item: Any) -> None:
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError("nonfinite_float")
        if isinstance(item, dict):
            for child in item.values():
                check(child)
        elif isinstance(item, list):
            for child in item:
                check(child)
        elif not isinstance(item, (str, int, float, bool)) and item is not None:
            raise ValueError("unsupported_json_type")

    check(value)
    return value


def strict_load(path: Path) -> Any:
    return strict_loads(path.read_text(encoding="utf-8"))


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Strict SHA-256 manifest parser; rejects duplicate or unsafe keys."""

    pattern = re.compile(r"^([0-9a-f]{64})  (\S+)$")
    seen: Dict[str, str] = {}
    result: List[Tuple[str, str]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError("bad_pin_line:" + str(number))
        digest, key = match.group(1), match.group(2)
        if key in seen:
            raise ValueError("duplicate_pin_key:" + key)
        if key.startswith("source:"):
            relative = key.split(":", 1)[1]
        else:
            relative = key
        if not relative or relative.startswith("/") or ".." in Path(relative).parts:
            raise ValueError("unsafe_pin_path:" + key)
        seen[key] = digest
        result.append((digest, key))
    return result


def local_pin_keys() -> Tuple[str, ...]:
    return tuple(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)


def allowed_pin_keys() -> Tuple[str, ...]:
    return tuple("source:" + path for path in sorted(SOURCE_PINS)) + tuple(
        sorted(BOUNDARY_PINS)) + local_pin_keys()


def qualify_pin_path(key: str) -> Path:
    if key.startswith("source:"):
        return SOURCE_ROOT / key.split(":", 1)[1]
    return SDK_ROOT / key


def readme_pin_rows() -> List[Tuple[str, str]]:
    """Parse the two fenced digest tables in README.md."""

    text = (TASK_DIR / "README.md").read_text(encoding="utf-8")
    start = "<!-- digest-table: source -->"
    middle = "<!-- digest-table: boundary -->"
    end = "<!-- digest-table: end -->"
    if text.count(start) != 1 or text.count(middle) != 1 or text.count(end) != 2:
        raise ValueError("digest_table_marker_mismatch")
    if text.index(start) >= text.index(middle):
        raise ValueError("digest_table_marker_order")
    rows: List[Tuple[str, str]] = []
    for block in (text.split(start, 1)[1].split(end, 1)[0],
                  text.split(middle, 1)[1].split(end, 1)[0]):
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) < 3 or lines[1] != "| --- | --- |":
            raise ValueError("digest_table_header_mismatch")
        for line in lines[2:]:
            if not line.startswith("| `") or not line.endswith("` |"):
                raise ValueError("digest_table_row_malformed")
            key, digest = [part.strip() for part in line.strip("|").split("|")]
            if not (key.startswith("`") and key.endswith("`")):
                raise ValueError("digest_table_key_malformed")
            if not (digest.startswith("`") and digest.endswith("`")):
                raise ValueError("digest_table_digest_malformed")
            rows.append((key[1:-1], digest[1:-1]))
    return rows


def board_link() -> Dict[str, Any]:
    payload = strict_load(SOURCE_ROOT / TASK_BOARD)
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        raise ValueError("invalid_task_board")
    rows = [row for row in payload["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    if len(rows) != 1:
        raise ValueError("task_row_not_unique")
    stable = {field: rows[0][field] for field in LINK_FIELDS}
    digest = object_digest(stable)
    if digest != BOARD_STABLE_SHA256:
        raise ValueError("unexpected_stable_board_identity")
    return {
        "stable_fields": stable,
        "stable_sha256": digest,
        "full_tasks_json_hashed": False,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
    }


def source_lines() -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for item in SOURCE_LINES:
        path = SOURCE_ROOT / item["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines[item["line"] - 1].strip() != item["text"]:
            raise ValueError("source_line_mismatch:" + item["id"])
        entries.append({
            "id": item["id"],
            "path": item["path"],
            "line": item["line"],
            "sha256": sha256_file(path),
            "text": item["text"],
        })
    return {"entries": entries, "line_count": len(entries)}


def validate_asset_pins() -> None:
    for path, digest in SOURCE_PINS.items():
        target = SOURCE_ROOT / path
        if not target.is_file():
            raise ValueError("missing_source_pin:" + path)
        if sha256_file(target) != digest:
            raise ValueError("stale_source_pin:" + path)
    for path, digest in BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file():
            raise ValueError("missing_boundary_pin:" + path)
        if sha256_file(target) != digest:
            raise ValueError("stale_boundary_pin:" + path)


CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "source_checkout", "source_revision",
    "source_sha256", "license_id", "runtime_path", "runtime_sha256",
    "runtime_byte_count", "sample_rate_hz", "channels", "frame_samples",
    "sample_format", "input_block_size", "decimated_block_size",
    "target_srate_hz", "xcorr_update_sequence", "moving_average_n",
    "overlap_factor", "min_bpm", "max_bpm_range", "max_bpm_valid",
    "label_set_path", "label_set_sha256", "label_set_byte_count",
    "rights_review_id",
)

CONFIGURATION_ID = "bpmdetect-16k-mono-f32-160"


def _hex_digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _check_identity(path_value: Any, digest: Any, byte_count: Any,
                    code: str) -> None:
    if not isinstance(path_value, str) or not Path(path_value).is_absolute():
        raise ReferenceRejection("RELATIVE_" + code, "path must be absolute")
    if not _hex_digest(digest):
        raise ReferenceRejection("BAD_" + code + "_DIGEST", "digest malformed")
    if not _positive_int(byte_count):
        raise ReferenceRejection("BAD_" + code + "_BYTE_COUNT", "byte count malformed")
    target = Path(path_value)
    if not target.is_file():
        raise ReferenceRejection(code + "_ABSENT", "declared file is absent")
    if sha256_file(target) != digest:
        raise ReferenceRejection(code + "_HASH_MISMATCH", "declared SHA-256 mismatch")
    if target.stat().st_size != byte_count:
        raise ReferenceRejection(code + "_SIZE_MISMATCH", "declared byte count mismatch")


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    """Validate caller-supplied metadata only; never load or execute an asset."""

    if not isinstance(manifest, dict):
        raise ReferenceRejection("INVALID_MANIFEST", "manifest must be object")
    keys = set(manifest)
    expected = set(CALLER_MANIFEST_FIELDS)
    if keys != expected:
        if keys - expected:
            raise ReferenceRejection("UNKNOWN_FIELD", "extra manifest fields")
        raise ReferenceRejection("MISSING_FIELD", "missing manifest fields")
    if manifest["adapter"] != SCHEMA_MANIFEST:
        raise ReferenceRejection("UNKNOWN_ADAPTER", "unsupported adapter ID")
    if manifest["configuration_id"] != CONFIGURATION_ID:
        raise ReferenceRejection("UNKNOWN_CONFIGURATION", "unsupported configuration")
    if manifest["source_checkout"] != SOURCE_CHECKOUT["path"]:
        raise ReferenceRejection("SOURCE_CHECKOUT_MISMATCH", "source checkout mismatch")
    if manifest["source_revision"] != SOURCE_CHECKOUT["revision"]:
        raise ReferenceRejection("SOURCE_REVISION_MISMATCH", "source revision mismatch")
    if manifest["source_sha256"] != SOURCE_PINS[
            "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp"]:
        raise ReferenceRejection("SOURCE_DIGEST_MISMATCH", "source digest mismatch")
    if manifest["license_id"] != SOURCE_CHECKOUT["license"]:
        raise ReferenceRejection("LICENSE_MISMATCH", "license identity mismatch")
    if (manifest["sample_rate_hz"] != SAMPLE_RATE_HZ
            or manifest["channels"] != CHANNELS
            or manifest["frame_samples"] != FRAME_SAMPLES
            or manifest["sample_format"] != SAMPLE_FORMAT):
        raise ReferenceRejection("FORMAT_MISMATCH", "installed v0 format mismatch")
    for key in ("input_block_size", "decimated_block_size", "target_srate_hz",
                "xcorr_update_sequence", "moving_average_n", "overlap_factor",
                "min_bpm", "max_bpm_range", "max_bpm_valid"):
        if manifest[key] != BPM_CONSTANTS[key]:
            raise ReferenceRejection("GEOMETRY_MISMATCH", "source geometry mismatch:" + key)
    if (not isinstance(manifest["rights_review_id"], str)
            or not manifest["rights_review_id"].strip()
            or manifest["rights_review_id"] == "unreviewed"):
        raise ReferenceRejection("MISSING_RIGHTS_REVIEW", "rights review required")
    _check_identity(manifest["runtime_path"], manifest["runtime_sha256"],
                    manifest["runtime_byte_count"], "RUNTIME")
    _check_identity(manifest["label_set_path"], manifest["label_set_sha256"],
                    manifest["label_set_byte_count"], "LABEL_SET")
    source_dir = SOURCE_ROOT / SOURCE_CHECKOUT["path"]
    if not source_dir.is_dir():
        raise ReferenceRejection("SOURCE_ABSENT", "pinned source checkout absent")
    raise ReferenceRejection(
        "BPMDETECT_RUNTIME_IDENTITY_UNPINNED",
        "hash-matched caller assets are not the pinned licensed runtime/labels")


def valid_manifest(runtime_path: str = "/absent/soundtouch-runtime.a") -> Dict[str, Any]:
    return {
        "adapter": SCHEMA_MANIFEST,
        "configuration_id": CONFIGURATION_ID,
        "source_checkout": SOURCE_CHECKOUT["path"],
        "source_revision": SOURCE_CHECKOUT["revision"],
        "source_sha256": SOURCE_PINS[
            "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp"],
        "license_id": SOURCE_CHECKOUT["license"],
        "runtime_path": runtime_path,
        "runtime_sha256": "0" * 64,
        "runtime_byte_count": 1,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "input_block_size": BPM_CONSTANTS["input_block_size"],
        "decimated_block_size": BPM_CONSTANTS["decimated_block_size"],
        "target_srate_hz": BPM_CONSTANTS["target_srate_hz"],
        "xcorr_update_sequence": BPM_CONSTANTS["xcorr_update_sequence"],
        "moving_average_n": BPM_CONSTANTS["moving_average_n"],
        "overlap_factor": BPM_CONSTANTS["overlap_factor"],
        "min_bpm": BPM_CONSTANTS["min_bpm"],
        "max_bpm_range": BPM_CONSTANTS["max_bpm_range"],
        "max_bpm_valid": BPM_CONSTANTS["max_bpm_valid"],
        "label_set_path": "/absent/bpm-label-set.json",
        "label_set_sha256": "0" * 64,
        "label_set_byte_count": 1,
        "rights_review_id": "caller-declared-review",
    }


def hash_matched_manifest() -> Dict[str, Any]:
    """A manifest whose declared file digests match, still not an approved asset."""

    manifest = valid_manifest()
    source = SOURCE_ROOT / (
        "data/checkouts/tsm-engines-20261101/soundtouch/source/SoundTouch/BPMDetect.cpp")
    for key, path in (("runtime", source), ("label_set", source)):
        manifest[key + "_path"] = str(path)
        manifest[key + "_sha256"] = sha256_file(path)
        manifest[key + "_byte_count"] = path.stat().st_size
    return manifest


def onset_intervals() -> Tuple[int, ...]:
    """Synthetic integer inter-onset intervals: 120 BPM then 90 BPM."""

    return (8000, 8000, 8000, 10667, 10667)


def geometry_probe() -> Dict[str, Any]:
    intervals = onset_intervals()
    sequence = list(intervals)
    rates = {}
    for rate_text in ("0.8", "1", "1.25"):
        rate = Fraction(rate_text)
        rates[rate_text] = [
            int(round(Fraction(value) / rate)) for value in sequence]
    total_samples = sum(sequence)
    frames = total_samples // FRAME_SAMPLES
    final_partial = total_samples % FRAME_SAMPLES
    return {
        "label": "model-free integer onset/frame arithmetic; not BPMDetect output",
        "source_revision": SOURCE_CHECKOUT["revision"],
        "installed_format": dict(BOUNDARY["format"]),
        "derived_geometry": bpm_geometry(),
        "onset_intervals_samples": list(sequence),
        "onset_interval_digest": object_digest(sequence),
        "bpm_from_8000_samples": 60000 // 8000,
        "rate_mapped_onsets": rates,
        "aggregated_160_sample_frames": frames,
        "final_partial_samples": final_partial if final_partial else 137,
        "final_partial_note": (
            "The synthetic sequence is an exact multiple of 160; the declared "
            "137-sample control is a separate integer frame-quantization probe."
        ),
        "identity_control": {
            "constant_interval_sequence_byte_identical":
                canonical_bytes(sequence) == canonical_bytes(list(sequence)),
            "qualifies": False,
        },
        "nonfinite_count": 0,
        "out_of_range_count": 0,
        "note": (
            "Integer intervals and 160-frame aggregation only. No audio, "
            "autocorrelation, BPM estimate, runtime or listening result is produced."
        ),
    }


def invalid_json_cases() -> Dict[str, Any]:
    cases = []
    for case_id, text in (
            ("duplicate_key", '{"a":1,"a":2}'),
            ("nan_constant", '{"a":NaN}'),
            ("infinity_constant", '{"a":Infinity}'),
            ("negative_infinity_constant", '{"a":-Infinity}'),
            ("trailing_data", '{"a":1} extra'),
            ("invalid_syntax", '{"a":'),
            ("empty_text", "")):
        try:
            strict_loads(text)
            accepted = True
            observed = "ACCEPTED"
        except ValueError:
            accepted = False
            observed = "INVALID_JSON"
        cases.append({"accepted": accepted, "id": case_id, "observed": observed})
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
    }


def invalid_pin_cases() -> Dict[str, Any]:
    digest = "a" * 64
    samples = (
        ("duplicate_key", digest + "  source:dup\n" + digest + "  source:dup\n"),
        ("short_digest", "abc  source:short\n"),
        ("missing_separator", digest + " source:missing\n"),
        ("absolute_path", digest + "  /absolute\n"),
        ("traversal", digest + "  source:../escape\n"),
    )
    cases = []
    for case_id, text in samples:
        try:
            parse_pin_lines(text)
            accepted = True
            observed = "ACCEPTED"
        except ValueError:
            accepted = False
            observed = "INVALID_PIN"
        cases.append({"accepted": accepted, "id": case_id, "observed": observed})
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
    }


def adverse_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []

    def probe(case_id: str, mutate: Any, candidate: Any = None) -> None:
        manifest = valid_manifest() if candidate is None else candidate
        mutate(manifest)
        try:
            validate_caller_manifest(manifest)
            observed = "ACCEPTED"
        except ReferenceRejection as error:
            observed = error.code
        cases.append({"accepted": observed == "ACCEPTED", "id": case_id,
                      "observed": observed})

    probe("missing_field", lambda m: m.pop("source_revision"))
    probe("unknown_field", lambda m: m.update({"unexpected": 1}))
    probe("wrong_adapter", lambda m: m.update({"adapter": "other"}))
    probe("wrong_configuration", lambda m: m.update({"configuration_id": "other"}))
    probe("wrong_source_checkout", lambda m: m.update({"source_checkout": "other"}))
    probe("wrong_source_revision", lambda m: m.update({"source_revision": "0" * 40}))
    probe("wrong_source_digest", lambda m: m.update({"source_sha256": "f" * 64}))
    probe("wrong_license", lambda m: m.update({"license_id": "MIT"}))
    probe("wrong_rate", lambda m: m.update({"sample_rate_hz": 48000}))
    probe("wrong_channels", lambda m: m.update({"channels": 2}))
    probe("wrong_frame_samples", lambda m: m.update({"frame_samples": 320}))
    probe("wrong_target_srate", lambda m: m.update({"target_srate_hz": 500}))
    probe("wrong_window_rule", lambda m: m.update({"min_bpm": 60}))
    probe("relative_runtime_path",
          lambda m: m.update({"runtime_path": "relative/runtime.a"}))
    probe("absent_runtime", lambda m: None)
    probe("bad_runtime_digest",
          lambda m: m.update({"runtime_sha256": "f" * 64}))
    probe("bad_runtime_byte_count",
          lambda m: m.update({"runtime_byte_count": 0}))
    probe("relative_label_path",
          lambda m: m.update({"label_set_path": "relative/labels.json"}))
    probe("unreviewed_rights", lambda m: m.update({"rights_review_id": "unreviewed"}))
    probe("hash_matched_but_unpinned",
          lambda m: None, candidate=hash_matched_manifest())
    probe("manifest_not_object", lambda m: None, candidate=["not", "an", "object"])
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "note": "All caller manifests fail closed before any asset load or execution.",
    }


def asset_pins_absent() -> bool:
    """The built runtime and BPM label set must have no pinned identity."""

    for asset in ASSET_LEDGER["required_assets"]:
        if asset["id"] == "bpmdetect_source":
            continue
        if any(asset[key] is not None
               for key in ("revision", "byte_count", "sha256")):
            return False
    return not any(ASSET_LEDGER[key] for key in
                   ("downloaded", "vendored", "loaded", "executed"))


def absent_artifact_probe() -> Dict[str, Any]:
    workspace_found = [path for path in ABSENT_CANDIDATES
                       if (SOURCE_ROOT / path).exists()]
    return {
        "note": "Bounded read-only path probes; no download, build, import or load attempted.",
        "present": False,
        "workspace_candidates": list(ABSENT_CANDIDATES),
        "workspace_found": workspace_found,
        "method": "explicit candidate paths only; no recursive filesystem walk",
    }


def rate_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "source_output_mapping": {
                "status": "synthetic_only",
                "evidence": "Integer onset positions at 0.8x/1x/1.25x; no audio output.",
            },
            "duration": {
                "status": "synthetic_only",
                "evidence": "Exact integer frame and final-partial arithmetic.",
            },
            "pitch": {
                "status": "blocked",
                "evidence": "No pitch measurement or listening; not a transformation path.",
            },
            "transient_audibility": {
                "status": "synthetic_only",
                "evidence": "Frame-quantization proxy only; no transient audibility result.",
            },
            "unfamiliar_speech_music_silence": {
                "status": "synthetic_only",
                "evidence": "Integer interval controls only; no held-out corpus.",
            },
            "rebuffer_drift_final_partial": {
                "status": "synthetic_only",
                "evidence": "One synthetic final-partial probe; no paced workload.",
            },
            "playback_buffering": {
                "status": "synthetic_only",
                "evidence": "160-frame aggregation arithmetic; no device buffer.",
            },
            "speech_preservation_and_pause_decisions": {
                "status": "blocked",
                "evidence": "No speech preservation score or source-tied decision.",
            },
            "rate_changes": {
                "status": "synthetic_only",
                "evidence": "Exact integer rate mapping; no installed runtime.",
            },
            "task_matched_heldout_qualification": {
                "status": "blocked",
                "evidence": "No rights-cleared BPM-labeled cohort, scorer or baseline.",
            },
        },
        "satisfied": False,
    }


def source_reported() -> Dict[str, Any]:
    lines = source_lines()
    return {
        "entries": lines["entries"],
        "line_count": lines["line_count"],
        "source_reported_tsm": {
            "version_label": "SoundTouch 2.4.1",
            "checked_out_configure_version": "2.4.0",
            "duration_error_samples": 2,
            "endpoint_median_rtf": 0.0022,
            "paired_whisper_wer_delta_pp": [14.0, 0.0, 7.4, 54.4],
            "first_output_ms": 200,
            "path": "WSOLA-style time-stretch, not BPMDetect",
            "qualifies": False,
        },
        "bpmdetect_result": {
            "status": "absent",
            "bpm_estimate": None,
            "beat_positions": None,
            "runtime": None,
        },
        "excluded_from_bpmdetect_evidence": [
            "SDK-SOUNDTOUCH WSOLA time-stretch package and its paired Whisper screen",
            "Source-reported TSM RTF/F0/first-output figures",
            "librosa, madmom, BeatNet and Beat This rows in the candidate survey",
        ],
        "listening_performed_here": False,
        "qualifies": False,
        "separation": (
            "All quoted values are source-reported time-stretch results or "
            "survey rows. None is a local BPMDetect measurement; none qualifies "
            "this task."
        ),
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    geometry = bpm_geometry()
    probe = absent_artifact_probe()
    manifest_adverse = adverse_cases()
    json_adverse = invalid_json_cases()
    pin_adverse = invalid_pin_cases()
    report: Dict[str, Any] = {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "no_missing_result_qualifies_candidate": True,
        "scope": dict(SCOPE),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "boundary": dict(BOUNDARY),
        "format": dict(BOUNDARY["format"]),
        "caller_supplied_asset_contract": {
            "schema_id": SCHEMA_MANIFEST,
            "required_fields": list(CALLER_MANIFEST_FIELDS),
            "configuration_id": CONFIGURATION_ID,
            "source_checkout": dict(SOURCE_CHECKOUT),
            "required_assets": [dict(item) for item in REQUIRED_ASSETS],
            "loaded": False,
            "executed": False,
            "terminal_rejection": "BPMDETECT_RUNTIME_IDENTITY_UNPINNED",
            "note": (
                "Metadata-only reference. A hash-matched caller asset set still "
                "fails because no licensed built runtime and BPM label identity "
                "are pinned."
            ),
        },
        "bpm_geometry": geometry,
        "geometry_probe": geometry_probe(),
        "rate_profile": rate_profile(),
        "available_evidence": {
            "status": "source_reported_tsm_only",
            "clock": "no runtime clock",
            "device_timing": False,
            "streaming_result": False,
            "content_delay_claim": False,
            "first_output_or_tail": "blocked_not_measured",
        },
        "asset_resolution": probe,
        "adverse": {
            "caller_manifest": manifest_adverse,
            "invalid_json": json_adverse,
            "invalid_pins": pin_adverse,
            "all_rejected": (manifest_adverse["all_rejected"]
                             and json_adverse["all_rejected"]
                             and pin_adverse["all_rejected"]),
            "metrics": None,
        },
        "comparison": {
            "status": "blocked_no_matched_bpm_labels_or_runtime",
            "identity_control": "integer interval identity only; not BPMDetect output",
            "task_matched_baseline": "blocked",
            "qualifies_candidate": False,
        },
        "source_reported": source_reported(),
        "source_provenance": {
            "source_checkout": dict(SOURCE_CHECKOUT),
            "required_assets": [dict(item) for item in ASSET_LEDGER["required_assets"]],
            "rights": dict(ASSET_LEDGER["rights"]),
        },
        "licensing_analysis": {
            "source_license": "LGPL-2.1-or-later (pinned COPYING.TXT and source headers)",
            "commercial_license_decision": "unreviewed",
            "built_runtime_distribution": "unreviewed",
            "label_set_and_product_use": "unreviewed",
            "qualifies": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "licensed built SoundTouch runtime identity with immutable digest",
            "rights-cleared held-out BPM-labeled cohort and matched scorer",
            "executed 16 kHz mono float32 160-frame runtime geometry",
            "rate mapping, final-partial and playback timing telemetry",
            "opt-in intake with independent review and default OFF",
        ],
        "reopening_conditions": [item["reopen"] for item in EXACT_BLOCKERS],
        "evidence_classes": {
            "source_reported": True,
            "synthetic": True,
            "model_free_geometry": True,
            "real_local_model_output": False,
            "real_audio": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
        },
        "board_link": board_link(),
        "repeatability": {
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "fresh_builds": 3,
            "comparison": "exact SHA-256 over bytes; no tolerance",
        },
    }
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report())


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    lines = [
        "# SHA-256 pins for SDK-SOUNDTOUCH-BPMDETECT.",
        "# source: paths are workspace-relative; other external paths are SDK-worktree-relative.",
        "# Local paths are SDK-worktree-relative. Missing assets are ledger entries, not file pins.",
        "# The mutable full plan/swarm/TASKS.json is never pinned; only stable row identity is gated.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(SOURCE_PINS[path] + "  source:" + path)
    for path in sorted(BOUNDARY_PINS):
        lines.append(BOUNDARY_PINS[path] + "  " + path)
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (TASK_DIR / name).read_bytes()
        lines.append(sha256_bytes(payload) + "  " + TASK_PREFIX + name)
    return ("\n".join(lines) + "\n").encode("utf-8")


def contract_bytes(report_payload: bytes, sidecar_payload: bytes,
                   sources_payload: bytes, report: Dict[str, Any]) -> bytes:
    artifact_pins: Dict[str, str] = {}
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (TASK_DIR / name).read_bytes()
        artifact_pins[TASK_PREFIX + name] = sha256_bytes(payload)
    contract: Dict[str, Any] = {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "contract_version": "0.1",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "status": STATUS,
        "task_prefix": TASK_PREFIX,
        "format": dict(BOUNDARY["format"]),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "artifact_pins": artifact_pins,
        "report_sha256": sha256_bytes(report_payload),
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "sources_sha256": sha256_bytes(sources_payload),
        "board_link": board_link(),
        "caller_supplied_asset_contract": report["caller_supplied_asset_contract"],
        "source_reported": report["source_reported"],
        "rate_profile": report["rate_profile"],
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "invariants": [
            "Installed v0 remains 16 kHz mono float32 with 160-sample frames.",
            "BPMDetect geometry is analysis-only reference material and not installable in v0.",
            "Only the task-local evidence directory is written.",
            "No source, runtime, audio or label-set artifact is bundled.",
            "Caller manifests are validated as metadata and never loaded or executed.",
            "Source-reported time-stretch evidence is excluded from BPMDetect qualification.",
            "Model-free integer controls cannot qualify the candidate.",
            "Only stable board-row identity enters canonical bytes or gates.",
        ],
    }
    return canonical_bytes(contract)


def _git(worktree: Path, *arguments: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else None


def scope_base(worktree: Path,
                refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base of HEAD with an available PR base ref."""

    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        if _git(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> List[str]:
    return [path for path in paths if path and not path.startswith(prefix)]
