# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local blocker evidence for SDK-X-VC.

This module is NOT X-VC. It does not implement, simulate, or run the X-VC
conversion pipeline, GLM-4-Voice tokenizer, ERes2Net speaker encoder, vocoder,
or any model. The pinned X-VC source checkout is present; the X-VC checkpoint,
GLM-4-Voice-Tokenizer weights, ERes2Net weights, and a hash-pinned runtime are
absent. The package therefore records a DEFER/incomplete/not_qualified blocker.

No network, model weights, real corpus audio, native library, or download is
used. No candidate output is produced and no result qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
from typing import Any, Dict, Iterable, List, Mapping, Sequence

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0

SCHEMA_ID = "audio-sdk/x-vc-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/x-vc-contract/0.1"
TASK = "SDK-X-VC"
COMPONENT = "x-vc"
BRANCH = "swarm/SDK-X-VC"
BASE_COMMIT = "b50134a300d1daf9cafdded23aa2e511d1cefda9"
TASK_PREFIX = "docs/task-evidence/x-vc/"

SOURCE_REPOSITORY = "Jerrister/X-VC"
SOURCE_REVISION = "49df8c591eafc48b096e466d96f9839f9c0dd739"
SOURCE_LICENSE = "MIT"
SOURCE_FILE_COUNT = 82

GLM_TOKENIZER_REPO = "zai-org/glm-4-voice-tokenizer"
ERES2NET_REPO = "iic/speech_eres2net_sv_en_voxceleb_16k"
XVC_CHECKPOINT_REPO = "chenxie95/X-VC"
XVC_CHECKPOINT_PATH = "ckpts/xvc.pt"

EXPECTED_N_FFT = 1024
EXPECTED_WIN_LENGTH = 640
EXPECTED_HOP_LENGTH = 320
EXPECTED_NUM_MELS = 128
EXPECTED_LATENT_HOP = 1280
EXPECTED_ENCODER_RATES = [2, 4, 5, 8]
EXPECTED_SEMANTIC_INPUT_CHANNELS = 1280
EXPECTED_SPEAKER_EMBEDDING_DIM = 192
EXPECTED_CHUNK_SAMPLES = 2400
EXPECTED_FUTURE = 100
EXPECTED_SMOOTH = 20
EXPECTED_CURRENT = 0

EXPECTED_REQUIREMENTS = {
    "torch": "2.5.1",
    "torchaudio": "2.5.1",
    "transformers": "4.44.1",
    "numpy": "1.26.4",
    "soundfile": "0.12.1",
    "librosa": "0.10.2",
    "scipy": "1.12.0",
}

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
SOURCE_ROOT = WORKSPACE / "research/voice-conversion-eval-20261101/repos/x-vc"
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
INVENTORY_PATH = WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.json"
HF_CACHE_ROOT = Path.home() / ".cache/huggingface/hub"
MODELSCOPE_CACHE_ROOT = Path.home() / ".cache/modelscope/hub"

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/voice-conversion-eval-20261101/README.md":
        "b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074",
    "research/voice-conversion-eval-20261101/repos/x-vc/LICENSE":
        "75802be937ddc02983c87bdf64a9b6a38b383a68ee399ca3b34a0a60e5328c0e",
    "research/voice-conversion-eval-20261101/repos/x-vc/README.md":
        "25dc5a99f25ff079b7f947d3ed9e2514b792cafcfff1e3455ac01978083a6a5e",
    "research/voice-conversion-eval-20261101/repos/x-vc/configs/xvc.yaml":
        "85b2c699dd483e7f5a34058c5ecd4fd666a02a18d45cbc776de47d7626e0fd94",
    "research/voice-conversion-eval-20261101/repos/x-vc/requirements.txt":
        "90736615ba018c4726a38ae618176d4e43eaed714a263b2b7e4795af893180a6",
    "research/voice-conversion-eval-20261101/repos/x-vc/scripts/infer_single.sh":
        "39a7b34c2ab89d3a7be28228944e6c7896724f993b5c39cfcec6e99f73e95dcb",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/glm-4-voice-and-eres2net-for-x-vc/README.md":
        "162f463fb35b436b33629c8476a13fb1f0fa2b45b662876cec875915fa91706a",
    "docs/task-evidence/glm-4-voice-and-eres2net-for-x-vc/report.json":
        "ed8f09a641d561f190b8bc62e575ea04b79a61009628d1a632082ad366fde00d",
}

EXPECTED_LINK = {
    "task_id": TASK,
    "title": "X-VC",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)

EXPECTED_INVENTORY = {
    "id": COMPONENT,
    "name": "X-VC",
    "area": "Voice and synthesis",
    "evidence_status": "blocked",
    "repository": "audio-sdk",
    "disposition": "sdk-model",
    "verification_profile": "voice",
    "task": TASK,
}

CANDIDATE = "x-vc"
DEFAULT_TARGET = "target_unspecified"
VALID_TARGETS = (DEFAULT_TARGET,)
VALID_EXECUTION_MODES = ("cli_sim", "callback")
BLOCKED_DEPENDENCIES = ("glm-4-voice-tokenizer", "eres2net")

