# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verifier for the SDK-NASE package.

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
            (reference.BOUNDARY_PINS, reference.WORKTREE, "boundary")):
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                errors.append("%s_pin_missing:%s" % (label, relative))
                continue
            observed = reference.sha256_file(path)
            if observed != expected:
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
        match = PIN_LINE.match(line)
        if match is None:
            errors.append("sources_manifest_bad_line:" + line[:80])
            continue
        observed[match.group(2)] = match.group(1)
    expected = {"source:" + key for key in reference.SOURCE_PINS}
    expected |= {"sdk:" + key for key in reference.BOUNDARY_PINS}
    expected |= {reference.TASK_PREFIX + name
                 for name in reference.LOCAL_FILES
                 if name != "SOURCES.sha256"}
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
    if reference.BOARD_TASK_ROW in observed or \
            "source:" + reference.BOARD_TASK_ROW in observed:
        errors.append("sources_manifest_pins_mutable_board")


def _check_linked_row(errors: list[str], boundary: dict) -> None:
    if boundary.get("board_file_pinned") is not False:
        errors.append("board_file_must_not_be_pinned")
    try:
        projection = reference.board_row_projection()
        rows = reference.linked_rows()
    except (OSError, ValueError) as error:
        errors.append("board_projection_failed:" + str(error))
        return
    if projection.get("id") != reference.TASK:
        errors.append("board_task_id_mismatch")
    if projection.get("component") != reference.COMPONENT_ID:
        errors.append("board_component_mismatch")
    if tuple(row["id"] for row in rows) != reference.LINKED_ROW_IDS:
        errors.append("board_linked_rows_mismatch")
    if projection != boundary.get("board_row_projection"):
        errors.append("board_projection_mismatch")
    if reference.board_row_digest(projection) != \
            boundary.get("board_row_sha256"):
        errors.append("board_row_digest_mismatch")
    if list(rows) != boundary.get("linked_rows"):
        errors.append("linked_rows_mismatch")
    if reference.linked_rows_digest(rows) != boundary.get("linked_rows_sha256"):
        errors.append("linked_rows_digest_mismatch")
    for field in ("status", "owner", "claim", "review", "handoff",
                  "dispatch_priority", "blocked_reason"):
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
    expected = reference.build_contract()
    if document != expected:
        errors.append("contract_differs_from_reference")
    if document.get("decision") != "DEFER":
        errors.append("contract_decision_not_defer")
    if document.get("status") != "proposal_only_incomplete":
        errors.append("contract_status_not_incomplete")
    if document.get("qualification_status") != "not_qualified":
        errors.append("contract_qualification_not_not_qualified")
    if document.get("incomplete") is not True or \
            document.get("proposal_only") is not True:
        errors.append("contract_incomplete_or_proposal_flag")
    gates = document.get("release_gates") or []
    if len(gates) != 8:
        errors.append("contract_release_gate_count:" + str(len(gates)))
    for gate in gates:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            errors.append("contract_gate_not_blocked:" + str(gate.get("id")))
    _check_linked_row(errors, document)
    if document.get("boundary", {}).get("provider_registration") is not False:
        errors.append("contract_provider_registration")
    if document.get("scope", {}).get("weights_vendored") is not False:
        errors.append("contract_weights_vendored")
    try:
        reference.assert_no_float(document)
    except TypeError as error:
        errors.append("contract_contains_float:" + str(error))
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
    expected = reference.canonical_bytes(reference.build_report())
    if payload != expected:
        errors.append("report_differs_from_reference")
    digest = hashlib.sha256(payload).hexdigest()
    if SIDECAR.read_text(encoding="ascii") != "%s  report.json\n" % digest:
        errors.append("report_sidecar_mismatch")
    if document.get("decision") != "DEFER":
        errors.append("report_decision_not_defer")
    if document.get("status") != "proposal_only_incomplete":
        errors.append("report_status_not_incomplete")
    if document.get("evidence_status") != "incomplete":
        errors.append("report_evidence_status")
    if document.get("qualification_status") != "not_qualified":
        errors.append("report_qualification_status")
    if document.get("incomplete") is not True or \
            document.get("proposal_only") is not True:
        errors.append("report_incomplete_or_proposal_flag")
    qualification = document.get("qualification") or {}
    if qualification.get("status") != "not_qualified":
        errors.append("report_qualification_block_status")
    if qualification.get("real_result_present") is not False or \
            qualification.get("release_claim") is not False:
        errors.append("report_result_or_release_claim")
    gates = document.get("gates") or []
    if len(gates) != 8:
        errors.append("report_release_gate_count:" + str(len(gates)))
    for gate in gates:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            errors.append("report_gate_not_blocked:" + str(gate.get("id")))
    blockers = document.get("exact_blockers") or []
    if len(blockers) != 6:
        errors.append("report_blocker_count:" + str(len(blockers)))
    for blocker in blockers:
        if blocker.get("status") != "open" or \
                blocker.get("qualifies") is not False:
            errors.append("report_blocker_not_open:" + str(blocker.get("id")))
    artifacts = document.get("required_artifacts") or []
    if len(artifacts) != 7:
        errors.append("report_artifact_count:" + str(len(artifacts)))
    for artifact in artifacts:
        if artifact.get("present") is not False or \
                artifact.get("verified") is not False or \
                artifact.get("blocked") is not True:
            errors.append("report_artifact_promoted:" + str(artifact.get("id")))
    profile = document.get("enhancement_profile") or {}
    summary = profile.get("row_summary") or {}
    if summary.get("requirement_count") != 8:
        errors.append("report_profile_row_count")
    if summary.get("blocked_count") != 7 or \
            summary.get("documented_count") != 1:
        errors.append("report_profile_row_state")
    if summary.get("profile_satisfied") is not False or \
            summary.get("real_result_count") != 0:
        errors.append("report_profile_promoted")
    absence = document.get("absence_evidence") or {}
    live = reference.absence_summary()
    if absence.get("probes") != live["probes"]:
        errors.append("report_absence_probes_stale")
    if absence.get("all_absent") is not True or live["all_absent"] is not True:
        errors.append("report_absence_present_artifact")
    identity = document.get("recorded_identity") or {}
    for field in ("checkpoint_path", "checkpoint_sha256", "checkpoint_bytes",
                  "checkpoint_variant", "model_revision",
                  "beats_checkpoint_sha256"):
        if identity.get(field) is not None:
            errors.append("report_recorded_identity_invented:" + field)
    if identity.get("qualifies") is not False:
        errors.append("report_recorded_identity_qualifies")
    registry = document.get("asset_registry") or {}
    if registry.get("nase_entry_present") is not False:
        errors.append("report_asset_registry_nase_present")
    declaration = document.get("asset_declaration") or {}
    if declaration.get("accepted_control_qualifies") is not False:
        errors.append("report_control_qualifies")
    if declaration.get("runtime_or_weights_invoked") is not False:
        errors.append("report_declaration_invoked_runtime")
    if declaration.get("rejection_cases", 0) < 30:
        errors.append("report_declaration_rejection_count")
    if declaration.get("strict_json_cases", 0) < 10:
        errors.append("report_strict_json_case_count")
    _check_linked_row(errors, document)
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
        if path.is_file() and path.suffix.lower() in reference.FORBIDDEN_SUFFIXES:
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
    with tempfile.TemporaryDirectory(prefix="nase-verify-") as root:
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
        "PASS verify.py version=%s pins=%d contract_sha256=%s "
        "report_sha256=%s gates=%d blockers=%d artifacts=%d "
        "declaration_cases=%d strict_json_cases=%d absence_probes=%d "
        "snippets=%d readme_rows=%s cold_starts=%d/3"
        % (
            platform.python_version(),
            pins,
            reference.object_digest(contract),
            hashlib.sha256(REPORT.read_bytes()).hexdigest(),
            len(report.get("gates", [])),
            len(report.get("exact_blockers", [])),
            len(report.get("required_artifacts", [])),
            report.get("asset_declaration", {}).get("rejection_cases", 0),
            report.get("asset_declaration", {}).get("strict_json_cases", 0),
            len(report.get("absence_evidence", {}).get("probes", [])),
            report.get("evidence_presence", {}).get("snippet_count", 0),
            ",".join("%s=%d" % (key, value)
                     for key, value in sorted(readme.items())),
            len(repeats),
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
