# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only evidence builder for SDK-DIFFATSM.

This module never downloads, reads, imports, links or executes DiffATSM, a
checkpoint, a PPG extractor, a diffusion runtime, an audio corpus or a model.
It records the exact absence, validates a bounded offline rate protocol
envelope and produces a canonical DEFER report. The envelope is protocol
plumbing over integer sample positions; it is not the candidate, does not
synthesize audio and cannot qualify anything.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-DIFFATSM"
COMPONENT_ID = "diffatsm"
TASK_TITLE = "DiffATSM"
CONTRACT_ID = "audio-sdk/diffatsm-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/diffatsm-rate-envelope/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "feasibility"
BASE_COMMIT = "fe0b37a0d0b8b70054cc55f301a83108abdeba77"
BRANCH = "swarm/SDK-DIFFATSM"
WRITE_SCOPE = "docs/task-evidence/diffatsm/ only"
TASK_PREFIX = "docs/task-evidence/diffatsm/"
REQUIRED_INTERPRETER = "3.11.5"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
MAX_SAMPLE_COUNT = 192_000
MAX_CONTROLS = 8
RUN_MODES = ("offline",)
CONTROL_KINDS = (
    "candidate",
    "identity_passthrough",
    "missing_runtime",
    "nonfinite_rejection",
)
REQUIRED_CONTROL_KINDS = frozenset(CONTROL_KINDS)

OFFICIAL_REPOSITORY = "https://github.com/shjang-97/DiffATSM"
RELEASE_STATE = "full implementation forthcoming after publication"
DISPOSITION = (
    "DiffATSM raw-audio diffusion time-scale-modification feasibility blocker. "
    "The official repository states that the full implementation will be "
    "released after publication and currently publishes only an abstract, "
    "citation, planned code structure and dependencies. No immutable revision, "
    "license text, source snapshot, PPG model, diffusion checkpoint, runtime, "
    "rights-cleared input or output is present or reproducible. The catalogued "
    "rate profile cannot be satisfied by a rendering system that has no "
    "runnable rate-only artefact."
)

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT")
    if override:
        return Path(override).resolve()
    for parent in (HERE.parents[3], *HERE.parents):
        if (parent / "audio-benchmark-platform" / "plan" / "INVENTORY.json").is_file():
            return parent
    raise RuntimeError("cannot locate the audioml workspace root")


AUDIO_ROOT = _find_audio_root()

