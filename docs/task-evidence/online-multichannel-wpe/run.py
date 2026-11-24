# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local two-channel waveform adapter and canonical artifact regeneration.

The adapter is opt-in, unregistered and disabled by default. It is not an
installed SDK realtime v0 provider, produces no Bench bundle and changes no
descriptor, default, registry entry or public ABI. Its only DSP mode is a
frame-causal 16 kHz 2x160 f32 in / 160 f32 out online multichannel WPE
reference. Provider-off output is a bit-exact mic-0 passthrough.
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
CROSSCHECK_PATH = ROOT / "crosscheck_vectors.json"
IDENTITY = "online-multichannel-wpe-reference-v1"
PROTOCOL_VERSION = 1
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id", "samples"}
CONTROLS = ("online_mc_wpe", "identity")
FIXTURES = ("short_rt60", "medium_rt60", "long_rt60", "echo_only",
            "near_end_only", "overlap_long", "clean", "impulse", "silence")


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
        if (not isinstance(samples, list) or len(samples) != reference.INPUT_CHANNELS
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


def _condition_pair(name: str):
    source = reference.clean_source()
    if name == "echo_only":
        source = reference.far_end_source()
    spec = reference.ROOM_SPECS.get(name, reference.ROOM_SPECS["short_rt60"])
    pair = reference.synthetic_rir_pair(spec)
    return reference.two_channel_convolve(source, pair)[:2]


def fixture_pair(name: str):
    if name in reference.ROOM_SPECS or name == "echo_only":
        return _condition_pair(name)
    if name == "near_end_only":
        return reference.clean_near_end_pair(reference.clean_source())
    if name == "overlap_long":
        spec = reference.ROOM_SPECS["long_rt60"]
        mixture = tuple(left + right for left, right in zip(
            reference.clean_source(), reference.second_source(len(reference.clean_source()))))
        return reference.two_channel_convolve(mixture, reference.synthetic_rir_pair(spec))[:2]
    if name == "clean":
        return reference.clean_near_end_pair(reference.clean_source())
    if name == "impulse":
        return reference.impulse_pair()
    if name == "silence":
        return reference.silence_pair()
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
        "supported_tasks": ["SDK-ONLINE-MULTICHANNEL-WPE"],
        "supported_modes": ["causal_frame_streaming"],
        "supported_formats": [
            "opt-in task-local 16 kHz float32 2x160-sample input frames, 160-sample mono output"],
        "input_channels": reference.INPUT_CHANNELS,
        "output_channels": reference.OUTPUT_CHANNELS,
        "content_delay_samples": reference.CONTENT_DELAY_SAMPLES,
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
        "installed_v0_note": (
            "installed v0 stays 16 kHz mono f32 at 160 samples/frame; this "
            "two-channel shape exists only at the opt-in task-local boundary"),
        "public_c_boundary": (
            "not used: task-local Python reference only; the installed v0 "
            "160-sample provider path is unchanged"),
        "decision": "DEFER",
    }


def run(request: Dict[str, Any]) -> Dict[str, Any]:
    config = validate_request(request, "run")
    pair = (tuple(tuple(float(value) for value in channel) for channel in request["samples"])
            if request["samples"] is not None else fixture_pair(request["stimulus_id"]))
    enabled = config["provider_enabled"]
    if enabled and config["control"] == "online_mc_wpe":
        status, output = reference.process_whole_clip(pair)
        applied = "online_mc_wpe"
    else:
        status, output = reference.Status.OK, pair[0]
        applied = "identity_provider_off" if not enabled else "mic0_passthrough_control"
    finite = [math.isfinite(value) for value in output]
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
            "frames_consumed": (len(pair[0]) + reference.FRAME_SAMPLES - 1)
                               // reference.FRAME_SAMPLES,
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "input_channels": reference.INPUT_CHANNELS,
            "output_channels": reference.OUTPUT_CHANNELS,
            "byte_count": len(output) * 4,
            "samples_sha256": reference.tensor_digest(output),
            "finite_count": sum(finite),
            "nonfinite_count": len(finite) - sum(finite),
            "peak_abs": max((abs(value) for value in output if math.isfinite(value)),
                            default=0.0),
        },
        "disclosure": (
            "synthetic-only developer result; opt-in unregistered task-local "
            "two-channel reference, not a Bench bundle, quality claim or release gate"),
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
    """Write canonical report bytes and the matching sidecar digest."""
    target = REPORT_PATH if path is None else path
    report = reference.build_report()
    text, digest = reference.canonical_report(report)
    target.write_bytes(text.encode("utf-8") + b"\n")
    Path(str(target) + ".sha256").write_text(digest + "\n", encoding="ascii")
    return digest


def generate_sources() -> str:
    payload = reference.sources_bytes()
    SOURCES_PATH.write_bytes(payload)
    return reference.file_digest(SOURCES_PATH)


def crosscheck_digest() -> str:
    vectors = reference.load_crosscheck_vectors()
    expected = reference.ARTIFACT_PINS[
        "docs/task-evidence/offline-mono-wpe/crosscheck_vectors.json"]
    actual = reference.file_digest(CROSSCHECK_PATH)
    if actual != expected:
        raise RequestError("crosscheck_pin_stale")
    return reference.object_digest(vectors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_path", nargs="?", type=Path, default=None,
                        help="optional report destination; bare invocation regenerates report.json")
    parser.add_argument("--request", type=Path, help="protocol-v1 request JSON")
    parser.add_argument("--result", type=Path, help="destination for canonical result JSON")
    parser.add_argument("--report", action="store_true",
                        help="regenerate report.json and its SHA-256")
    parser.add_argument("--sources", action="store_true",
                        help="regenerate SOURCES.sha256 from the pinned tables")
    parser.add_argument("--crosscheck", action="store_true",
                        help="validate and print the inherited scorer cross-check digest")
    options = parser.parse_args()
    modes = sum(bool(value) for value in (options.report, options.sources,
                                          options.crosscheck, options.request))
    if options.report_path is not None and modes:
        parser.error("a positional report path cannot be combined with a mode flag")
    if modes > 1:
        parser.error("select exactly one mode flag")
    if options.report or modes == 0:
        print(generate_report(options.report_path))
        return 0
    if options.sources:
        print(generate_sources())
        return 0
    if options.crosscheck:
        print(crosscheck_digest())
        return 0
    if not options.result:
        parser.error("--request requires --result")
    try:
        process_file(options.request, options.result)
    except RequestError as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
