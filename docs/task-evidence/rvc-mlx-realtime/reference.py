# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-RVC-MLX-REALTIME (RVC-MLX realtime).

This module is standard-library only and deterministic. It contains no RVC-MLX
source copy, RVC checkpoint, MLX weight, ContentVec/HuBERT or RMVPE asset, FAISS
index, MLX runtime, Metal execution, audio-device callback, captured microphone
sample, generated voice, listening result or device-timing measurement. It
records the exact external blockers, verifies and pins the present upstream
source checkout, probes a fixed list of workspace, checkout and home-cache paths
to evidence the absence of weights/assets/runtime, validates a caller-supplied
realtime bundle manifest with a fail-closed admission boundary, implements a
small deterministic arithmetic reference for the documented block/SOLA/queue
geometry, and builds the canonical contract/report.

The upstream checkout at `research/.../repos/rvc-mlx-realtime` is present at an
exact revision. That source presence is recorded and pinned, but it is not a
license grant, a verified weight set, a runtime, a target condition or a model
result. The checkout carries no LICENSE/NOTICE/COPYING file, the target and
shared model weights are absent, the MLX/MLX-Metal runtime is not installed, and
no realtime or device run exists. Nothing was downloaded, imported, loaded,
linked or executed.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-RVC-MLX-REALTIME"
COMPONENT_ID = "rvc-mlx-realtime"
TASK_TITLE = "RVC-MLX realtime"
CONTRACT_ID = "audio-sdk/rvc-mlx-realtime-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
MODE = "implementation"
BASE_COMMIT = "55d99cc1f03d06c16012abea914e75d93160935a"
BRANCH = "swarm/SDK-RVC-MLX-REALTIME"
WRITE_SCOPE = "docs/task-evidence/rvc-mlx-realtime/ only"
TASK_PREFIX = "docs/task-evidence/rvc-mlx-realtime/"

SOURCE_REVISION = "95a69ae2467738c605762bb5e84e8cdcef09d83d"
SOURCE_TREE_SHA256 = (
    "807c15e44d9769389f6382dcaeefa7618cda578fcb3d3a015660ba94756fd861")
SOURCE_TREE_FILE_COUNT = 68
SOURCE_TREE_BYTE_COUNT = 598143
SOURCE_ROOT = "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime"

# Documented realtime defaults from the pinned checkout. These are declared
# values, not measurements. The CLI/controller defaults (block 200 ms,
# crossfade 60 ms, extra 300 ms) and the StreamProcessor signature defaults
# (block 250 ms, crossfade 80 ms, extra 300 ms, SOLA search 12 ms) are
# cross-checked against the pinned source bytes below.
INPUT_SAMPLE_RATE = 16000
MODEL_SAMPLE_RATE = 40000
HUBERT_HOP = 160
BLOCK_MS = 200
CROSSFADE_MS = 60
EXTRA_MS = 300
SOLA_SEARCH_MS = 12
QUEUE_CAPACITY = 2
RING_BLOCKS = 4

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


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

