# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE.

This module is stdlib-only and deterministic. It does **not** contain, import,
build, link, load, execute, download or wrap libopus, the Opus reference
implementation, any codec, any packet capture or any audio asset. It records the
exact external blocker for codec/packetization, FEC, DTX and comfort-noise
evidence, probes a fixed list of task-local paths for the absent permitted
artifacts, validates caller-supplied manifest and packet-trace documents with a
fail-closed admission boundary, and builds the canonical report.

It also runs a deliberately small, synthetic, integer-only **packet-container
model** so that the receive/transmit packet contract can be exercised as a
contract and rejected when malformed. That model is a first-order delta +
zigzag-varint container with a synthetic tag byte. It is **not** Opus, not
RFC 6716, not CELP, not SILK, and not a codec result. No model output is
promoted to a codec, quality, timing or release claim.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

TASK = "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE"
COMPONENT_ID = "opus-packetization-fec-dtx-and-comfort-noise"
TASK_TITLE = "Opus packetization, FEC, DTX and comfort noise"
CONTRACT_ID = ("audio-sdk/opus-packetization-fec-dtx-and-comfort-noise-"
               "readiness/0.1")
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
CONTRACT_MODEL_ID = "audio-sdk/synthetic-packet-container/0.1"
PROFILE = "tool"
MODE = "feasibility"
BASE_COMMIT = "c7b157247be6e4ceea0ab5b04ff4463de1566146"
BRANCH = "swarm/SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
DEFAULT_AUDIO_ROOT = HERE.parents[5]
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT",
                                 str(DEFAULT_AUDIO_ROOT))).resolve()
TASK_PREFIX = "docs/task-evidence/opus-packetization-fec-dtx-and-comfort-noise/"
WRITE_SCOPE = TASK_PREFIX + " only"

# Installed v0 geometry (unchanged, never invoked).
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
FRAME_MS = 10
PACKET_FRAME_COUNTS = (1, 2, 3)
DTX_MODES = ("off", "omit", "cn")
PACKET_KINDS = ("audio", "comfort_noise")
MAX_PACKETS = 4096
MAX_FRAMES = 4096
SILENCE_MEAN_ABS = 140
COMFORT_NOISE_LEVEL = 64

# Immutable inputs. `source:` rows are workspace-relative; the rest are
# SDK-worktree-relative. The mutable shared board is deliberately excluded from
# the pin set; only its stable row projection may gate anything.
SOURCE_PINS = {
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/elastic-pcm-packets/README.md":
        "15ebaa6b2b7768faa5c1bd2fc45b900db7f71d49b7ad1292685263555953e742",
    "docs/task-evidence/elastic-pcm-packets/contract.json":
        "2ce960fb63a3ee2e1a888f33a990ce15da1804b0550aa3ad637c941222955e85",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md":
        "ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df",
    "docs/task-evidence/survey-eng-04/README.md":
        "c3c2f353f7fd647f2a1a0ea59736acfb49c1913915e1d5053d7172b0d4c82666",
    "docs/task-evidence/survey-eng-04/contract.json":
        "d13c92601c151d04bf026c4ab166d42f85836351b0c7123e75b8d880d2476ea0",
    "docs/task-evidence/survey-eng-04/report.json":
        "c11355762f528e51c8ea92782d921414b8221b0eb0b3ecee74227ac735e97583",
    "docs/task-evidence/webrtc-neteq/README.md":
        "315f5ba9835f1c09df0981740c9dbaf3da6f0224001c012b0e138cc90cb01857",
    "docs/task-evidence/webrtc-neteq/contract.json":
        "4a6c8e05189db69ea537b3a7715ac076ca2a8bf779c139589dde5088fc75666f",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
}

# Fixed, bounded absence probes for *admitted* artifacts. No recursive walk.
# Unqualified binaries outside this admitted boundary are recorded separately.
ABSENCE_PROBES = (
    "data/checkouts/opus",
    "data/checkouts/libopus",
    "data/checkouts/opus-1.4",
    "data/checkouts/opus-1.5",
    "data/checkouts/opus-1.6",
    "data/checkouts/opus-src",
    "adapters/opus-packetization",
    "adapters/opus-fec-dtx",
    "third_party/opus",
    "third_party/libopus",
    "deps/opus",
    "assets/opus",
    "data/traces/opus",
    "data/assets/opus-packet-traces",
    "audio-benchmark-platform/audio-sdk/third_party/opus",
    "audio-benchmark-platform/audio-sdk/third_party/libopus",
    "audio-benchmark-platform/audio-sdk/deps/opus",
    "audio-benchmark-platform/audio-sdk/core/opus",
    "LICENSES/Opus-BSD-3-Clause.txt",
    "third_party/opus/COPYING",
)

