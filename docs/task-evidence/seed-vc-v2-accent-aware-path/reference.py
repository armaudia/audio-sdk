# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for Seed-VC V2 accent-aware path.

This package is feasibility evidence only. It models a caller-supplied-asset
tool boundary and model-free Voice-profile geometry, but it does not implement,
download, load or execute Seed-VC V2. No V2 checkpoint, consented accent
cohort, real audio, listening result, device timing or benchmark result is
included. The v1 25M file run, the v1 real-time GUI block and the XLS-R
content-encoder package are explicitly recorded as excluded evidence.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/seed-vc-v2-accent-aware-path/caller-supplied/0.1"
TASK_ID = "SDK-SEED-VC-V2-ACCENT-AWARE-PATH"
TITLE = "Seed-VC V2 accent-aware path"
COMPONENT = "seed-vc-v2-accent-aware-path"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "a51e49f718500ec9e81242cf2816f0b576333d00"
BRANCH = "swarm/SDK-SEED-VC-V2-ACCENT-AWARE-PATH"
REVIEWER = "reviewer-SEED-VC-V2-ACCENT-AWARE-PATH"
PROFILE = "Voice"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_geometry_incomplete"

# Installed v0 is unchanged. V2 below is a separate, non-exposed reference path.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"

SOURCE_CHECKOUT = {
    "path": "research/voice-conversion-eval-20261101/repos/seed-vc",
    "revision": "51383efd921027683c89e5348211d93ff12ac2a8",
    "license": "GPL-3.0",
    "present_locally": True,
    "note": "Pinned source files are read-only pins; no source is imported or executed.",
}

SOURCE_PINS: Dict[str, str] = {
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/run_seedvc_realtime.py":
        "9461c7b81cc15dcdb0efa907098b8f8ad6ecd21d1a43b3a15ab5f4bd76193ff2",
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/agent-breadth-audit/REPORT.md":
        "ef093eee8c8cd68984d3a7f5602fcc44c9a0262990e7c90c9bd34ecc3d8fadc2",
    "research/voice-conversion-eval-20261101/repos/seed-vc/README.md":
        "293507df928d542341a69b9c93e3b7344f7cc7abe73ac4b2c6395d86527a1ce4",
    "research/voice-conversion-eval-20261101/repos/seed-vc/LICENSE":
        "8b1ba204bb69a0ade2bfcf65ef294a920f6bb361b317dba43c7ef29d96332b9b",
    "research/voice-conversion-eval-20261101/repos/seed-vc/inference_v2.py":
        "d6fa090d93e86313560cda74eb13e12a02da6540a357c7661155a119ffe2bd59",
    "research/voice-conversion-eval-20261101/repos/seed-vc/app_vc_v2.py":
        "7f05abbdb25a0c6633fde3dea925dd80866f99624a61406172fe3408ffa17196",
    "research/voice-conversion-eval-20261101/repos/seed-vc/configs/v2/vc_wrapper.yaml":
        "2f35157afb40ee03748fdd09b252f14bb8d1c8d7a3d2fd1136641a096c109e6e",
    "research/voice-conversion-eval-20261101/repos/seed-vc/modules/v2/vc_wrapper.py":
        "85d14d9e2ab96045e7886e9919d32f26bc5004da695f0f303060eec10f149fb9",
    "research/voice-conversion-eval-20261101/repos/seed-vc/hf_utils.py":
        "e189160f5381092936c122bd84de570276772e0aaf4f0004ee57f7366a8be6cc",
    "research/voice-conversion-eval-20261101/repos/seed-vc/configs/astral_quantization/default_32.yml":
        "13517744ce35fcc2f5cfd2f629f7fd9fab82099846314a823c3bba146eac9827",
    "research/voice-conversion-eval-20261101/repos/seed-vc/configs/astral_quantization/default_2048.yml":
        "ed9bf643b8d58b5da3d1cd7529fad5405c70016e40649727fa3e1244366d6f6f",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-SEED-VC-25M.md":
        "9ec8776f476a6296240405bc02418ee668a80f0dc868e95feea2f3cc57e36a6e",
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER.md":
        "3f82802d41944cb26200f6b7e3b85d0541b5c2d4f2b5f9be3f9f5871bd472c07",
}

BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/seed-vc-xls-r-300m-content-encoder/README.md":
        "3ffad57b383c93b98b051d10d8bf7f7ce6a4b7c74940611dfd1853269e103f09",
    "docs/task-evidence/seed-vc-xls-r-300m-content-encoder/report.json":
        "0a661101a938600bf26a07b18b6ae0d1fa2c94e6db6394d169dc052b8b3d19ef",
    "docs/task-evidence/meanvc/README.md":
        "34d358ab134b1942b9a3a030acc3017470135921fe90a3cd71fb61c7fd643e40",
    "docs/task-evidence/meanvc/report.json":
        "e9ce6e224056838848aa5bbe52c2bfa0e1f60abb3ffbf2f7c08449e00c983164",
    "docs/task-evidence/sanas-accent-translation/README.md":
        "c62e7fdda4d50d5aa7719cf17353ecadfba6e33d07c6dda9f134fe3685fcb58c",
    "docs/task-evidence/survey-trn-03/report.json":
        "aef09671dd0bf39ec7996096f5a866bff564b0110bc1a1e6340fd5fb993f5fe2",
}

BOARD_STABLE_SHA256 = (
    "af567d24cb88f8f92783bc13e628125b19f361d0a2616ddbab69137d9b875831"
)
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)

