# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local readiness evidence for SDK-SILERO-VAD-V5-ONNX-REFERENCE.

Standard-library only and deterministic. The exact Silero VAD v5 upstream
source, wrapper, frozen reference outputs, licensed runtime and analysis cohort
are absent. One ONNX file is present and is pinned and structurally
fingerprinted without decoding tensor values or executing the graph. No audio
is read, no model output is produced, and no result here qualifies the
candidate.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

TASK = "SDK-SILERO-VAD-V5-ONNX-REFERENCE"
COMPONENT_ID = "silero-vad-v5-onnx-reference"
TASK_TITLE = "Silero VAD v5 ONNX reference"
CONTRACT_ID = "audio-sdk/silero-vad-v5-onnx-reference-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
ADMISSION_SCHEMA_ID = "audio-sdk/silero-vad-v5-reference-bundle/0.1"
PROFILE = "analysis"
PROFILE_LABEL = "Analysis"
MODE = "implementation"
BASE_COMMIT = "acefdd1df870fd19f990eba92fd15bf38f171f75"
BRANCH = "swarm/SDK-SILERO-VAD-V5-ONNX-REFERENCE"
WRITE_SCOPE = "docs/task-evidence/silero-vad-v5-onnx-reference/ only"
TASK_PREFIX = "docs/task-evidence/silero-vad-v5-onnx-reference/"
DISPOSITION = (
    "Silero VAD v5 ONNX reference readiness blocker; one local ONNX artifact is "
    "pinned and structurally fingerprinted, but exact upstream source, version, "
    "license, runtime, reference outputs, analysis corpus and result are absent.")

MODEL_PATH = "cpp-library/.deps/silero_vad.onnx"
MODEL_SHA256 = (
    "1a153a22f4509e292a94e67d6f9b85e8deb25b4988682b7e174c65279d8788e3")
MODEL_BYTE_COUNT = 2327524
MODEL_IR_VERSION = 8
MODEL_PRODUCER = "spox"
GRAPH_INPUTS = ("input", "state", "sr")
GRAPH_OUTPUTS = ("output", "stateN")
STATE_SHAPE = (2, 1, 128)
SAMPLE_RATES = (8000, 16000)
STFT_16K = (258, 1, 256)
STFT_8K = (130, 1, 128)
ENCODER_16K = ((128, 129, 3), (64, 128, 3), (64, 64, 3), (128, 64, 3))
ENCODER_8K = ((128, 65, 3), (64, 128, 3), (64, 64, 3), (128, 64, 3))
LSTM_SHAPES = ((512, 128), (512, 128), (512,), (512,))
DECODER_SHAPES = ((1, 128, 1), (1,))
PARAMETERS_16K = 309633
PARAMETERS_8K = 235649
PARAMETERS_TOTAL = 545282
WEIGHT_BYTES_TOTAL = 2181128
STRUCTURAL_SHA256 = (
    "b513ef1ca141febaa5a8fa09ecdc83d9b87c7302cead9b8a35260c30093023f4")
CADENCE_16K = (512, 64)
CADENCE_8K = (256, 32)
V0_FRAME_SAMPLES = 160
MODEL_HOP_MS = 32
MODEL_MAX_BYTES = 16 * 1024 * 1024
MODEL_WINDOW_KEYS = (
    "stft.forward_basis_buffer",
    "encoder.0.reparam_conv.weight",
    "encoder.0.reparam_conv.bias",
    "encoder.1.reparam_conv.weight",
    "encoder.1.reparam_conv.bias",
    "encoder.2.reparam_conv.weight",
    "encoder.2.reparam_conv.bias",
    "encoder.3.reparam_conv.weight",
    "encoder.3.reparam_conv.bias",
    "decoder.rnn.weight_ih",
    "decoder.rnn.weight_hh",
    "decoder.rnn.bias_ih",
    "decoder.rnn.bias_hh",
    "decoder.decoder.2.weight",
    "decoder.decoder.2.bias",
)

PROFILE_PHRASES = (
    "Score timestamped probabilities, event boundaries and detections.",
    "Include quiet and active speech, idle noise, known positives and "
    "negatives, onset/offset delay and stratified FN/FP.",
    "Separate validity from nonspeech.",
    "Verify independent state, exact source intervals, availability, "
    "dropped/stale events and cross-hop behavior.",
)

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

# Read-only source pins. `source:` rows are workspace-relative; boundary rows
# are SDK-worktree-relative. The mutable shared board is never pinned; only the
# stable linked-row identity is projected below.
SOURCE_PINS = {
    "cpp-library/src/stages/silero_vad.cpp":
        "92d26974f3c7d89bd897921957d14865378f7ae02aa9dc9f8bacef51dc36d9b1",
    "cpp-library/src/stages/silero_vad_native.cpp":
        "8f85f68487c8f0a4735304e1c9dfde1ee6265c5f4beb72e53d1ebc4babb4a289",
    MODEL_PATH: MODEL_SHA256,
    "cpp-library/cmake/audio_enhance_models.json":
        "6b14470521a1ba599f572e236eb96c877dfe5777341eb402b9224c3eb5feedbe",
    "cpp-library/docs/api-contract.md":
        "cd38401b07cf7049438214807daeb41407470d31cb27e53e999ebd79954b6181",
    "cpp-library/docs/qualification.md":
        "dae52c726eb679620e6cf17631e6294e6af4c4b09a0a47e3d740d318767c3ba4",
    "cpp-library/docs/extension-guide.md":
        "a7c527c4ed4bc03ddcc2788e234aa04e35d1fc0ecb31766bb1f9f9762ff2c771",
    "cpp-library/README.md":
        "5bb42250f3f7485f539c6748a7e6e691c9b8b62b5ef882e19b2c08208caa7b00",
    "cpp-library/pipeline-validation/tiny-silero/results.json":
        "55bdd2d1febd0fe509e58d4c021087f5eb0e70d942949b952cb57e6429185fa9",
    "research/plans/F02/vad_sources.md":
        "374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec",
    "adapters/silero-vad/adapter.json":
        "45222fd98fe1bd76550d0529cdaa442783807a727880b168d7879eca4f54a60a",
    "adapters/silero-vad/run.py":
        "9f51a7b06440d8f7d0518928a291657803af96a79c0277101e259f870fec05d3",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
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
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/adaptive-energy-to-silero-cascade/README.md":
        "1e2632185f1e90d208958d2e49a1c2efc6eda5909e75e695d215cbea83d4b8a9",
    "docs/task-evidence/adaptive-energy-to-silero-cascade/report.json":
        "e7a1ee9f9df8ba70c18697a2e46c1f9599719134cdc7a62a37fbb51c4e56eb5e",
    "docs/task-evidence/silero-vad-opensmile-small-regression-head/README.md":
        "65ed5b651e2ce01cd5cf18a9d24201e04d1c2002d0f7f842f3b6fc155268f2c1",
    "docs/task-evidence/silero-vad-opensmile-small-regression-head/report.json":
        "208d81e915839a40a96033d657443691f62e4973930ef1543bea40f8793f946d",
    "docs/task-evidence/silero-vad-pause-duration-rules/README.md":
        "b6e422c591364dffa8b6ab0d3c9c78a579a6c85c88f831d86ee8c9d27593ab1f",
    "docs/task-evidence/silero-vad-pause-duration-rules/report.json":
        "9aebd32c6dc61cf4c5d3d5e0b38fd82a2f083792a453bf9db9548e52cfa5b22d",
}

BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = ("id", "title", "component", "mode", "repository",
                    "depends_on")
LINKED_ROW_IDS = (TASK, "SDK-FND-ANALYSIS", "SDK-FND-AUDIT",
                  "SDK-FND-EVIDENCE", "SDK-FND-NN", "SDK-FND-PROVIDER")

WORKSPACE_PROBES = (
    "data/models/silero-vad-v5",
    "data/models/silero-vad-5.1.2",
    "data/models/silero-vad-v5/silero_vad.onnx",
    "data/models/silero-vad-5.1.2/silero_vad.onnx",
    "data/wheels/vad-candidates/silero-runtime/"
    "silero_vad-5.1.2-py3-none-any.whl",
    "data/envs/silero-vad-v5/requirements.lock",
    "adapters/silero-vad-v5/adapter.json",
    "adapters/silero-vad-v5/run.py",
    "cpp-library/.deps/silero_vad_v5.onnx",
    "cpp-library/.deps/silero_vad.onnx.license",
    "research/voice-enhancement-20261101/agent-vad-v5-reference/REPORT.md",
    "data/corpora/silero-vad-v5-analysis/manifest.json",
)
HOME_PROBES = (
    ".cache/huggingface/hub/models--snakers4--silero-vad",
    ".cache/torch/hub/snakers4_silero-vad_master",
    ".cache/onnxruntime",
    ".cache/silero-vad",
)

