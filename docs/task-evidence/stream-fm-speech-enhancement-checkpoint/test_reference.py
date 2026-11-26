# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit and adverse tests for Stream.FM speech enhancement evidence."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import reference
import run

HERE = Path(__file__).resolve().parent


class TestReference(unittest.TestCase):
    def test_stable_task_identity(self) -> None:
        identity = reference.task_row_identity()
        self.assertFalse(identity["whole_file_hashed"])
        self.assertEqual(identity["stable_sha256"], reference.STABLE_TASK_SHA256)
        self.assertEqual(identity["source"], reference.BOARD_PATH)

    def test_build_report_invariants(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["blocked"] for g in report["gates"]))
        self.assertEqual(len(report["exact_blockers"]), 8)
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertTrue(report["qualification"]["no_missing_result_qualifies_candidate"])
        self.assertFalse(report["synthetic_control"]["qualifies_candidate"])
        self.assertTrue(report["synthetic_control"]["not_streamfm"])
        self.assertTrue(report["synthetic_control"]["not_real_audio_corpus"])

    def test_canonical_report_bytes_stable(self) -> None:
        a = run.report_bytes()
        b = run.report_bytes()
        self.assertEqual(a, b)
        self.assertTrue(a.endswith(b"\n"))
        reference.strict_loads(a.decode("utf-8"))

    def test_contract_and_sources(self) -> None:
        contract = reference.strict_loads(run.build_contract().decode("utf-8"))
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["streamfm_implementation_contract"]["variant"], reference.REQUIRED_VARIANT)
        sources = run.sources_bytes().decode("ascii").splitlines()
        labels = [line.split("  ", 1)[1] for line in sources]
        self.assertEqual(labels, sorted(labels))
        self.assertFalse(any(reference.BOARD_PATH in line for line in sources))

    def test_manifest_validation_and_adverse(self) -> None:
        manifest = reference.validate_manifest(reference._base_manifest())
        self.assertEqual(manifest["variant"], reference.REQUIRED_VARIANT)
        bad = dict(reference._base_manifest())
        bad["source_revision"] = "latest"
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(bad)
        bad = dict(reference._base_manifest())
        bad.pop("checkpoint_sha256")
        with self.assertRaises(reference.Reject):
            reference.validate_manifest(bad)
        cases = reference.adverse_cases()
        self.assertGreaterEqual(len(cases), 20)
        self.assertTrue(all(c["result"] == "rejected" for c in cases))

    def test_strict_json_rejects_nonfinite_and_duplicates(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')
        with self.assertRaises(reference.Reject):
            reference.strict_loads('[NaN]')
        with self.assertRaises(reference.Reject):
            reference.strict_loads('[Infinity]')

    def test_frame_validation(self) -> None:
        frame = [0.0] * 160
        self.assertEqual(len(reference.validate_frame(frame)), 160)
        with self.assertRaises(reference.Reject):
            reference.validate_frame([0.0] * 159)
        with self.assertRaises(reference.Reject):
            reference.validate_frame([float("nan")] + [0.0] * 159)

    def test_artifacts_exist_after_all(self) -> None:
        # run.py check uses generated expected bytes; ensure local files present in repo state test environment.
        for name in run.LOCAL_FILES:
            if name in ("report.json", "report.json.sha256", "contract.json", "SOURCES.sha256"):
                continue
            self.assertTrue((HERE / name).is_file(), name)

    def test_no_board_hashing(self) -> None:
        report = reference.build_report()
        self.assertNotIn(reference.BOARD_PATH, report["source_pins"])
        self.assertNotIn(reference.BOARD_PATH, report["boundary_pins"])
        self.assertFalse(report["task_row_identity"]["whole_file_hashed"])


if __name__ == "__main__":
    unittest.main()
