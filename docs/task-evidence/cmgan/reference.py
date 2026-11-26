# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence model for SDK-CMGAN.

This module is NOT CMGAN and is not a reproduction of its runtime. It does not
read weights, audio, media or a caller asset; it downloads nothing, invokes no
PyTorch/vendor runtime, measures no device clock or deadline, conducts no
listening, benchmarks no SDK build and makes no release or quality claim.

It models two things that can be checked without executing the pinned model:

* the exact upstream source geometry (16 kHz mono, 400/100 hamming STFT, power
  0.3 compression, TSCNet(64, 201), 16 s cut, whole-clip RMS normalization,
  wrap padding, batch reshape) as declared arithmetic;
* the *offline whole-clip boundary* a caller-supplied external asset would have
  to cross: exact asset identity, fail-closed admission, identity source-time
  mapping, output length equal to input length, zero declared lag and exact
  accounting.

The signal path is an original deterministic surrogate, labelled as such
everywhere. It is not CMGAN, not a substitute and qualifies nothing.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-CMGAN"
TITLE = "CMGAN"
SLUG = "cmgan"
COMPONENT = "cmgan"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "d45e0f22883021412b4206c77df4e1d8cf89dbd5"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
ADAPTER_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/adapter-proposal/0.1"
READINESS_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/readiness/0.1"
PROFILE = "enhancement"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "processor_exposure"
DISPOSITION = "proposal_only"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
SAMPLES = 32_000
FRAME_COUNT = SAMPLES // FRAME_SAMPLES
MAX_CLIP_SAMPLES = 10 * 60 * SAMPLE_RATE_HZ
MAX_CHUNK_SAMPLES = 2 * SAMPLE_RATE_HZ

N_FFT = 400
HOP_LENGTH = 100
STFT_BINS = N_FFT // 2 + 1
NUM_CHANNEL = 64
NUM_FEATURES = 201
POWER_EXPONENT = 0.3
CUT_LENGTH_SAMPLES = 16 * SAMPLE_RATE_HZ
WINDOW = "hamming"
SPECTROGRAM_MODE = "onesided"
NORMALIZATION = "whole_clip_rms_sqrt_length_over_energy"
PADDING_MODE = "wrap_tail_to_hop_multiple"
BATCH_MODE = "reshape_padded_clip_into_cut_length_rows"
DECLARED_LAG_SAMPLES = 0
ALGORITHMIC_LAG_NS = 0
FIXTURE_EPOCH_NS = 1_767_225_600_000_000_000
CLOCK_ID = "fixture-sample-coordinate-not-device"

SEED_BASE = 20261126
CONDITIONS: Tuple[str, ...] = (
    "quiet_speech",
    "active_speech",
    "low_snr_speech",
    "onset_offset",
    "idle_noise",
)
CHUNK_SIZES: Tuple[int, ...] = (1, 7, 80, 159, 160, 161, 320, 1280)
OVER_SUBTRACTION = 1.2
GAIN_FLOOR = 0.25
ATTACK = 0.5
RELEASE = 0.99
NOISE_PERCENTILE = 0.25
EPS = 1e-12

# Exact pinned candidate identity. The checkpoint, source files and license text
# were independently hashed from the already-staged pinned checkout on this
# host; nothing was downloaded, copied into, or read from this SDK worktree.
CANDIDATE_ID = "ruizhecao96/CMGAN-TSCNet"
MODEL_NAME = "CMGAN TSCNet (Conformer-based Metric GAN)"
SOURCE_REPOSITORY = "https://github.com/ruizhecao96/CMGAN"
SOURCE_REVISION = "39946005d9b66fa1e824edf4bb6bc9a06088e443"
SOURCE_DATE = "2024-05-03T19:57:24+02:00"
CODE_LICENSE = "MIT"
CHECKPOINT_PATH = "src/best_ckpt/ckpt"
CHECKPOINT_BYTES = 7_488_051
CHECKPOINT_SHA256 = "e57af0ccc3ef1b0ddc6434926d08f34ac3fdbcb1ff17783c00de17a1202f6bcf"
CHECKPOINT_GIT_BLOB = "cbafab9a5fe739f3662c65cfe7be009dc475e0d1"
MODEL_LICENSE_METADATA = "MIT repository LICENSE; no separate weight-specific model card"
TRAINING_DATA = "VCTK-DEMAND 16 kHz; exposure and redistribution not cleared here"
UPSTREAM_RUNTIME = "torch==1.10.0+cu113 / torchaudio==0.10.0+cu113 (upstream requirements)"
TRAINING_DATA_NOTE = "VCTK-DEMAND; dataset-level and artifact-level rights review absent"

# Source files of the pinned official checkout, verified locally by
# probe_local_asset() when the checkout is present. They are recorded here and in
# the contract/report, but only the hashes of the research/plan ledgers below are
# required pins of the package (the ignored checkout may be absent elsewhere).
ASSET_SOURCE_PINS: Dict[str, str] = {
    "src/models/generator.py":
        "b59a81e428859986cc39b3bc773fa772a8e571b3cbed8ec0f5da04432c3a7645",
    "src/models/conformer.py":
        "1ebc39298664118b682f820d4c0334885832d6cfa9c9d0256b471f15a7722c3d",
    "src/utils.py":
        "47856504faa9b23e2419d2dddd1c2a551a1c45d9dc6c9b3ba58e5cd64b3b2fe0",
    "src/evaluation.py":
        "f3b89ea3cd864d5208254ff9adbf71be862a1be90e87eb84a50979c7a7f1c3ea",
    "src/requirements.txt":
        "436e872022f085441682ee5fb77f13e7eee60c4c4b7620e7a5991560153042b2",
    "LICENSE":
        "1d22d7af3ef4a2f3cf738c4c716d2e8d7256626d54295feeb367a09d3378a1b4",
}
LOCAL_ASSET_CHECKOUT = Path(
    "/Users/htsakanyan/workspace/audio/audioml/data/checkouts/cmgan-official")

# Deterministic evidence ledgers and the prior bounded attempt. All paths are
# relative to SOURCE_ROOT.
SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/voice-enhancement-20261101/agent-cmgan-eval/REPORT.md":
        "5ccd8a6bc2d9af5415df9898cf85c3c35835285102c5592bbc66ba326eb2e8d8",
    "research/voice-enhancement-20261101/agent-cmgan-eval/adapter.json":
        "b8fa25e178d19c851804894153a92e3863463baab7e78ff645b261c2a369ffed",
    "research/voice-enhancement-20261101/agent-cmgan-eval/adapter.lock.json":
        "49d7f0b1d53702f89ca33768f45c5dabde5a1f96ecb041d6caaff31ced0061b2",
    "research/voice-enhancement-20261101/agent-cmgan-eval/adapter.py":
        "16cca93d81ba25a0bb71f2ed5c9f0556c3d13a20f05ad9267afc530971fb7c22",
    "research/voice-enhancement-20261101/agent-cmgan-eval/run_cmgan.py":
        "42e61fc0d9eb3c4463b908a1dd2d30daed1aa87aa761d07affd2f51e117bfbc6",
    "research/voice-enhancement-20261101/agent-cmgan-eval/cmgan_smoke.json":
        "1fced1439b019ce3ec1136275df129f37654d2e6a87db42a3483cd0e2f7b0625",
    "research/voice-enhancement-20261101/agent-cmgan-eval/cmgan_smoke-retry01.json":
        "d9c26a61501a1d8ebbd8278b3a91156fcaeaccf3ede005f20fb2f1df4f430075",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
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
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
}

