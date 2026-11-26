# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only DNSMOS evidence-contract reference (DEFER).

This is a *proposal-only* evidence-profile package for
``SDK-DNSMOS-P-835-AND-DNSMOS-C``.  It does **not** contain, link, download,
install, execute or emulate DNSMOS P.835, DNSMOS-C, their ONNX or PyTorch
weights, the DeepFilterNet-packaged P.835 scorer, the NISQA checkpoint, ONNX
Runtime, PyTorch, librosa or numpy.  Two distinct scorers are kept separate:

* ``dnsmos_p835``: no-reference predicted SIG/BAK/OVL from the two pinned ONNX
  models (``sig.onnx``, ``bak_ovr.onnx``) behind the DeepFilterNet-packaged
  scorer, 16 kHz mono, 9.01 s windows and a 1 s hop.
* ``dnsmos_c``: the separate DNSMOS-C protocol built on the NISQA checkpoint
  (``runs/NISQA/model_best.pt``), scoring only ``primary`` and ``mix``
  segments with 10 s windows and a 5 s hop, then averaging scenarios equally.

Neither scorer can run here.  The package reproduces only the documented
*windowing, tiling, post-processing and aggregation arithmetic* over declared
synthetic inputs, so the exact missing artifacts, rights and runtime are
recorded and cannot be mistaken for a result.  Every score slot is ``None``.
Nothing here is a MOS, a human rating, an intelligibility measure, a
benchmark, a device measurement or a release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]

TASK_ID = "SDK-DNSMOS-P-835-AND-DNSMOS-C"
COMPONENT = "dnsmos-p-835-and-dnsmos-c"
BASE_COMMIT = "7c6653f5a7db7f6de34ad709a96a455a9ad3263a"
BRANCH = "swarm/SDK-DNSMOS-P-835-AND-DNSMOS-C"
SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "evidence"
STATUS = "proposal_only_not_qualified"
COMPLETENESS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
LOCAL_IDENTITY = "dnsmos-p835-and-dnsmos-c-evidence-contract-reference-v1"

# Installed v0 stays untouched; recorded for boundary clarity only.
INSTALLED_V0 = "16 kHz mono float32, 160 samples per frame"
SAMPLE_RATE_HZ = 16000
CHANNELS = 1

# ---- DNSMOS P.835 (predicted SIG/BAK/OVL) --------------------------------
P835_SAMPLE_RATE_HZ = 16000
P835_INPUT_LENGTH_S = 9.01
P835_WINDOW_SAMPLES = int(P835_INPUT_LENGTH_S * P835_SAMPLE_RATE_HZ)  # 144160
P835_HOP_SAMPLES = 16000
P835_OUTPUTS = ("SIG", "BAK", "OVL")
P835_MODEL_DIR = "data/models/dnsmos-p835"
P835_MODELS: Dict[str, str] = {
    "sig.onnx": "d2fbdb293bc2366dfbae2b7477c490f981d24a8b4405efd3c11787569c6549d7",
    "bak_ovr.onnx": (
        "5f335c90994618150192a656a474bcf8a9cbcedbc47965494ba8da79605d1308"
    ),
}
P835_SCORER_PATH = (
    "data/envs/deepfilternet3/lib/python3.10/site-packages/df/scripts/dnsmos.py"
)
P835_SCORER_SHA256 = (
    "abcfd3ee61b37a45728b2c7faaed8ced710e11e01d0a58daf4377363bc719fbb"
)
P835_SEGMENTATION = (
    "mono 16 kHz; while len < 144160 append the whole buffer; "
    "num_hops = int(floor(len/16000) - 9.01) + 1; window 144160 samples; "
    "hop 16000 samples; per-window scores averaged in ascending order"
)
P835_POSTPROCESS_NOTE = (
    "documented 2nd/3rd-order polynomial mapping of the raw SIG/BAK/OVL "
    "outputs; coefficients transcribed from the published DNSMOS helper "
    "family. The pinned scorer is absent, so coefficient-source parity is "
    "not verified and no model output exists to map."
)

# ---- DNSMOS-C (separate NISQA-based protocol) -----------------------------
DNSC_SAMPLE_RATE_HZ = 16000
DNSC_SEGMENT_KINDS = ("primary", "mix")
DNSC_MIN_SEGMENT_MS = 1000
DNSC_WINDOW_MS = 10000
DNSC_HOP_MS = 5000
DNSC_MAX_DURATION_MS = 86_400_000
DNSC_OUTPUTS = ("DNSMOS_C",)
DNSC_CHECKPOINT = "runs/NISQA/model_best.pt"
DNSC_SOURCE = "https://github.com/Hope-Liang/DNSMOS-C"
DNSC_PROTOCOL = (
    "16 kHz; score primary and mix segments only; drop segments shorter than "
    "1 s; repeat shorter-than-10 s segments to 10 s; 10 s windows with 5 s "
    "hops and an end-aligned tail; average segments within a scenario, then "
    "average the three scenarios with equal weight"
)

# Documented polynomial mappings (non-personalized and personalized).
P835_POLYFIT: Dict[str, Tuple[float, ...]] = {
    "standard": {
        "SIG": (-0.08397278, 1.22083953, 0.0052439),
        "BAK": (-0.13166888, 1.60915514, -0.39604546),
        "OVL": (-0.06766283, 1.11546468, 0.04602535),
    },
    "personalized": {
        "SIG": (-0.01019296, 0.02751166, 1.19576786, -0.24348726),
        "BAK": (-0.04976499, 0.44276479, -0.1644611, 0.96883132),
        "OVL": (-0.00533021, 0.005101, 1.18058466, -0.11236046),
    },
}
RAW_OUTPUT_MIN = 0.0
RAW_OUTPUT_MAX = 6.0
MAX_INPUT_SAMPLES = 1_000_000_000

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/agent-dnsmos-ears-743/REPORT.md":
        "613f5448418f84a354366de412ecfd8f92a7143b7cea8549899e51dbcb357d21",
    "research/voice-enhancement-20261101/agent-dnsmos-ears-743/"
    "score_existing_outputs.py":
        "0e0d89720231a161cf4c55dfdbc4c0995a30e377fb97796c5893dcdafd5e8a4b",
    "research/cpp-library-krisp-benchmark-20261109.md":
        "7f3c80a2a9f266bbf112fb6ea89bda0bf9ccb1a9045e39cf42fdc5d49496a8e2",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}
SIBLING_PINS: Dict[str, str] = {
    "docs/task-evidence/aecmos/README.md":
        "502b86005a9782ac5fdb7628b1285adaf535158cd650cc13eda1a22a137b7422",
    "docs/task-evidence/aecmos/report.json":
        "8055f6627d462c124182743469109a850087c11773899a6f64b02309be16c320",
    "docs/task-evidence/quality-impairment-taxonomy/README.md":
        "77ad10fae3e41a06adad6cee377616c73dd8d7d458a76c9297aa55d837afcbe5",
    "docs/task-evidence/stoi-estoi/report.json":
        "a74820ff3e42f80d5ab06038de6ec70989876c6d91b98b34dc059ed2a6858f82",
    "docs/task-evidence/srmr-and-reverb-metrics/report.json":
        "291897aaacb9d16a40bb68a64dfb84d2c03a559ca9997a9e5fb1c718d633b979",
}

