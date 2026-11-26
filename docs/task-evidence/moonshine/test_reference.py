# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only tests for the SDK-MOONSHINE DEFER package."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
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
            with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
                reference.read_strict_json(path)
        finally:
            path.unlink()

    def test_nonfinite_constants_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            path = self._write('{"a":' + token + "}")
            try:
                with self.assertRaisesRegex(ValueError, "nonfinite_json"):
                    reference.read_strict_json(path)
            finally:
                path.unlink()

    def test_float_and_nonobject_rejected(self) -> None:
        path = self._write('{"a":1.5}')
        try:
            with self.assertRaisesRegex(ValueError, "float_not_allowed"):
                reference.read_strict_json(path)
        finally:
            path.unlink()
        path = self._write("[1, 2]")
        try:
            with self.assertRaisesRegex(ValueError, "manifest_not_object"):
                reference.read_strict_json(path)
        finally:
            path.unlink()


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins_verify(self) -> None:
        source, boundary = reference.verify_pins()
        self.assertEqual(set(source), set(reference.SOURCE_PINS))
        self.assertEqual(set(boundary), set(reference.BOUNDARY_PINS))
        self.assertTrue(all(row["verified"] for row in source.values()))
        self.assertTrue(all(row["verified"] for row in boundary.values()))

    def test_mutable_board_is_not_pinned(self) -> None:
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)

    def test_board_projection_has_only_stable_fields(self) -> None:
        projection = reference.board_row_projection()
        self.assertEqual(tuple(sorted(projection)),
                         tuple(sorted(reference.BOARD_ROW_FIELDS)))
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["component"], reference.COMPONENT_ID)
        self.assertEqual(projection["mode"], "feasibility")
        for excluded in reference.MUTABLE_FIELDS_EXCLUDED:
            self.assertNotIn(excluded, projection)

    def test_linked_rows_include_stable_dependencies(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual([row["id"] for row in rows],
                         [reference.TASK] + list(reference.DEPENDS_ON))
        self.assertEqual(reference.linked_rows_digest(rows),
                         reference.object_digest(rows))
        self.assertEqual(reference.board_row_digest(rows[0]),
                         reference.object_digest(rows[0]))

    def test_peer_reports_are_pinned_read_only(self) -> None:
        for row in reference.PEER_EVIDENCE:
            self.assertIn(row["path"], reference.BOUNDARY_PINS)
            self.assertFalse(row["admitted_as_result"])
            self.assertFalse(row["inherited_metrics"])
            self.assertEqual(row["decision"], "DEFER")


class AbsenceTests(unittest.TestCase):
    def test_every_fixed_probe_is_absent(self) -> None:
        probes = reference.absence_probes()
        summary = reference.absence_summary(probes)
        expected = (len(reference.SOURCE_PROBE_PATHS)
                    + len(reference.WEIGHTS_PROBE_PATHS)
                    + len(reference.RUNTIME_PROBE_PATHS)
                    + len(reference.HOME_PROBE_PATHS))
        self.assertEqual(summary["probe_count"], expected)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["network_used"])
        self.assertFalse(summary["recursive_workspace_walk"])
        for row in probes:
            self.assertIs(row["present"], False, row["path"])
        self.assertIn("moonshine", json.dumps(probes).lower())


