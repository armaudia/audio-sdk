# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unittest suite for the deterministic SDK-SURVEY-CLN-12 evidence map."""

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
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["decision"], "DEFER")
        self.assertEqual(self.report["qualification"]["readiness"], "incomplete")
        self.assertIs(self.report["qualification"]["qualifies"], False)
        self.assertIs(self.report["qualification"]["proposal_only"], True)

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
            "real_masker_audio",
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
        self.assertEqual(self.report["taxonomy"]["id"], "CLN-12")
        self.assertEqual(
            self.report["taxonomy"]["name"],
            "Near-end listening / intelligibility enhancement",
        )
        self.assertEqual(self.report["taxonomy"]["scope"], "discovered_extension")
        self.assertEqual(self.report["taxonomy"]["source_ids"], ["S54", "S55", "S56"])
        self.assertEqual(self.report["taxonomy"]["related_category_ids"], ["CLN-01", "CLN-09", "CLN-10", "OBS-01"])
        self.assertEqual(self.report["taxonomy"]["discovery_status"], "catalogued")
        self.assertEqual(self.report["taxonomy"]["candidate_census_status"], "not_started")
        self.assertEqual(self.report["taxonomy"]["benchmark_status"], "not_started")
        self.assertEqual(self.report["legacy_backlog"]["family_id"], "F09")
        self.assertEqual(self.report["category_scope"]["category_id"], "CLN-12")
        self.assertEqual(self.report["category_scope"]["not_capture_denoising_category"], "CLN-01")
        self.assertEqual(self.report["category_scope"]["not_gain_loudness_or_drc_category"], "CLN-09")
        self.assertEqual(self.report["category_scope"]["not_tonal_correction_category"], "CLN-10")
        self.assertEqual(self.report["category_scope"]["not_assessment_category"], "OBS-01")

    def test_both_catalogued_method_branches_covered(self):
        branches = {row["branch"] for row in self.report["method_families"]}
        self.assertEqual(branches, {"classic", "ml"})
        families = " ".join(row["family"].lower() for row in self.report["method_families"])
        self.assertIn("spectral energy redistribution", families)
        self.assertIn("intelligibility-index optimization", families)
        self.assertIn("dynamic-range compression", families)
        self.assertIn("family search remains open", families)

    def test_source_leads_are_s54_s55_s56(self):
        leads = self.report["source_leads"]
        self.assertEqual([lead["source_id"] for lead in leads], ["S54", "S55", "S56"])
        self.assertEqual(leads[0]["title"], "Near-end listening enhancement analysis")
        self.assertEqual(leads[1]["title"], "Fraunhofer receiver-side intelligibility enhancement")
        self.assertEqual(leads[2]["title"], "Author near-end enhancement software lead")
        for lead in leads:
            self.assertTrue(lead["mapped_components"])
            self.assertTrue(lead["gap_ids"])
            self.assertTrue(lead["finding"])

    def test_source_leads_state_limits_honestly(self):
        leads = {lead["source_id"]: lead for lead in self.report["source_leads"]}
        self.assertIn("not a runnable candidate", leads["S54"]["finding"])
        self.assertIn("no source", leads["S55"]["finding"].lower())
        self.assertIn("timed out", leads["S56"]["finding"])
        self.assertIn("no runnable candidate", leads["S56"]["finding"])

    def test_nele_boundary_is_not_overclaimed(self):
        boundary = self.report["nele_boundary"]
        for key in (
            "human_listening_result_present",
            "listening_effort_or_hearing_profile_present",
            "independent_heldout_benchmark_present",
            "intelligibility_benefit_established",
            "published_method_reproduction_present",
            "ml_family_verified",
            "category_specific_weights_present",
            "listener_panel_present",
            "target_device_timing_present",
            "output_power_constraint_protocol_present",
        ):
            self.assertIs(boundary[key], False, key)
        for key in (
            "modifies_received_speech_before_playback",
            "requires_listener_side_masking_or_noise_estimate",
            "output_power_constraint_is_material",
            "capture_denoising_is_not_nele",
            "simple_gain_is_not_nele",
            "tonal_correction_is_not_nele",
        ):
            self.assertIs(boundary[key], True, key)

    def test_discovery_is_closed_for_weights_runtime_and_listeners(self):
        discovery = self.report["discovery"]
        self.assertIs(discovery["weights_present"], False)
        self.assertIs(discovery["runtime_present"], False)
        self.assertIs(discovery["listener_panel_present"], False)
        self.assertIs(discovery["heldout_benchmark_present"], False)
        self.assertIs(discovery["published_method_archive_present"], False)
        self.assertEqual(
            discovery["category_specific_component_ids"],
            [
                "fixed-six-band-spectral-tilt",
                "optfractasii-approximation",
                "noise-aware-shaping-plus-drc",
                "full-band-receive-drc-control",
                "feed-forward-compressor",
            ],
        )
        self.assertEqual(
            discovery["learned_candidate_ids"],
            [
                "se-agcnet",
                "self-supervised-neural-multiband-eq-and-dynamics",
                "differentiable-biquad-neural-parametric-eq",
            ],
        )

    def test_historical_executions_link_censused_components(self):
        census = {row["component_id"] for row in self.report["component_census"]}
        for row in self.report["historical_executions"]:
            self.assertTrue(row["component_ids"], row["id"])
            self.assertTrue(set(row["component_ids"]) <= census, row["id"])
            self.assertIn("not rerun by this survey", row["scope"])

    def test_objective_screen_numbers_are_transcribed(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-1")
        values = execution["values"]
        self.assertEqual(values["utterances"], 12)
        self.assertEqual(values["maskers"], 3)
        self.assertEqual(values["pairs_per_method"], 108)
        self.assertAlmostEqual(values["identity_stoi"], 0.6896785488310864)
        self.assertAlmostEqual(values["fixed_tilt_estoi"], 0.5759644767419412)
        self.assertAlmostEqual(values["fixed_tilt_delta_estoi"], 0.004037045969401021)
        self.assertLess(values["fixed_tilt_delta_estoi_ci_low"], 0.0)
        self.assertGreater(values["fixed_tilt_delta_estoi_ci_high"], 0.0)
        self.assertGreater(values["drc_only_delta_estoi_ci_low"], 0.0)
        self.assertLess(values["noise_aware_optfract_delta_estoi"], 0.0)
        self.assertIn("objective predictors", execution["scope"])

    def test_synthetic_masking_control_is_not_intelligibility(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-2")
        self.assertEqual(execution["values"]["conditions"], 9)
        self.assertAlmostEqual(execution["values"]["tilt_rms_ratio_mean"], 1.000697)
        self.assertAlmostEqual(execution["values"]["level_confound_rms_ratio_mean"], 1.122018)
        self.assertIn("not STOI/ESTOI", execution["scope"])
        self.assertIn("band-energy redistribution", execution["scope"].lower())

    def test_receive_drc_control_is_excluded(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-3")
        self.assertEqual(execution["values"]["conditions"], 15)
        self.assertAlmostEqual(execution["values"]["output_peak_abs_at_0_dbfs"], 0.95)
        self.assertEqual(execution["values"]["zero_content_delay_samples"], 0)
        self.assertIn("excluded from qualification", execution["scope"])

    def test_drc_gain_ramp_control_is_engineering_only(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-4")
        values = execution["values"]
        self.assertEqual(values["pairs"], 30)
        self.assertLess(values["drc_rms_error_400ms_db"], values["identity_rms_error_400ms_db"])
        self.assertAlmostEqual(values["drc_delta_si_sdr_vs_identity_db"], 0.945)
        self.assertLess(values["drc_delta_rms_vs_agc_ci_low_db"], 0.0)
        self.assertGreater(values["drc_delta_rms_vs_agc_ci_high_db"], 0.0)
        self.assertIn("not a learned DRC", execution["scope"])

    def test_scorer_crosscheck_is_not_a_listener_result(self):
        execution = next(row for row in self.report["historical_executions"] if row["id"] == "HE-6")
        self.assertEqual(execution["values"]["paired_items"], 6)
        self.assertAlmostEqual(execution["values"]["crosscheck_abs_delta_stoi"], 2.1510571102112408e-15)
        self.assertIn("not evidence of speech intelligibility", execution["scope"])

    def test_evidence_classes_match_mapped_records(self):
        classes = self.report["evidence_classes"]
        self.assertIs(classes["local_objective_screen_historical_local"], True)
        self.assertIs(classes["local_synthetic_masking_control"], True)
        self.assertIs(classes["local_synthetic_drc_control"], True)
        self.assertIs(classes["local_scorer_crosscheck"], True)
        self.assertIs(classes["source_reported_only"], True)
        for key in (
            "human_listening_result",
            "listening_effort_or_hearing_profile",
            "independent_heldout_benchmark",
            "intelligibility_benefit",
            "published_method_reproduction",
            "ml_local_execution",
            "target_device_timing",
            "output_power_constraint_full_protocol",
            "new_execution_in_this_survey",
            "parity_or_qualification_claim",
        ):
            self.assertIs(classes[key], False, key)

    def test_simple_gain_family_is_adjacent_and_not_nele(self):
        family = next(row for row in self.report["method_families"] if row["family_id"] == "MF-C4")
        self.assertIn("adjacent", family["family"].lower())
        self.assertIn("not near-end listening", family["family"].lower())
        self.assertIn("boundary_only", family["status"])

    def test_ml_family_is_open_and_has_no_execution(self):
        ml = next(row for row in self.report["method_families"] if row["branch"] == "ml")
        self.assertIn("open", ml["family"].lower())
        self.assertEqual(ml["family_id"], "MF-M1")
        self.assertIs(self.report["evidence_classes"]["ml_local_execution"], False)
        ml_ids = set(self.report["discovery"]["learned_candidate_ids"])
        for row in self.report["historical_executions"]:
            self.assertFalse(set(row["component_ids"]) & ml_ids, row["id"])

    def test_published_methods_are_source_reported_only(self):
        self.assertIs(self.report["evidence_classes"]["published_method_reproduction"], False)
        reported = {row["id"]: row for row in self.report["reported_outcomes"]}
        for row_id in ("RO-1", "RO-2", "RO-3"):
            self.assertEqual(reported[row_id]["class"], "source_reported", row_id)
        self.assertIn("does not treat it as independent validation", reported["RO-1"]["boundary"])
        self.assertIn("no source archive", reported["RO-2"]["boundary"])
        self.assertIn("archive was not obtained", reported["RO-3"]["boundary"])

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

    def test_controls_assets_and_outcomes_are_pinned(self):
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

    def test_no_follow_up_task_invented_or_implementation_scoped(self):
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
        self.assertIn("source:research/listening_intelligibility_20261028.md", labels)
        self.assertIn("worktree:docs/task-evidence/fixed-six-band-spectral-tilt/evidence/report.json", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)

    def test_local_and_reported_outcomes_stay_distinct(self):
        local = {row["id"] for row in self.report["historical_executions"]}
        reported = {row["id"] for row in self.report["reported_outcomes"]}
        self.assertTrue(local)
        self.assertTrue(reported)
        self.assertFalse(local & reported)
        self.assertLessEqual(local, {"HE-1", "HE-2", "HE-3", "HE-4", "HE-5", "HE-6"})

    def test_acceptance_profile_maps_power_listening_and_timing_gaps(self):
        mapped = self.report["acceptance_profile"]["mapped"]
        self.assertEqual(self.report["acceptance_profile"]["profile"], "DSP")
        self.assertIn("output_power_constraint", mapped)
        self.assertIn("no full output-power-constraint protocol", mapped["output_power_constraint"])
        self.assertIn("listening", mapped)
        self.assertIn("No near-end listening panel", mapped["listening"])
        self.assertIn("target_device", mapped)
        self.assertIn("No target-device", mapped["target_device"])
        self.assertEqual(len(self.report["acceptance_profile"]["blocked"]), 8)

    def test_reproduction_commands_are_documented(self):
        reproduction = self.report["reproduction"]
        for key in ("comparison", "tests", "report", "sources", "contract", "verify"):
            self.assertTrue(reproduction[key], key)
        self.assertIn("three byte-identical cold-start repeats", reproduction["comparison"])
        self.assertIn("test_reference.py", reproduction["tests"])
        self.assertIn("verify.py", reproduction["verify"])


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

    def test_unsupported_human_listening_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"human_listening_result": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_intelligibility_benefit_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"intelligibility_benefit": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_ml_execution_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"ml_local_execution": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_heldout_benchmark_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"independent_heldout_benchmark": True}):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()

    def test_unsupported_published_reproduction_rejected_without_state_change(self):
        with mock.patch.dict(reference.EVIDENCE_CLASSES, {"published_method_reproduction": True}):
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

    def test_missing_source_lead_component_rejected_without_state_change(self):
        bad = dict(reference.SOURCE_LEADS[0], mapped_components=[])
        with mock.patch.object(reference, "SOURCE_LEADS", [bad]):
            with self.assertRaises(reference.MapError):
                self.builder.build()
        self._assert_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
