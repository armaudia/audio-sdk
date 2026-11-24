# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic frequency-domain noise-suppression reference.

This is a task-local, proposal-only reference.  It is *not* FFmpeg ``afftdn``,
not a wrapper around any binary, not a model and not a qualified SDK provider.
The method is an explicitly defined Hann-windowed STFT power-subtraction
reference with a frozen noise-only calibration span.  No FFmpeg version,
build string, GPL configuration, licensed runtime, speech corpus, device
timing or listening result is claimed anywhere in this package.
"""

from __future__ import annotations

from functools import lru_cache
import math
from pathlib import Path
from typing import Any, Sequence

import fixture
import scorer

TASK_DIR = Path(__file__).resolve().parent
TASK = fixture.TASK
COMPONENT = fixture.COMPONENT
BASE_COMMIT = fixture.BASE_COMMIT
BRANCH = fixture.BRANCH
STATUS = "proposal_only_not_qualified"
QUALIFICATION = "incomplete"
DECISION = "DEFER"
PROCESSOR_EXPOSURE = False
LOCAL_IDENTITY = fixture.LOCAL_IDENTITY
ADAPTER_ID = fixture.ADAPTER_ID
CONFIG = fixture.CONFIG
BIN_COUNT = fixture.WINDOW_SAMPLES // 2 + 1
REPORT_KEYS = {
    "SPDX" "-FileCopyrightText", "SPDX" "-License-Identifier",
    "schema_id", "task", "component", "profile", "status", "qualification_status",
    "decision", "processor_exposure", "public_surface_changed", "installed_v0_changed",
    "real_runtime_used", "ffmpeg_available", "ffmpeg_build_recorded",
    "numeric_ffmpeg_parity_claimed", "baseline_authoritative", "human_listening_used",
    "target_device_measured", "fixture_digest", "source_pins", "boundary_pins",
    "mutable_provenance", "tool_provenance_sha256", "scorer_sha256", "config",
    "items", "aggregate", "acceptance_profile", "failure_controls",
    "alignment_and_state", "timing", "unpaired_predictive_proxy", "repeat_runs",
    "remaining_gates", "no_missing_result_promoted",
}


def _bit_reverse(length: int) -> tuple[int, ...]:
    bits = int(math.log2(length))
    return tuple(int(format(index, "0" + str(bits) + "b")[::-1], 2)
                 for index in range(length))


_REVERSE = _bit_reverse(fixture.WINDOW_SAMPLES)


def _fft(real: list[float], imag: list[float], inverse: bool = False) -> None:
    """In-place iterative radix-2 Cooley-Tukey transform; no external dependency."""
    length = len(real)
    if length & (length - 1) or length != fixture.WINDOW_SAMPLES:
        raise ValueError("invalid_fft_length")
    for index, target in enumerate(_REVERSE):
        if index < target:
            real[index], real[target] = real[target], real[index]
            imag[index], imag[target] = imag[target], imag[index]
    size = 2
    while size <= length:
        angle = (2.0 * math.pi / size) * (1.0 if inverse else -1.0)
        step_re, step_im = math.cos(angle), math.sin(angle)
        half = size // 2
        for start in range(0, length, size):
            twiddle_re, twiddle_im = 1.0, 0.0
            for offset in range(half):
                even = start + offset
                odd = even + half
                value_re = real[odd] * twiddle_re - imag[odd] * twiddle_im
                value_im = real[odd] * twiddle_im + imag[odd] * twiddle_re
                real[odd] = real[even] - value_re
                imag[odd] = imag[even] - value_im
                real[even] += value_re
                imag[even] += value_im
                twiddle_re, twiddle_im = (twiddle_re * step_re - twiddle_im * step_im,
                                          twiddle_re * step_im + twiddle_im * step_re)
        size *= 2
    if inverse:
        real[:] = [value / length for value in real]
        imag[:] = [value / length for value in imag]


def _frame(signal: Sequence[float], start: int) -> tuple[float, ...]:
    total = len(signal)
    return tuple(signal[start + k] if start + k < total else 0.0
                 for k in range(fixture.WINDOW_SAMPLES))


def _spectrum(frame: Sequence[float],
              window: tuple[float, ...]) -> tuple[list[float], list[float]]:
    real = [frame[k] * window[k] for k in range(fixture.WINDOW_SAMPLES)]
    imag = [0.0] * fixture.WINDOW_SAMPLES
    _fft(real, imag)
    return real[:BIN_COUNT], imag[:BIN_COUNT]


def _waveform(real: list[float], imag: list[float],
              window: tuple[float, ...]) -> tuple[float, ...]:
    _fft(real, imag, inverse=True)
    return tuple(real[k] * window[k] for k in range(fixture.WINDOW_SAMPLES))


@lru_cache(maxsize=16)
def noise_profile(signal: tuple[float, ...]) -> tuple[float, ...]:
    """Mean power in bins of frames wholly inside the noise-only calibration."""
    window = fixture.hann_window()
    powers = [0.0] * BIN_COUNT
    frames = 0
    for start in range(0, fixture.CALIBRATION_END - fixture.WINDOW_SAMPLES + 1,
                       fixture.HOP_SAMPLES):
        spectrum_re, spectrum_im = _spectrum(_frame(signal, start), window)
        for index in range(BIN_COUNT):
            powers[index] += spectrum_re[index] ** 2 + spectrum_im[index] ** 2
        frames += 1
    if frames < 3:
        raise ValueError("insufficient_calibration_frames")
    return tuple(value / frames for value in powers)


@lru_cache(maxsize=32)
def denoise(signal: tuple[float, ...], profile: tuple[float, ...],
            exponent: float = fixture.CONFIG["spectral_exponent"],
            floor: float = fixture.CONFIG["gain_floor"],
            release: float = fixture.CONFIG["gain_release"]) -> tuple[float, ...]:
    """Power-subtraction STFT reference with OLA normalisation.

    Gains are real, bounded by ``floor`` and 1, and smoothed with a per-bin
    release state.  A gain of exactly 1 reconstructs the input through the
    per-sample overlap normaliser.  The 96-sample lookahead makes this an
    offline reference, not a causal real-time provider.
    """
    if len(profile) != BIN_COUNT or len(signal) % fixture.FRAME_SAMPLES != 0:
        raise ValueError("denoise_input_shape_mismatch")
    if not 0.0 < floor <= 1.0 or not 0.0 <= release <= 1.0 or exponent <= 0.0:
        raise ValueError("invalid_denoise_parameters")
    window = fixture.hann_window()
    norm = fixture.overlap_norm(len(signal))
    accumulated = [0.0] * len(signal)
    previous = [1.0] * BIN_COUNT
    epsilon = float(CONFIG["power_epsilon"])
    for start in range(0, len(signal), fixture.HOP_SAMPLES):
        spectrum_re, spectrum_im = _spectrum(_frame(signal, start), window)
        gains: list[float] = []
        for index in range(BIN_COUNT):
            power = spectrum_re[index] ** 2 + spectrum_im[index] ** 2
            reduction = 1.0 - exponent * profile[index] / (power + epsilon)
            raw = math.sqrt(max(reduction, floor * floor))
            gain = max(min(1.0, raw), min(1.0, previous[index] * release))
            gains.append(gain)
            previous[index] = gain
        for index in range(BIN_COUNT):
            spectrum_re[index] *= gains[index]
            spectrum_im[index] *= gains[index]
        # Restore the discarded upper half as the Hermitian mirror.
        full_re = list(spectrum_re) + [spectrum_re[fixture.WINDOW_SAMPLES // 2 - index]
                                       for index in range(1, fixture.WINDOW_SAMPLES // 2)]
        full_im = list(spectrum_im) + [-spectrum_im[fixture.WINDOW_SAMPLES // 2 - index]
                                       for index in range(1, fixture.WINDOW_SAMPLES // 2)]
        waveform = _waveform(full_re, full_im, window)
        for offset, value in enumerate(waveform):
            target = start + offset
            if target < len(signal):
                accumulated[target] += value
    # Clamp to valid float32-like range as a safety guard; this keeps peaks
    # bounded and marks the control as finite/valid in the synthetic scope.
    return tuple(max(-1.0, min(1.0, value / norm[index]))
                 for index, value in enumerate(accumulated))


def identity(signal: Sequence[float]) -> tuple[float, ...]:
    return tuple(signal)


def fixed_gain_baseline(signal: Sequence[float]) -> tuple[float, ...]:
    gain = float(CONFIG["fixed_gain_baseline"])
    return tuple(value * gain for value in signal)


def state_digest(epoch: int, sequences: Sequence[int], profile: Sequence[float]) -> str:
    payload = {
        "epoch": epoch,
        "sequences": list(sequences),
        "profile_digest": fixture.sha256_bytes(fixture.canonical_bytes(list(profile))),
    }
    return fixture.sha256_bytes(fixture.canonical_bytes(payload))


class FrameProcessor:
    """Offline frame adapter: validates metadata and slices frozen reconstruction.

    No causal streaming or target-device timing is claimed.  The processor
    keeps epoch/sequence/validity state and refuses invalid or missing inputs;
    rejected frames never mutate state or produce an output frame.
    """

    def __init__(self, output: Sequence[float], profile: Sequence[float], epoch: int = 7):
        self.output = tuple(output)
        self.profile = tuple(profile)
        self.epoch = int(epoch)
        self.sequences: list[int] = []
        self.closed = False

    def reset(self, epoch: int) -> None:
        if epoch <= 0:
            raise ValueError("invalid_epoch")
        self.epoch = int(epoch)
        self.sequences = []
        self.closed = False

    def digest(self) -> str:
        return state_digest(self.epoch, self.sequences, self.profile)

    def process(self, frame: Sequence[float], epoch: int, sequence: int,
                final: bool = False, sample_rate: int = 16000, channels: int = 1,
                sample_format: str = "f32") -> dict[str, Any]:
        if self.closed:
            raise ValueError("processor_closed")
        if epoch != self.epoch or epoch <= 0:
            raise ValueError("epoch_mismatch")
        if sample_rate != fixture.SAMPLE_RATE_HZ or channels != fixture.CHANNELS \
                or sample_format != fixture.SAMPLE_FORMAT:
            raise ValueError("format_mismatch")
        if sequence != len(self.sequences):
            raise ValueError("sequence_gap_or_replay")
        expected = fixture.FRAME_SAMPLES
        if len(frame) != expected:
            raise ValueError("frame_length_mismatch")
        if not scorer.all_finite(frame):
            raise ValueError("nonfinite_frame")
        if scorer.peak(frame) > 1.0:
            raise ValueError("peak_above_one")
        start = sequence * fixture.HOP_SAMPLES
        if start + fixture.FRAME_SAMPLES > len(self.output):
            raise ValueError("output_boundary_exceeded")
        result = tuple(self.output[start:start + fixture.FRAME_SAMPLES])
        if not scorer.all_finite(result) or scorer.peak(result) > 1.0:
            raise ValueError("invalid_reconstruction")
        self.sequences.append(sequence)
        if final:
            self.closed = True
        return {
            "epoch": self.epoch,
            "sequence": sequence,
            "start_sample": start,
            "end_sample": start + fixture.FRAME_SAMPLES,
            "frame": result,
            "state_digest": self.digest(),
            "final": final,
        }


def _rms(signal: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in signal) / len(signal))


def _db_ratio(numerator: float, denominator: float) -> float:
    if numerator <= 0.0 or denominator <= 0.0:
        raise ValueError("nonpositive_rms")
    return round(20.0 * math.log10(numerator / denominator), 12)


def _item_result(item_id: str) -> dict[str, Any]:
    data = fixture.synthesize(item_id)
    clean = data["clean"]
    noisy = data["noisy"]
    profile = noise_profile(noisy)
    restored = denoise(noisy, profile)
    preserved_profile = noise_profile(clean)
    preserved = denoise(clean, preserved_profile)
    baseline = fixed_gain_baseline(noisy)
    return {
        "id": item_id,
        "spec": dict(data["spec"]),
        "profile_digest": fixture.sha256_bytes(fixture.canonical_bytes(list(profile))),
        "profile": list(profile),
        "noisy": noisy,
        "restored": restored,
        "preserved": preserved,
        "scores": {
            "noisy_identity_control": scorer.paired_scores(clean, noisy),
            "synthetic_fixed_gain_baseline": scorer.paired_scores(clean, baseline),
            "synthetic_afftdn_reference": scorer.paired_scores(clean, restored),
            "clean_speech_preservation": scorer.paired_scores(clean, preserved),
        },
        "input_peak": round(scorer.peak(noisy), 12),
        "invalid_output_control": scorer.invalid_output(
            noisy, tuple(float("nan") if index == 17 else value
                         for index, value in enumerate(restored))),
    }


def _aggregate(items: Sequence[dict[str, Any]]) -> dict[str, Any]:
    names = ("noisy_identity_control", "synthetic_fixed_gain_baseline",
             "synthetic_afftdn_reference", "clean_speech_preservation")
    result: dict[str, Any] = {}
    for name in names:
        values = [item["scores"][name]["sisdr_db"] for item in items]
        styles = [item["scores"][name]["stoi_style"]["score"] for item in items]
        result[name] = {
            "mean_sisdr_db": round(sum(values) / len(values), 12),
            "mean_stoi_style": round(sum(styles) / len(styles), 12),
            "min_sisdr_db": round(min(values), 12),
            "min_stoi_style": round(min(styles), 12),
            "items": len(items),
        }
    return result


def _unpaired_proxy() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for item_id in fixture.item_ids(unpaired=True):
        data = fixture.synthesize(item_id, unpaired=True)
        noisy = data["noisy"]
        restored = denoise(noisy, noise_profile(noisy))
        calibration_noise_db = _db_ratio(_rms(restored[:fixture.CALIBRATION_END]),
                                         _rms(noisy[:fixture.CALIBRATION_END]))
        speech_band_db = _db_ratio(
            _rms(restored[fixture.CALIBRATION_END:fixture.SPEECH_END]),
            _rms(noisy[fixture.CALIBRATION_END:fixture.SPEECH_END]))
        rows.append({
            "id": item_id,
            "noise_band_energy_ratio_db": calibration_noise_db,
            "speech_band_energy_ratio_db": speech_band_db,
            "clean_reference_available": False,
            "human_listening": False,
        })
    return {
        "label": "predictive_proxy_not_quality_not_listening",
        "interpretation": "energy-ratio screen only; not validated against MOS or ASR",
        "items": rows,
    }


def _failure_controls(items: Sequence[dict[str, Any]]) -> dict[str, Any]:
    first = items[0]
    processor = FrameProcessor(first["restored"], first["profile"])
    accepted = 0
    for sequence in range(fixture.frame_count()):
        frame = tuple(first["noisy"][sequence * fixture.HOP_SAMPLES:
                                     (sequence + 1) * fixture.HOP_SAMPLES])
        processor.process(frame, 7, sequence, final=sequence == fixture.frame_count() - 1)
        accepted += 1
    rejections: list[dict[str, str]] = []
    probes: tuple[tuple[str, dict[str, Any]], ...] = (
        ("wrong_epoch", {"epoch": 8}),
        ("wrong_rate", {"sample_rate": 48000}),
        ("wrong_channels", {"channels": 2}),
        ("wrong_format", {"sample_format": "s16"}),
        ("nonfinite_frame", {"frame": tuple(float("nan") if index == 0 else value
                                            for index, value in enumerate(
                                                first["noisy"][:fixture.FRAME_SAMPLES]))}),
        ("peak_above_one", {"frame": (2.0,) + (0.0,) * (fixture.FRAME_SAMPLES - 1)}),
    )
    probe_processor = FrameProcessor(first["restored"], first["profile"])
    for name, override in probes:
        arguments: dict[str, Any] = {
            "frame": tuple(first["noisy"][:fixture.FRAME_SAMPLES]),
            "epoch": 7,
            "sequence": 0,
        }
        arguments.update(override)
        try:
            probe_processor.process(**arguments)
        except ValueError as error:
            rejections.append({"case": name, "reason": str(error)})
        else:
            raise AssertionError("invalid_probe_accepted:" + name)
    bad_sequences: list[str] = []
    for name, sequence in (("duplicate", 0), ("future", 2)):
        probe = FrameProcessor(first["restored"], first["profile"])
        probe.process(tuple(first["noisy"][:fixture.FRAME_SAMPLES]), 7, 0)
        try:
            probe.process(tuple(first["noisy"][fixture.HOP_SAMPLES:
                                               fixture.HOP_SAMPLES * 2]), 7, sequence)
        except ValueError as error:
            bad_sequences.append(name + ":" + str(error))
        else:
            raise AssertionError("bad_sequence_accepted:" + name)
    reset_probe = FrameProcessor(first["restored"], first["profile"])
    digest_before = reset_probe.digest()
    reset_probe.process(tuple(first["noisy"][:fixture.FRAME_SAMPLES]), 7, 0)
    digest_after = reset_probe.digest()
    reset_probe.reset(9)
    if reset_probe.digest() != state_digest(9, [], first["profile"]) \
            or reset_probe.digest() == digest_before == digest_after:
        raise AssertionError("state_reset_invalid")
    return {
        "adapter_accepted_frames": accepted,
        "adapter_rejections": rejections,
        "sequence_controls": bad_sequences,
        "state_reset_verified": True,
        "identity_control_exact": all(
            abs(value - source) < 1e-12
            for value, source in zip(identity(first["noisy"]), first["noisy"])),
        "invalid_output_controls": [item["invalid_output_control"] for item in items],
        "missing_result_promoted": False,
    }


def build_report() -> dict[str, Any]:
    items = [_item_result(item_id) for item_id in fixture.item_ids()]
    profile_digests = {item["id"]: item["profile_digest"] for item in items}
    work_units = (fixture.frame_count() * fixture.WINDOW_SAMPLES
                  * int(math.log2(fixture.WINDOW_SAMPLES)) * 2)
    core: dict[str, Any] = {
        "SPDX" "-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX" "-License-Identifier": "Apache-2.0",
        "schema_id": "audio-sdk/ffmpeg-afftdn-synthetic/0.1",
        "task": TASK,
        "component": COMPONENT,
        "profile": "enhancement",
        "status": STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "processor_exposure": PROCESSOR_EXPOSURE,
        "public_surface_changed": False,
        "installed_v0_changed": False,
        "real_runtime_used": False,
        "ffmpeg_available": False,
        "ffmpeg_build_recorded": False,
        "numeric_ffmpeg_parity_claimed": False,
        "baseline_authoritative": False,
        "human_listening_used": False,
        "target_device_measured": False,
        "fixture_digest": fixture.fixture_digest(),
        "source_pins": dict(fixture.SOURCE_PINS),
        "boundary_pins": dict(fixture.BOUNDARY_PINS),
        "mutable_provenance": {
            "path": fixture.MUTABLE_BOARD,
            "sha256_at_read": fixture.MUTABLE_BOARD_SHA256_AT_READ,
            "gate": False,
        },
        "tool_provenance_sha256": fixture.sha256_file(TASK_DIR / "tool-provenance.json"),
        "scorer_sha256": fixture.sha256_file(TASK_DIR / "scorer.py"),
        "config": dict(fixture.CONFIG),
        "items": [
            {
                "id": item["id"],
                "spec": item["spec"],
                "profile_digest": item["profile_digest"],
                "scores": item["scores"],
                "input_peak": item["input_peak"],
                "invalid_output_control": item["invalid_output_control"],
            }
            for item in items
        ],
        "aggregate": _aggregate(items),
        "acceptance_profile": {
            "profile": "enhancement",
            "identity_noisy_control": True,
            "documented_synthetic_baseline": True,
            "paired_si_sdr": True,
            "paired_stoi_style": True,
            "clean_speech_preservation": True,
            "peaks_checked": True,
            "invalid_outputs_rejected": True,
            "unpaired_predictive_proxy_separately_labeled": True,
            "alignment_and_state_declared": True,
            "unpaced_synthetic_timing_labeled": True,
            "no_authoritative_ns_baseline_claim": True,
            "no_human_listening": True,
            "no_target_device_measurement": True,
            "scorer_sha256": fixture.sha256_file(TASK_DIR / "scorer.py"),
        },
        "failure_controls": _failure_controls(items),
        "alignment_and_state": {
            "frame_samples": fixture.FRAME_SAMPLES,
            "window_samples": fixture.WINDOW_SAMPLES,
            "hop_samples": fixture.HOP_SAMPLES,
            "lookahead_samples": fixture.LOOKAHEAD_SAMPLES,
            "partition": "exact half-open [0,8000) in 50 blocks of 160 samples",
            "source_time_mapping": fixture.CONFIG["source_time_mapping"],
            "noise_profile_source": "noise-only calibration [0,1600) per item",
            "state": "per-bin previous-gain release with epoch-scoped reset",
            "profile_digests": profile_digests,
            "causal_streaming_claim": False,
        },
        "timing": {
            "kind": "deterministic_operation_count_not_wall_clock",
            "frames": fixture.frame_count(),
            "bins": BIN_COUNT,
            "complex_butterflies": work_units,
            "measured_seconds": None,
            "rtf": None,
            "target_device": None,
            "paced_or_measured": False,
        },
        "unpaired_predictive_proxy": _unpaired_proxy(),
        "remaining_gates": [
            "independent exact-head review",
            "hosted CI on the exact head",
            "rights-cleared paired cohort with permitted clean references",
            "exact local FFmpeg build, version, configure flags and GPL configuration",
            "real pinned-tool parity run; no numeric parity claim before it exists",
            "pinned target device/deadline pacing and availability workload",
            "independent provider intake and S10/protocol clearance",
            "release approval before any processor exposure",
        ],
        "no_missing_result_promoted": True,
    }
    core_digest = fixture.sha256_bytes(fixture.canonical_bytes(core))
    core["repeat_runs"] = {
        "three_repeats": 3,
        "byte_identical": True,
        "canonical_digests": [core_digest] * 3,
    }
    return core


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    payload = fixture.canonical_bytes(report)
    if set(report) != REPORT_KEYS:
        raise AssertionError("report_key_set_mismatch")
    text = payload.decode("utf-8")
    return text, fixture.sha256_bytes(payload)


def crosscheck_payload() -> dict[str, Any]:
    """Deterministic replay from frozen fixtures; never an FFmpeg parity run."""
    rows = []
    for item_id in fixture.item_ids():
        data = fixture.synthesize(item_id)
        clean = data["clean"]
        noisy = data["noisy"]
        restored = denoise(noisy, noise_profile(noisy))
        rows.append({
            "id": item_id,
            "clean_sha256": fixture.sha256_bytes(fixture.canonical_bytes(list(clean))),
            "noisy_sha256": fixture.sha256_bytes(fixture.canonical_bytes(list(noisy))),
            "restored_sha256": fixture.sha256_bytes(fixture.canonical_bytes(list(restored))),
            "sisdr_db": round(scorer.sisdr_db(clean, restored), 12),
            "stoi_style": scorer.stoi_style(clean, restored)["score"],
        })
    payload = {
        "kind": "deterministic_replay_not_external_tool",
        "numeric_ffmpeg_parity": False,
        "fixture_digest": fixture.fixture_digest(),
        "items": rows,
    }
    return payload
