# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for SDK-TD-PSOLA evidence package."""

from __future__ import annotations

import copy
import hashlib
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_rejects_invalid_json(self) -> None:
        for row in reference.strict_json_rejections()["rejections"]:
            self.assertTrue(row["rejected"], row)

    def test_canonical_roundtrip(self) -> None:
        doc = {"b": [1, True, None], "a": {"z": "x"}}
        payload = reference.canonical_bytes(doc)
        self.assertEqual(payload, b'{"a":{"z":"x"},"b":[1,true,null]}')
        self.assertEqual(reference.object_digest(doc), hashlib.sha256(payload).hexdigest())

    def test_no_floats(self) -> None:
        with self.assertRaises(TypeError):
            reference.assert_no_float({"x": 1.5})


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins(self) -> None:
        for rel, expected in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / rel
            self.assertTrue(path.is_file(), rel)
            self.assertEqual(reference.sha256_file(path), expected, rel)

    def test_boundary_pins(self) -> None:
        for rel, expected in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / rel
            self.assertTrue(path.is_file(), rel)
            self.assertEqual(reference.sha256_file(path), expected, rel)

    def test_snippets_present(self) -> None:
        result = reference.evidence_snippet_check()
        self.assertTrue(result["all_present"], result["checks"])
        self.assertEqual(result["count"], 7)

    def test_linked_row_identity_only(self) -> None:
        boundary = reference.boundary_block()
        self.assertFalse(boundary["board_file_pinned"])
        self.assertTrue(boundary["linked_row_identity_only"])
        self.assertFalse(boundary["mutable_board_fields_gate"])
        self.assertNotIn("status", boundary["linked_row"])
        self.assertEqual(boundary["linked_row"]["id"], reference.TASK)
        self.assertEqual(boundary["linked_row_sha256"], reference.board_row_digest(boundary["linked_row"]))
        self.assertEqual(boundary["linked_rows_sha256"], reference.linked_rows_digest(boundary["linked_rows"]))
        self.assertEqual(len(boundary["linked_rows"]), 4)


class AbsenceAndAdmissionTests(unittest.TestCase):
    def test_absence_all_absent(self) -> None:
        summary = reference.absence_summary()
        self.assertTrue(summary["all_absent"])
        self.assertEqual(summary["present_count"], 0)
        self.assertEqual(summary["probe_count"], 17)

    def test_accepted_declaration(self) -> None:
        doc = reference.validate_declaration(reference.accepted_declaration())
        self.assertEqual(doc["disposition"]["decision"], "DEFER")
        self.assertFalse(doc["disposition"]["qualifies"])

    def test_rejections(self) -> None:
        result = reference.declaration_rejections()
        self.assertEqual(result["rejection_cases"], 41)
        self.assertTrue(result["all_rejected"], result["rejections"])

    def test_rejection_does_not_mutate_valid(self) -> None:
        base = reference.accepted_declaration()
        before = copy.deepcopy(base)
        bad = copy.deepcopy(base)
        bad["disposition"]["qualifies"] = True
        with self.assertRaises(reference.AdmissionError):
            reference.validate_declaration(bad)
        self.assertEqual(reference.validate_declaration(before), before)


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_state(self) -> None:
        c = self.contract
        self.assertEqual(c["decision"], "DEFER")
        self.assertEqual(c["status"], "incomplete")
        self.assertEqual(c["qualification_status"], "not_qualified")
        self.assertTrue(c["proposal_only"])
        self.assertEqual(c["profile"], "rate")
        self.assertEqual(len(c["release_gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in c["release_gates"]))
        self.assertEqual(len(c["exact_blockers"]), 5)
        self.assertEqual(len(c["required_artifacts"]), 7)

    def test_report_state(self) -> None:
        r = self.report
        self.assertEqual(r["decision"], "DEFER")
        self.assertEqual(r["status"], "incomplete")
        self.assertEqual(r["qualification_status"], "not_qualified")
        self.assertTrue(r["proposal_only"])
        self.assertTrue(r["incomplete"])
        self.assertEqual(r["contract_sha256"], reference.object_digest(self.contract))
        self.assertEqual([g["id"] for g in r["gates"]], [f"RG-{i:02d}" for i in range(1, 9)])
        self.assertTrue(r["qualification"]["not_qualified"])
        self.assertTrue(r["qualification"]["all_release_gates_blocked"])
        for k, v in r["qualification"].items():
            if k in ("status", "readiness", "not_qualified", "all_release_gates_blocked", "reason"):
                continue
            self.assertIs(v, False, k)

    def test_rate_profile(self) -> None:
        rp = self.report["rate_profile"]
        self.assertEqual(rp["profile"], "rate")
        self.assertFalse(rp["profile_satisfied"])
        self.assertEqual(rp["real_results"], 0)
        self.assertEqual(len(rp["requirement_rows"]), 13)
        self.assertFalse(any(row["qualifies"] for row in rp["requirement_rows"]))

    def test_scope(self) -> None:
        s = self.report["scope"]
        self.assertTrue(s["task_local_only"])
        self.assertEqual(s["write_scope"], reference.WRITE_SCOPE)
        for k, v in s.items():
            if k in ("task_local_only", "write_scope"):
                continue
            self.assertIs(v, False, k)

    def test_no_floats_and_deterministic(self) -> None:
        reference.assert_no_float(self.report)
        a = reference.canonical_report(self.report)
        b = reference.canonical_report(reference.build_report())
        self.assertEqual(a, b)
        self.assertEqual(len(a[1]), 64)


class CommittedArtifactTests(unittest.TestCase):
    def test_contract_report_sources_exist_or_generated_later(self) -> None:
        # generation happens via run.py; this test checks invariants when files exist.
        contract = HERE / "contract.json"
        report = HERE / "report.json"
        sidecar = HERE / "report.json.sha256"
        if not contract.exists() or not report.exists() or not sidecar.exists():
            self.skipTest("artifacts not generated in this workspace snapshot")
        cbytes = contract.read_bytes()
        rbytes = report.read_bytes()
        self.assertEqual(cbytes, reference.canonical_bytes(reference.build_contract()))
        payload, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(rbytes, payload.encode("ascii"))
        self.assertEqual(sidecar.read_text(encoding="ascii"), digest + "  report.json\n")


if __name__ == "__main__":
    unittest.main()
