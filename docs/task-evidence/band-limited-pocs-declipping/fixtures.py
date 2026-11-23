"""Frozen synthetic stimuli and pinned source digests for the POCS fixture.

Every stimulus is generated from integer seeds and closed-form math; no WAV,
corpus, model download or host timing is involved.  The clean source is kept
separately from the corruption (hard clipping threshold and resulting mask),
so transparency and damaged-region scoring use a frozen baseline.
"""

from __future__ import annotations

import math

import reference

SCHEMA = "sdk.band-limited-pocs-declipping.fixtures.v1"

SOURCE_PINS = {
    "research/distortion_restoration_20261028.md":
        "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "src/audioml_eval/distortion_restoration.py":
        "c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f",
    "reports/distortion-restoration/20261028-synthetic-screen.json":
        "87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "adapters/controls/adapter.json":
        "3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599",
    "adapters/controls/run.py":
        "4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66",
}

STIMULI = {
    "clean_bandlimited": {
        "kind": "tones",
        "frequencies_hz": [220.0, 440.0, 880.0, 1500.0],
        "amplitudes": [0.40, 0.25, 0.15, 0.10],
        "peak": 0.90,
    },
    "clean_quiet": {
        "kind": "tones",
        "frequencies_hz": [300.0, 700.0, 1300.0],
        "amplitudes": [0.16, 0.09, 0.05],
        "peak": 0.30,
    },
    "sparse_transients": {
        "kind": "transients",
        "seed": 424242,
        "positions": [71, 307, 599, 811, 1103, 1379, 1601, 1887],
        "width_samples": 9,
        "noise_amplitude": 0.035,
        "peak": 1.0,
    },
    "very_sparse_transients": {
        "kind": "transients",
        "seed": 911,
        "positions": [173, 1501],
        "width_samples": 9,
        "noise_amplitude": 0.02,
        "peak": 1.0,
    },
    "speech_like": {
        "kind": "speech",
        "seed": 1907,
        "f0_hz": 145.0,
        "harmonics": [1.0, 0.55, 0.30, 0.18, 0.10],
        "burst_samples": 208,
        "gap_samples": 96,
        "peak": 1.0,
    },
    "dense_tones": {
        "kind": "tones",
        "frequencies_hz": [310.0, 770.0, 1310.0, 2470.0, 3610.0],
        "amplitudes": [0.35, 0.28, 0.20, 0.12, 0.05],
        "peak": 1.0,
    },
    "nonfinite": {
        "kind": "nonfinite",
        "frequency_hz": 440.0,
        "amplitude": 0.80,
        "nan_at": 17,
        "inf_at": 1025,
    },
}


def seed_spec():
    return {
        "schema": SCHEMA,
        "sample_rate_hz": reference.SAMPLE_RATE_HZ,
        "sdk_frame_samples": reference.SDK_FRAME_SAMPLES,
        "offline_block_samples": reference.OFFLINE_BLOCK_SAMPLES,
        "source_pins": SOURCE_PINS,
        "stimuli": STIMULI,
    }


def _lcg(seed):
    state = int(seed) & 0x7FFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield 2.0 * state / 0x7FFFFFFF - 1.0


def _normalize(values, peak):
    observed = max(abs(value) for value in values)
    if observed == 0.0:
        return values
    scale = float(peak) / observed
    return [value * scale for value in values]


def build_samples(stimulus_id):
    """Return the frozen *clean* source for one stimulus (float32)."""
    if stimulus_id not in STIMULI:
        raise ValueError("unknown_stimulus:" + stimulus_id)
    spec = STIMULI[stimulus_id]
    count = reference.OFFLINE_BLOCK_SAMPLES
    rate = float(reference.SAMPLE_RATE_HZ)
    kind = spec["kind"]
    if kind == "tones":
        values = []
        for index in range(count):
            values.append(sum(amplitude * math.sin(2.0 * math.pi * frequency * index / rate)
                              for frequency, amplitude in zip(spec["frequencies_hz"],
                                                              spec["amplitudes"])))
        values = _normalize(values, spec["peak"])
    elif kind == "transients":
        noise = _lcg(spec["seed"])
        values = [spec["noise_amplitude"] * next(noise) for _ in range(count)]
        half = int(spec["width_samples"]) // 2
        for position in spec["positions"]:
            for offset in range(-half, half + 1):
                index = int(position) + offset
                if 0 <= index < count:
                    values[index] += math.cos(math.pi * offset / (half + 1))
        values = _normalize(values, spec["peak"])
    elif kind == "speech":
        noise = _lcg(spec["seed"])
        period = int(spec["burst_samples"]) + int(spec["gap_samples"])
        values = []
        for index in range(count):
            within = index % period
            if within >= int(spec["burst_samples"]):
                values.append(0.02 * next(noise))
                continue
            envelope = 0.5 - 0.5 * math.cos(
                2.0 * math.pi * within / int(spec["burst_samples"]))
            voiced = sum(weight * math.sin((harmonic + 1) * 2.0 * math.pi
                                           * spec["f0_hz"] * index / rate)
                         for harmonic, weight in enumerate(spec["harmonics"]))
            values.append(envelope * voiced)
        values = _normalize(values, spec["peak"])
    elif kind == "nonfinite":
        values = [spec["amplitude"] * math.sin(
            2.0 * math.pi * spec["frequency_hz"] * index / rate) for index in range(count)]
        values[int(spec["nan_at"])] = math.nan
        values[int(spec["inf_at"])] = math.inf
    else:
        raise ValueError("unknown_stimulus_kind:" + kind)
    return [reference.f32(value) for value in values]
