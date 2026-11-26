# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the SDK-AFC-SPEX blocker evidence package."""

from __future__ import annotations

import copy
import json
import unittest

import reference


def valid_request() -> dict:
    return {
        "candidate": "afc_spex_three_channel",
        "sample_rate_hz": 16000,
        "channels": 3,
        "frame_samples": 160,
        "samples": [0.0] * 480,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
    }


def board_with(**changes) -> dict:
    row = {
        "id": "SDK-AFC-SPEX",
        "title": "AFC-SPEX",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "component": "afc-spex",
        "status": "in_progress",
        "owner": "agent-AFC-SPEX",
        "history": ["mutable"],
    }
    row.update(changes)
    return {"tasks": [{"id": "SDK-OTHER", "title": "Other",
                       "mode": "implementation", "status": "done"}, row]}


class StrictJsonTests(unittest.TestCase):
    def test_valid_object(self) -> None:
        self.assertEqual(reference.strict_json_loads('{"a":1}'), {"a": 1})

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.JsonError):
            reference.strict_json_loads('{"a":1,"a":2}')

    def test_nan_and_infinity_rejected(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)

    def test_trailing_and_syntax_rejected(self) -> None:
        for text in ('{"a":1} extra', '{"a":}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)


class RequestValidationTests(unittest.TestCase):
    def test_valid_request_accepted(self) -> None:
        validated = reference.validate_request(valid_request())
        self.assertEqual(validated["candidate"], "afc_spex_three_channel")
        self.assertEqual(validated["channels"], 3)
        self.assertEqual(len(validated["samples"]), 480)

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

    def test_geometry_lifecycle_and_mode_rejected(self) -> None:
        cases = (
            ("sample_rate_hz", 0),
            ("sample_rate_hz", -16000),
            ("sample_rate_hz", True),
            ("channels", 1),
            ("channels", 2),
            ("channels", 4),
            ("frame_samples", 0),
            ("frame_samples", 4097),
            ("epoch", -1),
            ("epoch", True),
            ("first_input_sample", -160),
            ("lifecycle", "closed"),
            ("lifecycle", "drained"),
            ("execution_mode", 4),
            ("execution_mode", True),
            ("candidate", "afc_spex"),
        )
        for key, value in cases:
            request = valid_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=str(key)):
                reference.validate_request(request)

    def test_wrong_sample_count_rejected(self) -> None:
        for count in (159, 160, 479, 481):
            request = valid_request()
            request["samples"] = [0.0] * count
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_adverse_cases_all_rejected(self) -> None:
        data = reference._adverse_cases()
        self.assertTrue(data["all_rejected"])
        self.assertEqual(data["accepted_count"], 0)
        self.assertIsNone(data["metrics"])
        self.assertGreaterEqual(data["case_count"], 25)
        self.assertTrue(all(not case["accepted"] for case in data["cases"]))

    def test_valid_request_fails_closed_without_artifacts(self) -> None:
        with self.assertRaises(reference.ArtifactsAbsent) as context:
            reference.probe_candidate(valid_request())
        self.assertEqual(context.exception.code, "ARTIFACTS_ABSENT")
        admitted = reference.admit(valid_request())
        self.assertEqual(admitted["status"], "DEFER")
        self.assertFalse(admitted["admissible"])
        self.assertFalse(admitted["candidate_processing"])
        self.assertFalse(admitted["qualifies_candidate"])
        self.assertIsNone(admitted["metrics"])
        self.assertIn("source_absent", admitted["blockers"])
        self.assertIn("checkpoint_absent", admitted["blockers"])
        self.assertIn("three_channel_matched_input_absent",
                      admitted["blockers"])


