"""Deterministic stdlib reference for the static-target-gain DSP fixture.

Developer-only and task-local. The controller re-expresses the pinned offline
baseline at ``src/audioml_eval/level_tone.py`` (sha256 a0ec2e3b...): measure
input RMS, derive a gain toward a target dBFS level, bound that gain, apply one
static scale factor and clamp the result with a hard peak ceiling. A required
silence floor bypasses whole segments that are already at or below the floor;
no per-sample adaptation, attack/release or lookahead is used.

Nothing in this module changes the public SDK ABI, header, descriptor,
registry, default provider or installed v0 behaviour. Fixed v0 remains
16 kHz, mono, float32, 160 samples per frame.
"""

import hashlib
import math
import struct

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
CHANNELS = 1
RMS_FLOOR_LINEAR = 1e-8
CONTROL_NAMES = ("identity", "static_target_gain_reference", "fixed_gain_reference")

_F32 = struct.Struct("<f")


class ControlError(ValueError):
    """Raised for a rejected reference control."""


def f32(value):
    """Round a Python double to IEEE-754 binary32."""
    number = float(value)
    try:
        return _F32.unpack(_F32.pack(number))[0]
    except OverflowError:
        return math.copysign(math.inf, number)


def f32_bytes(samples):
    return b"".join(_F32.pack(float(value)) for value in samples)


def digest_samples(samples):
    return hashlib.sha256(f32_bytes(samples)).hexdigest()


def cpp_min(left, right):
    """C++ std::min(left, right) ordering, including nonfinite operands."""
    return right if right < left else left


def cpp_max(left, right):
    """C++ std::max(left, right) ordering, including nonfinite operands."""
    return right if left < right else left


def dbfs_to_linear(dbfs):
    return 10.0 ** (float(dbfs) / 20.0)


def linear_to_dbfs(linear):
    return 20.0 * math.log10(max(float(linear), RMS_FLOOR_LINEAR))


def rms_linear(samples):
    """Finite-only RMS; nonfinite samples are counted by the caller instead."""
    total = 0.0
    count = 0
    for value in samples:
        number = float(value)
        if math.isfinite(number):
            total += number * number
            count += 1
    return math.sqrt(total / count) if count else 0.0


def rms_db(samples):
    return linear_to_dbfs(rms_linear(samples))


def windowed_rms_db(samples, window):
    if window < 1:
        raise ValueError("window must be positive")
    return [rms_db(samples[index:index + window])
            for index in range(0, len(samples) - window + 1, window)]


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_numeric(config, name, low, high):
    if name not in config:
        raise ControlError("missing_control:" + name)
    value = config[name]
    if not _is_number(value):
        raise ControlError("nonnumeric_control:" + name)
    number = float(value)
    if not math.isfinite(number):
        raise ControlError("nonfinite_control:" + name)
    if not (low <= number <= high):
        raise ControlError("out_of_range:" + name)
    return number


def validate_controls(config, control):
    """Fail-closed validation; missing values never silently default."""
    if not isinstance(config, dict):
        raise ControlError("config_not_object")
    if config.get("control") != control:
        raise ControlError("control_mismatch")

    if control == "identity":
        allowed = {"control"}
    elif control == "static_target_gain_reference":
        allowed = {"control", "target_dbfs", "min_gain_db", "max_gain_db",
                   "ceiling_dbfs", "silence_floor_dbfs"}
    elif control == "fixed_gain_reference":
        allowed = {"control", "gain_db", "ceiling_dbfs"}
    else:
        raise ControlError("unknown_control:" + str(control))

    unknown = sorted(str(key) for key in config if key not in allowed)
    if unknown:
        raise ControlError("unknown_control:" + ",".join(unknown))
    missing = sorted(key for key in allowed if key not in config)
    if missing:
        raise ControlError("missing_control:" + ",".join(missing))

    if control == "identity":
        return {"control": control}
    if control == "fixed_gain_reference":
        return {
            "control": control,
            "gain_db": _validate_numeric(config, "gain_db", -36.0, 36.0),
            "ceiling_dbfs": _validate_numeric(config, "ceiling_dbfs", -12.0, 0.0),
        }

    validated = {
        "control": control,
        "target_dbfs": _validate_numeric(config, "target_dbfs", -60.0, -6.0),
        "min_gain_db": _validate_numeric(config, "min_gain_db", -36.0, 0.0),
        "max_gain_db": _validate_numeric(config, "max_gain_db", 0.0, 36.0),
        "ceiling_dbfs": _validate_numeric(config, "ceiling_dbfs", -12.0, 0.0),
        "silence_floor_dbfs": _validate_numeric(config, "silence_floor_dbfs", -80.0, -20.0),
    }
    if validated["min_gain_db"] > validated["max_gain_db"]:
        raise ControlError("gain_bounds_inverted")
    return validated


