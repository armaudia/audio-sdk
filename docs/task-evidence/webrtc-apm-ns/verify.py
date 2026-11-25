# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only validation of the WebRTC-APM-NS evidence package.

It verifies strict JSON, source pins, the frozen manifest, canonical report
bytes, three cold-start regenerations, scope invariants and the licensing
boundary. It never edits shared files and never promotes the candidate.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Optional

import check_licensing
import fixture
import reference
import run

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "SOURCES.sha256"
JSON_FILES = ("contract.json", "adapter.json", "provider.json", "report.json")


def workspace_root() -> Optional[Path]:
    for parent in ROOT.parents:
        if (parent / "research" / "voice-enhancement-20261101").is_dir():
            return parent
    return None


def check_sources() -> None:
    actual = run.source_manifest()
    if SOURCES.read_text(encoding="utf-8") != actual:
        raise ValueError("sources_manifest_mismatch")
    for line in actual.splitlines():
        value, name = line.split("  ", 1)
        if len(value) != 64 or not name or name.endswith("/"):
            raise ValueError("invalid_sources_entry")


def check_source_pins() -> None:
    workspace = workspace_root()
    if workspace is None:
        raise ValueError("source_workspace_unavailable")
    for relative, expected in reference.SOURCE_PINS.items():
        path = workspace / relative
        if not path.is_file():
            raise ValueError("source_pin_missing:" + relative)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("source_pin_mismatch:" + relative)


def check_report() -> Dict[str, Any]:
    report = reference.read_strict_json(ROOT / "report.json")
    text, digest = reference.canonical_report(report)
    canonical = text.encode("utf-8")
    if (ROOT / "report.json").read_bytes() != canonical + b"\n":
        raise ValueError("report_bytes_not_canonical")
    if (ROOT / "report.json.sha256").read_text(encoding="ascii") != digest + "\n":
        raise ValueError("report_digest_mismatch")
    return report


def check_scope(report: Dict[str, Any]) -> None:
    contract = reference.read_strict_json(ROOT / "contract.json")
    adapter = reference.read_strict_json(ROOT / "adapter.json")
    provider = reference.read_strict_json(ROOT / "provider.json")
    if contract["status"] != "proposal_only_not_qualified":
        raise ValueError("contract_not_proposal_only")
    if contract.get("verification_profile") != "enhancement":
        raise ValueError("wrong_verification_profile")
    if any(contract.get(key) for key in ("public_surface_change", "installed_behavior_change",
                                         "descriptor_default_change")):
        raise ValueError("public_surface_change_claimed")
    for document in (contract, adapter, provider, report):
        decision = document.get("decision", {})
        if decision.get("disposition") != "DEFER" or decision.get("promote") is not False:
            raise ValueError("deferred_decision_missing")
        if decision.get("registered") is not False or decision.get("default_enabled") is not False:
            raise ValueError("opt_in_invariant_violated")
    if report["status"] != "proposal_only_not_qualified" or report["completeness"] != "incomplete":
        raise ValueError("report_status_not_incomplete")
    if any(gate["status"] != "not_met" for gate in report["gates"]):
        raise ValueError("gate_weakened")
    if report["profile_application"]["missing_result_qualifies"] is not False:
        raise ValueError("missing_result_qualifies")
    if report["scope"]["C_boundary_included"] is not False:
        raise ValueError("unexpected_c_boundary")
    if not report["failure_controls"]["all_explicit"]:
        raise ValueError("failure_controls_incomplete")
    if not report["bundle_validation"]["all_explicit"]:
        raise ValueError("bundle_validation_incomplete")


def check_fixture(report: Dict[str, Any]) -> None:
    items, pinned = fixture.cohort()
    if len(items) != 2 or pinned != report["fixture"]["digests"]:
        raise ValueError("fixture_pin_mismatch")
    if any(len(item["clean"]) != fixture.SAMPLES or len(item["noisy"]) != fixture.SAMPLES for item in items):
        raise ValueError("fixture_length_mismatch")


def check_paired(report: Dict[str, Any]) -> None:
    rows = report["paired_results"]
    if len(rows) != 2 * len(reference.PROCESS_VARIANTS):
        raise ValueError("paired_result_count_mismatch")
    for row in rows:
        if row["status"] != "scored" or row["metrics"] is None:
            raise ValueError("unscored_paired_result")
        metrics = row["metrics"]
        if not metrics["finite"] or metrics["delta_si_sdr_db"] is None or metrics["delta_stoi_style"] is None:
            raise ValueError("missing_paired_metric")
        if metrics["peak"] >= 1.0:
            raise ValueError("output_peak_not_finite_or_clipping")
    for condition in ("mild-snr+6", "hard-snr-3"):
        control = next(row for row in rows if row["condition"] == condition
                       and row["variant"] == reference.CONTROL_VARIANT)
        candidate = next(row for row in rows if row["condition"] == condition
                         and row["variant"] == reference.CANDIDATE_VARIANT)
        baseline = next(row for row in rows if row["condition"] == condition
                        and row["variant"] == reference.BASELINE_VARIANT)
        if control["metrics"]["delta_si_sdr_db"] != 0.0:
            raise ValueError("identity_control_not_zero")
        if candidate["metrics"]["delta_si_sdr_db"] <= 0.0:
            raise ValueError("candidate_not_better_than_noisy")
        if baseline["status"] != "scored":
            raise ValueError("baseline_unscored")
        adverse = {row["metric"] for row in report["adverse_results"]
                   if row["condition"] == condition and row["variant"] == reference.CANDIDATE_VARIANT}
        recorded = {metric for metric in ("delta_si_sdr_db", "delta_stoi_style")
                    if candidate["metrics"][metric] <= 0.0}
        if adverse != recorded:
            raise ValueError("adverse_results_not_retained")
    if not report["adverse_results"]:
        raise ValueError("no_adverse_results_recorded")
    if report["unpaired_predictive_screen"]["qualifies_candidate"] is not False:
        raise ValueError("unpaired_screen_qualifies")


def check_three_repeats() -> None:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    original = (ROOT / "report.json").read_bytes()
    digests: List[str] = []
    for _ in range(3):
        completed = subprocess.run([sys.executable, "run.py", "--report"], cwd=ROOT, env=environment,
                                   capture_output=True, text=True, check=True)
        digest = completed.stdout.strip()
        if len(digest) != 64:
            raise ValueError("repeat_digest_invalid")
        digests.append(digest)
        if (ROOT / "report.json").read_bytes() != original:
            raise ValueError("cold_start_report_mismatch")
    sidecar = (ROOT / "report.json.sha256").read_text(encoding="ascii").strip()
    if len(set(digests)) != 1 or digests[0] != sidecar:
        raise ValueError("three_repeat_mismatch")
    sources = subprocess.run([sys.executable, "run.py", "--sources"], cwd=ROOT, env=environment,
                             capture_output=True, text=True, check=True).stdout
    if sources != (ROOT / "SOURCES.sha256").read_text(encoding="utf-8"):
        raise ValueError("sources_regeneration_mismatch")


def main() -> int:
    try:
        for name in JSON_FILES:
            reference.read_strict_json(ROOT / name)
        check_sources()
        check_source_pins()
        report = check_report()
        check_scope(report)
        check_fixture(report)
        check_paired(report)
        check_three_repeats()
        if check_licensing.main() != 0:
            raise ValueError("licensing_check_failed")
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    print("PASS strict-json sources pins canonical three-repeats scope fixture paired licensing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
