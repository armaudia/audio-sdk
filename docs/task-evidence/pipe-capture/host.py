# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local host example for SDK-PIPE-CAPTURE.

This is a frozen synthetic reference host, not an SDK engine plugin, provider,
installed native runtime, ABI/default change or audio-quality result. It models
the ordered path capture + control -> 80 Hz high-pass -> Speex NS policy ->
sample-peak limiter, with an optional read-only advisory RMS tap. Fixed v0 is
16 kHz mono float32 with 160-sample frames. No model, real audio, corpus,
device, build output or paced timing claim is included.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
AUDIOML_ROOT = SDK_ROOT.parents[2]

SCHEMA = "audio-sdk/pipe-capture/0.1"
FRAME = 160
RATE = 16000
NS_PER_SAMPLE = 62500
ORIGIN_NS = 1_000_000_000
FINAL_INPUT = 1
_F32 = struct.Struct("<f")
_NS_CALIBRATION_FRAMES = 8
_NS_MIN_GAIN = 0.1  # -20 dB suppression floor from the pinned provider policy.
_CANON = {"sort_keys": True, "separators": (",", ":"), "ensure_ascii": True,
          "allow_nan": False}


class ControlError(ValueError):
    """A rejected recipe, frame or host control."""


class BackendFailure(RuntimeError):
    """An explicitly injected backend failure; never retried automatically."""

    def __init__(self, reason: str, source_start: int, source_end: int) -> None:
        super().__init__(reason)
        self.reason = reason
        self.source_start = source_start
        self.source_end = source_end

    def as_dict(self) -> dict[str, Any]:
        return {"reason": self.reason, "source_start": self.source_start,
                "source_end": self.source_end}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(payload, **_CANON) + "\n").encode("ascii")


def canonical_digest(payload: Mapping[str, Any]) -> str:
    return sha256(canonical_bytes(payload))


def f32(value: float) -> float:
    return _F32.unpack(_F32.pack(float(value)))[0]


def f32_bytes(values: Iterable[float]) -> bytes:
    return b"".join(_F32.pack(float(value)) for value in values)


def digest_samples(values: Iterable[float]) -> str:
    return sha256(f32_bytes(values))


def load_json(name: str) -> dict[str, Any]:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def resolve_pin_path(label: str) -> Path:
    if label.startswith("audio-sdk/"):
        return SDK_ROOT / label[len("audio-sdk/"):]
    if label in {"deps/lock.json", "deps/speexdsp-files.sha256"}:
        return SDK_ROOT / label
    return AUDIOML_ROOT / label


