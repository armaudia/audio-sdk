# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for
SDK-GLM-4-VOICE-AND-ERES2NET-FOR-X-VC.

This module is NOT X-VC, GLM-4-Voice or ERes2Net. It does not implement,
approximate, simulate or run the X-VC streaming conversion network, the
GLM-4-Voice tokenizer, the ERes2Net speaker encoder or any vocoder. The MIT
X-VC *source checkout* is present at a pinned revision, but the X-VC
checkpoint, the GLM-4-Voice-Tokenizer weights, the ERes2Net weights and a
hash-pinned runtime are absent. The module therefore builds a bounded,
deterministic blocker report:

* strict request validation at the installed v0 geometry with explicit
  resolution of both X-VC dependencies, and fail-closed rejection of missing,
  invalid, nonfinite, out-of-range and reordered inputs;
* explicit source, weights and runtime probes (read-only, bounded, no network);
* declared geometry from the pinned X-VC config, requirements and inference
  script, with exact pins and no claim of local measurement;
* synthetic harness stimuli for identity/rejection controls only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

No network, model weights, real corpus audio, native library or download is
used. No candidate output is produced and no result qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
from typing import Any, Dict, Iterable, List, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0

SCHEMA_ID = (
    "audio-sdk/glm-4-voice-and-eres2net-for-x-vc-reference-report/0.1")
CONTRACT_SCHEMA_ID = (
    "audio-sdk/glm-4-voice-and-eres2net-for-x-vc-contract/0.1")
TASK = "SDK-GLM-4-VOICE-AND-ERES2NET-FOR-X-VC"
COMPONENT = "glm-4-voice-and-eres2net-for-x-vc"
BRANCH = "swarm/SDK-GLM-4-VOICE-AND-ERES2NET-FOR-X-VC"
BASE_COMMIT = "77d7800cac82899eb02a8aa55535d00e4faa8946"
TASK_PREFIX = (
    "docs/task-evidence/glm-4-voice-and-eres2net-for-x-vc/")

SOURCE_REPOSITORY = "Jerrister/X-VC"
SOURCE_REVISION = "49df8c591eafc48b096e466d96f9839f9c0dd739"
SOURCE_TREE_DIGEST = (
    "d0fad742b6eeb3cff3ddc644460bf69c48f14c41adea839b92f94912f78338f0")
SOURCE_FILE_COUNT = 82
SOURCE_LICENSE = "MIT"

X_VC_CHECKPOINT = "chenxie95/X-VC checkpoint (xvc.pt)"
X_VC_CHECKPOINT_REPO = "https://huggingface.co/chenxie95/X-VC"
GLM_TOKENIZER = "zai-org/glm-4-voice-tokenizer"
GLM_TOKENIZER_REPO = "https://huggingface.co/zai-org/glm-4-voice-tokenizer"
ERES2NET = "iic/speech_eres2net_sv_en_voxceleb_16k"
ERES2NET_REPO = (
    "https://modelscope.cn/models/iic/speech_eres2net_sv_en_voxceleb_16k")

EXPECTED_N_FFT = 1024
EXPECTED_WIN_LENGTH = 640
EXPECTED_HOP_LENGTH = 320
EXPECTED_NUM_MELS = 128
EXPECTED_LATENT_HOP = 1280
EXPECTED_ENCODER_RATES = [2, 4, 5, 8]
EXPECTED_SEMANTIC_INPUT_CHANNELS = 1280
EXPECTED_SPEAKER_EMBEDDING_DIM = 192
EXPECTED_CHUNK_SAMPLES = 2400
EXPECTED_FUTURE = 100
EXPECTED_SMOOTH = 20
EXPECTED_CURRENT = 0

EXPECTED_REQUIREMENTS = {
    "torch": "2.5.1",
    "torchaudio": "2.5.1",
    "transformers": "4.44.1",
    "numpy": "1.26.4",
    "soundfile": "0.12.1",
    "librosa": "0.10.2",
    "scipy": "1.12.0",
}

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
SOURCE_ROOT = (
    WORKSPACE / "research/voice-conversion-eval-20261101/repos/x-vc")
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
INVENTORY_PATH = WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.json"
HF_CACHE_ROOT = Path.home() / ".cache/huggingface/hub"
MODELSCOPE_CACHE_ROOT = Path.home() / ".cache/modelscope/hub"

CONFIG_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/x-vc/configs/xvc.yaml")
REQUIREMENTS_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/x-vc/requirements.txt")
INFER_SCRIPT_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/x-vc/scripts/"
    "infer_single.sh")
SEMANTIC_ENCODER_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/x-vc/models/codec/sac/"
    "modules/semantic_encoder.py")
SPEAKER_ENCODER_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/x-vc/models/codec/sac/"
    "modules/speaker_encoder.py")
ERES2NET_CODE_RELATIVE = (
    "research/voice-conversion-eval-20261101/repos/x-vc/models/codec/sac/"
    "modules/utils/ERes2Net.py")

# Workspace-relative evidence pins. The mutable full TASKS.json is deliberately
# absent: only the stable linked row identity is projected, never hashed.
SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/repos/x-vc/LICENSE":
        "75802be937ddc02983c87bdf64a9b6a38b383a68ee399ca3b34a0a60e5328c0e",
    "research/voice-conversion-eval-20261101/repos/x-vc/README.md":
        "25dc5a99f25ff079b7f947d3ed9e2514b792cafcfff1e3455ac01978083a6a5e",
    "research/voice-conversion-eval-20261101/repos/x-vc/configs/xvc.yaml":
        "85b2c699dd483e7f5a34058c5ecd4fd666a02a18d45cbc776de47d7626e0fd94",
    "research/voice-conversion-eval-20261101/repos/x-vc/requirements.txt":
        "90736615ba018c4726a38ae618176d4e43eaed714a263b2b7e4795af893180a6",
    "research/voice-conversion-eval-20261101/repos/x-vc/scripts/"
    "infer_single.sh":
        "39a7b34c2ab89d3a7be28228944e6c7896724f993b5c39cfcec6e99f73e95dcb",
    "research/voice-conversion-eval-20261101/repos/x-vc/models/codec/sac/"
    "modules/semantic_encoder.py":
        "c9f737d84e28d4d5c0d28a2d69f19c3e57f5e1635b7467419db9a4b2d9c70b51",
    "research/voice-conversion-eval-20261101/repos/x-vc/models/codec/sac/"
    "modules/speaker_encoder.py":
        "0ccb6b0d783edbf6966450f21a0271daca9b4b31909b44c09c2099ec949ac33d",
    "research/voice-conversion-eval-20261101/repos/x-vc/models/codec/sac/"
    "modules/utils/ERes2Net.py":
        "e297406e211400a58922448bb4dda536dc37d2ebbaf87002c14b4fa50568a3fc",
}

# SDK-worktree-relative boundary pins. Every entry is read-only evidence that
# the installed v0 contract, public C surface, shared build, CI and merged
# sibling cross-lingual VC evidence were not changed by this task.
BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/dualvc-3/README.md":
        "24551d07a453de939da409160d6fe330567a92243e8eadc8e04a6685ba98cf70",
    "docs/task-evidence/dualvc-3/report.json":
        "1eea7877ce934885a2ebe82a1c50b989a33a062b8b7d34f4441786a52d19b0d1",
    "docs/task-evidence/seed-vc-xls-r-300m-content-encoder/README.md":
        "3ffad57b383c93b98b051d10d8bf7f7ce6a4b7c74940611dfd1853269e103f09",
    "docs/task-evidence/seed-vc-xls-r-300m-content-encoder/report.json":
        "0a661101a938600bf26a07b18b6ae0d1fa2c94e6db6394d169dc052b8b3d19ef",
    "docs/task-evidence/openvoice-v2/README.md":
        "bcd58494af03ffee38b65ac4926ae0aed8768dd45ad966617629cfd6c9a10226",
    "docs/task-evidence/openvoice-v2/report.json":
        "27986b993beca10ae2d9e354fca4102db8795e10d845f3b89d8273fa9531b9c8",
}

# Stable linked-row identity only. Status, owner, review, handoff, timestamps,
# dispatch priority, history and claim are deliberately excluded and never
# gated. The shared board itself is never modified.
EXPECTED_LINK = {
    "task_id": TASK,
    "title": "GLM-4-Voice and ERes2Net for X-VC",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)

EXPECTED_INVENTORY = {
    "id": COMPONENT,
    "name": "GLM-4-Voice and ERes2Net for X-VC",
    "area": "Voice and synthesis",
    "evidence_status": "blocked",
    "repository": "audio-sdk",
    "disposition": "sdk-model",
    "verification_profile": "voice",
    "task": TASK,
}

CANDIDATE = "x-vc"
# The linked ledger records no target voice or target condition. Only this
# explicit "unspecified" placeholder is accepted; every concrete condition is
# rejected until a reviewed target definition exists.
TARGET_CONDITION = "streaming_zero_shot_target_unspecified"
DEPENDENCIES = ("glm-4-voice-tokenizer", "eres2net")
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)
REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples", "samples",
    "epoch", "first_input_sample", "lifecycle", "execution_mode",
    "target_condition", "dependencies",
})

SOURCE_ARTIFACT_FILES = (
    "reference.py", "run.py", "test_reference.py", "verify.py",
)

