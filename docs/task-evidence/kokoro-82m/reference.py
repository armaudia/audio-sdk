# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-KOKORO-82M (Kokoro 82M).

This module is standard-library only and deterministic. It contains no Kokoro
source copy, model weight, voice-style tensor, inference runtime, generated
waveform, listening result or vendor result. It records the exact external
blocker, verifies the pinned source checkout, probes a fixed list of workspace
and home-cache paths to evidence the absence of weights and a pinned runtime,
validates a caller-supplied Voice cohort manifest with a fail-closed admission
boundary, and builds the canonical report.

The upstream Kokoro code checkout is present at an exact revision with an
Apache-2.0 license. That source presence is recorded and pinned, but it is not
a weight grant, a voice-style-asset grant, a runtime, a qualified preset voice
or a model result. The weights, the preset voice asset and the exact runtime
are absent. Nothing was downloaded, loaded or executed.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-KOKORO-82M"
COMPONENT_ID = "kokoro-82m"
TASK_TITLE = "Kokoro 82M"
CONTRACT_ID = "audio-sdk/kokoro-82m-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
MODE = "implementation"
BASE_COMMIT = "b8ac930b88f4cb7b87e01498a838b0a0654a1aef"
BRANCH = "swarm/SDK-KOKORO-82M"
WRITE_SCOPE = "docs/task-evidence/kokoro-82m/ only"
TASK_PREFIX = "docs/task-evidence/kokoro-82m/"

SOURCE_REVISION = "dfb907a02bba8152ca444717ca5d78747ccb4bec"
SOURCE_TREE_SHA256 = (
    "2530843b30567d1f4d00288a27badc650fb53c01f371c672c31cc12441811a26")
SOURCE_TREE_FILE_COUNT = 108
SOURCE_TREE_BYTE_COUNT = 29147679
HF_REPOSITORY = "hexgrad/Kokoro-82M"
HF_REFERENCE_REVISION = None
HF_CACHE_DIR = "~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M"

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
    "research/voice-conversion-eval-20261101/results/kokoro/metrics.json":
        "e96da8bd48e9e22063f8329fe16b5328916b9fd0024f50ae5a7fd7da59335850",
    "research/voice-conversion-eval-20261101/results/kokoro/asr.json":
        "8be4df45333cc4815457b5efb75182a2b0a29cd906be1f96a8692227ed878100",
    "research/voice-conversion-eval-20261101/scripts/run_kokoro_tts.py":
        "c4b6ba548495321bc6999214e117a58e9324203dc898ef9d01249faac289e450",
    "research/voice-conversion-eval-20261101/repos/kokoro/LICENSE":
        "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "research/voice-conversion-eval-20261101/repos/kokoro/pyproject.toml":
        "f8c3ae1c6b3c2644ad27b6c66e309bee32ac48fe46b7e4e676a95b417acdd04c",
    "research/voice-conversion-eval-20261101/repos/kokoro/README.md":
        "b50b84220668f8247a2405b249c34c7083acc24114279ff1429fd79f46a2c04b",
    "research/voice-conversion-eval-20261101/repos/kokoro/kokoro/model.py":
        "301c55350a068c4ed3b4cbd1209d2afb848bebca72db5657405e47e9dfb604db",
    "research/voice-conversion-eval-20261101/repos/kokoro/kokoro/pipeline.py":
        "499982bbc23a1019681cdb4c327c1d911e7034e240721b95686ff1a8f15c2a9a",
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
        "id": "SDK-CHATTERBOX-NANO",
        "title": "Chatterbox Nano",
        "component": "chatterbox-nano",
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
    "research/voice-conversion-eval-20261101/models/kokoro",
    "research/voice-conversion-eval-20261101/models/kokoro/kokoro-v1_0.pth",
    "research/voice-conversion-eval-20261101/models/kokoro/config.json",
    "research/voice-conversion-eval-20261101/models/kokoro/voices/af_heart.pt",
    "research/voice-conversion-eval-20261101/checkpoints/kokoro-v1_0.pth",
    "research/voice-conversion-eval-20261101/checkpoints/voices/af_heart.pt",
    "research/voice-conversion-eval-20261101/repos/kokoro/kokoro-v1_0.pth",
    "research/voice-conversion-eval-20261101/repos/kokoro/config.json",
    "research/voice-conversion-eval-20261101/repos/kokoro/voices/af_heart.pt",
    "research/voice-conversion-eval-20261101/.venv-kokoro",
    "data/models/kokoro-82m",
    "data/models/kokoro-82m/kokoro-v1_0.pth",
    "data/assets/kokoro-82m",
    "data/envs/kokoro",
    "data/wheels/kokoro-0.9.4-py3-none-any.whl",
    "third_party/kokoro",
    "deps/kokoro",
    "adapters/kokoro",
    "adapters/kokoro/run.py",
    "docs/task-evidence/kokoro-82m/weights",
    "docs/task-evidence/kokoro-82m/assets",
    "docs/task-evidence/kokoro-82m/kokoro-v1_0.pth",
    "docs/task-evidence/kokoro-82m/af_heart.wav",
    "docs/task-evidence/kokoro-82m/reference_output.wav",
    "docs/task-evidence/kokoro-82m/cohort",
    "LICENSES/Kokoro-82M-weights.txt",
    "research/voice-conversion-eval-20261101/data/kokoro-reference.wav",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/snapshots",
    "~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/blobs",
)

