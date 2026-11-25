"""Offline replay of synthetic CoreAudio-style capture/render callback slices."""

import argparse
from bisect import bisect_right
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path


TOOL = "audio-sdk/coreaudio-audiounit-duplex-replay/0.1"
FRAME = 480
DELAY_NS = 20_000_000
MAX_SLICES = 64
MAX_SLICE = 4096


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"expected integer in [{low}, {high}]")
    return value


@dataclass(frozen=True)
class Slice:
    first: int
    count: int
    arrival_ns: int
    timestamp_offset_ns: int

    @property
    def end(self):
        return self.first + self.count


@dataclass(frozen=True)
class Trace:
    origin_ns: int
    rate_ppm: int
    slices: tuple[Slice, ...]

    @property
    def ns_per_sample(self):
        return Fraction(10**15, 48_000 * (1_000_000 + self.rate_ppm))

    def discontinuity(self):
        for index, item in enumerate(self.slices):
            if item.timestamp_offset_ns != 0:
                return {"slice": index, "reason": "timestamp_jump"}
            if index:
                previous = self.slices[index - 1]
                if item.first != previous.end:
                    return {"slice": index, "reason": "gap" if item.first > previous.end else "overlap"}
                if item.arrival_ns < previous.arrival_ns:
                    return {"slice": index, "reason": "arrival_regression"}
        return None


def parse_trace(doc):
    if not isinstance(doc, dict) or doc.keys() != {"origin_ns", "rate_ppm", "slices"}:
        raise ValueError("trace requires origin_ns, rate_ppm and slices")
    rows = doc["slices"]
    if not isinstance(rows, list) or len(rows) > MAX_SLICES:
        raise ValueError(f"slices must be a list of at most {MAX_SLICES} rows")
    slices = []
    for row in rows:
        if not isinstance(row, list) or len(row) != 4:
            raise ValueError("slice requires [first, count, arrival_ns, timestamp_offset_ns]")
        first, count, arrival, offset = row
        slices.append(Slice(integer(first, 0, 2**31 - MAX_SLICE),
                            integer(count, 1, MAX_SLICE),
                            integer(arrival, 0, 2**63 - 1),
                            integer(offset, -10**9, 10**9)))
    return Trace(integer(doc["origin_ns"], 0, 2**63 - 1),
                 integer(doc["rate_ppm"], -1000, 1000), tuple(slices))


def ramp(position):
    return Fraction(position % 2048 - 1024, 1024)


def reference_digest(positions):
    # Rational text makes the interpolated synthetic signal reproducible across hosts.
    samples = []
    for position in positions:
        index = math.floor(position)
        weight = position - index
        value = ramp(index)
        if weight:
            value += weight * (ramp(index + 1) - value)
        samples.append(str(value))
    return hashlib.sha256("\n".join(samples).encode("ascii")).hexdigest()


def replay(capture, render):
    report = {"tool": TOOL, "evidence": "synthetic_replay_only",
              "frame_samples": FRAME, "model_delay_ns": str(DELAY_NS),
              "frames": [], "capture_tail_samples": 0}
    capture_fault = capture.discontinuity()
    if capture_fault or not capture.slices:
        report["capture_fault"] = capture_fault or {"reason": "missing_capture"}
        return report
    starts = [item.first for item in capture.slices]
    end = capture.slices[-1].end
    report["capture_tail_samples"] = (end - starts[0]) % FRAME
    render_fault = render.discontinuity() if render else None
    if render_fault:
        report["render_fault"] = render_fault
    render_starts = [item.first for item in render.slices] if render else []
    if render_starts and not render_fault:
        start = Fraction(capture.origin_ns - DELAY_NS - render.origin_ns) / render.ns_per_sample
        step = capture.ns_per_sample / render.ns_per_sample
    for first in range(starts[0], end - FRAME + 1, FRAME):
        last = first + FRAME - 1
        deadline = capture.slices[bisect_right(starts, last) - 1].arrival_ns
        frame = {"capture_interval": [str(first), str(last + 1)],
                 "capture_ready_ns": str(deadline), "status": "missing_reference"}
        if render_fault:
            frame["status"] = "discontinuous_reference"
        elif render_starts:
            low, high = start + first * step, start + last * step
            needed_first, needed_last = math.floor(low), math.ceil(high)
            frame["render_positions"] = [str(low), str(high)]
            if render_starts[0] <= needed_first and needed_last < render.slices[-1].end:
                # A contiguous trace with nondecreasing arrivals is available
                # only when the callback containing its last required sample arrives.
                available = render.slices[bisect_right(render_starts, needed_last) - 1].arrival_ns
                frame["reference_ready_ns"] = str(available)
                if available > deadline:
                    frame["status"] = "late_reference"
                else:
                    frame["status"] = "paired"
                    frame["reference_sha256"] = reference_digest(low + i * step for i in range(FRAME))
        report["frames"].append(frame)
    return report


def unique_object(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON keys")
    return obj


def load_trace(path):
    with path.open("rb") as stream:
        raw = stream.read(65_537)
    if len(raw) > 65_536:
        raise ValueError("trace exceeds 64 KiB")
    trace = parse_trace(json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object))
    return trace, hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=TOOL)
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--render", type=Path, help="omit to replay missing reference")
    args = parser.parse_args()

    def read(role, path):
        try:
            return load_trace(path)
        except (OSError, ValueError, RecursionError) as exc:
            parser.error(f"{role} trace: {exc}")

    capture, capture_hash = read("capture", args.capture)
    render, render_hash = read("render", args.render) if args.render is not None else (None, None)
    report = replay(capture, render)
    report["input_sha256"] = {"capture": capture_hash, "render": render_hash}
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
