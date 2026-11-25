# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen synthetic fixtures and verified source pins for the offline TSM reference.

Every signal is generated from integer arithmetic and a fixed LCG seed. No
recording, corpus, model, downloaded asset or licensed runtime is read.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
DEFAULT_AUDIOML_ROOT = Path("/Users/htsakanyan/workspace/audio/audioml")
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
NS_PER_SAMPLE = 1_000_000_000 // SAMPLE_RATE_HZ  # 62_500 ns at 16 kHz
SEED = 20261124

# Immutable source pins. All are documentation/provenance only; none is read as
# a signal, weight, code or runtime dependency.
SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/swarm/check.py":
        "5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539",
}

BOUNDARY_PINS: Dict[str, str] = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

# Mutable board provenance: recorded at task setup, never used as a gate.
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read": "721c972afbce171752475a1f082f822b29b59c31cd22b3534124d481530f724a",
    "mutable": True,
    "qualifies": False,
}


def audioml_root() -> Path:
    override_value = __import__("os").environ.get("AUDIOML_ROOT", "")
    if override_value:
        override = Path(override_value)
        if not override.is_dir():
            raise FileNotFoundError(f"AUDIOML_ROOT is not a directory: {override}")
        return override.resolve()
    if DEFAULT_AUDIOML_ROOT.is_dir():
        return DEFAULT_AUDIOML_ROOT
    for candidate in (TASK_DIR, *TASK_DIR.parents):
        if (candidate / "research").is_dir() and (candidate / "audio-benchmark-platform").is_dir():
            return candidate
    return DEFAULT_AUDIOML_ROOT


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def digest_value(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def verify_source_pins() -> Dict[str, Dict[str, Any]]:
    root = audioml_root()
    result: Dict[str, Dict[str, Any]] = {}
    for relative, expected in sorted(SOURCE_PINS.items()):
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        result[relative] = {
            "expected": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    return result


def verify_boundary_pins() -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    for relative, expected in sorted(BOUNDARY_PINS.items()):
        path = SDK_ROOT / relative
        actual = sha256_file(path) if path.is_file() else None
        result[relative] = {
            "expected": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    return result


class LCG:
    """Minimal deterministic signed uniform generator in [-1, 1)."""

    def __init__(self, seed: int = SEED) -> None:
        self.state = seed & 0xFFFFFFFFFFFFFFFF

    def next_int(self) -> int:
        self.state = (6364136223846793005 * self.state + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        return self.state >> 11

    def uniform(self) -> float:
        return (self.next_int() / float(1 << 53)) * 2.0 - 1.0


def synth_speech(n: int, pitch_hz: float, formant_hz: float, seed: int) -> List[float]:
    """Analytic vowel-like source with syllable envelope; no real speech."""
    rng = LCG(seed)
    out: List[float] = []
    phase = 0.0
    for i in range(n):
        t = i / float(SAMPLE_RATE_HZ)
        if (i // 2400) % 2 == 0:
            env = 0.55 + 0.45 * math.sin(math.pi * (i % 2400) / 2400.0)
        else:
            env = 0.12 + 0.20 * math.sin(math.pi * (i % 2400) / 2400.0)
        phase += 2.0 * math.pi * pitch_hz / SAMPLE_RATE_HZ
        if phase >= 2.0 * math.pi:
            phase -= 2.0 * math.pi
        glottal = math.sin(phase) + 0.35 * math.sin(2.0 * phase) + 0.12 * math.sin(3.0 * phase)
        formant = math.sin(2.0 * math.pi * formant_hz * t)
        noise = 0.018 * rng.uniform()
        value = env * (0.62 * glottal + 0.22 * formant + noise)
        out.append(max(-0.98, min(0.98, value)))
    return out


def synth_music(n: int, seed: int) -> List[float]:
    """Analytic chord/arpeggio with synthetic transients; no real music."""
    rng = LCG(seed)
    notes = (220.0, 277.1826, 329.6276, 440.0)
    out: List[float] = []
    for i in range(n):
        t = i / float(SAMPLE_RATE_HZ)
        note = notes[(i // 3200) % len(notes)]
        env = 0.30 + 0.16 * math.sin(2.0 * math.pi * 3.0 * t)
        chord = 0.58 * math.sin(2.0 * math.pi * note * t)
        chord += 0.24 * math.sin(2.0 * math.pi * note * 1.5 * t)
        chord += 0.12 * math.sin(2.0 * math.pi * note * 2.0 * t)
        age = i % 3200
        click = 0.34 * math.exp(-age / 65.0) * rng.uniform() if age < 420 else 0.0
        out.append(max(-0.98, min(0.98, env * chord + click)))
    return out


def synth_silence(n: int) -> List[float]:
    return [0.0] * n


def synth_transients(n: int, click_starts: Sequence[int], seed: int) -> List[float]:
    """Sparse deterministic clicks on a low bed for a transient proxy."""
    rng = LCG(seed)
    out = [0.004 * rng.uniform() for _ in range(n)]
    for start in click_starts:
        for k in range(220):
            idx = start + k
            if idx >= n:
                break
            out[idx] += 0.82 * math.exp(-k / 28.0) * (1.0 if (k & 1) == 0 else -1.0)
    return [max(-0.98, min(0.98, v)) for v in out]


CLICK_STARTS = (2400, 6400, 10400, 14400)


def build_stimuli() -> Dict[str, List[float]]:
    """Frozen stimuli; lengths are fixed and digests are recorded in the report."""
    return {
        "silence": synth_silence(9600),
        "speech_familiar": synth_speech(19200, 140.0, 620.0, SEED + 1),
        "speech_unfamiliar": synth_speech(19200, 190.0, 1180.0, SEED + 2),
        "music": synth_music(19200, SEED + 3),
        "transient": synth_transients(16000, CLICK_STARTS, SEED + 4),
        "tonal": [0.62 * math.sin(2.0 * math.pi * 220.0 * i / SAMPLE_RATE_HZ)
                  for i in range(9600)],
        "final_partial": synth_speech(12485, 165.0, 880.0, SEED + 5),
    }


# Source-timestamped decisions. Labels are frozen synthetic metadata, not the
# output of a real gate, ASR, VAD or listening test.
DECISION_LABELS: Dict[str, List[Dict[str, Any]]] = {
    "speech_unfamiliar": [
        {"source_start": 0, "source_end": 4800, "label": "speech", "decision": "protect"},
        {"source_start": 4800, "source_end": 6400, "label": "filler", "decision": "flex"},
        {"source_start": 6400, "source_end": 11200, "label": "speech", "decision": "protect"},
        {"source_start": 11200, "source_end": 12800, "label": "silence", "decision": "flex"},
        {"source_start": 12800, "source_end": 19200, "label": "speech", "decision": "protect"},
    ],
    "silence": [{"source_start": 0, "source_end": 9600, "label": "silence", "decision": "flex"}],
    "music": [{"source_start": 0, "source_end": 19200, "label": "music", "decision": "protect"}],
}

CASES: Dict[str, Dict[str, Any]] = {
    "identity_1x": {"stimulus": "speech_unfamiliar", "control": "identity", "rate": 1.0},
    "speed_up_125": {"stimulus": "speech_unfamiliar", "control": "ola_wsola", "rate": 1.25},
    "speed_up_150": {"stimulus": "music", "control": "ola_wsola", "rate": 1.5},
    "speed_down_080": {"stimulus": "speech_unfamiliar", "control": "ola_wsola", "rate": 0.8},
    "speed_down_090": {"stimulus": "speech_unfamiliar", "control": "ola_wsola", "rate": 0.9},
    "unfamiliar_speech": {"stimulus": "speech_unfamiliar", "control": "ola_wsola", "rate": 1.2},
    "music_material": {"stimulus": "music", "control": "ola_wsola", "rate": 0.85},
    "silence_case": {"stimulus": "silence", "control": "ola_wsola", "rate": 1.5},
    "transient_case": {"stimulus": "transient", "control": "ola_wsola", "rate": 1.25},
    "tonal_pitch_case": {"stimulus": "tonal", "control": "ola_wsola", "rate": 1.25},
    "final_partial_window": {"stimulus": "final_partial", "control": "ola_wsola", "rate": 1.25},
    "drift_case": {
        "stimulus": "speech_unfamiliar", "control": "ola_wsola",
        "schedule": [(0, 1.0), (4800, 1.1), (9600, 0.95), (14400, 1.0)],
    },
    "rebuffer_case": {
        "stimulus": "speech_unfamiliar", "control": "ola_wsola",
        "schedule": [(0, 1.0), (6400, 1.15), (12800, 0.9)],
        "rebuffer": {"source_sample": 6400, "gap_output_samples": 1600},
    },
    "source_timestamp_policy": {
        "stimulus": "speech_unfamiliar", "control": "ola_wsola",
        "label_driven_schedule": True,
    },
    "varispeed_adverse": {"stimulus": "tonal", "control": "varispeed", "rate": 1.25},
    "rate_step_unsmoothed_adverse": {
        "stimulus": "transient", "control": "rate_step_unsmoothed",
        "schedule": [(0, 1.0), (6400, 1.5)],
    },
}


def fixture_recipe() -> Dict[str, Any]:
    """Stable, hashable recipe describing every frozen input."""
    stimuli = build_stimuli()
    descriptions = {}
    for name, samples in sorted(stimuli.items()):
        descriptions[name] = {
            "length": len(samples),
            "digest": digest_value([round(v, 12) for v in samples]),
            "min": min(samples),
            "max": max(samples),
        }
    return {
        "seed": SEED,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "ns_per_sample": NS_PER_SAMPLE,
        "stimuli": descriptions,
        "click_starts": list(CLICK_STARTS),
        "decision_labels": DECISION_LABELS,
        "cases": CASES,
    }


def fixture_digest() -> str:
    return digest_value(fixture_recipe())


def source_ns(sample: int) -> int:
    return sample * NS_PER_SAMPLE
