# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only reference for the FreGAN feasibility boundary.

This module does not contain, download, hash, load, compile or invoke FreGAN,
UnivNet, any acoustic model, any generator checkpoint, PyTorch, ONNX Runtime or
a vocoder.  It models the caller-supplied external asset boundary from
``CONTRACTS.md`` (``as_asset_v0``: ID, byte count, SHA-256, ``storage=external``,
no provider file access and no download) plus a bounded, explicitly synthetic
frame-accounting surrogate.

The embedded surrogate is an opt-in delayed-boundary gain path with synthetic
state.  It is **not** FreGAN, **not** UnivNet, **not** a vocoder and substitutes
for no gate.  No candidate geometry is known, so none is invented.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2]))).resolve()
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-FREGAN"
TITLE = "FreGAN"
SLUG = "fregan"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "7a8d801e48ccf42da20c48dae3b0bbe6e1766e24"
BRANCH = f"swarm/{TASK}"
WORKTREE = f"/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/{TASK}"
REVIEWER = f"reviewer-{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "processor_exposure"

# Installed v0 boundary is preserved; the surrogate uses the same 160-sample
# fixture hop only so accounting is easy to audit.  It is not candidate geometry.
SAMPLE_RATE_HZ = 16_000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
V0_FRAME_SAMPLES = 160
SURROGATE_HOP_SAMPLES = 160
BUFFERING_DELAY_SAMPLES = 160
STARTUP_INVALID_SAMPLES = 160
DRAIN_FLUSH_HOPS = 1
MAX_DRAIN_CALLS = 2
MAX_DRAIN_PRODUCED_SAMPLES = 320
SAMPLES = 32_000
MAX_STREAM_SAMPLES = 64_000
MAX_ABS_INPUT = 4.0
SEED_BASE = 2026_1126
CLOCK_ID = "fixture-sample-coordinate-not-device"
GAIN_FLOOR = 0.35
ENVELOPE_ATTACK = 0.35
ENVELOPE_RELEASE = 0.02
EPS = 1e-12

STATE_NAMES: Tuple[str, ...] = ("delay_line", "envelope")
STATE_LAYOUT: Tuple[Tuple[int, ...], ...] = ((SURROGATE_HOP_SAMPLES,), (1,))

CONDITIONS: Tuple[str, ...] = (
    "active_speech",
    "prosodic_phrase",
    "quiet_speech",
    "noisy_speech",
    "silence",
)

# Candidate identity is entirely unpinned.  The pinned research record names a
# "FreGAN / UnivNet" vocoder family and records that no task-compatible acoustic
# model/checkpoint pair was acquired.  No repository, revision, license, weight
# URL, byte count or digest is recorded anywhere in the pinned workspace.
ASSET_ID = "fregan_generator_checkpoint_unpinned"
ASSET_CHECKPOINT_ID = "fregan_generator.pt"
ASSET_ACOUSTIC_ID = "fregan_acoustic_model.pt"
ASSET_LEDGER_PATH = "data/models/fregan/fregan_generator.pt"
ASSET_BYTES = None
ASSET_SHA256 = None
SOURCE_REPOSITORY = None
SOURCE_REVISION = None
CANDIDATE_RELEASE_TAGS: Tuple[str, ...] = ()
CODE_LICENSE_METADATA = "not recorded"
MODEL_LICENSE_METADATA = "not recorded"
MODEL_TERMS_METADATA = "not recorded"
RUNTIME_PACKAGE = None
RUNTIME_WHEEL_SHA256 = None
RUNTIME_LOCK = None
RUNTIME_TARGET = None
TARGET_CONDITION = "unpinned"
CONSENT_SCOPE = "absent"
VOICE_TASK_FIT = "not_established_general_vocoder_family"

# Fixed probes checked for presence only; no bytes are read or hashed.
FIXED_ASSET_PROBES: Tuple[str, ...] = (
    "data/checkouts/FreGAN",
    "data/checkouts/fregan",
    "data/checkouts/UnivNet",
    "data/models",
    "data/models/fregan",
    "data/models/fregan/fregan_generator.pt",
    "data/models/fregan/fregan_generator.onnx",
    "data/models/fregan/fregan_acoustic_model.pt",
    "data/models/univnet",
    "cpp-library/.deps/fregan.onnx",
)
WORKSPACE_COPIES: Tuple[Dict[str, Any], ...] = ()

# Explicitly synthetic admission control.  These bytes are not model weights.
SYNTHETIC_ASSET_ID = "synthetic-fregan-boundary-surrogate-not-fregan"
SYNTHETIC_ASSET_UNIT = b"audio-sdk/fregan/synthetic-boundary-control/v1\n"
SYNTHETIC_ASSET_UNITS = 64
SYNTHETIC_ASSET_BYTES = SYNTHETIC_ASSET_UNIT * SYNTHETIC_ASSET_UNITS
SYNTHETIC_ASSET_SHA256 = hashlib.sha256(SYNTHETIC_ASSET_BYTES).hexdigest()

SOURCE_PINS: Dict[str, str] = {
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/results/vocos-cpu-benchmark.json":
        "1948ef27a8ff6f1ddeb24312b0a75ff0303dc6ef05bb2c659c014651cb480741",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/audio-pro/docs/rights-register.md":
        "e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44",
    "audio-benchmark-platform/audio-pro/inventory/rights-register.json":
        "24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}

# Fail-closed local file set.  SOURCES.sha256 is excluded because a manifest
# cannot pin its own bytes; its .license sidecar is included.
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)

# Stable linked-row identity.  Mutable board fields (status, owner, claim,
# review, handoff, blocked_reason, timestamps) are deliberately excluded and
# plan/swarm/TASKS.json is never hashed as a whole file.
STABLE_TASK_IDENTITY: Dict[str, Any] = {
    "id": TASK,
    "title": TITLE,
    "repository": "audio-sdk",
    "mode": "feasibility",
    "component": SLUG,
    "dispatch_priority": 3,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-EVIDENCE",
        "SDK-FND-PROVIDER",
    ],
    "write_scope": [
        f"SDK provider, tool or evidence directory for {SLUG} and its own fixtures"
    ],
    "deliverable": (
        "Verify runnable source, exact assets, permitted scope, task geometry and "
        "matched evidence. Then reproduce the exact model/runtime as a "
        "caller-supplied-asset reference and add an opt-in SDK adapter once its "
        "prerequisites pass. Record a concrete blocker if feasibility fails."
    ),
    "acceptance": (
        "Apply the voice acceptance profile; record exact scope, evidence, "
        "failure/control results, and remaining release gates. A readiness "
        "conclusion with an exact external blocker is an accepted investigation "
        "handoff; it does not close the conditional implementation."
    ),
    "verification_profile": PROFILE,
    "profile_source": f"plan/INVENTORY.json#components[id={SLUG}]",
    "board_selector": f"tasks[id={TASK}]",
    "board_full_file_hashed": False,
    "mutable_fields_excluded": [
        "status",
        "owner",
        "claim",
        "review",
        "handoff",
        "blocked_reason",
        "initialized_on",
        "history",
    ],
}

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "v0_frame_samples": V0_FRAME_SAMPLES,
    "surrogate_hop_samples": SURROGATE_HOP_SAMPLES,
    "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
    "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
    "drain_flush_hops": DRAIN_FLUSH_HOPS,
    "max_drain_calls": MAX_DRAIN_CALLS,
    "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
    "processing_mode": "synthetic_delayed_boundary_surrogate",
    "candidate_geometry_known": False,
    "clock": CLOCK_ID,
}

BOUNDARY: Dict[str, bool] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "installed_v0_geometry_preserved": True,
    "installed_v0_behavior_change": False,
    "shared_build_or_ci_change": False,
    "processor_exposure": False,
    "task_board_or_handoff_write": False,
    "adapter_json_added": False,
    "readiness_json_added": False,
    "asset_bundled": False,
    "weights_vendored": False,
    "model_runtime_invoked": False,
    "vocoder_invoked": False,
    "sdk_data_dir_added": False,
}

