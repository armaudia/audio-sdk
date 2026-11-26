# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-SPK-04 evidence map."""

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

    def test_non_text_json_payload_rejected(self):
        with self.assertRaises(reference.MapError):
            reference.strict_json_loads(b'{"a":1}')


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.builder = reference.EvidenceMap()
        self.report = self.builder.build()
        self.snapshot = self.builder.snapshot()

    def test_disposition_is_defer_incomplete_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["qualification_status"], "not_qualified")
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
            "real_diarization_audio",
            "weights",
            "runtime_invocation",
            "listening",
            "device_timing",
            "benchmark_claim",
            "release_claim",
            "numeric_parity_claim",
            "diarization_claim",
            "speaker_identity_claim",
            "processor_exposure",
            "public_default",
            "network_access",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        self.assertIs(self.report["evidence_classes"]["new_execution_in_this_survey"], False)
        self.assertIs(self.report["evidence_classes"]["parity_or_qualification_claim"], False)
        self.assertIs(self.report["evidence_classes"]["diarization_execution"], False)
        self.assertIs(self.report["evidence_classes"]["der_execution"], False)

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "SPK-04")
        self.assertEqual(self.report["taxonomy"]["name"], "Anonymous speaker diarization")
        self.assertEqual(self.report["taxonomy"]["group"], "Speakers and separation")
        self.assertEqual(self.report["taxonomy"]["scope"], "requested")
        self.assertEqual(self.report["taxonomy"]["output_kind"], "annotation")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S06", "S47"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F06")
        self.assertEqual(self.report["legacy_backlog"]["next_action"], "Plan discovery across required source buckets")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml", "ml-adjacent", "adjacent"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        for term in ("segmentation", "statistical", "clustering", "neural", "diarization", "embedding", "end-to-end"):
            self.assertIn(term, families)
        classic = [row for row in self.report["method_families"] if row["branch"] == "classic"]
        ml = [row for row in self.report["method_families"] if row["branch"] == "ml"]
        self.assertTrue(classic)
        self.assertTrue(ml)

    def test_source_leads_cover_s06_and_s47(self):
        ids = {lead["source_id"] for lead in self.report["source_leads"]}
        self.assertEqual(ids, {"S06", "S47"})
        for lead in self.report["source_leads"]:
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["mapped_components"])
            self.assertIn(lead["source_id"], self.report["taxonomy"]["source_ids"])

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        for expected in (
            "historical_local_adjacent_any_speech",
            "historical_local_adjacent_positive_only",
            "historical_local_adjacent_synthetic_speaker_pair",
            "source_only_metric_documentation",
            "source_reported_meeting_pipeline_metadata",
            "source_only_catalogued_classic_components",
            "source_only_catalogued_ml_components",
            "prepared_manifest_only",
            "missing_rights_qualified_diarization_corpus",
            "missing_pyannote_runtime_and_weights",
            "missing_diarization_benchmark_protocol",
            "missing_online_revision_and_device_timing",
        ):
            self.assertIn(expected, classes)
        self.assertNotIn("diarization_execution", classes)
        self.assertNotIn("der_execution", classes)
        self.assertNotIn("human_listening_result", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        for key in (
            "adjacent_any_speech_historical_local",
            "adjacent_positive_only_historical_local",
            "adjacent_synthetic_speaker_pair_historical_local",
            "source_only_metric_documentation",
            "source_reported_meeting_pipeline_metadata",
            "source_only_catalogued_classic_components",
            "source_only_catalogued_ml_components",
            "prepared_manifest_only",
            "missing_rights_qualified_diarization_corpus",
            "missing_pyannote_runtime_and_weights",
            "missing_diarization_benchmark_protocol",
            "missing_online_revision_and_device_timing",
        ):
            self.assertIs(classes[key], True, key)
        for key in (
            "diarization_execution",
            "der_execution",
            "pyannote_local_execution",
            "neural_diarization_execution",
            "natural_meeting_diarization_execution",
            "speaker_label_output",
            "speaker_identity_execution",
            "online_revision_execution",
            "human_listening_result",
            "device_timing",
            "new_execution_in_this_survey",
            "parity_or_qualification_claim",
            "release_claim",
        ):
            self.assertIs(classes[key], False, key)

    def test_diarization_boundary_is_closed(self):
        boundary = self.report["diarization_boundary"]
        for key in (
            "anonymous_labels_only",
            "anonymous_labels_are_not_enrolled_identities",
            "diarization_is_not_speech_activity_detection",
            "diarization_is_not_overlap_detection",
            "diarization_is_not_speaker_identity",
            "diarization_is_not_source_separation",
            "diarization_is_not_target_speaker_extraction",
            "diarization_is_not_transcription_or_language_identification",
            "overlap_must_be_represented",
            "online_revisions_must_be_explicit",
            "speaker_level_truth_and_any_speaker_union_kept_separate",
            "unknown_time_is_never_nonspeech",
            "synthetic_mixture_is_not_natural_diarization",
            "author_reported_is_not_local",
        ):
            self.assertIs(boundary[key], True, key)
        for key in (
            "diarization_execution_present",
            "der_execution_present",
            "natural_meeting_diarization_execution_present",
            "pyannote_runtime_or_weights_present",
            "rights_qualified_diarization_corpus_present",
            "speaker_level_truth_present",
            "speaker_identity_execution_present",
            "online_revision_execution_present",
            "calibrated_array_geometry_present",
            "device_timing_present",
            "human_listening_result_present",
            "benchmark_or_release_qualification_present",
        ):
            self.assertIs(boundary[key], False, key)

    def test_execution_coverage_counts(self):
        coverage = self.report["execution_coverage"]
        self.assertEqual(coverage["catalogued_diarization_component_count"], 1)
        for key in (
            "locally_evaluated_diarization_component_count",
            "diarization_execution_count",
            "der_execution_count",
            "pyannote_execution_count",
            "neural_diarization_execution_count",
            "natural_meeting_diarization_execution_count",
            "rights_qualified_diarization_execution_count",
            "online_revision_execution_count",
            "device_timing_execution_count",
        ):
            self.assertEqual(coverage[key], 0, key)
        self.assertEqual(coverage["adjacent_any_speech_execution_count"], 2)
        self.assertEqual(coverage["adjacent_synthetic_speaker_pair_execution_count"], 1)

    def test_historical_executions_are_adjacent_only(self):
        allowed = {
            "historical_local_adjacent_any_speech",
            "historical_local_adjacent_positive_only",
            "historical_local_adjacent_synthetic_speaker_pair",
        }
        for row in self.report["historical_executions"]:
            self.assertIn(row["outcome_class"], allowed, row["id"])
            self.assertNotIn("diarization", row["outcome_class"])
            self.assertNotIn("der", row["outcome_class"])
            self.assertIn("not rerun by this survey", row["scope"])
            self.assertIn("not a diarization", row["scope"])
            self.assertIs(row["adjacent"], True, row["id"])
            self.assertIs(row["not_component_evidence"], True, row["id"])
            self.assertTrue(row["values"])

    def test_hush_row_is_synthetic_construction_not_natural_diarization(self):
        row = {item["id"]: item for item in self.report["historical_executions"]}["HE-3"]
        self.assertEqual(row["outcome_class"], "historical_local_adjacent_synthetic_speaker_pair")
        self.assertIs(row["values"]["natural_overlap"], False)
        self.assertIs(row["values"]["isolated_clean_references"], False)
        self.assertIs(row["values"]["speaker_ids_used_for_mixture_construction"], True)
        self.assertEqual(row["values"]["speaker_label_output_segments"], 0)
        self.assertEqual(row["values"]["der_metric_rows"], 0)

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

    def test_controls_and_assets_and_executions_are_pinned(self):
        pins = set(self.report["source_pins"]) | set(self.report["boundary_pins"])
        for row in self.report["controls"] + self.report["assets"] + self.report["historical_executions"]:
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

    def test_report_file_and_sidecar_match_recomputed_bytes(self):
        raw = run.report_bytes()
        self.assertEqual((HERE / "report.json").read_bytes(), raw)
        digest = reference.sha256_bytes(raw)
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            digest + "  report.json\n",
        )

    def test_contract_and_scope_fields(self):
        raw = run.build_contract()
        self.assertEqual((HERE / "contract.json").read_bytes(), raw)
        contract = reference.strict_json_loads(raw.decode("utf-8"))
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "proposal_only_survey_incomplete")
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertEqual(contract["qualification"]["readiness"], "incomplete")
        self.assertIs(contract["qualification"]["diarization_execution_present"], False)
        self.assertIs(contract["qualification"]["der_execution_present"], False)
        self.assertEqual(contract["category_scope"], reference.CATEGORY_SCOPE)
        self.assertEqual(contract["diarization_boundary"], reference.DIARIZATION_BOUNDARY)
        self.assertEqual(contract["scope"], reference.SCOPE)
        self.assertEqual(contract["public_surface"], reference.BOUNDARY)
        self.assertEqual(len(contract["release_gates"]), 8)

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
        self.assertIn("worktree:docs/task-evidence/survey-spk-01/README.md", labels)
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

    def test_missing_pinned_file_rejected(self):
        workspace = reference.find_workspace()
        sdk_root = reference.find_sdk_root()
        bad = dict(reference.SOURCE_PINS)
        bad["research/does-not-exist-spk04.md"] = "0" * 64
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

    def test_adjacent_execution_relabelled_as_diarization_rejected(self):
        bad = copy.deepcopy(reference.HISTORICAL_EXECUTIONS)
        bad[0]["outcome_class"] = "historical_local_diarization_execution"
        with mock.patch.object(reference, "HISTORICAL_EXECUTIONS", bad):
            with self.assertRaises(reference.MapError):
                reference.build_report()

    def test_diarization_claim_without_execution_rejected(self):
        bad = dict(reference.EVIDENCE_CLASSES)
        bad["diarization_execution"] = True
        with mock.patch.object(reference, "EVIDENCE_CLASSES", bad):
            with self.assertRaises(reference.MapError):
                reference.build_report()

    def test_der_claim_without_execution_rejected(self):
        bad = dict(reference.EVIDENCE_CLASSES)
        bad["der_execution"] = True
        with mock.patch.object(reference, "EVIDENCE_CLASSES", bad):
            with self.assertRaises(reference.MapError):
                reference.build_report()

    def test_unknown_board_task_rejected(self):
        bad = list(reference.BOARD_LINKS) + [
            {"task_id": "SDK-INVENTED-TASK", "title": "Invented", "mode": "feasibility"}
        ]
        with mock.patch.object(reference, "BOARD_LINKS", bad):
            with self.assertRaises(reference.MapError):
                reference.build_report()

    def test_gap_without_board_link_rejected(self):
        bad = copy.deepcopy(reference.GAPS)
        bad[0]["follow_up_ids"] = []
        with mock.patch.object(reference, "GAPS", bad):
            with self.assertRaises(reference.MapError):
                reference.build_report()

    def test_boundary_opened_rejected(self):
        bad = dict(reference.DIARIZATION_BOUNDARY)
        bad["diarization_execution_present"] = True
        with mock.patch.object(reference, "DIARIZATION_BOUNDARY", bad):
            with self.assertRaises(reference.MapError):
                reference.build_report()


if __name__ == "__main__":
    unittest.main()
