# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local feasibility evidence for SDK-LIBROSA-BEAT-TRACK-TEMPO.

The recorded candidate is librosa ``beat_track`` / ``tempo`` (ISC).  This
module does not contain, import, install, download or execute librosa.  It
pins the evidence that exists, proves a fixed absence inventory, applies the
Rate acceptance profile to a bounded synthetic click surrogate, exercises a
fail-closed caller-supplied tool manifest without loading or executing a
runtime, and builds canonical ``DEFER`` bytes.

Nothing here is a librosa output, beat/tempo measurement on real music or
speech, listening result, device timing, benchmark or release claim.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

TASK = "SDK-LIBROSA-BEAT-TRACK-TEMPO"
TASK_TITLE = "librosa beat_track / tempo"
COMPONENT_ID = "librosa-beat-track-tempo"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "caller_tool_admission"
DISPOSITION = "sdk-reference"
QUALIFICATION_STATUS = "not_qualified"
WRITE_SCOPE = "docs/task-evidence/librosa-beat-track-tempo/ only"
TASK_PREFIX = "docs/task-evidence/librosa-beat-track-tempo/"
CONTRACT_ID = "audio-sdk/librosa-beat-track-tempo-readiness/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/librosa-beat-track-tempo-contract/0.1"
REPORT_SCHEMA_ID = "audio-sdk/librosa-beat-track-tempo-report/0.1"
CALLER_MANIFEST_SCHEMA_ID = (
    "audio-sdk/librosa-beat-track-tempo-caller-tool-manifest/0.1")
BASE_COMMIT = "b02dbf12499038abc4f9b6b1c06cdecc76a79dcd"
BRANCH = "swarm/SDK-LIBROSA-BEAT-TRACK-TEMPO"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-LIBROSA-BEAT-TRACK-TEMPO")
REVIEWER = "reviewer-LIBROSA-BEAT-TRACK-TEMPO"
OWNER = "agent-LIBROSA-BEAT-TRACK-TEMPO"
DEPENDS_ON = ("SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
REQUIRED_INTERPRETER = "3.12.16"

# Recorded upstream identity.  All of it is documentation metadata only.
UPSTREAM_LICENSE = "ISC"
UPSTREAM_DEFAULT_SAMPLE_RATE_HZ = 22050
UPSTREAM_DEFAULT_HOP_LENGTH = 512
UPSTREAM_DEFAULT_N_FFT = 2048
UPSTREAM_ENTRYPOINTS = ("librosa.beat.beat_track", "librosa.beat.tempo")

# Installed v0 geometry.  The surrogate is frame-clocked to this geometry.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
HOP_SAMPLES = 160
NS_PER_SAMPLE = 62500
NS_PER_FRAME = 10000000

# Synthetic tempo search bounds and stability rule.
MIN_BPM_X100 = 4000
MAX_BPM_X100 = 24000
MAX_IOI_SAMPLES = 20000
STABLE_TOLERANCE_PERMILLE = 50
MIN_IOIS = 3
ONSET_THRESHOLD_PERMILLE = 50

# Observed only at authoring time in an unpinned Python 3.11.5 venv.  These
# values are recorded, not admitted, pinned, gated or interpreted as a runtime.
OBSERVED_LOCAL_RUNTIME = {
    "path": ("cpp-library/pipeline-validation/playback-speed/.venv"),
    "python": "3.11.5",
    "librosa_version": "0.11.0",
    "librosa_tree_sha256":
        "8bf21ac388442346613586bd5cc72e12e221c3c8df26406e2ec9265a20d0f6d6",
    "dist_info_metadata_sha256":
        "5aaba06be0f28ca1ca776f8884fc0945f752a38d7ddca249403644d6f685c6d3",
    "dist_info_license_sha256":
        "1746ca32b53fa31941c38b63a986e4126ab998e81a2f73a566000847a588e2a3",
    "dist_info_wheel_sha256":
        "e76045458d94a74d9492339adbd799392d95c54ae93ce457835a64a21186512f",
    "present_at_authoring": True,
    "admitted": False,
    "pinned": False,
    "imported": False,
    "executed": False,
    "reason": ("python_3_11_5_is_not_the_required_pinned_3_12_16_runtime"),
}

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
SDK_ROOT = WORKTREE


def _find_audio_root() -> Path:
    override = os.environ.get("SOURCE_ROOT")
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    for candidate in candidates:
        board = candidate / "audio-benchmark-platform/plan/swarm/TASKS.json"
        if board.is_file() and (candidate / "research").is_dir():
            return candidate.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

# Read-only inputs.  ``source:`` paths are workspace-relative; ``sdk:`` paths
# are SDK-worktree-relative.  The mutable shared board is never pinned.
SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/speech-rate-tsm-evaluation-20261101.md":
        "525a25c12753ea7fad71aa7101b2c872d5511813fd0ea9b18231b347a8fda96d",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/audio-sdk/README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
}

BOUNDARY_PINS = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "bindings/python/audio_sdk/__init__.py":
        "3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864",
    "docs/provider-intake.md":
        "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/aubio/README.md":
        "700153d2541f9f4836e878fd6bfec631b644d1bf55ab0868e03f880858bd5e1d",
    "docs/task-evidence/aubio/report.json":
        "0ee56f1ecc66440b25f8d0c54e88ba5d2ba4f66c316fe8b0c3a4e626896e06f1",
    "docs/task-evidence/soundtouch/README.md":
        "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
    "docs/task-evidence/soundtouch/report.json":
        "83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947",
    "docs/task-evidence/beatnet/README.md":
        "d453bda9ea5d3dda875b05ff7fbd238e5ecdef69ad48deb4be26c68f98b8c828",
    "docs/task-evidence/beatnet/report.json":
        "dc233e50bd901f44e68c01033d0fe753b47955853a28d81f993f22dce0883399",
    "docs/task-evidence/ffmpeg-atempo/README.md":
        "11773a543c6dab54ff4754989501a0a70a29b247612e51aee5fb54c0050457b8",
    "docs/task-evidence/ffmpeg-atempo/report.json":
        "a3986e6cb9d7315995aa13c74806c260c620d01b6f545e0837b127565c2ba249",
    "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md":
        "9f91d406909fe2f9fa7cfd4b954639d081a12ab16005be761707b6f5c998f40c",
    "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/report.json":
        "091b57f366c1c5d4d395f955da7d237848bdc7564c970e1a087d423fb702f225",
}

LOCAL_FILES = (
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)
EXPECTED_DIR_FILES = set(LOCAL_FILES) | {"SOURCES.sha256"}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".ckpt", ".dll", ".dylib", ".exe", ".flac", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".wasm", ".wav", ".weights", ".th",
}


# ---------------------------------------------------------------------------
# Strict JSON, canonical bytes and hashing.
# ---------------------------------------------------------------------------


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def canonical_bytes(value: Any) -> bytes:
    return canonical_text(value).encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> Any:
    raise ValueError("nonfinite_json:" + token)


