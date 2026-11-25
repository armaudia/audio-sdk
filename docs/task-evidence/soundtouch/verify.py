# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict validation of the task-local SoundTouch evidence package."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any, Dict

import check_licensing
import fixture
import reference
import run as generator
import scorer

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "SOURCES.sha256"
JSON_FILES = (
    "contract.json", "adapter.json", "provider.json",
    "provider/consumer_result.json", "report.json", "crosscheck.json",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expected_pin_digests() -> Dict[str, tuple[str, Path]]:
    rows: Dict[str, tuple[str, Path]] = {}
    for relative, sha in reference.SOURCE_PINS.items():
        rows["pin:" + relative] = (sha, reference.AUDIO_ROOT / relative)
    for relative, sha in reference.BOUNDARY_PINS.items():
        rows["pin:" + relative] = (sha, reference.WORKTREE / relative)
    return rows


def check_sources() -> None:
    listed: Dict[str, str] = {}
    for line in SOURCES.read_text(encoding="ascii").splitlines():
        if line.startswith("PIN  "):
            remainder = line[5:]
            sha, name = remainder.split("  ", 1)
            key = "pin:" + name
        else:
            sha, name = line.split("  ", 1)
            key = name
        if len(sha) != 64 or not name or key in listed or name == SOURCES.name:
            raise ValueError("invalid_sources_entry")
        listed[key] = sha
    actual: Dict[str, str] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name == SOURCES.name or "__pycache__" in path.parts:
            continue
        actual[path.relative_to(ROOT).as_posix()] = digest(path.read_bytes())
    for key, (sha, path) in expected_pin_digests().items():
        if not path.is_file() or digest(path.read_bytes()) != sha:
            raise ValueError("pin_mismatch:" + key)
        actual[key] = sha
    if listed != actual:
        missing = sorted(set(listed) - set(actual))
        extra = sorted(set(actual) - set(listed))
        changed = sorted(key for key in set(listed) & set(actual)
                         if listed[key] != actual[key])
        raise ValueError("sources_manifest_mismatch:" + ",".join(missing + extra + changed))


def check_report(canonical: bytes, sidecar: str) -> None:
    report = reference.read_strict_json(ROOT / "report.json")
    text, computed = reference.canonical_report(report)
    if text.encode("utf-8") != canonical or computed != sidecar:
        raise ValueError("report_canonical_mismatch")
    if (ROOT / "report.json").read_bytes() != canonical + b"\n":
        raise ValueError("report_bytes_mismatch")
    if (ROOT / "report.json.sha256").read_text(encoding="ascii") != sidecar + "\n":
        raise ValueError("report_digest_file_mismatch")
    if report["status"] != "proposal_only_not_qualified":
        raise ValueError("status_not_proposal_only")
    decision = report["decision"]
    if (decision["status"] != "incomplete"
            or decision["production_exposure"] != "DEFER"
            or decision["incomplete"] is not True
            or decision["expose_as_processor"] is not False
            or decision["registered"] is not False
            or decision["default_enabled"] is not False):
        raise ValueError("decision_invariant_violated")
    installed = report["installed_v0"]
    if (installed["sample_rate_hz"] != 16000 or installed["channels"] != 1
            or installed["frame_samples"] != 160
            or installed["sample_format"] != "float32" or installed["changed"] is not False):
        raise ValueError("installed_v0_changed")
    if report["acceptance_profile"]["profile"] != "Rate":
        raise ValueError("wrong_acceptance_profile")
    catalog = fixture.catalog()
    if report["fixture"] != catalog:
        raise ValueError("fixture_catalog_mismatch")
    score = scorer.score_profile(report, catalog)
    if not score["passed"] or report["profile_scoring"] != score:
        raise ValueError("profile_scoring_failed:" + ",".join(score["failed_checks"]))
    for row in report["source_pins"].values():
        if row["verified"] is not True or row["actual"] != row["sha256"]:
            raise ValueError("source_pin_not_verified")
    for row in report["boundary_pins"].values():
        if row["verified"] is not True or row["actual"] != row["sha256"]:
            raise ValueError("boundary_pin_not_verified")


def check_crosscheck() -> None:
    crosscheck = reference.read_strict_json(ROOT / "crosscheck.json")
    consumer = reference.read_strict_json(ROOT / "provider" / "consumer_result.json")
    expected = reference.c_boundary_evidence(fixture.c_vector())
    if (crosscheck["expected_content_digest"] != expected["content_digest"]
            or crosscheck["expected_content_samples"] != expected["content_samples"]
            or crosscheck["expected_frame_count"] != expected["frames"]
            or crosscheck["expected_final_valid_count"] != expected["valid_counts"][-1]):
        raise ValueError("crosscheck_model_mismatch")
    if crosscheck["consumer_result_sha256"] != digest(
            (ROOT / "provider" / "consumer_result.json").read_bytes()):
        raise ValueError("consumer_result_digest_mismatch")
    if consumer["sdk_ctest"] != "11/11" or consumer["consumer_off"] != "1/1" \
            or consumer["consumer_on"] != "1/1":
        raise ValueError("consumer_results_not_recorded")
    text, computed = reference.canonical_report(crosscheck)
    if (ROOT / "crosscheck.json").read_bytes() != text.encode("utf-8") + b"\n":
        raise ValueError("crosscheck_bytes_mismatch")
    if (ROOT / "crosscheck.json.sha256").read_text(encoding="ascii") != computed + "\n":
        raise ValueError("crosscheck_digest_mismatch")
    for key in ("expose_as_processor", "registered", "default_enabled"):
        if crosscheck["decision"][key] is not False:
            raise ValueError("crosscheck_decision_violated")
    if crosscheck["decision"]["production_exposure"] != "DEFER":
        raise ValueError("crosscheck_exposure_violated")


def check_scope() -> None:
    contract = reference.read_strict_json(ROOT / "contract.json")
    adapter = reference.read_strict_json(ROOT / "adapter.json")
    provider = reference.read_strict_json(ROOT / "provider.json")
    if contract["status"] != "proposal_only_not_qualified":
        raise ValueError("contract_status_violated")
    if contract["decision"]["production_exposure"] != "DEFER":
        raise ValueError("contract_exposure_violated")
    if contract["exact_scope"]["write_scope"] != "docs/task-evidence/soundtouch/ only":
        raise ValueError("contract_write_scope_violated")
    for key in ("shared_files_changed", "public_api_or_abi_changed", "headers_changed",
                "descriptor_registry_changed", "descriptor_default_changed",
                "provider_registration_changed", "installed_v0_changed",
                "board_handoff_ruleset_or_main_changed", "other_task_changed"):
        if contract["exact_scope"][key] is not False:
            raise ValueError("contract_scope_violated:" + key)
    if provider["provider_added"] is not False or provider["descriptor_added_to_sdk"] is not False:
        raise ValueError("provider_added")
    if provider["registration_call_added_to_sdk"] is not False:
        raise ValueError("registration_call_added")
    registration = adapter["registration"]
    if (registration["unregistered"] is not True or registration["default_enabled"] is not False
            or registration["opt_in_only"] is not True
            or registration["cmake_target_added_to_sdk"] is not False
            or adapter["c_boundary"]["default"] != "OFF"):
        raise ValueError("adapter_not_opt_in")
    if adapter["public_boundary"]["api_abi_changed"] is not False:
        raise ValueError("adapter_changes_public_boundary")


def check_generated_header() -> None:
    path = ROOT / "provider" / "expected_vectors.h"
    expected = reference.c_boundary_evidence(fixture.c_vector())
    if path.read_text(encoding="utf-8") != generator.header_text(expected):
        raise ValueError("generated_header_mismatch")
    text = path.read_text(encoding="utf-8")
    if "SPDX" "-License-Identifier: Apache-2.0" not in text:
        raise ValueError("generated_header_missing_spdx")


def check_three_repeats(canonical: bytes) -> None:
    for _ in range(3):
        report = generator.build_report()
        text, _ = reference.canonical_report(report)
        if text.encode("utf-8") != canonical:
            raise ValueError("report_three_repeat_mismatch")
        if generator.sources_text().encode("ascii") != SOURCES.read_bytes():
            raise ValueError("sources_three_repeat_mismatch")
        expected = reference.c_boundary_evidence(fixture.c_vector())
        if generator.header_text(expected).encode("utf-8") != (
                ROOT / "provider" / "expected_vectors.h").read_bytes():
            raise ValueError("header_three_repeat_mismatch")


def main() -> int:
    try:
        for name in JSON_FILES:
            reference.read_strict_json(ROOT / name)
        check_sources()
        check_pins()
        report = reference.read_strict_json(ROOT / "report.json")
        text, sidecar = reference.canonical_report(report)
        canonical = text.encode("utf-8")
        check_report(canonical, sidecar)
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


def check_pins() -> None:
    for key, (sha, path) in expected_pin_digests().items():
        if not path.is_file() or digest(path.read_bytes()) != sha:
            raise ValueError("pin_mismatch:" + key)


if __name__ == "__main__":
    raise SystemExit(main())
