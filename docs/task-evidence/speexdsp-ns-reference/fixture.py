# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic control for the installed speex.ns.v0 provider.

No corpus, model, weights or real audio is used. The full frame stream is
processed by the installed shared library through the shipped stdlib ctypes
binding. SI-SDR uses zero-mean v1 arithmetic; STOI uses the pinned pystoi
0.4.1 non-extended scorer when that dependency is present.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path

FRAME = 160
RATE = 16000
SCHEMA = "audio-sdk/task-evidence/speexdsp-ns-reference/0.1"
BASE_COMMIT = "3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41"
PROVIDER = "speex.ns.v0"
PINS = [
    ("research/voice-enhancement-20261101/candidate_matrix.csv",
     "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
     "Task matrix: SpeexDSP NS evaluated in CLN pilot, separate from its VAD and MDF rows; compared with WebRTC NS, RNNoise and noisy identity."),
    ("research/noise_suppression_candidate_census.md",
     "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
     "Census: no-weight classical NS baseline; pin build and attenuation; 30-pair DNS pilot is exploratory, not a representative holdout."),
    ("audio-benchmark-platform/audio-sdk/core/providers/speex/speex_provider.c",
     "d1a98e3aff897375db4f0fc7668329be5254faa361ccaba1635a5089ea8a71e6",
     "Frozen v0 policy: 16 kHz mono 160-sample frames, denoise on, AGC/dereverb off, VAD computed but not exported, -20 dB suppression, declared 160-sample buffering, PCM16 quantization."),
    ("adapters/speexdsp/adapter.json",
     "8daaf37bb19ae75bb705e31e98964cbf732e666b140823dfa1bd4f5f3496ad3c",
     "Offline CLN-01 waveform adapter identity at source commit 7a158783; weights not required; distinct from the SDK provider."),
    ("research/noise_suppression_assets_20261027.json",
     "35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4",
     "SpeexDSP-NS-only asset record: Xiph 7a158783, BSD-3-Clause, pinned preprocess header and native library digests."),
    ("research/selected_audio_enhancement_candidates.md",
     "0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946",
     "Source-reported pilot for NS-only: median SNR gain +0.560 dB, STOI .9375, RTF .0006, measured 20 ms delay; STOI regression made it unsuitable as default on that subset."),
    ("REALTIME_COMPONENT_CANDIDATES.md",
     "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
     "Component inventory: source-reported DNS pilot mean delta SI-SDR +1.06 dB, delta STOI -0.0057, RTF about .0006; experimental C++ backend exists."),
]


