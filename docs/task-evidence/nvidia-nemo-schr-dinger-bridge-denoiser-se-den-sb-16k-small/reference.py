# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local evidence for the NVIDIA NeMo Schrödinger-bridge denoiser (se_den_sb_16k_small) lane.

The pinned local records identify one candidate: NVIDIA NeMo
``nvidia/se_den_sb_16k_small``, a 16 kHz mono *utterance-level* generative
Schrödinger-bridge dereverberator.  The model card is reported to list NeMo 2.0
and CC BY-NC-SA 4.0, an SDE/ODE sampler over the complete clip, V100 testing and
WSJ0-Reverb scores.  It has no streaming API in the model card.

No local NeMo or PyTorch runtime exists, no checkpoint or config is present, the
upstream source revision was never established, and no rights entry, corpus,
exact output, listening result or device measurement exists.  The candidate is
therefore an explicit ``DEFER`` / ``incomplete`` / ``not_qualified`` blocker.

This module emits bounded, deterministic, stdlib-only evidence:

* fixed absence probes for candidate source, checkpoint, config, runtime,
  rights, parity and cohort artifacts;
* a caller-supplied-asset validator that hashes caller-owned files but never
  loads or executes them, and that always fails closed for the candidate;
* a **synthetic whole-clip denoising boundary surrogate** that proves deterministic
  full-utterance accounting, finite bounded output, exact silence preservation,
  statelessness, full-clip-only refusal and adverse/missing/invalid/nonfinite
  rejection.  The surrogate is not NeMo, contains no DNN, no weights, no
  sampler, no runtime and no real audio, and no surrogate observation may
  qualify the candidate.

Nothing here downloads, copies, imports, loads or executes NeMo, PyTorch, a
checkpoint, a runtime, a corpus or a device clock.  It does not register a
provider, change installed v0, a descriptor, a registry, a default, a shared
build, a dependency lock or CI, and it makes no listening, quality, timing,
benchmark or release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2]))).resolve()
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", str(SDK_ROOT.parents[2]))
).resolve()
if not (SOURCE_ROOT / "plan" / "INVENTORY.json").is_file():
    for _parent in HERE.parents:
        if (_parent / "adapters").is_dir() and (
            _parent / "audio-benchmark-platform"
        ).is_dir():
            SOURCE_ROOT = _parent
            break

TASK = "SDK-NVIDIA-NEMO-SCHR-DINGER-BRIDGE-DENOISER-SE-DEN-SB-16K-SMALL"
TITLE = "NVIDIA NeMo Schrödinger-bridge denoiser (se_den_sb_16k_small)"
SLUG = "nvidia-nemo-schr-dinger-bridge-denoiser-se-den-sb-16k-small"
COMPONENT = SLUG
MODE = "feasibility"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "9074704819a6af4168f8c9cf3bbe8da50484c29a"
BRANCH = f"swarm/{TASK}"
WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK
)
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "offline_checkpoint_staging_and_asset_admission"

CANDIDATE_MODEL_ID = "nvidia/se_den_sb_16k_small"
CANDIDATE_MODEL_CARD = "https://huggingface.co/nvidia/se_den_sb_16k_small"
CANDIDATE_SOURCE_REPOSITORY = "https://github.com/NVIDIA/NeMo"
CANDIDATE_SOURCE_REVISION = None
CANDIDATE_SOURCE_STATUS = "not_recorded"
CANDIDATE_LICENSE = "CC-BY-NC-SA-4.0"
CANDIDATE_LICENSE_STATUS = "upstream_reported_not_reviewed"
CANDIDATE_CHECKPOINT_ID = "se_den_sb_16k_small.nemo"
CANDIDATE_CHECKPOINT_BYTES = None
CANDIDATE_CHECKPOINT_SHA256 = None
CANDIDATE_CHECKPOINT_STATUS = "not_recorded"
CANDIDATE_RUNTIME = "NeMo 2.0 + PyTorch"
CANDIDATE_RUNTIME_STATUS = "not_installed"
CANDIDATE_GEOMETRY_STATUS = "unverified"
CANDIDATE_STREAMING_API = False
CANDIDATE_FRAME_GEOMETRY_KNOWN = False

SAMPLE_RATE_HZ = 16_000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
V0_FRAME_SAMPLES = 160
V0_SAMPLE_RATE_HZ = 16_000
V0_CHANNELS = 1

FIXTURE_FRAMES = 100
FIXTURE_BLOCK_SAMPLES = 160
FIXTURE_SAMPLES = FIXTURE_FRAMES * FIXTURE_BLOCK_SAMPLES
MAX_ABS_AUDIO = 1.0
SURROGATE_SAMPLER_STEPS = 4
SURROGATE_SEED = 2026_1126
SURROGATE_LATE_DELAY = 1024
CLOCK_ID = "fixture-whole-clip-coordinate-not-device"

INVENTORY_RECORD_ID = "nvidia-nemo-schr-dinger-bridge-denoiser-se-den-sb-16k-small"
INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"
RESEARCH_PATH = "research/noise_suppression_candidate_census.md"
RESEARCH_LINE = 70
ADAPTER_PATH = "research/noise_suppression_candidate_census.md"  # provenance-only if present; none expected
ADAPTER_LINE = 3
CENSUS_PATH = "research/noise_suppression_candidate_census.md"
VERIFICATION_PATH = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PLAN_README_PATH = "audio-benchmark-platform/plan/audio-sdk/README.md"
RIGHTS_REGISTER_PATH = "audio-benchmark-platform/audio-pro/docs/rights-register.md"
RIGHTS_JSON_PATH = "audio-benchmark-platform/audio-pro/inventory/rights-register.json"

RESEARCH_FINDING = (
    "16 kHz offline generative speech denoiser, WSJ0+CHiME; official NeMo "
    "Speech checkpoint catalog exposes a pretrained small Schrödinger-bridge "
    "denoising model and loading path; adjacent reverberation model excluded; "
    "pin NeMo release and checkpoint, inspect code/data/model terms, establish "
    "sampler and hardware cost, then measure alignment and speech-content "
    "preservation on the common set; published availability is not a local "
    "benchmark result"
)
ADAPTER_FINDING = (
    "No local nemo-denoiser adapter README is present in this worktree; the "
    "candidate is identified only by pinned census and inventory records. "
    "No NeMo or PyTorch runtime, checkpoint, config, exact revision, rights "
    "review, cohort or measured result is present."
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "model_id": CANDIDATE_MODEL_ID,
    "model_card": CANDIDATE_MODEL_CARD,
    "reported_license": CANDIDATE_LICENSE,
    "reported_runtime": CANDIDATE_RUNTIME,
    "reported_execution": "utterance_level_sde_ode_over_complete_clip",
    "reported_test_hardware": "NVIDIA V100",
    "reported_streaming_api": False,
    "reported_training_evaluation_corpus": "WSJ0+CHiME (upstream reported, unverified locally)",
    "reported_scores": "not locally reproduced; census reports official NeMo catalog availability only",
                "note": (
        "All values are upstream-reported in the pinned research record and "
        "adapter README. They are not local measurements, are not comparable "
        "to the local synthetic pilot, and no result is claimed here."
    ),
}

FIXED_ASSET_PROBES: Tuple[str, ...] = (
    "adapters/nemo-denoiser/checkpoint",
    "adapters/nemo-denoiser/model.nemo",
    "adapters/nemo-denoiser/weights",
    "cpp-library/.deps/nemo_denoiser.onnx",
    "cpp-library/.deps/se_den_sb_16k_small.onnx",
    "data/checkouts/NeMo",
    "data/checkouts/nemo",
    "data/checkouts/nemo-denoiser",
    "data/envs/nemo-denoiser",
    "data/envs/nemo-denoiser/requirements.lock",
    "data/models/nemo-denoiser",
    "data/models/nemo-denoiser/se_den_sb_16k_small.nemo",
    "data/models/se_den_sb_16k_small",
    "data/rights/nemo-denoiser-model-license.json",
    "data/rights/nemo-denoiser-rights.json",
    "data/runs/nemo-denoiser-cohort/manifest.json",
    "data/runs/nemo-denoiser-parity/manifest.json",
)
HOME_ASSET_PROBES: Tuple[str, ...] = (
    ".cache/huggingface/hub/models--nemo-denoiser",
    ".cache/huggingface/hub/models--nvidia--se_den_sb_16k_small",
    ".cache/torch/hub/checkpoints/se_den_sb_16k_small.nemo",
)

# The adapter README is present provenance only.  It is not source, weights,
# runtime or a result, and it is never admitted as a candidate artifact.
OBSERVED_ADAPTER: Dict[str, Any] = {
    "admitted": False,
    "exact_candidate": False,
    "note": (
        "No local nemo denoiser adapter README or artifact is present in this "
        "worktree. Candidate identity comes from pinned census and inventory "
        "records only; nothing is admitted as source, weight, runtime or result."
    ),
    "path": "adapters/nemo-denoiser/README.md",
    "present": False,
    "sha256": None,
    "weights_present": False,
}

SOURCE_PINS: Dict[str, str] = {
    'audio-benchmark-platform/plan/INVENTORY.json': '46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c',
    'audio-benchmark-platform/plan/audio-sdk/README.md': 'f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06',
    'audio-benchmark-platform/plan/swarm/VERIFICATION.md': '3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910',
    'audio-benchmark-platform/audio-pro/docs/rights-register.md': 'e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44',
    'audio-benchmark-platform/audio-pro/inventory/rights-register.json': '24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923',
    'research/noise_suppression_candidate_census.md': '525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a',
}

BOUNDARY_PINS: Dict[str, str] = {
    '.github/workflows/ci.yml': 'ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415',
    'CMakeLists.txt': 'af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04',
    'CONTRACTS.md': 'f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69',
    'LICENSE': 'e348a42d61105b8feddb5f6d25dbee55102601b7b211ddf04c879a8bb88a040e',
    'LICENSES/Apache-2.0.txt': 'cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30',
    'README.md': '4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35',
    'REUSE.toml': 'c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8',
    'api/include/audio_sdk/provider_v0.h': 'f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766',
    'api/include/audio_sdk/session_v0.h': 'a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1',
    'scripts/ci.py': '64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f',
}