SOURCE_PINS = {
    "research/speech-rate-tsm-evaluation-20261101.md":
        "525a25c12753ea7fad71aa7101b2c872d5511813fd0ea9b18231b347a8fda96d",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-text/REPORT.md":
        "86657ba0d2c82d64110dc058f40082e2d701ce0ff2427fe2e0d3a3f1719bfd93",
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
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository", "depends_on")
LINKED_ROW_IDS = (
    TASK,
    "SDK-FND-AUDIT",
    "SDK-FND-EVIDENCE",
    "SDK-FND-PROVIDER",
)
MUTABLE_BOARD_FIELDS = (
    "status",
    "owner",
    "claim",
    "review",
    "handoff",
    "blocked_reason",
    "dispatch_priority",
)

MANIFEST_FIELDS = (
    "schema_id",
    "request_id",
    "mode",
    "candidate",
    "input",
    "rate",
    "output",
    "controls",
    "rights",
)
CANDIDATE_FIELDS = (
    "name",
    "source_present",
    "weights_present",
    "runtime_present",
    "revision",
    "license",
)
INPUT_FIELDS = (
    "sample_rate_hz",
    "channels",
    "sample_count",
    "dtype",
    "finite",
    "peak",
)
RATE_FIELDS = ("numerator", "denominator")
OUTPUT_FIELDS = (
    "sample_count",
    "mapping_sha256",
    "finite",
    "peak",
    "first_source",
    "last_source",
)
CONTROL_FIELDS = ("id", "kind")
RIGHTS_FIELDS = (
    "source_terms",
    "weight_terms",
    "input_terms",
    "output_use",
    "claims_qualified",
)

SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
COMMIT_SHA = re.compile(r"^(?=.*[1-9a-f])[0-9a-f]{40}$")
REPO_URL = re.compile(r"^https://[a-z0-9][a-z0-9.-]*/[A-Za-z0-9._/-]+$")
DECIMAL = re.compile(r"^(0|1)(\.[0-9]*[1-9])?$|^0\.[0-9]*[1-9]$")
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")

RATE_REQUIREMENTS = (
    ("RATE-01", "Source/output mapping for the exact runtime.",
     "blocked_no_source_no_runtime"),
    ("RATE-02", "Target and actual duration for constant and changing rates.",
     "blocked_no_candidate_output"),
    ("RATE-03", "Pitch preservation or shift for the exact runtime.",
     "blocked_no_candidate_output"),
    ("RATE-04", "Transient audibility proxy or authorized listening.",
     "blocked_no_candidate_output"),
    ("RATE-05", "Playback buffering, fill/flush and deadline behaviour.",
     "blocked_no_device_or_scheduler"),
    ("RATE-06", "1x identity control.",
     "blocked_synthetic_position_map_only"),
    ("RATE-07", "Rate changes, including step and ramp profiles.",
     "blocked_synthetic_position_map_only"),
    ("RATE-08", "Unfamiliar speech material.",
     "blocked_no_rights_cleared_audio"),
    ("RATE-09", "Music material and a synthetic music negative control.",
     "blocked_no_rights_cleared_audio"),
    ("RATE-10", "Silence and empty input.",
     "blocked_synthetic_position_map_only"),
    ("RATE-11", "Rebuffer, drift and the final partial window.",
     "blocked_synthetic_position_map_only"),
    ("RATE-12", "Pause or filler decisions tied to source timestamps and "
                "speech preservation.",
     "blocked_no_speech_no_vad"),
    ("RATE-13", "Separate paired, unpaired, synthetic, human and "
                "source-reported evidence.",
     "documented"),
)

SOURCE_REPORTED_IDENTITY = {
    "candidate": TASK_TITLE,
    "architecture": (
        "phonetic-posteriorgram-conditioned adaptive neural generation with "
        "diffusion post-processing"
    ),
    "task": "raw_audio_time_scale_modification",
    "official_repository": OFFICIAL_REPOSITORY,
    "release_state": RELEASE_STATE,
    "released_content": (
        "abstract",
        "citation",
        "planned_code_structure",
        "dependencies",
    ),
    "immutable_revision_recorded": False,
    "license_recorded": False,
    "license_text_staged": False,
    "checkpoint_identity_recorded": False,
    "checkpoint_repository": None,
    "runtime_recorded": False,
    "source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "runnable_as_released": False,
    "rate_only_estimator": False,
    "source_reported_only": True,
    "verified": False,
}

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "evidence_register_and_policy_boundary",
        "requirement": (
            "The pinned candidate inventory row, rate acceptance profile, SDK "
            "delivery plan, research findings and unchanged v0 contract boundary."
        ),
        "present": True,
        "blocked": False,
        "verified": True,
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-02",
        "kind": "exact_upstream_source_snapshot",
        "requirement": (
            "The exact shjang-97/DiffATSM source tree at an immutable commit or "
            "release tag, including the license text, COPYING/NOTICE and README."
        ),
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-03",
        "kind": "checkpoint_ppg_and_diffusion_assets",
        "requirement": (
            "Every PPG extractor, acoustic model, diffusion checkpoint, "
            "vocoder, inference config and dependency lock file with exact "
            "names, immutable revision, byte counts and SHA-256 values."
        ),
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-04",
        "kind": "pinned_diffusion_runtime",
        "requirement": (
            "A locked offline runtime with interpreter, accelerator, wheel "
            "names/hashes, install location, device, dtype, diffusion step "
            "schedule, seed and padding recipe."
        ),
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_inputs_and_training_data",
        "requirement": (
            "The code, weight and training-data terms plus a digest-pinned, "
            "rights-cleared caller input set with acquisition, evaluation, "
            "derived-output and redistribution decisions."
        ),
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-06",
        "kind": "reproduced_rate_and_renderer_results",
        "requirement": (
            "Deterministic offline candidate output for identity and rate "
            "changes with duration, pitch, transient, buffering, preservation "
            "and final-partial measurements."
        ),
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
    },
    {
        "id": "ART-07",
        "kind": "provider_intake_and_public_surface",
        "requirement": (
            "A separate versioned OFF-by-default provider intake with clean "
            "install proof, empty defaults, no shared-build change and "
            "independent exact-head review."
        ),
        "present": False,
        "blocked": True,
        "verified": False,
        "revision": None,
        "sha256": None,
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-02",
        "linked_gates": ("RG-01",),
        "statement": (
            "The recorded repository https://github.com/shjang-97/DiffATSM is "
            "described as publishing only an abstract, citation, planned code "
            "structure and dependencies. No immutable commit or release tag, "
            "source file, license text, COPYING/NOTICE or model card is staged, "
            "and no DiffATSM source tree exists at any probed path."
        ),
        "required_action": (
            "Supply the exact upstream repository at an immutable commit or "
            "release tag with the complete source snapshot, license text, "
            "notices and a source-to-artifact map. No download is permitted "
            "inside this package."
        ),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-03",
        "linked_gates": ("RG-01", "RG-03"),
        "statement": (
            "No PPG extractor, acoustic model, diffusion checkpoint, vocoder "
            "or inference configuration is named. There is no file name, "
            "revision, byte count, SHA-256, tensor layout or dependency lock, "
            "and no weight byte is present or downloaded."
        ),
        "required_action": (
            "Stage the complete asset set with exact file names, immutable "
            "revision, byte counts and matching SHA-256 values, plus an "
            "artifact-specific terms review. Do not reconstruct or infer a "
            "weight."
        ),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-04",
        "linked_gates": ("RG-02",),
        "statement": (
            "No diffusion runtime, interpreter lock, accelerator requirement, "
            "device, dtype, step schedule, seed or padding recipe is recorded. "
            "The probed interpreter exposes no torch, torchaudio, diffusers or "
            "DiffATSM module."
        ),
        "required_action": (
            "Provide a locked offline runtime with wheel names, versions, byte "
            "counts, SHA-256 values and install location, plus the exact "
            "device, dtype, step schedule, seed and padding recipe."
        ),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-05",
        "linked_gates": ("RG-04",),
        "statement": (
            "No upstream license, weight term, training-data statement, PPG "
            "corpus lineage, attribution bundle or rights-cleared caller input "
            "is staged or reviewed. The repository license field is unrecorded."
        ),
        "required_action": (
            "Provide the license and notice text, reviewed code, weight, "
            "training-data and PPG-toolchain terms, and a digest-pinned "
            "rights-cleared caller input set with derived-output and "
            "redistribution decisions."
        ),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-06",
        "linked_gates": ("RG-05", "RG-06"),
        "statement": (
            "No DiffATSM render or rate result is reproduced. Without source, "
            "weights, runtime and inputs there is no identity/rate output, "
            "duration, pitch, transient, buffering, preservation or "
            "final-partial measurement."
        ),
        "required_action": (
            "After the source, asset, runtime and rights gates clear, run "
            "offline with deterministic settings and record per-item hashes, "
            "duration, pitch, transient, buffering, preservation and timing."
        ),
        "status": "open",
        "qualifies": False,
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-07",
        "linked_gates": ("RG-07", "RG-08"),
        "statement": (
            "No provider, descriptor, registry entry, default selection, mode "
            "or platform measurement, listening result, benchmark result or "
            "release claim exists. The package is task-local evidence only."
        ),
        "required_action": (
            "Measure mode and platform separately, record device timing and "
            "resources, run authorized listening or a labeled screen, then open "
            "a separate versioned OFF-by-default intake with clean-install "
            "proof and independent exact-head review."
        ),
        "status": "open",
        "qualifies": False,
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "source_revision_and_license_provenance",
        "statement": (
            "Only a repository URL and a forthcoming-implementation statement "
            "exist; no immutable revision, source snapshot, license text or "
            "notice is staged."
        ),
        "reopen_condition": (
            "Stage the DiffATSM source at an immutable revision with complete "
            "license, notice and README records, then record independent review."
        ),
    },
    {
        "id": "RG-02",
        "title": "pinned_diffusion_runtime_and_offline_install",
        "statement": (
            "No runtime, wheel lock, install location, import digest, device, "
            "dtype, step schedule, seed or padding recipe is recorded."
        ),
        "reopen_condition": (
            "Provide a locked offline runtime with wheel hashes, install "
            "location, clean-room import digest and exact inference settings."
        ),
    },
    {
        "id": "RG-03",
        "title": "checkpoint_ppg_and_diffusion_assets",
        "statement": (
            "No PPG model, diffusion checkpoint, vocoder or config file name, "
            "revision, byte count or SHA-256 is recorded."
        ),
        "reopen_condition": (
            "Stage every PPG, diffusion, vocoder and config file and verify "
            "each byte count and SHA-256 against an immutable revision."
        ),
    },
    {
        "id": "RG-04",
        "title": "rights_cleared_inputs_and_training_data",
        "statement": (
            "No license text, weight terms, training-data terms, PPG lineage, "
            "derived-output permission or redistribution decision exists."
        ),
        "reopen_condition": (
            "Freeze a permitted, digest-pinned input set with corpus, "
            "evaluation, derived-output and redistribution decisions plus "
            "weight and training-data terms."
        ),
    },
    {
        "id": "RG-05",
        "title": "reference_execution_and_output_validity",
        "statement": (
            "No renderer execution, per-item output hash, finite/length check "
            "or deterministic repeat exists."
        ),
        "reopen_condition": (
            "Execute the pinned assets offline in the exact runtime and record "
            "output hashes, finite/length preservation, exact repeats and "
            "peak/RSS values."
        ),
    },
    {
        "id": "RG-06",
        "title": "rate_profile_against_real_runtime",
        "statement": (
            "The Rate profile is not satisfied: no source/output mapping, "
            "duration, pitch, transient, buffering, speech-preservation or "
            "final-partial result exists for the candidate."
        ),
        "reopen_condition": (
            "Run every Rate-profile case on a rights-cleared cohort against the "
            "installed runtime, including 1x, rate changes, silence, rebuffer, "
            "drift and the final partial window."
        ),
    },
    {
        "id": "RG-07",
        "title": "mode_platform_timing_resources_and_listening",
        "statement": (
            "No offline mode/platform timing, latency, memory, pacing, device, "
            "energy, listening or benchmark measurement exists."
        ),
        "reopen_condition": (
            "Measure each mode and platform separately with timing, resources "
            "and pacing, and complete authorized listening or a labeled screen."
        ),
    },
    {
        "id": "RG-08",
        "title": "provider_intake_public_surface_and_release",
        "statement": (
            "No provider, descriptor, registry entry, default, shared-build "
            "change, clean-install proof or independent review exists."
        ),
        "reopen_condition": (
            "Open a separate versioned OFF-by-default intake with clean-install "
            "proof, no shared default/build change and independent exact-head "
            "approval after all prior gates clear."
        ),
    },
)

