# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest suite for the SDK-PIPE-PLAYOUT package.

No network, Bungee code, native library, real audio, corpus, model, runtime,
listening session or device measurement is used. No test is skipped.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import reference
import run

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_nan_and_infinity_rejected(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
            with self.assertRaises(ValueError):
                reference.loads_strict(text)

    def test_non_object_root_rejected(self) -> None:
        for text in ("[]", "1", "null", '"x"'):
            with self.assertRaises(ValueError):
                reference.loads_strict(text)

    def test_byte_order_mark_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('\ufeff{"a":1}')

    def test_canonical_bytes_are_sorted_and_newline_terminated(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": [True, "x"]})
        self.assertEqual(payload, b'{"a":[true,"x"],"b":1}\n')

    def test_object_digest_is_stable(self) -> None:
        document = {"b": [1, 2], "a": "x"}
        self.assertEqual(reference.object_digest(document),
                         reference.object_digest({"a": "x", "b": [1, 2]}))

    def test_no_floats_rejects_float(self) -> None:
        with self.assertRaises(ValueError):
            reference._no_floats({"a": 1.5})


class PinAndBoundaryTests(unittest.TestCase):
    def test_source_pins_verify(self) -> None:
        for relative, expected in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), expected, relative)

    def test_boundary_pins_verify(self) -> None:
        for relative, expected in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), expected, relative)

    def test_board_projection_has_only_stable_fields(self) -> None:
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(tuple(row), reference.BOARD_ROW_FIELDS)
        self.assertEqual(row["id"], reference.TASK)
        for field in ("status", "owner", "claim", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertNotIn(field, row)

    def test_linked_rows_include_dependencies(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))

    def test_linked_row_digest_is_stable(self) -> None:
        first = reference.linked_rows_digest()
        second = reference.linked_rows_digest(reference.linked_rows())
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f]{64}$")

    def test_mutable_board_is_not_pinned(self) -> None:
        pins = reference.SOURCE_PINS
        self.assertNotIn(reference.BOARD_TASK_ROW, pins)
        self.assertFalse(any("TASKS.json" in name for name in pins))


