# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen, matched synthetic cases; run through the adapter, not a separate law."""

from fractions import Fraction
from hashlib import sha256

from reference import BLOCK, HZ, TARGET, UNITY
from run import ADAPTER, BOUNDARY, canonical, dispatch_json, request


def trace(samples=HZ * 30 - 23, drift=0, hold_at=0, hold_for=0):
    return dict(source_samples=samples, source_drift_ppm=drift,
                hold_start_tick=hold_at, hold_ticks=hold_for)


CASES = {
    "nominal_final_partial": trace(samples=HZ * 2 + 17),
    "source_fast_1000ppm": trace(drift=1_000),
    "source_slow_1000ppm": trace(drift=-1_000),
    "hold_then_release": trace(samples=HZ * 8 + 17, hold_at=200, hold_for=40),
    "beyond_control_range": trace(drift=60_000),
    "overflow_on_release": trace(samples=HZ * 8, hold_at=200, hold_for=100),
}


def adverse():
    base = canonical(request(trace()))
    return {
        "missing_trace": canonical(request(trace()) | {"trace": None}),
        "invalid_geometry": canonical(request(trace(samples=0))),
        "invalid_type": canonical(request(trace(drift=True))),
        "stale_adapter": canonical(request(trace()) | {"adapter_ref": {**ADAPTER, "revision": 2}}),
        "duplicate_field": '{"protocol_version":1,' + base[1:],
        **{f"nonfinite_{name}": base.replace('"source_drift_ppm":0',
                                            '"source_drift_ppm":' + token)
           for name, token in (("nan", "NaN"), ("inf", "Infinity"), ("exponent", "1e309"))},
    }


def summarize(result):
    rows = result["timeline"]
    play = [row for row in rows if row["state"] == "play"]
    rates = [row["rate_ppm"] for row in play]
    total = result["trace"]["source_samples"]
    live = [abs(row["queued_usamples"] - TARGET * UNITY) for row in play
            if row["accepted_samples"] < total]
    active = sum(Fraction(row["playout_duration"]) for row in play)
    end = play[-1]["playout_start"] + Fraction(play[-1]["playout_duration"]) if play else 0
    return {
        **{key: result[key] for key in ("status", "accepted_samples", "consumed_usamples",
                                        "rejected_arrival_samples", "rebuffer_count",
                                        "candidate_qualified")},
        "timeline_sha256": sha256(canonical(rows).encode()).hexdigest(),
        "prefill_samples": BLOCK * sum(row["state"] == "prefill" for row in rows),
        "rebuffer_samples": BLOCK * sum(row["state"] == "rebuffer" for row in rows),
        "active_playout_samples": str(active),
        "playout_end_sample": str(end),
        "overflow_at_playout_sample": rows[-1]["playout_start"]
        if result["status"] == "overflow" else None,
        "end_vs_nominal_media_samples": str(end - total) if result["consumed_usamples"] == (
            total * UNITY) else None,
        "average_live_abs_target_error_samples": str(Fraction(sum(live), len(live) * UNITY))
        if live else None,
        "rate_bounds_ppm": [min(rates), max(rates)] if rates else None,
        "rate_changes": sum(a != b for a, b in zip([UNITY] + rates, rates)),
        "max_step_ppm": max((abs(a - b) for a, b in zip([UNITY] + rates, rates)), default=0),
        "last_play_interval": play[-1] if play else None,
        "peak_admitted_occupancy_usamples": max((row.get("queued_usamples", 0) for row in rows),
                                                default=0),
    }


def report():
    return {
        "boundary": BOUNDARY,
        "decision": "defer", "candidate_qualified": False,
        "not_measured": ["unfamiliar_speech", "music", "silence_pcm", "pitch",
                         "transient_audibility", "speech_preservation", "device_pacing",
                         "native_actuator_fill_flush", "device_latency", "resource_limits"],
        "cases": {name: {"trace": values, **{
            policy: summarize(dispatch_json(canonical(request(values, policy))))
            for policy in ("controller", "fixed_1x")
        }} for name, values in CASES.items()},
        "rejections": {name: dispatch_json(text) for name, text in adverse().items()},
    }


if __name__ == "__main__":
    print(canonical(report()), end="")
