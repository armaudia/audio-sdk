# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local byte, schema, pin, repeat and write-scope verification.

Run from this directory with ``python3 verify.py``. The script is read-only:
it never regenerates or rewrites evidence. It checks strict JSON, canonical
report bytes and digest sidecar, source/artifact pins, three byte-identical
cold-start passes, the room acceptance structure, SPDX coverage and that all
worktree changes stay inside this task directory.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

import check_licensing
import fixture
import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = fixture.REPORT_FILE
SIDECAR = fixture.SIDECAR_FILE
PINS = fixture.PINS_FILE
REQUIRED_REPORT_KEYS = {
    "schema_id", "contract", "status", "candidate_status", "completeness",
    "decision", "decision_reason", "scope", "fixture_digest", "format",
    "provider", "source_pins", "boundary_pins", "artifact_pins",
    "board_snapshot", "scorer", "config", "conditions", "special_conditions",
    "no_reference_suppressor", "clean_near_end_preservation",
    "alignment_and_state", "adverse", "repeatability", "room_profile",
    "noncausal_control", "scope_comparison", "qualification",
}


def _duplicate_rejecting_pairs(items: List[Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json_constant:" + token)


def strict_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"),
                         object_pairs_hook=_duplicate_rejecting_pairs,
                         parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise ValueError("root_not_object")
    return payload


def check_pins(errors: List[str]) -> int:
    count = 0
    for raw in PINS.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("#"):
            continue
        count += 1
        parts = raw.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append("malformed pin line: " + repr(raw))
            continue
        digest, raw_path = parts
        if raw_path.startswith("source:"):
            path = fixture.SOURCE_ROOT / raw_path.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw_path
        if not path.is_file():
            errors.append("pinned file missing: " + raw_path)
        elif fixture.sha256(path.read_bytes()) != digest:
            errors.append("pinned bytes changed: " + raw_path)
    return count


def check_report(errors: List[str]) -> Dict[str, Any]:
    try:
        report = strict_json(REPORT)
        contract = strict_json(fixture.CONTRACT_FILE)
        adapter = strict_json(fixture.ADAPTER_FILE)
        provider = strict_json(fixture.PROVIDER_FILE)
    except (OSError, ValueError) as error:
        errors.append("strict JSON failed: " + str(error))
        return {}
    if not REQUIRED_REPORT_KEYS <= set(report):
        errors.append("report is missing required sections: " + ", ".join(
            sorted(REQUIRED_REPORT_KEYS - set(report))))
        return report
    if REPORT.read_bytes() != fixture.canonical_report_bytes(report):
        errors.append("report.json is not canonical byte output")
    expected_sidecar = reference.canonical_report(report)[1] + "\n"
    if SIDECAR.read_text(encoding="ascii") != expected_sidecar:
        errors.append("report.json.sha256 is stale")
    if report["schema_id"] != "audio-sdk/offline-multichannel-wpe-report/0.1":
        errors.append("unexpected report schema")
    if report["status"] != "proposal_only_not_qualified":
        errors.append("report status is not proposal-only")
    if report["completeness"] != "incomplete" or report["decision"] != "DEFER":
        errors.append("report is not incomplete with a DEFER decision")
    if report["qualification"]["status"] != "not_qualified":
        errors.append("qualification status is not not_qualified")
    if not report["qualification"]["all_required_results_present"]:
        errors.append("a required result is missing")
    if report["format"]["processing_mode"] != "whole_clip_noncausal":
        errors.append("processing mode is not whole-clip noncausal")
    if report["format"]["realtime_v0_provider"]:
        errors.append("unexpected realtime v0 provider claim")
    if report["format"]["content_delay_samples"] != 0:
        errors.append("unexpected content delay")
    if report["format"]["c_provider_added"]:
        errors.append("unexpected C provider claim")
    if not report["provider"]["default_enabled"] is False:
        errors.append("provider must be disabled by default")
    if not report["provider"]["opt_in_required"] or report["provider"]["registered"]:
        errors.append("provider must be opt-in and unregistered")
    if report["provider"]["c_abi_or_sdk_default_change"]:
        errors.append("ABI/default change claimed")
    if not report["provider"]["off_on_probe"]["off_is_bit_exact_identity"]:
        errors.append("provider OFF is not a bit-exact identity")
    if not report["provider"]["off_on_probe"]["on_differs_from_off"]:
        errors.append("provider ON did not differ from OFF")
    if report["room_profile"]["profile"] != "room":
        errors.append("room acceptance profile not recorded")
    if "delayed_or_missing_render" not in report["room_profile"]["not_applicable"]:
        errors.append("missing render gap is not disclosed")
    if not report["repeatability"]["byte_identical"]:
        errors.append("three reported repeats are not byte-identical")
    control = report["noncausal_control"]
    if (control["whole_clip_noncausal"] is not True
            or control["real_time_claim"] is not False
            or control["used_as_candidate_oracle"] is not False
            or control["online_acceptance_threshold"] is not False
            or control["provider_substitution"] is not False):
        errors.append("noncausal control disclosure is inconsistent")
    required = report["qualification"]["required_results"]
    if not all(required.values()):
        errors.append("required results are incomplete: " + ", ".join(
            key for key, value in required.items() if not value))
    adverse = report["adverse"]["frame_rejections"]
    for key, expected in (
        ("nonfinite", "rejected_nonfinite"),
        ("stale_session", "rejected_session"),
        ("wrong_shape", "rejected_tensor"),
        ("out_of_range", "rejected_invalid"),
        ("stale_epoch", "rejected_epoch"),
        ("stale_position", "rejected_position"),
        ("finalize_status", "ok"),
        ("finished_reuse", "rejected_session"),
        ("process_after_finish", "rejected_session"),
    ):
        if adverse.get(key) != expected:
            errors.append(f"adverse {key} is {adverse.get(key)!r}, expected {expected!r}")
    if (not adverse.get("dsp_state_unchanged") or adverse.get("invalid_count_delta") != 6):
        errors.append("rejections mutated DSP state or missed the invalid count")
    if contract.get("task") != "SDK-OFFLINE-MULTICHANNEL-WPE":
        errors.append("contract task mismatch")
    if contract.get("verification_profile") != "room":
        errors.append("contract verification profile mismatch")
    if contract.get("base_commit") != fixture.BASE_COMMIT:
        errors.append("contract base commit mismatch")
    if contract["public_boundary"]["public_api_abi_changed"]:
        errors.append("contract claims an ABI change")
    if contract["public_boundary"]["installed_v0_behavior_changed"]:
        errors.append("contract claims an installed v0 behavior change")
    if provider.get("default_enabled") is not False or provider.get("registered") is not False:
        errors.append("opt-in provider manifest is not disabled by default")
    if adapter.get("registration") != "unregistered-developer-only":
        errors.append("adapter manifest is not unregistered")
    if adapter.get("protocol_version") != 1:
        errors.append("adapter protocol mismatch")
    if adapter.get("realtime_v0_provider") is not False:
        errors.append("adapter claims a realtime v0 provider")
    for relative, expected in {**report["source_pins"], **report["boundary_pins"],
                               **report["artifact_pins"]}.items():
        path = fixture.SOURCE_ROOT / relative if relative.startswith(
            ("research/", "adapters/", "REALTIME_", "audio-benchmark-platform/")) else SDK_ROOT / relative
        if not path.is_file() or fixture.sha256(path.read_bytes()) != expected:
            errors.append("report pin stale: " + relative)
    crosscheck = HERE / "crosscheck_vectors.json"
    if fixture.sha256(crosscheck.read_bytes()) != report["scorer"][
            "crosscheck_vectors_file_sha256"]:
        errors.append("cross-check file digest mismatch")
    return report


def check_repeats(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    repeats = fixture.repeat_probe()
    if not repeats["byte_identical"] or repeats["runs"] != 3:
        errors.append("three fresh-pass repeat check failed")
    if repeats["input_digest"] != report["repeatability"]["input_digest"]:
        errors.append("repeat probe input does not match report")
    if repeats["output_digests"] != report["repeatability"]["output_digests"]:
        errors.append("repeat probe output does not match report")


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True, check=True)
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if not path.startswith(fixture.TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    diff_check = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"],
                                capture_output=True, text=True)
    if diff_check.returncode != 0:
        errors.append("git diff --check failed: " + diff_check.stdout.strip())
    return changed


def main() -> int:
    errors: List[str] = []
    pin_count = check_pins(errors)
    report = check_report(errors)
    check_repeats(errors, report)
    licensing = check_licensing.check()
    errors.extend("licensing: " + problem for problem in licensing["problems"])
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print(f"pins_ok={pin_count} json_ok=4 report_sha256="
          f"{fixture.sha256(REPORT.read_bytes())} repeats_ok=3 "
          f"licensing_ok=1 scope_ok=1 changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
