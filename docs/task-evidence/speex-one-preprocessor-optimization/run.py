#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Private synthetic replay of the Basic Speex preprocessing topology."""

import argparse
import ctypes as c
import hashlib
import json
import math
import os
import platform
import re
import shlex
import struct
import subprocess
import sys
import time
from contextlib import ExitStack
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VENDOR = ROOT / "third_party/speexdsp"
MANIFEST = ROOT / "deps/speexdsp-files.sha256"
SOURCE_PIN = "3ff2b43a21b28a10a87f5a30b3c0339bef67a6b491c22f0f90c45696bd8f7a29"
RATE = 16000
NS_PER_SAMPLE = 62500
PEAK = round(0.98 * 32767)
CONTROLS = {"noise_suppress_db": -20, "vad_start_pct": 65,
            "vad_continue_pct": 50, "agc_level": 8000, "dereverb": 0}
# Each tuple describes (state name, denoise, AGC, read advisory). The raw tap
# consumes a separate copy of the input; only non-tap states change audio.
VARIANTS = {
    "identity": ((), False),
    "separate": ((("ns", 1, 0, False), ("agc", 0, 1, False), ("raw_tap", 0, 0, True)), True),
    "common": ((("common", 1, 1, True),), True),
    "no_ns": ((("common", 0, 1, True),), True),
    "no_agc": ((("common", 1, 0, True),), True),
    "no_advisory": ((("common", 1, 1, False),), True),
    "no_limiter": ((("common", 1, 1, True),), False),
    "fallback": ((("ns", 1, 0, False),), True),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pcm_hash(samples):
    return sha(struct.pack(f"<{len(samples)}h", *samples))


def build(output):
    manifest = MANIFEST.read_bytes()
    if sha(manifest) != SOURCE_PIN:
        raise ValueError("SDK Speex source manifest differs from the task pin")
    for line in manifest.decode().splitlines():
        digest, path = line.split("  ", 1)
        if sha((ROOT / path).read_bytes()) != digest:
            raise ValueError(f"SDK Speex source pin mismatch: {path}")
    if sys.platform not in ("darwin", "linux"):
        raise RuntimeError("private Speex adapter supported only on macOS and Linux")
    compiler = shlex.split(os.getenv("CC", "cc"))
    library = output / ("speex.dylib" if sys.platform == "darwin" else "speex.so")
    command = [*compiler, "-dynamiclib" if sys.platform == "darwin" else "-shared",
               "-fPIC", "-O3", "-DFLOATING_POINT", "-DUSE_SMALLFT", "-DEXPORT=",
               "-DDISABLE_WARNINGS", "-I", str(VENDOR / "include"),
               *(str(VENDOR / "libspeexdsp" / f"{name}.c")
                 for name in ("preprocess", "mdf", "fftwrap", "filterbank", "smallft")),
               "-lm", "-o", str(library)]
    subprocess.run(command, check=True)
    return Speex(library), {
        "vendor_manifest_sha256": SOURCE_PIN,
        "library_sha256": sha(library.read_bytes()),
        "compiler": subprocess.check_output([*compiler, "--version"], text=True).splitlines()[0],
        "command": command,
    }


class Speex:
    def __init__(self, library):
        lib = c.CDLL(str(library))
        self.init = lib.speex_preprocess_state_init
        self.init.argtypes, self.init.restype = [c.c_int, c.c_int], c.c_void_p
        self.destroy = lib.speex_preprocess_state_destroy
        self.destroy.argtypes, self.destroy.restype = [c.c_void_p], None
        self.run = lib.speex_preprocess_run
        self.run.argtypes, self.run.restype = [c.c_void_p, c.POINTER(c.c_int16)], c.c_int
        self.ctl = lib.speex_preprocess_ctl
        self.ctl.argtypes, self.ctl.restype = [c.c_void_p, c.c_int, c.c_void_p], c.c_int
        header = (VENDOR / "include/speex/speex_preprocess.h").read_text()
        self.controls = {name: int(code) for name, code in
                         re.findall(r"^#define SPEEX_PREPROCESS_(\w+) (\d+)$", header, re.M)}

    def control(self, state, name, value):
        return self.ctl(state, self.controls[name], c.byref(value)) == 0

    def state(self, stack, hop, denoise, agc, advisory):
        state = self.init(hop, RATE)
        if not state:
            raise RuntimeError("Speex state initialization failed")
        stack.callback(self.destroy, state)
        for name, value in (
            ("SET_DENOISE", c.c_int32(denoise)), ("SET_AGC", c.c_int32(agc)),
            ("SET_VAD", c.c_int32(advisory)), ("SET_DEREVERB", c.c_int32(CONTROLS["dereverb"])),
            ("SET_PROB_START", c.c_int32(CONTROLS["vad_start_pct"])),
            ("SET_PROB_CONTINUE", c.c_int32(CONTROLS["vad_continue_pct"])),
            ("SET_NOISE_SUPPRESS", c.c_int32(CONTROLS["noise_suppress_db"])),
            ("SET_AGC_LEVEL", c.c_float(CONTROLS["agc_level"])),
        ):
            if not self.control(state, name, value):
                raise RuntimeError(f"Speex control failed: {name}")
        return state

    def probability(self, state):
        value = c.c_int32(-1)
        if self.control(state, "GET_PROB", value) and 0 <= value.value <= 100:
            return value.value
        return None


def fixture(noisy):
    """Matched clean reference and deterministic PCM16 mixture; not speech."""
    sections = ((0, 3200, "silence", 0), (3200, 6400, "noise", 0),
                (6400, 9600, "quiet", 260), (9600, 14400, "loud", 10000),
                (14400, 19200, "noise", 0), (19200, 22473, "quiet", 260))
    rng = 0x5EED
    reference, samples = [], []
    for lo, hi, label, level in sections:
        for n in range(lo, hi):
            phase = 2 * math.pi * n / RATE
            tone = round(level * (0.7 * math.sin(177 * phase) + 0.3 * math.sin(531 * phase)))
            rng = (1664525 * rng + 1013904223) & 0xFFFFFFFF
            noise = (rng >> 21) - 1024 + round(768 * math.sin(61 * phase))
            reference.append(tone)
            samples.append(tone + (noise if noisy and label != "silence" else 0))
    return reference, samples, sections


def replay(speex, samples, hop, variant, *, paced=False):
    topology, limiter = VARIANTS[variant]
    delay = hop * sum(name != "raw_tap" for name, *_ in topology)
    count = len(samples)
    frames = (count + hop - 1) // hop
    flush = delay // hop if count else 0
    padded = samples + [0] * ((frames + flush) * hop - count)
    frame_type = c.c_int16 * hop
    out, trace = [], []
    step_ns = hop * NS_PER_SAMPLE
    with ExitStack() as stack:
        states = [(name, advisory, speex.state(stack, hop, denoise, agc, advisory))
                  for name, denoise, agc, advisory in topology]
        audio, tap = frame_type(), frame_type()
        origin = time.monotonic_ns()
        for i in range(frames + flush):
            due = (i + 1) * step_ns
            if paced:
                wait = origin + due - time.monotonic_ns()
                if wait > 0:
                    time.sleep(wait / 1e9)
            start = time.monotonic_ns() - origin
            n = i * hop
            source = padded[n:n + hop]
            audio[:] = source
            stages = {}
            observation = None
            for name, advisory, state in states:
                buf = audio
                if name == "raw_tap":
                    tap[:] = source
                    buf = tap
                before = time.monotonic_ns() - origin
                event = speex.run(state, buf)
                after = time.monotonic_ns() - origin
                stages[name] = after - before
                if event not in (0, 1):
                    raise RuntimeError("unexpected Speex process return; discard epoch")
                if advisory:
                    probability = speex.probability(state)
                    available = time.monotonic_ns() - origin
                    if n >= hop and n + hop <= count:
                        observation = {
                            "window": [n - hop, n + hop],
                            "available_ns": str(available),
                            "prob_pct": probability,
                            "advisory_active": bool(event) if probability is not None else None,
                        }
            frame = list(audio)
            peak = max(map(abs, frame))
            limited = limiter and peak > PEAK
            if limited:
                frame = [round(x * PEAK / peak) for x in frame]
            source_start = n - delay
            lo, hi = max(0, source_start), min(count, source_start + hop)
            if hi > lo:
                out.extend(frame[lo - source_start:hi - source_start])
            ready = time.monotonic_ns() - origin
            trace.append({
                "accepted_samples": min(hop, max(0, count - n)),
                "produced_samples": hop, "source_first": source_start,
                "valid_interval": [lo, hi] if hi > lo else None,
                "due_ns": str(due) if paced else None, "start_ns": str(start),
                "ready_ns": str(ready), "stage_run_ns": stages, "limited": limited,
                "advisory": observation,
            })
    return out, trace, delay


def rms_db(samples):
    return round(10 * math.log10(max(sum(x * x for x in samples) / len(samples) / 32768**2, 1e-12)), 3)


def si_sdr(reference, samples):
    ref_mean, out_mean = sum(reference) / len(reference), sum(samples) / len(samples)
    centered = [x - ref_mean for x in reference]
    norm = sum(x * x for x in centered)
    scale = sum(r * (x - out_mean) for r, x in zip(centered, samples, strict=True)) / norm
    target = scale * scale * norm
    residual = sum((x - out_mean - scale * r)**2 for r, x in zip(centered, samples, strict=True))
    return round(10 * math.log10(target / residual), 3) if target and residual else None


def timing(values):
    values = sorted(values)
    return {"sum": sum(values), "p50": values[math.ceil(len(values) * 0.50) - 1],
            "p95": values[math.ceil(len(values) * 0.95) - 1], "max": values[-1]}


def summarize(reference, out, sections, trace, hop, delay, paced):
    cursor = 0
    for frame in trace:
        if interval := frame["valid_interval"]:
            if interval[0] != cursor:
                raise ValueError("valid intervals overlap or leave a gap")
            cursor = interval[1]
    if sum(f["accepted_samples"] for f in trace) != cursor or cursor != len(reference):
        raise ValueError("accepted content was not conserved")
    frames = [f for f in trace if f["accepted_samples"]]
    scores = {}
    for lo, hi, label, _ in sections:
        row = scores.setdefault(label, {"windows": 0, "active": 0, "invalid": 0, "rms_dbfs": []})
        row["rms_dbfs"].append(rms_db(out[lo:hi]))
        for f in frames:
            obs = f["advisory"]
            if obs and lo <= obs["window"][0] and obs["window"][1] <= hi:
                row["windows"] += 1
                row["active"] += obs["advisory_active"] is True
                row["invalid"] += obs["advisory_active"] is None
    for label, row in scores.items():
        valid = row["windows"] - row["invalid"]
        row["surrogate_error"] = (
            {"kind": "FN" if label in ("quiet", "loud") else "FP",
             "count": valid - row["active"] if label in ("quiet", "loud") else row["active"],
             "valid_windows": valid} if valid else None
        )
    service = timing(int(f["ready_ns"]) - int(f["start_ns"]) for f in frames)
    stages = {name: {"calls": len(frames), **timing(f["stage_run_ns"][name] for f in frames)}
              for name in frames[0]["stage_run_ns"]}
    hop_ns = hop * NS_PER_SAMPLE
    return {
        "delay_samples": delay, "accepted_and_delivered_samples": cursor,
        "startup_frames": delay // hop, "flush_frames": len(trace) - len(frames),
        "final_input_samples": frames[-1]["accepted_samples"], "queue_capacity": 0,
        "output_sha256": pcm_hash(out), "si_sdr_db": si_sdr(reference, out),
        "output_peak_pcm16": max(map(abs, out)),
        "output_at_pcm16_limits": sum(x in (-32768, 32767) for x in out),
        "limited_frames_including_flush": sum(f["limited"] for f in trace),
        "advisory_and_rms_by_label": scores, "stage_wall_ns": stages, "inline_service_wall_ns": service,
        "stage_wall_rtf": sum(row["sum"] for row in stages.values()) / (cursor * NS_PER_SAMPLE),
        "paced": ({
            "release_to_ready_ns": timing(int(f["ready_ns"]) - int(f["due_ns"]) for f in frames),
            "deadline_misses": sum(int(f["ready_ns"]) > int(f["due_ns"]) + hop_ns for f in frames),
            "content_first_sample_to_ready_ns": timing(
                int(f["ready_ns"]) - f["valid_interval"][0] * NS_PER_SAMPLE
                for f in trace if f["valid_interval"]),
            "flush_ready_ns": [f["ready_ns"] for f in trace[len(frames):]],
        } if paced else None),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="new private directory outside the SDK checkout")
    parser.add_argument("--paced", action="store_true", help="also replay the mixed input at real cadence")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        parser.error("--output must be outside the SDK checkout")
    output.mkdir(mode=0o700)
    speex, provenance = build(output)
    report = {"python": platform.python_version(), "host": platform.platform(),
              "build": provenance, "topologies": VARIANTS, "rate_hz": RATE,
              "controls": CONTROLS, "limiter_peak_pcm16": PEAK, "runs": {}}
    for noisy in (False, True):
        reference, samples, sections = fixture(noisy)
        for hop in (160, 320):
            for variant in VARIANTS:
                baseline = None
                for paced in ((False, True) if noisy and args.paced else (False,)):
                    out, trace, delay = replay(speex, samples, hop, variant, paced=paced)
                    tag = f"{'mixed' if noisy else 'clean'}-{hop}-{variant}-{'paced' if paced else 'unpaced'}"
                    result = summarize(reference, out, sections, trace, hop, delay, paced)
                    result["input_sha256"] = pcm_hash(samples)
                    result["reference_sha256"] = pcm_hash(reference)
                    deterministic = (result["output_sha256"],
                                     [(f["advisory"]["prob_pct"], f["advisory"]["advisory_active"])
                                      if f["advisory"] else None for f in trace])
                    if paced and deterministic != baseline:
                        raise ValueError(f"{tag}: pacing changed the audio or advisory")
                    baseline = deterministic
                    (output / f"{tag}.json").write_text(json.dumps(trace) + "\n")
                    report["runs"][tag] = result
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(f"{len(report['runs'])} matched synthetic runs: {output / 'report.json'}")


if __name__ == "__main__":
    main()
