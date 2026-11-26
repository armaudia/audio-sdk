# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local DEFER evidence for SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS.

Standard-library only and deterministic. This module never downloads, registers,
imports or executes a challenge runtime, dataset, baseline, scorer or model. It
pins the provenance that is present, proves that participant registration, the
licensed train/dev/test material, the organizer permitted multi-distortion
pairing list, the official baseline/scorer and a rights-cleared cohort are
absent, and reproduces only declared degradation arithmetic plus deterministic
schema controls. None of it is runtime or benchmark evidence and none of it can
qualify.

The pinned research note names the CCF AATC 2025 Speech Restoration Challenge as
the relevant next benchmark for learned unified restoration models and records
that its training/dev data requires participant registration. It records four
distinct inverse problems (declipping, bandwidth extension, codec-artifact
restoration and packet-loss concealment) whose missing information and decoder
context differ, and it explicitly says that no single universal restorer was
selected or evaluated. Nothing is fabricated or downloaded here.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

TASK = "SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS"
COMPONENT_ID = "ccf-aatc-unified-restoration-controls"
TASK_TITLE = "CCF AATC unified restoration controls"
CONTRACT_ID = "audio-sdk/ccf-aatc-unified-restoration-controls/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
MANIFEST_SCHEMA_ID = (
    "audio-sdk/ccf-aatc-unified-restoration-controls/qualification/0.1")
PROFILE = "evidence"
PROFILE_LABEL = "Evidence"
MODE = "research-control"
BASE_COMMIT = "d45e0f22883021412b4206c77df4e1d8cf89dbd5"
BRANCH = "swarm/SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS"
REVIEWER = "reviewer-CCF-AATC-UNIFIED-RESTORATION-CONTROLS"
TASK_PREFIX = "docs/task-evidence/ccf-aatc-unified-restoration-controls/"
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = (
    "id", "title", "repository", "mode", "depends_on", "component", "evidence")

RESEARCH_NOTE = "research/distortion_restoration_20261028.md"
BASELINE_IMPLEMENTATION = "src/audioml_eval/distortion_restoration.py"
BASELINE_REPORT = (
    "reports/distortion-restoration/20261028-synthetic-screen.json")

