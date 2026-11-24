"""Deterministic, stdlib-only linear-interpolation declipping reference.

Developer-only, offline comparator.  No SDK ABI, descriptor, registry, default
provider or installed v0 behavior is changed by this module.  The reconstruction
mirrors ``declip_linear`` in ``src/audioml_eval/distortion_restoration.py``
(SHA-256 c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f)
and its runner's exact known-corruption mask: clipped samples are replaced by a
linear ramp between the nearest reliable samples on either side.  Boundary runs
hold the nearest reliable anchor, following NumPy ``numpy.interp`` endpoint
behavior; no extrapolation or clipping detection is attempted.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct

SAMPLE_RATE_HZ = 16000
SDK_FRAME_SAMPLES = 160
OFFLINE_BLOCK_SAMPLES = 2048
DEFAULT_THRESHOLD = 0.35
MASK_ABS_TOL = 1e-7
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


def json_dumps(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonical_bytes(value):
    return (json_dumps(value) + "\n").encode("ascii")


def canonical_digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def validate_controls(config):
    """Fail-closed validation: every control must be present and finite."""
    if not isinstance(config, dict):
        raise ControlError("config_not_object")
    allowed = {"threshold", "mask_source"}
    unknown = sorted(set(config) - allowed)
    if unknown:
        raise ControlError("unknown_control:" + ",".join(unknown))
    missing = sorted(allowed - {"mask_source"} - set(config))
    if missing:
        raise ControlError("missing_control:" + ",".join(missing))
    value = config["threshold"]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ControlError("nonnumeric_control:threshold")
    if not math.isfinite(value):
        raise ControlError("nonfinite_control:threshold")
    threshold = float(value)
    if not (0.0 < threshold <= 1.0):
        raise ControlError("threshold_out_of_range")
    mask_source = config.get("mask_source", "derived")
    if mask_source not in ("derived", "caller"):
        raise ControlError("mask_source_not_supported")
    return {"threshold": threshold, "mask_source": mask_source}


def hard_clip(samples, threshold):
    """Symmetric hard clipping at the exact binary32 saturation level."""
    level = f32(threshold)
    return [f32(max(-level, min(level, float(value)))) for value in samples]


def clip_mask(samples, threshold):
    """Exact known-corruption mask: saturation at either clipping level.

    The pilot runner identifies saturation with ``abs(clipped) >= threshold -
    1e-10`` in float64.  Here samples and levels are binary32, so the tolerance
    is widened to :data:`MASK_ABS_TOL`; membership is still exact equality after
    binary32 rounding, which :func:`assert_exact_mask` verifies.
    """
    level = abs(f32(threshold))
    return [math.isclose(abs(float(value)), level, rel_tol=0.0, abs_tol=MASK_ABS_TOL)
            for value in samples]


def assert_exact_mask(clean, clipped, mask, threshold):
    """Verify the mask is exactly the hard-clip mask of the frozen clean source."""
    if not (len(clean) == len(clipped) == len(mask)):
        raise ValueError("mask_length_mismatch")
    level = abs(f32(threshold))
    for index, bad in enumerate(mask):
        if bad:
            if abs(clipped[index]) != level:
                raise ValueError("mask_not_exact_saturation:" + str(index))
        elif clipped[index] != clean[index]:
            raise ValueError("mask_not_exact_preservation:" + str(index))


def _runs(mask):
    """Half-open [start, end) runs of masked samples."""
    runs = []
    start = None
    for index, bad in enumerate(mask):
        if bad and start is None:
            start = index
        elif not bad and start is not None:
            runs.append((start, index))
            start = None
    if start is not None:
        runs.append((start, len(mask)))
    return runs


def linear_interpolate(samples, mask):
    """Reconstruct clipped samples from the exact known mask.

    Returns samples plus a deterministic reconstruction trace.  Interior runs
    use a linear ramp between the nearest reliable samples; leading and trailing
    runs hold the nearest reliable anchor (NumPy ``interp`` endpoint behavior).
    With fewer than two reliable samples the clipped input is returned unchanged
    because no valid ramp or endpoint pair exists.
    """
    observed = [float(value) for value in samples]
    if len(observed) != len(mask):
        raise ValueError("mask_length_mismatch")
    if any(not math.isfinite(value) for value in observed):
        raise ValueError("nonfinite_input")
    reliable = [index for index, bad in enumerate(mask) if not bad]
    runs = _runs(mask)
    trace = {
        "anchor_rule": "numpy_interp_reliable_endpoints_constant_hold",
        "replacement_mode": "interior_ramp_and_endpoint_hold",
        "reliable_count": len(reliable),
        "masked_count": sum(mask),
        "run_count": len(runs),
        "runs": [],
    }
    if len(reliable) < 2:
        trace["replacement_mode"] = "no_reliable_anchor_unchanged"
        trace["replaced_count"] = 0
        for start, end in runs:
            trace["runs"].append({
                "start": start, "end": end, "length": end - start,
                "kind": "no_reliable_anchor", "left_anchor": None,
                "right_anchor": None, "left_anchor_value": None,
                "right_anchor_value": None, "first_output": observed[start],
                "last_output": observed[end - 1],
            })
        return {"samples": [f32(value) for value in observed], "trace": trace}
    first, last = reliable[0], reliable[-1]
    output = list(observed)
    replaced = 0
    for start, end in runs:
        if start == 0 and end == len(observed):
            kind = "all_masked"
        elif start == 0:
            kind = "leading"
        elif end == len(observed):
            kind = "trailing"
        else:
            kind = "interior"
        entry = {
            "start": start,
            "end": end,
            "length": end - start,
            "kind": kind,
            "left_anchor": None,
            "right_anchor": None,
            "left_anchor_value": None,
            "right_anchor_value": None,
        }
        if kind == "interior":
            left = max(index for index in reliable if index < start)
            right = min(index for index in reliable if index >= end)
            span = right - left
            entry["left_anchor"] = left
            entry["right_anchor"] = right
            entry["left_anchor_value"] = observed[left]
            entry["right_anchor_value"] = observed[right]
            for index in range(start, end):
                output[index] = observed[left] + ((index - left) / span) * (
                    observed[right] - observed[left])
        elif kind == "leading":
            anchor = first
            entry["left_anchor"] = anchor
            entry["right_anchor"] = anchor
            entry["left_anchor_value"] = observed[anchor]
            entry["right_anchor_value"] = observed[anchor]
            for index in range(start, end):
                output[index] = observed[anchor]
        elif kind == "trailing":
            anchor = last
            entry["left_anchor"] = anchor
            entry["right_anchor"] = anchor
            entry["left_anchor_value"] = observed[anchor]
            entry["right_anchor_value"] = observed[anchor]
            for index in range(start, end):
                output[index] = observed[anchor]
        else:  # all masked cannot occur with two reliable anchors
            raise ValueError("inconsistent_run")
        entry["first_output"] = output[start]
        entry["last_output"] = output[end - 1]
        replaced += end - start
        trace["runs"].append(entry)
    trace["replaced_count"] = replaced
    return {"samples": [f32(value) for value in output], "trace": trace}


def reliable_samples_preserved(samples, output, mask):
    """Every unmasked sample must survive the comparator bit-for-bit."""
    return all(output[index] == float(samples[index])
               for index, bad in enumerate(mask) if not bad)


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
