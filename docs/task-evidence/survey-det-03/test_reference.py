# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-DET-03 evidence map."""

from __future__ import annotations

import copy
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

import reference
import run

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


class StrictJsonTests(unittest.TestCase):
    def test_canonical_bytes_are_order_independent(self):
        left = reference.canonical_bytes({"b": 1, "a": [2, 3]})
        right = reference.canonical_bytes({"a": [2, 3], "b": 1})
        self.assertEqual(left, right)
        self.assertTrue(left.endswith(b"\n"))

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.strict_json_loads('{"a":1,"a":2}')

    def test_nan_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.strict_json_loads('{"a":NaN}')

    def test_infinity_rejected(self):
        for token in ("Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(reference.MapError):
                    reference.strict_json_loads('{"a":%s}' % token)

    def test_noncanonical_python_value_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.canonical_bytes({"a": float("nan")})

    def test_missing_json_file_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.strict_json_load(HERE / "missing-report.json")


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.builder = reference.EvidenceMap()
        self.report = self.builder.build()
        self.snapshot = self.builder.snapshot()

    def test_disposition_is_defer_incomplete_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["readiness"], "incomplete")
        self.assertEqual(self.report["qualification"]["survey_status"], "incomplete")
        self.assertIs(self.report["qualification"]["proposal_only"], True)
        self.assertEqual(self.report["status"], "proposal_only_survey_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["readiness"], "incomplete")

    def test_all_release_gates_blocked(self):
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates], ["RG-0%d" % k for k in range(1, 9)])
        self.assertTrue(all(gate["blocked"] is True for gate in gates))

    def test_no_public_or_release_change(self):
        for key, value in self.report["boundary"].items():
            self.assertIs(value, False, key)
        for key in (
            "real_speech",
            "real_corpus",
            "real_overlap_audio",
            "weights",
            "runtime_invocation",
            "listening",
            "device_timing",
            "benchmark_claim",
            "release_claim",
            "numeric_parity_claim",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)
        self.assertIs(self.report["evidence_classes"]["overlap_detection_execution"], False)
        self.assertIs(self.report["evidence_classes"]["speaker_count_execution"], False)

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "DET-03")
        self.assertEqual(self.report["taxonomy"]["scope"], "discovered_extension")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S02"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["output_kind"], "annotation")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F05")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        for term in ("energy", "spatial", "bayesian", "segmentation", "diarization", "embedding"):
            self.assertIn(term, families)

    def test_source_leads_cover_s02(self):
        ids = {lead["source_id"] for lead in self.report["source_leads"]}
        self.assertEqual(ids, {"S02"})
        for lead in self.report["source_leads"]:
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["mapped_components"])

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("historical_local_adjacent_any_speech", classes)
        self.assertIn("historical_local_adjacent_positive_only", classes)
        self.assertIn("historical_local_adjacent_synthetic_overlap_construction", classes)
        self.assertIn("source_reported_overlap_corpus_metadata", classes)
        self.assertIn("missing_rights_qualified_overlap_reference", classes)
        self.assertIn("missing_pyannote_runtime_and_weights", classes)
        self.assertIn("missing_overlap_and_count_benchmark", classes)
        self.assertNotIn("human_listening_result", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["adjacent_any_speech_historical_local"], True)
        self.assertIs(classes["adjacent_positive_only_historical_local"], True)
        self.assertIs(classes["adjacent_synthetic_overlap_construction_historical_local"], True)
        self.assertIs(classes["source_reported_only"], True)
        self.assertIs(classes["overlap_detection_execution"], False)
        self.assertIs(classes["speaker_count_execution"], False)
        self.assertIs(classes["natural_overlap_local_execution"], False)
        self.assertIs(classes["pyannote_local_execution"], False)
        self.assertIs(classes["human_listening_result"], False)
        self.assertIs(classes["device_timing"], False)
        self.assertIs(classes["clean_reference_accuracy_claim"], False)

    def test_historical_executions_are_adjacent_only(self):
        allowed = {
            "historical_local_adjacent_any_speech",
            "historical_local_adjacent_positive_only",
            "historical_local_adjacent_synthetic_overlap_construction",
        }
        for row in self.report["historical_executions"]:
            self.assertIn(row["outcome_class"], allowed, row["id"])
            self.assertNotIn("overlap_detection", row["outcome_class"])
            self.assertNotIn("speaker_count", row["outcome_class"])
            self.assertIn("not rerun by this survey", row["scope"])
            self.assertIn("not an overlap", row["scope"])

    def test_hush_row_is_synthetic_construction_not_natural_overlap(self):
        row = {item["id"]: item for item in self.report["historical_executions"]}["HE-3"]
        self.assertEqual(row["outcome_class"], "historical_local_adjacent_synthetic_overlap_construction")
        self.assertIs(row["values"]["natural_overlap"], False)
        self.assertIs(row["values"]["isolated_clean_references"], False)
        self.assertEqual(row["values"]["overlap_detection_components"], 0)
        self.assertEqual(row["values"]["active_speaker_count_estimates"], 0)

    def test_board_status_edits_do_not_change_canonical_bytes(self):
        original = reference.strict_json_load

        def mutated(path):
            data = original(path)
            if Path(path).name == "TASKS.json":
                data = copy.deepcopy(data)
                for task in data["tasks"]:
                    task["status"] = "blocked"
                    task["owner"] = "another-agent"
            return data

        with mock.patch.object(reference, "strict_json_load", mutated):
            rebuilt = reference.build_report()
        self.assertEqual(reference.canonical_bytes(rebuilt), reference.canonical_bytes(self.report))
        self.assertNotIn("sha256_at_read", rebuilt["mutable_provenance"])

    def test_historical_executions_link_censused_components(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        for row in self.report["historical_executions"]:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])

    def test_controls_and_assets_are_pinned(self):
        pins = set(self.report["source_pins"]) | set(self.report["boundary_pins"])
        for row in self.report["controls"] + self.report["assets"]:
            self.assertIn(row["source_pin"], pins)
        for row in self.report["historical_executions"]:
            self.assertIn(row["source_pin"], pins)

    def test_all_gaps_link_existing_board_tasks(self):
        board = reference.strict_json_load(reference.find_workspace() / reference.BOARD_PATH)
        ids = {task["id"] for task in board["tasks"]}
        links = {link["task_id"] for link in self.report["board_links"]}
        self.assertTrue(links)
        for gap in self.report["gaps"]:
            self.assertTrue(gap["follow_up_ids"])
            self.assertTrue(set(gap["follow_up_ids"]) <= links)
            self.assertTrue(set(gap["follow_up_ids"]) <= ids)
            self.assertTrue(gap["owner_note"])
            if not gap["feasibility_task_exists"]:
                self.assertTrue("no" in gap["owner_note"].lower())

    def test_feasibility_links_exist_where_claimed(self):
        modes = {link["task_id"]: link["mode"] for link in self.report["board_links"]}
        for gap in self.report["gaps"]:
            if gap["feasibility_task_exists"]:
                self.assertIn("feasibility", {modes[tid] for tid in gap["follow_up_ids"]})

    def test_no_follow_up_task_invented(self):
        for link in self.report["board_links"]:
            self.assertIn(link["mode"], reference.ALLOWED_LINK_MODES)
            self.assertTrue(link["title"])
            self.assertTrue(link["linked_gaps"])

    def test_board_projection_is_stable_across_builds(self):
        second = reference.build_report()
        self.assertEqual(
            self.report["board_link_projection_sha256"],
            second["board_link_projection_sha256"],
        )
        self.assertEqual(len(self.report["board_link_projection_sha256"]), 64)

    def test_three_fresh_process_builds_are_byte_identical(self):
        script = (
            "import sys; sys.path.insert(0, %r); import reference; "
            "sys.stdout.buffer.write(reference.canonical_bytes(reference.build_report()))" % str(HERE)
        )
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        outputs = []
        for _ in range(3):
            process = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                env=env,
                check=True,
            )
            outputs.append(process.stdout)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1], outputs[2])
        self.assertEqual(outputs[0], reference.canonical_bytes(self.report))

    def test_report_file_and_sidecars_match_recomputed_bytes(self):
        raw = run.report_bytes()
        self.assertEqual((HERE / "report.json").read_bytes(), raw)
        digest = reference.sha256_bytes(raw)
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            digest + "  report.json\n",
        )

    def test_sources_manifest_is_sorted_and_complete(self):
        raw = (HERE / "SOURCES.sha256").read_bytes()
        self.assertEqual(raw, run.sources_bytes())
        labels = [line.split("  ", 1)[1] for line in raw.decode("ascii").splitlines()]
        self.assertEqual(labels, sorted(labels))
        self.assertEqual(len(labels), len(set(labels)))
        self.assertNotIn("local:SOURCES.sha256", labels)
        self.assertIn("local:contract.json", labels)
        self.assertIn("source:research/category_registry.json", labels)
        self.assertIn("worktree:api/include/audio_sdk/provider_v0.h", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)
        self.assertNotIn("worktree:" + reference.BOARD_PATH, labels)


