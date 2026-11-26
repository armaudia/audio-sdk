# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local VCTK/DNS2020/AMI/EARS/SMARD evidence package."""

from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import unittest

import reference


class JsonTests(unittest.TestCase):
    def test_canonical_json_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"value": math.nan})

    def test_strict_json_rejects_duplicate_key(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_rejects_nan_constant(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":NaN}')


class IdentityTests(unittest.TestCase):
    def test_identity_is_linked_row_only(self) -> None:
        identity = reference.task_row_identity()
        self.assertIs(identity["whole_file_hashed"], False)
        self.assertEqual(identity["source"], "audio-benchmark-platform/plan/swarm/TASKS.json")
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_sha256"],
                         reference.sha256_bytes(reference.canonical_bytes(identity["stable_fields"])))

    def test_identity_matches_contract(self) -> None:
        identity = reference.task_row_identity()
        contract = json.loads((reference.HERE / "contract.json").read_text())
        self.assertEqual(contract["task_row_identity"]["stable_sha256"], identity["stable_sha256"])
        self.assertIs(contract["task_row_identity"]["whole_file_hashed"], False)

    def test_no_tasks_json_pin(self) -> None:
        report = reference.build_report()
        labels = set(report["source_pins"]) | set(report["boundary_pins"])
        self.assertFalse(any(label.endswith("TASKS.json") for label in labels))


class AuditTests(unittest.TestCase):
    def test_audit_is_observation_only(self) -> None:
        audit = reference.audit_workspace()
        self.assertFalse(audit["qualified"])
        self.assertEqual(audit["admitted_count"], 0)
        self.assertTrue(all(o["admitted"] is False for o in audit["observations"]))

    def test_reserved_paths_absent_or_recorded(self) -> None:
        audit = reference.audit_workspace()
        self.assertEqual(len(audit["reserved_absent_paths"]), len(reference.RESERVED_ABSENT_PATHS))
        self.assertTrue(all("exists" in r for r in audit["reserved_absent_paths"]))


class ControlTests(unittest.TestCase):
    def test_control_is_not_qualification(self) -> None:
        control = reference.build_control()
        self.assertFalse(control["qualified"])
        self.assertEqual(control["qualification_effect"], "none")
        self.assertTrue(control["missing_never_qualifies"])
        self.assertEqual(control["missing_score_count"], 1)

    def test_adverse_controls_all_rejected(self) -> None:
        adverse = reference.run_adverse_controls()
        self.assertGreaterEqual(len(adverse), 15)
        self.assertTrue(all(item["result"] == "rejected" for item in adverse))


class ManifestValidationTests(unittest.TestCase):
    def _base_manifest(self, root: Path) -> dict:
        files = {}
        for name in ("cohort.json", "scoring.json", "overlap.json", "approval.json", "rights-vctk.json"):
            p = root / name
            p.write_text("{}\n", encoding="utf-8")
            files[name] = p
        corpora = []
        for cid in reference.REQUIRED_CORPORA:
            rec = root / f"rights-{cid}.json"
            if not rec.exists():
                rec.write_text("{}\n", encoding="utf-8")
            corpora.append({
                "corpus_id": cid,
                "split": "test",
                "source_root_or_locator": str(root),
                "license": "declared",
                "intended_use": "evaluation",
                "rights_record_sha256": reference.sha256(rec),
                "source_items": [{
                    "item_id": f"{cid}-s1",
                    "path": str(rec),
                    "sha256": reference.sha256(rec),
                    "role": "source",
                    "group_id": f"{cid}-g1",
                    "split": "test",
                }],
                "pair_items": [],
                "group_items": [],
                "notes": "synthetic structure only",
            })
        return {
            "schema_id": reference.MANIFEST_SCHEMA_ID,
            "manifest_id": "m1",
            "revision": "r1",
            "corpora": corpora,
            "intended_use_records": [
                {"corpus_id": cid, "record_path": str(root / "rights-vctk.json"), "record_sha256": reference.sha256(root / "rights-vctk.json")}
                for cid in reference.REQUIRED_CORPORA
            ],
            "rights_records": [
                {"corpus_id": cid, "record_path": str(root / "rights-vctk.json"), "record_sha256": reference.sha256(root / "rights-vctk.json")}
                for cid in reference.REQUIRED_CORPORA
            ],
            "cohort_record_path": str(files["cohort.json"]),
            "cohort_record_sha256": reference.sha256(files["cohort.json"]),
            "scoring_plan_path": str(files["scoring.json"]),
            "scoring_plan_sha256": reference.sha256(files["scoring.json"]),
            "overlap_policy_path": str(files["overlap.json"]),
            "overlap_policy_sha256": reference.sha256(files["overlap.json"]),
            "approval_record_path": str(files["approval.json"]),
            "approval_record_sha256": reference.sha256(files["approval.json"]),
        }

    def test_valid_structure_accepted_but_not_qualified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = reference.validate_caller_manifest(self._base_manifest(root))
        self.assertTrue(result["accepted"])
        self.assertFalse(result["admitted_for_evaluation"])
        self.assertFalse(result["rights_approved"])
        self.assertFalse(result["reviewer_approved"])
        self.assertEqual(result["qualification_effect"], "none")

    def test_missing_corpus_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest(root)
            manifest["corpora"] = [c for c in manifest["corpora"] if c["corpus_id"] != "vctk"]
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_bad_hash_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest(root)
            manifest["cohort_record_sha256"] = "0" * 64
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_relative_path_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest(root)
            manifest["cohort_record_path"] = "cohort.json"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_unexpected_field_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest(root)
            manifest["extra"] = "x"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)


class ReportTests(unittest.TestCase):
    def test_report_is_defer_and_not_qualified(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))
        self.assertFalse(report["qualification"]["candidate_qualified"])

    def test_boundary_and_scope(self) -> None:
        report = reference.build_report()
        self.assertFalse(report["boundary"]["provider_registration"])
        self.assertFalse(report["boundary"]["default_selected"])
        self.assertFalse(report["boundary"]["shared_build_or_ci_change"])
        self.assertTrue(report["scope"]["task_local_only"])
        self.assertFalse(report["scope"]["real_corpus_scored"])

    def test_determinism(self) -> None:
        a = reference.canonical_bytes(reference.build_report())
        b = reference.canonical_bytes(reference.build_report())
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