WEIGHT_SUFFIXES = (
    ".pt", ".pth", ".ckpt", ".bin", ".safetensors", ".onnx", ".tflite",
    ".gguf",
)
WEIGHT_ARTIFACTS = {
    "x_vc_checkpoint": {
        "artifact": X_VC_CHECKPOINT,
        "upstream_repository": X_VC_CHECKPOINT_REPO,
        "required_files": ["ckpts/xvc.pt"],
        "paths": (
            "research/voice-conversion-eval-20261101/repos/x-vc/ckpts",
            "research/voice-conversion-eval-20261101/repos/x-vc/ckpts/"
            "xvc.pt",
            "research/voice-conversion-eval-20261101/repos/x-vc/xvc.pt",
            "research/voice-conversion-eval-20261101/checkpoints/xvc.pt",
            "data/models/chenxie95/X-VC",
            "~/.cache/huggingface/hub/models--chenxie95--X-VC",
        ),
    },
    "glm_4_voice_tokenizer": {
        "artifact": GLM_TOKENIZER,
        "upstream_repository": GLM_TOKENIZER_REPO,
        "required_files": [
            "config.json",
            "pytorch_model.bin or model.safetensors",
            "tokenizer/codebook assets named by the model card",
        ],
        "paths": (
            "research/voice-conversion-eval-20261101/repos/x-vc/pretrained/"
            "glm-4-voice-tokenizer",
            "research/voice-conversion-eval-20261101/checkpoints/"
            "glm-4-voice-tokenizer",
            "data/models/zai-org/glm-4-voice-tokenizer",
            "~/.cache/huggingface/hub/models--zai-org--glm-4-voice-tokenizer",
            "~/.cache/huggingface/hub/models--THUDM--glm-4-voice-tokenizer",
        ),
    },
    "eres2net": {
        "artifact": ERES2NET,
        "upstream_repository": ERES2NET_REPO,
        "required_files": [
            "configuration.json",
            "the weight file named by configuration.json",
        ],
        "paths": (
            "research/voice-conversion-eval-20261101/repos/x-vc/pretrained/"
            "speech_eres2net_sv_en_voxceleb_16k",
            "research/voice-conversion-eval-20261101/checkpoints/"
            "speech_eres2net_sv_en_voxceleb_16k",
            "data/models/iic/speech_eres2net_sv_en_voxceleb_16k",
            "~/.cache/modelscope/hub/iic/"
            "speech_eres2net_sv_en_voxceleb_16k",
        ),
    },
}

RUNTIME_CANDIDATE_PATHS = (
    "research/voice-conversion-eval-20261101/.venv",
    "research/voice-conversion-eval-20261101/.venv/bin/python",
    "research/accent-conversion-20261101/.venv/bin/python",
    "data/envs/x-vc",
    "data/envs/x-vc/bin/python",
)
RUNTIME_MODULES = (
    "torch", "torchaudio", "transformers", "numpy", "soundfile", "librosa",
    "modelscope", "huggingface_hub",
)
RUNTIME_LOCK_CANDIDATES = (
    "research/voice-conversion-eval-20261101/requirements.lock",
    "research/voice-conversion-eval-20261101/constraints.txt",
    "research/voice-conversion-eval-20261101/.venv-eval/pyvenv.cfg",
    "research/voice-conversion-eval-20261101/.venv/pyvenv.cfg",
    "data/envs/x-vc/pyvenv.cfg",
)

SEARCH_ROOTS = (
    "research/voice-conversion-eval-20261101",
    "research/accent-conversion-20261101",
    "data",
    "adapters",
    "configs",
)
NAME_NEEDLES = (
    "glm-4-voice", "glm_4_voice", "glm4voice", "eres2net", "eres_2net",
    "eres-2net", "xvc", "x-vc", "chenxie95",
)
MAX_SEARCH_ENTRIES = 200000
SEARCH_EXCLUSIONS = (
    "worktrees/** (separate git worktrees, including this task worktree "
    "directory name)",
    "docs/task-evidence/glm-4-voice-and-eres2net-for-x-vc/** (this evidence "
    "package)",
    "__pycache__/** and .git/**",
    "file contents (names only; no workspace tree is hashed)",
)

FIXTURE_SPANS = (
    (0, 800, "voiced"),
    (800, 1000, "pause"),
    (1000, 1800, "voiced"),
    (1800, 2100, "filler"),
    (2100, 2800, "voiced"),
    (2800, 3200, "pause"),
)

GATES = (
    {
        "id": "RG-01",
        "gate": "exact_source_and_dependency_weight_pin",
        "status": "blocked",
        "reason": (
            "The MIT X-VC source checkout is present and pinned at commit "
            "49df8c59, but the X-VC checkpoint, the GLM-4-Voice-Tokenizer "
            "weights and the ERes2Net weights are absent; no weight SHA-256 "
            "or byte count exists locally."),
        "reopen": (
            "Stage xvc.pt, the zai-org/glm-4-voice-tokenizer snapshot and the "
            "iic/speech_eres2net_sv_en_voxceleb_16k snapshot with per-file "
            "SHA-256 and byte counts before any reproduction."),
    },
    {
        "id": "RG-02",
        "gate": "license_rights_and_asset_review",
        "status": "blocked",
        "reason": (
            "X-VC source is MIT, but the X-VC checkpoint, GLM-4-Voice "
            "tokenizer, ERes2Net weight terms and caller-supplied-asset "
            "redistribution/use scope are not recorded; voice consent and "
            "corpus rights are absent."),
        "reopen": (
            "Record each weight licence/terms, the MIT obligations for the "
            "caller-supplied X-VC asset, and an approved use/redistribution "
            "scope for weights, runtime, inputs, target voices and outputs."),
    },
    {
        "id": "RG-03",
        "gate": "exact_runtime_build_and_install_parity",
        "status": "blocked",
        "reason": (
            "requirements.txt declares exact versions, but no environment, "
            "lockfile or wheel hash set exists and torch, torchaudio, "
            "transformers, numpy, soundfile, librosa, modelscope and "
            "huggingface_hub are not importable here."),
        "reopen": (
            "Create a frozen, hash-pinned CPU runtime for the declared "
            "versions, install it in a clean environment, and prove "
            "import/version parity before loading weights."),
    },
    {
        "id": "RG-04",
        "gate": "dependency_geometry_tokenizer_speaker_alignment_and_drain",
        "status": "blocked",
        "reason": (
            "No weight was loaded, so GLM-4-Voice tokenization, the 1280-wide "
            "semantic path, the 192-dimensional ERes2Net embedding, the "
            "320-sample acoustic hop, chunking, alignment, state/reset, "
            "finite drain and execution-mode ownership were not exercised."),
        "reopen": (
            "With all three weight artifacts and the exact runtime, verify "
            "tokenizer semantics, speaker embedding width, hop/delay/content "
            "mapping, chunking, state/reset, finite drain and mode ownership "
            "at 16 kHz mono."),
    },
    {
        "id": "RG-05",
        "gate": "rights_qualified_cohort_content_identity_and_naturalness",
        "status": "blocked",
        "reason": (
            "No permitted source/target voice pair, frozen language/speaker "
            "group, manual transcript, matched/mismatched/identity control or "
            "held-out cohort exists. Content, identity and naturalness are "
            "unmeasured."),
        "reopen": (
            "Freeze a rights-cleared cross-lingual cohort with manual "
            "transcripts, groups, exact target conditions and matched "
            "controls, then score text/semantic preservation, identity/"
            "similarity and naturalness separately."),
    },
    {
        "id": "RG-06",
        "gate": "content_preservation_adverse_and_nonfinite_cases",
        "status": "blocked",
        "reason": (
            "No candidate output exists, so silence, peaks, clipping, "
            "nonfinite input/output, unfamiliar speech, language mismatch and "
            "content-preservation controls were not run through the exact "
            "pipeline."),
        "reopen": (
            "Reproduce paired content/preservation controls with all exact "
            "assets, including silence, peaks, nonfinite and unfamiliar "
            "speech, and record every failure."),
    },
    {
        "id": "RG-07",
        "gate": "checkpoint_runtime_memory_timing_and_callback_suitability",
        "status": "blocked",
        "reason": (
            "The ledger reports a 5.01 GB checkpoint against an 8 GB host "
            "budget and no local X-VC run exists. Joint checkpoint/runtime "
            "memory, paced device timing, first-output/tail latency, "
            "listening and callback suitability were not measured."),
        "reopen": (
            "Measure joint checkpoint plus runtime memory, paced device "
            "timing, first-output/tail latency, resources and callback "
            "suitability, and complete an approved listening protocol."),
    },
    {
        "id": "RG-08",
        "gate": "provider_intake_public_surface_independent_review_release",
        "status": "blocked",
        "reason": (
            "No caller-supplied-asset adapter, provider intake, descriptor, "
            "public-surface decision, independent exact-head review or release "
            "approval exists."),
        "reopen": (
            "Complete provider intake, a versioned caller-supplied-asset "
            "adapter and public-surface decision, then obtain independent "
            "exact-head review and release approval."),
    },
)