class PipelineControlTests(unittest.TestCase):
    def _result(self, case_id: str) -> dict:
        for specification in reference._control_specs():
            if specification["id"] == case_id:
                return reference.run_pipeline(specification["request"])
        raise AssertionError("unknown case " + case_id)

    def test_identity_impulse_is_bit_exact(self) -> None:
        result = self._result("identity_impulse_1x")
        self.assertEqual(result["status"], "accepted_bypass")
        self.assertTrue(result["bit_exact"])
        self.assertEqual(result["delivered_samples"], 960)
        self.assertEqual(result["duration_error_samples"], 0)
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["tagged_impulse_delay_samples"], 0)
        self.assertEqual(result["bypass_reason"], "1x_passthrough")
        self.assertFalse(result["bungee_invoked"])
        self.assertFalse(result["qualifies"])

    def test_unknown_annotation_leaves_audio_unchanged(self) -> None:
        result = self._result("unknown_annotation_1_5x")
        self.assertTrue(result["bit_exact"])
        self.assertEqual(result["annotation_effect"],
                         "unknown_annotation_unchanged")
        self.assertEqual(result["bypass_reason"],
                         "bungee_runtime_not_admitted")
        self.assertEqual(result["applied_rate_ppm"], reference.BYPASS_RATE_PPM)

    def test_missing_annotation_leaves_audio_unchanged(self) -> None:
        result = self._result("missing_annotation_1_5x")
        self.assertTrue(result["bit_exact"])
        self.assertEqual(result["annotation_effect"],
                         "missing_annotation_unchanged")

    def test_rate_change_is_not_admitted(self) -> None:
        result = self._result("rate_1_25x_blocked")
        self.assertEqual(result["requested_rate_ppm"], 1_250_000)
        self.assertEqual(result["applied_rate_ppm"], 1_000_000)
        self.assertEqual(result["bypass_reason"],
                         "bungee_runtime_not_admitted")
        self.assertFalse(result["bungee_invoked"])
        self.assertIsNone(result["real_rate_path_delay_samples"])

    def test_buffer_unavailable_uses_bypass(self) -> None:
        result = self._result("buffer_unavailable_bypass")
        self.assertTrue(result["bit_exact"])
        self.assertEqual(result["bypass_reason"], "buffer_unavailable")

    def test_synthetic_speech_music_transition_are_finite(self) -> None:
        for case_id in ("speech_proxy_1x", "music_proxy_1x",
                        "transition_proxy_1x"):
            result = self._result(case_id)
            self.assertTrue(result["bit_exact"], case_id)
            self.assertTrue(result["finite_output"], case_id)
            self.assertEqual(result["gap_count"], 0, case_id)

    def test_final_partial_frame_conserved(self) -> None:
        result = self._result("final_partial_1x")
        self.assertTrue(result["bit_exact"])
        self.assertEqual(result["delivered_samples"], 3 * 160 + 37)

    def test_nonfinite_sample_rejected_without_state(self) -> None:
        result = self._result("nonfinite_rejected")
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["code"], "rejected_nonfinite_sample")
        self.assertFalse(result["finite_input"])
        self.assertFalse(result["state_advanced"])
        self.assertIsNone(result["output_sha256"])

    def test_invalid_annotation_rejected(self) -> None:
        result = self._result("invalid_annotation_rejected")
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["code"], "rejected_invalid_annotation")
        self.assertFalse(result["state_advanced"])

    def test_unsupported_annotation_rejected(self) -> None:
        result = self._result("unsupported_annotation_rejected")
        self.assertEqual(result["code"], "rejected_unsupported_annotation")

    def test_wrong_frame_length_rejected(self) -> None:
        result = self._result("wrong_frame_length_rejected")
        self.assertEqual(result["code"], "rejected_frame_length")

    def test_missing_frames_rejected(self) -> None:
        result = self._result("missing_frames_rejected")
        self.assertEqual(result["code"], "rejected_frame_count")
        self.assertFalse(result["state_advanced"])

    def test_missing_rate_rejected(self) -> None:
        result = self._result("missing_rate_rejected")
        self.assertEqual(result["code"], "rejected_rate_type")
        self.assertFalse(result["state_advanced"])

    def test_bad_geometry_rejected(self) -> None:
        result = self._result("bad_geometry_rejected")
        self.assertEqual(result["code"], "rejected_geometry")

    def test_bad_rate_rejected(self) -> None:
        result = self._result("bad_rate_rejected")
        self.assertEqual(result["code"], "rejected_rate_range")

    def test_no_control_qualifies(self) -> None:
        cases = reference.control_cases()
        self.assertEqual(len(cases), 17)
        self.assertTrue(all(case["qualifies"] is False for case in cases))
        summary = reference.control_summary(cases)
        self.assertEqual(summary["qualifying_count"], 0)
        self.assertEqual(summary["bungee_invoked_count"], 0)
        self.assertTrue(summary["all_accepted_are_bypass"])
        self.assertTrue(summary["all_rejected_state_unchanged"])
        self.assertTrue(summary["expected_status_matches"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.read_strict_json(HERE / "contract.json")
        cls.report = reference.read_strict_json(HERE / "report.json")

    def test_contract_validates(self) -> None:
        reference.validate_contract(self.contract)

    def test_machine_readable_defer_state(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.contract["qualification"]["not_qualified"])
        self.assertTrue(
            self.contract["qualification"]["all_release_gates_blocked"])

    def test_eight_blocked_release_gates(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])

    def test_artifacts_and_blockers(self) -> None:
        artifacts = self.report["required_artifacts"]
        self.assertEqual(len(artifacts), 9)
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        for artifact in artifacts[1:]:
            self.assertFalse(artifact["present"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 8)
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertTrue(blocker["required_action"])

    def test_rate_quality_and_timing_rows_blocked(self) -> None:
        for section, count in (("rate_profile", 8), ("quality_outcomes", 4),
                               ("timing", 4)):
            rows = self.report[section]["rows"]
            self.assertEqual(len(rows), count, section)
            for row in rows:
                self.assertEqual(row["status"], "blocked", section)
                self.assertIsNone(row["value"], section)

    def test_no_result_qualifies(self) -> None:
        summary = self.report["controls"]["summary"]
        self.assertEqual(summary["qualifying_count"], 0)
        self.assertEqual(summary["bungee_invoked_count"], 0)
        self.assertTrue(summary["synthetic_only"])
        self.assertFalse(summary["real_audio_read"])
        self.assertFalse(summary["listening_performed"])
        self.assertFalse(summary["device_timing_measured"])
        for case in self.report["controls"]["cases"]:
            self.assertFalse(case["qualifies"])
            self.assertFalse(case["bungee_invoked"])

    def test_source_presence_is_explicit(self) -> None:
        presence = self.report["source_presence"]
        self.assertTrue(presence["bungee_source_present"])
        self.assertTrue(presence["bungee_static_library_present"])
        self.assertFalse(presence["bungee_runtime_admitted"])
        self.assertFalse(presence["bungee_runtime_invoked"])
        self.assertFalse(presence["rights_cleared_speech_music_present"])
        self.assertFalse(presence["real_pipeline_result_present"])
        self.assertFalse(presence["audio_read"])
        self.assertFalse(presence["network_used"])

    def test_historical_context_is_provenance_only(self) -> None:
        historical = self.report["historical_context"]
        self.assertTrue(historical["provenance_only"])
        self.assertFalse(historical["reproduced_here"])
        self.assertFalse(historical["used_for_evidence"])
        self.assertFalse(historical["qualifies"])

    def test_report_is_canonical_float_free_and_sidecar_matches(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        self.assertEqual(payload, reference.canonical_bytes(self.report))
        reference._no_floats(self.report)
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_linked_row_identity_is_stable_only(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(identity["projection"]))
        self.assertEqual(identity["linked_rows_sha256"],
                         reference.linked_rows_digest(identity["linked_rows"]))

    def test_local_pins_exclude_mutable_board(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        self.assertNotIn("TASKS.json", text)
        self.assertIn("source:audio-benchmark-platform/plan/swarm/"
                      "VERIFICATION.md", text)
        self.assertIn("boundary:CONTRACTS.md", text)
        self.assertIn("boundary:docs/task-evidence/bungee-basic/report.json",
                      text)


class ColdStartTests(unittest.TestCase):
    def test_three_fresh_regenerations_are_byte_identical(self) -> None:
        names = ("contract.json", "report.json", "report.json.sha256",
                 "SOURCES.sha256")
        committed = tuple((HERE / name).read_bytes() for name in names)
        outputs: list[tuple[bytes, ...]] = []
        with tempfile.TemporaryDirectory(
                prefix="sdk-pipe-playout-test-cold-") as temporary:
            root = Path(temporary)
            for index in range(3):
                target = root / f"run-{index}"
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                           PYTHONHASHSEED=str(index + 11))
                process = subprocess.run(
                    [sys.executable, str(HERE / "run.py"),
                     "--output", str(target)],
                    cwd=HERE, capture_output=True, text=True, env=env)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertIn("byte_identical=true", process.stdout)
                outputs.append(tuple(
                    (target / name).read_bytes() for name in names))
        self.assertEqual(len(set(outputs)), 1)
        self.assertEqual(outputs[0], committed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