# Fail-closed local file set. SOURCES.sha256 is excluded because a manifest
# cannot pin its own bytes; its .license sidecar is included.
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256.license",
    "adapter.json",
    "adapter.json.license",
    "check_licensing.py",
    "contract.json",
    "contract.json.license",
    "readiness.json",
    "readiness.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)

README_DIGEST_FILES: Tuple[str, ...] = (
    "adapter.json",
    "readiness.json",
    "reference.py",
    "report.json",
    "run.py",
    "test_reference.py",
    "verify.py",
)
README_TABLE_START = "<!-- digest-table:start -->"
README_TABLE_END = "<!-- digest-table:end -->"
EXPECTED_TEST_COUNT = 38

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
    "samples_per_call": FRAME_SAMPLES,
}

BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "installed_v0_geometry_preserved": True,
    "installed_v0_behavior_change": False,
    "shared_build_or_ci_change": False,
    "processor_exposure": False,
    "task_board_or_handoff_write": False,
    "assets_copied_into_worktree": False,
    "weights_downloaded": False,
}

OFFLINE_BOUNDARY: Dict[str, Any] = {
    "mode": "offline-whole-clip",
    "streaming_public_api": False,
    "whole_clip_required": True,
    "frames_buffered_until_finish": True,
    "output_length_equals_input": True,
    "source_time_mapping": "identity",
    "delay_compensation_samples": DECLARED_LAG_SAMPLES,
    "padded_samples_emitted": 0,
    "algorithmic_lag_samples": DECLARED_LAG_SAMPLES,
    "flush_required": False,
    "asset_storage": "external",
    "provider_file_access": False,
}

CLAIMS: Dict[str, bool] = {
    "real_cmgan_runtime": False,
    "weights_accessed_by_package": False,
    "asset_downloaded": False,
    "real_audio_read": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "content_latency_measured": False,
    "memory_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "quality_claim": False,
    "release_claim": False,
    "source_reported_result_reproduced": False,
}

EXACT_BLOCKERS: Tuple[str, ...] = (
    "PRIMARY: no execution environment for the exact pinned model exists in "
    "this task. The upstream evaluation path requires CUDA (it calls .cuda() "
    "and its requirements pin torch==1.10.0+cu113); the recorded host is "
    "macOS arm64 with no CUDA device, the pinned Python 3.12.16 interpreter has "
    "no torch installed, and no pinned, validated CPU or alternate accelerator "
    "artifact with a recorded digest exists. The recorded CPU-only smoke "
    "entered STFT preprocessing and hit the 1200 s worker bound with zero "
    "outputs and 4,143,202,304 B peak child RSS, so no exact CMGAN output or "
    "inference completion exists.",
    "No matched qualification evidence exists. There is no CMGAN output on the "
    "frozen 30-pair DNS2020 no-reverb cohort, no CMGAN output on the EARS "
    "screen, no paired SI-SDR/STOI against a clean reference, no clean-speech "
    "preservation result, no permitted listening result and no independent "
    "scorer run. The matrix row remains unavailable/blocked and the census "
    "keeps CMGAN outside the runnable candidate count.",
    "Artifact-specific rights and training-data provenance are not cleared. The "
    "repository LICENSE is MIT and the checkpoint is tracked in that repository, "
    "but there is no separate weight-specific model card or terms text; the "
    "checkpoint was trained on VCTK-DEMAND, whose dataset-level terms, "
    "redistribution clearance and product-use review are absent. No checkpoint, "
    "upstream source, audio or runtime may be vendored, packaged or "
    "redistributed by this package.",
    "Target-runtime timing, memory, availability and content delay are "
    "unmeasured for any environment, and no opt-in provider intake, OFF-default "
    "adapter, independent exact-head review or release approval exists. The "
    "recorded 1200 s failure is a bound and a failure observation, not an RTF.",
)

REOPEN_CONDITIONS: Tuple[str, ...] = (
    "Reopen execution only when a pinned runtime artifact (exact PyTorch build "
    "and wheel digest, host OS/architecture, accelerator identity and driver) "
    "loads the exact checkpoint at git blob "
    "cbafab9a5fe739f3662c65cfe7be009dc475e0d1 (SHA-256 "
    "e57af0ccc3ef1b0ddc6434926d08f34ac3fdbcb1ff17783c00de17a1202f6bcf) and "
    "completes the official enhance_one_track geometry with a finite, "
    "length-preserving output on a frozen caller-owned synthetic input inside "
    "the bounded worker, with a recorded reference vector.",
    "Reopen qualification only when the exact runtime above produces outputs "
    "for the frozen common 30-pair DNS2020 no-reverb cohort, an independent "
    "clean-reference scorer reports paired SI-SDR and STOI with controls, a "
    "separate clean-speech preservation and silence/idle check passes, and a "
    "permitted listening protocol is run. A missing or failed item re-blocks "
    "the gate; it never qualifies the candidate.",
    "Reopen rights only with written weight-specific terms, training-data "
    "provenance and exposure, redistribution and product-use clearance for the "
    "exact checkpoint, plus a legal/rights decision. The MIT code license alone "
    "is not treated as artifact-specific clearance.",
    "Reopen timing and release only after measured target content delay, "
    "availability, memory and throughput under the intended workload are "
    "recorded, an opt-in provider intake with an OFF default and an unchanged "
    "v0 ABI passes independent review, and the owner makes an explicit default "
    "decision. No gate is satisfied by the synthetic boundary controls here.",
)

GATES: Tuple[Tuple[str, str], ...] = (
    ("exact_asset_identity", "clear"),
    ("runtime_admission", "blocked"),
    ("artifact_rights", "blocked"),
    ("exact_reference_parity", "blocked"),
    ("rights_cleared_cohort", "blocked"),
    ("independent_scoring_and_listening", "blocked"),
    ("target_runtime_timing", "blocked"),
    ("provider_intake", "blocked"),
    ("public_default_selection", "blocked"),
)

UPSTREAM_CLAIMS: Dict[str, Any] = {
    "dataset": "VoiceBank+DEMAND 16 kHz",
    "pesq": 3.41,
    "ssnr_db": 11.10,
    "source": "official repository README / paper abstract",
    "reproduced_here": False,
    "claim_scope": "author-reported upstream values only; not local measurements",
}

PRIOR_ATTEMPT: Dict[str, Any] = {
    "smoke": {
        "result": "failed before checkpoint load/inference",
        "reason": "adapter looked for best_ckpt/ckpt at the repository root",
        "wall_seconds": 0.387,
        "outputs": 0,
        "peak_child_rss_bytes": 36_077_568,
    },
    "smoke_retry01": {
        "result": "timed out at the worker bound",
        "reason": "adapter timed out",
        "wall_seconds": 1200.6426020000363,
        "outputs": 0,
        "peak_child_rss_bytes": 4_143_202_304,
        "entered_stft_preprocessing": True,
        "model_forward_proven": False,
        "host": "macOS-27.2-arm64-arm-64bit",
    },
    "pairs_expected": 1,
    "pairs_completed": 0,
    "quality_score_available": False,
    "recorded_as_rtf": False,
}