SOURCE_PINS: dict[str, str] = {
    RESEARCH_NOTE:
        "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    BASELINE_IMPLEMENTATION:
        "c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f",
    BASELINE_REPORT:
        "87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}

BOUNDARY_PINS: dict[str, str] = {
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
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
}

SIBLING_PINS: dict[str, str] = {
    "docs/task-evidence/survey-rst-01/report.json":
        "320a948f9c1bb9846295dbd1842db9c19d956588f02830549986b59f75bd76ec",
    "docs/task-evidence/survey-rst-02/report.json":
        "e9ae7bff5a2a5adccbc998ebfd12f23dac72b4461671cb530b63122b698c3a23",
    "docs/task-evidence/survey-rst-03/report.json":
        "8cbce9982b675de899989cf7b1c6bc14d4368c976d262f7b5d05990f3cd4c850",
    "docs/task-evidence/survey-rst-04/report.json":
        "da399d3192c14ce8471103464530cf3c684a28cde3c62249daeba7f163de6042",
    "docs/task-evidence/band-limited-pocs-declipping/report.json":
        "8d893e8055cdc2e982a4e568e7996b45d1b6dd73841ac2b701a15ec5160dc65b",
    "docs/task-evidence/linear-interpolation-declipping/report.json":
        "c3252fd080299e4b1804a9facf3fea02fe66f0df31728426476346f28d8dc310",
    "docs/task-evidence/zero-fill-plc/report.json":
        "3f23c4453caf289ab34ca61af6c94dacb5e9abe9b31fd71a6922ac305e7281ca",
    "docs/task-evidence/linear-interpolation-plc/report.json":
        "0a711aa398be0f86559249781f429323cee2eaf31ced1585f5d8fc205248b323",
    "docs/task-evidence/pitch-period-repeat-plc/report.json":
        "114f0107fc06176857157801f127a22e88639204b488cd2267bf80ee9b467445",
    "docs/task-evidence/autoregressive-plc/report.json":
        "4730ceb74e03782c90dcd78332443c2129cdf56af14ef29bcc89435b68007aec",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/report.json":
        "ec4c9ea5e46e02d9866920458b4d6365d300d8bcd626d2e05bf7f4c4955a080e",
    "docs/task-evidence/opus-deep-plc/report.json":
        "df8cb2dad636a6d1ded205b872297ddf43936c65dfc75febc5e6c5f4f0415df2",
    "docs/task-evidence/opus-dred/report.json":
        "2997dc6cc9e623a762379ca498c178c22a9607591a39ea8bcf6ef2691544a3f2",
    "docs/task-evidence/opus-1-5-lace/report.json":
        "9b98c595d812b724b523a5d748828452980946b9292a9d54c0ac9b804dabbf5b",
    "docs/task-evidence/opus-1-5-nolace/report.json":
        "9e09b14d9f55d0c2a2228f05982ab9ad3943460e742b3f959d6b4d1eea2336f6",
}

LOCAL_PIN_FILES = (
    "README.md",
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

PROFILE_PHRASES = (
    "scorer", "corpus and cohort", "aggregation", "failed items", "controls",
    "paired", "unpaired", "synthetic", "human", "source-reported",
    "invalid/missing", "representative valid result",
)

FAMILIES = ("RST-01", "RST-02", "RST-03", "RST-04")

FAMILY_SPECS: dict[str, dict[str, Any]] = {
    "RST-01": {
        "name": "declipping_saturation",
        "controlled_degradation":
            "hard clipping at 0.35 and 0.55 of normalized peak",
        "missing_information":
            "clipped peak samples and their lost sign/amplitude",
        "required_context": "clean reference plus clipping threshold or mask",
        "forbidden_substitution":
            "resampling, rate conversion or a limiter cannot recover clipped "
            "peaks",
        "local_baseline": "band-limited POCS (best tested local method)",
        "candidate_not_run":
            "constrained sparse declipper (SPADE/social sparsity) requiring "
            "MATLAB, LTFAT and CVX",
        "owned_task": "SDK-BAND-LIMITED-POCS-DECLIPPING",
    },
    "RST-02": {
        "name": "bandwidth_extension",
        "controlled_degradation": "zero-phase low-pass at 3.5 kHz",
        "missing_information":
            "high-frequency band above the 3.5 kHz cutoff",
        "required_context": "full-band clean reference",
        "forbidden_substitution":
            "resampling or rate conversion does not infer missing high "
            "frequencies",
        "local_baseline":
            "band-limited input; spectrum-copy extension was rejected",
        "candidate_not_run":
            "NU-Wave 2 official code/checkpoints are not staged locally",
        "owned_task": "SDK-NU-WAVE-2",
    },
    "RST-03": {
        "name": "codec_artifact_restoration",
        "controlled_degradation":
            "8-bit mu-law at 8 kHz and a 4-bit mu-law stress proxy",
        "missing_information":
            "codec-distorted detail and codec-specific decoder state",
        "required_context":
            "pre-companding narrowband reference and exact codec identity",
        "forbidden_substitution":
            "a generic PCM postfilter cannot claim codec-integrated "
            "restoration",
        "local_baseline":
            "decoded input; low-pass decoder postfilter harmed 8-bit fidelity",
        "candidate_not_run":
            "Opus 1.5 LACE/NoLACE require a compatible Opus build and "
            "packet-level integration",
        "owned_task": "SDK-OPUS-1-5-LACE",
    },
    "RST-04": {
        "name": "packet_loss_concealment",
        "controlled_degradation":
            "isolated 10% packet loss and 17% burst loss",
        "missing_information":
            "erased packets, decoder state or transmitted redundancy",
        "required_context":
            "loss mask plus decoder state or redundant packet information",
        "forbidden_substitution":
            "waveform-only inpainting cannot substitute for codec-integrated "
            "PLC or DRED",
        "local_baseline":
            "zero fill, linear interpolation, pitch-period repetition and AR "
            "prediction (metric-dependent ranking)",
        "candidate_not_run":
            "Opus deep PLC and DRED require integration and extra "
            "bitrate/latency review",
        "owned_task": "SDK-OPUS-DEEP-PLC",
    },
}

PAIR_IDS = tuple(
    f"{first}+{second}"
    for index, first in enumerate(FAMILIES)
    for second in FAMILIES[index + 1:])

INPUT_KINDS = (
    "waveform", "clean_reference", "clipping_mask", "codec_state",
    "decoder_bits", "packet_mask", "transmitted_redundancy",
)

SYNTHETIC_CLASS = "synthetic_contract_control_not_evidence"
METRICS = ("rmse", "si_sdr_db", "stoi")
CONTROL_KINDS = (
    "identity", "single_distortion", "paired_reference", "missing_case",
    "invalid_case",
)
DEVICE_OSES = ("macos", "linux", "windows", "android", "ios")
DEVICE_ARCHES = ("arm64", "x86_64")

CLAIM_FIELDS = (
    "family", "method", "claim", "uses_decoder_context", "input_kinds")
MANIFEST_FIELDS = (
    "schema_id", "run_id", "registration", "dataset", "pairing", "baseline",
    "strata", "controls", "rights", "device")
REGISTRATION_FIELDS = (
    "participant_id", "registered", "acceptance_sha256", "agreement_sha256")
DATASET_FIELDS = (
    "train_sha256", "dev_sha256", "test_sha256", "license_id",
    "license_sha256", "total_items", "sample_rate_hz")
PAIRING_FIELDS = ("list_sha256", "organizer_verified", "pairs")
BASELINE_FIELDS = (
    "package_sha256", "scorer_sha256", "submission_schema_sha256")
STRATUM_FIELDS = ("family", "pair", "items", "clean_reference_sha256")
MANIFEST_CONTROL_FIELDS = ("id", "kind", "passes")
RIGHTS_FIELDS = (
    "consent_recorded", "output_use_defined", "redistribution_approved",
    "listening_protocol_approved", "held_out_speaker_split")
DEVICE_FIELDS = ("os", "arch", "pinned")
AGG_ROW_FIELDS = ("family", "pair", "item_id", "metric", "value")

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
PAIR_PART = re.compile(r"^RST-[0-9]{2}$")
VALUE_TEXT = re.compile(r"^-?[0-9]+(?:/[1-9][0-9]*)?$")

FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".gguf", ".lib", ".m4a",
    ".mdl", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o", ".onnx", ".opus",
    ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wav", ".wasm", ".weights",
}

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(
    os.environ.get("AUDIOML_ROOT", str(WORKTREE.parents[2]))).resolve()

CHALLENGE_PROBES = (
    "adapters/ccf-aatc",
    "adapters/ccf-aatc-unified-restoration-controls",
    "data/ccf-aatc",
    "data/ccf-aatc-2025",
    "data/checkouts/ccf-aatc-2025",
    "data/datasets/ccf-aatc-2025",
    "data/restoration/ccf-aatc-2025",
    "data/restoration/ccf-aatc-2025/train",
    "data/restoration/ccf-aatc-2025/dev",
    "data/restoration/ccf-aatc-2025/test",
    "docs/ccf-aatc",
    "third_party/ccf-aatc",
    "tools/ccf-aatc",
    "vendor/ccf-aatc",
)

LINKED_ROWS: tuple[dict[str, Any], ...] = (
    {"task": "SDK-SURVEY-RST-01",
     "role": "merged declipping/saturation evidence map; per-task survey, "
             "not a unified restorer or challenge baseline",
     "report_sha256":
         "320a948f9c1bb9846295dbd1842db9c19d956588f02830549986b59f75bd76ec"},
    {"task": "SDK-SURVEY-RST-02",
     "role": "merged bandwidth-extension evidence map; per-task survey, "
             "not a unified restorer or challenge baseline",
     "report_sha256":
         "e9ae7bff5a2a5adccbc998ebfd12f23dac72b4461671cb530b63122b698c3a23"},
    {"task": "SDK-SURVEY-RST-03",
     "role": "merged codec-artifact evidence map; per-task survey, not a "
             "unified restorer or challenge baseline",
     "report_sha256":
         "8cbce9982b675de899989cf7b1c6bc14d4368c976d262f7b5d05990f3cd4c850"},
    {"task": "SDK-SURVEY-RST-04",
     "role": "merged packet-loss evidence map; per-task survey, not a "
             "unified restorer or challenge baseline",
     "report_sha256":
         "da399d3192c14ce8471103464530cf3c684a28cde3c62249daeba7f163de6042"},
    {"task": "SDK-BAND-LIMITED-POCS-DECLIPPING",
     "role": "merged RST-01 synthetic declipping reference; one family only",
     "report_sha256":
         "8d893e8055cdc2e982a4e568e7996b45d1b6dd73841ac2b701a15ec5160dc65b"},
    {"task": "SDK-LINEAR-INTERPOLATION-DECLIPPING",
     "role": "merged RST-01 control; one family only",
     "report_sha256":
         "c3252fd080299e4b1804a9facf3fea02fe66f0df31728426476346f28d8dc310"},
    {"task": "SDK-ZERO-FILL-PLC",
     "role": "merged RST-04 zero-fill control; one family only",
     "report_sha256":
         "3f23c4453caf289ab34ca61af6c94dacb5e9abe9b31fd71a6922ac305e7281ca"},
    {"task": "SDK-LINEAR-INTERPOLATION-PLC",
     "role": "merged RST-04 linear-interpolation control; one family only",
     "report_sha256":
         "0a711aa398be0f86559249781f429323cee2eaf31ced1585f5d8fc205248b323"},
    {"task": "SDK-PITCH-PERIOD-REPEAT-PLC",
     "role": "merged RST-04 pitch-repeat control; one family only",
     "report_sha256":
         "114f0107fc06176857157801f127a22e88639204b488cd2267bf80ee9b467445"},
    {"task": "SDK-AUTOREGRESSIVE-PLC",
     "role": "merged RST-04 AR-prediction control; one family only",
     "report_sha256":
         "4730ceb74e03782c90dcd78332443c2129cdf56af14ef29bcc89435b68007aec"},
    {"task": "SDK-OPUS-1-4-STANDARD-DECODER-PLC",
     "role": "merged standard Opus 1.4 decoder PLC; codec-bound RST-04 "
             "control, not the challenge baseline",
     "report_sha256":
         "ec4c9ea5e46e02d9866920458b4d6365d300d8bcd626d2e05bf7f4c4955a080e"},
    {"task": "SDK-OPUS-DEEP-PLC",
     "role": "merged Opus deep-PLC blocker; no qualified RST-04 result",
     "report_sha256":
         "df8cb2dad636a6d1ded205b872297ddf43936c65dfc75febc5e6c5f4f0415df2"},
    {"task": "SDK-OPUS-DRED",
     "role": "merged Opus DRED blocker; no qualified RST-04 result",
     "report_sha256":
         "2997dc6cc9e623a762379ca498c178c22a9607591a39ea8bcf6ef2691544a3f2"},
    {"task": "SDK-OPUS-1-5-LACE",
     "role": "merged LACE blocker; no codec-integrated RST-03 result",
     "report_sha256":
         "9b98c595d812b724b523a5d748828452980946b9292a9d54c0ac9b804dabbf5b"},
    {"task": "SDK-OPUS-1-5-NOLACE",
     "role": "merged NoLACE blocker; no codec-integrated RST-03 result",
     "report_sha256":
         "9e09b14d9f55d0c2a2228f05982ab9ad3943460e742b3f959d6b4d1eea2336f6"},
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False) + "\n").encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _no_floats(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("non_integer_number")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("non_string_key")
            _no_floats(item)
    elif isinstance(value, list):
        for item in value:
            _no_floats(item)


def read_strict_json(path: Path) -> Any:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def reject_float(_text: str) -> Any:
        raise ValueError("non_integer_number")

    def reject_constant(text: str) -> Any:
        raise ValueError("nonfinite_constant:" + text)

    text = path.read_text(encoding="utf-8")
    value = json.loads(text, object_pairs_hook=no_duplicates,
                       parse_float=reject_float,
                       parse_constant=reject_constant)
    _no_floats(value)
    return value


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_int(value: Any, code: str) -> int:
    if not _is_int(value):
        raise ValueError(code)
    return value


def _reject_nonfinite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite_value")
    if isinstance(value, dict):
        for item in value.values():
            _reject_nonfinite(item)
    elif isinstance(value, list):
        for item in value:
            _reject_nonfinite(item)


def _require_exact_keys(value: Any, fields: tuple[str, ...]) -> None:
    if not isinstance(value, dict):
        raise ValueError("invalid_type")
    if set(value) - set(fields):
        raise ValueError("unknown_field")
    for field in fields:
        if field not in value:
            raise ValueError("missing_field")


def _require_slug(value: Any, code: str) -> str:
    if not isinstance(value, str) or not SLUG.match(value):
        raise ValueError(code)
    return value


def _require_digest(value: Any) -> str:
    if not isinstance(value, str) or not HEX64.match(value):
        raise ValueError("invalid_digest")
    return value


def _require_bool(value: Any, code: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(code)
    return value


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def parse_fraction(value: Any, code: str) -> Fraction:
    if not isinstance(value, str) or not VALUE_TEXT.match(value):
        raise ValueError(code)
    return Fraction(value)


def canonicalize_pair(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("invalid_type")
    if not value:
        raise ValueError("invalid_pair")
    parts = value.split("+")
    if len(parts) not in (1, 2):
        raise ValueError("invalid_pair")
    for part in parts:
        if not PAIR_PART.match(part):
            raise ValueError("invalid_pair")
    for part in parts:
        if part not in FAMILIES:
            raise ValueError("unknown_family")
    if len(parts) == 2 and parts[0] == parts[1]:
        raise ValueError("invalid_pair")
    return "+".join(sorted(parts))


def _require_canonical_pair(value: Any) -> str:
    canonical = canonicalize_pair(value)
    if value != canonical:
        raise ValueError("pair_not_canonical")
    return canonical


def classify_claim(claim: Any) -> dict[str, Any]:
    if not isinstance(claim, dict):
        raise ValueError("invalid_type")
    _reject_nonfinite(claim)
    _require_exact_keys(claim, CLAIM_FIELDS)
    family = claim["family"]
    if not isinstance(family, str):
        raise ValueError("invalid_type")
    if family == "ALL":
        raise ValueError("unified_claim_requires_strata")
    if family not in FAMILIES:
        raise ValueError("unknown_family")
    method = _require_slug(claim["method"], "invalid_method")
    text = claim["claim"]
    if not isinstance(text, str) or not text.strip():
        raise ValueError("invalid_claim")
    uses_decoder_context = _require_bool(
        claim["uses_decoder_context"], "invalid_type")
    inputs = claim["input_kinds"]
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("missing_input_kind")
    for item in inputs:
        if not isinstance(item, str):
            raise ValueError("invalid_type")
        if item not in INPUT_KINDS:
            raise ValueError("unknown_input_kind")
    lowered = text.lower()
    if family == "RST-01" and any(
            token in method for token in
            ("limiter", "resampler", "resample", "rate_conversion")):
        raise ValueError("cross_family_substitution")
    if family == "RST-02" and method in {
            "resampler", "libsamplerate", "varispeed", "rate_conversion",
            "linear_resampler"}:
        raise ValueError("cross_family_substitution")
    if family == "RST-01" and "bandwidth extension" in lowered:
        raise ValueError("cross_family_claim")
    if family == "RST-02" and (
            "declip" in lowered or "clipping" in lowered):
        raise ValueError("cross_family_claim")
    if family in ("RST-03", "RST-04") and \
            "codec-integrated" in lowered and not uses_decoder_context:
        raise ValueError("decoder_context_required")
    if family == "RST-04" and "lossless" in lowered:
        raise ValueError("unsupported_lossless_claim")
    return {
        "family": family,
        "method": method,
        "uses_decoder_context": uses_decoder_context,
        "input_kinds": list(inputs),
        "accepted": True,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def _run_control(
        cases: list[dict[str, Any]], case_id: str,
        action: Callable[[], Any], expected: str | None) -> None:
    observed = None
    status = "accepted"
    try:
        action()
    except ValueError as error:
        observed = str(error)
        status = "rejected"
    cases.append({
        "id": case_id,
        "expected_code": expected,
        "observed_code": observed,
        "status": status,
        "qualifies": False,
    })


def family_control() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    def claim(family: str, method: str, text: str, uses: bool,
              inputs: list[str]) -> dict[str, Any]:
        return {
            "family": family,
            "method": method,
            "claim": text,
            "uses_decoder_context": uses,
            "input_kinds": inputs,
        }

    rows: tuple[tuple[str, dict[str, Any], str | None], ...] = (
        ("C01", claim(
            "RST-01", "band_limited_pocs",
            "recovers clipped samples from waveform and mask", False,
            ["waveform", "clipping_mask"]), None),
        ("C02", claim(
            "RST-02", "nuwave2",
            "generates an estimated high band", False, ["waveform"]), None),
        ("C03", claim(
            "RST-03", "lace",
            "uses decoder state for codec-integrated restoration", True,
            ["waveform", "codec_state", "decoder_bits"]), None),
        ("C04", claim(
            "RST-04", "opus_dred",
            "uses transmitted redundancy for burst loss", True,
            ["waveform", "transmitted_redundancy"]), None),
        ("C05", claim(
            "RST-01", "limiter",
            "recovers clipped peaks", False, ["waveform"]),
         "cross_family_substitution"),
        ("C06", claim(
            "RST-02", "resampler",
            "recovers missing high frequencies", False, ["waveform"]),
         "cross_family_substitution"),
        ("C07", claim(
            "RST-03", "generic_postfilter",
            "codec-integrated restoration", False, ["waveform"]),
         "decoder_context_required"),
        ("C08", claim(
            "RST-04", "zero_fill",
            "codec-integrated packet recovery", False, ["waveform"]),
         "decoder_context_required"),
        ("C09", claim(
            "RST-01", "band_limited_pocs",
            "bandwidth extension from clipped input", False,
            ["waveform", "clipping_mask"]), "cross_family_claim"),
        ("C10", claim(
            "RST-09", "unknown", "unknown family", False, ["waveform"]),
         "unknown_family"),
        ("C11", claim(
            "ALL", "universal_model", "single unified score", False,
            ["waveform"]), "unified_claim_requires_strata"),
        ("C12", claim(
            "RST-01", "band_limited_pocs", "missing input kinds", False,
            []), "missing_input_kind"),
        ("C13", claim(
            "RST-01", "band_limited_pocs", "bad bool", "yes",
            ["waveform"]), "invalid_type"),
        ("C14", claim(
            "RST-01", "band_limited_pocs", "", False, ["waveform"]),
         "invalid_claim"),
        ("C15", claim(
            "RST-01", "Band Limited", "bad method", False, ["waveform"]),
         "invalid_method"),
        ("C16", claim(
            "RST-01", "band_limited_pocs", "extra", False, ["waveform"]),
         "unknown_field"),
        ("C17", claim(
            "RST-02", "nuwave2", "unknown input", False, ["oracle"]),
         "unknown_input_kind"),
        ("C18", claim(
            "RST-04", "opus_dred", "lossless recovery", True,
            ["waveform", "transmitted_redundancy"]),
         "unsupported_lossless_claim"),
    )
    for case_id, payload, expected in rows:
        if case_id == "C16":
            payload = dict(payload)
            payload["extra"] = True
        _run_control(cases, case_id, lambda item=payload: classify_claim(item),
                     expected)
    summary = {
        "case_count": len(cases),
        "accepted_count": sum(
            1 for case in cases if case["status"] == "accepted"),
        "rejected_count": sum(
            1 for case in cases if case["status"] == "rejected"),
        "all_codes_match": all(
            case["observed_code"] == case["expected_code"]
            for case in cases),
        "families": list(FAMILIES),
        "qualifying_results": 0,
        "unified_score_claimed": False,
        "audio_read": False,
        "challenge_data_read": False,
        "network_used": False,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }
    return {
        "summary": summary,
        "cases": cases,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def clip_degradation(threshold: Any) -> dict[str, Any]:
    if not isinstance(threshold, str):
        raise ValueError("invalid_type")
    fraction = parse_fraction(threshold, "invalid_threshold")
    if not (0 < fraction < 1):
        raise ValueError("threshold_out_of_range")
    return {
        "kind": "hard_clip",
        "threshold": _fraction_text(fraction),
        "normalized_peak": 1,
        "open_unit_interval": True,
        "qualifies": False,
    }


def bwe_degradation(cutoff_hz: Any, sample_rate_hz: Any) -> dict[str, Any]:
    cutoff = _require_int(cutoff_hz, "invalid_cutoff")
    rate = _require_int(sample_rate_hz, "invalid_sample_rate")
    if cutoff <= 0:
        raise ValueError("invalid_cutoff")
    if rate <= 0:
        raise ValueError("invalid_sample_rate")
    if cutoff * 2 >= rate:
        raise ValueError("cutoff_not_below_nyquist")
    return {
        "kind": "zero_phase_low_pass",
        "cutoff_hz": cutoff,
        "sample_rate_hz": rate,
        "cutoff_fraction": _fraction_text(Fraction(cutoff, rate)),
        "below_nyquist": True,
        "qualifies": False,
    }


def codec_degradation(bits: Any, sample_rate_hz: Any) -> dict[str, Any]:
    bit_depth = _require_int(bits, "invalid_type")
    if bit_depth < 1 or bit_depth > 16:
        raise ValueError("bit_depth_out_of_range")
    rate = _require_int(sample_rate_hz, "invalid_sample_rate")
    if rate <= 0:
        raise ValueError("invalid_sample_rate")
    return {
        "kind": "mu_law_quantization",
        "bits": bit_depth,
        "levels": 2 ** bit_depth,
        "sample_rate_hz": rate,
        "stress_proxy": bit_depth == 4,
        "qualifies": False,
    }


def plc_degradation(loss_rate: Any) -> dict[str, Any]:
    fraction = parse_fraction(loss_rate, "invalid_loss_rate")
    if not (0 < fraction < 1):
        raise ValueError("loss_rate_out_of_range")
    return {
        "kind": "packet_loss_mask",
        "loss_rate": _fraction_text(fraction),
        "mask_known": True,
        "qualifies": False,
    }


def degradation_control() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    rows: tuple[tuple[str, Callable[[], Any], str | None], ...] = (
        ("D01", lambda: clip_degradation("7/20"), None),
        ("D02", lambda: clip_degradation("11/20"), None),
        ("D03", lambda: bwe_degradation(3500, 16000), None),
        ("D04", lambda: codec_degradation(8, 8000), None),
        ("D05", lambda: codec_degradation(4, 8000), None),
        ("D06", lambda: plc_degradation("1/10"), None),
        ("D07", lambda: plc_degradation("17/100"), None),
        ("D08", lambda: clip_degradation("0/1"), "threshold_out_of_range"),
        ("D09", lambda: clip_degradation("1/1"), "threshold_out_of_range"),
        ("D10", lambda: codec_degradation(0, 8000),
         "bit_depth_out_of_range"),
        ("D11", lambda: bwe_degradation(8000, 16000),
         "cutoff_not_below_nyquist"),
        ("D12", lambda: plc_degradation("3/2"), "loss_rate_out_of_range"),
        ("D13", lambda: bwe_degradation(float("inf"), 16000),
         "invalid_cutoff"),
        ("D14", lambda: codec_degradation(True, 8000), "invalid_type"),
    )
    for case_id, action, expected in rows:
        _run_control(cases, case_id, action, expected)
    low = clip_degradation("7/20")
    high = clip_degradation("11/20")
    bwe = bwe_degradation(3500, 16000)
    codec8 = codec_degradation(8, 8000)
    codec4 = codec_degradation(4, 8000)
    isolated = plc_degradation("1/10")
    burst = plc_degradation("17/100")
    summary = {
        "case_count": len(cases),
        "accepted_count": sum(
            1 for case in cases if case["status"] == "accepted"),
        "rejected_count": sum(
            1 for case in cases if case["status"] == "rejected"),
        "all_codes_match": all(
            case["observed_code"] == case["expected_code"]
            for case in cases),
        "clip_thresholds": [low["threshold"], high["threshold"]],
        "bwe_cutoff_fraction": bwe["cutoff_fraction"],
        "codec_levels": [codec8["levels"], codec4["levels"]],
        "loss_rates": [isolated["loss_rate"], burst["loss_rate"]],
        "audio_read": False,
        "audio_rendered": False,
        "challenge_data_read": False,
        "network_used": False,
        "qualifying_results": 0,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }
    return {
        "summary": summary,
        "cases": cases,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def pair_control() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    def entry(index: int, value: str) -> dict[str, Any]:
        canonical = canonicalize_pair(value)
        return {
            "id": f"PAIR-{index:02d}",
            "pair": canonical,
            "families": canonical.split("+"),
            "multi_distortion": "+" in canonical,
            "organizer_verified": False,
            "permitted_for_qualification": False,
            "qualifies": False,
            "evidence_class": SYNTHETIC_CLASS,
        }

    table = [entry(index, pair) for index, pair in enumerate(PAIR_IDS, start=1)]
    singles = [entry(index, family) for index, family in
               enumerate(FAMILIES, start=len(table) + 1)]
    canonical_case = canonicalize_pair("RST-02+RST-01")
    cases.append({
        "id": "P01",
        "input": "RST-02+RST-01",
        "canonical": canonical_case,
        "status": "accepted",
        "expected_code": None,
        "observed_code": None,
        "qualifies": False,
    })
    _run_control(cases, "P02", lambda: canonicalize_pair("RST-01+RST-01"),
                 "invalid_pair")
    _run_control(cases, "P03",
                 lambda: canonicalize_pair("RST-01+RST-02+RST-03"),
                 "invalid_pair")
    _run_control(cases, "P04", lambda: canonicalize_pair("RST-09"),
                 "unknown_family")
    _run_control(cases, "P05", lambda: canonicalize_pair(""), "invalid_pair")
    _run_control(cases, "P06", lambda: canonicalize_pair("rst-01"),
                 "invalid_pair")
    _run_control(cases, "P07", lambda: canonicalize_pair(1), "invalid_type")
    _run_control(cases, "P08", lambda: _check_pair_table(table, singles), None)
    _run_control(cases, "P09",
                 lambda: _require_pair_in_table("RST-03+RST-04", table), None)
    _run_control(cases, "P10", lambda: _require_single_in_table("RST-02",
                                                                singles), None)
    summary = {
        "case_count": len(cases),
        "accepted_count": sum(
            1 for case in cases if case["status"] == "accepted"),
        "rejected_count": sum(
            1 for case in cases if case["status"] == "rejected"),
        "all_codes_match": all(
            case["observed_code"] == case["expected_code"]
            for case in cases),
        "pair_count": len(table),
        "single_count": len(singles),
        "organizer_permitted_count": 0,
        "permitted_for_qualification": False,
        "canonical_order_invariant": canonical_case == "RST-01+RST-02",
        "qualifying_results": 0,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }
    return {
        "summary": summary,
        "cases": cases,
        "pairs": table,
        "singles": singles,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def _check_pair_table(table: list[dict[str, Any]],
                      singles: list[dict[str, Any]]) -> None:
    if len(table) != len(PAIR_IDS) or len(singles) != len(FAMILIES):
        raise ValueError("pair_table_size")
    seen: set[str] = set()
    for row in table:
        pair = row["pair"]
        if canonicalize_pair(pair) != pair or "+" not in pair:
            raise ValueError("pair_table_invalid")
        if pair in seen:
            raise ValueError("pair_table_duplicate")
        seen.add(pair)
        if row["permitted_for_qualification"] is not False:
            raise ValueError("pair_table_permitted")
    if seen != set(PAIR_IDS):
        raise ValueError("pair_table_incomplete")


def _require_pair_in_table(pair: str,
                           table: list[dict[str, Any]]) -> dict[str, Any]:
    for row in table:
        if row["pair"] == pair:
            if row["permitted_for_qualification"] is not False:
                raise ValueError("pair_permitted")
            return row
    raise ValueError("pair_not_in_table")


def _require_single_in_table(family: str,
                             singles: list[dict[str, Any]]) -> dict[str, Any]:
    for row in singles:
        if row["pair"] == family:
            return row
    raise ValueError("single_not_in_table")


def _aggregate_rows(rows: Any) -> dict[str, Any]:
    if not isinstance(rows, list):
        raise ValueError("invalid_type")
    _reject_nonfinite(rows)
    if not rows:
        raise ValueError("aggregation_empty")
    buckets: dict[str, dict[str, list[Fraction]]] = {
        family: {metric: [] for metric in METRICS} for family in FAMILIES}
    seen: set[tuple[str, str, str]] = set()
    pair_mode = "single_distortion_control_only"
    for row in rows:
        _require_exact_keys(row, AGG_ROW_FIELDS)
        family = row["family"]
        if not isinstance(family, str):
            raise ValueError("invalid_type")
        if family not in FAMILIES:
            raise ValueError("unknown_family")
        pair = _require_canonical_pair(row["pair"])
        if family not in pair.split("+"):
            raise ValueError("pair_family_mismatch")
        if "+" in pair:
            pair_mode = "multi_distortion_pair_unverified"
        metric = row["metric"]
        if not isinstance(metric, str):
            raise ValueError("invalid_type")
        if metric not in METRICS:
            raise ValueError("unknown_metric")
        item_id = _require_slug(row["item_id"], "invalid_item_id")
        value = row["value"]
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError("nonfinite_value")
            raise ValueError("invalid_type")
        fraction = parse_fraction(value, "invalid_value")
        key = (family, item_id, metric)
        if key in seen:
            raise ValueError("duplicate_row")
        seen.add(key)
        buckets[family][metric].append(fraction)
    present = [family for family in FAMILIES
               if any(buckets[family][metric] for metric in METRICS)]
    if set(present) != set(FAMILIES):
        raise ValueError("strata_incomplete")
    for family in FAMILIES:
        if any(not buckets[family][metric] for metric in METRICS):
            raise ValueError("metric_incomplete")
    strata: list[dict[str, Any]] = []
    for family in FAMILIES:
        metrics: dict[str, str] = {}
        row_count = 0
        for metric in METRICS:
            values = buckets[family][metric]
            total = sum(values, Fraction(0))
            metrics[metric] = _fraction_text(total / len(values))
            row_count += len(values)
        strata.append({
            "family": family,
            "metrics": metrics,
            "row_count": row_count,
            "qualifies": False,
        })
    return {
        "strata": strata,
        "strata_complete": True,
        "pair_mode": pair_mode,
        "unified": {
            "status": "forbidden",
            "value": None,
            "reason": "organizer_pairing_list_absent",
            "qualifies": False,
        },
        "qualifying_results": 0,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def _aggregation_rows() -> list[dict[str, Any]]:
    values = {
        "RST-01": {"si_sdr_db": ("15/1", "16/1"), "rmse": ("1/10", "2/10"),
                   "stoi": ("9/10", "91/100")},
        "RST-02": {"si_sdr_db": ("17/1", "18/1"), "rmse": ("2/10", "3/10"),
                   "stoi": ("88/100", "89/100")},
        "RST-03": {"si_sdr_db": ("37/1", "39/1"), "rmse": ("1/100", "2/100"),
                   "stoi": ("98/100", "99/100")},
        "RST-04": {"si_sdr_db": ("10/1", "11/1"), "rmse": ("11/100", "12/100"),
                   "stoi": ("9/10", "92/100")},
    }
    rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        for item_index in (1, 2):
            for metric in METRICS:
                rows.append({
                    "family": family,
                    "pair": family,
                    "item_id": f"item-{item_index:02d}",
                    "metric": metric,
                    "value": values[family][metric][item_index - 1],
                })
    return rows


def aggregation_control() -> dict[str, Any]:
    base = _aggregation_rows()
    cases: list[dict[str, Any]] = []

    def mutate(mutator: Callable[[list[dict[str, Any]]], None]) -> Any:
        rows = deepcopy(base)
        mutator(rows)
        return _aggregate_rows(rows)

    _run_control(cases, "A01", lambda: _aggregate_rows(base), None)

    def drop_family(rows: list[dict[str, Any]]) -> None:
        rows[:] = [row for row in rows if row["family"] != "RST-04"]

    _run_control(cases, "A02", lambda: mutate(drop_family),
                 "strata_incomplete")

    def unknown_family(rows: list[dict[str, Any]]) -> None:
        rows[0]["family"] = "RST-09"

    _run_control(cases, "A03", lambda: mutate(unknown_family),
                 "unknown_family")

    def unknown_metric(rows: list[dict[str, Any]]) -> None:
        rows[0]["metric"] = "mos"

    _run_control(cases, "A04", lambda: mutate(unknown_metric),
                 "unknown_metric")

    def duplicate(rows: list[dict[str, Any]]) -> None:
        rows.append(deepcopy(rows[0]))

    _run_control(cases, "A05", lambda: mutate(duplicate), "duplicate_row")

    def zero_denominator(rows: list[dict[str, Any]]) -> None:
        rows[0]["value"] = "1/0"

    _run_control(cases, "A06", lambda: mutate(zero_denominator),
                 "invalid_value")

    def nan_text(rows: list[dict[str, Any]]) -> None:
        rows[0]["value"] = "nan"

    _run_control(cases, "A07", lambda: mutate(nan_text), "invalid_value")

    def infinite(rows: list[dict[str, Any]]) -> None:
        rows[0]["value"] = float("inf")

    _run_control(cases, "A08", lambda: mutate(infinite), "nonfinite_value")

    def multi_pair(rows: list[dict[str, Any]]) -> None:
        rows[0]["pair"] = "RST-01+RST-02"

    _run_control(cases, "A09", lambda: mutate(multi_pair), None)

    def pair_mismatch(rows: list[dict[str, Any]]) -> None:
        rows[0]["pair"] = "RST-02"

    _run_control(cases, "A10", lambda: mutate(pair_mismatch),
                 "pair_family_mismatch")

    _run_control(cases, "A11", lambda: _aggregate_rows([]),
                 "aggregation_empty")

    def bad_item(rows: list[dict[str, Any]]) -> None:
        rows[0]["item_id"] = "Item 01"

    _run_control(cases, "A12", lambda: mutate(bad_item), "invalid_item_id")
    summary = {
        "case_count": len(cases),
        "accepted_count": sum(
            1 for case in cases if case["status"] == "accepted"),
        "rejected_count": sum(
            1 for case in cases if case["status"] == "rejected"),
        "all_codes_match": all(
            case["observed_code"] == case["expected_code"]
            for case in cases),
        "stratum_count": len(FAMILIES),
        "metric_count": len(METRICS),
        "unified_score_forbidden": True,
        "qualifying_results": 0,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }
    return {
        "summary": summary,
        "cases": cases,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def _base_manifest() -> dict[str, Any]:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "run_id": "synthetic-schema-control",
        "registration": {
            "participant_id": "synthetic-participant",
            "registered": True,
            "acceptance_sha256": "0" * 64,
            "agreement_sha256": "0" * 64,
        },
        "dataset": {
            "train_sha256": "0" * 64,
            "dev_sha256": "0" * 64,
            "test_sha256": "0" * 64,
            "license_id": "synthetic-license-control",
            "license_sha256": "0" * 64,
            "total_items": 4,
            "sample_rate_hz": 16000,
        },
        "pairing": {
            "list_sha256": "0" * 64,
            "organizer_verified": True,
            "pairs": ["RST-01", "RST-02", "RST-03", "RST-04"],
        },
        "baseline": {
            "package_sha256": "0" * 64,
            "scorer_sha256": "0" * 64,
            "submission_schema_sha256": "0" * 64,
        },
        "strata": [
            {"family": "RST-01", "pair": "RST-01", "items": 1,
             "clean_reference_sha256": "0" * 64},
            {"family": "RST-02", "pair": "RST-02", "items": 1,
             "clean_reference_sha256": "0" * 64},
            {"family": "RST-03", "pair": "RST-03", "items": 1,
             "clean_reference_sha256": "0" * 64},
            {"family": "RST-04", "pair": "RST-04", "items": 1,
             "clean_reference_sha256": "0" * 64},
        ],
        "controls": [
            {"id": "identity", "kind": "identity", "passes": True},
            {"id": "missing-case", "kind": "missing_case", "passes": True},
            {"id": "invalid-case", "kind": "invalid_case", "passes": True},
        ],
        "rights": {
            "consent_recorded": True,
            "output_use_defined": True,
            "redistribution_approved": True,
            "listening_protocol_approved": True,
            "held_out_speaker_split": True,
        },
        "device": {
            "os": "macos",
            "arch": "arm64",
            "pinned": True,
        },
    }


def validate_manifest(manifest: Any) -> None:
    if not isinstance(manifest, dict):
        raise ValueError("invalid_type")
    _reject_nonfinite(manifest)
    _require_exact_keys(manifest, MANIFEST_FIELDS)
    if manifest["schema_id"] != MANIFEST_SCHEMA_ID:
        raise ValueError("schema_mismatch")
    _require_slug(manifest["run_id"], "invalid_run_id")

    registration = manifest["registration"]
    _require_exact_keys(registration, REGISTRATION_FIELDS)
    _require_slug(registration["participant_id"], "invalid_participant_id")
    if _require_bool(registration["registered"], "invalid_type") is not True:
        raise ValueError("not_registered")
    _require_digest(registration["acceptance_sha256"])
    _require_digest(registration["agreement_sha256"])

    dataset = manifest["dataset"]
    _require_exact_keys(dataset, DATASET_FIELDS)
    _require_digest(dataset["train_sha256"])
    _require_digest(dataset["dev_sha256"])
    _require_digest(dataset["test_sha256"])
    _require_slug(dataset["license_id"], "invalid_license_id")
    _require_digest(dataset["license_sha256"])
    total = _require_int(dataset["total_items"], "invalid_type")
    if total <= 0:
        raise ValueError("invalid_items")
    sample_rate = _require_int(dataset["sample_rate_hz"], "invalid_type")
    if sample_rate <= 0:
        raise ValueError("invalid_sample_rate")

    pairing = manifest["pairing"]
    _require_exact_keys(pairing, PAIRING_FIELDS)
    _require_digest(pairing["list_sha256"])
    if _require_bool(pairing["organizer_verified"], "invalid_type") is not True:
        raise ValueError("organizer_pairing_unverified")
    pairs = pairing["pairs"]
    if not isinstance(pairs, list):
        raise ValueError("invalid_type")
    if not pairs:
        raise ValueError("pairing_empty")
    seen_pairs: set[str] = set()
    for pair in pairs:
        canonical = _require_canonical_pair(pair)
        if canonical in seen_pairs:
            raise ValueError("duplicate_pair")
        seen_pairs.add(canonical)

    baseline = manifest["baseline"]
    _require_exact_keys(baseline, BASELINE_FIELDS)
    _require_digest(baseline["package_sha256"])
    _require_digest(baseline["scorer_sha256"])
    _require_digest(baseline["submission_schema_sha256"])

    strata = manifest["strata"]
    if not isinstance(strata, list):
        raise ValueError("invalid_type")
    if not strata:
        raise ValueError("strata_empty")
    seen_families: set[str] = set()
    for stratum in strata:
        _require_exact_keys(stratum, STRATUM_FIELDS)
        family = stratum["family"]
        if not isinstance(family, str):
            raise ValueError("invalid_type")
        if family not in FAMILIES:
            raise ValueError("unknown_family")
        pair = _require_canonical_pair(stratum["pair"])
        if family not in pair.split("+"):
            raise ValueError("pair_family_mismatch")
        items = _require_int(stratum["items"], "invalid_type")
        if items <= 0:
            raise ValueError("invalid_items")
        _require_digest(stratum["clean_reference_sha256"])
        if family in seen_families:
            raise ValueError("duplicate_stratum")
        seen_families.add(family)
    if seen_families != set(FAMILIES):
        raise ValueError("strata_incomplete")

    controls = manifest["controls"]
    if not isinstance(controls, list):
        raise ValueError("invalid_type")
    if not controls:
        raise ValueError("controls_empty")
    seen_controls: set[str] = set()
    for control in controls:
        _require_exact_keys(control, MANIFEST_CONTROL_FIELDS)
        control_id = _require_slug(control["id"], "invalid_control_id")
        if control["kind"] not in CONTROL_KINDS:
            raise ValueError("invalid_control_kind")
        _require_bool(control["passes"], "invalid_type")
        if control_id in seen_controls:
            raise ValueError("duplicate_control")
        seen_controls.add(control_id)

    rights = manifest["rights"]
    _require_exact_keys(rights, RIGHTS_FIELDS)
    for field in RIGHTS_FIELDS:
        if _require_bool(rights[field], "invalid_type") is not True:
            raise ValueError("rights_incomplete")

    device = manifest["device"]
    _require_exact_keys(device, DEVICE_FIELDS)
    if device["os"] not in DEVICE_OSES:
        raise ValueError("invalid_device_os")
    if device["arch"] not in DEVICE_ARCHES:
        raise ValueError("invalid_device_arch")
    if _require_bool(device["pinned"], "invalid_type") is not True:
        raise ValueError("device_unpinned")


def assess_manifest(manifest: Any) -> dict[str, Any]:
    validate_manifest(manifest)
    return {
        "schema_valid": True,
        "admitted": False,
        "qualifies": False,
        "challenge_artifact_present": False,
        "organizer_pairing_present": False,
        "official_baseline_present": False,
        "rights_cleared_cohort_present": False,
        "reasons": [
            "registration_acceptance_not_verified",
            "dataset_artifact_absent",
            "organizer_pairing_list_absent",
            "official_baseline_and_scorer_absent",
        ],
        "evidence_class": SYNTHETIC_CLASS,
    }


def mutations() -> list[tuple[str, Callable[[dict[str, Any]], None], str]]:
    def drop_top(manifest: dict[str, Any]) -> None:
        del manifest["rights"]

    def add_top(manifest: dict[str, Any]) -> None:
        manifest["extra"] = True

    def bad_schema(manifest: dict[str, Any]) -> None:
        manifest["schema_id"] = "audio-sdk/other/0.1"

    def bad_run_id(manifest: dict[str, Any]) -> None:
        manifest["run_id"] = "Bad Run"

    def not_registered(manifest: dict[str, Any]) -> None:
        manifest["registration"]["registered"] = False

    def bad_acceptance(manifest: dict[str, Any]) -> None:
        manifest["registration"]["acceptance_sha256"] = "zz"

    def bad_participant(manifest: dict[str, Any]) -> None:
        manifest["registration"]["participant_id"] = "Bad Participant"

    def zero_items(manifest: dict[str, Any]) -> None:
        manifest["dataset"]["total_items"] = 0

    def bool_items(manifest: dict[str, Any]) -> None:
        manifest["dataset"]["total_items"] = True

    def zero_rate(manifest: dict[str, Any]) -> None:
        manifest["dataset"]["sample_rate_hz"] = 0

    def short_digest(manifest: dict[str, Any]) -> None:
        manifest["dataset"]["train_sha256"] = "0" * 63

    def unverified_pairing(manifest: dict[str, Any]) -> None:
        manifest["pairing"]["organizer_verified"] = False

    def empty_pairs(manifest: dict[str, Any]) -> None:
        manifest["pairing"]["pairs"] = []

    def unknown_pair(manifest: dict[str, Any]) -> None:
        manifest["pairing"]["pairs"] = ["RST-09"]

    def noncanonical_pair(manifest: dict[str, Any]) -> None:
        manifest["pairing"]["pairs"] = ["RST-02+RST-01"]

    def self_pair(manifest: dict[str, Any]) -> None:
        manifest["pairing"]["pairs"] = ["RST-01+RST-01"]

    def duplicate_pair(manifest: dict[str, Any]) -> None:
        manifest["pairing"]["pairs"] = ["RST-01", "RST-01"]

    def bad_baseline(manifest: dict[str, Any]) -> None:
        manifest["baseline"]["package_sha256"] = "not-a-digest"

    def empty_strata(manifest: dict[str, Any]) -> None:
        manifest["strata"] = []

    def unknown_family(manifest: dict[str, Any]) -> None:
        manifest["strata"][0]["family"] = "RST-09"

    def pair_mismatch(manifest: dict[str, Any]) -> None:
        manifest["strata"][0]["pair"] = "RST-02"

    def duplicate_stratum(manifest: dict[str, Any]) -> None:
        manifest["strata"][1]["family"] = "RST-01"
        manifest["strata"][1]["pair"] = "RST-01"

    def incomplete_strata(manifest: dict[str, Any]) -> None:
        manifest["strata"].pop()

    def negative_items(manifest: dict[str, Any]) -> None:
        manifest["strata"][0]["items"] = -1

    def bad_reference(manifest: dict[str, Any]) -> None:
        manifest["strata"][0]["clean_reference_sha256"] = "0"

    def empty_controls(manifest: dict[str, Any]) -> None:
        manifest["controls"] = []

    def bad_control_kind(manifest: dict[str, Any]) -> None:
        manifest["controls"][0]["kind"] = "unknown"

    def duplicate_control(manifest: dict[str, Any]) -> None:
        manifest["controls"][1]["id"] = manifest["controls"][0]["id"]

    def bad_control_passes(manifest: dict[str, Any]) -> None:
        manifest["controls"][0]["passes"] = "yes"

    def rights_false(manifest: dict[str, Any]) -> None:
        manifest["rights"]["consent_recorded"] = False

    def rights_type(manifest: dict[str, Any]) -> None:
        manifest["rights"]["output_use_defined"] = "true"

    def bad_os(manifest: dict[str, Any]) -> None:
        manifest["device"]["os"] = "plan9"

    def bad_arch(manifest: dict[str, Any]) -> None:
        manifest["device"]["arch"] = "mips"

    def unpinned(manifest: dict[str, Any]) -> None:
        manifest["device"]["pinned"] = False

    def nested_extra(manifest: dict[str, Any]) -> None:
        manifest["registration"]["extra"] = True

    def pairs_type(manifest: dict[str, Any]) -> None:
        manifest["pairing"]["pairs"] = "RST-01"

    def nonfinite_items(manifest: dict[str, Any]) -> None:
        manifest["dataset"]["total_items"] = float("nan")

    return [
        ("M01", drop_top, "missing_field"),
        ("M02", add_top, "unknown_field"),
        ("M03", bad_schema, "schema_mismatch"),
        ("M04", bad_run_id, "invalid_run_id"),
        ("M05", not_registered, "not_registered"),
        ("M06", bad_acceptance, "invalid_digest"),
        ("M07", bad_participant, "invalid_participant_id"),
        ("M08", zero_items, "invalid_items"),
        ("M09", bool_items, "invalid_type"),
        ("M10", zero_rate, "invalid_sample_rate"),
        ("M11", short_digest, "invalid_digest"),
        ("M12", unverified_pairing, "organizer_pairing_unverified"),
        ("M13", empty_pairs, "pairing_empty"),
        ("M14", unknown_pair, "unknown_family"),
        ("M15", noncanonical_pair, "pair_not_canonical"),
        ("M16", self_pair, "invalid_pair"),
        ("M17", duplicate_pair, "duplicate_pair"),
        ("M18", bad_baseline, "invalid_digest"),
        ("M19", empty_strata, "strata_empty"),
        ("M20", unknown_family, "unknown_family"),
        ("M21", pair_mismatch, "pair_family_mismatch"),
        ("M22", duplicate_stratum, "duplicate_stratum"),
        ("M23", incomplete_strata, "strata_incomplete"),
        ("M24", negative_items, "invalid_items"),
        ("M25", bad_reference, "invalid_digest"),
        ("M26", empty_controls, "controls_empty"),
        ("M27", bad_control_kind, "invalid_control_kind"),
        ("M28", duplicate_control, "duplicate_control"),
        ("M29", bad_control_passes, "invalid_type"),
        ("M30", rights_false, "rights_incomplete"),
        ("M31", rights_type, "invalid_type"),
        ("M32", bad_os, "invalid_device_os"),
        ("M33", bad_arch, "invalid_device_arch"),
        ("M34", unpinned, "device_unpinned"),
        ("M35", nested_extra, "unknown_field"),
        ("M36", pairs_type, "invalid_type"),
        ("M37", nonfinite_items, "nonfinite_value"),
    ]


def admission_controls() -> dict[str, Any]:
    base = _base_manifest()
    control = assess_manifest(base)
    cases: list[dict[str, Any]] = []
    for case_id, mutator, expected in mutations():
        candidate = deepcopy(base)
        mutator(candidate)
        observed = None
        status = "accepted"
        try:
            validate_manifest(candidate)
        except ValueError as error:
            observed = str(error)
            status = "rejected"
        cases.append({
            "id": case_id,
            "expected_code": expected,
            "observed_code": observed,
            "status": status,
            "state_unchanged": True,
            "qualifies": False,
        })
    summary = {
        "case_count": len(cases),
        "accepted_schema_controls": 1,
        "rejected_count": sum(
            1 for case in cases if case["status"] == "rejected"),
        "all_codes_match": all(
            case["observed_code"] == case["expected_code"]
            for case in cases),
        "state_advanced_on_rejection": False,
        "vendor_sdk_loaded": False,
        "vendor_runtime_invoked": False,
        "challenge_data_read": False,
        "audio_read": False,
        "audio_rendered": False,
        "network_used": False,
        "qualifying_results": 0,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }
    return {
        "summary": summary,
        "control": control,
        "cases": cases,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def research_note_probe() -> dict[str, Any]:
    path = AUDIO_ROOT / RESEARCH_NOTE
    present = path.is_file()
    lines = path.read_text(encoding="utf-8").splitlines() if present else []
    text = "\n".join(lines)
    challenge_line = next(
        (index for index, line in enumerate(lines, start=1)
         if "CCF AATC 2025 Speech Restoration Challenge" in line), None)
    limits_line = next(
        (index for index, line in enumerate(lines, start=1)
         if line.startswith("The neural and codec-integrated candidates were "
                            "researched but not run")), None)
    boundary_line = next(
        (index for index, line in enumerate(lines, start=1)
         if line.startswith("The registry divides this area into four")), None)
    dataset_line = next(
        (index for index, line in enumerate(lines, start=1)
         if line.startswith("The workspace has a staged subset of EARS")), None)
    return {
        "path": RESEARCH_NOTE,
        "present": present,
        "sha256": sha256_file(path) if present else None,
        "line_count": len(lines),
        "challenge_line": challenge_line,
        "limits_line": limits_line,
        "task_boundary_line": boundary_line,
        "dataset_line": dataset_line,
        "records_registration_required": (
            "requires participant registration" in text),
        "records_dataset_larger_than_pilot": (
            "far larger than the local pilot" in text),
        "records_universal_next_benchmark": (
            "relevant next benchmark for learned unified models" in text),
        "records_no_single_universal_model": (
            "no single selected universal model" in text),
        "records_no_neural_checkpoint": (
            "No neural restoration checkpoint was evaluated" in text),
        "records_no_local_paired_set": (
            "no local paired set for all four distortion types" in text),
        "records_no_human_evaluation": (
            "No human evaluation was conducted" in text),
        "challenge_urls": [
            "https://arxiv.org/abs/2509.12974",
            "https://www.ccf.org.cn/Media_list/TC/2025-06-23/845853.shtml",
        ],
        "evidence_class": "source_reported_provenance_not_remeasured",
        "not_reproduced_here": True,
        "qualifies": False,
    }


def challenge_state() -> dict[str, Any]:
    return {
        "registration_attempted": False,
        "participant_account_present": False,
        "acceptance_record_present": False,
        "participant_agreement_present": False,
        "train_split_present": False,
        "dev_split_present": False,
        "test_split_present": False,
        "dataset_license_present": False,
        "organizer_pairing_list_present": False,
        "official_baseline_present": False,
        "official_scorer_present": False,
        "submission_package_present": False,
        "evidence_class": "project_workspace_probe",
        "qualifies": False,
    }


def classical_baseline_guard() -> dict[str, Any]:
    return {
        "implementation_path": BASELINE_IMPLEMENTATION,
        "report_path": BASELINE_REPORT,
        "present": (
            (AUDIO_ROOT / BASELINE_IMPLEMENTATION).is_file()
            and (AUDIO_ROOT / BASELINE_REPORT).is_file()),
        "is_unified_restorer": False,
        "is_ccf_aatc_baseline": False,
        "is_ccf_aatc_submission": False,
        "can_substitute": False,
        "covers_families": list(FAMILIES),
        "uses_synthetic_corruptions_only": True,
        "uses_registered_challenge_data": False,
        "reason": (
            "The local screens are four separate classical per-task pilots on "
            "deterministic EARS-derived corruptions. The note records no "
            "universal restorer, no neural checkpoint and no human evaluation. "
            "They cannot substitute for the registered challenge data, the "
            "organizer pairing list, the official baseline/scorer or a unified "
            "benchmark."),
        "qualifies": False,
    }


def source_presence() -> dict[str, Any]:
    probes = []
    for relative in CHALLENGE_PROBES:
        path = AUDIO_ROOT / relative
        probes.append({"path": relative, "exists": path.exists()})
    return {
        "probe_scope": "project workspace only; participant portals, registered "
                       "dataset stores and organizer repositories are out of "
                       "scope and were not contacted",
        "probes": probes,
        "present_probes": [row["path"] for row in probes if row["exists"]],
        "research_note_present": (AUDIO_ROOT / RESEARCH_NOTE).is_file(),
        "baseline_implementation_present":
            (AUDIO_ROOT / BASELINE_IMPLEMENTATION).is_file(),
        "baseline_report_present": (AUDIO_ROOT / BASELINE_REPORT).is_file(),
        "registration_acceptance_present": False,
        "participant_agreement_present": False,
        "challenge_dataset_present": False,
        "organizer_pairing_present": False,
        "official_baseline_present": False,
        "official_scorer_present": False,
        "rights_cleared_cohort_present": False,
        "exact_challenge_artifact_present": False,
        "presence_is_not_admission": True,
        "network_used": False,
        "download_attempted": False,
        "challenge_data_read": False,
        "audio_read": False,
        "audio_played": False,
        "qualifies": False,
    }


def license_findings() -> dict[str, Any]:
    return {
        "registration_required_recorded": True,
        "registration_acceptance_present": False,
        "participant_agreement_present": False,
        "dataset_license_present": False,
        "dataset_terms_reviewed": False,
        "train_dev_test_use_approved": False,
        "output_use_defined": False,
        "redistribution_approved": False,
        "commercial_use_approved": False,
        "benchmark_publication_approved": False,
        "listening_or_consent_present": False,
        "held_out_speaker_split_present": False,
        "qualifies": False,
    }


def documented_challenge_envelope() -> dict[str, Any]:
    return {
        "source": RESEARCH_NOTE + " §Literature and candidate selection",
        "challenge_named": True,
        "registration_required_recorded": True,
        "organizer_pairing_list_recorded": False,
        "permitted_pair_list_recorded": False,
        "pair_count_recorded": False,
        "dataset_identity_recorded": False,
        "dataset_checksums_recorded": False,
        "dataset_license_recorded": False,
        "registration_terms_recorded": False,
        "official_baseline_identity_recorded": False,
        "official_scorer_identity_recorded": False,
        "submission_format_recorded": False,
        "metric_weights_recorded": False,
        "numeric_bounds_recorded": False,
        "semantics_verified_here": False,
        "local_evaluation_recorded": False,
        "evidence_class": "source_reported_provenance_not_remeasured",
        "qualifies": False,
    }


def synthetic_pairing_envelope() -> dict[str, Any]:
    return {
        "purpose": (
            "Task-local schema constants used only to exercise pair "
            "canonicalization, deduplication and fail-closed admission. They "
            "are not organizer rules, not a permitted-pair decision and not "
            "evidence."),
        "families": list(FAMILIES),
        "single_distortion_controls": len(FAMILIES),
        "multi_distortion_pairs": len(PAIR_IDS),
        "pair_ids": list(PAIR_IDS),
        "organizer_permitted": 0,
        "permitted_for_qualification": False,
        "evidence_class": SYNTHETIC_CLASS,
        "qualifies": False,
    }


def _pin_map(pins: dict[str, str], root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for relative, expected in sorted(pins.items()):
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        result[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    return result


def verify_pins() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        _pin_map(SOURCE_PINS, AUDIO_ROOT),
        _pin_map(BOUNDARY_PINS, WORKTREE),
        _pin_map(SIBLING_PINS, WORKTREE),
    )


def linked_rows_digest() -> str:
    return object_digest(list(LINKED_ROWS))


def board_row_projection(path: Path) -> dict[str, Any]:
    data = read_strict_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise ValueError("board_shape_invalid")
    for row in data["tasks"]:
        if isinstance(row, dict) and row.get("id") == TASK:
            missing = [field for field in BOARD_ROW_FIELDS if field not in row]
            if missing:
                raise ValueError("board_row_missing_fields")
            return {field: row[field] for field in BOARD_ROW_FIELDS}
    raise ValueError("board_row_missing")


def board_row_digest(projection: Any) -> str:
    return object_digest(projection)


def _required_artifacts() -> list[dict[str, Any]]:
    rows = (
        ("A01", "accepted CCF AATC 2025 participant registration and executed "
                "participant agreement for this project/team", "BLK-01"),
        ("A02", "immutable train/dev/test challenge dataset with exact "
                "version, file list and full SHA-256", "BLK-02"),
        ("A03", "challenge dataset licence and written terms for local "
                "execution, benchmarking, output use and publication",
         "BLK-02"),
        ("A04", "organizer-issued permitted multi-distortion pairing list "
                "with exact digest and official semantics", "BLK-03"),
        ("A05", "official baseline, scorer, metric implementation, "
                "submission schema and reference outputs", "BLK-04"),
        ("A06", "frozen matched cohort per RST stratum with clean/audio "
                "references, corruption metadata and loss masks", "BLK-05"),
        ("A07", "held-out speaker split, failed-item list and adverse/missing "
                "case results", "BLK-05"),
        ("A08", "rights-cleared listening or predictive scorer with consent, "
                "output-use terms and language/speaker groups", "BLK-05"),
        ("A09", "measured Evidence-profile results separating paired, "
                "unpaired, synthetic, human and source-reported evidence",
         "BLK-06"),
        ("A10", "target-device timing/resources, opt-in adapter intake with "
                "OFF default, benchmark review and release approval",
         "BLK-06"),
    )
    return [{
        "id": artifact_id,
        "name": name,
        "blocker": blocker,
        "present": False,
        "verified": False,
        "licensed": False,
        "admitted": False,
        "blocked": True,
        "sha256": None,
    } for artifact_id, name, blocker in rows]


def _exact_blockers() -> list[dict[str, Any]]:
    rows = (
        ("BLK-01", "A01",
         "No accepted CCF AATC 2025 participant registration or executed "
         "participant agreement exists in the workspace. The research note "
         "records only that training/dev data requires participant "
         "registration; it records no acceptance, account or terms.",
         "Supply the organizer acceptance record, participant/team identity "
         "and executed agreement with a reviewed digest, then register the "
         "exact permitted use."),
        ("BLK-02", "A02",
         "No challenge dataset, split manifest, license text or checksum "
         "exists. The local EARS-derived corruptions are a 12-clip synthetic "
         "pilot, not the registered train/dev/test material.",
         "Supply the immutable challenge dataset version, every split file "
         "list and full SHA-256, plus the dataset licence and written terms "
         "for execution, benchmarking, output use and publication."),
        ("BLK-03", "A04",
         "No organizer-issued permitted multi-distortion pairing list or "
         "official pair semantics exists. The task-local envelope is a "
         "synthetic schema control only and permits no combination.",
         "Supply the organizer pairing specification with exact digest, the "
         "permitted pair set, corruption parameters and any forbidden "
         "combinations, then pin it before a unified run."),
        ("BLK-04", "A05",
         "No official baseline, scorer, metric implementation, submission "
         "schema or reference outputs exist. The local per-task screens use "
         "project-defined SI-SDR/RMSE/STOI comparisons, not the challenge "
         "metric.",
         "Supply the official baseline and scorer packages with full "
         "SHA-256, the submission schema, metric weights and reference "
         "outputs, then verify them on a known item."),
        ("BLK-05", "A06",
         "No frozen matched cohort, clean/audio reference set, corruption "
         "metadata, loss mask, held-out speaker split, failed-item list or "
         "rights-cleared listening/predictive scorer exists for the challenge "
         "strata.",
         "Supply an immutable cohort per RST stratum with clean and degraded "
         "references, exact corruption metadata and masks, held-out speakers, "
         "failed items and approved preservation/listening scoring."),
        ("BLK-06", "A09",
         "No measured Evidence-profile run, unified comparison, device "
         "timing/resource telemetry, opt-in adapter intake, independent "
         "review or release approval exists. No result in this package "
         "qualifies.",
         "Supply measured Evidence-profile results with evidence-class "
         "separation, failed/adverse cases, target-device timing and "
         "resources, an opt-in adapter with OFF default, independent review "
         "and release approval."),
    )
    return [{
        "id": blocker_id,
        "artifact_id": artifact_id,
        "status": "open",
        "missing": missing,
        "required_action": action,
        "qualifies": False,
    } for blocker_id, artifact_id, missing, action in rows]


def _release_gates(linked_row: dict[str, Any]) -> list[dict[str, Any]]:
    rows = (
        ("RG-01", "challenge registration and participant agreement",
         "Organizer acceptance, participant/team identity and executed "
         "agreement with a reviewed digest."),
        ("RG-02", "licensed dataset identity",
         "Immutable train/dev/test version, file list, full SHA-256, dataset "
         "licence and written execution/publication terms."),
        ("RG-03", "organizer permitted multi-distortion pairing list",
         "Official pair set, corruption parameters, forbidden combinations "
         "and exact digest pinned before any unified run."),
        ("RG-04", "official baseline, scorer and submission format",
         "Baseline/scorer packages with SHA-256, metric implementation and "
         "weights, submission schema and reference outputs."),
        ("RG-05", "frozen matched cohorts per RST stratum",
         "Clean and degraded references, corruption metadata and loss masks, "
         "held-out speaker split and failed-item list."),
        ("RG-06", "Evidence acceptance profile",
         "Pinned scorer, corpus and cohort, aggregation, failed items, "
         "controls and separation of paired/unpaired/synthetic/human/"
         "source-reported evidence."),
        ("RG-07", "rights-cleared listening, consent and output use",
         "Consent, output-use terms, language/speaker groups and an approved "
         "listening or predictive scorer."),
        ("RG-08", "device timing, opt-in intake and release review",
         "Target-device timing/resources, separate opt-in adapter intake with "
         "OFF default, independent review and release approval."),
    )
    return [{
        "id": gate_id,
        "title": title,
        "status": "blocked",
        "qualifies": False,
        "reopen_condition": condition,
        "linked_row": linked_row,
    } for gate_id, title, condition in rows]


def _evidence_profile_rows() -> list[dict[str, Any]]:
    rows = (
        ("EVID-01", "scorer pinned and implemented",
         "No official or approved challenge scorer, metric implementation or "
         "weight set exists."),
        ("EVID-02", "corpus and cohort identity",
         "No registered dataset, split manifest or full SHA-256 exists."),
        ("EVID-03", "stratified cohort freeze",
         "No frozen paired cohort per RST stratum, clean reference or "
         "corruption metadata exists."),
        ("EVID-04", "aggregation and pair weights pre-registered",
         "No organizer pairing list or pre-registered aggregation/weight "
         "decision exists."),
        ("EVID-05", "failed items and adverse/missing cases",
         "Only synthetic schema controls exist; no measured failed-item, "
         "missing or adverse challenge result exists."),
        ("EVID-06", "identity and single-distortion controls",
         "No challenge identity control or per-family control run exists; "
         "only declared arithmetic was reproduced."),
        ("EVID-07", "evidence-class separation",
         "Paired, unpaired, synthetic, human and source-reported results "
         "cannot be separated because no measured result exists."),
        ("EVID-08", "representative valid and invalid case through the bundle",
         "No representative valid challenge item or invalid/missing item has "
         "been validated through an official bundle."),
    )
    return [{
        "id": row_id,
        "requirement": requirement,
        "status": "blocked",
        "qualifies": False,
        "evidence": evidence,
    } for row_id, requirement, evidence in rows]


def _evidence_outcomes() -> list[dict[str, Any]]:
    return [{
        "id": f"OUT-{index:02d}",
        "requirement": row["requirement"],
        "status": "blocked",
        "value": None,
        "qualifies": False,
    } for index, row in enumerate(_evidence_profile_rows(), start=1)]


def _qualification() -> dict[str, Any]:
    return {
        "status": "not_qualified",
        "decision": "DEFER",
        "proposal_only": True,
        "evidence_status": "incomplete",
        "licensed_implementation_runtime_present": False,
        "challenge_registration_present": False,
        "challenge_artifact_present": False,
        "organizer_pairing_present": False,
        "official_baseline_present": False,
        "rights_cleared_cohort_present": False,
        "research_note_present": (
            AUDIO_ROOT / RESEARCH_NOTE).is_file(),
        "classical_baseline_present": classical_baseline_guard()["present"],
        "blocked_release_gates": 8,
        "open_blockers": 6,
        "qualifying_results": 0,
        "reasons": [
            "no accepted participant registration or executed agreement "
            "exists",
            "no licensed train/dev/test challenge dataset, split manifest or "
            "SHA-256 exists",
            "no organizer-issued permitted multi-distortion pairing list "
            "exists",
            "no official baseline, scorer, submission package or reference "
            "outputs exist",
            "no frozen matched cohort, clean references, masks, held-out "
            "speakers or failed-item results exist",
            "no measured Evidence-profile, device-timing, opt-in intake or "
            "release review exists",
        ],
    }


def _report_core(projection: dict[str, Any],
                 linked_row: dict[str, Any]) -> dict[str, Any]:
    guard = classical_baseline_guard()
    state = challenge_state()
    return {
        "qualification": _qualification(),
        "disposition": {
            "decision": "DEFER",
            "status": "incomplete",
            "proposal_only": True,
            "qualification_status": "not_qualified",
            "qualifying_results": 0,
            "blocked_before": "registration_and_dataset_access",
            "blocked_release_gates": 8,
        },
        "boundary": {
            "provider_registration": False,
            "descriptor_or_registry_change": False,
            "default_change": False,
            "installed_v0_behavior_change": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
            "board_or_handoff_change": False,
            "external_assets_copied": False,
            "task_local_only": True,
            "installed_v0_geometry": {
                "sample_rate_hz": 16000,
                "channels": 1,
                "sample_format": "f32",
                "frame_samples": 160,
                "unchanged": True,
            },
        },
        "public_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
        },
        "scope": {
            "directory": TASK_PREFIX,
            "task_local_only": True,
            "network_used": False,
            "download_attempted": False,
            "challenge_registration_attempted": False,
            "challenge_data_read": False,
            "challenge_data_downloaded": False,
            "vendor_sdk_copied": False,
            "vendor_runtime_imported": False,
            "vendor_runtime_invoked": False,
            "baseline_runtime_invoked": False,
            "unified_benchmark_run": False,
            "unified_benchmark_claim": False,
            "pairing_pinned_from_organizer": False,
            "audio_read": False,
            "audio_played": False,
            "reference_audio_rendered": False,
            "listening_conducted": False,
            "device_timing_measured": False,
            "benchmark_run": False,
            "benchmark_claim": False,
            "release_claim": False,
            "provider_registration": False,
            "descriptor_registry_change": False,
            "default_selected": False,
            "installed_v0_behavior_change": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
        },
        "non_claims": [
            "No result in this package is a qualification, benchmark or "
            "release.",
            "No CCF AATC registration was attempted, accepted or implied; no "
            "participant account, agreement or credentials exist.",
            "No challenge dataset, split, license text, baseline, scorer, "
            "submission package or reference output was downloaded, read or "
            "copied.",
            "The four local classical screens are per-task synthetic pilots, "
            "not a unified restorer, not the challenge baseline and not a "
            "substitute for registered data.",
            "The pairing envelope is a synthetic schema control. It records "
            "no organizer-permitted pair and cannot qualify any combination.",
            "No audio was read or played; no reference was rendered; no "
            "listening, consent or output-use grant exists.",
            "No SI-SDR, RMSE, STOI, quality, intelligibility, complexity or "
            "unified result was measured for the challenge.",
            "No device timing, resource, benchmark, provider or release review "
            "was performed.",
            "No provider, descriptor, registry, default, installed-v0, ABI, "
            "shared-build, CI, board or handoff file is changed.",
        ],
        "observed_provenance": {
            "research_note": research_note_probe(),
            "challenge_state": state,
            "classical_baseline_guard": guard,
            "per_family_baselines": [
                {
                    "family": family,
                    "name": spec["name"],
                    "controlled_degradation": spec["controlled_degradation"],
                    "missing_information": spec["missing_information"],
                    "required_context": spec["required_context"],
                    "forbidden_substitution": spec["forbidden_substitution"],
                    "local_baseline": spec["local_baseline"],
                    "candidate_not_run": spec["candidate_not_run"],
                    "owned_task": spec["owned_task"],
                    "qualifies": False,
                }
                for family, spec in (
                    (family, FAMILY_SPECS[family]) for family in FAMILIES)
            ],
            "sibling_evidence": [dict(row) for row in LINKED_ROWS],
        },
        "documented_challenge_envelope": documented_challenge_envelope(),
        "synthetic_pairing_envelope": synthetic_pairing_envelope(),
        "source_presence": source_presence(),
        "license_findings": license_findings(),
        "required_artifacts": _required_artifacts(),
        "exact_blockers": _exact_blockers(),
        "required_results": {
            "registration_admitted": False,
            "dataset_identity_admitted": False,
            "organizer_pairing_admitted": False,
            "official_baseline_and_scorer_admitted": False,
            "rights_cleared_cohort_present": False,
            "frozen_stratified_cohort_present": False,
            "evidence_profile_measured": False,
            "failed_item_analysis_present": False,
            "listening_or_predictive_scoring_measured": False,
            "device_timing_measured": False,
            "provider_intake_approved": False,
            "release_approved": False,
            "no_result_qualifies": True,
        },
        "reproduction": {
            "commands": [
                "export PYTHONDONTWRITEBYTECODE=1",
                "python3 run.py all",
                "python3 -m unittest -v test_reference.py",
                "python3 verify.py",
            ],
            "python": "3.11 or newer, standard library only",
            "repeat_count": 3,
            "byte_identical_required": True,
            "network_used": False,
        },
        "gates": _release_gates(linked_row),
        "evidence_profile": {
            "profile": PROFILE,
            "profile_label": PROFILE_LABEL,
            "rows": _evidence_profile_rows(),
        },
        "evidence_outcomes": {"rows": _evidence_outcomes()},
        "linked_row_identity": {
            "projection": projection,
            "sha256": board_row_digest(projection),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "linked_rows": [dict(row) for row in LINKED_ROWS],
            "linked_rows_sha256": linked_rows_digest(),
        },
        "challenge_record": dict(state),
    }


def build_contract() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    linked_row = dict(projection)
    core = _report_core(projection, linked_row)
    return {
        "schema_id": CONTRACT_ID,
        "contract_version": "0.1",
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification": core["qualification"],
        "qualification_status": "not_qualified",
        "disposition": core["disposition"],
        "boundary": core["boundary"],
        "public_v0_geometry": core["public_v0_geometry"],
        "scope": core["scope"],
        "non_claims": core["non_claims"],
        "observed_provenance": core["observed_provenance"],
        "documented_challenge_envelope":
            core["documented_challenge_envelope"],
        "synthetic_pairing_envelope": core["synthetic_pairing_envelope"],
        "source_presence": core["source_presence"],
        "license_findings": core["license_findings"],
        "required_artifacts": core["required_artifacts"],
        "exact_blockers": core["exact_blockers"],
        "required_results": core["required_results"],
        "reproduction": core["reproduction"],
        "release_gates": core["gates"],
        "evidence_profile_requirements": core["evidence_profile"]["rows"],
        "evidence_outcomes": core["evidence_outcomes"]["rows"],
        "linked_row_projection": projection,
        "linked_row_projection_sha256": board_row_digest(projection),
        "linked_rows": core["linked_row_identity"]["linked_rows"],
        "linked_rows_sha256": core["linked_row_identity"]["linked_rows_sha256"],
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
        "classical_baseline_guard":
            core["observed_provenance"]["classical_baseline_guard"],
        "challenge_record": core["challenge_record"],
    }


def build_report() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    linked_row = dict(projection)
    core = _report_core(projection, linked_row)
    contract = build_contract()
    source_pins, boundary_pins, sibling_pins = verify_pins()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "contract_sha256": object_digest(contract),
        "disposition": core["disposition"],
        "qualification": core["qualification"],
        "boundary": core["boundary"],
        "public_v0_geometry": core["public_v0_geometry"],
        "scope": core["scope"],
        "non_claims": core["non_claims"],
        "observed_provenance": core["observed_provenance"],
        "documented_challenge_envelope":
            core["documented_challenge_envelope"],
        "synthetic_pairing_envelope": core["synthetic_pairing_envelope"],
        "source_presence": core["source_presence"],
        "license_findings": core["license_findings"],
        "required_artifacts": core["required_artifacts"],
        "exact_blockers": core["exact_blockers"],
        "required_results": core["required_results"],
        "reproduction": core["reproduction"],
        "gates": core["gates"],
        "evidence_profile": core["evidence_profile"],
        "evidence_outcomes": core["evidence_outcomes"],
        "linked_row_identity": core["linked_row_identity"],
        "board_snapshot": {
            "path": BOARD_TASK_ROW,
            "mutable": True,
            "note": "Mutable board path recorded for provenance only; never "
                    "hashed, gated or treated as a result.",
        },
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "sibling_pins": sibling_pins,
        "family_control": family_control(),
        "degradation_control": degradation_control(),
        "pair_control": pair_control(),
        "aggregation_control": aggregation_control(),
        "admission": admission_controls(),
        "classical_baseline_guard":
            core["observed_provenance"]["classical_baseline_guard"],
        "challenge_record": core["challenge_record"],
    }


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    payload = canonical_bytes(report)
    return payload.decode("ascii"), sha256_bytes(payload)


def validate_contract(contract: Any) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    required = (
        "schema_id", "contract_version", "task", "component", "decision",
        "status", "proposal_only", "qualification_status", "disposition",
        "boundary", "scope", "non_claims", "release_gates",
        "evidence_profile_requirements", "evidence_outcomes",
        "linked_row_projection", "source_pins", "boundary_pins",
        "sibling_pins", "classical_baseline_guard", "challenge_record",
        "board_file_pinned", "board_status_is_observation_only",
    )
    missing = [field for field in required if field not in contract]
    if missing:
        raise ValueError("contract_missing_fields")
    if contract["schema_id"] != CONTRACT_ID:
        raise ValueError("contract_schema_mismatch")
    if contract["task"] != TASK or contract["component"] != COMPONENT_ID:
        raise ValueError("contract_identity_mismatch")
    if contract["decision"] != "DEFER" or contract["status"] != "incomplete":
        raise ValueError("contract_disposition_mismatch")
    if contract["qualification_status"] != "not_qualified":
        raise ValueError("contract_qualification_mismatch")
    if contract["board_file_pinned"] is not False:
        raise ValueError("contract_board_pinned")
    if len(contract["release_gates"]) != 8:
        raise ValueError("contract_gate_count")
    if len(contract["evidence_profile_requirements"]) != 8:
        raise ValueError("contract_evidence_row_count")
    if len(contract["evidence_outcomes"]) != 8:
        raise ValueError("contract_evidence_outcome_count")
    if BOARD_TASK_ROW in contract["source_pins"]:
        raise ValueError("contract_board_pinned")


def verify_sources_manifest(payload: bytes) -> int:
    checked = 0
    for line in payload.decode("ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or not HEX64.match(parts[0]):
            raise ValueError("sources_malformed")
        digest, name = parts
        if name.startswith("source:"):
            path = AUDIO_ROOT / name[len("source:"):]
        elif name.startswith("boundary:") or name.startswith("sibling:"):
            path = WORKTREE / name.split(":", 1)[1]
        else:
            path = WORKTREE / name
        if not path.is_file():
            raise ValueError("sources_missing:" + name)
        if sha256_file(path) != digest:
            raise ValueError("sources_mismatch:" + name)
        checked += 1
    if BOARD_TASK_ROW in payload.decode("ascii"):
        raise ValueError("sources_board_pinned")
    return checked
