# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only feasibility evidence for SDK-MS-ISTFT-GENERATOR.

No exact MS-iSTFT-Generator source checkout, generator checkpoint, acoustic
feature contract, PyTorch/ONNX runtime, corpus, voice pair, generated candidate
waveform or device measurement exists in this workspace.  The pinned
accent-conversion record classifies MS-iSTFT-Generator as *not run* and records
that **no compatible accent-converter acoustic model/checkpoint was identified
for an end-to-end local run**.  A derived ``Multistream_iSTFT_Generator``
module is visible inside the MIT-licensed LLVC checkout, but it is not the
official MS-iSTFT-Generator release, carries no isolated weight, and is not
admitted to any gate.  Nothing here is downloaded, read, hashed, loaded,
compiled or executed.

This module provides four bounded pieces:

* a fail-closed absence audit over fixed workspace/home paths;
* a strict caller-supplied external-asset contract from ``CONTRACTS.md``
  (``as_asset_v0``: ID, byte count, SHA-256, ``storage=external``, no provider
  file access and no download) that only validates metadata;
* an explicitly synthetic, deterministic feature-frame boundary surrogate with
  a fixed two-frame delay, source-anchored accounting, finite drain, state
  reset and fail-closed rejection of invalid, missing and nonfinite input; and
* a paired synthetic scorer for that fixture only.

The synthetic branch is **not** MS-iSTFT-Generator, **not** a candidate vocoder and
substitutes for no release gate.  Candidate geometry is unknown and is recorded
as ``null``; the fixture's 80-bin/160-hop values are arbitrary bounded fixture
parameters, not candidate geometry.  The disposition is ``DEFER`` /
``proposal_only_incomplete`` / ``not_qualified``; all eight release gates remain
blocked and no missing result may qualify the candidate.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import struct
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2]))).resolve()
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml")
).resolve()

TASK = "SDK-MS-ISTFT-GENERATOR"
TITLE = "MS-iSTFT-Generator"
SLUG = "ms-istft-generator"
MODE = "feasibility"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "f8416852b07c700d232f75b28daba3de84748696"
BRANCH = f"swarm/{TASK}"
WORKTREE = f"/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/{TASK}"
REVIEWER = f"reviewer-{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_provider_intake"

# Installed v0 boundary is preserved.  The surrogate's feature hop is a fixture
# parameter only; it is not MS-iSTFT-Generator geometry.
SAMPLE_RATE_HZ = 16_000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
V0_FRAME_SAMPLES = 160
FEATURE_BINS = 80
FEATURE_HOP_SAMPLES = 160
SURROGATE_LOOKAHEAD_FRAMES = 2
BUFFERING_DELAY_SAMPLES = SURROGATE_LOOKAHEAD_FRAMES * FEATURE_HOP_SAMPLES
STARTUP_INVALID_SAMPLES = BUFFERING_DELAY_SAMPLES
DRAIN_FLUSH_FRAMES = SURROGATE_LOOKAHEAD_FRAMES
MAX_DRAIN_CALLS = 2
MAX_DRAIN_PRODUCED_SAMPLES = DRAIN_FLUSH_FRAMES * FEATURE_HOP_SAMPLES
FEATURE_FRAMES = 120
SAMPLES = FEATURE_FRAMES * FEATURE_HOP_SAMPLES
MAX_FEATURE_FRAMES_PER_STREAM = 400
MAX_STREAM_SAMPLES = MAX_FEATURE_FRAMES_PER_STREAM * FEATURE_HOP_SAMPLES
MAX_ABS_FEATURE = 1.0
MAX_ABS_AUDIO = 1.0
SEED_BASE = 2026_1126
CLOCK_ID = "fixture-frame-coordinate-not-device"
FEATURE_QUANTIZATION_STEPS = 63
SYNTHESIS_GAIN = 0.5
EPS = 1e-12

STATE_NAMES: Tuple[str, ...] = ("feature_delay",)
STATE_LAYOUT: Tuple[Tuple[int, ...], ...] = (
    (SURROGATE_LOOKAHEAD_FRAMES, FEATURE_BINS),
)

# Process-local memoization only; nothing here is written or shipped.
_SYNTH_CACHE: Dict[str, Tuple[List[float], List[float], List[List[float]]]] = {}
_STREAM_CACHE: Dict[str, List[float]] = {}
_REPORT_CACHE: Dict[str, Any] | None = None

CONDITIONS: Tuple[str, ...] = (
    "active_speech",
    "prosodic_phrase",
    "quiet_speech",
    "noisy_speech",
    "silence",
)

# Candidate identity is entirely unpinned.  The pinned records name no source
# repository or revision, and no weight byte count or digest exists.
ASSET_ID = "ms_istft_generator_checkpoint_unpinned"
ASSET_CHECKPOINT_ID = "ms_istft_generator.pt"
ASSET_LEDGER_PATH = "data/models/ms-istft-generator/generator.pt"
ASSET_BYTES = None
ASSET_SHA256 = None
SOURCE_REPOSITORY = None
SOURCE_REVISION = None
CANDIDATE_RELEASE_TAGS: Tuple[str, ...] = ()
CODE_LICENSE_METADATA = "not recorded"
MODEL_LICENSE_METADATA = "not recorded"
MODEL_TERMS_METADATA = "not recorded"
RUNTIME_PACKAGE = None
RUNTIME_WHEEL_SHA256 = None
RUNTIME_LOCK = None
RUNTIME_TARGET = None
TARGET_CONDITION = "unpinned"
CONSENT_SCOPE = "absent"
VOICE_TASK_FIT = "vocoder_component_only_no_checkpoint"

INVENTORY_RECORD_ID = "ms-istft-generator"
RESEARCH_README_PATH = "research/accent-conversion-20261101/README.md"
RESEARCH_README_LINE = 168
RESEARCH_STATUS = "Not run"
RESEARCH_FINDING = (
    "Vocoder component only; no compatible accent-converter acoustic "
    "model/checkpoint was identified for an end-to-end local run."
)
RESEARCH_HEADER = (
    "Accent conversion local evaluation: local runnable-model smoke tests and "
    "objective checks complete; human listening outstanding; blocked candidates "
    "kept separate from measured local results."
)
RESEARCH_TASK_FIT = (
    "A multi-stream iSTFT vocoder component alone cannot perform an accent "
    "conversion. The pinned record did not run MS-iSTFT-Generator and identified "
    "no compatible accent-converter acoustic model/checkpoint for an end-to-end "
    "local run."
)

# Fixed probes checked for presence only; no bytes are read or hashed.
FIXED_ASSET_PROBES: Tuple[str, ...] = (
    "data/checkouts/ms-istft-generator",
    "data/checkouts/MS-iSTFT-Generator",
    "data/checkouts/ms_istft_generator",
    "data/models/ms-istft-generator",
    "data/models/ms-istft-generator/generator.pt",
    "data/models/ms-istft-generator/generator.onnx",
    "data/models/ms_istft_generator",
    "data/models/ms_istft_generator/generator.pt",
    "cpp-library/.deps/ms_istft_generator.onnx",
    "data/envs/ms-istft-generator",
    "data/envs/ms-istft-generator/requirements.lock",
    "data/rights/ms-istft-generator-license.json",
    "data/rights/ms-istft-generator-model-license.json",
    "data/rights/ms-istft-generator-rights.json",
    "data/runs/ms-istft-generator-cohort/manifest.json",
    "data/runs/ms-istft-generator-parity/manifest.json",
)
HOME_ASSET_PROBES: Tuple[str, ...] = (
    ".cache/huggingface/hub/models--ms-istft-generator",
    ".cache/huggingface/hub/models--MS-iSTFT-Generator",
    ".cache/huggingface/hub/models--ms_istft_generator",
)

# One derived multi-stream iSTFT module is visible inside the LLVC checkout.  It
# is recorded, pinned and explicitly *not admitted*: it is not the official
# MS-iSTFT-Generator release, has no isolated weight, model card or runtime, and
# the LLVC checkpoint used for a full-system run was deleted after evaluation.
OBSERVED_COPIES: Tuple[Dict[str, Any], ...] = (
    {
        "project": "LLVC (Koe AI)",
        "path": "research/voice-conversion-eval-20261101/repos/llvc",
        "revision": "1627c5d358cf9bb2b92b0ccc513d8b36807c923d",
        "variant": (
            "derived Multistream_iSTFT_Generator selected by ms_istft_vits=True"
        ),
        "generator_path": "minimal_quickvc/models.py",
        "generator_sha256": (
            "af787a196e3f21083bf96a452de00eed22d5b4ae1193aafa814a68baab616150"
        ),
        "license": "MIT",
        "license_path": "LICENSE",
        "license_sha256": (
            "718657c20ba7035b25bb447d80a53304115b44fea7e684df2a1ca240555eae4b"
        ),
        "weights_present": False,
        "exact_upstream": False,
        "admitted": False,
        "note": (
            "Derived multi-stream iSTFT decoder inside the MIT-licensed LLVC "
            "project, not an official MS-iSTFT-Generator source release. The "
            "checkout contains no weight of any kind; the LLVC checkpoint used "
            "for a full any-to-one VC run was removed after evaluation, and no "
            "isolated vocoder parity, quality or timing result exists."
        ),
    },
)

# Explicitly synthetic admission control.  These bytes are not model weights.
SYNTHETIC_ASSET_ID = "synthetic-ms-istft-boundary-surrogate-not-ms-istft"
SYNTHETIC_ASSET_UNIT = b"audio-sdk/ms-istft-generator/synthetic-boundary-control/v1\n"
SYNTHETIC_ASSET_UNITS = 64
SYNTHETIC_ASSET_BYTES = SYNTHETIC_ASSET_UNIT * SYNTHETIC_ASSET_UNITS
SYNTHETIC_ASSET_SHA256 = hashlib.sha256(SYNTHETIC_ASSET_BYTES).hexdigest()

SOURCE_PINS: Dict[str, str] = {
    RESEARCH_README_PATH:
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/audio-pro/docs/rights-register.md":
        "e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44",
    "audio-benchmark-platform/audio-pro/inventory/rights-register.json":
        "24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923",
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/repos/llvc/LICENSE":
        "718657c20ba7035b25bb447d80a53304115b44fea7e684df2a1ca240555eae4b",
    "research/voice-conversion-eval-20261101/repos/llvc/minimal_quickvc/models.py":
        "af787a196e3f21083bf96a452de00eed22d5b4ae1193aafa814a68baab616150",
    "research/voice-conversion-eval-20261101/repos/llvc/minimal_quickvc/stft.py":
        "c7ce7cb488452d7ac523989d6dfc14ca1fe83a888e119052b46977b67501ebb6",
    "research/voice-conversion-eval-20261101/repos/llvc/minimal_quickvc/commons.py":
        "9f58ea84ed94dba3c7ac8cdd352aea279b979e1c0fbaad820d09275f91990672",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}
