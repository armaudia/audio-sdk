"""Opt-in developer adapter for the peak-limiter reference.

The request/result envelope mirrors the public harness-controls adapter
(adapters/controls/adapter.json, protocol_version 1): inspect/run operations,
candidate_ref/adapter_ref revisions and a configuration object. This local
adapter is NOT registered in audio-bench and its result is NOT a Bench bundle.
No WAV files or assets are read; stimuli are deterministic in-memory fixtures.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import reference

ROOT = Path(__file__).resolve().parent
FIXTURE_PATH = ROOT / "fixtures/stimuli.json"
ADAPTER_ID = "peak-limiter-reference"
IDENTITY = "peak-limiter-reference-v1"
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
REQUIRED_RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id", "reset_frames"}
RUN_FIELDS = REQUIRED_RUN_FIELDS | {"stimulus_samples"}
CONTROLS = ("identity", "peak_limiter_reference")


class RequestError(ValueError):
    pass


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise RequestError("duplicate_json_key")
            result[key] = value
        return result

    def constant(token):
        raise RequestError("nonfinite_json_constant:" + token)

    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=constant)


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("ascii")


def fixture():
    document = read_json(FIXTURE_PATH)
    if document["schema"] != "sdk.peak-limiter-reference.fixtures.v1":
        raise RequestError("unexpected_fixture_schema")
    if (document["sample_rate_hz"], document["frame_samples"]) != (
            reference.SAMPLE_RATE_HZ, reference.FRAME_SAMPLES):
        raise RequestError("geometry_mismatch")
    return document


def generate(stimulus_id):
    stimuli = fixture()["stimuli"]
    if stimulus_id not in stimuli:
        raise RequestError("unknown_stimulus:" + stimulus_id)
    spec = stimuli[stimulus_id]
    kind, length = spec["kind"], int(spec["length"])
    if length % reference.FRAME_SAMPLES:
        raise RequestError("stimulus_not_frame_aligned")
    rate = float(reference.SAMPLE_RATE_HZ)
    values = []
    if kind == "chirp":
        phase = 0.0
        for index in range(length):
            fraction = index / (length - 1)
            frequency = spec["f0_hz"] + (spec["f1_hz"] - spec["f0_hz"]) * fraction
            amplitude = spec["amp0"] + (spec["amp1"] - spec["amp0"]) * fraction
            phase += 2.0 * math.pi * frequency / rate
            values.append(amplitude * math.sin(phase))
    elif kind == "steps":
        tone = spec["tone_hz"]
        levels = spec["levels"]
        for index in range(length):
            level = levels[index // reference.FRAME_SAMPLES]
            values.append(level * math.sin(2.0 * math.pi * tone * index / rate))
    elif kind == "impulse":
        tail_hz = spec["tail_hz"]
        for index in range(length):
            tail = spec["tail_amplitude"] * math.sin(2.0 * math.pi * tail_hz * index / rate)
            values.append(tail + (spec["amplitude"] if index == spec["position"] else 0.0))
    elif kind == "silence":
        values = [0.0] * length
    elif kind == "tone":
        for index in range(length):
            values.append(spec["amplitude"] * math.sin(
                2.0 * math.pi * spec["frequency_hz"] * index / rate))
    elif kind == "speech_like":
        f0 = spec["f0_hz"]
        burst = int(spec["burst_samples"])
        gap = int(spec["gap_samples"])
        period = burst + gap
        for index in range(length):
            slot = index // period
            within = index % period
            if slot >= len(spec["amplitudes"]) or within >= burst:
                values.append(0.0)
                continue
            envelope = 0.5 - 0.5 * math.cos(2.0 * math.pi * within / burst)
            voiced = sum(weight * math.sin((harmonic + 1) * 2.0 * math.pi * f0 * index / rate)
                         for harmonic, weight in enumerate((1.0, 0.5, 0.25)))
            values.append(spec["amplitudes"][slot] * envelope * voiced / 1.75)
    elif kind == "lcg_noise":
        state = int(spec["seed"])
        modulus = 0x7FFFFFFF
        for _ in range(length):
            state = (1103515245 * state + 12345) & 0x7FFFFFFF
            values.append((2.0 * state / modulus - 1.0) * spec["amplitude"])
    elif kind == "nonfinite":
        tone, amplitude = spec["tone_hz"], spec["amplitude"]
        for index in range(length):
            value = amplitude * math.sin(2.0 * math.pi * tone * index / rate)
            if index == spec["nan_at"]:
                value = math.nan
            elif index == spec["inf_at"]:
                value = math.inf
            values.append(value)
    else:
        raise RequestError("unknown_stimulus_kind:" + kind)
    return [reference.f32(value) for value in values]


def validate_ref(ref, name):
    if not isinstance(ref, dict) or set(ref) != {"kind", "id", "revision"}:
        raise RequestError("invalid_" + name)
    if not isinstance(ref["id"], str) or not ref["id"]:
        raise RequestError("invalid_" + name)
    if isinstance(ref["revision"], bool) or not isinstance(ref["revision"], int) or ref["revision"] < 1:
        raise RequestError("invalid_" + name)


def validate_request(request, operation):
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else REQUIRED_RUN_FIELDS
    allowed = required if operation == "inspect" else (RUN_FIELDS | {"extensions"})
    if set(request) - allowed or not required <= set(request):
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != 1 or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    for name in ("candidate_ref", "adapter_ref"):
        validate_ref(request[name], name)
    config = request["configuration"]
    if not isinstance(config, dict):
        raise RequestError("configuration_not_object")
    control = config.get("control")
    if control not in CONTROLS:
        raise RequestError("unknown_control")
    if control == "peak_limiter_reference":
        reference.validate_controls({key: value for key, value in config.items()
                                     if key != "control"})
    elif set(config) != {"control"}:
        raise RequestError("unexpected_identity_configuration")
    if operation == "run":
        if not isinstance(request["attempt_id"], str) or not request["attempt_id"]:
            raise RequestError("invalid_attempt_id")
        if not isinstance(request["stimulus_id"], str):
            raise RequestError("invalid_stimulus_id")
        resets = request.get("reset_frames", [])
        if (not isinstance(resets, list) or any(isinstance(item, bool) or not isinstance(item, int)
                                                 or item < 0 for item in resets)):
            raise RequestError("invalid_reset_frames")
        override = request.get("stimulus_samples")
        if override is not None:
            if (not isinstance(override, list) or not override or
                    len(override) % reference.FRAME_SAMPLES or
                    any(isinstance(value, bool) or not isinstance(value, (int, float))
                        for value in override)):
                raise RequestError("invalid_stimulus_samples")
    return config, control


def inspect(request):
    _, control = validate_request(request, "inspect")
    return {
        "protocol_version": 1,
        "operation": "inspect",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": IDENTITY,
        "configuration": request["configuration"],
        "requested_control": control,
        "supported_controls": list(CONTROLS),
        "supported_tasks": [],
        "supported_modes": ["offline"],
        "supported_formats": ["mono 16 kHz float32, 160-sample frames"],
        "asset_readiness": [],
        "registration": "unregistered developer-only fixture; not an audio-bench result",
    }


def run(request):
    config, control = validate_request(request, "run")
    if request.get("stimulus_samples") is not None:
        samples = [reference.f32(value) for value in request["stimulus_samples"]]
    else:
        samples = generate(request["stimulus_id"])
    resets = request.get("reset_frames", [])
    if control == "identity":
        output = samples
        frames = []
        reset_count = 0
        gain = 1.0
    else:
        limiter = reference.PeakLimiterReference(config["ceiling"], config["release_ms"])
        processed = reference.process_sequence(limiter, samples, reset_at=resets)
        output = processed["samples"]
        frames = processed["frames"]
        reset_count = processed["reset_count"]
        gain = processed["gain"]
    finite = [math.isfinite(value) for value in output]
    result = {
        "protocol_version": 1,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "control": control,
        "stimulus_id": request["stimulus_id"],
        "reset_frames": resets,
        "status": "complete",
        "errors": [],
        "output": {
            "sample_count": len(output),
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": 1,
            "byte_count": len(output) * 4,
            "samples_sha256": reference.digest_samples(output),
            "finite_count": sum(finite),
            "nonfinite_count": len(finite) - sum(finite),
            "peak_abs": max((abs(value) for value in output if math.isfinite(value)), default=0.0),
            "frames": frames,
            "gain_final": gain,
            "reset_count": reset_count,
            "engaged_frames": sum(1 for frame in frames if frame["engaged"]),
            "fast_path_frames": sum(1 for frame in frames if frame["fast_path"]),
        },
    }
    if all(finite):
        result["output"]["samples"] = output
    else:
        result["output"]["preview"] = [
            None if not math.isfinite(value) else value for value in output[:16]
        ]
        result["errors"].append({"kind": "adverse_numerical",
                                 "reason": "nonfinite_input_or_output_not_serialized"})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--result", required=True)
    args = parser.parse_args()
    try:
        request = read_json(args.request)
        if not isinstance(request, dict) or request.get("operation") not in ("inspect", "run"):
            raise RequestError("unknown_operation")
        result = inspect(request) if request["operation"] == "inspect" else run(request)
        path = Path(args.result)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".tmp")
        temp.write_bytes(canonical_bytes(result))
        os.replace(temp, path)
    except (RequestError, reference.ControlError, ValueError, KeyError, TypeError) as error:
        print(str(error) or error.__class__.__name__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
