# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, offline-tooling-only WAV and resampling reference fixture.

Task-local evidence for the audio-sdk public v0 boundary. It mirrors the exact
semantics of the pinned ``src/audioml_eval/audio.py`` adapter (read / write /
resample / pcm16 / sample_interval / prepare / chunks) using only the installed
pinned NumPy, SciPy and SoundFile libraries. No download, vendored binary, real
audio, device, network or listening result is used.

This is Tool-profile evidence. The tools are developer fixtures and offline
reference processing only; they are NEVER part of SDK runtime timing. Nothing
is registered, enabled by default or added to the installed v0 surface. Status
is ``proposal_only_synthetic_incomplete`` / ``not_qualified`` throughout.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib
import importlib.metadata
import json
import math
import os
import pathlib
import struct
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Sequence

TASK_ID = "SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING"
SLUG = "numpy-scipy-soundfile-wav-resampling"
SCHEMA_ID = "audio-sdk/task-evidence/numpy-scipy-soundfile-wav-resampling/report/0.1"
CONTRACT_ID = "audio-sdk/tooling/wav-resample/0.1"
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"

# Installed v0 SDK boundary (CONTRACTS.md). Tooling may use other rates and
# channel counts, but only OUTSIDE this boundary and outside runtime timing.
SDK_SAMPLE_RATE_HZ = 16000
SDK_CHANNELS = 1
SDK_SAMPLE_FORMAT = "f32"
SDK_FRAME_SAMPLES = 160

BASE_RATE_HZ = 16000
TARGET_RATES_HZ = (8000, 16000, 22050, 32000, 44100, 48000)
PYTHON_VERSION = "3.12.16"
LIB_VERSIONS = {"numpy": "2.5.4", "scipy": "1.18.1", "soundfile": "0.14.0"}
LIBSNDFILE_VERSION = "1.2.2"

SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
SITE_PACKAGES = Path(os.environ.get(
    "PY312_SITE_PACKAGES",
    "/Users/htsakanyan/.pyenv/versions/3.12.16/lib/python3.12/site-packages"))
SDK_ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

# Source and boundary bytes are resolved from the workspace; worktree paths
# are resolved from the SDK worktree; py312 paths from the pinned site-packages.
SOURCE_PINS: tuple[dict[str, str], ...] = (
    {
        "path": "src/audioml_eval/audio.py",
        "root": "source",
        "sha256": "0809b1cc1daa207e46125b0fcfa321088b4b6cccfadf04fabc2cd8b74c947e20",
        "summary": "Exact pinned developer adapter: read/write FLOAT WAV, "
                   "kaiser(5.0) resample_poly, pcm16, crop and chunk semantics.",
    },
    {
        "path": "audio-benchmark-platform/audio-sdk/CONTRACTS.md",
        "root": "source",
        "sha256": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
        "summary": "Installed public v0 boundary: 16 kHz, mono, f32, 160 "
                   "samples per call; resampling=none in effective config.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "root": "source",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "summary": "Tool acceptance profile: provenance, clean checkout, one "
                   "typical use, caller-owned inputs, malformed and missing "
                   "optional selections, separated build/runtime/workload.",
    },
    {
        "path": "audio-benchmark-platform/audio-sdk/REUSE.toml",
        "root": "source",
        "sha256": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
        "summary": "docs/** SPDX annotation coverage for the new evidence files.",
    },
    {
        "path": "api/include/audio_sdk/provider_v0.h",
        "root": "worktree",
        "sha256": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "summary": "Public v0 provider ABI; unchanged by this offline fixture.",
    },
    {
        "path": "api/include/audio_sdk/session_v0.h",
        "root": "worktree",
        "sha256": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
        "summary": "Public v0 session facade; unchanged by this offline fixture.",
    },
)

# Installed-package provenance. module files and native artifacts are hashed
# as bytes in place; nothing is copied or committed.
LIBRARY_PIN_FILES: tuple[dict[str, str], ...] = (
    {"id": "numpy", "kind": "module", "path": "numpy/__init__.py",
     "sha256": "09295a80660f17925ae23765ce8cbd7ff7ceae968d5f2f89349f1cb74c0b9e11"},
    {"id": "numpy", "kind": "metadata", "path": "numpy-2.5.4.dist-info/METADATA",
     "sha256": "e2b909d6a37d76c2bc130f528d7fed0c517322bce16dc7846b6a6df30e200403"},
    {"id": "numpy", "kind": "native", "path":
     "numpy/_core/_multiarray_umath.cpython-312-darwin.so",
     "sha256": "af36cbbb39b27651a8b9f7dfa491775016f331a58e8d116eb6b4cfd5e22efb77"},
    {"id": "scipy", "kind": "module", "path": "scipy/signal/_signaltools.py",
     "sha256": "ae162c8d1c43ee90fae826ab9f9232425bf66042b84d97fcd808b270d9309a51"},
    {"id": "scipy", "kind": "metadata", "path": "scipy-1.18.1.dist-info/METADATA",
     "sha256": "1adfbde8be136cbf348b889c51028e7e1824cdb90d29a26d8e81501948864fae"},
    {"id": "scipy", "kind": "native", "path":
     "scipy/signal/_sigtools.cpython-312-darwin.so",
     "sha256": "ef178698287fc0ff2cd4ded9308aba9b34cd50abc426efc18eee9bae4d693099"},
    {"id": "scipy", "kind": "native", "path":
     "scipy/signal/_upfirdn_apply.cpython-312-darwin.so",
     "sha256": "7473575ea92fecd7a2e3bb92155bbdb78ad92ceb79de45c04279a2c6f9d8fbc6"},
    {"id": "soundfile", "kind": "module", "path": "soundfile.py",
     "sha256": "085feb318464c2a5e82747e0d6da43c214f3a6a4ed3a7a18f2c07fe7b3750df2"},
    {"id": "soundfile", "kind": "metadata", "path": "soundfile-0.14.0.dist-info/METADATA",
     "sha256": "266fbe4cb310c5222edd5216564149585c55395db7b29630f2e4b0ff8ac9cd47"},
    {"id": "soundfile", "kind": "native", "path":
     "_soundfile_data/libsndfile_arm64.dylib",
     "sha256": "e9fd4d76bc457dcfb956617e8d467df85087ce069747fccd78e1e702d8629c14"},
)