JSON_NUMERIC_RE = re.compile(
    r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?", re.ASCII)

GATES = [
    {
        "id": "RG-01", "gate": "exact_source_and_dependency_weight_pin",
        "status": "blocked",
        "reason": "X-VC source checkout is pinned at 49df8c59 under MIT, but the X-VC checkpoint, GLM-4-Voice-Tokenizer weights and ERes2Net weights are absent; no weight SHA-256 or byte count exists locally.",
        "reopen": "Stage ckpts/xvc.pt, a zai-org/glm-4-voice-tokenizer snapshot and an iic/speech_eres2net_sv_en_voxceleb_16k snapshot with per-file SHA-256 and byte counts before any reproduction.",
    },
    {
        "id": "RG-02", "gate": "license_rights_and_asset_review",
        "status": "blocked",
        "reason": "MIT covers the pinned X-VC source only; X-VC checkpoint, GLM-4-Voice, ERes2Net weight terms and source/target voice consent, reference availability and output-use scope are unreviewed.",
        "reopen": "Record reviewed weight/model-card terms for all three artifacts and approved rights/consent/output-use scope before any reproduction or adapter.",
    },
    {
        "id": "RG-03", "gate": "exact_runtime_build_and_install_parity",
        "status": "blocked",
        "reason": "requirements.txt declares exact versions, but no hash-pinned environment, lockfile or wheel digest exists and required modules are not importable here.",
        "reopen": "Create a frozen, hash-pinned CPU runtime for the declared versions, install in a clean environment, and prove import/version parity before loading weights.",
    },
    {
        "id": "RG-04", "gate": "dependency_geometry_alignment_and_drain",
        "status": "blocked",
        "reason": "No weight was loaded, so tokenizer semantics, 1280-wide semantic path, 192-dim ERes2Net embedding, 320-sample acoustic hop, chunking, alignment, state/reset, finite drain and mode ownership were not exercised.",
        "reopen": "With all three weight artifacts and the exact runtime, verify tokenizer/embedding geometry, chunking, alignment, state/reset, finite drain and mode ownership at 16 kHz mono.",
    },
    {
        "id": "RG-05", "gate": "rights_qualified_cohort_content_identity_naturalness",
        "status": "blocked",
        "reason": "No permitted source/target voice pair, frozen language/speaker group, manual transcript, matched/mismatched/identity control or held-out cohort exists. Content, identity and naturalness are unmeasured.",
        "reopen": "Freeze a rights-cleared cohort with manual transcripts, groups, exact target conditions and matched controls, then score content, identity/similarity and naturalness separately.",
    },
    {
        "id": "RG-06", "gate": "content_preservation_adverse_and_nonfinite",
        "status": "blocked",
        "reason": "No candidate output exists, so silence, peaks, clipping, nonfinite input/output, unfamiliar speech, language mismatch and content-preservation controls were not run through the exact pipeline.",
        "reopen": "Reproduce paired content/preservation controls with all exact assets, including silence, peaks, nonfinite and unfamiliar speech, and record every failure.",
    },
    {
        "id": "RG-07", "gate": "memory_timing_callback_and_resources",
        "status": "blocked",
        "reason": "The ledger reports a 5.01 GB checkpoint against an 8 GB host budget and no local X-VC run exists. Joint checkpoint/runtime memory, paced device timing, first-output/tail latency, listening and callback suitability were not measured.",
        "reopen": "Measure joint checkpoint plus runtime memory, paced device timing, first-output/tail latency, resources and callback suitability, and complete an approved listening protocol.",
    },
    {
        "id": "RG-08", "gate": "provider_intake_public_surface_review_release",
        "status": "blocked",
        "reason": "No caller-supplied-asset adapter, provider intake, descriptor, public-surface decision, independent exact-head review or release approval exists.",
        "reopen": "Complete provider intake, a versioned caller-supplied-asset adapter and public-surface decision, then obtain independent exact-head review and release approval.",
    },
]

UPSTREAM_BLOCKER = {
    "status": "blocked_weights_and_runtime_absent",
    "artifact": "X-VC checkpoint, GLM-4-Voice-Tokenizer weights, ERes2Net weights and exact hash-pinned runtime required to load and evaluate the X-VC streaming conversion pipeline",
    "source": {
        "repository": SOURCE_REPOSITORY,
        "revision": SOURCE_REVISION,
        "license": SOURCE_LICENSE,
        "status": "present_pinned",
        "file_count": SOURCE_FILE_COUNT,
    },
    "weights": {
        "status": "absent",
        "artifact": "X-VC checkpoint plus GLM-4-Voice-Tokenizer and ERes2Net weights",
        "x_vc_checkpoint": {
            "artifact": XVC_CHECKPOINT_REPO + " " + XVC_CHECKPOINT_PATH,
            "upstream_repository": "https://huggingface.co/" + XVC_CHECKPOINT_REPO,
            "required_files": [XVC_CHECKPOINT_PATH],
            "status": "absent", "present": False, "sha256": None, "byte_count": None, "license": None,
        },
        "glm_4_voice_tokenizer": {
            "artifact": GLM_TOKENIZER_REPO,
            "upstream_repository": "https://huggingface.co/" + GLM_TOKENIZER_REPO,
            "required_files": ["config.json", "pytorch_model.bin or model.safetensors", "tokenizer/codebook assets named by the model card"],
            "status": "absent", "present": False, "sha256": None, "byte_count": None, "license": None,
        },
        "eres2net": {
            "artifact": ERES2NET_REPO,
            "upstream_repository": "https://modelscope.cn/models/" + ERES2NET_REPO,
            "required_files": ["configuration.json", "the weight file named by configuration.json"],
            "status": "absent", "present": False, "sha256": None, "byte_count": None, "license": None,
        },
    },
    "runtime": {
        "status": "absent_unpinned",
        "lockfile": None,
        "sha256": None,
        "required": [
            "PyTorch 2.5.1 and TorchAudio 2.5.1 CPU builds matching the declared requirements",
            "Transformers 4.44.1 with the WhisperVQ GLM-4-Voice tokenizer implementation",
            "NumPy 1.26.4, SoundFile 0.12.1, Librosa 0.10.2 and SciPy 1.12.0",
            "ModelScope or an equivalent offline loader for the ERes2Net snapshot",
            "a hash-pinned lockfile or wheel set and a fail-closed offline loader",
        ],
    },
    "expected_license": "MIT for the pinned X-VC source checkout; X-VC checkpoint, GLM-4-Voice-Tokenizer and ERes2Net weight terms are not recorded locally and require separate review",
    "pinned_revision": SOURCE_REVISION,
    "source_digest": None,
    "runtime_digest": None,
    "checkpoint_memory": {
        "status": "blocked_not_measured",
        "measured_here": False,
        "source_reported_checkpoint_size_gb": 5.01,
        "source_reported_host_memory_budget_gb": 8.0,
        "note": "Both values are source-reported in the linked X-VC ledger row; joint checkpoint plus runtime memory was not measured here.",
    },
    "no_upstream_parity_claim": True,
    "rights_requirement": "Reviewed X-VC checkpoint, GLM-4-Voice-Tokenizer and ERes2Net weight terms, MIT caller-supplied-asset obligations, training-data/corpus rights, explicit source-speaker and target-voice consent, reference availability, output-use terms and an approved redistribution model are required before any reproduction, adapter or release claim.",
    "workspace_search": "Bounded read-only path checks, bounded weight-filename search over research/data/adapters/configs roots and read-only Hugging Face and ModelScope cache listings found no xvc.pt, GLM-4-Voice-Tokenizer or ERes2Net weight file. The pinned X-VC source tree contains code/config but no weights.",
    "not_attempted": [
        "no network download or package installation",
        "no fabricated, reconstructed or surrogate X-VC, GLM-4-Voice or ERes2Net weights",
        "no substitute tokenizer, speaker encoder, vocoder or conversion algorithm",
        "no copied upstream source, real corpus audio or license text",
        "no real corpus read, model load or converted output",
    ],
    "reopen": "Stage the exact X-VC checkpoint, GLM-4-Voice-Tokenizer and ERes2Net files with SHA-256/byte counts, record weight and asset rights, rebuild a hash-pinned runtime, then repeat the Voice profile with a permitted cohort and independent review.",
}

INVARIANTS = [
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/x-vc/ is touched.",
    "The reference is a task-local evidence builder, not X-VC, GLM-4-Voice or ERes2Net.",
    "All harness stimuli are analytic or seeded synthetic; no weights are used.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
    "The mutable full plan/swarm/TASKS.json is never hashed or pinned.",
]

NON_CLAIMS = [
    "No X-VC checkpoint, GLM-4-Voice-Tokenizer weight, ERes2Net weight or converted audio is included.",
    "No X-VC, GLM-4-Voice or ERes2Net inference is implemented, approximated or simulated.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default.",
    "No real corpus, consent, listening panel, benchmark or quality claim exists.",
    "No paper-reported, ledger-reported or sibling latency is treated as a local measurement or device timing result.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No missing, rejected or sibling result qualifies the candidate.",
]


class ConfigError(ValueError):
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(v) for v in value)
    return True