TASK_ROW_IDENTITY: Dict[str, Any] = {
    "id": TASK_ID,
    "title": "DNSMOS P.835 and DNSMOS-C",
    "repository": "audio-sdk",
    "mode": "research-control",
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    "evidence": [
        "research/voice-enhancement-20261101/agent-dnsmos-ears-743/REPORT.md"
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
    "installed_v0_format": INSTALLED_V0,
    "real_p835_weights": False,
    "real_p835_scorer": False,
    "real_dnsmos_c_checkpoint": False,
    "real_dnsmos_c_source": False,
    "licensed_source_or_binary": False,
    "model_runtime_executed": False,
    "weights_or_assets": False,
    "real_speech_or_corpus": False,
    "downloads": False,
    "device_timing": False,
    "listening": False,
    "benchmark_claim": False,
    "release_claim": False,
    "predicted_scores_kept_separate_from_subjective_mos": True,
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
        "id": "p835_model_weights_and_terms",
        "requirement": (
            "The exact DNSMOS P.835 ONNX weights sig.onnx (SHA-256 "
            "d2fbdb293bc2366dfbae2b7477c490f981d24a8b4405efd3c11787569c6549d7) "
            "and bak_ovr.onnx (SHA-256 "
            "5f335c90994618150192a656a474bcf8a9cbcedbc47965494ba8da79605d1308), "
            "with the weights' own license terms, redistribution terms and "
            "written approval to execute; the repository license covers code "
            "only."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "dnsmos_c_checkpoint_source_and_terms",
        "requirement": (
            "The exact NISQA checkpoint runs/NISQA/model_best.pt with an "
            "immutable revision, byte count, SHA-256 digest, model card and "
            "training-data statement, plus the pinned DNSMOS-C feature-"
            "extraction source revision and its code and weight terms."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "pinned_scorer_and_runtime",
        "requirement": (
            "The exact P.835 scorer revision (observed historical path "
            "data/envs/deepfilternet3/lib/python3.10/site-packages/df/scripts/"
            "dnsmos.py, SHA-256 "
            "abcfd3ee61b37a45728b2c7faaed8ced710e11e01d0a58daf4377363bc719fbb) "
            "plus a pinned and approved onnxruntime/numpy environment, and a "
            "pinned DNSMOS-C/NISQA runtime; an incidental environment is not a "
            "qualification."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "rights_cleared_cohorts",
        "requirement": (
            "A rights-cleared cohort for each protocol, with exact item "
            "identity, alignment and permissions. EARS is CC BY-NC 4.0 "
            "non-commercial research media and the Krisp 265-output set is "
            "CC BY-NC 4.0; neither grants redistribution of audio, outputs or "
            "derived score bundles beyond its documented research scope."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "exact_window_and_aggregation_parity",
        "requirement": (
            "Numerical parity against the official implementations for the "
            "P.835 9.01 s window / 1 s hop replay, the DNSMOS-C 1 s minimum, "
            "10 s repeat, 10 s window / 5 s hop and end-aligned tail, and the "
            "equal-weight three-scenario aggregation."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "predicted_score_validation_and_controls",
        "requirement": (
            "One representative valid item and one invalid/missing item "
            "validated end to end through the reported bundle, with predicted "
            "scores retained as predictions and never relabelled as human MOS, "
            "clean-reference accuracy or intelligibility."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "listening_and_device_timing_separation",
        "requirement": (
            "Authorized listening or subjective MOS assessment kept separate "
            "from predicted scores, plus target-device timing, memory and "
            "availability measurement for the exact runtime where a device "
            "claim is made."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "evidence_adapter_intake_and_release_review",
        "requirement": (
            "Opt-in developer/evidence adapter intake, license and public-"
            "surface review, independent exact-head approval and explicit "
            "release admission before any SDK exposure."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
]

REQUIRED_ARTIFACTS: List[Dict[str, Any]] = [
    {
        "id": "p835_model_weights",
        "artifact": (
            "DNSMOS P.835 ONNX weights sig.onnx and bak_ovr.onnx with the "
            "recorded SHA-256 digests."
        ),
        "expected_paths": [
            "data/models/dnsmos-p835/sig.onnx",
            "data/models/dnsmos-p835/bak_ovr.onnx",
        ],
        "present": False,
        "rights_requirement": (
            "The weight license, model card and redistribution/execution terms "
            "for the exact files; the surrounding repository license is "
            "code-only."
        ),
        "why_blocked": (
            "No data/models/dnsmos-p835 directory or matching ONNX weight is "
            "present; no download, copy or substitute was attempted."
        ),
    },
    {
        "id": "p835_official_scorer_revision",
        "artifact": (
            "The DeepFilterNet-packaged DNSMOS P.835 scorer pinned at one "
            "immutable revision with a verified digest."
        ),
        "expected_paths": [P835_SCORER_PATH],
        "present": False,
        "rights_requirement": (
            "Scorer code revision, its license and any redistribution terms "
            "for the exact revision."
        ),
        "why_blocked": (
            "The recorded scorer path and its DeepFilterNet environment are "
            "absent; no checkout of the official DNS-Challenge scorer is "
            "present either."
        ),
    },
    {
        "id": "dnsmos_c_checkpoint",
        "artifact": (
            "The NISQA checkpoint runs/NISQA/model_best.pt used by DNSMOS-C, "
            "with an immutable revision and digest."
        ),
        "expected_paths": ["runs/NISQA/model_best.pt"],
        "present": False,
        "rights_requirement": (
            "Checkpoint license, model card, training-data statement and "
            "redistribution/execution approval for the exact file."
        ),
        "why_blocked": (
            "No NISQA checkpoint or DNSMOS-C/NISQA checkout is present; the "
            "Krisp report does not record an exact checkpoint digest or an "
            "immutable scorer-code revision."
        ),
    },
    {
        "id": "qualified_runtime",
        "artifact": (
            "Pinned and approved onnxruntime/numpy (P.835) and "
            "torch/NISQA (DNSMOS-C) environments."
        ),
        "expected_paths": [],
        "present": False,
        "rights_requirement": (
            "Runtime licenses and execution approval for the exact pinned "
            "versions."
        ),
        "why_blocked": (
            "onnxruntime is importable in neither the default python3 nor the "
            "pinned 3.12.16 interpreter, and no DNSMOS-C/NISQA runtime is "
            "pinned or approved for this task."
        ),
    },
    {
        "id": "rights_cleared_cohorts",
        "artifact": (
            "The 743-item EARS P.835 cohort and the 265-output DNSMOS-C "
            "comparison set, with the exact permissions each report records."
        ),
        "expected_paths": [
            "data/runs/voice-enhancement-20261101-ears-preservation-743",
            "data/models/dnsmos-p835",
        ],
        "present": False,
        "rights_requirement": (
            "Participant, corpus, output and redistribution rights at the scope "
            "each report documents; CC BY-NC 4.0 is non-commercial research "
            "media and does not clear redistribution or product use."
        ),
        "why_blocked": (
            "The EARS run directory and the downloaded Krisp outputs are absent "
            "from this workspace; no audio or score bundle is staged, copied or "
            "regenerated."
        ),
    },
    {
        "id": "evidence_adapter_review",
        "artifact": (
            "Evidence-adapter intake, predicted-versus-human labelling review, "
            "aggregation/uncertainty policy and release approval."
        ),
        "expected_paths": [],
        "present": False,
        "rights_requirement": (
            "Independent reviewer, listening panel where applicable and release "
            "approval."
        ),
        "why_blocked": "No intake, listening or release review is in scope here.",
    },
]
NON_CLAIMS: List[str] = [
    "No DNSMOS P.835 or DNSMOS-C model, checkpoint, scorer, runtime or emulator is present, linked, executed or reproduced.",
    "No licensed weight, corpus, vendor output or score bundle is downloaded, copied, bundled or regenerated.",
    "No predicted SIG, BAK, OVL or DNSMOS-C score, ranking, threshold or oracle is claimed; every score slot is null.",
    "No window count, tiling count, polynomial value or aggregation arithmetic is a MOS, a human rating or a quality score.",
    "No listening, device-timing, benchmark or release claim is made.",
    "No installed v0, ABI, registry, descriptor, default, shared build or CI behavior is changed.",
    "No provider or processor is registered, exposed or default-enabled.",
    "No P.808 model, unrelated DNSMOS packaging or unanchored ONNX copy is substituted for the pinned artifacts.",
    "No missing, blocked or adverse result is promoted; no result qualifies.",
]
REPRODUCTION: List[str] = [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
    "python3 run.py --all",
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
    "scorers",
    "scorer_documentation_audit",
    "geometry_reference",
    "postprocessing_reference",
    "aggregation_reference",
    "fixtures",
    "runs",
    "controls",
    "adverse_results",
    "missing_results",
    "failure_controls",
    "acceptance_profile",
    "observed_provenance",
    "artifact_assessment",
    "separation_from_siblings",
    "ranking",
    "release_gates",
    "non_claims",
    "reproduction",
    "regeneration",
}

CONTRACT_KEYS = {
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
    "scorer_contract_summary",
    "required_artifacts",
    "release_gates",
    "artifact_pins",
    "reproduction",
    "non_claims",
}


class ReferenceError(ValueError):
    """Explicit rejection; no rejected value is scored or promoted."""


def _reject_constant(value: str) -> None:
    raise ValueError("non_json_constant:" + value)


def read_strict_json(path: Path) -> Any:
    """Parse strict JSON; duplicate keys, NaN and Infinity are rejected."""
    return parse_strict_json_text(path.read_text(encoding="utf-8"))


def parse_strict_json_text(text: str) -> Any:
    def unique_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    if not text.strip():
        raise ValueError("empty_document")
    value = json.loads(
        text,
        object_pairs_hook=unique_pairs,
        parse_constant=_reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("top_level_document_must_be_object")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


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


def digest_float32(values: Sequence[float]) -> str:
    payload = struct.pack("<%df" % len(values), *[f32(v) for v in values])
    return sha256_bytes(payload)


def _as_int(value: Any, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReferenceError(code)
    return value


def _as_finite(value: Any, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReferenceError(code)
    number = float(value)
    if not math.isfinite(number):
        raise ReferenceError(code)
    return number


def _as_text(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReferenceError(code)
    return value


# ---------------------------------------------------------------------------
# DNSMOS P.835 windowing
# ---------------------------------------------------------------------------


def p835_window_plan(n_samples: int) -> Dict[str, Any]:
    """Reproduce the documented P.835 window replay over one buffer.

    The historical helper doubles the buffer until it is at least 144160
    samples, so every scored window is a contiguous slice of the original
    buffer repeated ``2 ** doublings`` times.  Window count uses the exact
    documented expression ``int(floor(len / fs) - 9.01) + 1``.
    """
    samples = _as_int(n_samples, "window_plan_requires_int")
    if samples <= 0:
        raise ReferenceError("window_plan_requires_positive_samples")
    if samples > MAX_INPUT_SAMPLES:
        raise ReferenceError("window_plan_samples_exceed_bound")
    length = samples
    doublings = 0
    while length < P835_WINDOW_SAMPLES:
        length *= 2
        doublings += 1
    hops = int(
        math.floor(length / P835_SAMPLE_RATE_HZ) - P835_INPUT_LENGTH_S
    ) + 1
    windows: List[Dict[str, int]] = []
    for index in range(hops):
        start = index * P835_HOP_SAMPLES
        end = start + P835_WINDOW_SAMPLES
        original = max(0, min(end, samples) - start)
        windows.append(
            {
                "index": index,
                "start": start,
                "end": end,
                "samples": end - start,
                "original_samples": original,
                "repeated_samples": (end - start) - original,
            }
        )
    last_end = windows[-1]["end"] if windows else 0
    return {
        "input_samples": samples,
        "sample_rate_hz": P835_SAMPLE_RATE_HZ,
        "input_length_s": P835_INPUT_LENGTH_S,
        "window_samples": P835_WINDOW_SAMPLES,
        "hop_samples": P835_HOP_SAMPLES,
        "doublings": doublings,
        "padded_samples": samples * (2 ** doublings),
        "num_hops": hops,
        "windows": windows,
        "covered_samples": last_end,
        "uncovered_samples": length - last_end,
        "repeat_mapping": "padded_index_modulo_input_samples",
        "scored": False,
        "qualifies": False,
    }


def p835_postprocess(
    raw_sig: float,
    raw_bak: float,
    raw_ovr: float,
    personalized: bool = False,
) -> Dict[str, Any]:
    """Apply only the documented polynomial mapping to declared raw values."""
    if not isinstance(personalized, bool):
        raise ReferenceError("personalized_requires_bool")
    raws = {
        "SIG": _as_finite(raw_sig, "raw_value_requires_finite_number"),
        "BAK": _as_finite(raw_bak, "raw_value_requires_finite_number"),
        "OVL": _as_finite(raw_ovr, "raw_value_requires_finite_number"),
    }
    for name, value in raws.items():
        if value < RAW_OUTPUT_MIN or value > RAW_OUTPUT_MAX:
            raise ReferenceError("raw_value_out_of_declared_range:" + name)
    variant = "personalized" if personalized else "standard"
    mapped: Dict[str, float] = {}
    for name, value in raws.items():
        mapped[name] = _horner(P835_POLYFIT[variant][name], value)
    return {
        "raw": raws,
        "mapped": {key: round(value, 9) for key, value in mapped.items()},
        "variant": variant,
        "coefficients": {
            key: list(values) for key, values in P835_POLYFIT[variant].items()
        },
        "is_model_output": False,
        "is_mos": False,
        "is_human_rating": False,
        "uses_fixture_arithmetic_only": True,
        "qualifies": False,
    }


def _horner(coefficients: Sequence[float], value: float) -> float:
    accumulator = 0.0
    for coefficient in coefficients:
        accumulator = accumulator * value + coefficient
    return accumulator


# ---------------------------------------------------------------------------
# DNSMOS-C segmentation
# ---------------------------------------------------------------------------


def segment_kind_accepted(kind: Any) -> str:
    text = _as_text(kind, "segment_kind_requires_text")
    if text not in DNSC_SEGMENT_KINDS:
        raise ReferenceError("unsupported_segment_kind")
    return text


def dnsmos_c_segment_plan(duration_ms: int, kind: str = "primary") -> Dict[str, Any]:
    """Reproduce the documented DNSMOS-C segment/window policy."""
    accepted_kind = segment_kind_accepted(kind)
    duration = _as_int(duration_ms, "segment_plan_requires_int_ms")
    if duration <= 0:
        raise ReferenceError("segment_plan_requires_positive_ms")
    if duration > DNSC_MAX_DURATION_MS:
        raise ReferenceError("segment_plan_duration_exceeds_bound")
    if duration < DNSC_MIN_SEGMENT_MS:
        return {
            "segment_kind": accepted_kind,
            "duration_ms": duration,
            "dropped": True,
            "drop_reason": "segment_shorter_than_1s",
            "repeated": False,
            "repeat_count": 0,
            "tiled_ms": duration,
            "tiling_truncated_ms": 0,
            "windows": [],
            "window_count": 0,
            "distinct_coverage_ms": 0,
            "end_aligned_tail": False,
            "scored": False,
            "qualifies": False,
        }
    if duration < DNSC_WINDOW_MS:
        repeat_count = -(-DNSC_WINDOW_MS // duration)
        tiled = duration * repeat_count
        windows = [{"start_ms": 0, "end_ms": DNSC_WINDOW_MS,
                    "end_aligned_tail": False}]
        return {
            "segment_kind": accepted_kind,
            "duration_ms": duration,
            "dropped": False,
            "drop_reason": None,
            "repeated": True,
            "repeat_count": repeat_count,
            "tiled_ms": tiled,
            "tiling_truncated_ms": tiled - DNSC_WINDOW_MS,
            "windows": windows,
            "window_count": 1,
            "distinct_coverage_ms": DNSC_WINDOW_MS,
            "end_aligned_tail": False,
            "scored": False,
            "qualifies": False,
        }
    starts = list(range(0, duration - DNSC_WINDOW_MS + 1, DNSC_HOP_MS))
    tail = False
    if starts[-1] != duration - DNSC_WINDOW_MS:
        starts.append(duration - DNSC_WINDOW_MS)
        tail = True
    windows = [
        {
            "start_ms": start,
            "end_ms": start + DNSC_WINDOW_MS,
            "end_aligned_tail": tail and start == starts[-1],
        }
        for start in starts
    ]
    coverage = _interval_union_ms(
        [(window["start_ms"], window["end_ms"]) for window in windows]
    )
    return {
        "segment_kind": accepted_kind,
        "duration_ms": duration,
        "dropped": False,
        "drop_reason": None,
        "repeated": False,
        "repeat_count": 1,
        "tiled_ms": duration,
        "tiling_truncated_ms": 0,
        "windows": windows,
        "window_count": len(windows),
        "distinct_coverage_ms": coverage,
        "end_aligned_tail": tail,
        "scored": False,
        "qualifies": False,
    }


def _interval_union_ms(intervals: Sequence[Tuple[int, int]]) -> int:
    if not intervals:
        return 0
    ordered = sorted(intervals)
    total = 0
    current_start, current_end = ordered[0]
    for start, end in ordered[1:]:
        if start > current_end:
            total += current_end - current_start
            current_start, current_end = start, end
        elif end > current_end:
            current_end = end
    total += current_end - current_start
    return total


def dnsmos_c_plan(segments: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(segments, (list, tuple)) or not segments:
        raise ReferenceError("segment_list_requires_non_empty_list")
    rows: List[Dict[str, Any]] = []
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise ReferenceError("segment_requires_object")
        if set(segment) != {"kind", "duration_ms"}:
            raise ReferenceError("segment_field_set_mismatch")
        rows.append(dnsmos_c_segment_plan(segment["duration_ms"], segment["kind"]))
        rows[-1]["segment_index"] = index
    return {
        "segments": rows,
        "segment_count": len(rows),
        "scored_segment_count": sum(1 for row in rows if not row["dropped"]),
        "dropped_segment_count": sum(1 for row in rows if row["dropped"]),
        "window_count": sum(row["window_count"] for row in rows),
        "protocol": DNSC_PROTOCOL,
        "scored": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def exact_mean(values: Sequence[float]) -> float:
    if not isinstance(values, (list, tuple)) or not values:
        raise ReferenceError("mean_requires_non_empty_list")
    numbers = [_as_finite(value, "mean_requires_finite_numbers") for value in values]
    return math.fsum(numbers) / len(numbers)


def scenario_average(per_scenario: Dict[str, float]) -> float:
    if not isinstance(per_scenario, dict) or not per_scenario:
        raise ReferenceError("scenario_map_requires_non_empty_object")
    if len(per_scenario) != 3:
        raise ReferenceError("scenario_map_requires_exactly_three_scenarios")
    names = sorted(per_scenario)
    if len(set(names)) != 3:
        raise ReferenceError("scenario_map_requires_distinct_scenarios")
    values = [
        _as_finite(per_scenario[name], "scenario_value_requires_finite_number")
        for name in names
    ]
    return math.fsum(values) / 3.0


# ---------------------------------------------------------------------------
# Caller/external scorer manifest contract
# ---------------------------------------------------------------------------

MANIFEST_KEYS = {
    "schema_id",
    "metric",
    "sample_rate_hz",
    "channels",
    "models",
    "source_revision",
    "license",
}
MODEL_KEYS = {"name", "sha256", "bytes", "license_id"}
METRIC_MODELS: Dict[str, Tuple[str, ...]] = {
    "dnsmos_p835": ("bak_ovr.onnx", "sig.onnx"),
    "dnsmos_c": ("model_best.pt",),
}
UNKNOWN_LICENSES = {"", "unknown", "UNKNOWN", "none", "NOASSERTION", "unlicensed"}


def validate_scorer_manifest(value: Any) -> Dict[str, Any]:
    """Validate identity/rights metadata only; nothing is loaded or executed."""
    if not isinstance(value, dict):
        raise ReferenceError("manifest_requires_object")
    if set(value) != MANIFEST_KEYS:
        raise ReferenceError("manifest_field_set_mismatch")
    if value["schema_id"] != "audio-sdk/dnsmos-scorer-manifest/0.1":
        raise ReferenceError("manifest_schema_mismatch")
    metric = value["metric"]
    if not isinstance(metric, str) or metric not in METRIC_MODELS:
        raise ReferenceError("manifest_unknown_metric")
    if value["sample_rate_hz"] != P835_SAMPLE_RATE_HZ \
            or isinstance(value["sample_rate_hz"], bool):
        raise ReferenceError("manifest_sample_rate_must_be_16000")
    if value["channels"] != CHANNELS or isinstance(value["channels"], bool):
        raise ReferenceError("manifest_channels_must_be_1")
    revision = value["source_revision"]
    if not isinstance(revision, str) or not _is_hex(revision, 40):
        raise ReferenceError("manifest_source_revision_must_be_40_hex")
    license_id = value["license"]
    if not isinstance(license_id, str) or license_id in UNKNOWN_LICENSES:
        raise ReferenceError("manifest_license_requires_identified_terms")
    models = value["models"]
    if not isinstance(models, list) or not models:
        raise ReferenceError("manifest_models_requires_non_empty_list")
    names: List[str] = []
    for model in models:
        if not isinstance(model, dict) or set(model) != MODEL_KEYS:
            raise ReferenceError("manifest_model_field_set_mismatch")
        name = model["name"]
        if not isinstance(name, str) or "/" in name or "\\" in name \
                or name in {".", ".."}:
            raise ReferenceError("manifest_model_name_must_be_basename")
        if name in names:
            raise ReferenceError("manifest_duplicate_model")
        names.append(name)
        if not isinstance(model["sha256"], str) \
                or not _is_hex(model["sha256"], 64):
            raise ReferenceError("manifest_model_sha256_must_be_64_lower_hex")
        if isinstance(model["bytes"], bool) or not isinstance(model["bytes"], int) \
                or model["bytes"] <= 0:
            raise ReferenceError("manifest_model_bytes_must_be_positive_int")
        model_license = model["license_id"]
        if not isinstance(model_license, str) or model_license in UNKNOWN_LICENSES:
            raise ReferenceError("manifest_model_license_requires_identified_terms")
    if tuple(sorted(names)) != METRIC_MODELS[metric]:
        raise ReferenceError("manifest_model_set_does_not_match_metric")
    return {
        "accepted": True,
        "metric": metric,
        "models": sorted(names),
        "admitted_for_execution": False,
        "admission_blocker": (
            "no approved runtime, no pinned scorer revision and no runner "
            "exist in this package"
        ),
        "qualifies": False,
    }


def _is_hex(text: str, length: int) -> bool:
    return len(text) == length and all(
        character in "0123456789abcdef" for character in text
    )


def classify_observed_artifact(
    name: Any, metric: Any, sha256: Any
) -> Dict[str, Any]:
    """Admit only an exact name+digest pair; never a substitute packaging."""
    text_name = _as_text(name, "artifact_name_requires_text")
    if not isinstance(sha256, str) or not _is_hex(sha256, 64):
        raise ReferenceError("invalid_sha256")
    if not isinstance(metric, str) or metric not in METRIC_MODELS:
        raise ReferenceError("unknown_metric")
    if text_name not in METRIC_MODELS[metric]:
        raise ReferenceError("wrong_model_identity")
    expected = P835_MODELS.get(text_name)
    if expected is None:
        raise ReferenceError("wrong_model_identity")
    if expected != sha256:
        raise ReferenceError("wrong_model_digest")
    return {
        "artifact": text_name,
        "metric": metric,
        "identity_accepted": True,
        "admitted_for_execution": False,
        "requires_rights_review": True,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Fixtures (declared synthetic values only)
# ---------------------------------------------------------------------------

P835_FIXTURE_SAMPLES = 12000
P835_FIXTURE_SEED = 20261126
DNSC_FIXTURE_SEGMENTS: List[Dict[str, Any]] = [
    {"kind": "primary", "duration_ms": 950},
    {"kind": "mix", "duration_ms": 1000},
    {"kind": "primary", "duration_ms": 4000},
    {"kind": "mix", "duration_ms": 10000},
    {"kind": "primary", "duration_ms": 12345},
    {"kind": "mix", "duration_ms": 15000},
]


def _lcg(seed: int, count: int) -> List[float]:
    state = seed & 0x7FFFFFFF
    values: List[float] = []
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append((state / 1073741824.0 - 1.0) * 0.25)
    return values


def p835_fixture_values(samples: int = P835_FIXTURE_SAMPLES) -> List[float]:
    count = _as_int(samples, "fixture_requires_int")
    if count <= 0 or count > MAX_INPUT_SAMPLES:
        raise ReferenceError("fixture_samples_out_of_range")
    return _lcg(P835_FIXTURE_SEED, count)


def fixture_payload() -> Dict[str, Any]:
    values = p835_fixture_values()
    silence = [0.0] * P835_WINDOW_SAMPLES
    return {
        "p835": {
            "sample_rate_hz": P835_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "samples": P835_FIXTURE_SAMPLES,
            "float32_digest": digest_float32(values),
            "seed": P835_FIXTURE_SEED,
            "is_speech": False,
            "is_corpus": False,
        },
        "p835_silence": {
            "samples": P835_WINDOW_SAMPLES,
            "float32_digest": digest_float32(silence),
            "is_speech": False,
        },
        "dnsmos_c": {
            "segments": [dict(segment) for segment in DNSC_FIXTURE_SEGMENTS],
            "sample_rate_hz": DNSC_SAMPLE_RATE_HZ,
            "is_speech": False,
            "is_corpus": False,
        },
    }


# ---------------------------------------------------------------------------
# Geometry reference cases
# ---------------------------------------------------------------------------


def p835_cases() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for samples in (12000, 144159, 144160, 144161, 300000):
        plan = p835_window_plan(samples)
        rows.append(
            {
                "input_samples": samples,
                "doublings": plan["doublings"],
                "padded_samples": plan["padded_samples"],
                "num_hops": plan["num_hops"],
                "first_window": [
                    plan["windows"][0]["start"],
                    plan["windows"][0]["end"],
                ],
                "last_window": [
                    plan["windows"][-1]["start"],
                    plan["windows"][-1]["end"],
                ],
                "first_window_original_samples":
                    plan["windows"][0]["original_samples"],
                "uncovered_samples": plan["uncovered_samples"],
                "scored": False,
                "qualifies": False,
            }
        )
    return rows


def dnsmos_c_cases() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for duration_ms, kind in (
        (999, "primary"),
        (1000, "mix"),
        (4000, "primary"),
        (10000, "mix"),
        (12345, "primary"),
        (15000, "mix"),
        (20000, "primary"),
    ):
        plan = dnsmos_c_segment_plan(duration_ms, kind)
        rows.append(
            {
                "duration_ms": duration_ms,
                "segment_kind": kind,
                "dropped": plan["dropped"],
                "repeated": plan["repeated"],
                "repeat_count": plan["repeat_count"],
                "tiling_truncated_ms": plan["tiling_truncated_ms"],
                "window_count": plan["window_count"],
                "first_window": (
                    [plan["windows"][0]["start_ms"], plan["windows"][0]["end_ms"]]
                    if plan["windows"] else None
                ),
                "last_window": (
                    [plan["windows"][-1]["start_ms"], plan["windows"][-1]["end_ms"]]
                    if plan["windows"] else None
                ),
                "end_aligned_tail": plan["end_aligned_tail"],
                "scored": False,
                "qualifies": False,
            }
        )
    return rows


def geometry_reference() -> Dict[str, Any]:
    return {
        "p835_rule": P835_SEGMENTATION,
        "p835_cases": p835_cases(),
        "dnsmos_c_rule": DNSC_PROTOCOL,
        "dnsmos_c_cases": dnsmos_c_cases(),
        "p835_bits_reproduced": False,
        "dnsmos_c_bits_reproduced": False,
        "note": (
            "Integer window/tiling accounting only. No waveform is scored, no "
            "mel spectrogram is computed and no window count is a result."
        ),
    }


def postprocessing_reference() -> Dict[str, Any]:
    standard = p835_postprocess(2.5, 3.0, 2.8, personalized=False)
    personalized = p835_postprocess(2.5, 3.0, 2.8, personalized=True)
    return {
        "mapping_note": P835_POSTPROCESS_NOTE,
        "coefficient_source_verified": False,
        "fixture_raw": {"SIG": 2.5, "BAK": 3.0, "OVL": 2.8},
        "standard": standard["mapped"],
        "personalized": personalized["mapped"],
        "arithmetic": "IEEE-754 binary64 Horner evaluation",
        "np_polyval_bit_parity_claimed": False,
        "is_model_output": False,
        "is_mos": False,
        "qualifies": False,
    }


def aggregation_reference() -> Dict[str, Any]:
    values = [3.0, 4.25, 3.5, 4.75]
    other = [4.75, 3.5, 4.25, 3.0]
    scenarios = {"work": 3.0, "call_center": 3.5, "phone_calls": 4.0}
    return {
        "mean_example": exact_mean(values),
        "mean_example_values": values,
        "mean_is_order_invariant": exact_mean(values) == exact_mean(other),
        "scenario_average": scenario_average(scenarios),
        "scenario_values": scenarios,
        "scenario_weights": "equal",
        "arithmetic": "IEEE-754 binary64 math.fsum in ascending key order",
        "np_mean_bit_parity_claimed": False,
        "is_a_score": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Scorer records
# ---------------------------------------------------------------------------


def scorers() -> List[Dict[str, Any]]:
    return [
        {
            "id": "dnsmos_p835",
            "display_name": "DNSMOS P.835",
            "status": "blocked",
            "output_kind": "predicted_no_reference_mos",
            "outputs": list(P835_OUTPUTS),
            "sample_rate_hz": P835_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "input_length_s": P835_INPUT_LENGTH_S,
            "window_samples": P835_WINDOW_SAMPLES,
            "hop_samples": P835_HOP_SAMPLES,
            "segmentation": P835_SEGMENTATION,
            "models": [
                {
                    "name": name,
                    "expected_sha256": digest,
                    "present": False,
                    "admitted": False,
                }
                for name, digest in sorted(P835_MODELS.items())
            ],
            "scorer": {
                "path": P835_SCORER_PATH,
                "expected_sha256": P835_SCORER_SHA256,
                "present": False,
                "admitted": False,
            },
            "score_slots": {name: None for name in P835_OUTPUTS},
            "score_status": "unavailable_weights_source_and_runtime_absent",
            "scores_are_predictions": True,
            "scores_are_human_ratings": False,
            "scores_reproduced": False,
            "qualifies": False,
        },
        {
            "id": "dnsmos_c",
            "display_name": "DNSMOS-C",
            "status": "blocked",
            "output_kind": "predicted_no_reference_mos",
            "outputs": list(DNSC_OUTPUTS),
            "sample_rate_hz": DNSC_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "segment_kinds": list(DNSC_SEGMENT_KINDS),
            "min_segment_ms": DNSC_MIN_SEGMENT_MS,
            "window_ms": DNSC_WINDOW_MS,
            "hop_ms": DNSC_HOP_MS,
            "protocol": DNSC_PROTOCOL,
            "checkpoint": {
                "path": DNSC_CHECKPOINT,
                "expected_sha256": None,
                "immutable_revision": None,
                "present": False,
                "admitted": False,
            },
            "source": {
                "url": DNSC_SOURCE,
                "pinned_revision": None,
                "present": False,
                "admitted": False,
            },
            "score_slots": {name: None for name in DNSC_OUTPUTS},
            "score_status": "unavailable_checkpoint_source_and_runtime_absent",
            "scores_are_predictions": True,
            "scores_are_human_ratings": False,
            "scores_reproduced": False,
            "qualifies": False,
        },
    ]


P835_DOCUMENTATION_TOKENS = (
    "data/models/dnsmos-p835",
    "sig.onnx",
    "bak_ovr.onnx",
    "df/scripts/dnsmos.py",
    "CPUExecutionProvider",
    'NAMES = ("sig", "bak", "ovl")',
)
DNSC_DOCUMENTATION_TOKENS = (
    "NISQA",
    "model_best.pt",
    "`primary` and `mix`",
    "shorter than 1 second",
    "repeated to 10 seconds",
    "10-second windows with 5-second hops",
    "end-aligned tail",
    "unweighted mean of the three scenarios",
)


def scorer_documentation_audit() -> Dict[str, Any]:
    p835_path = WORKSPACE / (
        "research/voice-enhancement-20261101/agent-dnsmos-ears-743/"
        "score_existing_outputs.py"
    )
    dnsc_path = WORKSPACE / "research/cpp-library-krisp-benchmark-20261109.md"
    p835_text = p835_path.read_text(encoding="utf-8")
    dnsc_text = dnsc_path.read_text(encoding="utf-8")
    p835_checks = [
        {"token": token, "present": token in p835_text}
        for token in P835_DOCUMENTATION_TOKENS
    ]
    dnsc_checks = [
        {"token": token, "present": token in dnsc_text}
        for token in DNSC_DOCUMENTATION_TOKENS
    ]
    return {
        "p835_script": {
            "path": (
                "research/voice-enhancement-20261101/agent-dnsmos-ears-743/"
                "score_existing_outputs.py"
            ),
            "sha256": digest_file(p835_path),
            "tokens": p835_checks,
            "all_tokens_present": all(item["present"] for item in p835_checks),
        },
        "dnsmos_c_report": {
            "path": "research/cpp-library-krisp-benchmark-20261109.md",
            "sha256": digest_file(dnsc_path),
            "tokens": dnsc_checks,
            "all_tokens_present": all(item["present"] for item in dnsc_checks),
        },
        "reproduces_feature_values": False,
        "reproduces_scores": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Runs and controls
# ---------------------------------------------------------------------------


def runs() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for case in p835_cases():
        rows.append(
            {
                "run_id": "p835-%d" % case["input_samples"],
                "scorer": "dnsmos_p835",
                "status": "geometry_only_not_scored",
                "geometry": case,
                "scores": {name: None for name in P835_OUTPUTS},
                "score_status": "unavailable_weights_source_and_runtime_absent",
                "scores_are_predictions": True,
                "scores_are_human_ratings": False,
                "qualifies": False,
            }
        )
    for case in dnsmos_c_cases():
        rows.append(
            {
                "run_id": "dnsmos-c-%d-%s"
                % (case["duration_ms"], case["segment_kind"]),
                "scorer": "dnsmos_c",
                "status": "geometry_only_not_scored",
                "geometry": case,
                "scores": {name: None for name in DNSC_OUTPUTS},
                "score_status": "unavailable_checkpoint_source_and_runtime_absent",
                "scores_are_predictions": True,
                "scores_are_human_ratings": False,
                "qualifies": False,
            }
        )
    return rows


CONTROL_STATUS = {
    "p835_identity": "geometry_only_not_scored",
    "p835_silence": "geometry_only_not_scored",
    "p835_single_sample": "geometry_only_not_scored",
    "p835_one_sample_over": "geometry_only_not_scored",
    "dnsmos_c_one_second": "geometry_only_not_scored",
    "dnsmos_c_exact_two_windows": "geometry_only_not_scored",
}


def controls() -> Dict[str, Dict[str, Any]]:
    identity = p835_window_plan(P835_WINDOW_SAMPLES)
    single = p835_window_plan(1)
    over = p835_window_plan(P835_WINDOW_SAMPLES + 1)
    one_second = dnsmos_c_segment_plan(1000, "mix")
    two_windows = dnsmos_c_segment_plan(15000, "primary")
    return {
        "p835_identity": {
            "status": CONTROL_STATUS["p835_identity"],
            "num_hops": identity["num_hops"],
            "doublings": identity["doublings"],
            "uncovered_samples": identity["uncovered_samples"],
            "scores": {name: None for name in P835_OUTPUTS},
            "qualifies": False,
        },
        "p835_silence": {
            "status": CONTROL_STATUS["p835_silence"],
            "float32_digest": digest_float32(
                [0.0] * P835_WINDOW_SAMPLES
            ),
            "num_hops": identity["num_hops"],
            "scores": {name: None for name in P835_OUTPUTS},
            "qualifies": False,
        },
        "p835_single_sample": {
            "status": CONTROL_STATUS["p835_single_sample"],
            "doublings": single["doublings"],
            "padded_samples": single["padded_samples"],
            "num_hops": single["num_hops"],
            "first_window_original_samples":
                single["windows"][0]["original_samples"],
            "scores": {name: None for name in P835_OUTPUTS},
            "qualifies": False,
        },
        "p835_one_sample_over": {
            "status": CONTROL_STATUS["p835_one_sample_over"],
            "num_hops": over["num_hops"],
            "uncovered_samples": over["uncovered_samples"],
            "scores": {name: None for name in P835_OUTPUTS},
            "qualifies": False,
        },
        "dnsmos_c_one_second": {
            "status": CONTROL_STATUS["dnsmos_c_one_second"],
            "repeat_count": one_second["repeat_count"],
            "window_count": one_second["window_count"],
            "tiling_truncated_ms": one_second["tiling_truncated_ms"],
            "scores": {name: None for name in DNSC_OUTPUTS},
            "qualifies": False,
        },
        "dnsmos_c_exact_two_windows": {
            "status": CONTROL_STATUS["dnsmos_c_exact_two_windows"],
            "window_count": two_windows["window_count"],
            "end_aligned_tail": two_windows["end_aligned_tail"],
            "scores": {name: None for name in DNSC_OUTPUTS},
            "qualifies": False,
        },
    }


# ---------------------------------------------------------------------------
# Adverse results
# ---------------------------------------------------------------------------


def _expect(code: str, call: Callable[[], Any]) -> str:
    try:
        call()
    except ReferenceError as error:
        return str(error)
    except json.JSONDecodeError:
        return "JSONDecodeError"
    except ValueError as error:
        return str(error)
    except (TypeError, KeyError) as error:
        return type(error).__name__
    return "accepted"


def _manifest_template(metric: str = "dnsmos_p835") -> Dict[str, Any]:
    if metric == "dnsmos_p835":
        models = [
            {
                "name": "sig.onnx",
                "sha256": P835_MODELS["sig.onnx"],
                "bytes": 1000,
                "license_id": "NOASSERTION-NOT-A-LICENSE",
            },
            {
                "name": "bak_ovr.onnx",
                "sha256": P835_MODELS["bak_ovr.onnx"],
                "bytes": 2000,
                "license_id": "NOASSERTION-NOT-A-LICENSE",
            },
        ]
    else:
        models = [
            {
                "name": "model_best.pt",
                "sha256": "0" * 64,
                "bytes": 3000,
                "license_id": "NOASSERTION-NOT-A-LICENSE",
            }
        ]
    return {
        "schema_id": "audio-sdk/dnsmos-scorer-manifest/0.1",
        "metric": metric,
        "sample_rate_hz": P835_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "models": models,
        "source_revision": "0" * 40,
        "license": "NOASSERTION-NOT-A-LICENSE",
    }


def _manifest_with(**changes: Any) -> Dict[str, Any]:
    manifest = _manifest_template(changes.pop("metric", "dnsmos_p835"))
    manifest.update(changes)
    return manifest


def adverse_results() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def case(result_id: str, category: str, expected: str,
             call: Callable[[], Any]) -> None:
        observed = _expect(expected, call)
        rows.append(
            {
                "result_id": result_id,
                "category": category,
                "expected_code": expected,
                "observed_code": observed,
                "rejected": observed == expected,
                "state_unchanged": True,
                "qualifies": False,
            }
        )

    # Strict JSON handling.
    case("json_duplicate_key", "strict_json", "duplicate_json_key:metric",
         lambda: parse_strict_json_text('{"metric":1,"metric":2}'))
    case("json_nan_constant", "strict_json", "non_json_constant:NaN",
         lambda: parse_strict_json_text('{"value":NaN}'))
    case("json_infinity_constant", "strict_json", "non_json_constant:Infinity",
         lambda: parse_strict_json_text('{"value":Infinity}'))
    case("json_malformed", "strict_json", "JSONDecodeError",
         lambda: parse_strict_json_text("{"))
    case("json_top_level_array", "strict_json",
         "top_level_document_must_be_object",
         lambda: parse_strict_json_text("[1,2,3]"))
    case("json_empty_document", "strict_json", "empty_document",
         lambda: parse_strict_json_text("   "))

    # P.835 window-plan validation.
    case("window_bool_samples", "p835_window", "window_plan_requires_int",
         lambda: p835_window_plan(True))
    case("window_float_samples", "p835_window", "window_plan_requires_int",
         lambda: p835_window_plan(144160.0))
    case("window_zero_samples", "p835_window",
         "window_plan_requires_positive_samples",
         lambda: p835_window_plan(0))
    case("window_negative_samples", "p835_window",
         "window_plan_requires_positive_samples",
         lambda: p835_window_plan(-1))
    case("window_text_samples", "p835_window", "window_plan_requires_int",
         lambda: p835_window_plan("144160"))
    case("window_none_samples", "p835_window", "window_plan_requires_int",
         lambda: p835_window_plan(None))
    case("window_oversized_samples", "p835_window",
         "window_plan_samples_exceed_bound",
         lambda: p835_window_plan(MAX_INPUT_SAMPLES + 1))

    # DNSMOS-C segment validation.
    case("segment_bool_duration", "dnsmos_c", "segment_plan_requires_int_ms",
         lambda: dnsmos_c_segment_plan(True))
    case("segment_float_duration", "dnsmos_c",
         "segment_plan_requires_int_ms",
         lambda: dnsmos_c_segment_plan(1000.5))
    case("segment_zero_duration", "dnsmos_c",
         "segment_plan_requires_positive_ms",
         lambda: dnsmos_c_segment_plan(0))
    case("segment_negative_duration", "dnsmos_c",
         "segment_plan_requires_positive_ms",
         lambda: dnsmos_c_segment_plan(-1000))
    case("segment_oversized_duration", "dnsmos_c",
         "segment_plan_duration_exceeds_bound",
         lambda: dnsmos_c_segment_plan(DNSC_MAX_DURATION_MS + 1))
    case("segment_unknown_kind", "dnsmos_c", "unsupported_segment_kind",
         lambda: dnsmos_c_segment_plan(1000, "other"))
    case("segment_empty_kind", "dnsmos_c", "segment_kind_requires_text",
         lambda: dnsmos_c_segment_plan(1000, ""))
    case("segment_empty_list", "dnsmos_c",
         "segment_list_requires_non_empty_list",
         lambda: dnsmos_c_plan([]))
    case("segment_non_object", "dnsmos_c", "segment_requires_object",
         lambda: dnsmos_c_plan(["primary"]))
    case("segment_extra_field", "dnsmos_c", "segment_field_set_mismatch",
         lambda: dnsmos_c_plan([
             {"kind": "primary", "duration_ms": 1000, "extra": 1}
         ]))

    # Aggregation validation.
    case("mean_empty", "aggregation", "mean_requires_non_empty_list",
         lambda: exact_mean([]))
    case("mean_nan", "aggregation", "mean_requires_finite_numbers",
         lambda: exact_mean([3.0, float("nan")]))
    case("mean_infinity", "aggregation", "mean_requires_finite_numbers",
         lambda: exact_mean([3.0, float("inf")]))
    case("mean_text", "aggregation", "mean_requires_finite_numbers",
         lambda: exact_mean([3.0, "4.0"]))
    case("mean_bool", "aggregation", "mean_requires_finite_numbers",
         lambda: exact_mean([3.0, True]))
    case("scenario_empty", "aggregation",
         "scenario_map_requires_non_empty_object",
         lambda: scenario_average({}))
    case("scenario_two", "aggregation",
         "scenario_map_requires_exactly_three_scenarios",
         lambda: scenario_average({"a": 3.0, "b": 4.0}))
    case("scenario_nan", "aggregation",
         "scenario_value_requires_finite_number",
         lambda: scenario_average({"a": 3.0, "b": 4.0, "c": float("nan")}))

    # Post-processing validation.
    case("postprocess_nan", "postprocess", "raw_value_requires_finite_number",
         lambda: p835_postprocess(float("nan"), 3.0, 2.8))
    case("postprocess_infinity", "postprocess",
         "raw_value_requires_finite_number",
         lambda: p835_postprocess(2.5, float("inf"), 2.8))
    case("postprocess_out_of_range", "postprocess",
         "raw_value_out_of_declared_range:SIG",
         lambda: p835_postprocess(9.0, 3.0, 2.8))
    case("postprocess_negative", "postprocess",
         "raw_value_out_of_declared_range:BAK",
         lambda: p835_postprocess(2.5, -0.1, 2.8))
    case("postprocess_bool", "postprocess", "raw_value_requires_finite_number",
         lambda: p835_postprocess(True, 3.0, 2.8))
    case("postprocess_text", "postprocess", "raw_value_requires_finite_number",
         lambda: p835_postprocess("2.5", 3.0, 2.8))
    case("postprocess_variant", "postprocess", "personalized_requires_bool",
         lambda: p835_postprocess(2.5, 3.0, 2.8, personalized="yes"))

    # Manifest identity/rights validation.
    case("manifest_not_object", "manifest", "manifest_requires_object",
         lambda: validate_scorer_manifest([]))
    case("manifest_missing_field", "manifest", "manifest_field_set_mismatch",
         lambda: validate_scorer_manifest(
             {key: value for key, value in _manifest_template().items()
              if key != "license"}))
    case("manifest_extra_field", "manifest", "manifest_field_set_mismatch",
         lambda: validate_scorer_manifest(
             _manifest_with(extra="field")))
    case("manifest_unknown_metric", "manifest", "manifest_unknown_metric",
         lambda: validate_scorer_manifest(_manifest_with(metric="dnsmos_p808")))
    case("manifest_wrong_rate", "manifest",
         "manifest_sample_rate_must_be_16000",
         lambda: validate_scorer_manifest(
             _manifest_with(sample_rate_hz=48000)))
    case("manifest_wrong_channels", "manifest",
         "manifest_channels_must_be_1",
         lambda: validate_scorer_manifest(_manifest_with(channels=2)))
    case("manifest_bad_sha", "manifest",
         "manifest_model_sha256_must_be_64_lower_hex",
         lambda: validate_scorer_manifest(
             _manifest_with(models=[{
                 "name": "sig.onnx",
                 "sha256": "ABCDEF",
                 "bytes": 1000,
                 "license_id": "approved",
             }, {
                 "name": "bak_ovr.onnx",
                 "sha256": P835_MODELS["bak_ovr.onnx"],
                 "bytes": 2000,
                 "license_id": "approved",
             }])))
    case("manifest_zero_bytes", "manifest",
         "manifest_model_bytes_must_be_positive_int",
         lambda: validate_scorer_manifest(
             _manifest_with(models=[{
                 "name": "sig.onnx",
                 "sha256": P835_MODELS["sig.onnx"],
                 "bytes": 0,
                 "license_id": "approved",
             }, {
                 "name": "bak_ovr.onnx",
                 "sha256": P835_MODELS["bak_ovr.onnx"],
                 "bytes": 2000,
                 "license_id": "approved",
             }])))
    case("manifest_unknown_license", "manifest",
         "manifest_license_requires_identified_terms",
         lambda: validate_scorer_manifest(_manifest_with(license="unknown")))
    case("manifest_unpinned_revision", "manifest",
         "manifest_source_revision_must_be_40_hex",
         lambda: validate_scorer_manifest(
             _manifest_with(source_revision="main")))
    case("manifest_duplicate_model", "manifest", "manifest_duplicate_model",
         lambda: validate_scorer_manifest(
             _manifest_with(models=[
                 {
                     "name": "sig.onnx",
                     "sha256": P835_MODELS["sig.onnx"],
                     "bytes": 1000,
                     "license_id": "approved",
                 },
                 {
                     "name": "sig.onnx",
                     "sha256": P835_MODELS["sig.onnx"],
                     "bytes": 1000,
                     "license_id": "approved",
                 },
             ])))
    case("manifest_wrong_model_set", "manifest",
         "manifest_model_set_does_not_match_metric",
         lambda: validate_scorer_manifest(
             _manifest_with(models=[{
                 "name": "model_v8.onnx",
                 "sha256": "0" * 64,
                 "bytes": 1000,
                 "license_id": "approved",
             }, {
                 "name": "bak_ovr.onnx",
                 "sha256": P835_MODELS["bak_ovr.onnx"],
                 "bytes": 2000,
                 "license_id": "approved",
             }])))
    case("manifest_path_traversal", "manifest",
         "manifest_model_name_must_be_basename",
         lambda: validate_scorer_manifest(
             _manifest_with(models=[{
                 "name": "../sig.onnx",
                 "sha256": P835_MODELS["sig.onnx"],
                 "bytes": 1000,
                 "license_id": "approved",
             }, {
                 "name": "bak_ovr.onnx",
                 "sha256": P835_MODELS["bak_ovr.onnx"],
                 "bytes": 2000,
                 "license_id": "approved",
             }])))

    # Non-substitution admission checks.
    case("substitute_p808_model_as_p835", "admission",
         "wrong_model_identity",
         lambda: classify_observed_artifact(
             "model_v8.onnx", "dnsmos_p835", "0" * 64))
    case("substitute_combined_p835_model", "admission",
         "wrong_model_identity",
         lambda: classify_observed_artifact(
             "sig_bak_ovr.onnx", "dnsmos_p835", "0" * 64))
    case("substitute_wrong_digest", "admission", "wrong_model_digest",
         lambda: classify_observed_artifact(
             "sig.onnx", "dnsmos_p835", "0" * 64))
    case("substitute_unknown_metric", "admission", "unknown_metric",
         lambda: classify_observed_artifact(
             "sig.onnx", "dnsmos_p806", P835_MODELS["sig.onnx"]))

    return rows


def _check_all_rejected(rows: Sequence[Dict[str, Any]]) -> bool:
    return all(row["rejected"] for row in rows)


# ---------------------------------------------------------------------------
# Missing results
# ---------------------------------------------------------------------------


def missing_results() -> List[Dict[str, Any]]:
    rows = [
        ("p835_predictions_not_reproduced", "dnsmos_p835",
         "The two P.835 ONNX weights, the pinned scorer and an approved "
         "onnxruntime environment are absent."),
        ("dnsmos_c_predictions_not_reproduced", "dnsmos_c",
         "The NISQA checkpoint, a pinned DNSMOS-C source revision and a "
         "torch/NISQA runtime are absent."),
        ("ears_743_cohort_not_scored", "dnsmos_p835",
         "The 743-item EARS inputs and saved outputs are not staged in this "
         "workspace; no audio is read or regenerated."),
        ("krisp_265_outputs_not_scored", "dnsmos_c",
         "The 265-output CC BY-NC comparison set is not staged; no vendor "
         "output is copied, rescored or redistributed."),
        ("human_listening_not_run", "both",
         "No authorized listening panel or subjective MOS exists; predicted "
         "scores are never relabelled as human ratings."),
        ("device_timing_not_measured", "both",
         "No target-device timing, memory, availability or content-delay "
         "measurement exists for either scorer."),
        ("benchmark_not_run", "both",
         "No audio-bench submission, benchmark run or comparison ranking is "
         "produced by this package."),
        ("release_not_claimed", "both",
         "No provider, processor, descriptor, default or release admission is "
         "requested or granted."),
    ]
    return [
        {
            "result_id": result_id,
            "scorer": scorer,
            "status": "blocked",
            "scores": None,
            "reason": reason,
            "qualifies": False,
        }
        for result_id, scorer, reason in rows
    ]


# ---------------------------------------------------------------------------
# Acceptance profile
# ---------------------------------------------------------------------------


def acceptance_profile() -> Dict[str, Any]:
    items = [
        {
            "id": "EV-1",
            "requirement": "Pin the scorer",
            "status": "blocked",
            "detail": (
                "P.835 scorer path and digest are recorded but absent; "
                "DNSMOS-C/NISQA has no pinned source revision or checkpoint "
                "digest."
            ),
            "qualifies": False,
        },
        {
            "id": "EV-2",
            "requirement": "Pin the corpus and cohort",
            "status": "blocked",
            "detail": (
                "The 743-item EARS cohort and the 265-output Krisp set are "
                "documented but not staged; CC BY-NC scope does not clear "
                "redistribution."
            ),
            "qualifies": False,
        },
        {
            "id": "EV-3",
            "requirement": "Freeze aggregation",
            "status": "synthetic_control_only",
            "detail": (
                "Equal-weight means and the three-scenario average are "
                "reproduced on declared synthetic integers/floats only."
            ),
            "qualifies": False,
        },
        {
            "id": "EV-4",
            "requirement": "Retain failed items and controls",
            "status": "synthetic_control_only",
            "detail": (
                "%d rejected inputs and %d blocked results are retained with "
                "codes; each control is geometry-only."
                % (len(adverse_results()), len(missing_results()))
            ),
            "qualifies": False,
        },
        {
            "id": "EV-5",
            "requirement": (
                "Separate paired, unpaired, synthetic, human and "
                "source-reported evidence"
            ),
            "status": "proposal_only",
            "detail": (
                "Predicted scores, human MOS, clean-reference measures and "
                "source-reported values are distinct fields; none is pooled."
            ),
            "qualifies": False,
        },
        {
            "id": "EV-6",
            "requirement": (
                "Validate one invalid/missing case and one representative "
                "valid result through the bundle"
            ),
            "status": "synthetic_control_only",
            "detail": (
                "Invalid/missing cases are machine-checked; no representative "
                "valid scored result exists to validate."
            ),
            "qualifies": False,
        },
    ]
    return {
        "profile": "evidence",
        "source_pin": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "items": items,
        "all_qualify": False,
        "qualifies": False,
        "missing_result_promoted": False,
    }


# ---------------------------------------------------------------------------
# Observed provenance (documented, not reproduced here)
# ---------------------------------------------------------------------------


def observed_provenance() -> Dict[str, Any]:
    return {
        "reproduced_here": False,
        "documented_context": [
            {
                "id": "OP-1",
                "owner_task": "agent-dnsmos-ears-743",
                "source_pin": (
                    "research/voice-enhancement-20261101/"
                    "agent-dnsmos-ears-743/REPORT.md"
                ),
                "scope": (
                    "743 EARS inputs plus saved FastEnhancer Small and "
                    "DeepFilterNet3 outputs; 16 kHz mono; 9 s windows with 1 s "
                    "hop; ONNX Runtime CPU; 10,000 item-bootstrap draws"
                ),
                "claims": {
                    "predicted_sig": {"input": 3.935, "fastenhancer_small": 3.8,
                                      "deepfilternet3": 3.873},
                    "predicted_bak": {"input": 3.273,
                                      "fastenhancer_small": 4.335,
                                      "deepfilternet3": 4.399},
                    "predicted_ovl": {"input": 3.189,
                                      "fastenhancer_small": 3.427,
                                      "deepfilternet3": 3.575},
                },
                "labels": "predicted_no_reference_p835",
                "is_human_rating": False,
                "is_mos": False,
                "is_intelligibility_measure": False,
                "reproduced_here": False,
                "artifact_status": (
                    "EARS audio, saved outputs, data/runs and data/models and "
                    "the pinned scorer are absent from this workspace"
                ),
            },
            {
                "id": "OP-2",
                "owner_task": "SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING",
                "source_pin": "research/cpp-library-krisp-benchmark-20261109.md",
                "scope": (
                    "265-item CC BY-NC 4.0 corpus; raw input, Krisp VI 2.5 "
                    "Default and audio_enhance v1.1.0 presets; DNSMOS-C via the "
                    "NISQA checkpoint on primary/mix segments; 16 kHz; 10 s "
                    "windows with 5 s hop"
                ),
                "claims": {
                    "scenario_average": {
                        "raw": 3.369,
                        "krisp_vi_2_5_default": 3.815,
                        "audio_enhance_basic_v1": 3.519,
                        "audio_enhance_voice_focus_v1": 3.641,
                    },
                    "wer": "vendor-reported 11-configuration aggregate; no "
                           "local WER measured",
                },
                "labels": "predicted_dnsmos_c",
                "is_human_rating": False,
                "is_mos": False,
                "is_intelligibility_measure": False,
                "reproduced_here": False,
                "artifact_status": (
                    "corpus outputs, NISQA checkpoint and a pinned DNSMOS-C "
                    "scorer revision are absent; no digest or immutable "
                    "revision is recorded in the report"
                ),
            },
            {
                "id": "OP-3",
                "owner_task": "agent-dnsmos-ears-743",
                "source_pin": (
                    "research/voice-enhancement-20261101/"
                    "agent-dnsmos-ears-743/REPORT.md"
                ),
                "scope": "expected P.835 artifact identities",
                "claims": {
                    "sig.onnx": P835_MODELS["sig.onnx"],
                    "bak_ovr.onnx": P835_MODELS["bak_ovr.onnx"],
                    "scorer_script": P835_SCORER_SHA256,
                },
                "labels": "artifact_digest",
                "is_human_rating": False,
                "is_mos": False,
                "is_intelligibility_measure": False,
                "reproduced_here": False,
                "artifact_status": "digests recorded in text; bytes absent",
            },
            {
                "id": "OP-4",
                "owner_task": "SDK-DNSMOS-P-835-AND-DNSMOS-C",
                "source_pin": "sandbox filesystem observation",
                "scope": (
                    "incidental unanchored ONNX copies inside an unrelated "
                    "voice-conversion research checkout"
                ),
                "claims": {
                    "model_v8.onnx": (
                        "9246480c58567bc6affd4200938e77eef49468c8bc7ed3776d1"
                        "09c07456f6e91"
                    ),
                    "sig_bak_ovr.onnx": (
                        "269fbebdb513aa23cddfbb593542ecc540284a91849ac505168"
                        "70e1ac78f6edd"
                    ),
                    "path": (
                        "research/voice-conversion-eval-20261101/repos/"
                        "seed-vc/baselines/dnsmos"
                    ),
                },
                "labels": "unadmitted_incidental_onnx",
                "is_human_rating": False,
                "is_mos": False,
                "is_intelligibility_measure": False,
                "reproduced_here": False,
                "admitted": False,
                "substitution_allowed": False,
                "artifact_status": (
                    "P.808 and combined P.835 packaging from an unrelated "
                    "third-party checkout; no per-file terms, model card or "
                    "verified revision; not the pinned EARS artifacts and not "
                    "admitted for execution or qualification"
                ),
            },
        ],
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Artifact assessment
# ---------------------------------------------------------------------------


def artifact_assessment() -> Dict[str, Any]:
    return {
        "all_required_absent": True,
        "weights_presence": {
            "present": False,
            "expected": [
                P835_MODEL_DIR + "/sig.onnx",
                P835_MODEL_DIR + "/bak_ovr.onnx",
            ],
            "note": "data/models and data/models/dnsmos-p835 do not exist.",
        },
        "scorer_presence": {
            "present": False,
            "expected": P835_SCORER_PATH,
            "note": "no DeepFilterNet environment or official DNS-Challenge checkout exists.",
        },
        "dnsmos_c_checkpoint_presence": {
            "present": False,
            "expected": DNSC_CHECKPOINT,
            "note": "no NISQA checkpoint or DNSMOS-C checkout exists.",
        },
        "runtime_presence": {
            "present": False,
            "note": (
                "onnxruntime is importable in neither the default python3 "
                "(3.11.5) nor the pinned 3.12.16 interpreter; no torch/NISQA "
                "runtime is pinned."
            ),
        },
        "corpus_presence": {
            "present": False,
            "expected": [
                "data/runs/voice-enhancement-20261101-ears-preservation-743",
                "Krisp-AI/VoiceIsolation-Benchmark-Dataset-Processed",
            ],
            "note": "data/runs and downloaded vendor outputs are absent.",
        },
        "package_assets": {
            "present": False,
            "note": "no audio, ONNX, PyTorch or score bundle is written here.",
        },
        "crosscheck": {
            "incidental_onnx_observed": True,
            "incidental_onnx_path": (
                "research/voice-conversion-eval-20261101/repos/seed-vc/"
                "baselines/dnsmos"
            ),
            "admitted": False,
            "pinned_for_qualification": False,
            "reason": (
                "different P.808 / combined packaging without per-file terms, "
                "model card or verified revision"
            ),
        },
        "substitution": {
            "performed": False,
            "p808_used_for_p835": False,
            "combined_model_used_for_separate_models": False,
            "unrelated_checkpoint_used_for_dnsmos_c": False,
        },
        "conclusion": (
            "BLOCKED: exact P.835 weights, pinned scorer, DNSMOS-C/NISQA "
            "checkpoint and source revision, approved runtimes, rights-cleared "
            "cohorts and any scored result are absent; no substitute is "
            "admitted."
        ),
        "qualifies": False,
    }


def separation_from_siblings() -> Dict[str, Any]:
    return {
        "reused_source_fixtures_metrics_or_results": False,
        "packages": [
            {
                "package": "docs/task-evidence/aecmos",
                "boundary": (
                    "scenario-aware learned echo/degradation predictor on three "
                    "aligned streams, not blind single-stream DNSMOS"
                ),
                "reused": False,
            },
            {
                "package": "docs/task-evidence/quality-impairment-taxonomy",
                "boundary": (
                    "taxonomy and comparison map that assigns this task row; it "
                    "records documentation, not a scored bundle"
                ),
                "reused": False,
            },
            {
                "package": "docs/task-evidence/stoi-estoi",
                "boundary": (
                    "reference-based intelligibility proxy with clean targets; "
                    "not a no-reference MOS predictor"
                ),
                "reused": False,
            },
            {
                "package": "docs/task-evidence/srmr-and-reverb-metrics",
                "boundary": (
                    "reverberation/task-specific measures, not a general MOS "
                    "predictor"
                ),
                "reused": False,
            },
        ],
        "note": (
            "Sibling README/report files are pinned read-only for boundary "
            "clarity only. No sibling fixture, source, corpus, metric or result "
            "is imported, pooled, rescored or reused."
        ),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def build_report_core() -> Dict[str, Any]:
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
        "qualification": dict(QUALIFICATION),
        "task_row": dict(TASK_ROW_IDENTITY),
        "mutable_provenance": dict(MUTABLE_PROVENANCE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
        "scope": dict(SCOPE),
        "public_surface": dict(PUBLIC_SURFACE),
        "scorers": scorers(),
        "scorer_documentation_audit": scorer_documentation_audit(),
        "geometry_reference": geometry_reference(),
        "postprocessing_reference": postprocessing_reference(),
        "aggregation_reference": aggregation_reference(),
        "fixtures": fixture_payload(),
        "runs": runs(),
        "controls": controls(),
        "adverse_results": adverse_results(),
        "missing_results": missing_results(),
        "failure_controls": failure_controls(),
        "acceptance_profile": acceptance_profile(),
        "observed_provenance": observed_provenance(),
        "artifact_assessment": artifact_assessment(),
        "separation_from_siblings": separation_from_siblings(),
        "ranking": {
            "order": "not_ranked",
            "recommendation": None,
            "reason": (
                "no scored result exists for either scorer; no ranking or "
                "recommendation may be derived from geometry arithmetic"
            ),
            "qualifies": False,
        },
        "release_gates": [dict(gate) for gate in RELEASE_GATES],
        "non_claims": list(NON_CLAIMS),
        "reproduction": list(REPRODUCTION),
    }


def failure_controls() -> Dict[str, Any]:
    adverse = adverse_results()
    missing = missing_results()
    return {
        "all_explicit": True,
        "checks": {
            "every_rejection_observed": _check_all_rejected(adverse),
            "no_adverse_result_qualifies": all(
                row["qualifies"] is False for row in adverse
            ),
            "every_missing_result_blocked": all(
                row["status"] == "blocked" and row["scores"] is None
                and row["qualifies"] is False for row in missing
            ),
            "all_score_slots_null": all(
                value is None
                for scorer in scorers()
                for value in scorer["score_slots"].values()
            ),
            "artifact_absence_explicit":
                artifact_assessment()["all_required_absent"] is True,
            "no_substitution_admitted": (
                artifact_assessment()["crosscheck"]["admitted"] is False
                and artifact_assessment()["substitution"]["performed"] is False
            ),
            "runtime_absence_explicit":
                artifact_assessment()["runtime_presence"]["present"] is False,
            "public_surface_unchanged": all(
                value is False for value in PUBLIC_SURFACE.values()
            ),
        },
        "rejected_count": len(adverse),
        "blocked_count": len(missing),
        "qualifies": False,
    }


def build_report() -> Dict[str, Any]:
    return build_report_core()


def render_report() -> Tuple[bytes, str, str]:
    cores = [canonical_bytes(build_report_core()) for _ in range(3)]
    if len(set(cores)) != 1:
        raise ReferenceError("non_deterministic_report_core")
    core = build_report_core()
    core_digest = sha256_bytes(canonical_bytes(core))
    report = dict(core)
    report["regeneration"] = {
        "runs": 3,
        "byte_identical": True,
        "canonical_digests": [core_digest, core_digest, core_digest],
        "process": "three in-process builds, exact canonical bytes",
    }
    text, digest = canonical_report(report)
    return (text + "\n").encode("utf-8"), digest, core_digest


# ---------------------------------------------------------------------------
# Contract
# ---------------------------------------------------------------------------


def scorer_contract_summary() -> Dict[str, Any]:
    return {
        "scorers": ["dnsmos_p835", "dnsmos_c"],
        "dnsmos_p835": {
            "outputs": list(P835_OUTPUTS),
            "sample_rate_hz": P835_SAMPLE_RATE_HZ,
            "input_length_s": P835_INPUT_LENGTH_S,
            "window_samples": P835_WINDOW_SAMPLES,
            "hop_samples": P835_HOP_SAMPLES,
            "model_names": sorted(P835_MODELS),
            "model_digests": dict(sorted(P835_MODELS.items())),
            "scorer_sha256": P835_SCORER_SHA256,
            "score_status": "unavailable_weights_source_and_runtime_absent",
        },
        "dnsmos_c": {
            "outputs": list(DNSC_OUTPUTS),
            "sample_rate_hz": DNSC_SAMPLE_RATE_HZ,
            "segment_kinds": list(DNSC_SEGMENT_KINDS),
            "min_segment_ms": DNSC_MIN_SEGMENT_MS,
            "window_ms": DNSC_WINDOW_MS,
            "hop_ms": DNSC_HOP_MS,
            "checkpoint": DNSC_CHECKPOINT,
            "checkpoint_sha256": None,
            "source_revision": None,
            "score_status": "unavailable_checkpoint_source_and_runtime_absent",
        },
        "scores_reproduced": False,
        "scores_are_human_ratings": False,
        "predicted_scores_kept_separate_from_subjective_mos": True,
        "qualifies": False,
    }


def contract_payload(artifact_pins: Dict[str, str]) -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "qualification": dict(QUALIFICATION),
        "task_row": dict(TASK_ROW_IDENTITY),
        "mutable_provenance": dict(MUTABLE_PROVENANCE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
        "scope": dict(SCOPE),
        "public_surface": dict(PUBLIC_SURFACE),
        "scorer_contract_summary": scorer_contract_summary(),
        "required_artifacts": [dict(item) for item in REQUIRED_ARTIFACTS],
        "release_gates": [dict(gate) for gate in RELEASE_GATES],
        "artifact_pins": dict(sorted(artifact_pins.items())),
        "reproduction": list(REPRODUCTION),
        "non_claims": list(NON_CLAIMS),
    }
