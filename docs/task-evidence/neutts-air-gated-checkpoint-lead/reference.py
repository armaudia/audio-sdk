# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-NEUTTS-AIR-GATED-CHECKPOINT-LEAD.

This module is standard-library only and deterministic. It contains no NeuTTS
source copy, Air weight, Air Q4/Q8 GGUF snapshot, NeuCodec asset, inference
runtime, real reference voice, generated waveform, listening result or vendor
result. It records the exact external blocker, probes a fixed list of workspace
and home-cache paths to evidence the absence of the gated Air checkpoint, the
codec and the pinned runtime, validates a caller-supplied Voice cohort manifest
with a fail-closed admission boundary, and builds the canonical report.

The upstream `neuphonic/neutts` code checkout is present at an exact revision
with its repository `LICENSE` (NeuTTS Open License v1.0). Its README states that
NeuTTS-Air weights are Apache-2.0 while the repository `LICENSE` text is the
NeuTTS Open License v1.0. That discrepancy is recorded as an unresolved license
boundary, not as a grant. The Air checkpoint repositories are gated and absent;
the research record reports an HTTP 401 without authenticated access. Nothing
was downloaded, loaded or executed by this package.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-NEUTTS-AIR-GATED-CHECKPOINT-LEAD"
COMPONENT_ID = "neutts-air-gated-checkpoint-lead"
TASK_TITLE = "NeuTTS Air / gated checkpoint lead"
CONTRACT_ID = "audio-sdk/neutts-air-gated-checkpoint-lead-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
MODE = "feasibility"
BASE_COMMIT = "feb342c735740f32d64a668cf2234e488cdcdbfe"
BRANCH = "swarm/SDK-NEUTTS-AIR-GATED-CHECKPOINT-LEAD"
WRITE_SCOPE = "docs/task-evidence/neutts-air-gated-checkpoint-lead/ only"
TASK_PREFIX = "docs/task-evidence/neutts-air-gated-checkpoint-lead/"

SOURCE_REVISION = "ac69851f28fc63a487917e7c2e27f0d75c759cba"
SOURCE_ROOT = "research/voice-conversion-eval-20261101/repos/neutts"
HF_PYTORCH_REPOSITORY = "neuphonic/neutts-air"
HF_Q4_REPOSITORY = "neuphonic/neutts-air-q4-gguf"
HF_Q8_REPOSITORY = "neuphonic/neutts-air-q8-gguf"
HF_CODEC_REPOSITORY = "neuphonic/neucodec"
HF_CACHE_DIR = ("~/.cache/huggingface/hub/"
                "models--neuphonic--neutts-air")
EXACT_LLAMA_CPP = "0.3.36"
EXACT_TRANSFORMERS = "5.1.0"
MIN_TORCH = "2.8.0"
MIN_NEUCODEC = "0.0.4"

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
    "research/voice-conversion-eval-20261101/repos/neutts/LICENSE":
        "c3308963748766e2617138a754a0f6915564aae7a4cc31c7d60dc30abf326224",
    "research/voice-conversion-eval-20261101/repos/neutts/README.md":
        "df870ea2ac040be5fdf25555d8c6b804d6119991653ee1530853186d0b26d68b",
    "research/voice-conversion-eval-20261101/repos/neutts/pyproject.toml":
        "3d74df60f0db27733b308c93b88ae95f9deaa8f396f48183b0cf4f14eb3deb94",
    "research/voice-conversion-eval-20261101/repos/neutts/CMakeLists.txt":
        "bafe8e5131ebcf804a27679b2de91ad7d8a901e70c9d22c4688d5d49a2f5e267",
    "research/voice-conversion-eval-20261101/repos/neutts/neutts/neutts.py":
        "88295403fdf5bb14dfc0df712231c57f5000afc470c9f197c590cf082f8bd7ed",
    "research/voice-conversion-eval-20261101/repos/neutts/"
    "neutts/phonemizers.py":
        "737d1138839271f06bf762552de376f1c6816460bbf5855b51192b717d67d9cb",
    "research/voice-conversion-eval-20261101/repos/neutts/"
    "neuttsair/__init__.py":
        "6757ea82810bf5b91c52dc0770eeb2e25cb4bc835af7da484951592853bdfd44",
    "research/voice-conversion-eval-20261101/repos/neutts/"
    "neuttsair/neutts.py":
        "d466a4558459667953b65b191af4710d1639efaf2ccb0511a272c72c14a37a25",
    "research/voice-conversion-eval-20261101/repos/neutts/"
    "examples/basic_streaming_example.py":
        "dde68cb743b62db45b656d77444eb3a558b91fd04fe56d33ae676d9db771e2db",
    "research/voice-conversion-eval-20261101/repos/neutts/tests/test_neutts.py":
        "8aff58d09fb04ad0cd2941b0f5d1a10fa63447ac2628be2e9eb0764429c868c7",
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
    "docs/task-evidence/survey-trn-05/README.md":
        "81b51f5696142a7fb77dd285e1db866f550de0faf5e5160ed66d15499b64c26b",
    "docs/task-evidence/survey-trn-05/report.json":
        "fd281bbacb62298102af00da3f304bd564a1f7f25b7be050e5c95ad4e4fc0773",
    "docs/task-evidence/chatterbox-nano/report.json":
        "153a48e767fe368ed063ac7ba8543b243f62071a21513d985a2f5dd74de0cf95",
    "docs/task-evidence/cosyvoice-2-0-5b/report.json":
        "aee352f4b45d3ad11af6372886a5f2a1e6458ef8d0d89d597f4c8379787b75f2",
    "docs/task-evidence/kokoro-82m/report.json":
        "ee057a4ac944dd6af9f1c8845abbcc056fb9c81076ae17bfa78ab3092c6bd06c",
    "docs/task-evidence/neutts-nano-q4/report.json":
        "9593511d7510b2ff40b99210547c0d992c3f5e1419ac104976ed3766432ac740",
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
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
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
        "id": "SDK-FND-PROVIDER",
        "title": "Provider integration boundaries and build fragments",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-TIMING"],
    },
    {
        "id": "SDK-FND-TIMING",
        "title": "Complete fixed-frame lifecycle and timing evidence",
        "component": None,
        "mode": "foundation",
        "repository": "audio-sdk",
        "depends_on": [],
    },
)

