# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for SDK-WORLD-VOCODER blocker evidence."""

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
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECARS = ("SOURCES.sha256.license", "contract.json.license", "report.json.license", "report.json.sha256.license")
FORBIDDEN_SUFFIXES = {".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".gguf", ".lib", ".m4a", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o", ".onnx", ".opus", ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wasm", ".wav", ".weights"}


def check_profile(errors: list[str]) -> None:
    path = reference.AUDIO_ROOT / "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
    if not path.is_file():
        errors.append("profile_source_missing")
        return
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| Voice |")]
    if len(rows) != 1:
        errors.append("voice_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in ((reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"), (reference.BOUNDARY_PINS, SDK_ROOT, "boundary")):
        for rel, expected in sorted(pins.items()):
            path = root / rel
            if not path.is_file():
                errors.append(label + "_pin_missing:" + rel)
                continue
            actual = reference.sha256_file(path)
            if actual != expected:
                errors.append(label + "_pin_mismatch:" + rel)
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
    except ValueError as e:
        errors.append("contract_validation:" + str(e))
        return {}
    return contract


def check_report(errors: list[str], contract: dict) -> dict:
    if not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("committed_artifacts_missing")
        return {}
    try:
        report = reference.read_strict_json(REPORT)
    except ValueError as e:
        errors.append("strict_json_failure:" + str(e))
        return {}
    for k, v in (("schema_id", reference.REPORT_SCHEMA_ID), ("task", reference.TASK), ("component", reference.COMPONENT_ID), ("decision", "DEFER"), ("status", "incomplete"), ("qualification_status", "not_qualified")):
        if report.get(k) != v:
            errors.append("report_" + k)
    if report.get("proposal_only") is not True:
        errors.append("report_not_proposal_only")
    if contract:
        if report.get("contract_sha256") != reference.object_digest(contract):
            errors.append("contract_digest_mismatch")
        for key in ("disposition", "qualification", "required_artifacts", "exact_blockers", "required_results", "scope", "boundary", "public_v0_geometry", "non_claims", "reproduction"):
            if report.get(key) != contract.get(key):
                errors.append("contract_copy_mismatch:" + key)
        if report.get("gates") != contract.get("release_gates"):
            errors.append("contract_copy_mismatch:release_gates")
        if report.get("voice_profile", {}).get("rows") != contract.get("voice_profile_requirements"):
            errors.append("contract_copy_mismatch:voice_profile")
        if report.get("quality_outcomes", {}).get("rows") != contract.get("quality_outcomes"):
            errors.append("contract_copy_mismatch:quality_outcomes")
        if report.get("timing", {}).get("rows") != contract.get("timing_requirements"):
            errors.append("contract_copy_mismatch:timing")

    gates = report.get("gates", [])
    if len(gates) != 8:
        errors.append("gate_count")
    for i, g in enumerate(gates, 1):
        if g.get("id") != f"RG-{i:02d}" or g.get("status") != "blocked" or g.get("qualifies") is not False or not g.get("reopen_condition"):
            errors.append("gate_invalid:" + str(g.get("id")))
        if g.get("linked_row") != reference.BOARD_ROW_PROJECTION:
            errors.append("gate_linked_row:" + str(g.get("id")))

    arts = report.get("required_artifacts", [])
    if len(arts) != 6 or not arts or arts[0].get("present") is not True or arts[0].get("verified") is not True or arts[0].get("blocked") is not False:
        errors.append("artifact_source")
    for a in arts[1:]:
        if a.get("present") is not False or a.get("verified") is not False or a.get("blocked") is not True or a.get("sha256") is not None:
            errors.append("artifact_not_blocked:" + str(a.get("id")))

    blockers = report.get("exact_blockers", [])
    if len(blockers) != 5:
        errors.append("blocker_count")
    for b in blockers:
        if b.get("status") != "open" or b.get("qualifies") is not False or not b.get("required_action"):
            errors.append("blocker_invalid:" + str(b.get("id")))

    for rows, n, key in ((report.get("voice_profile", {}).get("rows", []), 8, "voice"), (report.get("quality_outcomes", {}).get("rows", []), 4, "quality"), (report.get("timing", {}).get("rows", []), 4, "timing")):
        if len(rows) != n:
            errors.append(key + "_row_count")
        for r in rows:
            if r.get("status") != "blocked":
                errors.append(key + "_row_not_blocked:" + str(r.get("id")))
            if "value" in r and r.get("value") is not None:
                errors.append(key + "_row_value:" + str(r.get("id")))

    absence = report.get("absence_evidence", {}).get("summary", {})
    if absence.get("present_count") != 0 or absence.get("all_probes_absent") is not True:
        errors.append("absence_present")
    if absence.get("probe_count") != len(reference.ABSENCE_PROBES) + len(reference.HOME_ABSENCE_PROBES):
        errors.append("absence_probe_count")
    for k in ("download_attempted", "network_used", "recursive_workspace_walk", "source_or_runtime_imported", "weights_loaded", "model_executed", "audio_read", "feature_input_read"):
        if absence.get(k) is not False:
            errors.append("absence_" + k)

    admission = report.get("admission", {})
    expected_admission = reference.admission_controls()
    if admission != expected_admission:
        errors.append("admission_mismatch")
    asu = admission.get("summary", {})
    if asu.get("qualifying_results") != 0 or asu.get("accepted_schema_controls") != 1 or asu.get("rejected_count") != asu.get("case_count"):
        errors.append("admission_summary_invalid")
    for k in ("state_advanced_on_rejection", "runtime_invoked", "audio_read", "feature_input_read", "weights_loaded", "model_executed", "network_used"):
        if asu.get(k) is not False:
            errors.append("admission_" + k)
    for case in admission.get("cases", []):
        if case.get("status") != "rejected" or case.get("qualifies") is not False or case.get("state_unchanged") is not True:
            errors.append("admission_case:" + str(case.get("id")))

    li = report.get("linked_row_identity", {})
    if li.get("projection") != reference.BOARD_ROW_PROJECTION or li.get("sha256") != reference.board_row_digest(reference.BOARD_ROW_PROJECTION):
        errors.append("linked_identity")
    if li.get("gating") != "stable_identity_only" or li.get("board_file_pinned") is not False or li.get("board_status_gates_anything") is not False:
        errors.append("linked_identity_policy")
    if li.get("linked_rows") != [dict(r) for r in reference.LINKED_ROWS] or li.get("linked_rows_sha256") != reference.linked_rows_digest():
        errors.append("linked_rows")

    required = report.get("required_results", {})
    for k, v in required.items():
        expected = True if k == "no_result_qualifies" else False
        if v is not expected:
            errors.append("required_results:" + k)

    expected_source = {p: {"sha256": d, "actual": d, "verified": True} for p, d in reference.SOURCE_PINS.items()}
    expected_boundary = {p: {"sha256": d, "actual": d, "verified": True} for p, d in reference.BOUNDARY_PINS.items()}
    if report.get("source_pins") != expected_source:
        errors.append("report_source_pins_mismatch")
    if report.get("boundary_pins") != expected_boundary:
        errors.append("report_boundary_pins_mismatch")

    payload = REPORT.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if SIDECAR.read_text(encoding="ascii") != f"{digest}  report.json\n":
        errors.append("report_sidecar_mismatch")
    if payload != reference.canonical_bytes(report):
        errors.append("report_not_canonical")
    try:
        reference._no_floats(report)
    except ValueError as e:
        errors.append("report_float:" + str(e))
    if PINS.is_file():
        try:
            expected_pins = run.sources_bytes()
        except ValueError as e:
            errors.append("sources_rebuild:" + str(e))
        else:
            if PINS.read_bytes() != expected_pins:
                errors.append("sources_manifest_mismatch")
    else:
        errors.append("sources_manifest_missing")
    return report