NON_CLAIMS = [
    "The present ONNX file is pinned by SHA-256 and structurally scanned; its "
    "tensor values are never decoded and its graph is never executed.",
    "No upstream Silero VAD v5 repository checkout, wrapper source, release tag, "
    "model card, weight terms or license/notice bundle is present.",
    "No exact Python or ONNX Runtime environment, wheel hash, install/import "
    "digest or deterministic runtime is pinned for v5.",
    "No frozen PCM fixture, timestamped probability trace, event boundary, "
    "detection or reference output is present or produced.",
    "No audio is read or decoded; no real corpus, annotation or rights-cleared "
    "cohort is present.",
    "No analysis score, FN/FP stratification, onset/offset delay, validity "
    "result, listening result or benchmark result exists.",
    "No device, callback, pacing, deadline, memory or thermal timing is "
    "measured.",
    "No provider, descriptor, registry entry, default selection, public ABI, "
    "shared build or CI change exists.",
    "The merged Silero packages use synthetic traces or model-free stubs; none "
    "supplies a v5 ONNX output, so none is reused as a reference result.",
    "A present file and matching structural shapes are not a version, license, "
    "output or release qualification.",
]

REQUIRED_RESULTS = [
    "The exact upstream Silero VAD v5 source revision and wrapper, with a "
    "reviewed license/notice and trained-weight product-use decision.",
    "An exact model manifest that resolves the v5 versus 6.2.3 provenance "
    "conflict for SHA-256 1a153a22f4509e292a94e67d6f9b85e8deb25b4988682b7e174c65279d8788e3.",
    "A pinned deterministic 8 kHz and 16 kHz runtime with every wheel hash, "
    "install/import digest, CPU/thread settings and offline behavior.",
    "A frozen caller-supplied PCM/probability/event oracle with exact digests, "
    "tolerance, warmup, reset, stale and missing-input controls.",
    "A rights-cleared continuous-label analysis cohort with quiet and active "
    "speech, idle noise, known positives/negatives, onset/offset labels and "
    "language/speaker groups.",
    "Reproduced timestamped probabilities, event boundaries, detections, "
    "validity separation, exact source intervals and stratified FN/FP.",
    "Independent-state, cross-hop, availability, dropped/stale-event and "
    "independent reset evidence.",
    "Target-device availability and deadline timing under paced workload, with "
    "resources and finite drain measured separately.",
    "A separate OFF-by-default versioned provider intake and independent "
    "exact-head review after every earlier gate clears.",
]

