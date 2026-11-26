# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for deterministic SpeechBrains ECAPA / speaker similarity evidence."""

from __future__ import annotations

import copy
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

TEMP_ROOT = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ReferenceTest(unittest.TestCase):
    def test_report_is_canonical_and_deterministic(self) -> None:
        a = run.report_bytes()
        b = run.report_bytes()
        self.assertEqual(a, b)
        report = reference.strict_loads(a.decode("utf-8"))
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["blocked"] for g in report["gates"]))
        self.assertFalse(report["synthetic_control"]["qualifies_candidate"])
        self.assertTrue(report["synthetic_control"]["not_speechbrain_ecapa"])

    def test_adverse_controls_rejected(self) -> None:
        cases = reference.run_adverse_controls()
        self.assertGreaterEqual(len(cases), 20)
        self.assertTrue(all(c["result"] == "rejected" for c in cases))

    def test_missing_or_invalid_inputs_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":NaN}')
        with self.assertRaises(reference.Reject):
            reference.validate_manifest({"bad": 1})
        bad = reference._base_manifest()
        bad["source_revision"] = "0" * 40
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(bad)
        with self.assertRaises(reference.Reject):
            reference.cosine_similarity([1.0, 0.0], [1.0])
        with self.assertRaises(reference.Reject):
            reference.cosine_similarity([0.0, 0.0], [1.0, 0.0])
        with self.assertRaises(reference.Reject):
            reference.frame_rms_dbfs([float("nan")] + [0.0] * 159)

    def test_candidate_metrics_are_null_and_not_derived(self) -> None:
        report = reference.build_report()
        cm = report["candidate_metrics"]
        self.assertFalse(cm["derived_from_synthetic_control"])
        for k, v in cm.items():
            if k == "derived_from_synthetic_control":
                continue
            self.assertFalse(v["measured"])
            self.assertIsNone(v["value"])

    def test_contract_and_sources_check(self) -> None:
        contract = run.build_contract()
        obj = reference.strict_loads(contract.decode("utf-8"))
        self.assertEqual(obj["decision"], "DEFER")
        self.assertEqual(obj["qualification_status"], "not_qualified")
        self.assertFalse(obj["qualification"]["candidate_qualified"])
        self.assertEqual(len(obj["release_gates"]), 8)
        self.assertNotIn(reference.BOARD_PATH, obj["source_pins"])
        sources = run.sources_bytes().decode("ascii")
        self.assertNotIn(reference.BOARD_PATH, sources)
        self.assertIn("local:report.json", sources)

    def test_cold_start_regeneration_three_times(self) -> None:
        base = TEMP_ROOT if TEMP_ROOT.exists() else Path(tempfile.gettempdir())
        digests = []
        for _ in range(3):
            with tempfile.TemporaryDirectory(prefix="speechbrain-ecapa-proxy-test-", dir=str(base)) as td:
                tmp = Path(td)
                for name in run.LOCAL_FILES:
                    (tmp / name).write_bytes((HERE / name).read_bytes())
                env = os.environ.copy()
                env["PYTHONDONTWRITEBYTECODE"] = "1"
                proc = subprocess.run([sys.executable, str(tmp / "run.py"), "all"], cwd=str(tmp), capture_output=True, text=True, env=env, check=False)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                digests.append(sha256((tmp / "report.json").read_bytes()))
                self.assertEqual((tmp / "report.json.sha256").read_bytes(), (sha256((tmp / "report.json").read_bytes()) + "  report.json\n").encode("ascii"))
        self.assertEqual(len(set(digests)), 1)

    def test_atomic_state_on_reject(self) -> None:
        er = reference.EvidenceReport()
        before = er.snapshot()
        with self.assertRaises(reference.Reject):
            er.build({"bad": float("nan")})
        self.assertEqual(er.snapshot(), before)
        report = er.build({})
        self.assertEqual(report["decision"], "DEFER")
        self.assertIsNotNone(er.snapshot())


if __name__ == "__main__":
    unittest.main()