TASK_PREFIX = "docs/task-evidence/seed-vc-v2-accent-aware-path/"
LOCAL_PIN_PATHS: Tuple[str, ...] = (
    "README.md",
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
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SCOPE_BASE_REFS = ("origin/main", "main")

# Source-derived V2 geometry: inference_v2.py, configs/v2/vc_wrapper.yaml and
# modules/v2/vc_wrapper.py at SOURCE_CHECKOUT revision. Read-only arithmetic.
V2_GEOMETRY: Dict[str, Any] = {
    "configuration_id": "hubert-bsqvae-small-accent-style",
    "sample_rate_hz": 22050,
    "hop_size": 256,
    "n_fft": 1024,
    "win_size": 1024,
    "num_mels": 80,
    "fmin": 0,
    "fmax": None,
    "center": False,
    "mel_frame_rate": "22050/256",
    "max_context_window_mel_frames": 2580,
    "overlap_frame_len": 16,
    "overlap_wave_samples": 4096,
    "compile_len": 2610,
    "target_cap_samples": 551250,
    "ar_max_content_len": 1500,
    "content_hop_16k_samples": 320,
    "ssl_output_layer": 18,
    "codebook_narrow": 32,
    "codebook_wide": 2048,
    "ar_dim": 768,
    "ar_layers": 12,
    "ar_heads": 12,
    "ar_vocab_size": 2049,
    "cfm_depth": 13,
    "cfm_heads": 8,
    "cfm_block_size": 8192,
    "diffusion_steps": 30,
    "length_adjust": 1.0,
    "intelligibility_cfg_rate": 0.7,
    "similarity_cfg_rate": 0.7,
    "top_p": 0.9,
    "temperature": 1.0,
    "repetition_penalty": 1.0,
    "dtype": "float16",
    "convert_style": True,
    "anonymization_only": False,
    "content_tokenizer": "openai/whisper-small",
    "ssl_model": "facebook/hubert-large-ll60k",
    "vocoder": "nvidia/bigvgan_v2_22khz_80band_256x",
    "note": (
        "Read-only source-derived geometry. The 22050 Hz V2 path is not an "
        "installed v0 format; no model is loaded, converted or timed here."
    ),
}

REQUIRED_ASSETS: Tuple[Dict[str, str], ...] = (
    {"id": "cfm", "artifact": "v2/cfm_small.pth", "repo": "Plachta/Seed-VC"},
    {"id": "ar", "artifact": "v2/ar_base.pth", "repo": "Plachta/Seed-VC"},
    {"id": "ce_narrow", "artifact": "bsq32/bsq32_light.pth",
     "repo": "Plachta/ASTRAL-quantization"},
    {"id": "ce_wide", "artifact": "bsq2048/bsq2048_light.pth",
     "repo": "Plachta/ASTRAL-quantization"},
    {"id": "style_encoder", "artifact": "campplus_cn_common.bin",
     "repo": "funasr/campplus"},
)

ASSET_LEDGER: Dict[str, Any] = {
    "status": "absent_exact_v2_accent_assets_unidentified",
    "source_checkout": dict(SOURCE_CHECKOUT),
    "required_assets": [
        {
            "id": item["id"],
            "repo": item["repo"],
            "artifact": item["artifact"],
            "revision": None,
            "byte_count": None,
            "sha256": None,
            "present_locally": False,
            "note": "Source names the artifact; no local pinned identity exists.",
        }
        for item in REQUIRED_ASSETS
    ],
    "external_model_snapshots": [
        {"id": "vocoder", "repo": V2_GEOMETRY["vocoder"], "revision": None,
         "sha256": None, "present_locally": False},
        {"id": "whisper_tokenizer", "repo": V2_GEOMETRY["content_tokenizer"],
         "revision": None, "sha256": None, "present_locally": False},
        {"id": "hubert_ssl", "repo": V2_GEOMETRY["ssl_model"], "revision": None,
         "sha256": None, "present_locally": False},
    ],
    "runtime": {
        "status": "absent_unpinned",
        "lockfile": None,
        "sha256": None,
        "note": (
            "No Python/PyTorch/Transformers/Hydra/TorchCodec lockfile or "
            "offline loader is staged."
        ),
    },
    "rights": {
        "status": "unreviewed",
        "note": (
            "GPL-3.0 source text does not clear checkpoint, Whisper, HuBERT, "
            "BigVGAN, CAMPPlus, corpus, consent or product-use rights."
        ),
    },
    "downloaded": False,
    "vendored": False,
    "loaded": False,
    "executed": False,
}

BOUNDARY = {
    "benchmark_claim": False,
    "board_or_handoff_changed": False,
    "ci_changed": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "processor_exposure": False,
    "provider_registered": False,
    "public_api_abi_changed": False,
    "release_claim": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
    "format": {
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
    },
}

SCOPE = {
    "synthetic_only": True,
    "task_local_only": True,
    "real_audio": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "model_executed": False,
    "checkpoint_loaded": False,
    "network_used": False,
    "v2_accent_conversion_executed": False,
    "provider_registered": False,
}

NEGATIVE_CLAIMS = [
    "No Seed-VC V2 source is imported, built or executed by this package.",
    "No V2 AR, CFM, ASTRAL, CAMPPlus, BigVGAN, Whisper or HuBERT asset is downloaded, vendored, present or loaded.",
    "No consented accent cohort, target reference, real recording or listening result is present.",
    "The model-free integer geometry probe is not converted audio or a quality result.",
    "The v1 25M file run and v1 real-time GUI block are source-reported and excluded from V2 evidence.",
    "The XLS-R-300M content-encoder package is a separate component and cannot qualify V2 accent conversion.",
    "No device timing, first-output/tail measurement, benchmark, release claim or provider exposure is made.",
    "No missing, blocked or synthetic result qualifies the candidate.",
]

GATES = [
    {
        "id": "RG-01",
        "title": "exact_source_asset_and_runtime_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "The exact Seed-VC V2 source revision, AR/CFM/ASTRAL/CAMPPlus "
            "checkpoint identities, Whisper/HuBERT/BigVGAN snapshots and runtime "
            "lockfile must be pinned."
        ),
        "reopen_condition": (
            "Stage immutable asset IDs, revisions, byte counts and SHA-256 values "
            "plus the locked offline runtime."
        ),
    },
    {
        "id": "RG-02",
        "title": "caller_asset_boundary_and_v2_geometry",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Caller asset identity, configuration, 22050 Hz/1024/256/80 mel "
            "geometry, convert-style selection and runtime digest must be verified "
            "without loading an asset."
        ),
        "reopen_condition": (
            "Pass a hash-matched caller manifest against the pinned V2 geometry "
            "and reproduce the exact conversion path."
        ),
    },
    {
        "id": "RG-03",
        "title": "rights_consent_and_target_availability",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Code, checkpoints, third-party encoders/vocoder, target-accent "
            "reference, consent, output use and attribution require explicit review."
        ),
        "reopen_condition": "Reviewed rights and consent records clear every asset and the exact target condition.",
    },
    {
        "id": "RG-04",
        "title": "frozen_permitted_input_and_target_references",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Freeze permitted input and target references, task, accent labels and "
            "language/speaker groups for the exact V2 accent-style condition."
        ),
        "reopen_condition": "A rights-cleared, speaker-labeled and accent-labeled cohort is staged with pinned references.",
    },
    {
        "id": "RG-05",
        "title": "content_identity_and_naturalness_outcomes",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Text/semantic preservation, identity/similarity and naturalness must "
            "be scored as separate outcomes with pinned scorers and controls."
        ),
        "reopen_condition": "Produce separated content, identity and naturalness results on the frozen cohort.",
    },
    {
        "id": "RG-06",
        "title": "alignment_first_output_tail_and_target_condition",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Alignment, first-output/tail timing and the exact target condition "
            "must be recorded on the locked runtime, separately from file RTF."
        ),
        "reopen_condition": "Measure alignment and startup/finalization timing with the exact target reference and runtime.",
    },
    {
        "id": "RG-07",
        "title": "controls_adverse_cases_and_matched_baselines",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Identity, no-target, anonymization-only, invalid-manifest and "
            "cross-path controls must pass, with v1 and content-encoder evidence "
            "kept out of the V2 comparison."
        ),
        "reopen_condition": "Run pinned adverse controls and a task-matched V2 baseline comparison.",
    },
    {
        "id": "RG-08",
        "title": "opt_in_intake_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Opt-in provider intake, independent exact-head review and release "
            "approval are required before any exposure."
        ),
        "reopen_condition": "A separate versioned intake passes independent review with OFF default and explicit approval.",
    },
]

