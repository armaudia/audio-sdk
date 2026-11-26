# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-PYANNOTE-DIARIZATION evidence package."""

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

SDK_ROOT = reference.WORKTREE
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"

SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECAR_TEXT = SPDX_COPYRIGHT + "\n" + SPDX_LICENSE + "\n"

SIDECARS = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)

EXPECTED_FILES = frozenset((
    "LICENSES.md",
    "README.md",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
))

ALLOWED_IMPORTS = frozenset((
    "__future__", "ast", "copy", "fractions", "hashlib", "json", "math",
    "os", "pathlib", "platform", "re", "reference", "shutil", "subprocess",
    "sys", "tempfile", "typing", "unittest",
))

FORBIDDEN_MODULES = frozenset((
    "aiohttp", "http", "huggingface_hub", "librosa", "numpy", "onnxruntime",
    "pyannote", "requests", "scipy", "socket", "soundfile", "ssl", "torch",
    "torchaudio", "urllib", "urllib3", "websocket",
))

PIN_LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")


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
    extra = sorted(observed - EXPECTED_FILES)
    missing = sorted(EXPECTED_FILES - observed)
    if extra:
        errors.append("unexpected files: " + ",".join(extra))
    if missing:
        errors.append("missing files: " + ",".join(missing))


def check_pins(errors: list[str]) -> None:
    for relative, expected in sorted(reference.SOURCE_PINS.items()):
        path = reference.AUDIO_ROOT / relative
        if not path.is_file():
            errors.append("source pin missing: " + relative)
            continue
        if reference.sha256_file(path) != expected:
            errors.append("source pin mismatch: " + relative)
    for relative, expected in sorted(reference.BOUNDARY_PINS.items()):
        path = SDK_ROOT / relative
        if not path.is_file():
            errors.append("boundary pin missing: " + relative)
            continue
        if reference.sha256_file(path) != expected:
            errors.append("boundary pin mismatch: " + relative)


def check_sources_manifest(errors: list[str]) -> None:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return
    rows: dict[str, str] = {}
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        match = PIN_LINE.match(line)
        if not match:
            errors.append("malformed SOURCES line: " + line[:60])
            continue
        digest, name = match.groups()
        if name in rows:
            errors.append("duplicate SOURCES row: " + name)
            continue
        rows[name] = digest
    expected: dict[str, str] = {}
    for relative in reference.SOURCE_PINS:
        expected["source:" + relative] = reference.sha256_file(reference.AUDIO_ROOT / relative)
    for relative in reference.BOUNDARY_PINS:
        expected[relative] = reference.sha256_file(SDK_ROOT / relative)
    for name in EXPECTED_FILES - {"SOURCES.sha256"}:
        expected[reference.TASK_PREFIX + name] = reference.sha256_file(HERE / name)
    if set(rows) != set(expected):
        missing = sorted(set(expected) - set(rows))
        extra = sorted(set(rows) - set(expected))
        if missing:
            errors.append("SOURCES missing rows: " + ",".join(missing[:5]))
        if extra:
            errors.append("SOURCES extra rows: " + ",".join(extra[:5]))
    for name, digest in sorted(rows.items()):
        if name.startswith("source:"):
            path = reference.AUDIO_ROOT / name[len("source:"):]
        elif name.startswith(reference.TASK_PREFIX):
            path = SDK_ROOT / name
        else:
            path = SDK_ROOT / name
        if not path.is_file():
            errors.append("SOURCES path missing: " + name)
        elif reference.sha256_file(path) != digest:
            errors.append("SOURCES digest mismatch: " + name)
    if "audio-benchmark-platform/plan/swarm/TASKS.json" in rows:
        errors.append("mutable board file must not be pinned")


