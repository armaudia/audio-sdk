"""Generate the frozen, asset-free developer screen. Not an audio-bench bundle."""

import hashlib
import json
import math
from pathlib import Path
from statistics import fmean

import numpy as np
from audio_bench import metrics

SDK_FIXTURE = Path(__file__).resolve().parents[3] / "conformance/evidence/positive/input.json"
FIXTURE_SHA = "a112e8c106b4b013f8fdf16af325e3d60b7ee4666bb3e57deec9bb1749369492"
BENCH_REVISION = "e623e14a4e85a6be7f6061aa50a30bb8824af132"
METRICS_SHA = "5f4a16aab66bdef244e57d7b3c93237ebf0bf2bf9ef2d9ad0e0b4ff063107210"
NUMPY_VERSION = "2.5.4"
METRIC_IDS = ("si_sdr_db", "local_sd_sdr_db", "local_snr_db")
VARIANTS = ("identity", "less_noise", "more_noise", "half_gain", "dc_offset", "missing", "nonfinite")
# (ID, frozen source crop, raw noise amplitude, positive-control residual fraction)
CASES = (("long", (0, 340), 0.5, 0.25), ("short", (1, 161), 0.25, 0.5))


def render(samples):
    # The fixture models a delayed sample buffer, not a processor or timing benchmark.
    return np.pad(samples, (160, 0))


def impulse_delay(probe, output):
    sent = np.flatnonzero(probe)
    received = np.flatnonzero(output)
    if (len(sent) == len(received) == 1 and np.isfinite(probe[sent[0]])
            and output[received[0]] == probe[sent[0]]):
        delay = int(received[0] - sent[0])
        if delay >= 0:
            return delay
    return None


def map_interval(trace, interval, delay):
    """Return the raw slice for a frozen source interval, or reject the mapping."""
    if delay is None:
        raise ValueError("timing_mapping_unverified")
    origin = int(trace["first_input_sample"])
    begin, end = interval
    cursor, produced = begin, 0
    mapped_start = None
    for entry in trace["entries"]:
        offset = int(entry["valid_offset"])
        count = int(entry["valid_count"])
        start = int(entry["source_first_sample"]) + offset
        if count:
            raw_start = produced + offset
            if raw_start - (start - origin) != delay:
                raise ValueError("timing_mapping_mismatch")
            lo, hi = max(start, begin), min(start + count, end)
            if lo < hi:
                if lo != cursor:
                    raise ValueError("incomplete_valid_region")
                if mapped_start is None:
                    mapped_start = raw_start + lo - start
                cursor = hi
        produced += int(entry["produced_count"])
    if mapped_start is None or cursor != end:
        raise ValueError("incomplete_valid_region")
    return slice(mapped_start, mapped_start + end - begin), produced


def energy(samples):
    return float(np.dot(samples, samples))


def local_ratios(clean, estimate):
    reference_energy = energy(clean)
    error = energy(estimate - clean)
    ref = clean - clean.mean()
    out = estimate - estimate.mean()
    centered_energy = energy(ref)
    target_energy = energy(ref * (float(np.dot(out, ref)) / centered_energy)) if centered_energy else 0.0

    def ratio(numerator, denominator, zero_reason):
        if not numerator:
            return None, zero_reason
        if not denominator:
            return None, "perfect_reconstruction"
        return 10.0 * math.log10(numerator / denominator), None

    sd_sdr = ratio(target_energy, energy(out - ref),
                   "zero_projected_energy" if centered_energy else "zero_reference_energy")
    return sd_sdr, ratio(reference_energy, error, "zero_reference_energy")


def score(clean, raw, output, mapped):
    region, produced = mapped
    reason = None
    if clean is None:
        reason = "missing_reference"
    elif output is None:
        reason = "missing_output"
    elif output.size < produced:
        reason = "incomplete_output"
    elif output.size > produced:
        reason = "invalid_output_geometry"
    elif not np.isfinite(output[region]).all():
        reason = "nonfinite_valid_output"
    if reason:
        status = {"missing_reference": "blocked", "missing_output": "blocked", "incomplete_output": "failed"}.get(
            reason, "invalid")
        return {"status": status, "reason": reason, "metrics": None}

    estimate = output[region]
    values = (metrics.si_sdr(clean, estimate), *local_ratios(clean, estimate),
              metrics.si_sdr_improvement(clean, estimate, raw))
    gain, gain_reason = metrics.rms_gain_ratio(raw, estimate)
    return {
        "status": "scored",
        "reason": None,
        "metrics": {key: {"value_db": value, "reason": why}
                    for key, (value, why) in zip((*METRIC_IDS, "si_sdr_improvement_db"), values, strict=True)},
        "rms_gain_ratio": {"value": gain, "reason": gain_reason},
    }


