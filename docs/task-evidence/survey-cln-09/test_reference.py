# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-CLN-09 evidence map."""

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
            "real_echo_audio",
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
        self.assertEqual(self.report["taxonomy"]["id"], "CLN-09")
        self.assertEqual(
            self.report["taxonomy"]["name"],
            "Gain, loudness and dynamic-range control",
        )
        self.assertEqual(self.report["taxonomy"]["scope"], "discovered_extension")
        self.assertEqual(self.report["taxonomy"]["output_kind"], "waveform/control")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S27", "S19", "S46"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F09")
        self.assertEqual(self.report["category_scope"]["category_id"], "CLN-09")
        self.assertEqual(self.report["category_scope"]["not_tonal_correction_category"], "CLN-10")
        self.assertEqual(self.report["category_scope"]["not_declipping_category"], "RST-01")
        self.assertEqual(self.report["category_scope"]["not_echo_cancellation_category"], "CLN-05")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        for token in ("automatic gain control", "compression", "peak limiting", "normalization"):
            self.assertIn(token, families)
        self.assertIn("learned", families)

    def test_source_leads_are_s27_s19_s46(self):
        leads = self.report["source_leads"]
        self.assertEqual([lead["source_id"] for lead in leads], ["S27", "S19", "S46"])
        self.assertEqual(leads[0]["title"], "WebRTC audio processing interface")
        self.assertEqual(leads[1]["title"], "FFmpeg audio filters")
        self.assertEqual(leads[2]["title"], "Speech Signal Improvement challenge findings")
        for lead in leads:
            self.assertTrue(lead["finding"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["mapped_components"])

    def test_subcase_separation_is_enforced(self):
        boundary = self.report["level_boundary"]
        self.assertIs(boundary["capture_gain_is_not_digital_leveling"], True)
        self.assertIs(boundary["digital_leveling_is_not_whole_file_normalization"], True)
        self.assertIs(boundary["peak_limiting_is_not_loudness_normalization"], True)
        self.assertIs(boundary["streaming_loudness_control_is_not_offline_mastering"], True)
        self.assertIs(boundary["clipping_and_noise_amplification_are_tracked"], True)

    def test_real_corpus_meter_and_runtime_are_not_claimed(self):
        self.assertIs(self.report["level_boundary"]["rights_qualified_paired_cohort_staged"], False)
        self.assertIs(self.report["level_boundary"]["loudness_standard_conformance_measured"], False)
        self.assertIs(self.report["level_boundary"]["device_gain_control_contract_measured"], False)
        self.assertIs(self.report["level_boundary"]["human_listening_result"], False)
        self.assertIs(self.report["level_boundary"]["target_device_timing_measured"], False)
        for key in (
            "independent_heldout_test_split_present",
            "licensed_public_corpus_staged",
            "rights_qualified_real_speech_staged",
            "standards_loudness_meter_present",
            "pinned_provider_runtime_parity_present",
            "neural_weights_present",
        ):
            self.assertIs(self.report["discovery"][key], False, key)

    def test_pcen_stays_an_adjacent_boundary(self):
        family = next(row for row in self.report["method_families"] if row["family_id"] == "MF-M3")
        self.assertIn("pcen-feature-frontend", family["components"])
        self.assertIn("adjacent", family["family"].lower())
        self.assertIn("not_a_waveform_loudness_controller", family["status"])

    def test_no_human_listening_or_independent_benchmark(self):
        self.assertIs(self.report["evidence_classes"]["human_listening_result"], False)
        self.assertIs(self.report["evidence_classes"]["independent_heldout_benchmark"], False)
        self.assertIs(self.report["evidence_classes"]["loudness_standard_conformance"], False)
        self.assertIs(self.report["evidence_classes"]["device_gain_control_or_loop"], False)
        self.assertIs(self.report["evidence_classes"]["target_device_timing"], False)
        self.assertIs(self.report["evidence_classes"]["real_speech_rights_qualified"], False)
        self.assertIs(self.report["evidence_classes"]["release_claim"], False)

    def test_comparison_inputs_separate_evidence_classes(self):
        classes = {row["class"] for row in self.report["comparison_inputs"]}
        self.assertIn("historical_local_synthetic_fixture", classes)
        self.assertIn("historical_local_recorded_research_screen", classes)
        self.assertIn("source_only_frozen_protocol", classes)
        self.assertIn("missing_no_local_cohort", classes)
        self.assertNotIn("human_listening_result", classes)
        self.assertNotIn("independent_heldout_benchmark", classes)
        self.assertNotIn("device_loop", classes)

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["synthetic_historical_local"], True)
        self.assertIs(classes["recorded_research_pilot_historical_local"], True)
        self.assertIs(classes["source_reported_documentation"], True)
        self.assertIs(classes["new_execution_in_this_survey"], False)
        self.assertIs(classes["parity_or_qualification_claim"], False)

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
        self.assertEqual(len(self.report["historical_executions"]), 10)
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
        self.assertEqual(len(self.report["gaps"]), 10)
        for gap in self.report["gaps"]:
            self.assertTrue(gap["follow_up_ids"])
            self.assertTrue(set(gap["follow_up_ids"]) <= links)
            self.assertTrue(set(gap["follow_up_ids"]) <= ids)
            self.assertTrue(gap["owner_note"])
            if not gap["feasibility_task_exists"]:
                self.assertIn("no", gap["owner_note"].lower())

    def test_feasibility_links_exist_where_claimed(self):
        modes = {link["task_id"]: link["mode"] for link in self.report["board_links"]}
        claimed = 0
        for gap in self.report["gaps"]:
            if gap["feasibility_task_exists"]:
                claimed += 1
                self.assertIn("feasibility", {modes[tid] for tid in gap["follow_up_ids"]})
        self.assertEqual(claimed, 2)

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
        self.assertIn("source:research/level_tone_control_20261028.md", labels)
        self.assertIn("worktree:docs/task-evidence/ebu-r128-ffmpeg-loudnorm/report.json", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)

    def test_local_and_reported_outcomes_stay_distinct(self):
        local = {row["id"] for row in self.report["historical_executions"]}
        reported = {row["id"] for row in self.report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)
        self.assertTrue(all(row["class"] == "source_reported" for row in self.report["reported_outcomes"]))

    def test_ffmpeg_screen_is_self_measured_and_offline(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-10")
        self.assertIs(execution["values"]["independent_ebu_meter"], False)
        self.assertIn("self-measured", execution["scope"])
        self.assertIn("FFmpeg is absent", execution["scope"])
        control = next(row for row in self.report["controls"] if row["id"] == "CT-9")
        self.assertIn("independent", control["role"])

    def test_ridge_loses_to_the_direct_rule(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-2")
        values = execution["values"]
        self.assertGreater(
            values["ridge_mean_abs_rms_error_db"],
            values["target_rms_mean_abs_rms_error_db"],
        )
        self.assertIn("worse than the direct rule", execution["scope"])

    def test_envelope_agc_gain_step_is_worse_than_identity(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-3")
        values = execution["values"]
        self.assertGreater(
            values["windowed_rms_abs_error_db_agc"],
            values["windowed_rms_abs_error_db_identity"],
        )
        self.assertGreater(values["agc_only_clipped_samples"], 0)

    def test_speex_activity_is_advisory(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-8")
        self.assertIn("advisory", execution["scope"])
        self.assertIn("never gates audio", execution["scope"])

    def test_acceptance_profile_maps_dsp_cases_and_blocks_gates(self):
        mapped = self.report["acceptance_profile"]["mapped"]
        self.assertEqual(self.report["acceptance_profile"]["profile"], "DSP")
        for key in (
            "sweeps",
            "steps",
            "impulses",
            "silence",
            "clean_speech",
            "intelligibility_or_load_control",
            "gain",
            "response",
            "attack_release",
            "headroom",
            "delay",
            "numerical_behavior",
            "state_transitions",
            "interacting_nonlinear_configurations",
        ):
            self.assertIn(key, mapped)
        self.assertEqual(len(self.report["acceptance_profile"]["blocked"]), 8)


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

    def test_unlabelled_execution_rejected_without_state_change(self):
        bad = dict(reference.HISTORICAL_EXECUTIONS[0], id="HX", scope="unlabelled")
        with mock.patch.object(
            reference, "HISTORICAL_EXECUTIONS", reference.HISTORICAL_EXECUTIONS + [bad]
        ):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_evidence_class_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"independent_heldout_benchmark": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_human_listening_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"human_listening_result": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_loudness_conformance_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"loudness_standard_conformance": True}):
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
        with mock.patch.object(reference, "SOURCE_LEADS", [bad]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_missing_subcase_separation_rejected_without_state_change(self):
        with mock.patch.dict(reference.LEVEL_BOUNDARY, {"capture_gain_is_not_digital_leveling": False}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_real_standard_meter_claim_rejected_without_state_change(self):
        with mock.patch.dict(reference.LEVEL_BOUNDARY, {"loudness_standard_conformance_measured": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unknown_component_rejected_without_state_change(self):
        bad = dict(reference.COMPONENT_CENSUS[0], component_id="not-an-inventory-component")
        with mock.patch.object(reference, "COMPONENT_CENSUS", reference.COMPONENT_CENSUS + [bad]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
