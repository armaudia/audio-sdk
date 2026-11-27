# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for SDK-VOSK blocker evidence."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import reference  # noqa: E402


def fail(msg: str) -> None:
    print("FAIL: " + msg)
    raise SystemExit(1)


def check_pins() -> None:
    for rel, expected in reference.SOURCE_PINS.items():
        p = reference.resolve_source(rel)
        if not p.is_file():
            fail("missing_source_pin:" + rel)
        got = reference.sha256_file(p)
        if got != expected:
            fail(f"source_pin_mismatch:{rel}:{got}")
    for rel, expected in reference.BOUNDARY_PINS.items():
        p = reference.resolve_worktree(rel)
        if not p.is_file():
            fail("missing_boundary_pin:" + rel)
        got = reference.sha256_file(p)
        if got != expected:
            fail(f"boundary_pin_mismatch:{rel}:{got}")


def check_profile() -> None:
    profile = reference.resolve_source("audio-benchmark-platform/plan/swarm/VERIFICATION.md").read_text(encoding="utf-8")
    for phrase in reference.RATE_PROFILE_PHRASES:
        if phrase not in profile:
            fail("profile_phrase_missing:" + phrase)


def check_json() -> tuple[dict, dict]:
    contract = reference.load_strict_json(HERE / "contract.json")
    report = reference.load_strict_json(HERE / "report.json")
    if contract != reference.build_contract():
        fail("contract_not_canonical_or_stale")
    if report != reference.build_report():
        fail("report_not_canonical_or_stale")
    if (HERE / "contract.json").read_bytes() != reference.canonical_bytes(contract):
        fail("contract_bytes_not_canonical")
    if (HERE / "report.json").read_bytes() != reference.canonical_bytes(report):
        fail("report_bytes_not_canonical")
    return contract, report


def check_report_digest(report: dict) -> str:
    expected = reference.report_digest(report)
    sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    if sidecar != expected + "  report.json":
        fail("report_sha256_mismatch")
    if report.get("report_sha256") != expected:
        fail("report_internal_sha256_mismatch")
    return expected


def check_sources() -> None:
    expected = reference.sources_manifest()
    got = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
    if got != expected:
        fail("sources_manifest_mismatch")
    for line in got.splitlines():
        if not line.strip():
            continue
        digest, name = line.split("  ", 1)
        if name.startswith("source:") or name.startswith("boundary:"):
            continue
        p = HERE / name
        if not p.is_file():
            fail("sources_missing_file:" + name)
        if reference.sha256_file(p) != digest:
            fail("sources_digest_mismatch:" + name)


def check_policy(contract: dict, report: dict) -> None:
    if contract.get("decision") != "DEFER" or report.get("decision") != "DEFER":
        fail("decision_not_defer")
    if contract.get("status") != "incomplete" or report.get("status") != "incomplete":
        fail("status_not_incomplete")
    cq = contract.get("qualification", {})
    rq = report.get("qualification", {})
    if cq.get("status") != "not_qualified" or rq.get("status") != "not_qualified":
        fail("qualification_not_not_qualified")
    if cq.get("qualified") is not False or rq.get("qualified") is not False:
        fail("qualification_claimed")
    gates = report.get("release_gates", [])
    if len(gates) != 8:
        fail("release_gate_count")
    for g in gates:
        if g.get("status") != "blocked" or g.get("qualifies") is not False:
            fail("release_gate_not_blocked:" + str(g.get("id")))
    blockers = report.get("exact_blockers", [])
    if len(blockers) != 6:
        fail("blocker_count")
    for b in blockers:
        if b.get("status") != "open" or b.get("qualifies") is not False:
            fail("blocker_not_open:" + str(b.get("id")))
    probes = report.get("absence_summary", {})
    if probes.get("all_absent") is not True:
        fail("absence_probe_present")
    if contract.get("linked_row_identity", {}).get("mutable_board_hash_used") is not False:
        fail("mutable_board_hash_used")
    if report.get("profile_requirements", {}).get("all_blocked") is not True:
        fail("rate_profile_not_blocked")


def check_scope() -> None:
    root = reference.WORKTREE
    base = reference.scope_base(root)
    if base is None:
        fail("scope_base_unavailable")
    try:
        changed = reference.scope_changed_paths(root, base)
    except Exception as e:
        fail("scope_diff_failed:" + str(e))
    violations = reference.scope_violations(changed)
    for path in violations:
        fail("base_out_of_scope_change:" + path)
    # staged/unstaged safety within worktree
    try:
        out = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True)
    except Exception as e:
        fail("git_status_failed:" + str(e))
    for line in out.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        if not path.startswith(reference.TASK_PREFIX):
            fail("out_of_scope_change:" + path)


def check_three_regens() -> None:
    import run  # noqa: E402

    before = (HERE / "report.json").read_bytes()
    for _ in range(3):
        run.main(["all"])
        after = (HERE / "report.json").read_bytes()
        if after != before:
            fail("regen_not_byte_identical")


def main() -> int:
    check_pins()
    check_profile()
    contract, report = check_json()
    digest = check_report_digest(report)
    check_sources()
    check_policy(contract, report)
    check_scope()
    check_three_regens()
    print(
        "PASS verify.py decision=DEFER status=incomplete qualification=not_qualified "
        f"gates=8 blockers=6 report_sha256={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