# Immutable read-only inputs. `source:` rows are workspace-relative; the rest
# are SDK-worktree-relative. The mutable shared board is deliberately excluded
# from the pin set; only its stable row identity gates anything.
SOURCE_PINS = {
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/results/rvc/metrics.json":
        "14fc2c08086efadea87ba5a254704e086c3c4c94831a82de8796184168918b36",
    "research/voice-conversion-eval-20261101/results/rvc/asr.json":
        "2d28a6e4e93e450bc7894e68881926bb315d73dd82cd08bd44e597f7d51fff24",
    "research/voice-conversion-eval-20261101/scripts/run_rvc_vctk_eval.py":
        "a8f66b2a5af368f4a0573e954022e17577e2d9f0c3778abb0a1a4e65c15877da",
    "research/voice-conversion-eval-20261101/repos/rvc/LICENSE":
        "bec61ed1eb9a3748644ddbc50303aa6978e14eeaba46822e59a006c722b52585",
    "research/voice-conversion-eval-20261101/repos/rvc/README.md":
        "6ae347c0cc60836f1e7fd2b73ee73327746e66c32a5dd4270d02a096810bca8b",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/README.md":
        "11957c429305383782cf793a1672c05b87fe1db01f4f2665fb594d11a6798aa4",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "pyproject.toml":
        "bf08a56975f4561b0c10dba0b422269a39ebb996a5059079db7235bdf7fadf9d",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/uv.lock":
        "c00f4e8d9f7b0034272d59e3d18d3aac3ef3683de788caf0d6f033c3b210f9c8",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "docs/realtime.md":
        "f4564c7d6fc4613e446d6e02093de6a32018cfec344bf0d8ed505b625bf2f45d",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "docs/engine.md":
        "5c821ec4645e5539e5a563667b0b2f9b8682f5049e6909dbf3c09ebb9c3ccf90",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "docs/performance.md":
        "4afd68f91dc75faa1753b67e0609e2bd11e281682b3c43572fdab388405f2dce",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "docs/models-and-conversion.md":
        "c9841d9f600dcbd37e61e3f5acaf06e86b4b543653724e07d7cf73a5fa9167ef",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "rvc_mlx_rt/realtime/stream.py":
        "b508cb45d43f9d4c614143c2962c5fa30b92c05cc7d0af0568b37535fc99b56d",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "rvc_mlx_rt/realtime/controller.py":
        "e762bebacf7910a23bba6e122a0b44c86aa68378a076b32bd944c772a7cb9ba6",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "rvc_mlx_rt/model_manager.py":
        "9a0824f79e61291c0fca908d12c83d6e48c203ec265adeb7f54272e8cc4f8ddc",
    "research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime/"
    "models/tomorin.json":
        "b6a886ba38052adeec2d5ba5e4ad5413b11d5692f42e6dcd676ed20927f2b63d",
    "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md":
        "b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6",
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
    "docs/task-evidence/llvc/README.md":
        "f6d663bc171026181107a6e9ddcf1356fa9eb9e2fd16625267b35a5bc3bda717",
    "docs/task-evidence/llvc/report.json":
        "22d30a3c4f70143ba38f099019c3fcc6b123f4f4f3120f6ee73932d82fed342f",
    "docs/task-evidence/survey-trn-04/README.md":
        "e0b4ea4d92b122e9820b9857da5e4813db29b048468f2b0383e67ef4264eccae",
    "docs/task-evidence/survey-trn-04/report.json":
        "fb34a1129db91808c450cf9ce90d68a2f2ff34734b26891763ede6b0915f0446",
    "docs/task-evidence/survey-trn-05/README.md":
        "81b51f5696142a7fb77dd285e1db866f550de0faf5e5160ed66d15499b64c26b",
    "docs/task-evidence/survey-trn-05/report.json":
        "fd281bbacb62298102af00da3f304bd564a1f7f25b7be050e5c95ad4e4fc0773",
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
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                   "SDK-FND-PROVIDER"],
}
LINKED_ROWS = (
    BOARD_ROW_PROJECTION,
    {
        "id": "SDK-FND-AUDIT",
        "title": "Public provider intake and asset boundary",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
    {
        "id": "SDK-FND-EVIDENCE",
        "title": "Task-matched conformance and reproducible benchmark evidence",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
    {
        "id": "SDK-FND-NN",
        "title": "Optional neural and offline runtime boundary",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-FND-PROVIDER",
        "title": "Provider integration boundaries and build fragments",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-TIMING"],
    },
    {
        "id": "SDK-RVC-V2-VCTK-P226",
        "title": "RVC v2 VCTK p226",
        "component": "rvc-v2-vctk-p226",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                       "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-RVC-FAISS-RETRIEVAL",
        "title": "RVC FAISS retrieval",
        "component": "rvc-faiss-retrieval",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                       "SDK-FND-PROVIDER"],
    },
)

# Fixed, bounded absence probes. No recursive workspace walk is performed and
# no download is attempted. Any present path makes report generation fail.
ABSENCE_PROBES = (
    SOURCE_ROOT + "/LICENSE",
    SOURCE_ROOT + "/LICENSE.txt",
    SOURCE_ROOT + "/COPYING",
    SOURCE_ROOT + "/NOTICE",
    SOURCE_ROOT + "/models/cache",
    SOURCE_ROOT + "/models/cache/hubert.npz",
    SOURCE_ROOT + "/models/cache/rmvpe.npz",
    SOURCE_ROOT + "/models/cache/tomorin.npz",
    SOURCE_ROOT + "/models/tomorin.npz",
    SOURCE_ROOT + "/models/tomorin.pth",
    SOURCE_ROOT + "/assets",
    SOURCE_ROOT + "/assets/contentvec/pytorch_model.bin",
    SOURCE_ROOT + "/assets/predictors/rmvpe.pt",
    SOURCE_ROOT + "/.venv",
    "research/voice-conversion-eval-20261101/.venv-rvc-mlx",
    "research/voice-conversion-eval-20261101/models/rvc-mlx-realtime",
    "research/voice-conversion-eval-20261101/models/rvc-mlx-realtime/"
    "tomorin.pth",
    "research/voice-conversion-eval-20261101/checkpoints/rvc-mlx-realtime",
    "research/voice-conversion-eval-20261101/checkpoints/rvc-mlx-realtime/"
    "hubert.npz",
    "research/voice-conversion-eval-20261101/checkpoints/rvc-mlx-realtime/"
    "rmvpe.npz",
    "data/models/rvc-mlx-realtime",
    "data/models/rvc-mlx-realtime/tomorin.npz",
    "data/assets/rvc-mlx-realtime",
    "data/envs/rvc-mlx",
    "data/wheels/rvc_mlx_rt-0.1.0-py3-none-any.whl",
    "third_party/rvc-mlx-realtime",
    "deps/rvc-mlx-realtime",
    "adapters/rvc-mlx-realtime",
    "adapters/rvc-mlx-realtime/run.py",
    "docs/task-evidence/rvc-mlx-realtime/weights",
    "docs/task-evidence/rvc-mlx-realtime/assets",
    "docs/task-evidence/rvc-mlx-realtime/models",
    "docs/task-evidence/rvc-mlx-realtime/output.wav",
    "docs/task-evidence/rvc-mlx-realtime/cohort",
    "LICENSES/RVC-MLX-REALTIME.txt",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/rvc-mlx-realtime",
    "~/.cache/huggingface/hub/models--tizee--rvc-mlx-realtime",
    "~/Library/Caches/rvc-mlx-realtime",
)

# The checkout has no declared license file. The original RVC project's MIT
# LICENSE is pinned for contrast; it does not automatically license this fork's
# own modifications, vendored MLX modules or redistributed base assets.
SOURCE_PRESENCE = {
    "path": SOURCE_ROOT,
    "revision": SOURCE_REVISION,
    "revision_source": "git rev-parse HEAD of the shallow checkout",
    "tree_sha256": SOURCE_TREE_SHA256,
    "tree_digest_recipe": (
        "sha256 over sorted '<relative-path>\\0<file-sha256>\\n' rows for "
        "every non-.git regular file"),
    "file_count": SOURCE_TREE_FILE_COUNT,
    "tree_byte_count": SOURCE_TREE_BYTE_COUNT,
    "license_id": None,
    "license_path": None,
    "license_present": False,
    "license_sha256": None,
    "original_rvc_license_id": "MIT",
    "original_rvc_license_path": (
        "research/voice-conversion-eval-20261101/repos/rvc/LICENSE"),
    "original_rvc_license_sha256":
        "bec61ed1eb9a3748644ddbc50303aa6978e14eeaba46822e59a006c722b52585",
    "fork_license_covers_modifications": False,
    "project_version": "0.1.0",
    "present": True,
    "verified": True,
    "admitted": False,
    "model_executed": False,
    "weights_used": False,
    "present_components": ["source_code_checkout"],
    "absent_components": [
        "source_license_and_notice_bundle",
        "target_synth_weights_and_config",
        "contentvec_hubert_asset",
        "rmvpe_asset",
        "faiss_index",
        "installed_mlx_runtime",
        "realtime_run",
    ],
    "exact_source_weights_runtime_conjunction_present": False,
    "reason": (
        "The rvc-mlx-realtime checkout is present at the pinned revision, but "
        "it contains no LICENSE/NOTICE/COPYING file, no target or shared model "
        "weights, no MLX runtime, and no realtime run. Source bytes alone are "
        "not a license grant, a weight archive, an installed runtime or a "
        "qualified result."),
}

OBSERVED_TEST_AUDIO = {
    "path": SOURCE_ROOT + "/tests/data/voiced_test_16k.wav",
    "sha256": "473a66da3cd868ac612cd4609a28401563a7ac98ad49d238477a0c473b4ea664",
    "byte_count": 96044,
    "present": True,
    "admitted": False,
    "decoded": False,
    "signal_loaded": False,
    "used_for_evidence": False,
    "reason": (
        "This is an upstream test fixture inside the checkout. Only its file "
        "bytes are hashed as source provenance; it is not a rights-cleared "
        "corpus, not a target reference and not decoded or used."),
}

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "source_code_snapshot",
        "present": True,
        "verified": True,
        "blocked": False,
        "sha256": None,
        "revision": SOURCE_REVISION,
        "requirement": (
            "Exact upstream rvc-mlx-realtime source at a 40-hex revision with "
            "per-file SHA-256 pins, a tree digest and file count from a "
            "reviewable source root."),
    },
    {
        "id": "ART-02",
        "kind": "source_license_and_notice_bundle",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "A complete source license/notice bundle for the fork and its "
            "adapted Acelogic RVC-MLX, w-okada, Applio, ContentVec and RMVPE "
            "lineage, with an explicit reviewed redistribution and product-use "
            "decision. The checkout contains no license file."),
    },
    {
        "id": "ART-03",
        "kind": "weights_and_shared_assets_snapshot",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "The target RVC v2 40 kHz f0=rmvpe synthesizer weights and JSON "
            "config, the ContentVec/HuBERT and RMVPE base assets, and the "
            "optional FAISS index, each with byte count, SHA-256 and reviewed "
            "terms."),
    },
    {
        "id": "ART-04",
        "kind": "pinned_mlx_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "A reproducible isolated CPython 3.11 runtime with mlx 0.31.2, "
            "mlx-metal 0.31.2, numpy 1.26.4, scipy 1.17.1, faiss-cpu 1.7.4, "
            "sounddevice 0.5.5 and soxr 1.1.0 installed from the pinned lock, "
            "an install digest, working Metal device access, deterministic "
            "settings and an offline load path."),
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_realtime_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "A frozen rights-cleared realtime cohort with permitted input "
            "utterances, target references, consent and output-use records, "
            "language/speaker groups, noise/silence/unfamiliar conditions and "
            "identity, target and alternate-target controls."),
    },
    {
        "id": "ART-06",
        "kind": "quality_timing_and_listening_harness",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "An agreed Voice protocol that separately measures content "
            "preservation, target identity/similarity, naturalness, "
            "alignment, first-output/tail, peaks and nonfinite behavior, plus "
            "target-device paced timing, drop/deadline margins and independent "
            "listening."),
    },
    {
        "id": "ART-07",
        "kind": "provider_intake",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "A separate versioned OFF-by-default SDK provider intake with an "
            "exact asset descriptor, empty descriptor settings, no "
            "registry/default/shared-build change, clean-install proof and "
            "independent exact-head review."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "statement": (
            "The checkout has no LICENSE, NOTICE, COPYING or license "
            "declaration in README, pyproject.toml or source headers. The "
            "original RVC repository's MIT LICENSE is present and pinned, but "
            "MIT requires retaining its notice and does not by itself license "
            "this fork's modifications or the adapted Acelogic/w-okada code. "
            "No source or modification terms are staged or reviewed."),
        "required_action": (
            "Stage the complete source license/notice bundle for the fork and "
            "every adapted/vendored lineage, record an explicit reviewed "
            "redistribution and product-use decision, and pin the exact "
            "license files by SHA-256."),
        "linked_gates": ["RG-01", "RG-08"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "statement": (
            "No target synthesizer checkpoint (tomorin.pth or .npz plus .json "
            "weights), no ContentVec/HuBERT pytorch_model.bin, no RMVPE "
            "rmvpe.pt/.npz and no FAISS .index exists at any fixed probe. "
            "models/ contains only the 669-byte tomorin.json architecture "
            "config. The documented runtime fetches missing base assets from "
            "the network; nothing was downloaded."),
        "required_action": (
            "Supply the immutable target and shared asset snapshots with byte "
            "counts, SHA-256 digests, source revisions and reviewed weight and "
            "redistribution terms, including the optional FAISS index."),
        "linked_gates": ["RG-02", "RG-03"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "statement": (
            "No MLX runtime is installed: the selected CPython 3.11.5 "
            "interpreter cannot import mlx/mlx.core, and no pinned virtual "
            "environment exists. uv.lock pins mlx 0.31.2 / mlx-metal 0.31.2, "
            "but a lock file is not an installed runtime, install digest or "
            "verified Metal execution path."),
        "required_action": (
            "Supply a locked offline CPython 3.11 runtime installed from the "
            "pinned lock (mlx/mlx-metal 0.31.2, numpy 1.26.4, faiss-cpu 1.7.4, "
            "scipy 1.17.1, sounddevice 0.5.5, soxr 1.1.0), with wheel hashes, "
            "an install/import digest, working Metal device access and "
            "deterministic/offline settings."),
        "linked_gates": ["RG-03", "RG-07"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "statement": (
            "No rights-cleared input/target cohort exists. The historical RVC "
            "PyTorch file run used one LJ Speech utterance and a p360 reference "
            "whose dataset/license provenance the research record calls "
            "unconfirmed. The checkout's tests/data/voiced_test_16k.wav is an "
            "upstream fixture, not a licensed cohort."),
        "required_action": (
            "Supply a frozen rights-cleared cohort with permitted source "
            "utterances, target references, consent records, output-use terms, "
            "manual transcripts, language/speaker groups and matched controls."),
        "linked_gates": ["RG-04", "RG-05"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "statement": (
            "No realtime quality, alignment, first-output/tail, listening or "
            "device-timing result exists. The research record states the MLX "
            "microphone fork could not initialize on its host; the historical "
            "RVC run used the PyTorch file pipeline at RTF 0.804 and is "
            "provenance only. Repository performance figures are from an M5 "
            "MacBook Pro and were not reproduced here."),
        "required_action": (
            "Agree and staff separate content, identity, naturalness, "
            "listening, alignment, first-output/tail, peak/nonfinite and "
            "target-device paced deadline/resource protocols on the qualified "
            "cohort."),
        "linked_gates": ["RG-06", "RG-07"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "statement": (
            "No provider, descriptor, registry, default-selection, shared "
            "build or CI change exists, and no release decision is available. "
            "Source presence on another host is not provider evidence."),
        "required_action": (
            "Open a separate versioned OFF-by-default provider intake after "
            "every prior gate clears, with an exact asset descriptor, "
            "clean-install proof and independent exact-head review."),
        "linked_gates": ["RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_and_license_provenance",
        "statement": (
            "The exact upstream revision, tree digest and the complete "
            "license/notice provenance for the fork and adapted lineage are "
            "recorded before any implementation claim."),
        "reopen_condition": (
            "An immutable source archive at the pinned 40-hex revision, with "
            "the complete reviewed fork/adaptation license and notice bundle, "
            "is supplied and reviewed."),
    },
    {
        "id": "RG-02",
        "title": "weights_and_shared_assets_and_terms",
        "statement": (
            "Every synthesizer, ContentVec/HuBERT, RMVPE and optional FAISS "
            "asset is pinned by byte count and SHA-256 with reviewed terms."),
        "reopen_condition": (
            "The target and shared asset snapshots, per-file digests and "
            "weight/redistribution terms are supplied and reviewed."),
    },
    {
        "id": "RG-03",
        "title": "pinned_mlx_runtime_and_metal_load",
        "statement": (
            "A reproducible isolated MLX/Metal runtime loads the exact "
            "snapshot offline with deterministic settings and no implicit "
            "download."),
        "reopen_condition": (
            "A locked runtime with install digest loads the pinned assets "
            "offline on a recorded Metal device and host profile."),
    },
    {
        "id": "RG-04",
        "title": "reference_availability_and_output_use",
        "statement": (
            "Input and target-reference availability, consent and generated "
            "output use are independent, explicitly cleared gates."),
        "reopen_condition": (
            "Consent, reference availability and output-use terms are staged "
            "and reviewed for every source and target used."),
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_realtime_cohort",
        "statement": (
            "A frozen rights-cleared realtime cohort with transcripts, "
            "language/speaker groups, adverse conditions and matched controls "
            "exists before any result."),
        "reopen_condition": (
            "The immutable cohort, transcripts, groups, target conditions and "
            "identity/target/alternate-target controls are supplied."),
    },
    {
        "id": "RG-06",
        "title": "separate_content_identity_naturalness_and_listening",
        "statement": (
            "Content preservation, target identity/similarity and naturalness "
            "are measured as separate outcomes with independent listening."),
        "reopen_condition": (
            "Pinned scorers and an approved blinded listening protocol "
            "produce reviewed results on the frozen cohort."),
    },
    {
        "id": "RG-07",
        "title": "realtime_alignment_first_output_tail_peaks_and_resources",
        "statement": (
            "Realtime alignment, first-output/tail, SOLA joins, peaks, "
            "nonfinite behavior, block-budget margins, drops and resources "
            "are measured on the target device, not inferred."),
        "reopen_condition": (
            "Target-device paced runs record alignment, joins, first-output/"
            "tail, peaks, nonfinite behavior, CPU/memory and deadline margins "
            "for the declared block/extra/crossfade configuration."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "statement": (
            "Opt-in provider intake, an explicit public-surface decision, "
            "independent exact-head review and release approval are complete."),
        "reopen_condition": (
            "A separate versioned intake accepts the component with an OFF "
            "default and passes independent exact-head review."),
    },
)

VOICE_PROFILE_ROWS = (
    {
        "id": "V-01",
        "requirement": (
            "Freeze permitted input and target references, task and "
            "language/speaker groups."),
        "status": "blocked",
        "evidence": (
            "No rights-cleared source utterance, target reference, consent "
            "record, language/speaker group or frozen target condition is "
            "staged."),
    },
    {
        "id": "V-02",
        "requirement": "Preserve text and semantic content.",
        "status": "blocked",
        "evidence": (
            "The historical one-utterance Whisper Tiny WER 0.00% belongs to "
            "the PyTorch file pipeline; it is not a manual transcript, not "
            "rerun and not realtime evidence."),
    },
    {
        "id": "V-03",
        "requirement": (
            "Measure identity/similarity as a separate outcome."),
        "status": "blocked",
        "evidence": (
            "No target-similarity score, independent encoder or perceptual "
            "identity rating exists for this fork; the historical p226 "
            "speaker-id mapping is unverified."),
    },
    {
        "id": "V-04",
        "requirement": "Measure naturalness as a separate outcome.",
        "status": "blocked",
        "evidence": (
            "No naturalness rating, blinded listening or preference panel "
            "was run."),
    },
    {
        "id": "V-05",
        "requirement": "Record alignment.",
        "status": "blocked",
        "evidence": (
            "No sample, frame, phoneme or word alignment was measured for the "
            "realtime path; SOLA offsets were not observed."),
    },
    {
        "id": "V-06",
        "requirement": "Record first-output and tail timing.",
        "status": "blocked",
        "evidence": (
            "No microphone callback, block pacing, first-output, tail or "
            "drain measurement exists. Declared block/crossfade geometry in "
            "this package is arithmetic, not timing."),
    },
    {
        "id": "V-07",
        "requirement": "Record the exact target condition.",
        "status": "blocked",
        "evidence": (
            "No qualified target condition exists. The historical PyTorch run "
            "used one LJ Speech utterance and a p360 reference whose "
            "provenance is unconfirmed; the MLX realtime path never ran."),
    },
    {
        "id": "V-08",
        "requirement": (
            "Keep consent, reference availability and output use as "
            "independent gates."),
        "status": "blocked",
        "evidence": (
            "No consent, reference-availability or output-use record exists; "
            "the original RVC MIT license does not clear the fork, weights, "
            "reference speakers or generated output."),
    },
)

QUALITY_OUTCOME_ROWS = (
    {
        "id": "QO-01",
        "outcome": "text_and_semantic_preservation",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No manual transcript, semantic-content adjudication or "
            "reproduced content metric exists."),
    },
    {
        "id": "QO-02",
        "outcome": "target_identity_similarity",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No independent target-similarity score, encoder or human "
            "identity rating exists."),
    },
    {
        "id": "QO-03",
        "outcome": "naturalness",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No naturalness score or independent listening result exists."),
    },
    {
        "id": "QO-04",
        "outcome": "independent_listening",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No listening panel, protocol, panel size or preference result "
            "exists."),
    },
)

TIMING_ROWS = (
    {
        "id": "TM-01",
        "metric": "per_block_inference_ms",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No MLX inference ran. The repository's 60 ms fp32 / 53 ms fp16 "
            "figures are M5 MacBook Pro provenance, not reproduced here."),
    },
    {
        "id": "TM-02",
        "metric": "first_output_and_tail_ms",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No microphone/target-device run, first-output timestamp, tail or "
            "drain measurement exists."),
    },
    {
        "id": "TM-03",
        "metric": "sola_alignment_and_join_behavior",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No synthesized output, observed SOLA offset, join artifact or "
            "alignment measurement exists. The exact correlation reference "
            "here is synthetic arithmetic only."),
    },
    {
        "id": "TM-04",
        "metric": "device_deadline_drops_and_resources",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No callback, queue/drop, deadline-margin, CPU, memory, thermal "
            "or energy measurement exists; the declared 200 ms budget and "
            "bounded-backlog arithmetic are not measurements."),
    },
)