REQUIRED_WEIGHT_FILES = (
    "config.json",
    "kokoro-v1_0.pth",
    "voices/af_heart.pt",
)

SOURCE_PRESENCE = {
    "path": "research/voice-conversion-eval-20261101/repos/kokoro",
    "revision": SOURCE_REVISION,
    "revision_source": "git rev-parse HEAD of the shallow checkout",
    "tree_sha256": SOURCE_TREE_SHA256,
    "tree_digest_recipe": (
        "sha256 over sorted '<relative-path>\\0<file-sha256>\\n' rows for "
        "every non-.git regular file"),
    "file_count": SOURCE_TREE_FILE_COUNT,
    "tree_byte_count": SOURCE_TREE_BYTE_COUNT,
    "license_id": "Apache-2.0",
    "license_path": ("research/voice-conversion-eval-20261101/repos/"
                     "kokoro/LICENSE"),
    "license_sha256":
        "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "project_version": "0.9.4",
    "present": True,
    "verified": True,
    "admitted": False,
    "model_executed": False,
    "weights_used": False,
    "present_components": ["source_code_and_apache_2_0_license"],
    "absent_components": ["exact_weights_snapshot", "exact_voice_style_asset",
                          "exact_runtime"],
    "exact_source_weights_runtime_conjunction_present": False,
    "reason": (
        "The official Kokoro code checkout is present at the pinned revision "
        "and its Apache-2.0 LICENSE is pinned. Code rights do not grant "
        "weight, voice-style, model-card or output-use rights, and the model "
        "weights, the preset voice asset and the exact runtime are absent."),
}

