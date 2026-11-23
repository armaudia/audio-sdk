"""Opt-in protocol-v1-shaped adapter for the static-target-gain reference.

The request/result envelope mirrors the public harness-controls adapter
(``adapters/controls/adapter.json``, protocol_version 1): inspect/run,
candidate_ref/adapter_ref revisions and an explicit configuration object. This
local adapter is NOT registered in audio-bench; its output is NOT a Bench
bundle. No WAV, asset, model or download path exists.

Every run is frame-aligned to the frozen v0 geometry: 16 kHz, mono f32,
160 samples per frame. Because the gain is sequence-static, a continued session
replays its buffered history and returns only the newly supplied suffix; this
makes split calls match the corresponding one-shot call. That is offline replay
semantics, not a streaming or real-time claim. Stale epochs are rejected before
any buffer or state is changed.
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
FIXTURE_PATH = ROOT / "fixtures" / "stimuli.json"
ADAPTER_ID = "static-target-gain-with-peak-ceiling-reference"
IDENTITY = "static-target-gain-reference-v1"
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
REQUIRED_RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id", "session_id", "epoch",
                                       "reset_frames"}
RUN_FIELDS = REQUIRED_RUN_FIELDS | {"stimulus_samples", "trace", "continue_session"}
CONTROLS = reference.CONTROL_NAMES

SESSIONS = {}


class RequestError(ValueError):
    pass


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise RequestError("duplicate_json_key:" + str(key))
            result[key] = value
        return result

    def constant(token):
        raise RequestError("nonfinite_json_constant:" + token)

    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=constant)


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def fixture():
    document = read_json(FIXTURE_PATH)
    if document.get("schema") != "sdk.static-target-gain-with-peak-ceiling.fixtures.v1":
        raise RequestError("unexpected_fixture_schema")
    geometry = document["geometry"]
    if (geometry["sample_rate_hz"], geometry["channels"], geometry["frame_samples"]) != (
            reference.SAMPLE_RATE_HZ, reference.CHANNELS, reference.FRAME_SAMPLES):
        raise RequestError("geometry_mismatch")
    return document


def generate(stimulus_id):
    stimuli = fixture()["stimuli"]
    if stimulus_id not in stimuli:
        raise RequestError("unknown_stimulus:" + stimulus_id)
    return _generate_from_spec(stimulus_id, stimuli)


def _generate_from_spec(stimulus_id, stimuli, seen=None):
    seen = set(seen or ())
    if stimulus_id in seen:
        raise RequestError("stimulus_cycle")
    seen.add(stimulus_id)
    spec = stimuli[stimulus_id]
    kind = spec["kind"]
    length = int(spec.get("length", 0))
    rate = float(reference.SAMPLE_RATE_HZ)
    frame = reference.FRAME_SAMPLES

    if kind != "gain_step":
        if length <= 0 or length % frame:
            raise RequestError("stimulus_not_frame_aligned:" + stimulus_id)

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
        tone = float(spec["tone_hz"])
        levels = spec["levels"]
        for index in range(length):
            level = levels[index // frame]
            values.append(level * math.sin(2.0 * math.pi * tone * index / rate))
    elif kind == "impulse":
        for index in range(length):
            tail = float(spec["tail_amplitude"]) * math.sin(
                2.0 * math.pi * float(spec["tail_hz"]) * index / rate)
            values.append(tail + (float(spec["amplitude"]) if index == int(spec["position"]) else 0.0))
    elif kind == "silence":
        values = [0.0] * length
    elif kind == "tone":
        amplitude = float(spec["amplitude"])
        for index in range(length):
            values.append(amplitude * math.sin(2.0 * math.pi * float(spec["frequency_hz"]) * index / rate))
    elif kind == "speech_like":
        f0 = float(spec["f0_hz"])
        burst = int(spec["burst_samples"])
        gap = int(spec["gap_samples"])
        period = burst + gap
        amplitudes = spec["amplitudes"]
        state = int(spec["seed"])
        modulus = 0x7FFFFFFF
        for index in range(length):
            slot, within = divmod(index, period)
            if slot >= len(amplitudes) or within >= burst:
                values.append(0.0)
                continue
            envelope = 0.5 - 0.5 * math.cos(2.0 * math.pi * within / burst)
            voiced = sum(weight * math.sin((harmonic + 1) * 2.0 * math.pi * f0 * index / rate)
                         for harmonic, weight in enumerate((1.0, 0.5, 0.25)))
            state = (1103515245 * state + 12345) & modulus
            jitter = 0.95 + 0.10 * (state / modulus)
            values.append(float(amplitudes[slot]) * envelope * voiced / 1.75 * jitter)
    elif kind == "gain_step":
        source = _generate_from_spec(str(spec["source"]), stimuli, seen)
        values = list(source)
        block = int(spec["block_samples"])
        ramp = int(spec["ramp_samples"])
        levels = [float(item) for item in spec["levels_db"]]
        state = int(spec["seed"])
        modulus = 0x7FFFFFFF
        gains_db = []
        for _ in range((len(values) + block - 1) // block):
            state = (1103515245 * state + 12345) & modulus
            gains_db.append(levels[state & 1])
        trajectory = [gains_db[index // block] for index in range(len(values))]
        for boundary in range(block, len(values), block):
            left, right = gains_db[boundary // block - 1], gains_db[boundary // block]
            lo, hi = max(0, boundary - ramp // 2), min(len(values), boundary + ramp // 2)
            for index in range(lo, hi):
                fraction = (index - lo) / max(1, hi - lo)
                trajectory[index] = left + (right - left) * fraction
        values = [value * (10.0 ** (gain_db / 20.0))
                  for value, gain_db in zip(values, trajectory)]
    elif kind == "overshoot":
        tone = float(spec["tone_hz"])
        for index in range(length):
            amplitude = (float(spec["loud_amplitude"])
                         if int(spec["loud_start"]) <= index < int(spec["loud_end"])
                         else float(spec["quiet_amplitude"]))
            values.append(amplitude * math.sin(2.0 * math.pi * tone * index / rate))
    elif kind == "nonfinite":
        tone = float(spec["tone_hz"])
        for index in range(length):
            value = float(spec["amplitude"]) * math.sin(2.0 * math.pi * tone * index / rate)
            if index == int(spec["nan_at"]):
                value = math.nan
            elif index == int(spec["inf_at"]):
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
    if not required <= set(request) or set(request) - allowed:
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
    reference.validate_controls(config, control)
    if operation == "run":
        if not isinstance(request["attempt_id"], str) or not request["attempt_id"]:
            raise RequestError("invalid_attempt_id")
        if not isinstance(request["stimulus_id"], str) or not request["stimulus_id"]:
            raise RequestError("invalid_stimulus_id")
        if (not isinstance(request["session_id"], str) or not request["session_id"]
                or not request["session_id"].isascii()):
            raise RequestError("invalid_session_id")
        epoch = request["epoch"]
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 1:
            raise RequestError("invalid_epoch")
        resets = request["reset_frames"]
        if (not isinstance(resets, list) or any(isinstance(item, bool) or not isinstance(item, int)
                                                 or item < 0 for item in resets)):
            raise RequestError("invalid_reset_frames")
        for name in ("trace", "continue_session"):
            if name in request and not isinstance(request[name], bool):
                raise RequestError("invalid_" + name)
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
        "supported_modes": ["offline", "frame_sequence"],
        "supported_formats": ["mono 16 kHz float32, 160-sample frames"],
        "asset_readiness": [],
        "registration": "unregistered developer-only fixture; not an audio-bench result",
    }


def _config_digest(config):
    return hashlib.sha256(canonical_bytes(config)).hexdigest()


def _session(request, config, control):
    """Inspect session state without changing it; stale epochs reject first."""
    key = (request["session_id"], control, _config_digest(config))
    epoch = int(request["epoch"])
    current = SESSIONS.get(key)
    if current is not None and epoch < current["epoch"]:
        raise RequestError("stale_epoch")
    continued = bool(request.get("continue_session", False))
    advance = current is not None and continued and epoch > current["epoch"]
    preserved = [] if advance or current is None or not continued else list(current["samples"])
    old_resets = [] if advance or current is None or not continued else list(current["reset_frames"])
    return key, current, continued, advance, preserved, old_resets


def _commit_session(key, current, continued, advance, request, config, control,
                    total, resets):
    if current is not None and continued:
        session = current
        if advance:
            session["samples"] = []
            session["reset_frames"] = []
            session["epoch"] = int(request["epoch"])
            session["transitions"].append({"kind": "epoch_advance",
                                           "to": int(request["epoch"]),
                                           "buffer": "cleared"})
    else:
        session = {
            "samples": [],
            "reset_frames": [],
            "epoch": int(request["epoch"]),
            "transitions": [],
            "control": control,
            "config_sha256": _config_digest(config),
        }
        SESSIONS[key] = session
    session["samples"] = total
    session["reset_frames"] = resets
    return session


def run(request):
    config, control = validate_request(request, "run")
    key, current, continued, advance, preserved, old_resets = _session(
        request, config, control)

    if request.get("stimulus_samples") is not None:
        new_samples = [reference.f32(value) for value in request["stimulus_samples"]]
    else:
        new_samples = generate(request["stimulus_id"])

    total = preserved + new_samples
    if len(total) % reference.FRAME_SAMPLES:
        raise RequestError("session_not_frame_aligned")
    resets = sorted(set(old_resets + list(request["reset_frames"])))
    if any(index >= len(total) // reference.FRAME_SAMPLES for index in resets):
        raise RequestError("reset_frame_out_of_range")
    session = _commit_session(key, current, continued, advance, request, config,
                              control, total, resets)

    trace_requested = bool(request.get("trace", False))
    processor = reference.make_processor(config)
    processed = reference.process_sequence(processor, total, resets, trace=trace_requested)
    full_output = processed["samples"]
    output = full_output[len(preserved):]

    session["samples"] = total
    session["reset_frames"] = resets
    output_finite = [math.isfinite(value) for value in output]
    finite_output_count = sum(output_finite)
    frames = processed["frames"]
    gains = [frame["gain_db"] for frame in frames]
    result = {
        "protocol_version": 1,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "control": control,
        "stimulus_id": request["stimulus_id"],
        "reset_frames": list(request["reset_frames"]),
        "session_state": {
            "session_id": request["session_id"],
            "epoch": session["epoch"],
            "continued": bool(request.get("continue_session", False)),
            "control": control,
            "config_sha256": session["config_sha256"],
            "buffered_frames": len(total) // reference.FRAME_SAMPLES,
            "buffer_samples_sha256": reference.digest_samples(total),
            "reset_count": processed["reset_count"],
            "transitions": list(session["transitions"]),
        },
        "status": "complete",
        "errors": [],
        "output": {
            "sample_count": len(output),
            "sample_rate_hz": reference.SAMPLE_RATE_HZ,
            "channels": reference.CHANNELS,
            "byte_count": len(output) * 4,
            "samples_sha256": reference.digest_samples(output),
            "input_samples_sha256": reference.digest_samples(new_samples),
            "full_output_sha256": reference.digest_samples(full_output),
            "finite_count": finite_output_count,
            "nonfinite_count": len(output) - finite_output_count,
            "nonfinite_input_count": sum(
                1 for value in new_samples if not math.isfinite(float(value))),
            "peak_abs": max((abs(value) for value in output if math.isfinite(value)), default=0.0),
            "peak_input_abs": max((abs(value) for value in new_samples if math.isfinite(value)),
                                  default=0.0),
            "frames": frames,
            "plans": processed["plans"],
            "gain_final": frames[-1]["gain"] if frames else 1.0,
            "gain_db_final": gains[-1] if gains else 0.0,
            "gain_db_min": min(gains) if gains else 0.0,
            "gain_db_max": max(gains) if gains else 0.0,
            "clipped_samples": sum(frame["clipped_samples"] for frame in frames),
            "reset_count": processed["reset_count"],
        },
    }
    if trace_requested and processed["gain_trace"] is not None:
        result["output"]["gain_trace_sha256"] = reference.digest_samples(processed["gain_trace"])
        result["output"]["gain_trace"] = processed["gain_trace"]
    if all(output_finite):
        result["output"]["samples"] = output
    else:
        result["output"]["preview"] = [
            None if not math.isfinite(value) else value for value in output[:16]
        ]
        result["errors"].append({"kind": "adverse_numerical",
                                 "reason": "nonfinite_input_or_output_not_serialized"})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
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
    except (RequestError, reference.ControlError, ValueError, KeyError, TypeError,
            OverflowError) as error:
        print(str(error) or error.__class__.__name__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
