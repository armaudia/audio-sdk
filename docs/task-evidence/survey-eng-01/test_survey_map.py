#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the SDK-SURVEY-ENG-01 task-local evidence map."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_report as spec  # noqa: E402
import verify as checker  # noqa: E402


def load_report() -> tuple[bytes, dict]:
    raw = (HERE / "report.json").read_bytes()
    return raw, json.loads(raw.decode("utf-8"))


class SurveyEng01MapTest(unittest.TestCase):
    def test_pinned_python_and_no_bytecode(self) -> None:
        self.assertEqual(sys.version_info[:3], (3, 12, 16))
        self.assertTrue(sys.dont_write_bytecode)

    def test_only_expected_files_present(self) -> None:
        actual = {path.name for path in HERE.iterdir() if path.is_file()}
        self.assertEqual(actual, checker.EXPECTED_FILES)
        for path in HERE.iterdir():
            self.assertFalse(path.is_symlink(), f"symlink: {path.name}")
            self.assertLess(path.stat().st_size, 200_000, f"large file: {path.name}")

    def test_canonical_report_and_sidecar(self) -> None:
        raw, _ = load_report()
        expected = spec.canonical_json(spec.build_report()).encode("utf-8")
        self.assertEqual(raw, expected)
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="utf-8"),
            f"{digest}  report.json\n",
        )

    def test_all_source_pins_recompute(self) -> None:
        _, report = load_report()
        pins = spec.build_pins()
        self.assertEqual(report["source_pins"], pins)
        self.assertEqual(report["source_pin_verification"]["count"], len(pins))
        for pin in pins:
            self.assertEqual(
                hashlib.sha256(spec.pin_path(pin["key"]).read_bytes()).hexdigest(),
                pin["sha256"],
            )

    def test_named_evidence_inputs_pinned(self) -> None:
        _, report = load_report()
        keys = {row["key"] for row in report["source_pins"]}
        self.assertTrue({
            "workspace:audio_categories.md",
            "workspace:research/category_registry.json",
            "workspace:research/task_backlog.json",
        }.issubset(keys))

    def test_board_projection_is_stable(self) -> None:
        _, report = load_report()
        projection = report["source_pin_verification"]["board"]
        self.assertEqual(projection, spec.board_projection())
        self.assertNotIn("status", projection["fields"])
        self.assertNotIn("review", projection["fields"])
        self.assertIn("claim", projection["fields"])

    def test_canonical_manifest(self) -> None:
        self.assertEqual(
            (HERE / "SOURCES.sha256").read_text(encoding="utf-8"),
            spec.build_manifest(),
        )

    def test_license_sidecars(self) -> None:
        for name in ("report.json", "report.json.sha256", "SOURCES.sha256"):
            self.assertEqual(
                (HERE / f"{name}.license").read_text(encoding="utf-8"),
                checker.LICENSE_TEXT,
            )

    def test_original_families_and_component_owners(self) -> None:
        _, report = load_report()
        families = report["original_method_families"]
        self.assertEqual(
            {row["id"] for row in families["classic"]},
            {"framing-channel-mapping", "bandlimited-resampling"},
        )
        self.assertEqual(families["ml"]["registry_text"], "No ML requirement")
        self.assertEqual(families["ml"]["status"], "not_applicable")
        self.assertEqual(families["ml"]["mapped_components"], [])
        components = {row["component_id"] for row in report["component_map"]}
        self.assertTrue(checker.EXPECTED_COMPONENTS.issubset(components))

    def test_source_lead_and_missing_evidence(self) -> None:
        _, report = load_report()
        lead = next(row for row in report["source_leads"] if row["id"] == "S42")
        self.assertEqual(lead["registry_revision_pin"], "unpinned master URL")
        self.assertIn(
            "not a byte-equal pin",
            lead["local_counterpart"]["relation"],
        )
        self.assertTrue(
            any(row["component_id"] == "speex-resampler"
                for row in lead["component_mapping"])
        )
        self.assertEqual(len(report["missing_evidence"]), 3)

    def test_historical_executions_have_comparison_fields(self) -> None:
        _, report = load_report()
        rows = report["historical_executions"]
        self.assertEqual(len(rows), 4)
        for row in rows:
            for field in ("inputs", "controls", "assets", "local_outcomes",
                          "reported_outcomes", "limits"):
                self.assertTrue(row[field], f"{row['id']}:{field}")
        self.assertEqual(
            rows[-1]["evidence_layer"], "reported_comparator_matrix_only"
        )

    def test_no_claims_and_release_boundary(self) -> None:
        _, report = load_report()
        claims = report["claim_gate"]
        self.assertTrue(claims["no_missing_result_qualifies_candidate"])
        for field in checker.CLAIM_FIELDS:
            self.assertIs(claims[field], False)
        boundary = report["release_boundary"]
        self.assertTrue(boundary["fixed_v0_unchanged"])
        self.assertTrue(boundary["no_default_abi_build_or_ci_change"])
        self.assertEqual(boundary["quality_and_publication_decision_owner"], "audio-bench")

    def test_gap_followup_is_bounded_and_unassigned(self) -> None:
        _, report = load_report()
        gap = report["gap_followup"]
        self.assertEqual(gap["parent_task"], spec.TASK_ID)
        self.assertIn("proposed", gap["status"])
        self.assertIn("not_a_board_entry", gap["status"])
        self.assertIn("no implementation", gap["deliverable"])
        self.assertTrue(gap["stop_condition"].startswith("feasibility only"))

    def test_readme_declares_survey_boundary(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        for heading in (
            "## Original method families",
            "## Source lead S42",
            "## Historical executions",
            "## Bounded feasibility",
            "## Release boundary",
            "## Reproduction and checks",
        ):
            self.assertIn(heading, text)

    def test_strict_verifier_passes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            result = checker.main()
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
