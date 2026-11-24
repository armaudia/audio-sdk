# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen synthetic fixture table for the Rate acceptance profile.

Every stimulus is analytic and regenerated from a fixed formula in
``reference.py``. No recording, corpus, model, download, device or licensed
runtime is involved. The cases below enumerate both the scored paths and the
explicit invalid/missing/nonfinite/adverse controls; no missing result is
promoted to a scored outcome.
"""

from __future__ import annotations

from typing import Any, Dict, List

import reference

STIMULI = ("silence", "speech_like", "music_like", "tonal", "pause_policy")
PROFILE_STIMULUS = "speech_like"
C_VECTOR_STIMULUS = "c_vector"

SCHEDULES: Dict[str, tuple[tuple[int, float], ...]] = {
    "identity_1x": reference.IDENTITY_SCHEDULE,
    "fixed_1_25": reference.FIXED_SCHEDULE,
    "slow_0_75": reference.SLOW_SCHEDULE,
    "dynamic_rate": reference.DYNAMIC_SCHEDULE,
    "drift": reference.DRIFT_SCHEDULE,
    "rebuffer": reference.REBUFFER_SCHEDULE,
    "pause_policy": reference.PAUSE_POLICY_SCHEDULE,
}

CONTROL_CASES: List[Dict[str, str]] = [
    {"case_id": "identity_1x_control", "category": "control",
     "expectation": "bit-exact source copy; duration error zero; pitch ratio 1.0"},
    {"case_id": "fixed_rate_reference", "category": "control",
     "expectation": "constant 1.25x caller-clock duration mapping; pitch proxy preserved"},
    {"case_id": "slow_rate_reference", "category": "control",
     "expectation": "constant 0.75x whole-clip expansion; not expressible in installed v0 frames"},
    {"case_id": "varispeed_adverse_control", "category": "adverse",
     "expectation": "linear resampling shifts pitch; must not be scored as pitch-preserving TSM"},
    {"case_id": "unsmoothed_rate_step", "category": "adverse",
     "expectation": "larger local adjacent-delta proxy than the slewed candidate at each rate change"},
    {"case_id": "silence", "category": "control",
     "expectation": "finite bounded zero-valued output with exact duration mapping"},
    {"case_id": "nonfinite_input", "category": "invalid",
     "expectation": "rejected with nonfinite_input and unchanged state"},
    {"case_id": "out_of_range_input", "category": "invalid",
     "expectation": "rejected with out_of_range and unchanged state"},
    {"case_id": "wrong_shape", "category": "malformed",
     "expectation": "rejected with wrong_shape; 160-sample v0 frame shape enforced"},
    {"case_id": "wrong_position", "category": "malformed",
     "expectation": "rejected with wrong_position; contiguous source positions enforced"},
    {"case_id": "wrong_epoch", "category": "malformed",
     "expectation": "rejected with wrong_epoch; stale session state cannot be reused"},
    {"case_id": "process_after_final", "category": "malformed",
     "expectation": "rejected with process_after_final; no input after final flag"},
    {"case_id": "drain_before_final", "category": "missing",
     "expectation": "rejected with missing_final_input; no missing tail promoted to content"},
    {"case_id": "missing_rate_selection", "category": "missing",
     "expectation": "rejected with missing_rate_selection; no implicit default rate"},
    {"case_id": "invalid_config", "category": "invalid",
     "expectation": "rejected with invalid_config; closed configuration schema"},
    {"case_id": "rate_out_of_range", "category": "invalid",
     "expectation": "rejected with rate_out_of_range outside the 0.75-1.5 clamp"},
    {"case_id": "nonfinite_rate", "category": "nonfinite",
     "expectation": "rejected with nonfinite_rate; NaN rate never advances the clock"},
]

PROFILE_DIMENSIONS: List[Dict[str, str]] = [
    {"dimension": "source/output mapping", "evidence": "duration_mapping,rate_updates",
     "scope": "source-sample coordinates; synthetic caller-owned output clock"},
    {"dimension": "duration", "evidence": "duration_mapping,pause_policy,drift_rebuffer",
     "scope": "whole-sample target lengths at 1x and rate changes"},
    {"dimension": "pitch preservation", "evidence": "steady_state.frequency_scale",
     "scope": "220 Hz analytic tone and Goertzel ratio; no listening claim"},
    {"dimension": "transient proxies", "evidence": "transient_behavior",
     "scope": "adjacent-delta and peak-retention proxies only"},
    {"dimension": "playback buffering", "evidence": "streaming,final_partial,c_boundary_expected",
     "scope": "160-sample frames, underrun reporting, drain padding and final partial window"},
    {"dimension": "unfamiliar speech/music surrogates", "evidence": "stimuli,variants",
     "scope": "analytic speech-like pulses and chord/click surrogate; not real speech or music"},
    {"dimension": "silence", "evidence": "stimuli.silence,duration_mapping.silence",
     "scope": "zero-valued analytic control"},
    {"dimension": "rebuffer and drift", "evidence": "drift_rebuffer",
     "scope": "frozen step schedules at source sample timestamps"},
    {"dimension": "pause/filler decisions", "evidence": "pause_policy",
     "scope": "voiced/pause schedule anchored to source samples, never output time"},
    {"dimension": "speech preservation", "evidence": "variants.speech_like,transient_behavior.speech_like",
     "scope": "finite bounded surrogate waveform and event-retention proxy; no intelligibility claim"},
]


def stimuli() -> Dict[str, List[float]]:
    """Regenerate the frozen fixture set; lengths are part of the pin."""
    return {
        name: reference.analytic_stimulus(
            name, reference.PAUSE_POLICY_LENGTH if name == "pause_policy"
            else reference.STIMULUS_LENGTH)
        for name in STIMULI
    }


def c_vector() -> List[float]:
    """Integer-exact pattern shared with the opt-in C consumer."""
    return list(reference.analytic_stimulus(C_VECTOR_STIMULUS))


def cases() -> List[Dict[str, str]]:
    return [dict(row) for row in CONTROL_CASES]


def catalog() -> Dict[str, Any]:
    frozen = stimuli()
    return {
        "kind": "synthetic analytic fixtures only",
        "sample_rate_hz": reference.SAMPLE_RATE_HZ,
        "frame_samples": reference.FRAME_SAMPLES,
        "stimulus_names": list(STIMULI),
        "stimulus_lengths": {name: len(values) for name, values in frozen.items()},
        "stimulus_stats": {name: reference.finite_stats(values)
                           for name, values in frozen.items()},
        "c_vector_length": len(c_vector()),
        "schedules": {name: [[start, rate] for start, rate in schedule]
                      for name, schedule in SCHEDULES.items()},
        "profile_dimensions": PROFILE_DIMENSIONS,
        "cases": cases(),
        "source_timestamps": "every rate boundary is a source sample index; output time is derived",
        "real_assets": False,
        "missing_result_promoted": False,
    }


if __name__ == "__main__":
    print(reference.canonical_json(catalog()))