def check_text_metadata(errors: list[str]) -> None:
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("sidecar_missing:" + name)
            continue
        text = path.read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("sidecar_spdx_missing:" + name)
    for name in ("README.md", "LICENSES.md"):
        path = HERE / name
        if not path.is_file():
            errors.append("doc_missing:" + name)
            continue
        text = path.read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("doc_spdx_missing:" + name)
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_COPYRIGHT not in head or SPDX_LICENSE not in head:
            errors.append("py_spdx_missing:" + path.name)
    try:
        reference.verify_readme_digests((HERE / "README.md").read_text(encoding="utf-8"))
    except Exception as e:
        errors.append("readme_digest_mismatch:" + str(e))


def check_hygiene(errors: list[str]) -> None:
    for path in sorted(HERE.iterdir()):
        if path.name == "__pycache__":
            shutil.rmtree(path, ignore_errors=True)
            continue
        if path.is_symlink():
            errors.append("symlink_present:" + path.name)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + path.name)
    for p in HERE.rglob("*"):
        if "__pycache__" in p.parts:
            errors.append("pycache_present")


def _run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(SDK_ROOT), *args], capture_output=True, text=True, check=False)


def check_scope(errors: list[str]) -> list[str]:
    status = _run_git("status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0:
        errors.append("git_status_failed:" + status.stderr.strip())
        return []
    changed: list[str] = []
    for line in status.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for args in (("diff", "--check"), ("diff", "--cached", "--check")):
        diff = _run_git(*args)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(args).replace("--", "") + "_failed:" + diff.stdout.strip())
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
    else:
        try:
            scoped = reference.scope_changed_paths(SDK_ROOT, base)
        except ValueError as e:
            errors.append(str(e))
        else:
            for p in reference.scope_violations(scoped):
                errors.append("base_out_of_scope_change:" + p)
    return changed


def regenerate_report(errors: list[str]) -> str:
    with tempfile.TemporaryDirectory(prefix="world-vocoder-verify-") as temp:
        path = Path(temp) / "report.json"
        path.write_bytes(reference.canonical_bytes(reference.build_report()))
        digest = reference.sha256_file(path)
        if REPORT.is_file() and reference.sha256_file(REPORT) != digest:
            errors.append("cold_regen_mismatch")
        return digest


def main(argv: list[str]) -> int:
    os.chdir(HERE)
    errors: list[str] = []
    check_profile(errors)
    checked = check_pins(errors)
    contract = check_contract(errors)
    report = check_report(errors, contract)
    check_scope(errors)
    check_text_metadata(errors)
    check_hygiene(errors)
    regenerated = regenerate_report(errors)
    absence = report.get("absence_evidence", {}).get("summary", {})
    admission = report.get("admission", {}).get("summary", {})
    ok = not errors
    print(f"SDK-WORLD-VOCODER verify: {'PASS' if ok else 'FAIL'} decision={report.get('decision','unknown')} qualifies=no")
    print(f"  checked_pins={checked} board_pinned=false gates_blocked=8 blockers={len(report.get('exact_blockers', []))}")
    print(f"  absence_probes={absence.get('probe_count', 0)} present={absence.get('present_count', 0)} admission_rejected={admission.get('rejected_count', 0)} qualifying={admission.get('qualifying_results', 0)}")
    print(f"  regenerated_report_sha256={regenerated}")
    if not ok:
        for e in errors:
            print("ERROR:", e)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
