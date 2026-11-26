# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-AUDIOTK.

The exact licensed AudioTK source checkout, resolved revision, build record and
runtime are absent from this workspace.  The only merged evidence is one
pinned survey line that records AudioTK as a BSD-3-Clause general DSP/filter
toolkit, states that the pass did not identify a ready-made time-stretch stage,
and notes that it may still be useful for supporting DSP.

This module therefore never imports, builds, links or executes AudioTK, never
reads real audio or a corpus, never downloads anything and never measures a
device clock.  It provides three bounded, verifiable pieces:

* a fail-closed source/asset/revision audit over fixed workspace paths plus an
  explicit supporting-DSP reuse audit that keeps existing SDK DSP and merged
  sibling rate evidence separate from AudioTK;
* a caller-supplied-asset manifest contract validated without execution, with
  every malformed, missing, invalid or nonfinite control rejected before use;
* a deterministic synthetic rate-accounting control that checks exact
  source/output interval mapping, duration arithmetic, scalar rate values,
  final-partial-window accounting, source-anchored pause/filler intervals,
  1x identity mapping and PCM validity without performing any time-scale
  modification or pitch processing.

Nothing in this package qualifies the candidate.  The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-AUDIOTK"
TITLE = "AudioTK"
SLUG = "audiotk"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "d7f51ea0800508ee36c4ea1a90e07f3127bf1e02"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
MODE = "research-control"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_provider_intake"

# Exact upstream identity recorded by the merged survey evidence.  The survey
# records the name, the reported BSD-3-Clause licence and the absence of a
# ready-made time-stretch stage.  It records no repository URL, resolved
# 40-hex revision, artifact hash or build record, so none is invented here.
UPSTREAM_NAME = "AudioTK"
UPSTREAM_REPOSITORY_URL: Optional[str] = None
UPSTREAM_PROJECT_URL: Optional[str] = None
UPSTREAM_REVISION: Optional[str] = None
SOURCE_REVISION_PIN_AVAILABLE = False
RECORDED_LICENSE = "BSD-3-Clause"
RECORDED_ROLE = "supporting_dsp_only"
RECORDED_TIME_STRETCH_STAGE_FOUND = False
RECORDED_HARDWARE = "not_recorded_in_merged_evidence"
TASK_GEOMETRY_STATUS = "unestablished"
EVIDENCE_SOURCE = "cpp-library/pipeline-validation/playback-speed-candidates.md"
EVIDENCE_LINE = 279

# Control geometry is the public SDK v0 input boundary.  It is not asserted
# AudioTK geometry and AudioTK is not used to produce any control sample.
CONTROL_SAMPLE_RATE_HZ = 16000
CONTROL_CHANNELS = 1
SDK_FRAME_SAMPLES = 160
OUTPUT_QUEUE_CAPACITY = 3
CONTROL_SECONDS = 3
CONTROL_SOURCE_SAMPLES = CONTROL_SAMPLE_RATE_HZ * CONTROL_SECONDS
CONTROL_TAIL_VALID_SAMPLES = 37
CONTROL_TAIL_PADDED_SAMPLES = SDK_FRAME_SAMPLES
CONTROL_TAIL_PADDING_SAMPLES = (
    CONTROL_TAIL_PADDED_SAMPLES - CONTROL_TAIL_VALID_SAMPLES)
PCM_SAMPLE_CAP = 5_000_000
MAX_MANIFEST_BYTES = 8 * 1024 ** 3
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
CANONICAL_DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?$")
MIN_RATE = Fraction(1, 2)
MAX_RATE = Fraction(2, 1)

# Fixed workspace paths used for the audit.  Absence is recorded, not filled.
RIGHTS_RECORD_PATH = "data/rights/audiotk-rights.json"
COHORT_MANIFEST_PATH = "data/runs/audiotk-rate-cohort/manifest.json"
PARITY_MANIFEST_PATH = "data/runs/audiotk-parity/manifest.json"
BUILD_RECORD_PATH = "data/build-records/audiotk.json"
RUNTIME_ENV_PATH = "data/envs/audiotk"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
SUPPORTING_DSP_PLAN_PATH = "data/plans/audiotk-supporting-dsp.json"
MISSING_SOURCE_PATH = "research/repos/audiotk"
MISSING_CHECKOUT_PATH = "data/checkouts/audiotk"

# Fixed absence probes.  Every probe must stay absent; any appearance forces a
# re-evaluation instead of silently promoting the candidate.
ABSENCE_PROBES: Tuple[str, ...] = (
    "research/repos/audiotk",
    "research/repos/AudioTK",
    "research/repos/audio-tk",
    "research/voice-enhancement-20261101/repos/audiotk",
    "research/voice-enhancement-20261101/repos/AudioTK",
    "data/checkouts/audiotk",
    "data/checkouts/AudioTK",
    "third_party/audiotk",
    "third_party/AudioTK",
    "third_party/audio-tk",
    "deps/audiotk",
    "deps/AudioTK",
    "data/models/audiotk",
    "data/envs/audiotk",
    "data/envs/audiotk/requirements.lock",
    "data/rights/audiotk-rights.json",
    "data/build-records/audiotk.json",
    "data/plans/audiotk-supporting-dsp.json",
    "data/runs/audiotk-rate-cohort/manifest.json",
    "data/runs/audiotk-parity/manifest.json",
)

STABLE_TASK_FIELDS = (
    "acceptance",
    "component",
    "deliverable",
    "depends_on",
    "evidence",
    "id",
    "mode",
    "repository",
    "title",
    "write_scope",
)
MUTABLE_TASK_FIELDS = (
    "blocked_reason",
    "dispatch_priority",
    "handoff",
    "owner",
    "review",
    "status",
)

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/audio-sdk/PIPELINES.md":
        "4d950978277dff9c562059d25d43ad5d2a85a46bb7a97aabb8518edaa0faea47",
    "audio-benchmark-platform/audio-sdk/README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "audio-benchmark-platform/audio-sdk/RELEASING.md":
        "67e996fc8b1e4bc3e1e90b6bf8e60a98287a9f64177eda2c409f15187a9c65d3",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "core/providers/highpass/highpass_provider.c":
        "051b423d078835ff1ab23d7303c8e0c8f876d3d4211339682f366797ef7fffef",
    "core/providers/speex/speex_provider.c":
        "d1a98e3aff897375db4f0fc7668329be5254faa361ccaba1635a5089ea8a71e6",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/aubio/README.md":
        "700153d2541f9f4836e878fd6bfec631b644d1bf55ab0868e03f880858bd5e1d",
    "docs/task-evidence/bungee-basic/README.md":
        "ee6edcc68764888500aed41963169e6e311cec447b511fcbd1f2d4189453d485",
    "docs/task-evidence/signalsmith-stretch/README.md":
        "446398e0c3aa27528e5ceacf1d4d0b6102f8c8e541c76aa6ac2a8abe62691934",
    "docs/task-evidence/sonic/README.md":
        "40f2fdcf708a75fbc3e0df296fabfecd296118e6a9eaee67fc34f8dec0e419cb",
    "docs/task-evidence/soundtouch/README.md":
        "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
}
LOCAL_PIN_PATHS = (
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
)

# Existing SDK DSP surface read by the supporting-DSP reuse audit.  Presence is
# recorded with a digest; nothing is compiled or executed.
EXISTING_DSP_FILES: Tuple[str, ...] = (
    "core/providers/highpass/highpass_provider.c",
    "core/providers/highpass/config/config.json",
    "core/providers/speex/speex_provider.c",
    "core/providers/speex/config/config.json",
    "third_party/speexdsp/COPYING",
    "docs/provider-intake.md",
    "docs/provider-v0.md",
)
SIBLING_RATE_PACKAGES: Tuple[str, ...] = (
    "docs/task-evidence/aubio/README.md",
    "docs/task-evidence/bungee-basic/README.md",
    "docs/task-evidence/signalsmith-stretch/README.md",
    "docs/task-evidence/sonic/README.md",
    "docs/task-evidence/soundtouch/README.md",
)

