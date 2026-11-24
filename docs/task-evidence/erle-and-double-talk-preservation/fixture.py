# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen synthetic paired-signal room profile for duplex preservation evidence.

Every signal, path, window and schedule in this module is generated from the
pinned scalars in :func:`fixture_spec`.  Nothing is read from disk, no corpus or
model is used, and no result from this module is a real-room, device, listening
or release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from typing import Any, Dict, List, Optional, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
CHANNELS = 1
SAMPLE_FORMAT = "f32"
TOTAL_SAMPLES = 112000
SEED = 20261124
MAX_ABS_INPUT = 1.0

PATH_A: Tuple[Tuple[int, float], ...] = (
    (32, 0.50), (71, -0.32), (110, 0.22), (151, 0.15), (199, -0.10),
)
PATH_B: Tuple[Tuple[int, float], ...] = (
    (48, 0.46), (87, 0.30), (126, -0.20), (167, 0.14), (215, -0.09),
)
RENDER_LATENCY_SAMPLES = 32
DELAY_CHANGE_SAMPLES = 16
SWITCH_AT = 76800
TRANSITION_END = 83200
NEAR_GAIN = 0.55
NOISE_LEVEL = 0.0015
NEAR_SEED = 20261125
NOISE_SEED = 20261126
GATE_SEED = 20261127

SEGMENTS: Dict[str, Tuple[int, int]] = {
    "startup": (0, 6400),
    "far_only_early": (6400, 19200),
    "double_talk": (19200, 70400),
    "far_only_pre_switch": (70400, 76800),
    "path_transition": (76800, 83200),
    "far_only_post_change": (83200, 96000),
    "near_only_tail": (96000, 112000),
}
ERLE_WINDOWS: Dict[str, Tuple[int, int]] = {
    "early": (9600, 18400),
    "pre_switch": (71200, 76000),
    "post_change": (84800, 95200),
}
NEAR_WINDOW: Tuple[int, int] = (22400, 68800)
DROPOUT_INTERVAL: Tuple[int, int] = (84800, 86400)
DELAYED_RENDER_SAMPLES = 32

OVERLAP_RATIOS: Dict[str, float] = {
    "echo_only": 0.0,
    "overlap_25": 0.25,
    "overlap_50": 0.50,
    "overlap_100": 1.0,
}
CONDITIONS: Tuple[str, ...] = (
    "echo_only", "near_only", "overlap_25", "overlap_50", "overlap_100",
    "delay_change", "no_reference", "delayed_render", "reference_dropout",
)
RESET_SCHEDULE: Dict[str, Any] = {
    "stream_start_epoch": 1,
    "explicit_reset_at_sample": SWITCH_AT,
    "explicit_reset_epoch": 2,
    "stale_epoch_rejected": True,
    "stale_position_rejected": True,
    "zero_reference_preserves_state": True,
}


def canonical_bytes(value: Any) -> bytes:
    """Canonical report bytes: sorted keys, compact separators, one trailing LF."""
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    """SHA-256 over little-endian float32 bytes, matching the installed v0 format."""
    packed = struct.pack("<%df" % len(values), *[float(value) for value in values])
    return sha256_bytes(packed)


def _lcg(seed: int) -> Any:
    state = seed & 0x7FFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield 2.0 * state / 0x7FFFFFFF - 1.0


def _speech(seed: int, count: int, fundamental_hz: float, syllable_hz: float) -> List[float]:
    noise = _lcg(seed)
    phase = 0.0
    output: List[float] = []
    for index in range(count):
        seconds = index / SAMPLE_RATE_HZ
        pitch = fundamental_hz * (1.0 + 0.16 * math.sin(2.0 * math.pi * 1.3 * seconds))
        phase += 2.0 * math.pi * pitch / SAMPLE_RATE_HZ
        syllable = math.sin(2.0 * math.pi * syllable_hz * seconds
                            + 0.6 * math.sin(2.0 * math.pi * 0.53 * seconds))
        envelope = 0.10 + 0.90 * max(0.0, syllable) ** 1.5
        harmonic = math.fsum(math.sin((order + 1) * phase) / (order + 1) ** 1.2
                             for order in range(4))
        output.append(envelope * (0.24 * harmonic + 0.06 * next(noise)))
    return output


def _echo(far_end: Sequence[float], switch_at: int) -> List[float]:
    output: List[float] = []
    for index in range(len(far_end)):
        path = PATH_A if index < switch_at else PATH_B
        total = 0.0
        for delay, gain in path:
            source = index - delay
            if source >= 0:
                total += gain * far_end[source]
        output.append(total)
    return output


def _near_gate(ratio: float, near_only: bool) -> List[int]:
    gate = [0] * TOTAL_SAMPLES
    if near_only:
        start, end = SEGMENTS["near_only_tail"]
        for index in range(start, end):
            gate[index] = 1
        return gate
    if ratio <= 0.0:
        return gate
    start, end = SEGMENTS["double_talk"]
    if ratio >= 1.0:
        for index in range(start, end):
            gate[index] = 1
        return gate
    random = _lcg(GATE_SEED)
    for frame in range(start, end, FRAME_SAMPLES):
        if next(random) < ratio:
            for index in range(frame, min(frame + FRAME_SAMPLES, end)):
                gate[index] = 1
    return gate