class ProbeTests(unittest.TestCase):
    def test_source_absent(self) -> None:
        probe = reference.source_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_source_absent")
        self.assertIsNone(probe["revision"])
        self.assertIsNone(probe["tree_digest"])
        self.assertIsNone(probe["license"])
        self.assertEqual(probe["found"], [])

    def test_checkpoint_absent(self) -> None:
        probe = reference.checkpoint_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_checkpoint_absent")
        self.assertIsNone(probe["sha256"])
        self.assertIsNone(probe["byte_count"])
        self.assertIsNone(probe["license"])
        self.assertFalse(probe["terms_recorded"])
        self.assertEqual(probe["found"], [])

    def test_three_channel_input_absent(self) -> None:
        probe = reference.input_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"],
                         "blocked_three_channel_input_absent")
        self.assertEqual(probe["required_channels"], 3)
        self.assertIsNone(probe["sample_rate_hz"])
        self.assertIsNone(probe["hop_samples"])
        self.assertFalse(probe["corpus_rights"])
        self.assertFalse(probe["mono_pilot_compatible"])

    def test_runtime_unpinned(self) -> None:
        probe = reference.runtime_probe()
        self.assertFalse(probe["pinned"])
        self.assertEqual(probe["status"], "blocked_runtime_unpinned")
        self.assertEqual(probe["lockfiles"], [])

    def test_rights_blocked(self) -> None:
        probe = reference.rights_probe()
        self.assertEqual(probe["status"], "blocked_rights_unrecorded")
        self.assertEqual(probe["review"], "blocked")
        self.assertIsNone(probe["source_license"])
        self.assertFalse(probe["checkpoint_terms_recorded"])
        self.assertFalse(probe["input_corpus_rights"])

    def test_geometry_is_not_invented(self) -> None:
        geom = reference.geometry()
        self.assertEqual(geom["declared_input_channels"], 3)
        self.assertIsNone(geom["declared_input_rate_hz"])
        self.assertIsNone(geom["declared_hop_samples"])
        self.assertIsNone(geom["declared_frame_samples"])
        self.assertIsNone(geom["declared_layer_count"])
        self.assertFalse(geom["verified_here"])
        self.assertFalse(geom["measured_here"])
        self.assertFalse(geom["candidate_output"])
        self.assertFalse(geom["v0_can_represent_declared_input"])

    def test_required_artifacts_all_absent(self) -> None:
        rows = reference.REQUIRED_ARTIFACTS
        self.assertEqual([row["id"] for row in rows],
                         ["A1", "A2", "A3", "A4", "A5", "A6"])
        for row in rows:
            self.assertEqual(row["status"], "absent")
            self.assertIsNone(row["sha256"])
            self.assertIsNone(row["byte_count"])
            self.assertFalse(row["rights_reviewed"])

    def test_board_projection_uses_stable_identity_only(self) -> None:
        links, digest = reference._board_projection(board_with())
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertNotIn("status", links[0])
        self.assertNotIn("owner", links[0])
        self.assertEqual(len(digest), 64)
        _, changed = reference._board_projection(
            board_with(status="done", owner="someone-else",
                       history=["changed"]))
        self.assertEqual(changed, digest)
        _, unrelated = reference._board_projection(
            {"tasks": [{"id": "SDK-OTHER", "title": "Other",
                        "mode": "implementation", "status": "queued"},
                       {"id": "SDK-AFC-SPEX", "title": "AFC-SPEX",
                        "mode": "feasibility", "repository": "audio-sdk",
                        "component": "afc-spex"}]})
        self.assertEqual(unrelated, digest)

    def test_board_identity_change_rejected(self) -> None:
        for change in ({"title": "AFC SPEX"}, {"mode": "implementation"},
                       {"repository": "audio-pro"}, {"component": "other"}):
            with self.assertRaises(reference.ConfigError):
                reference._board_projection(board_with(**change))
        with self.assertRaises(reference.ConfigError):
            reference._board_projection({"tasks": []})

    def test_speaker_extraction_is_separated(self) -> None:
        self.assertFalse(
            reference.SPEAKER_EXTRACTION[
                "may_be_reported_as_mono_howling_control"])
        self.assertFalse(reference.SPEAKER_EXTRACTION["qualifies_candidate"])
        self.assertEqual(reference.MONO_HOWLING_CONTROL["status"],
                         "not_evaluated_by_this_task")
        self.assertFalse(
            reference.MONO_HOWLING_CONTROL["maximum_stable_gain_claim"])

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
        self.assertEqual(probe["harness_geometry"]["channels"], 3)
        self.assertFalse(
            probe["harness_geometry"]["verified_model_geometry"])


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
        self.assertTrue(self.report["incomplete"])
        self.assertTrue(self.report["proposal_only"])
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

    def test_upstream_artifacts_are_absent(self) -> None:
        blocker = self.report["upstream_blocker"]
        self.assertEqual(
            blocker["status"],
            "blocked_source_checkpoint_input_and_runtime_absent")
        self.assertEqual(blocker["source"]["status"], "absent")
        self.assertIsNone(blocker["source"]["revision"])
        self.assertIsNone(blocker["source"]["license"])
        self.assertEqual(blocker["checkpoint"]["status"], "absent")
        self.assertIsNone(blocker["checkpoint"]["sha256"])
        self.assertIsNone(blocker["checkpoint"]["byte_count"])
        self.assertEqual(blocker["input"]["status"], "absent")
        self.assertEqual(blocker["input"]["required_channels"], 3)
        self.assertFalse(blocker["input"]["mono_pilot_compatible"])
        self.assertEqual(blocker["runtime"]["status"], "absent_unpinned")
        self.assertIsNone(blocker["runtime_digest"])
        self.assertIsNone(blocker["checkpoint_digest"])
        self.assertIsNone(blocker["input_digest"])
        self.assertTrue(blocker["no_upstream_parity_claim"])

    def test_no_candidate_result_qualifies(self) -> None:
        candidate = self.report["candidates"][reference.CANDIDATE]
        self.assertEqual(
            candidate["status"],
            "blocked_source_checkpoint_input_and_runtime_absent")
        self.assertIsNone(candidate["metrics"])
        self.assertIsNone(candidate["result"])
        self.assertFalse(candidate["qualifies_candidate"])
        self.assertIsNone(self.report["adverse"]["missing_result"]["metrics"])
        self.assertFalse(
            self.report["adverse"]["missing_result"]["qualifies_candidate"])
        required = self.report["required_results"]
        self.assertTrue(required)
        self.assertTrue(all(value.startswith("blocked_") or
                            value.startswith("partial_") or
                            value.startswith("not_evaluated_")
                            for value in required.values()))
        self.assertNotIn("passed", required.values())
        self.assertNotIn("qualified", required.values())

    def test_all_profile_items_are_unexecuted(self) -> None:
        mapping = self.report["profile_mapping"]
        self.assertEqual(self.report["verification_profile"], "DSP")
        self.assertTrue(all(value.startswith("blocked_") or
                            value.startswith("partial_")
                            for value in mapping.values()))
        self.assertNotIn("passed", mapping.values())

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

    def test_board_projection_is_reported_without_full_hash(self) -> None:
        self.assertFalse(self.report["board_full_file_hashed"])
        self.assertEqual(self.report["board_links"],
                         [reference.EXPECTED_LINK])
        self.assertIn("status",
                      self.report["board_mutable_fields_excluded"])
        self.assertIn("review",
                      self.report["board_mutable_fields_excluded"])
        self.assertEqual(len(self.report["board_link_projection_sha256"]),
                         64)

    def test_boundary_is_closed(self) -> None:
        boundary = self.report["boundary"]
        self.assertTrue(boundary["installed_v0_unchanged"])
        self.assertFalse(boundary["public_api_abi_changed"])
        self.assertFalse(boundary["provider_registered"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertFalse(boundary["real_corpus_or_weights"])
        self.assertFalse(boundary["release_claim"])
        self.assertEqual(boundary["format"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "float32", "frame_samples": 160,
        })


if __name__ == "__main__":
    unittest.main()
