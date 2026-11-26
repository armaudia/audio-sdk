# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the AVAudioUnitTimePitch DEFER package.

Standard library only, no network, no Apple framework, no Audio Unit, no
AVAudioEngine, no audio and no skips.
"""

from __future__ import annotations

import hashlib
import json
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
        self.assertIn("SDK-GRANULAR-TSM", tasks)
        self.assertIn("SDK-COREAUDIO-AUDIOUNIT-DUPLEX-HOST", tasks)
        self.assertIn("SDK-SURVEY-TRN-02", tasks)


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
        self.assertEqual(note["line"], 78)
        self.assertEqual(note["section_line"], 300)
        self.assertEqual(note["link_line"], 302)
        self.assertTrue(note["records_closed_source"])
        self.assertTrue(note["records_os_variation"])
        self.assertTrue(note["rate_range_recorded"])
        self.assertTrue(note["pitch_unit_recorded"])
        self.assertTrue(note["overlap_recorded"])
        self.assertTrue(note["records_os_platform_licence"])
        self.assertEqual(len(note["links"]), 1)
        self.assertFalse(note["qualifies"])

    def test_source_presence_fails_closed(self) -> None:
        presence = reference.source_presence()
        self.assertTrue(presence["candidate_note_present"])
        self.assertTrue(presence["candidate_note_records_closed_source"])
        self.assertTrue(presence["candidate_note_records_os_variation"])
        self.assertFalse(presence["candidate_note_is_implementation"])
        self.assertFalse(presence["apple_runtime_manifest_present"])
        self.assertFalse(presence["implementation_source_present"])
        self.assertFalse(presence["audio_unit_host_present"])
        self.assertFalse(presence["licensed_implementation_runtime_present"])
        self.assertFalse(
            presence["exact_licensed_source_weights_runtime_present"])
        self.assertFalse(presence["admitted"])
        self.assertFalse(presence["framework_loaded"])
        self.assertFalse(presence["audio_unit_instantiated"])
        self.assertFalse(presence["audio_engine_launched"])
        self.assertFalse(presence["network_used"])
        self.assertFalse(presence["qualifies"])

    def test_license_findings_fail_closed(self) -> None:
        findings = reference.license_marker_probe()
        for key in ("apple_platform_terms_present", "apple_sdk_license_present",
                    "implementation_source_license_present",
                    "platform_terms_reviewed", "apple_sdk_license_reviewed",
                    "redistribution_approved", "commercial_use_approved",
                    "output_use_defined", "qualifies"):
            self.assertFalse(findings[key], key)

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
        mapping = reference.map_timeline(16000, "1", 0, "8")
        self.assertTrue(mapping["duration_identity"])
        self.assertEqual(mapping["output_duration"], "16000")
        self.assertEqual(mapping["pitch_ratio"], "1")
        self.assertFalse(mapping["overlap_effect_modeled"])
        self.assertFalse(mapping["qualifies"])

    def test_rate_two(self) -> None:
        mapping = reference.map_timeline(16000, "2", 0, "8")
        self.assertEqual(mapping["output_duration"], "8000")
        self.assertEqual(mapping["output_duration_samples_floor"], 8000)
        self.assertFalse(mapping["duration_identity"])

    def test_rate_half(self) -> None:
        mapping = reference.map_timeline(16000, "1/2", 0, "8")
        self.assertEqual(mapping["output_duration"], "32000")

    def test_pitch_octave_up(self) -> None:
        mapping = reference.map_timeline(16000, "1", 1200, "8")
        self.assertEqual(mapping["pitch_ratio"], "2")
        self.assertEqual(mapping["output_duration"], "16000")

    def test_pitch_octave_down(self) -> None:
        mapping = reference.map_timeline(16000, "1", -1200, "8")
        self.assertEqual(mapping["pitch_ratio"], "0.5")

    def test_pitch_ratio_independent_of_rate(self) -> None:
        fast = reference.map_timeline(16000, "3/2", -700, "8")
        slow = reference.map_timeline(16000, "3/4", -700, "8")
        self.assertEqual(fast["pitch_ratio"], slow["pitch_ratio"])
        self.assertEqual(fast["pitch_ratio"], "0.667419927085")

    def test_combined_rate_and_pitch(self) -> None:
        mapping = reference.map_timeline(16000, "3/2", -700, "8")
        self.assertEqual(mapping["output_duration"], "32000/3")
        self.assertEqual(mapping["output_duration_samples_floor"], 10666)
        self.assertEqual(mapping["output_duration_samples_ceil"], 10667)
        self.assertFalse(mapping["duration_identity"])

    def test_overlap_is_recorded_not_modeled(self) -> None:
        low = reference.map_timeline(16000, "1", 0, "3")
        high = reference.map_timeline(16000, "1", 0, "32")
        self.assertEqual(low["output_duration"], high["output_duration"])
        self.assertFalse(low["overlap_effect_modeled"])
        self.assertNotEqual(low["overlap"], high["overlap"])

    def test_rate_change_schedule_is_contiguous(self) -> None:
        mapping = reference.map_timeline(16000, "1", 0, "8", [
            {"start_sample": 0, "end_sample": 4000, "rate": "1"},
            {"start_sample": 4000, "end_sample": 8000, "rate": "3/2"},
            {"start_sample": 8000, "end_sample": 16000, "rate": "3/4"},
        ])
        self.assertEqual(mapping["output_duration"], "52000/3")
        self.assertTrue(mapping["source_mapping_contiguous"])
        self.assertEqual(len(mapping["records"]), 3)

    def test_final_partial_window(self) -> None:
        mapping = reference.map_timeline(16165, "1", 0, "8")
        self.assertEqual(mapping["final_partial_window"]["block_samples"], 1600)
        self.assertEqual(
            mapping["final_partial_window"]["final_window_samples"], 165)
        self.assertTrue(mapping["final_partial_window"]["partial"])

    def test_rate_bounds(self) -> None:
        self.assertEqual(
            reference.map_timeline(16000, "1/32", 0, "8")["output_duration"],
            "512000")
        for rate, code in (
                ("1/0", "rate_malformed"),
                ("0", "rate_out_of_range"),
                ("33", "rate_out_of_range"),
                ("3/2/1", "rate_malformed")):
            with self.assertRaises(ValueError) as caught:
                reference.map_timeline(16000, rate, 0, "8")
            self.assertEqual(str(caught.exception), code)

    def test_pitch_bounds_and_types(self) -> None:
        self.assertEqual(
            reference.map_timeline(16000, "1", 2400, "8")["pitch_ratio"], "4")
        self.assertEqual(
            reference.map_timeline(16000, "1", -2400, "8")["pitch_ratio"],
            "0.25")
        for cents, code in (
                (2401, "pitch_cents_out_of_range"),
                (-2401, "pitch_cents_out_of_range"),
                (0.0, "pitch_cents_not_int"),
                (True, "pitch_cents_not_int")):
            with self.assertRaises(ValueError) as caught:
                reference.map_timeline(16000, "1", cents, "8")
            self.assertEqual(str(caught.exception), code)

    def test_overlap_bounds(self) -> None:
        for value, code in (
                ("2", "overlap_out_of_range"),
                ("33", "overlap_out_of_range"),
                ("1/0", "overlap_malformed")):
            with self.assertRaises(ValueError) as caught:
                reference.map_timeline(16000, "1", 0, value)
            self.assertEqual(str(caught.exception), code)


class ControlTests(unittest.TestCase):
    def test_gate_control_summary(self) -> None:
        control = reference.gate_control()
        self.assertEqual(control["summary"]["case_count"], 10)
        self.assertEqual(control["summary"]["identity_passes"], 5)
        self.assertEqual(control["summary"]["qualifying_results"], 0)
        for case in control["cases"]:
            self.assertFalse(case["qualifies"])
            self.assertFalse(case["mapping"]["qualifies"])

    def test_frame_control_rejects_all(self) -> None:
        frame = reference.frame_control()
        self.assertEqual(frame["summary"]["case_count"], 12)
        self.assertEqual(frame["summary"]["rejected_count"], 12)
        self.assertTrue(frame["summary"]["all_codes_match"])
        self.assertFalse(frame["summary"]["audio_read"])

    def test_admission_rejects_all(self) -> None:
        admission = reference.admission_controls()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], len(reference._mutations()))
        self.assertEqual(summary["rejected_count"], summary["case_count"])
        self.assertTrue(summary["all_rejected"])
        self.assertTrue(summary["all_codes_match"])
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["framework_loaded"])
        self.assertFalse(summary["audio_unit_instantiated"])
        self.assertFalse(summary["network_used"])

    def test_manifest_control_is_schema_only(self) -> None:
        admission = reference.admission_controls()
        control = admission["control"]
        self.assertTrue(control["accepted"])
        self.assertTrue(control["admitted"])
        self.assertFalse(control["qualifies"])
        self.assertEqual(control["rate"], "5/4")
        self.assertEqual(control["pitch_cents"], -700)
        self.assertEqual(control["pitch_ratio"], "0.667419927085")


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
                    "required_artifacts", "exact_blockers", "required_results",
                    "reproduction"):
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
        required = report["required_results"]
        self.assertTrue(required.pop("no_result_qualifies"))
        self.assertFalse(any(required.values()))

    def test_documented_envelope_is_not_a_spec(self) -> None:
        report = reference.read_strict_json(REPORT)
        envelope = report["documented_parameter_envelope"]
        self.assertTrue(envelope["link_recorded"])
        self.assertIsNone(envelope["rate"]["default"])
        self.assertEqual(envelope["rate"]["min"], "0.03125")
        self.assertEqual(envelope["rate"]["max"], "32")
        self.assertIsNone(envelope["pitch"]["min"])
        self.assertIsNone(envelope["overlap"]["min"])
        self.assertEqual(envelope["overlap"]["unit"], "unrecorded")
        self.assertFalse(envelope["defaults_recorded_in_candidate_note"])
        self.assertFalse(envelope["semantics_verified_here"])
        self.assertFalse(envelope["qualifies"])
        synthetic = report["synthetic_control_envelope"]
        self.assertEqual(synthetic["rate_min"], "1/32")
        self.assertEqual(synthetic["pitch_cents_min"], -2400)
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
