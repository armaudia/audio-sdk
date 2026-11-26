# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-USC-MRATE.

The exact licensed USC SAIL mrate source, preprocessing runtime and approved
parity vector are not all available.  An extracted 2005 MATLAB delivery is
present under ``data/checkouts/mrate-usc-sail/rate`` with a stable file tree,
but its official archive copy is gone, it contains no license or terms file,
it targets MATLAB 7.01 on Windows XP, it requires SFS ``voc19`` and ESPS
``get_f0`` for preprocessing, and neither the MATLAB runtime nor the MCR
installer is available.

This module therefore does not port, execute or claim the USC algorithm.  It
provides two bounded, verifiable pieces:

* a fail-closed audit of the fixed source, rights, runtime, cohort and parity
  paths, with exact SHA-256 pins and a stable source-tree digest;
* a deterministic rate-profile contract control that maps a caller-supplied
  synthetic nucleus-score trace to exact 10 ms frame intervals, counts and
  syllable rates, and rejects missing, invalid and non-finite inputs.

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

TASK = "SDK-USC-MRATE"
TITLE = "USC mrate"
SLUG = "usc-mrate"
COMPONENT = "usc-mrate"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "2f4251b9abc92584b025f9b6ea665d9f3ec6e991"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-USC-MRATE"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

# Exact upstream identity recorded by the merged research packages.
ARCHIVE_URL = "https://sail.usc.edu/shri_files/SAIL-speechrate.zip"
ARCHIVE_SHA256 = (
    "9b08e76ee826dfcb351f4bd3339870b05a1e9f8e35fc3c829b3a4a496cce4a7b")
ARCHIVE_BYTES = None
ARCHIVE_REL = "data/checkouts/SAIL-speechrate.zip"
SOURCE_CHECKOUT_REL = "data/checkouts/mrate-usc-sail"
SOURCE_RATE_REL = SOURCE_CHECKOUT_REL + "/rate"
SOURCE_TREE_SHA256 = (
    "246fae3af23bdca2f2eb61e90bcf91c15598efcf014b193a4a96b96e01efb59f")
MATLAB_VERSION = "7.01"
TARGET_OS = "Windows XP SP2"
REQUIRED_TOOLS = ("SFS voc19", "ESPS get_f0")

# Exact file pins observed in the extracted delivery.  These establish local
# integrity only; they do not prove byte-equality with the absent archive.
OBSERVED_SOURCE_FILES: Tuple[Tuple[str, str], ...] = (
    ("doc/README",
     "bdf24448015379150ab84a8c765d4ed55a1f9b8998388c308b3af6cea20af79a"),
    ("example/sw2523A-ws97-i-0026.e19",
     "abf26fd3d08c8897ba516ee9c5531617252689367db282603c14e97d5ff1a1ea"),
    ("example/sw2523A-ws97-i-0026.pch",
     "f9cee1a904dfc48378c2000c237378749b82124820973286158ba992b71ea601"),
    ("example/sw2523A-ws97-i-0026.rat",
     "deb1483fb450ae4ca38d0ba308bfa3cf24d90ac931312f14a7cf2aa9f466e920"),
    ("example/sw2523A-ws97-i-0026.wav",
     "127328a48b3bf50d1ba9edef5b602b076d5c2c4b456499d316820fa304cd4ddc"),
    ("src/cell2str.m",
     "a90e6236b8e693951f9c082156dbcb18d805ef0b41317ed870d103b325e9cf04"),
    ("src/comp_result.m",
     "2b400e742c097a087b5cb94b690378ca956b5b7dd8e6049bf18c9bccb4c6dddb"),
    ("src/find_hist.m",
     "59030aee8673d5ec22eca0c24e218dd68bbc9400462b4d9879db66034dc1045c"),
    ("src/find_maxima_pitch.m",
     "c5d96614891c940dbe9f7dacbd3070471f011cda9d65ac7a729b20af6ccc44b7"),
    ("src/find_minimal.m",
     "76e784d8b4f360f054ad2e02c8d7decc4e11e38f20ad57c3dbb1e0be02263fd3"),
    ("src/gen_rand.m",
     "96cceb2e476601cd0578a06efe99e8ad69e9774511b3628d987e7716ba211f4c"),
    ("src/plot_result.m",
     "4a928057016f68e102b90495341071f41efe545e04cd05766273b364725fb819"),
    ("src/proc_eng_track.m",
     "eadfe4493b112023cffac782917767e891996478ffb0ae2e29f45be5377edd4c"),
    ("src/save_data.m",
     "9747ffdf2594d3fab947788e476e67aa815965f156f67491d0b396e4ace321d1"),
    ("src/set_para.m",
     "71194d0e83dc2f0f1fd7e0e0f97e9a16a0a8f5615db0f996fbca5538beb409d8"),
    ("src/smooth.m",
     "3a3eb55b6877e9a08138614541359019b72dbf9cce2e4aa00f7827ede5d3a197"),
    ("src/spectral_corr.m",
     "230e5b3354fc6c5469ea0928cdb0509f0da9a6d0fb627bc4c8c1c8361340d439"),
    ("src/spectral_selection.m",
     "62ec1ffa1210d3b0a03d4be0c3d7abbd5f0a226b63aa54a7511061418ab67b26"),
    ("src/temp_vec_corr.m",
     "e382ad4235705a8cf7e0b6c08cc505332331d64d4eb215727b6ef4aabb8d7f3e"),
    ("src/temporal_corr.m",
     "17a691b5a6beac76ba81e34f5172aab06957a07517d8b5627f11da9a27182cc4"),
    ("src/v2e.m",
     "f58a579061e48d9319f9e5252ab8ed60aafbd6937f2513cc9327d309518e83af"),
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
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/root-baselines/REPORT.md":
        "63ea22bd4d027467a1abe97639f7c9ff6e00cdc2c6c753a52c2bd5e4028bab85",
    "research/tsm-followup-20261101/root-baselines/mrate_reference_parity.py":
        "a765ec304a9b0a410c93cd49239c0a459873d8b9a8f9f08c71663746396937b7",
    "research/tsm-followup-20261101/root-baselines/mrate_reference_parity.json":
        "7d187a9b76f623fed26664f06530d8bbd181d47eca157c86e793b8c46d3269f1",
    "research/tsm-followup-20261101/root-baselines/mrate_syl_common_eval.py":
        "e437500844f2d701060acf067053b1451846941acb33232642bf5041bd7c97a5",
    "research/tsm-followup-20261101/root-baselines/mrate_syl_common_eval.json":
        "8f66416b027e04bcbb901bb4b07cffc7926fee20e658119dd869a4e2118a34d3",
    "research/tsm-followup-20261101/root-baselines/mrate_frontend_dev_tune.py":
        "14e3c19bc1716c2e99efbde594826624b660df859f22d694b93559d5df28e9a2",
    "research/tsm-followup-20261101/root-baselines/mrate_frontend_dev_tune.json":
        "b851fc5c007637cac3026bf3b74379ac0e142b2a6fcef80ab1f64de1eb9420b6",
    "research/tsm-followup-20261101/root-baselines/mrate_ami_pilot.py":
        "33e1289612633b698d04f653088169d165d4394cc37d09da0e00875dea13327e",
    "research/tsm-followup-20261101/root-baselines/mrate_ami_pilot.json":
        "cd803148c46f78cd8782dcf78c81fa2a8a9b1c33b1e57e83d2910e7ba09a9bf1",
    "research/tsm-followup-20261101/agent-neural/run/syl_eval_manifest.json":
        "3c7b3731cf6d2312e42e3333cae03bc631f6d1dbf557b773e134468c867897e2",
}
for _relative, _digest in OBSERVED_SOURCE_FILES:
    SOURCE_PINS[SOURCE_RATE_REL + "/" + _relative] = _digest
