# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification for the rate-controlled HiFi-GAN speech TSM package."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, List

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402

SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SIDECAR = f"{SPDX_C}\n{SPDX_L}\n"
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
EXPECTED_GATES = {
    "exact_asset_identity",
    "runtime_admission",
    "artifact_rights",
    "exact_reference_parity",
    "rights_cleared_rate_cohort",
    "independent_scoring_and_listening",
    "target_runtime_timing",
    "provider_intake_and_default_selection",
}
FORBIDDEN_SOURCE_TOKENS = ("import " + "requests", "import " + "urllib", "import " + "socket", "url" + "open", "pip " + "install")
REQUIRED_README_PHRASES = ("DEFER", "not_qualified", "incomplete", "eight", "caller-supplied", "no candidate", "blocked")
BOARD_RELATIVE = "audio-benchmark-platform/plan/swarm/TASKS.json"


def _no_duplicates(pairs):
    seen = set()
    for k, _ in pairs:
        if k in seen:
            raise ValueError("duplicate JSON key: " + k)
        seen.add(k)
    return dict(pairs)


def _reject_constant(token: str):
    raise ValueError("nonfinite JSON constant: " + token)


def load_strict(path: Path) -> Any:
    text = path.read_text(encoding="ascii")
    value = json.loads(text, object_pairs_hook=_no_duplicates, parse_constant=_reject_constant)
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise ValueError("JSON file must end with exactly one newline: " + path.name)
    return value


def load_board(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text, object_pairs_hook=_no_duplicates, parse_constant=_reject_constant)