EXACT_BLOCKERS = [
    {
        "id": "XB-01",
        "title": "v2_accent_asset_identity_absent",
        "detail": (
            "The pinned source names v2/cfm_small.pth, v2/ar_base.pth, "
            "bsq32/bsq32_light.pth, bsq2048/bsq2048_light.pth and "
            "campplus_cn_common.bin, plus Whisper/HuBERT/BigVGAN snapshots, "
            "but no revision, byte count or SHA-256 is pinned for any of them."
        ),
        "reopen": (
            "Stage the exact licensed V2 asset identities with immutable "
            "revisions, byte counts and SHA-256 values, then verify them."
        ),
    },
    {
        "id": "XB-02",
        "title": "matched_runtime_and_geometry_unpinned",
        "detail": (
            "No locked Python/PyTorch/Transformers/Hydra/TorchCodec runtime or "
            "offline loader is staged. The 22050 Hz, 1024/256/80 mel, 30-step "
            "AR+CFM geometry is source-derived only and has not been executed."
        ),
        "reopen": (
            "Pin the exact runtime and V2 geometry, then reproduce the exact "
            "conversion path and byte-level output."
        ),
    },
    {
        "id": "XB-03",
        "title": "matched_consented_accent_cohort_absent",
        "detail": (
            "No permitted source/target reference, accent label, speaker/L1 "
            "grouping, target-accent gold, consent record, ASR scorer or blinded "
            "listening protocol is staged."
        ),
        "reopen": (
            "Stage a rights-cleared, consented, accent-labeled cohort with pinned "
            "references and scorers."
        ),
    },
    {
        "id": "XB-04",
        "title": "voice_profile_and_release_gates_unmet",
        "detail": (
            "No real V2 conversion, separated content/identity/naturalness "
            "outcome, first-output/tail timing, listening, benchmark, opt-in "
            "intake or independent release review exists."
        ),
        "reopen": (
            "Complete the Voice profile on the exact runtime and pass independent "
            "opt-in review with the default OFF."
        ),
    },
]

SOURCE_LINES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "v2_not_used_by_v1_gui_block",
        "path": "research/accent-conversion-20261101/README.md",
        "line": 98,
        "text": "separate Seed-VC V2 accent-conversion path.",
    },
    {
        "id": "v1_gui_block_timing",
        "path": "research/accent-conversion-20261101/README.md",
        "line": 101,
        "text": "254.01 s; conversion of the first block took 22.21 s, or 92.55× real-time.",
    },
    {
        "id": "v2_convert_style_is_accent_path",
        "path": "research/voice-conversion-eval-20261101/repos/seed-vc/inference_v2.py",
        "line": 133,
        "text": 'help="Convert style/emotion/accent for V2 model")',
    },
    {
        "id": "v2_convert_style_documented",
        "path": "research/voice-conversion-eval-20261101/repos/seed-vc/README.md",
        "line": 88,
        "text": (
            "--convert-style true # whether to use AR model for accent & "
            "emotion conversion, set to false will only conduct timbre "
            "conversion similar to V1"
        ),
    },
    {
        "id": "v1_25m_file_rtf_excluded",
        "path": "research/voice-conversion-eval-20261101/agent-breadth-audit/REPORT.md",
        "line": 26,
        "text": (
            "- Seed-VC 25M: 9.648 s file conversion; upstream runner measured "
            "warm RTF 0.244 after first-run RTF 1.32; ASR WER 0.00%; no "
            "clipping. The documented streaming GUI/device path was not tested."
        ),
    },
)

ABSENT_CANDIDATES: Tuple[str, ...] = (
    "data/models/seed-vc-v2/v2/cfm_small.pth",
    "data/checkpoints/seed-vc-v2",
    "research/voice-conversion-eval-20261101/repos/seed-vc/checkpoints",
    "research/voice-conversion-eval-20261101/repos/seed-vc/v2",
    "data/envs/seed-vc-v2",
    "adapters/seed-vc-v2",
)