OBSERVED_HF_CACHE = {
    "path": HF_CACHE_DIR,
    "repository": HF_REPOSITORY,
    "reference_revision": HF_REFERENCE_REVISION,
    "present": False,
    "blobs_present": False,
    "snapshots_present": False,
    "weights_present": False,
    "admitted": False,
    "used_for_evidence": False,
    "reason": (
        "No models--hexgrad--Kokoro-82M directory exists in the user cache. "
        "No weight, config or voice-style bytes are present, and this "
        "package does not download or reconstruct them."),
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
            "Exact upstream Kokoro source at a 40-hex revision with its "
            "Apache-2.0 license text, per-file SHA-256 pins, tree digest and "
            "file count, from a reviewable source root."),
    },
    {
        "id": "ART-02",
        "kind": "weights_and_voice_assets_snapshot",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "The exact hexgrad/Kokoro-82M immutable snapshot declared by the "
            "pinned source (config.json, kokoro-v1_0.pth and the preset "
            "voices/af_heart.pt style asset), with the 40-hex snapshot "
            "revision and every file's byte count and SHA-256."),
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
            "A reproducible isolated runtime satisfying the pinned project "
            "metadata and the historical run (CPython 3.11.x, kokoro 0.9.4, "
            "misaki 0.9.4, torch 2.15.0, torchaudio 2.11.1, CPU), with a "
            "lock/install digest and a fail-closed offline load path."),
    },
    {
        "id": "ART-04",
        "kind": "weight_voice_and_output_use_rights",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "Reviewed weight/model-card terms, per-artifact redistribution "
            "and product-use scope, and explicit preset-voice asset terms "
            "and generated-output use terms. The code Apache-2.0 license "
            "does not cover these."),
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_voice_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "revision": None,
        "requirement": (
            "A rights-cleared frozen text and preset-voice cohort with "
            "manual transcripts, language and speaker groups, declared "
            "target condition, and matched fixed-voice, alternate-voice and "
            "text-control controls."),
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
            "An agreed Voice protocol that separately measures text/semantic "
            "preservation, preset-identity/similarity, naturalness, "
            "alignment, first-output/tail, nonfinite/peak behavior, device "
            "timing, resource limits, independent listening and uncertainty."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "statement": (
            "The exact Kokoro-82M weight files and the af_heart preset voice "
            "style asset are absent from every fixed probe. The user Hugging "
            "Face cache has no models--hexgrad--Kokoro-82M directory. The "
            "research record states the weights were removed after the "
            "historical run; the checkpoints directory is empty. Nothing was "
            "downloaded or reconstructed."),
        "required_action": (
            "Supply an immutable hexgrad/Kokoro-82M snapshot at a 40-hex "
            "revision with config.json, kokoro-v1_0.pth and "
            "voices/af_heart.pt, and record the exact byte count and SHA-256 "
            "of every file."),
        "linked_gates": ["RG-02", "RG-03"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "statement": (
            "No isolated Kokoro runtime, lock file, install digest or offline "
            "load path is present. torch and kokoro are not importable in the "
            "available evidence interpreters, and the historical evaluation "
            "environment was not retained."),
        "required_action": (
            "Supply a reproducible pinned CPython 3.11.x runtime with "
            "kokoro 0.9.4, misaki 0.9.4, torch 2.15.0, torchaudio 2.11.1, a "
            "lock/install digest, an offline load path, deterministic "
            "settings and a recorded host profile."),
        "linked_gates": ["RG-03", "RG-07"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "statement": (
            "Weight/model-card terms, preset-voice asset terms and "
            "generated-output use terms are not staged or reviewed. The "
            "pinned Apache-2.0 LICENSE covers the code checkout only."),
        "required_action": (
            "Stage the complete weight/model-card and voice-style terms and "
            "record an explicit rights decision covering redistribution, "
            "product use, preset-voice availability and output use."),
        "linked_gates": ["RG-02", "RG-04"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "statement": (
            "No rights-cleared frozen text/preset-voice cohort exists. The "
            "historical run used one fixed 27-word sentence and the af_heart "
            "preset with no output-use grant, language/speaker groups, "
            "manual transcript adjudication or matched controls."),
        "required_action": (
            "Supply a frozen rights-cleared cohort with manual transcripts, "
            "language and speaker groups, explicit target conditions and "
            "fixed-voice, alternate-voice and text-control controls."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "statement": (
            "No agreed quality, preset-identity/similarity, naturalness, "
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
            "revision, tree digest and file count, with the complete "
            "Apache-2.0 license/notice set, is supplied and reviewed."),
    },
    {
        "id": "RG-02",
        "title": "weights_voice_assets_and_terms",
        "statement": (
            "Every Kokoro-82M weight, config and preset voice-style asset is "
            "pinned by byte count and SHA-256 with reviewed terms."),
        "reopen_condition": (
            "The immutable weight/voice snapshot and all per-file digests "
            "are supplied, and weight/model-card and voice-style terms are "
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
        "title": "voice_asset_availability_and_output_use",
        "statement": (
            "Preset-voice availability and generated-output use are "
            "independent, explicitly cleared gates for every voice used."),
        "reopen_condition": (
            "Preset-voice asset terms, availability and output-use terms are "
            "staged for every voice used, including af_heart."),
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_text_and_voice_cohort",
        "statement": (
            "A frozen rights-cleared text/voice cohort with manual "
            "transcripts, language/speaker groups and matched controls "
            "exists before any result."),
        "reopen_condition": (
            "The immutable cohort, transcripts, groups, target conditions "
            "and fixed/alternate-voice and text controls are supplied."),
    },
    {
        "id": "RG-06",
        "title": "separate_content_identity_naturalness_and_listening",
        "statement": (
            "Text/semantic preservation, preset-identity/similarity and "
            "naturalness are measured as separate outcomes with independent "
            "listening."),
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
            "Freeze permitted input text and target preset voice, task and "
            "language/speaker groups."),
        "status": "blocked",
        "evidence": (
            "No rights-cleared text set, preset-voice terms, consent record, "
            "language or speaker group, or frozen target condition is "
            "staged."),
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
            "No preset-voice consistency metric, reference similarity "
            "scorer, target encoder or reviewed result exists for Kokoro "
            "82M; it is a fixed-voice TTS control, not a cloning model."),
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
            "No phoneme, token or word alignment was measured."),
    },
    {
        "id": "V-06",
        "requirement": "Record first-output and tail timing.",
        "status": "blocked",
        "evidence": (
            "The historical generator yielded one whole segment; the "
            "57.297 s first-segment time is call-to-segment and not a "
            "streaming first-output latency. No tail timing exists."),
    },
    {
        "id": "V-07",
        "requirement": "Record the exact target condition.",
        "status": "blocked",
        "evidence": (
            "The historical condition was one 27-word English sentence with "
            "the af_heart preset at speed 1 on CPU; no voice-asset terms, "
            "target specification or reference-text policy exists. This is "
            "provenance, not a qualified target condition."),
    },
    {
        "id": "V-08",
        "requirement": (
            "Keep preset-voice availability and output use as independent "
            "gates."),
        "status": "blocked",
        "evidence": (
            "No preset-voice availability or output-use record exists; the "
            "code Apache-2.0 license does not clear either."),
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
        "outcome": "preset_identity_similarity",
        "status": "blocked",
        "value": None,
        "evidence": (
            "No preset-voice consistency score, independent encoder or "
            "human identity rating exists."),
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
            "No streaming or chunked output exists; the historical generator "
            "returned one whole segment and reports only call-to-segment."),
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
    "candidate": "hexgrad/Kokoro-82M (official repository, preset-voice TTS control)",
    "source": "research/voice-conversion-eval-20261101/README.md",
    "metrics_path": (
        "research/voice-conversion-eval-20261101/results/kokoro/metrics.json"),
    "metrics_sha256":
        "e96da8bd48e9e22063f8329fe16b5328916b9fd0024f50ae5a7fd7da59335850",
    "asr_path": (
        "research/voice-conversion-eval-20261101/results/kokoro/asr.json"),
    "asr_sha256":
        "8be4df45333cc4815457b5efb75182a2b0a29cd906be1f96a8692227ed878100",
    "output_path": (
        "research/voice-conversion-eval-20261101/results/kokoro/af_heart.wav"),
    "output_sha256":
        "85de4ae78e14aa7826f7f3bf6572adc2366a0338c33aac914f65957bbea233fa",
    "output_byte_count": 433244,
    "text": (
        "Printing, in the only sense with which we are at present "
        "concerned, differs from most if not from all the arts and crafts "
        "represented in the Exhibition."),
    "voice": "af_heart",
    "fixed_voice_preset": True,
    "voice_cloning": False,
    "mode": "fixed-voice whole-utterance TTS; CPU; 4 Torch threads",
    "sample_rate_hz": 24000,
    "chunk_count": 1,
    "audio_seconds_decimal": "9.025",
    "first_chunk_after_start_seconds_decimal": "57.297223249974195",
    "first_chunk_after_pipeline_init_seconds_decimal": "3.841400207951665",
    "total_wall_seconds_decimal": "57.29795258399099",
    "file_rtf_decimal": "0.1575099910729023",
    "peak_abs_decimal": "0.37054443359375",
    "clipped_sample_fraction_decimal": "0.0",
    "wer_decimal": "0.0",
    "asr_wall_seconds_decimal": "1.008296083949972",
    "first_audio_latency_present": False,
    "streaming_chunks_present": False,
    "naturalness_measured": False,
    "identity_similarity_measured": False,
    "manual_transcript_present": False,
    "device_timing_present": False,
    "not_rerun": True,
    "merged_task_evidence": False,
    "used_for_evidence": False,
    "qualifies": False,
    "limitations": [
        "Fixed-voice TTS control, not speech-to-speech conversion and not "
        "zero-shot voice cloning.",
        "The generator yielded one whole segment; no incremental chunks were "
        "exposed, so first-audio latency is unavailable.",
        "CPU-only run on the historical host; no MPS accelerator was used.",
        "One text, one preset voice, one output; no similarity, naturalness, "
        "listening, alignment, device timing or multi-speaker coverage.",
    ],
}

