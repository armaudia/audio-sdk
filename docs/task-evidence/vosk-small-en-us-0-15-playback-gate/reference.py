# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local DEFER evidence for SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE.

Standard-library only and deterministic. This module never imports, loads or
executes Vosk, Kaldi, ``libvosk``, a model directory, audio or a network client.
It records the exact present-but-unlicensed model/runtime provenance, the missing
rights and qualification artifacts, a fail-closed caller-manifest admission
boundary, and one explicitly synthetic gate-policy arithmetic control that is
labelled ``synthetic_contract_control_not_evidence`` and can never qualify.

The model tree and the Python runtime are present only in a mutable, git-ignored
prototype environment outside this worktree. Presence is pinned by SHA-256 but
is not admitted: there is no model ``LICENSE``/``NOTICE``/model card, no written
model grant, no official archive identity, no source checkout, no pinned wheel
archive or lock, and no reviewed output-use decision. Nothing is copied here.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE"
COMPONENT_ID = "vosk-small-en-us-0-15-playback-gate"
TASK_TITLE = "Vosk small-en-us-0.15 playback gate"
CONTRACT_ID = "audio-sdk/vosk-small-en-us-0-15-playback-gate/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "implementation"
BASE_COMMIT = "8bd03e2d9d08d550bb4b2ac28425c71eaf8a0ba9"
BRANCH = "swarm/SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE"
REVIEWER = "reviewer-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE"
TASK_PREFIX = "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/"
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = (
    "id", "title", "repository", "mode", "depends_on", "component", "evidence")

MODEL_PREFIX = (
    "cpp-library/pipeline-validation/playback-speed/models/"
    "vosk-model-small-en-us-0.15")
RUNTIME_PREFIX = (
    "cpp-library/pipeline-validation/playback-speed/.venv/lib/"
    "python3.11/site-packages/vosk")
DIST_PREFIX = (
    "cpp-library/pipeline-validation/playback-speed/.venv/lib/"
    "python3.11/site-packages/vosk-0.3.44.dist-info")
PLAYBACK_PREFIX = "cpp-library/pipeline-validation/playback-speed"

MODEL_FILES = {
    "README": "c0cf286e4f7783306c5f6469b37db69228fb16803b03cae661edb2d7bba64ebb",
    "am/final.mdl": "75370a0137f9daf8f469dedd7daa4513ae7a621f03240c6e512e2b50b656a7b6",
    "conf/mfcc.conf": "1e2228006d01d805ad1c267fee9f79709ca87ac51bd82b0e3f5c69ba543f0fc4",
    "conf/model.conf": "8f14cb1eeb07c762c371db648c6be688d347236155ca0f64fb13b6567a8ce81f",
    "graph/Gr.fst": "023c8b7e30704a9e37765c635c252e608a02f361235bf94abdcf2a5225d85b20",
    "graph/HCLr.fst": "5caafba3081e1646545ac6bff0dd7a318e53dcbdc86f237909ce1d2ac1293d34",
    "graph/disambig_tid.int": "9ad87cc166d0998f08f758f47a6223a120dfffcbee805c4849c3aa5e6bb3c0fc",
    "graph/phones/word_boundary.int": "da199d9c991e0e84681ddbb34627b915b26302d50a8fdaa23c51e2bc3a50b5c3",
    "ivector/final.dubm": "8c5d7dd69d2122313baaf19f61f35dd3fa18b70c62ac0687e311e1c46e6daca7",
    "ivector/final.ie": "3f37faf90c375b9e4740b569398b5829ed9cc07d19be6d441f72c3b71d7efcc6",
    "ivector/final.mat": "ddd83586dc5f928cda8738b922c85ffe38fc789cb5f9151a712ca12f37265382",
    "ivector/global_cmvn.stats": "33be09afcc80059847a275c3d043b51f1ab954c7c2438ddbbf4745e8ba144ff9",
    "ivector/online_cmvn.conf": "a2f3571754b64297cb7efb2e7ca3df61995c5a45fcbb97188f90613552bb2dfe",
    "ivector/splice.conf": "9f0c5f7c82d18eaf25d8bce470efa9f7741f88411fe428774bc0a9bb69a24756",
}
MODEL_FILE_BYTES = {
    "README": 199,
    "am/final.mdl": 15962575,
    "conf/mfcc.conf": 131,
    "conf/model.conf": 290,
    "graph/Gr.fst": 24013795,
    "graph/HCLr.fst": 22416994,
    "graph/disambig_tid.int": 102,
    "graph/phones/word_boundary.int": 1761,
    "ivector/final.dubm": 168048,
    "ivector/final.ie": 8288887,
    "ivector/final.mat": 44975,
    "ivector/global_cmvn.stats": 1080,
    "ivector/online_cmvn.conf": 95,
    "ivector/splice.conf": 35,
}

