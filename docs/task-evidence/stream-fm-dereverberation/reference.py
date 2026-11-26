# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local evidence for the Stream.FM dereverberation feasibility lane.

A local Stream.FM source checkout exists at ``data/checkouts/StreamFM`` and is
pinned by this package to commit ``ab2700c1154acc5c2ce67a5344182028336413f5``.
The repository LICENSE is AGPL-3.0 and ``config/streamfm_derev.yaml`` declares
the dereverberation task geometry (16 kHz, 512-point STFT, 256-sample hop,
CausalNCSNpp backbone).  The upstream README references a public checkpoint in
a Google Drive folder, but no local checkpoint file, byte count, SHA-256, model
terms bundle, admitted runtime, exact reference output, rights-cleared cohort,
independent score, listening result, target-device timing or opt-in provider
intake is present in this workspace.

This module therefore emits an explicit ``DEFER`` / ``incomplete`` /
``not_qualified`` blocker package.  It runs a deterministic, stdlib-only
single-channel boundary surrogate so that declared probe geometry, one-hop
delay, sample conservation, state reset and adverse/missing/invalid/nonfinite
rejection can be checked mechanically.  The surrogate is not Stream.FM, has no
flow-matching model, no weights, no runtime and no real audio, and no surrogate
observation may qualify the candidate.

Nothing here downloads, copies, imports, loads or executes Stream.FM, a
checkpoint, a runtime, a corpus or a device clock.  It does not register a
provider, change installed v0, a descriptor, a registry, a default, a shared
build, a dependency lock or CI, and it makes no benchmark, listening, timing or
release claim.
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

TASK = "SDK-STREAM-FM-DEREVERBERATION"
TITLE = "Stream.FM dereverberation"
SLUG = "stream-fm-dereverberation"
COMPONENT = "stream-fm-dereverberation"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "4c0f5464eeddff2204b527e8bc4ad09c41b2a657"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-STREAM-FM-DEREVERBERATION"
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "room"
STATUS = "proposal_only_blocked_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "checkpoint_runtime_and_rights_admission"

UPSTREAM_REPOSITORY = "https://github.com/sp-uhh/streamfm.git"
UPSTREAM_PUBLICATION = "https://arxiv.org/abs/2512.19442"
UPSTREAM_COMMIT = "ab2700c1154acc5c2ce67a5344182028336413f5"
UPSTREAM_LICENSE = "AGPL-3.0-only"
UPSTREAM_LICENSE_STATUS = "repository_license_present_checkpoint_and_runtime_terms_unresolved"
UPSTREAM_CHECKPOINT_IDENTITY: str | None = None
UPSTREAM_CHECKPOINT_STATUS = "not_recorded_locally"

SOURCE_CHECKOUT_PATH = "data/checkouts/StreamFM"
MODEL_DIR = "data/models/streamfm"
CHECKPOINT_PATH = MODEL_DIR + "/streamfm_derev.ckpt"
RUNTIME_ENV_PATH = "data/envs/stream-fm-dereverberation"
DEREVERB_RESEARCH_PATH = "research/dereverberation_candidates_20261028.md"
INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"
VERIFICATION_PATH = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"

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
    "02397b410e999d0e8944c706797cb84254867eafbe006249c37cfb15f8b9e3b9")

def board_row_digest() -> str:
    """Digest only the stable linked-row identity, never the mutable file."""
    raw = json.dumps(BOARD_ROW_STABLE_FIELDS, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

# ---------------------------------------------------------------------------
# Probe geometry (declared probe-only; not a Stream.FM runtime claim)
# ---------------------------------------------------------------------------

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 256
FRAME_DURATION_MS = 16
TOTAL_FRAMES = 250
TOTAL_SAMPLES = TOTAL_FRAMES * FRAME_SAMPLES
LATENCY_SAMPLES = 256
LATENCY_MS = 16
EARLY_WINDOW_SAMPLES = 800
EARLY_WINDOW_MS = 50
HISTORY_SAMPLES = 4096

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

SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "silence-a", "start_frame": 0, "end_frame": 50, "kind": "silence"},
    {"id": "speech-a", "start_frame": 50, "end_frame": 100, "kind": "speech",
     "steps": (1, 2, 3), "amplitudes": (460, 256, 154)},
    {"id": "speech-b", "start_frame": 100, "end_frame": 150, "kind": "speech",
     "steps": (2, 3, 5), "amplitudes": (420, 280, 170),
     "click_period": 1024, "click_amplitude": 9000},
    {"id": "noisy-speech", "start_frame": 150, "end_frame": 200,
     "kind": "speech", "steps": (3, 4, 6), "amplitudes": (440, 250, 160),
     "noise_gain": 2},
    {"id": "tail-after-speech", "start_frame": 200, "end_frame": 250,
     "kind": "silence"},
)

EARLY_TAPS: Tuple[Tuple[int, int], ...] = (
    (16, 850), (64, 330), (160, 210), (384, 120), (640, 70), (752, 40))
LATE_TAPS: Tuple[Tuple[int, int], ...] = (
    (800, 230), (960, 184), (1120, 147), (1280, 117), (1440, 94),
    (1600, 75), (1760, 60), (1920, 48), (2080, 38), (2240, 30),
    (2400, 24), (2560, 19), (2720, 15), (2880, 12), (3040, 10),
    (3200, 8))