class RateArithmeticTests(unittest.TestCase):
    def _spans(self) -> list[dict]:
        return [{"start_sample": index * 1840,
                 "end_sample": index * 1840 + 1600} for index in range(8)]

    def test_exact_word_rate(self) -> None:
        result = reference.word_rate(self._spans(), 64_000, 16_000)
        self.assertEqual(result["word_count"], 8)
        self.assertEqual(result["duration_ms"], "4000.000")
        self.assertEqual(result["speech_ms"], "800.000")
        self.assertEqual(result["words_per_minute_total"], "120.000")
        self.assertEqual(result["words_per_minute_speech"], "600.000")
        self.assertEqual(result["pause_ratio"], "0.800")

    def test_rate_rejects_adverse_spans(self) -> None:
        bad = [
            ([], 64_000, 16_000),
            ([{"start_sample": 10, "end_sample": 10}], 64_000, 16_000),
            ([{"start_sample": 10, "end_sample": 20},
              {"start_sample": 15, "end_sample": 30}], 64_000, 16_000),
            ([{"start_sample": -1, "end_sample": 20}], 64_000, 16_000),
            ([{"start_sample": 0, "end_sample": 70_000}], 64_000, 16_000),
            ([{"start_sample": True, "end_sample": 20}], 64_000, 16_000),
            ([{"start_sample": 0, "end_sample": 20}], 64_000, 44_100),
            ([{"start_sample": 0, "end_sample": 20}], 64_000, 0),
        ]
        for words, total, rate in bad:
            with self.assertRaises(ValueError):
                reference.word_rate(words, total, rate)

    def test_granularity_samples(self) -> None:
        self.assertEqual(reference.granularity_samples(16_000, 5), 80)
        self.assertEqual(reference.granularity_samples(16_000, 80), 1280)
        self.assertEqual(reference.granularity_samples(48_000, 5), 240)
        with self.assertRaisesRegex(ValueError, "granularity_unsupported"):
            reference.granularity_samples(16_000, 7)

    def test_quantization_shows_coarse_overlap(self) -> None:
        spans = [{"start_sample": 0, "end_sample": 1000},
                 {"start_sample": 1120, "end_sample": 1200},
                 {"start_sample": 2000, "end_sample": 2500}]
        fine = reference.quantize_spans(
            spans, reference.granularity_samples(16_000, 5), 16_000)
        coarse = reference.quantize_spans(
            spans, reference.granularity_samples(16_000, 80), 16_000)
        self.assertFalse(fine["overlap"])
        self.assertTrue(coarse["overlap"])
        self.assertGreater(coarse["changed_span_count"],
                           fine["changed_span_count"])

    def test_granularity_control_is_synthetic_and_nonqualifying(self) -> None:
        control = reference.granularity_control()
        self.assertEqual(control["evidence_class"],
                         "synthetic_contract_control_not_evidence")
        self.assertFalse(control["qualifies"])
        summary = control["summary"]
        self.assertEqual(summary["case_count"], 4)
        self.assertEqual(summary["boundary_stable_cases"], 2)
        self.assertEqual(summary["granularity_sensitive_cases"], 2)
        self.assertEqual(summary["overlapping_quantizations"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertTrue(control["observed"]["fine_vs_coarse_rate_differ"])
        self.assertTrue(control["observed"]["aligned_identity"])
        self.assertEqual(control["observed"]["final_partial_samples"], 65)
        for case in control["cases"]:
            self.assertFalse(case["qualifies"], case["id"])
        by_id = {case["id"]: case for case in control["cases"]}
        self.assertTrue(by_id["coarse_80ms"]["quantization"]["overlap"])
        self.assertEqual(by_id["final_partial_window"]["block_count"], 11)


class AdmissionTests(unittest.TestCase):
    def test_schema_control_is_admitted_but_never_qualifies(self) -> None:
        reference.validate_manifest(reference._control_manifest())
        admission = reference.admission_controls()
        self.assertEqual(admission["summary"]["accepted_schema_controls"], 1)
        self.assertEqual(admission["summary"]["qualifying_results"], 0)
        self.assertFalse(admission["summary"]["accepted_control_qualifies"])
        accepted = [case for case in admission["cases"]
                    if case["status"] == "accepted"]
        self.assertEqual(len(accepted), 1)
        self.assertTrue(accepted[0]["synthetic_schema_control"])
        self.assertFalse(accepted[0]["qualifies"])

    def test_all_adverse_cases_are_rejected(self) -> None:
        admission = reference.admission_controls()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], 59)
        self.assertEqual(summary["rejected_count"], 58)
        self.assertTrue(summary["all_adverse_cases_rejected"])
        for case in admission["cases"]:
            if case["status"] == "rejected":
                self.assertNotIn(case["code"], ("", "none"), case["id"])
                self.assertFalse(case["qualifies"], case["id"])
                self.assertTrue(case["state_unchanged"], case["id"])
        for key in ("state_advanced_on_rejection", "runtime_invoked",
                    "weights_loaded", "audio_read", "inference_performed",
                    "network_used"):
            self.assertFalse(summary[key], key)

    def test_specific_adverse_codes(self) -> None:
        admission = reference.admission_controls()
        codes = {case["id"]: case["code"] for case in admission["cases"]}
        self.assertEqual(codes["missing-rights"], "keys")
        self.assertEqual(codes["non-offline-runtime"],
                         "runtime_not_offline")
        self.assertEqual(codes["traversal-weight-path"], "relative_path")
        self.assertEqual(codes["single-annotator"], "reference_annotators")
        self.assertEqual(codes["overlapping-words"], "word_overlap")
        self.assertEqual(codes["nonfinite-count"], "outcome_nonfinite")
        self.assertEqual(codes["self-qualified"], "outcome_self_qualified")
        self.assertEqual(codes["claims-qualified"], "rights_claims_qualified")
        self.assertEqual(codes["duplicate-json-key"], "duplicate_json_key")
        self.assertEqual(codes["nonfinite-nan"], "nonfinite_json")
        self.assertEqual(codes["root-list"], "keys")

    def test_manifest_mutation_codes_are_exact(self) -> None:
        manifest = json.loads(json.dumps(reference._control_manifest()))
        manifest["outcomes"]["pause_ratio"] = "0.500"
        with self.assertRaisesRegex(ValueError, "outcome_pause_ratio"):
            reference.validate_manifest(manifest)
        manifest = json.loads(json.dumps(reference._control_manifest()))
        manifest["controls"] = list(reversed(manifest["controls"]))
        with self.assertRaisesRegex(ValueError, "controls_order"):
            reference.validate_manifest(manifest)
        manifest = json.loads(json.dumps(reference._control_manifest()))
        manifest["hypothesis"]["words"][1]["start_sample"] = 0
        with self.assertRaisesRegex(ValueError, "word_overlap"):
            reference.validate_manifest(manifest)

    def test_rights_flags_must_all_be_true(self) -> None:
        for field in reference.RIGHTS_TRUE_FIELDS:
            manifest = json.loads(json.dumps(reference._control_manifest()))
            manifest["rights"][field] = False
            with self.assertRaisesRegex(ValueError,
                                        "rights_not_cleared:" + field):
                reference.validate_manifest(manifest)

    def test_no_engine_or_audio_is_invoked(self) -> None:
        admission = reference.admission_controls()
        contract = admission["controls"]
        self.assertFalse(contract["runtime_or_weights_invoked"])
        self.assertTrue(contract["accepted_control_is_synthetic_only"])
        self.assertFalse(contract["accepted_control_qualifies"])
        self.assertTrue(contract["unknown_fields_rejected"])
        self.assertTrue(contract["nonfinite_rejected"])
        self.assertTrue(contract["floats_rejected"])
        self.assertTrue(contract["offline_deterministic_runtime_required"])
        self.assertTrue(contract["two_independent_annotators_required"])


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_disposition(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "proposal_only_incomplete")
        self.assertEqual(self.contract["evidence_status"], "incomplete")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.contract["proposal_only"])
        self.assertTrue(self.contract["incomplete"])
        self.assertFalse(self.contract["board_file_pinned"])
        reference.validate_contract(self.contract)

    def test_report_disposition(self) -> None:
        report = self.report
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["qualification"]["qualifying_results"], 0)
        self.assertTrue(report["required_results"]["no_result_qualifies"])
        for key, value in report["required_results"].items():
            if key != "no_result_qualifies":
                self.assertFalse(value, key)

    def test_eight_blocked_release_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        for index, gate in enumerate(gates, start=1):
            self.assertEqual(gate["id"], "RG-{:02d}".format(index))
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             self.report["linked_row_identity"]["projection"])

    def test_six_open_blockers_and_eight_artifacts(self) -> None:
        blockers = self.report["exact_blockers"]
        artifacts = self.report["required_artifacts"]
        self.assertEqual(len(blockers), 6)
        self.assertEqual(len(artifacts), 8)
        artifact_ids = {row["id"] for row in artifacts}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(blocker["required_action"])
            self.assertTrue(blocker["statement"])
        for artifact in artifacts:
            self.assertFalse(artifact["present"])
            self.assertFalse(artifact["verified"])
            self.assertFalse(artifact["licensed"])
            self.assertFalse(artifact["admitted"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])
            self.assertIsNone(artifact["revision"])
            self.assertIsNone(artifact["bytes"])

    def test_eight_rate_rows_and_outcomes_are_blocked(self) -> None:
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

    def test_upstream_record_is_source_reported_only(self) -> None:
        record = self.report["upstream_record"]
        self.assertEqual(record["source_repository"], reference.SOURCE_REPOSITORY)
        self.assertEqual(record["reported_finding"], reference.REPORTED_FINDING)
        self.assertIsNone(record["source_revision"])
        self.assertIsNone(record["model_revision"])
        self.assertFalse(record["license_verified"])
        self.assertFalse(record["license_text_present"])
        self.assertTrue(record["source_reported_only"])
        self.assertFalse(record["admitted_as_result"])
        self.assertFalse(record["qualifies"])

    def test_report_is_canonical_and_float_free(self) -> None:
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(hashlib.sha256(text.encode("ascii")).hexdigest(),
                         digest)
        self.assertTrue(text.endswith("\n"))
        reference._no_floats(json.loads(text))

    def test_contract_digest_matches(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_linked_row_identity_projection(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["projection"],
                         reference.board_row_projection())
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["linked_rows"], reference.linked_rows())
        self.assertEqual(identity["linked_rows_sha256"],
                         reference.linked_rows_digest())

    def test_scope_flags_are_all_negative(self) -> None:
        scope = self.report["scope"]
        for key, value in scope.items():
            if key in ("task_local_only", "directory", "write_scope"):
                continue
            self.assertFalse(value, key)
        self.assertTrue(scope["task_local_only"])
        self.assertEqual(scope["write_scope"],
                         reference.TASK_PREFIX + " only")

    def test_public_v0_geometry_is_preserved(self) -> None:
        geometry = self.report["public_v0_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16_000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "float32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertTrue(geometry["preserved"])
        self.assertFalse(geometry["sdk_callback_invoked"])

    def test_no_forbidden_artifacts_in_package(self) -> None:
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(),
                             reference.FORBIDDEN_SUFFIXES, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name,
                             {"LICENSE", "LICENSE.txt", "COPYING", "NOTICE"})
        names = {path.name for path in HERE.iterdir() if path.is_file()}
        self.assertEqual(names, set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"})


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

    def test_committed_contract_matches_build(self) -> None:
        payload = (HERE / "contract.json").read_bytes()
        self.assertEqual(payload,
                         reference.canonical_bytes(reference.build_contract()))


if __name__ == "__main__":
    unittest.main()
