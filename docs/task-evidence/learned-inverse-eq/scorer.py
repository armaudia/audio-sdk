# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Dependency-free deterministic metrics and strict JSON helpers for SDK-LEARNED-INVERSE-EQ.

Every number produced here is computed from synthetic, in-memory float
sequences.  This module is not a quality model, an audio-bench scorer, a
listening test or a release gate.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence


class StrictJSONError(ValueError):
    pass


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_json(value: Any) -> str:
    return digest_bytes(canonical_text(value).encode("utf-8"))


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _pairs(items: List[Any]) -> dict:
    result: dict = {}
    for key, value in items:
        if key in result:
            raise StrictJSONError("duplicate_json_key:" + str(key))
        result[key] = value
    return result


def _constant(token: str) -> None:
    raise StrictJSONError("nonfinite_json_constant:" + token)


def read_strict_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=_pairs, parse_constant=_constant)


def is_finite(values: Iterable[float]) -> bool:
    return all(math.isfinite(float(value)) for value in values)


def rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(float(value) ** 2 for value in values) / len(values))


def peak(values: Sequence[float]) -> float:
    return max((abs(float(value)) for value in values), default=0.0)


def finite_count(values: Sequence[float]) -> int:
    return sum(1 for value in values if math.isfinite(float(value)))


def safe_db(ratio: float, floor: float = 1e-12) -> Optional[float]:
    """Return a JSON-safe dB value; undefined ratios are reported as null."""
    if not math.isfinite(ratio) or ratio <= floor:
        return None
    return 20.0 * math.log10(ratio)


def gain_db(output: Sequence[float], reference: Sequence[float]) -> Optional[float]:
    if len(output) != len(reference) or not reference:
        return None
    return safe_db(rms(output) / max(rms(reference), 1e-12))


def snr_db(signal: Sequence[float], noise: Sequence[float]) -> Optional[float]:
    if len(signal) != len(noise) or not signal:
        return None
    return safe_db(rms(signal) / max(rms(noise), 1e-12))


def headroom_db(values: Sequence[float]) -> Optional[float]:
    """dB below full scale; a silent sequence has no finite headroom."""
    return safe_db(1.0 / max(peak(values), 1e-12))


def count_clipped(values: Sequence[float], threshold: float = 1.0) -> int:
    return sum(1 for value in values if abs(float(value)) >= threshold)


def max_abs_error(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    if len(a) != len(b) or not a:
        return None
    return max(abs(float(x) - float(y)) for x, y in zip(a, b))


def response_rmse_db(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    if len(a) != len(b) or not a:
        return None
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)) / len(a))


def delay_samples(reference: Sequence[float], output: Sequence[float],
                  max_lag: int = 48) -> int:
    """Lag maximizing zero-padded cross-correlation; 0 means no added delay."""
    if not reference or not output:
        return 0
    best_lag, best_score = 0, -math.inf
    for lag in range(-max_lag, max_lag + 1):
        score = 0.0
        for index in range(len(reference)):
            other = index + lag
            if 0 <= other < len(output):
                score += float(reference[index]) * float(output[other])
        if score > best_score:
            best_lag, best_score = lag, score
    return best_lag


def round_float(value: Optional[float], digits: int = 12) -> Optional[float]:
    if value is None or not math.isfinite(float(value)):
        return None
    return round(float(value), digits)
