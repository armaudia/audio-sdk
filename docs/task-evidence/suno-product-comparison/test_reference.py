# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for SDK-SUNO-PRODUCT-COMPARISON blocker package.

No network, no Suno source/runtime/output, no real audio, no skips.
"""

from __future__ import annotations

import hashlib
import math
import sys
import unittest

sys.dont_write_bytecode = True

import reference  # noqa: E402

REPORT_CACHE = None

def report() -> dict:
    global REPORT_CACHE
    if REPORT_CACHE is None:
        REPORT_CACHE = reference.build_report()
    return REPORT_CACHE

class CanonicalJsonTests(unittest.TestCase):
    def test_canonical_sorted_and_newline(self):
        data = reference.canonical_bytes({"b": 1, "a": 2})
        self.assertTrue(data.endswith(b"\n"))
        self.assertLess(data.index(b'"a"'), data.index(b'"b"'))

    def test_strict_loads_accepts_object(self):
        self.assertEqual(reference.strict_loads('{"a": 1}'), {"a": 1})

    def test_strict_loads_rejects_duplicate(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": 1, "a": 2}')

    def test_strict_loads_rejects_nan(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": NaN}')

    def test_strict_loads_rejects_infinity(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": Infinity}')

    def test_strict_loads_rejects_non_object(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('[1, 2]')

    def test_strict_loads_rejects_trailing(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": 1} trailing')

    def test_negative_zero_detection(self):
        self.assertTrue(reference.has_negative_zero({"a": -0.0}))
        self.assertFalse(reference.has_negative_zero({"a": 0.0}))

class ComparisonSurrogateTests(unittest.TestCase):
    def test_digest_deterministic(self):
        ctrl = report()["controls"]["comparison_digest"]
        self.assertTrue(ctrl["byte_identical_digest"])
        self.assertRegex(ctrl["digest"], r"^[0-9a-f]{64}$")

    def test_record_validation(self):
        for rec in reference.COMPARISON_RECORDS:
            normalized = reference.validate_record(rec)
            self.assertEqual(set(normalized.keys()), reference.REQUIRED_RECORD_FIELDS)

    def test_record_adverse_rejected(self):
        ctrl = report()["controls"]["record_adverse"]
        self.assertTrue(ctrl["rejected_all"])
        self.assertGreaterEqual(len(ctrl["rejections"]), 8)

    def test_nonfinite_rejected(self):
        ctrl = report()["controls"]["nonfinite"]
        self.assertTrue(ctrl["rejected_all"])
        self.assertEqual(set(ctrl["rejections"].keys()), {"nan", "inf", "neginf"})

    def test_missing_artifacts_control(self):
        ctrl = report()["controls"]["missing_artifacts"]
        self.assertTrue(ctrl["all_absent"])
        self.assertTrue(ctrl["no_missing_result_qualifies"])
        self.assertGreaterEqual(len(ctrl["missing"]), 7)

class ReportTests(unittest.TestCase):
    def test_disposition(self):
        r = report()
        self.assertEqual(r["decision"], "DEFER")
        self.assertEqual(r["status"], "proposal_only_blocked_incomplete")
        self.assertEqual(r["evidence_status"], "incomplete")
        self.assertEqual(r["qualification_status"], "not_qualified")
        self.assertTrue(r["proposal_only"])
        self.assertEqual(r["qualification"]["status"], "not_qualified")
        self.assertTrue(r["qualification"]["not_qualified"])
        self.assertFalse(r["qualification"]["missing_result_promoted"])
        self.assertTrue(r["qualification"]["all_release_gates_blocked"])

    def test_board_row_not_full_hash(self):
        r = report()
        self.assertFalse(r["board_row"]["full_tasks_json_hashed"])
        self.assertEqual(r["board_row"]["stable_sha256"], reference.BOARD_ROW_STABLE_SHA256)
        self.assertEqual(reference.board_row_digest(), reference.BOARD_ROW_STABLE_SHA256)

    def test_gates_blocked(self):
        gates = report()["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in gates))
        self.assertTrue(all(g["qualifies"] is False for g in gates))

    def test_no_missing_result_qualifies(self):
        self.assertTrue(report()["no_missing_result_qualifies_candidate"])
        self.assertTrue(report()["missing_results"])

    def test_required_keys(self):
        self.assertEqual(set(report().keys()), reference.REQUIRED_REPORT_KEYS)
        self.assertEqual(set(reference.contract_payload().keys()), reference.REQUIRED_CONTRACT_KEYS)

    def test_deterministic(self):
        a = reference.canonical_report_bytes(reference.build_report())
        b = reference.canonical_report_bytes(reference.build_report())
        c = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(a, b)
        self.assertEqual(b, c)
        self.assertEqual(hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest())

    def test_contract_deterministic(self):
        self.assertEqual(reference.contract_bytes(), reference.contract_bytes())

    def test_scope_task_local(self):
        scope = report()["scope"]
        self.assertTrue(scope["task_local_only"])
        self.assertFalse(scope["provider_registered"])
        self.assertFalse(scope["network_used"])
        self.assertFalse(scope["release_claim"])

    def test_boundary_unchanged(self):
        boundary = report()["boundary"]
        for k, v in boundary.items():
            if k == "descriptor_settings":
                self.assertEqual(v, {})
            else:
                self.assertFalse(v)

    def test_upstream_not_admitted(self):
        up = report()["upstream"]
        self.assertFalse(up["admitted_source"])
        self.assertFalse(up["admitted_runtime"])
        self.assertEqual(up["evidence_kind"], "source_only_research_note")

if __name__ == "__main__":
    unittest.main()
