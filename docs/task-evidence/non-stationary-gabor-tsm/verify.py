# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verifier for the SDK-NON-STATIONARY-GABOR-TSM package.

Scope is checked against the dirty worktree and against the commits this
branch adds relative to the newest merge-base with ``origin/main`` (falling
back to ``main``). An unresolved base emits ``scope_base_unavailable`` and any
committed path outside the task directory emits
``base_out_of_scope_change:<path>``.
"""

from __future__ import annotations

import ast
import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = reference.WORKTREE
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_LICENSE = "SPDX-" "License-Identifier: Apache-2.0"
SPDX_TAG = "SPDX-" "License-Identifier:"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECAR_TEXT = SPDX_COPYRIGHT + "\n" + SPDX_LICENSE + "\n"

SIDECARS = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)

ALLOWED_IMPORTS = frozenset((
    "__future__", "ast", "copy", "hashlib", "json", "os", "pathlib",
    "platform", "re", "reference", "run", "shutil", "subprocess", "sys",
    "tempfile", "typing", "unittest",
))

FORBIDDEN_MODULES = frozenset((
    "aiohttp", "essentia", "ffmpeg", "http", "librosa", "ltfat", "ltfatpy",
    "numpy", "nsgt", "onnxruntime", "requests", "scipy", "socket", "soundfile",
    "ssl", "tensorflow", "torch", "torchaudio", "urllib", "urllib3",
    "websocket",
))

PIN_LINE = re.compile(r"^([0-9a-f]{64})  (\S+)$")


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append(
            "interpreter mismatch: pinned %s observed %s"
            % (reference.REQUIRED_INTERPRETER, observed))


def check_files(errors: list[str]) -> None:
    observed = {
        path.name for path in HERE.iterdir()
        if path.is_file() and not path.name.startswith(".")
    }
    extra = sorted(observed - reference.EXPECTED_DIR_FILES)
    missing = sorted(reference.EXPECTED_DIR_FILES - observed)
    if extra:
        errors.append("unexpected files: " + ",".join(extra))
    if missing:
        errors.append("missing files: " + ",".join(missing))


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in (
            (reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"),
            (reference.BOUNDARY_PINS, SDK_ROOT, "boundary")):
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                errors.append(label + "_pin_missing:" + relative)
                continue
            if reference.sha256_file(path) != expected:
                errors.append(label + "_pin_mismatch:" + relative)
            checked += 1
    return checked


def check_readme(errors: list[str]) -> dict[str, int]:
    if not README.is_file():
        errors.append("readme_missing")
        return {}
    try:
        return reference.verify_readme_digests(
            README.read_text(encoding="utf-8"))
    except ValueError as error:
        errors.append("readme_digest_table_failed:" + str(error))
        return {}


def check_sources_manifest(errors: list[str]) -> None:
    if not PINS.is_file():
        errors.append("sources_manifest_missing")
        return
    if PINS.read_bytes() != run.sources_bytes():
        errors.append("sources_manifest_drift")
    rows: dict[str, str] = {}
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        match = PIN_LINE.match(line)
        if not match:
            errors.append("malformed_sources_line:" + line[:60])
            continue
        digest, name = match.groups()
        if name in rows:
            errors.append("duplicate_sources_row:" + name)
            continue
        rows[name] = digest
    for name, digest in sorted(rows.items()):
        if name.startswith("source:"):
            path = reference.AUDIO_ROOT / name[len("source:"):]
        elif name.startswith("sdk:"):
            path = SDK_ROOT / name[len("sdk:"):]
        else:
            path = SDK_ROOT / name
        if not path.is_file():
            errors.append("sources_path_missing:" + name)
        elif reference.sha256_file(path) != digest:
            errors.append("sources_digest_mismatch:" + name)
    if reference.BOARD_TASK_ROW in rows:
        errors.append("mutable_board_file_must_not_be_pinned")


def _check_linked_row(errors: list[str], boundary: dict) -> None:
    projection = reference.board_row_projection()
    rows = reference.linked_rows()
    if boundary.get("linked_row") != projection:
        errors.append("linked_row_projection_mismatch")
    if boundary.get("linked_row_sha256") != \
            reference.board_row_digest(projection):
        errors.append("linked_row_digest_mismatch")
    if boundary.get("linked_rows") != [dict(row) for row in rows]:
        errors.append("linked_rows_projection_mismatch")
    if boundary.get("linked_rows_sha256") != \
            reference.linked_rows_digest(rows):
        errors.append("linked_rows_digest_mismatch")
    if boundary.get("board_file_pinned") is not False:
        errors.append("board_file_must_not_be_pinned")
    if boundary.get("linked_row_identity_only") is not True:
        errors.append("linked_row_identity_only_must_be_true")
    if boundary.get("mutable_board_fields_gate") is not False:
        errors.append("mutable_board_fields_must_not_gate")


def check_contract(errors: list[str]) -> dict:
    if not CONTRACT.is_file():
        errors.append("contract_json_missing")
        return {}
    try:
        document = reference.read_strict_json(CONTRACT)
    except ValueError as error:
        errors.append("contract_json_invalid:" + str(error))
        return {}
    expected = reference.build_contract()
    if document != expected:
        errors.append("contract_does_not_match_builder")
    if CONTRACT.read_bytes() != reference.canonical_bytes(expected):
        errors.append("contract_not_canonical")
    if document.get("decision") != reference.DECISION:
        errors.append("contract_decision_mismatch")
    if document.get("status") != reference.STATUS:
        errors.append("contract_status_mismatch")
    if document.get("qualification_status") != \
            reference.QUALIFICATION_STATUS:
        errors.append("contract_qualification_mismatch")
    if document.get("proposal_only") is not True:
        errors.append("contract_proposal_only_mismatch")
    _check_linked_row(errors, document.get("boundary", {}))
    return document


def check_report(errors: list[str]) -> dict:
    if not REPORT.is_file():
        errors.append("report_json_missing")
        return {}
    try:
        document = reference.read_strict_json(REPORT)
    except ValueError as error:
        errors.append("report_json_invalid:" + str(error))
        return {}
    expected = reference.build_report()
    payload, digest = reference.canonical_report(expected)
    if document != expected:
        errors.append("report_does_not_match_builder")
    if REPORT.read_bytes() != payload.encode("ascii"):
        errors.append("report_not_canonical")
    if not SIDECAR.is_file():
        errors.append("report_sidecar_missing")
    elif SIDECAR.read_text(encoding="ascii") != \
            digest + "  report.json\n":
        errors.append("report_sidecar_mismatch")

    if document.get("schema_id") != reference.REPORT_SCHEMA_ID:
        errors.append("report_schema_mismatch")
    expected_fields = {
        "task": reference.TASK,
        "component": reference.COMPONENT_ID,
        "title": reference.TASK_TITLE,
        "base_commit": reference.BASE_COMMIT,
        "branch": reference.BRANCH,
        "mode": reference.MODE,
        "profile": reference.PROFILE,
        "decision": reference.DECISION,
        "status": reference.STATUS,
        "evidence_status": reference.EVIDENCE_STATUS,
        "qualification_status": reference.QUALIFICATION_STATUS,
    }
    for key, value in expected_fields.items():
        if document.get(key) != value:
            errors.append("report_field_mismatch:" + key)
    if document.get("proposal_only") is not True or \
            document.get("incomplete") is not True:
        errors.append("report_flags_mismatch")
    if document.get("contract_sha256") != reference.object_digest(
            reference.build_contract()):
        errors.append("report_contract_digest_mismatch")
    _check_linked_row(errors, document.get("boundary", {}))

    gates = document.get("gates", [])
    expected_ids = ["RG-%02d" % index for index in range(1, 9)]
    if [gate.get("id") for gate in gates] != expected_ids:
        errors.append("report_gate_order_mismatch")
    for gate in gates:
        if gate.get("status") != "blocked":
            errors.append("gate_not_blocked:" + str(gate.get("id")))
        if gate.get("qualifies") is not False:
            errors.append("gate_qualifies:" + str(gate.get("id")))
        if gate.get("linked_row") != document.get("boundary", {}).get(
                "linked_row"):
            errors.append("gate_linked_row_mismatch:" + str(gate.get("id")))

    blockers = document.get("exact_blockers", [])
    if [row.get("id") for row in blockers] != [
            "BLK-%02d" % index for index in range(1, 7)]:
        errors.append("blocker_ids_mismatch")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            errors.append("blocker_not_open:" + str(row.get("id")))

    artifacts = document.get("required_artifacts", [])
    if [row.get("id") for row in artifacts] != [
            "ART-%02d" % index for index in range(1, 8)]:
        errors.append("artifact_ids_mismatch")
    for row in artifacts:
        if row.get("id") == "ART-01":
            if row.get("present") is not True or \
                    row.get("verified") is not True:
                errors.append("ART-01_not_present_and_verified")
        elif row.get("present") is not False or row.get("blocked") is not True:
            errors.append("artifact_not_blocked:" + str(row.get("id")))

    qualification = document.get("qualification", {})
    if qualification.get("not_qualified") is not True:
        errors.append("qualification_not_qualified_missing")
    if qualification.get("status") != reference.QUALIFICATION_STATUS:
        errors.append("qualification_status_mismatch")
    if qualification.get("all_release_gates_blocked") is not True:
        errors.append("all_release_gates_must_be_blocked")
    for key, value in qualification.items():
        if key in ("status", "readiness", "not_qualified",
                   "all_release_gates_blocked", "reason"):
            continue
        if value is not False:
            errors.append("qualification_claim_must_be_false:" + key)

    profile = document.get("rate_profile", {})
    if profile.get("profile") != reference.PROFILE:
        errors.append("rate_profile_label_mismatch")
    if profile.get("profile_satisfied") is not False:
        errors.append("rate_profile_must_not_be_satisfied")
    if profile.get("real_results") != 0:
        errors.append("rate_profile_real_results_must_be_zero")
    if profile.get("synthetic_results") != 0:
        errors.append("rate_profile_synthetic_results_must_be_zero")
    if profile.get("surrogate_present") is not False:
        errors.append("rate_profile_surrogate_must_be_absent")
    rows = profile.get("requirement_rows", [])
    if len(rows) != 13:
        errors.append("rate_profile_requirement_count_mismatch")
    if sum(1 for row in rows if row.get("status") == "blocked") != 12:
        errors.append("rate_profile_blocked_count_mismatch")
    for row in rows:
        if row.get("qualifies") is not False:
            errors.append("rate_requirement_qualifies:" + str(row.get("id")))
    check = profile.get("profile_source_check", {})
    if check.get("all_phrases_present") is not True or \
            check.get("unique_row") is not True:
        errors.append("rate_profile_source_row_check_failed")

    matched = document.get("matched_evidence", {})
    if matched.get("candidate_profile_fit") != "plausible_unverified":
        errors.append("matched_evidence_fit_mismatch")
    if matched.get("classes_pooled") is not False:
        errors.append("evidence_classes_must_not_be_pooled")
    for key in ("matched_cohort_present", "matched_baseline_present",
                "paired_clean_reference_present",
                "source_output_mapping_present",
                "same_condition_control_present",
                "listening_or_labeled_screen_present"):
        if matched.get(key) is not False:
            errors.append("matched_evidence_claim_must_be_false:" + key)

    geometry = document.get("task_geometry", {})
    if geometry.get("state") != reference.TASK_GEOMETRY_STATE:
        errors.append("task_geometry_state_mismatch")
    for key in ("audio_input_path_verified", "audio_output_path_verified",
                "geometry_documented", "geometry_verified"):
        if geometry.get(key) is not False:
            errors.append("task_geometry_claim_must_be_false:" + key)
    for key in ("sample_rate_hz", "frame_samples", "hop_samples", "channels",
                "dtype", "analysis_window_schedule", "synthesis_window",
                "dual_window_rule", "transform_length", "latency_ms",
                "reset_and_drain_policy"):
        if geometry.get(key) is not None:
            errors.append("invented_task_geometry:" + key)

    identity = document.get("source_reported_identity", {})
    for key in ("official_code_found", "immutable_revision_recorded",
                "runnable_as_released", "license_text_staged",
                "reference_vendorable", "identity_verified"):
        if identity.get(key) is not False:
            errors.append("source_identity_claim_must_be_false:" + key)

    declaration = document.get("asset_declaration", {})
    recomputed = reference.declaration_rejections()
    strict = reference.strict_json_rejections()
    if declaration.get("rejection_cases") != recomputed["cases"]:
        errors.append("declaration_case_count_mismatch")
    if declaration.get("rejection_cases", 0) < 40:
        errors.append("declaration_suite_too_small")
    if declaration.get("rejections") != recomputed["rejections"]:
        errors.append("declaration_rejection_rows_mismatch")
    if declaration.get("all_rejected") is not True:
        errors.append("declaration_must_reject_every_invalid_case")
    if declaration.get("accepted_control_sha256") != \
            reference.validate_asset_declaration(
                reference.declaration_control())["canonical_sha256"]:
        errors.append("declaration_control_digest_mismatch")
    if declaration.get("accepted_control_qualifies") is not False:
        errors.append("declaration_control_must_not_qualify")
    if declaration.get("presence_claims_rejected") is not True:
        errors.append("declaration_presence_claims_must_be_rejected")
    if declaration.get("assets_loaded") is not False:
        errors.append("declaration_must_not_load_assets")
    if declaration.get("strict_json_cases") != strict["cases"]:
        errors.append("strict_json_case_count_mismatch")
    if declaration.get("strict_json_rejections") != strict["rejections"]:
        errors.append("strict_json_rejection_rows_mismatch")
    if declaration.get("strict_json_all_rejected") is not True:
        errors.append("strict_json_must_reject_every_case")

    rate_request = document.get("rate_request", {})
    rate_rejected = reference.rate_request_rejections()
    valid = reference.validate_rate_request(
        reference.rate_request_control())
    if rate_request.get("rejection_cases") != rate_rejected["cases"]:
        errors.append("rate_request_case_count_mismatch")
    if rate_request.get("rejection_cases", 0) < 50:
        errors.append("rate_request_suite_too_small")
    if rate_request.get("rejections") != rate_rejected["rejections"]:
        errors.append("rate_request_rejection_rows_mismatch")
    if rate_request.get("all_rejected") is not True:
        errors.append("rate_request_must_reject_every_invalid_case")
    if rate_request.get("nonfinite_rejected") is not True:
        errors.append("rate_request_nonfinite_must_be_rejected")
    if rate_request.get("accepted_control_status") != \
            "deferred_missing_reference":
        errors.append("rate_request_control_must_defer")
    if rate_request.get("accepted_control_qualifies") is not False:
        errors.append("rate_request_control_must_not_qualify")
    if rate_request.get("accepted_control_executed") is not False:
        errors.append("rate_request_control_must_not_execute")
    if rate_request.get("accepted_control_sha256") != \
            valid["canonical_sha256"]:
        errors.append("rate_request_control_digest_mismatch")

    absence = document.get("absence_evidence", {})
    if absence.get("all_absent") is not True or \
            absence.get("present_count") != 0:
        errors.append("absence_probes_must_all_be_absent")
    if len(absence.get("probes", [])) != \
            reference.absence_summary()["probe_count"]:
        errors.append("absence_probe_count_mismatch")

    presence = document.get("evidence_presence", {})
    if presence.get("all_snippets_present") is not True:
        errors.append("source_snippets_missing")
    if presence.get("snippet_count") != 12:
        errors.append("source_snippet_count_mismatch")
    if presence.get("inventory_evidence_line") != 415:
        errors.append("inventory_evidence_line_mismatch")
    if presence.get("inventory_evidence_section") != "5.9":
        errors.append("inventory_evidence_section_mismatch")
    inventory = document.get("inventory_record", {})
    if inventory.get("id") != reference.COMPONENT_ID or \
            inventory.get("evidence_status") != "considered" or \
            inventory.get("disposition") != "sdk-reference" or \
            inventory.get("verification_profile") != reference.PROFILE:
        errors.append("inventory_record_mismatch")

    scope = document.get("scope", {})
    if scope.get("task_local_only") is not True:
        errors.append("scope_must_be_task_local")
    if scope.get("write_scope") != reference.WRITE_SCOPE:
        errors.append("scoped_write_scope_mismatch")
    for key, value in scope.items():
        if key in ("task_local_only", "write_scope"):
            continue
        if value is not False:
            errors.append("scope_claim_must_be_false:" + key)
    exact = document.get("exact_scope", {})
    if exact != reference.exact_scope_block():
        errors.append("exact_scope_mismatch")

    if document.get("public_v0_geometry") != reference.public_v0_geometry():
        errors.append("public_v0_geometry_changed")

    runtime = document.get("runtime_readiness", {})
    for key in ("runtime_present", "runtime_pinned", "import_attempted",
                "candidate_module_available", "nsgt_reference_present",
                "ltfat_reference_present", "license_text_staged",
                "fft_dependency_pinned", "numeric_dependency_pinned"):
        if runtime.get(key) is not False:
            errors.append("runtime_claim_must_be_false:" + key)

    for row in document.get("historical_evidence", []):
        if row.get("admitted_as_result") is not False:
            errors.append("historical_evidence_admitted_as_result")
    for row in document.get("peer_separation", []):
        if row.get("admitted_as_result") is not False or \
                row.get("inherited_metrics") is not False:
            errors.append("peer_evidence_inherited")

    try:
        reference.assert_no_float(document)
    except TypeError as error:
        errors.append("report_contains_float:" + str(error))
    return document


def _check_imports(errors: list[str], path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [(node.module or "").split(".")[0]]
        else:
            continue
        for name in names:
            if name in FORBIDDEN_MODULES:
                errors.append("forbidden_import:%s:%s" % (name, path.name))
            if name and name not in ALLOWED_IMPORTS:
                errors.append("unexpected_import:%s:%s" % (name, path.name))


def check_licensing(errors: list[str]) -> None:
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("license_sidecar_missing:" + name)
        elif path.read_text(encoding="utf-8") != SIDECAR_TEXT:
            errors.append("license_sidecar_text_mismatch:" + name)
    for name in ("README.md", "LICENSES.md"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("missing_spdx_header:" + name)
    for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        head = "\n".join(text.splitlines()[:5])
        if SPDX_COPYRIGHT not in head or SPDX_LICENSE not in head:
            errors.append("missing_inline_spdx_header:" + name)
        for number, line in enumerate(text.splitlines(), start=1):
            if number > 2 and SPDX_TAG in line:
                errors.append(
                    "inline_spdx_expression_in_literal:%s:%d"
                    % (name, number))
        _check_imports(errors, HERE / name)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in reference.FORBIDDEN_SUFFIXES:
            errors.append("forbidden_payload_file:" + path.name)
    for name in reference.EXPECTED_DIR_FILES:
        path = HERE / name
        if not path.is_file():
            continue
        payload = path.read_bytes()
        try:
            text = payload.decode("ascii")
        except UnicodeDecodeError:
            errors.append("non_ascii_evidence_file:" + name)
            continue
        if name not in ("contract.json", "report.json") and \
                not text.endswith("\n"):
            errors.append("file_must_end_with_newline:" + name)
        for number, line in enumerate(text.splitlines(), start=1):
            if line != line.rstrip(" \t"):
                errors.append("trailing_whitespace:%s:%d" % (name, number))
            if "\r" in line:
                errors.append("carriage_return:%s:%d" % (name, number))


def _run_git(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(SDK_ROOT), *arguments],
                          capture_output=True, text=True, check=False)


def check_scope(errors: list[str]) -> bool:
    if not (SDK_ROOT / ".git").exists():
        return True
    ok = True
    status = _run_git("status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0:
        errors.append("git_status_failed:" + status.stderr.strip())
        return False
    for line in status.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(reference.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
            ok = False
    for arguments in (("diff", "--check"), ("diff", "--cached", "--check")):
        diff = _run_git(*arguments)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "")
                          + "_failed:" + diff.stdout.strip())
            ok = False
    branch = _run_git("rev-parse", "--abbrev-ref", "HEAD")
    if branch.returncode == 0:
        current = branch.stdout.strip()
        if current not in ("HEAD", reference.BRANCH):
            errors.append("unexpected_branch:" + current)
            ok = False
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
        ok = False
    else:
        try:
            paths = reference.scope_changed_paths(SDK_ROOT, base)
        except ValueError as error:
            errors.append(str(error))
            ok = False
        else:
            for path in reference.scope_violations(paths):
                errors.append("base_out_of_scope_change: " + path)
                ok = False
    return ok


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    if not REPORT.is_file() or not CONTRACT.is_file() or \
            not SIDECAR.is_file():
        errors.append("cannot_cold_start_without_committed_artifacts")
        return []
    with tempfile.TemporaryDirectory(prefix="nsgt-verify-") as root:
        target = Path(root)
        shutil.copy2(HERE / "reference.py", target / "reference.py")
        shutil.copy2(HERE / "run.py", target / "run.py")
        environment = dict(os.environ)
        environment["AUDIOML_ROOT"] = str(reference.AUDIO_ROOT)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        digests: list[str] = []
        for _ in range(3):
            result = subprocess.run(
                [sys.executable, str(target / "run.py"), "report.json"],
                cwd=str(target), env=environment, capture_output=True,
                text=True)
            if result.returncode != 0:
                errors.append("cold_start_run_failed:" + result.stderr.strip())
                return digests
            digests.append(hashlib.sha256(
                (target / "report.json").read_bytes()).hexdigest())
        if len(set(digests)) != 1:
            errors.append("cold_start_not_byte_identical")
            return digests
        if (target / "report.json").read_bytes() != REPORT.read_bytes():
            errors.append("cold_start_report_differs")
        if (target / "contract.json").read_bytes() != CONTRACT.read_bytes():
            errors.append("cold_start_contract_differs")
        if (target / "report.json.sha256").read_text(
                encoding="ascii") != SIDECAR.read_text(encoding="ascii"):
            errors.append("cold_start_sidecar_differs")
    return digests


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_files(errors)
    pins = check_pins(errors)
    readme = check_readme(errors)
    check_sources_manifest(errors)
    contract = check_contract(errors)
    report = check_report(errors)
    check_licensing(errors)
    check_scope(errors)
    repeats = check_cold_start_regeneration(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error, file=sys.stderr)
        print("FAIL verification (%d errors)" % len(errors), file=sys.stderr)
        return 1
    print(
        "PASS verify.py version=%s contract_sha256=%s report_sha256=%s "
        "gates=%d blockers=%d artifacts=%d declaration_cases=%d "
        "rate_request_cases=%d strict_json_cases=%d absence_probes=%d "
        "snippets=%d readme_rows=%s cold_starts=%d/3 pins=%d"
        % (
            platform.python_version(),
            reference.object_digest(contract),
            hashlib.sha256(REPORT.read_bytes()).hexdigest(),
            len(report.get("gates", [])),
            len(report.get("exact_blockers", [])),
            len(report.get("required_artifacts", [])),
            report.get("asset_declaration", {}).get("rejection_cases", 0),
            report.get("rate_request", {}).get("rejection_cases", 0),
            report.get("asset_declaration", {}).get("strict_json_cases", 0),
            len(report.get("absence_evidence", {}).get("probes", [])),
            report.get("evidence_presence", {}).get("snippet_count", 0),
            ",".join("%s=%d" % (key, value)
                     for key, value in sorted(readme.items())),
            len(repeats),
            pins,
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
