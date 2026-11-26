# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-CLEARSCALE.

The task is a feasibility investigation for the inventory component
``clearscale`` under the ``rate`` acceptance profile. The merged research note
records only one decisive line: *"ClearScale -- abandoned open-source
predecessor of DIRAC; no usable current licence/status."* It records no current
project URL, repository, revision, licence text, distribution path, runtime,
geometry, weights, corpus, output or rights.

No ClearScale source checkout, binary, licence record, rights record,
hash-pinned runtime, rate geometry, parity vector, cohort or measured output
exists in this workspace. This module therefore never imports NumPy, SciPy,
PyTorch, torch, ONNX, a codec, a TSM library or a device API. It never loads or
executes a time-stretch implementation, never reads or writes real audio, never
downloads anything and never measures a device clock. It provides three
bounded, verifiable pieces:

* a fail-closed source/asset audit over fixed workspace paths that records the
  absent source, implementation artifact, runtime, licence, rights, cohort and
  parity records and probes fixed paths for accidental assets;
* a caller-supplied-asset manifest contract validated without execution, with
  every malformed, missing, invalid or nonfinite control rejected before use;
* a deterministic rational rate-accounting control that checks PCM validity,
  exact source/output mapping, rate-schedule contiguity, duration floor/ceil,
  the final partial window and the declared non-candidate status. It performs
  no time-scale modification, emits no candidate audio and asserts no quality.

Nothing in this package qualifies the candidate. The decision is ``DEFER``.
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

TASK = "SDK-CLEARSCALE"
TITLE = "ClearScale"
SLUG = "clearscale"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "38f502b8e67a4cfef7dd72425aae6b0044846aad"
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

# The merged evidence records no usable current candidate URL, repository or
# resolved revision for ClearScale. None is invented here.
UPSTREAM_NAME = "ClearScale (abandoned predecessor of DIRAC; no pinned candidate)"
UPSTREAM_PROJECT_URL: Optional[str] = None
UPSTREAM_REPO_URL: Optional[str] = None
UPSTREAM_REVISION: Optional[str] = None
SOURCE_REVISION_PIN_AVAILABLE = False
TASK_GEOMETRY_STATUS = "unestablished"
NEURAL_WEIGHTS_APPLICABLE = False

# Control geometry is exactly the public SDK v0 input boundary. The candidate
# time-scale geometry beyond that boundary is not established.
CONTROL_SAMPLE_RATE_HZ = 16000
CONTROL_SECONDS = 3
CONTROL_SOURCE_SAMPLES = CONTROL_SAMPLE_RATE_HZ * CONTROL_SECONDS
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
NS_PER_SAMPLE = 62_500
CONTROL_RATE_MIN = Fraction(1, 2)
CONTROL_RATE_MAX = Fraction(2, 1)

# Fixed workspace paths used for the audit. Absence is recorded, not filled.
MISSING_SOURCE_PATH = "research/tsm-followup-20261101/clearscale"
MISSING_IMPLEMENTATION_PATH = "data/checkouts/clearscale"
RUNTIME_ENV_PATH = "data/envs/clearscale"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
LICENSE_RECORD_PATH = "data/rights/clearscale-license.json"
RIGHTS_RECORD_PATH = "data/rights/clearscale-rights.json"
COHORT_MANIFEST_PATH = "data/runs/clearscale-cohort/manifest.json"
PARITY_MANIFEST_PATH = "data/runs/clearscale-parity/manifest.json"
OUTPUT_USE_GRANT_PATH = "data/rights/clearscale-output-use-grant.json"

