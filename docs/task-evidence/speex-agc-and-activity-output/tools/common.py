# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Shared strict-JSON, source-pin, CLI and metric helpers for this fixture."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess

TASK = Path(__file__).resolve().parents[1]
SDK_ROOT = Path(os.environ.get("AUDIO_SDK_ROOT", str(TASK.parents[2]))).resolve()
WS_ROOT = Path(os.environ.get("AUDIOML_ROOT", str(TASK.parents[5]))).resolve()
SOURCES = TASK / "SOURCES.sha256"
REPORT_PATH = TASK / "evidence" / "report.json"
SCHEMA = "audio-sdk/task-evidence/speex-agc-and-activity-output/report/1"
META_SCHEMA = "speex-agc-activity-cli/1"
BASE_COMMIT = "941cabfc39f7e33f01881b6e50e3a1e49e7eb9ce"
BRANCH = "swarm/SDK-SPEEX-AGC-AND-ACTIVITY-OUTPUT"
TASK_ID = "SDK-SPEEX-AGC-AND-ACTIVITY-OUTPUT"
REPEATS = 3
FRAME = 160
SAMPLES = 16000

DEFAULT_CONFIG = {
    "agc": 1,
    "vad": 1,
    "denoise": 0,
    "target": 8192,
    "increment": 12,
    "decrement": 40,
    "max_gain": 30,
    "prob_start": 35,
    "prob_continue": 20,
    "noise_suppress": -20,
    "reset_frames": [],
}
CONFIG_KEYS = tuple(DEFAULT_CONFIG)
CONTROLS = {
    "identity": {"agc": 0, "vad": 0},
    "agc_only": {"agc": 1, "vad": 0},
    "vad_only": {"agc": 0, "vad": 1},
    "combined": {"agc": 1, "vad": 1},
    "combined_denoise": {"agc": 1, "vad": 1, "denoise": 1},
}


class StrictError(ValueError):
    pass


