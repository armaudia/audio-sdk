# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local evidence for the AdaptDRC / SSDRC feasibility lane.

The local record is a public-product locator in ``plan/INVENTORY.json`` and a
research note that explicitly says its compressor is **not** AdaptDRC/SSDRC.
No official source archive, implementation, algorithm parameters, licence,
runtime, reference output vector, rights-cleared corpus or target-device
evidence exists locally.

This module therefore emits an explicit ``DEFER`` / ``incomplete`` /
``not_qualified`` blocker package.  It runs a deterministic, stdlib-only
three-band adaptive DRC *local approximation* so that receiver-side geometry,
finite output, zero content delay, state reset, strict JSON and adverse/
missing/invalid/nonfinite rejection can be checked mechanically.  The local
approximation is not AdaptDRC, not SSDRC, has no official algorithm, no model,
no runtime and no real audio, and no observation from it may qualify the
candidate.

Nothing here downloads, copies, imports, loads or executes AdaptDRC/SSDRC, a
runtime, a corpus or a device clock.  It does not register a provider, change
installed v0, a descriptor, a registry, a default, a shared build or CI, and it
makes no listening, timing, benchmark or release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]

TASK = "SDK-ADAPTDRC-SSDRC"
TITLE = "AdaptDRC / SSDRC"
SLUG = "adaptdrc-ssdrc"
COMPONENT = "adaptdrc-ssdrc"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "3b581c09115f36408f77bf6a5c8ebd7389b9fb7b"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-ADAPTDRC-SSDRC"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-ADAPTDRC-SSDRC"
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "dsp"
STATUS = "proposal_only_blocked_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "published_control_and_rights_admission"

PRODUCT_PAGE = "https://www.idmt.fraunhofer.de/en/institute/projects-products/adaptdrc.html"
SSDRC_LITERATURE_LOCATOR = (
    "https://www.isca-archive.org/interspeech_2013/godoy13c_interspeech.html")
# The local record establishes none of the values below.  They remain null.
UPSTREAM_COMMIT: str | None = None
UPSTREAM_VERSION: str | None = None
UPSTREAM_LICENSE: str | None = None
UPSTREAM_LICENSE_STATUS = "not_established"
UPSTREAM_PARAMETERS: str | None = None
UPSTREAM_PARAMETERS_STATUS = "not_recorded"
UPSTREAM_REFERENCE_OUTPUT: str | None = None
UPSTREAM_REFERENCE_OUTPUT_STATUS = "not_recorded"
UPSTREAM_RUNTIME: str | None = None
UPSTREAM_RUNTIME_STATUS = "not_recorded"
UPSTREAM_GEOMETRY_STATUS = "unverified"

SOURCE_PATH = "data/sources/adaptdrc-ssdrc"
LICENSE_PATH = "data/licenses/adaptdrc-ssdrc"
RUNTIME_ENV_PATH = "data/envs/adaptdrc-ssdrc"
REFERENCE_OUTPUT_PATH = "data/reference/adaptdrc-ssdrc"
CONFIGURATION_PATH = "data/config/adaptdrc-ssdrc"

LISTENING_RESEARCH_PATH = "research/listening_intelligibility_20261028.md"
LEVEL_TONE_RESEARCH_PATH = "research/level_tone_control_20261028.md"
INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"
VERIFICATION_PATH = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
SDK_PLAN_PATH = "audio-benchmark-platform/plan/audio-sdk/README.md"

BOARD_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-EVIDENCE",
        "SDK-FND-PROVIDER",
    ],
    "id": TASK,
    "mode": "feasibility",
    "repository": "audio-sdk",
    "title": TITLE,
}
BOARD_ROW_STABLE_SHA256 = (
    "cdea755aff0a80858e653273520dfeaa4bb4efc994c743fb1f387a356cf10939")

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
TOTAL_FRAMES = 400
TOTAL_SAMPLES = TOTAL_FRAMES * FRAME_SAMPLES
CONTENT_DELAY_SAMPLES = 0
PEAK_CEILING = 0.95
BAND_EDGES_HZ = (400, 2000)
ATTACK_MS = 5.0
RELEASE_MS = 120.0
THRESHOLD_DBFS = -24.0
RATIO = 3.0
MAX_GAIN_DB = 12.0
MIN_GAIN_DB = -24.0
STATIC_GAIN_DB = 6.0
FIXED_TILT_DB = (0.0, 3.0, 6.0)
LOCAL_TILT_DB = (0.0, 2.0, 4.0)

SINE64: Tuple[int, ...] = (
    0, 3212, 6393, 9512, 12539, 15446, 18204, 20787,
    23170, 25329, 27245, 28898, 30273, 31356, 32137, 32609,
    32767, 32609, 32137, 31356, 30273, 28898, 27245, 25329,
    23170, 20787, 18204, 15446, 12539, 9512, 6393, 3212,
    0, -3212, -6393, -9512, -12539, -15446, -18204, -20787,
    -23170, -25329, -27245, -28898, -30273, -31356, -32137, -32609,
    -32767, -32609, -32137, -31356, -30273, -28898, -27245, -25329,
    -23170, -20787, -18204, -15446, -12539, -9512, -6393, -3212,
)

SEGMENT_FRAMES = 25
SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "silence-a", "start_frame": 0, "end_frame": 25, "kind": "silence"},
    {"id": "quiet-speech", "start_frame": 25, "end_frame": 75,
     "kind": "speech", "steps": (1, 2, 3), "amplitude": 900},
    {"id": "speech-transient", "start_frame": 75, "end_frame": 125,
     "kind": "speech", "steps": (2, 3, 5), "amplitude": 1400,
     "click_period": 2048, "click_amplitude": 7000},
    {"id": "level-step-up", "start_frame": 125, "end_frame": 175,
     "kind": "speech", "steps": (2, 3, 5), "amplitude": 5000},
    {"id": "noisy-speech", "start_frame": 175, "end_frame": 225,
     "kind": "speech", "steps": (3, 4, 6), "amplitude": 1800,
     "noise_gain": 2},
    {"id": "sweep", "start_frame": 225, "end_frame": 275,
     "kind": "sweep", "amplitude": 3000},
    {"id": "impulse-train", "start_frame": 275, "end_frame": 325,
     "kind": "impulse", "click_period": 1600, "click_amplitude": 9000},
    {"id": "silence-tail", "start_frame": 325, "end_frame": 400,
     "kind": "silence"},
)

VALID_MODES = (
    "identity",
    "static_gain",
    "fixed_tilt",
    "full_band_compressor",
    "local_approximation",
)

CONFIG: Dict[str, Any] = {
    "algorithm": "local_surrogate_not_adaptdrc",
    "adaptation": "bounded_three_band",
    "attack_ms": ATTACK_MS,
    "channels": CHANNELS,
    "default_enabled": False,
    "epoch": 0,
    "frame_samples": FRAME_SAMPLES,
    "input_format": "float32",
    "max_gain_db": MAX_GAIN_DB,
    "mode": "local_approximation",
    "model_used": False,
    "output_peak_ceiling": PEAK_CEILING,
    "ratio": RATIO,
    "real_runtime": False,
    "release_ms": RELEASE_MS,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "session_id": "adaptdrc-ssdrc-local-surrogate",
    "surrogate": True,
    "threshold_dbfs": THRESHOLD_DBFS,
}

REQUIRED_CONFIG_KEYS = set(CONFIG)

REQUIRED_ASSET_FIELDS = {
    "algorithm_id",
    "algorithm_version",
    "algorithmic_latency_samples",
    "channels",
    "configuration_path",
    "configuration_sha256",
    "frame_samples",
    "license_path",
    "license_sha256",
    "output_power_constraint_db",
    "qualification_authority",
    "reference_output_path",
    "reference_output_sha256",
    "runtime_path",
    "runtime_sha256",
    "sample_rate_hz",
    "source_archive_path",
    "source_archive_sha256",
    "source_commit",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-qualified-artifact/0.1",
    "official_artifact_admitted_here": False,
    "present_behavior": (
        "validate_hash_geometry_and_artifact_shape_only; never load, import or "
        "execute; official identity still requires independent rights review"),
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "source archive, licence, runtime, configuration and reference-output "
        "paths are caller-owned absolute paths that exist",
        "SHA-256 of the source archive, licence, runtime, configuration and "
        "reference output match the manifest",
        "source_commit is a 40-hex revision but is not admitted as official "
        "because no official revision was established",
        "geometry is 16000 Hz, mono, float32 and 160 samples with nonnegative "
        "latency",
        "algorithm_id is adaptdrc-ssdrc and algorithm_version is nonempty",
        "output_power_constraint_db is finite and nonpositive",
        "a hash-matched caller placeholder is never accepted as an official "
        "AdaptDRC/SSDRC artifact",
        "no download, copy, build, import, load or execution occurs here",
    ],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, indent=2)
    return (text + "\n").encode("utf-8")


