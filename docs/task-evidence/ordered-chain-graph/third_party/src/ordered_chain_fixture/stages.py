"""Deterministic third-party stages for the installed fixture probe.

No SDK symbols, imports, weights, downloads or runtime are used. The package is
installed as a wheel and consumed only through the proposed recipe/executor
duck-typed interface. It models one gain, one peak limiter and one analysis tap.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

FIXTURE_ID = "third-party/ordered-chain-fixture/0.1"
FIXTURE_VERSION = "0.1.0"


class _ThirdPartyStage:
    role = "audio"

    @staticmethod
    def delay_samples(settings: Mapping[str, Any]) -> int:
        return 0

    @staticmethod
    def cost_ns(settings: Mapping[str, Any]) -> int:
        return int(settings["availability_cost_ns"])


class Gain(_ThirdPartyStage):
    @staticmethod
    def transform(samples: Sequence[float], settings: Mapping[str, Any],
                  ctx: Mapping[str, Any]):
        gain = settings["gain"]
        if not isinstance(gain, (int, float)) or isinstance(gain, bool) or not math.isfinite(float(gain)):
            raise ValueError("nonfinite_gain")
        return tuple(float(x) * float(gain) for x in samples), ()


class Limiter(_ThirdPartyStage):
    @staticmethod
    def transform(samples: Sequence[float], settings: Mapping[str, Any],
                  ctx: Mapping[str, Any]):
        peak = settings["peak"]
        if not isinstance(peak, (int, float)) or isinstance(peak, bool) or not math.isfinite(float(peak)):
            raise ValueError("nonfinite_peak")
        bounded = max(0.0, float(peak))
        return tuple(max(-bounded, min(bounded, float(x))) for x in samples), ()


class Activity:
    role = "analysis"

    @staticmethod
    def delay_samples(settings: Mapping[str, Any]) -> int:
        return 0

    @staticmethod
    def cost_ns(settings: Mapping[str, Any]) -> int:
        return int(settings["availability_cost_ns"])

    @staticmethod
    def transform(samples: Sequence[float], settings: Mapping[str, Any],
                  ctx: Mapping[str, Any]):
        index = int(ctx["frame_index"])
        if index > 2:
            return tuple(samples), ()
        start = max(0, int(ctx["source_first"]))
        end = int(ctx["source_first"]) + int(ctx["valid_count_in"])
        available_ns = int(ctx["availability_ns"]) + int(settings.get("event_offset_ns", 0))
        if index == 1:
            return tuple(samples), ()
        if index == 0:
            value, validity = 0.75, "known"
        else:
            value, validity = None, "unknown"
        return tuple(samples), ({
            "source_start": start,
            "source_end": end,
            "value": value,
            "validity": validity,
            "available_ns": available_ns,
            "epoch": int(ctx["epoch"]),
        },)


def installed_stages() -> dict[str, Any]:
    """Provider IDs supplied by this installed third-party package."""
    return {
        "third_party.gain.v0": Gain(),
        "third_party.limiter.v0": Limiter(),
        "third_party.activity.v0": Activity(),
    }


def recipe() -> dict[str, Any]:
    """Recipe using installed stages plus the executor's built-in delay stage."""
    return {
        "schema_id": "audio-sdk/ordered-chain-graph/0.1",
        "recipe_id": "installed.chain.v1",
        "contract_version": "0.1",
        "engine": "reference.sequential.v0",
        "format": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
        },
        "audio_path": ["gain", "delay", "limiter"],
        "nodes": [
            {
                "id": "gain", "provider_id": "third_party.gain.v0", "role": "audio",
                "delay_samples": 0, "availability_cost_ns": 100000,
                "settings": {"gain": 0.5}, "depends_on": [],
                "input_port": "pcm.in", "output_port": "pcm.gain.out",
            },
            {
                "id": "delay", "provider_id": "fixture.delay.v0", "role": "audio",
                "delay_samples": 80, "availability_cost_ns": 500000,
                "settings": {"delay_samples": 80}, "depends_on": ["gain"],
                "input_port": "pcm.gain.out", "output_port": "pcm.delay.out",
            },
            {
                "id": "limiter", "provider_id": "third_party.limiter.v0", "role": "audio",
                "delay_samples": 0, "availability_cost_ns": 75000,
                "settings": {"peak": 0.25}, "depends_on": ["delay"],
                "input_port": "pcm.delay.out", "output_port": "pcm.out",
            },
            {
                "id": "activity", "provider_id": "third_party.activity.v0", "role": "analysis",
                "delay_samples": 0, "availability_cost_ns": 40000,
                "settings": {"event_offset_ns": 1000}, "depends_on": ["gain"],
                "tap_port": "pcm.gain.out", "max_age_samples": 320,
            },
        ],
    }


def source_digest() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def canonical_recipe_bytes() -> bytes:
    return json.dumps(recipe(), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")
