# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Independent frozen-window scoring for the synthetic room evidence.

Scoring uses the synthetic near-end ground truth, which is never supplied to
the processor.  A result is descriptive only: no threshold here qualifies a
candidate for release, and missing or blocked cases are never promoted.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Iterable, Sequence

from fixture import WINDOWS

DB_FLOOR = 1e-20


def digest(values: Iterable[float]) -> str:
    payload = json.dumps([float(value) for value in values], sort_keys=True,
                         separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def finite_count(values: Iterable[float]) -> int:
    return sum(1 for value in values if math.isfinite(value))


def peak_abs(values: Iterable[float]) -> float:
    return max((abs(value) for value in values if math.isfinite(value)), default=0.0)


def energy(values: Sequence[float], start: int, end: int) -> float:
    if not 0 <= start < end <= len(values):
        raise ValueError("invalid_scoring_window")
    return sum(float(value) * float(value) for value in values[start:end])


def db(ratio: float) -> float:
    if not math.isfinite(ratio) or ratio <= 0.0:
        ratio = DB_FLOOR
    return 10.0 * math.log10(ratio)


def erle(microphone: Sequence[float], output: Sequence[float],
         window: str = "echo_only_early") -> float:
    start, end = WINDOWS[window]
    before = energy(microphone, start, end)
    after = energy(output, start, end)
    if after <= 0.0:
        after = DB_FLOOR
    return db(before / after)


def near_snr(near: Sequence[float], output: Sequence[float],
             window: str) -> float:
    start, end = WINDOWS[window]
    target = energy(near, start, end)
    error = sum((float(output[index]) - float(near[index])) ** 2
                for index in range(start, end))
    if error <= 0.0:
        error = DB_FLOOR
    return db(target / error)


def overlap_near_snr(near: Sequence[float], output: Sequence[float]) -> float:
    """Pooled near-end preservation over the two frozen overlap windows."""
    target = 0.0
    error = 0.0
    for window in ("overlap_early", "overlap_late"):
        start, end = WINDOWS[window]
        for index in range(start, end):
            target += float(near[index]) ** 2
            error += (float(output[index]) - float(near[index])) ** 2
    if error <= 0.0:
        error = DB_FLOOR
    return db(target / error)


def alignment_lag(render: Sequence[float], microphone: Sequence[float],
                  window: str = "echo_only_early", max_lag: int = 64) -> int:
    """Best non-negative render-to-capture lag by normalized cross-correlation."""
    start, end = WINDOWS[window]
    best_lag = -1
    best_score = -1.0
    for lag in range(max_lag + 1):
        cross = 0.0
        render_energy = 0.0
        count = 0
        for index in range(start, end):
            played = float(render[index - lag]) if index >= lag else 0.0
            cross += played * float(microphone[index])
            render_energy += played * played
            count += 1
        if render_energy <= 0.0 or count == 0:
            continue
        score = cross / math.sqrt(render_energy * count)
        if score > best_score:
            best_score = score
            best_lag = lag
    return best_lag


def summarize(microphone: Sequence[float], output: Sequence[float],
              near: Sequence[float], render: Sequence[float],
              reference: Sequence[float] | None = None) -> dict[str, Any]:
    """All descriptive room metrics for one already-processed stream.

    ``alignment_lag_samples`` is measured between the supplied render/reference
    stream and microphone over the early echo-only window; it is a fixture
    alignment measurement, not device/buffering timing.
    """
    alignment_source = render if reference is None else reference
    return {
        "erle_early_db": round(erle(microphone, output, "echo_only_early"), 6),
        "erle_late_db": round(erle(microphone, output, "echo_only_late"), 6),
        "near_snr_near_only_early_db": round(
            near_snr(near, output, "near_only_early"), 6),
        "near_snr_near_only_late_db": round(
            near_snr(near, output, "near_only_late"), 6),
        "near_snr_overlap_db": round(overlap_near_snr(near, output), 6),
        "alignment_lag_samples": alignment_lag(alignment_source, microphone),
        "nonfinite_count": len(output) - finite_count(output),
        "peak_abs": round(peak_abs(output), 9),
        "output_sha256": digest(output),
    }