# Fixed absence probes. Every probe must stay absent; any appearance forces a
# re-evaluation instead of silently promoting the candidate.
ABSENCE_PROBES: Tuple[str, ...] = (
    MISSING_SOURCE_PATH,
    "research/tsm-followup-20261101/clear-scale",
    "research/tsm-followup-20261101/clear_scale",
    "data/checkouts/clearscale",
    "data/checkouts/clear-scale",
    "data/checkouts/clear_scale",
    "data/checkouts/tsm-engines-20261101/clearscale",
    "data/checkouts/tsm-engines-20261101/clear-scale",
    "data/models/clearscale",
    "data/runtimes/clearscale",
    "data/runtimes/clear-scale",
    "adapters/clearscale",
    "adapters/clear-scale",
    "bindings/clearscale",
    "third_party/clearscale",
    "third_party/clear-scale",
    "vendor/clearscale",
    "vendor/clear-scale",
    RUNTIME_ENV_PATH,
    RUNTIME_LOCK_PATH,
    LICENSE_RECORD_PATH,
    RIGHTS_RECORD_PATH,
    OUTPUT_USE_GRANT_PATH,
    COHORT_MANIFEST_PATH,
    PARITY_MANIFEST_PATH,
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
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
}
SIBLING_PINS: Dict[str, str] = {
    "docs/task-evidence/soundtouch/report.json":
        "83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947",
    "docs/task-evidence/bungee-basic/report.json":
        "bb434059ae6c3d07e247d7568d1dad3aab9441194f3b57c54851df4298447f8b",
    "docs/task-evidence/bungee-pro/report.json":
        "b83afd7e1279270cf8d4a2852de231ae159da0e4324a6e1c148b016306d0ffe4",
    "docs/task-evidence/signalsmith-stretch/report.json":
        "e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231",
    "docs/task-evidence/d1-whole-clip-duration-planner/fixtures/report.json":
        "522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98",
    "docs/task-evidence/audiosr/report.json":
        "495a3f4fa230f60069c51b8215b1e1ff198db2f2d557b1bde5485bffa5d9fbb2",
    "docs/task-evidence/gtcrn-dns3-offline/report.json":
        "b4768c1ee3b6f9934c576496a9f224a7293edc2c09993b11892c03535b8557bd",
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

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "task_geometry_status": TASK_GEOMETRY_STATUS,
    "task_geometry_asserted": False,
    "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "control_channels": CHANNELS,
    "control_sample_format": "f32",
    "control_frame_samples": SDK_FRAME_SAMPLES,
    "control_mode": "rational_rate_accounting",
    "control_performs_time_stretch": False,
    "control_performs_model_inference": False,
    "control_uses_declared_rate_schedules": True,
    "control_output_is_candidate_audio": False,
    "control_is_quality_result": False,
    "control_incremental_streaming": False,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "abi_change": False,
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "model_loaded": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "sdk_callback_invoked": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "audio_read": False,
    "audio_written": False,
    "device_timing": False,
    "implementation_executed": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "time_stretch_performed": False,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No ClearScale source, binary, coefficient table or configuration is loaded or executed.",
    "No NumPy, SciPy, PyTorch, torch, ONNX, CUDA, SoundFile, TSM library or device API is imported.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, consent record, clean reference or listening result is consumed.",
    "No duration, pitch, transient, buffering, rebuffer, drift, speech preservation, SI-SDR, STOI, WER, MOS, latency, memory or RTF is measured here.",
    "The synthetic rational rate-accounting control performs no time-scale modification and is never candidate audio.",
    "The ClearScale research note records an abandoned project with no usable current licence or status; it supplies no source, binary, rights or result.",
    "Adjacent SoundTouch, Bungee, Signalsmith, D1, AudioSR and GTCRN packages are not ClearScale and are not used as parity oracles.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "source_checkout",
        "path": MISSING_SOURCE_PATH,
        "revision": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "upstream_revision",
        "recorded_url": None,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "implementation_artifact",
        "path": MISSING_IMPLEMENTATION_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "ClearScale is a DSP time-stretch library, not a neural model; no "
            "neural weight is applicable. The exact licensed source or binary "
            "implementation and any coefficient table it needs are required."),
        "neural_weights_applicable": NEURAL_WEIGHTS_APPLICABLE,
    },
    {
        "id": "exact_runtime",
        "path": RUNTIME_ENV_PATH,
        "runtime_lock_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "source_license_record",
        "path": LICENSE_RECORD_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "rights_and_output_use",
        "path": RIGHTS_RECORD_PATH,
        "output_use_grant_path": OUTPUT_USE_GRANT_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "cohort_and_parity",
        "cohort_path": COHORT_MANIFEST_PATH,
        "parity_path": PARITY_MANIFEST_PATH,
        "required": True,
        "status": "absent",
    },
)

CALLER_ASSET_FIELDS = (
    "source_path",
    "source_revision",
    "implementation_path",
    "implementation_sha256",
    "config_path",
    "config_sha256",
    "runtime_path",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "license_record_path",
    "license_record_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "cohort_manifest_path",
    "cohort_manifest_sha256",
    "parity_vector_path",
    "parity_vector_sha256",
    "output_use_grant_path",
    "output_use_grant_sha256",
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "variant",
)

CALLER_FILE_PAIRS = (
    ("implementation_path", "implementation_sha256"),
    ("config_path", "config_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("cohort_manifest_path", "cohort_manifest_sha256"),
    ("parity_vector_path", "parity_vector_sha256"),
    ("output_use_grant_path", "output_use_grant_sha256"),
)
CALLER_DIR_FIELDS = ("source_path", "runtime_path")
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_VARIANT = "clearscale_pinned_time_scale_modification"

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/clearscale/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_revision_geometry_rights_and_variant_"
        "only; do_not_import_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_source_revision": UPSTREAM_REVISION,
    "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
    "required_geometry": {
        "channels": CHANNELS,
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "frame_samples": SDK_FRAME_SAMPLES,
        "status": (
            "exact_input_boundary_only; candidate rate semantics, buffering, "
            "content delay and final-padding geometry unestablished"),
    },
    "neural_weights_required": False,
    "license_record_required": True,
    "rights_record_required": True,
    "output_use_grant_required": True,
    "notes": (
        "Every implementation artifact, config, licence, rights record, cohort "
        "manifest, parity vector, runtime lock and output-use grant must exist "
        "at an absolute path and match its declared SHA-256 before a caller "
        "may process audio. No upstream revision is pinned because the merged "
        "evidence records only an abandoned project with no usable current "
        "licence or status. This package does not import or execute the asset."),
}

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_asset_identity",
        "The full 40-hex source revision, exact source/binary implementation, "
        "coefficient tables and metadata SHA-256 values and the source licence "
        "match exact pins.",
    ),
    (
        "runtime_admission",
        "An isolated hash-pinned runtime with a complete lock is admitted on a "
        "recorded platform, including the exact compiler, link mode and "
        "instruction-set assumptions.",
    ),
    (
        "artifact_rights_and_licence",
        "The abandoned-project status, copyright ownership, source and binary "
        "licence, redistribution, derivative-output use, patent status and "
        "commercial-use rights are cleared with notices and an output-use grant.",
    ),
    (
        "task_geometry_and_rate_semantics",
        "The exact sample rate, channels, frame/hop, rate-factor and pitch "
        "semantics, rate-change behavior, content delay, latency, final-padding "
        "rule and reset behavior are pinned in one immutable configuration.",
    ),
    (
        "rate_cohort_and_scoring",
        "A rights-cleared held-out rate cohort scores 1x, rate changes, "
        "unfamiliar speech, music, silence, rebuffer, drift and the final "
        "partial window with stratified controls and failure cases.",
    ),
    (
        "quality_and_playback_timing",
        "Paired or unpaired evidence separates duration mapping, pitch, "
        "transient audibility and speech preservation from output peaks, "
        "nonfinite failures, alignment and authorized listening; target-device "
        "pacing, fill/flush, deadlines and resource use are measured separately.",
    ),
    (
        "opt_in_provider_intake",
        "Explicit opt-in provider intake, licence review, descriptor review and "
        "an independent public-surface decision are complete; the component "
        "ships optional only.",
    ),
    (
        "public_default_and_release",
        "Explicit default selection, resource/deadline evidence and release or "
        "public-benchmark approval are recorded; this package is off by default.",
    ),
)

