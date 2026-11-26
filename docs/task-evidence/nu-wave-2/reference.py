# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-NU-WAVE-2.

The exact licensed NU-Wave 2 source, inference weights and runtime are absent.
The merged research evidence names the official implementation at
https://github.com/maum-ai/nuwave2 and the Interspeech 2022 paper, and it records
a bandwidth-conditioned generative family that targets different input rates
and generates 48 kHz audio. No source checkout, resolved 40-hex revision,
checkpoint digest, model card, runtime lock, licence grant, rights record,
band-limited/full-band cohort or parity vector exists in this workspace.

This module therefore never imports PyTorch, torch, NumPy, SoundFile, a vocoder
or any model runtime, never loads or executes a model, never reads or writes
real audio, never downloads anything and never measures a device clock. It
provides three bounded, verifiable pieces:

* a fail-closed source/asset audit over fixed workspace paths that records the
  absent source, revision, weights, runtime, licence and rights records and
  probes fixed paths for accidental assets;
* a caller-supplied-asset manifest contract validated without execution, with
  every malformed, missing, invalid or nonfinite control rejected before use;
* a deterministic synthetic bandwidth-extension accounting control that checks
  PCM validity, exact duration conservation, declared cutoff/bandwidth metadata
  and output peak bounds without performing or asserting any upsampling,
  generated-band reconstruction or model inference.

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

TASK = "SDK-NU-WAVE-2"
TITLE = "NU-Wave 2"
SLUG = "nu-wave-2"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "feb342c735740f32d64a668cf2234e488cdcdbfe"
BRANCH = "swarm/SDK-NU-WAVE-2"
REVIEWER = "reviewer-NU-WAVE-2"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-NU-WAVE-2")
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "restoration"
MODE = "feasibility"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_provider_intake"

# Exact upstream identity recorded by the merged research evidence.  The
# implementation URL and paper URL are recorded, but no resolved 40-hex
# revision exists, so none is invented here.
UPSTREAM_NAME = "NU-Wave 2"
UPSTREAM_REPO_URL = "https://github.com/maum-ai/nuwave2"
UPSTREAM_PAPER_URL = (
    "https://www.isca-archive.org/interspeech_2022/han22_interspeech.pdf")
UPSTREAM_REVISION: Optional[str] = None
SOURCE_REVISION_PIN_AVAILABLE = False
REPORTED_METHOD = "bandwidth_conditioned_generative_upsampling"
REPORTED_HARDWARE = "not_recorded_in_merged_evidence"
REPORTED_OUTPUT_SAMPLE_RATE_HZ = 48000
REPORTED_INPUT_RATE_DESCRIPTION = (
    "different input rates are described; no exact input-rate set is recorded")
REPORTED_BAND_DESCRIPTION = (
    "generated 48 kHz output is described; no cutoff, band or generated-band "
    "fidelity figure is recorded")
TASK_GEOMETRY_STATUS = "unestablished"

# Control geometry is the public SDK v0 input boundary plus a declared
# bandwidth-extension accounting output rate.  It is not asserted NU-Wave 2
# geometry and no upsampling or signal reconstruction happens.
CONTROL_SAMPLE_RATE_HZ = 16000
CONTROL_OUTPUT_SAMPLE_RATE_HZ = 48000
CONTROL_CUTOFF_HZ = 3500
CONTROL_SECONDS = 3
CONTROL_SOURCE_SAMPLES = CONTROL_SAMPLE_RATE_HZ * CONTROL_SECONDS
CONTROL_OUTPUT_SAMPLES = CONTROL_OUTPUT_SAMPLE_RATE_HZ * CONTROL_SECONDS
CHANNELS = 1
SDK_FRAME_SAMPLES = 160

# Fixed workspace paths used for the audit.  Absence is recorded, not filled.
RIGHTS_RECORD_PATH = "data/rights/nu-wave-2-rights.json"
COHORT_MANIFEST_PATH = "data/runs/nu-wave-2-bwe-cohort/manifest.json"
DEGRADATION_MANIFEST_PATH = "data/runs/nu-wave-2-bwe-cohort/degradation.json"
PARITY_MANIFEST_PATH = "data/runs/nu-wave-2-parity/manifest.json"
RUNTIME_ENV_PATH = "data/envs/nu-wave-2"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
MISSING_SOURCE_PATH = "research/voice-enhancement-20261101/repos/nuwave2"
MISSING_WEIGHTS_PATH = "data/models/nu-wave-2"