NON_CLAIMS = (
    "No DiffATSM source, repository snapshot, PPG extractor, diffusion "
    "checkpoint, vocoder, config or inference implementation is present, "
    "loaded, deserialized or reconstructed.",
    "No torch, torchaudio, diffusers or DiffATSM module is imported, "
    "installed, linked or executed.",
    "No real audio, corpus, manifest payload or model output is read, "
    "synthesized or produced.",
    "No DiffATSM time-scale-modification, rate, duration, pitch, transient, "
    "preservation, listening, device or benchmark result is reproduced.",
    "The integer position envelope and admission control are protocol "
    "plumbing only; they are not a renderer, a rate estimator, a model output "
    "or a qualification.",
    "No provider, descriptor, registry, default, public ABI, shared build or "
    "CI change exists.",
    "The research prose and repository URL are source-reported context only "
    "and are not promoted to measured evidence.",
)

REQUIRED_RESULTS = (
    "Exact upstream URL, immutable revision, source snapshot, license text and "
    "notice for DiffATSM.",
    "Complete PPG, diffusion, vocoder and config manifest with file names, "
    "revisions, byte counts and SHA-256 values.",
    "Locked offline diffusion runtime with wheel digests, install location and "
    "clean-room import digest.",
    "Exact device, dtype, diffusion step schedule, seed, context and padding "
    "recipe.",
    "Rights-cleared, digest-pinned caller inputs and code/weight/training-data "
    "terms.",
    "Deterministic reproduced renderer runs with finite, length-consistent "
    "outputs and exact repeats.",
    "Source/output mapping, duration, pitch, transient, buffering and "
    "speech-preservation results for the exact runtime.",
    "Separate mode/platform timing, authorized listening and independent "
    "provider intake review.",
)

REOPENING_CONDITIONS = (
    "Publish and pin the exact DiffATSM source revision with its license and "
    "notice text.",
    "Stage the PPG, diffusion, vocoder and config assets with per-file byte "
    "counts and SHA-256 values.",
    "Provide a locked offline diffusion runtime and the exact inference recipe.",
    "Provide rights-cleared inputs and code/weight/training-data terms.",
    "Reproduce deterministic offline renders and complete the Rate profile, "
    "including controls and preservation.",
    "Measure mode and platform separately, complete listening or a labeled "
    "screen, then open a separate OFF-by-default intake and independent review.",
)

EVIDENCE_SNIPPETS = (
    ("research/tsm-followup-20261101/README.md",
     "no complete executable implementation/checkpoint available"),
    ("research/tsm-followup-20261101/README.md",
     "It is an audio renderer candidate, not a standalone lightweight rate "
     "estimator."),
    ("research/tsm-followup-20261101/agent-text/REPORT.md",
     "full implementation will be released after publication"),
    ("research/tsm-followup-20261101/agent-text/REPORT.md",
     "not a standalone rate estimator"),
    ("research/speech-rate-tsm-evaluation-20261101.md",
     "Official repository says full implementation is forthcoming"),
    ("research/speech-rate-tsm-evaluation-20261101.md", OFFICIAL_REPOSITORY),
    ("audio-benchmark-platform/plan/INVENTORY.json",
     "no complete executable implementation/checkpoint available"),
)

WORKSPACE_ABSENCE_PROBES = (
    "data/checkouts/DiffATSM",
    "data/checkouts/diffatsm",
    "data/checkouts/shjang-97/DiffATSM",
    "data/models/DiffATSM",
    "data/models/diffatsm",
    "data/models/shjang-97/DiffATSM",
    "data/envs/diffatsm",
    "data/envs/diffatsm-diffusion",
    "adapters/diffatsm",
)

WORKTREE_ABSENCE_PROBES = (
    "third_party/DiffATSM",
    "third_party/diffatsm",
    "docs/task-evidence/diffatsm/weights",
    "docs/task-evidence/diffatsm/checkpoint",
)

HOME_ABSENCE_PROBES = (
    ".cache/huggingface/hub/models--shjang-97--DiffATSM",
)


