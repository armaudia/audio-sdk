"""Deterministic, stdlib-only band-limited POCS declipping reference.

Developer-only, offline reference.  No SDK ABI, descriptor, registry, default
provider or installed v0 behavior is changed by this module.  The projection
mirrors the lightweight baseline in
``src/audioml_eval/distortion_restoration.py`` (SHA-256
c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f):
zero the clipped samples, alternate a hard band-limit with exact known-sample
and saturation-cone constraints, then apply one final band-limit/constraint
pass.  The pilot uses NumPy's arbitrary-length rFFT; this reference uses a
power-of-two radix-2 transform on 2048-sample offline blocks so that it is
portable and dependency free.  Results are therefore descriptive for this
synthetic fixture, not a bit-exact replay of the pilot.
"""

from __future__ import annotations

import hashlib
import math
import struct

SAMPLE_RATE_HZ = 16000
SDK_FRAME_SAMPLES = 160
OFFLINE_BLOCK_SAMPLES = 2048
DEFAULT_THRESHOLD = 0.35
DEFAULT_CUTOFF_HZ = 7600.0
DEFAULT_ITERATIONS = 60
MAX_ITERATIONS = 60
MIN_CUTOFF_HZ = 100.0
MAX_CUTOFF_HZ = SAMPLE_RATE_HZ / 2.0 - 100.0
_F32 = struct.Struct("<f")


class ControlError(ValueError):
    """Raised for a rejected reference control."""


def f32(value):
    """Round a Python double to IEEE-754 binary32."""
    return _F32.unpack(_F32.pack(float(value)))[0]


def f32_bytes(samples):
    return b"".join(_F32.pack(value) for value in samples)


def digest_samples(samples):
    return hashlib.sha256(f32_bytes(samples)).hexdigest()


def canonical_bytes(value):
    return (json_dumps(value) + "\n").encode("ascii")