del _relative, _digest

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
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

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
FRAME_SHIFT_MS = 10
FRAME_RATE_HZ = 100
FRAME_SAMPLES = 160
MAX_TOTAL_SAMPLES = 10_000_000

CONTROL_FULL_FRAMES = 400
CONTROL_TAIL_SAMPLES = 77
CONTROL_TOTAL_SAMPLES = (
    CONTROL_FULL_FRAMES * FRAME_SAMPLES + CONTROL_TAIL_SAMPLES)
CONTROL_FRAME_COUNT = CONTROL_FULL_FRAMES + 1
CONTROL_ACTIVE_SAMPLES = 48000
CONTROL_THRESHOLD = 0.5
CONTROL_MIN_SEPARATION_FRAMES = 5
CONTROL_NUCLEUS_FRAMES: Tuple[int, ...] = (
    5, 40, 77, 114, 151, 188, 225, 262, 299, 336, 373, 400)
CONTROL_SUBTHRESHOLD_FRAMES: Tuple[int, ...] = (20, 250)

# Exact parameters in the delivered MATLAB core (rate/src/set_para.m).  They
# are recorded for identity only and are never executed here.
CORE_PARAMETERS: Dict[str, Any] = {
    "twin": 5,
    "t_sigma": 1.4,
    "subband_num": 5,
    "swin": 7,
    "s_sigma": 1.5,
    "mwin": 13,
    "max_threshold": 25,
}

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "analysis_frame_rate_hz": FRAME_RATE_HZ,
    "analysis_frame_shift_ms": FRAME_SHIFT_MS,
    "analysis_frame_samples": FRAME_SAMPLES,
    "source_example_sample_rate_hz": 8000,
    "source_frame_shift_ms": 10,
    "source_core_parameters": dict(CORE_PARAMETERS),
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
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
    "source_bundled": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "real_rate_estimate": False,
    "release_claim": False,
    "source_executed": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No USC MATLAB core, MCR executable or vendor runtime is executed.",
    "No SFS voc19, ESPS get_f0, MATLAB or Octave installation is invoked.",
    "No network request, download, staging or source redistribution occurs.",
    "No real audio, corpus, transcript, annotation or device is consumed.",
    "No syllable-rate accuracy, count error, latency, memory or RTF is measured here.",
    "The source-reported parity, MAE and correlation values are provenance only.",
    "The synthetic nucleus-score trace is a contract control, never USC output.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "official_source_archive",
        "path": ARCHIVE_REL,
        "url": ARCHIVE_URL,
        "sha256": ARCHIVE_SHA256,
        "bytes": ARCHIVE_BYTES,
        "required": True,
    },
    {
        "id": "extracted_source_tree",
        "path": SOURCE_RATE_REL,
        "tree_sha256": SOURCE_TREE_SHA256,
        "file_count": len(OBSERVED_SOURCE_FILES),
        "required": True,
        "observed_unqualified_copy": True,
    },
    {
        "id": "explicit_license_or_terms",
        "required": True,
        "status": "absent",
        "note": "The delivered README lists no license, terms or redistribution grant.",
    },
    {
        "id": "exact_matlab_runtime",
        "path": "data/runtimes/matlab-7.01",
        "matlab_version": MATLAB_VERSION,
        "target_os": TARGET_OS,
        "required": True,
    },
    {
        "id": "sfs_voc19",
        "path": "data/runtimes/sfs-voc19",
        "required": True,
    },
    {
        "id": "esps_get_f0",
        "path": "data/runtimes/esps-get_f0",
        "required": True,
    },
    {
        "id": "mcr_installer",
        "path": SOURCE_RATE_REL + "/utils/MCRInstaller.exe",
        "required": True,
        "status": "absent",
    },
    {
        "id": "approved_exact_parity_vector",
        "path": "data/runs/mrate-usc-sail-exact-parity/parity.json",
        "required": True,
        "status": "absent",
    },
    {
        "id": "rights_cleared_rate_cohort",
        "required": True,
        "status": "absent",
        "observed_unqualified_manifest":
            "research/tsm-followup-20261101/agent-neural/run/syl_eval_manifest.json",
    },
)

