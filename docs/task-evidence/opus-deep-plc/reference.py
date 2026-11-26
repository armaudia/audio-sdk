# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-OPUS-DEEP-PLC (Opus deep PLC).

This module is standard-library only and deterministic. It contains no Opus
source, libopus binary, deep-PLC model data, weight, encoder or decoder
runtime, codec stream, packet-loss trace, speech corpus or vendor result. It
records the exact external blocker, probes a fixed list of task-local paths to
evidence the absence, validates a caller-supplied restoration cohort manifest
that represents loss only through explicit missing-packet events, and builds
the canonical report.

Nothing here is a deep-PLC implementation, an upstream-parity result, a
missing-packet-event measurement, a concealment-interval result, a quality
result, a listening result, a device-timing result, a benchmark or a release
claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-OPUS-DEEP-PLC"
COMPONENT_ID = "opus-deep-plc"
TASK_TITLE = "Opus deep PLC"
CONTRACT_ID = "audio-sdk/opus-deep-plc-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "restoration"
MODE = "feasibility"
BASE_COMMIT = "59469bca84c63b9fc71a3a3b115567df92170df0"
BRANCH = "swarm/SDK-OPUS-DEEP-PLC"
REVIEWER = "reviewer-OPUS-DEEP-PLC"
CLAIM_WORKTREE = ("/Users/htsakanyan/workspace/audio/audioml/worktrees/"
                  "audio-sdk/SDK-OPUS-DEEP-PLC")
WRITE_SCOPE = "docs/task-evidence/opus-deep-plc/ only"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
TASK_PREFIX = "docs/task-evidence/opus-deep-plc/"


def _find_audio_root() -> Path:
    """Locate the audioml workspace without a recursive walk or network use."""
    override = os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

# Immutable inputs. `source:` rows are workspace-relative; the rest are
# SDK-worktree-relative. The mutable shared board is deliberately excluded from
# the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/distortion_restoration_20261028.md":
        "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md":
        "79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
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
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md":
        "ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/report.json":
        "ec4c9ea5e46e02d9866920458b4d6365d300d8bcd626d2e05bf7f4c4955a080e",
    "docs/task-evidence/opus-dred/report.json":
        "2997dc6cc9e623a762379ca498c178c22a9607591a39ea8bcf6ef2691544a3f2",
    "docs/task-evidence/pitch-period-repeat-plc/README.md":
        "8fb323ffd7ce59c361ac1078d7c434b1b3c0b5f088d9a7d07ae5b2278cfa3ea9",
}

# Only stable, non-mutable identity fields are projected. `status`, `owner`,
# `claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` never
# enter canonical bytes and never gate this package.
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_PROJECTION = {
    "id": TASK,
    "title": TASK_TITLE,
    "component": COMPONENT_ID,
    "mode": MODE,
    "repository": "audio-sdk",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
}
LINKED_ROWS = (
    BOARD_ROW_PROJECTION,
    {
        "id": "SDK-OPUS-1-4-STANDARD-DECODER-PLC",
        "title": "Opus 1.4 standard decoder PLC",
        "component": "opus-1-4-standard-decoder-plc",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-ELASTIC",
                       "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-OPUS-DRED",
        "title": "Opus DRED",
        "component": "opus-dred",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                       "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE",
        "title": "Opus packetization, FEC, DTX and comfort noise",
        "component": "opus-packetization-fec-dtx-and-comfort-noise",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                       "SDK-FND-PROVIDER"],
    },
)

# Fixed, bounded absence probes. No recursive workspace walk is performed and
# no download is attempted. Any present path makes report generation fail.
ABSENCE_PROBES = (
    "data/checkouts/opus",
    "data/checkouts/opus-1.5",
    "data/checkouts/opus-1.6",
    "data/checkouts/libopus",
    "data/checkouts/opus-deep-plc",
    "adapters/opus-deep-plc",
    "adapters/opus-deep-plc/run.py",
    "third_party/opus",
    "third_party/libopus",
    "deps/opus",
    "deps/libopus",
    "src/opus_decoder.c",
    "celt/celt_decoder.c",
    "dnn",
    "dnn/osce.c",
    "dnn/osce_features.c",
    "dnn/plc_data.c",
    "dnn/plc_data.h",
    "dnn/lpcnet_plc.c",
    "include/opus.h",
    "include/opus_deep_plc.h",
    "data/assets/opus-deep-plc",
    "data/assets/opus-plc-model.bin",
    "data/traces/opus-deep-plc",
    "research/voice-enhancement-20261101/agent-opus-deep-plc",
    "LICENSES/Opus-BSD-3-Clause.txt",
    "third_party/opus/COPYING",
    "opus-1.5",
    "notices/third-party/opus",
)