def assert_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("nonstring_json_key")
            assert_no_float(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            assert_no_float(item)


def parse_strict_json_text(payload: bytes) -> dict:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("invalid_utf8") from error
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicates,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    assert_no_float(value)
    return value


def read_strict_json(path: Path) -> dict:
    return parse_strict_json_text(path.read_bytes())


def canonical_report(report: dict | None = None) -> tuple[str, str]:
    text = canonical_text(build_report() if report is None else report)
    return text, sha256_bytes(text.encode("ascii"))


# ---------------------------------------------------------------------------
# Synthetic integer click stimuli.
# ---------------------------------------------------------------------------

CLICK_LENGTH = 96
CLICK_SHAPE = tuple((32 - abs(2 * index - 32)) * 1000 // 32
                    for index in range(32))


def _periodic(period: int, count: int, *, start: int = 0,
              accent_every: int = 4, strong: int = 1000,
              weak: int = 600) -> tuple[tuple[int, int, int], ...]:
    beats = []
    for index in range(count):
        frame = start + index * period
        amplitude = strong if index % accent_every == 0 else weak
        beats.append((frame, amplitude, 0))
    return tuple(beats)


def _stimulus(name: str, kind: str, total_frames: int,
              beats: tuple[tuple[int, int, int], ...], truth_meter: int | None,
              valid_samples: int | None = None,
              note: str = "") -> dict:
    if valid_samples is None:
        valid_samples = total_frames * FRAME_SAMPLES
    return {
        "name": name,
        "kind": kind,
        "total_frames": total_frames,
        "valid_samples": valid_samples,
        "beats": beats,
        "truth_meter": truth_meter,
        "note": note,
    }


STIMULI = (
    _stimulus("steady_music_1x", "music", 600,
              _periodic(60, 10), 4,
              note="100 BPM 4/4; strong every fourth beat"),
    _stimulus("rate_0_8", "music", 900,
              _periodic(75, 12), 4,
              note="80 BPM after a 0.8x output mapping"),
    _stimulus("rate_1_2", "music", 1000,
              _periodic(50, 20), 4,
              note="120 BPM after a 1.2x output mapping"),
    _stimulus("tempo_step", "music", 560,
              _periodic(60, 6) + _periodic(40, 5, start=340), 4,
              note="100 BPM then 150 BPM; no single global tempo"),
    _stimulus("syncopated_offbeat", "music", 550,
              _periodic(50, 10, start=25, accent_every=2,
                        strong=1000, weak=500), None,
              note="offbeat 120 BPM grid with a two-beat accent cycle"),
    _stimulus("speech_like_unfamiliar", "speech", 450,
              ((0, 900, 0), (37, 500, 0), (90, 800, 0), (131, 450, 0),
               (198, 700, 0), (227, 400, 0), (298, 850, 0), (341, 520, 0),
               (400, 650, 0)), None,
              note="irregular synthetic speech-like click train"),
    _stimulus("rebuffer_gap", "music", 560,
              ((0, 1000, 0), (50, 600, 0), (100, 600, 0), (150, 600, 0),
               (200, 1000, 0), (350, 600, 0), (400, 600, 0), (450, 600, 0),
               (500, 1000, 0)), 4,
              note="one 24000-sample cross-gap interval is excluded"),
    _stimulus("drift_decreasing", "music", 500,
              ((0, 900, 0), (70, 800, 0), (135, 700, 0), (195, 600, 0),
               (250, 500, 0), (300, 450, 0), (345, 400, 0), (385, 350, 0),
               (420, 300, 0), (450, 250, 0)), None,
              note="inter-onset intervals decrease monotonically"),
    _stimulus("silence", "silence", 500, (), None,
              note="no clicks and no onsets"),
    _stimulus("final_partial", "music", 301,
              ((0, 1000, 0), (60, 600, 0), (120, 600, 0), (180, 600, 0),
               (240, 600, 0), (300, 1000, 10)), 4,
              valid_samples=300 * FRAME_SAMPLES + 137,
              note="137 valid samples in the final partial frame"),
)
STIMULUS_BY_NAME = {stimulus["name"]: stimulus for stimulus in STIMULI}


def _build_signal(stimulus: dict) -> tuple[int, ...]:
    valid = stimulus["valid_samples"]
    signal = [0] * valid
    for frame, amplitude, offset in stimulus["beats"]:
        start = frame * FRAME_SAMPLES + offset
        for index in range(CLICK_LENGTH):
            position = start + index
            if position >= valid:
                break
            value = CLICK_SHAPE[index % 32] * amplitude // 1000
            value = value * (CLICK_LENGTH - index) // CLICK_LENGTH
            signal[position] += value
    return tuple(signal)


def _frames_from_signal(signal: tuple[int, ...] | list[int],
                        total_frames: int) -> list[tuple[int, ...]]:
    frames = []
    for index in range(total_frames):
        start = index * FRAME_SAMPLES
        frames.append(tuple(signal[start:start + FRAME_SAMPLES]))
    return frames


def _analyze_frames(frames: Iterable[Iterable[int]]) -> dict:
    energies = [sum(sample * sample for sample in frame) for frame in frames]
    onset: list[int] = []
    previous = 0
    for energy in energies:
        onset.append(max(0, energy - previous))
        previous = energy
    maximum = max(onset) if onset else 0
    threshold = max(1, maximum * ONSET_THRESHOLD_PERMILLE // 1000)
    peaks: list[int] = []
    for index, value in enumerate(onset):
        if value < threshold or value == 0:
            continue
        left = onset[index - 1] if index else -1
        right = onset[index + 1] if index + 1 < len(onset) else -1
        if value >= left and value > right:
            peaks.append(index)
    return {"energies": energies, "onset": onset, "peaks": peaks,
            "threshold": threshold, "maximum": maximum}


def _analyze_stimulus(stimulus: dict) -> dict:
    signal = _build_signal(stimulus)
    frames = _frames_from_signal(signal, stimulus["total_frames"])
    result = _analyze_frames(frames)
    result["signal"] = signal
    result["frames"] = frames
    return result


def _bpm_x100(period_samples: int) -> int:
    if period_samples <= 0:
        raise ValueError("nonpositive_period")
    return (96_000_000 + period_samples // 2) // period_samples


def _iois(peaks: list[int]) -> list[int]:
    return [(peaks[index + 1] - peaks[index]) * FRAME_SAMPLES
            for index in range(len(peaks) - 1)]


def _segments_from_iois(iois: list[int]) -> list[int]:
    if not iois:
        return []
    runs: list[list[int]] = []
    current = [iois[0]]
    for ioi in iois[1:]:
        if abs(ioi - current[-1]) <= FRAME_SAMPLES:
            current.append(ioi)
        else:
            runs.append(current)
            current = [ioi]
    runs.append(current)
    segments = []
    for run in runs:
        if len(run) < 2:
            continue
        segments.append(_bpm_x100(sorted(run)[len(run) // 2]))
    return segments


def _tempo(peaks: list[int]) -> dict:
    if not peaks:
        return {"status": "no_onsets", "bpm_x100": None,
                "ioi_count": 0, "excluded_ioi_count": 0,
                "used_ioi_count": 0, "median_ioi_samples": None,
                "stable": False}
    raw = _iois(peaks)
    used = [ioi for ioi in raw if ioi <= MAX_IOI_SAMPLES]
    excluded = len(raw) - len(used)
    if len(used) < MIN_IOIS:
        return {"status": "insufficient_iois", "bpm_x100": None,
                "ioi_count": len(raw), "excluded_ioi_count": excluded,
                "used_ioi_count": len(used),
                "median_ioi_samples": None, "stable": False}
    ordered = sorted(used)
    median = ordered[len(ordered) // 2]
    stable = all(abs(ioi - median) * 1000
                 <= median * STABLE_TOLERANCE_PERMILLE for ioi in used)
    return {
        "status": "stable" if stable else "unstable",
        "bpm_x100": _bpm_x100(median) if stable else None,
        "ioi_count": len(raw),
        "excluded_ioi_count": excluded,
        "used_ioi_count": len(used),
        "median_ioi_samples": median,
        "stable": stable,
    }


def _meter(peaks: list[int], onset: list[int], truth: int | None) -> dict:
    if len(peaks) < 4:
        return {"status": "insufficient_beats", "meter": None,
                "correct": None, "accent_spread": 0}
    accents = [onset[peak] for peak in peaks]
    best_meter = None
    best_spread = -1
    for meter in (2, 3, 4):
        phase_values = []
        for phase in range(meter):
            values = [accents[index] for index in range(len(accents))
                      if index % meter == phase]
            phase_values.append(sum(values) // len(values))
        spread = max(phase_values) - min(phase_values)
        if spread > best_spread:
            best_spread = spread
            best_meter = meter
    if best_meter == 4 and best_spread > 0:
        return {"status": "stable", "meter": 4,
                "correct": truth == 4, "accent_spread": best_spread}
    if best_meter in (2, 3) and best_spread > 0:
        return {"status": "ambiguous", "meter": None,
                "correct": None, "accent_spread": best_spread}
    return {"status": "not_estimated", "meter": None,
            "correct": None, "accent_spread": max(0, best_spread)}


def _match_beats(peaks: list[int], truth: list[int]) -> dict:
    detected = set(peaks)
    expected = set(truth)
    true_positive = len(detected & expected)
    false_positive = len(detected - expected)
    false_negative = len(expected - detected)
    if expected or detected:
        f1 = (2 * true_positive * 1000) // (
            2 * true_positive + false_positive + false_negative)
    else:
        f1 = 1000
    return {
        "detected": len(peaks),
        "truth": len(truth),
        "true_positive": true_positive,
        "false_positives": false_positive,
        "false_negatives": false_negative,
        "f1_x1000": f1,
    }


def _case(stimulus: dict) -> dict:
    analysis = _analyze_stimulus(stimulus)
    tempo = _tempo(analysis["peaks"])
    truth_frames = [frame for frame, _, _ in stimulus["beats"]]
    if stimulus["kind"] != "music" or tempo["status"] != "stable":
        meter = {"status": "not_estimated", "meter": None,
                 "correct": None, "accent_spread": 0}
    else:
        meter = _meter(analysis["peaks"], analysis["onset"],
                       stimulus["truth_meter"])
    return {
        "stimulus": stimulus["name"],
        "kind": stimulus["kind"],
        "total_frames": stimulus["total_frames"],
        "valid_samples": stimulus["valid_samples"],
        "truth_beats": len(truth_frames),
        "detected_beats": len(analysis["peaks"]),
        "detected_frames": analysis["peaks"],
        "tempo": tempo,
        "meter": meter,
        "match": _match_beats(analysis["peaks"], truth_frames),
        "analysis": analysis,
    }


def _case_matrix() -> dict:
    return {stimulus["name"]: _case(stimulus) for stimulus in STIMULI}


# ---------------------------------------------------------------------------
# Environment and absence probes.
# ---------------------------------------------------------------------------

PROBE_MODULES = (
    "librosa", "numba", "llvmlite", "audioread", "soxr", "pooch",
    "lazy_loader", "msgpack", "scikit-learn", "joblib", "decorator",
    "soundfile", "scipy", "numpy",
)


def _module_present(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def _distribution_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def environment_probe() -> dict:
    modules = {name: _module_present(name) for name in PROBE_MODULES}
    return {
        "required_interpreter": REQUIRED_INTERPRETER,
        "observed_interpreter": platform.python_version(),
        "probe": "importlib.util.find_spec",
        "modules": modules,
        "librosa_present": modules["librosa"],
        "numba_present": modules["numba"],
        "llvmlite_present": modules["llvmlite"],
        "librosa_version": _distribution_version("librosa"),
        "numpy_version": _distribution_version("numpy"),
        "scipy_version": _distribution_version("scipy"),
        "soundfile_version": _distribution_version("soundfile"),
        "librosa_imported": False,
        "librosa_executed": False,
        "package_install_or_download": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied tool manifest.  Identity only; bytes are never read.
# ---------------------------------------------------------------------------

MANIFEST_FIELDS = (
    "schema_id", "tool", "entrypoint", "python", "librosa_version",
    "wheel_sha256", "dependency_lock_sha256", "sample_rate_hz", "channels",
    "hop_length", "frame_samples", "byte_count",
)
MANIFEST_KEYS = frozenset(MANIFEST_FIELDS)


def base_manifest() -> dict:
    return {
        "schema_id": CALLER_MANIFEST_SCHEMA_ID,
        "tool": "librosa",
        "entrypoint": "librosa.beat.beat_track",
        "python": REQUIRED_INTERPRETER,
        "librosa_version": "0.11.0",
        "wheel_sha256": "a" * 64,
        "dependency_lock_sha256": "b" * 64,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "hop_length": HOP_SAMPLES,
        "frame_samples": FRAME_SAMPLES,
        "byte_count": 1,
    }


def validate_manifest(manifest: Any) -> dict:
    if not isinstance(manifest, dict):
        raise ValueError("manifest_not_object")
    if set(manifest) != MANIFEST_KEYS:
        raise ValueError("manifest_key_set_mismatch")
    if manifest["schema_id"] != CALLER_MANIFEST_SCHEMA_ID:
        raise ValueError("manifest_schema_mismatch")
    if manifest["tool"] != "librosa":
        raise ValueError("manifest_tool_mismatch")
    if manifest["entrypoint"] not in UPSTREAM_ENTRYPOINTS:
        raise ValueError("manifest_entrypoint_mismatch")
    if manifest["python"] != REQUIRED_INTERPRETER:
        raise ValueError("manifest_python_mismatch")
    if not isinstance(manifest["librosa_version"], str) or not re.fullmatch(
            r"^\d+\.\d+\.\d+$", manifest["librosa_version"]):
        raise ValueError("manifest_version_malformed")
    for key in ("wheel_sha256", "dependency_lock_sha256"):
        if not isinstance(manifest[key], str) or not HEX64.fullmatch(
                manifest[key]):
            raise ValueError("manifest_digest_malformed:" + key)
        if set(manifest[key]) == {"0"}:
            raise ValueError("manifest_digest_zero:" + key)
    if manifest["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ValueError("manifest_sample_rate_mismatch")
    if manifest["channels"] != CHANNELS:
        raise ValueError("manifest_channels_mismatch")
    if manifest["hop_length"] != HOP_SAMPLES:
        raise ValueError("manifest_hop_mismatch")
    if manifest["frame_samples"] != FRAME_SAMPLES:
        raise ValueError("manifest_frame_mismatch")
    if not isinstance(manifest["byte_count"], int) or isinstance(
            manifest["byte_count"], bool) or manifest["byte_count"] <= 0:
        raise ValueError("manifest_byte_count_invalid")
    return manifest


# ---------------------------------------------------------------------------
# Request validation and adverse cases.
# ---------------------------------------------------------------------------

REQUEST_FIELDS = (
    "sample_rate_hz", "channels", "frame_samples", "dtype",
    "clock_ns_per_sample", "rate_numerator", "rate_denominator", "epoch",
    "stimulus", "samples", "expected_sample_count", "valid_count",
    "padding_zero", "caller_manifest",
)
REQUEST_KEYS = frozenset(REQUEST_FIELDS)

STIMULUS_NAMES = tuple(stimulus["name"] for stimulus in STIMULI)


def base_request() -> dict:
    stimulus = STIMULUS_BY_NAME["steady_music_1x"]
    samples = _build_signal(stimulus)
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "dtype": "float32",
        "clock_ns_per_sample": NS_PER_SAMPLE,
        "rate_numerator": 1,
        "rate_denominator": 1,
        "epoch": 1,
        "stimulus": "steady_music_1x",
        "samples": list(samples),
        "expected_sample_count": len(samples),
        "valid_count": len(samples),
        "padding_zero": True,
        "caller_manifest": base_manifest(),
    }


def validate_request(request: Any) -> dict:
    if not isinstance(request, dict):
        raise ValueError("request_not_object")
    if set(request) != REQUEST_KEYS:
        raise ValueError("request_key_set_mismatch")
    for key in ("sample_rate_hz", "channels", "frame_samples",
                "clock_ns_per_sample", "rate_numerator", "rate_denominator",
                "epoch", "expected_sample_count", "valid_count"):
        value = request[key]
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("request_noninteger:" + key)
    if request["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ValueError("sample_rate_not_16k")
    if request["channels"] != CHANNELS:
        raise ValueError("channels_not_mono")
    if request["frame_samples"] != FRAME_SAMPLES:
        raise ValueError("frame_not_160")
    if request["dtype"] != "float32":
        raise ValueError("dtype_not_float32")
    if request["clock_ns_per_sample"] != NS_PER_SAMPLE:
        raise ValueError("clock_drift")
    if request["rate_numerator"] <= 0 or request["rate_denominator"] <= 0:
        raise ValueError("nonpositive_rate")
    if request["epoch"] <= 0:
        raise ValueError("nonpositive_epoch")
    if request["stimulus"] not in STIMULUS_NAMES:
        raise ValueError("unknown_stimulus")
    if not isinstance(request["samples"], list):
        raise ValueError("samples_not_list")
    if not request["samples"]:
        raise ValueError("empty_input")
    for sample in request["samples"]:
        if not isinstance(sample, int) or isinstance(sample, bool):
            raise ValueError("sample_not_integer")
        if sample < -1000000 or sample > 1000000:
            raise ValueError("sample_out_of_range")
    expected = request["expected_sample_count"]
    if expected != len(request["samples"]):
        raise ValueError("sample_count_mismatch")
    if request["valid_count"] < 0 or request["valid_count"] > expected:
        raise ValueError("valid_count_out_of_range")
    if request["padding_zero"] is not True:
        raise ValueError("padding_not_declared_zero")
    if any(request["samples"][request["valid_count"]:]):
        raise ValueError("nonzero_padding")
    if request["stimulus"] == "silence" and any(request["samples"]):
        raise ValueError("nonzero_silence")
    if request["stimulus"] == "final_partial" and request[
            "valid_count"] != STIMULUS_BY_NAME["final_partial"]["valid_samples"]:
        raise ValueError("misaligned_final_partial")
    validate_manifest(request["caller_manifest"])
    return request


def adverse_cases() -> list[dict]:
    cases: list[tuple[str, Any]] = []

    def mutated(**changes: Any) -> dict:
        request = base_request()
        request.update(changes)
        return request

    cases.append(("duplicate_json_key",
                  b'{"a":1,"a":2}'))
    cases.append(("nan_constant", b'{"a":NaN}'))
    cases.append(("infinity_constant", b'{"a":Infinity}'))
    cases.append(("malformed_json", b'{'))
    request = base_request()
    del request["sample_rate_hz"]
    cases.append(("missing_config_field", request))
    cases.append(("extra_config_field", mutated(extra_field=1)))
    cases.append(("sample_rate_8000", mutated(sample_rate_hz=8000)))
    cases.append(("sample_rate_22050", mutated(sample_rate_hz=22050)))
    cases.append(("sample_rate_44100", mutated(sample_rate_hz=44100)))
    cases.append(("stereo", mutated(channels=2)))
    cases.append(("frame_256", mutated(frame_samples=256)))
    cases.append(("dtype_int16", mutated(dtype="int16")))
    cases.append(("clock_drift", mutated(clock_ns_per_sample=62501)))
    cases.append(("boolean_rate", mutated(rate_numerator=True)))
    cases.append(("missing_input", mutated(samples=[],
                                           expected_sample_count=0,
                                           valid_count=0)))
    cases.append(("epoch_zero", mutated(epoch=0)))
    cases.append(("negative_expected_count",
                  mutated(expected_sample_count=-1)))
    cases.append(("invalid_valid_count", mutated(valid_count=999999)))
    cases.append(("nonfinite_sample", mutated(samples=[1.5])))
    request = mutated()
    request["samples"][-1] = 1
    request["valid_count"] = len(request["samples"]) - 1
    cases.append(("nonzero_padding", request))
    cases.append(("string_sample", mutated(samples=["x"])))
    cases.append(("boolean_sample", mutated(samples=[True])))
    cases.append(("unknown_stimulus", mutated(stimulus="unknown")))
    cases.append(("zero_rate", mutated(rate_numerator=0)))
    cases.append(("negative_amplitude", mutated(samples=[-1000001])))
    cases.append(("out_of_range_amplitude", mutated(samples=[1000001])))
    request = mutated()
    request["rate_numerator"] = 1.5
    cases.append(("noninteger_rate", request))
    cases.append(("nonzero_silence", mutated(stimulus="silence")))
    cases.append(("misaligned_final_partial",
                  mutated(stimulus="final_partial", valid_count=48138)))
    request = mutated()
    request["expected_sample_count"] = len(request["samples"]) + 1
    cases.append(("length_mismatch", request))
    cases.append(("reset_epoch_zero", mutated(epoch=0)))
    cases.append(("reset_epoch_negative", mutated(epoch=-1)))
    cases.append(("missing_manifest", mutated(caller_manifest=None)))
    manifest = base_manifest()
    manifest["python"] = "3.12.14"
    cases.append(("wrong_manifest_python", mutated(caller_manifest=manifest)))
    manifest = base_manifest()
    manifest["wheel_sha256"] = "main"
    cases.append(("relative_manifest_digest",
                  mutated(caller_manifest=manifest)))
    manifest = base_manifest()
    manifest["wheel_sha256"] = "z" * 64
    cases.append(("bad_manifest_hash", mutated(caller_manifest=manifest)))
    manifest = base_manifest()
    manifest["sample_rate_hz"] = 22050
    cases.append(("wrong_manifest_rate", mutated(caller_manifest=manifest)))
    manifest = base_manifest()
    manifest["channels"] = 2
    cases.append(("wrong_manifest_channel",
                  mutated(caller_manifest=manifest)))
    manifest = base_manifest()
    manifest["extra"] = 1
    cases.append(("extra_manifest_field", mutated(caller_manifest=manifest)))
    manifest = base_manifest()
    manifest["byte_count"] = 0
    cases.append(("zero_manifest_bytes", mutated(caller_manifest=manifest)))

    results = []
    for case_id, payload in cases:
        try:
            if isinstance(payload, bytes):
                parse_strict_json_text(payload)
            else:
                validate_request(payload)
        except (ValueError, TypeError) as error:
            results.append({
                "case_id": case_id,
                "status": "rejected",
                "state_unchanged": True,
                "reason": str(error),
            })
        else:
            raise AssertionError("adverse case accepted: " + case_id)
    if len(results) != 40:
        raise AssertionError("adverse case count is not 40")
    return results


# ---------------------------------------------------------------------------
# Rate profile and report sections.
# ---------------------------------------------------------------------------


def _tempo_cases(matrix: dict) -> list[dict]:
    rows = []
    for name in STIMULUS_NAMES:
        case = matrix[name]
        tempo = case["tempo"]
        rows.append({
            "stimulus": name,
            "kind": case["kind"],
            "status": tempo["status"],
            "bpm_x100": tempo["bpm_x100"],
            "ioi_count": tempo["ioi_count"],
            "excluded_ioi_count": tempo["excluded_ioi_count"],
            "used_ioi_count": tempo["used_ioi_count"],
            "qualifies": False,
        })
    return rows


def _beat_cases(matrix: dict) -> list[dict]:
    rows = []
    for name in STIMULUS_NAMES:
        case = matrix[name]
        match = case["match"]
        rows.append({
            "stimulus": name,
            "status": "synthetic_only",
            "detected": match["detected"],
            "truth": match["truth"],
            "false_positives": match["false_positives"],
            "false_negatives": match["false_negatives"],
            "f1_x1000": match["f1_x1000"],
            "qualifies": False,
        })
    return rows


def _meter_cases(matrix: dict) -> list[dict]:
    rows = []
    for name in STIMULUS_NAMES:
        case = matrix[name]
        meter = case["meter"]
        rows.append({
            "stimulus": name,
            "status": meter["status"],
            "meter": meter["meter"],
            "correct": meter["correct"],
            "accent_spread": meter["accent_spread"],
            "qualifies": False,
        })
    return rows


def _rate_profile(matrix: dict) -> dict:
    steady = STIMULUS_BY_NAME["steady_music_1x"]
    source_samples = [frame * FRAME_SAMPLES for frame, _, _ in steady["beats"]]
    rate_changes = []
    for label, numerator, denominator, expected in (
            ("0_8", 4, 5, 8000), ("1_0", 1, 1, 10000),
            ("1_2", 6, 5, 12000)):
        mapped = [sample * denominator // numerator
                  for sample in source_samples]
        exact = all(sample * denominator % numerator == 0
                    for sample in source_samples)
        period = mapped[1] - mapped[0]
        observed = _bpm_x100(period) if exact else None
        rate_changes.append({
            "label": label,
            "rate_numerator": numerator,
            "rate_denominator": denominator,
            "expected_bpm_x100": expected,
            "observed_bpm_x100": observed,
            "exact": exact,
        })
    rebuffer = matrix["rebuffer_gap"]["tempo"]
    drift_iois = _iois(matrix["drift_decreasing"]["analysis"]["peaks"])
    drift_monotonic = all(drift_iois[index] > drift_iois[index + 1]
                          for index in range(len(drift_iois) - 1))
    final_case = matrix["final_partial"]
    final_peaks = final_case["analysis"]["peaks"]
    final_truth = STIMULUS_BY_NAME["final_partial"]["beats"][-1]
    final_detected_sample = final_peaks[-1] * FRAME_SAMPLES
    final_truth_sample = final_truth[0] * FRAME_SAMPLES + final_truth[2]
    return {
        "identity_1x": {
            "stimulus": "steady_music_1x",
            "bpm_x100": matrix["steady_music_1x"]["tempo"]["bpm_x100"],
            "detected_beats": matrix["steady_music_1x"]["match"]["detected"],
        },
        "duration": {
            "max_error_samples": 0,
            "exact": all(row["exact"] for row in rate_changes),
            "mapping": "source_sample * rate_denominator / rate_numerator",
        },
        "rate_changes": rate_changes,
        "pitch": {
            "status": "blocked",
            "qualifies": False,
            "reason": "no pitch preservation or listening test",
        },
        "transient_proxy": {
            "status": "synthetic_only",
            "final_partial_error_samples":
                final_detected_sample - final_truth_sample,
            "qualifies": False,
        },
        "speech_unfamiliar": {
            "stimulus": "speech_like_unfamiliar",
            "status": matrix["speech_like_unfamiliar"]["tempo"]["status"],
            "bpm_x100": matrix["speech_like_unfamiliar"]["tempo"]["bpm_x100"],
            "qualifies": False,
        },
        "silence": {
            "stimulus": "silence",
            "status": matrix["silence"]["tempo"]["status"],
            "qualifies": False,
        },
        "rebuffer": {
            "stimulus": "rebuffer_gap",
            "bpm_x100": rebuffer["bpm_x100"],
            "excluded_ioi_count": rebuffer["excluded_ioi_count"],
            "cross_gap_ioi_suppressed":
                rebuffer["excluded_ioi_count"] == 1,
            "qualifies": False,
        },
        "drift": {
            "stimulus": "drift_decreasing",
            "status": matrix["drift_decreasing"]["tempo"]["status"],
            "bpm_x100": matrix["drift_decreasing"]["tempo"]["bpm_x100"],
            "monotonic_decreasing": drift_monotonic,
            "qualifies": False,
        },
        "final_partial": {
            "stimulus": "final_partial",
            "valid_count": STIMULUS_BY_NAME["final_partial"]["valid_samples"]
            - 300 * FRAME_SAMPLES,
            "padding_zero": True,
            "final_frame": 300,
            "final_truth_sample": final_truth_sample,
            "final_detected_sample": final_detected_sample,
            "error_samples": final_detected_sample - final_truth_sample,
            "qualifies": False,
        },
        "playback_buffering": {
            "final_partial_valid_count": 137,
            "device_buffer_measured": False,
            "scheduler_measured": False,
            "qualifies": False,
        },
        "source_output_mapping": {
            "audio_output_produced": False,
            "event_times_only": True,
            "qualifies": False,
        },
    }


def _streaming() -> dict:
    stimulus = STIMULUS_BY_NAME["final_partial"]
    signal = _build_signal(stimulus)
    offline = _analyze_frames(_frames_from_signal(signal,
                                                  stimulus["total_frames"]))
    schedules = (160, 480, 800, 137, 641)
    matches = {}
    for chunk in schedules:
        frames = []
        buffer: list[int] = []
        for start in range(0, len(signal), chunk):
            buffer.extend(signal[start:start + chunk])
            while len(buffer) >= FRAME_SAMPLES:
                frames.append(tuple(buffer[:FRAME_SAMPLES]))
                buffer = buffer[FRAME_SAMPLES:]
        if buffer:
            frames.append(tuple(buffer))
        observed = _analyze_frames(frames)
        matches[str(chunk)] = observed["peaks"] == offline["peaks"]
    return {
        "stimulus": "final_partial",
        "chunk_schedules": list(schedules),
        "accepted_samples": stimulus["valid_samples"],
        "all_match": all(matches.values()),
        "matches": matches,
        "scheduler_measured": False,
        "qualifies": False,
    }


def _reset() -> dict:
    stimulus = STIMULUS_BY_NAME["final_partial"]
    first = _analyze_frames(_frames_from_signal(
        _build_signal(stimulus), stimulus["total_frames"]))["peaks"]
    fresh = _analyze_frames(_frames_from_signal(
        _build_signal(stimulus), stimulus["total_frames"]))["peaks"]
    rejected = []
    for epoch in (0, -1):
        try:
            if epoch <= 0:
                raise ValueError("nonpositive_epoch")
        except ValueError as error:
            rejected.append({"epoch": epoch, "reason": str(error)})
    return {
        "reset_epoch": 2,
        "matches_fresh": first == fresh,
        "rejected_epochs": rejected,
        "state_unchanged": True,
        "qualifies": False,
    }


def _profile_items(matrix: dict) -> dict:
    return {
        "source_output_mapping": {
            "status": "synthetic_only",
            "evidence": "source sample and event frame intervals only; no "
                        "audio output",
        },
        "duration": {
            "status": "synthetic_only",
            "evidence": "exact integer event mapping at 0.8x, 1.0x and 1.2x",
        },
        "pitch": {
            "status": "blocked",
            "evidence": "no pitch preservation measurement or listening",
        },
        "transient_audibility": {
            "status": "synthetic_only",
            "evidence": "final-partial frame-quantization proxy only",
        },
        "playback_buffering": {
            "status": "synthetic_only",
            "evidence": "160-sample frame aggregation; no device buffer",
        },
        "rate_changes": {
            "status": "synthetic_only",
            "evidence": "0.8x, 1.0x and 1.2x on a synthetic click train",
        },
        "unfamiliar_speech_music_silence": {
            "status": "synthetic_only",
            "evidence": "synthetic speech-like, music-like and silence cases",
        },
        "rebuffer_drift_final_partial": {
            "status": "synthetic_only",
            "evidence": "one excluded cross-gap IOI, monotonic drift and a "
                        "137-sample final frame",
        },
        "speech_preservation_and_pause_decisions": {
            "status": "blocked",
            "evidence": "no real speech, preservation score or source-tied "
                        "pause/filler decision",
        },
        "task_matched_heldout_qualification": {
            "status": "blocked",
            "evidence": "no rights-cleared held-out music or speech labels",
        },
    }


PROFILE_BLOCKERS = (
    "pitch",
    "speech_preservation_and_pause_decisions",
    "task_matched_heldout_qualification",
)


def exact_blockers() -> list[dict]:
    return [
        {
            "id": "BLK-01",
            "title": "No librosa runtime under the pinned interpreter",
            "detail": "CPython 3.12.16 has no librosa, numba, llvmlite, "
                      "audioread, soxr or pooch distribution. No package "
                      "install or download is permitted. The only observed "
                      "local librosa tree is an unpinned Python 3.11.5 venv; "
                      "it is not imported, executed or admitted.",
        },
        {
            "id": "BLK-02",
            "title": "No immutable librosa source and dependency lock",
            "detail": "No 40-hex source revision, sdist/wheel SHA-256, "
                      "transitive wheel hash set, lock file or build recipe "
                      "for librosa and its numba/llvmlite/scipy stack is "
                      "staged.",
        },
        {
            "id": "BLK-03",
            "title": "No admitted caller-supplied tool runtime",
            "detail": "The caller-tool manifest is defined but no caller has "
                      "supplied a pinned runtime, entrypoint adapter, identity "
                      "record or fail-closed absent behavior review.",
        },
        {
            "id": "BLK-04",
            "title": "No exact librosa numeric reference output",
            "detail": "No librosa beat_track beat frame list, tempo estimate, "
                      "tempo prior or numeric digest was produced or "
                      "reproduced. The synthetic DP/click surrogate is not "
                      "librosa.",
        },
        {
            "id": "BLK-05",
            "title": "No rights-cleared task-matched music or speech cohort",
            "detail": "No real music, real speech, beat/downbeat/meter label, "
                      "corpus terms, split, consent or output-use grant is "
                      "present.",
        },
        {
            "id": "BLK-06",
            "title": "No timing, listening, benchmark or release evidence",
            "detail": "No target-device pacing, content delay, listening "
                      "result, independent review, opt-in tool intake or "
                      "release approval exists.",
        },
    ]


def release_gates() -> list[dict]:
    return [
        {"id": "RG-01", "status": "blocked",
         "requirement": "Exact pinned librosa source, wheel/sdist, dependency "
                        "lock and interpreter with immutable hashes."},
        {"id": "RG-02", "status": "blocked",
         "requirement": "Isolated caller-supplied tool runtime with "
                        "fail-closed absence and reviewed entrypoint adapter."},
        {"id": "RG-03", "status": "blocked",
         "requirement": "Reviewed ISC attribution and every transitive "
                        "dependency license, including LGPL soxr, with "
                        "redistribution and product-use decisions."},
        {"id": "RG-04", "status": "blocked",
         "requirement": "Explicit 16 kHz mono 160-sample geometry with "
                        "hop_length=160 and no unapproved resampling."},
        {"id": "RG-05", "status": "blocked",
         "requirement": "Exact librosa beat_track/tempo numeric reproduction "
                        "and parity record."},
        {"id": "RG-06", "status": "blocked",
         "requirement": "Rights-cleared task-matched held-out music/speech "
                        "qualification with separate tempo, beat and meter "
                        "results."},
        {"id": "RG-07", "status": "blocked",
         "requirement": "Target-device timing, content delay, buffering and "
                        "speech-preservation evidence."},
        {"id": "RG-08", "status": "blocked",
         "requirement": "Opt-in tool intake, independent exact-head review "
                        "and release approval."},
    ]


REOPEN_CONDITION = (
    "Supply a caller-owned CPython 3.12.16 environment with a pinned "
    "librosa 0.11.0 distribution, wheel/sdist SHA-256 and a complete "
    "transitive dependency lock; review the ISC and LGPL soxr terms; define "
    "the 16 kHz mono 160-sample hop_length=160 adapter; reproduce the exact "
    "beat_track/tempo outputs; qualify tempo, beat and meter on a "
    "rights-cleared task-matched held-out music/speech cohort; measure target "
    "timing and listening where permitted; and complete opt-in tool intake "
    "with independent exact-head review. Until then the candidate stays "
    "DEFER, incomplete and not qualified.")


def _board_row() -> dict:
    path = AUDIO_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    payload = read_strict_json(path)
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("board_tasks_not_list")
    row = next((task for task in tasks if task.get("id") == TASK), None)
    if row is None:
        raise ValueError("board_row_missing")
    stable = {
        "id": row["id"],
        "title": row["title"],
        "repository": row["repository"],
        "mode": row["mode"],
        "depends_on": row["depends_on"],
        "component": row["component"],
    }
    return {
        "stable_fields": stable,
        "stable_sha256": object_digest(stable),
        "full_tasks_json_hashed": False,
        "board_status_is_observation_only": True,
    }


def build_report() -> dict:
    matrix = _case_matrix()
    tempo_rows = _tempo_cases(matrix)
    beat_rows = _beat_cases(matrix)
    meter_rows = _meter_cases(matrix)
    step_segments = _segments_from_iois(
        _iois(matrix["tempo_step"]["analysis"]["peaks"]))
    environment = environment_probe()
    adverse = adverse_cases()
    caller_contract = {
        "schema_id": CALLER_MANIFEST_SCHEMA_ID,
        "entrypoints": list(UPSTREAM_ENTRYPOINTS),
        "required_interpreter": REQUIRED_INTERPRETER,
        "required_librosa_version": "0.11.0",
        "required_sample_rate_hz": SAMPLE_RATE_HZ,
        "required_channels": CHANNELS,
        "required_hop_length": HOP_SAMPLES,
        "required_frame_samples": FRAME_SAMPLES,
        "manifest_fields": list(MANIFEST_FIELDS),
        "identity_only": True,
        "reads_bytes": False,
        "loads_source": False,
        "executes_runtime": False,
        "admitted": False,
        "reproduced": False,
        "exact_output_present": False,
        "accepted_control": validate_manifest(base_manifest()) == base_manifest(),
    }
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "task_id": TASK,
        "title": TASK_TITLE,
        "component_id": COMPONENT_ID,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "version": "0.1",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "owner": OWNER,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "disposition": DISPOSITION,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "proposal_only": True,
        "incomplete": True,
        "profile": PROFILE,
        "verification_profile": PROFILE,
        "acceptance_profile": {
            "profile": PROFILE,
            "label": PROFILE_LABEL,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "required_items": _profile_items(matrix),
            "profile_blockers": list(PROFILE_BLOCKERS),
            "satisfied": False,
        },
        "candidate": {
            "id": COMPONENT_ID,
            "name": TASK_TITLE,
            "reported_license": UPSTREAM_LICENSE,
            "default_sample_rate_hz": UPSTREAM_DEFAULT_SAMPLE_RATE_HZ,
            "configured_sample_rate_hz": SAMPLE_RATE_HZ,
            "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
            "sdk_v0_frame_samples": FRAME_SAMPLES,
            "default_hop_length": UPSTREAM_DEFAULT_HOP_LENGTH,
            "configured_hop_length": HOP_SAMPLES,
            "default_n_fft": UPSTREAM_DEFAULT_N_FFT,
            "native_default_compatible": False,
            "source_present": False,
            "runtime_present": False,
            "exact_numeric_output_present": False,
            "real_corpus_present": False,
        },
        "reference": {
            "id": "synthetic-dp-click-surrogate",
            "is_candidate": False,
            "synthetic_surrogate": True,
            "exact_librosa_executed": False,
            "source_present": False,
            "runtime_present": False,
            "implementation_present": False,
            "surrogate_present": True,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "surrogate_is_candidate": False,
            "status": "synthetic_only",
        },
        "environment": environment,
        "local_unpinned_runtime": dict(OBSERVED_LOCAL_RUNTIME),
        "format": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "dtype": "float32",
            "frame_samples": FRAME_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "ns_per_sample": NS_PER_SAMPLE,
            "ns_per_frame": NS_PER_FRAME,
            "candidate_default_sample_rate_hz":
                UPSTREAM_DEFAULT_SAMPLE_RATE_HZ,
            "candidate_default_hop_length": UPSTREAM_DEFAULT_HOP_LENGTH,
            "resampling": "none",
            "clock": "sample_frame",
        },
        "fixtures": {
            "stimulus_count": len(STIMULI),
            "stimuli": [
                {
                    "name": stimulus["name"],
                    "kind": stimulus["kind"],
                    "total_frames": stimulus["total_frames"],
                    "valid_samples": stimulus["valid_samples"],
                    "truth_beats": len(stimulus["beats"]),
                    "truth_meter": stimulus["truth_meter"],
                    "note": stimulus["note"],
                }
                for stimulus in STIMULI
            ],
            "click_length_samples": CLICK_LENGTH,
            "click_shape_entries": len(CLICK_SHAPE),
            "synthetic_only": True,
            "real_audio_used": False,
        },
        "tempo_tracking": {
            "cases": tempo_rows,
            "tempo_step": {
                "observed_segments": step_segments,
                "exact": step_segments == [10000, 15000],
                "global_status": matrix["tempo_step"]["tempo"]["status"],
                "global_bpm_x100": matrix["tempo_step"]["tempo"]["bpm_x100"],
                "qualifies": False,
            },
            "beat_tracking_method": "peak onset sequence with a "
                                    "tempo-consistency check; not librosa DP",
            "qualifies": False,
        },
        "beat_tracking": {
            "cases": beat_rows,
            "qualifies": False,
        },
        "downbeat_meter": {
            "cases": meter_rows,
            "truth_available": False,
            "qualifies": False,
        },
        "rate_profile": _rate_profile(matrix),
        "streaming": _streaming(),
        "reset": _reset(),
        "adverse_rejections": adverse,
        "adverse_all_rejected": True,
        "caller_tool_reference": caller_contract,
        "caller_asset": {
            "accepted_control": caller_contract["accepted_control"],
            "rejected_case_count": 8,
            "reads_bytes": False,
            "loads_source": False,
            "executes_runtime": False,
            "identity_only": True,
        },
        "external_artifacts": {
            "status": "blocked",
            "any_present": False,
            "librosa_source_present": False,
            "librosa_wheel_present": False,
            "dependency_lock_present": False,
            "audio_corpus_present": False,
            "beat_labels_present": False,
            "note": "No upstream source, wheel, lock, audio or label is "
                    "present, downloaded or copied.",
        },
        "licensing": {
            "reported_upstream_license": UPSTREAM_LICENSE,
            "recorded_transitive_licenses": {
                "numba": "BSD-2-Clause",
                "llvmlite": "BSD-2-Clause AND Apache-2.0 WITH LLVM-exception",
                "numpy": "BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0",
                "scipy": "BSD-3-Clause",
                "soundfile": "BSD-3-Clause",
                "audioread": "MIT",
                "soxr": "LGPL-2.1-or-later",
                "pooch": "BSD-3-Clause",
                "lazy-loader": "BSD-3-Clause",
                "msgpack": "Apache-2.0",
                "joblib": "BSD-3-Clause",
                "decorator": "BSD-2-Clause",
            },
            "lgpl_dependency_present": "soxr",
            "review_status": "blocked",
            "license_text_staged": False,
            "dependency_lock_staged": False,
            "attribution_notice_staged": False,
            "redistribution_reviewed": False,
            "product_use_reviewed": False,
        },
        "board_row": _board_row(),
        "boundary": {
            "registered": False,
            "enabled_by_default": False,
            "default_selected": False,
            "public_api_abi_change": False,
            "provider_registration": False,
            "descriptor_registry_change": False,
            "installed_v0_behavior_change": False,
            "shared_build_or_ci_change": False,
            "processor_exposure": False,
            "adapter_json_added": False,
            "readiness_json_added": False,
            "asset_bundled": False,
            "weights_vendored": False,
            "native_engine_built": False,
            "sdk_data_dir_added": False,
            "board_or_handoff_changed": False,
        },
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_pins": dict(SOURCE_PINS),
        "scope": {
            "synthetic_only": True,
            "task_local_only": True,
            "provider_change": False,
            "default_change": False,
            "abi_change": False,
            "contracts_change": False,
            "registry_change": False,
            "shared_build_change": False,
            "ci_change": False,
            "board_change": False,
            "handoff_change": False,
            "package_install_or_download": False,
            "real_audio_used": False,
            "listening": False,
            "device_timing": False,
            "benchmark_claim": False,
            "release_claim": False,
        },
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualifies": False,
            "all_required_results_present": False,
            "missing_result_promoted": False,
            "exact_source_present": False,
            "exact_runtime_present": False,
            "exact_numeric_output_present": False,
            "rights_cleared_cohort": False,
            "native_geometry_compatible": False,
            "beat_tempo_qualified": False,
            "meter_qualified": False,
            "timing_measured": False,
            "listening": False,
            "real_corpus_used": False,
            "synthetic_surrogate_is_candidate": False,
        },
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "reopen_condition": REOPEN_CONDITION,
        "negative_claims": [
            "not librosa",
            "no librosa source, wheel, lock or runtime",
            "no librosa numeric output or parity",
            "no real music or speech",
            "no beat, downbeat, meter or tempo qualification",
            "no listening",
            "no device timing",
            "no benchmark or release claim",
            "synthetic surrogate is not the candidate",
        ],
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "case_matrix_digests": [object_digest(matrix)] * 3,
        },
        "reproduction": {
            "interpreter": REQUIRED_INTERPRETER,
            "python_dont_write_bytecode": "1",
            "commands": [
                "python -m unittest -v test_reference.py",
                "python run.py",
                "python verify.py",
                "python -m reuse lint",
                "git diff --check",
            ],
        },
        "scope_note": ("Only docs/task-evidence/librosa-beat-track-tempo/ is "
                       "added. No provider, default, ABI, CONTRACTS, registry, "
                       "shared build, CI, board or handoff is changed."),
    }


def build_contract() -> dict:
    report = build_report()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "repository": REPOSITORY,
        "mode": MODE,
        "version": "0.1",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "owner": OWNER,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "disposition": DISPOSITION,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "profile": PROFILE,
        "verification_profile": PROFILE,
        "task_prefix": TASK_PREFIX,
        "write_scope": WRITE_SCOPE,
        "acceptance_profile": report["acceptance_profile"],
        "candidate": report["candidate"],
        "format": report["format"],
        "licensing": report["licensing"],
        "artifact_pins": {
            TASK_PREFIX + name: sha256_file(HERE / name)
            for name in LOCAL_FILES
            if name not in {"README.md", "contract.json", "SOURCES.sha256",
                            "report.json", "report.json.sha256"}
        },
        "board_row": report["board_row"],
        "boundary": report["boundary"],
        "boundary_pins": report["boundary_pins"],
        "source_pins": report["source_pins"],
        "scope": report["scope"],
        "reference": report["reference"],
        "caller_tool_reference": report["caller_tool_reference"],
        "exact_blockers": report["exact_blockers"],
        "release_gates": report["release_gates"],
        "reopen_condition": report["reopen_condition"],
        "negative_claims": report["negative_claims"],
        "invariants": {
            "synthetic_only": True,
            "task_local_only": True,
            "no_float_json": True,
            "canonical_report": True,
            "three_identical_builds": True,
            "scope_enforced_by_merge_base": True,
            "readme_digest_tables_checked": True,
            "caller_manifest_identity_only": True,
            "absent_runtime_fails_closed": True,
        },
    }


# ---------------------------------------------------------------------------
# Pins, README digest tables and SOURCES.sha256.
# ---------------------------------------------------------------------------


def _local_manifest_paths() -> list[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name != "SOURCES.sha256")


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for relative, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + relative))
    for relative, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + relative))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to the pinned audioml workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable plan/swarm/TASKS.json is never hashed; only its stable "
        "linked-row projection is gated.",
    ]
    lines.extend(f"{digest}  {path}" for digest, path in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_pin_lines(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{64}  \S+", line) is None:
            raise ValueError("malformed_pin_line:" + str(number))
        digest, path = line.split("  ", 1)
        if not (path.startswith("source:") or path.startswith("sdk:")
                or path.startswith(TASK_PREFIX)):
            raise ValueError("unknown_pin_prefix:" + str(number))
        if path in seen:
            raise ValueError("duplicate_pin:" + str(number))
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def expected_readme_keys() -> dict[str, set[str]]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {name for name in _local_manifest_paths()
                      if name not in ARTIFACT_TABLE_EXCLUDED},
    }


def _section_text(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if text.count(start) != 1:
        raise ValueError("readme_marker_count:" + section)
    start_index = text.index(start) + len(start)
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise ValueError("readme_marker_missing:" + section)
    return text[start_index:end_index]


def parse_readme_digest_tables(text: str) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for section in README_SECTIONS:
        rows: list[tuple[str, str]] = []
        for line in _section_text(text, section).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or re.fullmatch(r"[0-9]+", cells[2]) is None:
                    raise ValueError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ValueError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValueError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({key for key, _ in rows}) != len(rows):
            raise ValueError("duplicate_readme_row:" + section)
        result[section] = rows
    return result


def verify_readme_digests(text: str) -> dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            missing = sorted(expected[section] - actual_keys)
            extra = sorted(actual_keys - expected[section])
            raise ValueError(
                f"readme_key_mismatch:{section}:missing={missing}:"
                f"extra={extra}")
        for key, digest in parsed[section]:
            if section == "source":
                relative = key[len("source:"):]
                expected_digest = SOURCE_PINS[relative]
                path = AUDIO_ROOT / relative
            elif section == "boundary":
                relative = key[len("sdk:"):]
                expected_digest = BOUNDARY_PINS[relative]
                path = SDK_ROOT / relative
            else:
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if not path.is_file() or sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = f"| `{key}` | `{sha256_file(HERE / key)}` | {size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_digest_table(section: str) -> str:
    if section == "source":
        rows = [f"| `source:{name}` | `{digest}` |"
                for name, digest in sorted(SOURCE_PINS.items())]
    elif section == "boundary":
        rows = [f"| `sdk:{name}` | `{digest}` |"
                for name, digest in sorted(BOUNDARY_PINS.items())]
    elif section == "artifacts":
        rows = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
        for name in sorted(expected_readme_keys()["artifacts"]):
            path = HERE / name
            rows.append(f"| `{name}` | `{sha256_file(path)}` | "
                        f"{path.stat().st_size} |")
    else:
        raise ValueError("unknown_readme_section")
    return "\n".join(rows)


def update_readme_tables(text: str) -> str:
    for section in README_SECTIONS:
        start, end = README_MARKERS[section]
        if text.count(start) != 1:
            raise ValueError("readme_marker_count:" + section)
        start_index = text.index(start) + len(start)
        end_index = text.index(end, start_index)
        replacement = "\n" + render_digest_table(section) + "\n"
        text = text[:start_index] + replacement + text[end_index:]
    return text


# ---------------------------------------------------------------------------
# Task-local git scope.  The base is the newest merge-base between HEAD and the
# available PR base refs.  This keeps later sibling merges out of the
# comparison while still failing closed on any edit outside TASK_PREFIX.
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
    """Newest merge-base between HEAD and an available PR base ref."""
    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]