def strict_loads(text: str) -> Any:
    def pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise ValueError("non_finite:" + value)

    result = json.loads(text, object_pairs_hook=pairs, parse_constant=reject)
    if not isinstance(result, dict):
        raise ValueError("root_not_object")
    return result


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(item) for item in value.values())
    if isinstance(value, list):
        return any(has_negative_zero(item) for item in value)
    return False


def _metric(value: float | None) -> float | None:
    if value is None:
        return None
    if not math.isfinite(value):
        raise ValueError("metric_nonfinite")
    rounded = round(value, 9)
    return 0.0 if rounded == 0.0 else rounded


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(float(value)))


def workspace_root() -> Path:
    override = os.environ.get("SOURCE_ROOT")
    if override:
        return Path(override).resolve()
    for parent in HERE.parents:
        if (parent / "adapters").is_dir() and \
                (parent / "audio-benchmark-platform").is_dir():
            return parent
    raise ValueError("workspace_root_not_found")


def resolve_source_path(name: str) -> Path:
    return workspace_root() / name


def board_row_digest() -> str:
    raw = json.dumps(BOARD_ROW_STABLE_FIELDS, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return sha256(raw)


def _clip16(value: int) -> int:
    if value < -32768:
        return -32768
    if value > 32767:
        return 32767
    return int(value)


def _ramp(index: int, length: int, ramp: int = 80) -> int:
    if length <= 1:
        return ramp
    return max(0, min(index, length - 1 - index, ramp))


def _clean_track() -> List[int]:
    data = [0] * TOTAL_SAMPLES
    for segment in SEGMENTS:
        start = segment["start_frame"] * FRAME_SAMPLES
        end = segment["end_frame"] * FRAME_SAMPLES
        length = end - start
        kind = segment["kind"]
        if kind == "silence":
            continue
        if kind == "impulse":
            period = int(segment["click_period"])
            amplitude = int(segment["click_amplitude"])
            for index in range(0, length, period):
                data[start + index] = _clip16(amplitude)
            continue
        amplitude = int(segment["amplitude"])
        steps = tuple(int(step) for step in segment.get("steps", (1,)))
        phases = [0] * len(steps)
        weights = (8, 4, 2, 1)
        for index in range(length):
            envelope = _ramp(index, length)
            if kind == "sweep":
                step = 2 + (index * 20) // max(1, length)
                value = (SINE64[index * step % 64] * amplitude) // 32767
            else:
                total = 0
                for position, step in enumerate(steps):
                    phases[position] = (phases[position] + step) % 64
                    total += (SINE64[phases[position]] * amplitude *
                              weights[position]) // (32767 * 15)
                value = total
            value = (value * envelope) // max(1, 80)
            click_period = segment.get("click_period")
            if click_period and index % int(click_period) == 0:
                value += int(segment["click_amplitude"])
            data[start + index] = _clip16(data[start + index] + value)
    return data


def _noise_track() -> List[int]:
    data = [0] * TOTAL_SAMPLES
    state = 0x13579BDF
    for segment in SEGMENTS:
        if "noise_gain" not in segment:
            continue
        start = segment["start_frame"] * FRAME_SAMPLES
        end = segment["end_frame"] * FRAME_SAMPLES
        gain = int(segment["noise_gain"])
        for index in range(start, end):
            state = (1103515245 * state + 12345) & 0x7FFFFFFF
            noise = ((state >> 8) & 0xFFFF) - 32768
            data[index] = _clip16(noise * gain)
    return data


def build_fixture() -> Dict[str, Any]:
    clean = _clean_track()
    noise = _noise_track()
    mixed = [_clip16(clean[index] + noise[index])
             for index in range(TOTAL_SAMPLES)]
    return {"clean": clean, "noise": noise, "mix": mixed}


FIXTURE_COMPONENTS = build_fixture()


def as_float(values: Sequence[int]) -> List[float]:
    return [value / 32768.0 for value in values]


def component_digests(components: Dict[str, Any]) -> Dict[str, str]:
    return {
        name: sha256(b"".join(
            (int(value) & 0xFFFF).to_bytes(2, "little")
            for value in values))
        for name, values in components.items()
    }


FIXTURE_DIGESTS = component_digests(FIXTURE_COMPONENTS)


def fixture_spec() -> Dict[str, Any]:
    return {
        "channels": CHANNELS,
        "components": ["clean", "noise", "mix"],
        "frame_samples": FRAME_SAMPLES,
        "generator": (
            "fixed 64-entry integer sine table, integer phases, integer "
            "amplitude envelopes and a 31-bit LCG; int16 quantised"),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "segments": [
            {key: value for key, value in segment.items()}
            for segment in SEGMENTS
        ],
        "total_frames": TOTAL_FRAMES,
        "total_samples": TOTAL_SAMPLES,
    }


FIXTURE_SPEC_DIGEST = sha256(canonical_bytes(fixture_spec()))


LOW_A = math.exp(-2.0 * math.pi * BAND_EDGES_HZ[0] / SAMPLE_RATE_HZ)
MID_A = math.exp(-2.0 * math.pi * BAND_EDGES_HZ[1] / SAMPLE_RATE_HZ)
ATTACK_COEFF = 1.0 - math.exp(-1.0 / (ATTACK_MS * 0.001 * SAMPLE_RATE_HZ))
RELEASE_COEFF = 1.0 - math.exp(-1.0 / (RELEASE_MS * 0.001 * SAMPLE_RATE_HZ))


def _clip_db(value: float) -> float:
    return max(MIN_GAIN_DB, min(MAX_GAIN_DB, value))


def _db_to_lin(value: float) -> float:
    return 10.0 ** (value / 20.0)


def _gain_db(envelope: float) -> float:
    level_db = 20.0 * math.log10(max(envelope, 1.0e-9))
    if level_db <= THRESHOLD_DBFS:
        return 0.0
    return _clip_db((level_db - THRESHOLD_DBFS) * (1.0 / RATIO - 1.0))


def _env_step(envelope: float, value: float) -> float:
    coefficient = ATTACK_COEFF if value > envelope else RELEASE_COEFF
    return envelope + coefficient * (value - envelope)


class _Processor:
    """Deterministic causal local approximation; not AdaptDRC or SSDRC."""

    def __init__(self, mode: str) -> None:
        if mode not in VALID_MODES:
            raise ValueError("unknown_mode")
        self.mode = mode
        self.low = 0.0
        self.mid = 0.0
        self.env_low = 0.0
        self.env_mid = 0.0
        self.env_high = 0.0
        self.env_full = 0.0
        self.balance = 0.0
        self.clipped = 0

    def _split(self, sample: float) -> Tuple[float, float, float]:
        self.low = LOW_A * self.low + (1.0 - LOW_A) * sample
        rest = sample - self.low
        self.mid = MID_A * self.mid + (1.0 - MID_A) * rest
        high = rest - self.mid
        return self.low, self.mid, high

    def _guard(self, value: float) -> float:
        if value > PEAK_CEILING:
            self.clipped += 1
            return PEAK_CEILING
        if value < -PEAK_CEILING:
            self.clipped += 1
            return -PEAK_CEILING
        return value

    def process_sample(self, sample: float) -> float:
        if self.mode == "identity":
            return sample
        if self.mode == "static_gain":
            return self._guard(sample * _db_to_lin(STATIC_GAIN_DB))
        low, mid, high = self._split(sample)
        if self.mode == "fixed_tilt":
            output = (low * _db_to_lin(FIXED_TILT_DB[0]) +
                      mid * _db_to_lin(FIXED_TILT_DB[1]) +
                      high * _db_to_lin(FIXED_TILT_DB[2]))
            return self._guard(output)
        if self.mode == "full_band_compressor":
            self.env_full = _env_step(self.env_full, abs(sample))
            return self._guard(sample * _db_to_lin(_gain_db(self.env_full)))
        self.env_low = _env_step(self.env_low, abs(low))
        self.env_mid = _env_step(self.env_mid, abs(mid))
        self.env_high = _env_step(self.env_high, abs(high))
        total = self.env_low + self.env_mid + self.env_high + 1.0e-12
        balance = self.env_high / total
        self.balance = 0.995 * self.balance + 0.005 * balance
        adaptive_high = max(-3.0, min(6.0, 6.0 * (0.20 - self.balance) / 0.20))
        output = (
            low * _db_to_lin(_gain_db(self.env_low) + LOCAL_TILT_DB[0]) +
            mid * _db_to_lin(_gain_db(self.env_mid) + LOCAL_TILT_DB[1]) +
            high * _db_to_lin(_gain_db(self.env_high) + LOCAL_TILT_DB[2] +
                              adaptive_high))
        return self._guard(output)

    def snapshot(self) -> Dict[str, float]:
        return {
            "balance": round(self.balance, 12),
            "env_full": round(self.env_full, 12),
            "env_high": round(self.env_high, 12),
            "env_low": round(self.env_low, 12),
            "env_mid": round(self.env_mid, 12),
            "low": round(self.low, 12),
            "mid": round(self.mid, 12),
        }


def validate_frame(frame: Any, final: bool = False) -> List[float]:
    if not isinstance(frame, list):
        raise ValueError("frame_not_list")
    count = len(frame)
    if final:
        if count < 1 or count > FRAME_SAMPLES:
            raise ValueError("bad_final_length")
    elif count != FRAME_SAMPLES:
        raise ValueError("bad_frame_length")
    result: List[float] = []
    for sample in frame:
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise ValueError("bad_sample_type")
        value = float(sample)
        if not math.isfinite(value):
            raise ValueError("nonfinite_sample")
        if value < -1.0 or value > 1.0:
            raise ValueError("sample_out_of_range")
        result.append(value)
    return result


def validate_config(config: Any) -> None:
    if not isinstance(config, dict):
        raise ValueError("config_not_object")
    if set(config) != REQUIRED_CONFIG_KEYS:
        raise ValueError("config_key_set")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ValueError("sample_rate")
    if config["channels"] != CHANNELS:
        raise ValueError("channels")
    if config["frame_samples"] != FRAME_SAMPLES:
        raise ValueError("frame_samples")
    if config["input_format"] != "float32":
        raise ValueError("input_format")
    if config["algorithm"] != "local_surrogate_not_adaptdrc":
        raise ValueError("algorithm")
    if config["adaptation"] != "bounded_three_band":
        raise ValueError("adaptation")
    if config["mode"] not in VALID_MODES:
        raise ValueError("mode")
    if not _is_number(config["threshold_dbfs"]) or \
            not -60.0 <= float(config["threshold_dbfs"]) <= 0.0:
        raise ValueError("threshold")
    if not _is_number(config["ratio"]) or not 1.0 <= float(config["ratio"]) <= 20.0:
        raise ValueError("ratio")
    if not _is_number(config["attack_ms"]) or \
            not 0.1 <= float(config["attack_ms"]) <= 500.0:
        raise ValueError("attack")
    if not _is_number(config["release_ms"]) or \
            not 1.0 <= float(config["release_ms"]) <= 5000.0:
        raise ValueError("release")
    if not _is_number(config["max_gain_db"]) or \
            not 0.0 <= float(config["max_gain_db"]) <= 24.0:
        raise ValueError("max_gain")
    if not _is_number(config["output_peak_ceiling"]) or \
            not 0.0 < float(config["output_peak_ceiling"]) <= 1.0:
        raise ValueError("ceiling")
    for key in ("default_enabled", "model_used", "real_runtime"):
        if config[key] is not False:
            raise ValueError(key)
    if config["surrogate"] is not True:
        raise ValueError("surrogate")
    session_id = config["session_id"]
    if not isinstance(session_id, str) or not session_id or \
            re.fullmatch(r"[\x21-\x7e]{1,96}", session_id) is None:
        raise ValueError("session_id")
    if not _is_int(config["epoch"]) or config["epoch"] < 0:
        raise ValueError("epoch")


class Session:
    def __init__(self, mode: str = "local_approximation", epoch: int = 0,
                 first_input_sample: int = 0) -> None:
        if mode not in VALID_MODES:
            raise ValueError("unknown_mode")
        if not _is_int(epoch) or epoch < 0:
            raise ValueError("bad_epoch")
        if not _is_int(first_input_sample) or first_input_sample < 0:
            raise ValueError("bad_first_input_sample")
        self.mode = mode
        self.epoch = epoch
        self.next_input_sample = first_input_sample
        self.accepted_samples = 0
        self.rejected_frames = 0
        self.processor = _Processor(mode)
        self.final = False

    def process(self, frame: Any, final: bool = False) -> Dict[str, Any]:
        if self.final:
            self.rejected_frames += 1
            raise ValueError("process_after_final")
        try:
            samples = validate_frame(frame, final)
        except ValueError:
            self.rejected_frames += 1
            raise
        padded = samples + [0.0] * (FRAME_SAMPLES - len(samples))
        output = [self.processor.process_sample(sample) for sample in padded]
        if any(not math.isfinite(value) for value in output):
            raise ValueError("nonfinite_output")
        self.accepted_samples += len(samples)
        self.next_input_sample += len(samples)
        if final:
            self.final = True
        return {
            "epoch": self.epoch,
            "flags": 2 if final else 0,
            "output": output,
            "produced_count": FRAME_SAMPLES,
            "source_first_sample": self.next_input_sample - FRAME_SAMPLES,
            "valid_count": len(samples),
        }

    def reset(self, epoch: int, first_input_sample: int) -> None:
        if not _is_int(epoch) or epoch <= self.epoch:
            raise ValueError("epoch_not_increasing")
        if not _is_int(first_input_sample) or first_input_sample < 0:
            raise ValueError("bad_first_input_sample")
        self.epoch = epoch
        self.next_input_sample = first_input_sample
        self.accepted_samples = 0
        self.rejected_frames = 0
        self.processor = _Processor(self.mode)
        self.final = False

    def state_digest(self) -> str:
        payload = {
            "accepted_samples": self.accepted_samples,
            "epoch": self.epoch,
            "final": self.final,
            "mode": self.mode,
            "next_input_sample": self.next_input_sample,
            "processor": self.processor.snapshot(),
        }
        return sha256(canonical_bytes(payload))


def run_samples(samples: Sequence[float], mode: str = "local_approximation",
                chunk: int = FRAME_SAMPLES) -> List[float]:
    session = Session(mode)
    output: List[float] = []
    index = 0
    while index < len(samples):
        take = min(chunk, len(samples) - index)
        final = index + take == len(samples) and take < FRAME_SAMPLES
        result = session.process(list(samples[index:index + take]), final=final)
        output.extend(result["output"][:result["valid_count"]])
        index += take
    return output


def run_chunked(samples: Sequence[float], sizes: Sequence[int],
                mode: str = "local_approximation") -> List[float]:
    session = Session(mode)
    output: List[float] = []
    buffer: List[float] = []
    index = 0
    for size in sizes:
        if index >= len(samples):
            break
        buffer.extend(samples[index:index + size])
        index += min(size, len(samples) - index)
        while len(buffer) >= FRAME_SAMPLES:
            result = session.process(buffer[:FRAME_SAMPLES])
            buffer = buffer[FRAME_SAMPLES:]
            output.extend(result["output"][:result["valid_count"]])
    if index < len(samples):
        buffer.extend(samples[index:])
    while len(buffer) >= FRAME_SAMPLES:
        result = session.process(buffer[:FRAME_SAMPLES])
        buffer = buffer[FRAME_SAMPLES:]
        output.extend(result["output"][:result["valid_count"]])
    if buffer:
        result = session.process(buffer, final=True)
        output.extend(result["output"][:result["valid_count"]])
    return output


def _rms(samples: Sequence[float]) -> float:
    if not samples:
        return 0.0
    return math.sqrt(sum(value * value for value in samples) / len(samples))


def _rms_db(samples: Sequence[float]) -> float:
    return 20.0 * math.log10(max(_rms(samples), 1.0e-12))


def tone_samples(frequency_hz: int, level_dbfs: float,
                 seconds: float = 1.0) -> List[float]:
    step = frequency_hz * 64 // SAMPLE_RATE_HZ
    if step < 1 or step > 32:
        raise ValueError("tone_frequency")
    amplitude = int(round(32767 * (10.0 ** (level_dbfs / 20.0))))
    count = int(SAMPLE_RATE_HZ * seconds)
    return [SINE64[index * step % 64] * amplitude / 32767.0 / 32768.0
            for index in range(count)]


def measure_tone_gain(mode: str, frequency_hz: int, level_dbfs: float) -> float:
    source = tone_samples(frequency_hz, level_dbfs)
    output = run_samples(source, mode)
    start = len(source) // 2
    input_rms = _rms(source[start:])
    output_rms = _rms(output[start:])
    return _metric(20.0 * math.log10(max(output_rms, 1.0e-12) /
                                     max(input_rms, 1.0e-12))) or 0.0


def level_transfer(mode: str) -> Dict[str, Any]:
    levels = [-30.0, -24.0, -18.0, -12.0, -6.0]
    gains = [measure_tone_gain(mode, 1000, level) for level in levels]
    output_levels = [level + gain for level, gain in zip(levels, gains)]
    mean_x = sum(levels) / len(levels)
    mean_y = sum(output_levels) / len(output_levels)
    numerator = sum((x - mean_x) * (y - mean_y)
                    for x, y in zip(levels, output_levels))
    denominator = sum((x - mean_x) ** 2 for x in levels)
    slope = numerator / denominator if denominator else 1.0
    return {
        "gain_db": [_metric(value) for value in gains],
        "input_dbfs": levels,
        "output_dbfs": [_metric(value) for value in output_levels],
        "slope_db_per_db": _metric(slope),
    }


def measure_step(mode: str, rising: bool) -> Dict[str, Any]:
    quiet = tone_samples(1000, -30.0, 0.5)
    loud = tone_samples(1000, -6.0, 0.5)
    source = quiet + loud if rising else loud + quiet
    output = run_samples(source, mode)
    step_index = len(quiet)

    def window_gain_db(start: int) -> float:
        count = 80
        input_window = source[start:start + count]
        output_window = output[start:start + count]
        return 20.0 * math.log10(max(_rms(output_window), 1.0e-12) /
                                 max(_rms(input_window), 1.0e-12))

    before = window_gain_db(max(0, step_index - 400))
    after = window_gain_db(len(source) - 400)
    transition = None
    if abs(after - before) <= 0.01:
        transition = 0.0
    else:
        for start in range(step_index, len(source) - 80, 40):
            if abs(window_gain_db(start) - after) <= 3.0:
                transition = (start + 80 - step_index) * 1000.0 / SAMPLE_RATE_HZ
                break
    return {
        "gain_after_db": _metric(after),
        "gain_before_db": _metric(before),
        "transition_ms": _metric(transition or 0.0),
    }


def measure_mode(mode: str) -> Dict[str, Any]:
    source = as_float(FIXTURE_COMPONENTS["mix"])
    output = run_samples(source, mode)
    clipped = 0 if mode == "identity" else sum(
        1 for value in output if abs(value) >= PEAK_CEILING - 1.0e-12)
    silence_input = source[:4000]
    silence_output = output[:4000]
    transfer = level_transfer(mode)
    tones = {
        str(frequency): measure_tone_gain(mode, frequency, -24.0)
        for frequency in (250, 500, 1000, 2000, 4000, 6000)
    }
    return {
        "clipped_output_samples": clipped,
        "crest_factor_out_db": _metric(
            20.0 * math.log10(max(max(abs(value) for value in output), 1.0e-12) /
                              max(_rms(output), 1.0e-12))),
        "gain_db": _metric(_rms_db(output) - _rms_db(source)),
        "level_transfer": transfer,
        "max_abs_output": _metric(max(abs(value) for value in output)),
        "nonfinite_output_samples": sum(
            1 for value in output if not math.isfinite(value)),
        "rms_in_dbfs": _metric(_rms_db(source)),
        "rms_out_dbfs": _metric(_rms_db(output)),
        "silence_exact_zero": all(value == 0.0 for value in silence_input) and
                              all(value == 0.0 for value in silence_output),
        "step_attack": measure_step(mode, True),
        "step_release": measure_step(mode, False),
        "tone_gain_db": tones,
    }


def impulse_control() -> Dict[str, Any]:
    source = [0.0] * 8000
    source[2000] = 0.25
    output = run_samples(source, "local_approximation")
    peak_index = max(range(len(output)), key=lambda index: abs(output[index]))
    return {
        "declared_delay_samples": CONTENT_DELAY_SAMPLES,
        "expected_output_index": 2000 + CONTENT_DELAY_SAMPLES,
        "observed_peak_index": peak_index,
        "peak_finite": math.isfinite(output[peak_index]),
    }


def silence_control() -> Dict[str, Any]:
    output = run_samples([0.0] * 512, "local_approximation")
    return {
        "exact_zero": all(value == 0.0 for value in output),
        "finite": all(math.isfinite(value) for value in output),
    }


def streaming_parity_control() -> Dict[str, Any]:
    source = as_float(FIXTURE_COMPONENTS["mix"][:4000])
    offline = run_samples(source, "local_approximation")
    sizes = [160, 137, 641, 320, 1000, 73, 211, 160]
    streamed = run_chunked(source, sizes, "local_approximation")
    return {
        "all_identical": offline == streamed,
        "chunk_sizes": sizes,
        "sample_count": len(source),
    }


def reset_control() -> Dict[str, Any]:
    source = as_float(FIXTURE_COMPONENTS["mix"][:1600])
    session = Session("local_approximation", epoch=0)
    for index in range(0, len(source), FRAME_SAMPLES):
        session.process(source[index:index + FRAME_SAMPLES])
    session.reset(1, 0)
    reset_output: List[float] = []
    for index in range(0, len(source), FRAME_SAMPLES):
        result = session.process(source[index:index + FRAME_SAMPLES])
        reset_output.extend(result["output"])
    fresh = Session("local_approximation", epoch=1)
    fresh_output: List[float] = []
    for index in range(0, len(source), FRAME_SAMPLES):
        result = fresh.process(source[index:index + FRAME_SAMPLES])
        fresh_output.extend(result["output"])
    epoch_zero_rejected = False
    try:
        session.reset(1, 0)
    except ValueError:
        epoch_zero_rejected = True
    negative_rejected = False
    try:
        fresh.reset(-1, 0)
    except ValueError:
        negative_rejected = True
    return {
        "epoch_zero_rejected": epoch_zero_rejected,
        "fresh_matches_reset": reset_output == fresh_output,
        "higher_epoch_accepted": session.epoch == 1,
        "negative_epoch_rejected": negative_rejected,
    }


def nonfinite_control() -> Dict[str, Any]:
    session = Session("local_approximation")
    result = session.process([0.0] * FRAME_SAMPLES)
    before_digest = session.state_digest()
    before_counter = session.accepted_samples
    rejected = 0
    for bad in (float("nan"), float("inf"), float("-inf")):
        frame = [0.0] * FRAME_SAMPLES
        frame[17] = bad
        try:
            session.process(frame)
        except ValueError:
            rejected += 1
    after_digest = session.state_digest()
    after_counter = session.accepted_samples
    return {
        "accepted_counter_unchanged": before_counter == after_counter,
        "counted_as_silence": False,
        "nonfinite_rejected": rejected,
        "state_digest_unchanged": before_digest == after_digest,
        "valid_frame_produced": result["produced_count"] == FRAME_SAMPLES,
    }


def config_adverse_control() -> Dict[str, Any]:
    patches = {
        "adaptation_unbounded": {"adaptation": "unbounded"},
        "algorithm_official": {"algorithm": "adaptdrc"},
        "attack_zero": {"attack_ms": 0.0},
        "bool_epoch": {"epoch": True},
        "channels_stereo": {"channels": 2},
        "default_enabled": {"default_enabled": True},
        "empty_session": {"session_id": ""},
        "extra_key": {"extra": 1},
        "frame_320": {"frame_samples": 320},
        "input_int16": {"input_format": "int16"},
        "max_gain_excess": {"max_gain_db": 40.0},
        "model_used": {"model_used": True},
        "negative_epoch": {"epoch": -1},
        "output_int16": {"input_format": "int16"},
        "ratio_inf": {"ratio": float("inf")},
        "ratio_low": {"ratio": 0.5},
        "real_runtime": {"real_runtime": True},
        "release_zero": {"release_ms": 0.0},
        "sample_rate_48k": {"sample_rate_hz": 48000},
        "surrogate_false": {"surrogate": False},
        "threshold_nan": {"threshold_dbfs": float("nan")},
        "threshold_positive": {"threshold_dbfs": 3.0},
        "unknown_mode": {"mode": "adaptdrc"},
    }
    rejected = 0
    for patch in patches.values():
        config = dict(CONFIG)
        config.update(patch)
        try:
            validate_config(config)
        except ValueError:
            rejected += 1
    validate_config(dict(CONFIG))
    return {
        "accepted_baseline": True,
        "case_count": len(patches),
        "rejected_all": rejected == len(patches),
    }


def frame_adverse_control() -> Dict[str, Any]:
    cases = {
        "bool_sample": [True] * FRAME_SAMPLES,
        "empty": [],
        "empty_final": ("empty", True),
        "final_zero_length": ("zero", True),
        "infinity": [0.0] * 17 + [float("inf")] + [0.0] * 142,
        "long_final": [0.0] * 161,
        "long_nonfinal": [0.0] * 161,
        "nan": [0.0] * 17 + [float("nan")] + [0.0] * 142,
        "negative_infinity": [0.0] * 17 + [float("-inf")] + [0.0] * 142,
        "nested": [0.0] * 17 + [[1.0]] + [0.0] * 142,
        "none": [0.0] * 17 + [None] + [0.0] * 142,
        "out_of_range": [0.0] * 17 + [1.5] + [0.0] * 142,
        "short_nonfinal": [0.0] * 159,
        "string_outer": "[0.0]",
        "string_sample": [0.0] * 17 + ["0.0"] + [0.0] * 142,
        "zero_length": [],
    }
    rejected = 0
    for value in cases.values():
        if isinstance(value, tuple):
            frame, final = value[0], value[1]
        else:
            frame, final = value, False
        try:
            validate_frame(frame, final=final)
        except ValueError:
            rejected += 1
    return {
        "case_count": len(cases),
        "rejected_all": rejected == len(cases),
    }


def _asset_manifest(root: Path) -> Dict[str, Any]:
    paths = {
        "source_archive_path": root / "source.tar",
        "license_path": root / "LICENSE.txt",
        "runtime_path": root / "runtime.bin",
        "configuration_path": root / "config.json",
        "reference_output_path": root / "output.f32",
    }
    for name, path in paths.items():
        path.write_bytes(("caller-owned-placeholder:" + name).encode("ascii"))
    manifest: Dict[str, Any] = {
        "algorithm_id": "adaptdrc-ssdrc",
        "algorithm_version": "caller-declared-v0",
        "algorithmic_latency_samples": 0,
        "channels": CHANNELS,
        "configuration_path": str(paths["configuration_path"]),
        "configuration_sha256": sha256_file(paths["configuration_path"]),
        "frame_samples": FRAME_SAMPLES,
        "license_path": str(paths["license_path"]),
        "license_sha256": sha256_file(paths["license_path"]),
        "output_power_constraint_db": 0.0,
        "qualification_authority": "caller-owned-independent-review",
        "reference_output_path": str(paths["reference_output_path"]),
        "reference_output_sha256": sha256_file(paths["reference_output_path"]),
        "runtime_path": str(paths["runtime_path"]),
        "runtime_sha256": sha256_file(paths["runtime_path"]),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "source_archive_path": str(paths["source_archive_path"]),
        "source_archive_sha256": sha256_file(paths["source_archive_path"]),
        "source_commit": "a" * 40,
    }
    return manifest


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest_not_object")
    if set(manifest) != REQUIRED_ASSET_FIELDS:
        raise ValueError("manifest_key_set")
    for field in ("source_archive_path", "license_path", "runtime_path",
                  "configuration_path", "reference_output_path"):
        value = manifest[field]
        if not isinstance(value, str) or not value:
            raise ValueError("bad_path:" + field)
        path = Path(value)
        if not path.is_absolute() or not path.is_file():
            raise ValueError("missing_or_relative_path:" + field)
    for hash_field, path_field in (
            ("source_archive_sha256", "source_archive_path"),
            ("license_sha256", "license_path"),
            ("runtime_sha256", "runtime_path"),
            ("configuration_sha256", "configuration_path"),
            ("reference_output_sha256", "reference_output_path")):
        digest = manifest[hash_field]
        if not isinstance(digest, str) or \
                re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError("bad_hash:" + hash_field)
        if sha256_file(Path(manifest[path_field])) != digest:
            raise ValueError("hash_mismatch:" + hash_field)
    if not isinstance(manifest["source_commit"], str) or \
            re.fullmatch(r"[0-9a-f]{40}", manifest["source_commit"]) is None:
        raise ValueError("bad_commit")
    if manifest["algorithm_id"] != "adaptdrc-ssdrc":
        raise ValueError("algorithm_id")
    if not isinstance(manifest["algorithm_version"], str) or \
            not manifest["algorithm_version"]:
        raise ValueError("algorithm_version")
    if not _is_int(manifest["sample_rate_hz"]) or \
            manifest["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ValueError("sample_rate")
    if not _is_int(manifest["channels"]) or manifest["channels"] != CHANNELS:
        raise ValueError("channels")
    if not _is_int(manifest["frame_samples"]) or \
            manifest["frame_samples"] != FRAME_SAMPLES:
        raise ValueError("frame_samples")
    if not _is_int(manifest["algorithmic_latency_samples"]) or \
            not 0 <= manifest["algorithmic_latency_samples"] <= SAMPLE_RATE_HZ:
        raise ValueError("latency")
    if not _is_number(manifest["output_power_constraint_db"]) or \
            float(manifest["output_power_constraint_db"]) > 0.0:
        raise ValueError("power_constraint")
    if not isinstance(manifest["qualification_authority"], str) or \
            not manifest["qualification_authority"]:
        raise ValueError("authority")
    return {
        "executed": False,
        "hashed_here": True,
        "loaded": False,
        "official_identity": False,
        "valid": True,
    }


def pinned_asset_identity(manifest: Any) -> Dict[str, Any]:
    validate_caller_asset(manifest)
    return {
        "admitted": False,
        "reason": "official_artifact_identity_not_established",
    }


def asset_controls() -> Dict[str, Any]:
    rejected = 0
    cases = 0
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        manifest = _asset_manifest(root)
        valid = validate_caller_asset(manifest)
        pinned = pinned_asset_identity(manifest)
        patches: Dict[str, Any] = {
            "absent_source": {"source_archive_path": str(root / "absent.tar")},
            "bad_algorithm": {"algorithm_id": "adaptdrc"},
            "bad_hash": {"source_archive_sha256": "0" * 64},
            "bad_version": {"algorithm_version": ""},
            "bool_latency": {"algorithmic_latency_samples": True},
            "extra_field": {"extra": 1},
            "latency_negative": {"algorithmic_latency_samples": -1},
            "missing_field": {"qualification_authority": None},
            "negative_commit": {"source_commit": "g" * 40},
            "power_positive": {"output_power_constraint_db": 3.0},
            "relative_path": {"runtime_path": "runtime.bin"},
            "short_commit": {"source_commit": "a" * 39},
            "stereo": {"channels": 2},
            "zero_frame": {"frame_samples": 0},
            "zero_rate": {"sample_rate_hz": 0},
        }
        cases = len(patches)
        for patch in patches.values():
            candidate = dict(manifest)
            candidate.update(patch)
            try:
                validate_caller_asset(candidate)
            except ValueError:
                rejected += 1
    return {
        "case_count": cases,
        "pinned_identity_admitted": pinned["admitted"],
        "rejected_all": rejected == cases,
        "valid_manifest_accepted": valid["valid"] is True,
        "valid_manifest_executed": valid["executed"],
        "valid_manifest_loaded": valid["loaded"],
    }


EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "official_source_and_license_absent",
        "requirement": (
            "Supply the exact AdaptDRC/SSDRC implementation at an immutable "
            "source revision, with a reviewed licence, notice bundle and "
            "written product, redistribution and derivative-output terms, "
            "verified locally without a network download."),
        "state": (
            "No official source archive, implementation, checkout, licence or "
            "terms exist at data/sources/adaptdrc-ssdrc or "
            "data/licenses/adaptdrc-ssdrc. The local inventory records only a "
            "public Fraunhofer product-page locator; the pinned research note "
            "explicitly says its compressor is not AdaptDRC/SSDRC."),
    },
    {
        "id": "published_algorithm_and_parameters_absent",
        "requirement": (
            "Supply the exact published algorithm identity, filterbank, band "
            "edges, thresholds, ratios, attack/release, adaptation policy, "
            "output-power constraint and configuration digest."),
        "state": (
            "No exact algorithm, parameter set, configuration file or version "
            "is recorded. The public locator and the SSDRC literature locator "
            "are descriptive only; nothing was downloaded, reconstructed or "
            "substituted."),
    },
    {
        "id": "runtime_and_reference_output_absent",
        "requirement": (
            "Admit a locked, hash-pinned runtime with exact dependency "
            "versions and approved exact-runtime output vectors for byte-level "
            "parity."),
        "state": (
            "No environment exists at data/envs/adaptdrc-ssdrc and no reference "
            "output exists at data/reference/adaptdrc-ssdrc. No import, "
            "inference or parity run was attempted."),
    },
    {
        "id": "geometry_and_content_delay_unverified",
        "requirement": (
            "Pin the exact sample rate, channels, frame/hop, buffering/content "
            "delay, loudness normalization and output-power constraint, then "
            "reproduce them on one declared streaming path."),
        "state": (
            "The local record records no sample rate, frame, hop, latency, "
            "loudness normalization or output-power constraint. This package's "
            "16 kHz mono float32 160-sample zero-delay harness is a probe-only "
            "local approximation, not the official geometry."),
    },
    {
        "id": "rights_cleared_cohort_absent",
        "requirement": (
            "Supply a rights-cleared target-speech and listener-side masker "
            "cohort, hearing-profile/listening protocol and explicit output-use "
            "permissions."),
        "state": (
            "No cohort, consent, masker recording, hearing-profile data or "
            "listening protocol exists for this task. No real corpus or "
            "listener is used here."),
    },
    {
        "id": "independent_qualification_absent",
        "requirement": (
            "Score independent intelligibility/quality and output-power "
            "controls, measure target-device timing, and complete an "
            "OFF-by-default opt-in provider intake with independent review."),
        "state": (
            "No independent score, listening result, target-device timing, "
            "provider intake, descriptor review or release approval exists. "
            "Surrogate observations do not qualify the candidate."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_source_revision_and_license",
     "Immutable official source revision, reviewed licence, notice bundle and "
     "clean caller-owned checkout verified locally without a download."),
    ("published_algorithm_and_parameter_identity",
     "Exact published algorithm, version, filterbank, band edges, thresholds, "
     "ratios, time constants and adaptation policy are pinned and reproduced."),
    ("pinned_runtime_and_reference_output",
     "Locked offline runtime with exact dependency versions, install/import "
     "digest and approved exact-runtime reference output vectors."),
    ("receiver_side_geometry_and_content_delay",
     "Exact rate, channels, frame/hop, buffering/content delay, loudness "
     "normalization and output-power constraint are pinned and reproduced."),
    ("fixed_dsp_and_published_control_separation",
     "Fixed DSP controls and published AdaptDRC/SSDRC controls are measured "
     "separately from the local approximation, with no pooled claim."),
    ("rights_cleared_listening_and_masker_cohort",
     "Rights-cleared target speech, listener-side maskers, hearing profiles, "
     "consent and output-use permissions are frozen."),
    ("independent_quality_timing_and_power",
     "Independent intelligibility/quality scoring, output-power constraints, "
     "target-device timing and adverse/missing/nonfinite controls."),
    ("opt_in_provider_intake_and_default_review",
     "OFF-by-default opt-in provider intake, descriptor review, exact-head "
     "review and explicit public default/release approval."),
)

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "onnxruntime_invoked": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "readiness_json_added": False,
    "registered": False,
    "registry_or_default_change": False,
    "runtime_invoked": False,
    "sdk_data_dir_added": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "benchmark_run": False,
    "device_timing_measured": False,
    "downloaded": False,
    "implementation_added": False,
    "listening_performed": False,
    "network_used": False,
    "provider_registered": False,
    "public_abi_changed": False,
    "real_assets_used": False,
    "registry_or_default_changed": False,
    "release_claim": False,
    "runtime_executed": False,
    "shared_build_or_ci_changed": False,
    "source_imported": False,
    "task_local_only": True,
    "weights_loaded": False,
    "write_scope": TASK_PREFIX + " only",
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No AdaptDRC/SSDRC source, implementation, algorithm parameter set, "
    "runtime call or reference output was produced.",
    "No intelligibility, quality, listening, timing, benchmark or release "
    "result is claimed.",
    "The three-band adaptive DRC local approximation is not AdaptDRC and not "
    "SSDRC and cannot qualify the candidate.",
    "The 16 kHz mono float32 160-sample zero-delay harness is not the "
    "unverified official geometry.",
    "No real corpus, target speech, masker, hearing profile, listener, device "
    "clock or output-power qualification was used.",
    "Fixed DSP controls and published-control locators are reported separately "
    "and are never pooled with the local approximation.",
    "No provider, descriptor, registry, installed v0 path, default, public "
    "ABI, shared build, dependency lock or CI was changed.",
    "A caller-owned hash-matched placeholder is never admitted as an official "
    "AdaptDRC/SSDRC artifact.",
)

