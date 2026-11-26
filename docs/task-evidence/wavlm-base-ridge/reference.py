# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local DEFER evidence for SDK-WAVLM-BASE-RIDGE.

Standard-library only and deterministic. This module never imports, loads or
executes WavLM, PyTorch, Transformers, a checkpoint, audio or a network client.
It records the documented-but-absent model provenance, the missing rights and
qualification artifacts, a fail-closed caller admission boundary, and one
explicitly synthetic standardized-ridge arithmetic control labelled
``synthetic_ridge_arithmetic_control_not_evidence`` that can never qualify.

The research source record documents ``microsoft/wavlm-base-plus`` revision
``4c66d4806a428f2e922ccfa1a962776e232d487b`` with a null license field and a
377,617,425-byte ``pytorch_model.bin``. No weight file is present locally, no
upstream snapshot or runtime is staged, and the model card/terms are absent.
Nothing is downloaded, reconstructed or copied here.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-WAVLM-BASE-RIDGE"
COMPONENT_ID = "wavlm-base-ridge"
TASK_TITLE = "WavLM Base+ + ridge"
CONTRACT_ID = "audio-sdk/wavlm-base-ridge/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "implementation"
BASE_COMMIT = "56d3736c6f4274bde419325d3892465018d6bfdb"
BRANCH = "swarm/SDK-WAVLM-BASE-RIDGE"
REVIEWER = "reviewer-WAVLM-BASE-RIDGE"
TASK_PREFIX = "docs/task-evidence/wavlm-base-ridge/"
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = (
    "id", "title", "repository", "mode", "depends_on", "component", "evidence")

RUN_PREFIX = "research/tsm-followup-20261101/agent-neural/run"

MODEL_REPO_ID = "microsoft/wavlm-base-plus"
MODEL_REVISION = "4c66d4806a428f2e922ccfa1a962776e232d487b"
MODEL_FILES = {
    "README.md":
        "d417fc16b08e2f66f0af6b371e47a5f9f1f596f6c1c593f1214d360c41d7a27e",
    "config.json":
        "fea6df1c2700a3954fc07e70588aecc9055eeb28db2ff57151a2db0d19180ed4",
    "preprocessor_config.json":
        "99272fe8ccfab114b68b478681ea47ee3a1ce62bb788cb92dd6e4f69fb1f1da2",
    "pytorch_model.bin":
        "3bb273a6ace99408b50cfc81afdbb7ef2de02da2eab0234e18db608ce692fe51",
}
MODEL_FILE_BYTES = {
    "README.md": 3904,
    "config.json": 2232,
    "preprocessor_config.json": 215,
    "pytorch_model.bin": 377617425,
}

SOURCE_PINS: dict[str, str] = {
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-neural/REPORT.md":
        "f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73",
    RUN_PREFIX + "/run_ssl_encoder_cv.py":
        "09b7e3cc4ff5fa01768cd925f38d972b555f9864feaf38036fafac7c6350f660",
    RUN_PREFIX + "/score_nonnegative_heads.py":
        "201f88580dfc3f0fe46d063d48a1fa306e1345c60c90581eac7a012c97512790",
    RUN_PREFIX + "/syl_eval_manifest.json":
        "3c7b3731cf6d2312e42e3333cae03bc631f6d1dbf557b773e134468c867897e2",
    RUN_PREFIX + "/wavlm-base-plus_source.json":
        "5210619f683caf2da4ee0c5e0973dba62fca8db8e06f47a215bdec54efe868d1",
    RUN_PREFIX + "/wavlm-base-plus_results.json":
        "9e041bf0369ebbc5f6142a9230ba41e84c86fd4ce2a6ba10bf94effa36570297",
    RUN_PREFIX + "/wavlm-base-plus_fp32_embeddings.npz":
        "12372ed9f204f1668778bc21096633758d1169bcde8e2db5d947f6ffd06776a1",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
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
    "docs/task-evidence/distil-wav2vec2-adult-child-ridge/report.json":
        "ff7b70f389b8c7908c917aa2488728d7f972a8acd22bf66c56d9a671cd5a65d4",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/report.json":
        "6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9",
    "docs/task-evidence/small-log-mel-gru/report.json":
        "619a4bf03655c3d49afd666ee8eaabaef3e452c98dfab1c36202d6ae44d7091c",
    "docs/task-evidence/sylnet/report.json":
        "b81b1cd8691528f4cd492deaced8a589309048cdca54ab256c7cb0926bd32331",
    "docs/task-evidence/usc-mrate/report.json":
        "d74c03b0e93c9e6c729fb5f10d17dc253e828dfade2579b9e3b586b11c02f246",
    "docs/task-evidence/phase-vocoder-baseline/report.json":
        "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json":
        "57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2",
}

PROFILE_PHRASES = (
    "source/output mapping", "duration", "pitch", "transient audibility",
    "playback buffering", "1×", "rebuffer", "drift",
    "final partial window", "source timestamps",
)

WEIGHT_PROBES = (
    "data/models/wavlm-base-plus",
    "data/models/microsoft/wavlm-base-plus",
    "data/checkouts/wavlm-base-plus",
    "data/checkouts/microsoft/wavlm-base-plus",
    "data/models/hub/models--microsoft--wavlm-base-plus",
)
SOURCE_PROBES = (
    "data/checkouts/wavlm-base-plus",
    "data/checkouts/microsoft/wavlm-base-plus",
    "research/wavlm-base-plus",
    "research/wavlm",
    "third_party/wavlm",
    "deps/wavlm",
)
HF_CACHE_NAME = "models--microsoft--wavlm-base-plus"

LICENSE_MARKER_NAMES = (
    "LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING", "COPYING.txt",
    "NOTICE", "NOTICE.txt", "MODEL_CARD", "MODEL_CARD.md",
)

FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".gguf", ".lib", ".m4a",
    ".mdl", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o", ".onnx", ".opus",
    ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wav", ".wasm", ".weights",
}

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(
    os.environ.get("AUDIOML_ROOT", str(WORKTREE.parents[2]))).resolve()

SCHEMA_MANIFEST_ID = "audio-sdk/wavlm-base-ridge/qualification/0.1"
ALPHA = Fraction(10)

MANIFEST_FIELDS = (
    "schema_id", "cohort_id", "source", "weights", "runtime",
    "feature_extractor", "windows", "head", "outcomes", "rights")
SOURCE_FIELDS = (
    "repo_id", "revision", "license_id", "license_sha256",
    "model_card_sha256")
WEIGHTS_FIELDS = ("format", "files")
WEIGHT_FILE_FIELDS = ("name", "sha256", "bytes")
RUNTIME_FIELDS = (
    "python", "torch", "transformers", "device", "threads", "deterministic",
    "offline", "torch_wheel_sha256", "transformers_wheel_sha256")
FEATURE_EXTRACTOR_FIELDS = (
    "kind", "layer", "pooling", "normalize", "sample_rate_hz", "window_samples",
    "feature_dim", "config_sha256")
WINDOW_FIELDS = ("id", "start_sample", "end_sample", "features",
                 "label_rate_sps")
HEAD_FIELDS = ("kind", "alpha", "scaler", "artifact_sha256")
OUTCOMES_FIELDS = (
    "mae_syllables_per_second", "rmse_syllables_per_second",
    "bias_syllables_per_second", "pearson_r_squared", "nonfinite_count",
    "window_count", "qualified")
RIGHTS_FIELDS = (
    "model_terms_reviewed", "weight_redistribution_approved",
    "corpus_terms_reviewed", "labels_reviewed", "output_use_defined",
    "commercial_use_approved")

REQUIRED_WEIGHT_NAMES = frozenset(
    {"README.md", "config.json", "preprocessor_config.json"})
WEIGHT_FILE_NAMES = frozenset({"pytorch_model.bin", "model.safetensors"})
SAMPLES_PER_WINDOW = 64000
SAMPLE_RATE_HZ = 16000
SAMPLE_ALIGNMENT = 160
TOTAL_MANIFEST_WINDOWS = 4

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
LICENSE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]{1,63}$")
RATIONAL = re.compile(r"^(0|[1-9][0-9]{0,8})/([1-9][0-9]{0,8})$")
DECIMAL = re.compile(r"^-?(0|[1-9][0-9]{0,7})\.[0-9]{1,9}$")


