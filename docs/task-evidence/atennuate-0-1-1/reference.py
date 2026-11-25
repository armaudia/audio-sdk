# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-ATENNUATE-0-1-1 (aTENNuate 0.1.1).

This module is standard-library only and deterministic. It contains no
aTENNuate source, ``attenuate`` wheel, PyTorch runtime, checkpoint, weight,
real speech, corpus or vendor result. It records the exact external blocker,
probes a fixed list of task-local paths to evidence the absence, validates a
caller-supplied asset manifest with a fail-closed admission boundary, and
builds the canonical report.

Nothing here is an aTENNuate implementation, an upstream-parity result, a
quality measurement, a listening result, a device-timing result, a benchmark
or a release claim.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-ATENNUATE-0-1-1"
COMPONENT_ID = "atennuate-0-1-1"
TASK_TITLE = "aTENNuate 0.1.1"
CONTRACT_ID = "audio-sdk/atennuate-0-1-1-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "enhancement"
MODE = "implementation"
BASE_COMMIT = "f2709c6b0efabdac98e4017e145d602e9f572d41"
BRANCH = "swarm/SDK-ATENNUATE-0-1-1"
WRITE_SCOPE = "docs/task-evidence/atennuate-0-1-1/ only"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
DEFAULT_AUDIO_ROOT = HERE.parents[5]
AUDIO_ROOT = Path(os.environ.get("SOURCE_ROOT", str(DEFAULT_AUDIO_ROOT))).resolve()
TASK_PREFIX = "docs/task-evidence/atennuate-0-1-1/"

# Immutable inputs. ``source:`` rows are workspace-relative; the rest are
# SDK-worktree-relative. The mutable shared board is deliberately excluded from
# the pin set; only its stable row identity may gate anything.
SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/noise_suppression_assets_20261027.json":
        "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
    "research/clean_speech_diagnostics_20261027.md":
        "c0b39bc33e2a5d9c7ca6a48a1f778de79c7c3e0a52b047beeaa43b09d5253460",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "adapters/atennuate/adapter.json":
        "e38c45287dfd31c427b8716baed8547d3c922676bbf891fb8f8d11f1efa7728a",
    "adapters/atennuate/README.md":
        "ff5e2d7b75a346e8d32bcfa598bde6716135e508cef599474146699f2d1d0bf3",
    "adapters/atennuate/run.py":
        "1fd63f6f8664cd377f57c4e6ee359b4977d30efcce39255c0eb03602a58f70cd",
    "adapters/atennuate/requirements.lock":
        "acb4233d46fd9277a234d0c8e9f8df8fd63b580f0f8fe2e3e8d9cc3bcb4185ba",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
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
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/gtcrn-streaming-onnx/report.json":
        "34970e44019cf99eddccfebddce2c19de1dbddda7108fe69e77040f2b503163d",
    "docs/task-evidence/puresound-dpcrn-mamba-v1/README.md":
        "0ce267e5e40d51007b6e31ac41479b875914e84b881e4a6897a10c2f21718457",
    "docs/task-evidence/puresound-dpcrn-mamba-v1/report.json":
        "b6967e090b8aed2e04f0e898e2f6094bc7870ffc3a7b1f0b8dfb2fa582dfbd8c",
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
)

# Exact pinned candidate identity from the research ledgers, the candidate
# census and the existing offline adapter. No asset bytes are copied here.
CHECKPOINT_MODEL_ID = "PeaBrane/aTENNuate"
CHECKPOINT_REVISION = "838e7c3815261ca7c3708330dd28626f41fe9390"
CHECKPOINT_SHA256 = (
    "0b973c44737db024887edd92beaad87887692743ae284be1f08c84bcd3a8b681"
)
CHECKPOINT_BYTES = 3_414_586
CHECKPOINT_PATH = "data/models/atennuate/weights.pt"
CHECKPOINT_LICENSE_METADATA = "Apache-2.0 (Hugging Face model card; re-verify)"
PACKAGE_NAME = "attenuate"
PACKAGE_VERSION = "0.1.1"
PACKAGE_PIN = PACKAGE_NAME + "==" + PACKAGE_VERSION
WHEEL_SHA256 = (
    "595a35f3118adc709ff430f8162d8f10b7da987f5dd322b25d84bb88f5671c99"
)
PYTHON_VERSION = "3.11"
TORCH_VERSION = "2.5.1"
TORCH_PACKAGE = "torch==" + TORCH_VERSION
TORCH_AUDIO_PACKAGE = "torchaudio==" + TORCH_VERSION
MODEL_SOURCE = "https://huggingface.co/PeaBrane/aTENNuate"
PACKAGE_SOURCE = "https://pypi.org/project/attenuate/"
CENSUS_SOURCE = "https://github.com/Brainchip-Inc/aTENNuate"
PAPER_SOURCE = "https://www.isca-archive.org/interspeech_2025/pei25_interspeech.pdf"
ADAPTER_IDENTITY = "aTENNuate-pypi-0.1.1-offline"
UPSTREAM_MODE = "offline"
UPSTREAM_STREAMING_CAPABLE = True
SERVICE_RUNTIME_CAPABLE = False
PAPER_PARAMETERS = 840_000
PAPER_LATENCY_MS = "46.5"
PAPER_DNS1_PESQ = "2.98"
PILOT_CLIP_COUNT = 30

# Installed v0 geometry is restated, never changed.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
SDK_GEOMETRY = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
}

# Fixed, bounded absence probes. No recursive workspace walk is performed and
# no download is attempted. Any present path makes report generation fail.
ABSENCE_PROBES = (
    "data/models/atennuate",
    "data/models/atennuate/weights.pt",
    "data/checkouts/aTENNuate",
    "data/checkouts/atennuate",
    "data/envs/atennuate",
    "data/envs/atennuate/lib/python3.11/site-packages/attenuate",
    "data/envs/atennuate/lib/python3.11/site-packages/torch",
    "adapters/atennuate/weights.pt",
    "third_party/atennuate",
    "deps/atennuate",
    "vendor/atennuate",
    "core/atennuate",
    "models/atennuate",
    "research/voice-enhancement-20261101/agent-atennuate/weights",
    "research/voice-enhancement-20261101/agent-atennuate/outputs",
    "data/wheels/attenuate-0.1.1-py3-none-any.whl",
    "data/wheels/torch-2.5.1",
    "docs/task-evidence/atennuate-0-1-1/weights.pt",
)