# Fixed absence probes.  Every probe must stay absent; any appearance forces a
# re-evaluation instead of silently promoting the candidate.
ABSENCE_PROBES: Tuple[str, ...] = (
    "research/voice-enhancement-20261101/repos/nuwave2",
    "research/voice-enhancement-20261101/repos/nu-wave-2",
    "research/voice-enhancement-20261101/repos/NU-Wave2",
    "research/voice-enhancement-20261101/hf-cache/models--nuwave2",
    "research/voice-enhancement-20261101/hf-cache/hub/models--nuwave2",
    "data/checkouts/nuwave2",
    "data/checkouts/nu-wave-2",
    "data/models/nuwave2",
    "data/models/nu-wave-2",
    "data/weights/nuwave2",
    "data/envs/nu-wave-2",
    "data/envs/nu-wave-2/requirements.lock",
    "data/rights/nu-wave-2-rights.json",
    "data/runs/nu-wave-2-bwe-cohort/manifest.json",
    "data/runs/nu-wave-2-bwe-cohort/degradation.json",
    "data/runs/nu-wave-2-parity/manifest.json",
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
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/distortion_restoration_20261028.md":
        "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
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
    "docs/task-evidence/survey-rst-02/README.md":
        "e94e6074a9247ce07b06a283d048daf79cbcea26bed01a1d5b0a4420135d8384",
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
    "control_input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "control_output_sample_rate_hz": CONTROL_OUTPUT_SAMPLE_RATE_HZ,
    "control_cutoff_hz": CONTROL_CUTOFF_HZ,
    "control_channels": CHANNELS,
    "control_sample_format": "f32",
    "control_mode": "offline_whole_utterance_bandwidth_extension_accounting",
    "control_incremental_streaming": False,
    "control_performs_bandwidth_extension": False,
    "control_artifact_latency_measured": False,
    "reported_output_sample_rate_hz": REPORTED_OUTPUT_SAMPLE_RATE_HZ,
    "reported_input_rate_description": REPORTED_INPUT_RATE_DESCRIPTION,
    "reported_band_description": REPORTED_BAND_DESCRIPTION,
    "reported_geometry_asserted": False,
    "generated_band_is_estimate": True,
    "resampling_is_not_bandwidth_extension": True,
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
    "bandwidth_extension_performed": False,
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "real_nu_wave_2_model": False,
    "release_claim": False,
    "runtime_invoked": False,
    "super_resolution_performed": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No NU-Wave 2 source, checkpoint, generative upsampling model or configuration is loaded or executed.",
    "No PyTorch, torch, NumPy, SoundFile, vocoder or neural runtime is imported.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, degradation trace or clean high-band reference is consumed.",
    "No bandwidth-extension output, generated-band fidelity, content preservation, SI-SDR, STOI, MOS, artifact latency, memory or RTF is measured here.",
    "The synthetic bandwidth-extension accounting control performs no upsampling and is never model output.",
    "The sibling survey-rst-02 map, the classical spectrum-copy pilot, the AudioSR/Vocos-BWE/VM-ASR rows and the resampling boundary are provenance only and are not attributed to NU-Wave 2.",
    "The source-reported different-input-rate and 48 kHz output description is provenance only, not an established task geometry.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "source_checkout",
        "recorded_url": UPSTREAM_REPO_URL,
        "path": MISSING_SOURCE_PATH,
        "revision": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "upstream_revision",
        "recorded_url": UPSTREAM_REPO_URL,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "inference_weights",
        "path": MISSING_WEIGHTS_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "model_card_and_config",
        "path": MISSING_WEIGHTS_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
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
        "required": True,
        "status": "absent",
    },
    {
        "id": "rights_record",
        "path": RIGHTS_RECORD_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "restoration_cohort",
        "path": COHORT_MANIFEST_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "degradation_and_parity_manifest",
        "degradation_path": DEGRADATION_MANIFEST_PATH,
        "parity_path": PARITY_MANIFEST_PATH,
        "required": True,
        "status": "absent",
    },
)

CALLER_ASSET_FIELDS = (
    "checkpoint_path",
    "checkpoint_sha256",
    "channels",
    "cohort_manifest_path",
    "cohort_manifest_sha256",
    "config_path",
    "config_sha256",
    "degradation_manifest_path",
    "degradation_manifest_sha256",
    "input_cutoff_hz",
    "input_sample_rate_hz",
    "license_record_path",
    "license_record_sha256",
    "model_card_path",
    "model_card_sha256",
    "output_sample_rate_hz",
    "parity_vector_path",
    "parity_vector_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "source_checkout_path",
    "source_revision",
    "variant",
)

