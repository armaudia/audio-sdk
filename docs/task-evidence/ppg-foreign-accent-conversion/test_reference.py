# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for SDK-PPG-FOREIGN-ACCENT-CONVERSION evidence."""

from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent


class ReferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.report_text, cls.report_digest = reference.canonical_report(cls.report)
        cls.contract = reference.build_contract(cls.report, cls.report_digest)

    def test_defer_incomplete_not_qualified(self) -> None:
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["profile"], "voice")
        q = self.report["qualification"]
        self.assertFalse(q["candidate_qualified"])
        self.assertTrue(q["no_missing_result_qualifies_candidate"])
        self.assertFalse(q["missing_result_promoted"])

    def test_release_gates_blocked(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([g["id"] for g in gates], [f"RG-{i:02d}" for i in range(1, 9)])
        self.assertTrue(all(g["status"] == "blocked" for g in gates))
        self.assertEqual(self.report["qualification"]["blocked_gate_count"], 8)

    def test_voice_profile_not_satisfied(self) -> None:
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "voice")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        for item in profile["required_items"].values():
            self.assertIn(item["status"], {"absent", "not_measured", "structural_only"})
            self.assertEqual(item["qualification_effect"], "none")

    def test_no_candidate_geometry_or_assets(self) -> None:
        c = self.report["candidate"]
        self.assertFalse(c["geometry_documented"])
        self.assertFalse(c["source_present"])
        self.assertFalse(c["weights_present"])
        self.assertFalse(c["runtime_present"])
        self.assertFalse(c["exact_numeric_output_present"])
        self.assertIsNone(c["reported_input_sample_rate_hz"])
        self.assertIsNone(c["reported_output_sample_rate_hz"])
        self.assertIsNone(c["reported_hop_samples"])

    def test_audit_absent_and_live(self) -> None:
        audit = self.report["asset_audit"]
        self.assertFalse(audit["qualified"])
        self.assertEqual(audit["audit_result"], "absent")
        self.assertEqual(audit["observed"], reference.audit_assets())

    def test_surrogate_is_structural_only(self) -> None:
        control = self.report["reference_protocol"]
        self.assertFalse(control["model_executed"])
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(control["duration"]["duration_ratio"], "1")
        self.assertFalse(control["alignment"]["streaming_supported"])
        self.assertFalse(control["alignment"]["candidate_alignment_asserted"])
        self.assertFalse(control["surrogate"]["uses_target_reference"])
        self.assertTrue(control["reset"]["matches_fresh"])
        for outcome in control["acceptance_outcomes"]:
            self.assertFalse(outcome["measured"])
            self.assertIsNone(outcome["value"])

    def test_adverse_controls_fail_closed(self) -> None:
        adverse = self.report["controls"]["adverse"]
        self.assertEqual([a["case_id"] for a in adverse], list(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(a["status"] == "rejected" for a in adverse))
        self.assertTrue(all(a["state_unchanged"] is True for a in adverse))
        self.assertTrue(self.report["controls"]["adverse_all_rejected"])
        self.assertTrue(self.report["controls"]["missing_asset_rejected_before_processing"])
        self.assertTrue(self.report["controls"]["missing_result_never_qualifies"])

    def test_strict_json_rejects_noncanonical(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":NaN}')
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":Infinity}')

    def test_pcm_and_fixture_reject_invalid(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_pcm([0.0, math.nan])
        with self.assertRaises(reference.Reject):
            reference.validate_pcm([0.0, 1.5])
        with self.assertRaises(reference.Reject):
            reference.validate_fixture({"source_samples": 1})

    def test_manifest_rejected_without_approved_identity(self) -> None:
        manifest = reference._shape_only_manifest()
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(manifest)

    def test_scope_and_boundary(self) -> None:
        self.assertTrue(all(v is False for v in self.report["boundary"].values()))
        scope = self.report["scope"]
        self.assertTrue(scope["synthetic_only"])
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key in {"synthetic_only", "task_local_only"}:
                continue
            self.assertFalse(value, key)

    def test_board_identity_stable_only(self) -> None:
        row = self.report["task_row_identity"]
        self.assertFalse(row["whole_file_hashed"])
        self.assertEqual(set(row["stable_fields"]), set(reference.STABLE_TASK_FIELDS))
        self.assertEqual(row["stable_fields"]["id"], reference.TASK)
        self.assertEqual(row["claim"]["base_commit"], reference.BASE_COMMIT)

    def test_report_deterministic_and_on_disk(self) -> None:
        first = reference.canonical_report(reference.build_report())
        second = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)
        text, digest = first
        self.assertEqual((HERE / "report.json").read_bytes(), text.encode("utf-8"))
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")

    def test_contract_matches_report(self) -> None:
        for key in ("decision", "status", "evidence_status", "qualification_status", "release_gates", "exact_blockers", "source_pins", "boundary_pins", "acceptance_profile", "candidate", "reference", "boundary", "scope", "format", "licensing", "caller_asset_contract", "source_reported_context", "qualification"):
            self.assertEqual(self.contract[key], self.report[key])
        self.assertEqual(self.contract["board_row"], self.report["task_row_identity"])
        self.assertEqual(self.contract["task"], self.report["task_id"])
        self.assertEqual(self.contract["component"], self.report["component"])

    def test_sources_manifest_no_mutable_task_board_hash(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            if "TASKS.json" in line:
                self.assertIn("linked-row identity only", line)

    def test_cold_start_run_out(self) -> None:
        expected = reference.canonical_report(reference.build_report())[0].encode("utf-8")
        with tempfile.TemporaryDirectory(prefix="ppg-fac-test-") as td:
            target = Path(td) / "out"
            result = subprocess.run([sys.executable, str(HERE / "run.py"), "--out", str(target)], cwd=str(HERE), capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual((target / "report.json").read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