BOUNDARY_FALSE_FLAGS: Tuple[str, ...] = (
    "abi_change",
    "adapter_json_added",
    "asset_bundled",
    "audiotk_compiled",
    "audiotk_linked",
    "ci_change",
    "default_selected",
    "descriptor_registry_change",
    "enabled_by_default",
    "installed_v0_behavior_change",
    "network_used",
    "processor_exposure",
    "production_callback_registered",
    "provider_registration",
    "public_api_abi_change",
    "registered",
    "sdk_callback_invoked",
    "shared_build_or_ci_change",
    "time_stretch_enabled",
    "weights_vendored",
)
BOUNDARY: Dict[str, Any] = {flag: False for flag in BOUNDARY_FALSE_FLAGS}
BOUNDARY["descriptor_settings"] = {}

SCOPE_FALSE_FLAGS: Tuple[str, ...] = (
    "audio_output_produced",
    "audiotk_compiled",
    "audiotk_linked",
    "device_timing",
    "listening",
    "model_executed",
    "network_used",
    "public_benchmark",
    "pitch_measured",
    "real_audio",
    "real_audiotk_source",
    "real_corpus",
    "release_claim",
    "runtime_invoked",
    "speech_preserved",
    "transient_audibility_measured",
    "time_stretch_performed",
    "vendor_runtime_invoked",
    "weights_downloaded",
    "weights_loaded",
)
SCOPE: Dict[str, Any] = {flag: False for flag in SCOPE_FALSE_FLAGS}
SCOPE["task_local_only"] = True

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "sdk_v0_channels": CONTROL_CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "task_geometry_status": TASK_GEOMETRY_STATUS,
    "task_geometry_asserted": False,
    "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "control_channels": CONTROL_CHANNELS,
    "control_sample_format": "f32",
    "control_mode": "offline_rate_accounting",
    "control_performs_time_scale_modification": False,
    "control_incremental_streaming": False,
    "recorded_upstream_license": RECORDED_LICENSE,
    "recorded_time_stretch_stage_found": RECORDED_TIME_STRETCH_STAGE_FOUND,
    "sdk_v0_geometry_preserved": True,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No AudioTK source, header, filter, build, binary or runtime is loaded, compiled or executed.",
    "No upstream AudioTK repository URL, revision, artifact hash or build record is invented.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, listening panel or device clock is used.",
    "No time-scale modification, pitch shift, transient processing or audio output is performed.",
    "The synthetic rate control is declared integer/rational accounting only and is never AudioTK output.",
    "The reported BSD-3-Clause string is a pinned survey note, not a verified licence grant.",
    "Existing SDK DSP providers and merged sibling rate packages are provenance only and are not AudioTK evidence.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, pitch, transient audibility, device timing, benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "source_checkout",
        "recorded_name": UPSTREAM_NAME,
        "recorded_license": RECORDED_LICENSE,
        "path": MISSING_SOURCE_PATH,
        "revision": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "upstream_identity",
        "repository_url": UPSTREAM_REPOSITORY_URL,
        "project_url": UPSTREAM_PROJECT_URL,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "runtime_and_build",
        "path": RUNTIME_ENV_PATH,
        "runtime_lock_path": RUNTIME_LOCK_PATH,
        "build_record_path": BUILD_RECORD_PATH,
        "runtime_lock_sha256": None,
        "build_record_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "source_license_record",
        "recorded_license": RECORDED_LICENSE,
        "required": True,
        "status": "absent",
    },
    {
        "id": "supporting_dsp_plan",
        "path": SUPPORTING_DSP_PLAN_PATH,
        "recorded_role": RECORDED_ROLE,
        "recorded_time_stretch_stage_found":
            RECORDED_TIME_STRETCH_STAGE_FOUND,
        "required": True,
        "status": "absent",
    },
    {
        "id": "rate_geometry_and_adapter",
        "rate_profile": PROFILE,
        "task_geometry_status": TASK_GEOMETRY_STATUS,
        "required": True,
        "status": "absent",
    },
    {
        "id": "rights_and_rate_cohort",
        "rights_path": RIGHTS_RECORD_PATH,
        "cohort_path": COHORT_MANIFEST_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "parity_and_benchmark",
        "parity_path": PARITY_MANIFEST_PATH,
        "required": True,
        "status": "absent",
    },
)

