# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the task-local evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Every check fails closed: missing or extra pins, duplicate JSON keys, nonfinite
constants, noncanonical regeneration, licensing gaps, a cleared gate, a promoted
missing result or any out-of-scope worktree change are hard failures.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

SDK_ROOT = reference.SDK_ROOT
TASK_PREFIX = reference.TASK_PREFIX
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SIDECAR_TEXT = f"{SPDX_C}\n{SPDX_L}\n"
MANIFEST_COMMENT = (
    "# SHA-256 pins for SDK-CMGAN-LITERT-COMMUNITY-PORT; source: paths are "
    "workspace-relative, worktree: is SDK-worktree-relative."
)

REPORT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "reviewer", "status", "decision", "defer_before",
    "evidence_status", "qualification_status", "profile", "acceptance_profile",
    "profile_blockers", "candidate", "reference", "format", "fixtures",
    "enhancement_profile", "identity_noisy_control", "surrogate_result",
    "clean_preservation", "peaks_and_invalid_outputs", "stoi",
    "task_matched_baseline", "alignment", "state_memory_timing",
    "unpaired_predictive_screen", "listening", "resource_usage",
    "final_partial", "streaming", "reset", "adverse_rejections",
    "adverse_all_rejected", "external_artifacts", "licensing", "caller_asset",
    "board_row", "boundary", "boundary_pins", "source_pins", "scope",
    "qualification", "exact_blockers", "release_gates", "reopen_condition",
    "negative_claims", "surrogate", "repeatability", "scope_note",
}
CONTRACT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "reviewer", "status", "decision", "defer_before",
    "evidence_status", "qualification_status", "profile", "verification_profile",
    "task_prefix", "acceptance_profile", "candidate", "format", "licensing",
    "artifact_pins", "board_row", "boundary", "boundary_pins", "source_pins",
    "scope", "reference", "exact_blockers", "release_gates", "reopen_condition",
    "negative_claims", "caller_asset_contract", "invariants",
}


