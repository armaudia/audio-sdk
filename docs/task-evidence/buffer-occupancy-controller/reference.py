# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Fixed-point live playback rate law and virtual FIFO, without PCM or I/O."""

from fractions import Fraction

HZ = 16_000
BLOCK = 160
TARGET = 3_200
CAPACITY = 9_600
UNITY = 1_000_000
LIMIT = 50_000  # ±5%, in rate ppm
SLEW = 5_000 * BLOCK // HZ  # 0.5 percentage points/s, in ppm per 10 ms
GAIN = 250_000  # Kp = 1/4
TRACE_FIELDS = {"source_samples", "source_drift_ppm", "hold_start_tick", "hold_ticks"}


def rate_ppm(queued, previous):
    """queued is in millionths of a source sample; return speed, not its reciprocal."""
    correction = GAIN * (queued - TARGET * UNITY) // (TARGET * UNITY)
    goal = UNITY + max(-LIMIT, min(LIMIT, correction))
    return max(previous - SLEW, min(previous + SLEW, goal))


def replay(trace, controller):
    if not isinstance(trace, dict) or set(trace) != TRACE_FIELDS:
        raise ValueError("invalid_trace_fields")
    if any(type(value) is not int for value in trace.values()):
        raise ValueError("integer_trace_values_required")
    total, drift, hold_at, hold_for = (
        trace[key] for key in ("source_samples", "source_drift_ppm", "hold_start_tick", "hold_ticks")
    )
    if not (1 <= total <= HZ * 30 and -200_000 <= drift <= 200_000
            and 0 <= hold_for <= 200):
        raise ValueError("trace_bounds")
    if (not hold_for and hold_at != 0) or (hold_for and not (
            0 <= hold_at and hold_at * BLOCK * (UNITY + drift) // UNITY < total)):
        raise ValueError("invalid_hold_interval")

    source = accepted = rejected = previous_arrival = rebuffer_count = 0
    rate = UNITY
    started = playing = False
    rows = []
    for tick in range(2 * ((total + BLOCK - 1) // BLOCK) + hold_for + 2):
        playout = tick * BLOCK
        # Arrivals are visible at the start of a virtual playout period. A hold
        # delays delivery, not production; release makes the backlog visible.
        scheduled = min(total, (tick + 1) * BLOCK * (UNITY + drift) // UNITY)
        arrival = previous_arrival if hold_at <= tick < hold_at + hold_for else scheduled
        incoming = arrival - previous_arrival
        previous_arrival = arrival
        queued = arrival * UNITY - source
        if queued > CAPACITY * UNITY:
            rejected = incoming
            rows.append({"state": "overflow", "playout_start": playout,
                         "source_start_usamples": source, "arrivals": incoming})
            break

        accepted = arrival
        eos = accepted == total
        if not playing:
            playing = queued >= TARGET * UNITY or eos
        if playing:
            # Apply only emitted commands; during a gap hold the last rate.
            requested = rate_ppm(queued, rate) if controller else UNITY
            needed = BLOCK * requested
            if queued >= needed or eos:
                consumed = min(queued, needed)
                duration = Fraction(consumed, requested)
                rows.append({
                    "state": "play", "playout_start": playout, "playout_duration": str(duration),
                    "source_start_usamples": source, "source_end_usamples": source + consumed,
                    "rate_ppm": requested, "queued_usamples": queued, "accepted_samples": accepted,
                })
                source += consumed
                rate = requested
                started = True
                if source == total * UNITY:
                    break
                continue
            playing = False
            rebuffer_count += int(started)
        rows.append({"state": "rebuffer" if started else "prefill", "playout_start": playout,
                     "source_start_usamples": source, "queued_usamples": queued,
                     "accepted_samples": accepted})
    return {
        "status": ("overflow" if rejected else "rebuffered" if source == total * UNITY and rebuffer_count
                   else "complete" if source == total * UNITY else "tick_limit"),
        "accepted_samples": accepted, "consumed_usamples": source,
        "rejected_arrival_samples": rejected, "rebuffer_count": rebuffer_count, "timeline": rows,
    }
