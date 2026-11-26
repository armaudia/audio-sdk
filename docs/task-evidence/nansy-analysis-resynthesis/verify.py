# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verifier for the NANSY readiness package.

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
    "__future__", "ast", "hashlib", "json", "math", "os", "pathlib",
    "platform", "re", "reference", "run", "shutil", "struct", "subprocess",
    "sys", "tempfile", "typing", "unittest",
))

FORBIDDEN_MODULES = frozenset((
    "aiohttp", "diffusers", "http", "librosa", "numpy", "onnxruntime",
    "requests", "scipy", "socket", "soundfile", "ssl", "tensorflow", "torch",
    "torchaudio", "transformers", "urllib", "urllib3", "websocket",
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
    for row in rows:
        if row.endswith("plan/swarm/TASKS.json"):
            errors.append("mutable_board_file_must_not_be_pinned:" + row)


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
    if CONTRACT.read_bytes() != \
            reference.canonical_bytes(expected) + b"\n":
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
    if document.get("incomplete") is not True:
        errors.append("contract_incomplete_mismatch")
    _check_linked_row(errors, document.get("boundary", {}))
    gates = document.get("release_gates", [])
    if len(gates) != 8 or any(gate.get("status") != "blocked"
                              for gate in gates):
        errors.append("contract_eight_gates_must_be_blocked")
    if any(gate.get("qualifies") is not False for gate in gates):
        errors.append("contract_gate_qualification_must_be_false")
    if document.get("qualification", {}).get("status") != "not_qualified":
        errors.append("contract_qualification_object_mismatch")
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
    payload = reference.report_bytes()
    if document != expected:
        errors.append("report_does_not_match_builder")
    if REPORT.read_bytes() != payload:
        errors.append("report_not_canonical")
    digest = hashlib.sha256(payload).hexdigest()
    if not SIDECAR.is_file():
        errors.append("report_sidecar_missing")
    elif SIDECAR.read_text(encoding="ascii") != digest + "  report.json\n":
        errors.append("report_sidecar_mismatch")

    if document.get("schema_id") != reference.REPORT_SCHEMA_ID:
        errors.append("report_schema_mismatch")
    if document.get("decision") != "DEFER":
        errors.append("report_decision_must_be_defer")
    if document.get("status") != reference.STATUS:
        errors.append("report_status_mismatch")
    if document.get("evidence_status") != "incomplete":
        errors.append("report_evidence_status_mismatch")
    if document.get("qualification_status") != "not_qualified":
        errors.append("report_qualification_status_mismatch")
    if document.get("proposal_only") is not True:
        errors.append("report_proposal_only_mismatch")
    if document.get("incomplete") is not True:
        errors.append("report_incomplete_mismatch")

    qualification = document.get("qualification", {})
    for key in ("candidate_qualified", "qualifies", "candidate_source_present",
                "candidate_weights_present", "candidate_runtime_present",
                "candidate_output_present", "rights_cleared_input_present",
                "parity_result_present", "preservation_result_present",
                "all_required_results_present", "upstream_parity"):
        if qualification.get(key) is not False:
            errors.append("qualification_flag_must_be_false:" + key)
    if qualification.get("status") != "not_qualified":
        errors.append("qualification_status_object_mismatch")

    absence = document.get("absence_evidence", {})
    if absence.get("all_absent") is not True:
        errors.append("absence_must_be_all_absent")
    if absence.get("probe_count") != 20:
        errors.append("absence_probe_count_mismatch")
    if any(probe.get("present") is not False
           for probe in absence.get("probes", [])):
        errors.append("absence_probe_present")
    if absence.get("candidate_runtime_executed") is not False:
        errors.append("candidate_runtime_must_not_execute")
    if absence.get("weights_loaded") is not False:
        errors.append("weights_must_not_load")

    profile_rows = document.get("profile_rows", [])
    if len(profile_rows) != 12:
        errors.append("voice_profile_row_count_mismatch")
    if any(row.get("qualifies") is not False for row in profile_rows):
        errors.append("voice_profile_row_qualifies_must_be_false")
    profile = document.get("profile", {})
    if profile.get("name") != "voice":
        errors.append("profile_name_mismatch")
    if not profile.get("source_check", {}).get("all_phrases_present"):
        errors.append("voice_profile_phrases_missing")

    declaration = document.get("asset_declaration", {})
    if declaration.get("all_rejected") is not True:
        errors.append("declaration_rejections_not_all_rejected")
    if declaration.get("rejection_cases") != 46:
        errors.append("declaration_rejection_count_mismatch")
    if declaration.get("accepted_control_qualifies") is not False:
        errors.append("declaration_control_must_not_qualify")

    adverse = document.get("adverse", {})
    if not adverse.get("invalid_request", {}).get("all_rejected"):
        errors.append("invalid_requests_not_all_rejected")
    if not adverse.get("strict_json", {}).get("all_rejected"):
        errors.append("strict_json_cases_not_all_rejected")
    if not adverse.get("reset_validation", {}).get(
            "matches_expectation"):
        errors.append("reset_cases_mismatch")
    if adverse.get("missing_result", {}).get("status") != "blocked":
        errors.append("missing_result_must_be_blocked")

    matched = document.get("matched_evidence", {})
    if matched.get("real_results") != 0:
        errors.append("real_results_must_be_zero")
    if matched.get("synthetic_results") != 0:
        errors.append("synthetic_results_must_be_zero")
    for key in ("matched_cohort_present", "paired_clean_reference_present",
                "analysis_to_waveform_parity_present",
                "speech_preservation_present", "candidate_output_present"):
        if matched.get(key) is not False:
            errors.append("matched_evidence_must_be_absent:" + key)

    gates = document.get("release_gates", [])
    if len(gates) != 8:
        errors.append("report_eight_gates_required")
    if any(gate.get("status") != "blocked" for gate in gates):
        errors.append("report_gates_must_be_blocked")
    if any(gate.get("qualifies") is not False for gate in gates):
        errors.append("report_gates_must_not_qualify")

    artifacts = document.get("required_artifacts", [])
    if len(artifacts) != 7:
        errors.append("required_artifact_count_mismatch")
    present = [row.get("id") for row in artifacts if row.get("present")]
    if present != ["ART-01"]:
        errors.append("only_evidence_register_may_be_present")
    if any(row.get("sha256") is not None or row.get("revision") is not None
           for row in artifacts if row.get("id") != "ART-01"):
        errors.append("blocked_artifacts_must_not_assert_pins")

    blockers = document.get("exact_blockers", [])
    if len(blockers) != 6 or any(blocker.get("status") != "open"
                                 or blocker.get("qualifies") is not False
                                 for blocker in blockers):
        errors.append("exact_blockers_mismatch")

    boundary = document.get("boundary", {})
    _check_linked_row(errors, boundary)
    for key in ("provider_registration", "descriptor_registry_change",
                "default_selected", "public_api_abi_change",
                "installed_v0_behavior_change", "shared_build_or_ci_change",
                "candidate_code_vendored", "weights_vendored", "audio_added",
                "processed_output_added", "runtime_imported",
                "native_engine_built", "board_or_handoff_changed"):
        if boundary.get(key) is not False:
            errors.append("boundary_flag_must_be_false:" + key)

    scope = document.get("scope", {})
    for key in ("network_access", "candidate_code_downloaded",
                "candidate_code_vendored", "model_weights_downloaded",
                "model_weights_vendored", "runtime_invoked", "real_audio",
                "synthetic_speech", "processed_output_present", "listening",
                "device_timing", "benchmark_claim", "release_claim",
                "provider_registration", "descriptor_registry_change",
                "public_default", "public_api_abi_change",
                "shared_build_or_ci_change", "peer_evidence_inherited",
                "board_or_handoff_change"):
        if scope.get(key) is not False:
            errors.append("scope_flag_must_be_false:" + key)

    geometry = document.get("task_geometry", {})
    for key in ("candidate_geometry_documented", "geometry_verified",
                "reset_drain_documented"):
        if geometry.get(key) is not False:
            errors.append("geometry_flag_must_be_false:" + key)
    if document.get("public_v0_geometry", {}).get("unchanged") is not True:
        errors.append("installed_v0_geometry_must_be_unchanged")

    checks = document.get("local_harness_checks", {})
    if not all(value is True for value in checks.values()):
        errors.append("local_harness_check_failed")

    try:
        reference.assert_finite(document)
    except TypeError as error:
        errors.append("report_contains_nonfinite:" + str(error))
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
        if not text.endswith("\n"):
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
        errors.append("git_metadata_missing")
        return False
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


COLD_START_FILES = (
    "LICENSES.md",
    "README.md",
    "SOURCES.sha256.license",
    "contract.json.license",
    "reference.py",
    "report.json.license",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)

COLD_START_TARGETS = ("report.json", "report.json.sha256", "contract.json",
                      "SOURCES.sha256", "README.md")


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    for name in COLD_START_TARGETS:
        if not (HERE / name).is_file():
            errors.append("cannot_cold_start_without:" + name)
            return []
    with tempfile.TemporaryDirectory(prefix="nansy-verify-") as root:
        target = Path(root)
        for name in COLD_START_FILES:
            shutil.copy2(HERE / name, target / name)
        environment = dict(os.environ)
        environment["AUDIOML_ROOT"] = str(reference.AUDIO_ROOT)
        environment["AUDIO_SDK_ROOT"] = str(reference.SDK_ROOT)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        digests: list[str] = []
        for _ in range(3):
            result = subprocess.run(
                [sys.executable, str(target / "run.py"), "all"],
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
        for name in COLD_START_TARGETS:
            if (target / name).read_bytes() != (HERE / name).read_bytes():
                errors.append("cold_start_differs:" + name)
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
        "PASS verify.py version=%s pins=%d contract_sha256=%s "
        "report_sha256=%s gates=%d blockers=%d artifacts=%d "
        "declaration_cases=%d strict_json_cases=%d absence_probes=%d "
        "snippets=%d readme_rows=%s cold_starts=%d/3"
        % (
            platform.python_version(),
            pins,
            reference.object_digest(contract),
            hashlib.sha256(REPORT.read_bytes()).hexdigest(),
            len(report.get("release_gates", [])),
            len(report.get("exact_blockers", [])),
            len(report.get("required_artifacts", [])),
            report.get("asset_declaration", {}).get("rejection_cases", 0),
            report.get("adverse", {}).get("strict_json", {}).get(
                "strict_json_cases", 0),
            len(report.get("absence_evidence", {}).get("probes", [])),
            report.get("evidence_presence", {}).get("snippet_count", 0),
            ",".join("%s=%d" % (key, value)
                     for key, value in sorted(readme.items())),
            len(repeats),
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
