# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only validation of the task-local learned-inverse-EQ evidence package."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, List

import reference
import scorer

ROOT = Path(__file__).resolve().parent
JSON_FILES = ("contract.json", "adapter.json", "provider.json", "report.json",
              "crosscheck_vectors.json")
EXPECTED_STATUS = "proposal_only_not_qualified"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    raise ValueError(message)


def check_strict_json() -> Dict[str, Any]:
    loaded: Dict[str, Any] = {}
    for name in JSON_FILES:
        loaded[name] = scorer.read_strict_json(ROOT / name)
    return loaded


def expected_sources() -> str:
    rows: List[str] = []
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == "SOURCES.sha256":
            continue
        rows.append(scorer.digest_bytes(path.read_bytes()) + "  " + relative + "\n")
    return "".join(rows)


def check_sources() -> None:
    text = (ROOT / "SOURCES.sha256").read_text(encoding="utf-8")
    if text != expected_sources():
        fail("sources_manifest_mismatch")
    for line in text.splitlines():
        digest, name = line.split("  ", 1)
        if not HEX64.fullmatch(digest) or name == "SOURCES.sha256" or ".." in name:
            fail("invalid_sources_entry")


def check_report(report: Dict[str, Any]) -> str:
    text, digest = reference.canonical_report(report)
    canonical = text.encode("utf-8")
    if (ROOT / "report.json").read_bytes() != canonical + b"\n":
        fail("report_bytes_not_canonical")
    if (ROOT / "report.json.sha256").read_text(encoding="utf-8") != digest + "\n":
        fail("report_digest_sidecar_mismatch")
    if report["status"] != EXPECTED_STATUS or report["qualification"] != "incomplete":
        fail("unexpected_status")
    if report["crosscheck"]["content_digest"] != scorer.read_strict_json(
            ROOT / "crosscheck_vectors.json")["sha256"]:
        fail("crosscheck_digest_mismatch")
    if report["crosscheck"]["file_sha256_at_build"] != scorer.digest_bytes(
            (ROOT / "crosscheck_vectors.json").read_bytes()):
        fail("crosscheck_file_pin_mismatch")
    return digest


def check_crosscheck() -> None:
    rendered = scorer.canonical_text(reference.crosscheck_vectors()) + "\n"
    if (ROOT / "crosscheck_vectors.json").read_text(encoding="utf-8") != rendered:
        fail("crosscheck_not_byte_identical")
    vectors = scorer.read_strict_json(ROOT / "crosscheck_vectors.json")
    if len(vectors["vectors"]) != 6:
        fail("crosscheck_vector_count")


def check_scope(loaded: Dict[str, Any]) -> None:
    contract, adapter, provider, report = (
        loaded["contract.json"], loaded["adapter.json"], loaded["provider.json"],
        loaded["report.json"])
    if contract["status"] != EXPECTED_STATUS or contract["verification_profile"] != "dsp":
        fail("contract_profile_mismatch")
    if contract["decision"] != report["decision"]:
        fail("decision_mismatch")
    for key in ("expose_as_processor", "registered", "default_enabled",
                "public_api_abi_change", "release_claim"):
        if report["decision"][key] is not False:
            fail("forbidden_decision:" + key)
    if report["decision"]["installed_v0_behavior"] != "unchanged":
        fail("installed_behavior_changed")
    if adapter["registration"] != "unregistered-developer-only" or adapter["public_c_boundary_included"]:
        fail("adapter_not_task_local")
    if (provider["registered"] or provider["default_enabled"] or provider["c_source_included"]
            or provider["descriptor_settings"] or provider["exposure_decision"] != "deferred"):
        fail("provider_not_deferred")
    if contract["source_pins"] != report["source_pins"]:
        fail("source_pin_mismatch")
    if contract["boundary_pins"] != report["boundary_pins"]:
        fail("boundary_pin_mismatch")
    if contract["board_snapshot"]["sha256_at_read"] != report["board_snapshot"]["sha256_at_read"]:
        fail("board_snapshot_mismatch")
    if not report["controls"]["no_missing_result_qualifies"]:
        fail("missing_result_qualifies")
    if not report["controls"]["identity_is_bit_exact"]:
        fail("identity_not_exact")
    for name, rows in report["comparisons"].items():
        for mode, row in rows.items():
            if row["status"] != "complete" or row["qualifies"] is not False:
                fail("comparison_qualifies:" + name + ":" + mode)
    if not all(value["dsp_state_unchanged"] for value in
               report["controls"]["invalid_and_missing"].values()):
        fail("invalid_input_mutated_dsp_state")
    ill = report["dsp_profile"]["ill_conditioned_inverse"]
    if ill["condition"]["condition_estimate"] <= 1.0 or ill["qualifies"] is not False:
        fail("ill_condition_not_reported")
    adverse = report["dsp_profile"]["adverse_out_of_band_amplification"]
    if (adverse["ill_conditioned_amplification_db"] is None
            or adverse["ill_conditioned_amplification_db"] <= 0.0
            or adverse["qualifies"] is not False):
        fail("out_of_band_amplification_not_reported")


def check_three_cold_starts(pinned: str) -> None:
    code = ("import reference, run; "
            "print(reference.canonical_report(run.report_with_pins())[1])")
    environment = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"}
    digests: List[str] = []
    for _ in range(3):
        completed = subprocess.run([sys.executable, "-c", code], cwd=ROOT,
                                   env=environment, capture_output=True,
                                   text=True, check=False, timeout=120)
        if completed.returncode != 0:
            fail("cold_start_failed:" + completed.stderr.strip()[:120])
        digests.append(completed.stdout.strip())
    if any(value != pinned for value in digests):
        fail("three_cold_start_repeat_mismatch")


def main() -> int:
    try:
        loaded = check_strict_json()
        check_sources()
        pinned = check_report(loaded["report.json"])
        check_crosscheck()
        check_scope(loaded)
        check_three_cold_starts(pinned)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    print("PASS strict-json sources canonical three-cold-starts crosscheck scope controls")
    return 0


if __name__ == "__main__":
    sys.exit(main())
