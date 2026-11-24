# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict validation of the task-local C/Rust binding evidence package."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any, Dict, List

import check_licensing
import fixture
import reference
import scorer

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "SOURCES.sha256"
JSON_FILES = (
    "contract.json", "adapter.json", "provider.json",
    "crosscheck.json", "c_boundary/harness_output.json", "report.json",
)


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_sources() -> None:
    pinned: Dict[str, str] = {}
    for line in SOURCES.read_text(encoding="ascii").splitlines():
        if line.startswith("PIN  "):
            remainder = line[5:]
            digest, name = remainder.split("  ", 1)
            key = "pin:" + name
        else:
            digest, name = line.split("  ", 1)
            key = name
        if len(digest) != 64 or key in pinned or name == SOURCES.name:
            raise ValueError("invalid_sources_entry")
        pinned[key] = digest
    actual: Dict[str, str] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name == SOURCES.name or "__pycache__" in path.parts:
            continue
        actual[path.relative_to(ROOT).as_posix()] = digest_bytes(path.read_bytes())
    for pin in reference.PINS:
        pin_path = reference.pin_paths()[pin["id"]]
        actual["pin:" + pin["id"]] = digest_bytes(pin_path.read_bytes())
    if pinned != actual:
        missing = sorted(set(pinned) - set(actual))
        extra = sorted(set(actual) - set(pinned))
        changed = sorted(key for key in set(pinned) & set(actual) if pinned[key] != actual[key])
        raise ValueError("sources_manifest_mismatch:" + ",".join(missing + extra + changed))
    if set(pinned) != set(actual):
        raise ValueError("sources_manifest_mismatch")


def check_report(canonical: bytes, digest: str) -> None:
    path = ROOT / "report.json"
    report = reference.read_strict_json(path)
    text, computed = reference.canonical_report(report)
    if text.encode("utf-8") != canonical or computed != digest:
        raise ValueError("report_canonical_mismatch")
    if path.read_bytes() != canonical + b"\n":
        raise ValueError("report_bytes_mismatch")
    if (ROOT / "report.json.sha256").read_text(encoding="ascii") != digest + "\n":
        raise ValueError("digest_file_mismatch")
    for key in ("expose_as_processor", "registered", "default_enabled"):
        if report["decision"][key] is not False:
            raise ValueError("decision_invariant_violated:" + key)
    if report["status"] != "proposal_only_not_qualified" or report["decision"]["incomplete"] is not True:
        raise ValueError("status_not_proposal_only")
    if report["decision"]["production_exposure"] != "DEFER":
        raise ValueError("production_exposure_not_deferred")
    if report["tool"]["rust"]["native_build"] != "DEFER":
        raise ValueError("rust_build_not_deferred")
    if report["installed_v0"]["frame_samples"] != 160 or report["installed_v0"]["changed"] is not False:
        raise ValueError("installed_v0_changed")
    if report["build_evidence"]["sdk_native_build_install_ctest"] != "11/11":
        raise ValueError("sdk_ctest_not_recorded")


def check_crosscheck() -> None:
    crosscheck = reference.read_strict_json(ROOT / "crosscheck.json")
    harness = reference.read_strict_json(ROOT / "c_boundary/harness_output.json")
    expected = reference.model_cases()
    result = scorer.score_all(expected, harness["cases"])
    if not result["passed"] or result["expected_count"] != len(fixture.cases()):
        raise ValueError("crosscheck_not_passing")
    if crosscheck["harness_output_sha256"] != digest_bytes((ROOT / "c_boundary/harness_output.json").read_bytes()):
        raise ValueError("harness_digest_mismatch")
    canonical, computed = reference.canonical_report(crosscheck)
    if (ROOT / "crosscheck.json.sha256").read_text(encoding="ascii").strip() != computed:
        raise ValueError("crosscheck_digest_mismatch")
    if (ROOT / "crosscheck.json").read_bytes() != canonical.encode("utf-8") + b"\n":
        raise ValueError("crosscheck_bytes_mismatch")
    if crosscheck["expected_model_digest"] != reference.model_digest(expected):
        raise ValueError("model_digest_mismatch")
    for key in ("expose_as_processor", "registered", "default_enabled"):
        if crosscheck["decision"][key] is not False:
            raise ValueError("crosscheck_decision_violated:" + key)


def check_pins() -> None:
    for pin in reference.PINS:
        path = reference.pin_paths()[pin["id"]]
        if not path.is_file() or digest_bytes(path.read_bytes()) != pin["sha256"]:
            raise ValueError("pin_mismatch:" + pin["id"])


def check_scope() -> None:
    contract = reference.read_strict_json(ROOT / "contract.json")
    adapter = reference.read_strict_json(ROOT / "adapter.json")
    provider = reference.read_strict_json(ROOT / "provider.json")
    if contract["decision"]["expose_as_processor"] is not False:
        raise ValueError("contract_exposes_processor")
    if contract["public_boundary"]["installed_behavior"] != "unchanged":
        raise ValueError("contract_changes_installed_behavior")
    if provider["provider_added"] is not False or provider["descriptor_added"] is not False:
        raise ValueError("provider_added")
    if provider["registration_call_added"] is not False:
        raise ValueError("registration_call_added")
    registration = adapter["registration"]
    if (not registration["unregistered"] or registration["default_enabled"]
            or not registration["opt_in_only"] or registration["cmake_target_added"]):
        raise ValueError("adapter_not_opt_in")
    if adapter["binding_model"]["rust"]["status"].split(":")[0] != "DEFER":
        raise ValueError("rust_binding_not_deferred")


def check_generated_header() -> None:
    path = ROOT / "c_boundary/raii_model.h"
    if path.read_text(encoding="utf-8") != reference.generated_header():
        raise ValueError("generated_header_mismatch")
    text = path.read_text(encoding="utf-8")
    if "SPDX" "-License-Identifier: Apache-2.0" not in text:
        raise ValueError("generated_header_missing_spdx")


def check_three_repeats(canonical: bytes) -> None:
    """Three in-memory regenerations must be byte-identical to the pinned report."""
    import run  # imported here so --report is independent of this validator
    for _ in range(3):
        report = reference.build_report()
        report["bundle_validation"] = run.bundle_validation()
        if not all(report["bundle_validation"]["checks"].values()):
            raise ValueError("bundle_validation_failed")
        text, _ = reference.canonical_report(report)
        if text.encode("utf-8") != canonical:
            raise ValueError("three_repeat_mismatch")
    for _ in range(3):
        if run.sources_text().encode("ascii") != SOURCES.read_bytes():
            raise ValueError("sources_repeat_mismatch")
        if reference.generated_header().encode("utf-8") != (ROOT / "c_boundary/raii_model.h").read_bytes():
            raise ValueError("header_repeat_mismatch")


def main() -> int:
    try:
        for name in JSON_FILES:
            reference.read_strict_json(ROOT / name)
        check_sources()
        check_pins()
        report = reference.read_strict_json(ROOT / "report.json")
        text, digest = reference.canonical_report(report)
        canonical = text.encode("utf-8")
        check_report(canonical, digest)
        check_crosscheck()
        check_scope()
        check_generated_header()
        check_three_repeats(canonical)
        licensing: Dict[str, Any] = check_licensing.check()
        if licensing["status"] != "ok":
            raise ValueError("licensing_failed:" + ",".join(licensing["problems"]))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    print("PASS strict-json sources pins canonical three-repeats crosscheck scope header licensing defer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