HISTORICAL_EXECUTION = {
    "id": "HE-1",
    "candidate": "tizee/rvc-mlx-realtime (RVC v2 40 kHz, f0=rmvpe)",
    "source": "research/voice-conversion-eval-20261101/README.md",
    "readme_sha256":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "metrics_path": (
        "research/voice-conversion-eval-20261101/results/rvc/metrics.json"),
    "metrics_sha256":
        "14fc2c08086efadea87ba5a254704e086c3c4c94831a82de8796184168918b36",
    "asr_path": (
        "research/voice-conversion-eval-20261101/results/rvc/asr.json"),
    "asr_sha256":
        "2d28a6e4e93e450bc7894e68881926bb315d73dd82cd08bd44e597f7d51fff24",
    "run_script_path": (
        "research/voice-conversion-eval-20261101/scripts/run_rvc_vctk_eval.py"),
    "run_script_sha256":
        "a8f66b2a5af368f4a0573e954022e17577e2d9f0c3778abb0a1a4e65c15877da",
    "realtime_fork_ran": False,
    "realtime_fork_blocker_recorded": (
        "The separate MLX microphone fork cannot initialize because this host "
        "exposes no Metal device."),
    "historical_path": "official RVC PyTorch file pipeline, CPU, 4 threads",
    "mlx_path_exercised": False,
    "checkpoint": "Mp226rmvpe.pth",
    "checkpoint_present": False,
    "index_used": False,
    "index_crash_recorded": True,
    "sample_rate_hz": 40000,
    "audio_seconds_decimal": "9.64",
    "load_seconds_decimal": "0.34603404195513576",
    "conversion_seconds_decimal": "7.748765500029549",
    "file_rtf_decimal": "0.8038138485507831",
    "wer_decimal": "0.0",
    "peak_abs_decimal": "0.497772216796875",
    "clipped_sample_fraction_decimal": "0.0",
    "speaker_mapping_verified": False,
    "first_output_latency_present": False,
    "device_timing_present": False,
    "listening_present": False,
    "not_rerun": True,
    "merged_task_evidence": False,
    "used_for_evidence": False,
    "qualifies": False,
    "limitations": [
        "The recorded run used the PyTorch RVC file pipeline, not this MLX "
        "realtime fork; it cannot be promoted to realtime evidence.",
        "The research record states the MLX microphone fork could not "
        "initialize on its host; the current host reports Apple M1 Metal 4 "
        "but MLX/MLX-Metal are not installed, so no runtime was exercised.",
        "File RTF 0.804 and one-utterance WER are not first-output latency, "
        "device timing, listening, naturalness or identity evidence.",
        "The checkpoint, HuBERT and RMVPE assets and the FAISS index are "
        "absent from every fixed probe; the checkpoint path in metrics.json "
        "does not exist.",
    ],
}

REPOSITORY_PERFORMANCE_RECORDED = {
    "host": "M5 MacBook Pro (repository README/docs, not this host)",
    "configuration": "block=200 ms, extra=300 ms, crossfade=60 ms",
    "realtime_infer_ms_fp32": 60,
    "realtime_infer_ms_fp16": 53,
    "offline_rtf_fp32_decimal": "0.13",
    "offline_rtf_fp16_decimal": "0.09",
    "per_block_budget_ms": 200,
    "reproduced_here": False,
    "used_for_evidence": False,
    "qualifies": False,
    "limitations": [
        "Repository-authored warm steady-state numbers on a different, faster "
        "host; no logs, counters, device or build digest are supplied.",
        "Per-block medians are documented as noisy; they are not a local "
        "deadline, first-output, tail, listening or release result.",
    ],
}

NON_CLAIMS = (
    "No RVC-MLX source copy, RVC checkpoint, MLX weight, ContentVec/HuBERT or "
    "RMVPE asset, FAISS index, runtime, captured audio, generated voice or "
    "vendor result is present, imported, loaded, linked or executed by this "
    "package.",
    "No model inference, audio read/write, voice conversion, SOLA join, "
    "listening, similarity, naturalness or content-preservation result is "
    "produced.",
    "No microphone/device callback, pacing, first-output, tail, drop, "
    "deadline, latency, CPU, memory or thermal measurement exists.",
    "The synthetic SOLA/correlation, block/queue and resampling arithmetic is "
    "a deterministic bookkeeping reference, not a signal renderer, model "
    "output or timing measurement.",
    "The historical PyTorch RVC file run and the repository-authored M5 "
    "performance figures are provenance only; neither is rerun, merged task "
    "evidence or a qualification.",
    "No provider is registered, exposed, enabled by default or selected as a "
    "descriptor default; no public API, ABI, registry, installed-v0, shared "
    "build or CI change is made.",
    "No missing, synthetic or schema-control result is promoted or treated as "
    "evidence for the candidate.",
    "The original RVC MIT license is not treated as a license for this fork's "
    "modifications, adapted code, weights or base assets.",
)

PROFILE_PHRASES = (
    "Freeze permitted input and target references, task and language/speaker "
    "groups.",
    "Preserve text and semantic content, identity/similarity and naturalness "
    "as separate outcomes.",
    "Record alignment, first-output/tail timing and the exact target "
    "condition.",
    "Consent, reference availability and output use are independent gates.",
)

# Admission manifest is a task-local schema, not an SDK, RVC-MLX or Voice
# contract. It admits metadata only and never reads audio or invokes a model.
MANIFEST_SCHEMA_ID = "audio-sdk/rvc-mlx-realtime-bundle/0.1"
MANIFEST_FIELDS = (
    "schema_id",
    "bundle_id",
    "source",
    "weights",
    "runtime",
    "realtime",
    "references",
    "outcomes",
    "rights",
)
SOURCE_FIELDS = ("revision", "path", "tree_sha256", "license_id",
                 "license_path", "license_sha256")
WEIGHT_FIELDS = ("name", "sha256", "byte_count", "terms_sha256")
RUNTIME_FIELDS = (
    "python_version",
    "mlx_version",
    "mlx_metal_version",
    "numpy_version",
    "faiss_version",
    "scipy_version",
    "sounddevice_version",
    "soxr_version",
    "device",
    "metal_available",
    "offline",
    "deterministic",
)
REALTIME_FIELDS = (
    "block_ms",
    "crossfade_ms",
    "extra_ms",
    "sola_search_ms",
    "input_sample_rate_hz",
    "target_sample_rate_hz",
    "queue_capacity",
    "ring_blocks",
    "block_samples",
    "convert_samples",
    "target_block_samples",
    "declared_buffering_samples",
    "budget_ms",
)
REFERENCE_FIELDS = ("id", "path", "sha256", "consent_id", "rights_reference",
                    "language", "speaker_group", "role")
REFERENCE_ROLES = ("source", "target")
OUTCOME_FIELDS = (
    "content_wer",
    "identity_similarity_cosine",
    "naturalness_mos",
    "alignment_samples",
    "first_output_ms",
    "tail_ms",
    "peak_abs",
    "clipped_fraction",
    "nonfinite_count",
    "sample_count",
)
RIGHTS_FIELDS = (
    "consent_reference",
    "reference_availability",
    "output_use",
    "terms_review",
    "listening_protocol",
    "listening_panel_size",
    "claims_qualified",
)
REQUIRED_WEIGHTS = ("synth_weights", "synth_config", "hubert", "rmvpe")
OPTIONAL_WEIGHTS = ("faiss_index",)
MAX_WEIGHT_BYTES = 4 * 1024 * 1024 * 1024
MAX_TEXT_LENGTH = 4096
MAX_ALIGNMENT_SAMPLES = 96000
MAX_PEAK = 4.0
MAX_SAMPLE_COUNT = 1000000000
MAX_PANEL = 1000
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PYTHON_VERSION = re.compile(r"^3\.11\.[0-9]+$")
LANGUAGE = re.compile(r"^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?$")
WEIGHT_NAME = re.compile(r"^[a-z0-9][a-z0-9._/-]{0,127}$")
EXACT_RUNTIME = {
    "mlx_version": "0.31.2",
    "mlx_metal_version": "0.31.2",
    "numpy_version": "1.26.4",
    "faiss_version": "1.7.4",
    "scipy_version": "1.17.1",
    "sounddevice_version": "0.5.5",
    "soxr_version": "1.1.0",
}


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


def _no_floats(value: Any, path: str = "") -> None:
    if isinstance(value, float):
        raise ValueError("float_in_canonical_report:" + (path or "<root>"))
    if isinstance(value, dict):
        for key in sorted(value):
            _no_floats(value[key], (path + "." + str(key)).lstrip("."))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _no_floats(item, f"{path}[{index}]")


# --------------------------------------------------------------------------
# Pins, board identity, source tree and absence probes
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


def source_tree_fingerprint(source_root: Path) -> dict:
    """Recompute the exact non-.git source tree fingerprint."""
    rows: list[tuple[str, str, int]] = []
    root = Path(source_root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name != ".git")
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.is_symlink() or not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            rows.append((relative, sha256_file(path), path.stat().st_size))
    rows.sort()
    payload = "".join(f"{relative}\0{digest}\n"
                      for relative, digest, _ in rows).encode("utf-8")
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "file_count": len(rows),
        "byte_count": sum(size for _, _, size in rows),
    }


