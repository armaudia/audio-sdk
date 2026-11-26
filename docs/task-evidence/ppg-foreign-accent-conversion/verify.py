# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-PPG-FOREIGN-ACCENT-CONVERSION package."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = reference.SOURCE_ROOT
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"
TEMP_ROOT = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
PIN_LINE = re.compile(r"^([0-9a-f]{64})  ((?:source|worktree|pkg):[A-Za-z0-9_./-]+)(?:  # .*)?$")
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = ("SOURCES.sha256.license", "contract.json.license", "report.json.license", "report.json.sha256.license")


def _eq(errors: List[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label)


def _strict(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.load_strict_json(path)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict JSON failed: " + label + ": " + str(error))
        return {}
    return payload


def check_json_files(errors: List[str]) -> Dict[str, Dict[str, Any]]:
    report = _strict(REPORT, errors, "report.json")
    contract = _strict(CONTRACT, errors, "contract.json")
    if report:
        text, digest = reference.canonical_report(report)
        if REPORT.read_bytes() != text.encode("utf-8"):
            errors.append("report.json is not canonical byte output")
        if not SIDECAR.is_file():
            errors.append("report.json.sha256 is missing")
        elif SIDECAR.read_text(encoding="ascii") != f"{digest}  report.json\n":
            errors.append("report.json.sha256 is stale or not sha256sum-style")
    if contract and CONTRACT.read_bytes() != (reference.canonical_text(contract) + "\n").encode("utf-8"):
        errors.append("contract.json is not canonical byte output")
    return {"report": report, "contract": contract}


def check_pins(errors: List[str]) -> int:
    try:
        lines = PINS.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        errors.append("missing SOURCES.sha256: " + str(error))
        return 0
    count = 0
    seen: set[str] = set()
    for raw in lines:
        if not raw or raw.startswith("#"):
            continue
        count += 1
        match = PIN_LINE.fullmatch(raw)
        if not match:
            errors.append("malformed pin line: " + repr(raw))
            continue
        digest, label = match.groups()
        if label in seen:
            errors.append("duplicate pin: " + label)
            continue
        seen.add(label)
        prefix, relative = label.split(":", 1)
        if relative.startswith("/") or ".." in Path(relative).parts:
            errors.append("unsafe pin path: " + label)
            continue
        base = {"source": SOURCE_ROOT, "worktree": SDK_ROOT, "pkg": HERE}[prefix]
        path = base / relative
        if not path.is_file():
            errors.append("pinned file missing: " + label)
        elif reference.file_digest(path) != digest:
            errors.append("pinned bytes changed: " + label)
    for name in reference.PIN_FILES:
        if "pkg:" + name not in seen:
            errors.append("unpinned package file: " + name)
    try:
        if PINS.read_bytes() != reference.sources_bytes():
            errors.append("SOURCES.sha256 is not the deterministic bytes")
    except (OSError, reference.Reject) as error:
        errors.append("pin regeneration failed: " + str(error))
    return count


def check_report(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    for key in ("schema_id", "task_id", "component", "title", "repository", "profile", "status", "evidence_status", "decision", "defer_before", "qualification_status", "qualification", "base_commit", "branch", "worktree", "reviewer", "format", "boundary", "scope", "task_row_identity", "source_pins", "boundary_pins", "source_reported_context", "candidate", "reference", "asset_requirements", "asset_audit", "external_artifacts", "caller_asset_contract", "acceptance_profile", "licensing", "reference_protocol", "controls", "release_gates", "exact_blockers", "reopen_conditions", "candidate_metrics", "missing_historical_artifacts", "non_claims", "tool_provenance", "repeatability", "determinism", "scope_note"):
        if key not in report:
            errors.append("report missing key: " + key)
    _eq(errors, "report schema", report.get("schema_id"), reference.SCHEMA_ID)
    _eq(errors, "report task", report.get("task_id"), reference.TASK)
    _eq(errors, "report component", report.get("component"), reference.COMPONENT)
    _eq(errors, "report profile", report.get("profile"), "voice")
    _eq(errors, "report status", report.get("status"), reference.STATUS)
    _eq(errors, "report evidence status", report.get("evidence_status"), "incomplete")
    _eq(errors, "report decision", report.get("decision"), "DEFER")
    _eq(errors, "report defer_before", report.get("defer_before"), "opt_in_adapter_exposure")
    _eq(errors, "report qualification_status", report.get("qualification_status"), "not_qualified")
    _eq(errors, "report base commit", report.get("base_commit"), reference.BASE_COMMIT)
    _eq(errors, "report branch", report.get("branch"), reference.BRANCH)
    _eq(errors, "report reviewer", report.get("reviewer"), reference.REVIEWER)

    qualification = report.get("qualification", {})
    _eq(errors, "qualification status", qualification.get("status"), "not_qualified")
    _eq(errors, "qualification decision", qualification.get("decision"), "DEFER")
    if qualification.get("candidate_qualified") is not False:
        errors.append("candidate_qualified is not false")
    if qualification.get("missing_result_promoted") is not False:
        errors.append("missing_result_promoted is not false")
    if qualification.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing-result guard missing")
    for key in ("exact_source_present", "exact_weights_present", "exact_runtime_outputs_present", "rights_cleared_cohort", "geometry_documented", "parity_measured", "timing_measured", "listening", "real_corpus_used"):
        if qualification.get(key) is not False:
            errors.append("qualification promotes missing result: " + key)

    gates = report.get("release_gates", [])
    _eq(errors, "release gate count", len(gates), 8)
    _eq(errors, "release gate IDs", [g.get("id") for g in gates], [f"RG-{i:02d}" for i in range(1, 9)])
    if any(g.get("status") != "blocked" for g in gates):
        errors.append("a release gate is not blocked")
    _eq(errors, "qualification gate count", qualification.get("blocked_gate_count"), 8)

    profile = report.get("acceptance_profile", {})
    _eq(errors, "acceptance profile", profile.get("profile"), "voice")
    items = profile.get("required_items", {})
    _eq(errors, "voice item count", len(items), 7)
    _eq(errors, "voice satisfied list", profile.get("satisfied_for_qualification"), [])
    for name, item in items.items():
        if item.get("status") not in {"absent", "not_measured", "structural_only"}:
            errors.append("voice item promoted: " + name)
        if item.get("qualification_effect") != "none":
            errors.append("voice item has qualification effect: " + name)

    candidate = report.get("candidate", {})
    for key in ("geometry_documented", "source_present", "weights_present", "runtime_present", "exact_numeric_output_present"):
        if candidate.get(key) is not False:
            errors.append("candidate claim not false: " + key)
    for key in ("reported_input_sample_rate_hz", "reported_output_sample_rate_hz", "reported_hop_samples", "reported_parameter_count"):
        if candidate.get(key) is not None:
            errors.append("candidate geometry fabricated: " + key)

    ref = report.get("reference", {})
    for key in ("source_present", "weights_present", "runtime_present", "implementation_present", "adapter_present", "exact_numeric_output_present", "surrogate_is_candidate"):
        if ref.get(key) is not False:
            errors.append("reference claim not false: " + key)
    _eq(errors, "reference status", ref.get("status"), "blocked")

    audit = report.get("asset_audit", {})
    _eq(errors, "audit result", audit.get("audit_result"), "absent")
    if audit.get("qualified") is not False:
        errors.append("asset audit qualified")
    _eq(errors, "live audit stale", audit.get("observed"), reference.audit_assets())

    control = report.get("reference_protocol", {})
    if control.get("model_executed") is not False:
        errors.append("reference protocol claims model execution")
    _eq(errors, "control qualification effect", control.get("qualification_effect"), "none")
    if control.get("reset", {}).get("matches_fresh") is not True:
        errors.append("surrogate reset mismatch")

    adverse = report.get("controls", {}).get("adverse", [])
    _eq(errors, "adverse case count", len(adverse), len(reference.ADVERSE_CASE_IDS))
    _eq(errors, "adverse IDs", [i.get("case_id") for i in adverse], list(reference.ADVERSE_CASE_IDS))
    if any(i.get("status") != "rejected" for i in adverse):
        errors.append("adverse case not rejected")
    if any(i.get("state_unchanged") is not True for i in adverse):
        errors.append("adverse case changed state")

    boundary = report.get("boundary", {})
    if not boundary or any(v is not False for v in boundary.values()):
        errors.append("boundary flag claims a change")
    scope = report.get("scope", {})
    if scope.get("synthetic_only") is not True or scope.get("task_local_only") is not True:
        errors.append("scope must be synthetic-only and task-local")
    for key, value in scope.items():
        if key in {"synthetic_only", "task_local_only"}:
            continue
        if value is not False:
            errors.append("scope flag not false: " + key)

    row = report.get("task_row_identity", {})
    if row.get("whole_file_hashed") is not False:
        errors.append("full task board hashed")
    for section in ("source_pins", "boundary_pins"):
        for path in report.get(section, {}):
            if path.endswith("TASKS.json") and section == "boundary_pins":
                errors.append("mutable task board in boundary pins")

    text = reference.canonical_text(report)
    if '"status":"qualified"' in text or '"candidate_qualified":true' in text:
        errors.append("report contains qualified claim")


def check_contract(errors: List[str], contract: Dict[str, Any], report: Dict[str, Any]) -> None:
    if not contract:
        return
    for key in ("schema_id", "task", "title", "component", "repository", "mode", "version", "base_commit", "branch", "worktree", "reviewer", "status", "decision", "defer_before", "evidence_status", "qualification_status", "profile", "verification_profile", "task_prefix", "write_scope", "acceptance_profile", "candidate", "format", "licensing", "artifact_pins", "board_row", "boundary", "boundary_pins", "source_pins", "scope", "reference", "exact_blockers", "release_gates", "reopen_condition", "negative_claims", "caller_asset_contract", "source_reported_context", "qualification", "invariants"):
        if key not in contract:
            errors.append("contract missing key: " + key)
    _eq(errors, "contract schema", contract.get("schema_id"), reference.CONTRACT_SCHEMA)
    _eq(errors, "contract task", contract.get("task"), reference.TASK)
    _eq(errors, "contract mode", contract.get("mode"), "feasibility")
    _eq(errors, "contract decision", contract.get("decision"), "DEFER")
    _eq(errors, "contract qualification", contract.get("qualification_status"), "not_qualified")
    _eq(errors, "contract profile", contract.get("profile"), "voice")
    _eq(errors, "contract write scope", contract.get("write_scope"), reference.TASK_PREFIX)
    for key in ("release_gates", "exact_blockers", "source_pins", "boundary_pins", "candidate", "format", "licensing", "acceptance_profile", "qualification", "boundary", "scope", "reference", "caller_asset_contract", "source_reported_context"):
        _eq(errors, "contract/report differ: " + key, contract.get(key), report.get(key))
    _eq(errors, "contract/report board row differ", contract.get("board_row"), report.get("task_row_identity"))
    if len(contract.get("release_gates", [])) != 8:
        errors.append("contract gate count is not eight")
    if any(g.get("status") != "blocked" for g in contract.get("release_gates", [])):
        errors.append("contract has non-blocked gate")
    if len(contract.get("exact_blockers", [])) != 8:
        errors.append("contract blocker count is not eight")
    pins = contract.get("artifact_pins", {})
    expected_names = {reference.TASK_PREFIX + name for name in reference.ARTIFACT_FILES}
    if set(pins) != expected_names:
        errors.append("artifact pin set mismatch")
    for path, digest in pins.items():
        full = SDK_ROOT / path
        if not full.is_file():
            errors.append("artifact pin missing: " + path)
        elif reference.file_digest(full) != digest:
            errors.append("artifact pin stale: " + path)
    for forbidden in ("contract.json", "SOURCES.sha256"):
        if reference.TASK_PREFIX + forbidden in pins:
            errors.append("self-referential artifact pin: " + forbidden)


def check_repeats(errors: List[str]) -> None:
    texts = [reference.canonical_report(reference.build_report())[0] for _ in range(3)]
    if len(set(texts)) != 1:
        errors.append("three fresh report builds differ")
    if texts and texts[0].encode("utf-8") != REPORT.read_bytes():
        errors.append("fresh build does not match report.json")


def check_cold_starts(errors: List[str]) -> List[str]:
    expected = reference.canonical_report(reference.build_report())[0].encode("utf-8")
    base = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    digests: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="ppg-fac-verify-", dir=base))
    except OSError as error:
        errors.append("cold-start scratch unavailable: " + str(error))
        return digests
    try:
        for index in range(3):
            target = work / f"cold-{index}"
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run([sys.executable, str(HERE / "run.py"), "--out", str(target)], cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
            generated = target / "report.json"
            if result.returncode != 0 or not generated.is_file():
                errors.append(f"cold regeneration {index} failed: " + (result.stderr.strip() or result.stdout.strip()))
                continue
            data = generated.read_bytes()
            digests.append(reference.sha256(data))
            if data != expected:
                errors.append(f"cold regeneration {index} is not byte-identical")
            sidecar = target / "report.json.sha256"
            if not sidecar.is_file() or sidecar.read_bytes() != f"{reference.sha256(data)}  report.json\n".encode("ascii"):
                errors.append(f"cold regeneration {index} sidecar differs")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if len(digests) == 3 and len(set(digests)) != 1:
        errors.append("cold-start report digests differ")
    return digests


def check_readme(errors: List[str], report: Dict[str, Any]) -> None:
    try:
        text = README.read_text(encoding="utf-8")
    except OSError as error:
        errors.append("README missing: " + str(error))
        return
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08", "voice", "PPG foreign-accent conversion", "not PPG foreign-accent conversion", "blocked", "no pretrained system suitable for an out-of-box test"):
        if token not in text:
            errors.append("README missing token: " + token)
    for digest in list(reference.SOURCE_PINS.values()) + list(reference.BOUNDARY_PINS.values()):
        if digest not in text:
            errors.append("README missing pinned digest: " + digest)
    if report and (reference.BASE_COMMIT not in text or reference.TASK not in text):
        errors.append("README missing identity")


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing SPDX header: " + path.name)
    readme_head = "\n".join(README.read_text(encoding="utf-8").splitlines()[:4])
    if SPDX_LICENSE not in readme_head or SPDX_COPYRIGHT not in readme_head:
        errors.append("README.md missing SPDX header")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("missing license sidecar: " + name)
            continue
        content = path.read_text(encoding="utf-8")
        if SPDX_LICENSE not in content or SPDX_COPYRIGHT not in content:
            errors.append("invalid license sidecar: " + name)
    reuse_path = SDK_ROOT / "REUSE.toml"
    if not reuse_path.is_file():
        errors.append("REUSE.toml missing")
        return
    reuse = reuse_path.read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or ('SPDX' '-License-Identifier = "Apache-2.0"') not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"], capture_output=True, text=True, check=True)
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    diff_check = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"], capture_output=True, text=True)
    if diff_check.returncode != 0:
        errors.append("git diff --check failed: " + (diff_check.stdout.strip() or diff_check.stderr.strip()))
    return changed


def main() -> int:
    errors: List[str] = []
    loaded = check_json_files(errors)
    report = loaded.get("report", {})
    contract = loaded.get("contract", {})
    pin_count = check_pins(errors)
    check_report(errors, report)
    check_contract(errors, contract, report)
    check_repeats(errors)
    cold = check_cold_starts(errors)
    check_readme(errors, report)
    check_licensing(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print(f"pins_ok={pin_count} json_ok=2 report_sha256={reference.file_digest(REPORT)} repeats_ok=3 cold_starts_ok={len(cold)} licensing_ok=1 scope_ok=1 changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