REQUIRED_ARTIFACTS = (
    {
        "id": "ART-01",
        "kind": "exact_checkpoint",
        "requirement": (
            "The exact caller-held PeaBrane/aTENNuate weights.pt at immutable "
            "revision 838e7c3815261ca7c3708330dd28626f41fe9390, 3,414,586 "
            "bytes, SHA-256 0b973c44737db024887edd92beaad87887692743ae284be1f08c84bcd3a8b681, "
            "with a verified model-card license and no provider download."),
    },
    {
        "id": "ART-02",
        "kind": "pinned_runtime",
        "requirement": (
            "The exact attenuate==0.1.1 wheel (SHA-256 "
            "595a35f3118adc709ff430f8162d8f10b7da987f5dd322b25d84bb88f5671c99), "
            "CPython 3.11, torch/torchaudio 2.5.1 CPU and every pinned "
            "transitive package installed in an approved isolated environment."),
    },
    {
        "id": "ART-03",
        "kind": "rights_bundle",
        "requirement": (
            "Artifact-specific code and checkpoint rights, training-data "
            "provenance, third-party notices and a written redistribution and "
            "product-use decision covering the exact wheel and weights."),
    },
    {
        "id": "ART-04",
        "kind": "reference_parity",
        "requirement": (
            "Approved exact aTENNuate reference outputs for frozen inputs "
            "under the pinned runtime and weights, with finite same-length "
            "output, identity source mapping and zero delay compensation."),
    },
    {
        "id": "ART-05",
        "kind": "rights_cleared_paired_cohort",
        "requirement": (
            "A rights-cleared task-matched paired clean/noisy cohort with "
            "independent SI-SDR and STOI scoring and permitted listening."),
    },
    {
        "id": "ART-06",
        "kind": "timing_and_intake_harness",
        "requirement": (
            "Target-runtime timing, memory and throughput measurements, "
            "content/availability timing, streaming-capability parity and a "
            "separate opt-in provider intake with OFF default."),
    },
)

EXACT_BLOCKERS = (
    {
        "id": "BLK-01",
        "artifact_id": "ART-01",
        "statement": (
            "No aTENNuate checkpoint exists in this workspace. "
            "data/models/atennuate/weights.pt is absent, the research ledger "
            "records only 3,414,586 bytes and SHA-256 "
            "0b973c44737db024887edd92beaad87887692743ae284be1f08c84bcd3a8b681 "
            "at revision 838e7c3815261ca7c3708330dd28626f41fe9390, and no "
            "caller-held copy was supplied. The bytes were neither read nor "
            "downloaded."),
        "required_action": (
            "Supply the exact weights.pt bytes from the caller's own storage "
            "at the pinned revision and byte count, verified by SHA-256, "
            "without a provider file access or network download."),
        "linked_gates": ["RG-01", "RG-03"],
    },
    {
        "id": "BLK-02",
        "artifact_id": "ART-02",
        "statement": (
            "The exact runtime is absent. attenuate 0.1.1 (wheel SHA-256 "
            "595a35f3118adc709ff430f8162d8f10b7da987f5dd322b25d84bb88f5671c99) "
            "is not importable in the pinned CPython 3.12.16 evidence "
            "interpreter and torch 2.5.1 is absent; no installed Python 3.11 "
            "environment or cached wheel exists at any fixed probe path. The "
            "package is a batch evaluation wrapper and omits the recurrent "
            "streaming configuration."),
        "required_action": (
            "Install the pinned attenuate==0.1.1 wheel, torch/torchaudio "
            "2.5.1 CPU and the recorded transitive lock in an approved "
            "isolated environment, and record every artifact digest."),
        "linked_gates": ["RG-02", "RG-07"],
    },
    {
        "id": "BLK-03",
        "artifact_id": "ART-03",
        "statement": (
            "Apache-2.0 is recorded for the package and the model card, but "
            "artifact-specific checkpoint terms, exact training-data "
            "provenance, third-party notices and a redistribution/product-use "
            "decision are not established. The adapter README also records a "
            "malformed package source URL and an unavailable linked source "
            "location, so the wheel hash is the only implementation "
            "provenance."),
        "required_action": (
            "Supply written code, weight and training-data terms plus the "
            "complete notice bundle and an explicit legal/redistribution "
            "decision for the exact wheel and checkpoint."),
        "linked_gates": ["RG-03"],
    },
    {
        "id": "BLK-04",
        "artifact_id": "ART-04",
        "statement": (
            "No approved exact reference output, frozen input vector or "
            "pinned scorer exists, and no candidate output was produced. The "
            "recorded 30-clip pilot is historical research evidence, not a "
            "reproduced result in this package."),
        "required_action": (
            "Produce approved reference outputs on frozen inputs with the "
            "pinned runtime and weights and record the exact output digests, "
            "finiteness, peaks, length and source mapping."),
        "linked_gates": ["RG-04", "RG-06"],
    },
    {
        "id": "BLK-05",
        "artifact_id": "ART-05",
        "statement": (
            "No rights-cleared paired real speech cohort, independent "
            "SI-SDR/STOI scorer, clean-speech preservation result or "
            "permitted listening result is present. The historical DNS2020 "
            "pilot used 30 engineering clips and is not a frozen benchmark."),
        "required_action": (
            "Supply a rights-cleared paired cohort with clean references, a "
            "pinned independent scorer and an approved listening protocol, "
            "then report all controls and adverse cases."),
        "linked_gates": ["RG-05", "RG-06"],
    },
    {
        "id": "BLK-06",
        "artifact_id": "ART-06",
        "statement": (
            "No target-runtime timing, memory, throughput, content or "
            "availability measurement and no streaming/runtime parity exists. "
            "No opt-in provider, descriptor or intake was created, and no "
            "public surface is proposed."),
        "required_action": (
            "Measure the exact runtime under a paced workload, record content "
            "and availability timing and resource limits, prove or reject "
            "streaming parity, and open a separate versioned intake with an "
            "OFF default."),
        "linked_gates": ["RG-07", "RG-08"],
    },
)

