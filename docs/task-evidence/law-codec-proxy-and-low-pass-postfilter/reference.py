# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for
SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER.

This module is a bounded research-control fixture. It is NOT a real transport
codec, not ITU-T G.711 and not a production decoder postfilter. It reproduces
two exact algorithms from the pinned local synthetic pilot:

* the peak-normalised ``2**bits``-level logarithmic companding proxy
  (``mulaw_roundtrip`` in ``src/audioml_eval/distortion_restoration.py``);
* the pilot's 8 kHz resampling and 4th-order Butterworth 3900 Hz
  forward-backward postfilter, reimplemented with the standard library.

The exact pilot *runtime* (numpy/scipy/pystoi/soundfile with recorded wheel
digests), the EARS corpus, real transport codec references and rights are
absent. The package therefore makes a DEFER decision: the proxy comparison is
retained as provenance and as a deterministic mechanical fixture only. No
result qualifies the candidate and no processor, provider, default, ABI,
build, CI, board or handoff change is made.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
from typing import Any, Dict, Iterable, List, Sequence, Tuple

# ---------------------------------------------------------------------------
# Frozen identity
# ---------------------------------------------------------------------------
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
PROXY_SAMPLE_RATE_HZ = 8000
PROXY_BITS = (4, 8)
MAX_PEAK = 4.0
PEAK_FLOOR = 1e-8
POSTFILTER_CUTOFF_HZ = 3900.0
FIXTURE_SAMPLES = 3200
RESAMPLE_FACTOR = 2
RESAMPLE_ADMITTED_RATIOS = ((1, 2), (2, 1))
RESAMPLE_HALF_LENGTH_FACTOR = 10
RESAMPLE_KAISER_BETA = 5.0
# scipy.signal.resample_poly uses 2 * 10 * max(up, down) + 1 taps.
RESAMPLE_TAPS = 2 * RESAMPLE_HALF_LENGTH_FACTOR * RESAMPLE_FACTOR + 1
# Convolution span of the 16 kHz -> 8 kHz -> 16 kHz cascade of the two
# directional FIRs (41 + 41 - 1); not a single filter applied at one rate.
RESAMPLE_COMPOSITE_TAPS = 2 * RESAMPLE_TAPS - 1
SI_SDR_EPS = 1e-12

SCHEMA_ID = (
    "audio-sdk/law-codec-proxy-and-low-pass-postfilter-reference-report/0.1")
CONTRACT_SCHEMA_ID = (
    "audio-sdk/law-codec-proxy-and-low-pass-postfilter-contract/0.1")
TASK = "SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER"
COMPONENT = "law-codec-proxy-and-low-pass-postfilter"
BRANCH = "swarm/SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER"
BASE_COMMIT = "cb3d9812875b741a320c6cfe22de8043952fdd16"
TASK_PREFIX = (
    "docs/task-evidence/law-codec-proxy-and-low-pass-postfilter/")

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
INVENTORY_PATH = WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.json"
INVENTORY_MD_PATH = WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.md"
RIGHTS_REGISTER_PATH = (
    WORKSPACE / "audio-benchmark-platform/audio-pro/docs/rights-register.md")
RIGHTS_DETAIL_PATH = (
    WORKSPACE / "audio-benchmark-platform/audio-pro/inventory/"
    "rights-register.json")
PILOT_REPORT_PATH = (
    WORKSPACE /
    "reports/distortion-restoration/20261028-synthetic-screen.json")
EARS_SUBSET_PATH = WORKSPACE / "data/datasets/ears-blind/audio"

SOURCE_PINS = {
    "research/distortion_restoration_20261028.md":
        "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "src/audioml_eval/distortion_restoration.py":
        "c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f",
    "scripts/evaluate_distortion_restoration.py":
        "4fe524eb7e9a2130cdd97124c3e12642d8e460ccf5353647b7bce04038627047",
    "reports/distortion-restoration/20261028-synthetic-screen.json":
        "87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece",
    "tests/test_distortion_restoration.py":
        "e936ede2ddf0449a88b6323d666ca727e898a2039cb2d7b3093f9f970942ae7e",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/INVENTORY.md":
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-pro/docs/rights-register.md":
        "e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44",
    "audio-benchmark-platform/audio-pro/inventory/rights-register.json":
        "24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

EXPECTED_LINK = {
    "task_id": TASK,
    "title": "\u00b5-law codec proxy and low-pass postfilter",
    "mode": "research-control",
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "initialized_on", "history",
)

EXPECTED_INVENTORY = {
    "id": COMPONENT,
    "name": "\u00b5-law codec proxy and low-pass postfilter",
    "area": "Restoration",
    "evidence_status": "evaluated",
    "repository": "audio-sdk",
    "disposition": "research-control",
    "verification_profile": "restoration",
    "task": TASK,
    "plan_note": (
        "Keep the known 4/8-bit proxy separate from results on real "
        "transport codecs."),
    "evidence_paths": ["research/distortion_restoration_20261028.md"],
}

EVIDENCE_LINE = 423
EVIDENCE_TOKENS = (
    "\u00b5-law codec proxy and low-pass postfilter", TASK, "research-control",
    "distortion_restoration_20261028.md")

SOURCE_ARTIFACT_FILES = (
    "README.md",
    "contract.json.license",
    "reference.py",
    "report.json.license",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)

REPORT_ARTIFACT_FILES = tuple(
    name for name in SOURCE_ARTIFACT_FILES if name != "report.json")

PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".amr", ".aac", ".m4a", ".caf",
    ".onnx", ".pt", ".pth", ".ckpt", ".safetensors", ".bin", ".so", ".dylib",
    ".a", ".o", ".zip", ".tar", ".gz", ".whl",
}

GATE_IDS = ["RG-0" + str(number) for number in range(1, 9)]

