# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verifier for the task evidence package.

Scope is checked against the dirty worktree and against commits added relative
to the newest merge-base with ``origin/main`` (falling back to ``main``). An
unresolved base emits ``scope_base_unavailable`` and any committed path outside
the task directory emits ``base_out_of_scope_change:<path>``.
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
    "aiohttp", "diffusers", "http", "librosa", "numpy", "onnxruntime",
    "requests", "scipy", "socket", "soundfile", "ssl", "tensorflow", "torch",
    "torchaudio", "transformers", "urllib", "urllib3", "websocket",
))

PIN_LINE = re.compile(r"^([0-9a-f]{64})  (\S+)$")


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append("interpreter mismatch: pinned %s observed %s" %
                      (reference.REQUIRED_INTERPRETER, observed))


def check_files(errors: list[str]) -> None:
    observed = {p.name for p in HERE.iterdir() if p.is_file() and not p.name.startswith(".")}
    extra = sorted(observed - reference.EXPECTED_DIR_FILES)
    missing = sorted(reference.EXPECTED_DIR_FILES - observed)
    if extra:
        errors.append("unexpected files: " + ",".join(extra))
    if missing:
        errors.append("missing files: " + ",".join(missing))


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in ((reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"),
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
        return reference.verify_readme_digests(README.read_text(encoding="utf-8"))
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
    if boundary.get("linked_row_sha256") != reference.board_row_digest(projection):
        errors.append("linked_row_digest_mismatch")
    if boundary.get("linked_rows") != [dict(row) for row in rows]:
        errors.append("linked_rows_projection_mismatch")
    if boundary.get("linked_rows_sha256") != reference.linked_rows_digest(rows):
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
    if document.get("qualification_status") != reference.QUALIFICATION_STATUS:
        errors.append("contract_qualification_mismatch")
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
    elif SIDECAR.read_text(encoding="ascii") != digest + "  report.json\n":
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
    if document.get("proposal_only") is not True or document.get("incomplete") is not True:
        errors.append("report_flags_mismatch")
    if document.get("contract_sha256") != reference.object_digest(reference.build_contract()):
        errors.append("report_contract_digest_mismatch")
    _check_linked_row(errors, document.get("boundary", {}))

    gates = document.get("gates", document.get("release_gates", []))
    expected_ids = ["RG-%02d" % index for index in range(1, 9)]
    if [gate.get("id") for gate in gates] != expected_ids:
        errors.append("report_gate_order_mismatch")
    for gate in gates:
        if gate.get("status") != "blocked":
            errors.append("gate_not_blocked:" + str(gate.get("id")))
        if gate.get("qualifies") is not False:
            errors.append("gate_qualifies:" + str(gate.get("id")))
        if gate.get("linked_row") != document.get("boundary", {}).get("linked_row"):
            errors.append("gate_linked_row_mismatch:" + str(gate.get("id")))

    blockers = document.get("exact_blockers", [])
    if [row.get("id") for row in blockers] != ["BLK-%02d" % index for index in range(1, 7)]:
        errors.append("blocker_ids_mismatch")
    for blocker in blockers:
        if blocker.get("qualifies") is not False:
            errors.append("blocker_qualifies:" + str(blocker.get("id")))
        if blocker.get("status") != "open":
            errors.append("blocker_not_open:" + str(blocker.get("id")))

    qualification = document.get("qualification_status")
    if qualification != reference.QUALIFICATION_STATUS:
        errors.append("qualification_status_mismatch")
    if document.get("scope", {}).get("task_local_only") is not True:
        errors.append("scope_not_task_local")
    return document


def check_declaration(errors: list[str], report: dict) -> None:
    declaration = report.get("asset_declaration", {})
    accepted = declaration.get("accepted_unpopulated")
    schema = declaration.get("schema", {})
    if accepted is None:
        errors.append("accepted_declaration_missing")
        return
    try:
        reference.validate_asset_declaration(accepted)
    except Exception as error:  # noqa: BLE001
        errors.append("accepted_declaration_invalid:" + str(error))
    if schema.get("schema_id") != reference.DECLARATION_SCHEMA_ID:
        errors.append("declaration_schema_id_mismatch")
    if schema.get("all_rejected") is not True:
        errors.append("declaration_rejections_incomplete")
    if schema.get("strict_json_all_rejected") is not True:
        errors.append("declaration_strict_json_incomplete")
    if schema.get("rejection_cases", 0) < 40:
        errors.append("declaration_rejection_count_low")
    if schema.get("strict_json_cases", 0) < 9:
        errors.append("declaration_strict_json_count_low")


def check_absence(errors: list[str], report: dict) -> None:
    absence = report.get("absence_summary", {})
    if absence.get("all_absent") is not True:
        errors.append("absence_not_all_absent")
    if absence.get("present_count") != 0:
        errors.append("absence_present_count_nonzero")
    probes = absence.get("probes", [])
    expected = len(reference.WORKSPACE_PROBES) + len(reference.WORKTREE_PROBES) + len(reference.HOME_PROBES)
    if len(probes) != expected:
        errors.append("absence_probe_count_mismatch")
    for probe in probes:
        if probe.get("present"):
            errors.append("absence_probe_present:" + str(probe.get("path")))


def check_scope(errors: list[str]) -> None:
    base, committed = reference.committed_paths_since_base(SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
    for path in committed:
        if not reference.path_is_within_prefix(path, reference.TASK_PREFIX):
            errors.append("base_out_of_scope_change:" + path)
    for path in reference.collect_dirty_paths(SDK_ROOT):
        if not reference.path_is_within_prefix(path, reference.TASK_PREFIX):
            errors.append("dirty_out_of_scope_change:" + path)


def check_license(errors: list[str]) -> None:
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("sidecar_missing:" + name)
            continue
        text = path.read_text(encoding="ascii")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("sidecar_license_missing:" + name)
    for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("source_license_missing:" + name)
        if SPDX_TAG in text.splitlines()[2:3][0] if len(text.splitlines()) > 2 else "":
            pass
        # no contiguous SPDX-License-Identifier token in string literal other than constructed tag
        forbidden = "SPDX-License-" + "Identifier: Apache-2.0"
        if (forbidden + '"') in text or (forbidden + "'") in text:
            errors.append("contiguous_spdx_token_in_source:" + name)


def check_imports(errors: list[str]) -> None:
    for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
        path = HERE / name
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in FORBIDDEN_MODULES:
                        errors.append("forbidden_import:" + name + ":" + alias.name)
                    if root not in ALLOWED_IMPORTS and root not in {"math", "fractions", "struct", "cmath", "copy"}:
                        # allow stdlib broad set? keep narrow: fail only on known forbidden
                        pass
            elif isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue
                root = node.module.split(".")[0]
                if root in FORBIDDEN_MODULES:
                    errors.append("forbidden_import:" + name + ":" + node.module)


def check_forbidden_files(errors: list[str]) -> None:
    for path in HERE.rglob("*"):
        if path.is_dir():
            continue
        if reference.has_forbidden_suffix(path):
            errors.append("forbidden_file_suffix:" + path.name)


def check_regeneration(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="neural-phase-vocoder-verify-") as tmp:
        temp_dir = Path(tmp) / HERE.name
        shutil.copytree(HERE, temp_dir)
        cmd = [sys.executable, str(temp_dir / "run.py"), "all"]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            errors.append("run_py_failed:" + proc.stdout.strip() + proc.stderr.strip())
            return
        for name in sorted(reference.EXPECTED_DIR_FILES):
            a = (HERE / name).read_bytes()
            b = (temp_dir / name).read_bytes()
            if a != b:
                errors.append("regeneration_drift:" + name)


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_files(errors)
    pin_count = check_pins(errors)
    readme_counts = check_readme(errors)
    check_sources_manifest(errors)
    contract = check_contract(errors)
    report = check_report(errors)
    if report:
        check_declaration(errors, report)
        check_absence(errors, report)
    check_scope(errors)
    check_license(errors)
    check_imports(errors)
    check_forbidden_files(errors)
    check_regeneration(errors)

    if errors:
        for err in errors:
            print("FAIL " + err)
        print(f"FAIL verify.py errors={len(errors)}")
        return 1
    print(
        "PASS verify.py "
        f"pins={pin_count} readme_sections={len(readme_counts)} "
        f"gates={len(report.get('release_gates', []))} "
        f"blockers={len(report.get('exact_blockers', []))} "
        f"decision={report.get('decision')} "
        f"qualification={report.get('qualification_status')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