def check() -> List[str]:
    problems: List[str] = []

    def fail(msg: str) -> None:
        problems.append(msg)

    expected_files = set(reference.LOCAL_FILES)
    present = {p.relative_to(HERE).as_posix() for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    for name in sorted(expected_files - present):
        fail("expected file missing: " + name)
    for name in sorted(present - expected_files):
        fail("file outside fail-closed local set: " + name)
    for p in HERE.rglob("*"):
        if "__pycache__" in p.parts:
            fail("bytecode cache present: " + p.relative_to(HERE).as_posix())

    report = {}
    contract = {}
    try:
        report = load_strict(HERE / "report.json")
    except Exception as exc:
        fail(f"report.json invalid: {exc}")
    try:
        contract = load_strict(HERE / "contract.json")
    except Exception as exc:
        fail(f"contract.json invalid: {exc}")

    if report:
        if report.get("schema_id") != reference.SCHEMA_ID:
            fail("report schema_id drift")
        if report.get("task") != reference.TASK or report.get("component") != reference.SLUG:
            fail("report task/component drift")
        if report.get("mode") != "feasibility":
            fail("report mode drift")
        if report.get("profile") != "rate":
            fail("report profile drift")
        if report.get("decision") != "DEFER":
            fail("decision is not DEFER")
        if report.get("status") != "proposal_only_incomplete":
            fail("status not proposal_only_incomplete")
        if report.get("evidence_status") != "incomplete":
            fail("evidence_status not incomplete")
        if report.get("qualification_status") != "not_qualified":
            fail("qualification_status not not_qualified")
        gates = report.get("release_gates", [])
        if len(gates) != 8 or report.get("release_gate_count") != 8 or report.get("release_gates_blocked") != 8:
            fail("release gate count/drift")
        if {g.get("name") for g in gates} != EXPECTED_GATES:
            fail("release gate names drift")
        for g in gates:
            if g.get("status") != "blocked":
                fail("gate not blocked: " + str(g.get("name")))
            if not g.get("evidence") or not g.get("reopen"):
                fail("gate missing evidence/reopen: " + str(g.get("name")))
        for k, v in report.get("claims", {}).items():
            if v is not False:
                fail("claim promoted: " + k)
        for k, v in report.get("boundary", {}).items():
            if k == "installed_v0_geometry_preserved":
                if v is not True:
                    fail("installed_v0_geometry_preserved drift")
            elif v is not False:
                fail("boundary promoted: " + k)
        asset = report.get("asset", {})
        if asset.get("byte_count") is not None or asset.get("sha256") is not None:
            fail("unpinned asset got identity")
        if asset.get("pinned") is not False or asset.get("asset_bytes_read") is not False:
            fail("asset read/pinned drift")
        if any(asset.get("workspace_probes", {}).values()):
            fail("fixed probe unexpectedly present")
        if report.get("absence_audit", {}).get("all_absence_probes_absent") is not True:
            fail("absence audit not all absent")
        adm = report.get("asset_admission", {})
        if adm.get("status") != "blocked" or adm.get("qualification_effect") != "none":
            fail("asset admission drift")
        syn = report.get("synthetic_admission_control", {})
        if syn.get("status") != "admitted_synthetic_control" or syn.get("candidate_asset") is not False:
            fail("synthetic admission drift")

    if contract:
        if contract.get("schema_id") != reference.CONTRACT_SCHEMA_ID:
            fail("contract schema_id drift")
        if contract.get("decision") != "DEFER" or contract.get("qualified") is not False:
            fail("contract decision/qualified drift")
        if contract.get("status") != "proposal_only_incomplete" or contract.get("evidence_status") != "incomplete":
            fail("contract status drift")
        if contract.get("qualification_status") != "not_qualified":
            fail("contract qualification drift")
        gates = contract.get("release_gates", [])
        if len(gates) != 8 or {g.get("name") for g in gates} != EXPECTED_GATES or any(g.get("status") != "blocked" for g in gates):
            fail("contract gates drift")
        board = contract.get("board_policy", {})
        if board.get("full_file_hashed") is not False or board.get("stable_fields_only") is not True:
            fail("board policy drift")
        if contract.get("artifact_pins") != cli.contract_pins():
            fail("contract artifact pins stale")
        if "contract.json" in contract.get("artifact_pins", {}):
            fail("contract pins itself")
        expected_pins = set(reference.LOCAL_FILES) - {"contract.json", "SOURCES.sha256"}
        if set(contract.get("artifact_pins", {})) != expected_pins:
            fail("contract artifact pin set drift")

    for name, digest in reference.SOURCE_PINS.items():
        path = reference.SOURCE_ROOT / name
        if not path.is_file():
            fail("source pin missing: " + name)
        elif reference.sha256_file(path) != digest:
            fail("source pin stale: " + name)
    for name, digest in {**reference.BOUNDARY_PINS, **reference.SIBLING_PINS}.items():
        path = reference.SDK_ROOT / name
        if not path.is_file():
            fail("boundary/sibling pin missing: " + name)
        elif reference.sha256_file(path) != digest:
            fail("boundary/sibling pin stale: " + name)

    board_path = reference.SOURCE_ROOT / BOARD_RELATIVE
    if not board_path.is_file():
        fail("task board unavailable for stable linked-row identity check")
    else:
        try:
            board = load_board(board_path)
            rows = [r for r in board.get("tasks", []) if isinstance(r, dict) and r.get("id") == reference.TASK]
            if len(rows) != 1:
                fail("task board does not contain exactly one linked row")
            else:
                projected = reference.project_board_row(rows[0])
                expected = {k: reference.STABLE_TASK_IDENTITY[k] for k in reference.PROJECTED_BOARD_FIELDS}
                if {k: projected.get(k) for k in reference.PROJECTED_BOARD_FIELDS} != expected:
                    fail("live board stable linked-row projection drifted")
        except Exception as exc:
            fail(f"stable board projection failed: {exc}")

    if report:
        if cli.report_bytes() != (HERE / "report.json").read_bytes():
            fail("report.json is not deterministic regeneration")
        digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        if sidecar != f"{digest}  report.json\n":
            fail("report.json.sha256 stale")
    if contract:
        if cli.contract_bytes(cli.contract_pins()) != (HERE / "contract.json").read_bytes():
            fail("contract.json is not deterministic regeneration")
    try:
        if cli.manifest_bytes() != (HERE / "SOURCES.sha256").read_bytes():
            fail("SOURCES.sha256 stale")
    except Exception as exc:
        fail(f"manifest regeneration failed: {exc}")

    try:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        low = text.lower()
        for phrase in REQUIRED_README_PHRASES:
            if phrase.lower() not in low:
                fail("README missing required phrase: " + phrase)
        block = text.split("<!-- DIGEST_TABLE_START -->", 1)[1].split("<!-- DIGEST_TABLE_END -->", 1)[0]
        for name in cli.TABLE_FILES:
            payload = (HERE / name).read_bytes()
            row = f"| `{name}` | `{hashlib.sha256(payload).hexdigest()}` | {len(payload)} |"
            if row not in block:
                fail("README digest table stale for " + name)
    except Exception as exc:
        fail(f"README digest table invalid: {exc}")

    for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
        head = (HERE / name).read_text(encoding="utf-8").splitlines()[:2]
        if head != ["# " + SPDX_C, "# " + SPDX_L]:
            fail("missing explicit Python SPDX header: " + name)
        text = (HERE / name).read_text(encoding="utf-8")
        for tok in FORBIDDEN_SOURCE_TOKENS:
            if tok in text:
                fail(f"forbidden token in {name}: {tok}")
    mdhead = (HERE / "README.md").read_text(encoding="utf-8").splitlines()[:2]
    if mdhead != ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"]:
        fail("missing explicit Markdown SPDX header: README.md")
    for name in SIDECAR_FILES:
        if (HERE / name).read_text(encoding="utf-8") != SIDECAR:
            fail("invalid sidecar: " + name)
    reuse = reference.SDK_ROOT / "REUSE.toml"
    if not reuse.is_file() or '"docs/**"' not in reuse.read_text(encoding="utf-8"):
        fail("REUSE.toml docs/** annotation missing")
    if not (reference.SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        fail("LICENSES/Apache-2.0.txt missing")

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    before = {name: reference.sha256_file(HERE / name) for name in expected_files}
    digests = []
    for _ in range(3):
        result = subprocess.run([sys.executable, str(HERE / "run.py"), "--digest"], cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            fail("cold-start digest run failed: " + result.stderr.strip())
            break
        digests.append(result.stdout.strip())
    if digests and len(set(digests)) != 1:
        fail("three cold-start regeneration digests differ")
    if digests and digests[0] != (HERE / "report.json.sha256").read_text(encoding="ascii").split()[0]:
        fail("cold-start digest does not match report.json.sha256")
    after = {name: reference.sha256_file(HERE / name) for name in expected_files}
    if before != after:
        fail("read-only verification mutated evidence files")

    try:
        git = subprocess.run(["git", "-C", str(reference.SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"], capture_output=True, text=True, check=False)
        if git.returncode != 0:
            fail("git status unavailable: " + git.stderr.strip())
        else:
            for line in git.stdout.splitlines():
                if not line:
                    continue
                raw = line[3:] if len(line) > 3 else line
                if " -> " in raw:
                    raw = raw.split(" -> ", 1)[1]
                if "__pycache__" in raw or raw.startswith("build/"):
                    continue
                if not raw.startswith(reference.TASK_PREFIX):
                    fail("change outside task evidence directory: " + raw)
    except FileNotFoundError:
        fail("git executable unavailable for scope verification")

    return problems


def main() -> int:
    problems = check()
    if problems:
        print("FAIL")
        for p in problems:
            print(" - " + p)
        return 1
    report = load_strict(HERE / "report.json")
    digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
    print("PASS")
    print("decision=" + report["decision"])
    print("status=" + report["status"])
    print("evidence_status=" + report["evidence_status"])
    print("qualification.status=" + report["qualification_status"])
    print("release_gates=8 blocked=8")
    print("report_sha256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
