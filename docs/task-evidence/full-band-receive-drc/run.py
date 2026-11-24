# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Opt-in task-local waveform adapter, canonical report and source-pin generator.

The adapter is protocol-shaped, unregistered and disabled by default. With
``provider_enabled=false`` it is bit-exact identity; only an explicit opt-in
selects the deterministic receive DRC reference. It is not an installed v0
provider, does not register a descriptor and changes no public ABI or default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Sequence

import reference
import scorer

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
DIGEST_PATH = ROOT / "report.json.sha256"
SOURCES_PATH = ROOT / "SOURCES.sha256"
IDENTITY = reference.ADAPTER_ID
PROTOCOL_VERSION = 1
# Adapter requests carry whole synthetic fixtures; the engine still processes
# them on its installed 160-sample grid with a 640-sample per-call cap.
MAX_REQUEST_SAMPLES = 32768
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id", "samples"}
CONFIG_KEYS = {"control", "provider_enabled", "level_dbfs", "tmr_db"}
CONTROLS = tuple(reference.MODE_STAGES)
FIXTURES = ("clean_speech", "synthetic_masker", "near_clip_speech", "preclipped_speech",
            "impulse", "silence", "step", "causal_probe", "sweep_1k")


class RequestError(ValueError):
    pass


def _pairs(items: List[Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise RequestError("duplicate_json_key")
        result[key] = value
    return result


def _constant(token: str) -> None:
    raise RequestError("nonfinite_json_constant:" + token)


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=_pairs, parse_constant=_constant)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def validate_ref(value: Any, name: str) -> None:
    if not isinstance(value, dict) or set(value) != {"kind", "id", "revision"}:
        raise RequestError("invalid_" + name)
    if not isinstance(value["id"], str) or not value["id"]:
        raise RequestError("invalid_" + name)
    if isinstance(value["revision"], bool) or not isinstance(value["revision"], int) \
            or value["revision"] < 1:
        raise RequestError("invalid_" + name)


def validate_request(request: Any, operation: str) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS
    if set(request) != required:
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != PROTOCOL_VERSION or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    validate_ref(request["candidate_ref"], "candidate_ref")
    validate_ref(request["adapter_ref"], "adapter_ref")
    config = request["configuration"]
    if not isinstance(config, dict) or set(config) != CONFIG_KEYS:
        raise RequestError("invalid_configuration")
    if config["control"] not in CONTROLS:
        raise RequestError("unknown_control")
    if not isinstance(config["provider_enabled"], bool):
        raise RequestError("invalid_provider_switch")
    if config["level_dbfs"] is not None and config["level_dbfs"] not in reference.LEVEL_DBFS:
        raise RequestError("invalid_level")
    if config["tmr_db"] is not None and config["tmr_db"] not in reference.TMR_DB:
        raise RequestError("invalid_tmr")
    if operation == "inspect":
        return config
    if not isinstance(request["attempt_id"], str) or not request["attempt_id"] \
            or not isinstance(request["stimulus_id"], str) \
            or request["stimulus_id"] not in FIXTURES:
        raise RequestError("invalid_run_identity")
    samples = request["samples"]
    if samples is not None:
        if (not isinstance(samples, list) or not samples
                or len(samples) > MAX_REQUEST_SAMPLES
                or any(isinstance(value, bool) or not isinstance(value, (int, float))
                       for value in samples)
                or any(not math.isfinite(float(value)) for value in samples)
                or any(abs(float(value)) > reference.MAX_ABS_INPUT for value in samples)):
            raise RequestError("invalid_samples")
    return config


def fixture_samples(name: str) -> Sequence[float]:
    if name == "clean_speech":
        return reference.synthetic_speech()
    if name == "synthetic_masker":
        return reference.synthetic_masker()
    if name == "near_clip_speech":
        return reference.near_clip_speech()
    if name == "preclipped_speech":
        return reference.preclipped_speech()
    if name == "impulse":
        return reference.impulse()
    if name == "silence":
        return reference.silence()
    if name == "step":
        return reference.step_fixture()
    if name == "causal_probe":
        return reference.causal_probe_signal()
    if name == "sweep_1k":
        return reference.sweep(1000.0)
    raise RequestError("unknown_stimulus")


def inspect(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "inspect")
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "inspect",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": IDENTITY,
        "configuration": config,
        "supported_controls": list(CONTROLS),
        "supported_fixtures": list(FIXTURES),
        "supported_levels_dbfs": list(reference.LEVEL_DBFS),
        "supported_tmrs_db": list(reference.TMR_DB),
        "supported_tasks": [reference.TASK],
        "supported_formats": ["mono 16 kHz f32 160-sample frames; installed v0 grid"],
        "content_delay_samples": 0,
        "realtime_v0_provider": False,
        "default_enabled": False,
        "provider_manifest": {
            "path": "provider.json",
            "default_enabled": False,
            "opt_in_required": True,
            "registered": False,
            "descriptor_settings": {},
        },
        "registration": "unregistered developer-only fixture; no SDK default or Bench result",
        "public_c_boundary": (
            "not used: task-local Python reference only; installed v0 provider path unchanged"),
    }


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    samples = (tuple(float(value) for value in request["samples"])
               if request["samples"] is not None
               else tuple(float(value) for value in fixture_samples(request["stimulus_id"])))
    if config["level_dbfs"] is not None:
        samples = scorer.scale_to_rms(samples, 10.0 ** (config["level_dbfs"] / 20.0))
    enabled = config["provider_enabled"]
    input_samples = samples
    if enabled:
        status, output = reference.process_whole_clip(samples, mode=config["control"])
        applied = "receive_drc_" + config["control"]
    else:
        status, output = reference.Status.OK, samples
        applied = "identity_provider_off"
    metrics: Dict[str, Any] = {
        "gain": scorer.gain_metrics(input_samples, output),
        "headroom": scorer.headroom(output, reference.DEFAULT_CONFIG.ceiling),
    }
    if config["tmr_db"] is not None:
        masker = reference.synthetic_masker(len(output), seed=5201)
        mixed = scorer.mix_at_tmr(output, masker, config["tmr_db"],
                                  target_rms=scorer.rms(input_samples))
        metrics["masker_control"] = {
            "measured_tmr_db": scorer.r6(mixed["measured_tmr_db"]),
            "mixture_headroom": scorer.headroom(mixed["mixture"]),
            "requested_tmr_db": config["tmr_db"],
            "status": "measured_synthetic_non_qualifying",
        }
    return {
        "protocol_version": PROTOCOL_VERSION,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "provider_enabled": enabled,
        "applied_control": applied,
        "stimulus_id": request["stimulus_id"],
        "status": "complete" if status is reference.Status.OK else "rejected",
        "errors": [] if status is reference.Status.OK else [status.value],
        "output": {
            "sample_count": len(output),
            "frames_consumed": (len(samples) + reference.FRAME_SAMPLES - 1)
                               // reference.FRAME_SAMPLES,
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": 1,
            "byte_count": len(output) * 4,
            "samples_sha256": reference.tensor_digest(output),
            "nonfinite_count": scorer.nonfinite_count(output),
            "peak_abs": scorer.r6(scorer.peak_abs(output)),
        },
        "metrics": metrics,
        "disclosure": (
            "synthetic-only developer result; opt-in unregistered task-local "
            "reference, not a Bench bundle, listening score, quality claim or release gate"),
    }


