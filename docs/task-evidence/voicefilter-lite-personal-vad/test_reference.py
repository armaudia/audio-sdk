# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the VoiceFilter-Lite/personal-VAD blocker package."""

from __future__ import annotations

import hashlib
import json
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


class ReferenceTests(unittest.TestCase):
    def test_report_contract_shape(self) -> None:
        report = reference.build_report()
        contract = reference.build_contract(report)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["profile"], "spatial")
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertTrue(report["qualification"]["no_missing_result_qualifies_candidate"])
        self.assertEqual(contract["schema_id"], "audio-sdk/task-evidence-contract/0.1")
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertEqual(contract["write_scope"], reference.TASK_PREFIX)

    def test_boundary_and_scope_flags(self) -> None:
        report = reference.build_report()
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "shared_build_or_ci_change", "installed_v0_behavior_change"):
            self.assertIs(report["boundary"][key], False, key)
        for key in ("real_audio", "real_corpus", "model_executed", "network_used",
                    "device_timing", "listening", "public_benchmark", "release_claim"):
            self.assertIs(report["scope"][key], False, key)
        self.assertTrue(report["scope"]["task_local_only"])

    def test_task_row_identity_not_whole_file(self) -> None:
        report = reference.build_report()
        ident = report["task_row_identity"]
        self.assertFalse(ident["whole_file_hashed"])
        self.assertEqual(ident["stable_sha256"], reference.TASK_ROW_STABLE_SHA256)
        self.assertEqual(set(ident["excluded_mutable_fields"]), set(reference.MUTABLE_TASK_FIELDS))
        encoded = reference.canonical_text(report)
        self.assertNotRegex(encoded, r'TASKS\\.json"\\s*:\\s*"[0-9a-f]{64}"')

    def test_adverse_controls_rejected(self) -> None:
        report = reference.build_report()
        adverse = report["controls"]["adverse"]
        self.assertGreaterEqual(len(adverse), 11)
        self.assertTrue(all(r["result"] == "rejected" for r in adverse))
        self.assertTrue(report["controls"]["adverse_all_rejected"])

    def test_synthetic_control_is_not_qualification(self) -> None:
        report = reference.build_report()
        proto = report["reference_protocol"]
        self.assertFalse(proto["model_executed"])
        self.assertEqual(proto["executor"], "absent")
        self.assertEqual(proto["qualification_effect"], "none")
        self.assertIsNone(report["candidate_metrics"])
        self.assertEqual(report["source_reported_context"]["label"], "source_reported_not_measured_here")

    def test_canonical_bytes_stable(self) -> None:
        r1 = reference.canonical_bytes(reference.build_report())
        r2 = reference.canonical_bytes(reference.build_report())
        self.assertEqual(r1, r2)
        self.assertTrue(r1.endswith(b"\n"))
        reference.strict_loads(r1.decode("utf-8"))

    def test_strict_json_rejects_duplicate_and_nonfinite(self) -> None:
        with self.assertRaises(Exception):
            reference.strict_loads('{"a":1,"a":2}')
        with self.assertRaises(Exception):
            reference.strict_loads('[NaN]')

    def test_run_regenerates_byte_identical_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
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


if __name__ == "__main__":
    unittest.main()
