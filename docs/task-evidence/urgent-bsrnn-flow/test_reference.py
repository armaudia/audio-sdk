# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for SDK-URGENT-BSRNN-FLOW blocker evidence."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import reference  # noqa: E402


def test_contract_canonical_and_policy() -> None:
    c = reference.build_contract()
    assert c["schema"] == reference.CONTRACT_ID
    assert c["task"] == reference.TASK
    assert c["decision"] == "DEFER"
    assert c["status"] == "incomplete"
    assert c["proposal_only"] is True
    assert c["incomplete"] is True
    assert c["qualification"] == {"status": "not_qualified", "qualified": False, "not_qualified": True}
    assert c["linked_row_identity"]["mutable_board_hash_used"] is False
    assert len(c["release_gates"]) == 8
    assert all(g["status"] == "blocked" and g["qualifies"] is False for g in c["release_gates"])
    b = reference.canonical_bytes(c)
    assert b.endswith(b"\n")
    assert json.loads(b.decode("utf-8")) == c


def test_report_canonical_and_policy() -> None:
    r = reference.build_report()
    assert r["schema"] == reference.REPORT_SCHEMA
    assert r["decision"] == "DEFER"
    assert r["status"] == "incomplete"
    assert r["qualification"]["status"] == "not_qualified"
    assert r["qualification"]["qualified"] is False
    assert r["qualification"]["not_qualified"] is True
    assert r["evidence"]["measured_result_present"] is False
    assert r["evidence"]["runtime_present"] is False
    assert r["evidence"]["weights_present"] is False
    assert r["evidence"]["real_corpus_present"] is False
    assert r["evidence"]["device_timing_present"] is False
    assert r["evidence"]["listening_present"] is False
    assert r["absence_summary"]["all_absent"] is True
    assert len(r["blockers"]) == 6
    assert reference.report_digest(r) == hashlib.sha256(reference.canonical_bytes(r)).hexdigest()


def test_strict_json_rejects_invalid() -> None:
    import pytest

    bad = [
        '{"a":1, "a":2}',
        "[1, NaN]",
        "[1.5]",
        "\ufeff{}",
        "{} trailing",
    ]
    for s in bad:
        try:
            reference.loads_strict(s)
        except reference.ReferenceError:
            continue
        raise AssertionError("accepted invalid: " + s)


def test_absence_probes_shape() -> None:
    probes = reference.absence_probes()
    assert len(probes) >= 18
    for p in probes:
        assert set(p.keys()) == {"path", "root", "exists"}
        assert isinstance(p["exists"], bool)
        assert p["root"] in {"audio_root", "worktree", "home"}


def test_source_and_boundary_pins_match() -> None:
    for rel, expected in reference.PLAN_PINS.items():
        p = reference.resolve_source(rel)
        assert p.is_file(), rel
        assert reference.sha256_file(p) == expected
    for rel, expected in reference.BOUNDARY_PINS.items():
        p = reference.resolve_worktree(rel)
        assert p.is_file(), rel
        assert reference.sha256_file(p) == expected


def test_stable_row_identity() -> None:
    row = reference.linked_row_projection()
    assert row["id"] == reference.TASK
    assert row["component"] == reference.COMPONENT
    assert "status" not in row
    assert "owner" not in row
    c = reference.build_contract()
    ident = c["linked_row_identity"]
    assert ident["mutable_board_hash_used"] is False
    assert ident["projection"] == row
    assert ident["projection_sha256"] == reference.sha256_bytes(reference.canonical_bytes(row).rstrip(b"\n"))


def test_run_three_regens_byte_identical(tmp_path: Path) -> None:
    # run in-place; verify idempotent
    env = os.environ.copy()
    cmd = [sys.executable, str(HERE / "run.py"), "all"]
    r1 = subprocess.run(cmd, cwd=str(HERE), capture_output=True, text=True, env=env, check=True)
    b1 = (HERE / "report.json").read_bytes()
    r2 = subprocess.run(cmd, cwd=str(HERE), capture_output=True, text=True, env=env, check=True)
    b2 = (HERE / "report.json").read_bytes()
    assert b1 == b2
    assert "repeat=3" in r1.stdout
    assert "repeat=3" in r2.stdout


def test_verify_passes() -> None:
    env = os.environ.copy()
    cmd = [sys.executable, str(HERE / "verify.py")]
    r = subprocess.run(cmd, cwd=str(HERE), capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS verify.py" in r.stdout
    assert "qualification=not_qualified" in r.stdout