CALLER_ASSET_FIELDS = (
    "build_record_path",
    "build_record_sha256",
    "channels",
    "claimed_time_stretch_capability",
    "cohort_manifest_path",
    "cohort_manifest_sha256",
    "license_record_path",
    "license_record_sha256",
    "parity_vector_path",
    "parity_vector_sha256",
    "rate_max",
    "rate_min",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "sample_rate_hz",
    "source_checkout_path",
    "source_revision",
    "supporting_dsp_plan_path",
    "supporting_dsp_plan_sha256",
    "variant",
)
CALLER_FILE_PAIRS = (
    ("license_record_path", "license_record_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("build_record_path", "build_record_sha256"),
    ("supporting_dsp_plan_path", "supporting_dsp_plan_sha256"),
    ("cohort_manifest_path", "cohort_manifest_sha256"),
    ("parity_vector_path", "parity_vector_sha256"),
)
CALLER_DIR_FIELDS = ("source_checkout_path", "runtime_path")
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_VARIANT = "supporting_dsp_only_offline_comparator"
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/audiotk/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_revision_shape_scalar_rates_"
        "source_anchored_policy_and_supporting_dsp_variant_only; "
        "do_not_import_build_link_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_source_revision": UPSTREAM_REVISION,
    "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
    "required_geometry": {
        "channels": CONTROL_CHANNELS,
        "sample_rate_hz": None,
        "rate_min": None,
        "rate_max": None,
        "status": TASK_GEOMETRY_STATUS,
    },
    "notes": (
        "Every licence, rights, runtime lock, build record, supporting-DSP "
        "plan, rate cohort and parity vector must exist at an absolute path "
        "and match its declared SHA-256 before a caller may process audio. "
        "The manifest must declare the supporting-DSP-only variant and must "
        "not claim a time-stretch capability, because the merged survey did "
        "not identify a ready-made AudioTK time-stretch stage and no upstream "
        "revision or URL is pinned."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "source_checkout_absent",
        "state": "absent",
        "requirement": (
            "Supply an AudioTK source checkout at an immutable 40-hex "
            "revision under research/repos/audiotk, data/checkouts/audiotk or "
            "third_party/audiotk with a per-file SHA-256 manifest; no checkout "
            "exists anywhere in the workspace."),
    },
    {
        "id": "upstream_identity_unpinned",
        "state": "absent",
        "requirement": (
            "Record the canonical upstream repository and project URLs, a "
            "full 40-hex commit, release/tag and per-file SHA-256 values; the "
            "merged survey records only the name AudioTK and the "
            "BSD-3-Clause note, with no URL, commit or digest."),
    },
    {
        "id": "runtime_and_build_record_absent",
        "state": "absent",
        "requirement": (
            "Provide an isolated, hash-pinned C++ build and runtime with a "
            "toolchain/compiler record, dependency lock and reproducible "
            "build digest at data/build-records/audiotk.json; no build, "
            "compiler, lock or runtime environment exists."),
    },
    {
        "id": "source_license_and_rights_unverified",
        "state": "absent",
        "requirement": (
            "Supply the upstream LICENSE/copyright notice at the resolved "
            "commit plus an output-use and redistribution rights record at "
            "data/rights/audiotk-rights.json; 'BSD-3-Clause' is only a survey "
            "string, not a verified grant, notice review or rights clearance."),
    },
    {
        "id": "time_stretch_stage_absent",
        "state": "absent",
        "requirement": (
            "Demonstrate and pin an actual AudioTK time-scale-modification or "
            "variable-frame playback stage with its filter graph and API; the "
            "merged survey explicitly did not identify a ready-made "
            "time-stretch stage and lists AudioTK only as supporting DSP."),
    },
    {
        "id": "supporting_dsp_reuse_plan_absent",
        "state": "absent",
        "requirement": (
            "Record which AudioTK filters, sample formats, frame geometries "
            "and DSP blocks would be reused, how they map to the 16 kHz mono "
            "float32 160-sample v0 boundary, and why existing SDK DSP does "
            "not already cover the need; no such plan exists."),
    },
    {
        "id": "rate_geometry_and_cohort_absent",
        "state": "absent",
        "requirement": (
            "Freeze the rate range, source/output geometry, buffering policy, "
            "pause/filler source-timestamp policy and final partial window, "
            "then supply a rights-cleared matched cohort covering 1x, rate "
            "changes, unfamiliar speech, music, silence, rebuffer, drift and "
            "the final partial window; none exists."),
    },
    {
        "id": "parity_benchmark_and_release_absent",
        "state": "absent",
        "requirement": (
            "Produce one approved exact-runtime AudioTK output and parity "
            "vector, then pitch preservation, transient audibility, speech "
            "preservation, paced playback buffering, benchmark and release "
            "evidence; no local output, timing, listening or parity exists."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_asset_identity",
        "The full 40-hex AudioTK revision, canonical upstream URLs, source "
        "and artifact SHA-256 values and the source licence match exact pins.",
    ),
    (
        "runtime_admission",
        "An isolated hash-pinned C++ build and runtime with a reproducible "
        "toolchain/dependency record is admitted on a recorded platform.",
    ),
    (
        "artifact_rights_and_licence",
        "The BSD-3-Clause notice, output-use, redistribution and cohort rights "
        "are verified with notices at the resolved commit.",
    ),
    (
        "exact_reference_parity",
        "An approved exact-runtime AudioTK output matches the reference on a "
        "frozen caller-supplied input for one frozen configuration.",
    ),
    (
        "rate_cohort_and_scoring",
        "A rights-cleared matched cohort scores source/output mapping, "
        "duration, pitch, transient audibility and playback buffering with "
        "1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift "
        "and the final partial window.",
    ),
    (
        "task_scope_and_supporting_dsp_reuse",
        "The supporting-DSP-only role, exact filter surface, frame geometry, "
        "v0 16 kHz mono 160-sample compatibility and the absence of a "
        "ready-made time-stretch stage are documented without overclaiming.",
    ),
    (
        "opt_in_provider_intake",
        "Explicit opt-in provider intake, licence review, descriptor review "
        "and an independent public-surface decision are complete.",
    ),
    (
        "public_default_and_release",
        "Explicit default selection, paced resource/deadline evidence and "
        "release or public-benchmark approval are recorded; this package is "
        "off by default.",
    ),
)

RATE_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "source_output_mapping",
        "Map half-open source intervals to exact output intervals for each "
        "declared rate and rate change.",
        "synthetic_accounting_only",
    ),
    (
        "duration",
        "Report source duration, output duration, duration ratio and drift "
        "over 1x and rate-change schedules.",
        "synthetic_accounting_only",
    ),
    (
        "pitch",
        "Establish pitch preservation independently of duration scaling.",
        "absent",
    ),
    (
        "transient_audibility",
        "Establish transient audibility under rate changes.",
        "absent",
    ),
    (
        "playback_buffering",
        "Measure FIFO fill/flush, queue depth, deadlines, final partial "
        "window and paced playback buffering.",
        "structural_only",
    ),
    (
        "condition_coverage",
        "Cover 1x, rate changes, unfamiliar speech, music, silence, rebuffer, "
        "drift and the final partial window.",
        "absent",
    ),
    (
        "pause_filler_and_speech_preservation",
        "Tie pause or filler decisions to source timestamps and measure "
        "speech preservation separately.",
        "structural_only",
    ),
    (
        "invalid_missing_nonfinite_adverse",
        "Reject invalid, missing, nonfinite and adverse inputs before "
        "processing and retain every outcome.",
        "structural_only",
    ),
)

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "pcm_empty",
    "pcm_not_sequence",
    "pcm_none",
    "pcm_wrong_rate",
    "pcm_stereo",
    "pcm_nan",
    "pcm_pos_inf",
    "pcm_neg_inf",
    "pcm_out_of_range",
    "pcm_bool",
    "pcm_string",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_short_revision",
    "manifest_nonhex_revision",
    "manifest_wrong_variant",
    "manifest_time_stretch_claimed",
    "manifest_channels_zero",
    "manifest_rate_below_range",
    "manifest_rate_above_range",
    "manifest_rate_zero",
    "manifest_rate_exponent",
    "manifest_rate_trailing_zero",
    "manifest_rate_min_not_less_than_max",
    "manifest_rate_one_not_covered",
    "manifest_sample_rate_out_of_range",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
    "policy_not_list",
    "policy_output_anchored",
    "policy_negative_start",
    "policy_empty_interval",
    "policy_unordered",
    "policy_beyond_source",
    "rate_zero",
    "rate_negative",
    "rate_nan",
    "rate_pos_inf",
    "rate_too_small",
    "rate_too_large",
    "rate_bool",
    "rate_string",
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "source": EVIDENCE_SOURCE,
    "source_sha256": SOURCE_PINS[EVIDENCE_SOURCE],
    "evidence_line": EVIDENCE_LINE,
    "recorded_name": UPSTREAM_NAME,
    "recorded_license": RECORDED_LICENSE,
    "recorded_time_stretch_stage_found": False,
    "recorded_role": RECORDED_ROLE,
    "recorded_repository_url": UPSTREAM_REPOSITORY_URL,
    "recorded_project_url": UPSTREAM_PROJECT_URL,
    "recorded_revision": UPSTREAM_REVISION,
    "recorded_quote": (
        "AudioTK (BSD-3-Clause) - general DSP/filter toolkit. This pass did "
        "not identify a ready-made time-stretch stage in it, so it is not "
        "listed as a stretcher; it may still be useful for supporting DSP."),
    "finding": (
        "The survey places AudioTK in the checked and not-carried-forward "
        "group, records a BSD-3-Clause licence string, finds no ready-made "
        "time-stretch stage and leaves it as possible supporting DSP."),
    "sibling_context_not_attributed": [
        "The SoundTouch, aubio, Signalsmith Stretch, Sonic and Bungee task "
        "packages are separate candidates or references and contribute no "
        "AudioTK source, output, licence or measurement.",
        "The existing SDK SpeexDSP and high-pass providers are installed DSP "
        "provenance only; they are not AudioTK filters and do not establish "
        "AudioTK reuse.",
        "The playback-speed candidate note's WSOLA, phase-vocoder and PSOLA "
        "algorithm sections are general references, not AudioTK code.",
    ],
    "notes": (
        "No AudioTK source, output, revision or runtime was acquired. No "
        "duration, pitch, transient, speech-preservation, latency, RTF or "
        "listening value is attributed to this candidate."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_rate_accounting_plan_not_audio_output")


class Reject(ValueError):
    """Fail-closed rejection for malformed, unsupported or unqualified input."""


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
    try:
        return json.dumps(_normalize_negzero(value), sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise Reject("value is not canonical-JSON serializable") from error


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def strict_loads(text: str) -> Dict[str, Any]:
    """Parse JSON while rejecting non-finite constants and duplicate keys."""

    def reject(value: str) -> Any:
        raise Reject("non-finite JSON: " + value)

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Reject("duplicate JSON key: " + key)
            result[key] = value
        return result

    value = json.loads(text, parse_constant=reject, object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise Reject("expected JSON object")
    return value


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def rate_decimal(value: Fraction) -> str:
    """Canonical non-exponential decimal for a positive terminating rate."""
    fraction = Fraction(value)
    if fraction <= 0:
        raise Reject("rate must be positive")
    denominator = fraction.denominator
    remainder = denominator
    twos = fives = 0
    while remainder % 2 == 0:
        remainder //= 2
        twos += 1
    while remainder % 5 == 0:
        remainder //= 5
        fives += 1
    if remainder != 1:
        raise Reject("rate has no finite decimal representation")
    scale = max(twos, fives)
    scaled = fraction.numerator * (10 ** scale) // fraction.denominator
    text = str(scaled)
    if scale:
        text = text.rjust(scale + 1, "0")
        text = text[:-scale] + "." + text[-scale:]
        text = text.rstrip("0")
        if text.endswith("."):
            text = text[:-1]
    if not CANONICAL_DECIMAL.fullmatch(text):
        raise Reject("rate is not a canonical decimal")
    return text


def parse_rate(value: Any, field: str) -> Fraction:
    if not isinstance(value, str) or not CANONICAL_DECIMAL.fullmatch(value):
        raise Reject(field + " is not a canonical decimal string")
    return Fraction(value)


# ---------------------------------------------------------------------------
# Source checkout, asset, supporting-DSP and absence audit.
# ---------------------------------------------------------------------------

def _read_git_head(repository: Path) -> Optional[str]:
    marker = repository / ".git"
    if not marker.exists():
        return None
    if marker.is_file():
        try:
            text = marker.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        if not text.startswith("gitdir:"):
            return None
        target = Path(text.split(":", 1)[1].strip())
        if not target.is_absolute():
            target = (repository / target).resolve()
    else:
        target = marker
    head_path = target / "HEAD"
    if not head_path.is_file():
        return None
    try:
        head = head_path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not head.startswith("ref: "):
        return head if COMMIT_PATTERN.fullmatch(head) else None
    ref = head.split(":", 1)[1].strip()
    ref_path = target / ref
    if ref_path.is_file():
        try:
            value = ref_path.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        return value if COMMIT_PATTERN.fullmatch(value) else None
    packed = target / "packed-refs"
    if packed.is_file():
        try:
            for line in packed.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("^"):
                    continue
                digest, _, name = line.partition(" ")
                if name == ref and COMMIT_PATTERN.fullmatch(digest):
                    return digest
        except OSError:
            return None
    return None


def _license_candidates(repository: Path) -> List[str]:
    found: List[str] = []
    if not repository.is_dir():
        return found
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING",
                 "COPYING.md", "COPYING.txt", "NOTICE"):
        if (repository / name).is_file():
            found.append(name)
    return found


def _source_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "research/repos/audiotk",
        SOURCE_ROOT / "research/repos/AudioTK",
        SOURCE_ROOT / "research/repos/audio-tk",
        SOURCE_ROOT / "data/checkouts/audiotk",
        SOURCE_ROOT / "data/checkouts/AudioTK",
        SOURCE_ROOT / "third_party/audiotk",
        SOURCE_ROOT / "third_party/AudioTK",
        SOURCE_ROOT / "third_party/audio-tk",
        SOURCE_ROOT / "deps/audiotk",
        SOURCE_ROOT / "deps/AudioTK",
    ]


def probe_absence() -> List[Dict[str, Any]]:
    return [
        {"path": relative, "exists": (SOURCE_ROOT / relative).exists()}
        for relative in ABSENCE_PROBES
    ]


def _file_pin(relative: str) -> Dict[str, Any]:
    path = SDK_ROOT / relative
    present = path.is_file()
    digest = sha256(path.read_bytes()) if present else None
    expected = BOUNDARY_PINS.get(relative)
    return {
        "path": relative,
        "present": present,
        "sha256": digest,
        "pinned": bool(expected),
        "matches_boundary_pin": bool(expected) and digest == expected,
    }


def audit_supporting_dsp() -> Dict[str, Any]:
    """Fixed local reads only; no compile, link or execution."""
    return {
        "audiotk_source_present": any(
            path.is_dir() for path in _source_candidates()),
        "audiotk_revision": None,
        "audiotk_revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "recorded_license": RECORDED_LICENSE,
        "recorded_role": RECORDED_ROLE,
        "recorded_time_stretch_stage_found":
            RECORDED_TIME_STRETCH_STAGE_FOUND,
        "existing_sdk_dsp": [
            _file_pin(relative) for relative in EXISTING_DSP_FILES],
        "sibling_rate_packages": [
            dict(_file_pin(relative),
                 role="sibling_rate_evidence_not_attributed")
            for relative in SIBLING_RATE_PACKAGES],
        "reuse_decision": (
            "no_audiotk_reuse; existing SDK DSP and sibling rate evidence are "
            "separate provenance and are not AudioTK measurements"),
        "note": (
            "The survey found no ready-made AudioTK time-stretch stage. SDK "
            "SpeexDSP and high-pass providers are already installed and are "
            "not replaced, extended or re-attributed by this package."),
    }


def audit_assets() -> Dict[str, Any]:
    source_paths = _source_candidates()
    present_sources = [path for path in source_paths if path.is_dir()]
    repository = present_sources[0] if present_sources else None
    revision = _read_git_head(repository) if repository is not None else None
    licenses = _license_candidates(repository) if repository is not None else []
    weight_paths = [
        SOURCE_ROOT / "data/models/audiotk",
        SOURCE_ROOT / "data/weights/audiotk",
    ]
    runtime_env = SOURCE_ROOT / RUNTIME_ENV_PATH
    runtime_lock = SOURCE_ROOT / RUNTIME_LOCK_PATH
    build_record = SOURCE_ROOT / BUILD_RECORD_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    parity_manifest = SOURCE_ROOT / PARITY_MANIFEST_PATH
    dsp_plan = SOURCE_ROOT / SUPPORTING_DSP_PLAN_PATH
    probes = probe_absence()
    return {
        "source_checkout_path": MISSING_SOURCE_PATH,
        "source_checkout_present": repository is not None,
        "source_revision": revision,
        "source_revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "source_revision_matches": False,
        "source_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.is_dir()}
            for path in source_paths
        ],
        "recorded_repository_url": UPSTREAM_REPOSITORY_URL,
        "recorded_project_url": UPSTREAM_PROJECT_URL,
        "license_files": licenses,
        "license_file_present": bool(licenses),
        "recorded_license": RECORDED_LICENSE,
        "weights_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in weight_paths
        ],
        "weights_present": any(path.exists() for path in weight_paths),
        "runtime_env_present": runtime_env.is_dir(),
        "runtime_lock_present": runtime_lock.is_file(),
        "build_record_present": build_record.is_file(),
        "rights_record_present": rights_record.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "parity_manifest_present": parity_manifest.is_file(),
        "supporting_dsp_plan_present": dsp_plan.is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "supporting_dsp_audit": audit_supporting_dsp(),
        "requested_config": {
            "recorded_name": UPSTREAM_NAME,
            "recorded_license": RECORDED_LICENSE,
            "recorded_role": RECORDED_ROLE,
            "recorded_hardware": RECORDED_HARDWARE,
            "geometry_status": TASK_GEOMETRY_STATUS,
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CONTROL_CHANNELS,
            "control_frame_samples": SDK_FRAME_SAMPLES,
            "upstream_revision": UPSTREAM_REVISION,
        },
    }