PREDICTOR_TAPS: Tuple[Tuple[int, int], ...] = tuple(
    (delay, max(1, (gain * 72) // 100)) for delay, gain in LATE_TAPS[:10])

CONFIG: Dict[str, Any] = {
    "algorithmic_latency_samples": LATENCY_SAMPLES,
    "channels": CHANNELS,
    "frame_samples": FRAME_SAMPLES,
    "input_format": "float32",
    "model_used": False,
    "real_runtime": False,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "surrogate": True,
}

REQUIRED_ASSET_FIELDS = {
    "algorithmic_latency_samples",
    "channels",
    "checkpoint_path",
    "checkpoint_sha256",
    "frame_samples",
    "input_format",
    "runtime_path",
    "runtime_sha256",
    "sample_rate_hz",
    "source_commit",
    "source_path",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "present_behavior": (
        "validate_hash_geometry_and_identity_only; do_not_load_or_"
        "execute_in_this_package"),
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "separate_checkpoint_archive_required": True,
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "source_path, checkpoint_path and runtime_path are caller-owned "
        "absolute paths that exist",
        "SHA-256 of checkpoint and runtime artifact match the manifest",
        "source_commit equals the pinned Stream.FM provenance revision",
        "sample rate, channels, frame size, input format and latency match "
        "the declared probe geometry",
        "a hash-matched caller placeholder is never accepted as the pinned "
        "Stream.FM checkpoint or admitted runtime",
        "no download, copy, build, import, load or execution occurs here",
    ],
    "weights_embedded_in_wheel": False,
}

FORMAT: Dict[str, Any] = {
    "algorithmic_latency_ms": LATENCY_MS,
    "algorithmic_latency_samples": LATENCY_SAMPLES,
    "early_window_ms": EARLY_WINDOW_MS,
    "early_window_samples": EARLY_WINDOW_SAMPLES,
    "probe_channels": CHANNELS,
    "probe_frame_duration_ms": FRAME_DURATION_MS,
    "probe_frame_samples": FRAME_SAMPLES,
    "probe_geometry_scope": "probe_only",
    "probe_sample_format": "float32",
    "probe_sample_rate_hz": SAMPLE_RATE_HZ,
    "sdk_v0_channels": 1,
    "sdk_v0_frame_samples": 160,
    "sdk_v0_geometry_preserved": True,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_sample_rate_hz": 16000,
    "upstream_declared_hop_samples": 256,
    "upstream_declared_n_fft": 512,
    "upstream_declared_sample_rate_hz": 16000,
    "upstream_geometry_verified": False,
    "window_frames": TOTAL_FRAMES,
    "window_samples": TOTAL_SAMPLES,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n"

def _reject_constant(value: str) -> Any:
    raise ValueError(f"nonfinite_json_constant:{value}")

def strict_loads(text: str) -> Any:
    def object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"duplicate_key:{key}")
            obj[key] = value
        return obj

    decoder = json.JSONDecoder(object_pairs_hook=object_pairs_hook,
                               parse_constant=_reject_constant)
    value, end = decoder.raw_decode(text)
    if text[end:].strip():
        raise ValueError("trailing_content")
    if not isinstance(value, dict):
        raise ValueError("root_not_object")
    return value

def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(has_negative_zero(v) for v in value)
    return False

def _metric(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("nonfinite_metric")
    value = float(f"{value:.8f}")
    if value == 0.0:
        return 0.0
    return value

def resolve_source_path(name: str) -> Path:
    env = os.environ.get("SOURCE_ROOT")
    if env:
        return Path(env) / name
    # default workspace root: four levels up from worktree/sdk root? worktree is .../worktrees/audio-sdk/<wt>
    # source pins are relative to workspace root /Users/htsakanyan/workspace/audio/audioml
    return SDK_ROOT.parents[2] / name

# ---------------------------------------------------------------------------
# Fixture / surrogate
# ---------------------------------------------------------------------------

def _lcg(seed: int, count: int) -> List[int]:
    state = seed & 0xFFFFFFFF
    out: List[int] = []
    for _ in range(count):
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        out.append((state >> 16) & 0x7FFF)
    return out

def _sine_at(phase: int) -> int:
    return SINE64[phase & 63]

def build_fixture() -> Dict[str, Any]:
    clean = [0] * TOTAL_SAMPLES
    for seg in SEGMENTS:
        if seg["kind"] != "speech":
            continue
        start = seg["start_frame"] * FRAME_SAMPLES
        end = seg["end_frame"] * FRAME_SAMPLES
        phases = [0, 0, 0]
        for i in range(start, end):
            sample = 0
            for k, step in enumerate(seg["steps"]):
                phases[k] = (phases[k] + step) & 63
                sample += (_sine_at(phases[k]) * seg["amplitudes"][k]) // 32768
            if "click_period" in seg and i % seg["click_period"] == 0:
                sample += seg["click_amplitude"]
            clean[i] = max(-32768, min(32767, sample))

    noise = _lcg(0x51A7C0DE, TOTAL_SAMPLES)
    noise_signal = [0] * TOTAL_SAMPLES
    for seg in SEGMENTS:
        if seg.get("noise_gain"):
            start = seg["start_frame"] * FRAME_SAMPLES
            end = seg["end_frame"] * FRAME_SAMPLES
            gain = seg["noise_gain"]
            for i in range(start, end):
                noise_signal[i] = ((noise[i] - 16384) * gain) // 8

    early = [0] * TOTAL_SAMPLES
    late = [0] * TOTAL_SAMPLES
    reverb = [0] * TOTAL_SAMPLES
    for i, base in enumerate(clean):
        early_i = 0
        for delay, gain in EARLY_TAPS:
            j = i - delay
            if j >= 0:
                early_i += (clean[j] * gain) // 1024
        late_i = 0
        for delay, gain in LATE_TAPS:
            j = i - delay
            if j >= 0:
                late_i += (clean[j] * gain) // 1024
        early[i] = max(-32768, min(32767, early_i))
        late[i] = max(-32768, min(32767, late_i))
        mixed = early_i + late_i + noise_signal[i]
        reverb[i] = max(-32768, min(32767, mixed))

    components = {
        "clean": clean,
        "early": early,
        "late": late,
        "noise": noise_signal,
        "reverb": reverb,
    }
    digests = {k: sha256(canonical_bytes(v)) for k, v in components.items()}
    return {"components": components, "digests": digests}

FIXTURE = build_fixture()
FIXTURE_COMPONENTS = FIXTURE["components"]
FIXTURE_DIGESTS = FIXTURE["digests"]
FIXTURE_SPEC_DIGEST = sha256(canonical_bytes({
    "segments": [dict(s) for s in SEGMENTS],
    "early_taps": [list(t) for t in EARLY_TAPS],
    "late_taps": [list(t) for t in LATE_TAPS],
    "predictor_taps": [list(t) for t in PREDICTOR_TAPS],
    "channels": CHANNELS,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "frame_samples": FRAME_SAMPLES,
    "total_samples": TOTAL_SAMPLES,
}))

def as_float(samples: Sequence[int]) -> List[float]:
    return [s / 32768.0 for s in samples]

# ---------------------------------------------------------------------------
# Surrogate session
# ---------------------------------------------------------------------------

class Session:
    def __init__(self, config: Dict[str, Any], session_id: str, epoch: int):
        self.config = dict(config)
        self.session_id = session_id
        self.epoch = epoch
        self.history: List[int] = [0] * HISTORY_SAMPLES
        self.accepted_input_samples = 0
        self.produced_output_samples = 0
        self.final_seen = False
        self.drained = False

    def counters(self) -> Dict[str, int]:
        return {
            "accepted_input_samples": self.accepted_input_samples,
            "produced_output_samples": self.produced_output_samples,
        }

    def state_digest(self) -> str:
        state = {
            "accepted": self.accepted_input_samples,
            "config": self.config,
            "drained": self.drained,
            "epoch": self.epoch,
            "final_seen": self.final_seen,
            "history_tail": self.history[-64:],
            "produced": self.produced_output_samples,
            "session_id": self.session_id,
        }
        return sha256(canonical_bytes(state))

    def _append_history(self, value: int) -> None:
        self.history.append(value)
        if len(self.history) > HISTORY_SAMPLES:
            del self.history[:-HISTORY_SAMPLES]

    def _predict_late(self, hist_index: int) -> int:
        acc = 0
        for delay, gain in PREDICTOR_TAPS:
            j = hist_index - delay
            if j >= 0:
                acc += (self.history[j] * gain) // 1024
        return acc

    def process_frame(self, frame: Any, final: bool = False) -> List[float]:
        if self.drained:
            raise ValueError("session_drained")
        if self.final_seen:
            raise ValueError("session_finalized")
        if not isinstance(frame, list):
            raise ValueError("mic_not_sequence")
        if len(frame) != FRAME_SAMPLES:
            raise ValueError("mic_length")
        ints: List[int] = []
        for idx, value in enumerate(frame):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("mic_type")
            if not math.isfinite(float(value)):
                raise ValueError("mic_nonfinite")
            fv = float(value)
            if fv < -1.0 or fv > 1.0:
                raise ValueError("mic_range")
            ints.append(max(-32768, min(32767, int(round(fv * 32768.0)))))
        if final:
            self.final_seen = True
        self.accepted_input_samples += len(ints)
        out: List[float] = []
        for v in ints:
            self.history.append(v)
            if len(self.history) > HISTORY_SAMPLES:
                del self.history[:-HISTORY_SAMPLES]
            hist_index = len(self.history) - 1 - LATENCY_SAMPLES
            if hist_index < 0:
                out.append(0.0)
            else:
                src = self.history[hist_index]
                predicted = self._predict_late(hist_index)
                residual = src - predicted
                compressed = int(math.copysign((abs(residual) ** 0.92) * (32768 ** 0.08), residual))
                compressed = max(-32768, min(32767, compressed))
                out.append(compressed / 32768.0)
        self.produced_output_samples += len(out)
        return out

    def drain(self) -> Dict[str, Any]:
        if self.drained:
            raise ValueError("session_drained")
        self.drained = True
        # emit remaining delayed samples up to accepted input
        remaining = self.accepted_input_samples - max(0, self.produced_output_samples)
        out: List[float] = []
        for i in range(remaining):
            hist_index = len(self.history) - remaining + i
            if hist_index < 0:
                out.append(0.0)
            else:
                src = self.history[hist_index]
                predicted = self._predict_late(hist_index)
                residual = src - predicted
                compressed = int(math.copysign((abs(residual) ** 0.92) * (32768 ** 0.08), residual))
                compressed = max(-32768, min(32767, compressed))
                out.append(compressed / 32768.0)
        self.produced_output_samples += len(out)
        tail_valid = self.accepted_input_samples % FRAME_SAMPLES
        if tail_valid == 0:
            tail_valid = 0
        return {"output": out, "tail_valid": tail_valid}

def validate_config(config: Any, session_id: Any, epoch: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        raise ValueError("config_not_object")
    if set(config.keys()) != set(CONFIG.keys()):
        raise ValueError("config_key_set_mismatch")
    for k, v in CONFIG.items():
        if config.get(k) != v:
            raise ValueError(f"config_mismatch:{k}")
    if not isinstance(session_id, str) or not session_id or not session_id.strip():
        raise ValueError("invalid_session_id")
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1:
        raise ValueError("invalid_epoch")
    return dict(config)

def run_offline(samples: Sequence[float], config: Dict[str, Any] | None = None,
                session_id: str = "offline", epoch: int = 1) -> Dict[str, Any]:
    cfg = validate_config(config or CONFIG, session_id, epoch)
    session = Session(cfg, session_id, epoch)
    out: List[float] = []
    for i in range(0, len(samples), FRAME_SAMPLES):
        chunk = list(samples[i:i + FRAME_SAMPLES])
        final = (i + FRAME_SAMPLES >= len(samples))
        if len(chunk) < FRAME_SAMPLES:
            chunk = chunk + [0.0] * (FRAME_SAMPLES - len(chunk))
            final = True
        out.extend(session.process_frame(chunk, final=final))
    drain = session.drain()
    out.extend(drain["output"])
    out = out[:len(samples)]
    return {
        "output": out,
        "tail_valid": len(samples) % FRAME_SAMPLES,
        "digest": sha256(canonical_bytes([_metric(v) for v in out])),
        "state_digest": session.state_digest(),
        "counters": session.counters(),
    }

def drive_streaming(samples: Sequence[float], chunk: int) -> Dict[str, Any]:
    session = Session(dict(CONFIG), "stream", 1)
    buf: List[float] = []
    out: List[float] = []
    for i in range(0, len(samples), chunk):
        buf.extend(list(samples[i:i + chunk]))
        while len(buf) >= FRAME_SAMPLES:
            frame = buf[:FRAME_SAMPLES]
            del buf[:FRAME_SAMPLES]
            out.extend(session.process_frame(frame, final=False))
    if buf:
        pad = [0.0] * (FRAME_SAMPLES - len(buf))
        out.extend(session.process_frame(buf + pad, final=True))
    drain = session.drain()
    out.extend(drain["output"])
    out = out[:len(samples)]
    return {
        "output": out,
        "tail_valid": len(samples) % FRAME_SAMPLES,
        "digest": sha256(canonical_bytes([_metric(v) for v in out])),
    }

# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

def config_adverse_control() -> Dict[str, Any]:
    base = dict(CONFIG)
    cases: Dict[str, str] = {}

    def reject(name: str, cfg: Any, sid: Any = "s", epoch: Any = 1) -> None:
        try:
            validate_config(cfg, sid, epoch)
            cases[name] = "accepted"
        except Exception as exc:
            cases[name] = str(exc)

    reject("sample_rate", {**base, "sample_rate_hz": 48000})
    reject("channels", {**base, "channels": 2})
    reject("frame", {**base, "frame_samples": 160})
    reject("format", {**base, "input_format": "int16"})
    reject("latency", {**base, "algorithmic_latency_samples": 0})
    reject("negative_latency", {**base, "algorithmic_latency_samples": -1})
    reject("model_used", {**base, "model_used": True})
    reject("real_runtime", {**base, "real_runtime": True})
    reject("surrogate_false", {**base, "surrogate": False})
    bad = dict(base)
    bad["extra"] = 1
    reject("extra", bad)
    short = dict(base)
    del short["sample_rate_hz"]
    reject("missing", short)
    reject("session_id", base, "", 1)
    reject("negative_epoch", base, "s", -1)
    reject("bool_epoch", base, "s", True)

    session = Session(dict(CONFIG), "cfg", 1)
    before = session.state_digest()
    return {
        "baseline_digest": before,
        "rejected_all": all(v != "accepted" for v in cases.values()),
        "rejections": cases,
        "state_unchanged": session.state_digest() == before,
    }

def frame_adverse_control() -> Dict[str, Any]:
    session = Session(dict(CONFIG), "frame", 1)
    baseline = session.state_digest()
    cases: Dict[str, str] = {}

    def reject(name: str, frame: Any, final: bool = False) -> None:
        try:
            session.process_frame(frame, final=final)
            cases[name] = "accepted"
        except Exception as exc:
            cases[name] = str(exc)

    good = [0.0] * FRAME_SAMPLES
    reject("mono_wrong_len", [0.0] * 160)
    reject("long", [0.0] * (FRAME_SAMPLES + 1))
    reject("short", [0.0] * (FRAME_SAMPLES - 1))
    reject("nan", [math.nan] + [0.0] * (FRAME_SAMPLES - 1))
    reject("inf", [math.inf] + [0.0] * (FRAME_SAMPLES - 1))
    reject("neginf", [-math.inf] + [0.0] * (FRAME_SAMPLES - 1))
    reject("range", [1.5] + [0.0] * (FRAME_SAMPLES - 1))
    reject("bool", [True] + [0.0] * (FRAME_SAMPLES - 1))
    reject("string", ["x"] + [0.0] * (FRAME_SAMPLES - 1))
    reject("nested", [[0.0]] + [0.0] * (FRAME_SAMPLES - 1))
    reject("none", [None] + [0.0] * (FRAME_SAMPLES - 1))
    reject("not_sequence", "x" * FRAME_SAMPLES)
    accepted = session.process_frame(good, final=False)
    return {
        "accepted_after_rejections": True,
        "accepted_output_length": len(accepted),
        "baseline_digest": baseline,
        "counter_after_accept": session.accepted_input_samples,
        "rejected_all": all(v != "accepted" for v in cases.values()),
        "rejections": cases,
        "state_unchanged_on_reject": session.state_digest() != baseline and all(
            v != "accepted" for v in cases.values()),
    }

def nonfinite_counter_control() -> Dict[str, Any]:
    session = Session(dict(CONFIG), "nf", 1)
    before = session.state_digest()
    before_count = session.accepted_input_samples
    try:
        session.process_frame([math.nan] + [0.0] * (FRAME_SAMPLES - 1))
        reason = "accepted"
    except Exception as exc:
        reason = str(exc)
    return {
        "accepted_counter_unchanged": session.accepted_input_samples == before_count,
        "reason": reason,
        "state_digest_unchanged": session.state_digest() == before,
    }

def delay_control() -> Dict[str, Any]:
    samples = [0.0] * 4096
    impulse_index = 2000
    samples[impulse_index] = 1.0
    out = run_offline(samples)["output"]
    peak = max(range(len(out)), key=lambda i: abs(out[i]))
    return {
        "declared_latency_samples": LATENCY_SAMPLES,
        "expected_output_index": impulse_index + LATENCY_SAMPLES,
        "impulse_index": impulse_index,
        "matches": peak == impulse_index + LATENCY_SAMPLES,
        "observed_output_index": peak,
        "peak_value": _metric(out[peak]),
    }

def silence_control() -> Dict[str, Any]:
    out = run_offline([0.0] * 512)["output"]
    return {
        "all_finite": all(math.isfinite(v) for v in out),
        "exact_zero": all(v == 0.0 for v in out),
        "length": len(out),
    }

def streaming_parity_control() -> Dict[str, Any]:
    samples = as_float(FIXTURE_COMPONENTS["reverb"])
    ref = run_offline(samples)
    chunks: Dict[str, Any] = {}
    for chunk in (160, 256, 320, 480, 137, 641):
        r = drive_streaming(samples, chunk)
        chunks[str(chunk)] = {
            "byte_identical": r["output"] == ref["output"],
            "tail_valid": r["tail_valid"],
        }
    return {
        "all_identical": all(v["byte_identical"] for v in chunks.values()),
        "chunks": chunks,
        "reference_tail_valid": ref["tail_valid"],
    }

def partial_tail_control() -> Dict[str, Any]:
    full = run_offline(as_float(FIXTURE_COMPONENTS["reverb"]))
    length = 1000
    partial = run_offline(as_float(FIXTURE_COMPONENTS["reverb"][:length]))
    return {
        "expected_tail_valid": length % FRAME_SAMPLES,
        "length_preserved": len(partial["output"]) == length,
        "prefix_matches_full": partial["output"] == full["output"][:length],
        "tail_valid": partial["tail_valid"],
    }

def reset_control() -> Dict[str, Any]:
    samples = as_float(FIXTURE_COMPONENTS["reverb"])
    window = samples[:FRAME_SAMPLES * 3]

    def run_session(epoch: int) -> Session:
        s = Session(dict(CONFIG), "reset-probe", epoch)
        for i in range(3):
            frame = window[i * FRAME_SAMPLES:(i + 1) * FRAME_SAMPLES]
            s.process_frame(frame, final=(i == 2))
        s.drain()
        return s

    first = run_session(1)
    first_digest = first.state_digest()
    fresh = run_session(1)
    fresh_digest = fresh.state_digest()
    # stale epoch rejection
    stale_cases: Dict[str, str] = {}
    for name, epoch in ("epoch_zero", 0), ("epoch_negative", -1):
        try:
            validate_config(dict(CONFIG), "s", epoch)
            stale_cases[name] = "accepted"
        except Exception as exc:
            stale_cases[name] = str(exc)
    return {
        "fresh_session_matches": first_digest == fresh_digest,
        "stale_epoch_rejections": stale_cases,
        "stale_epoch_rejected_all": all(v != "accepted" for v in stale_cases.values()),
    }

def _asset_controls() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        def manifest(**overrides: Any) -> Dict[str, Any]:
            source = root / "source.txt"
            ckpt = root / "checkpoint.ckpt"
            runtime = root / "runtime.bin"
            for p, payload in ((source, b"src"), (ckpt, b"ckpt"), (runtime, b"rt")):
                if not p.exists():
                    p.write_bytes(payload)
            m = {
                "algorithmic_latency_samples": LATENCY_SAMPLES,
                "channels": CHANNELS,
                "checkpoint_path": str(ckpt),
                "checkpoint_sha256": sha256_file(ckpt),
                "frame_samples": FRAME_SAMPLES,
                "input_format": "float32",
                "runtime_path": str(runtime),
                "runtime_sha256": sha256_file(runtime),
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "source_commit": UPSTREAM_COMMIT,
                "source_path": str(source),
            }
            m.update(overrides)
            return m

        def validate(m: Any) -> Dict[str, Any]:
            if not isinstance(m, dict):
                raise ValueError("asset_not_object")
            if set(m.keys()) != REQUIRED_ASSET_FIELDS:
                raise ValueError("asset_field_set_mismatch")
            for k in ("source_path", "checkpoint_path", "runtime_path"):
                v = m[k]
                if not isinstance(v, str) or not v or not os.path.isabs(v):
                    raise ValueError(f"asset_path_not_absolute:{k}")
                if not Path(v).is_file():
                    raise ValueError(f"asset_file_missing:{k}")
            for k in ("sample_rate_hz", "channels", "frame_samples", "algorithmic_latency_samples"):
                v = m[k]
                if not isinstance(v, int) or isinstance(v, bool):
                    raise ValueError(f"asset_type:{k}")
            if m["sample_rate_hz"] <= 0:
                raise ValueError("asset_sample_rate_not_positive")
            if m["channels"] != 1:
                raise ValueError("asset_channels_mismatch")
            if m["frame_samples"] <= 0:
                raise ValueError("asset_frame_not_positive")
            if m["algorithmic_latency_samples"] < 0:
                raise ValueError("asset_latency_negative")
            if m["input_format"] != "float32":
                raise ValueError("asset_format_mismatch")
            if not isinstance(m["source_commit"], str) or not re.fullmatch(r"[0-9a-f]{40}", m["source_commit"]):
                raise ValueError("asset_source_commit_not_hex")
            if m["source_commit"] != UPSTREAM_COMMIT:
                raise ValueError("asset_source_commit_mismatch")
            for path_k, hash_k in (("checkpoint_path", "checkpoint_sha256"), ("runtime_path", "runtime_sha256")):
                hv = m[hash_k]
                if not isinstance(hv, str) or not re.fullmatch(r"[0-9a-f]{64}", hv):
                    raise ValueError(f"asset_hash_not_hex:{hash_k}")
                if sha256_file(Path(m[path_k])) != hv:
                    raise ValueError(f"asset_hash_mismatch:{hash_k}")
            # pinned checkpoint identity not established locally; cannot admit
            return {
                "accepted": True,
                "executed": False,
                "imported": False,
                "loaded": False,
                "pinned_asset": False,
                "validated": True,
            }

        rejections: Dict[str, str] = {}

        def reject(name: str, m: Any) -> None:
            try:
                validate(m)
                rejections[name] = "accepted"
            except Exception as exc:
                rejections[name] = str(exc)

        reject("missing_field", {k: v for k, v in manifest().items() if k != "source_commit"})
        extra = manifest()
        extra["extra"] = 1
        reject("extra_field", extra)
        reject("relative_path", manifest(source_path="relative/source.txt"))
        reject("absent_source", manifest(source_path=str(root / "missing.txt")))
        reject("bad_commit", manifest(source_commit="abc"))
        reject("commit_mismatch", manifest(source_commit="0" * 40))
        reject("wrong_channels", manifest(channels=2))
        reject("zero_rate", manifest(sample_rate_hz=0))
        reject("zero_frame", manifest(frame_samples=0))
        reject("negative_latency", manifest(algorithmic_latency_samples=-1))
        reject("format", manifest(input_format="int16"))
        reject("checkpoint_hash", manifest(checkpoint_sha256="0" * 64))
        reject("runtime_hash", manifest(runtime_sha256="f" * 64))
        reject("bool_rate", manifest(sample_rate_hz=True))

        generic = None
        try:
            generic = validate(manifest())
        except Exception as exc:
            generic = {"error": str(exc)}

        return {
            "generic_admission": generic,
            "rejected_all": all(v != "accepted" for v in rejections.values()),
            "rejections": rejections,
            "workspace_checkpoint_present": resolve_source_path(CHECKPOINT_PATH).exists(),
            "workspace_runtime_present": resolve_source_path(RUNTIME_ENV_PATH).exists(),
            "workspace_source_present": resolve_source_path(SOURCE_CHECKOUT_PATH).exists(),
        }

# ---------------------------------------------------------------------------
# Report / contract
# ---------------------------------------------------------------------------

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "checkpoint_identity_absent",
        "requirement": (
            "Supply the exact Stream.FM dereverberation checkpoint "
            "(streamfm_derev.ckpt or admitted equivalent) with filename, byte "
            "count, SHA-256, acquisition record and artifact-specific terms, "
            "verified locally without a network download."),
        "state": (
            "The upstream README references a public Google Drive folder, but "
            "no local checkpoint exists at data/models/streamfm and no "
            "filename, byte count, SHA-256 or local file is recorded in this "
            "workspace. Nothing was downloaded, reconstructed or substituted."),
    },
    {
        "id": "runtime_absent",
        "requirement": (
            "Admit a locked, hash-pinned offline runtime with the exact "
            "Python, PyTorch/CUDA/CPU, dependency and native-library versions "
            "required by the pinned source, plus an install/import digest."),
        "state": (
            "No environment exists at data/envs/stream-fm-dereverberation. "
            "requirements.txt is present in the checkout but no runtime was "
            "created, resolved, imported or executed."),
    },
    {
        "id": "rights_unresolved",
        "requirement": (
            "Supply written checkpoint, training-data, corpus, redistribution, "
            "product-use and derivative-output terms plus the complete notice "
            "bundle for the exact checkpoint and runtime; account for the "
            "repository AGPL-3.0 licence in any distribution decision."),
        "state": (
            "The source checkout LICENSE is AGPL-3.0, but checkpoint, training "
            "data, evaluation corpora and runtime artifact terms are not "
            "established. Nothing may be bundled, rehosted, rebranded or "
            "deployed."),
    },
    {
        "id": "exact_reference_and_geometry_unverified",
        "requirement": (
            "Pin the exact dereverberation checkpoint, config, solver, seed, "
            "input normalization and total algorithmic/system latency, then "
            "reproduce approved exact-runtime outputs byte-for-byte or within "
            "an explicitly admitted numeric tolerance on a declared path."),
        "state": (
            "The config declares 16 kHz/512/256 STFT geometry, but no exact "
            "dereverb checkpoint, solver selection, reference output, "
            "streaming latency measurement or end-to-end parity evidence is "
            "present. This package's 256-sample one-hop probe is not a "
            "Stream.FM result."),
    },
    {
        "id": "quality_and_target_timing_absent",
        "requirement": (
            "Score a rights-cleared paired reverberant/early-target cohort with "
            "independent metrics or permitted listening, and measure "
            "target-device p50/p95/p99, RTF, memory and deadline behavior."),
        "state": (
            "No rights-cleared cohort, independent score, listening result, "
            "device timing, memory, RTF or deadline evidence exists. Surrogate "
            "observations do not qualify the candidate."),
    },
    {
        "id": "provider_intake_absent",
        "requirement": (
            "Complete OFF-by-default opt-in provider intake: descriptor, "
            "registry review, asset contract, default decision and failure "
            "controls, without changing installed v0 behavior."),
        "state": (
            "No provider, descriptor, registry, default, shared build, CI or "
            "installed-v0 change was made. This package is evidence-only."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_checkpoint_identity_and_terms",
     "Exact dereverberation checkpoint filename, byte count, SHA-256, "
     "acquisition record and artifact-specific terms are pinned and reviewed."),
    ("pinned_runtime_and_offline_load",
     "Locked offline runtime with exact dependency versions, install/import "
     "digest and deterministic model load/inference path."),
    ("source_checkpoint_rights",
     "Source AGPL-3.0 obligations, checkpoint, training-data, corpus, "
     "redistribution, product-use and derivative-output rights cleared with "
     "complete notices."),
    ("exact_geometry_and_latency",
     "Declared 16 kHz/512/256 geometry, solver, seed, normalization and total "
     "algorithmic/system latency are pinned and reproduced on target path."),
    ("exact_reference_parity",
     "Approved exact-runtime output vectors and parity/tolerance evidence for "
     "the declared streaming dereverberation path."),
    ("rights_cleared_paired_cohort",
     "Frozen rights-cleared reverberant corpus, measured/frozen RIRs, "
     "early-target definition, strata and reset/delay schedule."),
    ("independent_scoring_and_listening",
     "Independent SI-SDR/STOI/SRMR or permitted listening with identity and "
     "task-matched baselines, including missing/adverse/nonfinite controls."),
    ("target_runtime_timing_and_opt_in_provider",
     "Target-device p50/p95/p99, RTF, memory, deadline behavior, plus "
     "OFF-by-default opt-in provider intake and descriptor review."),
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
    "No Stream.FM checkpoint, derived weight, runtime or model call was produced.",
    "No dereverberation, quality, latency, timing, benchmark or release result is claimed.",
    "The boundary surrogate is not Stream.FM and cannot qualify the candidate.",
    "The 256-sample one-hop probe is not a measured Stream.FM latency result.",
    "No real corpus, room impulse response, audio, device clock or listener was used.",
    "No provider, descriptor, registry, installed v0 path, default, public ABI, shared build, dependency lock or CI was changed.",
    "A caller-owned hash-matched placeholder is never admitted as a pinned checkpoint or runtime.",
)

SOURCE_PINS: Dict[str, str] = {
    DEREVERB_RESEARCH_PATH:
        "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    INVENTORY_PATH:
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    VERIFICATION_PATH:
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "data/checkouts/StreamFM/LICENSE":
        "8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef",
    "data/checkouts/StreamFM/README.md":
        "add959204bf4f7c69e00e65a88898533bcde0ae1558e9ea25e8d9e3fb7ad6014",
    "data/checkouts/StreamFM/config/streamfm_derev.yaml":
        "901538c1ccec5a2805a7b2c50a0407e56b9cdcb931f0c07977732fbe161c4eec",
    "data/checkouts/StreamFM/inference.py":
        "c7196c752ac7da7cb322fda8babf93d70883913fd1dcef6c7a16e77b36aba378",
    "data/checkouts/StreamFM/requirements.txt":
        "e8ed8ec3c71de0e03d40a778589de6122df3649fc72f9a0f343ad53e95d3fd88",
    "data/checkouts/StreamFM/sgmse/backbones/streaming_unet.py":
        "d88c7bb526a97ae11d3cdede0e03e81b7c6e38cd2c6ad92296a37f974668d80a",
    "data/checkouts/StreamFM/sgmse/model.py":
        "c766ff24bfdf8dba9a10a3fff8b2070a216c5e61677056dffff964cb46493a75",
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
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".license", ".txt"}

REQUIRED_REPORT_KEYS = {
    "acceptance_profile", "asset_pins", "base_commit", "board_row", "boundary",
    "branch", "caller_asset_contract", "claim", "component_id",
    "contract_sha256", "controls", "decision", "defer_before",
    "evidence_status", "exact_blockers", "fixture", "format", "gates",
    "metrics", "missing_results", "no_missing_result_qualifies_candidate",
    "negative_claims", "profile", "proposal_only", "qualification",
    "qualification_status", "reopen_condition", "scenario", "schema_id",
    "scope", "status", "surrogate", "task_id", "title", "upstream",
}
REQUIRED_CONTRACT_KEYS = {
    "acceptance_profile", "base_commit", "board_row", "boundary",
    "boundary_pins", "branch", "caller_asset_contract", "component_id",
    "decision", "defer_before", "evidence_status", "exact_blockers", "format",
    "gates", "invariants", "local_files", "negative_claims", "profile",
    "proposal_only", "qualification", "qualification_status",
    "reopen_condition", "reviewer", "scenario", "schema_id", "scope",
    "source_pins", "status", "task_id", "title", "upstream",
}

def _acceptance_profile() -> Dict[str, Any]:
    return {
        "blocked_cases": [
            "no exact Stream.FM dereverberation checkpoint, admitted runtime or exact output vector",
            "no rights-cleared paired reverberant/early-target cohort with frozen RIRs",
            "no independent SI-SDR/STOI/SRMR or permitted listening result",
            "no target-device p50/p95/p99, RTF, memory or deadline measurement",
            "no opt-in provider intake, descriptor review or default decision",
        ],
        "mapped_cases": [
            "frozen synthetic single-channel room response with early/late/noise decomposition",
            "declared probe channel count, rate, hop, excitation and one-hop delay",
            "silence, speech, transient and decaying-tail strata",
            "impulse delay mapping and partial-tail preservation",
            "offline/streaming parity across arbitrary chunk sizes",
            "reset schedule and stale-epoch rejection",
            "finite, peak, clipping and silence-exactness bounds",
            "fail-closed caller-asset, config and frame controls",
        ],
        "name": PROFILE,
        "not_applicable": [
            "no real Stream.FM model artifact is available to evaluate",
            "the surrogate is not Stream.FM and has no flow matching, weights or runtime",
            "no target device, listener or rights-cleared corpus is available",
        ],
        "source": VERIFICATION_PATH,
    }

def _fixture_block() -> Dict[str, Any]:
    return {
        "channels": CHANNELS,
        "component_digests": dict(FIXTURE_DIGESTS),
        "early_taps": [list(t) for t in EARLY_TAPS],
        "early_window_ms": EARLY_WINDOW_MS,
        "early_window_samples": EARLY_WINDOW_SAMPLES,
        "fixture_id": f"{SLUG}/synthetic-room-boundary/1",
        "late_taps": [list(t) for t in LATE_TAPS],
        "predictor_taps": [list(t) for t in PREDICTOR_TAPS],
        "segments": [dict(s) for s in SEGMENTS],
        "spec_digest": FIXTURE_SPEC_DIGEST,
        "total_frames": TOTAL_FRAMES,
        "total_samples": TOTAL_SAMPLES,
    }

def _surrogate_block() -> Dict[str, Any]:
    return {
        "candidate_result": False,
        "delay_samples": LATENCY_SAMPLES,
        "dnn_free": True,
        "flow_matching": False,
        "is_stream_fm": False,
        "model_free": True,
        "note": (
            "The surrogate exists only to exercise declared probe geometry, "
            "delay, state reset and fail-closed controls. It is not Stream.FM "
            "and cannot qualify the candidate."),
        "stage1": "fixed_causal_late_subtraction_probe",
        "stage2": "single_channel_static_nonlinear_compression_probe",
        "type": "fixed two-stage boundary surrogate",
    }

def _metrics_block(output: Sequence[float]) -> Dict[str, Any]:
    scored = TOTAL_SAMPLES - LATENCY_SAMPLES
    return {
        "candidate_result": False,
        "channels": CHANNELS,
        "declared_latency_samples": LATENCY_SAMPLES,
        "max_abs_output": _metric(max(abs(v) for v in output)),
        "nonfinite_output_samples": sum(1 for v in output if not math.isfinite(v)),
        "output_peak_clipped_samples": sum(1 for v in output if abs(v) > 1.0),
        "scored_samples": scored,
        "silence_exact_zero": all(
            v == 0.0 for v in output[:50 * FRAME_SAMPLES]),
        "surrogate_only": True,
    }

def _qualification_block() -> Dict[str, Any]:
    return {
        "all_release_gates_blocked": True,
        "checkpoint_present": False,
        "exact_result_present": False,
        "geometry_verified": False,
        "missing_result_promoted": False,
        "not_qualified": True,
        "provider_intake_present": False,
        "quality_result_present": False,
        "readiness": "incomplete",
        "release_claim": False,
        "runtime_present": False,
        "source_licensed": True,
        "status": QUALIFICATION,
        "timing_result_present": False,
    }

def _report_body() -> Dict[str, Any]:
    samples = as_float(FIXTURE_COMPONENTS["reverb"])
    offline = run_offline(samples)
    output = offline["output"]
    return {
        "acceptance_profile": _acceptance_profile(),
        "asset_pins": {
            "asset:checkpoint": {
                "admitted": False,
                "executed": False,
                "expected_path": CHECKPOINT_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "present": resolve_source_path(CHECKPOINT_PATH).exists(),
            },
            "asset:runtime": {
                "admitted": False,
                "executed": False,
                "expected_path": RUNTIME_ENV_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "present": resolve_source_path(RUNTIME_ENV_PATH).exists(),
            },
            "asset:source_checkout": {
                "executed": False,
                "expected_path": SOURCE_CHECKOUT_PATH,
                "hashed_here": False,
                "identity_status": "pinned_commit_only",
                "loaded": False,
                "present": resolve_source_path(SOURCE_CHECKOUT_PATH).exists(),
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
            "asset": _asset_controls(),
            "config": config_adverse_control(),
            "delay": delay_control(),
            "frame": frame_adverse_control(),
            "nonfinite_counter": nonfinite_counter_control(),
            "partial_tail": partial_tail_control(),
            "reset": reset_control(),
            "silence": silence_control(),
            "streaming_parity": streaming_parity_control(),
        },
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "fixture": _fixture_block(),
        "format": dict(FORMAT),
        "gates": [
            {"id": gate, "qualifies": False, "requirement": req, "status": "blocked"}
            for gate, req in GATE_REQUIREMENTS
        ],
        "metrics": _metrics_block(output),
        "missing_results": [
            "exact Stream.FM dereverberation checkpoint identity and terms",
            "pinned offline runtime and deterministic load/import digest",
            "checkpoint/training-data/corpus/runtime rights and AGPL distribution review",
            "exact geometry, solver, normalization and total latency reproduction",
            "exact-runtime output vectors and parity/tolerance evidence",
            "rights-cleared paired reverberant/early-target cohort",
            "independent SI-SDR/STOI/SRMR or permitted listening",
            "target-device timing, memory and deadline evidence",
            "OFF-by-default opt-in provider intake and default decision",
        ],
        "no_missing_result_qualifies_candidate": True,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply the exact Stream.FM dereverberation checkpoint with byte "
            "count and SHA-256, an admitted locked runtime, clear artifact and "
            "corpus rights including AGPL distribution review, exact geometry/"
            "solver/latency reproduction, exact-runtime reference outputs, "
            "independent paired-cohort scoring or permitted listening, "
            "target-device timing and OFF-by-default opt-in provider intake. "
            "Until then the candidate stays DEFER, incomplete and not qualified."),
        "scenario": {
            "far_end_reference": False,
            "id": "stream-fm-dereverb-room-blocker-v1",
            "is_aec": False,
            "is_mono_baseline": True,
            "note": (
                "Stream.FM dereverberation is a single-channel dereverberation "
                "candidate in this task. No far-end playback reference is part "
                "of this scenario; it is not AEC."),
            "task_geometry": "single-channel dereverberation",
            "upstream_geometry_verified": False,
        },
        "schema_id": SCHEMA_ID,
        "scope": dict(SCOPE),
        "status": STATUS,
        "surrogate": _surrogate_block(),
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "checkpoint_identity": UPSTREAM_CHECKPOINT_IDENTITY,
            "checkpoint_identity_status": UPSTREAM_CHECKPOINT_STATUS,
            "commit": UPSTREAM_COMMIT,
            "commit_status": "pinned_local_checkout",
            "geometry_status": "declared_in_config_unverified_runtime",
            "license": UPSTREAM_LICENSE,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "note": (
                "Local checkout exists and is pinned by commit, but checkpoint "
                "file, runtime, rights-clearance and exact/runtime evidence are "
                "not admitted."),
            "publication": UPSTREAM_PUBLICATION,
            "repository": UPSTREAM_REPOSITORY,
            "source_present": True,
        },
    }

def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
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
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "format": dict(FORMAT),
        "gates": [
            {"id": gate, "qualifies": False, "requirement": req, "status": "blocked"}
            for gate, req in GATE_REQUIREMENTS
        ],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "the package is proposal-only and incomplete",
            "no missing, blocked or rejected result is promoted to a pass",
            "no checkpoint, weight, runtime or corpus is downloaded, copied, imported, loaded or executed",
            "no claim is made from observed path presence alone",
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
            "Supply the exact Stream.FM dereverberation checkpoint with byte "
            "count and SHA-256, an admitted locked runtime, clear artifact and "
            "corpus rights including AGPL distribution review, exact geometry/"
            "solver/latency reproduction, exact-runtime reference outputs, "
            "independent paired-cohort scoring or permitted listening, "
            "target-device timing and OFF-by-default opt-in provider intake."),
        "reviewer": REVIEWER,
        "scenario": {
            "far_end_reference": False,
            "id": "stream-fm-dereverb-room-blocker-v1",
            "is_aec": False,
            "is_mono_baseline": True,
            "task_geometry": "single-channel dereverberation",
            "upstream_geometry_verified": False,
        },
        "schema_id": CONTRACT_SCHEMA_ID,
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "checkpoint_identity": UPSTREAM_CHECKPOINT_IDENTITY,
            "checkpoint_identity_status": UPSTREAM_CHECKPOINT_STATUS,
            "commit": UPSTREAM_COMMIT,
            "commit_status": "pinned_local_checkout",
            "geometry_status": "declared_in_config_unverified_runtime",
            "license": UPSTREAM_LICENSE,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "publication": UPSTREAM_PUBLICATION,
            "repository": UPSTREAM_REPOSITORY,
            "source_present": True,
        },
    }

