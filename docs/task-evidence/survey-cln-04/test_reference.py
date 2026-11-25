# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-CLN-04 evidence map."""

from __future__ import annotations

import copy
import os
import subprocess
import sys
import tempfile
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


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.builder = reference.EvidenceMap()
        self.report = self.builder.build()
        self.snapshot = self.builder.snapshot()

    def test_disposition_is_defer_incomplete_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["readiness"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["status"], "proposal_only_survey_incomplete")

    def test_all_eight_release_gates_blocked(self):
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates], ["RG-0%d" % n for n in range(1, 9)])
        self.assertTrue(all(gate["blocked"] is True for gate in gates))

    def test_no_public_or_release_change(self):
        for key, value in self.report["boundary"].items():
            self.assertIs(value, False, key)
        for key in (
            "real_speech",
            "real_corpus",
            "real_reverb_audio",
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

    def test_taxonomy_and_legacy_family(self):
        self.assertEqual(self.report["taxonomy"]["id"], "CLN-04")
        self.assertEqual(self.report["taxonomy"]["name"], "Dereverberation")
        self.assertEqual(self.report["taxonomy"]["scope"], "requested")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S20", "S31"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F03")
        self.assertEqual(self.report["legacy_backlog"]["scope"], "requested")
        self.assertEqual(self.report["category_scope"]["category_id"], "CLN-04")
        self.assertIs(self.report["category_scope"]["dereverberation_only"], True)

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        self.assertIn("delayed linear prediction", families)
        self.assertIn("weighted prediction error", families)
        self.assertIn("frame-causal", families)
        self.assertIn("dnn-supported prediction", families)
        self.assertIn("nonlinear postfilters", families)
        self.assertIn("restoration", families)

    def test_source_leads_cover_s20_s31(self):
        leads = self.report["source_leads"]
        self.assertEqual([lead["source_id"] for lead in leads], ["S20", "S31"])
        self.assertEqual(leads[0]["title"], "NARA-WPE dereverberation implementation")
        self.assertEqual(leads[1]["title"], "VoiceFixer restoration implementation")
        for lead in leads:
            self.assertEqual(lead["access_scope"], "search excerpt")
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])

    def test_real_room_weights_and_benchmark_are_not_claimed(self):
        boundary = self.report["reverberation_boundary"]
        self.assertIs(boundary["real_room_cohort_staged"], False)
        self.assertIs(boundary["real_speech_or_listening_result"], False)
        self.assertIs(boundary["dereverb_weights_staged"], False)
        self.assertIs(boundary["dereverb_specific_benchmark_result"], False)
        self.assertIs(boundary["source_reported_results_promoted"], False)
        self.assertIs(self.report["discovery"]["dereverb_model_weights_staged"], False)
        self.assertIs(self.report["discovery"]["real_room_corpus_staged"], False)
        self.assertIs(self.report["discovery"]["real_speech_staged"], False)
        self.assertIs(self.report["evidence_classes"]["real_room_or_standard_cohort"], False)

    def test_playback_echo_is_not_pooled_as_dereverberation(self):
        boundary = self.report["reverberation_boundary"]
        self.assertIs(boundary["dereverberation_is_not_playback_echo"], True)
        self.assertIs(boundary["joint_aec_result_pooled_as_dereverb"], False)
        family = next(row for row in self.report["method_families"] if row["family_id"] == "MF-C4")
        self.assertIn("not_pooled_as_dereverb", family["status"])
        control = next(row for row in self.report["controls"] if row["id"] == "CT-7")
        self.assertIn("never pooled", control["role"])

    def test_offline_noncausal_and_online_causal_are_separated(self):
        families = {row["family_id"]: row for row in self.report["method_families"]}
        self.assertIn("offline", families["MF-C1"]["family"].lower())
        self.assertIn("frame-causal", families["MF-C2"]["family"].lower())
        self.assertIn("block-online", families["MF-C2"]["family"].lower())
        self.assertIs(
            self.report["reverberation_boundary"]["noncausal_offline_result_used_as_causal_evidence"],
            False,
        )
        control = next(row for row in self.report["controls"] if row["id"] == "CT-4")
        self.assertIn("never evidence for a causal implementation", control["role"])

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("historical_local_paired_synthetic", classes)
        self.assertIn("historical_local_measured_rir", classes)
        self.assertIn("historical_local_metric_control", classes)
        self.assertIn("historical_local_paired_synthetic_clean_preservation", classes)
        self.assertIn("source_reported_only", classes)
        self.assertIn("missing_no_local_cohort", classes)
        self.assertNotIn("human_listening_result", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["paired_synthetic_historical_local"], True)
        self.assertIs(classes["measured_rir_historical_local"], True)
        self.assertIs(classes["metric_control_historical_local"], True)
        self.assertIs(classes["clean_preservation_diagnostic_historical_local"], True)
        self.assertIs(classes["vendor_or_source_reported"], True)
        self.assertIs(classes["unpaired_predictive_historical_local"], False)
        self.assertIs(classes["prepared_listening_without_ratings"], False)
        self.assertIs(classes["human_listening_result"], False)
        self.assertIs(classes["real_room_or_standard_cohort"], False)
        text = " ".join(row["label"].lower() for row in self.report["historical_executions"])
        text += " " + " ".join(row["class"] for row in self.report["comparison_inputs"])
        self.assertNotIn("predictive", text)
        self.assertNotIn("prepared_listening", text)
        self.assertNotIn("real_room_cohort", text)

    def test_mutable_board_file_is_not_pinned_or_gated(self):
        self.assertNotIn(reference.BOARD_PATH, self.report["source_pins"])
        self.assertNotIn(reference.BOARD_PATH, self.report["boundary_pins"])
        self.assertIs(self.report["mutable_provenance"]["gate"], False)
        self.assertEqual(self.report["mutable_provenance"]["path"], reference.BOARD_PATH)
        self.assertNotIn("sha256_at_read", self.report["mutable_provenance"])
        raw = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        self.assertNotIn("source:" + reference.BOARD_PATH, raw)
        self.assertNotIn("worktree:" + reference.BOARD_PATH, raw)

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

    def test_board_projection_contains_only_linked_id_title_mode(self):
        board = reference.strict_json_load(reference.find_workspace() / reference.BOARD_PATH)
        projection = reference._board_projection(board)
        self.assertEqual(len(projection), 64)
        mutated = copy.deepcopy(board)
        for task in mutated["tasks"]:
            task["status"] = "done"
            task["owner"] = "somebody"
            task["notes"] = "mutable"
        self.assertEqual(reference._board_projection(mutated), projection)

    def test_historical_executions_link_censused_components(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        for row in self.report["historical_executions"]:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])
            self.assertIn("not rerun by this survey", row["scope"])

    def test_controls_and_assets_are_pinned(self):
        pins = set(self.report["source_pins"]) | set(self.report["boundary_pins"])
        for row in self.report["controls"] + self.report["assets"] + self.report["historical_executions"]:
            self.assertIn(row["source_pin"], pins)
        for row in self.report["comparison_inputs"] + self.report["reported_outcomes"]:
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
                self.assertIn("no", gap["owner_note"].lower())

    def test_feasibility_links_exist_where_claimed(self):
        modes = {link["task_id"]: link["mode"] for link in self.report["board_links"]}
        for gap in self.report["gaps"]:
            if gap["feasibility_task_exists"]:
                self.assertIn("feasibility", {modes[tid] for tid in gap["follow_up_ids"]})

    def test_no_follow_up_task_invented(self):
        for link in self.report["board_links"]:
            self.assertIn(link["mode"], ("feasibility", "research-control", "foundation", "external-adapter"))
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
        self.assertIn("source:research/dereverberation_candidates_20261028.md", labels)
        self.assertIn("worktree:api/include/audio_sdk/provider_v0.h", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)

    def test_local_and_reported_outcomes_stay_distinct(self):
        local = {row["id"] for row in self.report["historical_executions"]}
        reported = {row["id"] for row in self.report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)
        self.assertLessEqual(local, {"HE-1", "HE-2", "HE-3", "HE-4", "HE-5", "HE-6", "HE-7"})
        self.assertLessEqual(reported, {"RO-1", "RO-2", "RO-3", "RO-4", "RO-5", "RO-6"})

    def test_source_reported_model_results_are_not_promoted(self):
        outcomes = {row["id"]: row for row in self.report["reported_outcomes"]}
        for key in ("RO-3", "RO-4", "RO-5", "RO-6"):
            self.assertEqual(outcomes[key]["class"].startswith("source_reported"), True, key)
            boundary = outcomes[key]["boundary"].lower()
            self.assertTrue(
                any(word in boundary for word in ("no ", "not ", "missing")),
                key,
            )
        self.assertIn("not from the local VoiceBank-DEMAND checkpoint", outcomes["RO-4"]["boundary"])
        self.assertIn("no local hardware check", outcomes["RO-5"]["boundary"])

    def test_metric_and_preservation_controls_are_mapped(self):
        controls = {row["id"] for row in self.report["controls"]}
        self.assertIn("CT-5", controls)
        self.assertIn("CT-6", controls)
        comparison = {row["id"]: row for row in self.report["comparison_inputs"]}
        self.assertEqual(comparison["CI-7"]["class"], "historical_local_metric_control")
        self.assertEqual(comparison["CI-6"]["class"], "historical_local_paired_synthetic_clean_preservation")
        self.assertIn("no real speech", comparison["CI-6"]["boundary"])

    def test_acceptance_profile_is_room_and_maps_gaps(self):
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "Room")
        self.assertIn("frozen_rir_or_render_reference", profile["mapped"])
        self.assertIn("echo_only_near_end_overlap_no_reference", profile["mapped"])
        self.assertIn("clean_preservation", profile["mapped"])
        self.assertIn("alignment_state_memory_timing", profile["mapped"])
        self.assertEqual(len(profile["blocked"]), 8)


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

    def test_missing_workspace_rejected_without_state_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(reference, "find_workspace", return_value=Path(tmp)):
                with self.assertRaises(reference.MapError):
                    self.builder.build()
        self._assert_unchanged()

    def test_tampered_pin_rejected_without_state_change(self):
        with mock.patch.dict(reference.WORKTREE_PINS, {"CONTRACTS.md": "0" * 64}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_missing_document_anchor_rejected_without_state_change(self):
        with mock.patch.dict(reference.DOC_ANCHORS, {"audio_categories.md": ["not in the document"]}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unknown_board_link_rejected_without_state_change(self):
        invented = {"task_id": "SDK-NOT-ON-THE-BOARD", "title": "Invented", "mode": "feasibility"}
        with mock.patch.object(reference, "BOARD_LINKS", reference.BOARD_LINKS + [invented]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unlinked_gap_rejected_without_state_change(self):
        bad_gap = {"id": "GX", "follow_up_ids": [], "owner_note": "none"}
        with mock.patch.object(reference, "GAPS", reference.GAPS + [bad_gap]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_nonfeasibility_claim_rejected_without_state_change(self):
        bad_gap = {
            "id": "GY",
            "follow_up_ids": ["SDK-FND-TIMING"],
            "feasibility_task_exists": True,
            "owner_note": "none",
        }
        with mock.patch.object(reference, "GAPS", reference.GAPS + [bad_gap]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_execution_component_link_is_checked(self):
        bad = dict(reference.HISTORICAL_EXECUTIONS[0], id="HX", component_ids=["not-a-component"])
        with mock.patch.object(
            reference, "HISTORICAL_EXECUTIONS", reference.HISTORICAL_EXECUTIONS + [bad]
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_clean_preservation_class_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.EVIDENCE_CLASSES,
            {"clean_preservation_diagnostic_historical_local": False},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_board_identity_change_rejected_without_state_change(self):
        changed = dict(reference.BOARD_LINKS[0], title="Renamed task")
        with mock.patch.object(reference, "BOARD_LINKS", [changed] + reference.BOARD_LINKS[1:]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_pinning_mutable_board_rejected_without_state_change(self):
        with mock.patch.dict(reference.SOURCE_PINS, {reference.BOARD_PATH: "0" * 64}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unknown_source_lead_rejected_without_state_change(self):
        bad = dict(reference.SOURCE_LEADS[0], source_id="S99")
        with mock.patch.object(reference, "SOURCE_LEADS", [bad, reference.SOURCE_LEADS[1]]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_real_room_staging_rejected_without_state_change(self):
        with mock.patch.dict(reference.REVERBERATION_BOUNDARY, {"real_room_cohort_staged": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_dereverb_weights_staging_rejected_without_state_change(self):
        with mock.patch.dict(reference.REVERBERATION_BOUNDARY, {"dereverb_weights_staged": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_playback_echo_pooling_rejected_without_state_change(self):
        with mock.patch.dict(
            reference.REVERBERATION_BOUNDARY,
            {"joint_aec_result_pooled_as_dereverb": True},
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