NON_CLAIMS = (
    "No Kokoro source copy, model weight, config, preset voice-style asset, "
    "runtime, generated waveform or vendor result is present, loaded, linked "
    "or executed by this package.",
    "No model inference, text normalization, G2P, audio read, audio write, "
    "listening, preset-similarity, naturalness or content-preservation "
    "result is produced.",
    "The one historical Kokoro 82M run is provenance only; it is not rerun, "
    "not merged task evidence and not promoted to a qualification.",
    "No alignment, first-output/tail, device-timing, peak, nonfinite, CPU, "
    "memory or deadline result is produced.",
    "No provider is registered, exposed, enabled by default or selected as a "
    "descriptor default; no public API, ABI, registry, shared build or CI "
    "change is made.",
    "No Chatterbox Nano, Chatterbox VC, CosyVoice 2, F5-TTS, NeuTTS, "
    "StyleTTS 2, YourTTS or other voice result is reused, pooled or "
    "reinterpreted as Kokoro 82M evidence.",
    "No missing, synthetic or schema-control result is promoted or treated "
    "as evidence for the candidate.",
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

# Admission manifest is a task-local schema, not an SDK, Kokoro or Voice
# contract. It admits metadata only and never reads audio or invokes a model.
MANIFEST_SCHEMA_ID = "audio-sdk/kokoro-82m-cohort/0.1"
MANIFEST_FIELDS = (
    "schema_id",
    "cohort_id",
    "source",
    "weights",
    "runtime",
    "references",
    "texts",
    "controls",
    "outcomes",
    "rights",
)
SOURCE_FIELDS = ("revision", "path", "license_id", "license_path",
                 "license_sha256")
WEIGHT_FIELDS = ("name", "sha256", "byte_count", "terms_sha256")
RUNTIME_FIELDS = (
    "python_version",
    "kokoro_version",
    "misaki_version",
    "torch_version",
    "torchaudio_version",
    "device",
    "threads",
    "deterministic_algorithms",
)
REFERENCE_FIELDS = ("id", "path", "sha256", "consent_id", "rights_reference",
                    "language", "speaker_group")
TEXT_FIELDS = ("id", "text", "language", "speaker_group", "reference_id",
               "reference_sha256", "consent_id", "output_use")
CONTROL_FIELDS = ("id", "kind", "reference_id")
OUTCOME_FIELDS = (
    "text_semantic_wer",
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
CONTROL_KINDS = ("fixed_voice", "alternate_voice", "text_control")
REQUIRED_WEIGHTS = ("config.json", "kokoro-v1_0.pth", "voices/af_heart.pt")
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


def observed_hf_cache() -> dict:
    root = Path.home() / HF_CACHE_DIR[2:]
    if not root.is_dir():
        return dict(OBSERVED_HF_CACHE, present=False, entries=[], blob_count=0,
                    snapshot_count=0)
    entries = sorted(path.name for path in root.iterdir())
    blobs = sorted(path.name for path in (root / "blobs").iterdir()) \
        if (root / "blobs").is_dir() else []
    snapshots = sorted(path.name for path in (root / "snapshots").iterdir()) \
        if (root / "snapshots").is_dir() else []
    return dict(OBSERVED_HF_CACHE, present=True, entries=entries,
                blobs_present=bool(blobs), snapshots_present=bool(snapshots),
                blob_count=len(blobs), snapshot_count=len(snapshots))


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
    if source["license_id"] != "Apache-2.0":
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
    for field, expected in (("kokoro_version", "0.9.4"),
                            ("misaki_version", "0.9.4"),
                            ("torch_version", "2.15.0"),
                            ("torchaudio_version", "2.11.1")):
        if runtime[field] != expected:
            return _reject("invalid_value", "runtime." + field)
    if runtime["device"] != "cpu":
        return _reject("invalid_value", "runtime.device")
    if not _is_int(runtime["threads"]) \
            or not 1 <= runtime["threads"] <= MAX_THREADS:
        return _reject("invalid_value", "runtime.threads")
    if runtime["deterministic_algorithms"] is not True:
        return _reject("invalid_value", "runtime.deterministic_algorithms")
    checks += 8

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

    texts = document["texts"]
    if not isinstance(texts, list) or not texts:
        return _reject("invalid_value", "texts")
    seen_texts: set[str] = set()
    for text in texts:
        code = _exact_object(text, TEXT_FIELDS)
        if code:
            return _reject(code, "texts")
        if not _slug(text["id"]) or text["id"] in seen_texts:
            return _reject("invalid_value", "texts.id")
        seen_texts.add(text["id"])
        if not _text(text["text"], MAX_TEXT_LENGTH):
            return _reject("invalid_value", "texts.text")
        if not isinstance(text["language"], str) \
                or not LANGUAGE.match(text["language"]):
            return _reject("invalid_value", "texts.language")
        for field in ("speaker_group", "consent_id", "output_use"):
            if not _slug(text[field]):
                return _reject("invalid_value", "texts." + field)
        if text["reference_id"] not in reference_ids:
            return _reject("invalid_value", "texts.reference_id")
        if text["reference_sha256"] != reference_ids[text["reference_id"]]:
            return _reject("invalid_value", "texts.reference_sha256")
    checks += len(texts) * 8

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
        kinds[control["kind"]] = control["reference_id"]
        if control["kind"] == "text_control":
            if control["reference_id"] is not None:
                return _reject("invalid_value", "controls.reference_id")
        elif control["reference_id"] not in reference_ids:
            return _reject("invalid_value", "controls.reference_id")
    if set(CONTROL_KINDS) - set(kinds):
        return _reject("invalid_value", "controls.required")
    if kinds["fixed_voice"] == kinds["alternate_voice"]:
        return _reject("invalid_value", "controls.alternate_voice")
    checks += len(controls) * 3 + 1

    outcomes = document["outcomes"]
    code = _exact_object(outcomes, OUTCOME_FIELDS)
    if code:
        return _reject(code, "outcomes")
    if not _is_number(outcomes["text_semantic_wer"]) \
            or not 0.0 <= float(outcomes["text_semantic_wer"]) <= 1.0:
        return _reject("invalid_value", "outcomes.text_semantic_wer")
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
            "path": "/caller/kokoro/src",
            "license_id": "Apache-2.0",
            "license_path": "/caller/kokoro/LICENSE",
            "license_sha256": "a" * 64,
        },
        "weights": [
            {"name": "config.json", "sha256": "1" * 64,
             "byte_count": 1000, "terms_sha256": "2" * 64},
            {"name": "kokoro-v1_0.pth", "sha256": "3" * 64,
             "byte_count": 1000, "terms_sha256": "4" * 64},
            {"name": "voices/af_heart.pt", "sha256": "5" * 64,
             "byte_count": 1000, "terms_sha256": "6" * 64},
        ],
        "runtime": {
            "python_version": "3.11.5",
            "kokoro_version": "0.9.4",
            "misaki_version": "0.9.4",
            "torch_version": "2.15.0",
            "torchaudio_version": "2.11.1",
            "device": "cpu",
            "threads": 4,
            "deterministic_algorithms": True,
        },
        "references": [
            {"id": "voice-a", "path": "/caller/voice/af_heart.pt",
             "sha256": "9" * 64, "consent_id": "consent-a",
             "rights_reference": "rights-a", "language": "en-US",
             "speaker_group": "speaker-a"},
            {"id": "voice-b", "path": "/caller/voice/am_michael.pt",
             "sha256": "b" * 64, "consent_id": "consent-b",
             "rights_reference": "rights-b", "language": "en-US",
             "speaker_group": "speaker-b"},
        ],
        "texts": [
            {"id": "text-a", "text": "Synthetic schema control text.",
             "language": "en-US", "speaker_group": "speaker-a",
             "reference_id": "voice-a", "reference_sha256": "9" * 64,
             "consent_id": "consent-a", "output_use": "research-only"},
        ],
        "controls": [
            {"id": "ctl-fixed", "kind": "fixed_voice",
             "reference_id": "voice-a"},
            {"id": "ctl-alternate", "kind": "alternate_voice",
             "reference_id": "voice-b"},
            {"id": "ctl-text", "kind": "text_control",
             "reference_id": None},
        ],
        "outcomes": {
            "text_semantic_wer": 0.0,
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

    def set_nested(path: tuple[str, ...], value: Any):
        def apply(document: dict) -> None:
            target = document
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = value
        return apply

    def del_nested(path: tuple[str, ...]):
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
           set_nested(("source", "license_id"), "MIT"))
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
               "weights", [dict(document["weights"][0])]))
    mutate("weights-unknown-field",
           set_nested(("weights", 0, "extra"), "value"))
    mutate("weights-missing-field",
           del_nested(("weights", 0, "terms_sha256")))
    mutate("weights-name-traversal",
           set_nested(("weights", 0, "name"), "../config.json"))
    mutate("weights-name-absolute",
           set_nested(("weights", 0, "name"), "/config.json"))
    mutate("weights-name-double-slash",
           set_nested(("weights", 0, "name"), "voices//af_heart.pt"))
    mutate("weights-name-uppercase",
           set_nested(("weights", 0, "name"), "CONFIG.json"))
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
    mutate("runtime-kokoro-wrong",
           set_nested(("runtime", "kokoro_version"), "0.9.3"))
    mutate("runtime-misaki-wrong",
           set_nested(("runtime", "misaki_version"), "0.9.3"))
    mutate("runtime-torch-wrong",
           set_nested(("runtime", "torch_version"), "2.6.0"))
    mutate("runtime-torchaudio-wrong",
           set_nested(("runtime", "torchaudio_version"), "2.6.0"))
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
           set_nested(("references", 0, "path"), "af_heart.pt"))
    mutate("references-path-null",
           set_nested(("references", 0, "path"), "/caller/af_heart\x00.pt"))
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

    mutate("texts-empty", set_nested(("texts",), []))
    mutate("texts-not-list", set_nested(("texts",), {}))
    mutate("texts-missing-field", del_nested(("texts", 0, "text")))
    mutate("texts-unknown-field", set_nested(("texts", 0, "extra"), "value"))
    mutate("texts-duplicate-id",
           lambda document: document["texts"].append(
               dict(document["texts"][0])))
    mutate("texts-empty-text", set_nested(("texts", 0, "text"), ""))
    mutate("texts-too-long",
           set_nested(("texts", 0, "text"), "a" * (MAX_TEXT_LENGTH + 1)))
    mutate("texts-language-bad",
           set_nested(("texts", 0, "language"), "en_US"))
    mutate("texts-reference-unknown",
           set_nested(("texts", 0, "reference_id"), "voice-missing"))
    mutate("texts-reference-sha-mismatch",
           set_nested(("texts", 0, "reference_sha256"), "0" * 64))
    mutate("texts-output-use-empty",
           set_nested(("texts", 0, "output_use"), ""))
    mutate("texts-speaker-empty",
           set_nested(("texts", 0, "speaker_group"), ""))

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
           set_nested(("controls", 1, "kind"), "fixed_voice"))
    mutate("controls-missing-fixed", without_control("fixed_voice"))
    mutate("controls-missing-alternate", without_control("alternate_voice"))
    mutate("controls-missing-text", without_control("text_control"))
    mutate("controls-fixed-unknown-ref",
           set_nested(("controls", 0, "reference_id"), "voice-missing"))
    mutate("controls-alternate-unknown-ref",
           set_nested(("controls", 1, "reference_id"), "voice-missing"))
    mutate("controls-alternate-same-ref",
           set_nested(("controls", 1, "reference_id"), "voice-a"))
    mutate("controls-text-with-ref",
           set_nested(("controls", 2, "reference_id"), "voice-a"))

    for field in OUTCOME_FIELDS:
        mutate("missing-outcome-" + field, del_nested(("outcomes", field)))
    mutate("unknown-outcome-field",
           set_nested(("outcomes", "extra"), "value"))
    mutate("outcome-wer-nan",
           set_nested(("outcomes", "text_semantic_wer"), float("nan")))
    mutate("outcome-wer-inf",
           set_nested(("outcomes", "text_semantic_wer"), float("inf")))
    mutate("outcome-wer-neg",
           set_nested(("outcomes", "text_semantic_wer"), -0.1))
    mutate("outcome-wer-high",
           set_nested(("outcomes", "text_semantic_wer"), 1.1))
    mutate("outcome-wer-bool",
           set_nested(("outcomes", "text_semantic_wer"), True))
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
        "text_fields": list(TEXT_FIELDS),
        "control_fields": list(CONTROL_FIELDS),
        "control_kinds": list(CONTROL_KINDS),
        "outcome_fields": list(OUTCOME_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "required_weight_names": list(REQUIRED_WEIGHTS),
        "exact_source_revision": SOURCE_REVISION,
        "exact_kokoro": "0.9.4",
        "exact_misaki": "0.9.4",
        "exact_torch": "2.15.0",
        "exact_torchaudio": "2.11.1",
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
            "Installed v0 remains 16 kHz mono f32/160. The historical Kokoro "
            "output is 24 kHz whole-utterance TTS and is not an installed-v0 "
            "processor format."),
    }


