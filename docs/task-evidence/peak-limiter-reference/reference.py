"""Deterministic float32 model of the pinned limiter stage.

Developer-only reference. No SDK ABI, descriptor, registry or default provider
is changed by this module. The arithmetic mirrors the documented behavior of
cpp-library/src/stages/limiter.cpp at SHA-256
fc4bb899f81e87466b3ad1aafea28ae392fed5ca10f4ea99bfde56f313079ac3, including
its copy fast path, double gain state, one-pole release, per-sample clamp and
C++ std::min/std::max ordering for nonfinite values.
"""

import hashlib
import math
import struct

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
DEFAULT_CEILING = 0.98
DEFAULT_RELEASE_MS = 50.0
ENGAGED_THRESHOLD = 0.999999
_F32 = struct.Struct("<f")


class ControlError(ValueError):
    """Raised for a rejected reference control."""


def f32(value):
    """Round a Python double to IEEE-754 binary32, matching the C++ cast."""
    return _F32.unpack(_F32.pack(float(value)))[0]


def f32_bytes(samples):
    return b"".join(_F32.pack(value) for value in samples)


def cpp_min(left, right):
    """C++ std::min(left, right): right < left ? right : left."""
    return right if right < left else left


def cpp_max(left, right):
    """C++ std::max(left, right): left < right ? right : left."""
    return right if left < right else left


def smoothing_coefficient(release_ms, sample_rate):
    if not (release_ms > 0.0) or not (sample_rate > 0.0):
        return 1.0
    return 1.0 - math.exp(-1000.0 / (release_ms * sample_rate))


def validate_controls(config):
    """Fail-closed control check for the opt-in adapter boundary.

    The pinned source defaults absent settings; this boundary deliberately
    requires both controls so a missing value cannot silently select a default.
    """
    if not isinstance(config, dict):
        raise ControlError("config_not_object")
    allowed = {"ceiling", "release_ms"}
    unknown = sorted(set(config) - allowed)
    if unknown:
        raise ControlError("unknown_control:" + ",".join(unknown))
    missing = sorted(allowed - set(config))
    if missing:
        raise ControlError("missing_control:" + ",".join(missing))
    for name in ("ceiling", "release_ms"):
        value = config[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ControlError("nonnumeric_control:" + name)
        if not math.isfinite(value):
            raise ControlError("nonfinite_control:" + name)
    ceiling = float(config["ceiling"])
    release_ms = float(config["release_ms"])
    if not (ceiling > 0.0) or ceiling > 1.0:
        raise ControlError("ceiling_out_of_range")
    if not (release_ms > 0.0) or release_ms > 5000.0:
        raise ControlError("release_out_of_range")
    return {"ceiling": ceiling, "release_ms": release_ms}


class PeakLimiterReference:
    """Frame-stateful reference; process() consumes exactly one fixed frame."""

    def __init__(self, ceiling=DEFAULT_CEILING, release_ms=DEFAULT_RELEASE_MS,
                 sample_rate=SAMPLE_RATE_HZ):
        self.ceiling = float(ceiling)
        self.release_ms = float(release_ms)
        self.sample_rate = int(sample_rate)
        self.release_coefficient = smoothing_coefficient(self.release_ms, self.sample_rate)
        self.gain = 1.0
        self.reset_count = 0

    def reset(self):
        self.gain = 1.0
        self.reset_count += 1

    def process(self, samples, gain_trace=None):
        count = len(samples)
        if count != FRAME_SAMPLES:
            raise ValueError("frame_samples_mismatch")
        if self.gain == 1.0:
            finite = True
            needs_limit = False
            for value in samples:
                value = float(value)
                finite = finite and math.isfinite(value)
                needs_limit = needs_limit or abs(value) > self.ceiling
            if finite and not needs_limit:
                output = [f32(value) for value in samples]
                if gain_trace is not None:
                    gain_trace.extend([self.gain] * count)
                return {"samples": output, "engaged": False, "gain": self.gain,
                        "fast_path": True}
        engaged = False
        output = []
        for value in samples:
            sample = float(value)
            peak = abs(sample)
            target = 1.0
            if peak > self.ceiling:
                target = self.ceiling / peak
                engaged = True
            if target < self.gain:
                self.gain = target
            else:
                self.gain += self.release_coefficient * (target - self.gain)
            limited = sample * self.gain
            output.append(f32(cpp_max(-self.ceiling, cpp_min(self.ceiling, limited))))
            if gain_trace is not None:
                gain_trace.append(self.gain)
        if self.gain < ENGAGED_THRESHOLD:
            engaged = True
        return {"samples": output, "engaged": engaged, "gain": self.gain,
                "fast_path": False}


def hard_clip(samples, ceiling):
    return [f32(cpp_max(-ceiling, cpp_min(ceiling, float(value)))) for value in samples]


def process_sequence(limiter, samples, reset_at=()):
    """Process a multiple-of-160 sequence; reset_at holds frame indices."""
    if len(samples) % FRAME_SAMPLES:
        raise ValueError("sequence_not_frame_aligned")
    frames = []
    output = []
    for index in range(len(samples) // FRAME_SAMPLES):
        if index in reset_at:
            limiter.reset()
        begin = index * FRAME_SAMPLES
        frame = limiter.process(samples[begin:begin + FRAME_SAMPLES])
        output.extend(frame["samples"])
        frames.append({"index": index, "engaged": frame["engaged"],
                       "gain": frame["gain"], "fast_path": frame["fast_path"]})
    return {"samples": output, "frames": frames, "gain": limiter.gain,
            "reset_count": limiter.reset_count}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest_samples(samples):
    return sha256_bytes(f32_bytes(samples))
