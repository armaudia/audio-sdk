# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Exact, conservative scoring helpers for the synthetic Rate evidence.

These helpers never infer a missing result and never promote an invalid,
nonfinite or adverse observation to a scored candidate result. A passing score
means only that the required synthetic observations are present and internally
consistent; it is not a quality, listening, device or release qualification.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

MAX_PEAK = 1.0
PITCH_RATIO_TOLERANCE = 0.03
MAX_TRANSIENT_TIMING_ERROR = 512


def score_validity(stats: Dict[str, Any], *, expected_length: Optional[int] = None) -> Dict[str, Any]:
    checks = {
        "finite": stats.get("nonfinite_count") == 0,
        "in_range": stats.get("clipping_count") == 0
                    and float(stats.get("peak_abs", 0.0)) <= MAX_PEAK,
        "length_present": isinstance(stats.get("samples"), int) and stats["samples"] >= 0,
    }
    if expected_length is not None:
        checks["length_matches"] = stats.get("samples") == expected_length
    return {"status": "valid" if all(checks.values()) else "invalid",
            "checks": checks, "expected_length": expected_length}


def score_duration(row: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "expected_present": isinstance(row.get("expected_output_samples"), int),
        "observed_present": isinstance(row.get("observed_output_samples"), int),
        "exact": row.get("duration_error_samples") == 0,
        "finite": row.get("nonfinite_count") == 0,
        "in_range": row.get("clipping_count") == 0,
    }
    return {"status": "scored" if all(checks.values()) else "missing_or_invalid",
            "checks": checks}


def score_pitch(section: Dict[str, Any]) -> Dict[str, Any]:
    rows = section.get("rows", {})
    checks: Dict[str, bool] = {}
    for label, row in rows.items():
        checks[label + ":model_match"] = bool(row.get("matches_expected_model"))
        expected = float(row.get("expected_ratio", 1.0))
        if expected == 1.0:
            checks[label + ":preserved"] = bool(row.get("pitch_preserved"))
    adverse = rows.get("varispeed_adverse_control", {})
    checks["adverse_shifts_pitch"] = not bool(adverse.get("pitch_preserved", True))
    return {"status": "scored" if rows and all(checks.values()) else "missing_or_invalid",
            "checks": checks, "tolerance": PITCH_RATIO_TOLERANCE}


def score_transients(section: Dict[str, Any]) -> Dict[str, Any]:
    rows = section.get("transients", {})
    checks: Dict[str, bool] = {}
    for name, row in rows.items():
        events = row.get("transient_events", [])
        checks[name + ":present"] = bool(events) and row.get("status") == "ok"
        for event in events:
            key = name + ":" + str(event.get("source_sample"))
            checks[key + ":scored"] = event.get("status") == "scored"
            retention = float(event.get("amplitude_retention", 0.0))
            checks[key + ":positive_retention"] = retention > 0.0
            checks[key + ":timing_bounded"] = (
                int(event.get("source_timing_error_samples", 10**9))
                <= MAX_TRANSIENT_TIMING_ERROR)
    checks["boundaries_present"] = bool(section.get("rate_change_boundaries"))
    return {"status": "proxy-scored" if checks and all(checks.values()) else "missing_or_invalid",
            "checks": checks,
            "note": "Peak and adjacent-delta proxies only; no audibility claim."}


def score_controls(streaming: Dict[str, Any], catalog: Dict[str, Any]) -> Dict[str, Any]:
    expected = {
        "nonfinite_input": "nonfinite_input",
        "out_of_range_input": "out_of_range",
        "wrong_shape": "wrong_shape",
        "wrong_position": "wrong_position",
        "wrong_epoch": "wrong_epoch",
        "process_after_final": "process_after_final",
        "drain_before_final": "missing_final_input",
    }
    observed = streaming.get("frame_rejections", {})
    checks: Dict[str, bool] = {}
    for case_id, code in expected.items():
        row = observed.get(case_id, {})
        checks[case_id] = (row.get("status") == "rejected"
                           and row.get("code") == code
                           and row.get("state_unchanged") is True)
    config_checks = streaming.get("config_rejections", {})
    for case_id, code in (("missing_rate_selection", "missing_rate_selection"),
                          ("invalid_config", "invalid_config"),
                          ("rate_out_of_range", "rate_out_of_range"),
                          ("nonfinite_rate", "nonfinite_rate")):
        row = config_checks.get(case_id, {})
        checks[case_id] = row.get("status") == "rejected" and row.get("code") == code
    declared = {case["case_id"] for case in catalog.get("cases", [])}
    checks["all_declared_cases_enumerated"] = declared.issuperset(set(expected) | set(config_checks))
    return {"status": "controls-scored" if all(checks.values()) else "missing_or_invalid",
            "checks": checks}


