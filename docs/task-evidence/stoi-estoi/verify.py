# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict validation of the task-local STOI/ESTOI evidence package."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Dict, List

import fixture
import reference
import scorer

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "SOURCES.sha256"
RECORDED_ABS_DELTA = {
    "stoi": 2.1510571102112408e-15,
    "estoi": 1.0075273948473296e-14,
}


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_sources() -> None:
    lines = SOURCES.read_text(encoding="ascii").splitlines()
    pinned: Dict[str, str] = {}
    for line in lines:
        value, name = line.split("  ", 1)
        if len(value) != 64 or name in pinned or name == SOURCES.name:
            raise ValueError("invalid_sources_entry")
        pinned[name] = value
    actual = {
        path.relative_to(ROOT).as_posix(): digest_file(path)
        for path in ROOT.rglob("*") if path.is_file() and path.name != SOURCES.name
        and "__pycache__" not in path.parts
    }
    if pinned != actual:
        raise ValueError("sources_manifest_mismatch")


def check_report(canonical: bytes, digest: str) -> None:
    report = reference.read_strict_json(ROOT / "report.json")
    text, computed = reference.canonical_report(report)
    if text.encode("utf-8") != canonical or computed != digest:
        raise ValueError("report_canonical_mismatch")
    if (ROOT / "report.json").read_bytes() != canonical + b"\n":
        raise ValueError("report_bytes_mismatch")
    if (ROOT / "report.json.sha256").read_text(encoding="ascii") != digest + "\n":
        raise ValueError("digest_file_mismatch")
    if report["decision"]["expose_as_processor"] is not False:
        raise ValueError("processor_exposure_not_deferred")
    if report["decision"]["registered"] is not False or report["decision"]["default_enabled"] is not False:
        raise ValueError("opt_in_invariant_violated")
    if report["aggregation"]["failed_items"]:
        raise ValueError("failed_valid_comparison")


def check_three_repeats(canonical: bytes) -> None:
    """Three in-memory regenerations must be byte-identical to the pinned report."""
    import run  # imported here so --report is independent of this validator
    repeats: List[bytes] = []
    for _ in range(3):
        report = reference.build_report()
        report["bundle_validation"] = run.bundle_validation()
        if not all(report["bundle_validation"]["checks"].values()):
            raise ValueError("bundle_validation_failed")
        text, _ = reference.canonical_report(report)
        repeats.append(text.encode("utf-8"))
    if any(value != canonical for value in repeats):
        raise ValueError("three_repeat_mismatch")


def check_crosscheck() -> None:
    vectors = reference.read_strict_json(ROOT / "crosscheck_vectors.json")
    if vectors["pystoi_version"] != scorer.PYSTOI_VERSION:
        raise ValueError("pystoi_version_mismatch")
    if vectors["source_sha256"] != scorer.PYSTOI_SOURCE_SHA256:
        raise ValueError("pystoi_source_pin_mismatch")
    if len(vectors["vectors"]) != 12:
        raise ValueError("crosscheck_vector_count_mismatch")
    for row in vectors["vectors"]:
        if (abs(row["port_stoi"] - row["pystoi_stoi"]) != row["abs_delta_stoi"]
                or abs(row["port_estoi"] - row["pystoi_estoi"]) != row["abs_delta_estoi"]):
            raise ValueError("crosscheck_recorded_delta_mismatch")
    summary = reference.build_report()["crosscheck"]
    if summary["max_abs_delta"] != RECORDED_ABS_DELTA:
        raise ValueError("crosscheck_summary_mismatch")


def check_scope() -> None:
    contract = reference.read_strict_json(ROOT / "contract.json")
    adapter = reference.read_strict_json(ROOT / "adapter.json")
    if contract["decision"]["expose_as_processor"] is not False:
        raise ValueError("contract_exposes_processor")
    if contract["public_boundary"]["installed_behavior"] != "unchanged":
        raise ValueError("contract_changes_installed_behavior")
    registration = adapter["registration"]
    if (not registration["unregistered"] or registration["default_enabled"]
            or not registration["opt_in_only"] or registration["cmake_target_added"]):
        raise ValueError("adapter_not_opt_in")


def main() -> int:
    try:
        for name in ("contract.json", "adapter.json", "report.json", "crosscheck_vectors.json"):
            reference.read_strict_json(ROOT / name)
        check_sources()
        report = reference.read_strict_json(ROOT / "report.json")
        text, digest = reference.canonical_report(report)
        canonical = text.encode("utf-8")
        check_report(canonical, digest)
        check_three_repeats(canonical)
        check_crosscheck()
        check_scope()
        items, pinned = fixture.cohort()
        if len(items) != 6 or pinned["clean_digest"] != reference.build_report()["fixture"]["clean_digest"]:
            raise ValueError("fixture_pin_mismatch")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    print("PASS strict-json sources canonical three-repeats crosscheck scope fixture")
    return 0


if __name__ == "__main__":
    sys.exit(main())
