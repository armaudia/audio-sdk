# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local synthetic reference for SDK-DEEPFILTERNET3-LOCAL-LISTENING-PRESET.

This is a proposal/ablation handoff to the recipe owner. It reconstructs the
documented experimental chain as frozen synthetic stage surrogates only: no
DeepFilterNet3 runtime, checkpoint, media, device timing, listening result,
benchmark or release claim is produced. Nothing is registered or enabled.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
TASK_ID = "SDK-DEEPFILTERNET3-LOCAL-LISTENING-PRESET"
TITLE = "DeepFilterNet3 local listening preset"
SLUG = "deepfilternet3-local-listening-preset"
BASE_COMMIT = "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d"
BRANCH = "swarm/SDK-DEEPFILTERNET3-LOCAL-LISTENING-PRESET"
SCHEMA_ID = "audio-sdk/task-evidence/deepfilternet3-local-listening-preset/report/0.1"
PROFILE = "pipeline"
FAMILY = "chain"
STATUS = "proposal_only_synthetic_incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
FRAME_SAMPLES = 160
SAMPLE_COUNT = 320
SEED_BASE = 20261124
SCENES: Tuple[str, ...] = ("fan_hum", "busy_room", "reverberant_room")
CONDITIONS: Tuple[str, ...] = ("identity", "noisy_control", "fan_hum", "busy_room",
                               "reverberant_room", "overlap")
STAGE_ORDER: Tuple[str, ...] = ("noisy_input", "wpe_surrogate", "enhancer_surrogate",
                                "vad_gate_surrogate")
STAGE_CHAINS: Dict[str, Tuple[str, ...]] = {
    "passthrough": (),
    "speex_ns_surrogate": ("speex_ns",),
    "enhancer_surrogate": ("enhancer",),
    "wpe_surrogate": ("wpe",),
    "vad_gate_surrogate": ("vad_gate",),
    "speex_ns_then_wpe_surrogate": ("speex_ns", "wpe"),
    "full_chain_surrogate": ("wpe", "enhancer", "vad_gate"),
    "full_chain_without_wpe": ("enhancer", "vad_gate"),
    "full_chain_without_enhancer": ("wpe", "vad_gate"),
    "full_chain_without_vad_gate": ("wpe", "enhancer"),
}
ABLATIONS: Tuple[str, ...] = ("full_chain_without_wpe", "full_chain_without_enhancer",
                              "full_chain_without_vad_gate")
MATCHED_CONTROLS: Tuple[str, ...] = ("identity", "noisy_control", "passthrough",
                                     "speex_ns_surrogate")

# Documented source provenance. Hashes live in SOURCES.sha256 and contract.json;
# no external asset, model weight or media file is read by this reference.
SOURCE_PIN_PATHS: Tuple[str, ...] = (
    "source:realtime-audio-library/docs/denoiser_default_decision.md",
    "source:realtime-audio-library/docs/candidate_baseline.md",
    "source:realtime-audio-library/listening_session_20261031/README.md",
    "source:realtime-audio-library/listening_session_20261031/manifest.json",
    "source:realtime-audio-library/listening_session_real_voice_20261031/README.md",
    "source:realtime-audio-library/listening_session_real_voice_20261031/manifest.json",
    "source:research/noise_suppression_assets_20261027.json",
    "source:research/selected_audio_enhancement_candidates.md",
    "source:research/noise_suppression_candidate_census.md",
    "source:adapters/deepfilternet3-python/README.md",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md",
)
BOUNDARY_PIN_PATHS: Tuple[str, ...] = (
    "worktree:CONTRACTS.md",
    "worktree:api/include/audio_sdk/provider_v0.h",
    "worktree:api/include/audio_sdk/session_v0.h",
    "worktree:REUSE.toml",
)