CALLER_FILE_PAIRS = (
    ("checkpoint_path", "checkpoint_sha256"),
    ("config_path", "config_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("model_card_path", "model_card_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("cohort_manifest_path", "cohort_manifest_sha256"),
    ("degradation_manifest_path", "degradation_manifest_sha256"),
    ("parity_vector_path", "parity_vector_sha256"),
)
CALLER_DIR_FIELDS = ("source_checkout_path", "runtime_path")
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_VARIANT = "offline_whole_utterance_bandwidth_extension"
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000
MIN_CUTOFF_HZ = 1000

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/nu-wave-2/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_revision_shape_declared_bandwidth_"
        "and_offline_variant_only; do_not_import_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_source_revision": UPSTREAM_REVISION,
    "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
    "required_geometry": {
        "channels": CHANNELS,
        "input_sample_rate_hz": None,
        "output_sample_rate_hz": None,
        "input_cutoff_hz": None,
        "status": TASK_GEOMETRY_STATUS,
    },
    "notes": (
        "Every checkpoint, config, model card, licence, rights record, runtime "
        "lock, cohort manifest, degradation manifest and parity vector must "
        "exist at an absolute path and match its declared SHA-256 before a "
        "caller may process audio. No upstream revision is pinned because the "
        "merged evidence records only implementation and paper URLs."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "source_checkout_absent",
        "state": "absent",
        "requirement": (
            "Supply the NU-Wave 2 source checkout at an immutable 40-hex "
            "revision under research/voice-enhancement-20261101/repos/nuwave2 "
            "or data/checkouts/nuwave2; no checkout exists in the workspace."),
    },
    {
        "id": "upstream_revision_unpinned",
        "state": "absent",
        "requirement": (
            "Resolve https://github.com/maum-ai/nuwave2 to a full 40-hex "
            "commit and publish its per-file SHA-256 manifest; the merged "
            "evidence records only implementation and paper URLs."),
    },
    {
        "id": "inference_weights_absent",
        "state": "absent",
        "requirement": (
            "Supply the exact generator checkpoint, any auxiliary model, and "
            "the model configuration with byte counts and SHA-256 values at "
            "one immutable revision; no weight was downloaded or identified "
            "by digest in the merged evidence."),
    },
    {
        "id": "task_geometry_unestablished",
        "state": "absent",
        "requirement": (
            "Record the exact accepted input rates, input bandwidth/cutoff, "
            "output rate and band, channels, duration limits, padding/crop "
            "recipe and any resampling in a pinned config; the merged evidence "
            "only describes different input rates and a generated 48 kHz "
            "output, which is not an established task geometry."),
    },
    {
        "id": "runtime_absent",
        "state": "absent",
        "requirement": (
            "Provide an isolated hash-pinned runtime with a complete lock at "
            "data/envs/nu-wave-2/requirements.lock and a recorded platform; no "
            "environment, package pin or lock exists."),
    },
    {
        "id": "source_license_unverified",
        "state": "absent",
        "requirement": (
            "Add the upstream artifact licence and terms at the resolved "
            "commit, including checkpoint redistribution; no licence file, "
            "terms statement or redistribution grant is recorded in the "
            "merged evidence or present in the workspace."),
    },
    {
        "id": "rights_and_cohort_uncleared",
        "state": "absent",
        "requirement": (
            "Clear weights, training-data, source-audio, clean high-band "
            "reference, output-use and redistribution rights, then freeze a "
            "rights-cleared paired band-limited/full-band speech cohort with "
            "bandwidth strata; only research-listed sibling material exists."),
    },
    {
        "id": "artifact_latency_and_band_fidelity_absent",
        "state": "absent",
        "requirement": (
            "Produce one approved exact-runtime NU-Wave 2 output on a frozen "
            "caller input plus high-band/generated-band fidelity, content "
            "preservation, artifact latency and independent listening results; "
            "no local output, timing, benchmark or parity vector exists."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_asset_identity",
        "The full 40-hex source revision, checkpoint, config, model card and "
        "metadata SHA-256 values and the source licence match exact pins.",
    ),
    (
        "runtime_admission",
        "An isolated hash-pinned runtime with a complete lock is admitted on a "
        "recorded platform and its artifact latency is measured for the exact "
        "input/output geometry.",
    ),
    (
        "artifact_rights_and_licence",
        "Source, weight, training-data, source-audio, clean-reference, "
        "output-use and redistribution rights are cleared with notices.",
    ),
    (
        "exact_reference_parity",
        "An approved exact-runtime NU-Wave 2 output matches the reference on a "
        "frozen caller-supplied input for one frozen configuration.",
    ),
    (
        "bandwidth_and_generated_band_evidence",
        "A rights-cleared held-out cohort scores bandwidth, generated-band "
        "fidelity, content preservation and intelligibility or listening as "
        "separate outcomes.",
    ),
    (
        "task_scope_and_geometry",
        "Input rates, input cutoff, output rate and band, channels, duration "
        "and padding geometry are established and the candidate is not "
        "misrepresented as a conventional resampler or a voice-only enhancer.",
    ),
    (
        "opt_in_provider_intake",
        "Explicit opt-in provider intake, licence review, descriptor review and "
        "an independent public-surface decision are complete.",
    ),
    (
        "public_default_and_release",
        "Explicit default selection, resource/deadline evidence and release or "
        "public-benchmark approval are recorded; this package is off by default.",
    ),
)

RESTORATION_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "frozen_corruption_and_metadata",
        "Freeze the band-limiting corruption, cutoff, sample rates, channels "
        "and corresponding clean or full-band baseline.",
        "absent",
    ),
    (
        "matched_damaged_baseline",
        "Include the band-limited input identity and an established "
        "task-matched BWE baseline.",
        "absent",
    ),
    (
        "degradation_and_bandwidth_strata",
        "Stratify results by degradation, bandwidth and cutoff rather than "
        "pooling one condition.",
        "absent",
    ),
    (
        "discrete_validity_and_decoded_intervals",
        "Report validity, nonfinite failure and exact output intervals.",
        "synthetic_only",
    ),
    (
        "task_specific_quality",
        "Score generated-band fidelity and content preservation against "
        "permitted clean references.",
        "not_measured",
    ),
    (
        "output_peak_and_timing_bounds",
        "Bound output peaks, duration and content/availability timing, "
        "including artifact latency.",
        "structural_only",
    ),
    (
        "failure_and_control_results",
        "Record missing, invalid, nonfinite and adverse control results.",
        "structural_only",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "source_id": "S29",
    "sources_manifest": "research/category_survey/sources.md",
    "sources_manifest_sha256": SOURCE_PINS[
        "research/category_survey/sources.md"],
    "sources_manifest_line": 39,
    "research_note": "research/distortion_restoration_20261028.md",
    "research_note_sha256": SOURCE_PINS[
        "research/distortion_restoration_20261028.md"],
    "research_note_line": 43,
    "inventory_component": "nu-wave-2",
    "inventory_disposition": "sdk-model",
    "inventory_evidence_status": "considered",
    "inventory_plan_note": (
        "Stage exact weights and validate bandwidth, generated-band fidelity "
        "and artifact latency."),
    "implementation_url": UPSTREAM_REPO_URL,
    "paper_url": UPSTREAM_PAPER_URL,
    "reported_method": REPORTED_METHOD,
    "reported_hardware": REPORTED_HARDWARE,
    "reported_input_rate_description": REPORTED_INPUT_RATE_DESCRIPTION,
    "reported_band_description": REPORTED_BAND_DESCRIPTION,
    "reported_output_sample_rate_hz": REPORTED_OUTPUT_SAMPLE_RATE_HZ,
    "sibling_map": "docs/task-evidence/survey-rst-02/README.md",
    "sibling_map_sha256": BOUNDARY_PINS[
        "docs/task-evidence/survey-rst-02/README.md"],
    "sibling_map_line": 42,
    "sibling_gap": {
        "id": "G01",
        "actionable_gap": (
            "Stage NU-Wave 2 at an exact revision and checkpoint, then "
            "evaluate 48 kHz bandwidth extension against clean high-band "
            "references"),
        "evidence_gap": (
            "S29 is a direct project lead, but no pinned source, checkpoint "
            "digest, rights review, matched band-limited cohort, high-band "
            "fidelity or content-preservation result exists."),
        "follow_up_ids": ["SDK-NU-WAVE-2"],
    },
    "finding": (
        "The merged research note states that NU-Wave 2 is the strongest "
        "ready-to-investigate neural family for RST-02, that the authors "
        "provide official code and checkpoints, and that those weights are not "
        "staged locally. The note also states that different input rates and "
        "48 kHz generated audio are described and that generated bands are "
        "estimates needing explicit fidelity and preservation evaluation. No "
        "revision, checkpoint digest, licence, cohort or local output exists."),
    "sibling_context_not_attributed": [
        "The survey-rst-02 map records NU-Wave 2 as considered (G01) and "
        "supplies no NU-Wave 2 output, bandwidth or timing value.",
        "The 12-clip spectrum-copy pilot and its 3.5 kHz low-pass identity "
        "control are different classical proxies and are not NU-Wave 2 "
        "evidence.",
        "AudioSR, Vocos-BWE, VM-ASR, URGENT-family and Opus LACE/NoLACE "
        "observations are separate candidates and baselines, not NU-Wave 2 "
        "measurements.",
        "Resampling and rate-conversion tooling is adjacent only; changing the "
        "sample rate does not infer missing high-frequency content and is "
        "never counted as bandwidth extension here.",
        "Installed SDK v0 is 16 kHz mono f32 at 160 samples per frame and "
        "offers no exercised 48 kHz generative path.",
    ],
    "notes": (
        "No NU-Wave 2 output, checkpoint, implementation or runtime was "
        "acquired. No bandwidth, generated-band fidelity, SI-SDR, STOI, MOS, "
        "artifact latency, memory or RTF value is attributed to this "
        "candidate."),
}

