#!/usr/bin/env python3
"""Deterministic generator for the envelope-AGC fixture specification.

The script writes a small JSON specification (parameters, pins and immutability
metadata), not audio assets. All sample buffers are produced from these frozen
parameters by ``run.generate`` at report/test time. No recordings, downloads,
models or licensed runtimes are used.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "fixtures" / "stimuli.json"
SCHEMA = "sdk.envelope-agc.fixtures.v1"

SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "src/audioml_eval/level_tone.py":
        "a0ec2e3b217d877a26ae585402072d6d4ec4d1aa366ef6cd67c5b40176e2f84f",
    "research/voice-enhancement-20261101/agent-agc-expanded/REPORT.md":
        "cab8ef60b260f4b6af536111204e781c0e03a53b85986c16a271f1a1db004188",
    "adapters/controls/adapter.json":
        "3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599",
    "adapters/controls/run.py":
        "4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

TASK_BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read": "a858ebf522110d43e3e0b14c61a9705230b8732bb47e8f17819a2977738ea8ad",
    "mutable": True,
    "note": "Read-time snapshot only; never a qualification or gating source.",
}

STIMULI = {
    "sweep": {
        "kind": "chirp", "length": 4000, "f0_hz": 200.0, "f1_hz": 4000.0,
        "amp0": 0.02, "amp1": 0.5,
    },
    "steps": {
        "kind": "steps", "length": 4000, "tone_hz": 1000.0,
        "levels": [0.02, 0.08, 0.02, 0.4, 0.02, 0.15, 0.02, 0.6,
                   0.02, 0.08, 0.02, 0.3, 0.02, 0.5, 0.02, 0.1,
                   0.02, 0.35, 0.02, 0.2, 0.02, 0.45, 0.02, 0.12, 0.02],
    },
    "impulse": {
        "kind": "impulse", "length": 3200, "position": 17,
        "amplitude": 1.5, "tail_hz": 700.0, "tail_amplitude": 0.05,
    },
    "silence": {"kind": "silence", "length": 1600},
    "fixed_tone": {
        "kind": "tone", "length": 3200, "frequency_hz": 1000.0, "amplitude": 0.063,
    },
    "clean_speech_like": {
        "kind": "speech_like", "length": 6400, "f0_hz": 120.0,
        "burst_samples": 1600, "gap_samples": 400,
        "amplitudes": [0.12, 0.18, 0.10, 0.20], "seed": 41000,
    },
    "gain_step_speech": {
        "kind": "gain_step", "source": "clean_speech_like",
        "block_samples": 640, "ramp_samples": 320,
        "levels_db": [-9.0, 9.0], "seed": 41001,
    },
    "overshoot": {
        "kind": "overshoot", "length": 3200, "tone_hz": 1000.0,
        "quiet_amplitude": 0.005, "loud_amplitude": 1.2,
        "loud_start": 1600, "loud_end": 2400,
    },
    "nonfinite": {
        "kind": "nonfinite", "length": 320, "tone_hz": 1000.0,
        "amplitude": 0.1, "nan_at": 5, "inf_at": 165,
    },
}


def build_spec():
    return {
        "schema": SCHEMA,
        "task": "SDK-ENVELOPE-AGC",
        "status": "proposal_only_synthetic",
        "geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
        },
        "generator": "stdlib math, explicit LCG; no numpy, scipy, corpus or model",
        "source_pins": dict(sorted(SOURCE_PINS.items())),
        "task_board": TASK_BOARD_SNAPSHOT,
        "stimuli": STIMULI,
    }


def canonical_bytes(value):
    text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return text.encode("ascii") + b"\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(OUTPUT))
    parser.add_argument("--check", action="store_true",
                        help="verify the committed file instead of writing it")
    args = parser.parse_args()
    target = Path(args.output)
    data = canonical_bytes(build_spec())
    if args.check:
        if not target.exists() or target.read_bytes() != data:
            raise SystemExit("fixture specification is stale; rerun generate.py")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".tmp")
    temp.write_bytes(data)
    os.replace(temp, target)
    print(hashlib.sha256(data).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
