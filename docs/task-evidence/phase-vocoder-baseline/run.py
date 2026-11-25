# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Run the frozen synthetic rate comparison; print a report or check its bytes."""

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from math import isfinite, sin, tau
from pathlib import Path

from reference import OfflineComparison, Status, elastic, f32

HERE = Path(__file__).resolve().parent
FS, N, TONE = elastic.SAMPLE_RATE_HZ, 8197, 437
RATES = ("3/4", "1", "5/4", "3/2")
METHODS = ("phase-vocoder", "varispeed")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def render(method, samples, schedule):
    require(bool(samples) and bool(schedule), "missing stimulus or rate schedule")
    stream = OfflineComparison(method)
    count, start = 0, 0
    regions = []
    for end, rate in schedule:
        require(start < end <= len(samples), "invalid source interval")
        status = stream.push(elastic.PcmChunk(start, samples[start:end]), rate)
        require(status == Status.OK, f"input refused: {status}")
        ratio = Fraction(rate)
        next_count = count + (end - start) // ratio
        regions.append({"source": [start, end], "output": [count, next_count], "rate": rate})
        count, start = next_count, end
    require(start == len(samples), "missing source tail")
    before = stream.pull(160)
    require(before == elastic.PullResult(Status.NOT_READY, (), (), start, 0),
            "output or invalid counts before flush")
    require(stream.flush() == Status.OK, "flush failed")
    out, source, chunk_sizes = [], [], []
    for _ in range((count + 159) // 160 + 1):
        pulled = stream.pull(160)
        if pulled.status == Status.END_OF_STREAM:
            break
        require(pulled.status == Status.OK and 1 <= len(pulled.samples) <= 160,
                "invalid pull during drain")
        out.extend(pulled.samples)
        source.extend(pulled.source_indices)
        chunk_sizes.append(len(pulled.samples))
        require(pulled.consumed_count == start and pulled.produced_count == len(out),
                "invalid pull accounting")
    eos = elastic.PullResult(Status.END_OF_STREAM, (), (), start, count)
    require(pulled == eos and stream.flush() == Status.OK and stream.pull(160) == eos,
            "no stable, bounded EOS")
    expected_map = [region["source"][0] + i * Fraction(region["rate"]) // 1
                    for region in regions for i in range(region["output"][1] - region["output"][0])]
    require(source == expected_map and len(out) == count and all(isfinite(x) for x in out),
            "incomplete, nonfinite or unmapped render")
    ideal = sum(Fraction(r["source"][1] - r["source"][0]) / Fraction(r["rate"]) for r in regions)
    data = {"regions": regions, "output_samples": count, "duration_error_samples": str(count - ideal),
            "first_output_admitted_samples": start, "pending_at_flush_samples": count,
            "drain_pulls_with_data": len(chunk_sizes), "final_pull_samples": chunk_sizes[-1] if out else 0}
    return out, data


def tone_frequency(samples):
    middle = samples[1024:-1024]
    crossing = [i - a / (b - a) for i, (a, b) in enumerate(zip(middle, middle[1:]))
                if a <= 0 < b]
    require(len(crossing) > 2, "missing measurable tone")
    return (len(crossing) - 1) * FS / (crossing[-1] - crossing[0])


def impulse(index):
    return tuple(0.25 if i == index else 0.0 for i in range(N))


def transient(samples, ideal_index):
    energy = [x * x for x in samples]
    total = sum(energy)
    require(isfinite(total) and total > 0, "missing transient energy")
    peak = max(range(len(samples)), key=energy.__getitem__)
    cumulative, low, high = 0.0, None, None
    for i, e in enumerate(energy):
        cumulative += e
        if low is None and cumulative >= 0.05 * total:
            low = i
        if cumulative >= 0.95 * total:
            high = i
            break
    require(low is not None and high is not None, "incomplete transient energy")
    return {
        "peak_offset_samples": peak - ideal_index,
        "central_90pct_energy_width_samples": high - low + 1,
        "energy_outside_ideal_plus_minus_16_samples":
            round(sum(e for i, e in enumerate(energy) if abs(i - ideal_index) > 16) / total, 6),
    }


def report():
    tone = tuple(f32(0.2 * sin(tau * TONE * i / FS)) for i in range(N))
    identity, _ = render("identity", tone, [(N, "1")])
    require(tuple(identity) == tone, "identity changed input")
    pulse = impulse(4080)  # maps to an integer at every frozen test rate
    baseline, _ = render("identity", pulse, [(N, "1")])
    control = transient(baseline, 4080)
    require(control["central_90pct_energy_width_samples"] == 1
            and control["peak_offset_samples"] == 0, "bad identity transient control")

    rows = []
    for rate in RATES:
        ratio = Fraction(rate)
        for method in METHODS:
            schedule = [(N, rate)]
            out, timing = render(method, tone, schedule)
            hz = tone_frequency(out)
            expected = TONE * (ratio if method == "varispeed" else 1)
            require(abs(hz - expected) < 1, f"{method} {rate}: pitch check failed")
            if rate == "1":
                require(max(abs(x - y) for x, y in zip(out, identity, strict=True)) < 1e-6,
                        f"{method}: 1x reconstruction failed")
            attack, _ = render(method, pulse, schedule)
            onset = transient(attack, 4080 // ratio)
            rows.append({"method": method, "rate": rate, "tone_hz": round(hz, 4),
                         "pitch_shift_adverse_control": method == "varispeed" and rate != "1",
                         "transient": onset, "transient_spread_vs_identity":
                             onset["central_90pct_energy_width_samples"] > 1,
                         **timing})

    edges = {}
    for name, index in (("start", 0), ("tail", N - 1)):
        # The final source sample may map past the floor-trimmed output end.
        out, _ = render("phase-vocoder", impulse(index), [(N, "5/4")])
        edges[name] = transient(out, min(index // Fraction("5/4"), len(out) - 1))
    changed, stepped = render("phase-vocoder", tone, [(3200, "1"), (6400, "5/4"), (N, "3/4")])
    stepped["seam_sample_steps"] = [
        round(abs(changed[i] - changed[i - 1]), 6)
        for i in (r["output"][0] for r in stepped["regions"][1:])
    ]
    silence, _ = render("phase-vocoder", (0.0,) * 161, [(161, "3/4")])
    require(silence == [0.0] * 214, "silence or partial tail changed")
    require(any(r["transient_spread_vs_identity"] and r["method"] == "phase-vocoder" for r in rows),
            "missing expected phase-vocoder transient failure")
    return {"boundary": elastic.CONTRACT_ID, "protocol_version": 1,
            "scope": "offline synthetic fixture only", "decision": "defer",
            "candidate_qualified": False, "sample_rate_hz": FS, "input_samples": N,
            "source_tone_hz": TONE, "identity_transient": control, "constant_rate": rows,
            "edge_transients_at_5/4": edges, "rate_step": stepped, "silence_output_samples": len(silence),
            "omitted": ["held-out speech and music", "listening and speech preservation", "device clocks and drift",
                        "paced rebuffer recovery", "resource, deadline and playback availability qualification"]}


def verify_pins(manifest, root):
    pins = (HERE / manifest).read_text().splitlines()
    require(bool(pins), f"empty manifest: {manifest}")
    for line in pins:
        expected, name = line.split("  ", 1)
        require(sha256((root / name).read_bytes()).hexdigest() == expected, f"source mismatch: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the committed report")
    parser.add_argument("--source-root", type=Path, help="also verify external research/plan source pins")
    args = parser.parse_args()
    verify_pins("BOUNDARY.sha256", HERE.parents[2])
    if args.source_root is not None:
        verify_pins("EVIDENCE.sha256", args.source_root)
    text = json.dumps(report(), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.check:
        require((HERE / "report.json").read_bytes() == text.encode("utf-8"), "report mismatch")
        print("verified:", sha256(text.encode("utf-8")).hexdigest())
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
