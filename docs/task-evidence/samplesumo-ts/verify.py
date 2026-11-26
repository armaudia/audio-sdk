# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-SAMPLESUMO-TS evidence package.

The task-local scope gate diffs this branch against the newest merge-base with
``origin/main`` (falling back to ``main``). An unresolved base emits
``scope_base_unavailable``; a committed path outside this task directory emits
``base_out_of_scope_change``. Later sibling merges on the base branch are not
attributed to this branch.
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

SDK_ROOT = reference.WORKTREE
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_LICENSE = "SPDX-" "License-Identifier: Apache-2.0"
SPDX_TAG = "SPDX-" "License-Identifier:"
SIDECAR_TEXT = SPDX_COPYRIGHT + "\n" + SPDX_LICENSE + "\n"
SIDECARS = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
EXPECTED_FILES = frozenset(reference.EXPECTED_DIR_FILES)
ALLOWED_IMPORTS = frozenset((
    "__future__", "ast", "copy", "hashlib", "json", "os", "pathlib",
    "platform", "re", "reference", "shutil", "subprocess", "sys",
    "tempfile", "typing", "unittest", "verify",
))
FORBIDDEN_IMPORTS = frozenset((
    "aiohttp", "http", "librosa", "numpy", "onnxruntime", "requests",
    "scipy", "socket", "soundfile", "ssl", "torch", "torchaudio",
    "urllib", "urllib3", "websocket",
))
PIN_LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")
SCOPE_REGRESSION_TESTS = (
    "test_scope_base_newest_merge_base_and_out_of_scope_change",
    "test_scope_base_falls_back_to_main",
    "test_scope_base_unavailable_fails_closed",
)


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append("interpreter_mismatch:" + observed)


def check_files(errors: list[str]) -> None:
    observed = {path.name for path in HERE.iterdir()
                if path.is_file() and not path.name.startswith(".")}
    for name in sorted(observed - EXPECTED_FILES):
        errors.append("unexpected_file:" + name)
    for name in sorted(EXPECTED_FILES - observed):
        errors.append("missing_file:" + name)
    if [path.name for path in HERE.iterdir() if path.is_dir()]:
        errors.append("unexpected_subdirectory")


def check_pins(errors: list[str]) -> None:
    for relative, expected in sorted(reference.SOURCE_PINS.items()):
        path = reference.AUDIO_ROOT / relative
        if not path.is_file() or reference.sha256_file(path) != expected:
            errors.append("source_pin:" + relative)
    for relative, expected in sorted(reference.BOUNDARY_PINS.items()):
        path = SDK_ROOT / relative
        if not path.is_file() or reference.sha256_file(path) != expected:
            errors.append("boundary_pin:" + relative)


