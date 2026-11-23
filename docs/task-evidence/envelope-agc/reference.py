"""Deterministic stdlib reference for the SDK-ENVELOPE-AGC DSP fixture.

Developer-only and task-local. The envelope controller is a causal
re-expression of the algorithm pinned at ``src/audioml_eval/level_tone.py``
(sha256 a0ec2e3b...): asymmetric envelope smoothing, dBFS target with bounded
desired gain, first-order log-domain gain smoothing and a hard peak ceiling.
The one-pole gain smoother is implemented here without NumPy/SciPy using the
 bilinear-transformed first-order Butterworth section at 8 Hz.

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
ENVELOPE_FLOOR = 1e-8

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
    return 20.0 * math.log10(max(float(linear), 1e-300))


def rms_db(samples):
    total = 0.0
    count = 0
    for value in samples:
        number = float(value)
        if math.isfinite(number):
            total += number * number
            count += 1
    return 20.0 * math.log10(max(math.sqrt(total / count) if count else 0.0, 1e-8))


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
    elif control == "envelope_agc_reference":
        allowed = {"control", "target_dbfs", "attack_ms", "release_ms",
                   "min_gain_db", "max_gain_db", "ceiling_dbfs", "gain_smooth_hz"}
    elif control == "static_gain_reference":
        allowed = {"control", "gain_db", "ceiling_dbfs"}
    elif control == "peak_limiter_reference":
        allowed = {"control", "ceiling", "release_ms"}
    elif control == "compressor_reference":
        allowed = {"control", "threshold_dbfs", "ratio", "attack_ms",
                   "release_ms", "ceiling_dbfs"}
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
    if control == "envelope_agc_reference":
        validated = {
            "control": control,
            "target_dbfs": _validate_numeric(config, "target_dbfs", -60.0, -6.0),
            "attack_ms": _validate_numeric(config, "attack_ms", 0.1, 200.0),
            "release_ms": _validate_numeric(config, "release_ms", 1.0, 2000.0),
            "min_gain_db": _validate_numeric(config, "min_gain_db", -36.0, 0.0),
            "max_gain_db": _validate_numeric(config, "max_gain_db", 0.0, 36.0),
            "ceiling_dbfs": _validate_numeric(config, "ceiling_dbfs", -12.0, 0.0),
            "gain_smooth_hz": _validate_numeric(config, "gain_smooth_hz", 0.5, 40.0),
        }
        if validated["min_gain_db"] > validated["max_gain_db"]:
            raise ControlError("gain_bounds_inverted")
        return validated
    if control == "static_gain_reference":
        return {
            "control": control,
            "gain_db": _validate_numeric(config, "gain_db", -36.0, 36.0),
            "ceiling_dbfs": _validate_numeric(config, "ceiling_dbfs", -12.0, 0.0),
        }
    if control == "peak_limiter_reference":
        return {
            "control": control,
            "ceiling": _validate_numeric(config, "ceiling", 1e-6, 1.0),
            "release_ms": _validate_numeric(config, "release_ms", 1e-3, 5000.0),
        }
    return {
        "control": control,
        "threshold_dbfs": _validate_numeric(config, "threshold_dbfs", -48.0, -3.0),
        "ratio": _validate_numeric(config, "ratio", 1.0, 20.0),
        "attack_ms": _validate_numeric(config, "attack_ms", 0.1, 200.0),
        "release_ms": _validate_numeric(config, "release_ms", 1.0, 2000.0),
        "ceiling_dbfs": _validate_numeric(config, "ceiling_dbfs", -12.0, 0.0),
    }


class EnvelopeAGC:
    """Frame-stateful causal envelope AGC; process() consumes one fixed frame."""

    def __init__(self, config, sample_rate=SAMPLE_RATE_HZ):
        self.config = validate_controls(config, "envelope_agc_reference")
        self.sample_rate = int(sample_rate)
        self.attack_coeff = math.exp(-1000.0 / (self.sample_rate * self.config["attack_ms"]))
        self.release_coeff = math.exp(-1000.0 / (self.sample_rate * self.config["release_ms"]))
        warped = math.tan(math.pi * self.config["gain_smooth_hz"] / self.sample_rate)
        self.sos_b0 = warped / (1.0 + warped)
        self.sos_b1 = self.sos_b0
        self.sos_a1 = (warped - 1.0) / (warped + 1.0)
        self.target_linear = dbfs_to_linear(self.config["target_dbfs"])
        self.min_gain_linear = dbfs_to_linear(self.config["min_gain_db"])
        self.max_gain_linear = dbfs_to_linear(self.config["max_gain_db"])
        self.ceiling = dbfs_to_linear(self.config["ceiling_dbfs"])
        self.reset_count = 0
        self._initialize_state()

    def _initialize_state(self):
        self.envelope = ENVELOPE_FLOOR
        self.sos_z1 = None
        self.sos_z2 = 0.0
        self.gain_db = None

    def reset(self):
        self._initialize_state()
        self.reset_count += 1

    def _smooth(self, desired_db):
        if self.sos_z1 is None:
            self.sos_z1 = (1.0 - self.sos_b0) * desired_db
            self.sos_z2 = 0.0
            return desired_db
        value = self.sos_b0 * desired_db + self.sos_z1
        new_z1 = self.sos_b1 * desired_db - self.sos_a1 * value + self.sos_z2
        self.sos_z1 = new_z1
        self.sos_z2 = 0.0
        return value

    def process(self, samples, gain_trace=None):
        if len(samples) != FRAME_SAMPLES:
            raise ValueError("frame_samples_mismatch")
        output = []
        envelopes = []
        desired_db_values = []
        clipped = 0
        nonfinite_inputs = 0
        peak_envelope = 0.0
        for raw in samples:
            sample = float(raw)
            if not math.isfinite(sample):
                nonfinite_inputs += 1
            level = abs(sample)
            coefficient = self.attack_coeff if level > self.envelope else self.release_coeff
            self.envelope = coefficient * self.envelope + (1.0 - coefficient) * level
            if math.isfinite(self.envelope):
                peak_envelope = max(peak_envelope, self.envelope)
            desired = self.target_linear / max(self.envelope, ENVELOPE_FLOOR)
            desired = cpp_max(self.min_gain_linear, cpp_min(self.max_gain_linear, desired))
            desired_db = linear_to_dbfs(desired)
            self.gain_db = self._smooth(desired_db)
            gain = dbfs_to_linear(self.gain_db)
            limited = sample * gain
            value = cpp_max(-self.ceiling, cpp_min(self.ceiling, limited))
            if not (cpp_min(self.ceiling, limited) == limited and
                    cpp_max(-self.ceiling, limited) == limited):
                clipped += 1
            output.append(f32(value))
            envelopes.append(self.envelope)
            desired_db_values.append(desired_db)
            if gain_trace is not None:
                gain_trace.append(self.gain_db)
        return {
            "samples": output,
            "gain_db": self.gain_db,
            "gain": dbfs_to_linear(self.gain_db),
            "envelope": self.envelope,
            "envelope_peak": peak_envelope,
            "desired_gain_db_min": min(desired_db_values),
            "desired_gain_db_max": max(desired_db_values),
            "clipped_samples": clipped,
            "nonfinite_inputs": nonfinite_inputs,
        }


class StaticGain:
    """Stateless target-gain control with a hard safety ceiling."""

    def __init__(self, config):
        self.config = validate_controls(config, "static_gain_reference")
        self.gain = dbfs_to_linear(self.config["gain_db"])
        self.ceiling = dbfs_to_linear(self.config["ceiling_dbfs"])
        self.reset_count = 0

    def reset(self):
        self.reset_count += 1

    def process(self, samples, gain_trace=None):
        if len(samples) != FRAME_SAMPLES:
            raise ValueError("frame_samples_mismatch")
        output = []
        clipped = 0
        for raw in samples:
            sample = float(raw)
            limited = sample * self.gain
            value = cpp_max(-self.ceiling, cpp_min(self.ceiling, limited))
            if not (cpp_min(self.ceiling, limited) == limited and
                    cpp_max(-self.ceiling, limited) == limited):
                clipped += 1
            output.append(f32(value))
            if gain_trace is not None:
                gain_trace.append(linear_to_dbfs(self.gain))
        return {"samples": output, "gain_db": linear_to_dbfs(self.gain),
                "gain": self.gain, "envelope": None, "envelope_peak": 0.0,
                "desired_gain_db_min": linear_to_dbfs(self.gain),
                "desired_gain_db_max": linear_to_dbfs(self.gain),
                "clipped_samples": clipped,
                "nonfinite_inputs": sum(1 for value in samples if not math.isfinite(float(value)))}


class PeakLimiter:
    """Small release-smoothed peak limiter used only for interaction controls."""

    def __init__(self, config):
        self.config = validate_controls(config, "peak_limiter_reference")
        self.ceiling = self.config["ceiling"]
        self.coefficient = 1.0 - math.exp(-1000.0 /
                                          (self.config["release_ms"] * SAMPLE_RATE_HZ))
        self.gain = 1.0
        self.reset_count = 0

    def reset(self):
        self.gain = 1.0
        self.reset_count += 1

    def process(self, samples, gain_trace=None):
        if len(samples) != FRAME_SAMPLES:
            raise ValueError("frame_samples_mismatch")
        output = []
        engaged = False
        for raw in samples:
            sample = float(raw)
            peak = abs(sample)
            target = 1.0
            if peak > self.ceiling:
                target = self.ceiling / peak
                engaged = True
            if target < self.gain:
                self.gain = target
            else:
                self.gain += self.coefficient * (target - self.gain)
            value = cpp_max(-self.ceiling, cpp_min(self.ceiling, sample * self.gain))
            output.append(f32(value))
            if gain_trace is not None:
                gain_trace.append(linear_to_dbfs(self.gain))
        return {"samples": output, "gain_db": linear_to_dbfs(self.gain),
                "gain": self.gain, "envelope": None, "envelope_peak": 0.0,
                "desired_gain_db_min": 0.0, "desired_gain_db_max": 0.0,
                "clipped_samples": 0, "engaged": engaged,
                "nonfinite_inputs": sum(1 for value in samples if not math.isfinite(float(value)))}


class DownwardCompressor:
    """Small hard-knee log-domain compressor used only for interaction controls."""

    def __init__(self, config):
        self.config = validate_controls(config, "compressor_reference")
        self.threshold_db = self.config["threshold_dbfs"]
        self.ratio = self.config["ratio"]
        self.ceiling = dbfs_to_linear(self.config["ceiling_dbfs"])
        self.attack_alpha = 1.0 - math.exp(-1000.0 /
                                           (self.config["attack_ms"] * SAMPLE_RATE_HZ))
        self.release_alpha = 1.0 - math.exp(-1000.0 /
                                            (self.config["release_ms"] * SAMPLE_RATE_HZ))
        self.gain_reduction_db = 0.0
        self.reset_count = 0

    def reset(self):
        self.gain_reduction_db = 0.0
        self.reset_count += 1

    def process(self, samples, gain_trace=None):
        if len(samples) != FRAME_SAMPLES:
            raise ValueError("frame_samples_mismatch")
        output = []
        clipped = 0
        for raw in samples:
            sample = float(raw)
            level = abs(sample)
            if level > 0.0 and math.isfinite(level):
                level_db = linear_to_dbfs(level)
                excess = level_db - self.threshold_db
                target = -(excess - excess / self.ratio) if excess > 0.0 else 0.0
            else:
                target = 0.0
            alpha = self.attack_alpha if target < self.gain_reduction_db else self.release_alpha
            self.gain_reduction_db += alpha * (target - self.gain_reduction_db)
            gain = dbfs_to_linear(self.gain_reduction_db)
            limited = sample * gain
            value = cpp_max(-self.ceiling, cpp_min(self.ceiling, limited))
            if not (cpp_min(self.ceiling, limited) == limited and
                    cpp_max(-self.ceiling, limited) == limited):
                clipped += 1
            output.append(f32(value))
            if gain_trace is not None:
                gain_trace.append(self.gain_reduction_db)
        return {"samples": output, "gain_db": self.gain_reduction_db,
                "gain": gain, "envelope": None, "envelope_peak": 0.0,
                "desired_gain_db_min": 0.0, "desired_gain_db_max": 0.0,
                "clipped_samples": clipped,
                "nonfinite_inputs": sum(1 for value in samples if not math.isfinite(float(value)))}


def make_processor(config):
    control = config.get("control") if isinstance(config, dict) else None
    if control == "identity":
        validate_controls(config, "identity")
        return None
    if control == "envelope_agc_reference":
        return EnvelopeAGC(config)
    if control == "static_gain_reference":
        return StaticGain(config)
    if control == "peak_limiter_reference":
        return PeakLimiter(config)
    if control == "compressor_reference":
        return DownwardCompressor(config)
    raise ControlError("unknown_control:" + str(control))


def process_sequence(processor, samples, reset_at=(), trace=False):
    """Process a frame-aligned sequence; reset_at holds frame indices."""
    if len(samples) % FRAME_SAMPLES:
        raise ValueError("sequence_not_frame_aligned")
    frames = []
    output = []
    gain_trace = [] if trace else None
    resets = set(int(item) for item in reset_at)
    for index in range(len(samples) // FRAME_SAMPLES):
        if index in resets:
            processor.reset()
        begin = index * FRAME_SAMPLES
        frame = processor.process(samples[begin:begin + FRAME_SAMPLES], gain_trace)
        output.extend(frame["samples"])
        frames.append({
            "index": index,
            "gain_db": frame["gain_db"],
            "gain": frame["gain"],
            "envelope_peak": frame["envelope_peak"],
            "desired_gain_db_min": frame["desired_gain_db_min"],
            "desired_gain_db_max": frame["desired_gain_db_max"],
            "clipped_samples": frame["clipped_samples"],
            "nonfinite_inputs": frame["nonfinite_inputs"],
            "engaged": frame.get("engaged", False),
        })
    return {"samples": output, "frames": frames,
            "gain_trace": gain_trace, "reset_count": processor.reset_count,
            "gain_final": dbfs_to_linear(frames[-1]["gain_db"]) if frames else 1.0}