def verify_source_tree(source_root: Path) -> dict:
    observed = source_tree_fingerprint(source_root)
    expected = {
        "sha256": SOURCE_TREE_SHA256,
        "file_count": SOURCE_TREE_FILE_COUNT,
        "byte_count": SOURCE_TREE_BYTE_COUNT,
    }
    if observed != expected:
        raise ValueError("source_tree_mismatch")
    return observed


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


def home_absence_probes(probes: tuple[str, ...] = HOME_ABSENCE_PROBES) -> list[dict]:
    rows: list[dict] = []
    home = Path.home()
    for relative in probes:
        path = home / relative[2:] if relative.startswith("~/") else Path(relative)
        if path.exists():
            raise ValueError("artifact_present_reopen_required:" + relative)
        rows.append({"path": relative, "searched_home_cache": True,
                     "present": False})
    return rows


def runtime_module_probe() -> dict:
    """Fail closed if the exact MLX runtime becomes importable elsewhere.

    Only the top-level `mlx` package is probed. The captured interpreter is the
    one running this standard-library-only module; no module is imported.
    """
    import importlib.util

    importable = importlib.util.find_spec("mlx") is not None
    if importable:
        raise ValueError("mlx_runtime_present_reopen_required")
    return {
        "module": "mlx",
        "importable": False,
        "import_attempted": False,
        "runtime_invoked": False,
        "note": (
            "`find_spec` only; no MLX module, Metal device or model was "
            "imported or executed."),
    }