SIBLING_PINS: Dict[str, str] = {
    "docs/task-evidence/hifi-gan-vocoder/README.md":
        "75d3ae938366adeabdfeb022580f0a3554feb1d5f5f771fd82edd7943e8695a5",
    "docs/task-evidence/vocos/README.md":
        "9874b61a5acef218c59ae0fbbdf6165ec3e65c69d12010150a4b041d814c66dd",
    "docs/task-evidence/micro-hifi-gan/README.md":
        "53958c94833e8513d906fa8b6ef61dfb8c6b3d0b7c4d9a6c6accddee10bf8edc",
}

# Fail-closed local file set.  SOURCES.sha256 and the contract are excluded from
# the README digest table; SOURCES.sha256 is excluded because a manifest cannot
# pin its own bytes.
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "contract.json",
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
TABLE_FILES: Tuple[str, ...] = (
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "test_reference.py",
    "verify.py",
)

# Stable linked-row identity.  Mutable board fields (status, owner, claim,
# review, handoff, blocked_reason, timestamps and history) are deliberately
# excluded; plan/swarm/TASKS.json is never hashed as a whole file.
STABLE_TASK_IDENTITY: Dict[str, Any] = {
    "id": TASK,
    "title": TITLE,
    "repository": "audio-sdk",
    "mode": MODE,
    "component": SLUG,
    "dispatch_priority": 3,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-EVIDENCE",
        "SDK-FND-PROVIDER",
    ],
    "write_scope": [
        f"SDK provider, tool or evidence directory for {SLUG} and its own fixtures"
    ],
    "deliverable": (
        "Verify runnable source, exact assets, permitted scope, task geometry and "
        "matched evidence. Then reproduce the exact model/runtime as a "
        "caller-supplied-asset reference and add an opt-in SDK adapter once its "
        "prerequisites pass. Record a concrete blocker if feasibility fails."
    ),
    "acceptance": (
        "Apply the voice acceptance profile; record exact scope, evidence, "
        "failure/control results, and remaining release gates. A readiness "
        "conclusion with an exact external blocker is an accepted investigation "
        "handoff; it does not close the conditional implementation."
    ),
    "evidence": [RESEARCH_README_PATH],
    "verification_profile": PROFILE,
    "profile_source": f"plan/INVENTORY.json#components[id={INVENTORY_RECORD_ID}]",
    "board_selector": f"tasks[id={TASK}]",
    "board_full_file_hashed": False,
    "mutable_fields_excluded": [
        "status",
        "owner",
        "claim",
        "review",
        "handoff",
        "blocked_reason",
        "initialized_on",
        "history",
    ],
}

PROJECTED_BOARD_FIELDS: Tuple[str, ...] = (
    "acceptance",
    "component",
    "deliverable",
    "depends_on",
    "dispatch_priority",
    "evidence",
    "id",
    "mode",
    "repository",
    "title",
    "write_scope",
)

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "v0_frame_samples": V0_FRAME_SAMPLES,
    "surrogate_feature_bins": FEATURE_BINS,
    "surrogate_feature_hop_samples": FEATURE_HOP_SAMPLES,
    "surrogate_lookahead_frames": SURROGATE_LOOKAHEAD_FRAMES,
    "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
    "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
    "drain_flush_frames": DRAIN_FLUSH_FRAMES,
    "max_drain_calls": MAX_DRAIN_CALLS,
    "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
    "processing_mode": "synthetic_feature_frame_boundary_surrogate",
    "candidate_geometry_known": False,
    "clock": CLOCK_ID,
}

BOUNDARY: Dict[str, bool] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "installed_v0_geometry_preserved": True,
    "installed_v0_behavior_change": False,
    "shared_build_or_ci_change": False,
    "processor_exposure": False,
    "task_board_or_handoff_write": False,
    "adapter_json_added": False,
    "readiness_json_added": False,
    "asset_bundled": False,
    "weights_vendored": False,
    "model_runtime_invoked": False,
    "vocoder_invoked": False,
    "sdk_data_dir_added": False,
}

CLAIMS: Dict[str, bool] = {
    "real_ms_istft_runtime": False,
    "real_vocoder_runtime": False,
    "official_source_read": False,
    "source_read": False,
    "weights_accessed": False,
    "weights_hashed": False,
    "asset_downloaded": False,
    "asset_bytes_read": False,
    "model_bytes_read": False,
    "model_runtime_invoked": False,
    "payload_inference_invoked": False,
    "real_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "chunk_latency_measured": False,
    "listening_result_produced": False,
    "semantic_preservation_claimed": False,
    "speaker_identity_claimed": False,
    "naturalness_claimed": False,
    "accent_conversion_claimed": False,
    "benchmark_result": False,
    "quality_claim": False,
    "parity_claim": False,
    "release_claim": False,
}

EXACT_BLOCKERS: Tuple[str, ...] = (
    "No exact MS-iSTFT-Generator source is present or pinned. There is no checkout "
    "under data/checkouts (ms-istft-generator, MS-iSTFT-Generator, "
    "ms_istft_generator), no official repository revision, no LICENSE/notice "
    "bundle for that release and no official source digest. The pinned research "
    "record names no official repository or immutable revision. A derived "
    "Multistream_iSTFT_Generator module is visible at LLVC commit "
    "1627c5d358cf9bb2b92b0ccc513d8b36807c923d (MIT, minimal_quickvc/models.py), "
    "but it is not the official MS-iSTFT-Generator release and is not admitted.",
    "No exact weight identity exists. No generator checkpoint, ONNX graph, release "
    "tag, byte count, SHA-256 or linked asset-ledger row is recorded. Fixed probes "
    "are absent: data/models/ms-istft-generator, "
    "data/models/ms-istft-generator/generator.pt, "
    "data/models/ms-istft-generator/generator.onnx, "
    "data/models/ms_istft_generator, data/models/ms_istft_generator/generator.pt "
    "and cpp-library/.deps/ms_istft_generator.onnx. The observed LLVC checkout "
    "contains zero weight files, and its full-system LLVC checkpoint was removed "
    "after the documented any-to-one run.",
    "No runtime is present or pinned. There is no recorded Python, PyTorch, ONNX "
    "Runtime or other host version, wheel digest, target platform, lock file or "
    "evaluator environment; data/envs/ms-istft-generator is absent. No "
    "exact-runtime reference run, parity vector or isolated vocoder inference was "
    "produced.",
    "Rights, permitted scope and consent are unresolved. The rights register has no "
    "ms-istft-generator, ms_istft_generator or istft entry, so acquisition, "
    "evaluation, redistribution, customer deployment and public playback are all "
    "unknown. The containing LLVC code is MIT, but no MS-iSTFT-Generator model "
    "card, weight terms or training-data terms exist, and MIT source alone does "
    "not clear weights, voice references or outputs. For a voice task, consent for "
    "source and target speaker references, reference availability and output use "
    "are independent gates and none is recorded.",
    "No candidate geometry is known. No authoritative MS-iSTFT-Generator sample "
    "rate, spectral configuration, subband count, iSTFT FFT/hop layout, receptive "
    "field, lookahead or streaming state is recorded. Constructor defaults in the "
    "observed derived LLVC file are not an authoritative candidate pin, so this "
    "package fabricates none and exposes no v0 frame adapter. The surrogate's "
    "80-bin/160-hop/2-frame values are fixture parameters, not candidate geometry.",
    "The pinned research evidence is a negative run record, not candidate evidence. "
    "It states the candidate was not run because no compatible accent-converter "
    "acoustic model/checkpoint was identified for an end-to-end local run. A "
    "multi-stream iSTFT vocoder alone cannot perform an accent conversion, and "
    "there is no fixed upstream acoustic model, feature contract or end-to-end "
    "accent-conversion pipeline to reproduce.",
    "No candidate evidence exists. There is no output, exact-reference parity, "
    "rights-cleared paired voice cohort with permitted references, independent "
    "semantic, identity or naturalness scorer, permitted listening result or "
    "target-runtime timing. The synthetic feature-frame surrogate is not "
    "MS-iSTFT-Generator and cannot qualify the candidate. All eight release gates "
    "remain blocked and no result may qualify the candidate.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen source identity only when the exact MS-iSTFT-Generator source revision is "
    "present, pinned by 40-hex commit, tree digest, reviewed LICENSE and notice "
    "bundle, and recorded against the pinned research evidence row.",
    "Reopen asset identity only when the exact generator checkpoint is supplied as a "
    "caller-owned external asset with immutable upstream revision, release tag, byte "
    "count, SHA-256 and declared feature geometry, and the SDK session verifies those "
    "bytes without provider file access or download.",
    "Reopen runtime admission only when the exact pinned host and model runtime "
    "install in the intended environment with recorded artifact digests, documented "
    "distribution and product-use terms, and exact-runtime reference outputs are "
    "produced.",
    "Reopen rights and consent only after artifact-specific written terms record "
    "evaluation, redistribution, customer deployment and public playback decisions, "
    "and consent for source and target speaker references plus permitted output use "
    "is recorded. Possession or evaluation permission alone is not clearance.",
    "Reopen task geometry and fit only with a fixed upstream acoustic feature "
    "contract, authoritative MS-iSTFT-Generator spectral/subband/iSTFT geometry and "
    "an end-to-end accent-conversion pipeline that isolates the vocoder; a vocoder "
    "alone is not an accent conversion and constructor defaults in an unrelated "
    "derived checkout are not geometry evidence.",
    "Reopen exact reference parity only with approved outputs for frozen inputs from "
    "the exact caller-supplied assets under the exact pinned runtime, reproducible "
    "across three cold starts.",
    "Reopen the cohort and scoring gates only with a rights-cleared paired voice "
    "cohort that freezes permitted source and target references, task, language and "
    "speaker groups, plus independent semantic-preservation, speaker-identity and "
    "naturalness measurements and permitted listening under a recorded protocol.",
    "Reopen timing/provider/default only with target-runtime first-output, tail, "
    "availability, pacing, deadline and memory measurements, then an opt-in provider "
    "intake with OFF default, descriptor/catalog review and an explicit owner default "
    "decision.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "exact MS-iSTFT-Generator source revision, per-file digest manifest and LICENSE/notice bundle",
    "exact generator checkpoint with revision, release tag, byte count, SHA-256 and feature geometry",
    "installed pinned host/model runtime with recorded digests and documented terms",
    "written rights decisions for evaluation, redistribution, customer deployment and public playback",
    "recorded consent for source and target speaker references and permitted output use",
    "fixed upstream acoustic features and an end-to-end accent-conversion pipeline isolating the vocoder",
    "approved exact-runtime reference outputs for frozen inputs, reproducible across three cold starts",
    "rights-cleared paired voice cohort and independent semantic, identity, naturalness and timing evidence",
)