QUALIFICATION_BLOCKERS: tuple[dict[str, str], ...] = (
    {
        "id": "sdk_runtime_timing",
        "status": "blocked",
        "reason": "WAV I/O and resampling are developer fixtures/offline "
                  "reference only. No SDK session, provider or paced runtime "
                  "path is exercised or timed here.",
        "reopen": "Measure the exact installed v0 build on the target under "
                  "pacing, load, deadline, CPU and memory budgets; keep this "
                  "offline tooling outside that timing.",
    },
    {
        "id": "real_audio_and_quality",
        "status": "blocked",
        "reason": "Only seeded synthetic signals are used; no real speech, "
                  "quality, listening or perceptual result exists.",
        "reopen": "Freeze rights-qualified material with an independently "
                  "reviewed protocol before any quality claim.",
    },
    {
        "id": "provider_intake",
        "status": "blocked",
        "reason": "No provider is compiled, registered or enabled. The "
                  "conceptual tooling ID has empty descriptor settings.",
        "reopen": "Complete opt-in OFF intake with independent review; do "
                  "not promote offline tooling into the SDK runtime.",
    },
)

CODE_ARTIFACTS = ("fixture.py", "test_fixture.py", "verify.py", "run.py")
ALL_ARTIFACTS = CODE_ARTIFACTS + (
    "report.json", "report.json.sha256", "README.md",
    "runtime-measurements.json", "SOURCES.sha256")

# Frozen signal specifications: name, generator kind, frames, channels, seed.
SIGNAL_SPECS: tuple[tuple[str, str, int, int, int], ...] = (
    ("impulse_1600_mono", "impulse", 1600, 1, 1001),
    ("sine_1k_1600_mono", "sine", 1600, 1, 1002),
    ("multitone_1600_mono", "multitone", 1600, 1, 1003),
    ("silence_1600_mono", "silence", 1600, 1, 1004),
    ("noise_1600_mono", "noise", 1600, 1, 1005),
    ("ramp_1600_mono", "ramp", 1600, 1, 1006),
    ("stereo_1600", "stereo", 1600, 2, 1007),
    ("triple_1600", "triple", 1600, 3, 1008),
    ("short_8_mono", "impulse", 8, 1, 1009),
    ("single_1_mono", "impulse", 1, 1, 1010),
    ("empty_0_mono", "silence", 0, 1, 1011),
)
ROUNDTRIP_SIGNALS = tuple(spec[0] for spec in SIGNAL_SPECS)
RESAMPLE_SIGNALS = ("impulse_1600_mono", "sine_1k_1600_mono",
                    "stereo_1600", "short_8_mono", "single_1_mono",
                    "empty_0_mono")