def _check_linked_row(errors: list[str], boundary: dict) -> None:
    projection = reference.board_row_projection(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
    rows = reference.linked_rows()
    if boundary.get("linked_row") != projection:
        errors.append("linked row projection mismatch")
    if boundary.get("linked_row_sha256") != reference.board_row_digest(projection):
        errors.append("linked row digest mismatch")
    if boundary.get("linked_rows") != rows:
        errors.append("linked rows projection mismatch")
    if boundary.get("linked_rows_sha256") != reference.linked_rows_digest(rows):
        errors.append("linked rows digest mismatch")
    if boundary.get("board_file_pinned") is not False:
        errors.append("board file must not be pinned")
    if boundary.get("linked_row_identity_only") is not True:
        errors.append("linked row identity flag must be true")
    if boundary.get("mutable_board_fields_gate") is not False:
        errors.append("mutable board fields must not gate")


def check_contract(errors: list[str]) -> dict:
    if not CONTRACT.is_file():
        errors.append("contract.json missing")
        return {}
    try:
        document = reference.read_strict_json(CONTRACT)
    except Exception as error:  # noqa: BLE001
        errors.append("contract JSON invalid: " + str(error))
        return {}
    expected = reference.build_contract()
    if document != expected:
        errors.append("contract.json does not match builder")
    if CONTRACT.read_bytes() != reference.canonical_bytes(expected):
        errors.append("contract.json is not canonical")
    if document.get("decision") != "DEFER":
        errors.append("contract decision must be DEFER")
    if document.get("status") != "incomplete":
        errors.append("contract status must be incomplete")
    if document.get("qualification_status") != "not_qualified":
        errors.append("contract qualification must be not_qualified")
    if document.get("proposal_only") is not True:
        errors.append("contract proposal_only must be true")
    gates = document.get("release_gates", [])
    if [gate.get("id") for gate in gates] != ["RG-%02d" % index for index in range(1, 9)]:
        errors.append("contract must have exactly RG-01..RG-08")
    for gate in gates:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            errors.append("contract gate not blocked: " + str(gate.get("id")))
    _check_linked_row(errors, document.get("boundary", {}))
    return document


def check_report(errors: list[str]) -> dict:
    if not REPORT.is_file():
        errors.append("report.json missing")
        return {}
    try:
        document = reference.read_strict_json(REPORT)
    except Exception as error:  # noqa: BLE001
        errors.append("report JSON invalid: " + str(error))
        return {}
    expected = reference.build_report()
    if document != expected:
        errors.append("report.json does not match builder")
    text, digest = reference.canonical_report(expected)
    if REPORT.read_bytes() != text.encode("ascii"):
        errors.append("report.json is not canonical")
    if not SIDECAR.is_file():
        errors.append("report.json.sha256 missing")
    else:
        if SIDECAR.read_text(encoding="ascii") != f"{digest}  report.json\n":
            errors.append("report sidecar mismatch")
    if document.get("decision") != "DEFER":
        errors.append("report decision must be DEFER")
    if document.get("status") != "incomplete":
        errors.append("report status must be incomplete")
    if document.get("qualification_status") != "not_qualified":
        errors.append("report qualification must be not_qualified")
    qual = document.get("qualification", {})
    if qual.get("status") != "not_qualified" or qual.get("not_qualified") is not True:
        errors.append("qualification block invalid")
    if qual.get("all_release_gates_blocked") is not True:
        errors.append("all_release_gates_blocked must be true")
    gates = document.get("gates", [])
    if [gate.get("id") for gate in gates] != ["RG-%02d" % index for index in range(1, 9)]:
        errors.append("report must have exactly RG-01..RG-08")
    for gate in gates:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            errors.append("report gate not blocked: " + str(gate.get("id")))
    _check_linked_row(errors, document.get("boundary", {}))
    admission = document.get("admission", {})
    if admission.get("all_rejected") is not True or admission.get("strict_json_all_rejected") is not True:
        errors.append("admission suites must be all rejected")
    if admission.get("assets_never_loaded") is not True:
        errors.append("assets_never_loaded must be true")
    return document


def check_licensing(errors: list[str]) -> None:
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("missing sidecar: " + name)
            continue
        if path.read_text(encoding="ascii") != SIDECAR_TEXT:
            errors.append("bad sidecar text: " + name)
    for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing SPDX markers: " + name)
    try:
        tree = ast.parse((HERE / "reference.py").read_text(encoding="utf-8"))
    except SyntaxError as error:
        errors.append("reference.py syntax error: " + str(error))
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root not in ALLOWED_IMPORTS:
                    errors.append("disallowed import: " + alias.name)
                if root in FORBIDDEN_MODULES:
                    errors.append("forbidden module: " + alias.name)
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if root and root not in ALLOWED_IMPORTS:
                errors.append("disallowed import from: " + str(node.module))
            if root in FORBIDDEN_MODULES:
                errors.append("forbidden module: " + str(node.module))


def _branch_base() -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "merge-base", "HEAD", "origin/main"],
            check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return reference.BASE_COMMIT
    base = result.stdout.strip()
    return base or reference.BASE_COMMIT