GATES: Tuple[Dict[str, str], ...] = (
    {
        "name": "exact_asset_identity",
        "status": "blocked",
        "evidence": (
            "No source revision, weight byte count, SHA-256, release tag or ledger "
            "row exists; every fixed source and asset probe is absent and no bytes "
            "were caller-supplied."
        ),
        "reopen": REOPEN_CONDITIONS[0] + " " + REOPEN_CONDITIONS[1],
    },
    {
        "name": "runtime_admission",
        "status": "blocked",
        "evidence": (
            "No host/model runtime version, wheel digest, lock file, target platform "
            "or evaluator environment is recorded or present."
        ),
        "reopen": REOPEN_CONDITIONS[2],
    },
    {
        "name": "artifact_rights",
        "status": "blocked",
        "evidence": (
            "No ms-istft-generator or ms_istft entry exists in the rights register; "
            "all scopes are unknown and no speaker consent or output-use permission "
            "is recorded."
        ),
        "reopen": REOPEN_CONDITIONS[3],
    },
    {
        "name": "exact_reference_parity",
        "status": "blocked",
        "evidence": (
            "No candidate output, frozen input feature, exact-runtime reference or "
            "parity trace exists for MS-iSTFT-Generator."
        ),
        "reopen": REOPEN_CONDITIONS[5],
    },
    {
        "name": "rights_cleared_voice_cohort",
        "status": "blocked",
        "evidence": (
            "No rights-cleared paired voice cohort with permitted source and target "
            "references exists in this package."
        ),
        "reopen": REOPEN_CONDITIONS[6],
    },
    {
        "name": "independent_scoring_and_listening",
        "status": "blocked",
        "evidence": (
            "No independent semantic-preservation, speaker-identity or naturalness "
            "scorer and no permitted listening result exists; surrogate signal "
            "metrics are synthetic only."
        ),
        "reopen": REOPEN_CONDITIONS[6],
    },
    {
        "name": "target_runtime_timing",
        "status": "blocked",
        "evidence": (
            "No first-output, tail, availability, pacing, deadline or memory "
            "measurement was made; no accelerator, CPU or device profile is pinned."
        ),
        "reopen": REOPEN_CONDITIONS[7],
    },
    {
        "name": "provider_intake_and_default_selection",
        "status": "blocked",
        "evidence": (
            "No opt-in provider, descriptor or catalog entry exists; no default "
            "decision was made."
        ),
        "reopen": REOPEN_CONDITIONS[7],
    },
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "scope": "Pinned research provenance only; not reproduced, pooled or used as a threshold.",
    "pinned_inventory_record": (
        "plan/INVENTORY.json components[id=ms-istft-generator]: name MS-iSTFT-Generator, "
        "area 'Voice and synthesis', disposition sdk-model, evidence_status "
        "considered, verification_profile voice, finding 'Not run. Vocoder component "
        "only; no compatible accent-converter acoustic model/checkpoint was "
        "identified for an end-to-end local run.'"
    ),
    "pinned_research_row": (
        "research/accent-conversion-20261101/README.md line 168: MS-iSTFT-Generator | "
        "Not run. | Vocoder component only; no compatible accent-converter acoustic "
        "model/checkpoint was identified for an end-to-end local run."
    ),
    "pinned_research_scope": RESEARCH_HEADER,
    "task_fit_conclusion": RESEARCH_TASK_FIT,
    "observed_derived_source": (
        "research/voice-conversion-eval-20261101/repos/llvc at commit "
        "1627c5d358cf9bb2b92b0ccc513d8b36807c923d (MIT) defines "
        "Multistream_iSTFT_Generator in minimal_quickvc/models.py, selected by "
        "ms_istft_vits=True. This is a derived module inside a full any-to-one VC "
        "project, not an official MS-iSTFT-Generator release; it has no weight, "
        "model card, isolated runtime or vocoder-only result and is not admitted."
    ),
    "source_reported_llvc_context": (
        "The pinned research/voice-conversion-eval-20261101/README.md records one "
        "full-system LLVC any-to-one VC streaming run at commit 1627c5d: RTF 0.123 "
        "and an estimated 120.785 ms end-to-end latency on the M1 CPU host. That "
        "checkpoint was removed after the run and the result is not an isolated "
        "MS-iSTFT-Generator parity, quality or timing measurement."
    ),
    "sibling_boundary": (
        "The merged hifi-gan-vocoder, vocos and micro-hifi-gan evidence packages are "
        "adjacent vocoder blockers for different models. Their absent-asset "
        "findings, geometry and timing never transfer to MS-iSTFT-Generator and are "
        "not candidate evidence here."
    ),
    "no_candidate_metrics": (
        "No MS-iSTFT-Generator run, output, score, RTF, listening result, "
        "semantic-preservation measurement, speaker-identity measurement or "
        "naturalness measurement exists in any pinned local record."
    ),
    "disclaimer": (
        "These strings are quoted from pinned research files. They are not "
        "reproduced here, not device timing, not this fixture's metrics, not a "
        "listening result and not a release claim."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "No official MS-iSTFT-Generator source, weight, model runtime or vocoder is present in this package; no candidate artifact was downloaded, loaded, compiled or invoked.",
    "Source role, task fit and the negative run record are quoted from pinned workspace records.",
    "The observed LLVC-derived Multistream_iSTFT_Generator and its containing LICENSE were hashed read-only for provenance; no weight, checkpoint or graph was read, loaded, executed or admitted.",
    "No candidate output, score, parity, listening result or timing exists; the pinned research row is provenance only.",
    "All features, state and outputs are generated by a stdlib deterministic surrogate in reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
)

NON_CLAIMS: Tuple[str, ...] = (
    "No official MS-iSTFT-Generator source, weight, derived weight, graph, runtime, vocoder, corpus or media was downloaded, loaded, compiled, executed or bundled; the observed LLVC-derived source and LICENSE are hashed read-only for provenance only.",
    "No public API/ABI, CONTRACTS.md, descriptor, registry, installed default, shared build, dependency lock, CI, board or handoff file was changed.",
    "No listening, MOS, semantic-preservation, speaker-identity, naturalness, accent-conversion, parity, benchmark, device-timing, latency or release result is claimed for the candidate.",
    "The LLVC full-system runtime/latency record is quoted provenance, not an isolated MS-iSTFT-Generator result.",
    "The synthetic feature-frame boundary surrogate is not MS-iSTFT-Generator and no missing result ever qualifies the candidate.",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise ValueError("nonfinite float in canonical JSON")
        return 0.0 if value == 0.0 else value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize_negzero(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def r6(value: float | None) -> float | None:
    if value is None:
        return None
    rounded = round(float(value), 6)
    return 0.0 if rounded == 0.0 else rounded


def stable_identity_digest(identity: Dict[str, Any] | None = None) -> str:
    payload = dict(identity or STABLE_TASK_IDENTITY)
    payload.pop("stable_sha256", None)
    payload.pop("board_full_file_hashed", None)
    payload.pop("mutable_fields_excluded", None)
    return sha256(canonical_bytes(payload))


def stable_row_digest(fields: Dict[str, Any]) -> str:
    """Digest only the projected stable linked-row fields."""
    projected = {field: fields[field] for field in PROJECTED_BOARD_FIELDS}
    return sha256(canonical_bytes(projected))


def task_identity() -> Dict[str, Any]:
    identity = dict(STABLE_TASK_IDENTITY)
    identity["stable_sha256"] = stable_identity_digest()
    identity["board_full_file_hashed"] = False
    identity["mutable_fields_excluded"] = list(
        STABLE_TASK_IDENTITY["mutable_fields_excluded"]
    )
    return identity


def project_board_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Project only stable linked-row identity; never hash the mutable file."""
    missing = [field for field in PROJECTED_BOARD_FIELDS if field not in row]
    if missing:
        raise ValueError("board row missing stable field: " + ",".join(missing))
    projected = {field: row[field] for field in PROJECTED_BOARD_FIELDS}
    projected["stable_sha256"] = stable_row_digest(projected)
    return projected


# ---------------------------------------------------------------------------
# Deterministic synthetic features and signals (analytic; no corpus or media)
# ---------------------------------------------------------------------------


def _seed(name: str) -> int:
    return (
        SEED_BASE
        + int.from_bytes(hashlib.sha256(name.encode("ascii")).digest()[:4], "big")
    ) & 0xFFFFFFFF


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF

    def nxt() -> float:
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state / 4294967296.0

    return nxt


def _gaussian(rng) -> float:
    total = 0.0
    for _ in range(12):
        total += rng()
    return total - 6.0


def _bin_frequency(bin_index: int) -> float:
    low, high = 80.0, 7_600.0
    return low * (high / low) ** (bin_index / (FEATURE_BINS - 1))


def _bin_phase(bin_index: int) -> float:
    return (0.37 * bin_index) % (2.0 * math.pi)


def _frame_gate(condition: str, index: int, total: int) -> float:
    if condition == "silence":
        return 0.0
    if condition == "prosodic_phrase":
        start = int(total * 0.20)
        end = int(total * 0.85)
        ramp = 8
        if index < start or index >= end:
            return 0.0
        if index < start + ramp:
            return (index - start) / ramp
        if index >= end - ramp:
            return (end - index) / ramp
        return 0.65 + 0.35 * math.sin(2.0 * math.pi * 3.0 * index / total)
    return 1.0


def _frame_scale(condition: str) -> float:
    if condition == "quiet_speech":
        return 0.35
    return 1.0


def features(condition: str) -> List[List[float]]:
    """Synthetic mel-like feature frames; not a candidate feature contract."""
    if condition not in CONDITIONS:
        raise ValueError("unknown condition: " + condition)
    rng = _lcg(_seed("features:" + condition))
    scale = _frame_scale(condition)
    frames: List[List[float]] = []
    for index in range(FEATURE_FRAMES):
        gate = _frame_gate(condition, index, FEATURE_FRAMES)
        contour = 0.55 + 0.45 * math.sin(
            2.0 * math.pi * 3.0 * index / FEATURE_FRAMES + 0.4
        )
        frame: List[float] = []
        for bin_index in range(FEATURE_BINS):
            frequency = _bin_frequency(bin_index)
            formant = 1.0 / (1.0 + abs(math.log(frequency / 500.0)))
            formant += 0.6 * math.exp(-((math.log(frequency / 1_200.0)) ** 2) / 0.5)
            jitter = 0.9 + 0.2 * rng()
            value = gate * scale * contour * formant * jitter * 0.55
            frame.append(0.0 if value < 0.0 else (1.0 if value > 1.0 else value))
        frames.append(frame)
    return frames


def _quantize_frame(frame: Sequence[float]) -> List[float]:
    quantized: List[float] = []
    for value in frame:
        scaled = round(float(value) * FEATURE_QUANTIZATION_STEPS)
        quantized.append(scaled / FEATURE_QUANTIZATION_STEPS)
    return quantized


def render_frame(frame: Sequence[float], frame_index: int) -> List[float]:
    """Deterministic additive synthesis for one frame; not a vocoder.

    Carrier phases are advanced with an exact per-bin rotation recurrence so the
    fixture avoids millions of transcendental calls while remaining deterministic
    on a fixed platform.
    """
    start = frame_index * FEATURE_HOP_SAMPLES
    amplitudes = [float(value) for value in frame]
    cosine: List[float] = []
    sine: List[float] = []
    cosine_step: List[float] = []
    sine_step: List[float] = []
    for bin_index in range(FEATURE_BINS):
        omega = (
            2.0
            * math.pi
            * _bin_frequency(bin_index)
            * start
            / SAMPLE_RATE_HZ
        )
        phase = _bin_phase(bin_index)
        cosine.append(math.cos(omega + phase))
        sine.append(math.sin(omega + phase))
        step = (
            2.0
            * math.pi
            * _bin_frequency(bin_index)
            / SAMPLE_RATE_HZ
        )
        cosine_step.append(math.cos(step))
        sine_step.append(math.sin(step))
    output: List[float] = []
    for _local in range(FEATURE_HOP_SAMPLES):
        total = 0.0
        for bin_index in range(FEATURE_BINS):
            total += amplitudes[bin_index] * cosine[bin_index]
        output.append(math.tanh(SYNTHESIS_GAIN * total / FEATURE_BINS))
        for bin_index in range(FEATURE_BINS):
            current_cos = cosine[bin_index]
            current_sin = sine[bin_index]
            cosine[bin_index] = (
                current_cos * cosine_step[bin_index]
                - current_sin * sine_step[bin_index]
            )
            sine[bin_index] = (
                current_sin * cosine_step[bin_index]
                + current_cos * sine_step[bin_index]
            )
    return output


def synth_features(frames: Sequence[Sequence[float]], quantize: bool = False) -> List[float]:
    output: List[float] = []
    for frame_index, frame in enumerate(frames):
        selected = _quantize_frame(frame) if quantize else [float(v) for v in frame]
        output.extend(render_frame(selected, frame_index))
    return output


def synth(condition: str) -> Tuple[List[float], List[float], List[List[float]]]:
    """Return target, noisy observed and synthetic features for one condition."""
    cached = _SYNTH_CACHE.get(condition)
    if cached is not None:
        return cached
    frames = features(condition)
    target = synth_features(frames)
    if condition == "quiet_speech":
        noise_sigma = 0.012
    elif condition == "noisy_speech":
        noise_sigma = 0.090
    elif condition == "silence":
        noise_sigma = 0.006
    else:
        noise_sigma = 0.030
    rng = _lcg(_seed("observed:" + condition))
    observed = [value + noise_sigma * _gaussian(rng) for value in target]
    result = (target, observed, frames)
    _SYNTH_CACHE[condition] = result
    return result


# ---------------------------------------------------------------------------
# Synthetic delayed feature-frame surrogate (not MS-iSTFT-Generator)
# ---------------------------------------------------------------------------


def zero_state() -> Dict[str, Any]:
    return {
        "feature_delay": [
            [0.0] * FEATURE_BINS
            for _ in range(SURROGATE_LOOKAHEAD_FRAMES)
        ],
    }


def _shape_of(value: Any) -> Tuple[int, ...] | None:
    shape: List[int] = []
    current = value
    while isinstance(current, list):
        shape.append(len(current))
        if len(current) == 0:
            return tuple(shape)
        first = current[0]
        if any(not isinstance(item, list) for item in current):
            if any(isinstance(item, list) for item in current):
                return None
            return tuple(shape)
        current = first
    return tuple(shape)


def _flatten(value: Any) -> List[Any]:
    if isinstance(value, list):
        flat: List[Any] = []
        for item in value:
            flat.extend(_flatten(item))
        return flat
    return [value]


def _finite(value: Any) -> bool:
    return all(math.isfinite(float(item)) for item in _flatten(value))


def validate_state(state: Any) -> str | None:
    if not isinstance(state, dict):
        return "state_layout_mismatch"
    if set(state) != set(STATE_NAMES):
        return "state_layout_mismatch"
    if _shape_of(state["feature_delay"]) != STATE_LAYOUT[0]:
        return "state_layout_mismatch"
    values = _flatten(state["feature_delay"])
    if any(isinstance(item, bool) for item in values):
        return "state_type_invalid"
    if not _finite(values):
        return "state_nonfinite"
    if any(
        float(item) < 0.0 or float(item) > MAX_ABS_FEATURE for item in values
    ):
        return "state_out_of_range"
    return None


def surrogate_frame(
    frame: Sequence[float], state: Dict[str, Any], frame_index: int
) -> Tuple[List[float], Dict[str, Any]]:
    """One delayed frame step; payloads are fixture values only."""
    delayed = state["feature_delay"]
    output = render_frame(delayed[0], frame_index)
    new_state = {
        "feature_delay": [list(delayed[1]), [float(value) for value in frame]],
    }
    return output, new_state


def surrogate_stream(frames: Sequence[Sequence[float]]) -> List[float]:
    """Drive the synthetic frame API, drop startup delay and trim to source."""
    key = feature_digest(frames)
    cached = _STREAM_CACHE.get(key)
    if cached is not None:
        return cached
    state = zero_state()
    collected: List[float] = []
    sequence = [[float(value) for value in frame] for frame in frames]
    for frame_index in range(len(sequence) + DRAIN_FLUSH_FRAMES):
        if frame_index < len(sequence):
            frame = sequence[frame_index]
        else:
            frame = [0.0] * FEATURE_BINS
        output, state = surrogate_frame(frame, state, frame_index)
        collected.extend(output)
    source_samples = len(sequence) * FEATURE_HOP_SAMPLES
    result = collected[
        STARTUP_INVALID_SAMPLES : STARTUP_INVALID_SAMPLES + source_samples
    ]
    _STREAM_CACHE[key] = result
    return result


def surrogate_chunk_loop_control(frames: Sequence[Sequence[float]]) -> List[float]:
    """Independent driver over the same public frame step; byte-identical."""
    state = zero_state()
    output: List[float] = []
    sequence = [[float(value) for value in frame] for frame in frames]
    for frame_index in range(len(sequence) + DRAIN_FLUSH_FRAMES):
        if frame_index < len(sequence):
            frame = sequence[frame_index]
        else:
            frame = [0.0] * FEATURE_BINS
        frame_output, state = surrogate_frame(frame, state, frame_index)
        output.extend(frame_output)
    source_samples = len(sequence) * FEATURE_HOP_SAMPLES
    return output[STARTUP_INVALID_SAMPLES:STARTUP_INVALID_SAMPLES + source_samples]


def surrogate_split_halves(frames: Sequence[Sequence[float]]) -> List[float]:
    midpoint = len(frames) // 2
    return surrogate_stream(frames[:midpoint]) + surrogate_stream(frames[midpoint:])


def output_digest(samples: Sequence[float]) -> str:
    packed = struct.pack("<" + "f" * len(samples), *samples)
    return sha256(packed)


def feature_digest(frames: Sequence[Sequence[float]]) -> str:
    packed = struct.pack(
        "<" + "f" * (len(frames) * FEATURE_BINS),
        *(value for frame in frames for value in frame),
    )
    return sha256(packed)


def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    total = 0.0
    for value in values:
        total += value * value
    return math.sqrt(total / len(values))


def _snr_db(target: Sequence[float], observed: Sequence[float]) -> float | None:
    signal = 0.0
    error = 0.0
    for want, got in zip(target, observed):
        signal += want * want
        diff = got - want
        error += diff * diff
    if signal <= 0.0 or error <= 0.0:
        return None
    return 10.0 * math.log10(signal / error)


def _si_sdr_db(target: Sequence[float], observed: Sequence[float]) -> float | None:
    projection = 0.0
    energy = 0.0
    for want, got in zip(target, observed):
        projection += got * want
        energy += got * got
    if energy <= 0.0:
        return None
    scale = projection / energy
    signal = 0.0
    error = 0.0
    for want, got in zip(target, observed):
        fitted = scale * got
        signal += fitted * fitted
        diff = want - fitted
        error += diff * diff
    if signal <= 0.0 or error <= 0.0:
        return None
    return 10.0 * math.log10(signal / error)


def measure(
    target: Sequence[float], observed: Sequence[float], output: Sequence[float]
) -> Dict[str, Any]:
    nonfinite = sum(0 if math.isfinite(value) else 1 for value in output)
    clipped = sum(1 for value in output if abs(value) > 1.0)
    peak = max((abs(value) for value in output), default=0.0)
    noisy_snr = _snr_db(target, observed)
    surrogate_snr = _snr_db(target, output)
    noisy_si_sdr = _si_sdr_db(target, observed)
    surrogate_si_sdr = _si_sdr_db(target, output)
    return {
        "input_samples": len(observed),
        "output_samples": len(output),
        "output_sha256": output_digest(output),
        "peak_abs": r6(peak),
        "nonfinite_count": nonfinite,
        "clipped_count": clipped,
        "target_rms": r6(_rms(target)),
        "observed_rms": r6(_rms(observed)),
        "output_rms": r6(_rms(output)),
        "noisy_snr_db": r6(noisy_snr),
        "surrogate_snr_db": r6(surrogate_snr),
        "delta_snr_db": r6(surrogate_snr - noisy_snr)
        if surrogate_snr is not None and noisy_snr is not None
        else None,
        "noisy_si_sdr_db": r6(noisy_si_sdr),
        "surrogate_si_sdr_db": r6(surrogate_si_sdr),
        "delta_si_sdr_db": r6(surrogate_si_sdr - noisy_si_sdr)
        if surrogate_si_sdr is not None and noisy_si_sdr is not None
        else None,
    }


# ---------------------------------------------------------------------------
# Caller-supplied external asset boundary and admission
# ---------------------------------------------------------------------------


def _probe_present(relative: str, root: Path | None = None) -> bool:
    base = SOURCE_ROOT if root is None else root
    return (base / relative).exists()


def workspace_copies() -> List[Dict[str, Any]]:
    copies: List[Dict[str, Any]] = []
    for item in OBSERVED_COPIES:
        copies.append(
            {
                "project": item["project"],
                "path": item["path"],
                "revision": item["revision"],
                "variant": item["variant"],
                "license": item["license"],
                "generator_path": item["generator_path"],
                "generator_sha256": item["generator_sha256"],
                "license_path": item["license_path"],
                "license_sha256": item["license_sha256"],
                "weights_present": item["weights_present"],
                "exact_upstream": item["exact_upstream"],
                "present": (SOURCE_ROOT / item["path"]).is_dir(),
                "admitted": item["admitted"],
                "note": item["note"],
            }
        )
    return copies


def asset_ref() -> Dict[str, Any]:
    return {
        "asset_id": ASSET_ID,
        "checkpoint_id": ASSET_CHECKPOINT_ID,
        "path_relative": ASSET_LEDGER_PATH,
        "byte_count": ASSET_BYTES,
        "sha256": ASSET_SHA256,
        "pinned": False,
        "ledger_entry_present": False,
        "rights_entry_present": False,
        "storage": "external",
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "candidate_release_tags": list(CANDIDATE_RELEASE_TAGS),
        "code_license_metadata": CODE_LICENSE_METADATA,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "observed_model_terms": MODEL_TERMS_METADATA,
        "evaluation_allowed": False,
        "acquisition_cleared": False,
        "redistribution_cleared": False,
        "customer_deployment_cleared": False,
        "public_playback_cleared": False,
        "consent_scope": CONSENT_SCOPE,
        "target_condition": TARGET_CONDITION,
        "voice_task_fit": VOICE_TASK_FIT,
        "bytes_present_in_sdk_worktree": (SDK_ROOT / ASSET_LEDGER_PATH).is_file(),
        "workspace_probes": {
            relative: _probe_present(relative) for relative in FIXED_ASSET_PROBES
        },
        "home_probes": {
            relative: _probe_present(relative, Path.home())
            for relative in HOME_ASSET_PROBES
        },
        "workspace_copies": workspace_copies(),
        "asset_bytes_read": False,
        "digest_recomputed": False,
        "runtime_package": RUNTIME_PACKAGE,
        "runtime_target": RUNTIME_TARGET,
        "runtime_wheel_sha256": RUNTIME_WHEEL_SHA256,
        "runtime_lock": RUNTIME_LOCK,
        "runtime_available": False,
        "download_permitted": False,
    }


def asset_admission(ref: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ref = dict(ref or asset_ref())
    reasons: List[str] = []
    if not ref.get("pinned") or not ref.get("source_revision"):
        reasons.append("source_and_identity_unpinned")
    if not ref.get("bytes_present_in_sdk_worktree"):
        reasons.append("weights_not_supplied")
    if not ref.get("runtime_available"):
        reasons.append("runtime_unpinned")
    if not ref.get("model_license_metadata") or "not recorded" in str(
        ref.get("model_license_metadata")
    ):
        reasons.append("license_terms_unresolved")
    if ref.get("consent_scope") != "recorded":
        reasons.append("consent_not_recorded")
    if "no_checkpoint" in str(ref.get("voice_task_fit", "")):
        reasons.append("voice_task_fit_vocoder_only_no_checkpoint")
    if not ref.get("redistribution_cleared"):
        reasons.append("redistribution_rights_unknown")
    order = [
        "source_and_identity_unpinned",
        "weights_not_supplied",
        "runtime_unpinned",
        "license_terms_unresolved",
        "consent_not_recorded",
        "voice_task_fit_vocoder_only_no_checkpoint",
        "redistribution_rights_unknown",
    ]
    reasons = [reason for reason in order if reason in reasons]
    return {
        "status": "admitted" if not reasons else "blocked",
        "reason_codes": reasons,
        "asset_bytes_read": False,
        "asset_bytes_hashed": False,
        "download_attempted": False,
        "model_runtime_invoked": False,
        "vocoder_invoked": False,
        "candidate_asset": True,
        "qualification_effect": "none",
    }


def synthetic_asset_ref() -> Dict[str, Any]:
    return {
        "asset_id": SYNTHETIC_ASSET_ID,
        "byte_count": len(SYNTHETIC_ASSET_BYTES),
        "sha256": SYNTHETIC_ASSET_SHA256,
        "storage": "external",
        "synthetic": True,
        "candidate_asset": False,
        "model_revision": "synthetic-control-v1",
        "bytes_present_in_worktree": True,
        "asset_bytes_read": False,
        "runtime_available": False,
        "rights_cleared": True,
        "download_permitted": False,
    }


def synthetic_admission_control() -> Dict[str, Any]:
    return {
        "status": "admitted_synthetic_control",
        "reason_codes": [],
        "asset_bytes_read": False,
        "download_attempted": False,
        "model_runtime_invoked": False,
        "vocoder_invoked": False,
        "candidate_asset": False,
        "qualification_effect": "none",
        "asset_id": SYNTHETIC_ASSET_ID,
        "byte_count": len(SYNTHETIC_ASSET_BYTES),
        "sha256": SYNTHETIC_ASSET_SHA256,
        "note": (
            "Explicitly synthetic admission control; not MS-iSTFT-Generator and not "
            "eligible for any gate."
        ),
    }


def absence_audit() -> Dict[str, Any]:
    probes = asset_ref()
    workspace_values = list(probes["workspace_probes"].values())
    home_values = list(probes["home_probes"].values())
    return {
        "probe_count": len(workspace_values) + len(home_values),
        "probes": [
            {"path": path, "present": present}
            for path, present in sorted(
                list(probes["workspace_probes"].items())
                + list(probes["home_probes"].items())
            )
        ],
        "all_absence_probes_absent": not any(workspace_values + home_values),
        "source_checkout_present": any(
            probes["workspace_probes"].get(path, False)
            for path in FIXED_ASSET_PROBES
            if "/checkouts/" in path
        ),
        "weights_present": any(
            probes["workspace_probes"].get(path, False)
            for path in FIXED_ASSET_PROBES
            if "/models/" in path
        ),
        "runtime_present": probes["workspace_probes"].get(
            "data/envs/ms-istft-generator", False
        ),
        "runtime_lock_present": probes["workspace_probes"].get(
            "data/envs/ms-istft-generator/requirements.lock", False
        ),
        "license_record_present": probes["workspace_probes"].get(
            "data/rights/ms-istft-generator-license.json", False
        ),
        "model_license_record_present": probes["workspace_probes"].get(
            "data/rights/ms-istft-generator-model-license.json", False
        ),
        "rights_record_present": probes["workspace_probes"].get(
            "data/rights/ms-istft-generator-rights.json", False
        ),
        "cohort_manifest_present": probes["workspace_probes"].get(
            "data/runs/ms-istft-generator-cohort/manifest.json", False
        ),
        "parity_manifest_present": probes["workspace_probes"].get(
            "data/runs/ms-istft-generator-parity/manifest.json", False
        ),
        "download_performed": False,
        "network_used": False,
    }


# ---------------------------------------------------------------------------
# Configuration and streaming mechanics
# ---------------------------------------------------------------------------


def default_config() -> Dict[str, Any]:
    return {
        "model_id": "ms_istft_unpinned_voice_candidate",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "feature_bins": FEATURE_BINS,
        "feature_hop_samples": FEATURE_HOP_SAMPLES,
        "lookahead_frames": SURROGATE_LOOKAHEAD_FRAMES,
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "state_layout": [list(shape) for shape in STATE_LAYOUT],
        "target_condition": TARGET_CONDITION,
        "consent_scope": CONSENT_SCOPE,
        "asset_mode": "caller_supplied_external",
        "asset_id": ASSET_ID,
        "asset_byte_count": ASSET_BYTES,
        "asset_sha256": ASSET_SHA256,
        "surrogate_opt_in": False,
    }


def synthetic_config() -> Dict[str, Any]:
    config = default_config()
    config.update(
        {
            "asset_mode": "synthetic_surrogate",
            "asset_id": SYNTHETIC_ASSET_ID,
            "asset_byte_count": len(SYNTHETIC_ASSET_BYTES),
            "asset_sha256": SYNTHETIC_ASSET_SHA256,
            "surrogate_opt_in": True,
        }
    )
    return config


CONFIG_KEYS = tuple(default_config().keys())


def validate_config(config: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    if not isinstance(config, dict):
        return ["config_type_invalid"]
    if set(config) != set(CONFIG_KEYS):
        reasons.append("config_keys_mismatch")
        return reasons
    if config["model_id"] != "ms_istft_unpinned_voice_candidate":
        reasons.append("model_id_mismatch")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        reasons.append("sample_rate_hz_mismatch")
    if config["channels"] != CHANNELS:
        reasons.append("channels_mismatch")
    if config["sample_format"] != SAMPLE_FORMAT:
        reasons.append("sample_format_mismatch")
    if config["feature_bins"] != FEATURE_BINS:
        reasons.append("feature_bins_mismatch")
    if config["feature_hop_samples"] != FEATURE_HOP_SAMPLES:
        reasons.append("feature_hop_mismatch")
    if config["lookahead_frames"] != SURROGATE_LOOKAHEAD_FRAMES:
        reasons.append("lookahead_frames_mismatch")
    if config["buffering_delay_samples"] != BUFFERING_DELAY_SAMPLES:
        reasons.append("buffering_delay_mismatch")
    if config["state_layout"] != [list(shape) for shape in STATE_LAYOUT]:
        reasons.append("state_layout_mismatch")
    if config["target_condition"] != TARGET_CONDITION:
        reasons.append("target_condition_mismatch")
    if config["consent_scope"] != CONSENT_SCOPE:
        reasons.append("consent_scope_mismatch")
    if config["asset_mode"] not in (
        "caller_supplied_external",
        "synthetic_surrogate",
    ):
        reasons.append("asset_mode_unsupported")
    return reasons


def admit_config(config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if config is None:
        config = default_config()
    if not isinstance(config, dict):
        return {
            "status": "rejected",
            "reason_codes": ["config_type_invalid"],
            "candidate_asset": False,
            "processing_attempted": False,
        }
    config = dict(config)
    reasons = validate_config(config)
    if reasons:
        return {
            "status": "rejected",
            "reason_codes": reasons,
            "candidate_asset": False,
            "processing_attempted": False,
        }
    if config["asset_mode"] == "synthetic_surrogate":
        if config["surrogate_opt_in"] is not True:
            return {
                "status": "rejected",
                "reason_codes": ["surrogate_opt_in_required"],
                "candidate_asset": False,
                "processing_attempted": False,
            }
        expected = synthetic_asset_ref()
        if (
            config["asset_id"] != expected["asset_id"]
            or config["asset_byte_count"] != expected["byte_count"]
            or config["asset_sha256"] != expected["sha256"]
        ):
            return {
                "status": "rejected",
                "reason_codes": ["synthetic_asset_mismatch"],
                "candidate_asset": False,
                "processing_attempted": False,
            }
        admission = synthetic_admission_control()
        admission["processing_attempted"] = False
        return admission
    expected = asset_ref()
    if (
        config["asset_id"] != expected["asset_id"]
        or config["asset_byte_count"] != expected["byte_count"]
        or config["asset_sha256"] != expected["sha256"]
    ):
        return {
            "status": "rejected",
            "reason_codes": ["asset_identity_mismatch"],
            "candidate_asset": True,
            "processing_attempted": False,
        }
    blocked = asset_admission(expected)
    return {
        "status": "rejected",
        "reason_codes": ["asset_not_admitted"],
        "admission": blocked,
        "candidate_asset": True,
        "processing_attempted": False,
    }


def _reject(status: str, **extra: Any) -> Dict[str, Any]:
    payload = {
        "status": "rejected:" + status,
        "output": None,
        "output_samples": 0,
        "candidate": False,
        "qualifies": False,
    }
    payload.update(extra)
    return payload


def _feature_error(frame: Any) -> str | None:
    if isinstance(frame, str) or not isinstance(frame, (list, tuple)):
        return "frame_type_invalid"
    if len(frame) != FEATURE_BINS:
        return "frame_shape_invalid"
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float))
        for value in frame
    ):
        return "feature_type_invalid"
    if any(not math.isfinite(float(value)) for value in frame):
        return "feature_nonfinite"
    if any(float(value) < 0.0 or float(value) > MAX_ABS_FEATURE for value in frame):
        return "feature_out_of_range"
    return None


def _frames_error(frames: Any) -> str | None:
    if isinstance(frames, str) or not isinstance(frames, (list, tuple)):
        return "stream_type_invalid"
    if len(frames) == 0:
        return "stream_empty"
    if len(frames) > MAX_FEATURE_FRAMES_PER_STREAM:
        return "stream_oversized"
    for frame in frames:
        reason = _feature_error(frame)
        if reason is not None:
            return reason
    return None


class StreamingSession:
    """One bounded synthetic feature stream per session; reset to reuse."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = dict(config if config is not None else default_config())
        self.admission = admit_config(self.config)
        self.created = self.admission["status"].startswith("admitted")
        self.closed = False
        self.stream_complete = False
        self.frames = 0
        self.epoch = 0
        self.state = zero_state()
        self.output: List[float] | None = None

    def state_view(self) -> Dict[str, Any]:
        return {
            "created": self.created,
            "closed": self.closed,
            "stream_complete": self.stream_complete,
            "frames": self.frames,
            "epoch": self.epoch,
            "admission_status": self.admission["status"],
            "asset_mode": self.config.get("asset_mode"),
            "state_sha256": sha256(canonical_bytes(self.state)),
            "output_sha256": output_digest(self.output)
            if self.output is not None
            else None,
        }

    def state_digest(self) -> str:
        return sha256(canonical_bytes(self.state_view()))

    def reset(self) -> Dict[str, Any]:
        if self.closed:
            return _reject("session_closed", state_unchanged=True)
        before = self.state_digest()
        self.state = zero_state()
        self.stream_complete = False
        self.output = None
        self.frames = 0
        self.epoch += 1
        return {
            "status": "ok_reset",
            "epoch": self.epoch,
            "state_zeroed": all(
                all(float(item) == 0.0 for item in _flatten(self.state[name]))
                for name in STATE_NAMES
            ),
            "state_unchanged": self.state_digest() == before,
        }

    def process_frame(self, frame: Any, state: Any = None) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed", state_unchanged=True)
        elif not self.created:
            result = _reject(
                "not_admitted",
                reason_codes=self.admission.get("reason_codes", []),
                state_unchanged=True,
            )
        elif self.stream_complete:
            result = _reject("stream_already_complete", state_unchanged=True)
        else:
            reason = _feature_error(frame)
            if reason is not None:
                result = _reject(reason, state_unchanged=True)
            else:
                selected = self.state if state is None else state
                reason = validate_state(selected)
                if reason is not None:
                    result = _reject(reason, state_unchanged=True)
                else:
                    values = [float(value) for value in frame]
                    output, new_state = surrogate_frame(
                        values, selected, self.frames
                    )
                    self.state = new_state
                    self.frames += 1
                    result = {
                        "status": "ok_synthetic",
                        "output": list(output),
                        "output_samples": len(output),
                        "source_first_sample": (self.frames - 1)
                        * FEATURE_HOP_SAMPLES
                        - BUFFERING_DELAY_SAMPLES,
                        "candidate": False,
                        "qualifies": False,
                    }
        result["state_unchanged"] = self.state_digest() == before
        return result

    def process_frames(self, frames: Any) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed", state_unchanged=True)
        elif not self.created:
            result = _reject(
                "not_admitted",
                reason_codes=self.admission.get("reason_codes", []),
                state_unchanged=True,
            )
        elif self.stream_complete:
            result = _reject("stream_already_complete", state_unchanged=True)
        else:
            reason = _frames_error(frames)
            if reason is not None:
                result = _reject(reason, state_unchanged=True)
            else:
                sequence = [[float(value) for value in frame] for frame in frames]
                self.output = surrogate_stream(sequence)
                self.stream_complete = True
                self.frames = len(sequence)
                result = {
                    "status": "ok_synthetic",
                    "output": list(self.output),
                    "input_frames": len(sequence),
                    "input_samples": len(sequence) * FEATURE_HOP_SAMPLES,
                    "output_samples": len(self.output),
                    "output_digest": output_digest(self.output),
                    "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
                    "drain_flush_frames": DRAIN_FLUSH_FRAMES,
                    "candidate": False,
                    "qualifies": False,
                }
        result["state_unchanged"] = self.state_digest() == before
        return result

    def close(self) -> None:
        self.closed = True


def config_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, mutate) -> None:
        config = default_config()
        mutate(config)
        result = admit_config(config)
        cases[name] = {
            "status": result["status"],
            "reason_codes": list(result["reason_codes"]),
            "processing_attempted": bool(result.get("processing_attempted", False)),
            "candidate_asset": bool(result.get("candidate_asset", False)),
        }

    run("wrong_model_id", lambda c: c.update(model_id="hifigan_unpinned"))
    run("wrong_sample_rate", lambda c: c.update(sample_rate_hz=24_000))
    run("wrong_channels", lambda c: c.update(channels=2))
    run("wrong_sample_format", lambda c: c.update(sample_format="s16"))
    run("wrong_feature_bins", lambda c: c.update(feature_bins=64))
    run("wrong_feature_hop", lambda c: c.update(feature_hop_samples=256))
    run("wrong_lookahead", lambda c: c.update(lookahead_frames=0))
    run("wrong_buffering_delay", lambda c: c.update(buffering_delay_samples=0))
    run("wrong_state_layout", lambda c: c.update(state_layout=[[1, 80]]))
    run("wrong_target_condition", lambda c: c.update(target_condition="british_english"))
    run("wrong_consent_scope", lambda c: c.update(consent_scope="recorded"))
    run("caller_asset_unavailable", lambda c: None)
    run(
        "surrogate_without_opt_in",
        lambda c: c.update(
            asset_mode="synthetic_surrogate",
            asset_id=SYNTHETIC_ASSET_ID,
            asset_byte_count=len(SYNTHETIC_ASSET_BYTES),
            asset_sha256=SYNTHETIC_ASSET_SHA256,
            surrogate_opt_in=False,
        ),
    )
    run("wrong_asset_identity", lambda c: c.update(asset_sha256="0" * 64))
    run("wrong_asset_bytes", lambda c: c.update(asset_byte_count=1))

    control = synthetic_config()
    result = admit_config(control)
    cases["synthetic_admission_control"] = {
        "status": result["status"],
        "reason_codes": list(result["reason_codes"]),
        "processing_attempted": bool(result.get("processing_attempted", False)),
        "candidate_asset": bool(result.get("candidate_asset", True)),
        "note": (
            "Explicitly synthetic control branch; not MS-iSTFT-Generator and not a "
            "qualification result."
        ),
    }
    return cases


def stream_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, frames: Any, fresh: bool = True, after_close: bool = False) -> None:
        session = StreamingSession(synthetic_config())
        if not fresh:
            first = session.process_frames([[0.01] * FEATURE_BINS])
            if first["status"] != "ok_synthetic":
                raise RuntimeError("control stream failed: " + first["status"])
        if after_close:
            session.close()
        before = session.state_digest()
        result = session.process_frames(frames)
        cases[name] = {
            "status": result["status"],
            "state_unchanged": session.state_digest() == before,
            "output_samples": result.get("output_samples", 0),
        }

    run("empty_stream", [])
    run(
        "oversized_stream",
        [[0.01] * FEATURE_BINS] * (MAX_FEATURE_FRAMES_PER_STREAM + 1),
    )
    run("wrong_frame_shape", [[0.01] * (FEATURE_BINS - 1)])
    run("nonfinite_frame", [[0.01] * (FEATURE_BINS - 1) + [float("nan")]])
    run("infinite_frame", [[0.01] * (FEATURE_BINS - 1) + [float("inf")]])
    run("string_stream", "not-a-stream")
    run("boolean_feature", [[True] + [0.0] * (FEATURE_BINS - 1)])
    run("negative_feature", [[-0.01] + [0.0] * (FEATURE_BINS - 1)])
    run(
        "out_of_range_feature",
        [[MAX_ABS_FEATURE + 0.5] + [0.0] * (FEATURE_BINS - 1)],
    )
    run("second_stream", [[0.01] * FEATURE_BINS], fresh=False)
    run("after_close", [[0.01] * FEATURE_BINS], after_close=True)
    return cases


def frame_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, frame: Any, state: Any = None) -> None:
        session = StreamingSession(synthetic_config())
        before = session.state_digest()
        before_state = session.state_view()["state_sha256"]
        result = session.process_frame(frame, state)
        cases[name] = {
            "status": result["status"],
            "state_unchanged": session.state_digest() == before,
            "state_payload_unchanged": session.state_view()["state_sha256"]
            == before_state,
            "output_samples": result.get("output_samples", 0),
        }

    run("wrong_frame_length", [0.0] * (FEATURE_BINS - 1))
    run("wrong_frame_type", "frame")
    run("nonfinite_frame", [0.0] * (FEATURE_BINS - 1) + [float("nan")])
    run(
        "out_of_range_frame",
        [0.0] * (FEATURE_BINS - 1) + [MAX_ABS_FEATURE + 0.5],
    )
    run("wrong_state_set", [0.0] * FEATURE_BINS, {"feature_delay": [[0.0] * 80]})
    bad_shape = zero_state()
    bad_shape["feature_delay"] = [[0.0] * 80]
    run("wrong_state_shape", [0.0] * FEATURE_BINS, bad_shape)
    bad_state = zero_state()
    bad_state["feature_delay"][0][0] = float("nan")
    run("nonfinite_state", [0.0] * FEATURE_BINS, bad_state)
    bad_type = zero_state()
    bad_type["feature_delay"][0][0] = True
    run("boolean_state", [0.0] * FEATURE_BINS, bad_type)
    return cases