RELEASE_GATES = (
    {
        "id": "RG-01",
        "title": "exact_checkpoint_and_revision_pin",
        "statement": (
            "The exact caller-held aTENNuate checkpoint, immutable revision, "
            "byte count and SHA-256 are pinned before any implementation "
            "claim."),
        "reopen_condition": (
            "The caller supplies the exact weights.pt bytes at revision "
            "838e7c3815261ca7c3708330dd28626f41fe9390 with matching byte "
            "count and SHA-256, read from caller storage without a download."),
    },
    {
        "id": "RG-02",
        "title": "pinned_runtime_admission",
        "statement": (
            "The pinned attenuate 0.1.1, torch/torchaudio 2.5.1 and their "
            "transitive runtime are installed and importable for the exact "
            "Python version."),
        "reopen_condition": (
            "Install the recorded wheel and lock in an approved isolated "
            "environment, record every artifact digest and prove import and "
            "one deterministic forward pass."),
    },
    {
        "id": "RG-03",
        "title": "artifact_rights_and_training_data",
        "statement": (
            "Artifact-specific code, checkpoint, training-data and notice "
            "terms are reviewed with an explicit redistribution and "
            "product-use decision."),
        "reopen_condition": (
            "Supply written terms for the exact wheel and weights, resolve "
            "training-data provenance and third-party notices, and record the "
            "legal/product-use decision."),
    },
    {
        "id": "RG-04",
        "title": "exact_reference_parity",
        "statement": (
            "Approved aTENNuate reference outputs are reproduced by the "
            "pinned runtime and weights on frozen inputs."),
        "reopen_condition": (
            "Publish approved output digests for frozen inputs and reproduce "
            "them byte-exactly, including finite same-length output, peaks "
            "and identity source mapping."),
    },
    {
        "id": "RG-05",
        "title": "rights_cleared_paired_cohort",
        "statement": (
            "A rights-cleared task-matched paired cohort with clean "
            "references is frozen before any quality result."),
        "reopen_condition": (
            "Supply the immutable paired cohort, provenance, fidelity metadata "
            "and clean references with permission for the intended use."),
    },
    {
        "id": "RG-06",
        "title": "independent_scoring_and_permitted_listening",
        "statement": (
            "Independent SI-SDR/STOI scoring, clean-speech preservation and "
            "permitted listening are completed for the exact conditions."),
        "reopen_condition": (
            "Pin the scorer, report paired and unpaired evidence separately "
            "and complete an approved listening protocol on the frozen "
            "cohort."),
    },
    {
        "id": "RG-07",
        "title": "target_runtime_timing_memory_and_streaming_parity",
        "statement": (
            "Target-runtime timing, memory, throughput, content delay and "
            "streaming capability are measured, not inferred."),
        "reopen_condition": (
            "Run a paced target-runtime workload and record timing, memory, "
            "throughput, output peaks and content/availability delay, and "
            "prove or explicitly reject streaming parity."),
    },
    {
        "id": "RG-08",
        "title": "opt_in_provider_intake_and_release",
        "statement": (
            "A separate opt-in provider intake with OFF default, an explicit "
            "public-surface decision, independent review and release approval "
            "is complete."),
        "reopen_condition": (
            "Open a new versioned intake task, keep registration and default "
            "selection OFF, record the public-surface decision and pass "
            "independent exact-head review."),
    },
)

ENHANCEMENT_PROFILE_ROWS = (
    {
        "id": "ENH-01",
        "requirement": (
            "Run identity/noisy control and an established task-matched "
            "baseline."),
        "status": "blocked",
        "evidence": (
            "No candidate output exists; the historical pilot names "
            "FastEnhancer Small and DeepFilterNet3 baselines but is not "
            "reproduced here."),
    },
    {
        "id": "ENH-02",
        "requirement": (
            "Score paired SI-SDR and STOI where permitted clean references "
            "exist."),
        "status": "blocked",
        "evidence": (
            "No rights-cleared clean references, pinned scorer or candidate "
            "output exists."),
    },
    {
        "id": "ENH-03",
        "requirement": (
            "Measure clean-speech preservation, peaks and invalid outputs."),
        "status": "blocked",
        "evidence": (
            "No output samples exist, so preservation, peak and invalid-output "
            "checks cannot be run."),
    },
    {
        "id": "ENH-04",
        "requirement": (
            "For unpaired speech use a separately labeled predictive screen "
            "or authorized listening."),
        "status": "blocked",
        "evidence": (
            "No predictive screen and no authorized listening result exists; "
            "the historical smoke note is not a listening result."),
    },
    {
        "id": "ENH-05",
        "requirement": "Report alignment, state and memory.",
        "status": "blocked",
        "evidence": (
            "The adapter declares identity source mapping and zero delay "
            "compensation, but no runtime state or memory was measured."),
    },
    {
        "id": "ENH-06",
        "requirement": (
            "Report measured content/availability timing for the exact "
            "runtime."),
        "status": "blocked",
        "evidence": (
            "No device clock, pacing, deadline, throughput or availability "
            "measurement was made; the paper-reported 46.5 ms is not a local "
            "measurement."),
    },
)

NON_CLAIMS = (
    "No aTENNuate source, attenuate 0.1.1 wheel, PyTorch runtime, checkpoint, "
    "weight, model asset or vendor result is present, imported or executed.",
    "No real speech, clean reference, corpus, media file or audio sample is "
    "present or read.",
    "No denoiser is implemented, approximated, substituted or compared; no "
    "generic filter stands in for aTENNuate.",
    "No quality, intelligibility, naturalness, speech-preservation, "
    "listening, device-timing, benchmark or release result is produced.",
    "No provider is registered, exposed, enabled by default or selected as a "
    "descriptor default; no public API, ABI, registry, installed-v0, shared "
    "build or CI change is made.",
    "No missing, synthetic or schema-control result is promoted or treated as "
    "evidence for the candidate.",
)

PROFILE_PHRASES = (
    "Run identity/noisy control and an established task-matched baseline.",
    "Score paired SI-SDR and STOI where permitted clean references exist.",
    "Measure clean-speech preservation, peaks and invalid outputs.",
    "For unpaired speech use a separately labeled predictive screen or "
    "authorized listening.",
    "Report alignment, state, memory and measured content/availability "
    "timing for the exact runtime.",
)

# Admission manifest is a task-local schema, not an SDK or aTENNuate contract.
MANIFEST_SCHEMA_ID = "audio-sdk/atennuate-0-1-1-asset-admission/0.1"
MANIFEST_FIELDS = ("component_id", "checkpoint", "format", "reference_output",
                   "rights", "runtime", "schema_id")
