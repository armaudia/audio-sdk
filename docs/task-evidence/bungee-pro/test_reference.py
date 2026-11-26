# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the Bungee Pro DEFER package.

Standard library only, no network, no vendor SDK, no runtime, no audio and no
skips.
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "doc.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_nonfinite_constant_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "doc.json"
                path.write_text('{"a":' + token + "}", encoding="utf-8")
                with self.assertRaises(ValueError):
                    reference.read_strict_json(path)

    def test_float_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "doc.json"
            path.write_text('{"a":1.5}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_canonical_is_sorted_ascii_with_newline(self) -> None:
        payload = reference.canonical_bytes({"b": 2, "a": "1×"})
        self.assertTrue(payload.endswith(b"\n"))
        self.assertIn(b'\\u00d7', payload)
        self.assertLess(payload.index(b'"a"'), payload.index(b'"b"'))
        self.assertEqual(reference.canonical_bytes({"b": 2, "a": "1×"}),
                         payload)

    def test_no_floats_rejects_nested(self) -> None:
        with self.assertRaises(ValueError):
            reference._no_floats({"a": [1, {"b": 2.0}]})


class BoardIdentityTests(unittest.TestCase):
    def test_projection_has_only_stable_fields(self) -> None:
        projection = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(set(projection), set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["component"], reference.COMPONENT_ID)
        self.assertEqual(projection["mode"], reference.MODE)
        self.assertNotIn("status", projection)
        self.assertNotIn("claim", projection)
        self.assertNotIn("review", projection)

    def test_projection_digest_deterministic(self) -> None:
        projection = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        first = reference.board_row_digest(projection)
        second = reference.board_row_digest(dict(projection))
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_mutable_board_never_pinned(self) -> None:
        for pins in (reference.SOURCE_PINS, reference.BOUNDARY_PINS,
                     reference.SIBLING_PINS):
            self.assertNotIn(reference.BOARD_TASK_ROW, pins)

    def test_linked_rows_digest_deterministic(self) -> None:
        self.assertEqual(reference.linked_rows_digest(),
                         reference.linked_rows_digest())
        self.assertEqual(len(reference.linked_rows_digest()), 64)
        tasks = {row["task"] for row in reference.LINKED_ROWS}
        self.assertIn("SDK-BUNGEE-BASIC", tasks)
        self.assertIn("SDK-SIGNALSMITH-STRETCH", tasks)
        self.assertIn("SDK-SOUNDTOUCH", tasks)


class PinTests(unittest.TestCase):
    def test_all_pins_verify(self) -> None:
        source, boundary, sibling = reference.verify_pins()
        self.assertEqual(len(source), len(reference.SOURCE_PINS))
        self.assertEqual(len(boundary), len(reference.BOUNDARY_PINS))
        self.assertEqual(len(sibling), len(reference.SIBLING_PINS))
        for group in (source, boundary, sibling):
            for row in group.values():
                self.assertTrue(row["verified"])
                self.assertEqual(row["sha256"], row["actual"])

    def test_candidate_note_is_pinned(self) -> None:
        self.assertIn(reference.CANDIDATE_NOTE, reference.SOURCE_PINS)

    def test_candidate_note_provenance(self) -> None:
        note = reference.candidate_note_probe()
        self.assertTrue(note["present"])
        self.assertEqual(note["line"], 67)
        self.assertEqual(note["section_line"], 222)
        self.assertTrue(note["records_commercial_licence"])
        self.assertTrue(note["records_proprietary_algorithms"])
        self.assertTrue(note["records_simd_targets"])
        self.assertTrue(note["records_professional_support"])
        self.assertTrue(note["records_basic_repository_link"])
        self.assertFalse(note["records_pro_dedicated_link"])
        self.assertTrue(note["records_latency_as_similar_to_basic"])
        self.assertTrue(note["records_no_local_evaluation"])
        self.assertTrue(
            note["records_no_pricing_terms_or_patent_indemnity"])
        self.assertTrue(note["records_upgrade_path"])
        self.assertFalse(note["implementation_source_recorded"])
        self.assertFalse(note["api_identity_recorded"])
        self.assertFalse(note["numeric_bounds_recorded"])
        self.assertFalse(note["qualifies"])

    def test_source_presence_fails_closed(self) -> None:
        presence = reference.source_presence()
        self.assertTrue(presence["candidate_note_present"])
        self.assertTrue(
            presence["candidate_note_records_proprietary_algorithms"])
        self.assertTrue(
            presence["candidate_note_records_commercial_licence"])
        self.assertTrue(
            presence["candidate_note_records_no_local_evaluation"])
        self.assertFalse(presence["candidate_note_is_implementation"])
        self.assertFalse(presence["pro_artifact_present"])
        self.assertEqual(presence["present_probes"], [])
        self.assertFalse(presence["implementation_source_present"])
        self.assertFalse(presence["runtime_manifest_present"])
        self.assertFalse(presence["license_text_present"])
        self.assertFalse(presence["license_key_present"])
        self.assertFalse(presence["vendor_artifact_present"])
        self.assertFalse(presence["licensed_implementation_runtime_present"])
        self.assertFalse(
            presence["exact_licensed_source_weights_runtime_present"])
        self.assertFalse(presence["admitted"])
        self.assertFalse(presence["network_used"])
        self.assertFalse(presence["download_attempted"])
        self.assertFalse(presence["runtime_imported"])
        self.assertFalse(presence["qualifies"])

    def test_license_findings_fail_closed(self) -> None:
        findings = reference.license_findings()
        self.assertTrue(
            findings["candidate_note_records_commercial_licence"])
        self.assertTrue(
            findings["candidate_note_records_no_pricing_terms"])
        for key in ("pro_license_text_present",
                    "executed_agreement_present", "pricing_terms_present",
                    "patent_indemnity_reviewed", "terms_reviewed",
                    "redistribution_approved",
                    "derivative_output_use_approved",
                    "commercial_use_approved", "output_use_defined",
                    "qualifies"):
            self.assertFalse(findings[key], key)

    def test_basic_is_not_a_substitute(self) -> None:
        guard = reference.basic_substitution_guard()
        self.assertFalse(guard["basic_is_pro"])
        self.assertFalse(guard["basic_used_here"])
        self.assertFalse(guard["substitution_allowed"])
        self.assertEqual(guard["basic_license"], "MPL-2.0")

    def test_profile_phrases_exist_in_rate_row(self) -> None:
        text = (reference.AUDIO_ROOT /
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
                ).read_text(encoding="utf-8")
        rows = [line for line in text.splitlines()
                if line.startswith("| Rate |")]
        self.assertEqual(len(rows), 1)
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, rows[0])