def streaming_semantics() -> Dict[str, Any]:
    target, observed, frames = synth("active_speech")
    whole = surrogate_stream(frames)
    chunk_loop = surrogate_chunk_loop_control(frames)
    split = surrogate_split_halves(frames)
    split_changed = sum(1 for left, right in zip(whole, split) if left != right)

    prefix_frames = 96
    prefix = surrogate_stream(frames[:prefix_frames])
    prefix_stable = prefix == whole[: prefix_frames * FEATURE_HOP_SAMPLES]

    partial_frames = frames[:7]
    partial_output = surrogate_stream(partial_frames)

    impulse = [[0.0] * FEATURE_BINS for _ in range(40)]
    impulse[8] = [0.5] * FEATURE_BINS
    impulse_output = surrogate_stream(impulse)
    first_nonzero = next(
        (index for index, value in enumerate(impulse_output) if value != 0.0),
        None,
    )
    expected_first = 8 * FEATURE_HOP_SAMPLES

    session = StreamingSession(synthetic_config())
    first = session.process_frames(frames)
    second = session.process_frames(frames)
    after_stream_frame = session.process_frame([0.01] * FEATURE_BINS)
    reset = session.reset()
    replay = session.process_frames(frames)
    session.close()
    close_twice = session.closed
    after_close = session.process_frames(frames)

    fresh = StreamingSession(synthetic_config())
    fresh.process_frames(frames)
    reset_identical = fresh.output == first["output"]
    reset_zero = reset["state_zeroed"]

    return {
        "one_stream_per_session": first["status"] == "ok_synthetic"
        and second["status"] == "rejected:stream_already_complete",
        "second_stream_rejected": second["status"],
        "frame_after_stream_rejected": after_stream_frame["status"],
        "replay_bit_identical": reset_identical,
        "reset_state_zeroed": reset_zero,
        "reset_epoch": reset["epoch"],
        "close_idempotent": close_twice,
        "process_after_close": after_close["status"],
        "chunk_loop_equals_stream": chunk_loop == whole,
        "split_halves_differ": split_changed > 0,
        "split_halves_changed_samples": split_changed,
        "prefix_stable": prefix_stable,
        "prefix_samples": prefix_frames * FEATURE_HOP_SAMPLES,
        "partial_frames_input": len(partial_frames),
        "partial_tail_input_samples": len(partial_frames) * FEATURE_HOP_SAMPLES,
        "partial_tail_output_samples": len(partial_output),
        "partial_tail_digest": output_digest(partial_output),
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
        "drain_flush_frames": DRAIN_FLUSH_FRAMES,
        "drain_calls": DRAIN_FLUSH_FRAMES,
        "drain_produced_samples": DRAIN_FLUSH_FRAMES * FEATURE_HOP_SAMPLES,
        "max_drain_calls": MAX_DRAIN_CALLS,
        "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
        "drain_within_bounds": DRAIN_FLUSH_FRAMES <= MAX_DRAIN_CALLS
        and DRAIN_FLUSH_FRAMES * FEATURE_HOP_SAMPLES
        <= MAX_DRAIN_PRODUCED_SAMPLES,
        "impulse_frame_index": 8,
        "impulse_output_first_nonzero_sample": first_nonzero,
        "impulse_expected_first_nonzero_sample": expected_first,
        "impulse_delay_preserved": first_nonzero == expected_first,
        "cross_stream_state_carried": False,
        "availability_clock": CLOCK_ID,
        "device_clock_measured": False,
        "v0_frame_adapter_implemented": False,
        "v0_frame_samples": V0_FRAME_SAMPLES,
        "surrogate_feature_hop_samples": FEATURE_HOP_SAMPLES,
        "candidate_geometry_known": False,
    }


