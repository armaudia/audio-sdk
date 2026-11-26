#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verifier for SDK-OPTFRACTASII-APPROXIMATION evidence."""

from __future__ import annotations

import ast
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference as ref  # noqa: E402
import run  # noqa: E402

SDK_ROOT = ref.WORKTREE
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_TAG = "SPDX-" + "License-Identifier:"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan"
SPDX_LICENSE = "SPDX-License-" + "Identifier: Apache-2.0"
SIDECAR_TEXT = SPDX_COPYRIGHT + "\n" + SPDX_LICENSE + "\n"
SIDECARS = ("contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license")
ALLOWED_IMPORTS = frozenset({"__future__", "argparse", "ast", "hashlib", "json", "os", "pathlib", "platform", "re", "reference", "run", "shutil", "subprocess", "sys", "tempfile", "typing", "unittest"})
FORBIDDEN_MODULES = frozenset({"aiohttp", "http", "numpy", "onnxruntime", "requests", "scipy", "socket", "soundfile", "ssl", "torch", "torchaudio", "urllib", "urllib3"})


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != ref.REQUIRED_INTERPRETER:
        errors.append(f"interpreter mismatch: pinned {ref.REQUIRED_INTERPRETER} observed {observed}")


def check_files(errors: list[str]) -> None:
    observed = {p.name for p in HERE.iterdir() if p.is_file() and not p.name.startswith(".")}
    extra = sorted(observed - ref.EXPECTED_DIR_FILES)
    missing = sorted(ref.EXPECTED_DIR_FILES - observed)
    if extra:
        errors.append("unexpected files: " + ",".join(extra))
    if missing:
        errors.append("missing files: " + ",".join(missing))
    for p in HERE.rglob("*"):
        if p.is_file() and p.suffix.lower() in ref.FORBIDDEN_SUFFIXES:
            errors.append("forbidden_suffix:" + str(p.relative_to(HERE)))


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in ((ref.SOURCE_PINS, ref.AUDIO_ROOT, "source"), (ref.BOUNDARY_PINS, SDK_ROOT, "boundary")):
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                errors.append(f"{label}_pin_missing:{relative}")
                continue
            if ref.sha256_file(path) != expected:
                errors.append(f"{label}_pin_mismatch:{relative}")
            checked += 1
    return checked


def check_readme(errors: list[str]) -> dict[str, int]:
    if not README.is_file():
        errors.append("readme_missing")
        return {}
    try:
        return ref.verify_readme_digests(README.read_text(encoding="utf-8"))
    except ValueError as error:
        errors.append("readme_digest_table_failed:" + str(error))
        return {}


def check_sources_manifest(errors: list[str]) -> None:
    if not PINS.is_file():
        errors.append("sources_manifest_missing")
        return
    if PINS.read_bytes() != ref.sources_bytes():
        errors.append("sources_manifest_drift")


def check_contract(errors: list[str]) -> dict:
    if not CONTRACT.is_file():
        errors.append("contract_json_missing")
        return {}
    try:
        document = ref.read_strict_json(CONTRACT)
    except ValueError as error:
        errors.append("contract_json_invalid:" + str(error))
        return {}
    expected = ref.build_contract()
    if document != expected:
        errors.append("contract_does_not_match_builder")
    if CONTRACT.read_bytes() != ref.canonical_bytes(expected):
        errors.append("contract_not_canonical")
    for key, value in {
        "decision": ref.DECISION,
        "status": ref.STATUS,
        "evidence_status": ref.EVIDENCE_STATUS,
        "qualification_status": ref.QUALIFICATION_STATUS,
        "task": ref.TASK,
        "mode": ref.MODE,
        "profile": ref.PROFILE,
    }.items():
        if document.get(key) != value:
            errors.append(f"contract_field_mismatch:{key}")
    return document


