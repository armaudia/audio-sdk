# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only AECMOS input-contract reference (DEFER package).

This is a *proposal-only* evidence-profile package.  It does **not** contain,
link, download, install, execute or emulate Microsoft's AECMOS model, the
official AEC-Challenge inference source, ONNX Runtime, librosa or numpy.  It
reproduces only the documented **input/feature geometry** requested by the
local adapter: three 16 kHz mono streams (lpb, microphone, enhanced), a 20 s
truncation, a 513-point STFT with a 256-sample hop, 160 mel bands, a 20-frame
scenario marker, a 20-frame zero terminator and a zero GRU state of shape
(4, 1, 64) with two outputs (echo, degradation).

Every score slot is ``None`` with an explicit ``unavailable`` status.  The
package exists so the exact missing weights, source revision, runtime and
rights-cleared cohort are recorded and cannot be mistaken for a result.  No
synthetic number here is an AECMOS prediction, a MOS, a human rating, a
benchmark, a device measurement or a release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]

TASK_ID = "SDK-AECMOS"
COMPONENT = "aecmos"
BASE_COMMIT = "3b581c09115f36408f77bf6a5c8ebd7389b9fb7b"
BRANCH = "swarm/SDK-AECMOS"
SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "evidence"
STATUS = "proposal_only_not_qualified"
COMPLETENESS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
LOCAL_IDENTITY = "aecmos-input-contract-geometry-reference-v1"

# Installed v0 stays untouched; these are recorded for boundary clarity only.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160

# AECMOS v4 16 kHz input geometry, taken from the pinned local adapter.
N_FFT = 513
HOP_LENGTH = 256
N_MELS = 160
FFT_BINS = N_FFT // 2 + 1  # 257 real rFFT bins
MAX_SECONDS = 20
MAX_SAMPLES = MAX_SECONDS * SAMPLE_RATE_HZ  # 320000
MARKER_FRAMES = 20
TERMINATOR_FRAMES = 20
GRU_STATE_SHAPE = (4, 1, 64)
STREAM_ORDER = ("lpb", "microphone", "enhanced")
TALK_TYPES = ("st", "nst", "dt")
OUTPUT_NAMES = ("aecmos_echo", "aecmos_degradation")
FEATURE_NORMALIZATION = "(power_to_db(mel, ref=np.max) + 40.0) / 40.0"
FRAME_COUNT_RULE = "1 + (n - 1) // hop_length"
MAX_ABS_INPUT = 8.0

AECMOS_MODEL_FILENAME = "Run_1663915512_Stage_0.onnx"
AECMOS_MODEL_SHA256 = (
    "f53122f43cb7e5b77ec797e85c8b997cfc2aac8220857c709226d876de8c0a99"
)
AECMOS_MODEL_PATH = "data/models/aecmos/" + AECMOS_MODEL_FILENAME

# Frozen deterministic synthetic fixture.  1.2 s is long enough for the marker
# and terminator geometry and short enough to keep pure-Python regeneration
# bounded; it is not a corpus and not speech.
FIXTURE_SAMPLES = 19200
FIXTURE_FRAMES = FIXTURE_SAMPLES // FRAME_SAMPLES
RENDER_SEED = 439041101
NEAR_SEED = 1584361601
NOISE_SEED = 2596069104
RENDER_NOISE_SEED = 907633385
ECHO_TAPS = {7: 0.72, 15: 0.45, 29: 0.22, 47: 0.11}
DELAYED_ENHANCED_SAMPLES = 128
DROPOUT_START_FRAME = 30
DROPOUT_END_FRAME = 40