def task_row_identity() -> Dict[str, Any]:
    relative = "audio-benchmark-platform/plan/swarm/TASKS.json"
    path = SOURCE_ROOT / relative
    if not path.is_file():
        raise Reject("task board is unavailable at " + relative)
    try:
        document = strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        raise Reject("task board unreadable") from error
    rows = [row for row in document.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise Reject("expected exactly one linked task row")
    row = rows[0]
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK or stable["component"] != COMPONENT:
        raise Reject("linked task row identity mismatch")
    if stable["repository"] != "audio-sdk" or stable["mode"] != MODE:
        raise Reject("linked task row repository/mode mismatch")
    claim = row.get("claim")
    if not isinstance(claim, dict):
        raise Reject("linked task row claim missing")
    if claim.get("base_commit") != BASE_COMMIT:
        raise Reject("claim base commit mismatch")
    if claim.get("branch") != BRANCH:
        raise Reject("claim branch mismatch")
    if claim.get("worktree") != CLAIM_WORKTREE:
        raise Reject("claim worktree mismatch")
    if claim.get("reviewer") != REVIEWER:
        raise Reject("claim reviewer mismatch")
    return {
        "source": relative,
        "stable_fields": stable,
        "stable_sha256": sha256(canonical_bytes(stable)),
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "claim": {
            "base_commit": claim["base_commit"],
            "branch": claim["branch"],
            "worktree": claim["worktree"],
            "reviewer": claim["reviewer"],
        },
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic PCM and rate accounting.  No audio is transformed.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x544B4155
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 37, 0.30) + 0.01 * noise)
    return samples


