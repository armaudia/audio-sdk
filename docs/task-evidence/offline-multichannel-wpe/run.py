# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local opt-in waveform adapter and canonical report regeneration.

The adapter is opt-in, unregistered and disabled by default. It is not an
installed SDK realtime v0 provider, produces no Bench bundle and changes no
descriptor, default, registry entry or public ABI. Its only DSP mode is a
whole-clip, noncausal two-channel frequency-domain WPE reference over a frozen
synthetic fixture set. Every input frame is buffered before any predictor is
estimated, so this is never a streaming/real-time boundary claim.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

import reference

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
DIGEST_PATH = ROOT / "report.json.sha256"
SOURCES_PATH = ROOT / "SOURCES.sha256"
IDENTITY = "offline-multichannel-wpe-reference-v1"
PROTOCOL_VERSION = 1
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id", "samples"}
CONTROLS = ("mc_wpe_candidate", "identity_control", "noisy_identity_control", "mc_wpe_on_noisy")
FIXTURES = ("short_rt60", "medium_rt60", "long_rt60", "movement_long", "overlap_long",
            "clean", "impulse", "silence", "probe")


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


def validate_ref(ref: Any, name: str) -> None:
    if not isinstance(ref, dict) or set(ref) != {"kind", "id", "revision"}:
        raise RequestError("invalid_" + name)
    if (not isinstance(ref["id"], str) or not ref["id"]
            or isinstance(ref["revision"], bool) or not isinstance(ref["revision"], int)
            or ref["revision"] < 1):
        raise RequestError("invalid_" + name)


def validate_request(request: Any, operation: str) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS
    if not required <= set(request) or set(request) - required:
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != PROTOCOL_VERSION or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    validate_ref(request["candidate_ref"], "candidate_ref")
    validate_ref(request["adapter_ref"], "adapter_ref")
    config = request["configuration"]
    if (not isinstance(config, dict) or set(config) != {"control", "provider_enabled"}):
        raise RequestError("invalid_configuration")
    if config["control"] not in CONTROLS:
        raise RequestError("unknown_control")
    if not isinstance(config["provider_enabled"], bool):
        raise RequestError("invalid_provider_switch")
    if operation == "inspect":
        return config
    if (not isinstance(request["attempt_id"], str) or not request["attempt_id"]
            or not isinstance(request["stimulus_id"], str)):
        raise RequestError("invalid_run_identity")
    samples = request["samples"]
    if samples is not None:
        if (not isinstance(samples, list) or len(samples) != reference.CHANNELS
                or any(not isinstance(channel, list) or not channel
                       or len(channel) != len(samples[0])
                       or len(channel) > reference.MAX_CHUNK_SAMPLES
                       for channel in samples)
                or any(isinstance(value, bool) or not isinstance(value, (int, float))
                       for channel in samples for value in channel)
                or any(not math.isfinite(float(value))
                       for channel in samples for value in channel)):
            raise RequestError("invalid_samples")
    elif request["stimulus_id"] not in FIXTURES:
        raise RequestError("unknown_stimulus")
    return config


def _condition_channels(name: str):
    source = reference.clean_source()
    spec = reference.ROOM_SPECS[name]
    rirs = reference.room_rirs(name)
    unscaled = reference.convolve_channels(source, rirs)
    peak = max(abs(value) for channel in unscaled for value in channel)
    gain = min(1.0, 0.9 / peak)
    return tuple(tuple(value * gain for value in channel) for channel in unscaled)


