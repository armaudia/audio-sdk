# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only fail-closed verifier for transient-aware-phase-vocoder evidence."""

from __future__ import annotations

import ast
import hashlib
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

SDK_ROOT = reference.SDK_ROOT
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECARS = ("contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license")
FORBIDDEN_IMPORTS = {"requests", "urllib", "http", "socket", "numpy", "torch", "torchaudio", "tensorflow", "onnxruntime", "scipy", "librosa", "soundfile"}


def check_interpreter(errors: list[str]) -> None:
    if platform.python_version() != reference.REQUIRED_INTERPRETER:
        errors.append(f"interpreter:{platform.python_version()}")


def check_files(errors: list[str]) -> None:
    obs = {p.name for p in HERE.iterdir() if p.is_file() and not p.name.startswith(".")}
    extra = sorted(obs - reference.EXPECTED_DIR_FILES)
    missing = sorted(reference.EXPECTED_DIR_FILES - obs)
    if extra:
        errors.append("unexpected:" + ",".join(extra))
    if missing:
        errors.append("missing:" + ",".join(missing))


def check_pins(errors: list[str]) -> int:
    n = 0
    for pins, root, label in ((reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"), (reference.BOUNDARY_PINS, SDK_ROOT, "boundary")):
        for rel, exp in sorted(pins.items()):
            p = root / rel
            if not p.is_file():
                errors.append(f"{label}_missing:{rel}")
                continue
            if reference.sha256_file(p) != exp:
                errors.append(f"{label}_mismatch:{rel}")
            n += 1
    return n


def check_readme(errors: list[str]) -> dict[str, int]:
    p = HERE / "README.md"
    if not p.is_file():
        errors.append("readme_missing")
        return {}
    try:
        return reference.verify_readme_digests(p.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append("readme_digest:" + str(e))
        return {}


def check_sources(errors: list[str]) -> None:
    p = HERE / "SOURCES.sha256"
    if not p.is_file():
        errors.append("sources_missing")
        return
    if p.read_bytes() != run.sources_bytes():
        errors.append("sources_drift")
    for line in p.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or not reference.HEX64.match(parts[0]):
            errors.append("sources_malformed")
            continue
        digest, name = parts
        if name.startswith("source:"):
            fs = reference.AUDIO_ROOT / name[len("source:"):]
        else:
            fs = SDK_ROOT / name
        if not fs.is_file():
            errors.append("sources_path_missing:" + name)
        elif reference.sha256_file(fs) != digest:
            errors.append("sources_digest_mismatch:" + name)


def check_contract(errors: list[str]) -> dict:
    p = HERE / "contract.json"
    if not p.is_file():
        errors.append("contract_missing")
        return {}
    try:
        doc = reference.read_strict_json(p)
    except Exception as e:
        errors.append("contract_invalid:" + str(e))
        return {}
    exp = reference.build_contract()
    if doc != exp:
        errors.append("contract_builder_mismatch")
    if p.read_bytes() != reference.canonical_bytes(exp):
        errors.append("contract_not_canonical")
    if doc.get("decision") != reference.DECISION:
        errors.append("contract_decision")
    if doc.get("qualification_status") != reference.QUALIFICATION:
        errors.append("contract_qualification")
    if doc.get("boundary", {}).get("linked_row") != reference.board_row_projection():
        errors.append("contract_linked_row")
    return doc


def check_report(errors: list[str]) -> dict:
    p = HERE / "report.json"
    if not p.is_file():
        errors.append("report_missing")
        return {}
    try:
        doc = reference.read_strict_json(p)
    except Exception as e:
        errors.append("report_invalid:" + str(e))
        return {}
    exp = reference.build_report()
    payload, digest = reference.canonical_report(exp)
    if doc != exp:
        errors.append("report_builder_mismatch")
    if p.read_bytes() != payload.encode("ascii"):
        errors.append("report_not_canonical")
    sc = HERE / "report.json.sha256"
    if not sc.is_file() or sc.read_text(encoding="ascii") != digest + "  report.json\n":
        errors.append("report_sidecar_mismatch")
    for k, v in {
        "task": reference.TASK, "decision": reference.DECISION, "qualification_status": reference.QUALIFICATION,
        "status": reference.STATUS, "evidence_status": reference.EVIDENCE_STATUS, "profile": reference.PROFILE,
    }.items():
        if doc.get(k) != v:
            errors.append("report_field:" + k)
    if doc.get("proposal_only") is not True or doc.get("incomplete") is not True:
        errors.append("report_flags")
    gates = doc.get("release_gates", [])
    if [g.get("id") for g in gates] != [f"RG-{i:02d}" for i in range(1, 9)]:
        errors.append("gate_ids")
    for g in gates:
        if g.get("status") != "blocked" or g.get("qualifies") is not False:
            errors.append("gate_not_blocked:" + str(g.get("id")))
    blockers = doc.get("exact_blockers", [])
    if [b.get("id") for b in blockers] != [f"BLK-{i:02d}" for i in range(1, 6)]:
        errors.append("blocker_ids")
    for b in blockers:
        if b.get("status") != "open" or b.get("qualifies") is not False:
            errors.append("blocker_not_open:" + str(b.get("id")))
    if doc.get("contract_sha256") != reference.object_digest(reference.build_contract()):
        errors.append("report_contract_digest")
    return doc


def check_declaration(errors: list[str], report: dict) -> None:
    decl = report.get("asset_declaration", {})
    acc = decl.get("accepted_unpopulated")
    schema = decl.get("schema", {})
    if acc is None:
        errors.append("declaration_missing")
        return
    try:
        reference.validate_asset_declaration(acc)
    except Exception as e:
        errors.append("declaration_invalid:" + str(e))
    if schema.get("all_rejected") is not True or schema.get("strict_json_all_rejected") is not True:
        errors.append("declaration_rejections_incomplete")


def check_absence(errors: list[str], report: dict) -> None:
    absn = report.get("absence_summary", {})
    if absn.get("all_absent") is not True or absn.get("present_count") != 0:
        errors.append("absence_not_clean")
    expected = len(reference.WORKSPACE_PROBES) + len(reference.WORKTREE_PROBES) + len(reference.HOME_PROBES)
    if absn.get("probe_count") != expected:
        errors.append("absence_probe_count")


def check_scope(errors: list[str]) -> None:
    base, committed = reference.committed_paths_since_base(SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
    for p in committed:
        if not reference.path_is_within_prefix(p, reference.TASK_PREFIX):
            errors.append("base_out_of_scope_change:" + p)
    for p in reference.collect_dirty_paths(SDK_ROOT):
        if not reference.path_is_within_prefix(p, reference.TASK_PREFIX):
            errors.append("dirty_out_of_scope_change:" + p)


def check_license(errors: list[str]) -> None:
    for name in SIDECARS:
        p = HERE / name
        if not p.is_file() or SPDX_COPYRIGHT not in p.read_text(encoding="ascii") or SPDX_LICENSE not in p.read_text(encoding="ascii"):
            errors.append("sidecar_license:" + name)
    for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("source_license:" + name)
        contiguous = "SPDX-License-" + "Identifier: Apache-2.0"
        # allow in comment headers; reject inside python string literal forms commonly caught by naive grep - easier: check for contiguous token in quotes
        if ('"' + contiguous + '"') in text or ("'" + contiguous + "'") in text:
            errors.append("contiguous_spdx_literal:" + name)


def check_imports(errors: list[str]) -> None:
    for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
        tree = ast.parse((HERE / name).read_text(encoding="utf-8"), filename=name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    root = a.name.split(".")[0]
                    if root in FORBIDDEN_IMPORTS:
                        errors.append("forbidden_import:" + name + ":" + a.name)
            if isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in FORBIDDEN_IMPORTS:
                    errors.append("forbidden_import:" + name + ":" + node.module)


def check_forbidden_files(errors: list[str]) -> None:
    for p in HERE.rglob("*"):
        if p.is_file() and reference.has_forbidden_suffix(p):
            errors.append("forbidden_file:" + p.name)


def check_regen(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="tapv-verify-") as tmp:
        td = Path(tmp) / HERE.name
        shutil.copytree(HERE, td)
        proc = subprocess.run([sys.executable, str(td / "run.py"), "all"], capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            errors.append("run_failed:" + proc.stdout + proc.stderr)
            return
        for name in sorted(reference.EXPECTED_DIR_FILES):
            if (HERE / name).read_bytes() != (td / name).read_bytes():
                errors.append("regen_drift:" + name)


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_files(errors)
    pins = check_pins(errors)
    readme = check_readme(errors)
    check_sources(errors)
    check_contract(errors)
    report = check_report(errors)
    if report:
        check_declaration(errors, report)
        check_absence(errors, report)
    check_scope(errors)
    check_license(errors)
    check_imports(errors)
    check_forbidden_files(errors)
    check_regen(errors)
    if errors:
        for e in errors:
            print("FAIL " + e)
        print(f"FAIL verify.py errors={len(errors)}")
        return 1
    print(f"PASS verify.py pins={pins} readme_sections={len(readme)} gates={len(report.get('release_gates',[]))} blockers={len(report.get('exact_blockers',[]))} decision={report.get('decision')} qualification={report.get('qualification_status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