def validate_pcm(signal: Any, sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ,
                 channels: int = CONTROL_CHANNELS) -> List[float]:
    if isinstance(sample_rate_hz, bool) or not isinstance(sample_rate_hz, int):
        raise Reject("sample rate must be an integer")
    if sample_rate_hz != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("control supports only 16000 Hz")
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise Reject("channels must be an integer")
    if channels != CONTROL_CHANNELS:
        raise Reject("only mono is supported")
    if not isinstance(signal, (list, tuple)):
        raise Reject("signal must be a sample sequence")
    if not signal:
        raise Reject("signal must be nonempty")
    if len(signal) > PCM_SAMPLE_CAP:
        raise Reject("signal exceeds the evidence cap")
    checked: List[float] = []
    for index, sample in enumerate(signal):
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise Reject(f"sample {index} is not numeric")
        value = float(sample)
        if not math.isfinite(value):
            raise Reject(f"sample {index} is not finite")
        if value < -1.0 or value > 1.0:
            raise Reject(f"sample {index} is outside [-1, 1]")
        checked.append(value)
    return checked


def pcm_summary(signal: Sequence[float],
                sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ) -> Dict[str, Any]:
    values = validate_pcm(signal, sample_rate_hz)
    peak = max(abs(value) for value in values)
    return {
        "samples": len(values),
        "sample_rate_hz": sample_rate_hz,
        "channels": CONTROL_CHANNELS,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs": peak,
        "nonfinite_samples": 0,
        "sha256": sha256(canonical_bytes(list(values))),
    }


def _checked_rate(rate: Any) -> Fraction:
    if isinstance(rate, bool):
        raise Reject("rate must not be boolean")
    if isinstance(rate, Fraction):
        fraction = rate
    elif isinstance(rate, (int, float)):
        value = float(rate)
        if not math.isfinite(value):
            raise Reject("rate is not finite")
        fraction = Fraction(rate)
    elif isinstance(rate, str):
        fraction = parse_rate(rate, "rate")
    else:
        raise Reject("rate must be numeric or a canonical decimal string")
    if fraction < MIN_RATE or fraction > MAX_RATE:
        raise Reject("rate is outside the admitted accounting range")
    return fraction


def rate_mapping(rate: Any, source_samples: int) -> Dict[str, Any]:
    fraction = _checked_rate(rate)
    if isinstance(source_samples, bool) or not isinstance(source_samples, int):
        raise Reject("source_samples must be an integer")
    if source_samples <= 0:
        raise Reject("source_samples must be positive")
    output = Fraction(source_samples) / fraction
    if output.denominator != 1:
        raise Reject("declared rate does not yield an integer output count")
    output_samples = int(output)
    return {
        "rate": rate_decimal(fraction),
        "source_samples": source_samples,
        "output_samples": output_samples,
        "source_interval": [0, source_samples],
        "output_interval": [0, output_samples],
        "duration_ratio": fraction_text(Fraction(1, 1) / fraction),
        "pitch_measured": False,
        "transient_measured": False,
        "audio_produced": False,
    }


def rate_table(source_samples: int = CONTROL_SOURCE_SAMPLES
               ) -> List[Dict[str, Any]]:
    return [
        rate_mapping(Fraction(1, 1), source_samples),
        rate_mapping(Fraction(3, 4), source_samples),
        rate_mapping(Fraction(4, 5), source_samples),
        rate_mapping(Fraction(5, 4), source_samples),
        rate_mapping(Fraction(3, 2), source_samples),
    ]


def rate_schedule(segments: Sequence[Tuple[Any, int]],
                  source_samples: int = CONTROL_SOURCE_SAMPLES
                  ) -> Dict[str, Any]:
    if not isinstance(segments, (list, tuple)) or not segments:
        raise Reject("schedule must be a nonempty segment list")
    rows: List[Dict[str, Any]] = []
    source_cursor = 0
    output_cursor = 0
    for index, segment in enumerate(segments):
        if not isinstance(segment, (list, tuple)) or len(segment) != 2:
            raise Reject("schedule segment must be a (rate, samples) pair")
        rate_value, count = segment
        fraction = _checked_rate(rate_value)
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise Reject("schedule sample count must be a positive integer")
        output = Fraction(count) / fraction
        if output.denominator != 1:
            raise Reject("schedule rate does not yield an integer output")
        produced = int(output)
        rows.append({
            "index": index,
            "rate": rate_decimal(fraction),
            "source_start": source_cursor,
            "source_end": source_cursor + count,
            "output_start": output_cursor,
            "output_end": output_cursor + produced,
            "source_samples": count,
            "output_samples": produced,
            "audio_produced": False,
        })
        source_cursor += count
        output_cursor += produced
    if source_cursor != source_samples:
        raise Reject("schedule does not consume the declared source length")
    return {
        "segments": rows,
        "source_samples": source_cursor,
        "output_samples": output_cursor,
        "output_ratio": fraction_text(Fraction(output_cursor, source_cursor)),
        "rate_change_count": len(rows) - 1,
        "audio_produced": False,
    }