EXACT_BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "clearscale_source_absent",
        "artifact_id": "A01",
        "state": "absent",
        "requirement": (
            "Supply one exact ClearScale source checkout at an immutable 40-hex "
            "revision under research/tsm-followup-20261101/clearscale or "
            "data/checkouts/clearscale; no such checkout exists in the "
            "workspace and the merged note records an abandoned project."),
    },
    {
        "id": "clearscale_license_and_status_unusable",
        "artifact_id": "A05",
        "state": "absent",
        "requirement": (
            "Provide a current, reviewed licence and project-status record for "
            "the exact artifact: copyright ownership, source and binary terms, "
            "redistribution, derivative-output use, patent status and "
            "commercial-use permission. The note records no usable current "
            "licence or status, so no rights can be assumed."),
    },
    {
        "id": "implementation_artifact_absent",
        "artifact_id": "A03",
        "state": "absent",
        "requirement": (
            "Supply the exact licensed source or binary implementation with "
            "byte counts and SHA-256 values, plus any coefficient table it "
            "requires. ClearScale is a DSP library, not a neural model; no "
            "neural weight exists to substitute."),
    },
    {
        "id": "task_geometry_unestablished",
        "artifact_id": "A04",
        "state": "absent",
        "requirement": (
            "Record the exact sample rate, channels, frame/hop, rate-factor "
            "and pitch semantics, rate-change bounds, content delay, latency, "
            "final-padding rule and reset behavior in a pinned config; the "
            "merged note contains no ClearScale geometry or API."),
    },
    {
        "id": "runtime_absent",
        "artifact_id": "A06",
        "state": "absent",
        "requirement": (
            "Provide an isolated hash-pinned runtime with a complete lock at "
            "data/envs/clearscale/requirements.lock and a recorded platform; "
            "no environment, package pin or lock exists."),
    },
    {
        "id": "rights_and_output_use_uncleared",
        "artifact_id": "A07",
        "state": "absent",
        "requirement": (
            "Clear source, binary, training/coefficient, contributor, corpus, "
            "speaker-consent, source-audio, output-use and redistribution "
            "rights, then add the rights record and output-use grant; no "
            "rights record exists and the project status is abandoned."),
    },
    {
        "id": "cohort_and_parity_absent",
        "artifact_id": "A08",
        "state": "absent",
        "requirement": (
            "Produce one approved exact-runtime 1x/rate-change output plus a "
            "rights-cleared held-out cohort and parity vector covering "
            "unfamiliar speech, music, silence, rebuffer, drift and the final "
            "partial window; no output, parity vector or cohort exists."),
    },
    {
        "id": "quality_timing_and_release_absent",
        "artifact_id": "A09",
        "state": "absent",
        "requirement": (
            "Measure pitch, transients, speech preservation, peaks, nonfinite "
            "failures, alignment, content delay, buffering, deadlines, memory "
            "and CPU, then complete opt-in intake and release review; no "
            "quality, listening, device-timing or release result exists."),
    },
)

RATE_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "source_output_mapping",
        "Measure exact source-sample to output-sample mapping, content delay "
        "and the final partial window for the intended frame path.",
        "structural_only",
    ),
    (
        "duration_and_error",
        "Measure output duration identity, floor/ceil error and cumulative "
        "drift for 1x and every supported rate factor.",
        "structural_only",
    ),
    (
        "pitch_and_transient_audibility",
        "Measure pitch preservation and transient audibility for 1x, rate "
        "changes, music and speech.",
        "not_measured",
    ),
    (
        "rate_case_coverage",
        "Include 1x, rate changes, unfamiliar speech, music, silence, rebuffer, "
        "drift and the final partial window.",
        "absent",
    ),
    (
        "source_timestamp_decisions",
        "Keep pause, filler and rate decisions tied to exact source timestamps "
        "rather than a separate wall clock.",
        "synthetic_only",
    ),
    (
        "speech_preservation",
        "Measure speech, consonant and intelligibility preservation for every "
        "rate decision.",
        "not_measured",
    ),
    (
        "playback_buffering_and_rebuffer",
        "Measure fill/flush, rebuffer, underrun and recoverable buffering on "
        "the intended playback path.",
        "absent",
    ),
    (
        "real_cohort",
        "Score a rights-cleared held-out cohort of unfamiliar speech, music and "
        "silence with matched controls and failures.",
        "absent",
    ),
    (
        "resource_and_device_timing",
        "Measure memory, CPU, deadlines and actual availability on the intended "
        "device and runtime.",
        "absent",
    ),
    (
        "authorized_listening",
        "Run authorized listening separately where permitted references exist; "
        "listening is not inferred from synthetic arithmetic.",
        "absent",
    ),
)

CONTROL_PLAN_PROVENANCE = (
    "cpp-library/pipeline-validation/playback-speed-candidates.md, sections 1, "
    "2.1 and 3.14; the note defines rate = output/input and lists ClearScale as "
    "an abandoned predecessor of DIRAC with no usable current licence/status. "
    "It supplies no ClearScale API, geometry, source, binary or result."
)