SOURCE_PINS: dict[str, str] = {
    **{MODEL_PREFIX + "/" + name: digest
       for name, digest in MODEL_FILES.items()},
    RUNTIME_PREFIX + "/__init__.py":
        "3e29f285cdeec3793ab3c566e9205db1bc26ef75f1bd8b9781728f90841f96d7",
    RUNTIME_PREFIX + "/vosk_cffi.py":
        "94180ec83bd96eee4ef8835ef3fea6d2a955ff1dc8bdb69d5b398727007e6478",
    RUNTIME_PREFIX + "/libvosk.dyld":
        "82fdfba0dde392a7dbba70f9c1a17f6e3da27a50444a9f53939508525a1e6fdf",
    DIST_PREFIX + "/METADATA":
        "ea20f0c3c548e68d9b08ccc2a9aa5fef42754915a70d5e67098e2dcd6bec4746",
    DIST_PREFIX + "/RECORD":
        "26069e235f04cac8337303cd31d01999016e076290a38af26ef3b2c9e65f2593",
    DIST_PREFIX + "/WHEEL":
        "96da1ac11905129e2c1720e4d53e5dcf6205962b29d934ee97a8702b096504d0",
    PLAYBACK_PREFIX + "/README.md":
        "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f",
    PLAYBACK_PREFIX + "/generate_corpus.py":
        "05442e1be54d7a408eac55c62ac6eb48fdee3f76543602228bf6ec61a0e96a27",
    PLAYBACK_PREFIX + "/run_validation.py":
        "d9b7eacf76cfbcb623e79eda3a0577ceb4b0284d1a388e0fa0c29fd2f23b2814",
    PLAYBACK_PREFIX + "/audio/corpus.json":
        "7e3533b2256b1904cae4020a3b5c75e2814c1e2057ec99cd5cc9fbd40fa74fd1",
    PLAYBACK_PREFIX + "/audio/tts_lecture_fast.wav":
        "042de519bee66f05731290fee77b4d08e33361a0c95529ff66ad9232f7fb5069",
    PLAYBACK_PREFIX + "/audio/tts_lecture_fillers.wav":
        "d3668a3386f6fdae995284bed2d870c288c370bd3cb4942f5c0aabd3e1426367",
    PLAYBACK_PREFIX + "/audio/ami_stitched.wav":
        "f173f6a9cf944f7d442190056f7a6922ded26a7366beb7d1847662abc5228280",
    PLAYBACK_PREFIX + "/results/results.json":
        "69b5bcc4dc3740bacc182e93419b6a83d5c3eebba7d9b4dfdd8fe4b09813cfc1",
    PLAYBACK_PREFIX + "/results/report.md":
        "9c9383297b1160dbe4f7261f789b493d70354b11930f4d8527b20b0ca8c87c34",
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
    "docs/task-evidence/d1-whole-clip-duration-planner/fixtures/report.json":
        "522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98",
    "docs/task-evidence/dynamic-int8-wav2vec2-base/report.json":
        "6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9",
    "docs/task-evidence/distil-wav2vec2-adult-child-ridge/report.json":
        "ff7b70f389b8c7908c917aa2488728d7f972a8acd22bf66c56d9a671cd5a65d4",
    "docs/task-evidence/survey-rec-01/report.json":
        "b89364422f6e2796d0fd6d955417066d7f01da59420e817f0a781e4e69c20ac5",
    "docs/task-evidence/survey-det-04/report.json":
        "dfbc259cce5c87d186cb6c0aa556724ebdf327c03258f73cdc5ef855c053fd11",
    "docs/task-evidence/phase-vocoder-baseline/report.json":
        "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7",
}

PROFILE_PHRASES = (
    "source/output mapping", "duration", "pitch", "transient audibility",
    "playback buffering", "1×", "rebuffer", "drift",
    "final partial window", "source timestamps",
)

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

SCHEMA_MANIFEST_ID = (
    "audio-sdk/vosk-small-en-us-0-15-playback-gate/qualification/0.1")
BLOCK_SAMPLES = 1600
SOURCE_SAMPLE_NS = 62500
CONTROL_KINDS = (
    "identity_1x", "rate_change", "rebuffer", "final_partial_window")

MANIFEST_FIELDS = (
    "schema_id", "cohort_id", "source", "weights", "runtime", "events",
    "controls", "outcomes", "rights")
SOURCE_FIELDS = (
    "model_revision", "upstream_revision", "license_id", "license_sha256",
    "model_archive_sha256")
WEIGHTS_FIELDS = ("format", "files")
WEIGHT_FILE_FIELDS = ("name", "sha256", "bytes")
RUNTIME_FIELDS = (
    "name", "version", "python", "threads", "offline", "streaming",
    "deterministic", "libvosk_sha256", "wheel_sha256")
EVENTS_FIELDS = ("total_samples", "block_samples", "items")
EVENT_FIELDS = ("kind", "start_sample", "end_sample")
CONTROL_FIELDS = ("id", "kind", "passes")
OUTCOMES_FIELDS = (
    "map_contiguous", "duration_error_samples", "pitch_measured",
    "transient_measured", "buffering_measured", "streaming_rtf", "wer", "peak",
    "nonfinite_count", "deadline_misses", "samples_produced", "sample_rate_hz",
    "first_output_ms", "tail_ms", "qualified")
RIGHTS_FIELDS = (
    "consent_recorded", "model_terms_reviewed", "runtime_license_reviewed",
    "output_use_defined", "commercial_use_approved",
    "listening_protocol_approved")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
WEIGHT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


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
    {"task": "SDK-D1-WHOLE-CLIP-DURATION-PLANNER",
     "role": "merged synthetic D1 budget-identity reference; not reused",
     "report_sha256":
         "522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98"},
    {"task": "SDK-DYNAMIC-INT8-WAV2VEC2-BASE",
     "role": "merged ASR-adjacent DEFER boundary; not recognition evidence",
     "report_sha256":
         "6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9"},
    {"task": "SDK-DISTIL-WAV2VEC2-ADULT-CHILD-RIDGE",
     "role": "merged ASR-adjacent DEFER boundary; not recognition evidence",
     "report_sha256":
         "ff7b70f389b8c7908c917aa2488728d7f972a8acd22bf66c56d9a671cd5a65d4"},
    {"task": "SDK-SURVEY-REC-01",
     "role": "merged ASR taxonomy map; HE-4 is adjacent pre-screen only",
     "report_sha256":
         "b89364422f6e2796d0fd6d955417066d7f01da59420e817f0a781e4e69c20ac5"},
    {"task": "SDK-SURVEY-DET-04",
     "role": "merged detection taxonomy map; HE-2 is adjacent pre-screen only",
     "report_sha256":
         "dfbc259cce5c87d186cb6c0aa556724ebdf327c03258f73cdc5ef855c053fd11"},
    {"task": "SDK-PHASE-VOCODER-BASELINE",
     "role": "merged rate/playback baseline; no gate content",
     "report_sha256":
         "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7"},
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
    model_dir = AUDIO_ROOT / MODEL_PREFIX
    dist_dir = AUDIO_ROOT / DIST_PREFIX
    model_markers = [name for name in LICENSE_MARKER_NAMES
                     if (model_dir / name).is_file()]
    runtime_markers = [name for name in LICENSE_MARKER_NAMES
                       if (dist_dir / name).is_file()]
    readme_path = model_dir / "README"
    readme = (readme_path.read_text(encoding="utf-8", errors="replace")
              if readme_path.is_file() else "")
    readme_lower = readme.lower()
    metadata_path = dist_dir / "METADATA"
    metadata = (metadata_path.read_text(encoding="utf-8", errors="replace")
                if metadata_path.is_file() else "")
    license_field = ""
    classifiers: list[str] = []
    for line in metadata.splitlines():
        if line.startswith("License:"):
            license_field = line.split(":", 1)[1].strip()
        elif line.startswith("Classifier: License ::"):
            classifiers.append(line.split(":", 1)[1].strip())
    return {
        "model_license_marker_files": model_markers,
        "runtime_license_marker_files": runtime_markers,
        "model_readme_states_license": "license" in readme_lower,
        "model_readme_states_apache": "apache" in readme_lower,
        "model_readme_copyright": (
            "Copyright 2020 Alpha Cephei Inc" in readme),
        "runtime_metadata_license_field": license_field,
        "runtime_metadata_license_classifiers": classifiers,
        "model_terms_reviewed": False,
        "redistribution_approved": False,
        "commercial_use_approved": False,
        "output_use_defined": False,
        "qualifies": False,
    }