def fail(message: str) -> None:
    print("verify: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def check_finite(value: Any, where: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        fail("nonfinite number: " + where)
    if isinstance(value, dict):
        for key, item in value.items():
            check_finite(item, where + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_finite(item, where + "[" + str(index) + "]")


def strict_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                fail("duplicate JSON key in " + path.name + ": " + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        fail("nonfinite JSON constant in " + path.name + ": " + token)

    try:
        value = json.loads(path.read_text(encoding="utf-8"),
                           object_pairs_hook=pairs, parse_constant=constant)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        fail("cannot parse " + path.name + ": " + str(error))
    if not isinstance(value, dict):
        fail("JSON root is not an object: " + path.name)
    check_finite(value, path.name)
    return value


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_manifest() -> dict[str, str]:
    try:
        lines = (HERE / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        fail("cannot read SOURCES.sha256: " + str(error))
    if not lines or lines[0] != MANIFEST_COMMENT:
        fail("SOURCES.sha256 header mismatch")
    result: dict[str, str] = {}
    for line in lines[1:]:
        parts = re.fullmatch(r"([0-9a-f]{64})  (\S+)", line)
        if parts is None:
            fail("malformed pin line: " + repr(line))
        digest, raw = parts.group(1), parts.group(2)
        if raw in result:
            fail("duplicate pin path: " + raw)
        result[raw] = digest
    return result


def manifest_expected_paths() -> set[str]:
    local = {"worktree:" + TASK_PREFIX + name
             for name in reference.LOCAL_PIN_FILES}
    return (set("source:" + path for path in reference.SOURCE_PINS)
            | set("worktree:" + path for path in reference.BOUNDARY_PINS)
            | local)


def check_pins(manifest: dict[str, str]) -> None:
    expected = manifest_expected_paths()
    if set(manifest) != expected:
        fail("pin set mismatch: missing=" + str(sorted(expected - set(manifest)))
             + " extra=" + str(sorted(set(manifest) - expected)))
    if "worktree:" + TASK_PREFIX + "SOURCES.sha256" in manifest:
        fail("SOURCES.sha256 must not pin itself")
    if any(raw.endswith("plan/swarm/TASKS.json") for raw in manifest):
        fail("mutable task board must not be pinned")
    for raw, digest in sorted(manifest.items()):
        if raw.startswith("source:"):
            path = reference.SOURCE_ROOT / raw.split(":", 1)[1]
        elif raw.startswith("worktree:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            fail("unsupported pin prefix: " + raw)
        if not path.is_file() or path.is_symlink():
            fail("missing or non-regular pin target: " + raw)
        if sha256(path.read_bytes()) != digest:
            fail("pin mismatch: " + raw)
    print(f"verify: {len(manifest)} source/boundary/artifact pins exact")


def check_file_set() -> None:
    expected = set(reference.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    actual = {path.name for path in HERE.iterdir()
              if path.is_file() and not path.name.startswith(".")}
    if actual != expected:
        fail("task directory file set mismatch: missing="
             + str(sorted(expected - actual))
             + " extra=" + str(sorted(actual - expected)))
    for name in expected:
        if (HERE / name).is_symlink():
            fail("symlink is not allowed: " + name)


def check_scope_status() -> None:
    try:
        output = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "status", "--porcelain", "-z"],
            check=True, capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        fail("cannot inspect worktree status: " + str(error))
    entries = [entry for entry in output.split("\0") if entry]
    for entry in entries:
        path = entry[3:] if len(entry) > 3 else entry
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path.startswith(TASK_PREFIX):
            fail("out-of-scope worktree change: " + entry)
    print(f"verify: {len(entries)} worktree changes confined to {TASK_PREFIX}")


def check_sidecars() -> None:
    for name in ("contract.json", "report.json", "report.json.sha256",
                 "SOURCES.sha256"):
        path = HERE / (name + ".license")
        if not path.is_file():
            fail("missing license sidecar: " + path.name)
        if path.read_text(encoding="utf-8") != SIDECAR_TEXT:
            fail("license sidecar text mismatch: " + path.name)
    for name in ("README.md", "reference.py", "run.py", "test_reference.py",
                 "verify.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_C not in text or SPDX_L not in text:
            fail("missing SPDX header: " + name)
    print("verify: SPDX headers and generated-artifact sidecars exact")


def check_no_promotion(value: Any, where: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"qualifies", "qualifies_candidate"} and item is not False:
                fail("promoted qualification at " + where + "." + key)
            check_no_promotion(item, where + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_no_promotion(item, where + "[" + str(index) + "]")


def check_report(report: dict[str, Any], contract: dict[str, Any],
                 manifest: dict[str, str]) -> None:
    if set(report) != REPORT_KEYS:
        fail("report key set mismatch: "
             + str(sorted(set(report) ^ REPORT_KEYS)))
    if set(contract) != CONTRACT_KEYS:
        fail("contract key set mismatch: "
             + str(sorted(set(contract) ^ CONTRACT_KEYS)))
    scalar_expectations = {
        "task": reference.TASK_ID,
        "component": reference.COMPONENT,
        "repository": reference.REPOSITORY,
        "base_commit": reference.BASE_COMMIT,
        "branch": reference.BRANCH,
        "reviewer": reference.REVIEWER,
        "profile": reference.PROFILE,
        "status": reference.STATUS,
        "decision": "DEFER",
        "defer_before": "opt_in_adapter_exposure",
        "evidence_status": "incomplete",
        "qualification_status": "not_qualified",
    }
    for key, expected in scalar_expectations.items():
        if report.get(key) != expected:
            fail("report " + key + " mismatch")
        if contract.get(key) != expected:
            fail("contract " + key + " mismatch")
    if contract["profile"] != reference.PROFILE:
        fail("contract verification profile mismatch")
    if contract["task_prefix"] != TASK_PREFIX:
        fail("contract task prefix mismatch")
    qualification = report["qualification"]
    required = {
        "status": "not_qualified", "qualifies": False,
        "all_required_results_present": False,
        "missing_result_promoted": False, "exact_source_present": False,
        "exact_weights_present": False, "exact_runtime_present": False,
        "android_target_present": False, "conversion_parity_verified": False,
        "rights_cleared_cohort": False, "geometry_documented": False,
        "baseline_run": False, "paired_si_sdr_on_real_data": False,
        "stoi_measured": False,
        "clean_preservation_measured_on_real_data": False,
        "timing_measured": False, "listening": False, "real_corpus_used": False,
    }
    for key, expected in required.items():
        if qualification.get(key) != expected:
            fail("qualification field not blocked: " + key)
    reference_block = report["reference"]
    for key in ("source_present", "weights_present", "runtime_present",
                "implementation_present", "adapter_present",
                "exact_numeric_output_present"):
        if reference_block.get(key) is not False:
            fail("reference asset promoted: " + key)
    candidate = report["candidate"]
    for key in ("source_present", "weights_present", "runtime_present",
                "android_target_present", "conversion_parity_verified",
                "exact_numeric_output_present", "geometry_documented"):
        if candidate.get(key) is not False:
            fail("candidate asset promoted: " + key)
    for key in ("pinned_revision", "model_filename", "model_byte_count",
                "model_sha256", "runtime_version", "delegate",
                "android_target", "reported_input_sample_rate_hz",
                "reported_hop_samples", "reported_content_delay_samples"):
        if candidate.get(key) is not None:
            fail("unverified candidate identity asserted: " + key)
    if report["stoi"]["status"] != "blocked_not_measured":
        fail("STOI result promoted")
    if report["task_matched_baseline"]["status"] != "blocked_not_run":
        fail("baseline result promoted")
    if report["state_memory_timing"]["status"] != "blocked_unmeasured":
        fail("timing result promoted")
    if report["listening"]["status"] != "blocked_not_run":
        fail("listening result promoted")
    if report["licensing"]["review_status"] != "blocked":
        fail("licensing review promoted")
    if report["external_artifacts"]["any_present"] is not False:
        fail("external artifact presence contradicts blocker package")
    if report["adverse_all_rejected"] is not True:
        fail("adverse matrix is not fully rejected")
    if len(report["adverse_rejections"]) < 40:
        fail("adverse matrix is too small")
    for case in report["adverse_rejections"]:
        if case["status"] != "rejected" or case["state_unchanged"] is not True:
            fail("adverse case not rejected with unchanged state: "
                 + case["case_id"])
    gates = report["release_gates"]
    if [gate["id"] for gate in gates] != [
            "RG-0" + str(index) for index in range(1, 9)]:
        fail("release gate ids mismatch")
    if any(gate["status"] != "blocked" for gate in gates):
        fail("a release gate is not blocked")
    if contract["release_gates"] != gates:
        fail("contract/report release gates differ")
    if report["repeatability"]["runs"] != 3:
        fail("repeatability run count mismatch")
    if len(set(report["repeatability"]["case_matrix_digests"])) != 1:
        fail("repeatability digest mismatch")
    if not report["streaming"]["all_match"]:
        fail("streaming block invariance failed")
    if not report["reset"]["matches_fresh"]:
        fail("reset equivalence failed")
    if not report["final_partial"]["tail_zero"]:
        fail("final partial tail is not zero")
    blockers = set(report["profile_blockers"])
    for key in ("task_matched_baseline", "stoi", "unpaired_predictive_screen",
                "listening", "alignment", "state_memory_timing",
                "heldout_qualification"):
        if key not in blockers:
            fail("required profile blocker missing: " + key)
    if report["board_row"]["stable_sha256"] != (
            reference.BOARD_ROW_STABLE_SHA256):
        fail("board stable identity mismatch")
    if report["board_row"]["full_tasks_json_hashed"] is not False:
        fail("full task board was hashed")
    for key, value in report["boundary"].items():
        if value is not False:
            fail("boundary flag is not false: " + key)
    for key, value in reference._boundary().items():
        if report["boundary"].get(key) != value:
            fail("boundary key mismatch: " + key)
    if contract["boundary"] != report["boundary"]:
        fail("contract boundary differs from report")
    if contract["scope"] != report["scope"]:
        fail("contract scope differs from report")
    if report["scope"]["synthetic_only"] is not True:
        fail("scope is not synthetic")
    if report["scope"]["task_local_only"] is not True:
        fail("scope is not task-local")
    for key in ("real_corpus", "real_audio", "weights", "litert_runtime",
                "android_device", "conversion", "device_timing", "listening",
                "runtime_invocation", "network_access", "benchmark_claim",
                "release_claim", "numeric_parity_claim", "provider_registration",
                "processor_exposure", "public_default"):
        if report["scope"].get(key) is not False:
            fail("scope claim promoted: " + key)
    if report["source_pins"] != dict(reference.SOURCE_PINS):
        fail("report source pins mismatch")
    if report["boundary_pins"] != dict(reference.BOUNDARY_PINS):
        fail("report boundary pins mismatch")
    if contract["source_pins"] != report["source_pins"]:
        fail("contract source pins differ from report")
    if contract["boundary_pins"] != report["boundary_pins"]:
        fail("contract boundary pins differ from report")
    source_pins = {key: value for key, value in manifest.items()
                   if key.startswith("source:")}
    if contract["source_pins"] != {
            key.split(":", 1)[1]: value for key, value in source_pins.items()}:
        fail("contract source pins differ from manifest")
    boundary_pins = {key.split(":", 1)[1]: value
                     for key, value in manifest.items()
                     if key.startswith("worktree:")
                     and key.split(":", 1)[1] in reference.BOUNDARY_PINS}
    if contract["boundary_pins"] != boundary_pins:
        fail("contract boundary pins differ from manifest")
    local_pins = {key[len("worktree:"):]: value
                  for key, value in manifest.items()
                  if key.startswith("worktree:")}
    for name in reference.CONTRACT_PIN_FILES:
        key = TASK_PREFIX + name
        if contract["artifact_pins"].get(key) != local_pins.get(key):
            fail("contract artifact pin mismatch: " + name)
    check_no_promotion(report, "report")
    check_no_promotion(contract, "contract")


def check_digests(report: dict[str, Any],
                  contract: dict[str, Any]) -> tuple[str, str, str]:
    report_bytes = (HERE / "report.json").read_bytes()
    report_digest = sha256(report_bytes)
    expected_sidecar = (report_digest + "  report.json\n").encode("ascii")
    if (HERE / "report.json.sha256").read_bytes() != expected_sidecar:
        fail("report.json.sha256 mismatch")
    canonical = reference.canonical_text(report) + "\n"
    if report_bytes != canonical.encode("utf-8"):
        fail("committed report is not canonical JSON")
    artifacts: dict[str, bytes] = {}
    for name in reference.LOCAL_PIN_FILES:
        if name == "contract.json":
            continue
        artifacts[name] = (HERE / name).read_bytes()
    regenerated_contract = (
        reference.canonical_text(reference.build_contract(
            report, report_digest, artifacts)) + "\n").encode("utf-8")
    if (HERE / "contract.json").read_bytes() != regenerated_contract:
        fail("committed contract does not regenerate byte-identically")
    contract_digest = sha256(regenerated_contract)
    sources_digest = sha256((HERE / "SOURCES.sha256").read_bytes())
    print(f"verify: report_sha256={report_digest} bytes={len(report_bytes)}")
    return report_digest, contract_digest, sources_digest


def check_cold_start(report_digest: str, contract_digest: str,
                     sources_digest: str) -> None:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [sys.executable, str(HERE / "run.py"), "--check"]
    observed: list[dict[str, str]] = []
    for _ in range(3):
        completed = subprocess.run(command, cwd=str(HERE), env=environment,
                                   capture_output=True, text=True)
        if completed.returncode != 0:
            fail("cold-start regeneration failed: " + completed.stderr.strip())
        fields: dict[str, str] = {}
        for token in completed.stdout.split():
            if "=" in token:
                key, value = token.split("=", 1)
                fields[key] = value
        observed.append(fields)
    first = observed[0]
    if any(item != first for item in observed[1:]):
        fail("cold-start regeneration is not byte-identical")
    expected = {
        "report_sha256": report_digest,
        "contract_sha256": contract_digest,
        "sources_sha256": sources_digest,
    }
    for key, value in expected.items():
        if first.get(key) != value:
            fail("cold-start " + key + " mismatch")
    print("verify: three cold-start regenerations are byte-identical")


def main() -> int:
    report = strict_json(HERE / "report.json")
    contract = strict_json(HERE / "contract.json")
    manifest = read_manifest()
    check_file_set()
    check_sidecars()
    check_pins(manifest)
    check_scope_status()
    check_report(report, contract, manifest)
    report_digest, contract_digest, sources_digest = check_digests(
        report, contract)
    check_cold_start(report_digest, contract_digest, sources_digest)
    print("verify: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
