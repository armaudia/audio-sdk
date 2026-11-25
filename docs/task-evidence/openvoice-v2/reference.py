# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-OPENVOICE-V2 (OpenVoice V2).

This module is standard-library only and deterministic. It contains no
OpenVoice source copy, model weight, converter checkpoint, speaker-embedding
tensor, inference runtime, generated waveform, listening result or vendor
result. It records the exact external blocker, verifies the pinned source
checkout, probes a fixed list of workspace and home-cache paths to evidence the
absence of the weight archive and a pinned runtime, validates a caller-supplied
Voice cohort manifest with a fail-closed admission boundary, and builds the
canonical report.

The upstream MyShell OpenVoice code checkout is present at an exact revision
with an MIT license. That source presence is recorded and pinned, but it is not
a verified weight archive, a speaker-embedding asset, a runtime, a qualified
target condition or a model result. The V2 converter checkpoint, the release
archive and the exact historical runtime are absent. Nothing was downloaded,
loaded or executed.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-OPENVOICE-V2"
COMPONENT_ID = "openvoice-v2"
TASK_TITLE = "OpenVoice V2"
CONTRACT_ID = "audio-sdk/openvoice-v2-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
MODE = "implementation"
BASE_COMMIT = "bcc4572f2f1ed596f314204a59472586a0c94cc6"
BRANCH = "swarm/SDK-OPENVOICE-V2"
WRITE_SCOPE = "docs/task-evidence/openvoice-v2/ only"
TASK_PREFIX = "docs/task-evidence/openvoice-v2/"

SOURCE_REVISION = "74a1d147b17a8c3092dd5430504bd83ef6c7eb23"
SOURCE_TREE_SHA256 = (
    "477585d11e9e4a5c03c1c7ce8bbff3e5b7aa11cacce4c99294ec2761182ca558")
SOURCE_TREE_FILE_COUNT = 37
SOURCE_TREE_BYTE_COUNT = 3463846
RELEASE_ARCHIVE_NAME = "checkpoints_v2_0417.zip"
RELEASE_ARCHIVE_URL = (
    "https://myshell-public-repo-host.s3.amazonaws.com/openvoice/"
    "checkpoints_v2_0417.zip")
HF_CACHE_DIRS = (
    "~/.cache/huggingface/hub/models--myshell-ai--OpenVoice",
    "~/.cache/huggingface/hub/models--myshell-ai--OpenVoiceV2",
)

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
# from the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/results/openvoice/metrics.json":
        "322d49984ff5599b74bb18833517a5ca0a2b636d93d3a81b5fe7d6a0177557f9",
    "research/voice-conversion-eval-20261101/results/openvoice/asr.json":
        "30a851e463b8e1a0840f92d64acf924900d42b193b3b3b1366541255814ac737",
    "research/voice-conversion-eval-20261101/scripts/run_openvoice_eval.py":
        "2060622f3db3bc9997037d62c1dd17e24f593fa2365b3d249f62103d72204058",
    "research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md":
        "b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6",
    "research/voice-conversion-eval-20261101/repos/openvoice/LICENSE":
        "bb3541f421e6273d3a3e3dd5bdba2bd3b79a3c2eadca65cde9c62c2467903ac0",
    "research/voice-conversion-eval-20261101/repos/openvoice/README.md":
        "3c6f5d24798763ebb9ca5fea8a1cbd21b935a140300ba531138b5518cd297dfc",
    "research/voice-conversion-eval-20261101/repos/openvoice/docs/USAGE.md":
        "8dc88ad1a938a4fa07b5cad8d6950030444e4d1a1c4626fd3998b2cb121fc2f0",
    "research/voice-conversion-eval-20261101/repos/openvoice/requirements.txt":
        "ff3a30cda9e6b66e5628677fd88632f72c8eef784832e08dadd11046dcafd59a",
    "research/voice-conversion-eval-20261101/repos/openvoice/setup.py":
        "bdc21e07e8636827f48eda91518467efdda93e3dd1a43d3f4331080d24de4d8c",
    "research/voice-conversion-eval-20261101/repos/openvoice/openvoice/api.py":
        "6830abaf9b0ea6023fe7e3df3d9a0a1fd9b73a7dbbc13f8a892da009052637b9",
    "research/voice-conversion-eval-20261101/repos/openvoice/openvoice/models.py":
        "54f9e8284a0e9a89c75cb3163d2694cf34d90a5d05cfbcbf12ccd4f0b1ba2dc8",
    "research/voice-conversion-eval-20261101/repos/openvoice/openvoice/se_extractor.py":
        "deb53f75846b8f6e0e331a3b875b8f9e44cd03cdb99a1a8a143ff73376d69ae3",
    "research/voice-conversion-eval-20261101/repos/openvoice/demo_part3.ipynb":
        "b60a930f422c0a39908142f10d769e7c7afeeea5b1010b50dda55c269cdd0843",
    "research/voice-conversion-eval-20261101/repos/seed-vc/modules/openvoice/"
    "checkpoints_v2/converter/config.json":
        "9dfff60350b8c63f2c664efd92a61b2516efb22671466960f0e5dfebd881fa47",
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
        "id": "SDK-LLVC",
        "title": "LLVC",
        "component": "llvc",
        "mode": "implementation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                       "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-SURVEY-TRN-04",
        "title": "Review coverage for Speech-to-speech voice conversion",
        "component": None,
        "mode": "taxonomy",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    },
    {
        "id": "SDK-SURVEY-TRN-05",
        "title": "Review coverage for Reference-conditioned voice cloning / TTS",
        "component": None,
        "mode": "taxonomy",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    },
)

# Fixed, bounded absence probes. No recursive workspace walk is performed and
# no download is attempted. Any present path makes report generation fail.
ABSENCE_PROBES = (
    "research/voice-conversion-eval-20261101/repos/openvoice/checkpoints_v2",
    "research/voice-conversion-eval-20261101/repos/openvoice/checkpoints_v2/"
    "converter",
    "research/voice-conversion-eval-20261101/repos/openvoice/checkpoints_v2/"
    "converter/checkpoint.pth",
    "research/voice-conversion-eval-20261101/repos/openvoice/checkpoints_v2/"
    "converter/config.json",
    "research/voice-conversion-eval-20261101/repos/openvoice/checkpoints_v2/"
    "base_speakers",
    "research/voice-conversion-eval-20261101/repos/openvoice/checkpoints_v2/"
    "base_speakers/ses",
    "research/voice-conversion-eval-20261101/repos/openvoice/checkpoints",
    "research/voice-conversion-eval-20261101/checkpoints/openvoice",
    "research/voice-conversion-eval-20261101/checkpoints/openvoice/"
    "checkpoint.pth",
    "research/voice-conversion-eval-20261101/checkpoints_v2_0417.zip",
    "research/voice-conversion-eval-20261101/models/openvoice",
    "research/voice-conversion-eval-20261101/models/openvoice/checkpoint.pth",
    "research/voice-conversion-eval-20261101/models/openvoice/config.json",
    "research/voice-conversion-eval-20261101/.venv-openvoice",
    "data/models/openvoice-v2",
    "data/models/openvoice-v2/checkpoint.pth",
    "data/assets/openvoice-v2",
    "data/envs/openvoice",
    "data/wheels/MyShell_OpenVoice-0.0.0-py3-none-any.whl",
    "third_party/openvoice",
    "deps/openvoice",
    "adapters/openvoice",
    "adapters/openvoice/run.py",
    "docs/task-evidence/openvoice-v2/weights",
    "docs/task-evidence/openvoice-v2/assets",
    "docs/task-evidence/openvoice-v2/checkpoints_v2",
    "docs/task-evidence/openvoice-v2/output.wav",
    "docs/task-evidence/openvoice-v2/cohort",
    "LICENSES/OpenVoice-V2-weights.txt",
    "research/voice-conversion-eval-20261101/data/openvoice-reference.wav",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--myshell-ai--OpenVoice",
    "~/.cache/huggingface/hub/models--myshell-ai--OpenVoiceV2",
    "~/.cache/torch/hub/checkpoints/openvoice",
)

