# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-DIRAC-LEGACY-ZTX package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale digests,
stale pins, a non-rate profile, a promoted DIRAC/ZTX result, a qualified claim,
an open release gate, license gaps, out-of-scope worktree changes, whitespace
damage or a dirty ``git diff --check``. Never writes.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
ALLOWED_FILES = {
    "README.md", "contract.json", "contract.json.license", "reference.py",
    "report.json", "report.json.license", "report.json.sha256",
    "report.json.sha256.license", "run.py", "SOURCES.sha256",
    "SOURCES.sha256.license", "test_reference.py", "verify.py",
}
REQUIRED_REPORT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "status", "decision", "defer_before",
    "defer_after", "evidence_status", "profile", "acceptance_profile",
    "profile_blockers", "candidate", "reference", "format", "config",
    "fixture", "surrogate_model", "scorer", "results", "rate_profile",
    "controls", "adverse_rejections", "adverse_all_rejected",
    "external_artifacts", "licensing", "caller_asset", "board_row",
    "boundary", "source_pins", "boundary_pins", "scope", "qualification",
    "exact_blockers", "release_gates", "reopen_condition", "negative_claims",
    "repeatability", "scope_note",
}
REQUIRED_CONTRACT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "reviewer", "status", "decision", "defer_before",
    "defer_after", "evidence_status", "qualification_status", "profile",
    "verification_profile", "task_prefix", "acceptance_profile", "candidate",
    "format", "config", "licensing", "surrogate_model", "scorer",
    "artifact_pins", "board_row", "boundary", "boundary_pins", "source_pins",
    "scope", "reference", "exact_blockers", "release_gates",
    "reopen_condition", "negative_claims", "caller_archive_contract",
    "invariants",
}
ALLOWED_IMPORTS = {
    "__future__", "argparse", "ast", "hashlib", "json", "math", "os",
    "pathlib", "re", "struct", "subprocess", "sys", "typing", "unittest",
    "reference", "run",
}


