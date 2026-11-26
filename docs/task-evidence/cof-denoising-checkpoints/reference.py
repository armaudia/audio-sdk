# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local feasibility evidence for SDK-COF-DENOISING-CHECKPOINTS.

Standard-library only and deterministic. The workspace records only a census
sentence naming CoF denoising checkpoints. No upstream repository URL,
immutable revision, source file, checkpoint name, byte count, SHA-256, runtime,
wheel, sampler configuration, rights-cleared input or model output is present.
This module therefore pins the evidence that *does* exist, probes fixed paths
for the absent artifacts, exercises a fail-closed caller-supplied run manifest
and a synthetic protocol envelope with no model, and builds the canonical
DEFER report. Nothing here is a model, inference, quality or release result.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import struct
import subprocess
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-COF-DENOISING-CHECKPOINTS"
COMPONENT_ID = "cof-denoising-checkpoints"
TASK_TITLE = "CoF denoising checkpoints"
CONTRACT_ID = "audio-sdk/cof-denoising-checkpoints-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/cof-generative-denoise-run/0.1"
ENVELOPE_SCHEMA_ID = (
    "audio-sdk/cof-denoising-checkpoints/protocol-envelope/0.1")
PROFILE = "enhancement"
PROFILE_LABEL = "Enhancement"
MODE = "feasibility"
BASE_COMMIT = "6967a728b5c4048fb01ed4522a76a6906fbcffe2"
BRANCH = "swarm/SDK-COF-DENOISING-CHECKPOINTS"
WRITE_SCOPE = "docs/task-evidence/cof-denoising-checkpoints/ only"
TASK_PREFIX = "docs/task-evidence/cof-denoising-checkpoints/"
DISPOSITION = (
    "CoF generative denoising feasibility blocker; only a census sentence "
    "names the candidate. The upstream source, exact checkpoints, generative "
    "runtime, rights and inputs are absent, so there is no implementation, "
    "execution or result.")

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
FRAME_BYTES = FRAME_SAMPLES * 4
MAX_SAMPLE_COUNT = 60 * SAMPLE_RATE_HZ
MAX_ASSET_BYTES = 4 * 1024 * 1024 * 1024
PROTOCOL_ID = "audioml-generative-run/1"
RUN_MODES = ("offline",)
FORMULATIONS = ("diffusion", "flow", "other_declared")
TRAINING_CORPORA = ("voicebank_demand", "wsj0_wham", "other_declared")
STAGES = ("pretrained", "corrective_forcing")
SAMPLERS = ("euler", "heun", "rk4", "other_declared")
DEVICES = ("cpu", "cuda", "mps")
DTYPES = ("f32", "f64")
CONTROL_KINDS = ("candidate", "identity_passthrough", "missing_runtime",
                 "noisy_control", "nonfinite_rejection")

REQUIRED_INTERPRETER = "3.12.16"
RUNTIME_MODULES = ("torch", "torchaudio")
RECORDED_RUNTIME = None
EXACT_RUNTIME_ERROR = "ModuleNotFoundError: No module named 'torch'"

CHECKPOINT_SCOPE = (
    {
        "id": "CS-01",
        "training_corpus": "VoiceBank+DEMAND",
        "formulation_count_reported": 2,
        "formulation_files_mapped": False,
        "stage": "pretrained",
        "file_names": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present": False,
    },
    {
        "id": "CS-02",
        "training_corpus": "VoiceBank+DEMAND",
        "formulation_count_reported": 2,
        "formulation_files_mapped": False,
        "stage": "corrective_forcing",
        "file_names": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present": False,
    },
    {
        "id": "CS-03",
        "training_corpus": "WSJ0+WHAM",
        "formulation_count_reported": 2,
        "formulation_files_mapped": False,
        "stage": "pretrained",
        "file_names": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present": False,
    },
    {
        "id": "CS-04",
        "training_corpus": "WSJ0+WHAM",
        "formulation_count_reported": 2,
        "formulation_files_mapped": False,
        "stage": "corrective_forcing",
        "file_names": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present": False,
    },
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
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
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
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/classical-wiener-denoising/README.md":
        "84cbbaa1599838614433f71c7e4144290dbe1fbc252d9ca65a3e6eb20a80ef85",
    "docs/task-evidence/classical-wiener-denoising/report.json":
        "b395b08417212cdf07988c359dde424e9ee011d5d961adfda0d668b8251be8b0",
    "docs/task-evidence/cleanunet-dns-large-high/README.md":
        "4b75817d7ba211530fdaa5787264bb207cd430691932c5c41b5faf21f13cbb5f",
    "docs/task-evidence/cleanunet-dns-large-high/report.json":
        "23289aecb0e5b502e92a14ee43f2d94be0a2a069b466eebeb7f6281e58a84468",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                  "SDK-FND-PROVIDER")

MANIFEST_FIELDS = ("schema_id", "run_id", "model", "runtime", "command",
                   "assets", "input", "output", "controls", "rights")
MODEL_FIELDS = ("upstream_repository", "upstream_revision", "code_license",
                "formulation", "training_corpus", "stage", "sampler", "steps",
                "seed", "padding_profile")
RUNTIME_FIELDS = ("python", "torch", "torchaudio", "device", "dtype",
                  "intra_op_threads", "interop_op_threads",
                  "deterministic_algorithms", "offline", "install_reference",
                  "wheel_digests")
COMMAND_FIELDS = ("cli", "request_argument", "result_argument", "network",
                  "downloads")
ASSET_FIELDS = ("asset_id", "name", "byte_count", "sha256", "terms_sha256",
                "present_at_review")
INPUT_FIELDS = ("sample_rate_hz", "channels", "sample_count", "dtype",
                "sha256", "finite", "peak")
OUTPUT_FIELDS = ("sample_count", "sha256", "finite", "peak",
                 "delay_compensation_samples")
CONTROL_FIELDS = ("id", "kind")
RIGHTS_FIELDS = ("source_terms", "runtime_terms", "weight_terms",
                 "training_data_terms", "input_terms", "output_use",
                 "review_reference", "claims_qualified")

SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX64 = re.compile(r"^(?=.*[1-9a-f])[0-9a-f]{64}$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
REPO_URL = re.compile(r"^https://[a-z0-9][a-z0-9.-]*/[A-Za-z0-9._/-]+$")
PYTHON_VERSION = re.compile(r"^3\.[0-9]{1,2}\.[0-9]{1,2}$")
PACKAGE_VERSION = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+(?:[a-z0-9.+_-]*)$")
REQUEST_PATH = re.compile(
    r"^/attempt/[a-z0-9][a-z0-9._-]{0,63}/request\.json$")
RESULT_PATH = re.compile(
    r"^/attempt/[a-z0-9][a-z0-9._-]{0,63}/result\.json$")

PROFILE_PHRASES = (
    "Run identity/noisy control and an established task-matched baseline.",
    "Score paired SI-SDR and STOI where permitted clean references exist.",
    "Measure clean-speech preservation, peaks and invalid outputs.",
    "For unpaired speech use a separately labeled predictive screen or "
    "authorized listening.",
    "Report alignment, state, memory and measured content/availability timing "
    "for the exact runtime.",
)

CENSUS_PHRASES = (
    "CoF denoising checkpoints",
    "Diffusion / flow generative speech enhancement, offline quality reference",
    "VoiceBank+Demand and WSJ0+WHAM denoising checkpoints",
    "two formulations and both pretrained and corrective-forcing stages",
    "verify weight/code/data terms, sampler, hardware and output fidelity",
)

ENHANCEMENT_REQUIREMENTS = (
    {
        "id": "ENH-01",
        "requirement": "Identity/noisy control plus an established "
                       "task-matched baseline.",
        "status": "blocked",
        "evidence": (
            "The synthetic envelope copies caller bytes exactly and labels an "
            "identity control, but no CoF candidate, noise injection or "
            "established enhancement baseline is executed."),
    },
    {
        "id": "ENH-02",
        "requirement": "Paired SI-SDR and STOI where permitted clean "
                       "references exist.",
        "status": "blocked",
        "evidence": (
            "No rights-cleared clean-reference cohort, independent scorer or "
            "candidate output exists; no paired metric is computed."),
    },
    {
        "id": "ENH-03",
        "requirement": "Clean-speech preservation, peaks and invalid outputs.",
        "status": "blocked",
        "evidence": (
            "Only synthetic finite/peak breath checks on copied bytes exist; "
            "no clean-speech preservation result and no candidate output "
            "validity result is available."),
    },
    {
        "id": "ENH-04",
        "requirement": "Alignment, state, memory and measured "
                       "content/availability timing for the exact runtime.",
        "status": "blocked",
        "evidence": (
            "The exact generative runtime, sampler, padding recipe and device "
            "are absent; no alignment, state, memory or availability timing "
            "was measured."),
    },
    {
        "id": "ENH-05",
        "requirement": "Separately labeled predictive screen or authorized "
                       "listening for unpaired speech.",
        "status": "blocked",
        "evidence": (
            "No unpaired speech, predictive screen or listening protocol and "
            "result exists."),
    },
    {
        "id": "ENH-06",
        "requirement": "Quiet and active speech, idle noise, low SNR and "
                       "onset/offset condition coverage.",
        "status": "blocked",
        "evidence": (
            "No real or synthetic speech condition is scored; the envelope "
            "uses one deterministic placeholder frame that is not audio "
            "evidence."),
    },
    {
        "id": "ENH-07",
        "requirement": "Separate paired, unpaired, synthetic, human and "
                       "source-reported evidence.",
        "status": "documented",
        "evidence": (
            "The report keeps synthetic envelope, admission schema, historical "
            "census prose and missing real results in distinct sections; no "
            "category is pooled with another."),
    },
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "evidence_register_and_policy_boundary",
        "present": True,
        "verified": True,
        "blocked": False,
        "requirement": (
            "The pinned candidate census, structured inventory record, "
            "acceptance profile, SDK delivery plan and unchanged v0 contract "
            "boundary."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-02",
        "kind": "exact_upstream_source_snapshot",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The exact upstream repository URL, immutable commit or release "
            "revision, source tree for both formulations, code license, notice "
            "and model-card/README text."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-03",
        "kind": "exact_checkpoint_assets",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "The complete checkpoint set for VoiceBank+DEMAND and WSJ0+WHAM "
            "covering the two reported formulations and both the pretrained "
            "and corrective-forcing stages, with exact file names, immutable "
            "revision, byte counts and SHA-256 values."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-04",
        "kind": "pinned_generative_runtime",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A locked offline Python/PyTorch-class runtime with wheel names, "
            "versions, byte counts, SHA-256 values and install location, plus "
            "the exact sampler, step count, seed, dtype, device, context and "
            "padding recipe."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_inputs_and_training_data",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A digest-pinned caller-owned input set with corpus, acquisition, "
            "evaluation, derived-output and redistribution decisions, plus "
            "checkpoint training-data terms for both corpora and an "
            "attribution record."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-06",
        "kind": "reproduced_enhancement_results",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A deterministic offline run in the exact runtime with per-item "
            "input/output hashes, finite and length-preserving checks, exact "
            "repeats, peak/RSS values, identity/noisy controls, paired "
            "SI-SDR/STOI, preservation, alignment, state, memory and "
            "content/availability timing."),
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-07",
        "kind": "provider_intake_and_public_surface",
        "present": False,
        "verified": False,
        "blocked": True,
        "requirement": (
            "A separate versioned OFF-by-default developer tool or provider "
            "intake with clean-install proof, empty defaults, no registry or "
            "shared-build change, separate mode/platform measurements and "
            "independent exact-head review after every other gate clears."),
        "revision": None,
        "sha256": None,
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "linked_gates": ["RG-01"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No upstream source identity is recorded. The pinned census names "
            "'CoF denoising checkpoints' and an 'Official 2026 repository' but "
            "gives no repository URL, commit, release tag, source file, code "
            "license or notice. No CoF source is present at any probed path."),
        "required_action": (
            "Supply the exact upstream repository URL and immutable revision "
            "for both formulations, the complete source snapshot, the code "
            "license and notice text, and a formulation-to-file map. No "
            "download is permitted inside this package."),
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "linked_gates": ["RG-01", "RG-03"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No checkpoint identity or byte set is recorded. The census says "
            "VoiceBank+Demand and WSJ0+WHAM checkpoints exist for two "
            "formulations and both pretrained and corrective-forcing stages, "
            "but records no file names, immutable revision, byte counts or "
            "SHA-256 values. No checkpoint file is present at any probed "
            "path."),
        "required_action": (
            "Stage the complete checkpoint set for both corpora, both "
            "formulations and both stages with exact file names, immutable "
            "revision, byte counts and matching SHA-256 values, plus an "
            "artifact-specific terms review. No weight may be downloaded, "
            "reconstructed or inferred here."),
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "linked_gates": ["RG-02"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No generative runtime is installed or pinned. The probed "
            "interpreters expose no torch or torchaudio, no CoF environment or "
            "wheel lock exists, and no sampler, step count, seed, dtype, "
            "device, context or padding recipe is recorded."),
        "required_action": (
            "Provide a locked offline Python/PyTorch-class runtime with wheel "
            "names, versions, byte counts, SHA-256 values and install "
            "location, plus the exact sampler, steps, seed, dtype, device, "
            "context and padding recipe used for the reference."),
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "linked_gates": ["RG-04"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No rights-cleared caller input set or training-data review "
            "exists. The census says to verify weight/code/data terms but "
            "records no license, training corpus terms, derived-output "
            "permission or redistribution decision for either corpus."),
        "required_action": (
            "Provide a digest-pinned, rights-reviewed caller-owned input set "
            "with corpus, acquisition, evaluation, derived-output and "
            "redistribution decisions, the checkpoint training-data terms for "
            "both corpora, and an attribution record."),
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "linked_gates": ["RG-05", "RG-06"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No CoF inference or enhancement result is reproduced. Without "
            "source, checkpoint bytes, runtime and inputs, there is no "
            "identity/noisy control, candidate output, paired SI-SDR/STOI, "
            "clean-speech preservation, finite/length check, alignment, "
            "state, memory or content/availability timing."),
        "required_action": (
            "After the source, checkpoint, runtime and rights gates clear, run "
            "both corpora and both stages offline with deterministic settings "
            "and no network; record per-item hashes, finite and "
            "length-preserving checks, exact repeats, identity/noisy controls, "
            "paired SI-SDR/STOI, preservation, peaks, alignment, state, "
            "memory and timing."),
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "linked_gates": ["RG-07", "RG-08"],
        "status": "open",
        "qualifies": False,
        "statement": (
            "No provider, descriptor, registry entry, default selection, "
            "mode/platform measurement, listening test, benchmark result or "
            "release claim exists. The package is task-local evidence only."),
        "required_action": (
            "Measure mode and platform separately, record device timing and "
            "resources, run authorized listening or a labeled predictive "
            "screen, then open a separate versioned OFF-by-default provider "
            "intake with clean-install proof and independent exact-head "
            "review."),
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_and_license_provenance",
        "status": "blocked",
        "statement": (
            "No exact upstream URL, immutable revision, source snapshot, code "
            "license or notice exists for either CoF formulation."),
        "reopen_condition": (
            "Stage both formulation source snapshots at an immutable revision "
            "with complete license, notice, model-card and mapping records, "
            "then record an independent rights review."),
    },
    {
        "id": "RG-02",
        "title": "pinned_runtime_and_offline_install",
        "status": "blocked",
        "statement": (
            "No generative runtime, wheel lock, install location, import "
            "digest, sampler, step count, seed, dtype, device or padding "
            "recipe is recorded."),
        "reopen_condition": (
            "Provide a locked offline runtime with wheel hashes, install "
            "location, clean-room import digest and the exact sampler "
            "configuration."),
    },
    {
        "id": "RG-03",
        "title": "checkpoint_assets_and_per_file_digests",
        "status": "blocked",
        "statement": (
            "No checkpoint file name, revision, byte count or SHA-256 is "
            "recorded for either corpus, formulation or stage."),
        "reopen_condition": (
            "Stage every checkpoint, config and metadata file for both corpora "
            "and both stages and verify each byte count and SHA-256 against an "
            "immutable revision."),
    },
    {
        "id": "RG-04",
        "title": "rights_cleared_inputs_and_training_data",
        "status": "blocked",
        "statement": (
            "No rights-reviewed input set, training-data terms, "
            "derived-output permission or redistribution decision exists."),
        "reopen_condition": (
            "Freeze a permitted, digest-pinned input set with corpus, "
            "acquisition, evaluation, derived-output and redistribution "
            "decisions plus checkpoint training-data terms and attribution."),
    },
    {
        "id": "RG-05",
        "title": "reference_execution_and_output_validity",
        "status": "blocked",
        "statement": (
            "No CoF inference, finite/length-preserving output check, "
            "deterministic repeat, sampler reproducibility check or resource "
            "measurement exists."),
        "reopen_condition": (
            "Execute the pinned checkpoints offline in the exact runtime and "
            "record per-item output hashes, finite/length preservation, exact "
            "repeats, sampler settings and peak/RSS values."),
    },
    {
        "id": "RG-06",
        "title": "enhancement_profile_against_real_runtime",
        "status": "blocked",
        "statement": (
            "The Enhancement profile is not satisfied: no identity/noisy "
            "control, task-matched baseline, paired SI-SDR/STOI, "
            "clean-speech preservation or alignment/state/timing result "
            "exists."),
        "reopen_condition": (
            "Run every Enhancement-profile case on a rights-cleared cohort "
            "against the installed runtime and both checkpoints, including "
            "quiet/active speech, idle noise, onset/offset and adverse "
            "controls."),
    },
    {
        "id": "RG-07",
        "title": "mode_platform_timing_resources_and_listening",
        "status": "blocked",
        "statement": (
            "No offline/GPU/CPU timing, p95/p99 latency, memory, pacing, "
            "device, energy, listening or benchmark measurement exists."),
        "reopen_condition": (
            "Measure each mode and platform separately with timing, resources "
            "and pacing, and complete authorized listening or a separately "
            "labeled predictive screen."),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "statement": (
            "No provider, descriptor, registry entry, default, shared-build "
            "change, clean-install proof or independent review exists."),
        "reopen_condition": (
            "Open a separate versioned OFF-by-default provider intake with "
            "clean-install proof, no shared default/build change and "
            "independent exact-head approval after all prior gates clear."),
    },
)