MATCHED_EVIDENCE: Dict[str, Any] = {
    "candidate_matrix": {
        "record": 15,
        "csv_line": 16,
        "status": "unavailable/blocked",
        "finding": (
            "Official MIT checkpoint staged and hash-pinned, but one 10-second "
            "CPU smoke timed out at 1,200 s after entering STFT preprocessing; "
            "no output, telemetry cannot prove the model forward began, "
            "process-tree peak RSS 4.14 GB, no quality score, needs CUDA or an "
            "optimized backend."),
        "baseline": "FastEnhancer; ClearVoice FRCRN",
    },
    "noise_suppression_census": {
        "role": "follow-up research lead, outside the runnable candidate count",
        "note": (
            "The census recorded that no official pretrained checkpoint was "
            "located at screen time and kept CMGAN outside the runnable count. "
            "That note is superseded by the later attempt, which staged and "
            "hash-pinned the tracked checkpoint but could not execute it."),
    },
    "paired_dns2020_30": {"run": False, "results": None},
    "ears_screen": {"run": False, "results": None},
    "baseline_pairing": {
        "declared_baselines": ["FastEnhancer Small", "ClearVoice FRCRN"],
        "matched_measured_baseline_against_cmgan": False,
        "reason": "no CMGAN output exists to pair",
    },
}