def check_sources_manifest(errors: list[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256_missing")
        return 0
    rows: dict[str, str] = {}
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        match = PIN_LINE.match(line)
        if not match:
            errors.append("SOURCES_malformed_line")
            continue
        digest, name = match.groups()
        if name in rows:
            errors.append("SOURCES_duplicate_row:" + name)
        rows[name] = digest
    expected: dict[str, str] = {}
    for relative in reference.SOURCE_PINS:
        expected["source:" + relative] = reference.sha256_file(
            reference.AUDIO_ROOT / relative)
    for relative in reference.BOUNDARY_PINS:
        expected["sdk:" + relative] = reference.sha256_file(
            SDK_ROOT / relative)
    for name in EXPECTED_FILES - {"SOURCES.sha256"}:
        expected[reference.TASK_PREFIX + name] = reference.sha256_file(
            HERE / name)
    for name in sorted(set(expected) - set(rows)):
        errors.append("SOURCES_missing_row:" + name)
    for name in sorted(set(rows) - set(expected)):
        errors.append("SOURCES_extra_row:" + name)
    for name, digest in sorted(rows.items()):
        if name not in expected:
            continue
        if name.startswith("source:"):
            path = reference.AUDIO_ROOT / name[len("source:"):]
        elif name.startswith("sdk:"):
            path = SDK_ROOT / name[len("sdk:"):]
        elif name.startswith(reference.TASK_PREFIX):
            path = SDK_ROOT / name
        else:
            path = SDK_ROOT / name
        if not path.is_file() or reference.sha256_file(path) != digest:
            errors.append("SOURCES_digest:" + name)
    if any("plan/swarm/TASKS.json" in name for name in rows):
        errors.append("mutable_board_file_pinned")
    return len(rows)


def _check_linked_row(errors: list[str], boundary: dict) -> None:
    projection = reference.board_row_projection()
    rows = reference.linked_rows()
    if boundary.get("linked_row") != projection:
        errors.append("linked_row_mismatch")
    if boundary.get("linked_row_sha256") != reference.board_row_digest(projection):
        errors.append("linked_row_digest_mismatch")
    if boundary.get("linked_rows") != rows:
        errors.append("linked_rows_mismatch")
    if boundary.get("linked_rows_sha256") != reference.linked_rows_digest(rows):
        errors.append("linked_rows_digest_mismatch")
    if boundary.get("board_file_pinned") is not False:
        errors.append("board_file_pinned")
    if boundary.get("linked_row_identity_only") is not True:
        errors.append("linked_row_identity_only")
    if boundary.get("mutable_board_fields_gate") is not False:
        errors.append("mutable_board_fields_gate")


def check_contract(errors: list[str]) -> dict:
    if not CONTRACT.is_file():
        errors.append("contract_missing")
        return {}
    try:
        document = reference.read_strict_json(CONTRACT)
    except (ValueError, UnicodeDecodeError) as error:
        errors.append("contract_json_invalid:" + str(error))
        return {}
    expected = reference.build_contract()
    if document != expected:
        errors.append("contract_builder_mismatch")
    if CONTRACT.read_bytes() != reference.canonical_bytes(expected):
        errors.append("contract_not_canonical")
    if document.get("decision") != "DEFER" or document.get("status") != "incomplete":
        errors.append("contract_disposition")
    if document.get("qualification_status") != "not_qualified":
        errors.append("contract_qualification")
    if [row.get("id") for row in document.get("release_gates", [])] != [
            "RG-%02d" % index for index in range(1, 9)]:
        errors.append("contract_gate_ids")
    if all(row.get("status") == "blocked" for row in
           document.get("release_gates", [])) is False:
        errors.append("contract_gates_not_blocked")
    _check_linked_row(errors, document.get("boundary", {}))
    return document


def check_report(errors: list[str]) -> dict:
    if not REPORT.is_file():
        errors.append("report_missing")
        return {}
    try:
        document = reference.read_strict_json(REPORT)
    except (ValueError, UnicodeDecodeError) as error:
        errors.append("report_json_invalid:" + str(error))
        return {}
    expected = reference.build_report()
    payload, digest = reference.canonical_report(expected)
    if document != expected:
        errors.append("report_builder_mismatch")
    if REPORT.read_bytes() != payload.encode("ascii"):
        errors.append("report_not_canonical")
    if not SIDECAR.is_file() or SIDECAR.read_text(encoding="ascii") != (
            digest + "  report.json\n"):
        errors.append("report_sidecar_mismatch")
    for key, value in (
            ("task", reference.TASK), ("component", reference.COMPONENT_ID),
            ("title", reference.TASK_TITLE),
            ("base_commit", reference.BASE_COMMIT),
            ("branch", reference.BRANCH), ("mode", reference.MODE),
            ("profile", reference.PROFILE), ("decision", "DEFER"),
            ("status", "incomplete"), ("evidence_status", "incomplete"),
            ("qualification_status", "not_qualified"),
            ("proposal_only", True)):
        if document.get(key) != value:
            errors.append("report_field:" + key)
    if document.get("contract_sha256") != reference.object_digest(
            reference.build_contract()):
        errors.append("report_contract_digest")
    _check_linked_row(errors, document.get("boundary", {}))
    if [row.get("id") for row in document.get("release_gates", [])] != [
            "RG-%02d" % index for index in range(1, 9)]:
        errors.append("report_gate_ids")
    if any(row.get("status") != "blocked" or row.get("qualifies") is not False
           for row in document.get("release_gates", [])):
        errors.append("report_gate_not_blocked")
    if [row.get("id") for row in document.get("exact_blockers", [])] != [
            "BLK-%02d" % index for index in range(1, 7)]:
        errors.append("report_blocker_ids")
    if any(row.get("status") != "open" or row.get("qualifies") is not False
           for row in document.get("exact_blockers", [])):
        errors.append("report_blocker_not_open")
    artifacts = document.get("required_artifacts", [])
    if [row.get("id") for row in artifacts] != [
            "ART-%02d" % index for index in range(1, 8)]:
        errors.append("report_artifact_ids")
    if artifacts and (artifacts[0].get("present") is not True
                      or artifacts[0].get("verified") is not True):
        errors.append("report_ART01")
    if any(row.get("id") != "ART-01" and
           (row.get("present") is not False or row.get("verified") is not False
            or row.get("blocked") is not True) for row in artifacts):
        errors.append("report_artifact_not_blocked")
    profile = document.get("rate_profile", {})
    if profile.get("profile") != "rate" or profile.get("profile_satisfied") is not False:
        errors.append("report_rate_profile")
    if profile.get("real_results") != 0 or len(
            profile.get("requirement_rows", [])) != len(reference.RATE_REQUIREMENTS):
        errors.append("report_rate_rows")
    if any(row.get("qualifies") is not False
           for row in profile.get("requirement_rows", [])):
        errors.append("report_rate_row_qualifies")
    if document.get("absence_evidence", {}).get("summary", {}).get(
            "all_absent") is not True or document.get("absence_evidence", {}).get(
            "summary", {}).get("present_count") != 0:
        errors.append("report_absence")
    if document.get("snippet_evidence", {}).get("all_present") is not True:
        errors.append("report_snippets")
    if document.get("public_v0_geometry") != {
            "sample_rate_hz": 16000, "channels": 1, "frame_samples": 160,
            "sample_format": "float32", "unchanged": True}:
        errors.append("report_geometry_changed")
    envelope = document.get("protocol_envelope", {})
    if envelope.get("case_count") != 5 or envelope.get("synthesizes_audio") is not False:
        errors.append("report_envelope")
    if any(case.get("duration_error_samples") != 0
           or case.get("monotone") is not True or case.get("bounded") is not True
           for case in envelope.get("cases", [])):
        errors.append("report_envelope_case")
    admission = document.get("admission", {})
    recomputed = reference.admission_rejections()
    if admission.get("cases") != recomputed["cases"] or admission.get(
            "rejections") != recomputed["rejections"]:
        errors.append("report_admission")
    if admission.get("all_rejected") is not True or admission.get(
            "assets_never_loaded") is not True or admission.get(
            "control_qualifies") is not False:
        errors.append("report_admission_flags")
    if document.get("strict_json", {}).get("all_rejected") is not True:
        errors.append("report_strict_json")
    scope = document.get("scope", {})
    if scope.get("task_local_only") is not True or scope.get(
            "write_scope") != reference.WRITE_SCOPE:
        errors.append("report_scope")
    for key, value in scope.items():
        if key in ("task_local_only", "write_scope"):
            continue
        if value is not False:
            errors.append("report_scope_claim:" + key)
    qualification = document.get("qualification", {})
    if qualification.get("not_qualified") is not True or qualification.get(
            "all_release_gates_blocked") is not True:
        errors.append("report_qualification")
    for key, value in qualification.items():
        if key in ("status", "readiness", "not_qualified",
                   "all_release_gates_blocked"):
            continue
        if value is not False:
            errors.append("report_qualification_claim:" + key)
    try:
        reference.assert_no_float(document)
    except TypeError as error:
        errors.append("report_float:" + str(error))
    return document


def check_readme(errors: list[str]) -> int:
    if not README.is_file():
        errors.append("README_missing")
        return 0
    try:
        text = README.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        errors.append("README_not_ascii")
        return 0
    problems = reference.readme_table_errors(text)
    errors.extend(problems)
    return sum(len(reference.readme_table_rows(text, section))
               for section in reference.README_MARKERS
               if not any("readme_" + section in item for item in problems))


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
            if name in FORBIDDEN_IMPORTS:
                errors.append("forbidden_import:" + path.name + ":" + name)
            if name and name not in ALLOWED_IMPORTS:
                errors.append("unexpected_import:" + path.name + ":" + name)


def check_licensing(errors: list[str]) -> None:
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file() or path.read_text(encoding="utf-8") != SIDECAR_TEXT:
            errors.append("license_sidecar:" + name)
    for name in ("README.md", "LICENSES.md"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("spdx_header:" + name)
    for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        head = "\n".join(text.splitlines()[:5])
        if SPDX_COPYRIGHT not in head or SPDX_LICENSE not in head:
            errors.append("spdx_header:" + name)
        for number, line in enumerate(text.splitlines(), start=1):
            if number > 2 and SPDX_TAG in line:
                errors.append("spdx_literal:" + name + ":" + str(number))
        _check_imports(errors, HERE / name)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in {
                ".bin", ".ckpt", ".npy", ".onnx", ".pt", ".pth",
                ".safetensors", ".wav", ".mp3", ".flac", ".ogg", ".zip",
                ".tar", ".gz"}:
            errors.append("forbidden_payload:" + path.name)
    for name in EXPECTED_FILES:
        path = HERE / name
        if not path.is_file():
            continue
        try:
            text = path.read_bytes().decode("ascii")
        except UnicodeDecodeError:
            errors.append("non_ascii:" + name)
            continue
        if name not in ("contract.json", "report.json") and not text.endswith("\n"):
            errors.append("no_final_newline:" + name)
        for number, line in enumerate(text.splitlines(), start=1):
            if line != line.rstrip(" \t"):
                errors.append("trailing_whitespace:%s:%d" % (name, number))
            if "\r" in line:
                errors.append("carriage_return:%s:%d" % (name, number))


def scope_error_codes(worktree: Path,
                      refs: tuple[str, ...] = reference.SCOPE_BASE_REFS,
                      prefix: str = reference.TASK_PREFIX) -> list[str]:
    """Exact fail-closed diagnostics for the newest-merge-base scope gate."""
    base = reference.scope_base(worktree, refs)
    if base is None:
        return ["scope_base_unavailable"]
    try:
        paths = reference.scope_changed_paths(worktree, base)
    except ValueError as error:
        return [str(error)]
    return ["base_out_of_scope_change:" + path
            for path in reference.scope_violations(paths, prefix)]


def check_scope(errors: list[str]) -> list[str]:
    status = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"], capture_output=True, text=True)
    if status.returncode != 0:
        errors.append("git_status_failed:" + status.stderr.strip())
    else:
        for line in status.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path and not path.startswith(reference.TASK_PREFIX):
                errors.append("out_of_scope_change:" + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        result = subprocess.run(["git", "-C", str(SDK_ROOT), *arguments],
                                capture_output=True, text=True)
        if result.returncode != 0 or result.stdout.strip():
            errors.append("git_diff_check_failed:" + result.stdout.strip())
    codes = scope_error_codes(SDK_ROOT)
    errors.extend(codes)
    return codes


def check_tests(errors: list[str]) -> int:
    text = (HERE / "test_reference.py").read_text(encoding="utf-8")
    names = [line.strip().split("def ", 1)[1].split("(", 1)[0]
             for line in text.splitlines() if line.startswith("    def test_")]
    for required in SCOPE_REGRESSION_TESTS:
        if required not in names:
            errors.append("missing_scope_regression_test:" + required)
    if len(names) < 24:
        errors.append("fewer_than_24_tests:" + str(len(names)))
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONHASHSEED="0")
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "-q", "test_reference.py"],
        cwd=HERE, capture_output=True, text=True, env=environment, timeout=300)
    if result.returncode != 0:
        errors.append("test_suite_failed:" +
                      (result.stderr.strip() or result.stdout.strip()))
    return len(names)


def _prepare_scratch(root: Path, index: int) -> Path:
    sdk = root / "audioml/worktrees/audio-sdk" / reference.TASK
    target = sdk / reference.TASK_PREFIX
    target.mkdir(parents=True, exist_ok=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for name in ("research", "audio-benchmark-platform", "cpp-library"):
        link = root / "audioml" / name
        link.parent.mkdir(parents=True, exist_ok=True)
        if not link.exists() and not link.is_symlink():
            link.symlink_to(reference.AUDIO_ROOT / name)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        if not link.exists() and not link.is_symlink():
            link.symlink_to(SDK_ROOT / relative)
    return target


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    committed = (
        (CONTRACT.read_bytes() if CONTRACT.is_file() else b""),
        (REPORT.read_bytes() if REPORT.is_file() else b""),
        (SIDECAR.read_bytes() if SIDECAR.is_file() else b""),
        (PINS.read_bytes() if PINS.is_file() else b""),
        (README.read_bytes() if README.is_file() else b""),
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(prefix="sdk-samplesumo-ts-cold-") as folder:
        root = Path(folder)
        environment["SOURCE_ROOT"] = str(root / "audioml")
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            result = subprocess.run(
                [sys.executable, "run.py", "all"], cwd=target,
                capture_output=True, text=True, env=environment, timeout=300)
            if result.returncode != 0:
                errors.append("cold_start_%d_failed:%s" % (
                    index, result.stderr.strip()))
                continue
            generated = (
                (target / "contract.json").read_bytes(),
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
                (target / "README.md").read_bytes(),
            )
            if generated != committed:
                errors.append("cold_start_%d_bytes_differ" % index)
            digests.append(hashlib.sha256(generated[1]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_files(errors)
    check_pins(errors)
    pins = check_sources_manifest(errors)
    contract = check_contract(errors)
    report = check_report(errors)
    readme_rows = check_readme(errors)
    check_licensing(errors)
    tests = check_tests(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print("FAIL pins=%d json_ok=%s readme_rows=%d tests=%d "
              "cold_starts=%d report_sha256=%s changed_files=%d failures=%d"
              % (pins, bool(report), readme_rows, tests, len(digests),
                 digest, len(changed), len(errors)))
        return 1
    print("PASS verify.py version=%s contract_sha256=%s report_sha256=%s "
          "gates=%d blockers=%d artifacts=%d rate_rows=%d admission_cases=%d "
          "strict_json_cases=%d absence_probes=%d readme_rows=%d tests=%d "
          "cold_starts=3/3 byte_identical=true profile=%s status=%s "
          "decision=%s changed_files=%d"
          % (platform.python_version(),
             reference.object_digest(contract), digest,
             len(report["release_gates"]), len(report["exact_blockers"]),
             len(report["required_artifacts"]),
             len(report["rate_profile"]["requirement_rows"]),
             report["admission"]["cases"],
             report["strict_json"]["cases"],
             report["absence_evidence"]["summary"]["probe_count"],
             readme_rows, tests, reference.PROFILE, reference.STATUS,
             reference.DECISION, len(changed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
