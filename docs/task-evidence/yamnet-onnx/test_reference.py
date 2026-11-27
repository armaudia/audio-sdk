# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the YAMNet ONNX blocker package."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def _commit(repo: Path, rel: str, content: str, msg: str) -> str:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    _git(repo, "add", rel)
    _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD")


class ReferenceTests(unittest.TestCase):
    def test_report_contract_shape(self) -> None:
        report = reference.build_report()
        contract = reference.build_contract(report)
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["profile"], "rate")
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertTrue(report["qualification"]["no_missing_result_qualifies_candidate"])
        self.assertEqual(contract["schema_id"], "audio-sdk/task-evidence-contract/0.1")
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["write_scope"], reference.TASK_PREFIX)

    def test_boundary_scope_flags(self) -> None:
        report = reference.build_report()
        for k in ("registered", "enabled_by_default", "default_selected", "public_api_abi_change", "provider_registration", "shared_build_or_ci_change", "installed_v0_behavior_change", "asset_bundled", "weights_vendored", "network_used"):
            self.assertIs(report["boundary"][k], False, k)
        for k in ("real_audio", "real_corpus", "model_executed", "network_used", "device_timing", "listening", "public_benchmark", "release_claim"):
            self.assertIs(report["scope"][k], False, k)
        self.assertTrue(report["scope"]["task_local_only"])

    def test_task_row_identity_not_whole_file(self) -> None:
        report = reference.build_report()
        ident = report["task_row_identity"]
        self.assertFalse(ident["whole_file_hashed"])
        self.assertEqual(ident["stable_sha256"], reference.TASK_ROW_STABLE_SHA256)
        self.assertEqual(set(ident["excluded_mutable_fields"]), set(reference.MUTABLE_TASK_FIELDS))
        encoded = reference.canonical_text(report)
        self.assertNotRegex(encoded, r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"')

    def test_adverse_controls_rejected(self) -> None:
        report = reference.build_report()
        adverse = report["controls"]["adverse"]
        self.assertGreaterEqual(len(adverse), 11)
        self.assertTrue(all(r["result"] == "rejected" for r in adverse))
        self.assertTrue(report["controls"]["adverse_all_rejected"])

    def test_synthetic_control_not_qualification(self) -> None:
        report = reference.build_report()
        self.assertFalse(report["reference_protocol"]["model_executed"])
        self.assertEqual(report["reference_protocol"]["executor"], "absent")
        self.assertEqual(report["reference_protocol"]["qualification_effect"], "none")
        self.assertIsNone(report["candidate_metrics"])
        self.assertEqual(report["source_reported_context"]["label"], "source_reported_not_measured_here")
        self.assertEqual(report["advisory_label_cadence_contract"]["qualification_effect"], "none")

    def test_canonical_bytes_stable(self) -> None:
        r1 = reference.canonical_bytes(reference.build_report())
        r2 = reference.canonical_bytes(reference.build_report())
        self.assertEqual(r1, r2)
        self.assertTrue(r1.endswith(b"\n"))
        reference.strict_loads(r1.decode("utf-8"))

    def test_strict_json_rejects_duplicate_nonfinite_bom_trailing(self) -> None:
        with self.assertRaises(Exception):
            reference.strict_loads('{"a":1,"a":2}')
        with self.assertRaises(Exception):
            reference.strict_loads('[NaN]')
        with self.assertRaises(Exception):
            reference.strict_loads('\ufeff{"a":1}')
        with self.assertRaises(Exception):
            reference.strict_loads('{"a":1}x')

    def test_run_regenerates_byte_identical_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
            cmd = [sys.executable, str(HERE / "run.py"), "--out", str(out)]
            s1 = subprocess.run(cmd, cwd=str(HERE), env=env, capture_output=True, text=True)
            self.assertEqual(s1.returncode, 0, s1.stdout + s1.stderr)
            b1 = (out / "report.json").read_bytes()
            s2 = subprocess.run(cmd, cwd=str(HERE), env=env, capture_output=True, text=True)
            self.assertEqual(s2.returncode, 0, s2.stdout + s2.stderr)
            b2 = (out / "report.json").read_bytes()
            self.assertEqual(b1, b2)
            sidecar = (out / "report.json.sha256").read_text(encoding="utf-8")
            self.assertEqual(sidecar.strip(), f"{sha256(b1)}  report.json")


class ScopeBaseTests(unittest.TestCase):
    def _repo(self, path: Path) -> None:
        _git(path, "init", "-q", "-b", "main")
        _git(path, "config", "user.email", "test@example.invalid")
        _git(path, "config", "user.name", "Test User")
        _commit(path, "seed.txt", "seed\n", "seed")

    def test_newest_merge_base_preferred(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self._repo(repo)
            base_a = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "-q", "-b", "base-b")
            base_b = _commit(repo, "base-b.txt", "b\n", "newer")
            _git(repo, "update-ref", "refs/remotes/origin/main", base_b)
            _git(repo, "branch", "-f", "main", base_a)
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task")
            self.assertEqual(reference.scope_base(repo, ("origin/main", "main")), base_b)
            changed = reference.scope_changed_paths(repo, base_b)
            self.assertEqual(reference.scope_violations(changed), [])

    def test_origin_missing_falls_back_to_main(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self._repo(repo)
            base = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "-q", "-b", "feature")
            _commit(repo, reference.TASK_PREFIX + "report.json", "{}\n", "task")
            self.assertEqual(reference.scope_base(repo, ("origin/main", "main")), base)

    def test_no_base_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self._repo(repo)
            self.assertIsNone(reference.scope_base(repo, ("missing-a", "missing-b")))


if __name__ == "__main__":
    unittest.main()
