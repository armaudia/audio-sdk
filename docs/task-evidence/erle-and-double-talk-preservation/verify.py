# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Verify pinned sources, strict JSON, boundary, artifacts and exact repeats.

Usage (from the task-local directory)::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

All checks are local and read-only.  The mutable board snapshot is reported as
provenance and never gates this evidence.  The final check performs three
independent ``run.py --report`` regenerations and requires byte-identical
standard output each time.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Optional

import fixture
import reference
import run as adapter

TASK = Path(__file__).resolve().parent
SDK_ROOT = TASK.parents[2]
REPORT_KEYS = {
    "schema_id", "task", "component", "mode", "verification_profile",
    "disposition", "status", "decision", "format", "fixture_digest",
    "fixture_spec", "candidate_settings", "source_pins", "boundary_pins",
    "mutable_provenance", "streams", "results", "controls",
    "acceptance_profile", "bundle_validation", "mdf_limitation_disclosure",
    "invalid_and_missing_cases", "qualification", "release_gates",
    "non_claims", "repeat_runs",
}
ROW_KEYS = {
    "variant", "condition", "render_mode", "status", "note", "qualifies",
    "missing_results", "far_end_erle", "near_preservation", "frames", "output",
}
ADAPTER_KEYS = {
    "protocol_version", "identity", "input_kind", "output_kinds", "tasks",
    "modes", "controls", "reference_modes", "entrypoint", "configuration_keys",
    "registration", "processor_exposure", "supported_formats", "qualification",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    print("verify: FAIL", message, file=sys.stderr)
    raise SystemExit(1)


def workspace_root() -> Path:
    for parent in TASK.parents:
        if ((parent / "research" / "aec_research_20261028.md").is_file()
                and (parent / "audio-benchmark-platform" / "plan" / "swarm"
                     / "VERIFICATION.md").is_file()):
            return parent
    fail("workspace root with pinned research and plan files not found")
    raise AssertionError("unreachable")


def read_strict_json(path: Path) -> Dict[str, Any]:
    """Reject duplicate keys and nonfinite JSON constants."""

    def pairs(items: Any) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                fail("duplicate JSON key in %s: %s" % (path.name, key))
            result[key] = value
        return result

    def constant(token: str) -> None:
        fail("nonfinite JSON constant in %s: %s" % (path.name, token))

    try:
        data = json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as error:
        fail("invalid JSON in %s: %s" % (path.name, error))
    if not isinstance(data, dict):
        fail("JSON root is not an object: " + path.name)
    return data


def _assert_finite(value: Any, where: str) -> None:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            fail("nonfinite number at " + where)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_finite(item, "%s.%s" % (where, key))
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _assert_finite(item, "%s[%d]" % (where, index))
        return
    if isinstance(value, int):
        return
    fail("unexpected JSON value type at " + where)


def check_schema(contract: Dict[str, Any], report: Dict[str, Any],
                 adapter_manifest: Dict[str, Any]) -> None:
    if set(adapter_manifest) != ADAPTER_KEYS:
        fail("adapter.json key set differs from the pinned schema")
    if set(report) != REPORT_KEYS:
        fail("report.json key set differs from the pinned schema")
    if report["schema_id"] != reference.SCHEMA_ID:
        fail("report schema_id mismatch")
    if set(report["results"]) != set(fixture.CONDITIONS):
        fail("report conditions differ from the frozen cohort")
    for condition, variants in report["results"].items():
        expected = {"identity", reference.CANDIDATE}
        if condition != "no_reference":
            expected |= set(reference.CONTROLS[1:])
        if set(variants) != expected:
            fail("report variants mismatch for " + condition)
        for variant, row in variants.items():
            if set(row) != ROW_KEYS:
                fail("report row schema mismatch: %s/%s" % (condition, variant))
            if row["variant"] != variant or row["condition"] != condition:
                fail("report row identity mismatch: %s/%s" % (condition, variant))
    for key in ("no_tolerance_widening", "no_provider_substitution",
                "three_byte_identical_repeats", "no_tiny16_comparison"):
        if contract["decision"].get(key) is not True:
            fail("contract decision flag missing or false: " + key)
    _assert_finite(report, "report")


def check_pins(contract: Dict[str, Any], report: Dict[str, Any], root: Path) -> None:
    for name, expected in contract["source_pins"].items():
        path = root / name
        if not path.is_file():
            fail("source pin missing: " + name)
        actual = sha256(path)
        if actual != expected:
            fail("source pin mismatch: %s (%s != %s)" % (name, actual, expected))
        if report["source_pins"].get(name) != expected:
            fail("report source pin mismatch: " + name)
    for name, expected in contract["boundary_pins"].items():
        path = SDK_ROOT / name
        if not path.is_file():
            fail("boundary pin missing: " + name)
        actual = sha256(path)
        if actual != expected:
            fail("boundary pin mismatch: %s (%s != %s)" % (name, actual, expected))
        if report["boundary_pins"].get(name) != expected:
            fail("report boundary pin mismatch: " + name)

    board = root / contract["mutable_provenance"]["path"]
    actual = sha256(board) if board.is_file() else "missing"
    if actual == contract["mutable_provenance"]["sha256_at_read"]:
        print("verify: mutable board snapshot unchanged (provenance only)")
    else:
        print("verify: mutable board changed since snapshot (provenance only, not a gate)")


def check_sources_manifest() -> None:
    manifest = TASK / "SOURCES.sha256"
    if not manifest.is_file():
        fail("SOURCES.sha256 missing")
    lines = manifest.read_text(encoding="utf-8").splitlines()
    if not lines:
        fail("SOURCES.sha256 empty")
    names = set()
    for line in lines:
        expected, name = line.split("  ", 1)
        if name in names:
            fail("duplicate source manifest entry: " + name)
        names.add(name)
        path = TASK / name
        if not path.is_file():
            fail("source manifest path missing: " + name)
        if sha256(path) != expected:
            fail("source manifest digest mismatch: " + name)
    if "SOURCES.sha256" in names:
        fail("SOURCES.sha256 must not pin itself")
    for path in sorted(TASK.rglob("*")):
        if path.is_file() and path != manifest:
            relative = path.relative_to(TASK).as_posix()
            if relative not in names:
                fail("unpinned artifact: " + relative)
    print("verify: %d local artifacts pinned" % len(names))


def check_repeat_runs(report: Dict[str, Any]) -> None:
    repeat = report["repeat_runs"]
    core = dict(report)
    core.pop("repeat_runs", None)
    core_digest = fixture.sha256_bytes(fixture.canonical_bytes(core))
    if repeat["three_repeats"] != 3:
        fail("repeat_runs does not record exactly three repeats")
    if repeat["canonical_digests"] != [core_digest] * 3:
        fail("repeat_runs canonical digests are not three exact repeats")
    if repeat["byte_identical"] is not True:
        fail("repeat_runs is not byte-identical")
    print("verify: 3/3 internal canonical repeats verified (%s)" % core_digest)


def check_acceptance_profile(report: Dict[str, Any]) -> None:
    profile = report["acceptance_profile"]
    if profile["profile"] != "evidence" or profile["room_controls_applied"] is not True:
        fail("evidence/room acceptance profile not applied")
    if profile["scorer_pin_sha256"] != sha256(TASK / "scorer.py"):
        fail("scorer pin does not match task-local scorer bytes")
    if profile["cohort"] != list(fixture.CONDITIONS):
        fail("pinned cohort mismatch")
    if profile["cohort_size"] != len(fixture.CONDITIONS):
        fail("pinned cohort size mismatch")
    if profile["failed_items"] != sorted(report["invalid_and_missing_cases"]):
        fail("failed-item list mismatch")
    if profile["failed_item_count"] != len(report["invalid_and_missing_cases"]):
        fail("failed-item count mismatch")
    disclosure = report["mdf_limitation_disclosure"]
    if disclosure["source"] != reference.MDF_EVIDENCE_PATH:
        fail("MDF disclosure source mismatch")
    if (disclosure["aligned_erle_db"], disclosure["misaligned_erle_db"],
            disclosure["overlap_near_ratio"]) != (
                reference.MDF_ALIGNED_ERLE_DB,
                reference.MDF_MISALIGNED_ERLE_DB,
                reference.MDF_OVERLAP_NEAR_RATIO):
        fail("MDF disclosure values mismatch")


def _request(operation: str, condition: Optional[str] = None) -> Dict[str, Any]:
    request = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": {"kind": "component", "id": reference.COMPONENT, "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": reference.COMPONENT, "revision": 1},
        "configuration": {"variant": reference.CANDIDATE},
    }
    if condition is not None:
        request["condition"] = condition
    return request