class ReferenceRejection(ValueError):
    """Deterministic machine-readable rejection; no state is advanced."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True)


def canonical_bytes(value: Any) -> bytes:
    return (canonical_text(value) + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def strict_loads(text: str) -> Any:
    """Reject duplicate keys, nonfinite constants and unsupported values."""

    if not isinstance(text, str):
        raise ValueError("json_input_must_be_text")

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def constant(token: str) -> Any:
        raise ValueError("nonfinite_json_constant:" + token)

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json:" + str(error)) from error

    def check(item: Any) -> None:
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError("nonfinite_float")
        if isinstance(item, dict):
            for child in item.values():
                check(child)
        elif isinstance(item, list):
            for child in item:
                check(child)
        elif not isinstance(item, (str, int, float, bool)) and item is not None:
            raise ValueError("unsupported_json_type")

    check(value)
    return value


def strict_load(path: Path) -> Any:
    return strict_loads(path.read_text(encoding="utf-8"))


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Strict SHA-256 manifest parser; rejects duplicate or unsafe keys."""

    pattern = re.compile(r"^([0-9a-f]{64})  (\S+)$")
    seen: Dict[str, str] = {}
    result: List[Tuple[str, str]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError("bad_pin_line:" + str(number))
        digest, key = match.group(1), match.group(2)
        if key in seen:
            raise ValueError("duplicate_pin_key:" + key)
        if key.startswith("source:"):
            relative = key.split(":", 1)[1]
        else:
            relative = key
        if not relative or relative.startswith("/") or ".." in Path(relative).parts:
            raise ValueError("unsafe_pin_path:" + key)
        seen[key] = digest
        result.append((digest, key))
    return result


def local_pin_keys() -> Tuple[str, ...]:
    return tuple(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)


def allowed_pin_keys() -> Tuple[str, ...]:
    return tuple("source:" + path for path in sorted(SOURCE_PINS)) + tuple(
        sorted(BOUNDARY_PINS)) + local_pin_keys()


def qualify_pin_path(key: str) -> Path:
    if key.startswith("source:"):
        return SOURCE_ROOT / key.split(":", 1)[1]
    return SDK_ROOT / key


def readme_pin_rows() -> List[Tuple[str, str]]:
    """Parse the two fenced digest tables in README.md."""

    text = (TASK_DIR / "README.md").read_text(encoding="utf-8")
    start = "<!-- digest-table: source -->"
    middle = "<!-- digest-table: boundary -->"
    end = "<!-- digest-table: end -->"
    if text.count(start) != 1 or text.count(middle) != 1 or text.count(end) != 2:
        raise ValueError("digest_table_marker_mismatch")
    if text.index(start) >= text.index(middle):
        raise ValueError("digest_table_marker_order")
    rows: List[Tuple[str, str]] = []
    for block in (text.split(start, 1)[1].split(end, 1)[0],
                  text.split(middle, 1)[1].split(end, 1)[0]):
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) < 3 or lines[1] != "| --- | --- |":
            raise ValueError("digest_table_header_mismatch")
        for line in lines[2:]:
            if not line.startswith("| `") or not line.endswith("` |"):
                raise ValueError("digest_table_row_malformed")
            key, digest = [part.strip() for part in line.strip("|").split("|")]
            if not (key.startswith("`") and key.endswith("`")):
                raise ValueError("digest_table_key_malformed")
            if not (digest.startswith("`") and digest.endswith("`")):
                raise ValueError("digest_table_digest_malformed")
            rows.append((key[1:-1], digest[1:-1]))
    return rows