REQUIRED_WEIGHT_FILES = (
    "checkpoints_v2/converter/config.json",
    "checkpoints_v2/converter/checkpoint.pth",
)

SOURCE_PRESENCE = {
    "path": "research/voice-conversion-eval-20261101/repos/openvoice",
    "revision": SOURCE_REVISION,
    "revision_source": "git rev-parse HEAD of the shallow checkout",
    "tree_sha256": SOURCE_TREE_SHA256,
    "tree_digest_recipe": (
        "sha256 over sorted '<relative-path>\\0<file-sha256>\\n' rows for "
        "every non-.git regular file"),
    "file_count": SOURCE_TREE_FILE_COUNT,
    "tree_byte_count": SOURCE_TREE_BYTE_COUNT,
    "license_id": "MIT",
    "license_path": ("research/voice-conversion-eval-20261101/repos/"
                     "openvoice/LICENSE"),
    "license_sha256":
        "bb3541f421e6273d3a3e3dd5bdba2bd3b79a3c2eadca65cde9c62c2467903ac0",
    "project_version": "0.0.0",
    "present": True,
    "verified": True,
    "admitted": False,
    "model_executed": False,
    "weights_used": False,
    "present_components": ["source_code_and_mit_license"],
    "absent_components": ["verified_v2_weight_archive",
                          "converter_checkpoint", "speaker_embedding_assets",
                          "exact_runtime"],
    "exact_source_weights_runtime_conjunction_present": False,
    "reason": (
        "The official OpenVoice code checkout is present at the pinned "
        "revision and its MIT LICENSE is pinned. Source and a code license do "
        "not establish that the removed V2 converter checkpoint, the release "
        "archive members, the speaker-embedding assets or the exact runtime "
        "are present or verified."),
}