def synthetic_results() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for condition in CONDITIONS:
        target, observed, frames = synth(condition)
        stream_output = surrogate_stream(frames)
        entry: Dict[str, Any] = {
            "identity_passthrough": measure(target, observed, target),
            "noisy_control": measure(target, observed, observed),
            "surrogate_stream": measure(target, observed, stream_output),
            "surrogate_chunk_loop_control": measure(
                target, observed, surrogate_chunk_loop_control(frames)
            ),
            "surrogate_split_halves": measure(
                target, observed, surrogate_split_halves(frames)
            ),
            "feature_digest": feature_digest(frames),
            "frame_count": len(frames),
        }
        entry["identity_exact"] = entry["identity_passthrough"][
            "output_sha256"
        ] == output_digest(target)
        entry["chunk_loop_matches_stream"] = entry[
            "surrogate_chunk_loop_control"
        ]["output_sha256"] == entry["surrogate_stream"]["output_sha256"]
        entry["split_halves_differs"] = entry["surrogate_split_halves"][
            "output_sha256"
        ] != entry["surrogate_stream"]["output_sha256"]
        entry["target_all_zero"] = all(value == 0.0 for value in target)
        results[condition] = entry
    return results


def regressions(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for condition in CONDITIONS:
        stream = results[condition]["surrogate_stream"]
        for metric in ("delta_snr_db", "delta_si_sdr_db"):
            value = stream[metric]
            if value is not None and value < 0.0:
                rows.append(
                    {
                        "condition": condition,
                        "metric": metric,
                        "value_db": value,
                        "interpretation": (
                            "Synthetic surrogate regression versus the noisy/direct "
                            "control; property of the fixture, not evidence about "
                            "MS-iSTFT-Generator and not a tuned threshold."
                        ),
                    }
                )
    return rows


def voice_profile(results: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "profile_source": "plan/swarm/VERIFICATION.md#Voice",
        "candidate_result_present": False,
        "synthetic_only": True,
        "task_fit": VOICE_TASK_FIT,
        "task_fit_source": f"plan/INVENTORY.json#components[id={INVENTORY_RECORD_ID}]",
        "consent": "not_recorded",
        "permitted_reference_input": "absent",
        "target_condition": TARGET_CONDITION,
        "language_speaker_groups": "not_defined",
        "semantic_preservation": "blocked_unmeasured",
        "speaker_identity_similarity": "blocked_unmeasured",
        "naturalness": "blocked_unmeasured",
        "alignment": "not_measured_no_candidate_output",
        "first_output_tail_timing": "blocked_unmeasured",
        "listening": "not_run",
        "output_use": "blocked",
        "real_runtime": False,
        "paired_synthetic_metrics": ["snr_db", "si_sdr_db"],
        "conditions": list(CONDITIONS),
        "note": (
            "The table describes only the synthetic feature-frame boundary "
            "surrogate. No candidate output, permitted voice reference, consent, "
            "scorer, listening result or target condition exists. Signal metrics are "
            "not semantic, identity or naturalness evidence, and a vocoder is not an "
            "accent conversion."
        ),
        "synthetic_conditions_with_results": sum(
            1
            for condition in CONDITIONS
            if results[condition]["target_all_zero"] is False
        ),
    }


def reference_interface() -> Dict[str, Any]:
    return {
        "source": (
            "none: no pinned MS-iSTFT-Generator source checkout, repository revision, "
            "LICENSE digest, graph or configuration exists"
        ),
        "inspection_only": True,
        "model_bytes_read": False,
        "model_id": "ms_istft_unpinned_voice_candidate",
        "candidate_geometry_known": False,
        "candidate_sample_rate_hz": None,
        "candidate_feature_bins": None,
        "candidate_hop_samples": None,
        "candidate_window": None,
        "candidate_feature_contract": None,
        "candidate_upsample_layout": None,
        "candidate_lookahead_frames": None,
        "candidate_istft_n_fft": None,
        "candidate_istft_hop_samples": None,
        "candidate_subband_count": None,
        "candidate_state_layout": None,
        "surrogate_fixture": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "feature_bins": FEATURE_BINS,
            "feature_hop_samples": FEATURE_HOP_SAMPLES,
            "lookahead_frames": SURROGATE_LOOKAHEAD_FRAMES,
            "state_names": list(STATE_NAMES),
            "state_layout": [list(shape) for shape in STATE_LAYOUT],
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        },
        "timing": {
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
            "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
            "drain_flush_frames": DRAIN_FLUSH_FRAMES,
            "max_drain_calls": MAX_DRAIN_CALLS,
            "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
            "measured": False,
        },
        "state": {
            "surrogate_mutable_state_scope": "per_instance",
            "candidate_state": "unknown",
        },
        "note": (
            "No candidate geometry is known or fabricated. The surrogate fixture "
            "uses arbitrary bounded feature-frame values only for deterministic "
            "accounting."
        ),
    }