MATCHED_PILOT_CONTEXT: Dict[str, Any] = {
    "label": "historical_pilot_provenance_not_reproduced",
    "source": "research/distortion_restoration_20261028.md",
    "source_sha256": SOURCE_PINS["research/distortion_restoration_20261028.md"],
    "cohort": (
        "12 EARS clips, zero-phase low-pass at 3.5 kHz, 16 kHz mono, at most "
        "4 s, compared with the clean full-band waveform"),
    "bandlimited_input_si_sdr_db": 17.4,
    "spectral_copy_si_sdr_db": 14.39,
    "spectral_copy_delta_db": -3.01,
    "stoi_values_recorded_in_pinned_note": False,
    "candidate_row_present": False,
    "candidate_output_present": False,
    "reproduced_here": False,
    "pooled_with_candidate": False,
    "admitted_as_result": False,
    "note": (
        "Pilot means are transcribed from the pinned research note as "
        "provenance only. They are not rerun, re-scored, pooled or inherited, "
        "and no row is NU-Wave 2. The primary source also warns that these are "
        "small pilot effects and that generated high bands still need explicit "
        "fidelity and preservation evaluation."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_bandwidth_extension_accounting_plan_"
    "not_model_output")

PCM_SAMPLE_CAP = 10_000_000

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
    "manifest_channels_zero",
    "manifest_rate_below_range",
    "manifest_output_rate_below_input",
    "manifest_cutoff_zero",
    "manifest_cutoff_above_nyquist",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
)

