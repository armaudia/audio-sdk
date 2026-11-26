# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-VOCOS (Vocos).

This module is standard-library only and deterministic. It contains no Vocos
source copy, JIT weight, PyTorch runtime, feature tensor, generated waveform,
listening result or vendor result. It records the exact external blocker, pins
the read-only provenance that is present, probes a fixed list of workspace and
home-cache paths to evidence the absence of the exact upstream source, the
weights and the runtime, validates a caller-supplied qualification manifest
with a fail-closed admission boundary, and builds the canonical report.

The repository contains a modified Vocos-derived source copy vendored inside a
MeanVC2 checkout. That copy is recorded and pinned as provenance only. The
exact upstream Vocos revision, its MIT license/notice set, the MeanVC2-bundled
``vocos.pt`` JIT weights, a pinned PyTorch runtime, reviewed weight/output terms
and a rights-cleared feature cohort are absent. Nothing was downloaded, loaded,
imported or executed by this package.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-VOCOS"
COMPONENT_ID = "vocos"
TASK_TITLE = "Vocos"
CONTRACT_ID = "audio-sdk/vocos-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
MODE = "implementation"
BASE_COMMIT = "a7e0aeef6a6766b7e1635685ced9d85fd2c6c4fa"
BRANCH = "swarm/SDK-VOCOS"
WRITE_SCOPE = "docs/task-evidence/vocos/ only"
TASK_PREFIX = "docs/task-evidence/vocos/"

# The containing MeanVC2 checkout and the modified ``vocos`` copy are present.
# This is not the exact upstream gemelo-ai/vocos source and it carries no
# separate Vocos license or notice file. No upstream revision is asserted.
SOURCE_REVISION = "fe5286ae205a26ad4eba64395513130bd5974b46"
SOURCE_ROOT = "research/voice-conversion-eval-20261101/repos/meanvc"
VOCOS_SOURCE_ROOT = SOURCE_ROOT + "/vocos"
UPSTREAM_PROJECT = "gemelo-ai/vocos"
VENDOR_REPOSITORY = "ASLP-lab/MeanVC"
HF_REPOSITORY = "ASLP-lab/MeanVC"
HF_REFERENCE_REVISION = None
HISTORICAL_ARTIFACT_PATH = (
    "research/accent-conversion-20261101/repos/MeanVC2/ckpts/vocos/vocos.pt")
HISTORICAL_BENCHMARK_SCRIPT = (
    "research/accent-conversion-20261101/benchmark_vocos_cpu.py")
HISTORICAL_BENCHMARK_RESULT = (
    "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json")
HISTORICAL_README = "research/accent-conversion-20261101/README.md"
HF_CACHE_DIR = "~/.cache/huggingface/hub/models--ASLP-lab--MeanVC"

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

# Immutable read-only inputs. ``source:`` rows are workspace-relative; the
# rest are SDK-worktree-relative. The mutable shared board is deliberately
# excluded from the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/benchmark_vocos_cpu.py":
        "6daf428ff4862d74b77fb7eaee4ea513c1078796eb88ead28d6d6c49ac3117c1",
    "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json":
        "1948ef27a8ff6f1ddeb24312b0a75ff0303dc6ef05bb2c659c014651cb480741",
    "research/voice-conversion-eval-20261101/repos/meanvc/LICENSE":
        "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "research/voice-conversion-eval-20261101/repos/meanvc/README.md":
        "5421a6346a5b1fdb93722307898d5019a3c22756b90333139cd0ac30a94b0f8d",
    "research/voice-conversion-eval-20261101/repos/meanvc/download_ckpt.py":
        "f08930c9af4afbe6992809dd27a2d0259f8fe2565d98c207b191f8d064d0f83d",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos/__init__.py":
        "89adaa6f53c75f96f53ee8fc79720e701f109b242d6f7a78fa51fa9a35e07ec6",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos/models.py":
        "47065294c38d042f01262e39dd50b437231506facdb13f3aaa960db9cc31b5e8",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos/modules.py":
        "f60b36d6af92cef1baa8e22f8cc6a75a18467ffbe0543e8c232992dbccecfe59",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos/pretrained.py":
        "07773c3146e072fb609dd99468ce9667e6dfbb73c869dd7472b8b142890c002d",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos/heads.py":
        "1ae5389805e63a77eaaf36502396591e34e0d92ccc4ae94e69e3f495f551a38d",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos/spectral_ops.py":
        "5577771daae83a9ffc6df3f1a3ce7f3f9c2543562c8ca3f5aff740ee2b515682",
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
    "docs/task-evidence/phase-vocoder-baseline/report.json":
        "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7",
    "docs/task-evidence/chatterbox-nano/report.json":
        "153a48e767fe368ed063ac7ba8543b243f62071a21513d985a2f5dd74de0cf95",
    "docs/task-evidence/neutts-nano-q4/report.json":
        "9593511d7510b2ff40b99210547c0d992c3f5e1419ac104976ed3766432ac740",
    "docs/task-evidence/survey-trn-05/README.md":
        "81b51f5696142a7fb77dd285e1db866f550de0faf5e5160ed66d15499b64c26b",
}

# Only stable, non-mutable identity fields are projected. ``status``, ``owner``,
# ``claim``, ``review``, ``handoff``, ``blocked_reason`` and
# ``dispatch_priority`` never enter canonical bytes and never gate this package.
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
        "id": "SDK-VOCOS-VOCODER",
        "title": "Vocos vocoder",
        "component": "vocos-vocoder",
        "mode": "research-control",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    },
    {
        "id": "SDK-VOCOS-BWE",
        "title": "Vocos-BWE",
        "component": "vocos-bwe",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                       "SDK-FND-PROVIDER"],
    },
    {
        "id": "SDK-HIFI-GAN-VOCODER",
        "title": "HiFi-GAN vocoder",
        "component": "hifi-gan-vocoder",
        "mode": "research-control",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    },
    {
        "id": "SDK-PHASE-VOCODER-BASELINE",
        "title": "Phase vocoder baseline",
        "component": "phase-vocoder-baseline",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                       "SDK-FND-PROVIDER"],
    },
)