def source_presence() -> dict[str, Any]:
    model_dir = AUDIO_ROOT / MODEL_PREFIX
    present_files = sum(1 for name in MODEL_FILES
                        if (model_dir / name).is_file())
    runtime_lib = AUDIO_ROOT / RUNTIME_PREFIX / "libvosk.dyld"
    runtime_metadata = AUDIO_ROOT / DIST_PREFIX / "METADATA"
    source_probes = (
        "cpp-library/pipeline-validation/playback-speed/vendor/vosk",
        "cpp-library/pipeline-validation/playback-speed/vendor/vosk-api",
        "cpp-library/pipeline-validation/playback-speed/deps/vosk",
        "cpp-library/pipeline-validation/playback-speed/models/vosk-api",
        "research/vosk-api",
        "research/asr-20261101/vosk-api",
        "third_party/vosk",
        "deps/vosk",
    )
    source_checkout = any((AUDIO_ROOT / probe).is_dir()
                          for probe in source_probes)
    return {
        "model_tree_present": present_files == len(MODEL_FILES),
        "model_file_count": present_files,
        "model_tree_sha256": MODEL_TREE_SHA256,
        "runtime_library_present": runtime_lib.is_file(),
        "runtime_metadata_present": runtime_metadata.is_file(),
        "runtime_version": "0.3.44" if runtime_metadata.is_file() else None,
        "libvosk_bytes": (runtime_lib.stat().st_size
                          if runtime_lib.is_file() else None),
        "upstream_source_checkout_present": source_checkout,
        "upstream_source_probes": list(source_probes),
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
# Synthetic gate-policy arithmetic control (never evidence)
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
    if not re.match(r"^(0|[1-9][0-9]{0,8})/([1-9][0-9]{0,8})$", value):
        raise ValueError(label + "_malformed")
    numerator, denominator = value.split("/")
    parsed = Fraction(int(numerator), int(denominator))
    if parsed < low or parsed > high:
        raise ValueError(label + "_out_of_range")
    return parsed


def validate_events(items: Any, total_samples: Any,
                    block_samples: Any = BLOCK_SAMPLES) -> list[dict[str, int]]:
    total = _exact_int(total_samples, "total_samples", 1, 1_000_000_000)
    block = _exact_int(block_samples, "block_samples", 160, 16000)
    if not isinstance(items, list) or not items or len(items) > 10000:
        raise ValueError("events_items_count")
    result: list[dict[str, int]] = []
    previous_end = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError("event_not_object")
        if set(item) != set(EVENT_FIELDS):
            raise ValueError("event_fields")
        kind = item["kind"]
        if kind not in ("word", "filler"):
            raise ValueError("event_kind")
        start = _exact_int(item["start_sample"], "event_start", 0)
        end = _exact_int(item["end_sample"], "event_end", 0)
        if end <= start:
            raise ValueError("event_empty")
        if end > total:
            raise ValueError("event_out_of_range")
        if start < previous_end:
            raise ValueError("event_overlap_or_unsorted")
        previous_end = end
        result.append({"kind": kind, "start_sample": start,
                       "end_sample": end})
    return result


def block_labels(items: list[dict[str, int]], total_samples: int,
                 block_samples: int = BLOCK_SAMPLES) -> list[str]:
    count = (total_samples + block_samples - 1) // block_samples
    labels = ["silence"] * count
    for item in items:
        first = item["start_sample"] // block_samples
        last = (item["end_sample"] - 1) // block_samples
        for index in range(first, last + 1):
            if item["kind"] == "word":
                labels[index] = "speech"
            elif labels[index] != "speech":
                labels[index] = "filler"
    return labels


def _block_durations(total_samples: int,
                     block_samples: int = BLOCK_SAMPLES) -> list[int]:
    return [min(block_samples, total_samples - index * block_samples)
            for index in range((total_samples + block_samples - 1)
                               // block_samples)]


def _rate_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def plan_labels(labels: list[str], durations: list[int],
                rate_speech: Fraction | None = None,
                rate_flex: Fraction | None = None,
                allow_out_of_bounds: bool = False) -> dict[str, Any]:
    if len(labels) != len(durations):
        raise ValueError("label_duration_length")
    if not labels or any(label not in ("speech", "filler", "silence")
                         for label in labels):
        raise ValueError("label_invalid")
    if any(type(value) is not int or value <= 0 for value in durations):
        raise ValueError("duration_invalid")
    protected = sum(duration for label, duration in zip(labels, durations)
                    if label == "speech")
    flex = sum(duration for label, duration in zip(labels, durations)
               if label != "speech")
    reason = "explicit"
    if rate_speech is None and rate_flex is None:
        if protected == 0:
            rate_speech = Fraction(1)
            rate_flex = Fraction(1)
            reason = "no_protected_speech"
        elif flex == 0:
            rate_speech = Fraction(1)
            rate_flex = Fraction(1)
            reason = "no_flex_budget"
        else:
            balanced = Fraction(protected) / (
                Fraction(protected) + Fraction(flex, 3))
            if balanced < Fraction(4, 5):
                rate_speech = Fraction(1)
                rate_flex = Fraction(1)
                reason = "insufficient_pause_budget"
            else:
                rate_speech = balanced
                rate_flex = Fraction(3, 2)
                reason = "full_pause_budget"
    if rate_speech is None or rate_flex is None:
        raise ValueError("rate_pair_incomplete")
    if not allow_out_of_bounds and not (
            Fraction(4, 5) <= rate_speech <= 1
            and 1 <= rate_flex <= Fraction(3, 2)):
        raise ValueError("rate_out_of_bounds")

    records: list[dict[str, Any]] = []
    source_cursor = 0
    playback_cursor = Fraction(0)
    changes = 0
    previous_rate: Fraction | None = None
    for index, (label, duration) in enumerate(zip(labels, durations)):
        rate = rate_speech if label == "speech" else rate_flex
        if previous_rate is not None and rate != previous_rate:
            changes += 1
        previous_rate = rate
        playback = Fraction(duration) / rate
        source_ns = source_cursor * SOURCE_SAMPLE_NS
        records.append({
            "index": index,
            "label": label,
            "source_start_sample": source_cursor,
            "source_end_sample": source_cursor + duration,
            "source_ns_start": source_ns,
            "source_ns_end": source_ns + duration * SOURCE_SAMPLE_NS,
            "rate": _rate_text(rate),
            "playback_ns_start": _rate_text(
                playback_cursor * SOURCE_SAMPLE_NS),
            "playback_ns_end": _rate_text(
                (playback_cursor + playback) * SOURCE_SAMPLE_NS),
        })
        source_cursor += duration
        playback_cursor += playback

    planned_ns = Fraction(protected + flex) * SOURCE_SAMPLE_NS
    identity = playback_cursor * SOURCE_SAMPLE_NS == planned_ns
    return {
        "records": records,
        "summary": {
            "block_count": len(records),
            "rate_changes": changes,
            "protected_blocks": sum(1 for label in labels if label == "speech"),
            "flex_blocks": sum(1 for label in labels if label != "speech"),
            "protected_samples": protected,
            "flex_samples": flex,
            "rate_speech": _rate_text(rate_speech),
            "rate_flex": _rate_text(rate_flex),
            "reason": reason,
            "planned_source_samples": protected + flex,
            "planned_playback_ns": _rate_text(planned_ns),
            "duration_identity": identity,
            "qualifies": False,
        },
    }


def gate_control() -> dict[str, Any]:
    mixed_events = [
        {"kind": "word", "start_sample": 0, "end_sample": 3200},
        {"kind": "filler", "start_sample": 3200, "end_sample": 4800},
        {"kind": "word", "start_sample": 4800, "end_sample": 11200},
    ]
    cases: list[dict[str, Any]] = []

    def add(case_id: str, total: int, items: list[dict[str, int]],
            rate_speech: Fraction | None = None,
            rate_flex: Fraction | None = None,
            allow_out_of_bounds: bool = False) -> None:
        events = validate_events(items, total)
        labels = block_labels(events, total)
        plan = plan_labels(labels, _block_durations(total),
                           rate_speech, rate_flex, allow_out_of_bounds)
        cases.append({
            "id": case_id,
            "evidence_class": "synthetic_contract_control_not_evidence",
            "total_samples": total,
            "events": events,
            "labels": labels,
            "plan": plan,
            "qualifies": False,
        })

    add("mixed_gate_d1", 16000, mixed_events)
    add("all_speech_fallback", 8000,
        [{"kind": "word", "start_sample": 0, "end_sample": 8000}])
    add("final_partial_window", 16165,
        [{"kind": "word", "start_sample": 0, "end_sample": 9600},
         {"kind": "filler", "start_sample": 9600, "end_sample": 14400}])
    add("fixed_1.25_control", 16000, mixed_events,
        Fraction(5, 4), Fraction(5, 4), True)
    add("slow_only_control", 16000, mixed_events,
        Fraction(4, 5), Fraction(1))

    identity_passes = sum(1 for case in cases
                          if case["plan"]["summary"]["duration_identity"])
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "purpose": "block-mapping and exact-rational duration accounting only",
        "source_sample_ns": SOURCE_SAMPLE_NS,
        "block_samples": BLOCK_SAMPLES,
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "identity_passes": identity_passes,
            "explicit_nonidentity_controls":
                len(cases) - identity_passes,
            "qualifying_results": 0,
            "model_executed": False,
            "runtime_imported": False,
            "audio_read": False,
            "network_used": False,
        },
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


def validate_manifest(manifest: Any) -> dict[str, Any]:
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root["schema_id"] != SCHEMA_MANIFEST_ID:
        raise ValueError("manifest_schema_id")
    if not isinstance(root["cohort_id"], str) \
            or not SLUG.match(root["cohort_id"]):
        raise ValueError("manifest_cohort_id")

    source = _exact_keys(root["source"], SOURCE_FIELDS, "source")
    if not isinstance(source["model_revision"], str) \
            or not SLUG.match(source["model_revision"]):
        raise ValueError("source_model_revision")
    _hex(source["upstream_revision"], "source_upstream_revision", HEX40)
    if source["license_id"] != "Apache-2.0":
        raise ValueError("source_license_id")
    _hex(source["license_sha256"], "source_license_sha256", HEX64)
    _hex(source["model_archive_sha256"], "source_model_archive_sha256", HEX64)

    weights = _exact_keys(root["weights"], WEIGHTS_FIELDS, "weights")
    if weights["format"] != "kaldi_model_dir":
        raise ValueError("weights_format")
    files = weights["files"]
    if not isinstance(files, list) or len(files) != len(MODEL_FILES):
        raise ValueError("weights_files_count")
    seen_names: set[str] = set()
    total_bytes = 0
    has_final_mdl = False
    for index, entry in enumerate(files):
        row = _exact_keys(entry, WEIGHT_FILE_FIELDS, "weight_file")
        name = row["name"]
        if not isinstance(name, str) or not WEIGHT_NAME.match(name) \
                or ".." in name or name.startswith("/") \
                or name not in MODEL_FILES:
            raise ValueError("weight_name")
        if name in seen_names:
            raise ValueError("weight_name_duplicate")
        seen_names.add(name)
        _hex(row["sha256"], "weight_sha256", HEX64)
        byte_count = _exact_int(row["bytes"], "weight_bytes", 1, 1_000_000_000)
        total_bytes += byte_count
        if name.endswith("final.mdl"):
            has_final_mdl = True
    if total_bytes > 8 * 1024 * 1024 * 1024:
        raise ValueError("weights_total_bytes")
    if seen_names != set(MODEL_FILES):
        raise ValueError("weights_incomplete")
    if not has_final_mdl:
        raise ValueError("weights_final_mdl_missing")

    runtime = _exact_keys(root["runtime"], RUNTIME_FIELDS, "runtime")
    if runtime["name"] != "vosk":
        raise ValueError("runtime_name")
    if not isinstance(runtime["version"], str) \
            or not SEMVER.match(runtime["version"]):
        raise ValueError("runtime_version")
    if runtime["python"] not in ("3.10", "3.11", "3.12", "3.13"):
        raise ValueError("runtime_python")
    _exact_int(runtime["threads"], "runtime_threads", 1, 64)
    for field in ("offline", "streaming", "deterministic"):
        if runtime[field] is not True:
            raise ValueError("runtime_" + field)
    _hex(runtime["libvosk_sha256"], "runtime_libvosk_sha256", HEX64)
    _hex(runtime["wheel_sha256"], "runtime_wheel_sha256", HEX64)

    events = _exact_keys(root["events"], EVENTS_FIELDS, "events")
    items = validate_events(events["items"], events["total_samples"],
                            events["block_samples"])

    controls = root["controls"]
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise ValueError("controls_count")
    seen_ids: set[str] = set()
    seen_kinds: set[str] = set()
    for entry in controls:
        row = _exact_keys(entry, CONTROL_FIELDS, "control")
        if not isinstance(row["id"], str) or not SLUG.match(row["id"]):
            raise ValueError("control_id")
        if row["id"] in seen_ids:
            raise ValueError("control_id_duplicate")
        seen_ids.add(row["id"])
        if row["kind"] not in CONTROL_KINDS:
            raise ValueError("control_kind")
        if row["kind"] in seen_kinds:
            raise ValueError("control_kind_duplicate")
        seen_kinds.add(row["kind"])
        if row["passes"] is not True:
            raise ValueError("control_not_passed")

    outcomes = _exact_keys(root["outcomes"], OUTCOMES_FIELDS, "outcomes")
    for field in ("map_contiguous", "pitch_measured", "transient_measured",
                  "buffering_measured"):
        if outcomes[field] is not True:
            raise ValueError("outcome_" + field)
    _exact_int(outcomes["duration_error_samples"],
               "outcome_duration_error", -1600, 1600)
    _fraction(outcomes["streaming_rtf"], "outcome_streaming_rtf",
              Fraction(0), Fraction(1))
    _fraction(outcomes["wer"], "outcome_wer", Fraction(0), Fraction(1))
    _fraction(outcomes["peak"], "outcome_peak", Fraction(0), Fraction(4))
    if _exact_int(outcomes["nonfinite_count"],
                  "outcome_nonfinite_count", 0, 1_000_000) != 0:
        raise ValueError("outcome_nonfinite")
    if _exact_int(outcomes["deadline_misses"],
                  "outcome_deadline_misses", 0, 1_000_000) != 0:
        raise ValueError("outcome_deadline_miss")
    _exact_int(outcomes["samples_produced"], "outcome_samples", 1, 10**9)
    if outcomes["sample_rate_hz"] not in (8000, 16000, 48000):
        raise ValueError("outcome_sample_rate")
    _exact_int(outcomes["first_output_ms"], "outcome_first_output", 0, 600000)
    _exact_int(outcomes["tail_ms"], "outcome_tail", 0, 600000)
    if outcomes["qualified"] is not False:
        raise ValueError("outcome_self_qualified")

    rights = _exact_keys(root["rights"], RIGHTS_FIELDS, "rights")
    for field in RIGHTS_FIELDS:
        if rights[field] is not True:
            raise ValueError("rights_" + field)

    labels = block_labels(items, events["total_samples"],
                          events["block_samples"])
    plan = plan_labels(labels, _block_durations(
        events["total_samples"], events["block_samples"]))
    return {
        "admitted": True,
        "qualifies": False,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "cohort_id": root["cohort_id"],
        "block_count": len(labels),
        "duration_identity": plan["summary"]["duration_identity"],
        "plan_digest": object_digest(plan),
    }


def _base_manifest() -> dict[str, Any]:
    def syn(name: str) -> str:
        return hashlib.sha256(("synthetic:" + name).encode("ascii")).hexdigest()

    names = sorted(MODEL_FILES)
    return {
        "schema_id": SCHEMA_MANIFEST_ID,
        "cohort_id": "synthetic-schema-control",
        "source": {
            "model_revision": "vosk-model-small-en-us-0.15",
            "upstream_revision": "0" * 40,
            "license_id": "Apache-2.0",
            "license_sha256": syn("model-license"),
            "model_archive_sha256": syn("model-archive"),
        },
        "weights": {
            "format": "kaldi_model_dir",
            "files": [{"name": name, "sha256": syn("weight:" + name),
                       "bytes": MODEL_FILE_BYTES[name]} for name in names],
        },
        "runtime": {
            "name": "vosk",
            "version": "0.3.44",
            "python": "3.12",
            "threads": 4,
            "offline": True,
            "streaming": True,
            "deterministic": True,
            "libvosk_sha256": syn("libvosk"),
            "wheel_sha256": syn("wheel"),
        },
        "events": {
            "total_samples": 16000,
            "block_samples": BLOCK_SAMPLES,
            "items": [
                {"kind": "word", "start_sample": 0, "end_sample": 4000},
                {"kind": "filler", "start_sample": 4000, "end_sample": 4800},
                {"kind": "word", "start_sample": 4800, "end_sample": 11200},
            ],
        },
        "controls": [
            {"id": "control-identity", "kind": "identity_1x", "passes": True},
            {"id": "control-rate", "kind": "rate_change", "passes": True},
            {"id": "control-rebuffer", "kind": "rebuffer", "passes": True},
            {"id": "control-final", "kind": "final_partial_window",
             "passes": True},
        ],
        "outcomes": {
            "map_contiguous": True,
            "duration_error_samples": 0,
            "pitch_measured": True,
            "transient_measured": True,
            "buffering_measured": True,
            "streaming_rtf": "1/2",
            "wer": "1/20",
            "peak": "4/5",
            "nonfinite_count": 0,
            "deadline_misses": 0,
            "samples_produced": 16000,
            "sample_rate_hz": 16000,
            "first_output_ms": 150,
            "tail_ms": 150,
            "qualified": False,
        },
        "rights": {
            "consent_recorded": True,
            "model_terms_reviewed": True,
            "runtime_license_reviewed": True,
            "output_use_defined": True,
            "commercial_use_approved": True,
            "listening_protocol_approved": True,
        },
    }


def _mutations() -> list[tuple[str, str, Any]]:
    def setter(path: tuple[str, ...], value: Any):
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

    return [
        ("manifest_missing_rights", "manifest_fields",
         deleter(("rights",))),
        ("manifest_unknown_field", "manifest_fields",
         setter(("extra",), True)),
        ("manifest_schema", "manifest_schema_id",
         setter(("schema_id",), "audio-sdk/other/0.1")),
        ("source_revision_short", "source_upstream_revision_malformed",
         setter(("source", "upstream_revision"), "a" * 39)),
        ("source_license_not_apache", "source_license_id",
         setter(("source", "license_id"), "MIT")),
        ("source_license_digest", "source_license_sha256_malformed",
         setter(("source", "license_sha256"), "z" * 64)),
        ("weights_empty", "weights_files_count",
         setter(("weights", "files"), [])),
        ("weights_final_mdl_missing", "weights_files_count",
         setter(("weights", "files"),
                [{"name": "graph/Gr.fst", "sha256": "a" * 64,
                  "bytes": 10}])),
        ("weight_traversal", "weight_name",
         setter(("weights", "files", 0, "name"), "../final.mdl")),
        ("weight_bad_suffix", "weight_name",
         setter(("weights", "files", 0, "name"), "final.mdl.exe")),
        ("weight_zero_bytes", "weight_bytes_below_minimum",
         setter(("weights", "files", 0, "bytes"), 0)),
        ("weight_bad_digest", "weight_sha256_malformed",
         setter(("weights", "files", 0, "sha256"), "A" * 64)),
        ("weight_duplicate", "weight_name_duplicate",
         lambda manifest: manifest["weights"]["files"][1].update(
             {"name": manifest["weights"]["files"][0]["name"]})),
        ("runtime_name", "runtime_name",
         setter(("runtime", "name"), "kaldi")),
        ("runtime_version", "runtime_version",
         setter(("runtime", "version"), "0.3")),
        ("runtime_python", "runtime_python",
         setter(("runtime", "python"), "3.9")),
        ("runtime_threads", "runtime_threads_below_minimum",
         setter(("runtime", "threads"), 0)),
        ("runtime_offline", "runtime_offline",
         setter(("runtime", "offline"), False)),
        ("runtime_streaming", "runtime_streaming",
         setter(("runtime", "streaming"), False)),
        ("runtime_libvosk_digest", "runtime_libvosk_sha256_malformed",
         setter(("runtime", "libvosk_sha256"), "x" * 64)),
        ("events_empty", "events_items_count",
         setter(("events", "items"), [])),
        ("event_bool_start", "event_start_not_int",
         setter(("events", "items", 0, "start_sample"), True)),
        ("event_negative", "event_start_below_minimum",
         setter(("events", "items", 0, "start_sample"), -1)),
        ("event_empty_span", "event_empty",
         setter(("events", "items", 0, "end_sample"), 0)),
        ("event_overlap", "event_overlap_or_unsorted",
         setter(("events", "items", 1, "start_sample"), 3999)),
        ("event_out_of_range", "event_out_of_range",
         setter(("events", "items", 2, "end_sample"), 16001)),
        ("event_unknown_kind", "event_kind",
         setter(("events", "items", 0, "kind"), "music")),
        ("outcome_nonfinite", "outcome_nonfinite",
         setter(("outcomes", "nonfinite_count"), 1)),
        ("outcome_wer_range", "outcome_wer_out_of_range",
         setter(("outcomes", "wer"), "3/2")),
        ("outcome_peak_range", "outcome_peak_out_of_range",
         setter(("outcomes", "peak"), "9/2")),
        ("outcome_self_qualified", "outcome_self_qualified",
         setter(("outcomes", "qualified"), True)),
        ("outcome_float", "runtime_threads_not_int",
         setter(("runtime", "threads"), 4.0)),
        ("controls_missing_kind", "controls_count",
         lambda manifest: manifest["controls"].pop()),
        ("controls_duplicate", "control_kind_duplicate",
         setter(("controls", 1, "kind"), "identity_1x")),
        ("controls_not_passed", "control_not_passed",
         setter(("controls", 0, "passes"), False)),
        ("rights_consent", "rights_consent_recorded",
         setter(("rights", "consent_recorded"), False)),
        ("rights_commercial", "rights_commercial_use_approved",
         setter(("rights", "commercial_use_approved"), False)),
        ("source_unknown_field", "source_fields",
         setter(("source", "extra"), "x")),
        ("runtime_unknown_field", "runtime_fields",
         setter(("runtime", "extra"), "x")),
        ("event_unknown_field", "event_fields",
         setter(("events", "items", 0, "extra"), "x")),
        ("outcome_unknown_field", "outcomes_fields",
         setter(("outcomes", "extra"), "x")),
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
            "block_count": control["block_count"],
            "duration_identity": control["duration_identity"],
            "plan_digest": control["plan_digest"],
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
        "Source-reported gate RTF, block counts and IoU are provenance only; "
        "they were not remeasured here.",
        "No streaming Vosk run, first-output time, right-context, endpoint, "
        "reset or final-partial behavior was measured.",
        "No model or runtime license, notice, model card or output-use grant "
        "was found locally; presence is not admission.",
        "No rights-cleared real corpus, consent record or human-verified word/"
        "filler/pause labels are present.",
        "No audio was decoded, read or played; no weight was loaded and no "
        "runtime was imported or executed.",
        "No pitch, transient, buffering, rebuffer, drift, listening, device "
        "timing, resource or benchmark result exists.",
        "No provider, descriptor, registry, default, installed-v0, ABI, "
        "shared-build, CI, board or handoff file is changed.",
    ]


def _required_results() -> dict[str, bool]:
    return {
        "upstream_model_archive_and_license_admitted": False,
        "upstream_source_revision_and_license_admitted": False,
        "pinned_runtime_archive_lock_and_license_admitted": False,
        "streaming_gate_run_and_trace_present": False,
        "model_reproduced_offline": False,
        "rights_cleared_corpus_and_labels_present": False,
        "rate_acceptance_profile_measured": False,
        "content_preservation_measured": False,
        "listening_measured": False,
        "device_timing_measured": False,
        "provider_intake_approved": False,
        "release_approved": False,
        "no_result_qualifies": True,
    }


def _required_artifacts() -> list[dict[str, Any]]:
    markers = license_marker_probe()
    presence = source_presence()
    return [
        {
            "id": "A01",
            "name": "vosk-model-small-en-us-0.15 weight tree",
            "present": presence["model_tree_present"],
            "verified": presence["model_tree_present"],
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "path": MODEL_PREFIX,
            "file_count": presence["model_file_count"],
            "tree_sha256": MODEL_TREE_SHA256,
            "blocker": "BLK-01",
        },
        {
            "id": "A02",
            "name": "Python Vosk runtime artifacts",
            "present": presence["runtime_library_present"],
            "verified": presence["runtime_library_present"],
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "path": RUNTIME_PREFIX,
            "version": presence["runtime_version"],
            "libvosk_bytes": presence["libvosk_bytes"],
            "blocker": "BLK-03",
        },
        {
            "id": "A03",
            "name": "Vosk source checkout at an exact revision",
            "present": presence["upstream_source_checkout_present"],
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-02",
        },
        {
            "id": "A04",
            "name": "model LICENSE/NOTICE/model card and written terms",
            "present": bool(markers["model_license_marker_files"]),
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-01",
        },
        {
            "id": "A05",
            "name": "runtime LICENSE/NOTICE text",
            "present": bool(markers["runtime_license_marker_files"]),
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-03",
        },
        {
            "id": "A06",
            "name": "wheel archive, lockfile and offline install record",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-03",
        },
        {
            "id": "A07",
            "name": "rights-cleared corpus with consent and output-use terms",
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
            "name": "human-verified word/filler/pause span labels",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-05",
        },
        {
            "id": "A09",
            "name": "streaming gate run with callbacks and reset/final trace",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-04",
        },
        {
            "id": "A10",
            "name": "listening, device timing and benchmark/release record",
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
            "status": "open",
            "qualifies": False,
            "missing": (
                "Official vosk-model-small-en-us-0.15 archive identity "
                "(published URL/archive name, model revision, archive size and "
                "SHA-256), a LICENSE/NOTICE/model card and a written Apache-2.0 "
                "model grant covering redistribution, commercial use and "
                "generated-output use. The 14-file local tree is byte-pinned "
                "but has no license marker and its README states only "
                "'Copyright 2020 Alpha Cephei Inc'."),
            "required_action": (
                "Supply the official model archive or immutable artifact "
                "revision plus archive SHA-256, the complete license/notice/"
                "model-card text, and a reviewed model/output-use decision."),
        },
        {
            "id": "BLK-02",
            "artifact_id": "A03",
            "status": "open",
            "qualifies": False,
            "missing": (
                "Vosk source checkout at an exact 40-hex revision with the "
                "Apache-2.0 LICENSE and NOTICE text for the decoder, Kaldi "
                "derivation and bundled third-party components. No source "
                "checkout is present."),
            "required_action": (
                "Supply the exact source revision, tree digest, license, "
                "notice bundle and a reviewed correspondence to the pinned "
                "runtime."),
        },
        {
            "id": "BLK-03",
            "artifact_id": "A02",
            "status": "open",
            "qualifies": False,
            "missing": (
                "A pinned wheel/sdist archive with SHA-256, a lockfile, an "
                "offline install record and the runtime LICENSE text. The "
                "local vosk 0.3.44 dist-info has no LICENSE file and its "
                "METADATA says 'License: UNKNOWN' (an Apache classifier is "
                "not a grant). libvosk.dyld is 12,533,472 bytes."),
            "required_action": (
                "Supply the exact wheel archive digest, license/notice text, "
                "locked isolated install, offline load proof and recorded "
                "host profile."),
        },
        {
            "id": "BLK-04",
            "artifact_id": "A09",
            "status": "open",
            "qualifies": False,
            "missing": (
                "A streaming gate run. The prototype used one batch "
                "KaldiRecognizer call with SetWords(True) over the whole clip; "
                "right-context, chunking, endpoint/reset, dropped/stale events, "
                "final partial window, first-output time and callback timing "
                "were not measured."),
            "required_action": (
                "Supply the exact streaming API trace at a pinned chunk size, "
                "including final partial, reset, availability and latency."),
        },
        {
            "id": "BLK-05",
            "artifact_id": "A07",
            "status": "open",
            "qualifies": False,
            "missing": (
                "A rights-cleared frozen corpus with consent, speaker/language "
                "groups and output-use terms, plus human-verified word/filler/"
                "pause spans. The prototype corpus is two macOS say TTS clips "
                "with construction-time labels and one unlabeled AMI stitch."),
            "required_action": (
                "Supply an immutable consented cohort with human-verified "
                "spans, matched controls and independent review."),
        },
        {
            "id": "BLK-06",
            "artifact_id": "A10",
            "status": "open",
            "qualifies": False,
            "missing": (
                "Rate-profile acceptance results: measured source/output "
                "mapping, duration, pitch, transient audibility, 1x/rate-change/"
                "rebuffer/drift/final-partial controls, content preservation, "
                "blind listening, target-device timing, resources and release "
                "review."),
            "required_action": (
                "Supply measured rate-profile evidence, independent scoring "
                "and listening, target-device timing and a separate approved "
                "provider intake with an OFF default."),
        },
    ]


def _rate_profile_rows() -> list[dict[str, Any]]:
    return [
        {"id": "RATE-01", "requirement": "1× control",
         "status": "blocked", "qualifies": False,
         "evidence": "No measured 1× gate/actuator playback control."},
        {"id": "RATE-02", "requirement": "source/output mapping and rate changes",
         "status": "blocked", "qualifies": False,
         "evidence": "Synthetic arithmetic only; no source-to-output gate run."},
        {"id": "RATE-03", "requirement": "duration identity and error",
         "status": "blocked", "qualifies": False,
         "evidence": "No measured output duration for a real gate/actuator."},
        {"id": "RATE-04", "requirement": "pitch",
         "status": "blocked", "qualifies": False,
         "evidence": "No stretched waveform or pitch measurement."},
        {"id": "RATE-05", "requirement": "transient audibility",
         "status": "blocked", "qualifies": False,
         "evidence": "No waveform, listening or transient analysis."},
        {"id": "RATE-06", "requirement": "playback buffering, rebuffer and drift",
         "status": "blocked", "qualifies": False,
         "evidence": "No device clock, buffering, fill/flush or drift run."},
        {"id": "RATE-07", "requirement": "unfamiliar speech, music and silence",
         "status": "blocked", "qualifies": False,
         "evidence": "No rights-cleared stratified corpus exists."},
        {"id": "RATE-08",
         "requirement": "final partial window and speech preservation",
         "status": "blocked", "qualifies": False,
         "evidence": "Synthetic final window only; no real gate labels or "
                     "preservation score."},
    ]


def _rate_outcomes() -> list[dict[str, Any]]:
    rows = []
    for row in _rate_profile_rows():
        rows.append({
            "id": row["id"].replace("RATE", "OUT"),
            "requirement": row["requirement"],
            "status": "blocked",
            "value": None,
            "qualifies": False,
        })
    return rows


def _release_gates(projection: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        ("RG-01", "model archive identity, license, notice and model card",
         "Official archive name/URL, model revision, byte count, SHA-256, "
         "complete Apache-2.0 model/notice text and reviewed output-use terms."),
        ("RG-02", "Vosk source revision, license and notice bundle",
         "Exact 40-hex source revision, tree digest, Apache-2.0 license and "
         "complete notice set corresponding to the pinned runtime."),
        ("RG-03", "runtime archive, lock and offline load",
         "Pinned wheel/sdist digest, lockfile, isolated offline install, "
         "runtime license text and recorded host profile."),
        ("RG-04", "streaming gate availability and event integrity",
         "Pinned chunk size, right-context, endpoint/reset/final-partial "
         "behavior, dropped/stale event accounting and measured latency."),
        ("RG-05", "rights-cleared corpus and human-verified labels",
         "Signed consent, immutable cohort, speaker/language groups, "
         "human-verified word/filler/pause spans and matched controls."),
        ("RG-06", "rate acceptance profile",
         "Measured mapping, 1x/rate-change/duration/pitch/transient/buffering/"
         "rebuffer/drift/final-partial results with agreed margins."),
        ("RG-07", "content preservation and independent scoring",
         "Independent scorer or human transcript, stratified WER/semantic "
         "preservation and separation from the source-reported Whisper proxy."),
        ("RG-08", "listening, device timing, provider intake and release",
         "Blind listening, target-device timing/power/resources, separate "
         "opt-in provider intake with OFF default and exact-head review."),
    ]
    return [{"id": gate_id, "title": title, "status": "blocked",
             "qualifies": False, "reopen_condition": condition,
             "linked_row": dict(projection)}
            for gate_id, title, condition in rows]


def _prototype_provenance() -> dict[str, Any]:
    return {
        "evidence_class": "source_reported_not_remeasured",
        "qualifies": False,
        "package": PLAYBACK_PREFIX,
        "gate": "Vosk small-en-us-0.15",
        "mode": "batch whole-clip KaldiRecognizer, SetWords(True)",
        "streaming": False,
        "corpus": {
            "clips": 3,
            "synthetic_tts_clips": 2,
            "real_clip_without_reference_transcript": 1,
            "listeners": 0,
        },
        "reported": {
            "gate_rtf_median": "0.056",
            "gate_share_of_chain_cost": "about 98 percent",
            "total_blocks": 15708,
            "deadline_misses": 0,
            "gate_iou_range": "0.94-0.95",
            "false_speech_blocks": 12,
            "missed_speech_blocks": 24,
            "labeled_blocks": "345/467",
            "duration_error_range_ms": "-6 to +30",
        },
        "not_reproduced_here": True,
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
            "model_present": presence["model_tree_present"],
            "runtime_present": presence["runtime_library_present"],
            "licensed_artifact_set_present": False,
            "reasons": [
                "model and runtime have no local license/notice grant",
                "no exact Vosk source revision or license",
                "no pinned wheel archive, lock or offline load",
                "no streaming gate run",
                "no rights-cleared corpus or human-verified labels",
                "no measured rate, listening or device-timing result",
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
        "observed_provenance": {
            "model_files": {
                "count": len(MODEL_FILES),
                "bytes": sum(MODEL_FILE_BYTES.values()),
                "tree_sha256": MODEL_TREE_SHA256,
                "files": [
                    {"name": name, "bytes": MODEL_FILE_BYTES[name],
                     "sha256": MODEL_FILES[name]}
                    for name in sorted(MODEL_FILES)
                ],
            },
            "runtime": {
                "name": "vosk",
                "version": "0.3.44",
                "python_wheel": "osx_arm64, cpython 3.11 (local install only)",
                "libvosk_bytes": 12533472,
                "libvosk_sha256": SOURCE_PINS[
                    RUNTIME_PREFIX + "/libvosk.dyld"],
                "wheel_archive_present": False,
                "license_text_present": False,
                "metadata_license_field": markers[
                    "runtime_metadata_license_field"],
            },
            "prototype": _prototype_provenance(),
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
        "gate_control": gate_control(),
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
