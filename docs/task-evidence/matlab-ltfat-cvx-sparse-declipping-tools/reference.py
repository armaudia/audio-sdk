# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for the MATLAB/LTFAT/CVX tools.

The task documents the vendor boundary and tool dependency for the authors'
``declipping2020_codes`` MATLAB declipping toolbox.  The merged research
document says that toolbox evaluates sparse/constrained declipping methods but
requires MATLAB, LTFAT and, for C-OMP, CVX, so it was not runnable in the
Python pilot.  No toolbox checkout, resolved revision, MATLAB/LTFAT/CVX
runtime, documented tool use, licence, rights record or numeric output exists
in this workspace, so the isolated-adapter prototype is not attempted.

This module therefore never imports NumPy, SciPy, MATLAB, Octave, LTFAT, CVX,
a sparse solver or an audio codec.  It never loads or executes the toolbox,
never reads or writes real audio, never downloads anything and never measures
a device clock.  It provides three bounded, verifiable pieces:

* a fail-closed source/toolbox/runtime audit over fixed workspace paths that
  records the absent source, revision, MATLAB/LTFAT/CVX runtime, documented
  tool use, licence, rights and cohort records and probes fixed paths for
  accidental assets;
* a caller-supplied-asset manifest contract validated without execution, with
  every malformed, missing, invalid or nonfinite control rejected before use;
* a deterministic synthetic exact-clipping-mask accounting control that checks
  binary32 threshold equality, reliable-sample preservation, exact occupancy,
  exact half-open mask intervals, duration conservation and finite/peak bounds
  without performing sparse recovery, interpolation or declipping.

Nothing in this package qualifies the candidate.  The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import struct
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS"
TITLE = "MATLAB/LTFAT/CVX sparse declipping tools"
SLUG = "matlab-ltfat-cvx-sparse-declipping-tools"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "0cc1e79e592d7fc25f054fcd98824053be281f5e"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "tool"
MODE = "external-adapter"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

# The merged evidence records project and repository URLs but no resolved
# revision, licence identity or numeric output.  None is invented here.
UPSTREAM_NAME = (
    "MATLAB/LTFAT/CVX sparse declipping tools (declipping2020_codes toolbox)")
UPSTREAM_PROJECT_URL = "https://rajmic.github.io/declipping2020/"
UPSTREAM_REPO_URL = "https://github.com/rajmic/declipping2020_codes"
UPSTREAM_REVISION: Optional[str] = None
SOURCE_REVISION_PIN_AVAILABLE = False
REPORTED_METHOD = "sparse_and_constrained_declipping_toolbox_methods"
REPORTED_TOOLBOX = "declipping2020_codes"
REPORTED_DEPENDENCIES = ("MATLAB", "LTFAT", "CVX")
REPORTED_OPTIONAL_CVX_PATH = "constrained_orthogonal_matching_pursuit_c_omp"
REPORTED_LICENSE: Optional[str] = None
TASK_GEOMETRY_STATUS = "unestablished"

# Control geometry is exactly the public SDK v0 input boundary.  The candidate
# block/frame, dictionary, sparsity, constraint and solver geometry is not
# established.
CONTROL_SAMPLE_RATE_HZ = 16000
CONTROL_SECONDS = 1
CONTROL_SOURCE_SAMPLES = CONTROL_SAMPLE_RATE_HZ * CONTROL_SECONDS
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
NS_PER_SAMPLE = 62_500
CONTROL_THRESHOLDS = (0.35, 0.55)
QUIET_SCALE = 0.20
QUIET_THRESHOLD = 0.55

# Fixed workspace paths used for the audit.  Absence is recorded, not filled.
MISSING_SOURCE_PATH = "data/checkouts/declipping2020_codes"
MISSING_SOURCE_ALIASES = (
    "data/checkouts/declipping2020",
    "data/checkouts/declipping2020-code",
    "data/checkouts/rajmic-declipping2020-codes",
    "research/voice-enhancement-20261101/repos/declipping2020_codes",
)
MATLAB_ENV_PATH = "data/envs/matlab-ltfat-cvx"
MATLAB_ENV_MANIFEST_PATH = MATLAB_ENV_PATH + "/environment.json"
MATLAB_INSTALL_PATH = "data/envs/matlab-ltfat-cvx/matlab"
LTFAT_PATH = "data/toolboxes/ltfat"
LTFAT_MANIFEST_PATH = LTFAT_PATH + "/manifest.json"
CVX_PATH = "data/toolboxes/cvx"
CVX_MANIFEST_PATH = CVX_PATH + "/manifest.json"
REFERENCE_EXPERIMENT_PATH = (
    "data/runs/matlab-ltfat-cvx-tools-reference/expected.json")
RIGHTS_RECORD_PATH = "data/rights/declipping2020-codes-rights.json"
COHORT_MANIFEST_PATH = "data/runs/matlab-ltfat-cvx-tools-cohort/manifest.json"
PARITY_MANIFEST_PATH = (
    "data/runs/matlab-ltfat-cvx-tools-parity/manifest.json")
OUTPUT_USE_GRANT_PATH = (
    "data/rights/matlab-ltfat-cvx-tools-output-use-grant.json")
ADAPTER_PROTOTYPE_PATH = "data/adapters/matlab-ltfat-cvx-tools/adapter.json"

