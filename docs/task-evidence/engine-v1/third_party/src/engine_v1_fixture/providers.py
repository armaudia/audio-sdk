"""Deterministic third-party providers for the installed engine fixture probe.

No SDK symbols, imports, models, downloads or runtime are used. These classes
duck-type the proposal's provider hooks and are consumed only through the
source-independent reference scheduler.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

CALIBRATION_DIGEST = "74ccca3b2342225b60a75bdbafbd40b0cc28b4f18ab15b258c3529018c1c4276"


@dataclass(frozen=True)
class Outcome:
    samples: tuple[float, ...]
    events: tuple[dict[str, Any], ...] = ()
    work_ns: int = 0
    validity: str = "known"
    failure: Optional[str] = None


def _outcome(samples, work_ns=0, events=()):
    return Outcome(tuple(float(x) for x in samples), tuple(events), int(work_ns))


class _Base:
    role = "audio"

    def __init__(self, provider_id: str, instance_id: str = "third_party.instance") -> None:
        self.provider_id = provider_id
        self.instance_id = instance_id
        self.state = 0.0
        self.version = 0
        self.in_batch = False
        self.lane_states: dict[str, Any] = {}

    def capabilities(self):
        return {"policy_query": False, "process_mode": False, "resume_prepare": False,
                "process_batch": False, "max_batch": 0}

    def delay_samples(self, settings: Mapping[str, Any]) -> int:
        return int(settings.get("delay_samples", 0))

    def work_ns(self, settings: Mapping[str, Any]) -> int:
        return int(settings.get("work_ns", 1_000_000))

    def reset(self) -> None:
        self.state = 0.0
        self.version += 1
        self.lane_states.clear()

    def state_digest(self) -> str:
        payload = f"{self.instance_id}:{self.version}:{self.state!r}".encode("ascii")
        return hashlib.sha256(payload).hexdigest()


class Gain(_Base):
    def process(self, samples: Sequence[float], settings: Mapping[str, Any],
                ctx: Mapping[str, Any]):
        gain = float(settings["gain"])
        if not math.isfinite(gain):
            raise ValueError("nonfinite_gain")
        return _outcome((float(x) * gain for x in samples), self.work_ns(settings))


class Transition(_Base):
    def capabilities(self):
        return {"policy_query": True, "process_mode": True, "resume_prepare": True,
                "process_batch": False, "max_batch": 0}

    def policy_query(self):
        return {"cheap_state_semantics": "full_state_update", "history_samples": 0,
                "warm_frames": 0, "crossfade_compatible": True, "invariant_delay": True}

    def process(self, samples, settings, ctx):
        return self.process_mode(samples, settings, ctx, "full")

    def process_mode(self, samples, settings, ctx, mode):
        if mode not in ("full", "cheap", "observe"):
            raise ValueError("unknown_mode")
        current = float(self.state)
        mean = sum(float(x) for x in samples) / len(samples)
        output = tuple(float(x) + current for x in samples)
        if mode != "observe":
            self.state = 0.5 * current + mean
        return _outcome(output, self.work_ns(settings))

    def resume_prepare(self, retained_history, warm_samples):
        payload = json.dumps({"history": [float(x) for x in retained_history],
                              "state": float(self.state), "warm_samples": int(warm_samples)},
                             sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
        if not hasattr(self, "_buffer"):
            self._buffer = [0.0] * 160
        return {"prepared_digest": hashlib.sha256(payload).hexdigest(),
                "warm_frames": int(warm_samples), "buffer": self._buffer}


class Activity(_Base):
    role = "analysis"

    def process(self, samples, settings, ctx):
        index = int(ctx["frame_index"])
        if index % 2 == 1:
            return _outcome(samples, self.work_ns(settings))
        value = None if index % 4 == 2 else float(settings["event_value"])
        event = {
            "producer_id": self.provider_id,
            "tap_id": ctx["tap_port"],
            "stream_id": int(ctx["stream_id"]),
            "epoch": int(ctx["epoch"]),
            "source_start": max(0, int(ctx["source_first"])),
            "source_end": int(ctx["source_first"]) + int(ctx["valid_count_in"]),
            "available_ns": int(ctx["ready_ns"]) + int(settings.get("event_offset_ns", 0)),
            "signal_kind": settings.get("signal_kind", "speech_probability"),
            "value": value,
            "validity": "unknown" if value is None else "known",
            "calibration_digest": settings.get("calibration_digest", CALIBRATION_DIGEST),
        }
        return _outcome(samples, self.work_ns(settings), (event,))