def native_evidence_status() -> Dict[str, Any]:
    return {
        "candidate_native_reference_present": False,
        "present_in_workspace": False,
        "fixture_trace_pin": None,
        "fixture_trace_sha256": None,
        "trace_is_synthetic_weights": False,
        "model_parity": "not_available",
        "model_quality": "not_assessed",
        "used_for_qualification": False,
        "sibling_native_artifacts_present": False,
        "sibling_scope": (
            "none admitted; merged hifi-gan-vocoder, vocos and micro-hifi-gan evidence "
            "packages are different-model blockers and supply no MS-iSTFT-Generator "
            "artifact"
        ),
        "note": (
            "No MS-iSTFT-Generator native processor, trace or parity vector exists. "
            "Sibling vocoder evidence never transfers."
        ),
    }


def rights_status() -> Dict[str, Any]:
    return {
        "register": "audio-benchmark-platform/audio-pro/docs/rights-register.md",
        "register_detail": "audio-benchmark-platform/audio-pro/inventory/rights-register.json",
        "entry_present": False,
        "review_date": None,
        "reviewer": None,
        "acquisition": "unknown",
        "evaluation": "unknown",
        "redistribution": "unknown",
        "customer_deployment": "unknown",
        "public_playback": "unknown",
        "consent": "not_recorded",
        "speaker_reference_permission": "unknown",
        "output_use": "unknown",
        "evaluation_only": False,
        "weights_must_remain_private": True,
        "packaging_permitted": False,
        "blocked": True,
    }