def _strict(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.load_strict_json(path)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict JSON failed: " + label + ": " + str(error))
        return {}
    if not isinstance(payload, dict):
        errors.append("JSON root is not an object: " + label)
        return {}
    return payload


def _eq(errors: List[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label + " (actual=" + repr(actual)
                      + ", expected=" + repr(expected) + ")")


def _false(errors: List[str], label: str, value: Any) -> None:
    if value is not False:
        errors.append(label + " is not false")


def _true(errors: List[str], label: str, value: Any) -> None:
    if value is not True:
        errors.append(label + " is not true")


def check_json_files(errors: List[str]) -> Dict[str, Any]:
    report = _strict(REPORT, errors, "report.json")
    contract = _strict(CONTRACT, errors, "contract.json")
    if report:
        expected, digest = reference.canonical_report(report)
        if REPORT.read_bytes() != expected.encode("utf-8"):
            errors.append("report.json is not canonical byte output")
        if SIDECAR.read_text(encoding="ascii") != digest + "\n":
            errors.append("report.json.sha256 is stale")
    if contract:
        if CONTRACT.read_bytes() != (
                reference.canonical_text(contract) + "\n").encode("utf-8"):
            errors.append("contract.json is not canonical byte output")
    return {"report": report, "contract": contract}


def check_pins(errors: List[str]) -> int:
    count = 0
    try:
        lines = PINS.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        errors.append("missing SOURCES.sha256: " + str(error))
        return 0
    for raw in lines:
        if not raw or raw.startswith("#"):
            continue
        count += 1
        parts = raw.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append("malformed pin line: " + repr(raw))
            continue
        digest, raw_path = parts
        if raw_path.startswith("source:"):
            path = reference.SOURCE_ROOT / raw_path.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw_path
        if not path.is_file():
            errors.append("pinned file missing: " + raw_path)
        elif reference.file_digest(path) != digest:
            errors.append("pinned bytes changed: " + raw_path)
    try:
        if PINS.read_bytes() != reference.sources_bytes():
            errors.append("SOURCES.sha256 is not the deterministic generated bytes")
    except (OSError, reference.ReferenceRejection) as error:
        errors.append("pin regeneration failed: " + str(error))
    if "TASKS.json" in PINS.read_text(encoding="utf-8"):
        errors.append("mutable task board is pinned")
    return count


def check_artifact_pins(errors: List[str], report: Dict[str, Any],
                        contract: Dict[str, Any]) -> None:
    if not report or not contract:
        return
    _report_text, report_digest = reference.canonical_report(report)
    sidecar_digest = reference.sha256_bytes((report_digest + "\n").encode("ascii"))
    expected = reference.artifact_pins(report_digest, sidecar_digest)
    _eq(errors, "artifact pins are stale", contract.get("artifact_pins"), expected)
    for name in reference.ARTIFACT_FILES:
        if not (HERE / name).is_file():
            errors.append("artifact file missing: " + name)
    for path in report.get("source_pins", {}):
        if path.endswith("TASKS.json"):
            errors.append("mutable task board is pinned in source_pins")
    for path in report.get("boundary_pins", {}):
        if path.endswith("TASKS.json"):
            errors.append("mutable task board is pinned in boundary_pins")


def check_board(errors: List[str], report: Dict[str, Any],
                contract: Dict[str, Any]) -> None:
    try:
        live = reference.board_row()
    except (OSError, reference.ReferenceRejection) as error:
        errors.append("board identity failed: " + str(error))
        return
    _eq(errors, "report board identity is stale", report.get("board_row"), live)
    _eq(errors, "contract board identity is stale",
        contract.get("board_row"), live)
    row = report.get("board_row", {})
    _false(errors, "full task board hashed", row.get("full_tasks_json_hashed"))
    stable = row.get("stable_fields", {})
    if reference.object_digest(stable) != row.get("stable_sha256"):
        errors.append("stable board hash mismatch")
    _eq(errors, "stable board task id mismatch", stable.get("id"),
        reference.TASK_ID)
    _eq(errors, "stable board component mismatch", stable.get("component"),
        reference.COMPONENT)
    _eq(errors, "stable board mode mismatch", stable.get("mode"),
        "external-adapter")


def check_report(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    missing = REQUIRED_REPORT_KEYS - set(report)
    if missing:
        errors.append("report missing sections: " + ", ".join(sorted(missing)))
        return
    _eq(errors, "report schema", report["schema_id"], reference.REPORT_SCHEMA)
    _eq(errors, "report task", report["task"], reference.TASK_ID)
    _eq(errors, "report component", report["component"], reference.COMPONENT)
    _eq(errors, "report base commit", report["base_commit"],
        reference.BASE_COMMIT)
    _eq(errors, "report branch", report["branch"], reference.BRANCH)
    _eq(errors, "report status", report["status"], reference.STATUS)
    _eq(errors, "report decision", report["decision"], "DEFER")
    _eq(errors, "report defer point", report["defer_before"],
        "opt_in_adapter_exposure")
    _eq(errors, "report defer after", report["defer_after"],
        reference.DEFER_AFTER)
    _eq(errors, "report evidence status", report["evidence_status"],
        "incomplete")
    _eq(errors, "report profile", report["profile"], "rate")

    profile = report["acceptance_profile"]
    _eq(errors, "profile name", profile.get("profile"), "rate")
    items = profile.get("required_items", {})
    _eq(errors, "rate item count", len(items), 15)
    for name, item in items.items():
        if item.get("status") != "synthetic_only":
            errors.append("rate item promoted: " + name)
        if not item.get("evidence"):
            errors.append("rate item lacks evidence: " + name)
    _eq(errors, "profile blockers", report["profile_blockers"], [])

    candidate = report["candidate"]
    vendor = candidate.get("vendor_reported", {})
    _false(errors, "candidate locally verified", vendor.get("locally_verified"))
    _false(errors, "candidate local run", vendor.get("local_run"))
    _false(errors, "candidate public source", vendor.get("public_source"))
    for key in ("legacy_artifact_present", "ztx_sdk_present",
                "evaluation_kit_present", "signed_sla_present",
                "source_present", "headers_present", "runtime_present",
                "adapter_present", "exact_geometry_documented",
                "exact_numeric_output_present", "implemented_here"):
        _false(errors, "candidate claim " + key, candidate.get(key))

    reference_record = report["reference"]
    _eq(errors, "reference status", reference_record.get("status"), "blocked")
    for key in ("source_present", "runtime_present", "headers_present",
                "implementation_present", "adapter_present",
                "exact_numeric_output_present", "is_dirac", "is_ztx",
                "uses_vendor_binary", "uses_vendor_headers"):
        _false(errors, "reference claim " + key, reference_record.get(key))

    fmt = report["format"]
    _eq(errors, "sdk rate", fmt.get("sdk_v0_sample_rate_hz"), 16000)
    _eq(errors, "sdk channels", fmt.get("sdk_v0_channels"), 1)
    _eq(errors, "sdk frame", fmt.get("sdk_v0_frame_samples"), 160)
    _eq(errors, "sdk format", fmt.get("sdk_v0_sample_format"), "float32")
    _eq(errors, "resampling", fmt.get("resampling"), "none")
    for key in ("candidate_reported_sample_rate_hz",
                "candidate_reported_block_samples",
                "candidate_reported_channel_limit"):
        if fmt.get(key) is not None:
            errors.append("format invents a candidate value: " + key)
    _false(errors, "candidate geometry documented",
           fmt.get("candidate_geometry_documented"))
    _false(errors, "candidate dynamic rate verified",
           fmt.get("candidate_dynamic_rate_verified"))

    config = report["config"]
    for key in ("candidate_runtime", "candidate_header",
                "candidate_block_size", "candidate_dynamic_rate"):
        if config.get(key) is not None:
            errors.append("config invents a candidate value: " + key)

    fixture = report["fixture"]
    _true(errors, "fixture synthetic", fixture.get("synthetic"))
    _false(errors, "fixture real speech", fixture.get("real_speech"))
    _false(errors, "fixture real music", fixture.get("real_music"))
    _false(errors, "fixture candidate audio", fixture.get("candidate_audio"))
    _eq(errors, "fixture digest", fixture.get("fixture_digest"),
        reference.fixture_digest(reference.build_fixtures()))
    _eq(errors, "fixture stimulus count", len(fixture.get("stimuli", {})), 6)

    model = report["surrogate_model"]
    _eq(errors, "surrogate pin", model.get("sha256"),
        reference.surrogate_model_digest())
    _eq(errors, "surrogate digest mismatch",
        reference.object_digest(model.get("spec", {})), model.get("sha256"))
    for key in ("is_dirac", "is_ztx", "is_candidate", "is_learned",
                "uses_weights", "uses_vendor_code", "uses_vendor_binary",
                "uses_vendor_headers", "device_timing", "listening"):
        _false(errors, "surrogate claim " + key, model.get("spec", {}).get(key))
    _false(errors, "surrogate qualified", model.get("qualifies"))

    scorer = report["scorer"]
    _eq(errors, "scorer pin", scorer.get("sha256"),
        reference.scoring_protocol_digest())
    _eq(errors, "scorer digest mismatch",
        reference.object_digest(scorer.get("spec", {})), scorer.get("sha256"))
    if model.get("sha256") == scorer.get("sha256"):
        errors.append("surrogate and scorer pins are not independent")
    _false(errors, "scorer oracle", scorer.get("oracle_used_for_score"))
    _false(errors, "scorer qualified", scorer.get("qualifies"))

    results = report["results"]
    cases = results.get("cases", {})
    _eq(errors, "case count", results.get("case_count"), len(reference.CASES))
    _eq(errors, "case dict count", len(cases), len(reference.CASES))
    _eq(errors, "adverse control count",
        results.get("adverse_control_count"), 2)
    _eq(errors, "candidate qualified count",
        results.get("candidate_qualified_count"), 0)
    computed_pass = sum(1 for case in cases.values()
                        if case.get("surrogate_checks_pass"))
    _eq(errors, "surrogate pass count", results.get(
        "surrogate_checks_pass_count"), computed_pass)
    if computed_pass >= len(cases):
        errors.append("every surrogate case claims a pass")
    for case_id, case in cases.items():
        _false(errors, "case qualified: " + case_id, case.get("qualifies"))
        _false(errors, "case candidate: " + case_id,
               case.get("candidate_qualified"))
        _false(errors, "case missing result: " + case_id,
               case.get("missing_result_promoted"))
        _eq(errors, "case duration error: " + case_id,
            case.get("duration", {}).get("error_samples"), 0)
        _eq(errors, "case nonfinite: " + case_id,
            case.get("signal", {}).get("nonfinite_samples"), 0)
        _eq(errors, "case uncovered: " + case_id,
            case.get("mapping", {}).get("uncovered_samples"), 0)
    identity = results["identity"]
    _true(errors, "identity bit exact", identity.get("bit_exact_passthrough"))
    _eq(errors, "identity error", identity.get("duration_error_samples"), 0)
    _false(errors, "identity qualifies", identity.get("qualifies"))
    partial = results["final_partial"]
    _eq(errors, "partial input", partial.get("input_samples"), 12485)
    _eq(errors, "partial input partial", partial.get("input_partial_samples"), 5)
    _eq(errors, "partial output", partial.get("output_samples"), 9988)
    _eq(errors, "partial output partial", partial.get("output_partial_samples"), 68)
    _eq(errors, "partial final window", partial.get(
        "final_window_valid_samples"), 260)
    _false(errors, "partial qualifies", partial.get("qualifies"))

    rate = report["rate_profile"]
    coverage = rate.get("coverage", {})
    _eq(errors, "rate coverage count", len(coverage), 17)
    if not all(value is True for value in coverage.values()):
        errors.append("rate coverage is incomplete")
    _false(errors, "rate candidate measured", rate.get("candidate_measured"))
    _true(errors, "rate all synthetic", rate.get("all_synthetic"))
    _false(errors, "rate qualifies", rate.get("qualifies"))

    for name, record in report["controls"].items():
        _false(errors, "control qualified: " + name, record.get("qualifies"))
        _false(errors, "control candidate: " + name,
               record.get("candidate_claim"))

    adverse = report["adverse_rejections"]
    _eq(errors, "adverse count", len(adverse),
        len(reference.REQUIRED_ADVERSE))
    _true(errors, "adverse flag", report.get("adverse_all_rejected"))
    present = set()
    for item in adverse:
        case_id = str(item.get("case_id"))
        before = item.get("state_digest_before")
        after = item.get("state_digest_after")
        if item.get("status") not in ("rejected", "metric_withheld"):
            errors.append("adverse case not rejected/withheld: " + case_id)
        if (not isinstance(before, str) or len(before) != 64
                or not isinstance(after, str) or len(after) != 64):
            errors.append("adverse case lacks measured state digests: "
                          + case_id)
            continue
        measured = before == after
        if item.get("state_unchanged") is not measured:
            errors.append("adverse state_unchanged is not the measured result: "
                          + case_id)
        if not measured:
            errors.append("adverse rejection mutated state: " + case_id)
        _false(errors, "adverse candidate: " + case_id,
               item.get("candidate_qualified"))
        present.add(item.get("case_id"))
    if not set(reference.REQUIRED_ADVERSE) <= present:
        errors.append("required adverse cases missing: "
                      + ", ".join(sorted(set(reference.REQUIRED_ADVERSE)
                                         - present)))
    for case_id in reference.WITHHELD_ADVERSE:
        record = next((item for item in adverse
                       if item.get("case_id") == case_id), None)
        if record is None or record.get("status") != "metric_withheld":
            errors.append("withheld metric is not withheld: " + case_id)

    external = report["external_artifacts"]
    _eq(errors, "external artifact status", external.get("status"), "blocked")
    _false(errors, "external artifact presence", external.get("any_present"))
    for key in ("legacy_dirac_binary_present", "ztx_sdk_present",
                "evaluation_kit_present", "vendor_headers_present",
                "signed_sla_present", "license_text_present",
                "real_corpus_present"):
        _false(errors, "external artifact " + key, external.get(key))

    licensing = report["licensing"]
    _true(errors, "license source reported", licensing.get("source_reported"))
    _eq(errors, "license review", licensing.get("review_status"), "blocked")
    for key in ("locally_verified_terms", "license_text_staged", "sla_staged",
                "evaluation_kit_staged", "redistribution_reviewed",
                "product_use_reviewed", "derivative_output_reviewed",
                "patent_indemnity_reviewed", "corpus_rights_reviewed"):
        _false(errors, "licensing claim " + key, licensing.get(key))

    caller = report["caller_asset"]
    _true(errors, "caller ownership", caller.get("asset_is_caller_owned"))
    _false(errors, "vendored asset", caller.get("asset_is_vendored"))
    _eq(errors, "caller status", caller.get("status"),
        "shape_only_not_qualified")
    _false(errors, "candidate archive validated",
           caller.get("real_candidate_archive_validated"))

    qualification = report["qualification"]
    _eq(errors, "qualification status", qualification.get("status"),
        "not_qualified")
    for key, value in qualification.items():
        if key == "status":
            continue
        _false(errors, "qualification promoted: " + key, value)

    blockers = report["exact_blockers"]
    _eq(errors, "exact blocker count", len(blockers), 8)
    _eq(errors, "exact blocker ids", [item.get("id") for item in blockers],
        ["EB-0" + str(index) for index in range(1, 9)])
    for item in blockers:
        _eq(errors, "blocker status " + str(item.get("id")),
            item.get("status"), "blocked")
        _false(errors, "blocker present " + str(item.get("id")),
               item.get("present"))
        if not item.get("requirement"):
            errors.append("blocker lacks requirement: " + str(item.get("id")))

    gates = report["release_gates"]
    _eq(errors, "release gate count", len(gates), 8)
    _eq(errors, "release gate ids", [gate.get("id") for gate in gates],
        ["RG-0" + str(index) for index in range(1, 9)])
    for gate in gates:
        _eq(errors, "gate status " + str(gate.get("id")), gate.get("status"),
            "blocked")
        if not gate.get("requirement"):
            errors.append("gate lacks requirement: " + str(gate.get("id")))

    for key, value in report["boundary"].items():
        _false(errors, "boundary claim " + key, value)
    scope = report["scope"]
    _eq(errors, "write scope", scope.get("write_scope"),
        "docs/task-evidence/dirac-legacy-ztx/ only")
    for key, value in scope.items():
        if key != "write_scope":
            _false(errors, "scope claim " + key, value)
    _eq(errors, "repeat rounds", report["repeatability"].get("rounds"), 3)
    _true(errors, "repeat identity",
          report["repeatability"].get("byte_identical"))
    if len(report.get("negative_claims", [])) < 7:
        errors.append("negative claims are too few")
    if "DEFER" not in report.get("reopen_condition", ""):
        errors.append("reopen condition omits DEFER")


def check_contract(errors: List[str], contract: Dict[str, Any],
                   report: Dict[str, Any]) -> None:
    if not contract:
        return
    missing = REQUIRED_CONTRACT_KEYS - set(contract)
    if missing:
        errors.append("contract missing sections: "
                      + ", ".join(sorted(missing)))
        return
    _eq(errors, "contract schema", contract["schema_id"],
        reference.CONTRACT_SCHEMA)
    _eq(errors, "contract task", contract["task"], reference.TASK_ID)
    _eq(errors, "contract decision", contract["decision"], "DEFER")
    _eq(errors, "contract status", contract["status"], reference.STATUS)
    _eq(errors, "contract evidence", contract["evidence_status"], "incomplete")
    _eq(errors, "contract qualification", contract["qualification_status"],
        "not_qualified")
    _eq(errors, "contract profile", contract["profile"], "rate")
    _eq(errors, "contract base", contract["base_commit"], reference.BASE_COMMIT)
    _eq(errors, "contract branch", contract["branch"], reference.BRANCH)
    _eq(errors, "contract reviewer", contract["reviewer"], reference.REVIEWER)
    _eq(errors, "contract surrogate", contract["surrogate_model"],
        report.get("surrogate_model"))
    _eq(errors, "contract scorer", contract["scorer"], report.get("scorer"))
    _eq(errors, "contract candidate", contract["candidate"],
        report.get("candidate"))
    _eq(errors, "contract gates", contract["release_gates"],
        report.get("release_gates"))
    _eq(errors, "contract blockers", contract["exact_blockers"],
        report.get("exact_blockers"))
    _eq(errors, "contract config", contract["config"], report.get("config"))
    if len(contract.get("invariants", [])) < 8:
        errors.append("contract invariants are too few")
    if "TASKS.json" in reference.canonical_text(contract.get("source_pins", {})):
        errors.append("contract pins the mutable full task board")
    if "TASKS.json" in reference.canonical_text(contract.get("boundary_pins", {})):
        errors.append("contract boundary-pins the mutable full task board")
    for path in contract.get("artifact_pins", {}):
        if path.endswith("TASKS.json"):
            errors.append("contract artifact-pins the mutable full task board")


def check_files(errors: List[str]) -> None:
    present = {path.name for path in HERE.iterdir() if path.is_file()}
    unexpected = present - ALLOWED_FILES
    missing = ALLOWED_FILES - present
    if unexpected:
        errors.append("unexpected files: " + ", ".join(sorted(unexpected)))
    if missing:
        errors.append("missing files: " + ", ".join(sorted(missing)))
    expected_sidecar = (SPDX_COPYRIGHT + "\n" + SPDX_LICENSE + "\n").encode()
    for name in LICENSE_SIDECARS:
        path = HERE / name
        if path.is_file() and path.read_bytes() != expected_sidecar:
            errors.append("bad SPDX sidecar: " + name)
    for name in ("README.md", "reference.py", "run.py", "test_reference.py",
                 "verify.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("missing SPDX header: " + name)
    for path in HERE.glob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as error:
            errors.append("python syntax error: " + path.name + ": " + str(error))
            continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]]
            for name in names:
                if name and name not in ALLOWED_IMPORTS:
                    errors.append("unexpected import in " + path.name + ": " + name)
    for name in ("report.json", "contract.json", "SOURCES.sha256"):
        if "/Users/" in (HERE / name).read_text(encoding="utf-8"):
            errors.append("absolute path leaked into " + name)


def check_readme(errors: List[str]) -> None:
    text = README.read_text(encoding="utf-8")
    for token in ("DEFER", "not_qualified", "incomplete", "proposal",
                  "RG-01", "RG-08", "SOURCES.sha256", "3x", "DIRAC", "ZTX",
                  "synthetic"):
        if token not in text:
            errors.append("README lacks required token: " + token)
    rows = re.findall(r"\| `source:([^`]+)` \| `([0-9a-f]{64})` \|", text)
    found_source = dict(rows)
    if found_source != reference.SOURCE_PINS:
        errors.append("README source digest table does not match pins")
    rows = re.findall(r"\| `sdk:([^`]+)` \| `([0-9a-f]{64})` \|", text)
    found_boundary = dict(rows)
    if found_boundary != reference.BOUNDARY_PINS:
        errors.append("README boundary digest table does not match pins")


def check_rounds(errors: List[str]) -> None:
    payloads = []
    for _ in range(3):
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        contract = reference.build_contract(report, digest)
        payloads.append((text, digest,
                         reference.canonical_text(contract) + "\n"))
    if not payloads[0] == payloads[1] == payloads[2]:
        errors.append("three cold-start rounds are not byte-identical")
    if REPORT.is_file():
        if REPORT.read_text(encoding="utf-8") != payloads[0][0]:
            errors.append("committed report.json is stale")
        if CONTRACT.read_text(encoding="utf-8") != payloads[0][2]:
            errors.append("committed contract.json is stale")
        if SIDECAR.read_text(encoding="ascii") != payloads[0][1] + "\n":
            errors.append("committed report.json.sha256 is stale")


def check_git(errors: List[str]) -> None:
    try:
        result = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "diff", "--check"],
            capture_output=True, text=True, check=False)
    except OSError as error:
        errors.append("git diff --check failed to run: " + str(error))
        return
    if result.stdout.strip() or result.returncode != 0:
        errors.append("git diff --check is not clean: "
                      + (result.stdout.strip() or result.stderr.strip()))


def main() -> int:
    errors: List[str] = []
    parsed = check_json_files(errors)
    report = parsed["report"]
    contract = parsed["contract"]
    count = check_pins(errors)
    check_artifact_pins(errors, report, contract)
    check_board(errors, report, contract)
    check_report(errors, report)
    check_contract(errors, contract, report)
    check_files(errors)
    check_readme(errors)
    check_rounds(errors)
    check_git(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error, file=sys.stderr)
        print(f"verify_failed={len(errors)}", file=sys.stderr)
        return 1
    print(f"verify_ok=1 pins={count} "
          f"report_sha256={reference.file_digest(REPORT)} "
          f"decision=DEFER qualification=not_qualified "
          f"gates_blocked=8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