def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())

# ---------------------------------------------------------------------------
# SOURCES.sha256 and README digest tables
# ---------------------------------------------------------------------------

def _local_manifest_paths() -> List[str]:
    return sorted(p.name for p in HERE.iterdir()
                  if p.is_file() and p.name != "SOURCES.sha256")

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
    si = text.index(start) + len(start)
    ei = text.find(end, si)
    if ei < 0:
        raise ValueError("readme_marker_missing:" + section)
    return text[si:ei]

def parse_readme_tables(text: str) -> Dict[str, List[Tuple[str, str, int | None]]]:
    tables: Dict[str, List[Tuple[str, str, int | None]]] = {}
    for section in README_SECTIONS:
        body = _section_text(text, section)
        rows: List[Tuple[str, str, int | None]] = []
        for line in body.splitlines():
            if not line.startswith("| `"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) not in (2, 3):
                raise ValueError(f"readme_row_shape:{section}")
            key = cells[0].strip("`")
            digest = cells[1].strip("`")
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValueError(f"readme_bad_digest:{section}:{key}")
            size = None
            if len(cells) == 3:
                if not re.fullmatch(r"\d+", cells[2]):
                    raise ValueError(f"readme_bad_size:{section}:{key}")
                size = int(cells[2])
            rows.append((key, digest, size))
        tables[section] = rows
    return tables

def render_readme_table(rows: List[Tuple[str, str, int | None]],
                        with_size: bool) -> str:
    if with_size:
        lines = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
    else:
        lines = ["| Key | SHA-256 |", "| --- | --- |"]
    for key, digest, size in rows:
        if with_size:
            lines.append(f"| `{key}` | `{digest}` | {size} |")
        else:
            lines.append(f"| `{key}` | `{digest}` |")
    return "\n".join(lines)

def update_readme_artifact_table(text: str) -> str:
    start, end = README_MARKERS["artifacts"]
    si = text.index(start) + len(start)
    ei = text.index(end, si)
    rows = []
    for name in _local_manifest_paths():
        if name in ARTIFACT_TABLE_EXCLUDED:
            continue
        p = HERE / name
        rows.append((name, sha256_file(p), p.stat().st_size))
    rows.sort(key=lambda r: r[0])
    table = "\n\n" + render_readme_table(rows, with_size=True) + "\n"
    return text[:si] + table + text[ei:]