# Fixed absence probes.  Every probe must stay absent; any appearance forces a
# re-evaluation instead of silently promoting the candidate.
ABSENCE_PROBES: Tuple[str, ...] = (
    MISSING_SOURCE_PATH,
    *MISSING_SOURCE_ALIASES,
    MATLAB_ENV_PATH,
    MATLAB_ENV_MANIFEST_PATH,
    MATLAB_INSTALL_PATH,
    LTFAT_PATH,
    LTFAT_MANIFEST_PATH,
    CVX_PATH,
    CVX_MANIFEST_PATH,
    REFERENCE_EXPERIMENT_PATH,
    RIGHTS_RECORD_PATH,
    COHORT_MANIFEST_PATH,
    PARITY_MANIFEST_PATH,
    OUTPUT_USE_GRANT_PATH,
    ADAPTER_PROTOTYPE_PATH,
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
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/audio-sdk/README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "reports/distortion-restoration/20261028-synthetic-screen.json":
        "87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece",
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
    "docs/task-evidence/band-limited-pocs-declipping/README.md":
        "8e6bfec06db0b02321d6b6313536cf4a438204680d28240c15c9f57189dcdc65",
    "docs/task-evidence/band-limited-pocs-declipping/report.json":
        "8d893e8055cdc2e982a4e568e7996b45d1b6dd73841ac2b701a15ec5160dc65b",
    "docs/task-evidence/c-omp-declipping/README.md":
        "0891576454410a354c3bebb0ed31368b27f48f845bdd78be58048d0cdbcfd3ee",
    "docs/task-evidence/c-omp-declipping/report.json":
        "eb1e7213fd6abc95d9cc491531e3114d2fe92233f34e9f41280dcbf8c2a6e77e",
    "docs/task-evidence/linear-interpolation-declipping/README.md":
        "ab68e2a7b000f5b73e26e97e0ebb95c45ff15e1db2922d26365ac96466758a6d",
    "docs/task-evidence/linear-interpolation-declipping/report.json":
        "c3252fd080299e4b1804a9facf3fea02fe66f0df31728426476346f28d8dc310",
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
    "tool_version": None,
    "tool_install_location": None,
    "tool_provenance": UPSTREAM_REPO_URL,
    "tool_provenance_pinned": False,
    "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "control_channels": CHANNELS,
    "control_sample_format": "f32",
    "control_source_samples": CONTROL_SOURCE_SAMPLES,
    "control_thresholds": list(CONTROL_THRESHOLDS),
    "control_mode": "offline_exact_clipping_mask_accounting",
    "control_performs_sparse_recovery": False,
    "control_performs_declipping": False,
    "control_performs_interpolation": False,
    "control_output_is_candidate_output": False,
    "control_is_quality_result": False,
    "control_incremental_streaming": False,
    "reported_method": REPORTED_METHOD,
    "reported_toolbox": REPORTED_TOOLBOX,
    "reported_dependencies": list(REPORTED_DEPENDENCIES),
    "reported_optional_cvx_path": REPORTED_OPTIONAL_CVX_PATH,
    "reported_geometry_asserted": False,
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
    "matlab_dependency_added": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "sdk_callback_invoked": False,
    "shared_build_or_ci_change": False,
    "toolbox_vendored": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "adapter_prototype_created": False,
    "c_omp_executed": False,
    "clean_install_verified": False,
    "cvx_loaded": False,
    "declipping_output_produced": False,
    "device_timing": False,
    "listening": False,
    "ltfat_loaded": False,
    "matlab_invoked": False,
    "network_used": False,
    "public_benchmark": False,
    "quality_metrics_computed": False,
    "real_audio": False,
    "real_corpus": False,
    "release_claim": False,
    "runtime_invoked": False,
    "sparse_recovery_performed": False,
    "task_local_only": True,
    "toolbox_executed": False,
    "tool_use_run": False,
    "vendor_output_scored": False,
    "vendor_runtime_invoked": False,
    "workload_measured": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No declipping2020_codes toolbox, MATLAB script, LTFAT frame or CVX solve is loaded or executed.",
    "No MATLAB, Octave, NumPy, SciPy, CVX, LTFAT, sparse solver or audio codec is imported.",
    "No isolated adapter prototype is created; the approved runtime required for one is absent.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, clipping trace, clean reference or rights-cleared cohort is consumed.",
    "No declipped output, SI-SDR, RMSE, STOI, WER, MOS, latency, memory or RTF is measured here.",
    "The synthetic exact-mask control performs no sparse recovery, interpolation or declipping and is never toolbox output.",
    "The merged research document states only that the authors' MATLAB toolbox requires MATLAB, LTFAT and CVX and was not runnable in the Python pilot.",
    "The source-reported RST-01 pilot values belong to clipped-input, linear-interpolation and band-limited POCS controls; no toolbox or C-OMP row exists.",
    "The merged band-limited POCS, linear-interpolation and C-OMP packages are separate controls with their own fixtures and results.",
    "No provider, processor, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, workload, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "source_checkout",
        "path": MISSING_SOURCE_PATH,
        "recorded_url": UPSTREAM_REPO_URL,
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
        "id": "matlab_runtime",
        "path": MATLAB_ENV_PATH,
        "install_path": MATLAB_INSTALL_PATH,
        "environment_manifest": MATLAB_ENV_MANIFEST_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "ltfat_runtime",
        "path": LTFAT_PATH,
        "manifest_path": LTFAT_MANIFEST_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "cvx_optional_solver",
        "path": CVX_PATH,
        "manifest_path": CVX_MANIFEST_PATH,
        "optional": True,
        "required_for_c_omp_comparison": True,
        "required": True,
        "status": "absent",
    },
    {
        "id": "source_license_record",
        "required": True,
        "status": "absent",
    },
    {
        "id": "documented_tool_use",
        "path": REFERENCE_EXPERIMENT_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "rights_and_cohort",
        "path": RIGHTS_RECORD_PATH,
        "cohort_path": COHORT_MANIFEST_PATH,
        "output_use_grant_path": OUTPUT_USE_GRANT_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "parity_vector",
        "path": PARITY_MANIFEST_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
)

CALLER_ASSET_FIELDS = (
    "source_checkout_path",
    "source_revision",
    "matlab_runtime_path",
    "matlab_version",
    "ltfat_path",
    "ltfat_revision",
    "cvx_path",
    "cvx_revision",
    "tool_version",
    "tool_install_path",
    "config_path",
    "config_sha256",
    "license_record_path",
    "license_record_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "reference_experiment_path",
    "reference_experiment_sha256",
    "cohort_manifest_path",
    "cohort_manifest_sha256",
    "parity_vector_path",
    "parity_vector_sha256",
    "output_use_grant_path",
    "output_use_grant_sha256",
    "sample_rate_hz",
    "channels",
    "block_samples",
    "variant",
)