def strict_json(text: str):
    """Parse JSON with duplicate keys and nonfinite constants rejected."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise StrictError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def constant(token):
        raise StrictError("nonfinite_json_constant:" + token)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def read_strict(path: Path):
    return strict_json(path.read_text(encoding="utf-8"))


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("ascii")


def digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def source_pins() -> list[dict]:
    pins = []
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (sdk|ws):(.+)", line)
        if match is None:
            raise StrictError("malformed SOURCES.sha256 line: " + line)
        digest, namespace, relative = match.groups()
        if ".." in Path(relative).parts or Path(relative).is_absolute():
            raise StrictError("unsafe source pin path: " + relative)
        root = SDK_ROOT if namespace == "sdk" else WS_ROOT
        path = root / relative
        observed = digest_bytes(path.read_bytes()) if path.is_file() else None
        pins.append({
            "scope": namespace,
            "path": relative,
            "sha256": digest,
            "observed_sha256": observed,
            "status": "match" if observed == digest else "mismatch_or_missing",
        })
    return pins


def case(name: str, stimulus: str, control: str, **overrides):
    config = dict(DEFAULT_CONFIG)
    config.update(CONTROLS[control])
    config.update(overrides)
    config["reset_frames"] = list(overrides.get("reset_frames", []))
    return {
        "id": name,
        "stimulus": stimulus,
        "control": control,
        "config": config,
    }


CASES = [
    case("identity_chirp", "chirp", "identity"),
    case("identity_steps", "steps", "identity"),
    case("identity_impulse", "impulse", "identity"),
    case("identity_silence", "silence", "identity"),
    case("identity_speech_like", "speech_like", "identity"),
    case("identity_noise_only", "noise_only", "identity"),
    case("identity_gain_step", "gain_step", "identity"),
    case("combined_chirp", "chirp", "combined"),
    case("combined_steps", "steps", "combined"),
    case("combined_impulse", "impulse", "combined"),
    case("combined_silence", "silence", "combined"),
    case("combined_speech_like", "speech_like", "combined"),
    case("combined_noise_only", "noise_only", "combined"),
    case("combined_gain_step", "gain_step", "combined"),
    case("agc_only_speech_like", "speech_like", "agc_only"),
    case("vad_only_speech_like", "speech_like", "vad_only"),
    case("target_4096_speech_like", "speech_like", "combined", target=4096),
    case("target_16384_speech_like", "speech_like", "combined", target=16384),
    case("fast_steps", "steps", "combined", increment=24, decrement=80),
    case("prob_60_40_speech_like", "speech_like", "combined", prob_start=60, prob_continue=40),
    case("prob_10_5_speech_like", "speech_like", "combined", prob_start=10, prob_continue=5),
    case("reset_steps", "steps", "combined", reset_frames=[10]),
    case("combined_denoise_speech_like", "speech_like", "combined_denoise"),
]


def case_by_id(case_id: str) -> dict:
    for item in CASES:
        if item["id"] == case_id:
            return item
    raise StrictError("unknown case: " + case_id)


def cli_arguments(config: dict) -> list[str]:
    args = []
    for key in CONFIG_KEYS:
        value = config[key]
        flag = "--" + key.replace("_", "-")
        if key == "reset_frames":
            args += [flag, ",".join(str(index) for index in value)]
        else:
            args += [flag, str(value)]
    return args


def run_cli(cli: Path, work: Path, stimulus: Path, config: dict,
            case_id: str, repeat: int) -> dict:
    output = work / (case_id + "-r" + str(repeat) + ".f32")
    meta_path = work / (case_id + "-r" + str(repeat) + ".json")
    command = [str(cli), "--input", str(stimulus), "--output", str(output),
               "--meta", str(meta_path)] + cli_arguments(config)
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise StrictError("cli_exit_" + str(proc.returncode) + ":" + proc.stderr.strip())
    raw = output.read_bytes()
    meta_bytes = meta_path.read_bytes()
    meta = read_strict(meta_path)
    if meta.get("schema") != META_SCHEMA or meta.get("frames") != SAMPLES // FRAME:
        raise StrictError("invalid_meta_schema_or_frames")
    if meta.get("config") != {key: config[key] for key in DEFAULT_CONFIG if key != "reset_frames"}:
        raise StrictError("meta_config_echo_mismatch")
    records = meta.get("records")
    if not isinstance(records, list) or len(records) != SAMPLES // FRAME:
        raise StrictError("invalid_meta_records")
    expected = set(range(SAMPLES // FRAME))
    if [record.get("frame") for record in records] != list(expected):
        raise StrictError("non_contiguous_meta_frames")
    fields = {"frame", "reset", "vad", "agc_gain_db", "prob_percent", "agc_loudness"}
    for record in records:
        if not isinstance(record, dict) or set(record) != fields:
            raise StrictError("invalid_meta_record_fields")
        if any(isinstance(value, bool) or not isinstance(value, int)
               for value in record.values()):
            raise StrictError("non_integer_meta_record")
        if record["vad"] not in (0, 1):
            raise StrictError("invalid_advisory_vad")
    return {
        "output_path": output,
        "meta_path": meta_path,
        "output_bytes": raw,
        "meta_bytes": meta_bytes,
        "meta": meta,
        "records": records,
    }


def output_metrics(raw: bytes) -> dict:
    count = len(raw) // 4
    if count != SAMPLES or len(raw) % 4:
        raise StrictError("unexpected_output_length")
    values = struct.unpack("<" + str(count) + "f", raw)
    if not all(math.isfinite(value) for value in values):
        raise StrictError("nonfinite_output")
    peak = max(abs(value) for value in values)
    rms = math.sqrt(sum(value * value for value in values) / count)
    return {
        "samples": count,
        "byte_count": len(raw),
        "peak_abs": round(peak, 6),
        "rms": round(rms, 6),
        "clipped_or_at_one": sum(1 for value in values if abs(value) >= 1.0),
        "nonfinite_count": 0,
        "first_sample": round(values[0], 6),
        "last_sample": round(values[-1], 6),
    }


def activity_metrics(records: list[dict]) -> dict:
    gains = [record["agc_gain_db"] for record in records]
    vad = [record["vad"] for record in records]
    prob = [record["prob_percent"] for record in records]
    loudness = [record["agc_loudness"] for record in records]
    resets = [record["frame"] for record in records if record["reset"]]
    return {
        "advisory_vad_frames": sum(vad),
        "advisory_vad_sequence": vad,
        "agc_gain_db_min": min(gains),
        "agc_gain_db_max": max(gains),
        "agc_gain_db_first": gains[0],
        "agc_gain_db_last": gains[-1],
        "agc_gain_db_sequence": gains,
        "speech_prob_percent_min": min(prob),
        "speech_prob_percent_max": max(prob),
        "speech_prob_percent_sequence": prob,
        "agc_loudness_sequence": loudness,
        "reset_frames": resets,
    }
