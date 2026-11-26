# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-UNIVNET blocker evidence."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402


class UnivnetEvidenceTest(unittest.TestCase):
    def test_contract_shape_and_decision(self) -> None:
        contract = reference.build_contract()
        reference.validate_contract(contract)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "incomplete")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertTrue(contract["proposal_only"])
        self.assertFalse(contract["board_file_pinned"])
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in contract["release_gates"]))
        self.assertEqual(len(contract["exact_blockers"]), 6)
        self.assertTrue(all(b["status"] == "open" and b["qualifies"] is False for b in contract["exact_blockers"]))

    def test_report_is_canonical_and_matches_contract(self) -> None:
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        self.assertEqual(text, json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n")
        self.assertEqual(digest, hashlib.sha256(text.encode("utf-8")).hexdigest())
        contract = reference.build_contract()
        self.assertEqual(report["contract_sha256"], reference.object_digest(contract))
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["all_release_gates_blocked"], True)
        self.assertEqual(report["qualification"]["real_result_present"], False)

    def test_board_identity_is_stable_projection_only(self) -> None:
        projection = reference.board_row_projection(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(projection, reference.BOARD_ROW_PROJECTION)
        self.assertEqual(reference.board_row_digest(projection), reference.board_row_digest(reference.BOARD_ROW_PROJECTION))
        self.assertEqual(reference.linked_rows_digest(), reference.linked_rows_digest(reference.LINKED_ROWS))
        self.assertNotIn("status", projection)
        self.assertNotIn("owner", projection)

    def test_absence_probes_detect_present_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data/models/univnet").mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "artifact_present_reopen_required"):
                reference.absence_probes(root)

    def test_manifest_rejects_invalid_cases(self) -> None:
        cases = [
            ({}, "missing_field"),
            ({"schema_id": reference.MANIFEST_SCHEMA_ID}, "missing_field"),
            ({"bad": 1}, "missing_field"),
        ]
        for payload, code in cases:
            result = reference.validate_manifest(payload, probe_paths=False)
            self.assertFalse(result["accepted"])
            self.assertEqual(result["code"], code)
        control = reference._manifest_control()
        control["schema_id"] = "wrong"
        self.assertEqual(reference.validate_manifest(control, probe_paths=False)["code"], "invalid_schema")
        control = reference._manifest_control()
        control["outcomes"]["intelligibility_wer"] = float("nan")
        self.assertEqual(reference.validate_manifest(control, probe_paths=False)["code"], "nonfinite_value")
        control = reference._manifest_control()
        control["outcomes"]["intelligibility_wer"] = float("inf")
        self.assertEqual(reference.validate_manifest(control, probe_paths=False)["code"], "nonfinite_value")
        control = reference._manifest_control()
        control["weights"][0]["byte_count"] = -1
        self.assertEqual(reference.validate_manifest(control, probe_paths=False)["code"], "invalid_value")
        control = reference._manifest_control()
        control["features"][0]["path"] = "relative.npy"
        self.assertEqual(reference.validate_manifest(control, probe_paths=False)["code"], "invalid_path")
        control = reference._manifest_control()
        control["controls"][2]["feature_id"] = "mel-a"
        self.assertEqual(reference.validate_manifest(control, probe_paths=False)["code"], "invalid_value")
        control = reference._manifest_control()
        control["runtime"]["threads"] = True
        self.assertEqual(reference.validate_manifest(control, probe_paths=False)["code"], "invalid_value")

    def test_admission_controls_are_fail_closed(self) -> None:
        admission = reference.admission_controls()
        self.assertTrue(admission["control"]["accepted"])
        self.assertFalse(admission["control"]["qualifies"])
        self.assertGreaterEqual(admission["summary"]["case_count"], 80)
        self.assertEqual(admission["summary"]["case_count"], admission["summary"]["rejected_count"])
        self.assertEqual(admission["summary"]["qualifying_results"], 0)
        self.assertFalse(admission["summary"]["state_advanced_on_rejection"])
        for case in admission["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])

    def test_canonical_json_rejects_duplicates_and_nonfinite(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            reference.loads_strict('{"a":1,"a":2}')
        with self.assertRaisesRegex(ValueError, "nonfinite_json_constant"):
            reference.loads_strict('{"a":NaN}')
        with self.assertRaisesRegex(ValueError, "json_root_not_object"):
            reference.loads_strict('[1]')

    def test_run_is_byte_identical(self) -> None:
        report, digest = reference.canonical_report()
        sources = run.sources_bytes().decode("ascii")
        self.assertIn(digest + "  report.json", (HERE / "report.json.sha256").read_text(encoding="ascii"))
        self.assertEqual((HERE / "report.json").read_bytes(), report.encode("utf-8"))
        self.assertIn("docs/task-evidence/univnet/reference.py", sources)


if __name__ == "__main__":
    unittest.main()