CONTROL_SCHEDULES: Tuple[Tuple[str, Tuple[Dict[str, Any], ...]], ...] = (
    (
        "identity_1x",
        ({"start": 0, "end": CONTROL_SOURCE_SAMPLES, "rate": "1"},),
    ),
    (
        "faster_3_2",
        ({"start": 0, "end": CONTROL_SOURCE_SAMPLES, "rate": "3/2"},),
    ),
    (
        "slower_2_3",
        ({"start": 0, "end": CONTROL_SOURCE_SAMPLES, "rate": "2/3"},),
    ),
    (
        "rate_change_1_3_2_2_3",
        (
            {"start": 0, "end": 16000, "rate": "1"},
            {"start": 16000, "end": 32000, "rate": "3/2"},
            {"start": 32000, "end": 48000, "rate": "2/3"},
        ),
    ),
    (
        "fractional_final_partial_7_4",
        ({"start": 0, "end": CONTROL_SOURCE_SAMPLES, "rate": "7/4"},),
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
    "pcm_short",
    "schedule_not_sequence",
    "schedule_none",
    "schedule_empty",
    "segment_not_object",
    "segment_missing_field",
    "segment_extra_field",
    "segment_bool_start",
    "segment_float_start",
    "segment_negative_start",
    "segment_zero_length",
    "segment_end_before_start",
    "segment_out_of_bounds",
    "segment_gap",
    "segment_overlap",
    "segment_unsorted",
    "segment_wrong_total",
    "rate_none",
    "rate_zero",
    "rate_negative",
    "rate_float_nan",
    "rate_float_inf",
    "rate_text_nan",
    "rate_text_inf",
    "rate_text_zero_denominator",
    "rate_text_nonnumeric",
    "rate_above_control_clamp",
    "rate_below_control_clamp",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_short_revision",
    "manifest_nonhex_revision",
    "manifest_wrong_variant",
    "manifest_wrong_rate",
    "manifest_wrong_channels",
    "manifest_wrong_frame_samples",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
)

MAX_MANIFEST_BYTES = 8 * 1024 ** 3
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
RATE_PATTERN = re.compile(r"^[0-9]+(?:/[0-9]+)?$")


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
                          separators=(",", ":"),
                          allow_nan=False).encode("utf-8")
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


# ---------------------------------------------------------------------------
# Source checkout, asset and absence audit. Fixed local reads only.
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
        SOURCE_ROOT / MISSING_SOURCE_PATH,
        SOURCE_ROOT / "research/tsm-followup-20261101/clear-scale",
        SOURCE_ROOT / "research/tsm-followup-20261101/clear_scale",
        SOURCE_ROOT / "data/checkouts/clearscale",
        SOURCE_ROOT / "data/checkouts/clear-scale",
        SOURCE_ROOT / "data/checkouts/tsm-engines-20261101/clearscale",
        SOURCE_ROOT / "vendor/clearscale",
    ]


def _implementation_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_IMPLEMENTATION_PATH,
        SOURCE_ROOT / "data/checkouts/clear-scale",
        SOURCE_ROOT / "data/models/clearscale",
        SOURCE_ROOT / "data/runtimes/clearscale",
        SOURCE_ROOT / "third_party/clearscale",
        SOURCE_ROOT / "vendor/clear-scale",
    ]


def probe_absence() -> List[Dict[str, Any]]:
    return [
        {"path": relative, "exists": (SOURCE_ROOT / relative).exists()}
        for relative in ABSENCE_PROBES
    ]


def audit_assets() -> Dict[str, Any]:
    source_paths = _source_candidates()
    present_sources = [path for path in source_paths if path.is_dir()]
    repository = present_sources[0] if present_sources else None
    revision = _read_git_head(repository) if repository is not None else None
    licenses = _license_candidates(repository) if repository is not None else []
    readme = repository / "README.md" if repository is not None else None
    readme_declares = False
    if readme is not None and readme.is_file():
        try:
            text = readme.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            text = ""
        readme_declares = ("license" in text or "licence" in text
                           or "copyright" in text)
    implementation_paths = _implementation_candidates()
    runtime_env = SOURCE_ROOT / RUNTIME_ENV_PATH
    runtime_lock = SOURCE_ROOT / RUNTIME_LOCK_PATH
    license_record = SOURCE_ROOT / LICENSE_RECORD_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    output_use_grant = SOURCE_ROOT / OUTPUT_USE_GRANT_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    parity_manifest = SOURCE_ROOT / PARITY_MANIFEST_PATH
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
        "license_files": licenses,
        "license_file_present": bool(licenses),
        "license_declared_in_readme": readme_declares,
        "implementation_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in implementation_paths
        ],
        "implementation_artifact_present": any(
            path.exists() for path in implementation_paths),
        "neural_weights_applicable": NEURAL_WEIGHTS_APPLICABLE,
        "runtime_env_present": runtime_env.is_dir(),
        "runtime_lock_present": runtime_lock.is_file(),
        "license_record_present": license_record.is_file(),
        "rights_record_present": rights_record.is_file(),
        "output_use_grant_present": output_use_grant.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "parity_manifest_present": parity_manifest.is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "geometry_status": TASK_GEOMETRY_STATUS,
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": SDK_FRAME_SAMPLES,
            "upstream_revision": UPSTREAM_REVISION,
            "pinned_candidate_source": False,
            "neural_weights_applicable": NEURAL_WEIGHTS_APPLICABLE,
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
# Deterministic synthetic PCM and rational rate accounting.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_input_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x434C5343
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 37, 0.30) + 0.01 * noise)
    return samples


