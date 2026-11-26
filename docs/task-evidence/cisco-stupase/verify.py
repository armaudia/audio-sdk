# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the SDK-CISCO-STUPASE evidence package.

Every check fails closed: stale pins, a stale README digest table, duplicate
JSON keys, nonfinite constants, noncanonical regeneration, disposition drift, a
promoted missing result, a claimed asset, licensing gaps or any out-of-scope
worktree change is a hard failure.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402

SDK_ROOT = reference.SDK_ROOT
TASK_PREFIX = reference.TASK_PREFIX
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_TOKEN = "SPDX" "-License-Identifier:"
SIDECAR_TEXT = f"{SPDX_C}\n{SPDX_L}\n"


def fail(message: str) -> None:
    print("verify: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def check_interpreter() -> None:
    if sys.version_info[:3] != (3, 12, 16):
        fail("verify.py requires Python 3.12.16; found "
             + "%d.%d.%d" % sys.version_info[:3])


def check_finite(value: Any, where: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        fail("nonfinite number: " + where)
    if isinstance(value, dict):
        for key, item in value.items():
            check_finite(item, where + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_finite(item, where + "[" + str(index) + "]")


def strict_json(path: Path) -> Dict[str, Any]:
    def pairs(items: List[tuple]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
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


def read_manifest() -> Dict[str, str]:
    try:
        lines = (HERE / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        fail("cannot read SOURCES.sha256: " + str(error))
    if not lines or lines[0] != cli.MANIFEST_COMMENT:
        fail("SOURCES.sha256 header mismatch")
    result: Dict[str, str] = {}
    for line in lines[1:]:
        parts = re.fullmatch(r"([0-9a-f]{64})  ([^\s]+(?:\s[^\s]+)*)", line)
        if parts is None:
            fail("malformed pin line: " + repr(line))
        digest, raw = parts.group(1), parts.group(2)
        if raw in result:
            fail("duplicate pin path: " + raw)
        result[raw] = digest
    return result


def manifest_expected_paths() -> set:
    local = {f"worktree:{TASK_PREFIX}{name}" for name in reference.LOCAL_FILES}
    return ({f"source:{name}" for name in reference.SOURCE_PINS}
            | {f"worktree:{name}" for name in reference.BOUNDARY_PINS}
            | local)


def check_pins(manifest: Dict[str, str]) -> None:
    expected = manifest_expected_paths()
    if set(manifest) != expected:
        fail("pin set mismatch: missing=" + str(sorted(expected - set(manifest)))
             + " extra=" + str(sorted(set(manifest) - expected)))
    if f"worktree:{TASK_PREFIX}SOURCES.sha256" in manifest:
        fail("SOURCES.sha256 must not pin itself")
    for raw, digest in sorted(manifest.items()):
        if raw.startswith("source:"):
            path = reference.SOURCE_ROOT / raw.split(":", 1)[1]
        elif raw.startswith("worktree:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            fail("unknown pin prefix: " + raw)
        if not path.is_file() or path.is_symlink():
            fail("pin target is not a regular file: " + raw)
        if reference.sha256_file(path) != digest:
            fail("pin mismatch: " + raw)
    print(f"verify: {len(manifest)} source/boundary/artifact pins exact")


def check_readme_digest_table() -> int:
    if not (HERE / "README.md").is_file():
        fail("README.md missing")
    try:
        rows = reference.readme_pin_rows()
    except (OSError, ValueError, UnicodeError) as error:
        fail("readme_table_unreadable: " + str(error))
    if not rows:
        fail("readme_digest_table_missing")
    seen: Dict[str, str] = {}
    for path, digest in rows:
        if path in seen:
            fail("readme_duplicate_row: " + path)
        seen[path] = digest
        if path.startswith(TASK_PREFIX):
            fail("readme_row_for_local_artifact: " + path)
        try:
            target = reference.qualify_pin_path(path)
        except ValueError as error:
            fail("readme_row_path_invalid: " + str(error))
        if not target.is_file():
            fail("readme_row_target_missing: " + path)
        if reference.sha256_file(target) != digest:
            fail("readme_row_digest_stale: " + path)
    missing = sorted(set(reference.SOURCE_PINS) - set(seen))
    extra = sorted(set(seen) - set(reference.SOURCE_PINS))
    if missing or extra:
        fail("readme table set mismatch: missing=" + str(missing)
             + " extra=" + str(extra))
    for path, digest in reference.SOURCE_PINS.items():
        if seen.get(path) != digest:
            fail("readme_row_pin_disagreement: " + path)
    print(f"verify: README digest table has {len(rows)} exact source rows")
    return len(rows)


def check_source_records() -> None:
    snapshot = reference.SOURCE_ROOT / (
        "research/store/snapshots/"
        "c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7.jsonl")
    method = None
    candidate = None
    try:
        lines = snapshot.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        fail("cannot read store snapshot: " + str(error))
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            fail("invalid store snapshot line: " + str(error))
        if record.get("id") == reference.METHOD_RECORD["id"]:
            method = record
        elif record.get("id") == reference.CANDIDATE_RECORD["id"]:
            candidate = record
    if method is None or candidate is None:
        fail("pinned method/candidate record missing from store snapshot")

    payload = method.get("payload", {})
    for key in ("name", "purpose", "scope", "provenance"):
        if payload.get(key) != reference.METHOD_RECORD[key]:
            fail("method record field drift: " + key)
    if method.get("revision") != reference.METHOD_RECORD["revision"]:
        fail("method record revision drift")
    if method.get("kind") != "method":
        fail("method record kind drift")

    candidate_payload = candidate.get("payload", {})
    details = candidate_payload.get("candidate_details", {})
    eligibility = candidate_payload.get("eligibility", {})
    checks = {
        "benchmark_state": (candidate_payload.get("benchmark_state"), "not_run"),
        "code": (candidate_payload.get("code"), reference.CANDIDATE_RECORD["code"]),
        "weights": (candidate_payload.get("weights"), reference.CANDIDATE_RECORD["weights"]),
        "eligibility_state": (eligibility.get("state"),
                              reference.CANDIDATE_RECORD["eligibility_state"]),
        "eligibility_reason": (eligibility.get("reason"),
                               reference.CANDIDATE_RECORD["eligibility_reason"]),
        "architecture": (details.get("architecture"),
                         reference.CANDIDATE_RECORD["architecture"]),
        "dataset": (details.get("dataset"), reference.CANDIDATE_RECORD["dataset"]),
        "reported_only": (details.get("reported_only"), True),
        "sample_rate_hz": (details.get("sample_rate_hz"), 16000),
        "implementation_source": (candidate_payload.get("implementation_source"),
                                   reference.CANDIDATE_RECORD["implementation_source"]),
        "method_id": ((candidate_payload.get("method") or {}).get("id"),
                      reference.CANDIDATE_RECORD["method_id"]),
        "method_revision": ((candidate_payload.get("method") or {}).get("revision"),
                            reference.CANDIDATE_RECORD["method_revision"]),
    }
    for key, (actual, expected) in checks.items():
        if actual != expected:
            fail("candidate record drift: " + key)

    accounting = reference.SOURCE_ROOT / (
        "reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/"
        "candidate_accounting.csv")
    try:
        with accounting.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as error:
        fail("cannot read accounting CSV: " + str(error))
    row = next((item for item in rows
                if item.get("id") == reference.ACCOUNTING_ROW["id"]), None)
    if row is None:
        fail("accounting row missing")
    for key in ("revision", "method", "eligibility", "reason", "code", "weights"):
        if row.get(key) != str(reference.ACCOUNTING_ROW[key]):
            fail("accounting row drift: " + key)

    ledger = reference.asset_ledger_presence()
    if ledger["present"] is not True:
        fail("asset ledger missing")
    if ledger["contains_stupase_entry"] or ledger["contains_cisco_entry"]:
        fail("asset ledger contains an unexpected StuPASE/Cisco entry")
    print("verify: pinned method, candidate, accounting row and empty asset ledger exact")


def check_disposition(contract: Dict[str, Any], adapter: Dict[str, Any],
                      readiness: Dict[str, Any], report: Dict[str, Any]) -> None:
    for name, document in (("contract", contract), ("adapter", adapter),
                           ("readiness", readiness), ("report", report)):
        if document.get("decision") != reference.DECISION:
            fail(name + " decision is not DEFER")
    if contract.get("status") != reference.STATUS:
        fail("contract status drift")
    if report.get("status") != reference.STATUS:
        fail("report status drift")
    if contract.get("evidence_status") != reference.EVIDENCE_STATUS:
        fail("contract evidence status drift")
    if report.get("evidence_status") != reference.EVIDENCE_STATUS:
        fail("report evidence status drift")
    if contract.get("qualification_status") != reference.QUALIFICATION_STATUS:
        fail("contract qualification status drift")
    if readiness.get("qualification_status") != reference.QUALIFICATION_STATUS:
        fail("readiness qualification status drift")
    if report.get("qualification_status") != reference.QUALIFICATION_STATUS:
        fail("report qualification status drift")
    if contract.get("profile") != reference.PROFILE:
        fail("contract profile drift")
    if report.get("profile") != reference.PROFILE:
        fail("report profile drift")
    if contract.get("base_commit") != reference.BASE_COMMIT:
        fail("contract base commit drift")
    if report.get("base_commit") != reference.BASE_COMMIT:
        fail("report base commit drift")
    if contract.get("branch") != reference.BRANCH:
        fail("contract branch drift")
    if report.get("branch") != reference.BRANCH:
        fail("report branch drift")
    if report.get("reviewer") != reference.REVIEWER:
        fail("report reviewer drift")
    if adapter.get("registered") or adapter.get("implemented"):
        fail("adapter is not proposal-only")
    if adapter.get("enabled_by_default") or adapter.get("default_selected"):
        fail("adapter is enabled or selected")
    if readiness.get("qualified") or readiness.get("qualifying_results") != 0:
        fail("readiness is not blocked")


def check_report(report: Dict[str, Any], digest: str) -> None:
    if report.get("schema_id") != reference.SCHEMA_ID:
        fail("report schema drift")
    if report.get("task_id") != reference.TASK:
        fail("report task drift")
    if report.get("component") != reference.SLUG:
        fail("report component drift")
    if report.get("proposal_only") is not True:
        fail("report is not proposal-only")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        fail("report missing-result guard drift")
    if report.get("boundary") != reference.BOUNDARY:
        fail("report boundary drift")
    if report.get("public_v0_geometry") != reference.PUBLIC_V0_GEOMETRY:
        fail("public v0 geometry drift")
    if report.get("task_geometry") != reference.TASK_GEOMETRY:
        fail("task geometry drift")
    if report.get("source_pin_paths") != sorted(reference.SOURCE_PINS):
        fail("source pin paths mismatch")
    if report.get("boundary_pin_paths") != sorted(reference.BOUNDARY_PINS):
        fail("boundary pin paths mismatch")
    if report.get("local_file_names") != list(reference.LOCAL_FILES):
        fail("local file names mismatch")

    gates = report.get("gates")
    if not isinstance(gates, list) or len(gates) != 10:
        fail("report must have ten gates")
    expected_gate_ids = [f"RG-{index:02d}" for index in range(1, 11)]
    if [gate.get("id") for gate in gates] != expected_gate_ids:
        fail("gate ids or order drift")
    for gate in gates:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            fail("gate is not blocked: " + str(gate.get("id")))
        if not gate.get("reopen"):
            fail("gate reopen condition missing: " + str(gate.get("id")))

    blockers = report.get("exact_blockers")
    if not isinstance(blockers, list) or len(blockers) != 8:
        fail("report must have eight exact blockers")
    expected_blocker_ids = [f"BLK-{index:02d}" for index in range(1, 9)]
    if [blocker.get("id") for blocker in blockers] != expected_blocker_ids:
        fail("blocker ids or order drift")
    for blocker in blockers:
        if blocker.get("status") != "open" or blocker.get("qualifies") is not False:
            fail("blocker is not open: " + str(blocker.get("id")))
        if not blocker.get("missing") or not blocker.get("reopen"):
            fail("blocker text missing: " + str(blocker.get("id")))

    qualification = report.get("qualification", {})
    if qualification.get("qualifying_results") != 0:
        fail("qualifying results must be zero")
    if qualification.get("blocked_release_gates") != 10:
        fail("blocked gate count drift")
    if qualification.get("open_blockers") != 8:
        fail("open blocker count drift")
    for key in ("source_checkout_present", "checkpoint_files_present",
                "runtime_present"):
        if qualification.get(key) is not False:
            fail("qualification presence flag drift: " + key)

    boundary = report.get("asset_boundary", {})
    if boundary.get("source_commit") != reference.SOURCE_COMMIT:
        fail("source commit drift")
    if boundary.get("hub_revision") != reference.HUB_REVISION:
        fail("hub revision drift")
    if boundary.get("asset_count") != 3:
        fail("asset count drift")
    if boundary.get("checkpoint_total_bytes") != reference.TOTAL_CHECKPOINT_BYTES:
        fail("checkpoint total drift")
    assets = boundary.get("assets")
    if not isinstance(assets, list) or len(assets) != 3:
        fail("asset list drift")
    for asset, expected in zip(assets, reference.EXTERNAL_ASSETS):
        for key in ("id", "path", "byte_count", "sha256", "role", "format", "url"):
            if asset.get(key) != expected[key]:
                fail("asset field drift: " + expected["id"] + "." + key)
        for key in ("present_locally", "admitted", "bytes_read",
                    "verified_locally", "qualifies"):
            if asset.get(key) is not False:
                fail("asset claim drift: " + expected["id"] + "." + key)
    config = boundary.get("config", {})
    for key in ("id", "path", "byte_count", "sha256", "role", "url"):
        if config.get(key) != reference.EXTERNAL_CONFIG[key]:
            fail("config field drift: " + key)
    for key in ("present_locally", "admitted", "bytes_read",
                "verified_locally", "qualifies"):
        if config.get(key) is not False:
            fail("config claim drift: " + key)
    candidate = boundary.get("candidate_admission", {})
    if candidate.get("admitted") is not False or candidate.get("accepted") is not False:
        fail("candidate admission was promoted")
    if candidate.get("qualifies") is not False:
        fail("candidate admission qualifies")
    synthetic_present = boundary.get("synthetic_present_control", {})
    if synthetic_present.get("admitted") is not True:
        fail("synthetic present control did not exercise admission")
    if synthetic_present.get("qualifies") is not False:
        fail("synthetic present control qualifies")
    if boundary.get("weights_downloaded") is not False:
        fail("weights download claim")
    if boundary.get("asset_bytes_read") is not False:
        fail("asset bytes read claim")

    presence = report.get("source_presence", {})
    if presence.get("present_probes") != []:
        fail("a source/checkpoint probe is present")
    for key in ("source_checkout_present", "checkpoint_files_present",
                "weights_present", "runtime_present", "audio_fixtures_present"):
        if presence.get(key) is not False:
            fail("presence claim drift: " + key)
    if presence.get("candidate_record") != reference.CANDIDATE_RECORD:
        fail("candidate record drift")
    if presence.get("method_record") != reference.METHOD_RECORD:
        fail("method record drift")
    if presence.get("accounting_row") != reference.ACCOUNTING_ROW:
        fail("accounting row drift")
    if presence.get("inventory_component") != reference.INVENTORY_COMPONENT:
        fail("inventory component drift")
    if presence.get("asset_ledger") != reference.asset_ledger_presence():
        fail("asset ledger presence drift")
    for line in presence.get("evidence_lines", []):
        if line.get("present") is not True or line.get("line_matches") is not True:
            fail("evidence line drift: " + str(line.get("id")))

    runtime = report.get("runtime_boundary", {})
    for key in ("runtime_vendored_in_package", "runtime_imported_by_package",
                "forward_pass_executed", "runtime_reproduced", "cuda_measured",
                "timing_measured", "memory_measured", "qualifies"):
        if runtime.get(key) is not False:
            fail("runtime claim drift: " + key)
    if runtime.get("required_python") != reference.PYTHON_PINNED:
        fail("required Python drift")
    if runtime.get("host_runtime_probe") != reference.host_runtime_probe():
        fail("host runtime probe drift")

    profile = report.get("enhancement_profile", {})
    rows = profile.get("rows", [])
    if len(rows) != 10:
        fail("enhancement row count drift")
    for row in rows:
        if row.get("qualifies") is not False:
            fail("enhancement row qualifies: " + str(row.get("id")))
    if profile.get("qualifying_results") != 0:
        fail("enhancement qualifying results must be zero")
    if profile.get("measured_candidate_results") != 0:
        fail("measured candidate results must be zero")
    for key in ("qualifies", "clean_references_present", "stoi_scorer_present",
                "listening_conducted", "device_timing_measured"):
        if profile.get(key) is not False:
            fail("enhancement claim drift: " + key)
    if profile.get("identity_noisy_control") != reference.scoring_control():
        fail("scoring control drift")
    if profile.get("frame_control") != reference.frame_control():
        fail("frame control drift")
    if profile.get("mel_geometry_control") != reference.mel_geometry_control():
        fail("Mel geometry control drift")

    licensing = report.get("licensing", {})
    if licensing.get("code_license_metadata") != reference.SOURCE_CODE_LICENSE:
        fail("code license metadata drift")
    if licensing.get("model_license_metadata") != reference.HUB_MODEL_LICENSE:
        fail("model license metadata drift")
    for key in ("weight_license_text_present", "artifact_specific_terms_reviewed",
                "training_data_obligations_reviewed", "redistribution_approved",
                "derivative_output_use_approved", "commercial_use_approved",
                "output_use_defined", "legal_review", "qualifies"):
        if licensing.get(key) is not False:
            fail("licensing claim drift: " + key)

    if report.get("linked_row") != reference.linked_row():
        fail("linked board row drift")
    if report.get("linked_row_sha256") != reference.linked_row_digest():
        fail("linked board row digest drift")

    repeat = report.get("repeatability", {})
    if repeat.get("count") != 3 or repeat.get("byte_identical") is not True:
        fail("report repeatability drift")
    if len(repeat.get("digests", [])) != 3 or len(set(repeat["digests"])) != 1:
        fail("report repeatability digests differ")
    if reference.has_negative_zero(report):
        fail("negative zero in canonical report")

    scope = report.get("scope", {})
    false_keys = (
        "benchmark_claim", "benchmark_run", "default_selected",
        "descriptor_registry_change", "device_timing_measured",
        "download_attempted", "audio_played", "audio_read",
        "installed_v0_behavior_change", "license_key_used",
        "listening_conducted", "network_used_by_package",
        "provider_registration", "public_api_abi_change",
        "release_claim", "render_produced", "shared_build_or_ci_change",
        "vendor_runtime_imported", "vendor_runtime_invoked",
        "vendor_sdk_copied", "weights_downloaded", "asset_bytes_read",
    )
    for key in false_keys:
        if scope.get(key) is not False:
            fail("scope claim drift: " + key)
    if scope.get("network_used_for_metadata") is not True:
        fail("metadata network disclosure missing")
    if scope.get("task_local_only") is not True:
        fail("task-local scope drift")

    sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    if sidecar != digest + "  report.json":
        fail("report digest sidecar mismatch")
    print("verify: report pins, assets, controls, gates and claims strict")


def check_reproduction(manifest: Dict[str, str], report_digest: str) -> None:
    if (HERE / "report.json").read_bytes() != cli.report_bytes():
        fail("report.json is not byte-reproducible")
    if (HERE / "adapter.json").read_bytes() != (
            reference.canonical_bytes(reference.build_adapter()) + b"\n"):
        fail("adapter.json is not byte-reproducible")
    if (HERE / "readiness.json").read_bytes() != (
            reference.canonical_bytes(reference.build_readiness()) + b"\n"):
        fail("readiness.json is not byte-reproducible")
    if (HERE / "contract.json").read_bytes() != cli.contract_bytes(
            cli.contract_pins(), report_digest):
        fail("contract.json is not byte-reproducible")
    if (HERE / "SOURCES.sha256").read_bytes() != cli.manifest_bytes():
        fail("SOURCES.sha256 is not byte-reproducible")
    if hashlib.sha256(cli.report_bytes()).hexdigest() != report_digest:
        fail("canonical report digest mismatch")
    code = "import hashlib,run; print(hashlib.sha256(run.report_bytes()).hexdigest())"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                capture_output=True, text=True, check=False)
        if result.returncode != 0 or result.stdout.strip() != report_digest:
            fail("cold-start reproduction failed: " + result.stderr.strip())
    print("verify: canonical artifacts, sidecar, manifest and three cold starts exact")


def check_licensing(manifest: Dict[str, str]) -> None:
    explicit = 0
    annotated = 0
    expected = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.rglob("*"), key=lambda item: item.relative_to(HERE).as_posix()):
        if not path.is_file():
            fail("non-file entry in evidence directory")
        if "__pycache__" in path.parts:
            fail("unexpected __pycache__ in evidence directory")
        name = path.relative_to(HERE).as_posix()
        if name not in expected:
            fail("file outside fail-closed local set: " + name)
        if name == "SOURCES.sha256":
            if not (HERE / "SOURCES.sha256.license").is_file():
                fail("SOURCES.sha256.license missing")
            annotated += 1
            continue
        if path.suffix == ".py":
            lines = path.read_text(encoding="utf-8").splitlines()[:3]
            if lines[:2] != ["# " + SPDX_C, "# " + SPDX_L]:
                fail("missing explicit Python SPDX header: " + name)
            if path.read_text(encoding="utf-8").count(SPDX_TOKEN) != 1:
                fail("repeated SPDX identifier token: " + name)
            explicit += 1
        elif path.suffix == ".md":
            lines = path.read_text(encoding="utf-8").splitlines()[:3]
            if lines[:2] != ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"]:
                fail("missing Markdown SPDX header: " + name)
            explicit += 1
        elif name.endswith(".license"):
            if path.read_text(encoding="utf-8") != SIDECAR_TEXT:
                fail("invalid license sidecar: " + name)
            annotated += 1
        else:
            sidecar = HERE / (name + ".license")
            if not sidecar.is_file() or sidecar.read_text(encoding="utf-8") != SIDECAR_TEXT:
                fail("missing or invalid license sidecar: " + name + ".license")
            if f"worktree:{TASK_PREFIX}{name}.license" not in manifest:
                fail("license sidecar is unpinned: " + name + ".license")
            annotated += 1
    present = {path.relative_to(HERE).as_posix()
               for path in HERE.rglob("*") if path.is_file()}
    for name in sorted(expected - present):
        fail("expected file missing: " + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        fail("REUSE.toml docs/** Apache-2.0 annotation missing")
    if not (SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        fail("LICENSES/Apache-2.0.txt missing")
    print(f"verify: {explicit} explicit SPDX files, {annotated} annotated artifacts licensed")


def check_scope() -> None:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True,
                            check=True)
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            fail("out of scope change: " + path)
    print("verify: write scope limited to the task-local evidence directory")


def main() -> int:
    check_interpreter()
    manifest = read_manifest()
    check_pins(manifest)
    check_readme_digest_table()
    check_source_records()
    contract = strict_json(HERE / "contract.json")
    adapter = strict_json(HERE / "adapter.json")
    readiness = strict_json(HERE / "readiness.json")
    report = strict_json(HERE / "report.json")
    check_disposition(contract, adapter, readiness, report)
    digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
    check_report(report, digest)
    check_reproduction(manifest, digest)
    check_licensing(manifest)
    check_scope()
    print(f"verify: PASS report_sha256={digest} status={reference.STATUS} "
          f"decision={reference.DECISION} qualification={reference.QUALIFICATION_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
