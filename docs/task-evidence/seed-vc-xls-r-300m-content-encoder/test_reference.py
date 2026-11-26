# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the Seed-VC XLS-R-300M content-encoder
blocker evidence package."""

from __future__ import annotations

import json
import unittest

import reference


def valid_request() -> dict:
    return {
        "candidate": "seed_vc_xlsr_300m_content_encoder",
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "samples": [0.0] * 160,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
        "output_layer": 12,
    }


class StrictJsonTests(unittest.TestCase):
    def test_valid_object(self) -> None:
        self.assertEqual(reference.strict_json_loads('{"a":1}'), {"a": 1})

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.JsonError):
            reference.strict_json_loads('{"a":1,"a":2}')

    def test_nan_and_infinity_rejected(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}',
                     '{"a":-Infinity}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)

    def test_trailing_and_syntax_rejected(self) -> None:
        for text in ('{"a":1} extra', '{"a":}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)


class RequestValidationTests(unittest.TestCase):
    def test_valid_request_accepted(self) -> None:
        validated = reference.validate_request(valid_request())
        self.assertEqual(validated["candidate"],
                         "seed_vc_xlsr_300m_content_encoder")
        self.assertEqual(validated["output_layer"], 12)
        self.assertEqual(len(validated["samples"]), 160)

    def test_unknown_and_missing_fields_rejected(self) -> None:
        request = valid_request()
        request["extra"] = True
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(request)
        request = valid_request()
        del request["epoch"]
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(request)

    def test_nonfinite_and_out_of_range_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            request = valid_request()
            request["samples"][3] = value
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)
        request = valid_request()
        request["samples"][0] = 4.5
        with self.assertRaises(reference.InputError):
            reference.validate_request(request)

    def test_bool_and_string_samples_rejected(self) -> None:
        for value in (True, "0.0", None):
            request = valid_request()
            request["samples"][0] = value
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_geometry_and_lifecycle_rejected(self) -> None:
        cases = (
            ("sample_rate_hz", 48000),
            ("channels", 2),
            ("frame_samples", 320),
            ("epoch", -1),
            ("first_input_sample", -160),
            ("lifecycle", "drained"),
            ("execution_mode", 4),
            ("output_layer", 13),
            ("output_layer", 0),
            ("output_layer", True),
            ("candidate", "seed_vc_xlsr_300m"),
        )
        for key, value in cases:
            request = valid_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=str(key)):
                reference.validate_request(request)

    def test_short_sample_list_rejected(self) -> None:
        request = valid_request()
        request["samples"] = [0.0] * 159
        with self.assertRaises(reference.InputError):
            reference.validate_request(request)

    def test_adverse_cases_all_rejected(self) -> None:
        data = reference._adverse_cases()
        self.assertTrue(data["all_rejected"])
        self.assertEqual(data["accepted_count"], 0)
        self.assertIsNone(data["metrics"])
        self.assertGreaterEqual(data["case_count"], 20)
        self.assertTrue(all(not case["accepted"] for case in data["cases"]))

    def test_valid_request_fails_closed_without_weights(self) -> None:
        with self.assertRaises(reference.WeightsAbsent) as context:
            reference.probe_candidate(valid_request())
        self.assertEqual(context.exception.code, "WEIGHTS_ABSENT")
        self.assertIn("WEIGHTS_ABSENT", str(context.exception))


class ProbeTests(unittest.TestCase):
    def test_source_is_present_and_exactly_pinned(self) -> None:
        probe = reference.source_probe()
        self.assertTrue(probe["present"])
        self.assertEqual(probe["status"], "present_pinned")
        self.assertEqual(probe["revision"], reference.SOURCE_REVISION)
        self.assertEqual(probe["tree_digest"], reference.SOURCE_TREE_DIGEST)
        self.assertEqual(probe["file_count"], reference.SOURCE_FILE_COUNT)

    def test_weights_absent(self) -> None:
        probe = reference.weights_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_weights_absent")
        self.assertIsNone(probe["sha256"])
        self.assertIsNone(probe["byte_count"])
        self.assertEqual(probe["found"], [])

    def test_runtime_unpinned(self) -> None:
        probe = reference.runtime_probe()
        self.assertFalse(probe["pinned"])
        self.assertEqual(probe["status"], "blocked_runtime_unpinned")
        self.assertEqual(probe["lockfiles"], [])

    def test_geometry_matches_pinned_config(self) -> None:
        geom = reference.geometry()
        self.assertEqual(geom["encoder_model"],
                         "facebook/wav2vec2-xls-r-300m")
        self.assertEqual(geom["encoder_output_layer"], 12)
        self.assertEqual(geom["encoder_hidden_size"], 1024)
        self.assertEqual(geom["encoder_frame_stride_samples"], 320)
        self.assertEqual(geom["encoder_frame_rate_hz"], 50.0)
        self.assertEqual(geom["content_dim"], 384)
        self.assertEqual(geom["length_regulator_sampling_ratios"],
                         [1, 1, 1, 1])
        block = geom["one_block"]
        self.assertEqual(block["left_context_samples"], 35200)
        self.assertEqual(block["emit_samples"], 3840)
        self.assertEqual(block["right_context_samples"], 3200)
        self.assertEqual(block["total_context_samples"], 42240)
        self.assertEqual(block["diffusion_steps"], 10)
        self.assertFalse(geom["measured_here"])
        self.assertFalse(geom["candidate_output"])

    def test_frame_geometry_is_arithmetic_only(self) -> None:
        self.assertEqual(reference.frame_geometry(1600)["full_frames"], 5)
        self.assertEqual(
            reference.frame_geometry(1600)["remainder_samples"], 0)
        self.assertEqual(reference.frame_geometry(3200)["full_frames"], 10)
        self.assertEqual(
            reference.frame_geometry(3210)["remainder_samples"], 10)
        with self.assertRaises(reference.InputError):
            reference.frame_geometry(-1)
        with self.assertRaises(reference.InputError):
            reference.frame_geometry(True)

    def test_historical_artifact_is_pinned_not_reproduced(self) -> None:
        history = reference.historical_evidence()
        self.assertEqual(
            history["status"],
            "source_reported_one_block_not_reproduced")
        self.assertTrue(history["output_digest_matches_pin"])
        self.assertEqual(history["output_metadata"]["frames"], 5292)
        self.assertEqual(history["output_metadata"]["sample_rate_hz"], 22050)
        self.assertEqual(history["output_metadata"]["duration_seconds"], 0.24)
        self.assertFalse(history["log_present"])
        self.assertFalse(history["reproduced_here"])
        self.assertFalse(history["qualifies_candidate"])

    def test_board_projection_uses_stable_identity_only(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertNotIn("status", links[0])
        self.assertNotIn("owner", links[0])
        self.assertEqual(len(digest), 64)

    def test_stimulus_probe_reports_no_candidate_processing(self) -> None:
        probe = reference.stimulus_probe()
        self.assertFalse(probe["candidate_processing"])
        self.assertEqual(set(probe["stimuli"]),
                         {"silence", "impulse", "step", "sweep",
                          "speech_like"})
        self.assertTrue(all(item["nonfinite_count"] == 0
                            for item in probe["stimuli"].values()))
        self.assertTrue(all(item["byte_identical"]
                            for item in probe["identity_control"].values()))


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.payload = reference.report_bytes()

    def test_report_is_deterministic_and_canonical(self) -> None:
        self.assertEqual(reference.report_bytes(), self.payload)
        self.assertTrue(self.payload.endswith(b"\n"))
        self.assertFalse(self.payload.endswith(b"\n\n"))
        self.assertEqual(
            reference.canonical_bytes(self.report) + b"\n", self.payload)
        self.assertTrue(reference.finite_json(self.report))

    def test_blocker_semantics(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"],
                         "proposal_only_not_qualified")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["readiness"], "incomplete")
        self.assertEqual(qualification["decision"], "DEFER")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertFalse(qualification["all_required_results_present"])
        self.assertFalse(qualification["upstream_parity"])
        self.assertTrue(qualification["proposal_only"])

    def test_eight_gates_are_blocked(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-0" + str(number) for number in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(gate["reason"] for gate in gates))
        self.assertTrue(all(gate["reopen"] for gate in gates))

    def test_weights_and_runtime_are_absent(self) -> None:
        blocker = self.report["upstream_blocker"]
        self.assertEqual(blocker["status"],
                         "blocked_weights_and_runtime_absent")
        self.assertEqual(blocker["source"]["status"], "present_pinned")
        self.assertEqual(blocker["source"]["license"], "GPL-3.0")
        self.assertEqual(blocker["weights"]["status"], "absent")
        self.assertIsNone(blocker["weights"]["sha256"])
        self.assertIsNone(blocker["weights"]["byte_count"])
        self.assertEqual(blocker["runtime"]["status"], "absent_unpinned")
        self.assertIsNone(blocker["runtime_digest"])
        self.assertTrue(blocker["no_upstream_parity_claim"])

    def test_no_candidate_result_qualifies(self) -> None:
        candidate = self.report["candidates"][reference.CANDIDATE]
        self.assertEqual(candidate["status"],
                         "blocked_weights_and_runtime_absent")
        self.assertIsNone(candidate["metrics"])
        self.assertFalse(candidate["qualifies_candidate"])
        self.assertIsNone(self.report["adverse"]["missing_result"]["metrics"])
        self.assertFalse(
            self.report["adverse"]["missing_result"]["qualifies_candidate"])
        required = self.report["required_results"]
        self.assertTrue(required)
        self.assertTrue(all(value != "passed" and value != "qualified"
                            for value in required.values()))

    def test_adverse_and_json_rejections(self) -> None:
        adverse = self.report["adverse"]
        self.assertTrue(adverse["invalid_config_and_input"]["all_rejected"])
        self.assertEqual(
            adverse["invalid_config_and_input"]["accepted_count"], 0)
        self.assertTrue(adverse["invalid_json_numeric_fields"]["all_rejected"])
        self.assertEqual(
            adverse["invalid_json_numeric_fields"]["accepted_count"], 0)

    def test_local_checks_all_true(self) -> None:
        checks = self.report["local_harness_checks"]
        self.assertTrue(checks)
        self.assertTrue(all(value is True for value in checks.values()))
        self.assertGreaterEqual(len(checks), 12)


if __name__ == "__main__":
    unittest.main()