NON_CLAIMS = (
    "No CoF source, repository, checkpoint, weight, config or sampler "
    "implementation is present, loaded, deserialized or reconstructed.",
    "No torch, torchaudio, generative runtime or model dependency is "
    "imported, installed, linked or executed.",
    "No real audio, corpus, manifest payload or model output is read or "
    "produced.",
    "No CoF inference, quality, fidelity, parity, speed, resource, listening, "
    "device or benchmark result is reproduced or claimed.",
    "The synthetic envelope and admission control are protocol plumbing only; "
    "they are not a model, a sampler, a checkpoint, a quality result or a "
    "qualification.",
    "No provider, descriptor, registry, default, public ABI, shared build or "
    "CI change exists.",
    "The census sentence is source-reported context only and is not promoted "
    "to measured evidence.",
)

REQUIRED_RESULTS = (
    "Exact upstream URL, immutable revision, source snapshot, license and "
    "notice for both formulations.",
    "Complete checkpoint manifest for both corpora, both formulations and "
    "both stages with byte counts and SHA-256.",
    "Locked offline runtime with wheel digests, install location and "
    "clean-room import digest.",
    "Exact sampler, steps, seed, dtype, device, context and padding recipe.",
    "Rights-cleared, digest-pinned caller inputs and checkpoint "
    "training-data terms.",
    "Deterministic reproduced runs with finite/length-preserving outputs and "
    "exact repeats.",
    "Identity/noisy controls, task-matched baseline, paired SI-SDR/STOI and "
    "clean-speech preservation.",
    "Alignment, state, memory and content/availability timing for the exact "
    "runtime.",
    "Separate mode/platform timing, authorized listening and independent "
    "provider intake review.",
)

REOPENING_CONDITIONS = (
    "Pin the exact upstream source revision, license and notice for both "
    "formulations.",
    "Stage both corpora and both stages with per-file byte counts and SHA-256 "
    "values.",
    "Provide a locked offline runtime and the exact sampler configuration.",
    "Provide rights-cleared inputs and checkpoint training-data terms.",
    "Reproduce deterministic offline runs and complete the Enhancement "
    "profile, including controls and preservation.",
    "Measure mode and platform separately, complete listening or a labeled "
    "predictive screen, then open a separate OFF-by-default intake and "
    "independent review.",
)

EVIDENCE_SNIPPETS = {
    "research/noise_suppression_candidate_census.md": CENSUS_PHRASES,
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": PROFILE_PHRASES,
}

ABSENCE_PROBES = (
    "data/models/cof",
    "data/models/cof/denoising",
    "data/models/cof/denoising/voicebank-demand/pretrained",
    "data/models/cof/denoising/voicebank-demand/corrective-forcing",
    "data/models/cof/denoising/wsj0-wham/pretrained",
    "data/models/cof/denoising/wsj0-wham/corrective-forcing",
    "data/checkouts/cof",
    "data/checkouts/cof-denoising",
    "data/envs/cof",
    "data/envs/cof-denoising",
    "data/manifests/cof-runtime.lock",
    "data/manifests/cof-checkpoints.json",
    "research/cof",
    "research/cof-denoising",
    "reports/cof",
    "reports/cof-denoising",
)

WORKTREE_ABSENCE_PROBES = (
    "third_party/cof",
    "third_party/cof-denoising",
    "build/check-env/lib/python3.12/site-packages/torch",
    "build/check-env/lib/python3.12/site-packages/torchaudio",
    "models/cof",
    "data/cof",
)

HOME_ABSENCE_PROBES = (
    "~/.cache/huggingface/hub/models--cof--denoising",
    "~/.cache/huggingface/hub/models--cof-denoising",
    "~/.cache/torch/hub/checkpoints/cof",
    "~/.pyenv/versions/3.12.16/lib/python3.12/site-packages/torch",
    "~/.pyenv/versions/3.11.5/lib/python3.11/site-packages/torch",
)