# An unqualified transitive PyAV-wheel binary observed during authoring. It is
# provenance only: no license/notice bundle, source revision or rights review
# accompanies it, and this package never loads or executes it. The observation
# found DRED decoder symbols but no distinct exported deep-PLC selector, which
# is itself not evidence that deep PLC is unavailable upstream.
UNQUALIFIED_RUNTIME = {
    "path": ("cpp-library/pipeline-validation/playback-speed/.venv/lib/"
             "python3.11/site-packages/av/.dylibs/libopus.0.dylib"),
    "sha256": ("dca12b81b778f51dc5cecbc789fffaac472de09b102a164d5348b360b"
               "238a202"),
    "byte_count": 636800,
    "version_string": "libopus 1.6.1",
    "kind": "dynamic_library",
    "authoring_probe": ("read-only version-string and exported-symbol "
                        "provenance probe; no deep-PLC decode, concealment, "
                        "model load, packet parse or audio operation was "
                        "executed"),
    "dred_symbols_observed": [
        "opus_dred_decoder_create",
        "opus_dred_decoder_destroy",
        "opus_dred_decoder_get_size",
        "opus_dred_decoder_init",
        "opus_dred_parse",
        "opus_dred_process",
        "opus_dred_alloc",
        "opus_dred_free",
        "opus_decoder_dred_decode",
        "opus_decoder_dred_decode_float",
        "opus_decoder_dred_decode24",
    ],
    "deep_plc_selector_symbols_observed": [],
    "deep_plc_capability_verified": False,
    "license_text_present": False,
    "source_revision": None,
    "git_tracked": False,
    "git_ignored": True,
    "admitted": False,
    "linked": False,
    "executed_by_package": False,
    "used_for_evidence": False,
    "reason": (
        "Unqualified transitive PyAV 18.1.0 wheel binary in a gitignored, "
        "mutable virtualenv. It ships the PyAV wheel license, not the Opus "
        "COPYING/LICENSE_PLEASE_READ.txt or copyright notices, pins no "
        "source revision, and has no deep-PLC selector, model geometry, "
        "rights-cleared missing-packet trace or product rights review. "
        "Exported DRED decoder symbols are unrelated to deep PLC and do not "
        "admit this binary as a deep-PLC runtime."),
}

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "permitted_source",
        "requirement": (
            "Exact permitted Opus source tree at revision >= 1.5 that "
            "contains the deep-PLC (neural PLC) decoder path and its model "
            "data, pinned by an immutable 40-hex revision and an immutable "
            "archive SHA-256."),
    },
    {
        "id": "ART-02",
        "kind": "license_and_model_terms",
        "requirement": (
            "The upstream BSD-3-Clause license text, copyright notices, "
            "deep-PLC model-data/weight terms and complete third-party "
            "notice bundle that apply to the pinned revision, with an "
            "explicit rights review."),
    },
    {
        "id": "ART-03",
        "kind": "built_deep_plc_runtime",
        "requirement": (
            "A reproducible pinned libopus build with the exact decoder "
            "control/API or build option that selects deep PLC, its contrast "
            "standard-PLC condition, default state, install location and "
            "artifact SHA-256."),
    },
    {
        "id": "ART-04",
        "kind": "deep_plc_model_and_runtime",
        "requirement": (
            "The exact deep-PLC model assets or compiled model blobs, "
            "inference runtime, feature/state geometry and per-asset "
            "SHA-256, with redistribution and product-use terms."),
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_events_and_baseline",
        "requirement": (
            "A rights-cleared frozen packet corpus whose losses are "
            "represented by explicit missing-packet events, with packet "
            "metadata, loss strata, a matching standard-PLC control and the "
            "corresponding clean/source baseline."),
    },
    {
        "id": "ART-06",
        "kind": "measurement_and_quality_harness",
        "requirement": (
            "An agreed task-specific quality, independent listening, output "
            "peak, concealment-interval, content/availability delay and "
            "target-runtime timing/resource protocol with margins, deadlines "
            "and limits."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-01",
        "statement": (
            "No permitted Opus source snapshot containing deep PLC exists in "
            "this workspace. Every fixed absence probe is missing, and no "
            "revision or archive digest can be pinned from a local "
            "artifact."),
        "required_action": (
            "Supply the exact Opus source revision (>= 1.5) containing the "
            "deep-PLC decoder path and model data, with an immutable archive "
            "SHA-256, from a source root that permits review."),
        "linked_gates": ["RG-01", "RG-03"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-02",
        "statement": (
            "The upstream license, copyright, deep-PLC model-data terms and "
            "notice bundle are absent, so no redistribution or product-use "
            "scope for a deep-PLC artifact can be reviewed."),
        "required_action": (
            "Supply the complete license/notices/model-terms bundle for the "
            "pinned revision and record an explicit rights decision."),
        "linked_gates": ["RG-02"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-03",
        "statement": (
            "No built libopus runtime, installed location or reproducible "
            "build recipe is present. The exact deep-PLC selector, decoder "
            "symbols, default state and standard-PLC contrast cannot be "
            "exercised or verified."),
        "required_action": (
            "Supply a reproducible pinned build and identify the exact "
            "deep-PLC selector/API, accepted values, decoder symbols, "
            "default state and artifact digest from the pinned source."),
        "linked_gates": ["RG-03", "RG-07"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-04",
        "statement": (
            "No deep-PLC model asset, compiled model blob, inference "
            "runtime or feature/state geometry is present. Nothing was "
            "downloaded, reconstructed or substituted."),
        "required_action": (
            "Supply the exact deep-PLC model assets and inference runtime "
            "with per-asset SHA-256, geometry, provenance and permitted-use "
            "terms."),
        "linked_gates": ["RG-04", "RG-03"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "statement": (
            "No rights-cleared packet corpus with explicit missing-packet "
            "events, packet metadata, matching standard-PLC control or "
            "matching clean/source baseline is present."),
        "required_action": (
            "Supply an immutable corpus and loss trace whose every loss is an "
            "explicit missing-packet event reported to the decoder, with "
            "provenance, packet metadata, declared strata, a standard-PLC "
            "control and a corresponding clean/source baseline."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "statement": (
            "No task-specific quality, independent listening, output-peak, "
            "concealment-interval, delay or target-runtime timing/resource "
            "protocol and no agreed margins, deadlines or limits exist, so "
            "no result can qualify."),
        "required_action": (
            "Agree and staff the task-specific quality, listening, peak, "
            "missing-event/concealment and target-runtime protocols, margins, "
            "deadlines and resource limits before collecting results."),
        "linked_gates": ["RG-06", "RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "upstream_source_and_revision_pin",
        "statement": (
            "An exact permitted Opus source revision containing deep PLC and "
            "an immutable archive are pinned before any implementation "
            "claim."),
        "reopen_condition": (
            "The exact source revision, tree and archive digests are recorded "
            "and the source root permits local review."),
    },
    {
        "id": "RG-02",
        "title": "upstream_license_model_terms_and_notices",
        "statement": (
            "A reviewed license, deep-PLC model-data terms and notice bundle "
            "exists for the pinned revision."),
        "reopen_condition": (
            "The complete license/notices/model-terms bundle is supplied, "
            "reviewed and its approved scope recorded."),
    },
    {
        "id": "RG-03",
        "title": "exact_build_and_deep_plc_selection_parity",
        "statement": (
            "A reproducible build and the exact deep-PLC selector, decoder "
            "symbols, default state and standard-PLC contrast are verified."),
        "reopen_condition": (
            "Build and install the pinned revision and map the exact "
            "deep-PLC selector, values, symbols and default behavior to this "
            "boundary."),
    },
    {
        "id": "RG-04",
        "title": "deep_plc_model_and_runtime_integrity",
        "statement": (
            "Every deep-PLC model asset and its inference runtime are pinned "
            "and integrity-checked."),
        "reopen_condition": (
            "Pin each asset and runtime by SHA-256, verify geometry and "
            "provenance, and confirm permitted use."),
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_explicit_missing_event_cohort",
        "statement": (
            "A rights-cleared corpus with explicit missing-packet events, "
            "metadata, strata, a standard-PLC control and a clean baseline "
            "is frozen before any result."),
        "reopen_condition": (
            "The immutable corpus and loss trace, explicit event records, "
            "metadata, strata, control and corresponding baseline are "
            "supplied and reviewed."),
    },
    {
        "id": "RG-06",
        "title": "task_specific_quality_and_independent_listening",
        "statement": (
            "Task-specific quality and independent listening are completed "
            "for the exact conditions and rights scope."),
        "reopen_condition": (
            "Pinned scorers and an approved listening protocol/panel produce "
            "reviewed results on the frozen cohort."),
    },
    {
        "id": "RG-07",
        "title": "concealment_peak_delay_and_resources",
        "statement": (
            "Missing-event accounting, concealment intervals, output-peak "
            "bounds, content/availability delay and target-runtime resource "
            "limits are measured, not inferred."),
        "reopen_condition": (
            "Paced target-runtime runs record explicit events, concealment "
            "intervals, peaks, delay, CPU, memory and deadline behavior "
            "against agreed limits."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "statement": (
            "Opt-in provider intake, an explicit public-surface decision, "
            "independent review and release approval are complete."),
        "reopen_condition": (
            "A separate versioned intake accepts the component with an OFF "
            "default, records the public-surface decision and passes "
            "independent exact-head review."),
    },
)

RESTORATION_PROFILE_ROWS = (
    {
        "id": "RST-01",
        "requirement": (
            "Freeze corruption, metadata and the corresponding clean/audio "
            "packet baseline."),
        "status": "blocked",
        "evidence": (
            "No genuine packet corpus, explicit missing-packet event trace, "
            "packet metadata or clean baseline is present; the manifest "
            "schema admits none."),
    },
    {
        "id": "RST-02",
        "requirement": (
            "Stratify by degradation, erasure burst and bandwidth."),
        "status": "blocked",
        "evidence": (
            "Strata are declared in the admission schema only; no real "
            "degradation, burst or bandwidth cohort exists."),
    },
    {
        "id": "RST-03",
        "requirement": (
            "Report discrete concealment/validity and decoded intervals."),
        "status": "blocked",
        "evidence": (
            "No decoder runs, so no explicit missing event, concealed "
            "interval, valid or decoded sample is observed or reported."),
    },
    {
        "id": "RST-04",
        "requirement": (
            "Report task-specific quality on genuine low-bitrate traffic."),
        "status": "blocked",
        "evidence": (
            "No deep-PLC output, standard-PLC control, clean reference, "
            "pinned scorer or listening result exists."),
    },
    {
        "id": "RST-05",
        "requirement": "Bound output peaks and timing.",
        "status": "blocked",
        "evidence": (
            "No output samples and no runtime measurement exist, so no peak "
            "or timing bound can be reported."),
    },
)

DEEP_PLC_MEASUREMENT_ROWS = (
    {
        "id": "MR-01",
        "metric": "explicit_missing_packet_events",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No corpus or loss trace exists; no missing-packet event was "
            "observed, counted or reported to a decoder."),
    },
    {
        "id": "MR-02",
        "metric": "concealed_interval_samples",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No decoder and no explicit missing event exist, so no concealed "
            "interval or sample count was produced."),
    },
    {
        "id": "MR-03",
        "metric": "output_peak_q15",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No output samples exist, so no output-peak bound was measured."),
    },
    {
        "id": "MR-04",
        "metric": "content_and_availability_delay_samples",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No aligned output or paced stream exists, so no content or "
            "availability delay was measured."),
    },
    {
        "id": "MR-05",
        "metric": "deep_plc_vs_standard_plc_quality",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No paired deep-PLC and standard-PLC run exists, so no "
            "task-specific quality comparison was produced."),
    },
)

EXPLICIT_MISSING_EVENT_POLICY = {
    "policy": "explicit_missing_packet_events_only",
    "inferred_loss_from_sequence_gaps": False,
    "missing_packet_without_event": "rejected",
    "event_reported_to_decoder_required": True,
    "event_count_observed": None,
    "events_recorded": False,
    "concealment_intervals_recorded": False,
    "status": "blocked",
}

NON_CLAIMS = (
    "No Opus, libopus, deep-PLC decoder, neural PLC model, weight or vendor "
    "result is present, linked or executed.",
    "No genuine packet corpus, explicit missing-packet event trace, packet "
    "capture, clean reference, real corpus or media file is present or read.",
    "No deep-PLC implementation, approximation, substitute or comparison is "
    "shipped; no zero-fill, hold, linear, pitch-repeat, autoregressive, Opus "
    "1.4 standard PLC or generic model result stands in for deep PLC.",
    "No missing-packet-event, concealment-interval, quality, intelligibility, "
    "naturalness, speech-preservation, listening, delay, device-timing, "
    "benchmark or release result is produced.",
    "No provider is registered, exposed, enabled by default or selected as a "
    "descriptor default; no public API, ABI, registry, shared build or CI "
    "change is made.",
    "No Opus 1.4 standard decoder PLC, Opus DRED, LACE, NoLACE or "
    "packetization result is reused, pooled or reinterpreted as deep-PLC "
    "evidence.",
    "No missing, synthetic or schema-control result is promoted or treated as "
    "evidence for the candidate.",
)

PROFILE_PHRASES = (
    "Freeze corruption, metadata and corresponding clean/audio packet "
    "baseline.",
    "Stratify by degradation, erasure burst and bandwidth.",
    "Report discrete concealment/validity, decoded intervals, task-specific "
    "quality and bounds on output peaks and timing.",
)

# Admission manifest is a task-local schema, not an SDK or Opus contract.
MANIFEST_SCHEMA_ID = "audio-sdk/opus-deep-plc-cohort/0.1"
MANIFEST_FIELDS = (
    "schema_id",
    "cohort_id",
    "source_revision",
    "source_sha256",
    "source_path",
    "license_path",
    "license_sha256",
    "runtime_path",
    "runtime_sha256",
    "deep_plc_api",
    "restoration",
    "clean_reference",
    "strata",
    "missing_events",
    "packets",
    "concealment_outputs",
    "score_protocol",
)
DEEP_PLC_API_FIELDS = (
    "selector_name",
    "selector_value",
    "default_state",
    "decoder_symbol",
    "source_path",
    "source_sha256",
)
RESTORATION_FIELDS = (
    "corpus_path",
    "corpus_sha256",
    "rights_reference",
    "codec",
    "codec_version",
    "sample_rate_hz",
    "channels",
    "packet_duration_us",
    "bitrate_bps",
    "concealment_mode",
    "loss_trace_sha256",
    "expected_delay_samples",
    "baseline_control",
)
CLEAN_REFERENCE_FIELDS = ("path", "sha256", "alignment", "offset_samples")
STRATUM_FIELDS = ("id", "degradation", "bandwidth_hz", "burst_packets")
MISSING_EVENT_FIELDS = ("event_id", "first_packet_index", "packet_count",
                        "cause", "detected_by", "reported_to_decoder")
PACKET_FIELDS = ("index", "status", "valid_samples", "produced_samples",
                 "payload_bytes", "payload_sha256", "missing_event_id")
OUTPUT_FIELDS = ("event_id", "concealed_samples", "valid_samples", "peak_q15")
SCORE_PROTOCOL_FIELDS = ("metrics", "control", "paired_clean_reference",
                         "minimum_items")
PACKET_STATUSES = ("received", "missing")
DEGRADATIONS = ("packet_loss", "burst_loss", "low_bitrate", "mixed")
ALIGNMENTS = ("sample_exact", "declared_offset")
CONCEALMENT_MODES = ("deep_plc", "standard_plc_control")
BASELINE_CONTROLS = ("standard_plc", "no_concealment")
DEFAULT_STATES = ("disabled", "enabled")
EVENT_CAUSES = ("network_loss", "late_arrival", "corrupt_payload")
EVENT_DETECTORS = ("sequence_gap", "rtp_marker", "explicit_trace")
METRICS = ("si_sdr", "stoi", "rmse")
SDK_SAMPLE_RATE = 16000
SDK_CHANNELS = 1
MAX_PACKETS = 100000
MIN_PACKET_US = 2500
MAX_PACKET_US = 120000
MIN_BITRATE_BPS = 6000
MAX_BITRATE_BPS = 512000
MAX_DELAY_SAMPLES = 96000
MAX_BANDWIDTH_HZ = 16000
MAX_BURST_PACKETS = 1000
MAX_FRAME_SAMPLES = 1920
MAX_PACKET_BYTES = 65535
MAX_SELECTOR_VALUE = 65535
MAX_MINIMUM_ITEMS = 10000
MAX_RIGHTS_REFERENCE = 200
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
CODEC_VERSION = re.compile(r"^1\.(5|6)(\.[0-9]+){0,2}$")


# --------------------------------------------------------------------------
# Strict JSON and digests
# --------------------------------------------------------------------------
def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
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


def canonical_text(document: Any) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False) + "\n"


def canonical_bytes(document: Any) -> bytes:
    return canonical_text(document).encode("utf-8")


def object_digest(document: Any) -> str:
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
        path = root / relative
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
    return {field: rows[0].get(field) for field in BOARD_ROW_FIELDS}


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows_digest(rows: tuple[dict, ...] = LINKED_ROWS) -> str:
    return object_digest([{field: row.get(field) for field in BOARD_ROW_FIELDS}
                          for row in rows])


def absence_probes(audio_root: Path, probes: tuple[str, ...] = ABSENCE_PROBES,
                   worktree: Path | None = None) -> list[dict]:
    """Return the fixed probe inventory; any present path blocks shipping."""
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
# Admission validator (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _reject(code: str, field: str = "") -> dict:
    return {"accepted": False, "code": code, "field": field,
            "checks": 0, "state_unchanged": True}


def _accept(checks: int) -> dict:
    return {"accepted": True, "code": "ok", "field": "", "checks": checks,
            "state_unchanged": True}


def _nonfinite_path(value: Any, path: str = "") -> str | None:
    if isinstance(value, float) and not math.isfinite(value):
        return path or "<root>"
    if isinstance(value, dict):
        for key in sorted(value):
            found = _nonfinite_path(value[key],
                                    (path + "." + str(key)).lstrip("."))
            if found:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = _nonfinite_path(item, f"{path}[{index}]")
            if found:
                return found
    return None


def _path_is_canonical(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    if not os.path.isabs(value):
        return False
    if ".." in Path(value).parts or "~" in value:
        return False
    return os.path.normpath(value) == value


def _exact_object(value: Any, fields: tuple[str, ...]) -> str:
    if not isinstance(value, dict):
        return "invalid_object"
    if set(value) != set(fields):
        return ("missing_field" if set(fields) - set(value)
                else "unknown_field")
    return ""


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and HEX64.match(value) is not None


def _samples_per_packet(packet_duration_us: int) -> int:
    return packet_duration_us * SDK_SAMPLE_RATE // 1_000_000


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed cohort admission. No audio is read and no decoder runs."""
    checks = 0
    nonfinite = _nonfinite_path(document)
    if nonfinite:
        return _reject("nonfinite_value", nonfinite)
    if not isinstance(document, dict):
        return _reject("manifest_not_object")

    if set(document) != set(MANIFEST_FIELDS):
        missing = sorted(set(MANIFEST_FIELDS) - set(document))
        extra = sorted(set(document) - set(MANIFEST_FIELDS))
        return _reject("missing_field" if missing else "unknown_field",
                       missing[0] if missing else extra[0])
    checks += 1

    if document["schema_id"] != MANIFEST_SCHEMA_ID:
        return _reject("invalid_schema", "schema_id")
    if not isinstance(document["cohort_id"], str) \
            or not SLUG.match(document["cohort_id"]):
        return _reject("invalid_value", "cohort_id")
    if not isinstance(document["source_revision"], str) \
            or not HEX40.match(document["source_revision"]):
        return _reject("invalid_value", "source_revision")
    for field in ("source_sha256", "license_sha256", "runtime_sha256"):
        if not _is_sha(document[field]):
            return _reject("invalid_value", field)
    for field in ("source_path", "license_path", "runtime_path"):
        if not _path_is_canonical(document[field]):
            return _reject("invalid_path", field)
    checks += 7

    api = document["deep_plc_api"]
    code = _exact_object(api, DEEP_PLC_API_FIELDS)
    if code:
        return _reject(code, "deep_plc_api")
    if not isinstance(api["selector_name"], str) \
            or not SLUG.match(api["selector_name"]):
        return _reject("invalid_value", "deep_plc_api.selector_name")
    if not _is_int(api["selector_value"]) \
            or not 0 <= api["selector_value"] <= MAX_SELECTOR_VALUE:
        return _reject("invalid_value", "deep_plc_api.selector_value")
    if api["default_state"] not in DEFAULT_STATES:
        return _reject("invalid_value", "deep_plc_api.default_state")
    if not isinstance(api["decoder_symbol"], str) \
            or not SLUG.match(api["decoder_symbol"]):
        return _reject("invalid_value", "deep_plc_api.decoder_symbol")
    if not _path_is_canonical(api["source_path"]):
        return _reject("invalid_path", "deep_plc_api.source_path")
    if not _is_sha(api["source_sha256"]):
        return _reject("invalid_value", "deep_plc_api.source_sha256")
    checks += 6

    restoration = document["restoration"]
    code = _exact_object(restoration, RESTORATION_FIELDS)
    if code:
        return _reject(code, "restoration")
    if not _path_is_canonical(restoration["corpus_path"]):
        return _reject("invalid_path", "restoration.corpus_path")
    if not _is_sha(restoration["corpus_sha256"]):
        return _reject("invalid_value", "restoration.corpus_sha256")
    rights = restoration["rights_reference"]
    if not isinstance(rights, str) or not rights.strip() \
            or len(rights) > MAX_RIGHTS_REFERENCE \
            or any(ord(char) < 32 for char in rights):
        return _reject("invalid_value", "restoration.rights_reference")
    if restoration["codec"] != "opus":
        return _reject("invalid_value", "restoration.codec")
    if not isinstance(restoration["codec_version"], str) \
            or not CODEC_VERSION.match(restoration["codec_version"]):
        return _reject("invalid_value", "restoration.codec_version")
    if not _is_int(restoration["sample_rate_hz"]) \
            or restoration["sample_rate_hz"] != SDK_SAMPLE_RATE:
        return _reject("invalid_value", "restoration.sample_rate_hz")
    if not _is_int(restoration["channels"]) \
            or restoration["channels"] != SDK_CHANNELS:
        return _reject("invalid_value", "restoration.channels")
    duration = restoration["packet_duration_us"]
    if not _is_int(duration) or not MIN_PACKET_US <= duration <= MAX_PACKET_US \
            or duration % 250:
        return _reject("invalid_value", "restoration.packet_duration_us")
    if not _is_int(restoration["bitrate_bps"]) \
            or not MIN_BITRATE_BPS <= restoration["bitrate_bps"] \
            <= MAX_BITRATE_BPS:
        return _reject("invalid_value", "restoration.bitrate_bps")
    if restoration["concealment_mode"] not in CONCEALMENT_MODES:
        return _reject("invalid_value", "restoration.concealment_mode")
    if not _is_sha(restoration["loss_trace_sha256"]):
        return _reject("invalid_value", "restoration.loss_trace_sha256")
    if not _is_int(restoration["expected_delay_samples"]) \
            or not 0 <= restoration["expected_delay_samples"] \
            <= MAX_DELAY_SAMPLES:
        return _reject("invalid_value", "restoration.expected_delay_samples")
    if restoration["baseline_control"] not in BASELINE_CONTROLS:
        return _reject("invalid_value", "restoration.baseline_control")
    checks += 12

    clean = document["clean_reference"]
    code = _exact_object(clean, CLEAN_REFERENCE_FIELDS)
    if code:
        return _reject(code, "clean_reference")
    if not _path_is_canonical(clean["path"]):
        return _reject("invalid_path", "clean_reference.path")
    if not _is_sha(clean["sha256"]):
        return _reject("invalid_value", "clean_reference.sha256")
    if clean["alignment"] not in ALIGNMENTS:
        return _reject("invalid_value", "clean_reference.alignment")
    if not _is_int(clean["offset_samples"]) or clean["offset_samples"] < 0:
        return _reject("invalid_value", "clean_reference.offset_samples")
    if clean["alignment"] == "sample_exact" and clean["offset_samples"] != 0:
        return _reject("invalid_value", "clean_reference.offset_samples")
    checks += 5

    strata = document["strata"]
    if not isinstance(strata, list) or not strata:
        return _reject("invalid_value", "strata")
    seen_ids: set[str] = set()
    for stratum in strata:
        code = _exact_object(stratum, STRATUM_FIELDS)
        if code:
            return _reject(code, "strata")
        if not isinstance(stratum["id"], str) \
                or not SLUG.match(stratum["id"]):
            return _reject("invalid_value", "strata.id")
        if stratum["id"] in seen_ids:
            return _reject("invalid_value", "strata.id")
        seen_ids.add(stratum["id"])
        if stratum["degradation"] not in DEGRADATIONS:
            return _reject("invalid_value", "strata.degradation")
        if not _is_int(stratum["bandwidth_hz"]) \
                or not 0 <= stratum["bandwidth_hz"] <= MAX_BANDWIDTH_HZ:
            return _reject("invalid_value", "strata.bandwidth_hz")
        if not _is_int(stratum["burst_packets"]) \
                or not 0 <= stratum["burst_packets"] <= MAX_BURST_PACKETS:
            return _reject("invalid_value", "strata.burst_packets")
    checks += len(strata) * 4

    packet_samples = _samples_per_packet(duration)
    if not 1 <= packet_samples <= MAX_FRAME_SAMPLES:
        return _reject("invalid_value", "restoration.packet_duration_us")

    packets = document["packets"]
    if not isinstance(packets, list) or not packets:
        return _reject("invalid_value", "packets")
    if len(packets) > MAX_PACKETS:
        return _reject("invalid_value", "packets")
    received = 0
    missing_indices: list[int] = []
    packet_events: dict[int, str] = {}
    for index, packet in enumerate(packets):
        code = _exact_object(packet, PACKET_FIELDS)
        if code:
            return _reject(code, "packets")
        if not _is_int(packet["index"]) or packet["index"] != index:
            return _reject("invalid_value", "packets.index")
        if packet["status"] not in PACKET_STATUSES:
            return _reject("invalid_value", "packets.status")
        for field in ("valid_samples", "produced_samples", "payload_bytes"):
            if not _is_int(packet[field]) or packet[field] < 0:
                return _reject("invalid_value", "packets." + field)
        if packet["valid_samples"] > MAX_FRAME_SAMPLES \
                or packet["produced_samples"] > MAX_FRAME_SAMPLES:
            return _reject("invalid_value", "packets.samples")
        if packet["payload_bytes"] > MAX_PACKET_BYTES:
            return _reject("invalid_value", "packets.payload_bytes")
        if not _is_sha(packet["payload_sha256"]):
            return _reject("invalid_value", "packets.payload_sha256")
        if not isinstance(packet["missing_event_id"], str):
            return _reject("invalid_value", "packets.missing_event_id")
        status = packet["status"]
        if status == "received":
            received += 1
            if packet["valid_samples"] != packet_samples \
                    or packet["produced_samples"] != packet_samples \
                    or packet["payload_bytes"] <= 0 \
                    or packet["payload_sha256"] == EMPTY_SHA256 \
                    or packet["missing_event_id"] != "":
                return _reject("invalid_value", "packets.received")
        else:
            missing_indices.append(index)
            packet_events[index] = packet["missing_event_id"]
            if packet["valid_samples"] != 0 \
                    or packet["produced_samples"] != 0 \
                    or packet["payload_bytes"] != 0 \
                    or packet["payload_sha256"] != EMPTY_SHA256 \
                    or not SLUG.match(packet["missing_event_id"]):
                return _reject("invalid_value", "packets.missing")
    if received == 0:
        return _reject("invalid_value", "packets.received")
    if not missing_indices:
        return _reject("invalid_value", "packets.missing")
    checks += len(packets) * 8

    events = document["missing_events"]
    if not isinstance(events, list) or not events:
        return _reject("invalid_value", "missing_events")
    event_ids: list[str] = []
    covered: dict[int, str] = {}
    previous_end = -1
    for event in events:
        code = _exact_object(event, MISSING_EVENT_FIELDS)
        if code:
            return _reject(code, "missing_events")
        if not isinstance(event["event_id"], str) \
                or not SLUG.match(event["event_id"]):
            return _reject("invalid_value", "missing_events.event_id")
        if event["event_id"] in event_ids:
            return _reject("invalid_value", "missing_events.event_id")
        event_ids.append(event["event_id"])
        first = event["first_packet_index"]
        count = event["packet_count"]
        if not _is_int(first) or not _is_int(count) \
                or first < 0 or not 1 <= count <= MAX_BURST_PACKETS:
            return _reject("invalid_value", "missing_events.range")
        if first <= previous_end:
            return _reject("invalid_value", "missing_events.order")
        if first + count > len(packets):
            return _reject("invalid_value", "missing_events.range")
        previous_end = first + count - 1
        if event["cause"] not in EVENT_CAUSES:
            return _reject("invalid_value", "missing_events.cause")
        if event["detected_by"] not in EVENT_DETECTORS:
            return _reject("invalid_value", "missing_events.detected_by")
        if event["reported_to_decoder"] is not True:
            return _reject("invalid_value",
                           "missing_events.reported_to_decoder")
        for position in range(first, first + count):
            if position in covered:
                return _reject("invalid_value", "missing_events.overlap")
            covered[position] = event["event_id"]
    if sorted(covered) != missing_indices:
        return _reject("invalid_value", "missing_events.coverage")
    for position, event_id in covered.items():
        if packet_events.get(position) != event_id:
            return _reject("invalid_value", "missing_events.coverage")
    checks += len(events) * 7

    outputs = document["concealment_outputs"]
    if not isinstance(outputs, list) or len(outputs) != len(events):
        return _reject("invalid_value", "concealment_outputs")
    for event, output in zip(events, outputs):
        code = _exact_object(output, OUTPUT_FIELDS)
        if code:
            return _reject(code, "concealment_outputs")
        if output["event_id"] != event["event_id"]:
            return _reject("invalid_value", "concealment_outputs.event_id")
        if not _is_int(output["concealed_samples"]) \
                or output["concealed_samples"] != \
                event["packet_count"] * packet_samples:
            return _reject("invalid_value",
                           "concealment_outputs.concealed_samples")
        if not _is_int(output["valid_samples"]) \
                or output["valid_samples"] != 0:
            return _reject("invalid_value",
                           "concealment_outputs.valid_samples")
        if not _is_int(output["peak_q15"]) \
                or not 0 <= output["peak_q15"] <= 32767:
            return _reject("invalid_value", "concealment_outputs.peak_q15")
    checks += len(outputs) * 4

    score = document["score_protocol"]
    code = _exact_object(score, SCORE_PROTOCOL_FIELDS)
    if code:
        return _reject(code, "score_protocol")
    metrics = score["metrics"]
    if not isinstance(metrics, list) or not metrics:
        return _reject("invalid_value", "score_protocol.metrics")
    if any(metric not in METRICS for metric in metrics):
        return _reject("invalid_value", "score_protocol.metrics")
    if len(set(metrics)) != len(metrics):
        return _reject("invalid_value", "score_protocol.metrics")
    if score["control"] != "standard_plc":
        return _reject("invalid_value", "score_protocol.control")
    if score["paired_clean_reference"] is not True:
        return _reject("invalid_value",
                       "score_protocol.paired_clean_reference")
    if not _is_int(score["minimum_items"]) \
            or not 1 <= score["minimum_items"] <= MAX_MINIMUM_ITEMS:
        return _reject("invalid_value", "score_protocol.minimum_items")
    checks += 5

    if probe_paths:
        probes = (
            ("source_path", "source_sha256"),
            ("license_path", "license_sha256"),
            ("runtime_path", "runtime_sha256"),
        )
        for path_field, digest_field in probes:
            path = Path(document[path_field])
            if not path.is_file():
                return _reject("probe_missing", path_field)
            if sha256_file(path) != document[digest_field]:
                return _reject("probe_digest_mismatch", path_field)
        option_path = Path(api["source_path"])
        if not option_path.is_file():
            return _reject("probe_missing", "deep_plc_api.source_path")
        if sha256_file(option_path) != api["source_sha256"]:
            return _reject("probe_digest_mismatch",
                           "deep_plc_api.source_path")
        corpus_path = Path(restoration["corpus_path"])
        if not corpus_path.is_file():
            return _reject("probe_missing", "restoration.corpus_path")
        if sha256_file(corpus_path) != restoration["corpus_sha256"]:
            return _reject("probe_digest_mismatch", "restoration.corpus_path")
        clean_path = Path(clean["path"])
        if not clean_path.is_file():
            return _reject("probe_missing", "clean_reference.path")
        if sha256_file(clean_path) != clean["sha256"]:
            return _reject("probe_digest_mismatch", "clean_reference.path")
        checks += 7
    return _accept(checks)


def _manifest_control() -> dict:
    """Structural schema control. It is not evidence and never qualifies."""
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "schema_control",
        "source_revision": "0" * 40,
        "source_sha256": "0" * 64,
        "source_path": "/caller/opus-deep-plc-source",
        "license_path": "/caller/opus-deep-plc-source/COPYING",
        "license_sha256": "1" * 64,
        "runtime_path": "/caller/lib/libopus.dylib",
        "runtime_sha256": "2" * 64,
        "deep_plc_api": {
            "selector_name": "set_deep_plc",
            "selector_value": 1,
            "default_state": "disabled",
            "decoder_symbol": "opus_decode_float",
            "source_path": "/caller/opus-deep-plc-source/src/opus_decoder.c",
            "source_sha256": "3" * 64,
        },
        "restoration": {
            "corpus_path": "/caller/cohort/packets-16k",
            "corpus_sha256": "4" * 64,
            "rights_reference": "synthetic-schema-control-no-rights",
            "codec": "opus",
            "codec_version": "1.5.2",
            "sample_rate_hz": 16000,
            "channels": 1,
            "packet_duration_us": 20000,
            "bitrate_bps": 24000,
            "concealment_mode": "deep_plc",
            "loss_trace_sha256": "5" * 64,
            "expected_delay_samples": 0,
            "baseline_control": "standard_plc",
        },
        "clean_reference": {
            "path": "/caller/cohort/clean-16k",
            "sha256": "6" * 64,
            "alignment": "sample_exact",
            "offset_samples": 0,
        },
        "strata": [
            {"id": "s1", "degradation": "packet_loss",
             "bandwidth_hz": 16000, "burst_packets": 1},
            {"id": "s2", "degradation": "burst_loss",
             "bandwidth_hz": 16000, "burst_packets": 2},
        ],
        "missing_events": [
            {"event_id": "e1", "first_packet_index": 2, "packet_count": 1,
             "cause": "network_loss", "detected_by": "explicit_trace",
             "reported_to_decoder": True},
            {"event_id": "e2", "first_packet_index": 4, "packet_count": 2,
             "cause": "network_loss", "detected_by": "explicit_trace",
             "reported_to_decoder": True},
        ],
        "packets": [
            {"index": 0, "status": "received", "valid_samples": 320,
             "produced_samples": 320, "payload_bytes": 120,
             "payload_sha256": "7" * 64, "missing_event_id": ""},
            {"index": 1, "status": "received", "valid_samples": 320,
             "produced_samples": 320, "payload_bytes": 120,
             "payload_sha256": "8" * 64, "missing_event_id": ""},
            {"index": 2, "status": "missing", "valid_samples": 0,
             "produced_samples": 0, "payload_bytes": 0,
             "payload_sha256": EMPTY_SHA256, "missing_event_id": "e1"},
            {"index": 3, "status": "received", "valid_samples": 320,
             "produced_samples": 320, "payload_bytes": 120,
             "payload_sha256": "9" * 64, "missing_event_id": ""},
            {"index": 4, "status": "missing", "valid_samples": 0,
             "produced_samples": 0, "payload_bytes": 0,
             "payload_sha256": EMPTY_SHA256, "missing_event_id": "e2"},
            {"index": 5, "status": "missing", "valid_samples": 0,
             "produced_samples": 0, "payload_bytes": 0,
             "payload_sha256": EMPTY_SHA256, "missing_event_id": "e2"},
        ],
        "concealment_outputs": [
            {"event_id": "e1", "concealed_samples": 320,
             "valid_samples": 0, "peak_q15": 12000},
            {"event_id": "e2", "concealed_samples": 640,
             "valid_samples": 0, "peak_q15": 14000},
        ],
        "score_protocol": {
            "metrics": ["si_sdr", "stoi"],
            "control": "standard_plc",
            "paired_clean_reference": True,
            "minimum_items": 4,
        },
    }


def admission_controls() -> dict:
    """Build the frozen adverse matrix plus one structural schema control."""
    cases: list[dict] = []

    def manifest_case(case_id: str, mutate, kind: str = "manifest") -> None:
        document = _manifest_control()
        result = mutate(document)
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

    def drop(document, field):
        del document[field]
        return validate_manifest(document, probe_paths=False)

    def put(document, field, value):
        document[field] = value
        return validate_manifest(document, probe_paths=False)

    def nested(document, section, field, value):
        document[section][field] = value
        return validate_manifest(document, probe_paths=False)

    def packet_field(document, index, field, value):
        document["packets"][index][field] = value
        return validate_manifest(document, probe_paths=False)

    def event_field(document, index, field, value):
        document["missing_events"][index][field] = value
        return validate_manifest(document, probe_paths=False)

    def output_field(document, index, field, value):
        document["concealment_outputs"][index][field] = value
        return validate_manifest(document, probe_paths=False)

    def no_missing(document):
        for index, packet in enumerate(document["packets"]):
            packet["status"] = "received"
            packet["valid_samples"] = 320
            packet["produced_samples"] = 320
            packet["payload_bytes"] = 120
            packet["payload_sha256"] = f"{index:x}" * 64
            packet["missing_event_id"] = ""
        document["missing_events"] = []
        document["concealment_outputs"] = []
        return validate_manifest(document, probe_paths=False)

    cases.append({
        "id": "MISS-01", "kind": "manifest", "status": "rejected",
        "code": validate_manifest(None, probe_paths=False)["code"],
        "field": "", "state_unchanged": True, "qualifies": False,
        "evidence_class": "synthetic_admission_control"})
    manifest_case("INV-01", lambda doc: drop(doc, "source_sha256"))
    manifest_case("INV-02", lambda doc: put(doc, "extra", "value"))
    manifest_case("INV-03", lambda doc: put(doc, "schema_id", "wrong"))
    manifest_case("INV-04", lambda doc: put(doc, "cohort_id", "Bad Id"))
    manifest_case("INV-05", lambda doc: put(doc, "source_revision", "A" * 40))
    manifest_case("INV-06", lambda doc: put(doc, "source_sha256", "0" * 63))
    manifest_case("INV-07", lambda doc: put(doc, "source_path",
                                            "relative/src"))
    manifest_case("INV-08", lambda doc: put(doc, "license_path",
                                            "/caller/../COPYING"))
    manifest_case("INV-09", lambda doc: put(doc, "runtime_sha256", "x" * 64))
    manifest_case("INV-10", lambda doc: put(doc, "deep_plc_api", "deep"))
    manifest_case("INV-11", lambda doc: validate_manifest(
        _without_nested("deep_plc_api", "selector_name"),
        probe_paths=False))
    manifest_case("INV-12", lambda doc: nested(doc, "deep_plc_api",
                                               "selector_value", 1.5))
    manifest_case("INV-13", lambda doc: nested(doc, "deep_plc_api",
                                               "selector_value", True))
    manifest_case("INV-14", lambda doc: nested(doc, "deep_plc_api",
                                               "selector_value", -1))
    manifest_case("INV-15", lambda doc: nested(doc, "deep_plc_api",
                                               "default_state", "auto"))
    manifest_case("INV-16", lambda doc: nested(doc, "deep_plc_api",
                                               "decoder_symbol",
                                               "Bad Symbol"))
    manifest_case("INV-17", lambda doc: nested(doc, "deep_plc_api",
                                               "source_path",
                                               "/caller/\x00/src.c"))
    manifest_case("INV-18", lambda doc: put(doc, "restoration", "pcm"))
    manifest_case("INV-19", lambda doc: nested(doc, "restoration",
                                               "codec", "aac"))
    manifest_case("INV-20", lambda doc: nested(doc, "restoration",
                                               "codec_version", "1.4"))
    manifest_case("INV-21", lambda doc: nested(doc, "restoration",
                                               "sample_rate_hz", 48000))
    manifest_case("INV-22", lambda doc: nested(doc, "restoration",
                                               "channels", 2))
    manifest_case("INV-23", lambda doc: nested(doc, "restoration",
                                               "packet_duration_us", 0))
    manifest_case("INV-24", lambda doc: nested(doc, "restoration",
                                               "packet_duration_us", 12345))
    manifest_case("INV-25", lambda doc: nested(doc, "restoration",
                                               "bitrate_bps", 1000))
    manifest_case("INV-26", lambda doc: nested(doc, "restoration",
                                               "bitrate_bps", True))
    manifest_case("INV-27", lambda doc: nested(doc, "restoration",
                                               "bitrate_bps",
                                               float("nan")))
    manifest_case("INV-28", lambda doc: nested(doc, "restoration",
                                               "concealment_mode",
                                               "zero_fill"))
    manifest_case("INV-29", lambda doc: nested(doc, "restoration",
                                               "expected_delay_samples", -1))
    manifest_case("INV-30", lambda doc: nested(doc, "restoration",
                                               "expected_delay_samples",
                                               float("inf")))
    manifest_case("INV-31", lambda doc: nested(doc, "restoration",
                                               "baseline_control",
                                               "identity"))
    manifest_case("INV-32", lambda doc: nested(doc, "clean_reference",
                                               "alignment", "guess"))
    manifest_case("INV-33", lambda doc: nested(doc, "clean_reference",
                                               "offset_samples", 5))
    manifest_case("INV-34", lambda doc: put(doc, "strata", []))
    manifest_case("INV-35", lambda doc: put(
        doc, "strata", [dict(doc["strata"][0]), dict(doc["strata"][0])]))
    manifest_case("INV-36", lambda _doc: validate_manifest(
        _with_stratum("degradation", "clean"), probe_paths=False))
    manifest_case("INV-37", lambda _doc: validate_manifest(
        _with_stratum("bandwidth_hz", 24000), probe_paths=False))
    manifest_case("INV-38", lambda _doc: validate_manifest(
        _with_stratum("burst_packets", -1), probe_paths=False))
    manifest_case("INV-39", lambda doc: put(doc, "missing_events", []))
    manifest_case("INV-40", lambda doc: event_field(doc, 1, "event_id", "e1"))
    manifest_case("INV-41", lambda doc: event_field(
        doc, 0, "first_packet_index", -1))
    manifest_case("INV-42", lambda doc: event_field(
        doc, 0, "packet_count", 0))
    manifest_case("INV-43", lambda doc: event_field(
        doc, 0, "cause", "unknown"))
    manifest_case("INV-44", lambda doc: event_field(
        doc, 0, "detected_by", "guess"))
    manifest_case("INV-45", lambda doc: event_field(
        doc, 0, "reported_to_decoder", False))
    manifest_case("INV-46", lambda doc: event_field(
        doc, 0, "reported_to_decoder", 1))
    manifest_case("INV-47", lambda doc: event_field(
        doc, 0, "first_packet_index", 4))
    manifest_case("INV-48", lambda doc: event_field(
        doc, 1, "first_packet_index", 3))
    manifest_case("INV-49", lambda doc: event_field(
        doc, 0, "first_packet_index", 1))
    manifest_case("INV-50", lambda doc: packet_field(
        doc, 2, "missing_event_id", ""))
    manifest_case("INV-51", lambda doc: packet_field(
        doc, 2, "missing_event_id", "e9"))
    manifest_case("INV-52", lambda doc: packet_field(doc, 0, "index", 1))
    manifest_case("INV-53", lambda doc: packet_field(
        doc, 0, "valid_samples", 0))
    manifest_case("INV-54", lambda doc: packet_field(
        doc, 0, "produced_samples", 321))
    manifest_case("INV-55", lambda doc: packet_field(
        doc, 0, "payload_bytes", 0))
    manifest_case("INV-56", lambda doc: packet_field(
        doc, 0, "payload_sha256", EMPTY_SHA256))
    manifest_case("INV-57", lambda doc: packet_field(
        doc, 2, "valid_samples", 1))
    manifest_case("INV-58", lambda doc: packet_field(
        doc, 2, "payload_bytes", 1))
    manifest_case("INV-59", lambda doc: packet_field(
        doc, 2, "payload_sha256", "a" * 64))
    manifest_case("INV-60", lambda doc: packet_field(
        doc, 0, "payload_bytes", 99999))
    manifest_case("INV-61", lambda doc: packet_field(
        doc, 0, "valid_samples", 99999))
    manifest_case("INV-62", lambda doc: packet_field(
        doc, 0, "valid_samples", float("nan")))
    manifest_case("INV-63", lambda doc: put(doc, "packets", []))
    manifest_case("INV-64", lambda doc: no_missing(doc))
    manifest_case("INV-65", lambda doc: put(
        doc, "concealment_outputs", list(reversed(
            doc["concealment_outputs"]))))
    manifest_case("INV-66", lambda doc: output_field(
        doc, 0, "concealed_samples", 321))
    manifest_case("INV-67", lambda doc: output_field(
        doc, 0, "valid_samples", 1))
    manifest_case("INV-68", lambda doc: output_field(
        doc, 0, "peak_q15", 32768))
    manifest_case("INV-69", lambda doc: output_field(
        doc, 0, "event_id", "e2"))
    manifest_case("INV-70", lambda doc: put(doc, "score_protocol", "stoi"))
    manifest_case("INV-71", lambda doc: nested(doc, "score_protocol",
                                               "metrics", []))
    manifest_case("INV-72", lambda doc: nested(doc, "score_protocol",
                                               "metrics", ["stoi", "stoi"]))
    manifest_case("INV-73", lambda doc: nested(doc, "score_protocol",
                                               "metrics", ["mos"]))
    manifest_case("INV-74", lambda doc: nested(doc, "score_protocol",
                                               "control", "identity"))
    manifest_case("INV-75", lambda doc: nested(doc, "score_protocol",
                                               "paired_clean_reference",
                                               False))
    manifest_case("INV-76", lambda doc: nested(doc, "score_protocol",
                                               "minimum_items", 0))
    manifest_case("INV-77", lambda doc: put(doc, "runtime_path",
                                            "/caller/lib\x00/libopus.dylib"))
    manifest_case("INV-78", lambda doc: put(doc, "license_sha256", "A" * 64))
    manifest_case("INV-79", lambda doc: validate_manifest(
        _without_nested("restoration", "concealment_mode"),
        probe_paths=False))
    manifest_case("INV-80", lambda doc: validate_manifest(
        _without_nested("restoration", "loss_trace_sha256"),
        probe_paths=False))
    manifest_case("PRS-01", lambda doc: validate_manifest(doc,
                                                          probe_paths=True))

    for case_id, text, code in (
            ("JSON-01", '{"a":1,"a":2}', "duplicate_json_key:a"),
            ("JSON-02", '{"a":NaN}', "nonfinite_json_constant:NaN"),
            ("JSON-03", '{"a":Infinity}', "nonfinite_json_constant:Infinity"),
            ("JSON-04", '{"a":-Infinity}',
             "nonfinite_json_constant:-Infinity"),
            ("JSON-05", "[]", "json_root_not_object"),
            ("JSON-06", "\ufeff{}", "json_byte_order_mark")):
        try:
            loads_strict(text)
        except ValueError as error:
            message = str(error)
        else:  # pragma: no cover - the fixtures are malformed by design
            message = "accepted"
        cases.append({
            "id": case_id, "kind": "strict_json", "status": "rejected",
            "code": code, "field": "",
            "message_matches": message == code,
            "state_unchanged": True, "qualifies": False,
            "evidence_class": "synthetic_admission_control"})

    control = validate_manifest(_manifest_control(), probe_paths=False)
    if not control["accepted"]:
        raise ValueError("schema_control_rejected:" + control["code"])
    controls = [{
        "id": "CTL-01",
        "kind": "manifest",
        "status": "accepted_schema_control",
        "code": control["code"],
        "checks": control["checks"],
        "artifacts_probed": False,
        "runtime_loaded": False,
        "audio_read": False,
        "decoder_invoked": False,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "qualifies": False,
    }]
    return {"cases": cases, "controls": controls}


def _without_nested(section: str, field: str) -> dict:
    document = _manifest_control()
    del document[section][field]
    return document


def _with_stratum(field: str, value: Any) -> dict:
    document = _manifest_control()
    document["strata"][0][field] = value
    return document


# --------------------------------------------------------------------------
# Canonical contract and report
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
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
    }


def qualification_block() -> dict:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "all_release_gates_blocked": True,
        "real_source_present": False,
        "real_runtime_present": False,
        "real_deep_plc_model_present": False,
        "real_deep_plc_selector_verified": False,
        "real_packet_corpus_present": False,
        "real_missing_event_trace_present": False,
        "real_clean_baseline_present": False,
        "real_result_present": False,
        "deep_plc_implementation_result": False,
        "explicit_missing_event_result": False,
        "concealment_interval_result": False,
        "quality_result": False,
        "listening_result": False,
        "output_peak_bound": False,
        "delay_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "missing_result_promoted": False,
        "not_qualified": True,
    }


def disposition_block() -> dict:
    return {
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
        "default_enabled": False,
        "missing_result_qualifies": False,
    }


def boundary_block() -> dict:
    return {
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "shared_cmakelists_change": False,
        "ci_workflow_change": False,
        "installed_v0_behavior_change": False,
        "processor_exposure": False,
        "task_local_only": True,
        "files_outside_task_directory_written": False,
    }


def scope_block() -> dict:
    return {
        "source_present": False,
        "runtime_present": False,
        "runtime_executed": False,
        "codec_runtime_executed": False,
        "deep_plc_model_asset_present": False,
        "real_corpus": False,
        "real_packet_trace": False,
        "explicit_missing_events_present": False,
        "audio_read": False,
        "decoding_performed": False,
        "concealment_executed": False,
        "quality_scored": False,
        "listening": False,
        "device_timing": False,
        "output_peak_bound": False,
        "benchmark": False,
        "release_claim": False,
        "network_used": False,
        "download_attempted": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "preserved": True,
        "sdk_callback_invoked": False,
    }


def exact_scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "single_component": COMPONENT_ID,
        "provider_work": False,
        "runtime_work": False,
        "release_work": False,
        "write_scope": WRITE_SCOPE,
    }


def profile_source_block() -> dict:
    return {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "sha256": SOURCE_PINS[
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "row": "Restoration",
        "phrases": list(PROFILE_PHRASES),
    }


def admission_contract_block() -> dict:
    return {
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "manifest_schema_id": MANIFEST_SCHEMA_ID,
        "manifest_fields": list(MANIFEST_FIELDS),
        "deep_plc_api_fields": list(DEEP_PLC_API_FIELDS),
        "restoration_fields": list(RESTORATION_FIELDS),
        "clean_reference_fields": list(CLEAN_REFERENCE_FIELDS),
        "stratum_fields": list(STRATUM_FIELDS),
        "missing_event_fields": list(MISSING_EVENT_FIELDS),
        "packet_fields": list(PACKET_FIELDS),
        "output_fields": list(OUTPUT_FIELDS),
        "score_protocol_fields": list(SCORE_PROTOCOL_FIELDS),
        "packet_statuses": list(PACKET_STATUSES),
        "degradations": list(DEGRADATIONS),
        "alignments": list(ALIGNMENTS),
        "concealment_modes": list(CONCEALMENT_MODES),
        "baseline_controls": list(BASELINE_CONTROLS),
        "default_states": list(DEFAULT_STATES),
        "event_causes": list(EVENT_CAUSES),
        "event_detectors": list(EVENT_DETECTORS),
        "metrics": list(METRICS),
        "sdk_sample_rate_hz": SDK_SAMPLE_RATE,
        "sdk_channels": SDK_CHANNELS,
        "packet_duration_us_bounds": [MIN_PACKET_US, MAX_PACKET_US],
        "packet_duration_us_multiple": 250,
        "bitrate_bps_bounds": [MIN_BITRATE_BPS, MAX_BITRATE_BPS],
        "expected_delay_samples_bounds": [0, MAX_DELAY_SAMPLES],
        "selector_value_bounds": [0, MAX_SELECTOR_VALUE],
        "minimum_items_bounds": [1, MAX_MINIMUM_ITEMS],
        "max_packets": MAX_PACKETS,
        "max_bandwidth_hz": MAX_BANDWIDTH_HZ,
        "max_burst_packets": MAX_BURST_PACKETS,
        "max_frame_samples": MAX_FRAME_SAMPLES,
        "max_packet_bytes": MAX_PACKET_BYTES,
        "sdk_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
        },
        "empty_payload_sha256": EMPTY_SHA256,
        "loss_representation": "explicit_missing_packet_events",
        "inferred_loss_allowed": False,
        "event_reported_to_decoder_required": True,
        "audio_read": False,
        "runtime_invoked": False,
        "decoding_performed": False,
        "concealment_executed": False,
        "replay_performed": False,
    }


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "profile": PROFILE,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "worktree": CLAIM_WORKTREE,
        "write_scope": WRITE_SCOPE,
        "status": "incomplete",
        "decision": "DEFER",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_scope": exact_scope_block(),
        "qualification": qualification_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_row_fields": list(BOARD_ROW_FIELDS),
        "board_row_projection": dict(BOARD_ROW_PROJECTION),
        "board_row_sha256": board_row_digest(BOARD_ROW_PROJECTION),
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "absence_policy": {
            "fixed_probe_list_only": True,
            "recursive_workspace_walk": False,
            "download_attempted": False,
            "any_present_probe_blocks_shipping": True,
        },
        "absence_probes": list(ABSENCE_PROBES),
        "unqualified_runtime_observation": dict(UNQUALIFIED_RUNTIME),
        "required_artifacts": _artifact_rows(),
        "exact_blockers": _blocker_rows(),
        "release_gates": _gate_rows(),
        "admission_contract": admission_contract_block(),
        "explicit_missing_event_policy": dict(EXPLICIT_MISSING_EVENT_POLICY),
        "restoration_profile_requirements": [dict(row)
                                             for row in
                                             RESTORATION_PROFILE_ROWS],
        "deep_plc_measurement_requirements": [dict(row)
                                              for row in
                                              DEEP_PLC_MEASUREMENT_ROWS],
        "profile_source": profile_source_block(),
        "non_claims": list(NON_CLAIMS),
    }


def build_report() -> dict:
    contract = read_strict_json(HERE / "contract.json")
    probes = absence_probes(AUDIO_ROOT)
    controls = admission_controls()
    rejected = [case for case in controls["cases"]
                if case["status"] == "rejected"]
    accepted_controls = [case for case in controls["controls"]
                         if case["status"] == "accepted_schema_control"]
    gates = _gate_rows()
    artifacts = _artifact_rows()
    blockers = _blocker_rows()
    return {
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
        "decision": "DEFER",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_scope": exact_scope_block(),
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
            "observed_unqualified_binaries": [dict(UNQUALIFIED_RUNTIME)],
            "conclusion": (
                "No Opus source containing deep PLC, libopus deep-PLC "
                "runtime, deep-PLC model asset, selector, packet corpus with "
                "explicit missing-packet events, clean baseline or vendor "
                "result exists at any fixed probe location. One unqualified "
                "transitive PyAV-wheel dylib is recorded as provenance only "
                "and is never admitted."),
        },
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "restoration_profile": {
            "profile": PROFILE,
            "rows": [dict(row) for row in RESTORATION_PROFILE_ROWS],
            "corruption_frozen": False,
            "metadata_frozen": False,
            "clean_or_packet_baseline_frozen": False,
            "degradation_strata_present": False,
            "erasure_burst_strata_present": False,
            "bandwidth_strata_present": False,
            "discrete_concealment_validity_result": False,
            "decoded_interval_result": False,
            "task_specific_quality_result": False,
            "output_peak_bounds": False,
            "timing_bounds": False,
            "status": "blocked",
        },
        "deep_plc_measurements": {
            "rows": [dict(row) for row in DEEP_PLC_MEASUREMENT_ROWS],
            "explicit_missing_events_measured": False,
            "concealed_intervals_measured": False,
            "output_peak_measured": False,
            "delay_measured": False,
            "relative_quality_measured": False,
            "status": "blocked",
        },
        "explicit_missing_event_policy": dict(EXPLICIT_MISSING_EVENT_POLICY),
        "required_results": {
            "explicit_missing_event_result": False,
            "concealed_interval_result": False,
            "decoded_intervals_reported": False,
            "frame_accounting_complete": False,
            "output_peak_bound": False,
            "task_specific_quality": False,
            "standard_plc_control_result": False,
            "independent_listening": False,
            "delay_measured": False,
            "no_result_qualifies": True,
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
                "audio_read": False,
                "decoding_performed": False,
                "concealment_executed": False,
            },
        },
        "qualification": qualification_block(),
        "prohibited_claims": list(NON_CLAIMS),
        "gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "linked_row_identity": linked_row_identity(),
        "profile_source": profile_source_block(),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "regeneration": {
            "runs": 3,
            "byte_identical": True,
            "cold_start_processes": True,
            "canonical_json": True,
            "sorted_keys": True,
            "compact_separators": True,
            "trailing_newline": True,
        },
        "reproduction": {
            "tests": ("PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v "
                      "test_reference.py"),
            "report": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
        },
    }


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_id")
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
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification_status")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal_only")
    if contract.get("base_commit") != BASE_COMMIT:
        raise ValueError("contract_base_commit")
    if contract.get("branch") != BRANCH:
        raise ValueError("contract_branch")
    if contract.get("reviewer") != REVIEWER:
        raise ValueError("contract_reviewer")
    if contract.get("worktree") != CLAIM_WORKTREE:
        raise ValueError("contract_worktree")
    if len(contract.get("release_gates", [])) != 8:
        raise ValueError("contract_gate_count")
    if any(gate.get("status") != "blocked"
           for gate in contract["release_gates"]):
        raise ValueError("contract_gate_not_blocked")
    if contract.get("board_row_projection") != BOARD_ROW_PROJECTION:
        raise ValueError("contract_board_row_projection")
    if contract.get("board_row_sha256") != board_row_digest(
            BOARD_ROW_PROJECTION):
        raise ValueError("contract_board_row_digest")
    if contract.get("linked_rows") != [dict(row) for row in LINKED_ROWS]:
        raise ValueError("contract_linked_rows")
    for key, value in (("source_pins", SOURCE_PINS),
                       ("boundary_pins", BOUNDARY_PINS)):
        if contract.get(key) != value:
            raise ValueError("contract_pin_table:" + key)
