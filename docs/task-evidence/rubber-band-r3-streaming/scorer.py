# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Score the deterministic synthetic streaming TSM fixtures.

No result in this module promotes a candidate. Missing, rejected, nonfinite and
adverse results are recorded explicitly and are always `qualifies=false`.
"""

from __future__ import annotations

import math
import platform
import sys
from typing import Sequence

import fixture
import reference as ref


VARIANT_LABELS = {
    "identity_1x_control": "control",
    "fixed_rate_ola_baseline": "control",
    "candidate_dynamic_wsola_ola": "scored",
    "alignment_disabled_control": "control",
    "unsmoothed_step_adverse": "adverse_control",
    "varispeed_adverse": "adverse_control",
    "source_timestamp_policy": "scored",
    "drift_control": "control",
    "rebuffer_control": "control",
}


def variant_row(values: Sequence[float], *, label: str,
                schedule: Sequence[tuple[int, float]] = ref.DYNAMIC_SCHEDULE,
                parameters: dict | None = ref.DEFAULT_SETTINGS,
                alignment: bool = True, slew: bool = True,
                varispeed: bool = False) -> dict:
    stats = ref.finite_stats(values)
    if varispeed:
        output, sources = ref.varispeed_run(values, 1.25)
        stream = None
    else:
        output, sources, stream = ref.run_tsm(
            values, schedule=schedule, parameters=parameters,
            alignment=alignment, slew=slew,
            chunk_size=len(values) + ref.FRAME_SAMPLES)
    output_stats = ref.finite_stats(output)
    expected = (len(values) / 1.25 if varispeed
                else ref.expected_duration(schedule, len(values)))
    error = len(output) - expected
    row = {
        "status": VARIANT_LABELS[label],
        "label": label,
        "schedule": [[start, rate] for start, rate in schedule],
        "parameters": {key: parameters[key] for key in
                       ("grain_samples", "overlap_samples", "density")}
        if parameters else None,
        "alignment_search": alignment and not varispeed,
        "bounded_slew": slew and not varispeed,
        "source_samples": len(values),
        "input_digest": stats["digest"],
        "output_samples": output_stats["samples"],
        "output_digest": output_stats["digest"],
        "nonfinite_count": output_stats["nonfinite_count"],
        "clipping_count": output_stats["clipping_count"],
        "peak_abs": output_stats["peak_abs"],
        "expected_output_samples": expected,
        "duration_error_samples": error,
        "relative_duration_error": error / expected,
        "effective_rate": len(values) / len(output) if output else None,
        "source_map_digest": ref.tensor_digest(float(value) for value in sources),
        "source_map": ref.source_map_stats(sources) if sources else None,
        "segments": stream.segments if stream else 0,
        "rate_updates": len(stream.rate_updates) if stream else 0,
        "max_applied_rate_step": max(
            (abs(item["applied_step"]) for item in stream.rate_updates),
            default=0.0) if stream else None,
        "alignment_shift_min": min(stream.alignment_deltas)
        if stream and stream.alignment_deltas else 0,
        "alignment_shift_max": max(stream.alignment_deltas)
        if stream and stream.alignment_deltas else 0,
        "qualifies": False,
    }
    return row


def variant_bundle(stimuli: dict[str, Sequence[float]]) -> dict:
    bundle = {}
    for name, values in stimuli.items():
        bundle[name] = {
            "identity_1x_control": variant_row(
                values, label="identity_1x_control",
                schedule=ref.IDENTITY_SCHEDULE),
            "fixed_rate_ola_baseline": variant_row(
                values, label="fixed_rate_ola_baseline",
                schedule=ref.FIXED_SCHEDULE,
                parameters=ref.FIXED_BASELINE_SETTINGS),
            "candidate_dynamic_wsola_ola": variant_row(
                values, label="candidate_dynamic_wsola_ola"),
            "alignment_disabled_control": variant_row(
                values, label="alignment_disabled_control", alignment=False),
            "unsmoothed_step_adverse": variant_row(
                values, label="unsmoothed_step_adverse", slew=False),
            "varispeed_adverse": variant_row(
                values, label="varispeed_adverse", varispeed=True),
            "source_timestamp_policy": variant_row(
                values, label="source_timestamp_policy",
                schedule=ref.POLICY_SCHEDULE),
            "drift_control": variant_row(
                values, label="drift_control", schedule=ref.DRIFT_SCHEDULE),
            "rebuffer_control": variant_row(
                values, label="rebuffer_control", schedule=ref.REBUFFER_SCHEDULE),
        }
    return bundle


def frequency_evidence(stimuli: dict[str, Sequence[float]]) -> dict:
    values = stimuli["tonal"]
    analysis = {"start": 512, "count": 2048}
    reference = ref.dominant_frequency(values, **analysis)
    runs = {
        "identity_1x_control": ref.identity_run(values)[0],
        "fixed_rate_ola_baseline": ref.run_tsm(
            values, schedule=ref.FIXED_SCHEDULE,
            parameters=ref.FIXED_BASELINE_SETTINGS,
            chunk_size=len(values) + ref.FRAME_SAMPLES)[0],
        "candidate_dynamic_wsola_ola": ref.run_tsm(
            values, schedule=ref.DYNAMIC_SCHEDULE,
            chunk_size=len(values) + ref.FRAME_SAMPLES)[0],
        "alignment_disabled_control": ref.run_tsm(
            values, schedule=ref.DYNAMIC_SCHEDULE, alignment=False,
            chunk_size=len(values) + ref.FRAME_SAMPLES)[0],
        "varispeed_adverse": ref.varispeed_run(values, 1.25)[0],
    }
    rows = {}
    for label, output in runs.items():
        measured = ref.dominant_frequency(output, **analysis)
        ratio = measured["dominant_hz"] / reference["dominant_hz"]
        expected = 1.25 if label == "varispeed_adverse" else 1.0
        rows[label] = {
            "input_dominant_hz": reference["dominant_hz"],
            "output_dominant_hz": measured["dominant_hz"],
            "frequency_ratio": ratio,
            "expected_ratio": expected,
            "absolute_error": abs(ratio - expected),
            "analysis_interval": measured["analysis_interval"],
            "pitch_preserved": abs(ratio - 1.0) <= 0.03,
            "matches_expected_model": abs(ratio - expected) <= 0.03,
            "audibility_measured": False,
            "qualifies": False,
        }
    return {"stimulus": "tonal", "analysis": analysis, "rows": rows}


def transient_evidence(stimuli: dict[str, Sequence[float]]) -> dict:
    positions = {"tonal": 4300, "speech_like": 5600, "music_like": 7200}
    rows = {}
    for name, boundary in positions.items():
        values = stimuli[name]
        source_peak = max(abs(value) for value in
                          values[boundary - 24:boundary + 25])
        candidate, candidate_src, _ = ref.run_tsm(
            values, schedule=ref.DYNAMIC_SCHEDULE,
            chunk_size=len(values) + ref.FRAME_SAMPLES)
        aligned_off, aligned_off_src, _ = ref.run_tsm(
            values, schedule=ref.DYNAMIC_SCHEDULE, alignment=False,
            chunk_size=len(values) + ref.FRAME_SAMPLES)
        varispeed, varispeed_src = ref.varispeed_run(values, 1.25)
        rows[name] = {
            "source_boundary": boundary,
            "source_peak_abs": source_peak,
            "candidate": ref.transient_at(candidate, candidate_src, boundary),
            "alignment_disabled_control": ref.transient_at(
                aligned_off, aligned_off_src, boundary),
            "varispeed_adverse": ref.transient_at(
                varispeed, varispeed_src, boundary),
            "proxy_only": True,
            "audibility_measured": False,
            "qualifies": False,
        }
    return {"rows": rows}


def rate_update_evidence(stimuli: dict[str, Sequence[float]]) -> dict:
    runs = {
        "identity_1x_control": (ref.IDENTITY_SCHEDULE, ref.DEFAULT_SETTINGS,
                                True, True),
        "fixed_rate_ola_baseline": (ref.FIXED_SCHEDULE,
                                    ref.FIXED_BASELINE_SETTINGS, True, True),
        "candidate_dynamic_wsola_ola": (ref.DYNAMIC_SCHEDULE,
                                        ref.DEFAULT_SETTINGS, True, True),
        "alignment_disabled_control": (ref.DYNAMIC_SCHEDULE,
                                       ref.DEFAULT_SETTINGS, False, True),
        "unsmoothed_step_adverse": (ref.DYNAMIC_SCHEDULE,
                                    ref.DEFAULT_SETTINGS, True, False),
    }
    boundaries = (3200, 6400, 9600)
    rows = {}
    for name, values in stimuli.items():
        outputs = {}
        for label, (schedule, params, alignment, slew) in runs.items():
            output, sources, _ = ref.run_tsm(
                values, schedule=schedule, parameters=params,
                alignment=alignment, slew=slew,
                chunk_size=len(values) + ref.FRAME_SAMPLES)
            outputs[label] = (output, sources)
        rows[name] = {
            str(boundary): {
                label: ref.discontinuity_at(outputs[label][0],
                                            outputs[label][1], boundary)
                for label in outputs
            }
            for boundary in boundaries
        }
    smoothness = {}
    candidate_stream = ref.run_tsm(
        stimuli["tonal"], schedule=ref.DYNAMIC_SCHEDULE,
        chunk_size=len(stimuli["tonal"]) + ref.FRAME_SAMPLES)[2]
    adverse_stream = ref.run_tsm(
        stimuli["tonal"], schedule=ref.DYNAMIC_SCHEDULE, slew=False,
        chunk_size=len(stimuli["tonal"]) + ref.FRAME_SAMPLES)[2]
    for label, stream in (("candidate_dynamic_wsola_ola", candidate_stream),
                          ("unsmoothed_step_adverse", adverse_stream)):
        steps = [abs(item["applied_step"]) for item in stream.rate_updates]
        smoothness[label] = {
            "configured_max_step": ref.MAX_RATE_STEP if label.startswith(
                "candidate") else None,
            "observed_max_step": max(steps, default=0.0),
            "rate_update_count": len(stream.rate_updates),
            "source_timestamps": [item["source_sample"]
                                  for item in stream.rate_updates],
            "qualifies": False,
        }
    return {"boundaries": list(boundaries), "rows": rows,
            "smoothness": smoothness}


def parameter_grid() -> dict:
    rows = {}
    probe = ref.analytic_stimulus("tonal")[:4096]
    for grain in ref.ALLOWED_GRAIN_SAMPLES:
        for ratio in ref.ALLOWED_OVERLAP_RATIOS:
            overlap = ref.round_half_away(grain * ratio)
            for density in ref.ALLOWED_DENSITIES:
                params = ref.validate_parameters({
                    "grain_samples": grain, "overlap_samples": overlap,
                    "density": density})
                window = ref.window_for(grain)
                hop = params["synth_hop_samples"]
                overlaps = grain // hop
                sums = [sum(window[offset + step * hop]
                            for step in range(overlaps))
                        for offset in range(hop)]
                output, sources, _ = ref.run_tsm(
                    probe, schedule=ref.FIXED_SCHEDULE, parameters=params,
                    chunk_size=len(probe) + ref.FRAME_SAMPLES)
                stats = ref.finite_stats(output)
                key = f"grain_{grain}_overlap_{overlap}_density_{density}"
                rows[key] = {
                    "grain_samples": grain,
                    "overlap_samples": overlap,
                    "overlap_ratio": ratio,
                    "density": density,
                    "analysis_hop_samples": params["analysis_hop_samples"],
                    "synth_hop_samples": hop,
                    "window_sum_min": min(sums),
                    "window_sum_max": max(sums),
                    "output_samples": stats["samples"],
                    "effective_rate": len(probe) / stats["samples"],
                    "source_map": ref.source_map_stats(sources),
                    "nonfinite_count": stats["nonfinite_count"],
                    "peak_abs": stats["peak_abs"],
                    "digest": stats["digest"],
                    "qualifies": False,
                }
    invalid = ref.invalid_cases()
    invalid_subset = {key: invalid[key] for key in (
        "missing_parameter_set", "invalid_grain_size", "invalid_overlap",
        "invalid_density_zero", "invalid_density_divisor",
        "missing_rate_selection", "nonfinite_rate", "nan_rate",
        "rate_out_of_range", "nonfinite_input", "missing_valid_input")}
    return {
        "declared_grid": {
            "grain_samples": list(ref.ALLOWED_GRAIN_SAMPLES),
            "overlap_ratios": list(ref.ALLOWED_OVERLAP_RATIOS),
            "densities": list(ref.ALLOWED_DENSITIES),
            "default": {key: ref.DEFAULT_SETTINGS[key] for key in
                        ("grain_samples", "overlap_samples", "density")},
        },
        "rows": rows,
        "invalid_cases": invalid_subset,
    }


def streaming_evidence(stimuli: dict[str, Sequence[float]]) -> dict:
    values = stimuli["speech_like"]
    whole = ref.run_tsm(values, schedule=ref.DYNAMIC_SCHEDULE,
                        chunk_size=len(values) + ref.FRAME_SAMPLES)
    chunked = ref.run_tsm(values, schedule=ref.DYNAMIC_SCHEDULE)
    replay = ref.run_tsm(values, schedule=ref.DYNAMIC_SCHEDULE,
                         first_input_sample=50000)
    independent = ref.run_tsm(values, schedule=ref.DYNAMIC_SCHEDULE,
                              parameters=ref.DENSITY1_SETTINGS)
    reset_stream = ref.StreamTSM(ref.DYNAMIC_SCHEDULE,
                                 parameters=ref.DEFAULT_SETTINGS,
                                 first_input_sample=50000)
    for start in range(0, 5 * ref.FRAME_SAMPLES, ref.FRAME_SAMPLES):
        reset_stream.push([0.0] * ref.FRAME_SAMPLES, ref.FRAME_SAMPLES)
    replay_state = reset_stream.state_digest()
    reset_stream2 = ref.StreamTSM(ref.DYNAMIC_SCHEDULE,
                                  parameters=ref.DEFAULT_SETTINGS,
                                  first_input_sample=50000)
    for start in range(0, 5 * ref.FRAME_SAMPLES, ref.FRAME_SAMPLES):
        reset_stream2.push([0.0] * ref.FRAME_SAMPLES, ref.FRAME_SAMPLES)
    whole_digest = ref.tensor_digest(whole[0])
    chunked_digest = ref.tensor_digest(chunked[0])
    return {
        "one_output_frame_per_input_frame": True,
        "frame_shape": "160 input f32 samples and one 160-sample output frame per call",
        "chunking": {
            "whole_digest": whole_digest,
            "chunked_digest": chunked_digest,
            "byte_identical": whole_digest == chunked_digest,
            "reason": ("The alignment search only addresses samples inside "
                       "the current grain, which is complete before a "
                       "synthesis decision; both feeds see the same prefix."),
        },
        "reset_replay": {
            "original_digest": chunked_digest,
            "offset_replay_digest": ref.tensor_digest(replay[0]),
            "state_digest": replay_state,
            "state_digest_replay": reset_stream2.state_digest(),
            "state_replay_identical": (
                replay_state == reset_stream2.state_digest()),
            "source_offset_respected": replay[1][0] >= 50000,
        },
        "session_independence": {
            "independent_parameters": "density_1_control",
            "different_digest": ref.tensor_digest(independent[0]) != chunked_digest,
            "digest": ref.tensor_digest(independent[0]),
        },
        "frame_rejections": {key: ref.invalid_cases()[key] for key in (
            "nonfinite_input", "missing_valid_input", "wrong_shape",
            "wrong_position", "process_after_final", "out_of_range")},
        "qualifies": False,
    }


def final_partial_evidence(values: Sequence[float]) -> dict:
    stream = ref.StreamTSM(ref.DYNAMIC_SCHEDULE, parameters=ref.DEFAULT_SETTINGS)
    for start in range(0, len(values) - ref.FRAME_SAMPLES, ref.FRAME_SAMPLES):
        stream.push(values[start:start + ref.FRAME_SAMPLES], ref.FRAME_SAMPLES)
    remainder = len(values) % ref.FRAME_SAMPLES
    stream.push(values[-ref.FRAME_SAMPLES:], remainder, final=True)
    stream.flush()
    pairs = stream.output()
    content = [value for value, _ in pairs]
    stats = ref.finite_stats(content)
    target = ref.round_half_away(
        remainder / ref.rate_at(ref.DYNAMIC_SCHEDULE, len(values) - remainder))
    return {
        "input_samples": len(values),
        "full_input_frames": len(values) // ref.FRAME_SAMPLES,
        "final_input_valid_count": remainder,
        "content_output_samples": stats["samples"],
        "target_final_output_samples": target,
        "nonfinite_count": stats["nonfinite_count"],
        "peak_abs": stats["peak_abs"],
        "output_digest": stats["digest"],
        "source_map": ref.source_map_stats([source for _, source in pairs]),
        "qualifies": False,
    }


def rate_profile_evidence(stimuli: dict[str, Sequence[float]],
                          variants: dict, frequency: dict, transients: dict,
                          updates: dict, streaming: dict, final: dict,
                          c_expected: dict) -> dict:
    candidate = {name: rows["candidate_dynamic_wsola_ola"]
                 for name, rows in variants.items()}
    control_rows = {name: rows for name, rows in variants.items()}
    duration_failures = [name for name, row in candidate.items()
                         if abs(row["relative_duration_error"]) >= 0.001]
    preservation = ref.speech_preservation(
        ref.run_tsm(stimuli["speech_like"], schedule=ref.POLICY_SCHEDULE,
                    chunk_size=len(stimuli["speech_like"]) + ref.FRAME_SAMPLES)[1],
        ref.POLICY_SCHEDULE)
    return {
        "source_output_mapping": {
            "rows": {name: {"input_digest": row["input_digest"],
                            "output_digest": row["output_digest"],
                            "source_map_digest": row["source_map_digest"],
                            "source_map": row["source_map"]}
                     for name, row in candidate.items()},
            "source_map_non_monotonic_expected": True,
            "note": ("WSOLA-style backward shifts can revisit a bounded "
                     "source interval; exact bounds are recorded per row."),
        },
        "duration": {
            "rows": {name: {"expected_output_samples": row["expected_output_samples"],
                            "output_samples": row["output_samples"],
                            "duration_error_samples": row["duration_error_samples"],
                            "relative_duration_error": row["relative_duration_error"]}
                     for name, row in candidate.items()},
            "one_ms_per_second_gate_pass": not duration_failures,
            "failing_cases": duration_failures,
            "qualifies": not duration_failures,
        },
        "pitch_preservation": {
            "rows": frequency["rows"],
            "proxied_by": "Goertzel dominant frequency on a stationary tonal prefix",
            "audibility_measured": False,
        },
        "transient_audibility": {
            "rows": transients["rows"],
            "status": "numerical_proxy_only",
            "audibility_measured": False,
            "qualifies": False,
        },
        "playback_buffering": {
            "status": "fixed_boundary_model_only",
            "one_output_frame_per_input_frame": streaming[
                "one_output_frame_per_input_frame"],
            "first_output_frame_index": c_expected["first_output_frame"],
            "first_output_source_samples": c_expected[
                "first_output_source_samples"],
            "first_output_ms": c_expected["first_output_ms"],
            "alignment_lookahead_samples": 0,
            "causal_search_range_samples": ref.SEARCH_RANGE,
            "grain_samples": ref.GRAIN_SAMPLES,
            "drain_non_content_samples": c_expected["drain_non_content_samples"],
            "fifo_capacity_samples": 65536,
            "target_device_buffer_occupancy_measured": False,
            "fill_flush_or_deadline_measured": False,
            "qualifies": False,
        },
        "one_x_and_rate_changes": {
            "identity_digest_equals_input": False,
            "identity_output_length_errors": {
                name: control_rows[name]["identity_1x_control"][
                    "duration_error_samples"]
                for name in control_rows
            },
            "identity_note": ("The 1x OLA reference has a deterministic "
                              "41-sample boundary shortfall; it is recorded "
                              "and not presented as exact identity."),
            "boundaries": list(updates["boundaries"]),
            "candidate_smoothness": updates["smoothness"][
                "candidate_dynamic_wsola_ola"],
            "rate_change_artifacts": "local adjacent-delta proxies only",
        },
        "unfamiliar_speech": {
            "status": "synthetic_formant_surrogate_only",
            "stimulus_digest": fixture.STIMULUS_DIGESTS["speech_like"],
            "real_speech": False,
            "listening_or_wer_measured": False,
        },
        "music": {
            "status": "synthetic_chord_and_beat_surrogate_only",
            "stimulus_digest": fixture.STIMULUS_DIGESTS["music_like"],
            "recording": False,
            "listening_measured": False,
        },
        "silence": {
            "status": "synthetic_zero_stimulus",
            "stimulus_digest": fixture.STIMULUS_DIGESTS["silence"],
            "finite_output": all(
                rows["candidate_dynamic_wsola_ola"]["nonfinite_count"] == 0
                for rows in variants.values()),
        },
        "drift": {
            "schedule": [[start, rate] for start, rate in ref.DRIFT_SCHEDULE],
            "expected_output_samples": ref.expected_duration(
                ref.DRIFT_SCHEDULE, len(stimuli["speech_like"])),
            "observed_output_samples": candidate["speech_like"]["output_samples"],
            "relative_duration_error": candidate["speech_like"][
                "relative_duration_error"],
        },
        "rebuffer": {
            "schedule": [[start, rate] for start, rate in ref.REBUFFER_SCHEDULE],
            "source_event_sample": 6400,
            "synthetic_gap_samples": 800,
            "expected_output_samples": ref.expected_duration(
                ref.REBUFFER_SCHEDULE, len(stimuli["speech_like"])),
            "observed_output_samples": control_rows["speech_like"][
                "rebuffer_control"]["output_samples"],
            "relative_duration_error": control_rows["speech_like"][
                "rebuffer_control"]["relative_duration_error"],
            "target_device_recovery_measured": False,
        },
        "final_partial_window": final,
        "pause_filler_decisions": preservation,
        "speech_preservation": {
            "policy_compliance": preservation["all_policy_rows_ok"],
            "protected_source_coverage_min": preservation[
                "protected_coverage_min"],
            "source_timestamps": preservation[
                "all_rate_decisions_at_source_timestamps"],
            "intelligibility_or_listening_measured": False,
            "qualifies": False,
        },
    }


def build_report(install_location: str | None = None) -> dict:
    stimuli = {name: ref.analytic_stimulus(name)
               for name in fixture.ALL_STIMULI}
    scored = {name: values for name, values in stimuli.items()
              if name in fixture.SCORED_STIMULI}
    stimuli_rows = {name: ref.finite_stats(values)
                    for name, values in stimuli.items()}
    variants = variant_bundle(scored)
    frequency = frequency_evidence(stimuli)
    transients = transient_evidence(stimuli)
    updates = rate_update_evidence(scored)
    grid = parameter_grid()
    streaming = streaming_evidence(stimuli)
    final = final_partial_evidence(stimuli["speech_like"])
    c_expected = ref.c_boundary_evidence(stimuli["c_vector"])
    profile = rate_profile_evidence(stimuli, variants, frequency, transients,
                                    updates, streaming, final, c_expected)
    source_pins = fixture.verify_source_pins()
    boundary_pins = fixture.verify_boundary_pins()
    frozen = fixture.verify_frozen_fixtures()
    return {
        "schema": ref.CONTRACT_ID,
        "status": "proposal_only_not_qualified",
        "disposition": "incomplete",
        "task": {
            "id": "SDK-RUBBER-BAND-R3-STREAMING",
            "component": "rubber-band-r3-streaming",
            "base_commit": ref.BASE_COMMIT,
            "base_commit_at_claim": ref.BASE_COMMIT_AT_CLAIM,
            "branch": ref.BRANCH,
            "write_scope": "docs/task-evidence/rubber-band-r3-streaming/",
            "verification_profile": "rate",
        },
        "tool_profile": {
            "version": ref.VERSION,
            "install_location": install_location or str(ref.TASK_DIR),
            "provenance": "https://github.com/armaudia/audio-sdk.git",
            "repository": "audio-sdk",
            "runner_python": sys.version.split()[0],
            "runner_platform": platform.platform(),
            "candidate": "Deterministic synthetic frame-causal WSOLA-style OLA TSM",
            "profile": "Rate",
        },
        "scope": {
            "task_local_only": True,
            "installed_v0": "16 kHz, mono, f32, 160-sample frames; unchanged",
            "public_surface_changed": False,
            "installed_behavior_changed": False,
            "descriptor_or_registry_changed": False,
            "shared_cmake_changed": False,
            "board_or_handoff_changed": False,
            "real_rubber_band_source_or_binary": False,
            "model_weights": False,
            "licensed_runtime": False,
            "real_corpus": False,
            "playback_device": False,
            "listening_or_release_claim": False,
        },
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "board_snapshot": fixture.verify_board_snapshot(),
        "frozen_fixtures": frozen,
        "contract": {
            "sample_rate_hz": ref.SAMPLE_RATE_HZ,
            "frame_samples": ref.FRAME_SAMPLES,
            "grain_samples": ref.GRAIN_SAMPLES,
            "overlap_samples": ref.OVERLAP_SAMPLES,
            "analysis_hop_samples": ref.ANALYSIS_HOP,
            "synth_hop_samples": ref.SYNTH_HOP,
            "synthesis_hop_density": ref.DENSITY,
            "window": "exact rational Bartlett with overlap-add denominator normalization",
            "phase_denominator": ref.PHASE_DENOMINATOR,
            "alignment": "bounded backward shift search within the current grain",
            "alignment_search_range_samples": ref.SEARCH_RANGE,
            "rate_min": ref.RATE_MIN,
            "rate_max": ref.RATE_MAX,
            "max_rate_step_per_grain": ref.MAX_RATE_STEP,
            "dynamic_schedule": [[start, rate] for start, rate in
                                 ref.DYNAMIC_SCHEDULE],
            "policy_schedule": [[start, rate] for start, rate in
                                ref.POLICY_SCHEDULE],
            "drift_schedule": [[start, rate] for start, rate in
                               ref.DRIFT_SCHEDULE],
            "rebuffer_schedule": [[start, rate] for start, rate in
                                  ref.REBUFFER_SCHEDULE],
        },
        "adapter": fixture.strict_load(ref.TASK_DIR / "adapter.json"),
        "provider": fixture.strict_load(ref.TASK_DIR / "provider.json"),
        "stimuli": stimuli_rows,
        "variants": variants,
        "parameter_grid": grid,
        "rate_profile": profile,
        "frequency_scale": frequency,
        "transient_proxy": transients,
        "rate_updates": updates,
        "streaming": streaming,
        "final_partial": final,
        "c_boundary_expected": c_expected,
        "invalid_and_adverse": fixture.strict_load(
            ref.TASK_DIR / "contract.json")["invalid_and_adverse"],
        "qualification": {
            "status": "proposal_only_not_qualified",
            "disposition": "incomplete",
            "decision": "DEFER",
            "processor_exposure": "deferred",
            "candidate_qualified": False,
            "all_required_results_present": all((
                bool(stimuli_rows), bool(variants), bool(grid["rows"]),
                bool(frequency["rows"]), bool(transients["rows"]),
                bool(updates["rows"]), bool(profile), bool(streaming),
                bool(final), bool(c_expected),
            )),
            "missing_result_promoted": False,
            "duration_gate_pass": profile["duration"]["one_ms_per_second_gate_pass"],
            "rate_mapping_note": ("Synthetic duration error exceeds the "
                                  "proposed 1 ms/s gate; recorded, not waived."),
            "next_gate": "DEFER before any processor exposure or installation",
        },
        "release_gates": [
            "Versioned variable-frame playback actuator or caller-owned TSM FIFO with explicit source/output timestamps outside v0 for r<1 expansion",
            "Paced target-device buffer occupancy, fill/flush, deadline, CPU and availability telemetry",
            "Rights-qualified unfamiliar speech and music cohorts with matched controls and authorized listening/intelligibility scoring",
            "Pinned, rights-cleared exact Rubber Band source or caller-supplied licensed runtime with parity evidence",
            "Explicit provider intake, license review, versioned public-surface decision and independent review before processor exposure",
        ],
        "blockers": [
            {
                "id": "BLK-01",
                "blocker": ("The frozen v0 boundary returns exactly 160 samples "
                            "per call; r<1 expansion is only visible as FIFO "
                            "depth and drain samples."),
                "reopen": "Versioned variable-frame playback actuator or caller-owned timestamped FIFO.",
            },
            {
                "id": "BLK-02",
                "blocker": "No target-device pacing, buffering, fill/flush, deadline or resource measurement.",
                "reopen": "Paced target workload with buffer and resource telemetry.",
            },
            {
                "id": "BLK-03",
                "blocker": "No real or unfamiliar speech, music recording, listening or intelligibility result.",
                "reopen": "Rights-cleared cohorts with independent scoring.",
            },
            {
                "id": "BLK-04",
                "blocker": ("The optional C provider is default-OFF, unlinked and "
                            "unregistered; no public surface is changed."),
                "reopen": "Explicit intake and versioned public-surface decision.",
            },
            {
                "id": "BLK-05",
                "blocker": ("No real Rubber Band source, binary, weights or licensed "
                            "runtime is used; this is an analytic surrogate."),
                "reopen": "Rights-cleared pinned implementation with matched evidence.",
            },
        ],
    }