CALLER_FILE_PAIRS = (
    ("config_path", "config_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("reference_experiment_path", "reference_experiment_sha256"),
    ("cohort_manifest_path", "cohort_manifest_sha256"),
    ("parity_vector_path", "parity_vector_sha256"),
    ("output_use_grant_path", "output_use_grant_sha256"),
)
CALLER_DIR_FIELDS = (
    "source_checkout_path",
    "matlab_runtime_path",
    "ltfat_path",
    "cvx_path",
    "tool_install_path",
)
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_VARIANT = "isolated_offline_toolbox_adapter"
MIN_BLOCK_SAMPLES = SDK_FRAME_SAMPLES
MAX_BLOCK_SAMPLES = 65_536

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id":
        "audio-sdk/matlab-ltfat-cvx-tools/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_revision_tool_version_geometry_and_"
        "isolated_offline_variant_only; do_not_import_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_source_revision": UPSTREAM_REVISION,
    "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
    "required_geometry": {
        "channels": CHANNELS,
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "block_samples": None,
        "status": TASK_GEOMETRY_STATUS,
    },
    "required_dependencies": list(REPORTED_DEPENDENCIES),
    "notes": (
        "Every source, MATLAB, LTFAT and CVX path, toolbox version, install "
        "location, experiment config, licence, rights record, documented tool "
        "use, cohort manifest, parity vector and output-use grant must exist at "
        "an absolute path and match its declared SHA-256 or revision before a "
        "caller may process audio. No upstream revision is pinned because the "
        "merged evidence records only project and repository URLs; a "
        "shape-valid manifest cannot manufacture qualification."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "toolbox_source_checkout_absent",
        "state": "absent",
        "requirement": (
            "Supply the exact declipping2020_codes source checkout at an "
            "immutable 40-hex revision under data/checkouts/declipping2020_codes "
            "or a recorded alias; no checkout exists in the workspace."),
    },
    {
        "id": "upstream_revision_unpinned",
        "state": "absent",
        "requirement": (
            "Resolve https://github.com/rajmic/declipping2020_codes to a full "
            "40-hex commit and publish its per-file SHA-256 manifest plus the "
            "toolbox release version; the merged evidence records only project "
            "and repository URLs."),
    },
    {
        "id": "matlab_runtime_absent",
        "state": "absent",
        "requirement": (
            "Provide one licensed MATLAB installation (proprietary, licensed "
            "product) with exact release/update identifier, recorded platform "
            "and install location, and an environment manifest at "
            "data/envs/matlab-ltfat-cvx/environment.json; no MATLAB "
            "installation is present."),
    },
    {
        "id": "ltfat_runtime_absent",
        "state": "absent",
        "requirement": (
            "Provide LTFAT at an exact 40-hex revision with a per-file SHA-256 "
            "manifest at data/toolboxes/ltfat/manifest.json and its licence "
            "terms; no LTFAT checkout is present and no revision is recorded."),
    },
    {
        "id": "cvx_optional_solver_absent",
        "state": "absent",
        "requirement": (
            "Provide the optional CVX solver path at an exact 40-hex revision "
            "with a per-file SHA-256 manifest at data/toolboxes/cvx/manifest.json "
            "for the C-OMP comparison, or record an approved alternative; no "
            "CVX checkout is present and no revision is recorded."),
    },
    {
        "id": "documented_tool_use_absent",
        "state": "absent",
        "requirement": (
            "Record one documented typical tool use: exact invocation, "
            "dictionary/frame, window and hop, block length, clipping "
            "threshold and mask policy, sparsity or target cardinality, "
            "stopping tolerance, iteration cap, regularization and expected "
            "numeric output. The merged research document reports only that "
            "the authors' toolbox needs MATLAB, LTFAT and CVX and was not "
            "runnable in the Python pilot."),
    },
    {
        "id": "vendor_terms_and_rights_unverified",
        "state": "absent",
        "requirement": (
            "Add the declipping2020_codes licence and terms at the resolved "
            "commit, the MATLAB licence basis and activation constraints, the "
            "LTFAT and CVX licence terms, and source-audio, clean-reference "
            "and redistribution/product-use rights with notices; no licence "
            "file, terms statement, grant or rights record exists."),
    },
    {
        "id": "isolated_adapter_and_parity_absent",
        "state": "absent",
        "requirement": (
            "Produce one approved exact-runtime output from an isolated, "
            "licensed environment, a frozen parity vector at "
            "data/runs/matlab-ltfat-cvx-tools-parity/manifest.json, and "
            "separated compile/build, synthetic runtime and measured workload "
            "evidence; no adapter prototype, output, parity vector or timing "
            "result exists."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_tool_identity",
        "The full 40-hex toolbox/LTFAT/CVX revisions, MATLAB release identity, "
        "toolbox version, install location, experiment config and metadata "
        "SHA-256 values and the source licence match exact pins.",
    ),
    (
        "runtime_and_toolbox_admission",
        "An isolated, licensed MATLAB runtime plus LTFAT and the optional CVX "
        "path with a complete environment manifest is admitted on a recorded "
        "platform.",
    ),
    (
        "artifact_rights_and_licence",
        "Toolbox, MATLAB, LTFAT, CVX, source-audio, clean-reference, "
        "output-use and redistribution rights are cleared with notices.",
    ),
    (
        "clean_install_and_typical_use",
        "A clean checkout or extracted package is verified and one documented "
        "typical CLI/API use produces a reproducible numeric result.",
    ),
    (
        "malformed_and_missing_optional_inputs",
        "Caller-owned inputs are validated and malformed inputs plus missing "
        "optional selections are rejected before processing.",
    ),
    (
        "vendor_boundary_and_disclosure",
        "Allowed access, exact candidate data, local runtime versus "
        "vendor-output scoring versus vendor claim, fallback and disclosure "
        "without a licensed runtime are documented and approved.",
    ),
    (
        "opt_in_adapter_intake",
        "Explicit opt-in adapter intake, licence review and an independent "
        "public-surface decision are complete; the component remains optional.",
    ),
    (
        "public_default_and_release",
        "Explicit default selection, resource/deadline evidence and release or "
        "public-benchmark approval are recorded; this package is off by default.",
    ),
)

TOOL_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "version_install_location_and_provenance",
        "Record the tool version, exact install location and upstream "
        "provenance with a pinned revision and per-file digest.",
        "absent",
    ),
    (
        "clean_checkout_or_extracted_package",
        "Verify a clean checkout or extracted package, including the MATLAB, "
        "LTFAT and optional CVX dependencies.",
        "absent",
    ),
    (
        "typical_cli_or_api_use",
        "Run one typical documented CLI/API use and record its exact output.",
        "absent",
    ),
    (
        "caller_owned_inputs",
        "Accept caller-owned inputs only after absolute-path, digest, revision "
        "and geometry validation.",
        "structural_only",
    ),
    (
        "malformed_inputs",
        "Reject malformed, nonfinite, duplicate-key and out-of-range inputs "
        "before use.",
        "synthetic_only",
    ),
    (
        "missing_optional_selections",
        "Handle missing optional selections explicitly, including an absent "
        "CVX path, without silently substituting a different method.",
        "synthetic_only",
    ),
    (
        "evidence_class_separation",
        "Separate compile/build evidence, synthetic runtime evidence and "
        "measured workload support as distinct outcomes.",
        "structural_only",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "source": "research/distortion_restoration_20261028.md",
    "source_sha256": SOURCE_PINS[
        "research/distortion_restoration_20261028.md"],
    "evidence_line": 42,
    "task_family": "RST-01 declipping/saturation",
    "inventory_record": COMPONENT,
    "inventory_status": "blocked",
    "inventory_disposition": "external-adapter",
    "record_name": TITLE,
    "project_url": UPSTREAM_PROJECT_URL,
    "repository_url": UPSTREAM_REPO_URL,
    "reported_toolbox": REPORTED_TOOLBOX,
    "reported_method": REPORTED_METHOD,
    "reported_optional_cvx_path": REPORTED_OPTIONAL_CVX_PATH,
    "reported_dependencies": list(REPORTED_DEPENDENCIES),
    "reported_license": REPORTED_LICENSE,
    "source_reported_revision": None,
    "source_reported_numeric_result": False,
    "pilot_source": (
        "reports/distortion-restoration/20261028-synthetic-screen.json"),
    "pilot_source_sha256": SOURCE_PINS[
        "reports/distortion-restoration/20261028-synthetic-screen.json"],
    "pilot_methods_for_rst_01": [
        "clipped_input",
        "linear_interpolation",
        "bandlimited_POCS",
    ],
    "pilot_thresholds": [0.35, 0.55],
    "pilot_c_omp_row_present": False,
    "pilot_source_reported_values": {
        "threshold_0_35": {
            "clipped_input_si_sdr_db": 14.794303531410954,
            "linear_interpolation_si_sdr_db": 10.989719355161837,
            "bandlimited_pocs_si_sdr_db": 15.050125728660396,
        },
        "threshold_0_55": {
            "clipped_input_si_sdr_db": 22.76335728125356,
            "linear_interpolation_si_sdr_db": 17.8638535865987,
            "bandlimited_pocs_si_sdr_db": 23.32441494144946,
        },
    },
    "sibling_context_not_attributed": [
        "The band-limited POCS package is a separate synthetic offline control "
        "with its own fixtures and claims; it is not toolbox evidence.",
        "The linear-interpolation package is a separate synthetic comparator "
        "on an exact known mask; it is not toolbox evidence.",
        "The C-OMP package is a separate blocker package that also records "
        "MATLAB/LTFAT/CVX absence; its controls are not attributed here.",
        "All sibling packages list toolbox parity as not run, so their results "
        "cannot be attributed to this candidate.",
        "The source pilot reports clipped-input, linear-interpolation and POCS "
        "values only; the screen JSON has no toolbox or C-OMP method row.",
        "No MATLAB/LTFAT/CVX source, revision, experiment or numeric output is "
        "pinned in the merged evidence.",
    ],
    "notes": (
        "The merged document names the authors' open MATLAB toolbox as the "
        "established next constrained sparse comparison and states that it "
        "requires MATLAB, LTFAT and (for C-OMP) CVX, so it was not runnable in "
        "the Python pilot. No toolbox output, score or runtime is attributed "
        "here."),
}