SOURCE_PINS: Dict[str, str] = {
    LISTENING_RESEARCH_PATH:
        "f29de5cdb58676b6f61ac8489ff5af44a88b2125c2022920436a6f064405992a",
    LEVEL_TONE_RESEARCH_PATH:
        "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
    INVENTORY_PATH:
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    VERIFICATION_PATH:
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    SDK_PLAN_PATH:
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS: Dict[str, str] = {
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
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LOCAL_FILES: Tuple[str, ...] = (
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

REQUIRED_REPORT_KEYS = {
    "acceptance_profile",
    "asset_pins",
    "base_commit",
    "board_row",
    "boundary",
    "branch",
    "caller_asset_contract",
    "claim",
    "component_id",
    "contract_sha256",
    "controls",
    "decision",
    "defer_before",
    "evidence_status",
    "exact_blockers",
    "fixed_dsp_controls",
    "fixture",
    "format",
    "gates",
    "local_approximation",
    "measurements",
    "missing_results",
    "negative_claims",
    "no_missing_result_qualifies_candidate",
    "profile",
    "proposal_only",
    "published_controls_assessment",
    "qualification",
    "qualification_status",
    "reopen_condition",
    "schema_id",
    "scope",
    "separation_from_siblings",
    "status",
    "task_id",
    "title",
    "upstream",
}

REQUIRED_CONTRACT_KEYS = {
    "acceptance_profile",
    "base_commit",
    "board_row",
    "boundary",
    "boundary_pins",
    "branch",
    "caller_asset_contract",
    "component_id",
    "decision",
    "defer_before",
    "evidence_status",
    "exact_blockers",
    "format",
    "gates",
    "invariants",
    "local_files",
    "negative_claims",
    "profile",
    "proposal_only",
    "qualification",
    "qualification_status",
    "reopen_condition",
    "reviewer",
    "scenario",
    "schema_id",
    "scope",
    "source_pins",
    "status",
    "task_id",
    "title",
    "upstream",
}


def _format_block() -> Dict[str, Any]:
    return {
        "sdk_v0_channels": CHANNELS,
        "sdk_v0_frame_samples": FRAME_SAMPLES,
        "sdk_v0_geometry_preserved": True,
        "sdk_v0_sample_format": "f32",
        "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
        "surrogate_channels": CHANNELS,
        "surrogate_content_delay_samples": CONTENT_DELAY_SAMPLES,
        "surrogate_frame_samples": FRAME_SAMPLES,
        "surrogate_sample_format": "float32",
        "surrogate_sample_rate_hz": SAMPLE_RATE_HZ,
        "upstream_channels": None,
        "upstream_content_delay_samples": None,
        "upstream_frame_samples": None,
        "upstream_geometry_verified": False,
        "upstream_hop_samples": None,
        "upstream_loudness_normalization": None,
        "upstream_output_power_constraint_db": None,
        "upstream_sample_rate_hz": None,
    }


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "blocked_cases": [
            "no official AdaptDRC/SSDRC source, parameters or runtime, so no "
            "exact output is reproduced",
            "no official receiver-side geometry, buffering delay, loudness "
            "normalization or output-power constraint",
            "no rights-cleared target speech, listener-side masker or hearing "
            "profile cohort",
            "no independent intelligibility, quality, listening-effort or "
            "output-power result",
            "no target-device playback availability, deadline or memory timing",
            "no opt-in provider intake, descriptor review or release approval",
        ],
        "mapped_cases": [
            "identity, static-gain, fixed-tilt and full-band compressor "
            "controls on the exact 16 kHz/160-sample grid",
            "deterministic synthetic sweeps, steps, impulses, silence and "
            "speech-like mixtures",
            "gain, tone response, level-transfer slope, attack/release, "
            "headroom and zero content delay",
            "finite, peak, clipping, silence-exactness and nonfinite rejection",
            "state reset, stale epoch, chunk-boundary and streaming parity",
            "fixed DSP controls separated from the local approximation and from "
            "unreproduced published controls",
        ],
        "name": "DSP",
        "not_applicable": [
            "no candidate artifact exists to evaluate",
            "the local approximation is not AdaptDRC or SSDRC",
            "no real corpus, listener or target device is available",
        ],
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    }


def _published_controls() -> Dict[str, Any]:
    return {
        "adaptdrc": {
            "exact_algorithm_present": False,
            "exact_parameters_present": False,
            "license_present": False,
            "locator": PRODUCT_PAGE,
            "reference_output_present": False,
            "reproduced": False,
            "result_claim": False,
            "runtime_present": False,
            "source_present": False,
            "status": "public_product_description_only",
        },
        "separation": {
            "fixed_dsp_measured_locally": True,
            "local_approximation_is_published_control": False,
            "pooling_performed": False,
            "published_controls_reproduced": False,
        },
        "ssdrc": {
            "designation": "spectral shaping and dynamic-range compression",
            "exact_algorithm_present": False,
            "exact_filterbank_or_parameters_present": False,
            "license_present": False,
            "literature_locator": SSDRC_LITERATURE_LOCATOR,
            "reference_output_present": False,
            "reproduced": False,
            "result_claim": False,
            "runtime_present": False,
            "source_present": False,
            "status": "literature_locator_only",
        },
    }


def _qualification_block() -> Dict[str, Any]:
    return {
        "all_release_gates_blocked": True,
        "algorithm_identity_verified": False,
        "fixed_dsp_separated": True,
        "geometry_verified": False,
        "listening_present": False,
        "local_approximation_is_candidate": False,
        "missing_result_promoted": False,
        "not_qualified": True,
        "provider_intake_present": False,
        "published_control_reproduced": False,
        "quality_result_present": False,
        "readiness": "incomplete",
        "reference_output_present": False,
        "release_claim": False,
        "rights_cleared_cohort_present": False,
        "runtime_present": False,
        "source_licensed": False,
        "source_present": False,
        "status": QUALIFICATION,
        "timing_result_present": False,
    }


def _report_body() -> Dict[str, Any]:
    measurements = {mode: measure_mode(mode) for mode in VALID_MODES}
    impulse = impulse_control()
    return {
        "acceptance_profile": _acceptance_profile(),
        "asset_pins": {
            "asset:configuration": {
                "executed": False,
                "expected_path": CONFIGURATION_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(CONFIGURATION_PATH).exists(),
            },
            "asset:license": {
                "executed": False,
                "expected_path": LICENSE_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(LICENSE_PATH).exists(),
            },
            "asset:reference_output": {
                "executed": False,
                "expected_path": REFERENCE_OUTPUT_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(REFERENCE_OUTPUT_PATH).exists(),
            },
            "asset:runtime": {
                "admitted": False,
                "executed": False,
                "expected_path": RUNTIME_ENV_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(RUNTIME_ENV_PATH).exists(),
            },
            "asset:source": {
                "executed": False,
                "expected_path": SOURCE_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(SOURCE_PATH).exists(),
            },
        },
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "reviewer": REVIEWER,
            "worktree": CLAIM_WORKTREE,
        },
        "component_id": COMPONENT,
        "contract_sha256": sha256(canonical_bytes(contract_payload())),
        "controls": {
            "asset": asset_controls(),
            "config": config_adverse_control(),
            "frame": frame_adverse_control(),
            "impulse": impulse,
            "nonfinite": nonfinite_control(),
            "reset": reset_control(),
            "silence": silence_control(),
            "streaming_parity": streaming_parity_control(),
        },
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(blocker) for blocker in EXACT_BLOCKERS],
        "fixed_dsp_controls": {
            "fixed_tilt": {
                "candidate_result": False,
                "measurements": measurements["fixed_tilt"],
                "role": "fixed_dsp_control",
            },
            "full_band_compressor": {
                "candidate_result": False,
                "measurements": measurements["full_band_compressor"],
                "role": "fixed_dsp_control",
            },
            "identity": {
                "candidate_result": False,
                "measurements": measurements["identity"],
                "role": "mandatory_control",
            },
            "static_gain": {
                "candidate_result": False,
                "measurements": measurements["static_gain"],
                "role": "fixed_dsp_control",
            },
        },
        "fixture": {
            "channels": CHANNELS,
            "component_digests": FIXTURE_DIGESTS,
            "frames": TOTAL_FRAMES,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "spec_digest": FIXTURE_SPEC_DIGEST,
            "total_samples": TOTAL_SAMPLES,
        },
        "format": _format_block(),
        "gates": [
            {"id": gate, "qualifies": False, "requirement": requirement,
             "status": "blocked"}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "local_approximation": {
            "algorithm": {
                "adaptation": "bounded high-band balance controller",
                "bands": list(BAND_EDGES_HZ),
                "content_delay_samples": CONTENT_DELAY_SAMPLES,
                "gain_computer": "threshold -24 dBFS, ratio 3:1, 5 ms attack, "
                                 "120 ms release",
                "peak_ceiling": PEAK_CEILING,
                "static_tilt_db": list(LOCAL_TILT_DB),
            },
            "candidate_result": False,
            "id": "local_three_band_adaptive_drc_surrogate",
            "is_adaptdrc": False,
            "is_ssdrc": False,
            "measurements": measurements["local_approximation"],
            "model_free": True,
            "surrogate_only": True,
            "uses_real_corpus": False,
        },
        "measurements": measurements,
        "missing_results": [
            "official AdaptDRC/SSDRC source revision and licence",
            "official algorithm identity and exact parameter set",
            "pinned runtime and approved reference output vectors",
            "official receiver-side geometry, content delay and output-power "
            "constraint",
            "rights-cleared target-speech and listener-side masker cohort",
            "independent intelligibility/quality or permitted listening result",
            "target-device timing, memory and deadline",
            "opt-in provider intake, descriptor review and default decision",
        ],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "no_missing_result_qualifies_candidate": True,
        "profile": PROFILE,
        "proposal_only": True,
        "published_controls_assessment": _published_controls(),
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply the official source revision and licence, the exact "
            "published algorithm and parameters, a locked runtime and approved "
            "reference outputs, the official receiver-side geometry and "
            "output-power constraint, and a rights-cleared target/masker/"
            "listening cohort. Then score independently, measure target timing "
            "and complete OFF-by-default opt-in provider intake. Until then the "
            "candidate stays DEFER, incomplete and not qualified."),
        "schema_id": SCHEMA_ID,
        "scope": dict(SCOPE),
        "separation_from_siblings": {
            "no_pooling": True,
            "note": (
                "The full-band receive DRC, feed-forward compressor, envelope "
                "AGC, EBU R128/loudnorm, fixed spectral tilt and STOI/ESTOI "
                "packages are separate evidence. They use different candidates, "
                "fixtures and dispositions; this package does not pool, import, "
                "reuse or reinterpret their outputs."),
            "sibling_packages": [
                "docs/task-evidence/full-band-receive-drc",
                "docs/task-evidence/feed-forward-compressor",
                "docs/task-evidence/envelope-agc",
                "docs/task-evidence/ebu-r128-ffmpeg-loudnorm",
                "docs/task-evidence/fixed-six-band-spectral-tilt",
                "docs/task-evidence/stoi-estoi",
            ],
        },
        "status": STATUS,
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "algorithm_parameters": UPSTREAM_PARAMETERS,
            "algorithm_parameters_status": UPSTREAM_PARAMETERS_STATUS,
            "commit": UPSTREAM_COMMIT,
            "commit_status": "not_recorded",
            "geometry_status": UPSTREAM_GEOMETRY_STATUS,
            "license": UPSTREAM_LICENSE,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "note": (
                "The local inventory records only a public product-page "
                "locator. The pinned research note explicitly says its "
                "compressor is not AdaptDRC/SSDRC. No commit, licence, version, "
                "parameter set, runtime or output vector was obtained or "
                "fabricated."),
            "product_page": PRODUCT_PAGE,
            "reference_output": UPSTREAM_REFERENCE_OUTPUT,
            "reference_output_status": UPSTREAM_REFERENCE_OUTPUT_STATUS,
            "runtime": UPSTREAM_RUNTIME,
            "runtime_status": UPSTREAM_RUNTIME_STATUS,
            "source_present": False,
            "source_licensed": False,
            "ssdrc_designation": "spectral shaping and dynamic-range compression",
            "ssdrc_literature_locator": SSDRC_LITERATURE_LOCATOR,
            "version": UPSTREAM_VERSION,
            "version_status": "not_recorded",
        },
    }


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def build_report() -> Dict[str, Any]:
    report = _plain(_report_body())
    if has_negative_zero(report):
        raise ValueError("negative_zero_in_report")
    return report


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    if report is None:
        report = build_report()
    return canonical_bytes(report)