def duration_accounting(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(rows, (list, tuple)) or not rows:
        raise Reject("duration accounting needs rate rows")
    entries: List[Dict[str, Any]] = []
    for row in rows:
        rate = parse_rate(row["rate"], "rate")
        source_duration = Fraction(row["source_samples"],
                                   CONTROL_SAMPLE_RATE_HZ)
        output_duration = Fraction(row["output_samples"],
                                   CONTROL_SAMPLE_RATE_HZ)
        entries.append({
            "rate": row["rate"],
            "source_duration_s": fraction_text(source_duration),
            "output_duration_s": fraction_text(output_duration),
            "duration_ratio": fraction_text(output_duration / source_duration),
            "expected_ratio": fraction_text(Fraction(1, 1) / rate),
            "conserved_against_expected": (
                output_duration / source_duration == Fraction(1, 1) / rate),
        })
    return {
        "rows": entries,
        "all_ratios_match": all(
            entry["conserved_against_expected"] for entry in entries),
        "audio_produced": False,
    }


def final_partial_window(valid_samples: int = CONTROL_TAIL_VALID_SAMPLES,
                         frame_samples: int = SDK_FRAME_SAMPLES
                         ) -> Dict[str, Any]:
    if isinstance(valid_samples, bool) or not isinstance(valid_samples, int):
        raise Reject("valid_samples must be an integer")
    if not 1 <= valid_samples <= frame_samples:
        raise Reject("valid_samples must be within the final frame")
    return {
        "valid_samples": valid_samples,
        "padded_samples": frame_samples,
        "padding_samples": frame_samples - valid_samples,
        "zero_padded": True,
        "frame_samples": frame_samples,
        "audio_produced": False,
        "note": (
            "Declared final-window accounting at 1x only; the padding is not "
            "accepted audio and no output samples are generated."),
    }


def paired_identity(signal: Sequence[float]) -> Dict[str, Any]:
    """1x identity mapping only: the same samples are validated and copied."""
    values = validate_pcm(signal)
    copied = list(values)
    source = pcm_summary(values)
    target = pcm_summary(copied)
    return {
        "rate": "1",
        "identity_mapping": True,
        "processing_performed": False,
        "source": source,
        "output": target,
        "bytes_equal": source["sha256"] == target["sha256"],
        "audio_output_claimed": False,
    }


def validate_pause_policy(policy: Any, source_samples: int
                          ) -> Dict[str, Any]:
    if not isinstance(policy, list):
        raise Reject("pause/filler policy must be a list")
    if not policy:
        raise Reject("pause/filler policy must be nonempty")
    checked: List[Dict[str, Any]] = []
    previous_end = 0
    for index, item in enumerate(policy):
        if not isinstance(item, dict):
            raise Reject("pause/filler interval must be an object")
        if "output_start" in item or "output_end" in item:
            raise Reject("pause/filler interval must be source-anchored")
        expected = {"id", "source_start", "source_end"}
        if set(item) != expected:
            raise Reject("pause/filler interval has unexpected fields")
        identifier = item["id"]
        if not isinstance(identifier, str) or not identifier:
            raise Reject("pause/filler interval id must be a string")
        start = item["source_start"]
        end = item["source_end"]
        for name, value in (("source_start", start), ("source_end", end)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise Reject("pause/filler " + name + " must be an integer")
        if start < 0:
            raise Reject("pause/filler interval starts before the source")
        if end <= start:
            raise Reject("pause/filler interval is empty or reversed")
        if end > source_samples:
            raise Reject("pause/filler interval exceeds the source")
        if start < previous_end:
            raise Reject("pause/filler intervals overlap or are unordered")
        previous_end = end
        checked.append({
            "id": identifier,
            "source_start": start,
            "source_end": end,
            "source_anchored": True,
            "output_anchored": False,
        })
    return {
        "intervals": checked,
        "interval_count": len(checked),
        "source_samples": source_samples,
        "source_anchored": True,
        "speech_preserved": None,
        "speech_preservation_measured": False,
    }


PAUSE_POLICY: Tuple[Dict[str, Any], ...] = (
    {"id": "pause-0", "source_start": 8000, "source_end": 8480},
    {"id": "filler-1", "source_start": 24000, "source_end": 24320},
)


def qualification_gate(evidence: Any) -> Dict[str, Any]:
    """Fail closed: any missing or non-passed gate rejects qualification."""
    if not isinstance(evidence, dict):
        raise Reject("qualification evidence must be an object")
    missing = [gate for gate, _ in GATE_REQUIREMENTS
               if evidence.get(gate) != "passed"]
    if missing:
        raise Reject("missing or unqualified gates: " + ",".join(missing))
    raise Reject("no exact-runtime AudioTK evidence exists to qualify")


# ---------------------------------------------------------------------------
# Caller-supplied manifest contract.
# ---------------------------------------------------------------------------

def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent."""
    root = "/nonexistent/audiotk-evidence-fixture"
    digest = "0" * 64
    return {
        "build_record_path": root + "/build.json",
        "build_record_sha256": digest,
        "channels": CONTROL_CHANNELS,
        "claimed_time_stretch_capability": False,
        "cohort_manifest_path": root + "/cohort.json",
        "cohort_manifest_sha256": digest,
        "license_record_path": root + "/license.json",
        "license_record_sha256": digest,
        "parity_vector_path": root + "/parity.json",
        "parity_vector_sha256": digest,
        "rate_max": "1.5",
        "rate_min": "0.75",
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "runtime_path": root + "/runtime",
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "source_checkout_path": root + "/source",
        "source_revision": "0" * 40,
        "supporting_dsp_plan_path": root + "/dsp-plan.json",
        "supporting_dsp_plan_sha256": digest,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package."""
    assignments = {
        "build_record_path": HERE / "reference.py",
        "cohort_manifest_path": HERE / "reference.py",
        "license_record_path": HERE / "README.md",
        "parity_vector_path": HERE / "README.md",
        "rights_record_path": HERE / "test_reference.py",
        "runtime_lock_path": HERE / "verify.py",
        "supporting_dsp_plan_path": HERE / "reference.py",
    }
    manifest: Dict[str, Any] = {
        "channels": CONTROL_CHANNELS,
        "claimed_time_stretch_capability": False,
        "rate_max": "1.5",
        "rate_min": "0.75",
        "runtime_path": str(SDK_ROOT),
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "source_checkout_path": str(HERE),
        "source_revision": "a" * 40,
        "variant": CALLER_VARIANT,
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = sha256(
            path.read_bytes())
    return manifest


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_MANIFEST_BYTES:
                raise Reject("asset exceeds the evidence cap")
            digest.update(chunk)
    return digest.hexdigest()


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise Reject("manifest must be an object")
    expected = set(CALLER_ASSET_FIELDS)
    present = set(manifest)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing:
        raise Reject("manifest missing fields: " + ",".join(missing))
    if extra:
        raise Reject("manifest has unknown fields: " + ",".join(extra))
    for field in CALLER_SHA_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}",
                                                         value):
            raise Reject("manifest " + field + " is not a lowercase SHA-256")
    for field in CALLER_DIR_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + field + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + field + " must be absolute")
    for path_field, _ in CALLER_FILE_PAIRS:
        value = manifest[path_field]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + path_field + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + path_field + " must be absolute")
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not COMMIT_PATTERN.fullmatch(revision):
        raise Reject("manifest source_revision must be a full 40-hex commit")
    channels = manifest["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise Reject("manifest channels must be an integer")
    if channels != CONTROL_CHANNELS:
        raise Reject("manifest channels mismatch")
    sample_rate = manifest["sample_rate_hz"]
    if isinstance(sample_rate, bool) or not isinstance(sample_rate, int):
        raise Reject("manifest sample_rate_hz must be an integer")
    if sample_rate < MIN_SAMPLE_RATE_HZ or sample_rate > MAX_SAMPLE_RATE_HZ:
        raise Reject("manifest sample_rate_hz is outside the admitted range")
    rate_min = parse_rate(manifest["rate_min"], "manifest rate_min")
    rate_max = parse_rate(manifest["rate_max"], "manifest rate_max")
    if rate_min < MIN_RATE or rate_max > MAX_RATE:
        raise Reject("manifest rate range is outside the admitted bounds")
    if rate_min >= rate_max:
        raise Reject("manifest rate_min must be below rate_max")
    if not rate_min <= Fraction(1, 1) <= rate_max:
        raise Reject("manifest rate range must include 1x")
    if manifest["claimed_time_stretch_capability"] is not False:
        raise Reject("manifest must not claim a time-stretch capability")
    if manifest["variant"] != CALLER_VARIANT:
        raise Reject("manifest variant must be " + CALLER_VARIANT)
    for field in CALLER_DIR_FIELDS:
        if not Path(manifest[field]).is_dir():
            raise Reject("manifest " + field + " directory is missing")
    total_bytes = 0
    for path_field, sha_field in CALLER_FILE_PAIRS:
        path = Path(manifest[path_field])
        if not path.is_file():
            raise Reject("manifest " + path_field + " file is missing")
        actual = _hash_file(path)
        if actual != manifest[sha_field]:
            raise Reject("manifest " + path_field + " SHA-256 mismatch")
        total_bytes += path.stat().st_size
    return {
        "accepted": True,
        "source_revision": revision,
        "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "variant": CALLER_VARIANT,
        "sample_rate_hz": sample_rate,
        "channels": CONTROL_CHANNELS,
        "rate_min": rate_decimal(rate_min),
        "rate_max": rate_decimal(rate_max),
        "time_stretch_capability_claimed": False,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "audiotk_executed": False,
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    good_pcm = synthetic_pcm()
    good_manifest = _shape_only_manifest()
    existing = _existing_file_manifest()

    def case(case_id: str, action) -> Dict[str, str]:
        try:
            action()
        except Reject as error:
            return {"case": case_id, "result": "rejected",
                    "reason": str(error)}
        except Exception as error:  # noqa: BLE001 - recorded, never swallowed
            return {"case": case_id, "result": "unexpected_error",
                    "reason": type(error).__name__ + ": " + str(error)}
        return {"case": case_id, "result": "accepted", "reason": ""}

    def wrong(key: str, value: Any):
        manifest = dict(good_manifest)
        manifest[key] = value
        return lambda: validate_caller_manifest(manifest)

    def drop(key: str):
        manifest = {k: v for k, v in good_manifest.items() if k != key}
        return lambda: validate_caller_manifest(manifest)

    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_pcm, 8000)),
        ("pcm_stereo", lambda: validate_pcm(
            good_pcm, CONTROL_SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("build_record_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "source_checkout_path", "checkouts/audiotk")),
        ("manifest_bad_sha", wrong("build_record_sha256", "ABC")),
        ("manifest_short_revision", wrong("source_revision", "7dae8a2")),
        ("manifest_nonhex_revision", wrong("source_revision", "g" * 40)),
        ("manifest_wrong_variant", wrong(
            "variant", "time_stretch_offline_renderer")),
        ("manifest_time_stretch_claimed", wrong(
            "claimed_time_stretch_capability", True)),
        ("manifest_channels_zero", wrong("channels", 0)),
        ("manifest_rate_below_range", wrong("rate_min", "0.25")),
        ("manifest_rate_above_range", wrong("rate_max", "2.5")),
        ("manifest_rate_zero", wrong("rate_min", "0")),
        ("manifest_rate_exponent", wrong("rate_max", "1e0")),
        ("manifest_rate_trailing_zero", wrong("rate_max", "1.50")),
        ("manifest_rate_min_not_less_than_max", wrong("rate_min", "1.5")),
        ("manifest_rate_one_not_covered", lambda: validate_caller_manifest(
            dict(good_manifest, rate_min="0.75", rate_max="0.8"))),
        ("manifest_sample_rate_out_of_range", wrong(
            "sample_rate_hz", 4000)),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, build_record_path=(
                "/nonexistent/audiotk-evidence-fixture/build.json")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, runtime_path=(
                "/nonexistent/audiotk-evidence-fixture/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, build_record_sha256="0" * 64))),
        ("policy_not_list", lambda: validate_pause_policy(
            {"source_start": 0}, CONTROL_SOURCE_SAMPLES)),
        ("policy_output_anchored", lambda: validate_pause_policy(
            [{"id": "bad", "output_start": 0, "output_end": 160}],
            CONTROL_SOURCE_SAMPLES)),
        ("policy_negative_start", lambda: validate_pause_policy(
            [{"id": "bad", "source_start": -1, "source_end": 10}],
            CONTROL_SOURCE_SAMPLES)),
        ("policy_empty_interval", lambda: validate_pause_policy(
            [{"id": "bad", "source_start": 10, "source_end": 10}],
            CONTROL_SOURCE_SAMPLES)),
        ("policy_unordered", lambda: validate_pause_policy(
            [{"id": "a", "source_start": 100, "source_end": 200},
             {"id": "b", "source_start": 150, "source_end": 250}],
            CONTROL_SOURCE_SAMPLES)),
        ("policy_beyond_source", lambda: validate_pause_policy(
            [{"id": "bad", "source_start": 0,
              "source_end": CONTROL_SOURCE_SAMPLES + 1}],
            CONTROL_SOURCE_SAMPLES)),
        ("rate_zero", lambda: rate_mapping(0, 160)),
        ("rate_negative", lambda: rate_mapping(-1, 160)),
        ("rate_nan", lambda: rate_mapping(math.nan, 160)),
        ("rate_pos_inf", lambda: rate_mapping(math.inf, 160)),
        ("rate_too_small", lambda: rate_mapping(Fraction(1, 4), 160)),
        ("rate_too_large", lambda: rate_mapping(Fraction(5, 2), 160)),
        ("rate_bool", lambda: rate_mapping(True, 160)),
        ("rate_string", lambda: rate_mapping("fast", 160)),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    if [item["case"] for item in results] != list(ADVERSE_CASE_IDS):
        raise Reject("adverse case IDs or order mismatch")
    if any(item["result"] != "rejected" for item in results):
        raise Reject("an adverse control was accepted")
    return results


def build_control() -> Dict[str, Any]:
    source = synthetic_pcm()
    identity = paired_identity(source)
    rows = rate_table()
    schedule = rate_schedule([
        (Fraction(1, 1), 8000),
        (Fraction(4, 5), 16000),
        (Fraction(5, 4), 12000),
        (Fraction(1, 1), 12000),
    ])
    duration = duration_accounting(rows)
    partial = final_partial_window()
    policy = validate_pause_policy(list(PAUSE_POLICY), CONTROL_SOURCE_SAMPLES)
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse]
    return {
        "model_executed": False,
        "audiotk_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CONTROL_CHANNELS,
            "control_frame_samples": SDK_FRAME_SAMPLES,
            "output_queue_capacity": OUTPUT_QUEUE_CAPACITY,
            "task_geometry_status": TASK_GEOMETRY_STATUS,
            "task_geometry_asserted": False,
            "mode": "offline_rate_accounting",
            "incremental_streaming": False,
            "performs_time_scale_modification": False,
            "pitch_shift_performed": False,
            "audio_output_produced": False,
        },
        "input_pcm": pcm_summary(source),
        "identity_control": identity,
        "rate_table": rows,
        "rate_schedule": schedule,
        "duration": duration,
        "final_partial_window": partial,
        "pause_filler_policy": policy,
        "pitch": {
            "status": "not_measured",
            "preserved": None,
            "qualification_effect": "none",
        },
        "transient_audibility": {
            "status": "not_measured",
            "qualification_effect": "none",
        },
        "playback_buffering": {
            "input_frame_samples": SDK_FRAME_SAMPLES,
            "output_queue_capacity": OUTPUT_QUEUE_CAPACITY,
            "worker_measured": False,
            "device_measured": False,
            "fill_flush_measured": False,
            "note": (
                "Only declared frame and queue geometry from the v0 contract; "
                "no worker, queue, renderer or device was run."),
        },
        "speech_preservation": {
            "status": "not_measured",
            "value": None,
            "qualification_effect": "none",
        },
        "acceptance_outcomes": [
            {
                "id": "source_output_mapping",
                "measured": False,
                "value": None,
                "reason": "declared half-open interval accounting only",
            },
            {
                "id": "duration",
                "measured": False,
                "value": None,
                "reason": "exact arithmetic on a declared plan; no playback",
            },
            {
                "id": "pitch",
                "measured": False,
                "value": None,
                "reason": "no time-scale modification or pitch measurement",
            },
            {
                "id": "transient_audibility",
                "measured": False,
                "value": None,
                "reason": "no TSM output, listening or transient score",
            },
            {
                "id": "playback_buffering",
                "measured": False,
                "value": None,
                "reason": "no worker, FIFO, renderer or device clock",
            },
            {
                "id": "condition_coverage",
                "measured": False,
                "value": None,
                "reason": "no real speech, music, silence, rebuffer or drift set",
            },
            {
                "id": "pause_filler_and_speech_preservation",
                "measured": False,
                "value": None,
                "reason": "policy shape only; no speech-preservation score",
            },
            {
                "id": "invalid_missing_nonfinite_adverse",
                "measured": False,
                "value": None,
                "reason": "structural rejection control only",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf",
                "rate_nan", "rate_pos_inf"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range",
                "pcm_wrong_rate", "pcm_stereo",
                "manifest_channels_zero", "manifest_rate_below_range",
                "manifest_rate_above_range", "manifest_rate_zero",
                "manifest_rate_exponent", "manifest_rate_trailing_zero",
                "manifest_rate_min_not_less_than_max",
                "manifest_rate_one_not_covered",
                "manifest_sample_rate_out_of_range",
                "manifest_time_stretch_claimed",
                "rate_zero", "rate_negative", "rate_too_small",
                "rate_too_large", "rate_bool", "rate_string",
                "policy_output_anchored", "policy_negative_start",
                "policy_empty_interval", "policy_unordered",
                "policy_beyond_source"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "manifest_missing_field", "manifest_missing_asset",
                "manifest_missing_directory", "policy_not_list"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic rate-accounting control only. It performs no "
            "time-scale modification, pitch shift or audio rendering, is not "
            "AudioTK output, not real speech, not a quality or timing result "
            "and cannot qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Report and contract models.
# ---------------------------------------------------------------------------

def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["source_checkout_present"]
        and observed["source_revision"] is not None
        and observed["license_file_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["build_record_present"]
        and observed["rights_record_present"]
        and observed["cohort_manifest_present"]
        and observed["parity_manifest_present"]
        and observed["supporting_dsp_plan_present"])
    if complete:
        result = "asset_set_complete_pending_parity"
    elif observed["source_checkout_present"]:
        result = "source_present_assets_unqualified"
    else:
        result = "absent"
    return {
        "qualified": False,
        "audit_result": result,
        "source_present": observed["source_checkout_present"],
        "source_revision": observed["source_revision"],
        "source_revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "license_present": observed["license_file_present"],
        "recorded_license": RECORDED_LICENSE,
        "weights_present": observed["weights_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "build_record_present": observed["build_record_present"],
        "rights_record_present": observed["rights_record_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "supporting_dsp_plan_present": observed["supporting_dsp_plan_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No AudioTK source, revision, licence file, build record, runtime "
            "lock, rights record, cohort, parity vector or supporting-DSP "
            "plan was observed. Sibling and existing SDK DSP material is not "
            "AudioTK evidence."),
    }


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = _asset_audit_summary()
    control = build_control()
    gates = [
        {"id": gate, "requirement": requirement, "status": "blocked"}
        for gate, requirement in GATE_REQUIREMENTS
    ]
    profile_items = [
        {
            "id": item,
            "requirement": requirement,
            "package_status": status,
            "satisfied_for_qualification": False,
            "qualification_effect": "none",
        }
        for item, requirement, status in RATE_REQUIREMENTS
    ]
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": {
            "status": QUALIFICATION,
            "candidate_qualified": False,
            "no_missing_result_qualifies_candidate": True,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "blocked_gate_count": len(gates),
            "blocked_gate_ids": [gate["id"] for gate in gates],
            "reason": (
                "The AudioTK source checkout, canonical upstream URL, full "
                "40-hex revision, build record, runtime, verified licence, "
                "rights record, supporting-DSP reuse plan and an actual "
                "time-stretch stage are absent; no rate cohort, parity "
                "vector, local output or supporting-DSP measurement exists."),
        },
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "generated_by": "reference.py",
        "format": FORMAT,
        "boundary": BOUNDARY,
        "scope": SCOPE,
        "task_row_identity": identity,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "upstream_identity": {
            "name": UPSTREAM_NAME,
            "repository_url": UPSTREAM_REPOSITORY_URL,
            "project_url": UPSTREAM_PROJECT_URL,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "recorded_license": RECORDED_LICENSE,
            "recorded_role": RECORDED_ROLE,
            "recorded_time_stretch_stage_found":
                RECORDED_TIME_STRETCH_STAGE_FOUND,
            "recorded_hardware": RECORDED_HARDWARE,
            "recorded_geometry_asserted": False,
            "geometry_status": TASK_GEOMETRY_STATUS,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "rate_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_candidate_metrics": None,
            "note": (
                "Structural rate arithmetic and fail-closed controls pass, "
                "but no AudioTK source, actual time-stretch stage, rights-"
                "cleared cohort, pitch/transient/speech-preservation "
                "measurement, target runtime, listening or parity exists, so "
                "the rate profile is not satisfied for qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_streaming_separation_declared": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
            "time_stretch_not_performed": True,
            "adverse": control["adverse"],
            "adverse_all_rejected": all(
                item["result"] == "rejected" for item in control["adverse"]),
        },
        "gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "supporting_dsp_reuse": audit["observed"]["supporting_dsp_audit"],
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            MISSING_SOURCE_PATH,
            MISSING_CHECKOUT_PATH,
            RUNTIME_ENV_PATH,
            RUNTIME_LOCK_PATH,
            BUILD_RECORD_PATH,
            RIGHTS_RECORD_PATH,
            COHORT_MANIFEST_PATH,
            PARITY_MANIFEST_PATH,
            SUPPORTING_DSP_PLAN_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no AudioTK or audio runtime is imported.",
            "Fixed workspace paths are probed for source, build, runtime, rights, cohort and DSP-plan presence.",
            "No source checkout is built or executed and no artifact byte is downloaded.",
            "No network request, audio device, time-scale modification or timing run occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }


def build_contract() -> Dict[str, Any]:
    report = build_report()
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": report["qualification"],
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "task_row_identity": report["task_row_identity"],
        "scope": report["scope"],
        "boundary": report["boundary"],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_checkout": {
            "path": MISSING_SOURCE_PATH,
            "present": False,
            "repository_url": UPSTREAM_REPOSITORY_URL,
            "project_url": UPSTREAM_PROJECT_URL,
            "revision": None,
            "revision_pin_available": False,
            "recorded_license": RECORDED_LICENSE,
            "recorded_role": RECORDED_ROLE,
            "recorded_time_stretch_stage_found":
                RECORDED_TIME_STRETCH_STAGE_FOUND,
        },
        "upstream_identity": report["upstream_identity"],
        "asset_requirements": report["asset_requirements"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "exact_blockers": report["exact_blockers"],
        "gates": report["gates"],
        "rate_profile_requirements": [
            {
                "id": item["id"],
                "requirement": item["requirement"],
                "package_status": item["package_status"],
            }
            for item in report["rate_profile"]["required_items"]
        ],
        "supporting_dsp_reuse": report["supporting_dsp_reuse"],
        "missing_historical_artifacts": report["missing_historical_artifacts"],
        "reproduction": {
            "report_sha256_sidecar": "report.json.sha256",
            "sources_manifest": "SOURCES.sha256",
            "cold_start_regenerations": 3,
            "command": "python3 run.py all",
            "verify": "python3 verify.py",
            "tests": "python3 -m unittest -v test_reference.py",
        },
        "licensing": {
            "copyright": "2026 Tsakanyan Hovhannes",
            "license": "Apache-2.0",
            "reported_upstream_license": RECORDED_LICENSE,
            "upstream_license_verified": False,
            "json_sidecars": True,
        },
    }


def canonical_contract_bytes() -> bytes:
    return canonical_bytes(build_contract()) + b"\n"