def board_link() -> Dict[str, Any]:
    payload = strict_load(SOURCE_ROOT / TASK_BOARD)
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        raise ValueError("invalid_task_board")
    rows = [row for row in payload["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    if len(rows) != 1:
        raise ValueError("task_row_not_unique")
    stable = {field: rows[0][field] for field in LINK_FIELDS}
    digest = object_digest(stable)
    if digest != BOARD_STABLE_SHA256:
        raise ValueError("unexpected_stable_board_identity")
    return {
        "stable_fields": stable,
        "stable_sha256": digest,
        "full_tasks_json_hashed": False,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
    }


def source_lines() -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for item in SOURCE_LINES:
        path = SOURCE_ROOT / item["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines[item["line"] - 1].strip() != item["text"]:
            raise ValueError("source_line_mismatch:" + item["id"])
        entries.append({
            "id": item["id"],
            "path": item["path"],
            "line": item["line"],
            "sha256": sha256_file(path),
            "text": item["text"],
        })
    return {"entries": entries, "line_count": len(entries)}


def validate_asset_pins() -> None:
    for path, digest in SOURCE_PINS.items():
        target = SOURCE_ROOT / path
        if not target.is_file():
            raise ValueError("missing_source_pin:" + path)
        if sha256_file(target) != digest:
            raise ValueError("stale_source_pin:" + path)
    for path, digest in BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file():
            raise ValueError("missing_boundary_pin:" + path)
        if sha256_file(target) != digest:
            raise ValueError("stale_boundary_pin:" + path)


CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "source_dir", "source_revision",
    "sample_rate_hz", "hop_size", "n_fft", "win_size", "num_mels", "center",
    "convert_style", "anonymization_only", "diffusion_steps", "length_adjust",
    "intelligibility_cfg_rate", "similarity_cfg_rate", "top_p", "temperature",
    "repetition_penalty", "runtime_lock_digest", "vocoder_revision",
    "whisper_revision", "hubert_revision", "target_reference_path",
    "target_reference_sha256", "target_reference_byte_count",
    "target_accent_label", "target_consent_id", "assets",
)


def _hex_digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    """Validate caller-supplied metadata only; never load or execute an asset."""

    if not isinstance(manifest, dict):
        raise ReferenceRejection("INVALID_MANIFEST", "manifest must be object")
    keys = set(manifest)
    expected = set(CALLER_MANIFEST_FIELDS)
    if keys != expected:
        if keys - expected:
            raise ReferenceRejection("UNKNOWN_FIELD", "extra manifest fields")
        raise ReferenceRejection("MISSING_FIELD", "missing manifest fields")
    if manifest["adapter"] != SCHEMA_MANIFEST:
        raise ReferenceRejection("UNKNOWN_ADAPTER", "unsupported adapter ID")
    if manifest["configuration_id"] != V2_GEOMETRY["configuration_id"]:
        raise ReferenceRejection("UNKNOWN_CONFIGURATION", "unsupported configuration")
    if manifest["source_revision"] != SOURCE_CHECKOUT["revision"]:
        raise ReferenceRejection("SOURCE_REVISION_MISMATCH", "source revision mismatch")
    if (manifest["sample_rate_hz"] != V2_GEOMETRY["sample_rate_hz"]
            or manifest["hop_size"] != V2_GEOMETRY["hop_size"]
            or manifest["n_fft"] != V2_GEOMETRY["n_fft"]
            or manifest["win_size"] != V2_GEOMETRY["win_size"]
            or manifest["num_mels"] != V2_GEOMETRY["num_mels"]
            or manifest["center"] is not False):
        raise ReferenceRejection("FORMAT_MISMATCH", "V2 reference format mismatch")
    if manifest["convert_style"] is not True:
        raise ReferenceRejection("ACCENT_PATH_NOT_SELECTED", "convert-style must be true")
    if manifest["anonymization_only"] is not False:
        raise ReferenceRejection("ANONYMIZATION_ONLY_NOT_ACCENT", "anonymization-only excluded")
    if (manifest["diffusion_steps"] != V2_GEOMETRY["diffusion_steps"]
            or manifest["length_adjust"] != V2_GEOMETRY["length_adjust"]
            or manifest["intelligibility_cfg_rate"] != V2_GEOMETRY["intelligibility_cfg_rate"]
            or manifest["similarity_cfg_rate"] != V2_GEOMETRY["similarity_cfg_rate"]
            or manifest["top_p"] != V2_GEOMETRY["top_p"]
            or manifest["temperature"] != V2_GEOMETRY["temperature"]
            or manifest["repetition_penalty"] != V2_GEOMETRY["repetition_penalty"]):
        raise ReferenceRejection("PARAMETER_MISMATCH", "V2 parameters mismatch")
    if not _hex_digest(manifest["runtime_lock_digest"]):
        raise ReferenceRejection("BAD_RUNTIME_DIGEST", "runtime lock digest malformed")
    for field in ("vocoder_revision", "whisper_revision", "hubert_revision"):
        if not isinstance(manifest[field], str) or not manifest[field].strip():
            raise ReferenceRejection("MISSING_MODEL_REVISION", field)
    if not isinstance(manifest["source_dir"], str) or not Path(
            manifest["source_dir"]).is_absolute():
        raise ReferenceRejection("RELATIVE_SOURCE", "source directory must be absolute")
    if not isinstance(manifest["target_reference_path"], str) or not Path(
            manifest["target_reference_path"]).is_absolute():
        raise ReferenceRejection("RELATIVE_TARGET", "target reference must be absolute")
    if not _hex_digest(manifest["target_reference_sha256"]):
        raise ReferenceRejection("BAD_TARGET_DIGEST", "target digest malformed")
    if not _positive_int(manifest["target_reference_byte_count"]):
        raise ReferenceRejection("BAD_TARGET_BYTE_COUNT", "target byte count malformed")
    if not isinstance(manifest["target_accent_label"], str) or not manifest[
            "target_accent_label"].strip():
        raise ReferenceRejection("MISSING_ACCENT_LABEL", "accent label required")
    if (not isinstance(manifest["target_consent_id"], str)
            or not manifest["target_consent_id"].strip()
            or manifest["target_consent_id"] == "unreviewed"):
        raise ReferenceRejection("MISSING_CONSENT", "consent record required")
    assets = manifest["assets"]
    if not isinstance(assets, list) or len(assets) != len(REQUIRED_ASSETS):
        raise ReferenceRejection("ASSET_SET_MISMATCH", "asset set mismatch")
    if {item.get("id") for item in assets if isinstance(item, dict)} != {
            item["id"] for item in REQUIRED_ASSETS}:
        raise ReferenceRejection("ASSET_SET_MISMATCH", "asset IDs mismatch")
    for item in assets:
        if set(item) != {"id", "path", "sha256", "byte_count", "revision"}:
            raise ReferenceRejection("BAD_ASSET_FIELDS", "asset fields mismatch")
        if not isinstance(item["path"], str) or not Path(item["path"]).is_absolute():
            raise ReferenceRejection("RELATIVE_ASSET_PATH", "asset path must be absolute")
        if not _hex_digest(item["sha256"]):
            raise ReferenceRejection("BAD_ASSET_DIGEST", "asset digest malformed")
        if not _positive_int(item["byte_count"]):
            raise ReferenceRejection("BAD_BYTE_COUNT", "asset byte count malformed")
        if not isinstance(item["revision"], str) or not item["revision"].strip():
            raise ReferenceRejection("MISSING_ASSET_REVISION", "asset revision required")
    for item in sorted(assets, key=lambda entry: entry["id"]):
        asset = Path(item["path"])
        if not asset.is_file():
            raise ReferenceRejection("ASSET_ABSENT", "declared asset is absent")
        if sha256_file(asset) != item["sha256"]:
            raise ReferenceRejection("ASSET_HASH_MISMATCH", "asset SHA-256 mismatch")
        if asset.stat().st_size != item["byte_count"]:
            raise ReferenceRejection("ASSET_SIZE_MISMATCH", "asset byte count mismatch")
    if not Path(manifest["source_dir"]).is_dir():
        raise ReferenceRejection("SOURCE_ABSENT", "declared source directory is absent")
    if not Path(manifest["target_reference_path"]).is_file():
        raise ReferenceRejection("TARGET_REFERENCE_ABSENT", "target reference is absent")
    raise ReferenceRejection(
        "V2_CHECKPOINT_IDENTITY_UNPINNED",
        "hash-matched caller assets still are not the pinned V2 accent assets")


def valid_manifest(cfm_path: str = "/absent/cfm_small.pth") -> Dict[str, Any]:
    assets = []
    for item in REQUIRED_ASSETS:
        assets.append({
            "id": item["id"],
            "path": (cfm_path if item["id"] == "cfm"
                     else "/absent/" + item["id"] + ".bin"),
            "sha256": "0" * 64,
            "byte_count": 1,
            "revision": "caller-declared-unverified",
        })
    return {
        "adapter": SCHEMA_MANIFEST,
        "configuration_id": V2_GEOMETRY["configuration_id"],
        "source_dir": str(SOURCE_ROOT / SOURCE_CHECKOUT["path"]),
        "source_revision": SOURCE_CHECKOUT["revision"],
        "sample_rate_hz": V2_GEOMETRY["sample_rate_hz"],
        "hop_size": V2_GEOMETRY["hop_size"],
        "n_fft": V2_GEOMETRY["n_fft"],
        "win_size": V2_GEOMETRY["win_size"],
        "num_mels": V2_GEOMETRY["num_mels"],
        "center": V2_GEOMETRY["center"],
        "convert_style": V2_GEOMETRY["convert_style"],
        "anonymization_only": V2_GEOMETRY["anonymization_only"],
        "diffusion_steps": V2_GEOMETRY["diffusion_steps"],
        "length_adjust": V2_GEOMETRY["length_adjust"],
        "intelligibility_cfg_rate": V2_GEOMETRY["intelligibility_cfg_rate"],
        "similarity_cfg_rate": V2_GEOMETRY["similarity_cfg_rate"],
        "top_p": V2_GEOMETRY["top_p"],
        "temperature": V2_GEOMETRY["temperature"],
        "repetition_penalty": V2_GEOMETRY["repetition_penalty"],
        "runtime_lock_digest": "0" * 64,
        "vocoder_revision": "caller-declared-unverified",
        "whisper_revision": "caller-declared-unverified",
        "hubert_revision": "caller-declared-unverified",
        "target_reference_path": "/absent/target_reference.wav",
        "target_reference_sha256": "0" * 64,
        "target_reference_byte_count": 1,
        "target_accent_label": "caller-declared-accent",
        "target_consent_id": "caller-declared-consent",
        "assets": assets,
    }


def duration_reduction(tokens: Sequence[int]) -> List[int]:
    """Source n-gram=1 duration reduction reproduced with integer tokens only."""

    if not tokens:
        raise ReferenceRejection("EMPTY_TOKEN_SEQUENCE", "no token sequence")
    reduced = [tokens[0]]
    reduced.extend(tokens[index] for index in range(1, len(tokens))
                   if tokens[index] != tokens[index - 1])
    return reduced


def geometry_probe() -> Dict[str, Any]:
    clip_samples = 22050 * 2
    mel_frames = (clip_samples - V2_GEOMETRY["n_fft"]) // V2_GEOMETRY["hop_size"] + 1
    content_samples_16k = clip_samples * 16000 // V2_GEOMETRY["sample_rate_hz"]
    content_frames = content_samples_16k // V2_GEOMETRY["content_hop_16k_samples"]
    flat = [4] * 24
    alternating = [4, 9] * 12
    flat_reduced = duration_reduction(flat)
    alternating_reduced = duration_reduction(alternating)
    return {
        "label": "model-free integer token/frame geometry; not V2 output",
        "source_revision": SOURCE_CHECKOUT["revision"],
        "clip_samples": clip_samples,
        "mel_frames_center_false": mel_frames,
        "content_samples_16k": content_samples_16k,
        "content_frames_16k": content_frames,
        "max_context_window_mel_frames": V2_GEOMETRY["max_context_window_mel_frames"],
        "overlap_wave_samples": V2_GEOMETRY["overlap_wave_samples"],
        "compile_len": V2_GEOMETRY["compile_len"],
        "target_cap_samples": V2_GEOMETRY["target_cap_samples"],
        "ar_max_content_len": V2_GEOMETRY["ar_max_content_len"],
        "duration_reduction": {
            "flat_token_digest": object_digest(flat),
            "flat_reduced_digest": object_digest(flat_reduced),
            "flat_reduced_count": len(flat_reduced),
            "alternating_token_digest": object_digest(alternating),
            "alternating_reduced_digest": object_digest(alternating_reduced),
            "alternating_reduced_count": len(alternating_reduced),
            "reduction_is_model_free": True,
        },
        "identity_control": {
            "alternating_token_sequence_byte_identical": True,
            "qualifies": False,
        },
        "nonfinite_count": 0,
        "out_of_range_count": 0,
        "note": (
            "Integer frame counts and source duration reduction only. No audio, "
            "mel, checkpoint, AR sampling or CFM inference is performed."
        ),
    }


def invalid_json_cases() -> Dict[str, Any]:
    cases = []
    for case_id, text in (
            ("duplicate_key", '{"a":1,"a":2}'),
            ("nan_constant", '{"a":NaN}'),
            ("infinity_constant", '{"a":Infinity}'),
            ("negative_infinity_constant", '{"a":-Infinity}'),
            ("trailing_data", '{"a":1} extra'),
            ("invalid_syntax", '{"a":'),
            ("empty_text", "")):
        try:
            strict_loads(text)
            accepted = True
            observed = "ACCEPTED"
        except ValueError:
            accepted = False
            observed = "INVALID_JSON"
        cases.append({"accepted": accepted, "id": case_id, "observed": observed})
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
    }


def invalid_pin_cases() -> Dict[str, Any]:
    digest = "a" * 64
    samples = (
        ("duplicate_key", digest + "  source:dup\n" + digest + "  source:dup\n"),
        ("short_digest", "abc  source:short\n"),
        ("missing_separator", digest + " source:missing\n"),
        ("absolute_path", digest + "  /absolute\n"),
        ("traversal", digest + "  source:../escape\n"),
    )
    cases = []
    for case_id, text in samples:
        try:
            parse_pin_lines(text)
            accepted = True
            observed = "ACCEPTED"
        except ValueError:
            accepted = False
            observed = "INVALID_PIN"
        cases.append({"accepted": accepted, "id": case_id, "observed": observed})
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
    }


