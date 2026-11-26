# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-DIFFATSM evidence package."""

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
    "aiohttp", "diffusers", "http", "librosa", "numpy", "onnxruntime",
    "requests", "scipy", "socket", "soundfile", "ssl", "torch",
    "torchaudio", "urllib", "urllib3", "websocket", "zlib",
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
        expected["source:" + relative] = reference.sha256_file(
            reference.AUDIO_ROOT / relative)
    for relative in reference.BOUNDARY_PINS:
        expected[relative] = reference.sha256_file(SDK_ROOT / relative)
    for name in EXPECTED_FILES - {"SOURCES.sha256"}:
        expected[reference.TASK_PREFIX + name] = reference.sha256_file(
            HERE / name)
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
    projection = reference.board_row_projection(
        reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
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
    if [gate.get("id") for gate in gates] != [
            "RG-%02d" % index for index in range(1, 9)]:
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
    payload, digest = reference.canonical_report(expected)
    if document != expected:
        errors.append("report.json does not match builder")
    if REPORT.read_bytes() != payload.encode("ascii"):
        errors.append("report.json is not canonical")
    if not SIDECAR.is_file():
        errors.append("report.json.sha256 missing")
    else:
        sidecar = SIDECAR.read_text(encoding="ascii")
        if sidecar != digest + "  report.json\n":
            errors.append("report.json.sha256 mismatch")

    if document.get("schema_id") != reference.REPORT_SCHEMA_ID:
        errors.append("report schema mismatch")
    expected_fields = {
        "task": reference.TASK,
        "component": reference.COMPONENT_ID,
        "title": reference.TASK_TITLE,
        "base_commit": reference.BASE_COMMIT,
        "branch": reference.BRANCH,
        "mode": reference.MODE,
        "profile": reference.PROFILE,
    }
    for key, value in expected_fields.items():
        if document.get(key) != value:
            errors.append("report field mismatch: " + key)
    if document.get("decision") != "DEFER":
        errors.append("report decision must be DEFER")
    if document.get("status") != "incomplete":
        errors.append("report status must be incomplete")
    if document.get("qualification_status") != "not_qualified":
        errors.append("report qualification must be not_qualified")
    if document.get("proposal_only") is not True:
        errors.append("report proposal_only must be true")
    if document.get("contract_sha256") != reference.object_digest(
            reference.build_contract()):
        errors.append("report contract digest mismatch")
    _check_linked_row(errors, document.get("boundary", {}))

    gates = document.get("gates", [])
    expected_ids = ["RG-%02d" % index for index in range(1, 9)]
    if [gate.get("id") for gate in gates] != expected_ids:
        errors.append("report must have exactly eight ordered gates")
    if len({gate.get("id") for gate in gates}) != len(gates):
        errors.append("duplicate release gate")
    for gate in gates:
        if gate.get("status") != "blocked":
            errors.append("gate not blocked: " + str(gate.get("id")))
        if gate.get("qualifies") is not False:
            errors.append("gate qualifies unexpectedly: " + str(gate.get("id")))
        if gate.get("linked_row") != document.get("boundary", {}).get(
                "linked_row"):
            errors.append("gate linked row mismatch: " + str(gate.get("id")))
    if len(gates) != 8:
        errors.append("report gate count is not eight")

    blockers = document.get("exact_blockers", [])
    if [row.get("id") for row in blockers] != [
            "BLK-%02d" % index for index in range(1, 7)]:
        errors.append("report must have BLK-01..BLK-06")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            errors.append("blocker not open: " + str(row.get("id")))

    artifacts = document.get("required_artifacts", [])
    if [row.get("id") for row in artifacts] != [
            "ART-%02d" % index for index in range(1, 8)]:
        errors.append("report must have ART-01..ART-07")
    for row in artifacts:
        if row.get("id") == "ART-01":
            if row.get("present") is not True or row.get("verified") is not True:
                errors.append("ART-01 must be present and verified")
        elif row.get("present") is not False or row.get("blocked") is not True:
            errors.append("artifact must remain blocked: " + str(row.get("id")))

    qualification = document.get("qualification", {})
    if qualification.get("not_qualified") is not True:
        errors.append("qualification.not_qualified must be true")
    if qualification.get("status") != "not_qualified":
        errors.append("qualification.status must be not_qualified")
    if qualification.get("all_release_gates_blocked") is not True:
        errors.append("all release gates must be blocked")
    for key, value in qualification.items():
        if key in ("status", "readiness", "not_qualified",
                   "all_release_gates_blocked"):
            continue
        if value is not False:
            errors.append("qualification claim must be false: " + key)

    profile = document.get("rate_profile", {})
    if profile.get("profile") != "rate":
        errors.append("rate profile label mismatch")
    if profile.get("profile_satisfied") is not False:
        errors.append("rate profile must not be satisfied")
    if profile.get("real_results") != 0:
        errors.append("rate profile real results must be zero")
    rows = profile.get("requirement_rows", [])
    if len(rows) != 13:
        errors.append("rate profile must have 13 requirement rows")
    for row in rows:
        if row.get("qualifies") is not False:
            errors.append("rate requirement qualifies: " + str(row.get("id")))
    if not any(row.get("status") == "blocked" for row in rows):
        errors.append("rate profile must record blocked rows")

    envelope = document.get("protocol_envelope", {})
    if envelope.get("case_count") != 5 or len(envelope.get("cases", [])) != 5:
        errors.append("envelope must have five cases")
    if envelope.get("identity_exact") is not True:
        errors.append("envelope identity must be exact")
    if envelope.get("synthesizes_audio") is not False:
        errors.append("envelope must not synthesize audio")
    if envelope.get("not_candidate") is not True:
        errors.append("envelope must be marked not_candidate")
    expected_cases = {
        "identity_1x": (19200, 19200),
        "speed_up_125": (19200, 15360),
        "speed_up_150": (19200, 12800),
        "speed_down_080": (19200, 24000),
        "speed_down_090": (19200, 21333),
    }
    for case in envelope.get("cases", []):
        case_id = case.get("id")
        if case_id not in expected_cases:
            errors.append("unknown envelope case: " + str(case_id))
            continue
        source, target = expected_cases[case_id]
        if case.get("input_samples") != source:
            errors.append("envelope input mismatch: " + case_id)
        if case.get("target_samples") != target:
            errors.append("envelope target mismatch: " + case_id)
        if case.get("duration_error_samples") != 0:
            errors.append("envelope duration error: " + case_id)
        if case.get("monotone") is not True or case.get("bounded") is not True:
            errors.append("envelope mapping invalid: " + case_id)
        if case.get("identity_exact") is not (case_id == "identity_1x"):
            errors.append("envelope identity flag mismatch: " + case_id)
        record = reference.mapping_record(
            source, case["numerator"], case["denominator"])
        if case.get("mapping_sha256") != record["mapping_sha256"]:
            errors.append("envelope mapping digest mismatch: " + case_id)

    admission = document.get("admission", {})
    recomputed = reference.admission_rejections()
    strict = reference.strict_json_rejections()
    if admission.get("manifest_cases") != recomputed["cases"]:
        errors.append("admission case count mismatch")
    if admission.get("manifest_cases", 0) < 40:
        errors.append("admission suite is too small")
    if admission.get("rejections") != recomputed["rejections"]:
        errors.append("admission rejection rows mismatch")
    if admission.get("all_rejected") is not True:
        errors.append("admission must reject every invalid manifest")
    if admission.get("strict_json_cases") != strict["cases"]:
        errors.append("strict JSON case count mismatch")
    if admission.get("strict_json_rejections") != strict["rejections"]:
        errors.append("strict JSON rejection rows mismatch")
    if admission.get("assets_never_loaded") is not True:
        errors.append("admission must declare assets never loaded")

    absence = document.get("absence_evidence", {})
    if absence.get("all_absent") is not True or absence.get("present_count") != 0:
        errors.append("absence probes must all be absent")
    if len(absence.get("probes", [])) != reference.absence_summary()["probe_count"]:
        errors.append("absence probe count mismatch")

    presence = document.get("evidence_presence", {})
    if presence.get("all_snippets_present") is not True:
        errors.append("source snippets missing")
    if presence.get("snippet_count") != 7:
        errors.append("source snippet count mismatch")

    scope = document.get("scope", {})
    if scope.get("task_local_only") is not True:
        errors.append("scope must be task-local")
    if scope.get("write_scope") != reference.WRITE_SCOPE:
        errors.append("write scope mismatch")
    for key, value in scope.items():
        if key in ("task_local_only", "write_scope"):
            continue
        if value is not False:
            errors.append("scope claim must be false: " + key)

    geometry = document.get("public_v0_geometry", {})
    if geometry != {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "sample_format": "float32",
            "unchanged": True,
    }:
        errors.append("public v0 geometry changed")

    for row in document.get("checkpoint_scope", []):
        if row.get("present") is not False:
            errors.append("checkpoint must be absent: " + str(row.get("id")))
    if document.get("runtime_readiness", {}).get("runtime_present") is not False:
        errors.append("runtime must remain absent")
    if document.get("source_reported_identity", {}).get(
            "runnable_as_released") is not False:
        errors.append("candidate must not be runnable")
    if document.get("source_reported_identity", {}).get(
            "rate_only_estimator") is not False:
        errors.append("candidate must not be a rate-only estimator")

    try:
        reference._assert_no_floats(document)
    except TypeError as error:
        errors.append("report contains a float: " + str(error))
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
                errors.append("forbidden import %s in %s" % (name, path.name))
            if name and name not in ALLOWED_IMPORTS:
                errors.append("unexpected import %s in %s" % (name, path.name))


def check_licensing(errors: list[str]) -> None:
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("license sidecar missing: " + name)
        elif path.read_text(encoding="utf-8") != SIDECAR_TEXT:
            errors.append("license sidecar text mismatch: " + name)
    for name in ("README.md", "LICENSES.md"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("missing SPDX header: " + name)
    for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        head = "\n".join(text.splitlines()[:5])
        if SPDX_COPYRIGHT not in head or SPDX_LICENSE not in head:
            errors.append("missing inline SPDX header: " + name)
        for number, line in enumerate(text.splitlines(), start=1):
            if number > 2 and SPDX_TAG in line:
                errors.append(
                    "inline SPDX expression must not appear in a literal: "
                    "%s:%d" % (name, number))
        _check_imports(errors, HERE / name)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in {
                ".bin", ".ckpt", ".npy", ".onnx", ".pt", ".pth", ".safetensors",
                ".wav", ".mp3", ".flac", ".ogg", ".zip", ".tar", ".gz"}:
            errors.append("forbidden payload file: " + path.name)
    for name in EXPECTED_FILES:
        path = HERE / name
        if not path.is_file():
            continue
        payload = path.read_bytes()
        try:
            text = payload.decode("ascii")
        except UnicodeDecodeError:
            errors.append("non-ASCII evidence file: " + name)
            continue
        if name not in ("contract.json", "report.json") and not text.endswith("\n"):
            errors.append("file must end with newline: " + name)
        for number, line in enumerate(text.splitlines(), start=1):
            if line != line.rstrip(" \t"):
                errors.append("trailing whitespace: %s:%d" % (name, number))
            if "\r" in line:
                errors.append("carriage return: %s:%d" % (name, number))


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
            ["git", "-C", str(SDK_ROOT), "status", "--porcelain",
             "--untracked-files=all"],
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
            ["git", "-C", str(SDK_ROOT), "diff", "--name-only",
             base, "--"],
            check=True, capture_output=True, text=True).stdout
        staged = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "diff", "--cached", "--name-only",
             base, "--"],
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
    with tempfile.TemporaryDirectory(prefix="diffatsm-verify-") as temporary:
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
                errors.append("cold-start run failed: " + result.stderr.strip())
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
        expected_sidecar = (root / "report.json.sha256").read_text(
            encoding="ascii")
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
        "gates=%d blockers=%d artifacts=%d admission_cases=%d "
        "strict_json_cases=%d envelope_cases=%d absence_probes=%d"
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