def check_scope(errors: list[str]) -> None:
    try:
        status = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "status", "--porcelain", "--untracked-files=all"],
            check=True, capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        errors.append("git status failed: " + str(error))
        return
    for line in status.splitlines():
        if not line.strip():
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    base = _branch_base()
    try:
        diff = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "diff", "--name-only", base, "--"],
            check=True, capture_output=True, text=True).stdout
        staged = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "diff", "--cached", "--name-only", base, "--"],
            check=True, capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        errors.append("git diff failed: " + str(error))
        return
    for line in (diff + staged).splitlines():
        if line and not line.startswith(reference.TASK_PREFIX):
            errors.append("committed change outside task scope: " + line)
    for command in (["git", "-C", str(SDK_ROOT), "diff", "--check"],
                    ["git", "-C", str(SDK_ROOT), "diff", "--cached", "--check"]):
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            errors.append("git diff --check failed: " + result.stdout.strip())


def check_cold_start_regeneration(errors: list[str]) -> None:
    if not REPORT.is_file() or not CONTRACT.is_file():
        errors.append("cannot cold-start without committed artifacts")
        return
    with tempfile.TemporaryDirectory(prefix="pyannote-diar-verify-") as temporary:
        root = Path(temporary)
        shutil.copy2(HERE / "reference.py", root / "reference.py")
        shutil.copy2(HERE / "run.py", root / "run.py")
        environment = dict(os.environ)
        environment["AUDIOML_ROOT"] = str(reference.AUDIO_ROOT)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        digests: list[tuple[str, str]] = []
        for _ in range(3):
            result = subprocess.run(
                [sys.executable, str(root / "run.py"), "report.json"],
                cwd=str(root), env=environment, capture_output=True, text=True)
            if result.returncode != 0:
                errors.append("cold-start run failed: " + (result.stderr.strip() or result.stdout.strip()))
                return
            digests.append((
                hashlib.sha256((root / "report.json").read_bytes()).hexdigest(),
                hashlib.sha256((root / "contract.json").read_bytes()).hexdigest(),
            ))
        if len(set(digests)) != 1:
            errors.append("cold-start regeneration is not byte-identical")
            return
        if (root / "report.json").read_bytes() != REPORT.read_bytes():
            errors.append("cold-start report differs from committed report")
        if (root / "contract.json").read_bytes() != CONTRACT.read_bytes():
            errors.append("cold-start contract differs from committed contract")
        expected_sidecar = (root / "report.json.sha256").read_text(encoding="ascii")
        if expected_sidecar != SIDECAR.read_text(encoding="ascii"):
            errors.append("cold-start sidecar differs from committed sidecar")


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_files(errors)
    check_pins(errors)
    contract = check_contract(errors)
    report = check_report(errors)
    check_sources_manifest(errors)
    check_licensing(errors)
    check_scope(errors)
    check_cold_start_regeneration(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error, file=sys.stderr)
        print("FAIL verification (%d errors)" % len(errors), file=sys.stderr)
        return 1
    print(
        "PASS verify.py version=%s contract_sha256=%s report_sha256=%s "
        "gates=%d blockers=%d artifacts=%d admission_cases=%d strict_json_cases=%d envelope_cases=%d absence_probes=%d"
        % (
            platform.python_version(),
            reference.object_digest(contract),
            hashlib.sha256(REPORT.read_bytes()).hexdigest(),
            len(report.get("gates", [])),
            len(report.get("exact_blockers", [])),
            len(report.get("required_artifacts", [])),
            report.get("admission", {}).get("manifest_cases", 0),
            report.get("admission", {}).get("strict_json_cases", 0),
            report.get("protocol_envelope", {}).get("case_count", 0),
            len(report.get("absence_evidence", {}).get("probes", [])),
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