CHECKPOINT_FIELDS = ("byte_count", "license_path", "license_sha256",
                     "model_id", "path", "revision", "sha256")
RUNTIME_FIELDS = ("package_name", "package_version", "python_version",
                  "runtime_path", "runtime_sha256", "torch_version",
                  "wheel_sha256")
RIGHTS_FIELDS = ("code_license", "model_license",
                 "redistribution_decision_reference",
                 "training_data_reference")
FORMAT_FIELDS = ("channels", "delay_compensation_samples", "frame_samples",
                 "output_length", "sample_format", "sample_rate_hz",
                 "source_time_mapping")
REFERENCE_FIELDS = ("finite", "path", "sample_count", "scorer", "sha256")
OUTPUT_LENGTH = "identity"
SOURCE_TIME_MAPPING = "identity"
DELAY_COMPENSATION_SAMPLES = 0
MAX_CHECKPOINT_BYTES = 512 * 1024 * 1024
MAX_REFERENCE_SAMPLES = 16_000 * 60 * 60
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


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


def absence_summary(rows: list[dict]) -> dict:
    return {
        "probe_count": len(rows),
        "present_count": sum(1 for row in rows if row["present"]),
        "recursive_workspace_walk": False,
        "download_attempted": False,
        "source_or_runtime_imported": False,
        "all_probes_absent": all(not row["present"] for row in rows),
    }


def runtime_probe() -> dict:
    """Report whether the exact runtime modules are installed. Never imports."""
    modules = ("attenuate", "torch", "torchaudio")
    present: dict[str, bool] = {}
    for name in modules:
        try:
            found = importlib.util.find_spec(name) is not None
        except (ImportError, AttributeError, ValueError):
            found = False
        present[name] = found
    return {
        "modules": list(modules),
        "present": present,
        "any_present": any(present.values()),
        "imported_or_executed": False,
    }


# --------------------------------------------------------------------------
# Admission validator (task-local; never a runtime boundary)
# --------------------------------------------------------------------------
def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _reject(code: str, field: str = "") -> dict:
    return {"accepted": False, "code": code, "field": field,
            "checks": 0, "state_unchanged": True}


def _accept(checks: int) -> dict:
    return {"accepted": True, "code": "ok", "field": "", "checks": checks,
            "state_unchanged": True}