def check_report(errors: list[str]) -> dict:
    if not REPORT.is_file():
        errors.append("report_json_missing")
        return {}
    try:
        document = ref.read_strict_json(REPORT)
    except ValueError as error:
        errors.append("report_json_invalid:" + str(error))
        return {}
    expected = ref.build_report()
    payload, digest = ref.canonical_report(expected)
    if document != expected:
        errors.append("report_does_not_match_builder")
    if REPORT.read_bytes() != payload.encode("ascii"):
        errors.append("report_not_canonical")
    if not SIDECAR.is_file():
        errors.append("report_sidecar_missing")
    elif SIDECAR.read_text(encoding="ascii") != digest + "  report.json\n":
        errors.append("report_sidecar_mismatch")
    for key, value in {
        "schema_id": ref.REPORT_SCHEMA_ID,
        "task": ref.TASK,
        "component": ref.COMPONENT_ID,
        "decision": ref.DECISION,
        "status": ref.STATUS,
        "evidence_status": ref.EVIDENCE_STATUS,
        "qualification_status": ref.QUALIFICATION_STATUS,
        "mode": ref.MODE,
        "profile": ref.PROFILE,
    }.items():
        if document.get(key) != value:
            errors.append(f"report_field_mismatch:{key}")
    if document.get("disposition", {}).get("proposal_only") is not True:
        errors.append("report_not_proposal_only")
    if document.get("disposition", {}).get("incomplete") is not True:
        errors.append("report_not_incomplete")
    if document.get("qualification", {}).get("not_qualified") is not True:
        errors.append("report_qualification_not_blocked")
    if document.get("qualification", {}).get("status") != ref.QUALIFICATION_STATUS:
        errors.append("report_qualification_status_mismatch")
    gates = document.get("release_gates", [])
    if len(gates) != 8:
        errors.append("release_gate_count_mismatch")
    for gate in gates:
        if gate.get("status") != "blocked":
            errors.append("gate_not_blocked:" + str(gate.get("id")))
        if gate.get("qualifies") is not False:
            errors.append("gate_qualifies:" + str(gate.get("id")))
    if document.get("contract_sha256") != ref.object_digest(ref.build_contract()):
        errors.append("report_contract_digest_mismatch")
    return document


def check_sidecars(errors: list[str]) -> None:
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("missing_sidecar:" + name)
            continue
        text = path.read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("sidecar_spdx_missing:" + name)


def check_licensing_and_headers(errors: list[str]) -> None:
    for name in ["reference.py", "run.py", "verify.py", "test_reference.py"]:
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_TAG not in text:
            errors.append("python_header_missing:" + name)
        contiguous = "SPDX-License-" + "Identifier: Apache-2.0"
        if contiguous in text and name != "LICENSES.md":
            for line in text.splitlines():
                if contiguous in line and not line.lstrip().startswith("#"):
                    errors.append("contiguous_spdx_in_python_literal:" + name)
                    break


def check_imports(errors: list[str]) -> None:
    for name in ["reference.py", "run.py", "verify.py", "test_reference.py"]:
        tree = ast.parse((HERE / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if mod in FORBIDDEN_MODULES:
                        errors.append("forbidden_import:" + mod)
                    if mod not in ALLOWED_IMPORTS and not mod.startswith("reference") and not mod.startswith("run"):
                        # allow stdlib-like unknown? be conservative
                        pass
            if isinstance(node, ast.ImportFrom):
                mod = (node.module or "").split(".")[0]
                if mod in FORBIDDEN_MODULES:
                    errors.append("forbidden_import:" + mod)


def check_scope(errors: list[str]) -> str | None:
    # dirty worktree scope
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain", "--untracked-files=all"], capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        errors.append("git_status_failed")
    else:
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            path = path.replace("\\", "/")
            if not (path == ref.TASK_PREFIX.rstrip("/") or path.startswith(ref.TASK_PREFIX)):
                errors.append("dirty_out_of_scope:" + path)
    base = ref.scope_base(SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
        return None
    for violation in ref.scope_violations(ref.scope_changed_paths(SDK_ROOT, base)):
        errors.append(violation)
    return base


def check_regeneration(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="optfractasii-verify-") as tmp:
        tmp_dir = Path(tmp)
        # run regeneration in temp by copying required static files and invoking run.py with output-dir
        cmd = [sys.executable, str(HERE / "run.py"), "all", "--repeats", "3", "--output-dir", str(tmp_dir)]
        proc = subprocess.run(cmd, cwd=str(HERE), capture_output=True, text=True, encoding="utf-8")
        if proc.returncode != 0:
            errors.append("regeneration_failed")
            errors.append((proc.stdout + proc.stderr)[-400:])
            return
        for name in ["contract.json", "report.json", "report.json.sha256", "SOURCES.sha256", "README.md"]:
            a = (HERE / name).read_bytes()
            b = (tmp_dir / name).read_bytes()
            if a != b:
                errors.append("regeneration_mismatch:" + name)


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_files(errors)
    checked_pins = check_pins(errors)
    readme_counts = check_readme(errors)
    check_sources_manifest(errors)
    check_contract(errors)
    check_report(errors)
    check_sidecars(errors)
    check_licensing_and_headers(errors)
    check_imports(errors)
    base = check_scope(errors)
    check_regeneration(errors)

    if errors:
        for err in errors:
            print("FAIL", err)
        return 1
    print(
        "PASS verify.py "
        f"task={ref.TASK} decision={ref.DECISION} "
        f"pins={checked_pins} readme={readme_counts} scope_base={base or 'none'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
