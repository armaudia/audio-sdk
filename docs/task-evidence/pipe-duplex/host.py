# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local host example for SDK-PIPE-DUPLEX.

This is a frozen synthetic reference pipeline, not an AEC, double-talk, quality,
device, listening, paced-workload or release result. It composes the merged
SDK-PIPE-CAPTURE stages with the merged, default-OFF SpeexDSP MDF reference CLI:
capture plus timestamped far-end render -> aligned Speex MDF -> Speex NS policy
-> sample-peak limiter, with a task-local residual-suppressor surrogate toggled
independently. Invalid or absent reference selects an explicit capture-only
recipe and reports the reason. No shared source, ABI, default, provider, CMake
or CI file is changed. Fixture, output and CLI scratch bytes stay outside the
worktree.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import struct
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
AUDIOML_ROOT = SDK_ROOT.parents[2]

SCHEMA = "audio-sdk/pipe-duplex/0.1"
FRAME = 160
RATE = 16000
NS_PER_SAMPLE = 62500
ORIGIN_NS = 1_000_000_000
FRAME_NS = FRAME * NS_PER_SAMPLE
F32 = struct.Struct("<f")
_CANON = {"sort_keys": True, "separators": (",", ":"), "ensure_ascii": True,
          "allow_nan": False}
_NS_CALIBRATION_FRAMES = 8
_NS_MIN_GAIN = 0.1

MDF_PROVIDERS = {
    "merged.speexdsp_mdf_reference.v1": 0,
    "merged.speexdsp_mdf_reference_reset150.v1": 150,
}
CAPTURE_ONLY_VARIANTS = {"identity", "capture_only", "capture_residual"}


