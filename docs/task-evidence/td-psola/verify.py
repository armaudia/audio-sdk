# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-TD-PSOLA evidence package."""

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
SOURCES = HERE / "SOURCES.sha256"

SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECAR_TEXT = SPDX_COPYRIGHT + "\n" + SPDX_LICENSE + "\n"

EXPECTED_FILES = frozenset(reference.EXPECTED_DIR_FILES)
PIN_LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")
FORBIDDEN_MODULES = frozenset({
    "requests", "urllib", "http", "socket", "torch", "torchaudio",
    "numpy", "scipy", "librosa", "soundfile", "praat-parselmouth",
    "parselmouth", "diffusers",
})


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append(f"interpreter mismatch: pinned {reference.REQUIRED_INTERPRETER} observed {observed}")


def check_files(errors: list[str]) -> None:
    observed = {p.name for p in HERE.iterdir() if p.is_file() and not p.name.startswith('.')}
    extra = sorted(observed - EXPECTED_FILES)
    missing = sorted(EXPECTED_FILES - observed)
    if extra:
        errors.append("unexpected files: " + ",".join(extra))
    if missing:
        errors.append("missing files: " + ",".join(missing))


def check_pins(errors: list[str]) -> None:
    for rel, expected in sorted(reference.SOURCE_PINS.items()):
        path = reference.AUDIO_ROOT / rel
        if not path.is_file():
            errors.append("source pin missing: " + rel)
        elif reference.sha256_file(path) != expected:
            errors.append("source pin mismatch: " + rel)
    for rel, expected in sorted(reference.BOUNDARY_PINS.items()):
        path = SDK_ROOT / rel
        if not path.is_file():
            errors.append("boundary pin missing: " + rel)
        elif reference.sha256_file(path) != expected:
            errors.append("boundary pin mismatch: " + rel)


def check_sources_manifest(errors: list[str]) -> None:
    if not SOURCES.is_file():
        errors.append("SOURCES.sha256 missing")
        return
    rows: dict[str, str] = {}
    for line in SOURCES.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        m = PIN_LINE.match(line)
        if not m:
            errors.append("malformed SOURCES line: " + line[:80])
            continue
        digest, name = m.groups()
        if name in rows:
            errors.append("duplicate SOURCES row: " + name)
        rows[name] = digest
    expected: dict[str, str] = {}
    for rel in reference.SOURCE_PINS:
        expected["source:" + rel] = reference.sha256_file(reference.AUDIO_ROOT / rel)
    for rel in reference.BOUNDARY_PINS:
        expected[rel] = reference.sha256_file(SDK_ROOT / rel)
    for name in sorted(EXPECTED_FILES - {"SOURCES.sha256"}):
        expected[reference.TASK_PREFIX + name] = reference.sha256_file(HERE / name)
    if set(rows) != set(expected):
        missing = sorted(set(expected) - set(rows))
        extra = sorted(set(rows) - set(expected))
        if missing:
            errors.append("SOURCES missing: " + ",".join(missing[:8]))
        if extra:
            errors.append("SOURCES extra: " + ",".join(extra[:8]))
    for name, digest in rows.items():
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
        errors.append("mutable board must not be pinned")


def _check_linked_row(errors: list[str], boundary: dict) -> None:
    projection = reference.board_row_projection()
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
        doc = reference.read_strict_json(CONTRACT)
    except Exception as error:  # noqa: BLE001
        errors.append("contract JSON invalid: " + str(error))
        return {}
    expected = reference.build_contract()
    if doc != expected:
        errors.append("contract.json does not match builder")
    if CONTRACT.read_bytes() != reference.canonical_bytes(expected):
        errors.append("contract.json is not canonical")
    if doc.get("decision") != "DEFER":
        errors.append("contract decision must be DEFER")
    if doc.get("qualification_status") != "not_qualified":
        errors.append("contract qualification must be not_qualified")
    if doc.get("proposal_only") is not True:
        errors.append("contract proposal_only must be true")
    gates = doc.get("release_gates", [])
    if [g.get("id") for g in gates] != [f"RG-{i:02d}" for i in range(1, 9)]:
        errors.append("contract must have RG-01..RG-08")
    for gate in gates:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            errors.append("contract gate not blocked: " + str(gate.get("id")))
    _check_linked_row(errors, doc.get("boundary", {}))
    return doc