def contract_payload() -> Dict[str, Any]:
    return {
        "acceptance_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "note": (
                "Only the stable linked-row identity is gated. The mutable "
                "full plan/swarm/TASKS.json is never read into, hashed by or "
                "pinned to this package."),
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "boundary_pins": dict(BOUNDARY_PINS),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "component_id": COMPONENT,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(blocker) for blocker in EXACT_BLOCKERS],
        "format": _format_block(),
        "gates": [
            {"id": gate, "qualifies": False, "requirement": requirement,
             "status": "blocked"}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "the package is proposal-only and incomplete",
            "no missing, blocked or rejected result is promoted to a pass",
            "no official source, algorithm, runtime, reference output, corpus "
            "or listener is downloaded, copied, imported, loaded or executed",
            "fixed DSP controls, published-control locators and the local "
            "approximation are never pooled",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
        "local_files": sorted(LOCAL_FILES),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply the official source revision and licence, the exact "
            "published algorithm and parameters, a locked runtime and approved "
            "reference outputs, the official receiver-side geometry and "
            "output-power constraint, and a rights-cleared target/masker/"
            "listening cohort. Then score independently, measure target timing "
            "and complete OFF-by-default opt-in provider intake."),
        "reviewer": REVIEWER,
        "scenario": {
            "channels": CHANNELS,
            "content_delay_samples": CONTENT_DELAY_SAMPLES,
            "id": "adaptdrc-ssdrc-receiver-side-dsp-blocker-v1",
            "is_candidate_result": False,
            "is_local_approximation": True,
            "note": (
                "The local approximation runs on the exact installed v0 grid "
                "with zero content delay. It is not AdaptDRC or SSDRC and its "
                "geometry is not the unverified official geometry."),
            "output_power_constraint": "not_established",
            "task_geometry": "receiver-side spectral shaping plus DRC",
            "upstream_geometry_verified": False,
        },
        "schema_id": CONTRACT_SCHEMA_ID,
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "algorithm_parameters": UPSTREAM_PARAMETERS,
            "algorithm_parameters_status": UPSTREAM_PARAMETERS_STATUS,
            "commit": UPSTREAM_COMMIT,
            "commit_status": "not_recorded",
            "geometry_status": UPSTREAM_GEOMETRY_STATUS,
            "license": UPSTREAM_LICENSE,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "product_page": PRODUCT_PAGE,
            "reference_output": UPSTREAM_REFERENCE_OUTPUT,
            "reference_output_status": UPSTREAM_REFERENCE_OUTPUT_STATUS,
            "runtime": UPSTREAM_RUNTIME,
            "runtime_status": UPSTREAM_RUNTIME_STATUS,
            "source_present": False,
            "source_licensed": False,
            "ssdrc_designation": "spectral shaping and dynamic-range compression",
            "ssdrc_literature_locator": SSDRC_LITERATURE_LOCATOR,
            "version": UPSTREAM_VERSION,
            "version_status": "not_recorded",
        },
    }