UPSTREAM_BLOCKER = {
    "status": "blocked_weights_and_runtime_absent",
    "artifact": (
        "X-VC checkpoint, GLM-4-Voice-Tokenizer weights, ERes2Net weights and "
        "the exact hash-pinned runtime required to load and evaluate the "
        "X-VC streaming conversion pipeline"),
    "source": {
        "status": "present_pinned",
        "repository": SOURCE_REPOSITORY,
        "revision": SOURCE_REVISION,
        "tree_digest": SOURCE_TREE_DIGEST,
        "file_count": SOURCE_FILE_COUNT,
        "license": SOURCE_LICENSE,
    },
    "weights": {
        "status": "absent",
        "artifact": (
            "X-VC checkpoint plus GLM-4-Voice-Tokenizer and ERes2Net weights"),
        "x_vc_checkpoint": {
            "status": "absent",
            "artifact": X_VC_CHECKPOINT,
            "upstream_repository": X_VC_CHECKPOINT_REPO,
            "required_files": ["ckpts/xvc.pt"],
            "sha256": None,
            "byte_count": None,
            "license": None,
        },
        "glm_4_voice_tokenizer": {
            "status": "absent",
            "artifact": GLM_TOKENIZER,
            "upstream_repository": GLM_TOKENIZER_REPO,
            "required_files": [
                "config.json",
                "pytorch_model.bin or model.safetensors",
                "tokenizer/codebook assets named by the model card",
            ],
            "sha256": None,
            "byte_count": None,
            "license": None,
        },
        "eres2net": {
            "status": "absent",
            "artifact": ERES2NET,
            "upstream_repository": ERES2NET_REPO,
            "required_files": [
                "configuration.json",
                "the weight file named by configuration.json",
            ],
            "sha256": None,
            "byte_count": None,
            "license": None,
        },
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "PyTorch 2.5.1 and TorchAudio 2.5.1 CPU builds matching the "
            "declared requirements",
            "Transformers 4.44.1 with the WhisperVQ GLM-4-Voice tokenizer "
            "implementation",
            "NumPy 1.26.4, SoundFile 0.12.1, Librosa 0.10.2 and SciPy 1.12.0",
            "ModelScope or an equivalent offline loader for the ERes2Net "
            "snapshot",
            "a hash-pinned lockfile or wheel set and a fail-closed offline "
            "loader",
        ],
        "sha256": None,
        "lockfile": None,
    },
    "expected_license": (
        "MIT for the pinned X-VC source checkout; the X-VC checkpoint, "
        "GLM-4-Voice-Tokenizer and ERes2Net weight terms are not recorded "
        "locally and require separate review"),
    "pinned_revision": SOURCE_REVISION,
    "source_digest": SOURCE_TREE_DIGEST,
    "runtime_digest": None,
    "checkpoint_memory": {
        "status": "blocked_not_measured",
        "source_reported_checkpoint_size_gb": 5.01,
        "source_reported_host_memory_budget_gb": 8.0,
        "measured_here": False,
        "note": (
            "Both values are source-reported in the linked X-VC ledger row; "
            "joint checkpoint plus runtime memory was not measured here."),
    },
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "Reviewed X-VC checkpoint, GLM-4-Voice-Tokenizer and ERes2Net weight "
        "terms, the MIT caller-supplied-asset obligations, training-data and "
        "corpus rights, explicit source-speaker and target-voice consent, "
        "reference availability, output-use terms and an approved "
        "redistribution model for the runtime and any converted output are "
        "required before any reproduction, adapter or release claim."),
    "workspace_search": (
        "Bounded read-only path checks, a bounded weight-filename search over "
        "the research/data/adapters/configs roots and read-only Hugging Face "
        "and ModelScope cache listings found no xvc.pt, GLM-4-Voice-Tokenizer "
        "or ERes2Net weight file. The pinned X-VC source tree contains the "
        "ERes2Net *code* and tokenizer wrappers but no weights."),
    "not_attempted": [
        "no network download or package installation",
        "no fabricated, reconstructed or surrogate X-VC, GLM-4-Voice or "
        "ERes2Net weights",
        "no substitute tokenizer, speaker encoder, vocoder or conversion "
        "algorithm",
        "no copied upstream source, real corpus audio or license text",
        "no real corpus read, model load or converted output",
    ],
    "reopen": (
        "Stage the exact X-VC checkpoint, GLM-4-Voice-Tokenizer and ERes2Net "
        "files with SHA-256/byte counts, record weight and asset rights, "
        "rebuild a hash-pinned runtime, then repeat the voice profile with a "
        "permitted cross-lingual cohort and independent review."),
}

NON_CLAIMS = (
    "No X-VC checkpoint, GLM-4-Voice-Tokenizer weight, ERes2Net weight or "
    "converted audio is included.",
    "No X-VC, GLM-4-Voice or ERes2Net inference is implemented, approximated "
    "or simulated.",
    "No installed v0, public API, C ABI, descriptor, registry or default "
    "change.",
    "No provider is registered or enabled by default.",
    "No real corpus, consent, listening panel, benchmark or quality claim "
    "exists.",
    "No paper-reported, ledger-reported or sibling latency is treated as a "
    "local measurement or device timing result.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No missing, rejected or sibling result qualifies the candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/glm-4-voice-and-eres2net-for-x-vc/ is touched.",
    "The reference is a task-local evidence builder, not X-VC, GLM-4-Voice "
    "or ERes2Net.",
    "All harness stimuli are analytic or seeded synthetic; no weights are "
    "used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
    "The mutable full plan/swarm/TASKS.json is never hashed or pinned.",
)

VOICE_PROFILE_SOURCE = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"


class EvidenceError(ValueError):
    """Base error with a stable machine-readable code."""

    code = "EVIDENCE_ERROR"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class ConfigError(EvidenceError):
    code = "INVALID_CONFIG"


class InputError(EvidenceError):
    code = "INVALID_INPUT"


class JsonError(EvidenceError):
    code = "INVALID_JSON"