# A V2 converter config-shaped file exists only inside the Seed-VC vendored
# OpenVoice module. It is pinned and disclosed, but it is not admitted as the
# exact checkpoints_v2_0417.zip member and no companion checkpoint exists.
OBSERVED_CONFIG_COPY = {
    "path": ("research/voice-conversion-eval-20261101/repos/seed-vc/modules/"
             "openvoice/checkpoints_v2/converter/config.json"),
    "sha256":
        "9dfff60350b8c63f2c664efd92a61b2516efb22671466960f0e5dfebd881fa47",
    "byte_count": 838,
    "version": "v2",
    "sample_rate_hz": 22050,
    "present": True,
    "admitted": False,
    "exact_release_archive_member": False,
    "companion_checkpoint_present": False,
    "used_for_evidence": False,
    "reason": (
        "This config lives in the Seed-VC repository's vendored OpenVoice "
        "module, not in the removed OpenVoice V2 checkpoint bundle. It cannot "
        "be verified against the official checkpoints_v2_0417.zip archive, "
        "and checkpoints_v2/converter/checkpoint.pth is absent. It is "
        "disclosed as an observed copy only and is not used."),
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
            "Exact upstream OpenVoice source at a 40-hex revision with its MIT "
            "license text, per-file SHA-256 pins, tree digest and file count, "
            "from a reviewable source root."),
    },
    {
        "id": "ART-02",
        "kind": "weights_and_speaker_assets_snapshot",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "The exact official OpenVoice V2 release archive "
            "(checkpoints_v2_0417.zip) at a recorded archive revision, with "
            "checkpoints_v2/converter/config.json, "
            "checkpoints_v2/converter/checkpoint.pth and the speaker-embedding "
            "assets used by the declared cohort, each with byte count and "
            "SHA-256."),
    },
    {
        "id": "ART-03",
        "kind": "pinned_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "A reproducible isolated runtime matching the historical run "
            "(CPython 3.11.x, PyTorch 2.15.0, TorchAudio 2.11.1, the pinned "
            "OpenVoice source, librosa 0.9.1, soundfile and librosa load "
            "shims, CPU), with a lock/install digest and a fail-closed offline "
            "load path."),
    },
    {
        "id": "ART-04",
        "kind": "weight_archive_and_output_use_rights",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "A reviewed release-archive terms and notice bundle, explicit "
            "weight and speaker-embedding availability records for every "
            "reference used, and generated-output use terms. The upstream "
            "README asserts MIT for V1/V2, but no archive, notice bundle or "
            "per-asset output-use record is staged or reviewed here."),
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_source_target_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "A rights-cleared frozen speech-to-speech cohort with permitted "
            "source utterances, target reference speakers, manual "
            "transcripts, language/speaker groups, declared target conditions "
            "and identity, target and alternate-target controls."),
    },
    {
        "id": "ART-06",
        "kind": "quality_and_timing_harness",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "An agreed Voice protocol that separately measures content "
            "preservation, target identity/similarity, naturalness, "
            "alignment, first-output/tail, nonfinite/peak behavior, device "
            "timing, resource limits, independent listening and uncertainty."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "statement": (
            "The V2 converter checkpoint and the official release archive are "
            "absent from every fixed probe. The openvoice checkout has no "
            "checkpoints_v2 directory, the shared checkpoints directory is "
            "empty, and only a V2 config-shaped copy exists in the Seed-VC "
            "vendored module. The research record states the 125 MiB "
            "checkpoint was removed after the historical run. Nothing was "
            "downloaded or reconstructed."),
        "required_action": (
            "Supply the immutable official checkpoints_v2_0417.zip archive or "
            "an equivalent reviewed snapshot at a recorded revision, and "
            "record the exact byte count and SHA-256 of config.json, "
            "checkpoint.pth and every speaker-embedding asset used."),
        "linked_gates": ["RG-02", "RG-03"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "statement": (
            "No isolated OpenVoice runtime, lock file, install digest or "
            "offline load path is present. The available interpreter is "
            "CPython 3.11.5, but torch, torchaudio, librosa, soundfile, "
            "wavmark and MeloTTS are not importable, and the historical "
            "evaluation environment was not retained."),
        "required_action": (
            "Supply a reproducible pinned CPython 3.11.x runtime with PyTorch "
            "2.15.0, TorchAudio 2.11.1, the pinned OpenVoice source and the "
            "required I/O compatibility layer, a lock/install digest, an "
            "offline load path, deterministic settings and a recorded host "
            "profile."),
        "linked_gates": ["RG-03", "RG-07"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "statement": (
            "The release archive, its notice bundle, per-asset "
            "speaker-embedding availability and generated-output use terms "
            "are not staged or reviewed. The upstream README asserts MIT for "
            "V1/V2, but an assertion is not a verified archive license, a "
            "consent record or a product-use decision."),
        "required_action": (
            "Stage the complete release-archive terms and notice bundle, "
            "record an explicit rights decision covering redistribution, "
            "product use, speaker-reference availability and output use, and "
            "review it against the pinned archive."),
        "linked_gates": ["RG-02", "RG-04"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "statement": (
            "No rights-cleared frozen source/target cohort exists. The "
            "historical run used one LJ Speech utterance and one p360 "
            "reference with no output-use grant, language/speaker groups, "
            "manual transcript adjudication or matched controls."),
        "required_action": (
            "Supply a frozen rights-cleared cohort with permitted source "
            "utterances, target reference speakers, manual transcripts, "
            "language and speaker groups, explicit target conditions and "
            "identity, target and alternate-target controls."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "statement": (
            "No agreed content, target-identity/similarity, naturalness, "
            "listening, alignment, first-output/tail, device-timing or "
            "resource protocol and no qualifying result exists. The one "
            "historical output is provenance only and was not rerun."),
        "required_action": (
            "Agree and staff the separate Voice outcome and timing protocols "
            "with margins, uncertainty, device, deadline and resource limits "
            "before collecting results."),
        "linked_gates": ["RG-06", "RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_archive_and_license_provenance",
        "statement": (
            "The exact upstream revision, immutable archive/tree digest and "
            "license provenance are recorded before any implementation "
            "claim."),
        "reopen_condition": (
            "An immutable source archive matching the pinned 40-hex "
            "revision, tree digest and file count, with the complete MIT "
            "license/notice set, is supplied and reviewed."),
    },
    {
        "id": "RG-02",
        "title": "weights_speaker_assets_and_terms",
        "statement": (
            "Every OpenVoice V2 checkpoint, config and speaker-embedding "
            "asset is pinned by byte count and SHA-256 with reviewed terms."),
        "reopen_condition": (
            "The immutable release archive and all per-file digests are "
            "supplied, and weight/archive and speaker-asset terms are "
            "reviewed."),
    },
    {
        "id": "RG-03",
        "title": "pinned_runtime_and_offline_load",
        "statement": (
            "A reproducible isolated runtime loads the exact snapshot "
            "offline with deterministic settings and no implicit download."),
        "reopen_condition": (
            "A locked runtime with install digest loads the pinned snapshot "
            "offline and records the exact host profile."),
    },
    {
        "id": "RG-04",
        "title": "speaker_reference_availability_and_output_use",
        "statement": (
            "Target reference availability and generated-output use are "
            "independent, explicitly cleared gates for every speaker used."),
        "reopen_condition": (
            "Speaker-reference availability and output-use terms are staged "
            "and reviewed for every source and target reference used."),
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_source_and_target_cohort",
        "statement": (
            "A frozen rights-cleared source/target cohort with manual "
            "transcripts, language/speaker groups and matched controls "
            "exists before any result."),
        "reopen_condition": (
            "The immutable cohort, transcripts, groups, target conditions "
            "and identity/target/alternate-target controls are supplied."),
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
        "title": "alignment_first_output_tail_peaks_and_resources",
        "statement": (
            "Alignment, first-output/tail timing, nonfinite/peak behavior, "
            "device timing, resources and deadlines are measured, not "
            "inferred."),
        "reopen_condition": (
            "Target-device paced runs record alignment, first-output/tail, "
            "peaks, nonfinite behavior, CPU, memory and deadline margins."),
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
            "record, language or speaker group, or frozen target condition "
            "is staged."),
    },
    {
        "id": "V-02",
        "requirement": "Preserve text and semantic content.",
        "status": "blocked",
        "evidence": (
            "The historical one-utterance Whisper Tiny WER is not a manual "
            "transcript or semantic-content gold and was not rerun."),
    },
    {
        "id": "V-03",
        "requirement": (
            "Measure identity/similarity as a separate outcome."),
        "status": "blocked",
        "evidence": (
            "The historical 0.890 cosine is OpenVoice's own reference-encoder "
            "diagnostic on one pair; no independent encoder or perceptual "
            "identity rating exists."),
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
            "No phoneme, token, word or frame alignment was measured."),
    },
    {
        "id": "V-06",
        "requirement": "Record first-output and tail timing.",
        "status": "blocked",
        "evidence": (
            "The published converter processes whole files. Model init, "
            "embedding and conversion wall times exist, but no streaming "
            "first-output or tail timing exists."),
    },
    {
        "id": "V-07",
        "requirement": "Record the exact target condition.",
        "status": "blocked",
        "evidence": (
            "The historical condition was one LJ Speech utterance converted "
            "to a p360 reference on CPU; no reference-availability, "
            "target-specification or output-use policy exists. This is "
            "provenance, not a qualified target condition."),
    },
    {
        "id": "V-08",
        "requirement": (
            "Keep consent, reference availability and output use as "
            "independent gates."),
        "status": "blocked",
        "evidence": (
            "No consent, speaker-reference availability or output-use record "
            "exists; the upstream MIT assertion does not clear either in this "
            "package."),
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
)

TIMING_ROWS = (
    {
        "id": "TM-01",
        "metric": "alignment_samples",
        "status": "blocked",
        "value": None,
        "evidence": "No aligned output or alignment measurement exists.",
    },
    {
        "id": "TM-02",
        "metric": "first_output_and_tail_ms",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No streaming or chunked output exists; the published converter "
            "is whole-file and reports only total conversion wall time."),
    },
    {
        "id": "TM-03",
        "metric": "device_timing_and_resources",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No target-device paced run, deadline margin, CPU, memory or "
            "nonfinite/peak observation exists."),
    },
)

HISTORICAL_EXECUTION = {
    "id": "HE-1",
    "candidate": "myshell-ai/OpenVoice V2 (official repository, ToneColorConverter)",
    "source": "research/voice-conversion-eval-20261101/README.md",
    "metrics_path": (
        "research/voice-conversion-eval-20261101/results/openvoice/metrics.json"),
    "metrics_sha256":
        "322d49984ff5599b74bb18833517a5ca0a2b636d93d3a81b5fe7d6a0177557f9",
    "asr_path": (
        "research/voice-conversion-eval-20261101/results/openvoice/asr.json"),
    "asr_sha256":
        "30a851e463b8e1a0840f92d64acf924900d42b193b3b3b1366541255814ac737",
    "output_path": (
        "research/voice-conversion-eval-20261101/results/openvoice/"
        "source_to_p360.wav"),
    "output_sha256":
        "1e1fac98e38da71999f6bfe0ca65879c82f7be104dd958f27eb5a0d2bb2709f7",
    "output_byte_count": 425516,
    "source_audio_path": (
        "research/voice-conversion-eval-20261101/data/"
        "source_ljspeech_lj001-0001.wav"),
    "source_audio_sha256":
        "adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b",
    "source_audio_byte_count": 309006,
    "target_audio_path": (
        "research/voice-conversion-eval-20261101/data/target_rtvc_p360.flac"),
    "target_audio_sha256":
        "fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44",
    "target_audio_byte_count": 69398,
    "source_text": (
        "Printing, in the only sense with which we are at present "
        "concerned, differs from most if not from all the arts and crafts "
        "represented in the Exhibition."),
    "target_reference": "p360",
    "mode": "offline whole-utterance tone-color conversion; CPU",
    "conversion_direction": "one source utterance to one target reference",
    "sample_rate_hz": 22050,
    "audio_seconds_decimal": "9.647891156462585",
    "model_init_seconds_decimal": "0.38248795800609514",
    "speaker_embedding_seconds_decimal": "0.9023486669757403",
    "conversion_seconds_decimal": "3.292042249988299",
    "file_rtf_decimal": "0.3412188421905178",
    "in_model_speaker_cosine_decimal": "0.8901664018630981",
    "peak_abs_decimal": "0.847869873046875",
    "clipped_sample_fraction_decimal": "0.0",
    "wer_decimal": "0.0",
    "asr_wall_seconds_decimal": "1.237452084023971",
    "first_audio_latency_present": False,
    "streaming_chunks_present": False,
    "causal_path_present": False,
    "naturalness_measured": False,
    "independent_identity_measured": False,
    "in_model_cosine_is_perceptual": False,
    "manual_transcript_present": False,
    "device_timing_present": False,
    "not_rerun": True,
    "merged_task_evidence": False,
    "used_for_evidence": False,
    "qualifies": False,
    "limitations": [
        "Whole-file offline conversion; the published converter has no "
        "causal streaming path, so first-audio latency is unavailable.",
        "The 0.890 cosine uses OpenVoice's own reference encoder on one pair; "
        "it is not independent, perceptual or a target-identity certificate.",
        "One English utterance, one target reference and one CPU host; no "
        "naturalness, listening, alignment, device timing or multi-speaker "
        "coverage.",
        "The converter checkpoint was removed after the run; only metrics, "
        "ASR output and the generated waveform are retained.",
    ],
}

NON_CLAIMS = (
    "No OpenVoice source copy, model weight, converter checkpoint, speaker "
    "embedding, release archive, runtime, generated waveform or vendor result "
    "is present, loaded, linked or executed by this package.",
    "No model inference, audio read, audio write, conversion, listening, "
    "target-similarity, naturalness or content-preservation result is "
    "produced.",
    "The one historical OpenVoice V2 run is provenance only; it is not "
    "rerun, not merged task evidence and not promoted to a qualification.",
    "No alignment, first-output/tail, device-timing, peak, nonfinite, CPU, "
    "memory or deadline result is produced.",
    "No provider is registered, exposed, enabled by default or selected as a "
    "descriptor default; no public API, ABI, registry, shared build or CI "
    "change is made.",
    "No LLVC, MeanVC2, Chatterbox VC, Seed-VC, RVC, CosyVoice 2, Kokoro 82M "
    "or other voice result is reused, pooled or reinterpreted as OpenVoice V2 "
    "evidence.",
    "No missing, synthetic or schema-control result is promoted or treated as "
    "evidence for the candidate.",
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

# Admission manifest is a task-local schema, not an SDK, OpenVoice or Voice
# contract. It admits metadata only and never reads audio or invokes a model.
MANIFEST_SCHEMA_ID = "audio-sdk/openvoice-v2-cohort/0.1"
MANIFEST_FIELDS = (
    "schema_id",
    "cohort_id",
    "source",
    "weights",
    "runtime",
    "references",
    "pairs",
    "controls",
    "outcomes",
    "rights",
)
SOURCE_FIELDS = ("revision", "path", "license_id", "license_path",
                 "license_sha256")
WEIGHT_FIELDS = ("name", "sha256", "byte_count", "terms_sha256")
RUNTIME_FIELDS = (
    "python_version",
    "torch_version",
    "torchaudio_version",
    "openvoice_version",
    "device",
    "threads",
    "deterministic_algorithms",
)
REFERENCE_FIELDS = ("id", "path", "sha256", "consent_id", "rights_reference",
                    "language", "speaker_group")
PAIR_FIELDS = (
    "id",
    "source_reference_id",
    "target_reference_id",
    "target_reference_sha256",
    "source_path",
    "source_sha256",
    "source_text",
    "language",
    "consent_id",
    "output_use",
)
CONTROL_FIELDS = ("id", "kind", "reference_id")
CONTROL_KINDS = ("source_identity", "target_reference", "alternate_target")
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
)
REQUIRED_WEIGHTS = (
    "checkpoints_v2/converter/config.json",
    "checkpoints_v2/converter/checkpoint.pth",
)
MAX_WEIGHT_BYTES = 4 * 1024 * 1024 * 1024
MAX_THREADS = 64
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


def observed_cache_paths() -> list[dict]:
    home = Path.home()
    rows: list[dict] = []
    for relative in HF_CACHE_DIRS:
        path = home / relative[2:]
        rows.append({"path": relative, "present": path.is_dir()})
    return rows


def observed_config_copy() -> dict:
    path = AUDIO_ROOT / OBSERVED_CONFIG_COPY["path"]
    if not path.is_file():
        return dict(OBSERVED_CONFIG_COPY, present=False,
                    observed_sha256=None, observed_byte_count=None)
    return dict(OBSERVED_CONFIG_COPY,
                observed_sha256=sha256_file(path),
                observed_byte_count=path.stat().st_size)


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
        return ("missing_field" if set(fields) - set(value) else "unknown_field")
    return ""


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX64.match(value))