class AtomicRejectionTests(unittest.TestCase):
    def setUp(self):
        self.builder = reference.EvidenceMap()
        self.builder.build()
        self.snapshot = self.builder.snapshot()

    def _assert_unchanged(self):
        self.assertEqual(self.builder.snapshot(), self.snapshot)

    def test_invalid_payload_type_rejected_without_state_change(self):
        with self.assertRaises(reference.MapError):
            self.builder.build(payload={"bad": object()})
        self._assert_unchanged()

    def test_nonfinite_payload_rejected_without_state_change(self):
        with self.assertRaises(reference.MapError):
            self.builder.build(payload={"bad": float("nan")})
        self._assert_unchanged()

    def test_tampered_pin_rejected(self):
        workspace = reference.find_workspace()
        sdk_root = reference.find_sdk_root()
        bad = dict(reference.SOURCE_PINS)
        first = sorted(bad)[0]
        bad[first] = "0" * 64
        with mock.patch.object(reference, "SOURCE_PINS", bad):
            with self.assertRaises(reference.MapError):
                reference._check_document_pins(workspace, sdk_root)

    def test_unknown_component_rejected(self):
        bad = list(reference.COMPONENT_CENSUS) + [
            {"component_id": "missing-component", "evidence_status": "blocked", "task": "SDK-MISSING"}
        ]
        with mock.patch.object(reference, "COMPONENT_CENSUS", bad):
            with self.assertRaises(reference.MapError):
                reference.build_report()


if __name__ == "__main__":
    unittest.main()