# Fixed, bounded absence probes. No recursive workspace walk is performed and
# no download is attempted. Any present path makes report generation fail.
ABSENCE_PROBES = (
    "research/voice-conversion-eval-20261101/models/neutts-air",
    "research/voice-conversion-eval-20261101/models/neutts-air/"
    "model.safetensors",
    "research/voice-conversion-eval-20261101/models/neutts-air/config.json",
    "research/voice-conversion-eval-20261101/models/neutts-air/README.md",
    "research/voice-conversion-eval-20261101/models/neutts-air-q4-gguf",
    "research/voice-conversion-eval-20261101/models/neutts-air-q4-gguf/"
    "neutts-air-q4.gguf",
    "research/voice-conversion-eval-20261101/models/neutts-air-q4-gguf/"
    "model.gguf",
    "research/voice-conversion-eval-20261101/models/neutts-air-q8-gguf",
    "research/voice-conversion-eval-20261101/models/neutts-air-q8-gguf/"
    "neutts-air-q8.gguf",
    "research/voice-conversion-eval-20261101/models/neutts-air-q8-gguf/"
    "model.gguf",
    "research/voice-conversion-eval-20261101/repos/neutts/neutts-air.gguf",
    "research/voice-conversion-eval-20261101/repos/neutts/model.gguf",
    "research/voice-conversion-eval-20261101/checkpoints/neutts-air",
    "research/voice-conversion-eval-20261101/checkpoints/neutts-air-q4-gguf",
    "research/voice-conversion-eval-20261101/checkpoints/neutts-air-q8-gguf",
    "research/voice-conversion-eval-20261101/models/neucodec",
    "research/voice-conversion-eval-20261101/checkpoints/neucodec",
    "research/voice-conversion-eval-20261101/.venv-neutts",
    "research/voice-conversion-eval-20261101/.venv-neutts-air",
    "data/assets/neutts-air",
    "data/assets/neutts-air/neutts-air-q4.gguf",
    "data/assets/neutts-air/neucodec",
    "data/assets/neucodec",
    "third_party/neutts-air",
    "third_party/neucodec",
    "deps/neutts-air",
    "adapters/neutts-air",
    "adapters/neutts-air/run.py",
    "docs/task-evidence/neutts-air-gated-checkpoint-lead/weights",
    "docs/task-evidence/neutts-air-gated-checkpoint-lead/assets",
    "LICENSES/NeuTTS-Air-weights.txt",
    "research/voice-conversion-eval-20261101/data/"
    "neutts-air-reference.wav",
)
HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--neuphonic--neutts-air/blobs",
    "~/.cache/huggingface/hub/models--neuphonic--neutts-air/snapshots",
    "~/.cache/huggingface/hub/models--neuphonic--neutts-air-q4-gguf/blobs",
    "~/.cache/huggingface/hub/models--neuphonic--neutts-air-q4-gguf/snapshots",
    "~/.cache/huggingface/hub/models--neuphonic--neucodec/blobs",
)

REQUIRED_WEIGHT_FILES = (
    "neuphonic/neutts-air PyTorch snapshot (*.safetensors)",
    "neuphonic/neutts-air-q4-gguf or -q8-gguf snapshot (*.gguf)",
    "neucodec / distill-neucodec codec snapshot",
    "exact Air model card, tokenizer/chat-template metadata and terms",
)

CHECKPOINT_GATE = {
    "candidate": "Neuphonic NeuTTS Air (~360M active parameters, phonemes)",
    "repositories": [
        HF_PYTORCH_REPOSITORY,
        HF_Q4_REPOSITORY,
        HF_Q8_REPOSITORY,
    ],
    "gating_condition": (
        "each repository requires accepting gated Hugging Face conditions "
        "before any weight file can be fetched"),
    "recorded_http_status": 401,
    "recorded_scope": (
        "research/voice-conversion-eval-20261101/README.md row "
        "'NeuTTS Nano/Air'"),
    "access_grant_present": False,
    "authenticated_access_attempted": False,
    "anonymous_download_attempted": False,
    "weights_present": False,
    "revision": None,
    "per_file_digests_present": False,
    "admitted": False,
    "used_for_evidence": False,
    "reason": (
        "The research record states that the available Nano/Air GGUF "
        "repositories require accepting gated Hugging Face conditions and "
        "returned HTTP 401, and that only public models were used. No Air "
        "access grant, snapshot revision, per-file digest or Air weight file "
        "exists in this workspace. This package does not download, "
        "reconstruct, proxy or invent one."),
}

SOURCE_PRESENCE = {
    "path": SOURCE_ROOT,
    "revision": SOURCE_REVISION,
    "license_id": "NeuTTS-Open-License-1.0",
    "license_path": SOURCE_ROOT + "/LICENSE",
    "license_sha256":
        "c3308963748766e2617138a754a0f6915564aae7a4cc31c7d60dc30abf326224",
    "project_version": "1.4.1",
    "present": True,
    "verified": True,
    "admitted": False,
    "model_executed": False,
    "weights_used": False,
    "present_components": [
        "source_code_and_repository_license_text",
        "neuttsair_subclass_module",
    ],
    "absent_components": [
        "gated_air_pytorch_weights_snapshot",
        "gated_air_q4_gguf_snapshot",
        "gated_air_q8_gguf_snapshot",
        "exact_neucodec_assets",
        "pinned_air_runtime",
        "air_model_card_terms_and_access_grant",
        "consented_reference_voice",
    ],
    "exact_source_weights_runtime_conjunction_present": False,
    "reason": (
        "The official NeuTTS code checkout is present at the pinned revision, "
        "including the `neuttsair` subclass module, and its repository LICENSE "
        "text is pinned. That text is the NeuTTS Open License v1.0, while the "
        "upstream README states that NeuTTS-Air weights are Apache-2.0; the "
        "exact Air model card that would resolve the weight terms is gated and "
        "absent. The Air weights, NeuCodec assets, pinned runtime and any "
        "consented reference voice are absent, so source presence alone is not "
        "admission."),
}