SOURCE_PINS: Dict[str, str] = {
    "research/aec_research_20261028.md":
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180",
    "adapters/aecmos/run.py":
        "5add699066f267a68bc44bfb114d0e1f36cd22561a523cf5c87d73cec45e9e59",
    "scripts/evaluate_aec_challenge_real_pilot.py":
        "922cd0e155efc48d9042b23a863d59f0aba07fda825741567cbdd9b04c089a88",
    "reports/aec_challenge_real_pilot_20261028.csv":
        "32b41d1cab6b6b28a03cb6db164debfb408441822642c2a0c1a9b42b5889aba3",
    "reports/aec_challenge_real_pilot_summary_20261028.csv":
        "4784755161aa0fa4027b2b6524f8dd34b7ccc9390ecd785103dda95b65bb27e7",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
SIBLING_PINS: Dict[str, str] = {
    "docs/task-evidence/erle-and-double-talk-preservation/contract.json":
        "d95d812edd6986929e3e67dd791f1f1d62417a6724a8464bb1eb48672a6f1c29",
    "docs/task-evidence/erle-and-double-talk-preservation/report.json":
        "6860139e8c1a9f5c01fa219f81b6b8f5ee3f43160dd139d00e45cfb853d63b50",
    "docs/task-evidence/stoi-estoi/contract.json":
        "aa42da4c71b6eee281fca1ccc52f394c32d85cb2c65e31d1bc0a814a7726f7f5",
    "docs/task-evidence/stoi-estoi/report.json":
        "a74820ff3e42f80d5ab06038de6ec70989876c6d91b98b34dc059ed2a6858f82",
    "docs/task-evidence/srmr-and-reverb-metrics/contract.json":
        "707399441ff60a24cf6b5475f86bdebe91522d98e4e269829f69022daaefdbe8",
    "docs/task-evidence/srmr-and-reverb-metrics/report.json":
        "291897aaacb9d16a40bb68a64dfb84d2c03a559ca9997a9e5fb1c718d633b979",
    "docs/task-evidence/localvqe-compact-echo-only/contract.json":
        "c44d9325733467e7668869c2c228d533a384189ed77bdf4821e40d544fd66f85",
    "docs/task-evidence/localvqe-compact-echo-only/report.json":
        "28b17d5ee0afa2f017009456ef58d0fbac6383bf64744682e7400079df862369",
    "docs/task-evidence/webrtc-aec3/contract.json":
        "f3bd95cac4ce78cfddb971a90a11ecc4b17097444398edd3eb32dee665bb3258",
    "docs/task-evidence/webrtc-aec3/report.json":
        "da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283",
}

TASK_ROW_IDENTITY: Dict[str, Any] = {
    "id": TASK_ID,
    "title": "AECMOS",
    "repository": "audio-sdk",
    "mode": "research-control",
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    "evidence": [
        "research/aec_research_20261028.md",
        "adapters/aecmos/run.py",
    ],
    "base_commit": BASE_COMMIT,
    "branch": BRANCH,
}
MUTABLE_PROVENANCE: Dict[str, Any] = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "mutable": True,
    "gate": False,
    "hashed": False,
    "note": (
        "Only the stable linked-row identity above is compared. The mutable "
        "full board file is never hashed into canonical bytes."
    ),
}
SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_only": True,
    "installed_v0_format": "16 kHz mono float32, 160 samples",
    "real_aecmos_weights": False,
    "real_aecmos_source": False,
    "licensed_source_or_binary": False,
    "model_runtime_executed": False,
    "weights_or_assets": False,
    "real_speech_or_corpus": False,
    "downloads": False,
    "device_timing": False,
    "listening": False,
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
    "processor_exposure": False,
    "release_claim": False,
}