def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())


def _local_manifest_paths() -> List[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name != "SOURCES.sha256")


def sources_bytes() -> bytes:
    rows: List[Tuple[str, str]] = []
    for name, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + name))
    for name, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + name))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to the pinned research workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        f"# Full mutable plan/swarm/TASKS.json is never hashed; only "
        f"board_row.stable_sha256={BOARD_ROW_STABLE_SHA256} is gated.",
    ]
    for digest, path in rows:
        lines.append(f"{digest}  {path}")
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{64}  \S+", line) is None:
            raise ValueError(f"malformed_pin_line:{number}")
        digest, path = line.split("  ", 1)
        if not (path.startswith("source:") or path.startswith("sdk:") or
                path.startswith(TASK_PREFIX)):
            raise ValueError(f"unknown_pin_prefix:{number}")
        if path in seen:
            raise ValueError(f"duplicate_pin:{number}")
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def allowed_pin_keys() -> set[str]:
    return ({"source:" + name for name in SOURCE_PINS} |
            {"sdk:" + name for name in BOUNDARY_PINS} |
            {TASK_PREFIX + name for name in _local_manifest_paths()})


def expected_readme_keys() -> Dict[str, set[str]]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {
            name for name in _local_manifest_paths()
            if name not in ARTIFACT_TABLE_EXCLUDED
        },
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