def feasibility_decision() -> Dict[str, Any]:
    return {
        "inventory_record": INVENTORY_RECORD_ID,
        "inventory_disposition": "sdk-model",
        "inventory_area": "Voice and synthesis",
        "inventory_evidence_status": "considered",
        "research_path": RESEARCH_README_PATH,
        "research_line": RESEARCH_README_LINE,
        "research_status": RESEARCH_STATUS,
        "finding": RESEARCH_FINDING,
        "task_fit": RESEARCH_TASK_FIT,
        "source_revision_pin_available": False,
        "official_source_pinned": False,
        "derived_source_observed": True,
        "derived_source_admitted": False,
        "weights_available": False,
        "runtime_available": False,
        "permitted_scope": "unknown",
        "task_geometry": "unestablished",
        "matched_evidence_present": False,
        "candidate_run_attempted": False,
        "comparison_retained": False,
        "comparison_reproduced": False,
        "proceed_defer": DECISION,
        "decision_reason": (
            "Feasibility fails before implementation: the pinned research record did "
            "not run MS-iSTFT-Generator and identified no compatible "
            "accent-converter acoustic model/checkpoint for an end-to-end local run. "
            "A derived Multistream_iSTFT_Generator module exists in the MIT LLVC "
            "checkout, but it is not the official release, has no weight, model card "
            "or isolated runtime, and is not admitted. Exact source, weights, runtime, "
            "rights, consent, geometry and matched voice evidence are all absent. A "
            "caller-supplied-asset reference or opt-in adapter cannot be built or "
            "verified, so no processor is exposed and the conditional implementation "
            "remains open."
        ),
        "required_for_proceed": [
            "exact source and checkpoint identity with reviewed terms",
            "pinned isolated runtime with recorded artifact digests",
            "rights-cleared paired voice cohort with permitted references and output use",
            "fixed acoustic features and an end-to-end accent-conversion context isolating the vocoder",
            "independent semantic, speaker-identity and naturalness evidence plus permitted listening",
            "measured first-output, drain and resource behaviour on the target runtime",
        ],
    }