class ControlError(ValueError):
    """A rejected recipe, pin, frame or timeline control."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(payload, **_CANON) + "\n").encode("ascii")


def canonical_digest(payload: Mapping[str, Any]) -> str:
    return sha256(canonical_bytes(payload))


def f32(value: float) -> float:
    return F32.unpack(F32.pack(float(value)))[0]


def f32_bytes(values: Sequence[float]) -> bytes:
    return b"".join(F32.pack(float(value)) for value in values)


def digest_samples(values: Sequence[float]) -> str:
    return sha256(f32_bytes(values))


def load_json(name: str) -> dict[str, Any]:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def resolve_pin_path(spec: str) -> Path:
    if spec.startswith("sdk:"):
        return SDK_ROOT / spec[4:]
    if spec.startswith("ws:"):
        return AUDIOML_ROOT / spec[3:]
    raise ControlError("pin_prefix:" + spec)


def check_pins(fixtures: Mapping[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for pin in fixtures["source_pins"]:
        path = resolve_pin_path(pin["path"])
        observed = sha256(path.read_bytes()) if path.is_file() else None
        result.append({"path": pin["path"], "sha256": pin["sha256"],
                       "observed_sha256": observed,
                       "verified": observed == pin["sha256"], "use": pin["use"]})
    return result


def check_dependency_pins(fixtures: Mapping[str, Any]) -> dict[str, Any]:
    lock = fixtures["dependency_pin"]
    native = fixtures["native_manifest_pin"]
    oracle = fixtures["merged_oracle_pin"]
    lock_path = resolve_pin_path(lock["path"])
    native_path = resolve_pin_path(native["path"])
    oracle_path = resolve_pin_path(oracle["path"])
    sidecar_path = resolve_pin_path(oracle["sidecar_path"])
    lock_observed = sha256(lock_path.read_bytes()) if lock_path.is_file() else None
    native_observed = sha256(native_path.read_bytes()) if native_path.is_file() else None
    oracle_bytes = oracle_path.read_bytes() if oracle_path.is_file() else b""
    sidecar_text = sidecar_path.read_text(encoding="utf-8") if sidecar_path.is_file() else ""
    sidecar_digest = sidecar_text.split()[0] if sidecar_text.strip() else None
    oracle_payload = json.loads(oracle_bytes) if oracle_bytes else {}
    return {
        "name": lock["name"], "version": lock["version"],
        "revision": lock["revision"], "source": lock["source"],
        "network_fetch_required": lock["network_fetch_required"],
        "dependency_pin_verified": lock_observed == lock["sha256"],
        "native_manifest_pin_verified": native_observed == native["sha256"],
        "merged_oracle_pin_verified": sha256(oracle_bytes) == oracle["sha256"],
        "merged_oracle_sidecar_file_verified": (
            sha256(sidecar_path.read_bytes()) == oracle["sidecar_sha256"]
            if sidecar_path.is_file() else False),
        "merged_oracle_sidecar_content_verified": (
            sidecar_digest == oracle["sha256"]),
        "merged_fixture_digest_verified": (
            oracle_payload.get("fixture_digest") == oracle["fixture_digest"]),
    }


def validate_recipe(recipe: Mapping[str, Any],
                    fixtures: Mapping[str, Any] | None = None) -> tuple[bool, str]:
    if recipe.get("schema_id") != SCHEMA or recipe.get("status") != "proposal_only":
        return False, "schema_or_status"
    activation = recipe.get("activation", {})
    if activation.get("default_enabled") is not False or activation.get("opt_in_only") is not True:
        return False, "default_enabled"
    if (activation.get("build_targets_added") or activation.get("shared_sources_modified")
            or activation.get("shared_abi_changed")
            or activation.get("provider_registry_changed")):
        return False, "shared_change"
    fmt = recipe.get("format")
    if fmt != {"sample_rate_hz": RATE, "channels": 1,
               "sample_format": "f32", "frame_samples": FRAME}:
        return False, "format"
    clock = recipe.get("clock", {})
    if clock.get("origin_ns") != ORIGIN_NS or clock.get("ns_per_sample") != NS_PER_SAMPLE:
        return False, "clock"
    if not isinstance(clock.get("frame_timeout_ns"), int) or clock["frame_timeout_ns"] <= 0:
        return False, "timeout"
    transport = recipe.get("transport", {})
    if (transport.get("automatic_retry") is not False
            or transport.get("provider_substitution") is not False
            or transport.get("hot_swap") is not False
            or transport.get("capture_only_on_invalid_reference") is not True
            or transport.get("report_reference_fault") is not True):
        return False, "transport"
    stages = recipe.get("stages", {})
    if not isinstance(stages, dict) or not stages:
        return False, "stages"
    for name, policy in stages.items():
        if (policy.get("role") != "audio"
                or not isinstance(policy.get("delay_samples"), int)
                or not isinstance(policy.get("availability_cost_ns"), int)):
            return False, "stage_policy:" + name
        if policy.get("availability_cost_ns", 0) > clock["frame_timeout_ns"]:
            return False, "stage_cost:" + name
    if set(MDF_PROVIDERS) - set(stages):
        return False, "mdf_stage_pins"

    variants = recipe.get("variants", {})
    for name, variant in variants.items():
        path = variant.get("audio_path")
        nodes = variant.get("nodes")
        if not isinstance(path, list) or not path or not isinstance(nodes, list):
            return False, name + ":shape"
        by_id = {node.get("id"): node for node in nodes}
        if len(by_id) != len(nodes) or any(node is None for node in by_id.values()):
            return False, name + ":duplicate_or_missing_id"
        if any(node_id not in by_id for node_id in path):
            return False, name + ":path_id"
        audio_nodes = [by_id[node_id] for node_id in path]
        if {node["id"] for node in audio_nodes} != {node["id"] for node in nodes}:
            return False, name + ":audio_path_coverage"
        ports: list[str] = []
        for index, node in enumerate(audio_nodes):
            policy = stages.get(node.get("provider_id"))
            if policy is None:
                return False, name + ":provider"
            if (node.get("role") != "audio"
                    or node.get("delay_samples") != policy.get("delay_samples")
                    or node.get("availability_cost_ns") != policy.get("availability_cost_ns")
                    or node.get("settings") != policy.get("settings")):
                return False, name + ":metadata_mismatch"
            expected_in = "pcm.in" if index == 0 else audio_nodes[index - 1]["output_port"]
            if node.get("input_port") != expected_in:
                return False, name + ":port_chain"
            if not node.get("output_port") or node["output_port"] in ports:
                return False, name + ":port_id"
            ports.append(node["output_port"])
        if sum(int(node["delay_samples"]) for node in audio_nodes) > clock["frame_timeout_ns"]:
            return False, name + ":delay"
        if "residual" in path and "mdf" not in path and name != "capture_residual":
            return False, name + ":residual_coupling"
    if fixtures is not None:
        matrix = recipe.get("case_matrix", {})
        if set(matrix) != set(fixtures["cases"]):
            return False, "case_matrix_coverage"
        for case_name, names in matrix.items():
            if not names or any(name not in variants for name in names):
                return False, "case_matrix_variant:" + case_name
            if "identity" not in names:
                return False, "case_matrix_identity:" + case_name
    return True, "ok"


def _lcg(seed: int, count: int) -> list[float]:
    state = seed & 0xFFFFFFFF
    out: list[float] = []
    for _ in range(count):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        out.append((state >> 8) / 8388608.0 - 1.0)
    return out


def _echo_path(render: Sequence[float], delay: int,
               taps: Sequence[float], gain: float) -> list[float]:
    out = [0.0] * len(render)
    for n in range(len(render)):
        total = 0.0
        for tap, coefficient in enumerate(taps):
            index = n - delay + tap
            if 0 <= index < len(render):
                total += coefficient * render[index]
        out[n] = gain * total
    return out


def _near_wave(count: int) -> list[float]:
    out: list[float] = []
    for n in range(count):
        envelope = 0.5 + 0.5 * math.sin(2.0 * math.pi * 2.0 * n / count)
        carrier = math.sin(2.0 * math.pi * 180.0 * n / RATE)
        harmonic = 0.4 * math.sin(2.0 * math.pi * 360.0 * n / RATE)
        out.append(0.12 * envelope * (carrier + harmonic))
    return out


def generate_streams(fixtures: Mapping[str, Any]) -> dict[str, dict[str, list[float]]]:
    """Regenerate the frozen base streams; no audio file or asset is read."""
    spec = fixtures["stimulus"]
    count = int(spec["samples"])
    frames = int(spec["frames"])
    draws = _lcg(int(spec["lcg_seed"]), count * 2)
    render: list[float] = []
    lowpass = 0.0
    for index in range(count):
        lowpass = 0.6 * lowpass + 0.4 * draws[index]
        render.append(0.4 * lowpass)
    noise = [float(spec["noise_scale"]) * value for value in draws[count:]]
    delay = int(spec["delay_before_samples"])
    echo = _echo_path(render, delay, spec["echo_taps"], float(spec["echo_gain"]))
    near = _near_wave(count)
    zeros = [0.0] * count

    near_burst = list(zeros)
    burst_start, burst_end = (int(value) * FRAME for value in spec["near_burst_frames"])
    near_burst[burst_start:burst_end] = near[burst_start:burst_end]
    near_full = list(zeros)
    full_start, full_end = (int(value) * FRAME for value in spec["near_full_frames"])
    near_full[full_start:full_end] = near[full_start:full_end]
    near_reference = [f32(near_full[n] + noise[n]) for n in range(count)]
    shifted = list(zeros)
    shifted[FRAME:] = render[:-FRAME]

    base: dict[str, tuple[list[float], list[float], list[float]]] = {
        "echo_only": (render, [f32(echo[n] + noise[n]) for n in range(count)], zeros),
        "overlap_small": (render,
                          [f32(echo[n] + near_burst[n] + noise[n]) for n in range(count)],
                          near_burst),
        "near_end_only": (zeros,
                          [f32(near_full[n] + noise[n]) for n in range(count)],
                          near_full),
        "misaligned_reference": (shifted,
                                 [f32(echo[n] + noise[n]) for n in range(count)],
                                 zeros),
    }
    streams: dict[str, dict[str, list[float]]] = {}
    for case_name, case in fixtures["cases"].items():
        source, capture, _near_signal = base[case["base_stream"]]
        capture = list(capture)
        if case["echo_path"] == "changing_delay":
            change = int(spec["delay_change_frame"]) * FRAME
            after = _echo_path(source, int(spec["delay_after_samples"]),
                               spec["echo_taps"], float(spec["echo_gain"]))
            capture[change:] = [f32(after[n] + noise[n]) for n in range(change, count)]
        if case["timeline_injection"] == "capture_zeroed_range":
            start, end = (int(value) * FRAME for value in spec["capture_dropout_frames"])
            for n in range(start, end):
                capture[n] = 0.0
        for value in capture:
            if not math.isfinite(value) or abs(value) > 1.0:
                raise ControlError("stimulus_out_of_range:" + case_name)
        streams[case_name] = {
            "render": [f32(value) for value in source],
            "capture": [f32(value) for value in capture],
            "near": list(near_reference),
        }
    if frames * FRAME != count:
        raise ControlError("frame_count_mismatch")
    return streams


def classify_reference_frames(frames: Sequence[Mapping[str, Any]],
                              fixtures: Mapping[str, Any]) -> dict[str, Any]:
    """Validate render timestamps before MDF; ERLE is never used as a detector."""
    spec = fixtures["stimulus"]
    max_skew = 1
    expected_start = ORIGIN_NS
    previous: int | None = None
    starved = 0
    repaired = 0
    stale = 0
    nonmonotonic = 0
    excessive = 0
    fractional = 0
    for frame in frames:
        if not frame["present"]:
            starved += 1
            continue
        timestamp = int(frame["timestamp_ns"])
        expected = expected_start + int(frame["index"]) * FRAME_NS
        if previous is not None and timestamp <= previous:
            nonmonotonic += 1
        previous = timestamp
        delta = timestamp - expected
        if delta % FRAME_NS != 0:
            fractional += 1
            continue
        offset = delta // FRAME_NS
        if offset == 0:
            continue
        if 0 < offset <= max_skew:
            repaired += 1
        elif offset < 0:
            stale += 1
        else:
            excessive += 1
    reasons: list[str] = []
    if nonmonotonic:
        reasons.append("nonmonotonic_timestamps")
    if fractional:
        reasons.append("fractional_timestamps")
    if excessive:
        reasons.append("excessive_skew")
    if stale:
        reasons.append("stale_reference")
    if starved:
        reasons.append("reference_starvation")
    return {
        "render_frames_total": len(frames),
        "render_frames_received": sum(1 for frame in frames if frame["present"]),
        "starved_frames": starved,
        "timestamp_skew_repaired_frames": repaired,
        "stale_frames": stale,
        "nonmonotonic_timestamps": nonmonotonic,
        "fractional_timestamps": fractional,
        "excessive_skew_frames": excessive,
        "reference_decision": "capture_only" if reasons else "duplex",
        "reasons": reasons,
        "max_skew_frames": max_skew,
        "skew_start_frame": int(spec["skew_start_frame"]),
    }


def build_timeline(fixtures: Mapping[str, Any], case_name: str,
                   streams: Mapping[str, Mapping[str, list[float]]]) -> dict[str, Any]:
    spec = fixtures["stimulus"]
    case = fixtures["cases"][case_name]
    mode = case["render_mode"]
    start, end = (int(value) for value in spec["render_starvation_frames"])
    render = streams[case_name]["render"]
    frames: list[dict[str, Any]] = []
    for index in range(len(render) // FRAME):
        present = True
        timestamp = ORIGIN_NS + index * FRAME_NS
        if mode == "withheld_all" or (mode == "starved_range" and start <= index < end):
            present = False
        elif mode == "stale_timestamps":
            timestamp += int(spec["stale_offset_frames"]) * FRAME_NS
        elif (mode == "timestamp_offset_positive"
              and index >= int(spec["skew_start_frame"])):
            timestamp += int(spec["skew_offset_frames"]) * FRAME_NS
        samples = tuple(render[index * FRAME:(index + 1) * FRAME]) if present else (0.0,) * FRAME
        frames.append({"index": index, "timestamp_ns": timestamp,
                       "samples": samples, "present": present})

    classification = classify_reference_frames(frames, fixtures)
    aligned_render: list[float] = []
    render_activity: list[bool] = []
    for frame in frames:
        aligned_render.extend(frame["samples"])
        render_activity.append(any(value != 0.0 for value in frame["samples"]))
    if len(aligned_render) != len(render):
        raise ControlError("timeline_length")
    capture_dropout: list[int] = []
    if case["timeline_injection"] == "capture_zeroed_range":
        first, last = (int(value) for value in spec["capture_dropout_frames"])
        capture_dropout = list(range(first, last))
    return {
        "classification": classification,
        "capture_timestamps_ns": [ORIGIN_NS + index * FRAME_NS
                                  for index in range(len(render) // FRAME)],
        "aligned_render": [f32(value) for value in aligned_render],
        "render_activity": render_activity,
        "capture_dropout_frames": capture_dropout,
        "reference_decision": classification["reference_decision"],
        "reasons": classification["reasons"],
    }


def _pcm16(value: float) -> int:
    clamped = max(-1.0, min(1.0, float(value)))
    return int(round(clamped * 32767.0))


def _apply_highpass(values: Sequence[float], node: Mapping[str, Any]) -> list[float]:
    if node["settings"]["cutoff_hz"] != 80.0:
        raise ControlError("highpass_cutoff")
    q = float(node["settings"]["q"])
    w0 = 2.0 * math.pi * 80.0 / RATE
    cosine = math.cos(w0)
    alpha = math.sin(w0) / (2.0 * q)
    a0 = 1.0 + alpha
    b0 = ((1.0 + cosine) * 0.5) / a0
    b1 = (-(1.0 + cosine)) / a0
    b2 = b0
    a1 = (-2.0 * cosine) / a0
    a2 = (1.0 - alpha) / a0
    z1 = 0.0
    z2 = 0.0
    output: list[float] = []
    for value in values:
        x = f32(value)
        y = b0 * x + z1
        z1 = b1 * x - a1 * y + z2
        z2 = b2 * x - a2 * y
        output.append(f32(y))
    return output


def _apply_ns(values: Sequence[float], node: Mapping[str, Any]) -> list[float]:
    settings = node["settings"]
    if (settings.get("suppression_db") != -20 or settings.get("vad_start") != 35
            or settings.get("vad_continue") != 20
            or settings.get("agc_enabled") is not False
            or settings.get("dereverb_enabled") is not False):
        raise ControlError("ns_policy_mismatch")
    shaped_frames: list[tuple[float, ...]] = []
    calibration: list[float] = []
    noise_power = 1e-12
    for offset in range(0, len(values), FRAME):
        chunk = values[offset:offset + FRAME]
        quantized = [float(_pcm16(value)) / 32768.0 for value in chunk]
        power = (sum(value * value for value in quantized) / len(quantized)
                 if quantized else 0.0)
        if len(calibration) < _NS_CALIBRATION_FRAMES:
            calibration.append(power)
            noise_power = sum(calibration) / len(calibration)
            gain = _NS_MIN_GAIN
        else:
            gain = (math.sqrt(max(_NS_MIN_GAIN ** 2, 1.0 - noise_power / power))
                    if power > 0.0 else _NS_MIN_GAIN)
        shaped_frames.append(tuple(f32(float(_pcm16(value * gain)) / 32768.0)
                                   for value in quantized))
    output: list[float] = [0.0] * FRAME
    for frame in shaped_frames[:-1]:
        output.extend(frame)
    if shaped_frames:
        output.extend(shaped_frames[-1])
    return output[:len(values)]


def _apply_limiter(values: Sequence[float], node: Mapping[str, Any]) -> list[float]:
    settings = node["settings"]
    ceiling = float(settings.get("ceiling", 0.98))
    release_ms = float(settings.get("release_ms", 50.0))
    if not (0.0 < ceiling <= 1.0) or not (0.0 < release_ms <= 5000.0):
        raise ControlError("limiter_controls")
    release = 1.0 - math.exp(-1000.0 / (release_ms * RATE))
    gain = 1.0
    output: list[float] = []
    for value in values:
        sample = float(value)
        peak = abs(sample)
        target = ceiling / peak if peak > ceiling else 1.0
        if target < gain:
            gain = target
        else:
            gain += release * (target - gain)
        limited = sample * gain
        output.append(f32(max(-ceiling, min(ceiling, limited))))
    return output


def _apply_residual(values: Sequence[float], activity: Sequence[bool],
                    node: Mapping[str, Any]) -> tuple[list[float], int]:
    settings = node["settings"]
    threshold = float(settings["low_rms_threshold"])
    floor = float(settings["floor_gain"])
    if settings.get("requires_reference") is not True:
        raise ControlError("residual_reference_requirement")
    output: list[float] = []
    suppressed = 0
    for index in range(0, len(values), FRAME):
        chunk = values[index:index + FRAME]
        if activity[index // FRAME] and chunk:
            rms = math.sqrt(sum(value * value for value in chunk) / len(chunk))
            if rms < threshold:
                suppressed += 1
                output.extend(f32(value * floor) for value in chunk)
                continue
        output.extend(chunk)
    return output, suppressed


def apply_variant(recipe: Mapping[str, Any], variant_name: str,
                  capture: Sequence[float], aligned_render: Sequence[float],
                  activity: Sequence[bool], mdf_output: Sequence[float] | None,
                  timeline: Mapping[str, Any]) -> tuple[list[float], int]:
    variant = recipe["variants"][variant_name]
    by_id = {node["id"]: node for node in variant["nodes"]}
    uses_mdf = any(node["provider_id"] in MDF_PROVIDERS for node in variant["nodes"])
    if uses_mdf and mdf_output is None:
        raise ControlError("mdf_output_missing:" + variant_name)
    current: list[float] = list(mdf_output if uses_mdf else capture)
    suppressed = 0
    for node_id in variant["audio_path"]:
        node = by_id[node_id]
        provider = node["provider_id"]
        if provider == "fixture.identity.v0" or provider in MDF_PROVIDERS:
            current = [f32(value) for value in current]
        elif provider == "dsp.highpass80.v0":
            current = _apply_highpass(current, node)
        elif provider == "speex.ns.v0":
            current = _apply_ns(current, node)
        elif provider == "fixture.peak_limiter.v0":
            current = _apply_limiter(current, node)
        elif provider == "fixture.residual_suppressor_surrogate.v0":
            if timeline["reference_decision"] != "duplex":
                raise ControlError("residual_without_reference")
            current, suppressed = _apply_residual(current, activity, node)
        else:
            raise ControlError("unmapped_provider:" + provider)
    return current, suppressed


def features(values: Sequence[float]) -> dict[str, Any]:
    finite = all(math.isfinite(value) for value in values)
    peak = max((abs(value) for value in values if math.isfinite(value)), default=0.0)
    return {
        "samples": len(values),
        "finite": finite,
        "nonfinite_count": sum(1 for value in values if not math.isfinite(value)),
        "peak_abs": round(peak, 6),
        "clipped_or_nonfinite": sum(1 for value in values
                                    if not math.isfinite(value) or abs(value) >= 1.0),
        "at_or_above_ceiling": sum(1 for value in values
                                   if math.isfinite(value) and abs(value) >= 0.98),
    }


def digest_features(values: Sequence[float]) -> dict[str, Any]:
    result = features(values)
    result["f32_digest"] = digest_samples(values)
    return result


def _energy(values: Sequence[float], start: int, end: int) -> float:
    return sum(value * value for value in values[start:end])


def erle_db(capture: Sequence[float], output: Sequence[float],
            window: Sequence[int]) -> float:
    start, end = (int(value) * FRAME for value in window)
    before = _energy(capture, start, end)
    after = _energy(output, start, end)
    return round(10.0 * math.log10((before + 1e-12) / (after + 1e-12)), 6)


def ratio_to_reference(output: Sequence[float], reference: Sequence[float],
                       window: Sequence[int]) -> float | None:
    if not any(reference):
        return None
    start, end = (int(value) * FRAME for value in window)
    after = _energy(output, start, end)
    expected = _energy(reference, start, end)
    return round(math.sqrt((after + 1e-12) / (expected + 1e-12)), 6)


def _invoke_cli(cli: Path, work: Path, label: str, render: Sequence[float],
                capture: Sequence[float], reset_every: int = 0,
                extra: list[str] | None = None) -> tuple[int, bytes | None]:
    case_dir = work / label
    case_dir.mkdir(parents=True, exist_ok=True)
    render_path = case_dir / "render.f32"
    capture_path = case_dir / "capture.f32"
    output_path = case_dir / "output.f32"
    render_path.write_bytes(f32_bytes(render))
    capture_path.write_bytes(f32_bytes(capture))
    if output_path.exists():
        output_path.unlink()
    command = [str(cli), "--render", str(render_path), "--capture", str(capture_path),
               "--output", str(output_path), "--frame-samples", str(FRAME),
               "--rate", str(RATE), "--filter-length", "3200",
               "--reset-every", str(reset_every)]
    command.extend(extra or [])
    completed = subprocess.run(command, capture_output=True, text=True)
    payload = output_path.read_bytes() if output_path.exists() else None
    return completed.returncode, payload


def _read_f32(payload: bytes) -> list[float]:
    if len(payload) % 4 != 0:
        raise ControlError("mdf_output_length")
    return list(struct.unpack("<%df" % (len(payload) // 4), payload))


def run_mdf(cli: Path, work: Path, label: str, render: Sequence[float],
            capture: Sequence[float], reset_every: int = 0) -> tuple[list[float], bytes]:
    status, payload = _invoke_cli(cli, work, label, render, capture, reset_every)
    if status != 0 or payload is None:
        raise ControlError("mdf_failed:%s:%d" % (label, status))
    output = _read_f32(payload)
    if len(output) != len(capture):
        raise ControlError("mdf_length:" + label)
    return output, payload


def run_matrix(cli: Path, work: Path, recipe: Mapping[str, Any],
               fixtures: Mapping[str, Any],
               streams: Mapping[str, Mapping[str, list[float]]]) -> dict[str, Any]:
    spec = fixtures["stimulus"]
    converged = spec["converged_window_frames"]
    preservation = spec["preservation_window_frames"]
    post_change = spec["post_change_window_frames"]
    cases: dict[str, Any] = {}
    for case_index, (case_name, matrix) in enumerate(recipe["case_matrix"].items()):
        case = fixtures["cases"][case_name]
        timeline = build_timeline(fixtures, case_name, streams)
        capture = streams[case_name]["capture"]
        near = streams[case_name]["near"]
        aligned_render = timeline["aligned_render"]
        uses_mdf = any(any(node["provider_id"] in MDF_PROVIDERS for node in
                           recipe["variants"][name]["nodes"]) for name in matrix)
        mdf_output: list[float] | None = None
        mdf_record: dict[str, Any] | None = None
        if uses_mdf:
            if timeline["reference_decision"] != "duplex":
                raise ControlError("mdf_on_invalid_reference:" + case_name)
            expected_reset = int(case.get("mdf_reset_frames", 0))
            for name in matrix:
                for node in recipe["variants"][name]["nodes"]:
                    if node["provider_id"] in MDF_PROVIDERS:
                        actual = MDF_PROVIDERS[node["provider_id"]]
                        if actual != expected_reset:
                            raise ControlError("reset_mismatch:" + case_name)
            mdf_output, payload = run_mdf(cli, work,
                                          "case-%02d-mdf" % case_index,
                                          aligned_render, capture, expected_reset)
            mdf_record = {
                "stage_digest": sha256(payload),
                **digest_features(mdf_output),
                "erle_db_converged": erle_db(capture, mdf_output, converged),
                "near_ratio_overlap": ratio_to_reference(mdf_output, near, preservation),
                "erle_db_post_change": (erle_db(capture, mdf_output, post_change)
                                        if case["echo_path"] == "changing_delay" else None),
                "reset_every_frames": expected_reset,
            }
        elif timeline["reference_decision"] == "duplex":
            raise ControlError("matrix_without_mdf:" + case_name)

        variants: dict[str, Any] = {}
        for name in matrix:
            output, suppressed = apply_variant(recipe, name, capture, aligned_render,
                                               timeline["render_activity"], mdf_output,
                                               timeline)
            variant = recipe["variants"][name]
            variants[name] = {
                "purpose": variant["purpose"],
                "declared_audio_path": list(variant["audio_path"]),
                "declared_delay_samples": sum(
                    int(node["delay_samples"]) for node in variant["nodes"]),
                "declared_availability_cost_ns": sum(
                    int(node["availability_cost_ns"]) for node in variant["nodes"]),
                "output_digest": digest_samples(output),
                "output": digest_features(output),
                "suppressed_frames": suppressed,
                "erle_db_converged": erle_db(capture, output, converged),
                "identity_rms_ratio_overlap": ratio_to_reference(output, capture,
                                                                 preservation),
                "near_ratio_overlap": ratio_to_reference(output, near, preservation),
            }
        identity_digest = variants["identity"]["output_digest"]
        for name in matrix:
            variants[name]["output_equals_identity"] = (
                variants[name]["output_digest"] == identity_digest)
        cases[case_name] = {
            "note": case["note"],
            "reference_status": case["reference_status"],
            "render_mode": case["render_mode"],
            "echo_path": case["echo_path"],
            "timeline_injection": case["timeline_injection"],
            "reference_decision": timeline["reference_decision"],
            "reasons": timeline["reasons"],
            "timeline": timeline["classification"],
            "capture_dropout_frames": timeline["capture_dropout_frames"],
            "render_source_digest": digest_samples(streams[case_name]["render"]),
            "aligned_render_digest": digest_samples(aligned_render),
            "capture_digest": digest_samples(capture),
            "near_reference_digest": digest_samples(near),
            "mdf_stage": mdf_record,
            "variants": variants,
        }
    return cases


def run_controls(cli: Path, work: Path, recipe: Mapping[str, Any],
                 fixtures: Mapping[str, Any],
                 streams: Mapping[str, Mapping[str, list[float]]]) -> dict[str, Any]:
    controls = fixtures["controls"]
    expected = controls["expected_mdf_exit_codes"]
    echo = streams["echo_only"]
    work.mkdir(parents=True, exist_ok=True)

    bad_capture = list(echo["capture"])
    bad_capture[int(controls["nonfinite_capture_index"])] = float("nan")
    status, payload = _invoke_cli(cli, work, "nonfinite", echo["render"], bad_capture)
    reject_nonfinite = {"exit_code": status, "expected": expected["nonfinite_capture"],
                        "output_written": payload is not None,
                        "passed": status == expected["nonfinite_capture"] and payload is None}

    status, payload = _invoke_cli(cli, work, "short", echo["render"],
                                  echo["capture"][:-int(controls["length_short_by_samples"])])
    reject_length = {"exit_code": status, "expected": expected["wrong_length"],
                     "output_written": payload is not None,
                     "passed": status == expected["wrong_length"] and payload is None}

    status, payload = _invoke_cli(cli, work, "rate", echo["render"], echo["capture"],
                                  extra=["--rate", str(controls["wrong_rate_hz"])])
    reject_rate = {"exit_code": status, "expected": expected["wrong_rate"],
                   "output_written": payload is not None,
                   "passed": status == expected["wrong_rate"] and payload is None}

    missing_dir = work / "missing-render"
    missing_dir.mkdir(parents=True, exist_ok=True)
    (missing_dir / "capture.f32").write_bytes(f32_bytes(echo["capture"]))
    output_path = missing_dir / "output.f32"
    missing = subprocess.run(
        [str(cli), "--render", str(missing_dir / "absent.f32"),
         "--capture", str(missing_dir / "capture.f32"), "--output", str(output_path)],
        capture_output=True, text=True)
    reject_missing = {"exit_code": missing.returncode,
                      "expected": expected["missing_render"],
                      "output_written": output_path.exists(),
                      "passed": (missing.returncode == expected["missing_render"]
                                 and not output_path.exists())}

    default_on = json.loads(json.dumps(recipe))
    default_on["activation"]["default_enabled"] = True
    default_ok, default_reason = validate_recipe(default_on, fixtures)
    reject_default = {"reason": default_reason, "passed": not default_ok}

    substituted = json.loads(json.dumps(recipe))
    substituted["variants"]["duplex_base"]["nodes"][0]["provider_id"] = "unknown.provider.v0"
    substituted_ok, substituted_reason = validate_recipe(substituted, fixtures)
    reject_provider = {"reason": substituted_reason, "passed": not substituted_ok}

    tampered = json.loads(json.dumps(fixtures))
    tampered["source_pins"][0]["sha256"] = controls["tampered_pin_prefix"]
    tampered_pin_results = check_pins(tampered)
    reject_pin = {"verified_count": sum(1 for item in tampered_pin_results if item["verified"]),
                  "passed": not all(item["verified"] for item in tampered_pin_results)}

    bad_frames = [
        {"index": 0, "timestamp_ns": ORIGIN_NS, "present": True},
        {"index": 1, "timestamp_ns": ORIGIN_NS, "present": True},
    ]
    bad_timeline = classify_reference_frames(bad_frames, fixtures)
    reject_clock = {"reasons": bad_timeline["reasons"], "decision": bad_timeline["reference_decision"],
                    "passed": ("nonmonotonic_timestamps" in bad_timeline["reasons"]
                               and bad_timeline["reference_decision"] == "capture_only")}

    stale_frames = [
        {"index": 0, "timestamp_ns": ORIGIN_NS - FRAME_NS, "present": True},
        {"index": 1, "timestamp_ns": ORIGIN_NS, "present": True},
    ]
    stale_timeline = classify_reference_frames(stale_frames, fixtures)
    reject_stale = {"reasons": stale_timeline["reasons"],
                    "decision": stale_timeline["reference_decision"],
                    "passed": ("stale_reference" in stale_timeline["reasons"]
                               and stale_timeline["reference_decision"] == "capture_only")}

    absent_timeline = build_timeline(fixtures, "reference_absent", streams)
    forced_error = ""
    try:
        apply_variant(recipe, "capture_residual", streams["reference_absent"]["capture"],
                      absent_timeline["aligned_render"], absent_timeline["render_activity"],
                      None, absent_timeline)
    except ControlError as exc:
        forced_error = str(exc)
    reject_residual = {
        "reference_decision": absent_timeline["reference_decision"],
        "forced_error": forced_error,
        "passed": (absent_timeline["reference_decision"] == "capture_only"
                   and "residual_without_reference" in forced_error),
    }

    passthrough, payload = run_mdf(cli, work, "zero-render",
                                   streams["near_end_only"]["render"],
                                   streams["near_end_only"]["capture"])
    passthrough_digest = digest_samples(passthrough)
    zero_render = {"mdf_output_digest": passthrough_digest,
                   "capture_digest": digest_samples(streams["near_end_only"]["capture"]),
                   "passed": (passthrough_digest
                              == digest_samples(streams["near_end_only"]["capture"])
                              and payload == f32_bytes(passthrough))}

    results = {
        "reject_nonfinite_capture": reject_nonfinite,
        "reject_wrong_length": reject_length,
        "reject_wrong_rate": reject_rate,
        "reject_missing_render": reject_missing,
        "reject_nonmonotonic_timestamps": reject_clock,
        "reject_stale_reference": reject_stale,
        "reject_residual_without_reference": reject_residual,
        "reject_default_on_recipe": reject_default,
        "reject_unknown_provider": reject_provider,
        "reject_tampered_pin_manifest": reject_pin,
        "zero_render_bit_exact_passthrough": zero_render,
    }
    results["expected_controls"] = list(controls["expected_rejections"]) + [
        "zero_render_bit_exact_passthrough"]
    results["all_expected"] = all(
        results[name]["passed"] for name in results["expected_controls"])
    return results


def build_report(cli: Path, work: Path) -> dict[str, Any]:
    cli = Path(cli).resolve()
    work = Path(work).resolve()
    if not cli.is_file():
        raise ControlError("cli_missing:" + str(cli))
    recipe = load_json("recipe.json")
    fixtures = load_json("fixtures.json")
    valid, reason = validate_recipe(recipe, fixtures)
    if not valid:
        raise ControlError("recipe_invalid:" + reason)
    pins = check_pins(fixtures)
    if not all(pin["verified"] for pin in pins):
        raise ControlError("source_pin_mismatch")
    dependencies = check_dependency_pins(fixtures)
    if not all(value for key, value in dependencies.items() if key.endswith("_verified")):
        raise ControlError("dependency_pin_mismatch")

    streams = generate_streams(fixtures)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    repeats: list[dict[str, Any]] = []
    repeat_digests: list[str] = []
    for index in range(3):
        matrix = run_matrix(cli, work / ("repeat-%02d" % index), recipe, fixtures, streams)
        repeats.append(matrix)
        repeat_digests.append(canonical_digest(matrix))

    cases: dict[str, Any] = {}
    for case_name, matrix in recipe["case_matrix"].items():
        variants: dict[str, Any] = {}
        for name in matrix:
            per_repeat = [run[case_name]["variants"][name] for run in repeats]
            digests = [entry["output_digest"] for entry in per_repeat]
            result = dict(per_repeat[0])
            result["output_digests"] = digests
            result["repeat_bytes_identical"] = len(set(digests)) == 1
            variants[name] = result
        first = repeats[0][case_name]
        mdf_stage = first["mdf_stage"]
        if mdf_stage is not None:
            stage_digests = [run[case_name]["mdf_stage"]["stage_digest"] for run in repeats]
            mdf_stage = dict(mdf_stage)
            mdf_stage["stage_digests"] = stage_digests
            mdf_stage["repeat_bytes_identical"] = len(set(stage_digests)) == 1
        cases[case_name] = {
            "note": first["note"],
            "reference_status": first["reference_status"],
            "render_mode": first["render_mode"],
            "echo_path": first["echo_path"],
            "timeline_injection": first["timeline_injection"],
            "reference_decision": first["reference_decision"],
            "reasons": first["reasons"],
            "timeline": first["timeline"],
            "capture_dropout_frames": first["capture_dropout_frames"],
            "render_source_digest": first["render_source_digest"],
            "aligned_render_digest": first["aligned_render_digest"],
            "capture_digest": first["capture_digest"],
            "near_reference_digest": first["near_reference_digest"],
            "mdf_stage": mdf_stage,
            "variants": variants,
        }

    controls = run_controls(cli, work / "controls", recipe, fixtures, streams)
    expectations = fixtures["merged_oracle_expectations"]
    echo = cases["echo_only"]
    content = cases["content_skew_undetected"]
    overlap = cases["double_talk_overlap"]
    near = cases["near_end_only"]
    aligned_mdf = echo["mdf_stage"]["stage_digest"]
    skewed_mdf = content["mdf_stage"]["stage_digest"]
    skew_repaired = cases["skew_timestamp_repair"]["mdf_stage"]["stage_digest"]
    comparisons = {
        "merged_render_digest_exact": (
            echo["render_source_digest"] == expectations["echo_only"]["render_digest"]),
        "merged_capture_digest_exact": (
            echo["capture_digest"] == expectations["echo_only"]["capture_digest"]),
        "merged_echo_mdf_output_exact": (
            aligned_mdf == expectations["echo_only"]["mdf_output_digest"]),
        "merged_erle_values_exact": (
            echo["mdf_stage"]["erle_db_converged"]
            == expectations["echo_only"]["erle_db_converged"]
            and content["mdf_stage"]["erle_db_converged"]
            == expectations["content_skew_undetected"]["erle_db_converged"]),
        "merged_overlap_values_exact": (
            overlap["capture_digest"] == expectations["double_talk_overlap"]["capture_digest"]
            and overlap["mdf_stage"]["stage_digest"]
            == expectations["double_talk_overlap"]["mdf_output_digest"]
            and overlap["mdf_stage"]["near_ratio_overlap"]
            == expectations["double_talk_overlap"]["near_ratio_overlap"]),
        "merged_near_passthrough_exact": (
            near["capture_digest"] == expectations["near_end_only"]["capture_digest"]
            and near["mdf_stage"]["stage_digest"]
            == expectations["near_end_only"]["mdf_output_digest"]),
        "content_skew_mdf_output_exact": (
            skewed_mdf == expectations["content_skew_undetected"]["mdf_output_digest"]),
        "timestamp_skew_repair_restores_aligned_mdf": skew_repaired == aligned_mdf,
        "identity_preserves_capture_bit_exact": all(
            case["variants"]["identity"]["output_digest"] == case["capture_digest"]
            for case in cases.values()),
        "residual_toggle_independent_of_mdf": (
            echo["variants"]["duplex_residual"]["output_digest"]
            != echo["variants"]["duplex_base"]["output_digest"]
            and echo["variants"]["duplex_residual"]["suppressed_frames"] > 0),
        "reference_fault_excludes_residual_and_mdf": all(
            not any(
                node["provider_id"] in MDF_PROVIDERS
                or node["provider_id"] == "fixture.residual_suppressor_surrogate.v0"
                for name in recipe["case_matrix"][case_name]
                for node in recipe["variants"][name]["nodes"])
            for case_name in ("render_dropout", "reference_absent", "reference_stale")),
        "reference_fault_forces_capture_only": all(
            cases[name]["reference_decision"] == "capture_only"
            and cases[name]["reasons"]
            for name in ("render_dropout", "reference_absent", "reference_stale")),
        "capture_dropout_keeps_valid_reference": (
            cases["capture_dropout"]["reference_decision"] == "duplex"
            and len(cases["capture_dropout"]["capture_dropout_frames"]) > 0),
        "all_outputs_finite_and_full_length": all(
            result["output"]["finite"]
            and result["output"]["samples"] == int(fixtures["stimulus"]["samples"])
            for case in cases.values() for result in case["variants"].values()),
        "all_repeat_outputs_identical": all(
            result["repeat_bytes_identical"] and result["output"]["nonfinite_count"] == 0
            for case in cases.values() for result in case["variants"].values()),
    }
    alignment = {
        "warm_aligned_erle_db": echo["mdf_stage"]["erle_db_converged"],
        "content_skew_erle_db": content["mdf_stage"]["erle_db_converged"],
        "misalignment_erle_not_a_detector": (
            content["mdf_stage"]["erle_db_converged"]
            > echo["mdf_stage"]["erle_db_converged"]),
        "timestamp_skew_repaired_frames": (
            cases["skew_timestamp_repair"]["timeline"]["timestamp_skew_repaired_frames"]),
        "changing_delay_warm_post_change_erle_db": (
            cases["changing_delay_warm"]["mdf_stage"]["erle_db_post_change"]),
        "changing_delay_reset_post_change_erle_db": (
            cases["changing_delay_reset"]["mdf_stage"]["erle_db_post_change"]),
        "reset_output_differs_from_warm": (
            cases["changing_delay_reset"]["mdf_stage"]["stage_digest"]
            != cases["changing_delay_warm"]["mdf_stage"]["stage_digest"]),
        "warm_and_reset_finite": all(
            cases[name]["mdf_stage"]["finite"]
            for name in ("changing_delay_warm", "changing_delay_reset")),
        "overlap_near_ratio_including_residual_echo": (
            overlap["mdf_stage"]["near_ratio_overlap"]),
        "disclosure": ("One-frame reference shift is not detected by ERLE; small "
                       "overlap does not qualify double-talk or residual suppressor quality."),
    }
    core: dict[str, Any] = {
        "schema_id": SCHEMA + "/report",
        "task": "SDK-PIPE-DUPLEX",
        "status": "proposal_only_synthetic_incomplete",
        "claim": "none",
        "base_commit": "45b1b82a021ba350ee9e419013df146785b2f426",
        "parent_commit": "c41814bc0ea39151c29ca83fbde9267ccc063493",
        "branch": "swarm/SDK-PIPE-DUPLEX",
        "fixed_v0": fixtures["fixed_v0"],
        "activation": recipe["activation"],
        "recipe_digest": canonical_digest(recipe),
        "fixtures_digest": canonical_digest(fixtures),
        "source_pins": pins,
        "source_pin_count": len(pins),
        "dependency_pins": dependencies,
        "merged_oracle_expectations": expectations,
        "cases": cases,
        "case_count": len(cases),
        "comparisons": comparisons,
        "alignment_and_disclosure": alignment,
        "controls": controls,
        "repeat_runs": {
            "method": "three independent full render/align/MDF/post-stage report builds",
            "canonical_digests": repeat_digests,
            "three_repeats": len(repeat_digests),
            "byte_identical": len(set(repeat_digests)) == 1,
        },
        "change_scope": {
            "task_local_files_only": True,
            "cmake_ci_edits": 0,
            "abi_or_default_changes": 0,
            "provider_substitutions": [],
            "tolerance_widening": [],
            "external_assets": 0,
            "scratch_audio_and_build_bytes_committed": False,
        },
        "remaining_gates": [
            "independent_review",
            "hosted_ci_and_exact_head_verification",
            "target_runtime_paced_resource_evidence",
            "rights_cleared_paired_real_speech_room_qualification",
            "S10_protocol_clearance_for_any_Tiny16_or_adverse_exploratory_comparison",
            "release_qualification",
        ],
        "non_claims": fixtures["excluded_evidence"],
    }
    checks = [
        all(pin["verified"] for pin in pins),
        all(value for key, value in dependencies.items() if key.endswith("_verified")),
        controls["all_expected"],
        core["repeat_runs"]["byte_identical"],
    ] + list(comparisons.values())
    core["all_checks_pass"] = all(checks)
    if not core["all_checks_pass"]:
        failed = [name for name, passed in
                  zip(["source_pins", "dependency_pins", "controls", "repeat"]
                      + list(comparisons), checks)
                  if not passed]
        raise ControlError("acceptance_checks_failed:" + ",".join(failed))
    return core