EXTERNAL_ADAPTER_BOUNDARY: Dict[str, Any] = {
    "boundary": "vendor_documented_external_tool_no_adapter_built",
    "allowed_access_documented": False,
    "allowed_access_basis": None,
    "exact_candidate_or_processed_data": None,
    "local_runtime_present": False,
    "vendor_output_scoring_present": False,
    "vendor_claim_present": False,
    "fallback_without_licensed_runtime": (
        "the merged sibling synthetic controls remain the only available "
        "evidence, and they do not reproduce or approximate the toolbox"),
    "fallback_requires_no_licensed_asset": True,
    "disclosure_without_licensed_runtime": (
        "report the absent MATLAB/LTFAT/CVX runtime and the resulting blocker; "
        "never present a sibling control as the toolbox method"),
    "adapter_prototype_created": False,
    "adapter_prototype_condition": (
        "only if an approved public or user-supplied MATLAB/LTFAT/CVX runtime "
        "is supplied at exact pins; no such runtime is present"),
    "separation": {
        "compile_or_build_evidence": "absent",
        "synthetic_runtime_evidence": "structural_accounting_only",
        "measured_workload_support": "absent",
        "vendor_output_scoring": "absent",
        "vendor_claim": "absent",
    },
    "matlab_dependency_added": False,
    "toolbox_vendored": False,
    "network_used": False,
    "notes": (
        "The vendor boundary is documented, not bridged. MATLAB is a "
        "proprietary licensed product; LTFAT and the optional CVX path are "
        "caller-supplied dependencies. Nothing is downloaded, vendored, "
        "registered or invoked, and no adapter JSON is added."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_exact_clipping_mask_accounting_plan_"
    "not_toolbox_or_c_omp_output")

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
    "config_not_object",
    "config_missing_field",
    "config_extra_field",
    "threshold_zero",
    "threshold_one",
    "threshold_negative",
    "threshold_above_one",
    "threshold_nan",
    "threshold_pos_inf",
    "threshold_neg_inf",
    "threshold_bool",
    "threshold_string",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_short_revision",
    "manifest_nonhex_revision",
    "manifest_bad_ltfat_revision",
    "manifest_bad_cvx_revision",
    "manifest_empty_matlab_version",
    "manifest_empty_tool_version",
    "manifest_wrong_variant",
    "manifest_wrong_rate",
    "manifest_wrong_channels",
    "manifest_block_too_small",
    "manifest_block_not_aligned",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_missing_tool_install",
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


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


# ---------------------------------------------------------------------------
# Source checkout, toolbox, runtime and absence audit.  Fixed local reads only.
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
    return [SOURCE_ROOT / relative
            for relative in (MISSING_SOURCE_PATH, *MISSING_SOURCE_ALIASES)]


def _toolbox_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / LTFAT_PATH,
        SOURCE_ROOT / "data/checkouts/LTFAT",
        SOURCE_ROOT / "data/checkouts/ltfat",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/ltfat",
    ]


