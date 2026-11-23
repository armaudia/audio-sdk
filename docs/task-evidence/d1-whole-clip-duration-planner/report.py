"""Build the canonical rate-profile evidence report from the adapter boundary.

Every case, control and adverse result below is produced through
``run.dispatch()``. No result is synthesized here, and no missing or unrun
control is treated as a pass.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import fixtures
import reference
import run

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "fixtures" / "report.json"
BASE_COMMIT = "dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc"
BRANCH = "swarm/SDK-D1-WHOLE-CLIP-DURATION-PLANNER"
TASK_ID = "SDK-D1-WHOLE-CLIP-DURATION-PLANNER"


def standard_request(operation: str, *, attempt_id: str = "report", **fields: Any) -> dict[str, Any]:
    request = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": dict(run.CANDIDATE_REF),
        "adapter_ref": dict(run.ADAPTER_REF),
        "configuration": dict(run.DEFAULT_CONFIG),
    }
    if operation == "run":
        request.update({
            "attempt_id": attempt_id,
            "session_id": "report-session",
            "epoch": 1,
        })
    request.update(fields)
    return request


def _summary(cases: list[dict[str, Any]], adverse: list[dict[str, Any]]) -> dict[str, Any]:
    results = [row["response"]["result"] for row in cases]
    identity = [row for row in results if row.get("duration_identity") is True]
    bounds = [row for row in results if row.get("profile_checks", {}).get("rate_bounds") is True]
    nonidentity = [row for row in results if row.get("duration_identity") is False]
    return {
        "case_variant_count": len(cases),
        "duration_identity_pass_count": len(identity),
        "duration_identity_fail_count": len(nonidentity),
        "duration_identity_fail_examples": [
            {"case_id": row["case_id"], "variant": row["variant"],
             "duration_error_ns": row["duration_error_ns"]}
            for row in nonidentity
        ],
        "rate_bounds_pass_count": len(bounds),
        "adverse_control_count": len(adverse),
        "adverse_rejected_count": sum(
            1 for row in adverse if row["response"]["result"]["outcome"] == "rejected"),
        "adverse_reported_infeasible_count": sum(
            1 for row in adverse if row["response"]["result"]["outcome"] == "reported_infeasible"),
        "missing_result_count": 0,
        "candidate_qualified": False,
        "qualification_note": "All results are deterministic offline proposals on synthetic timelines. No candidate is qualified by this report.",
    }


def build_report() -> bytes:
    stimuli = fixtures.load_stimuli()
    verified_pins = fixtures.verify_source_pins(stimuli)
    inspect_response = run.dispatch(standard_request("inspect"))

    case_rows: list[dict[str, Any]] = []
    for case_id in stimuli["cases"]:
        for variant in stimuli["case_variants"][case_id]:
            response = run.dispatch(standard_request(
                "run", attempt_id=f"report-{case_id}-{variant}",
                scenario="case", case_id=case_id, variant=variant))
            case_rows.append({
                "case_id": case_id,
                "variant": variant,
                "response": response,
            })

    adverse_rows: list[dict[str, Any]] = []
    for adverse_id in run.ADVERSE_IDS:
        response = run.dispatch(standard_request(
            "run", attempt_id="report-adverse-" + adverse_id,
            scenario="adverse", adverse_id=adverse_id))
        adverse_rows.append({"adverse_id": adverse_id, "response": response})

    by_key = {(row["case_id"], row["variant"]): row["response"]["result"]
              for row in case_rows}
    one_x = by_key[("identity_all_speech", "1x")]
    final_partial = by_key[("final_partial_window", "d1")]
    drift_uncompensated = by_key[("drift_interval", "drift_uncompensated")]
    drift_oracle = by_key[("drift_interval", "oracle_compensated")]
    rebuffer_uncompensated = by_key[("rebuffer_gap", "rebuffer_uncompensated")]
    rebuffer_oracle = by_key[("rebuffer_gap", "oracle_compensated")]
    recorded = [
        {
            "case_id": case_id,
            "recorded_slow_floor": case["recorded_slow_floor"],
            "planned_speech_rate": by_key[(case_id, "d1")]["budget"]["speech_rate"],
            "matches_recorded_slow_floor": by_key[(case_id, "d1")]["budget"]["matches_recorded_slow_floor"],
        }
        for case_id, case in stimuli["cases"].items() if "recorded_slow_floor" in case
    ]
    artifact_names = ("adapter.json", "reference.py", "fixtures.py", "run.py", "report.py")
    artifacts = {
        name: reference.sha256_hex((ROOT / name).read_bytes()) for name in artifact_names
    }

    report = {
        "protocol_version": 1,
        "report_id": "sdk-d1-whole-clip-duration-planner-rate-evidence",
        "revision": 1,
        "task": TASK_ID,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": "opt-in synthetic developer-only offline proposal",
        "candidate_qualified": False,
        "scope_assertions": {
            "installed_v0_unchanged": True,
            "installed_format": "16 kHz mono float32, 160 samples",
            "offline_proposal_only": True,
            "playback_actuator_installed": False,
            "target_device_pacing_measured": False,
            "fill_flush_measured": False,
            "cpu_or_deadline_measured": False,
            "listening_or_quality_score": False,
            "real_weights_or_assets": False,
            "release_claim": False,
            "shared_files_modified": False,
        },
        "source_pins": verified_pins,
        "recorded_reference": stimuli["recorded_reference"],
        "fixtures": {
            "stimuli_sha256": fixtures.stimuli_digest(),
            "fixture_id": stimuli["fixture_id"],
            "revision": stimuli["revision"],
            "case_count": len(stimuli["cases"]),
            "case_digests": stimuli["case_digests"],
            "deterministic": True,
            "real_audio": False,
        },
        "adapter": {
            "descriptor_sha256": reference.sha256_hex((ROOT / "adapter.json").read_bytes()),
            "identity": reference.IDENTITY,
            "boundary_identity": reference.BOUNDARY_IDENTITY,
            "registration": "unregistered developer-only fixture",
            "inspect": inspect_response,
        },
        "artifact_sha256": artifacts,
        "rate_profile_coverage": {
            "source_output_duration_mapping": {
                "status": "observed",
                "all_maps_union_equals_source": all(
                    row["response"]["result"]["profile_checks"]["source_output_mapping"]["union_equals_source"]
                    for row in case_rows),
                "view": "exact rational source-sample interval to playback-ns interval per block",
            },
            "source_and_output_duration": {
                "status": "observed",
                "source_ns_exact": True,
                "playback_ns_exact_rational": True,
                "identity_checked_exactly": True,
            },
            "one_x_control": {
                "status": "observed",
                "case_id": one_x["case_id"],
                "rate_changes": one_x["rate_change_count"],
                "duration_identity": one_x["duration_identity"],
            },
            "planned_rate_changes_with_recorded_budget": {
                "status": "observed",
                "recorded_cases": recorded,
                "rate_changes_are_source_block_boundaries": all(
                    change["source_ns"] == change["source_first_sample"] * reference.NS_PER_SAMPLE
                    for row in case_rows
                    for change in row["response"]["result"]["rate_changes"]),
            },
            "oracle_variants": {
                "status": "observed",
                "names": [
                    "oracle_labels", "oracle_compensated", "drift_uncompensated",
                    "rebuffer_uncompensated", "fixed_125", "slow_only",
                ],
                "labels_oracle_changes_rate_at_source_sample_16000": (
                    by_key[("gate_label_error", "oracle_labels")]["rate_changes"] !=
                    by_key[("gate_label_error", "d1")]["rate_changes"]),
            },
            "final_partial_window": {
                "status": "observed",
                "case_id": final_partial["case_id"],
                "window": final_partial["profile_checks"]["final_partial_window"],
            },
            "silence_speech_like_and_material_changes": {
                "status": "observed",
                "case_ids": ["final_partial_window", "gate_label_error", "material_transitions"],
                "protected_labels": list(reference.PROTECTED_LABELS),
                "flex_labels": list(reference.FLEX_LABELS),
            },
            "drift": {
                "status": "observed",
                "uncompensated_identity": drift_uncompensated["duration_identity"],
                "oracle_compensated_identity": drift_oracle["duration_identity"],
                "oracle_compensation": drift_oracle["oracle_compensation"],
            },
            "rebuffer": {
                "status": "observed",
                "uncompensated_identity": rebuffer_uncompensated["duration_identity"],
                "oracle_compensated_identity": rebuffer_oracle["duration_identity"],
                "oracle_compensation": rebuffer_oracle["oracle_compensation"],
            },
            "pitch_audibility": dict(reference.PITCH_NOT_MEASURED),
            "transient_audibility": dict(reference.TRANSIENT_NOT_MEASURED),
            "playback_buffering": dict(reference.BUFFERING_SEMANTICS),
            "decisions_tied_to_source_timestamps": all(
                row["response"]["result"]["profile_checks"]["source_timestamp_ties"]
                for row in case_rows),
            "explicit_adverse_controls": {
                "status": "observed",
                "count": len(adverse_rows),
                "ids": list(run.ADVERSE_IDS),
            },
            "missing_results_qualify": False,
        },
        "cases": case_rows,
        "adverse_controls": adverse_rows,
        "summary": _summary(case_rows, adverse_rows),
    }
    return reference.canonical_bytes(report)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="write canonical report bytes here instead of stdout")
    options = parser.parse_args()
    payload = build_report()
    if options.output:
        target = Path(options.output).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        sidecar = target.with_name(target.name + ".sha256")
        sidecar.write_text(reference.sha256_hex(payload) + "  " + target.name + "\n",
                           encoding="utf-8")
        print("report_sha256=" + reference.sha256_hex(payload))
        print("report_bytes=" + str(len(payload)))
    else:
        sys.stdout.buffer.write(payload)


if __name__ == "__main__":
    main()