def fixture_spec() -> Dict[str, Any]:
    """Pinned, JSON-serializable description of the frozen synthetic room."""
    return {
        "channels": CHANNELS,
        "conditions": list(CONDITIONS),
        "delay_change_samples": DELAY_CHANGE_SAMPLES,
        "delayed_render_samples": DELAYED_RENDER_SAMPLES,
        "dropout_interval_samples": list(DROPOUT_INTERVAL),
        "erle_windows_samples": {key: list(value) for key, value in ERLE_WINDOWS.items()},
        "excitation": {
            "far_end": "analytic harmonic/syllable source, no corpus (seed 20261124)",
            "near_end": "independent analytic harmonic/syllable source, no corpus (seed 20261125)",
            "noise": "seeded LCG capture noise (seed 20261126)",
        },
        "far_end_near_gain": NEAR_GAIN,
        "format": {"channels": CHANNELS, "sample_format": SAMPLE_FORMAT,
                   "frame_samples": FRAME_SAMPLES, "sample_rate_hz": SAMPLE_RATE_HZ},
        "frame_samples": FRAME_SAMPLES,
        "near_gate_seed": GATE_SEED,
        "near_metrics_window_samples": list(NEAR_WINDOW),
        "noise_level": NOISE_LEVEL,
        "overlap_ratios": dict(OVERLAP_RATIOS),
        "path_a": [list(item) for item in PATH_A],
        "path_b": [list(item) for item in PATH_B],
        "real_device_claim": False,
        "render_latency_samples": RENDER_LATENCY_SAMPLES,
        "reset_schedule": dict(RESET_SCHEDULE),
        "room_acoustics_measured": False,
        "sample_format": SAMPLE_FORMAT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "seed": SEED,
        "segments_samples": {key: list(value) for key, value in SEGMENTS.items()},
        "switch_at_sample": SWITCH_AT,
        "total_samples": TOTAL_SAMPLES,
        "transition_end_sample": TRANSITION_END,
    }


def fixture_digest() -> str:
    return sha256_bytes(canonical_bytes(fixture_spec()))


def fixture(name: str) -> Dict[str, Any]:
    """Build one frozen condition.  All streams have exactly TOTAL_SAMPLES samples."""
    if name not in CONDITIONS:
        raise ValueError("unknown_condition:" + name)

    far_base = _speech(SEED, TOTAL_SAMPLES, 118.0, 2.6)
    near_base = _speech(NEAR_SEED, TOTAL_SAMPLES, 187.0, 3.1)
    noise_source = _lcg(NOISE_SEED)
    noise = [NOISE_LEVEL * next(noise_source) for _ in range(TOTAL_SAMPLES)]

    if name == "near_only":
        far_end = [0.0] * TOTAL_SAMPLES
        ratio = 0.0
    else:
        far_end = far_base
        ratio = OVERLAP_RATIOS.get(name, OVERLAP_RATIOS["overlap_50"])
    gate = _near_gate(ratio, near_only=(name == "near_only"))
    near = [NEAR_GAIN * gate[index] * near_base[index] for index in range(TOTAL_SAMPLES)]
    echo = _echo(far_end, SWITCH_AT)
    microphone = [echo[index] + near[index] + noise[index] for index in range(TOTAL_SAMPLES)]

    reference: Optional[List[float]]
    if name == "no_reference":
        reference = None
    else:
        reference = list(far_end)
    if name == "delayed_render" and reference is not None:
        reference = [0.0] * DELAYED_RENDER_SAMPLES + reference[:-DELAYED_RENDER_SAMPLES]
    if name == "reference_dropout" and reference is not None:
        start, end = DROPOUT_INTERVAL
        reference = list(reference)
        for index in range(start, end):
            reference[index] = 0.0

    return {
        "condition": name,
        "microphone": microphone,
        "reference": reference,
        "render_mode": {
            "echo_only": "explicit_aligned",
            "near_only": "explicit_silent_render",
            "overlap_25": "explicit_aligned",
            "overlap_50": "explicit_aligned",
            "overlap_100": "explicit_aligned",
            "delay_change": "explicit_aligned_path_switch",
            "no_reference": "withheld",
            "delayed_render": "explicit_delayed_32_samples",
            "reference_dropout": "explicit_zero_render_gap",
        }[name],
        "near": near,
        "echo": echo,
        "noise": noise,
        "near_gate": gate,
        "active_path_before_switch": [list(item) for item in PATH_A],
        "active_path_after_switch": [list(item) for item in PATH_B],
        "overlap_ratio": ratio,
        "streams_sha256": {
            "microphone": tensor_digest(microphone),
            "reference": tensor_digest(reference) if reference is not None else None,
            "near": tensor_digest(near),
            "echo": tensor_digest(echo),
            "noise": tensor_digest(noise),
        },
    }