HEADER_COMMENT = (
    "# SHA-256 pins for SDK-SILERO-VAD-V5-ONNX-REFERENCE readiness evidence.\n"
    "# source: paths are relative to AUDIO_ROOT; other paths are SDK-worktree "
    "relative.\n"
    "# The mutable shared board is not pinned; only its stable row identity "
    "gates.\n"
    "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.\n"
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def loads_strict(text: str) -> dict[str, Any]:
    """Parse a JSON object, rejecting duplicates, BOM, NaN and Infinity."""
    if not isinstance(text, str):
        raise ValueError("json_text_type")
    if text.startswith("\ufeff"):
        raise ValueError("json_bom")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("json_duplicate_key:" + key)
            result[key] = value
        return result

    def constant_hook(name: str) -> Any:
        raise ValueError("json_nonfinite:" + name)

    try:
        parsed = json.loads(text, object_pairs_hook=pairs_hook,
                            parse_constant=constant_hook)
    except ValueError:
        raise
    except Exception as error:  # pragma: no cover - defensive
        raise ValueError("json_parse:" + str(error)) from error
    if not isinstance(parsed, dict):
        raise ValueError("json_root_not_object")
    return parsed


def read_strict_json(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("json_not_utf8:" + str(error)) from error
    return loads_strict(text)


def _no_floats(value: Any, where: str = "$") -> None:
    if isinstance(value, float):
        raise ValueError("canonical_float:" + where)
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("canonical_nonstring_key:" + where)
            _no_floats(item, where + "." + key)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _no_floats(item, where + "[" + str(index) + "]")


def canonical_bytes(value: Any) -> bytes:
    _no_floats(value)
    text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return (text + "\n").encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


class AdmissionError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _require_exact_keys(value: Any, keys: tuple[str, ...], code: str) -> None:
    if not isinstance(value, dict) or set(value) != set(keys):
        raise AdmissionError(code)


def _require_hex64(value: Any, code: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise AdmissionError(code)
    return value


def _require_version(value: Any, code: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise AdmissionError(code)
    return value


def _require_text(value: Any, code: str, maximum: int = 256) -> str:
    if (not isinstance(value, str) or not value or len(value) > maximum
            or any(ord(ch) < 32 or ord(ch) > 126 for ch in value)):
        raise AdmissionError(code)
    return value


def _require_int(value: Any, code: str, minimum: int = 0,
                 maximum: int = 2 ** 63 - 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AdmissionError(code)
    if value < minimum or value > maximum:
        raise AdmissionError(code)
    return value


def _require_bool(value: Any, code: str) -> bool:
    if not isinstance(value, bool):
        raise AdmissionError(code)
    return value


def _require_decimal(value: Any, code: str) -> str:
    if not isinstance(value, str):
        raise AdmissionError(code)
    if not re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value):
        raise AdmissionError(code)
    if value == "-0":
        raise AdmissionError(code)
    return value


def _project_row(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in BOARD_ROW_FIELDS}


def _board_rows(path: Path | None = None) -> dict[str, dict[str, Any]]:
    document = read_strict_json(path or (AUDIO_ROOT / BOARD_TASK_ROW))
    tasks = document.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_not_list")
    rows: dict[str, dict[str, Any]] = {}
    for row in tasks:
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            rows[row["id"]] = row
    return rows


def board_row_projection(path: Path | None = None) -> dict[str, Any]:
    row = _board_rows(path).get(TASK)
    if row is None:
        raise ValueError("linked_task_row_missing")
    return _project_row(row)


def linked_rows(path: Path | None = None) -> list[dict[str, Any]]:
    rows = _board_rows(path)
    result = []
    for task_id in LINKED_ROW_IDS:
        row = rows.get(task_id)
        if row is None:
            raise ValueError("linked_row_missing:" + task_id)
        result.append(_project_row(row))
    return result


def linked_rows_digest(rows: list[dict[str, Any]] | None = None) -> str:
    return object_digest(rows if rows is not None else linked_rows())


def _probe(root: Path, relative: str, kind: str) -> dict[str, Any]:
    if (root / relative).exists():
        raise ValueError("unexpected_artifact_present:" + relative)
    return {"kind": kind, "path": relative, "present": False}


def absence_probes(root: Path) -> list[dict[str, Any]]:
    return [_probe(root, relative, "workspace")
            for relative in WORKSPACE_PROBES]


def home_absence_probes() -> list[dict[str, Any]]:
    home = Path.home()
    return [_probe(home, relative, "home") for relative in HOME_PROBES]


def absence_summary(workspace: list[dict[str, Any]],
                    home: list[dict[str, Any]]) -> dict[str, Any]:
    probes = workspace + home
    present = [row for row in probes if row["present"]]
    return {
        "probe_count": len(probes),
        "workspace_probe_count": len(workspace),
        "home_probe_count": len(home),
        "present_count": len(present),
        "all_probes_absent": not present,
        "download_attempted": False,
        "network_used": False,
        "recursive_workspace_walk": False,
        "source_or_runtime_imported": False,
        "weights_loaded": False,
        "weights_decoded": False,
        "model_executed": False,
        "audio_read": False,
    }


# --- Minimal ONNX protobuf structure scanner (shapes only) -----------------

def _varint(data: bytes, position: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while position < len(data) and shift < 70:
        byte = data[position]
        position += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, position
        shift += 7
    raise ValueError("protobuf_varint")


def _fields(data: bytes) -> list[tuple[int, int, Any]]:
    position = 0
    result: list[tuple[int, int, Any]] = []
    while position < len(data):
        key, position = _varint(data, position)
        number = key >> 3
        wire = key & 7
        if number == 0:
            raise ValueError("protobuf_field_zero")
        if wire == 0:
            value, position = _varint(data, position)
        elif wire == 1:
            if position + 8 > len(data):
                raise ValueError("protobuf_truncated")
            value = data[position:position + 8]
            position += 8
        elif wire == 2:
            length, position = _varint(data, position)
            if position + length > len(data):
                raise ValueError("protobuf_truncated")
            value = data[position:position + length]
            position += length
        elif wire == 5:
            if position + 4 > len(data):
                raise ValueError("protobuf_truncated")
            value = data[position:position + 4]
            position += 4
        else:
            raise ValueError("protobuf_wire")
        result.append((number, wire, value))
    return result


def _string_value(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("protobuf_utf8") from error


def _packed_int64(data: bytes) -> list[int]:
    values: list[int] = []
    position = 0
    while position < len(data):
        value, position = _varint(data, position)
        values.append(value)
    return values


def _tensor_meta(data: bytes) -> dict[str, Any]:
    shape: list[int] = []
    element_type: int | None = None
    raw = b""
    float_count = 0
    int_values: list[int] = []
    for number, wire, value in _fields(data):
        if number == 1 and wire == 0:
            shape.append(value)
        elif number == 2 and wire == 0:
            element_type = value
        elif number == 4 and wire == 5:
            float_count += 1
        elif number == 4 and wire == 2:
            if len(value) % 4:
                raise ValueError("tensor_float_truncated")
            float_count += len(value) // 4
        elif number == 7 and wire == 2:
            int_values.extend(_packed_int64(value))
        elif number == 7 and wire == 0:
            int_values.append(value)
        elif number == 9 and wire == 2:
            raw = value
    if any(dimension <= 0 for dimension in shape):
        raise ValueError("tensor_shape")
    count = 1
    for dimension in shape:
        count *= dimension
    if element_type is None:
        raise ValueError("tensor_type")
    if element_type == 1:
        observed = max(len(raw) // 4, float_count)
        if raw and len(raw) != count * 4:
            raise ValueError("tensor_raw_size")
        if not raw and float_count != count:
            raise ValueError("tensor_float_size")
        if observed != count:
            raise ValueError("tensor_count")
    elif element_type == 7:
        if raw:
            int_values.extend(_packed_int64(raw))
        if len(int_values) != count:
            raise ValueError("tensor_int_count")
    else:
        raise ValueError("tensor_element_type")
    return {"shape": tuple(shape), "count": count,
            "element_type": element_type, "int_values": int_values}


def _node_parts(data: bytes) -> tuple[str, list[str],
                                      list[tuple[str, bytes | None,
                                                 bytes | None]]]:
    op = ""
    outputs: list[str] = []
    attributes: list[tuple[str, bytes | None, bytes | None]] = []
    for number, wire, value in _fields(data):
        if number == 4 and wire == 2:
            op = _string_value(value)
        elif number == 2 and wire == 2:
            outputs.append(_string_value(value))
        elif number == 5 and wire == 2:
            name = ""
            graph = None
            tensor = None
            for sub_number, sub_wire, sub_value in _fields(value):
                if sub_number == 1 and sub_wire == 2:
                    name = _string_value(sub_value)
                elif sub_number == 6 and sub_wire == 2:
                    graph = sub_value
                elif sub_number == 5 and sub_wire == 2:
                    tensor = sub_value
            attributes.append((name, graph, tensor))
    return op, outputs, attributes


def _branch_tensors(graph: bytes) -> tuple[dict[str, dict[str, Any]], int]:
    found: dict[str, dict[str, Any]] = {}
    node_count = 0

    def walk(data: bytes, depth: int) -> None:
        nonlocal node_count
        if depth > 32:
            raise ValueError("graph_depth")
        for number, wire, value in _fields(data):
            if number != 1 or wire != 2:
                continue
            node_count += 1
            if node_count > 20000:
                raise ValueError("graph_nodes")
            op, outputs, attributes = _node_parts(value)
            for _name, subgraph, tensor in attributes:
                if tensor is not None and op == "Constant":
                    key = None
                    for output in outputs:
                        for suffix in MODEL_WINDOW_KEYS:
                            if output.endswith(suffix):
                                key = suffix
                                break
                        if key is not None:
                            break
                    if key is not None:
                        meta = _tensor_meta(tensor)
                        if key in found and found[key]["shape"] != meta["shape"]:
                            raise ValueError("duplicate_tensor_shape")
                        found[key] = meta
                if subgraph is not None:
                    walk(subgraph, depth + 1)

    walk(graph, 0)
    return found, node_count


def structural_graph() -> dict[str, Any]:
    if not (AUDIO_ROOT / MODEL_PATH).is_file():
        raise ValueError("model_absent")
    payload = (AUDIO_ROOT / MODEL_PATH).read_bytes()
    if len(payload) > MODEL_MAX_BYTES:
        raise ValueError("model_too_large")
    top = _fields(payload)
    ir_version = None
    producer = ""
    graph = None
    for number, wire, value in top:
        if number == 1 and wire == 0:
            ir_version = value
        elif number == 2 and wire == 2:
            producer = _string_value(value)
        elif number == 7 and wire == 2:
            graph = value
    if graph is None or ir_version != MODEL_IR_VERSION or producer != MODEL_PRODUCER:
        raise ValueError("model_header")
    inputs: list[str] = []
    outputs: list[str] = []
    rate_guard: int | None = None
    branches: dict[str, dict[str, Any]] = {}
    for number, wire, value in _fields(graph):
        if number == 11 and wire == 2:
            for sub_number, sub_wire, sub_value in _fields(value):
                if sub_number == 1 and sub_wire == 2:
                    inputs.append(_string_value(sub_value))
        elif number == 12 and wire == 2:
            for sub_number, sub_wire, sub_value in _fields(value):
                if sub_number == 1 and sub_wire == 2:
                    outputs.append(_string_value(sub_value))
        elif number == 1 and wire == 2:
            op, node_outputs, attributes = _node_parts(value)
            if op == "Constant" and "Constant_0_output" in node_outputs:
                for _name, _graph, tensor in attributes:
                    if tensor is not None:
                        meta = _tensor_meta(tensor)
                        if meta["element_type"] != 7 or len(meta["int_values"]) != 1:
                            raise ValueError("rate_guard")
                        rate_guard = meta["int_values"][0]
            if op == "If":
                for name, subgraph, _tensor in attributes:
                    if subgraph is None or name not in ("then_branch", "else_branch"):
                        continue
                    tensors, node_count = _branch_tensors(subgraph)
                    missing = [key for key in MODEL_WINDOW_KEYS if key not in tensors]
                    if missing:
                        raise ValueError("branch_tensor_missing:" + missing[0])
                    stft = tensors["stft.forward_basis_buffer"]["shape"]
                    if stft == STFT_16K:
                        rate = 16000
                        encoder = ENCODER_16K
                        parameters = PARAMETERS_16K
                    elif stft == STFT_8K:
                        rate = 8000
                        encoder = ENCODER_8K
                        parameters = PARAMETERS_8K
                    else:
                        raise ValueError("branch_stft_shape")
                    observed_encoder = tuple(
                        tensors[f"encoder.{index}.reparam_conv.weight"]["shape"]
                        for index in range(4))
                    if observed_encoder != encoder:
                        raise ValueError("branch_encoder_shape")
                    for index in range(4):
                        if tensors[f"encoder.{index}.reparam_conv.bias"]["shape"] != (encoder[index][0],):
                            raise ValueError("branch_encoder_bias")
                    observed_lstm = (
                        tensors["decoder.rnn.weight_ih"]["shape"],
                        tensors["decoder.rnn.weight_hh"]["shape"],
                        tensors["decoder.rnn.bias_ih"]["shape"],
                        tensors["decoder.rnn.bias_hh"]["shape"],
                    )
                    if observed_lstm != LSTM_SHAPES:
                        raise ValueError("branch_lstm_shape")
                    observed_decoder = (
                        tensors["decoder.decoder.2.weight"]["shape"],
                        tensors["decoder.decoder.2.bias"]["shape"],
                    )
                    if observed_decoder != DECODER_SHAPES:
                        raise ValueError("branch_decoder_shape")
                    observed_parameters = sum(row["count"] for row in tensors.values())
                    if observed_parameters != parameters:
                        raise ValueError("branch_parameter_count")
                    branches[str(rate)] = {
                        "decoder": [list(shape) for shape in observed_decoder],
                        "encoder": [list(shape) for shape in observed_encoder],
                        "lstm": [list(shape) for shape in observed_lstm],
                        "node_count": node_count,
                        "parameter_count": observed_parameters,
                        "stft": list(stft),
                        "weight_byte_count": observed_parameters * 4,
                    }
    if tuple(inputs) != GRAPH_INPUTS or tuple(outputs) != GRAPH_OUTPUTS:
        raise ValueError("graph_io")
    if rate_guard != 16000:
        raise ValueError("graph_rate_guard")
    if set(branches) != {"8000", "16000"}:
        raise ValueError("graph_branches")
    if sum(row["parameter_count"] for row in branches.values()) != PARAMETERS_TOTAL:
        raise ValueError("graph_parameter_total")
    if sum(row["weight_byte_count"] for row in branches.values()) != WEIGHT_BYTES_TOTAL:
        raise ValueError("graph_weight_bytes")
    result = {
        "branches": branches,
        "inputs": list(inputs),
        "ir_version": ir_version,
        "outputs": list(outputs),
        "producer_name": producer,
        "sample_rate_guard": rate_guard,
        "sample_rates": list(SAMPLE_RATES),
        "state_shape": list(STATE_SHAPE),
    }
    if object_digest(result) != STRUCTURAL_SHA256:
        raise ValueError("structural_digest")
    return result


def model_provenance() -> dict[str, Any]:
    path = AUDIO_ROOT / MODEL_PATH
    if not path.is_file():
        raise ValueError("model_absent")
    byte_count = path.stat().st_size
    digest = sha256_file(path)
    if byte_count != MODEL_BYTE_COUNT:
        raise ValueError("model_byte_count")
    if digest != MODEL_SHA256:
        raise ValueError("model_digest")
    structure = structural_graph()
    if structure["state_shape"] != list(STATE_SHAPE):
        raise ValueError("state_shape")
    return {
        "artifact_id": "ART-01",
        "byte_count": byte_count,
        "decoded": False,
        "executed": False,
        "license_reference": None,
        "license_reviewed": False,
        "path": MODEL_PATH,
        "present": True,
        "producer_name": structure["producer_name"],
        "provenance_conflict": True,
        "sha256": digest,
        "structural_match": True,
        "structural_sha256": STRUCTURAL_SHA256,
        "structure": structure,
        "upstream_release_tag": None,
        "version_proven": False,
        "version_labels": [
            {"label": "Silero VAD v5", "source": "cpp-library/README.md"},
            {"label": "pinned Silero v5 ONNX file",
             "source": "cpp-library/docs/api-contract.md"},
            {"label": "silero-vad 6.2.3 bundled standard ONNX (same SHA-256)",
             "source": "research/plans/F02/vad_sources.md"},
        ],
        "weights_loaded": False,
        "weights_decoded": False,
        "model_executed": False,
    }


def cadence_reference() -> dict[str, Any]:
    rows = []
    for rate, window, context in ((8000, 256, 32), (16000, 512, 64)):
        divisor = math.gcd(window, V0_FRAME_SAMPLES)
        cross_hop = window * V0_FRAME_SAMPLES // divisor
        rows.append({
            "availability_quantization_ms": MODEL_HOP_MS,
            "context_samples": context,
            "cross_hop_model_windows": cross_hop // window,
            "cross_hop_samples": cross_hop,
            "cross_hop_v0_frames": cross_hop // V0_FRAME_SAMPLES,
            "input_samples_per_model_step": window + context,
            "model_window_samples": window,
            "sample_rate_hz": rate,
            "v0_frames_per_model_window": "{}/{}".format(
                window // divisor, V0_FRAME_SAMPLES // divisor),
            "window_ms": window * 1000 // rate,
        })
    return {
        "availability": {
            "exact_10ms_alignment": False,
            "model_quantization_ms": MODEL_HOP_MS,
            "v0_frame_ms": V0_FRAME_SAMPLES * 1000 // 16000,
        },
        "public_v0_frame_samples": V0_FRAME_SAMPLES,
        "public_v0_sample_rate_hz": 16000,
        "rates": rows,
        "warmup": {
            "declared_initial_context": "zeros",
            "declared_initial_state": "zeros",
            "exact_warmup_parity": False,
            "local_cpp_stage_caches_last_probability": True,
            "local_cpp_stage_silent_shortcut_windows": 3,
            "upstream_v5_wrapper_source_present": False,
            "verified_against_upstream_v5_wrapper": False,
        },
        "wrapper": {
            "context_samples_16k": CADENCE_16K[1],
            "context_samples_8k": CADENCE_8K[1],
            "model_window_samples_16k": CADENCE_16K[0],
            "model_window_samples_8k": CADENCE_8K[0],
            "threshold": "0.5",
            "threshold_verified": False,
        },
    }


def runtime_recorded() -> dict[str, Any]:
    return {
        "deterministic": None,
        "exact_runtime_present": False,
        "exact_v5_runtime_recorded": False,
        "incidental_onnxruntime_used": False,
        "inter_op_threads": 1,
        "intra_op_threads": 1,
        "name": None,
        "offline": None,
        "python": None,
        "runtime_imported": False,
        "version": None,
        "wheel_sha256": None,
    }


def source_presence(model: dict[str, Any] | None = None) -> dict[str, Any]:
    model = model or model_provenance()
    return {
        "audio_read": False,
        "corpus_present": False,
        "exact_model_version_proven": False,
        "exact_runtime_present": False,
        "exact_source_weights_runtime_conjunction_present": False,
        "license_files_present": False,
        "model_artifact_present": model["present"],
        "model_executed": False,
        "network_used": False,
        "reference_outputs_present": False,
        "runtime_imported": False,
        "upstream_source_present": False,
        "weights_decoded": False,
        "weights_used": False,
    }


def qualification(model: dict[str, Any] | None = None) -> dict[str, Any]:
    model = model or model_provenance()
    return {
        "all_release_gates_blocked": True,
        "analysis_result": False,
        "benchmark_result": False,
        "corpus_present": False,
        "device_timing_result": False,
        "exact_model_version_proven": False,
        "exact_runtime_present": False,
        "license_present": False,
        "listening_result": False,
        "missing_result_promoted": False,
        "model_artifact_present": model["present"],
        "not_qualified": True,
        "readiness": "incomplete",
        "real_result_present": False,
        "reference_outputs_present": False,
        "release_claim": False,
        "runtime_present": False,
        "status": "not_qualified",
        "upstream_source_present": False,
        "weights_present": model["present"],
        "weights_used": False,
    }


def analysis_requirements() -> list[dict[str, Any]]:
    rows = (
        ("ANAL-01", "Score timestamped probabilities.",
         "No probability trace exists; the model was not executed."),
        ("ANAL-02", "Score event boundaries and detections.",
         "No event boundary or detection output exists."),
        ("ANAL-03", "Include quiet and active speech and idle noise.",
         "No rights-cleared audio or condition-stratified cohort is present."),
        ("ANAL-04", "Include known positives and negatives.",
         "No labeled positive or negative case is present."),
        ("ANAL-05", "Measure onset and offset delay.",
         "No timestamped reference or model output exists."),
        ("ANAL-06", "Report stratified false negatives and false positives.",
         "No scored condition groups or predictions exist."),
        ("ANAL-07", "Separate validity from nonspeech.",
         "No validity policy was exercised against a caller-supplied trace."),
        ("ANAL-08", "Verify independent state, exact source intervals, "
                    "availability, dropped/stale events and cross-hop behavior.",
         "No independent state, interval, availability or cross-hop run exists."),
    )
    return [{"evidence": evidence, "id": identifier, "qualifies": False,
             "requirement": requirement, "status": "blocked", "value": None}
            for identifier, requirement, evidence in rows]


def quality_outcomes() -> list[dict[str, Any]]:
    rows = (
        ("QUAL-01", "probability_scoring",
         "No probability output or scorer exists."),
        ("QUAL-02", "event_boundary_and_detection_scoring",
         "No event boundary or detection output exists."),
        ("QUAL-03", "onset_offset_delay",
         "No timestamped reference pair exists."),
        ("QUAL-04", "stratified_fn_fp_and_controls",
         "No condition labels, predictions, finite-output scan or adverse/"
         "missing/nonfinite control exists."),
    )
    return [{"evidence": evidence, "id": identifier, "outcome": outcome,
             "qualifies": False, "status": "blocked", "value": None}
            for identifier, outcome, evidence in rows]


def timing_requirements() -> list[dict[str, Any]]:
    rows = (
        ("TIME-01", "feature_and_model_inference",
         "No model or front end was executed."),
        ("TIME-02", "wrapper_cadence_and_availability",
         "No paced wrapper or availability trace was measured."),
        ("TIME-03", "end_to_end_p95",
         "No end-to-end analysis path exists."),
        ("TIME-04", "device_deadline_and_resources",
         "No target device, callback, CPU/memory, thermal or energy measurement "
         "exists."),
    )
    return [{"evidence": evidence, "id": identifier, "metric": metric,
             "qualifies": False, "status": "blocked", "value": None}
            for identifier, metric, evidence in rows]


def required_artifacts(model: dict[str, Any] | None = None
                       ) -> list[dict[str, Any]]:
    model = model or model_provenance()
    rows: list[dict[str, Any]] = [{
        "blocked": False,
        "id": "ART-01",
        "kind": "local_wrapper_source_and_present_onnx_artifact",
        "present": True,
        "requirement": "The local ONNX Runtime and native wrappers plus the one "
                       "present ONNX file, pinned by SHA-256 and structurally "
                       "scanned without tensor decoding.",
        "revision": None,
        "sha256": None,
        "verified": model["structural_match"],
    }]
    spec = (
        ("ART-02", "exact_upstream_source_version_and_weight_terms",
         "Exact upstream v5 source revision and wrapper plus a reviewed "
         "license/notice and trained-weight product-use decision."),
        ("ART-03", "pinned_deterministic_runtime",
         "A locked offline 8/16 kHz runtime with exact versions, wheel hashes, "
         "install/import digest and deterministic CPU/thread settings."),
        ("ART-04", "exact_reference_outputs_and_controls",
         "Frozen PCM/probability/event outputs with digests, tolerance, warmup, "
         "reset, finite, adverse, missing, stale and nonfinite controls."),
        ("ART-05", "rights_cleared_analysis_cohort",
         "A continuous-label cohort with quiet/active speech, idle noise, known "
         "positives/negatives, onset/offset labels and reviewed terms."),
        ("ART-06", "reproduced_analysis_results",
         "Reproduced timestamped probabilities, boundaries, detections, validity, "
         "exact intervals, independent state, cross-hop and stratified FN/FP."),
        ("ART-07", "device_availability_and_deadline_timing",
         "Target-device availability, pacing, deadline, resource, finite drain "
         "and reset timing."),
        ("ART-08", "off_by_default_provider_intake",
         "A separate versioned OFF-by-default provider intake with an exact "
         "asset descriptor and independent exact-head review."),
    )
    for identifier, kind, requirement in spec:
        rows.append({
            "blocked": True,
            "id": identifier,
            "kind": kind,
            "present": False,
            "requirement": requirement,
            "revision": None,
            "sha256": None,
            "verified": False,
        })
    return rows


def exact_blockers() -> list[dict[str, Any]]:
    rows = (
        ("BLK-01", "ART-02", ("RG-01", "RG-02"),
         "One ONNX file is present, but its version is not proven: in-repo "
         "documents call SHA-256 1a153a22f4509e292a94e67d6f9b85e8deb25b4988682b7e174c65279d8788e3 "
         "the v5 graph, while research/plans/F02/vad_sources.md records the same "
         "digest as the silero-vad 6.2.3 bundled standard graph. No upstream "
         "release tag, commit, model card, per-weight terms or license/notice "
         "bundle is present.",
         "Supply the exact upstream v5 release tag/commit and wrapper source, an "
         "artifact manifest that resolves the version conflict, and a reviewed "
         "license/notice and trained-weight product-use decision."),
        ("BLK-02", "ART-04", ("RG-02", "RG-04"),
         "No frozen PCM/probability/event oracle or reference output exists. The "
         "local cpp wrapper aggregates 160-sample v0 frames, caches the last "
         "probability and adds a three-silent-window shortcut, so it is not an "
         "independent exact v5 wrapper, and its warmup/reset parity is unproven.",
         "Provide the exact upstream wrapper and warmup/reset semantics, plus "
         "frozen fixtures and outputs with SHA-256, tolerance, and finite/"
         "adverse/missing/stale/nonfinite controls reproduced three times."),
        ("BLK-03", "ART-03", ("RG-03",),
         "No pinned v5 runtime exists. No Python, ONNX Runtime, NumPy or wheel "
         "hash, install/import digest, deterministic setting or offline lock is "
         "recorded for v5. The unrelated playback-speed venv is neither the v5 "
         "historical runtime nor pinned and is not imported or used.",
         "Supply a locked offline runtime for 8 kHz and 16 kHz with exact "
         "versions, every wheel hash, one install/import digest, deterministic "
         "algorithms and one intra-op/inter-op thread."),
        ("BLK-04", "ART-05", ("RG-05",),
         "No rights-cleared continuous-label analysis cohort is present. The "
         "merged Silero evidence packages use synthetic traces, surrogate "
         "features or a model-free stub and cannot substitute for v5 audio "
         "labels.",
         "Freeze a permitted cohort with quiet and active speech, idle noise, "
         "known positives/negatives, onset/offset labels, language/speaker "
         "groups, exact source intervals and reviewed corpus/annotation terms."),
        ("BLK-05", "ART-06", ("RG-06",),
         "No timestamped probability, event boundary, detection, onset/offset "
         "delay, validity-separated, stratified FN/FP, independent-state, "
         "exact-interval, availability, dropped/stale-event or cross-hop result "
         "was produced. No result may be inferred from the file or a sibling.",
         "Reproduce the Analysis profile on the qualified cohort with a frozen "
         "scorer, exact intervals, independent state, finite/adverse/missing/"
         "nonfinite controls and stratified FN/FP."),
        ("BLK-06", "ART-07", ("RG-07", "RG-08"),
         "No target-device availability, paced timing, deadline, resource, "
         "finite-drain or reset measurement exists, and no provider/descriptor/"
         "registry/default/shared-build/CI intake or release review exists.",
         "Measure target-device paced availability, p95/p99, resources and "
         "deadlines, then open a separate versioned OFF-by-default provider "
         "intake with independent exact-head review after every earlier gate."),
    )
    return [{
        "artifact_id": artifact,
        "id": identifier,
        "linked_gates": list(gates),
        "qualifies": False,
        "required_action": action,
        "statement": statement,
        "status": "open",
    } for identifier, artifact, gates, statement, action in rows]


def release_gates(board_row: dict[str, Any] | None = None
                  ) -> list[dict[str, Any]]:
    row = board_row or board_row_projection()
    rows = (
        ("RG-01", "source_revision_and_weight_license_provenance",
         "In-repo labels disagree on whether the present ONNX bytes are v5 or "
         "the 6.2.3 bundled graph; no upstream revision, model card, license, "
         "notice or product-use decision is staged.",
         "Stage the exact upstream v5 source revision, artifact manifest, "
         "license/notice bundle and reviewed product-use decision."),
        ("RG-02", "exact_graph_wrapper_cadence_and_warmup_parity",
         "The graph is structurally consistent with the documented v5 8/16 kHz "
         "shape, but no independent wrapper oracle, warmup policy, reset policy "
         "or output parity exists.",
         "Provide an exact upstream wrapper plus frozen 8 kHz and 16 kHz "
         "outputs, warmup/reset rules and a reproducible tolerance."),
        ("RG-03", "pinned_deterministic_runtime",
         "No exact v5 Python/ONNX Runtime lock, wheel hashes, install/import "
         "digest or deterministic thread setting is recorded.",
         "Provide a locked offline runtime with every wheel hash, import digest, "
         "deterministic algorithms and 1/1 threads."),
        ("RG-04", "frozen_reference_outputs_and_controls",
         "No PCM fixture, probability trace, event stream or finite/adverse/"
         "missing/stale/nonfinite control is present.",
         "Freeze caller-supplied fixtures and outputs with digests and "
         "rejection controls, and regenerate them three times."),
        ("RG-05", "rights_cleared_analysis_cohort",
         "No rights-cleared continuous-label cohort covers quiet/active speech, "
         "idle noise, known positives/negatives, onset/offset or speaker/language "
         "groups.",
         "Freeze the permitted cohort, labels, source intervals and corpus terms."),
        ("RG-06", "reproduced_analysis_and_stratified_results",
         "No timestamped probability, boundary, detection, validity, interval, "
         "state, availability, cross-hop or stratified FN/FP result exists.",
         "Reproduce the full Analysis profile with a frozen scorer, exact "
         "intervals, independent state and controls."),
        ("RG-07", "target_device_availability_and_deadline_timing",
         "No paced availability, p95/p99, deadline, resource, finite-drain or "
         "reset timing exists.",
         "Measure paced target-device availability, deadlines, resources and "
         "finite drain."),
        ("RG-08", "off_by_default_provider_intake_and_release_review",
         "No provider, descriptor, registry/default/shared-build/CI change or "
         "independent exact-head release review exists.",
         "Open a separate OFF-by-default versioned intake and obtain independent "
         "exact-head review after every earlier gate clears."),
    )
    return [{
        "id": identifier,
        "linked_row": row,
        "qualifies": False,
        "reopen_condition": reopen,
        "statement": statement,
        "status": "blocked",
        "title": title,
    } for identifier, title, statement, reopen in rows]


def scope() -> dict[str, Any]:
    return {
        "adapter_implemented": False,
        "benchmark_run": False,
        "device_timing_measured": False,
        "listening_performed": False,
        "model_executed": False,
        "network_used": False,
        "provider_registered": False,
        "public_abi_changed": False,
        "real_assets_used": False,
        "registry_or_default_changed": False,
        "release_claim": False,
        "shared_build_or_ci_changed": False,
        "task_local_only": True,
        "weights_decoded": False,
        "write_scope": WRITE_SCOPE,
    }


def boundary() -> dict[str, Any]:
    rows = linked_rows()
    row = board_row_projection()
    return {
        "board_file_pinned": False,
        "linked_row": row,
        "linked_row_identity_only": True,
        "linked_row_sha256": object_digest(row),
        "linked_rows": rows,
        "linked_rows_sha256": linked_rows_digest(rows),
        "mutable_board_fields_gate": False,
        "projected_fields": list(BOARD_ROW_FIELDS),
    }


def public_v0_geometry() -> dict[str, Any]:
    return {
        "channels": 1,
        "changed": False,
        "frame_samples": V0_FRAME_SAMPLES,
        "sample_format": "float32",
        "sample_rate_hz": 16000,
    }


def input_inventory() -> list[dict[str, Any]]:
    roles = {
        MODEL_PATH: "present ONNX artifact; hashed and structurally scanned only",
        "silero_vad.cpp": "existing ONNX Runtime wrapper, read-only provenance",
        "silero_vad_native.cpp": "existing native wrapper and cadence/warmup provenance",
        "audio_enhance_models.json": "pinned model hash and license caveat",
        "api-contract.md": "v5 label and 512+64/16 kHz wrapper statement",
        "qualification.md": "native v5 smoke scope and exclusions",
        "extension-guide.md": "v5 native parameter-extraction statement",
        "README.md": "v5 native provider boundary",
        "results.json": "recorded model SHA-256 and timing context; not a result",
        "vad_sources.md": "conflicting 6.2.3 bundled-standard provenance for the same hash",
        "adapter.json": "6.2.3 adapter identity, not a v5 reference",
        "run.py": "6.2.3 adapter code, not a v5 reference",
        "INVENTORY.json": "component row and Analysis profile",
        "VERIFICATION.md": "Analysis acceptance profile",
        "README.md#audio-sdk": "SDK delivery boundary",
    }
    rows: list[dict[str, Any]] = []
    for relative, digest in sorted(SOURCE_PINS.items()):
        name = relative.rsplit("/", 1)[-1]
        role = roles.get(name, "pinned input")
        if relative.endswith("plan/audio-sdk/README.md"):
            role = roles["README.md#audio-sdk"]
        rows.append({
            "byte_count": (AUDIO_ROOT / relative).stat().st_size,
            "path": "source:" + relative,
            "role": role,
            "sha256": digest,
        })
    for relative, digest in sorted(BOUNDARY_PINS.items()):
        rows.append({
            "byte_count": (WORKTREE / relative).stat().st_size,
            "path": relative,
            "role": "unchanged shared boundary or merged Silero evidence",
            "sha256": digest,
        })
    return rows


def pin_rows(pins: dict[str, str], root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for relative, expected in sorted(pins.items()):
        path = root / relative
        if not path.is_file():
            raise ValueError("pin_missing:" + relative)
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError("pin_mismatch:" + relative)
        rows[relative] = {"actual": actual, "sha256": expected,
                          "verified": actual == expected}
    return rows


# --- Caller-supplied reference bundle admission (schema only) ---------------

ADMISSION_FIELDS = ("schema_id", "bundle_id", "model", "source", "runtime",
                    "cadence", "fixtures", "rights", "controls", "outcomes")
MODEL_FIELDS = ("sha256", "byte_count", "producer", "ir_version", "inputs",
                "outputs", "sample_rates", "structural_sha256")
SOURCE_FIELDS = ("repository", "revision", "license_reference", "wrapper_path",
                 "wrapper_sha256")
RUNTIME_FIELDS = ("name", "version", "python", "wheel_sha256",
                  "intra_op_threads", "inter_op_threads", "deterministic",
                  "offline")
CADENCE_FIELDS = ("sample_rate_hz", "window_samples", "context_samples",
                  "state_shape", "threshold", "warmup_policy", "reset_policy")
FIXTURE_FIELDS = ("id", "sample_rate_hz", "samples", "pcm_sha256",
                  "probabilities_sha256", "event_sha256", "nonfinite_count")
RIGHTS_FIELDS = ("model_terms_reference", "source_license_reference",
                 "corpus_terms_reference", "output_use_reference",
                 "review_reference", "claims_qualified")
CONTROL_FIELDS = ("finite", "missing", "adverse", "nonfinite", "stale")
OUTCOME_FIELDS = ("probability_score", "event_score", "onset_offset_delay",
                  "stratified_fn_fp", "qualifies")
CONTROL_EXPECTED = {
    "adverse": "rejected",
    "finite": "passed",
    "missing": "rejected",
    "nonfinite": "rejected",
    "stale": "rejected",
}
WARMUP_POLICY = "zero_initial_state_and_zero_context"
RESET_POLICY = "zero_state_zero_context_per_stream"


def _validate_model(value: Any) -> None:
    _require_exact_keys(value, MODEL_FIELDS, "model_fields")
    if _require_hex64(value["sha256"], "model_sha256") != MODEL_SHA256:
        raise AdmissionError("model_sha256")
    if _require_int(value["byte_count"], "model_byte_count") != MODEL_BYTE_COUNT:
        raise AdmissionError("model_byte_count")
    if value["producer"] != MODEL_PRODUCER:
        raise AdmissionError("model_producer")
    if _require_int(value["ir_version"], "model_ir_version") != MODEL_IR_VERSION:
        raise AdmissionError("model_ir_version")
    if value["inputs"] != list(GRAPH_INPUTS):
        raise AdmissionError("model_inputs")
    if value["outputs"] != list(GRAPH_OUTPUTS):
        raise AdmissionError("model_outputs")
    if value["sample_rates"] != list(SAMPLE_RATES):
        raise AdmissionError("model_sample_rates")
    if _require_hex64(value["structural_sha256"],
                      "model_structural_sha256") != STRUCTURAL_SHA256:
        raise AdmissionError("model_structural_sha256")


def _validate_source(value: Any) -> None:
    _require_exact_keys(value, SOURCE_FIELDS, "source_fields")
    repository = _require_text(value["repository"], "source_repository", 512)
    if not re.fullmatch(r"[A-Za-z0-9._/@:+-]+", repository):
        raise AdmissionError("source_repository")
    if not isinstance(value["revision"], str) or not re.fullmatch(
            r"[0-9a-f]{40}", value["revision"]):
        raise AdmissionError("source_revision")
    _require_text(value["license_reference"], "source_license_reference", 512)
    _require_text(value["wrapper_path"], "source_wrapper_path", 512)
    _require_hex64(value["wrapper_sha256"], "source_wrapper_sha256")


def _validate_runtime(value: Any) -> None:
    _require_exact_keys(value, RUNTIME_FIELDS, "runtime_fields")
    if value["name"] != "onnxruntime":
        raise AdmissionError("runtime_name")
    _require_version(value["version"], "runtime_version")
    _require_version(value["python"], "runtime_python")
    _require_hex64(value["wheel_sha256"], "runtime_wheel_sha256")
    if _require_int(value["intra_op_threads"], "runtime_intra_threads") != 1:
        raise AdmissionError("runtime_intra_threads")
    if _require_int(value["inter_op_threads"], "runtime_interop_threads") != 1:
        raise AdmissionError("runtime_interop_threads")
    if _require_bool(value["deterministic"], "runtime_deterministic") is not True:
        raise AdmissionError("runtime_deterministic")
    if _require_bool(value["offline"], "runtime_offline") is not True:
        raise AdmissionError("runtime_offline")


def _validate_cadence(value: Any) -> None:
    _require_exact_keys(value, CADENCE_FIELDS, "cadence_fields")
    rate = _require_int(value["sample_rate_hz"], "cadence_rate")
    if rate == 16000:
        expected = CADENCE_16K
    elif rate == 8000:
        expected = CADENCE_8K
    else:
        raise AdmissionError("cadence_rate")
    if _require_int(value["window_samples"], "cadence_window") != expected[0]:
        raise AdmissionError("cadence_window")
    if _require_int(value["context_samples"], "cadence_context") != expected[1]:
        raise AdmissionError("cadence_context")
    if value["state_shape"] != list(STATE_SHAPE):
        raise AdmissionError("cadence_state_shape")
    if _require_decimal(value["threshold"], "cadence_threshold") != "0.5":
        raise AdmissionError("cadence_threshold")
    if value["warmup_policy"] != WARMUP_POLICY:
        raise AdmissionError("cadence_warmup_policy")
    if value["reset_policy"] != RESET_POLICY:
        raise AdmissionError("cadence_reset_policy")


def _validate_fixtures(value: Any) -> None:
    if not isinstance(value, list) or len(value) != 8:
        raise AdmissionError("fixtures_count")
    seen: set[str] = set()
    rates: set[int] = set()
    for fixture in value:
        _require_exact_keys(fixture, FIXTURE_FIELDS, "fixture_fields")
        identifier = _require_text(fixture["id"], "fixture_id", 64)
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}", identifier):
            raise AdmissionError("fixture_id")
        if identifier in seen:
            raise AdmissionError("fixture_duplicate_id")
        seen.add(identifier)
        rate = _require_int(fixture["sample_rate_hz"], "fixture_rate")
        if rate not in SAMPLE_RATES:
            raise AdmissionError("fixture_rate")
        rates.add(rate)
        _require_int(fixture["samples"], "fixture_samples", 1, 2 ** 31 - 1)
        _require_hex64(fixture["pcm_sha256"], "fixture_pcm_sha256")
        _require_hex64(fixture["probabilities_sha256"],
                       "fixture_probabilities_sha256")
        _require_hex64(fixture["event_sha256"], "fixture_event_sha256")
        if _require_int(fixture["nonfinite_count"],
                        "fixture_nonfinite_count") != 0:
            raise AdmissionError("fixture_nonfinite_count")
    if rates != set(SAMPLE_RATES):
        raise AdmissionError("fixture_rate_coverage")


def _validate_rights(value: Any) -> None:
    _require_exact_keys(value, RIGHTS_FIELDS, "rights_fields")
    for field in RIGHTS_FIELDS[:-1]:
        _require_text(value[field], "rights_" + field, 512)
    if _require_bool(value["claims_qualified"],
                     "rights_claims_qualified") is not False:
        raise AdmissionError("rights_claims_qualified")


def _validate_controls(value: Any) -> None:
    _require_exact_keys(value, CONTROL_FIELDS, "controls_fields")
    for field in CONTROL_FIELDS:
        if value[field] != CONTROL_EXPECTED[field]:
            raise AdmissionError("controls_" + field)


def _validate_outcomes(value: Any) -> None:
    _require_exact_keys(value, OUTCOME_FIELDS, "outcomes_fields")
    for field in OUTCOME_FIELDS[:-1]:
        text = value[field]
        if not isinstance(text, str):
            raise AdmissionError("outcomes_" + field)
        if text != "not_measured":
            _require_decimal(text, "outcomes_" + field)
    if _require_bool(value["qualifies"], "outcomes_qualifies") is not False:
        raise AdmissionError("outcomes_qualifies")


def admit_bundle(value: Any) -> dict[str, Any]:
    """Validate a caller-supplied reference bundle; never qualify it."""
    _no_floats(value)
    _require_exact_keys(value, ADMISSION_FIELDS, "bundle_fields")
    if value["schema_id"] != ADMISSION_SCHEMA_ID:
        raise AdmissionError("schema_id")
    bundle_id = _require_text(value["bundle_id"], "bundle_id", 64)
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}", bundle_id):
        raise AdmissionError("bundle_id")
    _validate_model(value["model"])
    _validate_source(value["source"])
    _validate_runtime(value["runtime"])
    _validate_cadence(value["cadence"])
    _validate_fixtures(value["fixtures"])
    _validate_rights(value["rights"])
    _validate_controls(value["controls"])
    _validate_outcomes(value["outcomes"])
    return {"accepted": True, "code": "admitted_schema_only",
            "qualifies": False, "state_unchanged": False}


def admission_control() -> dict[str, Any]:
    """A structurally valid synthetic control; never evidence."""
    digests = [sha256_bytes(("control-pcm-" + str(index)).encode("ascii"))
               for index in range(8)]
    fixtures = []
    for index in range(8):
        fixture = {
            "event_sha256": sha256_bytes(("control-event-" + str(index)).encode("ascii")),
            "id": "synthetic-control-" + str(index),
            "nonfinite_count": 0,
            "pcm_sha256": digests[index],
            "probabilities_sha256": sha256_bytes(
                ("control-probabilities-" + str(index)).encode("ascii")),
            "sample_rate_hz": 16000 if index % 2 else 8000,
            "samples": 16000 if index % 2 else 8000,
        }
        fixtures.append(fixture)
    return {
        "bundle_id": "synthetic-schema-control",
        "cadence": {
            "context_samples": CADENCE_16K[1],
            "reset_policy": RESET_POLICY,
            "sample_rate_hz": 16000,
            "state_shape": list(STATE_SHAPE),
            "threshold": "0.5",
            "warmup_policy": WARMUP_POLICY,
            "window_samples": CADENCE_16K[0],
        },
        "controls": dict(CONTROL_EXPECTED),
        "fixtures": fixtures,
        "model": {
            "byte_count": MODEL_BYTE_COUNT,
            "inputs": list(GRAPH_INPUTS),
            "ir_version": MODEL_IR_VERSION,
            "outputs": list(GRAPH_OUTPUTS),
            "producer": MODEL_PRODUCER,
            "sample_rates": list(SAMPLE_RATES),
            "sha256": MODEL_SHA256,
            "structural_sha256": STRUCTURAL_SHA256,
        },
        "outcomes": {
            "event_score": "not_measured",
            "onset_offset_delay": "not_measured",
            "probability_score": "not_measured",
            "qualifies": False,
            "stratified_fn_fp": "not_measured",
        },
        "rights": {
            "claims_qualified": False,
            "corpus_terms_reference": "synthetic-control-not-a-rights-grant",
            "model_terms_reference": "synthetic-control-not-a-rights-grant",
            "output_use_reference": "synthetic-control-not-a-rights-grant",
            "review_reference": "synthetic-control-not-a-review",
            "source_license_reference": "synthetic-control-not-a-rights-grant",
        },
        "runtime": {
            "deterministic": True,
            "inter_op_threads": 1,
            "intra_op_threads": 1,
            "name": "onnxruntime",
            "offline": True,
            "python": "3.12.16",
            "version": "1.24.1",
            "wheel_sha256": sha256_bytes(b"synthetic-control-wheel"),
        },
        "schema_id": ADMISSION_SCHEMA_ID,
        "source": {
            "license_reference": "synthetic-control-not-a-rights-grant",
            "repository": "synthetic/schema-control",
            "revision": "0" * 40,
            "wrapper_path": "synthetic/control.py",
            "wrapper_sha256": sha256_bytes(b"synthetic-control-wrapper"),
        },
    }


def _reject_case(identifier: str, mutator: Any,
                 expected_code: str) -> dict[str, Any]:
    candidate = copy.deepcopy(admission_control())
    mutator(candidate)
    try:
        admit_bundle(candidate)
    except AdmissionError as error:
        if error.code != expected_code:
            raise ValueError("admission_code_mismatch:{}:{}:{}".format(
                identifier, expected_code, error.code))
        return {"code": error.code, "id": identifier, "qualifies": False,
                "state_unchanged": True, "status": "rejected"}
    raise ValueError("admission_case_accepted:" + identifier)


def admission_cases() -> list[dict[str, Any]]:
    def delete_rights(bundle: dict[str, Any]) -> None:
        del bundle["rights"]

    def add_extra(bundle: dict[str, Any]) -> None:
        bundle["extra"] = True

    def bad_schema(bundle: dict[str, Any]) -> None:
        bundle["schema_id"] = "audio-sdk/not-the-schema/0.1"

    def bad_model_digest(bundle: dict[str, Any]) -> None:
        bundle["model"]["sha256"] = "0" * 64

    def bad_model_bytes(bundle: dict[str, Any]) -> None:
        bundle["model"]["byte_count"] = 1

    def bad_producer(bundle: dict[str, Any]) -> None:
        bundle["model"]["producer"] = "other"

    def bad_structural(bundle: dict[str, Any]) -> None:
        bundle["model"]["structural_sha256"] = "1" * 64

    def bad_rates(bundle: dict[str, Any]) -> None:
        bundle["model"]["sample_rates"] = [16000]

    def bad_revision(bundle: dict[str, Any]) -> None:
        bundle["source"]["revision"] = "abc"

    def missing_license(bundle: dict[str, Any]) -> None:
        bundle["source"]["license_reference"] = ""

    def bad_runtime_version(bundle: dict[str, Any]) -> None:
        bundle["runtime"]["version"] = "1.24"

    def two_threads(bundle: dict[str, Any]) -> None:
        bundle["runtime"]["intra_op_threads"] = 2

    def not_deterministic(bundle: dict[str, Any]) -> None:
        bundle["runtime"]["deterministic"] = False

    def mismatch_window(bundle: dict[str, Any]) -> None:
        bundle["cadence"]["sample_rate_hz"] = 8000
        bundle["cadence"]["window_samples"] = 512

    def bad_state(bundle: dict[str, Any]) -> None:
        bundle["cadence"]["state_shape"] = [2, 1, 64]

    def noncanonical_threshold(bundle: dict[str, Any]) -> None:
        bundle["cadence"]["threshold"] = "0.50"

    def bad_pcm(bundle: dict[str, Any]) -> None:
        bundle["fixtures"][0]["pcm_sha256"] = "f" * 63

    def nonfinite_fixture(bundle: dict[str, Any]) -> None:
        bundle["fixtures"][0]["nonfinite_count"] = 1

    def duplicate_fixture(bundle: dict[str, Any]) -> None:
        bundle["fixtures"][1]["id"] = bundle["fixtures"][0]["id"]

    def rights_qualified(bundle: dict[str, Any]) -> None:
        bundle["rights"]["claims_qualified"] = True

    def controls_fail(bundle: dict[str, Any]) -> None:
        bundle["controls"]["nonfinite"] = "passed"

    def outcome_qualified(bundle: dict[str, Any]) -> None:
        bundle["outcomes"]["qualifies"] = True

    def drop_rate(bundle: dict[str, Any]) -> None:
        bundle["fixtures"] = [row for row in bundle["fixtures"]
                              if row["sample_rate_hz"] == 16000]

    def drop_field(bundle: dict[str, Any]) -> None:
        del bundle["model"]["sha256"]

    return [
        _reject_case("ADM-01", delete_rights, "bundle_fields"),
        _reject_case("ADM-02", add_extra, "bundle_fields"),
        _reject_case("ADM-03", bad_schema, "schema_id"),
        _reject_case("ADM-04", bad_model_digest, "model_sha256"),
        _reject_case("ADM-05", bad_model_bytes, "model_byte_count"),
        _reject_case("ADM-06", bad_producer, "model_producer"),
        _reject_case("ADM-07", bad_structural, "model_structural_sha256"),
        _reject_case("ADM-08", bad_rates, "model_sample_rates"),
        _reject_case("ADM-09", drop_field, "model_fields"),
        _reject_case("ADM-10", bad_revision, "source_revision"),
        _reject_case("ADM-11", missing_license, "source_license_reference"),
        _reject_case("ADM-12", bad_runtime_version, "runtime_version"),
        _reject_case("ADM-13", two_threads, "runtime_intra_threads"),
        _reject_case("ADM-14", not_deterministic, "runtime_deterministic"),
        _reject_case("ADM-15", mismatch_window, "cadence_window"),
        _reject_case("ADM-16", bad_state, "cadence_state_shape"),
        _reject_case("ADM-17", noncanonical_threshold, "cadence_threshold"),
        _reject_case("ADM-18", bad_pcm, "fixture_pcm_sha256"),
        _reject_case("ADM-19", nonfinite_fixture, "fixture_nonfinite_count"),
        _reject_case("ADM-20", duplicate_fixture, "fixture_duplicate_id"),
        _reject_case("ADM-21", drop_rate, "fixtures_count"),
        _reject_case("ADM-22", rights_qualified, "rights_claims_qualified"),
        _reject_case("ADM-23", controls_fail, "controls_nonfinite"),
        _reject_case("ADM-24", outcome_qualified, "outcomes_qualifies"),
    ]


def admission_report() -> dict[str, Any]:
    cases = admission_cases()
    control = admission_control()
    admitted = admit_bundle(control)
    control_result = {
        "accepted": admitted["accepted"],
        "code": admitted["code"],
        "qualifies": admitted["qualifies"],
        "synthetic_schema_control_not_evidence": True,
    }
    return {
        "cases": cases,
        "control": control_result,
        "summary": {
            "accepted_schema_controls": 1,
            "audio_read": False,
            "case_count": len(cases),
            "model_executed": False,
            "network_used": False,
            "qualifying_results": 0,
            "rejected_count": len(cases),
            "runtime_invoked": False,
            "state_advanced_on_rejection": False,
            "weights_loaded": False,
        },
    }


def admission_schema() -> dict[str, Any]:
    return {
        "admission_only": True,
        "bundle_fields": list(ADMISSION_FIELDS),
        "cadence": {
            "exact_state_shape": list(STATE_SHAPE),
            "exact_threshold": "0.5",
            "exact_warmup_policy": WARMUP_POLICY,
            "exact_reset_policy": RESET_POLICY,
            "rate_windows": {"8000": list(CADENCE_8K), "16000": list(CADENCE_16K)},
            "sample_rates": list(SAMPLE_RATES),
        },
        "control": {
            "accepted_for_schema_only": True,
            "qualifies": False,
            "synthetic_schema_control_not_evidence": True,
        },
        "controls": dict(CONTROL_EXPECTED),
        "fixture_fields": list(FIXTURE_FIELDS),
        "exact_fixture_count": 8,
        "exact_model": {
            "byte_count": MODEL_BYTE_COUNT,
            "ir_version": MODEL_IR_VERSION,
            "producer": MODEL_PRODUCER,
            "sha256": MODEL_SHA256,
            "structural_sha256": STRUCTURAL_SHA256,
        },
        "model_fields": list(MODEL_FIELDS),
        "outcome_fields": list(OUTCOME_FIELDS),
        "qualifies": False,
        "required_controls": dict(CONTROL_EXPECTED),
        "rights_fields": list(RIGHTS_FIELDS),
        "runtime": {
            "exact_name": "onnxruntime",
            "exact_threads": {"inter_op": 1, "intra_op": 1},
            "deterministic": True,
            "offline": True,
        },
        "runtime_fields": list(RUNTIME_FIELDS),
        "schema_id": ADMISSION_SCHEMA_ID,
        "source_fields": list(SOURCE_FIELDS),
        "fixture_rates": list(SAMPLE_RATES),
    }


def validate_contract(contract: dict[str, Any]) -> None:
    _no_floats(contract)
    if contract.get("schema_id") != CONTRACT_ID:
        raise ValueError("contract_schema")
    if contract.get("task") != TASK:
        raise ValueError("contract_task")
    if contract.get("decision") != "DEFER":
        raise ValueError("contract_decision")
    if contract.get("status") != "incomplete":
        raise ValueError("contract_status")
    if contract.get("proposal_only") is not True:
        raise ValueError("contract_proposal")
    if contract.get("qualification_status") != "not_qualified":
        raise ValueError("contract_qualification")
    if contract.get("profile") != PROFILE:
        raise ValueError("contract_profile")
    if len(contract.get("release_gates", [])) != 8:
        raise ValueError("contract_gates")
    if len(contract.get("required_artifacts", [])) != 8:
        raise ValueError("contract_artifacts")
    if len(contract.get("exact_blockers", [])) != 6:
        raise ValueError("contract_blockers")
    if len(contract.get("analysis_profile_requirements", [])) != 8:
        raise ValueError("contract_analysis")
    if len(contract.get("quality_outcomes", [])) != 4:
        raise ValueError("contract_quality")
    if len(contract.get("timing_requirements", [])) != 4:
        raise ValueError("contract_timing")
    for gate in contract["release_gates"]:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            raise ValueError("gate_not_blocked")
        if not gate.get("reopen_condition"):
            raise ValueError("gate_reopen")
    for artifact in contract["required_artifacts"][1:]:
        if artifact.get("blocked") is not True or artifact.get("present") is not False:
            raise ValueError("artifact_not_blocked")
    for blocker in contract["exact_blockers"]:
        if blocker.get("status") != "open" or blocker.get("qualifies") is not False:
            raise ValueError("blocker_not_open")
    if "TASKS.json" in " ".join(contract.get("source_pins", {})):
        raise ValueError("contract_pins_board")
    if contract.get("boundary", {}).get("board_file_pinned") is not False:
        raise ValueError("contract_board_pin")
    if contract.get("admission_schema", {}).get("qualifies") is not False:
        raise ValueError("contract_admission_qualifies")


def build_contract() -> dict[str, Any]:
    model = model_provenance()
    workspace = absence_probes(AUDIO_ROOT)
    home = home_absence_probes()
    board_row = board_row_projection()
    contract = {
        "absence_evidence": {
            "home_probes": home,
            "summary": absence_summary(workspace, home),
            "workspace_probes": workspace,
        },
        "admission_schema": admission_schema(),
        "analysis_profile_requirements": analysis_requirements(),
        "base_commit": BASE_COMMIT,
        "boundary": boundary(),
        "boundary_pins": pin_rows(BOUNDARY_PINS, WORKTREE),
        "branch": BRANCH,
        "cadence_reference": cadence_reference(),
        "component": COMPONENT_ID,
        "contract_schema_id": CONTRACT_SCHEMA_ID,
        "decision": "DEFER",
        "disposition": DISPOSITION,
        "exact_blockers": exact_blockers(),
        "input_inventory": input_inventory(),
        "mode": MODE,
        "model_provenance": model,
        "non_claims": NON_CLAIMS,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "proposal_only": True,
        "public_v0_geometry": public_v0_geometry(),
        "qualification": qualification(model),
        "qualification_status": "not_qualified",
        "quality_outcomes": quality_outcomes(),
        "release_gates": release_gates(board_row),
        "required_artifacts": required_artifacts(model),
        "required_results": REQUIRED_RESULTS,
        "runtime_recorded": runtime_recorded(),
        "schema_id": CONTRACT_ID,
        "scope": scope(),
        "source_pins": pin_rows(SOURCE_PINS, AUDIO_ROOT),
        "source_presence": source_presence(model),
        "status": "incomplete",
        "task": TASK,
        "timing_requirements": timing_requirements(),
        "title": TASK_TITLE,
        "write_scope": WRITE_SCOPE,
    }
    validate_contract(contract)
    return contract


def build_report(contract: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = contract or build_contract()
    board_row = contract["boundary"]["linked_row"]
    report = {
        "absence_evidence": contract["absence_evidence"],
        "admission": admission_report(),
        "admission_schema": contract["admission_schema"],
        "analysis_profile": {
            "profile": PROFILE_LABEL,
            "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "rows": contract["analysis_profile_requirements"],
        },
        "boundary": contract["boundary"],
        "boundary_pins": contract["boundary_pins"],
        "cadence_reference": contract["cadence_reference"],
        "component": contract["component"],
        "contract_sha256": object_digest(contract),
        "decision": contract["decision"],
        "disposition": contract["disposition"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "input_inventory_digest": object_digest(contract["input_inventory"]),
        "linked_row_identity": {
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "gating": "stable_identity_only",
            "linked_row": board_row,
            "linked_rows": contract["boundary"]["linked_rows"],
            "linked_rows_sha256": contract["boundary"]["linked_rows_sha256"],
            "projection": board_row,
            "sha256": object_digest(board_row),
        },
        "model_provenance": contract["model_provenance"],
        "non_claims": contract["non_claims"],
        "profile": contract["profile"],
        "profile_label": contract["profile_label"],
        "proposal_only": contract["proposal_only"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "qualification": contract["qualification"],
        "qualification_status": contract["qualification_status"],
        "quality_outcomes": {"rows": contract["quality_outcomes"]},
        "required_artifacts": contract["required_artifacts"],
        "required_results": contract["required_results"],
        "runtime_recorded": contract["runtime_recorded"],
        "schema_id": REPORT_SCHEMA_ID,
        "scope": contract["scope"],
        "source_pins": contract["source_pins"],
        "source_presence": contract["source_presence"],
        "status": contract["status"],
        "task": contract["task"],
        "timing": {"rows": contract["timing_requirements"]},
        "title": contract["title"],
        "write_scope": contract["write_scope"],
    }
    return report


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    payload = canonical_bytes(report)
    return payload.decode("ascii"), sha256_bytes(payload)
