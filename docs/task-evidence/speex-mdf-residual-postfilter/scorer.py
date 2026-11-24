# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Pinned local scorer for the synthetic paired render/capture evidence.

The scorer is intentionally simple and finite: echo attenuation (ERLE), two
near-end preservation windows, peak and nonfinite count. Every field is
computed from the exact CLI output bytes; no tolerance is widened and no
missing result is filled in.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

import fixture

SCORER_ID = "audio-sdk/speex-mdf-residual-postfilter-scorer/0.1"


def score(output: Sequence[float], capture: Sequence[float],
          near: Sequence[float]) -> dict[str, Any]:
    """Score one deterministic CLI output against its paired streams."""
    converged = fixture.window(fixture.CONVERGED_FRAMES)
    overlap = fixture.window(fixture.NEAR_BURST_FRAMES)
    near_only = fixture.window(fixture.NEAR_ONLY_WINDOW_FRAMES)
    return {
        "erle_db_converged": fixture.round6(
            fixture.erle_db(capture, output, *converged)),
        "near_ratio_overlap": fixture.round6(
            fixture.rms_ratio(output, near, *overlap)),
        "near_attenuation_db_near_only": fixture.round6(
            fixture.attenuation_db(output, near, *near_only)),
        "peak": fixture.round6(max(abs(value) for value in output)),
        "nonfinite_count": sum(1 for value in output if not math.isfinite(value)),
        "duration_samples": len(output),
    }


def delta(baseline: float, candidate: float) -> float:
    """Exact rounded difference; negative near-end delta means damage."""
    return fixture.round6(candidate - baseline)


def metadata() -> dict[str, Any]:
    return {
        "scorer_id": SCORER_ID,
        "erle_window_frames": list(fixture.CONVERGED_FRAMES),
        "near_overlap_window_frames": list(fixture.NEAR_BURST_FRAMES),
        "near_only_window_frames": list(fixture.NEAR_ONLY_WINDOW_FRAMES),
        "missing_result_policy": "withhold; never impute or tolerance-widen",
    }