def adverse_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []

    def probe(case_id: str, mutate: Any, candidate: Any = None) -> None:
        manifest = valid_manifest() if candidate is None else candidate
        mutate(manifest)
        try:
            validate_caller_manifest(manifest)
            observed = "ACCEPTED"
        except ReferenceRejection as error:
            observed = error.code
        cases.append({"accepted": observed == "ACCEPTED", "id": case_id,
                      "observed": observed})

    probe("missing_field", lambda m: m.pop("source_revision"))
    probe("unknown_field", lambda m: m.update({"unexpected": 1}))
    probe("wrong_adapter", lambda m: m.update({"adapter": "other"}))
    probe("wrong_configuration", lambda m: m.update({"configuration_id": "other"}))
    probe("wrong_source_revision", lambda m: m.update({"source_revision": "0" * 40}))
    probe("wrong_rate", lambda m: m.update({"sample_rate_hz": 16000}))
    probe("wrong_hop", lambda m: m.update({"hop_size": 512}))
    probe("wrong_n_fft", lambda m: m.update({"n_fft": 512}))
    probe("wrong_num_mels", lambda m: m.update({"num_mels": 128}))
    probe("convert_style_false", lambda m: m.update({"convert_style": False}))
    probe("anonymization_only_true", lambda m: m.update({"anonymization_only": True}))
    probe("wrong_diffusion_steps", lambda m: m.update({"diffusion_steps": 10}))
    probe("relative_cfm_path",
          lambda m: m["assets"][0].update({"path": "relative/cfm.pth"}))
    probe("absent_cfm", lambda m: None)
    probe("bad_cfm_digest",
          lambda m: m["assets"][0].update({"sha256": "f" * 64}))
    probe("bad_cfm_byte_count",
          lambda m: m["assets"][0].update({"byte_count": 0}))
    probe("bad_runtime_digest", lambda m: m.update({"runtime_lock_digest": "z" * 64}))
    probe("missing_consent", lambda m: m.update({"target_consent_id": "unreviewed"}))
    probe("manifest_not_object", lambda m: None, candidate=["not", "an", "object"])
    return {
        "case_count": len(cases),
        "cases": cases,
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "note": "All caller manifests fail closed before any asset load or execution.",
    }