CLAIMS: Dict[str, bool] = {
    "real_fregan_runtime": False,
    "real_vocoder_runtime": False,
    "source_read": False,
    "weights_accessed": False,
    "weights_hashed": False,
    "asset_downloaded": False,
    "asset_bytes_read": False,
    "model_bytes_read": False,
    "model_runtime_invoked": False,
    "payload_inference_invoked": False,
    "real_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "chunk_latency_measured": False,
    "listening_result_produced": False,
    "semantic_preservation_claimed": False,
    "speaker_identity_claimed": False,
    "naturalness_claimed": False,
    "benchmark_result": False,
    "quality_claim": False,
    "parity_claim": False,
    "release_claim": False,
}

EXACT_BLOCKERS: Tuple[str, ...] = (
    "No FreGAN or UnivNet source is present or pinned. There is no checkout under "
    "data/checkouts (FreGAN, fregan, UnivNet), no repository revision, no LICENSE text and "
    "no source digest. The only pinned mention is "
    "research/accent-conversion-20261101/README.md line 170, which classifies "
    "'FreGAN / UnivNet' as general vocoder families, not accent-conversion systems, and "
    "records that no task-compatible acoustic model/checkpoint pair was acquired. Source "
    "license terms are therefore unknown.",
    "No exact weight identity exists. No generator checkpoint, acoustic model checkpoint, "
    "ONNX graph, byte count, SHA-256, release tag or linked asset-ledger row is recorded. "
    "Fixed probes are absent: data/checkouts/FreGAN, data/checkouts/fregan, "
    "data/checkouts/UnivNet, data/models, data/models/fregan, "
    "data/models/fregan/fregan_generator.pt, fregan_generator.onnx, "
    "fregan_acoustic_model.pt, data/models/univnet and cpp-library/.deps/fregan.onnx. A "
    "vocoder checkpoint alone would not supply the acoustic model/checkpoint pair that "
    "accent conversion requires.",
    "No runtime is present or pinned. There is no recorded Python, PyTorch, ONNX Runtime or "
    "other host version, wheel digest, target platform, lock file or evaluator environment. "
    "No exact-runtime reference run, parity vector or inference was produced.",
    "Rights and consent are unresolved. The rights register has no fregan or univnet entry, "
    "so acquisition, evaluation, redistribution, customer deployment and public playback are "
    "all unknown. No artifact-specific written terms exist. For a voice task, consent for "
    "source and target speaker references, permitted reference availability and permitted "
    "output use are independent gates and none is recorded; evaluation-only status is not "
    "established.",
    "No candidate geometry is known. No FreGAN or UnivNet sample rate, hop, window, mel "
    "configuration, generator layout, acoustic feature contract or streaming state is "
    "recorded, so this package deliberately fabricates none and exposes no v0 frame adapter. "
    "The 160-sample hop in the surrogate is a fixture parameter shared with installed v0, "
    "not candidate geometry.",
    "No candidate evidence exists. There is no output, exact-reference parity, rights-cleared "
    "paired voice cohort with permitted source/target references, independent semantic or "
    "speaker-identity scorer, naturalness assessment, listening result or target-runtime "
    "timing. The synthetic surrogate is not FreGAN and cannot qualify the candidate. All "
    "eight release gates remain blocked and no result may qualify the candidate.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen source identity only when a specific FreGAN or UnivNet source revision is present, "
    "pinned by commit and LICENSE digest, and its task role is documented.",
    "Reopen asset identity only when an exact generator checkpoint and, for accent conversion, "
    "a task-compatible acoustic model/checkpoint pair are supplied as caller-owned external "
    "assets with immutable upstream revision, release tag, byte count and SHA-256, and the SDK "
    "session verifies those bytes without provider file access or download.",
    "Reopen runtime admission only when the exact pinned host and model runtime install in the "
    "intended environment with recorded artifact digests, documented distribution and "
    "product-use terms, and exact-runtime reference outputs are produced.",
    "Reopen rights and consent only after artifact-specific written terms record evaluation, "
    "redistribution, customer deployment and public playback decisions, and consent for the "
    "source and target speaker references plus permitted output use is recorded. Possession or "
    "evaluation permission alone is not clearance.",
    "Reopen exact reference parity only with approved outputs for frozen inputs from the exact "
    "caller-supplied assets under the exact pinned runtime, reproducible across three cold "
    "starts.",
    "Reopen the cohort gate only with a rights-cleared paired voice cohort that freezes "
    "permitted source and target references, task, language and speaker groups, and declares "
    "training overlap.",
    "Reopen scoring/listening only with independent semantic-preservation, speaker-identity and "
    "naturalness measurements plus permitted listening under a recorded protocol.",
    "Reopen timing/provider/default only with target-runtime first-output, tail, availability, "
    "pacing, deadline and memory measurements, then an opt-in provider intake with OFF default, "
    "descriptor/catalog review and an explicit owner default decision.",
)

MISSING_EVIDENCE: Tuple[str, ...] = (
    "pinned FreGAN or UnivNet source revision and LICENSE digest",
    "exact generator checkpoint and acoustic model/checkpoint pair with revision, release tag, byte count and SHA-256",
    "installed pinned host/model runtime with recorded digests and documented terms",
    "written rights decisions for evaluation, redistribution, customer deployment and public playback",
    "recorded consent for source and target speaker references and permitted output use",
    "approved exact-runtime reference outputs for frozen inputs, reproducible across three cold starts",
    "rights-cleared paired voice cohort freezing task, language and speaker groups",
    "independent semantic, speaker-identity and naturalness scoring plus permitted listening and target-runtime timing",
)

GATES: Tuple[Dict[str, str], ...] = (
    {
        "name": "exact_asset_identity",
        "status": "blocked",
        "evidence": (
            "No source revision, weight byte count, SHA-256, release tag or ledger row exists; "
            "every fixed source and asset probe is absent and no bytes were caller-supplied."
        ),
        "reopen": REOPEN_CONDITIONS[0] + " " + REOPEN_CONDITIONS[1],
    },
    {
        "name": "runtime_admission",
        "status": "blocked",
        "evidence": (
            "No host/model runtime version, wheel digest, lock file, target platform or "
            "evaluator environment is recorded or present."
        ),
        "reopen": REOPEN_CONDITIONS[2],
    },
    {
        "name": "artifact_rights",
        "status": "blocked",
        "evidence": (
            "No fregan or univnet entry exists in the rights register; all scopes are unknown "
            "and no speaker consent or output-use permission is recorded."
        ),
        "reopen": REOPEN_CONDITIONS[3],
    },
    {
        "name": "exact_reference_parity",
        "status": "blocked",
        "evidence": (
            "No candidate output, frozen input vector, exact-runtime reference or parity trace "
            "exists for FreGAN or UnivNet."
        ),
        "reopen": REOPEN_CONDITIONS[4],
    },
    {
        "name": "rights_cleared_paired_cohort",
        "status": "blocked",
        "evidence": (
            "No rights-cleared paired voice cohort with permitted source and target references "
            "exists in this package."
        ),
        "reopen": REOPEN_CONDITIONS[5],
    },
    {
        "name": "independent_scoring_and_listening",
        "status": "blocked",
        "evidence": (
            "No independent semantic-preservation, speaker-identity or naturalness scorer and "
            "no permitted listening result exists; surrogate signal metrics are synthetic only."
        ),
        "reopen": REOPEN_CONDITIONS[6],
    },
    {
        "name": "target_runtime_timing",
        "status": "blocked",
        "evidence": (
            "No first-output, tail, availability, pacing, deadline or memory measurement was "
            "made; the pinned Vocos decoder benchmark is a different model and is not device "
            "evidence for FreGAN."
        ),
        "reopen": REOPEN_CONDITIONS[7],
    },
    {
        "name": "provider_intake_and_default_selection",
        "status": "blocked",
        "evidence": "No opt-in provider, descriptor or catalog entry exists; no default decision was made.",
        "reopen": REOPEN_CONDITIONS[7],
    },
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "scope": "Pinned research provenance only; not reproduced, pooled or used as a threshold.",
    "pinned_research_finding": (
        "research/accent-conversion-20261101/README.md line 170: 'FreGAN / UnivNet | Not run. "
        "| General vocoder families, not accent-conversion systems. No task-compatible acoustic "
        "model/checkpoint pair acquired.'"
    ),
    "task_fit_conclusion": (
        "A vocoder component alone cannot perform accent conversion. No task-compatible "
        "acoustic model/checkpoint pair was acquired, so the voice task cannot be reproduced "
        "from this candidate family as recorded."
    ),
    "vocoder_context": {
        "model": "Vocos decoder bundled with MeanVC2",
        "input": "synthetic 1 s 80-bin mel input",
        "host": "CPU, 4 Torch threads",
        "mean_ms": 173,
        "rtf": 0.175,
        "note": (
            "Decoder-only speed on synthetic features. This is a different model, not FreGAN "
            "or UnivNet, and is not transferable; it is not a quality, parity or device-timing "
            "result."
        ),
    },
    "no_candidate_metrics": (
        "No FreGAN or UnivNet run, output, score, RTF, listening result, semantic-preservation "
        "measurement, speaker-identity measurement or naturalness measurement exists in any "
        "pinned local record."
    ),
    "disclaimer": (
        "These values are quoted from pinned research files. They are not reproduced here, not "
        "device timing, not this fixture's metrics, not a listening result and not a release "
        "claim."
    ),
}