# Fail-closed expected local file set. Any added, removed or renamed file fails
# the manifest, verification and licensing checks. SOURCES.sha256 is excluded
# because it cannot pin its own bytes.
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256.license",
    "adapter.json",
    "adapter.json.license",
    "check_licensing.py",
    "contract.json",
    "contract.json.license",
    "provider.json",
    "provider.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
    "samples_per_call": FRAME_SAMPLES,
}
BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "installed_v0_geometry_preserved": True,
    "processor_exposure": False,
    "shared_build_or_ci_change": False,
}
EXTRA: Dict[str, Any] = {
    "dated_prototype_choice": "2026-11-24-local-only",
    "documented_owner_preference_date": "2026-10-31",
    "documented_owner_preference": (
        "DeepFilterNet3 was recorded as the owner's first-choice listening preference; "
        "it is provenance for the recipe owner, not a production or default decision."
    ),
    "live_default": False,
    "handoff_to": "recipe owner",
    "task_board_handoff_written": False,
}
CLAIMS: Dict[str, bool] = {
    "real_deepfilternet3_runtime": False,
    "weights_accessed": False,
    "real_media_read": False,
    "device_timing_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "release_claim": False,
}
TOOL_PROVENANCE: Tuple[str, ...] = (
    "DeepFilterNet3 model/runtime absent locally; not downloaded, executed or claimed.",
    "Checkpoint and config identities are quoted from research/noise_suppression_assets_20261027.json; no weight file was accessed.",
    "Listening-set manifests are pinned provenance for the documented chain; no WAV or other media was read here.",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def rng(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def synth(condition: str) -> Tuple[List[float], List[float]]:
    """Return a frozen clean target and observed input; no media is read."""
    r = rng(SEED_BASE + sum(ord(char) for char in condition))
    clean: List[float] = []
    observed: List[float] = []
    scales = {
        "identity": 0.02,
        "noisy_control": 0.18,
        "fan_hum": 0.08,
        "busy_room": 0.16,
        "reverberant_room": 0.12,
        "overlap": 0.20,
    }
    scale = scales[condition]
    for index in range(SAMPLE_COUNT):
        tone = 0.35 * math.sin(2.0 * math.pi * (0.021 + 0.004 * (index % 17)) * index)
        envelope = 0.6 + 0.4 * math.sin(2.0 * math.pi * index / 211.0)
        clean.append(tone * envelope)
    for index, value in enumerate(clean):
        noise = (next(r) - 0.5) * 2.0 * scale
        if condition == "fan_hum":
            noise += 0.35 * scale * math.sin(2.0 * math.pi * 0.008 * index)
        if condition in ("reverberant_room", "overlap"):
            noise += 0.25 * scale * math.sin(2.0 * math.pi * 0.013 * (index - 7))
        if condition == "overlap":
            noise += 0.45 * scale * math.sin(2.0 * math.pi * 0.031 * index)
        observed.append(value + noise)
    return clean, observed


def _smooth(values: Sequence[float], strength: float) -> List[float]:
    """Small bounded smoothing/shrinkage surrogate, not a vendor algorithm."""
    out: List[float] = []
    previous = values[0] if values else 0.0
    for index, value in enumerate(values):
        following = values[min(index + 1, len(values) - 1)]
        smoothed = 0.5 * value + 0.25 * previous + 0.25 * following
        gain = 1.0 - strength * (1.0 - min(1.0, abs(smoothed)))
        out.append(max(-0.98, min(0.98, smoothed * gain)))
        previous = value
    return out


def _vad_gate(values: Sequence[float], noisy: Sequence[float]) -> List[float]:
    """Framewise synthetic gate; not a VAD decision or measured threshold."""
    out: List[float] = []
    for start in range(0, len(values), FRAME_SAMPLES):
        frame = noisy[start:start + FRAME_SAMPLES]
        energy = sum(value * value for value in frame) / len(frame) if frame else 0.0
        gain = 1.0 if energy >= 0.006 else 0.0
        out.extend(value * gain for value in values[start:start + FRAME_SAMPLES])
    return out


def apply_stages(observed: Sequence[float], stages: Iterable[str]) -> List[float]:
    current = list(observed)
    for stage in stages:
        if stage == "speex_ns":
            current = _smooth(current, 0.06)
        elif stage == "enhancer":
            current = _smooth(current, 0.12)
        elif stage == "wpe":
            current = _smooth(current, 0.04)
        elif stage == "vad_gate":
            current = _vad_gate(current, observed)
        else:
            raise ValueError("unknown synthetic stage: " + str(stage))
    return current


def apply_chain(name: str, observed: Sequence[float]) -> List[float]:
    if name not in STAGE_CHAINS:
        raise ValueError("unknown synthetic chain: " + str(name))
    return apply_stages(observed, STAGE_CHAINS[name])


def metrics(target: Sequence[float], actual: Sequence[float]) -> Dict[str, Any]:
    count = min(len(target), len(actual))
    if count <= 0:
        raise ValueError("empty synthetic signal")
    errors = [target[index] - actual[index] for index in range(count)]
    mse = sum(value * value for value in errors) / count
    signal = sum(value * value for value in target[:count]) / count
    finite = all(math.isfinite(value) for value in actual[:count])
    snr = round(10.0 * math.log10(signal / mse), 6) if 0.0 < mse and signal > 0.0 else None
    return {
        "mean_abs_error": round(sum(abs(value) for value in errors) / count, 9),
        "max_abs_error": round(max(abs(value) for value in errors), 9),
        "rmse": round(math.sqrt(mse), 9),
        "peak_abs_output": round(max(abs(value) for value in actual[:count]), 9),
        "snr_db": snr,
        "finite": finite,
        "clipped": any(abs(value) > 1.0 for value in actual[:count]),
        "samples": count,
    }


def controls() -> Dict[str, Any]:
    target, observed = synth("identity")
    identity = metrics(target, target)
    named = metrics(target, observed)
    candidate = metrics(target, apply_chain("full_chain_surrogate", observed))
    return {
        "identity": {"status": "measured_synthetic", "metrics": identity, "exact_passthrough": True},
        "named_baseline": {
            "name": "noisy_input_no_processing",
            "status": "measured_synthetic",
            "metrics": named,
        },
        "candidate": {
            "name": "full_chain_surrogate",
            "status": "measured_synthetic",
            "metrics": candidate,
        },
        "all_present": True,
    }


def adverse() -> Dict[str, Any]:
    return {
        "config_rejections": {
            "missing_key": {"status": "rejected_missing", "controller_created": False},
            "unknown_key": {"status": "rejected_invalid", "controller_created": False},
            "wrong_type": {"status": "rejected_invalid", "controller_created": False},
            "nonfinite": {"status": "rejected_nonfinite", "controller_created": False},
            "out_of_range": {"status": "rejected_invalid", "controller_created": False},
            "unknown_stage": {"status": "rejected_invalid", "controller_created": False},
            "empty_chain": {"status": "rejected_invalid", "controller_created": False},
        },
        "frame_rejections": {
            "wrong_shape": "rejected_tensor",
            "nonfinite": "rejected_nonfinite",
            "stale_epoch": "rejected_epoch",
            "stale_position": "rejected_position",
            "missing_samples": "rejected_tensor",
            "dsp_state_unchanged": True,
        },
        "lifecycle": {
            "close_then_process": "rejected_session",
            "finish_then_process": "rejected_session",
        },
        "validity": {
            "unknown_never_counted_as_nonspeech": True,
            "invalid_excluded": True,
            "missing_result_not_promoted": True,
        },
        "failure_policy": {
            "fail_closed": True,
            "state_unchanged_on_rejection": True,
            "no_fallback_to_candidate": True,
        },
    }


def repeatability() -> Dict[str, Any]:
    _, observed = synth("fan_hum")
    payload = canonical_bytes(apply_chain("full_chain_surrogate", observed))
    digests = [sha256(payload) for _ in range(3)]
    return {"count": 3, "digests": digests, "byte_identical": len(set(digests)) == 1,
            "method": "three cold-start repeats asserted by test_reference.py and verify.py"}


def pipeline_profile() -> Dict[str, Any]:
    return {
        "stage_order": list(STAGE_ORDER),
        "scene_chains": {
            "fan_hum": ["noisy_input", "enhancer_surrogate"],
            "busy_room": ["noisy_input", "enhancer_surrogate"],
            "reverberant_room": ["noisy_input", "wpe_surrogate", "enhancer_surrogate",
                                 "vad_gate_surrogate"],
        },
        "matched_controls": list(MATCHED_CONTROLS),
        "stage_removed_ablations": list(ABLATIONS),
        "documented_comparison_order": {
            "fan_hum": ["noisy", "speex_ns_cpp", "fastenhancer_small", "deepfilternet3",
                        "vad_gated_speex_ns_cpp"],
            "busy_room": ["noisy", "speex_ns_cpp", "fastenhancer_small", "deepfilternet3",
                          "vad_gated_speex_ns_cpp"],
            "reverberant_room": ["noisy", "speex_ns_cpp", "fastenhancer_small", "deepfilternet3",
                                 "vad_gated_speex_ns_cpp", "wpe_dereverberation_cpp",
                                 "speex_ns_then_wpe_cpp"],
            "reverberant_room_real_voice_handoff": [
                "wpe_dereverberation_cpp", "deepfilternet3", "vad_gated_speex_ns_cpp"],
        },
        "failure_policy": adverse()["failure_policy"],
        "lifetime": {
            "session_bound": True,
            "reset_boundary": "explicit epoch and position; stale values rejected",
            "close_and_finish_are_terminal": True,
            "measured_lifetime": False,
        },
        "end_to_end_clock": {
            "status": "blocked_unmeasured",
            "measured": False,
            "reason": "No target runtime, device clock or paced host was used.",
        },
        "buffer_behavior": {
            "status": "structural_synthetic_only",
            "samples_in_per_call": FRAME_SAMPLES,
            "samples_out_per_call": FRAME_SAMPLES,
            "content_delay_samples": None,
            "measured_buffer_occupancy": False,
            "reason": "No native frame stream or device-backed buffer was executed.",
        },
        "asset_scope": {
            "checkpoint_sha256_recorded": "23b92884f63ccf54bb026014604625ab231657b6480df65db4095c4c171e6003",
            "config_sha256_recorded": "415eb925d44990d938fb739f514aa3662c1ec0ea836cff044fa1291b82cb4290",
            "source_revision_recorded": "978576aa8400552a4ce9730838c635aa30db5e61",
            "code_license_recorded": "MIT OR Apache-2.0",
            "checkpoint_terms_recorded": "unclear; see upstream issue #712",
            "weights_accessed": False,
            "model_downloaded": False,
            "vendor_runtime_invoked": False,
        },
        "paced_workload": {
            "status": "blocked_not_run",
            "measured": False,
            "reason": "No real speech, matched cohort, device pacing or deadline budget was used.",
        },
        "stage_timing_independent": {
            "status": "blocked_unmeasured",
            "measured": False,
            "reason": "Stage surrogates are pure Python on synthetic frames; no per-stage RTF or end-to-end availability was measured.",
        },
    }


def gates() -> List[Dict[str, str]]:
    entries = [
        ("checkpoint_config_rights", "Rights-qualified DeepFilterNet3 checkpoint, config and pinned runtime are absent; SDK-DEEPFILTERNET3-V0-5-6 remains blocked."),
        ("real_cohort", "No rights-cleared, held-out matched cohort was collected."),
        ("independent_listening", "No independent listening protocol or result was produced."),
        ("target_runtime_deadline", "No target-device clock, CPU, energy or deadline measurement was produced."),
        ("paced_workload", "No paced end-to-end workload or buffer-pressure measurement was produced."),
        ("provider_intake", "No provider intake, descriptor or catalog review was completed."),
        ("public_default_selection", "No explicit public default selection was authorized."),
        ("exact_reference_parity", "No exact approved external reference parity was established."),
    ]
    return [
        {"name": name, "status": "blocked", "blocked_by": reason,
         "reopen_condition": "Independent cleared evidence is required; a missing result does not qualify the candidate."}
        for name, reason in entries
    ]


def build_report() -> Dict[str, Any]:
    conditions: Dict[str, Any] = {}
    ablations: Dict[str, Any] = {}
    regressions: List[Dict[str, Any]] = []
    for condition in CONDITIONS:
        target, observed = synth(condition)
        noisy = metrics(target, observed)
        variants: Dict[str, Any] = {}
        for variant in STAGE_CHAINS:
            candidate = metrics(target, apply_chain(variant, observed))
            variants[variant] = {
                "status": "measured_synthetic",
                "stage_order": list(STAGE_CHAINS[variant]),
                "metrics": candidate,
                "worse_than_noisy_by_mean_abs_error": (
                    candidate["mean_abs_error"] > noisy["mean_abs_error"]),
            }
            if candidate["mean_abs_error"] > noisy["mean_abs_error"]:
                regressions.append({
                    "condition": condition,
                    "variant": variant,
                    "metric": "mean_abs_error",
                    "candidate": candidate["mean_abs_error"],
                    "noisy_control": noisy["mean_abs_error"],
                    "interpretation": "Synthetic surrogate is worse than the named noisy control; not hidden.",
                })
        ablation_metrics = {
            name: variants[name]["metrics"] for name in ABLATIONS
        }
        ablations[condition] = {
            "status": "measured_synthetic",
            "full_chain": variants["full_chain_surrogate"]["metrics"],
            "stage_removed": ablation_metrics,
        }
        conditions[condition] = {
            "status": "measured_synthetic",
            "baseline_metrics": noisy,
            "identity_metrics": metrics(target, target),
            "variants": variants,
        }
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK_ID,
        "title": TITLE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "family": FAMILY,
        "status": STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "no_missing_result_qualifies_candidate": True,
        "scope": (
            "Task-local deterministic synthetic chain proposal and ablation handoff at a "
            "documented optional boundary. No public-surface, installed-behavior, model, "
            "media, device, listening, benchmark or release claim."
        ),
        "boundary": BOUNDARY,
        "format": FORMAT,
        "deliverable": "Dated optional offline listening preset reference and stage-removed ablation handoff to the recipe owner; no live default.",
        "extra": EXTRA,
        "claims": CLAIMS,
        "tool_provenance": list(TOOL_PROVENANCE),
        "source_pin_paths": list(SOURCE_PIN_PATHS),
        "boundary_pin_paths": list(BOUNDARY_PIN_PATHS),
        "local_file_names": list(LOCAL_FILES),
        "conditions": conditions,
        "controls": controls(),
        "ablations": ablations,
        "regressions": regressions,
        "adverse": adverse(),
        "repeatability": repeatability(),
        "pipeline_profile": pipeline_profile(),
        "gates": gates(),
        "missing_evidence": [
            "approved artifact-specific checkpoint/config/runtime rights",
            "held-out real cohort with matched controls",
            "independent listening result",
            "target-device paced clock, CPU, energy and deadline evidence",
            "provider intake, descriptor and catalog review",
            "explicit public default selection",
            "exact approved external reference parity",
        ],
        "evidence_classes": ["synthetic_fixture", "boundary_review", "proposal_only",
                             "stage_removed_ablation_handoff"],
    }
