# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Verify pinned sources, strict JSON, boundary, controls and exact repeats.

Usage (from the task-local directory)::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py --cli <path-to-opt-in-cli>

All generated fixture, output and build bytes stay in caller scratch. The
mutable board snapshot is reported as provenance and never gates this evidence.
The final check performs three independent ``run.py --report`` regenerations
and requires byte-identical standard output each time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Dict, Optional

import fixture
import reference
import run as adapter

TASK = Path(__file__).resolve().parent
SDK_ROOT = TASK.parents[2]
REPORT_KEYS = {
    "schema_id", "task", "component", "mode", "verification_profile",
    "disposition", "decision", "format", "fixture_digest", "fixture_spec",
    "fixture_digests", "configurations", "source_pins", "boundary_pins",
    "legacy_blob_count", "mutable_provenance", "conditions", "results",
    "controls", "near_end_preservation", "acceptance_profile",
    "mdf_limitation_disclosure", "invalid_and_missing_cases", "qualification",
    "release_gates", "non_claims", "repeat_runs",
}
ADAPTER_KEYS = {
    "protocol_version", "identity", "input_kind", "output_kinds", "tasks",
    "modes", "configuration_keys", "registration", "processor_exposure",
    "supported_formats", "provider_option", "qualification",
}
CONTRACT_KEYS = {
    "schema_id", "task", "component", "repository", "base_commit", "branch",
    "worktree", "decision", "write_scope", "acceptance_profile",
    "scorer_pin_sha256", "source_pins", "boundary_pins", "legacy_repo",
    "legacy_commit", "legacy_blobs", "mutable_provenance", "release_gates",
    "report",
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


def assert_finite(value: Any, where: str) -> None:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            fail("nonfinite number at " + where)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            assert_finite(item, "%s.%s" % (where, key))
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            assert_finite(item, "%s[%d]" % (where, index))
        return
    if isinstance(value, int):
        return
    fail("unexpected JSON value type at " + where)


def check_schema(contract: Dict[str, Any], report: Dict[str, Any],
                 adapter_manifest: Dict[str, Any]) -> None:
    if set(contract) != CONTRACT_KEYS:
        fail("contract.json key set differs from the pinned schema")
    if set(adapter_manifest) != ADAPTER_KEYS:
        fail("adapter.json key set differs from the pinned schema")
    if set(report) != REPORT_KEYS:
        fail("report.json key set differs from the pinned schema")
    if report["schema_id"] != reference.SCHEMA_ID:
        fail("report schema_id mismatch")
    if set(report["conditions"]) != set(fixture.CONDITIONS):
        fail("report conditions differ from the frozen cohort")
    if set(report["results"]) != set(fixture.CONDITIONS):
        fail("report results differ from the frozen cohort")
    for condition, variants in report["results"].items():
        if set(variants) != set(reference.VARIANTS):
            fail("report variants mismatch for " + condition)
        for variant, row in variants.items():
            if set(row) != reference.ROW_KEYS:
                fail("row key set mismatch: %s/%s" % (condition, variant))
            if row["variant"] != variant or row["condition"] != condition:
                fail("row identity mismatch: %s/%s" % (condition, variant))
            if len(row["output_digests"]) != reference.REPEAT:
                fail("row repeat count mismatch: %s/%s" % (condition, variant))
            if not row["repeat_bytes_identical"]:
                fail("row repeats differ: %s/%s" % (condition, variant))
            if row["qualifies"] is not False:
                fail("synthetic row must not qualify")
    for key in ("no_tolerance_widening", "no_provider_substitution",
                "three_byte_identical_repeats", "no_tiny16_comparison",
                "no_default_or_abi_change", "no_missing_result_may_qualify"):
        if report["qualification"].get(key) is not True:
            fail("qualification flag missing or false: " + key)
    assert_finite(report, "report")
    print("verify: strict JSON/schema checks passed")


def resolve(spec: str, root: Path, sdk: Path) -> Path:
    if spec.startswith("ws:"):
        return root / spec[3:]
    if spec.startswith("sdk:"):
        return sdk / spec[4:]
    raise ValueError("pin name must use sdk: or ws: prefix: " + spec)


def check_pins(contract: Dict[str, Any], report: Dict[str, Any], root: Path) -> int:
    for name, expected in contract["source_pins"].items():
        path = resolve(name, root, SDK_ROOT)
        if not path.is_file():
            fail("source pin missing: " + name)
        actual = sha256(path)
        if actual != expected:
            fail("source pin mismatch: %s (%s != %s)" % (name, actual, expected))
        if report["source_pins"].get(name) != expected:
            fail("report source pin mismatch: " + name)
    for name, expected in contract["boundary_pins"].items():
        path = resolve(name, root, SDK_ROOT)
        if not path.is_file():
            fail("boundary pin missing: " + name)
        actual = sha256(path)
        if actual != expected:
            fail("boundary pin mismatch: %s (%s != %s)" % (name, actual, expected))
        if report["boundary_pins"].get(name) != expected:
            fail("report boundary pin mismatch: " + name)
    if sha256(TASK / "scorer.py") != contract["scorer_pin_sha256"]:
        fail("scorer pin mismatch")
    if (report["acceptance_profile"]["scorer_pin_sha256"] !=
            contract["scorer_pin_sha256"]):
        fail("report scorer pin mismatch")
    board = resolve("ws:" + contract["mutable_provenance"]["path"], root, SDK_ROOT)
    actual_board = sha256(board) if board.is_file() else "missing"
    state = "unchanged" if actual_board == contract["mutable_provenance"]["sha256_at_read"] else "changed"
    print("verify: mutable board snapshot %s (provenance only, not a gate)" % state)
    print("verify: %d external pins checked" %
          (len(contract["source_pins"]) + len(contract["boundary_pins"])))
    return len(contract["source_pins"]) + len(contract["boundary_pins"])


def git_blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def check_legacy_blobs(contract: Dict[str, Any], root: Path,
                       legacy_repo: Optional[Path]) -> int:
    checked = 0
    for name, expected in contract["legacy_blobs"].items():
        data = resolve(name, root, SDK_ROOT).read_bytes()
        actual = git_blob_id(data)
        if actual != expected:
            fail("legacy blob mismatch %s: %s != %s" % (name, actual, expected))
        if legacy_repo is not None:
            path = name[4:]
            result = subprocess.run(
                ["git", "-C", str(legacy_repo), "rev-parse",
                 "%s:%s" % (contract["legacy_commit"], path)],
                capture_output=True, text=True)
            if result.returncode != 0 or result.stdout.strip() != expected:
                fail("legacy checkout mismatch for " + name)
        checked += 1
    return checked


def check_sources_manifest() -> None:
    manifest = TASK / "SOURCES.sha256"
    if not manifest.is_file():
        fail("SOURCES.sha256 missing")
    lines = manifest.read_text(encoding="utf-8").splitlines()
    if not lines:
        fail("SOURCES.sha256 empty")
    names: set[str] = set()
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
    digest = fixture.sha256_bytes(fixture.canonical_bytes(core))
    if repeat["three_repeats"] != reference.REPEAT:
        fail("repeat_runs count mismatch")
    if repeat["canonical_digests"] != [digest] * reference.REPEAT:
        fail("repeat canonical digests are not three exact repeats")
    if repeat["byte_identical"] is not True:
        fail("repeat_runs is not byte-identical")
    print("verify: 3/3 report-core repeats verified (%s)" % digest)


def check_acceptance_profile(contract: Dict[str, Any], report: Dict[str, Any]) -> None:
    profile = report["acceptance_profile"]
    if profile["profile"] != "room" or profile["evidence_scope"] is not True:
        fail("room acceptance profile not applied")
    if profile["room_controls_applied"] is not True:
        fail("room controls not applied")
    if profile["cohort"] != list(fixture.CONDITIONS):
        fail("pinned room cohort mismatch")
    if profile["cohort_size"] != len(fixture.CONDITIONS):
        fail("pinned room cohort size mismatch")
    if profile["failed_items"] != sorted(report["invalid_and_missing_cases"]):
        fail("failed-item list mismatch")
    if profile["failed_item_count"] != len(report["invalid_and_missing_cases"]):
        fail("failed-item count mismatch")
    if contract["acceptance_profile"]["profile"] != "room":
        fail("contract acceptance profile mismatch")
    disclosure = report["mdf_limitation_disclosure"]
    if disclosure["source"] != reference.MDF_EVIDENCE_PATH:
        fail("MDF limitation source mismatch")
    if (disclosure["aligned_erle_db"], disclosure["misaligned_erle_db"],
            disclosure["overlap_near_ratio"]) != (
                reference.MDF_ALIGNED_ERLE_DB,
                reference.MDF_MISALIGNED_ERLE_DB,
                reference.MDF_OVERLAP_NEAR_RATIO):
        fail("MDF limitation values mismatch")
    if report["legacy_blob_count"] != len(contract["legacy_blobs"]):
        fail("legacy blob count mismatch")


def check_bundle_validation(cli: Path, work: Path,
                            adapter_manifest: Dict[str, Any],
                            report: Dict[str, Any]) -> None:
    base = {
        "protocol_version": 1,
        "candidate_ref": {"kind": "component", "id": reference.COMPONENT, "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": reference.COMPONENT, "revision": 1},
        "configuration": {"variant": "mdf_postfilter"},
    }
    inspection_request = dict(base, operation="inspect")
    inspection = adapter.inspect(inspection_request)
    if inspection["registration"] != adapter_manifest["registration"]:
        fail("adapter inspection registration mismatch")
    if inspection["processor_exposure"] != "none":
        fail("adapter inspection exposes a processor")
    if inspection["fixture_digest"] != fixture.fixture_digest():
        fail("adapter inspection fixture digest mismatch")
    for condition in ("echo_only", "no_reference"):
        response = adapter.run(dict(base, operation="run", condition=condition),
                               cli, work / ("request-" + condition))
        row = report["results"][condition]["mdf_postfilter"]
        if response["status"] != row["status"]:
            fail("adapter status mismatch for " + condition)
        if response["qualifies"] != row["qualifies"]:
            fail("adapter qualification mismatch for " + condition)
        if response["missing_results"] != row["missing_results"]:
            fail("adapter missing-result mismatch for " + condition)
        if response["metrics"] != {
                "erle_db_converged": row["erle_db_converged"],
                "near_ratio_overlap": row["near_ratio_overlap"],
                "near_attenuation_db_near_only": row["near_attenuation_db_near_only"]}:
            fail("adapter metric mismatch for " + condition)
    print("verify: adapter inspect/run validation passed (valid + missing-metric case)")


def check_qualification(contract: Dict[str, Any], report: Dict[str, Any]) -> None:
    if report["qualification"]["all_rows_unqualified"] is not True:
        fail("not all rows are unqualified")
    if not all(case["qualifies"] is False and case["metrics"] is None
               for case in report["invalid_and_missing_cases"].values()):
        fail("invalid/missing case qualified")
    if report["decision"]["status"] != "defer":
        fail("decision is not defer")
    if report["decision"]["postfilter_enabled"] is not False:
        fail("postfilter is reported as enabled")
    if (TASK / "provider").exists() or (TASK / "CMakeLists.txt").exists():
        fail("unexpected provider/CMake scope in task evidence")
    if not contract["decision"]["no_public_api_abi_default_or_shared_code_change"]:
        fail("contract does not declare scope isolation")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True, type=Path,
                        help="path to the opt-in task-local CLI")
    parser.add_argument("--work", type=Path,
                        help="caller scratch directory (outside the worktree)")
    parser.add_argument("--legacy-repo", type=Path, default=None,
                        help="optional legacy cpp-library checkout for direct rev-parse")
    args = parser.parse_args()
    cli = args.cli.resolve()
    if not cli.is_file():
        fail("CLI not found: %s" % cli)
    work = args.work or Path(tempfile.mkdtemp(prefix="speex-mdf-postfilter-verify-"))

    contract = read_strict_json(TASK / "contract.json")
    adapter_manifest = read_strict_json(TASK / "adapter.json")
    report_path = TASK / "report.json"
    report = read_strict_json(report_path)
    root = workspace_root()

    check_schema(contract, report, adapter_manifest)
    external_pins = check_pins(contract, report, root)
    blobs = check_legacy_blobs(contract, root, args.legacy_repo)
    check_sources_manifest()
    check_repeat_runs(report)
    check_acceptance_profile(contract, report)
    check_bundle_validation(cli, work / "bundle", adapter_manifest, report)
    check_qualification(contract, report)

    expected = reference.build_report(cli, work / "full")
    if report != expected:
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
    sidecar = (TASK / "report.json.sha256").read_text(encoding="utf-8").splitlines()
    if sidecar != ["%s  report.json" % canonical_digest]:
        fail("report.json.sha256 does not contain the canonical digest")

    env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"}
    for attempt in range(1, 4):
        regenerated = subprocess.run(
            [sys.executable, "run.py", "--report", "--cli", str(cli),
             "--work", str(work / ("regen-%02d" % attempt))],
            cwd=TASK, capture_output=True, env=env)
        if regenerated.returncode != 0:
            fail("report regeneration %d failed: %s" %
                 (attempt, regenerated.stderr.decode("utf-8", "replace")))
        if regenerated.stdout != canonical:
            fail("report regeneration %d is not byte-identical" % attempt)
    print("verify: 3/3 byte-identical CLI report regenerations")
    print("verify: all checks passed")
    print("verify: canonical=%s file=%s fixture=%s blobs=%d external_pins=%d" %
          (canonical_digest, file_digest, report["fixture_digest"], blobs,
           external_pins))
    return 0


if __name__ == "__main__":
    sys.exit(main())
