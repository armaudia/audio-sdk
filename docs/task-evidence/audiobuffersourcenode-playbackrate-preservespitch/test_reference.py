# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the AudioBufferSourceNode DEFER package.

Standard library only, no network, no browser, no audio, no skips.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402


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
        self.assertEqual(note["line"], 81)
        self.assertEqual(note["link_line"], 320)
        self.assertTrue(note["records_browser_dependent"])
        self.assertEqual(len(note["links"]), 2)
        self.assertFalse(note["qualifies"])

    def test_source_presence_fails_closed(self) -> None:
        presence = reference.source_presence()
        self.assertTrue(presence["candidate_note_present"])
        self.assertTrue(presence["candidate_note_records_browser_dependent"])
        self.assertFalse(presence["candidate_note_is_implementation"])
        self.assertFalse(presence["browser_engine_source_present"])
        self.assertFalse(presence["web_audio_implementation_present"])
        self.assertFalse(presence["licensed_implementation_runtime_present"])
        self.assertFalse(
            presence["exact_licensed_source_weights_runtime_present"])
        self.assertFalse(presence["admitted"])
        self.assertFalse(presence["browser_launched"])
        self.assertFalse(presence["network_used"])
        self.assertFalse(presence["qualifies"])

    def test_license_findings_fail_closed(self) -> None:
        findings = reference.license_marker_probe()
        for key in ("browser_terms_reviewed", "algorithm_license_reviewed",
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


class PlaybackArithmeticTests(unittest.TestCase):
    def test_identity(self) -> None:
        mapping = reference.map_playback(16000, "1", True)
        self.assertTrue(mapping["duration_identity"])
        self.assertEqual(mapping["output_duration"], "16000")
        self.assertEqual(mapping["pitch_ratio"], "1")
        self.assertFalse(mapping["qualifies"])

    def test_faster_preserve_pitch(self) -> None:
        mapping = reference.map_playback(16000, "3/2", True)
        self.assertFalse(mapping["duration_identity"])
        self.assertEqual(mapping["output_duration"], "32000/3")
        self.assertEqual(mapping["pitch_ratio"], "1")

    def test_slower_preserve_pitch(self) -> None:
        mapping = reference.map_playback(16000, "3/4", True)
        self.assertEqual(mapping["output_duration"], "64000/3")
        self.assertEqual(mapping["pitch_ratio"], "1")

    def test_varispeed_changes_pitch(self) -> None:
        mapping = reference.map_playback(16000, "5/4", False)
        self.assertEqual(mapping["output_duration"], "12800")
        self.assertEqual(mapping["pitch_ratio"], "5/4")

    def test_rate_change_schedule_is_contiguous(self) -> None:
        mapping = reference.map_playback(16000, "1", True, [
            {"start_sample": 0, "end_sample": 4000, "rate": "1"},
            {"start_sample": 4000, "end_sample": 8000, "rate": "3/2"},
            {"start_sample": 8000, "end_sample": 16000, "rate": "3/4"},
        ])
        self.assertEqual(mapping["output_duration"], "52000/3")
        self.assertTrue(mapping["source_mapping_contiguous"])
        self.assertEqual(len(mapping["records"]), 3)

    def test_final_partial_window(self) -> None:
        mapping = reference.map_playback(16165, "1", True)
        self.assertEqual(mapping["final_partial_window"]["block_samples"], 1600)
        self.assertEqual(
            mapping["final_partial_window"]["final_window_samples"], 165)
        self.assertTrue(mapping["final_partial_window"]["partial"])

    def test_invalid_rates_rejected(self) -> None:
        for rate, code in (
                ("1/0", "playback_rate_malformed"),
                ("0", "playback_rate_out_of_range"),
                ("9", "playback_rate_out_of_range"),
                ("3/2/1", "playback_rate_malformed")):
            with self.assertRaises(ValueError) as caught:
                reference.map_playback(16000, rate, True)
            self.assertEqual(str(caught.exception), code)

    def test_boolean_and_nonfinite_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.map_playback(16000, "1", 1)
        with self.assertRaises(ValueError):
            reference.map_playback(16000, "1", True, [
                {"start_sample": 0, "end_sample": 16000, "rate": "1/0"}])

    def test_noncontiguous_schedule_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.map_playback(16000, "1", True, [
                {"start_sample": 1, "end_sample": 16000, "rate": "1"}])

    def test_incomplete_schedule_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.map_playback(16000, "1", True, [
                {"start_sample": 0, "end_sample": 8000, "rate": "1"}])

    def test_schedule_pitch_undefined_without_preservation(self) -> None:
        with self.assertRaises(ValueError):
            reference.map_playback(16000, "1", False, [
                {"start_sample": 0, "end_sample": 4000, "rate": "1"},
                {"start_sample": 4000, "end_sample": 16000, "rate": "3/2"}])


class FrameTests(unittest.TestCase):
    def test_synthetic_frame_is_finite_and_bounded(self) -> None:
        frame = reference._synthetic_frame()
        self.assertEqual(len(frame), reference.FRAME_SAMPLES)
        self.assertTrue(all(isinstance(value, float) for value in frame))
        self.assertTrue(all(math.isfinite(value) for value in frame))
        self.assertTrue(all(-1.0 <= value <= 1.0 for value in frame))
        result = reference.validate_frame(frame)
        self.assertTrue(result["finite"])
        self.assertEqual(len(result["digest_sha256"]), 64)
        self.assertFalse(result["qualifies"])

    def test_frame_control_rejects_all_adverse_vectors(self) -> None:
        control = reference.frame_control()
        summary = control["summary"]
        self.assertEqual(summary["case_count"], 12)
        self.assertEqual(summary["rejected_count"], 12)
        self.assertTrue(summary["all_rejected"])
        self.assertTrue(summary["all_codes_match"])
        self.assertEqual(summary["qualifying_results"], 0)
        for case in control["cases"]:
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertEqual(case["code"], case["expected_code"])

    def test_direct_nonfinite_rejection(self) -> None:
        frame = reference._synthetic_frame()
        for bad in (float("nan"), float("inf"), float("-inf")):
            candidate = list(frame)
            candidate[0] = bad
            with self.assertRaises(ValueError) as caught:
                reference.validate_frame(candidate)
            self.assertEqual(str(caught.exception), "frame_nonfinite")


class GateControlTests(unittest.TestCase):
    def test_gate_control_summary(self) -> None:
        control = reference.gate_control()
        self.assertEqual(control["summary"]["case_count"], 6)
        self.assertEqual(control["summary"]["identity_passes"], 2)
        self.assertEqual(control["summary"]["explicit_nonidentity_controls"], 4)
        self.assertEqual(control["summary"]["qualifying_results"], 0)
        self.assertFalse(control["summary"]["browser_launched"])
        self.assertFalse(control["summary"]["audio_read"])
        self.assertFalse(control["qualifies"])
        for case in control["cases"]:
            self.assertFalse(case["qualifies"])
            self.assertFalse(case["mapping"]["qualifies"])

    def test_gate_control_is_deterministic(self) -> None:
        self.assertEqual(reference.canonical_bytes(reference.gate_control()),
                         reference.canonical_bytes(reference.gate_control()))


class ManifestTests(unittest.TestCase):
    def test_synthetic_schema_control_is_accepted_but_not_qualified(self) -> None:
        result = reference.validate_manifest(reference._base_manifest())
        self.assertTrue(result["admitted"])
        self.assertFalse(result["qualifies"])
        self.assertEqual(result["evidence_class"],
                         "synthetic_schema_control_not_evidence")
        self.assertEqual(result["rate"], "5/4")
        self.assertEqual(result["pitch_ratio"], "1")

    def test_all_admission_mutations_rejected(self) -> None:
        admission = reference.admission_controls()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], 56)
        self.assertEqual(summary["rejected_count"], 56)
        self.assertTrue(summary["all_rejected"])
        self.assertTrue(summary["all_codes_match"])
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        for case in admission["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertEqual(case["code"], case["expected_code"])

    def test_float_and_boolean_values_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["runtime"]["sample_rate_hz"] = 48000.0
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)
        manifest = reference._base_manifest()
        manifest["mapping"]["preserves_pitch"] = 1
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_self_qualification_cannot_be_declared(self) -> None:
        manifest = reference._base_manifest()
        manifest["qualifies"] = True
        with self.assertRaises(ValueError) as caught:
            reference.validate_manifest(manifest)
        self.assertEqual(str(caught.exception), "manifest_fields")


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_disposition(self) -> None:
        reference.validate_contract(self.contract)
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(
            self.contract["disposition"]["qualifying_results"], 0)
        self.assertEqual(
            self.contract["disposition"]["blocked_release_gates"], 8)

    def test_eight_blocked_gates(self) -> None:
        gates = self.contract["release_gates"]
        self.assertEqual(len(gates), 8)
        for index, gate in enumerate(gates, start=1):
            self.assertEqual(gate["id"], f"RG-{index:02d}")
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             self.contract["linked_row_projection"])

    def test_six_open_blockers(self) -> None:
        blockers = self.contract["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        artifact_ids = {row["id"]
                        for row in self.contract["required_artifacts"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertTrue(blocker["required_action"])
            self.assertIn(blocker["artifact_id"], artifact_ids)

    def test_ten_absent_artifacts(self) -> None:
        artifacts = self.contract["required_artifacts"]
        self.assertEqual(len(artifacts), 10)
        for row in artifacts:
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertFalse(row["licensed"])
            self.assertFalse(row["admitted"])
            self.assertTrue(row["blocked"])
            self.assertIsNone(row["sha256"])

    def test_eight_rate_rows_and_outcomes(self) -> None:
        rows = self.contract["rate_profile_requirements"]
        outcomes = self.contract["rate_outcomes"]
        self.assertEqual(len(rows), 8)
        self.assertEqual(len(outcomes), 8)
        for row in rows:
            self.assertEqual(row["status"], "blocked")
            self.assertFalse(row["qualifies"])
        for row in outcomes:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
            self.assertFalse(row["qualifies"])

    def test_required_results_all_false(self) -> None:
        required = self.contract["required_results"]
        for key, value in required.items():
            if key == "no_result_qualifies":
                self.assertTrue(value)
            else:
                self.assertFalse(value, key)

    def test_board_is_not_pinned(self) -> None:
        self.assertFalse(self.contract["board_file_pinned"])
        self.assertTrue(self.contract["board_status_is_observation_only"])
        self.assertNotIn(reference.BOARD_TASK_ROW,
                         self.contract["source_pins"])
        self.assertNotIn(reference.BOARD_TASK_ROW,
                         self.contract["boundary_pins"])
        self.assertNotIn(reference.BOARD_TASK_ROW,
                         self.contract["sibling_pins"])

    def test_report_disposition_and_contract_digest(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["proposal_only"])
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_report_gates_and_controls(self) -> None:
        self.assertEqual(self.report["gates"],
                         self.contract["release_gates"])
        self.assertEqual(self.report["gate_control"],
                         reference.gate_control())
        self.assertEqual(self.report["admission"],
                         reference.admission_controls())
        self.assertEqual(self.report["required_artifacts"],
                         self.contract["required_artifacts"])
        self.assertEqual(self.report["exact_blockers"],
                         self.contract["exact_blockers"])

    def test_report_is_float_free_and_canonical(self) -> None:
        reference._no_floats(self.report)
        payload = reference.canonical_bytes(self.report)
        self.assertEqual(payload, reference.canonical_bytes(self.report))
        self.assertTrue(payload.endswith(b"\n"))

    def test_report_digest_is_deterministic(self) -> None:
        digests = {reference.canonical_report(reference.build_report())[1]
                   for _ in range(3)}
        self.assertEqual(len(digests), 1)

    def test_linked_row_identity(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["projection"],
                         self.contract["linked_row_projection"])
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(identity["projection"]))
        self.assertEqual(identity["linked_rows"],
                         [dict(row) for row in reference.LINKED_ROWS])
        self.assertEqual(identity["linked_rows_sha256"],
                         reference.linked_rows_digest())


class SourcesManifestTests(unittest.TestCase):
    def test_sources_manifest_round_trip(self) -> None:
        payload = run.sources_bytes()
        reference.verify_sources_manifest(payload)
        self.assertTrue(payload.startswith(b"# SHA-256 pins for"))
        self.assertNotIn(
            b"  " + reference.TASK_PREFIX.encode("ascii")
            + b"SOURCES.sha256\n", payload)

    def test_local_files_are_pinned(self) -> None:
        for name in reference.LOCAL_PIN_FILES:
            self.assertTrue((HERE / name).is_file(), name)


class ScopeTests(unittest.TestCase):
    def test_no_forbidden_artifacts(self) -> None:
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(),
                             reference.FORBIDDEN_SUFFIXES, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name,
                             {"CMakeLists.txt", "provider.json",
                              "adapter.json", "LICENSE", "LICENSE.txt",
                              "COPYING", "NOTICE"})

    def test_python_files_have_spdx(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(
                path.read_text(encoding="utf-8").splitlines()[:4])
            # REUSE-IgnoreStart
            self.assertIn("SPDX-License-Identifier: Apache-2.0", head)
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          head)
            # REUSE-IgnoreEnd

    def test_task_prefix_is_local(self) -> None:
        self.assertEqual(reference.TASK_PREFIX,
                         "docs/task-evidence/"
                         "audiobuffersourcenode-playbackrate-preservespitch/")
        self.assertEqual(reference.HERE.as_posix(),
                         (reference.WORKTREE / reference.TASK_PREFIX
                          ).as_posix().rstrip("/"))


class DigestTests(unittest.TestCase):
    def test_report_sidecar_after_generation(self) -> None:
        report_path = HERE / "report.json"
        sidecar_path = HERE / "report.json.sha256"
        self.assertTrue(report_path.is_file())
        self.assertTrue(sidecar_path.is_file())
        digest = hashlib.sha256(report_path.read_bytes()).hexdigest()
        self.assertEqual(sidecar_path.read_text(encoding="ascii"),
                         f"{digest}  report.json\n")

    def test_contract_json_matches_rebuild(self) -> None:
        contract_path = HERE / "contract.json"
        self.assertTrue(contract_path.is_file())
        committed = contract_path.read_bytes()
        self.assertEqual(committed,
                         reference.canonical_bytes(
                             reference.build_contract()))


if __name__ == "__main__":
    unittest.main()