def _path_is_canonical(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    if not os.path.isabs(value):
        return False
    return os.path.normpath(value) == value


def _exact_object(value: Any, fields: tuple[str, ...]) -> str:
    if not isinstance(value, dict):
        return "invalid_object"
    if set(value) != set(fields):
        return ("missing_field" if set(fields) - set(value) else "unknown_field")
    return ""


def _reference_text(value: Any) -> bool:
    return (isinstance(value, str) and bool(value.strip())
            and len(value) <= 200
            and not any(ord(char) < 32 for char in value))


def validate_manifest(document: object, probe_paths: bool = True) -> dict:
    """Fail-closed asset admission. No weight is read and no model runs."""
    checks = 0
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
    if document["component_id"] != COMPONENT_ID:
        return _reject("invalid_value", "component_id")

    checkpoint = document["checkpoint"]
    code = _exact_object(checkpoint, CHECKPOINT_FIELDS)
    if code:
        return _reject(code, "checkpoint")
    if checkpoint["model_id"] != CHECKPOINT_MODEL_ID:
        return _reject("invalid_value", "checkpoint.model_id")
    if not isinstance(checkpoint["revision"], str) \
            or not HEX40.match(checkpoint["revision"]) \
            or checkpoint["revision"] != CHECKPOINT_REVISION:
        return _reject("invalid_value", "checkpoint.revision")
    if not isinstance(checkpoint["sha256"], str) \
            or not HEX64.match(checkpoint["sha256"]) \
            or checkpoint["sha256"] != CHECKPOINT_SHA256:
        return _reject("invalid_value", "checkpoint.sha256")
    if not _is_int(checkpoint["byte_count"]) \
            or not 0 < checkpoint["byte_count"] <= MAX_CHECKPOINT_BYTES \
            or checkpoint["byte_count"] != CHECKPOINT_BYTES:
        return _reject("invalid_value", "checkpoint.byte_count")
    if not _path_is_canonical(checkpoint["path"]):
        return _reject("invalid_path", "checkpoint.path")
    if not _path_is_canonical(checkpoint["license_path"]):
        return _reject("invalid_path", "checkpoint.license_path")
    if not isinstance(checkpoint["license_sha256"], str) \
            or not HEX64.match(checkpoint["license_sha256"]):
        return _reject("invalid_value", "checkpoint.license_sha256")
    checks += 8

    runtime = document["runtime"]
    code = _exact_object(runtime, RUNTIME_FIELDS)
    if code:
        return _reject(code, "runtime")
    if runtime["package_name"] != PACKAGE_NAME:
        return _reject("invalid_value", "runtime.package_name")
    if runtime["package_version"] != PACKAGE_VERSION:
        return _reject("invalid_value", "runtime.package_version")
    if runtime["wheel_sha256"] != WHEEL_SHA256:
        return _reject("invalid_value", "runtime.wheel_sha256")
    if runtime["python_version"] != PYTHON_VERSION:
        return _reject("invalid_value", "runtime.python_version")
    if runtime["torch_version"] != TORCH_VERSION:
        return _reject("invalid_value", "runtime.torch_version")
    if not _path_is_canonical(runtime["runtime_path"]):
        return _reject("invalid_path", "runtime.runtime_path")
    if not isinstance(runtime["runtime_sha256"], str) \
            or not HEX64.match(runtime["runtime_sha256"]):
        return _reject("invalid_value", "runtime.runtime_sha256")
    checks += 7

    rights = document["rights"]
    code = _exact_object(rights, RIGHTS_FIELDS)
    if code:
        return _reject(code, "rights")
    if rights["code_license"] != "Apache-2.0":
        return _reject("invalid_value", "rights.code_license")
    if rights["model_license"] != "Apache-2.0":
        return _reject("invalid_value", "rights.model_license")
    if not _reference_text(rights["training_data_reference"]):
        return _reject("invalid_value", "rights.training_data_reference")
    if not _reference_text(rights["redistribution_decision_reference"]):
        return _reject("invalid_value",
                       "rights.redistribution_decision_reference")
    checks += 4

    fmt = document["format"]
    code = _exact_object(fmt, FORMAT_FIELDS)
    if code:
        return _reject(code, "format")
    if not _is_int(fmt["sample_rate_hz"]) \
            or fmt["sample_rate_hz"] != SAMPLE_RATE_HZ:
        return _reject("invalid_value", "format.sample_rate_hz")
    if not _is_int(fmt["channels"]) or fmt["channels"] != CHANNELS:
        return _reject("invalid_value", "format.channels")
    if fmt["sample_format"] != SAMPLE_FORMAT:
        return _reject("invalid_value", "format.sample_format")
    if not _is_int(fmt["frame_samples"]) \
            or fmt["frame_samples"] != FRAME_SAMPLES:
        return _reject("invalid_value", "format.frame_samples")
    if fmt["output_length"] != OUTPUT_LENGTH:
        return _reject("invalid_value", "format.output_length")
    if fmt["source_time_mapping"] != SOURCE_TIME_MAPPING:
        return _reject("invalid_value", "format.source_time_mapping")
    if not _is_int(fmt["delay_compensation_samples"]) \
            or fmt["delay_compensation_samples"] != DELAY_COMPENSATION_SAMPLES:
        return _reject("invalid_value", "format.delay_compensation_samples")
    checks += 7

    reference = document["reference_output"]
    code = _exact_object(reference, REFERENCE_FIELDS)
    if code:
        return _reject(code, "reference_output")
    if not _path_is_canonical(reference["path"]):
        return _reject("invalid_path", "reference_output.path")
    if not isinstance(reference["sha256"], str) \
            or not HEX64.match(reference["sha256"]):
        return _reject("invalid_value", "reference_output.sha256")
    if not _is_int(reference["sample_count"]) \
            or not 0 < reference["sample_count"] <= MAX_REFERENCE_SAMPLES:
        return _reject("invalid_value", "reference_output.sample_count")
    if reference["finite"] is not True:
        return _reject("invalid_value", "reference_output.finite")
    if not _reference_text(reference["scorer"]):
        return _reject("invalid_value", "reference_output.scorer")
    checks += 5

    if probe_paths:
        probes = (
            (checkpoint["path"], checkpoint["sha256"], "checkpoint.path"),
            (checkpoint["license_path"], checkpoint["license_sha256"],
             "checkpoint.license_path"),
            (runtime["runtime_path"], runtime["runtime_sha256"],
             "runtime.runtime_path"),
            (reference["path"], reference["sha256"],
             "reference_output.path"),
        )
        for raw_path, digest, field in probes:
            path = Path(raw_path)
            if not path.is_file():
                return _reject("probe_missing", field)
            if sha256_file(path) != digest:
                return _reject("probe_digest_mismatch", field)
        checks += 4
    return _accept(checks)


def _manifest_control() -> dict:
    """Structural schema control. It is not evidence and never qualifies."""
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "component_id": COMPONENT_ID,
        "checkpoint": {
            "model_id": CHECKPOINT_MODEL_ID,
            "revision": CHECKPOINT_REVISION,
            "path": "/caller/models/atennuate/weights.pt",
            "sha256": CHECKPOINT_SHA256,
            "byte_count": CHECKPOINT_BYTES,
            "license_path": "/caller/models/atennuate/LICENSE",
            "license_sha256": "1" * 64,
        },
        "runtime": {
            "package_name": PACKAGE_NAME,
            "package_version": PACKAGE_VERSION,
            "wheel_sha256": WHEEL_SHA256,
            "python_version": PYTHON_VERSION,
            "torch_version": TORCH_VERSION,
            "runtime_path": "/caller/env/bin/python3.11",
            "runtime_sha256": "2" * 64,
        },
        "rights": {
            "code_license": "Apache-2.0",
            "model_license": "Apache-2.0",
            "training_data_reference": "caller-rights-record-training-data",
            "redistribution_decision_reference": "caller-rights-decision-001",
        },
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "frame_samples": FRAME_SAMPLES,
            "output_length": OUTPUT_LENGTH,
            "source_time_mapping": SOURCE_TIME_MAPPING,
            "delay_compensation_samples": DELAY_COMPENSATION_SAMPLES,
        },
        "reference_output": {
            "path": "/caller/evidence/reference.wav",
            "sha256": "3" * 64,
            "sample_count": SAMPLE_RATE_HZ,
            "finite": True,
            "scorer": "paired_si_sdr_stoi",
        },
    }


def _without_nested(section: str, field: str) -> dict:
    document = _manifest_control()
    del document[section][field]
    return document


def _with_nested(section: str, field: str, value: Any) -> dict:
    document = _manifest_control()
    document[section][field] = value
    return document