def _text(value: Any, limit: int = 200) -> bool:
    return (isinstance(value, str) and bool(value.strip())
            and len(value) <= limit
            and not any(ord(char) < 32 for char in value))


def _slug(value: Any) -> bool:
    return isinstance(value, str) and bool(SLUG.match(value))


def _weight_name(value: Any) -> bool:
    if not isinstance(value, str) or not WEIGHT_NAME.match(value):
        return False
    if value.startswith("/") or ".." in value.split("/") or "//" in value:
        return False
    return value == os.path.normpath(value)


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed Voice cohort admission. No audio is read; no model runs."""
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
    if not _slug(document["cohort_id"]):
        return _reject("invalid_value", "cohort_id")
    checks += 2

    source = document["source"]
    code = _exact_object(source, SOURCE_FIELDS)
    if code:
        return _reject(code, "source")
    if not isinstance(source["revision"], str) \
            or not HEX40.match(source["revision"]):
        return _reject("invalid_value", "source.revision")
    if source["revision"] != SOURCE_REVISION:
        return _reject("invalid_value", "source.revision")
    if not _path_is_canonical(source["path"]):
        return _reject("invalid_path", "source.path")
    if source["license_id"] != "MIT":
        return _reject("invalid_value", "source.license_id")
    if not _path_is_canonical(source["license_path"]):
        return _reject("invalid_path", "source.license_path")
    if not _sha(source["license_sha256"]):
        return _reject("invalid_value", "source.license_sha256")
    if probe_paths:
        for field in ("path", "license_path"):
            if not Path(source[field]).is_file():
                return _reject("probe_missing", "source." + field)
    checks += 6

    weights = document["weights"]
    if not isinstance(weights, list) or not weights:
        return _reject("invalid_value", "weights")
    names: set[str] = set()
    for weight in weights:
        code = _exact_object(weight, WEIGHT_FIELDS)
        if code:
            return _reject(code, "weights")
        if not _weight_name(weight["name"]):
            return _reject("invalid_value", "weights.name")
        if weight["name"] in names:
            return _reject("invalid_value", "weights.name")
        names.add(weight["name"])
        if not _sha(weight["sha256"]):
            return _reject("invalid_value", "weights.sha256")
        if not _is_int(weight["byte_count"]) \
                or not 1 <= weight["byte_count"] <= MAX_WEIGHT_BYTES:
            return _reject("invalid_value", "weights.byte_count")
        if not _sha(weight["terms_sha256"]):
            return _reject("invalid_value", "weights.terms_sha256")
    if not set(REQUIRED_WEIGHTS) <= names:
        return _reject("invalid_value", "weights.required")
    if probe_paths:
        for weight in weights:
            if not Path(weight["name"]).is_file():
                return _reject("probe_missing", "weights")
    checks += len(weights) * 4 + 1

    runtime = document["runtime"]
    code = _exact_object(runtime, RUNTIME_FIELDS)
    if code:
        return _reject(code, "runtime")
    if not isinstance(runtime["python_version"], str) \
            or not PYTHON_VERSION.match(runtime["python_version"]):
        return _reject("invalid_value", "runtime.python_version")
    for field, expected in (("torch_version", "2.15.0"),
                            ("torchaudio_version", "2.11.1"),
                            ("openvoice_version", "0.0.0")):
        if runtime[field] != expected:
            return _reject("invalid_value", "runtime." + field)
    if runtime["device"] != "cpu":
        return _reject("invalid_value", "runtime.device")
    if not _is_int(runtime["threads"]) \
            or not 1 <= runtime["threads"] <= MAX_THREADS:
        return _reject("invalid_value", "runtime.threads")
    if runtime["deterministic_algorithms"] is not True:
        return _reject("invalid_value", "runtime.deterministic_algorithms")
    checks += 7

    references = document["references"]
    if not isinstance(references, list) or not references:
        return _reject("invalid_value", "references")
    reference_ids: dict[str, str] = {}
    for reference in references:
        code = _exact_object(reference, REFERENCE_FIELDS)
        if code:
            return _reject(code, "references")
        if not _slug(reference["id"]) or reference["id"] in reference_ids:
            return _reject("invalid_value", "references.id")
        if not _path_is_canonical(reference["path"]):
            return _reject("invalid_path", "references.path")
        if not _sha(reference["sha256"]):
            return _reject("invalid_value", "references.sha256")
        for field in ("consent_id", "rights_reference", "speaker_group"):
            if not _slug(reference[field]):
                return _reject("invalid_value", "references." + field)
        if not isinstance(reference["language"], str) \
                or not LANGUAGE.match(reference["language"]):
            return _reject("invalid_value", "references.language")
        reference_ids[reference["id"]] = reference["sha256"]
        if probe_paths and not Path(reference["path"]).is_file():
            return _reject("probe_missing", "references.path")
    checks += len(references) * 7

    pairs = document["pairs"]
    if not isinstance(pairs, list) or not pairs:
        return _reject("invalid_value", "pairs")
    seen_pairs: set[str] = set()
    source_refs: set[str] = set()
    target_refs: set[str] = set()
    for pair in pairs:
        code = _exact_object(pair, PAIR_FIELDS)
        if code:
            return _reject(code, "pairs")
        if not _slug(pair["id"]) or pair["id"] in seen_pairs:
            return _reject("invalid_value", "pairs.id")
        seen_pairs.add(pair["id"])
        for field in ("source_reference_id", "target_reference_id"):
            if pair[field] not in reference_ids:
                return _reject("invalid_value", "pairs." + field)
        if pair["source_reference_id"] == pair["target_reference_id"]:
            return _reject("invalid_value", "pairs.target_reference_id")
        if pair["target_reference_sha256"] != \
                reference_ids[pair["target_reference_id"]]:
            return _reject("invalid_value", "pairs.target_reference_sha256")
        if not _path_is_canonical(pair["source_path"]):
            return _reject("invalid_path", "pairs.source_path")
        if not _sha(pair["source_sha256"]):
            return _reject("invalid_value", "pairs.source_sha256")
        if not _text(pair["source_text"], MAX_TEXT_LENGTH):
            return _reject("invalid_value", "pairs.source_text")
        if not isinstance(pair["language"], str) \
                or not LANGUAGE.match(pair["language"]):
            return _reject("invalid_value", "pairs.language")
        for field in ("consent_id", "output_use"):
            if not _slug(pair[field]):
                return _reject("invalid_value", "pairs." + field)
        source_refs.add(pair["source_reference_id"])
        target_refs.add(pair["target_reference_id"])
        if probe_paths and not Path(pair["source_path"]).is_file():
            return _reject("probe_missing", "pairs.source_path")
    checks += len(pairs) * 12

    controls = document["controls"]
    if not isinstance(controls, list) or not controls:
        return _reject("invalid_value", "controls")
    kinds: dict[str, str] = {}
    control_ids: set[str] = set()
    for control in controls:
        code = _exact_object(control, CONTROL_FIELDS)
        if code:
            return _reject(code, "controls")
        if not _slug(control["id"]) or control["id"] in control_ids:
            return _reject("invalid_value", "controls.id")
        control_ids.add(control["id"])
        if control["kind"] not in CONTROL_KINDS \
                or control["kind"] in kinds:
            return _reject("invalid_value", "controls.kind")
        if control["reference_id"] not in reference_ids:
            return _reject("invalid_value", "controls.reference_id")
        kinds[control["kind"]] = control["reference_id"]
    if set(CONTROL_KINDS) - set(kinds):
        return _reject("invalid_value", "controls.required")
    if kinds["source_identity"] not in source_refs:
        return _reject("invalid_value", "controls.source_identity")
    if kinds["target_reference"] not in target_refs:
        return _reject("invalid_value", "controls.target_reference")
    if kinds["alternate_target"] in target_refs:
        return _reject("invalid_value", "controls.alternate_target")
    checks += len(controls) * 3 + 3

    outcomes = document["outcomes"]
    code = _exact_object(outcomes, OUTCOME_FIELDS)
    if code:
        return _reject(code, "outcomes")
    if not _is_number(outcomes["content_wer"]) \
            or not 0.0 <= float(outcomes["content_wer"]) <= 1.0:
        return _reject("invalid_value", "outcomes.content_wer")
    if not _is_number(outcomes["identity_similarity_cosine"]) \
            or not -1.0 <= float(outcomes["identity_similarity_cosine"]) <= 1.0:
        return _reject("invalid_value", "outcomes.identity_similarity_cosine")
    if not _is_number(outcomes["naturalness_mos"]) \
            or not 1.0 <= float(outcomes["naturalness_mos"]) <= 5.0:
        return _reject("invalid_value", "outcomes.naturalness_mos")
    if not _is_int(outcomes["alignment_samples"]) \
            or not 0 <= outcomes["alignment_samples"] <= MAX_ALIGNMENT_SAMPLES:
        return _reject("invalid_value", "outcomes.alignment_samples")
    for field in ("first_output_ms", "tail_ms"):
        if not _is_number(outcomes[field]) \
                or float(outcomes[field]) < 0.0:
            return _reject("invalid_value", "outcomes." + field)
    if not _is_number(outcomes["peak_abs"]) \
            or not 0.0 <= float(outcomes["peak_abs"]) <= MAX_PEAK:
        return _reject("invalid_value", "outcomes.peak_abs")
    if not _is_number(outcomes["clipped_fraction"]) \
            or not 0.0 <= float(outcomes["clipped_fraction"]) <= 1.0:
        return _reject("invalid_value", "outcomes.clipped_fraction")
    if not _is_int(outcomes["nonfinite_count"]) \
            or outcomes["nonfinite_count"] != 0:
        return _reject("invalid_value", "outcomes.nonfinite_count")
    if not _is_int(outcomes["sample_count"]) \
            or not 1 <= outcomes["sample_count"] <= MAX_SAMPLE_COUNT:
        return _reject("invalid_value", "outcomes.sample_count")
    checks += 10

    rights = document["rights"]
    code = _exact_object(rights, RIGHTS_FIELDS)
    if code:
        return _reject(code, "rights")
    for field in ("consent_reference", "reference_availability",
                  "output_use", "terms_review", "listening_protocol"):
        if not _text(rights[field]):
            return _reject("invalid_value", "rights." + field)
    if not _is_int(rights["listening_panel_size"]) \
            or not 1 <= rights["listening_panel_size"] <= MAX_PANEL:
        return _reject("invalid_value", "rights.listening_panel_size")
    checks += 6

    return _accept(checks)


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "synthetic-schema-control",
        "source": {
            "revision": SOURCE_REVISION,
            "path": "/caller/openvoice",
            "license_id": "MIT",
            "license_path": "/caller/openvoice/LICENSE",
            "license_sha256": "a" * 64,
        },
        "weights": [
            {"name": "checkpoints_v2/converter/config.json", "sha256": "1" * 64,
             "byte_count": 838, "terms_sha256": "2" * 64},
            {"name": "checkpoints_v2/converter/checkpoint.pth",
             "sha256": "3" * 64, "byte_count": 1000,
             "terms_sha256": "4" * 64},
        ],
        "runtime": {
            "python_version": "3.11.5",
            "torch_version": "2.15.0",
            "torchaudio_version": "2.11.1",
            "openvoice_version": "0.0.0",
            "device": "cpu",
            "threads": 4,
            "deterministic_algorithms": True,
        },
        "references": [
            {"id": "source-a", "path": "/caller/voice/source-a.wav",
             "sha256": "9" * 64, "consent_id": "consent-a",
             "rights_reference": "rights-a", "language": "en-US",
             "speaker_group": "speaker-a"},
            {"id": "target-b", "path": "/caller/voice/target-b.wav",
             "sha256": "b" * 64, "consent_id": "consent-b",
             "rights_reference": "rights-b", "language": "en-US",
             "speaker_group": "speaker-b"},
            {"id": "target-c", "path": "/caller/voice/target-c.wav",
             "sha256": "c" * 64, "consent_id": "consent-c",
             "rights_reference": "rights-c", "language": "en-US",
             "speaker_group": "speaker-c"},
        ],
        "pairs": [
            {"id": "pair-a", "source_reference_id": "source-a",
             "target_reference_id": "target-b",
             "target_reference_sha256": "b" * 64,
             "source_path": "/caller/audio/source-a.wav",
             "source_sha256": "9" * 64,
             "source_text": "Synthetic schema control source utterance.",
             "language": "en-US", "consent_id": "consent-a",
             "output_use": "research-only"},
        ],
        "controls": [
            {"id": "ctl-source", "kind": "source_identity",
             "reference_id": "source-a"},
            {"id": "ctl-target", "kind": "target_reference",
             "reference_id": "target-b"},
            {"id": "ctl-alternate", "kind": "alternate_target",
             "reference_id": "target-c"},
        ],
        "outcomes": {
            "content_wer": 0.0,
            "identity_similarity_cosine": 0.5,
            "naturalness_mos": 3.0,
            "alignment_samples": 0,
            "first_output_ms": 1.0,
            "tail_ms": 1.0,
            "peak_abs": 0.5,
            "clipped_fraction": 0.0,
            "nonfinite_count": 0,
            "sample_count": 16000,
        },
        "rights": {
            "consent_reference": "consent-a",
            "reference_availability": "caller-supplied",
            "output_use": "research-only",
            "terms_review": "review-a",
            "listening_protocol": "protocol-a",
            "listening_panel_size": 3,
        },
    }


def admission_controls() -> dict:
    """Build the frozen structural control and adverse rejection matrix."""
    control = _manifest_control()
    accepted = validate_manifest(control, probe_paths=False)
    cases: list[dict] = []

    def mutate(case_id: str, function) -> None:
        document = _manifest_control()
        function(document)
        result = validate_manifest(document, probe_paths=False)
        cases.append({
            "id": case_id,
            "status": "rejected" if not result["accepted"] else "accepted",
            "code": result["code"],
            "field": result["field"],
            "qualifies": False,
            "state_unchanged": result["state_unchanged"],
        })

    def set_top(field: str, value: Any):
        def apply(document: dict) -> None:
            document[field] = value
        return apply

    def del_top(field: str):
        def apply(document: dict) -> None:
            del document[field]
        return apply

    def set_nested(path: tuple, value: Any):
        def apply(document: dict) -> None:
            target = document
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = value
        return apply

    def del_nested(path: tuple):
        def apply(document: dict) -> None:
            target = document
            for part in path[:-1]:
                target = target[part]
            del target[path[-1]]
        return apply

    for case_id, value in (("root-list", []), ("root-null", None),
                           ("root-string", "x")):
        result = validate_manifest(value, probe_paths=False)
        cases.append({"id": case_id, "status": "rejected",
                      "code": result["code"], "field": result["field"],
                      "qualifies": False,
                      "state_unchanged": result["state_unchanged"]})

    for field in MANIFEST_FIELDS:
        mutate("missing-" + field, del_top(field))
    mutate("unknown-top-field", set_top("extra", "value"))
    mutate("wrong-schema", set_top("schema_id", "wrong"))
    mutate("cohort-uppercase", set_top("cohort_id", "Bad"))
    mutate("cohort-empty", set_top("cohort_id", ""))
    mutate("cohort-too-long", set_top("cohort_id", "a" * 65))
    mutate("cohort-null-byte", set_top("cohort_id", "a\x00b"))

    for field in SOURCE_FIELDS:
        mutate("missing-source-" + field, del_nested(("source", field)))
    mutate("unknown-source-field",
           set_nested(("source", "extra"), "value"))
    mutate("source-revision-uppercase",
           set_nested(("source", "revision"), "A" * 40))
    mutate("source-revision-short",
           set_nested(("source", "revision"), "a" * 39))
    mutate("source-revision-wrong",
           set_nested(("source", "revision"), "0" * 40))
    mutate("source-path-relative",
           set_nested(("source", "path"), "relative/src"))
    mutate("source-path-traversal",
           set_nested(("source", "path"), "/caller/../src"))
    mutate("source-path-null",
           set_nested(("source", "path"), "/caller/src\x00"))
    mutate("source-license-id",
           set_nested(("source", "license_id"), "Apache-2.0"))
    mutate("source-license-sha",
           set_nested(("source", "license_sha256"), "x" * 64))
    mutate("source-license-path-traversal",
           set_nested(("source", "license_path"), "/caller/../LICENSE"))

    mutate("weights-empty", set_nested(("weights",), []))
    mutate("weights-not-list", set_nested(("weights",), {}))
    mutate("weights-duplicate-name",
           lambda document: document["weights"].append(
               dict(document["weights"][0])))
    mutate("weights-missing-required",
           lambda document: document.__setitem__(
               "weights", [dict(document["weights"][1])]))
    mutate("weights-unknown-field",
           set_nested(("weights", 0, "extra"), "value"))
    mutate("weights-missing-field",
           del_nested(("weights", 0, "terms_sha256")))
    mutate("weights-name-traversal",
           set_nested(("weights", 0, "name"), "../config.json"))
    mutate("weights-name-absolute",
           set_nested(("weights", 0, "name"),
                      "/checkpoints_v2/converter/config.json"))
    mutate("weights-name-double-slash",
           set_nested(("weights", 0, "name"),
                      "checkpoints_v2//converter/config.json"))
    mutate("weights-name-uppercase",
           set_nested(("weights", 0, "name"),
                      "Checkpoints_v2/converter/config.json"))
    mutate("weights-sha-uppercase",
           set_nested(("weights", 0, "sha256"), "A" * 64))
    mutate("weights-byte-zero",
           set_nested(("weights", 0, "byte_count"), 0))
    mutate("weights-byte-bool",
           set_nested(("weights", 0, "byte_count"), True))
    mutate("weights-byte-float",
           set_nested(("weights", 0, "byte_count"), 1.5))
    mutate("weights-byte-negative",
           set_nested(("weights", 0, "byte_count"), -1))
    mutate("weights-byte-huge",
           set_nested(("weights", 0, "byte_count"), MAX_WEIGHT_BYTES + 1))
    mutate("weights-terms-sha",
           set_nested(("weights", 0, "terms_sha256"), "bad"))

    for field in RUNTIME_FIELDS:
        mutate("missing-runtime-" + field, del_nested(("runtime", field)))
    mutate("unknown-runtime-field",
           set_nested(("runtime", "extra"), "value"))
    mutate("runtime-python-old",
           set_nested(("runtime", "python_version"), "3.10.14"))
    mutate("runtime-python-other-minor",
           set_nested(("runtime", "python_version"), "3.12.16"))
    mutate("runtime-python-float",
           set_nested(("runtime", "python_version"), 3.11))
    mutate("runtime-torch-wrong",
           set_nested(("runtime", "torch_version"), "2.6.0"))
    mutate("runtime-torchaudio-wrong",
           set_nested(("runtime", "torchaudio_version"), "2.6.0"))
    mutate("runtime-openvoice-wrong",
           set_nested(("runtime", "openvoice_version"), "2.0.0"))
    mutate("runtime-device-cuda",
           set_nested(("runtime", "device"), "cuda"))
    mutate("runtime-threads-zero",
           set_nested(("runtime", "threads"), 0))
    mutate("runtime-threads-huge",
           set_nested(("runtime", "threads"), MAX_THREADS + 1))
    mutate("runtime-threads-bool",
           set_nested(("runtime", "threads"), True))
    mutate("runtime-deterministic-false",
           set_nested(("runtime", "deterministic_algorithms"), False))
    mutate("runtime-deterministic-string",
           set_nested(("runtime", "deterministic_algorithms"), "yes"))

    mutate("references-empty", set_nested(("references",), []))
    mutate("references-not-list", set_nested(("references",), {}))
    mutate("references-missing-field",
           del_nested(("references", 0, "consent_id")))
    mutate("references-unknown-field",
           set_nested(("references", 0, "extra"), "value"))
    mutate("references-duplicate-id",
           lambda document: document["references"].append(
               dict(document["references"][0])))
    mutate("references-path-relative",
           set_nested(("references", 0, "path"), "source-a.wav"))
    mutate("references-path-null",
           set_nested(("references", 0, "path"), "/caller/source\x00.wav"))
    mutate("references-sha",
           set_nested(("references", 0, "sha256"), "bad"))
    mutate("references-consent-empty",
           set_nested(("references", 0, "consent_id"), ""))
    mutate("references-rights-empty",
           set_nested(("references", 0, "rights_reference"), ""))
    mutate("references-language-bad",
           set_nested(("references", 0, "language"), "English"))
    mutate("references-speaker-empty",
           set_nested(("references", 0, "speaker_group"), ""))

    mutate("pairs-empty", set_nested(("pairs",), []))
    mutate("pairs-not-list", set_nested(("pairs",), {}))
    mutate("pairs-missing-field", del_nested(("pairs", 0, "source_text")))
    mutate("pairs-unknown-field", set_nested(("pairs", 0, "extra"), "value"))
    mutate("pairs-duplicate-id",
           lambda document: document["pairs"].append(
               dict(document["pairs"][0])))
    mutate("pairs-source-ref-unknown",
           set_nested(("pairs", 0, "source_reference_id"), "missing"))
    mutate("pairs-target-ref-unknown",
           set_nested(("pairs", 0, "target_reference_id"), "missing"))
    mutate("pairs-same-ref",
           set_nested(("pairs", 0, "target_reference_id"), "source-a"))
    mutate("pairs-target-sha-mismatch",
           set_nested(("pairs", 0, "target_reference_sha256"), "0" * 64))
    mutate("pairs-source-path-relative",
           set_nested(("pairs", 0, "source_path"), "source-a.wav"))
    mutate("pairs-source-sha",
           set_nested(("pairs", 0, "source_sha256"), "bad"))
    mutate("pairs-empty-text",
           set_nested(("pairs", 0, "source_text"), ""))
    mutate("pairs-too-long-text",
           set_nested(("pairs", 0, "source_text"),
                      "a" * (MAX_TEXT_LENGTH + 1)))
    mutate("pairs-language-bad",
           set_nested(("pairs", 0, "language"), "en_US"))
    mutate("pairs-output-use-empty",
           set_nested(("pairs", 0, "output_use"), ""))
    mutate("pairs-consent-empty",
           set_nested(("pairs", 0, "consent_id"), ""))

    def without_control(kind: str):
        def apply(document: dict) -> None:
            document["controls"] = [control for control in document["controls"]
                                    if control["kind"] != kind]
        return apply

    mutate("controls-empty", set_nested(("controls",), []))
    mutate("controls-not-list", set_nested(("controls",), {}))
    mutate("controls-missing-field",
           del_nested(("controls", 0, "kind")))
    mutate("controls-unknown-field",
           set_nested(("controls", 0, "extra"), "value"))
    mutate("controls-duplicate-id",
           lambda document: document["controls"].append(
               dict(document["controls"][0])))
    mutate("controls-bad-kind",
           set_nested(("controls", 0, "kind"), "unknown"))
    mutate("controls-duplicate-kind",
           set_nested(("controls", 1, "kind"), "source_identity"))
    mutate("controls-missing-source", without_control("source_identity"))
    mutate("controls-missing-target", without_control("target_reference"))
    mutate("controls-missing-alternate", without_control("alternate_target"))
    mutate("controls-source-unknown-ref",
           set_nested(("controls", 0, "reference_id"), "missing"))
    mutate("controls-target-unknown-ref",
           set_nested(("controls", 1, "reference_id"), "missing"))
    mutate("controls-source-not-a-source",
           set_nested(("controls", 0, "reference_id"), "target-b"))
    mutate("controls-target-not-a-target",
           set_nested(("controls", 1, "reference_id"), "source-a"))
    mutate("controls-alternate-is-target",
           set_nested(("controls", 2, "reference_id"), "target-b"))

    for field in OUTCOME_FIELDS:
        mutate("missing-outcome-" + field, del_nested(("outcomes", field)))
    mutate("unknown-outcome-field",
           set_nested(("outcomes", "extra"), "value"))
    mutate("outcome-wer-nan",
           set_nested(("outcomes", "content_wer"), float("nan")))
    mutate("outcome-wer-inf",
           set_nested(("outcomes", "content_wer"), float("inf")))
    mutate("outcome-wer-neg",
           set_nested(("outcomes", "content_wer"), -0.1))
    mutate("outcome-wer-high",
           set_nested(("outcomes", "content_wer"), 1.1))
    mutate("outcome-wer-bool",
           set_nested(("outcomes", "content_wer"), True))
    mutate("outcome-cosine-low",
           set_nested(("outcomes", "identity_similarity_cosine"), -1.1))
    mutate("outcome-cosine-high",
           set_nested(("outcomes", "identity_similarity_cosine"), 1.1))
    mutate("outcome-mos-low",
           set_nested(("outcomes", "naturalness_mos"), 0.9))
    mutate("outcome-mos-high",
           set_nested(("outcomes", "naturalness_mos"), 5.1))
    mutate("outcome-alignment-negative",
           set_nested(("outcomes", "alignment_samples"), -1))
    mutate("outcome-alignment-float",
           set_nested(("outcomes", "alignment_samples"), 1.5))
    mutate("outcome-first-negative",
           set_nested(("outcomes", "first_output_ms"), -1.0))
    mutate("outcome-first-inf",
           set_nested(("outcomes", "first_output_ms"), float("inf")))
    mutate("outcome-tail-negative",
           set_nested(("outcomes", "tail_ms"), -1.0))
    mutate("outcome-peak-negative",
           set_nested(("outcomes", "peak_abs"), -0.1))
    mutate("outcome-peak-high",
           set_nested(("outcomes", "peak_abs"), MAX_PEAK + 0.1))
    mutate("outcome-clipped-high",
           set_nested(("outcomes", "clipped_fraction"), 1.1))
    mutate("outcome-nonfinite-count",
           set_nested(("outcomes", "nonfinite_count"), 1))
    mutate("outcome-sample-zero",
           set_nested(("outcomes", "sample_count"), 0))
    mutate("outcome-sample-bool",
           set_nested(("outcomes", "sample_count"), True))
    mutate("outcome-sample-float",
           set_nested(("outcomes", "sample_count"), 16000.0))

    for field in RIGHTS_FIELDS:
        mutate("missing-rights-" + field, del_nested(("rights", field)))
    mutate("unknown-rights-field",
           set_nested(("rights", "extra"), "value"))
    mutate("rights-consent-empty",
           set_nested(("rights", "consent_reference"), ""))
    mutate("rights-availability-empty",
           set_nested(("rights", "reference_availability"), ""))
    mutate("rights-output-empty",
           set_nested(("rights", "output_use"), ""))
    mutate("rights-terms-empty",
           set_nested(("rights", "terms_review"), ""))
    mutate("rights-listening-empty",
           set_nested(("rights", "listening_protocol"), ""))
    mutate("rights-panel-zero",
           set_nested(("rights", "listening_panel_size"), 0))
    mutate("rights-panel-high",
           set_nested(("rights", "listening_panel_size"), MAX_PANEL + 1))
    mutate("rights-panel-bool",
           set_nested(("rights", "listening_panel_size"), True))

    return {
        "control": {
            "id": "schema-control",
            "status": "accepted_schema_control",
            "evidence_class": "synthetic_schema_control_not_evidence",
            "qualifies": False,
            "accepted": accepted["accepted"],
            "checks": accepted["checks"],
        },
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "rejected_count": sum(1 for case in cases
                                  if case["status"] == "rejected"),
            "accepted_schema_controls": 1,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "audio_read": False,
            "weights_loaded": False,
            "model_executed": False,
            "network_used": False,
        },
    }


# --------------------------------------------------------------------------
# Contract and report
# --------------------------------------------------------------------------
def admission_contract_block() -> dict:
    return {
        "manifest_schema_id": MANIFEST_SCHEMA_ID,
        "manifest_fields": list(MANIFEST_FIELDS),
        "source_fields": list(SOURCE_FIELDS),
        "weight_fields": list(WEIGHT_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "reference_fields": list(REFERENCE_FIELDS),
        "pair_fields": list(PAIR_FIELDS),
        "control_fields": list(CONTROL_FIELDS),
        "control_kinds": list(CONTROL_KINDS),
        "outcome_fields": list(OUTCOME_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "required_weight_names": list(REQUIRED_WEIGHTS),
        "exact_source_revision": SOURCE_REVISION,
        "exact_torch": "2.15.0",
        "exact_torchaudio": "2.11.1",
        "exact_openvoice": "0.0.0",
        "device": "cpu",
        "python_version_pattern": PYTHON_VERSION.pattern,
        "max_weight_bytes": MAX_WEIGHT_BYTES,
        "max_threads": MAX_THREADS,
        "max_text_length": MAX_TEXT_LENGTH,
        "max_alignment_samples": MAX_ALIGNMENT_SAMPLES,
        "max_peak": 4,
        "max_panel": MAX_PANEL,
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "audio_read": False,
        "weights_loaded": False,
        "model_executed": False,
        "network_used": False,
    }


def _public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "frame_samples": 160,
        "preserved": True,
        "sdk_callback_invoked": False,
        "note": (
            "Installed v0 remains 16 kHz mono f32/160. The historical "
            "OpenVoice V2 output is 22.05 kHz whole-file conversion and is "
            "not an installed-v0 processor format."),
    }


def _scope() -> dict:
    return {
        "task_local_only": True,
        "source_present": True,
        "weights_present": False,
        "runtime_present": False,
        "weights_loaded": False,
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
        "weights_present": False,
        "runtime_present": False,
        "real_result_present": False,
        "quality_result": False,
        "identity_similarity_result": False,
        "naturalness_result": False,
        "listening_result": False,
        "alignment_result": False,
        "first_output_or_tail_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
    }


def _required_results() -> dict:
    return {
        "no_result_qualifies": True,
        "weights_present": False,
        "runtime_present": False,
        "reference_consent_present": False,
        "quality_result_present": False,
        "identity_similarity_result_present": False,
        "naturalness_result_present": False,
        "listening_result_present": False,
        "alignment_result_present": False,
        "first_output_or_tail_result_present": False,
        "device_timing_result_present": False,
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
            "Task-local OpenVoice V2 readiness evidence: source and absence "
            "pins, an observed non-admitted config copy, a fail-closed Voice "
            "admission schema, blocked profile accounting and eight blocked "
            "release gates. No model, weight, speaker asset, runtime, corpus "
            "or result."),
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
        "release_archive_name": RELEASE_ARCHIVE_NAME,
        "release_archive_url": RELEASE_ARCHIVE_URL,
        "required_weight_files": list(REQUIRED_WEIGHT_FILES),
        "source_presence": SOURCE_PRESENCE,
        "observed_config_copy": OBSERVED_CONFIG_COPY,
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "release_gates": gates,
        "voice_profile_requirements": [dict(row)
                                       for row in VOICE_PROFILE_ROWS],
        "quality_outcomes": [dict(row) for row in QUALITY_OUTCOME_ROWS],
        "timing_requirements": [dict(row) for row in TIMING_ROWS],
        "historical_execution": HISTORICAL_EXECUTION,
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
    "release_archive_name",
    "release_archive_url",
    "required_weight_files",
    "source_presence",
    "observed_config_copy",
    "required_artifacts",
    "exact_blockers",
    "release_gates",
    "voice_profile_requirements",
    "quality_outcomes",
    "timing_requirements",
    "historical_execution",
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
    if len(document["required_artifacts"]) != 6:
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
    if document["observed_config_copy"] != OBSERVED_CONFIG_COPY:
        raise ValueError("contract_observed_config_mismatch")
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
    verify_source_tree(AUDIO_ROOT / SOURCE_PRESENCE["path"])
    config_copy = observed_config_copy()
    if config_copy["present"] is not True:
        raise ValueError("observed_config_copy_missing")
    if config_copy["observed_sha256"] != OBSERVED_CONFIG_COPY["sha256"]:
        raise ValueError("observed_config_copy_digest_mismatch")
    workspace_rows = absence_probes(AUDIO_ROOT)
    home_rows = home_absence_probes()
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
            "observed_cache_paths": observed_cache_paths(),
            "observed_config_copy": config_copy,
            "observed_media": {
                "output_path": HISTORICAL_EXECUTION["output_path"],
                "output_sha256": HISTORICAL_EXECUTION["output_sha256"],
                "output_byte_count": HISTORICAL_EXECUTION["output_byte_count"],
                "source_audio_sha256":
                    HISTORICAL_EXECUTION["source_audio_sha256"],
                "target_audio_sha256":
                    HISTORICAL_EXECUTION["target_audio_sha256"],
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
            "device_timing_measured": False,
            "peak_bound_measured": False,
            "resource_measured": False,
        },
        "historical_execution": HISTORICAL_EXECUTION,
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