class AdmissionError(ValueError):
    """A fail-closed task-local admission or envelope rejection."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


# --------------------------------------------------------------------------
# Strict JSON, canonical serialization and digests
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


def _decimal_string(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("nonfinite_decimal")
    text = repr(float(value))
    if "e" in text or "E" in text:
        text = format(float(value), ".17f").rstrip("0").rstrip(".")
    if text in {"-0", "-0.0"}:
        text = "0"
    if text.startswith("+"):
        text = text[1:]
    return text


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


# --------------------------------------------------------------------------
# Task-local git scope
# --------------------------------------------------------------------------
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
    """Newest merge-base between HEAD and an available PR base ref.

    Returns None only when no base ref exists, which the verifier treats as a
    fail-closed condition rather than a silent pass.
    """
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


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]


def linked_rows(path: Path | None = None) -> list[dict]:
    board = read_strict_json(path or (AUDIO_ROOT / BOARD_TASK_ROW))
    by_id = {row.get("id"): row for row in board.get("tasks", [])
             if isinstance(row, dict)}
    rows: list[dict] = []
    for row_id in LINKED_ROW_IDS:
        row = by_id.get(row_id)
        if row is None:
            raise ValueError("linked_row_missing:" + row_id)
        rows.append({field: row.get(field) for field in BOARD_ROW_FIELDS})
    return rows


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return object_digest(rows if rows is not None else linked_rows())


def _absent(path: Path, label: str) -> None:
    if path.exists():
        raise ValueError("artifact_present_reopen_required:" + label)


def absence_probes(audio_root: Path,
                   probes: tuple[str, ...] = ABSENCE_PROBES) -> list[dict]:
    rows: list[dict] = []
    for relative in probes:
        _absent(Path(audio_root) / relative, relative)
        rows.append({"path": relative, "searched_workspace": True,
                     "searched_sdk_worktree": False, "present": False})
    return rows


def worktree_absence_probes(
        probes: tuple[str, ...] = WORKTREE_ABSENCE_PROBES) -> list[dict]:
    rows: list[dict] = []
    for relative in probes:
        _absent(WORKTREE / relative, relative)
        rows.append({"path": relative, "searched_workspace": False,
                     "searched_sdk_worktree": True, "present": False})
    return rows


def home_absence_probes(
        probes: tuple[str, ...] = HOME_ABSENCE_PROBES) -> list[dict]:
    rows: list[dict] = []
    home = Path.home()
    for relative in probes:
        path = home / relative[2:] if relative.startswith("~/") else Path(
            relative)
        _absent(path, relative)
        rows.append({"path": relative, "searched_home_cache": True,
                     "present": False})
    return rows


def absence_summary(workspace_rows: list[dict],
                    worktree_rows: list[dict],
                    home_rows: list[dict]) -> dict:
    all_rows = workspace_rows + worktree_rows + home_rows
    return {
        "probe_count": len(all_rows),
        "workspace_probe_count": len(workspace_rows),
        "worktree_probe_count": len(worktree_rows),
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
# Evidence, runtime and checkpoint presence
# --------------------------------------------------------------------------
def evidence_snippet_check() -> dict:
    rows: dict[str, dict] = {}
    for relative, phrases in sorted(EVIDENCE_SNIPPETS.items()):
        path = AUDIO_ROOT / relative
        if not path.is_file():
            raise ValueError("evidence_source_missing:" + relative)
        text = path.read_text(encoding="utf-8")
        found = {phrase: (phrase in text) for phrase in phrases}
        missing = [phrase for phrase, present in found.items() if not present]
        if missing:
            raise ValueError("evidence_snippet_missing:" + missing[0])
        rows[relative] = {
            "sha256": sha256_file(path),
            "byte_count": path.stat().st_size,
            "snippets_required": len(phrases),
            "snippets_found": len(phrases),
            "verified": True,
        }
    return rows


def inventory_record() -> dict:
    document = read_strict_json(
        AUDIO_ROOT / "audio-benchmark-platform/plan/INVENTORY.json")
    matches = [row for row in document.get("components", [])
               if isinstance(row, dict)
               and row.get("id") == COMPONENT_ID]
    if len(matches) != 1:
        raise ValueError("inventory_record_not_unique:" + COMPONENT_ID)
    row = matches[0]
    expected = {
        "verification_profile": "enhancement",
        "disposition": "sdk-model",
        "task": TASK,
        "area": "Enhancement",
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise ValueError("inventory_field_mismatch:" + key)
    evidence = row.get("evidence") or []
    if not any(
            item.get("path") ==
            "research/noise_suppression_candidate_census.md"
            and item.get("line") == 62
            and item.get("record_name") == TASK_TITLE
            for item in evidence):
        raise ValueError("inventory_evidence_link_mismatch")
    return {
        "id": row["id"],
        "name": row["name"],
        "area": row["area"],
        "evidence_status": row["evidence_status"],
        "repository": row["repository"],
        "disposition": row["disposition"],
        "verification_profile": row["verification_profile"],
        "task": row["task"],
        "evidence_path": "research/noise_suppression_candidate_census.md",
        "evidence_line": 62,
        "verified": True,
    }


def runtime_readiness() -> dict:
    modules: list[dict] = []
    for name in RUNTIME_MODULES:
        try:
            found = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError):
            found = False
        modules.append({
            "module": name,
            "module_spec_found": found,
            "installed_version": None,
            "import_error": (None if found else
                             "ModuleNotFoundError: No module named '%s'"
                             % name),
        })
    observed = platform.python_version()
    return {
        "blocked": True,
        "interpreter_required": REQUIRED_INTERPRETER,
        "interpreter_observed": observed,
        "interpreter_matches": observed == REQUIRED_INTERPRETER,
        "recorded_runtime": RECORDED_RUNTIME,
        "runtime_versions_recorded": False,
        "runtime_overlay": [],
        "modules": modules,
        "importable": False,
        "module_spec_found": any(row["module_spec_found"] for row in modules),
        "installed_version": None,
        "install_location": None,
        "exact_error": EXACT_RUNTIME_ERROR,
        "runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "reopen_conditions": [
            "Pin wheel names, versions, byte counts and SHA-256 values for the "
            "exact CoF generative runtime.",
            "Record the isolated install location and a clean-room import "
            "digest.",
            "Record the exact sampler, steps, seed, dtype, device, context "
            "and padding recipe.",
            "Load the staged checkpoints offline with networking disabled "
            "before any claim.",
        ],
    }


def evidence_presence() -> dict:
    inventory = inventory_record()
    snippets = evidence_snippet_check()
    return {
        "evidence_register_present": True,
        "inventory_record_present": True,
        "acceptance_profile_present": True,
        "census_source_present": True,
        "census_source_used_for": "source_reported_context_only",
        "inventory_record": inventory,
        "snippet_checks": snippets,
        "source_present": False,
        "source_identity_recorded": False,
        "runtime_present": False,
        "runtime_pinned": False,
        "weights_present": False,
        "weights_identified": False,
        "input_media_present": False,
        "exact_source_runtime_weights_conjunction_present": False,
        "runtime_imported": False,
        "weights_loaded": False,
        "model_executed": False,
        "audio_read": False,
        "network_used": False,
    }


def checkpoint_presence() -> dict:
    rows = []
    for row in CHECKPOINT_SCOPE:
        corpus = {"VoiceBank+DEMAND": "voicebank-demand",
                  "WSJ0+WHAM": "wsj0-wham"}[row["training_corpus"]]
        probe = "data/models/cof/denoising/%s/%s" % (corpus, row["stage"])
        rows.append(dict(row, probe_path=probe))
    return {
        "rows": rows,
        "row_count": len(rows),
        "artifact_count_asserted": False,
        "file_names_recorded": False,
        "revisions_recorded": False,
        "byte_counts_recorded": False,
        "sha256_values_recorded": False,
        "any_checkpoint_present": False,
        "weights_loaded": False,
        "model_executed": False,
    }


def profile_row_check() -> dict:
    path = (AUDIO_ROOT /
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| Enhancement |")]
    if len(rows) != 1:
        raise ValueError("enhancement_profile_row_not_unique")
    missing = [phrase for phrase in PROFILE_PHRASES
               if phrase not in rows[0]]
    if missing:
        raise ValueError("enhancement_profile_phrase_missing:" + missing[0])
    return {
        "profile": PROFILE,
        "label": PROFILE_LABEL,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "row_found": True,
        "required_phrases": len(PROFILE_PHRASES),
        "phrases_found": len(PROFILE_PHRASES),
        "verified": True,
    }


# --------------------------------------------------------------------------
# Strict manifest admission (task-local; not an SDK or runtime contract)
# --------------------------------------------------------------------------
def _require_object(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise AdmissionError(path + "_not_object")
    return value


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> dict:
    obj = _require_object(value, path)
    keys = tuple(sorted(obj))
    if keys != tuple(sorted(expected)):
        missing = sorted(set(expected) - set(obj))
        extra = sorted(set(obj) - set(expected))
        if missing:
            raise AdmissionError(path + "_missing_field:" + missing[0])
        raise AdmissionError(path + "_extra_field:" + extra[0])
    return obj


def _text(obj: dict, key: str, path: str, pattern: re.Pattern | None = None,
          allowed: tuple[str, ...] | None = None,
          maximum: int = 4096) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        raise AdmissionError(path + "_" + key + "_not_text")
    if len(value) > maximum:
        raise AdmissionError(path + "_" + key + "_too_long")
    if allowed is not None and value not in allowed:
        raise AdmissionError(path + "_" + key + "_not_allowed")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise AdmissionError(path + "_" + key + "_invalid")
    return value


def _int_field(obj: dict, key: str, path: str, minimum: int,
               maximum: int) -> int:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise AdmissionError(path + "_" + key + "_not_int")
    if value < minimum or value > maximum:
        raise AdmissionError(path + "_" + key + "_out_of_range")
    return value


def _decimal_field(obj: dict, key: str, path: str, minimum: str,
                   maximum: str) -> Decimal:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise AdmissionError(path + "_" + key + "_not_decimal")
    if isinstance(value, float) and not math.isfinite(value):
        raise AdmissionError(path + "_" + key + "_nonfinite")
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise AdmissionError(path + "_" + key + "_not_decimal")
    if not number.is_finite():
        raise AdmissionError(path + "_" + key + "_nonfinite")
    if number < Decimal(minimum) or number > Decimal(maximum):
        raise AdmissionError(path + "_" + key + "_out_of_range")
    return number


def _bool_field(obj: dict, key: str, path: str,
                expected: bool | None = None) -> bool:
    value = obj.get(key)
    if not isinstance(value, bool):
        raise AdmissionError(path + "_" + key + "_not_bool")
    if expected is not None and value is not expected:
        raise AdmissionError(path + "_" + key + "_wrong_value")
    return value


def _hex_field(obj: dict, key: str, path: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise AdmissionError(path + "_" + key + "_not_sha256")
    return value


def _digest_map(value: Any, path: str) -> dict:
    obj = _require_object(value, path)
    if not obj:
        raise AdmissionError(path + "_empty")
    if len(obj) > 16:
        raise AdmissionError(path + "_too_many")
    for key in sorted(obj):
        if SLUG.fullmatch(key) is None:
            raise AdmissionError(path + "_key_invalid")
        _hex_field(obj, key, path)
    return obj


def validate_manifest(manifest: dict) -> None:
    """Validate one caller-supplied CoF run manifest; mutate nothing."""
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root.get("schema_id") != ADMISSION_SCHEMA_ID:
        raise AdmissionError("manifest_schema_id")
    _text(root, "run_id", "manifest", SLUG)

    model = _exact_keys(root.get("model"), MODEL_FIELDS, "model")
    _text(model, "upstream_repository", "model", REPO_URL)
    _text(model, "upstream_revision", "model", COMMIT_SHA)
    _text(model, "code_license", "model", maximum=256)
    _text(model, "formulation", "model", allowed=FORMULATIONS)
    _text(model, "training_corpus", "model", allowed=TRAINING_CORPORA)
    _text(model, "stage", "model", allowed=STAGES)
    _text(model, "sampler", "model", allowed=SAMPLERS)
    _int_field(model, "steps", "model", 1, 1024)
    _int_field(model, "seed", "model", 0, (1 << 63) - 1)
    _text(model, "padding_profile", "model", maximum=256)

    runtime = _exact_keys(root.get("runtime"), RUNTIME_FIELDS, "runtime")
    _text(runtime, "python", "runtime", PYTHON_VERSION)
    _text(runtime, "torch", "runtime", PACKAGE_VERSION)
    _text(runtime, "torchaudio", "runtime", PACKAGE_VERSION)
    _text(runtime, "device", "runtime", allowed=DEVICES)
    _text(runtime, "dtype", "runtime", allowed=DTYPES)
    _int_field(runtime, "intra_op_threads", "runtime", 1, 64)
    _int_field(runtime, "interop_op_threads", "runtime", 1, 64)
    _bool_field(runtime, "deterministic_algorithms", "runtime", True)
    _bool_field(runtime, "offline", "runtime", True)
    _text(runtime, "install_reference", "runtime", maximum=256)
    _digest_map(runtime.get("wheel_digests"), "runtime_wheel_digests")

    command = _exact_keys(root.get("command"), COMMAND_FIELDS, "command")
    if command.get("cli") != PROTOCOL_ID:
        raise AdmissionError("command_cli")
    _text(command, "request_argument", "command", REQUEST_PATH)
    _text(command, "result_argument", "command", RESULT_PATH)
    if command.get("network") != "denied":
        raise AdmissionError("command_network")
    if command.get("downloads") != "denied":
        raise AdmissionError("command_downloads")

    assets = root.get("assets")
    if not isinstance(assets, list) or not assets:
        raise AdmissionError("assets_not_nonempty_list")
    if len(assets) > 16:
        raise AdmissionError("assets_too_many")
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for index, raw in enumerate(assets):
        path = "assets[%d]" % index
        asset = _exact_keys(raw, ASSET_FIELDS, path)
        asset_id = _text(asset, "asset_id", path, SLUG)
        name = _text(asset, "name", path, maximum=256)
        if asset_id in seen_ids:
            raise AdmissionError("assets_duplicate_asset_id")
        if name in seen_names:
            raise AdmissionError("assets_duplicate_name")
        seen_ids.add(asset_id)
        seen_names.add(name)
        _int_field(asset, "byte_count", path, 1, MAX_ASSET_BYTES)
        _hex_field(asset, "sha256", path)
        _hex_field(asset, "terms_sha256", path)
        if _bool_field(asset, "present_at_review", path, True) is not True:
            raise AdmissionError("assets_not_present")

    input_row = _exact_keys(root.get("input"), INPUT_FIELDS, "input")
    if _int_field(input_row, "sample_rate_hz", "input", SAMPLE_RATE_HZ,
                  SAMPLE_RATE_HZ) != SAMPLE_RATE_HZ:
        raise AdmissionError("input_sample_rate_hz")
    if _int_field(input_row, "channels", "input", 1, 1) != 1:
        raise AdmissionError("input_channels")
    sample_count = _int_field(input_row, "sample_count", "input", 1,
                              MAX_SAMPLE_COUNT)
    if input_row.get("dtype") != "f32":
        raise AdmissionError("input_dtype")
    _hex_field(input_row, "sha256", "input")
    if _bool_field(input_row, "finite", "input", True) is not True:
        raise AdmissionError("input_nonfinite")
    _decimal_field(input_row, "peak", "input", "0", "1")

    output_row = _exact_keys(root.get("output"), OUTPUT_FIELDS, "output")
    if _int_field(output_row, "sample_count", "output", 1,
                  MAX_SAMPLE_COUNT) != sample_count:
        raise AdmissionError("output_length_mismatch")
    _hex_field(output_row, "sha256", "output")
    if _bool_field(output_row, "finite", "output", True) is not True:
        raise AdmissionError("output_nonfinite")
    _decimal_field(output_row, "peak", "output", "0", "1")
    if _int_field(output_row, "delay_compensation_samples", "output", 0,
                  0) != 0:
        raise AdmissionError("output_delay")

    controls = root.get("controls")
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise AdmissionError("controls_not_exact_list")
    kinds: list[str] = []
    control_ids: set[str] = set()
    for index, raw in enumerate(controls):
        path = "controls[%d]" % index
        control = _exact_keys(raw, CONTROL_FIELDS, path)
        control_id = _text(control, "id", path, SLUG)
        if control_id in control_ids:
            raise AdmissionError("controls_duplicate_id")
        control_ids.add(control_id)
        kinds.append(_text(control, "kind", path, allowed=CONTROL_KINDS))
    if sorted(kinds) != sorted(CONTROL_KINDS):
        raise AdmissionError("controls_kind_set")

    rights = _exact_keys(root.get("rights"), RIGHTS_FIELDS, "rights")
    for key in ("source_terms", "runtime_terms", "weight_terms",
                "training_data_terms", "input_terms", "output_use",
                "review_reference"):
        _text(rights, key, "rights", maximum=256)
    if _bool_field(rights, "claims_qualified", "rights", False) is not False:
        raise AdmissionError("rights_claims_qualified")


# --------------------------------------------------------------------------
# Synthetic protocol envelope (no runtime, no model, no audio)
# --------------------------------------------------------------------------
def synthetic_frame() -> list[float]:
    """Deterministic 160-sample float32 frame with binary-fraction values."""
    return [((index * 37) % 201 - 100) / 128.0
            for index in range(FRAME_SAMPLES)]


def frame_bytes(values: list[float]) -> bytes:
    if len(values) != FRAME_SAMPLES:
        raise AdmissionError("frame_length")
    return struct.pack("<%df" % FRAME_SAMPLES, *values)


def frame_from_bytes(payload: bytes) -> list[float]:
    if len(payload) != FRAME_BYTES:
        raise AdmissionError("payload_byte_count")
    values = list(struct.unpack("<%df" % FRAME_SAMPLES, payload))
    if not all(math.isfinite(value) for value in values):
        raise AdmissionError("payload_nonfinite")
    return values


def _payload_from_hex(text: Any) -> bytes:
    if not isinstance(text, str) or len(text) != FRAME_BYTES * 2:
        raise AdmissionError("payload_hex_length")
    try:
        payload = bytes.fromhex(text)
    except ValueError:
        raise AdmissionError("payload_hex_invalid")
    if len(payload) != FRAME_BYTES:
        raise AdmissionError("payload_byte_count")
    return payload


def _request_input() -> dict:
    payload = frame_bytes(synthetic_frame())
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "sample_count": FRAME_SAMPLES,
        "dtype": "f32",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "byte_count": len(payload),
        "payload_hex": payload.hex(),
    }


def protocol_request() -> dict:
    return {
        "protocol": PROTOCOL_ID,
        "request_id": "synthetic-envelope-0001",
        "mode": "offline",
        "model": {
            "formulation": "flow",
            "sampler": "other_declared",
            "steps": 1,
            "seed": 0,
        },
        "input": _request_input(),
        "options": {
            "network": "denied",
            "downloads": "denied",
            "writes": "attempt_only",
        },
    }


ENVELOPE_MODEL_FIELDS = ("formulation", "sampler", "steps", "seed")
ENVELOPE_INPUT_FIELDS = ("sample_rate_hz", "channels", "sample_count",
                         "dtype", "sha256", "byte_count", "payload_hex")
ENVELOPE_OPTION_FIELDS = ("network", "downloads", "writes")
ENVELOPE_FIELDS = ("protocol", "request_id", "mode", "model", "input",
                   "options")


def validate_protocol_request(request: Any) -> bytes:
    root = _exact_keys(request, ENVELOPE_FIELDS, "request")
    if root.get("protocol") != PROTOCOL_ID:
        raise AdmissionError("envelope_protocol")
    _text(root, "request_id", "request", SLUG)
    if root.get("mode") not in RUN_MODES:
        raise AdmissionError("envelope_mode")
    model = _exact_keys(root.get("model"), ENVELOPE_MODEL_FIELDS,
                        "request_model")
    _text(model, "formulation", "request_model", allowed=FORMULATIONS)
    _text(model, "sampler", "request_model", allowed=SAMPLERS)
    _int_field(model, "steps", "request_model", 1, 1024)
    _int_field(model, "seed", "request_model", 0, (1 << 63) - 1)
    input_row = _exact_keys(root.get("input"), ENVELOPE_INPUT_FIELDS,
                            "request_input")
    if input_row.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        raise AdmissionError("envelope_sample_rate_hz")
    if input_row.get("channels") != 1:
        raise AdmissionError("envelope_channels")
    if input_row.get("sample_count") != FRAME_SAMPLES:
        raise AdmissionError("envelope_sample_count")
    if input_row.get("dtype") != "f32":
        raise AdmissionError("envelope_dtype")
    byte_count = input_row.get("byte_count")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or \
            byte_count != FRAME_BYTES:
        raise AdmissionError("envelope_byte_count")
    payload = _payload_from_hex(input_row.get("payload_hex"))
    frame_from_bytes(payload)
    if input_row.get("sha256") != hashlib.sha256(payload).hexdigest():
        raise AdmissionError("envelope_sha256")
    options = _exact_keys(root.get("options"), ENVELOPE_OPTION_FIELDS,
                          "request_options")
    if options.get("network") != "denied":
        raise AdmissionError("envelope_network")
    if options.get("downloads") != "denied":
        raise AdmissionError("envelope_downloads")
    if options.get("writes") != "attempt_only":
        raise AdmissionError("envelope_writes")
    return payload


class SyntheticEnvelopeAdapter:
    """Protocol-envelope stand-in. Never imports or executes a runtime."""

    def __init__(self) -> None:
        self.closed = False
        self.call_count = 0

    def _ensure_open(self) -> None:
        if self.closed:
            raise AdmissionError("adapter_closed")

    def process(self, request: Any) -> dict:
        self._ensure_open()
        payload = validate_protocol_request(request)
        output_payload = bytes(bytearray(payload))
        self.call_count += 1
        return {
            "protocol": PROTOCOL_ID,
            "request_id": request["request_id"],
            "status": "ok",
            "call_index": self.call_count,
            "output": {
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "channels": 1,
                "sample_count": FRAME_SAMPLES,
                "dtype": "f32",
                "sha256": hashlib.sha256(output_payload).hexdigest(),
                "byte_count": len(output_payload),
                "payload_hex": output_payload.hex(),
            },
            "timing_measured": False,
            "runtime_invoked": False,
            "weights_loaded": False,
            "network_used": False,
        }

    def reset(self) -> None:
        self._ensure_open()
        self.call_count = 0

    def close(self) -> None:
        self.closed = True


def _envelope_case(case_id: str, mutate: Any) -> dict:
    request = copy.deepcopy(protocol_request())
    before = copy.deepcopy(request)
    mutate(request)
    adapter = SyntheticEnvelopeAdapter()
    try:
        adapter.process(request)
    except AdmissionError as error:
        return {
            "id": case_id,
            "status": "rejected",
            "code": error.code,
            "qualifies": False,
            "calls_after_rejection": adapter.call_count,
            "state_unchanged": adapter.call_count == 0 and request != before,
        }
    raise AssertionError("envelope case accepted: " + case_id)


def envelope_cases() -> list[dict]:
    def delete_option(row):
        del row["options"]["writes"]

    def network_allowed(row):
        row["options"]["network"] = "allowed"

    def downloads_allowed(row):
        row["options"]["downloads"] = "allowed"

    def writes_anywhere(row):
        row["options"]["writes"] = "anywhere"

    def protocol_wrong(row):
        row["protocol"] = "audioml-generative-run/2"

    def mode_streaming(row):
        row["mode"] = "streaming"

    def formulation_unknown(row):
        row["model"]["formulation"] = "gan"

    def sampler_unknown(row):
        row["model"]["sampler"] = "adaptive"

    def steps_zero(row):
        row["model"]["steps"] = 0

    def steps_too_many(row):
        row["model"]["steps"] = 1025

    def seed_negative(row):
        row["model"]["seed"] = -1

    def rate_wrong(row):
        row["input"]["sample_rate_hz"] = 8000

    def channels_wrong(row):
        row["input"]["channels"] = 2

    def dtype_wrong(row):
        row["input"]["dtype"] = "f64"

    def sha_wrong(row):
        row["input"]["sha256"] = "1" * 64

    def nonfinite(row):
        mutated = bytearray(frame_bytes(synthetic_frame()))
        mutated[0:4] = struct.pack("<f", float("nan"))
        mutated_bytes = bytes(mutated)
        row["input"]["payload_hex"] = mutated_bytes.hex()
        row["input"]["sha256"] = hashlib.sha256(mutated_bytes).hexdigest()

    def byte_count_wrong(row):
        row["input"]["byte_count"] = FRAME_BYTES - 4

    def extra_key(row):
        row["input"]["extra"] = 1

    def payload_invalid(row):
        row["input"]["payload_hex"] = "zz" * FRAME_BYTES

    def sample_count_wrong(row):
        row["input"]["sample_count"] = FRAME_SAMPLES + 1

    cases = (
        ("EV-01", delete_option),
        ("EV-02", network_allowed),
        ("EV-03", downloads_allowed),
        ("EV-04", writes_anywhere),
        ("EV-05", protocol_wrong),
        ("EV-06", mode_streaming),
        ("EV-07", formulation_unknown),
        ("EV-08", sampler_unknown),
        ("EV-09", steps_zero),
        ("EV-10", steps_too_many),
        ("EV-11", seed_negative),
        ("EV-12", rate_wrong),
        ("EV-13", channels_wrong),
        ("EV-14", dtype_wrong),
        ("EV-15", sha_wrong),
        ("EV-16", nonfinite),
        ("EV-17", byte_count_wrong),
        ("EV-18", extra_key),
        ("EV-19", payload_invalid),
        ("EV-20", sample_count_wrong),
    )
    return [_envelope_case(case_id, mutate) for case_id, mutate in cases]


def synthetic_envelope_probe() -> dict:
    """Execute the deterministic envelope only; no runtime or model."""
    request = protocol_request()
    payload = validate_protocol_request(copy.deepcopy(request))
    adapter = SyntheticEnvelopeAdapter()
    first = adapter.process(copy.deepcopy(request))
    second = adapter.process(copy.deepcopy(request))
    adapter.reset()
    replay = adapter.process(copy.deepcopy(request))
    adapter.close()
    adapter.close()
    lifecycle_rejected = False
    lifecycle_code = ""
    try:
        adapter.process(copy.deepcopy(request))
    except AdmissionError as error:
        lifecycle_rejected = True
        lifecycle_code = error.code
    first_payload = bytes.fromhex(first["output"]["payload_hex"])
    second_payload = bytes.fromhex(second["output"]["payload_hex"])
    replay_payload = bytes.fromhex(replay["output"]["payload_hex"])
    values = frame_from_bytes(first_payload)
    peak = max(abs(value) for value in values)
    cases = envelope_cases()
    return {
        "schema_id": ENVELOPE_SCHEMA_ID,
        "boundary": "synthetic_protocol_envelope_only_not_a_runtime_or_model",
        "request": request,
        "typical_api_use": {
            "status": "synthetic_pass",
            "calls": 3,
            "request_sha256": hashlib.sha256(payload).hexdigest(),
            "output_sha256": first["output"]["sha256"],
            "output_byte_count": first["output"]["byte_count"],
            "output_sample_count": first["output"]["sample_count"],
            "output_peak": _decimal_string(peak),
            "payload_prefix_hex": first_payload[:16].hex(),
            "identity_exact": first_payload == payload,
            "replay_identical": first_payload == second_payload,
            "reset_replay_identical": first_payload == replay_payload,
            "close_idempotent": True,
            "run_after_close_rejected": lifecycle_rejected,
            "timing_measured": False,
            "runtime_invoked": False,
            "weights_loaded": False,
            "model_executed": False,
            "audio_read": False,
            "network_used": False,
            "qualifies": False,
        },
        "lifecycle": {
            "id": "EV-LC-01",
            "status": "rejected" if lifecycle_rejected else "accepted",
            "code": lifecycle_code,
            "qualifies": False,
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
            "weights_loaded": False,
            "model_executed": False,
            "audio_read": False,
            "network_used": False,
        },
        "qualifies": False,
    }


# --------------------------------------------------------------------------
# Admission control and rejection matrix
# --------------------------------------------------------------------------
def control_manifest() -> dict:
    payload = frame_bytes(synthetic_frame())
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "run_id": "synthetic-run-0001",
        "model": {
            "upstream_repository": "https://example.invalid/cof-denoising",
            "upstream_revision": "1" * 40,
            "code_license": "synthetic_schema_control_only",
            "formulation": "flow",
            "training_corpus": "voicebank_demand",
            "stage": "pretrained",
            "sampler": "other_declared",
            "steps": 1,
            "seed": 0,
            "padding_profile": "synthetic_schema_control_no_padding_recipe",
        },
        "runtime": {
            "python": REQUIRED_INTERPRETER,
            "torch": "0.0.0-synthetic",
            "torchaudio": "0.0.0-synthetic",
            "device": "cpu",
            "dtype": "f32",
            "intra_op_threads": 1,
            "interop_op_threads": 1,
            "deterministic_algorithms": True,
            "offline": True,
            "install_reference": "synthetic-schema-control-no-install",
            "wheel_digests": {
                "torch": "1" * 64,
                "torchaudio": "2" * 64,
            },
        },
        "command": {
            "cli": PROTOCOL_ID,
            "request_argument": "/attempt/synthetic-run-0001/request.json",
            "result_argument": "/attempt/synthetic-run-0001/result.json",
            "network": "denied",
            "downloads": "denied",
        },
        "assets": [
            {
                "asset_id": "synthetic-asset-01",
                "name": "denoiser.safetensors",
                "byte_count": 1024,
                "sha256": "3" * 64,
                "terms_sha256": "4" * 64,
                "present_at_review": True,
            },
            {
                "asset_id": "synthetic-asset-02",
                "name": "config.json",
                "byte_count": 512,
                "sha256": "5" * 64,
                "terms_sha256": "6" * 64,
                "present_at_review": True,
            },
        ],
        "input": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_count": FRAME_SAMPLES,
            "dtype": "f32",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "finite": True,
            "peak": "0.78125",
        },
        "output": {
            "sample_count": FRAME_SAMPLES,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "finite": True,
            "peak": "0.78125",
            "delay_compensation_samples": 0,
        },
        "controls": [
            {"id": "control-candidate", "kind": "candidate"},
            {"id": "control-identity", "kind": "identity_passthrough"},
            {"id": "control-missing-runtime", "kind": "missing_runtime"},
            {"id": "control-noisy", "kind": "noisy_control"},
            {"id": "control-nonfinite", "kind": "nonfinite_rejection"},
        ],
        "rights": {
            "source_terms": "synthetic_schema_control_only",
            "runtime_terms": "synthetic_schema_control_only",
            "weight_terms": "synthetic_schema_control_only",
            "training_data_terms": "synthetic_schema_control_only",
            "input_terms": "synthetic_bytes_only_not_audio",
            "output_use": "synthetic_schema_control_only",
            "review_reference": "pending_task_local_schema_control",
            "claims_qualified": False,
        },
    }


def _manifest_case(case_id: str, group: str, mutate: Any) -> dict:
    manifest = control_manifest()
    before = copy.deepcopy(manifest)
    mutate(manifest)
    snapshot = copy.deepcopy(manifest)
    try:
        validate_manifest(manifest)
    except AdmissionError as error:
        return {
            "id": case_id,
            "group": group,
            "status": "rejected",
            "code": error.code,
            "qualifies": False,
            "state_unchanged": manifest == snapshot and manifest != before,
        }
    raise AssertionError("manifest case accepted: " + case_id)


def _normalise_parse_code(error: ValueError) -> str:
    raw = str(error).split(":", 1)[0]
    if raw.startswith("duplicate_json_key"):
        return "duplicate_json_key"
    if raw.startswith("nonfinite_json_constant"):
        return "nonfinite_json_constant"
    if raw == "json_root_not_object":
        return "json_root_not_object"
    if raw == "json_byte_order_mark":
        return "json_byte_order_mark"
    if raw == "Extra data":
        return "strict_json_trailing_data"
    return "strict_json_rejected"


def _parse_case(case_id: str, text: str) -> dict:
    try:
        loads_strict(text)
    except ValueError as error:
        return {
            "id": case_id,
            "group": "document",
            "status": "rejected",
            "code": _normalise_parse_code(error),
            "qualifies": False,
            "state_unchanged": True,
        }
    raise AssertionError("parse case accepted: " + case_id)


def admission_cases() -> list[dict]:
    parse_cases = (
        _parse_case("DOC-01", '{"a":1,"a":2}'),
        _parse_case("DOC-02", '{"a":NaN}'),
        _parse_case("DOC-03", '{"a":Infinity}'),
        _parse_case("DOC-04", '[]'),
        _parse_case("DOC-05", '{"a":1} trailing'),
        _parse_case("DOC-06", '\ufeff{"a":1}'),
    )

    def drop(key):
        def mutate(row):
            del row[key]
        return mutate

    def set_key(key, value):
        def mutate(row):
            row[key] = value
        return mutate

    def nested(section, key, value):
        def mutate(row):
            row[section][key] = value
        return mutate

    def drop_nested(section, key):
        def mutate(row):
            del row[section][key]
        return mutate

    def extra_nested(section, key, value):
        def mutate(row):
            row[section][key] = value
        return mutate

    def assets_mutate(fn):
        def mutate(row):
            fn(row["assets"])
        return mutate

    def asset_field(index, key, value):
        def mutate(row):
            row["assets"][index][key] = value
        return mutate

    def controls_empty(row):
        row["controls"] = []

    def controls_duplicate(row):
        row["controls"][1]["kind"] = row["controls"][0]["kind"]

    def controls_unknown(row):
        row["controls"][0]["kind"] = "runtime_candidate"

    def controls_extra(row):
        row["controls"][0]["extra"] = 1

    def controls_empty_id(row):
        row["controls"][0]["id"] = ""

    def output_peak_nan(row):
        row["output"]["peak"] = float("nan")

    def input_peak_inf(row):
        row["input"]["peak"] = float("inf")

    def too_many_assets(row):
        row["assets"] = [
            {
                "asset_id": "extra-%02d" % index,
                "name": "extra-%02d.bin" % index,
                "byte_count": 1,
                "sha256": "%064x" % (index + 1),
                "terms_sha256": "%064x" % (index + 100),
                "present_at_review": True,
            }
            for index in range(17)
        ]

    cases = parse_cases + (
        _manifest_case("ST-01", "structure", drop("runtime")),
        _manifest_case("ST-02", "structure", set_key("extra", 1)),
        _manifest_case("ST-03", "structure", lambda row: row.clear()),
        _manifest_case("ST-04", "structure", set_key("schema_id", "x")),
        _manifest_case("ST-05", "structure", set_key("run_id", "Bad Run")),
        _manifest_case("ST-06", "structure", set_key("run_id", 7)),
        _manifest_case("ST-07", "structure", set_key("model", [])),
        _manifest_case("ST-08", "structure", set_key("rights", "x")),
        _manifest_case("MD-01", "model", nested(
            "model", "upstream_repository", "github.com/cof")),
        _manifest_case("MD-02", "model", nested(
            "model", "upstream_revision", "abc")),
        _manifest_case("MD-03", "model", nested(
            "model", "upstream_revision", "A" * 40)),
        _manifest_case("MD-04", "model", nested("model", "code_license", "")),
        _manifest_case("MD-05", "model", nested(
            "model", "formulation", "gan")),
        _manifest_case("MD-06", "model", nested(
            "model", "training_corpus", "dns2020")),
        _manifest_case("MD-07", "model", nested("model", "stage", "fine_tuned")),
        _manifest_case("MD-08", "model", nested("model", "sampler", "adaptive")),
        _manifest_case("MD-09", "model", nested("model", "steps", 0)),
        _manifest_case("MD-10", "model", nested("model", "steps", 1025)),
        _manifest_case("MD-11", "model", nested("model", "steps", "1")),
        _manifest_case("MD-12", "model", nested("model", "seed", -1)),
        _manifest_case("MD-13", "model", nested(
            "model", "seed", (1 << 63))),
        _manifest_case("MD-14", "model", nested(
            "model", "padding_profile", "")),
        _manifest_case("MD-15", "model", extra_nested("model", "extra", 1)),
        _manifest_case("MD-16", "model", drop_nested(
            "model", "upstream_revision")),
        _manifest_case("RT-01", "runtime", nested("runtime", "python", "3.11")),
        _manifest_case("RT-02", "runtime", nested("runtime", "torch", "")),
        _manifest_case("RT-03", "runtime", nested(
            "runtime", "torchaudio", "main")),
        _manifest_case("RT-04", "runtime", nested("runtime", "device", "tpu")),
        _manifest_case("RT-05", "runtime", nested("runtime", "dtype", "i16")),
        _manifest_case("RT-06", "runtime", nested(
            "runtime", "intra_op_threads", 0)),
        _manifest_case("RT-07", "runtime", nested(
            "runtime", "interop_op_threads", 65)),
        _manifest_case("RT-08", "runtime", nested(
            "runtime", "deterministic_algorithms", False)),
        _manifest_case("RT-09", "runtime", nested("runtime", "offline", False)),
        _manifest_case("RT-10", "runtime", nested(
            "runtime", "install_reference", "")),
        _manifest_case("RT-11", "runtime", nested(
            "runtime", "wheel_digests", {})),
        _manifest_case("RT-12", "runtime", nested(
            "runtime", "wheel_digests", {"torch": "x"})),
        _manifest_case("RT-13", "runtime", extra_nested("runtime", "extra", 1)),
        _manifest_case("CM-01", "command", nested(
            "command", "cli", "audioml-generative-run/2")),
        _manifest_case("CM-02", "command", nested(
            "command", "request_argument", "/tmp/request.json")),
        _manifest_case("CM-03", "command", nested(
            "command", "result_argument", "/attempt/x/out.json")),
        _manifest_case("CM-04", "command", nested(
            "command", "network", "allowed")),
        _manifest_case("CM-05", "command", nested(
            "command", "downloads", "permitted")),
        _manifest_case("CM-06", "command", extra_nested("command", "extra", 1)),
        _manifest_case("AS-01", "assets", assets_mutate(
            lambda rows: rows.clear())),
        _manifest_case("AS-02", "assets", asset_field(
            1, "asset_id", "synthetic-asset-01")),
        _manifest_case("AS-03", "assets", asset_field(
            1, "name", "denoiser.safetensors")),
        _manifest_case("AS-04", "assets", asset_field(0, "byte_count", 0)),
        _manifest_case("AS-05", "assets", asset_field(0, "sha256", "1")),
        _manifest_case("AS-06", "assets", asset_field(
            0, "terms_sha256", "not-a-digest")),
        _manifest_case("AS-07", "assets", asset_field(
            0, "present_at_review", False)),
        _manifest_case("AS-08", "assets", too_many_assets),
        _manifest_case("AS-09", "assets", asset_field(0, "extra", 1)),
        _manifest_case("AS-10", "assets", asset_field(
            0, "name", "x" * 257)),
        _manifest_case("IN-01", "input", nested(
            "input", "sample_rate_hz", 8000)),
        _manifest_case("IN-02", "input", nested("input", "channels", 2)),
        _manifest_case("IN-03", "input", nested("input", "sample_count", 0)),
        _manifest_case("IN-04", "input", nested(
            "input", "sample_count", MAX_SAMPLE_COUNT + 1)),
        _manifest_case("IN-05", "input", nested("input", "dtype", "f64")),
        _manifest_case("IN-06", "input", nested("input", "sha256", "x")),
        _manifest_case("IN-07", "input", nested("input", "finite", False)),
        _manifest_case("IN-08", "input", nested("input", "peak", "1.5")),
        _manifest_case("IN-09", "input", extra_nested("input", "extra", 1)),
        _manifest_case("OUT-01", "output", nested(
            "output", "sample_count", FRAME_SAMPLES - 1)),
        _manifest_case("OUT-02", "output", nested("output", "sha256", "x")),
        _manifest_case("OUT-03", "output", nested("output", "finite", False)),
        _manifest_case("OUT-04", "output", nested("output", "peak", "-0.1")),
        _manifest_case("OUT-05", "output", nested(
            "output", "delay_compensation_samples", 1)),
        _manifest_case("OUT-06", "output", extra_nested("output", "extra", 1)),
        _manifest_case("OUT-07", "output", drop_nested("output", "peak")),
        _manifest_case("RI-01", "rights", nested(
            "rights", "claims_qualified", True)),
        _manifest_case("RI-02", "rights", nested("rights", "runtime_terms", "")),
        _manifest_case("RI-03", "rights", nested(
            "rights", "review_reference", "")),
        _manifest_case("RI-04", "rights", nested(
            "rights", "training_data_terms", "")),
        _manifest_case("RI-05", "rights", nested(
            "rights", "source_terms", "")),
        _manifest_case("RI-06", "rights", nested("rights", "output_use", "")),
        _manifest_case("RI-07", "rights", extra_nested("rights", "extra", 1)),
        _manifest_case("CT-01", "controls", controls_empty),
        _manifest_case("CT-02", "controls", controls_duplicate),
        _manifest_case("CT-03", "controls", controls_unknown),
        _manifest_case("CT-04", "controls", controls_extra),
        _manifest_case("CT-05", "controls", lambda row: row.update(
            controls=[])),
        _manifest_case("CT-06", "controls", controls_empty_id),
        _manifest_case("NF-01", "nonfinite", output_peak_nan),
        _manifest_case("NF-02", "nonfinite", input_peak_inf),
    )
    return list(cases)


def build_admission() -> dict:
    control = control_manifest()
    before = copy.deepcopy(control)
    validate_manifest(control)
    if control != before:
        raise RuntimeError("admission_control_mutated")
    cases = admission_cases()
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "boundary": "task_local_manifest_admission_only_not_a_runtime",
        "control": {
            "id": "ADM-ACCEPT-01",
            "accepted": True,
            "qualifies": False,
            "label": "synthetic_schema_control_not_evidence",
            "state_unchanged": True,
            "asset_records": len(control["assets"]),
            "control_records": len(control["controls"]),
            "manifest_sha256": object_digest(control),
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
            "weights_loaded": False,
            "model_executed": False,
            "audio_read": False,
            "network_used": False,
        },
    }


# --------------------------------------------------------------------------
# Contract and report
# --------------------------------------------------------------------------
def qualification() -> dict:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "not_qualified": True,
        "real_result_present": False,
        "source_present": False,
        "source_identity_recorded": False,
        "runtime_present": False,
        "runtime_pinned": False,
        "weights_present": False,
        "weights_identified": False,
        "input_media_present": False,
        "implementation_present": False,
        "reference_execution_result": False,
        "output_validity_result": False,
        "enhancement_profile_result": False,
        "device_timing_result": False,
        "listening_result": False,
        "benchmark_result": False,
        "release_claim": False,
        "missing_result_promoted": False,
        "all_release_gates_blocked": True,
    }


def build_contract() -> dict:
    row = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
    gates = [dict(gate, qualifies=False, linked_row=row)
             for gate in RELEASE_GATES]
    return {
        "schema_id": CONTRACT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification": qualification(),
        "qualification_status": "not_qualified",
        "disposition": DISPOSITION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "scope": {
            "write_scope": WRITE_SCOPE,
            "task_local_only": True,
            "provider_registered": False,
            "reference_implemented": False,
            "reference_executed": False,
            "public_abi_changed": False,
            "installed_v0_changed": False,
            "registry_or_default_changed": False,
            "shared_build_or_ci_changed": False,
            "real_assets_used": False,
            "network_used": False,
            "listening_performed": False,
            "device_timing_measured": False,
            "benchmark_run": False,
            "release_claim": False,
        },
        "boundary": {
            "linked_row_identity_only": True,
            "board_file_pinned": False,
            "mutable_board_fields_gate": False,
            "projected_fields": list(BOARD_ROW_FIELDS),
            "linked_row": row,
            "linked_row_sha256": board_row_digest(row),
            "linked_rows_sha256": linked_rows_digest(rows),
            "linked_rows": rows,
        },
        "public_v0_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "sample_format": "float32",
            "frame_samples": FRAME_SAMPLES,
            "unchanged": True,
        },
        "checkpoint_scope": copy.deepcopy(CHECKPOINT_SCOPE),
        "required_artifacts": [dict(item) for item in REQUIRED_ARTIFACTS],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "release_gates": gates,
        "enhancement_profile": {
            "profile": PROFILE,
            "profile_label": PROFILE_LABEL,
            "requirement_rows": [dict(item)
                                 for item in ENHANCEMENT_REQUIREMENTS],
            "conditions": [
                "active_speech",
                "quiet_speech",
                "idle_noise",
                "low_snr_speech",
                "onset_offset",
            ],
            "identity_noisy_control": "synthetic_envelope_only",
            "task_matched_baseline": "absent",
            "paired_si_sdr_stoi": "blocked_no_rights_cleared_clean_references",
            "clean_speech_preservation": "blocked_no_candidate_output",
            "peaks_and_invalid_outputs": "synthetic_envelope_only",
            "alignment_state_memory_timing":
                "blocked_no_exact_runtime",
            "unpaired_screen_or_listening": "blocked",
            "profile_satisfied": False,
            "real_results": 0,
        },
        "mode_platform_rows": [
            {
                "id": "MP-01",
                "mode": "offline",
                "platform": "not_measured",
                "status": "blocked",
                "evidence": (
                    "The census describes an offline generative family but "
                    "records no runtime, sampler, hardware or whole-clip "
                    "measurement; nothing was run."),
            },
            {
                "id": "MP-02",
                "mode": "streaming",
                "platform": "not_available",
                "status": "not_applicable",
                "evidence": (
                    "No streaming CoF formulation, checkpoint or runtime is "
                    "recorded; no streaming result is claimed."),
            },
            {
                "id": "MP-03",
                "mode": "offline",
                "platform": "target_device_and_mobile",
                "status": "blocked",
                "evidence": (
                    "No phone, GPU, NPU, callback, thermal, battery, energy or "
                    "target-device measurement exists."),
            },
        ],
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "model_fields": list(MODEL_FIELDS),
            "runtime_fields": list(RUNTIME_FIELDS),
            "command_fields": list(COMMAND_FIELDS),
            "asset_fields": list(ASSET_FIELDS),
            "input_fields": list(INPUT_FIELDS),
            "output_fields": list(OUTPUT_FIELDS),
            "control_fields": list(CONTROL_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "run_modes": list(RUN_MODES),
            "formulations": list(FORMULATIONS),
            "training_corpora": list(TRAINING_CORPORA),
            "stages": list(STAGES),
            "samplers": list(SAMPLERS),
            "exact_protocol": PROTOCOL_ID,
            "exact_interpreter": REQUIRED_INTERPRETER,
            "admission_only": True,
            "qualifies": False,
        },
        "non_claims": list(NON_CLAIMS),
        "required_results": list(REQUIRED_RESULTS),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "licensing": {
            "package_license": "Apache-2.0",
            "vendored_third_party_bytes": False,
            "upstream_source_present": False,
            "upstream_license_reviewed": False,
            "weight_terms_reviewed": False,
            "training_data_terms_reviewed": False,
            "input_terms_reviewed": False,
            "derived_output_terms_reviewed": False,
        },
    }


def build_report() -> dict:
    contract = build_contract()
    pins = {
        "source": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary": pin_rows(BOUNDARY_PINS, WORKTREE),
    }
    workspace_probes = absence_probes(AUDIO_ROOT)
    worktree_probes = worktree_absence_probes()
    home_probes = home_absence_probes()
    enhancement_rows = contract["enhancement_profile"]["requirement_rows"]
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "profile_label": PROFILE_LABEL,
        "mode": MODE,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "qualification": contract["qualification"],
        "disposition": DISPOSITION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "contract_sha256": object_digest(contract),
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "checkpoint_scope": contract["checkpoint_scope"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "enhancement_profile": dict(
            contract["enhancement_profile"],
            row_summary={
                "requirement_count": len(enhancement_rows),
                "documented_count": sum(
                    1 for row in enhancement_rows
                    if row["status"] == "documented"),
                "blocked_count": sum(1 for row in enhancement_rows
                                     if row["status"] == "blocked"),
                "synthetic_only_count": sum(
                    1 for row in enhancement_rows
                    if row["status"] == "synthetic_only"),
                "real_result_count": 0,
                "profile_satisfied": False,
            },
            profile_source_check=profile_row_check(),
        ),
        "mode_platform": {
            "rows": contract["mode_platform_rows"],
            "offline_mode_present": True,
            "streaming_mode_present": False,
            "modes_measured": [],
            "platforms_measured": [],
            "separate_mode_platform_measurement": "blocked",
            "device_timing_measured": False,
            "listening_performed": False,
        },
        "runtime_readiness": runtime_readiness(),
        "evidence_presence": evidence_presence(),
        "checkpoint_presence": checkpoint_presence(),
        "protocol_envelope": synthetic_envelope_probe(),
        "admission": build_admission(),
        "absence_evidence": {
            "workspace_probes": workspace_probes,
            "worktree_probes": worktree_probes,
            "home_probes": home_probes,
            "summary": absence_summary(workspace_probes, worktree_probes,
                                       home_probes),
        },
        "source_pins": pins["source"],
        "boundary_pins": pins["boundary"],
        "linked_row_identity": {
            "projection": board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW),
            "sha256": board_row_digest(
                board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)),
            "linked_rows": linked_rows(),
            "linked_rows_sha256": linked_rows_digest(),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
        },
        "non_claims": contract["non_claims"],
        "required_results": contract["required_results"],
        "reopening_conditions": contract["reopening_conditions"],
        "reproduction": {
            "regeneration": "run.py all (repeat=3, byte-identical)",
            "tests": "python3 -m unittest -v test_reference.py",
            "verifier": "python3 verify.py",
            "stdlib_only": True,
            "network_used": False,
        },
    }


def canonical_report(document: dict) -> tuple[str, str]:
    text = canonical_text(document)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_ID:
        raise ValueError("contract_schema")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != "incomplete":
        raise ValueError("contract_status")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal_only")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification")
    gates = contract.get("release_gates", [])
    if len(gates) != 8:
        raise ValueError("contract_gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != "RG-%02d" % index:
            raise ValueError("contract_gate_id")
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            raise ValueError("contract_gate_not_blocked")
        if not gate.get("reopen_condition"):
            raise ValueError("contract_gate_reopen")
    artifacts = contract.get("required_artifacts", [])
    if len(artifacts) != len(REQUIRED_ARTIFACTS):
        raise ValueError("contract_artifact_count")
    if sum(1 for row in artifacts if row.get("present")) != 1:
        raise ValueError("contract_artifact_presence")
    for row in artifacts[1:]:
        if row.get("present") is not False or row.get("blocked") is not True:
            raise ValueError("contract_artifact_not_blocked")
    blockers = contract.get("exact_blockers", [])
    if len(blockers) != len(EXACT_BLOCKERS):
        raise ValueError("contract_blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            raise ValueError("contract_blocker_not_open")
    rows = contract.get("enhancement_profile", {}).get("requirement_rows", [])
    if len(rows) != len(ENHANCEMENT_REQUIREMENTS):
        raise ValueError("contract_enhancement_count")
    if any(row.get("status") not in ("blocked", "documented", "synthetic_only")
           for row in rows):
        raise ValueError("contract_enhancement_status")
    flags = contract.get("qualification", {})
    if flags.get("not_qualified") is not True \
            or flags.get("all_release_gates_blocked") is not True \
            or flags.get("missing_result_promoted") is not False \
            or flags.get("release_claim") is not False \
            or flags.get("source_present") is not False \
            or flags.get("runtime_present") is not False \
            or flags.get("weights_present") is not False:
        raise ValueError("contract_qualification_flags")
    scope = contract.get("scope", {})
    for key in ("provider_registered", "reference_implemented",
                "reference_executed", "public_abi_changed",
                "installed_v0_changed", "registry_or_default_changed",
                "shared_build_or_ci_changed", "real_assets_used",
                "network_used", "listening_performed",
                "device_timing_measured", "benchmark_run", "release_claim"):
        if scope.get(key) is not False:
            raise ValueError("contract_scope_flag:" + key)
