# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-RESEMBLE-ENHANCE-DENOISE-ONLY blocker evidence."""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = reference.build_contract()

    def test_report_is_canonical_and_repeatable(self) -> None:
        b1 = reference.canonical_report_bytes(self.report)
        b2 = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(b1, b2)
        self.assertEqual(self.report["repeatability"]["count"], 3)
        self.assertTrue(self.report["repeatability"]["byte_identical"])
        self.assertEqual(len(set(self.report["repeatability"]["digests"])), 1)

    def test_decision_and_qualification(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertFalse(self.report["qualification"]["qualified"])
        self.assertEqual(self.contract["qualification_status"], "not_qualified")

    def test_no_missing_result_qualifies(self) -> None:
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        self.assertTrue(self.contract["no_missing_result_qualifies_candidate"])

    def test_scope_and_negative_claims(self) -> None:
        for k, v in reference.SCOPE.items():
            self.assertEqual(self.report["scope"][k], v)
        for k, v in reference.NEGATIVE_CLAIMS.items():
            self.assertFalse(v)
            self.assertFalse(self.report["negative_claims"][k])

    def test_boundary_closed(self) -> None:
        for k, v in reference.BOUNDARY.items():
            self.assertEqual(self.report["boundary"][k], v, k)
        self.assertEqual(self.report["boundary"]["registered"], False)
        self.assertEqual(self.report["boundary"]["enabled_by_default"], False)

    def test_format_preserves_public_v0(self) -> None:
        fmt = self.report["format"]
        self.assertEqual(fmt["public_sample_rate_hz"], 16000)
        self.assertEqual(fmt["public_channels"], 1)
        self.assertEqual(fmt["public_sample_format"], "f32")
        self.assertEqual(fmt["public_frame_samples"], 160)
        self.assertTrue(fmt["public_v0_geometry_preserved"])

    def test_linked_row_identity_stable_and_not_full_tasks(self) -> None:
        ident = self.report["linked_row_identity"]
        self.assertIn("never hash mutable full plan/swarm/TASKS.json", ident["policy"])
        self.assertEqual(ident["projection_sha256"], reference.stable_linked_row_projection_sha256())
        self.assertEqual(ident["linked_rows_sha256"], reference.stable_linked_rows_sha256())
        self.assertEqual(ident["projection"]["id"], reference.TASK)

    def test_gates_blocked(self) -> None:
        self.assertEqual(len(self.report["gates"]), 8)
        for g in self.report["gates"]:
            self.assertEqual(g["status"], "blocked")
            self.assertFalse(g["qualifies"])
            self.assertTrue(g["reopen_condition"])

    def test_adverse_cases_all_rejected(self) -> None:
        adverse = self.report["adverse_cases"]
        self.assertTrue(adverse["all_rejected"])
        self.assertFalse(adverse["any_qualifying"])
        for name, case in adverse["cases"].items():
            self.assertEqual(case["status"], "rejected", name)

    def test_strict_json_rejections(self) -> None:
        r = reference.strict_rejection_examples()
        self.assertEqual(r["bad_json_rejected"], r["bad_json_total"])
        self.assertEqual(r["bad_pins_rejected"], r["bad_pins_total"])

    def test_pin_manifest_deterministic(self) -> None:
        b1 = reference.sources_bytes()
        b2 = reference.sources_bytes()
        self.assertEqual(b1, b2)
        pins = reference.parse_pin_lines(b1.decode("ascii"))
        self.assertEqual({n for _, n in pins}, reference.allowed_pin_keys())

    def test_source_and_boundary_pins_match(self) -> None:
        for rel, digest in reference.SOURCE_PINS.items():
            p = reference.SOURCE_ROOT / rel
            self.assertTrue(p.is_file(), rel)
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), digest, rel)
        for rel, digest in reference.BOUNDARY_PINS.items():
            p = SDK_ROOT / rel
            self.assertTrue(p.is_file(), rel)
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), digest, rel)

    def test_no_spdx_token_literal(self) -> None:
        token = "SPDX-License-" + "Identifier:"
        for py in HERE.glob("*.py"):
            for line in py.read_text(encoding="utf-8").splitlines():
                if line.lstrip().startswith("#"):
                    continue
                self.assertNotIn(token, line, py.name)

    def test_contract_bytes_deterministic(self) -> None:
        self.assertEqual(reference.contract_bytes(), reference.contract_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