def check_report(errors: list[str]) -> dict:
    if not REPORT.is_file():
        errors.append("report.json missing")
        return {}
    try:
        doc = reference.read_strict_json(REPORT)
    except Exception as error:  # noqa: BLE001
        errors.append("report JSON invalid: " + str(error))
        return {}
    expected = reference.build_report()
    payload, digest = reference.canonical_report(expected)
    if doc != expected:
        errors.append("report.json does not match builder")
    if REPORT.read_bytes() != payload.encode("ascii"):
        errors.append("report.json is not canonical")
    if not SIDECAR.is_file():
        errors.append("report.json.sha256 missing")
    elif SIDECAR.read_text(encoding="ascii") != digest + "  report.json\n":
        errors.append("report.json.sha256 mismatch")

    if doc.get("schema_id") != reference.REPORT_SCHEMA_ID:
        errors.append("report schema mismatch")
    for key, value in {
        "task": reference.TASK, "component": reference.COMPONENT_ID,
        "title": reference.TASK_TITLE, "base_commit": reference.BASE_COMMIT,
        "branch": reference.BRANCH, "mode": reference.MODE,
        "profile": reference.PROFILE, "decision": "DEFER",
        "status": "incomplete", "qualification_status": "not_qualified",
    }.items():
        if doc.get(key) != value:
            errors.append("report field mismatch: " + key)
    if doc.get("proposal_only") is not True or doc.get("incomplete") is not True:
        errors.append("report must be proposal_only and incomplete")
    if doc.get("contract_sha256") != reference.object_digest(reference.build_contract()):
        errors.append("report contract digest mismatch")
    _check_linked_row(errors, doc.get("boundary", {}))

    gates = doc.get("gates", [])
    if [g.get("id") for g in gates] != [f"RG-{i:02d}" for i in range(1, 9)]:
        errors.append("report must have RG-01..RG-08")
    for gate in gates:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            errors.append("gate not blocked: " + str(gate.get("id")))
        if gate.get("linked_row") != doc.get("boundary", {}).get("linked_row"):
            errors.append("gate linked row mismatch: " + str(gate.get("id")))

    blockers = doc.get("exact_blockers", [])
    if [b.get("id") for b in blockers] != [f"BLK-{i:02d}" for i in range(1, 6)]:
        errors.append("report must have BLK-01..BLK-05")
    for b in blockers:
        if b.get("status") != "open" or b.get("qualifies") is not False:
            errors.append("blocker not open: " + str(b.get("id")))

    artifacts = doc.get("required_artifacts", [])
    if [a.get("id") for a in artifacts] != [f"ART-{i:02d}" for i in range(1, 8)]:
        errors.append("report must have ART-01..ART-07")
    if artifacts and (artifacts[0].get("present") is not True or artifacts[0].get("verified") is not True):
        errors.append("ART-01 must be present and verified")
    for a in artifacts[1:]:
        if a.get("present") is not False or a.get("blocked") is not True:
            errors.append("artifact must remain blocked: " + str(a.get("id")))

    q = doc.get("qualification", {})
    if q.get("not_qualified") is not True or q.get("status") != "not_qualified":
        errors.append("qualification must be not_qualified")
    if q.get("all_release_gates_blocked") is not True:
        errors.append("all release gates must be blocked")
    for k, v in q.items():
        if k in ("status", "readiness", "not_qualified", "all_release_gates_blocked", "reason"):
            continue
        if v is not False:
            errors.append("qualification claim must be false: " + k)

    rp = doc.get("rate_profile", {})
    if rp.get("profile_satisfied") is not False or rp.get("real_results") != 0:
        errors.append("rate profile must be unsatisfied with zero real results")
    rows = rp.get("requirement_rows", [])
    if len(rows) != 13:
        errors.append("rate profile must have 13 rows")
    if any(row.get("qualifies") for row in rows):
        errors.append("rate rows must not qualify")

    admission = doc.get("admission", {})
    recomputed = reference.declaration_rejections()
    strict = reference.strict_json_rejections()
    if admission.get("manifest_cases") != recomputed["rejection_cases"]:
        errors.append("admission case count mismatch")
    if admission.get("all_rejected") is not True:
        errors.append("admission must reject every invalid manifest")
    if admission.get("strict_json_cases") != strict["rejection_cases"]:
        errors.append("strict JSON case count mismatch")
    if admission.get("strict_json_all_rejected") is not True:
        errors.append("strict JSON suite must reject all")
    if admission.get("assets_never_loaded") is not True:
        errors.append("assets_never_loaded must be true")

    absence = doc.get("absence_evidence", {})
    if absence.get("all_absent") is not True or absence.get("present_count") != 0:
        errors.append("absence probes must all be absent")

    scope = doc.get("scope", {})
    if scope.get("task_local_only") is not True or scope.get("write_scope") != reference.WRITE_SCOPE:
        errors.append("scope mismatch")
    for k, v in scope.items():
        if k in ("task_local_only", "write_scope"):
            continue
        if v is not False:
            errors.append("scope claim must be false: " + k)
    return doc