def json_dumps(value):
    # Kept here so every local digest and report uses one canonical form.
    import json

    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonical_digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def validate_controls(config):
    """Fail-closed validation: all controls must be present and finite."""
    if not isinstance(config, dict):
        raise ControlError("config_not_object")
    allowed = {"threshold", "cutoff_hz", "iterations"}
    unknown = sorted(set(config) - allowed)
    if unknown:
        raise ControlError("unknown_control:" + ",".join(unknown))
    missing = sorted(allowed - set(config))
    if missing:
        raise ControlError("missing_control:" + ",".join(missing))
    for name in ("threshold", "cutoff_hz"):
        value = config[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ControlError("nonnumeric_control:" + name)
        if not math.isfinite(value):
            raise ControlError("nonfinite_control:" + name)
    threshold = float(config["threshold"])
    cutoff_hz = float(config["cutoff_hz"])
    iterations = config["iterations"]
    if not (0.0 < threshold <= 1.0):
        raise ControlError("threshold_out_of_range")
    if not (MIN_CUTOFF_HZ <= cutoff_hz <= MAX_CUTOFF_HZ):
        raise ControlError("cutoff_out_of_range")
    if isinstance(iterations, bool) or not isinstance(iterations, int):
        raise ControlError("iterations_not_integer")
    if not (1 <= iterations <= MAX_ITERATIONS):
        raise ControlError("iterations_out_of_range")
    return {"threshold": threshold, "cutoff_hz": cutoff_hz, "iterations": iterations}


def complex_fft(values, inverse=False):
    """Iterative radix-2 Cooley-Tukey transform; length must be a power of two."""
    count = len(values)
    if count < 1 or count & (count - 1):
        raise ValueError("fft_requires_power_of_two")
    real = [float(value.real) for value in values]
    imag = [float(value.imag) for value in values]
    j = 0
    for index in range(1, count):
        bit = count >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if index < j:
            real[index], real[j] = real[j], real[index]
            imag[index], imag[j] = imag[j], imag[index]
    sign = 2.0 if inverse else -2.0
    length = 2
    while length <= count:
        angle = sign * math.pi / length
        step_re, step_im = math.cos(angle), math.sin(angle)
        half = length // 2
        for start in range(0, count, length):
            w_re, w_im = 1.0, 0.0
            for index in range(start, start + half):
                other = index + half
                tr = w_re * real[other] - w_im * imag[other]
                ti = w_re * imag[other] + w_im * real[other]
                real[other] = real[index] - tr
                imag[other] = imag[index] - ti
                real[index] += tr
                imag[index] += ti
                next_re = w_re * step_re - w_im * step_im
                w_im = w_re * step_im + w_im * step_re
                w_re = next_re
        length <<= 1
    if inverse:
        real = [value / count for value in real]
        imag = [value / count for value in imag]
    return [complex(real[index], imag[index]) for index in range(count)]


def rfft(samples):
    spectrum = complex_fft([complex(float(value), 0.0) for value in samples])
    return spectrum[:len(samples) // 2 + 1]


def irfft(spectrum, count):
    full = []
    for index in range(count):
        if index < len(spectrum):
            full.append(spectrum[index])
        else:
            conjugate = spectrum[count - index]
            full.append(complex(conjugate.real, -conjugate.imag))
    return [value.real for value in complex_fft(full, inverse=True)]


def hard_clip(samples, threshold):
    return [f32(max(-threshold, min(threshold, float(value)))) for value in samples]


def clip_mask(samples, threshold):
    """Known-corruption mask: hard clipping saturates at +/- threshold."""
    return [math.isclose(abs(float(value)), threshold, rel_tol=0.0, abs_tol=1e-7)
            for value in samples]


def linear_interpolate(samples, mask):
    """Pilot linear-interpolation baseline; no change if fewer than two anchors."""
    observed = [float(value) for value in samples]
    reliable = [index for index, bad in enumerate(mask) if not bad]
    if len(reliable) < 2:
        return [f32(value) for value in observed]
    output = list(observed)
    for index, bad in enumerate(mask):
        if not bad:
            continue
        right = 0
        while right < len(reliable) and reliable[right] < index:
            right += 1
        if right == 0:
            left_index, right_index = reliable[0], reliable[1]
        elif right == len(reliable):
            left_index, right_index = reliable[-2], reliable[-1]
        else:
            left_index, right_index = reliable[right - 1], reliable[right]
        fraction = ((index - left_index) / (right_index - left_index)
                    if right_index != left_index else 0.0)
        output[index] = observed[left_index] + fraction * (
            observed[right_index] - observed[left_index])
    return [f32(value) for value in output]


def pocs_declip(samples, mask, cutoff_hz=DEFAULT_CUTOFF_HZ,
                iterations=DEFAULT_ITERATIONS):
    """Band-limited POCS on one fixed offline block.

    Returns the float32 output plus a deterministic per-projection trace.
    ``iterations`` is capped by :func:`validate_controls` before this function
    is reached; a direct call still fails closed on the documented cap.
    """
    count = len(samples)
    if count != OFFLINE_BLOCK_SAMPLES:
        raise ValueError("offline_block_samples_mismatch")
    if len(mask) != count:
        raise ValueError("mask_length_mismatch")
    if not (1 <= iterations <= MAX_ITERATIONS):
        raise ValueError("iterations_out_of_range")
    observed = [float(value) for value in samples]
    if any(not math.isfinite(value) for value in observed):
        raise ValueError("nonfinite_input")
    if not (MIN_CUTOFF_HZ <= cutoff_hz <= MAX_CUTOFF_HZ):
        raise ValueError("cutoff_out_of_range")
    frequencies = [index * SAMPLE_RATE_HZ / count for index in range(count // 2 + 1)]
    keep = [frequency <= min(cutoff_hz, SAMPLE_RATE_HZ / 2.0 - 1.0)
            for frequency in frequencies]
    reliable = [not bad for bad in mask]
    positive = [bad and value > 0.0 for bad, value in zip(mask, observed)]
    negative = [bad and value < 0.0 for bad, value in zip(mask, observed)]
    working = list(observed)
    for index, bad in enumerate(mask):
        if bad:
            working[index] = 0.0
    trace = []

    def constrain(values):
        for index in range(count):
            if reliable[index]:
                values[index] = observed[index]
            elif positive[index]:
                values[index] = max(values[index], observed[index])
            elif negative[index]:
                values[index] = min(values[index], observed[index])

    def project(values):
        spectrum = rfft(values)
        for index, allowed in enumerate(keep):
            if not allowed:
                spectrum[index] = 0j
        return irfft(spectrum, count)

    constrain(working)
    for step in range(1, iterations + 1):
        previous = list(working)
        projected = project(previous)
        before_constraint = max((abs(projected[index] - previous[index])
                                 for index in range(count) if mask[index]), default=0.0)
        working = projected
        constrain(working)
        deltas = [abs(working[index] - previous[index]) for index in range(count)]
        trace.append({
            "projection": step,
            "max_delta": max(deltas),
            "rms_delta": math.sqrt(sum(delta * delta for delta in deltas) / count),
            "clipped_pre_constraint_delta": before_constraint,
            "peak_abs": max(abs(value) for value in working),
        })
    # The pilot performs one final projection; report it as a distinct step so
    # the bounded work total is explicit.
    previous = list(working)
    projected = project(previous)
    before_constraint = max((abs(projected[index] - previous[index])
                             for index in range(count) if mask[index]), default=0.0)
    working = projected
    constrain(working)
    deltas = [abs(working[index] - previous[index]) for index in range(count)]
    trace.append({
        "projection": iterations + 1,
        "max_delta": max(deltas),
        "rms_delta": math.sqrt(sum(delta * delta for delta in deltas) / count),
        "clipped_pre_constraint_delta": before_constraint,
        "peak_abs": max(abs(value) for value in working),
    })
    output = [f32(value) for value in working]
    return {
        "samples": output,
        "trace": trace,
        "projection_count": iterations + 1,
        "iterations": iterations,
        "cutoff_hz": cutoff_hz,
        "kept_bins": sum(keep),
        "clipped_samples": sum(mask),
    }


def si_sdr_db(reference_samples, estimate):
    if len(reference_samples) != len(estimate):
        raise ValueError("scoring_length_mismatch")
    target_energy = sum(float(value) ** 2 for value in reference_samples)
    if target_energy == 0.0:
        return 0.0
    projection = sum(float(value) * float(guess)
                     for value, guess in zip(reference_samples, estimate)) / target_energy
    target = [projection * float(value) for value in reference_samples]
    noise = [float(guess) - value for value, guess in zip(target, estimate)]
    target_norm = sum(value ** 2 for value in target)
    noise_norm = sum(value ** 2 for value in noise)
    if noise_norm == 0.0:
        return 120.0
    return 10.0 * math.log10(target_norm / noise_norm)


def rmse(reference_samples, estimate, indices=None):
    positions = range(len(reference_samples)) if indices is None else indices
    differences = [float(reference_samples[index]) - float(estimate[index])
                   for index in positions]
    if not differences:
        return 0.0
    return math.sqrt(sum(value * value for value in differences) / len(differences))


def max_abs_diff(left, right):
    if len(left) != len(right):
        raise ValueError("comparison_length_mismatch")
    return max((abs(float(a) - float(b)) for a, b in zip(left, right)), default=0.0)