def parse_readme_digest_tables(text: str) -> Dict[str, List[Tuple[str, str]]]:
    result: Dict[str, List[Tuple[str, str]]] = {}
    for section in README_SECTIONS:
        rows: List[Tuple[str, str]] = []
        for line in _section_text(text, section).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or \
                        re.fullmatch(r"[0-9]+", cells[2]) is None:
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


def verify_readme_digests(text: str) -> Dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            missing = sorted(expected[section] - actual_keys)
            extra = sorted(actual_keys - expected[section])
            raise ValueError(
                f"readme_key_mismatch:{section}:missing={missing}:extra={extra}")
        for key, digest in parsed[section]:
            if section == "source":
                expected_digest = SOURCE_PINS[key[len("source:"):]]
                path = resolve_source_path(key[len("source:"):])
            elif section == "boundary":
                expected_digest = BOUNDARY_PINS[key[len("sdk:"):]]
                path = SDK_ROOT / key[len("sdk:"):]
            else:
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if path is not None and path.is_file() and \
                    sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = f"| `{key}` | `{sha256_file(HERE / key)}` | {size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_artifact_table() -> str:
    rows = [
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->",
        "| Path | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
    ]
    for name in _local_manifest_paths():
        if name in ARTIFACT_TABLE_EXCLUDED:
            continue
        path = HERE / name
        rows.append(f"| `{name}` | `{sha256_file(path)}` | "
                    f"{path.stat().st_size} |")
    rows.append("<!-- DIGEST_TABLE_ARTIFACTS_END -->")
    return "\n".join(rows)