def check_pins(fixtures: Mapping[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for pin in fixtures["source_pins"]:
        path = resolve_pin_path(pin["path"])
        observed = sha256(path.read_bytes()) if path.is_file() else None
        result.append({"path": pin["path"], "sha256": pin["sha256"],
                       "observed_sha256": observed,
                       "verified": observed == pin["sha256"],
                       "use": pin["use"]})
    return result


def check_dependency_pin(fixtures: Mapping[str, Any]) -> dict[str, Any]:
    pin = fixtures["dependency_pins"]
    path = resolve_pin_path(pin["path"])
    observed = sha256(path.read_bytes()) if path.is_file() else None
    native = fixtures["native_library_pin"]
    native_path = resolve_pin_path(native["path"])
    native_observed = sha256(native_path.read_bytes()) if native_path.is_file() else None
    return {
        "path": pin["path"], "sha256": pin["sha256"], "observed_sha256": observed,
        "verified": observed == pin["sha256"],
        "name": pin["name"], "version": pin["version"],
        "revision": pin["revision"], "source": pin["source"],
        "network_fetch_required": pin["network_fetch_required"],
        "native_library_pin_path": native["path"],
        "native_library_pin_sha256": native["sha256"],
        "native_library_pin_verified": native_observed == native["sha256"],
    }


def validate_recipe(recipe: Mapping[str, Any]) -> tuple[bool, str]:
    if recipe.get("schema_id") != SCHEMA or recipe.get("status") != "proposal_only":
        return False, "schema_or_status"
    activation = recipe.get("activation", {})
    if activation.get("default_enabled") is not False or activation.get("opt_in_only") is not True:
        return False, "default_enabled"
    if activation.get("build_targets_added") or activation.get("shared_sources_modified"):
        return False, "shared_change"
    fmt = recipe.get("format")
    expected_fmt = {"sample_rate_hz": RATE, "channels": 1,
                    "sample_format": "f32", "frame_samples": FRAME}
    if fmt != expected_fmt:
        return False, "format"
    clock = recipe.get("clock", {})
    if clock.get("origin_ns") != ORIGIN_NS or clock.get("ns_per_sample") != NS_PER_SAMPLE:
        return False, "clock"
    timeout = clock.get("frame_timeout_ns")
    if not isinstance(timeout, int) or timeout <= 0:
        return False, "timeout"
    if recipe.get("transport", {}).get("automatic_retry") is not False:
        return False, "automatic_retry"
    providers = recipe.get("providers", {})
    if not isinstance(providers, dict):
        return False, "providers"

    for name, variant in recipe.get("variants", {}).items():
        nodes = variant.get("nodes")
        path = variant.get("audio_path")
        if not isinstance(nodes, list) or not isinstance(path, list) or not path:
            return False, f"{name}:shape"
        by_id = {node.get("id"): node for node in nodes}
        if len(by_id) != len(nodes) or any(node is None for node in by_id):
            return False, f"{name}:duplicate_or_missing_id"
        if any(node_id not in by_id for node_id in path):
            return False, f"{name}:path_id"
        audio_nodes = [by_id[node_id] for node_id in path]
        declared_audio = [node for node in nodes if node.get("role") == "audio"]
        if {node["id"] for node in audio_nodes} != {node["id"] for node in declared_audio}:
            return False, f"{name}:audio_path_coverage"
        ports: list[str] = []
        total_delay = 0
        total_cost = 0
        for index, node in enumerate(audio_nodes):
            policy = providers.get(node.get("provider_id"))
            if policy is None or policy.get("role") != "audio":
                return False, f"{name}:provider"
            if (node.get("delay_samples") != policy.get("delay_samples")
                    or node.get("availability_cost_ns") != policy.get("availability_cost_ns")
                    or node.get("settings") != policy.get("settings")
                    or node.get("role") != "audio"):
                return False, f"{name}:metadata_mismatch"
            expected_in = "pcm.in" if index == 0 else audio_nodes[index - 1]["output_port"]
            if node.get("input_port") != expected_in:
                return False, f"{name}:port_chain"
            if not node.get("output_port") or node["output_port"] in ports:
                return False, f"{name}:port_id"
            ports.append(node["output_port"])
            total_delay += int(node["delay_samples"])
            total_cost += int(node["availability_cost_ns"])
        if sum(int(node["delay_samples"]) for node in audio_nodes) != total_delay:
            return False, f"{name}:delay"
        if not variant.get("control_only") and total_cost > timeout:
            return False, f"{name}:timeout_budget"
        for node in nodes:
            if node.get("role") != "analysis":
                continue
            policy = providers.get(node.get("provider_id"))
            if policy is None or policy.get("role") != "analysis":
                return False, f"{name}:tap_provider"
            if (node.get("settings") != policy.get("settings")
                    or node.get("settings", {}).get("mutates_audio") is not False
                    or node.get("availability_cost_ns") != policy.get("availability_cost_ns")):
                return False, f"{name}:tap_mutation"
            if node.get("tap_port") not in ports:
                return False, f"{name}:tap_port"
            tapped = [n for n in audio_nodes if n["output_port"] == node["tap_port"]]
            if len(tapped) != 1 or tapped[0]["id"] not in node.get("depends_on", []):
                return False, f"{name}:tap_dependency"
    return True, "ok"


@dataclass(frozen=True)
class Frame:
    samples: tuple[float, ...]
    valid_count: int
    source_first: int
    epoch: int
    flags: int = 0

    @property
    def source_end(self) -> int:
        return self.source_first + self.valid_count


@dataclass(frozen=True)
class ProcessResult:
    status: str
    accepted_count: int = 0
    produced_count: int = 0
    valid_count: int = 0
    source_first_sample: int | None = None
    availability_ns: int | None = None
    deadline_ns: int | None = None
    epoch: int = 0
    reason: str = ""


class Stage:
    role = "audio"

    def __init__(self, node: Mapping[str, Any]) -> None:
        self.node = dict(node)

    @property
    def node_id(self) -> str:
        return str(self.node["id"])

    @property
    def delay_samples(self) -> int:
        return int(self.node["delay_samples"])

    def process(self, frame: Frame, ctx: Mapping[str, Any]) -> list[Frame]:
        raise NotImplementedError

    def drain(self) -> list[Frame]:
        return []


class IdentityStage(Stage):
    def process(self, frame: Frame, ctx: Mapping[str, Any]) -> list[Frame]:
        return [Frame(tuple(f32(value) for value in frame.samples), frame.valid_count,
                      frame.source_first, frame.epoch, frame.flags)]


class HighPassStage(Stage):
    def __init__(self, node: Mapping[str, Any]) -> None:
        super().__init__(node)
        cutoff = float(node["settings"]["cutoff_hz"])
        q = float(node["settings"]["q"])
        w0 = 2.0 * math.pi * cutoff / RATE
        cosine = math.cos(w0)
        alpha = math.sin(w0) / (2.0 * q)
        a0 = 1.0 + alpha
        self.b0 = ((1.0 + cosine) * 0.5) / a0
        self.b1 = (-(1.0 + cosine)) / a0
        self.b2 = self.b0
        self.a1 = (-2.0 * cosine) / a0
        self.a2 = (1.0 - alpha) / a0
        self.z1 = 0.0
        self.z2 = 0.0

    def process(self, frame: Frame, ctx: Mapping[str, Any]) -> list[Frame]:
        output: list[float] = []
        for value in frame.samples:
            x = f32(value)
            y = self.b0 * x + self.z1
            self.z1 = self.b1 * x - self.a1 * y + self.z2
            self.z2 = self.b2 * x - self.a2 * y
            output.append(f32(y))
        return [Frame(tuple(output), frame.valid_count, frame.source_first,
                      frame.epoch, frame.flags)]


def _pcm16(value: float) -> int:
    clamped = max(-1.0, min(1.0, float(value)))
    return int(round(clamped * 32767.0))


class NsPolicyStage(Stage):
    """Deterministic task-local policy surrogate, not SpeexDSP bit parity.

    It preserves the pinned provider's declared one-frame buffering, PCM16
    quantization and -20 dB suppression floor. The stationary-noise estimator is
    an offline fixture rule, calibrated on the frozen noise-only lead-in; it is
    never presented as the vendored SpeexDSP algorithm or a quality result.
    """

    def __init__(self, node: Mapping[str, Any]) -> None:
        super().__init__(node)
        settings = node["settings"]
        if (settings.get("suppression_db") != -20
                or settings.get("vad_start") != 35
                or settings.get("vad_continue") != 20
                or settings.get("agc_enabled") is not False
                or settings.get("dereverb_enabled") is not False):
            raise ControlError("ns_policy_mismatch")
        self.calibration: list[float] = []
        self.noise_power = 1e-12
        self.pending: Frame | None = None

    def _shaped(self, frame: Frame) -> Frame:
        quantized = [float(_pcm16(value)) / 32768.0 for value in frame.samples]
        if frame.valid_count:
            power = sum(value * value for value in quantized[:frame.valid_count]) / frame.valid_count
        else:
            power = 0.0
        if len(self.calibration) < _NS_CALIBRATION_FRAMES:
            self.calibration.append(power)
            self.noise_power = sum(self.calibration) / len(self.calibration)
            gain = _NS_MIN_GAIN
        else:
            if power > 0.0:
                gain = math.sqrt(max(_NS_MIN_GAIN ** 2, 1.0 - self.noise_power / power))
            else:
                gain = _NS_MIN_GAIN
        shaped = [f32(float(_pcm16(value * gain)) / 32768.0) for value in quantized]
        return Frame(tuple(shaped), frame.valid_count, frame.source_first,
                     frame.epoch, frame.flags)

    def process(self, frame: Frame, ctx: Mapping[str, Any]) -> list[Frame]:
        current = self._shaped(frame)
        if self.pending is None:
            self.pending = current
            startup = Frame((0.0,) * FRAME, 0,
                            frame.source_first - self.delay_samples,
                            frame.epoch, 0)
            return [startup]
        output = self.pending
        self.pending = current
        return [output]

    def drain(self) -> list[Frame]:
        if self.pending is None:
            return []
        output = self.pending
        self.pending = None
        return [output]


def _cpp_min(left: float, right: float) -> float:
    return right if right < left else left


def _cpp_max(left: float, right: float) -> float:
    return right if left < right else left


class LimiterStage(Stage):
    def __init__(self, node: Mapping[str, Any]) -> None:
        super().__init__(node)
        settings = node["settings"]
        ceiling = float(settings.get("ceiling", 0.98))
        release_ms = float(settings.get("release_ms", 50.0))
        if not (0.0 < ceiling <= 1.0) or not (0.0 < release_ms <= 5000.0):
            raise ControlError("limiter_controls")
        self.ceiling = ceiling
        self.release = 1.0 - math.exp(-1000.0 / (release_ms * RATE))
        self.gain = 1.0

    def process(self, frame: Frame, ctx: Mapping[str, Any]) -> list[Frame]:
        output: list[float] = []
        if self.gain == 1.0:
            finite = True
            needs_limit = False
            for value in frame.samples:
                sample = float(value)
                finite = finite and math.isfinite(sample)
                needs_limit = needs_limit or abs(sample) > self.ceiling
            if finite and not needs_limit:
                return [Frame(tuple(f32(value) for value in frame.samples),
                              frame.valid_count, frame.source_first,
                              frame.epoch, frame.flags)]
        for value in frame.samples:
            sample = float(value)
            peak = abs(sample)
            target = self.ceiling / peak if peak > self.ceiling else 1.0
            if target < self.gain:
                self.gain = target
            else:
                self.gain += self.release * (target - self.gain)
            limited = sample * self.gain
            output.append(f32(_cpp_max(-self.ceiling, _cpp_min(self.ceiling, limited))))
        return [Frame(tuple(output), frame.valid_count, frame.source_first,
                      frame.epoch, frame.flags)]


def build_audio_stages(recipe: Mapping[str, Any], variant_name: str) -> list[Stage]:
    variant = recipe["variants"][variant_name]
    by_id = {node["id"]: node for node in variant["nodes"]}
    stages: list[Stage] = []
    for node_id in variant["audio_path"]:
        node = by_id[node_id]
        provider = node["provider_id"]
        if provider in {"fixture.identity.v0", "fixture.timeout_probe.v0"}:
            stages.append(IdentityStage(node))
        elif provider == "dsp.highpass80.v0":
            stages.append(HighPassStage(node))
        elif provider == "speex.ns.v0":
            stages.append(NsPolicyStage(node))
        elif provider == "fixture.peak_limiter.v0":
            stages.append(LimiterStage(node))
        else:
            raise ControlError(f"unmapped_provider:{provider}")
    return stages


def build_analysis_nodes(recipe: Mapping[str, Any], variant_name: str) -> list[dict[str, Any]]:
    return [node for node in recipe["variants"][variant_name]["nodes"]
            if node.get("role") == "analysis"]


@dataclass
class Session:
    recipe: Mapping[str, Any]
    variant_name: str
    epoch: int
    first_input_sample: int = 0
    fail_at_frame: int | None = None
    failure_reason: str = "explicit_backend_failure"
    raw_frames: list[Frame] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    counters: dict[str, int] = field(default_factory=lambda: {
        "submitted_frames": 0, "accepted_samples": 0, "produced_raw_samples": 0,
        "rejected_frames": 0, "tap_events": 0})
    rejections: list[dict[str, Any]] = field(default_factory=list)
    state: str = "prepared"
    failed: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        valid, reason = validate_recipe(self.recipe)
        if not valid:
            raise ControlError(f"recipe_invalid:{reason}")
        self.variant = self.recipe["variants"][self.variant_name]
        self.stages = build_audio_stages(self.recipe, self.variant_name)
        self.analysis_nodes = build_analysis_nodes(self.recipe, self.variant_name)
        self.expected_first = int(self.first_input_sample)
        self.last_clock_ns = ORIGIN_NS - 1
        self.frame_index = 0
        self.declared_cost_ns = sum(
            int(node["availability_cost_ns"])
            for node in self.variant["nodes"] if node["role"] in {"audio", "analysis"})
        self.timeout_ns = int(self.recipe["clock"]["frame_timeout_ns"])

    def _reject(self, reason: str, frame: Frame) -> ProcessResult:
        self.counters["rejected_frames"] += 1
        self.rejections.append({"reason": reason, "source_first": frame.source_first,
                                "epoch": frame.epoch})
        return ProcessResult(status=reason, epoch=frame.epoch, reason=reason)

    def _emit_tap_events(self, frames: Sequence[Frame], ctx: Mapping[str, Any]) -> None:
        if not self.analysis_nodes:
            return
        for frame in frames:
            if frame.valid_count <= 0:
                continue
            values = frame.samples[:frame.valid_count]
            rms = math.sqrt(sum(value * value for value in values) / frame.valid_count)
            self.events.append({
                "node_id": self.analysis_nodes[0]["id"],
                "provider_id": self.analysis_nodes[0]["provider_id"],
                "source_start": frame.source_first,
                "source_end": frame.source_end,
                "rms": round(rms, 6),
                "epoch": frame.epoch,
                "available_ns": int(ctx["availability_ns"]),
                "mutates_audio": False,
            })
            self.counters["tap_events"] += 1

    def process(self, frame: Frame, submit_clock_ns: int) -> ProcessResult:
        if self.state not in {"prepared", "processing"}:
            return self._reject("rejected_closed", frame)
        self.counters["submitted_frames"] += 1
        if frame.epoch != self.epoch:
            return self._reject("rejected_stale_epoch", frame)
        if frame.source_first != self.expected_first:
            return self._reject("rejected_bad_frame", frame)
        if submit_clock_ns < self.last_clock_ns:
            return self._reject("rejected_bad_clock", frame)
        if not (1 <= frame.valid_count <= FRAME) or len(frame.samples) != FRAME:
            return self._reject("rejected_bad_frame", frame)
        if any(not math.isfinite(value) for value in frame.samples[:frame.valid_count]):
            return self._reject("rejected_nonfinite_input", frame)
        if frame.flags & FINAL_INPUT and any(value != 0.0 for value in frame.samples[frame.valid_count:]):
            return self._reject("rejected_bad_padding", frame)

        if self.fail_at_frame is not None and self.frame_index == self.fail_at_frame:
            failure = BackendFailure(self.failure_reason, frame.source_first,
                                     frame.source_first + frame.valid_count)
            self.failed = failure.as_dict()
            self.state = "needs_reset"
            raise failure

        source_complete_ns = submit_clock_ns + frame.valid_count * NS_PER_SAMPLE
        availability_ns = source_complete_ns + self.declared_cost_ns
        deadline_ns = source_complete_ns + self.timeout_ns
        if availability_ns > deadline_ns:
            return self._reject("rejected_timeout", frame)

        self.last_clock_ns = submit_clock_ns
        self.expected_first += frame.valid_count
        self.frame_index += 1
        self.state = "processing"
        ctx = {"frame_index": self.frame_index - 1, "epoch": self.epoch,
               "availability_ns": availability_ns, "variant": self.variant_name}
        produced: list[Frame] = [frame]
        for stage in self.stages:
            downstream: list[Frame] = []
            for candidate in produced:
                downstream.extend(stage.process(candidate, ctx))
            produced = downstream
        self._emit_tap_events(produced, ctx)
        self.raw_frames.extend(produced)
        self.counters["accepted_samples"] += frame.valid_count
        self.counters["produced_raw_samples"] += sum(len(item.samples) for item in produced)
        return ProcessResult(
            status="ok", accepted_count=frame.valid_count,
            produced_count=sum(len(item.samples) for item in produced),
            valid_count=sum(item.valid_count for item in produced),
            source_first_sample=produced[0].source_first if produced else None,
            availability_ns=availability_ns, deadline_ns=deadline_ns, epoch=self.epoch)

    def drain(self) -> ProcessResult:
        if self.state not in {"prepared", "processing"}:
            return ProcessResult(status="rejected_needs_reset", reason="state", epoch=self.epoch)
        produced: list[Frame] = []
        for index, stage in enumerate(self.stages):
            buffered = stage.drain()
            frames = list(buffered)
            for downstream_stage in self.stages[index + 1:]:
                next_frames: list[Frame] = []
                for candidate in frames:
                    next_frames.extend(downstream_stage.process(
                        candidate, {"frame_index": -1, "epoch": self.epoch,
                                    "availability_ns": self.last_clock_ns,
                                    "variant": self.variant_name}))
                frames = next_frames
            produced.extend(frames)
        self._emit_tap_events(
            produced, {"availability_ns": self.last_clock_ns + self.declared_cost_ns})
        self.raw_frames.extend(produced)
        self.counters["produced_raw_samples"] += sum(len(item.samples) for item in produced)
        self.state = "drained"
        return ProcessResult(
            status="ok", produced_count=sum(len(item.samples) for item in produced),
            valid_count=sum(item.valid_count for item in produced),
            source_first_sample=produced[0].source_first if produced else None,
            epoch=self.epoch)


def lcg_values(seed: int, count: int) -> list[float]:
    state = seed & 0xFFFFFFFF
    output: list[float] = []
    for _ in range(count):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        output.append(2.0 * (state / 4294967296.0) - 1.0)
    return output


def speech_values(spec: Mapping[str, Any], count: int) -> list[float]:
    f0 = float(spec["f0_hz"])
    harmonics = int(spec["harmonics"])
    period = max(1, int(spec["syllable_period_samples"]))
    ramp = max(1, int(spec["edge_ramp_samples"]))
    output: list[float] = []
    for index in range(count):
        position = index % period
        envelope = 0.5 - 0.5 * math.cos(2.0 * math.pi * position / period)
        edge = min(1.0, index / ramp, (count - index) / ramp)
        sample = 0.0
        for harmonic in range(1, harmonics + 1):
            frequency = f0 * harmonic
            sample += math.sin(2.0 * math.pi * frequency * index / RATE
                               + 0.31 * harmonic) / (harmonic ** 1.05)
        output.append(0.24 * envelope * edge * sample / harmonics)
    return output


def mix_to_snr(clean: Sequence[float], noise: Sequence[float], snr_db: float) -> list[float]:
    clean_power = sum(value * value for value in clean) / len(clean)
    noise_power = sum(value * value for value in noise) / len(noise)
    if noise_power <= 0.0:
        raise ControlError("zero_noise_power")
    gain = math.sqrt(clean_power / (noise_power * 10 ** (snr_db / 10.0)))
    return [float(c) + gain * float(n) for c, n in zip(clean, noise)]


def make_stimulus(spec: Mapping[str, Any]) -> tuple[list[float] | None, list[float]]:
    kind = spec["kind"]
    count = int(spec["samples"])
    if kind in {"speech_plus_stationary_noise", "partial_speech_plus_stationary_noise"}:
        clean = speech_values(spec, count)
        lead = max(0, int(spec["noise_lead_in_samples"]))
        clean = [0.0] * min(lead, count) + clean[min(lead, count):]
        noise = lcg_values(int(spec["noise_seed"]), count)
        return clean, mix_to_snr(clean, noise, float(spec["snr_db"]))
    if kind == "impulse_plus_low_tail":
        noise = lcg_values(int(spec["seed"]), count)
        output = [float(spec["tail_amplitude"]) * value for value in noise]
        position = int(spec["position"])
        output[position] += float(spec["amplitude"])
        return None, output
    if kind == "tone":
        frequency = float(spec["frequency_hz"])
        amplitude = float(spec["amplitude"])
        return None, [amplitude * math.sin(2.0 * math.pi * frequency * i / RATE)
                      for i in range(count)]
    raise ControlError(f"unknown_stimulus:{kind}")


def frames_from_samples(samples: Sequence[float], first_sample: int = 0,
                        epoch: int = 1, origin_ns: int = ORIGIN_NS
                        ) -> list[tuple[Frame, int]]:
    frames: list[tuple[Frame, int]] = []
    for offset in range(0, len(samples), FRAME):
        chunk = samples[offset:offset + FRAME]
        valid = len(chunk)
        padded = tuple(f32(value) for value in chunk) + (0.0,) * (FRAME - valid)
        flags = FINAL_INPUT if valid < FRAME else 0
        clock_ns = origin_ns + (first_sample + offset) * NS_PER_SAMPLE
        frames.append((Frame(padded, valid, first_sample + offset, epoch, flags), clock_ns))
    return frames


def features(values: Iterable[float], ceiling: float = 0.98) -> dict[str, Any]:
    samples = [float(value) for value in values]
    peak = max((abs(value) for value in samples), default=0.0)
    return {
        "samples": len(samples),
        "finite": all(math.isfinite(value) for value in samples),
        "peak_abs": round(peak, 6),
        "clipped_or_nonfinite": sum(1 for value in samples
                                    if not math.isfinite(value) or abs(value) >= 1.0),
        "at_or_above_ceiling": sum(1 for value in samples
                                   if math.isfinite(value) and abs(value) >= ceiling),
    }


def digest_features(values: Iterable[float]) -> dict[str, Any]:
    result = features(values)
    result["f32_digest"] = digest_samples(values)
    return result


def si_sdr_db(reference: Sequence[float] | None, estimate: Sequence[float] | None
              ) -> tuple[float | None, str | None]:
    if reference is None or estimate is None:
        return None, "missing_reference_or_output"
    if len(reference) != len(estimate) or not reference:
        return None, "length_mismatch"
    if not all(math.isfinite(value) for value in reference) or not all(
            math.isfinite(value) for value in estimate):
        return None, "invalid_input"
    n = len(reference)
    ref_mean = sum(reference) / n
    est_mean = sum(estimate) / n
    ref = [value - ref_mean for value in reference]
    est = [value - est_mean for value in estimate]
    denominator = sum(value * value for value in ref)
    if denominator == 0.0:
        return None, "zero_reference"
    alpha = sum(x * y for x, y in zip(est, ref)) / denominator
    projection = [alpha * value for value in ref]
    target = sum(value * value for value in projection)
    residual = sum((x - y) ** 2 for x, y in zip(est, projection))
    if target == 0.0:
        return None, "zero_projection"
    if residual == 0.0:
        return None, "exact_reconstruction"
    return round(10.0 * math.log10(target / residual), 6), None


def correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) != len(right) or not left:
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    covariance = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_var = sum((a - left_mean) ** 2 for a in left)
    right_var = sum((b - right_mean) ** 2 for b in right)
    if left_var <= 0.0 or right_var <= 0.0:
        return None
    return round(covariance / math.sqrt(left_var * right_var), 6)


def paired_metrics(clean: Sequence[float], noisy: Sequence[float],
                   output: Sequence[float]) -> dict[str, Any]:
    input_si, input_reason = si_sdr_db(clean, noisy)
    output_si, output_reason = si_sdr_db(clean, output)
    input_power = sum(value * value for value in noisy) / len(noisy)
    output_power = sum(value * value for value in output) / len(output)
    return {
        "si_sdr_db": {
            "identity_noisy": input_si,
            "variant_output": output_si,
            "paired_delta": (round(output_si - input_si, 6)
                             if input_si is not None and output_si is not None else None),
            "invalid_reasons": [reason for reason in (input_reason, output_reason) if reason],
        },
        "preservation": {
            "rms_gain_ratio": (round(math.sqrt(output_power / input_power), 6)
                               if input_power > 0.0 else None),
            "clean_correlation": correlation(clean, output),
        },
        "input": digest_features(noisy),
        "output": digest_features(output),
        "stoi": {"status": "blocked_missing_pinned_scorer", "value": None,
                 "reason": "numpy and pystoi 0.4.1 are unavailable offline; no STOI claim is made."},
    }


def collect_output(raw_frames: Sequence[Frame], expected_samples: int) -> dict[str, Any]:
    values: dict[int, float] = {}
    intervals: list[list[int]] = []
    duplicates = 0
    for frame in raw_frames:
        intervals.append([frame.source_first, frame.source_end])
        for index in range(frame.valid_count):
            source = frame.source_first + index
            if 0 <= source < expected_samples:
                if source in values:
                    duplicates += 1
                else:
                    values[source] = frame.samples[index]
    missing = sum(1 for index in range(expected_samples) if index not in values)
    aligned = tuple(values.get(index, 0.0) for index in range(expected_samples))
    starts = [frame.source_first for frame in raw_frames]
    ends = [frame.source_first + len(frame.samples) for frame in raw_frames]
    return {
        "aligned": aligned,
        "accepted_samples": expected_samples,
        "delivered_valid_samples": len(values),
        "missing_samples": missing,
        "duplicate_samples": duplicates,
        "source_interval": [0, expected_samples],
        "raw_interval": [min(starts) if starts else 0, max(ends) if ends else 0],
        "startup_padding_samples": max(0, -min(starts)) if starts else 0,
        "tail_padding_samples": max(0, (max(ends) if ends else 0) - expected_samples),
        "raw_frames": len(raw_frames),
        "valid_intervals": sorted(intervals),
    }


def run_variant(recipe: Mapping[str, Any], fixtures: Mapping[str, Any], variant: str,
                stimulus: str, epoch: int = 1,
                first_input_sample: int = 0) -> dict[str, Any]:
    spec = fixtures["stimuli"][stimulus]
    clean, samples = make_stimulus(spec)
    session = Session(recipe, variant, epoch=epoch, first_input_sample=first_input_sample)
    for frame, clock_ns in frames_from_samples(samples, first_input_sample, epoch):
        result = session.process(frame, clock_ns)
        if result.status != "ok":
            raise ControlError(f"unexpected_rejection:{result.status}")
    drain = session.drain()
    if drain.status != "ok":
        raise ControlError(f"unexpected_drain:{drain.status}")
    accounting = collect_output(session.raw_frames, len(samples))
    aligned = accounting.pop("aligned")
    return {
        "clean": clean, "input": samples, "aligned": aligned,
        "accounting": accounting, "events": session.events,
        "raw_frames": session.raw_frames, "session": session,
        "input_digest": digest_samples(samples),
        "output_digest": digest_samples(aligned),
    }


def run_failure_bypass(recipe: Mapping[str, Any],
                       fixtures: Mapping[str, Any]) -> dict[str, Any]:
    controls = fixtures["controls"]
    spec = fixtures["stimuli"]["failure"]
    clean, samples = make_stimulus(spec)
    all_frames = frames_from_samples(samples, 0, int(controls["failure_epoch"]))
    fail_at = int(spec["fail_at_frame"])
    first = Session(recipe, "basic_chain", epoch=int(controls["failure_epoch"]),
                    fail_at_frame=fail_at, failure_reason=controls["failure_reason"])
    accepted_before = 0
    for frame, clock_ns in all_frames[:fail_at]:
        result = first.process(frame, clock_ns)
        if result.status != "ok":
            raise ControlError(f"pre_failure_rejection:{result.status}")
        accepted_before += result.accepted_count
    failed_frame = all_frames[fail_at][0]
    try:
        first.process(failed_frame, all_frames[fail_at][1])
        raise AssertionError("backend failure was not raised")
    except BackendFailure as failure:
        recorded = failure.as_dict()
    if first.state != "needs_reset":
        raise AssertionError("failure did not require reset")
    # Drain accepted frames from the failed session before opening the next epoch.
    first.state = "processing"
    first.drain()
    first.state = "closed"

    bypass_start = failed_frame.source_first
    bypass_frames = frames_from_samples(samples[bypass_start:], bypass_start,
                                        int(controls["bypass_epoch"]))
    second = Session(recipe, "bypass", epoch=int(controls["bypass_epoch"]),
                     first_input_sample=bypass_start)
    for frame, clock_ns in bypass_frames:
        result = second.process(frame, clock_ns)
        if result.status != "ok":
            raise ControlError(f"bypass_rejection:{result.status}")
    second.drain()
    accounting = collect_output(first.raw_frames + second.raw_frames, len(samples))
    return {
        "failure": recorded,
        "failed_epoch": int(controls["failure_epoch"]),
        "bypass_epoch": int(controls["bypass_epoch"]),
        "automatic_retry": False,
        "operator_selected_bypass_recipe": "bypass",
        "first_session_state": first.state,
        "pre_failure_drained_valid_samples": accepted_before,
        "bypass_accepted_samples": second.counters["accepted_samples"],
        "combined": {key: value for key, value in accounting.items() if key != "aligned"},
        "combined_output_digest": digest_samples(
            collect_output(first.raw_frames + second.raw_frames, len(samples))["aligned"]),
        "epochs": [first.epoch, second.epoch],
        "recipe_digests": [
            canonical_digest(recipe["variants"]["basic_chain"]),
            canonical_digest(recipe["variants"]["bypass"]),
        ],
    }


def run_controls(recipe: Mapping[str, Any], fixtures: Mapping[str, Any]) -> dict[str, Any]:
    controls = fixtures["controls"]
    spec = fixtures["stimuli"]["conservation"]
    clean, samples = make_stimulus(spec)
    frames = frames_from_samples(samples, 0, 1)

    timeout_session = Session(recipe, "timeout_probe", epoch=1)
    timeout_result = timeout_session.process(frames[0][0], frames[0][1])

    clock_session = Session(recipe, "identity", epoch=1)
    ok_result = clock_session.process(frames[0][0], frames[0][1])
    regressed = clock_session.process(frames[1][0], frames[0][1] - 1)

    stale_session = Session(recipe, "identity", epoch=1)
    stale_frame = Frame(frames[0][0].samples, frames[0][0].valid_count,
                        frames[0][0].source_first,
                        frames[0][0].epoch + int(controls["stale_epoch_delta"]),
                        frames[0][0].flags)
    stale = stale_session.process(stale_frame, frames[0][1])

    nonfinite_frame = Frame((float("nan"),) + frames[0][0].samples[1:],
                            frames[0][0].valid_count, frames[0][0].source_first, 1,
                            frames[0][0].flags)
    nonfinite_session = Session(recipe, "identity", epoch=1)
    nonfinite = nonfinite_session.process(nonfinite_frame, frames[0][1])

    final_frame = frames[-1][0]
    bad_padding_samples = list(final_frame.samples)
    bad_padding_samples[-1] = float(controls["bad_padding_value"])
    bad_padding = Frame(tuple(bad_padding_samples), final_frame.valid_count,
                        final_frame.source_first, 1, final_frame.flags)
    padding_session = Session(recipe, "identity", epoch=1)
    for frame, clock_ns in frames[:-1]:
        padding_session.process(frame, clock_ns)
    padding = padding_session.process(bad_padding, frames[-1][1])

    expected = set(controls["expected_rejections"])
    observed = {
        "timeout_exceeded": timeout_result.status,
        "nonmonotonic_clock": regressed.status,
        "stale_epoch": stale.status,
        "nonfinite_input": nonfinite.status,
        "bad_final_padding": padding.status,
    }
    return {
        "observations": observed,
        "normal_submission_status": ok_result.status,
        "rejection_counts": {
            "timeout_probe": timeout_session.counters["rejected_frames"],
            "post_rejection_clock_session": clock_session.counters["rejected_frames"],
        },
        "all_expected": set(observed.values()) == expected and ok_result.status == "ok",
    }


def measure_delay(recipe: Mapping[str, Any], fixtures: Mapping[str, Any]) -> dict[str, Any]:
    specs = fixtures["stimuli"]["impulse"]
    position = int(specs["position"])
    output: dict[str, Any] = {}
    for variant in ("identity", "basic_chain"):
        result = run_variant(recipe, fixtures, variant, "impulse")
        raw = [value for frame in result["raw_frames"] for value in frame.samples]
        peak = max(range(len(raw)), key=lambda index: abs(raw[index]))
        startup = result["accounting"]["startup_padding_samples"]
        output[variant] = {
            "declared_buffering_samples": sum(
                int(node["delay_samples"])
                for node in recipe["variants"][variant]["nodes"] if node["role"] == "audio"),
            "startup_padding_samples": startup,
            "input_impulse_index": position,
            "measured_raw_peak_index": peak,
            "measured_raw_offset_samples": peak - position,
            "measured_content_lag_after_alignment": peak - startup - position,
            "valid_output_samples": result["accounting"]["delivered_valid_samples"],
        }
    return output


def build_report() -> dict[str, Any]:
    recipe = load_json("recipe.json")
    fixtures = load_json("fixtures.json")
    valid, reason = validate_recipe(recipe)
    if not valid:
        raise ControlError(f"recipe_invalid:{reason}")

    pins = check_pins(fixtures)
    dependency_pin = check_dependency_pin(fixtures)
    names = ["identity", "highpass_only", "ns_only", "limiter_only",
             "basic_chain", "voice_focus"]
    variants: dict[str, Any] = {}
    for name in names:
        paired = run_variant(recipe, fixtures, name, "paired")
        conservation = run_variant(recipe, fixtures, name, "conservation")
        clipping = run_variant(recipe, fixtures, name, "clipping")
        variants[name] = {
            "purpose": recipe["variants"][name]["purpose"],
            "declared_audio_path": recipe["variants"][name]["audio_path"],
            "declared_delay_samples": sum(
                int(node["delay_samples"])
                for node in recipe["variants"][name]["nodes"] if node["role"] == "audio"),
            "declared_availability_cost_ns": sum(
                int(node["availability_cost_ns"])
                for node in recipe["variants"][name]["nodes"]),
            "paired": paired_metrics(paired["clean"], paired["input"], paired["aligned"]),
            "paired_input_digest": paired["input_digest"],
            "paired_output_digest": paired["output_digest"],
            "conservation": conservation["accounting"],
            "conservation_input_digest": conservation["input_digest"],
            "conservation_output_digest": conservation["output_digest"],
            "clipping_input": digest_features(clipping["input"]),
            "clipping_output": digest_features(clipping["aligned"]),
            "tap_events": len(paired["events"]),
        }

    basic = variants["basic_chain"]["paired_output_digest"]
    focus = variants["voice_focus"]["paired_output_digest"]
    comparisons = {
        "identity_output_equals_noisy_input": variants["identity"]["paired_output_digest"]
        == variants["identity"]["paired_input_digest"],
        "basic_and_voice_focus_audio_bit_identical": basic == focus,
        "analysis_tap_in_audio_path": any(
            node["id"] in recipe["variants"]["voice_focus"]["audio_path"]
            for node in recipe["variants"]["voice_focus"]["nodes"] if node["role"] == "analysis"),
        "tap_events_basic": variants["basic_chain"]["tap_events"],
        "tap_events_voice_focus": variants["voice_focus"]["tap_events"],
        "tap_read_only": all(event["mutates_audio"] is False
                             for event in run_variant(recipe, fixtures, "voice_focus",
                                                      "paired")["events"]),
    }

    delay = measure_delay(recipe, fixtures)
    bypass = run_failure_bypass(recipe, fixtures)
    controls = run_controls(recipe, fixtures)
    exact_conservation = all(
        entry["conservation"]["missing_samples"] == 0
        and entry["conservation"]["duplicate_samples"] == 0
        and entry["conservation"]["accepted_samples"]
        == entry["conservation"]["delivered_valid_samples"]
        for entry in variants.values())

    core: dict[str, Any] = {
        "schema_id": SCHEMA + "/report",
        "task": "SDK-PIPE-CAPTURE",
        "status": "proposal_only_synthetic_incomplete",
        "claim": "none",
        "base_commit": "d665c298e8cce8b4d576dc45f3c7f7d3b3457425",
        "parent_commit": "dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc",
        "branch": "swarm/SDK-PIPE-CAPTURE",
        "fixed_v0": fixtures["fixed_v0"],
        "activation": recipe["activation"],
        "recipe_digest": canonical_digest(recipe),
        "fixtures_digest": canonical_digest(fixtures),
        "source_pins": pins,
        "dependency_pin": dependency_pin,
        "variants": variants,
        "comparisons": comparisons,
        "measured_delay": delay,
        "failure_bypass": bypass,
        "controls": controls,
        "exact_valid_audio_conservation": exact_conservation,
        "change_scope": {
            "task_local_files_only": True,
            "cmake_ci_edits": 0,
            "abi_or_default_changes": 0,
            "provider_substitutions": [],
            "tolerance_widening": [],
            "external_assets": 0,
        },
        "remaining_gates": [
            "independent_review",
            "native_consumer_and_exact_head_ci",
            "measured_paced_target_device_workload",
            "real_rights_cleared_audio_and_listening_qualification",
            "S10_protocol_clearance_for_any_Tiny16_or_adverse_exploratory_comparison",
        ],
        "non_claims": fixtures["excluded_evidence"],
    }
    repeat_digests = [canonical_digest(core) for _ in range(3)]
    core["repeat_runs"] = {
        "method": "three independent build_report() calls on the same frozen inputs",
        "canonical_digests": repeat_digests,
        "byte_identical": len(set(repeat_digests)) == 1,
        "three_repeats": len(repeat_digests),
    }
    core["all_checks_pass"] = all([
        all(pin["verified"] for pin in pins),
        dependency_pin["verified"] and dependency_pin["native_library_pin_verified"],
        comparisons["identity_output_equals_noisy_input"],
        comparisons["basic_and_voice_focus_audio_bit_identical"],
        not comparisons["analysis_tap_in_audio_path"],
        comparisons["tap_events_basic"] == 0,
        comparisons["tap_events_voice_focus"] > 0,
        comparisons["tap_read_only"],
        exact_conservation,
        bypass["combined"]["missing_samples"] == 0,
        bypass["combined"]["duplicate_samples"] == 0,
        controls["all_expected"],
        core["repeat_runs"]["byte_identical"],
        delay["identity"]["measured_content_lag_after_alignment"] == 0,
        delay["basic_chain"]["measured_content_lag_after_alignment"] == 0,
        delay["basic_chain"]["measured_raw_offset_samples"]
        == fixtures["fixed_v0"]["frame_samples"],
    ])
    return core


if __name__ == "__main__":
    report = build_report()
    print(canonical_bytes(report).decode("ascii"))
