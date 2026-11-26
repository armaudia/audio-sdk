# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-VOICEFIXER blocker evidence."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import reference  # noqa: E402


class VoiceFixerBlockerTest(unittest.TestCase):
    def test_decision_and_qualification(self) -> None:
        report = reference.build_report()
        contract = reference.build_contract()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["qualified"])
        self.assertTrue(report["qualification"]["not_qualified"])
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification"]["status"], "not_qualified")

    def test_release_gates_blocked(self) -> None:
        gates = reference.build_report()["release_gates"]
        self.assertEqual(len(gates), 8)
        for g in gates:
            self.assertEqual(g["status"], "blocked")
            self.assertFalse(g["qualifies"])

    def test_restoration_profile_blocked(self) -> None:
        reqs = reference.build_report()["restoration_profile_requirements"]
        self.assertEqual(len(reqs), 6)
        for r in reqs:
            self.assertEqual(r["status"], "blocked")

    def test_absence_probes_absent(self) -> None:
        probes = reference.absence_probes()
        self.assertGreaterEqual(len(probes), 15)
        self.assertTrue(all(not p["exists"] for p in probes))

    def test_linked_row_identity_stable(self) -> None:
        ident = reference.linked_row_identity()
        self.assertFalse(ident["mutable_board_hash_used"])
        self.assertEqual(ident["task"], "SDK-VOICEFIXER")
        self.assertIn("id", ident["stable_fields"])
        self.assertIn("projection_sha256", ident)
        self.assertEqual(set(ident["dependency_rows"].keys()), {"SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"})

    def test_strict_json_rejects_nonfinite_and_duplicate(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.loads_strict('{"a":NaN}')
        with self.assertRaises(reference.ReferenceError):
            reference.loads_strict('{"a":1,"a":2}')
        with self.assertRaises(reference.ReferenceError):
            reference.loads_strict('[1.5]')

    def test_canonical_bytes_stable(self) -> None:
        obj = {"b": 1, "a": [2, 3]}
        b1 = reference.canonical_bytes(obj)
        b2 = reference.canonical_bytes({"a": [2, 3], "b": 1})
        self.assertEqual(b1, b2)
        self.assertTrue(b1.endswith(b"\n"))

    def test_report_digest_stable(self) -> None:
        r1 = reference.build_report()
        r2 = reference.build_report()
        self.assertEqual(reference.report_digest(r1), reference.report_digest(r2))

    def test_missing_invalid_adverse_do_not_qualify(self) -> None:
        report = reference.build_report()
        self.assertFalse(report["evidence"]["measured_result_present"])
        self.assertTrue(report["qualification"]["not_qualified"])
        self.assertFalse(report["qualification"]["qualified"])
        for g in report["release_gates"]:
            self.assertFalse(g["qualifies"])

    def test_source_pins_match(self) -> None:
        pins = reference.actual_source_pins()
        for rel, expected in reference.PLAN_PINS.items():
            self.assertEqual(pins[rel], expected)
        for rel, expected in reference.BOUNDARY_PINS.items():
            self.assertEqual(reference.actual_boundary_pins()[rel], expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