class ArithmeticTests(unittest.TestCase):
    def test_identity(self) -> None:
        mapping = reference.map_timeline(16000, "1")
        self.assertTrue(mapping["duration_identity"])
        self.assertEqual(mapping["output_duration"], "16000")
        self.assertEqual(mapping["pitch_ratio"], "1")
        self.assertFalse(mapping["qualifies"])

    def test_rate_two(self) -> None:
        mapping = reference.map_timeline(16000, "2")
        self.assertEqual(mapping["output_duration"], "8000")
        self.assertEqual(mapping["output_samples_floor"], 8000)
        self.assertFalse(mapping["duration_identity"])

    def test_rate_half(self) -> None:
        mapping = reference.map_timeline(16000, "1/2")
        self.assertEqual(mapping["output_duration"], "32000")

    def test_pitch_octave_up(self) -> None:
        mapping = reference.map_timeline(16000, "1", 1200)
        self.assertEqual(mapping["pitch_ratio"], "2")
        self.assertEqual(mapping["output_duration"], "16000")
        self.assertFalse(mapping["pitch_preserved"])

    def test_pitch_octave_down(self) -> None:
        mapping = reference.map_timeline(16000, "1", -1200)
        self.assertEqual(mapping["pitch_ratio"], "0.5")

    def test_pitch_ratio_independent_of_rate(self) -> None:
        fast = reference.map_timeline(16000, "3/2", -700)
        slow = reference.map_timeline(16000, "3/4", -700)
        self.assertEqual(fast["pitch_ratio"], slow["pitch_ratio"])
        self.assertEqual(fast["pitch_ratio"], "0.667419927085")

    def test_combined_rate_and_pitch(self) -> None:
        mapping = reference.map_timeline(16000, "3/2", -700)
        self.assertEqual(mapping["output_duration"], "32000/3")
        self.assertEqual(mapping["output_samples_floor"], 10666)
        self.assertEqual(mapping["output_samples_ceil"], 10667)
        self.assertFalse(mapping["duration_identity"])

    def test_rate_change_schedule_is_contiguous(self) -> None:
        mapping = reference.map_timeline(16000, "1", 0, [
            {"start_sample": 0, "end_sample": 4000, "rate": "1"},
            {"start_sample": 4000, "end_sample": 8000, "rate": "3/2"},
            {"start_sample": 8000, "end_sample": 16000, "rate": "3/4"},
        ])
        self.assertEqual(mapping["output_duration"], "52000/3")
        self.assertTrue(mapping["source_mapping_contiguous"])
        self.assertEqual(len(mapping["records"]), 3)

    def test_final_partial_window(self) -> None:
        mapping = reference.map_timeline(16165, "1")
        self.assertEqual(mapping["final_partial_window"]["block_samples"],
                         1600)
        self.assertEqual(
            mapping["final_partial_window"]["final_window_samples"], 165)
        self.assertTrue(mapping["final_partial_window"]["partial"])

    def test_rate_bounds(self) -> None:
        self.assertEqual(
            reference.map_timeline(16000, "1/4")["output_duration"],
            "64000")
        self.assertEqual(
            reference.map_timeline(16000, "4")["output_duration"], "4000")
        for rate, code in (
                ("1/0", "rate_malformed"),
                ("0", "rate_out_of_range"),
                ("5", "rate_out_of_range"),
                ("1/32", "rate_out_of_range"),
                ("3/2/1", "rate_malformed")):
            with self.assertRaises(ValueError) as caught:
                reference.map_timeline(16000, rate)
            self.assertEqual(str(caught.exception), code)

    def test_pitch_bounds_and_types(self) -> None:
        self.assertEqual(
            reference.map_timeline(16000, "1", 2400)["pitch_ratio"], "4")
        self.assertEqual(
            reference.map_timeline(16000, "1", -2400)["pitch_ratio"], "0.25")
        for cents, code in (
                (2401, "pitch_cents_out_of_range"),
                (-2401, "pitch_cents_out_of_range"),
                (0.0, "pitch_cents_not_int"),
                (True, "pitch_cents_not_int")):
            with self.assertRaises(ValueError) as caught:
                reference.map_timeline(16000, "1", cents)
            self.assertEqual(str(caught.exception), code)

    def test_schedule_rejections(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.map_timeline(16000, "1", 0, [
                {"start_sample": 0, "end_sample": 4000, "rate": "1"},
                {"start_sample": 4001, "end_sample": 16000, "rate": "1"},
            ])
        self.assertEqual(str(caught.exception), "schedule_not_contiguous")
        with self.assertRaises(ValueError) as caught:
            reference.map_timeline(16000, "1", 0, [
                {"start_sample": 0, "end_sample": 8000, "rate": "1"},
            ])
        self.assertEqual(str(caught.exception),
                         "schedule_does_not_cover_source")


class ControlTests(unittest.TestCase):
    def test_gate_control_summary(self) -> None:
        control = reference.gate_control()
        self.assertEqual(control["summary"]["case_count"], 10)
        self.assertEqual(control["summary"]["arithmetic_passes"], 10)
        self.assertTrue(control["summary"]["identity_1x_exact"])
        self.assertTrue(control["summary"]["final_partial_detected"])
        self.assertTrue(control["summary"]["rate_change_contiguous"])
        self.assertEqual(control["summary"]["qualifying_results"], 0)
        self.assertFalse(control["summary"]["vendor_sdk_loaded"])
        self.assertFalse(control["summary"]["network_used"])
        for case in control["cases"]:
            self.assertFalse(case["qualifies"])
            self.assertFalse(case["mapping"]["qualifies"])

    def test_frame_control_rejects_all_invalid(self) -> None:
        frame = reference.frame_control()
        self.assertEqual(frame["summary"]["case_count"], 12)
        self.assertEqual(frame["summary"]["accepted_count"], 1)
        self.assertEqual(frame["summary"]["rejected_count"], 11)
        self.assertTrue(frame["summary"]["all_codes_match"])
        self.assertFalse(frame["summary"]["audio_read"])
        self.assertFalse(frame["summary"]["vendor_runtime_invoked"])

    def test_admission_rejects_all(self) -> None:
        admission = reference.admission_controls()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], len(reference._mutations()))
        self.assertEqual(summary["case_count"], 55)
        self.assertEqual(summary["rejected_count"], summary["case_count"])
        self.assertTrue(summary["all_rejected"])
        self.assertTrue(summary["all_codes_match"])
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["vendor_sdk_loaded"])
        self.assertFalse(summary["vendor_runtime_invoked"])
        self.assertFalse(summary["network_used"])

    def test_manifest_control_is_schema_only(self) -> None:
        admission = reference.admission_controls()
        control = admission["control"]
        self.assertTrue(control["accepted"])
        self.assertTrue(control["schema_valid"])
        self.assertTrue(control["rights_complete"])
        self.assertFalse(control["artifact_present"])
        self.assertFalse(control["admitted"])
        self.assertFalse(control["qualifies"])
        self.assertEqual(control["rate"], "5/4")
        self.assertEqual(control["output_duration_samples"], 12800)