def _build_report() -> Dict[str, Any]:
    results = synthetic_results()
    config_cases = config_rejection_matrix()
    stream_cases = stream_rejection_matrix()
    frame_cases = frame_rejection_matrix()
    semantics = streaming_semantics()
    admission = asset_admission()
    identity = task_identity()
    audit = absence_audit()
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "mode": MODE,
        "repository": "audio-sdk",
        "candidate": (
            "MS-iSTFT-Generator multi-stream iSTFT neural vocoder; official source, "
            "weights, runtime, geometry and accent-conversion role unpinned"
        ),
        "verification_profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "candidate_qualified": False,
            "missing_result_may_qualify": False,
            "all_release_gates_blocked": all(
                gate["status"] == "blocked" for gate in GATES
            ),
            "blocked_gate_count": sum(
                1 for gate in GATES if gate["status"] == "blocked"
            ),
            "blocked_gate_ids": [gate["name"] for gate in GATES],
            "release_results_present": False,
            "synthetic_profile_checks_passed": all(
                results[condition]["chunk_loop_matches_stream"]
                for condition in CONDITIONS
            ),
            "real_source_or_runtime_used": False,
            "listening_or_device_timing_claim": False,
            "missing_result_promoted": False,
            "reason": (
                "No pinned source, exact weights, feature contract, runtime, rights "
                "or consent, candidate output or qualification evidence exists; the "
                "pinned research record is a negative, not-run row."
            ),
        },
        "scope": (
            "Task-local synthetic feature-frame boundary fixture only; the "
            "candidate was not run and no claim is made. Feasibility is recorded as "
            "DEFER before opt-in provider intake."
        ),
        "task_identity": identity,
        "board_row": {
            "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "selector": f"tasks[id={TASK}]",
            "whole_file_hashed": False,
            "stable_fields": {
                field: STABLE_TASK_IDENTITY[field]
                for field in PROJECTED_BOARD_FIELDS
            },
            "stable_sha256": stable_row_digest(
                {
                    field: STABLE_TASK_IDENTITY[field]
                    for field in PROJECTED_BOARD_FIELDS
                }
            ),
            "excluded_mutable_fields": list(
                STABLE_TASK_IDENTITY["mutable_fields_excluded"]
            ),
            "note": (
                "Only the stable linked-row projection is gated. The mutable board "
                "file is never hashed or pinned."
            ),
        },
        "format": dict(FORMAT),
        "feasibility": feasibility_decision(),
        "absence_audit": audit,
        "asset_boundary": {
            "kind": "caller-supplied external asset reference",
            "contract": (
                "CONTRACTS.md as_asset_v0: ID, byte count, SHA-256, "
                "storage=external, no provider file access and no download"
            ),
            "asset": asset_ref(),
            "asset_bytes_read": False,
            "asset_bytes_hashed": False,
            "bytes_present_in_sdk_worktree": (
                SDK_ROOT / ASSET_LEDGER_PATH
            ).is_file(),
            "download_attempted": False,
            "model_runtime_invoked": False,
            "runtime_available": False,
        },
        "asset_admission": admission,
        "synthetic_admission_control": synthetic_admission_control(),
        "workspace_observations": {
            "copies": workspace_copies(),
            "observed_copy_count": len(OBSERVED_COPIES),
            "exact_official_source_present": False,
            "admitted_copy_count": 0,
            "note": (
                "One derived Multistream_iSTFT_Generator module is observed in the "
                "LLVC checkout and pinned by file digest, but it is not the official "
                "MS-iSTFT-Generator release, has no weight, and is not admitted to any "
                "gate. No official source checkout is present."
            ),
        },
        "rights": rights_status(),
        "reference_interface": reference_interface(),
        "native_evidence": native_evidence_status(),
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(gate) for gate in GATES],
        "release_gate_count": len(GATES),
        "voice_profile": voice_profile(results),
        "synthetic_results": results,
        "regressions": regressions(results),
        "controls": {
            "identity_control_is_exact": all(
                results[condition]["identity_exact"] for condition in CONDITIONS
            ),
            "chunk_loop_matches_stream": all(
                results[condition]["chunk_loop_matches_stream"]
                for condition in CONDITIONS
            ),
            "split_halves_differs": all(
                results[condition]["split_halves_differs"]
                for condition in CONDITIONS
                if condition != "silence"
            ),
            "variant_count": 5,
            "condition_count": len(CONDITIONS),
            "note": "Controls describe the synthetic boundary surrogate only.",
        },
        "adverse": {
            "config_rejections": config_cases,
            "stream_cases": {
                "cases": stream_cases,
                "state_after_close_unchanged_by_rejected_call": True,
            },
            "frame_cases": {
                "cases": frame_cases,
                "state_validation_before_state_update": True,
            },
            "lifecycle": {
                "one_stream_per_session": semantics["one_stream_per_session"],
                "close_idempotent": semantics["close_idempotent"],
                "second_stream": semantics["second_stream_rejected"],
                "frame_after_stream": semantics["frame_after_stream_rejected"],
                "process_after_close": semantics["process_after_close"],
                "reset_state_zeroed": semantics["reset_state_zeroed"],
            },
            "nonfinite_and_invalid_rejected": all(
                stream_cases[name]["status"].startswith("rejected:")
                for name in (
                    "wrong_frame_shape",
                    "nonfinite_frame",
                    "infinite_frame",
                    "string_stream",
                    "boolean_feature",
                    "negative_feature",
                    "out_of_range_feature",
                )
            ),
            "missing_asset_blocked": admission["status"] == "blocked",
        },
        "state": {
            "deterministic_output_digest": True,
            "deterministic_state_digest": True,
            "chunk_loop_equals_stream": semantics["chunk_loop_equals_stream"],
            "one_stream_per_session": semantics["one_stream_per_session"],
            "close_idempotent": semantics["close_idempotent"],
            "process_after_close": semantics["process_after_close"],
            "partial_tail_preserved": semantics["partial_tail_output_samples"]
            == semantics["partial_tail_input_samples"],
            "impulse_delay_preserved": semantics["impulse_delay_preserved"],
            "prefix_stable": semantics["prefix_stable"],
            "reset_replay_identical": semantics["replay_bit_identical"],
            "reset_state_zeroed": semantics["reset_state_zeroed"],
        },
        "streaming_semantics": semantics,
        "source_reported_context": dict(SOURCE_REPORTED_CONTEXT),
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
        "pins": {
            "source": dict(SOURCE_PINS),
            "boundary": dict(BOUNDARY_PINS),
            "sibling": dict(SIBLING_PINS),
            "local_files": list(LOCAL_FILES),
            "board_full_file_hashed": False,
            "board_file_pinned": False,
        },
        "counts": {
            "conditions": len(CONDITIONS),
            "feature_frames_per_condition": FEATURE_FRAMES,
            "samples_per_condition": SAMPLES,
            "synthetic_observed_samples": len(CONDITIONS) * SAMPLES,
            "surrogate_frames_per_condition": FEATURE_FRAMES,
            "config_adverse_cases": len(config_cases),
            "stream_adverse_cases": len(stream_cases),
            "frame_adverse_cases": len(frame_cases),
            "release_gates": len(GATES),
            "release_gates_blocked": sum(
                1 for gate in GATES if gate["status"] == "blocked"
            ),
        },
        "reproduction": {
            "run": "python3 run.py --all",
            "verify": "python3 verify.py",
            "tests": "python3 -m unittest -v test_reference.py",
            "sources_manifest": "SOURCES.sha256",
            "report_sha256_sidecar": "report.json.sha256",
            "cold_start_regenerations": 3,
        },
    }
    return report


def build_report() -> Dict[str, Any]:
    """Return a deep copy of the memoized deterministic report."""
    global _REPORT_CACHE
    if _REPORT_CACHE is None:
        _REPORT_CACHE = _build_report()
    return copy.deepcopy(_REPORT_CACHE)


def build_contract(artifact_pins: Dict[str, str] | None = None) -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "mode": MODE,
        "repository": "audio-sdk",
        "candidate": (
            "MS-iSTFT-Generator multi-stream iSTFT neural vocoder; official source, "
            "weights, runtime, geometry and accent-conversion role unpinned"
        ),
        "verification_profile": PROFILE,
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "worktree": WORKTREE,
            "reviewer": REVIEWER,
            "mutable_claim_not_hashed": True,
        },
        "task_identity": task_identity(),
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "qualified": False,
        "scope": (
            "Writes are limited to " + TASK_PREFIX + "**; no public API/ABI, "
            "provider, registry, installed default, shared build, dependency lock, "
            "CI, board or handoff change."
        ),
        "format": dict(FORMAT),
        "feasibility": feasibility_decision(),
        "asset": asset_ref(),
        "asset_admission": asset_admission(),
        "synthetic_admission_control": synthetic_admission_control(),
        "workspace_observations": {
            "copies": workspace_copies(),
            "observed_copy_count": len(OBSERVED_COPIES),
            "exact_official_source_present": False,
            "admitted_copy_count": 0,
        },
        "rights": rights_status(),
        "reference_interface": reference_interface(),
        "native_evidence": native_evidence_status(),
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(gate) for gate in GATES],
        "release_gate_count": len(GATES),
        "allowed_now": [
            "synthetic feature-frame accounting tests with explicit opt-in",
            "read-only documentation of the caller-supplied external asset contract and pinned metadata",
        ],
        "not_allowed": [
            "downloading, reading, hashing, loading, executing or bundling any MS-iSTFT-Generator source, checkpoint, graph or derived weight",
            "invoking PyTorch, ONNX Runtime, a vocoder or any model runtime",
            "registering a provider, changing defaults or claiming semantic/identity/naturalness/quality/latency/parity/release",
        ],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
        "local_files": list(LOCAL_FILES),
        "artifact_pins": dict(artifact_pins or {}),
        "board_policy": {
            "selector": f"tasks[id={TASK}]",
            "full_file_hashed": False,
            "mutable_file": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "stable_fields_only": True,
            "mutable_fields_excluded": list(
                STABLE_TASK_IDENTITY["mutable_fields_excluded"]
            ),
        },
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
    }