def asset_pins_absent() -> bool:
    """No exact V2 asset identity may be present in the ledger."""

    if any(asset[key] is not None for asset in ASSET_LEDGER["required_assets"]
           for key in ("revision", "byte_count", "sha256")):
        return False
    if any(asset[key] is not None
           for asset in ASSET_LEDGER["external_model_snapshots"]
           for key in ("revision", "sha256")):
        return False
    return not any(ASSET_LEDGER[key] for key in
                   ("downloaded", "vendored", "loaded", "executed"))


def absent_artifact_probe() -> Dict[str, Any]:
    workspace_found = [path for path in ABSENT_CANDIDATES
                       if (SOURCE_ROOT / path).exists()]
    sdk_found: List[str] = []
    return {
        "note": "Bounded read-only path probes; no download, import or load attempted.",
        "present": False,
        "workspace_candidates": list(ABSENT_CANDIDATES),
        "workspace_found": workspace_found,
        "sdk_worktree_found": sdk_found,
        "method": "explicit candidate paths only; no recursive filesystem walk",
    }


def voice_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "permitted_input_and_target_references": {
                "status": "blocked",
                "evidence": "No consented source/target pair is pinned.",
            },
            "task_and_language_speaker_groups": {
                "status": "blocked",
                "evidence": "No accent-labeled or L1-grouped cohort is staged.",
            },
            "text_and_semantic_preservation": {
                "status": "model_free_only",
                "evidence": "Integer token identity control; no ASR or transcript scoring.",
            },
            "identity_similarity": {
                "status": "blocked",
                "evidence": "No speaker embedding or human identity rating is staged.",
            },
            "naturalness": {
                "status": "blocked",
                "evidence": "No listening panel or naturalness scorer is staged.",
            },
            "alignment": {
                "status": "model_free_only",
                "evidence": "Frame/token counts only; no converted-sample alignment.",
            },
            "first_output_and_tail_timing": {
                "status": "blocked",
                "evidence": "No runtime or device timing is measured.",
            },
            "exact_target_condition": {
                "status": "modelled_only",
                "evidence": "convert-style=true geometry is pinned; no target asset exists.",
            },
            "consent_reference_availability_output_use": {
                "status": "blocked",
                "evidence": "Consent, reference rights and output-use rights are unreviewed.",
            },
        },
    }