def summaries(cases):
    result = {}
    for variant in VARIANTS:
        result[variant] = {}
        for metric in METRIC_IDS:
            deltas, excluded = {}, {}
            for case_id, case in cases.items():
                pair = []
                for name in (variant, "identity"):
                    row = case["variants"][name]
                    value = row["metrics"][metric] if row["metrics"] else {"value_db": None, "reason": row["reason"]}
                    pair.append(value)
                if all(item["value_db"] is not None and math.isfinite(item["value_db"]) for item in pair):
                    deltas[case_id] = pair[0]["value_db"] - pair[1]["value_db"]
                else:
                    excluded[case_id] = {"candidate": pair[0]["reason"], "identity": pair[1]["reason"]}
            result[variant][metric] = {
                "eligible": len(cases), "paired": len(deltas), "excluded": excluded,
                "paired_delta_db": deltas, "mean_delta_db": fmean(deltas.values()) if deltas else None,
                "coverage": "complete" if not excluded else "partial_diagnostic" if deltas else "unavailable",
            }
    return result


def build_report():
    if hashlib.sha256(Path(metrics.__file__).read_bytes()).hexdigest() != METRICS_SHA or np.__version__ != NUMPY_VERSION:
        raise ValueError("use the pinned audio-bench metrics module and NumPy version")
    fixture = SDK_FIXTURE.read_bytes()
    if hashlib.sha256(fixture).hexdigest() != FIXTURE_SHA:
        raise ValueError("SDK evidence fixture bytes differ from the frozen input")
    trace = json.loads(fixture)["trace"]
    probe = np.zeros(340, dtype=np.float64)
    probe[19] = 1.0
    delay = impulse_delay(probe, render(probe))
    ref = np.tile([0.25, -0.25, 0.25, -0.25], 85)
    noise = np.tile([0.25, 0.25, -0.25, -0.25], 85)
    cases = {}
    for case_id, interval, amplitude, fraction in CASES:
        begin, end = interval
        mapped = map_interval(trace, interval, delay)
        raw = ref + amplitude * noise
        less = ref + fraction * amplitude * noise
        more = ref + 2.0 * amplitude * noise
        values = (raw, less, more, 0.5 * raw, raw + 0.125,
                  less if case_id == "long" else None, less)
        rows = {}
        for variant, samples in zip(VARIANTS, values, strict=True):
            output = render(samples) if samples is not None else None
            if output is not None:
                # A NaN in invalid startup must be irrelevant; one in the valid crop must block scoring.
                output[:delay] = np.nan
                if variant == "nonfinite" and case_id == "long":
                    output[mapped[0].start] = np.nan
            rows[variant] = score(ref[begin:end], raw[begin:end], output, mapped)
        cases[case_id] = {"source_interval": interval, "raw_interval": (mapped[0].start, mapped[0].stop),
                          "valid_samples": end - begin, "variants": rows}
    return {
        "protocol": "sdk.synthetic-metric-comparison.v1",
        "evidence_kind": "paired_synthetic_developer_only",
        "bench_revision": BENCH_REVISION,
        "bench_metrics_sha256": METRICS_SHA,
        "numpy_version": NUMPY_VERSION,
        "sdk_fixture_sha256": FIXTURE_SHA,
        "sample_rate_hz": trace["sample_rate_hz"],
        "synthetic_measured_content_delay_samples": delay,
        "cases": cases,
        "summaries": summaries(cases),
    }


if __name__ == "__main__":
    try:
        print(json.dumps(build_report(), allow_nan=False, indent=2))
    except ValueError as error:
        raise SystemExit(str(error)) from error