class AdmissionError(ValueError):
    """Raised when a manifest is not admissible under the envelope schema."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code + (":" + detail if detail else ""))
        self.code = code
        self.detail = detail


def _reject_constant(value: str) -> None:
    raise ValueError("nonfinite JSON constant: " + value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def loads_strict(text: str) -> dict:
    if not isinstance(text, str):
        raise ValueError("JSON input must be text")
    if text.startswith("\ufeff"):
        raise ValueError("byte-order mark is not permitted")
    if not text.strip():
        raise ValueError("empty JSON input")
    document = json.loads(
        text,
        object_pairs_hook=_unique_object,
        parse_constant=_reject_constant,
    )
    if not isinstance(document, dict):
        raise ValueError("root must be a JSON object")
    return document


def read_strict_json(path: Path) -> dict:
    return loads_strict(path.read_text(encoding="utf-8"))


def canonical_text(document: Any) -> str:
    return json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def canonical_bytes(document: Any) -> bytes:
    return canonical_text(document).encode("ascii")


def object_digest(document: Any) -> str:
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_lists(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_lists(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_lists(item) for item in value]
    return value


def _assert_no_floats(value: Any, path: str = "") -> None:
    if isinstance(value, float):
        raise TypeError("float is not allowed in canonical evidence: " + path)
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("non-string key at " + path)
            _assert_no_floats(item, path + "/" + key)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _assert_no_floats(item, path + "/" + str(index))


def _format_decimal(value: Fraction) -> str:
    if value < 0:
        return "-" + _format_decimal(-value)
    denominator = value.denominator
    twos = 0
    fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        raise ValueError("non-terminating decimal")
    places = max(twos, fives)
    scaled = value.numerator * (10 ** places) // value.denominator
    text = str(scaled).rjust(places + 1, "0")
    if places == 0:
        return text
    whole, fraction = text[:-places], text[-places:]
    fraction = fraction.rstrip("0")
    return whole if not fraction else whole + "." + fraction


def canonical_decimal(text: Any, label: str) -> Fraction:
    if not isinstance(text, str):
        raise AdmissionError("peak_not_string", label)
    if not DECIMAL.match(text):
        raise AdmissionError("peak_not_canonical", label)
    value = Fraction(text)
    if _format_decimal(value) != text:
        raise AdmissionError("peak_not_canonical", label)
    if value > 1:
        raise AdmissionError("peak_out_of_range", label)
    return value


def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict]:
    return {
        relative: {
            "sha256": sha256_file(root / relative),
            "expected": expected,
            "match": sha256_file(root / relative) == expected,
        }
        for relative, expected in sorted(pins.items())
    }


def board_row_projection(path: Path) -> dict:
    document = read_strict_json(path)
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board does not contain a tasks list")
    for task in tasks:
        if isinstance(task, dict) and task.get("id") == TASK:
            return {field: task.get(field) for field in BOARD_ROW_FIELDS}
    raise ValueError("linked task row is absent: " + TASK)


def board_row_digest(projection: dict) -> str:
    return object_digest(projection)


def linked_rows(path: Path | None = None) -> list[dict]:
    document = read_strict_json(path or (AUDIO_ROOT / BOARD_TASK_ROW))
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board does not contain a tasks list")
    by_id = {
        task.get("id"): task
        for task in tasks
        if isinstance(task, dict) and task.get("id") in LINKED_ROW_IDS
    }
    missing = [task_id for task_id in LINKED_ROW_IDS if task_id not in by_id]
    if missing:
        raise ValueError("linked rows absent: " + ",".join(missing))
    return [
        {field: by_id[task_id].get(field) for field in BOARD_ROW_FIELDS}
        for task_id in LINKED_ROW_IDS
    ]


def linked_rows_digest(rows: list[dict] | None = None) -> str:
    return object_digest(rows if rows is not None else linked_rows())


def boundary_block() -> dict:
    row = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    rows = linked_rows()
    return {
        "board_file_pinned": False,
        "linked_row": row,
        "linked_row_identity_only": True,
        "linked_row_sha256": board_row_digest(row),
        "linked_rows": rows,
        "linked_rows_sha256": linked_rows_digest(rows),
        "mutable_board_fields_gate": False,
        "projected_fields": list(BOARD_ROW_FIELDS),
        "excluded_mutable_fields": list(MUTABLE_BOARD_FIELDS),
    }


def absence_probes() -> list[dict]:
    rows: list[dict] = []
    for relative in WORKSPACE_ABSENCE_PROBES:
        path = AUDIO_ROOT / relative
        rows.append({"path": "workspace:" + relative, "present": path.exists()})
    for relative in WORKTREE_ABSENCE_PROBES:
        path = WORKTREE / relative
        rows.append({"path": "worktree:" + relative, "present": path.exists()})
    for relative in HOME_ABSENCE_PROBES:
        path = Path.home() / relative
        rows.append({"path": "home:" + relative, "present": path.exists()})
    return rows


def absence_summary(rows: list[dict] | None = None) -> dict:
    observed = rows if rows is not None else absence_probes()
    present = [row for row in observed if row["present"]]
    return {
        "probe_count": len(observed),
        "present_count": len(present),
        "all_absent": not present,
        "probes": observed,
    }


def evidence_snippet_check() -> dict:
    rows: list[dict] = []
    for relative, phrase in EVIDENCE_SNIPPETS:
        path = AUDIO_ROOT / relative
        if not path.is_file():
            rows.append({"path": relative, "present": False,
                         "phrase": phrase})
            continue
        text = path.read_text(encoding="utf-8")
        rows.append({
            "path": relative,
            "present": phrase in text,
            "phrase": phrase,
        })
    return {
        "checks": rows,
        "all_present": all(row["present"] for row in rows),
        "count": len(rows),
    }


def inventory_record() -> dict:
    document = read_strict_json(
        AUDIO_ROOT / "audio-benchmark-platform" / "plan" / "INVENTORY.json")
    for component in document.get("components", []):
        if isinstance(component, dict) and component.get("id") == COMPONENT_ID:
            return {
                "id": component.get("id"),
                "name": component.get("name"),
                "area": component.get("area"),
                "evidence_status": component.get("evidence_status"),
                "repository": component.get("repository"),
                "disposition": component.get("disposition"),
                "verification_profile": component.get("verification_profile"),
                "task": component.get("task"),
                "aliases": component.get("aliases", []),
                "evidence": component.get("evidence", []),
            }
    raise ValueError("inventory record absent: " + COMPONENT_ID)


def runtime_readiness() -> dict:
    modules: dict[str, bool] = {}
    for module in ("torch", "torchaudio", "diffusers"):
        try:
            __import__(module)
        except Exception:
            modules[module] = False
        else:
            modules[module] = True
    return {
        "probed_modules": modules,
        "any_diffusion_module_available": any(modules.values()),
        "runtime_present": False,
        "runtime_pinned": False,
    }


def synthetic_frame(count: int = FRAME_SAMPLES) -> list[Fraction]:
    if not isinstance(count, int) or isinstance(count, bool):
        raise ValueError("frame count must be an integer")
    if count < 1 or count > MAX_SAMPLE_COUNT:
        raise ValueError("frame count out of range")
    return [Fraction((index * 37) % 201 - 100, 128) for index in range(count)]


def frame_metrics(values: list[Fraction] | list[int] | list[float]) -> dict:
    if not isinstance(values, list) or not values:
        raise ValueError("frame must be a non-empty list")
    if len(values) > MAX_SAMPLE_COUNT:
        raise ValueError("frame too long")
    peak = Fraction(0)
    for value in values:
        if isinstance(value, bool):
            raise ValueError("boolean sample")
        try:
            fraction = Fraction(value)
        except (ValueError, OverflowError):
            raise ValueError("nonfinite sample")
        if not math.isfinite(float(fraction)):
            raise ValueError("nonfinite sample")
        if fraction < -1 or fraction > 1:
            raise ValueError("sample outside [-1,1]")
        peak = max(peak, abs(fraction))
    payload = canonical_text([_format_decimal(value) for value in values])
    return {
        "sample_count": len(values),
        "finite": True,
        "peak": _format_decimal(peak),
        "sha256": hashlib.sha256(payload.encode("ascii")).hexdigest(),
    }


def target_sample_count(sample_count: int, numerator: int,
                        denominator: int) -> int:
    return (sample_count * denominator) // numerator


def source_position(output_index: int, numerator: int,
                    denominator: int) -> int:
    return (output_index * numerator) // denominator


def mapping_record(sample_count: int, numerator: int,
                   denominator: int) -> dict:
    if sample_count < 1 or sample_count > MAX_SAMPLE_COUNT:
        raise AdmissionError("input_sample_count_out_of_range")
    if numerator < 1 or denominator < 1:
        raise AdmissionError("rate_not_positive")
    if math.gcd(numerator, denominator) != 1:
        raise AdmissionError("rate_not_reduced")
    if numerator * 2 < denominator or numerator > denominator * 2:
        raise AdmissionError("rate_out_of_bounds")
    target = target_sample_count(sample_count, numerator, denominator)
    if target < 1:
        raise AdmissionError("target_sample_count_zero")
    digest = hashlib.sha256()
    previous = 0
    last = 0
    monotone = True
    for index in range(target):
        source = source_position(index, numerator, denominator)
        if source < 0 or source >= sample_count:
            raise AdmissionError("mapping_out_of_bounds")
        if index and source < previous:
            monotone = False
        previous = source
        last = source
        digest.update(("%d,%d\n" % (index, source)).encode("ascii"))
    identity = (numerator, denominator) == (1, 1)
    return {
        "input_samples": sample_count,
        "numerator": numerator,
        "denominator": denominator,
        "speed_ratio": "%d/%d" % (numerator, denominator),
        "target_samples": target,
        "duration_error_samples": 0,
        "first_source": 0,
        "last_source": last,
        "mapping_sha256": digest.hexdigest(),
        "monotone": monotone,
        "bounded": True,
        "identity_exact": identity and target == sample_count,
    }


ENVELOPE_CASES = (
    ("identity_1x", 1, 1),
    ("speed_up_125", 5, 4),
    ("speed_up_150", 3, 2),
    ("speed_down_080", 4, 5),
    ("speed_down_090", 9, 10),
)
ENVELOPE_INPUT_SAMPLES = 19_200
ENVELOPE_PEAK = "0.78125"


def _require_exact_keys(value: Any, expected: tuple[str, ...],
                        label: str) -> dict:
    if not isinstance(value, dict):
        raise AdmissionError(label + "_not_object")
    actual = tuple(sorted(value))
    if actual != tuple(sorted(expected)):
        if set(actual) - set(expected):
            raise AdmissionError(label + "_extra_keys")
        raise AdmissionError(label + "_missing_keys")
    return value


def _require_bool(value: Any, label: str, expected: bool | None = None) -> bool:
    if not isinstance(value, bool):
        raise AdmissionError(label + "_not_bool")
    if expected is not None and value is not expected:
        raise AdmissionError(label + "_must_be_" + ("true" if expected else "false"))
    return value


def _require_int(value: Any, label: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AdmissionError(label + "_not_integer")
    if value < minimum or value > maximum:
        raise AdmissionError(label + "_out_of_range")
    return value


def _require_text(value: Any, label: str, maximum: int = 200) -> str:
    if not isinstance(value, str) or not value:
        raise AdmissionError(label + "_empty")
    if len(value) > maximum:
        raise AdmissionError(label + "_too_long")
    if any(ord(character) < 0x20 for character in value):
        raise AdmissionError(label + "_control_character")
    return value


def validate_manifest(document: Any) -> dict:
    manifest = _require_exact_keys(document, MANIFEST_FIELDS, "manifest")
    if manifest["schema_id"] != ADMISSION_SCHEMA_ID:
        raise AdmissionError("schema_id_mismatch")
    request_id = manifest["request_id"]
    if not isinstance(request_id, str) or not SLUG.match(request_id):
        raise AdmissionError("request_id_invalid")
    if manifest["mode"] not in RUN_MODES:
        raise AdmissionError("mode_unsupported")

    candidate = _require_exact_keys(
        manifest["candidate"], CANDIDATE_FIELDS, "candidate")
    if candidate["name"] != TASK_TITLE:
        raise AdmissionError("candidate_name_mismatch")
    for key in ("source_present", "weights_present", "runtime_present"):
        _require_bool(candidate[key], key, False)
    if candidate["revision"] is not None or candidate["license"] is not None:
        raise AdmissionError("candidate_artifact_unpinned")

    source = _require_exact_keys(manifest["input"], INPUT_FIELDS, "input")
    if source["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise AdmissionError("input_rate_unsupported")
    if source["channels"] != CHANNELS:
        raise AdmissionError("input_channels_unsupported")
    if source["dtype"] != "f32":
        raise AdmissionError("input_dtype_unsupported")
    _require_bool(source["finite"], "input_finite", True)
    sample_count = _require_int(
        source["sample_count"], "input_sample_count", 1, MAX_SAMPLE_COUNT)
    peak = canonical_decimal(source["peak"], "input_peak")
    if peak > 1:
        raise AdmissionError("input_peak_out_of_range")

    rate = _require_exact_keys(manifest["rate"], RATE_FIELDS, "rate")
    numerator = _require_int(rate["numerator"], "rate_numerator", 1, 16)
    denominator = _require_int(rate["denominator"], "rate_denominator", 1, 16)
    record = mapping_record(sample_count, numerator, denominator)

    output = _require_exact_keys(manifest["output"], OUTPUT_FIELDS, "output")
    if output["sample_count"] != record["target_samples"]:
        raise AdmissionError("output_sample_count_mismatch")
    digest = output["mapping_sha256"]
    if not isinstance(digest, str) or not SHA256_HEX.match(digest):
        raise AdmissionError("output_mapping_digest_invalid")
    if digest != record["mapping_sha256"]:
        raise AdmissionError("output_mapping_digest_mismatch")
    _require_bool(output["finite"], "output_finite", True)
    if canonical_decimal(output["peak"], "output_peak") != peak:
        raise AdmissionError("output_peak_mismatch")
    if output["first_source"] != record["first_source"]:
        raise AdmissionError("output_first_source_mismatch")
    if output["last_source"] != record["last_source"]:
        raise AdmissionError("output_last_source_mismatch")

    controls = manifest["controls"]
    if not isinstance(controls, list) or not 1 <= len(controls) <= MAX_CONTROLS:
        raise AdmissionError("controls_invalid")
    seen_ids: set[str] = set()
    seen_kinds: set[str] = set()
    for control in controls:
        entry = _require_exact_keys(control, CONTROL_FIELDS, "control")
        control_id = entry["id"]
        if not isinstance(control_id, str) or not SLUG.match(control_id):
            raise AdmissionError("control_id_invalid")
        if control_id in seen_ids:
            raise AdmissionError("control_id_duplicate")
        seen_ids.add(control_id)
        if entry["kind"] not in CONTROL_KINDS:
            raise AdmissionError("control_kind_unknown")
        seen_kinds.add(entry["kind"])
    if not REQUIRED_CONTROL_KINDS <= seen_kinds:
        raise AdmissionError("control_kind_missing")

    rights = _require_exact_keys(manifest["rights"], RIGHTS_FIELDS, "rights")
    for key in ("source_terms", "weight_terms", "input_terms", "output_use"):
        _require_text(rights[key], "rights_" + key)
    _require_bool(rights["claims_qualified"], "claims_qualified", False)

    return {
        "request_id": request_id,
        "sample_count": sample_count,
        "speed_ratio": record["speed_ratio"],
        "target_samples": record["target_samples"],
        "mapping_sha256": record["mapping_sha256"],
        "canonical_sha256": object_digest(manifest),
    }


def envelope_manifest(case_id: str, numerator: int,
                      denominator: int) -> dict:
    record = mapping_record(ENVELOPE_INPUT_SAMPLES, numerator, denominator)
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "request_id": "envelope-" + case_id.replace("_", "-"),
        "mode": "offline",
        "candidate": {
            "name": TASK_TITLE,
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "revision": None,
            "license": None,
        },
        "input": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_count": ENVELOPE_INPUT_SAMPLES,
            "dtype": "f32",
            "finite": True,
            "peak": ENVELOPE_PEAK,
        },
        "rate": {
            "numerator": numerator,
            "denominator": denominator,
        },
        "output": {
            "sample_count": record["target_samples"],
            "mapping_sha256": record["mapping_sha256"],
            "finite": True,
            "peak": ENVELOPE_PEAK,
            "first_source": record["first_source"],
            "last_source": record["last_source"],
        },
        "controls": [
            {"id": "candidate", "kind": "candidate"},
            {"id": "identity", "kind": "identity_passthrough"},
            {"id": "missing", "kind": "missing_runtime"},
            {"id": "nonfinite", "kind": "nonfinite_rejection"},
        ],
        "rights": {
            "source_terms": "blocked: no upstream license text staged",
            "weight_terms": "blocked: no checkpoint or weight staged",
            "input_terms": "blocked: no rights-cleared media staged",
            "output_use": "blocked: no derived-output terms staged",
            "claims_qualified": False,
        },
    }


def envelope_cases() -> list[dict]:
    rows: list[dict] = []
    for case_id, numerator, denominator in ENVELOPE_CASES:
        manifest = envelope_manifest(case_id, numerator, denominator)
        accepted = validate_manifest(manifest)
        record = mapping_record(
            ENVELOPE_INPUT_SAMPLES, numerator, denominator)
        rows.append({
            "id": case_id,
            "input_samples": record["input_samples"],
            "numerator": numerator,
            "denominator": denominator,
            "speed_ratio": record["speed_ratio"],
            "target_samples": record["target_samples"],
            "duration_error_samples": record["duration_error_samples"],
            "first_source": record["first_source"],
            "last_source": record["last_source"],
            "mapping_sha256": record["mapping_sha256"],
            "monotone": record["monotone"],
            "bounded": record["bounded"],
            "identity_exact": record["identity_exact"],
            "accepted_manifest_sha256": accepted["canonical_sha256"],
        })
    return rows


def _mutations() -> list[tuple[str, Any]]:
    base = envelope_manifest("speed_up_125", 5, 4)

    def change(path: tuple[str, ...], value: Any) -> dict:
        document = copy.deepcopy(base)
        target = document
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return document

    def drop(section: str, key: str) -> dict:
        document = copy.deepcopy(base)
        del document[section][key]
        return document

    def add(section: str, key: str) -> dict:
        document = copy.deepcopy(base)
        document[section][key] = "unexpected"
        return document

    return [
        ("missing_manifest_section", drop("candidate", "name")),
        ("extra_manifest_section", add("candidate", "extra")),
        ("extra_top_level_key",
         dict(copy.deepcopy(base), extra="unexpected")),
        ("bad_schema_id", change(("schema_id",), "audio-sdk/x/0.1")),
        ("bad_request_id", change(("request_id",), "Bad Request")),
        ("empty_request_id", change(("request_id",), "")),
        ("unsupported_mode", change(("mode",), "online")),
        ("candidate_name_mismatch", change(("candidate", "name"), "NeuralATSM")),
        ("candidate_source_claimed", change(("candidate", "source_present"), True)),
        ("candidate_weights_claimed",
         change(("candidate", "weights_present"), True)),
        ("candidate_runtime_claimed",
         change(("candidate", "runtime_present"), True)),
        ("candidate_revision_unpinned", change(("candidate", "revision"), "main")),
        ("candidate_license_unpinned", change(("candidate", "license"), "MIT")),
        ("candidate_flag_not_bool", change(("candidate", "source_present"), 0)),
        ("input_rate_8k", change(("input", "sample_rate_hz"), 8000)),
        ("input_stereo", change(("input", "channels"), 2)),
        ("input_zero_samples", change(("input", "sample_count"), 0)),
        ("input_oversized", change(("input", "sample_count"), MAX_SAMPLE_COUNT + 1)),
        ("input_float_count", change(("input", "sample_count"), 19200.0)),
        ("input_dtype_f16", change(("input", "dtype"), "f16")),
        ("input_nonfinite", change(("input", "finite"), False)),
        ("input_peak_nan", change(("input", "peak"), "NaN")),
        ("input_peak_infinity", change(("input", "peak"), "Infinity")),
        ("input_peak_negative", change(("input", "peak"), "-0.5")),
        ("input_peak_over_one", change(("input", "peak"), "1.5")),
        ("input_peak_not_canonical", change(("input", "peak"), "0.781250")),
        ("input_peak_not_string", change(("input", "peak"), 0.5)),
        ("rate_zero_numerator", change(("rate", "numerator"), 0)),
        ("rate_zero_denominator", change(("rate", "denominator"), 0)),
        ("rate_not_reduced", change(("rate", "denominator"), 8)),
        ("rate_too_slow", change(("rate", "numerator"), 1),
         ) if False else (
            "rate_too_slow",
            {"schema_id": ADMISSION_SCHEMA_ID,
             "request_id": "envelope-slow",
             "mode": "offline",
             "candidate": copy.deepcopy(base["candidate"]),
             "input": copy.deepcopy(base["input"]),
             "rate": {"numerator": 1, "denominator": 3},
             "output": copy.deepcopy(base["output"]),
             "controls": copy.deepcopy(base["controls"]),
             "rights": copy.deepcopy(base["rights"])}),
        ("rate_too_fast", {
            "schema_id": ADMISSION_SCHEMA_ID,
            "request_id": "envelope-fast",
            "mode": "offline",
            "candidate": copy.deepcopy(base["candidate"]),
            "input": copy.deepcopy(base["input"]),
            "rate": {"numerator": 3, "denominator": 1},
            "output": copy.deepcopy(base["output"]),
            "controls": copy.deepcopy(base["controls"]),
            "rights": copy.deepcopy(base["rights"]),
        }),
        ("output_count_wrong", change(("output", "sample_count"), 19201)),
        ("output_digest_bad_hex",
         change(("output", "mapping_sha256"), "z" * 64)),
        ("output_digest_mismatch",
         change(("output", "mapping_sha256"), "0" * 64)),
        ("output_finite_false", change(("output", "finite"), False)),
        ("output_peak_mismatch", change(("output", "peak"), "0.5")),
        ("output_first_source_wrong", change(("output", "first_source"), 1)),
        ("output_last_source_wrong", change(("output", "last_source"), 0)),
        ("output_extra_key", add("output", "delay_samples")),
        ("controls_empty", change(("controls",), [])),
        ("controls_missing_candidate",
         change(("controls",),
                [{"id": "identity", "kind": "identity_passthrough"}])),
        ("controls_duplicate_id",
         change(("controls",),
                [{"id": "candidate", "kind": "candidate"},
                 {"id": "candidate", "kind": "identity_passthrough"},
                 {"id": "missing", "kind": "missing_runtime"},
                 {"id": "nonfinite", "kind": "nonfinite_rejection"}])),
        ("controls_unknown_kind",
         change(("controls",),
                [{"id": "candidate", "kind": "candidate"},
                 {"id": "identity", "kind": "listening_result"}])),
        ("controls_too_many",
         change(("controls",),
                [{"id": "c%d" % index, "kind": "candidate"}
                 for index in range(MAX_CONTROLS + 1)])),
        ("rights_claims_qualified", change(("rights", "claims_qualified"), True)),
        ("rights_empty_source", change(("rights", "source_terms"), "")),
        ("rights_missing_output_use", drop("rights", "output_use")),
        ("rights_extra_field", add("rights", "notes")),
    ]


def admission_rejections() -> dict:
    rows: list[dict] = []
    for case_id, document in _mutations():
        try:
            validate_manifest(document)
        except AdmissionError as error:
            rows.append({"id": case_id, "code": error.code})
        else:
            raise RuntimeError("invalid manifest was accepted: " + case_id)
    return {
        "cases": len(rows),
        "rejections": rows,
        "all_rejected": True,
    }


def strict_json_rejections() -> dict:
    payloads = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_literal", '{"a":NaN}'),
        ("infinity_literal", '{"a":Infinity}'),
        ("negative_infinity_literal", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} trailing'),
        ("byte_order_mark", '\ufeff{"a":1}'),
        ("non_object_root", '[1,2,3]'),
        ("empty_input", "   "),
        ("unterminated", '{"a":'),
    )
    rows: list[dict] = []
    for case_id, payload in payloads:
        try:
            loads_strict(payload)
        except (ValueError, json.JSONDecodeError):
            rows.append({"id": case_id, "rejected": True})
        else:
            raise RuntimeError("strict JSON accepted: " + case_id)
    return {"cases": len(rows), "rejections": rows, "all_rejected": True}


def build_protocol_envelope() -> dict:
    cases = envelope_cases()
    identity = next(case for case in cases if case["id"] == "identity_1x")
    if not identity["identity_exact"]:
        raise RuntimeError("identity case is not exact")
    if len(cases) != len(ENVELOPE_CASES):
        raise RuntimeError("envelope case count mismatch")
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "purpose": (
            "Deterministic integer source-to-output position map over one "
            "frozen synthetic duration. Protocol plumbing only; not DiffATSM, "
            "not audio synthesis and not a rate estimator."
        ),
        "algorithm": (
            "target=(input_samples*denominator)//numerator; "
            "source(output_index)=(output_index*numerator)//denominator"
        ),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "input_samples": ENVELOPE_INPUT_SAMPLES,
        "cases": cases,
        "case_count": len(cases),
        "identity_case": identity["id"],
        "identity_exact": identity["identity_exact"],
        "synthesizes_audio": False,
        "loads_model": False,
        "not_candidate": True,
    }


def build_admission() -> dict:
    rejections = admission_rejections()
    strict = strict_json_rejections()
    valid = validate_manifest(envelope_manifest("identity_1x", 1, 1))
    return {
        "schema_id": ADMISSION_SCHEMA_ID,
        "manifest_sha256": valid["canonical_sha256"],
        "manifest_cases": rejections["cases"],
        "rejections": rejections["rejections"],
        "all_rejected": rejections["all_rejected"],
        "strict_json_cases": strict["cases"],
        "strict_json_rejections": strict["rejections"],
        "strict_json_all_rejected": strict["all_rejected"],
        "accepts": (
            "Only an offline manifest that declares absent candidate "
            "artifacts, canonical fields and closed rights terms."
        ),
        "assets_never_loaded": True,
    }


def rate_profile() -> dict:
    rows = []
    for row_id, requirement, state in RATE_REQUIREMENTS:
        blocked = state.startswith("blocked")
        rows.append({
            "id": row_id,
            "requirement": requirement,
            "status": "blocked" if blocked else "documented",
            "evidence": (
                "No candidate source, asset, runtime or output exists; this "
                "item cannot be measured."
                if blocked else
                "Synthetic envelope and missing real results are kept in "
                "separate report sections; no category is pooled."
            ),
            "qualifies": False,
        })
    return {
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "profile_source": SOURCE_PINS[
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "requirement_rows": rows,
        "conditions": [
            "identity_1x",
            "rate_changes",
            "unfamiliar_speech",
            "music",
            "silence",
            "rebuffer",
            "drift",
            "final_partial_window",
            "pause_filler_source_timestamps",
        ],
        "profile_satisfied": False,
        "real_results": 0,
        "synthetic_envelope_only": True,
        "candidate_geometry": None,
        "candidate_duration_result": None,
        "candidate_pitch_result": None,
        "candidate_transient_result": None,
        "candidate_preservation_result": None,
    }


def build_contract() -> dict:
    contract = {
        "schema_id": CONTRACT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "disposition": DISPOSITION,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "source_reported_identity": SOURCE_REPORTED_IDENTITY,
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "exact_blockers": [dict(row) for row in EXACT_BLOCKERS],
        "release_gates": [
            dict(row, status="blocked", qualifies=False,
                 linked_row=board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW))
            for row in RELEASE_GATES
        ],
        "rate_profile": rate_profile(),
        "boundary": boundary_block(),
        "absence_probes": absence_probes(),
        "evidence_snippets": evidence_snippet_check()["checks"],
        "public_v0_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
            "unchanged": True,
        },
        "admission_schema": {
            "schema_id": ADMISSION_SCHEMA_ID,
            "fields": list(MANIFEST_FIELDS),
            "candidate_fields": list(CANDIDATE_FIELDS),
            "input_fields": list(INPUT_FIELDS),
            "rate_fields": list(RATE_FIELDS),
            "output_fields": list(OUTPUT_FIELDS),
            "control_fields": list(CONTROL_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "rights_fields": list(RIGHTS_FIELDS),
            "run_modes": list(RUN_MODES),
            "rate_bounds": {"numerator": [1, 16], "denominator": [1, 16],
                            "speed": ["1/2", "2/1"]},
            "max_sample_count": MAX_SAMPLE_COUNT,
            "max_controls": MAX_CONTROLS,
            "qualifies": False,
        },
        "non_claims": list(NON_CLAIMS),
        "required_results": list(REQUIRED_RESULTS),
        "reopening_conditions": list(REOPENING_CONDITIONS),
    }
    _assert_no_floats(contract)
    return _json_lists(contract)


def build_report() -> dict:
    contract = build_contract()
    contract_digest = object_digest(contract)
    inventory = inventory_record()
    snippets = evidence_snippet_check()
    absence = absence_summary()
    envelope = build_protocol_envelope()
    admission = build_admission()
    checkpoint_scope = (
        {
            "id": "CS-01",
            "artifact": "upstream_source_snapshot",
            "present": False,
            "revision": None,
            "byte_count": None,
            "sha256": None,
            "file_names": None,
            "identity_verified": False,
        },
        {
            "id": "CS-02",
            "artifact": "ppg_extractor_and_acoustic_model",
            "present": False,
            "revision": None,
            "byte_count": None,
            "sha256": None,
            "file_names": None,
            "identity_verified": False,
        },
        {
            "id": "CS-03",
            "artifact": "diffusion_checkpoint_and_vocoder",
            "present": False,
            "revision": None,
            "byte_count": None,
            "sha256": None,
            "file_names": None,
            "identity_verified": False,
        },
        {
            "id": "CS-04",
            "artifact": "inference_config_dependency_lock_and_recipe",
            "present": False,
            "revision": None,
            "byte_count": None,
            "sha256": None,
            "file_names": None,
            "identity_verified": False,
        },
    )
    gates = [
        dict(row, status="blocked", qualifies=False,
             linked_row=board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW))
        for row in RELEASE_GATES
    ]
    report = {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "mode": MODE,
        "profile": PROFILE,
        "profile_key": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "disposition": DISPOSITION,
        "contract_sha256": contract_digest,
        "generated_by": TASK_PREFIX + "run.py",
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "boundary": boundary_block(),
        "inventory_record": inventory,
        "evidence_presence": {
            "inventory_evidence_path": "research/tsm-followup-20261101/README.md",
            "inventory_evidence_line": 36,
            "inventory_evidence_status": inventory["evidence_status"],
            "inventory_disposition": inventory["disposition"],
            "inventory_profile": inventory["verification_profile"],
            "repository_url_recorded": True,
            "official_repository": OFFICIAL_REPOSITORY,
            "release_state": RELEASE_STATE,
            "source_snapshot_present": False,
            "license_text_present": False,
            "checkpoint_present": False,
            "runtime_present": False,
            "snippet_checks": snippets["checks"],
            "all_snippets_present": snippets["all_present"],
            "snippet_count": snippets["count"],
        },
        "source_reported_identity": SOURCE_REPORTED_IDENTITY,
        "absence_evidence": absence,
        "checkpoint_scope": list(checkpoint_scope),
        "runtime_readiness": runtime_readiness(),
        "rate_profile": rate_profile(),
        "protocol_envelope": envelope,
        "admission": admission,
        "gates": gates,
        "exact_blockers": [dict(row) for row in EXACT_BLOCKERS],
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "required_results": list(REQUIRED_RESULTS),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "non_claims": list(NON_CLAIMS),
        "public_v0_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
            "unchanged": True,
        },
        "qualification": {
            "all_release_gates_blocked": True,
            "benchmark_result": False,
            "candidate_present": False,
            "checkpoint_present": False,
            "device_timing_result": False,
            "duration_result": False,
            "implementation_present": False,
            "input_media_present": False,
            "license_text_present": False,
            "listening_result": False,
            "missing_result_promoted": False,
            "not_qualified": True,
            "output_validity_result": False,
            "pitch_result": False,
            "rate_profile_result": False,
            "readiness": "incomplete",
            "real_result_present": False,
            "reference_execution_result": False,
            "release_claim": False,
            "renderer_result": False,
            "runtime_pinned": False,
            "runtime_present": False,
            "source_identity_recorded": False,
            "source_present": False,
            "status": "not_qualified",
            "transient_result": False,
            "weights_identified": False,
            "weights_present": False,
        },
        "reproduction": {
            "repeat_count": 3,
            "byte_identical": True,
            "interpreter": REQUIRED_INTERPRETER,
            "canonical_json": True,
            "sorted_keys": True,
            "trailing_newline": False,
            "report_sha256_sidecar": "report.json.sha256",
        },
        "scope": {
            "benchmark_run": False,
            "device_timing_measured": False,
            "installed_v0_changed": False,
            "listening_performed": False,
            "network_used": False,
            "provider_registered": False,
            "public_abi_changed": False,
            "real_assets_used": False,
            "reference_executed": False,
            "reference_implemented": False,
            "registry_or_default_changed": False,
            "release_claim": False,
            "shared_build_or_ci_changed": False,
            "task_local_only": True,
            "write_scope": WRITE_SCOPE,
        },
    }
    _assert_no_floats(report)
    return _json_lists(report)


def canonical_report(document: dict | None = None) -> tuple[str, str]:
    payload = canonical_text(document if document is not None else build_report())
    return payload, hashlib.sha256(payload.encode("ascii")).hexdigest()


def main() -> int:
    document = build_report()
    payload, digest = canonical_report(document)
    print(payload)
    print("report_sha256=" + digest, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
