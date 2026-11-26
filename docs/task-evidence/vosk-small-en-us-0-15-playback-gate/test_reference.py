# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only tests for the Vosk playback-gate DEFER package."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import reference
import run

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def _write(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8")
        handle.write(text)
        handle.close()
        return Path(handle.name)

    def test_canonical_bytes_sorted_compact_terminal_newline(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": [True, None]})
        self.assertEqual(payload, b'{"a":[true,null],"b":1}\n')
        self.assertTrue(payload.endswith(b"\n"))

    def test_float_rejected_everywhere(self) -> None:
        with self.assertRaisesRegex(ValueError, "float_not_allowed"):
            reference.canonical_bytes({"x": 1.0})

    def test_duplicate_keys_rejected(self) -> None:
        path = self._write('{"a":1,"a":2}')
        try:
            with self.assertRaisesRegex(ValueError, "json_duplicate_key"):
                reference.read_strict_json(path)
        finally:
            path.unlink()

    def test_nonfinite_constants_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            path = self._write('{"a":' + token + "}")
            try:
                with self.assertRaisesRegex(ValueError, "json_nonfinite"):
                    reference.read_strict_json(path)
            finally:
                path.unlink()

    def test_malformed_and_nonobject_rejected(self) -> None:
        path = self._write('{"a":1.5}')
        try:
            with self.assertRaisesRegex(ValueError, "float_not_allowed"):
                reference.read_strict_json(path)
        finally:
            path.unlink()


class PinAndPresenceTests(unittest.TestCase):
    def test_source_pins_verify(self) -> None:
        source, boundary = reference.verify_pins()
        self.assertEqual(set(source), set(reference.SOURCE_PINS))
        self.assertEqual(set(boundary), set(reference.BOUNDARY_PINS))
        self.assertTrue(all(row["verified"] for row in source.values()))

    def test_mutable_board_is_not_pinned(self) -> None:
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)

    def test_board_projection_has_only_stable_fields(self) -> None:
        projection = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(tuple(sorted(projection)),
                         tuple(sorted(reference.BOARD_ROW_FIELDS)))
        self.assertEqual(projection["id"], reference.TASK)
        for excluded in ("status", "owner", "claim", "review", "handoff"):
            self.assertNotIn(excluded, projection)

    def test_board_projection_digest(self) -> None:
        projection = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(reference.board_row_digest(projection),
                         hashlib.sha256(
                             reference.canonical_bytes(projection)).hexdigest())

    def test_model_tree_presence_and_exact_count(self) -> None:
        presence = reference.source_presence()
        self.assertTrue(presence["model_tree_present"])
        self.assertEqual(presence["model_file_count"], 14)
        self.assertEqual(presence["model_tree_sha256"],
                         reference.MODEL_TREE_SHA256)
        self.assertTrue(presence["runtime_library_present"])
        self.assertEqual(presence["runtime_version"], "0.3.44")
        self.assertEqual(presence["libvosk_bytes"], 12533472)

    def test_no_licensed_artifact_set_is_claimed(self) -> None:
        presence = reference.source_presence()
        self.assertFalse(
            presence["exact_licensed_source_weights_runtime_present"])
        self.assertFalse(presence["admitted"])
        self.assertFalse(presence["weights_used"])
        self.assertFalse(presence["runtime_imported"])
        self.assertFalse(presence["model_executed"])
        self.assertFalse(presence["download_attempted"])

    def test_license_markers_are_absent(self) -> None:
        findings = reference.license_marker_probe()
        self.assertEqual(findings["model_license_marker_files"], [])
        self.assertEqual(findings["runtime_license_marker_files"], [])
        self.assertFalse(findings["model_readme_states_license"])
        self.assertTrue(findings["model_readme_copyright"])
        self.assertEqual(findings["runtime_metadata_license_field"],
                         "UNKNOWN")
        self.assertFalse(findings["qualifies"])

    def test_source_pins_include_present_artifacts_and_plan_inputs(self) -> None:
        self.assertIn(
            reference.MODEL_PREFIX + "/am/final.mdl", reference.SOURCE_PINS)
        self.assertIn(
            reference.RUNTIME_PREFIX + "/libvosk.dyld", reference.SOURCE_PINS)
        self.assertIn(
            "audio-benchmark-platform/plan/INVENTORY.json",
            reference.SOURCE_PINS)


class EventAndPlanTests(unittest.TestCase):
    def test_block_mapping_and_labels(self) -> None:
        events = reference.validate_events([
            {"kind": "word", "start_sample": 0, "end_sample": 3200},
            {"kind": "filler", "start_sample": 3200, "end_sample": 4800},
            {"kind": "word", "start_sample": 4800, "end_sample": 11200},
        ], 16000)
        labels = reference.block_labels(events, 16000)
        self.assertEqual(labels, [
            "speech", "speech", "filler", "speech", "speech", "speech",
            "speech", "silence", "silence", "silence"])

    def test_full_budget_plan_has_exact_identity(self) -> None:
        labels = ["speech"] * 6 + ["filler"] + ["silence"] * 3
        plan = reference.plan_labels(labels, [1600] * 10)
        summary = plan["summary"]
        self.assertEqual(summary["rate_speech"], "9/11")
        self.assertEqual(summary["rate_flex"], "3/2")
        self.assertEqual(summary["reason"], "full_pause_budget")
        self.assertTrue(summary["duration_identity"])
        self.assertEqual(summary["planned_playback_ns"], "1000000000/1")
        self.assertEqual(plan["records"][-1]["playback_ns_end"],
                         "1000000000/1")

    def test_all_speech_falls_back_to_one(self) -> None:
        plan = reference.plan_labels(["speech"] * 5, [1600] * 5)
        self.assertEqual(plan["summary"]["reason"], "no_flex_budget")
        self.assertEqual(plan["summary"]["rate_speech"], "1/1")
        self.assertTrue(plan["summary"]["duration_identity"])

    def test_insufficient_budget_falls_back_to_one(self) -> None:
        labels = ["speech"] * 5 + ["silence"] * 5
        plan = reference.plan_labels(labels, [1600] * 10)
        self.assertEqual(plan["summary"]["reason"],
                         "insufficient_pause_budget")
        self.assertEqual(plan["summary"]["rate_speech"], "1/1")
        self.assertTrue(plan["summary"]["duration_identity"])

    def test_final_partial_window(self) -> None:
        labels = ["speech"] * 10 + ["silence"]
        durations = [1600] * 10 + [165]
        plan = reference.plan_labels(labels, durations)
        self.assertEqual(plan["summary"]["planned_source_samples"], 16165)
        self.assertEqual(plan["records"][-1]["source_end_sample"], 16165)
        self.assertTrue(plan["summary"]["duration_identity"])
        self.assertEqual(plan["summary"]["rate_flex"], "3/2")

    def test_event_rejections(self) -> None:
        bad = [
            ([], 16000),
            ([{"kind": "music", "start_sample": 0, "end_sample": 10}], 16000),
            ([{"kind": "word", "start_sample": True, "end_sample": 10}], 16000),
            ([{"kind": "word", "start_sample": -1, "end_sample": 10}], 16000),
            ([{"kind": "word", "start_sample": 10, "end_sample": 10}], 16000),
            ([{"kind": "word", "start_sample": 0, "end_sample": 16001}],
             16000),
            ([{"kind": "word", "start_sample": 0, "end_sample": 1600},
              {"kind": "word", "start_sample": 1599, "end_sample": 3200}],
             16000),
            ([{"kind": "word", "start_sample": 0.0, "end_sample": 10}], 16000),
        ]
        for items, total in bad:
            with self.assertRaises(ValueError):
                reference.validate_events(items, total)

    def test_rate_bounds_enforced_without_control_override(self) -> None:
        with self.assertRaisesRegex(ValueError, "rate_out_of_bounds"):
            reference.plan_labels(["speech"], [1600],
                                  Fraction(5, 4), Fraction(5, 4))

    def test_gate_control_is_synthetic_and_nonqualifying(self) -> None:
        control = reference.gate_control()
        self.assertEqual(control["evidence_class"],
                         "synthetic_contract_control_not_evidence")
        self.assertFalse(control["qualifies"])
        self.assertEqual(control["summary"]["case_count"], 5)
        self.assertEqual(control["summary"]["identity_passes"], 3)
        self.assertEqual(control["summary"]["qualifying_results"], 0)
        by_id = {case["id"]: case for case in control["cases"]}
        self.assertTrue(
            by_id["mixed_gate_d1"]["plan"]["summary"]["duration_identity"])
        self.assertFalse(
            by_id["fixed_1.25_control"]["plan"]["summary"]
            ["duration_identity"])
        self.assertFalse(
            by_id["slow_only_control"]["plan"]["summary"]
            ["duration_identity"])
        partial = by_id["final_partial_window"]
        self.assertEqual(partial["plan"]["records"][-1]["source_end_sample"],
                         16165)


class ManifestAdmissionTests(unittest.TestCase):
    def test_schema_control_is_admitted_but_never_qualifies(self) -> None:
        result = reference.validate_manifest(reference._base_manifest())
        self.assertTrue(result["admitted"])
        self.assertFalse(result["qualifies"])
        self.assertEqual(result["evidence_class"],
                         "synthetic_schema_control_not_evidence")
        self.assertTrue(result["duration_identity"])
        self.assertEqual(result["block_count"], 10)

    def test_all_adverse_controls_are_rejected_with_exact_code(self) -> None:
        admission = reference.admission_controls()
        self.assertEqual(admission["summary"]["rejected_count"],
                         admission["summary"]["case_count"])
        self.assertTrue(admission["summary"]["all_rejected"])
        self.assertTrue(admission["summary"]["all_codes_match"])
        self.assertEqual(admission["summary"]["qualifying_results"], 0)
        self.assertTrue(admission["control"]["accepted"])
        self.assertFalse(admission["control"]["qualifies"])
        for case in admission["cases"]:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertEqual(case["code"], case["expected_code"], case["id"])
            self.assertTrue(case["state_unchanged"], case["id"])
            self.assertFalse(case["qualifies"], case["id"])

    def test_missing_and_unknown_fields_rejected(self) -> None:
        manifest = reference._base_manifest()
        del manifest["rights"]
        with self.assertRaisesRegex(ValueError, "manifest_fields"):
            reference.validate_manifest(manifest)
        manifest = reference._base_manifest()
        manifest["extra"] = True
        with self.assertRaisesRegex(ValueError, "manifest_fields"):
            reference.validate_manifest(manifest)

    def test_nonfinite_outcome_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["outcomes"]["nonfinite_count"] = 1
        with self.assertRaisesRegex(ValueError, "outcome_nonfinite"):
            reference.validate_manifest(manifest)

    def test_float_and_real_number_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["runtime"]["threads"] = 4.5
        with self.assertRaisesRegex(ValueError, "runtime_threads_not_int"):
            reference.validate_manifest(manifest)

    def test_self_qualified_outcome_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["outcomes"]["qualified"] = True
        with self.assertRaisesRegex(ValueError, "outcome_self_qualified"):
            reference.validate_manifest(manifest)

    def test_unaligned_and_overlapping_events_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["events"]["items"][1]["start_sample"] = 3199
        with self.assertRaisesRegex(ValueError,
                                    "event_overlap_or_unsorted"):
            reference.validate_manifest(manifest)

    def test_rights_flags_must_all_be_true(self) -> None:
        for field in reference.RIGHTS_FIELDS:
            manifest = reference._base_manifest()
            manifest["rights"][field] = False
            with self.assertRaisesRegex(ValueError, "rights_" + field):
                reference.validate_manifest(manifest)

    def test_weight_set_must_be_exact_model_tree(self) -> None:
        manifest = reference._base_manifest()
        manifest["weights"]["files"][0]["name"] = "extra.bin"
        with self.assertRaisesRegex(ValueError, "weight_name"):
            reference.validate_manifest(manifest)

    def test_control_kinds_must_be_unique_and_complete(self) -> None:
        manifest = reference._base_manifest()
        manifest["controls"][1]["kind"] = "identity_1x"
        with self.assertRaisesRegex(ValueError, "control_kind_duplicate"):
            reference.validate_manifest(manifest)

    def test_admission_never_invokes_runtime_or_reads_audio(self) -> None:
        summary = reference.admission_controls()["summary"]
        for field in ("runtime_invoked", "audio_read", "weights_loaded",
                      "model_executed", "network_used",
                      "state_advanced_on_rejection"):
            self.assertFalse(summary[field], field)


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_disposition(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.contract["proposal_only"])
        self.assertFalse(self.contract["board_file_pinned"])
        reference.validate_contract(self.contract)

    def test_report_disposition(self) -> None:
        report = self.report
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["qualification"]["qualifying_results"], 0)

    def test_eight_blocked_release_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        for index, gate in enumerate(gates, start=1):
            self.assertEqual(gate["id"], f"RG-{index:02d}")
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             self.report["linked_row_identity"]["projection"])

    def test_six_open_blockers(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        artifact_ids = {row["id"] for row in self.report["required_artifacts"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)

    def test_present_artifacts_are_still_blocked(self) -> None:
        artifacts = {row["id"]: row for row in
                     self.report["required_artifacts"]}
        for artifact_id in ("A01", "A02"):
            row = artifacts[artifact_id]
            self.assertTrue(row["present"])
            self.assertTrue(row["verified"])
            self.assertFalse(row["licensed"])
            self.assertFalse(row["admitted"])
            self.assertTrue(row["blocked"])
        for artifact_id in ("A03", "A04", "A05", "A06", "A07", "A08",
                            "A09", "A10"):
            row = artifacts[artifact_id]
            self.assertFalse(row["present"], artifact_id)
            self.assertTrue(row["blocked"], artifact_id)
            self.assertIsNone(row["sha256"], artifact_id)

    def test_eight_rate_requirements_and_outcomes_are_blocked(self) -> None:
        rows = self.report["rate_profile"]["rows"]
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertEqual(row["status"], "blocked")
            self.assertFalse(row["qualifies"])
        outcomes = self.report["rate_outcomes"]["rows"]
        self.assertEqual(len(outcomes), 8)
        for row in outcomes:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
            self.assertFalse(row["qualifies"])

    def test_required_results_never_promote(self) -> None:
        results = self.report["required_results"]
        self.assertTrue(results["no_result_qualifies"])
        for key, value in results.items():
            if key != "no_result_qualifies":
                self.assertFalse(value, key)

    def test_report_is_canonical_and_float_free(self) -> None:
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(hashlib.sha256(text.encode("ascii")).hexdigest(),
                         digest)
        self.assertTrue(text.endswith("\n"))
        reference._no_floats(self.report)

    def test_contract_digest_matches(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_linked_row_identity_projection(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["projection"],
                         reference.board_row_projection(
                             reference.AUDIO_ROOT /
                             reference.BOARD_TASK_ROW))
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])

    def test_scope_flags_are_all_negative(self) -> None:
        scope = self.report["scope"]
        for key, value in scope.items():
            if key in ("task_local_only", "directory"):
                continue
            self.assertFalse(value, key)

    def test_no_forbidden_artifacts_in_package(self) -> None:
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(),
                             reference.FORBIDDEN_SUFFIXES, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name,
                             {"LICENSE", "LICENSE.txt", "COPYING", "NOTICE"})


class RegenerationTests(unittest.TestCase):
    def test_committed_sources_manifest_verifies(self) -> None:
        path = HERE / "SOURCES.sha256"
        self.assertTrue(path.is_file())
        reference.verify_sources_manifest(path.read_bytes())
        self.assertEqual(path.read_bytes(), run.sources_bytes())

    def test_committed_report_matches_build(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        text, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(payload, text.encode("ascii"))
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), digest + "  report.json\n")


if __name__ == "__main__":
    unittest.main()