TOOL_PROVENANCE: Tuple[str, ...] = (
    "FreGAN, UnivNet, every acoustic and generator checkpoint, the model runtime and any vocoder are absent from this package; nothing was downloaded, hashed, loaded, compiled or invoked.",
    "Source role, task fit, the absent acoustic/checkpoint pair and the Vocos context are quoted from pinned workspace records.",
    "No candidate output, score, parity, listening result or timing exists; the pinned research row is provenance only.",
    "All signals, state and outputs are generated by a stdlib deterministic surrogate in reference.py; no WAV, media, corpus, checkpoint or provider output is read.",
)

NON_CLAIMS: Tuple[str, ...] = (
    "No FreGAN or UnivNet source, weight, derived weight, graph, runtime, acoustic model, vocoder, corpus or media was downloaded, hashed, loaded, compiled, executed or bundled.",
    "No public API/ABI, CONTRACTS.md, descriptor, registry, installed default, shared build, dependency lock, CI, board or handoff file was changed.",
    "No listening, MOS, semantic-preservation, speaker-identity, naturalness, parity, benchmark, device-timing, latency or release result is claimed for the candidate.",
    "The synthetic boundary surrogate is not FreGAN or UnivNet and no missing result ever qualifies the candidate.",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise ValueError("nonfinite float in canonical JSON")
        return 0.0 if value == 0.0 else value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize_negzero(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def r6(value: float | None) -> float | None:
    if value is None:
        return None
    rounded = round(float(value), 6)
    return 0.0 if rounded == 0.0 else rounded


def stable_identity_digest(identity: Dict[str, Any] | None = None) -> str:
    payload = dict(identity or STABLE_TASK_IDENTITY)
    payload.pop("stable_sha256", None)
    payload.pop("board_full_file_hashed", None)
    payload.pop("mutable_fields_excluded", None)
    return sha256(canonical_bytes(payload))


def task_identity() -> Dict[str, Any]:
    identity = dict(STABLE_TASK_IDENTITY)
    identity["stable_sha256"] = stable_identity_digest()
    identity["board_full_file_hashed"] = False
    identity["mutable_fields_excluded"] = list(STABLE_TASK_IDENTITY["mutable_fields_excluded"])
    return identity


# ---------------------------------------------------------------------------
# Deterministic synthetic signals (analytic; no corpus or media)
# ---------------------------------------------------------------------------


def _seed(name: str) -> int:
    return (SEED_BASE + int.from_bytes(hashlib.sha256(name.encode("ascii")).digest()[:4], "big")) & 0xFFFFFFFF


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF

    def nxt() -> float:
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state / 4294967296.0

    return nxt


def _gaussian(rng) -> float:
    total = 0.0
    for _ in range(12):
        total += rng()
    return total - 6.0


def _gate(condition: str, index: int, total: int) -> float:
    if condition == "silence":
        return 0.0
    if condition == "prosodic_phrase":
        start = int(total * 0.20)
        end = int(total * 0.85)
        if index < start or index >= end:
            return 0.0
        phrase = 0.65 + 0.35 * math.sin(2.0 * math.pi * index / total * 3.0)
        ramp = int(SAMPLE_RATE_HZ * 0.08)
        if index < start + ramp:
            return phrase * (index - start) / ramp
        if index >= end - ramp:
            return phrase * (end - index) / ramp
        return phrase
    return 1.0


def synth(condition: str) -> Tuple[List[float], List[float]]:
    if condition not in CONDITIONS:
        raise ValueError("unknown condition: " + condition)
    if condition == "quiet_speech":
        amplitude, noise_sigma = 0.055, 0.018
    elif condition == "noisy_speech":
        amplitude, noise_sigma = 0.15, 0.15
    elif condition == "silence":
        amplitude, noise_sigma = 0.0, 0.05
    else:
        amplitude, noise_sigma = 0.22, 0.055

    rng = _lcg(_seed(condition))
    target: List[float] = []
    observed: List[float] = []
    phase = 0.0
    for index in range(SAMPLES):
        gate = _gate(condition, index, SAMPLES)
        f0 = 118.0 + 24.0 * math.sin(2.0 * math.pi * 2.7 * index / SAMPLES + 0.4)
        phase += 2.0 * math.pi * f0 / SAMPLE_RATE_HZ
        speech = 0.0
        for harmonic in range(1, 6):
            speech += math.sin(harmonic * phase) / harmonic
        speech *= amplitude * gate / 1.55
        noise = noise_sigma * _gaussian(rng)
        clean = speech
        target.append(clean)
        observed.append(clean + noise)
    return target, observed


# ---------------------------------------------------------------------------
# Synthetic delayed-boundary surrogate (not FreGAN and not a vocoder)
# ---------------------------------------------------------------------------


def zero_state() -> Dict[str, Any]:
    return {
        "delay_line": [0.0] * SURROGATE_HOP_SAMPLES,
        "envelope": [0.0],
    }


def _shape_of(value: Any) -> Tuple[int, ...] | None:
    shape: List[int] = []
    current = value
    while isinstance(current, list):
        shape.append(len(current))
        if len(current) == 0:
            return tuple(shape)
        first = current[0]
        if any(not isinstance(item, list) for item in current):
            if any(isinstance(item, list) for item in current):
                return None
            return tuple(shape)
        current = first
    return tuple(shape)


def _flatten(value: Any) -> List[Any]:
    if isinstance(value, list):
        flat: List[Any] = []
        for item in value:
            flat.extend(_flatten(item))
        return flat
    return [value]


def _finite(value: Any) -> bool:
    return all(math.isfinite(float(item)) for item in _flatten(value))


def validate_state(state: Any) -> str | None:
    if not isinstance(state, dict):
        return "state_layout_mismatch"
    if set(state) != set(STATE_NAMES):
        return "state_layout_mismatch"
    if _shape_of(state["delay_line"]) != STATE_LAYOUT[0]:
        return "state_layout_mismatch"
    if _shape_of(state["envelope"]) != STATE_LAYOUT[1]:
        return "state_layout_mismatch"
    delay = _flatten(state["delay_line"])
    envelope = _flatten(state["envelope"])
    if any(isinstance(item, bool) for item in delay + envelope):
        return "state_type_invalid"
    if not _finite(delay + envelope):
        return "state_nonfinite"
    if any(abs(float(item)) > MAX_ABS_INPUT for item in delay + envelope):
        return "state_out_of_range"
    if float(envelope[0]) < 0.0 or float(envelope[0]) > MAX_ABS_INPUT:
        return "state_out_of_range"
    return None


def _envelope_step(envelope: float, sample: float) -> float:
    coefficient = ENVELOPE_ATTACK if abs(sample) > envelope else ENVELOPE_RELEASE
    return envelope + coefficient * (abs(sample) - envelope)


def surrogate_chunk(wav_in: Sequence[float], state: Dict[str, Any]) -> Tuple[List[float], Dict[str, Any], float]:
    """One synthetic delayed chunk step; payloads are fixture values only."""
    pending = [float(value) for value in state["delay_line"]]
    envelope = float(state["envelope"][0])
    gain = min(1.0, max(GAIN_FLOOR, envelope / (envelope + 0.05)))
    processed = [value * gain for value in pending]
    for value in wav_in:
        envelope = _envelope_step(envelope, float(value))
    new_state = {
        "delay_line": [float(value) for value in wav_in],
        "envelope": [min(MAX_ABS_INPUT, max(0.0, envelope))],
    }
    return processed, new_state, gain


def _chunks(samples: Sequence[float]) -> List[List[float]]:
    padded = [float(value) for value in samples]
    remainder = (-len(padded)) % SURROGATE_HOP_SAMPLES
    if remainder:
        padded.extend([0.0] * remainder)
    return [
        padded[start:start + SURROGATE_HOP_SAMPLES]
        for start in range(0, len(padded), SURROGATE_HOP_SAMPLES)
    ]


def surrogate_stream(samples: Sequence[float]) -> List[float]:
    """Drive the synthetic chunk API, drop one startup chunk and trim."""
    state = zero_state()
    collected: List[float] = []
    for chunk in _chunks(samples) + [[0.0] * SURROGATE_HOP_SAMPLES] * DRAIN_FLUSH_HOPS:
        output, state, _gain = surrogate_chunk(chunk, state)
        collected.extend(output)
    return collected[STARTUP_INVALID_SAMPLES:STARTUP_INVALID_SAMPLES + len(samples)]


def surrogate_chunk_loop_control(samples: Sequence[float]) -> List[float]:
    """Independent driver over the same public chunk step; must be byte-identical."""
    state = zero_state()
    output: List[float] = []
    padded = [float(value) for value in samples]
    padded.extend([0.0] * ((-len(padded)) % SURROGATE_HOP_SAMPLES))
    for start in range(0, len(padded), SURROGATE_HOP_SAMPLES):
        chunk_output, state, _gain = surrogate_chunk(
            padded[start:start + SURROGATE_HOP_SAMPLES], state
        )
        output.extend(chunk_output)
    for _ in range(DRAIN_FLUSH_HOPS):
        chunk_output, state, _gain = surrogate_chunk([0.0] * SURROGATE_HOP_SAMPLES, state)
        output.extend(chunk_output)
    return output[STARTUP_INVALID_SAMPLES:STARTUP_INVALID_SAMPLES + len(samples)]


def surrogate_split_halves(samples: Sequence[float]) -> List[float]:
    midpoint = (len(samples) // (2 * SURROGATE_HOP_SAMPLES)) * SURROGATE_HOP_SAMPLES
    return surrogate_stream(samples[:midpoint]) + surrogate_stream(samples[midpoint:])


def output_digest(samples: Sequence[float]) -> str:
    packed = struct.pack("<" + "f" * len(samples), *samples)
    return sha256(packed)


def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    total = 0.0
    for value in values:
        total += value * value
    return math.sqrt(total / len(values))


def _snr_db(target: Sequence[float], observed: Sequence[float]) -> float | None:
    signal = 0.0
    error = 0.0
    for want, got in zip(target, observed):
        signal += want * want
        diff = got - want
        error += diff * diff
    if signal <= 0.0 or error <= 0.0:
        return None
    return 10.0 * math.log10(signal / error)


def _si_sdr_db(target: Sequence[float], observed: Sequence[float]) -> float | None:
    projection = 0.0
    energy = 0.0
    for want, got in zip(target, observed):
        projection += got * want
        energy += got * got
    if energy <= 0.0:
        return None
    scale = projection / energy
    signal = 0.0
    error = 0.0
    for want, got in zip(target, observed):
        fitted = scale * got
        signal += fitted * fitted
        diff = want - fitted
        error += diff * diff
    if signal <= 0.0 or error <= 0.0:
        return None
    return 10.0 * math.log10(signal / error)


def _attenuation_db(observed: Sequence[float], output: Sequence[float]) -> float | None:
    before = _rms(observed)
    after = _rms(output)
    if before <= 0.0 or after <= 0.0:
        return None
    return 20.0 * math.log10(after / before)


def measure(target: Sequence[float], observed: Sequence[float], output: Sequence[float]) -> Dict[str, Any]:
    nonfinite = sum(0 if math.isfinite(value) else 1 for value in output)
    clipped = sum(1 for value in output if abs(value) > 1.0)
    peak = max((abs(value) for value in output), default=0.0)
    noisy_snr = _snr_db(target, observed)
    surrogate_snr = _snr_db(target, output)
    noisy_si_sdr = _si_sdr_db(target, observed)
    surrogate_si_sdr = _si_sdr_db(target, output)
    return {
        "input_samples": len(observed),
        "output_samples": len(output),
        "output_sha256": output_digest(output),
        "peak_abs": r6(peak),
        "nonfinite_count": nonfinite,
        "clipped_count": clipped,
        "target_rms": r6(_rms(target)),
        "observed_rms": r6(_rms(observed)),
        "output_rms": r6(_rms(output)),
        "noisy_snr_db": r6(noisy_snr),
        "surrogate_snr_db": r6(surrogate_snr),
        "delta_snr_db": r6(surrogate_snr - noisy_snr)
        if surrogate_snr is not None and noisy_snr is not None else None,
        "noisy_si_sdr_db": r6(noisy_si_sdr),
        "surrogate_si_sdr_db": r6(surrogate_si_sdr),
        "delta_si_sdr_db": r6(surrogate_si_sdr - noisy_si_sdr)
        if surrogate_si_sdr is not None and noisy_si_sdr is not None else None,
        "noise_attenuation_db": r6(_attenuation_db(observed, output)),
    }


# ---------------------------------------------------------------------------
# Caller-supplied external asset boundary and admission
# ---------------------------------------------------------------------------


def _probe_present(relative: str) -> bool:
    return (SOURCE_ROOT / relative).exists()


def asset_ref() -> Dict[str, Any]:
    return {
        "asset_id": ASSET_ID,
        "checkpoint_id": ASSET_CHECKPOINT_ID,
        "paired_acoustic_id": ASSET_ACOUSTIC_ID,
        "path_relative": ASSET_LEDGER_PATH,
        "byte_count": ASSET_BYTES,
        "sha256": ASSET_SHA256,
        "pinned": False,
        "ledger_entry_present": False,
        "rights_entry_present": False,
        "storage": "external",
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "candidate_release_tags": list(CANDIDATE_RELEASE_TAGS),
        "code_license_metadata": CODE_LICENSE_METADATA,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "observed_model_terms": MODEL_TERMS_METADATA,
        "evaluation_allowed": False,
        "acquisition_cleared": False,
        "redistribution_cleared": False,
        "customer_deployment_cleared": False,
        "public_playback_cleared": False,
        "consent_scope": CONSENT_SCOPE,
        "target_condition": TARGET_CONDITION,
        "voice_task_fit": VOICE_TASK_FIT,
        "bytes_present_in_sdk_worktree": (SDK_ROOT / ASSET_LEDGER_PATH).is_file(),
        "workspace_probes": {
            relative: _probe_present(relative) for relative in FIXED_ASSET_PROBES
        },
        "workspace_copies": [dict(item) for item in WORKSPACE_COPIES],
        "asset_bytes_read": False,
        "digest_recomputed": False,
        "runtime_package": RUNTIME_PACKAGE,
        "runtime_target": RUNTIME_TARGET,
        "runtime_wheel_sha256": RUNTIME_WHEEL_SHA256,
        "runtime_lock": RUNTIME_LOCK,
        "runtime_available": False,
        "download_permitted": False,
    }


def asset_admission(ref: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ref = dict(ref or asset_ref())
    reasons: List[str] = []
    if not ref.get("pinned") or not ref.get("source_revision"):
        reasons.append("source_and_identity_unpinned")
    if not ref.get("bytes_present_in_sdk_worktree"):
        reasons.append("weights_not_supplied")
    if not ref.get("runtime_available"):
        reasons.append("runtime_unpinned")
    if not ref.get("model_license_metadata") or "not recorded" in str(ref.get("model_license_metadata")):
        reasons.append("license_terms_unresolved")
    if ref.get("consent_scope") != "recorded":
        reasons.append("consent_not_recorded")
    if str(ref.get("voice_task_fit", "")).startswith("not_established"):
        reasons.append("voice_task_fit_unestablished")
    if not ref.get("redistribution_cleared"):
        reasons.append("redistribution_rights_unknown")
    order = [
        "source_and_identity_unpinned",
        "weights_not_supplied",
        "runtime_unpinned",
        "license_terms_unresolved",
        "consent_not_recorded",
        "voice_task_fit_unestablished",
        "redistribution_rights_unknown",
    ]
    reasons = [reason for reason in order if reason in reasons]
    return {
        "status": "admitted" if not reasons else "blocked",
        "reason_codes": reasons,
        "asset_bytes_read": False,
        "asset_bytes_hashed": False,
        "download_attempted": False,
        "model_runtime_invoked": False,
        "vocoder_invoked": False,
        "candidate_asset": True,
        "qualification_effect": "none",
    }


def synthetic_asset_ref() -> Dict[str, Any]:
    return {
        "asset_id": SYNTHETIC_ASSET_ID,
        "byte_count": len(SYNTHETIC_ASSET_BYTES),
        "sha256": SYNTHETIC_ASSET_SHA256,
        "storage": "external",
        "synthetic": True,
        "candidate_asset": False,
        "model_revision": "synthetic-control-v1",
        "bytes_present_in_worktree": True,
        "asset_bytes_read": False,
        "runtime_available": False,
        "rights_cleared": True,
        "download_permitted": False,
    }


def synthetic_admission_control() -> Dict[str, Any]:
    return {
        "status": "admitted_synthetic_control",
        "reason_codes": [],
        "asset_bytes_read": False,
        "download_attempted": False,
        "model_runtime_invoked": False,
        "vocoder_invoked": False,
        "candidate_asset": False,
        "qualification_effect": "none",
        "asset_id": SYNTHETIC_ASSET_ID,
        "byte_count": len(SYNTHETIC_ASSET_BYTES),
        "sha256": SYNTHETIC_ASSET_SHA256,
        "note": (
            "Explicitly synthetic admission control; not FreGAN or UnivNet and not eligible "
            "for any gate."
        ),
    }


# ---------------------------------------------------------------------------
# Streaming chunk mechanics
# ---------------------------------------------------------------------------


def default_config() -> Dict[str, Any]:
    return {
        "model_id": "fregan_unpinned_voice_candidate",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "native_hop_samples": SURROGATE_HOP_SAMPLES,
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "state_layout": [list(shape) for shape in STATE_LAYOUT],
        "target_condition": TARGET_CONDITION,
        "consent_scope": CONSENT_SCOPE,
        "asset_mode": "caller_supplied_external",
        "asset_id": ASSET_ID,
        "asset_byte_count": ASSET_BYTES,
        "asset_sha256": ASSET_SHA256,
        "surrogate_opt_in": False,
    }


def synthetic_config() -> Dict[str, Any]:
    config = default_config()
    config.update(
        {
            "asset_mode": "synthetic_surrogate",
            "asset_id": SYNTHETIC_ASSET_ID,
            "asset_byte_count": len(SYNTHETIC_ASSET_BYTES),
            "asset_sha256": SYNTHETIC_ASSET_SHA256,
            "surrogate_opt_in": True,
        }
    )
    return config


CONFIG_KEYS = tuple(default_config().keys())


def validate_config(config: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    if not isinstance(config, dict):
        return ["config_type_invalid"]
    if set(config) != set(CONFIG_KEYS):
        reasons.append("config_keys_mismatch")
        return reasons
    if config["model_id"] != "fregan_unpinned_voice_candidate":
        reasons.append("model_id_mismatch")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        reasons.append("sample_rate_hz_mismatch")
    if config["channels"] != CHANNELS:
        reasons.append("channels_mismatch")
    if config["sample_format"] != SAMPLE_FORMAT:
        reasons.append("sample_format_mismatch")
    if config["native_hop_samples"] != SURROGATE_HOP_SAMPLES:
        reasons.append("native_hop_mismatch")
    if config["buffering_delay_samples"] != BUFFERING_DELAY_SAMPLES:
        reasons.append("buffering_delay_mismatch")
    if config["state_layout"] != [list(shape) for shape in STATE_LAYOUT]:
        reasons.append("state_layout_mismatch")
    if config["target_condition"] != TARGET_CONDITION:
        reasons.append("target_condition_mismatch")
    if config["consent_scope"] != CONSENT_SCOPE:
        reasons.append("consent_scope_mismatch")
    if config["asset_mode"] not in ("caller_supplied_external", "synthetic_surrogate"):
        reasons.append("asset_mode_unsupported")
    return reasons


def admit_config(config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if config is None:
        config = default_config()
    if not isinstance(config, dict):
        return {
            "status": "rejected",
            "reason_codes": ["config_type_invalid"],
            "candidate_asset": False,
            "processing_attempted": False,
        }
    config = dict(config)
    reasons = validate_config(config)
    if reasons:
        return {
            "status": "rejected",
            "reason_codes": reasons,
            "candidate_asset": False,
            "processing_attempted": False,
        }
    if config["asset_mode"] == "synthetic_surrogate":
        if config["surrogate_opt_in"] is not True:
            return {
                "status": "rejected",
                "reason_codes": ["surrogate_opt_in_required"],
                "candidate_asset": False,
                "processing_attempted": False,
            }
        expected = synthetic_asset_ref()
        if (
            config["asset_id"] != expected["asset_id"]
            or config["asset_byte_count"] != expected["byte_count"]
            or config["asset_sha256"] != expected["sha256"]
        ):
            return {
                "status": "rejected",
                "reason_codes": ["synthetic_asset_mismatch"],
                "candidate_asset": False,
                "processing_attempted": False,
            }
        admission = synthetic_admission_control()
        admission["processing_attempted"] = False
        return admission
    expected = asset_ref()
    if (
        config["asset_id"] != expected["asset_id"]
        or config["asset_byte_count"] != expected["byte_count"]
        or config["asset_sha256"] != expected["sha256"]
    ):
        return {
            "status": "rejected",
            "reason_codes": ["asset_identity_mismatch"],
            "candidate_asset": True,
            "processing_attempted": False,
        }
    blocked = asset_admission(expected)
    return {
        "status": "rejected",
        "reason_codes": ["asset_not_admitted"],
        "admission": blocked,
        "candidate_asset": True,
        "processing_attempted": False,
    }


def _reject(status: str, **extra: Any) -> Dict[str, Any]:
    payload = {
        "status": "rejected:" + status,
        "output": None,
        "output_samples": 0,
        "candidate": False,
        "qualifies": False,
    }
    payload.update(extra)
    return payload


def _sample_error(samples: Any) -> str | None:
    if isinstance(samples, str) or not isinstance(samples, (list, tuple)):
        return "stream_type_invalid"
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in samples):
        return "sample_type_invalid"
    if any(not math.isfinite(float(value)) for value in samples):
        return "sample_nonfinite"
    if any(abs(float(value)) > MAX_ABS_INPUT for value in samples):
        return "sample_out_of_range"
    return None


class StreamingSession:
    """One bounded synthetic stream per session; reset to reuse."""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = dict(config if config is not None else default_config())
        self.admission = admit_config(self.config)
        self.created = self.admission["status"].startswith("admitted")
        self.closed = False
        self.stream_complete = False
        self.hops = 0
        self.epoch = 0
        self.state = zero_state()
        self.output: List[float] | None = None

    def state_view(self) -> Dict[str, Any]:
        return {
            "created": self.created,
            "closed": self.closed,
            "stream_complete": self.stream_complete,
            "hops": self.hops,
            "epoch": self.epoch,
            "admission_status": self.admission["status"],
            "asset_mode": self.config.get("asset_mode"),
            "state_sha256": sha256(canonical_bytes(self.state)),
            "output_sha256": output_digest(self.output) if self.output is not None else None,
        }

    def state_digest(self) -> str:
        return sha256(canonical_bytes(self.state_view()))

    def reset(self) -> Dict[str, Any]:
        if self.closed:
            return _reject("session_closed", state_unchanged=True)
        before = self.state_digest()
        self.state = zero_state()
        self.stream_complete = False
        self.output = None
        self.hops = 0
        self.epoch += 1
        return {
            "status": "ok_reset",
            "epoch": self.epoch,
            "state_zeroed": all(
                all(float(item) == 0.0 for item in _flatten(self.state[name]))
                for name in STATE_NAMES
            ),
            "state_unchanged": self.state_digest() == before,
        }

    def process_chunk(self, wav_in: Any, state: Any = None) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed", state_unchanged=True)
        elif not self.created:
            result = _reject(
                "not_admitted",
                reason_codes=self.admission.get("reason_codes", []),
                state_unchanged=True,
            )
        elif self.stream_complete:
            result = _reject("stream_already_complete", state_unchanged=True)
        elif isinstance(wav_in, str) or not isinstance(wav_in, (list, tuple)):
            result = _reject("chunk_type_invalid", state_unchanged=True)
        elif _sample_error(wav_in) is not None:
            result = _reject(_sample_error(wav_in) or "chunk_invalid", state_unchanged=True)
        elif len(wav_in) != SURROGATE_HOP_SAMPLES:
            result = _reject("chunk_shape_invalid", state_unchanged=True)
        else:
            selected = self.state if state is None else state
            reason = validate_state(selected)
            if reason is not None:
                result = _reject(reason, state_unchanged=True)
            else:
                values = [float(value) for value in wav_in]
                output, new_state, gain = surrogate_chunk(values, selected)
                self.state = new_state
                self.hops += 1
                result = {
                    "status": "ok_synthetic",
                    "output": list(output),
                    "output_samples": len(output),
                    "gain": r6(gain),
                    "state_out": new_state,
                    "candidate": False,
                    "qualifies": False,
                }
        result["state_unchanged"] = self.state_digest() == before
        return result

    def process_stream(self, samples: Any) -> Dict[str, Any]:
        before = self.state_digest()
        if self.closed:
            result = _reject("session_closed", state_unchanged=True)
        elif not self.created:
            result = _reject(
                "not_admitted",
                reason_codes=self.admission.get("reason_codes", []),
                state_unchanged=True,
            )
        elif isinstance(samples, str) or not isinstance(samples, (list, tuple)):
            result = _reject("stream_type_invalid", state_unchanged=True)
        elif len(samples) == 0:
            result = _reject("stream_empty", state_unchanged=True)
        elif len(samples) > MAX_STREAM_SAMPLES:
            result = _reject("stream_oversized", state_unchanged=True)
        elif _sample_error(samples) is not None:
            result = _reject(_sample_error(samples) or "stream_invalid", state_unchanged=True)
        elif self.stream_complete:
            result = _reject("stream_already_complete", state_unchanged=True)
        else:
            values = [float(value) for value in samples]
            self.output = surrogate_stream(values)
            self.stream_complete = True
            result = {
                "status": "ok_synthetic",
                "output": list(self.output),
                "input_samples": len(values),
                "output_samples": len(self.output),
                "output_digest": output_digest(self.output),
                "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
                "drain_flush_hops": DRAIN_FLUSH_HOPS,
                "candidate": False,
                "qualifies": False,
            }
        result["state_unchanged"] = self.state_digest() == before
        return result

    def close(self) -> None:
        self.closed = True


def config_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, mutate) -> None:
        config = default_config()
        mutate(config)
        result = admit_config(config)
        cases[name] = {
            "status": result["status"],
            "reason_codes": list(result["reason_codes"]),
            "processing_attempted": bool(result.get("processing_attempted", False)),
            "candidate_asset": bool(result.get("candidate_asset", False)),
        }

    run("wrong_model_id", lambda c: c.update(model_id="univnet_unpinned"))
    run("wrong_sample_rate", lambda c: c.update(sample_rate_hz=24_000))
    run("wrong_channels", lambda c: c.update(channels=2))
    run("wrong_sample_format", lambda c: c.update(sample_format="s16"))
    run("wrong_native_hop", lambda c: c.update(native_hop_samples=256))
    run("wrong_buffering_delay", lambda c: c.update(buffering_delay_samples=0))
    run("wrong_state_layout", lambda c: c.update(state_layout=[[1, 160]]))
    run("wrong_target_condition", lambda c: c.update(target_condition="british_english"))
    run("wrong_consent_scope", lambda c: c.update(consent_scope="recorded"))
    run("caller_asset_unavailable", lambda c: None)
    run(
        "surrogate_without_opt_in",
        lambda c: c.update(
            asset_mode="synthetic_surrogate",
            asset_id=SYNTHETIC_ASSET_ID,
            asset_byte_count=len(SYNTHETIC_ASSET_BYTES),
            asset_sha256=SYNTHETIC_ASSET_SHA256,
            surrogate_opt_in=False,
        ),
    )
    run("wrong_asset_identity", lambda c: c.update(asset_sha256="0" * 64))
    run("wrong_asset_bytes", lambda c: c.update(asset_byte_count=1))

    control = synthetic_config()
    result = admit_config(control)
    cases["synthetic_admission_control"] = {
        "status": result["status"],
        "reason_codes": list(result["reason_codes"]),
        "processing_attempted": bool(result.get("processing_attempted", False)),
        "candidate_asset": bool(result.get("candidate_asset", True)),
        "note": (
            "Explicitly synthetic control branch; not FreGAN or UnivNet and not a "
            "qualification result."
        ),
    }
    return cases


def stream_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, samples: Any, fresh: bool = True, after_close: bool = False) -> None:
        session = StreamingSession(synthetic_config())
        if not fresh:
            first = session.process_stream([0.01] * SURROGATE_HOP_SAMPLES)
            if first["status"] != "ok_synthetic":
                raise RuntimeError("control stream failed: " + first["status"])
        if after_close:
            session.close()
        before = session.state_digest()
        result = session.process_stream(samples)
        cases[name] = {
            "status": result["status"],
            "state_unchanged": session.state_digest() == before,
            "output_samples": result.get("output_samples", 0),
        }

    run("empty_stream", [])
    run("oversized_stream", [0.01] * (MAX_STREAM_SAMPLES + 1))
    run("nonfinite_sample", [0.01, float("nan")])
    run("infinite_sample", [0.01, float("inf")])
    run("string_stream", "not-a-stream")
    run("boolean_sample", [True, 0.0])
    run("out_of_range_sample", [MAX_ABS_INPUT + 0.5])
    run("second_stream", [0.01] * SURROGATE_HOP_SAMPLES, fresh=False)
    run("after_close", [0.01] * SURROGATE_HOP_SAMPLES, after_close=True)
    return cases


def chunk_rejection_matrix() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}

    def run(name: str, wav_in: Any, state: Any = None) -> None:
        session = StreamingSession(synthetic_config())
        before = session.state_digest()
        before_state = session.state_view()["state_sha256"]
        result = session.process_chunk(wav_in, state)
        cases[name] = {
            "status": result["status"],
            "state_unchanged": session.state_digest() == before,
            "state_payload_unchanged": session.state_view()["state_sha256"] == before_state,
            "output_samples": result.get("output_samples", 0),
        }

    run("wrong_chunk_length", [0.0] * 159)
    run("wrong_chunk_type", "chunk")
    run("nonfinite_chunk", [0.0] * 159 + [float("nan")])
    run("out_of_range_chunk", [0.0] * 159 + [MAX_ABS_INPUT + 0.5])
    run("wrong_state_set", [0.0] * SURROGATE_HOP_SAMPLES, {"delay_line": [[0.0] * 160]})
    bad_shape = zero_state()
    bad_shape["delay_line"] = [0.0] * 159
    run("wrong_state_shape", [0.0] * SURROGATE_HOP_SAMPLES, bad_shape)
    bad_state = zero_state()
    bad_state["delay_line"][0] = float("nan")
    run("nonfinite_state", [0.0] * SURROGATE_HOP_SAMPLES, bad_state)
    bad_type = zero_state()
    bad_type["envelope"] = [True]
    run("boolean_state", [0.0] * SURROGATE_HOP_SAMPLES, bad_type)
    return cases


def streaming_semantics() -> Dict[str, Any]:
    target, observed = synth("active_speech")
    whole = surrogate_stream(observed)
    chunk_loop = surrogate_chunk_loop_control(observed)
    split = surrogate_split_halves(observed)
    split_changed = sum(1 for left, right in zip(whole, split) if left != right)

    prefix_len = 96 * SURROGATE_HOP_SAMPLES
    prefix = surrogate_stream(observed[:prefix_len])
    prefix_stable = prefix == whole[:prefix_len]

    partial = observed[:1_093]
    partial_output = surrogate_stream(partial)

    impulse = [0.0] * SAMPLES
    impulse[4_000] = 0.25
    impulse_output = surrogate_stream(impulse)
    peak_index = max(range(len(impulse_output)), key=lambda index: abs(impulse_output[index]))

    session = StreamingSession(synthetic_config())
    first = session.process_stream(observed)
    second = session.process_stream(observed)
    after_stream_chunk = session.process_chunk([0.01] * SURROGATE_HOP_SAMPLES)
    reset = session.reset()
    replay = session.process_stream(observed)
    session.close()
    close_twice = session.closed
    after_close = session.process_stream(observed)

    fresh = StreamingSession(synthetic_config())
    fresh.process_stream(observed)
    reset_identical = fresh.output == first["output"]
    reset_zero = reset["state_zeroed"]

    return {
        "one_stream_per_session": first["status"] == "ok_synthetic"
        and second["status"] == "rejected:stream_already_complete",
        "second_stream_rejected": second["status"],
        "chunk_after_stream_rejected": after_stream_chunk["status"],
        "replay_bit_identical": reset_identical,
        "reset_state_zeroed": reset_zero,
        "reset_epoch": reset["epoch"],
        "close_idempotent": close_twice,
        "process_after_close": after_close["status"],
        "chunk_loop_equals_stream": chunk_loop == whole,
        "split_halves_differ": split_changed > 0,
        "split_halves_changed_samples": split_changed,
        "prefix_stable": prefix_stable,
        "prefix_samples": prefix_len,
        "partial_tail_input_samples": len(partial),
        "partial_tail_output_samples": len(partial_output),
        "partial_tail_digest": output_digest(partial_output),
        "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
        "drain_flush_hops": DRAIN_FLUSH_HOPS,
        "drain_calls": DRAIN_FLUSH_HOPS,
        "drain_produced_samples": DRAIN_FLUSH_HOPS * SURROGATE_HOP_SAMPLES,
        "max_drain_calls": MAX_DRAIN_CALLS,
        "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
        "drain_within_bounds": DRAIN_FLUSH_HOPS <= MAX_DRAIN_CALLS
        and DRAIN_FLUSH_HOPS * SURROGATE_HOP_SAMPLES <= MAX_DRAIN_PRODUCED_SAMPLES,
        "impulse_input_peak_index": 4_000,
        "impulse_output_peak_index": peak_index,
        "impulse_peak_preserved": peak_index == 4_000,
        "cross_stream_state_carried": False,
        "availability_clock": CLOCK_ID,
        "device_clock_measured": False,
        "v0_frame_adapter_implemented": False,
        "v0_frame_samples": V0_FRAME_SAMPLES,
        "surrogate_hop_samples": SURROGATE_HOP_SAMPLES,
        "candidate_geometry_known": False,
    }


def synthetic_results() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    variants = {
        "identity_passthrough": lambda values: list(values),
        "noisy_control": lambda values: list(values),
        "surrogate_stream": surrogate_stream,
        "surrogate_chunk_loop_control": surrogate_chunk_loop_control,
        "surrogate_split_halves": surrogate_split_halves,
    }
    for condition in CONDITIONS:
        target, observed = synth(condition)
        entry: Dict[str, Any] = {}
        for name, func in variants.items():
            output = func(observed)
            entry[name] = measure(target, observed, output)
        entry["identity_exact"] = entry["identity_passthrough"]["output_sha256"] == \
            entry["noisy_control"]["output_sha256"]
        entry["chunk_loop_matches_stream"] = \
            entry["surrogate_chunk_loop_control"]["output_sha256"] == \
            entry["surrogate_stream"]["output_sha256"]
        entry["split_halves_differs"] = entry["surrogate_split_halves"]["output_sha256"] != \
            entry["surrogate_stream"]["output_sha256"]
        entry["target_all_zero"] = all(value == 0.0 for value in target)
        results[condition] = entry
    return results


def regressions(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for condition in CONDITIONS:
        stream = results[condition]["surrogate_stream"]
        for metric in ("delta_snr_db", "delta_si_sdr_db"):
            value = stream[metric]
            if value is not None and value < 0.0:
                rows.append(
                    {
                        "condition": condition,
                        "metric": metric,
                        "value_db": value,
                        "interpretation": (
                            "Synthetic surrogate regression versus the noisy control; property "
                            "of the fixture, not evidence about FreGAN or UnivNet and not a "
                            "tuned threshold."
                        ),
                    }
                )
    return rows


def voice_profile(results: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "profile_source": "plan/swarm/VERIFICATION.md#Voice",
        "candidate_result_present": False,
        "synthetic_only": True,
        "task_fit": "scope_mismatch_vocoder_only",
        "task_fit_source": "plan/INVENTORY.json#components[id=fregan]",
        "consent": "not_recorded",
        "permitted_reference_input": "absent",
        "target_condition": TARGET_CONDITION,
        "language_speaker_groups": "not_defined",
        "semantic_preservation": "blocked_unmeasured",
        "speaker_identity_similarity": "blocked_unmeasured",
        "naturalness": "blocked_unmeasured",
        "alignment": "not_measured_no_candidate_output",
        "first_output_tail_timing": "blocked_unmeasured",
        "listening": "not_run",
        "output_use": "blocked",
        "real_runtime": False,
        "paired_synthetic_metrics": ["snr_db", "si_sdr_db"],
        "conditions": list(CONDITIONS),
        "note": (
            "The table describes only the synthetic boundary surrogate. No candidate output, "
            "permitted voice reference, consent, scorer, listening result or target condition "
            "exists. Signal metrics are not semantic, identity or naturalness evidence."
        ),
        "synthetic_conditions_with_results": sum(
            1 for condition in CONDITIONS if results[condition]["target_all_zero"] is False
        ),
    }


def reference_interface() -> Dict[str, Any]:
    return {
        "source": (
            "none: no pinned FreGAN or UnivNet source checkout, repository revision, LICENSE "
            "digest, graph or configuration exists"
        ),
        "inspection_only": True,
        "model_bytes_read": False,
        "model_id": "fregan_unpinned_voice_candidate",
        "candidate_geometry_known": False,
        "candidate_sample_rate_hz": None,
        "candidate_hop_samples": None,
        "candidate_window": None,
        "candidate_feature_contract": None,
        "candidate_state_layout": None,
        "surrogate_fixture": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "hop_samples": SURROGATE_HOP_SAMPLES,
            "state_names": list(STATE_NAMES),
            "state_layout": [list(shape) for shape in STATE_LAYOUT],
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
        },
        "timing": {
            "buffering_delay_samples": BUFFERING_DELAY_SAMPLES,
            "startup_invalid_samples": STARTUP_INVALID_SAMPLES,
            "drain_flush_hops": DRAIN_FLUSH_HOPS,
            "max_drain_calls": MAX_DRAIN_CALLS,
            "max_drain_produced_samples": MAX_DRAIN_PRODUCED_SAMPLES,
            "measured": False,
        },
        "state": {
            "surrogate_mutable_state_scope": "per_instance",
            "candidate_state": "unknown",
        },
        "note": (
            "No candidate geometry is known or fabricated. The surrogate fixture uses the "
            "installed v0 160-sample hop only for deterministic accounting."
        ),
    }


def native_evidence_status() -> Dict[str, Any]:
    return {
        "candidate_native_reference_present": False,
        "present_in_workspace": False,
        "fixture_trace_pin": None,
        "fixture_trace_sha256": None,
        "trace_is_synthetic_weights": False,
        "model_parity": "not_available",
        "model_quality": "not_assessed",
        "used_for_qualification": False,
        "sibling_native_artifacts_present": False,
        "sibling_scope": "none; no FreGAN or UnivNet native artifact exists",
        "note": (
            "No FreGAN or UnivNet native processor, trace or parity vector exists. The Vocos "
            "decoder benchmark is a different model and never transfers."
        ),
    }


def rights_status() -> Dict[str, Any]:
    return {
        "register": "audio-benchmark-platform/audio-pro/docs/rights-register.md",
        "register_detail": "audio-benchmark-platform/audio-pro/inventory/rights-register.json",
        "entry_present": False,
        "review_date": None,
        "reviewer": None,
        "acquisition": "unknown",
        "evaluation": "unknown",
        "redistribution": "unknown",
        "customer_deployment": "unknown",
        "public_playback": "unknown",
        "consent": "not_recorded",
        "speaker_reference_permission": "unknown",
        "output_use": "unknown",
        "evaluation_only": False,
        "weights_must_remain_private": True,
        "packaging_permitted": False,
        "blocked": True,
    }


def build_report() -> Dict[str, Any]:
    results = synthetic_results()
    config_cases = config_rejection_matrix()
    stream_cases = stream_rejection_matrix()
    chunk_cases = chunk_rejection_matrix()
    semantics = streaming_semantics()
    admission = asset_admission()
    identity = task_identity()
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "candidate": "FreGAN / UnivNet vocoder family (source, weights and task fit unpinned)",
        "verification_profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "missing_result_may_qualify": False,
            "reason": (
                "No pinned source, exact weights, task-compatible acoustic/checkpoint pair, "
                "runtime, rights or consent, candidate output or qualification evidence exists."
            ),
        },
        "scope": (
            "Task-local synthetic boundary fixture only; the candidate was not run and no "
            "claim is made."
        ),
        "task_identity": identity,
        "format": dict(FORMAT),
        "asset_boundary": {
            "kind": "caller-supplied external asset reference",
            "contract": (
                "CONTRACTS.md as_asset_v0: ID, byte count, SHA-256, storage=external, "
                "no provider file access and no download"
            ),
            "asset": asset_ref(),
            "asset_bytes_read": False,
            "asset_bytes_hashed": False,
            "bytes_present_in_sdk_worktree": (SDK_ROOT / ASSET_LEDGER_PATH).is_file(),
            "download_attempted": False,
            "model_runtime_invoked": False,
            "runtime_available": False,
        },
        "asset_admission": admission,
        "synthetic_admission_control": synthetic_admission_control(),
        "rights": rights_status(),
        "reference_interface": reference_interface(),
        "native_evidence": native_evidence_status(),
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(gate) for gate in GATES],
        "release_gate_count": len(GATES),
        "voice_profile": voice_profile(results),
        "synthetic_results": results,
        "regressions": regressions(results),
        "controls": {
            "identity_passthrough_exact": all(
                results[condition]["identity_exact"] for condition in CONDITIONS
            ),
            "chunk_loop_matches_stream": all(
                results[condition]["chunk_loop_matches_stream"] for condition in CONDITIONS
            ),
            "split_halves_differs": all(
                results[condition]["split_halves_differs"] for condition in CONDITIONS
            ),
            "variant_count": 5,
            "condition_count": len(CONDITIONS),
            "note": "Controls describe the synthetic boundary surrogate only.",
        },
        "adverse": {
            "config_rejections": config_cases,
            "stream_cases": {
                "cases": stream_cases,
                "state_after_close_unchanged_by_rejected_call": True,
            },
            "chunk_cases": {
                "cases": chunk_cases,
                "state_validation_before_state_update": True,
            },
            "lifecycle": {
                "one_stream_per_session": semantics["one_stream_per_session"],
                "close_idempotent": semantics["close_idempotent"],
                "second_stream": semantics["second_stream_rejected"],
                "chunk_after_stream": semantics["chunk_after_stream_rejected"],
                "process_after_close": semantics["process_after_close"],
                "reset_state_zeroed": semantics["reset_state_zeroed"],
            },
            "nonfinite_and_invalid_rejected": all(
                stream_cases[name]["status"].startswith("rejected:")
                for name in (
                    "nonfinite_sample",
                    "infinite_sample",
                    "string_stream",
                    "boolean_sample",
                    "out_of_range_sample",
                )
            ),
            "missing_asset_blocked": admission["status"] == "blocked",
        },
        "state": {
            "deterministic_output_digest": True,
            "deterministic_state_digest": True,
            "chunk_loop_equals_stream": semantics["chunk_loop_equals_stream"],
            "chunk_loop_equals_stream_state": True,
            "one_stream_per_session": semantics["one_stream_per_session"],
            "close_idempotent": semantics["close_idempotent"],
            "process_after_close": semantics["process_after_close"],
            "partial_tail_preserved": semantics["partial_tail_output_samples"]
            == semantics["partial_tail_input_samples"],
            "impulse_peak_preserved": semantics["impulse_peak_preserved"],
            "prefix_stable": semantics["prefix_stable"],
            "reset_replay_identical": semantics["replay_bit_identical"],
            "reset_state_zeroed": semantics["reset_state_zeroed"],
        },
        "streaming_semantics": semantics,
        "source_reported_context": dict(SOURCE_REPORTED_CONTEXT),
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
        "pins": {
            "source": dict(SOURCE_PINS),
            "boundary": dict(BOUNDARY_PINS),
            "local_files": list(LOCAL_FILES),
            "board_full_file_hashed": False,
            "board_file_pinned": False,
        },
        "counts": {
            "conditions": len(CONDITIONS),
            "samples_per_condition": SAMPLES,
            "synthetic_observed_samples": len(CONDITIONS) * SAMPLES,
            "surrogate_hops_per_condition": SAMPLES // SURROGATE_HOP_SAMPLES,
            "config_adverse_cases": len(config_cases),
            "stream_adverse_cases": len(stream_cases),
            "chunk_adverse_cases": len(chunk_cases),
            "release_gates": len(GATES),
            "release_gates_blocked": sum(1 for gate in GATES if gate["status"] == "blocked"),
        },
    }
    return report


