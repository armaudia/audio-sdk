# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only AIx Speed ASR-guided planner DEFER package.

This is a *proposal-only* rate-profile evidence package.  It does not contain,
link, import, install, download, execute or emulate the AIx Speed research
method, a jointly trained speed/ASR model, Wav2Vec2 weights, an ASR runtime, a
held-out transcript cohort, a listening panel or a target device.  No public
AIx Speed implementation was found in the pinned source, so there is nothing
exact to reproduce.  Consequently every candidate result is ``None`` with an
explicit status and no result qualifies.

What is reproduced mechanically is only a bounded, deterministic
*arithmetic* control:

* a strict content-aware rate-envelope contract with exact rational rates,
  exact source-to-output sample mapping, contiguous source coverage, the
  declared 3/4..3/2 clamp and the "never speed meaningful speech above 1.0x"
  guard, all labelled as a local declared policy, not AIx Speed;
* one synthetic guided envelope and one exact 1x identity envelope on a
  16,000-sample integer fixture, with the duration identity
  ``sum(d_i / r_i) == sum(d_i)`` checked exactly;
* an explicit, fail-closed separation between an ASR proxy and listening:
  both are ``blocked`` and neither is promoted, pooled or relabelled;
* a strict caller-supplied qualification manifest whose paths and full
  SHA-256 values are checked but whose bytes are never parsed, loaded or
  executed; and
* adverse, missing, invalid, nonfinite, guarded, gap, overlap and
  candidate-claim inputs rejected before any state change.

No synthetic number here is an AIx Speed output, a recognition score, a WER or
CER, a comprehension result, a human rating, a device measurement, a benchmark
or a release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]

TASK_ID = "SDK-AIX-SPEED-ASR-GUIDED-PLANNER"
COMPONENT = "aix-speed-asr-guided-planner"
TITLE = "AIx Speed ASR-guided planner"
BASE_COMMIT = "f245d81f86b556dca4bcdb1b7afb2ea898065ed7"
BRANCH = "swarm/SDK-AIX-SPEED-ASR-GUIDED-PLANNER"
SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
STATUS = "proposal_only_incomplete_not_qualified"
COMPLETENESS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
PROPOSAL_ONLY = True
LOCAL_IDENTITY = "aix-speed-asr-guided-planner-rate-envelope-reference-v1"

# Installed v0 stays untouched; these constants are boundary facts only.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"

# Declared first-product clamp from the pinned rate note.  This is a declared
# policy, not a measurement and not an AIx Speed reproduction.
MIN_RATE = Fraction(3, 4)
MAX_RATE = Fraction(3, 2)
PROTECTED_SPEECH_CEILING = Fraction(1, 1)
LOOKAHEAD_MIN_MS = 200
LOOKAHEAD_MAX_MS = 1000

# Deterministic synthetic integer fixture, not speech and not a corpus.
CONTROL_TOTAL_SAMPLES = 16000
CONTROL_TOTAL_MS = 1000.0
CONTROL_SEGMENTS: Tuple[Tuple[int, int, str, int, int], ...] = (
    (0, 2400, "silence", 3, 2),
    (2400, 3600, "filler", 6, 5),
    (3600, 7600, "speech", 4, 5),
    (7600, 16000, "speech", 1, 1),
)
CONTENT_CLASSES = ("speech", "filler", "silence", "music", "noise")
SEGMENT_FIELDS: Tuple[str, ...] = (
    "segment_id",
    "start_sample",
    "end_sample_exclusive",
    "content_class",
    "rate_numerator",
    "rate_denominator",
    "asr_proxy_score",
    "is_candidate_result",
)

# Paper provenance only.  No source, weights or runtime is present.
CANDIDATE_LOCATOR = "https://arxiv.org/abs/2403.02938"
CANDIDATE_METHOD = (
    "per-phoneme playback speed chosen from an ASR recognition score used as "
    "a proxy for human intelligibility"
)
CANDIDATE_CLAIM = (
    "source-reported ~1.3x average speed with lower CER/WER than "
    "constant-speed playback"
)
CANDIDATE_FAMILY = "AIx Speed"
CANDIDATE_IMPLEMENTATION_PUBLIC = False

MANIFEST_FIELDS: Tuple[str, ...] = (
    "artifact_id",
    "asr_proxy_scorer_id",
    "caller_attestation",
    "candidate_id",
    "license_path",
    "license_sha256",
    "listening_protocol_id",
    "model_family",
    "rights_approval_path",
    "rights_approval_sha256",
    "runtime_path",
    "runtime_sha256",
    "source_path",
    "source_revision",
    "source_sha256",
    "terms_accepted",
    "transcript_cohort_id",
    "transcript_manifest_path",
    "transcript_manifest_sha256",
    "weights_path",
    "weights_sha256",
)
CALLER_ATTESTATION = "caller_owned_and_rights_reviewed"
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,95}$")

SOURCE_PINS: Dict[str, str] = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "cpp-library/pipeline-validation/playback-speed/README.md":
        "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f",
    "cpp-library/pipeline-validation/playback-speed/results/report.md":
        "9c9383297b1160dbe4f7261f789b493d70354b11930f4d8527b20b0ca8c87c34",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}
SIBLING_PINS: Dict[str, str] = {
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/contract.json":
        "ee23e6cc21f9f3293a48dab7008a4c41f129074cafa3eb6b273f2f3ef413d694",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json":
        "57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2",
    "docs/task-evidence/d1-whole-clip-duration-planner/reference.py":
        "ffb59e3d09d7cef0580d73cf9772d6e69d0ddfb991457e7878ac4bf86cf7c253",
    "docs/task-evidence/d1-whole-clip-duration-planner/fixtures/report.json":
        "522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98",
    "docs/task-evidence/additional-vm-asr-audio-super-resolution/contract.json":
        "c59d99d0bb9280bb73bdf8608d8021cc338556609748db597b385c5d12d91301",
    "docs/task-evidence/additional-vm-asr-audio-super-resolution/report.json":
        "3fa34b0e49d992f7e6261970b648aaa095a88bc07877372ba4df4422c5023b12",
    "docs/task-evidence/ffmpeg-atempo/contract.json":
        "0f3ca86b4658d6656b0528bbcc1e1aa822928dbd72a48a66f16ad4f981b10fac",
    "docs/task-evidence/ffmpeg-atempo/report.json":
        "a3986e6cb9d7315995aa13c74806c260c620d01b6f545e0837b127565c2ba249",
    "docs/task-evidence/signalsmith-stretch/contract.json":
        "cec65c71a339e76bb668cb9d895285b7b152229d6a9af20c2401b69c7785ff9e",
    "docs/task-evidence/signalsmith-stretch/report.json":
        "e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231",
}

