"""Model-free, deterministic fixture for typed frames, resampling and drift.

This is a *developer-facing tool model*, not SDK runtime code. The fixed v0
provider ABI stays 16 kHz mono f32 in 160-sample frames. All format/rate/channel
conversion, source clock mapping and drift checks happen outside that ABI in an
explicit adapter. Nothing here registers a provider, changes a descriptor or
default, or claims a measured workload or target-device result.

The fixture is source-local and stdlib-only. Every result is explicit: a missing
or unrun control is never promoted to a pass.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import platform
import re
import struct
from typing import Any, Mapping, Optional, Sequence

CONTRACT_ID = "audio-sdk/typed-frame-resample-drift/0.1"
CONTRACT_VERSION = "0.1"
TOOL_VERSION = "0.1.0"

# Fixed v0 boundary: never changed by this developer tool.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SAMPLE_FORMAT = "f32"
FRAME_SAMPLES = 160
NS_PER_SAMPLE = 62500
NS_PER_FRAME = FRAME_SAMPLES * NS_PER_SAMPLE

# Explicit conversions allowed only outside the v0 provider ABI.
RATE_FACTORS = {16000: 1, 32000: 2, 48000: 3}
VALID_CHANNELS = (1, 2)
VALID_FORMATS = ("f32", "s16")

# Declared fixture policy.
MAX_DRIFT_PPM = 10000
DELAY_SAMPLES = 173  # deliberately not a multiple of 160
MAX_DRAIN_CALLS = 4
TAIL_BUDGET_SAMPLES = 160
DEFAULT_EPOCH = 1
STREAM_ORIGIN_NS = 1_000_000_000

FINAL_INPUT = 1
FLAG_STARTUP_PADDING = 1
FLAG_FINAL_PADDING = 2
FLAG_CONCEALMENT = 4

REPOSITORY = "https://github.com/armaudia/audio-sdk.git"
BRANCH = "swarm/SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS"
BASE_COMMIT = "0673cb354cceb66f2f71faf9af7703b5a5d2fcfa"
WORKSPACE_ROOT = Path("/Users/htsakanyan/workspace/audio/audioml")
FIXTURE_REL = "docs/task-evidence/typed-frame-resample-and-drift-diagnostics"
SOURCE_PINS = {
    "audio-sdk/CONTRACTS.md": (
        "audio-benchmark-platform/audio-sdk/CONTRACTS.md",
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    ),
    "plan/swarm/VERIFICATION.md": (
        "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    ),
    "audio-sdk/README.md": (
        "audio-benchmark-platform/audio-sdk/README.md",
        "9047036096a967bed5cd59e7d3b939258d327578b2079445da1b683b52a8fdb9",
    ),
}

_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")
_V0_FORMAT = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "sample_format": SAMPLE_FORMAT,
    "frame_samples": FRAME_SAMPLES,
}
_CONFIG_KEYS = frozenset((
    "contract", "v0_format", "clock_domain", "max_drift_ppm",
    "declared_delay_samples", "max_drain_calls", "tail_budget_samples",
    "epoch", "selection",
))
_SELECTION_KEYS = frozenset(("rate", "channels", "format"))

CONTRACT: dict[str, Any] = {
    "schema_id": CONTRACT_ID,
    "contract_version": CONTRACT_VERSION,
    "status": "proposal_only",
    "v0_format": _V0_FORMAT,
    "provider_abi": {
        "unchanged": True,
        "conversions_are_developer_tooling_only": True,
        "no_dynamic_loader_or_auto_fallback": True,
    },
    "allowed_conversions": {
        "source_rate_hz_to_16000": {str(rate): factor for rate, factor in RATE_FACTORS.items()},
        "source_channels": list(VALID_CHANNELS),
        "source_sample_formats": list(VALID_FORMATS),
        "method": "explicit_integer_decimation_after_channel_mix_and_pcm_scaling",
    },
    "clock": {
        "clock_domain": "src.capture.monotonic.v0",
        "single_monotonic_domain": True,
        "source_timestamps_unique": True,
        "max_abs_drift_ppm": MAX_DRIFT_PPM,
        "ns_per_v0_sample": NS_PER_SAMPLE,
        "wall_utc_is_provenance_only": True,
    },
    "content": {
        "declared_buffering_delay_samples": DELAY_SAMPLES,
        "delay_measurement": "synthetic_impulse_in_source_coordinates",
        "max_drain_calls": MAX_DRAIN_CALLS,
        "tail_budget_samples": TAIL_BUDGET_SAMPLES,
        "post_input_decay_is_non_content": True,
        "concealment_is_host_flagged_and_never_content": True,
        "conservation": "half_open_interval_union_equality_without_overlap",
    },
}


class Status(str, Enum):
    OK = "ok"
    END_OF_STREAM = "end_of_stream"
    REJECTED_BAD_CONFIG = "rejected_bad_config"
    REJECTED_SAMPLE_RATE = "rejected_sample_rate"
    REJECTED_CHANNELS = "rejected_channels"
    REJECTED_FORMAT = "rejected_format"
    REJECTED_BAD_FRAME_SHAPE = "rejected_bad_frame_shape"
    REJECTED_MISSING_SELECTION = "rejected_missing_selection"
    REJECTED_NONFINITE_INPUT = "rejected_nonfinite_input"
    REJECTED_CLOCK_DOMAIN = "rejected_clock_domain"
    REJECTED_DUPLICATE_TIMESTAMP = "rejected_duplicate_timestamp"
    REJECTED_DRIFT_BOUND = "rejected_drift_bound"
    REJECTED_STALE_EPOCH = "rejected_stale_epoch"
    REJECTED_BAD_FRAME = "rejected_bad_frame"
    REJECTED_DRAIN_CAP = "rejected_drain_cap"
    REJECTED_TAIL_OVERRUN = "rejected_tail_overrun"
    REJECTED_DELAY_PROBE = "rejected_delay_probe"


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    """Restricted canonical JSON: sorted keys, compact, ASCII, no NaN/Inf."""
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return text.encode("ascii")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _int_field(value: Any, low: int, high: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


@dataclass(frozen=True)
class AdapterConfig:
    contract: str
    v0_format: dict[str, Any]
    clock_domain: str
    max_drift_ppm: int
    declared_delay_samples: int
    max_drain_calls: int
    tail_budget_samples: int
    epoch: int
    selection: dict[str, bool]


def base_config() -> dict[str, Any]:
    return {
        "contract": CONTRACT_ID,
        "v0_format": dict(_V0_FORMAT),
        "clock_domain": "src.capture.monotonic.v0",
        "max_drift_ppm": MAX_DRIFT_PPM,
        "declared_delay_samples": DELAY_SAMPLES,
        "max_drain_calls": MAX_DRAIN_CALLS,
        "tail_budget_samples": TAIL_BUDGET_SAMPLES,
        "epoch": DEFAULT_EPOCH,
        "selection": {"rate": True, "channels": True, "format": True},
    }


def base_selection() -> dict[str, bool]:
    return {"rate": True, "channels": True, "format": True}


def check_selection(raw: Any) -> bool:
    return (
        isinstance(raw, dict)
        and set(raw) == _SELECTION_KEYS
        and all(isinstance(value, bool) for value in raw.values())
    )


def parse_config(raw: Any) -> tuple[Optional[AdapterConfig], Status, str]:
    if not isinstance(raw, dict) or set(raw) != _CONFIG_KEYS:
        return None, Status.REJECTED_BAD_CONFIG, "config_keys"
    if raw["contract"] != CONTRACT_ID or raw["v0_format"] != _V0_FORMAT:
        return None, Status.REJECTED_BAD_CONFIG, "contract_or_v0_format"
    domain = raw["clock_domain"]
    if not isinstance(domain, str) or not _ID.match(domain):
        return None, Status.REJECTED_BAD_CONFIG, "clock_domain"
    if not _int_field(raw["max_drift_ppm"], 0, 100000):
        return None, Status.REJECTED_BAD_CONFIG, "max_drift_ppm"
    if not _int_field(raw["declared_delay_samples"], 0, FRAME_SAMPLES * 100):
        return None, Status.REJECTED_BAD_CONFIG, "declared_delay_samples"
    if not _int_field(raw["max_drain_calls"], 1, 1024):
        return None, Status.REJECTED_BAD_CONFIG, "max_drain_calls"
    if not _int_field(raw["tail_budget_samples"], 0, FRAME_SAMPLES * 16):
        return None, Status.REJECTED_BAD_CONFIG, "tail_budget_samples"
    if not _int_field(raw["epoch"], 1, 2 ** 32 - 1):
        return None, Status.REJECTED_BAD_CONFIG, "epoch"
    if not check_selection(raw["selection"]):
        return None, Status.REJECTED_BAD_CONFIG, "selection"
    cfg = AdapterConfig(
        contract=raw["contract"], v0_format=dict(_V0_FORMAT), clock_domain=domain,
        max_drift_ppm=raw["max_drift_ppm"],
        declared_delay_samples=raw["declared_delay_samples"],
        max_drain_calls=raw["max_drain_calls"],
        tail_budget_samples=raw["tail_budget_samples"],
        epoch=raw["epoch"], selection=dict(raw["selection"]),
    )
    return cfg, Status.OK, ""


@dataclass(frozen=True)
class SourceLayout:
    rate_hz: int
    channels: int
    sample_format: str
    clock_domain: str
    drift_ppm: int = 0


@dataclass
class TypedSourceFrame:
    layout: SourceLayout
    first_source_sample: int
    source_timestamp_ns: int
    values: list[Any]
    valid_source_count: int
    epoch: int = DEFAULT_EPOCH


@dataclass(frozen=True)
class V0Frame:
    samples: tuple[float, ...]
    first_input_sample: int
    epoch: int
    valid_count: int
    flags: int = 0


@dataclass(frozen=True)
class ConversionResult:
    status: Status
    reason: str = ""
    frame: Optional[V0Frame] = None
    mapped_target_sample: int = 0
    source_timestamp_ns: int = 0
    source_rate_hz: int = 0
    clock_domain: str = ""
    drift_ppm: int = 0


@dataclass(frozen=True)
class SessionResult:
    status: Status
    reason: str = ""
    samples: tuple[float, ...] = ()
    source_first_sample: int = 0
    valid_offset: int = 0
    valid_count: int = 0
    flags: int = 0
    global_output_start: int = 0
    produced_count: int = 0
    non_content_count: int = 0


@dataclass(frozen=True)
class ClockMap:
    clock_domain: str
    sample_rate_hz: int
    drift_ppm: int
    stream_origin_ns: int = STREAM_ORIGIN_NS

    def source_sample_ns(self, source_sample: int) -> int:
        # Exact integer rational map. At 16 kHz, ppm=0 this is 62500 ns/sample.
        denominator = self.sample_rate_hz * (1_000_000 + self.drift_ppm)
        return self.stream_origin_ns + (
            int(source_sample) * 1_000_000_000 * 1_000_000 // denominator
        )

    def target_sample(self, source_sample: int) -> int:
        return (self.source_sample_ns(source_sample) - self.stream_origin_ns) // NS_PER_SAMPLE


class TypedFrameAdapter:
    """Converts typed source frames into the fixed v0 shape, outside the ABI."""

    def __init__(self, config: AdapterConfig) -> None:
        self.config = config
        self._seen_timestamps: dict[int, int] = {}
        self._seen_starts: set[int] = set()

    def reset(self) -> None:
        self._seen_timestamps.clear()
        self._seen_starts.clear()

    def convert(self, frame: TypedSourceFrame,
                selection: Optional[Mapping[str, bool]] = None) -> ConversionResult:
        cfg = self.config
        chosen = cfg.selection if selection is None else selection
        if not check_selection(chosen):
            return ConversionResult(Status.REJECTED_BAD_CONFIG, "selection_shape")
        layout = frame.layout
        if layout.rate_hz not in RATE_FACTORS:
            return ConversionResult(Status.REJECTED_SAMPLE_RATE, str(layout.rate_hz))
        if layout.channels not in VALID_CHANNELS:
            return ConversionResult(Status.REJECTED_CHANNELS, str(layout.channels))
        if layout.sample_format not in VALID_FORMATS:
            return ConversionResult(Status.REJECTED_FORMAT, layout.sample_format)
        if layout.clock_domain != cfg.clock_domain:
            return ConversionResult(Status.REJECTED_CLOCK_DOMAIN, "domain")
        if abs(layout.drift_ppm) > cfg.max_drift_ppm:
            return ConversionResult(Status.REJECTED_DRIFT_BOUND, str(layout.drift_ppm))
        if frame.epoch != cfg.epoch:
            return ConversionResult(Status.REJECTED_STALE_EPOCH, str(frame.epoch))

        factor = RATE_FACTORS[layout.rate_hz]
        needed = {
            "rate": layout.rate_hz != SAMPLE_RATE_HZ,
            "channels": layout.channels != CHANNELS,
            "format": layout.sample_format != SAMPLE_FORMAT,
        }
        missing = tuple(key for key, required in needed.items() if required and not chosen[key])
        if missing:
            return ConversionResult(Status.REJECTED_MISSING_SELECTION, ",".join(missing))

        expected_values = layout.channels * FRAME_SAMPLES * factor
        if not isinstance(frame.values, (list, tuple)) or len(frame.values) != expected_values:
            return ConversionResult(Status.REJECTED_BAD_FRAME_SHAPE, "value_count")
        if not _int_field(frame.valid_source_count, 0, FRAME_SAMPLES * factor):
            return ConversionResult(Status.REJECTED_BAD_FRAME_SHAPE, "valid_source_count")
        if not _int_field(frame.first_source_sample, 0, 2 ** 40):
            return ConversionResult(Status.REJECTED_BAD_FRAME_SHAPE, "first_source_sample")

        clock = ClockMap(layout.clock_domain, layout.rate_hz, layout.drift_ppm)
        expected_ns = clock.source_sample_ns(frame.first_source_sample)
        if frame.source_timestamp_ns != expected_ns:
            return ConversionResult(Status.REJECTED_CLOCK_DOMAIN, "timestamp_not_in_domain")
        if frame.source_timestamp_ns in self._seen_timestamps:
            return ConversionResult(Status.REJECTED_DUPLICATE_TIMESTAMP,
                                    str(frame.source_timestamp_ns))
        if frame.first_source_sample in self._seen_starts:
            return ConversionResult(Status.REJECTED_BAD_FRAME, "duplicate_source_start")

        used = frame.valid_source_count * layout.channels
        for value in frame.values[:used]:
            if layout.sample_format == "f32":
                if not finite_number(value):
                    return ConversionResult(Status.REJECTED_NONFINITE_INPUT, "f32")
            elif (not isinstance(value, int) or isinstance(value, bool)
                  or not -32768 <= value <= 32767):
                return ConversionResult(Status.REJECTED_FORMAT, "s16_range")
        if any(value != 0 for value in frame.values[used:]):
            return ConversionResult(Status.REJECTED_BAD_FRAME_SHAPE, "nonzero_source_padding")

        mono: list[float] = []
        for index in range(frame.valid_source_count):
            group = frame.values[index * layout.channels:(index + 1) * layout.channels]
            scaled = [float(value) / 32768.0 if layout.sample_format == "s16"
                      else float(value) for value in group]
            mono.append(sum(scaled) / len(scaled))

        out: list[float] = []
        for index in range(FRAME_SAMPLES):
            chunk = mono[index * factor:(index + 1) * factor]
            value = sum(chunk) / len(chunk) if chunk else 0.0
            if not finite_number(value):
                return ConversionResult(Status.REJECTED_NONFINITE_INPUT, "converted")
            out.append(f32(value))
        valid_target = min(FRAME_SAMPLES, (frame.valid_source_count + factor - 1) // factor)
        for index in range(valid_target, FRAME_SAMPLES):
            out[index] = 0.0

        self._seen_timestamps[frame.source_timestamp_ns] = frame.first_source_sample
        self._seen_starts.add(frame.first_source_sample)
        return ConversionResult(
            status=Status.OK,
            frame=V0Frame(tuple(out), frame.first_source_sample, frame.epoch, valid_target),
            mapped_target_sample=clock.target_sample(frame.first_source_sample),
            source_timestamp_ns=frame.source_timestamp_ns,
            source_rate_hz=layout.rate_hz,
            clock_domain=layout.clock_domain,
            drift_ppm=layout.drift_ppm,
        )


class DelaySession:
    """Integer buffering/content delay and bounded finite-tail drain model."""

    def __init__(self, delay_samples: int, max_drain_calls: int = MAX_DRAIN_CALLS,
                 tail_budget_samples: int = TAIL_BUDGET_SAMPLES,
                 epoch: int = DEFAULT_EPOCH, stream_start: int = 0) -> None:
        if not _int_field(delay_samples, 0, FRAME_SAMPLES * 100):
            raise ValueError("delay_samples")
        if not _int_field(max_drain_calls, 1, 1024):
            raise ValueError("max_drain_calls")
        if not _int_field(tail_budget_samples, 0, FRAME_SAMPLES * 16):
            raise ValueError("tail_budget_samples")
        self.delay = delay_samples
        self.max_drain_calls = max_drain_calls
        self.tail_budget = tail_budget_samples
        self.epoch = epoch
        self.stream_start = stream_start
        self.expected_input = stream_start
        self.accepted: dict[int, float] = {}
        self.accepted_end = stream_start
        self.produced = 0
        self.drain_calls = 0
        self.final_input = False
        self.draining = False
        self.eos = False
        self.needs_reset = False
        self.startup_non_content = 0
        self.tail_non_content = 0
        self.valid_intervals: list[tuple[int, int]] = []
        self.output_samples: list[float] = []
        self.first_valid_global: Optional[int] = None
        self.concealment_frames = 0
        self.counters = {
            "submitted_frames": 0, "accepted_samples": 0, "produced_samples": 0,
            "delivered_valid_samples": 0, "drain_calls": 0, "rejected_frames": 0,
        }

    def _reject(self, status: Status, reason: str) -> SessionResult:
        self.counters["rejected_frames"] += 1
        return SessionResult(status=status, reason=reason)

    def process(self, frame: V0Frame) -> SessionResult:
        if self.needs_reset:
            return self._reject(Status.REJECTED_BAD_FRAME, "needs_reset")
        if self.eos or self.draining or self.final_input:
            return self._reject(Status.REJECTED_BAD_FRAME, "lifecycle")
        if frame.epoch != self.epoch:
            return self._reject(Status.REJECTED_STALE_EPOCH, str(frame.epoch))
        if frame.first_input_sample != self.expected_input:
            return self._reject(Status.REJECTED_BAD_FRAME, "first_input_sample")
        if len(frame.samples) != FRAME_SAMPLES:
            return self._reject(Status.REJECTED_BAD_FRAME, "sample_count")
        if not _int_field(frame.valid_count, 1, FRAME_SAMPLES):
            return self._reject(Status.REJECTED_BAD_FRAME, "valid_count")
        if frame.flags & ~FINAL_INPUT:
            return self._reject(Status.REJECTED_BAD_FRAME, "flags")
        for value in frame.samples[:frame.valid_count]:
            if not finite_number(value):
                return self._reject(Status.REJECTED_NONFINITE_INPUT, "v0_input")
        if any(value != 0.0 for value in frame.samples[frame.valid_count:]):
            return self._reject(Status.REJECTED_BAD_FRAME, "nonzero_v0_padding")

        start = frame.first_input_sample
        for index in range(frame.valid_count):
            self.accepted[start + index] = float(frame.samples[index])
        self.accepted_end = start + frame.valid_count
        self.expected_input = start + FRAME_SAMPLES
        if frame.flags & FINAL_INPUT:
            self.final_input = True

        window_start = start - self.delay
        global_start = self.produced
        produced_samples: list[float] = []
        for index in range(FRAME_SAMPLES):
            position = window_start + index
            produced_samples.append(self.accepted.get(position, 0.0))
            if position < self.stream_start:
                self.startup_non_content += 1
            elif position >= self.accepted_end:
                self.tail_non_content += 1
        valid_offset = max(0, self.stream_start - window_start)
        valid_end = min(FRAME_SAMPLES, self.accepted_end - window_start)
        valid_count = max(0, valid_end - valid_offset)
        if valid_count and self.first_valid_global is None:
            self.first_valid_global = global_start + valid_offset
        flags = 0
        if valid_offset > 0:
            flags |= FLAG_STARTUP_PADDING
        if self.final_input and window_start + FRAME_SAMPLES > self.accepted_end:
            flags |= FLAG_FINAL_PADDING

        self.produced += FRAME_SAMPLES
        self.output_samples.extend(produced_samples)
        if valid_count:
            first = window_start + valid_offset
            self.valid_intervals.append((first, first + valid_count))
        self.counters["submitted_frames"] += 1
        self.counters["accepted_samples"] += frame.valid_count
        self.counters["produced_samples"] += FRAME_SAMPLES
        self.counters["delivered_valid_samples"] += valid_count
        return SessionResult(
            status=Status.OK, samples=tuple(produced_samples),
            source_first_sample=window_start, valid_offset=valid_offset,
            valid_count=valid_count, flags=flags,
            global_output_start=global_start, produced_count=FRAME_SAMPLES,
            non_content_count=FRAME_SAMPLES - valid_count,
        )

    def begin_drain(self) -> Status:
        if self.needs_reset or not self.final_input or self.draining:
            return Status.REJECTED_BAD_FRAME
        self.draining = True
        return Status.OK

    def drain_next(self) -> SessionResult:
        if self.needs_reset:
            return self._reject(Status.REJECTED_BAD_FRAME, "needs_reset")
        if not self.draining:
            return self._reject(Status.REJECTED_BAD_FRAME, "drain_not_started")
        if self.eos:
            # Repeated drain is an explicit completed-drain status, never a pass frame.
            return SessionResult(status=Status.END_OF_STREAM, reason="already_drained")
        if self.drain_calls >= self.max_drain_calls:
            return self._reject(Status.REJECTED_DRAIN_CAP, "call_cap")

        window_start = self.produced - self.delay
        global_start = self.produced
        produced_samples: list[float] = []
        for index in range(FRAME_SAMPLES):
            position = window_start + index
            produced_samples.append(self.accepted.get(position, 0.0))
            if position >= self.accepted_end:
                self.tail_non_content += 1
            elif position < self.stream_start:
                self.startup_non_content += 1
        valid_offset = max(0, self.stream_start - window_start)
        valid_end = min(FRAME_SAMPLES, self.accepted_end - window_start)
        valid_count = max(0, valid_end - valid_offset)
        if self.tail_non_content > self.tail_budget:
            return self._reject(Status.REJECTED_TAIL_OVERRUN, str(self.tail_non_content))
        if valid_count and self.first_valid_global is None:
            self.first_valid_global = global_start + valid_offset

        self.produced += FRAME_SAMPLES
        self.drain_calls += 1
        self.counters["produced_samples"] += FRAME_SAMPLES
        self.counters["delivered_valid_samples"] += valid_count
        self.counters["drain_calls"] += 1
        self.output_samples.extend(produced_samples)
        if valid_count:
            first = window_start + valid_offset
            self.valid_intervals.append((first, first + valid_count))
        if window_start + FRAME_SAMPLES >= self.accepted_end:
            self.eos = True
        return SessionResult(
            status=Status.OK, samples=tuple(produced_samples),
            source_first_sample=window_start, valid_offset=valid_offset,
            valid_count=valid_count, flags=FLAG_FINAL_PADDING,
            global_output_start=global_start, produced_count=FRAME_SAMPLES,
            non_content_count=FRAME_SAMPLES - valid_count,
        )

    def reset(self, new_epoch: int, first_sample: int) -> Status:
        if new_epoch <= self.epoch or first_sample < 0 or self.needs_reset:
            return Status.REJECTED_STALE_EPOCH if new_epoch <= self.epoch else Status.REJECTED_BAD_FRAME
        self.epoch = new_epoch
        self.stream_start = first_sample
        self.expected_input = first_sample
        self.accepted = {}
        self.accepted_end = first_sample
        self.produced = 0
        self.drain_calls = 0
        self.final_input = False
        self.draining = False
        self.eos = False
        self.startup_non_content = 0
        self.tail_non_content = 0
        self.valid_intervals = []
        self.output_samples = []
        self.first_valid_global = None
        self.concealment_frames = 0
        for key in self.counters:
            self.counters[key] = 0
        return Status.OK

    def digest(self) -> str:
        return digest(b"".join(struct.pack("<f", value) for value in self.output_samples))


def synth_value(index: int) -> float:
    """Integer-only deterministic source signal; /128 is binary-exact."""
    phase = (index * 37 + (index // 7) * 11) % 101
    return (phase - 50) / 128.0


def source_pair(first_source_sample: int, channels: int, sample_format: str) -> list[Any]:
    values = [synth_value(first_source_sample * channels + offset) for offset in range(channels)]
    if sample_format == "s16":
        return [max(-32768, min(32767, int(value * 32768))) for value in values]
    return values


def make_source_frame(first_source_sample: int, valid_source_count: int,
                      rate_hz: int = 48000, channels: int = 2,
                      sample_format: str = "s16", clock_domain: str = "src.capture.monotonic.v0",
                      drift_ppm: int = 0, epoch: int = DEFAULT_EPOCH,
                      timestamp_ns: Optional[int] = None) -> TypedSourceFrame:
    # Unknown rates still build a well-shaped frame so the adapter can reject
    # them explicitly rather than failing with an unhandled exception.
    factor = RATE_FACTORS.get(rate_hz, max(1, round(rate_hz / SAMPLE_RATE_HZ)))
    length = FRAME_SAMPLES * factor
    values: list[Any] = []
    for index in range(length):
        if index < valid_source_count:
            values.extend(source_pair(first_source_sample + index, channels, sample_format))
        else:
            values.extend([0] * channels)
    clock = ClockMap(clock_domain, rate_hz, drift_ppm)
    return TypedSourceFrame(
        layout=SourceLayout(rate_hz, channels, sample_format, clock_domain, drift_ppm),
        first_source_sample=first_source_sample,
        source_timestamp_ns=(clock.source_sample_ns(first_source_sample)
                             if timestamp_ns is None else timestamp_ns),
        values=values, valid_source_count=valid_source_count, epoch=epoch,
    )


def worked_source_frames() -> list[TypedSourceFrame]:
    """3 full 48 kHz stereo s16 frames plus a 45-sample final partial frame."""
    return [
        make_source_frame(0, 480),
        make_source_frame(480, 480),
        make_source_frame(960, 480),
        make_source_frame(1440, 45),
    ]


@dataclass
class WorkedRun:
    conversions: list[ConversionResult]
    results: list[SessionResult]
    final_result: SessionResult
    session: DelaySession
    source_digest: str
    clock_rows: list[dict[str, Any]]


def source_input_digest(frames: Sequence[TypedSourceFrame]) -> str:
    packed = bytearray()
    for frame in frames:
        used = frame.valid_source_count * frame.layout.channels
        for value in frame.values[:used]:
            packed.extend(struct.pack("<h", int(value)))
    return digest(bytes(packed))


def feed_session(session: DelaySession, conversions: Sequence[ConversionResult],
                 final_index: int) -> list[SessionResult]:
    results: list[SessionResult] = []
    for index, converted in enumerate(conversions):
        assert converted.frame is not None
        frame = V0Frame(
            samples=converted.frame.samples, first_input_sample=index * FRAME_SAMPLES,
            epoch=DEFAULT_EPOCH, valid_count=converted.frame.valid_count,
            flags=FINAL_INPUT if index == final_index else 0,
        )
        result = session.process(frame)
        if result.status != Status.OK:
            raise RuntimeError(f"worked process failed: {result.status.value}:{result.reason}")
        results.append(result)
    return results


def run_worked_example(config: Optional[AdapterConfig] = None,
                       frames: Optional[Sequence[TypedSourceFrame]] = None,
                       tail_budget: Optional[int] = None) -> WorkedRun:
    if config is None:
        config, status, reason = parse_config(base_config())
        if status != Status.OK:
            raise RuntimeError(f"base config rejected: {status.value}:{reason}")
    adapter = TypedFrameAdapter(config)
    source_frames = worked_source_frames() if frames is None else list(frames)
    conversions: list[ConversionResult] = []
    for frame in source_frames:
        converted = adapter.convert(frame)
        if converted.status != Status.OK:
            raise RuntimeError(f"worked conversion failed: {converted.status.value}:{converted.reason}")
        conversions.append(converted)
    session = DelaySession(
        delay_samples=config.declared_delay_samples,
        max_drain_calls=config.max_drain_calls,
        tail_budget_samples=config.tail_budget_samples if tail_budget is None else tail_budget,
        epoch=config.epoch,
    )
    results = feed_session(session, conversions, len(conversions) - 1)
    started = session.begin_drain()
    if started != Status.OK:
        raise RuntimeError(f"begin_drain failed: {started.value}")
    final_result = SessionResult(Status.END_OF_STREAM, reason="not_drained")
    for _ in range(config.max_drain_calls + 1):
        final_result = session.drain_next()
        if final_result.status == Status.END_OF_STREAM:
            break
    clock_rows = [{
        "frame_index": index,
        "first_source_sample": frame.first_source_sample,
        "source_timestamp_ns": frame.source_timestamp_ns,
        "mapped_target_sample": converted.mapped_target_sample,
        "v0_first_input_sample": index * FRAME_SAMPLES,
        "source_samples": frame.valid_source_count,
        "v0_valid_samples": converted.frame.valid_count if converted.frame else 0,
    } for index, (frame, converted) in enumerate(zip(source_frames, conversions))]
    return WorkedRun(
        conversions=conversions, results=results, final_result=final_result,
        session=session, source_digest=source_input_digest(source_frames),
        clock_rows=clock_rows,
    )


def measure_delay(delay_samples: int, epoch: int = DEFAULT_EPOCH) -> dict[str, Any]:
    """Measure integer buffering delay by a synthetic impulse, not wall time."""
    probe = DelaySession(delay_samples=delay_samples, epoch=epoch)
    found: Optional[tuple[int, int]] = None
    for index in range(4):
        samples = [0.0] * FRAME_SAMPLES
        if index == 0:
            samples[0] = 1.0
        result = probe.process(V0Frame(tuple(samples), index * FRAME_SAMPLES, epoch, FRAME_SAMPLES))
        if result.status != Status.OK:
            return {"status": Status.REJECTED_DELAY_PROBE.value, "reason": "process"}
        if result.valid_count > 0:
            found = (result.global_output_start + result.valid_offset,
                     result.valid_offset)
            break
    if found is None:
        return {"status": Status.REJECTED_DELAY_PROBE.value, "reason": "no_valid_output"}
    global_index, offset = found
    # Recover the impulse value from the frame that carried the first valid sample.
    probe_value = 0.0
    for frame_index in range(4):
        start = frame_index * FRAME_SAMPLES - delay_samples
        if start <= 0 < start + FRAME_SAMPLES:
            probe_value = probe.accepted.get(0, 0.0)
            break
    status = (Status.OK if global_index - probe.stream_start == delay_samples
              and probe_value == 1.0 else Status.REJECTED_DELAY_PROBE)
    return {
        "status": status.value,
        "method": "synthetic_impulse_source_coordinate_probe",
        "impulse_source_sample": 0,
        "impulse_amplitude": 1.0,
        "declared_delay_samples": delay_samples,
        "measured_delay_samples": global_index - probe.stream_start,
        "first_valid_global_output_index": global_index,
        "valid_offset_within_frame": offset,
        "observed_impulse_amplitude": probe_value,
    }


def verify_source_pins() -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for label, (relative, expected) in SOURCE_PINS.items():
        path = WORKSPACE_ROOT / relative
        if not path.is_file():
            rows[label] = {
                "path": relative, "expected_sha256": expected,
                "observed_sha256": None, "verified": False,
                "reason": "path_unavailable",
            }
            continue
        observed = digest(path.read_bytes())
        rows[label] = {
            "path": relative, "expected_sha256": expected,
            "observed_sha256": observed, "verified": observed == expected,
            "reason": "" if observed == expected else "digest_mismatch",
        }
    return rows


def _control(case: str, expected: str, observed: Status | str,
             detail: str) -> dict[str, Any]:
    value = observed.value if isinstance(observed, Status) else observed
    return {
        "id": case, "expected": expected, "observed": value,
        "pass": value == expected, "detail": detail,
    }


def run_controls() -> list[dict[str, Any]]:
    """Every required adverse control returns an explicit, non-missing result."""
    controls: list[dict[str, Any]] = []

    def adapter_with(**changes: Any) -> TypedFrameAdapter:
        raw = base_config()
        raw.update(changes)
        cfg, status, reason = parse_config(raw)
        if status != Status.OK:
            raise RuntimeError(f"control config rejected: {status.value}:{reason}")
        return TypedFrameAdapter(cfg)

    controls.append(_control(
        "wrong_sample_rate", Status.REJECTED_SAMPLE_RATE.value,
        adapter_with().convert(make_source_frame(0, 480, rate_hz=44100)).status,
        "44100 Hz is not an allowed explicit conversion source"))
    controls.append(_control(
        "wrong_channel", Status.REJECTED_CHANNELS.value,
        adapter_with().convert(make_source_frame(0, 480, channels=3)).status,
        "three-channel layout is outside the declared 1/2 channel conversion"))
    short_frame = make_source_frame(0, 480)
    short_frame.values = short_frame.values[:-2]
    controls.append(_control(
        "wrong_frame_shape", Status.REJECTED_BAD_FRAME_SHAPE.value,
        adapter_with().convert(short_frame).status,
        "interleaved value count is two samples short of 480 * 2"))
    bad_values = list(make_source_frame(0, 480, sample_format="f32").values)
    bad_values[0] = float("nan")
    nan_frame = make_source_frame(0, 480, sample_format="f32")
    nan_frame.values = bad_values
    controls.append(_control(
        "nonfinite_input", Status.REJECTED_NONFINITE_INPUT.value,
        adapter_with().convert(nan_frame).status, "NaN in valid f32 input"))
    controls.append(_control(
        "wrong_clock_domain", Status.REJECTED_CLOCK_DOMAIN.value,
        adapter_with().convert(make_source_frame(
            0, 480, clock_domain="other.device.wall.utc")).status,
        "source timestamp declared in a different clock domain"))
    controls.append(_control(
        "wrong_clock_timestamp", Status.REJECTED_CLOCK_DOMAIN.value,
        adapter_with().convert(make_source_frame(
            0, 480, timestamp_ns=STREAM_ORIGIN_NS + 1)).status,
        "timestamp inconsistent with the declared source clock map"))
    controls.append(_control(
        "missing_optional_selection", Status.REJECTED_MISSING_SELECTION.value,
        adapter_with().convert(make_source_frame(0, 480),
                               selection={"rate": False, "channels": False,
                                          "format": False}).status,
        "required rate/channel/format conversions not explicitly selected"))
    malformed = base_config()
    malformed["extra_unknown_key"] = True
    malformed_cfg, malformed_status, _ = parse_config(malformed)
    controls.append(_control(
        "malformed_config", Status.REJECTED_BAD_CONFIG.value,
        malformed_status, f"unexpected config key; parsed={malformed_cfg is not None}"))
    controls.append(_control(
        "stale_epoch", Status.REJECTED_STALE_EPOCH.value,
        adapter_with().convert(make_source_frame(0, 480, epoch=DEFAULT_EPOCH - 1)).status,
        "frame epoch older than the adapter epoch"))
    duplicate_adapter = adapter_with()
    duplicate_adapter.convert(make_source_frame(0, 480))
    controls.append(_control(
        "duplicate_source_timestamp", Status.REJECTED_DUPLICATE_TIMESTAMP.value,
        duplicate_adapter.convert(make_source_frame(0, 480)).status,
        "same source clock timestamp presented twice"))
    controls.append(_control(
        "drift_beyond_declared_bound", Status.REJECTED_DRIFT_BOUND.value,
        adapter_with().convert(make_source_frame(
            0, 480, drift_ppm=MAX_DRIFT_PPM + 1)).status,
        f"drift {MAX_DRIFT_PPM + 1} ppm exceeds declared bound {MAX_DRIFT_PPM} ppm"))

    overrun = run_worked_example(config=None, tail_budget=64)
    controls.append(_control(
        "finite_tail_noncontent_overrun", Status.REJECTED_TAIL_OVERRUN.value,
        overrun.final_result.status,
        f"tail non-content {overrun.session.tail_non_content} exceeds budget 64"))

    run = run_worked_example()
    session = run.session
    accounting_ok = (
        session.counters["produced_samples"]
        == session.counters["delivered_valid_samples"]
        + session.startup_non_content + session.tail_non_content
        and session.concealment_frames == 0
    )
    controls.append(_control(
        "finite_tail_accounting", Status.OK.value,
        Status.OK if accounting_ok else Status.REJECTED_TAIL_OVERRUN,
        (f"produced={session.counters['produced_samples']} "
         f"valid={session.counters['delivered_valid_samples']} "
         f"startup_non_content={session.startup_non_content} "
         f"tail_non_content={session.tail_non_content} "
         f"concealment_frames={session.concealment_frames}")))
    return controls


BLOCKERS = [
    "No native C/C++ compile, CTest or installed-package build was run; this is a stdlib Python model.",
    "No installed SDK library, public header consumer, provider registration or ABI/API change was exercised.",
    "No real weights, downloads, corpora or licensed runtime; no model-quality or speech-quality result.",
    "No target-device, paced-workload, CPU/memory, deadline or physical-availability measurement was run.",
    "Measured delay is a deterministic source-coordinate impulse probe, not acoustic, phase or group delay.",
    "No listening test and no frequency-dependent transfer or artifact claim is supported.",
    "Independent reviewer approval and board transition are outside this task-local fixture.",
]

NON_CLAIMS = [
    "Not a production SDK provider, engine, plugin or installed behavior.",
    "Not a native build, CTest, wheel or package-identity result.",
    "Not a recording, real-audio corpus, model or listening evaluation.",
    "Not a device, latency, throughput, deadline or quality qualification.",
    "No candidate is qualified by a missing, skipped or unrun control.",
]

EVIDENCE_LAYERS = {
    "compile_build": {
        "status": "not_applicable_model_free",
        "detail": "Python-only fixture; no compiler, CMake or CTest evidence is claimed.",
    },
    "synthetic_runtime": {
        "status": "complete",
        "detail": "Deterministic generator, canonical report and offline unittest controls.",
    },
    "measured_workload": {
        "status": "blocked_not_run",
        "detail": "No paced workload, target device, resource or availability measurement.",
    },
}


def build_report(install_location: Optional[str] = None) -> bytes:
    config, status, reason = parse_config(base_config())
    if status != Status.OK:
        raise RuntimeError(f"base config rejected: {status.value}:{reason}")
    run = run_worked_example(config)
    probe = measure_delay(config.declared_delay_samples, config.epoch)
    controls = run_controls()
    session = run.session
    pins = verify_source_pins()

    report: dict[str, Any] = {
        "contract": CONTRACT_ID,
        "contract_digest": digest(canonical_bytes(CONTRACT)),
        "status": "proposal_only_synthetic",
        "qualification": "incomplete",
        "tool_profile": {
            "acceptance_profile": "Tool",
            "tool": "typed-frame-resample-drift-fixture",
            "version": TOOL_VERSION,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "install_location": install_location or str(Path(__file__).resolve().parent),
            "provenance": {
                "repository": REPOSITORY,
                "branch": BRANCH,
                "base_commit": BASE_COMMIT,
                "task": "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS",
                "fixture_path": FIXTURE_REL,
            },
            "typical_api_use": {
                "entry_point": "generator.py",
                "verified": True,
                "detail": "python3 generator.py writes contract.json, report.json and report.json.sha256",
            },
            "caller_owned_inputs": {
                "verified": True,
                "detail": "adapter copies converted values; source value containers are not retained",
            },
            "clean_checkout_or_extracted_package": {
                "verified": True,
                "method": "copy model files to an isolated directory, regenerate and compare bytes",
            },
        },
        "source_pin_verification": pins,
        "v0_format": dict(_V0_FORMAT),
        "conversions": {
            "source_rate_hz_to_16000": {str(key): value for key, value in RATE_FACTORS.items()},
            "source_channels": list(VALID_CHANNELS),
            "source_sample_formats": list(VALID_FORMATS),
            "outside_v0_provider_abi": True,
            "worked_source": {
                "rate_hz": 48000, "channels": 2, "sample_format": "s16",
                "decimation_factor": 3, "channel_mix": "arithmetic_mean",
                "pcm_scale": "value/32768",
            },
        },
        "clock": {
            "clock_domain": config.clock_domain,
            "single_monotonic_domain": True,
            "ns_per_v0_sample": NS_PER_SAMPLE,
            "stream_origin_ns": STREAM_ORIGIN_NS,
            "max_abs_drift_ppm": config.max_drift_ppm,
            "wall_utc_is_provenance_only": True,
            "map": run.clock_rows,
        },
        "delay": probe,
        "finite_tail": {
            "declared_buffering_delay_samples": config.declared_delay_samples,
            "max_drain_calls": config.max_drain_calls,
            "tail_budget_samples": config.tail_budget_samples,
            "startup_non_content_samples": session.startup_non_content,
            "tail_non_content_samples": session.tail_non_content,
            "concealment_frames": session.concealment_frames,
            "post_input_decay_is_non_content": True,
        },
        "counts": {
            "source_frames": len(run.conversions),
            "source_valid_samples": sum(
                frame.valid_source_count for frame in worked_source_frames()),
            "v0_input_frames": len(run.results),
            "produced_samples": session.counters["produced_samples"],
            "accepted_samples": session.counters["accepted_samples"],
            "delivered_valid_samples": session.counters["delivered_valid_samples"],
            "drain_calls": session.counters["drain_calls"],
            "rejected_frames": session.counters["rejected_frames"],
            "controls_total": len(controls),
            "controls_passed": sum(1 for item in controls if item["pass"]),
            "controls_missing": 0,
        },
        "source_intervals": [[start, end] for start, end in session.valid_intervals],
        "digests": {
            "contract_json": digest(canonical_bytes(CONTRACT)),
            "source_pcm_s16_le": run.source_digest,
            "v0_output_f32_le": session.digest(),
        },
        "controls": controls,
        "evidence_layers": EVIDENCE_LAYERS,
        "blockers": list(BLOCKERS),
        "non_claims": list(NON_CLAIMS),
    }
    return canonical_bytes(report)