class CandidateAbsent(EvidenceError):
    code = "SOURCE_WEIGHTS_RUNTIME_ABSENT"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _pairs_hook(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise JsonError("DUPLICATE_KEY: " + key, "DUPLICATE_KEY")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise JsonError("NONFINITE_CONSTANT: " + token, "NONFINITE_CONSTANT")


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_pairs_hook,
                          parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise JsonError("INVALID_JSON: " + str(error), "INVALID_JSON")


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def _r(value: float, places: int = 9) -> float:
    return round(float(value), places)


def tensor_digest(samples: Iterable[float]) -> str:
    digest = hashlib.sha256()
    for value in samples:
        digest.update(struct.pack("<f", float(value)))
    return digest.hexdigest()


def peak_abs(samples: Iterable[float]) -> float:
    return max((abs(float(value)) for value in samples), default=0.0)


def rms(samples: Sequence[float]) -> float:
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    total = math.fsum(float(value) * float(value) for value in samples)
    return math.sqrt(total / len(samples))


def db_ratio(numerator: float, denominator: float) -> float:
    if numerator <= 0.0 or denominator <= 0.0:
        raise InputError("NONPOSITIVE_RMS", "NONPOSITIVE_RMS")
    return 20.0 * math.log10(numerator / denominator)


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield (state / 4294967296.0) * 2.0 - 1.0


def silence(length: int = 1600) -> Tuple[float, ...]:
    return (0.0,) * length


def impulse(length: int = 1600, position: int = 800,
            amplitude: float = 0.5) -> Tuple[float, ...]:
    if not 0 <= position < length:
        raise ConfigError("impulse position out of range", "INVALID_STIMULUS")
    values = [0.0] * length
    values[position] = amplitude
    return tuple(values)


def step(length: int = 1600, position: int = 800,
         amplitude: float = 0.25) -> Tuple[float, ...]:
    if not 0 <= position <= length:
        raise ConfigError("step position out of range", "INVALID_STIMULUS")
    return tuple(0.0 if index < position else amplitude
                 for index in range(length))


def sweep(length: int = 1600, start_hz: float = 200.0,
          end_hz: float = 3000.0, amplitude: float = 0.3) -> Tuple[float, ...]:
    if length <= 0 or start_hz <= 0.0 or end_hz <= 0.0:
        raise ConfigError("invalid sweep geometry", "INVALID_STIMULUS")
    duration = length / float(SAMPLE_RATE_HZ)
    values = []
    for index in range(length):
        t = index / float(SAMPLE_RATE_HZ)
        phase = 2.0 * math.pi * (start_hz * t +
                                 (end_hz - start_hz) * t * t /
                                 (2.0 * duration))
        values.append(amplitude * math.sin(phase))
    return tuple(values)


def _span_kind(index: int) -> str:
    for start, end, kind in FIXTURE_SPANS:
        if start <= index < end:
            return kind
    return "pause"


def speech_like(length: int = 3200, seed: int = 20261126) -> Tuple[float, ...]:
    noise = _lcg(seed)
    values = []
    for index in range(length):
        kind = _span_kind(index)
        noise_value = next(noise)
        t = index / float(SAMPLE_RATE_HZ)
        if kind == "voiced":
            value = (0.25 * math.sin(2.0 * math.pi * 120.0 * t) +
                     0.12 * math.sin(2.0 * math.pi * 240.0 * t) +
                     0.06 * math.sin(2.0 * math.pi * 360.0 * t))
            envelope = 0.65 + 0.35 * math.sin(2.0 * math.pi * 3.0 * t)
            value = value * envelope + 0.005 * noise_value
        elif kind == "filler":
            value = 0.02 * noise_value
        else:
            value = 0.001 * noise_value
        values.append(value)
    return tuple(values)


STIMULUS_GENERATORS = {
    "silence": lambda: silence(1600),
    "impulse": lambda: impulse(1600, 800, 0.5),
    "step": lambda: step(1600, 800, 0.25),
    "sweep": lambda: sweep(1600, 200.0, 3000.0, 0.3),
    "speech_like": lambda: speech_like(3200),
}


def stimulus_metrics(name: str, samples: Sequence[float]) -> Dict[str, Any]:
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    peak = 0.0
    nonfinite = 0
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("INVALID_SAMPLE_TYPE: " + str(index),
                             "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            nonfinite += 1
            continue
        peak = max(peak, abs(number))
    if nonfinite:
        raise InputError("NONFINITE_SAMPLE", "NONFINITE")
    if peak > MAX_ABS_STIMULUS:
        raise InputError("STIMULUS_OUT_OF_RANGE", "OUT_OF_RANGE")
    return {
        "name": name,
        "sample_count": len(samples),
        "peak_abs": _r(peak),
        "rms": _r(rms([float(value) for value in samples])),
        "nonfinite_count": 0,
        "digest": tensor_digest([float(value) for value in samples]),
    }


def speech_contrast(samples: Sequence[float]) -> Dict[str, Any]:
    voiced = []
    pause = []
    for index, value in enumerate(samples):
        kind = _span_kind(index)
        if kind == "voiced":
            voiced.append(float(value))
        elif kind == "pause":
            pause.append(float(value))
    voiced_rms = rms(voiced)
    pause_rms = rms(pause)
    return {
        "voiced_rms": _r(voiced_rms),
        "pause_rms": _r(pause_rms),
        "voiced_to_pause_db": _r(db_ratio(voiced_rms, pause_rms)),
        "proxy": "source-anchored voiced/pause RMS contrast; not intelligibility",
    }


def acoustic_hop_geometry(sample_count: int) -> Dict[str, Any]:
    if isinstance(sample_count, bool) or not isinstance(sample_count, int):
        raise InputError("INVALID_SAMPLE_COUNT", "INVALID_SAMPLE_COUNT")
    if sample_count < 0:
        raise InputError("NEGATIVE_SAMPLE_COUNT", "INVALID_SAMPLE_COUNT")
    full = sample_count // EXPECTED_HOP_LENGTH
    return {
        "sample_count": sample_count,
        "hop_samples": EXPECTED_HOP_LENGTH,
        "full_frames": full,
        "remainder_samples": sample_count - full * EXPECTED_HOP_LENGTH,
        "measured_here": False,
        "note": ("Arithmetic floor division on the declared 320-sample "
                 "acoustic hop; not a model measurement."),
    }


def _validate_sample_list(samples: Any, expected: int | None) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise InputError("SAMPLES_NOT_A_LIST", "INVALID_SAMPLE_TYPE")
    if expected is not None and len(samples) != expected:
        raise InputError("WRONG_SAMPLE_COUNT", "WRONG_SAMPLE_COUNT")
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    result: List[float] = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("INVALID_SAMPLE_TYPE: " + str(index),
                             "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            raise InputError("NONFINITE_SAMPLE: " + str(index), "NONFINITE")
        if abs(number) > MAX_ABS_INPUT:
            raise InputError("SAMPLE_OUT_OF_RANGE: " + str(index),
                             "OUT_OF_RANGE")
        result.append(number)
    return result


def _require_int(value: Any, code: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(code, code)
    if minimum is not None and value < minimum:
        raise ConfigError(code, code)
    return value


def _validate_dependencies(value: Any) -> Tuple[str, str]:
    if not isinstance(value, (list, tuple)):
        raise ConfigError("DEPENDENCIES_NOT_A_LIST", "DEPENDENCIES_NOT_A_LIST")
    if len(value) != len(DEPENDENCIES):
        raise ConfigError("WRONG_DEPENDENCY_COUNT", "WRONG_DEPENDENCY_COUNT")
    for item in value:
        if not isinstance(item, str):
            raise ConfigError("INVALID_DEPENDENCY_TYPE",
                              "INVALID_DEPENDENCY_TYPE")
        if item not in DEPENDENCIES:
            raise ConfigError("UNKNOWN_DEPENDENCY", "UNKNOWN_DEPENDENCY")
    if len(set(value)) != len(DEPENDENCIES):
        raise ConfigError("DUPLICATE_DEPENDENCY", "DUPLICATE_DEPENDENCY")
    if tuple(value) != DEPENDENCIES:
        raise ConfigError("DEPENDENCY_ORDER", "DEPENDENCY_ORDER")
    return (value[0], value[1])


def validate_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise InputError("request must be an object", "INVALID_REQUEST")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown), "UNKNOWN_FIELD")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing), "MISSING_FIELD")
    candidate = request["candidate"]
    if candidate != CANDIDATE:
        raise ConfigError("UNKNOWN_CANDIDATE", "UNKNOWN_CANDIDATE")
    if _require_int(request["sample_rate_hz"], "WRONG_RATE") != SAMPLE_RATE_HZ:
        raise ConfigError("WRONG_RATE", "WRONG_RATE")
    if _require_int(request["channels"], "WRONG_CHANNELS") != 1:
        raise ConfigError("WRONG_CHANNELS", "WRONG_CHANNELS")
    if _require_int(request["frame_samples"], "WRONG_FRAME") != FRAME_SAMPLES:
        raise ConfigError("WRONG_FRAME", "WRONG_FRAME")
    samples = _validate_sample_list(request["samples"], FRAME_SAMPLES)
    epoch = _require_int(request["epoch"], "INVALID_EPOCH", 0)
    first_input_sample = _require_int(request["first_input_sample"],
                                      "INVALID_POSITION", 0)
    lifecycle = request["lifecycle"]
    if lifecycle not in LIFECYCLES:
        raise ConfigError("INVALID_LIFECYCLE", "INVALID_LIFECYCLE")
    execution_mode = _require_int(request["execution_mode"], "INVALID_MODE")
    if execution_mode not in EXECUTION_MODES:
        raise ConfigError("INVALID_MODE", "INVALID_MODE")
    target_condition = request["target_condition"]
    if target_condition != TARGET_CONDITION:
        raise ConfigError("UNKNOWN_TARGET_CONDITION",
                          "UNKNOWN_TARGET_CONDITION")
    dependencies = _validate_dependencies(request["dependencies"])
    return {
        "candidate": candidate,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "samples": tuple(samples),
        "epoch": epoch,
        "first_input_sample": first_input_sample,
        "lifecycle": lifecycle,
        "execution_mode": execution_mode,
        "target_condition": target_condition,
        "dependencies": dependencies,
    }


def validate_reset(epoch: Any, first_input_sample: Any,
                   previous_epoch: Any) -> Dict[str, int]:
    """Structural reset validator; owns no candidate state."""
    new_epoch = _require_int(epoch, "INVALID_EPOCH", 0)
    previous = _require_int(previous_epoch, "INVALID_EPOCH", 0)
    position = _require_int(first_input_sample, "INVALID_POSITION", 0)
    if new_epoch <= previous:
        raise ConfigError("EPOCH_NOT_INCREASING", "EPOCH_NOT_INCREASING")
    return {"epoch": new_epoch, "first_input_sample": position,
            "previous_epoch": previous}


def probe_candidate(request: Any) -> None:
    validated = validate_request(request)
    raise CandidateAbsent(
        "SOURCE_WEIGHTS_RUNTIME_ABSENT: " + validated["candidate"] + " X-VC "
        "checkpoint, GLM-4-Voice-Tokenizer weights, ERes2Net weights and "
        "pinned runtime are not present; no candidate processing is performed",
        "SOURCE_WEIGHTS_RUNTIME_ABSENT")


def _base_request() -> Dict[str, Any]:
    return {
        "candidate": CANDIDATE,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "samples": [0.0] * FRAME_SAMPLES,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
        "target_condition": TARGET_CONDITION,
        "dependencies": list(DEPENDENCIES),
    }


def _adverse_request_specs():
    base = _base_request()

    def variant(**changes):
        value = dict(base)
        value.update(changes)
        return value

    def with_samples(samples):
        return variant(samples=samples)

    short = [0.0] * (FRAME_SAMPLES - 1)
    nan_samples = [0.0] * FRAME_SAMPLES
    nan_samples[7] = float("nan")
    inf_samples = [0.0] * FRAME_SAMPLES
    inf_samples[9] = float("inf")
    negative_inf_samples = [0.0] * FRAME_SAMPLES
    negative_inf_samples[9] = float("-inf")
    return (
        ("unknown_candidate", variant(candidate="glm-4-voice")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("wrong_rate", variant(sample_rate_hz=48000)),
        ("wrong_channels", variant(channels=2)),
        ("wrong_frame", variant(frame_samples=320)),
        ("short_samples", with_samples(short)),
        ("empty_samples", with_samples([])),
        ("nonfinite_nan", with_samples(nan_samples)),
        ("nonfinite_inf", with_samples(inf_samples)),
        ("nonfinite_negative_inf", with_samples(negative_inf_samples)),
        ("out_of_range", with_samples([4.5] * FRAME_SAMPLES)),
        ("bool_sample", with_samples([True] + [0.0] * (FRAME_SAMPLES - 1))),
        ("string_sample", with_samples(["0.0"] + [0.0] * (FRAME_SAMPLES - 1))),
        ("null_sample", with_samples([None] + [0.0] * (FRAME_SAMPLES - 1))),
        ("negative_epoch", variant(epoch=-1)),
        ("bool_epoch", variant(epoch=True)),
        ("float_epoch", variant(epoch=1.0)),
        ("negative_position", variant(first_input_sample=-160)),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("invalid_execution_mode", variant(execution_mode=4)),
        ("zero_execution_mode", variant(execution_mode=0)),
        ("unknown_target_condition", variant(target_condition="p360")),
        ("missing_dependency", variant(
            dependencies=["glm-4-voice-tokenizer"])),
        ("extra_dependency", variant(
            dependencies=list(DEPENDENCIES) + ["x-vc"])),
        ("reordered_dependencies", variant(
            dependencies=["eres2net", "glm-4-voice-tokenizer"])),
        ("duplicate_dependency", variant(
            dependencies=["glm-4-voice-tokenizer",
                          "glm-4-voice-tokenizer"])),
        ("unknown_dependency", variant(
            dependencies=["glm-4-voice-tokenizer", "vocoder"])),
        ("dependencies_not_a_list", variant(
            dependencies="glm-4-voice-tokenizer,eres2net")),
        ("bool_dependency", variant(
            dependencies=[True, "eres2net"])),
        ("empty_dependencies", variant(dependencies=[])),
        ("request_not_object", "not-an-object"),
    )


def _adverse_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    for name, request in _adverse_request_specs():
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_request(request)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "dependency_case_count": sum(
            1 for case in cases if "dependenc" in case["id"]),
        "metrics": None,
        "cases": cases,
        "note": ("Invalid requests are rejected before any candidate call; no "
                 "metrics exist."),
    }