def admission_controls() -> dict:
    """Build the frozen adverse matrix plus one structural schema control."""
    cases: list[dict] = []

    def manifest_case(case_id: str, mutate, kind: str = "manifest") -> None:
        document = _manifest_control()
        result = mutate(document)
        if result["accepted"]:
            raise ValueError("control_not_rejected:" + case_id)
        cases.append({
            "id": case_id,
            "kind": kind,
            "status": "rejected",
            "code": result["code"],
            "field": result["field"],
            "state_unchanged": result["state_unchanged"],
            "qualifies": False,
            "evidence_class": "synthetic_admission_control",
        })

    def drop(document, field):
        del document[field]
        return validate_manifest(document, probe_paths=False)

    def put(document, field, value):
        document[field] = value
        return validate_manifest(document, probe_paths=False)

    def nested(document, section, field, value):
        document[section][field] = value
        return validate_manifest(document, probe_paths=False)

    cases.append({
        "id": "MISS-01", "kind": "manifest", "status": "rejected",
        "code": validate_manifest(None, probe_paths=False)["code"],
        "field": "", "state_unchanged": True, "qualifies": False,
        "evidence_class": "synthetic_admission_control"})
    manifest_case("INV-01", lambda doc: drop(doc, "checkpoint"))
    manifest_case("INV-02", lambda doc: put(doc, "extra", "value"))
    manifest_case("INV-03", lambda doc: put(doc, "schema_id", "wrong"))
    manifest_case("INV-04", lambda doc: put(doc, "component_id", "other"))
    manifest_case("INV-05", lambda doc: validate_manifest(
        _without_nested("checkpoint", "model_id"), probe_paths=False))
    manifest_case("INV-06", lambda doc: nested(
        doc, "checkpoint", "model_id", "other/model"))
    manifest_case("INV-07", lambda doc: nested(
        doc, "checkpoint", "revision", CHECKPOINT_REVISION.upper()))
    manifest_case("INV-08", lambda doc: nested(
        doc, "checkpoint", "revision", CHECKPOINT_REVISION[:39]))
    manifest_case("INV-09", lambda doc: nested(
        doc, "checkpoint", "sha256", "0" * 63))
    manifest_case("INV-10", lambda doc: nested(
        doc, "checkpoint", "sha256", "g" * 64))
    manifest_case("INV-11", lambda doc: nested(
        doc, "checkpoint", "byte_count", -1))
    manifest_case("INV-12", lambda doc: nested(
        doc, "checkpoint", "byte_count", True))
    manifest_case("INV-13", lambda doc: nested(
        doc, "checkpoint", "byte_count", float("nan")))
    manifest_case("INV-14", lambda doc: nested(
        doc, "checkpoint", "byte_count", float("inf")))
    manifest_case("INV-15", lambda doc: nested(
        doc, "checkpoint", "byte_count", CHECKPOINT_BYTES + 1))
    manifest_case("INV-16", lambda doc: nested(
        doc, "checkpoint", "path", "relative/weights.pt"))
    manifest_case("INV-17", lambda doc: nested(
        doc, "checkpoint", "path", "/caller/../weights.pt"))
    manifest_case("INV-18", lambda doc: nested(
        doc, "checkpoint", "path", "/caller/\x00weights.pt"))
    manifest_case("INV-19", lambda doc: nested(
        doc, "checkpoint", "license_sha256", "1" * 63))
    manifest_case("INV-20", lambda doc: nested(
        doc, "runtime", "package_name", "torch"))
    manifest_case("INV-21", lambda doc: nested(
        doc, "runtime", "package_version", "0.1.0"))
    manifest_case("INV-22", lambda doc: nested(
        doc, "runtime", "wheel_sha256", "0" * 64))
    manifest_case("INV-23", lambda doc: nested(
        doc, "runtime", "python_version", "3.12"))
    manifest_case("INV-24", lambda doc: nested(
        doc, "runtime", "torch_version", "2.4.1"))
    manifest_case("INV-25", lambda doc: nested(
        doc, "runtime", "runtime_path", "bin/python"))
    manifest_case("INV-26", lambda doc: nested(
        doc, "runtime", "runtime_sha256", "x" * 64))
    manifest_case("INV-27", lambda doc: nested(
        doc, "rights", "code_license", "MIT"))
    manifest_case("INV-28", lambda doc: nested(
        doc, "rights", "training_data_reference", ""))
    manifest_case("INV-29", lambda doc: nested(
        doc, "rights", "redistribution_decision_reference", ""))
    manifest_case("INV-30", lambda doc: nested(
        doc, "rights", "training_data_reference", 7))
    manifest_case("INV-31", lambda doc: nested(
        doc, "format", "sample_rate_hz", 48000))
    manifest_case("INV-32", lambda doc: nested(
        doc, "format", "channels", 2))
    manifest_case("INV-33", lambda doc: nested(
        doc, "format", "sample_format", "i16"))
    manifest_case("INV-34", lambda doc: nested(
        doc, "format", "frame_samples", 320))
    manifest_case("INV-35", lambda doc: nested(
        doc, "format", "output_length", "streaming"))
    manifest_case("INV-36", lambda doc: nested(
        doc, "format", "source_time_mapping", "guessed"))
    manifest_case("INV-37", lambda doc: nested(
        doc, "format", "delay_compensation_samples", 160))
    manifest_case("INV-38", lambda doc: validate_manifest(
        _without_nested("reference_output", "sha256"), probe_paths=False))
    manifest_case("INV-39", lambda doc: nested(
        doc, "reference_output", "sha256", "z" * 64))
    manifest_case("INV-40", lambda doc: nested(
        doc, "reference_output", "sample_count", 0))
    manifest_case("INV-41", lambda doc: nested(
        doc, "reference_output", "sample_count", float("nan")))
    manifest_case("INV-42", lambda doc: nested(
        doc, "reference_output", "finite", False))
    manifest_case("INV-43", lambda doc: nested(
        doc, "reference_output", "scorer", ""))
    manifest_case("INV-44", lambda doc: nested(
        doc, "reference_output", "path", "reference.wav"))
    manifest_case("INV-45", lambda doc: put(doc, "checkpoint", "weights.pt"))
    manifest_case("INV-46", lambda doc: validate_manifest(
        {**_manifest_control(), "format": {"bad": True}}, probe_paths=False))
    manifest_case("PRS-01", lambda doc: validate_manifest(doc,
                                                          probe_paths=True))

    for case_id, text, code in (
            ("JSON-01", '{"a":1,"a":2}', "duplicate_json_key:a"),
            ("JSON-02", '{"a":NaN}', "nonfinite_json_constant:NaN"),
            ("JSON-03", '{"a":Infinity}', "nonfinite_json_constant:Infinity"),
            ("JSON-04", '[]', "json_root_not_object")):
        try:
            loads_strict(text)
        except ValueError as error:
            message = str(error)
        else:  # pragma: no cover - the fixtures are malformed by design
            message = "accepted"
        cases.append({
            "id": case_id, "kind": "strict_json", "status": "rejected",
            "code": code, "field": "",
            "message_matches": message == code,
            "state_unchanged": True, "qualifies": False,
            "evidence_class": "synthetic_admission_control"})

    control = validate_manifest(_manifest_control(), probe_paths=False)
    controls = [{
        "id": "CTL-01",
        "kind": "manifest",
        "status": "accepted_schema_control",
        "code": control["code"],
        "checks": control["checks"],
        "artifacts_probed": False,
        "runtime_loaded": False,
        "weights_read": False,
        "audio_read": False,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "qualifies": False,
    }]
    return {"cases": cases, "controls": controls}


# --------------------------------------------------------------------------
# Canonical contract and report
# --------------------------------------------------------------------------
def _artifact_rows() -> list[dict]:
    return [{
        "id": artifact["id"],
        "kind": artifact["kind"],
        "requirement": artifact["requirement"],
        "present": False,
        "verified": False,
        "sha256": None,
        "blocked": True,
    } for artifact in REQUIRED_ARTIFACTS]