# Fixed, bounded absence probes. No recursive workspace walk is performed and
# no download is attempted. Any present path makes report generation fail.
ABSENCE_PROBES = (
    "research/accent-conversion-20261101/repos/MeanVC2/ckpts",
    "research/accent-conversion-20261101/repos/MeanVC2/ckpts/vocos",
    "research/accent-conversion-20261101/repos/MeanVC2/ckpts/vocos/vocos.pt",
    "research/accent-conversion-20261101/repos/MeanVC2/ckpts/vocos/config.yaml",
    "research/accent-conversion-20261101/repos/MeanVC2/ckpts/vocos.pt",
    "research/voice-conversion-eval-20261101/models/vocos",
    "research/voice-conversion-eval-20261101/models/vocos-mel-24khz",
    "research/voice-conversion-eval-20261101/checkpoints/vocos",
    "research/voice-conversion-eval-20261101/checkpoints/vocos-mel-24khz",
    "research/voice-conversion-eval-20261101/repos/vocos",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos/LICENSE",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos/LICENSE.txt",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos/NOTICE",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos/pyproject.toml",
    "research/voice-conversion-eval-20261101/repos/meanvc/vocos.pt",
    "research/voice-conversion-eval-20261101/repos/meanvc/src/ckpt",
    "research/voice-conversion-eval-20261101/repos/meanvc/src/ckpt/vocos.pt",
    "research/voice-conversion-eval-20261101/repos/meanvc/ckpts",
    "research/voice-conversion-eval-20261101/.venv-vocos",
    "research/accent-conversion-20261101/.venv-vocos",
    "data/assets/vocos",
    "data/assets/vocos/vocos.pt",
    "third_party/vocos",
    "deps/vocos",
    "adapters/vocos",
    "adapters/vocos/run.py",
    "docs/task-evidence/vocos/weights",
    "docs/task-evidence/vocos/assets",
    "docs/task-evidence/vocos/runtime",
    "LICENSES/Vocos-weights.txt",
)

HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--ASLP-lab--MeanVC/blobs",
    "~/.cache/huggingface/hub/models--ASLP-lab--MeanVC/snapshots",
    "~/.cache/huggingface/hub/models--charactr--vocos-mel-24khz/blobs",
    "~/.cache/huggingface/hub/models--gemelo-ai--vocos-mel-24khz/blobs",
    "~/.cache/huggingface/hub/models--charactr--vocos-encodec-24khz/blobs",
)

REQUIRED_WEIGHT_FILES = (
    "the MeanVC2-bundled JIT decoder historically named vocos.pt (32 MB "
    "bundle; no retained file, byte count or SHA-256 is known)",
    "the exact upstream Vocos checkpoint(s) selected for the intended mel "
    "geometry, with immutable repository, revision and per-file digests",
    "the mel configuration (n_mels, hop, sample rate), JIT/torch build and "
    "any companion config or tokenizer metadata",
)

SOURCE_PRESENCE = {
    "path": VOCOS_SOURCE_ROOT,
    "vendor_repository": VENDOR_REPOSITORY,
    "vendor_revision": SOURCE_REVISION,
    "upstream_project": UPSTREAM_PROJECT,
    "upstream_revision": None,
    "license_id": "Apache-2.0",
    "license_path": SOURCE_ROOT + "/LICENSE",
    "license_sha256":
        "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "present": True,
    "verified": True,
    "admitted": False,
    "model_executed": False,
    "weights_used": False,
    "source_kind": "modified_vendored_vocos_derived_copy",
    "exact_upstream_source_present": False,
    "exact_source_weights_runtime_conjunction_present": False,
    "present_components": [
        "modified_vendored_vocos_derived_source",
        "meanvc_apache_2_0_root_license",
    ],
    "absent_components": [
        "exact_upstream_vocos_source_mit_license_and_notices",
        "vocos_jit_weights",
        "pinned_torch_runtime",
        "reviewed_weight_and_output_terms",
        "rights_cleared_feature_cohort",
    ],
    "reason": (
        "A modified Vocos-derived source copy is vendored inside the MeanVC2 "
        "checkout under the repository's Apache-2.0 root license. The exact "
        "upstream gemelo-ai/vocos revision, its MIT license and notice set and "
        "any separate package metadata are absent. The MeanVC2-bundled "
        "vocos.pt weights, a pinned Torch runtime, reviewed weight/output "
        "terms and a rights-cleared feature cohort are absent, so source "
        "presence alone is not admission."),
}