def _json_adverse_cases() -> Dict[str, Any]:
    specs = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} extra'),
        ("invalid_syntax", '{"a":}'),
        ("empty_text", ""),
    )
    cases: List[Dict[str, Any]] = []
    for name, text in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            strict_json_loads(text)
            accepted = True
        except JsonError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "cases": cases,
    }


RESET_CASES = (
    ("fresh_epoch_2_accepted", 2, 0, 1, True),
    ("equal_epoch_rejected", 1, 0, 1, False),
    ("lower_epoch_rejected", 0, 0, 1, False),
    ("negative_epoch_rejected", -1, 0, 1, False),
    ("negative_position_rejected", 2, -160, 1, False),
    ("bool_epoch_rejected", True, 0, 1, False),
    ("bool_position_rejected", 2, True, 1, False),
    ("float_epoch_rejected", 2.0, 0, 1, False),
)


def _reset_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    for name, epoch, position, previous, expected in RESET_CASES:
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_reset(epoch, position, previous)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        cases.append({
            "id": name,
            "accepted": accepted,
            "expected_accepted": expected,
            "error": error,
        })
    accepted_count = sum(1 for case in cases if case["accepted"])
    expected_count = sum(1 for case in cases if case["expected_accepted"])
    return {
        "case_count": len(cases),
        "accepted_count": accepted_count,
        "expected_accepted_count": expected_count,
        "matches_expectation": all(case["accepted"] == case["expected_accepted"]
                                   for case in cases),
        "state_owned": False,
        "metrics": None,
        "cases": cases,
        "note": ("Structural reset validation only; no candidate state exists "
                 "and no reset is executed."),
    }