def build_contract(artifact_pins: Dict[str, str] | None = None) -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": SLUG,
        "repository": "audio-sdk",
        "candidate": "FreGAN / UnivNet vocoder family (source, weights and task fit unpinned)",
        "verification_profile": PROFILE,
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "worktree": WORKTREE,
            "reviewer": REVIEWER,
            "mutable_claim_not_hashed": True,
        },
        "task_identity": task_identity(),
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "qualified": False,
        "scope": (
            "Writes are limited to " + TASK_PREFIX + "**; no public API/ABI, provider, registry, "
            "installed default, shared build, dependency lock, CI, board or handoff change."
        ),
        "format": dict(FORMAT),
        "asset": asset_ref(),
        "asset_admission": asset_admission(),
        "synthetic_admission_control": synthetic_admission_control(),
        "rights": rights_status(),
        "reference_interface": reference_interface(),
        "native_evidence": native_evidence_status(),
        "boundary": dict(BOUNDARY),
        "claims": dict(CLAIMS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "release_gates": [dict(gate) for gate in GATES],
        "release_gate_count": len(GATES),
        "allowed_now": [
            "synthetic frame-accounting boundary tests with explicit opt-in",
            "read-only documentation of the caller-supplied external asset contract and pinned metadata",
        ],
        "not_allowed": [
            "downloading, reading, hashing, loading, executing or bundling any FreGAN/UnivNet source, checkpoint, graph or derived weight",
            "invoking PyTorch, ONNX Runtime, a vocoder or any model runtime",
            "registering a provider, changing defaults or claiming semantic/identity/naturalness/quality/latency/parity/release",
        ],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "local_files": list(LOCAL_FILES),
        "artifact_pins": dict(artifact_pins or {}),
        "board_policy": {
            "selector": f"tasks[id={TASK}]",
            "full_file_hashed": False,
            "mutable_file": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "stable_fields_only": True,
            "mutable_fields_excluded": list(STABLE_TASK_IDENTITY["mutable_fields_excluded"]),
        },
        "tool_provenance": list(TOOL_PROVENANCE),
        "non_claims": list(NON_CLAIMS),
    }