SIBLING_PINS: Dict[str, str] = {
    'docs/task-evidence/nemo-schr-dinger-bridge-dereverberation/README.md': 'd2f85e19b2d4c467659560dbd0141e63939b3f7b2a1163b8e86332c63c4b4f91',
}

# SOURCES.sha256 is excluded because a manifest cannot pin its own bytes.
LOCAL_FILES: Tuple[str, ...] = (
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
TABLE_FILES: Tuple[str, ...] = (
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "test_reference.py",
    "verify.py",
)

STABLE_TASK_IDENTITY: Dict[str, Any] = {
    "id": TASK,
    "title": "NVIDIA NeMo Schrödinger-bridge denoiser (`se_den_sb_16k_small`)",
    "repository": "audio-sdk",
    "mode": MODE,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-EVIDENCE",
        "SDK-FND-PROVIDER",
    ],
    "write_scope": [
        "SDK provider, tool or evidence directory for nvidia-nemo-schr-dinger-bridge-denoiser-se-den-sb-16k-small and its own fixtures"
    ],
    "deliverable": (
        "Verify runnable source, exact assets, permitted scope, task geometry "
        "and matched evidence. Then reproduce the exact model/runtime as a "
        "caller-supplied-asset reference and add an opt-in SDK adapter once "
        "its prerequisites pass. Record a concrete blocker if feasibility fails."
    ),
    "acceptance": (
        "Apply the enhancement acceptance profile; record exact scope, evidence, "
        "failure/control results, and remaining release gates. A readiness "
        "conclusion with an exact external blocker is an accepted investigation "
        "handoff; it does not close the conditional implementation."
    ),
    "evidence": ["research/noise_suppression_candidate_census.md"],
    "component": COMPONENT,
    "dispatch_priority": 3,
}
PROJECTED_BOARD_FIELDS: Tuple[str, ...] = tuple(sorted(STABLE_TASK_IDENTITY))
MUTABLE_BOARD_FIELDS: Tuple[str, ...] = (
    "status",
    "owner",
    "claim",
    "review",
    "handoff",
    "blocked_reason",
    "initialized_on",
    "history",
)

BOUNDARY: Dict[str, bool] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "installed_v0_geometry_preserved": True,
    "model_runtime_invoked": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "readiness_json_added": False,
    "registered": False,
    "sdk_data_dir_added": False,
    "shared_build_or_ci_change": False,
    "task_board_or_handoff_write": False,
    "weights_vendored": False,
}

CLAIMS: Dict[str, bool] = {
    "asset_bytes_read": False,
    "asset_downloaded": False,
    "benchmark_result": False,
    "checkpoint_loaded": False,
    "cohort_scored": False,
    "device_timing_measured": False,
    "exact_parity_claim": False,
    "listening_result_produced": False,
    "model_bytes_read": False,
    "model_runtime_invoked": False,
    "quality_claim": False,
    "real_audio_read": False,
    "real_corpus_read": False,
    "real_nemo_runtime": False,
    "release_claim": False,
    "sampler_invoked": False,
    "source_read": False,
    "weights_accessed": False,
}

FORMAT: Dict[str, Any] = {
    "candidate_algorithmic_latency_samples": None,
    "candidate_channels": CHANNELS,
    "candidate_frame_geometry_known": False,
    "candidate_hop_samples": None,
    "candidate_sample_format": "float32",
    "candidate_sample_rate_hz": SAMPLE_RATE_HZ,
    "candidate_streaming_api": False,
    "fixture_block_samples": FIXTURE_BLOCK_SAMPLES,
    "fixture_geometry_scope": "probe_only",
    "fixture_sampler_steps": SURROGATE_SAMPLER_STEPS,
    "fixture_samples": FIXTURE_SAMPLES,
    "sdk_v0_channels": V0_CHANNELS,
    "sdk_v0_frame_samples": V0_FRAME_SAMPLES,
    "sdk_v0_geometry_preserved": True,
    "sdk_v0_sample_format": SAMPLE_FORMAT,
    "sdk_v0_sample_rate_hz": V0_SAMPLE_RATE_HZ,
    "upstream_geometry_verified": False,
    "upstream_utterance_level": True,
}

REQUIRED_ASSET_FIELDS = {
    "asset_id",
    "candidate_asset",
    "checkpoint_bytes",
    "checkpoint_path",
    "checkpoint_sha256",
    "channels",
    "config_path",
    "config_sha256",
    "license_id",
    "nemo_version",
    "rights_entry_present",
    "runtime_lock_sha256",
    "runtime_path",
    "runtime_sha256",
    "sample_format",
    "sample_rate_hz",
    "sampler",
    "sampler_steps",
    "source_commit",
    "source_path",
    "storage",
    "torch_version",
}

CANDIDATE_REJECTION_REASONS: Tuple[str, ...] = (
    "checkpoint_identity_not_verified",
    "license_scope_unresolved",
    "rights_register_entry_absent",
    "runtime_not_pinned",
    "upstream_revision_not_verified",
)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "present_behavior": (
        "validate_hash_geometry_and_identity_only; do not load, import or "
        "execute anything in this package"
    ),
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "runtime_and_asset_approved_separately": True,
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "source, checkpoint, config and runtime paths are caller-owned "
        "absolute existing regular files",
        "checkpoint byte count and every SHA-256 match the supplied bytes",
        "source_commit is a 40-hex revision but is never admitted as verified "
        "upstream because no upstream revision is recorded in this package",
        "sample rate is 16000, channels is one and sample_format is f32",
        "sampler is sde or ode and sampler_steps is one of 1, 2, 4, 8",
        "runtime_lock_sha256 and versions are present but cannot be admitted "
        "as a pinned NeMo/PyTorch runtime",
        "a hash-matched caller placeholder is structurally accepted only as a "
        "synthetic control and is never admitted as the candidate",
        "the candidate path always fails closed with the recorded reason codes",
        "no download, copy, import, load, sampler invocation or execution "
        "occurs in this package",
    ],
    "weights_embedded_in_wheel": False,
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "upstream_source_absent_unpinned",
        "requirement": (
            "Supply the exact NeMo source tree at an immutable 40-hex commit as "
            "a caller-owned checkout, with a per-file SHA-256 manifest, the "
            "reviewed upstream LICENSE and the complete notice bundle, verified "
            "locally without a network download."
        ),
        "state": (
            "No checkout exists at data/checkouts/NeMo, data/checkouts/nemo or "
            "data/checkouts/nemo-denoiser. The pinned record names the model "
            "card and NeMo 2.0 but records no repository revision, tree digest, "
            "release tag or source licence bundle. None is fabricated or "
            "downloaded here."
        ),
    },
    {
        "id": "checkpoint_config_and_identity_absent",
        "requirement": (
            "Supply the exact se_den_sb_16k_small checkpoint and the exact "
            "hydra/model config as caller-owned external assets with filename, "
            "byte count, SHA-256, acquisition record and artifact-specific "
            "terms."
        ),
        "state": (
            "No file exists at data/models/nemo-denoiser or "
            "data/models/se_den_sb_16k_small, and no filename, byte count or "
            "SHA-256 is recorded. The adapter README names the model card only. "
            "Nothing was downloaded, reconstructed or substituted."
        ),
    },
    {
        "id": "runtime_absent",
        "requirement": (
            "Admit a locked, hash-pinned offline NeMo 2.0 and PyTorch runtime "
            "with exact versions, wheel digests, target platform, native "
            "libraries and an offline load/import digest."
        ),
        "state": (
            "No environment exists at data/envs/nemo-denoiser and no lock file, "
            "wheel digest, interpreter version, torch version or NeMo install "
            "digest is recorded. No import, load or inference was attempted."
        ),
    },
    {
        "id": "rights_unresolved",
        "requirement": (
            "Supply written source, checkpoint, model-card, training-data, "
            "corpus, redistribution, product-use and derivative-output terms. "
            "The noncommercial share-alike terms must be reviewed and, for any "
            "product use, separately cleared."
        ),
        "state": (
            "The fixed rights register has no nemo, se_der or schrödinger "
            "entry. The model card is reported as CC BY-NC-SA 4.0 in local "
            "prose, but no licence text, notice bundle, review date or "
            "artifact-specific decision exists. Evaluation, redistribution, "
            "customer deployment and public playback are all unresolved."
        ),
    },
    {
        "id": "geometry_and_sampler_unverified",
        "requirement": (
            "Pin the exact accepted audio length, channel layout, sample rate, "
            "config, sampler (SDE or ODE), step count, solver, seed behaviour, "
            "post-processing and any algorithmic latency, then reproduce them "
            "on one declared whole-utterance path."
        ),
        "state": (
            "The pinned records establish only 16 kHz mono, whole-clip SDE/ODE "
            "sampling and no streaming API. They record no exact config, "
            "sampler defaults, step count, solver tolerances, seed handling, "
            "frame/hop geometry or algorithmic latency. This package's 16,000 "
            "sample fixture and four-step integer surrogate are probe-only and "
            "are not candidate geometry."
        ),
    },
    {
        "id": "corpus_and_selection_absent",
        "requirement": (
            "Freeze a rights-cleared reverberant evaluation cohort with clean or "
            "early-reference targets, measured or frozen RIRs, the exact "
            "early-response definition, strata and identity controls."
        ),
        "state": (
            "WSJ0-Reverb requires external access and is not staged locally. No "
            "rights-cleared cohort, RIR set, early-target definition, split, "
            "stratum or identity control exists in this package."
        ),
    },
    {
        "id": "exact_reference_and_quality_absent",
        "requirement": (
            "Reproduce approved exact-runtime outputs for frozen inputs and score "
            "a matched cohort with independent SI-SDR, STOI/ESTOI, PESQ or SRMR "
            "where permitted plus permitted listening, including adverse, "
            "missing and nonfinite controls."
        ),
        "state": (
            "No exact output vector, parity trace, paired score, listening "
            "result or failure-control result exists for the candidate. The "
            "upstream-reported WSJ0-Reverb values are quoted context only and "
            "are not reproduced here."
        ),
    },
    {
        "id": "target_timing_and_provider_absent",
        "requirement": (
            "Measure target-device whole-utterance and any chunked-path compute, "
            "RTF, memory, first-output/tail and deadline behaviour, then complete "
            "OFF-by-default opt-in provider intake with descriptor review."
        ),
        "state": (
            "No runtime exists to measure. The model card's V100 note is "
            "upstream context, not a local timing result. No provider, "
            "descriptor, registry entry, adapter JSON or readiness JSON exists."
        ),
    },
)