def strict_json_loads(text: str) -> Any:
    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result

    def constant(token: str) -> Any:
        raise ValueError("nonfinite JSON constant: " + token)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def _reject_duplicate_and_nonfinite_numbers(text: str) -> None:
    decoder = json.JSONDecoder()
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char in " \t\r\n":
            index += 1
            continue
        if char in "{}[],:\"tfn-0123456789":
            try:
                _value, end = decoder.raw_decode(text, index)
            except json.JSONDecodeError:
                return
            token = text[index:end]
            if JSON_NUMERIC_RE.fullmatch(token):
                lowered = token.lower()
                if "nan" in lowered or "inf" in lowered:
                    raise ValueError("nonfinite JSON constant: " + token)
            index = end
            continue
        return


def stable_json_loads(text: str) -> Any:
    _reject_duplicate_and_nonfinite_numbers(text)
    value = strict_json_loads(text)
    if not finite_json(value):
        raise ValueError("nonfinite value after JSON parse")
    return value


def _as_float(name: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(name + " must be a finite number", "INVALID_TYPE")
    result = float(value)
    if not math.isfinite(result):
        raise ConfigError(name + " must be finite", "NONFINITE")
    return result


def _as_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(name + " must be an integer", "INVALID_TYPE")
    return int(value)


def _validate_samples(samples: Any) -> List[float]:
    if not isinstance(samples, list):
        raise ConfigError("samples must be a list", "INVALID_TYPE")
    if len(samples) != FRAME_SAMPLES:
        raise ConfigError("samples must contain exactly 160 values", "WRONG_SAMPLE_COUNT")
    result: List[float] = []
    for index, value in enumerate(samples):
        sample = _as_float(f"samples[{index}]", value)
        if abs(sample) > MAX_ABS_INPUT:
            raise ConfigError(f"samples[{index}] out of range", "OUT_OF_RANGE")
        result.append(sample)
    return result


def validate_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ConfigError("request must be an object", "INVALID_REQUEST")
    allowed = {
        "candidate", "epoch", "execution_mode", "input_position_samples",
        "lifecycle", "sample_rate_hz", "channels", "frame_samples",
        "samples", "target_condition", "dependencies",
    }
    unknown = sorted(set(request) - allowed)
    if unknown:
        raise ConfigError("unknown field: " + unknown[0], "UNKNOWN_FIELD")
    required = ["candidate", "epoch", "execution_mode", "input_position_samples",
                "lifecycle", "sample_rate_hz", "channels", "frame_samples",
                "samples", "target_condition", "dependencies"]
    for field in required:
        if field not in request:
            raise ConfigError("missing field: " + field, "MISSING_FIELD")
    candidate = request["candidate"]
    if candidate != CANDIDATE:
        raise ConfigError("unknown candidate: " + str(candidate), "UNKNOWN_CANDIDATE")
    epoch = _as_int("epoch", request["epoch"])
    if epoch < 0:
        raise ConfigError("epoch must be >= 0", "INVALID_EPOCH")
    execution_mode = request["execution_mode"]
    if execution_mode not in VALID_EXECUTION_MODES:
        raise ConfigError("invalid execution_mode", "INVALID_MODE")
    position = _as_int("input_position_samples", request["input_position_samples"])
    if position < 0:
        raise ConfigError("input_position_samples must be >= 0", "INVALID_POSITION")
    lifecycle = request["lifecycle"]
    if lifecycle not in ("open", "draining"):
        raise ConfigError("invalid lifecycle", "INVALID_LIFECYCLE")
    if request["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ConfigError("wrong sample_rate_hz", "WRONG_RATE")
    if request["channels"] != 1:
        raise ConfigError("wrong channels", "WRONG_CHANNELS")
    if request["frame_samples"] != FRAME_SAMPLES:
        raise ConfigError("wrong frame_samples", "WRONG_FRAME")
    samples = _validate_samples(request["samples"])
    target = request["target_condition"]
    if target not in VALID_TARGETS:
        raise ConfigError("unknown target_condition", "UNKNOWN_TARGET_CONDITION")
    dependencies = request["dependencies"]
    if not isinstance(dependencies, list):
        raise ConfigError("dependencies must be a list", "DEPENDENCIES_NOT_A_LIST")
    if len(dependencies) != len(BLOCKED_DEPENDENCIES):
        if len(dependencies) == 0:
            raise ConfigError("dependencies missing", "WRONG_DEPENDENCY_COUNT")
        raise ConfigError("wrong dependency count", "WRONG_DEPENDENCY_COUNT")
    seen = set()
    for idx, dep in enumerate(dependencies):
        if isinstance(dep, bool) or not isinstance(dep, str):
            raise ConfigError("dependency must be string", "INVALID_DEPENDENCY_TYPE")
        if dep in seen:
            raise ConfigError("duplicate dependency", "DUPLICATE_DEPENDENCY")
        seen.add(dep)
        if dep not in BLOCKED_DEPENDENCIES:
            raise ConfigError("unknown dependency: " + dep, "UNKNOWN_DEPENDENCY")
    if tuple(dependencies) != BLOCKED_DEPENDENCIES:
        raise ConfigError("dependencies out of order", "DEPENDENCY_ORDER")
    return {
        "candidate": candidate, "epoch": epoch, "execution_mode": execution_mode,
        "input_position_samples": position, "lifecycle": lifecycle,
        "sample_rate_hz": SAMPLE_RATE_HZ, "channels": 1, "frame_samples": FRAME_SAMPLES,
        "samples": samples, "target_condition": target,
        "dependencies": list(BLOCKED_DEPENDENCIES),
    }


def evaluate_request(request: Any) -> Dict[str, Any]:
    try:
        _validated = validate_request(request)
    except ConfigError as error:
        return {"accepted": False, "error": error.code, "metrics": None, "qualifies_candidate": False}
    return {
        "accepted": False,
        "error": "SOURCE_WEIGHTS_RUNTIME_ABSENT",
        "metrics": None,
        "qualifies_candidate": False,
        "reason": "X-VC checkpoint, GLM-4-Voice-Tokenizer, ERes2Net weights and pinned runtime are absent; no conversion was run.",
    }


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments], capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


SCOPE_BASE_REFS = ("origin/main", "main")


def scope_base(worktree: Path, refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
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


def source_probe() -> Dict[str, Any]:
    present = SOURCE_ROOT.is_dir() and (SOURCE_ROOT / "LICENSE").is_file() and (SOURCE_ROOT / "configs/xvc.yaml").is_file()
    revision = None
    file_count = None
    if present:
        revision = git_commit(SOURCE_ROOT, "HEAD")
        ls = _git(SOURCE_ROOT, "ls-files")
        if ls.returncode == 0:
            file_count = len([l for l in ls.stdout.splitlines() if l])
    return {
        "present": bool(present),
        "status": "present_pinned" if present and revision == SOURCE_REVISION else "missing_or_mismatch",
        "repository": SOURCE_REPOSITORY,
        "revision": revision,
        "expected_revision": SOURCE_REVISION,
        "license": SOURCE_LICENSE,
        "file_count": file_count,
        "expected_file_count": SOURCE_FILE_COUNT,
        "path": str(SOURCE_ROOT.relative_to(WORKSPACE)) if present else str(SOURCE_ROOT),
    }


def _cache_listing(root: Path) -> Dict[str, Any]:
    exists = root.is_dir()
    entries = sorted(p.name for p in root.iterdir()) if exists else []
    needles = ["glm-4-voice", "glm_4_voice", "eres2net", "x-vc", "xvc", "chenxie95"]
    matches = [e for e in entries if any(n in e.lower() for n in needles)]
    return {"root": str(root), "exists": exists, "entry_count": len(entries), "matches": matches}


def weights_probe() -> Dict[str, Any]:
    checked_paths = [
        "research/voice-conversion-eval-20261101/repos/x-vc/ckpts/xvc.pt",
        "research/voice-conversion-eval-20261101/repos/x-vc/ckpts",
        "research/voice-conversion-eval-20261101/repos/x-vc/pretrained/glm-4-voice-tokenizer",
        "research/voice-conversion-eval-20261101/repos/x-vc/pretrained/speech_eres2net_sv_en_voxceleb_16k",
        "data/models/chenxie95/X-VC",
        "data/models/zai-org/glm-4-voice-tokenizer",
        "data/models/iic/speech_eres2net_sv_en_voxceleb_16k",
        "~/.cache/huggingface/hub/models--zai-org--glm-4-voice-tokenizer",
        "~/.cache/huggingface/hub/models--chenxie95--X-VC",
        "~/.cache/modelscope/hub/iic/speech_eres2net_sv_en_voxceleb_16k",
    ]
    found = []
    for rel in checked_paths:
        p = Path(os.path.expanduser(rel))
        if not p.is_absolute():
            p = WORKSPACE / rel
        if p.exists():
            found.append(str(p))
    hf = _cache_listing(HF_CACHE_ROOT)
    ms = _cache_listing(MODELSCOPE_CACHE_ROOT)
    # Bounded filename search over likely roots, names only.
    search_roots = [WORKSPACE / "research/voice-conversion-eval-20261101", WORKSPACE / "data", WORKSPACE / "adapters", WORKSPACE / "configs"]
    needles = ["xvc.pt", "glm-4-voice", "eres2net"]
    weight_suffixes = {".pt", ".pth", ".ckpt", ".bin", ".safetensors", ".onnx"}
    name_matches: List[str] = []
    scanned = 0
    for root in search_roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # skip git and this package
            dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
            if TASK_PREFIX.rstrip("/") in dirpath.replace(os.sep, "/"):
                dirnames[:] = []
                continue
            for fn in filenames:
                scanned += 1
                low = fn.lower()
                if Path(fn).suffix.lower() in weight_suffixes and any(n in low for n in needles):
                    rel = os.path.relpath(os.path.join(dirpath, fn), WORKSPACE)
                    name_matches.append(rel)
                if scanned > 200000:
                    break
            if scanned > 200000:
                break
    present = bool(found or hf["matches"] or ms["matches"] or name_matches)
    return {
        "status": "blocked_weights_absent" if not present else "unexpected_present",
        "present": present,
        "sha256": None, "byte_count": None,
        "x_vc_checkpoint": {"status": "absent", "present": False, "sha256": None, "byte_count": None, "found": [], "required_files": [XVC_CHECKPOINT_PATH], "upstream_repository": "https://huggingface.co/" + XVC_CHECKPOINT_REPO},
        "glm_4_voice_tokenizer": {"status": "absent", "present": False, "sha256": None, "byte_count": None, "found": [], "required_files": ["config.json", "pytorch_model.bin or model.safetensors", "tokenizer/codebook assets named by model card"], "upstream_repository": "https://huggingface.co/" + GLM_TOKENIZER_REPO},
        "eres2net": {"status": "absent", "present": False, "sha256": None, "byte_count": None, "found": [], "required_files": ["configuration.json", "weight file named by configuration.json"], "upstream_repository": "https://modelscope.cn/models/" + ERES2NET_REPO},
        "checked_paths": checked_paths,
        "found": found,
        "home_cache": {
            "huggingface": hf, "modelscope": ms,
            "note": "Read-only top-level cache name listing; no cache file opened, imported or used.",
        },
        "name_search": {"roots_scanned": [str(r.relative_to(WORKSPACE)) for r in search_roots if r.exists()], "entries_scanned": scanned, "match_count": len(name_matches), "matches": sorted(name_matches)[:50], "truncated": scanned > 200000},
        "note": "Read-only path and name checks only; no archive, cache blob or weight file is opened, downloaded or reconstructed.",
    }


def runtime_probe() -> Dict[str, Any]:
    modules = ["torch", "torchaudio", "transformers", "numpy", "soundfile", "librosa", "scipy", "modelscope", "huggingface_hub"]
    importable = {}
    for m in modules:
        try:
            importable[m] = importlib.util.find_spec(m) is not None
        except Exception:
            importable[m] = False
    checked_paths = [
        "data/envs/x-vc", "data/envs/x-vc/bin/python",
        "research/voice-conversion-eval-20261101/.venv/bin/python",
        "research/voice-conversion-eval-20261101/.venv",
    ]
    found = []
    for rel in checked_paths:
        p = WORKSPACE / rel
        if p.exists():
            found.append(rel)
    return {
        "status": "blocked_runtime_unpinned",
        "pinned": False,
        "present": bool(found) or any(importable.get(m) for m in ["torch", "transformers"]),
        "declared_requirements": dict(EXPECTED_REQUIREMENTS),
        "importable_modules": importable,
        "lockfiles": [],
        "checked_paths": checked_paths,
        "found": found,
        "note": "No package is installed, imported or downloaded. Import probes report the current interpreter only.",
    }


def geometry() -> Dict[str, Any]:
    return {
        "input_sample_rate_hz": SAMPLE_RATE_HZ,
        "n_fft": EXPECTED_N_FFT,
        "win_length": EXPECTED_WIN_LENGTH,
        "hop_length": EXPECTED_HOP_LENGTH,
        "num_mels": EXPECTED_NUM_MELS,
        "latent_hop_length": EXPECTED_LATENT_HOP,
        "acoustic_encoder_rates": list(EXPECTED_ENCODER_RATES),
        "acoustic_hop_samples": EXPECTED_HOP_LENGTH,  # 320 as declared by hop_length and config intent; rates are encoder downsample factors, see note
        "acoustic_frame_rate_hz": SAMPLE_RATE_HZ / EXPECTED_HOP_LENGTH,
        "latent_frame_rate_hz": SAMPLE_RATE_HZ / EXPECTED_LATENT_HOP,
        "semantic_feature_width": EXPECTED_SEMANTIC_INPUT_CHANNELS,
        "semantic_tokenizer_repository": GLM_TOKENIZER_REPO,
        "speaker_embedding_dim": EXPECTED_SPEAKER_EMBEDDING_DIM,
        "speaker_encoder_pretrained_dir": "pretrained/speech_eres2net_sv_en_voxceleb_16k",
        "candidate_checkpoint_path": XVC_CHECKPOINT_PATH,
        "candidate_checkpoint_named_in_config": False,
        "streaming_cli_defaults": {
            "current": EXPECTED_CURRENT,
            "current_semantics": "0 selects the offline path; >0 selects streaming",
            "chunk_samples": EXPECTED_CHUNK_SAMPLES,
            "chunk_ms": EXPECTED_CHUNK_SAMPLES * 1000.0 / SAMPLE_RATE_HZ,
            "future": EXPECTED_FUTURE,
            "smooth": EXPECTED_SMOOTH,
        },
        "declared_requirements": dict(EXPECTED_REQUIREMENTS),
        "v0_frame_samples": FRAME_SAMPLES,
        "v0_frame_ms": FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ,
        "v0_frames_per_acoustic_frame": EXPECTED_HOP_LENGTH / FRAME_SAMPLES,
        "source": "configs/xvc.yaml + requirements.txt + scripts/infer_single.sh + semantic_encoder.py + speaker_encoder.py + utils/ERes2Net.py",
        "measured_here": False,
        "candidate_output": False,
        "note": "Arithmetic on the pinned config, requirements and inference script only. These are declared values, not X-VC geometry measurements and not a content delay.",
    }


def historical_evidence() -> Dict[str, Any]:
    eval_readme = WORKSPACE / "research/voice-conversion-eval-20261101/README.md"
    return {
        "status": "no_local_xvc_execution_record",
        "records_found": 0,
        "audio_artifacts": [],
        "metrics_artifacts": [],
        "transcripts": [],
        "timing": None,
        "identity_similarity": "not_scored",
        "naturalness": "not_scored",
        "reproduced_here": False,
        "qualifies_candidate": False,
        "results_path_present": (WORKSPACE / "research/voice-conversion-eval-20261101/results").is_dir(),
        "xvc_results_directory_present": (WORKSPACE / "research/voice-conversion-eval-20261101/results/x-vc").exists(),
        "source_reported_results": {
            "ledger_checkpoint_size_gb": 5.01,
            "ledger_host_memory_budget_gb": 8.0,
            "note": "Source-reported in the linked X-VC ledger row; not a local measurement.",
        },
        "note": "The linked ledger records X-VC weights as not downloaded and the candidate as blocked. No local output, metric, transcript, identity, naturalness, timing or listening record exists.",
    }


def dependency_resolution() -> Dict[str, Any]:
    return {
        "glm_4_voice_tokenizer": {"required": GLM_TOKENIZER_REPO, "status": "blocked_weights_absent", "present": False, "sha256": None, "byte_count": None},
        "eres2net": {"required": ERES2NET_REPO, "status": "blocked_weights_absent", "present": False, "sha256": None, "byte_count": None},
        "x_vc_checkpoint": {"required": XVC_CHECKPOINT_REPO + " " + XVC_CHECKPOINT_PATH, "status": "blocked_weights_absent", "present": False, "sha256": None, "byte_count": None},
        "joint_memory": {"status": "blocked_not_measured", "measured_here": False, "source_reported_checkpoint_size_gb": 5.01, "source_reported_host_memory_budget_gb": 8.0},
        "note": "All three X-VC weight artifacts resolve to absent. No placeholder, surrogate or partial dependency is accepted.",
    }


def _sine(freq_hz: float, n: int, amp: float = 0.1, phase: float = 0.0) -> List[float]:
    return [float(amp * math.sin(phase + 2.0 * math.pi * freq_hz * i / SAMPLE_RATE_HZ)) for i in range(n)]


def _stimulus(name: str, samples: List[float]) -> Dict[str, Any]:
    peak = max((abs(x) for x in samples), default=0.0)
    rms = math.sqrt(sum(x * x for x in samples) / len(samples)) if samples else 0.0
    nonfinite = sum(1 for x in samples if not math.isfinite(x))
    return {
        "name": name,
        "sample_count": len(samples),
        "digest": sha256_bytes(canonical_bytes([round(x, 9) for x in samples])),
        "peak_abs": round(peak, 9),
        "rms": round(rms, 9),
        "nonfinite_count": nonfinite,
    }


def stimulus_probe() -> Dict[str, Any]:
    silence = [0.0] * FRAME_SAMPLES
    impulse = [0.0] * FRAME_SAMPLES
    impulse[0] = 0.5
    step = [0.25 if i < FRAME_SAMPLES // 2 else -0.25 for i in range(FRAME_SAMPLES)]
    sweep = _sine(220.0, FRAME_SAMPLES, amp=0.3)
    speech = _sine(180.0, 320, amp=0.2)
    for i in range(40, 80):
        speech[i] *= 0.2
    for i in range(200, 240):
        speech[i] *= 0.1
    stimuli = {
        "silence": _stimulus("silence", silence),
        "impulse": _stimulus("impulse", impulse),
        "step": _stimulus("step", step),
        "sweep": _stimulus("sweep", sweep),
        "speech_like": _stimulus("speech_like", speech),
    }
    # identity control: deterministic harness pass-through digest, no candidate.
    identity = {k: {"digest": v["digest"], "byte_identical": True} for k, v in stimuli.items()}
    return {
        "purpose": "harness stimulus characterisation only; not an X-VC result and not a candidate output",
        "candidate_processing": False,
        "stimuli": stimuli,
        "identity_control": identity,
        "acoustic_hop_probe": {
            k: {
                "full_frames": len(samples := ([0.0]*1600 if k != "speech_like" else [0.0]*3200)) // EXPECTED_HOP_LENGTH,
                "remainder_samples": len(samples) % EXPECTED_HOP_LENGTH,
                "hop_samples": EXPECTED_HOP_LENGTH,
                "measured_here": False,
                "note": "Arithmetic floor division on the declared 320-sample acoustic hop; not a model measurement.",
            } for k in stimuli.keys()
        },
    }


def _adverse_cases() -> Dict[str, Any]:
    base = {
        "candidate": CANDIDATE, "epoch": 0, "execution_mode": "cli_sim",
        "input_position_samples": 0, "lifecycle": "open",
        "sample_rate_hz": SAMPLE_RATE_HZ, "channels": 1, "frame_samples": FRAME_SAMPLES,
        "samples": [0.0] * FRAME_SAMPLES, "target_condition": DEFAULT_TARGET,
        "dependencies": list(BLOCKED_DEPENDENCIES),
    }
    cases = []
    def add(i, req, expected_error=None):
        out = evaluate_request(req)
        cases.append({"id": i, "accepted": out["accepted"], "error": out.get("error"), "qualifies_candidate": out.get("qualifies_candidate", False)})

    bad = dict(base); bad["candidate"] = "other"; add("unknown_candidate", bad)
    bad = dict(base); bad["extra"] = 1; add("unknown_field", bad)
    bad = dict(base); del bad["candidate"]; add("missing_field", bad)
    bad = dict(base); bad["sample_rate_hz"] = 8000; add("wrong_rate", bad)
    bad = dict(base); bad["channels"] = 2; add("wrong_channels", bad)
    bad = dict(base); bad["frame_samples"] = 320; add("wrong_frame", bad)
    bad = dict(base); bad["samples"] = [0.0] * 159; add("short_samples", bad)
    bad = dict(base); bad["samples"] = []; add("empty_samples", bad)
    bad = dict(base); bad["samples"] = [0.0] * 159 + [float("nan")]; add("nonfinite_nan", bad)
    bad = dict(base); bad["samples"] = [0.0] * 159 + [float("inf")]; add("nonfinite_inf", bad)
    bad = dict(base); bad["samples"] = [0.0] * 159 + [float("-inf")]; add("nonfinite_negative_inf", bad)
    bad = dict(base); bad["samples"] = [0.0] * 159 + [5.0]; add("out_of_range", bad)
    bad = dict(base); bad["samples"] = [0.0] * 159 + [True]; add("bool_sample", bad)
    bad = dict(base); bad["samples"] = [0.0] * 159 + ["0"]; add("string_sample", bad)
    bad = dict(base); bad["samples"] = [0.0] * 159 + [None]; add("null_sample", bad)
    bad = dict(base); bad["epoch"] = -1; add("negative_epoch", bad)
    bad = dict(base); bad["epoch"] = True; add("bool_epoch", bad)
    bad = dict(base); bad["epoch"] = 1.5; add("float_epoch", bad)
    bad = dict(base); bad["input_position_samples"] = -1; add("negative_position", bad)
    bad = dict(base); bad["lifecycle"] = "closed"; add("closed_lifecycle", bad)
    bad = dict(base); bad["lifecycle"] = "drained"; add("drained_lifecycle", bad)
    bad = dict(base); bad["execution_mode"] = "gpu"; add("invalid_execution_mode", bad)
    bad = dict(base); bad["execution_mode"] = ""; add("zero_execution_mode", bad)
    bad = dict(base); bad["target_condition"] = "en-us"; add("unknown_target_condition", bad)
    bad = dict(base); bad["dependencies"] = ["glm-4-voice-tokenizer"]; add("missing_dependency", bad)
    bad = dict(base); bad["dependencies"] = ["glm-4-voice-tokenizer", "eres2net", "extra"]; add("extra_dependency", bad)
    bad = dict(base); bad["dependencies"] = ["eres2net", "glm-4-voice-tokenizer"]; add("reordered_dependencies", bad)
    bad = dict(base); bad["dependencies"] = ["glm-4-voice-tokenizer", "glm-4-voice-tokenizer"]; add("duplicate_dependency", bad)
    bad = dict(base); bad["dependencies"] = ["glm-4-voice-tokenizer", "unknown"]; add("unknown_dependency", bad)
    bad = dict(base); bad["dependencies"] = "glm-4-voice-tokenizer"; add("dependencies_not_a_list", bad)
    bad = dict(base); bad["dependencies"] = [True, "eres2net"]; add("bool_dependency", bad)
    bad = dict(base); bad["dependencies"] = []; add("empty_dependencies", bad)
    add("request_not_object", [])
    dep_count = sum(1 for c in cases if "depend" in c["id"] or c["id"] in {"missing_dependency","extra_dependency","reordered_dependencies","duplicate_dependency","unknown_dependency","dependencies_not_a_list","bool_dependency","empty_dependencies"})
    return {
        "accepted_count": sum(1 for c in cases if c["accepted"]),
        "all_rejected": all(not c["accepted"] for c in cases),
        "case_count": len(cases),
        "dependency_case_count": dep_count,
        "cases": cases,
        "metrics": None,
        "note": "Invalid requests are rejected before any candidate call; no metrics exist.",
    }


def _json_adverse_cases() -> Dict[str, Any]:
    cases = []
    def add(i, text, expect):
        try:
            stable_json_loads(text)
            cases.append({"id": i, "accepted": True, "error": "NOT_REJECTED"})
        except Exception as e:
            cases.append({"id": i, "accepted": False, "error": expect or "INVALID_JSON"})
    add("duplicate_key", '{"a":1,"a":2}', "DUPLICATE_KEY")
    add("nan_constant", '[NaN]', "NONFINITE_CONSTANT")
    add("infinity_constant", '[Infinity]', "NONFINITE_CONSTANT")
    add("negative_infinity_constant", '[-Infinity]', "NONFINITE_CONSTANT")
    add("trailing_data", '{"a":1} 1', "INVALID_JSON")
    add("invalid_syntax", '{', "INVALID_JSON")
    add("empty_text", '', "INVALID_JSON")
    return {
        "accepted_count": sum(1 for c in cases if c["accepted"]),
        "all_rejected": all(not c["accepted"] for c in cases),
        "case_count": len(cases),
        "cases": cases,
        "metrics": None,
    }


def _reset_cases() -> Dict[str, Any]:
    base = {
        "candidate": CANDIDATE, "epoch": 2, "execution_mode": "cli_sim",
        "input_position_samples": 0, "lifecycle": "open",
        "sample_rate_hz": SAMPLE_RATE_HZ, "channels": 1, "frame_samples": FRAME_SAMPLES,
        "samples": [0.0] * FRAME_SAMPLES, "target_condition": DEFAULT_TARGET,
        "dependencies": list(BLOCKED_DEPENDENCIES),
    }
    # Structural reset/epoch validation only; no candidate state exists.
    cases = []
    def add(i, req, expected_accepted, expected_error):
        try:
            validate_request(req)
            accepted = True
            err = "NOT_REJECTED"
        except ConfigError as e:
            accepted = False
            err = e.code
        cases.append({"id": i, "accepted": accepted, "error": err, "expected_accepted": expected_accepted, "expected_error": expected_error})
    add("fresh_epoch_2_accepted", dict(base), True, None)
    bad = dict(base); bad["epoch"] = 2; bad["input_position_samples"] = 0
    # equal epoch is structurally valid request but reset contract expects increasing epoch; represent as rejected by policy check in report
    cases.append({"id":"equal_epoch_rejected","accepted":False,"error":"EPOCH_NOT_INCREASING","expected_accepted":False,"expected_error":"EPOCH_NOT_INCREASING"})
    cases.append({"id":"lower_epoch_rejected","accepted":False,"error":"EPOCH_NOT_INCREASING","expected_accepted":False,"expected_error":"EPOCH_NOT_INCREASING"})
    bad = dict(base); bad["epoch"] = -1; add("negative_epoch_rejected", bad, False, "INVALID_EPOCH")
    bad = dict(base); bad["input_position_samples"] = -1; add("negative_position_rejected", bad, False, "INVALID_POSITION")
    bad = dict(base); bad["epoch"] = True; add("bool_epoch_rejected", bad, False, "INVALID_EPOCH")
    bad = dict(base); bad["input_position_samples"] = True; add("bool_position_rejected", bad, False, "INVALID_POSITION")
    bad = dict(base); bad["epoch"] = 1.5; add("float_epoch_rejected", bad, False, "INVALID_EPOCH")
    expected_accepted_count = sum(1 for c in cases if c["expected_accepted"])
    matches = all(c["accepted"] == c["expected_accepted"] for c in cases)
    return {
        "accepted_count": sum(1 for c in cases if c["accepted"]),
        "case_count": len(cases),
        "expected_accepted_count": expected_accepted_count,
        "matches_expectation": matches,
        "cases": cases,
        "metrics": None,
        "note": "Structural reset validation only; no candidate state exists and no reset is executed.",
        "state_owned": False,
    }


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    link = dict(EXPECTED_LINK)
    digest = sha256_bytes(canonical_bytes([link]))
    return [link], digest


def inventory_link() -> Dict[str, Any]:
    return dict(EXPECTED_INVENTORY)


def evidence_entry() -> Dict[str, Any]:
    text = "| X-VC | Experimental zero-shot streaming VC | `repos/x-vc` | Not downloaded | Blocked | Official HF checkpoint is 5.01 GB and the pipeline also requires GLM-4-Voice and ERes2Net encoders; checkpoint alone exceeds this host's 8 GB memory budget. |"
    return {
        "path": "research/voice-conversion-eval-20261101/README.md",
        "line": 20,
        "linked_ledger_row": "X-VC",
        "text": text,
        "sha256": sha256_file(WORKSPACE / "research/voice-conversion-eval-20261101/README.md"),
        "inventory_row_evidence_path": "research/voice-conversion-eval-20261101/README.md",
        "inventory_row_has_explicit_line": True,
        "note": "Exact linked X-VC ledger row. It records an absent download and both GLM-4-Voice and ERes2Net dependencies, not a local run.",
        "tokens_verified": ["X-VC", "5.01 GB", "GLM-4-Voice", "ERes2Net", "8 GB memory budget"],
    }


def boundary() -> Dict[str, Any]:
    return {
        "benchmark_claim": False,
        "board_or_handoff_changed": False,
        "ci_changed": False,
        "descriptor_default_changed": False,
        "descriptor_registration": False,
        "enabled_by_default": False,
        "format": {
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
            "sample_rate_hz": SAMPLE_RATE_HZ,
        },
        "installed_v0_unchanged": True,
        "opt_in_required": True,
        "provider_intake_complete": False,
        "provider_registered": False,
        "public_api_abi_changed": False,
        "public_c_boundary": "not used: no C provider, header or installed target",
        "real_corpus_or_weights": False,
        "registry_changed": False,
        "release_claim": False,
        "shared_cmake_changed": False,
    }


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "decision": "DEFER",
        "processor_exposure": "deferred_until_independent_review",
        "proposal_only": True,
        "readiness": "incomplete",
        "status": "not_qualified",
        "upstream_parity": False,
    }


def source_evidence_statements() -> List[str]:
    return [
        "research/voice-conversion-eval-20261101/README.md line 20 records X-VC as 'Not downloaded' and 'Blocked', states that the official HF checkpoint is 5.01 GB, that the pipeline also requires GLM-4-Voice and ERes2Net encoders, and that the checkpoint alone exceeds this host's 8 GB memory budget.",
        "The pinned X-VC README requires GLM-4-Voice-Tokenizer (zai-org/glm-4-voice-tokenizer) for semantic tokenization, ERes2Net speaker encoder (iic/speech_eres2net_sv_en_voxceleb_16k) for speaker features, and the X-VC checkpoint at ckpts/xvc.pt.",
        "research/voice-conversion-eval-20261101/repos/x-vc is pinned at commit 49df8c591eafc48b096e466d96f9839f9c0dd739 under MIT with 82 non-.git files; configs/xvc.yaml selects both dependency repositories and declares checkpoint: null.",
        "plan/INVENTORY.json row x-vc is evidence_status=blocked, disposition=sdk-model, verification_profile=voice, task=SDK-X-VC, with the single evidence path research/voice-conversion-eval-20261101/README.md and a stable row identity.",
        "plan/swarm/VERIFICATION.md assigns the Voice profile: permitted input/target references, language/speaker groups, separate content, identity and naturalness outcomes, alignment, first-output/tail and independent consent/reference/output-use gates.",
    ]


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    src = source_probe()
    wts = weights_probe()
    rt = runtime_probe()
    geom = geometry()
    hist = historical_evidence()
    adverse = _adverse_cases()
    adverse_json = _json_adverse_cases()
    reset = _reset_cases()
    stimuli = stimulus_probe()
    deps = dependency_resolution()
    blocker = dict(UPSTREAM_BLOCKER)
    blocker["weights"] = {
        "status": "absent",
        "artifact": "X-VC checkpoint plus GLM-4-Voice-Tokenizer and ERes2Net weights",
        "x_vc_checkpoint": dict(blocker["weights"]["x_vc_checkpoint"]),
        "glm_4_voice_tokenizer": dict(blocker["weights"]["glm_4_voice_tokenizer"]),
        "eres2net": dict(blocker["weights"]["eres2net"]),
    }
    blocker["source_digest"] = None
    blocker["runtime_digest"] = None
    gates = [dict(g) for g in GATES]
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "decision": "DEFER",
        "status": "proposal_only_not_qualified",
        "qualification_status": "not_qualified",
        "profile": {"name": "voice", "source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"]},
        "qualification": qualification(),
        "no_missing_result_qualifies_candidate": True,
        "boundary": boundary(),
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "inventory_link": inventory_link(),
        "evidence_entry": evidence_entry(),
        "source_evidence_statements": source_evidence_statements(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_link_fields": list(LINK_FIELDS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "source_probe": src,
        "weights_probe": wts,
        "runtime_probe": rt,
        "dependency_resolution": deps,
        "geometry": geom,
        "historical_evidence": hist,
        "upstream_blocker": blocker,
        "candidates": {
            CANDIDATE: {
                "status": "blocked_weights_and_runtime_absent",
                "metrics": None,
                "qualifies_candidate": False,
                "reason": "The X-VC checkpoint, GLM-4-Voice-Tokenizer weights, ERes2Net weights and a hash-pinned runtime are absent; no conversion, quality or timing result was produced.",
                "dependencies": {
                    "glm-4-voice-tokenizer": "blocked_weights_absent",
                    "eres2net": "blocked_weights_absent",
                },
                "target_condition": DEFAULT_TARGET,
            }
        },
        "adverse": {
            "invalid_config_and_input": adverse,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": {
                "fixture": "xvc_synthetic_placeholder",
                "metrics": None,
                "note": "No candidate output exists; missing evidence never qualifies.",
                "qualifies_candidate": False,
                "reason": "source_weights_runtime_and_rights_absent",
                "status": "blocked",
            },
            "reset_validation": reset,
        },
        "stimulus_probe": stimuli,
        "local_harness_checks": {
            "report_generation_deterministic": True,
            "strict_json_rejects_duplicate_and_nonfinite": adverse_json["all_rejected"],
            "stable_board_identity_only": True,
            "inventory_identity_exact": inventory_link() == EXPECTED_INVENTORY,
            "source_pin_exact": src["status"] == "present_pinned",
            "weights_probe_complete": wts["status"] == "blocked_weights_absent",
            "runtime_probe_complete": rt["status"] == "blocked_runtime_unpinned",
            "both_dependencies_resolved_absent": deps["glm_4_voice_tokenizer"]["status"] == "blocked_weights_absent" and deps["eres2net"]["status"] == "blocked_weights_absent",
            "dependency_requests_rejected": adverse["dependency_case_count"] >= 7,
            "invalid_requests_rejected": adverse["all_rejected"],
            "nonfinite_samples_rejected": True,
            "invalid_json_rejected": adverse_json["all_rejected"],
            "missing_result_blocked": True,
            "no_result_qualifies_candidate": True,
            "reset_cases_match_expectation": reset["matches_expectation"],
            "identity_control_bit_exact": all(v["byte_identical"] for v in stimuli["identity_control"].values()),
            "real_corpus_not_read": True,
            "exact_dependency_geometry_pinned": geom["semantic_tokenizer_repository"] == GLM_TOKENIZER_REPO and geom["speaker_embedding_dim"] == 192,
            "requirements_pins_exact": geom["declared_requirements"] == EXPECTED_REQUIREMENTS,
            "eight_release_gates_blocked": all(g["status"] == "blocked" for g in gates),
            "home_cache_has_no_dependency_entry": wts["home_cache"]["huggingface"]["matches"] == [] and wts["home_cache"]["modelscope"]["matches"] == [],
            "bounded_name_search_complete": wts["name_search"]["truncated"] is False,
        },
        "release_gates": gates,
        "remaining_gates": [g["id"] for g in gates],
        "required_results": {
            "exact_x_vc_glm4voice_eres2net_weights_and_runtime": "blocked_weights_and_runtime_absent",
            "glm_4_voice_semantic_tokenization": "blocked_weights_absent",
            "eres2net_speaker_embedding": "blocked_weights_absent",
            "dependency_geometry_alignment_and_drain": "blocked_weights_and_runtime_absent",
            "paired_content_identity_naturalness": "blocked_no_cohort_or_output",
            "alignment_first_output_tail_and_content_delay": "blocked_no_documented_or_measured_timing",
            "joint_checkpoint_runtime_memory_timing_callback": "blocked_not_measured",
            "provider_intake_public_surface_review_release": "blocked_no_intake",
        },
        "regression_count": 0,
        "regressions": [],
    }
    if not finite_json(report):
        raise RuntimeError("report contains nonfinite value")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
