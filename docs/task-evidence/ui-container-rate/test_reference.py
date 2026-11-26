# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-UI-CONTAINER-RATE blocker package."""

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent


class TestReference(unittest.TestCase):
    def test_board_row_sha(self) -> None:
        self.assertEqual(reference.board_row_digest(), reference.BOARD_ROW_STABLE_SHA256)
        self.assertEqual(reference.BOARD_ROW_STABLE_FIELDS["id"], reference.TASK)

    def test_report_contract_deterministic(self) -> None:
        r1 = reference.canonical_report_bytes(reference.build_report())
        r2 = reference.canonical_report_bytes(reference.build_report())
        c1 = reference.contract_bytes()
        c2 = reference.contract_bytes()
        self.assertEqual(r1, r2)
        self.assertEqual(c1, c2)
        self.assertEqual(hashlib.sha256(r1).hexdigest(), hashlib.sha256(r2).hexdigest())
        self.assertEqual(reference.strict_loads(r1.decode("utf-8"))["decision"], "DEFER")

    def test_gates_blocked(self) -> None:
        report = reference.build_report()
        self.assertEqual(len(report["gates"]), 8)
        for gate in report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertTrue(report["proposal_only"])
        self.assertTrue(report["no_missing_result_qualifies_candidate"])

    def test_surrogate_is_not_candidate(self) -> None:
        out = reference.run_synthetic_surrogate(reference.valid_surrogate_config())
        self.assertTrue(out["surrogate"])
        self.assertFalse(out["candidate_is_ui_container_rate"])
        self.assertFalse(out["qualified"])
        self.assertTrue(out["summary"]["has_one_x_control"])
        self.assertTrue(out["summary"]["has_rate_change"])
        self.assertTrue(out["summary"]["has_music"])
        self.assertTrue(out["summary"]["has_silence"])
        self.assertEqual(out["summary"]["final_partial_source_samples"], 41637 % 160)

    def test_adverse_all_rejected(self) -> None:
        adverse = reference.adverse_cases()
        self.assertGreater(adverse["case_count"], 10)
        self.assertEqual(adverse["accepted_count"], 0)
        self.assertTrue(adverse["all_rejected"])
        self.assertEqual(adverse["case_count"], adverse["rejected_count"])

    def test_strict_rejections(self) -> None:
        sr = reference.strict_rejection_examples()
        self.assertEqual(sr["bad_json_rejected"], sr["bad_json_total"])
        self.assertEqual(sr["bad_pins_rejected"], sr["bad_pins_total"])
        self.assertEqual(sr["bad_readme_rejected"], sr["bad_readme_total"])

    def test_pins_cover_manifest(self) -> None:
        keys = reference.allowed_pin_keys()
        self.assertIn("source:cpp-library/pipeline-validation/playback-speed-candidates.md", keys)
        self.assertIn(reference.TASK_PREFIX + "report.json", keys)
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", keys)

    def test_pin_paths_safe(self) -> None:
        self.assertEqual(len(reference.parse_pin_lines(reference.sources_bytes().decode("ascii"))), len(reference.allowed_pin_keys()))
        with self.assertRaises(ValueError):
            reference.parse_pin_lines("a" * 64 + "  /abs\n")
        with self.assertRaises(ValueError):
            reference.parse_pin_lines("a" * 64 + "  source:../escape\n")

    def test_readme_tables(self) -> None:
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(readme)
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))
        self.assertEqual(counts["artifacts"], len(reference.LOCAL_FILES) - 1)
        self.assertEqual(readme, reference.update_readme_artifact_table(readme))

    def test_license_sidecars(self) -> None:
        for name in reference.LICENSE_SIDECARS:
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(reference.SPDX_COPYRIGHT, text)
            self.assertIn(reference.SPDX_LICENSE, text)
        for path in HERE.glob("*.py"):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(reference.SPDX_COPYRIGHT, head)
            self.assertIn(reference.SPDX_LICENSE, head)


if __name__ == "__main__":
    unittest.main()
