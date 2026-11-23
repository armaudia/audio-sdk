# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic caller-owned PCM fixture for the fixed v0 identity baseline.

The values are exact binary fractions (integer/128), so the same bytes are
produced by Python and by the installed C consumer. This module never opens
an SDK library; it defines only the synthetic input and canonical report form.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from typing import Any

SCHEMA_ID = "audio-sdk/task-evidence/identity-pcm-fixture/0.1"
BASE_COMMIT = "3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41"
PROVIDER_ID = "fixture.identity-pcm.v0"
CONTRACT_ID = "audio-sdk/descriptor/0.1"
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
FRAME_LENGTHS = (160, 160, 37)
FIRST_INPUT_SAMPLE = 9007199254740993  # 2**53 + 1; exact through int64/JSON.
GENERATOR = {
    "modulus": 101,
    "multiplier": 37,
    "frame_offset": 17,
    "offset": -50,
    "scale": 128,
}
SOURCE_PINS = {
    "cpp-library/src/stages/identity.cpp":
        "5fff7e319c32485a541fec5785fefb11ca0d9ad4139d77e7126c1cf963811a44",
    "adapters/controls/adapter.json":
        "3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599",
}


def sample(frame_index: int, position: int) -> float:
    """Return an exact k/128 float matching the C fixture generator."""
    raw = (position * GENERATOR["multiplier"]
           + frame_index * GENERATOR["frame_offset"]) % GENERATOR["modulus"]
    return (raw + GENERATOR["offset"]) / GENERATOR["scale"]


def accepted_samples() -> tuple[float, ...]:
    """Flatten the caller-owned stream, including the partial final frame."""
    values = [sample(frame, position)
              for frame, length in enumerate(FRAME_LENGTHS)
              for position in range(length)]
    if len(values) != sum(FRAME_LENGTHS):
        raise AssertionError("fixture length mismatch")
    if any(not math.isfinite(value) for value in values):
        raise AssertionError("fixture contains a nonfinite sample")
    return tuple(values)


def pcm_bytes(values: tuple[float, ...] | list[float]) -> bytes:
    """Little-endian float32 bytes, the exact bytes compared by memcmp in C."""
    return b"".join(struct.pack("<f", value) for value in values)


def payload() -> dict[str, Any]:
    """Return the full canonical fixture payload."""
    return {
        "schema_id": SCHEMA_ID,
        "base_commit": BASE_COMMIT,
        "provider_id": PROVIDER_ID,
        "contract_id": CONTRACT_ID,
        "format": {
            "sample_format": "f32",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
        },
        "first_input_sample": FIRST_INPUT_SAMPLE,
        "frame_lengths": list(FRAME_LENGTHS),
        "generator": dict(GENERATOR),
        "source_pins": dict(SOURCE_PINS),
        "samples": list(accepted_samples()),
    }


def canonical_json(value: Any) -> str:
    """Serialize with sorted keys, no whitespace and no NaN/Infinity."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_fixture() -> tuple[str, str]:
    text = canonical_json(payload())
    return text, digest(text)