def _scope() -> dict:
    return {
        "task_local_only": True,
        "source_present": True,
        "weights_present": False,
        "voice_style_asset_present": False,
        "runtime_present": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "real_corpus": False,
        "listening": False,
        "voice_cloning": False,
        "device_timing": False,
        "benchmark": False,
        "quality_scored": False,
        "reference_similarity_scored": False,
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
        "voice_cloning": False,
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
        "voice_style_asset_present": False,
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
        "voice_style_asset_present": False,
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
            "Task-local Kokoro 82M readiness evidence: source and absence "
            "pins, a fail-closed Voice admission schema, blocked profile "
            "accounting and eight blocked release gates. No model, weight, "
            "voice-style asset, runtime, corpus or result."),
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
        "hf_repository": HF_REPOSITORY,
        "hf_reference_revision": HF_REFERENCE_REVISION,
        "required_weight_files": list(REQUIRED_WEIGHT_FILES),
        "source_presence": SOURCE_PRESENCE,
        "observed_hf_cache": OBSERVED_HF_CACHE,
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
    "hf_repository",
    "hf_reference_revision",
    "required_weight_files",
    "source_presence",
    "observed_hf_cache",
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
            "observed_hf_cache": observed_hf_cache(),
            "observed_media": {
                "output_path": HISTORICAL_EXECUTION["output_path"],
                "output_sha256": HISTORICAL_EXECUTION["output_sha256"],
                "output_byte_count": HISTORICAL_EXECUTION["output_byte_count"],
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