def _cvx_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / CVX_PATH,
        SOURCE_ROOT / "data/checkouts/CVX",
        SOURCE_ROOT / "data/checkouts/cvx",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/cvx",
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
    matlab_env = SOURCE_ROOT / MATLAB_ENV_PATH
    matlab_manifest = SOURCE_ROOT / MATLAB_ENV_MANIFEST_PATH
    matlab_install = SOURCE_ROOT / MATLAB_INSTALL_PATH
    ltfat_paths = _toolbox_candidates()
    cvx_paths = _cvx_candidates()
    ltfat_present = any(path.is_dir() for path in ltfat_paths)
    cvx_present = any(path.is_dir() for path in cvx_paths)
    matlab_present = (
        shutil.which("matlab") is not None or matlab_install.is_dir())
    octave_present = shutil.which("octave") is not None
    reference_experiment = SOURCE_ROOT / REFERENCE_EXPERIMENT_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    parity_manifest = SOURCE_ROOT / PARITY_MANIFEST_PATH
    output_use_grant = SOURCE_ROOT / OUTPUT_USE_GRANT_PATH
    adapter_prototype = SOURCE_ROOT / ADAPTER_PROTOTYPE_PATH
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
        "matlab_env_present": matlab_env.is_dir(),
        "matlab_env_manifest_present": matlab_manifest.is_file(),
        "matlab_install_present": matlab_install.is_dir(),
        "matlab_present": matlab_present,
        "octave_present": octave_present,
        "ltfat_present": ltfat_present,
        "ltfat_manifest_present": (SOURCE_ROOT / LTFAT_MANIFEST_PATH).is_file(),
        "cvx_present": cvx_present,
        "cvx_manifest_present": (SOURCE_ROOT / CVX_MANIFEST_PATH).is_file(),
        "complete_runtime_present": bool(
            matlab_present and ltfat_present and cvx_present),
        "reference_experiment_present": reference_experiment.is_file(),
        "rights_record_present": rights_record.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "parity_manifest_present": parity_manifest.is_file(),
        "output_use_grant_present": output_use_grant.is_file(),
        "adapter_prototype_present": adapter_prototype.is_file(),
        "runtime_probes": {
            "matlab": matlab_present,
            "octave": octave_present,
            "ltfat": ltfat_present,
            "cvx": cvx_present,
        },
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "geometry_status": TASK_GEOMETRY_STATUS,
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_source_samples": CONTROL_SOURCE_SAMPLES,
            "upstream_revision": UPSTREAM_REVISION,
            "pinned_candidate_source": False,
            "reported_dependencies": list(REPORTED_DEPENDENCIES),
            "reported_optional_cvx_path": REPORTED_OPTIONAL_CVX_PATH,
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
# Deterministic synthetic PCM and exact clipping-mask accounting.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_clean_pcm(scale: float = 1.0) -> List[float]:
    """Deterministic binary32 clean surrogate, peak <= 0.90 * scale."""
    if isinstance(scale, bool) or not isinstance(scale, (int, float)):
        raise Reject("scale must be numeric")
    scale_value = float(scale)
    if not math.isfinite(scale_value) or scale_value <= 0.0:
        raise Reject("scale must be finite and positive")
    raw: List[float] = []
    state = 0x434F4D50
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        raw.append(0.55 * _triangle(index, 37, 1.0)
                   + 0.30 * _triangle(index, 53, 1.0)
                   + 0.01 * noise)
    peak = max(abs(value) for value in raw)
    factor = (0.90 * scale_value) / peak
    return [_f32(value * factor) for value in raw]


def validate_pcm(signal: Any, sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ,
                 channels: int = CHANNELS) -> List[float]:
    if isinstance(sample_rate_hz, bool) or not isinstance(sample_rate_hz, int):
        raise Reject("sample rate must be an integer")
    if sample_rate_hz != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("unsupported control sample rate")
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise Reject("channels must be an integer")
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


def validate_threshold(threshold: Any) -> float:
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise Reject("threshold must be numeric")
    value = float(threshold)
    if not math.isfinite(value):
        raise Reject("threshold must be finite")
    if value <= 0.0 or value >= 1.0:
        raise Reject("threshold must be strictly between 0 and 1")
    quantized = _f32(value)
    if quantized <= 0.0 or quantized >= 1.0:
        raise Reject("quantized threshold is outside (0, 1)")
    return quantized


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