# Observed but never admitted, loaded, linked or used as evidence. The path is
# inside a gitignored, mutable virtualenv belonging to an unrelated pipeline.
OBSERVED_UNQUALIFIED_BINARIES = (
    {
        "path": ("cpp-library/pipeline-validation/playback-speed/.venv/lib/"
                 "python3.11/site-packages/av/.dylibs/libopus.0.dylib"),
        "kind": "dynamic_library",
        "sha256": ("dca12b81b778f51dc5cecbc789fffaac472de09b102a164d5348b360"
                   "b238a202"),
        "byte_count": 636800,
        "version_string": "libopus 1.6.1",
        "authoring_probe": (
            "read-only version-string provenance probe during authoring; no "
            "encode, decode, packetization, DTX, FEC or comfort-noise "
            "operation was executed and no payload was produced"),
        "git_tracked": False,
        "git_ignored": True,
        "opus_license_text_present": False,
        "source_revision": None,
        "admitted": False,
        "used_for_evidence": False,
        "linked": False,
        "executed_by_package": False,
        "reason": (
            "Unqualified transitive PyAV-wheel binary in a gitignored, mutable "
            "virtualenv. It ships no Opus COPYING/LICENSE_PLEASE_READ.txt, no "
            "source revision and no rights review, and it is not the exact "
            "licensed pinned artifact. It is recorded as provenance only and is "
            "never used for any result."),
    },
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "permitted_source",
        "requirement": (
            "The Xiph.Org Opus reference-implementation source tree at an exact "
            "immutable revision with an archive SHA-256, staged in the admitted "
            "workspace."),
    },
    {
        "id": "ART-02",
        "kind": "license_and_notices",
        "requirement": (
            "The upstream Opus BSD-3-Clause COPYING, LICENSE_PLEASE_READ.txt, "
            "copyright notices and any third-party notice bundle for that "
            "revision, with an explicit rights review."),
    },
    {
        "id": "ART-03",
        "kind": "built_runtime",
        "requirement": (
            "A reproducible, pinned Opus build with toolchain, configuration, "
            "install location, exported ABI and artifact SHA-256."),
    },
    {
        "id": "ART-04",
        "kind": "packet_and_erasure_trace",
        "requirement": (
            "A rights-cleared, immutable packet trace with frame duration, "
            "packetization mode, DTX state, in-band FEC/LBRR presence, payload "
            "bytes, payload digests and an exact erasure mask."),
    },
    {
        "id": "ART-05",
        "kind": "media_and_listening",
        "requirement": (
            "A rights-cleared speech/noise cohort plus an approved listening or "
            "independent quality protocol for DTX, comfort-noise and FEC "
            "conditions."),
    },
    {
        "id": "ART-06",
        "kind": "runtime_harness",
        "requirement": (
            "A target-runtime/device harness with agreed pacing, deadline, CPU, "
            "memory and workload budgets for the intended execution profile."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-01",
        "statement": (
            "No permitted Opus source snapshot exists at any fixed absence "
            "probe. No revision or source digest can be pinned from a local "
            "admitted artifact."),
        "required_action": (
            "Stage the exact Opus source revision and immutable archive with a "
            "matching SHA-256 from a source root that permits review."),
        "linked_gates": ["G2", "G7"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-02",
        "statement": (
            "No Opus BSD-3-Clause COPYING, LICENSE_PLEASE_READ.txt, copyright "
            "notice bundle or rights decision exists in the admitted "
            "workspace."),
        "required_action": (
            "Supply the license/notices bundle for the pinned revision and "
            "record an explicit rights and redistribution decision."),
        "linked_gates": ["G1", "G2"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-03",
        "statement": (
            "No reproducible Opus build, install location, exported ABI or "
            "artifact digest exists. The Tool profile cannot record a version, "
            "install location or provenance. An unqualified PyAV-bundled "
            "libopus 1.6.1 dylib is present outside the admitted boundary and "
            "is explicitly not used."),
        "required_action": (
            "Supply a reproducible pinned build and artifact digest, or record "
            "an explicit build-and-measure plan on an approved host."),
        "linked_gates": ["G2", "G7"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-04",
        "statement": (
            "No rights-cleared codec packet trace or erasure corpus exists. "
            "Every packet trace in this package is generated by the synthetic "
            "container model and is not Opus evidence."),
        "required_action": (
            "Supply rights-cleared traces with provenance, immutable digest, "
            "packetization mode, DTX/FEC state and the exact erasure mask."),
        "linked_gates": ["G1", "G7"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "statement": (
            "No permitted speech/noise cohort and no listening or independent "
            "quality protocol exist, so DTX, comfort-noise and FEC quality "
            "cannot be judged."),
        "required_action": (
            "Supply a rights-cleared cohort and an approved listening or "
            "independent quality protocol for the exact conditions."),
        "linked_gates": ["G1", "G3"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "statement": (
            "No target-runtime or device harness, pacing budget, deadline or "
            "resource limit exists, so availability and timing cannot be "
            "claimed."),
        "required_action": (
            "Supply the target harness and agree coverage, margins, deadlines "
            "and resource limits before collecting results."),
        "linked_gates": ["G4", "G8"],
    },
)

RELEASE_GATES = (
    {
        "id": "G1",
        "title": "rights_cleared_packet_trace_and_media",
        "statement": (
            "Rights-cleared frozen packet/FEC/DTX traces and a media cohort "
            "before any codec or quality result."),
        "reopen_condition": (
            "A rights-cleared immutable trace cohort with declared provenance, "
            "timestamp domain and erasure mask is supplied and reviewed."),
    },
    {
        "id": "G2",
        "title": "permitted_source_runtime_and_assets",
        "statement": (
            "Pinned permitted Opus source, built runtime and license notices "
            "before any implementation or parity claim."),
        "reopen_condition": (
            "Exact source revision, built runtime and license/notices bundle "
            "are pinned by digest and their use is permitted."),
    },
    {
        "id": "G3",
        "title": "independent_listening_and_dtx_cn_quality",
        "statement": (
            "Independent listening or an approved predictive protocol before "
            "any DTX, comfort-noise or FEC quality claim."),
        "reopen_condition": (
            "An approved protocol and panel or agreed predictive scorer exist "
            "for the exact conditions and rights scope."),
    },
    {
        "id": "G4",
        "title": "target_runtime_timing_and_resources",
        "statement": (
            "Paced target-runtime timing, deadline, CPU and memory evidence "
            "before any availability claim."),
        "reopen_condition": (
            "Paced runs on the target with instrumented clocks, deadlines and "
            "resource limits are recorded and reviewed."),
    },
    {
        "id": "G5",
        "title": "opt_in_provider_intake",
        "statement": (
            "Opt-in provider intake and licensing clearance before any "
            "registration."),
        "reopen_condition": (
            "A separate versioned intake task accepts the adapter with an OFF "
            "default and independent review."),
    },
    {
        "id": "G6",
        "title": "public_default_selection",
        "statement": (
            "An explicit public default decision before any enabled-by-default "
            "claim."),
        "reopen_condition": (
            "The owner records an explicit default decision after intake, "
            "separately from this feasibility task."),
    },
    {
        "id": "G7",
        "title": "exact_external_reference_parity",
        "statement": (
            "Exact parity with the approved pinned Opus runtime before any "
            "codec-native packetization, FEC, DTX or comfort-noise claim."),
        "reopen_condition": (
            "The same packetization inputs and erasure masks are replayed "
            "through the approved runtime and this boundary with exact "
            "accounting."),
    },
    {
        "id": "G8",
        "title": "independent_review_and_board_transition",
        "statement": (
            "Independent review and a board transition before any component "
            "acceptance claim."),
        "reopen_condition": (
            "The named reviewer verifies this package from its pinned revision "
            "and the coordinator records the board transition."),
    },
)

PROHIBITED_CLAIMS = (
    "No Opus, libopus, CELP, SILK, DRED, LACE or other codec source, binary, "
    "header, model or runtime is present, built, linked, loaded, executed or "
    "wrapped.",
    "No real packet trace, RTP capture, codec packetization, in-band FEC/LBRR, "
    "DTX or comfort-noise codec operation is replayed or produced.",
    "No real speech, noise, corpus, listening, intelligibility, naturalness or "
    "quality result is produced.",
    "No jitter, pacing, deadline, latency, device timing, CPU, memory or "
    "workload measurement is made.",
    "No provider is registered, exposed, enabled by default or selected as a "
    "descriptor default, and no public API, ABI, CMake or CI change is made.",
    "No benchmark, install, CTest, upstream-parity or release qualification "
    "result is claimed.",
)

TOOL_PROFILE_ROWS = (
    {
        "id": "TOOL-01",
        "requirement": "Record version, install location and provenance.",
        "status": "blocked",
        "evidence": (
            "No admitted Opus source, runtime or install location exists. The "
            "observed PyAV dylib is unqualified and not admitted."),
    },
    {
        "id": "TOOL-02",
        "requirement": "Verify a clean checkout or extracted package.",
        "status": "blocked",
        "evidence": "No checkout or package archive is present.",
    },
    {
        "id": "TOOL-03",
        "requirement": "One typical CLI/API use.",
        "status": "blocked",
        "evidence": "No admitted CLI or API exists to invoke.",
    },
    {
        "id": "TOOL-04",
        "requirement": "Caller-owned inputs.",
        "status": "blocked",
        "evidence": (
            "The caller-asset manifest and packet trace are declared and "
            "admission-checked only; no real input is supplied."),
    },
    {
        "id": "TOOL-05",
        "requirement": "Malformed inputs.",
        "status": "verified_task_local_only",
        "evidence": (
            "The task-local manifest, packet, trace and strict-JSON validators "
            "reject every malformed, missing, invalid and nonfinite control "
            "before any state change; this is not runtime error behavior."),
    },
    {
        "id": "TOOL-06",
        "requirement": "Missing optional selections.",
        "status": "blocked",
        "evidence": (
            "No optional codec or runtime selection can be exercised without "
            "an admitted runtime."),
    },
    {
        "id": "TOOL-07",
        "requirement": (
            "Separate compile/build evidence, synthetic runtime evidence and "
            "measured workload support."),
        "status": "blocked",
        "evidence": (
            "Compile/build evidence is absent, codec synthetic-runtime evidence "
            "is absent, and no workload support exists. The task-local "
            "container model is not codec runtime evidence."),
    },
)

# --------------------------------------------------------------------------
# Synthetic packet-container contract (task-local; not Opus, not RFC 6716)
# --------------------------------------------------------------------------
PACKET_CONTRACT = {
    "id": CONTRACT_MODEL_ID,
    "purpose": (
        "Exercise a receive/transmit packet contract that is distinct from PCM "
        "so packetization, redundancy, DTX and comfort-noise accounting can be "
        "validated fail-closed without a codec runtime."),
    "not_opus": True,
    "rfc6716_toc_used": False,
    "codec_operation": False,
    "distinct_from_pcm": True,
    "pcm_frame": {
        "fields": ["sample_index", "label", "samples[160]"],
        "sample_type": "signed integer proxy (not float32 delivery)",
        "samples_per_frame": FRAME_SAMPLES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
    },
    "transmit_packet": {
        "fields": [
            "seq", "timestamp", "duration_samples", "frame_count", "kind",
            "fec_copy_of", "payload_bytes", "payload_sha256", "payload_hex",
        ],
        "seq": "non-negative integer, contiguous from zero within a trace",
        "timestamp": "source frame index * 160",
        "duration_samples": "frame_count * 160",
        "frame_count": "1..3",
        "kind": "audio|comfort_noise",
        "fec_copy_of": "previous seq or null",
    },
    "receive_packet": {
        "fields": [
            "seq", "timestamp", "duration_samples", "frame_count", "arrival",
            "status", "recovery", "payload_sha256",
        ],
        "status": "received|lost",
        "recovery": "none|fec|plc|comfort_noise|missing",
    },
    "tag_layout": {
        "bits_0_1": "frame_count_minus_one",
        "bit_2": "fec_copy_present",
        "bits_3_4": "kind (0 audio, 1 comfort_noise)",
        "bits_5_7": "reserved, must be zero",
    },
    "frame_encoding": (
        "first-order sample delta, zigzag signed mapping, 7-bit little-endian "
        "varint; each frame length-prefixed with two big-endian bytes"),
    "fec_model": (
        "synthetic previous-frame copy embedded in the next contiguous audio "
        "packet; one packet deep; not Opus LBRR"),
    "dtx_model": (
        "deterministic mean-absolute-energy gate; omit drops silent source "
        "frames, cn emits one bounded comfort-noise packet per silent run"),
    "limitations": (
        "Synthetic structural model only. Payload sizes, recovery depth and "
        "comfort-noise levels do not describe Opus, RFC 6716, SILK, CELT, "
        "Opus 1.4/1.5/1.6 or any vendor implementation."),
}

MANIFEST_FIELDS = (
    "source_path",
    "source_revision",
    "source_sha256",
    "license_path",
    "license_sha256",
    "runtime_path",
    "runtime_sha256",
    "trace_path",
    "trace_sha256",
    "codec_id",
    "packet_duration_ms",
    "dtx_enabled",
    "fec_enabled",
    "comfort_noise_enabled",
    "sdk_sample_rate_hz",
    "sdk_channels",
    "sdk_frame_samples",
)
MANIFEST_PATH_FIELDS = ("source_path", "license_path", "runtime_path",
                        "trace_path")
MANIFEST_DIGEST_FIELDS = ("source_sha256", "license_sha256", "runtime_sha256",
                          "trace_sha256")
ALLOWED_PACKET_MS = (10, 20, 40, 60)

PACKET_FIELDS = ("seq", "timestamp", "duration_samples", "frame_count", "kind",
                 "fec_copy_of", "payload_bytes", "payload_sha256",
                 "payload_hex")
TRACE_FIELDS = ("trace_id", "packet_frames", "dtx", "fec", "packets")
TRACE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
CODEC_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,31}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX_EVEN = re.compile(r"^(?:[0-9a-f]{2})+$")

# --------------------------------------------------------------------------
# Static report sections
# --------------------------------------------------------------------------
DISPOSITION = {
    "status": "incomplete",
    "decision": "DEFER",
    "qualification_status": "not_qualified",
    "promotion": "defer",
    "production_exposure": "DEFER",
    "proposal_only": True,
    "incomplete": True,
    "not_qualified": True,
    "expose_as_processor": False,
    "registered": False,
    "enabled_by_default": False,
    "missing_result_qualifies": False,
}

BOUNDARY = {
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
    "board_or_handoff_changed": False,
    "processor_exposure": False,
    "task_local_only": True,
    "files_outside_task_directory_written": False,
}

PUBLIC_V0_GEOMETRY = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
    "preserved": True,
    "sdk_callback_invoked": False,
}

SCOPE = {
    "source_present": False,
    "runtime_present": False,
    "runtime_executed": False,
    "codec_runtime_linked": False,
    "codec_runtime_executed": False,
    "real_packet_trace": False,
    "real_audio": False,
    "network_capture": False,
    "dtx_fec_cn_codec_operation": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "release_claim": False,
    "network_used": False,
    "download_attempted": False,
    "authoring_provenance_probe_only": True,
    "task_local_contract_model_executed": True,
}

EXACT_SCOPE = {
    "task_local_evidence_only": True,
    "single_component": COMPONENT_ID,
    "provider_work": False,
    "runtime_work": False,
    "release_work": False,
    "write_scope": WRITE_SCOPE,
}

QUALIFICATION = {
    "status": "not_qualified",
    "readiness": "incomplete",
    "decision": "DEFER",
    "processor_exposure": "DEFER",
    "proposal_only": True,
    "all_release_gates_blocked": True,
    "all_required_results_present": True,
    "real_codec_source_present": False,
    "real_codec_runtime_present": False,
    "codec_runtime_executed": False,
    "real_packet_trace_present": False,
    "real_audio_present": False,
    "upstream_parity": False,
    "candidate_qualified": False,
    "missing_result_promoted": False,
    "not_qualified": True,
}

UPSTREAM_BLOCKER = {
    "status": "blocked_upstream_absent",
    "artifact": (
        "Xiph.Org Opus reference-implementation source tree at an exact pinned "
        "revision"),
    "expected_license": (
        "BSD-3-Clause (Opus), including upstream COPYING, "
        "LICENSE_PLEASE_READ.txt and copyright notices"),
    "required_files": [
        "include/opus.h",
        "src/opus_encoder.c",
        "src/opus_decoder.c",
        "src/repacketizer.c",
        "src/opus_private.h",
        "configure.ac or CMakeLists.txt",
        "COPYING",
        "LICENSE_PLEASE_READ.txt",
    ],
    "pinned_revision": None,
    "source_digest": None,
    "workspace_search": [
        "the SDK worktree third_party/ contains only speexdsp",
        "deps/lock.json pins only SpeexDSP 1.2.1; no Opus entry",
        ("no include/opus.h, src/opus_encoder.c, repacketizer.c or Opus source "
         "archive exists at any fixed admitted probe"),
        ("no task-local Opus packet, FEC, DTX or comfort-noise trace, corpus or "
         "license text is staged"),
        "no CMake, dependency lock, registry or descriptor reference to Opus",
        ("an unqualified PyAV-bundled libopus 1.6.1 dylib exists in a "
         "gitignored .venv outside the admitted boundary and was not used"),
    ],
    "rights_requirement": (
        "The upstream BSD-3-Clause COPYING, LICENSE_PLEASE_READ.txt, copyright "
        "notices, an exact source revision/digest and a rights review are "
        "required before any wrapper, build, trace or comparison can be "
        "claimed."),
    "observed_unqualified_runtime": (
        "dca12b81b778f51dc5cecbc789fffaac472de09b102a164d5348b360b238a202 "
        "libopus.0.dylib (version string libopus 1.6.1) in a gitignored PyAV "
        ".venv; unqualified, unlicensed for this use and never admitted"),
    "not_attempted": [
        "no network download",
        "no fabricated or reconstructed upstream source",
        ("no unqualified bundled dylib substitution for the absent licensed "
         "source or runtime"),
    ],
    "no_upstream_parity_claim": True,
    "reopen": (
        "Stage the exact Opus revision with its BSD-3-Clause license and "
        "notices, record the digest, complete a rights review, build it "
        "reproducibly, then repeat this packet/FEC/DTX/comfort-noise profile "
        "against the real runtime for an exact comparison."),
}

REGENERATION = {
    "runs": 3,
    "byte_identical": True,
    "cold_start_processes": True,
    "canonical_json": True,
    "sorted_keys": True,
    "compact_separators": True,
    "trailing_newline": True,
}

REPRODUCTION = {
    "tests": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
    "contract": "PYTHONDONTWRITEBYTECODE=1 python3 run.py contract",
    "report": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
    "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
    "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
}


class ContractError(ValueError):
    """Deterministic task-local contract failure."""


# --------------------------------------------------------------------------
# Strict JSON and digests
# --------------------------------------------------------------------------
def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def loads_strict(text: str) -> dict:
    """Parse a strict JSON object; reject duplicate keys, NaN and Infinity."""
    if text.startswith("\ufeff"):
        raise ValueError("json_byte_order_mark")
    parsed = json.loads(text, object_pairs_hook=_unique_object,
                        parse_constant=_reject_constant)
    if not isinstance(parsed, dict):
        raise ValueError("json_root_not_object")
    return parsed


def read_strict_json(path: Path) -> dict:
    return loads_strict(Path(path).read_text(encoding="utf-8"))


def canonical_text(document: object) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def canonical_bytes(document: object) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: object) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# Pins, board identity and absence probes
# --------------------------------------------------------------------------
def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for relative in sorted(pins):
        path = Path(root) / relative
        if not path.is_file():
            raise ValueError("pin_target_missing:" + relative)
        actual = sha256_file(path)
        if actual != pins[relative]:
            raise ValueError("pin_digest_mismatch:" + relative)
        rows[relative] = {"sha256": pins[relative], "actual": actual,
                          "verified": True}
    return rows


def board_row_projection(path: Path) -> dict:
    board = read_strict_json(path)
    rows = [row for row in board.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise ValueError("board_row_not_unique:" + TASK)
    row = rows[0]
    return {field: row.get(field) for field in BOARD_ROW_FIELDS}


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def absence_probes(audio_root: Path,
                   probes: tuple[str, ...] = ABSENCE_PROBES,
                   worktree: Path | None = None) -> list[dict]:
    """Return the fixed probe inventory. Any present path must block shipping."""
    sdk_root = WORKTREE if worktree is None else worktree
    rows: list[dict] = []
    for relative in probes:
        workspace_path = Path(audio_root) / relative
        sdk_candidate = sdk_root / relative
        if workspace_path.exists() or sdk_candidate.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_workspace": True,
                     "searched_sdk_worktree": True, "present": False})
    return rows


def absence_summary(rows: list[dict]) -> dict:
    return {
        "probe_count": len(rows),
        "present_count": sum(1 for row in rows if row["present"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "source_or_runtime_imported": False,
        "all_probes_absent": all(not row["present"] for row in rows),
    }


# --------------------------------------------------------------------------
# Deterministic synthetic signal and container model
# --------------------------------------------------------------------------
_MASK64 = (1 << 64) - 1
TRANSIENT_FRAMES = frozenset((20, 60, 92))
_LABEL_PAUSE = "pause"
_LABEL_VOICED = "voiced"


def lcg(seed: int):
    state = (seed * 6364136223846793005 + 1442695040888963407) & _MASK64

    def generator() -> int:
        nonlocal state
        state = (state * 6364136223846793005 + 1442695040888963407) & _MASK64
        return state >> 33

    return generator


def frame_labels(count: int) -> list[str]:
    labels: list[str] = []
    for index in range(count):
        position = index % 100
        if 35 <= position < 45 or 75 <= position < 85:
            labels.append(_LABEL_PAUSE)
        else:
            labels.append(_LABEL_VOICED)
    return labels


def _triangle(phase: int, period: int) -> int:
    half = period // 2 or 1
    other = period - half or 1
    if phase < half:
        return -1000 + (2000 * phase) // half
    return 1000 - (2000 * (phase - half)) // other


def synthetic_frame(label: str, frame_index: int, seed: int = 7000) -> tuple:
    noise = lcg(seed + frame_index * 7919)
    if label == _LABEL_PAUSE:
        amplitude = 40 + (frame_index % 7) * 8
        span = 2 * amplitude + 1
        return tuple((noise() % span) - amplitude for _ in range(FRAME_SAMPLES))
    period = 64 + (frame_index % 5) * 4
    base = 2200 + (frame_index % 11) * 90
    if frame_index in TRANSIENT_FRAMES:
        base += 9000
    output = []
    for position in range(FRAME_SAMPLES):
        wave = _triangle(position % period, period)
        dither = (noise() % 401) - 200
        output.append((base * wave) // 1000 + dither)
    return tuple(output)


def synthetic_frames(count: int, seed: int = 7000) -> tuple:
    labels = frame_labels(count)
    return tuple(synthetic_frame(label, index, seed)
                 for index, label in enumerate(labels))


def frame_mean_abs(frame: tuple) -> int:
    return sum(abs(sample) for sample in frame) // len(frame)


def frame_is_silent(frame: tuple) -> bool:
    return frame_mean_abs(frame) <= SILENCE_MEAN_ABS


def comfort_noise_seed(frame_index: int) -> int:
    return 0x5EED + frame_index * 7919


def comfort_noise_frame(frame_index: int,
                        level: int = COMFORT_NOISE_LEVEL) -> tuple:
    if level < 0 or level > 512:
        raise ContractError("comfort_noise_level_out_of_range")
    noise = lcg(comfort_noise_seed(frame_index))
    span = 2 * level + 1
    return tuple((noise() % span) - level for _ in range(FRAME_SAMPLES))


def _varint_encode(value: int) -> bytes:
    if value < 0:
        raise ContractError("varint_negative")
    output = bytearray()
    while True:
        block = value & 0x7F
        value >>= 7
        if value:
            output.append(block | 0x80)
        else:
            output.append(block)
            return bytes(output)


def encode_frame(frame: tuple) -> bytes:
    if len(frame) != FRAME_SAMPLES:
        raise ContractError("frame_length_invalid")
    output = bytearray()
    previous = 0
    for sample in frame:
        if not isinstance(sample, int) or isinstance(sample, bool):
            raise ContractError("sample_not_integer")
        if not -32768 <= sample <= 32767:
            raise ContractError("sample_out_of_range")
        residual = sample - previous
        previous = sample
        zigzag = (residual << 1) if residual >= 0 else ((-residual << 1) - 1)
        output += _varint_encode(zigzag)
    return bytes(output)


def decode_frame(data: bytes) -> tuple:
    output: list[int] = []
    previous = 0
    position = 0
    size = len(data)
    while position < size:
        shift = 0
        value = 0
        count = 0
        while True:
            if position >= size:
                raise ContractError("truncated_varint")
            block = data[position]
            position += 1
            count += 1
            if count > 5:
                raise ContractError("varint_too_long")
            value |= (block & 0x7F) << shift
            if not block & 0x80:
                break
            shift += 7
        residual = (value >> 1) if not value & 1 else -((value + 1) >> 1)
        previous += residual
        if not -32768 <= previous <= 32767:
            raise ContractError("sample_out_of_range")
        output.append(previous)
    if len(output) != FRAME_SAMPLES:
        raise ContractError("frame_length_invalid")
    return tuple(output)


def _build_payload(kind: str, frame_bytes: list[bytes],
                   fec_bytes: bytes) -> bytes:
    if kind not in PACKET_KINDS:
        raise ContractError("unknown_packet_kind")
    if not 1 <= len(frame_bytes) <= len(PACKET_FRAME_COUNTS):
        raise ContractError("frame_count_out_of_range")
    kind_bits = 0 if kind == "audio" else 1
    tag = ((len(frame_bytes) - 1) & 0x03)
    tag |= 0x04 if fec_bytes else 0
    tag |= (kind_bits & 0x03) << 3
    payload = bytearray([tag])
    payload += len(fec_bytes).to_bytes(2, "big") + fec_bytes
    for encoded in frame_bytes:
        payload += len(encoded).to_bytes(2, "big") + encoded
    return bytes(payload)


def parse_payload(payload: bytes) -> dict:
    if not payload:
        raise ContractError("empty_payload")
    tag = payload[0]
    if tag & 0xE0:
        raise ContractError("reserved_tag_bits")
    frame_count = (tag & 0x03) + 1
    fec_present = bool(tag & 0x04)
    kind_bits = (tag >> 3) & 0x03
    if kind_bits == 0:
        kind = "audio"
    elif kind_bits == 1:
        kind = "comfort_noise"
    else:
        raise ContractError("unknown_packet_kind")
    position = 1
    if position + 2 > len(payload):
        raise ContractError("truncated_payload")
    fec_length = int.from_bytes(payload[position:position + 2], "big")
    position += 2
    if position + fec_length > len(payload):
        raise ContractError("truncated_fec")
    fec_bytes = payload[position:position + fec_length]
    position += fec_length
    if fec_present != bool(fec_length):
        raise ContractError("fec_flag_mismatch")
    frames: list[bytes] = []
    for _ in range(frame_count):
        if position + 2 > len(payload):
            raise ContractError("truncated_frame")
        length = int.from_bytes(payload[position:position + 2], "big")
        position += 2
        if position + length > len(payload):
            raise ContractError("truncated_frame_body")
        frames.append(payload[position:position + length])
        position += length
    if position != len(payload):
        raise ContractError("trailing_payload_bytes")
    for encoded in frames:
        decode_frame(encoded)
    fec_frame = decode_frame(fec_bytes) if fec_bytes else None
    return {
        "kind": kind,
        "frame_count": frame_count,
        "fec_present": fec_present,
        "frames": frames,
        "fec_frame": fec_frame,
    }


def _packet_record(seq: int, timestamp: int, frame_count: int, kind: str,
                   fec_copy_of: int | None, payload: bytes) -> dict:
    return {
        "seq": seq,
        "timestamp": timestamp,
        "duration_samples": frame_count * FRAME_SAMPLES,
        "frame_count": frame_count,
        "kind": kind,
        "fec_copy_of": fec_copy_of,
        "payload_bytes": len(payload),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "payload_hex": payload.hex(),
    }


def packetize(frames: tuple, labels: list[str], *, packet_frames: int = 2,
              dtx: str = "off", fec: bool = False) -> list[dict]:
    if packet_frames not in PACKET_FRAME_COUNTS:
        raise ContractError("packet_frames_invalid")
    if dtx not in DTX_MODES:
        raise ContractError("dtx_mode_invalid")
    if len(frames) != len(labels):
        raise ContractError("label_length_mismatch")
    packets: list[dict] = []
    pending: list[tuple[int, tuple]] = []

    def emit(entries: list[tuple[int, tuple]], kind: str) -> None:
        if not entries:
            return
        seq = len(packets)
        timestamp = entries[0][0] * FRAME_SAMPLES
        fec_copy_of = None
        fec_bytes = b""
        if fec and kind == "audio" and packets:
            previous = packets[-1]
            previous_start = previous["timestamp"] // FRAME_SAMPLES
            contiguous = (previous["kind"] == "audio"
                          and previous_start + previous["frame_count"]
                          == entries[0][0])
            if contiguous:
                fec_copy_of = previous["seq"]
                fec_bytes = encode_frame(frames[previous_start])
        frame_bytes = [encode_frame(frame) for _index, frame in entries]
        payload = _build_payload(kind, frame_bytes, fec_bytes)
        packets.append(_packet_record(seq, timestamp, len(entries), kind,
                                      fec_copy_of, payload))

    index = 0
    total = len(frames)
    while index < total:
        if dtx != "off" and labels[index] == _LABEL_PAUSE:
            if pending:
                emit(pending, "audio")
                pending = []
            if dtx == "cn":
                emit([(index, comfort_noise_frame(index))], "comfort_noise")
            while index < total and labels[index] == _LABEL_PAUSE:
                index += 1
            continue
        pending.append((index, frames[index]))
        index += 1
        if len(pending) == packet_frames:
            emit(pending, "audio")
            pending = []
    if pending:
        emit(pending, "audio")
    if len(packets) > MAX_PACKETS:
        raise ContractError("packet_count_out_of_range")
    return packets


def _plc_frame(recon: list, index: int) -> tuple:
    for previous in range(index - 1, -1, -1):
        if recon[previous] is not None:
            return tuple(recon[previous])
    return (0,) * FRAME_SAMPLES


def receive(frames: tuple, labels: list[str], trace: list[dict],
            lost_seqs: set[int] | frozenset[int]) -> dict:
    total = len(frames)
    recon: list = [None] * total
    origin: list = [None] * total
    lost = set(lost_seqs)
    fec_protector = {packet["fec_copy_of"]: packet for packet in trace
                     if packet["fec_copy_of"] is not None}
    for packet in trace:
        start = packet["timestamp"] // FRAME_SAMPLES
        if packet["seq"] in lost:
            protector = fec_protector.get(packet["seq"])
            if protector is not None and protector["seq"] not in lost:
                parsed = parse_payload(bytes.fromhex(protector["payload_hex"]))
                if parsed["fec_frame"] is not None:
                    recon[start] = parsed["fec_frame"]
                    origin[start] = "fec"
            for offset in range(packet["frame_count"]):
                index = start + offset
                if recon[index] is None:
                    recon[index] = _plc_frame(recon, index)
                    origin[index] = "plc"
            continue
        parsed = parse_payload(bytes.fromhex(packet["payload_hex"]))
        if packet["kind"] == "comfort_noise":
            recon[start] = parsed["frames"][0]
            origin[start] = "comfort_noise"
        else:
            for offset, encoded in enumerate(parsed["frames"]):
                index = start + offset
                recon[index] = decode_frame(encoded)
                origin[index] = "received"
    for index in range(total):
        if recon[index] is not None:
            continue
        if labels[index] == _LABEL_PAUSE:
            recon[index] = comfort_noise_frame(index)
            origin[index] = "comfort_noise"
        else:
            recon[index] = _plc_frame(recon, index)
            origin[index] = "missing"
    counts = {name: origin.count(name) for name in
              ("received", "fec", "plc", "comfort_noise", "missing")}
    transmitted_exact = all(
        tuple(recon[index]) == tuple(frames[index])
        for index in range(total) if origin[index] in ("received", "fec"))
    peak = max((abs(sample) for frame in recon for sample in frame), default=0)
    return {
        "total_frames": total,
        "counts": counts,
        "accounting_total": sum(counts.values()),
        "received_frames": counts["received"],
        "fec_recovered_frames": counts["fec"],
        "plc_frames": counts["plc"],
        "comfort_noise_frames": counts["comfort_noise"],
        "missing_frames": counts["missing"],
        "transmitted_frames_exact": transmitted_exact,
        "output_peak_abs": peak,
        "output_nonfinite_count": 0,
        "output_digest": object_digest([list(frame) for frame in recon]),
    }


# --------------------------------------------------------------------------
# Admission validators (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _reject(code: str, field: str = "") -> dict:
    return {"accepted": False, "code": code, "field": field,
            "checks": 0, "state_unchanged": True}


def _accept(code: str, checks: int) -> dict:
    return {"accepted": True, "code": code, "field": "", "checks": checks,
            "state_unchanged": True}


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed caller-asset manifest admission. No file is loaded."""
    checks = 0
    if not isinstance(document, dict):
        return _reject("manifest_not_object")
    checks += 1
    unknown = sorted(set(document) - set(MANIFEST_FIELDS))
    if unknown:
        return _reject("unexpected_field", unknown[0])
    missing = [field for field in MANIFEST_FIELDS if field not in document]
    if missing:
        return _reject("missing_field", missing[0])
    checks += 1
    for field in MANIFEST_PATH_FIELDS:
        value = document[field]
        if not isinstance(value, str):
            return _reject("path_not_string", field)
        if not value or not os.path.isabs(value):
            return _reject("path_not_absolute", field)
        if os.path.normpath(value) != value:
            return _reject("path_not_normalized", field)
    checks += 1
    revision = document["source_revision"]
    if not isinstance(revision, str) or not HEX40.match(revision):
        return _reject("revision_not_lower_hex40", "source_revision")
    checks += 1
    for field in MANIFEST_DIGEST_FIELDS:
        value = document[field]
        if not isinstance(value, str) or not HEX64.match(value):
            return _reject("digest_not_lower_hex64", field)
    checks += 1
    codec_id = document["codec_id"]
    if not isinstance(codec_id, str) or not CODEC_ID.match(codec_id):
        return _reject("codec_id_invalid", "codec_id")
    checks += 1
    for field in ("packet_duration_ms", "sdk_sample_rate_hz", "sdk_channels",
                  "sdk_frame_samples"):
        if not _is_int(document[field]):
            return _reject("not_integer", field)
    checks += 1
    if document["packet_duration_ms"] not in ALLOWED_PACKET_MS:
        return _reject("packet_duration_unsupported", "packet_duration_ms")
    for field in ("dtx_enabled", "fec_enabled", "comfort_noise_enabled"):
        if not isinstance(document[field], bool):
            return _reject("not_boolean", field)
    checks += 1
    if document["sdk_sample_rate_hz"] != SAMPLE_RATE_HZ:
        return _reject("sdk_geometry_unsupported", "sdk_sample_rate_hz")
    if document["sdk_channels"] != CHANNELS:
        return _reject("sdk_geometry_unsupported", "sdk_channels")
    if document["sdk_frame_samples"] != FRAME_SAMPLES:
        return _reject("sdk_geometry_unsupported", "sdk_frame_samples")
    checks += 1
    if probe_paths:
        for field in MANIFEST_PATH_FIELDS:
            if not Path(document[field]).is_file():
                return _reject("artifact_absent", field)
        checks += 1
        for path_field, digest_field in zip(MANIFEST_PATH_FIELDS,
                                            MANIFEST_DIGEST_FIELDS):
            if sha256_file(Path(document[path_field])) != document[digest_field]:
                return _reject("artifact_digest_mismatch", digest_field)
        checks += 1
    return _accept("manifest_admitted", checks)


def validate_packet(document: object) -> dict:
    """Fail-closed transmit-packet admission. No codec is involved."""
    checks = 0
    if not isinstance(document, dict):
        return _reject("packet_not_object")
    unknown = sorted(set(document) - set(PACKET_FIELDS))
    if unknown:
        return _reject("unexpected_field", unknown[0])
    missing = [field for field in PACKET_FIELDS if field not in document]
    if missing:
        return _reject("missing_field", missing[0])
    checks += 1
    for field in ("seq", "timestamp", "duration_samples", "frame_count",
                  "payload_bytes"):
        if not _is_int(document[field]):
            return _reject("not_integer", field)
    checks += 1
    seq = document["seq"]
    timestamp = document["timestamp"]
    frame_count = document["frame_count"]
    if not 0 <= seq <= 65535:
        return _reject("seq_out_of_range", "seq")
    if timestamp < 0 or timestamp % FRAME_SAMPLES != 0:
        return _reject("timestamp_not_frame_aligned", "timestamp")
    if not 1 <= frame_count <= len(PACKET_FRAME_COUNTS):
        return _reject("frame_count_out_of_range", "frame_count")
    if document["duration_samples"] != frame_count * FRAME_SAMPLES:
        return _reject("duration_mismatch", "duration_samples")
    checks += 1
    kind = document["kind"]
    if not isinstance(kind, str) or kind not in PACKET_KINDS:
        return _reject("kind_invalid", "kind")
    if kind == "comfort_noise" and frame_count != 1:
        return _reject("comfort_noise_frame_count", "frame_count")
    fec_copy_of = document["fec_copy_of"]
    if fec_copy_of is not None:
        if not _is_int(fec_copy_of) or not 0 <= fec_copy_of < seq:
            return _reject("fec_copy_invalid", "fec_copy_of")
    checks += 1
    payload_hex = document["payload_hex"]
    if not isinstance(payload_hex, str) or not HEX_EVEN.match(payload_hex):
        return _reject("payload_hex_invalid", "payload_hex")
    payload = bytes.fromhex(payload_hex)
    if document["payload_bytes"] != len(payload):
        return _reject("payload_bytes_mismatch", "payload_bytes")
    digest = document["payload_sha256"]
    if not isinstance(digest, str) or not HEX64.match(digest):
        return _reject("payload_digest_invalid", "payload_sha256")
    if hashlib.sha256(payload).hexdigest() != digest:
        return _reject("payload_digest_mismatch", "payload_sha256")
    checks += 1
    try:
        parsed = parse_payload(payload)
    except ContractError as error:
        return _reject("payload_parse_failed:" + str(error), "payload_hex")
    if parsed["kind"] != kind:
        return _reject("payload_kind_mismatch", "kind")
    if parsed["frame_count"] != frame_count:
        return _reject("payload_frame_count_mismatch", "frame_count")
    if parsed["fec_present"] != (fec_copy_of is not None):
        return _reject("payload_fec_mismatch", "fec_copy_of")
    checks += 1
    return _accept("packet_admitted", checks)


def validate_trace(document: object) -> dict:
    """Fail-closed transmit packet-trace admission. No replay is performed."""
    checks = 0
    if not isinstance(document, dict):
        return _reject("trace_not_object")
    unknown = sorted(set(document) - set(TRACE_FIELDS))
    if unknown:
        return _reject("unexpected_field", unknown[0])
    missing = [field for field in TRACE_FIELDS if field not in document]
    if missing:
        return _reject("missing_field", missing[0])
    checks += 1
    trace_id = document["trace_id"]
    if not isinstance(trace_id, str) or not TRACE_ID.match(trace_id):
        return _reject("trace_id_invalid", "trace_id")
    packet_frames = document["packet_frames"]
    if not _is_int(packet_frames) or packet_frames not in PACKET_FRAME_COUNTS:
        return _reject("packet_frames_invalid", "packet_frames")
    dtx = document["dtx"]
    if not isinstance(dtx, str) or dtx not in DTX_MODES:
        return _reject("dtx_mode_invalid", "dtx")
    if not isinstance(document["fec"], bool):
        return _reject("fec_not_boolean", "fec")
    checks += 1
    packets = document["packets"]
    if not isinstance(packets, list):
        return _reject("packets_not_list", "packets")
    if not 1 <= len(packets) <= MAX_PACKETS:
        return _reject("packet_count_out_of_range", "packets")
    checks += 1
    previous_timestamp: int | None = None
    previous_seq: int | None = None
    for index, packet in enumerate(packets):
        prefix = "packets[%d]." % index
        result = validate_packet(packet)
        if not result["accepted"]:
            return _reject(result["code"], prefix + result["field"])
        seq = packet["seq"]
        if seq != index:
            return _reject("seq_not_contiguous", prefix + "seq")
        timestamp = packet["timestamp"]
        if previous_timestamp is not None and timestamp <= previous_timestamp:
            return _reject("timestamp_not_increasing", prefix + "timestamp")
        if packet["frame_count"] > packet_frames:
            return _reject("frame_count_exceeds_packet_frames",
                           prefix + "frame_count")
        fec_copy_of = packet["fec_copy_of"]
        if fec_copy_of is not None and fec_copy_of != previous_seq:
            return _reject("fec_copy_not_previous", prefix + "fec_copy_of")
        if packet["kind"] == "comfort_noise" and document["fec"]:
            if fec_copy_of is not None:
                return _reject("comfort_noise_carries_fec",
                               prefix + "fec_copy_of")
        previous_timestamp = timestamp
        previous_seq = seq
        checks += 1
    return _accept("trace_admitted", checks)


# --------------------------------------------------------------------------
# Synthetic admission controls (never evidence)
# --------------------------------------------------------------------------
_SHORT_LENGTH = 24


def _short_material() -> tuple[tuple, list[str]]:
    frames = synthetic_frames(_SHORT_LENGTH, seed=9100)
    labels = ([_LABEL_VOICED] * 8 + [_LABEL_PAUSE] * 4
              + [_LABEL_VOICED] * 12)
    if len(labels) != _SHORT_LENGTH:
        raise ContractError("short_label_length")
    return frames, labels


def _manifest_control() -> dict:
    synthetic = "d" * 64
    return {
        "source_path": "/caller/opus/source",
        "source_revision": "0" * 40,
        "source_sha256": synthetic,
        "license_path": "/caller/opus/COPYING",
        "license_sha256": synthetic,
        "runtime_path": "/caller/opus/libopus.dylib",
        "runtime_sha256": synthetic,
        "trace_path": "/caller/opus/trace.json",
        "trace_sha256": synthetic,
        "codec_id": "opus",
        "packet_duration_ms": 20,
        "dtx_enabled": True,
        "fec_enabled": True,
        "comfort_noise_enabled": True,
        "sdk_sample_rate_hz": SAMPLE_RATE_HZ,
        "sdk_channels": CHANNELS,
        "sdk_frame_samples": FRAME_SAMPLES,
    }


def _packet_control() -> dict:
    frames, labels = _short_material()
    return packetize(frames, labels, packet_frames=2, dtx="cn",
                     fec=True)[0]


def _trace_control() -> dict:
    frames, labels = _short_material()
    packets = packetize(frames, labels, packet_frames=2, dtx="cn", fec=True)
    return {
        "trace_id": "synthetic-schema-control",
        "packet_frames": 2,
        "dtx": "cn",
        "fec": True,
        "packets": packets,
    }


def admission_controls() -> dict:
    """Build the frozen adverse matrix plus three structural controls."""
    cases: list[dict] = []

    def record(case_id: str, kind: str, result: dict) -> None:
        if result["accepted"]:
            raise ValueError("control_not_rejected:" + case_id)
        cases.append({
            "id": case_id,
            "kind": kind,
            "status": "rejected",
            "code": result["code"],
            "field": result["field"],
            "state_unchanged": result["state_unchanged"],
            "qualifies": False,
            "evidence_class": "synthetic_admission_control",
        })

    def manifest_case(case_id: str, mutate) -> None:
        record(case_id, "manifest", mutate(_manifest_control()))

    def packet_case(case_id: str, mutate) -> None:
        record(case_id, "packet", mutate(_packet_control()))

    def trace_case(case_id: str, mutate) -> None:
        record(case_id, "trace", mutate(_trace_control()))

    def drop(document, field):
        del document[field]
        return validate_manifest(document, probe_paths=False)

    def put(document, field, value):
        document[field] = value
        return validate_manifest(document, probe_paths=False)

    def pput(document, field, value):
        document[field] = value
        return validate_packet(document)

    def tput(document, field, value):
        document[field] = value
        return validate_trace(document)

    def tpacket(document, index, field, value):
        document["packets"][index][field] = value
        return validate_trace(document)

    cases.append({
        "id": "MAN-01", "kind": "manifest", "status": "rejected",
        "code": validate_manifest(None, probe_paths=False)["code"],
        "field": "", "state_unchanged": True, "qualifies": False,
        "evidence_class": "synthetic_admission_control"})
    manifest_case("MAN-02", lambda doc: drop(doc, "source_sha256"))
    manifest_case("MAN-03", lambda doc: put(doc, "source_path", "opus/source"))
    manifest_case("MAN-04", lambda doc: put(doc, "license_path",
                                            "/caller/../opus/COPYING"))
    manifest_case("MAN-05", lambda doc: put(doc, "source_revision", "A" * 40))
    manifest_case("MAN-06", lambda doc: put(doc, "source_sha256", "0" * 63))
    manifest_case("MAN-07", lambda doc: put(doc, "packet_duration_ms", True))
    manifest_case("MAN-08", lambda doc: put(doc, "packet_duration_ms", 15))
    manifest_case("MAN-09", lambda doc: put(doc, "sdk_sample_rate_hz", 48000))
    manifest_case("MAN-10", lambda doc: put(doc, "sdk_channels", 2))
    manifest_case("MAN-11", lambda doc: put(doc, "sdk_frame_samples", 480))
    manifest_case("MAN-12", lambda doc: put(doc, "extra", "value"))
    manifest_case("MAN-13", lambda doc: put(doc, "codec_id", "Opus Main"))
    manifest_case("MAN-14", lambda doc: put(doc, "dtx_enabled", 1))
    manifest_case("MAN-15", lambda doc: validate_manifest(doc,
                                                          probe_paths=True))

    cases.append({
        "id": "PKT-01", "kind": "packet", "status": "rejected",
        "code": validate_packet(None)["code"], "field": "",
        "state_unchanged": True, "qualifies": False,
        "evidence_class": "synthetic_admission_control"})
    packet_case("PKT-02", lambda doc: pput(doc, "unknown", 1))
    packet_case("PKT-03", lambda doc: pput(doc, "seq", True))
    packet_case("PKT-04", lambda doc: pput(doc, "seq", -1))
    packet_case("PKT-05", lambda doc: pput(doc, "timestamp", 160.0))
    packet_case("PKT-06", lambda doc: pput(doc, "duration_samples", 160))
    packet_case("PKT-07", lambda doc: pput(doc, "frame_count", 4))
    packet_case("PKT-08", lambda doc: pput(doc, "kind", "opus"))
    packet_case("PKT-09", lambda doc: pput(doc, "payload_hex", "0"))
    packet_case("PKT-10", lambda doc: pput(doc, "payload_hex", "zz"))
    packet_case("PKT-11", lambda doc: pput(doc, "payload_sha256", "0" * 64))
    packet_case("PKT-12", lambda doc: pput(doc, "payload_bytes", 0))
    packet_case("PKT-13", lambda doc: pput(doc, "fec_copy_of", 1))
    packet_case("PKT-14", lambda doc: pput(doc, "frame_count", 0))
    packet_case("PKT-15", lambda doc: pput(doc, "payload_hex", "ffe0"))
    packet_case("PKT-16", lambda doc: (
        doc.__setitem__("payload_hex", "ffe0"),
        doc.__setitem__("payload_bytes", 2),
        doc.__setitem__("payload_sha256",
                        hashlib.sha256(b"\xff\xe0").hexdigest()),
        validate_packet(doc))[-1])

    cases.append({
        "id": "TRC-01", "kind": "trace", "status": "rejected",
        "code": validate_trace(None)["code"], "field": "",
        "state_unchanged": True, "qualifies": False,
        "evidence_class": "synthetic_admission_control"})
    trace_case("TRC-02", lambda doc: tput(doc, "packets", []))
    trace_case("TRC-03", lambda doc: tpacket(doc, 1, "seq", 0))
    trace_case("TRC-04", lambda doc: tpacket(doc, 1, "timestamp",
                                             doc["packets"][0]["timestamp"]))
    trace_case("TRC-05", lambda doc: tpacket(doc, 1, "timestamp", 161))
    trace_case("TRC-06", lambda doc: tpacket(doc, 1, "duration_samples", 160))
    trace_case("TRC-07", lambda doc: tpacket(doc, 1, "payload_sha256",
                                             "0" * 64))
    trace_case("TRC-08", lambda doc: tpacket(doc, 2, "fec_copy_of", 0))
    trace_case("TRC-09", lambda doc: tput(doc, "extra", 1))
    trace_case("TRC-10", lambda doc: tput(doc, "dtx", "maybe"))
    trace_case("TRC-11", lambda doc: tput(doc, "packet_frames", 4))
    trace_case("TRC-12", lambda doc: tput(doc, "trace_id", "Not An Id"))
    trace_case("TRC-13", lambda doc: tput(doc, "fec", 1))
    trace_case("TRC-14", lambda doc: tput(doc, "packets", {}))

    for case_id, text, code in (
            ("JSON-01", '{"a":1,"a":2}', "duplicate_json_key:a"),
            ("JSON-02", '{"a":NaN}', "nonfinite_json_constant:NaN"),
            ("JSON-03", '{"a":Infinity}', "nonfinite_json_constant:Infinity"),
            ("JSON-04", '[]', "json_root_not_object")):
        try:
            loads_strict(text)
        except ValueError as error:
            message = str(error)
        else:  # pragma: no cover - the fixtures are malformed by design
            message = "accepted"
        cases.append({
            "id": case_id, "kind": "strict_json", "status": "rejected",
            "code": code, "field": "", "message_matches": message == code,
            "state_unchanged": True, "qualifies": False,
            "evidence_class": "synthetic_admission_control"})

    manifest_control = validate_manifest(_manifest_control(),
                                         probe_paths=False)
    packet_control = validate_packet(_packet_control())
    trace_control = validate_trace(_trace_control())
    controls = [
        {"id": "CTL-01", "kind": "manifest",
         "status": "accepted_schema_control",
         "code": manifest_control["code"],
         "checks": manifest_control["checks"],
         "artifacts_probed": False,
         "evidence_class": "synthetic_schema_control_not_evidence",
         "qualifies": False, "runtime_loaded": False},
        {"id": "CTL-02", "kind": "packet",
         "status": "accepted_schema_control",
         "code": packet_control["code"],
         "checks": packet_control["checks"],
         "codec_invoked": False,
         "evidence_class": "synthetic_schema_control_not_evidence",
         "qualifies": False},
        {"id": "CTL-03", "kind": "trace",
         "status": "accepted_schema_control",
         "code": trace_control["code"],
         "checks": trace_control["checks"],
         "packets_admitted": len(_trace_control()["packets"]),
         "replay_performed": False, "codec_invoked": False,
         "evidence_class": "synthetic_schema_control_not_evidence",
         "qualifies": False},
    ]
    return {"cases": cases, "controls": controls}


# --------------------------------------------------------------------------
# Static rows and contract document
# --------------------------------------------------------------------------
def _artifact_rows() -> list[dict]:
    return [{
        "id": artifact["id"],
        "kind": artifact["kind"],
        "requirement": artifact["requirement"],
        "present": False,
        "verified": False,
        "sha256": None,
        "blocked": True,
    } for artifact in REQUIRED_ARTIFACTS]


def _blocker_rows() -> list[dict]:
    return [{
        "id": blocker["id"],
        "artifact_id": blocker["artifact_id"],
        "statement": blocker["statement"],
        "required_action": blocker["required_action"],
        "linked_gates": list(blocker["linked_gates"]),
        "status": "open",
        "qualifies": False,
    } for blocker in EXACT_BLOCKERS]


def _gate_rows() -> list[dict]:
    identity = {"task_id": TASK, "component_id": COMPONENT_ID, "mode": MODE}
    return [{
        "id": gate["id"],
        "title": gate["title"],
        "statement": gate["statement"],
        "reopen_condition": gate["reopen_condition"],
        "status": "blocked",
        "qualifies": False,
        "linked_row": identity,
    } for gate in RELEASE_GATES]


def linked_row_identity() -> dict:
    projection = {field: BOARD_ROW_PROJECTION[field]
                  for field in BOARD_ROW_FIELDS}
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "selector": "stable-row-identity/0.1:" + ",".join(BOARD_ROW_FIELDS),
        "gating": "stable_identity_only",
        "mutable_fields_excluded": ["status", "owner", "claim", "review",
                                    "handoff", "blocked_reason",
                                    "dispatch_priority"],
        "board_file_pinned": False,
        "board_status_gates_anything": False,
    }


def manifest_contract() -> dict:
    return {
        "fields": list(MANIFEST_FIELDS),
        "path_fields": list(MANIFEST_PATH_FIELDS),
        "digest_fields": list(MANIFEST_DIGEST_FIELDS),
        "allowed_packet_duration_ms": list(ALLOWED_PACKET_MS),
        "sdk_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
        },
        "probe_paths_default": True,
    }


def contract_document() -> dict:
    controls = admission_controls()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "profile": PROFILE,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "decision": "DEFER",
        "status": "incomplete",
        "candidate_status": "proposal_only_not_qualified",
        "qualification_status": "not_qualified",
        "no_missing_result_qualifies": True,
        "board_status_is_observation_only": True,
        "board_file_pinned": False,
        "disposition": dict(DISPOSITION),
        "boundary": dict(BOUNDARY),
        "public_v0_geometry": dict(PUBLIC_V0_GEOMETRY),
        "scope": dict(SCOPE),
        "exact_scope": dict(EXACT_SCOPE),
        "qualification": dict(QUALIFICATION),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_row_projection": dict(BOARD_ROW_PROJECTION),
        "board_row_projection_sha256":
            board_row_digest(BOARD_ROW_PROJECTION),
        "absence_probes": list(ABSENCE_PROBES),
        "required_artifacts": _artifact_rows(),
        "exact_blockers": _blocker_rows(),
        "release_gates": _gate_rows(),
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "tool_profile_rows": [dict(row) for row in TOOL_PROFILE_ROWS],
        "packet_contract": PACKET_CONTRACT,
        "manifest_contract": manifest_contract(),
        "admission_contract": {
            "manifest_fields": list(MANIFEST_FIELDS),
            "packet_fields": list(PACKET_FIELDS),
            "trace_fields": list(TRACE_FIELDS),
            "case_ids": [case["id"] for case in controls["cases"]],
            "control_ids": [control["id"] for control in controls["controls"]],
            "empty_payload_sha256": hashlib.sha256(b"").hexdigest(),
        },
        "upstream_blocker": UPSTREAM_BLOCKER,
        "regeneration": dict(REGENERATION),
        "reproduction": dict(REPRODUCTION),
    }


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_id")
    if contract.get("contract_id") != CONTRACT_ID:
        raise ValueError("contract_contract_id")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("component") != COMPONENT_ID:
        raise ValueError("contract_component")
    if contract.get("profile") != PROFILE or contract.get("mode") != MODE:
        raise ValueError("contract_profile_or_mode")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != "incomplete":
        raise ValueError("contract_status")
    if contract.get("candidate_status") != "proposal_only_not_qualified":
        raise ValueError("contract_candidate_status")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification_status")
    if contract.get("no_missing_result_qualifies") is not True:
        raise ValueError("contract_missing_result_gate")
    if contract.get("board_file_pinned") is not False:
        raise ValueError("contract_board_file_pinned")
    if len(contract.get("release_gates", [])) != 8:
        raise ValueError("contract_gate_count")
    if any(gate.get("status") != "blocked" for gate in contract["release_gates"]):
        raise ValueError("contract_gate_not_blocked")
    if len(contract.get("required_artifacts", [])) != 6:
        raise ValueError("contract_artifact_count")
    if len(contract.get("exact_blockers", [])) != 6:
        raise ValueError("contract_blocker_count")
    if contract.get("board_row_projection") != BOARD_ROW_PROJECTION:
        raise ValueError("contract_board_row_projection")
    if contract.get("board_row_projection_sha256") != board_row_digest(
            BOARD_ROW_PROJECTION):
        raise ValueError("contract_board_projection_digest")
    for key, value in (("source_pins", SOURCE_PINS),
                       ("boundary_pins", BOUNDARY_PINS)):
        if contract.get(key) != value:
            raise ValueError("contract_pin_table:" + key)
    if contract.get("absence_probes") != list(ABSENCE_PROBES):
        raise ValueError("contract_absence_probes")
    blocker = contract.get("upstream_blocker", {})
    if blocker.get("status") != "blocked_upstream_absent":
        raise ValueError("contract_upstream_blocker_status")
    if blocker.get("pinned_revision") is not None \
            or blocker.get("source_digest") is not None:
        raise ValueError("contract_upstream_blocker_claims_revision")
    if blocker.get("no_upstream_parity_claim") is not True:
        raise ValueError("contract_upstream_parity_claim")
    contract_model = contract.get("packet_contract", {})
    if contract_model.get("not_opus") is not True \
            or contract_model.get("distinct_from_pcm") is not True \
            or contract_model.get("codec_operation") is not False \
            or contract_model.get("rfc6716_toc_used") is not False:
        raise ValueError("contract_packet_model_claim")
    qualification = contract.get("qualification", {})
    if (qualification.get("status") != "not_qualified"
            or qualification.get("readiness") != "incomplete"
            or qualification.get("decision") != "DEFER"
            or qualification.get("upstream_parity") is not False
            or qualification.get("candidate_qualified") is not False):
        raise ValueError("contract_qualification")
    if contract.get("tool_profile_rows") != [dict(row) for row in
                                             TOOL_PROFILE_ROWS]:
        raise ValueError("contract_tool_profile")


# --------------------------------------------------------------------------
# Canonical report
# --------------------------------------------------------------------------
def _condition(frames: tuple, labels: list[str], packet_frames: int,
               dtx: str, fec: bool, losses=()) -> dict:
    trace = packetize(frames, labels, packet_frames=packet_frames, dtx=dtx,
                      fec=fec)
    reconstruction = receive(frames, labels, trace, set(losses))
    total_bytes = sum(packet["payload_bytes"] for packet in trace)
    audio_packets = sum(1 for packet in trace if packet["kind"] == "audio")
    cn_packets = sum(1 for packet in trace
                     if packet["kind"] == "comfort_noise")
    transmitted = sum(packet["frame_count"] for packet in trace
                      if packet["kind"] == "audio")
    return {
        "packet_frames": packet_frames,
        "packet_duration_ms": packet_frames * FRAME_MS,
        "dtx": dtx,
        "fec": fec,
        "losses": list(losses),
        "packet_count": len(trace),
        "audio_packets": audio_packets,
        "comfort_noise_packets": cn_packets,
        "total_payload_bytes": total_bytes,
        "mean_payload_bytes_milli": total_bytes * 1000 // len(trace),
        "transmitted_source_frames": transmitted,
        "omitted_source_frames": len(frames) - transmitted,
        "trace_digest": object_digest(trace),
        "reconstruction": reconstruction,
    }


def build_report() -> dict:
    contract = read_strict_json(HERE / "contract.json")
    validate_contract(contract)
    probes = absence_probes(AUDIO_ROOT)
    controls = admission_controls()
    rejected = [case for case in controls["cases"]
                if case["status"] == "rejected"]
    accepted_controls = [control for control in controls["controls"]
                         if control["status"] == "accepted_schema_control"]

    frames = synthetic_frames(100)
    labels = frame_labels(100)

    grid = {}
    for packet_frames in PACKET_FRAME_COUNTS:
        condition = _condition(frames, labels, packet_frames, "off", False)
        grid[str(packet_frames * FRAME_MS) + "ms"] = condition

    dtx_conditions = {}
    for mode in DTX_MODES:
        dtx_conditions[mode] = _condition(frames, labels, 2, mode, False)

    fec_conditions = {}
    for enabled in (False, True):
        fec_conditions["on" if enabled else "off"] = _condition(
            frames, labels, 2, "off", enabled)
    overhead = (fec_conditions["on"]["total_payload_bytes"]
                - fec_conditions["off"]["total_payload_bytes"])
    overhead_ppm = (overhead * 1_000_000
                    // fec_conditions["off"]["total_payload_bytes"])

    loss_conditions = {}
    for name, lost in (("single", (2,)), ("burst_two", (5, 6))):
        for enabled in (False, True):
            key = name + "_fec_" + ("on" if enabled else "off")
            loss_conditions[key] = _condition(
                frames, labels, 2, "off", enabled, losses=lost)

    short_frames, short_labels = _short_material()
    short_trace = packetize(short_frames, short_labels, packet_frames=2,
                            dtx="cn", fec=True)
    short_receive = receive(short_frames, short_labels, short_trace, {2})
    trace_document = {
        "trace_id": "synthetic-dtx-cn-fec-trace",
        "packet_frames": 2,
        "dtx": "cn",
        "fec": True,
        "packets": short_trace,
    }
    trace_validation = validate_trace(trace_document)

    # Fail closed if the synthetic model stops demonstrating its own contract.
    if not all(condition["reconstruction"]["accounting_total"]
               == condition["reconstruction"]["total_frames"]
               for condition in grid.values()):
        raise ValueError("frame_accounting_incomplete")
    if not all(condition["reconstruction"]["output_nonfinite_count"] == 0
               and condition["reconstruction"]["output_peak_abs"] <= 32767
               for condition in grid.values()):
        raise ValueError("synthetic_output_not_bounded")
    if dtx_conditions["cn"]["packet_count"] >= dtx_conditions["off"]["packet_count"]:
        raise ValueError("dtx_did_not_suppress_packets")
    if dtx_conditions["cn"]["comfort_noise_packets"] < 1:
        raise ValueError("comfort_noise_not_emitted")
    if dtx_conditions["omit"]["comfort_noise_packets"] != 0:
        raise ValueError("omit_mode_emitted_comfort_noise")
    if overhead <= 0 or fec_conditions["on"][
            "reconstruction"]["fec_recovered_frames"] != 0:
        raise ValueError("fec_overhead_or_recovery_invalid")
    if loss_conditions["single_fec_on"]["reconstruction"][
            "fec_recovered_frames"] != 1:
        raise ValueError("single_loss_fec_recovery_failed")
    if loss_conditions["single_fec_on"]["reconstruction"]["plc_frames"] != 1:
        raise ValueError("single_loss_plc_fallback_missing")
    if loss_conditions["single_fec_off"]["reconstruction"][
            "fec_recovered_frames"] != 0:
        raise ValueError("fec_off_recovered_frames")
    if loss_conditions["burst_two_fec_on"]["reconstruction"][
            "fec_recovered_frames"] != 1:
        raise ValueError("burst_fec_depth_not_one")
    if loss_conditions["burst_two_fec_on"]["reconstruction"]["plc_frames"] < 1:
        raise ValueError("burst_plc_fallback_missing")
    if not short_receive["transmitted_frames_exact"]:
        raise ValueError("lossless_container_not_exact")
    if not trace_validation["accepted"]:
        raise ValueError("primary_trace_not_admitted")
    if accepted_controls != [control for control in controls["controls"]
                             if control["id"] in
                             ("CTL-01", "CTL-02", "CTL-03")]:
        raise ValueError("schema_controls_invalid")
    if any(case["status"] != "rejected" for case in controls["cases"]):
        raise ValueError("admission_case_not_rejected")

    required_results = {
        "packet_contract_distinct_from_pcm": PACKET_CONTRACT[
            "distinct_from_pcm"] is True,
        "packet_payload_roundtrip_exact": all(
            decode_frame(encode_frame(frame)) == frame
            for frame in frames[:10]),
        "packetization_grid_complete": sorted(grid) == ["10ms", "20ms", "30ms"],
        "dtx_suppresses_source_frames": dtx_conditions["cn"][
            "omitted_source_frames"] > 0,
        "comfort_noise_bounded_and_nonzero": (
            dtx_conditions["cn"]["reconstruction"]["comfort_noise_frames"] > 0
            and dtx_conditions["cn"]["reconstruction"]["output_peak_abs"] > 0),
        "fec_single_loss_recovery_exact": (
            loss_conditions["single_fec_on"]["reconstruction"]
            ["fec_recovered_frames"] == 1
            and loss_conditions["single_fec_on"]["reconstruction"]
            ["transmitted_frames_exact"]),
        "fec_burst_depth_recorded": (
            loss_conditions["burst_two_fec_on"]["reconstruction"]
            ["fec_recovered_frames"] == 1),
        "plc_fallback_recorded": (
            loss_conditions["burst_two_fec_on"]["reconstruction"]
            ["plc_frames"] >= 1),
        "manifest_admission_strict": all(
            case["status"] == "rejected" for case in controls["cases"]
            if case["kind"] == "manifest"),
        "packet_admission_strict": all(
            case["status"] == "rejected" for case in controls["cases"]
            if case["kind"] == "packet"),
        "trace_admission_strict": all(
            case["status"] == "rejected" for case in controls["cases"]
            if case["kind"] == "trace"),
        "invalid_missing_nonfinite_rejected": all(
            case["status"] == "rejected" for case in controls["cases"]),
        "frame_accounting_complete": all(
            condition["reconstruction"]["accounting_total"]
            == condition["reconstruction"]["total_frames"]
            for condition in grid.values()),
        "no_codec_runtime_used": SCOPE["codec_runtime_executed"] is False,
        "no_result_qualifies": True,
    }
    if not all(required_results.values()):
        raise ValueError("required_result_false")

    gates = _gate_rows()
    blockers = _blocker_rows()
    artifacts = _artifact_rows()
    identity = linked_row_identity()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "task_id": TASK,
        "task_title": TASK_TITLE,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "status": "incomplete",
        "candidate_status": "proposal_only_not_qualified",
        "qualification_status": "not_qualified",
        "decision": "DEFER",
        "no_missing_result_qualifies": True,
        "board_status_is_observation_only": True,
        "board_file_pinned": False,
        "disposition": dict(contract["disposition"]),
        "boundary": dict(contract["boundary"]),
        "public_v0_geometry": dict(contract["public_v0_geometry"]),
        "scope": dict(contract["scope"]),
        "exact_scope": dict(contract["exact_scope"]),
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
            "observed_unqualified_binaries":
                [dict(row) for row in OBSERVED_UNQUALIFIED_BINARIES],
            "conclusion": (
                "No permitted Opus source, header, license text, build, runtime "
                "or packet-trace asset exists at any fixed admitted probe. An "
                "unqualified PyAV-bundled libopus dylib outside the admitted "
                "boundary is recorded as provenance and is not used."),
        },
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "upstream_blocker": dict(contract["upstream_blocker"]),
        "tool_profile": {
            "profile": "tool",
            "rows": [dict(row) for row in TOOL_PROFILE_ROWS],
            "runtime_version": None,
            "install_location": None,
            "provenance": None,
            "clean_checkout_verified": False,
            "typical_use_performed": False,
            "caller_owned_inputs_admitted": False,
            "malformed_inputs_checked": True,
            "missing_optional_selection_exercised": False,
            "compile_build_evidence": False,
            "codec_synthetic_runtime_evidence": False,
            "measured_workload_support": False,
            "task_local_contract_model_executed": True,
            "task_local_contract_model_is_runtime_evidence": False,
            "status": "blocked",
        },
        "packet_contract_model": dict(PACKET_CONTRACT),
        "conditions": {
            "packetization_grid": grid,
            "dtx": dtx_conditions,
            "fec": {
                "off": fec_conditions["off"],
                "on": fec_conditions["on"],
                "overhead_bytes": overhead,
                "overhead_ppm": overhead_ppm,
                "fec_copy_packets": sum(
                    1 for packet in packetize(frames, labels, packet_frames=2,
                                              dtx="off", fec=True)
                    if packet["fec_copy_of"] is not None),
                "recovery_depth_packets": 1,
            },
            "loss": loss_conditions,
        },
        "packet_trace": {
            "trace_id": trace_document["trace_id"],
            "signal_frames": _SHORT_LENGTH,
            "packet_frames": 2,
            "dtx": "cn",
            "fec": True,
            "lost_seqs": [2],
            "packet_count": len(short_trace),
            "packets_are_not_pcm": True,
            "payload_hex_included": True,
            "codec_runtime_used": False,
            "trace_digest": object_digest(short_trace),
            "validation": trace_validation,
            "reconstruction": short_receive,
            "packets": short_trace,
        },
        "admission": {
            "policy": "task_local_fail_closed_admission_not_runtime_behavior",
            "cases": controls["cases"],
            "schema_controls": controls["controls"],
            "summary": {
                "case_count": len(controls["cases"]),
                "rejected_count": len(rejected),
                "accepted_schema_controls": len(accepted_controls),
                "qualifying_results": 0,
                "state_advanced_on_rejection": any(
                    case["state_unchanged"] is not True for case in rejected),
                "runtime_invoked": False,
                "codec_invoked": False,
                "replay_performed": False,
            },
        },
        "required_results": required_results,
        "qualification": {
            "status": "not_qualified",
            "readiness": "incomplete",
            "decision": "DEFER",
            "processor_exposure": "DEFER",
            "proposal_only": True,
            "all_release_gates_blocked": True,
            "all_required_results_present": all(required_results.values()),
            "real_codec_source_present": False,
            "real_codec_runtime_present": False,
            "codec_runtime_executed": False,
            "real_packet_trace_present": False,
            "real_audio_present": False,
            "upstream_parity": False,
            "candidate_qualified": False,
            "missing_result_promoted": False,
            "not_qualified": True,
        },
        "prohibited_claims": list(PROHIBITED_CLAIMS),
        "gates": gates,
        "linked_row_identity": identity,
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "regeneration": dict(contract["regeneration"]),
        "reproduction": dict(contract["reproduction"]),
        "non_claims": [
            "No installed v0, public API, C ABI, descriptor, registry or default change.",
            "No C provider, installed target, registration or descriptor is added.",
            "No Opus, libopus, CELP, SILK, DRED or LACE source, binary, header or runtime.",
            "No real speech, noise, corpus, listening panel or quality claim.",
            "No device timing, fill/flush, deadline, CPU, memory or release qualification.",
            "No missing result qualifies a candidate; every adverse case is excluded.",
        ],
    }
    return report


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