def _blocker_rows() -> list[dict]:
    return [{
        "id": blocker["id"],
        "artifact_id": blocker["artifact_id"],
        "statement": blocker["statement"],
        "required_action": blocker["required_action"],
        "linked_gates": list(blocker["linked_gates"]),
        "status": "open",
        "qualifies": False,
    } for blocker in EXACT_BLOCKERS]


def _gate_rows() -> list[dict]:
    identity = {"task_id": TASK, "component_id": COMPONENT_ID, "mode": MODE}
    return [{
        "id": gate["id"],
        "title": gate["title"],
        "statement": gate["statement"],
        "reopen_condition": gate["reopen_condition"],
        "status": "blocked",
        "qualifies": False,
        "linked_row": identity,
    } for gate in RELEASE_GATES]


def linked_row_identity() -> dict:
    projection = {field: BOARD_ROW_PROJECTION[field]
                  for field in BOARD_ROW_FIELDS}
    return {
        "projection": projection,
        "sha256": board_row_digest(projection),
        "selector": "stable-row-identity/0.1:" + ",".join(BOARD_ROW_FIELDS),
        "gating": "stable_identity_only",
        "mutable_fields_excluded": ["status", "owner", "claim", "review",
                                    "handoff", "blocked_reason",
                                    "dispatch_priority"],
        "board_file_pinned": False,
        "board_status_gates_anything": False,
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
    }


def qualification_block() -> dict:
    return {
        "status": QUALIFICATION_STATUS,
        "readiness": "incomplete",
        "all_release_gates_blocked": True,
        "real_source_present": False,
        "real_runtime_present": False,
        "real_checkpoint_present": False,
        "real_weights_present": False,
        "real_cohort_present": False,
        "real_result_present": False,
        "denoiser_implementation_result": False,
        "reference_parity_result": False,
        "quality_result": False,
        "listening_result": False,
        "timing_or_peak_result": False,
        "benchmark_result": False,
        "missing_result_promoted": False,
        "not_qualified": True,
    }


def disposition_block() -> dict:
    return {
        "status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "promotion": "defer",
        "production_exposure": "DEFER",
        "proposal_only": True,
        "incomplete": True,
        "not_qualified": True,
        "expose_as_processor": False,
        "registered": False,
        "default_enabled": False,
        "missing_result_qualifies": False,
    }


def boundary_block() -> dict:
    return {
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "shared_cmakelists_change": False,
        "ci_workflow_change": False,
        "installed_v0_behavior_change": False,
        "processor_exposure": False,
        "task_local_only": True,
        "files_outside_task_directory_written": False,
    }


def scope_block() -> dict:
    return {
        "source_present": False,
        "runtime_present": False,
        "runtime_executed": False,
        "weights_present": False,
        "weights_read": False,
        "checkpoint_loaded": False,
        "real_corpus": False,
        "audio_read": False,
        "denoising_performed": False,
        "reference_parity_result": False,
        "quality_scored": False,
        "listening": False,
        "device_timing": False,
        "peak_bound_measured": False,
        "benchmark": False,
        "release_claim": False,
        "network_used": False,
        "download_attempted": False,
    }


def public_v0_geometry() -> dict:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "preserved": True,
        "sdk_callback_invoked": False,
    }


def exact_scope_block() -> dict:
    return {
        "task_local_evidence_only": True,
        "single_component": COMPONENT_ID,
        "provider_work": False,
        "runtime_work": False,
        "release_work": False,
        "write_scope": WRITE_SCOPE,
    }


def profile_source_block() -> dict:
    return {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "row": "Enhancement",
        "phrases": list(PROFILE_PHRASES),
    }


def upstream_record_block() -> dict:
    return {
        "checkpoint_model_id": CHECKPOINT_MODEL_ID,
        "checkpoint_revision": CHECKPOINT_REVISION,
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "checkpoint_byte_count": CHECKPOINT_BYTES,
        "checkpoint_path": CHECKPOINT_PATH,
        "checkpoint_license_metadata": CHECKPOINT_LICENSE_METADATA,
        "package": PACKAGE_PIN,
        "package_wheel_sha256": WHEEL_SHA256,
        "python_version": PYTHON_VERSION,
        "torch_package": TORCH_PACKAGE,
        "torchaudio_package": TORCH_AUDIO_PACKAGE,
        "adapter_identity": ADAPTER_IDENTITY,
        "upstream_mode": UPSTREAM_MODE,
        "upstream_streaming_capable": UPSTREAM_STREAMING_CAPABLE,
        "service_runtime_capable": SERVICE_RUNTIME_CAPABLE,
        "paper_parameters": PAPER_PARAMETERS,
        "paper_latency_ms": PAPER_LATENCY_MS,
        "paper_dns1_pesq": PAPER_DNS1_PESQ,
        "pilot_clip_count": PILOT_CLIP_COUNT,
        "model_source": MODEL_SOURCE,
        "package_source": PACKAGE_SOURCE,
        "census_source": CENSUS_SOURCE,
        "paper_source": PAPER_SOURCE,
        "source_location_note": (
            "The adapter README records a malformed package source URL and an "
            "unavailable linked source location; the wheel SHA-256 and wheel "
            "contents are the recorded implementation provenance."),
        "source_reported_values_are_provenance_only": True,
        "not_reproduced_here": True,
    }


def admission_contract_block() -> dict:
    return {
        "policy": "task_local_fail_closed_admission_not_runtime_behavior",
        "manifest_schema_id": MANIFEST_SCHEMA_ID,
        "manifest_fields": list(MANIFEST_FIELDS),
        "checkpoint_fields": list(CHECKPOINT_FIELDS),
        "runtime_fields": list(RUNTIME_FIELDS),
        "rights_fields": list(RIGHTS_FIELDS),
        "format_fields": list(FORMAT_FIELDS),
        "reference_fields": list(REFERENCE_FIELDS),
        "pinned_model_id": CHECKPOINT_MODEL_ID,
        "pinned_revision": CHECKPOINT_REVISION,
        "pinned_checkpoint_sha256": CHECKPOINT_SHA256,
        "pinned_checkpoint_byte_count": CHECKPOINT_BYTES,
        "pinned_package": PACKAGE_PIN,
        "pinned_wheel_sha256": WHEEL_SHA256,
        "pinned_python_version": PYTHON_VERSION,
        "pinned_torch_version": TORCH_VERSION,
        "max_checkpoint_bytes": MAX_CHECKPOINT_BYTES,
        "max_reference_samples": MAX_REFERENCE_SAMPLES,
        "output_length": OUTPUT_LENGTH,
        "source_time_mapping": SOURCE_TIME_MAPPING,
        "delay_compensation_samples": DELAY_COMPENSATION_SAMPLES,
        "sdk_geometry": dict(SDK_GEOMETRY),
        "empty_payload_sha256": EMPTY_SHA256,
        "audio_read": False,
        "runtime_invoked": False,
        "weights_loaded": False,
        "denoising_performed": False,
    }


