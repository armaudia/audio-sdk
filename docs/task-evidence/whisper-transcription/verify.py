# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only fail-closed verifier for SDK-WHISPER-TRANSCRIPTION evidence."""

from __future__ import annotations

import ast
import hashlib
import os
import platform
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
ALLOWED_IMPORTS = frozenset((
    "__future__", "ast", "hashlib", "json", "os", "pathlib", "platform",
    "re", "reference", "run", "shutil", "subprocess", "sys", "tempfile",
    "typing", "unittest",
))
FORBIDDEN_MODULES = frozenset((
    "aiohttp", "http", "numpy", "requests", "socket", "soundfile", "ssl",
    "torch", "torchaudio", "transformers", "urllib", "urllib3", "websocket",
    "whisper",
))


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append(f"interpreter_mismatch:pinned={reference.REQUIRED_INTERPRETER}:observed={observed}")


def check_files(errors: list[str]) -> None:
    observed = {p.name for p in HERE.iterdir() if p.is_file() and not p.name.startswith(".")}
    for name in sorted(observed - reference.EXPECTED_DIR_FILES):
        errors.append("unexpected_file:" + name)
    for name in sorted(reference.EXPECTED_DIR_FILES - observed):
        errors.append("missing_file:" + name)
    if any(p.is_dir() for p in HERE.iterdir()):
        errors.append("unexpected_subdirectory")


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in ((reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"),
                              (reference.BOUNDARY_PINS, SDK_ROOT, "boundary")):
        for rel, expected in sorted(pins.items()):
            path = root / rel
            if not path.is_file():
                errors.append(label + "_pin_missing:" + rel)
                continue
            actual = reference.sha256_file(path)
            if actual != expected:
                errors.append(label + "_pin_mismatch:" + rel)
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
    expected = reference.sources_bytes()
    got = PINS.read_bytes()
    if got != expected:
        errors.append("sources_manifest_mismatch")
    for line in got.decode("ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        digest, name = line.split("  ", 1)
        if name.startswith("source:") or name.startswith("sdk:"):
            continue
        path = HERE / name.rsplit("/", 1)[-1]
        if not path.is_file():
            errors.append("sources_missing_file:" + name)
            continue
        if reference.sha256_file(path) != digest:
            errors.append("sources_digest_mismatch:" + name)


def check_contract_and_report(errors: list[str]) -> tuple[dict, dict]:
    if not CONTRACT.is_file() or not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("committed_artifacts_missing")
        return {}, {}
    try:
        contract = reference.read_strict_json(CONTRACT)
        report = reference.read_strict_json(REPORT)
    except ValueError as error:
        errors.append("strict_json_failure:" + str(error))
        return {}, {}
    expected_contract = reference.build_contract()
    if contract != expected_contract:
        errors.append("contract_not_canonical_or_stale")
    expected_report = reference.build_report(contract)
    if report != expected_report:
        errors.append("report_not_canonical_or_stale")
    if CONTRACT.read_bytes() != reference.canonical_bytes(contract):
        errors.append("contract_bytes_not_canonical")
    report_text, report_digest = reference.canonical_report(report)
    if REPORT.read_bytes() != report_text.encode("ascii"):
        errors.append("report_bytes_not_canonical")
    sidecar = SIDECAR.read_text(encoding="ascii").strip()
    if sidecar != report_digest + "  report.json":
        errors.append("report_sha256_mismatch")
    # Policy checks
    if report.get("decision") != "DEFER":
        errors.append("decision_not_defer")
    if report.get("status") != "incomplete":
        errors.append("status_not_incomplete")
    if report.get("qualification_status") != "not_qualified":
        errors.append("qualification_not_not_qualified")
    if report.get("proposal_only") is not True:
        errors.append("not_proposal_only")
    if report.get("claim_eligible") is not False or report.get("release_claim_eligible") is not False:
        errors.append("claim_eligible")
    gates = report.get("gates", [])
    if len(gates) != 5:
        errors.append("gate_count")
    for g in gates:
        if g.get("status") != "blocked" or g.get("qualifies") is not False:
            errors.append("gate_not_blocked:" + str(g.get("id")))
    blockers = report.get("blockers", [])
    if len(blockers) != 5:
        errors.append("blocker_count")
    for b in blockers:
        if b.get("status") != "open" or b.get("qualifies") is not False:
            errors.append("blocker_not_open:" + str(b.get("id")))
    absence = report.get("absence_summary", {})
    if absence.get("all_absent") is not True or absence.get("present_count") != 0:
        errors.append("absence_probe_present")
    snippets = report.get("evidence_snippets", {})
    if snippets.get("all_present") is not True:
        errors.append("evidence_snippet_missing")
    scope = report.get("scope", {})
    for k in ("provider_registered", "default_enabled", "public_api_changed", "abi_changed",
              "contracts_changed", "shared_build_changed", "ci_behavior_changed"):
        if scope.get(k) is not False:
            errors.append("scope_flag_true:" + k)
    for k in ("task_write_scope_only", "task_local_only"):
        if scope.get(k) is not True:
            errors.append("scope_flag_false:" + k)
    return contract, report


def _check_imports(errors: list[str], path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [(node.module or "").split(".")[0]]
        else:
            continue
        for name in names:
            if name in FORBIDDEN_MODULES:
                errors.append("forbidden_import:" + name + ":" + path.name)
            if name and name not in ALLOWED_IMPORTS:
                errors.append("unexpected_import:" + name + ":" + path.name)


def check_licensing(errors: list[str]) -> None:
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("license_sidecar_missing:" + name)
        elif path.read_text(encoding="utf-8") != SIDECAR_TEXT:
            errors.append("license_sidecar_text_mismatch:" + name)
    for name in ("README.md", "LICENSES.md"):
        path = HERE / name
        if not path.is_file():
            errors.append("missing_file:" + name)
            continue
        text = path.read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("missing_spdx_header:" + name)
    for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
        path = HERE / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        head = "\n".join(text.splitlines()[:5])
        if SPDX_COPYRIGHT not in head or SPDX_LICENSE not in head:
            errors.append("missing_inline_spdx_header:" + name)
        for n, line in enumerate(text.splitlines(), start=1):
            if n > 2 and SPDX_TAG in line:
                errors.append(f"inline_spdx_expression_in_literal:{name}:{n}")
        _check_imports(errors, path)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in reference.FORBIDDEN_SUFFIXES:
            errors.append("forbidden_payload_file:" + path.name)


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
            errors.append("git_" + "_".join(arguments).replace("--", "") + "_failed:" + diff.stdout.strip())
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
                errors.append("base_out_of_scope_change:" + path)
                ok = False
    return ok


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    if not REPORT.is_file() or not CONTRACT.is_file() or not SIDECAR.is_file():
        errors.append("cannot_cold_start_without_committed_artifacts")
        return []
    with tempfile.TemporaryDirectory(prefix="whisper-transcription-verify-") as root:
        target = Path(root) / "pkg"
        target.mkdir()
        shutil.copy2(HERE / "reference.py", target / "reference.py")
        shutil.copy2(HERE / "run.py", target / "run.py")
        # copy committed task-local artifacts so SOURCES pinning is stable
        for name in reference.EXPECTED_DIR_FILES:
            src = HERE / name
            if src.is_file() and name not in {"reference.py", "run.py"}:
                shutil.copy2(src, target / name)
        env = dict(os.environ)
        env["AUDIOML_ROOT"] = str(reference.AUDIO_ROOT)
        env["SDK_WORKTREE"] = str(reference.WORKTREE)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONHASHSEED"] = "0"
        digests: list[str] = []
        for _ in range(3):
            result = subprocess.run(
                [sys.executable, str(target / "run.py"), "all"],
                cwd=str(target), env=env, capture_output=True, text=True)
            if result.returncode != 0:
                errors.append("cold_start_run_failed:" + (result.stderr.strip() or result.stdout.strip()))
                return digests
            digests.append(hashlib.sha256((target / "report.json").read_bytes()).hexdigest())
        if len(set(digests)) != 1:
            errors.append("cold_start_not_byte_identical")
            return digests
        if (target / "report.json").read_bytes() != REPORT.read_bytes():
            errors.append("cold_start_report_differs")
        if (target / "contract.json").read_bytes() != CONTRACT.read_bytes():
            errors.append("cold_start_contract_differs")
        if (target / "report.json.sha256").read_text(encoding="ascii") != SIDECAR.read_text(encoding="ascii"):
            errors.append("cold_start_sidecar_differs")
    return digests


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_files(errors)
    pins = check_pins(errors)
    readme = check_readme(errors)
    check_sources_manifest(errors)
    contract, report = check_contract_and_report(errors)
    check_licensing(errors)
    check_scope(errors)
    repeats = check_cold_start_regeneration(errors)
    if errors:
        for e in errors:
            print("FAIL: " + e, file=sys.stderr)
        print(f"FAIL verification ({len(errors)} errors)", file=sys.stderr)
        return 1
    print(
        "PASS verify.py "
        f"version={platform.python_version()} "
        f"contract_sha256={reference.object_digest(contract)} "
        f"report_sha256={hashlib.sha256(REPORT.read_bytes()).hexdigest()} "
        f"pins={pins} readme_rows={','.join(f'{k}={v}' for k,v in sorted(readme.items()))} "
        f"cold_starts={len(repeats)}/3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