MAX_MANIFEST_BYTES = 8 * 1024 ** 3
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


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


# ---------------------------------------------------------------------------
# Source checkout, asset and absence audit.  Fixed local reads only.
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
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/nuwave2",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/nu-wave-2",
        SOURCE_ROOT / "data/checkouts/nuwave2",
        SOURCE_ROOT / "data/checkouts/nu-wave-2",
    ]


def _weights_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "data/models/nuwave2",
        SOURCE_ROOT / "data/models/nu-wave-2",
        SOURCE_ROOT / "data/weights/nuwave2",
        SOURCE_ROOT / (
            "research/voice-enhancement-20261101/repos/nuwave2/checkpoints"),
        SOURCE_ROOT / (
            "research/voice-enhancement-20261101/repos/nu-wave-2/checkpoints"),
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
    weight_paths = _weights_candidates()
    runtime_env = SOURCE_ROOT / RUNTIME_ENV_PATH
    runtime_lock = SOURCE_ROOT / RUNTIME_LOCK_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    parity_manifest = SOURCE_ROOT / PARITY_MANIFEST_PATH
    degradation_manifest = SOURCE_ROOT / DEGRADATION_MANIFEST_PATH
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
        "weights_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in weight_paths
        ],
        "weights_present": any(path.exists() for path in weight_paths),
        "runtime_env_present": runtime_env.is_dir(),
        "runtime_lock_present": runtime_lock.is_file(),
        "rights_record_present": rights_record.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "degradation_manifest_present": degradation_manifest.is_file(),
        "parity_manifest_present": parity_manifest.is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "reported_method": REPORTED_METHOD,
            "reported_hardware": REPORTED_HARDWARE,
            "geometry_status": TASK_GEOMETRY_STATUS,
            "control_input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_output_sample_rate_hz": CONTROL_OUTPUT_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
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
# Deterministic synthetic PCM and bandwidth-extension accounting.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_input_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x4E555741
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 37, 0.30) + 0.01 * noise)
    return samples


def synthetic_declared_output_pcm() -> List[float]:
    """A deterministic surrogate used only to exercise accounting.

    It is not produced by interpolation, upsampling, bandwidth extension or
    any model.
    """
    samples: List[float] = []
    state = 0x57415645
    for index in range(CONTROL_OUTPUT_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 41, 0.25) + 0.02 * noise)
    return samples


def validate_pcm(signal: Any, sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ,
                 channels: int = CHANNELS) -> List[float]:
    if sample_rate_hz not in (CONTROL_SAMPLE_RATE_HZ,
                              CONTROL_OUTPUT_SAMPLE_RATE_HZ):
        raise Reject("unsupported control sample rate")
    if channels != CHANNELS:
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


def pcm_summary(signal: Sequence[float], sample_rate_hz: int) -> Dict[str, Any]:
    values = validate_pcm(signal, sample_rate_hz)
    peak = max(abs(value) for value in values)
    return {
        "samples": len(values),
        "sample_rate_hz": sample_rate_hz,
        "channels": CHANNELS,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs": peak,
        "nonfinite_samples": 0,
        "sha256": sha256(canonical_bytes(list(values))),
    }