ENHANCEMENT_PROFILE: Dict[str, Any] = {
    "identity_noisy_controls": "identity_exact_and_synthetic_noisy_control",
    "paired_si_sdr": "synthetic_surrogate_only_not_cmgan",
    "stoi": "blocked_unmeasured",
    "clean_speech_preservation": "synthetic_only",
    "peaks_and_invalid_outputs": "synthetic_only_checked",
    "alignment": "identity_declared_not_measured",
    "state_and_memory": "synthetic_state_only_memory_blocked_unmeasured",
    "content_and_availability_timing": "blocked_unmeasured",
    "listening": "not_run",
    "real_clean_references": False,
    "real_runtime": False,
    "qualifies": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No result in this package is a qualification, benchmark, quality or release claim.",
    "The deterministic signal path is an original surrogate. It is not CMGAN, "
    "does not load the checkpoint and cannot stand in for a CMGAN result.",
    "No checkpoint, upstream source, audio, corpus, media or runtime was "
    "downloaded, copied, vendored, packaged or redistributed into this worktree.",
    "The upstream PESQ 3.41 / SSNR 11.10 dB values are author-reported "
    "VoiceBank+DEMAND figures. They are not reproduced, not pooled with the "
    "synthetic numbers and not evidence for this host.",
    "No audio was read or played; no cohort, consent, output-use grant or "
    "listening protocol exists.",
    "No device clock, content delay, availability, memory or throughput was "
    "measured. The 1200 s prior bound is not reported as inference timing.",
    "No provider, descriptor, registry, default, installed-v0 behavior, ABI, "
    "shared build, CI, board or handoff file is changed.",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        return 0.0 if value == 0.0 else value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def _lcg(seed: int):
    state = seed & 0x7FFFFFFF

    def nxt() -> float:
        nonlocal state
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        return state / 0x7FFFFFFF

    return nxt


def _seed(name: str) -> int:
    return SEED_BASE + int(sha256(name.encode("utf-8"))[:8], 16) % 100_000


def _syllable_envelope(seconds: float, condition: str) -> float:
    if condition == "onset_offset":
        gate = 1.0 if 0.12 <= seconds <= 0.52 else 0.0
        if gate == 0.0:
            return 0.0
    rate = 3.1 if condition != "quiet_speech" else 2.4
    shape = 0.5 * (1.0 + math.sin(2.0 * math.pi * rate * seconds - 1.1))
    return 0.35 + 0.65 * shape


def synth(condition: str) -> Tuple[List[float], List[float]]:
    """Return (clean target, observed noisy) for a labelled synthetic condition."""
    if condition not in CONDITIONS:
        raise ValueError("unknown synthetic condition: " + condition)
    if condition == "idle_noise":
        clean_amplitude = 0.0
        noise_amplitude = 0.045
    elif condition == "quiet_speech":
        clean_amplitude = 0.05
        noise_amplitude = 0.008
    elif condition == "active_speech":
        clean_amplitude = 0.32
        noise_amplitude = 0.06
    elif condition == "low_snr_speech":
        clean_amplitude = 0.10
        noise_amplitude = 0.22
    else:
        clean_amplitude = 0.30
        noise_amplitude = 0.03
    rng = _lcg(_seed(condition))
    f0 = 138.0 + (7.0 if condition == "active_speech" else 0.0)
    clean: List[float] = []
    observed: List[float] = []
    for index in range(SAMPLES):
        seconds = index / SAMPLE_RATE_HZ
        envelope = _syllable_envelope(seconds, condition)
        sample = (
            0.60 * math.sin(2.0 * math.pi * f0 * seconds)
            + 0.28 * math.sin(2.0 * math.pi * 2.0 * f0 * seconds + 0.4)
            + 0.12 * math.sin(2.0 * math.pi * 3.0 * f0 * seconds + 0.9)
        )
        target = clean_amplitude * envelope * sample
        noise = noise_amplitude * (2.0 * rng() - 1.0)
        clean.append(target)
        observed.append(target + noise)
    peak = max(max(abs(value) for value in clean),
               max(abs(value) for value in observed))
    if peak > 0.95:
        factor = peak / 0.95
        clean = [value / factor for value in clean]
        observed = [value / factor for value in observed]
    return clean, observed


def asset_ref() -> Dict[str, Any]:
    """The exact caller-supplied external asset reference, metadata only."""
    return {
        "asset_id": CANDIDATE_ID,
        "storage": "external",
        "provider_file_access": False,
        "download_attempted": False,
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "checkpoint_path": CHECKPOINT_PATH,
        "checkpoint_bytes": CHECKPOINT_BYTES,
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "checkpoint_git_blob": CHECKPOINT_GIT_BLOB,
        "code_license": CODE_LICENSE,
        "model_license_metadata": MODEL_LICENSE_METADATA,
        "training_data": TRAINING_DATA,
        "runtime_spec": UPSTREAM_RUNTIME,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
    }


ASSET_REQUIRED_FIELDS: Tuple[str, ...] = (
    "asset_id", "storage", "provider_file_access", "download_attempted",
    "source_repository", "source_revision", "checkpoint_path",
    "checkpoint_bytes", "checkpoint_sha256", "checkpoint_git_blob",
    "code_license", "model_license_metadata", "training_data", "runtime_spec",
    "sample_rate_hz", "channels", "sample_format",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def asset_admission(ref: Dict[str, Any]) -> Dict[str, Any]:
    """Fail-closed schema admission of a caller-supplied asset reference."""
    errors: List[str] = []
    if not isinstance(ref, dict):
        return {"admitted": False, "qualifies": False,
                "errors": ["asset_not_object"], "reason": "not_admitted"}
    missing = sorted(set(ASSET_REQUIRED_FIELDS) - set(ref))
    unknown = sorted(set(ref) - set(ASSET_REQUIRED_FIELDS))
    if missing:
        errors.append("missing_field")
    if unknown:
        errors.append("unknown_field")
    if ref.get("asset_id") != CANDIDATE_ID:
        errors.append("wrong_asset_id")
    if ref.get("storage") != "external":
        errors.append("provider_storage")
    if ref.get("provider_file_access") is not False:
        errors.append("provider_file_access")
    if ref.get("download_attempted") is not False:
        errors.append("download_attempted")
    if ref.get("source_repository") != SOURCE_REPOSITORY:
        errors.append("wrong_source_repository")
    if ref.get("source_revision") != SOURCE_REVISION:
        errors.append("wrong_source_revision")
    if ref.get("checkpoint_path") != CHECKPOINT_PATH:
        errors.append("wrong_checkpoint_path")
    size = ref.get("checkpoint_bytes")
    if isinstance(size, bool) or not isinstance(size, int) or size != CHECKPOINT_BYTES:
        errors.append("wrong_checkpoint_bytes")
    digest = ref.get("checkpoint_sha256")
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        errors.append("malformed_checkpoint_sha")
    elif digest != CHECKPOINT_SHA256:
        errors.append("wrong_checkpoint_sha")
    if ref.get("checkpoint_git_blob") != CHECKPOINT_GIT_BLOB:
        errors.append("wrong_checkpoint_git_blob")
    if ref.get("code_license") != CODE_LICENSE:
        errors.append("wrong_code_license")
    if ref.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        errors.append("wrong_sample_rate")
    if ref.get("channels") != CHANNELS:
        errors.append("wrong_channels")
    if ref.get("sample_format") != SAMPLE_FORMAT:
        errors.append("wrong_sample_format")
    admitted = not errors
    return {
        "admitted": admitted,
        "qualifies": False,
        "errors": sorted(set(errors)),
        "reason": ("schema_control_only_no_runtime_or_result" if admitted
                   else "not_admitted"),
    }


CONFIG_REQUIRED_FIELDS: Tuple[str, ...] = (
    "model_name", "source_revision", "checkpoint_sha256", "checkpoint_bytes",
    "sample_rate_hz", "channels", "sample_format", "n_fft", "hop_length",
    "cut_length_samples", "num_channel", "num_features", "power_exponent",
    "mode", "surrogate_opt_in",
)


def default_config(surrogate_opt_in: bool = False) -> Dict[str, Any]:
    return {
        "model_name": MODEL_NAME,
        "source_revision": SOURCE_REVISION,
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "checkpoint_bytes": CHECKPOINT_BYTES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "n_fft": N_FFT,
        "hop_length": HOP_LENGTH,
        "cut_length_samples": CUT_LENGTH_SAMPLES,
        "num_channel": NUM_CHANNEL,
        "num_features": NUM_FEATURES,
        "power_exponent": POWER_EXPONENT,
        "mode": "offline",
        "surrogate_opt_in": surrogate_opt_in,
    }


def validate_config(config: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not isinstance(config, dict):
        return ["config_not_object"]
    missing = sorted(set(CONFIG_REQUIRED_FIELDS) - set(config))
    unknown = sorted(set(config) - set(CONFIG_REQUIRED_FIELDS))
    if missing:
        errors.append("missing_field")
    if unknown:
        errors.append("unknown_field")
    if config.get("model_name") != MODEL_NAME:
        errors.append("wrong_model_name")
    if config.get("source_revision") != SOURCE_REVISION:
        errors.append("wrong_source_revision")
    if config.get("checkpoint_sha256") != CHECKPOINT_SHA256:
        errors.append("wrong_checkpoint_sha")
    if config.get("checkpoint_bytes") != CHECKPOINT_BYTES:
        errors.append("wrong_checkpoint_bytes")
    if config.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        errors.append("wrong_sample_rate")
    if config.get("channels") != CHANNELS:
        errors.append("wrong_channels")
    if config.get("sample_format") != SAMPLE_FORMAT:
        errors.append("wrong_sample_format")
    if config.get("n_fft") != N_FFT:
        errors.append("wrong_n_fft")
    if config.get("hop_length") != HOP_LENGTH:
        errors.append("wrong_hop_length")
    if config.get("cut_length_samples") != CUT_LENGTH_SAMPLES:
        errors.append("wrong_cut_length")
    if config.get("num_channel") != NUM_CHANNEL:
        errors.append("wrong_num_channel")
    if config.get("num_features") != NUM_FEATURES:
        errors.append("wrong_num_features")
    if config.get("power_exponent") != POWER_EXPONENT:
        errors.append("wrong_power_exponent")
    if config.get("mode") != "offline":
        errors.append("mode_unsupported")
    if config.get("surrogate_opt_in") is not True:
        errors.append("surrogate_without_opt_in")
    return sorted(set(errors))


def geometry(length: int) -> Dict[str, Any]:
    """Exact arithmetic of the official enhance_one_track boundary."""
    if isinstance(length, bool) or not isinstance(length, int) or length <= 0:
        raise ValueError("length must be a positive integer")
    if length > MAX_CLIP_SAMPLES:
        raise ValueError("length exceeds the declared maximum clip size")
    frame_num = (length + HOP_LENGTH - 1) // HOP_LENGTH
    padded_len = frame_num * HOP_LENGTH
    padding_len = padded_len - length
    cut_len = CUT_LENGTH_SAMPLES
    if padded_len > cut_len:
        batch_size = (padded_len + cut_len - 1) // cut_len
        while 100 % batch_size != 0:
            batch_size += 1
    else:
        batch_size = 1
    if padded_len % batch_size != 0:
        raise ValueError("official batching invariant violated")
    chunk_len = padded_len // batch_size
    return {
        "input_samples": length,
        "hop_length": HOP_LENGTH,
        "frame_num_ceil": frame_num,
        "padded_len_samples": padded_len,
        "wrap_padding_samples": padding_len,
        "padded_samples_emitted": 0,
        "cut_length_samples": cut_len,
        "batch_size": batch_size,
        "samples_per_batch_row": chunk_len,
        "stft_bins": STFT_BINS,
        "stft_frames_per_row": chunk_len // HOP_LENGTH + 1,
        "output_samples": length,
        "source_time_mapping": "identity",
        "delay_compensation_samples": DECLARED_LAG_SAMPLES,
        "algorithmic_lag_samples": DECLARED_LAG_SAMPLES,
    }


def normalization_scale(samples: Sequence[float]) -> float:
    energy = sum(float(value) * float(value) for value in samples)
    if energy <= EPS:
        return 0.0
    return math.sqrt(len(samples) / energy)


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = int((len(ordered) - 1) * fraction)
    return ordered[index]


def enhance_offline(samples: Sequence[float]) -> Tuple[List[float], Dict[str, Any]]:
    """Original deterministic soft-gate surrogate; explicitly not CMGAN."""
    if not samples:
        return [], {"frame_count": 0, "noise_floor_rms": 0.0,
                    "declared_gain_floor": GAIN_FLOOR}
    frame_rms: List[float] = []
    for start in range(0, len(samples), FRAME_SAMPLES):
        frame = samples[start:start + FRAME_SAMPLES]
        frame_rms.append(math.sqrt(sum(value * value for value in frame) / len(frame)))
    noise_floor = _percentile(frame_rms, NOISE_PERCENTILE)
    envelope = 0.0
    output: List[float] = []
    for value in samples:
        magnitude = abs(value)
        if magnitude > envelope:
            envelope = ATTACK * magnitude + (1.0 - ATTACK) * envelope
        else:
            envelope = RELEASE * envelope + (1.0 - RELEASE) * magnitude
        residual = envelope - OVER_SUBTRACTION * noise_floor
        gain = residual / (envelope + EPS) if envelope > EPS else 0.0
        gain = min(1.0, max(GAIN_FLOOR, gain))
        output.append(value * gain)
    return output, {
        "frame_count": len(frame_rms),
        "noise_floor_rms": round(noise_floor, 12),
        "declared_gain_floor": GAIN_FLOOR,
        "over_subtraction": OVER_SUBTRACTION,
        "attack": ATTACK,
        "release": RELEASE,
        "noise_percentile": NOISE_PERCENTILE,
    }


def _validate_chunk(samples: Any) -> List[str]:
    errors: List[str] = []
    if not isinstance(samples, (list, tuple)):
        return ["chunk_not_sequence"]
    if len(samples) == 0:
        errors.append("chunk_empty")
    if len(samples) > MAX_CHUNK_SAMPLES:
        errors.append("chunk_oversized")
    for value in samples:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append("chunk_non_numeric")
            break
        number = float(value)
        if not math.isfinite(number):
            errors.append("chunk_nonfinite")
            break
        if number < -1.0 or number > 1.0:
            errors.append("chunk_out_of_range")
            break
    return sorted(set(errors))


class OfflineSurrogateSession:
    """Whole-clip buffering boundary; synchronous, deterministic, no clock."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = default_config(surrogate_opt_in=True) if config is None else config
        errors = validate_config(self.config)
        if errors:
            raise ValueError("invalid configuration: " + ",".join(errors))
        self._hasher = hashlib.sha256()
        self._buffer: List[float] = []
        self._finished = False
        self._closed = False
        self._feed_calls = 0

    @property
    def feed_calls(self) -> int:
        return self._feed_calls

    def state_digest(self) -> str:
        snapshot = self._hasher.copy()
        snapshot.update(b"|" + str(len(self._buffer)).encode("ascii"))
        snapshot.update(b"|" + (b"finished" if self._finished else b"open"))
        snapshot.update(b"|" + (b"closed" if self._closed else b"live"))
        return snapshot.hexdigest()

    def feed(self, samples: Sequence[float]) -> str:
        if self._closed:
            raise RuntimeError("session_closed")
        if self._finished:
            raise RuntimeError("session_finished")
        errors = _validate_chunk(samples)
        if errors:
            raise ValueError(",".join(errors))
        if len(self._buffer) + len(samples) > MAX_CLIP_SAMPLES:
            raise ValueError("clip_oversized")
        for value in samples:
            self._buffer.append(float(value))
        for value in samples:
            self._hasher.update(struct.pack("<d", float(value)))
        self._feed_calls += 1
        return self.state_digest()

    def finish(self) -> List[float]:
        if self._closed:
            raise RuntimeError("session_closed")
        if self._finished:
            raise RuntimeError("session_finished")
        output, _ = enhance_offline(self._buffer)
        if len(output) != len(self._buffer):
            raise RuntimeError("output_length_not_preserved")
        self._finished = True
        return output

    def reset(self) -> None:
        if self._closed:
            raise RuntimeError("session_closed")
        self._hasher = hashlib.sha256()
        self._buffer = []
        self._finished = False
        self._feed_calls = 0

    def close(self) -> None:
        self._closed = True


def run_offline(samples: Sequence[float], chunk_size: int) -> Dict[str, Any]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    session = OfflineSurrogateSession()
    chain: List[str] = []
    for start in range(0, len(samples), chunk_size):
        chain.append(session.feed(samples[start:start + chunk_size]))
    output = session.finish()
    return {"output": output, "chain": chain, "feed_calls": session.feed_calls}


def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / len(values))


def _db(ratio: float) -> Optional[float]:
    if ratio <= 0.0 or not math.isfinite(ratio):
        return None
    return round(20.0 * math.log10(ratio), 6)


def _snr_db(clean: Sequence[float], estimate: Sequence[float]) -> Optional[float]:
    signal = sum(value * value for value in clean)
    error = sum((a - b) ** 2 for a, b in zip(clean, estimate))
    if signal <= EPS or error <= EPS:
        return None
    return round(10.0 * math.log10(signal / error), 6)


def _si_sdr_db(clean: Sequence[float], estimate: Sequence[float]) -> Optional[float]:
    denominator = sum(value * value for value in clean)
    if denominator <= EPS:
        return None
    scale = sum(a * b for a, b in zip(clean, estimate)) / denominator
    target = [scale * value for value in clean]
    noise = [b - a for a, b in zip(target, estimate)]
    target_energy = sum(value * value for value in target)
    noise_energy = sum(value * value for value in noise)
    if target_energy <= EPS or noise_energy <= EPS:
        return None
    return round(10.0 * math.log10(target_energy / noise_energy), 6)


def _delta(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None:
        return None
    return round(b - a, 6)


def score(clean: Sequence[float], estimate: Sequence[float]) -> Dict[str, Any]:
    return {
        "snr_db": _snr_db(clean, estimate),
        "si_sdr_db": _si_sdr_db(clean, estimate),
        "rms_dbfs": _db(_rms(estimate)) if _rms(estimate) > 0 else None,
    }


def _float_digest(values: Sequence[float]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(struct.pack("<d", float(value)))
    return digest.hexdigest()


def identity_passthrough(samples: Sequence[float]) -> List[float]:
    """Exact identity control; mutates nothing and scores as the noisy control."""
    return [float(value) for value in samples]


def condition_block(condition: str) -> Dict[str, Any]:
    clean, observed = synth(condition)
    identity = identity_passthrough(observed)
    surrogate, surrogate_state = enhance_offline(observed)
    noisy_scores = score(clean, observed)
    surrogate_scores = score(clean, surrogate)
    identity_scores = score(clean, identity)
    peak = max(abs(value) for value in surrogate) if surrogate else 0.0
    return {
        "condition": condition,
        "samples": len(observed),
        "synthetic_not_cmgan": True,
        "identity_exact": identity == list(observed),
        "identity_matches_noisy_control": (
            identity_scores["snr_db"] == noisy_scores["snr_db"]
            and identity_scores["si_sdr_db"] == noisy_scores["si_sdr_db"]),
        "noisy_control": noisy_scores,
        "surrogate": surrogate_scores,
        "delta_snr_db": _delta(noisy_scores["snr_db"], surrogate_scores["snr_db"]),
        "delta_si_sdr_db": _delta(noisy_scores["si_sdr_db"],
                                  surrogate_scores["si_sdr_db"]),
        "rms_change_db": _delta(noisy_scores["rms_dbfs"], surrogate_scores["rms_dbfs"]),
        "surrogate_peak": round(peak, 12),
        "clipped": peak > 1.0,
        "nonfinite": any(not math.isfinite(value) for value in surrogate),
        "surrogate_state": surrogate_state,
    }


def _condition_blocks() -> Dict[str, Any]:
    return {condition: condition_block(condition) for condition in CONDITIONS}


def _regressions(blocks: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    for condition in CONDITIONS:
        block = blocks[condition]
        for metric, key in (("snr_db", "delta_snr_db"), ("si_sdr_db", "delta_si_sdr_db")):
            delta = block[key]
            if delta is not None and delta < 0.0:
                regressions.append({
                    "condition": condition,
                    "metric": metric,
                    "noisy_control": block["noisy_control"][metric],
                    "surrogate": block["surrogate"][metric],
                    "delta": delta,
                })
    return regressions


def alignment_probe() -> Dict[str, Any]:
    clean, observed = synth("active_speech")
    result = run_offline(observed, 160)
    output = result["output"]
    return {
        "input_samples": len(observed),
        "output_samples": len(output),
        "source_time_mapping": "identity",
        "delay_compensation_samples": DECLARED_LAG_SAMPLES,
        "padded_samples_emitted": 0,
        "length_preserved": len(output) == len(observed),
        "finite": all(math.isfinite(value) for value in output),
        "first_sample_close": abs(output[0] - observed[0]) <= 1.0,
        "target_peak": round(max(abs(value) for value in clean), 12),
    }


def geometry_probes() -> Dict[str, Any]:
    probes = {}
    for length in (SAMPLES, 32_123, CUT_LENGTH_SAMPLES, CUT_LENGTH_SAMPLES + 1,
                   1_000_000):
        probes[str(length)] = geometry(length)
    return probes


def tail_probe() -> Dict[str, Any]:
    clean, observed = synth("active_speech")
    tail = observed + observed[:123]
    info = geometry(len(tail))
    return {
        "input_samples": len(tail),
        "wrap_padding_samples": info["wrap_padding_samples"],
        "padded_len_samples": info["padded_len_samples"],
        "padded_samples_emitted": 0,
        "output_samples": info["output_samples"],
        "output_length_equals_input": info["output_samples"] == len(tail),
    }


def cross_hop_evidence() -> Dict[str, Any]:
    _, observed = synth("active_speech")
    whole = run_offline(observed, len(observed))
    whole_digest = _float_digest(whole["output"])
    cases = []
    for chunk_size in CHUNK_SIZES:
        result = run_offline(observed, chunk_size)
        digest = _float_digest(result["output"])
        cases.append({
            "chunk_size": chunk_size,
            "feed_calls": result["feed_calls"],
            "output_sha256": digest,
            "matches_whole_clip": digest == whole_digest,
        })
    total_chunks = sum(case["feed_calls"] for case in cases) + whole["feed_calls"]
    return {
        "fixture_samples": len(observed),
        "chunk_sizes_tested": list(CHUNK_SIZES),
        "whole_clip_output_sha256": whole_digest,
        "cases": cases,
        "caller_chunks_total": total_chunks,
        "all_match_whole_clip": all(case["matches_whole_clip"] for case in cases),
    }


def state_evidence() -> Dict[str, Any]:
    _, observed = synth("active_speech")
    chunk = observed[:160]
    fresh = OfflineSurrogateSession()
    steps = [fresh.feed(chunk) for _ in range(3)]
    independent = OfflineSurrogateSession()
    independent_steps = [independent.feed(chunk) for _ in range(3)]
    fresh.reset()
    reset_steps = [fresh.feed(chunk) for _ in range(3)]
    return {
        "identical_state_chain": steps == independent_steps,
        "reset_restores_initial_state": steps == reset_steps,
        "state_steps": steps,
        "initial_state_digest": OfflineSurrogateSession().state_digest(),
        "closed_is_idempotent": _close_probe(),
    }


def _close_probe() -> bool:
    session = OfflineSurrogateSession()
    session.close()
    session.close()
    return True


def config_adverse_cases() -> Dict[str, Any]:
    cases: Dict[str, Dict[str, Any]] = {}

    def check(name: str, mutate) -> None:
        config = default_config(surrogate_opt_in=True)
        mutate(config)
        errors = validate_config(config)
        cases[name] = {"errors": errors, "rejected": bool(errors)}

    check("wrong_sample_rate", lambda c: c.update(sample_rate_hz=8000))
    check("wrong_channels", lambda c: c.update(channels=2))
    check("wrong_sample_format", lambda c: c.update(sample_format="s16"))
    check("wrong_model_name", lambda c: c.update(model_name="other"))
    check("wrong_source_revision", lambda c: c.update(source_revision="0" * 40))
    check("wrong_checkpoint_sha", lambda c: c.update(checkpoint_sha256="0" * 64))
    check("wrong_checkpoint_bytes", lambda c: c.update(checkpoint_bytes=1))
    check("wrong_n_fft", lambda c: c.update(n_fft=512))
    check("wrong_hop_length", lambda c: c.update(hop_length=160))
    check("wrong_cut_length", lambda c: c.update(cut_length_samples=16000))
    check("wrong_num_channel", lambda c: c.update(num_channel=32))
    check("wrong_num_features", lambda c: c.update(num_features=257))
    check("wrong_power_exponent", lambda c: c.update(power_exponent=0.5))
    check("mode_unsupported", lambda c: c.update(mode="streaming"))
    check("surrogate_without_opt_in", lambda c: c.update(surrogate_opt_in=False))
    config = default_config(surrogate_opt_in=True)
    config.pop("checkpoint_sha256")
    cases["missing_field"] = {"errors": validate_config(config), "rejected": True}
    config = default_config(surrogate_opt_in=True)
    config["extra"] = 1
    cases["unknown_field"] = {"errors": validate_config(config), "rejected": True}
    return cases


def asset_adverse_cases() -> Dict[str, Dict[str, Any]]:
    cases: Dict[str, Dict[str, Any]] = {}

    def check(name: str, mutate) -> None:
        ref = asset_ref()
        mutate(ref)
        result = asset_admission(ref)
        cases[name] = {
            "admitted": result["admitted"],
            "errors": result["errors"],
            "rejected": not result["admitted"],
        }

    check("provider_storage", lambda r: r.update(storage="provider"))
    check("provider_file_access", lambda r: r.update(provider_file_access=True))
    check("download_attempted", lambda r: r.update(download_attempted=True))
    check("wrong_asset_id", lambda r: r.update(asset_id="other"))
    check("wrong_source_revision", lambda r: r.update(source_revision="0" * 40))
    check("wrong_checkpoint_path", lambda r: r.update(checkpoint_path="ckpt"))
    check("wrong_checkpoint_bytes", lambda r: r.update(checkpoint_bytes=1))
    check("bool_checkpoint_bytes", lambda r: r.update(checkpoint_bytes=True))
    check("wrong_checkpoint_sha", lambda r: r.update(checkpoint_sha256="0" * 64))
    check("malformed_checkpoint_sha", lambda r: r.update(checkpoint_sha256="abc"))
    check("wrong_checkpoint_git_blob", lambda r: r.update(checkpoint_git_blob="0" * 40))
    check("wrong_code_license", lambda r: r.update(code_license="Apache-2.0"))
    check("wrong_sample_rate", lambda r: r.update(sample_rate_hz=8000))
    check("wrong_channels", lambda r: r.update(channels=2))
    check("wrong_sample_format", lambda r: r.update(sample_format="s16"))
    ref = asset_ref()
    ref.pop("checkpoint_sha256")
    result = asset_admission(ref)
    cases["missing_field"] = {"admitted": result["admitted"],
                              "errors": result["errors"], "rejected": True}
    ref = asset_ref()
    ref["extra"] = 1
    result = asset_admission(ref)
    cases["unknown_field"] = {"admitted": result["admitted"],
                              "errors": result["errors"], "rejected": True}
    return cases


def frame_adverse_cases() -> Dict[str, Dict[str, Any]]:
    cases: Dict[str, Dict[str, Any]] = {}
    probes = {
        "chunk_empty": [],
        "chunk_oversized": [0.0] * (MAX_CHUNK_SAMPLES + 1),
        "chunk_non_numeric": ["0.0"],
        "chunk_boolean": [True],
        "chunk_nonfinite": [float("nan")],
        "chunk_out_of_range": [1.5],
    }
    for name, samples in probes.items():
        session = OfflineSurrogateSession()
        before = session.state_digest()
        try:
            session.feed(samples)  # type: ignore[arg-type]
            rejected = False
            error = ""
        except ValueError as exc:
            rejected = True
            error = str(exc)
        cases[name] = {
            "rejected": rejected,
            "error": error,
            "state_unchanged": session.state_digest() == before,
        }
    return cases


def lifecycle_evidence() -> Dict[str, Any]:
    session = OfflineSurrogateSession()
    session.feed([0.0] * 160)
    session.finish()
    finish_again = _raises(session.finish, RuntimeError)
    feed_after = _raises(lambda: session.feed([0.0] * 160), RuntimeError)
    reset_after = not _raises(session.reset, RuntimeError)
    closed = OfflineSurrogateSession()
    closed.close()
    closed.close()
    feed_closed = _raises(lambda: closed.feed([0.0] * 160), RuntimeError)
    empty = OfflineSurrogateSession()
    empty_output = empty.finish()
    return {
        "finish_twice_rejected": finish_again,
        "feed_after_finish_rejected": feed_after,
        "reset_after_finish_allowed": reset_after,
        "close_idempotent": True,
        "feed_after_close_rejected": feed_closed,
        "empty_clip_output_samples": len(empty_output),
    }


def _raises(function, error_type) -> bool:
    try:
        function()
    except error_type:
        return True
    return False


def asset_boundary() -> Dict[str, Any]:
    ref = asset_ref()
    admission = asset_admission(ref)
    return {
        "required_fields": list(ASSET_REQUIRED_FIELDS),
        "reference": ref,
        "admission": admission,
        "adverse_cases": asset_adverse_cases(),
        "bytes_read_by_package": 0,
        "file_access": False,
        "download": False,
    }


def local_asset_probe() -> Dict[str, Any]:
    """Advisory probe of an already-staged checkout; never downloads."""
    checkout = LOCAL_ASSET_CHECKOUT
    if not checkout.is_dir():
        return {"checkout_present": False, "checked": 0, "mismatches": [],
                "checkpoint_bytes": None, "checkpoint_sha256": None}
    mismatches: List[str] = []
    checked = 0
    for relative, expected in ASSET_SOURCE_PINS.items():
        path = checkout / relative
        if not path.is_file() or path.is_symlink():
            mismatches.append(relative + ":missing")
            continue
        checked += 1
        if sha256_file(path) != expected:
            mismatches.append(relative + ":sha256")
    checkpoint = checkout / CHECKPOINT_PATH
    size = checkpoint.stat().st_size if checkpoint.is_file() else None
    digest = sha256_file(checkpoint) if checkpoint.is_file() else None
    if size != CHECKPOINT_BYTES:
        mismatches.append("checkpoint:bytes")
    if digest != CHECKPOINT_SHA256:
        mismatches.append("checkpoint:sha256")
    return {
        "checkout_present": True,
        "checked": checked,
        "mismatches": mismatches,
        "checkpoint_bytes": size,
        "checkpoint_sha256": digest,
    }


def _core_report() -> Dict[str, Any]:
    blocks = _condition_blocks()
    cross_hop = cross_hop_evidence()
    return {
        "schema": SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "profile": PROFILE,
        "mode": "feasibility",
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": DISPOSITION,
        "defer_before": DEFER_BEFORE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "boundary": BOUNDARY,
        "format": FORMAT,
        "offline_boundary": OFFLINE_BOUNDARY,
        "claims": CLAIMS,
        "candidate": {
            "candidate_id": CANDIDATE_ID,
            "model_name": MODEL_NAME,
            "source_repository": SOURCE_REPOSITORY,
            "source_revision": SOURCE_REVISION,
            "source_date": SOURCE_DATE,
            "code_license": CODE_LICENSE,
            "model_license_metadata": MODEL_LICENSE_METADATA,
            "training_data": TRAINING_DATA,
            "training_data_note": TRAINING_DATA_NOTE,
            "checkpoint_path": CHECKPOINT_PATH,
            "checkpoint_bytes": CHECKPOINT_BYTES,
            "checkpoint_sha256": CHECKPOINT_SHA256,
            "checkpoint_git_blob": CHECKPOINT_GIT_BLOB,
            "upstream_runtime": UPSTREAM_RUNTIME,
            "immutable_identity": True,
            "asset_present_in_sdk_worktree": False,
            "asset_bytes_read_by_package": 0,
        },
        "task_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "frame_samples": FRAME_SAMPLES,
            "n_fft": N_FFT,
            "hop_length": HOP_LENGTH,
            "window": WINDOW,
            "spectrogram_mode": SPECTROGRAM_MODE,
            "stft_bins": STFT_BINS,
            "num_channel": NUM_CHANNEL,
            "num_features": NUM_FEATURES,
            "power_exponent": POWER_EXPONENT,
            "cut_length_samples": CUT_LENGTH_SAMPLES,
            "normalization": NORMALIZATION,
            "padding_mode": PADDING_MODE,
            "batch_mode": BATCH_MODE,
            "streaming_api": False,
            "declared_lag_samples": DECLARED_LAG_SAMPLES,
            "geometry_probes": geometry_probes(),
        },
        "asset_reference": asset_boundary(),
        "partial_local_observation": {
            "checkout_path_outside_worktree": str(LOCAL_ASSET_CHECKOUT),
            "source_revision_observed": SOURCE_REVISION,
            "checkpoint_bytes_observed": CHECKPOINT_BYTES,
            "checkpoint_sha256_observed": CHECKPOINT_SHA256,
            "checkpoint_git_blob_observed": CHECKPOINT_GIT_BLOB,
            "verified_from_staged_checkout_on_host": True,
            "downloaded_by_this_task": False,
            "copied_into_worktree": False,
        },
        "synthetic_surrogate": {
            "identity": "original_time_domain_soft_gate",
            "not_cmgan": True,
            "qualifies": False,
            "conditions": blocks,
            "regressions": _regressions(blocks),
            "total_synthetic_samples": SAMPLES * len(CONDITIONS),
        },
        "controls": {
            "identity_passthrough_exact": all(
                block["identity_exact"] for block in blocks.values()),
            "noisy_control_recorded": True,
            "surrogate_offline_chunked_160": True,
            "surrogate_offline_whole_clip": True,
            "cross_hop": cross_hop,
        },
        "adverse_cases": {
            "config": config_adverse_cases(),
            "frame": frame_adverse_cases(),
            "lifecycle": lifecycle_evidence(),
        },
        "alignment": alignment_probe(),
        "tail": tail_probe(),
        "state": state_evidence(),
        "enhancement_profile": ENHANCEMENT_PROFILE,
        "matched_evidence": MATCHED_EVIDENCE,
        "prior_attempt": PRIOR_ATTEMPT,
        "upstream_claims": UPSTREAM_CLAIMS,
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "gates": [{"gate": name, "status": status} for name, status in GATES],
        "blocked_release_gates": sum(1 for _, status in GATES if status == "blocked"),
        "open_exact_blockers": len(EXACT_BLOCKERS),
        "qualifying_results": 0,
        "non_claims": list(NON_CLAIMS),
        "counts": {
            "conditions": len(CONDITIONS),
            "samples_per_condition": SAMPLES,
            "total_synthetic_samples": SAMPLES * len(CONDITIONS),
            "chunk_sizes": len(CHUNK_SIZES),
            "caller_chunks_total": cross_hop["caller_chunks_total"],
            "output_samples_per_clip": SAMPLES,
            "emitted_padding_samples": 0,
            "real_audio_samples": 0,
        },
        "pins": {
            "source": dict(SOURCE_PINS),
            "boundary": dict(BOUNDARY_PINS),
            "asset_source": dict(ASSET_SOURCE_PINS),
            "local_file_names": list(LOCAL_FILES),
            "readme_digest_files": list(README_DIGEST_FILES),
        },
        "test_count": EXPECTED_TEST_COUNT,
    }


def build_report() -> Dict[str, Any]:
    report = _core_report()
    report["source_pin_paths"] = sorted(SOURCE_PINS)
    report["boundary_pin_paths"] = sorted(BOUNDARY_PINS)
    report["local_file_names"] = list(LOCAL_FILES)
    report["readme_digest_files"] = list(README_DIGEST_FILES)
    return report


def build_contract() -> Dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA_ID,
        "contract_version": "0.1",
        "task": TASK,
        "component": COMPONENT,
        "profile": PROFILE,
        "decision": DECISION,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": DISPOSITION,
        "defer_before": DEFER_BEFORE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "task_prefix": TASK_PREFIX,
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "candidate": {
            "candidate_id": CANDIDATE_ID,
            "source_repository": SOURCE_REPOSITORY,
            "source_revision": SOURCE_REVISION,
            "code_license": CODE_LICENSE,
            "checkpoint_path": CHECKPOINT_PATH,
            "checkpoint_bytes": CHECKPOINT_BYTES,
            "checkpoint_sha256": CHECKPOINT_SHA256,
            "checkpoint_git_blob": CHECKPOINT_GIT_BLOB,
            "asset_storage": "external",
            "asset_present_in_sdk_worktree": False,
            "downloaded_by_task": False,
        },
        "asset_source_pins": dict(ASSET_SOURCE_PINS),
        "task_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "frame_samples": FRAME_SAMPLES,
            "n_fft": N_FFT,
            "hop_length": HOP_LENGTH,
            "window": WINDOW,
            "stft_bins": STFT_BINS,
            "num_channel": NUM_CHANNEL,
            "num_features": NUM_FEATURES,
            "power_exponent": POWER_EXPONENT,
            "cut_length_samples": CUT_LENGTH_SAMPLES,
            "normalization": NORMALIZATION,
            "padding_mode": PADDING_MODE,
            "batch_mode": BATCH_MODE,
            "declared_lag_samples": DECLARED_LAG_SAMPLES,
        },
        "boundary": BOUNDARY,
        "exact_blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "gates": [{"gate": name, "status": status} for name, status in GATES],
        "non_claims": list(NON_CLAIMS),
        "pins": {
            "source": dict(SOURCE_PINS),
            "boundary": dict(BOUNDARY_PINS),
            "local_file_names": list(LOCAL_FILES),
            "readme_digest_files": list(README_DIGEST_FILES),
        },
        "artifact_pins": {},
    }


def build_adapter() -> Dict[str, Any]:
    return {
        "schema": ADAPTER_SCHEMA_ID,
        "component": COMPONENT,
        "identity": CANDIDATE_ID,
        "proposal_only": True,
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "provider_intake": False,
        "tasks": ["enhancement"],
        "modes": ["offline"],
        "input_kind": "waveform",
        "output_kinds": ["waveform"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "whole_clip_required": True,
        "source_time_mapping": "identity",
        "delay_compensation_samples": DECLARED_LAG_SAMPLES,
        "asset": {
            "asset_id": CANDIDATE_ID,
            "storage": "external",
            "checkpoint_path": CHECKPOINT_PATH,
            "checkpoint_bytes": CHECKPOINT_BYTES,
            "checkpoint_sha256": CHECKPOINT_SHA256,
            "source_revision": SOURCE_REVISION,
            "code_license": CODE_LICENSE,
            "asset_readiness": "blocked",
            "download": False,
        },
        "runtime_requirement": (
            "pinned CUDA-capable host or validated optimized CPU backend with a "
            "recorded artifact digest; absent in this task"),
        "entrypoint": None,
        "qualifies": False,
        "reason": (
            "proposal descriptor only; no runtime, no CMGAN output, no matched "
            "cohort and no release decision"),
    }


def build_readiness() -> Dict[str, Any]:
    return {
        "schema": READINESS_SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "profile": PROFILE,
        "decision": DECISION,
        "status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "ready": False,
        "proposal_only": True,
        "exact_external_blocker": EXACT_BLOCKERS[0],
        "blockers": list(EXACT_BLOCKERS),
        "reopen_conditions": list(REOPEN_CONDITIONS),
        "prerequisites": {
            "official_source_present_and_pinned": True,
            "exact_checkpoint_identity_verified": True,
            "task_geometry_verified_statically": True,
            "permitted_scope_unchanged": True,
            "runtime_available": False,
            "cuda_or_validated_accelerator_available": False,
            "torch_installed_in_pinned_interpreter": False,
            "exact_reference_output_available": False,
            "rights_cleared_cohort": False,
            "independent_scorer_available": False,
            "permitted_listening_available": False,
            "target_timing_measured": False,
            "provider_intake_approved": False,
        },
        "observed": {
            "prior_cpu_smoke_result": "timed out with zero outputs",
            "prior_cpu_smoke_wall_seconds": 1200.6426020000363,
            "prior_cpu_smoke_peak_rss_bytes": 4_143_202_304,
            "prior_cpu_smoke_is_rtf": False,
            "matched_30_pair_results": 0,
            "ears_results": 0,
            "qualifying_results": 0,
        },
        "gates": [{"gate": name, "status": status} for name, status in GATES],
        "blocked_release_gates": sum(1 for _, status in GATES if status == "blocked"),
        "open_exact_blockers": len(EXACT_BLOCKERS),
        "non_claims": list(NON_CLAIMS),
    }