TASK_ROW_IDENTITY: Dict[str, Any] = {
    "id": TASK_ID,
    "title": TITLE,
    "repository": "audio-sdk",
    "mode": "research-control",
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    "evidence": ["cpp-library/pipeline-validation/playback-speed-candidates.md"],
    "base_commit": BASE_COMMIT,
    "branch": BRANCH,
}
MUTABLE_PROVENANCE: Dict[str, Any] = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "mutable": True,
    "gate": False,
    "hashed": False,
    "note": (
        "Only the stable linked-row projection above is compared. The mutable "
        "full board file is never hashed by or pinned to this package."
    ),
}
SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_only": True,
    "installed_v0_format": "16 kHz mono float32, 160 samples",
    "aix_speed_source": False,
    "licensed_source_or_binary": False,
    "trained_weights": False,
    "model_runtime_executed": False,
    "asr_runtime_executed": False,
    "heldout_transcripts": False,
    "real_speech_or_corpus": False,
    "audio_processed": False,
    "asr_proxy_result": False,
    "listening": False,
    "downloads": False,
    "network_used": False,
    "provider_registered": False,
    "device_timing": False,
    "benchmark_claim": False,
    "release_claim": False,
}
PUBLIC_SURFACE: Dict[str, bool] = {
    "abi_change": False,
    "benchmark_claim": False,
    "ci_change": False,
    "descriptor_default_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_change": False,
    "registry_change": False,
    "release_claim": False,
    "shared_cmakelists_change": False,
}
QUALIFICATION: Dict[str, Any] = {
    "status": QUALIFICATION_STATUS,
    "qualifies": False,
    "incomplete": True,
    "proposal_only": True,
    "missing_result_promoted": False,
    "aix_speed_source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "license_approved": False,
    "heldout_transcripts_present": False,
    "asr_proxy_result_present": False,
    "listening_present": False,
    "measured_rate_present": False,
    "measured_timing_present": False,
    "device_timing_present": False,
    "release_claim": False,
    "all_release_gates_blocked": True,
    "local_control_is_candidate": False,
    "asr_proxy_is_listening": False,
}
REQUIRED_ARTIFACTS: List[Dict[str, Any]] = [
    {
        "id": "exact_aix_speed_source",
        "artifact": (
            "The exact author source revision for the AIx Speed per-phoneme "
            "speed planner, or an authorized implementation, pinned by a "
            "40-hex revision and a full SHA-256."
        ),
        "present": False,
        "rights_requirement": (
            "The repository/paper code licence, a written grant to reproduce "
            "and redistribute the implementation, and an output-use decision."
        ),
        "why_blocked": (
            "The pinned note records no public implementation for AIx Speed; "
            "no checkout, revision or source archive exists locally."
        ),
    },
    {
        "id": "joint_speed_asr_weights",
        "artifact": (
            "The exact jointly trained speed/ASR model weights, including the "
            "Wav2Vec2 backbone, with an immutable version and full SHA-256."
        ),
        "present": False,
        "rights_requirement": (
            "Weight-specific terms covering local execution, commercial use, "
            "redistribution and generated-output use."
        ),
        "why_blocked": (
            "No AIx Speed checkpoint, Wav2Vec2 derivative or model card exists "
            "locally; nothing is downloaded or substituted."
        ),
    },
    {
        "id": "pinned_asr_runtime_environment",
        "artifact": (
            "A locked inference environment with exact framework, tokenizer, "
            "audio-frontend and accelerator versions plus install digests."
        ),
        "present": False,
        "rights_requirement": (
            "Runtime and dependency licences plus approval for the exact "
            "versions on the target host."
        ),
        "why_blocked": (
            "No environment, package lock or installed runtime for AIx Speed "
            "exists; no import or execution is attempted."
        ),
    },
    {
        "id": "license_and_output_rights",
        "artifact": (
            "The exact paper/code/weight terms and a signed rights decision "
            "for execution, benchmarking, redistribution and output use."
        ),
        "present": False,
        "rights_requirement": (
            "Author and weight rightsholder terms, derivative-output "
            "permissions and commercial-use approval for the named revision."
        ),
        "why_blocked": (
            "The method is described in a copyrighted paper; no code or weight "
            "licence text and no signed approval are present."
        ),
    },
    {
        "id": "rights_cleared_heldout_transcript_cohort",
        "artifact": (
            "A frozen held-out transcript cohort with consent, language and "
            "speaker metadata, human-verified word and phoneme timestamps and "
            "a manifest digest."
        ),
        "present": False,
        "rights_requirement": (
            "Corpus, participant, annotation, redistribution and "
            "model-evaluation rights for every recording and transcript."
        ),
        "why_blocked": (
            "No held-out transcript cohort, human-verified phoneme alignment "
            "or rights record is assigned to this task."
        ),
    },
    {
        "id": "independent_asr_proxy_scorer",
        "artifact": (
            "A pinned ASR proxy implementation with reference transcripts, "
            "alignment rules, aggregation and retained failures."
        ),
        "present": False,
        "rights_requirement": (
            "Scorer, model and reference-transcript terms plus approval for "
            "the exact implementation revisions."
        ),
        "why_blocked": (
            "No independent ASR proxy scorer, reference transcript or "
            "calibration result exists for this task."
        ),
    },
    {
        "id": "listening_protocol_and_panel",
        "artifact": (
            "A blind listening protocol, matched anchors, authorized panel and "
            "a comprehension/preference analysis separate from the ASR proxy."
        ),
        "present": False,
        "rights_requirement": (
            "Panel consent, participant-data terms and approval to collect and "
            "publish listening outcomes."
        ),
        "why_blocked": (
            "No listening protocol, panel, anchor set or authorization exists; "
            "the ASR proxy is never relabelled as listening."
        ),
    },
    {
        "id": "opt_in_adapter_intake_and_release_review",
        "artifact": (
            "An OFF-by-default opt-in adapter intake, independent exact-head "
            "review, measured rate/device evidence and explicit release "
            "approval."
        ),
        "present": False,
        "rights_requirement": (
            "Reviewer, timing-harness and release-authority approval for the "
            "declared scope."
        ),
        "why_blocked": (
            "No adapter, registration, default, measured rate evidence, review "
            "or release decision exists; none is added here."
        ),
    },
]
RELEASE_GATES: List[Dict[str, Any]] = [
    {
        "id": "exact_aix_speed_source_and_weights_identity",
        "requirement": (
            "An exact AIx Speed source revision or authorized implementation "
            "and jointly trained weights, each with an immutable version and "
            "full SHA-256."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "license_and_output_rights",
        "requirement": (
            "Reviewed paper/code/weight terms and written approval for local "
            "execution, benchmarking, redistribution and generated-output use."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "pinned_asr_runtime_and_environment",
        "requirement": (
            "A locked framework, tokenizer, frontend and accelerator "
            "environment with exact dependency versions and install digests."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "declared_planner_geometry_lookahead_and_content_delay",
        "requirement": (
            "The official per-phoneme alignment, rate application, lookahead, "
            "buffering, reset, drain, content-delay and final-window contract "
            "reproduced for the exact runtime."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "rights_cleared_heldout_transcript_cohort",
        "requirement": (
            "A rights-cleared held-out transcript cohort with human-verified "
            "word/phoneme timestamps, consent and a frozen manifest."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "separate_asr_proxy_and_listening_quality",
        "requirement": (
            "Independent ASR-proxy WER/CER deltas and a separate authorized "
            "blind listening/comprehension result, reported separately with "
            "uncertainty and retained failures."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "measured_rate_duration_pitch_transient_and_device_timing",
        "requirement": (
            "Measured source/output mapping, duration drift, pitch, transient "
            "audibility, buffering, final partial window and target-device "
            "timing/resources for the exact runtime."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "opt_in_adapter_intake_and_release_review",
        "requirement": (
            "An OFF-by-default opt-in adapter intake, independent exact-head "
            "review of this evidence, and explicit release approval."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
]
NON_CLAIMS: List[str] = [
    "No AIx Speed source, implementation, jointly trained weights, Wav2Vec2 derivative, ASR runtime or emulator is present, linked, imported, executed or reproduced.",
    "No paper, code, weights, corpus, transcript or recording is downloaded, copied, vendored or substituted.",
    "No AIx Speed rate envelope, per-phoneme speed, recognition score, WER/CER delta, comprehension result, MOS, ranking or threshold is claimed; every candidate result is null.",
    "The synthetic envelope control is arithmetic only and is not an AIx Speed output, an ASR proxy result or a listening result.",
    "ASR proxy and listening are reported as separate blocked evidence classes; neither is relabelled, pooled or promoted.",
    "No real speech, held-out transcript, listening panel, device timing, benchmark or release claim is made.",
    "No installed v0, ABI, registry, descriptor, default, shared build or CI behavior is changed.",
    "No provider or processor is registered, exposed or default-enabled.",
    "No missing, blocked or adverse result is promoted; no result qualifies.",
]
REPRODUCTION: List[str] = [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
    "python3 run.py --report",
    "python3 run.py --contract",
    "python3 run.py --sources",
    "python3 run.py --inspect",
    "python3 verify.py",
]
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256",
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
REPORT_KEYS = {
    "SPDX-FileCopyrightText",
    "SPDX-License-Identifier",
    "schema_id",
    "task",
    "component",
    "title",
    "profile",
    "status",
    "completeness",
    "decision",
    "proposal_only",
    "base_commit",
    "branch",
    "qualification",
    "task_row",
    "mutable_provenance",
    "source_pins",
    "boundary_pins",
    "sibling_pins",
    "scope",
    "public_surface",
    "candidate_record",
    "declared_contract",
    "manifest_contract",
    "required_artifacts",
    "control_envelope",
    "manifest_controls",
    "adverse_results",
    "missing_results",
    "qualification_slots",
    "failure_controls",
    "acceptance_profile",
    "observed_provenance",
    "artifact_assessment",
    "ranking",
    "release_gates",
    "non_claims",
    "reproduction",
    "regeneration",
}
CONTRACT_KEYS = {
    "SPDX-FileCopyrightText",
    "SPDX-License-Identifier",
    "schema_id",
    "task",
    "component",
    "title",
    "profile",
    "status",
    "completeness",
    "decision",
    "proposal_only",
    "base_commit",
    "branch",
    "qualification",
    "task_row",
    "mutable_provenance",
    "source_pins",
    "boundary_pins",
    "sibling_pins",
    "scope",
    "public_surface",
    "candidate_record",
    "declared_contract",
    "manifest_contract",
    "required_artifacts",
    "release_gates",
    "artifact_pins",
    "local_files",
    "reproduction",
    "non_claims",
}


class ReferenceError(ValueError):
    """Explicit rejection; no rejected value is scored or promoted."""


def _reject_constant(value: str) -> None:
    raise ValueError("non_json_constant:" + value)


def read_strict_json(path: Path) -> Any:
    """Parse strict JSON; duplicate keys, NaN and Infinity are rejected."""
    def unique_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"),
                       parse_constant=_reject_constant,
                       object_pairs_hook=unique_pairs)
    if not isinstance(value, dict):
        raise ValueError("json_root_is_not_an_object")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True,
                      allow_nan=False)
    payload = (text + "\n").encode("utf-8")
    return text, sha256_bytes(payload)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _r9(value: Any) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), 9)


def _ratio_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return "%d/%d" % (value.numerator, value.denominator)


# ---------------------------------------------------------------------------
# Strict content-aware rate envelope (declared local policy, not AIx Speed)
# ---------------------------------------------------------------------------

def parse_rate(numerator: Any, denominator: Any) -> Fraction:
    if type(numerator) is not int:
        raise ReferenceError("rate_numerator_is_not_an_integer")
    if type(denominator) is not int:
        raise ReferenceError("rate_denominator_is_not_an_integer")
    if numerator <= 0:
        raise ReferenceError("rate_numerator_is_not_positive")
    if denominator <= 0:
        raise ReferenceError("rate_denominator_is_not_positive")
    rate = Fraction(numerator, denominator)
    if rate < MIN_RATE:
        raise ReferenceError("rate_below_declared_floor")
    if rate > MAX_RATE:
        raise ReferenceError("rate_above_declared_ceiling")
    return rate


def _check_content_guard(content_class: str, rate: Fraction) -> None:
    if content_class == "speech":
        if rate > PROTECTED_SPEECH_CEILING:
            raise ReferenceError("meaningful_speech_must_not_be_sped_up")
    elif content_class in ("silence", "filler"):
        if rate < PROTECTED_SPEECH_CEILING:
            raise ReferenceError("silence_or_filler_must_not_be_slowed")
    elif content_class in ("music", "noise"):
        if rate > PROTECTED_SPEECH_CEILING:
            raise ReferenceError("music_or_noise_must_not_be_sped_up")
    else:
        raise ReferenceError("unsupported_content_class")


def _validate_score(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReferenceError("asr_proxy_score_is_not_a_real_number")
    number = float(value)
    if not math.isfinite(number):
        raise ReferenceError("asr_proxy_score_is_nonfinite")
    if number < 0.0 or number > 1.0:
        raise ReferenceError("asr_proxy_score_out_of_range")
    return number


def validate_envelope(segments: Any,
                      total_samples: int = CONTROL_TOTAL_SAMPLES) -> List[Dict[str, Any]]:
    """Validate a strict rate envelope; never process or play audio."""
    if type(total_samples) is not int:
        raise ReferenceError("total_samples_is_not_an_integer")
    if total_samples <= 0:
        raise ReferenceError("total_samples_is_not_positive")
    if not isinstance(segments, (list, tuple)):
        raise ReferenceError("envelope_is_not_a_segment_list")
    if not segments:
        raise ReferenceError("envelope_is_empty")
    normalized: List[Dict[str, Any]] = []
    seen: set = set()
    cursor = 0
    for position, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise ReferenceError("segment_is_not_an_object")
        if set(segment) != set(SEGMENT_FIELDS):
            missing = sorted(set(SEGMENT_FIELDS) - set(segment))
            extra = sorted(set(segment) - set(SEGMENT_FIELDS))
            if missing:
                raise ReferenceError(
                    "segment_missing_fields:" + ",".join(missing))
            raise ReferenceError("segment_extra_fields:" + ",".join(extra))
        segment_id = segment["segment_id"]
        if not isinstance(segment_id, str) or not ID_RE.match(segment_id):
            raise ReferenceError("segment_id_is_invalid")
        if segment_id in seen:
            raise ReferenceError("segment_id_is_duplicated")
        seen.add(segment_id)
        start = segment["start_sample"]
        end = segment["end_sample_exclusive"]
        if type(start) is not int:
            raise ReferenceError("segment_start_is_not_an_integer")
        if type(end) is not int:
            raise ReferenceError("segment_end_is_not_an_integer")
        if start != cursor:
            if start < cursor:
                raise ReferenceError("segment_intervals_overlap")
            raise ReferenceError("segment_intervals_have_a_gap")
        if end <= start:
            raise ReferenceError("segment_interval_is_empty_or_reversed")
        if end > total_samples:
            raise ReferenceError("segment_extends_beyond_total_samples")
        content_class = segment["content_class"]
        if content_class not in CONTENT_CLASSES:
            raise ReferenceError("unsupported_content_class")
        rate = parse_rate(segment["rate_numerator"],
                          segment["rate_denominator"])
        _check_content_guard(content_class, rate)
        score = _validate_score(segment["asr_proxy_score"])
        if segment["is_candidate_result"] is not False:
            raise ReferenceError("candidate_claim_without_artifact")
        normalized.append({
            "position": position,
            "segment_id": segment_id,
            "start_sample": start,
            "end_sample_exclusive": end,
            "content_class": content_class,
            "rate": rate,
            "asr_proxy_score": score,
            "is_candidate_result": False,
        })
        cursor = end
    if cursor != total_samples:
        raise ReferenceError("envelope_does_not_cover_total_samples")
    return normalized


def _control_segment_documents() -> List[Dict[str, Any]]:
    documents: List[Dict[str, Any]] = []
    for index, (start, end, content_class, num, den) in enumerate(
            CONTROL_SEGMENTS):
        documents.append({
            "segment_id": "seg-%02d-%s" % (index, content_class),
            "start_sample": start,
            "end_sample_exclusive": end,
            "content_class": content_class,
            "rate_numerator": num,
            "rate_denominator": den,
            "asr_proxy_score": None,
            "is_candidate_result": False,
        })
    return documents


def _identity_segment_document() -> List[Dict[str, Any]]:
    return [{
        "segment_id": "identity-seg-00-speech",
        "start_sample": 0,
        "end_sample_exclusive": CONTROL_TOTAL_SAMPLES,
        "content_class": "speech",
        "rate_numerator": 1,
        "rate_denominator": 1,
        "asr_proxy_score": None,
        "is_candidate_result": False,
    }]


def _rate_bounds(normalized: Sequence[Dict[str, Any]]) -> Tuple[Fraction, Fraction]:
    rates = [item["rate"] for item in normalized]
    return min(rates), max(rates)


def envelope_payload(segments: Any, control_id: str) -> Dict[str, Any]:
    normalized = validate_envelope(segments)
    total_input = sum(item["end_sample_exclusive"] - item["start_sample"]
                      for item in normalized)
    cursor = Fraction(0, 1)
    rows: List[Dict[str, Any]] = []
    for item in normalized:
        duration = Fraction(item["end_sample_exclusive"]
                            - item["start_sample"], 1)
        output = duration / item["rate"]
        rows.append({
            "position": item["position"],
            "segment_id": item["segment_id"],
            "start_sample": item["start_sample"],
            "end_sample_exclusive": item["end_sample_exclusive"],
            "content_class": item["content_class"],
            "rate": _ratio_text(item["rate"]),
            "asr_proxy_score": (_r9(item["asr_proxy_score"])
                                if item["asr_proxy_score"] is not None
                                else None),
            "output_start_sample": _ratio_text(cursor),
            "output_end_sample": _ratio_text(cursor + output),
            "output_start_ms": _r9(cursor * 1000 / SAMPLE_RATE_HZ),
            "output_end_ms": _r9((cursor + output) * 1000 / SAMPLE_RATE_HZ),
            "is_candidate_result": False,
        })
        cursor += output
    total_output = cursor
    delta = total_output - total_input
    minimum, maximum = _rate_bounds(normalized)
    mapping_digest = sha256_bytes(canonical_bytes([
        {key: row[key] for key in (
            "segment_id", "start_sample", "end_sample_exclusive",
            "content_class", "rate", "output_start_sample",
            "output_end_sample")}
        for row in rows
    ]))
    return {
        "control_id": control_id,
        "segments": rows,
        "total_input_samples": total_input,
        "total_output_samples": _ratio_text(total_output),
        "output_samples_is_integer": total_output.denominator == 1,
        "average_rate": _ratio_text(Fraction(total_input, 1) / total_output),
        "duration_delta_samples": _ratio_text(delta),
        "duration_delta_ms": _r9(delta * 1000 / SAMPLE_RATE_HZ),
        "min_rate": _ratio_text(minimum),
        "max_rate": _ratio_text(maximum),
        "source_output_mapping_exact": True,
        "mapping_sha256": mapping_digest,
        "is_synthetic_control": True,
        "is_aix_speed": False,
        "is_candidate_result": False,
        "qualifies": False,
    }


def control_envelope_payload() -> Dict[str, Any]:
    guided = envelope_payload(_control_segment_documents(),
                              "guided_content_aware_control")
    identity = envelope_payload(_identity_segment_document(),
                                "identity_1x_control")
    return {
        "design": {
            "guided": (
                "declared content-aware envelope: silence 3/2, filler 6/5, "
                "protected speech 4/5 and 1/1, exact duration identity"
            ),
            "identity": "exact 1x passthrough envelope",
            "declared_min_rate": _ratio_text(MIN_RATE),
            "declared_max_rate": _ratio_text(MAX_RATE),
            "protected_speech_ceiling": _ratio_text(
                PROTECTED_SPEECH_CEILING),
            "policy_is_aix_speed": False,
            "is_synthetic_control": True,
            "is_candidate_result": False,
        },
        "guided": guided,
        "identity": identity,
        "asr_proxy": {
            "status": "blocked",
            "scorer_id": None,
            "reference_transcript": None,
            "wer_delta_pp": None,
            "cer_delta_pp": None,
            "reason": (
                "no AIx Speed weights, ASR runtime or rights-cleared held-out "
                "transcript cohort exists"
            ),
            "qualifies": False,
        },
        "listening": {
            "status": "blocked",
            "protocol_id": None,
            "panel_authorized": False,
            "comprehension": None,
            "preference": None,
            "mos": None,
            "reason": (
                "no blind listening protocol, matched anchors or authorized "
                "panel exists"
            ),
            "qualifies": False,
        },
        "separation": {
            "asr_proxy_is_listening": False,
            "pooled_metric": None,
            "separate_reporting_required": True,
            "asr_proxy_result_present": False,
            "listening_result_present": False,
            "qualifies": False,
        },
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Declared boundary and candidate record
# ---------------------------------------------------------------------------

def declared_contract() -> Dict[str, Any]:
    return {
        "contract_id": "aix-speed-asr-guided-planner/rate-envelope-proposal/0.1",
        "adapter_status": "proposal_only_no_aix_speed_source_weights_or_runtime",
        "host_grid": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
        },
        "declared_rate_range": [_ratio_text(MIN_RATE), _ratio_text(MAX_RATE)],
        "declared_protected_speech_ceiling": _ratio_text(
            PROTECTED_SPEECH_CEILING),
        "declared_lookahead_ms_range": [LOOKAHEAD_MIN_MS, LOOKAHEAD_MAX_MS],
        "declared_duration_target": "sum(d_i / r_i) == sum(d_i)",
        "declared_source_timestamp_unit": "source_sample_at_16khz",
        "rate_range_is_a_measurement": False,
        "lookahead_is_a_measurement": False,
        "per_phoneme_alignment_contract": "not_established",
        "rate_application_contract": "not_established",
        "content_delay_contract": "not_established",
        "availability_contract": "not_established",
        "buffering_contract": "not_established",
        "reset_contract": "not_established",
        "drain_contract": "not_established",
        "final_partial_window_contract": "not_established",
        "official_geometry_verified": False,
        "aix_speed_runtime_verified": False,
        "installed_v0_unchanged": True,
        "qualifies": False,
    }


def candidate_record() -> Dict[str, Any]:
    return {
        "candidate": "AIx Speed",
        "family": CANDIDATE_FAMILY,
        "component": COMPONENT,
        "locator": CANDIDATE_LOCATOR,
        "authors": "Kawamura & Rekimoto (per the pinned note)",
        "method": CANDIDATE_METHOD,
        "source_reported_claim": CANDIDATE_CLAIM,
        "backbone": "Wav2Vec2-based joint speed/ASR training",
        "public_implementation_found": CANDIDATE_IMPLEMENTATION_PUBLIC,
        "artifact_present": False,
        "weights_present": False,
        "runtime_present": False,
        "license_reviewed": False,
        "source_reported_only": True,
        "reproduced_here": False,
        "source_reported_scores_present": False,
        "qualifies": False,
    }


def _path_present(relative: str) -> bool:
    return (WORKSPACE / relative).exists()


def artifact_assessment() -> Dict[str, Any]:
    checked = (
        "data/checkouts/aix-speed",
        "data/checkouts/aix-speed-asr-guided-planner",
        "data/models/aix-speed",
        "data/models/aix-speed-asr-guided-planner",
        "data/sources/aix-speed",
        "data/sources/aix-speed-asr-guided-planner",
        "data/licenses/aix-speed",
        "data/licenses/aix-speed-asr-guided-planner",
        "data/envs/aix-speed",
        "data/envs/aix-speed-asr-guided-planner",
        "data/reference/aix-speed",
        "data/reference/aix-speed-asr-guided-planner",
        "adapters/aix-speed-asr-guided-planner",
    )
    presence = {path: _path_present(path) for path in checked}
    all_absent = not any(presence.values())
    return {
        "checked_paths": presence,
        "all_required_absent": all_absent,
        "aix_speed_source_present": any(
            presence[path] for path in checked
            if "checkouts" in path or "sources" in path),
        "weights_present": any(
            presence[path] for path in checked if "models" in path),
        "runtime_present": any(
            presence[path] for path in checked if "envs" in path),
        "license_approved": any(
            presence[path] for path in checked if "licenses" in path),
        "heldout_transcripts_present": any(
            presence[path] for path in checked if "reference" in path),
        "adapter_present": any(
            presence[path] for path in checked if "adapters" in path),
        "package_assets_present": False,
        "conclusion": (
            "BLOCKED: no AIx Speed source revision, jointly trained weights, "
            "ASR runtime, licence/rights approval, rights-cleared held-out "
            "transcript cohort, ASR proxy result or listening result exists "
            "locally; nothing was downloaded, copied or executed."
        ),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied qualification manifest (shape and hash only; never executed)
# ---------------------------------------------------------------------------

def _valid_manifest_document() -> Dict[str, Any]:
    return {
        "artifact_id": "aix-speed-bundle-2026",
        "asr_proxy_scorer_id": "whisper-proxy-2026",
        "caller_attestation": CALLER_ATTESTATION,
        "candidate_id": COMPONENT,
        "license_path": "/caller/aix-speed/LICENSE.txt",
        "license_sha256": "b" * 64,
        "listening_protocol_id": "blind-listening-protocol-2026",
        "model_family": CANDIDATE_FAMILY,
        "rights_approval_path": "/caller/aix-speed/APPROVAL.txt",
        "rights_approval_sha256": "c" * 64,
        "runtime_path": "/caller/aix-speed/runtime",
        "runtime_sha256": "d" * 64,
        "source_path": "/caller/aix-speed/source",
        "source_revision": "a" * 40,
        "source_sha256": "e" * 64,
        "terms_accepted": True,
        "transcript_cohort_id": "heldout-transcripts-2026",
        "transcript_manifest_path": "/caller/aix-speed/transcripts.json",
        "transcript_manifest_sha256": "f" * 64,
        "weights_path": "/caller/aix-speed/weights",
        "weights_sha256": "9" * 64,
    }


def validate_manifest_path(key: str, value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise ReferenceError("path_is_not_a_nonempty_string:" + key)
    if "\\" in value:
        raise ReferenceError("path_is_not_posix:" + key)
    if not os.path.isabs(value):
        raise ReferenceError("path_is_not_absolute:" + key)
    parts = [part for part in value.split("/") if part]
    if any(part in (".", "..") for part in parts):
        raise ReferenceError("path_has_traversal_component:" + key)
    if not parts:
        raise ReferenceError("path_has_no_components:" + key)
    return value


def parse_manifest(document: Any) -> Dict[str, Any]:
    """Validate manifest shape; never open, parse or execute an artifact."""
    if not isinstance(document, dict):
        raise ReferenceError("manifest_is_not_an_object")
    keys = set(document)
    if keys != set(MANIFEST_FIELDS):
        missing = sorted(set(MANIFEST_FIELDS) - keys)
        extra = sorted(keys - set(MANIFEST_FIELDS))
        if missing:
            raise ReferenceError("manifest_missing_fields:" + ",".join(missing))
        raise ReferenceError("manifest_extra_fields:" + ",".join(extra))
    if document["candidate_id"] != COMPONENT:
        raise ReferenceError("manifest_candidate_id_mismatch")
    if document["model_family"] != CANDIDATE_FAMILY:
        raise ReferenceError("manifest_model_family_mismatch")
    for key in ("artifact_id", "transcript_cohort_id"):
        value = document[key]
        if not isinstance(value, str) or not ID_RE.match(value):
            raise ReferenceError("manifest_invalid_identifier:" + key)
    for key in ("asr_proxy_scorer_id", "listening_protocol_id"):
        value = document[key]
        if not isinstance(value, str) or not ID_RE.match(value):
            raise ReferenceError("manifest_invalid_identifier:" + key)
    if document["listening_protocol_id"] in ("not_established", "none", "null"):
        raise ReferenceError("manifest_listening_protocol_is_not_established")
    if document["asr_proxy_scorer_id"] == document["listening_protocol_id"]:
        raise ReferenceError("manifest_asr_proxy_and_listening_are_not_separate")
    revision = document["source_revision"]
    if not isinstance(revision, str) or not REVISION_RE.match(revision):
        raise ReferenceError("manifest_invalid_source_revision")
    for key in ("source_sha256", "weights_sha256", "runtime_sha256",
                "license_sha256", "rights_approval_sha256",
                "transcript_manifest_sha256"):
        value = document[key]
        if not isinstance(value, str) or not HASH_RE.match(value):
            raise ReferenceError("manifest_invalid_sha256:" + key)
    if type(document["terms_accepted"]) is not bool:
        raise ReferenceError("manifest_terms_accepted_is_not_a_boolean")
    if document["terms_accepted"] is not True:
        raise ReferenceError("manifest_terms_not_accepted")
    if document["caller_attestation"] != CALLER_ATTESTATION:
        raise ReferenceError("manifest_caller_attestation_mismatch")
    paths: Dict[str, str] = {}
    for key in ("source_path", "weights_path", "runtime_path", "license_path",
                "rights_approval_path", "transcript_manifest_path"):
        paths[key] = validate_manifest_path(key, document[key])
    if len(set(paths.values())) != len(paths):
        raise ReferenceError("manifest_paths_are_not_distinct")
    normalized = dict(document)
    normalized["paths"] = paths
    normalized["shape_valid"] = True
    normalized["files_verified"] = False
    normalized["loaded"] = False
    normalized["executed"] = False
    normalized["official_identity"] = False
    normalized["asr_proxy_is_listening"] = False
    normalized["qualifies"] = False
    return normalized


def verify_manifest_files(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Hash caller-owned files only; never parse, import or execute them."""
    if not manifest.get("shape_valid"):
        raise ReferenceError("manifest_shape_not_validated")
    for path_key, sha_key in (
            ("source_path", "source_sha256"),
            ("weights_path", "weights_sha256"),
            ("runtime_path", "runtime_sha256"),
            ("license_path", "license_sha256"),
            ("rights_approval_path", "rights_approval_sha256"),
            ("transcript_manifest_path", "transcript_manifest_sha256")):
        path = Path(manifest[path_key])
        if not path.is_file():
            raise ReferenceError("manifest_missing_file:" + path_key)
        if digest_file(path) != manifest[sha_key]:
            raise ReferenceError("manifest_hash_mismatch:" + path_key)
    return {
        "files_verified": True,
        "bytes_hashed_only": True,
        "loaded": False,
        "executed": False,
        "official_identity": False,
        "rights_review_required": True,
        "asr_proxy_is_listening": False,
        "qualifies": False,
    }


def manifest_controls() -> List[Dict[str, Any]]:
    def run(control_id: str,
            mutate: Optional[Callable[[Dict[str, Any]], None]]) -> Dict[str, Any]:
        document = _valid_manifest_document()
        if mutate is not None:
            mutate(document)
        try:
            parse_manifest(document)
        except ReferenceError as error:
            return {
                "control_id": control_id,
                "accepted": False,
                "reason": str(error),
                "shape_only": True,
                "qualifies": False,
            }
        return {
            "control_id": control_id,
            "accepted": True,
            "reason": "shape_valid_files_not_verified",
            "shape_only": True,
            "files_verified": False,
            "official_identity": False,
            "asr_proxy_is_listening": False,
            "qualifies": False,
        }

    def remove(key: str) -> Callable[[Dict[str, Any]], None]:
        def mutate(document: Dict[str, Any]) -> None:
            document.pop(key)
        return mutate

    def set_value(key: str, value: Any) -> Callable[[Dict[str, Any]], None]:
        def mutate(document: Dict[str, Any]) -> None:
            document[key] = value
        return mutate

    def duplicate_paths(document: Dict[str, Any]) -> None:
        document["license_path"] = document["source_path"]

    def listening_not_separate(document: Dict[str, Any]) -> None:
        document["listening_protocol_id"] = document["asr_proxy_scorer_id"]

    controls = [
        run("valid_shape", None),
        run("missing_artifact_id", remove("artifact_id")),
        run("extra_field", set_value("extra", 1)),
        run("wrong_candidate", set_value("candidate_id", "aix-speed")),
        run("wrong_family", set_value("model_family", "AIxSpeed")),
        run("relative_weights_path",
            set_value("weights_path", "aix-speed/weights")),
        run("parent_traversal",
            set_value("weights_path", "/caller/../weights")),
        run("bad_source_revision", set_value("source_revision", "a" * 39)),
        run("uppercase_source_hash", set_value("source_sha256", "E" * 64)),
        run("bad_weights_hash_length", set_value("weights_sha256", "9" * 63)),
        run("duplicate_paths", duplicate_paths),
        run("terms_not_accepted", set_value("terms_accepted", False)),
        run("wrong_attestation", set_value("caller_attestation", "trust_me")),
        run("empty_transcript_cohort",
            set_value("transcript_cohort_id", "")),
        run("missing_asr_proxy_scorer",
            set_value("asr_proxy_scorer_id", "")),
        run("listening_not_separate", listening_not_separate),
        run("listening_not_established",
            set_value("listening_protocol_id", "not_established")),
        run("empty_artifact_id", set_value("artifact_id", "")),
    ]
    return controls


def manifest_contract() -> Dict[str, Any]:
    return {
        "contract_id": (
            "aix-speed-asr-guided-planner/"
            "caller-supplied-qualified-bundle/0.1"
        ),
        "required_fields": list(MANIFEST_FIELDS),
        "checksum_policy": (
            "full_sha256_required_for_source_weights_runtime_license_approval_"
            "and_transcript_manifest"
        ),
        "caller_owned": True,
        "vendored": False,
        "loaded": False,
        "executed": False,
        "official_identity_requires_author_rights_review": True,
        "asr_proxy_and_listening_must_be_separate": True,
        "files_behavior": (
            "hash caller-owned bytes and geometry only; never parse, import, "
            "link or execute the source, weights, runtime or transcript"
        ),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Adverse envelope and manifest controls
# ---------------------------------------------------------------------------

def _mutated_control_segments(
        index: int, key: str, value: Any) -> List[Dict[str, Any]]:
    segments = _control_segment_documents()
    segments[index][key] = value
    return segments


def _rate_case(index: int, numerator: int,
               denominator: int) -> List[Dict[str, Any]]:
    segments = _control_segment_documents()
    segments[index]["rate_numerator"] = numerator
    segments[index]["rate_denominator"] = denominator
    return segments


def _adverse_vectors() -> List[Tuple[str, Any, str, bool]]:
    def envelope(segments: Any) -> Any:
        return segments

    cases: List[Tuple[str, Any, str, bool]] = [
        ("nan_rate_numerator",
         _mutated_control_segments(1, "rate_numerator", float("nan")),
         "rate_numerator_is_not_an_integer", True),
        ("infinity_rate_denominator",
         _mutated_control_segments(1, "rate_denominator", float("inf")),
         "rate_denominator_is_not_an_integer", True),
        ("boolean_rate_numerator",
         _mutated_control_segments(1, "rate_numerator", True),
         "rate_numerator_is_not_an_integer", True),
        ("string_rate_numerator",
         _mutated_control_segments(1, "rate_numerator", "3"),
         "rate_numerator_is_not_an_integer", True),
        ("zero_denominator",
         _mutated_control_segments(1, "rate_denominator", 0),
         "rate_denominator_is_not_positive", True),
        ("negative_numerator",
         _mutated_control_segments(1, "rate_numerator", -3),
         "rate_numerator_is_not_positive", True),
        ("rate_below_floor",
         _mutated_control_segments(2, "rate_numerator", 1),
         "rate_below_declared_floor", True),
        ("rate_above_ceiling",
         _rate_case(1, 4, 2),
         "rate_above_declared_ceiling", True),
        ("speech_speedup",
         _rate_case(3, 6, 5),
         "meaningful_speech_must_not_be_sped_up", True),
        ("silence_slowing",
         _rate_case(0, 4, 5),
         "silence_or_filler_must_not_be_slowed", True),
        ("interval_gap",
         _mutated_control_segments(1, "start_sample", 2401),
         "segment_intervals_have_a_gap", True),
        ("interval_overlap",
         _mutated_control_segments(1, "start_sample", 2399),
         "segment_intervals_overlap", True),
        ("reversed_interval",
         _mutated_control_segments(2, "end_sample_exclusive", 3600),
         "segment_interval_is_empty_or_reversed", True),
        ("uncovered_tail",
         _mutated_control_segments(3, "end_sample_exclusive", 15999),
         "envelope_does_not_cover_total_samples", True),
        ("duplicate_segment_id",
         _mutated_control_segments(1, "segment_id", "seg-00-silence"),
         "segment_id_is_duplicated", True),
        ("nonfinite_asr_score",
         _mutated_control_segments(2, "asr_proxy_score", float("inf")),
         "asr_proxy_score_is_nonfinite", True),
        ("boolean_asr_score",
         _mutated_control_segments(2, "asr_proxy_score", True),
         "asr_proxy_score_is_not_a_real_number", True),
        ("asr_score_out_of_range",
         _mutated_control_segments(2, "asr_proxy_score", 1.5),
         "asr_proxy_score_out_of_range", True),
        ("candidate_claim",
         _mutated_control_segments(2, "is_candidate_result", True),
         "candidate_claim_without_artifact", True),
        ("non_object_segment", ["not-a-segment"],
         "segment_is_not_an_object", True),
        ("empty_envelope", [],
         "envelope_is_empty", True),
        ("mapping_container", {"segments": []},
         "envelope_is_not_a_segment_list", True),
        ("extra_segment_field",
         _mutated_control_segments(0, "extra", 1),
         "segment_extra_fields:extra", True),
        ("unsupported_content_class",
         _mutated_control_segments(2, "content_class", "tone"),
         "unsupported_content_class", True),
    ]
    return cases


def adverse_results() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for result_id, value, expected, _wrapped in _adverse_vectors():
        try:
            validate_envelope(value)
        except ReferenceError as error:
            rows.append({
                "result_id": result_id,
                "status": "rejected",
                "error": str(error),
                "expected": expected,
                "matches_expected": str(error) == expected,
                "qualifies": False,
            })
        else:
            rows.append({
                "result_id": result_id,
                "status": "unexpected_acceptance",
                "error": None,
                "expected": expected,
                "matches_expected": False,
                "qualifies": False,
            })
    return rows


def missing_results() -> List[Dict[str, Any]]:
    items = (
        ("aix_speed_source_revision",
         "Exact AIx Speed source revision or authorized implementation"),
        ("joint_speed_asr_weights",
         "Exact jointly trained speed/ASR weights and full digest"),
        ("asr_runtime_environment",
         "Pinned Wav2Vec2/framework/tokenizer runtime and lock"),
        ("license_and_output_rights",
         "Reviewed paper/code/weight terms and written approval"),
        ("rights_cleared_heldout_transcripts",
         "Held-out transcripts with human-verified phoneme timestamps"),
        ("candidate_rate_envelope",
         "AIx Speed rate envelope on any held-out item"),
        ("asr_proxy_wer_delta_pp",
         "Independent ASR-proxy WER delta"),
        ("asr_proxy_cer_delta_pp",
         "Independent ASR-proxy CER delta"),
        ("duration_pitch_and_transient",
         "Measured duration, drift, pitch and transient audibility"),
        ("playback_buffering_and_final_window",
         "Measured buffering, rebuffer and final partial window"),
        ("device_timing_and_resources",
         "Target-device timing, memory and callback behavior"),
        ("listening_or_comprehension",
         "Authorized blind listening or comprehension result"),
        ("release_decision",
         "Independent exact-head release approval"),
    )
    return [{
        "result_id": result_id,
        "requirement": requirement,
        "value": None,
        "status": "blocked",
        "qualifies": False,
    } for result_id, requirement in items]


def qualification_slots() -> Dict[str, Any]:
    return {
        "candidate_rate_envelope": {
            "value": None,
            "status": "unavailable_aix_speed_source_weights_and_runtime_absent",
            "qualifies": False,
        },
        "asr_proxy_wer_delta_pp": {
            "value": None,
            "status": "unavailable_asr_proxy_scorer_and_heldout_cohort_absent",
            "qualifies": False,
        },
        "asr_proxy_cer_delta_pp": {
            "value": None,
            "status": "unavailable_asr_proxy_scorer_and_heldout_cohort_absent",
            "qualifies": False,
        },
        "duration_error_ms_per_audio_second": {
            "value": None,
            "status": "unavailable_candidate_runtime_absent",
            "qualifies": False,
        },
        "pitch_error_cents": {
            "value": None,
            "status": "unavailable_actuator_and_measurement_harness_absent",
            "qualifies": False,
        },
        "transient_audibility": {
            "value": None,
            "status": "unavailable_actuator_and_listening_assets_absent",
            "qualifies": False,
        },
        "listening_or_comprehension": {
            "value": None,
            "status": "unavailable_panel_authorization_and_assets_absent",
            "qualifies": False,
        },
        "device_timing": {
            "value": None,
            "status": "unavailable_target_device_and_runtime_absent",
            "qualifies": False,
        },
        "release": {
            "value": None,
            "status": "blocked",
            "qualifies": False,
        },
    }


def _rejects(call: Callable[[], Any]) -> bool:
    try:
        call()
    except ReferenceError:
        return True
    return False


def _mutated_manifest(key: str, value: Any) -> Dict[str, Any]:
    document = _valid_manifest_document()
    if value is None:
        document.pop(key, None)
    else:
        document[key] = value
    return document


def failure_controls() -> Dict[str, Any]:
    rejected_envelopes = sum(
        1 for _, value, _, _ in _adverse_vectors()
        if _rejects(lambda value=value: validate_envelope(value))
    )
    controls = manifest_controls()
    rejected_manifests = sum(1 for row in controls if not row["accepted"])
    valid = parse_manifest(_valid_manifest_document())
    missing_file_rejected = _rejects(
        lambda: verify_manifest_files(valid))
    checks = {
        "nan_rate_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(1, "rate_numerator", float("nan")))),
        "infinity_rate_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(1, "rate_denominator", float("inf")))),
        "boolean_rate_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(1, "rate_numerator", True))),
        "string_rate_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(1, "rate_numerator", "3"))),
        "speech_speedup_rejected": _rejects(
            lambda: validate_envelope(_rate_case(3, 6, 5))),
        "silence_slowing_rejected": _rejects(
            lambda: validate_envelope(_rate_case(0, 4, 5))),
        "rate_floor_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(2, "rate_numerator", 1))),
        "rate_ceiling_rejected": _rejects(
            lambda: validate_envelope(_rate_case(1, 4, 2))),
        "interval_gap_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(1, "start_sample", 2401))),
        "interval_overlap_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(1, "start_sample", 2399))),
        "uncovered_tail_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(3, "end_sample_exclusive", 15999))),
        "duplicate_id_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(
                    1, "segment_id", "seg-00-silence"))),
        "nonfinite_score_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(
                    2, "asr_proxy_score", float("inf")))),
        "boolean_score_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(2, "asr_proxy_score", True))),
        "candidate_claim_rejected": _rejects(
            lambda: validate_envelope(
                _mutated_control_segments(
                    2, "is_candidate_result", True))),
        "missing_manifest_field_rejected": _rejects(
            lambda: parse_manifest(_mutated_manifest("source_path", None))),
        "extra_manifest_field_rejected": _rejects(
            lambda: parse_manifest(_mutated_manifest("extra", 1))),
        "relative_manifest_path_rejected": _rejects(
            lambda: parse_manifest(
                _mutated_manifest("weights_path", "relative/weights"))),
        "bad_source_revision_rejected": _rejects(
            lambda: parse_manifest(
                _mutated_manifest("source_revision", "a" * 39))),
        "uppercase_hash_rejected": _rejects(
            lambda: parse_manifest(
                _mutated_manifest("source_sha256", "E" * 64))),
        "terms_not_accepted_rejected": _rejects(
            lambda: parse_manifest(
                _mutated_manifest("terms_accepted", False))),
        "listening_not_separate_rejected": _rejects(
            lambda: parse_manifest(
                _mutated_manifest(
                    "listening_protocol_id", "whisper-proxy-2026"))),
        "missing_manifest_files_rejected": missing_file_rejected,
    }
    return {
        "all_explicit": True,
        "rejected_envelope_documents": rejected_envelopes,
        "rejected_manifest_documents": rejected_manifests,
        "blocked_release_gates": len(RELEASE_GATES),
        "checks": checks,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Evidence reporting
# ---------------------------------------------------------------------------

def acceptance_profile() -> Dict[str, Any]:
    items = [
        {
            "item": "source_output_mapping",
            "status": "synthetic_control_only",
            "evidence": "exact rational source-to-output sample mapping",
            "qualifies": False,
        },
        {
            "item": "duration_identity",
            "status": "synthetic_control_only",
            "evidence": "exact sum(d_i / r_i) == sum(d_i) on the fixture",
            "qualifies": False,
        },
        {
            "item": "unity_1x_control",
            "status": "synthetic_control_only",
            "evidence": "exact 1x identity envelope",
            "qualifies": False,
        },
        {
            "item": "silence_and_filler_policy",
            "status": "synthetic_control_only",
            "evidence": "declared-only 3/2 silence and 6/5 filler on the fixture",
            "qualifies": False,
        },
        {
            "item": "source_timestamp_tied_decisions",
            "status": "synthetic_control_only",
            "evidence": "every control decision is tied to a source sample interval",
            "qualifies": False,
        },
        {
            "item": "final_partial_window",
            "status": "synthetic_control_only",
            "evidence": "control coverage ends exactly at the fixture boundary",
            "qualifies": False,
        },
        {
            "item": "pitch_preservation",
            "status": "blocked",
            "evidence": "no actuator, audio path or pitch measurement",
            "qualifies": False,
        },
        {
            "item": "transient_audibility",
            "status": "blocked",
            "evidence": "no actuator or listening asset",
            "qualifies": False,
        },
        {
            "item": "playback_buffering_and_rebuffer",
            "status": "blocked",
            "evidence": "no playout FIFO, lookahead run or rebuffer injection",
            "qualifies": False,
        },
        {
            "item": "rate_changes_step_and_ramp",
            "status": "blocked",
            "evidence": "no runtime or rate-change trace",
            "qualifies": False,
        },
        {
            "item": "unfamiliar_speech_and_music",
            "status": "blocked",
            "evidence": "no real speech, music or held-out corpus",
            "qualifies": False,
        },
        {
            "item": "drift_over_long_run",
            "status": "blocked",
            "evidence": "no actuator or long-run measurement",
            "qualifies": False,
        },
        {
            "item": "speech_preservation",
            "status": "blocked",
            "evidence": "no candidate output or preservation metric",
            "qualifies": False,
        },
        {
            "item": "asr_proxy_separate_from_listening",
            "status": "blocked",
            "evidence": "both classes are blocked and reported separately",
            "qualifies": False,
        },
        {
            "item": "listening_or_comprehension",
            "status": "blocked",
            "evidence": "no protocol, panel or authorization",
            "qualifies": False,
        },
        {
            "item": "adverse_missing_nonfinite_controls",
            "status": "synthetic_control_only",
            "evidence": "explicit rejection of invalid, nonfinite and blocked cases",
            "qualifies": False,
        },
        {
            "item": "release_and_distribution_terms",
            "status": "blocked",
            "evidence": "no code, weight or output-use approval",
            "qualifies": False,
        },
    ]
    return {
        "profile": PROFILE,
        "items": items,
        "all_qualify": False,
        "missing_result_promoted": False,
        "qualifies": False,
    }


def observed_provenance() -> Dict[str, Any]:
    return {
        "documented_context": [
            {
                "claim_id": "candidate_description",
                "statement": (
                    "AIx Speed chooses playback speed per phoneme using an ASR "
                    "model's recognition score as a proxy for human "
                    "intelligibility."
                ),
                "source": (
                    "cpp-library/pipeline-validation/"
                    "playback-speed-candidates.md:920"
                ),
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "source_reported_outcome",
                "statement": (
                    "The paper reports ~1.3x average speed with lower CER/WER "
                    "than constant-speed playback on a Wav2Vec2-based joint "
                    "speed/ASR design."
                ),
                "source": (
                    "cpp-library/pipeline-validation/"
                    "playback-speed-candidates.md:920"
                ),
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "public_implementation_absent",
                "statement": (
                    "No public AIx Speed implementation was found; the pinned "
                    "note recommends it only as an upper bound, not a first "
                    "build."
                ),
                "source": (
                    "cpp-library/pipeline-validation/"
                    "playback-speed-candidates.md:920,1030"
                ),
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "rate_clamp",
                "statement": (
                    "The first product is clamped to 0.75-1.5x; local ASR "
                    "proxies degraded sharply at 0.5x and 2.5x."
                ),
                "source": (
                    "cpp-library/pipeline-validation/"
                    "playback-speed-candidates.md:486,657,717"
                ),
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "lookahead_design",
                "statement": (
                    "Slowing the start of an utterance requires 200-500 ms of "
                    "lookahead for streaming partials, or 0.5-1 s for reliable "
                    "word timestamps; this is design guidance, not a "
                    "measurement."
                ),
                "source": (
                    "cpp-library/pipeline-validation/"
                    "playback-speed-candidates.md:602,645-649"
                ),
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "local_prescreen_is_a_different_planner",
                "statement": (
                    "The local pre-screen measures D1/D2 with a Vosk gate, "
                    "Whisper tiny.en proxy and Bungee/Signalsmith/Sonic "
                    "actuators; it is not AIx Speed and has no listening "
                    "result."
                ),
                "source": (
                    "cpp-library/pipeline-validation/playback-speed/README.md:1-140"
                ),
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "patent_posture",
                "statement": (
                    "The debt-controller research formulation reads on pending "
                    "US20260075269A1; D1/D2 are the shipping design-arounds and "
                    "AIx Speed is listed as prior art for counsel. No legal "
                    "conclusion is made here."
                ),
                "source": (
                    "cpp-library/pipeline-validation/"
                    "playback-speed-candidates.md:24,930-1001"
                ),
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "claim_id": "inventory_disposition",
                "statement": (
                    "The structured inventory marks the candidate "
                    "evidence_status=considered, disposition=research-control "
                    "and verification_profile=rate."
                ),
                "source": "audio-benchmark-platform/plan/INVENTORY.json",
                "reproduced_here": False,
                "is_measurement": False,
                "is_human_rating": False,
                "qualifies": False,
            },
        ],
        "reproduced_here": False,
        "asr_proxy_is_listening": False,
        "qualifies": False,
    }


def ranking_payload() -> Dict[str, Any]:
    return {
        "order": "not_ranked",
        "recommendation": None,
        "reason": (
            "No AIx Speed source, weights, runtime, held-out transcript "
            "cohort, ASR proxy result or listening result exists; a synthetic "
            "arithmetic control cannot rank the candidate."
        ),
        "qualifies": False,
    }


def build_report_core() -> Dict[str, Any]:
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "title": TITLE,
        "profile": PROFILE,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "proposal_only": PROPOSAL_ONLY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "qualification": QUALIFICATION,
        "task_row": TASK_ROW_IDENTITY,
        "mutable_provenance": MUTABLE_PROVENANCE,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "sibling_pins": SIBLING_PINS,
        "scope": SCOPE,
        "public_surface": PUBLIC_SURFACE,
        "candidate_record": candidate_record(),
        "declared_contract": declared_contract(),
        "manifest_contract": manifest_contract(),
        "required_artifacts": REQUIRED_ARTIFACTS,
        "control_envelope": control_envelope_payload(),
        "manifest_controls": manifest_controls(),
        "adverse_results": adverse_results(),
        "missing_results": missing_results(),
        "qualification_slots": qualification_slots(),
        "failure_controls": failure_controls(),
        "acceptance_profile": acceptance_profile(),
        "observed_provenance": observed_provenance(),
        "artifact_assessment": artifact_assessment(),
        "ranking": ranking_payload(),
        "release_gates": RELEASE_GATES,
        "non_claims": NON_CLAIMS,
        "reproduction": REPRODUCTION,
    }


def build_report() -> Dict[str, Any]:
    first = build_report_core()
    second = build_report_core()
    third = build_report_core()
    digests = [sha256_bytes(canonical_bytes(item))
               for item in (first, second, third)]
    if len(set(digests)) != 1:
        raise ReferenceError("non_deterministic_report")
    report = dict(first)
    report["regeneration"] = {
        "runs": 3,
        "byte_identical": True,
        "canonical_digests": digests,
        "mode": "three_in_process_canonical_builds_plus_cold_start_verify",
    }
    return report


def render_report() -> Tuple[bytes, str, str]:
    report = build_report()
    text, file_digest = canonical_report(report)
    payload = (text + "\n").encode("utf-8")
    canonical_digest = sha256_bytes(canonical_bytes(report))
    return payload, file_digest, canonical_digest


def _local_artifact_names() -> List[str]:
    names: List[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        names.append(path.relative_to(ROOT).as_posix())
    return names


def contract_payload() -> Dict[str, Any]:
    pins: Dict[str, str] = {}
    for name in _local_artifact_names():
        if name in ("contract.json", "SOURCES.sha256"):
            continue
        pins[name] = digest_file(ROOT / name)
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "title": TITLE,
        "profile": PROFILE,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "proposal_only": PROPOSAL_ONLY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "qualification": QUALIFICATION,
        "task_row": TASK_ROW_IDENTITY,
        "mutable_provenance": MUTABLE_PROVENANCE,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "sibling_pins": SIBLING_PINS,
        "scope": SCOPE,
        "public_surface": PUBLIC_SURFACE,
        "candidate_record": candidate_record(),
        "declared_contract": declared_contract(),
        "manifest_contract": manifest_contract(),
        "required_artifacts": REQUIRED_ARTIFACTS,
        "release_gates": RELEASE_GATES,
        "artifact_pins": pins,
        "local_files": list(LOCAL_FILES),
        "reproduction": REPRODUCTION,
        "non_claims": NON_CLAIMS,
    }


def inspect_payload() -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "profile": PROFILE,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "proposal_only": PROPOSAL_ONLY,
        "qualification": QUALIFICATION,
        "candidate_record": candidate_record(),
        "declared_contract": declared_contract(),
        "required_artifacts": [
            {"id": item["id"], "present": item["present"]}
            for item in REQUIRED_ARTIFACTS
        ],
        "control_envelope": {
            "guided_output_samples": (
                control_envelope_payload()["guided"]["total_output_samples"]),
            "guided_average_rate": (
                control_envelope_payload()["guided"]["average_rate"]),
            "guided_min_rate": (
                control_envelope_payload()["guided"]["min_rate"]),
            "guided_max_rate": (
                control_envelope_payload()["guided"]["max_rate"]),
            "asr_proxy_is_listening": False,
            "is_synthetic_control": True,
            "qualifies": False,
        },
        "release_gates": [
            {"id": gate["id"], "status": gate["status"],
             "qualifies": gate["qualifies"]}
            for gate in RELEASE_GATES
        ],
        "scope": SCOPE,
        "public_surface": PUBLIC_SURFACE,
        "qualifies": False,
    }