CALLER_ASSET_FIELDS = (
    "approved_parity_path",
    "approved_parity_sha256",
    "archive_sha256",
    "archive_zip_path",
    "esps_get_f0_path",
    "frontend_record_path",
    "frontend_record_sha256",
    "license_record_path",
    "license_record_sha256",
    "matlab_runtime_path",
    "matlab_version",
    "sfs_voc19_path",
    "source_identity",
    "source_root_path",
    "source_tree_sha256",
)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-source-runtime/0.1",
    "present_behavior": (
        "validate_archive_hash_source_tree_license_runtime_and_parity_hashes_only; "
        "do_not_extract_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "separate_source_archive_required": True,
    "source_is_script_not_weights": True,
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "archive, source, license, frontend and parity paths are absolute and present",
        "archive SHA-256 equals the published archive pin",
        "source-tree digest equals the pinned 21-file tree digest",
        "MATLAB version is exactly 7.01 and SFS/ESPS paths are present",
        "license record is an explicit grant, not an inference from silence",
        "approved parity SHA-256 matches the caller-supplied vector",
        "no extraction, import, execution, download or audio read occurs here",
    ],
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "official_archive_copy_absent",
        "requirement": (
            "Supply the official SAIL-speechrate.zip at "
            f"{ARCHIVE_REL} with SHA-256 {ARCHIVE_SHA256}."),
        "state": (
            "Only an extracted tree is present. The temporary download "
            "recorded by the research run was not retained, so the archive "
            "bytes cannot be re-verified."),
        "gate_ids": ["exact_asset_identity", "artifact_rights"],
    },
    {
        "id": "source_identity_unverified",
        "requirement": (
            "Tie the extracted 21-file tree to the published archive and an "
            "immutable upstream snapshot, not only to local file hashes."),
        "state": (
            "The local tree digest "
            f"{SOURCE_TREE_SHA256} is pinned, but with the archive absent it "
            "cannot be shown byte-identical to the official release."),
        "gate_ids": ["exact_asset_identity"],
    },
    {
        "id": "explicit_license_absent",
        "requirement": (
            "Obtain an explicit written license or permission covering the "
            "MATLAB source, bundled example audio and derivative use."),
        "state": (
            "The delivered README, source files and example contain no "
            "LICENSE, COPYING, NOTICE or terms text. Silence is not a grant."),
        "gate_ids": ["artifact_rights"],
    },
    {
        "id": "exact_runtime_absent",
        "requirement": (
            "Provide MATLAB 7.01 on Windows XP SP2, or an approved equivalent, "
            "plus the referenced MCR installer and a recorded platform."),
        "state": (
            "No MATLAB, Octave, MCR installer or Windows XP runtime is "
            "present. The README targets MATLAB 7.01 / Windows XP SP2."),
        "gate_ids": ["runtime_admission", "exact_reference_parity"],
    },
    {
        "id": "exact_frontend_absent",
        "requirement": (
            "Reproduce SFS voc19 19-subband absolute energy and ESPS get_f0 "
            "pitch exactly, with versioned binaries and parameters."),
        "state": (
            "Neither SFS voc19 nor ESPS get_f0 is present. The research "
            "front end is an approximate Bark-spaced Butterworth substitute."),
        "gate_ids": ["frontend_core_separation", "exact_reference_parity"],
    },
    {
        "id": "approved_reference_parity_absent",
        "requirement": (
            "Produce an approved exact-runtime frame and nucleus vector on "
            "frozen feature input, including fresh-process reset."),
        "state": (
            "Only unapproved source-output parity exists: 321/331 frames, "
            "12/12 events, five 1-2 frame differences and invalid-sqrt "
            "warnings reported by the research port."),
        "gate_ids": ["exact_reference_parity"],
    },
    {
        "id": "rights_cleared_rate_cohort_absent",
        "requirement": (
            "Freeze a rights-cleared, multi-meeting rate cohort with manual or "
            "approved syllable truth, active-speech denominators and strata."),
        "state": (
            "A 210-window EN2003a manifest and audio are present, but rights "
            "for reuse are not recorded and labels are CMUdict-derived from "
            "one meeting's forced alignments."),
        "gate_ids": ["rate_cohort_and_scoring"],
    },
    {
        "id": "opt_in_and_release_absent",
        "requirement": (
            "Complete opt-in provider intake, descriptor review, default-off "
            "selection and release approval on the intended target."),
        "state": (
            "No provider, adapter, descriptor, registry entry or release "
            "decision exists; this package is task-local evidence only."),
        "gate_ids": ["opt_in_provider_intake", "public_default_and_release"],
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_asset_identity",
     "The official archive and extracted 21-file source tree match exact "
     "SHA-256 pins and a recorded upstream identity."),
    ("runtime_admission",
     "MATLAB 7.01 or an approved equivalent, SFS voc19, ESPS get_f0 and the "
     "MCR installer are present with a recorded platform."),
    ("artifact_rights",
     "Explicit source, example-audio, derivative-output and redistribution "
     "rights are granted with complete notices."),
    ("exact_reference_parity",
     "An approved exact-runtime frame and nucleus vector matches on frozen "
     "feature input, including fresh-process reset."),
    ("rate_cohort_and_scoring",
     "A rights-cleared multi-meeting cohort with approved syllable truth, "
     "active-speech denominators and rate strata is scored."),
    ("frontend_core_separation",
     "SFS voc19 and ESPS get_f0 preprocessing is reproduced separately from "
     "the mrate core and never substituted silently."),
    ("opt_in_provider_intake",
     "Explicit opt-in intake, license review, descriptor review and an "
     "independent public-surface decision are complete."),
    ("public_default_and_release",
     "Default-off selection, resource/deadline evidence and release or "
     "public-benchmark approval are recorded."),
)

