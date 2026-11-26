# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local PESQ/POLQA/3QUEST evidence package."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import reference

HERE = Path(__file__).resolve().parent


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class JsonAndCanonicalTests(unittest.TestCase):
    def test_canonical_rejects_nonfinite(self):
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"x": math.nan})

    def test_strict_rejects_duplicate(self):
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_rejects_non_object(self):
        with self.assertRaises(reference.Reject):
            reference.strict_loads('[1]')


class AuditAndIdentityTests(unittest.TestCase):
    def test_absence_probes_absent(self):
        audit = reference.audit_assets()
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertEqual(audit["audit_result"], "absent")

    def test_task_identity(self):
        ident = reference.task_row_identity()
        self.assertEqual(ident["stable_fields"]["id"], reference.TASK)
        self.assertEqual(ident["stable_fields"]["component"], reference.COMPONENT)
        self.assertFalse(ident["whole_file_hashed"])
        self.assertEqual(ident["claim"]["base_commit"], reference.BASE_COMMIT)

    def test_mutable_fields_excluded(self):
        ident = reference.task_row_identity()
        for f in reference.MUTABLE_TASK_FIELDS:
            self.assertNotIn(f, ident["stable_fields"])


class PcmTests(unittest.TestCase):
    def test_synthetic_control_is_valid(self):
        pcm = reference.synthetic_control_pcm()
        self.assertEqual(pcm["valid"]["channels"], 1)
        self.assertEqual(pcm["valid"]["sample_rate_hz"], 16000)
        self.assertGreater(pcm["valid"]["samples"], 0)

    def test_pcm_rejects_nonfinite(self):
        with self.assertRaises(reference.Reject):
            reference.validate_pcm([0.0, float('inf')], 16000, 1)

    def test_pcm_rejects_out_of_range(self):
        with self.assertRaises(reference.Reject):
            reference.validate_pcm([2.0], 16000, 1)


class AdverseTests(unittest.TestCase):
    def test_adverse_all_rejected(self):
        cases = reference.adverse_cases()
        self.assertGreaterEqual(len(cases), 10)
        self.assertTrue(all(c["result"] == "rejected" for c in cases))

    def test_caller_manifest_rejects_missing_file(self):
        bad = {k: ("/tmp/nope-pesq-polqa" if k.endswith('_path') else ('a'*40 if k=='source_revision' else ('0'*64 if k.endswith('_sha256') else ('pesq' if k=='scorer' else ('nb' if k=='mode' else 'offline_reference_comparison'))))) for k in reference.CALLER_MANIFEST_FIELDS}
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(bad)


class ReportContractTests(unittest.TestCase):
    def test_report_contract_shape(self):
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["profile"], "evidence")
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))
        self.assertEqual(len(report["exact_blockers"]), 8)

    def test_contract_shape(self):
        contract = reference.build_contract()
        self.assertEqual(contract["schema_id"], reference.CONTRACT_SCHEMA_ID)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(len(contract["gates"]), 8)
        self.assertFalse(contract["caller_manifest_contract"]["asset_is_vendored"])

    def test_canonical_bytes_stable(self):
        a = reference.canonical_report_bytes(reference.build_report())
        b = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(a, b)
        self.assertTrue(a.endswith(b"\n"))

    def test_report_does_not_hash_full_tasks_json(self):
        text = reference.canonical_report_bytes(reference.build_report()).decode('utf-8')
        self.assertNotRegex(text, r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"')


class SourcePinTests(unittest.TestCase):
    def test_source_pins_exist(self):
        for rel, expected in reference.SOURCE_PINS.items():
            p = reference.SOURCE_ROOT / rel
            self.assertTrue(p.is_file(), rel)
            self.assertEqual(sha(p.read_bytes()), expected, rel)

    def test_boundary_pins_exist(self):
        for rel, expected in reference.BOUNDARY_PINS.items():
            p = reference.SDK_ROOT / rel
            self.assertTrue(p.is_file(), rel)
            self.assertEqual(sha(p.read_bytes()), expected, rel)


if __name__ == "__main__":
    unittest.main()