def absence_summary(rows: list[dict], home_rows: list[dict]) -> dict:
    all_rows = rows + home_rows
    return {
        "probe_count": len(all_rows),
        "workspace_probe_count": len(rows),
        "home_probe_count": len(home_rows),
        "present_count": sum(1 for row in all_rows if row["present"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "all_probes_absent": all(not row["present"] for row in all_rows),
    }


# --------------------------------------------------------------------------
# Deterministic realtime arithmetic reference (no audio, no model)
# --------------------------------------------------------------------------
def _exact_ms_samples(milliseconds: int, sample_rate: int) -> int:
    """Exact integer sample count for a whole-millisecond setting."""
    if type(milliseconds) is not int or milliseconds < 0:
        raise ValueError("invalid_milliseconds")
    value = Fraction(milliseconds * sample_rate, 1000)
    if value.denominator != 1:
        raise ValueError("non_integral_sample_count")
    return value.numerator


def realtime_geometry() -> dict:
    block = _exact_ms_samples(BLOCK_MS, INPUT_SAMPLE_RATE)
    crossfade = _exact_ms_samples(CROSSFADE_MS, INPUT_SAMPLE_RATE)
    extra = _exact_ms_samples(EXTRA_MS, INPUT_SAMPLE_RATE)
    search = _exact_ms_samples(SOLA_SEARCH_MS, INPUT_SAMPLE_RATE)
    convert = block + crossfade + search + extra
    up = Fraction(MODEL_SAMPLE_RATE, INPUT_SAMPLE_RATE)
    target_block = int(block * up)
    target_crossfade = int(crossfade * up)
    target_search = int(search * up)
    need = target_block + target_crossfade + target_search
    buffering = block + crossfade
    ring_cap = RING_BLOCKS * target_block
    backlog_blocks = QUEUE_CAPACITY + RING_BLOCKS
    return {
        "input_sample_rate_hz": INPUT_SAMPLE_RATE,
        "target_sample_rate_hz": MODEL_SAMPLE_RATE,
        "hop_samples": HUBERT_HOP,
        "block_ms": BLOCK_MS,
        "crossfade_ms": CROSSFADE_MS,
        "extra_ms": EXTRA_MS,
        "sola_search_ms": SOLA_SEARCH_MS,
        "block_samples": block,
        "crossfade_samples": crossfade,
        "extra_samples": extra,
        "sola_search_samples": search,
        "convert_samples": convert,
        "convert_ms": convert * 1000 // INPUT_SAMPLE_RATE,
        "upsample_numerator": up.numerator,
        "upsample_denominator": up.denominator,
        "target_block_samples": target_block,
        "target_crossfade_samples": target_crossfade,
        "target_search_samples": target_search,
        "sola_need_samples": need,
        "sola_candidate_count": target_search + 1,
        "declared_buffering_samples": buffering,
        "declared_buffering_seconds": str(
            Fraction(buffering, INPUT_SAMPLE_RATE)),
        "budget_ms": BLOCK_MS,
        "queue_capacity": QUEUE_CAPACITY,
        "ring_blocks": RING_BLOCKS,
        "ring_capacity_samples": ring_cap,
        "bounded_backlog_blocks": backlog_blocks,
        "bounded_backlog_ms": backlog_blocks * BLOCK_MS,
        "emitted_samples_per_block": target_block,
        "output_blocks_per_input_block": 1,
    }


def _check(condition: bool, name: str) -> dict:
    return {"check": name, "pass": bool(condition)}


def geometry_reference() -> dict:
    """Prove the documented integer geometry and its derived relations."""
    g = realtime_geometry()
    checks = [
        _check(g["block_samples"] == 3200, "block_is_3200"),
        _check(g["crossfade_samples"] == 960, "crossfade_is_960"),
        _check(g["extra_samples"] == 4800, "extra_is_4800"),
        _check(g["sola_search_samples"] == 192, "search_is_192"),
        _check(g["convert_samples"] == 9152, "convert_window_is_9152"),
        _check(g["convert_samples"] ==
               g["block_samples"] + g["crossfade_samples"] +
               g["sola_search_samples"] + g["extra_samples"],
               "convert_window_is_sum"),
        _check(g["target_block_samples"] == 8000, "target_block_is_8000"),
        _check(g["target_crossfade_samples"] == 2400,
               "target_crossfade_is_2400"),
        _check(g["target_search_samples"] == 480, "target_search_is_480"),
        _check(g["sola_need_samples"] == 10880, "sola_need_is_10880"),
        _check(g["sola_candidate_count"] == 481, "sola_candidates_is_481"),
        _check(g["declared_buffering_samples"] == 4160,
               "declared_buffering_is_4160"),
        _check(g["declared_buffering_seconds"] == "13/50",
               "declared_buffering_is_0_26s"),
        _check(g["budget_ms"] == 200, "budget_is_200ms"),
        _check(g["ring_capacity_samples"] == 32000, "ring_capacity_is_32000"),
        _check(g["bounded_backlog_ms"] == 1200, "backlog_bound_is_1200ms"),
    ]
    return {
        "kind": "declared_configuration_arithmetic_not_measurement",
        "geometry": g,
        "checks": checks,
        "all_checks_pass": all(row["pass"] for row in checks),
        "audio_read": False,
        "model_executed": False,
        "measured": False,
        "qualifies": False,
    }


def resample_reference() -> dict:
    """Exact device-rate to 16 kHz / 40 kHz to device-rate geometry."""
    rows = []
    for device_rate in (44100, 48000, 96000, 192000):
        divisor = math.gcd(INPUT_SAMPLE_RATE, device_rate)
        up_num = device_rate // divisor
        down_den = INPUT_SAMPLE_RATE // divisor
        block_dev = int(Fraction(3200 * device_rate, INPUT_SAMPLE_RATE))
        out_divisor = math.gcd(MODEL_SAMPLE_RATE, device_rate)
        out_num = device_rate // out_divisor
        out_den = MODEL_SAMPLE_RATE // out_divisor
        out_block_dev = int(Fraction(8000 * device_rate, MODEL_SAMPLE_RATE))
        rows.append({
            "device_sample_rate_hz": device_rate,
            "input_resample_num": up_num,
            "input_resample_den": down_den,
            "device_block_samples": block_dev,
            "output_resample_num": out_num,
            "output_resample_den": out_den,
            "device_output_block_samples": out_block_dev,
            "exact": (3200 * device_rate) % INPUT_SAMPLE_RATE == 0 and
                     (8000 * device_rate) % MODEL_SAMPLE_RATE == 0,
        })
    expected = {44100: (441, 160, 8820, 441, 400, 8820),
                48000: (3, 1, 9600, 6, 5, 9600),
                96000: (6, 1, 19200, 12, 5, 19200),
                192000: (12, 1, 38400, 24, 5, 38400)}
    checks = []
    for row in rows:
        key = row["device_sample_rate_hz"]
        got = (row["input_resample_num"], row["input_resample_den"],
               row["device_block_samples"], row["output_resample_num"],
               row["output_resample_den"], row["device_output_block_samples"])
        checks.append(_check(got == expected[key],
                             f"device_rate_{key}_ratios"))
        checks.append(_check(row["exact"], f"device_rate_{key}_exact"))
    return {
        "kind": "rational_resampling_arithmetic_not_signal_processing",
        "rows": rows,
        "checks": checks,
        "all_checks_pass": all(row["pass"] for row in checks),
        "audio_read": False,
        "resampler_invoked": False,
        "qualifies": False,
    }


def _lcg_signal(length: int, seed: int = 20261126) -> list[int]:
    """Deterministic integer signal; no random module and no audio."""
    state = seed & 0xFFFFFFFF
    values = []
    for _ in range(length):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append(((state >> 8) % 2001) - 1000)
    return values


def exact_lag_search(previous_tail: list[int], window: list[int],
                     search: int) -> dict:
    """Exact integer SOLA alignment over candidate offsets 0..search.

    Compares squared cross-correlation / window energy as exact Fractions,
    after requiring a nonnegative numerator. This models the documented
    argmax over normalized cross-correlation without floating point and
    without the runtime's `1e-3` denominator guard. It is an algorithm
    reference only; it does not render or measure audio.
    """
    if search < 0 or len(window) != len(previous_tail) + search:
        raise ValueError("invalid_sola_geometry")
    candidates = []
    for lag in range(search + 1):
        segment = window[lag:lag + len(previous_tail)]
        numerator = sum(a * b for a, b in zip(segment, previous_tail))
        energy = sum(b * b for b in segment)
        if energy == 0:
            score = None
        elif numerator <= 0:
            score = Fraction(0, 1)
        else:
            score = Fraction(numerator * numerator, energy)
        candidates.append({"lag": lag, "numerator": numerator,
                           "energy": energy,
                           "score": None if score is None else str(score)})
    scored = [row for row in candidates if row["score"] is not None]
    if not scored:
        raise ValueError("all_candidate_energies_zero")
    best = max(scored, key=lambda row: (Fraction(row["score"]),
                                        -row["lag"]))
    return {
        "candidate_count": len(candidates),
        "best_lag": best["lag"],
        "best_score": best["score"],
        "candidates": candidates,
    }


def sola_reference() -> dict:
    """Recover a known synthetic shift exactly for representative lags."""
    crossfade = 64
    search = 24
    tail = _lcg_signal(crossfade, seed=7)
    cases = []
    for lag in (0, 7, 12, search):
        window = [0] * lag + tail + [0] * (search - lag)
        result = exact_lag_search(tail, window, search)
        cases.append({
            "injected_lag": lag,
            "recovered_lag": result["best_lag"],
            "candidate_count": result["candidate_count"],
            "unique_match": result["best_lag"] == lag,
            "best_score": result["best_score"],
        })
    checks = [
        _check(row["unique_match"], f"recover_lag_{row['injected_lag']}")
        for row in cases
    ]
    checks.append(_check(all(row["candidate_count"] == search + 1
                             for row in cases),
                         "candidate_count_is_search_plus_one"))
    return {
        "kind": "synthetic_integer_cross_correlation_reference_not_audio",
        "crossfade_samples": crossfade,
        "search_samples": search,
        "padding_guard_epsilon_modeled": False,
        "float_path_used": False,
        "cases": cases,
        "checks": checks,
        "all_checks_pass": all(row["pass"] for row in checks),
        "audio_read": False,
        "signal_rendered": False,
        "qualifies": False,
    }


def bounded_backlog_reference() -> dict:
    """Exact block accounting for the declared queues and ring cap.

    Models the controller's declared bounds only: two queued blocks per queue
    and a four-block output ring truncation. It is not a scheduler, thread or
    device simulation.
    """
    block = 8000
    queue = QUEUE_CAPACITY
    ring = RING_BLOCKS
    retained = queue + ring
    rows = []
    for produced in range(0, 11):
        queued = min(produced, queue)
        emitted = max(0, produced - retained)
        backlog = min(retained, produced) * block
        rows.append({"produced_blocks": produced,
                     "queued_or_ring_blocks": min(retained, produced),
                     "emitted_blocks": emitted,
                     "retained_samples": backlog,
                     "bounded": backlog <= retained * block})
    checks = [
        _check(all(row["bounded"] for row in rows),
               "retained_never_exceeds_bound"),
        _check(retained * block == 48000, "retained_bound_is_48000_samples"),
        _check(retained * BLOCK_MS == 1200, "retained_bound_is_1200ms"),
        _check(max(row["emitted_blocks"] for row in rows) == 4,
               "ten_produced_blocks_emit_four"),
        _check(all(row["queued_or_ring_blocks"] + row["emitted_blocks"] ==
                   row["produced_blocks"] for row in rows),
               "produced_equals_retained_plus_emitted"),
    ]
    return {
        "kind": "declared_bounded_queue_accounting_not_scheduling",
        "block_samples": block,
        "queue_capacity_blocks": queue,
        "ring_blocks": ring,
        "retained_bound_blocks": retained,
        "retained_bound_samples": retained * block,
        "retained_bound_ms": retained * BLOCK_MS,
        "rows": rows,
        "checks": checks,
        "all_checks_pass": all(row["pass"] for row in checks),
        "threads_started": False,
        "callback_invoked": False,
        "qualifies": False,
    }


def source_declaration_checks() -> dict:
    """Check the pinned source bytes declare the modelled configuration."""
    stream = (AUDIO_ROOT / SOURCE_ROOT /
              "rvc_mlx_rt/realtime/stream.py").read_text(encoding="utf-8")
    controller = (AUDIO_ROOT / SOURCE_ROOT /
                  "rvc_mlx_rt/realtime/controller.py").read_text(encoding="utf-8")
    cli = (AUDIO_ROOT / SOURCE_ROOT /
           "rvc_mlx_rt/realtime/run.py").read_text(encoding="utf-8")
    requirements = (
        (stream, "block_ms: float = 250.0", "stream_block_default"),
        (stream, "crossfade_ms: float = 80.0", "stream_crossfade_default"),
        (stream, "extra_ms: float = 300.0", "stream_extra_default"),
        (stream, "sola_search_ms: float = 12.0", "stream_search_default"),
        (stream, "convert_size = self.block + self.crossfade + "
                 "self.sola_search + self.extra", "convert_size_formula"),
        (stream, "self.up = self.tgt_sr / self.sr", "upsample_ratio"),
        (stream, "np.argmax(cor_nom / cor_den)", "argmax_alignment"),
        (controller, "block_ms: float = 200.0", "controller_block_default"),
        (controller, "crossfade_ms: float = 60.0",
         "controller_crossfade_default"),
        (controller, "extra_ms: float = 300.0", "controller_extra_default"),
        (controller, "queue.Queue(maxsize=2)", "queue_capacity_two"),
        (controller, "max_ring = block_out_dev * 4", "ring_four_blocks"),
        (cli, '"--block-ms", dest="block_ms", type=float, default=200.0',
         "cli_block_default"),
        (cli, '"--crossfade-ms", dest="crossfade_ms", type=float, '
              'default=60.0', "cli_crossfade_default"),
        (cli, '"--extra-ms", dest="extra_ms", type=float, default=300.0',
         "cli_extra_default"),
    )
    checks = [_check(token in text, name)
              for text, token, name in requirements]
    return {
        "kind": "pinned_source_declaration_check_not_execution",
        "checks": checks,
        "all_checks_pass": all(row["pass"] for row in checks),
        "source_imported": False,
        "executed": False,
    }


def arithmetic_reference() -> dict:
    geometry = geometry_reference()
    resample = resample_reference()
    sola = sola_reference()
    backlog = bounded_backlog_reference()
    declarations = source_declaration_checks()
    parts = (geometry, resample, sola, backlog, declarations)
    return {
        "kind": "standard_library_deterministic_reference",
        "geometry": geometry,
        "resampling": resample,
        "sola": sola,
        "bounded_backlog": backlog,
        "source_declarations": declarations,
        "all_checks_pass": all(part["all_checks_pass"] for part in parts),
        "audio_read": False,
        "model_executed": False,
        "runtime_invoked": False,
        "device_timing_measured": False,
        "qualifies": False,
    }


# --------------------------------------------------------------------------
# Admission validator (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return (isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value)))


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
            found = _nonfinite_path(value[key], (path + "." + str(key)).lstrip("."))
            if found:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = _nonfinite_path(item, f"{path}[{index}]")
            if found:
                return found
    return None


def _path_is_canonical(value: Any) -> bool:
    if not isinstance(value, str) or not value or len(value) > 1024:
        return False
    if value.startswith("/") or "\\" in value or ".." in value.split("/"):
        return False
    return all(part not in ("", ".") for part in value.split("/"))


def _exact_object(value: Any, fields: tuple[str, ...]) -> str:
    if not isinstance(value, dict):
        return "not_object"
    if set(value) != set(fields):
        missing = sorted(set(fields) - set(value))
        extra = sorted(set(value) - set(fields))
        return "fields:" + (missing[0] if missing else extra[0])
    return ""


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX64.fullmatch(value))


def _text(value: Any, limit: int = 200) -> bool:
    return (isinstance(value, str) and 0 < len(value) <= limit
            and value.strip() == value)


def _slug(value: Any) -> bool:
    return isinstance(value, str) and bool(SLUG.fullmatch(value))


def _weight_name(value: Any) -> bool:
    return isinstance(value, str) and bool(WEIGHT_NAME.fullmatch(value))


def _derived_realtime(value: dict) -> dict | None:
    try:
        block_ms = value["block_ms"]
        crossfade_ms = value["crossfade_ms"]
        extra_ms = value["extra_ms"]
        search_ms = value["sola_search_ms"]
        in_rate = value["input_sample_rate_hz"]
        out_rate = value["target_sample_rate_hz"]
        if not all(_is_int(item) for item in
                   (block_ms, crossfade_ms, extra_ms, search_ms, in_rate,
                    out_rate)):
            return None
        block = _exact_ms_samples(block_ms, in_rate)
        crossfade = _exact_ms_samples(crossfade_ms, in_rate)
        extra = _exact_ms_samples(extra_ms, in_rate)
        search = _exact_ms_samples(search_ms, in_rate)
        up = Fraction(out_rate, in_rate)
        target_block_fraction = block * up
        if target_block_fraction.denominator != 1:
            return None
        target_block = target_block_fraction.numerator
        return {
            "block_samples": block,
            "convert_samples": block + crossfade + search + extra,
            "target_block_samples": target_block,
            "declared_buffering_samples": block + crossfade,
            "budget_ms": block_ms,
        }
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed admission for a caller-supplied realtime bundle.

    This validates metadata only. It never reads audio, weights, an index or a
    model, and it never invokes the runtime. A successful validation is not a
    qualified result: `rights.claims_qualified` must stay false.
    """
    if not isinstance(document, dict):
        return _reject("manifest_not_object")
    nonfinite = _nonfinite_path(document)
    if nonfinite:
        return _reject("nonfinite_value", nonfinite)
    problem = _exact_object(document, MANIFEST_FIELDS)
    if problem:
        return _reject("manifest_" + problem, problem.split(":")[-1])
    if document["schema_id"] != MANIFEST_SCHEMA_ID:
        return _reject("schema_id", "schema_id")
    if not _slug(document["bundle_id"]):
        return _reject("bundle_id", "bundle_id")

    source = document["source"]
    problem = _exact_object(source, SOURCE_FIELDS)
    if problem:
        return _reject("source_" + problem, "source")
    if source["revision"] != SOURCE_REVISION:
        return _reject("source_revision", "source.revision")
    if source["tree_sha256"] != SOURCE_TREE_SHA256:
        return _reject("source_tree", "source.tree_sha256")
    if not _path_is_canonical(source["path"]):
        return _reject("source_path", "source.path")
    if source["license_id"] not in ("MIT", "Apache-2.0", "BSD-3-Clause"):
        return _reject("source_license_id", "source.license_id")
    if not _path_is_canonical(source["license_path"]):
        return _reject("source_license_path", "source.license_path")
    if not _sha(source["license_sha256"]):
        return _reject("source_license_sha", "source.license_sha256")

    weights = document["weights"]
    if not isinstance(weights, list) or not weights:
        return _reject("weights_not_list", "weights")
    names: set[str] = set()
    digests: set[str] = set()
    for index, weight in enumerate(weights):
        problem = _exact_object(weight, WEIGHT_FIELDS)
        if problem:
            return _reject("weights_" + problem, f"weights[{index}]")
        if not _weight_name(weight["name"]):
            return _reject("weight_name", f"weights[{index}].name")
        if weight["name"] in names:
            return _reject("weight_duplicate", weight["name"])
        names.add(weight["name"])
        if not _sha(weight["sha256"]):
            return _reject("weight_sha", f"weights[{index}].sha256")
        if weight["sha256"] in digests:
            return _reject("weight_digest_duplicate", weight["sha256"])
        digests.add(weight["sha256"])
        if not _is_int(weight["byte_count"]) or not (
                0 < weight["byte_count"] <= MAX_WEIGHT_BYTES):
            return _reject("weight_bytes", f"weights[{index}].byte_count")
        if not _sha(weight["terms_sha256"]):
            return _reject("weight_terms", f"weights[{index}].terms_sha256")
    if not set(REQUIRED_WEIGHTS) <= names:
        missing = sorted(set(REQUIRED_WEIGHTS) - names)
        return _reject("weight_required", missing[0])
    if not names <= set(REQUIRED_WEIGHTS) | set(OPTIONAL_WEIGHTS):
        extra = sorted(names - set(REQUIRED_WEIGHTS) - set(OPTIONAL_WEIGHTS))
        return _reject("weight_unknown", extra[0])

    runtime = document["runtime"]
    problem = _exact_object(runtime, RUNTIME_FIELDS)
    if problem:
        return _reject("runtime_" + problem, "runtime")
    if not isinstance(runtime["python_version"], str) or not \
            PYTHON_VERSION.fullmatch(runtime["python_version"]):
        return _reject("runtime_python", "runtime.python_version")
    for field, expected in EXACT_RUNTIME.items():
        if runtime[field] != expected:
            return _reject("runtime_" + field, "runtime." + field)
    if runtime["device"] != "metal":
        return _reject("runtime_device", "runtime.device")
    for field in ("metal_available", "offline", "deterministic"):
        if runtime[field] is not True:
            return _reject("runtime_" + field, "runtime." + field)

    realtime = document["realtime"]
    problem = _exact_object(realtime, REALTIME_FIELDS)
    if problem:
        return _reject("realtime_" + problem, "realtime")
    derived = _derived_realtime(realtime)
    if derived is None:
        return _reject("realtime_geometry", "realtime")
    if realtime["input_sample_rate_hz"] != INPUT_SAMPLE_RATE:
        return _reject("realtime_input_rate", "realtime.input_sample_rate_hz")
    if realtime["target_sample_rate_hz"] != MODEL_SAMPLE_RATE:
        return _reject("realtime_target_rate",
                       "realtime.target_sample_rate_hz")
    if realtime["block_ms"] != BLOCK_MS or \
            realtime["crossfade_ms"] != CROSSFADE_MS or \
            realtime["extra_ms"] != EXTRA_MS or \
            realtime["sola_search_ms"] != SOLA_SEARCH_MS:
        return _reject("realtime_defaults", "realtime")
    if realtime["queue_capacity"] != QUEUE_CAPACITY or \
            realtime["ring_blocks"] != RING_BLOCKS:
        return _reject("realtime_bounds", "realtime")
    for field in ("block_samples", "convert_samples", "target_block_samples",
                  "declared_buffering_samples", "budget_ms"):
        if realtime[field] != derived[field]:
            return _reject("realtime_derived:" + field, "realtime." + field)

    references = document["references"]
    if not isinstance(references, list) or len(references) != 2:
        return _reject("references_count", "references")
    roles = set()
    reference_digests = set()
    reference_ids = set()
    for index, reference in enumerate(references):
        problem = _exact_object(reference, REFERENCE_FIELDS)
        if problem:
            return _reject("reference_" + problem, f"references[{index}]")
        if not _slug(reference["id"]) or reference["id"] in reference_ids:
            return _reject("reference_id", f"references[{index}].id")
        reference_ids.add(reference["id"])
        if reference["role"] not in REFERENCE_ROLES or \
                reference["role"] in roles:
            return _reject("reference_role", f"references[{index}].role")
        roles.add(reference["role"])
        if not _path_is_canonical(reference["path"]):
            return _reject("reference_path", f"references[{index}].path")
        if not _sha(reference["sha256"]) or \
                reference["sha256"] in reference_digests:
            return _reject("reference_sha", f"references[{index}].sha256")
        reference_digests.add(reference["sha256"])
        for field in ("consent_id", "rights_reference"):
            if not _text(reference[field], MAX_TEXT_LENGTH):
                return _reject("reference_" + field,
                               f"references[{index}].{field}")
        if not isinstance(reference["language"], str) or not \
                LANGUAGE.fullmatch(reference["language"]):
            return _reject("reference_language",
                           f"references[{index}].language")
        if not _text(reference["speaker_group"], MAX_TEXT_LENGTH):
            return _reject("reference_speaker_group",
                           f"references[{index}].speaker_group")
    if roles != set(REFERENCE_ROLES):
        return _reject("reference_roles", "references")

    outcomes = document["outcomes"]
    problem = _exact_object(outcomes, OUTCOME_FIELDS)
    if problem:
        return _reject("outcomes_" + problem, "outcomes")
    for field in OUTCOME_FIELDS:
        if not _is_number(outcomes[field]):
            return _reject("outcome_nonfinite:" + field, "outcomes." + field)
    if not 0.0 <= float(outcomes["content_wer"]) <= 1.0:
        return _reject("outcome_range:content_wer", "outcomes.content_wer")
    if not -1.0 <= float(outcomes["identity_similarity_cosine"]) <= 1.0:
        return _reject("outcome_range:identity",
                       "outcomes.identity_similarity_cosine")
    if not 1.0 <= float(outcomes["naturalness_mos"]) <= 5.0:
        return _reject("outcome_range:naturalness", "outcomes.naturalness_mos")
    if not _is_int(outcomes["alignment_samples"]) or not (
            -MAX_ALIGNMENT_SAMPLES <= outcomes["alignment_samples"] <=
            MAX_ALIGNMENT_SAMPLES):
        return _reject("outcome_alignment", "outcomes.alignment_samples")
    for field in ("first_output_ms", "tail_ms"):
        if not _is_number(outcomes[field]) or not (
                0.0 <= float(outcomes[field]) <= 10000.0):
            return _reject("outcome_range:" + field, "outcomes." + field)
    if not _is_number(outcomes["peak_abs"]) or not (
            0.0 <= float(outcomes["peak_abs"]) <= MAX_PEAK):
        return _reject("outcome_peak", "outcomes.peak_abs")
    if not _is_number(outcomes["clipped_fraction"]) or not (
            0.0 <= float(outcomes["clipped_fraction"]) <= 1.0):
        return _reject("outcome_clip", "outcomes.clipped_fraction")
    if not _is_int(outcomes["nonfinite_count"]) or \
            outcomes["nonfinite_count"] != 0:
        return _reject("outcome_nonfinite_count",
                       "outcomes.nonfinite_count")
    if not _is_int(outcomes["sample_count"]) or not (
            0 < outcomes["sample_count"] <= MAX_SAMPLE_COUNT):
        return _reject("outcome_sample_count", "outcomes.sample_count")

    rights = document["rights"]
    problem = _exact_object(rights, RIGHTS_FIELDS)
    if problem:
        return _reject("rights_" + problem, "rights")
    for field in ("consent_reference", "reference_availability",
                  "output_use", "terms_review", "listening_protocol"):
        if not _text(rights[field], MAX_TEXT_LENGTH):
            return _reject("rights_" + field, "rights." + field)
    if not _is_int(rights["listening_panel_size"]) or not (
            0 <= rights["listening_panel_size"] <= MAX_PANEL):
        return _reject("rights_panel", "rights.listening_panel_size")
    if rights["claims_qualified"] is not False:
        return _reject("rights_claims_qualified", "rights.claims_qualified")

    if probe_paths:
        for reference in references:
            if not (AUDIO_ROOT / reference["path"]).is_file():
                return _reject("reference_missing", reference["path"])
        if not (AUDIO_ROOT / source["license_path"]).is_file():
            return _reject("license_missing", source["license_path"])

    checks = (
        len(MANIFEST_FIELDS) + len(SOURCE_FIELDS) +
        len(weights) * len(WEIGHT_FIELDS) + len(RUNTIME_FIELDS) +
        len(REALTIME_FIELDS) + len(references) * len(REFERENCE_FIELDS) +
        len(OUTCOME_FIELDS) + len(RIGHTS_FIELDS) + 3)
    return _accept(checks)


def _synthetic_bundle() -> dict:
    """A schema-shaped control. It is never evidence and never qualifies."""
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "bundle_id": "synthetic-schema-control",
        "source": {
            "revision": SOURCE_REVISION,
            "path": "synthetic/rvc-mlx-realtime-source",
            "tree_sha256": SOURCE_TREE_SHA256,
            "license_id": "MIT",
            "license_path": "synthetic/LICENSE",
            "license_sha256": "1" * 64,
        },
        "weights": [
            {"name": "synth_weights", "sha256": "2" * 64,
             "byte_count": 60_000_000, "terms_sha256": "3" * 64},
            {"name": "synth_config", "sha256": "4" * 64,
             "byte_count": 669, "terms_sha256": "3" * 64},
            {"name": "hubert", "sha256": "5" * 64,
             "byte_count": 190_000_000, "terms_sha256": "3" * 64},
            {"name": "rmvpe", "sha256": "6" * 64,
             "byte_count": 180_000_000, "terms_sha256": "3" * 64},
        ],
        "runtime": {
            "python_version": "3.11.5",
            "mlx_version": "0.31.2",
            "mlx_metal_version": "0.31.2",
            "numpy_version": "1.26.4",
            "faiss_version": "1.7.4",
            "scipy_version": "1.17.1",
            "sounddevice_version": "0.5.5",
            "soxr_version": "1.1.0",
            "device": "metal",
            "metal_available": True,
            "offline": True,
            "deterministic": True,
        },
        "realtime": {
            "block_ms": BLOCK_MS,
            "crossfade_ms": CROSSFADE_MS,
            "extra_ms": EXTRA_MS,
            "sola_search_ms": SOLA_SEARCH_MS,
            "input_sample_rate_hz": INPUT_SAMPLE_RATE,
            "target_sample_rate_hz": MODEL_SAMPLE_RATE,
            "queue_capacity": QUEUE_CAPACITY,
            "ring_blocks": RING_BLOCKS,
            "block_samples": 3200,
            "convert_samples": 9152,
            "target_block_samples": 8000,
            "declared_buffering_samples": 4160,
            "budget_ms": 200,
        },
        "references": [
            {"id": "source-utterance", "path": "synthetic/source.wav",
             "sha256": "7" * 64, "consent_id": "synthetic-consent",
             "rights_reference": "synthetic-rights", "language": "en",
             "speaker_group": "synthetic-source", "role": "source"},
            {"id": "target-speaker", "path": "synthetic/target.wav",
             "sha256": "8" * 64, "consent_id": "synthetic-consent",
             "rights_reference": "synthetic-rights", "language": "en",
             "speaker_group": "synthetic-target", "role": "target"},
        ],
        "outcomes": {
            "content_wer": 0.0,
            "identity_similarity_cosine": 0.0,
            "naturalness_mos": 3.0,
            "alignment_samples": 0,
            "first_output_ms": 260.0,
            "tail_ms": 200.0,
            "peak_abs": 0.5,
            "clipped_fraction": 0.0,
            "nonfinite_count": 0,
            "sample_count": 16000,
        },
        "rights": {
            "consent_reference": "synthetic-consent",
            "reference_availability": "synthetic-availability",
            "output_use": "synthetic-output-use",
            "terms_review": "synthetic-terms-review",
            "listening_protocol": "synthetic-listening",
            "listening_panel_size": 0,
            "claims_qualified": False,
        },
    }


def _mutation_cases(control: dict) -> list[tuple[str, dict]]:
    cases: list[tuple[str, dict]] = []

    def add(code: str, mutate) -> None:
        document = json.loads(json.dumps(control))
        mutate(document)
        cases.append((code, document))

    add("manifest_fields", lambda d: d.update(extra_field=True))
    add("schema_id", lambda d: d.update(schema_id="wrong"))
    add("bundle_id", lambda d: d.update(bundle_id="Not A Slug"))
    add("source_fields", lambda d: d["source"].update(extra="x"))
    add("source_revision", lambda d: d["source"].update(revision="0" * 40))
    add("source_tree", lambda d: d["source"].update(tree_sha256="0" * 64))
    add("source_path", lambda d: d["source"].update(path="../escape"))
    add("source_license_id", lambda d: d["source"].update(license_id="WTFPL"))
    add("source_license_sha",
        lambda d: d["source"].update(license_sha256="xyz"))
    add("weights_not_list", lambda d: d.update(weights={}))
    add("weight_fields",
        lambda d: d["weights"][0].update(extra="x"))
    add("weight_name",
        lambda d: d["weights"][0].update(name="Upper Name"))
    add("weight_duplicate",
        lambda d: d["weights"][1].update(name="synth_weights"))
    add("weight_digest_duplicate",
        lambda d: d["weights"][1].update(sha256=d["weights"][0]["sha256"]))
    add("weight_bytes",
        lambda d: d["weights"][0].update(byte_count=0))
    add("weight_bytes_too_large",
        lambda d: d["weights"][0].update(byte_count=MAX_WEIGHT_BYTES + 1))
    add("weight_terms",
        lambda d: d["weights"][0].update(terms_sha256="bad"))
    add("weight_required",
        lambda d: d.update(weights=d["weights"][:3]))
    add("weight_unknown",
        lambda d: d["weights"].append(
            {"name": "extra", "sha256": "9" * 64, "byte_count": 1,
             "terms_sha256": "3" * 64}))
    add("runtime_fields", lambda d: d["runtime"].update(extra="x"))
    add("runtime_python",
        lambda d: d["runtime"].update(python_version="3.12.0"))
    add("runtime_mlx",
        lambda d: d["runtime"].update(mlx_version="0.30.0"))
    add("runtime_mlx_metal",
        lambda d: d["runtime"].update(mlx_metal_version="0.30.0"))
    add("runtime_numpy",
        lambda d: d["runtime"].update(numpy_version="2.0.0"))
    add("runtime_faiss",
        lambda d: d["runtime"].update(faiss_version="1.8.0"))
    add("runtime_scipy",
        lambda d: d["runtime"].update(scipy_version="1.16.0"))
    add("runtime_sounddevice",
        lambda d: d["runtime"].update(sounddevice_version="0.5.4"))
    add("runtime_soxr",
        lambda d: d["runtime"].update(soxr_version="1.0.0"))
    add("runtime_device",
        lambda d: d["runtime"].update(device="cpu"))
    add("runtime_metal",
        lambda d: d["runtime"].update(metal_available=False))
    add("runtime_offline",
        lambda d: d["runtime"].update(offline=False))
    add("runtime_deterministic",
        lambda d: d["runtime"].update(deterministic=False))
    add("realtime_fields", lambda d: d["realtime"].update(extra="x"))
    add("realtime_defaults",
        lambda d: d["realtime"].update(block_ms=250))
    add("realtime_rate",
        lambda d: d["realtime"].update(input_sample_rate_hz=48000))
    add("realtime_bounds",
        lambda d: d["realtime"].update(queue_capacity=3))
    add("realtime_derived",
        lambda d: d["realtime"].update(convert_samples=9153))
    add("references_count",
        lambda d: d["references"].pop())
    add("reference_fields",
        lambda d: d["references"][0].update(extra="x"))
    add("reference_role",
        lambda d: d["references"][0].update(role="target"))
    add("reference_id",
        lambda d: d["references"][0].update(id="Bad Id"))
    add("reference_path",
        lambda d: d["references"][0].update(path="synthetic/../x.wav"))
    add("reference_sha",
        lambda d: d["references"][0].update(sha256="bad"))
    add("reference_sha_duplicate",
        lambda d: d["references"][1].update(
            sha256=d["references"][0]["sha256"]))
    add("reference_consent",
        lambda d: d["references"][0].update(consent_id=""))
    add("reference_language",
        lambda d: d["references"][0].update(language="english"))
    add("reference_speaker_group",
        lambda d: d["references"][0].update(speaker_group=""))
    add("outcomes_fields", lambda d: d["outcomes"].update(extra=1))
    add("outcome_nonfinite:content_wer",
        lambda d: d["outcomes"].update(content_wer=float("nan")))
    add("outcome_nonfinite:identity_similarity_cosine",
        lambda d: d["outcomes"].update(
            identity_similarity_cosine=float("inf")))
    add("outcome_nonfinite:naturalness_mos",
        lambda d: d["outcomes"].update(naturalness_mos=float("nan")))
    add("outcome_range:content_wer",
        lambda d: d["outcomes"].update(content_wer=1.5))
    add("outcome_range:identity_similarity_cosine",
        lambda d: d["outcomes"].update(identity_similarity_cosine=-1.5))
    add("outcome_range:naturalness_mos",
        lambda d: d["outcomes"].update(naturalness_mos=0.0))
    add("outcome_alignment",
        lambda d: d["outcomes"].update(alignment_samples=MAX_ALIGNMENT_SAMPLES + 1))
    add("outcome_range:first_output_ms",
        lambda d: d["outcomes"].update(first_output_ms=-1.0))
    add("outcome_range:tail_ms",
        lambda d: d["outcomes"].update(tail_ms=10001.0))
    add("outcome_peak",
        lambda d: d["outcomes"].update(peak_abs=4.5))
    add("outcome_clip",
        lambda d: d["outcomes"].update(clipped_fraction=1.2))
    add("outcome_nonfinite_count",
        lambda d: d["outcomes"].update(nonfinite_count=1))
    add("outcome_sample_count",
        lambda d: d["outcomes"].update(sample_count=0))
    add("rights_fields", lambda d: d["rights"].update(extra="x"))
    add("rights_consent_reference",
        lambda d: d["rights"].update(consent_reference=""))
    add("rights_reference_availability",
        lambda d: d["rights"].update(reference_availability=""))
    add("rights_output_use", lambda d: d["rights"].update(output_use=""))
    add("rights_terms_review",
        lambda d: d["rights"].update(terms_review=""))
    add("rights_listening_protocol",
        lambda d: d["rights"].update(listening_protocol=""))
    add("rights_panel",
        lambda d: d["rights"].update(listening_panel_size=MAX_PANEL + 1))
    add("rights_claims_qualified",
        lambda d: d["rights"].update(claims_qualified=True))
    return cases


def admission_controls() -> dict:
    control = _synthetic_bundle()
    accepted = validate_manifest(control, probe_paths=False)
    if not accepted["accepted"]:
        raise ValueError("schema_control_rejected:" + accepted["code"])
    cases = []
    for index, (code, document) in enumerate(_mutation_cases(control),
                                             start=1):
        result = validate_manifest(document, probe_paths=False)
        if result["accepted"]:
            raise ValueError("admission_case_accepted:" + code)
        cases.append({
            "id": f"ADM-{index:02d}",
            "mutation": code,
            "code": result["code"],
            "field": result["field"],
            "status": "rejected",
            "state_unchanged": result["state_unchanged"],
            "qualifies": False,
        })
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "cases": cases,
        "control": {
            "accepted": True,
            "bundle_id": control["bundle_id"],
            "reason": "admission_only_no_qualified_result",
            "synthetic_schema_control_not_evidence": True,
            "state_advanced": False,
            "qualifies": False,
            "audio_read": False,
            "weights_loaded": False,
            "model_executed": False,
            "runtime_invoked": False,
            "network_used": False,
        },
        "summary": {
            "case_count": len(cases),
            "rejected_count": len(cases),
            "accepted_schema_controls": 1,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "audio_read": False,
            "weights_loaded": False,
            "model_executed": False,
            "runtime_invoked": False,
            "network_used": False,
        },
    }


def admission_contract_block() -> dict:
    return {
        "manifest_schema_id": MANIFEST_SCHEMA_ID,
        "manifest_fields": list(MANIFEST_FIELDS),
        "source_fields": list(SOURCE_FIELDS),
        "weight_fields": list(WEIGHT_FIELDS),
        "required_weight_names": list(REQUIRED_WEIGHTS),
        "optional_weight_names": list(OPTIONAL_WEIGHTS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "realtime_fields": list(REALTIME_FIELDS),
        "reference_fields": list(REFERENCE_FIELDS),
        "reference_roles": list(REFERENCE_ROLES),
        "outcome_fields": list(OUTCOME_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "exact_source_revision": SOURCE_REVISION,
        "exact_source_tree_sha256": SOURCE_TREE_SHA256,
        "exact_runtime": dict(EXACT_RUNTIME),
        "device": "metal",
        "python_version_pattern": PYTHON_VERSION.pattern,
        "realtime_defaults": {
            "block_ms": BLOCK_MS,
            "crossfade_ms": CROSSFADE_MS,
            "extra_ms": EXTRA_MS,
            "sola_search_ms": SOLA_SEARCH_MS,
            "input_sample_rate_hz": INPUT_SAMPLE_RATE,
            "target_sample_rate_hz": MODEL_SAMPLE_RATE,
            "queue_capacity": QUEUE_CAPACITY,
            "ring_blocks": RING_BLOCKS,
        },
        "max_weight_bytes": MAX_WEIGHT_BYTES,
        "max_alignment_samples": MAX_ALIGNMENT_SAMPLES,
        "max_peak": 4,
        "max_panel": MAX_PANEL,
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "audio_read": False,
        "weights_loaded": False,
        "model_executed": False,
        "runtime_invoked": False,
        "network_used": False,
    }


# --------------------------------------------------------------------------
# Report sections
# --------------------------------------------------------------------------
def _public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "preserved": True,
        "sdk_callback_invoked": False,
        "note": (
            "Installed v0 remains 16 kHz mono f32/160. The documented "
            "RVC-MLX path is a 16 kHz block front end with a 40 kHz model "
            "output and is not an installed-v0 processor format."),
    }


def _scope() -> dict:
    return {
        "task_local_only": True,
        "source_present": True,
        "license_present": False,
        "weights_present": False,
        "runtime_present": False,
        "weights_loaded": False,
        "runtime_imported": False,
        "model_executed": False,
        "audio_read": False,
        "real_corpus": False,
        "listening": False,
        "voice_conversion": False,
        "device_timing": False,
        "benchmark": False,
        "quality_scored": False,
        "identity_similarity_scored": False,
        "naturalness_scored": False,
        "download_attempted": False,
        "network_used": False,
        "release_claim": False,
    }


def _boundary() -> dict:
    return {
        "task_local_only": True,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "public_api_abi_change": False,
        "installed_v0_behavior_change": False,
        "shared_cmakelists_change": False,
        "ci_workflow_change": False,
        "default_selected": False,
        "enabled_by_default": False,
        "processor_exposure": False,
        "files_outside_task_directory_written": False,
        "real_weights_or_runtime": False,
        "voice_conversion": False,
        "listening": False,
    }


def _disposition() -> dict:
    return {
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "incomplete": True,
        "not_qualified": True,
        "promotion": "defer",
        "production_exposure": "DEFER",
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
        "missing_result_qualifies": False,
    }


def _qualification() -> dict:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "not_qualified": True,
        "all_release_gates_blocked": True,
        "source_present": True,
        "license_present": False,
        "weights_present": False,
        "runtime_present": False,
        "real_result_present": False,
        "quality_result": False,
        "identity_similarity_result": False,
        "naturalness_result": False,
        "listening_result": False,
        "alignment_result": False,
        "first_output_or_tail_result": False,
        "sola_join_result": False,
        "device_timing_result": False,
        "latency_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
    }


def _required_results() -> dict:
    return {
        "no_result_qualifies": True,
        "license_present": False,
        "weights_present": False,
        "runtime_present": False,
        "reference_consent_present": False,
        "quality_result_present": False,
        "identity_similarity_result_present": False,
        "naturalness_result_present": False,
        "listening_result_present": False,
        "alignment_result_present": False,
        "first_output_or_tail_result_present": False,
        "sola_join_result_present": False,
        "device_timing_result_present": False,
        "latency_result_present": False,
        "benchmark_result_present": False,
        "release_claim": False,
    }


def build_contract() -> dict:
    gates = []
    for gate in RELEASE_GATES:
        gates.append(dict(gate, status="blocked", qualifies=False,
                          linked_row=dict(BOARD_ROW_PROJECTION)))
    artifacts = [dict(row) for row in REQUIRED_ARTIFACTS]
    blockers = [dict(row, status="open", qualifies=False)
                for row in EXACT_BLOCKERS]
    arithmetic = arithmetic_reference()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE_LABEL,
        "profile_key": PROFILE,
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "profile_phrases": list(PROFILE_PHRASES),
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "write_scope": WRITE_SCOPE,
        "exact_scope": (
            "Task-local RVC-MLX realtime readiness blocker: pinned source "
            "checkout and tree digest, explicit missing license/weights/"
            "runtime, a fail-closed realtime-bundle admission schema, a "
            "deterministic block/SOLA/queue arithmetic reference and eight "
            "blocked release gates. No model, weight, runtime, audio, "
            "microphone, conversion or timing result."),
        "public_v0_geometry": _public_v0_geometry(),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "board_file_pinned": False,
        "board_row_fields": list(BOARD_ROW_FIELDS),
        "board_row_projection": BOARD_ROW_PROJECTION,
        "board_row_sha256": board_row_digest(BOARD_ROW_PROJECTION),
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
        "board_status_is_observation_only": True,
        "absence_policy": {
            "any_present_probe_blocks_shipping": True,
            "download_attempted": False,
            "network_used": False,
            "fixed_probe_list_only": True,
            "recursive_workspace_walk": False,
        },
        "absence_probes": list(ABSENCE_PROBES),
        "home_absence_probes": list(HOME_ABSENCE_PROBES),
        "source_revision": SOURCE_REVISION,
        "source_tree_sha256": SOURCE_TREE_SHA256,
        "source_tree_file_count": SOURCE_TREE_FILE_COUNT,
        "source_tree_byte_count": SOURCE_TREE_BYTE_COUNT,
        "required_weight_names": list(REQUIRED_WEIGHTS),
        "optional_weight_names": list(OPTIONAL_WEIGHTS),
        "source_presence": SOURCE_PRESENCE,
        "observed_test_audio": OBSERVED_TEST_AUDIO,
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "release_gates": gates,
        "voice_profile_requirements": [dict(row)
                                       for row in VOICE_PROFILE_ROWS],
        "quality_outcomes": [dict(row) for row in QUALITY_OUTCOME_ROWS],
        "timing_requirements": [dict(row) for row in TIMING_ROWS],
        "historical_execution": HISTORICAL_EXECUTION,
        "repository_performance_recorded": REPOSITORY_PERFORMANCE_RECORDED,
        "arithmetic_reference": arithmetic,
        "admission_contract": admission_contract_block(),
        "non_claims": list(NON_CLAIMS),
        "scope": _scope(),
        "boundary": _boundary(),
        "disposition": _disposition(),
        "qualification": _qualification(),
        "required_results": _required_results(),
        "reproduction": {
            "interpreter": "Python 3.12, standard library only",
            "commands": [
                "python3 run.py all",
                "python3 -m unittest -v test_reference.py",
                "python3 verify.py",
            ],
            "cold_start_repeats": 3,
            "network_required": False,
            "runtime_required": False,
        },
    }


CONTRACT_FIELDS = (
    "schema_id",
    "contract_id",
    "task",
    "component",
    "title",
    "mode",
    "branch",
    "base_commit",
    "profile",
    "profile_key",
    "profile_source",
    "profile_phrases",
    "decision",
    "status",
    "qualification_status",
    "proposal_only",
    "write_scope",
    "exact_scope",
    "public_v0_geometry",
    "source_pins",
    "boundary_pins",
    "board_file_pinned",
    "board_row_fields",
    "board_row_projection",
    "board_row_sha256",
    "linked_rows",
    "linked_rows_sha256",
    "board_status_is_observation_only",
    "absence_policy",
    "absence_probes",
    "home_absence_probes",
    "source_revision",
    "source_tree_sha256",
    "source_tree_file_count",
    "source_tree_byte_count",
    "required_weight_names",
    "optional_weight_names",
    "source_presence",
    "observed_test_audio",
    "required_artifacts",
    "exact_blockers",
    "release_gates",
    "voice_profile_requirements",
    "quality_outcomes",
    "timing_requirements",
    "historical_execution",
    "repository_performance_recorded",
    "arithmetic_reference",
    "admission_contract",
    "non_claims",
    "scope",
    "boundary",
    "disposition",
    "qualification",
    "required_results",
    "reproduction",
)


def validate_contract(document: dict) -> None:
    if set(document) != set(CONTRACT_FIELDS):
        missing = sorted(set(CONTRACT_FIELDS) - set(document))
        extra = sorted(set(document) - set(CONTRACT_FIELDS))
        raise ValueError("contract_field_mismatch:" +
                         (missing[0] if missing else extra[0]))
    _no_floats(document)
    if document["schema_id"] != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_mismatch")
    if document["task"] != TASK or document["component"] != COMPONENT_ID:
        raise ValueError("contract_identity_mismatch")
    if document["profile"] != PROFILE_LABEL:
        raise ValueError("contract_profile_mismatch")
    if document["decision"] != "DEFER" or document["status"] != "incomplete":
        raise ValueError("contract_disposition_mismatch")
    if document["qualification_status"] != "not_qualified":
        raise ValueError("contract_qualification_mismatch")
    if document["proposal_only"] is not True:
        raise ValueError("contract_proposal_only_mismatch")
    if document["board_file_pinned"] is not False:
        raise ValueError("contract_board_pin_mismatch")
    if document["board_row_projection"] != BOARD_ROW_PROJECTION:
        raise ValueError("contract_board_projection_mismatch")
    if document["board_row_sha256"] != board_row_digest(BOARD_ROW_PROJECTION):
        raise ValueError("contract_board_digest_mismatch")
    if document["linked_rows_sha256"] != linked_rows_digest():
        raise ValueError("contract_linked_rows_mismatch")
    if len(document["release_gates"]) != 8:
        raise ValueError("contract_gate_count")
    for index, gate in enumerate(document["release_gates"], start=1):
        if gate["id"] != f"RG-{index:02d}":
            raise ValueError("contract_gate_id")
        if gate["status"] != "blocked" or gate["qualifies"] is not False:
            raise ValueError("contract_gate_not_blocked")
        if not gate["reopen_condition"]:
            raise ValueError("contract_gate_reopen_missing")
    if len(document["required_artifacts"]) != 7:
        raise ValueError("contract_artifact_count")
    if document["required_artifacts"][0]["present"] is not True:
        raise ValueError("contract_source_artifact_missing")
    for artifact in document["required_artifacts"][1:]:
        if artifact["present"] is not False or artifact["blocked"] is not True:
            raise ValueError("contract_artifact_not_blocked")
    if len(document["voice_profile_requirements"]) != 8:
        raise ValueError("contract_voice_row_count")
    for row in document["voice_profile_requirements"]:
        if row["status"] != "blocked":
            raise ValueError("contract_voice_row_not_blocked")
    if document["admission_contract"] != admission_contract_block():
        raise ValueError("contract_admission_contract_mismatch")
    if document["source_pins"] != SOURCE_PINS:
        raise ValueError("contract_source_pins_mismatch")
    if document["boundary_pins"] != BOUNDARY_PINS:
        raise ValueError("contract_boundary_pins_mismatch")
    if document["observed_test_audio"] != OBSERVED_TEST_AUDIO:
        raise ValueError("contract_observed_audio_mismatch")
    if document["arithmetic_reference"]["all_checks_pass"] is not True:
        raise ValueError("contract_arithmetic_reference_failed")
    for section in ("scope", "boundary"):
        for key, value in document[section].items():
            if key in ("task_local_only", "source_present"):
                if value is not True:
                    raise ValueError("contract_task_local_mismatch")
            elif value is not False:
                raise ValueError("contract_" + section + "_claim:" + key)


def build_report() -> dict:
    contract = build_contract()
    source_rows = pin_rows(SOURCE_PINS, AUDIO_ROOT)
    boundary_rows = pin_rows(BOUNDARY_PINS, WORKTREE)
    verify_source_tree(AUDIO_ROOT / SOURCE_ROOT)
    if (AUDIO_ROOT / SOURCE_PRESENCE["original_rvc_license_path"]).is_file():
        actual = sha256_file(
            AUDIO_ROOT / SOURCE_PRESENCE["original_rvc_license_path"])
        if actual != SOURCE_PRESENCE["original_rvc_license_sha256"]:
            raise ValueError("original_rvc_license_mismatch")
    else:
        raise ValueError("original_rvc_license_missing")
    test_audio = AUDIO_ROOT / OBSERVED_TEST_AUDIO["path"]
    if not test_audio.is_file():
        raise ValueError("observed_test_audio_missing")
    if sha256_file(test_audio) != OBSERVED_TEST_AUDIO["sha256"]:
        raise ValueError("observed_test_audio_digest_mismatch")
    workspace_rows = absence_probes(AUDIO_ROOT)
    home_rows = home_absence_probes()
    runtime_probe = runtime_module_probe()
    admission = admission_controls()
    if not admission["control"]["accepted"]:
        raise ValueError("schema_control_not_accepted")
    for case in admission["cases"]:
        if case["status"] != "rejected":
            raise ValueError("admission_case_not_rejected:" + case["id"])
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "profile": PROFILE_LABEL,
        "profile_key": PROFILE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": _disposition(),
        "qualification": _qualification(),
        "contract_sha256": object_digest(contract),
        "source_pins": source_rows,
        "boundary_pins": boundary_rows,
        "source_presence": SOURCE_PRESENCE,
        "absence_evidence": {
            "summary": absence_summary(workspace_rows, home_rows),
            "probes": workspace_rows,
            "home_probes": home_rows,
            "runtime_probe": runtime_probe,
            "observed_test_audio": OBSERVED_TEST_AUDIO,
            "observed_media": {
                "test_audio_path": OBSERVED_TEST_AUDIO["path"],
                "test_audio_sha256": OBSERVED_TEST_AUDIO["sha256"],
                "test_audio_byte_count": OBSERVED_TEST_AUDIO["byte_count"],
                "byte_hash_only": True,
                "decoded": False,
                "signal_loaded": False,
                "audio_read": False,
                "listening_performed": False,
                "used_for_evidence": False,
            },
        },
        "required_artifacts": [dict(row) for row in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(row, status="open", qualifies=False)
                           for row in EXACT_BLOCKERS],
        "gates": [dict(gate, status="blocked", qualifies=False,
                       linked_row=dict(BOARD_ROW_PROJECTION))
                  for gate in RELEASE_GATES],
        "voice_profile": {
            "profile": PROFILE_LABEL,
            "status": "blocked",
            "rows": [dict(row) for row in VOICE_PROFILE_ROWS],
            "text_and_semantic_preserved": False,
            "identity_similarity_measured": False,
            "naturalness_measured": False,
            "alignment_measured": False,
            "first_output_or_tail_measured": False,
            "exact_target_condition_qualified": False,
            "consent_cleared": False,
            "reference_availability_cleared": False,
            "output_use_cleared": False,
        },
        "quality_outcomes": {
            "status": "blocked",
            "rows": [dict(row) for row in QUALITY_OUTCOME_ROWS],
            "text_and_semantic_preserved": False,
            "identity_similarity_measured": False,
            "naturalness_measured": False,
            "independent_listening_present": False,
        },
        "timing": {
            "status": "blocked",
            "rows": [dict(row) for row in TIMING_ROWS],
            "alignment_measured": False,
            "first_output_measured": False,
            "tail_measured": False,
            "sola_join_measured": False,
            "device_timing_measured": False,
            "peak_bound_measured": False,
            "resource_measured": False,
            "latency_measured": False,
        },
        "arithmetic_reference": arithmetic_reference(),
        "historical_execution": HISTORICAL_EXECUTION,
        "repository_performance_recorded": REPOSITORY_PERFORMANCE_RECORDED,
        "admission": admission,
        "linked_row_identity": {
            "projection": BOARD_ROW_PROJECTION,
            "sha256": board_row_digest(BOARD_ROW_PROJECTION),
            "linked_rows_sha256": linked_rows_digest(),
            "linked_rows": [dict(row) for row in LINKED_ROWS],
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "mutable_fields_excluded": [
                "status", "owner", "claim", "review", "handoff",
                "blocked_reason", "dispatch_priority",
            ],
        },
        "boundary": _boundary(),
        "scope": _scope(),
        "public_v0_geometry": _public_v0_geometry(),
        "required_results": _required_results(),
        "non_claims": list(NON_CLAIMS),
        "reproduction": {
            "interpreter": "Python 3.12, standard library only",
            "commands": [
                "python3 run.py all",
                "python3 -m unittest -v test_reference.py",
                "python3 verify.py",
            ],
            "cold_start_repeats": 3,
            "network_required": False,
            "runtime_required": False,
        },
    }
    _no_floats(report)
    return report


def canonical_report(document: dict | None = None) -> tuple[str, str]:
    report = build_report() if document is None else document
    _no_floats(report)
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