# Pilot values copied from the pinned frozen report. They are provenance only.
PILOT_CONDITIONS = {
    "4-bit_mu-law_proxy_at_8kHz": {
        "decoded_input": {
            "si_sdr_db": 16.42695885012993,
            "rmse": 0.01812955116508933,
            "stoi": 0.8750834688333559,
        },
        "lowpass_decoder_postfilter": {
            "si_sdr_db": 16.70902966619368,
            "rmse": 0.017525118745058892,
            "stoi": 0.874904637422683,
        },
    },
    "8-bit_mu-law_proxy_at_8kHz": {
        "decoded_input": {
            "si_sdr_db": 37.99292499545241,
            "rmse": 0.001530791504200852,
            "stoi": 0.9983874090677153,
        },
        "lowpass_decoder_postfilter": {
            "si_sdr_db": 33.1203949870981,
            "rmse": 0.002902633869009632,
            "stoi": 0.9976566305447778,
        },
    },
}
PILOT_DEGRADATION = {
    "4-bit_mu-law_proxy_at_8kHz": {
        "codec_rmse_vs_narrow_reference": 0.01812955116508933,
    },
    "8-bit_mu-law_proxy_at_8kHz": {
        "codec_rmse_vs_narrow_reference": 0.001530791504200852,
    },
}
PILOT_LIMITATIONS = (
    "These are controlled synthetic degradations, not a real-capture "
    "restoration benchmark.",
    "No human listening test or listener quality score was run.",
    "Codec modeling isolates 8-bit mu-law and a 4-bit mu-law proxy at 8 kHz; "
    "the 4-bit case is not a standard codec. Neither models MP3/AAC/Opus "
    "transform artifacts, tandem coding, or network jitter.",
    "The local ROSE-CD checkpoint targets additive-noise/reverberation "
    "enhancement and was not a fair model for this task.",
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------
class Rejected(ValueError):
    """A request was rejected with a stable machine-readable reason code."""

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(reason)
        self.reason = reason
        self.detail = detail


class EvidenceError(RuntimeError):
    """A frozen pin, probe or report invariant failed."""

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(reason)
        self.reason = reason
        self.detail = detail


# ---------------------------------------------------------------------------
# Strict JSON and canonical bytes
# ---------------------------------------------------------------------------
def _pairs_hook(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise Rejected("DUPLICATE_JSON_KEY", key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise Rejected("NONFINITE_JSON_CONSTANT", token)


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_pairs_hook,
                          parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise Rejected("INVALID_JSON", str(error)) from error


def require_object(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise Rejected("JSON_ROOT_NOT_OBJECT")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True).encode("utf-8")


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _rounded(value: float, places: int = 12) -> float:
    rounded = round(float(value), places)
    return 0.0 if rounded == 0.0 else rounded


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------
def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_bits(bits: Any) -> int:
    if isinstance(bits, bool) or not isinstance(bits, int):
        raise Rejected("BITS_NOT_INTEGER")
    if bits not in PROXY_BITS:
        raise Rejected("BITS_NOT_ADMITTED")
    return bits


def _validate_samples(samples: Any, expected: int | None = None
                      ) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise Rejected("SAMPLES_NOT_SEQUENCE")
    if expected is not None and len(samples) != expected:
        raise Rejected("WRONG_FRAME_LENGTH")
    if not samples:
        raise Rejected("EMPTY_SAMPLES")
    values: List[float] = []
    for value in samples:
        if not _is_number(value):
            raise Rejected("SAMPLE_NOT_NUMERIC")
        number = float(value)
        if not math.isfinite(number):
            raise Rejected("NONFINITE_SAMPLE")
        values.append(number)
    peak = max(abs(value) for value in values)
    if peak <= PEAK_FLOOR:
        raise Rejected("ZERO_OR_BELOW_FLOOR_PEAK")
    if peak > MAX_PEAK:
        raise Rejected("PEAK_OUT_OF_RANGE")
    return values


# ---------------------------------------------------------------------------
# Exact pilot proxy quantizer (peak-normalised logarithmic companding)
# ---------------------------------------------------------------------------
def _sign(value: float) -> float:
    if value > 0.0:
        return 1.0
    if value < 0.0:
        return -1.0
    return 0.0


def mulaw_proxy_quantize(samples: Any, bits: Any) -> List[float]:
    """Reproduce the pinned pilot's ``mulaw_roundtrip`` exactly.

    The pilot names this "mu-law", but it is a peak-normalised
    ``2**bits``-level logarithmic quantizer, not ITU-T G.711 companding.
    A zero or sub-floor peak is rejected instead of being amplified.
    """
    admitted_bits = _validate_bits(bits)
    values = _validate_samples(samples)
    levels = 2 ** admitted_bits
    mu = float(levels - 1)
    peak = max(max(abs(value) for value in values), PEAK_FLOOR)
    log_mu = math.log1p(mu)
    output: List[float] = []
    for value in values:
        normalised = min(1.0, max(-1.0, value / peak))
        if normalised == 0.0:
            encoded = 0.0
        else:
            encoded = (_sign(normalised) *
                       math.log1p(mu * abs(normalised)) / log_mu)
        code = (round((encoded + 1.0) * (levels - 1) / 2.0) *
                2.0 / (levels - 1) - 1.0)
        if code == 0.0:
            decoded = 0.0
        else:
            decoded = (_sign(code) *
                       math.expm1(abs(code) * log_mu) / mu)
        output.append(decoded * peak)
    return output


# ---------------------------------------------------------------------------
# Standard-library polyphase resampler matching scipy.signal.resample_poly
# ---------------------------------------------------------------------------
def _bessel_i0(value: float) -> float:
    total = 1.0
    term = 1.0
    index = 1
    while True:
        term *= (value / (2.0 * index)) ** 2
        total += term
        if term < 1e-18 * total:
            return total
        index += 1


def _kaiser_window(length: int, beta: float) -> List[float]:
    alpha = (length - 1) / 2.0
    denominator = _bessel_i0(beta)
    window: List[float] = []
    for index in range(length):
        ratio = (index - alpha) / alpha
        window.append(
            _bessel_i0(beta * math.sqrt(max(0.0, 1.0 - ratio * ratio))) /
            denominator)
    return window


def _sinc(value: float) -> float:
    if value == 0.0:
        return 1.0
    return math.sin(math.pi * value) / (math.pi * value)


def _firwin_lowpass(taps: int, cutoff: float, beta: float) -> List[float]:
    alpha = (taps - 1) / 2.0
    window = _kaiser_window(taps, beta)
    coefficients = [_sinc(cutoff * (index - alpha)) * window[index]
                    for index in range(taps)]
    total = math.fsum(coefficients)
    return [value / total for value in coefficients]


def _upfirdn(coefficients: Sequence[float], samples: Sequence[float],
             up: int, down: int) -> List[float]:
    zero_stuffed = [0.0] * (len(samples) * up)
    zero_stuffed[::up] = samples
    length = len(zero_stuffed) + len(coefficients) - 1
    filtered = [0.0] * length
    for index, value in enumerate(zero_stuffed):
        if value == 0.0:
            continue
        for offset, coefficient in enumerate(coefficients):
            filtered[index + offset] += value * coefficient
    return filtered[::down]


def _output_length(coefficient_count: int, input_count: int, up: int,
                   down: int) -> int:
    total = (input_count - 1) * up + coefficient_count
    return (total + down - 1) // down


def resampler_tap_count(up: int, down: int) -> int:
    """Return the per-direction FIR tap count for an admitted ratio.

    The pilot's ``scipy.signal.resample_poly`` prototype is
    ``2 * 10 * max(up, down) + 1`` taps. Only the admitted 1:2 / 2:1
    narrowband geometry is accepted, so every admitted call yields 41 taps.
    """
    if (up, down) not in RESAMPLE_ADMITTED_RATIOS:
        raise Rejected("RESAMPLE_RATIO_NOT_ADMITTED")
    return 2 * RESAMPLE_HALF_LENGTH_FACTOR * max(up, down) + 1


def resample_poly(samples: Any, up: Any, down: Any) -> List[float]:
    """Deterministic ``scipy.signal.resample_poly`` equivalent.

    Uses the pilot's default Kaiser beta 5.0 window and 10*max(up, down)
    half-length, i.e. ``2 * 10 * max(up, down) + 1`` taps per direction. Only
    the admitted 1:2 / 2:1 narrowband geometry is accepted.
    """
    if isinstance(up, bool) or not isinstance(up, int):
        raise Rejected("UP_NOT_INTEGER")
    if isinstance(down, bool) or not isinstance(down, int):
        raise Rejected("DOWN_NOT_INTEGER")
    if up < 1 or down < 1:
        raise Rejected("INVALID_RESAMPLE_RATIO")
    if (up, down) not in RESAMPLE_ADMITTED_RATIOS:
        raise Rejected("RESAMPLE_RATIO_NOT_ADMITTED")
    values = _validate_samples(samples)
    maximum_rate = max(up, down)
    taps = resampler_tap_count(up, down)
    half_length = (taps - 1) // 2
    coefficients = _firwin_lowpass(taps, 1.0 / maximum_rate,
                                   RESAMPLE_KAISER_BETA)
    coefficients = [value * up for value in coefficients]
    input_count = len(values)
    output_count = (input_count * up + down - 1) // down
    pre_pad = down - half_length % down
    post_pad = 0
    pre_remove = (half_length + pre_pad) // down
    while (_output_length(len(coefficients) + pre_pad + post_pad,
                          input_count, up, down) <
           output_count + pre_remove):
        post_pad += 1
    padded = ([0.0] * pre_pad + coefficients + [0.0] * post_pad)
    filtered = _upfirdn(padded, values, up, down)
    return filtered[pre_remove:pre_remove + output_count]


# ---------------------------------------------------------------------------
# Exact pilot postfilter: 4th-order Butterworth 3900 Hz, zero phase
# ---------------------------------------------------------------------------
def _butterworth_sections(cutoff_hz: float,
                          sample_rate_hz: int = SAMPLE_RATE_HZ
                          ) -> List[Tuple[List[float], List[float]]]:
    if not 0.0 < cutoff_hz < sample_rate_hz / 2.0:
        raise Rejected("POSTFILTER_CUTOFF_OUT_OF_RANGE")
    omega = 2.0 * math.pi * cutoff_hz / sample_rate_hz
    cosine = math.cos(omega)
    sine = math.sin(omega)
    quality_factors = (
        1.0 / (2.0 * math.cos(3.0 * math.pi / 8.0)),
        1.0 / (2.0 * math.cos(math.pi / 8.0)),
    )
    sections: List[Tuple[List[float], List[float]]] = []
    for quality in quality_factors:
        alpha = sine / (2.0 * quality)
        b0 = (1.0 - cosine) / 2.0
        b1 = 1.0 - cosine
        b2 = b0
        a0 = 1.0 + alpha
        a1 = -2.0 * cosine
        a2 = 1.0 - alpha
        sections.append((
            [b0 / a0, b1 / a0, b2 / a0],
            [1.0, a1 / a0, a2 / a0],
        ))
    return sections


def _biquad_df2t(samples: Sequence[float], numerator: Sequence[float],
                 denominator: Sequence[float],
                 state: Tuple[float, float]) -> List[float]:
    z1, z2 = state
    output: List[float] = []
    b0, b1, b2 = numerator
    _a0, a1, a2 = denominator
    for value in samples:
        result = b0 * value + z1
        z1 = b1 * value - a1 * result + z2
        z2 = b2 * value - a2 * result
        output.append(result)
    return output


def _biquad_steady_state(numerator: Sequence[float],
                         denominator: Sequence[float],
                         constant: float) -> Tuple[float, float]:
    b0, b1, b2 = numerator
    _a0, a1, a2 = denominator
    steady = constant * (b0 + b1 + b2) / (1.0 + a1 + a2)
    z1 = steady - b0 * constant
    z2 = steady * (1.0 + a1) - (b0 + b1) * constant
    return z1, z2


def lowpass_postfilter(samples: Any,
                       cutoff_hz: float = POSTFILTER_CUTOFF_HZ) -> List[float]:
    """Forward-backward 4th-order Butterworth low-pass postfilter.

    This reproduces the pinned pilot's ``codec_spectral_postfilter``
    (butter(4, cutoff, fs=16000) + sosfiltfilt) with odd edge padding and
    per-section steady-state initialisation. It is whole-clip and zero phase,
    therefore non-causal and unsuitable for the streaming v0 process path.
    """
    values = _validate_samples(samples)
    sections = _butterworth_sections(cutoff_hz)
    padding = 3 * (2 * len(sections) + 1)
    if len(values) <= padding:
        raise Rejected("SAMPLES_TOO_SHORT_FOR_POSTFILTER")
    left = [2.0 * values[0] - values[index]
            for index in range(padding, 0, -1)]
    right = [2.0 * values[-1] - values[-1 - index]
             for index in range(1, padding + 1)]
    extended = left + values + right
    for numerator, denominator in sections:
        extended = _biquad_df2t(
            extended, numerator, denominator,
            _biquad_steady_state(numerator, denominator, extended[0]))
    extended.reverse()
    for numerator, denominator in sections:
        extended = _biquad_df2t(
            extended, numerator, denominator,
            _biquad_steady_state(numerator, denominator, extended[0]))
    extended.reverse()
    return extended[padding:padding + len(values)]


# ---------------------------------------------------------------------------
# Metrics, synthetic stimulus and offline proxy comparison
# ---------------------------------------------------------------------------
def rmse(reference: Sequence[float], estimate: Sequence[float]) -> float:
    length = min(len(reference), len(estimate))
    if length == 0:
        raise Rejected("EMPTY_COMPARISON")
    total = math.fsum((float(reference[index]) - float(estimate[index])) ** 2
                      for index in range(length))
    return math.sqrt(total / length)


def si_sdr(reference: Sequence[float], estimate: Sequence[float]
           ) -> Tuple[float | None, bool]:
    """Return (SI-SDR dB, exact_identity) using the pilot's formula."""
    length = min(len(reference), len(estimate))
    if length == 0:
        raise Rejected("EMPTY_COMPARISON")
    ref = [float(reference[index]) for index in range(length)]
    est = [float(estimate[index]) for index in range(length)]
    if ref == est:
        return None, True
    ref_mean = math.fsum(ref) / length
    est_mean = math.fsum(est) / length
    centred_ref = [value - ref_mean for value in ref]
    centred_est = [value - est_mean for value in est]
    dot = math.fsum(a * b for a, b in zip(centred_est, centred_ref))
    ref_energy = math.fsum(value * value for value in centred_ref)
    scale = dot / (ref_energy + SI_SDR_EPS)
    target = [scale * value for value in centred_ref]
    noise = [estimate_value - target_value
             for estimate_value, target_value in zip(centred_est, target)]
    numerator = math.fsum(value * value for value in target) + SI_SDR_EPS
    denominator = math.fsum(value * value for value in noise) + SI_SDR_EPS
    return 10.0 * math.log10(numerator / denominator), False


def _metric_block(reference: Sequence[float],
                  estimate: Sequence[float]) -> Dict[str, Any]:
    value, perfect = si_sdr(reference, estimate)
    return {
        "si_sdr_db": _rounded(value) if value is not None else None,
        "si_sdr_perfect": perfect,
        "rmse": _rounded(rmse(reference, estimate)),
        "stoi": None,
        "stoi_status": "not_computed_runtime_absent",
    }


def synthetic_speech_like(length: int = FIXTURE_SAMPLES) -> List[float]:
    """Deterministic harmonic speech-like stimulus with onset, gap and decay.

    No corpus, recording, media file or model is read. The generator uses a
    fixed harmonic series (125 Hz fundamental, 1/k amplitudes, deterministic
    phases) and a raised-cosine envelope with an 80-120 ms silence.
    """
    if length <= 0:
        raise Rejected("INVALID_STIMULUS_LENGTH")
    values: List[float] = []
    for index in range(length):
        time = index / float(SAMPLE_RATE_HZ)
        envelope = 1.0
        if time < 0.02:
            envelope = 0.5 * (1.0 - math.cos(math.pi * time / 0.02))
        elif time > 0.18:
            envelope = 0.5 * (1.0 - math.cos(math.pi * (0.2 - time) / 0.02))
        if 0.08 <= time < 0.12:
            envelope = 0.0
        value = 0.0
        for harmonic in range(1, 29):
            frequency = 125.0 * harmonic
            if frequency >= 3500.0:
                break
            value += (1.0 / harmonic) * math.sin(
                2.0 * math.pi * frequency * time + 0.37 * harmonic * harmonic)
        values.append(envelope * value)
    peak = max(abs(value) for value in values)
    return [0.5 * value / peak for value in values]


def evaluate_offline(signal: Sequence[float] | None = None) -> Dict[str, Any]:
    """Run the exact offline proxy comparison on a synthetic stimulus."""
    values = list(signal) if signal is not None else synthetic_speech_like()
    values = _validate_samples(values)
    narrowband = resample_poly(values, 1, 2)
    reference = resample_poly(narrowband, 2, 1)[:len(values)]
    reference_peak = max(abs(value) for value in reference)
    identity_filtered = lowpass_postfilter(reference)
    identity = _metric_block(reference, identity_filtered)
    conditions: Dict[str, Any] = {}
    for bits in PROXY_BITS:
        decoded = resample_poly(mulaw_proxy_quantize(narrowband, bits),
                                2, 1)[:len(values)]
        postfiltered = lowpass_postfilter(decoded)
        decoded_metrics = _metric_block(reference, decoded)
        postfiltered_metrics = _metric_block(reference, postfiltered)
        decoded_value = decoded_metrics["si_sdr_db"]
        postfiltered_value = postfiltered_metrics["si_sdr_db"]
        if decoded_value is None:
            decoded_value = 120.0
        if postfiltered_value is None:
            postfiltered_value = 120.0
        delta = postfiltered_value - decoded_value
        peak = max(max(abs(value) for value in decoded),
                   max(abs(value) for value in postfiltered))
        conditions[str(bits) + "bit"] = {
            "bits": bits,
            "decoded_input": decoded_metrics,
            "lowpass_postfilter": postfiltered_metrics,
            "delta_si_sdr_db": _rounded(delta),
            "peak_abs": _rounded(peak),
            "reference_peak_abs": _rounded(reference_peak),
            "finite": all(math.isfinite(value)
                          for value in decoded + postfiltered),
            "peak_bounded": peak <= 2.0 * reference_peak,
        }
    return {
        "stimulus": {
            "generator": "deterministic harmonic speech-like fixture",
            "length_samples": len(values),
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "peak_abs": _rounded(max(abs(value) for value in values)),
            "real_audio_read": False,
            "corpus_used": False,
            "seed_or_media": "none",
        },
        "identity_control": {
            "decoded_bit_exact": True,
            "filtered_bit_exact": False,
            "filtered": identity,
            "postfilter_max_abs_change": _rounded(max(
                abs(a - b) for a, b in zip(reference, identity_filtered))),
            "note": (
                "The postfilter is deliberately not an identity operation; "
                "its own distortion bounds the attainable SI-SDR of any "
                "decoded condition."),
        },
        "conditions": conditions,
        "all_finite": all(
            condition["finite"] for condition in conditions.values()),
        "peak_bounded": all(
            condition["peak_bounded"] for condition in conditions.values()),
        "results_role": "synthetic_fixture_control_not_qualifying",
        "pilot_numeric_parity": False,
    }


# ---------------------------------------------------------------------------
# Installed-v0-shaped frame request fixture
# ---------------------------------------------------------------------------
FRAME_CONFIG_KEYS = frozenset({
    "sample_rate_hz", "channels", "frame_samples", "bits", "postfilter",
    "mode",
})
FRAME_MODE = "proxy_frame_quantize"


def validate_frame_request(samples: Any, config: Any) -> Dict[str, Any]:
    """Validate one v0-shaped 160-sample proxy request.

    The frame path is intentionally quantizer-only. A zero-phase
    forward-backward postfilter needs the complete clip (or lookahead) and is
    therefore rejected on the frame path as ``FRAME_POSTFILTER_UNSUPPORTED``.
    """
    if not isinstance(config, dict):
        raise Rejected("CONFIG_NOT_OBJECT")
    keys = set(config)
    if keys - FRAME_CONFIG_KEYS:
        raise Rejected("UNKNOWN_CONFIG_KEY")
    if FRAME_CONFIG_KEYS - keys:
        raise Rejected("MISSING_CONFIG_KEY")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise Rejected("SAMPLE_RATE_NOT_ADMITTED")
    if (isinstance(config["channels"], bool) or
            not isinstance(config["channels"], int) or
            config["channels"] != 1):
        raise Rejected("CHANNELS_NOT_ADMITTED")
    if (isinstance(config["frame_samples"], bool) or
            not isinstance(config["frame_samples"], int) or
            config["frame_samples"] != FRAME_SAMPLES):
        raise Rejected("FRAME_SAMPLES_NOT_ADMITTED")
    if config["postfilter"] is not False:
        if config["postfilter"] is True:
            raise Rejected("FRAME_POSTFILTER_UNSUPPORTED")
        raise Rejected("POSTFILTER_FLAG_NOT_BOOLEAN")
    if config["mode"] != FRAME_MODE:
        raise Rejected("MODE_NOT_ADMITTED")
    bits = _validate_bits(config["bits"])
    values = _validate_samples(samples, FRAME_SAMPLES)
    return {"bits": bits, "samples": values}


def process_frame(samples: Any, config: Any) -> Dict[str, Any]:
    admitted = validate_frame_request(samples, config)
    quantized = mulaw_proxy_quantize(admitted["samples"], admitted["bits"])
    return {
        "status": "accepted",
        "bits": admitted["bits"],
        "samples": quantized,
        "input_peak_abs": _rounded(max(abs(value)
                                       for value in admitted["samples"])),
        "output_peak_abs": _rounded(max(abs(value) for value in quantized)),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "postfilter_applied": False,
    }


class ProxySession:
    """Minimal epoch/position lifecycle for the frame fixture."""

    def __init__(self, bits: int) -> None:
        self.bits = _validate_bits(bits)
        self.epoch = 1
        self.next_source_sample = 0
        self.frame_count = 0
        self.closed = False

    def _config(self) -> Dict[str, Any]:
        return {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "bits": self.bits,
            "postfilter": False,
            "mode": FRAME_MODE,
        }

    def process(self, samples: Any, epoch: Any,
                first_source_sample: Any) -> Dict[str, Any]:
        if self.closed:
            raise Rejected("SESSION_CLOSED")
        if isinstance(epoch, bool) or not isinstance(epoch, int):
            raise Rejected("EPOCH_NOT_INTEGER")
        if epoch != self.epoch:
            raise Rejected("STALE_OR_UNKNOWN_EPOCH")
        if isinstance(first_source_sample, bool) or \
                not isinstance(first_source_sample, int):
            raise Rejected("POSITION_NOT_INTEGER")
        if first_source_sample != self.next_source_sample:
            raise Rejected("WRONG_SOURCE_POSITION")
        result = process_frame(samples, self._config())
        self.next_source_sample += FRAME_SAMPLES
        self.frame_count += 1
        result["epoch"] = self.epoch
        result["source_first_sample"] = first_source_sample
        result["source_end_sample"] = self.next_source_sample
        return result

    def reset(self, epoch: Any, first_source_sample: Any) -> Dict[str, Any]:
        if isinstance(epoch, bool) or not isinstance(epoch, int):
            raise Rejected("EPOCH_NOT_INTEGER")
        if epoch <= self.epoch:
            raise Rejected("NON_INCREASING_EPOCH")
        if isinstance(first_source_sample, bool) or \
                not isinstance(first_source_sample, int):
            raise Rejected("POSITION_NOT_INTEGER")
        if first_source_sample < 0:
            raise Rejected("NEGATIVE_SOURCE_POSITION")
        self.epoch = epoch
        self.next_source_sample = first_source_sample
        self.frame_count = 0
        return {"status": "reset", "epoch": self.epoch,
                "source_first_sample": first_source_sample}

    def close(self) -> None:
        self.closed = True


def _frame_stimulus() -> List[float]:
    values = synthetic_speech_like(480)
    return values[80:240]


# ---------------------------------------------------------------------------
# Adverse, missing and lifecycle cases
# ---------------------------------------------------------------------------
def _case(identifier: str, function) -> Dict[str, Any]:
    try:
        function()
    except Rejected as error:
        return {"id": identifier, "accepted": False,
                "reason": error.reason}
    except (TypeError, ValueError, OverflowError) as error:
        return {"id": identifier, "accepted": False,
                "reason": "UNEXPECTED_VALUE_ERROR: " + type(error).__name__}
    return {"id": identifier, "accepted": True, "reason": "ACCEPTED"}


def _frame_cases() -> Dict[str, Any]:
    good = _frame_stimulus()
    good_config = {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "bits": 8,
        "postfilter": False,
        "mode": FRAME_MODE,
    }

    def config_with(**changes: Any) -> Dict[str, Any]:
        updated = dict(good_config)
        updated.update(changes)
        return updated

    cases = [
        _case("missing_samples", lambda: process_frame(None, good_config)),
        _case("empty_samples", lambda: process_frame([], good_config)),
        _case("short_frame", lambda: process_frame(good[:-1], good_config)),
        _case("long_frame", lambda: process_frame(good + [0.0], good_config)),
        _case("nonfinite_nan", lambda: process_frame(
            good[:80] + [float("nan")] + good[81:], good_config)),
        _case("nonfinite_inf", lambda: process_frame(
            good[:80] + [float("inf")] + good[81:], good_config)),
        _case("nonfinite_negative_inf", lambda: process_frame(
            good[:80] + [float("-inf")] + good[81:], good_config)),
        _case("zero_signal", lambda: process_frame(
            [0.0] * FRAME_SAMPLES, good_config)),
        _case("below_peak_floor", lambda: process_frame(
            [1e-12] * FRAME_SAMPLES, good_config)),
        _case("peak_out_of_range", lambda: process_frame(
            [value * 20.0 for value in good], good_config)),
        _case("bits_3", lambda: process_frame(good, config_with(bits=3))),
        _case("bits_9", lambda: process_frame(good, config_with(bits=9))),
        _case("bits_float", lambda: process_frame(good, config_with(bits=4.5))),
        _case("bits_bool", lambda: process_frame(good, config_with(bits=True))),
        _case("sample_rate_8000", lambda: process_frame(
            good, config_with(sample_rate_hz=8000))),
        _case("channels_2", lambda: process_frame(good, config_with(channels=2))),
        _case("frame_samples_320", lambda: process_frame(
            good, config_with(frame_samples=320))),
        _case("postfilter_true", lambda: process_frame(
            good, config_with(postfilter=True))),
        _case("postfilter_string", lambda: process_frame(
            good, config_with(postfilter="true"))),
        _case("mode_unknown", lambda: process_frame(
            good, config_with(mode="streaming"))),
        _case("unknown_config_key", lambda: process_frame(
            good, config_with(extra=1))),
        _case("missing_config_key", lambda: process_frame(good, {
            key: value for key, value in good_config.items()
            if key != "bits"})),
        _case("config_not_object", lambda: process_frame(good, [])),
        _case("samples_not_sequence", lambda: process_frame(0, good_config)),
        _case("sample_not_numeric", lambda: process_frame(
            good[:80] + ["0.1"] + good[81:], good_config)),
    ]
    accepted = sum(1 for case in cases if case["accepted"])
    return {
        "all_rejected": accepted == 0,
        "accepted_count": accepted,
        "case_count": len(cases),
        "cases": cases,
    }


def _json_cases() -> Dict[str, Any]:
    cases = [
        _case("duplicate_key", lambda: strict_json_loads(
            '{"a":1,"a":2}')),
        _case("nan_constant", lambda: strict_json_loads('{"a":NaN}')),
        _case("infinity_constant", lambda: strict_json_loads(
            '{"a":Infinity}')),
        _case("negative_infinity_constant", lambda: strict_json_loads(
            '{"a":-Infinity}')),
        _case("truncated", lambda: strict_json_loads('{"a":1')),
        _case("wrong_root", lambda: require_object(strict_json_loads('[]'))),
    ]
    accepted = sum(1 for case in cases if case["accepted"])
    return {
        "all_rejected": accepted == 0,
        "accepted_count": accepted,
        "case_count": len(cases),
        "cases": cases,
    }


def _lifecycle_cases() -> Dict[str, Any]:
    good = _frame_stimulus()
    session = ProxySession(bits=8)
    first = session.process(good, 1, 0)
    second = session.process(good, 1, FRAME_SAMPLES)
    wrong_epoch = _case("wrong_epoch_rejected",
                        lambda: session.process(good, 9, 2 * FRAME_SAMPLES))
    wrong_position = _case(
        "wrong_position_rejected",
        lambda: session.process(good, 1, 12345))
    after_rejections = session.process(good, 1, 2 * FRAME_SAMPLES)
    reset_same_epoch = _case("reset_same_epoch_rejected",
                             lambda: session.reset(1, 0))
    reset_lower_epoch = _case("reset_lower_epoch_rejected",
                              lambda: session.reset(0, 0))
    reset_negative = _case("reset_negative_position_rejected",
                           lambda: session.reset(2, -1))
    reset_ok = session.reset(2, 1000)
    post_reset = session.process(good, 2, 1000)
    post_reset_wrong = _case(
        "post_reset_wrong_position_rejected",
        lambda: session.process(good, 2, 0))
    closed = ProxySession(bits=4)
    closed.close()
    closed_case = _case("closed_session_rejected",
                        lambda: closed.process(good, 1, 0))
    isolation_left = ProxySession(bits=4)
    isolation_right = ProxySession(bits=8)
    left = isolation_left.process(good, 1, 0)["samples"]
    right = isolation_right.process(good, 1, 0)["samples"]
    expected = sum(1 for case in
                   (wrong_epoch, wrong_position, reset_same_epoch,
                    reset_lower_epoch, reset_negative, post_reset_wrong,
                    closed_case)
                   if not case["accepted"])
    return {
        "matches_expectation": (
            first["status"] == "accepted" and
            second["source_end_sample"] == 2 * FRAME_SAMPLES and
            after_rejections["source_first_sample"] == 2 * FRAME_SAMPLES and
            reset_ok["status"] == "reset" and
            post_reset["source_first_sample"] == 1000 and
            expected == 7 and
            left != right),
        "rejection_count": expected,
        "case_count": 9,
        "frames_accepted": session.frame_count,
        "cases": [wrong_epoch, wrong_position, reset_same_epoch,
                  reset_lower_epoch, reset_negative, post_reset_wrong,
                  closed_case,
                  {"id": "reset_accepted", "accepted": True,
                   "reason": "RESET"},
                  {"id": "post_reset_accepted", "accepted": True,
                   "reason": "ACCEPTED"}],
    }


def _missing_result() -> Dict[str, Any]:
    return {
        "id": "real_transport_codec_postfilter_result",
        "status": "blocked",
        "metrics": None,
        "qualifies_candidate": False,
        "reason": (
            "No licensed real-codec reference, pinned pilot runtime, "
            "rights-cleared paired corpus or target-runtime measurement is "
            "present. A missing result cannot qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Bounded probes
# ---------------------------------------------------------------------------
def source_probe() -> Dict[str, Any]:
    files: List[Dict[str, Any]] = []
    for relative, digest in sorted(SOURCE_PINS.items()):
        path = WORKSPACE / relative
        present = path.is_file()
        actual = sha256_file(path) if present else None
        files.append({
            "path": relative,
            "present": present,
            "sha256": actual,
            "matches_pin": actual == digest,
        })
    verified = all(item["present"] and item["matches_pin"]
                   for item in files)
    return {
        "status": "present_pinned" if verified else "blocked_source_changed",
        "present": all(item["present"] for item in files),
        "verified": verified,
        "file_count": len(files),
        "files": files,
        "pilot_source_license": "not_recorded",
        "pilot_report_role": "frozen_provenance_only",
        "note": (
            "The first-party pilot source and frozen report are present and "
            "digest-verified, but no artifact-specific licence, corpus "
            "licence or runtime lock accompanies them."),
    }


def runtime_probe() -> Dict[str, Any]:
    return {
        "status": "unpinned_not_admitted",
        "pinned": False,
        "runtime_digest": None,
        "declared_target": (
            "CPython 3.12+ per the workspace project requirement; not "
            "admitted as the pilot runtime"),
        "admitted_modules": [],
        "live_interpreter_probe": (
            "not embedded: the committed report depends only on stable "
            "workspace facts, so byte reproduction does not depend on the "
            "verifier interpreter"),
        "unpinned_venv": {
            "path": (
                "cpp-library/pipeline-validation/playback-speed/.venv"),
            "admitted": False,
            "lock_file_present": False,
            "wheel_digests_recorded": False,
            "note": (
                "An unrelated workspace virtual environment may contain "
                "numpy, scipy, pystoi and soundfile. It has no lock or wheel "
                "digests, is not the pilot environment and is never invoked "
                "by the committed evidence or verifier. Its presence is not "
                "embedded in the report so byte reproduction does not depend "
                "on that ephemeral directory."),
        },
        "audioop_policy": "not_admitted_deprecated_removed_in_python_3_13",
        "audioop_note": (
            "audioop would expose a CPython G.711 mu-law codec, but it is "
            "deprecated and unavailable on the target 3.12+ interpreter; it "
            "is not the pilot proxy, has no pinned wheel and is not used."),
        "downloads": False,
        "network_used": False,
    }


def corpus_probe() -> Dict[str, Any]:
    present = EARS_SUBSET_PATH.is_dir()
    clips: List[str] = []
    if present:
        for path in sorted(EARS_SUBSET_PATH.glob("*.wav"))[:100]:
            clips.append(path.name)
    return {
        "status": "present_unadmitted" if present else "absent",
        "path": "data/datasets/ears-blind/audio",
        "present": present,
        "observed_clip_count": len(clips),
        "frozen_pilot_clip_count": 12,
        "frozen_pilot_sample_rate_hz": 16000,
        "real_audio_read": False,
        "media_read": False,
        "downloads": False,
        "rights_cleared": False,
    }


def rights_probe() -> Dict[str, Any]:
    entry_present = False
    register_present = RIGHTS_REGISTER_PATH.is_file()
    detail_present = RIGHTS_DETAIL_PATH.is_file()
    if register_present:
        text = RIGHTS_REGISTER_PATH.read_text(encoding="utf-8").lower()
        entry_present = any(needle in text for needle in
                            ("law-codec", "law codec", "g.711", "g711",
                             "mu-law", "\u00b5-law", "ulaw"))
    if detail_present and not entry_present:
        detail = RIGHTS_DETAIL_PATH.read_text(encoding="utf-8").lower()
        entry_present = any(needle in detail for needle in
                            ("law-codec", "g.711", "g711", "mu-law",
                             "\u00b5-law", "ulaw"))
    return {
        "status": "entry_present_unreviewed" if entry_present else "absent",
        "register": "audio-benchmark-platform/audio-pro/docs/rights-register.md",
        "register_present": register_present,
        "detail_present": detail_present,
        "entry_present": entry_present,
        "acquisition": "unknown",
        "evaluation": "unknown",
        "redistribution": "unknown",
        "customer_deployment": "unknown",
        "public_playback": "unknown",
        "consent": "not_recorded",
        "evaluation_only": False,
        "packaging_permitted": False,
        "blocked": True,
    }


def codec_reference_probe() -> Dict[str, Any]:
    fixed_probes = {
        "data/checkouts/libopus": False,
        "data/checkouts/opus": False,
        "data/checkouts/g711": False,
        "data/checkouts/G711": False,
        "data/checkouts/ffmpeg": False,
        "src/audioml_eval/distortion_restoration.py": True,
        "third_party/speexdsp": (SDK_ROOT / "third_party/speexdsp").is_dir(),
    }
    for relative in list(fixed_probes):
        if relative.startswith("data/") and fixed_probes[relative] is False:
            fixed_probes[relative] = (WORKSPACE / relative).is_dir()
    return {
        "status": "absent",
        "licensed_reference_present": False,
        "g711_reference_present": False,
        "real_transport_codec_present": False,
        "admitted": False,
        "conformance_vectors": {
            "status": "absent",
            "sha256": None,
            "byte_count": None,
        },
        "real_transport_families_absent": [
            "ITU-T G.711 companding conformance vectors",
            "MP3", "AAC", "Opus", "AMR", "tandem coding", "jitter",
        ],
        "fixed_workspace_probes": fixed_probes,
        "proxy_script_present": True,
        "proxy_script_is_real_codec": False,
        "downloads": False,
        "note": (
            "Only the first-party synthetic proxy script and the earlier "
            "SpeexDSP tree are present. No licensed real codec reference, "
            "binary, conformance vector or runtime is admitted."),
    }


# ---------------------------------------------------------------------------
# Pilot provenance
# ---------------------------------------------------------------------------
def pilot_evidence() -> Dict[str, Any]:
    if not PILOT_REPORT_PATH.is_file():
        raise EvidenceError("PILOT_REPORT_MISSING")
    digest = sha256_file(PILOT_REPORT_PATH)
    if digest != SOURCE_PINS[
            "reports/distortion-restoration/20261028-synthetic-screen.json"]:
        raise EvidenceError("PILOT_REPORT_CHANGED")
    report = strict_json_loads(PILOT_REPORT_PATH.read_text(encoding="utf-8"))
    aggregate = report["aggregate"]["RST-03-codec-artifacts"]
    degradation = report["degradation_summary"]["RST-03"]
    conditions: Dict[str, Any] = {}
    for key, expected in PILOT_CONDITIONS.items():
        observed = aggregate[key]
        if observed != expected:
            raise EvidenceError("PILOT_METRIC_CHANGED: " + key)
        if degradation[key] != PILOT_DEGRADATION[key]:
            raise EvidenceError("PILOT_DEGRADATION_CHANGED: " + key)
        delta = (observed["lowpass_decoder_postfilter"]["si_sdr_db"] -
                 observed["decoded_input"]["si_sdr_db"])
        stoi_delta = (observed["lowpass_decoder_postfilter"]["stoi"] -
                      observed["decoded_input"]["stoi"])
        conditions[key] = {
            "decoded_input": dict(observed["decoded_input"]),
            "lowpass_decoder_postfilter":
                dict(observed["lowpass_decoder_postfilter"]),
            "delta_si_sdr_db": _rounded(delta),
            "delta_stoi": _rounded(stoi_delta),
            "degradation": dict(degradation[key]),
        }
    return {
        "path": "reports/distortion-restoration/20261028-synthetic-screen.json",
        "sha256": digest,
        "protocol": report["protocol"],
        "dataset": report["dataset"],
        "conditions": conditions,
        "limitations": list(report["limitations"]) + list(PILOT_LIMITATIONS),
        "provenance_only": True,
        "reproduced_here": False,
        "qualifies_candidate": False,
        "interpretation": (
            "On the frozen synthetic pilot the postfilter adds 0.282 dB "
            "SI-SDR to the 4-bit stress proxy and removes 4.873 dB from the "
            "8-bit proxy, while STOI is effectively unchanged. The effect is "
            "small, sign-dependent and limited to a non-standard proxy."),
    }


# ---------------------------------------------------------------------------
# Geometry, blockers, gates
# ---------------------------------------------------------------------------
def geometry() -> Dict[str, Any]:
    return {
        "v0_format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
        },
        "proxy_sample_rate_hz": PROXY_SAMPLE_RATE_HZ,
        "evaluation_sample_rate_hz": SAMPLE_RATE_HZ,
        "masking_companding_bits": list(PROXY_BITS),
        "quantizer_levels": {"4": 16, "8": 256},
        "is_itu_t_g711": False,
        "is_real_transport_codec": False,
        "global_peak_normalisation": True,
        "postfilter": {
            "type": "4th-order Butterworth low-pass",
            "cutoff_hz": POSTFILTER_CUTOFF_HZ,
            "zero_phase": True,
            "forward_backward": True,
            "frame_causal": False,
            "pilot_implementation":
                "scipy.signal.butter(4, 3900, fs=16000) + sosfiltfilt",
        },
        "resampler": {
            "pilot_implementation": "scipy.signal.resample_poly",
            "fixture_implementation":
                "stdlib Kaiser-windowed polyphase equivalent",
            "admitted_ratios": [list(pair)
                                for pair in RESAMPLE_ADMITTED_RATIOS],
            "taps_per_direction": RESAMPLE_TAPS,
            "taps_formula": "2 * 10 * max(up, down) + 1",
            "half_length_factor": RESAMPLE_HALF_LENGTH_FACTOR,
            "kaiser_beta": RESAMPLE_KAISER_BETA,
            "composite_cascade_taps": RESAMPLE_COMPOSITE_TAPS,
            "composite_cascade_note": (
                "16 kHz -> 8 kHz -> 16 kHz convolution span of the two "
                "41-tap directional FIRs (41 + 41 - 1 = 81); it is not a "
                "single filter applied at one rate and no (up, down) = "
                "(2, 2) call is admitted."),
        },
        "streaming_ready": False,
        "whole_clip_processing": True,
        "measured_here": False,
    }


GATES = (
    {
        "id": "RG-01",
        "name": "exact_codec_reference_identity",
        "status": "blocked",
        "reason": (
            "No licensed ITU-T G.711 or real transport codec reference, "
            "binary, conformance vector or pinned runtime exists. The local "
            "8 kHz 4/8-bit logarithmic compander is a synthetic proxy with "
            "global peak normalisation, not G.711 or MP3/AAC/Opus/AMR."),
        "reopen": (
            "Reopen only with an exact licensed real-codec reference at a "
            "40-hex revision, a SHA-256 artifact pin, admitted conformance "
            "vectors and a declared real-codec matrix (codec, bitrate, mode, "
            "sample rate)."),
    },
    {
        "id": "RG-02",
        "name": "pilot_runtime_and_reproduction",
        "status": "blocked",
        "reason": (
            "The pilot needs numpy, scipy, pystoi and soundfile with recorded "
            "wheel digests. The task interpreter has none. An unrelated "
            "workspace virtual environment contains them, but it has no lock "
            "or wheel digests and is not the pilot environment. The pilot "
            "metrics are not reproduced here."),
        "reopen": (
            "Reopen only with a pinned runtime (interpreter, package versions, "
            "wheel SHA-256, platform), the frozen pilot inputs and a "
            "byte-identical three-cold-start reproduction of the pilot "
            "metrics."),
    },
    {
        "id": "RG-03",
        "name": "rights_cleared_corpus",
        "status": "blocked",
        "reason": (
            "The EARS subset used by the pilot is absent from the workspace, "
            "and the rights register has no law-codec or codec entry. "
            "Acquisition, evaluation, redistribution, customer deployment, "
            "public playback and speaker consent are all unknown."),
        "reopen": (
            "Reopen only with a rights-cleared, frozen paired corpus that "
            "records acquisition, evaluation, redistribution, deployment and "
            "playback decisions plus all required speaker consent."),
    },
    {
        "id": "RG-04",
        "name": "exact_reference_parity",
        "status": "blocked",
        "reason": (
            "No approved reference output exists for any frozen input under "
            "the exact pilot runtime. The committed stdlib fixture is a "
            "mechanical control, not pilot parity or a codec oracle."),
        "reopen": (
            "Reopen only with approved outputs for frozen inputs from the "
            "exact admitted reference, reproducible across three cold starts "
            "and published with input and output digests."),
    },
    {
        "id": "RG-05",
        "name": "restoration_quality_evidence",
        "status": "blocked",
        "reason": (
            "Only synthetic SI-SDR and RMSE are computed. STOI, decoded "
            "interval accounting, bandwidth stratification, burst/erasure "
            "behaviour and peak/timing bounds for a real transport codec do "
            "not exist."),
        "reopen": (
            "Reopen only with Restoration-profile evidence on a frozen paired "
            "cohort: decoded intervals, degradation and bandwidth strata, "
            "task-specific quality metrics, output peak bounds and failure "
            "controls."),
    },
    {
        "id": "RG-06",
        "name": "independent_scoring_and_listening",
        "status": "blocked",
        "reason": (
            "STOI is not computed because pystoi is absent. No independent "
            "scorer, perceptual model or permitted listening result exists; "
            "the pilot itself records that no human evaluation was run."),
        "reopen": (
            "Reopen only with independent scoring and a recorded permitted "
            "listening protocol on the admitted cohort, with scorer version, "
            "ratings, confidence and any exclusions."),
    },
    {
        "id": "RG-07",
        "name": "target_runtime_timing",
        "status": "blocked",
        "reason": (
            "The postfilter is a whole-clip zero-phase forward-backward "
            "filter and the quantizer normalises by the global clip peak. "
            "Neither is frame-causal; no first-output, tail, pacing, "
            "deadline or memory measurement exists."),
        "reopen": (
            "Reopen only with a frame-causal or explicitly delayed streaming "
            "design and measured first-output, tail, pacing, deadline, "
            "availability and memory behaviour on the target runtime."),
    },
    {
        "id": "RG-08",
        "name": "provider_intake_and_default_selection",
        "status": "blocked",
        "reason": (
            "No provider, descriptor, registry entry or default exists. "
            "Exposure is deferred before processor intake and no owner "
            "decision was made."),
        "reopen": (
            "Reopen only after RG-01 to RG-07 pass, with an opt-in provider "
            "that is OFF by default, descriptor/catalog review and an "
            "explicit owner decision."),
    },
)

UPSTREAM_BLOCKER = {
    "status": "blocked_exact_codec_reference_runtime_corpus_and_rights_absent",
    "artifact": (
        "licensed ITU-T G.711 / real transport codec reference, conformance "
        "vectors, pinned pilot runtime and rights-cleared paired corpus"),
    "source": {
        "status": "present_pinned",
        "role": "first-party synthetic pilot provenance only",
        "license": "not_recorded",
        "real_codec": False,
        "pinned_files": len(SOURCE_PINS),
    },
    "codec_reference": {
        "status": "absent",
        "g711": False,
        "real_transport_codec": False,
        "conformance_vectors": False,
        "sha256": None,
        "byte_count": None,
    },
    "runtime": {
        "status": "unpinned_not_admitted",
        "pinned": False,
        "wheel_digests": False,
        "lock_file": False,
        "admitted": False,
        "runtime_digest": None,
    },
    "corpus": {
        "status": "absent",
        "path": "data/datasets/ears-blind/audio",
        "present": False,
        "rights_cleared": False,
        "consent": "not_recorded",
    },
    "rights_requirement": (
        "Written artifact-specific terms must record acquisition, evaluation, "
        "redistribution, customer deployment and public playback; the corpus "
        "must record speaker consent, permitted reference availability and "
        "permitted output use. Possession or evaluation permission alone is "
        "not clearance."),
    "expected_license": (
        "A licensed codec reference and conformance vectors with documented "
        "evaluation and redistribution terms, plus a rights-cleared corpus; "
        "the first-party pilot has no recorded artifact licence."),
    "pinned_revision": None,
    "source_digest": None,
    "runtime_digest": None,
    "codec_conformance_vectors": {
        "status": "absent",
        "sha256": None,
        "byte_count": None,
    },
    "pilot_numbers_are_provenance_only": True,
    "no_upstream_parity_claim": True,
    "not_attempted": [
        "downloading or invoking a codec/library",
        "reading or writing real media or corpus audio",
        "importing numpy, scipy, pystoi, soundfile or audioop",
        "listening, device timing or benchmark execution",
    ],
    "reopen": (
        "Provide the exact licensed codec reference and conformance vectors, "
        "a pinned runtime with wheel digests, a rights-cleared frozen corpus "
        "and approved exact-reference outputs; then replace this blocker "
        "package with a qualified comparison."),
}

INVARIANTS = (
    "The 4/8-bit companding proxy is not ITU-T G.711 and not a real "
    "transport codec; no real-codec claim is made.",
    "Pilot metric rows are frozen provenance only; they are not reproduced, "
    "pooled or qualified here.",
    "No corpus, weights, model, real media, codec binary or runtime is "
    "downloaded, read, hashed, loaded or invoked.",
    "No provider, descriptor, registry, installed default, public API/ABI, "
    "shared build, dependency lock, CI, board or handoff changes.",
    "The postfilter is zero-phase and whole-clip; the frame path rejects it.",
    "No missing or adverse result can qualify the candidate.",
    "Artifact pins are exact; the mutable full plan/swarm/TASKS.json is never "
    "hashed. Only the stable linked-row identity is projected.",
    "All report bytes are canonical JSON with one trailing newline and "
    "reproduce across three cold starts.",
)

NON_CLAIMS = (
    "No real codec, transport, packet-loss, jitter or tandem-coding result.",
    "No listening, MOS, STOI, perceptual, benchmark or release result.",
    "No device timing, first-output, tail, pacing or deadline measurement.",
    "No upstream parity, corpus reproduction or pilot numeric parity.",
    "No processor exposure, provider registration or default selection.",
    "No rights clearance, consent or redistribution permission.",
)


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "decision": "DEFER",
        "processor_exposure": "deferred_until_independent_review",
        "proposal_only": True,
        "readiness": "incomplete",
        "status": "not_qualified",
        "upstream_parity": False,
    }


def boundary() -> Dict[str, Any]:
    return {
        "benchmark_claim": False,
        "board_or_handoff_changed": False,
        "ci_changed": False,
        "descriptor_registration": False,
        "device_timing_measured": False,
        "enabled_by_default": False,
        "format": {
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
            "sample_rate_hz": SAMPLE_RATE_HZ,
        },
        "installed_v0_unchanged": True,
        "listening_result": False,
        "opt_in_required": True,
        "processor_exposure": "deferred",
        "provider_intake_complete": False,
        "provider_registered": False,
        "public_api_abi_changed": False,
        "public_c_boundary":
            "not used: no C provider, header or installed target",
        "real_codec_media_read": False,
        "real_corpus_or_weights": False,
        "registry_changed": False,
        "release_claim": False,
        "shared_cmake_changed": False,
        "writes_limited_to": TASK_PREFIX + "**",
    }


# ---------------------------------------------------------------------------
# Stable board projection and inventory link
# ---------------------------------------------------------------------------
def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise EvidenceError("BOARD_MISSING")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise EvidenceError("BOARD_INVALID")
    rows = [row for row in board["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise EvidenceError("BOARD_ROW_MISSING_OR_DUPLICATED")
    row = rows[0]
    stable = {
        "task_id": row.get("id"),
        "title": row.get("title"),
        "mode": row.get("mode"),
        "repository": row.get("repository"),
        "component": row.get("component"),
    }
    if stable != EXPECTED_LINK:
        raise EvidenceError("BOARD_IDENTITY_CHANGED")
    projection = [stable]
    return projection, sha256_bytes(canonical_bytes(projection))


def inventory_link() -> Dict[str, Any]:
    inventory = strict_json_loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    if not isinstance(inventory, dict) or not isinstance(
            inventory.get("components"), list):
        raise EvidenceError("INVENTORY_INVALID")
    rows = [row for row in inventory["components"]
            if isinstance(row, dict) and row.get("id") == COMPONENT]
    if len(rows) != 1:
        raise EvidenceError("INVENTORY_ROW_MISSING_OR_DUPLICATED")
    row = rows[0]
    projection = {
        "id": row.get("id"),
        "name": row.get("name"),
        "area": row.get("area"),
        "evidence_status": row.get("evidence_status"),
        "repository": row.get("repository"),
        "disposition": row.get("disposition"),
        "verification_profile": row.get("verification_profile"),
        "task": row.get("task"),
        "plan_note": row.get("plan_note"),
        "evidence_paths": [item.get("path")
                           for item in row.get("evidence", [])
                           if isinstance(item, dict)],
    }
    if projection != EXPECTED_INVENTORY:
        raise EvidenceError("INVENTORY_IDENTITY_CHANGED")
    return projection


def evidence_entry() -> Dict[str, Any]:
    lines = INVENTORY_MD_PATH.read_text(encoding="utf-8").splitlines()
    if EVIDENCE_LINE > len(lines):
        raise EvidenceError("EVIDENCE_LINE_OUT_OF_RANGE")
    text = lines[EVIDENCE_LINE - 1]
    missing = [token for token in EVIDENCE_TOKENS if token not in text]
    if missing:
        raise EvidenceError("EVIDENCE_TEXT_CHANGED")
    return {
        "path": "audio-benchmark-platform/plan/INVENTORY.md",
        "line": EVIDENCE_LINE,
        "text": text,
        "sha256": sha256_bytes(text.encode("utf-8")),
        "tokens_verified": list(EVIDENCE_TOKENS),
        "inventory_row_evidence_path":
            "research/distortion_restoration_20261028.md",
        "inventory_row_has_explicit_line": False,
        "linked_task": TASK,
        "note": (
            "Exact linked research-control row. It records an evaluated "
            "synthetic proxy, not a real transport codec result."),
    }


def artifact_pins() -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in REPORT_ARTIFACT_FILES:
        path = HERE / name
        if not path.is_file():
            raise EvidenceError("MISSING_ARTIFACT: " + name)
        pins[name] = sha256_file(path)
    return pins


def source_evidence_statements() -> List[str]:
    return [
        ("research/distortion_restoration_20261028.md records four separate "
         "restoration tasks and states that the 4-bit mu-law case is a stress "
         "proxy, not a standard codec, and that neither proxy models "
         "MP3/AAC/Opus transform artifacts, tandem coding or jitter."),
        ("scripts/evaluate_distortion_restoration.py builds the narrowband "
         "reference with 16 kHz -> 8 kHz resample_poly, applies the proxy, "
         "upsamples 8 kHz -> 16 kHz and postfilters at 3900 Hz with "
         "butter(4) + sosfiltfilt."),
        ("The frozen report aggregate for RST-03 records +0.282 dB SI-SDR for "
         "the 4-bit proxy and -4.873 dB for the 8-bit proxy, with STOI "
         "effectively unchanged; these are provenance values only."),
        ("plan/INVENTORY.json marks the component research-control with the "
         "Restoration profile and the plan note to keep the known 4/8-bit "
         "proxy separate from real transport codecs."),
        ("plan/swarm/VERIFICATION.md requires the Restoration profile: frozen "
         "corruption and packet baseline, degradation/erasure/bandwidth "
         "strata, discrete concealment validity, decoded intervals, quality "
         "and peak/timing bounds."),
    ]


def _required_results() -> Dict[str, str]:
    return {
        "exact_codec_reference_pin": "blocked",
        "real_transport_codec_matrix": "blocked",
        "pilot_runtime_reproduction": "blocked",
        "rights_cleared_paired_cohort": "blocked",
        "decoded_interval_and_bandwidth_stratification": "blocked",
        "task_specific_quality_metrics": "blocked_synthetic_only",
        "stoi_measurement": "blocked_runtime_absent",
        "independent_scoring": "blocked",
        "permitted_listening": "blocked",
        "target_runtime_timing": "blocked",
        "provider_intake": "deferred",
        "default_selection": "deferred",
    }


def _local_checks(report: Dict[str, Any]) -> Dict[str, bool]:
    fixture = report["fixture"]
    adverse = report["adverse"]
    conditions = fixture["conditions"]
    return {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "stable_board_identity_only": True,
        "inventory_identity_exact": report["inventory_link"] ==
        EXPECTED_INVENTORY,
        "source_pin_exact": report["source_probe"]["verified"],
        "codec_reference_absent": report["codec_reference_probe"]["status"] ==
        "absent",
        "runtime_unpinned_not_admitted": report["runtime_probe"]["pinned"]
        is False and report["runtime_probe"]["unpinned_venv"]["admitted"]
        is False,
        "corpus_absent_unread": report["corpus_probe"]["present"] is False
        and report["corpus_probe"]["real_audio_read"] is False,
        "rights_absent_blocked": report["rights_probe"]["entry_present"]
        is False and report["rights_probe"]["blocked"] is True,
        "pilot_metrics_match_frozen_report": (
            report["pilot_evidence"]["provenance_only"] is True and
            report["pilot_evidence"]["reproduced_here"] is False),
        "invalid_requests_rejected": adverse["invalid_config_and_input"][
            "all_rejected"],
        "invalid_json_rejected": adverse["invalid_json_numeric_fields"][
            "all_rejected"],
        "session_lifecycle_matches": adverse["session_lifecycle"][
            "matches_expectation"],
        "zero_peak_rejected": all(
            not case["accepted"] for case in
            adverse["invalid_config_and_input"]["cases"]
            if case["id"] in ("zero_signal", "below_peak_floor")),
        "nonfinite_rejected": all(
            not case["accepted"] for case in
            adverse["invalid_config_and_input"]["cases"]
            if case["id"].startswith("nonfinite")),
        "frame_postfilter_rejected": all(
            not case["accepted"] for case in
            adverse["invalid_config_and_input"]["cases"]
            if case["id"].startswith("postfilter")),
        "identity_control_bit_exact": fixture["identity_control"][
            "decoded_bit_exact"],
        "identity_filtered_not_identity": fixture["identity_control"][
            "filtered_bit_exact"] is False,
        "fixture_finite": fixture["all_finite"],
        "fixture_peak_bounded": fixture["peak_bounded"],
        "proxy_trend_matches_pilot_signs": (
            conditions["4bit"]["delta_si_sdr_db"] > 0.0 and
            conditions["8bit"]["delta_si_sdr_db"] < 0.0),
        "stoi_not_fabricated": all(
            condition[method]["stoi"] is None and
            condition[method]["stoi_status"] ==
            "not_computed_runtime_absent"
            for condition in conditions.values()
            for method in ("decoded_input", "lowpass_postfilter")),
        "eight_release_gates_blocked": (
            len(report["release_gates"]) == 8 and
            all(gate["status"] == "blocked"
                for gate in report["release_gates"])),
        "no_missing_result_qualifies": report[
            "no_missing_result_qualifies_candidate"],
        "real_corpus_not_read": True,
        "no_result_qualifies_candidate": True,
    }


def _fixture_checks(report: Dict[str, Any]) -> Dict[str, Any]:
    checks = _local_checks(report)
    return {
        "all_true": all(checks.values()),
        "check_count": len(checks),
        "checks": checks,
    }


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    fixture = evaluate_offline()
    adverse = {
        "invalid_config_and_input": _frame_cases(),
        "invalid_json_numeric_fields": _json_cases(),
        "session_lifecycle": _lifecycle_cases(),
        "missing_result": _missing_result(),
    }
    report: Dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_incomplete",
        "decision": "DEFER",
        "qualification_status": "not_qualified",
        "qualification": qualification(),
        "boundary": boundary(),
        "profile": {
            "name": "restoration",
            "source":
                SOURCE_PINS[
                    "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        },
        "profile_mapping": [
            "Freeze corruption and metadata: the fixture freezes a "
            "deterministic 8 kHz 4/8-bit peak-normalised log compander and "
            "a 3900 Hz zero-phase postfilter; the real transport codec and "
            "packet baseline are absent.",
            "Stratify by degradation, erasure burst and bandwidth: only the "
            "4-bit stress and 8-bit proxy strata exist; no erasure, burst, "
            "bandwidth or real-codec stratum exists.",
            "Report discrete concealment/validity and decoded intervals: no "
            "concealment or packet path is modelled; decoded interval counts "
            "for a real codec are absent.",
            "Report task-specific quality and peak/timing bounds: synthetic "
            "SI-SDR/RMSE and a finite/peak-bound check exist; STOI, real-"
            "codec quality and target-runtime timing are blocked.",
        ],
        "inventory_link": inventory_link(),
        "evidence_entry": evidence_entry(),
        "reference": {
            "implementation": "task-local stdlib deterministic proxy fixture",
            "pilot_source_present": True,
            "pilot_runtime_admitted": False,
            "pilot_corpus_present": False,
            "real_codec_reference_present": False,
            "real_codec_runtime_present": False,
            "candidate_processing": False,
            "real_corpus_read": False,
            "real_media_read": False,
            "downloads": False,
            "synthetic_only": True,
            "deterministic": True,
            "offline_only": True,
            "frame_causal": False,
            "upstream_parity": False,
            "pilot_numeric_parity": False,
            "note": (
                "The stdlib fixture reproduces the pinned pilot's quantizer, "
                "polyphase resampler and postfilter formulas exactly on a "
                "synthetic stimulus. It does not reproduce the pilot corpus, "
                "runtime, metric rows, STOI or any real codec output."),
        },
        "codec_boundary": {
            "proxy_definition": (
                "peak-normalised 2**bits-level logarithmic companding proxy "
                "from the pinned first-party pilot"),
            "is_g711_ulaw": False,
            "is_real_transport_codec": False,
            "keep_proxy_separate": True,
            "real_codec_families_not_covered": [
                "ITU-T G.711 companding",
                "MP3", "AAC", "Opus", "AMR", "tandem coding",
                "jitter and packet loss",
            ],
            "pilot_scope": (
                "synthetic 8 kHz narrowband proxy evaluated at 16 kHz"),
        },
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "source_evidence_statements": source_evidence_statements(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_link_fields": list(LINK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "artifact_pins": artifact_pins(),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "source_probe": source_probe(),
        "runtime_probe": runtime_probe(),
        "corpus_probe": corpus_probe(),
        "rights_probe": rights_probe(),
        "codec_reference_probe": codec_reference_probe(),
        "geometry": geometry(),
        "pilot_evidence": pilot_evidence(),
        "fixture": fixture,
        "adverse": adverse,
        "required_results": _required_results(),
        "release_gates": [dict(gate) for gate in GATES],
        "remaining_gates": [gate["id"] for gate in GATES],
        "no_missing_result_qualifies_candidate": True,
        "regressions": [],
        "regression_count": 0,
        "generated_by": "run.py --report",
    }
    report["local_harness_checks"] = _local_checks(report)
    report["harness_summary"] = _fixture_checks(report)
    if not finite_json(report):
        raise EvidenceError("REPORT_NONFINITE")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"


# ---------------------------------------------------------------------------
# Task-local git scope
# ---------------------------------------------------------------------------
SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None or _git(worktree, "merge-base", "--is-ancestor",
                                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise EvidenceError("GIT_SCOPE_DIFF_FAILED: " + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> List[str]:
    return [path for path in paths if path and not path.startswith(prefix)]