RATE_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    ("source_output_mapping",
     "Each nucleus event maps to an exact half-open source sample interval.",
     "control_only_structurally_verified"),
    ("duration_and_window_mapping",
     "Duration and 10 ms window arithmetic use exact integer coordinates.",
     "control_only_structurally_verified"),
    ("syllable_nucleus_detection",
     "Thresholded local maxima with a minimum separation are deterministic.",
     "control_only_structurally_verified"),
    ("syllable_count_and_rate",
     "Count and syllables-per-second are derived from exact counts and "
     "active-duration denominators.",
     "control_only_structurally_verified"),
    ("final_partial_window",
     "A final partial window is clipped to the true source end and can host "
     "a nucleus.",
     "control_only_structurally_verified"),
    ("silence_and_nonfinite_validity",
     "Silence yields zero events; missing, invalid and non-finite values are "
     "rejected rather than scored.",
     "control_only_structurally_verified"),
    ("one_x_and_rate_changes",
     "1x, rate-change, rebuffer and drift behavior on a playback path.",
     "not_applicable_estimator_has_no_playback_output"),
    ("unfamiliar_speech_and_music",
     "Unfamiliar speech, music and mixed content on approved real audio.",
     "blocked_no_rights_cleared_cohort"),
    ("rebuffer_drift_and_buffering",
     "Playback buffering, rebuffer and clock drift.",
     "not_applicable_estimator_has_no_playback_output"),
    ("pause_or_filler_decisions_tied_to_source",
     "Pause or filler decisions tied to source timestamps.",
     "not_applicable_candidate_emits_nuclei_only"),
    ("speech_preservation",
     "Speech preservation for an audio-modifying path.",
     "not_applicable_candidate_does_not_modify_audio"),
    ("pitch_and_transient_audibility",
     "Pitch and transient audibility on rendered output.",
     "blocked_no_pitch_track_or_rendered_output"),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "archive": {
        "url": ARCHIVE_URL,
        "sha256": ARCHIVE_SHA256,
        "license_file_present": False,
        "matlab_version": MATLAB_VERSION,
        "target_os": TARGET_OS,
        "required_tools": list(REQUIRED_TOOLS),
    },
    "source_output_parity": {
        "frames": 331,
        "matching_frames": 321,
        "framewise_agreement": 0.9697885196374623,
        "expected_event_count": 12,
        "predicted_event_count": 12,
        "timing_differences": 5,
        "timing_difference_range_frames": "1-2",
        "core_wall_seconds": 0.019143624987918884,
        "warning": "invalid-sqrt warnings in some windows",
        "scope": "parity with the bundled implementation output, not accuracy",
    },
    "default_pilot": {
        "windows": 210,
        "meeting": "EN2003a",
        "syllable_count_mae": 6.904761904761905,
        "syllable_rate_mae_sps": 1.8027738935641857,
        "syllable_rate_rmse_sps": 2.130044551957181,
        "rate_pearson": 0.5686435757387486,
        "rate_bias_sps": -1.7830583693911342,
        "constant_mean_baseline_mae_sps": 1.1315020268651048,
    },
    "tuned_pilot": {
        "windows": 90,
        "selected_lowpass_hz": 100,
        "documented_lowpass_hz": 50,
        "selected_pitch_confidence": 0.2,
        "dev_rate_mae_sps": 0.9451234649081911,
        "dev_count_mae": 2.8444444444444446,
        "heldout_windows": 210,
        "heldout_rate_mae_sps": 0.8699755936085545,
        "heldout_rate_rmse_sps": 1.1185167306396433,
        "heldout_rate_pearson": 0.7435362319445914,
        "heldout_rate_bias_sps": -0.5936143534823185,
        "canonical": False,
        "reason": "selected 100 Hz low-pass departs from the 50 Hz description",
    },
    "cohort": {
        "windows": 210,
        "meeting": "EN2003a",
        "duration_seconds": 4,
        "truth": "CMUdict 1.1.1 syllable counts from AMI orthographic transcripts",
        "boundaries": "AMI forced word alignments",
        "meetings": 1,
        "manual_syllabification": False,
    },
    "note": (
        "These values are copied from the merged research record. They are "
        "not reproduced, re-scored or promoted by this package."),
}

MISSING_HISTORICAL_ARTIFACTS: Tuple[str, ...] = (
    ARCHIVE_REL,
    SOURCE_RATE_REL + "/LICENSE",
    "data/runs/mrate-usc-sail-exact-parity/parity.json",
)

RIGHTS_PATHS = (
    SOURCE_RATE_REL + "/LICENSE",
    SOURCE_RATE_REL + "/LICENSE.md",
    SOURCE_RATE_REL + "/COPYING",
    SOURCE_RATE_REL + "/NOTICE",
    SOURCE_RATE_REL + "/doc/LICENSE",
    SOURCE_RATE_REL + "/doc/COPYING",
    SOURCE_CHECKOUT_REL + "/LICENSE",
)
RUNTIME_PATHS = (
    "data/runtimes/matlab-7.01",
    "data/runtimes/sfs-voc19",
    "data/runtimes/esps-get-f0",
    "data/envs/mrate-usc-sail",
    SOURCE_RATE_REL + "/utils/MCRInstaller.exe",
)
COHORT_MANIFEST = (
    "research/tsm-followup-20261101/agent-neural/run/syl_eval_manifest.json")
COHORT_AUDIO_DIR = "research/tsm-followup-20261101/agent-neural/run/data"
APPROVED_PARITY_PATH = "data/runs/mrate-usc-sail-exact-parity/parity.json"
OBSERVED_PARITY_PATHS = (
    SOURCE_RATE_REL + "/example/sw2523A-ws97-i-0026.rat",
    "research/tsm-followup-20261101/root-baselines/"
    "mrate_reference_parity.json",
)


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
# Fixed-path audit.  No network, no download, no extraction, no execution.
# ---------------------------------------------------------------------------

def _observe_file(relative: str) -> Dict[str, Any]:
    path = SOURCE_ROOT / relative
    if not path.is_file():
        return {"path": relative, "present": False, "bytes": None,
                "sha256": None}
    data = path.read_bytes()
    return {"path": relative, "present": True, "bytes": len(data),
            "sha256": sha256(data)}


def _observe_path(relative: str) -> Dict[str, Any]:
    path = SOURCE_ROOT / relative
    if not path.exists():
        return {"path": relative, "present": False, "kind": None}
    return {"path": relative, "present": True,
            "kind": "dir" if path.is_dir() else "file"}