def check_bundle_validation(report: Dict[str, Any]) -> None:
    validation = report["bundle_validation"]
    inspection = adapter.inspect(_request("inspect"))
    if inspection["registration"] != "unregistered developer-only; no installed SDK provider":
        fail("adapter inspection is not unregistered")
    if inspection["processor_exposure"] != "none":
        fail("adapter inspection exposes a processor")
    if inspection["fixture_digest"] != fixture.fixture_digest():
        fail("adapter inspection fixture digest mismatch")
    for name in ("representative_valid_result", "invalid_or_missing_case"):
        expected = validation[name]
        response = adapter.run(_request("run", expected["condition"]))
        row = report["results"][expected["condition"]][expected["variant"]]
        if response["status"] != row["status"]:
            fail("bundle response status mismatch for " + name)
        if response["qualifies"] != row["qualifies"]:
            fail("bundle response qualification mismatch for " + name)
        if response["missing_results"] != row["missing_results"]:
            fail("bundle response missing-result mismatch for " + name)
        for group in ("far_end_erle", "near_preservation"):
            if response["metrics"][group] != row[group]:
                fail("bundle response metric mismatch for %s/%s" % (name, group))
        for key, value in expected.items():
            if key in ("condition", "variant"):
                continue
            response_key = key[len("expected_"):] if key.startswith("expected_") else key
            if response[response_key] != value:
                fail("bundle validation expectation mismatch for %s/%s" % (name, key))
    print("verify: bundle validation passed (valid result + invalid/missing case)")