def source_reported() -> Dict[str, Any]:
    lines = source_lines()
    return {
        "entries": lines["entries"],
        "line_count": lines["line_count"],
        "v1_gui_block": {
            "block_ms": 240,
            "left_context_s": 2.2,
            "right_context_s": 0.2,
            "diffusion_steps": 10,
            "sample_rate_hz": 22050,
            "model_load_s": 254.01,
            "first_block_s": 22.21,
            "rtf": 92.55,
            "semantic_extraction_s": 12.20,
            "path": "v1 real-time GUI; explicitly not V2",
            "qualifies": False,
        },
        "v1_25m_file_mode": {
            "output_s": 9.648,
            "first_run_rtf": 1.32,
            "warm_rtf": 0.244,
            "asr_wer_percent": 0.0,
            "path": "v1 seed-uvit-tat-xlsr-tiny file conversion",
            "qualifies": False,
        },
        "v2_geometry_from_source": dict(V2_GEOMETRY),
        "excluded_from_v2_evidence": [
            "v1 real-time GUI 240 ms block and 92.55x RTF",
            "v1 25M file-mode first/warm RTF and single-pair output",
            "XLS-R-300M content-encoder blocker package",
            "MeanVC2, TokAN, Vocos and other candidate results",
        ],
        "listening_performed_here": False,
        "qualifies": False,
        "separation": (
            "All quoted timings and RTF values are source-reported v1 or other "
            "candidate results. None is a V2 accent conversion result or a local "
            "measurement; none qualifies this task."
        ),
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    probe = absent_artifact_probe()
    manifest_adverse = adverse_cases()
    json_adverse = invalid_json_cases()
    pin_adverse = invalid_pin_cases()
    geometry = geometry_probe()
    report: Dict[str, Any] = {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "no_missing_result_qualifies_candidate": True,
        "scope": dict(SCOPE),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "boundary": dict(BOUNDARY),
        "format": dict(BOUNDARY["format"]),
        "caller_supplied_asset_contract": {
            "schema_id": SCHEMA_MANIFEST,
            "required_fields": list(CALLER_MANIFEST_FIELDS),
            "configuration_id": V2_GEOMETRY["configuration_id"],
            "source_revision": SOURCE_CHECKOUT["revision"],
            "required_assets": [dict(item) for item in REQUIRED_ASSETS],
            "loaded": False,
            "executed": False,
            "note": (
                "Metadata-only reference. A hash-matched caller asset set still "
                "fails as V2_CHECKPOINT_IDENTITY_UNPINNED."
            ),
        },
        "v2_geometry": dict(V2_GEOMETRY),
        "geometry_probe": geometry,
        "voice_profile": voice_profile(),
        "available_evidence": {
            "status": "source_reported_only",
            "clock": "no runtime clock",
            "device_timing": False,
            "streaming_result": False,
            "content_delay_claim": False,
            "first_output_or_tail": "blocked_not_measured",
        },
        "asset_resolution": probe,
        "adverse": {
            "caller_manifest": manifest_adverse,
            "invalid_json": json_adverse,
            "invalid_pins": pin_adverse,
            "all_rejected": (manifest_adverse["all_rejected"]
                             and json_adverse["all_rejected"]
                             and pin_adverse["all_rejected"]),
            "metrics": None,
        },
        "comparison": {
            "status": "blocked_no_matched_v2_accent_assets_or_cohort",
            "identity_control": "integer token identity only; not V2 output",
            "task_matched_baseline": "blocked",
            "qualifies_candidate": False,
        },
        "source_reported": source_reported(),
        "model_provenance": {
            "source_revision": SOURCE_CHECKOUT["revision"],
            "source_license": SOURCE_CHECKOUT["license"],
            "required_assets": [dict(item) for item in ASSET_LEDGER["required_assets"]],
            "external_model_snapshots": [
                dict(item) for item in ASSET_LEDGER["external_model_snapshots"]
            ],
            "runtime": dict(ASSET_LEDGER["runtime"]),
        },
        "licensing_analysis": {
            "source_license": "GPL-3.0 (pinned LICENSE text)",
            "checkpoint_terms": "unreviewed",
            "third_party_model_terms": "unreviewed",
            "target_reference_and_consent": "unreviewed",
            "product_use": "unreviewed",
            "qualifies": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "exact V2 AR/CFM/ASTRAL/CAMPPlus/Whisper/HuBERT/BigVGAN asset identities",
            "locked offline runtime and reproduced 22050/1024/256/80 V2 geometry",
            "rights-cleared consented accent-labeled input/target cohort",
            "separated content, identity and naturalness outcomes",
            "alignment, first-output/tail timing, listening and opt-in review",
        ],
        "reopening_conditions": [item["reopen"] for item in EXACT_BLOCKERS],
        "evidence_classes": {
            "source_reported": True,
            "synthetic": True,
            "model_free_geometry": True,
            "real_local_model_output": False,
            "real_audio": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
        },
        "board_link": board_link(),
        "repeatability": {
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "fresh_builds": 3,
            "comparison": "exact SHA-256 over bytes; no tolerance",
        },
    }
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report())


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    lines = [
        "# SHA-256 pins for SDK-SEED-VC-V2-ACCENT-AWARE-PATH.",
        "# source: paths are workspace-relative; other external paths are SDK-worktree-relative.",
        "# Local paths are SDK-worktree-relative. Missing assets are ledger entries, not file pins.",
        "# The mutable full plan/swarm/TASKS.json is never pinned; only stable row identity is gated.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(SOURCE_PINS[path] + "  source:" + path)
    for path in sorted(BOUNDARY_PINS):
        lines.append(BOUNDARY_PINS[path] + "  " + path)
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (TASK_DIR / name).read_bytes()
        lines.append(sha256_bytes(payload) + "  " + TASK_PREFIX + name)
    return ("\n".join(lines) + "\n").encode("utf-8")


def contract_bytes(report_payload: bytes, sidecar_payload: bytes,
                   sources_payload: bytes, report: Dict[str, Any]) -> bytes:
    artifact_pins: Dict[str, str] = {}
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (TASK_DIR / name).read_bytes()
        artifact_pins[TASK_PREFIX + name] = sha256_bytes(payload)
    contract: Dict[str, Any] = {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "contract_version": "0.1",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "status": STATUS,
        "task_prefix": TASK_PREFIX,
        "format": dict(BOUNDARY["format"]),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "artifact_pins": artifact_pins,
        "report_sha256": sha256_bytes(report_payload),
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "sources_sha256": sha256_bytes(sources_payload),
        "board_link": board_link(),
        "caller_supplied_asset_contract": report["caller_supplied_asset_contract"],
        "source_reported": report["source_reported"],
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "invariants": [
            "Installed v0 remains 16 kHz mono float32 with 160-sample frames.",
            "Seed-VC V2 22050 Hz geometry is reference-only and not installable in v0.",
            "Only the task-local evidence directory is written.",
            "No source, checkpoint, audio or runtime artifact is bundled.",
            "Caller manifests are validated as metadata and never loaded or executed.",
            "v1 25M, v1 GUI and XLS-R content-encoder evidence is excluded from V2.",
            "Model-free integer controls cannot qualify the candidate.",
            "Only stable board-row identity enters canonical bytes or gates.",
        ],
    }
    return canonical_bytes(contract)


def _git(worktree: Path, *arguments: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else None


def scope_base(worktree: Path,
               refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base of HEAD with an available PR base ref."""

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
        if _git(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> List[str]:
    return [path for path in paths if path and not path.startswith(prefix)]