def source_tree_digest(root: Path) -> str:
    """Canonical digest over sorted relative paths and file SHA-256 values."""
    root = Path(root)
    if not root.is_dir():
        raise Reject("source tree is absent")
    items: List[Dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise Reject("source tree contains a symlink")
        if path.is_file():
            items.append({
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256(path.read_bytes()),
            })
    return sha256(canonical_bytes(items))


def audit_assets() -> Dict[str, Any]:
    archive = _observe_file(ARCHIVE_REL)
    source_root = _observe_path(SOURCE_RATE_REL)
    observed_files = [
        _observe_file(SOURCE_RATE_REL + "/" + relative)
        for relative, _ in OBSERVED_SOURCE_FILES]
    matches = []
    for observation, (_, expected) in zip(observed_files,
                                           OBSERVED_SOURCE_FILES):
        matches.append(
            observation["present"] and observation.get("sha256") == expected)
    tree_actual = None
    tree_matches = False
    if source_root["present"] and source_root["kind"] == "dir":
        try:
            tree_actual = source_tree_digest(SOURCE_ROOT / SOURCE_RATE_REL)
        except (Reject, OSError):
            tree_actual = None
        tree_matches = tree_actual == SOURCE_TREE_SHA256

    rights = [_observe_file(path) for path in RIGHTS_PATHS]
    runtimes = [_observe_path(path) for path in RUNTIME_PATHS]
    cohort_manifest = _observe_file(COHORT_MANIFEST)
    audio = _observe_path(COHORT_AUDIO_DIR)
    observed_parity = [_observe_file(path) for path in OBSERVED_PARITY_PATHS]
    approved_parity = _observe_file(APPROVED_PARITY_PATH)

    runtime_present = any(
        item["present"] and item["path"].endswith(("matlab-7.01",
                                                   "sfs-voc19",
                                                   "esps-get-f0",
                                                   "MCRInstaller.exe"))
        for item in runtimes)
    rights_present = any(item["present"] for item in rights)
    return {
        "archive_candidates": [archive],
        "source_root": source_root,
        "observed_source_files": observed_files,
        "observed_source_file_count": len(observed_files),
        "observed_source_files_match_pins": all(matches),
        "source_tree_expected_sha256": SOURCE_TREE_SHA256,
        "source_tree_actual_sha256": tree_actual,
        "source_tree_matches_pins": tree_matches,
        "rights_records": rights,
        "runtime_paths": runtimes,
        "cohort_manifest": cohort_manifest,
        "cohort_audio": audio,
        "observed_parity": observed_parity,
        "approved_parity": approved_parity,
        "archive_present": archive["present"],
        "source_checkout_present": source_root["present"],
        "rights_record_present": rights_present,
        "runtime_present": runtime_present,
        "rate_manifest_present": cohort_manifest["present"],
        "rate_audio_present": audio["present"],
        "rights_cleared_cohort_present": False,
        "approved_parity_present": approved_parity["present"],
        "observed_parity_present": all(
            item["present"] for item in observed_parity),
        "audit_scope": (
            "fixed workspace paths only; no network, no download, "
            "no extraction, no execution, no audio decode or playback"),
    }


# ---------------------------------------------------------------------------
# Task-row identity: stable linked-row fields only; never the whole file.
# ---------------------------------------------------------------------------

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
    if stable["repository"] != "audio-sdk" or stable["mode"] != "implementation":
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
# Geometry, exact frame mapping and synthetic rate control.
# ---------------------------------------------------------------------------

def validate_geometry(sample_rate_hz: Any, channels: Any,
                      frame_samples: Any) -> Dict[str, int]:
    if type(sample_rate_hz) is not int or sample_rate_hz != SAMPLE_RATE_HZ:
        raise Reject("only 16000 Hz is supported")
    if type(channels) is not int or channels != CHANNELS:
        raise Reject("only mono is supported")
    if type(frame_samples) is not int or frame_samples != FRAME_SAMPLES:
        raise Reject("only 160-sample / 10 ms frames are supported")
    return {"sample_rate_hz": SAMPLE_RATE_HZ, "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES}


def map_frames(total_samples: Any) -> Dict[str, Any]:
    if type(total_samples) is not int or total_samples <= 0:
        raise Reject("total_samples must be a positive integer")
    if total_samples > MAX_TOTAL_SAMPLES:
        raise Reject("total_samples exceeds the evidence cap")
    frame_count = (total_samples + FRAME_SAMPLES - 1) // FRAME_SAMPLES
    last_start = (frame_count - 1) * FRAME_SAMPLES
    return {
        "total_samples": total_samples,
        "frame_samples": FRAME_SAMPLES,
        "frame_rate_hz": FRAME_RATE_HZ,
        "frame_count": frame_count,
        "partial_samples": total_samples % FRAME_SAMPLES,
        "last_frame": {
            "index": frame_count - 1,
            "start_sample": last_start,
            "end_sample": total_samples,
            "samples": total_samples - last_start,
        },
    }


def synthetic_trace() -> List[float]:
    """Deterministic caller-supplied control trace, not USC output."""
    trace = [0.05] * CONTROL_FRAME_COUNT
    for index in CONTROL_SUBTHRESHOLD_FRAMES:
        trace[index] = 0.49
    for index in CONTROL_NUCLEUS_FRAMES:
        if index > 0 and index - 1 not in CONTROL_SUBTHRESHOLD_FRAMES:
            trace[index - 1] = 0.2
        if index + 1 < CONTROL_FRAME_COUNT:
            trace[index + 1] = 0.2
        trace[index] = 0.9
    return trace


def _score(value: Any, index: int) -> float:
    if value is None:
        raise Reject(f"missing nucleus score at frame {index}")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Reject(f"nucleus score {index} is not a number")
    number = float(value)
    if not math.isfinite(number):
        raise Reject(f"nucleus score {index} is not finite")
    if number < 0.0 or number > 1.0:
        raise Reject(f"nucleus score {index} is outside [0,1]")
    return number


def _validate_active(active_samples: Any, total_samples: int) -> int:
    if type(active_samples) is not int or active_samples <= 0:
        raise Reject("active_samples must be a positive integer")
    if active_samples > total_samples:
        raise Reject("active_samples exceeds total_samples")
    return active_samples


def detect_nuclei(trace: Any, total_samples: Any,
                  threshold: float = CONTROL_THRESHOLD,
                  min_separation_frames: int = CONTROL_MIN_SEPARATION_FRAMES,
                  active_samples: Optional[int] = None) -> Dict[str, Any]:
    """Map a synthetic nucleus-score trace to exact source intervals."""
    if threshold != CONTROL_THRESHOLD:
        raise Reject("only the pinned threshold 0.5 is supported")
    if (type(min_separation_frames) is not int
            or min_separation_frames != CONTROL_MIN_SEPARATION_FRAMES):
        raise Reject("only the pinned 5-frame separation is supported")
    plan = map_frames(total_samples)
    if not isinstance(trace, (list, tuple)):
        raise Reject("trace must be a sequence")
    if len(trace) != plan["frame_count"]:
        raise Reject("trace count does not match frame count")
    scores = [_score(item, index) for index, item in enumerate(trace)]
    active = _validate_active(
        plan["total_samples"] if active_samples is None else active_samples,
        plan["total_samples"])
    events: List[Dict[str, Any]] = []
    last_selected = -(10 ** 9)
    for index, score in enumerate(scores):
        if score < threshold:
            continue
        left = scores[index - 1] if index > 0 else -1.0
        right = scores[index + 1] if index + 1 < len(scores) else -1.0
        if score <= left or score < right:
            continue
        if index - last_selected < min_separation_frames:
            continue
        start = index * FRAME_SAMPLES
        events.append({
            "index": index,
            "start_sample": start,
            "end_sample": min(start + FRAME_SAMPLES, plan["total_samples"]),
            "time_ms": index * FRAME_SHIFT_MS,
            "score": score,
        })
        last_selected = index
    count = len(events)
    rate = Fraction(count * SAMPLE_RATE_HZ, active)
    return {
        "frame_count": plan["frame_count"],
        "total_samples": plan["total_samples"],
        "active_samples": active,
        "threshold": threshold,
        "min_separation_frames": min_separation_frames,
        "events": events,
        "nucleus_count": count,
        "syllables_per_second_fraction": fraction_text(rate),
        "syllables_per_second": round(float(rate), 6),
        "duration_seconds_fraction": fraction_text(
            Fraction(plan["total_samples"], SAMPLE_RATE_HZ)),
        "active_seconds_fraction": fraction_text(
            Fraction(active, SAMPLE_RATE_HZ)),
        "trace_sha256": sha256(canonical_bytes(scores)),
        "qualification_effect": "none",
        "note": (
            "Caller-supplied synthetic control only; this is not USC mrate "
            "output and cannot qualify the candidate."),
    }


def score_rate(predicted_count: Any, truth_count: Any,
               active_samples: Any) -> Dict[str, Any]:
    """Score one count pair; a missing truth is rejected, never imputed."""
    if truth_count is None:
        raise Reject("truth count is missing")
    if type(predicted_count) is not int or predicted_count < 0:
        raise Reject("predicted_count must be a nonnegative integer")
    if type(truth_count) is not int or truth_count < 0:
        raise Reject("truth_count must be a nonnegative integer")
    if type(active_samples) is not int or active_samples <= 0:
        raise Reject("active_samples must be a positive integer")
    predicted_rate = Fraction(predicted_count * SAMPLE_RATE_HZ, active_samples)
    truth_rate = Fraction(truth_count * SAMPLE_RATE_HZ, active_samples)
    absolute_count_error = abs(predicted_count - truth_count)
    absolute_rate_error = abs(predicted_rate - truth_rate)
    return {
        "predicted_count": predicted_count,
        "truth_count": truth_count,
        "absolute_count_error": absolute_count_error,
        "predicted_rate_fraction": fraction_text(predicted_rate),
        "truth_rate_fraction": fraction_text(truth_rate),
        "absolute_rate_error_fraction": fraction_text(absolute_rate_error),
        "absolute_rate_error": round(float(absolute_rate_error), 6),
        "qualification_effect": "none",
    }


def _refractory_trace() -> List[float]:
    trace = [0.05] * CONTROL_FRAME_COUNT
    for index in (100, 102):
        trace[index - 1] = 0.2
        trace[index] = 0.9
        trace[index + 1] = 0.2
    return trace


# ---------------------------------------------------------------------------
# Caller-supplied source/runtime manifest.  Validation only; never execution.
# ---------------------------------------------------------------------------

def _absolute_file(manifest: Dict[str, Any], field: str) -> Path:
    raw = manifest.get(field)
    if not isinstance(raw, str) or not raw:
        raise Reject(f"{field} must be a nonempty string")
    path = Path(raw)
    if not path.is_absolute():
        raise Reject(f"{field} must be an absolute path")
    if not path.is_file():
        raise Reject(f"{field} does not exist")
    return path


def _absolute_dir(manifest: Dict[str, Any], field: str) -> Path:
    raw = manifest.get(field)
    if not isinstance(raw, str) or not raw:
        raise Reject(f"{field} must be a nonempty string")
    path = Path(raw)
    if not path.is_absolute():
        raise Reject(f"{field} must be an absolute path")
    if not path.is_dir():
        raise Reject(f"{field} does not exist")
    return path


def _sha_field(manifest: Dict[str, Any], field: str) -> str:
    raw = manifest.get(field)
    if not isinstance(raw, str) or not re.fullmatch(r"[0-9a-f]{64}", raw):
        raise Reject(f"{field} must be 64 lowercase hex characters")
    return raw


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise Reject("caller manifest must be a JSON object")
    if set(manifest) != set(CALLER_ASSET_FIELDS):
        missing = sorted(set(CALLER_ASSET_FIELDS) - set(manifest))
        extra = sorted(set(manifest) - set(CALLER_ASSET_FIELDS))
        raise Reject(
            f"caller manifest fields differ missing={missing} extra={extra}")
    if manifest.get("matlab_version") != MATLAB_VERSION:
        raise Reject("matlab_version must be exactly " + MATLAB_VERSION)
    if not isinstance(manifest.get("source_identity"), str) or not \
            manifest["source_identity"].strip():
        raise Reject("source_identity must be a nonempty string")
    archive = _absolute_file(manifest, "archive_zip_path")
    source_root = _absolute_dir(manifest, "source_root_path")
    license_path = _absolute_file(manifest, "license_record_path")
    frontend_path = _absolute_file(manifest, "frontend_record_path")
    parity_path = _absolute_file(manifest, "approved_parity_path")
    matlab = _absolute_dir(manifest, "matlab_runtime_path")
    sfs = _absolute_dir(manifest, "sfs_voc19_path")
    esps = _absolute_dir(manifest, "esps_get_f0_path")
    archive_sha = _sha_field(manifest, "archive_sha256")
    tree_sha = _sha_field(manifest, "source_tree_sha256")
    license_sha = _sha_field(manifest, "license_record_sha256")
    frontend_sha = _sha_field(manifest, "frontend_record_sha256")
    parity_sha = _sha_field(manifest, "approved_parity_sha256")
    if archive_sha != ARCHIVE_SHA256:
        raise Reject("archive_sha256 does not match the published archive pin")
    if tree_sha != SOURCE_TREE_SHA256:
        raise Reject("source_tree_sha256 does not match the pinned tree")
    if sha256(archive.read_bytes()) != archive_sha:
        raise Reject("archive file SHA-256 mismatch")
    if sha256(license_path.read_bytes()) != license_sha:
        raise Reject("license record SHA-256 mismatch")
    if sha256(frontend_path.read_bytes()) != frontend_sha:
        raise Reject("frontend record SHA-256 mismatch")
    if sha256(parity_path.read_bytes()) != parity_sha:
        raise Reject("approved parity SHA-256 mismatch")
    if source_tree_digest(source_root) != tree_sha:
        raise Reject("source tree digest mismatch")
    if not (matlab / "bin").exists() and matlab.name.lower() != "matlab":
        raise Reject("MATLAB runtime layout is not recognized")
    return {
        "accepted": True,
        "executed": False,
        "extracted": False,
        "loaded": False,
        "archive_zip_path": str(archive),
        "archive_sha256": archive_sha,
        "source_root_path": str(source_root),
        "source_tree_sha256": tree_sha,
        "license_record_path": str(license_path),
        "license_record_sha256": license_sha,
        "matlab_runtime_path": str(matlab),
        "matlab_version": MATLAB_VERSION,
        "sfs_voc19_path": str(sfs),
        "esps_get_f0_path": str(esps),
        "frontend_record_path": str(frontend_path),
        "frontend_record_sha256": frontend_sha,
        "approved_parity_path": str(parity_path),
        "approved_parity_sha256": parity_sha,
        "source_identity": manifest["source_identity"],
        "note": "validation only; no archive, runtime or audio was executed",
    }


# ---------------------------------------------------------------------------
# Adverse controls.  Each case is actually invoked and must fail closed.
# ---------------------------------------------------------------------------

def _trace_with_missing() -> List[Optional[float]]:
    trace: List[Optional[float]] = list(synthetic_trace())
    trace[0] = None
    return trace


def run_adverse_controls() -> List[Dict[str, str]]:
    cases: List[Tuple[str, Any]] = [
        ("strict_json_duplicate_key",
         lambda: strict_loads('{"a":1,"a":2}')),
        ("strict_json_nonfinite",
         lambda: strict_loads('{"a":NaN}')),
        ("trace_not_a_sequence",
         lambda: detect_nuclei("trace", CONTROL_TOTAL_SAMPLES)),
        ("trace_empty",
         lambda: detect_nuclei([], CONTROL_TOTAL_SAMPLES)),
        ("trace_count_mismatch",
         lambda: detect_nuclei([0.1] * 3, CONTROL_TOTAL_SAMPLES)),
        ("trace_missing_value",
         lambda: detect_nuclei(_trace_with_missing(), CONTROL_TOTAL_SAMPLES)),
        ("trace_nan",
         lambda: detect_nuclei(
             [math.nan] * CONTROL_FRAME_COUNT, CONTROL_TOTAL_SAMPLES)),
        ("trace_infinity",
         lambda: detect_nuclei(
             [math.inf] * CONTROL_FRAME_COUNT, CONTROL_TOTAL_SAMPLES)),
        ("trace_negative",
         lambda: detect_nuclei(
             [-0.1] * CONTROL_FRAME_COUNT, CONTROL_TOTAL_SAMPLES)),
        ("trace_above_one",
         lambda: detect_nuclei(
             [1.1] * CONTROL_FRAME_COUNT, CONTROL_TOTAL_SAMPLES)),
        ("trace_boolean",
         lambda: detect_nuclei(
             [True] * CONTROL_FRAME_COUNT, CONTROL_TOTAL_SAMPLES)),
        ("trace_string",
         lambda: detect_nuclei(
             ["0.5"] * CONTROL_FRAME_COUNT, CONTROL_TOTAL_SAMPLES)),
        ("total_samples_zero", lambda: map_frames(0)),
        ("total_samples_boolean", lambda: map_frames(True)),
        ("total_samples_float", lambda: map_frames(64077.0)),
        ("total_samples_over_cap",
         lambda: map_frames(MAX_TOTAL_SAMPLES + 1)),
        ("threshold_wrong",
         lambda: detect_nuclei(
             synthetic_trace(), CONTROL_TOTAL_SAMPLES, threshold=0.4)),
        ("min_separation_zero",
         lambda: detect_nuclei(
             synthetic_trace(), CONTROL_TOTAL_SAMPLES,
             min_separation_frames=0)),
        ("active_samples_zero",
         lambda: detect_nuclei(
             synthetic_trace(), CONTROL_TOTAL_SAMPLES, active_samples=0)),
        ("active_samples_above_total",
         lambda: detect_nuclei(
             synthetic_trace(), CONTROL_TOTAL_SAMPLES,
             active_samples=CONTROL_TOTAL_SAMPLES + 1)),
        ("truth_missing",
         lambda: score_rate(12, None, CONTROL_ACTIVE_SAMPLES)),
        ("truth_negative",
         lambda: score_rate(12, -1, CONTROL_ACTIVE_SAMPLES)),
        ("prediction_boolean",
         lambda: score_rate(True, 12, CONTROL_ACTIVE_SAMPLES)),
        ("geometry_wrong_rate", lambda: validate_geometry(44100, 1, 160)),
        ("geometry_wrong_channels",
         lambda: validate_geometry(SAMPLE_RATE_HZ, 2, 160)),
        ("geometry_wrong_frame",
         lambda: validate_geometry(SAMPLE_RATE_HZ, 1, 512)),
        ("caller_manifest_not_object", lambda: validate_caller_manifest([])),
        ("caller_manifest_missing_field",
         lambda: validate_caller_manifest({"matlab_version": MATLAB_VERSION})),
        ("caller_manifest_relative_path",
         lambda: validate_caller_manifest({
             "approved_parity_path": "relative-parity.json",
             "approved_parity_sha256": "0" * 64,
             "archive_sha256": ARCHIVE_SHA256,
             "archive_zip_path": "relative-archive.zip",
             "esps_get_f0_path": "relative-esps",
             "frontend_record_path": "/nonexistent/frontend.json",
             "frontend_record_sha256": "0" * 64,
             "license_record_path": "/nonexistent/LICENSE",
             "license_record_sha256": "0" * 64,
             "matlab_runtime_path": "relative-matlab",
             "matlab_version": MATLAB_VERSION,
             "sfs_voc19_path": "relative-sfs",
             "source_identity": "archive-sha256-plus-tree",
             "source_root_path": "relative-source",
             "source_tree_sha256": SOURCE_TREE_SHA256,
         })),
    ]
    results: List[Dict[str, str]] = []
    for name, function in cases:
        try:
            function()
        except (Reject, OSError, ValueError):
            results.append({"case": name, "result": "rejected"})
        else:
            results.append({"case": name, "result": "accepted"})
    return results


def build_control() -> Dict[str, Any]:
    trace = synthetic_trace()
    mapped = detect_nuclei(
        trace, CONTROL_TOTAL_SAMPLES, active_samples=CONTROL_ACTIVE_SAMPLES)
    silence = detect_nuclei(
        [0.0] * CONTROL_FRAME_COUNT, CONTROL_TOTAL_SAMPLES,
        active_samples=CONTROL_ACTIVE_SAMPLES)
    refractory = detect_nuclei(
        _refractory_trace(), CONTROL_TOTAL_SAMPLES,
        active_samples=CONTROL_ACTIVE_SAMPLES)
    scoring = score_rate(
        mapped["nucleus_count"], len(CONTROL_NUCLEUS_FRAMES),
        CONTROL_ACTIVE_SAMPLES)
    adverse = run_adverse_controls()
    below = [event for event in mapped["events"]
             if event["index"] in CONTROL_SUBTHRESHOLD_FRAMES]
    return {
        "source_executed": False,
        "executor": "absent",
        "trace_source": (
            "caller_supplied_synthetic_control_trace_not_usc_output"),
        "geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "frame_shift_ms": FRAME_SHIFT_MS,
            "frame_rate_hz": FRAME_RATE_HZ,
            "threshold": CONTROL_THRESHOLD,
            "min_separation_frames": CONTROL_MIN_SEPARATION_FRAMES,
        },
        "trace": {
            "length": len(trace),
            "sha256": mapped["trace_sha256"],
            "values": trace,
            "nucleus_frames": list(CONTROL_NUCLEUS_FRAMES),
            "subthreshold_frames": list(CONTROL_SUBTHRESHOLD_FRAMES),
        },
        "frame_plan": map_frames(CONTROL_TOTAL_SAMPLES),
        "mapped": {
            "event_count": mapped["nucleus_count"],
            "events": mapped["events"],
            "syllables_per_second": mapped["syllables_per_second"],
            "syllables_per_second_fraction":
                mapped["syllables_per_second_fraction"],
            "duration_seconds_fraction":
                mapped["duration_seconds_fraction"],
            "active_seconds_fraction": mapped["active_seconds_fraction"],
        },
        "silence_control": {
            "frame_count": silence["frame_count"],
            "event_count": silence["nucleus_count"],
            "syllables_per_second": silence["syllables_per_second"],
            "result": "zero_events",
        },
        "subthreshold_control": {
            "spike_frames": list(CONTROL_SUBTHRESHOLD_FRAMES),
            "accepted_events": len(below),
            "result": "below_threshold_rejected",
        },
        "refractory_control": {
            "input_peak_frames": [100, 102],
            "accepted_events": refractory["nucleus_count"],
            "accepted_frames": [item["index"] for item in refractory["events"]],
            "result": "minimum_separation_enforced",
        },
        "final_partial_window": {
            "total_samples": CONTROL_TOTAL_SAMPLES,
            "frame_index": CONTROL_FRAME_COUNT - 1,
            "start_sample": CONTROL_FULL_FRAMES * FRAME_SAMPLES,
            "end_sample": CONTROL_TOTAL_SAMPLES,
            "samples": CONTROL_TAIL_SAMPLES,
            "hosts_nucleus": any(
                event["index"] == CONTROL_FRAME_COUNT - 1
                for event in mapped["events"]),
        },
        "scoring": scoring,
        "missing_result": {
            "truth_missing_rejected": any(
                item["case"] == "truth_missing"
                and item["result"] == "rejected" for item in adverse),
            "missing_trace_value_rejected": any(
                item["case"] == "trace_missing_value"
                and item["result"] == "rejected" for item in adverse),
            "produced_result_for_missing": False,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic contract control only.  It is not USC mrate output, "
            "not a real cohort result and cannot qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Report model.
# ---------------------------------------------------------------------------

def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    return {
        "qualified": False,
        "audit_result": "extracted_source_present_unqualified",
        "archive_present": observed["archive_present"],
        "source_checkout_present": observed["source_checkout_present"],
        "source_tree_matches_pins": observed["source_tree_matches_pins"],
        "rights_record_present": observed["rights_record_present"],
        "runtime_present": observed["runtime_present"],
        "rate_manifest_present": observed["rate_manifest_present"],
        "rate_audio_present": observed["rate_audio_present"],
        "rights_cleared_cohort_present":
            observed["rights_cleared_cohort_present"],
        "approved_parity_present": observed["approved_parity_present"],
        "observed": observed,
        "note": (
            "Presence is not qualification. The extracted tree matches its "
            "local pins, but the official archive, explicit rights, exact "
            "runtime, exact front end and approved parity are absent."),
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
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
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
                "The official archive copy, explicit license, MATLAB 7.01 / "
                "SFS voc19 / ESPS get_f0 runtime, exact front end, approved "
                "parity vector and rights-cleared multi-meeting cohort are "
                "absent."),
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
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "source_artifact": {
            "url": ARCHIVE_URL,
            "archive_sha256": ARCHIVE_SHA256,
            "archive_bytes": ARCHIVE_BYTES,
            "source_tree_sha256": SOURCE_TREE_SHA256,
            "file_count": len(OBSERVED_SOURCE_FILES),
            "matlab_version": MATLAB_VERSION,
            "target_os": TARGET_OS,
            "required_tools": list(REQUIRED_TOOLS),
            "core_parameters": dict(CORE_PARAMETERS),
            "license_file_present": False,
            "source_revision_present": False,
            "executed": False,
        },
        "asset_audit": audit,
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
            "real_rate_metrics": None,
            "note": (
                "Structural controls pass, but no exact source/runtime, "
                "rights-cleared cohort or approved parity exists, so the rate "
                "profile is not satisfied for qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "missing_result_never_qualifies": True,
            "invalid_values_rejected": True,
            "nonfinite_values_rejected": True,
            "silence_yields_zero_events": True,
            "final_partial_window_clipped": True,
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
        "candidate_metrics": None,
        "missing_historical_artifacts": list(MISSING_HISTORICAL_ARTIFACTS),
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; NumPy, SciPy and soundfile are not imported.",
            "The source tree is read as bytes for SHA-256 only; no .m file is executed.",
            "All asset observations use fixed workspace paths and local reads.",
            "No network request, download, archive extraction, audio device or timing run occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }
