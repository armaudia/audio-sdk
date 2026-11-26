# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-NANSY-ANALYSIS-RESYNTHESIS.

This module is NOT NANSY. It does not implement, approximate, simulate, train
or run the NANSY analysis/resynthesis network. It contains no source tree,
checkpoint, weight, encoder, decoder, vocoder, runtime, real speech, reference
voice or candidate output. The catalogued evidence is one NeurIPS 2021 paper
lead plus research/survey prose; no official runnable source, weight artifact,
pinned runtime, reviewed terms or matched voice cohort is present locally.

The module therefore builds a bounded, deterministic blocker report:

* strict request validation that rejects missing, unknown, invalid, nonfinite,
  out-of-range and stale inputs before any candidate call;
* explicit, bounded, read-only source/weights/runtime absence probes;
* a fail-closed caller-supplied asset declaration shape check;
* synthetic harness stimuli for identity and rejection controls only;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

No network, model weight, real corpus audio, native library or download is
used. No analysis, resynthesis or parity output is produced, and no result
qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import struct
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

TASK = "SDK-NANSY-ANALYSIS-RESYNTHESIS"
TASK_TITLE = "NANSY analysis/resynthesis"
COMPONENT_ID = "nansy-analysis-resynthesis"
COMPONENT_NAME = "NANSY analysis/resynthesis"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "voice"
PROFILE_LABEL = "Voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/nansy-analysis-resynthesis/ only"
TASK_PREFIX = "docs/task-evidence/nansy-analysis-resynthesis/"
CONTRACT_SCHEMA_ID = "audio-sdk/nansy-analysis-resynthesis-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/nansy-analysis-resynthesis-report/0.1"
DECLARATION_SCHEMA_ID = (
    "audio-sdk/nansy-analysis-resynthesis-asset-declaration/0.1")
BASE_COMMIT = "e3e3deccb3c852bce8255305700be219ccceadb8"
BRANCH = "swarm/SDK-NANSY-ANALYSIS-RESYNTHESIS"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
HOP_SAMPLES = 160
CHANNELS = 1
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0

PAPER_URL = ("https://proceedings.neurips.cc/paper_files/paper/2021/file/"
             "87682805257e619d49b8e0dfdc14affa-Paper.pdf")
PAPER_TITLE = "NANSY analysis and resynthesis paper"
CANDIDATE_NAME = "NANSY analysis/resynthesis"
CANDIDATE_FAMILY = "disentangled_neural_analysis_resynthesis"
TARGET_CONDITION = "analysis_resynthesis_identity_target_unspecified"
LIFECYCLES = ("prepared", "processing")
STAGES = ("analysis", "resynthesis", "round_trip")

SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    """Locate the audioml root without a recursive walk or network use."""
    override = os.environ.get("AUDIOML_ROOT") or os.environ.get("SOURCE_ROOT")
    candidates: List[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()


def _find_sdk_root() -> Path:
    """Locate this SDK worktree, allowing a cold-start verifier override."""
    override = os.environ.get("AUDIO_SDK_ROOT")
    if override:
        candidate = Path(override)
        if (candidate / "CONTRACTS.md").is_file():
            return candidate.resolve()
    return WORKTREE


SDK_ROOT = _find_sdk_root()

# Read-only inputs. `source:` paths are workspace-relative; `sdk:` paths are
# SDK-worktree-relative. The mutable shared board is deliberately absent.
SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/mp-senet/report.json":
        "989c64c1c069e55d9b871f308a607669507d605247f85f614f13132efa2b010f",
    "docs/task-evidence/nara-wpe-reference-tools/report.json":
        "7ed65ec26de33815a42514b51921cc939e72fb2f57294e31e56b357f5ac87ee9",
    "docs/task-evidence/neural-atsm/report.json":
        "3dd7b111cb8af978fd5581f0ffbab6d6907e8ba2eb3e9469b19b15af72e1057b",
    "docs/task-evidence/survey-trn-02/report.json":
        "a594cd9e0c1c638835e11263c84b147b592ac1f344f0e83da4480ef310703f3a",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")

PROFILE_SOURCE_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
PROFILE_PHRASES = (
    "Freeze permitted input and target references, task and language/speaker "
    "groups.",
    "Preserve text and semantic content, identity/similarity and naturalness "
    "as separate outcomes.",
    "Record alignment, first-output/tail timing and the exact target condition.",
    "Consent, reference availability and output use are independent gates.",
)

LOCAL_FILES = (
    "LICENSES.md",
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
EXPECTED_DIR_FILES = set(LOCAL_FILES) | {"SOURCES.sha256"}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".h5",
    ".lib", ".m4a", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o",
    ".onnx", ".opus", ".otf", ".pcap", ".pcapng", ".pt", ".pth", ".pyc",
    ".safetensors", ".so", ".tar", ".ttf", ".wav", ".wasm", ".weights",
    ".zip",
}

# Fixed probes only; no recursive walk and no network.
WORKSPACE_PROBES = (
    "data/checkouts/nansy",
    "data/checkouts/NANSY",
    "data/checkouts/nansy-analysis-resynthesis",
    "data/models/nansy",
    "data/models/nansy-analysis-resynthesis",
    "data/envs/nansy",
    "data/envs/nansy-analysis-resynthesis",
    "data/reference/nansy",
    "data/audio/nansy",
    "data/runs/nansy",
    "research/nansy",
    "research/nansy-analysis-resynthesis",
)
WORKTREE_PROBES = (
    "adapters/nansy-analysis-resynthesis",
    "schemas/providers/nansy-analysis-resynthesis",
    "third_party/nansy",
    "third_party/nansy-analysis-resynthesis",
    "build/check-env/lib/python3.12/site-packages/nansy",
)
HOME_PROBES = (
    "~/.cache/nansy",
    "~/.cache/huggingface/hub/models--nansy",
    "~/.cache/huggingface/hub/models--nansy-analysis-resynthesis",
)

NON_CLAIMS = [
    "No NANSY source, code snapshot, checkpoint, weight, config, encoder, "
    "decoder, vocoder or inference implementation is present, imported, "
    "deserialised, loaded or executed.",
    "No PyTorch, TensorFlow, ONNX Runtime or other model runtime is installed, "
    "imported or linked by this package.",
    "No real speech, corpus, reference voice, target voice, synthetic speech, "
    "resynthesis or candidate output is read, generated or produced.",
    "No analysis-to-waveform parity, speech-preservation, identity, "
    "naturalness, listening, alignment, device-timing or benchmark result is "
    "reproduced.",
    "The caller-supplied asset declaration is a fail-closed shape check only; "
    "it never resolves a path, hashes an external byte, admits a presence "
    "claim or grants qualification.",
    "No provider, descriptor, registry, default, public ABI, shared build, CI "
    "workflow, board or handoff change exists.",
    "The paper URL and survey prose are source-reported context only and are "
    "not promoted to measured evidence.",
    "No network access or download is attempted; absent artifacts are not "
    "fabricated, reconstructed, mirrored or substituted.",
    "No sibling voice-conversion, vocoder or analysis evidence is inherited, "
    "pooled or treated as a NANSY result.",
]

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/nansy-analysis-resynthesis/ is touched.",
    "The reference is a task-local evidence builder, not NANSY.",
    "All harness stimuli are analytic or seeded synthetic; no weights are used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
    "The mutable full plan/swarm/TASKS.json is never hashed or pinned.",
)

GATES = (
    {
        "id": "RG-01",
        "gate": "exact_source_revision_and_license_provenance",
        "status": "blocked",
        "reason": (
            "No official NANSY source repository, release archive, immutable "
            "40-hex revision, tree digest or upstream licence text was "
            "identified or staged. The linked record is a NeurIPS 2021 paper "
            "URL only."),
        "reopen": (
            "Stage the exact licensed NANSY source at an immutable revision "
            "with a tree digest, file count and complete licence/notice/README "
            "bundle, then record independent review."),
    },
    {
        "id": "RG-02",
        "gate": "exact_weights_config_and_weight_terms",
        "status": "blocked",
        "reason": (
            "No official NANSY checkpoint, weight file, inference config, "
            "model card or weight licence/terms record exists locally. No "
            "file name, byte count, SHA-256 or tensor layout is asserted."),
        "reopen": (
            "Stage every required checkpoint, config, normalisation and "
            "vocoder asset at an immutable identity with per-file byte counts "
            "and SHA-256, plus reviewed weight/model-card terms."),
    },
    {
        "id": "RG-03",
        "gate": "pinned_runtime_offline_load_and_geometry",
        "status": "blocked",
        "reason": (
            "No hash-pinned NANSY runtime exists. No interpreter lock, wheel "
            "hash set, device, dtype, determinism setting, analysis frame/hop, "
            "lookahead, reset or drain behaviour is documented or present."),
        "reopen": (
            "Create a frozen, hash-pinned offline runtime that loads the "
            "pinned snapshot with a fail-closed missing-asset path and records "
            "the exact analysis/resynthesis sample rate, frame, hop, channels "
            "and latency."),
    },
    {
        "id": "RG-04",
        "gate": "code_weight_training_data_input_and_output_use_rights",
        "status": "blocked",
        "reason": (
            "No code, weight, training-data, corpus, source-voice, "
            "target-voice, consent or output-use rights record exists. A paper "
            "lead grants no redistribution or product-use right."),
        "reopen": (
            "Record reviewed code/weight/training-data/corpus terms, signed "
            "source and target voice consent, reference availability and "
            "output-use/redistribution decisions."),
    },
    {
        "id": "RG-05",
        "gate": "reproduced_analysis_to_waveform_parity_and_preservation",
        "status": "blocked",
        "reason": (
            "No candidate execution, analysis feature, resynthesised waveform, "
            "output hash, duration, level, peak, nonfinite count or "
            "speech-preservation measurement exists on the exact runtime."),
        "reopen": (
            "Execute the pinned assets offline and record deterministic "
            "analysis-to-waveform parity, tolerated reconstruction difference, "
            "speech preservation, peaks, nonfinite behaviour and exact "
            "repeats."),
    },
    {
        "id": "RG-06",
        "gate": "voice_profile_against_rights_cleared_cohort",
        "status": "blocked",
        "reason": (
            "No rights-cleared input/reference pair, frozen language/speaker "
            "group, exact target condition or matched cohort exists. Content, "
            "identity/similarity and naturalness are unmeasured."),
        "reopen": (
            "Freeze a rights-cleared cohort with permitted input and target "
            "references, language/speaker groups and exact target conditions, "
            "then score content, identity/similarity and naturalness "
            "separately."),
    },
    {
        "id": "RG-07",
        "gate": "alignment_timing_resources_and_listening",
        "status": "blocked",
        "reason": (
            "No first-output/tail timing, alignment, content delay, paced "
            "device run, CPU/memory measurement or authorized listening panel "
            "exists for NANSY."),
        "reopen": (
            "Measure alignment, first-output/tail timing, content delay, CPU, "
            "memory and callback suitability on the intended device, and "
            "complete an approved blinded listening protocol."),
    },
    {
        "id": "RG-08",
        "gate": "provider_intake_public_surface_review_and_release",
        "status": "blocked",
        "reason": (
            "No caller-supplied-asset adapter, provider intake, descriptor, "
            "registry/default change, public-surface decision, independent "
            "exact-head review or release approval exists."),
        "reopen": (
            "After every prior gate clears, complete opt-in OFF-by-default "
            "provider intake with a versioned descriptor, obtain independent "
            "exact-head review, and approve release separately."),
    },
)

UPSTREAM_BLOCKER = {
    "status": "blocked_source_weights_runtime_rights_absent",
    "artifact": (
        "Official NANSY analysis/resynthesis source, checkpoint/weights, "
        "pinned runtime, reference and target voice rights required to load "
        "and evaluate it"),
    "source": {
        "status": "absent",
        "repository": None,
        "revision": None,
        "tree_digest": None,
        "file_count": None,
        "license": None,
    },
    "weights": {
        "status": "absent",
        "artifact": "NANSY official checkpoint",
        "sha256": None,
        "byte_count": None,
        "license": None,
    },
    "runtime": {
        "status": "absent_unpinned",
        "required": [
            "a hash-pinned CPU PyTorch or ONNX Runtime build compatible with "
            "the official checkpoint",
            "the content, pitch, energy and timbre analysis components that "
            "the official checkpoint declares, each at a pinned version",
            "the synthesis generator and vocoder declared by the checkpoint",
            "a lockfile or wheel hash set plus a fail-closed offline loader",
        ],
        "sha256": None,
        "lockfile": None,
    },
    "expected_license": (
        "None identified: no upstream code licence, weight/model-card terms, "
        "training-data statement or voice terms were located, so every future "
        "use requires an explicit reviewed licence decision"),
    "pinned_revision": None,
    "source_digest": None,
    "runtime_digest": None,
    "no_upstream_parity_claim": True,
    "rights_requirement": (
        "Reviewed code and weight terms, training-data and corpus rights, "
        "explicit source-speaker and target-voice consent, reference "
        "availability and output-use terms, and an approved redistribution "
        "model for the runtime and any resynthesised output are required "
        "before any reproduction, adapter or release claim."),
    "workspace_search": (
        "Fixed read-only path probes over workspace, SDK-worktree and home "
        "cache locations found no NANSY source, checkpoint, weight file, "
        "pinned runtime or adapter."),
    "not_attempted": [
        "no network download or package installation",
        "no fabricated, reconstructed or surrogate NANSY weights",
        "no substitute model, analysis frontend, generator or vocoder",
        "no copied upstream source, paper asset, test audio or licence text",
    ],
    "reopen": (
        "Identify and stage the exact licensed source at an immutable "
        "revision, the official checkpoint with per-file digests, a locked "
        "offline runtime, all code/weight/data/voice rights and consent, a "
        "rights-cleared cohort and an agreed Voice protocol; then reproduce "
        "approved parity and preservation output and complete opt-in provider "
        "intake."),
}

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "title": "No immutable runnable upstream source",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-01"],
        "statement": (
            "The catalogued record is the NeurIPS 2021 NANSY paper URL. No "
            "official repository, commit, release tag, source file, licence "
            "text or notice is staged at any probed path."),
        "required_action": (
            "Supply the exact official source at an immutable revision with a "
            "reviewed licence/notice bundle and independent review."),
        "reopen_condition": (
            "Only a caller-supplied exact artifact with verified identity, "
            "terms and matched evidence can reopen this blocker."),
    },
    {
        "id": "BLK-02",
        "title": "No checkpoint, config or resynthesis asset identity",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-01", "RG-02"],
        "statement": (
            "No content encoder, pitch/energy analysis module, timbre "
            "encoder, generator, vocoder or inference config is named. No file "
            "name, revision, byte count, SHA-256 or tensor layout exists, and "
            "no weight byte is present or downloaded."),
        "required_action": (
            "Stage every required checkpoint/config/vocoder asset with "
            "per-file byte counts and SHA-256 and reviewed weight terms."),
        "reopen_condition": (
            "Only a caller-supplied exact artifact with verified identity, "
            "terms and matched evidence can reopen this blocker."),
    },
    {
        "id": "BLK-03",
        "title": "No pinned runtime or candidate task geometry",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-03"],
        "statement": (
            "No interpreter lock, wheel hash set, device, dtype, determinism "
            "setting, analysis frame, hop, lookahead, chunk, reset or drain "
            "behaviour is documented. The probed interpreter exposes no NANSY "
            "module."),
        "required_action": (
            "Provide a locked offline runtime and the exact analysis/"
            "resynthesis geometry on the intended host."),
        "reopen_condition": (
            "Only a caller-supplied exact artifact with verified identity, "
            "terms and matched evidence can reopen this blocker."),
    },
    {
        "id": "BLK-04",
        "title": "No reviewed rights, consent or training-data terms",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-04"],
        "statement": (
            "No code licence, weight term, training-data statement, corpus "
            "lineage, attribution bundle, source/target voice consent, "
            "derived-output permission or redistribution decision is staged or "
            "reviewed. No rights-cleared speech input exists."),
        "required_action": (
            "Record reviewed code/weight/training-data terms and consent, "
            "reference availability and output-use decisions for every voice."),
        "reopen_condition": (
            "Only a caller-supplied exact artifact with verified identity, "
            "terms and matched evidence can reopen this blocker."),
    },
    {
        "id": "BLK-05",
        "title": "No reproduced analysis/resynthesis parity or preservation",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-05", "RG-06"],
        "statement": (
            "No candidate execution, analysis feature, resynthesised waveform, "
            "output hash, duration, level, peak, nonfinite, exact-repeat, "
            "parity-tolerance or speech-preservation measurement exists. The "
            "Voice profile is unsatisfied."),
        "required_action": (
            "Execute the pinned assets and measure parity, preservation, "
            "content, identity and naturalness on a rights-cleared cohort."),
        "reopen_condition": (
            "Only a caller-supplied exact artifact with verified identity, "
            "terms and matched evidence can reopen this blocker."),
    },
    {
        "id": "BLK-06",
        "title": "No matched cohort, listening, timing or release evidence",
        "status": "open",
        "qualifies": False,
        "linked_gates": ["RG-07", "RG-08"],
        "statement": (
            "No rights-cleared matched cohort, same-condition baseline, "
            "authorized listening, labeled screen, alignment/timing, device "
            "resource measurement, provider intake or independent review "
            "exists."),
        "required_action": (
            "Supply the matched cohort, listening/timing evidence, provider "
            "intake and independent exact-head review."),
        "reopen_condition": (
            "Only a caller-supplied exact artifact with verified identity, "
            "terms and matched evidence can reopen this blocker."),
    },
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "evidence_register_and_policy_boundary",
        "present": True,
        "blocked": False,
        "verified": True,
        "revision": None,
        "sha256": None,
        "bytes": None,
        "requirement": (
            "The linked inventory row, pinned Voice acceptance profile, SDK "
            "delivery plan, paper/survey context, merged sibling evidence and "
            "unchanged v0 contract boundary."),
    },
    {
        "id": "ART-02",
        "kind": "exact_upstream_source_snapshot",
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
        "bytes": None,
        "requirement": (
            "The exact official NANSY source tree at an immutable 40-hex "
            "commit or release tag, including licence text, README and a "
            "per-file SHA-256 manifest."),
    },
    {
        "id": "ART-03",
        "kind": "checkpoint_config_and_resynthesis_assets",
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
        "bytes": None,
        "requirement": (
            "Every content/pitch/energy/timbre analysis module, generator, "
            "vocoder and inference config with exact names, revision, byte "
            "counts and SHA-256 values."),
    },
    {
        "id": "ART-04",
        "kind": "pinned_offline_runtime_and_task_geometry",
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
        "bytes": None,
        "requirement": (
            "A locked offline runtime with interpreter, package versions, "
            "wheel hashes, platform, device, dtype, determinism settings, "
            "install location and the exact analysis/resynthesis geometry."),
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_inputs_targets_and_training_data",
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
        "bytes": None,
        "requirement": (
            "Code, weight, training-data, corpus and derived-output terms plus "
            "a digest-pinned, rights-cleared input set with source/target "
            "voice consent, acquisition and redistribution decisions."),
    },
    {
        "id": "ART-06",
        "kind": "reproduced_parity_preservation_and_voice_results",
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
        "bytes": None,
        "requirement": (
            "Deterministic reproduced analysis-to-waveform parity, speech "
            "preservation, content, identity/similarity, naturalness, "
            "alignment, first-output/tail and timing results on the exact "
            "runtime."),
    },
    {
        "id": "ART-07",
        "kind": "provider_intake_and_public_surface",
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
        "bytes": None,
        "requirement": (
            "A separate versioned OFF-by-default provider intake with "
            "clean-install proof, empty defaults, no shared-build change and "
            "independent exact-head review."),
    },
)

PROFILE_ROWS = (
    ("permitted_input_and_target_reference_scope",
     "Freeze permitted input and target references.",
     "No permitted input speech, target voice or reference record exists."),
    ("task_and_language_speaker_groups",
     "Freeze task and language/speaker groups.",
     "No frozen cohort, language group or speaker group exists."),
    ("text_and_semantic_content",
     "Preserve text and semantic content.",
     "No model transcript, cohort or output exists to score."),
    ("identity_and_similarity",
     "Score identity and similarity.",
     "No reference/target pair and no converted output exist."),
    ("naturalness",
     "Score naturalness.",
     "No candidate output and no authorized listening or MOS exist."),
    ("alignment_first_output_and_tail_timing",
     "Record alignment, first-output and tail timing.",
     "No runtime, chunk, lookahead, delay or device timing exists."),
    ("exact_target_condition",
     "Record the exact target condition.",
     "No designated target condition exists; only an unspecified "
     "identity-resynthesis placeholder is accepted."),
    ("consent_reference_availability_and_output_use",
     "Consent, reference availability and output use are independent gates.",
     "No consent, reference availability or output-use decision exists."),
    ("analysis_to_waveform_parity",
     "Validate analysis-to-waveform parity.",
     "No analysis frontend, resynthesis decoder, runtime or pair exists."),
    ("speech_preservation",
     "Validate speech preservation.",
     "No paired input/output, scorer or cohort exists."),
    ("paired_quality_control",
     "Use a same-condition control and established baseline.",
     "No source/weights/runtime and no comparable baseline exist."),
    ("numerical_and_nonfinite",
     "Reject nonfinite and invalid output.",
     "Only a task-local request validator exists; no candidate output."),
)


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
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _reject_duplicates(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise ValueError("nonfinite_json:" + token)


def loads_strict(payload: str) -> dict:
    try:
        value = json.loads(payload, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    return value


def read_strict_json(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("invalid_utf8") from error
    value = loads_strict(text)
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_finite(value)
    return value


def assert_finite(value: Any, path: str = "") -> None:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise TypeError("nonfinite value in canonical evidence: " + path)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("non-string key at " + path)
            assert_finite(item, path + "/" + key)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            assert_finite(item, path + "/" + str(index))


def canonical_report(report: dict | None = None) -> Tuple[str, str]:
    value = build_report() if report is None else report
    text = canonical_text(value) + "\n"
    return text, sha256_bytes(text.encode("ascii"))


# ---------------------------------------------------------------------------
# Stable board identity. The mutable board file is read, never pinned.
# ---------------------------------------------------------------------------


def _project(row: Mapping[str, Any], require_component: bool = False) -> dict:
    required = ("id", "title", "mode", "repository", "depends_on")
    missing = [field for field in required if field not in row]
    if require_component and "component" not in row:
        missing.append("component")
    if missing:
        raise ValueError("board_row_missing_field:" + missing[0])
    depends_on = row.get("depends_on")
    if not isinstance(depends_on, list):
        raise ValueError("board_depends_on_not_list")
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "component": row.get("component"),
        "mode": row.get("mode"),
        "repository": row.get("repository"),
        "depends_on": list(depends_on),
    }


def _board_tasks(path: Path | None = None) -> List[dict]:
    board = AUDIO_ROOT / BOARD_TASK_ROW if path is None else Path(path)
    document = read_strict_json(board)
    rows = document.get("tasks")
    if not isinstance(rows, list):
        raise ValueError("board_tasks_not_list")
    return rows


def board_row_projection(path: Path | None = None) -> dict:
    matches = [row for row in _board_tasks(path)
               if isinstance(row, dict) and row.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    projection = _project(matches[0], require_component=True)
    if projection["component"] != COMPONENT_ID:
        raise ValueError("board_component_mismatch")
    if projection["mode"] != MODE:
        raise ValueError("board_mode_mismatch")
    if projection["repository"] != REPOSITORY:
        raise ValueError("board_repository_mismatch")
    if tuple(projection["depends_on"]) != DEPENDS_ON:
        raise ValueError("board_depends_on_mismatch")
    if projection["title"] != TASK_TITLE:
        raise ValueError("board_title_mismatch")
    return projection


def linked_rows(path: Path | None = None) -> Tuple[dict, ...]:
    rows = _board_tasks(path)
    by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
    result: List[dict] = []
    for row_id in LINKED_ROW_IDS:
        row = by_id.get(row_id)
        if row is None:
            raise ValueError("linked_row_absent:" + row_id)
        result.append(_project(row, require_component=row_id == TASK))
    if result[0]["component"] != COMPONENT_ID:
        raise ValueError("linked_component_mismatch")
    return tuple(result)


def board_row_digest(projection: dict | None = None) -> str:
    return object_digest(projection if projection is not None
                         else board_row_projection())


def linked_rows_digest(rows: Tuple[dict, ...] | None = None) -> str:
    return object_digest(list(rows if rows is not None else linked_rows()))


# ---------------------------------------------------------------------------
# Task-local git scope.
# ---------------------------------------------------------------------------

SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
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


# ---------------------------------------------------------------------------
# Fixed evidence probes. No recursive walk and no network.
# ---------------------------------------------------------------------------


def _probe(path: Path, label: str, workspace: bool, worktree: bool,
           home: bool) -> dict:
    return {
        "path": label,
        "present": path.exists(),
        "searched_workspace": workspace,
        "searched_sdk_worktree": worktree,
        "searched_home_cache": home,
    }


def workspace_probes() -> List[dict]:
    return [_probe(AUDIO_ROOT / path, path, True, False, False)
            for path in WORKSPACE_PROBES]


def worktree_probes() -> List[dict]:
    return [_probe(WORKTREE / path, path, False, True, False)
            for path in WORKTREE_PROBES]


def home_probes() -> List[dict]:
    return [_probe(Path(path).expanduser(), path, False, False, True)
            for path in HOME_PROBES]


def all_probes() -> List[dict]:
    return workspace_probes() + worktree_probes() + home_probes()


def absence_summary(probes: List[dict] | None = None) -> dict:
    rows = all_probes() if probes is None else probes
    return {
        "probe_count": len(rows),
        "workspace_probe_count": sum(1 for row in rows
                                     if row["searched_workspace"]),
        "worktree_probe_count": sum(1 for row in rows
                                    if row["searched_sdk_worktree"]),
        "home_probe_count": sum(1 for row in rows
                                if row["searched_home_cache"]),
        "present_count": sum(1 for row in rows if row["present"] is not False),
        "all_absent": all(row["present"] is False for row in rows),
        "probes": rows,
        "fixed_probe_list_only": True,
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "network_used": False,
        "candidate_module_imported": False,
        "candidate_runtime_executed": False,
        "weights_loaded": False,
        "audio_read": False,
        "processed_output_present": False,
    }


def runtime_readiness() -> dict:
    return {
        "runtime_present": False,
        "runtime_pinned": False,
        "interpreter_pin": REQUIRED_INTERPRETER,
        "observed_interpreter": platform.python_version(),
        "candidate_module_available": False,
        "import_attempted": False,
        "analysis_frontend_present": False,
        "synthesis_generator_present": False,
        "vocoder_present": False,
        "device": None,
        "dtype": None,
        "lock_sha256": None,
        "packages": [],
        "note": ("No package is installed, imported or downloaded. The "
                 "observed interpreter is reported for provenance only."),
    }


# ---------------------------------------------------------------------------
# Pins, README digest tables and SOURCES.sha256.
# ---------------------------------------------------------------------------


def pin_rows(pins: Mapping[str, str], root: Path) -> List[dict]:
    rows: List[dict] = []
    for relative in sorted(pins):
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        rows.append({
            "path": relative,
            "sha256": pins[relative],
            "actual": actual,
            "verified": actual == pins[relative],
        })
    return rows


def _local_manifest_paths() -> List[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name != "SOURCES.sha256")


def sources_bytes() -> bytes:
    rows: List[Tuple[str, str]] = []
    for relative, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + relative))
    for relative, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + relative))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        "# SHA-256 pins for " + TASK + " task-local evidence.",
        "# source: paths are relative to the pinned audioml workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable plan/swarm/TASKS.json is never hashed; only its stable "
        "linked-row projection is gated.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(digest + "  " + path for digest, path in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def expected_readme_keys() -> Dict[str, set]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {name for name in _local_manifest_paths()
                      if name not in ARTIFACT_TABLE_EXCLUDED},
    }


def _section_text(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if text.count(start) != 1:
        raise ValueError("readme_marker_count:" + section)
    start_index = text.index(start) + len(start)
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise ValueError("readme_marker_missing:" + section)
    return text[start_index:end_index]


def parse_readme_digest_tables(
        text: str) -> Dict[str, List[Tuple[str, str]]]:
    result: Dict[str, List[Tuple[str, str]]] = {}
    for section in README_SECTIONS:
        rows: List[Tuple[str, str]] = []
        for line in _section_text(text, section).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or re.fullmatch(r"[0-9]+",
                                                   cells[2]) is None:
                    raise ValueError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ValueError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if HEX64.fullmatch(digest) is None:
                raise ValueError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({key for key, _ in rows}) != len(rows):
            raise ValueError("duplicate_readme_row:" + section)
        result[section] = rows
    return result


def verify_readme_digests(text: str) -> Dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            missing = sorted(expected[section] - actual_keys)
            extra = sorted(actual_keys - expected[section])
            raise ValueError(
                "readme_key_mismatch:%s:missing=%s:extra=%s"
                % (section, missing, extra))
        for key, digest in parsed[section]:
            if section == "source":
                relative = key[len("source:"):]
                path = AUDIO_ROOT / relative
                expected_digest = SOURCE_PINS[relative]
            elif section == "boundary":
                relative = key[len("sdk:"):]
                path = SDK_ROOT / relative
                expected_digest = BOUNDARY_PINS[relative]
            else:
                path = HERE / key
                expected_digest = sha256_file(path)
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if not path.is_file() or sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = "| `%s` | `%s` | %d |" % (key, sha256_file(HERE / key), size)
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_digest_table(section: str) -> str:
    if section == "source":
        rows = ["| `source:%s` | `%s` |" % (name, digest)
                for name, digest in sorted(SOURCE_PINS.items())]
    elif section == "boundary":
        rows = ["| `sdk:%s` | `%s` |" % (name, digest)
                for name, digest in sorted(BOUNDARY_PINS.items())]
    elif section == "artifacts":
        rows = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
        for name in _local_manifest_paths():
            if name in ARTIFACT_TABLE_EXCLUDED:
                continue
            path = HERE / name
            rows.append("| `%s` | `%s` | %d |"
                        % (name, sha256_file(path), path.stat().st_size))
    else:
        raise ValueError("unknown_readme_section:" + section)
    return "\n".join(rows)


def update_readme_table(text: str, section: str) -> str:
    block = render_digest_table(section)
    start, end = README_MARKERS[section]
    start_index = text.index(start)
    end_index = text.index(end, start_index) + len(end)
    return text[:start_index] + start + "\n" + block + "\n" + end + \
        text[end_index:]


def update_readme_tables(text: str) -> str:
    for section in README_SECTIONS:
        text = update_readme_table(text, section)
    return text


# ---------------------------------------------------------------------------
# Candidate identity, task geometry and the Voice profile.
# ---------------------------------------------------------------------------


def source_reported_identity() -> dict:
    return {
        "candidate": CANDIDATE_NAME,
        "candidate_family": CANDIDATE_FAMILY,
        "venue": "NeurIPS 2021",
        "paper_reference": PAPER_URL,
        "paper_title": PAPER_TITLE,
        "source_reported_task": (
            "disentangled neural analysis of content, pitch, energy and "
            "timbre followed by neural resynthesis"),
        "source_reported_stages": [
            "self_supervised_content_analysis",
            "pitch_and_energy_analysis",
            "timbre_analysis",
            "pitch_energy_conditioned_generator",
            "neural_vocoder",
        ],
        "input_is_speech": True,
        "output_is_speech": True,
        "analysis_to_waveform_task": True,
        "voice_conversion_task": True,
        "official_code_found": False,
        "official_weights_found": False,
        "immutable_revision_recorded": False,
        "license_recorded": False,
        "license_text_staged": False,
        "model_card_staged": False,
        "runnable_as_released": False,
        "source_reported_only": True,
        "identity_verified": False,
        "note": (
            "Only the NeurIPS 2021 paper title/URL and a one-line survey lead "
            "are pinned. No source, weight, config, runtime or numeric result "
            "follows from them."),
    }


def task_geometry() -> dict:
    frame_ms = FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ
    return {
        "public_v0": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "sample_format": "float32",
            "frame_ms": frame_ms,
            "unchanged": True,
        },
        "candidate_geometry_documented": False,
        "geometry_verified": False,
        "sample_rate_hz": None,
        "channels": None,
        "frame_samples": None,
        "hop_samples": None,
        "lookahead_samples": None,
        "analysis_frame_ms": None,
        "latency_ms": None,
        "reset_drain_documented": False,
        "candidate_processing_modes": ["analysis", "resynthesis", "round_trip"],
        "profile_fit": "unverified_candidate_geometry_absent",
        "note": (
            "The 16 kHz mono 160-sample values are the installed v0 contract, "
            "not NANSY geometry. No candidate frame, hop, lookahead, latency, "
            "reset or drain behaviour is known."),
    }


def profile_rows() -> List[dict]:
    rows: List[dict] = []
    for index, (key, requirement, evidence) in enumerate(PROFILE_ROWS, start=1):
        blocked = key != "numerical_and_nonfinite"
        rows.append({
            "id": "VOICE-%02d" % index,
            "field": key,
            "requirement": requirement,
            "status": "blocked" if blocked else "partial_local_harness_only",
            "qualifies": False,
            "evidence": evidence,
        })
    return rows


def profile_source_check() -> dict:
    path = AUDIO_ROOT / PROFILE_SOURCE_REL
    text = path.read_text(encoding="utf-8")
    voice_rows = [line for line in text.splitlines()
                  if line.startswith("| Voice |")]
    phrases_present = [phrase for phrase in PROFILE_PHRASES if phrase in text]
    return {
        "path": PROFILE_SOURCE_REL,
        "voice_row_count": len(voice_rows),
        "unique_voice_row": len(voice_rows) == 1,
        "phrases_present": phrases_present,
        "all_phrases_present": len(phrases_present) == len(PROFILE_PHRASES),
    }


def matched_evidence() -> dict:
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "candidate_output_present": False,
        "source_output_mapping_present": False,
        "analysis_to_waveform_parity_present": False,
        "speech_preservation_present": False,
        "matched_cohort_present": False,
        "paired_clean_reference_present": False,
        "matched_baseline_present": False,
        "same_condition_control_present": False,
        "listening_or_labeled_screen_present": False,
        "consent_and_output_use_present": False,
        "real_results": 0,
        "synthetic_results": 0,
        "synthetic_schema_control_counted_as_result": False,
        "evidence_classes": [
            "source_reported_paper_and_survey_lead",
            "schema_only_declaration_control",
            "missing_real_candidate_result",
            "separate_sibling_voice_candidate",
            "unchanged_v0_contract",
        ],
        "classes_pooled": False,
        "required_separation": (
            "Source-reported prose, schema-only declarations, missing real "
            "measurements and sibling candidate evidence stay in distinct "
            "sections and are never pooled."),
    }


def required_results() -> List[dict]:
    requirements = (
        ("RES-01", "Exact source, licence and provenance",
         "No official source or licence is staged."),
        ("RES-02", "Exact checkpoint and weight identity",
         "No checkpoint, config, byte count or digest exists."),
        ("RES-03", "Pinned offline runtime and geometry",
         "No lockfile, wheel hashes, device, dtype or geometry exist."),
        ("RES-04", "Rights-cleared input and target references",
         "No consent, corpus or target voice exists."),
        ("RES-05", "Analysis-to-waveform parity",
         "No analysis feature or resynthesised waveform exists."),
        ("RES-06", "Speech preservation",
         "No paired input/output or preservation measure exists."),
        ("RES-07", "Content, identity/similarity and naturalness",
         "No transcript, reference pair, output or listening result exists."),
        ("RES-08", "Alignment, first-output/tail and device timing",
         "No runtime and no timing measurement exist."),
        ("RES-09", "Nonfinite, peak, reset and drain behaviour",
         "Only a task-local request validator exists."),
        ("RES-10", "Provider intake and independent review",
         "No adapter, intake, descriptor or review exists."),
    )
    return [{"id": key, "requirement": requirement, "status": "blocked",
             "qualifies": False, "evidence": evidence}
            for key, requirement, evidence in requirements]


# ---------------------------------------------------------------------------
# Fail-closed caller-supplied asset declaration.
# ---------------------------------------------------------------------------