class LCG:
    """Version-stable 32-bit LCG; no dependency on Python's random internals."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def uniform(self) -> float:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return 2.0 * (self.state / 4294967296.0) - 1.0


def clean_speech(n: int) -> list[float]:
    """Deterministic band-limited voiced surrogate, with 20 ms edge ramps."""
    out = []
    for i in range(n):
        t = i / RATE
        env = 0.5 * (1.0 + math.sin(2.0 * math.pi * 2.5 * t))
        env *= min(1.0, i / 320.0, (n - i) / 320.0)
        out.append(0.6 * env * (
            math.sin(2.0 * math.pi * 120.0 * t)
            + 0.5 * math.sin(2.0 * math.pi * 240.0 * t)
            + 0.25 * math.sin(2.0 * math.pi * 360.0 * t)))
    return out


def noise(n: int) -> list[float]:
    rng = LCG(0x53505845)
    return [rng.uniform() for _ in range(n)]


def impulse(n: int, at: int = 4000) -> list[float]:
    out = [0.0] * n
    out[at] = 0.9
    return out


def mixture(clean: list[float], noise_signal: list[float], snr_db: float) -> list[float]:
    clean_power = sum(x * x for x in clean) / len(clean)
    noise_power = sum(x * x for x in noise_signal) / len(noise_signal)
    gain = math.sqrt(clean_power / (noise_power * 10 ** (snr_db / 10.0)))
    return [c + gain * z for c, z in zip(clean, noise_signal)]


def si_sdr_db(reference: list[float] | None, estimate: list[float] | None) -> tuple[float | None, str | None]:
    if reference is None or estimate is None:
        return None, "missing_reference_or_output"
    if len(reference) != len(estimate):
        return None, "length_mismatch"
    if not reference or not all(math.isfinite(v) for v in reference + estimate):
        return None, "invalid_input"
    n = len(reference)
    rm = sum(reference) / n
    em = sum(estimate) / n
    ref = [v - rm for v in reference]
    est = [v - em for v in estimate]
    denom = sum(v * v for v in ref)
    if denom == 0.0:
        return None, "zero_reference"
    a = sum(x * y for x, y in zip(est, ref)) / denom
    proj = [a * v for v in ref]
    target = sum(v * v for v in proj)
    residual = sum((x - y) ** 2 for x, y in zip(est, proj))
    if target == 0.0:
        return None, "zero_projection"
    if residual == 0.0:
        return None, "exact_reconstruction"
    return round(10.0 * math.log10(target / residual), 6), None


def stoi_score(reference: list[float] | None, estimate: list[float] | None) -> tuple[float | None, str | None]:
    if reference is None or estimate is None:
        return None, "missing_reference_or_output"
    if len(reference) != len(estimate) or not reference:
        return None, "invalid_input"
    if not all(math.isfinite(v) for v in reference + estimate) or not any(reference):
        return None, "invalid_input"
    try:
        import numpy as np
        from pystoi import stoi
    except ImportError:
        return None, "missing_pinned_scorer"
    try:
        value = float(stoi(np.asarray(reference), np.asarray(estimate), RATE, extended=False))
    except Exception:
        return None, "metric_undefined"
    if not math.isfinite(value):
        return None, "metric_undefined"
    return round(value, 6), None


def features(samples: list[float]) -> dict:
    peak = max((abs(v) for v in samples), default=0.0)
    return {
        "samples": len(samples),
        "finite": all(math.isfinite(v) for v in samples),
        "peak_abs": round(peak, 6),
        "clipped_or_nonfinite": sum(1 for v in samples if not math.isfinite(v) or abs(v) >= 1.0),
    }


def process_stream(samples: list[float], binding, epoch: int = 1):
    """Drive one full stream; return raw output, metadata, call durations and RSS delta."""
    reg = binding.Registry()
    session = reg.session(PROVIDER, epoch=epoch)
    raw: list[float] = []
    meta: list[dict] = []
    durations: list[float] = []
    start_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    wall_start = time.perf_counter()
    try:
        for offset in range(0, len(samples), FRAME):
            chunk = samples[offset:offset + FRAME]
            valid = len(chunk)
            chunk = chunk + [0.0] * (FRAME - valid)
            t0 = time.perf_counter()
            out, result = session.process(chunk, valid_count=valid, final=valid < FRAME)
            durations.append(time.perf_counter() - t0)
            raw.extend(out)
            meta.append({"source_first": result.source_first_sample,
                         "valid_offset": result.valid_offset,
                         "valid_count": result.valid_count,
                         "produced": result.produced_count,
                         "epoch": result.epoch})
        drain_start = time.perf_counter()
        for out, result in session.drain():
            raw.extend(out)
            meta.append({"source_first": result.source_first_sample,
                         "valid_offset": result.valid_offset,
                         "valid_count": result.valid_count,
                         "produced": result.produced_count,
                         "epoch": result.epoch})
        drain_wall = time.perf_counter() - drain_start
        wall = time.perf_counter() - wall_start
    finally:
        session.close()
        reg.close()
    end_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return raw, meta, durations, {
        "stream_wall_s": round(wall, 6),
        "drain_wall_s": round(drain_wall, 6),
        "maxrss_delta_bytes": end_rss - start_rss,
    }


def process_frames(binding, samples: list[float], epoch: int = 1):
    """Process-only run (no drain), for like-for-like state comparisons."""
    reg = binding.Registry()
    session = reg.session(PROVIDER, epoch=epoch)
    raw: list[float] = []
    try:
        for off in range(0, len(samples), FRAME):
            out, _ = session.process(samples[off:off + FRAME])
            raw.extend(out)
    finally:
        session.close()
        reg.close()
    return raw


def align(raw: list[float], meta: list[dict], n: int) -> list[float]:
    """Map the declared source interval [0,n) onto raw output; fail closed on geometry drift."""
    if not meta or meta[0]["source_first"] != -FRAME:
        raise AssertionError("missing declared 160-sample startup padding")
    for i, item in enumerate(meta):
        if item["source_first"] != -FRAME + i * FRAME:
            raise AssertionError("non-contiguous source mapping")
        if item["produced"] != FRAME or item["valid_offset"] not in (0, FRAME):
            raise AssertionError("invalid produced/valid geometry")
    if len(raw) < FRAME + n:
        raise AssertionError("truncated raw output")
    return raw[FRAME:FRAME + n]


def condition_metrics(clean: list[float], noisy: list[float], aligned: list[float]) -> dict:
    ident_si, ident_si_reason = si_sdr_db(clean, noisy)
    proc_si, proc_si_reason = si_sdr_db(clean, aligned)
    ident_stoi, ident_stoi_reason = stoi_score(clean, noisy)
    proc_stoi, proc_stoi_reason = stoi_score(clean, aligned)
    ref_power = sum(v * v for v in noisy) / len(noisy)
    out_power = sum(v * v for v in aligned) / len(aligned)
    return {
        "si_sdr_db": {
            "identity_noisy": ident_si,
            "provider": proc_si,
            "paired_delta": (round(proc_si - ident_si, 6)
                             if proc_si is not None and ident_si is not None else None),
            "invalid_reasons": [r for r in (ident_si_reason, proc_si_reason) if r],
        },
        "stoi": {
            "identity_noisy": ident_stoi,
            "provider": proc_stoi,
            "paired_delta": (round(proc_stoi - ident_stoi, 6)
                             if proc_stoi is not None and ident_stoi is not None else None),
            "invalid_reasons": [r for r in (ident_stoi_reason, proc_stoi_reason) if r],
        },
        "preservation": {
            "rms_gain_ratio": (round(math.sqrt(out_power / ref_power), 6)
                               if ref_power > 0 else None),
        },
        "output": features(aligned),
        "input": features(noisy),
    }


def installed_identity(build_id: str) -> dict:
    return {
        "provider": PROVIDER,
        "build_id": build_id,
        "contract_version": "0.1",
        "format": "mono float32 16000 Hz 160 samples per call",
        "base_commit": BASE_COMMIT,
    }


def load_binding():
    """Import the shipped ctypes binding against an explicitly installed library."""
    if not os.environ.get("AUDIO_SDK_LIBRARY") or not os.environ.get("AUDIO_SDK_EXPECTED_BUILD_ID"):
        raise RuntimeError("set AUDIO_SDK_LIBRARY and AUDIO_SDK_EXPECTED_BUILD_ID first")
    import audio_sdk  # noqa: PLC0415 - environment is validated by the binding itself
    return audio_sdk


def import_control(env_overrides: dict[str, str], needle: str) -> dict:
    env = os.environ.copy()
    env.update(env_overrides)
    proc = subprocess.run([sys.executable, "-c", "import audio_sdk"], env=env,
                          capture_output=True, text=True, check=False)
    ok = proc.returncode != 0 and needle in proc.stderr
    return {"status": "pass" if ok else "fail",
            "expected": needle,
            "observed": proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "",
            "exit_code": proc.returncode}


def collect(binding, conformance_path: Path) -> dict:
    build_id = os.environ["AUDIO_SDK_EXPECTED_BUILD_ID"]
    conformance = json.loads(conformance_path.read_text())
    if conformance.get("provider_id") != PROVIDER or conformance.get("build_id") != build_id:
        raise AssertionError("conformance report does not match the installed runtime")

    n = 32000  # 2 s, 200 frames; synthetic only
    clean = clean_speech(n)
    nz = noise(n)
    conditions = {}
    runtime_measurements = {}
    for name, noisy in (
        ("noisy_snr10", mixture(clean, nz, 10.0)),
        ("noisy_snr0", mixture(clean, nz, 0.0)),
        ("clean_only", clean[:]),
        ("noise_only", [0.6 * v for v in nz]),
        ("silence", [0.0] * n),
    ):
        raw, meta, durations, measured = process_stream(noisy, binding)
        aligned = align(raw, meta, n)
        conditions[name] = condition_metrics(clean, noisy, aligned)
        runtime_measurements[name] = {
            "process_frames": len(meta) - 1,
            "drain_frames": 1,
            "process_duration_ms": {
                "median": round(1000 * statistics.median(durations[:-1]), 6),
                "max": round(1000 * max(durations[:-1]), 6),
            },
            "stream_wall_s": measured["stream_wall_s"],
            "drain_wall_s": measured["drain_wall_s"],
            "maxrss_delta_bytes": measured["maxrss_delta_bytes"],
            "first_valid_output_s": round(durations[0] + durations[1], 6),
        }

    # Content mapping measured with an isolated transient, independent of metrics above.
    imp = impulse(n)
    raw_imp, meta_imp, _, _ = process_stream(imp, binding)
    aligned_imp = align(raw_imp, meta_imp, n)
    peak_at = max(range(n), key=lambda i: abs(aligned_imp[i]))
    alignment = {
        "declared_buffering_samples": FRAME,
        "declared_first_source_sample": meta_imp[0]["source_first"],
        "measured_impulse_index": peak_at,
        "expected_impulse_index": 4000,
        "measured_content_lag_samples": peak_at - 4000,
        "source_interval": [0, n],
        "raw_interval": [-FRAME, n],
        "valid_output_samples": sum(m["valid_count"] for m in meta_imp),
    }

    # State controls: two instances and an epoch reset must not couple or retain state.
    short = clean[:640]
    a_raw = process_frames(binding, short)
    b_raw = process_frames(binding, [0.3 * v for v in short])
    reg = binding.Registry()
    session = reg.session(PROVIDER, epoch=1)
    try:
        first = []
        for off in range(0, 640, FRAME):
            out, _ = session.process(short[off:off + FRAME])
            first.extend(out)
        session.reset(epoch=2, first_input_sample=0)
        second = []
        epochs = []
        for off in range(0, 640, FRAME):
            out, result = session.process(short[off:off + FRAME])
            epochs.append(result.epoch)
            second.extend(out)
    finally:
        session.close()
        reg.close()
    c_raw = process_frames(binding, short, epoch=2)
    state = {
        "separate_instances_uncoupled": a_raw == c_raw,
        "different_stimuli_differ": a_raw != b_raw,
        "reset_bit_identical": first == second,
        "reset_epoch_propagated": epochs == [2] * (len(short) // FRAME),
        "fresh_epoch2_bit_identical_to_reset": second == c_raw,
    }

    # Invalid, missing and nonfinite controls are explicit and never scored.
    reg = binding.Registry()
    session = reg.session(PROVIDER)
    try:
        try:
            session.process([float("nan")] * FRAME)
            nan_rejected = False
        except Exception:
            nan_rejected = True
    finally:
        session.close()
        reg.close()
    baseline = process_frames(binding, short)
    reg = binding.Registry()
    session = reg.session(PROVIDER)
    try:
        if not nan_rejected:
            session.process([float("nan")] * FRAME)
        after = []
        for off in range(0, 640, FRAME):
            out, _ = session.process(short[off:off + FRAME])
            after.extend(out)
    finally:
        session.close()
        reg.close()
    missing_si, missing_reason = si_sdr_db(None, [0.0] * 10)
    truncated_si, truncated_reason = si_sdr_db(clean[:n], aligned_imp[:n - 1])
    controls = {
        "missing_library": import_control({"AUDIO_SDK_LIBRARY": "/nonexistent/libaudio_sdk.dylib"},
                                          "AUDIO_SDK_LIBRARY"),
        "wrong_build_id": import_control({"AUDIO_SDK_EXPECTED_BUILD_ID": "audio-sdk/0.1.0+sha256:bad"},
                                         "identity mismatch"),
        "nonfinite_input_rejected": {"status": "pass" if nan_rejected else "fail",
                                     "expected": "invalid_argument on NaN frame",
                                     "state_unchanged_after_rejection": baseline == after},
        "missing_reference": {"status": "pass" if missing_si is None else "fail",
                              "reason": missing_reason},
        "truncated_output": {"status": "pass" if truncated_si is None else "fail",
                             "reason": truncated_reason},
        "invalid_config_conformance": {
            "status": "pass" if all(c["result"] == "pass" for c in conformance["checks"]
                                    if c["id"].startswith("create.reject")) else "fail",
            "count": sum(1 for c in conformance["checks"] if c["id"].startswith("create.reject")),
        },
    }

    checks = conformance["checks"]
    report = {
        "schema_id": SCHEMA,
        "mode": "reference-verification",
        "profile": "Enhancement",
        "installed_identity": installed_identity(build_id),
        "source_pins": [{"path": p, "sha256": d, "summary": s} for p, d, s in PINS],
        "conformance": {
            "pass": conformance["summary"]["pass"],
            "fail": conformance["summary"]["fail"],
            "skip": conformance["summary"]["skip"],
            "result": conformance["result"],
            "descriptor_digest": conformance["descriptor_digest"],
            "report_sha256": hashlib.sha256(conformance_path.read_bytes()).hexdigest(),
        },
        "controls": controls,
        "alignment": alignment,
        "state": state,
        "conditions": conditions,
        "evidence_classes": {
            "synthetic_runtimes": "Installed library driven with deterministic model-free stimuli; no corpus or weights",
            "historical_source_reported": "Retained from pinned research only; not rerun or pooled with local scores",
            "real_audio_rights_qualified": "none; no result qualifies a candidate",
        },
        "all_controls_pass": all(
            (c["status"] == "pass" and c.get("state_unchanged_after_rejection", True))
            for c in controls.values()),
        "all_state_pass": all(state.values()) and alignment["measured_content_lag_samples"] == 0,
        "all_conformance_pass": conformance["result"] == "pass" and not conformance["summary"]["fail"] and not conformance["summary"]["skip"],
        "all_outputs_finite": all(c["output"]["finite"] for c in conditions.values()),
    }
    measurements = {
        "schema_id": SCHEMA + "/runtime-measurements",
        "non_deterministic": True,
        "installed_identity": installed_identity(build_id),
        "platform": {
            "system": platform.system(), "machine": platform.machine(),
            "python": sys.version.split()[0],
            "pystoi": _version("pystoi"), "numpy": _version("numpy"),
        },
        "pacing": "unpaced",
        "load": "one synthetic stream at a time, no competing load",
        "deadline_ns": None,
        "per_condition": runtime_measurements,
        "note": "ru_maxrss is a coarse process high-water mark; availability is the elapsed time to the first frame with valid samples. Neither a deadline nor a workload claim.",
    }
    return report, measurements


def _version(name: str) -> str | None:
    try:
        from importlib.metadata import version
        return version(name)
    except Exception:
        return None


def canonical_bytes(obj: dict) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: fixture.py <conformance-report.json> <report.json> <runtime-measurements.json>")
    conformance_path, report_path, measurements_path = map(Path, sys.argv[1:])
    report, measurements = collect(load_binding(), conformance_path)
    report_path.write_bytes(canonical_bytes(report))
    measurements_path.write_bytes(canonical_bytes(measurements))
    print(f"report_sha256={hashlib.sha256(report_path.read_bytes()).hexdigest()}")
    print(f"conformance={report['conformance']['pass']}/{report['conformance']['pass'] + report['conformance']['fail'] + report['conformance']['skip']}")
    print(f"all_controls_pass={report['all_controls_pass']} all_state_pass={report['all_state_pass']} "
          f"all_outputs_finite={report['all_outputs_finite']}")


if __name__ == "__main__":
    main()