LICENSE_REVIEW = {
    "readme_air_claim": "Apache-2.0",
    "readme_source": SOURCE_ROOT + "/README.md",
    "readme_row": "| **License** | Apache 2.0 | NeuTTS Open License 1.0 |",
    "repository_license_id": "NeuTTS-Open-License-1.0",
    "repository_license_path": SOURCE_ROOT + "/LICENSE",
    "repository_license_sha256":
        "c3308963748766e2617138a754a0f6915564aae7a4cc31c7d60dc30abf326224",
    "air_model_card_present": False,
    "air_weight_terms_present": False,
    "conflict": True,
    "resolved": False,
    "resolved_license_id": None,
    "resolution_requires": (
        "the exact gated `neuphonic/neutts-air` model card and weight terms at "
        "a pinned revision, reviewed against the repository LICENSE and the "
        "Apache-2.0 claim in the upstream README"),
    "reason": (
        "The repository LICENSE text is the NeuTTS Open License v1.0 and "
        "conditions commercial use and Output use, while the README table "
        "states that NeuTTS-Air weights are Apache-2.0. That discrepancy "
        "cannot be resolved from the files present. Neither reading is "
        "asserted here, and Apache-2.0 may not be assumed for the weights or "
        "for generated Outputs."),
}

OBSERVED_HF_CACHE = {
    "path": HF_CACHE_DIR,
    "repository": HF_PYTORCH_REPOSITORY,
    "reference_revision": None,
    "blobs_present": False,
    "snapshots_present": False,
    "weights_present": False,
    "admitted": False,
    "used_for_evidence": False,
    "reason": (
        "No neuphonic Hugging Face cache entry exists. The research record "
        "states the available Nano/Air GGUF repositories are gated and "
        "returned HTTP 401, so no immutable revision or per-file digest is "
        "known. This package does not download, reconstruct or invent one."),
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
            "Exact upstream neuphonic/neutts source at a 40-hex revision, "
            "including the `neuttsair` subclass, with per-file SHA-256 pins "
            "and the repository LICENSE text from a reviewable source root."),
    },
    {
        "id": "ART-02",
        "kind": "gated_air_weights_snapshot",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": (
            "Immutable, access-granted snapshot of `neuphonic/neutts-air` "
            "(*.safetensors) or `neuphonic/neutts-air-q4-gguf` / "
            "`-q8-gguf` (*.gguf): exact filenames, 40-hex revision, per-file "
            "byte counts and SHA-256, tokenizer/chat-template metadata and "
            "the gated-access authorization record."),
    },
    {
        "id": "ART-03",
        "kind": "neucodec_assets",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": (
            "Immutable NeuCodec or distill-NeuCodec codec snapshot with exact "
            "revision, per-file byte counts and SHA-256, plus any ONNX decoder "
            "variant selected and an offline load path."),
    },
    {
        "id": "ART-04",
        "kind": "pinned_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": (
            "Reproducible isolated runtime with lock/install digest: torch >= "
            "2.8.0, transformers 5.1.0, neucodec >= 0.0.4 and, for the GGUF "
            "path, llama-cpp-python 0.3.36, loading the pinned Air snapshot "
            "offline with deterministic settings and a fixed seed."),
    },
    {
        "id": "ART-05",
        "kind": "reviewed_air_terms_and_access",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": (
            "Reviewed Air model card, weight terms and Output-use terms that "
            "resolve the Apache-2.0 README claim against the repository "
            "NeuTTS Open License v1.0, including attribution, watermark, "
            "redistribution and commercial conditions, plus the recorded "
            "gated-access grant and complete notice bundle."),
    },
    {
        "id": "ART-06",
        "kind": "consented_reference_voice_and_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": (
            "Rights-cleared, consented frozen text/reference-voice cohort with "
            "manual transcripts, language/speaker groups, exact target "
            "conditions, output-use terms and fixed-voice, mismatched-reference "
            "and ignore-reference controls."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "statement": (
            "The Air checkpoint repositories are gated and absent. The "
            "research record reports HTTP 401 without authenticated access "
            "and no Air weight snapshot exists in the workspace or cache."),
        "required_action": (
            "Supply the recorded gated-access grant and the immutable Air "
            "snapshot (PyTorch or Q4/Q8 GGUF) with exact filenames, 40-hex "
            "revision, per-file byte counts, SHA-256 and tokenizer metadata."),
        "linked_gates": ["RG-02"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "statement": (
            "No NeuCodec or distill-NeuCodec codec snapshot or ONNX decoder is "
            "present, so the waveform codec cannot be pinned or loaded."),
        "required_action": (
            "Supply the immutable NeuCodec asset set with exact repository and "
            "revision, per-file byte counts and SHA-256, and an offline load "
            "path for the selected decoder."),
        "linked_gates": ["RG-03"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "statement": (
            "No pinned Air runtime is present. The package records no "
            "qualified locked runtime, and the historical llama-cpp build in "
            "the research record belongs to the sibling Nano Q4 attempt."),
        "required_action": (
            "Supply a locked isolated runtime with install digest that loads "
            "the pinned Air snapshot and codec offline, with deterministic "
            "settings, a fixed seed and a recorded host profile."),
        "linked_gates": ["RG-04"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "statement": (
            "The Air weight/model-card terms and the gated-access conditions "
            "are unresolved: the repository LICENSE is the NeuTTS Open "
            "License v1.0 while the README states Apache-2.0 for Air weights."),
        "required_action": (
            "Record the reviewed Air model card, weight and Output terms that "
            "resolve the Apache-2.0 claim against the repository license, "
            "including commercial, attribution, watermark and redistribution "
            "obligations, plus the access grant and notice bundle."),
        "linked_gates": ["RG-01", "RG-05"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "statement": (
            "No consented reference voice, frozen text cohort, language/"
            "speaker groups, manual transcripts or output-use record exists."),
        "required_action": (
            "Supply a rights-cleared frozen Voice cohort with consent, "
            "reference availability, output use, manual transcripts, groups, "
            "exact target conditions and fixed/mismatched/ignore controls."),
        "linked_gates": ["RG-06", "RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "Source revision, license conflict and notice provenance",
        "reopen_condition": (
            "The exact checkout revision, tree digest and the complete "
            "license/notice set are supplied, and the Air Apache-2.0 README "
            "claim is reconciled with the repository NeuTTS Open License "
            "v1.0 by the pinned Air model card."),
    },
    {
        "id": "RG-02",
        "title": "Gated Air checkpoint access and weight assets",
        "reopen_condition": (
            "A recorded gated-access grant and an immutable Air PyTorch or "
            "Q4/Q8 GGUF snapshot with per-file digests and tokenizer metadata "
            "are supplied."),
    },
    {
        "id": "RG-03",
        "title": "NeuCodec codec assets and terms",
        "reopen_condition": (
            "An immutable NeuCodec snapshot with per-file digests and reviewed "
            "codec/model-card terms is supplied."),
    },
    {
        "id": "RG-04",
        "title": "Pinned runtime and offline load",
        "reopen_condition": (
            "A locked runtime with install digest loads the pinned Air "
            "snapshot and codec offline with deterministic settings and a "
            "fixed seed."),
    },
    {
        "id": "RG-05",
        "title": "Weight terms, Output use, watermark and commercial review",
        "reopen_condition": (
            "Reviewed Air model-card, weight and Output terms resolve "
            "commercial use, attribution, watermark, redistribution and "
            "notice obligations for the intended use."),
    },
    {
        "id": "RG-06",
        "title": "Rights-cleared text and voice cohort",
        "reopen_condition": (
            "An immutable cohort, manual transcripts, language/speaker groups, "
            "target conditions and matched controls are supplied."),
    },
    {
        "id": "RG-07",
        "title": "Separate content, identity, naturalness and listening",
        "reopen_condition": (
            "Pinned scorers and an approved blinded listening protocol produce "
            "reviewed content, identity and naturalness results."),
    },
    {
        "id": "RG-08",
        "title": "Alignment, timing, resources, provider intake and release",
        "reopen_condition": (
            "Target-device paced runs record alignment, first-output/tail, "
            "peaks, nonfinite behavior, CPU, memory and deadlines; a separate "
            "versioned intake with OFF default and exact-head review passes."),
    },
)

VOICE_PROFILE_ROWS = (
    {
        "id": "VP-01",
        "requirement": ("Freeze permitted input and target references, task and "
                        "language/speaker groups."),
        "status": "blocked",
        "evidence": ("No rights-cleared reference voice, consent record, "
                     "language/speaker group or frozen target condition."),
    },
    {
        "id": "VP-02",
        "requirement": "Preserve text and semantic content.",
        "status": "blocked",
        "evidence": ("No manual transcript, semantic-content adjudication or "
                     "reproduced content metric."),
    },
    {
        "id": "VP-03",
        "requirement": "Identity/similarity as a separate outcome.",
        "status": "blocked",
        "evidence": ("No reference-voice similarity score, independent encoder "
                     "or human identity rating."),
    },
    {
        "id": "VP-04",
        "requirement": "Naturalness as a separate outcome.",
        "status": "blocked",
        "evidence": ("No naturalness rating, blinded listening or preference "
                     "panel."),
    },
    {
        "id": "VP-05",
        "requirement": "Record alignment.",
        "status": "blocked",
        "evidence": ("No word/phoneme, onset or reference-content alignment."),
    },
    {
        "id": "VP-06",
        "requirement": "Record first-output/tail timing.",
        "status": "blocked",
        "evidence": ("No streaming run, chunk boundary, first-output or tail "
                     "measurement."),
    },
    {
        "id": "VP-07",
        "requirement": "Record the exact target condition.",
        "status": "blocked",
        "evidence": ("No consent, target-voice specification, language or "
                     "reference-text policy."),
    },
    {
        "id": "VP-08",
        "requirement": ("Consent, reference availability and output use as "
                        "independent gates."),
        "status": "blocked",
        "evidence": ("No consent, availability or output-use record; neither "
                     "the repository NeuTTS Open License v1.0 nor the "
                     "unverified Apache-2.0 claim clears them."),
    },
)

QUALITY_OUTCOME_ROWS = (
    {
        "id": "QO-01",
        "outcome": "text/semantic content preservation",
        "status": "blocked",
        "value": None,
        "evidence": "No qualified output or manual transcript.",
    },
    {
        "id": "QO-02",
        "outcome": "identity/similarity",
        "status": "blocked",
        "value": None,
        "evidence": "No qualified output, encoder or human identity rating.",
    },
    {
        "id": "QO-03",
        "outcome": "naturalness",
        "status": "blocked",
        "value": None,
        "evidence": "No qualified output, blinded listening or panel.",
    },
)

TIMING_ROWS = (
    {
        "id": "TR-01",
        "metric": "alignment",
        "status": "blocked",
        "value": None,
        "evidence": "No run, transcript alignment or reference-content mapping.",
    },
    {
        "id": "TR-02",
        "metric": "first-output/tail",
        "status": "blocked",
        "value": None,
        "evidence": "No streaming run or content-delay measurement.",
    },
    {
        "id": "TR-03",
        "metric": "device timing/resources",
        "status": "blocked",
        "value": None,
        "evidence": "No target-device paced run, CPU/memory or deadline data.",
    },
)

HISTORICAL_EXECUTION = {
    "id": "HE-1",
    "candidate": "Neuphonic NeuTTS Air (gated PyTorch/Q4/Q8)",
    "source": "research/voice-conversion-eval-20261101/README.md",
    "mode": "streaming cloned-voice TTS; PyTorch or GGUF; CPU",
    "acquisition_http_status": 401,
    "acquisition_succeeded": False,
    "inference_attempted": False,
    "output_present": False,
    "runtime_build_historical_success": False,
    "runtime_present": False,
    "seed_recorded": False,
    "streaming_chunks_present": False,
    "first_audio_latency_present": False,
    "identity_similarity_measured": False,
    "naturalness_measured": False,
    "manual_transcript_present": False,
    "device_timing_present": False,
    "not_rerun": True,
    "merged_task_evidence": False,
    "used_for_evidence": False,
    "qualifies": False,
    "limitations": [
        "The gated Hugging Face repositories returned HTTP 401 without "
        "authenticated access; no Air weights were acquired.",
        "No Air inference, waveform, metric, listening or timing result "
        "exists for this candidate on this host.",
        "The llama-cpp-python 0.3.36 source build in the research record was "
        "part of the separate NeuTTS Nano Q4 attempt; it is not an Air "
        "runtime and is not reused as Air evidence.",
    ],
}

REPOSITORY_BUNDLED_ASSETS = {
    "sample_directory": SOURCE_ROOT + "/samples",
    "sample_directory_present": True,
    "sample_audio_files": 9,
    "sample_embedding_files": 9,
    "sample_transcript_files": 9,
    "output_audio_path": SOURCE_ROOT + "/output.wav",
    "output_audio_sha256":
        "94a75ae8159f8c41338436b5ac652b39bdd661fd102a645431a120b7aac82b98",
    "output_audio_byte_count": 60524,
    "admitted": False,
    "used_for_evidence": False,
    "audio_read": False,
    "decoded": False,
    "signal_loaded": False,
    "byte_hash_only": True,
    "reason": (
        "The upstream checkout bundles demo reference samples and one demo "
        "output.wav. They carry no consent, cohort, output-use or run record "
        "and are covered by the repository license. They are recorded as "
        "repository content only; only the whole-file SHA-256 of output.wav is "
        "checked, and no audio is decoded, played or scored."),
}

NON_CLAIMS = (
    "No NeuTTS source copy, Air weight, Q4/Q8 GGUF snapshot, NeuCodec asset, "
    "inference runtime, reference voice, generated waveform or vendor output "
    "is bundled.",
    "No model or checkpoint was downloaded, reconstructed, proxied, loaded, "
    "imported or executed.",
    "No gated-access grant, Hugging Face authentication or alternate route was "
    "attempted or obtained.",
    "No audio was decoded, played, listened to or scored; only a whole-file "
    "SHA-256 of the repository demo output.wav is recorded.",
    "No content, identity, similarity, naturalness, alignment, first-output, "
    "tail, peak, device-timing, resource, benchmark or release result exists.",
    "No voice was cloned and no consent, reference-availability or output-use "
    "clearance is asserted.",
    "The README Apache-2.0 statement for Air weights is not confirmed as the "
    "weight or Output license; the repository LICENSE text is the NeuTTS Open "
    "License v1.0.",
    "No provider was registered, enabled by default, described in a registry "
    "or exposed through installed-v0, an ABI, the shared build or CI.",
    "The historical HTTP 401 acquisition is provenance only; it is not task "
    "evidence and qualifies nothing.",
)

PROFILE_PHRASES = (
    "Freeze permitted input and target references, task and language/speaker "
    "groups.",
    "Preserve text and semantic content, identity/similarity and naturalness "
    "as separate outcomes.",
    "Record alignment, first-output/tail timing and the exact target condition.",
    "Consent, reference availability and output use are independent gates.",
)

# --------------------------------------------------------------------------
# Admission schema (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
MANIFEST_SCHEMA_ID = "audio-sdk/neutts-air-cohort/0.1"
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
                 "license_sha256", "model_card_path", "model_card_sha256")
WEIGHT_FIELDS = ("name", "sha256", "byte_count", "terms_sha256")
RUNTIME_FIELDS = (
    "python_version",
    "backend",
    "llama_cpp_version",
    "torch_version",
    "transformers_version",
    "neucodec_version",
    "device",
    "threads",
    "deterministic_algorithms",
    "seed",
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
    "gated_access_grant",
    "weight_terms_review",
    "terms_review",
    "listening_protocol",
    "listening_panel_size",
)
CONTROL_KINDS = ("fixed_voice", "mismatched_reference", "ignore_reference")
BACKENDS = ("torch", "gguf")
AIR_WEIGHT_SUFFIXES = (".gguf", ".safetensors")
REQUIRED_CODEC_TOKEN = "neucodec"
ADMISSION_LICENSE_ID = "Apache-2.0"
MAX_WEIGHT_BYTES = 4 * 1024 * 1024 * 1024
MAX_THREADS = 64
MAX_SEED = 2 ** 31 - 1
MAX_TEXT_LENGTH = 4096
MAX_ALIGNMENT_SAMPLES = 96000
MAX_PEAK = 4.0
MAX_SAMPLE_COUNT = 1000000000
MAX_PANEL = 1000
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PYTHON_VERSION = re.compile(r"^3\.(10|11|12|13)\.[0-9]+$")
LANGUAGE = re.compile(r"^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?$")
WEIGHT_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


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
# Pins, board identity and absence probes
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
        return dict(OBSERVED_HF_CACHE, present=False, entries=[])
    entries = sorted(path.name for path in root.iterdir())
    blobs = sorted(path.name for path in (root / "blobs").iterdir()) \
        if (root / "blobs").is_dir() else []
    snapshots = sorted(path.name for path in (root / "snapshots").iterdir()) \
        if (root / "snapshots").is_dir() else []
    return dict(OBSERVED_HF_CACHE, present=True, entries=entries,
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


def _semver(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    match = SEMVER.match(value)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


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
    if source["license_id"] != ADMISSION_LICENSE_ID:
        return _reject("invalid_value", "source.license_id")
    if not _path_is_canonical(source["license_path"]):
        return _reject("invalid_path", "source.license_path")
    if not _sha(source["license_sha256"]):
        return _reject("invalid_value", "source.license_sha256")
    if not _path_is_canonical(source["model_card_path"]):
        return _reject("invalid_path", "source.model_card_path")
    if not _sha(source["model_card_sha256"]):
        return _reject("invalid_value", "source.model_card_sha256")
    if probe_paths:
        for field in ("path", "license_path", "model_card_path"):
            if not Path(source[field]).is_file():
                return _reject("probe_missing", "source." + field)
    checks += 8

    weights = document["weights"]
    if not isinstance(weights, list) or not weights:
        return _reject("invalid_value", "weights")
    names: set[str] = set()
    for weight in weights:
        code = _exact_object(weight, WEIGHT_FIELDS)
        if code:
            return _reject(code, "weights")
        if not isinstance(weight["name"], str) or not WEIGHT_NAME.match(
                weight["name"]):
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
    if not any(name.endswith(AIR_WEIGHT_SUFFIXES)
               and REQUIRED_CODEC_TOKEN not in name for name in names):
        return _reject("invalid_value", "weights.backbone_required")
    if not any(REQUIRED_CODEC_TOKEN in name for name in names):
        return _reject("invalid_value", "weights.codec_required")
    if probe_paths:
        for weight in weights:
            if not Path(weight["name"]).is_file():
                return _reject("probe_missing", "weights")
    checks += len(weights) * 4 + 2

    runtime = document["runtime"]
    code = _exact_object(runtime, RUNTIME_FIELDS)
    if code:
        return _reject(code, "runtime")
    if not isinstance(runtime["python_version"], str) \
            or not PYTHON_VERSION.match(runtime["python_version"]):
        return _reject("invalid_value", "runtime.python_version")
    if runtime["backend"] not in BACKENDS:
        return _reject("invalid_value", "runtime.backend")
    if runtime["backend"] == "gguf":
        if runtime["llama_cpp_version"] != EXACT_LLAMA_CPP:
            return _reject("invalid_value", "runtime.llama_cpp_version")
    elif runtime["llama_cpp_version"] is not None:
        return _reject("invalid_value", "runtime.llama_cpp_version")
    torch_version = _semver(runtime["torch_version"])
    if torch_version is None or torch_version < _semver(MIN_TORCH):
        return _reject("invalid_value", "runtime.torch_version")
    if runtime["transformers_version"] != EXACT_TRANSFORMERS:
        return _reject("invalid_value", "runtime.transformers_version")
    neucodec_version = _semver(runtime["neucodec_version"])
    if neucodec_version is None or neucodec_version < _semver(MIN_NEUCODEC):
        return _reject("invalid_value", "runtime.neucodec_version")
    if runtime["device"] != "cpu":
        return _reject("invalid_value", "runtime.device")
    if not _is_int(runtime["threads"]) \
            or not 1 <= runtime["threads"] <= MAX_THREADS:
        return _reject("invalid_value", "runtime.threads")
    if runtime["deterministic_algorithms"] is not True:
        return _reject("invalid_value", "runtime.deterministic_algorithms")
    if not _is_int(runtime["seed"]) \
            or not 0 <= runtime["seed"] <= MAX_SEED:
        return _reject("invalid_value", "runtime.seed")
    checks += 11

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
    kinds: set[str] = set()
    control_ids: set[str] = set()
    for control in controls:
        code = _exact_object(control, CONTROL_FIELDS)
        if code:
            return _reject(code, "controls")
        if not _slug(control["id"]) or control["id"] in control_ids:
            return _reject("invalid_value", "controls.id")
        control_ids.add(control["id"])
        if control["kind"] not in CONTROL_KINDS or control["kind"] in kinds:
            return _reject("invalid_value", "controls.kind")
        kinds.add(control["kind"])
        if control["kind"] == "mismatched_reference":
            if control["reference_id"] not in reference_ids:
                return _reject("invalid_value", "controls.reference_id")
        elif control["reference_id"] is not None:
            return _reject("invalid_value", "controls.reference_id")
    if set(CONTROL_KINDS) - kinds:
        return _reject("invalid_value", "controls.required")
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
    for field in ("consent_reference", "reference_availability", "output_use",
                  "gated_access_grant", "weight_terms_review", "terms_review",
                  "listening_protocol"):
        if not _text(rights[field]):
            return _reject("invalid_value", "rights." + field)
    if not _is_int(rights["listening_panel_size"]) \
            or not 1 <= rights["listening_panel_size"] <= MAX_PANEL:
        return _reject("invalid_value", "rights.listening_panel_size")
    checks += 8

    return _accept(checks)


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "synthetic-schema-control",
        "source": {
            "revision": SOURCE_REVISION,
            "path": "/caller/neutts-air/src",
            "license_id": ADMISSION_LICENSE_ID,
            "license_path": "/caller/neutts-air/LICENSE",
            "license_sha256": "a" * 64,
            "model_card_path": "/caller/neutts-air/MODEL_CARD.md",
            "model_card_sha256": "b" * 64,
        },
        "weights": [
            {"name": "neutts-air-q4.gguf", "sha256": "1" * 64,
             "byte_count": 1000, "terms_sha256": "2" * 64},
            {"name": "neucodec.safetensors", "sha256": "3" * 64,
             "byte_count": 1000, "terms_sha256": "4" * 64},
        ],
        "runtime": {
            "python_version": "3.11.5",
            "backend": "gguf",
            "llama_cpp_version": EXACT_LLAMA_CPP,
            "torch_version": "2.8.0",
            "transformers_version": EXACT_TRANSFORMERS,
            "neucodec_version": "0.0.4",
            "device": "cpu",
            "threads": 4,
            "deterministic_algorithms": True,
            "seed": 1729,
        },
        "references": [
            {"id": "ref-a", "path": "/caller/voice/ref-a.wav",
             "sha256": "9" * 64, "consent_id": "consent-a",
             "rights_reference": "rights-a", "language": "en-US",
             "speaker_group": "speaker-a"},
        ],
        "texts": [
            {"id": "text-a", "text": "Synthetic schema control text.",
             "language": "en-US", "speaker_group": "speaker-a",
             "reference_id": "ref-a", "reference_sha256": "9" * 64,
             "consent_id": "consent-a", "output_use": "research-only"},
        ],
        "controls": [
            {"id": "ctl-fixed", "kind": "fixed_voice", "reference_id": None},
            {"id": "ctl-mismatch", "kind": "mismatched_reference",
             "reference_id": "ref-a"},
            {"id": "ctl-ignore", "kind": "ignore_reference",
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
            "gated_access_grant": "grant-a",
            "weight_terms_review": "review-weights-a",
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

    for case_id, payload in (("root-list", []), ("root-null", None),
                             ("root-string", "x"), ("root-int", 7)):
        result = validate_manifest(payload, probe_paths=False)
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
    mutate("source-license-id-apache-missing",
           set_nested(("source", "license_id"), "NeuTTS-Open-License-1.0"))
    mutate("source-license-id-empty",
           set_nested(("source", "license_id"), ""))
    mutate("source-license-sha",
           set_nested(("source", "license_sha256"), "x" * 64))
    mutate("source-license-path-traversal",
           set_nested(("source", "license_path"), "/caller/../LICENSE"))
    mutate("source-model-card-relative",
           set_nested(("source", "model_card_path"), "MODEL_CARD.md"))
    mutate("source-model-card-traversal",
           set_nested(("source", "model_card_path"),
                      "/caller/../MODEL_CARD.md"))
    mutate("source-model-card-null",
           set_nested(("source", "model_card_path"), "/caller/mc\x00.md"))
    mutate("source-model-card-sha",
           set_nested(("source", "model_card_sha256"), "A" * 64))

    mutate("weights-empty", set_nested(("weights",), []))
    mutate("weights-not-list", set_nested(("weights",), {}))
    mutate("weights-duplicate-name",
           lambda document: document["weights"].append(
               dict(document["weights"][0])))
    mutate("weights-missing-backbone",
           lambda document: document.__setitem__(
               "weights", [document["weights"][1]]))
    mutate("weights-missing-codec",
           lambda document: document.__setitem__(
               "weights", [document["weights"][0]]))
    mutate("weights-pytorch-backbone-without-codec",
           lambda document: document.__setitem__(
               "weights",
               [{"name": "neutts-air.safetensors", "sha256": "5" * 64,
                 "byte_count": 1000, "terms_sha256": "6" * 64}]))
    mutate("weights-codec-only-safetensors",
           lambda document: document.__setitem__(
               "weights",
               [{"name": "neucodec.safetensors", "sha256": "5" * 64,
                 "byte_count": 1000, "terms_sha256": "6" * 64}]))
    mutate("weights-unknown-field",
           set_nested(("weights", 0, "extra"), "value"))
    mutate("weights-missing-field",
           del_nested(("weights", 0, "terms_sha256")))
    mutate("weights-name-traversal",
           set_nested(("weights", 0, "name"), "../neutts-air-q4.gguf"))
    mutate("weights-name-uppercase",
           set_nested(("weights", 0, "name"), "NEUTTS.gguf"))
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
           set_nested(("runtime", "python_version"), "3.9.18"))
    mutate("runtime-python-new",
           set_nested(("runtime", "python_version"), "3.14.0"))
    mutate("runtime-python-float",
           set_nested(("runtime", "python_version"), 3.11))
    mutate("runtime-backend-unknown",
           set_nested(("runtime", "backend"), "mlx"))
    mutate("runtime-backend-uppercase",
           set_nested(("runtime", "backend"), "GGUF"))
    mutate("runtime-llama-wrong",
           set_nested(("runtime", "llama_cpp_version"), "0.3.35"))
    def torch_backend_with_llama(document: dict) -> None:
        document["runtime"]["backend"] = "torch"
        document["runtime"]["llama_cpp_version"] = EXACT_LLAMA_CPP

    mutate("runtime-llama-torch-backend", torch_backend_with_llama)
    mutate("runtime-llama-null-gguf",
           set_nested(("runtime", "llama_cpp_version"), None))
    mutate("runtime-torch-old",
           set_nested(("runtime", "torch_version"), "2.7.1"))
    mutate("runtime-torch-bad",
           set_nested(("runtime", "torch_version"), "torch"))
    mutate("runtime-transformers-wrong",
           set_nested(("runtime", "transformers_version"), "5.2.0"))
    mutate("runtime-neucodec-old",
           set_nested(("runtime", "neucodec_version"), "0.0.3"))
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
    mutate("runtime-seed-negative",
           set_nested(("runtime", "seed"), -1))
    mutate("runtime-seed-huge",
           set_nested(("runtime", "seed"), MAX_SEED + 1))
    mutate("runtime-seed-bool",
           set_nested(("runtime", "seed"), True))

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
           set_nested(("references", 0, "path"), "ref.wav"))
    mutate("references-path-null",
           set_nested(("references", 0, "path"), "/caller/ref\x00.wav"))
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
           set_nested(("texts", 0, "reference_id"), "ref-missing"))
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
    mutate("controls-missing-mismatch",
           without_control("mismatched_reference"))
    mutate("controls-missing-ignore", without_control("ignore_reference"))
    mutate("controls-mismatch-unknown-ref",
           set_nested(("controls", 1, "reference_id"), "ref-missing"))
    mutate("controls-fixed-with-ref",
           set_nested(("controls", 0, "reference_id"), "ref-a"))
    mutate("controls-ignore-with-ref",
           set_nested(("controls", 2, "reference_id"), "ref-a"))

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
    mutate("rights-grant-empty",
           set_nested(("rights", "gated_access_grant"), ""))
    mutate("rights-weight-terms-empty",
           set_nested(("rights", "weight_terms_review"), ""))
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
# Contract and report blocks
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
        "backends": list(BACKENDS),
        "air_weight_suffixes": list(AIR_WEIGHT_SUFFIXES),
        "required_codec_token": REQUIRED_CODEC_TOKEN,
        "admission_license_id": ADMISSION_LICENSE_ID,
        "exact_source_revision": SOURCE_REVISION,
        "exact_llama_cpp": EXACT_LLAMA_CPP,
        "exact_transformers": EXACT_TRANSFORMERS,
        "min_torch": MIN_TORCH,
        "min_neucodec": MIN_NEUCODEC,
        "device": "cpu",
        "python_version_pattern": PYTHON_VERSION.pattern,
        "max_weight_bytes": MAX_WEIGHT_BYTES,
        "max_threads": MAX_THREADS,
        "max_seed": MAX_SEED,
        "max_text_length": MAX_TEXT_LENGTH,
        "max_alignment_samples": MAX_ALIGNMENT_SAMPLES,
        "max_peak": 4,
        "max_panel": MAX_PANEL,
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "license_id_is_caller_declaration_only": True,
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
    }


def _scope() -> dict:
    return {
        "task_local_only": True,
        "source_present": True,
        "checkpoint_present": False,
        "access_grant_present": False,
        "weights_present": False,
        "runtime_present": False,
        "weights_loaded": False,
        "model_executed": False,
        "real_corpus": False,
        "audio_read": False,
        "listening": False,
        "voice_cloning": False,
        "quality_scored": False,
        "reference_similarity_scored": False,
        "naturalness_scored": False,
        "device_timing": False,
        "benchmark": False,
        "download_attempted": False,
        "network_used": False,
        "release_claim": False,
    }


def _boundary() -> dict:
    return {
        "task_local_only": True,
        "files_outside_task_directory_written": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "public_api_abi_change": False,
        "shared_cmakelists_change": False,
        "ci_workflow_change": False,
        "default_selected": False,
        "enabled_by_default": False,
        "processor_exposure": False,
        "listening": False,
        "voice_cloning": False,
        "real_weights_or_runtime": False,
    }


def _disposition() -> dict:
    return {
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "incomplete": True,
        "not_qualified": True,
        "qualification_status": "not_qualified",
        "promotion": "defer",
        "registered": False,
        "default_enabled": False,
        "expose_as_processor": False,
        "production_exposure": "DEFER",
        "missing_result_qualifies": False,
    }


def _qualification() -> dict:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "not_qualified": True,
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
        "source_present": True,
        "checkpoint_present": False,
        "access_grant_present": False,
        "license_resolved": False,
        "weights_present": False,
        "runtime_present": False,
        "all_release_gates_blocked": True,
        "missing_result_promoted": False,
    }


def _required_results() -> dict:
    return {
        "quality_result_present": False,
        "identity_similarity_result_present": False,
        "naturalness_result_present": False,
        "listening_result_present": False,
        "alignment_result_present": False,
        "first_output_or_tail_result_present": False,
        "device_timing_result_present": False,
        "benchmark_result_present": False,
        "reference_consent_present": False,
        "checkpoint_present": False,
        "access_grant_present": False,
        "license_terms_present": False,
        "weights_present": False,
        "runtime_present": False,
        "release_claim": False,
        "no_result_qualifies": True,
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
            "Task-local NeuTTS Air gated-checkpoint feasibility evidence: "
            "source, license-conflict and absence pins, a fail-closed Voice "
            "admission schema, blocked profile accounting and eight blocked "
            "release gates. No model, Air weight, codec, runtime, voice, "
            "corpus or result."),
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
        "hf_pytorch_repository": HF_PYTORCH_REPOSITORY,
        "hf_q4_repository": HF_Q4_REPOSITORY,
        "hf_q8_repository": HF_Q8_REPOSITORY,
        "hf_codec_repository": HF_CODEC_REPOSITORY,
        "hf_reference_revision": None,
        "required_weight_files": list(REQUIRED_WEIGHT_FILES),
        "checkpoint_gate": CHECKPOINT_GATE,
        "source_presence": SOURCE_PRESENCE,
        "license_review": LICENSE_REVIEW,
        "observed_hf_cache": OBSERVED_HF_CACHE,
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "release_gates": gates,
        "voice_profile_requirements": [dict(row)
                                       for row in VOICE_PROFILE_ROWS],
        "quality_outcomes": [dict(row) for row in QUALITY_OUTCOME_ROWS],
        "timing_requirements": [dict(row) for row in TIMING_ROWS],
        "historical_execution": HISTORICAL_EXECUTION,
        "repository_bundled_assets": REPOSITORY_BUNDLED_ASSETS,
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
    "hf_pytorch_repository",
    "hf_q4_repository",
    "hf_q8_repository",
    "hf_codec_repository",
    "hf_reference_revision",
    "required_weight_files",
    "checkpoint_gate",
    "source_presence",
    "license_review",
    "observed_hf_cache",
    "required_artifacts",
    "exact_blockers",
    "release_gates",
    "voice_profile_requirements",
    "quality_outcomes",
    "timing_requirements",
    "historical_execution",
    "repository_bundled_assets",
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
    if document["mode"] != MODE:
        raise ValueError("contract_mode_mismatch")
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
    if document["checkpoint_gate"] != CHECKPOINT_GATE:
        raise ValueError("contract_checkpoint_gate_mismatch")
    if document["license_review"] != LICENSE_REVIEW:
        raise ValueError("contract_license_review_mismatch")
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
    if len(document["exact_blockers"]) != 5:
        raise ValueError("contract_blocker_count")
    for blocker in document["exact_blockers"]:
        if blocker["status"] != "open" or blocker["qualifies"] is not False:
            raise ValueError("contract_blocker_not_open")
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
    workspace_rows = absence_probes(AUDIO_ROOT)
    home_rows = home_absence_probes()
    admission = admission_controls()
    if not admission["control"]["accepted"]:
        raise ValueError("schema_control_not_accepted")
    for case in admission["cases"]:
        if case["status"] != "rejected":
            raise ValueError("admission_case_not_rejected:" + case["id"])
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "profile": PROFILE_LABEL,
        "profile_key": PROFILE,
        "mode": MODE,
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
        "license_review": LICENSE_REVIEW,
        "checkpoint_gate": CHECKPOINT_GATE,
        "absence_evidence": {
            "summary": absence_summary(workspace_rows, home_rows),
            "probes": workspace_rows,
            "home_probes": home_rows,
            "observed_hf_cache": observed_hf_cache(),
            "repository_bundled_assets": REPOSITORY_BUNDLED_ASSETS,
        },
        "admission": admission,
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "voice_profile": {
            "profile": PROFILE_LABEL,
            "rows": contract["voice_profile_requirements"],
        },
        "quality_outcomes": {
            "rows": contract["quality_outcomes"],
        },
        "timing": {
            "rows": contract["timing_requirements"],
        },
        "historical_execution": HISTORICAL_EXECUTION,
        "linked_row_identity": {
            "projection": BOARD_ROW_PROJECTION,
            "sha256": board_row_digest(BOARD_ROW_PROJECTION),
            "linked_rows": [dict(row) for row in LINKED_ROWS],
            "linked_rows_sha256": linked_rows_digest(),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
        },
        "required_results": contract["required_results"],
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
    }


def canonical_report(document: dict | None = None) -> tuple[str, str]:
    report = build_report() if document is None else document
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()
