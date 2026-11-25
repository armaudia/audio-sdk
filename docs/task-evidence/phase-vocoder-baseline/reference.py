# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Offline phase vocoder and controls on the existing elastic PCM fixture."""

from cmath import exp, phase
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from math import cos, isfinite, remainder, tau
from pathlib import Path
from struct import pack, unpack
import sys


def _elastic_fixture():
    path = Path(__file__).resolve().parents[1] / "elastic-pcm-packets" / "fixture.py"
    spec = spec_from_file_location("_sdk_elastic_pcm_fixture", path)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


elastic = _elastic_fixture()
Status = elastic.Status
WINDOW, HOP, CAPACITY = 1024, 256, 32768
HALF = WINDOW // 2
HANN = tuple(0.5 - 0.5 * cos(tau * i / WINDOW) for i in range(WINDOW))
TWIDDLES = tuple(exp(-1j * tau * i / WINDOW) for i in range(HALF))
BIT_REVERSE = tuple(int(f"{i:010b}"[::-1], 2) for i in range(WINDOW))


def fft(values, inverse=False):
    """Fixed-size radix-2 FFT; inverse includes the 1/N scale."""
    bins = [values[i] for i in BIT_REVERSE]
    width = 2
    while width <= WINDOW:
        half = width // 2
        for j in range(half):
            w = TWIDDLES[j * (WINDOW // width)]
            if inverse:
                w = w.conjugate()
            for a in range(j, WINDOW, width):
                b = a + half
                t = w * bins[b]
                bins[a], bins[b] = bins[a] + t, bins[a] - t
        width *= 2
    return [value / WINDOW for value in bins] if inverse else bins


def phase_vocoder(samples, ratio, count):
    if not count:
        return ()
    out, weights = [0.0] * count, [0.0] * count
    prev_center, prev_angles, synthesis = None, None, None
    for center in range(0, count + HOP - 1, HOP):
        source_center = round(center * ratio)
        start = source_center - HALF
        spectrum = fft([w * samples[start + i] if 0 <= start + i < len(samples) else 0.0
                        for i, w in enumerate(HANN)])
        angles = [phase(z) for z in spectrum[:HALF + 1]]
        if prev_center is None:
            synthesis = angles.copy()
        else:
            analysis_hop = source_center - prev_center
            for k, angle in enumerate(angles):
                omega = tau * k / WINDOW
                residual = remainder(angle - prev_angles[k] - omega * analysis_hop, tau)
                synthesis[k] = remainder(synthesis[k] + (omega + residual / analysis_hop) * HOP, tau)
        prev_center, prev_angles = source_center, angles
        positive = [abs(spectrum[k]) * exp(1j * p) for k, p in enumerate(synthesis)]
        positive[0], positive[-1] = positive[0].real, positive[-1].real
        frame = fft(positive + [z.conjugate() for z in positive[-2:0:-1]], inverse=True)
        for i in range(max(0, HALF - center), min(WINDOW, count + HALF - center)):
            j = center - HALF + i
            out[j] += frame[i].real * HANN[i]
            weights[j] += HANN[i] ** 2
    return tuple(y / w for y, w in zip(out, weights, strict=True))


def varispeed(samples, ratio, count):
    out = []
    for i in range(count):
        index, frac = divmod(i * ratio.numerator, ratio.denominator)
        following = samples[min(index + 1, len(samples) - 1)]
        out.append(samples[index] + (following - samples[index]) * (frac / ratio.denominator))
    return tuple(out)


def f32(value):
    return unpack("<f", pack("<f", value))[0]


class OfflineComparison:
    """Whole-clip adapter: admit timestamped rate regions, render atomically at EOS.

    The elastic fixture owns source mapping, queue bounds, counts and pull/EOS.
    Its nearest-sample render is not the comparison audio.
    """

    def __init__(self, method):
        if method not in ("phase-vocoder", "identity", "varispeed"):
            raise ValueError("unknown comparison method")
        self._method = method
        self._clock = elastic.ElasticStream(method, max_queued_samples=CAPACITY)
        self._regions = []
        self._output = ()
        self._failed = False

    def push(self, chunk, ratio):
        if self._clock.eos or self._failed:
            return Status.CLOSED
        if (not isinstance(chunk, elastic.PcmChunk) or type(chunk.source_start) is not int
                or not isinstance(chunk.samples, tuple) or not chunk.samples
                or chunk.source_start != self._clock.consumed_count):
            return Status.REJECTED_SOURCE_GAP
        if len(chunk.samples) + self._clock.consumed_count > CAPACITY:
            return Status.REJECTED_BACKPRESSURE
        if any(type(x) not in (int, float) or not -1 <= x <= 1 for x in chunk.samples):
            return Status.REJECTED_SOURCE_GAP
        if not isinstance(ratio, (str, Fraction)):
            return Status.REJECTED_RATIO
        try:
            ratio = Fraction(ratio)
        except (ValueError, ZeroDivisionError):
            return Status.REJECTED_RATIO
        if not Fraction(3, 4) <= ratio <= Fraction(3, 2) or (self._method == "identity" and ratio != 1):
            return Status.REJECTED_RATIO
        self._clock.set_ratio(ratio)
        pcm = tuple(map(f32, chunk.samples))
        status = self._clock.push(elastic.PcmChunk(chunk.source_start, pcm))
        if status == Status.OK:
            self._regions.append((pcm, ratio))
        return status

    def flush(self):
        if self._failed:
            return Status.CLOSED
        if self._clock.eos:
            return Status.OK
        self._failed = True  # never expose partial results if any region fails
        output = []
        for samples, ratio in self._regions:
            count = len(samples) // ratio
            if self._method == "phase-vocoder":
                rendered = phase_vocoder(samples, ratio, count)
            elif self._method == "varispeed":
                rendered = varispeed(samples, ratio, count)
            else:
                rendered = samples
            if len(rendered) != count or any(not isfinite(x) or abs(x) > 1 for x in rendered):
                raise ValueError("invalid render: missing samples, nonfinite samples or clipping")
            output.extend(map(f32, rendered))
        self._output = tuple(output)
        self._clock.flush()
        self._failed = False
        return Status.OK

    def pull(self, limit):
        if type(limit) is not int or limit < 1:
            raise ValueError("positive integer pull capacity required")
        if self._failed or not self._clock.eos:
            status = Status.CLOSED if self._failed else Status.NOT_READY
            return elastic.PullResult(status, (), (), self._clock.consumed_count, 0)
        result = self._clock.pull(limit)
        end = result.produced_count
        return elastic.PullResult(result.status, self._output[end - len(result.samples):end],
                                  result.source_indices, result.consumed_count, end)