def bandwidth_ledger(input_rate_hz: int, output_rate_hz: int,
                     cutoff_hz: int) -> Dict[str, Any]:
    """Declared cutoff/bandwidth metadata only; no signal is reconstructed."""
    for name, value in (("input_rate_hz", input_rate_hz),
                        ("output_rate_hz", output_rate_hz),
                        ("cutoff_hz", cutoff_hz)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject(name + " must be an integer")
    if input_rate_hz < MIN_SAMPLE_RATE_HZ or input_rate_hz > MAX_SAMPLE_RATE_HZ:
        raise Reject("input sample rate is outside the admitted range")
    if output_rate_hz < input_rate_hz or output_rate_hz > MAX_SAMPLE_RATE_HZ:
        raise Reject("output sample rate must be at least the input rate")
    lower_nyquist = input_rate_hz // 2
    upper_nyquist = output_rate_hz // 2
    if cutoff_hz < MIN_CUTOFF_HZ or cutoff_hz >= lower_nyquist:
        raise Reject("cutoff must leave a missing input band")
    if cutoff_hz >= upper_nyquist:
        raise Reject("cutoff must be below the output Nyquist")
    return {
        "input_sample_rate_hz": input_rate_hz,
        "output_sample_rate_hz": output_rate_hz,
        "input_cutoff_hz": cutoff_hz,
        "input_nyquist_hz": lower_nyquist,
        "output_nyquist_hz": upper_nyquist,
        "missing_band_hz": [cutoff_hz, lower_nyquist],
        "declared_extended_band_hz": [lower_nyquist, upper_nyquist],
        "missing_band_width_hz": lower_nyquist - cutoff_hz,
        "declared_extended_band_width_hz": upper_nyquist - lower_nyquist,
        "generated_band_is_estimate": True,
        "signal_reconstructed": False,
        "artifact_latency_measured": False,
        "note": (
            "Declared metadata accounting only. No interpolation, upsampling, "
            "envelope extension, generative model or high-band reconstruction "
            "runs, and no artifact latency is measured."),
    }


def duration_conservation(input_samples: int, input_rate_hz: int,
                          output_samples: int, output_rate_hz: int
                          ) -> Dict[str, Any]:
    for name, value in (("input_samples", input_samples),
                        ("input_rate_hz", input_rate_hz),
                        ("output_samples", output_samples),
                        ("output_rate_hz", output_rate_hz)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject(name + " must be an integer")
        if value <= 0:
            raise Reject(name + " must be positive")
    if input_rate_hz not in (CONTROL_SAMPLE_RATE_HZ,
                             CONTROL_OUTPUT_SAMPLE_RATE_HZ):
        raise Reject("unsupported control input rate")
    if output_rate_hz not in (CONTROL_SAMPLE_RATE_HZ,
                              CONTROL_OUTPUT_SAMPLE_RATE_HZ):
        raise Reject("unsupported control output rate")
    source_duration = Fraction(input_samples, input_rate_hz)
    output_duration = Fraction(output_samples, output_rate_hz)
    ratio = output_duration / source_duration
    return {
        "input_duration_s": fraction_text(source_duration),
        "output_duration_s": fraction_text(output_duration),
        "duration_ratio": fraction_text(ratio),
        "duration_ratio_float": float(ratio),
        "duration_conserved": ratio == 1,
        "duration_ratio_interpretation": (
            "output_duration_divided_by_input_duration"),
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    good_input = synthetic_input_pcm()
    good_output = synthetic_declared_output_pcm()
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
    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_input, 8000)),
        ("pcm_stereo", lambda: validate_pcm(good_input, CONTROL_SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("checkpoint_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "checkpoint_path", "checkpoints/nuwave2.pt")),
        ("manifest_bad_sha", wrong("checkpoint_sha256", "ABC")),
        ("manifest_short_revision", wrong("source_revision", "7dae8a2")),
        ("manifest_nonhex_revision", wrong("source_revision", "g" * 40)),
        ("manifest_wrong_variant", wrong("variant", "incremental_streaming")),
        ("manifest_channels_zero", wrong("channels", 0)),
        ("manifest_rate_below_range", wrong("input_sample_rate_hz", 4000)),
        ("manifest_output_rate_below_input", wrong("output_sample_rate_hz", 8000)),
        ("manifest_cutoff_zero", wrong("input_cutoff_hz", 0)),
        ("manifest_cutoff_above_nyquist", wrong("input_cutoff_hz", 9000)),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, checkpoint_path=(
                "/nonexistent/nuwave2-checkpoints/checkpoint.pt")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, runtime_path=(
                "/nonexistent/nuwave2-checkpoints/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, checkpoint_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    good = pcm_summary(good_input, CONTROL_SAMPLE_RATE_HZ)
    good_out = pcm_summary(good_output, CONTROL_OUTPUT_SAMPLE_RATE_HZ)
    if good["samples"] != CONTROL_SOURCE_SAMPLES:
        raise Reject("synthetic input control mismatch")
    if good_out["samples"] != CONTROL_OUTPUT_SAMPLES:
        raise Reject("synthetic output control mismatch")
    return results


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It is only used to exercise fail-closed shape checks.  Validation reaches
    the missing-asset branch before any file is read.
    """

    root = "/nonexistent/nuwave2-evidence-fixture"
    digest = "0" * 64
    return {
        "channels": CHANNELS,
        "checkpoint_path": root + "/checkpoint.pt",
        "checkpoint_sha256": digest,
        "cohort_manifest_path": root + "/cohort.json",
        "cohort_manifest_sha256": digest,
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "degradation_manifest_path": root + "/degradation.json",
        "degradation_manifest_sha256": digest,
        "input_cutoff_hz": CONTROL_CUTOFF_HZ,
        "input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "license_record_path": root + "/license.json",
        "license_record_sha256": digest,
        "model_card_path": root + "/model-card.json",
        "model_card_sha256": digest,
        "output_sample_rate_hz": CONTROL_OUTPUT_SAMPLE_RATE_HZ,
        "parity_vector_path": root + "/parity.json",
        "parity_vector_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "runtime_path": root + "/runtime",
        "source_checkout_path": root + "/source",
        "source_revision": "0" * 40,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package.

    It exercises file hashing and directory checks without reading audio or
    loading a model.  Duplicate paths are allowed; each pair carries the real
    digest so a single corrupted digest reaches the SHA-256 mismatch branch.
    """

    assignments = {
        "checkpoint_path": HERE / "reference.py",
        "config_path": HERE / "README.md",
        "license_record_path": HERE / "verify.py",
        "model_card_path": HERE / "contract.json",
        "rights_record_path": HERE / "run.py",
        "runtime_lock_path": HERE / "test_reference.py",
        "cohort_manifest_path": HERE / "reference.py",
        "degradation_manifest_path": HERE / "run.py",
        "parity_vector_path": HERE / "README.md",
    }
    manifest: Dict[str, Any] = {
        "channels": CHANNELS,
        "runtime_path": str(SDK_ROOT),
        "input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "output_sample_rate_hz": CONTROL_OUTPUT_SAMPLE_RATE_HZ,
        "input_cutoff_hz": CONTROL_CUTOFF_HZ,
        "source_checkout_path": str(HERE),
        "source_revision": "a" * 40,
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


def _rate_value(manifest: Dict[str, Any], field: str) -> int:
    value = manifest[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject("manifest " + field + " must be an integer")
    if value < MIN_SAMPLE_RATE_HZ or value > MAX_SAMPLE_RATE_HZ:
        raise Reject("manifest " + field + " is outside the admitted range")
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
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
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
    channels = manifest["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise Reject("manifest channels must be an integer")
    if channels != CHANNELS:
        raise Reject("manifest channels mismatch")
    input_rate = _rate_value(manifest, "input_sample_rate_hz")
    output_rate = _rate_value(manifest, "output_sample_rate_hz")
    if output_rate < input_rate:
        raise Reject("manifest output rate must be at least the input rate")
    cutoff = manifest["input_cutoff_hz"]
    if isinstance(cutoff, bool) or not isinstance(cutoff, int):
        raise Reject("manifest input_cutoff_hz must be an integer")
    if cutoff < MIN_CUTOFF_HZ or cutoff >= input_rate // 2:
        raise Reject("manifest input_cutoff_hz must leave a missing band")
    if cutoff >= output_rate // 2:
        raise Reject("manifest input_cutoff_hz must be below output Nyquist")
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
        "input_sample_rate_hz": input_rate,
        "output_sample_rate_hz": output_rate,
        "input_cutoff_hz": cutoff,
        "channels": CHANNELS,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "model_executed": False,
    }


def build_control() -> Dict[str, Any]:
    source = synthetic_input_pcm()
    output = synthetic_declared_output_pcm()
    source_summary = pcm_summary(source, CONTROL_SAMPLE_RATE_HZ)
    output_summary = pcm_summary(output, CONTROL_OUTPUT_SAMPLE_RATE_HZ)
    ledger = bandwidth_ledger(CONTROL_SAMPLE_RATE_HZ,
                              CONTROL_OUTPUT_SAMPLE_RATE_HZ,
                              CONTROL_CUTOFF_HZ)
    duration = duration_conservation(
        len(source), CONTROL_SAMPLE_RATE_HZ,
        len(output), CONTROL_OUTPUT_SAMPLE_RATE_HZ)
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_output_sample_rate_hz": CONTROL_OUTPUT_SAMPLE_RATE_HZ,
            "control_cutoff_hz": CONTROL_CUTOFF_HZ,
            "control_channels": CHANNELS,
            "task_geometry_status": TASK_GEOMETRY_STATUS,
            "task_geometry_asserted": False,
            "mode": "offline_whole_utterance_bandwidth_extension_accounting",
            "incremental_streaming": False,
            "performs_bandwidth_extension": False,
            "artifact_latency_measured": False,
        },
        "input_pcm": source_summary,
        "declared_output_pcm": output_summary,
        "bandwidth": ledger,
        "duration": duration,
        "acceptance_outcomes": [
            {
                "id": "validity_and_nonfinite",
                "measured": False,
                "value": None,
                "reason": "synthetic validity control only; no model output",
            },
            {
                "id": "output_peak_bounds",
                "measured": False,
                "value": None,
                "reason": "synthetic peak bound only; no model output",
            },
            {
                "id": "duration_conservation",
                "measured": False,
                "value": None,
                "reason": "declared structural accounting only; no runtime",
            },
            {
                "id": "degradation_and_bandwidth_strata",
                "measured": False,
                "value": None,
                "reason": "one declared cutoff; no rights-cleared paired cohort",
            },
            {
                "id": "generated_band_fidelity",
                "measured": False,
                "value": None,
                "reason": "no clean high-band reference or generated output",
            },
            {
                "id": "content_preservation",
                "measured": False,
                "value": None,
                "reason": "no clean reference, scorer or model output",
            },
            {
                "id": "intelligibility_or_listening",
                "measured": False,
                "value": None,
                "reason": "no authorized listening panel or speech-content score",
            },
            {
                "id": "artifact_latency_and_memory",
                "measured": False,
                "value": None,
                "reason": "no runtime, device clock or memory measurement",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range",
                "pcm_wrong_rate", "pcm_stereo",
                "manifest_channels_zero", "manifest_rate_below_range",
                "manifest_output_rate_below_input", "manifest_cutoff_zero",
                "manifest_cutoff_above_nyquist"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "manifest_missing_field", "manifest_missing_asset",
                "manifest_missing_directory"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic bandwidth-extension accounting control only. It "
            "performs no interpolation, upsampling, bandwidth extension or "
            "model inference, is not NU-Wave 2 output, not real speech, not a "
            "quality, fidelity or latency result and cannot qualify the "
            "candidate."),
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
        and observed["weights_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["rights_record_present"]
        and observed["cohort_manifest_present"]
        and observed["degradation_manifest_present"]
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
        "weights_present": observed["weights_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "rights_record_present": observed["rights_record_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "degradation_manifest_present":
            observed["degradation_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No NU-Wave 2 source, revision, weight, model card, runtime, "
            "licence, rights record, cohort or parity vector was observed. "
            "Sibling survey and pilot material is not NU-Wave 2 evidence."),
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
        for item, requirement, status in RESTORATION_REQUIREMENTS
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
                "The NU-Wave 2 source checkout, full upstream revision, "
                "inference weights, model card, exact geometry and hash-pinned "
                "runtime are absent; no licence, rights record, rights-cleared "
                "paired band-limited/full-band cohort, degradation manifest, "
                "clean high-band reference, parity vector, generated-band "
                "fidelity, content-preservation, artifact-latency or local "
                "output evidence exists."),
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
            "repository_url": UPSTREAM_REPO_URL,
            "paper_url": UPSTREAM_PAPER_URL,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "reported_method": REPORTED_METHOD,
            "reported_hardware": REPORTED_HARDWARE,
            "reported_input_rate_description": REPORTED_INPUT_RATE_DESCRIPTION,
            "reported_band_description": REPORTED_BAND_DESCRIPTION,
            "reported_output_sample_rate_hz": REPORTED_OUTPUT_SAMPLE_RATE_HZ,
            "reported_geometry_asserted": False,
            "geometry_status": TASK_GEOMETRY_STATUS,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "restoration_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_model_metrics": None,
            "note": (
                "Structural accounting passes, but no real model, licensed "
                "reference set, degradation trace, rights-cleared cohort, "
                "target runtime or approved parity exists, so the restoration "
                "profile is not satisfied for qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_streaming_separation_declared": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
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
        "matched_pilot_context": MATCHED_PILOT_CONTEXT,
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            MISSING_SOURCE_PATH,
            MISSING_WEIGHTS_PATH,
            RUNTIME_ENV_PATH,
            RUNTIME_LOCK_PATH,
            DEGRADATION_MANIFEST_PATH,
            COHORT_MANIFEST_PATH,
            RIGHTS_RECORD_PATH,
            PARITY_MANIFEST_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model or audio runtime is imported.",
            "Fixed workspace paths are probed for source, weights, runtime, rights and cohort presence.",
            "No source checkout is executed and no weight byte is read.",
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
        "source_checkout": {
            "path": MISSING_SOURCE_PATH,
            "present": False,
            "repository_url": UPSTREAM_REPO_URL,
            "paper_url": UPSTREAM_PAPER_URL,
            "revision": None,
            "revision_pin_available": False,
        },
        "upstream_identity": report["upstream_identity"],
        "asset_requirements": report["asset_requirements"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "exact_blockers": report["exact_blockers"],
        "gates": report["gates"],
        "restoration_profile_requirements": [
            {
                "id": item["id"],
                "requirement": item["requirement"],
                "package_status": item["package_status"],
            }
            for item in report["restoration_profile"]["required_items"]
        ],
        "matched_pilot_context": report["matched_pilot_context"],
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
            "json_sidecars": True,
        },
    }


def canonical_contract_bytes() -> bytes:
    return canonical_bytes(build_contract()) + b"\n"