def _clamp_gain_linear(desired, low_db, high_db):
    return cpp_max(dbfs_to_linear(low_db), cpp_min(dbfs_to_linear(high_db), desired))


def _clamp_output(sample, gain, ceiling):
    limited = sample * gain
    value = cpp_max(-ceiling, cpp_min(ceiling, limited))
    clipped = 0
    if not (cpp_min(ceiling, limited) == limited and
            cpp_max(-ceiling, limited) == limited):
        clipped = 1
    return f32(value), clipped


def _frame_nonfinite(frame):
    return sum(1 for value in frame if not math.isfinite(float(value)))


def _require_frame(frame):
    if len(frame) != FRAME_SAMPLES:
        raise ValueError("frame_samples_mismatch")


class Identity:
    """Fidelity control: exact float32 pass-through with no ceiling applied."""

    name = "identity"

    def __init__(self, config):
        self.config = validate_controls(config, "identity")
        self.reset_count = 0

    def reset(self):
        self.reset_count += 1

    def plan(self, samples):
        return {
            "rms_db": rms_db(samples),
            "gain_db": 0.0,
            "gain": 1.0,
            "desired_gain_db_unbounded": None,
            "silence_bypass": False,
            "numerical_fallback": False,
            "ceiling": None,
            "finite_count": sum(1 for value in samples if math.isfinite(float(value))),
        }

    def process_frame(self, frame, plan, gain_trace=None):
        _require_frame(frame)
        output = [f32(value) for value in frame]
        if gain_trace is not None:
            gain_trace.extend([0.0] * len(frame))
        return {
            "samples": output,
            "clipped_samples": 0,
            "nonfinite_inputs": _frame_nonfinite(frame),
        }


class FixedGain:
    """Stateless fixed scale with a hard ceiling (energy-matched control)."""

    name = "fixed_gain_reference"

    def __init__(self, config):
        self.config = validate_controls(config, "fixed_gain_reference")
        self.gain_db = self.config["gain_db"]
        self.gain = dbfs_to_linear(self.gain_db)
        self.ceiling = dbfs_to_linear(self.config["ceiling_dbfs"])
        self.reset_count = 0

    def reset(self):
        self.reset_count += 1

    def plan(self, samples):
        return {
            "rms_db": rms_db(samples),
            "gain_db": self.gain_db,
            "gain": self.gain,
            "desired_gain_db_unbounded": self.gain_db,
            "silence_bypass": False,
            "numerical_fallback": False,
            "ceiling": self.ceiling,
            "finite_count": sum(1 for value in samples if math.isfinite(float(value))),
        }

    def process_frame(self, frame, plan, gain_trace=None):
        _require_frame(frame)
        output = []
        clipped = 0
        for raw in frame:
            value, was_clipped = _clamp_output(float(raw), self.gain, self.ceiling)
            output.append(value)
            clipped += was_clipped
        if gain_trace is not None:
            gain_trace.extend([self.gain_db] * len(frame))
        return {
            "samples": output,
            "clipped_samples": clipped,
            "nonfinite_inputs": _frame_nonfinite(frame),
        }