GATES: Tuple[Dict[str, str], ...] = (
    {
        "evidence": (
            "No source revision, checkpoint byte count, SHA-256, config digest, "
            "release tag or rights ledger row exists; every fixed asset probe is "
            "absent and no candidate bytes were supplied."
        ),
        "name": "exact_source_checkpoint_and_config_identity",
        "reopen": (
            "Reopen only when the exact NeMo source revision is present and "
            "pinned by 40-hex commit, per-file digest manifest and reviewed "
            "LICENSE/notice bundle, and the exact checkpoint and config are "
            "caller-supplied with immutable identity, byte counts, SHA-256 and "
            "artifact-specific terms."
        ),
        "status": "blocked",
    },
    {
        "evidence": (
            "No NeMo 2.0 or PyTorch runtime, interpreter version, wheel digest, "
            "lock file, target platform or offline import/load record exists."
        ),
        "name": "pinned_runtime_and_offline_load",
        "reopen": (
            "Reopen only when the exact pinned NeMo and PyTorch runtime install "
            "in the intended offline environment with recorded artifact digests "
            "and a deterministic load of the exact checkpoint and config."
        ),
        "status": "blocked",
    },
    {
        "evidence": (
            "The rights register has no nemo, se_der or schrödinger entry; "
            "CC BY-NC-SA 4.0 is upstream-reported prose only and no artifact or "
            "output-use decision exists."
        ),
        "name": "artifact_and_output_rights",
        "reopen": (
            "Reopen only after artifact-specific written terms settle "
            "evaluation, redistribution, customer deployment, public playback "
            "and derivative-output use for the reviewed source, checkpoint and "
            "runtime, with a recorded review date and complete notice bundle."
        ),
        "status": "blocked",
    },
    {
        "evidence": (
            "No exact config, accepted audio length, sampler, solver, step "
            "count, seed handling, post-processing or algorithmic latency is "
            "pinned; the model card reports no streaming API."
        ),
        "name": "whole_utterance_geometry_and_sampler",
        "reopen": (
            "Reopen only with an authoritative config and a declared "
            "whole-utterance geometry that pins sample rate, channels, accepted "
            "length, sampler, solver, step count, seed behaviour, "
            "post-processing and latency, reproduced on one declared path."
        ),
        "status": "blocked",
    },
    {
        "evidence": (
            "No candidate output, frozen input, exact-runtime reference or "
            "parity trace exists."
        ),
        "name": "exact_reference_parity",
        "reopen": (
            "Reopen only with approved outputs for frozen inputs from the exact "
            "caller-supplied source, checkpoint, config and runtime, "
            "reproducible across three cold starts."
        ),
        "status": "blocked",
    },
    {
        "evidence": (
            "No rights-cleared reverberant corpus, measured or frozen RIRs, "
            "early-target definition, strata or identity control exists."
        ),
        "name": "rights_cleared_paired_cohort",
        "reopen": (
            "Reopen only with a frozen rights-cleared paired reverberant cohort "
            "that fixes clean or early targets, RIRs, early-response window, "
            "strata, held-out splits and identity controls."
        ),
        "status": "blocked",
    },
    {
        "evidence": (
            "No independent intrusive or non-intrusive score and no permitted "
            "listening result exists; upstream-reported numbers are not "
            "reproduced."
        ),
        "name": "independent_scoring_and_listening",
        "reopen": (
            "Reopen only with independent SI-SDR, STOI/ESTOI, PESQ or SRMR "
            "where permitted, identity and task-matched baselines, adverse and "
            "nonfinite controls, and permitted listening under a recorded "
            "protocol."
        ),
        "status": "blocked",
    },
    {
        "evidence": (
            "No target-device timing, RTF, memory or deadline measurement and no "
            "OFF-by-default opt-in provider, descriptor or catalog entry exists."
        ),
        "name": "target_timing_and_opt_in_provider",
        "reopen": (
            "Reopen only with target-device whole-utterance and any chunked-path "
            "compute, RTF, memory, first-output/tail and deadline measurements, "
            "then an OFF-by-default opt-in provider intake and descriptor "
            "review."
        ),
        "status": "blocked",
    },
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "exact NeMo source revision, per-file digest manifest and LICENSE/notice bundle",
    "exact se_den_sb_16k_small checkpoint with filename, byte count, SHA-256 and acquisition record",
    "exact model/config with digest, sampler, solver, step count and seed behaviour",
    "pinned offline NeMo 2.0 and PyTorch runtime with wheel digests and load record",
    "written artifact and output-use rights decisions, including noncommercial scope",
    "rights-cleared paired reverberant cohort with RIRs and early-target definition",
    "approved exact-runtime reference outputs and parity trace",
    "independent quality scores, permitted listening and target-device timing",
)

REOPEN_CONDITIONS: Tuple[str, ...] = tuple(gate["reopen"] for gate in GATES)

NON_CLAIMS: Tuple[str, ...] = (
    "No NeMo source, checkpoint, config, weight, derived weight, runtime, corpus or media was downloaded, loaded, compiled, executed or bundled; the local adapter README is hashed read-only for provenance only.",
    "No public API/ABI, CONTRACTS.md, descriptor, registry, installed default, shared build, dependency lock, CI, board or handoff file was changed.",
    "No listening, MOS, SI-SDR, STOI, ESTOI, PESQ, SRMR, WER, quality, parity, benchmark, device-timing, latency or release result is claimed for the candidate.",
    "The upstream-reported WSJ0-Reverb scores and V100 note are quoted provenance, not local measurements.",
    "The synthetic whole-clip boundary surrogate is not NeMo, contains no neural network or sampler, and no missing or surrogate result ever qualifies the candidate.",
)

# ---------------------------------------------------------------------------
# Canonical JSON and digests
# ---------------------------------------------------------------------------


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        return 0.0 if value == 0.0 else value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(
        _normalize_negzero(value),
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    )
    return (text + "\n").encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    return canonical_bytes(report if report is not None else build_report())


def stable_identity_digest(identity: Dict[str, Any] | None = None) -> str:
    source = STABLE_TASK_IDENTITY if identity is None else identity
    projected = {field: source[field] for field in PROJECTED_BOARD_FIELDS}
    return sha256(
        json.dumps(
            projected, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
    )


def stable_row_digest(fields: Dict[str, Any]) -> str:
    projected = {field: fields[field] for field in PROJECTED_BOARD_FIELDS}
    return sha256(
        json.dumps(
            projected, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
    )


def project_board_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {field: row[field] for field in PROJECTED_BOARD_FIELDS}


def task_identity() -> Dict[str, Any]:
    identity = dict(STABLE_TASK_IDENTITY)
    identity["board_full_file_hashed"] = False
    identity["mutable_fields_excluded"] = list(MUTABLE_BOARD_FIELDS)
    identity["profile_source"] = (
        f"plan/INVENTORY.json#components[id={INVENTORY_RECORD_ID}]"
    )
    identity["stable_sha256"] = stable_identity_digest()
    identity["verification_profile"] = PROFILE
    return identity


# ---------------------------------------------------------------------------
# Deterministic synthetic whole-clip denoising fixture
# ---------------------------------------------------------------------------

SINE64: Tuple[int, ...] = (
    0, 3212, 6393, 9512, 12539, 15446, 18204, 20787,
    23170, 25329, 27245, 28898, 30273, 31356, 32137, 32609,
    32767, 32609, 32137, 31356, 30273, 28898, 27245, 25329,
    23170, 20787, 18204, 15446, 12539, 9512, 6393, 3212,
    0, -3212, -6393, -9512, -12539, -15446, -18204, -20787,
    -23170, -25329, -27245, -28898, -30273, -31356, -32137, -32609,
    -32767, -32609, -32137, -31356, -30273, -28898, -27245, -25329,
    -23170, -20787, -18204, -15446, -12539, -9512, -6393, -3212,
)

SEGMENT_FRAMES = 20
SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "silence-a", "start_frame": 0, "end_frame": 20, "kind": "silence"},
    {"id": "speech-a", "start_frame": 20, "end_frame": 50, "kind": "speech",
     "steps": (1, 2, 3), "amplitudes": (520, 300, 170)},
    {"id": "speech-b", "start_frame": 50, "end_frame": 70, "kind": "speech",
     "steps": (2, 3, 5), "amplitudes": (470, 320, 190),
     "click_period": 1024, "click_amplitude": 8000},
    {"id": "noisy-speech", "start_frame": 70, "end_frame": 90,
     "kind": "speech", "steps": (3, 4, 6), "amplitudes": (450, 270, 160),
     "noise_gain": 2},
    {"id": "tail-after-speech", "start_frame": 90, "end_frame": 100,
     "kind": "silence"},
)

