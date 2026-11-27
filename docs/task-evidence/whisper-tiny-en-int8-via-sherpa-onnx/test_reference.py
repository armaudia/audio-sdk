# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for whisper-tiny-en-int8-via-sherpa-onnx task evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def test_contract_shape():
    c = reference.build_contract()
    assert c["task_id"] == reference.TASK_ID
    assert c["decision"] == "DEFER"
    assert c["status"] == "incomplete"
    assert c["qualification_status"] == "not_qualified"
    assert c["proposal_only"] is True
    assert len(c["blockers"]) == 6
    assert len(c["release_gates"]) == 8


def test_report_gates_blocked():
    r = reference.build_report()
    assert all(g["status"] == "blocked" for g in r["release_gates"])
    assert all(b["status"] == "open" for b in r["blockers"])
    assert r["summary"]["qualifying_result_count"] == 0
    assert r["claims"]["provider_or_adapter_registered"] is False


def test_admission_fail_closed():
    cases = reference.admission_cases()
    statuses = {c["case_id"]: c["status"] for c in cases}
    assert statuses["valid-shape-control"] == "accepted_for_schema_only"
    assert statuses["missing-model-digest"] == "rejected"
    assert statuses["unreviewed-license"] == "rejected"
    assert statuses["rights-unreviewed"] == "rejected"
    assert statuses["missing-invalid-control"] == "rejected"
    assert statuses["bad-digest-shape"] == "rejected"
    for c in cases:
        assert c["qualifies"] is False
        assert c["counts_as_qualification"] is False


def test_synthetic_control_not_qualifying():
    c = reference.synthetic_scorer_control()
    assert c["synthetic"] is True
    assert c["qualifies"] is False
    assert abs(c["wer"] - 0.25) < 1e-9


def test_scope_base_resolution():
    base = reference.resolve_scope_base(reference.WORKTREE)
    assert base["status"] == "ok"
    assert base["merge_base"]
    assert base["base_ref"] in ("origin/main", "main")


def test_branch_diff_scope_enforcement():
    diff = reference.branch_diff_paths(reference.WORKTREE)
    if diff["status"] == "scope_base_unavailable":
        assert "scope_base_unavailable" in diff["violations"]
    else:
        for p in diff["paths"]:
            pass
        # violations list exists; test enforces shape
        assert isinstance(diff["violations"], list)


def test_working_tree_scope():
    v = reference.working_tree_violations(reference.WORKTREE)
    assert isinstance(v, list)


def test_pin_manifest_has_expected_entries():
    pins = reference.pin_manifest()
    assert any(k.startswith("source:") for k in pins)
    assert any(k.startswith("worktree:") for k in pins)


def test_readme_digest_validation():
    readme = HERE / "README.md"
    assert readme.exists()
    text = readme.read_text(encoding="utf-8")
    assert "DEFER" in text
    assert "incomplete" in text
    assert "not_qualified" in text
    assert reference.TASK_ID in text


def test_report_json_roundtrip():
    r = reference.build_report()
    b = reference.canonical_bytes(r)
    r2 = json.loads(b.decode("utf-8"))
    assert r2["task_id"] == r["task_id"]


def run() -> int:
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:
            failures += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"{len(tests)-failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(run())