def empty_declaration() -> dict:
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "declaration_id": "nansy-analysis-resynthesis-unpopulated",
        "candidate": {
            "name": CANDIDATE_NAME,
            "family": CANDIDATE_FAMILY,
            "paper_reference": PAPER_URL,
            "analysis_to_waveform_task": True,
            "source_reported_only": True,
        },
        "source": {
            "declared_present": False,
            "revision": None,
            "license_sha256": None,
            "source_sha256": None,
        },
        "weights": {
            "declared_present": False,
            "revision": None,
            "weights_sha256": None,
            "byte_count": None,
        },
        "runtime": {
            "declared_present": False,
            "python_version": None,
            "platform": None,
            "device": None,
            "lock_sha256": None,
        },
        "geometry": {
            "declared": False,
            "sample_rate_hz": None,
            "frame_samples": None,
            "hop_samples": None,
            "channels": None,
        },
        "rights": {
            "code": False,
            "weights": False,
            "training_data": False,
            "inputs": False,
            "output_use": False,
            "target_voice": False,
            "redistribution": False,
            "review_reference": None,
        },
        "disposition": {
            "decision": "DEFER",
            "qualifies": False,
        },
    }


DECLARATION_FIELDS = (
    "schema_id", "declaration_id", "candidate", "source", "weights",
    "runtime", "geometry", "rights", "disposition",
)
DECLARATION_SECTIONS = {
    "candidate": ("name", "family", "paper_reference",
                  "analysis_to_waveform_task", "source_reported_only"),
    "source": ("declared_present", "revision", "license_sha256",
               "source_sha256"),
    "weights": ("declared_present", "revision", "weights_sha256",
                "byte_count"),
    "runtime": ("declared_present", "python_version", "platform", "device",
                "lock_sha256"),
    "geometry": ("declared", "sample_rate_hz", "frame_samples", "hop_samples",
                 "channels"),
    "rights": ("code", "weights", "training_data", "inputs", "output_use",
               "target_voice", "redistribution", "review_reference"),
    "disposition": ("decision", "qualifies"),
}


def validate_declaration(declaration: Any) -> dict:
    """Fail-closed shape check for an unpopulated declaration only."""
    if not isinstance(declaration, dict):
        raise ConfigError("not_object", "not_object")
    extra = sorted(set(declaration) - set(DECLARATION_FIELDS))
    if extra:
        raise ConfigError("unknown_field:" + extra[0], "unknown_field")
    missing = [field for field in DECLARATION_FIELDS
               if field not in declaration]
    if missing:
        raise ConfigError("missing_field:" + missing[0], "missing_field")
    if declaration["schema_id"] != DECLARATION_SCHEMA_ID:
        raise ConfigError("schema_id_mismatch", "schema_id_mismatch")
    declaration_id = declaration["declaration_id"]
    if not isinstance(declaration_id, str) or \
            SLUG.fullmatch(declaration_id) is None:
        raise ConfigError("invalid_slug", "invalid_slug")
    for section, fields in DECLARATION_SECTIONS.items():
        block = declaration[section]
        if not isinstance(block, dict):
            raise ConfigError("not_object:" + section, "not_object")
        unknown = sorted(set(block) - set(fields))
        if unknown:
            raise ConfigError("unknown_field:" + section + "." + unknown[0],
                              "unknown_field")
        absent = [field for field in fields if field not in block]
        if absent:
            raise ConfigError("missing_field:" + section + "." + absent[0],
                              "missing_field")
    expected = empty_declaration()
    for section in DECLARATION_SECTIONS:
        for field in DECLARATION_SECTIONS[section]:
            observed = declaration[section][field]
            wanted = expected[section][field]
            path = section + "." + field
            if isinstance(observed, float) or isinstance(wanted, float):
                if isinstance(observed, bool) or not isinstance(
                        observed, (int, float)):
                    raise ConfigError("invalid_type:" + path, "invalid_type")
                raise ConfigError("float_not_allowed:" + path,
                                  "invalid_type")
            if wanted is True or wanted is False:
                if observed is not wanted:
                    raise ConfigError("unverified_claim:" + path,
                                      "unverified_claim")
                continue
            if wanted is None:
                if observed is not None:
                    raise ConfigError("unverified_claim:" + path,
                                      "unverified_claim")
                continue
            if observed != wanted:
                raise ConfigError("identity_mismatch:" + path,
                                  "identity_mismatch")
    if declaration["disposition"]["decision"] != "DEFER":
        raise ConfigError("premature_decision", "premature_decision")
    if declaration["disposition"]["qualifies"] is not False:
        raise ConfigError("unverified_claim:disposition.qualifies",
                          "unverified_claim")
    return {"decision": "DEFER", "qualifies": False,
            "status": "accepted_unpopulated"}


def _set_path(declaration: dict, path: str, value: Any) -> None:
    parts = path.split(".")
    target = declaration
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = value


def _delete_path(declaration: dict, path: str) -> None:
    parts = path.split(".")
    target = declaration
    for part in parts[:-1]:
        target = target[part]
    del target[parts[-1]]


def _declaration_cases() -> dict:
    base = empty_declaration()
    mutations: List[Tuple[str, str, Any]] = [
        ("root_not_object", "root", "x"),
        ("root_missing_schema_id", "delete", "schema_id"),
        ("root_missing_declaration_id", "delete", "declaration_id"),
        ("extra_top_key", "extra", "attestation"),
        ("bad_schema_id", "schema_id", "audio-sdk/other/0.1"),
        ("bad_declaration_id", "declaration_id", "NANSY POPULATED"),
        ("wrong_candidate_name", "candidate.name", "NANSY"),
        ("wrong_candidate_family", "candidate.family", "generic_vocoder"),
        ("wrong_paper", "candidate.paper_reference", "https://example.invalid"),
        ("analysis_task_false", "candidate.analysis_to_waveform_task", False),
        ("source_reported_only_false", "candidate.source_reported_only", False),
        ("source_present_true", "source.declared_present", True),
        ("source_revision_set", "source.revision", "0" * 40),
        ("source_license_set", "source.license_sha256", "a" * 64),
        ("source_digest_set", "source.source_sha256", "b" * 64),
        ("weights_present_true", "weights.declared_present", True),
        ("weights_revision_set", "weights.revision", "0" * 40),
        ("weights_digest_set", "weights.weights_sha256", "c" * 64),
        ("weights_bytes_set", "weights.byte_count", 1),
        ("runtime_present_true", "runtime.declared_present", True),
        ("runtime_python_set", "runtime.python_version", "3.12.16"),
        ("runtime_platform_set", "runtime.platform", "darwin-arm64"),
        ("runtime_device_set", "runtime.device", "cpu"),
        ("runtime_lock_set", "runtime.lock_sha256", "d" * 64),
        ("geometry_declared_true", "geometry.declared", True),
        ("geometry_rate_set", "geometry.sample_rate_hz", 16000),
        ("geometry_frame_set", "geometry.frame_samples", 160),
        ("geometry_hop_set", "geometry.hop_samples", 160),
        ("geometry_channels_set", "geometry.channels", 1),
        ("rights_code_true", "rights.code", True),
        ("rights_weights_true", "rights.weights", True),
        ("rights_training_true", "rights.training_data", True),
        ("rights_inputs_true", "rights.inputs", True),
        ("rights_output_true", "rights.output_use", True),
        ("rights_target_voice_true", "rights.target_voice", True),
        ("rights_redistribution_true", "rights.redistribution", True),
        ("rights_review_set", "rights.review_reference", "RR-1"),
        ("qualifies_true", "disposition.qualifies", True),
        ("premature_admit", "disposition.decision", "ADMIT"),
        ("missing_weights_section", "delete", "weights"),
        ("extra_geometry_key", "geometry.bit_depth", 16),
        ("float_byte_count", "weights.byte_count", 1.0),
        ("source_not_object", "source", []),
        ("candidate_not_object", "candidate", "x"),
        ("presence_int_zero", "source.declared_present", 0),
        ("bool_revision", "source.revision", False),
    ]
    cases: List[dict] = []
    for case_id, field, value in mutations:
        declaration = empty_declaration()
        if field == "root":
            candidate: Any = value
        elif field == "delete":
            candidate = declaration
            _delete_path(candidate, value)
        elif field == "extra":
            candidate = declaration
            candidate[value] = True
        else:
            candidate = declaration
            _set_path(candidate, field, value)
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_declaration(candidate)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        cases.append({
            "id": case_id,
            "field": field if field not in ("delete", "extra", "root")
                     else value,
            "accepted": accepted,
            "error": error,
        })
    return {
        "schema_id": DECLARATION_SCHEMA_ID,
        "purpose": (
            "Defines the exact caller-supplied asset declaration a future "
            "intake must populate and verify externally. This package accepts "
            "only the unpopulated declaration and never resolves or loads an "
            "asset."),
        "fields": list(DECLARATION_FIELDS),
        "candidate_fields": list(DECLARATION_SECTIONS["candidate"]),
        "source_fields": list(DECLARATION_SECTIONS["source"]),
        "weights_fields": list(DECLARATION_SECTIONS["weights"]),
        "runtime_fields": list(DECLARATION_SECTIONS["runtime"]),
        "geometry_fields": list(DECLARATION_SECTIONS["geometry"]),
        "rights_fields": list(DECLARATION_SECTIONS["rights"]),
        "disposition_fields": list(DECLARATION_SECTIONS["disposition"]),
        "accepted_control_status": "accepted_unpopulated",
        "accepted_control_qualifies": False,
        "accepted_control_checks": len(DECLARATION_FIELDS) + sum(
            len(fields) for fields in DECLARATION_SECTIONS.values()),
        "rejection_cases": len(cases),
        "all_rejected": all(not case["accepted"] for case in cases),
        "presence_claims_rejected": True,
        "assets_loaded": False,
        "cases": cases,
    }


def _json_adverse_cases() -> dict:
    payloads = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_literal", '{"a":NaN}'),
        ("infinity_literal", '{"a":Infinity}'),
        ("negative_infinity_literal", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} extra'),
        ("byte_order_mark", '\ufeff{"a":1}'),
        ("non_object_root", '[1,2]'),
        ("empty_input", ""),
        ("unterminated", '{"a":1'),
    )
    cases: List[dict] = []
    for case_id, text in payloads:
        rejected = False
        code = "NOT_REJECTED"
        try:
            loads_strict(text)
        except ValueError as error:
            rejected = True
            code = str(error) or "invalid_json"
        cases.append({"id": case_id, "rejected": rejected, "error": code})
    return {
        "strict_json_cases": len(cases),
        "strict_json_rejections": cases,
        "all_rejected": all(case["rejected"] for case in cases),
    }


# ---------------------------------------------------------------------------
# Fail-closed request validation. No candidate call exists.
# ---------------------------------------------------------------------------

REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples",
    "hop_samples", "samples", "epoch", "first_input_sample", "lifecycle",
    "stage", "target_condition",
})


def _require_int(value: Any, code: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(code, code)
    if minimum is not None and value < minimum:
        raise ConfigError(code, code)
    return value


def _validate_samples(samples: Any, expected: int | None) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise InputError("samples_not_a_list", "invalid_sample_type")
    if not samples:
        raise InputError("empty_samples", "empty_samples")
    if expected is not None and len(samples) != expected:
        raise InputError("wrong_sample_count", "wrong_sample_count")
    result: List[float] = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("invalid_sample_type:" + str(index),
                             "invalid_sample_type")
        number = float(value)
        if not math.isfinite(number):
            raise InputError("nonfinite_sample:" + str(index), "nonfinite")
        if abs(number) > MAX_ABS_INPUT:
            raise InputError("sample_out_of_range:" + str(index),
                             "out_of_range")
        result.append(number)
    return result


def validate_request(request: Any) -> dict:
    if not isinstance(request, dict):
        raise InputError("request must be an object", "invalid_request")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise ConfigError("unknown_field:" + ",".join(unknown),
                          "unknown_field")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise ConfigError("missing_field:" + ",".join(missing),
                          "missing_field")
    if request["candidate"] != "nansy":
        raise ConfigError("unknown_candidate", "unknown_candidate")
    if _require_int(request["sample_rate_hz"], "wrong_rate") != SAMPLE_RATE_HZ:
        raise ConfigError("wrong_rate", "wrong_rate")
    if _require_int(request["channels"], "wrong_channels") != CHANNELS:
        raise ConfigError("wrong_channels", "wrong_channels")
    if _require_int(request["frame_samples"], "wrong_frame") != FRAME_SAMPLES:
        raise ConfigError("wrong_frame", "wrong_frame")
    if _require_int(request["hop_samples"], "wrong_hop") != HOP_SAMPLES:
        raise ConfigError("wrong_hop", "wrong_hop")
    samples = _validate_samples(request["samples"], FRAME_SAMPLES)
    epoch = _require_int(request["epoch"], "invalid_epoch", 0)
    first_input_sample = _require_int(request["first_input_sample"],
                                      "invalid_position", 0)
    if request["lifecycle"] not in LIFECYCLES:
        raise ConfigError("invalid_lifecycle", "invalid_lifecycle")
    if request["stage"] not in STAGES:
        raise ConfigError("invalid_stage", "invalid_stage")
    if request["target_condition"] != TARGET_CONDITION:
        raise ConfigError("unknown_target_condition",
                          "unknown_target_condition")
    return {
        "candidate": "nansy",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "hop_samples": HOP_SAMPLES,
        "samples": tuple(samples),
        "epoch": epoch,
        "first_input_sample": first_input_sample,
        "lifecycle": request["lifecycle"],
        "stage": request["stage"],
        "target_condition": request["target_condition"],
    }


def probe_candidate(request: Any) -> None:
    validated = validate_request(request)
    raise CandidateAbsent(
        "SOURCE_WEIGHTS_RUNTIME_ABSENT: " + validated["candidate"] +
        " source, checkpoint and pinned runtime are not present; no analysis "
        "or resynthesis is performed",
        "SOURCE_WEIGHTS_RUNTIME_ABSENT")


def _base_request() -> dict:
    return {
        "candidate": "nansy",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "hop_samples": HOP_SAMPLES,
        "samples": [0.0] * FRAME_SAMPLES,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "stage": "round_trip",
        "target_condition": TARGET_CONDITION,
    }


def _adverse_request_cases() -> dict:
    base = _base_request()

    def variant(**changes: Any) -> dict:
        value = dict(base)
        value.update(changes)
        return value

    def with_samples(samples: Any) -> dict:
        return variant(samples=samples)

    nan_samples = [0.0] * FRAME_SAMPLES
    nan_samples[11] = float("nan")
    inf_samples = [0.0] * FRAME_SAMPLES
    inf_samples[13] = float("inf")
    specs = (
        ("unknown_candidate", variant(candidate="nansy-vc")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("wrong_rate", variant(sample_rate_hz=48000)),
        ("wrong_channels", variant(channels=2)),
        ("wrong_frame", variant(frame_samples=320)),
        ("wrong_hop", variant(hop_samples=80)),
        ("short_samples", with_samples([0.0] * (FRAME_SAMPLES - 1))),
        ("empty_samples", with_samples([])),
        ("nonfinite_nan", with_samples(nan_samples)),
        ("nonfinite_inf", with_samples(inf_samples)),
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
        ("invalid_stage", variant(stage="conversion")),
        ("empty_stage", variant(stage="")),
        ("unknown_target_condition", variant(target_condition="target-voice")),
        ("request_not_object", "not-an-object"),
        ("samples_not_list", with_samples(0.0)),
    )
    cases: List[dict] = []
    for case_id, request in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_request(request)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        cases.append({"id": case_id, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "cases": cases,
        "note": ("Invalid requests are rejected before any candidate call; no "
                 "analysis or resynthesis metrics exist."),
    }


def validate_reset(epoch: Any, first_input_sample: Any,
                   previous_epoch: Any) -> dict:
    """Structural reset validator; owns no candidate state."""
    new_epoch = _require_int(epoch, "invalid_epoch", 0)
    previous = _require_int(previous_epoch, "invalid_epoch", 0)
    position = _require_int(first_input_sample, "invalid_position", 0)
    if new_epoch <= previous:
        raise ConfigError("epoch_not_increasing", "epoch_not_increasing")
    return {"epoch": new_epoch, "first_input_sample": position,
            "previous_epoch": previous}


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


def _reset_cases() -> dict:
    cases: List[dict] = []
    for name, epoch, position, previous, expected in RESET_CASES:
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_reset(epoch, position, previous)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted,
                      "expected_accepted": expected, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "expected_accepted_count": sum(1 for case in cases
                                       if case["expected_accepted"]),
        "matches_expectation": all(case["accepted"] == case["expected_accepted"]
                                   for case in cases),
        "state_owned": False,
        "metrics": None,
        "cases": cases,
        "note": ("Structural reset validation only; no candidate state exists "
                 "and no reset is executed."),
    }


def missing_result(fixture_name: str) -> dict:
    return {
        "fixture": fixture_name,
        "status": "blocked",
        "reason": "source_weights_runtime_and_rights_absent",
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


# ---------------------------------------------------------------------------
# Harness stimuli. Synthetic characterisation only; not candidate output.
# ---------------------------------------------------------------------------


def tensor_digest(samples: Iterable[float]) -> str:
    digest = hashlib.sha256()
    for value in samples:
        digest.update(struct.pack("<f", float(value)))
    return digest.hexdigest()


def rms(samples: Sequence[float]) -> float:
    if not samples:
        raise InputError("empty_samples", "empty_samples")
    total = math.fsum(float(value) * float(value) for value in samples)
    return math.sqrt(total / len(samples))


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
        raise ConfigError("impulse position out of range", "invalid_stimulus")
    values = [0.0] * length
    values[position] = amplitude
    return tuple(values)


def step(length: int = 1600, position: int = 800,
         amplitude: float = 0.25) -> Tuple[float, ...]:
    if not 0 <= position <= length:
        raise ConfigError("step position out of range", "invalid_stimulus")
    return tuple(0.0 if index < position else amplitude
                 for index in range(length))


def sweep(length: int = 1600, start_hz: float = 200.0,
          end_hz: float = 3000.0, amplitude: float = 0.3) -> Tuple[float, ...]:
    if length <= 0 or start_hz <= 0.0 or end_hz <= 0.0:
        raise ConfigError("invalid sweep geometry", "invalid_stimulus")
    duration = length / float(SAMPLE_RATE_HZ)
    values = []
    for index in range(length):
        t = index / float(SAMPLE_RATE_HZ)
        phase = 2.0 * math.pi * (start_hz * t +
                                 (end_hz - start_hz) * t * t /
                                 (2.0 * duration))
        values.append(amplitude * math.sin(phase))
    return tuple(values)


def speech_like(length: int = 3200, seed: int = 20261126) -> Tuple[float, ...]:
    noise = _lcg(seed)
    values = []
    for index in range(length):
        noise_value = next(noise)
        t = index / float(SAMPLE_RATE_HZ)
        if index < length // 3 or (length // 2) <= index < (5 * length) // 6:
            value = (0.25 * math.sin(2.0 * math.pi * 120.0 * t) +
                     0.12 * math.sin(2.0 * math.pi * 240.0 * t) +
                     0.06 * math.sin(2.0 * math.pi * 360.0 * t))
            envelope = 0.65 + 0.35 * math.sin(2.0 * math.pi * 3.0 * t)
            value = value * envelope + 0.005 * noise_value
        else:
            value = 0.001 * noise_value
        values.append(value)
    return tuple(values)


STIMULUS_GENERATORS = {
    "silence": lambda: silence(1600),
    "impulse": lambda: impulse(1600, 800, 0.5),
    "step": lambda: step(1600, 800, 0.25),
    "sweep": lambda: sweep(1600, 200.0, 3000.0, 0.3),
    "speech_like_proxy": lambda: speech_like(3200),
}


def stimulus_metrics(name: str, samples: Sequence[float]) -> dict:
    if not samples:
        raise InputError("empty_samples", "empty_samples")
    peak = 0.0
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("invalid_sample_type:" + str(index),
                             "invalid_sample_type")
        number = float(value)
        if not math.isfinite(number):
            raise InputError("nonfinite_sample:" + str(index), "nonfinite")
        peak = max(peak, abs(number))
    if peak > MAX_ABS_STIMULUS:
        raise InputError("stimulus_out_of_range", "out_of_range")
    return {
        "name": name,
        "sample_count": len(samples),
        "peak_abs": round(peak, 9),
        "rms": round(rms([float(value) for value in samples]), 9),
        "nonfinite_count": 0,
        "digest": tensor_digest([float(value) for value in samples]),
    }


def stimulus_probe() -> dict:
    stimuli: Dict[str, Any] = {}
    identity: Dict[str, Any] = {}
    for name, generator in STIMULUS_GENERATORS.items():
        samples = generator()
        stimuli[name] = stimulus_metrics(name, samples)
        identity[name] = {
            "digest": tensor_digest(samples),
            "byte_identical": tuple(samples) == tuple(
                float(value) for value in samples),
        }
    return {
        "purpose": ("harness stimulus characterisation only; not a NANSY "
                    "result and not a candidate output"),
        "stimuli": stimuli,
        "identity_control": identity,
        "candidate_processing": False,
        "synthetic_speech": False,
        "note": ("speech_like_proxy is an analytic tone/noise proxy used to "
                 "characterise the harness only; it is not speech, a corpus "
                 "item or a resynthesis result."),
    }


# ---------------------------------------------------------------------------
# Evidence snippets and historical records.
# ---------------------------------------------------------------------------

EVIDENCE_SNIPPETS = (
    ("audio-benchmark-platform/plan/INVENTORY.md",
     "| NANSY analysis/resynthesis | considered | "
     "`SDK-NANSY-ANALYSIS-RESYNTHESIS`"),
    ("audio-benchmark-platform/plan/INVENTORY.json",
     '"plan_note": "Stage exact model, validate analysis-to-waveform parity '
     'and speech preservation."'),
    ("research/category_registry.json", '"title": "NANSY analysis and '
     'resynthesis paper"'),
    ("research/category_registry.json", PAPER_URL),
    ("research/category_survey/sources.md",
     "[NANSY analysis and resynthesis paper](" + PAPER_URL),
    ("audio-benchmark-platform/plan/audio-sdk/README.md",
     "Reproduce a consented offline waveform VC case with exact input and "
     "assets"),
    ("audio-benchmark-platform/plan/swarm/VERIFICATION.md",
     "Freeze permitted input and target references, task and language/speaker "
     "groups."),
)


def evidence_presence() -> dict:
    checks: List[dict] = []
    for relative, phrase in EVIDENCE_SNIPPETS:
        path = AUDIO_ROOT / relative
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        checks.append({
            "path": relative,
            "phrase": phrase,
            "present": phrase in text,
        })
    return {
        "checks": checks,
        "count": len(checks),
        "snippet_count": len(checks),
        "all_present": all(check["present"] for check in checks),
        "note": ("Exact phrases are read from pinned inputs; they are "
                 "source-reported context, never a local execution."),
    }


HISTORICAL_EVIDENCE = (
    {
        "source": "audio-benchmark-platform/plan/INVENTORY.json",
        "class": "inventory_scope",
        "admitted_as_result": False,
        "boundary": (
            "Records nansy-analysis-resynthesis as area Voice and synthesis, "
            "evidence_status considered, disposition sdk-model, "
            "verification_profile voice, task "
            "SDK-NANSY-ANALYSIS-RESYNTHESIS; it is not a result."),
    },
    {
        "source": "research/category_registry.json",
        "class": "source_reported_paper_lead",
        "admitted_as_result": False,
        "boundary": (
            "S35 names the NeurIPS 2021 NANSY analysis and resynthesis paper "
            "with a direct paper URL only. No source, weight, runtime or "
            "measurement follows."),
    },
    {
        "source": "research/category_survey/sources.md",
        "class": "source_reported_survey_lead",
        "admitted_as_result": False,
        "boundary": (
            "The S35 table row links the NANSY paper under transformations "
            "with access_scope direct. It is a documentation lead, not an "
            "artifact or result."),
    },
    {
        "source": "docs/task-evidence/survey-trn-02/report.json",
        "class": "merged_sibling_survey",
        "admitted_as_result": False,
        "boundary": (
            "The merged TRN-02 survey maps NANSY in family MF-M1 as "
            "blocked_no_checkpoint_decoder_runtime_or_target_reference and "
            "records gap G07. No source, checkpoint, decoder, runtime or "
            "target reference exists, and no metric is inherited or pooled."),
    },
    {
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "class": "acceptance_profile_scope",
        "admitted_as_result": False,
        "boundary": (
            "Defines the Voice profile requirements. No parity, preservation, "
            "content, identity, naturalness, alignment or timing record exists "
            "for NANSY."),
    },
)


def historical_evidence() -> dict:
    return {
        "status": "no_local_nansy_execution_record",
        "records_found": 0,
        "records": list(HISTORICAL_EVIDENCE),
        "source_reported_results": None,
        "audio_artifacts": [],
        "metrics_artifacts": [],
        "transcripts": [],
        "timing": None,
        "parity": "not_measured",
        "preservation": "not_measured",
        "identity_similarity": "not_measured",
        "naturalness": "not_measured",
        "reproduced_here": False,
        "qualifies_candidate": False,
        "note": (
            "The pinned records place NANSY at paper/survey level only. No "
            "local output, metric, transcript, parity, preservation, identity, "
            "naturalness, timing or listening record exists to preserve."),
    }


def peer_separation() -> List[dict]:
    return [
        {
            "component": "openvoice-v2",
            "task": "SDK-OPENVOICE-V2",
            "path": "docs/task-evidence/openvoice-v2/report.json",
            "class": "separate_voice_conversion_candidate",
            "decision": "DEFER",
            "admitted_as_result": False,
            "inherited_metrics": False,
            "boundary": (
                "OpenVoice V2 is a distinct tone-colour conversion system with "
                "its own blocker. No source, checkpoint, tone-colour model, "
                "case or metric is inherited or pooled here."),
        },
        {
            "component": "dualvc-3",
            "task": "SDK-DUALVC-3",
            "path": "docs/task-evidence/dualvc-3/report.json",
            "class": "separate_streaming_voice_conversion_candidate",
            "decision": "DEFER",
            "admitted_as_result": False,
            "inherited_metrics": False,
            "boundary": (
                "DualVC 3 is a distinct streaming voice-conversion system with "
                "its own blocked source/weights/runtime package. No rejection "
                "count, stimulus, control or metric is inherited or pooled."),
        },
        {
            "component": "seed-vc-xls-r-300m-content-encoder",
            "task": "SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER",
            "path": "docs/task-evidence/seed-vc-xls-r-300m-content-encoder/"
                    "report.json",
            "class": "separate_content_encoder_candidate",
            "decision": "DEFER",
            "admitted_as_result": False,
            "inherited_metrics": False,
            "boundary": (
                "Seed-VC XLS-R is a separate content-encoder lead. No encoder, "
                "checkpoint, probe or result is inherited or pooled."),
        },
    ]


# ---------------------------------------------------------------------------
# Disposition, boundary and builders.
# ---------------------------------------------------------------------------


def qualification() -> dict:
    return {
        "decision": "DEFER",
        "status": "not_qualified",
        "qualification_status": "not_qualified",
        "readiness": "incomplete",
        "proposal_only": True,
        "incomplete": True,
        "evidence_status": "incomplete",
        "candidate_qualified": False,
        "qualifies": False,
        "candidate_source_present": False,
        "candidate_weights_present": False,
        "candidate_runtime_present": False,
        "candidate_output_present": False,
        "rights_cleared_input_present": False,
        "parity_result_present": False,
        "preservation_result_present": False,
        "all_required_results_present": False,
        "processor_exposure": "deferred_until_independent_review",
        "upstream_parity": False,
    }


def boundary() -> dict:
    projection = board_row_projection()
    rows = linked_rows()
    return {
        "board_file_pinned": False,
        "board_or_handoff_changed": False,
        "linked_row": projection,
        "linked_row_sha256": board_row_digest(projection),
        "linked_rows": [dict(row) for row in rows],
        "linked_rows_sha256": linked_rows_digest(rows),
        "linked_row_identity_only": True,
        "mutable_board_fields_gate": False,
        "mutable_fields_excluded": [
            "status", "owner", "claim", "review", "handoff", "blocked_reason",
            "dispatch_priority", "history", "write_scope", "deliverable",
            "acceptance", "evidence",
        ],
        "provider_registration": False,
        "descriptor_registry_change": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "installed_v0_behavior_change": False,
        "shared_build_or_ci_change": False,
        "candidate_code_vendored": False,
        "weights_vendored": False,
        "audio_added": False,
        "processed_output_added": False,
        "runtime_imported": False,
        "native_engine_built": False,
        "write_scope": WRITE_SCOPE,
    }


def scope() -> dict:
    return {
        "task_local_only": True,
        "write_scope": WRITE_SCOPE,
        "network_access": False,
        "candidate_code_downloaded": False,
        "candidate_code_vendored": False,
        "model_weights_downloaded": False,
        "model_weights_vendored": False,
        "runtime_invoked": False,
        "real_audio": False,
        "synthetic_speech": False,
        "processed_output_present": False,
        "listening": False,
        "device_timing": False,
        "benchmark_claim": False,
        "release_claim": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "public_default": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "peer_evidence_inherited": False,
        "board_or_handoff_change": False,
    }


def local_harness_checks() -> dict:
    declaration = _declaration_cases()
    json_cases = _json_adverse_cases()
    requests = _adverse_request_cases()
    reset = _reset_cases()
    probes = absence_summary()
    stimuli = stimulus_probe()
    profile = profile_source_check()
    return {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": json_cases["all_rejected"],
        "stable_board_identity_only": True,
        "inventory_identity_exact": inventory_link()["id"] == COMPONENT_ID,
        "absence_probes_all_absent": probes["all_absent"],
        "absence_probe_count_fixed": probes["probe_count"] == 20,
        "runtime_confirms_absent_unpinned": (
            runtime_readiness()["runtime_pinned"] is False),
        "voice_profile_row_pinned": (
            profile["unique_voice_row"] and profile["all_phrases_present"]),
        "invalid_requests_rejected": requests["all_rejected"],
        "nonfinite_samples_rejected": all(
            case["accepted"] is False for case in requests["cases"]
            if case["id"].startswith("nonfinite")),
        "invalid_json_rejected": json_cases["all_rejected"],
        "declaration_rejections_all_rejected": declaration["all_rejected"],
        "declaration_claims_no_qualification": (
            "accepted_control_qualifies" in declaration and
            declaration["accepted_control_qualifies"] is False),
        "reset_cases_match_expectation": reset["matches_expectation"],
        "missing_result_blocked": (
            missing_result("nansy_synthetic_placeholder")["status"] ==
            "blocked"),
        "identity_control_bit_exact": all(
            block["byte_identical"]
            for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(GATES) == 8 and all(gate["status"] == "blocked"
                                    for gate in GATES)),
        "no_result_qualifies_candidate": True,
    }


def inventory_link() -> dict:
    inventory = read_strict_json(AUDIO_ROOT /
                                 "audio-benchmark-platform/plan/INVENTORY.json")
    components = inventory.get("components")
    if not isinstance(components, list):
        raise ValueError("inventory_components_not_list")
    rows = [row for row in components
            if isinstance(row, dict) and row.get("id") == COMPONENT_ID]
    if len(rows) != 1:
        raise ValueError("inventory_row_not_unique")
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
        "plan_note": row.get("plan_note"),
    }
    expected = {
        "id": COMPONENT_ID,
        "name": COMPONENT_NAME,
        "area": "Voice and synthesis",
        "evidence_status": "considered",
        "repository": REPOSITORY,
        "disposition": "sdk-model",
        "verification_profile": "voice",
        "task": TASK,
        "plan_note": ("Stage exact model, validate analysis-to-waveform parity "
                      "and speech preservation."),
    }
    if projection != expected:
        raise ValueError("inventory_identity_changed")
    return projection


def release_gates() -> List[dict]:
    projection = board_row_projection()
    rows: List[dict] = []
    for gate in GATES:
        rows.append({
            "id": gate["id"],
            "title": gate["gate"],
            "status": "blocked",
            "qualifies": False,
            "statement": (
                "No NANSY artifact, runtime, right, matched measurement or "
                "review satisfies this requirement."),
            "reopen_condition": gate["reopen"],
            "linked_row": projection,
        })
    return rows


def reproduction() -> dict:
    return {
        "interpreter": REQUIRED_INTERPRETER,
        "observed_interpreter": platform.python_version(),
        "bytecode_disabled": True,
        "network_required": False,
        "runtime_required": False,
        "weights_required": False,
        "commands": [
            "PYTHONDONTWRITEBYTECODE=1 python3 reference.py",
            "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v "
            "test_reference.py",
            "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
        ],
        "cold_start_repeats": 3,
        "writes_only_task_directory": True,
    }


def build_report() -> dict:
    probes = absence_summary()
    declaration = _declaration_cases()
    json_cases = _json_adverse_cases()
    requests = _adverse_request_cases()
    reset = _reset_cases()
    profile = profile_rows()
    profile_check = profile_source_check()
    gates = release_gates()
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "profile": {
            "name": PROFILE,
            "label": PROFILE_LABEL,
            "source": PROFILE_SOURCE_REL,
            "source_sha256": SOURCE_PINS[PROFILE_SOURCE_REL],
            "source_check": profile_check,
        },
        "profile_rows": profile,
        "candidate_identity": source_reported_identity(),
        "task_geometry": task_geometry(),
        "absence_evidence": probes,
        "runtime_probe": runtime_readiness(),
        "asset_declaration": declaration,
        "adverse": {
            "invalid_request": requests,
            "strict_json": json_cases,
            "reset_validation": reset,
            "missing_result": missing_result("nansy_synthetic_placeholder"),
        },
        "stimulus_probe": stimulus_probe(),
        "evidence_presence": evidence_presence(),
        "historical_evidence": historical_evidence(),
        "matched_evidence": matched_evidence(),
        "peer_separation": peer_separation(),
        "exact_blockers": [dict(blocker) for blocker in EXACT_BLOCKERS],
        "required_artifacts": [dict(artifact)
                               for artifact in REQUIRED_ARTIFACTS],
        "required_results": required_results(),
        "release_gates": gates,
        "gates": [gate["id"] for gate in gates],
        "remaining_gates": [gate["id"] for gate in gates],
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "qualification": qualification(),
        "boundary": boundary(),
        "scope": scope(),
        "public_v0_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "sample_format": "float32",
            "unchanged": True,
            "candidate_mapping_present": False,
        },
        "inventory_link": inventory_link(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": {name: sha256_file(HERE / name)
                          for name in local_pin_targets()},
        "local_harness_checks": local_harness_checks(),
        "non_claims": list(NON_CLAIMS),
        "invariants": list(INVARIANTS),
        "reproduction": reproduction(),
        "generated_by": "run.py all",
    }
    assert_finite(report)
    return report