RELEASE_GATES: List[Dict[str, Any]] = [
    {
        "id": "licensed_aecmos_model_weights",
        "requirement": (
            "The exact AECMOS v4 16 kHz ONNX weights with SHA-256 "
            "f53122f43cb7e5b77ec797e85c8b997cfc2aac8220857c709226d876de8c0a99, "
            "the model's own license terms, redistribution terms and written "
            "approval to execute; the repository MIT license covers code only."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "official_aecmos_source_revision_and_runtime",
        "requirement": (
            "The official AEC-Challenge AECMOS inference source pinned to one "
            "revision plus a pinned onnxruntime/librosa/numpy runtime approved "
            "for this task; an incidental environment is not a qualification."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "rights_cleared_paired_cohort",
        "requirement": (
            "A rights-cleared paired lpb/microphone/enhanced cohort with exact "
            "talk-type labels, alignment, device metadata and participant and "
            "redistribution rights."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "exact_preprocessing_and_state_parity",
        "requirement": (
            "Numerical parity for the 513/256/160 log-mel features, the 20-frame "
            "st/nst/dt markers, the 20-frame zero terminator, the zero GRU h0 "
            "state and both output names against the official implementation."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "paired_echo_and_degradation_scores",
        "requirement": (
            "Official AECMOS echo and degradation predictions reproduced on the "
            "pinned runtime and rights-cleared cohort, keeping the two output "
            "dimensions separate."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "aggregation_uncertainty_and_failed_items",
        "requirement": (
            "A frozen paired aggregation with uncertainty intervals, retained "
            "failed items and a stated validity policy for every stratum."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "human_prediction_separation_and_listening",
        "requirement": (
            "Predicted scores labelled as learned AECMOS predictions and never "
            "as human ratings, plus authorized listening or an approved quality "
            "assessment where a rating is claimed."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "provider_intake_and_release_review",
        "requirement": (
            "Evidence-adapter intake, license and public-surface review, "
            "independent exact-head approval and explicit release admission "
            "before any developer exposure."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
]

REQUIRED_ARTIFACTS: List[Dict[str, Any]] = [
    {
        "id": "licensed_aecmos_model_weights",
        "artifact": (
            "AECMOS v4 16 kHz ONNX weights file "
            "Run_1663915512_Stage_0.onnx with exact SHA-256."
        ),
        "present": False,
        "rights_requirement": (
            "The model weight license and redistribution terms for the exact "
            "file plus written approval to execute; the MIT repository license "
            "is code-only and does not clear the weights."
        ),
        "why_blocked": (
            "No ONNX weights file is present anywhere in the workspace; no "
            "download, copy or substitute was attempted."
        ),
    },
    {
        "id": "official_aecmos_source_revision",
        "artifact": (
            "The official AEC-Challenge AECMOS inference source pinned to one "
            "immutable revision with its feature and marker reference."
        ),
        "present": False,
        "rights_requirement": (
            "Upstream source revision, its code license and any redistribution "
            "terms for the exact revision."
        ),
        "why_blocked": (
            "No AEC-Challenge or AECMOS source checkout is present; the local "
            "adapter is a wrapper, not the official implementation."
        ),
    },
    {
        "id": "qualified_model_runtime",
        "artifact": (
            "A pinned and approved onnxruntime + librosa + numpy environment "
            "for the exact AECMOS revision and track."
        ),
        "present": False,
        "rights_requirement": "Runtime licenses and execution approval for the exact pinned versions.",
        "why_blocked": (
            "Only an incidental, unpinned pipeline-validation virtualenv exposes "
            "onnxruntime/librosa/numpy; the default interpreter has none and no "
            "environment is pinned or approved for this task."
        ),
    },
    {
        "id": "rights_cleared_paired_cohort",
        "artifact": (
            "Rights-cleared paired lpb/microphone/enhanced audio with talk-type "
            "labels and alignment metadata."
        ),
        "present": False,
        "rights_requirement": (
            "Written corpus, participant, device and redistribution rights; no "
            "unlicensed AEC-Challenge or other recording is bundled."
        ),
        "why_blocked": "No rights-cleared paired cohort is supplied in the workspace.",
    },
    {
        "id": "evidence_adapter_review",
        "artifact": (
            "Evidence-adapter intake, aggregation/uncertainty policy, human "
            "versus predicted labelling review and release approval."
        ),
        "present": False,
        "rights_requirement": "Reviewer, listening-panel where applicable and release approval.",
        "why_blocked": "No intake, listening or release review is in scope here.",
    },
]
NON_CLAIMS: List[str] = [
    "No AECMOS model, official inference source, ONNX weight, runtime or emulator is present, linked, executed or reproduced.",
    "No licensed weight, corpus or paired recording is downloaded, copied or bundled.",
    "No AECMOS echo or degradation prediction, MOS, ranking, oracle or threshold is claimed; every score slot is null.",
    "No synthetic geometry, feature digest or diagnostic is a human rating or a quality score.",
    "No listening, device-timing, benchmark or release claim is made.",
    "No installed v0, ABI, registry, descriptor, default, shared build or CI behavior is changed.",
    "No provider or processor is registered, exposed or default-enabled.",
    "No missing, blocked or adverse result is promoted; no result qualifies.",
]
REPRODUCTION: List[str] = [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
    "python3 run.py --report",
    "python3 run.py --sources",
    "python3 run.py --inspect",
    "python3 verify.py",
]

REPORT_KEYS = {
    "SPDX-FileCopyrightText",
    "SPDX-License-Identifier",
    "schema_id",
    "task",
    "component",
    "profile",
    "base_commit",
    "branch",
    "status",
    "completeness",
    "decision",
    "qualification",
    "task_row",
    "mutable_provenance",
    "source_pins",
    "boundary_pins",
    "sibling_pins",
    "scope",
    "public_surface",
    "input_contract",
    "adapter_contract_audit",
    "fixture",
    "runs",
    "controls",
    "adverse_results",
    "missing_results",
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
    text = canonical_bytes(report).decode("utf-8")
    payload = (text + "\n").encode("utf-8")
    return text, sha256_bytes(payload)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _round6(value: float) -> float:
    return round(float(value), 6)


def digest_float32(values: Sequence[float]) -> str:
    payload = struct.pack("<%df" % len(values), *[f32(v) for v in values])
    return sha256_bytes(payload)


def feature_frame_count(samples: int) -> int:
    """Frames for center=True STFT: 1 + (n - 1) // hop_length."""
    if isinstance(samples, bool) or not isinstance(samples, int):
        raise ReferenceError("frame_count_requires_int")
    if samples <= 0:
        raise ReferenceError("frame_count_requires_positive_samples")
    return 1 + (samples - 1) // HOP_LENGTH


def length_policy(samples: int) -> Tuple[int, bool]:
    """Keep at most MAX_SAMPLES, preserving the first samples in order."""
    if isinstance(samples, bool) or not isinstance(samples, int):
        raise ReferenceError("length_policy_requires_int")
    if samples <= 0:
        raise ReferenceError("length_policy_requires_positive_samples")
    return (samples if samples <= MAX_SAMPLES else MAX_SAMPLES,
            samples > MAX_SAMPLES)


def scenario_marker(talk_type: str) -> Dict[str, float]:
    """Official adapter marker values after normalization (0.0/1.0)."""
    if talk_type == "nst":
        near_end, far_end = 1, 0
    elif talk_type == "st":
        near_end, far_end = 0, 1
    elif talk_type == "dt":
        near_end, far_end = 0, 0
    else:
        raise ReferenceError("invalid_talk_type")
    return {
        "lpb": float(1 - near_end),
        "microphone": float(1 - far_end),
        "enhanced": 1.0,
    }


def input_contract() -> Dict[str, Any]:
    return {
        "contract_id": "aecmos-v4-16khz-three-stream-geometry",
        "source_of_truth": "adapters/aecmos/run.py",
        "installed_v0_format": "16 kHz mono float32, 160 samples",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "max_seconds": MAX_SECONDS,
        "max_samples": MAX_SAMPLES,
        "n_fft": N_FFT,
        "hop_length": HOP_LENGTH,
        "n_mels": N_MELS,
        "fft_bins": FFT_BINS,
        "stft_center": True,
        "frame_count_rule": FRAME_COUNT_RULE,
        "stream_order": list(STREAM_ORDER),
        "talk_types": list(TALK_TYPES),
        "scenario_marker_frames": MARKER_FRAMES,
        "scenario_terminator_frames": TERMINATOR_FRAMES,
        "marker_values_are_post_normalization": True,
        "feature_normalization": FEATURE_NORMALIZATION,
        "truncation": "keep the first 320000 samples",
        "state_input": "h0",
        "state_shape": list(GRU_STATE_SHAPE),
        "output_names": list(OUTPUT_NAMES),
        "mel_implementation_reproduced": False,
        "feature_values_reproduced": False,
        "scores_reproduced": False,
        "qualifies": False,
    }


def input_contract_summary() -> Dict[str, Any]:
    return {
        "contract_id": "aecmos-v4-16khz-three-stream-geometry",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "n_fft": N_FFT,
        "hop_length": HOP_LENGTH,
        "n_mels": N_MELS,
        "max_samples": MAX_SAMPLES,
        "scenario_marker_frames": MARKER_FRAMES,
        "scenario_terminator_frames": TERMINATOR_FRAMES,
        "talk_types": list(TALK_TYPES),
        "stream_order": list(STREAM_ORDER),
        "state_shape": list(GRU_STATE_SHAPE),
        "output_names": list(OUTPUT_NAMES),
        "scores_reproduced": False,
    }


ADAPTER_TOKENS = (
    "sr=16000",
    "n_fft=513",
    "hop_length=256",
    "n_mels=160",
    "max_samples = 20 * 16000",
    "np.zeros((4, 1, 64), np.float32)",
    '"h0":',
    'talk_type not in {"st", "nst", "dt"}',
    "aecmos_echo",
    "aecmos_degradation",
    "+ 40.0) / 40.0",
    "np.ones((20, 160), np.float32)",
    "np.zeros((20,160),np.float32)",
)


def adapter_contract_audit() -> Dict[str, Any]:
    path = WORKSPACE / "adapters/aecmos/run.py"
    text = path.read_text(encoding="utf-8")
    checks = [{"token": token, "present": token in text}
              for token in ADAPTER_TOKENS]
    return {
        "adapter_path": "adapters/aecmos/run.py",
        "adapter_sha256": digest_file(path),
        "expected_sha256": SOURCE_PINS["adapters/aecmos/run.py"],
        "hash_matches_source_pin": digest_file(path) == SOURCE_PINS["adapters/aecmos/run.py"],
        "tokens": checks,
        "all_tokens_present": all(item["present"] for item in checks),
        "reproduces_feature_values": False,
        "qualifies": False,
    }


def _lcg(seed: int, count: int) -> List[float]:
    state = seed & 0x7FFFFFFF
    values: List[float] = []
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append(state / 1073741824.0 - 1.0)
    return values


def build_streams(condition: str = "paired") -> Dict[str, List[float]]:
    """Frozen deterministic three-stream fixture.  Not speech, not a corpus."""
    if condition not in {"paired", "no_reference", "reference_dropout",
                         "delayed_enhanced", "swapped_streams", "silence"}:
        raise ReferenceError("unknown_condition")
    if condition == "silence":
        zeros = [0.0] * FIXTURE_SAMPLES
        return {"lpb": list(zeros), "microphone": list(zeros),
                "enhanced": list(zeros)}
    render_noise = _lcg(RENDER_NOISE_SEED, FIXTURE_SAMPLES)
    capture_noise = _lcg(NOISE_SEED, FIXTURE_SAMPLES)
    lpb: List[float] = []
    near: List[float] = []
    for sample in range(FIXTURE_SAMPLES):
        t = sample / SAMPLE_RATE_HZ
        render_base = (0.22 * math.sin(2.0 * math.pi * 137.0 * t)
                       + 0.09 * math.sin(2.0 * math.pi * 311.0 * t)
                       + 0.025 * math.sin(2.0 * math.pi * 523.0 * t))
        near_base = (0.16 * math.sin(2.0 * math.pi * 183.0 * t + 0.31)
                     + 0.06 * math.sin(2.0 * math.pi * 271.0 * t + 0.77)
                     + 0.02 * math.sin(2.0 * math.pi * 431.0 * t + 1.11))
        lpb.append(f32(render_base + 0.001 * render_noise[sample]))
        near.append(f32(near_base))
    echo: List[float] = []
    for sample in range(FIXTURE_SAMPLES):
        value = 0.0
        for delay, gain in ECHO_TAPS.items():
            if sample >= delay:
                value += gain * lpb[sample - delay]
        echo.append(f32(value))
    microphone = [f32(echo[i] + near[i] + 0.0025 * capture_noise[i])
                  for i in range(FIXTURE_SAMPLES)]
    enhanced = [f32(microphone[i] - 0.65 * echo[i])
                for i in range(FIXTURE_SAMPLES)]
    if condition == "no_reference":
        lpb = [0.0] * FIXTURE_SAMPLES
    if condition == "reference_dropout":
        start = DROPOUT_START_FRAME * FRAME_SAMPLES
        end = DROPOUT_END_FRAME * FRAME_SAMPLES
        lpb = [0.0 if start <= i < end else lpb[i]
               for i in range(FIXTURE_SAMPLES)]
    if condition == "delayed_enhanced":
        enhanced = ([0.0] * DELAYED_ENHANCED_SAMPLES
                    + enhanced[:-DELAYED_ENHANCED_SAMPLES])
    if condition == "swapped_streams":
        lpb, microphone = microphone, lpb
    return {"lpb": lpb, "microphone": microphone, "enhanced": enhanced}


def validate_triplet(lpb: Any, microphone: Any, enhanced: Any,
                     talk_type: Any) -> Dict[str, Any]:
    """Validate the three-stream contract; reject rather than repair."""
    if not isinstance(talk_type, str) or talk_type not in TALK_TYPES:
        raise ReferenceError("invalid_talk_type")
    streams = (("lpb", lpb), ("microphone", microphone),
               ("enhanced", enhanced))
    lengths = []
    for name, signal in streams:
        if signal is None:
            raise ReferenceError("missing_stream:" + name)
        if isinstance(signal, (str, bytes)) or not isinstance(signal, Sequence):
            raise ReferenceError("invalid_stream_type:" + name)
        if len(signal) == 0:
            raise ReferenceError("empty_stream:" + name)
        for value in signal:
            if isinstance(value, bool):
                raise ReferenceError("bool_sample:" + name)
            if not isinstance(value, (int, float)):
                raise ReferenceError("non_numeric_sample:" + name)
            number = float(value)
            if not math.isfinite(number):
                raise ReferenceError("nonfinite_sample:" + name)
            if abs(number) > MAX_ABS_INPUT:
                raise ReferenceError("out_of_bounds_sample:" + name)
        lengths.append(len(signal))
    if len(set(lengths)) != 1:
        raise ReferenceError("unequal_stream_lengths")
    kept, truncated = length_policy(lengths[0])
    return {
        "talk_type": talk_type,
        "input_samples": lengths[0],
        "kept_samples": kept,
        "truncated": truncated,
        "finite": True,
    }


def _diagnostics(values: Sequence[float]) -> Dict[str, float]:
    energy = sum(float(v) * float(v) for v in values)
    rms = math.sqrt(energy / len(values)) if values else 0.0
    peak = max(abs(float(v)) for v in values) if values else 0.0
    return {"rms": _round6(rms), "peak_abs": _round6(peak)}


def geometry_payload(condition: str = "paired",
                     talk_type: str = "dt") -> Dict[str, Any]:
    streams = build_streams(condition)
    validated = validate_triplet(streams["lpb"], streams["microphone"],
                                 streams["enhanced"], talk_type)
    marker = scenario_marker(talk_type)
    base_frames = feature_frame_count(validated["kept_samples"])
    total_frames = base_frames + MARKER_FRAMES + TERMINATOR_FRAMES
    digests = {name: digest_float32(streams[name]) for name in STREAM_ORDER}
    return {
        "condition": condition,
        "talk_type": talk_type,
        "input_samples": validated["input_samples"],
        "kept_samples": validated["kept_samples"],
        "truncated": validated["truncated"],
        "frame_count_before_marker": base_frames,
        "marker_frames": MARKER_FRAMES,
        "terminator_frames": TERMINATOR_FRAMES,
        "feature_frames": total_frames,
        "feature_shape": [len(STREAM_ORDER), total_frames, N_MELS],
        "marker_start_frame": base_frames,
        "marker_end_frame": base_frames + MARKER_FRAMES - 1,
        "terminator_start_frame": base_frames + MARKER_FRAMES,
        "terminator_end_frame": total_frames - 1,
        "scenario_marker": marker,
        "state_input": "h0",
        "state_shape": list(GRU_STATE_SHAPE),
        "output_names": list(OUTPUT_NAMES),
        "stream_digests": digests,
        "triplet_digest": sha256_bytes(
            canonical_bytes(digests)),
        "diagnostics": {
            "lpb": _diagnostics(streams["lpb"]),
            "microphone": _diagnostics(streams["microphone"]),
            "enhanced": _diagnostics(streams["enhanced"]),
        },
        "scores": {"aecmos_echo": None, "aecmos_degradation": None},
        "score_status": "unavailable_weights_and_official_source_absent",
        "scores_are_aecmos_predictions": False,
        "scores_are_human_ratings": False,
        "geometry_is_declared_not_runtime_verified": True,
        "qualifies": False,
    }


def _run_status(condition: str) -> str:
    return {
        "paired": "geometry_only_not_scored",
        "no_reference": "no_reference_input_not_scored",
        "reference_dropout": "partial_reference_not_scored",
        "delayed_enhanced": "misaligned_enhanced_not_scored",
        "swapped_streams": "stream_order_control_not_scored",
        "silence": "degenerate_silence_not_scored",
    }[condition]


def run_payload(condition: str, talk_type: str) -> Dict[str, Any]:
    payload = geometry_payload(condition, talk_type)
    payload["run_id"] = "aecmos_geometry_%s_%s" % (condition, talk_type)
    payload["status"] = _run_status(condition)
    payload["variant"] = "input_contract_geometry_only"
    payload["notes"] = (
        "No model is executed; the three streams are validated and their "
        "declared feature geometry is recorded. Score slots stay null."
    )
    return payload


def talk_type_runs() -> List[Dict[str, Any]]:
    return [run_payload("paired", talk_type) for talk_type in TALK_TYPES]


def control_runs() -> Dict[str, Dict[str, Any]]:
    return {
        "paired_reference": run_payload("paired", "dt"),
        "swapped_streams": run_payload("swapped_streams", "dt"),
        "no_reference": run_payload("no_reference", "dt"),
        "reference_dropout": run_payload("reference_dropout", "dt"),
        "delayed_enhanced": run_payload("delayed_enhanced", "dt"),
        "silence": run_payload("silence", "dt"),
    }


def truncation_control() -> Dict[str, Any]:
    kept, truncated = length_policy(MAX_SAMPLES + 12345)
    return {
        "control_id": "over_20s_truncation",
        "input_samples": MAX_SAMPLES + 12345,
        "kept_samples": kept,
        "truncated": truncated,
        "kept_equals_max": kept == MAX_SAMPLES,
        "frames_after_truncation": feature_frame_count(kept),
        "qualifies": False,
    }


def failure_controls() -> Dict[str, Any]:
    good = [0.01, -0.02, 0.03, 0.0]
    checks = {
        "rejects_invalid_talk_type": False,
        "rejects_missing_stream": False,
        "rejects_empty_stream": False,
        "rejects_unequal_lengths": False,
        "rejects_bool_sample": False,
        "rejects_nonfinite_sample": False,
        "rejects_out_of_bounds_sample": False,
        "rejects_string_stream": False,
        "rejects_zero_sample_frame_count": False,
        "rejects_bool_sample_count": False,
        "truncation_is_first_samples": False,
        "marker_terminator_is_consistent": False,
        "scores_are_null_everywhere": False,
    }
    rejected = 0

    def reject(call) -> bool:
        nonlocal rejected
        try:
            call()
        except ReferenceError:
            rejected += 1
            return True
        return False

    checks["rejects_invalid_talk_type"] = reject(
        lambda: validate_triplet(good, good, good, "bogus"))
    checks["rejects_missing_stream"] = reject(
        lambda: validate_triplet(None, good, good, "dt"))
    checks["rejects_empty_stream"] = reject(
        lambda: validate_triplet([], good, good, "dt"))
    checks["rejects_unequal_lengths"] = reject(
        lambda: validate_triplet(good, good + [0.0], good, "dt"))
    checks["rejects_bool_sample"] = reject(
        lambda: validate_triplet([True, 0.0], [0.0, 0.0], [0.0, 0.0], "dt"))
    checks["rejects_nonfinite_sample"] = reject(
        lambda: validate_triplet([float("nan"), 0.0], [0.0, 0.0],
                                 [0.0, 0.0], "dt"))
    checks["rejects_out_of_bounds_sample"] = reject(
        lambda: validate_triplet([MAX_ABS_INPUT + 1.0], [0.0], [0.0], "dt"))
    checks["rejects_string_stream"] = reject(
        lambda: validate_triplet("abcd", good, good, "dt"))
    checks["rejects_zero_sample_frame_count"] = reject(
        lambda: feature_frame_count(0))
    checks["rejects_bool_sample_count"] = reject(
        lambda: feature_frame_count(True))

    outcome = length_policy(MAX_SAMPLES + 5)
    checks["truncation_is_first_samples"] = (
        outcome == (MAX_SAMPLES, True)
        and length_policy(MAX_SAMPLES) == (MAX_SAMPLES, False)
        and length_policy(1) == (1, False))
    markers_ok = True
    for talk_type in TALK_TYPES:
        marker = scenario_marker(talk_type)
        expected = {
            "st": {"lpb": 1.0, "microphone": 0.0, "enhanced": 1.0},
            "nst": {"lpb": 0.0, "microphone": 1.0, "enhanced": 1.0},
            "dt": {"lpb": 1.0, "microphone": 1.0, "enhanced": 1.0},
        }[talk_type]
        if marker != expected:
            markers_ok = False
        geometry = geometry_payload("paired", talk_type)
        if geometry["terminator_start_frame"] != \
                geometry["marker_end_frame"] + 1:
            markers_ok = False
        if geometry["feature_frames"] != (
                geometry["frame_count_before_marker"] + MARKER_FRAMES
                + TERMINATOR_FRAMES):
            markers_ok = False
    checks["marker_terminator_is_consistent"] = markers_ok
    reports = talk_type_runs() + list(control_runs().values())
    checks["scores_are_null_everywhere"] = all(
        row["scores"] == {"aecmos_echo": None, "aecmos_degradation": None}
        for row in reports)
    return {
        "all_explicit": all(checks.values()),
        "checks": checks,
        "rejected_count": rejected,
        "blocked_count": 8,
        "note": (
            "Every rejection is explicit and local; no rejected value is "
            "scored, repaired or promoted."
        ),
        "qualifies": False,
    }


def adverse_results(controls: Dict[str, Dict[str, Any]],
                    truncation: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for name in ("swapped_streams", "no_reference", "reference_dropout",
                 "delayed_enhanced", "silence"):
        payload = controls[name]
        rows.append({
            "result_id": name,
            "status": payload["status"],
            "triplet_digest": payload["triplet_digest"],
            "scores": payload["scores"],
            "observation": {
                "swapped_streams": "lpb and microphone are exchanged; geometry is finite but stream order is wrong.",
                "no_reference": "lpb is all zeros; an AECMOS run would have no echo reference.",
                "reference_dropout": "lpb is zeroed over frames 30-39; the reference is partial.",
                "delayed_enhanced": "enhanced is shifted by 128 samples; content is misaligned.",
                "silence": "all three streams are zero; the mel/loudness geometry is degenerate.",
            }[name],
            "qualifies": False,
        })
    rows.append({
        "result_id": truncation["control_id"],
        "status": "truncation_policy_only",
        "triplet_digest": None,
        "scores": {"aecmos_echo": None, "aecmos_degradation": None},
        "observation": "Inputs above 20 s keep only the first 320000 samples.",
        "qualifies": False,
    })
    return rows


def missing_results() -> List[Dict[str, Any]]:
    return [
        {"result_id": "aecmos_echo_prediction", "status": "blocked",
         "scores": None, "reason": "weights_and_official_source_absent",
         "qualifies": False},
        {"result_id": "aecmos_degradation_prediction", "status": "blocked",
         "scores": None, "reason": "weights_and_official_source_absent",
         "qualifies": False},
        {"result_id": "preprocessing_numerical_parity", "status": "blocked",
         "scores": None, "reason": "runtime_not_pinned_or_approved",
         "qualifies": False},
        {"result_id": "rights_cleared_cohort_scores", "status": "blocked",
         "scores": None, "reason": "cohort_and_rights_absent",
         "qualifies": False},
        {"result_id": "human_listening_correlation", "status": "blocked",
         "scores": None, "reason": "listening_not_performed",
         "qualifies": False},
    ]


def acceptance_profile() -> Dict[str, Any]:
    items = [
        ("scorer_pinned", "blocked",
         "The exact AECMOS weights, revision and runtime are absent."),
        ("corpus_pinned", "blocked",
         "No rights-cleared paired corpus is present or bundled."),
        ("cohort_pinned", "blocked",
         "No frozen paired lpb/microphone/enhanced cohort with talk-type labels."),
        ("aggregation_pinned", "proposal_only",
         "A paired aggregation and uncertainty policy is stated but not applied."),
        ("failed_items_retained", "synthetic_control_only",
         "Adverse, rejected and missing cases are retained with null scores."),
        ("controls_present", "synthetic_control_only",
         "Identity, swapped, no-reference, dropout, delayed and silence controls exist."),
        ("paired_vs_unpaired_separation", "proposal_only",
         "Only synthetic triplet geometry is modeled; nothing is paired-scored."),
        ("synthetic_vs_human_separation", "proposal_only",
         "Synthetic geometry diagnostics are never labelled as human ratings."),
        ("invalid_case_validated", "synthetic_control_only",
         "Missing, empty, unequal, bool, nonfinite and out-of-bounds inputs are rejected."),
        ("valid_case_validated", "synthetic_geometry_only",
         "One valid synthetic triplet reproduces the declared geometry only."),
        ("source_reported_separation", "proposal_only",
         "Historical AECMOS values are quoted as source statements, not reproduced."),
    ]
    return {
        "profile": PROFILE,
        "synthetic_only": True,
        "items": [
            {"item": item, "status": status, "evidence": evidence,
             "qualifies": False}
            for item, status, evidence in items
        ],
        "all_qualify": False,
        "missing_result_promoted": False,
        "qualifies": False,
    }


def observed_provenance() -> Dict[str, Any]:
    return {
        "reproduced_here": False,
        "qualifies": False,
        "score_interpretation": (
            "Learned AECMOS echo/degradation predictions, not human ratings; "
            "none are reproduced or used as a threshold in this package."
        ),
        "documented_context": [
            {
                "source": "research/aec_research_20261028.md",
                "statement": (
                    "The local pilot uses Microsoft's 16 kHz AECMOS v4 ONNX "
                    "model (SHA-256 f53122f4...) to score echo quality and other "
                    "degradation; the scores are learned MOS-like predictions."
                ),
                "reproduced_here": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "source": "reports/aec_challenge_real_pilot_summary_20261028.csv",
                "statement": (
                    "12-device-group training pilot medians, e.g. double-talk "
                    "WebRTC-AEC3+NS3 echo 4.5053 / degradation 2.3808 and "
                    "LocalVQE-full echo 4.1768 / degradation 3.3370."
                ),
                "reproduced_here": False,
                "is_human_rating": False,
                "qualifies": False,
            },
            {
                "source": "adapters/aecmos/run.py",
                "statement": (
                    "The wrapper builds three log-mel streams, appends 20-frame "
                    "st/nst/dt markers plus 20 zero frames, uses a zero (4,1,64) "
                    "GRU state and returns aecmos_echo and aecmos_degradation."
                ),
                "reproduced_here": False,
                "is_human_rating": False,
                "qualifies": False,
            },
        ],
    }


def artifact_assessment() -> Dict[str, Any]:
    return {
        "all_required_absent": True,
        "runtime_presence": {
            "present": False,
            "exact_task_qualified_runtime_present": False,
            "generic_runtime_available": True,
            "expected": (
                "Official AECMOS inference source at one revision plus a "
                "pinned, approved onnxruntime/librosa/numpy environment."
            ),
            "probes": [
                {"probe": "default_python_import_onnxruntime",
                 "result": "ModuleNotFoundError"},
                {"probe": "default_python_import_librosa",
                 "result": "ModuleNotFoundError"},
                {"probe": "default_python_import_numpy",
                 "result": "ModuleNotFoundError"},
                {"probe": "incidental_venv",
                 "path": "cpp-library/pipeline-validation/playback-speed/.venv",
                 "result": (
                     "onnxruntime 1.31.1 / librosa 0.11.0 / numpy 2.4.6 present, "
                     "but unpinned and not approved for this task"
                 )},
                {"probe": "official_source_checkout",
                 "result": "no AEC-Challenge or AECMOS source checkout present"},
            ],
        },
        "weights_presence": {
            "present": False,
            "expected_path": AECMOS_MODEL_PATH,
            "expected_sha256": AECMOS_MODEL_SHA256,
            "probes": [
                {"probe": "model_path", "result": "absent"},
                {"probe": "filename_scan", "result": "no Run_1663915512* file"},
                {"probe": "onnx_sha256_scan",
                 "result": "no ONNX file matches; the hash appears only in text provenance"},
            ],
        },
        "corpus_presence": {
            "present": False,
            "expected": "rights-cleared paired lpb/microphone/enhanced audio",
            "probes": [
                {"probe": "data_models_aecmos", "result": "absent"},
                {"probe": "data_tmp_aec_pilot", "result": "absent"},
            ],
        },
        "crosscheck": {
            "performed": True,
            "external_tool": "incidental librosa 0.11.0 venv",
            "frames_for_19200_samples": 75,
            "frames_for_320000_samples": 1250,
            "matches_frame_count_rule": True,
            "pinned_for_qualification": False,
            "reproduced_by_package": False,
        },
        "package_assets": {
            "present": False,
            "onnx_weights": 0,
            "wave_files": 0,
            "licensed_corpus": 0,
        },
        "conclusion": (
            "BLOCKED: the AECMOS ONNX weights, official inference source and "
            "rights-cleared paired cohort are absent, and no pinned approved "
            "runtime exists; no artifact was downloaded, copied or fabricated "
            "and no score qualifies."
        ),
    }


def ranking_payload(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "order": "not_ranked",
        "recommendation": None,
        "reason": (
            "No AECMOS score exists; synthetic input geometry cannot rank "
            "processors, devices or quality, and the weights, source, runtime "
            "and rights-cleared cohort are absent."
        ),
        "row_count": len(rows),
        "qualifies": False,
    }


def fixture_payload() -> Dict[str, Any]:
    streams = build_streams("paired")
    return {
        "fixture_id": "aecmos-three-stream-geometry-v1",
        "condition": "paired",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": "f32",
        "samples": FIXTURE_SAMPLES,
        "v0_frames": FIXTURE_FRAMES,
        "seconds": _round6(FIXTURE_SAMPLES / SAMPLE_RATE_HZ),
        "stream_order": list(STREAM_ORDER),
        "stream_digests": {
            name: digest_float32(streams[name]) for name in STREAM_ORDER
        },
        "excitation": {
            "render_hz": [137.0, 311.0, 523.0],
            "render_amplitudes": [0.22, 0.09, 0.025],
            "near_hz": [183.0, 271.0, 431.0],
            "near_amplitudes": [0.16, 0.06, 0.02],
            "seeds": {
                "render_noise": RENDER_NOISE_SEED,
                "near": NEAR_SEED,
                "capture_noise": NOISE_SEED,
            },
        },
        "geometry": {
            "echo_taps": {str(k): v for k, v in ECHO_TAPS.items()},
            "max_echo_delay_samples": max(ECHO_TAPS),
            "delayed_enhanced_samples": DELAYED_ENHANCED_SAMPLES,
            "dropout_frames": [DROPOUT_START_FRAME, DROPOUT_END_FRAME],
        },
        "note": (
            "Deterministic sines plus seeded integer noise; not speech, not a "
            "corpus and not a room recording."
        ),
        "qualifies": False,
    }


def build_report_core() -> Dict[str, Any]:
    runs = talk_type_runs()
    controls = control_runs()
    truncation = truncation_control()
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "qualification": QUALIFICATION,
        "task_row": TASK_ROW_IDENTITY,
        "mutable_provenance": MUTABLE_PROVENANCE,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "sibling_pins": SIBLING_PINS,
        "scope": SCOPE,
        "public_surface": PUBLIC_SURFACE,
        "input_contract": input_contract(),
        "adapter_contract_audit": adapter_contract_audit(),
        "fixture": fixture_payload(),
        "runs": runs,
        "controls": controls,
        "adverse_results": adverse_results(controls, truncation),
        "missing_results": missing_results(),
        "failure_controls": failure_controls(),
        "acceptance_profile": acceptance_profile(),
        "observed_provenance": observed_provenance(),
        "artifact_assessment": artifact_assessment(),
        "ranking": ranking_payload(runs + list(controls.values())),
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
        "mode": "three_cold_start_canonical_builds",
    }
    return report


def render_report() -> Tuple[bytes, str, str]:
    report = build_report()
    text, canonical_digest = canonical_report(report)
    payload = (text + "\n").encode("utf-8")
    return payload, sha256_bytes(payload), canonical_digest