def fixture_channels(name: str):
    if name in reference.ROOM_SPECS:
        return _condition_channels(name)
    if name == "clean":
        return (reference.clean_source(), reference.clean_source())
    if name == "impulse":
        return reference.impulse()
    if name == "silence":
        return reference.silence()
    if name == "probe":
        return reference.probe_channels()
    if name == "movement_long":
        source = reference.clean_source()
        rirs = reference.room_rirs("long_rt60")
        movement = tuple(reference.movement_envelope(
            len(source), index * reference.MOVEMENT_CHANNEL_OFFSET)
            for index in range(reference.CHANNELS))
        raw = tuple(tuple(value * envelope for value, envelope in zip(channel, movement[index]))
                    for index, channel in enumerate(reference.convolve_channels(source, rirs)))
        peak = max(abs(value) for channel in raw for value in channel)
        return reference.scale_channels(raw, min(1.0, 0.9 / peak))
    if name == "overlap_long":
        source = reference.clean_source()
        second = reference.second_source(len(source))
        mixture = tuple(left + right for left, right in zip(source, second))
        raw = reference.convolve_channels(mixture, reference.room_rirs("long_rt60"))
        peak = max(abs(value) for channel in raw for value in channel)
        return reference.scale_channels(raw, min(1.0, 0.9 / peak))
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
        "requested_control": config["control"],
        "supported_controls": list(CONTROLS),
        "supported_fixtures": list(FIXTURES),
        "supported_tasks": ["SDK-OFFLINE-MULTICHANNEL-WPE"],
        "supported_modes": ["whole_clip_noncausal"],
        "supported_formats": ["two-channel 16 kHz float32 160-sample chunks (fixture grid only)"],
        "channels": reference.CHANNELS,
        "frame_samples": reference.FRAME_SAMPLES,
        "processing_mode": "whole_clip_noncausal",
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
        "registration": "unregistered developer-only fixture; no SDK default, Bench bundle or installed behavior change",
        "public_c_boundary": (
            "not used: task-local Python reference only; the installed v0 "
            "160-sample mono provider path is unchanged"),
    }


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    samples = (tuple(tuple(float(value) for value in channel) for channel in request["samples"])
               if request["samples"] is not None
               else fixture_channels(request["stimulus_id"]))
    enabled = config["provider_enabled"]
    if enabled and config["control"] == "mc_wpe_candidate":
        status, output = reference.process_whole_clip(samples)
        applied = "mc_wpe_candidate"
    elif enabled and config["control"] == "noisy_identity_control":
        status, output = reference.Status.OK, samples
        applied = "noisy_identity_control"
    elif enabled and config["control"] == "mc_wpe_on_noisy":
        status, output = reference.process_whole_clip(samples)
        applied = "mc_wpe_on_noisy"
    else:
        status, output = reference.Status.OK, samples
        applied = "identity_provider_off" if not enabled else "identity_control"
    finite = [math.isfinite(value) for channel in output for value in channel]
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
            "channels": reference.CHANNELS,
            "sample_count": len(output[0]) if output else 0,
            "frames_consumed": (len(samples[0]) + reference.FRAME_SAMPLES - 1)
                               // reference.FRAME_SAMPLES,
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "byte_count": len(output[0]) * reference.CHANNELS * 4 if output else 0,
            "samples_sha256": reference.channels_digest(output),
            "finite_count": sum(finite),
            "nonfinite_count": len(finite) - sum(finite),
            "peak_abs": max((abs(value) for channel in output for value in channel
                             if math.isfinite(value)), default=0.0),
        },
        "disclosure": (
            "synthetic-only developer result from an opt-in unregistered task-local "
            "whole-clip noncausal reference; not a Bench bundle, real-time provider, "
            "quality claim or release gate"),
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


def generate_report() -> str:
    report = reference.build_report()
    text, digest = reference.canonical_report(report)
    REPORT_PATH.write_bytes(text.encode("utf-8") + b"\n")
    DIGEST_PATH.write_text(digest + "\n", encoding="ascii")
    return digest


def generate_sources() -> str:
    lines = ["# SHA-256 pins for SDK-OFFLINE-MULTICHANNEL-WPE; source: paths "
             "are workspace-relative, others SDK-worktree-relative."]
    for mapping in (reference.SOURCE_PINS, reference.BOUNDARY_PINS,
                    reference.ARTIFACT_PINS):
        for relative, digest in mapping.items():
            prefix = "source:" if relative.startswith(
                ("research/", "adapters/", "REALTIME_", "audio-benchmark-platform/")) else ""
            lines.append(f"{digest}  {prefix}{relative}")
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    SOURCES_PATH.write_bytes(payload)
    return reference.file_digest(SOURCES_PATH)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, help="protocol-v1 request JSON")
    parser.add_argument("--result", type=Path, help="destination for canonical result JSON")
    parser.add_argument("--report", action="store_true", help="regenerate report.json and its SHA-256")
    parser.add_argument("--sources", action="store_true", help="regenerate SOURCES.sha256 and print its SHA-256")
    options = parser.parse_args()
    flags = sum(bool(value) for value in (options.report, options.sources,
                                          options.request or options.result))
    if flags != 1:
        parser.error("select exactly one of --report, --sources or --request/--result")
    if options.report:
        print(generate_report())
        return 0
    if options.sources:
        print(generate_sources())
        return 0
    if bool(options.request) != bool(options.result):
        parser.error("--request and --result must be used together")
    try:
        process_file(options.request, options.result)
    except RequestError as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