def check_licensing(errors: list[str]) -> None:
    for name in ("contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"):
        path = HERE / name
        if not path.is_file():
            errors.append("missing sidecar: " + name)
        elif path.read_text(encoding="ascii") != SIDECAR_TEXT:
            errors.append("sidecar mismatch: " + name)
    for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing SPDX header: " + name)
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in FORBIDDEN_MODULES:
                        errors.append("forbidden import: " + alias.name)
            if isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in FORBIDDEN_MODULES:
                    errors.append("forbidden import: " + node.module)


def _branch_base() -> str:
    for ref in ("origin/main", "main"):
        result = subprocess.run(["git", "-C", str(SDK_ROOT), "merge-base", "HEAD", ref], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return reference.BASE_COMMIT


def check_scope(errors: list[str]) -> None:
    try:
        status = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "status", "--porcelain", "--untracked-files=all"],
            check=True, capture_output=True, text=True).stdout
    except Exception as error:  # noqa: BLE001
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
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--name-only", base, "--"], check=True, capture_output=True, text=True).stdout
        staged = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--cached", "--name-only", base, "--"], check=True, capture_output=True, text=True).stdout
    except Exception as error:  # noqa: BLE001
        errors.append("git diff failed: " + str(error))
        return
    for line in (diff + staged).splitlines():
        if line and not line.startswith(reference.TASK_PREFIX):
            errors.append("committed change outside task scope: " + line)
    for cmd in (["git", "-C", str(SDK_ROOT), "diff", "--check"], ["git", "-C", str(SDK_ROOT), "diff", "--cached", "--check"]):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            errors.append("git diff --check failed: " + (result.stdout or result.stderr).strip())


def check_cold_start_regeneration(errors: list[str]) -> None:
    if not REPORT.is_file() or not CONTRACT.is_file():
        errors.append("cannot cold-start without committed artifacts")
        return
    with tempfile.TemporaryDirectory(prefix="td-psola-verify-") as tmp:
        root = Path(tmp)
        shutil.copy2(HERE / "reference.py", root / "reference.py")
        shutil.copy2(HERE / "run.py", root / "run.py")
        env = dict(os.environ)
        env["AUDIOML_ROOT"] = str(reference.AUDIO_ROOT)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        digests = []
        for _ in range(3):
            result = subprocess.run([sys.executable, str(root / "run.py"), "report.json"], cwd=str(root), env=env, capture_output=True, text=True)
            if result.returncode != 0:
                errors.append("cold-start run failed: " + (result.stderr or result.stdout).strip())
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
        if (root / "report.json.sha256").read_text(encoding="ascii") != SIDECAR.read_text(encoding="ascii"):
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
        print(f"FAIL verification ({len(errors)} errors)", file=sys.stderr)
        return 1
    print(
        "PASS verify.py version=%s contract_sha256=%s report_sha256=%s gates=%d blockers=%d artifacts=%d admission_cases=%d strict_json_cases=%d absence_probes=%d"
        % (
            platform.python_version(),
            reference.object_digest(contract),
            hashlib.sha256(REPORT.read_bytes()).hexdigest(),
            len(report.get("gates", [])),
            len(report.get("exact_blockers", [])),
            len(report.get("required_artifacts", [])),
            report.get("admission", {}).get("manifest_cases", 0),
            report.get("admission", {}).get("strict_json_cases", 0),
            len(report.get("absence_evidence", {}).get("probes", [])),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