class ContractAndReportTests(unittest.TestCase):
    def test_contract_is_canonical_and_strict(self) -> None:
        contract = reference.read_strict_json(CONTRACT)
        reference.validate_contract(contract)
        self.assertEqual(CONTRACT.read_bytes(),
                         reference.canonical_bytes(contract))

    def test_report_is_canonical_and_strict(self) -> None:
        report = reference.read_strict_json(REPORT)
        self.assertEqual(REPORT.read_bytes(), reference.canonical_bytes(report))
        self.assertFalse(any(isinstance(value, float)
                             for value in _walk(report)))

    def test_report_sidecar(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="ascii"),
                         f"{digest}  report.json\n")

    def test_contract_digest_in_report(self) -> None:
        contract = reference.read_strict_json(CONTRACT)
        report = reference.read_strict_json(REPORT)
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))
        for key in ("disposition", "qualification", "scope", "boundary",
                    "public_v0_geometry", "non_claims", "observed_provenance",
                    "documented_parameter_envelope",
                    "synthetic_control_envelope", "required_artifacts",
                    "exact_blockers", "required_results", "reproduction",
                    "basic_substitution_guard", "vendor_record"):
            self.assertEqual(report[key], contract[key], key)
        self.assertEqual(report["gates"], contract["release_gates"])

    def test_report_disposition_and_gates(self) -> None:
        report = reference.read_strict_json(REPORT)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(len(report["gates"]), 8)
        self.assertEqual(len(report["exact_blockers"]), 6)
        self.assertEqual(len(report["required_artifacts"]), 10)
        for index, gate in enumerate(report["gates"], start=1):
            self.assertEqual(gate["id"], f"RG-{index:02d}")
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
        for row in report["rate_profile"]["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertFalse(row["qualifies"])
        for row in report["rate_outcomes"]["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
            self.assertFalse(row["qualifies"])
        required = dict(report["required_results"])
        self.assertTrue(required.pop("no_result_qualifies"))
        self.assertFalse(any(required.values()))

    def test_documented_envelope_is_not_a_spec(self) -> None:
        report = reference.read_strict_json(REPORT)
        envelope = report["documented_parameter_envelope"]
        self.assertTrue(envelope["commercial_upgrade_recorded"])
        self.assertTrue(envelope["proprietary_algorithms_recorded"])
        self.assertIsNone(envelope["rate"]["min"])
        self.assertIsNone(envelope["rate"]["max"])
        self.assertIsNone(envelope["rate"]["default"])
        self.assertIsNone(envelope["pitch"]["min"])
        self.assertFalse(envelope["api_identity_recorded"])
        self.assertFalse(envelope["numeric_bounds_recorded_in_candidate_note"])
        self.assertFalse(envelope["local_evaluation_recorded"])
        self.assertFalse(envelope["semantics_verified_here"])
        self.assertFalse(envelope["qualifies"])
        synthetic = report["synthetic_control_envelope"]
        self.assertEqual(synthetic["rate_min"], "1/4")
        self.assertEqual(synthetic["pitch_cents_min"], -1200)
        self.assertFalse(synthetic["qualifies"])

    def test_sources_manifest_rebuilds(self) -> None:
        payload = PINS.read_bytes()
        reference.verify_sources_manifest(payload)
        self.assertEqual(payload, run.sources_bytes())
        names = {
            line.split("  ", 1)[1]
            for line in payload.decode("ascii").splitlines()
            if line and not line.startswith("#")
        }
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", names)
        self.assertNotIn(reference.BOARD_TASK_ROW,
                         payload.decode("ascii"))


def _walk(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)
    else:
        yield value


if __name__ == "__main__":
    unittest.main()