# ---------------------------------------------------------------------------
# Strict JSON and canonicalization
# ---------------------------------------------------------------------------

def _reject_constant(value: str) -> None:
    raise ValueError("json_nonfinite_constant:" + value)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("json_duplicate_key:" + key)
        result[key] = value
    return result


def read_strict_json(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("json_not_utf8") from error
    try:
        value = json.loads(
            text, object_pairs_hook=_strict_object,
            parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("json_malformed:" + str(error)) from error
    _no_floats(value)
    return value


def _no_floats(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("nonstring_key")
            _no_floats(item)
    elif isinstance(value, list):
        for item in value:
            _no_floats(item)


def canonical_bytes(value: Any) -> bytes:
    _no_floats(value)
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    payload = canonical_bytes(report)
    return payload.decode("ascii"), hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# Exact decimal formatting
# ---------------------------------------------------------------------------

def _decimal(value: Fraction, places: int = 9) -> str:
    scale = 10 ** places
    magnitude = abs(value)
    scaled = magnitude.numerator * scale
    whole, remainder = divmod(scaled, magnitude.denominator)
    if remainder * 2 >= magnitude.denominator:
        whole += 1
    sign = "-" if value < 0 and whole != 0 else ""
    return f"{sign}{whole // scale}.{whole % scale:0{places}d}"


def _sqrt_decimal(value: Fraction, places: int = 9) -> str:
    if value < 0:
        raise ValueError("sqrt_negative")
    scale = 10 ** places
    root = math.isqrt(value.numerator * scale * scale // value.denominator)
    return f"{root // scale}.{root % scale:0{places}d}"


def _sqrt_fraction(value: Fraction, places: int = 18) -> Fraction:
    if value < 0:
        raise ValueError("variance_negative")
    scale = 10 ** places
    root = math.isqrt(value.numerator * scale * scale // value.denominator)
    return Fraction(root, scale)


# ---------------------------------------------------------------------------
# Linked-row identity
# ---------------------------------------------------------------------------

def board_row_projection(path: Path) -> dict[str, Any]:
    board = read_strict_json(path)
    rows = board.get("tasks") if isinstance(board, dict) else None
    if not isinstance(rows, list):
        raise ValueError("board_tasks_missing")
    matches = [row for row in rows
               if isinstance(row, dict) and row.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    row = matches[0]
    missing = [field for field in BOARD_ROW_FIELDS if field not in row]
    if missing:
        raise ValueError("board_row_field_missing:" + missing[0])
    return {field: row[field] for field in BOARD_ROW_FIELDS}


def board_row_digest(projection: dict[str, Any]) -> str:
    return object_digest(projection)


LINKED_ROWS = (
    {"task": "SDK-DISTIL-WAV2VEC2-ADULT-CHILD-RIDGE",
     "role": "merged ridge rate head boundary; not reused",
     "report_sha256":
         "ff7b70f389b8c7908c917aa2488728d7f972a8acd22bf66c56d9a671cd5a65d4"},
    {"task": "SDK-DYNAMIC-INT8-WAV2VEC2-BASE",
     "role": "merged wav2vec2 rate-encoder boundary; no WavLM content",
     "report_sha256":
         "6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9"},
    {"task": "SDK-SMALL-LOG-MEL-GRU",
     "role": "merged tiny rate estimator baseline; not reused",
     "report_sha256":
         "619a4bf03655c3d49afd666ee8eaabaef3e452c98dfab1c36202d6ae44d7091c"},
    {"task": "SDK-SYLNET",
     "role": "merged syllable-count rate estimator; not reused",
     "report_sha256":
         "b81b1cd8691528f4cd492deaced8a589309048cdca54ab256c7cb0926bd32331"},
    {"task": "SDK-USC-MRATE",
     "role": "merged transcript-free rate estimator; not reused",
     "report_sha256":
         "d74c03b0e93c9e6c729fb5f10d17dc253e828dfade2579b9e3b586b11c02f246"},
    {"task": "SDK-PHASE-VOCODER-BASELINE",
     "role": "merged rate/playback baseline; no estimator content",
     "report_sha256":
         "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7"},
    {"task": "SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE",
     "role": "merged rate-playback DEFER boundary; not recognition evidence",
     "report_sha256":
         "57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2"},
)


def linked_rows_digest() -> str:
    return object_digest([dict(row) for row in LINKED_ROWS])


# ---------------------------------------------------------------------------
# Source presence, licensing and pins
# ---------------------------------------------------------------------------

def _tree_digest(files: dict[str, str]) -> str:
    lines = [f"{name} {digest}" for name, digest in sorted(files.items())]
    return hashlib.sha256(("\n".join(lines) + "\n").encode("ascii")).hexdigest()


MODEL_TREE_SHA256 = _tree_digest(MODEL_FILES)


def verify_pins() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    def collect(pins: dict[str, str], root: Path, label: str) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                raise ValueError(label + "_pin_missing:" + relative)
            actual = sha256_file(path)
            if actual != expected:
                raise ValueError(label + "_pin_mismatch:" + relative)
            result[relative] = {
                "sha256": expected, "actual": actual, "verified": True}
        return result

    return (collect(SOURCE_PINS, AUDIO_ROOT, "source"),
            collect(BOUNDARY_PINS, WORKTREE, "boundary"))


def license_marker_probe() -> dict[str, Any]:
    model_dir = AUDIO_ROOT / "data/models/microsoft/wavlm-base-plus"
    model_markers = [name for name in LICENSE_MARKER_NAMES
                     if (model_dir / name).is_file()]
    record_path = AUDIO_ROOT / (RUN_PREFIX + "/wavlm-base-plus_source.json")
    license_value: Any = None
    if record_path.is_file():
        record = read_strict_json(record_path)
        if isinstance(record, dict):
            license_value = record.get("license")
    return {
        "model_license_marker_files": model_markers,
        "source_record_license_value": license_value,
        "source_record_license_present": (
            isinstance(license_value, str) and bool(license_value.strip())),
        "model_terms_understood": False,
        "redistribution_approved": False,
        "commercial_use_approved": False,
        "output_use_defined": False,
        "qualifies": False,
    }


def _module_present(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def source_presence() -> dict[str, Any]:
    weight_probes = {probe: (AUDIO_ROOT / probe).is_dir()
                     for probe in WEIGHT_PROBES}
    hf_cache_present = (
        Path.home() / ".cache/huggingface/hub" / HF_CACHE_NAME).is_dir()
    source_probes = {probe: (AUDIO_ROOT / probe).is_dir()
                     for probe in SOURCE_PROBES}
    weights_present = any(weight_probes.values()) or hf_cache_present
    return {
        "documented_revision": MODEL_REVISION,
        "documented_revision_present": True,
        "weight_probes": weight_probes,
        "hf_cache_probe": HF_CACHE_NAME,
        "hf_cache_present": hf_cache_present,
        "weights_present": weights_present,
        "model_weight_file_count": (
            len(MODEL_FILES) if weights_present else 0),
        "source_probes": source_probes,
        "upstream_source_checkout_present": any(source_probes.values()),
        "runtime_torch_present": _module_present("torch"),
        "runtime_transformers_present": _module_present("transformers"),
        "runtime_present": False,
        "runtime_note": (
            "runtime_present means the exact pinned torch 2.2.2 / "
            "transformers 4.40.2 pair on Python 3.10, not mere module "
            "availability"),
        "license_present": False,
        "exact_licensed_source_weights_runtime_present": False,
        "presence_is_not_admission": True,
        "admitted": False,
        "weights_used": False,
        "runtime_imported": False,
        "model_executed": False,
        "audio_read": False,
        "download_attempted": False,
        "network_used": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Synthetic standardized-ridge arithmetic control (never evidence)
# ---------------------------------------------------------------------------

def _exact_int(value: Any, label: str, minimum: int = 0,
               maximum: int | None = None) -> int:
    if type(value) is not int:
        raise ValueError(label + "_not_int")
    if value < minimum:
        raise ValueError(label + "_below_minimum")
    if maximum is not None and value > maximum:
        raise ValueError(label + "_above_maximum")
    return value


def _fraction(value: Any, label: str, low: Fraction,
              high: Fraction) -> Fraction:
    if not isinstance(value, str):
        raise ValueError(label + "_not_string")
    if not RATIONAL.match(value):
        raise ValueError(label + "_malformed")
    numerator, denominator = value.split("/")
    parsed = Fraction(int(numerator), int(denominator))
    if parsed < low or parsed > high:
        raise ValueError(label + "_out_of_range")
    return parsed


def _decimal_value(value: Any, label: str, low: Fraction,
                   high: Fraction) -> Fraction:
    if not isinstance(value, str):
        raise ValueError(label + "_not_string")
    if not DECIMAL.match(value):
        raise ValueError(label + "_malformed")
    parsed = Fraction(value)
    if parsed < low or parsed > high:
        raise ValueError(label + "_out_of_range")
    return parsed


def _synthetic_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index in range(24):
        syllables = 4 + ((index * 7) % 13)
        noise = ((index * 5) % 3) - 1
        features = [
            Fraction(syllables * 2 + noise),
            Fraction(((index * 11) % 7) - 3),
            Fraction(((index * 3) % 5) - 2),
            Fraction(((index * 13) % 4) - 1),
        ]
        rows.append({
            "index": index,
            "features": features,
            "label": Fraction(syllables, 4),
        })
    return rows


def _solve(matrix: list[list[Fraction]], vector: list[Fraction]
           ) -> list[Fraction]:
    size = len(vector)
    augmented = [row[:] + [vector[index]]
                 for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = None
        for row in range(column, size):
            if augmented[row][column] != 0:
                pivot = row
                break
        if pivot is None:
            raise ValueError("ridge_singular")
        augmented[column], augmented[pivot] = (
            augmented[pivot], augmented[column])
        divisor = augmented[column][column]
        augmented[column] = [value / divisor
                             for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor == 0:
                continue
            augmented[row] = [value - factor * pivot_value
                              for value, pivot_value
                              in zip(augmented[row], augmented[column])]
    return [augmented[index][size] for index in range(size)]


def fit_ridge(rows: list[dict[str, Any]], alpha: Fraction
              ) -> dict[str, Any]:
    if type(alpha) is not Fraction or alpha <= 0:
        raise ValueError("ridge_alpha")
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError("ridge_rows")
    dimension = None
    labels: list[Fraction] = []
    matrix: list[list[Fraction]] = []
    for row in rows:
        if not isinstance(row, dict) or "features" not in row \
                or "label" not in row:
            raise ValueError("ridge_row_fields")
        features = row["features"]
        label = row["label"]
        if not isinstance(features, list) or not features:
            raise ValueError("ridge_features")
        if dimension is None:
            dimension = len(features)
        if len(features) != dimension:
            raise ValueError("ridge_dimension")
        for value in features:
            if type(value) is not Fraction:
                raise ValueError("ridge_feature_not_exact")
        if type(label) is not Fraction or label <= 0:
            raise ValueError("ridge_label")
        matrix.append(features)
        labels.append(label)
    if dimension is None or dimension < 1:
        raise ValueError("ridge_dimension")

    count = len(rows)
    means = [sum((row[column] for row in matrix), Fraction(0)) / count
             for column in range(dimension)]
    scales: list[Fraction] = []
    for column in range(dimension):
        variance = sum(((row[column] - means[column]) ** 2
                        for row in matrix), Fraction(0)) / count
        scale = _sqrt_fraction(variance)
        scales.append(scale if scale != 0 else Fraction(1))

    design = [[(row[column] - means[column]) / scales[column]
               for column in range(dimension)] for row in matrix]
    mean_label = sum(labels, Fraction(0)) / count
    centered = [value - mean_label for value in labels]

    normal = [[sum((design[row][i] * design[row][j]
                    for row in range(count)), Fraction(0))
               for j in range(dimension)] for i in range(dimension)]
    for index in range(dimension):
        normal[index][index] += alpha
    rhs = [sum((design[row][index] * centered[row]
                for row in range(count)), Fraction(0))
           for index in range(dimension)]
    weights = _solve(normal, rhs)
    intercept = mean_label
    return {
        "alpha": alpha,
        "means": means,
        "scales": scales,
        "weights": weights,
        "intercept": intercept,
        "dimension": dimension,
        "count": count,
    }


def predict_ridge(head: dict[str, Any], features: list[Fraction]) -> Fraction:
    if not isinstance(features, list) or len(features) != head["dimension"]:
        raise ValueError("predict_dimension")
    value = head["intercept"]
    for index, feature in enumerate(features):
        if type(feature) is not Fraction:
            raise ValueError("predict_feature_not_exact")
        value += head["weights"][index] * (
            (feature - head["means"][index]) / head["scales"][index])
    return value


def _metrics(predictions: list[Fraction], labels: list[Fraction]
             ) -> dict[str, str]:
    if len(predictions) != len(labels) or not predictions:
        raise ValueError("metrics_count")
    count = len(predictions)
    errors = [prediction - label
              for prediction, label in zip(predictions, labels)]
    mae = sum((abs(error) for error in errors), Fraction(0)) / count
    mse = sum((error * error for error in errors), Fraction(0)) / count
    bias = sum(errors, Fraction(0)) / count
    mean_label = sum(labels, Fraction(0)) / count
    total = sum(((label - mean_label) ** 2 for label in labels), Fraction(0))
    residual = sum((error * error for error in errors), Fraction(0))
    if total == 0:
        r_squared = "undefined"
    else:
        r_squared = _decimal(Fraction(1) - residual / total)
    return {
        "mae_syllables_per_second": _decimal(mae),
        "rmse_syllables_per_second": _sqrt_decimal(mse),
        "bias_syllables_per_second": _decimal(bias),
        "pearson_r_squared": r_squared,
    }


def ridge_control() -> dict[str, Any]:
    rows = _synthetic_rows()
    calibration = rows[:18]
    evaluation = rows[18:]
    head = fit_ridge(calibration, ALPHA)
    predictions = [predict_ridge(head, row["features"])
                   for row in evaluation]
    clipped = [prediction if prediction > 0 else Fraction(0)
               for prediction in predictions]
    labels = [row["label"] for row in evaluation]
    calibration_mean = sum((row["label"] for row in calibration),
                           Fraction(0)) / len(calibration)
    baseline = [calibration_mean for _ in evaluation]
    return {
        "evidence_class": "synthetic_ridge_arithmetic_control_not_evidence",
        "purpose": "exact standardize-and-solve arithmetic only; no WavLM input",
        "alpha": "10/1",
        "calibration_count": len(calibration),
        "evaluation_count": len(evaluation),
        "feature_dim": head["dimension"],
        "weights": [_decimal(weight) for weight in head["weights"]],
        "intercept": _decimal(head["intercept"]),
        "means": [_decimal(value) for value in head["means"]],
        "scales": [_decimal(value) for value in head["scales"]],
        "predictions_syllables_per_second": [
            _decimal(value) for value in predictions],
        "nonnegative_clipped": {
            "negative_prediction_count": sum(
                1 for value in predictions if value < 0),
            "metrics": _metrics(clipped, labels),
        },
        "raw_metrics": _metrics(predictions, labels),
        "constant_calibration_mean_baseline": {
            "value": _decimal(calibration_mean),
            "metrics": _metrics(baseline, labels),
        },
        "labels_are_synthetic": True,
        "audio_read": False,
        "weights_loaded": False,
        "model_executed": False,
        "runtime_imported": False,
        "network_used": False,
        "qualifying_results": 0,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Caller qualification manifest admission (fail-closed)
# ---------------------------------------------------------------------------

def _exact_keys(value: Any, fields: tuple[str, ...], label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(label + "_not_object")
    if set(value) != set(fields):
        raise ValueError(label + "_fields")
    return value


def _hex(value: Any, label: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or not pattern.match(value):
        raise ValueError(label + "_malformed")
    return value


def _validate_windows(windows: Any, dimension: int) -> int:
    if not isinstance(windows, list) or not windows \
            or len(windows) > 10000:
        raise ValueError("windows_count")
    seen: set[str] = set()
    cursor = 0
    for entry in windows:
        window = _exact_keys(entry, WINDOW_FIELDS, "window")
        window_id = window["id"]
        if not isinstance(window_id, str) or not SLUG.match(window_id):
            raise ValueError("window_id")
        if window_id in seen:
            raise ValueError("window_id_duplicate")
        seen.add(window_id)
        start = _exact_int(window["start_sample"], "window_start", 0)
        end = _exact_int(window["end_sample"], "window_end", 0)
        if start % SAMPLE_ALIGNMENT != 0:
            raise ValueError("window_start_misaligned")
        if end % SAMPLE_ALIGNMENT != 0:
            raise ValueError("window_end_misaligned")
        if start != cursor:
            raise ValueError("window_contiguous")
        if end - start != SAMPLES_PER_WINDOW:
            raise ValueError("window_length")
        features = window["features"]
        if not isinstance(features, list) or len(features) != dimension:
            raise ValueError("window_feature_count")
        for feature in features:
            _decimal_value(feature, "window_feature",
                           Fraction(-1000), Fraction(1000))
        _fraction(window["label_rate_sps"], "window_rate",
                  Fraction(1, 1000), Fraction(20))
        cursor = end
    return len(windows)


def validate_manifest(manifest: Any) -> dict[str, Any]:
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root["schema_id"] != SCHEMA_MANIFEST_ID:
        raise ValueError("manifest_schema_id")
    if not isinstance(root["cohort_id"], str) \
            or not SLUG.match(root["cohort_id"]):
        raise ValueError("manifest_cohort_id")

    source = _exact_keys(root["source"], SOURCE_FIELDS, "source")
    if source["repo_id"] != MODEL_REPO_ID:
        raise ValueError("source_repo_id")
    _hex(source["revision"], "source_revision", HEX40)
    license_id = source["license_id"]
    if not isinstance(license_id, str) or not LICENSE_ID.match(license_id) \
            or license_id.upper() in {"UNKNOWN", "NONE", "NOASSERTION"}:
        raise ValueError("source_license_id")
    _hex(source["license_sha256"], "source_license_sha256", HEX64)
    _hex(source["model_card_sha256"], "source_model_card_sha256", HEX64)

    weights = _exact_keys(root["weights"], WEIGHTS_FIELDS, "weights")
    if weights["format"] != "hf_snapshot":
        raise ValueError("weights_format")
    files = weights["files"]
    if not isinstance(files, list) or len(files) != len(MODEL_FILES):
        raise ValueError("weights_files_count")
    seen_names: set[str] = set()
    total_bytes = 0
    weight_count = 0
    for entry in files:
        row = _exact_keys(entry, WEIGHT_FILE_FIELDS, "weight_file")
        name = row["name"]
        if not isinstance(name, str) or name not in (
                REQUIRED_WEIGHT_NAMES | WEIGHT_FILE_NAMES):
            raise ValueError("weight_name")
        if name in seen_names:
            raise ValueError("weight_name_duplicate")
        seen_names.add(name)
        _hex(row["sha256"], "weight_sha256", HEX64)
        total_bytes += _exact_int(row["bytes"], "weight_bytes", 1,
                                  2_000_000_000)
        if name in WEIGHT_FILE_NAMES:
            weight_count += 1
    if not REQUIRED_WEIGHT_NAMES <= seen_names:
        raise ValueError("weights_required_name")
    if weight_count != 1:
        raise ValueError("weights_weight_file_count")
    if total_bytes > 8 * 1024 * 1024 * 1024:
        raise ValueError("weights_total_bytes")

    runtime = _exact_keys(root["runtime"], RUNTIME_FIELDS, "runtime")
    if runtime["python"] != "3.10":
        raise ValueError("runtime_python")
    if runtime["torch"] != "2.2.2":
        raise ValueError("runtime_torch")
    if runtime["transformers"] != "4.40.2":
        raise ValueError("runtime_transformers")
    if runtime["device"] != "cpu":
        raise ValueError("runtime_device")
    if _exact_int(runtime["threads"], "runtime_threads", 1, 64) != 1:
        raise ValueError("runtime_threads")
    for field in ("deterministic", "offline"):
        if runtime[field] is not True:
            raise ValueError("runtime_" + field)
    _hex(runtime["torch_wheel_sha256"], "runtime_torch_wheel_sha256", HEX64)
    _hex(runtime["transformers_wheel_sha256"],
         "runtime_transformers_wheel_sha256", HEX64)

    extractor = _exact_keys(
        root["feature_extractor"], FEATURE_EXTRACTOR_FIELDS,
        "feature_extractor")
    if extractor["kind"] != "wavlm_last_hidden_state":
        raise ValueError("feature_extractor_kind")
    if extractor["layer"] != "last":
        raise ValueError("feature_extractor_layer")
    if extractor["pooling"] != "mean_time":
        raise ValueError("feature_extractor_pooling")
    if extractor["normalize"] != "upstream_layer_norm":
        raise ValueError("feature_extractor_normalize")
    if _exact_int(extractor["sample_rate_hz"],
                  "feature_extractor_sample_rate_hz") != SAMPLE_RATE_HZ:
        raise ValueError("feature_extractor_sample_rate_hz")
    if _exact_int(extractor["window_samples"],
                  "feature_extractor_window_samples") != SAMPLES_PER_WINDOW:
        raise ValueError("feature_extractor_window_samples")
    dimension = _exact_int(extractor["feature_dim"],
                           "feature_extractor_feature_dim", 1, 4096)
    _hex(extractor["config_sha256"],
         "feature_extractor_config_sha256", HEX64)

    window_count = _validate_windows(root["windows"], dimension)

    head = _exact_keys(root["head"], HEAD_FIELDS, "head")
    if head["kind"] != "standardized_ridge":
        raise ValueError("head_kind")
    _fraction(head["alpha"], "head_alpha",
              Fraction(1, 1000), Fraction(1000))
    if head["scaler"] != "standard":
        raise ValueError("head_scaler")
    _hex(head["artifact_sha256"], "head_artifact_sha256", HEX64)

    outcomes = _exact_keys(root["outcomes"], OUTCOMES_FIELDS, "outcomes")
    _decimal_value(outcomes["mae_syllables_per_second"],
                   "outcome_mae", Fraction(0), Fraction(100))
    _decimal_value(outcomes["rmse_syllables_per_second"],
                   "outcome_rmse", Fraction(0), Fraction(100))
    _decimal_value(outcomes["bias_syllables_per_second"],
                   "outcome_bias", Fraction(-100), Fraction(100))
    _decimal_value(outcomes["pearson_r_squared"],
                   "outcome_r_squared", Fraction(-100), Fraction(100))
    if _exact_int(outcomes["nonfinite_count"],
                  "outcome_nonfinite_count", 0, 1_000_000) != 0:
        raise ValueError("outcome_nonfinite")
    if _exact_int(outcomes["window_count"],
                  "outcome_window_count", 1, 10000) != window_count:
        raise ValueError("outcome_window_count")
    if outcomes["qualified"] is not False:
        raise ValueError("outcome_self_qualified")

    rights = _exact_keys(root["rights"], RIGHTS_FIELDS, "rights")
    for field in RIGHTS_FIELDS:
        if rights[field] is not True:
            raise ValueError("rights_" + field)

    return {
        "admitted": True,
        "qualifies": False,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "cohort_id": root["cohort_id"],
        "window_count": window_count,
        "feature_dim": dimension,
        "manifest_digest": object_digest(root),
    }


def _synth(name: str) -> str:
    return hashlib.sha256(("synthetic:" + name).encode("ascii")).hexdigest()


def _base_manifest() -> dict[str, Any]:
    names = sorted(REQUIRED_WEIGHT_NAMES) + ["pytorch_model.bin"]
    return {
        "schema_id": SCHEMA_MANIFEST_ID,
        "cohort_id": "synthetic-schema-control",
        "source": {
            "repo_id": MODEL_REPO_ID,
            "revision": "a" * 40,
            "license_id": "LicenseRef-synthetic-control",
            "license_sha256": _synth("model-license"),
            "model_card_sha256": _synth("model-card"),
        },
        "weights": {
            "format": "hf_snapshot",
            "files": [{"name": name, "sha256": _synth("weight:" + name),
                       "bytes": 4096} for name in names],
        },
        "runtime": {
            "python": "3.10",
            "torch": "2.2.2",
            "transformers": "4.40.2",
            "device": "cpu",
            "threads": 1,
            "deterministic": True,
            "offline": True,
            "torch_wheel_sha256": _synth("torch-wheel"),
            "transformers_wheel_sha256": _synth("transformers-wheel"),
        },
        "feature_extractor": {
            "kind": "wavlm_last_hidden_state",
            "layer": "last",
            "pooling": "mean_time",
            "normalize": "upstream_layer_norm",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "window_samples": SAMPLES_PER_WINDOW,
            "feature_dim": 4,
            "config_sha256": _synth("feature-config"),
        },
        "windows": [
            {
                "id": f"w{index:03d}",
                "start_sample": index * SAMPLES_PER_WINDOW,
                "end_sample": (index + 1) * SAMPLES_PER_WINDOW,
                "features": [f"{index + column}.500000000"
                             for column in range(4)],
                "label_rate_sps": f"{4 + index}/4",
            }
            for index in range(TOTAL_MANIFEST_WINDOWS)
        ],
        "head": {
            "kind": "standardized_ridge",
            "alpha": "10/1",
            "scaler": "standard",
            "artifact_sha256": _synth("head-artifact"),
        },
        "outcomes": {
            "mae_syllables_per_second": "0.250000000",
            "rmse_syllables_per_second": "0.300000000",
            "bias_syllables_per_second": "-0.050000000",
            "pearson_r_squared": "0.800000000",
            "nonfinite_count": 0,
            "window_count": TOTAL_MANIFEST_WINDOWS,
            "qualified": False,
        },
        "rights": {field: True for field in RIGHTS_FIELDS},
    }


def _mutations() -> list[tuple[str, str, Any]]:
    def setter(path: tuple[Any, ...], value: Any):
        def apply(manifest: dict[str, Any]) -> None:
            target: Any = manifest
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
        return apply

    def deleter(path: tuple[str, ...]):
        def apply(manifest: dict[str, Any]) -> None:
            target: Any = manifest
            for key in path[:-1]:
                target = target[key]
            del target[path[-1]]
        return apply

    def duplicate_window(manifest: dict[str, Any]) -> None:
        manifest["windows"][1]["id"] = manifest["windows"][0]["id"]

    return [
        ("manifest_missing_rights", "manifest_fields",
         deleter(("rights",))),
        ("manifest_unknown_field", "manifest_fields",
         setter(("extra",), True)),
        ("manifest_schema", "manifest_schema_id",
         setter(("schema_id",), "audio-sdk/other/0.1")),
        ("manifest_cohort", "manifest_cohort_id",
         setter(("cohort_id",), "Bad Cohort")),
        ("source_unknown_field", "source_fields",
         setter(("source", "extra"), "x")),
        ("source_repo", "source_repo_id",
         setter(("source", "repo_id"), "microsoft/wavlm-large")),
        ("source_revision_short", "source_revision_malformed",
         setter(("source", "revision"), "a" * 39)),
        ("source_revision_upper", "source_revision_malformed",
         setter(("source", "revision"), "A" * 40)),
        ("source_license_null", "source_license_id",
         setter(("source", "license_id"), None)),
        ("source_license_unknown", "source_license_id",
         setter(("source", "license_id"), "UNKNOWN")),
        ("source_license_empty", "source_license_id",
         setter(("source", "license_id"), "")),
        ("source_license_digest", "source_license_sha256_malformed",
         setter(("source", "license_sha256"), "z" * 64)),
        ("weights_format", "weights_format",
         setter(("weights", "format"), "pytorch_state_dict")),
        ("weights_empty", "weights_files_count",
         setter(("weights", "files"), [])),
        ("weights_missing_file", "weights_files_count",
         lambda manifest: manifest["weights"]["files"].pop()),
        ("weight_unknown_name", "weight_name",
         setter(("weights", "files", 0, "name"), "extra.bin")),
        ("weight_traversal", "weight_name",
         setter(("weights", "files", 0, "name"), "../README.md")),
        ("weight_duplicate", "weight_name_duplicate",
         lambda manifest: manifest["weights"]["files"][1].update(
             {"name": manifest["weights"]["files"][0]["name"]})),
        ("weight_zero_bytes", "weight_bytes_below_minimum",
         setter(("weights", "files", 0, "bytes"), 0)),
        ("weight_bad_digest", "weight_sha256_malformed",
         setter(("weights", "files", 0, "sha256"), "A" * 64)),
        ("weights_missing_required", "weights_required_name",
         setter(("weights", "files", 2, "name"), "model.safetensors")),
        ("runtime_unknown_field", "runtime_fields",
         setter(("runtime", "extra"), "x")),
        ("runtime_python", "runtime_python",
         setter(("runtime", "python"), "3.9")),
        ("runtime_torch", "runtime_torch",
         setter(("runtime", "torch"), "2.3.0")),
        ("runtime_transformers", "runtime_transformers",
         setter(("runtime", "transformers"), "4.41.0")),
        ("runtime_device", "runtime_device",
         setter(("runtime", "device"), "cuda")),
        ("runtime_threads_zero", "runtime_threads_below_minimum",
         setter(("runtime", "threads"), 0)),
        ("runtime_threads_two", "runtime_threads",
         setter(("runtime", "threads"), 2)),
        ("runtime_threads_float", "runtime_threads_not_int",
         setter(("runtime", "threads"), 1.0)),
        ("runtime_deterministic", "runtime_deterministic",
         setter(("runtime", "deterministic"), False)),
        ("runtime_offline", "runtime_offline",
         setter(("runtime", "offline"), False)),
        ("runtime_wheel_digest", "runtime_torch_wheel_sha256_malformed",
         setter(("runtime", "torch_wheel_sha256"), "x" * 64)),
        ("feature_unknown_field", "feature_extractor_fields",
         setter(("feature_extractor", "extra"), "x")),
        ("feature_kind", "feature_extractor_kind",
         setter(("feature_extractor", "kind"), "wav2vec2_hidden_state")),
        ("feature_layer", "feature_extractor_layer",
         setter(("feature_extractor", "layer"), "second")),
        ("feature_pooling", "feature_extractor_pooling",
         setter(("feature_extractor", "pooling"), "max_time")),
        ("feature_normalize", "feature_extractor_normalize",
         setter(("feature_extractor", "normalize"), "none")),
        ("feature_rate", "feature_extractor_sample_rate_hz",
         setter(("feature_extractor", "sample_rate_hz"), 8000)),
        ("feature_window", "feature_extractor_window_samples",
         setter(("feature_extractor", "window_samples"), 32000)),
        ("feature_dim_zero", "feature_extractor_feature_dim_below_minimum",
         setter(("feature_extractor", "feature_dim"), 0)),
        ("feature_config_digest", "feature_extractor_config_sha256_malformed",
         setter(("feature_extractor", "config_sha256"), "z" * 64)),
        ("windows_empty", "windows_count",
         setter(("windows",), [])),
        ("window_unknown_field", "window_fields",
         setter(("windows", 0, "extra"), "x")),
        ("window_id_bad", "window_id",
         setter(("windows", 0, "id"), "W 0")),
        ("window_id_duplicate", "window_id_duplicate",
         duplicate_window),
        ("window_start_bool", "window_start_not_int",
         setter(("windows", 0, "start_sample"), True)),
        ("window_start_negative", "window_start_below_minimum",
         setter(("windows", 0, "start_sample"), -160)),
        ("window_start_misaligned", "window_start_misaligned",
         setter(("windows", 1, "start_sample"), 64001)),
        ("window_end_misaligned", "window_end_misaligned",
         setter(("windows", 0, "end_sample"), 63999)),
        ("window_length", "window_length",
         setter(("windows", 1, "end_sample"), 128160)),
        ("window_contiguous", "window_contiguous",
         setter(("windows", 1, "start_sample"), 64160)),
        ("window_feature_count", "window_feature_count",
         lambda manifest: manifest["windows"][0]["features"].pop()),
        ("window_feature_nan", "window_feature_malformed",
         setter(("windows", 0, "features", 0), "NaN")),
        ("window_feature_inf", "window_feature_malformed",
         setter(("windows", 0, "features", 0), "Infinity")),
        ("window_feature_float", "window_feature_not_string",
         setter(("windows", 0, "features", 0), 0.5)),
        ("window_feature_leading_zero", "window_feature_malformed",
         setter(("windows", 0, "features", 0), "00.500000000")),
        ("window_rate_nan", "window_rate_malformed",
         setter(("windows", 0, "label_rate_sps"), "NaN")),
        ("window_rate_zero", "window_rate_out_of_range",
         setter(("windows", 0, "label_rate_sps"), "0/1")),
        ("window_rate_negative", "window_rate_malformed",
         setter(("windows", 0, "label_rate_sps"), "-1/2")),
        ("window_rate_high", "window_rate_out_of_range",
         setter(("windows", 0, "label_rate_sps"), "21/1")),
        ("head_unknown_field", "head_fields",
         setter(("head", "extra"), "x")),
        ("head_kind", "head_kind",
         setter(("head", "kind"), "ridge")),
        ("head_alpha_zero", "head_alpha_out_of_range",
         setter(("head", "alpha"), "0/1")),
        ("head_scaler", "head_scaler",
         setter(("head", "scaler"), "none")),
        ("head_digest", "head_artifact_sha256_malformed",
         setter(("head", "artifact_sha256"), "z" * 64)),
        ("outcomes_unknown_field", "outcomes_fields",
         setter(("outcomes", "extra"), "x")),
        ("outcome_nonfinite", "outcome_nonfinite",
         setter(("outcomes", "nonfinite_count"), 1)),
        ("outcome_mae_nan", "outcome_mae_malformed",
         setter(("outcomes", "mae_syllables_per_second"), "NaN")),
        ("outcome_mae_negative", "outcome_mae_out_of_range",
         setter(("outcomes", "mae_syllables_per_second"), "-0.500000000")),
        ("outcome_r2_high", "outcome_r_squared_out_of_range",
         setter(("outcomes", "pearson_r_squared"), "101.000000000")),
        ("outcome_window_count", "outcome_window_count",
         setter(("outcomes", "window_count"), 3)),
        ("outcome_self_qualified", "outcome_self_qualified",
         setter(("outcomes", "qualified"), True)),
        ("rights_model_terms", "rights_model_terms_reviewed",
         setter(("rights", "model_terms_reviewed"), False)),
        ("rights_commercial", "rights_commercial_use_approved",
         setter(("rights", "commercial_use_approved"), False)),
    ]


def admission_controls() -> dict[str, Any]:
    base = _base_manifest()
    control = validate_manifest(base)
    rejected: list[dict[str, Any]] = []
    for case_id, code, mutate in _mutations():
        candidate = json.loads(json.dumps(base))
        mutate(candidate)
        try:
            validate_manifest(candidate)
        except ValueError as error:
            actual = str(error)
            rejected.append({
                "id": case_id,
                "status": "rejected",
                "code": actual,
                "expected_code": code,
                "qualifies": False,
                "state_unchanged": True,
            })
        else:
            rejected.append({
                "id": case_id,
                "status": "unexpectedly_admitted",
                "code": "",
                "expected_code": code,
                "qualifies": False,
                "state_unchanged": False,
            })
    rejected.sort(key=lambda row: row["id"])
    all_rejected = all(row["status"] == "rejected" for row in rejected)
    codes_match = all(row["code"] == row["expected_code"]
                      for row in rejected)
    return {
        "control": {
            "id": "synthetic_schema_control",
            "accepted": True,
            "admitted": bool(control["admitted"]),
            "qualifies": False,
            "evidence_class": control["evidence_class"],
            "window_count": control["window_count"],
            "feature_dim": control["feature_dim"],
            "manifest_digest": control["manifest_digest"],
        },
        "cases": rejected,
        "summary": {
            "case_count": len(rejected),
            "rejected_count": sum(1 for row in rejected
                                  if row["status"] == "rejected"),
            "all_rejected": all_rejected,
            "all_codes_match": codes_match,
            "accepted_schema_controls": 1,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "runtime_invoked": False,
            "audio_read": False,
            "weights_loaded": False,
            "model_executed": False,
            "network_used": False,
        },
    }


# ---------------------------------------------------------------------------
# Contract and report
# ---------------------------------------------------------------------------

def _scope() -> dict[str, Any]:
    return {
        "task_local_only": True,
        "directory": TASK_PREFIX,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "default_selected": False,
        "benchmark_claim": False,
        "release_claim": False,
        "network_used": False,
        "download_attempted": False,
        "weights_copied": False,
        "runtime_imported": False,
        "model_executed": False,
        "audio_read": False,
        "listening_conducted": False,
        "device_timing_measured": False,
        "benchmark_run": False,
    }


def _boundary() -> dict[str, Any]:
    return {
        "installed_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
            "unchanged": True,
        },
        "provider_or_abi_change": False,
        "descriptor_or_registry_change": False,
        "default_change": False,
        "shared_build_or_ci_change": False,
        "board_or_handoff_change": False,
        "external_assets_copied": False,
    }


def _non_claims() -> list[str]:
    return [
        "No result in this package is a qualification, benchmark or release.",
        "The documented WavLM rate MAE/RMSE/r and encoder p95 are provenance "
        "only; they were not remeasured or reproduced here.",
        "No WavLM weight, snapshot, config, tokenizer or feature archive is "
        "loaded, parsed, scored or promoted by this package.",
        "No PyTorch or Transformers runtime is installed, imported or executed.",
        "The model card records no license value; no model, weight, notice or "
        "output-use grant was reviewed or found.",
        "No rights-cleared corpus, consent record, human syllable label or "
        "speaker/meeting-held-out cohort is present.",
        "The standardized-ridge arithmetic control uses deterministic synthetic "
        "fractions only and is not speech, encoder or accuracy evidence.",
        "No listening, device timing, resource, benchmark or release result "
        "exists.",
        "A syllables/second estimate is not a preferred speed factor, a TSM "
        "setting or a product policy.",
        "No provider, descriptor, registry, default, installed-v0, ABI, "
        "shared-build, CI, board or handoff file is changed.",
    ]


def _required_results() -> dict[str, bool]:
    return {
        "upstream_revision_and_license_admitted": False,
        "weight_snapshot_and_redistribution_admitted": False,
        "pinned_runtime_archive_lock_and_license_admitted": False,
        "rights_cleared_cohort_and_labels_present": False,
        "real_fp32_encoder_and_ridge_reproduced": False,
        "external_accuracy_generalization_measured": False,
        "rate_profile_mapping_buffering_and_preservation_measured": False,
        "listening_measured": False,
        "device_timing_measured": False,
        "provider_intake_approved": False,
        "release_approved": False,
        "no_result_qualifies": True,
    }


def _required_artifacts() -> list[dict[str, Any]]:
    presence = source_presence()
    markers = license_marker_probe()
    return [
        {
            "id": "A01",
            "name": "research source record, runner, manifest and derived "
                    "embedding archive",
            "present": True,
            "verified": True,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "path": "research/tsm-followup-20261101/agent-neural/run",
            "file_count": 8,
            "sha256": None,
            "blocker": "BLK-01",
        },
        {
            "id": "A02",
            "name": "microsoft/wavlm-base-plus weight snapshot",
            "present": presence["weights_present"],
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "file_count": presence["model_weight_file_count"],
            "tree_sha256": MODEL_TREE_SHA256,
            "sha256": None,
            "blocker": "BLK-01",
        },
        {
            "id": "A03",
            "name": "pinned offline PyTorch/Transformers runtime",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-03",
        },
        {
            "id": "A04",
            "name": "model card, LICENSE/NOTICE bundle and written terms",
            "present": bool(markers["model_license_marker_files"]),
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-02",
        },
        {
            "id": "A05",
            "name": "rights-cleared frozen corpus with consent",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-04",
        },
        {
            "id": "A06",
            "name": "checked syllable-rate labels and timestamp provenance",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-04",
        },
        {
            "id": "A07",
            "name": "reproduced FP32 encoder plus ridge result and controls",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-05",
        },
        {
            "id": "A08",
            "name": "target-device timing and resource record",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-06",
        },
        {
            "id": "A09",
            "name": "rate-profile mapping, buffering and preservation record",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-06",
        },
        {
            "id": "A10",
            "name": "opt-in provider intake and release review",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-06",
        },
    ]


def _exact_blockers() -> list[dict[str, Any]]:
    return [
        {
            "id": "BLK-01",
            "artifact_id": "A01",
            "linked_gates": ["RG-01", "RG-02"],
            "status": "open",
            "qualifies": False,
            "missing": (
                "The exact microsoft/wavlm-base-plus weight snapshot is absent. "
                "The research source record pins revision "
                "4c66d4806a428f2e922ccfa1a962776e232d487b and "
                "pytorch_model.bin at 377,617,425 bytes / SHA-256 3bb273a6..., "
                "but no local snapshot exists in the data/model probes or the "
                "Hugging Face cache. No weight was downloaded or "
                "reconstructed. The research runner and derived embeddings are "
                "pinned as provenance only and are not loaded or scored."),
            "required_action": (
                "Supply the immutable upstream snapshot at the exact revision "
                "with every file's byte count and SHA-256, and keep it "
                "read-only during qualification."),
        },
        {
            "id": "BLK-02",
            "artifact_id": "A04",
            "linked_gates": ["RG-01", "RG-02"],
            "status": "open",
            "qualifies": False,
            "missing": (
                "The model card records no license value (the source record "
                "sets license=null). No LICENSE/NOTICE/model-card text, "
                "redistribution permission, commercial-use permission or "
                "generated-output-use decision is staged or reviewed."),
            "required_action": (
                "Supply the complete model card, license/notice bundle and a "
                "written rights decision covering redistribution, commercial "
                "use and generated-output use; then record an independent "
                "terms review."),
        },
        {
            "id": "BLK-03",
            "artifact_id": "A03",
            "linked_gates": ["RG-03"],
            "status": "open",
            "qualifies": False,
            "missing": (
                "No pinned offline runtime is present. Qualification requires "
                "Python 3.10.13 with torch 2.2.2 and transformers 4.40.2 on CPU "
                "with one intra-op/one inter-op thread and deterministic "
                "settings. None of the available interpreters exposes torch or "
                "transformers, and no wheel hashes, lockfile, isolated install "
                "or offline load record exists."),
            "required_action": (
                "Supply a locked offline environment with exact interpreter, "
                "wheel hashes, install/import digest, CPU thread settings and "
                "deterministic flags, then perform a clean-room load."),
        },
        {
            "id": "BLK-04",
            "artifact_id": "A05",
            "linked_gates": ["RG-04", "RG-06"],
            "status": "open",
            "qualifies": False,
            "missing": (
                "No rights-cleared frozen rate cohort is staged. The historical "
                "pilot is 210 four-second windows from one AMI EN2003a meeting "
                "with transcript-plus-CMUdict syllable labels, not human "
                "syllable-nucleus labels, and AMI/CMUdict terms are not "
                "reviewed for this package."),
            "required_action": (
                "Freeze a permitted, speaker/meeting-disjoint cohort with "
                "reviewed corpus and dictionary terms, independent syllable "
                "labels, language/speaker groups and source-timestamp "
                "provenance."),
        },
        {
            "id": "BLK-05",
            "artifact_id": "A07",
            "linked_gates": ["RG-05", "RG-06"],
            "status": "open",
            "qualifies": False,
            "missing": (
                "No FP32 WavLM encoder plus ridge-head result was reproduced. "
                "The recorded MAE .609 syll/s, RMSE .760, r .849 and encoder "
                "p95 462 ms are quoted context only; the derived embedding "
                "archive is not loaded, scored or promoted, and no adverse, "
                "missing or nonfinite control was exercised against the real "
                "encoder."),
            "required_action": (
                "Reproduce the exact encoder and ridge head on the qualified "
                "cohort with frozen folds and scorer, reporting accuracy, "
                "bias, correlation, nonfinite/output checks and identity and "
                "constant baselines."),
        },
        {
            "id": "BLK-06",
            "artifact_id": "A09",
            "linked_gates": ["RG-07", "RG-08"],
            "status": "open",
            "qualifies": False,
            "missing": (
                "No Rate-profile integration, device timing, listening or "
                "provider intake exists. There is no measured source/output "
                "mapping, duration, pitch, transient, buffering, rebuffer, "
                "drift, final-partial-window or speech-preservation result; "
                "the historical encoder p95 is host context, not a device "
                "deadline result."),
            "required_action": (
                "After model/data/runtime/quality gates clear, measure the "
                "exact target-device paced workload and the full Rate profile, "
                "then open a separate OFF-by-default versioned provider intake "
                "with independent exact-head review."),
        },
    ]


def _rate_profile_rows() -> list[dict[str, Any]]:
    return [
        {"id": "RATE-01", "requirement": "1× control", "status": "blocked",
         "qualifies": False,
         "evidence": "No measured 1× playback or estimator-to-policy control."},
        {"id": "RATE-02",
         "requirement": "source/output mapping and rate changes",
         "status": "blocked", "qualifies": False,
         "evidence": "The candidate estimates syllables/second; no source-to-"
                     "output mapping or rate change was measured."},
        {"id": "RATE-03", "requirement": "duration identity and error",
         "status": "blocked", "qualifies": False,
         "evidence": "No rendered output duration exists for a real rate path."},
        {"id": "RATE-04", "requirement": "pitch", "status": "blocked",
         "qualifies": False,
         "evidence": "No stretched waveform or pitch measurement exists."},
        {"id": "RATE-05", "requirement": "transient audibility",
         "status": "blocked", "qualifies": False,
         "evidence": "No waveform, listening or transient analysis exists."},
        {"id": "RATE-06",
         "requirement": "playback buffering, rebuffer and drift",
         "status": "blocked", "qualifies": False,
         "evidence": "No device clock, buffering, fill/flush or drift run "
                     "exists."},
        {"id": "RATE-07",
         "requirement": "unfamiliar speech, music and silence",
         "status": "blocked", "qualifies": False,
         "evidence": "No rights-cleared stratified corpus exists; the "
                     "historical pilot is one meeting of speech."},
        {"id": "RATE-08",
         "requirement": "final partial window and speech preservation",
         "status": "blocked", "qualifies": False,
         "evidence": "No final partial window, source-timestamp pause/filler "
                     "decision or preservation score exists."},
    ]


def _rate_outcomes() -> list[dict[str, Any]]:
    return [{
        "id": row["id"].replace("RATE", "OUT"),
        "requirement": row["requirement"],
        "status": "blocked",
        "value": None,
        "qualifies": False,
    } for row in _rate_profile_rows()]


def _release_gates(projection: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        ("RG-01", "source_revision_model_card_and_license",
         "Pin the exact upstream revision/tree, complete model card and "
         "license/notice set, and record an independent terms and output-use "
         "review."),
        ("RG-02", "weight_snapshot_and_redistribution_rights",
         "Supply the immutable four-file snapshot with byte counts and "
         "SHA-256, plus a written redistribution and product-use decision."),
        ("RG-03", "pinned_offline_runtime",
         "Provide Python 3.10.13, torch 2.2.2 and transformers 4.40.2 wheel "
         "digests, a lockfile, one intra-op/one inter-op CPU thread, "
         "deterministic flags, an offline install and a load proof."),
        ("RG-04", "rights_cleared_cohort_and_labels",
         "Freeze a consented, speaker/meeting-disjoint cohort with reviewed "
         "corpus/dictionary terms, independent syllable labels and source "
         "timestamps."),
        ("RG-05", "frozen_encoder_and_ridge_reproduction",
         "Reproduce the exact frozen WavLM encoder plus standardized ridge "
         "head on the qualified cohort with frozen folds, accuracy/bias/"
         "correlation, nonfinite, identity and constant controls."),
        ("RG-06", "external_accuracy_generalization",
         "Score the exact artifact on a reviewed multi-speaker/multi-meeting "
         "corpus with pre-agreed MAE/RMSE/r margins; single-meeting synthetic "
         "or recorded context is insufficient."),
        ("RG-07", "rate_profile_mapping_buffering_and_preservation",
         "Measure source/output mapping, 1x/rate-change, duration, pitch, "
         "transient, buffering, rebuffer, drift, final partial window and "
         "speech preservation with source-timestamp-tied decisions."),
        ("RG-08", "provider_intake_device_timing_and_release",
         "Measure target-device timing/resources/deadlines and open a separate "
         "versioned OFF-by-default provider intake with independent exact-head "
         "review."),
    ]
    return [{"id": gate_id, "title": title, "status": "blocked",
             "qualifies": False, "reopen_condition": condition,
             "linked_row": dict(projection)}
            for gate_id, title, condition in rows]


def _documented_context() -> dict[str, Any]:
    return {
        "evidence_class": "source_reported_not_reproduced_here",
        "qualifies": False,
        "source": "research/tsm-followup-20261101/README.md line 30",
        "repo_id": MODEL_REPO_ID,
        "revision": MODEL_REVISION,
        "license": None,
        "parameter_count": "94381936",
        "weight_bytes": 377617425,
        "serialized_model_bytes": 377623776,
        "reported": {
            "rate_mae_syllables_per_second": "0.609",
            "rate_rmse_syllables_per_second": "0.760",
            "pearson_r": "0.849",
            "spearman_rho": "0.844",
            "encoder_p95_ms_per_4s_clip": "462.14",
            "encoder_mean_ms_per_4s_clip": "255.75",
            "encoder_rtf": "0.0639",
            "window_count": 210,
            "meeting_count": 1,
            "fold_count": 5,
        },
        "feature_and_head": (
            "mean-pooled last hidden layer; StandardScaler + Ridge(alpha=10) "
            "re-fit per chronological fold"),
        "limitations": [
            "one AMI meeting only",
            "transcript/CMUdict syllables, not human syllable nuclei",
            "no preferred-speed or product-policy label",
            "CPU host timing excludes load and feature normalization",
            "the model card has no license value",
        ],
        "reproduced_here": False,
        "weights_used_here": False,
        "runtime_imported_here": False,
        "audio_read_here": False,
    }


def _reproduction() -> dict[str, Any]:
    return {
        "python": "3.12 or newer, standard library only",
        "commands": [
            "export PYTHONDONTWRITEBYTECODE=1",
            "python3 run.py all",
            "python3 -m unittest -v test_reference.py",
            "python3 verify.py",
        ],
        "repeat_count": 3,
        "byte_identical_required": True,
        "network_used": False,
    }


def build_contract() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    source_pins, boundary_pins = verify_pins()
    presence = source_presence()
    markers = license_marker_probe()
    return {
        "contract_id": CONTRACT_ID,
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": {
            "decision": "DEFER",
            "status": "incomplete",
            "proposal_only": True,
            "qualification_status": "not_qualified",
            "blocked_before": "implementation_or_intake",
            "qualifying_results": 0,
            "blocked_release_gates": 8,
        },
        "qualification": {
            "status": "not_qualified",
            "evidence_status": "incomplete",
            "proposal_only": True,
            "qualifying_results": 0,
            "blocked_release_gates": 8,
            "open_blockers": 6,
            "source_metadata_present": True,
            "weights_present": presence["weights_present"],
            "runtime_present": False,
            "license_present": False,
            "licensed_artifact_set_present": False,
            "real_result_present": False,
            "reasons": [
                "no WavLM weight snapshot is present",
                "the model card records no license value",
                "no pinned offline PyTorch/Transformers runtime is present",
                "no rights-cleared cohort or checked syllable labels",
                "no reproduced encoder/ridge result or adverse controls",
                "no rate-profile, listening, device-timing or release result",
            ],
        },
        "scope": _scope(),
        "boundary": _boundary(),
        "public_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
        },
        "non_claims": _non_claims(),
        "profile_phrases": list(PROFILE_PHRASES),
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "source_presence": presence,
        "license_findings": markers,
        "exact_model": {
            "repo_id": MODEL_REPO_ID,
            "revision": MODEL_REVISION,
            "license": None,
            "files": {
                name: {"byte_count": MODEL_FILE_BYTES[name],
                       "sha256": MODEL_FILES[name]}
                for name in sorted(MODEL_FILES)
            },
            "tree_sha256": MODEL_TREE_SHA256,
            "parameter_count": "94381936",
            "serialized_model_bytes": 377623776,
            "weight_bytes": 377617425,
            "weight_sha256": MODEL_FILES["pytorch_model.bin"],
            "files_documented_locally_verified": False,
            "locally_present": presence["weights_present"],
            "downloaded_or_reconstructed": False,
        },
        "observed_provenance": {
            "documented_context": _documented_context(),
            "ridge_control": ridge_control(),
        },
        "required_artifacts": _required_artifacts(),
        "exact_blockers": _exact_blockers(),
        "release_gates": _release_gates(projection),
        "rate_profile_requirements": _rate_profile_rows(),
        "rate_outcomes": _rate_outcomes(),
        "required_results": _required_results(),
        "linked_row_projection": projection,
        "linked_row_fields": list(BOARD_ROW_FIELDS),
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "reproduction": _reproduction(),
    }


def build_report() -> dict[str, Any]:
    contract = build_contract()
    contract_sha = object_digest(contract)
    source_pins, boundary_pins = verify_pins()
    presence = source_presence()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "contract_sha256": contract_sha,
        "disposition": contract["disposition"],
        "qualification": contract["qualification"],
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "non_claims": contract["non_claims"],
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "source_presence": presence,
        "license_findings": contract["license_findings"],
        "exact_model": contract["exact_model"],
        "observed_provenance": contract["observed_provenance"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "rate_profile": {
            "profile": PROFILE,
            "profile_label": PROFILE_LABEL,
            "source": contract["profile_source"],
            "rows": contract["rate_profile_requirements"],
        },
        "rate_outcomes": {"rows": contract["rate_outcomes"]},
        "admission": admission_controls(),
        "linked_row_identity": {
            "projection": contract["linked_row_projection"],
            "sha256": board_row_digest(contract["linked_row_projection"]),
            "fields": contract["linked_row_fields"],
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "linked_rows": contract["linked_rows"],
            "linked_rows_sha256": contract["linked_rows_sha256"],
        },
        "required_results": contract["required_results"],
        "reproduction": contract["reproduction"],
    }


def validate_contract(contract: Any) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    required = (
        "contract_id", "schema_id", "task", "component", "decision", "status",
        "qualification_status", "proposal_only", "qualification",
        "release_gates", "exact_blockers", "required_artifacts",
        "rate_profile_requirements", "rate_outcomes", "linked_row_projection",
        "board_file_pinned",
    )
    for field in required:
        if field not in contract:
            raise ValueError("contract_field_missing:" + field)
    if contract["task"] != TASK:
        raise ValueError("contract_task")
    if contract["component"] != COMPONENT_ID:
        raise ValueError("contract_component")
    if contract["decision"] != "DEFER" \
            or contract["status"] != "incomplete" \
            or contract["qualification_status"] != "not_qualified" \
            or contract["proposal_only"] is not True:
        raise ValueError("contract_disposition")
    gates = contract["release_gates"]
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gates")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}" \
                or gate.get("status") != "blocked" \
                or gate.get("qualifies") is not False:
            raise ValueError("contract_gate:" + str(index))
    if len(contract["exact_blockers"]) != 6:
        raise ValueError("contract_blockers")
    if contract["board_file_pinned"] is not False:
        raise ValueError("contract_board_pinned")
    if BOARD_TASK_ROW in contract["source_pins"] \
            or BOARD_TASK_ROW in contract["boundary_pins"]:
        raise ValueError("mutable_board_pinned")


def verify_sources_manifest(payload: bytes) -> None:
    lines = payload.decode("ascii").splitlines()
    if not lines or not lines[0].startswith("# SHA-256 pins for"):
        raise ValueError("sources_header")
    seen: set[str] = set()
    for line in lines:
        if not line or line.startswith("#"):
            continue
        digest, name = line.split("  ", 1)
        if not HEX64.match(digest):
            raise ValueError("sources_digest")
        if name in seen:
            raise ValueError("sources_duplicate")
        seen.add(name)
    prefixed = {"source:" + name for name in SOURCE_PINS}
    prefixed |= set(BOUNDARY_PINS)
    prefixed |= {TASK_PREFIX + name for name in (
        "LICENSES.md", "README.md", "SOURCES.sha256.license",
        "contract.json", "contract.json.license", "reference.py",
        "report.json", "report.json.license", "report.json.sha256",
        "report.json.sha256.license", "run.py", "test_reference.py",
        "verify.py")}
    if seen != prefixed:
        raise ValueError("sources_set")
    if TASK_PREFIX + "SOURCES.sha256" in seen:
        raise ValueError("sources_self_pinned")
