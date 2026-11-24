# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Offline rate-map fixture and pitch-changing control; no Bungee runtime."""

import hashlib
import json
import math
from fractions import Fraction
from itertools import pairwise

RATE = 16_000
HOP = 160
SPEEDS = ("0.5", "0.75", "1", "1.25", "1.5", "2.5")


def rate_map(length, schedule):
    """Map half-open source ranges to output ranges with one cumulative clock."""
    if type(length) is not int or length <= 0 or not schedule:
        raise ValueError("expected nonempty content and schedule")
    previous = -1
    for offset, speed in schedule:
        if (type(offset) is not int or not previous < offset < length
                or offset % HOP or speed not in SPEEDS):
            raise ValueError("invalid rate change")
        previous = offset
    if schedule[0][0] != 0:
        raise ValueError("schedule must begin at source sample zero")
    clock = Fraction(0)
    out = 0
    spans = []
    for (start, speed), (end, _) in pairwise([*schedule, (length, None)]):
        clock += Fraction(end - start) / Fraction(speed)
        next_out = round(clock)
        spans.append({"source": [start, end], "output": [out, next_out], "rate": speed})
        out = next_out
    return spans, clock


def linear_control(samples, spans):
    """Deliberately pitch-changing interpolation, not a time-stretch candidate."""
    if not samples or any(not math.isfinite(value) for value in samples):
        raise ValueError("expected finite samples")
    output = []
    for span in spans:
        start, end = span["source"]
        left, right = span["output"]
        width = right - left
        for index in range(width):
            whole, remainder = divmod(index * (end - start), width)
            at = start + whole
            a, b = samples[at], samples[min(at + 1, end - 1)]
            output.append(a if not remainder else a + (b - a) * remainder / width)
    return output


def crossings(samples):
    return sum(a <= 0 < b for a, b in pairwise(samples))


def observe(samples, schedule, transient=None):
    spans, exact_length = rate_map(len(samples), schedule)
    output = linear_control(samples, spans)
    result = {
        "mapping": spans,
        "duration": {"samples": len(output), "ideal_samples": str(exact_length),
                     "error_samples": str(len(output) - exact_length)},
        "final_partial_source_samples": len(samples) % HOP,
        "positive_crossings": {"source": crossings(samples), "output": crossings(output)},
        "peak_abs": round(max(map(abs, output), default=0.0), 8),
        "identity": list(samples) == output,
    }
    if transient is not None:
        result["impulse"] = {
            "source_sample": transient,
            "output_peak_sample": max(range(len(output)), key=lambda i: abs(output[i])),
            "nonzero_output_samples": sum(value != 0 for value in output),
            "audibility": "not_measured",
        }
    return result


def buffer_control():
    """Simulated arrivals, explicitly not a runtime timing measurement."""
    queue = rendered = rebuffer = peak = 0
    for arrival, demand in ((160, 160), (0, 160), (240, 160), (80, 160)):
        queue += arrival
        peak = max(peak, queue)
        take = min(queue, demand)
        queue -= take
        rendered += take
        rebuffer += demand - take
    return {"rendered_samples": rendered, "rebuffer_samples": rebuffer,
            "peak_queue_samples": peak, "tail_samples": queue}


def build_report():
    # Binary-exact triangles avoid platform libm differences at zero crossings.
    def triangle(i, period):
        return (period - 4 * abs(i % period - period // 2)) / 64

    tone = [triangle(i, 40) for i in range(16_003)]
    chord = [0.5 * value + 0.25 * triangle(i, 28)
             for i, value in enumerate(tone)]
    impulse = [0.0] * 323
    impulse[160] = 1.0
    cases = {speed: observe(tone, [(0, speed)]) for speed in SPEEDS}
    # Estimate F0 from positive crossings per rendered second, not listening.
    for case in cases.values():
        case["output_pitch_proxy_hz"] = round(
            RATE * case["positive_crossings"]["output"] / case["duration"]["samples"], 3)
    changes = [(i * HOP, ("0.75", "1.5", "2.5")[i % 3]) for i in range(100)]
    changed = observe(chord, changes)
    return {
        "task_id": "SDK-BUNGEE-BASIC",
        "base_commit": "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d",
        "profile": "rate",
        "status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "no_missing_result_qualifies_candidate": True,
        "boundary": {"registered": False, "enabled_by_default": False, "descriptor_settings": {},
                     "sdk_callback_invoked": False, "public_v0_geometry": [RATE, 1, "f32", HOP]},
        "native_bungee": {"invoked": False, "parity": "not_run", "license_context": "MPL-2.0"},
        "controls": {"linear_pitch_changing": cases, "music_proxy_rate_changes": changed,
                     "silence": observe([0.0] * 323, [(0, "1.25")]),
                     "impulse": observe(impulse, [(0, "0.5")], 160),
                     "buffer_simulation": buffer_control()},
        "regressions": [
            {"rate": speed, "control": "linear_pitch_changing", "pitch_preserving": False,
             "output_pitch_proxy_hz": case["output_pitch_proxy_hz"]}
            for speed, case in cases.items() if speed != "1"
        ],
        "blocked_gates": {
            "native_reference": "Pin and independently verify an approved Bungee build and assets.",
            "speech_and_music": "Run a rights-cleared unfamiliar speech and music cohort.",
            "transient_audibility": "Run cleared listening; impulse spread alone is insufficient.",
            "paced_playback": "Measure playback buffering, rebuffer and drift on the target runtime.",
            "provider_intake": "Review licensing and a separate opt-in boundary before registration.",
        },
    }


def canonical_report_bytes(report):
    return (json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
            + "\n").encode("utf-8")