OBSERVED_HF_CACHE = {
    "path": HF_CACHE_DIR,
    "repository": HF_REPOSITORY,
    "reference_revision": HF_REFERENCE_REVISION,
    "blobs_present": False,
    "snapshots_present": False,
    "weights_present": False,
    "admitted": False,
    "used_for_evidence": False,
    "reason": (
        "No ASLP-lab/MeanVC Hugging Face cache entry exists. The research "
        "record states that the downloaded MeanVC2 bundle, including the "
        "32 MB vocos.pt decoder, was removed after the historical synthetic "
        "benchmark, so no immutable revision or per-file digest is known. "
        "This package does not download, reconstruct or invent one."),
}

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "historical_vendored_source_snapshot",
        "present": True,
        "verified": True,
        "blocked": False,
        "sha256": None,
        "revision": SOURCE_REVISION,
        "requirement": (
            "The modified Vocos-derived source copy vendored inside the "
            "MeanVC2 checkout at a 40-hex revision, with the repository "
            "Apache-2.0 root license and per-file SHA-256 pins."),
    },
    {
        "id": "ART-02",
        "kind": "exact_upstream_vocos_source_and_notices",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": (
            "The exact upstream gemelo-ai/vocos source at a 40-hex revision "
            "with its MIT license, copyright notice and any third-party "
            "notice bundle, from a reviewable source root."),
    },
    {
        "id": "ART-03",
        "kind": "vocos_weights_snapshot",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": (
            "Immutable Vocos weight snapshot: exact artifact filename(s), "
            "40-hex source revision, per-file byte counts and SHA-256, the "
            "selected format (JIT, state dict or safetensors), and the mel "
            "geometry the checkpoint expects."),
    },
    {
        "id": "ART-04",
        "kind": "pinned_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": (
            "Reproducible isolated runtime with lock/install digest: exact "
            "Python, exact torch/JIT versions, offline load, deterministic "
            "settings, a fixed seed and a recorded host profile."),
    },
    {
        "id": "ART-05",
        "kind": "reviewed_weight_and_output_terms",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": (
            "Reviewed weight/model-card and output-use terms for the selected "
            "Vocos artifact, including attribution, notice, redistribution, "
            "commercial-use and generated-output conditions."),
    },
    {
        "id": "ART-06",
        "kind": "rights_cleared_feature_cohort",
        "present": False,
        "verified": False,
        "blocked": True,
        "sha256": None,
        "requirement": (
            "Rights-cleared, consented frozen mel/feature cohort with exact "
            "geometry, hashes, language/speaker groups, output-use terms and "
            "matched-feature, mismatched-feature and zero-feature controls."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "statement": (
            "The checkout contains only a modified Vocos-derived source copy "
            "under MeanVC2's Apache-2.0 root license. The exact upstream "
            "gemelo-ai/vocos revision, its MIT license and notice set are "
            "absent."),
        "required_action": (
            "Supply the exact upstream Vocos checkout/archive at a 40-hex "
            "revision with its MIT license, copyright notice and complete "
            "notice bundle, and review it against the vendored copy."),
        "linked_gates": ["RG-01"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "statement": (
            "The MeanVC2-bundled JIT vocos.pt decoder (32 MB) was downloaded "
            "for a historical synthetic benchmark and later removed. No "
            "weight file, byte count or SHA-256 is present."),
        "required_action": (
            "Supply the immutable vocos.pt or exact upstream weight snapshot "
            "with its repository, 40-hex revision, byte count, SHA-256, "
            "format and expected mel geometry."),
        "linked_gates": ["RG-02"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "statement": (
            "No pinned Torch/JIT runtime, lock file or install digest is "
            "present. The historical decoder-only 173 ms figure is provenance "
            "from a removed environment, not a current runtime result."),
        "required_action": (
            "Supply a locked isolated runtime with install digest that loads "
            "the pinned weights offline with deterministic settings, a fixed "
            "seed and a recorded host profile."),
        "linked_gates": ["RG-04"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "statement": (
            "No reviewed Vocos weight/model-card or output-use terms are "
            "staged. The upstream MIT code license does not by itself settle "
            "the JIT weight bundle, attribution, notice or output conditions."),
        "required_action": (
            "Record a reviewed weight/model-card/license/notice bundle that "
            "resolves attribution, redistribution, commercial-use and "
            "generated-output obligations for the intended use."),
        "linked_gates": ["RG-03", "RG-05"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "statement": (
            "No rights-cleared mel/feature cohort, consent, language/speaker "
            "groups, exact geometry or matched/mismatched/zero controls "
            "exists."),
        "required_action": (
            "Supply a rights-cleared frozen feature cohort with consent, "
            "exact geometry and hashes, language/speaker groups, output-use "
            "terms and matched-feature, mismatched-feature and zero-feature "
            "controls."),
        "linked_gates": ["RG-06", "RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "Source revision, archive and license provenance",
        "reopen_condition": (
            "Exact upstream Vocos archive or checkout, 40-hex revision, tree "
            "digest, MIT license/notice set and a reviewed comparison with the "
            "vendored copy are supplied."),
    },
    {
        "id": "RG-02",
        "title": "Vocos weights identity and mel geometry",
        "reopen_condition": (
            "Immutable Vocos weight snapshot with per-file byte counts, "
            "SHA-256, format and exact mel geometry is supplied and verified "
            "offline."),
    },
    {
        "id": "RG-03",
        "title": "Weight, model-card and output terms",
        "reopen_condition": (
            "Reviewed weight/model-card/license/notice terms settle "
            "attribution, redistribution, commercial use and output use."),
    },
    {
        "id": "RG-04",
        "title": "Pinned runtime and offline load",
        "reopen_condition": (
            "A locked runtime with install digest loads the pinned weights "
            "offline with deterministic settings, a fixed seed and a recorded "
            "host profile."),
    },
    {
        "id": "RG-05",
        "title": "Consent, feature availability and output use",
        "reopen_condition": (
            "Signed consent, feature-availability, output-use and "
            "commercial-terms review are recorded for every input and output."),
    },
    {
        "id": "RG-06",
        "title": "Rights-cleared feature cohort and conditioning controls",
        "reopen_condition": (
            "Immutable feature cohort, exact geometry, language/speaker "
            "groups and matched/mismatched/zero controls are supplied."),
    },
    {
        "id": "RG-07",
        "title": "Separate content, conditioning, naturalness and listening",
        "reopen_condition": (
            "Pinned scorers and an approved blinded listening protocol produce "
            "reviewed intelligibility, conditioning-fidelity, naturalness and "
            "conditional identity results."),
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
        "evidence": ("No rights-cleared feature cohort, consent record, "
                     "language/speaker group or exact target condition."),
    },
    {
        "id": "VP-02",
        "requirement": ("Preserve content: intelligibility, semantic content "
                        "and feature conditioning."),
        "status": "blocked",
        "evidence": ("No generated waveform, manual transcript, "
                     "intelligibility score or feature-conditioning result."),
    },
    {
        "id": "VP-03",
        "requirement": ("Identity/similarity as a separate outcome, only when "
                        "the decoder is explicitly speaker-conditioned."),
        "status": "blocked",
        "evidence": ("No selected speaker-conditioned model, encoder, "
                     "reference target or human identity rating."),
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
        "evidence": ("No frame/sample alignment, onset mapping or "
                     "feature-output content mapping."),
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
        "evidence": ("No model/weight identity, mel geometry, sample rate, "
                     "hop, precision, runtime or device target."),
    },
    {
        "id": "VP-08",
        "requirement": ("Consent, reference availability and output use as "
                        "independent gates."),
        "status": "blocked",
        "evidence": ("No consent, feature-availability or output-use record; "
                     "the repository and model terms clear none of them."),
    },
)

QUALITY_OUTCOME_ROWS = (
    {
        "id": "QO-01",
        "outcome": "content/intelligibility preservation",
        "status": "blocked",
        "value": None,
        "evidence": "No qualified waveform, transcript or intelligibility score.",
    },
    {
        "id": "QO-02",
        "outcome": "mel/feature conditioning fidelity",
        "status": "blocked",
        "value": None,
        "evidence": ("No qualified waveform, pinned feature input or spectral "
                     "conditioning metric."),
    },
    {
        "id": "QO-03",
        "outcome": "naturalness",
        "status": "blocked",
        "value": None,
        "evidence": "No qualified waveform, blinded listening or panel.",
    },
    {
        "id": "QO-04",
        "outcome": "identity/similarity (conditional on a speaker conditioner)",
        "status": "blocked",
        "value": None,
        "evidence": ("No speaker-conditioned model, reference target, encoder "
                     "or human identity rating."),
    },
)

TIMING_ROWS = (
    {
        "id": "TR-01",
        "metric": "alignment",
        "status": "blocked",
        "value": None,
        "evidence": "No run, frame/sample alignment or content mapping.",
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
    {
        "id": "TR-04",
        "metric": "benchmark/real-time factor",
        "status": "blocked",
        "value": None,
        "evidence": ("No current run; the historical decoder-only figure is "
                     "provenance from a removed environment."),
    },
)

HISTORICAL_EXECUTION = {
    "id": "HE-1",
    "candidate": "MeanVC2-bundled Vocos JIT decoder",
    "source": HISTORICAL_README,
    "mode": "decoder-only synthetic mel; CPU; torch JIT",
    "evidence_class": "historical_provenance_only",
    "device": "cpu",
    "torch_threads": 4,
    "synthetic_input_only": True,
    "input_mel_shape": [1, 80, 100],
    "output_shape": [1, 15840],
    "output_duration_s": "0.99",
    "mean_decode_s": "0.17284687500214205",
    "rtf": "0.17459280303246671",
    "finite_output": True,
    "warmup_calls": 1,
    "timed_calls": 5,
    "historical_weight_bundle_mb": 32,
    "historical_acquisition_succeeded": True,
    "historical_execution_succeeded": True,
    "artifact_retained": False,
    "weights_present_now": False,
    "runtime_present_now": False,
    "output_present_now": False,
    "model_quality_measured": False,
    "drop_in_replacement_claim": False,
    "not_rerun": True,
    "merged_task_evidence": False,
    "used_for_evidence": False,
    "qualifies": False,
    "limitations": [
        "The historical run used a synthetic mel, not a rights-cleared feature "
        "cohort, and produced no retained waveform.",
        "It measured decoder-only CPU time in a removed Torch environment; it "
        "is not a current runtime, device-timing or release result.",
        "It assessed no content, conditioning fidelity, identity, naturalness, "
        "alignment, first-output or tail outcome.",
        "The 32 MB MeanVC2 bundle and its JIT file were removed after the run; "
        "no byte count or SHA-256 of the artifact is known.",
    ],
}

NON_CLAIMS = (
    "No Vocos source copy, JIT weight, PyTorch runtime, feature tensor, "
    "generated waveform or vendor output is bundled.",
    "The modified vendored source was not imported, built, loaded or executed; "
    "no weight was loaded and no model was run.",
    "No audio or feature tensor was read, decoded, played, listened to or "
    "scored. The historical benchmark numbers are quoted provenance only.",
    "No content, conditioning, identity, similarity, naturalness, alignment, "
    "first-output, tail, peak, device-timing, resource, benchmark or release "
    "result exists.",
    "No consent, feature-availability or output-use clearance is asserted.",
    "No upstream MIT notice, model-card term or weight/output term is asserted.",
    "No provider was registered, enabled by default, described in a registry "
    "or exposed through installed-v0, an ABI, the shared build or CI.",
    "The historical 173 ms / RTF 0.175 decoder-only observation qualifies "
    "nothing and is not merged task evidence.",
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
MANIFEST_SCHEMA_ID = "audio-sdk/vocos-qualification/0.1"
MANIFEST_FIELDS = (
    "schema_id",
    "cohort_id",
    "source",
    "weights",
    "runtime",
    "features",
    "controls",
    "outcomes",
    "rights",
)
SOURCE_FIELDS = ("revision", "path", "license_id", "license_path",
                 "license_sha256", "upstream_revision",
                 "upstream_license_sha256")
WEIGHT_FIELDS = ("name", "path", "sha256", "byte_count", "format",
                 "terms_sha256")
RUNTIME_FIELDS = (
    "python_version",
    "torch_version",
    "device",
    "threads",
    "deterministic_algorithms",
    "seed",
    "install_digest",
)
FEATURE_FIELDS = (
    "id",
    "path",
    "sha256",
    "sample_rate_hz",
    "n_mels",
    "hop_samples",
    "frame_count",
    "feature_kind",
    "consent_id",
    "rights_reference",
    "language",
    "speaker_group",
)
CONTROL_FIELDS = ("id", "kind", "feature_id", "feature_sha256")
OUTCOME_FIELDS = (
    "mel_spectral_convergence",
    "intelligibility_wer",
    "stoi",
    "naturalness_mos",
    "identity_similarity_cosine",
    "alignment_samples",
    "first_output_ms",
    "tail_ms",
    "peak_abs",
    "clipped_fraction",
    "nonfinite_count",
    "sample_count",
    "output_sample_rate_hz",
)
RIGHTS_FIELDS = (
    "consent_reference",
    "input_availability",
    "output_use",
    "commercial_terms_review",
    "terms_review",
    "listening_protocol",
    "listening_panel_size",
)
CONTROL_KINDS = ("matched_features", "mismatched_features", "zero_features")
WEIGHT_FORMATS = ("jit_torchscript", "safetensors", "pytorch_state_dict",
                  "onnx")
WEIGHT_SUFFIXES = (".pt", ".pth", ".safetensors", ".onnx")
FEATURE_KINDS = ("mel", "log_mel", "linear_spectrogram")
OUTPUT_SAMPLE_RATES = (16000, 22050, 24000, 44100, 48000)
INPUT_SAMPLE_RATES = (8000, 16000, 22050, 24000, 44100, 48000)
REQUIRED_WEIGHT_TOKEN = "vocos"
MAX_WEIGHT_BYTES = 8 * 1024 * 1024 * 1024
MAX_THREADS = 64
MAX_SEED = 2 ** 31 - 1
MAX_FRAME_COUNT = 1000000
MAX_HOP = 2048
MAX_N_MELS = 256
MAX_ALIGNMENT_SAMPLES = 96000
MAX_PEAK = 4
MAX_PANEL = 1000
MAX_SAMPLE_COUNT = 1000000000
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
        "feature_input_read": False,
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
    """Fail-closed Vocos qualification admission. No feature or audio is read."""
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
    if not isinstance(source["upstream_revision"], str) \
            or not HEX40.match(source["upstream_revision"]):
        return _reject("invalid_value", "source.upstream_revision")
    if not _sha(source["upstream_license_sha256"]):
        return _reject("invalid_value", "source.upstream_license_sha256")
    if probe_paths:
        for field in ("path", "license_path"):
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
        if not _path_is_canonical(weight["path"]):
            return _reject("invalid_path", "weights.path")
        if not _sha(weight["sha256"]):
            return _reject("invalid_value", "weights.sha256")
        if not _is_int(weight["byte_count"]) \
                or not 1 <= weight["byte_count"] <= MAX_WEIGHT_BYTES:
            return _reject("invalid_value", "weights.byte_count")
        if weight["format"] not in WEIGHT_FORMATS:
            return _reject("invalid_value", "weights.format")
        if not _sha(weight["terms_sha256"]):
            return _reject("invalid_value", "weights.terms_sha256")
        if probe_paths and not Path(weight["path"]).is_file():
            return _reject("probe_missing", "weights.path")
    if not any(REQUIRED_WEIGHT_TOKEN in name for name in names):
        return _reject("invalid_value", "weights.vocos_required")
    if not any(name.endswith(WEIGHT_SUFFIXES) for name in names):
        return _reject("invalid_value", "weights.suffix_required")
    checks += len(weights) * 7 + 2

    runtime = document["runtime"]
    code = _exact_object(runtime, RUNTIME_FIELDS)
    if code:
        return _reject(code, "runtime")
    if not isinstance(runtime["python_version"], str) \
            or not PYTHON_VERSION.match(runtime["python_version"]):
        return _reject("invalid_value", "runtime.python_version")
    if _semver(runtime["torch_version"]) is None:
        return _reject("invalid_value", "runtime.torch_version")
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
    if not _sha(runtime["install_digest"]):
        return _reject("invalid_value", "runtime.install_digest")
    checks += 7

    features = document["features"]
    if not isinstance(features, list) or not features:
        return _reject("invalid_value", "features")
    feature_ids: dict[str, str] = {}
    for feature in features:
        code = _exact_object(feature, FEATURE_FIELDS)
        if code:
            return _reject(code, "features")
        if not _slug(feature["id"]) or feature["id"] in feature_ids:
            return _reject("invalid_value", "features.id")
        if not _path_is_canonical(feature["path"]):
            return _reject("invalid_path", "features.path")
        if not _sha(feature["sha256"]):
            return _reject("invalid_value", "features.sha256")
        if not _is_int(feature["sample_rate_hz"]) \
                or feature["sample_rate_hz"] not in INPUT_SAMPLE_RATES:
            return _reject("invalid_value", "features.sample_rate_hz")
        if not _is_int(feature["n_mels"]) \
                or not 1 <= feature["n_mels"] <= MAX_N_MELS:
            return _reject("invalid_value", "features.n_mels")
        if not _is_int(feature["hop_samples"]) \
                or not 1 <= feature["hop_samples"] <= MAX_HOP:
            return _reject("invalid_value", "features.hop_samples")
        if not _is_int(feature["frame_count"]) \
                or not 1 <= feature["frame_count"] <= MAX_FRAME_COUNT:
            return _reject("invalid_value", "features.frame_count")
        if feature["feature_kind"] not in FEATURE_KINDS:
            return _reject("invalid_value", "features.feature_kind")
        for field in ("consent_id", "rights_reference", "speaker_group"):
            if not _slug(feature[field]):
                return _reject("invalid_value", "features." + field)
        if not isinstance(feature["language"], str) \
                or not LANGUAGE.match(feature["language"]):
            return _reject("invalid_value", "features.language")
        feature_ids[feature["id"]] = feature["sha256"]
        if probe_paths and not Path(feature["path"]).is_file():
            return _reject("probe_missing", "features.path")
    checks += len(features) * 12

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
        if control["kind"] == "zero_features":
            if control["feature_id"] is not None \
                    or control["feature_sha256"] is not None:
                return _reject("invalid_value", "controls.feature_id")
        else:
            if control["feature_id"] not in feature_ids:
                return _reject("invalid_value", "controls.feature_id")
            if control["feature_sha256"] != feature_ids[control["feature_id"]]:
                return _reject("invalid_value", "controls.feature_sha256")
    if set(CONTROL_KINDS) - kinds:
        return _reject("invalid_value", "controls.required")
    checks += len(controls) * 3 + 1

    outcomes = document["outcomes"]
    code = _exact_object(outcomes, OUTCOME_FIELDS)
    if code:
        return _reject(code, "outcomes")
    if not _is_number(outcomes["mel_spectral_convergence"]) \
            or not 0.0 <= float(outcomes["mel_spectral_convergence"]) <= 100.0:
        return _reject("invalid_value", "outcomes.mel_spectral_convergence")
    if not _is_number(outcomes["intelligibility_wer"]) \
            or not 0.0 <= float(outcomes["intelligibility_wer"]) <= 1.0:
        return _reject("invalid_value", "outcomes.intelligibility_wer")
    if not _is_number(outcomes["stoi"]) \
            or not 0.0 <= float(outcomes["stoi"]) <= 1.0:
        return _reject("invalid_value", "outcomes.stoi")
    if not _is_number(outcomes["naturalness_mos"]) \
            or not 1.0 <= float(outcomes["naturalness_mos"]) <= 5.0:
        return _reject("invalid_value", "outcomes.naturalness_mos")
    if not _is_number(outcomes["identity_similarity_cosine"]) \
            or not -1.0 <= float(outcomes["identity_similarity_cosine"]) <= 1.0:
        return _reject("invalid_value", "outcomes.identity_similarity_cosine")
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
    if not _is_int(outcomes["output_sample_rate_hz"]) \
            or outcomes["output_sample_rate_hz"] not in OUTPUT_SAMPLE_RATES:
        return _reject("invalid_value", "outcomes.output_sample_rate_hz")
    checks += 13

    rights = document["rights"]
    code = _exact_object(rights, RIGHTS_FIELDS)
    if code:
        return _reject(code, "rights")
    for field in ("consent_reference", "input_availability", "output_use",
                  "commercial_terms_review", "terms_review",
                  "listening_protocol"):
        if not _text(rights[field]):
            return _reject("invalid_value", "rights." + field)
    if not _is_int(rights["listening_panel_size"]) \
            or not 1 <= rights["listening_panel_size"] <= MAX_PANEL:
        return _reject("invalid_value", "rights.listening_panel_size")
    checks += 7

    return _accept(checks)


def _manifest_control() -> dict:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "synthetic-schema-control",
        "source": {
            "revision": SOURCE_REVISION,
            "path": "/caller/vocos/vendored",
            "license_id": "Apache-2.0",
            "license_path": "/caller/vocos/LICENSE",
            "license_sha256": "a" * 64,
            "upstream_revision": "b" * 40,
            "upstream_license_sha256": "c" * 64,
        },
        "weights": [
            {"name": "vocos.pt", "path": "/caller/vocos/vocos.pt",
             "sha256": "1" * 64, "byte_count": 33554432,
             "format": "jit_torchscript", "terms_sha256": "2" * 64},
        ],
        "runtime": {
            "python_version": "3.11.5",
            "torch_version": "2.5.1",
            "device": "cpu",
            "threads": 4,
            "deterministic_algorithms": True,
            "seed": 1729,
            "install_digest": "3" * 64,
        },
        "features": [
            {"id": "mel-a", "path": "/caller/vocos/mel-a.npy",
             "sha256": "9" * 64, "sample_rate_hz": 24000, "n_mels": 80,
             "hop_samples": 240, "frame_count": 100, "feature_kind": "mel",
             "consent_id": "consent-a", "rights_reference": "rights-a",
             "language": "en-US", "speaker_group": "speaker-a"},
            {"id": "mel-b", "path": "/caller/vocos/mel-b.npy",
             "sha256": "8" * 64, "sample_rate_hz": 24000, "n_mels": 80,
             "hop_samples": 240, "frame_count": 100, "feature_kind": "mel",
             "consent_id": "consent-b", "rights_reference": "rights-b",
             "language": "en-US", "speaker_group": "speaker-b"},
        ],
        "controls": [
            {"id": "ctl-matched", "kind": "matched_features",
             "feature_id": "mel-a", "feature_sha256": "9" * 64},
            {"id": "ctl-mismatch", "kind": "mismatched_features",
             "feature_id": "mel-b", "feature_sha256": "8" * 64},
            {"id": "ctl-zero", "kind": "zero_features",
             "feature_id": None, "feature_sha256": None},
        ],
        "outcomes": {
            "mel_spectral_convergence": 0.1,
            "intelligibility_wer": 0.0,
            "stoi": 0.95,
            "naturalness_mos": 3.0,
            "identity_similarity_cosine": 0.5,
            "alignment_samples": 0,
            "first_output_ms": 1.0,
            "tail_ms": 1.0,
            "peak_abs": 0.5,
            "clipped_fraction": 0.0,
            "nonfinite_count": 0,
            "sample_count": 24000,
            "output_sample_rate_hz": 24000,
        },
        "rights": {
            "consent_reference": "consent-a",
            "input_availability": "caller-supplied",
            "output_use": "research-only",
            "commercial_terms_review": "review-commercial-a",
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
                             ("root-string", "x"), ("root-int", 7),
                             ("root-bool", True)):
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
    mutate("cohort-bool", set_top("cohort_id", True))

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
    mutate("source-path-int", set_nested(("source", "path"), 7))
    mutate("source-license-id",
           set_nested(("source", "license_id"), "MIT"))
    mutate("source-license-sha",
           set_nested(("source", "license_sha256"), "x" * 64))
    mutate("source-upstream-revision-short",
           set_nested(("source", "upstream_revision"), "b" * 39))
    mutate("source-upstream-revision-uppercase",
           set_nested(("source", "upstream_revision"), "B" * 40))
    mutate("source-upstream-license",
           set_nested(("source", "upstream_license_sha256"), "bad"))

    mutate("weights-empty", set_nested(("weights",), []))
    mutate("weights-not-list", set_nested(("weights",), {}))
    for field in WEIGHT_FIELDS:
        mutate("missing-weight-" + field,
               del_nested(("weights", 0, field)))
    mutate("unknown-weight-field",
           set_nested(("weights", 0, "extra"), "value"))
    mutate("weights-duplicate-name",
           lambda document: document["weights"].append(
               dict(document["weights"][0])))
    mutate("weights-missing-vocos",
           lambda document: document["weights"].__setitem__(
               0, dict(document["weights"][0], name="decoder.pt")))
    mutate("weights-bad-suffix",
           lambda document: document["weights"].__setitem__(
               0, dict(document["weights"][0], name="vocos.gguf")))
    mutate("weights-name-traversal",
           set_nested(("weights", 0, "name"), "../vocos.pt"))
    mutate("weights-name-uppercase",
           set_nested(("weights", 0, "name"), "VOCOS.pt"))
    mutate("weights-path-relative",
           set_nested(("weights", 0, "path"), "vocos.pt"))
    mutate("weights-path-traversal",
           set_nested(("weights", 0, "path"), "/caller/../vocos.pt"))
    mutate("weights-path-null",
           set_nested(("weights", 0, "path"), "/caller/vocos.pt\x00"))
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
    mutate("weights-format",
           set_nested(("weights", 0, "format"), "pickle"))
    mutate("weights-terms-sha",
           set_nested(("weights", 0, "terms_sha256"), "bad"))

    for field in RUNTIME_FIELDS:
        mutate("missing-runtime-" + field, del_nested(("runtime", field)))
    mutate("unknown-runtime-field",
           set_nested(("runtime", "extra"), "value"))
    mutate("runtime-python-old",
           set_nested(("runtime", "python_version"), "3.9.18"))
    mutate("runtime-python-float",
           set_nested(("runtime", "python_version"), 3.11))
    mutate("runtime-torch-bad",
           set_nested(("runtime", "torch_version"), "torch"))
    mutate("runtime-torch-empty",
           set_nested(("runtime", "torch_version"), ""))
    mutate("runtime-device-cuda",
           set_nested(("runtime", "device"), "cuda"))
    mutate("runtime-threads-zero",
           set_nested(("runtime", "threads"), 0))
    mutate("runtime-threads-huge",
           set_nested(("runtime", "threads"), MAX_THREADS + 1))
    mutate("runtime-threads-bool",
           set_nested(("runtime", "threads"), True))
    mutate("runtime-threads-float",
           set_nested(("runtime", "threads"), 4.0))
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
    mutate("runtime-seed-float",
           set_nested(("runtime", "seed"), 1.0))
    mutate("runtime-install-digest",
           set_nested(("runtime", "install_digest"), "bad"))

    mutate("features-empty", set_nested(("features",), []))
    mutate("features-not-list", set_nested(("features",), {}))
    for field in FEATURE_FIELDS:
        mutate("missing-feature-" + field,
               del_nested(("features", 0, field)))
    mutate("unknown-feature-field",
           set_nested(("features", 0, "extra"), "value"))
    mutate("features-duplicate-id",
           lambda document: document["features"].append(
               dict(document["features"][0])))
    mutate("features-path-relative",
           set_nested(("features", 0, "path"), "mel-a.npy"))
    mutate("features-path-traversal",
           set_nested(("features", 0, "path"), "/caller/../mel-a.npy"))
    mutate("features-path-null",
           set_nested(("features", 0, "path"), "/caller/mel-a.npy\x00"))
    mutate("features-sha",
           set_nested(("features", 0, "sha256"), "bad"))
    mutate("features-rate-bad",
           set_nested(("features", 0, "sample_rate_hz"), 32000))
    mutate("features-rate-bool",
           set_nested(("features", 0, "sample_rate_hz"), True))
    mutate("features-rate-float",
           set_nested(("features", 0, "sample_rate_hz"), 24000.0))
    mutate("features-nmels-zero",
           set_nested(("features", 0, "n_mels"), 0))
    mutate("features-nmels-huge",
           set_nested(("features", 0, "n_mels"), MAX_N_MELS + 1))
    mutate("features-nmels-bool",
           set_nested(("features", 0, "n_mels"), True))
    mutate("features-nmels-float",
           set_nested(("features", 0, "n_mels"), 80.0))
    mutate("features-hop-zero",
           set_nested(("features", 0, "hop_samples"), 0))
    mutate("features-hop-huge",
           set_nested(("features", 0, "hop_samples"), MAX_HOP + 1))
    mutate("features-hop-bool",
           set_nested(("features", 0, "hop_samples"), True))
    mutate("features-frames-zero",
           set_nested(("features", 0, "frame_count"), 0))
    mutate("features-frames-huge",
           set_nested(("features", 0, "frame_count"),
                      MAX_FRAME_COUNT + 1))
    mutate("features-frames-bool",
           set_nested(("features", 0, "frame_count"), True))
    mutate("features-kind",
           set_nested(("features", 0, "feature_kind"), "unknown"))
    mutate("features-consent-empty",
           set_nested(("features", 0, "consent_id"), ""))
    mutate("features-rights-empty",
           set_nested(("features", 0, "rights_reference"), ""))
    mutate("features-speaker-empty",
           set_nested(("features", 0, "speaker_group"), ""))
    mutate("features-language",
           set_nested(("features", 0, "language"), "English"))

    mutate("controls-empty", set_nested(("controls",), []))
    mutate("controls-not-list", set_nested(("controls",), {}))
    for field in CONTROL_FIELDS:
        mutate("missing-control-" + field,
               del_nested(("controls", 0, field)))
    mutate("controls-unknown-field",
           set_nested(("controls", 0, "extra"), "value"))
    mutate("controls-duplicate-id",
           lambda document: document["controls"].append(
               dict(document["controls"][0])))
    mutate("controls-bad-kind",
           set_nested(("controls", 0, "kind"), "unknown"))
    mutate("controls-duplicate-kind",
           set_nested(("controls", 1, "kind"), "matched_features"))
    mutate("controls-missing-matched",
           lambda document: document.__setitem__(
               "controls", [row for row in document["controls"]
                            if row["kind"] != "matched_features"]))
    mutate("controls-missing-mismatch",
           lambda document: document.__setitem__(
               "controls", [row for row in document["controls"]
                            if row["kind"] != "mismatched_features"]))
    mutate("controls-missing-zero",
           lambda document: document.__setitem__(
               "controls", [row for row in document["controls"]
                            if row["kind"] != "zero_features"]))
    mutate("controls-matched-unknown",
           set_nested(("controls", 0, "feature_id"), "mel-missing"))
    mutate("controls-matched-digest",
           set_nested(("controls", 0, "feature_sha256"), "0" * 64))
    mutate("controls-mismatch-unknown",
           set_nested(("controls", 1, "feature_id"), "mel-missing"))
    mutate("controls-mismatch-digest",
           set_nested(("controls", 1, "feature_sha256"), "0" * 64))
    mutate("controls-zero-with-id",
           set_nested(("controls", 2, "feature_id"), "mel-a"))
    mutate("controls-zero-with-sha",
           set_nested(("controls", 2, "feature_sha256"), "9" * 64))
    mutate("controls-matched-null",
           set_nested(("controls", 0, "feature_id"), None))
    mutate("controls-mismatch-null",
           set_nested(("controls", 1, "feature_id"), None))

    for field in OUTCOME_FIELDS:
        mutate("missing-outcome-" + field, del_nested(("outcomes", field)))
    mutate("unknown-outcome-field",
           set_nested(("outcomes", "extra"), "value"))
    mutate("outcome-convergence-nan",
           set_nested(("outcomes", "mel_spectral_convergence"),
                      float("nan")))
    mutate("outcome-convergence-inf",
           set_nested(("outcomes", "mel_spectral_convergence"),
                      float("inf")))
    mutate("outcome-convergence-neg",
           set_nested(("outcomes", "mel_spectral_convergence"), -0.1))
    mutate("outcome-convergence-high",
           set_nested(("outcomes", "mel_spectral_convergence"), 100.1))
    mutate("outcome-wer-nan",
           set_nested(("outcomes", "intelligibility_wer"), float("nan")))
    mutate("outcome-wer-inf",
           set_nested(("outcomes", "intelligibility_wer"), float("inf")))
    mutate("outcome-wer-neg",
           set_nested(("outcomes", "intelligibility_wer"), -0.1))
    mutate("outcome-wer-high",
           set_nested(("outcomes", "intelligibility_wer"), 1.1))
    mutate("outcome-wer-bool",
           set_nested(("outcomes", "intelligibility_wer"), True))
    mutate("outcome-stoi-neg",
           set_nested(("outcomes", "stoi"), -0.1))
    mutate("outcome-stoi-high",
           set_nested(("outcomes", "stoi"), 1.1))
    mutate("outcome-mos-low",
           set_nested(("outcomes", "naturalness_mos"), 0.9))
    mutate("outcome-mos-high",
           set_nested(("outcomes", "naturalness_mos"), 5.1))
    mutate("outcome-cosine-low",
           set_nested(("outcomes", "identity_similarity_cosine"), -1.1))
    mutate("outcome-cosine-high",
           set_nested(("outcomes", "identity_similarity_cosine"), 1.1))
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
    mutate("outcome-clipped-negative",
           set_nested(("outcomes", "clipped_fraction"), -0.1))
    mutate("outcome-nonfinite-count",
           set_nested(("outcomes", "nonfinite_count"), 1))
    mutate("outcome-sample-zero",
           set_nested(("outcomes", "sample_count"), 0))
    mutate("outcome-sample-bool",
           set_nested(("outcomes", "sample_count"), True))
    mutate("outcome-sample-float",
           set_nested(("outcomes", "sample_count"), 24000.0))
    mutate("outcome-output-rate",
           set_nested(("outcomes", "output_sample_rate_hz"), 32000))

    for field in RIGHTS_FIELDS:
        mutate("missing-rights-" + field, del_nested(("rights", field)))
    mutate("unknown-rights-field",
           set_nested(("rights", "extra"), "value"))
    mutate("rights-consent-empty",
           set_nested(("rights", "consent_reference"), ""))
    mutate("rights-availability-empty",
           set_nested(("rights", "input_availability"), ""))
    mutate("rights-output-empty",
           set_nested(("rights", "output_use"), ""))
    mutate("rights-commercial-empty",
           set_nested(("rights", "commercial_terms_review"), ""))
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
    mutate("rights-panel-float",
           set_nested(("rights", "listening_panel_size"), 3.0))

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
            "feature_input_read": False,
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
        "feature_fields": list(FEATURE_FIELDS),
        "control_fields": list(CONTROL_FIELDS),
        "control_kinds": list(CONTROL_KINDS),
        "outcome_fields": list(OUTCOME_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "weight_formats": list(WEIGHT_FORMATS),
        "weight_suffixes": list(WEIGHT_SUFFIXES),
        "feature_kinds": list(FEATURE_KINDS),
        "required_weight_token": REQUIRED_WEIGHT_TOKEN,
        "exact_vendor_revision": SOURCE_REVISION,
        "upstream_project": UPSTREAM_PROJECT,
        "upstream_revision": None,
        "device": "cpu",
        "python_version_pattern": PYTHON_VERSION.pattern,
        "torch_version_policy": "pinned_semver_recorded_by_caller",
        "input_sample_rates_hz": list(INPUT_SAMPLE_RATES),
        "output_sample_rates_hz": list(OUTPUT_SAMPLE_RATES),
        "max_weight_bytes": MAX_WEIGHT_BYTES,
        "max_threads": MAX_THREADS,
        "max_seed": MAX_SEED,
        "max_frame_count": MAX_FRAME_COUNT,
        "max_hop_samples": MAX_HOP,
        "max_n_mels": MAX_N_MELS,
        "max_alignment_samples": MAX_ALIGNMENT_SAMPLES,
        "max_peak": MAX_PEAK,
        "max_panel": MAX_PANEL,
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "audio_read": False,
        "feature_input_read": False,
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
        "model_io_claimed": False,
        "sdk_compatible": False,
    }


def _scope() -> dict:
    return {
        "task_local_only": True,
        "source_present": True,
        "exact_upstream_source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "weights_loaded": False,
        "model_executed": False,
        "real_corpus": False,
        "audio_read": False,
        "feature_input_read": False,
        "listening": False,
        "quality_scored": False,
        "intelligibility_scored": False,
        "conditioning_scored": False,
        "identity_scored": False,
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
        "intelligibility_result": False,
        "conditioning_result": False,
        "identity_similarity_result": False,
        "naturalness_result": False,
        "listening_result": False,
        "alignment_result": False,
        "first_output_or_tail_result": False,
        "device_timing_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "source_present": True,
        "exact_upstream_source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "all_release_gates_blocked": True,
        "missing_result_promoted": False,
    }


def _required_results() -> dict:
    return {
        "quality_result_present": False,
        "intelligibility_result_present": False,
        "conditioning_result_present": False,
        "identity_similarity_result_present": False,
        "naturalness_result_present": False,
        "listening_result_present": False,
        "alignment_result_present": False,
        "first_output_or_tail_result_present": False,
        "device_timing_result_present": False,
        "benchmark_result_present": False,
        "reference_consent_present": False,
        "exact_upstream_source_present": False,
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
            "Task-local Vocos readiness evidence: source and absence pins, a "
            "fail-closed Voice/qualification admission schema, blocked "
            "profile accounting and eight blocked release gates. No model, "
            "JIT weight, Torch runtime, feature cohort or result."),
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
        "upstream_project": UPSTREAM_PROJECT,
        "upstream_revision": None,
        "historical_artifact_path": HISTORICAL_ARTIFACT_PATH,
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
    "upstream_project",
    "upstream_revision",
    "historical_artifact_path",
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
            if key == "task_local_only" or key == "source_present":
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
