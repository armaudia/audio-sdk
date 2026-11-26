# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for SDK-VOCOS-BWE blocker evidence."""

from __future__ import annotations

import hashlib
import os
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

# REUSE-IgnoreStart
SPDX_LICENSE = "SPDX-" "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-" "FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd

SIDECARS = ("SOURCES.sha256.license", "contract.json.license", "report.json.license", "report.json.sha256.license")
FORBIDDEN_SUFFIXES = {".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".gguf", ".lib", ".m4a", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o", ".onnx", ".opus", ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wasm", ".wav", ".weights"}


def check_profile_source(errors: list[str]) -> None:
    path = reference.AUDIO_ROOT / "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
    if not path.is_file():
        errors.append("profile_source_missing")
        return
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| Restoration |")]
    if len(rows) != 1:
        errors.append("restoration_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in ((reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"), (reference.BOUNDARY_PINS, reference.WORKTREE, "boundary")):
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                errors.append(label + "_pin_missing:" + relative)
                continue
            actual = reference.sha256_file(path)
            if actual != expected:
                errors.append(label + "_pin_mismatch:" + relative)
            checked += 1
    if reference.BOARD_TASK_ROW in reference.SOURCE_PINS or reference.BOARD_TASK_ROW in reference.BOUNDARY_PINS:
        errors.append("mutable_board_pinned")
    return checked


def check_contract(errors: list[str]) -> dict:
    if not CONTRACT.is_file():
        errors.append("contract_missing")
        return {}
    try:
        contract = reference.read_strict_json(CONTRACT)
        reference.validate_contract(contract)
    except ValueError as error:
        errors.append("contract_validation:" + str(error))
        return {}
    if contract.get("decision") != "DEFER" or contract.get("status") != "incomplete" or contract.get("qualification_status") != "not_qualified" or contract.get("proposal_only") is not True:
        errors.append("contract_disposition")
    if contract.get("board_file_pinned") is not False:
        errors.append("contract_board_pinned")
    return contract


def check_report(errors: list[str], contract: dict) -> dict:
    if not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("committed_artifacts_missing")
        return {}
    try:
        report = reference.read_strict_json(REPORT)
    except ValueError as error:
        errors.append("strict_json_failure:" + str(error))
        return {}
    expected = reference.build_report()
    if report != expected:
        errors.append("report_not_canonical_or_stale")
    if contract and report.get("contract_sha256") != reference.object_digest(contract):
        errors.append("contract_digest_mismatch")
    payload = REPORT.read_bytes()
    expected_payload, digest = reference.canonical_report(report)
    expected_payload = expected_payload.encode("utf-8")
    if payload != expected_payload:
        errors.append("report_not_canonical")
    digest = hashlib.sha256(payload).hexdigest()
    if SIDECAR.read_text(encoding="ascii") != f"{digest}  report.json\n":
        errors.append("report_sidecar_mismatch")
    if report.get("decision") != "DEFER" or report.get("status") != "incomplete" or report.get("qualification_status") != "not_qualified":
        errors.append("report_disposition")
    gates = report.get("gates", [])
    if len(gates) != 8 or not all(g.get("status") == "blocked" and g.get("qualifies") is False for g in gates):
        errors.append("gates_not_blocked")
    blockers = report.get("exact_blockers", [])
    if len(blockers) != 6 or not all(b.get("status") == "open" and b.get("qualifies") is False for b in blockers):
        errors.append("blockers_not_open")
    if report.get("qualification", {}).get("all_release_gates_blocked") is not True:
        errors.append("qualification_not_blocked")
    if report.get("linked_row_identity", {}).get("board_file_pinned") is not False:
        errors.append("board_file_pinned")
    if report.get("linked_row_identity", {}).get("board_status_gates_anything") is not False:
        errors.append("board_status_gates")
    if report.get("absence_evidence", {}).get("summary", {}).get("all_probes_absent") is not True:
        errors.append("absence_probe_present")
    admission = report.get("admission", {})
    if admission.get("control", {}).get("accepted") is not True or admission.get("control", {}).get("qualifies") is not False:
        errors.append("admission_control")
    if admission.get("summary", {}).get("qualifying_results") != 0:
        errors.append("admission_qualifying_result")
    if admission.get("summary", {}).get("case_count") != admission.get("summary", {}).get("rejected_count") + admission.get("summary", {}).get("accepted_schema_controls", 0):
        errors.append("admission_not_fail_closed")
    if PINS.is_file():
        try:
            expected_pins = run.sources_bytes()
        except ValueError as error:
            errors.append("sources_rebuild:" + str(error))
        else:
            if PINS.read_bytes() != expected_pins:
                errors.append("sources_manifest_mismatch")
    else:
        errors.append("sources_manifest_missing")
    return report


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        text = ((HERE / name).read_text(encoding="utf-8") if (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    for name in ("README.md", "LICENSES.md"):
        text = ((HERE / name).read_text(encoding="utf-8") if (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_markdown_spdx:" + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    # REUSE-IgnoreStart
    reuse_token = 'SPDX-License-Identifier = "Apache-2.0"'
    # REUSE-IgnoreEnd
    if '"docs/**"' not in reuse or reuse_token not in reuse:
        errors.append("reuse_docs_coverage_missing")
    for path in sorted(HERE.iterdir()):
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + path.name)
        if path.is_symlink():
            errors.append("task_symlink:" + path.name)


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"], capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return []
    changed: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(run.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for args in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), *args], capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_diff_check_failed:" + diff.stdout.strip())
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-VOCOS-BWE"
    target = sdk / "docs/task-evidence/vocos-bwe"
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.SOURCE_PINS):
        link = scratch / "audioml" / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / relative)
    board = scratch / "audioml" / reference.BOARD_TASK_ROW
    board.parent.mkdir(parents=True, exist_ok=True)
    board.symlink_to(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.WORKTREE / relative)
    return target


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    committed = ((CONTRACT.read_bytes() if CONTRACT.is_file() else b""), (REPORT.read_bytes() if REPORT.is_file() else b""), (SIDECAR.read_bytes() if SIDECAR.is_file() else b""), (PINS.read_bytes() if PINS.is_file() else b""))
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(prefix="sdk-vocos-bwe-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py", "all"], cwd=target, capture_output=True, text=True, env=env)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:" + process.stderr.strip())
                continue
            generated = ((target / "contract.json").read_bytes(), (target / "report.json").read_bytes(), (target / "report.json.sha256").read_bytes(), (target / "SOURCES.sha256").read_bytes())
            if generated != committed:
                errors.append(f"cold_start_{index}_bytes_differ")
            digests.append(hashlib.sha256(generated[1]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    check_profile_source(errors)
    pins = check_pins(errors)
    contract = check_contract(errors)
    report = check_report(errors, contract)
    check_licensing(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = hashlib.sha256(REPORT.read_bytes()).hexdigest() if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} checks_ok={bool(report)} cold_starts={len(digests)} report_sha256={digest} changed_files={len(changed)} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates={len(report['gates'])} blockers={len(report['exact_blockers'])} admission_cases={len(report['admission']['cases'])} cold_starts=3/3 byte_identical=true profile=Restoration status={report['status']} decision=DEFER qualification=not_qualified report_sha256={digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
