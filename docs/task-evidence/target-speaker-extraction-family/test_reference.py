# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-TARGET-SPEAKER-EXTRACTION-FAMILY blocker package."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]


class ReferenceTest(unittest.TestCase):
    def test_board_row_digest(self) -> None:
        self.assertEqual(reference.board_row_digest(), reference.BOARD_ROW_STABLE_SHA256)

    def test_contract_report_deterministic(self) -> None:
        self.assertEqual(reference.canonical_report_bytes(), reference.canonical_report_bytes())
        self.assertEqual(reference.contract_bytes(), reference.contract_bytes())

    def test_report_schema_and_disposition(self) -> None:
        report = reference.build_report()
        self.assertEqual(set(report), reference.REQUIRED_REPORT_KEYS)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_blocked_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertTrue(report["no_missing_result_qualifies_candidate"])

    def test_gates_blocked(self) -> None:
        report = reference.build_report()
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in report["gates"]))

    def test_boundary_and_scope(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["boundary"], reference.BOUNDARY)
        self.assertEqual(report["scope"], reference.SCOPE)
        self.assertTrue(report["scope"]["task_local_only"])
        self.assertFalse(any(v for k, v in report["scope"].items() if isinstance(v, bool) and k != "task_local_only"))
        self.assertFalse(any(v for v in report["boundary"].values() if isinstance(v, bool)))

    def test_upstream_not_fabricated(self) -> None:
        up = reference.build_report()["upstream"]
        self.assertIsNone(up["commit"])
        self.assertIsNone(up["license"])
        self.assertIsNone(up["checkpoint_identity"])
        self.assertFalse(up["source_present"])

    def test_controls(self) -> None:
        ctrl = reference.controls()
        self.assertTrue(ctrl["asset"]["rejected_all"])
        self.assertTrue(ctrl["config"]["rejected_all"])
        self.assertTrue(ctrl["frame"]["rejected_all"])
        self.assertTrue(ctrl["streaming_parity"]["all_identical"])
        self.assertTrue(ctrl["delay"]["matches"])
        self.assertTrue(ctrl["reset"]["fresh_matches_reset"])
        self.assertTrue(ctrl["silence"]["exact_zero"])
        self.assertTrue(ctrl["multichannel"]["mono_rejected"])
        self.assertTrue(ctrl["multichannel"]["other_channels_change_output"])
        self.assertTrue(ctrl["partial_tail"]["prefix_matches_full"])
        self.assertTrue(ctrl["nonfinite_counter"]["state_digest_unchanged"])

    def test_report_digest_sidecar_matches(self) -> None:
        report = (HERE / "report.json").read_bytes()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii").strip().split()[0]
        self.assertEqual(hashlib.sha256(report).hexdigest(), sidecar)

    def test_pins_and_readme(self) -> None:
        pins = reference.parse_pin_lines((HERE / "SOURCES.sha256").read_text(encoding="ascii"))
        self.assertEqual(len(pins), len(reference.allowed_pin_keys()))
        for digest, raw in pins:
            if raw.startswith("source:"):
                path = reference.resolve_source_path(raw.split(":", 1)[1])
            elif raw.startswith("sdk:"):
                path = SDK_ROOT / raw.split(":", 1)[1]
            else:
                path = SDK_ROOT / raw
            self.assertTrue(path.is_file(), raw)
            self.assertEqual(reference.sha256_file(path), digest)
        counts = reference.verify_readme_digests((HERE / "README.md").read_text(encoding="utf-8"))
        expected = reference.expected_readme_keys()
        for section in reference.README_SECTIONS:
            self.assertEqual(counts[section], len(expected[section]))

    def test_strict_rejections(self) -> None:
        r = reference.strict_rejection_examples()
        self.assertEqual(r["bad_json_rejected"], r["bad_json_total"])
        self.assertEqual(r["bad_pins_rejected"], r["bad_pins_total"])
        self.assertEqual(r["bad_readme_rejected"], r["bad_readme_total"])

    def test_no_negative_zero(self) -> None:
        self.assertFalse(reference.has_negative_zero(reference.build_report()))
        self.assertFalse(reference.has_negative_zero(reference.contract_payload()))


if __name__ == "__main__":
    unittest.main()