def check_qualification(contract: Dict[str, Any], report: Dict[str, Any]) -> None:
    if report["qualification"]["no_missing_result_may_qualify"] is not True:
        fail("missing-result rule disabled")
    for condition, variants in report["results"].items():
        for variant, row in variants.items():
            missing = reference.qualification_gate(row)
            if row["missing_results"] != missing:
                fail("stale qualification gate: %s/%s" % (condition, variant))
            if row["qualifies"] and (missing or variant != reference.CANDIDATE):
                fail("invalid qualifying row: %s/%s" % (condition, variant))
    if not all(case["qualifies"] is False
               for case in report["invalid_and_missing_cases"].values()):
        fail("invalid case qualified")
    if report["decision"]["direction"] != "defer":
        fail("decision is not defer")
    if report["decision"]["release_qualification"] != "not_qualified":
        fail("release qualification is not not_qualified")
    if report["decision"]["processor_exposure"] != "none":
        fail("processor exposure is not none")
    if (TASK / "provider").exists() or (TASK / "CMakeLists.txt").exists():
        fail("unexpected provider/CMake scope in task evidence")


def main() -> int:
    contract = read_strict_json(TASK / "contract.json")
    adapter_manifest = read_strict_json(TASK / "adapter.json")
    report_path = TASK / "report.json"
    report = read_strict_json(report_path)
    root = workspace_root()

    check_schema(contract, report, adapter_manifest)
    check_pins(contract, report, root)
    if report != reference.build_report():
        fail("report.json differs from the deterministic reference build")
    canonical = fixture.canonical_bytes(report)
    if report_path.read_bytes() != canonical:
        fail("report.json is not canonical bytes")
    canonical_digest = fixture.sha256_bytes(canonical)
    file_digest = sha256(report_path)
    if contract["report"]["canonical_sha256"] != canonical_digest:
        fail("contract canonical digest mismatch")
    if contract["report"]["file_sha256"] != file_digest:
        fail("contract file digest mismatch")
    if contract["report"]["fixture_digest"] != report["fixture_digest"]:
        fail("contract fixture digest mismatch")
    digest_file = (TASK / "report.json.sha256").read_text(encoding="utf-8").splitlines()
    if digest_file != ["%s  report.json" % canonical_digest]:
        fail("report.json.sha256 does not contain the canonical digest")
    check_sources_manifest()
    check_repeat_runs(report)
    check_acceptance_profile(report)
    check_bundle_validation(report)
    check_qualification(contract, report)

    env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"}
    report_bytes = report_path.read_bytes()
    for attempt in range(1, 4):
        regenerated = subprocess.run([sys.executable, "run.py", "--report"], cwd=TASK,
                                     capture_output=True, env=env)
        if regenerated.returncode != 0:
            fail("report regeneration %d failed: %s" % (
                attempt, regenerated.stderr.decode("utf-8", "replace")))
        if regenerated.stdout != report_bytes:
            fail("report regeneration %d is not byte-identical" % attempt)
    print("verify: 3/3 byte-identical CLI report regenerations")
    print("verify: all checks passed")
    print("verify: canonical=%s file=%s fixture=%s" % (
        canonical_digest, file_digest, report["fixture_digest"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