def validate_clip_config(config: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        raise Reject("config must be an object")
    expected = {"threshold", "sample_rate_hz", "channels"}
    present = set(config)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing:
        raise Reject("config missing fields: " + ",".join(missing))
    if extra:
        raise Reject("config has unknown fields: " + ",".join(extra))
    threshold = validate_threshold(config["threshold"])
    sample_rate = config["sample_rate_hz"]
    if isinstance(sample_rate, bool) or not isinstance(sample_rate, int):
        raise Reject("config sample_rate_hz must be an integer")
    if sample_rate != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("config sample_rate_hz mismatch")
    channels = config["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise Reject("config channels must be an integer")
    if channels != CHANNELS:
        raise Reject("config channels mismatch")
    return {
        "threshold": threshold,
        "sample_rate_hz": sample_rate,
        "channels": channels,
    }


def hard_clip_pcm(clean_signal: Any, threshold: Any) -> Tuple[List[float], float]:
    """Return binary32 hard-clipped samples and the exact binary32 threshold."""
    values = validate_pcm(clean_signal)
    clipped_threshold = validate_threshold(threshold)
    clipped = [_f32(min(max(value, -clipped_threshold), clipped_threshold))
               for value in values]
    return clipped, clipped_threshold


def clipping_mask(clean_signal: Any,
                  threshold: Any) -> Tuple[List[float], float, List[bool]]:
    clipped, clipped_threshold = hard_clip_pcm(clean_signal, threshold)
    mask = [abs(value) == clipped_threshold for value in clipped]
    return clipped, clipped_threshold, mask


def _mask_intervals(mask: Sequence[bool]) -> List[Dict[str, Any]]:
    intervals: List[Dict[str, Any]] = []
    start: Optional[int] = None
    for index, flag in enumerate(mask):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            intervals.append({
                "start": start,
                "end": index,
                "duration_samples": index - start,
                "start_ns": str(start * NS_PER_SAMPLE),
                "end_ns": str(index * NS_PER_SAMPLE),
                "duration_ns": str((index - start) * NS_PER_SAMPLE),
            })
            start = None
    if start is not None:
        end = len(mask)
        intervals.append({
            "start": start,
            "end": end,
            "duration_samples": end - start,
            "start_ns": str(start * NS_PER_SAMPLE),
            "end_ns": str(end * NS_PER_SAMPLE),
            "duration_ns": str((end - start) * NS_PER_SAMPLE),
        })
    return intervals


def clipping_accounting(clean_signal: Any, threshold: Any,
                        sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ,
                        channels: int = CHANNELS) -> Dict[str, Any]:
    """Exact mask accounting only.  No reconstruction or sparse recovery."""
    values = validate_pcm(clean_signal, sample_rate_hz, channels)
    clipped, clipped_threshold, mask = clipping_mask(values, threshold)
    masked_indices = [index for index, flag in enumerate(mask) if flag]
    unmasked_indices = [index for index, flag in enumerate(mask) if not flag]
    exact_mask = all(abs(clipped[index]) == clipped_threshold
                     for index in masked_indices)
    unmasked_preserved = all(clipped[index] == values[index]
                             for index in unmasked_indices)
    no_false_negative = all(abs(values[index]) > clipped_threshold
                            for index in masked_indices)
    intervals = _mask_intervals(mask)
    clipped_peak = max(abs(value) for value in clipped)
    clean_peak = max(abs(value) for value in values)
    occupancy = Fraction(len(masked_indices), len(values))
    mask_bits = [1 if flag else 0 for flag in mask]
    return {
        "input_samples": len(values),
        "output_samples": len(clipped),
        "sample_rate_hz": sample_rate_hz,
        "channels": channels,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "output_duration_s": fraction_text(
            Fraction(len(clipped), sample_rate_hz)),
        "duration_ratio": "1",
        "duration_conserved": len(clipped) == len(values),
        "source_clock_ns_per_sample": NS_PER_SAMPLE,
        "threshold_input": float(threshold)
        if not isinstance(threshold, bool) else None,
        "threshold_binary32": clipped_threshold,
        "input_peak_abs": clean_peak,
        "output_peak_abs": clipped_peak,
        "output_within_input_peak": clipped_peak <= clean_peak,
        "output_within_threshold": clipped_peak <= clipped_threshold,
        "masked_samples": len(masked_indices),
        "unmasked_samples": len(unmasked_indices),
        "occupancy_fraction": fraction_text(occupancy),
        "occupancy_percent": float(occupancy * 100),
        "exact_mask": exact_mask,
        "unmasked_preserved": unmasked_preserved,
        "mask_has_no_false_negatives": no_false_negative,
        "mask_interval_count": len(intervals),
        "mask_intervals": intervals,
        "mask_bits_sha256": sha256(canonical_bytes(mask_bits)),
        "clean_pcm_sha256": sha256(canonical_bytes(list(values))),
        "clipped_pcm_sha256": sha256(canonical_bytes(list(clipped))),
        "reconstruction_performed": False,
        "toolbox_executed": False,
        "c_omp_executed": False,
        "sparse_recovery_performed": False,
        "quality_metrics": None,
        "candidate_output": False,
        "qualification_effect": "none",
        "status": "complete_synthetic_accounting",
        "note": (
            "Exact binary32 clipping mask accounting only. The clipped input "
            "is a damaged baseline, not a declipped output; no toolbox, C-OMP, "
            "sparse recovery, interpolation, quality metric or listening result "
            "is produced."),
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    good_input = synthetic_clean_pcm()
    good_config = {
        "threshold": CONTROL_THRESHOLDS[0],
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
    }
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

    def config_with(key: str, value: Any):
        config = dict(good_config)
        config[key] = value
        return lambda: validate_clip_config(config)

    def config_without(key: str):
        config = {k: v for k, v in good_config.items() if k != key}
        return lambda: validate_clip_config(config)

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
        ("config_not_object", lambda: validate_clip_config([])),
        ("config_missing_field", config_without("threshold")),
        ("config_extra_field", lambda: validate_clip_config(
            dict(good_config, extra_field=1))),
        ("threshold_zero", lambda: validate_threshold(0)),
        ("threshold_one", lambda: validate_threshold(1)),
        ("threshold_negative", lambda: validate_threshold(-0.1)),
        ("threshold_above_one", lambda: validate_threshold(1.1)),
        ("threshold_nan", lambda: validate_threshold(math.nan)),
        ("threshold_pos_inf", lambda: validate_threshold(math.inf)),
        ("threshold_neg_inf", lambda: validate_threshold(-math.inf)),
        ("threshold_bool", lambda: validate_threshold(True)),
        ("threshold_string", lambda: validate_threshold("0.35")),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("config_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "config_path", "config/experiment.json")),
        ("manifest_bad_sha", wrong("config_sha256", "ABC")),
        ("manifest_short_revision", wrong("source_revision", "7dae8a2")),
        ("manifest_nonhex_revision", wrong("source_revision", "g" * 40)),
        ("manifest_bad_ltfat_revision", wrong("ltfat_revision", "short")),
        ("manifest_bad_cvx_revision", wrong("cvx_revision", "z" * 40)),
        ("manifest_empty_matlab_version", wrong("matlab_version", "")),
        ("manifest_empty_tool_version", wrong("tool_version", "  ")),
        ("manifest_wrong_variant", wrong("variant", "incremental_streaming")),
        ("manifest_wrong_rate", wrong("sample_rate_hz", 48000)),
        ("manifest_wrong_channels", wrong("channels", 2)),
        ("manifest_block_too_small", wrong("block_samples", 0)),
        ("manifest_block_not_aligned", wrong("block_samples", 1001)),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, config_path=(
                "/nonexistent/matlab-ltfat-cvx-evidence/config.json")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, matlab_runtime_path=(
                "/nonexistent/matlab-ltfat-cvx-evidence/no-matlab")))),
        ("manifest_missing_tool_install", lambda: validate_caller_manifest(
            dict(existing, tool_install_path=(
                "/nonexistent/matlab-ltfat-cvx-evidence/no-tool")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, config_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    if [item["case"] for item in results] != list(ADVERSE_CASE_IDS):
        raise Reject("adverse case order mismatch")
    if any(item["result"] != "rejected" for item in results):
        raise Reject("an adverse control was not rejected")
    return results


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It is only used to exercise fail-closed shape checks.  Validation reaches
    the missing-asset branch before any file is read.
    """

    root = "/nonexistent/matlab-ltfat-cvx-tools-evidence-fixture"
    digest = "0" * 64
    return {
        "source_checkout_path": root + "/source",
        "source_revision": "0" * 40,
        "matlab_runtime_path": root + "/matlab",
        "matlab_version": "R0000a",
        "ltfat_path": root + "/ltfat",
        "ltfat_revision": "0" * 40,
        "cvx_path": root + "/cvx",
        "cvx_revision": "0" * 40,
        "tool_version": "0.0.0",
        "tool_install_path": root + "/tool",
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "license_record_path": root + "/license.json",
        "license_record_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "reference_experiment_path": root + "/expected.json",
        "reference_experiment_sha256": digest,
        "cohort_manifest_path": root + "/cohort.json",
        "cohort_manifest_sha256": digest,
        "parity_vector_path": root + "/parity.json",
        "parity_vector_sha256": digest,
        "output_use_grant_path": root + "/output-use-grant.json",
        "output_use_grant_sha256": digest,
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "block_samples": 1600,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package.

    It exercises file hashing and directory checks without reading audio or
    loading a model.  Duplicate paths are allowed; each pair carries the real
    digest so a single corrupted digest reaches the SHA-256 mismatch branch.
    """

    assignments = {
        "config_path": HERE / "README.md",
        "license_record_path": HERE / "verify.py",
        "rights_record_path": HERE / "run.py",
        "reference_experiment_path": HERE / "reference.py",
        "cohort_manifest_path": HERE / "test_reference.py",
        "parity_vector_path": HERE / "README.md",
        "output_use_grant_path": HERE / "reference.py",
    }
    manifest: Dict[str, Any] = {
        "source_checkout_path": str(HERE),
        "source_revision": "a" * 40,
        "matlab_runtime_path": str(SDK_ROOT),
        "matlab_version": "R0000a",
        "ltfat_path": str(HERE),
        "ltfat_revision": "b" * 40,
        "cvx_path": str(HERE),
        "cvx_revision": "c" * 40,
        "tool_version": "0.0.0",
        "tool_install_path": str(HERE),
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "block_samples": 1600,
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


def _revision_field(manifest: Dict[str, Any], field: str) -> str:
    value = manifest[field]
    if not isinstance(value, str) or not COMMIT_PATTERN.fullmatch(value):
        raise Reject("manifest " + field + " must be a full 40-hex commit")
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
    revision = _revision_field(manifest, "source_revision")
    ltfat_revision = _revision_field(manifest, "ltfat_revision")
    cvx_revision = _revision_field(manifest, "cvx_revision")
    matlab_version = manifest["matlab_version"]
    if not isinstance(matlab_version, str) or not matlab_version.strip():
        raise Reject("manifest matlab_version must be a nonempty string")
    tool_version = manifest["tool_version"]
    if not isinstance(tool_version, str) or not tool_version.strip():
        raise Reject("manifest tool_version must be a nonempty string")
    sample_rate = _int_field(manifest, "sample_rate_hz")
    if sample_rate != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("manifest sample_rate_hz mismatch")
    channels = _int_field(manifest, "channels")
    if channels != CHANNELS:
        raise Reject("manifest channels mismatch")
    block_samples = _int_field(manifest, "block_samples")
    if block_samples < MIN_BLOCK_SAMPLES or block_samples > MAX_BLOCK_SAMPLES:
        raise Reject("manifest block_samples is outside the admitted range")
    if block_samples % SDK_FRAME_SAMPLES != 0:
        raise Reject("manifest block_samples must align to the SDK frame")
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
        "ltfat_revision": ltfat_revision,
        "cvx_revision": cvx_revision,
        "matlab_version": matlab_version,
        "tool_version": tool_version,
        "variant": CALLER_VARIANT,
        "sample_rate_hz": sample_rate,
        "channels": CHANNELS,
        "block_samples": block_samples,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "toolbox_executed": False,
        "c_omp_executed": False,
        "sparse_recovery_performed": False,
    }


def _case(case_id: str, clean: Sequence[float],
          config: Dict[str, Any]) -> Dict[str, Any]:
    checked = validate_clip_config(config)
    accounting = clipping_accounting(
        clean, checked["threshold"], checked["sample_rate_hz"],
        checked["channels"])
    source_summary = pcm_summary(clean, checked["sample_rate_hz"])
    clipped = hard_clip_pcm(clean, checked["threshold"])[0]
    clipped_summary = pcm_summary(clipped, checked["sample_rate_hz"])
    return {
        "id": case_id,
        "configuration": {
            "threshold": checked["threshold"],
            "sample_rate_hz": checked["sample_rate_hz"],
            "channels": checked["channels"],
            "mode": "exact_clipping_mask_accounting",
        },
        "input": source_summary,
        "clipped_baseline": clipped_summary,
        "accounting": accounting,
        "status": "complete_synthetic_accounting",
        "candidate_output": False,
        "qualification_effect": "none",
    }


def build_control() -> Dict[str, Any]:
    clean = synthetic_clean_pcm()
    quiet = synthetic_clean_pcm(QUIET_SCALE)
    cases = [
        _case("clipped_0_35", clean, {
            "threshold": CONTROL_THRESHOLDS[0],
            "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
        }),
        _case("clipped_0_55", clean, {
            "threshold": CONTROL_THRESHOLDS[1],
            "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
        }),
        _case("quiet_no_clip_0_55", quiet, {
            "threshold": QUIET_THRESHOLD,
            "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
        }),
    ]
    for item in cases:
        if item["accounting"]["exact_mask"] is not True:
            raise Reject("a control case did not produce an exact mask")
        if item["accounting"]["unmasked_preserved"] is not True:
            raise Reject("a control case changed an unmasked sample")
        if item["accounting"]["output_within_threshold"] is not True:
            raise Reject("a clipped baseline exceeded its threshold")
    if cases[2]["accounting"]["masked_samples"] != 0:
        raise Reject("the quiet no-clip control produced clipped samples")
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "toolbox_executed": False,
        "c_omp_executed": False,
        "matlab_invoked": False,
        "ltfat_loaded": False,
        "cvx_loaded": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "tool_provenance": {
            "tool_name": REPORTED_TOOLBOX,
            "tool_version": None,
            "install_location": None,
            "upstream_revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "clean_checkout_or_package_verified": False,
            "typical_use_run": False,
        },
        "geometry": {
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_source_samples": CONTROL_SOURCE_SAMPLES,
            "control_seconds": CONTROL_SECONDS,
            "task_geometry_status": TASK_GEOMETRY_STATUS,
            "task_geometry_asserted": False,
            "mode": "offline_exact_clipping_mask_accounting",
            "incremental_streaming": False,
            "performs_sparse_recovery": False,
            "performs_declipping": False,
            "performs_interpolation": False,
        },
        "cases": cases,
        "acceptance_outcomes": [
            {
                "id": "version_install_location_and_provenance",
                "measured": False,
                "value": None,
                "reason": "no toolbox checkout, version or install location exists",
            },
            {
                "id": "clean_checkout_or_extracted_package",
                "measured": False,
                "value": None,
                "reason": "no clean checkout, extracted package or runtime manifest",
            },
            {
                "id": "typical_cli_or_api_use",
                "measured": False,
                "value": None,
                "reason": "no MATLAB/LTFAT/CVX runtime to run one documented use",
            },
            {
                "id": "caller_owned_inputs",
                "measured": False,
                "value": None,
                "reason": "only shape/digest validation is exercised; no audio processed",
            },
            {
                "id": "malformed_inputs",
                "measured": False,
                "value": None,
                "reason": "synthetic rejection control only; no tool invocation",
            },
            {
                "id": "missing_optional_selections",
                "measured": False,
                "value": None,
                "reason": "the optional CVX path is absent and not exercised",
            },
            {
                "id": "evidence_class_separation",
                "measured": False,
                "value": None,
                "reason": "compile/build, runtime and workload evidence are all absent",
            },
            {
                "id": "parity_vector",
                "measured": False,
                "value": None,
                "reason": "no approved exact-runtime toolbox output",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf",
                "threshold_nan", "threshold_pos_inf", "threshold_neg_inf"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range",
                "pcm_wrong_rate", "pcm_stereo",
                "threshold_zero", "threshold_one", "threshold_negative",
                "threshold_above_one", "threshold_bool", "threshold_string",
                "manifest_bad_ltfat_revision", "manifest_bad_cvx_revision",
                "manifest_empty_matlab_version", "manifest_empty_tool_version",
                "manifest_wrong_variant", "manifest_wrong_rate",
                "manifest_wrong_channels", "manifest_block_too_small",
                "manifest_block_not_aligned"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "config_missing_field", "manifest_missing_field",
                "manifest_missing_asset", "manifest_missing_directory",
                "manifest_missing_tool_install"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic exact-clipping-mask accounting only. It performs no "
            "toolbox, C-OMP, sparse recovery, interpolation or declipping "
            "step, is not candidate output, not real speech, not a quality, "
            "workload or timing result and cannot qualify the candidate."),
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
        and observed["complete_runtime_present"]
        and observed["reference_experiment_present"]
        and observed["rights_record_present"]
        and observed["cohort_manifest_present"]
        and observed["parity_manifest_present"]
        and observed["output_use_grant_present"])
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
        "matlab_env_present": observed["matlab_env_present"],
        "matlab_env_manifest_present": observed[
            "matlab_env_manifest_present"],
        "matlab_install_present": observed["matlab_install_present"],
        "matlab_present": observed["matlab_present"],
        "octave_present": observed["octave_present"],
        "ltfat_present": observed["ltfat_present"],
        "ltfat_manifest_present": observed["ltfat_manifest_present"],
        "cvx_present": observed["cvx_present"],
        "cvx_manifest_present": observed["cvx_manifest_present"],
        "complete_runtime_present": observed["complete_runtime_present"],
        "reference_experiment_present": observed[
            "reference_experiment_present"],
        "rights_record_present": observed["rights_record_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "output_use_grant_present": observed["output_use_grant_present"],
        "adapter_prototype_present": observed["adapter_prototype_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No declipping2020_codes source, revision, MATLAB/LTFAT/CVX "
            "runtime, documented tool use, licence, rights record, cohort, "
            "parity vector or adapter prototype was observed. The sibling "
            "POCS, linear-interpolation and C-OMP packages are separate "
            "controls, not toolbox evidence."),
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
        for item, requirement, status in TOOL_REQUIREMENTS
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
                "The exact declipping2020_codes source checkout, full upstream "
                "revision, licensed MATLAB/LTFAT/CVX runtime, documented "
                "typical tool use, task geometry and hash-pinned environment "
                "are absent; no licence, rights record, rights-cleared "
                "clipped/clean cohort, clean reference, isolated adapter, "
                "parity vector or local toolbox output exists."),
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
            "project_url": UPSTREAM_PROJECT_URL,
            "repository_url": UPSTREAM_REPO_URL,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "reported_method": REPORTED_METHOD,
            "reported_toolbox": REPORTED_TOOLBOX,
            "reported_optional_cvx_path": REPORTED_OPTIONAL_CVX_PATH,
            "reported_dependencies": list(REPORTED_DEPENDENCIES),
            "reported_license": REPORTED_LICENSE,
            "reported_geometry_asserted": False,
            "geometry_status": TASK_GEOMETRY_STATUS,
        },
        "runtime_requirements": {
            "matlab": {
                "role": "proprietary licensed MATLAB runtime for the toolbox",
                "present": audit["matlab_present"],
                "install_present": audit["matlab_install_present"],
                "version": None,
                "licensed": False,
                "required": True,
            },
            "ltfat": {
                "role": "frame/dictionary dependency",
                "present": audit["ltfat_present"],
                "manifest_present": audit["ltfat_manifest_present"],
                "revision": None,
                "licensed": False,
                "required": True,
            },
            "cvx": {
                "role": "optional convex solver path for the C-OMP comparison",
                "present": audit["cvx_present"],
                "manifest_present": audit["cvx_manifest_present"],
                "revision": None,
                "licensed": False,
                "required": True,
                "optional_selection": True,
            },
            "complete_runtime_present": audit["complete_runtime_present"],
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "tool_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "measured_workload_metrics": None,
            "note": (
                "Only synthetic rejection/structural accounting is exercised; "
                "no toolbox checkout, version, install location, licensed "
                "MATLAB/LTFAT/CVX runtime, typical tool use, caller-owned "
                "audio run, measured workload, adapter prototype or approved "
                "parity exists, so the tool profile is not satisfied for "
                "qualification."),
        },
        "external_adapter_boundary": EXTERNAL_ADAPTER_BOUNDARY,
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "exact_mask_declared": True,
            "unmasked_samples_preserved": True,
            "toolbox_absent_and_not_executed": True,
            "adapter_prototype_absent": True,
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
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            MISSING_SOURCE_PATH,
            MATLAB_ENV_PATH,
            MATLAB_ENV_MANIFEST_PATH,
            MATLAB_INSTALL_PATH,
            LTFAT_PATH,
            LTFAT_MANIFEST_PATH,
            CVX_PATH,
            CVX_MANIFEST_PATH,
            REFERENCE_EXPERIMENT_PATH,
            RIGHTS_RECORD_PATH,
            COHORT_MANIFEST_PATH,
            PARITY_MANIFEST_PATH,
            OUTPUT_USE_GRANT_PATH,
            ADAPTER_PROTOTYPE_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no MATLAB, Octave, LTFAT, CVX, NumPy, SciPy or audio runtime is imported.",
            "Fixed workspace paths are probed for source, toolbox, runtime, documented tool use, rights and cohort presence.",
            "No source checkout is executed, no toolbox installation is inspected beyond fixed-path presence, and no audio byte is read.",
            "No isolated adapter prototype is generated or shipped.",
            "No network request, download, audio device, sparse solve or timing run occurs.",
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
            "project_url": UPSTREAM_PROJECT_URL,
            "repository_url": UPSTREAM_REPO_URL,
            "revision": None,
            "revision_pin_available": False,
        },
        "upstream_identity": report["upstream_identity"],
        "runtime_requirements": report["runtime_requirements"],
        "asset_requirements": report["asset_requirements"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "external_adapter_boundary": report["external_adapter_boundary"],
        "exact_blockers": report["exact_blockers"],
        "gates": report["gates"],
        "tool_profile_requirements": [
            {
                "id": item["id"],
                "requirement": item["requirement"],
                "package_status": item["package_status"],
            }
            for item in report["tool_profile"]["required_items"]
        ],
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