# Static task-local files only. Generated artifacts that depend on the report
# (report.json, contract.json, README.md, SOURCES.sha256 and the sidecar) are
# excluded so the report can never become self-referential.
ARTIFACT_PIN_FILES = (
    "LICENSES.md",
    "SOURCES.sha256.license",
    "contract.json.license",
    "reference.py",
    "report.json.license",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)


def local_pin_targets() -> List[str]:
    """Static committed local files whose live digest the report records."""
    return [name for name in ARTIFACT_PIN_FILES if (HERE / name).is_file()]


def report_file_bytes(report: dict | None = None) -> bytes:
    text, _ = canonical_report(report)
    return text.encode("ascii")


def build_contract() -> dict:
    report = build_report()
    _, report_digest = canonical_report(report)
    report_file = report_file_bytes(report)
    contract = {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "profile": report["profile"],
        "profile_rows": report["profile_rows"],
        "candidate_identity": report["candidate_identity"],
        "task_geometry": report["task_geometry"],
        "absence_summary": report["absence_evidence"],
        "runtime_probe": report["runtime_probe"],
        "asset_declaration_schema": {
            key: value for key, value in report["asset_declaration"].items()
            if key != "cases"
        },
        "exact_blockers": report["exact_blockers"],
        "required_artifacts": report["required_artifacts"],
        "required_results": report["required_results"],
        "release_gates": report["release_gates"],
        "gates": report["gates"],
        "matched_evidence": report["matched_evidence"],
        "qualification": report["qualification"],
        "boundary": report["boundary"],
        "scope": report["scope"],
        "public_v0_geometry": report["public_v0_geometry"],
        "inventory_link": report["inventory_link"],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "canonical_report": {
            "format": ("canonical JSON: sort_keys=True, compact separators, "
                       "allow_nan=False, one trailing newline"),
            "canonical_digest": report_digest,
            "file_sha256": sha256_bytes(report_file),
        },
        "non_claims": list(NON_CLAIMS),
        "invariants": list(INVARIANTS),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "reproduction": report["reproduction"],
    }
    assert_finite(contract)
    return contract


def report_bytes() -> bytes:
    return report_file_bytes()


if __name__ == "__main__":
    import sys

    sys.stdout.write(canonical_report()[0])
