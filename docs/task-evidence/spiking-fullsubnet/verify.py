# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verifier for the SDK-SPIKING-FULLSUBNET package.

Scope is checked against the dirty worktree and against the commits this
branch adds relative to the newest merge-base with ``origin/main`` (falling
back to ``main``). An unresolved base emits ``scope_base_unavailable`` and any
committed path outside the task directory emits
``base_out_of_scope_change:<path>``.
"""

from __future__ import annotations

import ast
import hashlib
import platform
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

SDK_ROOT = reference.WORKTREE
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_LICENSE = "SPDX-" "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECAR_TEXT = SPDX_COPYRIGHT + "\n" + SPDX_LICENSE + "\n"
SIDECARS = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)

ALLOWED_IMPORTS = frozenset((
    "__future__", "ast", "hashlib", "json", "os", "pathlib", "platform", "re",
    "reference", "run", "shutil", "subprocess", "sys", "tempfile", "typing",
    "unittest",
))
FORBIDDEN_MODULES = frozenset((
    "aiohttp", "http", "librosa", "numpy", "onnxruntime", "requests", "scipy",
    "socket", "soundfile", "ssl", "tensorflow", "torch", "torchaudio",
    "urllib", "urllib3", "websocket",
))


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append("interpreter_mismatch:pinned=%s:observed=%s" % (reference.REQUIRED_INTERPRETER, observed))


def check_files(errors: list[str]) -> None:
    observed = {p.name for p in HERE.iterdir() if p.is_file()}
    extra = sorted(observed - reference.EXPECTED_DIR_FILES)
    missing = sorted(reference.EXPECTED_DIR_FILES - observed)
    if extra:
        errors.append("unexpected_files:" + ",".join(extra))
    if missing:
        errors.append("missing_files:" + ",".join(missing))
    for path in HERE.rglob("*"):
        rel = path.relative_to(HERE).as_posix()
        if path.is_dir() and path.name == "__pycache__":
            errors.append("pycache_present:" + rel)
        if path.is_file() and path.suffix.lower() in (".pyc", ".pyo"):
            errors.append("compiled_python_present:" + rel)
        if path.is_file() and path.suffix.lower() in reference.FORBIDDEN_SUFFIXES:
            errors.append("forbidden_payload:" + rel)


def check_sidecars(errors: list[str]) -> None:
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("sidecar_missing:" + name)
            continue
        if path.read_text(encoding="utf-8") != SIDECAR_TEXT:
            errors.append("sidecar_content_mismatch:" + name)


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in ((reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"), (reference.BOUNDARY_PINS, reference.WORKTREE, "boundary")):
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                errors.append("%s_pin_missing:%s" % (label, relative))
                continue
            actual = reference.sha256_file(path)
            if actual != expected:
                errors.append("%s_pin_mismatch:%s" % (label, relative))
            checked += 1
    return checked


def check_readme(errors: list[str]) -> dict[str, int]:
    try:
        text = README.read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
    except (OSError, ValueError) as error:
        errors.append("readme_digest_invalid:" + str(error))
        return {}
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08", "Spiking-FullSubNet", "synthetic", "16 kHz", reference.TASK, reference.BASE_COMMIT, "not downloaded"):
        if token not in text:
            errors.append("readme_token_missing:" + token)
    if reference.BOARD_TASK_ROW in text:
        errors.append("readme_references_mutable_board_path")
    return counts


def check_sources_manifest(errors: list[str]) -> None:
    if not PINS.is_file():
        errors.append("sources_manifest_missing")
        return
    try:
        text = PINS.read_text(encoding="ascii")
    except UnicodeDecodeError:
        errors.append("sources_manifest_not_ascii")
        return
    observed: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ")
        if len(parts) != 2 or not reference.HEX64.match(parts[0]):
            errors.append("sources_manifest_bad_line:" + line[:80])
            continue
        observed[parts[1]] = parts[0]
    expected = {"source:" + k for k in reference.SOURCE_PINS}
    expected |= {"sdk:" + k for k in reference.BOUNDARY_PINS}
    expected |= {reference.TASK_PREFIX + name for name in reference.LOCAL_FILES if name != "SOURCES.sha256"}
    if set(observed) != expected:
        errors.append("sources_manifest_key_set_mismatch")
    for key, digest in observed.items():
        if key.startswith("source:"):
            path = reference.AUDIO_ROOT / key[len("source:"):]
        elif key.startswith("sdk:"):
            path = reference.WORKTREE / key[len("sdk:"):]
        else:
            path = HERE / key[len(reference.TASK_PREFIX):]
        if not path.is_file():
            errors.append("sources_manifest_path_missing:" + key)
        elif reference.sha256_file(path) != digest:
            errors.append("sources_manifest_digest_mismatch:" + key)
    if reference.TASK_PREFIX + "SOURCES.sha256" in observed:
        errors.append("sources_manifest_pins_itself")
    if "source:" + reference.BOARD_TASK_ROW in observed:
        errors.append("sources_manifest_pins_mutable_board")


def _check_linked_row(errors: list[str], document: dict) -> None:
    if document.get("board_file_pinned") is not False:
        errors.append("board_file_must_not_be_pinned")
    projection = reference.board_row_projection()
    rows = reference.linked_rows()
    if projection.get("id") != reference.TASK or projection.get("component") != reference.COMPONENT_ID:
        errors.append("board_projection_identity_mismatch")
    if tuple(r["id"] for r in rows) != reference.LINKED_ROW_IDS:
        errors.append("board_linked_rows_mismatch")
    if projection != document.get("board_row_projection"):
        errors.append("board_projection_mismatch")
    if reference.board_row_digest(projection) != document.get("board_row_sha256"):
        errors.append("board_row_digest_mismatch")
    if list(rows) != document.get("linked_rows"):
        errors.append("linked_rows_mismatch")
    if reference.linked_rows_digest(rows) != document.get("linked_rows_sha256"):
        errors.append("linked_rows_digest_mismatch")
    for field in ("status", "owner", "claim", "review", "handoff", "dispatch_priority", "blocked_reason"):
        if field in projection:
            errors.append("board_projection_includes_mutable:" + field)


def check_contract(errors: list[str]) -> dict:
    if not CONTRACT.is_file():
        errors.append("contract_missing")
        return {}
    try:
        document = reference.read_strict_json(CONTRACT)
    except (OSError, ValueError) as error:
        errors.append("contract_strict_json:" + str(error))
        return {}
    if document != reference.build_contract():
        errors.append("contract_differs_from_reference")
    for key, expected in (("decision", "DEFER"), ("status", "proposal_only_incomplete"), ("evidence_status", "incomplete"), ("qualification_status", "not_qualified"), ("defer_before", "opt_in_adapter_exposure"), ("base_commit", reference.BASE_COMMIT), ("branch", reference.BRANCH)):
        if document.get(key) != expected:
            errors.append("contract_field_mismatch:" + key)
    if document.get("incomplete") is not True or document.get("proposal_only") is not True:
        errors.append("contract_incomplete_or_proposal_flag")
    gates = document.get("release_gates") or []
    if len(gates) != 8 or any(g.get("status") != "blocked" or g.get("qualifies") is not False for g in gates):
        errors.append("contract_release_gates_invalid")
    if document.get("boundary", {}).get("provider_registration") is not False:
        errors.append("contract_provider_registration")
    if document.get("scope", {}).get("weights_vendored") is not False:
        errors.append("contract_weights_vendored")
    if document.get("public_v0_geometry") != reference.public_v0_geometry():
        errors.append("contract_public_v0_geometry_mismatch")
    try:
        reference.assert_no_float(document)
    except TypeError as error:
        errors.append("contract_contains_float:" + str(error))
    _check_linked_row(errors, document)
    return document


def check_report(errors: list[str]) -> dict:
    if not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("report_or_sidecar_missing")
        return {}
    payload = REPORT.read_bytes()
    try:
        document = reference.parse_strict_json_text(payload)
    except ValueError as error:
        errors.append("report_strict_json:" + str(error))
        return {}
    if payload != reference.canonical_bytes(reference.build_report()):
        errors.append("report_differs_from_reference")
    digest = hashlib.sha256(payload).hexdigest()
    if SIDECAR.read_text(encoding="ascii") != "%s  report.json\n" % digest:
        errors.append("report_sidecar_mismatch")
    for key, expected in (("decision", "DEFER"), ("status", "proposal_only_incomplete"), ("evidence_status", "incomplete"), ("qualification_status", "not_qualified")):
        if document.get(key) != expected:
            errors.append("report_field_mismatch:" + key)
    if document.get("qualification", {}).get("status") != "not_qualified":
        errors.append("report_qualification_status")
    if document.get("qualification", {}).get("real_result_present") is not False:
        errors.append("report_real_result_present")
    if document.get("qualification", {}).get("missing_result_promoted") is not False:
        errors.append("report_missing_result_promoted")
    gates = document.get("release_gates") or []
    if len(gates) != 8 or any(g.get("status") != "blocked" or g.get("qualifies") is not False for g in gates):
        errors.append("report_release_gates_invalid")
    adm = document.get("admission", {})
    if adm.get("admissible") is not False or adm.get("status") != "DEFER":
        errors.append("report_admission_invalid")
    control = document.get("declaration_control", {})
    if control.get("accepted") is not True or control.get("qualifies") is not False or control.get("synthetic_schema_control") is not True:
        errors.append("report_synthetic_control_invalid")
    rej = document.get("declaration_rejections", {})
    if not rej.get("all_rejected"):
        errors.append("report_declaration_rejections_invalid")
    if document.get("reported_metrics", {}).get("admitted_as_result") is not False:
        errors.append("report_metrics_admitted")
    for banned in ("real_runtime_result", "paired_si_sdr_result", "paired_stoi_result"):
        if banned in document.get("qualification", {}):
            errors.append("report_unexpected_qualification_field:" + banned)
    try:
        reference.assert_no_float(document)
    except TypeError as error:
        errors.append("report_contains_float:" + str(error))
    _check_linked_row(errors, document)
    return document


def check_imports(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        except SyntaxError as error:
            errors.append("syntax_error:%s:%s" % (path.name, error))
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in FORBIDDEN_MODULES:
                        errors.append("forbidden_import:%s:%s" % (path.name, alias.name))
                    if root not in ALLOWED_IMPORTS and root not in {"reference", "run"}:
                        # allow stdlib by module name only when in allowlist for local scripts
                        if path.name in {"reference.py", "run.py", "verify.py", "test_reference.py"} and root not in ALLOWED_IMPORTS:
                            errors.append("unlisted_import:%s:%s" % (path.name, alias.name))
            if isinstance(node, ast.ImportFrom):
                mod = (node.module or "").split(".")[0]
                if mod in FORBIDDEN_MODULES:
                    errors.append("forbidden_import:%s:%s" % (path.name, node.module))
                if mod and mod not in ALLOWED_IMPORTS and mod not in {"reference", "run"}:
                    if path.name in {"reference.py", "run.py", "verify.py", "test_reference.py"} and mod not in ALLOWED_IMPORTS:
                        errors.append("unlisted_import:%s:%s" % (path.name, node.module))


def check_scope(errors: list[str]) -> dict:
    status = reference.scope_status(SDK_ROOT)
    if not status.get("ok"):
        reason = status.get("reason", "scope_base_unavailable")
        if reason == "scope_base_unavailable":
            errors.append("scope_base_unavailable")
        for item in status.get("base_out_of_scope_changes", []):
            errors.append(item)
    return status


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_files(errors)
    check_sidecars(errors)
    pins_checked = check_pins(errors)
    readme_counts = check_readme(errors)
    check_sources_manifest(errors)
    check_contract(errors)
    check_report(errors)
    check_imports(errors)
    scope = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL " + error)
        return 1
    print(
        "PASS decision=DEFER status=proposal_only_incomplete qualification=not_qualified "
        "pins=%d readme=%s scope_base=%s" % (pins_checked, readme_counts, scope.get("base"))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
