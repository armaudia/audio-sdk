# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Synthetic, deterministic 16 kHz mono float32 frames and ABI-mutation cases.

Everything is generated from an integer seed. No recording, model, network
resource, device or licensed runtime is used.  The coefficients are exactly
representable binary fractions so the same bytes are produced by the Python
model and the task-local C harness.
"""

from __future__ import annotations

import struct
from typing import Dict, List, Tuple

RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SEED = 20261124
PROVIDER_ID = "speex.ns.v0"
UNKNOWN_PROVIDER_ID = "no.such.provider.v0"
DENOMINATOR = 8192

_M64 = 0xFFFFFFFFFFFFFFFF
_FNV_OFFSET = 0xCBF29CE484222325
_FNV_PRIME = 0x100000001B3

# case_id, kind, mutation, create status, process status (None = no process call)
_SPECS: Tuple[Tuple[str, str, str, str, str | None], ...] = (
    ("valid_full_frame", "valid", "none", "OK", "OK"),
    ("assets_omitted", "missing_optional", "assets_null_count_zero", "OK", "OK"),
    ("partial_final_frame", "valid", "valid_count_80_final", "OK", "OK"),
    ("malformed_struct_tag", "malformed", "abi_major_1", "OK", "INVALID_ARGUMENT"),
    ("wrong_input_count", "malformed", "input_count_159", "OK", "INVALID_ARGUMENT"),
    ("partial_without_final", "malformed", "valid_count_80_no_final", "OK", "INVALID_ARGUMENT"),
    ("nonfinite_input", "nonfinite", "sample_20_nan", "OK", "INVALID_ARGUMENT"),
    ("missing_output_buffer", "missing_optional", "output_samples_null", "OK", "INVALID_ARGUMENT"),
    ("missing_provider_selection", "missing_optional", "provider_id_empty", "INVALID_ARGUMENT", None),
    ("missing_config_json", "missing_optional", "config_json_null", "INVALID_ARGUMENT", None),
    ("unknown_provider", "invalid", "unknown_provider_id", "UNSUPPORTED", None),
)


def coefficients() -> Tuple[int, ...]:
    """Return 160 deterministic integer coefficients in [-8192, 8191]."""
    state = SEED
    values: List[int] = []
    for _ in range(FRAME_SAMPLES):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append((state % (2 * DENOMINATOR)) - DENOMINATOR)
    return tuple(values)


def samples() -> Tuple[float, ...]:
    """Return the caller-owned float32 frame as exact binary fractions."""
    return tuple(value / float(DENOMINATOR) for value in coefficients())


def fnv1a64(data: bytes) -> int:
    value = _FNV_OFFSET
    for byte in data:
        value ^= byte
        value = (value * _FNV_PRIME) & _M64
    return value


def input_digest() -> str:
    """FNV-1a/64 over little-endian IEEE-754 bits of the generated frame."""
    value = _FNV_OFFSET
    for coefficient in coefficients():
        bits = struct.pack("<f", coefficient / float(DENOMINATOR))
        for byte in bits:
            value ^= byte
            value = (value * _FNV_PRIME) & _M64
    return f"{value:016x}"


def cases() -> List[Dict[str, object]]:
    """Return the frozen case table consumed by the model, scorer and report."""
    digest = input_digest()
    return [
        {
            "case_id": case_id,
            "kind": kind,
            "mutation": mutation,
            "expected_create_status": create_status,
            "expected_process_status": process_status,
            "input_digest": digest,
        }
        for case_id, kind, mutation, create_status, process_status in _SPECS
    ]


def fixture_pins() -> Dict[str, object]:
    return {
        "fixture_id": "c-raii-bindings-synthetic-v1",
        "sample_rate_hz": RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "seed": SEED,
        "denominator": DENOMINATOR,
        "sample_encoding": "binary fractions coeff/8192 as IEEE-754 float32",
        "input_digest": input_digest(),
        "digest_algorithm": "FNV-1a/64 over little-endian float32 bit patterns",
        "case_count": len(_SPECS),
    }