class LCG:
    """Version-stable 32-bit LCG; independent of NumPy/Python RNG internals."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def uniform(self) -> float:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return 2.0 * (self.state / 4294967296.0) - 1.0


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def array_digest(values: Any) -> str:
    """Exact digest over IEEE-754 little-endian f32 samples in C order."""
    array = values if hasattr(values, "tobytes") else _module("numpy").asarray(
        values, dtype="float32")
    ordered = array if getattr(array, "flags", None) is None or array.flags.c_contiguous else array.copy(order="C")
    return hashlib.sha256(ordered.astype("<f4", copy=False).tobytes()).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_pins() -> list[dict[str, str]]:
    return [{"path": name, "sha256": file_digest(HERE / name)}
            for name in CODE_ARTIFACTS]


def pin_root(pin: dict[str, str]) -> Path:
    return SOURCE_ROOT if pin["root"] == "source" else SDK_ROOT


# Optional-selection control: adapter functions import lazily through this
# indirection so a missing or blocked library is an explicit status, never a
# silent substitution. Default behaviour is the installed pinned module.
_IMPORTER: Callable[[str], Any] = importlib.import_module


@contextlib.contextmanager
def importer_override(importer: Callable[[str], Any]):
    global _IMPORTER
    previous = _IMPORTER
    _IMPORTER = importer
    try:
        yield
    finally:
        _IMPORTER = previous


def blocking_importer(*blocked: str) -> Callable[[str], Any]:
    denied = frozenset(blocked)

    def importer(name: str) -> Any:
        if name.split(".")[0] in denied:
            raise ImportError(f"blocked optional selection: {name}")
        return importlib.import_module(name)

    return importer


def _module(name: str) -> Any:
    return _IMPORTER(name)


def _version(name: str) -> str:
    return importlib.metadata.version(name)


def probe_optional_selection(
        importer: Optional[Callable[[str], Any]] = None,
        blocked: Iterable[str] = ()) -> dict[str, Any]:
    """Report exact installed provenance or an explicit missing selection."""
    denied = frozenset(blocked)
    use = importer or importlib.import_module
    entries: dict[str, Any] = {}
    for name in ("numpy", "scipy", "soundfile"):
        if name in denied:
            entries[name] = {"status": "missing_optional_selection",
                             "available": False, "version": None}
            continue
        try:
            module = use(name)
            version = _version(name)
            entries[name] = {
                "status": "ok" if version == LIB_VERSIONS[name] else "unpinned_selection",
                "available": True,
                "version": version,
                "module": str(pathlib.Path(module.__file__).resolve()),
            }
        except (ImportError, importlib.metadata.PackageNotFoundError) as error:
            entries[name] = {"status": "missing_optional_selection",
                             "available": False, "version": None,
                             "reason": type(error).__name__}
    statuses = {entry["status"] for entry in entries.values()}
    overall = ("ok" if statuses == {"ok"} else
               "missing_optional_selection" if "missing_optional_selection" in statuses
               else "unpinned_selection")
    return {"overall_status": overall, "entries": entries,
            "interpreter": sys.version.split()[0],
            "python_pin": PYTHON_VERSION,
            "site_packages": str(SITE_PACKAGES)}


# ---------------------------------------------------------------------------
# Local mirror of the exact pinned audioml_eval.audio boundary. The only
# intentional difference is lazy optional imports so a missing library is a
# reportable status instead of an import-time crash.
# ---------------------------------------------------------------------------
def read(path: Any, *, rate: Optional[int] = None,
         channels: Optional[int] = None) -> tuple[Any, int]:
    """Decode without normalization or downmixing; reject LFS pointers."""
    with open(path, "rb") as handle:
        if handle.read(40).startswith(b"version https://git-lfs.github.com/spec/"):
            raise ValueError("Git LFS pointer is not audio")
    np = _module("numpy")
    sf = _module("soundfile")
    data, actual_rate = sf.read(str(path), dtype="float32", always_2d=True)
    if rate is not None and actual_rate != rate:
        raise ValueError("unexpected sample rate")
    if channels is not None and data.shape[1] != channels:
        raise ValueError("unexpected channel count")
    if not np.isfinite(data).all():
        raise ValueError("non-finite samples")
    return data, actual_rate


def write(path: Any, samples: Any, rate: int) -> None:
    np = _module("numpy")
    sf = _module("soundfile")
    samples = np.asarray(samples, dtype=np.float32)
    if samples.ndim != 2 or not np.isfinite(samples).all() or rate <= 0:
        raise ValueError("audio must be finite samples by channels at a positive rate")
    sf.write(str(path), samples, rate, format="WAV", subtype="FLOAT")


def resample(samples: Any, source_rate: int, target_rate: int) -> Any:
    np = _module("numpy")
    resample_poly = _module("scipy.signal").resample_poly
    samples = np.asarray(samples, dtype=np.float32)
    if samples.ndim != 2 or source_rate <= 0 or target_rate <= 0:
        raise ValueError("invalid audio or rate")
    divisor = math.gcd(source_rate, target_rate)
    up, down = target_rate // divisor, source_rate // divisor
    if not len(samples):
        return np.empty((0, samples.shape[1]), dtype=np.float32)
    result = resample_poly(samples, up, down, axis=0, window=("kaiser", 5.0),
                           padtype="constant", cval=0).astype(np.float32)
    expected = (len(samples) * up + down - 1) // down
    if len(result) != expected:
        raise ValueError("resampler produced unexpected sample count")
    return result


def pcm16(samples: Any) -> tuple[Any, int]:
    np = _module("numpy")
    samples = np.asarray(samples, dtype=np.float32)
    if not np.isfinite(samples).all():
        raise ValueError("non-finite PCM input")
    rounded = np.rint(samples.astype(np.float64) * 32768)
    clipped = int(np.count_nonzero((rounded < -32768) | (rounded > 32767)))
    return np.clip(rounded, -32768, 32767).astype(np.int16), clipped


def sample_interval(start: float, end: float, rate: int, length: int) -> tuple[int, int]:
    if not all(math.isfinite(x) for x in (start, end)) or start < 0 or end < start or rate <= 0 or length < 0:
        raise ValueError("invalid interval")
    return min(length, math.floor(start * rate)), min(length, math.ceil(end * rate))


def prepare(path: Any, *, rate: Optional[int] = None,
            channels: Optional[int] = None, start: Optional[float] = None,
            end: Optional[float] = None) -> tuple[Any, int]:
    samples, source_rate = read(path, channels=channels)
    if start is not None or end is not None:
        if start is None or end is None:
            raise ValueError("crop requires both endpoints")
        a, b = sample_interval(start, end, source_rate, len(samples))
        samples = samples[a:b]
    if rate is not None and rate != source_rate:
        samples = resample(samples, source_rate, rate)
    return samples, rate or source_rate


def chunks(length: int, sizes: Sequence[int]):
    if length < 0 or not sizes or any(size <= 0 for size in sizes):
        raise ValueError("invalid chunk schedule")
    position = 0
    index = 0
    while position < length:
        end = min(length, position + sizes[index % len(sizes)])
        yield position, end
        position, index = end, index + 1


# ---------------------------------------------------------------------------
# Deterministic synthetic generator
# ---------------------------------------------------------------------------
def make_signal(kind: str, frames: int, channels: int, seed: int) -> Any:
    np = _module("numpy")
    out = np.zeros((frames, channels), dtype=np.float32)
    if not frames:
        return out
    rng = LCG(seed)
    for channel in range(channels):
        channel_rng = LCG(seed + 7919 * channel)
        for index in range(frames):
            t = index / BASE_RATE_HZ
            if kind == "silence":
                value = 0.0
            elif kind == "impulse":
                value = 0.8 if index == frames // 4 else 0.0
            elif kind == "sine":
                value = 0.25 * math.sin(2.0 * math.pi * 1000.0 * t)
            elif kind == "multitone":
                value = sum(0.09 * math.sin(2.0 * math.pi * freq * t)
                            for freq in (220.0, 440.0, 880.0, 1760.0))
            elif kind == "noise":
                value = 0.12 * channel_rng.uniform()
            elif kind == "ramp":
                value = -0.5 + index / max(frames - 1, 1)
            elif kind == "stereo":
                value = (0.25 * math.sin(2.0 * math.pi * 1000.0 * t)
                         if channel == 0 else
                         0.18 * math.sin(2.0 * math.pi * 440.0 * t)
                         + 0.05 * channel_rng.uniform())
            elif kind == "triple":
                if channel == 0:
                    value = 0.25 * math.sin(2.0 * math.pi * 1000.0 * t)
                elif channel == 1:
                    value = 0.12 * channel_rng.uniform()
                else:
                    value = 0.0
            else:
                raise ValueError(f"unknown signal kind: {kind}")
            out[index, channel] = value
    _ = rng  # reserved deterministic stream marker; generation uses per-channel LCG
    return out


def build_signals() -> dict[str, Any]:
    return {name: make_signal(kind, frames, channels, seed)
            for name, kind, frames, channels, seed in SIGNAL_SPECS}


def signal_features(values: Any) -> dict[str, Any]:
    np = _module("numpy")
    array = np.asarray(values, dtype=np.float32)
    finite = bool(np.isfinite(array).all())
    peak = float(np.max(np.abs(array))) if array.size else 0.0
    rms = float(np.sqrt(np.mean(array.astype(np.float64) ** 2))) if array.size else 0.0
    return {
        "frames": int(array.shape[0]) if array.ndim == 2 else None,
        "channels": int(array.shape[1]) if array.ndim == 2 else None,
        "finite": finite,
        "peak_abs": round(peak, 9),
        "rms": round(rms, 9),
        "digest": array_digest(array),
    }


def first_values(values: Any, count: int = 8) -> list[float]:
    np = _module("numpy")
    flat = np.asarray(values, dtype=np.float32).reshape(-1)
    return [round(float(value), 9) for value in flat[:count]]


def exception_kind(error: BaseException) -> str:
    """Normalized failure name; never include a temp path in the report."""
    if isinstance(error, ValueError):
        return "ValueError"
    if isinstance(error, ImportError):
        return "ImportError"
    return type(error).__name__


def attempt(callable_: Callable[[], Any]) -> dict[str, Any]:
    try:
        result = callable_()
    except Exception as error:  # noqa: BLE001 - explicit normalized failure record
        return {"status": "rejected", "exception": exception_kind(error)}
    return {"status": "ok", "result": result}


# ---------------------------------------------------------------------------
# Evidence sections
# ---------------------------------------------------------------------------
def compile_build_section() -> dict[str, Any]:
    libraries = []
    for name, version in LIB_VERSIONS.items():
        module = importlib.import_module(name)
        libraries.append({
            "id": name,
            "version": version,
            "installed_version": _version(name),
            "module": str(pathlib.Path(module.__file__).resolve()),
            "install_location": str(SITE_PACKAGES),
            "provenance": "installed wheel in pinned Python 3.12.16 environment; "
                          "no download and no in-tree vendor",
        })
    return {
        "status": "verified_installed_packages",
        "compilation_performed": False,
        "note": "Python wheels are already compiled and installed; this "
                "fixture performs no build, install, download or vendoring. "
                "Clean-checkout and write-scope checks are read-only in verify.py.",
        "python": {"pin": PYTHON_VERSION, "runtime": sys.version.split()[0],
                   "executable": sys.executable},
        "libraries": libraries,
        "pinned_library_files": [dict(record) for record in LIBRARY_PIN_FILES],
        "libsndfile_version": LIBSNDFILE_VERSION,
        "base_commit": BASE_COMMIT,
        "expected_branch": f"swarm/{TASK_ID}",
    }


def synthetic_runtime_section(signals: dict[str, Any], tmp: str) -> dict[str, Any]:
    np = _module("numpy")
    signal_info = {name: signal_features(values) for name, values in signals.items()}

    # One typical caller-owned use: FLOAT WAV write + read is bit-exact.
    roundtrip: dict[str, Any] = {}
    for name in ROUNDTRIP_SIGNALS:
        source = signals[name]
        path = os.path.join(tmp, f"rt_{name}.wav")
        write(path, source, BASE_RATE_HZ)
        decoded, rate = read(path, rate=BASE_RATE_HZ,
                             channels=source.shape[1])
        roundtrip[name] = {
            "status": "ok",
            "wav_bytes": Path(path).stat().st_size,
            "sample_rate_hz": rate,
            "bit_exact": bool(np.array_equal(source, decoded)),
            "input_digest": array_digest(source),
            "output_digest": array_digest(decoded),
        }
        if not roundtrip[name]["bit_exact"]:
            roundtrip[name]["status"] = "roundtrip_mismatch"

    # Format edge: PCM_16 WAV is readable but quantised relative to FLOAT.
    pcm_path = os.path.join(tmp, "pcm16_format.wav")
    raw_sf = _module("soundfile")
    raw_sf.write(pcm_path, signals["sine_1k_1600_mono"], BASE_RATE_HZ,
                 format="WAV", subtype="PCM_16")
    pcm_decoded, _ = read(pcm_path)
    pcm_diff = float(np.max(np.abs(
        signals["sine_1k_1600_mono"] - pcm_decoded)))
    format_case = {
        "status": "ok",
        "subtype": "PCM_16",
        "wav_bytes": Path(pcm_path).stat().st_size,
        "max_abs_quantisation_error": round(pcm_diff, 9),
        "differs_from_float_roundtrip": bool(pcm_diff > 0.0),
        "output_digest": array_digest(pcm_decoded),
    }

    # Resampling matrix on frozen synthetic signals.
    resampling: dict[str, Any] = {}
    for name in RESAMPLE_SIGNALS:
        source = signals[name]
        source_digest = array_digest(source)
        for target in TARGET_RATES_HZ:
            divisor = math.gcd(BASE_RATE_HZ, target)
            up, down = target // divisor, BASE_RATE_HZ // divisor
            output = resample(source, BASE_RATE_HZ, target)
            expected = (len(source) * up + down - 1) // down
            key = f"{name}__{BASE_RATE_HZ}_to_{target}"
            resampling[key] = {
                "source_signal": name,
                "source_rate_hz": BASE_RATE_HZ,
                "target_rate_hz": target,
                "up": up, "down": down,
                "expected_frames": expected,
                "actual_frames": int(len(output)),
                "count_matches": int(len(output)) == expected,
                "finite": signal_features(output)["finite"],
                "output_digest": array_digest(output),
                "first_values": first_values(output),
            }

    # pcm16 clipping behaviour and non-mutation of caller arrays.
    clipped_path = os.path.join(tmp, "clipped.wav")
    clipped_input = np.array([[-1.5, -0.5], [0.5, 1.5]], dtype=np.float32)
    pcm_values, clipped_count = pcm16(clipped_input)
    write(clipped_path, clipped_input, BASE_RATE_HZ)
    pcm_result = {
        "clipped_count": clipped_count,
        "values": pcm_values.astype(int).tolist(),
        "write_dtype_f32": str(np.asarray(clipped_input).dtype),
        "nonfinite_rejected": attempt(lambda: pcm16(np.array([[float("nan")]],
                                                            dtype=np.float32)))["status"],
    }

    # prepare (crop + resample) and chunk schedule.
    prep_path = os.path.join(tmp, "prepare.wav")
    write(prep_path, signals["sine_1k_1600_mono"], BASE_RATE_HZ)
    prepared, out_rate = prepare(prep_path, channels=1, start=0.02, end=0.04,
                                 rate=48000)
    plan = list(chunks(len(signals["sine_1k_1600_mono"]), (160, 320)))
    prepare_and_chunks = {
        "prepared_frames": int(len(prepared)),
        "output_rate_hz": out_rate,
        "output_digest": array_digest(prepared),
        "crop_rejected_without_end": attempt(
            lambda: prepare(prep_path, start=0.02))["status"],
        "chunk_count": len(plan),
        "chunk_covers_all_samples": plan[0][0] == 0
        and plan[-1][1] == len(signals["sine_1k_1600_mono"])
        and all(right > left for left, right in plan),
        "chunk_invalid_schedule": attempt(lambda: list(chunks(10, (0,))))["status"],
    }

    return {
        "signals": signal_info,
        "one_typical_use_wav_float_roundtrip": roundtrip,
        "format_edge_pcm16_read": format_case,
        "resampling": resampling,
        "pcm16": pcm_result,
        "prepare_and_chunks": prepare_and_chunks,
        "crosscheck_vectors": {
            "sine_1k_first_values": first_values(signals["sine_1k_1600_mono"]),
            "resampled_16k_to_8k_first_values": first_values(
                resample(signals["sine_1k_1600_mono"], 16000, 8000)),
            "resampled_16k_to_48k_first_values": first_values(
                resample(signals["sine_1k_1600_mono"], 16000, 48000)),
        },
    }


def failures_section(tmp: str, signals: dict[str, Any]) -> dict[str, Any]:
    np = _module("numpy")
    good_path = os.path.join(tmp, "rt_sine_1k_1600_mono.wav")
    lfs_path = os.path.join(tmp, "lfs_pointer.wav")
    Path(lfs_path).write_bytes(
        b"version https://git-lfs.github.com/spec/v1\noid sha256:deadbeef\n")
    empty_path = os.path.join(tmp, "empty.wav")
    Path(empty_path).write_bytes(b"")
    riff_path = os.path.join(tmp, "truncated_riff.wav")
    Path(riff_path).write_bytes(b"RIFF\x24\x00\x00\x00WAVE")
    text_path = os.path.join(tmp, "text.wav")
    Path(text_path).write_bytes(b"not a WAV container" * 4)

    cases: dict[str, Any] = {}
    cases["git_lfs_pointer"] = attempt(lambda: read(lfs_path))
    cases["empty_file"] = attempt(lambda: read(empty_path))
    cases["truncated_riff_header"] = attempt(lambda: read(riff_path))
    cases["non_wav_bytes"] = attempt(lambda: read(text_path))
    cases["missing_file"] = attempt(lambda: read(os.path.join(tmp, "absent.wav")))
    cases["unexpected_sample_rate"] = attempt(
        lambda: read(good_path, rate=48000))
    cases["unexpected_channel_count"] = attempt(
        lambda: read(good_path, channels=2))
    cases["write_nonfinite"] = attempt(lambda: write(
        os.path.join(tmp, "bad_nonfinite.wav"),
        np.array([[float("inf")]], dtype=np.float32), BASE_RATE_HZ))
    cases["write_1d"] = attempt(lambda: write(
        os.path.join(tmp, "bad_1d.wav"),
        np.array([0.1, 0.2], dtype=np.float32), BASE_RATE_HZ))
    cases["write_rate_zero"] = attempt(lambda: write(
        os.path.join(tmp, "bad_rate.wav"), signals["single_1_mono"], 0))
    cases["resample_1d"] = attempt(lambda: resample(
        np.array([0.1, 0.2], dtype=np.float32), 16000, 8000))
    cases["resample_rate_zero"] = attempt(lambda: resample(
        signals["single_1_mono"], 16000, 0))
    cases["sample_interval_invalid"] = attempt(
        lambda: sample_interval(0.1, 0.0, 16000, 1600))
    cases["chunk_invalid"] = attempt(lambda: list(chunks(4, ())))

    # Missing optional selections: explicit status, no file written, no substitute.
    missing_path = os.path.join(tmp, "missing_optional.wav")
    with importer_override(blocking_importer("numpy")):
        missing_numpy_read = probe_optional_selection(blocked=("numpy",))
        missing_numpy_write = attempt(lambda: write(
            missing_path, signals["single_1_mono"], BASE_RATE_HZ))
    with importer_override(blocking_importer("soundfile")):
        missing_soundfile_read = attempt(lambda: read(good_path))
        missing_soundfile_write = attempt(lambda: write(
            missing_path, signals["single_1_mono"], BASE_RATE_HZ))
    with importer_override(blocking_importer("scipy")):
        missing_scipy_resample = attempt(lambda: resample(
            signals["single_1_mono"], 16000, 8000))
    cases["missing_optional_selection"] = {
        "numpy_probe_status": missing_numpy_read["overall_status"],
        "numpy_write": missing_numpy_write,
        "soundfile_read": missing_soundfile_read,
        "soundfile_write": missing_soundfile_write,
        "scipy_resample": missing_scipy_resample,
        "no_fallback_written": not Path(missing_path).exists(),
    }

    # Caller-owned inputs: no mutation and no retained references.
    source = signals["sine_1k_1600_mono"].copy()
    before = array_digest(source)
    resampled = resample(source, 16000, 48000)
    resampled[0, 0] = -99.0
    caller_owned = {
        "input_unchanged_after_resample": array_digest(source) == before,
        "output_is_independent_array": not np.shares_memory(source, resampled),
        "read_accepts_caller_path": attempt(
            lambda: read(good_path, rate=16000))["status"],
        "write_accepts_caller_path": attempt(
            lambda: write(os.path.join(tmp, "caller_owned.wav"),
                          source, BASE_RATE_HZ))["status"],
    }
    return {"cases": cases, "caller_owned": caller_owned}


def build_report() -> dict[str, Any]:
    np = _module("numpy")
    if sys.version.split()[0] != PYTHON_VERSION:
        raise ValueError("pinned Python not active")
    for name, version in LIB_VERSIONS.items():
        if _version(name) != version:
            raise ValueError(f"unpinned library: {name}")
    if _module("soundfile").__libsndfile_version__ != LIBSNDFILE_VERSION:
        raise ValueError("unpinned libsndfile")

    signals = build_signals()
    optional = probe_optional_selection()
    if optional["overall_status"] != "ok":
        raise ValueError("optional selection is not the pinned environment")
    with tempfile.TemporaryDirectory(prefix="sdk-wav-resample-") as tmp:
        runtime = synthetic_runtime_section(signals, tmp)
        failures = failures_section(tmp, signals)

    roundtrip = runtime["one_typical_use_wav_float_roundtrip"]
    resampling = runtime["resampling"]
    flags = {
        "all_float_roundtrips_bit_exact": all(
            case["bit_exact"] for case in roundtrip.values()),
        "all_resample_counts_match": all(
            case["count_matches"] for case in resampling.values()),
        "all_resample_outputs_finite": all(
            case["finite"] for case in resampling.values()),
        "pcm16_clip_count_positive": runtime["pcm16"]["clipped_count"] == 2,
        "prepare_crop_and_resample_ok": runtime["prepare_and_chunks"][
            "prepared_frames"] > 0,
        "malformed_inputs_rejected": all(
            failures["cases"][name]["status"] == "rejected"
            for name in ("git_lfs_pointer", "empty_file", "truncated_riff_header",
                         "non_wav_bytes", "missing_file")),
        "edge_inputs_rejected": all(
            failures["cases"][name]["status"] == "rejected"
            for name in ("unexpected_sample_rate", "unexpected_channel_count",
                         "write_nonfinite", "write_1d", "write_rate_zero",
                         "resample_1d", "resample_rate_zero",
                         "sample_interval_invalid", "chunk_invalid")),
        "missing_optional_selection_explicit": (
            failures["cases"]["missing_optional_selection"]["numpy_probe_status"]
            == "missing_optional_selection"
            and all(failures["cases"]["missing_optional_selection"][key]["status"]
                    == "rejected" for key in (
                        "numpy_write", "soundfile_read", "soundfile_write",
                        "scipy_resample"))
            and failures["cases"]["missing_optional_selection"]["no_fallback_written"]),
        "caller_owned_inputs_isolated": all(
            failures["caller_owned"][key] for key in (
                "input_unchanged_after_resample", "output_is_independent_array",
                "read_accepts_caller_path", "write_accepts_caller_path")),
        "sdk_runtime_timing_excluded": True,
        "no_missing_result_qualifies_candidate": True,
    }
    counts = {
        "signals": len(signals),
        "wav_float_roundtrips": len(roundtrip),
        "resampling_cases": len(resampling),
        "target_rates": list(TARGET_RATES_HZ),
        "malformed_input_cases": len(("git_lfs_pointer", "empty_file",
                                      "truncated_riff_header", "non_wav_bytes",
                                      "missing_file")),
        "missing_optional_selections": 3,
        "source_pins": len(SOURCE_PINS),
        "library_pin_files": len(LIBRARY_PIN_FILES),
        "code_artifacts": len(artifact_pins()),
    }
    spec = {
        "contract": CONTRACT_ID,
        "schema": SCHEMA_ID,
        "task_id": TASK_ID,
        "base_commit": BASE_COMMIT,
        "profile": "Tool",
        "sdk_boundary": {"sample_rate_hz": SDK_SAMPLE_RATE_HZ,
                         "channels": SDK_CHANNELS,
                         "sample_format": SDK_SAMPLE_FORMAT,
                         "frame_samples": SDK_FRAME_SAMPLES},
        "base_rate_hz": BASE_RATE_HZ,
        "target_rates_hz": list(TARGET_RATES_HZ),
        "signal_specs": [list(row) for row in SIGNAL_SPECS],
        "library_versions": dict(LIB_VERSIONS),
        "libsndfile_version": LIBSNDFILE_VERSION,
        "source_pins": {pin["path"]: pin["sha256"] for pin in SOURCE_PINS},
        "library_pin_files": {pin["path"]: pin["sha256"]
                              for pin in LIBRARY_PIN_FILES},
        "artifact_pins": {pin["path"]: pin["sha256"] for pin in artifact_pins()},
    }
    report: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task_id": TASK_ID,
        "base_commit": BASE_COMMIT,
        "profile": "Tool",
        "candidate_status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "no_missing_result_qualifies_candidate": True,
        "fixture_digest": object_digest(spec),
        "scope": {
            "claim": "Deterministic offline tooling fixture for WAV read/write "
                     "and resampling; developer-facing adapter only.",
            "no_public_api_change": True,
            "no_provider_registered": True,
            "no_default_enabled": True,
            "no_sdk_runtime_timing": True,
            "boundary_statement": "NumPy/SciPy/SoundFile read, write and "
                                  "resample are fixtures and offline reference "
                                  "processing only. They are NEVER included in "
                                  "SDK runtime timing; installed v0 remains "
                                  "16 kHz mono f32 at 160 samples per call.",
        },
        "boundary": {
            "sdk_public_boundary": {"sample_rate_hz": SDK_SAMPLE_RATE_HZ,
                                    "channels": SDK_CHANNELS,
                                    "sample_format": SDK_SAMPLE_FORMAT,
                                    "frame_samples": SDK_FRAME_SAMPLES},
            "tooling_rates_hz": [BASE_RATE_HZ, *TARGET_RATES_HZ],
            "tooling_channels": [1, 2, 3],
            "registered": False,
            "enabled_by_default": False,
            "descriptor_settings": {},
            "conceptual_id": "tooling.numpy-scipy-soundfile-wav.v0",
            "included_in_sdk_runtime_timing": False,
        },
        "pins": {
            "source_pins": [dict(pin) for pin in SOURCE_PINS],
            "library_pin_files": [dict(pin) for pin in LIBRARY_PIN_FILES],
            "artifact_pins": artifact_pins(),
            "quantization": {"digest_bytes": "IEEE-754 little-endian float32",
                             "json": "RFC 8785-like canonical sorted compact"},
        },
        "optional_selection": optional,
        "compile_build": compile_build_section(),
        "synthetic_runtime": runtime,
        "failure_cases": failures,
        "counts": counts,
        "flags": flags,
        "blockers": [dict(item) for item in QUALIFICATION_BLOCKERS],
        "evidence_classes": {
            "synthetic_offline_tooling": "Seeded, frozen signals generated here.",
            "source_reported": "none; no external benchmark value is pooled.",
            "real_audio_rights_qualified": "none",
            "sdk_runtime_or_device": "none",
        },
        "gates": [
            {"id": "clean_checkout_and_pins", "status": "pass",
             "detail": "verify.py rechecks every pinned byte and write scope."},
            {"id": "one_typical_use", "status": "pass",
             "detail": "FLOAT WAV write/read is bit-exact on all frozen signals."},
            {"id": "malformed_and_edge_inputs", "status": "pass",
             "detail": "Malformed WAVs, rate/channel/shape/rate-limit cases are rejected."},
            {"id": "missing_optional_selection", "status": "pass",
             "detail": "Blocked numpy/scipy/soundfile return explicit status with "
                       "no substitute and no written file."},
            {"id": "compile_build_vs_runtime_vs_workload", "status": "pass",
             "detail": "Installed-package provenance, deterministic synthetic "
                       "results and unpaced workload pointer are separate."},
            {"id": "sdk_runtime_timing", "status": "blocked",
             "detail": "Offline tooling is explicitly outside SDK runtime timing."},
        ],
    }
    if any(not value for key, value in flags.items()
           if key != "no_missing_result_qualifies_candidate"):
        raise AssertionError("tooling fixture flag failed")
    return report


def qualification_state(report: dict[str, Any]) -> str:
    """Missing or failed evidence never qualifies the candidate."""
    if not report.get("no_missing_result_qualifies_candidate"):
        raise ValueError("missing-result gate disabled")
    if any(not value for key, value in report["flags"].items()
           if key != "no_missing_result_qualifies_candidate"):
        return "not_qualified"
    if any(item["status"] == "blocked" for item in report["blockers"]):
        return "not_qualified"
    return "proposal_only_synthetic_incomplete"


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def write_report(path: Path) -> str:
    payload = canonical_report_bytes(build_report())
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def measure_workload() -> dict[str, Any]:
    """Non-deterministic, unpaced pointer; never qualification timing."""
    np = _module("numpy")
    signals = build_signals()
    repeats = 12
    wav_times: list[float] = []
    resample_times: list[float] = []
    with tempfile.TemporaryDirectory(prefix="sdk-wav-workload-") as tmp:
        path = os.path.join(tmp, "workload.wav")
        for _ in range(repeats):
            start = time.perf_counter()
            write(path, signals["sine_1k_1600_mono"], 16000)
            read(path, rate=16000, channels=1)
            wav_times.append(time.perf_counter() - start)
        for _ in range(repeats):
            start = time.perf_counter()
            resample(signals["sine_1k_1600_mono"], 16000, 48000)
            resample_times.append(time.perf_counter() - start)
    return {
        "schema_id": SCHEMA_ID + "/workload-pointer/0.1",
        "task_id": TASK_ID,
        "base_commit": BASE_COMMIT,
        "non_deterministic": True,
        "unpaced": True,
        "qualification_status": "blocked",
        "deadline_ns": None,
        "included_in_sdk_runtime_timing": False,
        "reads": {"repeats": repeats,
                  "median_wav_write_read_s": round(float(np.median(wav_times)), 9)},
        "resampling": {"repeats": repeats,
                       "median_16k_to_48k_s": round(float(np.median(resample_times)), 9)},
        "note": "Unpaced wall-clock pointer for this installed Python reference "
                "only. No pacing, load, target device, CPU/memory budget, SDK "
                "session timing, deadline or qualification result is claimed.",
    }


def sources_text() -> str:
    lines = ["# SHA-256 pins for SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING.",
             "# source: = workspace root, py312: = pinned site-packages, others = SDK worktree.",
             "# SOURCES.sha256 cannot pin its own bytes and is intentionally omitted."]
    for pin in SOURCE_PINS:
        prefix = "source:" if pin["root"] == "source" else ""
        lines.append(f"{pin['sha256']}  {prefix}{pin['path']}")
    for pin in LIBRARY_PIN_FILES:
        lines.append(f"{pin['sha256']}  py312:{pin['path']}")
    for name in ALL_ARTIFACTS:
        if name == "SOURCES.sha256":
            continue
        lines.append(f"{file_digest(HERE / name)}  "
                     f"docs/task-evidence/{SLUG}/{name}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--measure":
        payload = canonical_bytes(measure_workload()) + b"\n"
        Path(sys.argv[2]).write_bytes(payload)
        print(hashlib.sha256(payload).hexdigest())
    elif len(sys.argv) == 3 and sys.argv[1] == "--pins":
        (HERE / "SOURCES.sha256").write_text(sources_text(), encoding="utf-8")
        print(file_digest(HERE / "SOURCES.sha256"))
    else:
        print(write_report(Path(sys.argv[1])))