def score_profile(report: Dict[str, Any], catalog: Dict[str, Any]) -> Dict[str, Any]:
    """Score presence and internal consistency of every required rate observation."""
    duration_rows = [row for group in report.get("duration_mapping", {}).values()
                     for row in group.values()]
    variant_rows = [row for group in report.get("variants", {}).values()
                    for row in group.values()]
    checks: Dict[str, bool] = {
        "status_is_proposal_only": report.get("status") == "proposal_only_not_qualified",
        "decision_is_deferred": (report.get("decision", {}).get("production_exposure") == "DEFER"
                                 and report.get("decision", {}).get("incomplete") is True),
        "installed_v0_unchanged": report.get("installed_v0", {}).get("changed") is False,
        "pins_verified": bool(report.get("source_pins"))
                         and all(row.get("verified") is True
                                 for row in report.get("source_pins", {}).values())
                         and all(row.get("verified") is True
                                 for row in report.get("boundary_pins", {}).values()),
        "stimuli_present": len(report.get("stimuli", {})) == len(catalog.get("stimulus_names", [])),
        "duration_rows_present": bool(duration_rows),
        "durations_exact": all(score_duration(row)["status"] == "scored" for row in duration_rows),
        "variants_present": bool(variant_rows),
        "variants_valid": all(row.get("nonfinite_count") == 0
                              and row.get("clipping_count") == 0 for row in variant_rows),
        "pitch": score_pitch(report.get("steady_state", {}).get("frequency_scale", {}))["status"]
                 == "scored",
        "transients": score_transients(report.get("transient_behavior", {}))["status"]
                      == "proxy-scored",
        "pause_policy_present": bool(report.get("pause_policy"))
                                and report["pause_policy"].get("duration_error_samples") == 0,
        "drift_rebuffer_present": bool(report.get("drift_rebuffer"))
                                  and all(row.get("duration_error_samples") == 0
                                          for row in report["drift_rebuffer"].values()),
        "streaming_present": bool(report.get("streaming")),
        "final_partial_present": bool(report.get("final_partial"))
                                 and report["final_partial"].get("output_finite") is True,
        "c_boundary_expected_present": bool(report.get("c_boundary_expected")),
        "controls": score_controls(report.get("streaming", {}), catalog)["status"]
                    == "controls-scored",
        "profile_rows_present": bool(report.get("acceptance_profile", {}).get("rows")),
        "blockers_present": len(report.get("blockers", [])) >= 5,
        "no_missing_result_promoted": report.get("qualification", {}).get(
            "missing_result_promoted") is False,
        "no_real_speech_claimed": report.get("qualification", {}).get(
            "real_speech_claimed") is False,
        "no_listening_claimed": report.get("qualification", {}).get(
            "listening_claimed") is False,
        "no_device_timing_claimed": report.get("qualification", {}).get(
            "device_timing_claimed") is False,
        "release_not_qualified": report.get("qualification", {}).get(
            "release_qualified") is False,
    }
    failures: List[str] = [name for name, ok in checks.items() if not ok]
    return {
        "profile": "Rate",
        "passed": not failures,
        "checks": checks,
        "failed_checks": failures,
        "status": ("all-required-synthetic-results-present-not-qualified" if not failures
                   else "incomplete-missing-or-invalid-result"),
        "note": ("Internal consistency of synthetic evidence only; no candidate is "
                 "qualified by this score."),
    }


if __name__ == "__main__":
    import json
    print(json.dumps({"status": "scorer-helpers-only", "note": __doc__}, sort_keys=True))