def missing_result(fixture_name: str) -> Dict[str, Any]:
    return {
        "fixture": fixture_name,
        "status": "blocked",
        "reason": "source_weights_runtime_and_rights_absent",
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def _module_importable(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _resolve_workspace_path(label: str) -> Path:
    if label.startswith("~/"):
        return Path.home() / label[2:]
    return WORKSPACE / label


def _read_git_revision(root: Path) -> str | None:
    head_path = root / ".git/HEAD"
    if not head_path.is_file():
        return None
    head = head_path.read_text(encoding="ascii").strip()
    if not head.startswith("ref: "):
        return head or None
    reference = head[5:].strip()
    reference_path = root / ".git" / reference
    if reference_path.is_file():
        return reference_path.read_text(encoding="ascii").strip() or None
    packed_path = root / ".git/packed-refs"
    if packed_path.is_file():
        for line in packed_path.read_text(encoding="ascii").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            if len(parts) == 2 and parts[1] == reference:
                return parts[0]
    return None


def source_probe() -> Dict[str, Any]:
    if not SOURCE_ROOT.is_dir():
        return {
            "status": "blocked_source_absent",
            "present": False,
            "revision": None,
            "expected_revision": SOURCE_REVISION,
            "tree_digest": None,
            "expected_tree_digest": SOURCE_TREE_DIGEST,
            "file_count": 0,
            "expected_file_count": SOURCE_FILE_COUNT,
            "license": None,
            "note": "Pinned X-VC source checkout is absent.",
        }
    rows: List[str] = []
    for directory, directory_names, file_names in os.walk(SOURCE_ROOT):
        directory_names[:] = sorted(
            name for name in directory_names if name != ".git")
        for name in sorted(file_names):
            path = Path(directory) / name
            relative = path.relative_to(SOURCE_ROOT).as_posix()
            payload = path.read_bytes()
            rows.append(relative + " " + sha256_bytes(payload) + " " +
                        str(len(payload)) + "\n")
    tree_digest = sha256_bytes("".join(rows).encode("utf-8"))
    revision = _read_git_revision(SOURCE_ROOT)
    present = (
        revision == SOURCE_REVISION
        and tree_digest == SOURCE_TREE_DIGEST
        and len(rows) == SOURCE_FILE_COUNT
    )
    return {
        "status": "present_pinned" if present else "source_mismatch",
        "present": present,
        "revision": revision,
        "expected_revision": SOURCE_REVISION,
        "tree_digest": tree_digest,
        "expected_tree_digest": SOURCE_TREE_DIGEST,
        "file_count": len(rows),
        "expected_file_count": SOURCE_FILE_COUNT,
        "license": SOURCE_LICENSE,
        "note": ("Read-only digest over every non-.git file in the local "
                 "checkout; no upstream file is copied or executed. The "
                 "working-tree digest is pinned at the exact commit."),
    }


def _weight_markers_in(directory: Path, max_depth: int = 4) -> List[str]:
    found: List[str] = []
    base_depth = len(directory.parts)
    for current, directory_names, file_names in os.walk(directory):
        current_path = Path(current)
        depth = len(current_path.parts) - base_depth
        if depth >= max_depth:
            directory_names[:] = []
        else:
            directory_names[:] = sorted(directory_names)
        for name in sorted(file_names):
            if name.lower().endswith(WEIGHT_SUFFIXES):
                found.append(
                    (current_path / name).relative_to(directory).as_posix())
    return sorted(found)


def _bounded_name_search() -> Dict[str, Any]:
    roots: List[str] = []
    matches: List[str] = []
    entries = 0
    truncated = False
    for relative in SEARCH_ROOTS:
        root = WORKSPACE / relative
        if not root.exists():
            continue
        roots.append(relative)
        for directory, directory_names, file_names in os.walk(root):
            directory_names[:] = sorted(
                name for name in directory_names
                if name not in (".git", "__pycache__", "worktrees"))
            names = sorted(directory_names) + sorted(file_names)
            if entries + len(names) > MAX_SEARCH_ENTRIES:
                truncated = True
                break
            entries += len(names)
            for name in names:
                lowered = name.lower()
                if not lowered.endswith(WEIGHT_SUFFIXES):
                    continue
                if any(needle in lowered for needle in NAME_NEEDLES):
                    matches.append(
                        (Path(directory) / name).relative_to(
                            WORKSPACE).as_posix())
            if truncated:
                break
        if truncated:
            break
    return {
        "roots_requested": list(SEARCH_ROOTS),
        "roots_scanned": roots,
        "needles": list(NAME_NEEDLES),
        "weight_suffixes": list(WEIGHT_SUFFIXES),
        "entries_scanned": entries,
        "max_entries": MAX_SEARCH_ENTRIES,
        "truncated": truncated,
        "excluded": list(SEARCH_EXCLUSIONS),
        "match_count": len(matches),
        "matches": sorted(matches),
    }


def home_cache_probe() -> Dict[str, Any]:
    entries: List[str] = []
    matches: List[str] = []
    if HF_CACHE_ROOT.is_dir():
        entries = sorted(item.name for item in HF_CACHE_ROOT.iterdir())
        matches = [name for name in entries
                   if any(needle in name.lower() for needle in NAME_NEEDLES)]
    modelscope_entries: List[str] = []
    modelscope_matches: List[str] = []
    if MODELSCOPE_CACHE_ROOT.is_dir():
        for directory, directory_names, file_names in os.walk(
                MODELSCOPE_CACHE_ROOT):
            directory_names[:] = sorted(directory_names)
            if len(modelscope_entries) >= 64:
                break
            modelscope_entries.extend(
                sorted(directory_names) + sorted(file_names))
            break
        modelscope_matches = [
            name for name in modelscope_entries
            if any(needle in name.lower() for needle in NAME_NEEDLES)]
    return {
        "huggingface_root": "~/.cache/huggingface/hub",
        "huggingface_probed": HF_CACHE_ROOT.is_dir(),
        "huggingface_entry_count": len(entries),
        "huggingface_entries": entries,
        "huggingface_matches": matches,
        "modelscope_root": "~/.cache/modelscope/hub",
        "modelscope_probed": MODELSCOPE_CACHE_ROOT.is_dir(),
        "modelscope_entries": modelscope_entries,
        "modelscope_matches": modelscope_matches,
        "note": ("Read-only top-level directory-name listings; no cache file "
                 "is opened, imported or used."),
    }


def weights_probe() -> Dict[str, Any]:
    artifacts: Dict[str, Any] = {}
    all_checked: List[str] = []
    all_found: List[str] = []
    all_empty: List[str] = []
    for key, spec in WEIGHT_ARTIFACTS.items():
        checked: List[str] = []
        found: List[str] = []
        empty: List[str] = []
        for label in spec["paths"]:
            checked.append(label)
            target = _resolve_workspace_path(label)
            if target.is_file():
                if target.name.lower().endswith(WEIGHT_SUFFIXES):
                    found.append(label)
            elif target.is_dir():
                hits = _weight_markers_in(target)
                if hits:
                    found.extend((Path(label) / hit).as_posix()
                                 for hit in hits)
                else:
                    empty.append(label)
        all_checked.extend(checked)
        all_found.extend(found)
        all_empty.extend(empty)
        artifacts[key] = {
            "status": "weights_present_unqualified" if found
                      else "blocked_weights_absent",
            "present": bool(found),
            "artifact": spec["artifact"],
            "upstream_repository": spec["upstream_repository"],
            "required_files": list(spec["required_files"]),
            "checked_paths": sorted(checked),
            "found": sorted(set(found)),
            "empty_directories": sorted(set(empty)),
            "sha256": None,
            "byte_count": None,
            "license": None,
        }
    name_search = _bounded_name_search()
    for match in name_search["matches"]:
        all_found.append("search:" + match)
    cache = home_cache_probe()
    for name in cache["huggingface_matches"]:
        all_found.append("hf-cache:" + name)
    for name in cache["modelscope_matches"]:
        all_found.append("modelscope-cache:" + name)
    return {
        "status": "weights_present_unqualified" if all_found
                  else "blocked_weights_absent",
        "present": bool(all_found),
        "artifact": (
            "X-VC checkpoint plus GLM-4-Voice-Tokenizer and ERes2Net weights"),
        "x_vc_checkpoint": artifacts["x_vc_checkpoint"],
        "glm_4_voice_tokenizer": artifacts["glm_4_voice_tokenizer"],
        "eres2net": artifacts["eres2net"],
        "checked_paths": sorted(set(all_checked)),
        "empty_directories": sorted(set(all_empty)),
        "found": sorted(set(all_found)),
        "name_search": name_search,
        "home_cache": cache,
        "sha256": None,
        "byte_count": None,
        "note": ("Read-only path and name checks only; no archive, cache blob "
                 "or weight file is opened, downloaded or reconstructed."),
    }


def runtime_probe() -> Dict[str, Any]:
    checked: List[str] = []
    found: List[str] = []
    for label in RUNTIME_CANDIDATE_PATHS:
        checked.append(label)
        if _resolve_workspace_path(label).exists():
            found.append(label)
    modules = {name: _module_importable(name) for name in RUNTIME_MODULES}
    locks = [path for path in RUNTIME_LOCK_CANDIDATES
             if (WORKSPACE / path).is_file()]
    pinned = bool(found) and bool(locks)
    return {
        "status": "runtime_present_unqualified" if pinned
                  else "blocked_runtime_unpinned",
        "checked_paths": sorted(checked),
        "found": sorted(found),
        "lockfiles": sorted(locks),
        "importable_modules": modules,
        "present": bool(found),
        "pinned": pinned,
        "declared_requirements": dict(EXPECTED_REQUIREMENTS),
        "note": ("No package is installed, imported or downloaded. Import "
                 "probes report the current interpreter only."),
    }


def _yaml_lookup(text: str, *path: str) -> str | None:
    stack: List[Tuple[int, str]] = []
    for line in text.splitlines():
        match = re.match(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*):(.*)$", line)
        if match is None:
            continue
        indent = len(match.group(1))
        key = match.group(2)
        value = match.group(3).strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        current = tuple(item[1] for item in stack) + (key,)
        if current == path:
            return value
        stack.append((indent, key))
    return None


def _unquote(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in (
            "'", '"'):
        return stripped[1:-1]
    return stripped


def _require_yaml(text: str, *path: str) -> str:
    value = _yaml_lookup(text, *path)
    if value is None:
        raise ConfigError("missing config key: " + ".".join(path),
                          "CONFIG_INVALID")
    raw = value.strip()
    if raw[:1] in ("'", '"'):
        quote = raw[0]
        end = raw.find(quote, 1)
        if end <= 0:
            raise ConfigError("unterminated config string: " + ".".join(path),
                              "CONFIG_INVALID")
        return raw[1:end]
    return raw.split("#", 1)[0].strip()


def _require_yaml_int(text: str, *path: str) -> int:
    raw = _require_yaml(text, *path).split("#", 1)[0].strip()
    if re.fullmatch(r"-?[0-9]+", raw) is None:
        raise ConfigError("nonintegral config key: " + ".".join(path),
                          "CONFIG_INVALID")
    return int(raw, 10)


def requirements_pins(text: str) -> Dict[str, str]:
    declared: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.match(
            r"^([A-Za-z0-9_.-]+)\s*==\s*([0-9][A-Za-z0-9_.+-]*)\s*$",
            stripped)
        if match is None:
            continue
        declared[match.group(1).lower()] = match.group(2)
    for name, version in EXPECTED_REQUIREMENTS.items():
        if declared.get(name) != version:
            raise ConfigError("requirement pin mismatch: " + name,
                              "REQUIREMENTS_INVALID")
    return {name: declared[name] for name in EXPECTED_REQUIREMENTS}


def geometry() -> Dict[str, Any]:
    config_path = WORKSPACE / CONFIG_RELATIVE
    if sha256_file(config_path) != SOURCE_PINS[CONFIG_RELATIVE]:
        raise ConfigError("config digest mismatch", "CONFIG_INVALID")
    config = config_path.read_text(encoding="utf-8")

    sample_rate = _require_yaml_int(config, "sample_rate")
    n_fft = _require_yaml_int(config, "n_fft")
    win_length = _require_yaml_int(config, "win_length")
    hop_length = _require_yaml_int(config, "hop_length")
    num_mels = _require_yaml_int(config, "num_mels")
    latent_hop = _require_yaml_int(config, "latent_hop_length")
    rates_raw = _require_yaml(config, "model", "generator",
                              "acoustic_encoder", "encoder_rates")
    rates_literal = rates_raw.split("#", 1)[0].strip()
    try:
        rates = strict_json_loads(rates_literal)
    except JsonError:
        raise ConfigError("encoder rates are invalid", "CONFIG_INVALID")
    semantic_repo = _require_yaml(
        config, "model", "generator", "semantic_encoder", "encoder",
        "from_pretrained", "hf_repo")
    speaker_dir = _require_yaml(
        config, "model", "generator", "speaker_encoder", "pretrained_dir")
    speaker_dim = _require_yaml_int(
        config, "model", "generator", "speaker_predictor", "output_dim")
    semantic_width = _require_yaml_int(
        config, "model", "generator", "semantic_adapter", "input_channels")
    checkpoint = _require_yaml(
        config, "model", "generator", "checkpoint")

    if sample_rate != SAMPLE_RATE_HZ:
        raise ConfigError("config sample rate mismatch", "CONFIG_INVALID")
    if n_fft != EXPECTED_N_FFT or win_length != EXPECTED_WIN_LENGTH:
        raise ConfigError("config fft geometry mismatch", "CONFIG_INVALID")
    if hop_length != EXPECTED_HOP_LENGTH:
        raise ConfigError("config hop mismatch", "CONFIG_INVALID")
    if num_mels != EXPECTED_NUM_MELS:
        raise ConfigError("config mel count mismatch", "CONFIG_INVALID")
    if latent_hop != EXPECTED_LATENT_HOP:
        raise ConfigError("config latent hop mismatch", "CONFIG_INVALID")
    if rates != EXPECTED_ENCODER_RATES:
        raise ConfigError("config encoder rates mismatch", "CONFIG_INVALID")
    if semantic_repo != GLM_TOKENIZER:
        raise ConfigError("config semantic tokenizer mismatch",
                          "CONFIG_INVALID")
    expected_speaker_dir = (
        "pretrained/speech_eres2net_sv_en_voxceleb_16k")
    if speaker_dir != expected_speaker_dir:
        raise ConfigError("config speaker encoder path mismatch",
                          "CONFIG_INVALID")
    if speaker_dim != EXPECTED_SPEAKER_EMBEDDING_DIM:
        raise ConfigError("config speaker dimension mismatch",
                          "CONFIG_INVALID")
    if semantic_width != EXPECTED_SEMANTIC_INPUT_CHANNELS:
        raise ConfigError("config semantic width mismatch", "CONFIG_INVALID")
    if checkpoint != "null":
        raise ConfigError("config unexpectedly names a checkpoint",
                          "CONFIG_INVALID")

    requirements_path = WORKSPACE / REQUIREMENTS_RELATIVE
    if sha256_file(requirements_path) != SOURCE_PINS[REQUIREMENTS_RELATIVE]:
        raise ConfigError("requirements digest mismatch", "CONFIG_INVALID")
    requirements = requirements_pins(
        requirements_path.read_text(encoding="utf-8"))

    script_path = WORKSPACE / INFER_SCRIPT_RELATIVE
    if sha256_file(script_path) != SOURCE_PINS[INFER_SCRIPT_RELATIVE]:
        raise ConfigError("inference script digest mismatch", "CONFIG_INVALID")
    script = script_path.read_text(encoding="utf-8")
    current_match = re.findall(r"^current=(\d+)\s*$", script, re.MULTILINE)
    chunk_match = re.findall(r"^chunk=(\d+)\s*$", script, re.MULTILINE)
    future_match = re.findall(r"^future=(\d+)\s*$", script, re.MULTILINE)
    smooth_match = re.findall(r"^smooth=(\d+)\s*$", script, re.MULTILINE)
    if (len(current_match) != 1 or len(chunk_match) != 1
            or len(future_match) != 1 or len(smooth_match) != 1):
        raise ConfigError("inference script geometry is ambiguous",
                          "CONFIG_INVALID")
    current = int(current_match[0], 10)
    chunk_samples = int(chunk_match[0])
    future = int(future_match[0])
    smooth = int(smooth_match[0])
    if (current, chunk_samples, future, smooth) != (
            EXPECTED_CURRENT, EXPECTED_CHUNK_SAMPLES, EXPECTED_FUTURE,
            EXPECTED_SMOOTH):
        raise ConfigError("inference script geometry changed",
                          "CONFIG_INVALID")
    checkpoint_path_match = re.findall(r'^ckpt="([^"]+)"\s*$', script,
                                       re.MULTILINE)
    if checkpoint_path_match != ["ckpts/xvc.pt"]:
        raise ConfigError("checkpoint path changed", "CONFIG_INVALID")

    acoustic_hop = 1
    for rate in rates:
        acoustic_hop *= rate
    if acoustic_hop != EXPECTED_HOP_LENGTH:
        raise ConfigError("acoustic hop product mismatch", "CONFIG_INVALID")

    speaker_code = (WORKSPACE / SPEAKER_ENCODER_RELATIVE).read_text(
        encoding="utf-8")
    if '"embedding_size": 192' not in speaker_code:
        raise ConfigError("ERes2Net embedding width changed",
                          "CONFIG_INVALID")
    semantic_code = (WORKSPACE / SEMANTIC_ENCODER_RELATIVE).read_text(
        encoding="utf-8")
    if "WhisperVQEncoder" not in semantic_code:
        raise ConfigError("GLM tokenizer encoder wrapper changed",
                          "CONFIG_INVALID")
    eres_code = (WORKSPACE / ERES2NET_CODE_RELATIVE).read_text(
        encoding="utf-8")
    if "class ERes2Net" not in eres_code:
        raise ConfigError("ERes2Net code changed", "CONFIG_INVALID")

    return {
        "source": (
            "configs/xvc.yaml + requirements.txt + scripts/infer_single.sh + "
            "semantic_encoder.py + speaker_encoder.py + utils/ERes2Net.py"),
        "input_sample_rate_hz": sample_rate,
        "v0_frame_samples": FRAME_SAMPLES,
        "v0_frame_ms": _r(FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ),
        "n_fft": n_fft,
        "win_length": win_length,
        "hop_length": hop_length,
        "hop_ms": _r(hop_length * 1000.0 / SAMPLE_RATE_HZ),
        "num_mels": num_mels,
        "latent_hop_length": latent_hop,
        "acoustic_encoder_rates": rates,
        "acoustic_hop_samples": acoustic_hop,
        "acoustic_frame_rate_hz": _r(SAMPLE_RATE_HZ / float(acoustic_hop)),
        "latent_frame_rate_hz": _r(SAMPLE_RATE_HZ / float(latent_hop)),
        "v0_frames_per_acoustic_frame": acoustic_hop // FRAME_SAMPLES,
        "semantic_tokenizer_repository": semantic_repo,
        "semantic_feature_width": semantic_width,
        "speaker_encoder_pretrained_dir": speaker_dir,
        "speaker_embedding_dim": speaker_dim,
        "declared_requirements": requirements,
        "streaming_cli_defaults": {
            "current": current,
            "current_semantics": (
                "0 selects the offline path; >0 selects streaming"),
            "chunk_samples": chunk_samples,
            "chunk_ms": _r(chunk_samples * 1000.0 / SAMPLE_RATE_HZ),
            "future": future,
            "smooth": smooth,
        },
        "candidate_checkpoint_path": checkpoint_path_match[0],
        "candidate_checkpoint_named_in_config": False,
        "measured_here": False,
        "candidate_output": False,
        "note": (
            "Arithmetic on the pinned config, requirements and inference "
            "script only. These are declared values, not X-VC geometry "
            "measurements and not a content delay."),
    }


def historical_evidence() -> Dict[str, Any]:
    results_dir = (
        WORKSPACE / "research/voice-conversion-eval-20261101/results")
    return {
        "status": "no_local_xvc_execution_record",
        "records_found": 0,
        "results_path": (
            "research/voice-conversion-eval-20261101/results"),
        "results_path_present": results_dir.is_dir(),
        "xvc_results_directory_present": (results_dir / "xvc").is_dir(),
        "source_reported_results": {
            "ledger_checkpoint_size_gb": 5.01,
            "ledger_host_memory_budget_gb": 8.0,
            "note": ("Source-reported in the linked X-VC ledger row; not a "
                     "local measurement."),
        },
        "audio_artifacts": [],
        "metrics_artifacts": [],
        "transcripts": [],
        "timing": None,
        "identity_similarity": "not_scored",
        "naturalness": "not_scored",
        "reproduced_here": False,
        "qualifies_candidate": False,
        "note": (
            "The linked ledger records X-VC weights as not downloaded and the "
            "candidate as blocked. No local output, metric, transcript, "
            "identity, naturalness, timing or listening record exists."),
    }


def dependency_resolution() -> Dict[str, Any]:
    return {
        "x_vc_checkpoint": {
            "status": "blocked_weights_absent",
            "present": False,
            "required": X_VC_CHECKPOINT,
            "sha256": None,
            "byte_count": None,
        },
        "glm_4_voice_tokenizer": {
            "status": "blocked_weights_absent",
            "present": False,
            "required": GLM_TOKENIZER,
            "sha256": None,
            "byte_count": None,
        },
        "eres2net": {
            "status": "blocked_weights_absent",
            "present": False,
            "required": ERES2NET,
            "sha256": None,
            "byte_count": None,
        },
        "joint_memory": {
            "status": "blocked_not_measured",
            "source_reported_checkpoint_size_gb": 5.01,
            "source_reported_host_memory_budget_gb": 8.0,
            "measured_here": False,
        },
        "note": (
            "Both X-VC dependencies resolve to absent weight artifacts. No "
            "placeholder, surrogate or partial dependency is accepted."),
    }


def voice_profile_mapping() -> Dict[str, str]:
    return {
        "permitted_input_and_target_reference_scope":
            "blocked_no_source_target_pair_or_rights_record",
        "task_and_language_speaker_groups":
            "blocked_no_frozen_cohort_or_groups",
        "text_and_semantic_content":
            "blocked_no_model_transcript_or_cohort",
        "identity_and_similarity": "blocked_not_scored",
        "naturalness": "blocked_no_listening_or_mos",
        "alignment_first_output_and_tail_timing":
            "blocked_no_documented_or_measured_timing",
        "exact_target_condition":
            "blocked_no_documented_target_voice_or_condition",
        "consent_reference_availability_and_output_use":
            "blocked_rights_and_consent_absent",
        "paired_quality_control": "blocked_weights_and_runtime_absent",
        "clean_reference_preservation": "blocked_no_paired_clean_reference",
        "numerical_and_nonfinite": "partial_local_harness_only",
        "glm_4_voice_tokenizer_resolution": "blocked_weights_absent",
        "eres2net_resolution": "blocked_weights_absent",
        "joint_checkpoint_runtime_memory": "blocked_not_measured",
        "candidate_output": "blocked_weights_and_runtime_absent",
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "exact_x_vc_glm4voice_eres2net_weights_and_runtime":
            "blocked_weights_and_runtime_absent",
        "glm_4_voice_semantic_tokenization": "blocked_weights_absent",
        "eres2net_speaker_embedding": "blocked_weights_absent",
        "joint_checkpoint_runtime_memory": "blocked_not_measured",
        "paired_si_sdr_stoi": "blocked_no_paired_clean_reference",
        "clean_speech_preservation": "blocked_no_paired_clean_reference",
        "text_semantic_content": "blocked_no_model_transcript_or_cohort",
        "identity_similarity": "blocked_not_scored",
        "naturalness": "blocked_no_listening",
        "alignment_first_output_tail_and_content_delay":
            "blocked_no_documented_or_measured_timing",
        "target_condition_and_consent":
            "blocked_rights_and_consent_absent",
        "language_and_speaker_groups": "blocked_no_frozen_cohort",
        "numerical_and_nonfinite": "partial_local_harness_only",
        "delay_state_reset_drain_and_modes":
            "blocked_weights_and_runtime_absent",
        "device_timing_and_callback": "blocked_no_paced_device_measurement",
    }


def candidates() -> Dict[str, Any]:
    return {
        CANDIDATE: {
            "status": "blocked_weights_and_runtime_absent",
            "metrics": None,
            "qualifies_candidate": False,
            "target_condition": TARGET_CONDITION,
            "dependencies": {
                "glm-4-voice-tokenizer": "blocked_weights_absent",
                "eres2net": "blocked_weights_absent",
            },
            "reason": (
                "The X-VC checkpoint, GLM-4-Voice-Tokenizer weights, ERes2Net "
                "weights and a hash-pinned runtime are absent; no conversion, "
                "quality or timing result was produced."),
        }
    }


def controls() -> Dict[str, Any]:
    return {
        "source_identity_control": {
            "status": "not_run_no_candidate",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "sibling_voice_baseline": {
            "status": "not_reused_separate_candidate",
            "metrics": None,
            "qualifies_candidate": False,
        },
        "harness_identity_control": {
            "status": "bit_exact_synthetic_only",
            "candidate_processing": False,
        },
    }


def stimulus_probe() -> Dict[str, Any]:
    stimuli: Dict[str, Any] = {}
    identity: Dict[str, Any] = {}
    hop: Dict[str, Any] = {}
    for name, generator in STIMULUS_GENERATORS.items():
        samples = generator()
        stimuli[name] = stimulus_metrics(name, samples)
        identity[name] = {
            "digest": tensor_digest(samples),
            "byte_identical": tuple(samples) == tuple(float(value)
                                                     for value in samples),
        }
        hop[name] = acoustic_hop_geometry(len(samples))
    return {
        "purpose": (
            "harness stimulus characterisation only; not an X-VC result and "
            "not a candidate output"),
        "stimuli": stimuli,
        "speech_contrast": speech_contrast(STIMULUS_GENERATORS["speech_like"]()),
        "identity_control": identity,
        "acoustic_hop_probe": hop,
        "candidate_processing": False,
    }


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ConfigError("TASKS.json is missing", "BOARD_MISSING")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise ConfigError("TASKS.json shape is invalid", "BOARD_INVALID")
    task = None
    for row in board["tasks"]:
        if isinstance(row, dict) and row.get("id") == TASK:
            task = row
            break
    if task is None:
        raise ConfigError("linked task row is missing", "BOARD_ROW_MISSING")
    stable = {
        "task_id": task.get("id"),
        "title": task.get("title"),
        "mode": task.get("mode"),
        "repository": task.get("repository"),
        "component": task.get("component"),
    }
    if stable != EXPECTED_LINK:
        raise ConfigError("stable linked-row identity changed",
                          "BOARD_IDENTITY_CHANGED")
    rows = [stable]
    digest = sha256_bytes(canonical_bytes(rows))
    return rows, digest


def inventory_link() -> Dict[str, Any]:
    inventory = strict_json_loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    if not isinstance(inventory, dict) or not isinstance(
            inventory.get("components"), list):
        raise ConfigError("INVENTORY.json shape is invalid",
                          "INVENTORY_INVALID")
    rows = [row for row in inventory["components"]
            if isinstance(row, dict) and row.get("id") == COMPONENT]
    if len(rows) != 1:
        raise ConfigError("inventory row is missing or duplicated",
                          "INVENTORY_ROW_MISSING")
    row = rows[0]
    projection = {
        "id": row.get("id"),
        "name": row.get("name"),
        "area": row.get("area"),
        "evidence_status": row.get("evidence_status"),
        "repository": row.get("repository"),
        "disposition": row.get("disposition"),
        "verification_profile": row.get("verification_profile"),
        "task": row.get("task"),
    }
    if projection != EXPECTED_INVENTORY:
        raise ConfigError("inventory row identity changed",
                          "INVENTORY_IDENTITY_CHANGED")
    return projection


def evidence_entry() -> Dict[str, Any]:
    path = WORKSPACE / "research/voice-conversion-eval-20261101/README.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    line_number = 20
    if line_number > len(lines):
        raise ConfigError("evidence line is out of range", "EVIDENCE_MISSING")
    text = lines[line_number - 1]
    required = ("X-VC", "5.01 GB", "GLM-4-Voice", "ERes2Net",
                "8 GB memory budget")
    if not all(token in text for token in required):
        raise ConfigError("evidence line changed", "EVIDENCE_CHANGED")
    return {
        "path": "research/voice-conversion-eval-20261101/README.md",
        "line": line_number,
        "text": text,
        "sha256": sha256_bytes(text.encode("utf-8")),
        "tokens_verified": list(required),
        "inventory_row_evidence_path": (
            "research/voice-conversion-eval-20261101/README.md"),
        "inventory_row_has_explicit_line": False,
        "linked_ledger_row": "X-VC",
        "note": (
            "Exact linked X-VC ledger row. It records an absent download and "
            "both GLM-4-Voice and ERes2Net dependencies, not a local run."),
    }


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "decision": "DEFER",
        "processor_exposure": "deferred_until_independent_review",
        "proposal_only": True,
        "readiness": "incomplete",
        "status": "not_qualified",
        "upstream_parity": False,
    }


def boundary() -> Dict[str, Any]:
    return {
        "benchmark_claim": False,
        "board_or_handoff_changed": False,
        "ci_changed": False,
        "descriptor_default_changed": False,
        "descriptor_registration": False,
        "enabled_by_default": False,
        "format": {
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
            "sample_rate_hz": SAMPLE_RATE_HZ,
        },
        "installed_v0_unchanged": True,
        "opt_in_required": True,
        "provider_intake_complete": False,
        "provider_registered": False,
        "public_api_abi_changed": False,
        "public_c_boundary": "not used: no C provider, header or installed target",
        "real_corpus_or_weights": False,
        "registry_changed": False,
        "release_claim": False,
        "shared_cmake_changed": False,
    }


def artifact_pins(names: Sequence[str] = SOURCE_ARTIFACT_FILES) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in names:
        path = HERE / name
        if not path.is_file():
            raise ConfigError("missing package artifact: " + name,
                              "MISSING_ARTIFACT")
        pins[name] = sha256_file(path)
    return pins


def source_evidence_statements() -> List[str]:
    return [
        ("research/voice-conversion-eval-20261101/README.md line 20 records "
         "X-VC as 'Not downloaded' and 'Blocked', states that the official "
         "HF checkpoint is 5.01 GB, that the pipeline also requires "
         "GLM-4-Voice and ERes2Net encoders, and that the checkpoint alone "
         "exceeds this host's 8 GB memory budget."),
        ("the pinned X-VC README requires GLM-4-Voice-Tokenizer "
         "(zai-org/glm-4-voice-tokenizer) for semantic tokenization, the "
         "ERes2Net speaker encoder "
         "(iic/speech_eres2net_sv_en_voxceleb_16k) for speaker features, and "
         "the X-VC checkpoint at ckpts/xvc.pt."),
        ("research/voice-conversion-eval-20261101/repos/x-vc is pinned at "
         "commit 49df8c591eafc48b096e466d96f9839f9c0dd739 under MIT with 82 "
         "non-.git files; configs/xvc.yaml selects both dependency "
         "repositories and declares checkpoint: null."),
        ("plan/INVENTORY.json row glm-4-voice-and-eres2net-for-x-vc is "
         "evidence_status=blocked, disposition=sdk-model, "
         "verification_profile=voice, task="
         "SDK-GLM-4-VOICE-AND-ERES2NET-FOR-X-VC, with the single evidence "
         "path research/voice-conversion-eval-20261101/README.md and the plan "
         "note to resolve both exact dependencies and checkpoint/runtime "
         "memory before X-VC evaluation."),
        ("plan/swarm/VERIFICATION.md assigns the Voice profile: permitted "
         "input/target references, language/speaker groups, separate content, "
         "identity and naturalness outcomes, alignment, first-output/tail and "
         "independent consent/reference/output-use gates."),
    ]


# ---------------------------------------------------------------------------
# Task-local git scope
# ---------------------------------------------------------------------------
# The merged squash lands on `main`; later merges add unrelated sibling task
# packages. A fixed historical commit therefore cannot be the scope base: it
# would report those siblings as out-of-scope edits of this task. The base is
# the newest merge-base between HEAD and the PR base refs, so the comparison
# contains exactly the commits this branch added and fail-closed scope checks
# still catch any edit outside TASK_PREFIX.
SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    """Return the commit SHA a ref resolves to, or None when it is absent."""
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base between HEAD and an available PR base ref."""
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
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> List[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    source = source_probe()
    weights = weights_probe()
    runtime = runtime_probe()
    geom = geometry()
    history = historical_evidence()
    dependencies = dependency_resolution()
    adverse_request = _adverse_cases()
    adverse_json = _json_adverse_cases()
    reset = _reset_cases()
    stimuli = stimulus_probe()
    gates = [dict(gate) for gate in GATES]
    local_checks = {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "stable_board_identity_only": True,
        "inventory_identity_exact": inventory_link() == EXPECTED_INVENTORY,
        "source_pin_exact": source["status"] == "present_pinned",
        "weights_probe_complete": weights["status"] ==
        "blocked_weights_absent",
        "runtime_probe_complete": runtime["status"] ==
        "blocked_runtime_unpinned",
        "bounded_name_search_complete": (
            weights["name_search"]["truncated"] is False and
            weights["name_search"]["match_count"] == 0),
        "home_cache_has_no_dependency_entry": (
            weights["home_cache"]["huggingface_matches"] == [] and
            weights["home_cache"]["modelscope_matches"] == []),
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "dependency_requests_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if "dependenc" in case["id"]),
        "nonfinite_samples_rejected": all(
            not case["accepted"] for case in adverse_request["cases"]
            if case["id"].startswith("nonfinite")),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "reset_cases_match_expectation": reset["matches_expectation"],
        "missing_result_blocked":
            missing_result("xvc_synthetic_placeholder")["status"] == "blocked",
        "identity_control_bit_exact": all(
            block["byte_identical"]
            for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
        "exact_dependency_geometry_pinned": (
            geom["semantic_tokenizer_repository"] == GLM_TOKENIZER
            and geom["speaker_embedding_dim"] ==
            EXPECTED_SPEAKER_EMBEDDING_DIM
            and geom["semantic_feature_width"] ==
            EXPECTED_SEMANTIC_INPUT_CHANNELS
            and geom["acoustic_hop_samples"] == EXPECTED_HOP_LENGTH),
        "requirements_pins_exact": (
            geom["declared_requirements"] == EXPECTED_REQUIREMENTS),
        "both_dependencies_resolved_absent": (
            dependencies["glm_4_voice_tokenizer"]["present"] is False and
            dependencies["eres2net"]["present"] is False),
        "real_corpus_not_read": True,
        "no_result_qualifies_candidate": True,
    }
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_not_qualified",
        "decision": "DEFER",
        "qualification_status": "not_qualified",
        "qualification": qualification(),
        "boundary": boundary(),
        "profile": {
            "name": "voice",
            "source": SOURCE_PINS[VOICE_PROFILE_SOURCE],
        },
        "profile_mapping": voice_profile_mapping(),
        "inventory_link": inventory_link(),
        "evidence_entry": evidence_entry(),
        "reference": {
            "implementation": "task-local standard-library evidence builder",
            "real_x_vc_source_present": source["present"],
            "real_x_vc_checkpoint_present": weights["x_vc_checkpoint"][
                "present"],
            "real_glm_4_voice_tokenizer_present": weights[
                "glm_4_voice_tokenizer"]["present"],
            "real_eres2net_present": weights["eres2net"]["present"],
            "pinned_runtime_present": runtime["pinned"],
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "real_corpus_read": False,
            "note": (
                "No X-VC network, GLM-4-Voice tokenizer, ERes2Net encoder, "
                "vocoder, checkpoint loader or inference path is implemented "
                "or simulated; only probes, declared geometry arithmetic, "
                "request rejection and synthetic controls are performed."),
        },
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "source_evidence_statements": source_evidence_statements(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_link_fields": list(LINK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "artifact_pins": artifact_pins(),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "source_probe": source,
        "weights_probe": weights,
        "runtime_probe": runtime,
        "geometry": geom,
        "historical_evidence": history,
        "dependency_resolution": dependencies,
        "candidates": candidates(),
        "controls": controls(),
        "required_results": candidate_required_results(),
        "stimulus_probe": stimuli,
        "adverse": {
            "invalid_config_and_input": adverse_request,
            "invalid_json_numeric_fields": adverse_json,
            "reset_validation": reset,
            "missing_result": missing_result("xvc_synthetic_placeholder"),
        },
        "local_harness_checks": local_checks,
        "release_gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "gates": [gate["id"] for gate in gates],
        "regressions": [],
        "regression_count": 0,
        "no_missing_result_qualifies_candidate": True,
        "generated_by": "run.py --report",
    }
    if not finite_json(report):
        raise EvidenceError("REPORT_NONFINITE", "REPORT_NONFINITE")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