def build_contract() -> dict:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT_ID,
        "title": TASK_TITLE,
        "profile": PROFILE,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_scope": exact_scope_block(),
        "qualification": qualification_block(),
        "upstream_record": upstream_record_block(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_row_fields": list(BOARD_ROW_FIELDS),
        "board_row_projection": dict(BOARD_ROW_PROJECTION),
        "board_row_sha256": board_row_digest(BOARD_ROW_PROJECTION),
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "absence_policy": {
            "fixed_probe_list_only": True,
            "recursive_workspace_walk": False,
            "download_attempted": False,
            "any_present_probe_blocks_shipping": True,
        },
        "absence_probes": list(ABSENCE_PROBES),
        "required_artifacts": _artifact_rows(),
        "exact_blockers": _blocker_rows(),
        "release_gates": _gate_rows(),
        "admission_contract": admission_contract_block(),
        "enhancement_profile_requirements": [dict(row)
                                             for row in ENHANCEMENT_PROFILE_ROWS],
        "profile_source": profile_source_block(),
        "non_claims": list(NON_CLAIMS),
    }


def build_report() -> dict:
    contract = read_strict_json(HERE / "contract.json")
    probes = absence_probes(AUDIO_ROOT)
    controls = admission_controls()
    rejected = [case for case in controls["cases"]
                if case["status"] == "rejected"]
    accepted_controls = [case for case in controls["controls"]
                         if case["status"] == "accepted_schema_control"]
    gates = _gate_rows()
    artifacts = _artifact_rows()
    blockers = _blocker_rows()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "contract_sha256": object_digest(contract),
        "task_id": TASK,
        "task_title": TASK_TITLE,
        "component_id": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification_status": QUALIFICATION_STATUS,
        "disposition": disposition_block(),
        "boundary": boundary_block(),
        "scope": scope_block(),
        "public_v0_geometry": public_v0_geometry(),
        "exact_scope": exact_scope_block(),
        "upstream_record": upstream_record_block(),
        "absence_evidence": {
            "probes": probes,
            "summary": absence_summary(probes),
            "conclusion": (
                "No aTENNuate checkpoint, weights.pt, attenuate 0.1.1 wheel, "
                "PyTorch runtime, real cohort, clean reference or vendor "
                "result exists at any fixed probe location."),
        },
        "runtime_probe": runtime_probe(),
        "required_artifacts": artifacts,
        "exact_blockers": blockers,
        "enhancement_profile": {
            "profile": PROFILE,
            "rows": [dict(row) for row in ENHANCEMENT_PROFILE_ROWS],
            "identity_control": False,
            "noisy_control": False,
            "task_matched_baseline": False,
            "paired_clean_references": False,
            "paired_si_sdr": False,
            "paired_stoi": False,
            "clean_speech_preservation": False,
            "peak_and_invalid_output_checks": False,
            "unpaired_predictive_screen": False,
            "authorized_listening": False,
            "alignment_reported": False,
            "state_reported": False,
            "memory_reported": False,
            "content_availability_timing_measured": False,
            "status": "blocked",
        },
        "admission": {
            "policy": "task_local_fail_closed_admission_not_runtime_behavior",
            "cases": controls["cases"],
            "schema_controls": controls["controls"],
            "summary": {
                "case_count": len(controls["cases"]),
                "rejected_count": len(rejected),
                "accepted_schema_controls": len(accepted_controls),
                "qualifying_results": 0,
                "state_advanced_on_rejection": any(
                    case["state_unchanged"] is not True for case in rejected),
                "runtime_invoked": False,
                "weights_loaded": False,
                "audio_read": False,
                "denoising_performed": False,
            },
        },
        "qualification": qualification_block(),
        "prohibited_claims": list(NON_CLAIMS),
        "gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "linked_row_identity": linked_row_identity(),
        "profile_source": profile_source_block(),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "regeneration": {
            "runs": 3,
            "byte_identical": True,
            "cold_start_processes": True,
            "canonical_json": True,
            "sorted_keys": True,
            "compact_separators": True,
            "trailing_newline": True,
        },
        "reproduction": {
            "tests": ("PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v "
                      "test_reference.py"),
            "report": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
        },
    }


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_text(report)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema_id") != CONTRACT_SCHEMA_ID:
        raise ValueError("contract_schema_id")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("component") != COMPONENT_ID:
        raise ValueError("contract_component")
    if contract.get("profile") != PROFILE or contract.get("mode") != MODE:
        raise ValueError("contract_profile_or_mode")
    if contract.get("decision") != DECISION:
        raise ValueError("contract_decision")
    if contract.get("status") != STATUS:
        raise ValueError("contract_status")
    if contract.get("evidence_status") != EVIDENCE_STATUS:
        raise ValueError("contract_evidence_status")
    if contract.get("qualification_status") != QUALIFICATION_STATUS:
        raise ValueError("contract_qualification_status")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal_only")
    if contract.get("incomplete") is not True:
        raise ValueError("contract_incomplete")
    if len(contract.get("release_gates", [])) != 8:
        raise ValueError("contract_gate_count")
    if any(gate.get("status") != "blocked"
           for gate in contract["release_gates"]):
        raise ValueError("contract_gate_not_blocked")
    if contract.get("board_row_projection") != BOARD_ROW_PROJECTION:
        raise ValueError("contract_board_row_projection")
    if contract.get("board_row_sha256") != board_row_digest(
            BOARD_ROW_PROJECTION):
        raise ValueError("contract_board_row_digest")
    if contract.get("linked_rows") != [dict(row) for row in LINKED_ROWS]:
        raise ValueError("contract_linked_rows")
    for key, value in (("source_pins", SOURCE_PINS),
                       ("boundary_pins", BOUNDARY_PINS)):
        if contract.get(key) != value:
            raise ValueError("contract_pin_table:" + key)