def update_readme_artifact_table(text: str) -> str:
    block = render_artifact_table()
    start = text.index(README_MARKERS["artifacts"][0])
    end = text.index(README_MARKERS["artifacts"][1], start) + \
        len(README_MARKERS["artifacts"][1])
    return text[:start] + block + text[end:]


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = [
        '{"a":1,"a":2}',
        '{"a": NaN}',
        '{"a": Infinity}',
        '[]',
        '{"a":1} trailing',
    ]
    rejected_json = 0
    for text in bad_json:
        try:
            strict_loads(text)
        except ValueError:
            rejected_json += 1
    bad_pins = [
        "not-a-pin",
        "0" * 64 + " source:one",
        "0" * 63 + "  source:one",
        "\n".join(["0" * 64 + "  source:one", "0" * 64 + "  source:one"]),
        "0" * 64 + "  other:one",
    ]
    rejected_pins = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except ValueError:
            rejected_pins += 1
    bad_readme = [
        "# no tables",
        "<!-- digest-table: source -->\n| `source:x` | `zz` |\n"
        "<!-- digest-table: end -->",
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->\n"
        "| `a` | `" + "0" * 64 + "` |\n<!-- DIGEST_TABLE_ARTIFACTS_END -->",
    ]
    rejected_readme = 0
    for text in bad_readme:
        try:
            parse_readme_digest_tables(text)
        except ValueError:
            rejected_readme += 1
    return {
        "bad_json_rejected": rejected_json,
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": rejected_pins,
        "bad_pins_total": len(bad_pins),
        "bad_readme_rejected": rejected_readme,
        "bad_readme_total": len(bad_readme),
    }