def process_file(request_path: Path, result_path: Path) -> Dict[str, Any]:
    request = read_json(request_path)
    operation = request.get("operation") if isinstance(request, dict) else None
    if operation == "inspect":
        result = inspect(request)
    elif operation == "run":
        result = run(request)
    else:
        raise RequestError("unsupported_operation")
    result_path.write_bytes(canonical_bytes(result) + b"\n")
    return result


def generate_report(path: Optional[Path] = None) -> str:
    report = reference.build_report()
    text, _canonical_digest = reference.canonical_report(report)
    target = path or REPORT_PATH
    payload = text.encode("utf-8") + b"\n"
    target.write_bytes(payload)
    file_digest = hashlib.sha256(payload).hexdigest()
    target.with_name(target.name + ".sha256").write_text(
        file_digest + "\n", encoding="ascii")
    return file_digest


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_sources() -> str:
    """Write the curated, self-contained source/artifact pin manifest.

    The manifest pins external context, public boundary headers, every
    implementation and manifest file, the README and the generated report plus
    its digest sidecar. It deliberately excludes itself so regeneration is
    byte-identical and it never expands to unrelated worktree files.
    """
    sdk_root = ROOT.parents[2]
    task_relative = reference.TASK_PREFIX
    rows: List[str] = [
        "# SHA-256 pins for SDK-FULL-BAND-RECEIVE-DRC-CONTROL; "
        "source: paths are workspace-relative, others SDK-worktree-relative.\n",
        "# board snapshot (mutable, provenance only): "
        + reference.BOARD_SNAPSHOT["sha256_at_read"] + " "
        + reference.BOARD_SNAPSHOT["path"] + "\n",
    ]
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        rows.append(digest + "  source:" + path + "\n")
    for path, digest in sorted(reference.BOUNDARY_PINS.items()):
        rows.append(digest + "  " + path + "\n")
    names = sorted({**reference.artifact_pins(), **{
        "README.md": "", "report.json": "", "report.json.sha256": "",
    }})
    for name in names:
        path = ROOT / name
        rows.append(_file_sha256(path) + "  " + task_relative + name + "\n")
    payload = "".join(rows)
    SOURCES_PATH.write_text(payload, encoding="utf-8", newline="\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_path", nargs="?", type=Path,
                        help="positional report path; regenerates it and its .sha256 sidecar")
    parser.add_argument("--request", type=Path, help="protocol-v1 request JSON")
    parser.add_argument("--result", type=Path, help="destination for canonical result JSON")
    parser.add_argument("--report", action="store_true", help="regenerate report.json and digest sidecar")
    parser.add_argument("--sources", action="store_true", help="regenerate SOURCES.sha256")
    options = parser.parse_args()
    if options.report or options.report_path is not None:
        print(generate_report(options.report_path))
        return 0
    if options.sources:
        print(generate_sources())
        return 0
    if bool(options.request) != bool(options.result):
        parser.error("--request and --result must be used together")
    if options.request:
        try:
            process_file(options.request, options.result)
        except (RequestError, scorer.ScorerError) as error:
            print(str(error), file=sys.stderr)
            return 2
        return 0
    parser.error("select --report, --sources or --request/--result")


if __name__ == "__main__":
    sys.exit(main())