# Probe-only early response: (delay, gain/1024).
EARLY_TAPS: Tuple[Tuple[int, int], ...] = (
    (8, 880), (48, 320), (144, 190), (352, 110), (624, 64),
)
# Probe-only late response after the fixture early window: (delay, gain/1024).
LATE_TAPS: Tuple[Tuple[int, int], ...] = (
    (1024, 240), (1184, 192), (1344, 154), (1504, 123),
    (1664, 98), (1824, 78), (1984, 62), (2144, 50),
)
# Fixed probe-only late estimator: 60% of the first four late taps.
PREDICTOR_TAPS: Tuple[Tuple[int, int], ...] = tuple(
    (delay, max(1, (gain * 60) // 100)) for delay, gain in LATE_TAPS[:4]
)

CONFIG: Dict[str, Any] = {
    "channels": CHANNELS,
    "model_id": "nemo_se_den_sb_16k_small_surrogate",
    "model_used": False,
    "opt_in": True,
    "real_runtime": False,
    "sample_format": SAMPLE_FORMAT,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "sampler": "sde",
    "sampler_steps": SURROGATE_SAMPLER_STEPS,
    "seed": SURROGATE_SEED,
    "surrogate": True,
    "utterance_samples": FIXTURE_SAMPLES,
}
CONFIG_FIELDS = tuple(sorted(CONFIG))


# ---------------------------------------------------------------------------
# Small deterministic helpers
# ---------------------------------------------------------------------------


def _clip16(value: int) -> int:
    if value > 32767:
        return 32767
    if value < -32768:
        return -32768
    return value


def _envelope(index: int, length: int) -> int:
    fade = 512
    if index < fade:
        return (index * 1024) // fade
    if index >= length - fade:
        return ((length - 1 - index) * 1024) // fade
    return 1024


def _clean_track() -> List[int]:
    track = [0] * FIXTURE_SAMPLES
    for segment in SEGMENTS:
        start = segment["start_frame"] * FIXTURE_BLOCK_SAMPLES
        end = segment["end_frame"] * FIXTURE_BLOCK_SAMPLES
        if segment["kind"] == "silence":
            continue
        phases = [0, 0, 0]
        for offset in range(end - start):
            sample = 0
            for index in range(3):
                phases[index] = (phases[index] + segment["steps"][index]) & 63
                sample += segment["amplitudes"][index] * SINE64[phases[index]]
            sample >>= 10
            if "click_period" in segment and offset % segment["click_period"] < 4:
                sign = 1 if (offset // segment["click_period"]) % 2 == 0 else -1
                sample += sign * segment["click_amplitude"]
            sample = (sample * _envelope(offset, end - start)) >> 10
            track[start + offset] = _clip16(sample)
    return track


def _noise_track() -> List[int]:
    noise = [0] * FIXTURE_SAMPLES
    seed = 123456789
    for segment in SEGMENTS:
        gain = segment.get("noise_gain")
        if not gain:
            continue
        start = segment["start_frame"] * FIXTURE_BLOCK_SAMPLES
        end = segment["end_frame"] * FIXTURE_BLOCK_SAMPLES
        for index in range(start, end):
            seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
            value = ((seed >> 16) % 2001) - 1000
            noise[index] = _clip16(value * gain)
    return noise


def _convolve(clean: Sequence[int], taps: Sequence[Tuple[int, int]]
              ) -> List[int]:
    output = [0] * len(clean)
    for delay, gain in taps:
        for index in range(delay, len(clean)):
            output[index] += (clean[index - delay] * gain) >> 10
    return output


def build_fixture() -> Dict[str, Any]:
    clean = _clean_track()
    early = _convolve(clean, EARLY_TAPS)
    late = _convolve(clean, LATE_TAPS)
    noise = _noise_track()
    reverb = [
        _clip16(early[index] + late[index] + noise[index])
        for index in range(FIXTURE_SAMPLES)
    ]
    return {
        "channels": CHANNELS,
        "clean": [value / 32768.0 for value in clean],
        "early": [value / 32768.0 for value in early],
        "late": [value / 32768.0 for value in late],
        "noise": [value / 32768.0 for value in noise],
        "reverb": reverb,
        "reverb_float": [value / 32768.0 for value in reverb],
        "sample_format": "float32",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "samples": FIXTURE_SAMPLES,
        "segments": [dict(segment) for segment in SEGMENTS],
    }


# ---------------------------------------------------------------------------
# Validation and rejection
# ---------------------------------------------------------------------------


def _is_int(value: Any) -> bool:
    return type(value) is int


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def validate_config(config: Any) -> None:
    _require(isinstance(config, dict), "config_type_invalid")
    if set(config) != set(CONFIG):
        raise ValueError("config_keys_mismatch")
    _require(config["model_id"] == CONFIG["model_id"], "model_id_mismatch")
    _require(
        _is_int(config["sample_rate_hz"])
        and config["sample_rate_hz"] == SAMPLE_RATE_HZ,
        "sample_rate_mismatch",
    )
    _require(
        _is_int(config["channels"]) and config["channels"] == CHANNELS,
        "channels_mismatch",
    )
    _require(config["sample_format"] == SAMPLE_FORMAT, "sample_format_mismatch")
    _require(
        _is_int(config["utterance_samples"])
        and config["utterance_samples"] == FIXTURE_SAMPLES,
        "utterance_samples_mismatch",
    )
    _require(config["sampler"] in ("sde", "ode"), "sampler_unsupported")
    _require(
        _is_int(config["sampler_steps"])
        and config["sampler_steps"] in (1, 2, 4, 8),
        "sampler_steps_invalid",
    )
    _require(
        _is_int(config["seed"]) and 0 <= config["seed"] <= 0x7FFFFFFF,
        "seed_invalid",
    )
    _require(config["real_runtime"] is False, "real_runtime_forbidden")
    _require(config["model_used"] is False, "model_used_forbidden")
    _require(config["surrogate"] is True, "surrogate_required")
    _require(config["opt_in"] is True, "surrogate_opt_in_required")


def validate_utterance(samples: Any) -> None:
    _require(isinstance(samples, list), "utterance_type_invalid")
    _require(len(samples) == FIXTURE_SAMPLES, "utterance_length_mismatch")
    for value in samples:
        _require(
            isinstance(value, (int, float)) and not isinstance(value, bool),
            "sample_type_invalid",
        )
        _require(math.isfinite(float(value)), "sample_nonfinite")
        _require(abs(float(value)) <= MAX_ABS_AUDIO, "sample_out_of_range")


def _to_i16(value: float) -> int:
    return _clip16(int(round(value * 32768.0)))


# ---------------------------------------------------------------------------
# Synthetic whole-clip boundary surrogate
# ---------------------------------------------------------------------------


def _late_estimate(samples: Sequence[int]) -> List[int]:
    estimate = [0] * len(samples)
    for delay, gain in PREDICTOR_TAPS:
        for index in range(delay, len(samples)):
            estimate[index] += (samples[index - delay] * gain) >> 10
    return estimate


def _soft_limit(value: int) -> int:
    magnitude = abs(value)
    if magnitude > 20000:
        value = 20000 + (magnitude - 20000) // 2
        return value if value >= 0 else -value
    return value


def _surrogate_core(
    reverb: Sequence[int], sampler: str, steps: int
) -> List[int]:
    late = _late_estimate(reverb)
    # Probe-only fixed gain difference proves both sampler strings are
    # exercised; it is not candidate sampler semantics.
    gain = 60 if sampler == "sde" else 70
    residual = [(value * gain) // 100 for value in late]
    output = list(reverb)
    for _step in range(steps):
        for index in range(len(output)):
            output[index] = _clip16(output[index] - residual[index] // steps)
    return [_soft_limit(value) for value in output]


def process_utterance(samples: Any, config: Any) -> Dict[str, Any]:
    validate_config(config)
    validate_utterance(samples)
    reverb = [_to_i16(value) for value in samples]
    output = _surrogate_core(reverb, config["sampler"], config["sampler_steps"])
    floats = [value / 32768.0 for value in output]
    return {
        "chunk_count": 1,
        "input_samples": len(samples),
        "output": floats,
        "output_samples": len(floats),
        "sampler": config["sampler"],
        "sampler_steps": config["sampler_steps"],
        "status": "ok",
        "streaming": False,
    }


def process_chunks(chunks: Any, config: Any) -> Dict[str, Any]:
    _require(isinstance(chunks, list), "chunks_type_invalid")
    if len(chunks) != 1:
        raise ValueError("utterance_level_offline_only")
    result = process_utterance(chunks[0], config)
    return {
        "one_shot": True,
        "output": result["output"],
        "output_samples": result["output_samples"],
        "status": "ok",
        "streaming": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied asset validation (never loads or executes)
# ---------------------------------------------------------------------------

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _require_abs_regular(path_value: Any, reason: str) -> Path:
    _require(isinstance(path_value, str) and path_value, reason)
    path = Path(path_value)
    _require(path.is_absolute(), reason)
    _require(path.is_file() and not path.is_symlink(), reason)
    return path


def _hash_matches(path: Path, expected: str, reason: str) -> None:
    _require(_HEX64.match(expected) is not None, reason)
    _require(sha256_file(path) == expected, reason)


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    _require(isinstance(manifest, dict), "manifest_type_invalid")
    if set(manifest) != REQUIRED_ASSET_FIELDS:
        raise ValueError("manifest_fields_mismatch")
    for field in (
        "asset_id",
        "license_id",
        "nemo_version",
        "runtime_lock_sha256",
        "runtime_sha256",
        "sample_format",
        "sampler",
        "source_commit",
        "storage",
        "torch_version",
    ):
        _require(
            isinstance(manifest[field], str) and manifest[field],
            "manifest_field_invalid:" + field,
        )
    _require(
        manifest["storage"] == "external", "manifest_storage_not_external"
    )
    _require(
        type(manifest["rights_entry_present"]) is bool,
        "manifest_rights_flag_invalid",
    )
    _require(
        type(manifest["candidate_asset"]) is bool,
        "manifest_candidate_flag_invalid",
    )
    _require(
        _HEX40.match(manifest["source_commit"]) is not None,
        "manifest_source_commit_invalid",
    )
    _require(
        _is_int(manifest["sample_rate_hz"])
        and manifest["sample_rate_hz"] == SAMPLE_RATE_HZ,
        "manifest_sample_rate_invalid",
    )
    _require(
        _is_int(manifest["channels"]) and manifest["channels"] == CHANNELS,
        "manifest_channels_invalid",
    )
    _require(
        manifest["sample_format"] == "f32", "manifest_sample_format_invalid"
    )
    _require(manifest["sampler"] in ("sde", "ode"), "manifest_sampler_invalid")
    _require(
        _is_int(manifest["sampler_steps"])
        and manifest["sampler_steps"] in (1, 2, 4, 8),
        "manifest_sampler_steps_invalid",
    )
    _require(
        _is_int(manifest["checkpoint_bytes"])
        and manifest["checkpoint_bytes"] > 0,
        "manifest_checkpoint_bytes_invalid",
    )
    source = _require_abs_regular(
        manifest["source_path"], "manifest_source_path_invalid"
    )
    checkpoint = _require_abs_regular(
        manifest["checkpoint_path"], "manifest_checkpoint_path_invalid"
    )
    config = _require_abs_regular(
        manifest["config_path"], "manifest_config_path_invalid"
    )
    runtime = _require_abs_regular(
        manifest["runtime_path"], "manifest_runtime_path_invalid"
    )
    _require(source.stat().st_size >= 0, "manifest_source_path_invalid")
    _require(
        checkpoint.stat().st_size == manifest["checkpoint_bytes"],
        "manifest_checkpoint_bytes_mismatch",
    )
    _hash_matches(
        checkpoint,
        manifest["checkpoint_sha256"],
        "manifest_checkpoint_hash_mismatch",
    )
    _hash_matches(
        config, manifest["config_sha256"], "manifest_config_hash_mismatch"
    )
    _hash_matches(
        runtime, manifest["runtime_sha256"], "manifest_runtime_hash_mismatch"
    )
    _require(
        _HEX64.match(manifest["runtime_lock_sha256"]) is not None,
        "manifest_runtime_lock_invalid",
    )
    return {
        "asset_id": manifest["asset_id"],
        "asset_bytes_hashed": True,
        "asset_bytes_read": False,
        "candidate_asset": manifest["candidate_asset"],
        "checkpoint_bytes": manifest["checkpoint_bytes"],
        "checkpoint_sha256": manifest["checkpoint_sha256"],
        "download_attempted": False,
        "executed": False,
        "imported": False,
        "loaded": False,
        "runtime_lock_sha256": manifest["runtime_lock_sha256"],
        "status": "accepted_structure",
    }


def admit_candidate_asset(manifest: Any) -> Dict[str, Any]:
    try:
        structural = validate_caller_asset(manifest)
    except ValueError as exc:
        return {
            "admitted": False,
            "candidate_asset": None,
            "download_attempted": False,
            "executed": False,
            "imported": False,
            "loaded": False,
            "reason_codes": [str(exc)],
            "status": "rejected",
        }
    if structural["candidate_asset"] is not True:
        return {
            "admitted": False,
            "candidate_asset": False,
            "download_attempted": False,
            "executed": False,
            "imported": False,
            "loaded": False,
            "reason_codes": ["synthetic_control_not_candidate"],
            "status": "rejected",
        }
    return {
        "admitted": False,
        "candidate_asset": True,
        "download_attempted": False,
        "executed": False,
        "imported": False,
        "loaded": False,
        "reason_codes": list(CANDIDATE_REJECTION_REASONS),
        "status": "blocked",
    }


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------


def config_adverse_control() -> Dict[str, Any]:
    variants: Dict[str, Any] = {
        "wrong_model_id": ("model_id", "other/model", "model_id_mismatch"),
        "wrong_sample_rate": ("sample_rate_hz", 48000, "sample_rate_mismatch"),
        "wrong_channels": ("channels", 2, "channels_mismatch"),
        "wrong_sample_format": ("sample_format", "int16", "sample_format_mismatch"),
        "wrong_utterance_length": (
            "utterance_samples", 8000, "utterance_samples_mismatch"
        ),
        "unsupported_sampler": ("sampler", "ddim", "sampler_unsupported"),
        "zero_steps": ("sampler_steps", 0, "sampler_steps_invalid"),
        "three_steps": ("sampler_steps", 3, "sampler_steps_invalid"),
        "negative_seed": ("seed", -1, "seed_invalid"),
        "boolean_seed": ("seed", True, "seed_invalid"),
        "real_runtime": ("real_runtime", True, "real_runtime_forbidden"),
        "model_used": ("model_used", True, "model_used_forbidden"),
        "surrogate_disabled": ("surrogate", False, "surrogate_required"),
        "opt_out": ("opt_in", False, "surrogate_opt_in_required"),
    }
    results: Dict[str, str] = {}
    for name, (field, value, expected) in variants.items():
        config = dict(CONFIG)
        config[field] = value
        try:
            validate_config(config)
            results[name] = "accepted"
        except ValueError as exc:
            results[name] = str(exc)
        results[name + ":expected"] = expected
    missing = dict(CONFIG)
    del missing["seed"]
    try:
        validate_config(missing)
        results["missing_seed"] = "accepted"
    except ValueError as exc:
        results["missing_seed"] = str(exc)
    extra = dict(CONFIG)
    extra["unknown"] = 1
    try:
        validate_config(extra)
        results["extra_key"] = "accepted"
    except ValueError as exc:
        results["extra_key"] = str(exc)
    results["missing_seed:expected"] = "config_keys_mismatch"
    results["extra_key:expected"] = "config_keys_mismatch"
    return results


def input_adverse_control(fixture: Dict[str, Any]) -> Dict[str, Any]:
    good = list(fixture["reverb_float"])
    variants: Dict[str, Any] = {
        "empty": [],
        "short": good[:-1],
        "long": good + [0.0],
        "string": "not-a-list",
        "bytes": b"\x00" * FIXTURE_SAMPLES,
        "nested": [good[0], [good[1]]] + good[2:],
        "boolean": [True] + good[1:],
        "nan": [float("nan")] + good[1:],
        "positive_infinity": [float("inf")] + good[1:],
        "negative_infinity": [float("-inf")] + good[1:],
        "out_of_range": [1.5] + good[1:],
    }
    results: Dict[str, str] = {}
    for name, value in variants.items():
        try:
            validate_utterance(value)
            results[name] = "accepted"
        except ValueError as exc:
            results[name] = str(exc)
    keys = {
        "empty": "utterance_length_mismatch",
        "short": "utterance_length_mismatch",
        "long": "utterance_length_mismatch",
        "string": "utterance_type_invalid",
        "bytes": "utterance_type_invalid",
        "nested": "sample_type_invalid",
        "boolean": "sample_type_invalid",
        "nan": "sample_nonfinite",
        "positive_infinity": "sample_nonfinite",
        "negative_infinity": "sample_nonfinite",
        "out_of_range": "sample_out_of_range",
    }
    for name, expected in keys.items():
        results[name + ":expected"] = expected
    return results


def _write_synthetic_assets(root: Path) -> Dict[str, str]:
    unit = b"audio-sdk/nvidia-nemo-schr-dinger-bridge-denoiser-se-den-sb-16k-small/synthetic-control/v1\n"
    source = unit * 8
    checkpoint = unit * 32
    config = unit * 4
    runtime = unit * 16
    (root / "source.bin").write_bytes(source)
    (root / "checkpoint.bin").write_bytes(checkpoint)
    (root / "config.bin").write_bytes(config)
    (root / "runtime.bin").write_bytes(runtime)
    return {
        "checkpoint_bytes": str(len(checkpoint)),
        "checkpoint_sha256": sha256(checkpoint),
        "config_sha256": sha256(config),
        "runtime_sha256": sha256(runtime),
    }


def asset_admission_control() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="nemo-sb-asset-") as tmp:
        root = Path(tmp).resolve()
        digests = _write_synthetic_assets(root)
        base: Dict[str, Any] = {
            "asset_id": "synthetic-nemo-boundary-control-not-nemo",
            "candidate_asset": False,
            "checkpoint_bytes": int(digests["checkpoint_bytes"]),
            "checkpoint_path": str(root / "checkpoint.bin"),
            "checkpoint_sha256": digests["checkpoint_sha256"],
            "channels": 1,
            "config_path": str(root / "config.bin"),
            "config_sha256": digests["config_sha256"],
            "license_id": "synthetic-control",
            "nemo_version": "not-a-runtime",
            "rights_entry_present": False,
            "runtime_lock_sha256": "0" * 64,
            "runtime_path": str(root / "runtime.bin"),
            "runtime_sha256": digests["runtime_sha256"],
            "sample_format": "f32",
            "sample_rate_hz": 16000,
            "sampler": "sde",
            "sampler_steps": 4,
            "source_commit": "0" * 40,
            "source_path": str(root / "source.bin"),
            "storage": "external",
            "torch_version": "not-a-runtime",
        }
        synthetic = validate_caller_asset(base)
        candidate = dict(base)
        candidate["asset_id"] = "nemo-se-der-sb-16k-small-unpinned"
        candidate["candidate_asset"] = True
        candidate_result = admit_candidate_asset(candidate)
        synthetic_admission = admit_candidate_asset(base)

        variants: Dict[str, Tuple[Dict[str, Any], str]] = {}
        missing = dict(base)
        del missing["checkpoint_sha256"]
        variants["missing_checkpoint_sha256"] = (
            missing, "manifest_fields_mismatch"
        )
        extra = dict(base)
        extra["extra"] = 1
        variants["extra_field"] = (extra, "manifest_fields_mismatch")
        relative = dict(base)
        relative["checkpoint_path"] = "checkpoint.bin"
        variants["relative_path"] = (relative, "manifest_checkpoint_path_invalid")
        absent = dict(base)
        absent["checkpoint_path"] = str(root / "absent.bin")
        variants["absent_path"] = (absent, "manifest_checkpoint_path_invalid")
        bad_bytes = dict(base)
        bad_bytes["checkpoint_bytes"] = 1
        variants["wrong_byte_count"] = (
            bad_bytes, "manifest_checkpoint_bytes_mismatch"
        )
        bad_hash = dict(base)
        bad_hash["checkpoint_sha256"] = "1" * 64
        variants["wrong_checkpoint_hash"] = (
            bad_hash, "manifest_checkpoint_hash_mismatch"
        )
        bad_config_hash = dict(base)
        bad_config_hash["config_sha256"] = "2" * 64
        variants["wrong_config_hash"] = (
            bad_config_hash, "manifest_config_hash_mismatch"
        )
        bad_runtime_hash = dict(base)
        bad_runtime_hash["runtime_sha256"] = "3" * 64
        variants["wrong_runtime_hash"] = (
            bad_runtime_hash, "manifest_runtime_hash_mismatch"
        )
        short_commit = dict(base)
        short_commit["source_commit"] = "a" * 8
        variants["short_commit"] = (
            short_commit, "manifest_source_commit_invalid"
        )
        nonhex_commit = dict(base)
        nonhex_commit["source_commit"] = "z" * 40
        variants["nonhex_commit"] = (
            nonhex_commit, "manifest_source_commit_invalid"
        )
        bad_rate = dict(base)
        bad_rate["sample_rate_hz"] = 48000
        variants["wrong_rate"] = (bad_rate, "manifest_sample_rate_invalid")
        bad_channels = dict(base)
        bad_channels["channels"] = 2
        variants["wrong_channels"] = (bad_channels, "manifest_channels_invalid")
        bad_format = dict(base)
        bad_format["sample_format"] = "int16"
        variants["int16"] = (bad_format, "manifest_sample_format_invalid")
        bad_sampler = dict(base)
        bad_sampler["sampler"] = "ddim"
        variants["bad_sampler"] = (bad_sampler, "manifest_sampler_invalid")
        zero_steps = dict(base)
        zero_steps["sampler_steps"] = 0
        variants["zero_steps"] = (
            zero_steps, "manifest_sampler_steps_invalid"
        )
        bool_steps = dict(base)
        bool_steps["sampler_steps"] = True
        variants["boolean_steps"] = (
            bool_steps, "manifest_sampler_steps_invalid"
        )
        internal = dict(base)
        internal["storage"] = "vendored"
        variants["not_external"] = (internal, "manifest_storage_not_external")
        no_license = dict(base)
        no_license["license_id"] = ""
        variants["empty_license"] = (
            no_license, "manifest_field_invalid:license_id"
        )
        results: Dict[str, str] = {}
        for name, (manifest, expected) in variants.items():
            try:
                validate_caller_asset(manifest)
                results[name] = "accepted"
            except ValueError as exc:
                results[name] = str(exc)
            results[name + ":expected"] = expected
        return {
            "candidate_admission": candidate_result,
            "candidate_manifest_blocked": candidate_result["status"] == "blocked",
            "candidate_rejection_reasons": list(CANDIDATE_REJECTION_REASONS),
            "rejection_controls": results,
            "synthetic_accepted": synthetic["status"] == "accepted_structure",
            "synthetic_admission": synthetic_admission,
            "synthetic_control": {
                "asset_bytes_hashed": synthetic["asset_bytes_hashed"],
                "asset_bytes_read": synthetic["asset_bytes_read"],
                "candidate_asset": synthetic["candidate_asset"],
                "downloaded": synthetic["download_attempted"],
                "executed": synthetic["executed"],
                "imported": synthetic["imported"],
                "loaded": synthetic["loaded"],
                "qualification_effect": "none",
            },
        }


def streaming_control(fixture: Dict[str, Any]) -> Dict[str, Any]:
    samples = list(fixture["reverb_float"])
    one = process_chunks([samples], dict(CONFIG))
    try:
        process_chunks([samples[:8000], samples[8000:]], dict(CONFIG))
        chunked = "accepted"
    except ValueError as exc:
        chunked = str(exc)
    try:
        process_chunks([samples[:1]], dict(CONFIG))
        partial = "accepted"
    except ValueError as exc:
        partial = str(exc)
    return {
        "candidate_streaming_api": False,
        "chunked_expected": "utterance_level_offline_only",
        "chunked_result": chunked,
        "full_clip_output_samples": one["output_samples"],
        "one_shot_accepted": one["status"] == "ok",
        "partial_expected": "utterance_length_mismatch",
        "partial_result": partial,
        "streaming_claimed": False,
    }


def _digest_samples(samples: Sequence[float]) -> str:
    payload = json.dumps(list(samples), separators=(",", ":"), allow_nan=False)
    return sha256(payload.encode("utf-8"))


def surrogate_results(fixture: Dict[str, Any]) -> Dict[str, Any]:
    samples = list(fixture["reverb_float"])
    sde = process_utterance(samples, dict(CONFIG))
    sde_again = process_utterance(samples, dict(CONFIG))
    ode_config = dict(CONFIG)
    ode_config["sampler"] = "ode"
    ode = process_utterance(samples, ode_config)
    steps_one = dict(CONFIG)
    steps_one["sampler_steps"] = 1
    one_step = process_utterance(samples, steps_one)
    silence_config = dict(CONFIG)
    silence = process_utterance([0.0] * FIXTURE_SAMPLES, silence_config)
    zero_count = sum(1 for value in sde["output"] if value == 0.0)
    nonfinite = sum(
        1 for value in sde["output"] if not math.isfinite(float(value))
    )
    clipped = sum(1 for value in sde["output"] if abs(value) >= 1.0)
    return {
        "deterministic_repeat_equal": sde["output"] == sde_again["output"],
        "input_samples": sde["input_samples"],
        "max_abs_output": round(max(abs(value) for value in sde["output"]), 9),
        "nonfinite_output_count": nonfinite,
        "clipped_output_count": clipped,
        "one_shot_output_samples": sde["output_samples"],
        "output_samples_equal_input": sde["output_samples"]
        == sde["input_samples"],
        "sampler_modes_differ": sde["output"] != ode["output"],
        "sampler_step_variants_differ": sde["output"] != one_step["output"],
        "sde_digest": _digest_samples(sde["output"]),
        "ode_digest": _digest_samples(ode["output"]),
        "silence_exact_zero": all(value == 0.0 for value in silence["output"]),
        "silence_nonzero_count": sum(
            1 for value in silence["output"] if value != 0.0
        ),
        "zero_output_count": zero_count,
        "stateless_repeat": sde["output"] == sde_again["output"],
    }


# ---------------------------------------------------------------------------
# Report and contract
# ---------------------------------------------------------------------------


def _absence_audit() -> Dict[str, Any]:
    probes = {path: (SOURCE_ROOT / path).exists() for path in FIXED_ASSET_PROBES}
    home = {
        path: (Path.home() / path).exists() for path in HOME_ASSET_PROBES
    }
    return {
        "all_absence_probes_absent": not any(probes.values())
        and not any(home.values()),
        "cohort_manifest_present": probes[
            "data/runs/nemo-denoiser-cohort/manifest.json"
        ],
        "config_present": probes["data/models/nemo-denoiser"],
        "download_performed": False,
        "fixed_probes": probes,
        "home_probes": home,
        "license_record_present": probes[
            "data/rights/nemo-denoiser-model-license.json"
        ],
        "network_used": False,
        "parity_manifest_present": probes[
            "data/runs/nemo-denoiser-parity/manifest.json"
        ],
        "rights_record_present": probes[
            "data/rights/nemo-denoiser-rights.json"
        ],
        "runtime_lock_present": probes[
            "data/envs/nemo-denoiser/requirements.lock"
        ],
        "runtime_present": probes["data/envs/nemo-denoiser"],
        "source_checkout_present": any(
            probes[path]
            for path in (
                "data/checkouts/NeMo",
                "data/checkouts/nemo",
                "data/checkouts/nemo-denoiser",
            )
        ),
        "weights_present": any(
            probes[path]
            for path in (
                "data/models/nemo-denoiser",
                "data/models/nemo-denoiser/se_den_sb_16k_small.nemo",
                "data/models/se_den_sb_16k_small",
                "adapters/nemo-denoiser/checkpoint",
                "adapters/nemo-denoiser/model.nemo",
                "adapters/nemo-denoiser/weights",
            )
        ),
    }


def _asset_block() -> Dict[str, Any]:
    return {
        "asset": {
            "acquisition_cleared": False,
            "asset_bytes_read": False,
            "asset_id": "nemo_se_den_sb_16k_small_unpinned",
            "byte_count": CANDIDATE_CHECKPOINT_BYTES,
            "bytes_present_in_sdk_worktree": False,
            "candidate_model_id": CANDIDATE_MODEL_ID,
            "candidate_model_card": CANDIDATE_MODEL_CARD,
            "checkpoint_id": CANDIDATE_CHECKPOINT_ID,
            "code_license_metadata": CANDIDATE_LICENSE_STATUS,
            "customer_deployment_cleared": False,
            "digest_recomputed": False,
            "download_permitted": False,
            "evaluation_allowed": False,
            "home_probes": {
                path: (Path.home() / path).exists()
                for path in HOME_ASSET_PROBES
            },
            "ledger_entry_present": False,
            "model_license_metadata": CANDIDATE_LICENSE_STATUS,
            "observed_model_terms": "upstream_reported_not_reviewed",
            "path_relative": "data/models/nemo-denoiser/se_den_sb_16k_small.nemo",
            "pinned": False,
            "public_playback_cleared": False,
            "redistribution_cleared": False,
            "rights_entry_present": False,
            "runtime_available": False,
            "runtime_lock": None,
            "runtime_package": None,
            "runtime_target": None,
            "runtime_wheel_sha256": None,
            "sha256": CANDIDATE_CHECKPOINT_SHA256,
            "source_repository": CANDIDATE_SOURCE_REPOSITORY,
            "source_revision": CANDIDATE_SOURCE_REVISION,
            "storage": "external",
            "target_condition": (
                "16 kHz mono whole-utterance offline; sampler and exact config "
                "unverified"
            ),
            "workspace_copies": [
                {
                    "admitted": OBSERVED_ADAPTER["admitted"],
                    "exact_candidate": OBSERVED_ADAPTER["exact_candidate"],
                    "note": OBSERVED_ADAPTER["note"],
                    "path": OBSERVED_ADAPTER["path"],
                    "present": OBSERVED_ADAPTER["present"],
                    "sha256": OBSERVED_ADAPTER["sha256"],
                    "weights_present": OBSERVED_ADAPTER["weights_present"],
                }
            ],
            "workspace_probes": {
                path: (SOURCE_ROOT / path).exists()
                for path in FIXED_ASSET_PROBES
            },
        },
        "asset_admission": {
            "asset_bytes_hashed": False,
            "asset_bytes_read": False,
            "candidate_asset": True,
            "download_attempted": False,
            "model_runtime_invoked": False,
            "qualification_effect": "none",
            "reason_codes": list(CANDIDATE_REJECTION_REASONS),
            "status": "blocked",
        },
    }


def _rights_block() -> Dict[str, Any]:
    return {
        "acquisition": "unknown",
        "blocked": True,
        "consent": "not_applicable_no_speaker_reference",
        "customer_deployment": "unknown",
        "entry_present": False,
        "evaluation": "unknown",
        "evaluation_only": False,
        "license_reported": CANDIDATE_LICENSE,
        "license_review": CANDIDATE_LICENSE_STATUS,
        "noncommercial": True,
        "output_use": "unknown",
        "packaging_permitted": False,
        "public_playback": "unknown",
        "redistribution": "unknown",
        "register": RIGHTS_REGISTER_PATH,
        "register_detail": RIGHTS_JSON_PATH,
        "review_date": None,
        "reviewer": None,
        "share_alike": True,
        "weights_must_remain_private": True,
    }


def _qualification_block() -> Dict[str, Any]:
    return {
        "all_release_gates_blocked": True,
        "candidate_result_present": False,
        "checkpoint_present": False,
        "exact_reference_present": False,
        "geometry_verified": False,
        "missing_result_may_qualify": False,
        "missing_result_promoted": False,
        "not_qualified": True,
        "provider_intake_present": False,
        "qualified": False,
        "quality_result_present": False,
        "readiness": "incomplete",
        "release_claim": False,
        "runtime_present": False,
        "source_licensed": False,
        "source_present": False,
        "status": QUALIFICATION_STATUS,
        "timing_result_present": False,
    }


def _acceptance_profile() -> Dict[str, Any]:
    items = [
        {
            "evidence": "Identity/noisy synthetic control is exercised by deterministic fixture strata; no candidate model output exists.",
            "item": "identity/noisy control and task-matched baseline",
            "status": "synthetic_only_blocked_baseline",
        },
        {
            "evidence": "No clean-reference paired corpus or candidate output exists; paired SI-SDR/STOI cannot be scored.",
            "item": "paired SI-SDR and STOI on permitted clean references",
            "status": "blocked",
        },
        {
            "evidence": "Surrogate output remains finite and bounded on the synthetic control; no candidate clean-speech preservation claim is made.",
            "item": "clean-speech preservation, peaks and invalid outputs",
            "status": "surrogate_verified_no_candidate_claim",
        },
        {
            "evidence": "No unpaired speech corpus, predictive screen, or authorized listening was run.",
            "item": "unpaired predictive screen or authorized listening",
            "status": "blocked",
        },
        {
            "evidence": "No candidate alignment, state, memory, content/availability timing or exact runtime was measured.",
            "item": "alignment, state, memory and measured content/availability timing",
            "status": "blocked",
        },
    ]
    return {
        "candidate_qualified": False,
        "items": items,
        "profile": PROFILE,
        "source": "plan/swarm/VERIFICATION.md#profiles-by-task",
    }


def _asset_block() -> Dict[str, Any]:
    return {
        "asset": {
            "acquisition_cleared": False,
            "asset_bytes_read": False,
            "asset_id": "nemo_se_den_sb_16k_small_unpinned",
            "byte_count": CANDIDATE_CHECKPOINT_BYTES,
            "bytes_present_in_sdk_worktree": False,
            "candidate_model_id": CANDIDATE_MODEL_ID,
            "candidate_model_card": CANDIDATE_MODEL_CARD,
            "checkpoint_id": CANDIDATE_CHECKPOINT_ID,
            "code_license_metadata": CANDIDATE_LICENSE_STATUS,
            "customer_deployment_cleared": False,
            "digest_recomputed": False,
            "download_permitted": False,
            "evaluation_allowed": False,
            "home_probes": {
                path: (Path.home() / path).exists()
                for path in HOME_ASSET_PROBES
            },
            "ledger_entry_present": False,
            "model_license_metadata": CANDIDATE_LICENSE_STATUS,
            "observed_model_terms": "upstream_reported_not_reviewed",
            "path_relative": "data/models/nemo-denoiser/se_den_sb_16k_small.nemo",
            "pinned": False,
            "public_playback_cleared": False,
            "redistribution_cleared": False,
            "rights_entry_present": False,
            "runtime_available": False,
            "runtime_lock": None,
            "runtime_package": None,
            "runtime_target": None,
            "runtime_wheel_sha256": None,
            "sha256": CANDIDATE_CHECKPOINT_SHA256,
            "source_repository": CANDIDATE_SOURCE_REPOSITORY,
            "source_revision": CANDIDATE_SOURCE_REVISION,
            "storage": "external",
            "target_condition": (
                "16 kHz mono whole-utterance offline; sampler and exact config "
                "unverified"
            ),
            "workspace_copies": [
                {
                    "admitted": OBSERVED_ADAPTER["admitted"],
                    "exact_candidate": OBSERVED_ADAPTER["exact_candidate"],
                    "note": OBSERVED_ADAPTER["note"],
                    "path": OBSERVED_ADAPTER["path"],
                    "present": OBSERVED_ADAPTER["present"],
                    "sha256": OBSERVED_ADAPTER["sha256"],
                    "weights_present": OBSERVED_ADAPTER["weights_present"],
                }
            ],
            "workspace_probes": {
                path: (SOURCE_ROOT / path).exists()
                for path in FIXED_ASSET_PROBES
            },
        },
        "asset_admission": {
            "asset_bytes_hashed": False,
            "asset_bytes_read": False,
            "candidate_asset": True,
            "download_attempted": False,
            "model_runtime_invoked": False,
            "qualification_effect": "none",
            "reason_codes": list(CANDIDATE_REJECTION_REASONS),
            "status": "blocked",
        },
    }


def _rights_block() -> Dict[str, Any]:
    return {
        "acquisition": "unknown",
        "blocked": True,
        "consent": "not_applicable_no_speaker_reference",
        "customer_deployment": "unknown",
        "entry_present": False,
        "evaluation": "unknown",
        "evaluation_only": False,
        "license_reported": CANDIDATE_LICENSE,
        "license_review": CANDIDATE_LICENSE_STATUS,
        "noncommercial": True,
        "output_use": "unknown",
        "packaging_permitted": False,
        "public_playback": "unknown",
        "redistribution": "unknown",
        "register": RIGHTS_REGISTER_PATH,
        "register_detail": RIGHTS_JSON_PATH,
        "review_date": None,
        "reviewer": None,
        "share_alike": True,
        "weights_must_remain_private": True,
    }


def _qualification_block() -> Dict[str, Any]:
    return {
        "all_release_gates_blocked": True,
        "candidate_result_present": False,
        "checkpoint_present": False,
        "exact_reference_present": False,
        "geometry_verified": False,
        "missing_result_may_qualify": False,
        "missing_result_promoted": False,
        "not_qualified": True,
        "provider_intake_present": False,
        "qualified": False,
        "quality_result_present": False,
        "readiness": "incomplete",
        "release_claim": False,
        "runtime_present": False,
        "source_licensed": False,
        "source_present": False,
        "status": QUALIFICATION_STATUS,
        "timing_result_present": False,
    }


def _fixture_block(fixture: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "block_samples": FIXTURE_BLOCK_SAMPLES,
        "channels": CHANNELS,
        "clean_noise_decomposition": True,
        "geometry_scope": "probe_only",
        "sample_format": "float32",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "samples": FIXTURE_SAMPLES,
        "segments": [
            {
                "end_frame": segment["end_frame"],
                "id": segment["id"],
                "kind": segment["kind"],
                "start_frame": segment["start_frame"],
            }
            for segment in fixture["segments"]
        ],
    }


def _surrogate_block() -> Dict[str, Any]:
    return {
        "algorithm": "fixed_integer_late_subtraction_then_soft_limit",
        "candidate_sampler_emulated": False,
        "contains_neural_network": False,
        "contains_weights": False,
        "fixture_only": True,
        "model": False,
        "note": (
            "Synthetic whole-clip boundary surrogate; not NeMo and not evidence "
            "for the candidate."
        ),
        "sampler_steps": SURROGATE_SAMPLER_STEPS,
        "streaming": False,
    }


def _report_body() -> Dict[str, Any]:
    fixture = build_fixture()
    results = surrogate_results(fixture)
    controls = asset_admission_control()
    config_controls = config_adverse_control()
    input_controls = input_adverse_control(fixture)
    stream_controls = streaming_control(fixture)
    report: Dict[str, Any] = {
        "absence_audit": _absence_audit(),
        "acceptance_profile": _acceptance_profile(),
        "asset_boundary": _asset_block(),
        "base_commit": BASE_COMMIT,
        "board_policy": {
            "full_file_hashed": False,
            "mutable_fields_excluded": list(MUTABLE_BOARD_FIELDS),
            "mutable_file": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "selector": f"tasks[id={TASK}]",
            "stable_fields_only": True,
        },
        "board_row": {
            "full_tasks_json_hashed": False,
            "note": (
                "Only the stable linked-row identity is gated. The mutable full "
                "plan/swarm/TASKS.json is never read into, hashed by or pinned "
                "to this package."
            ),
            "stable_fields": dict(STABLE_TASK_IDENTITY),
            "stable_sha256": stable_identity_digest(),
        },
        "boundary": dict(BOUNDARY),
        "branch": BRANCH,
        "candidate": {
            "execution": "utterance_level_offline_sde_or_ode",
            "model_id": CANDIDATE_MODEL_ID,
            "model_card": CANDIDATE_MODEL_CARD,
            "reported_license": CANDIDATE_LICENSE,
            "reported_runtime": CANDIDATE_RUNTIME,
            "source_repository": CANDIDATE_SOURCE_REPOSITORY,
            "streaming_api": CANDIDATE_STREAMING_API,
        },
        "claims": dict(CLAIMS),
        "component": COMPONENT,
        "controls": {
            "asset": controls,
            "config_adverse": config_controls,
            "input_adverse": input_controls,
            "streaming": stream_controls,
            "variant_count": 3,
        },
        "counts": {
            "exact_blockers": len(EXACT_BLOCKERS),
            "release_gates_blocked": len(GATES),
            "release_gates_total": len(GATES),
        },
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(blocker) for blocker in EXACT_BLOCKERS],
        "feasibility": {
            "candidate_run_attempted": False,
            "comparison_reproduced": False,
            "comparison_retained": False,
            "decision_reason": (
                "Feasibility fails before implementation: no local NeMo or "
                "PyTorch runtime, no checkpoint, no config, no pinned upstream "
                "revision, no rights entry and no matched evidence exists. The "
                "local adapter README records upstream scope and scores only and "
                "was never executed. A caller-supplied-asset reference and an "
                "opt-in adapter cannot be built or verified, so no processor is "
                "exposed and the conditional implementation remains open."
            ),
            "inventory_area": "Echo and room",
            "inventory_disposition": "sdk-model",
            "inventory_evidence_status": "blocked",
            "inventory_record": INVENTORY_RECORD_ID,
            "matched_evidence_present": False,
            "permitted_scope": "unknown",
            "proceed_defer": DECISION,
            "required_for_proceed": list(MISSING_EVIDENCE),
            "research_finding": RESEARCH_FINDING,
            "research_line": RESEARCH_LINE,
            "research_path": RESEARCH_PATH,
            "research_status": "upstream_reported_not_locally_run",
            "runtime_available": False,
            "source_revision_pin_available": False,
            "streaming_api_present": False,
            "task_fit": (
                "Offline whole-utterance generative denoising comparator; "
                "not a streaming candidate and not locally runnable."
            ),
            "weights_available": False,
        },
        "fixture": _fixture_block(fixture),
        "format": dict(FORMAT),
        "mode": MODE,
        "native_evidence": {
            "candidate_native_reference_present": False,
            "fixture_trace_pin": None,
            "model_parity": "not_available",
            "model_quality": "not_assessed",
            "note": (
                "No NeMo processor, checkpoint, config, trace or parity vector "
                "exists. Sibling denoising evidence never transfers."
            ),
            "present_in_workspace": False,
            "sibling_artifacts_present": True,
            "sibling_scope": (
                "merged 2s-dereverb, localvqe-dereverberation-probe, "
                "nara-wpe-reference-tools and WPE evidence packages are "
                "different-model blockers and supply no NeMo artifact"
            ),
            "used_for_qualification": False,
        },
        "non_claims": list(NON_CLAIMS),
        "pins": {
            "board_file_pinned": False,
            "board_full_file_hashed": False,
            "boundary_pins": dict(BOUNDARY_PINS),
            "sibling_pins": dict(SIBLING_PINS),
            "source_pins": dict(SOURCE_PINS),
        },
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION_STATUS,
        "reference_interface": {
            "candidate_accepts_arbitrary_length": None,
            "candidate_algorithmic_latency_samples": None,
            "candidate_channels": CHANNELS,
            "candidate_config": None,
            "candidate_frame_geometry": None,
            "candidate_geometry_known": False,
            "candidate_hop_samples": None,
            "candidate_sample_format": "float32",
            "candidate_sample_rate_hz": SAMPLE_RATE_HZ,
            "candidate_sampler": None,
            "candidate_sampler_steps": None,
            "candidate_seed_behaviour": None,
            "candidate_solver": None,
            "candidate_streaming_api": False,
            "inspection_only": True,
            "model_bytes_read": False,
            "model_id": "nemo_se_den_sb_16k_small_unpinned",
            "note": (
                "Only 16 kHz mono whole-utterance scope and the absence of a "
                "streaming API are recorded. No exact config, sampler, solver, "
                "step count or geometry is fabricated."
            ),
            "source": "none: no pinned NeMo source, checkpoint or config exists",
            "surrogate_fixture": {
                "channels": CHANNELS,
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "samples": FIXTURE_SAMPLES,
                "sampler_steps": SURROGATE_SAMPLER_STEPS,
                "state_layout": [],
                "state_names": [],
            },
        },
        "release_gate_count": len(GATES),
        "release_gates": [dict(gate) for gate in GATES],
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "repository": "audio-sdk",
        "results": results,
        "reviewer": REVIEWER,
        "rights": _rights_block(),
        "schema_id": SCHEMA_ID,
        "source_reported_context": dict(SOURCE_REPORTED_CONTEXT),
        "status": STATUS,
        "streaming_semantics": {
            "candidate_streaming_api": False,
            "chunked_input_rejected": stream_controls["chunked_result"]
            == "utterance_level_offline_only",
            "device_clock_measured": False,
            "full_clip_only": True,
            "partial_input_rejected": stream_controls["partial_result"]
            == "utterance_length_mismatch",
            "streaming_claimed": False,
            "v0_frame_adapter_implemented": False,
            "v0_frame_samples": V0_FRAME_SAMPLES,
        },
        "surrogate": _surrogate_block(),
        "task": TASK,
        "task_identity": task_identity(),
        "title": TITLE,
        "tool_provenance": [
            "No NeMo source, checkpoint, config, weight, PyTorch runtime or sampler is present in this package; no candidate artifact was downloaded, loaded, compiled or invoked.",
            "Candidate scope and upstream scores are quoted from pinned workspace records and are not local measurements.",
            "The local adapter README is hashed read-only for provenance; it contains no source, weight, runtime or output.",
            "No candidate output, score, parity, listening result or timing exists.",
            "All fixture samples, state and outputs are generated by a stdlib deterministic surrogate in reference.py; no WAV, media, corpus or checkpoint is read.",
        ],
        "verification_profile": PROFILE,
        "worktree": WORKTREE,
    }
    return report


def _plain(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))


def build_report() -> Dict[str, Any]:
    return _plain(_report_body())


def contract_payload() -> Dict[str, Any]:
    gates = [
        {
            "evidence": gate["evidence"],
            "name": gate["name"],
            "qualifies": False,
            "reopen": gate["reopen"],
            "status": gate["status"],
        }
        for gate in GATES
    ]
    exact_blockers = [dict(blocker) for blocker in EXACT_BLOCKERS]
    return {
        "asset": _asset_block()["asset"],
        "asset_admission": _asset_block()["asset_admission"],
        "boundary": dict(BOUNDARY),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "candidate": {
            "checkpoint_id": CANDIDATE_CHECKPOINT_ID,
            "checkpoint_status": CANDIDATE_CHECKPOINT_STATUS,
            "geometry_status": CANDIDATE_GEOMETRY_STATUS,
            "license": CANDIDATE_LICENSE,
            "license_status": CANDIDATE_LICENSE_STATUS,
            "model_card": CANDIDATE_MODEL_CARD,
            "model_id": CANDIDATE_MODEL_ID,
            "repository": CANDIDATE_SOURCE_REPOSITORY,
            "revision": CANDIDATE_SOURCE_REVISION,
            "revision_status": CANDIDATE_SOURCE_STATUS,
            "runtime": CANDIDATE_RUNTIME,
            "runtime_status": CANDIDATE_RUNTIME_STATUS,
            "streaming_api": CANDIDATE_STREAMING_API,
        },
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "mutable_claim_not_hashed": True,
            "reviewer": REVIEWER,
            "worktree": WORKTREE,
        },
        "component_id": COMPONENT,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": exact_blockers,
        "format": dict(FORMAT),
        "gates": gates,
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "the package is proposal-only and incomplete",
            "no missing, blocked or rejected result is promoted to a pass",
            "no source, checkpoint, config, weight, runtime or corpus is downloaded, copied, imported, loaded or executed",
            "no claim is made from observed path presence or the local adapter README",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
        "local_files": list(LOCAL_FILES),
        "mode": MODE,
        "missing_evidence": list(MISSING_EVIDENCE),
        "negative_claims": list(NON_CLAIMS),
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION_STATUS,
        "release_gate_count": len(GATES),
        "release_gates": gates,
        "reopen_condition": (
            "Supply the exact source revision and licence, checkpoint and config "
            "with pinned byte counts and SHA-256, a locked offline NeMo/PyTorch "
            "runtime, the exact whole-utterance geometry and sampler, and clear "
            "artifact and corpus rights. Then reproduce exact-runtime outputs, "
            "score a rights-cleared paired cohort independently or with "
            "permitted listening, measure target timing and complete "
            "OFF-by-default opt-in provider intake."
        ),
        "repository": "audio-sdk",
        "reviewer": REVIEWER,
        "rights": _rights_block(),
        "schema_id": CONTRACT_SCHEMA_ID,
        "scope": {
            "benchmark_run": False,
            "device_timing_measured": False,
            "downloaded": False,
            "implementation_added": False,
            "listening_performed": False,
            "network_used": False,
            "provider_registered": False,
            "public_abi_changed": False,
            "real_assets_used": False,
            "registry_or_default_changed": False,
            "release_claim": False,
            "runtime_executed": False,
            "shared_build_or_ci_changed": False,
            "source_imported": False,
            "task_local_only": True,
            "weights_loaded": False,
            "write_scope": f"docs/task-evidence/{SLUG}/ only",
        },
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "task_id": TASK,
        "task_identity": task_identity(),
        "title": TITLE,
        "verification_profile": PROFILE,
    }


def spdx_header_text() -> str:
    """Return the exact sidecar text without embedding a contiguous token."""
    copyright_line = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
    license_line = "SPDX" "-License-Identifier: Apache-2.0"
    return copyright_line + "\n" + license_line + "\n"