class StaticTargetGain:
    """Sequence-static RMS target gain, bounded scale, silence floor and ceiling."""

    name = "static_target_gain_reference"

    def __init__(self, config):
        self.config = validate_controls(config, "static_target_gain_reference")
        self.target_linear = dbfs_to_linear(self.config["target_dbfs"])
        self.ceiling = dbfs_to_linear(self.config["ceiling_dbfs"])
        self.reset_count = 0

    def reset(self):
        self.reset_count += 1

    def plan(self, samples):
        rms = rms_linear(samples)
        rms_db_value = linear_to_dbfs(rms)
        finite_count = sum(1 for value in samples if math.isfinite(float(value)))
        plan = {
            "rms_linear": rms,
            "rms_db": rms_db_value,
            "desired_gain_db_unbounded": None,
            "gain_db": 0.0,
            "gain": 1.0,
            "silence_bypass": False,
            "numerical_fallback": False,
            "ceiling": self.ceiling,
            "finite_count": finite_count,
        }
        if finite_count == 0:
            # Local fail-safe: no finite level to measure. Keep scale at 0 dB and
            # let the C++-style ceiling ordering map nonfinite samples to bounds.
            plan["numerical_fallback"] = True
            return plan

        desired_linear = self.target_linear / max(rms, RMS_FLOOR_LINEAR)
        plan["desired_gain_db_unbounded"] = linear_to_dbfs(desired_linear)
        if rms_db_value <= self.config["silence_floor_dbfs"]:
            # Explicit pause guard: a whole segment at/below the floor is not
            # amplified. This does not gate quiet spans inside an active segment.
            plan["silence_bypass"] = True
            return plan

        gain = _clamp_gain_linear(desired_linear,
                                  self.config["min_gain_db"],
                                  self.config["max_gain_db"])
        plan["gain"] = gain
        plan["gain_db"] = linear_to_dbfs(gain)
        return plan

    def process_frame(self, frame, plan, gain_trace=None):
        _require_frame(frame)
        output = []
        clipped = 0
        if plan["silence_bypass"]:
            output = [0.0] * len(frame)
        else:
            for raw in frame:
                value, was_clipped = _clamp_output(float(raw), plan["gain"], self.ceiling)
                output.append(value)
                clipped += was_clipped
        if gain_trace is not None:
            gain_trace.extend([plan["gain_db"]] * len(frame))
        return {
            "samples": output,
            "clipped_samples": clipped,
            "nonfinite_inputs": _frame_nonfinite(frame),
        }


def make_processor(config):
    control = config.get("control") if isinstance(config, dict) else None
    if control == "identity":
        return Identity(config)
    if control == "static_target_gain_reference":
        return StaticTargetGain(config)
    if control == "fixed_gain_reference":
        return FixedGain(config)
    raise ControlError("unknown_control:" + str(control))


def process_sequence(processor, samples, reset_at=(), trace=False):
    """Process a frame-aligned sequence; reset_at splits it into static segments.

    The gain of each segment is computed once from that segment's complete input.
    Reset boundaries therefore change the measured RMS and the applied gain, but
    there is no per-sample attack/release and no gain adaptation inside a segment.
    """
    if len(samples) % FRAME_SAMPLES:
        raise ValueError("sequence_not_frame_aligned")
    frame_count = len(samples) // FRAME_SAMPLES
    resets = sorted(set(int(item) for item in reset_at))
    if any(index <= 0 or index >= frame_count for index in resets):
        raise ValueError("reset_frame_out_of_range")

    output = []
    frames = []
    plans = []
    gain_trace = [] if trace else None
    boundaries = [0] + resets + [frame_count]
    for segment, begin in enumerate(boundaries[:-1]):
        end = boundaries[segment + 1]
        segment_samples = samples[begin * FRAME_SAMPLES:end * FRAME_SAMPLES]
        plan = processor.plan(segment_samples)
        plans.append({
            "segment": segment,
            "start_frame": begin,
            "end_frame": end,
            "rms_db": plan["rms_db"],
            "gain_db": plan["gain_db"],
            "gain": plan["gain"],
            "desired_gain_db_unbounded": plan["desired_gain_db_unbounded"],
            "silence_bypass": plan["silence_bypass"],
            "numerical_fallback": plan["numerical_fallback"],
        })
        for index in range(begin, end):
            frame = processor.process_frame(
                segment_samples[(index - begin) * FRAME_SAMPLES:
                                (index - begin + 1) * FRAME_SAMPLES],
                plan, gain_trace)
            output.extend(frame["samples"])
            frames.append({
                "index": index,
                "segment": segment,
                "reset_here": index in resets,
                "rms_db": plan["rms_db"],
                "gain_db": plan["gain_db"],
                "gain": plan["gain"],
                "desired_gain_db_unbounded": plan["desired_gain_db_unbounded"],
                "silence_bypass": plan["silence_bypass"],
                "numerical_fallback": plan["numerical_fallback"],
                "clipped_samples": frame["clipped_samples"],
                "nonfinite_inputs": frame["nonfinite_inputs"],
            })
    processor.reset_count = len(resets)
    return {
        "samples": output,
        "frames": frames,
        "plans": plans,
        "gain_trace": gain_trace,
        "reset_count": len(resets),
    }
