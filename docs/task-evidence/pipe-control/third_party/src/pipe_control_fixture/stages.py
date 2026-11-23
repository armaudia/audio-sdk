# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Installed third-party identity providers and recipe copies.

This package is built as a stdlib wheel and installed with pip --no-index. It
supplies caller-owned provider objects and frozen recipe bytes only. It has no
SDK linkage, weights, assets, downloads, real audio, device access or timing
measurement. The task reference executor supplies the session bookkeeping.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Mapping, Sequence

FIXTURE_ID = "third-party/pipe-control-fixture/0.1"
FIXTURE_VERSION = "0.1.0"

_FORMAT = {
    "channels": 1,
    "frame_samples": 160,
    "sample_format": "f32",
    "sample_rate_hz": 16000,
}


class IdentityStage:
    stage_id = "identity"
    role = "audio"
    delay_samples = 0
    cost_ns = 25000

    def transform(self, samples: Sequence[float], settings: Mapping[str, Any],
                  ctx: Mapping[str, Any]) -> tuple[float, ...]:
        if settings:
            raise ValueError("unsupported_settings")
        if len(samples) != 160:
            raise ValueError("bad_input_count")
        return tuple(struct.unpack("<f", struct.pack("<f", float(value)))[0]
                     for value in samples)


def installed_stages() -> dict[str, IdentityStage]:
    """Two independently registered providers for the planned switch/fallback."""
    return {
        "third_party.identity.v0": IdentityStage(),
        "third_party.fallback_identity.v0": IdentityStage(),
    }


def base_recipe() -> dict[str, Any]:
    return {
        "schema_id": "audio-sdk/session-loopback-control/0.1",
        "recipe_id": "identity.loopback.v1",
        "contract_version": "0.1",
        "engine": "reference.sequential.v0",
        "format": dict(_FORMAT),
        "execution_mode": 3,
        "queue_capacity": 3,
        "stage_availability_cost_ns": 25000,
        "audio_path": ["pcm.in", "pcm.identity.out", "pcm.out"],
        "stages": [{
            "availability_cost_ns": 25000,
            "buffering_delay_samples": 0,
            "id": "identity",
            "input_port": "pcm.in",
            "instance": "identity",
            "output_port": "pcm.identity.out",
            "provider_id": "third_party.identity.v0",
            "role": "audio",
            "settings": {},
            "stage_id": "identity",
        }],
        "assets": [],
    }


def fallback_recipe() -> dict[str, Any]:
    return {
        "schema_id": "audio-sdk/session-loopback-control/0.1",
        "recipe_id": "identity.fallback.v1",
        "contract_version": "0.1",
        "engine": "reference.sequential.v0",
        "format": dict(_FORMAT),
        "execution_mode": 3,
        "queue_capacity": 3,
        "stage_availability_cost_ns": 25000,
        "audio_path": ["pcm.in", "pcm.fallback.out", "pcm.out"],
        "stages": [{
            "availability_cost_ns": 25000,
            "buffering_delay_samples": 0,
            "id": "identity",
            "input_port": "pcm.in",
            "instance": "identity_fallback",
            "output_port": "pcm.fallback.out",
            "provider_id": "third_party.fallback_identity.v0",
            "role": "audio",
            "settings": {},
            "stage_id": "identity",
        }],
        "assets": [],
    }


def canonical_recipe_bytes(raw: Mapping[str, Any]) -> bytes:
    return json.dumps(raw, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def source_digest() -> str:
    root = Path(__file__).resolve().parent
    joined = b"".join(path.name.encode("ascii") + b"\0" + path.read_bytes()
                      for path in sorted(root.glob("*.py")))
    return hashlib.sha256(joined).hexdigest()