def validate_pcm(signal: Any, sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ,
                 channels: int = CHANNELS,
                 expected_samples: Optional[int] = None) -> List[float]:
    if isinstance(sample_rate_hz, bool) or not isinstance(sample_rate_hz, int):
        raise Reject("sample rate must be an integer")
    if sample_rate_hz != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("unsupported control sample rate")
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise Reject("channels must be an integer")
    if channels != CHANNELS:
        raise Reject("unsupported control channel count")
    if expected_samples is not None and (
            isinstance(expected_samples, bool)
            or not isinstance(expected_samples, int)
            or expected_samples <= 0):
        raise Reject("expected sample count must be a positive integer")
    if not isinstance(signal, (list, tuple)):
        raise Reject("pcm must be a sequence")
    if not signal:
        raise Reject("pcm is empty")
    result: List[float] = []
    for value in signal:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Reject("pcm sample must be a number")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise Reject("pcm sample is non-finite")
        if numeric < -1.0 or numeric > 1.0:
            raise Reject("pcm sample is out of range")
        result.append(numeric)
    if expected_samples is not None and len(result) != expected_samples:
        raise Reject("pcm sample count mismatch")
    return result


def pcm_summary(signal: Sequence[float], sample_rate_hz: int) -> Dict[str, Any]:
    if sample_rate_hz != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("summary sample rate mismatch")
    count = len(signal)
    if count == 0:
        raise Reject("summary of empty pcm")
    peak = max(abs(value) for value in signal)
    minimum = min(signal)
    maximum = max(signal)
    mean_abs = sum(abs(value) for value in signal) / count
    return {
        "sample_count": count,
        "duration_ns": count * NS_PER_SAMPLE,
        "sample_rate_hz": sample_rate_hz,
        "channels": CHANNELS,
        "sample_format": "f32",
        "peak_abs": peak,
        "minimum": minimum,
        "maximum": maximum,
        "mean_abs": mean_abs,
        "finite": True,
        "in_range": True,
    }


def parse_rate(value: Any, minimum: Fraction = CONTROL_RATE_MIN,
               maximum: Fraction = CONTROL_RATE_MAX) -> Fraction:
    if isinstance(value, bool) or value is None:
        raise Reject("rate must be an integer or rational string")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise Reject("rate is non-finite")
        raise Reject("floating-point rate is not accepted; use a rational string")
    if isinstance(value, int):
        rate = Fraction(value, 1)
    elif isinstance(value, str):
        if not RATE_PATTERN.fullmatch(value):
            raise Reject("rate text is not a positive rational")
        try:
            rate = Fraction(value)
        except (ValueError, ZeroDivisionError) as error:
            raise Reject("rate text is not a valid rational") from error
    else:
        raise Reject("rate must be an integer or rational string")
    if rate <= 0:
        raise Reject("rate must be positive")
    if rate < minimum or rate > maximum:
        raise Reject("rate is outside the synthetic control clamp")
    return rate


def validate_rate_schedule(segments: Any,
                           source_samples: int = CONTROL_SOURCE_SAMPLES
                           ) -> List[Dict[str, Any]]:
    if isinstance(source_samples, bool) or not isinstance(source_samples, int):
        raise Reject("source sample count must be an integer")
    if source_samples <= 0:
        raise Reject("source sample count must be positive")
    if not isinstance(segments, (list, tuple)):
        raise Reject("rate schedule must be a sequence")
    if not segments:
        raise Reject("rate schedule is empty")
    checked: List[Dict[str, Any]] = []
    expected_start = 0
    for item in segments:
        if not isinstance(item, dict):
            raise Reject("schedule segment must be an object")
        if set(item) != {"start", "end", "rate"}:
            raise Reject("schedule segment fields must be start, end, rate")
        start = item["start"]
        end = item["end"]
        for field, value in (("start", start), ("end", end)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise Reject("schedule " + field + " must be an integer")
        if start < 0:
            raise Reject("schedule start must be non-negative")
        if end <= start:
            raise Reject("schedule end must be after start")
        if end > source_samples:
            raise Reject("schedule end exceeds the source length")
        if start != expected_start:
            raise Reject("rate schedule must be sorted and contiguous")
        rate = parse_rate(item["rate"])
        checked.append({"start": start, "end": end,
                        "rate": fraction_text(rate)})
        expected_start = end
    if expected_start != source_samples:
        raise Reject("rate schedule does not cover the source length")
    return checked


def rate_mapping(segments: Any,
                 source_samples: int = CONTROL_SOURCE_SAMPLES) -> Dict[str, Any]:
    checked = validate_rate_schedule(segments, source_samples)
    records: List[Dict[str, Any]] = []
    cumulative_source = 0
    cumulative_output = Fraction(0)
    for segment in checked:
        source_frames = segment["end"] - segment["start"]
        rate = Fraction(segment["rate"])
        exact_output = Fraction(source_frames, 1) / rate
        previous_output = cumulative_output
        cumulative_source += source_frames
        cumulative_output += exact_output
        floor_before = math.floor(previous_output)
        floor_after = math.floor(cumulative_output)
        ceil_before = math.ceil(previous_output)
        ceil_after = math.ceil(cumulative_output)
        records.append({
            "start_sample": segment["start"],
            "end_sample": segment["end"],
            "rate": fraction_text(rate),
            "source_samples": source_frames,
            "output_duration": fraction_text(exact_output),
            "output_samples_floor": floor_after - floor_before,
            "output_samples_ceil": ceil_after - ceil_before,
            "final_partial": exact_output.denominator != 1,
            "cumulative_output_duration": fraction_text(cumulative_output),
        })
    total_floor = math.floor(cumulative_output)
    total_ceil = math.ceil(cumulative_output)
    final_record = records[-1]
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "qualifies": False,
        "source_samples": cumulative_source,
        "source_mapping_contiguous": True,
        "output_duration": fraction_text(cumulative_output),
        "output_samples_floor": total_floor,
        "output_samples_ceil": total_ceil,
        "duration_identity": cumulative_output.denominator == 1,
        "cumulative_drift_samples": fraction_text(
            cumulative_output - total_floor),
        "final_partial_window": {
            "segment_index": len(records) - 1,
            "rate": final_record["rate"],
            "fractional_output": fraction_text(
                cumulative_output - math.floor(cumulative_output)),
            "partial": cumulative_output.denominator != 1,
        },
        "records": records,
        "performs_time_stretch": False,
        "output_is_candidate_audio": False,
        "note": (
            "Exact rational mapping arithmetic only. No waveform is stretched, "
            "no pitch or transient is measured and no candidate output exists."),
    }


def build_control() -> Dict[str, Any]:
    source = synthetic_input_pcm()
    source_summary = pcm_summary(source, CONTROL_SAMPLE_RATE_HZ)
    schedules = []
    for name, segments in CONTROL_SCHEDULES:
        schedules.append({
            "name": name,
            "mapping": rate_mapping(list(segments)),
        })
    adverse = run_adverse_controls()
    return {
        "executor": "absent",
        "implementation_executed": False,
        "model_executed": False,
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": SDK_FRAME_SAMPLES,
            "task_geometry_status": TASK_GEOMETRY_STATUS,
            "task_geometry_asserted": False,
            "mode": "rational_rate_accounting",
            "incremental_streaming": False,
            "performs_time_stretch": False,
            "performs_model_inference": False,
            "uses_declared_rate_schedules": True,
        },
        "input_pcm": source_summary,
        "rate_schedules": schedules,
        "adverse": adverse,
        "adverse_all_rejected": all(
            item["result"] == "rejected" for item in adverse),
        "adverse_case_count": len(adverse),
        "control_claims": {
            "exact_source_output_mapping": True,
            "duration_floor_ceil_arithmetic": True,
            "final_partial_window_arithmetic": True,
            "nonfinite_and_invalid_rejection": True,
            "adverse_case_rejection": True,
            "candidate_audio_produced": False,
            "pitch_measured": False,
            "transient_audibility_measured": False,
            "speech_preservation_measured": False,
            "playback_buffering_measured": False,
            "device_timing_measured": False,
            "listening_conducted": False,
            "qualification_effect": "none",
        },
        "note": (
            "The schedules are declared synthetic controls, not ClearScale "
            "behavior. The mapping checks exact rational arithmetic and the "
            "final partial window only; it does not qualify the candidate."),
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    good_input = synthetic_input_pcm()
    good_schedule = [dict(item) for item in CONTROL_SCHEDULES[0][1]]
    good_manifest = _shape_only_manifest()

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

    existing = _existing_file_manifest()
    total = len(good_input)
    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_input, 8000)),
        ("pcm_stereo", lambda: validate_pcm(good_input,
                                            CONTROL_SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("pcm_short", lambda: validate_pcm(
            good_input[:-1], expected_samples=total)),
        ("schedule_not_sequence", lambda: validate_rate_schedule(b"\x00")),
        ("schedule_none", lambda: validate_rate_schedule(None)),
        ("schedule_empty", lambda: validate_rate_schedule([])),
        ("segment_not_object", lambda: validate_rate_schedule([1])),
        ("segment_missing_field", lambda: validate_rate_schedule(
            [{"start": 0, "end": total}])),
        ("segment_extra_field", lambda: validate_rate_schedule(
            [{"start": 0, "end": total, "rate": "1", "extra": 1}])),
        ("segment_bool_start", lambda: validate_rate_schedule(
            [{"start": True, "end": total, "rate": "1"}])),
        ("segment_float_start", lambda: validate_rate_schedule(
            [{"start": 0.0, "end": total, "rate": "1"}])),
        ("segment_negative_start", lambda: validate_rate_schedule(
            [{"start": -1, "end": total, "rate": "1"}])),
        ("segment_zero_length", lambda: validate_rate_schedule(
            [{"start": 10, "end": 10, "rate": "1"}])),
        ("segment_end_before_start", lambda: validate_rate_schedule(
            [{"start": 10, "end": 9, "rate": "1"}])),
        ("segment_out_of_bounds", lambda: validate_rate_schedule(
            [{"start": 0, "end": total + 1, "rate": "1"}])),
        ("segment_gap", lambda: validate_rate_schedule(
            [{"start": 0, "end": 10, "rate": "1"},
             {"start": 11, "end": total, "rate": "1"}])),
        ("segment_overlap", lambda: validate_rate_schedule(
            [{"start": 0, "end": 20, "rate": "1"},
             {"start": 10, "end": total, "rate": "1"}])),
        ("segment_unsorted", lambda: validate_rate_schedule(
            [{"start": 10, "end": total, "rate": "1"},
             {"start": 0, "end": 10, "rate": "1"}])),
        ("segment_wrong_total", lambda: validate_rate_schedule(
            [{"start": 0, "end": total - 1, "rate": "1"}])),
        ("rate_none", lambda: parse_rate(None)),
        ("rate_zero", lambda: parse_rate("0")),
        ("rate_negative", lambda: parse_rate(-1)),
        ("rate_float_nan", lambda: parse_rate(math.nan)),
        ("rate_float_inf", lambda: parse_rate(math.inf)),
        ("rate_text_nan", lambda: parse_rate("NaN")),
        ("rate_text_inf", lambda: parse_rate("inf")),
        ("rate_text_zero_denominator", lambda: parse_rate("1/0")),
        ("rate_text_nonnumeric", lambda: parse_rate("fast")),
        ("rate_above_control_clamp", lambda: parse_rate("5/2")),
        ("rate_below_control_clamp", lambda: parse_rate("1/4")),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("rights_record_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "implementation_path", "lib/clearscale.bin")),
        ("manifest_bad_sha", wrong("implementation_sha256", "ABC")),
        ("manifest_short_revision", wrong("source_revision", "7dae8a2")),
        ("manifest_nonhex_revision", wrong("source_revision", "g" * 40)),
        ("manifest_wrong_variant", wrong("variant", "offline_batch_stretch")),
        ("manifest_wrong_rate", wrong("sample_rate_hz", 48000)),
        ("manifest_wrong_channels", wrong("channels", 2)),
        ("manifest_wrong_frame_samples", wrong("frame_samples", 512)),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, implementation_path=(
                "/nonexistent/clearscale-evidence/implementation.bin")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, runtime_path=(
                "/nonexistent/clearscale-evidence/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, implementation_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    if [item["case"] for item in results] != list(ADVERSE_CASE_IDS):
        raise Reject("adverse case order mismatch")
    if any(item["result"] != "rejected" for item in results):
        raise Reject("an adverse control was not rejected")
    if not good_schedule:
        raise Reject("control schedule is empty")
    return results


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It is only used to exercise fail-closed shape checks. Validation reaches
    the missing-asset branch before any file is read.
    """

    root = "/nonexistent/clearscale-evidence-fixture"
    digest = "0" * 64
    return {
        "source_path": root + "/source",
        "source_revision": "0" * 40,
        "implementation_path": root + "/implementation.bin",
        "implementation_sha256": digest,
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "runtime_path": root + "/runtime",
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "license_record_path": root + "/license.json",
        "license_record_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "cohort_manifest_path": root + "/cohort.json",
        "cohort_manifest_sha256": digest,
        "parity_vector_path": root + "/parity.json",
        "parity_vector_sha256": digest,
        "output_use_grant_path": root + "/output-use-grant.json",
        "output_use_grant_sha256": digest,
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package.

    It exercises file hashing and directory checks without reading audio or
    loading an implementation. Duplicate paths are allowed; each pair carries
    the real digest so a single corrupted digest reaches the mismatch branch.
    """

    assignments = {
        "implementation_path": HERE / "reference.py",
        "config_path": HERE / "README.md",
        "runtime_lock_path": HERE / "run.py",
        "license_record_path": HERE / "test_reference.py",
        "rights_record_path": HERE / "reference.py",
        "cohort_manifest_path": HERE / "run.py",
        "parity_vector_path": HERE / "test_reference.py",
        "output_use_grant_path": HERE / "reference.py",
    }
    manifest: Dict[str, Any] = {
        "source_path": str(HERE),
        "source_revision": "a" * 40,
        "runtime_path": str(SDK_ROOT),
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "variant": CALLER_VARIANT,
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = sha256(path.read_bytes())
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


def _int_field(manifest: Dict[str, Any], field: str) -> int:
    value = manifest[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject("manifest " + field + " must be an integer")
    return value


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
    for first, _ in CALLER_FILE_PAIRS:
        value = manifest[first]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + first + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + first + " must be absolute")
    for field in CALLER_DIR_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + field + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + field + " must be absolute")
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not COMMIT_PATTERN.fullmatch(revision):
        raise Reject("manifest source_revision must be a full 40-hex commit")
    sample_rate = _int_field(manifest, "sample_rate_hz")
    if sample_rate != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("manifest sample_rate_hz mismatch")
    channels = _int_field(manifest, "channels")
    if channels != CHANNELS:
        raise Reject("manifest channels mismatch")
    frame_samples = _int_field(manifest, "frame_samples")
    if frame_samples != SDK_FRAME_SAMPLES:
        raise Reject("manifest frame_samples mismatch")
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
        "channels": CHANNELS,
        "frame_samples": frame_samples,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "license_record_checked": True,
        "rights_record_checked": True,
        "output_use_grant_checked": True,
        "implementation_executed": False,
        "neural_weights_applicable": NEURAL_WEIGHTS_APPLICABLE,
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
        and observed["implementation_artifact_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["license_record_present"]
        and observed["rights_record_present"]
        and observed["output_use_grant_present"]
        and observed["cohort_manifest_present"]
        and observed["parity_manifest_present"])
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
        "implementation_artifact_present": observed[
            "implementation_artifact_present"],
        "neural_weights_applicable": NEURAL_WEIGHTS_APPLICABLE,
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "license_record_present": observed["license_record_present"],
        "rights_record_present": observed["rights_record_present"],
        "output_use_grant_present": observed["output_use_grant_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No ClearScale source, revision, implementation artifact, "
            "licence record, runtime, rights record, output-use grant, cohort "
            "or parity vector was observed. The merged note records an "
            "abandoned project with no usable current licence/status."),
    }


def _sibling_evidence() -> List[Dict[str, Any]]:
    return [
        {
            "id": "soundtouch",
            "path": "docs/task-evidence/soundtouch/report.json",
            "sha256": SIBLING_PINS[
                "docs/task-evidence/soundtouch/report.json"],
            "decision": "incomplete",
            "status": "proposal_only_not_qualified",
            "role": (
                "Adjacent synthetic WSOLA/TSM reference. It is not ClearScale, "
                "does not contain ClearScale output and cannot be a parity "
                "oracle for it."),
        },
        {
            "id": "bungee-basic",
            "path": "docs/task-evidence/bungee-basic/report.json",
            "sha256": SIBLING_PINS[
                "docs/task-evidence/bungee-basic/report.json"],
            "decision": "proposal_only",
            "status": "synthetic_rate_map_fixture",
            "role": (
                "Adjacent Bungee Basic rate-map fixture, synthetic only. It "
                "does not implement or measure ClearScale."),
        },
        {
            "id": "bungee-pro",
            "path": "docs/task-evidence/bungee-pro/report.json",
            "sha256": SIBLING_PINS[
                "docs/task-evidence/bungee-pro/report.json"],
            "decision": "DEFER",
            "status": "incomplete",
            "role": (
                "Adjacent commercial TSM blocker. Its proprietary artifact and "
                "rights findings do not transfer to ClearScale."),
        },
        {
            "id": "signalsmith-stretch",
            "path": "docs/task-evidence/signalsmith-stretch/report.json",
            "sha256": SIBLING_PINS[
                "docs/task-evidence/signalsmith-stretch/report.json"],
            "decision": "defer",
            "status": "synthetic-fixture-only",
            "role": (
                "Adjacent synthetic TSM reference. It is not ClearScale and "
                "supplies no ClearScale source, rights or result."),
        },
        {
            "id": "d1-whole-clip-duration-planner",
            "path": (
                "docs/task-evidence/d1-whole-clip-duration-planner/fixtures/"
                "report.json"),
            "sha256": SIBLING_PINS[
                "docs/task-evidence/d1-whole-clip-duration-planner/fixtures/"
                "report.json"],
            "decision": "proposal_only",
            "status": "opt-in synthetic developer-only offline proposal",
            "role": (
                "Adjacent whole-clip rate planner fixture. It neither executes "
                "nor qualifies ClearScale."),
        },
        {
            "id": "audiosr",
            "path": "docs/task-evidence/audiosr/report.json",
            "sha256": SIBLING_PINS[
                "docs/task-evidence/audiosr/report.json"],
            "decision": "DEFER",
            "status": "proposal_only_incomplete",
            "role": (
                "Diffusion restoration sibling. It is unrelated to rate/TSM, "
                "contains no ClearScale output and grants no rights."),
        },
        {
            "id": "gtcrn-dns3-offline",
            "path": "docs/task-evidence/gtcrn-dns3-offline/report.json",
            "sha256": SIBLING_PINS[
                "docs/task-evidence/gtcrn-dns3-offline/report.json"],
            "decision": "DEFER",
            "status": "proposal_only_synthetic_offline_incomplete",
            "role": (
                "Enhancement sibling. It is unrelated to rate/TSM and supplies "
                "no ClearScale evidence."),
        },
    ]


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = _asset_audit_summary()
    control = build_control()
    gates = [
        {"id": gate, "requirement": requirement, "status": "blocked",
         "qualifies": False}
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
                "No ClearScale source checkout, full upstream revision, "
                "licensed implementation artifact, exact rate geometry, "
                "hash-pinned runtime, licence record, rights record, "
                "output-use grant, rights-cleared cohort, parity vector or "
                "measured output exists. The merged note records only an "
                "abandoned project with no usable current licence/status."),
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
        "sibling_pins": dict(SIBLING_PINS),
        "upstream_identity": {
            "name": UPSTREAM_NAME,
            "project_url": UPSTREAM_PROJECT_URL,
            "repository_url": UPSTREAM_REPO_URL,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "geometry_status": TASK_GEOMETRY_STATUS,
            "pinned_candidate_source_present": False,
            "neural_weights_applicable": NEURAL_WEIGHTS_APPLICABLE,
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
            "real_implementation_metrics": None,
            "note": (
                "Only exact synthetic rational arithmetic passes. No candidate "
                "implementation, runtime, real cohort, rate/pitch/transient "
                "measurement, speech preservation, playback buffering, device "
                "timing or authorized listening exists, so the rate profile is "
                "not satisfied for qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "declared_rate_schedules_separated": True,
            "implementation_absent_and_not_executed": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
            "adverse": control["adverse"],
            "adverse_all_rejected": control["adverse_all_rejected"],
        },
        "gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": {
            "candidate_note": (
                "cpp-library/pipeline-validation/playback-speed-candidates.md"),
            "candidate_note_sha256": SOURCE_PINS[
                "cpp-library/pipeline-validation/playback-speed-candidates.md"],
            "candidate_status_quote": (
                "ClearScale \u2014 abandoned open-source predecessor of DIRAC; "
                "no usable current licence/status."),
            "dirac_context_quote": (
                "DIRAC \u2014 legacy name for the DSP Dimension technology; "
                "current licensing is through Zynaptiq (see 3.13). Old free "
                "binaries should not be adopted without checking their terms."),
            "is_benchmark_report": False,
            "source_reported_not_reexecuted": True,
            "interpretation": (
                "The note records no current project URL, repository, "
                "revision, licence text, distribution path, runtime, geometry, "
                "quality result or rights. It is provenance, not execution."),
        },
        "sibling_evidence": _sibling_evidence(),
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            MISSING_SOURCE_PATH,
            MISSING_IMPLEMENTATION_PATH,
            LICENSE_RECORD_PATH,
            RIGHTS_RECORD_PATH,
            OUTPUT_USE_GRANT_PATH,
            RUNTIME_ENV_PATH,
            RUNTIME_LOCK_PATH,
            COHORT_MANIFEST_PATH,
            PARITY_MANIFEST_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no TSM implementation, model, codec or audio runtime is imported.",
            "Fixed workspace paths are probed for source, implementation, runtime, licence, rights, cohort and parity presence.",
            "No source checkout is executed and no implementation byte is read.",
            "No network request, download, audio device, model load or timing run occurs.",
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
        "sibling_pins": dict(SIBLING_PINS),
        "source_checkout": {
            "path": MISSING_SOURCE_PATH,
            "present": False,
            "project_url": None,
            "repository_url": None,
            "revision": None,
            "revision_pin_available": False,
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
        "missing_historical_artifacts": report["missing_historical_artifacts"],
        "sibling_evidence": report["sibling_evidence"],
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
            "json_sidecars": True,
        },
    }


def canonical_contract_bytes() -> bytes:
    return canonical_bytes(build_contract()) + b"\n"
