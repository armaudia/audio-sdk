# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION evidence."""

from __future__ import annotations

import unittest

import reference


def valid_request() -> dict:
    return {
        "candidate": "hybridahs_v2_complex_ratio_mask",
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "samples": [0.0] * 160,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
    }


def board_with(**changes) -> dict:
    row = {
        "id": "SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION",
        "title": "Neural direct howling suppression",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "component": "neural-direct-howling-suppression",
        "status": "in_progress",
        "owner": "agent-NEURAL-DIRECT-HOWLING-SUPPRESSION",
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
        for text in ('{"a":1} extra', '{"a":} '):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)


class RequestValidationTests(unittest.TestCase):
    def test_valid_request_accepted(self) -> None:
        validated = reference.validate_request(valid_request())
        self.assertEqual(validated["candidate"],
                         "hybridahs_v2_complex_ratio_mask")
        self.assertEqual(validated["sample_rate_hz"], 16000)
        self.assertEqual(validated["frame_samples"], 160)
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

    def test_geometry_lifecycle_and_mode_rejected(self) -> None:
        cases = (
            ("sample_rate_hz", 0),
            ("sample_rate_hz", -16000),
            ("sample_rate_hz", True),
            ("sample_rate_hz", 22050),
            ("channels", 0),
            ("channels", -1),
            ("channels", True),
            ("channels", 2),
            ("frame_samples", 0),
            ("frame_samples", 4097),
            ("frame_samples", 512),
            ("epoch", -1),
            ("epoch", True),
            ("first_input_sample", -160),
            ("lifecycle", "closed"),
            ("lifecycle", "drained"),
            ("execution_mode", 4),
            ("execution_mode", True),
            ("candidate", "neural_direct_ahs"),
        )
        for key, value in cases:
            request = valid_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=str(key)):
                reference.validate_request(request)

    def test_unverified_geometry_rejected_without_model_claim(self) -> None:
        for rate in (8000, 48000):
            request = valid_request()
            request["sample_rate_hz"] = rate
            with self.assertRaises(reference.ConfigError) as context:
                reference.validate_request(request)
            self.assertEqual(context.exception.code,
                             "UNVERIFIED_TASK_GEOMETRY")
        self.assertEqual(reference.HARNESS_SAMPLE_RATE_HZ, 16000)
        self.assertEqual(reference.HARNESS_FRAME_SAMPLES, 160)
        self.assertEqual(reference.HARNESS_CHANNELS, 1)

    def test_wrong_sample_count_rejected(self) -> None:
        for count in (159, 161, 512):
            request = valid_request()
            request["samples"] = [0.0] * count
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_adverse_cases_all_rejected(self) -> None:
        data = reference._adverse_cases()
        self.assertTrue(data["all_rejected"])
        self.assertEqual(data["accepted_count"], 0)
        self.assertIsNone(data["metrics"])
        self.assertGreaterEqual(data["case_count"], 30)
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
        self.assertIn("weights_absent", admitted["blockers"])
        self.assertIn("rights_unrecorded", admitted["blockers"])
        self.assertIn("runtime_unpinned", admitted["blockers"])
        self.assertIn("geometry_undocumented", admitted["blockers"])
        self.assertIn("matched_closed_loop_fixture_absent",
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

    def test_weights_absent(self) -> None:
        probe = reference.weights_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_weights_absent")
        self.assertIsNone(probe["checkpoint_count"])
        self.assertIsNone(probe["sha256"])
        self.assertEqual(probe["found"], [])

    def test_license_not_approved(self) -> None:
        probe = reference.license_probe()
        self.assertEqual(probe["status"], "blocked_rights_unrecorded")
        self.assertFalse(probe["license_text_present"])
        self.assertIsNone(probe["license_text_sha256"])
        self.assertFalse(probe["use_approved"])
        self.assertFalse(probe["redistribution_approved"])
        self.assertFalse(probe["host_target_approved"])
        self.assertEqual(probe["review"], "blocked")

    def test_runtime_unpinned(self) -> None:
        probe = reference.runtime_probe()
        self.assertFalse(probe["pinned"])
        self.assertEqual(probe["status"], "blocked_runtime_unpinned")
        self.assertEqual(probe["lockfiles"], [])
        self.assertIsNone(probe["sha256"])
        self.assertIsNone(probe["lockfile"])

    def test_geometry_undocumented(self) -> None:
        probe = reference.geometry_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_geometry_undocumented")
        for key in ("sample_rate_hz", "channels", "frame_samples",
                    "hop_samples", "lookahead_samples",
                    "content_delay_samples", "configuration"):
            self.assertIsNone(probe[key])
        self.assertFalse(probe["reset_and_drain_documented"])

    def test_fixture_absent(self) -> None:
        probe = reference.fixture_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"],
                         "blocked_matched_fixture_absent")
        self.assertFalse(probe["corpus_rights"])
        self.assertFalse(probe["loop_gain_measured"])
        self.assertFalse(probe["delay_measured"])

    def test_rights_blocked(self) -> None:
        probe = reference.rights_probe()
        self.assertEqual(probe["status"], "blocked_rights_unrecorded")
        self.assertEqual(probe["review"], "blocked")
        self.assertIsNone(probe["source_license"])
        self.assertFalse(probe["code_rights"])
        self.assertFalse(probe["weight_rights"])
        self.assertFalse(probe["input_corpus_rights"])

    def test_geometry_is_not_invented(self) -> None:
        geom = reference.geometry()
        self.assertFalse(geom["geometry_documented"])
        self.assertIsNone(geom["declared_sample_rate_hz"])
        self.assertIsNone(geom["declared_channels"])
        self.assertIsNone(geom["declared_frame_samples"])
        self.assertIsNone(geom["declared_hop_samples"])
        self.assertIsNone(geom["declared_lookahead_samples"])
        self.assertIsNone(geom["declared_content_delay_samples"])
        self.assertIsNone(geom["v0_can_represent_declared_input"])
        harness = geom["harness_geometry"]
        self.assertEqual(harness["sample_rate_hz"], 16000)
        self.assertEqual(harness["channels"], 1)
        self.assertEqual(harness["frame_samples"], 160)
        self.assertEqual(harness["sample_format"], "float32")
        self.assertFalse(geom["verified_here"])
        self.assertFalse(geom["measured_here"])
        self.assertFalse(geom["candidate_output"])

    def test_required_artifacts_all_absent(self) -> None:
        rows = reference.REQUIRED_ARTIFACTS
        self.assertEqual([row["id"] for row in rows],
                         ["A1", "A2", "A3", "A4", "A5", "A6", "A7"])
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
                       {"id": "SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION",
                        "title": "Neural direct howling suppression",
                        "mode": "feasibility", "repository": "audio-sdk",
                        "component": "neural-direct-howling-suppression"}]})
        self.assertEqual(unrelated, digest)

    def test_board_identity_change_rejected(self) -> None:
        for change in ({"title": "Neural direct suppression"},
                       {"mode": "implementation"},
                       {"repository": "audio-pro"},
                       {"component": "other"}):
            with self.assertRaises(reference.ConfigError):
                reference._board_projection(board_with(**change))
        with self.assertRaises(reference.ConfigError):
            reference._board_projection({"tasks": []})

    def test_external_boundary_is_closed(self) -> None:
        boundary = reference.EXTERNAL_BOUNDARY
        self.assertTrue(boundary["documented"])
        self.assertFalse(boundary["host_target_eligible"])
        self.assertFalse(boundary["license_text_present"])
        self.assertFalse(boundary["use_approved"])
        self.assertFalse(boundary["redistribution_approved"])
        self.assertFalse(boundary["weights_present"])
        self.assertFalse(boundary["adapter_implemented"])
        self.assertFalse(boundary["adapter_default_registration"])
        self.assertFalse(boundary["automatic_discovery"])
        self.assertEqual(boundary["fallback"], "none")
        self.assertTrue(
            boundary["vendor_claims_separate_from_local_measurements"])

    def test_howling_control_is_unmeasured(self) -> None:
        block = reference.HOWLING_CONTROL
        self.assertEqual(block["status"], "not_evaluated_by_this_task")
        self.assertIsNone(block["metrics"])
        self.assertIsNone(block["result"])
        self.assertFalse(block["qualifies_candidate"])
        self.assertFalse(block["howl_detection_claim"])
        self.assertFalse(block["mask_or_enhancement_claim"])
        self.assertFalse(block["maximum_stable_gain_claim"])
        self.assertFalse(block["feedback_cancellation_claim"])
        self.assertFalse(block["closed_loop_stability_claim"])

    def test_source_reported_metrics_are_provenance_only(self) -> None:
        metrics = reference.SOURCE_REPORTED_METRICS
        self.assertEqual(metrics["variant"], "NeuralKalmanAHS")
        self.assertEqual(metrics["mean_sdr_db"], [2.65, 1.98, 1.45])
        self.assertEqual(metrics["mean_pesq"], [2.33, 2.17, 2.04])
        self.assertFalse(metrics["reproduced_here"])
        self.assertFalse(metrics["qualifies_candidate"])

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
        self.assertEqual(probe["harness_geometry"]["channels"], 1)
        self.assertEqual(probe["harness_geometry"]["frame_samples"], 160)
        self.assertEqual(probe["harness_geometry"]["sample_rate_hz"], 16000)
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
            "blocked_source_weights_runtime_geometry_rights_and_fixture_absent")
        self.assertEqual(blocker["source"]["status"], "absent")
        self.assertIsNone(blocker["source"]["revision"])
        self.assertIsNone(blocker["source"]["license"])
        self.assertEqual(blocker["weights"]["status"], "absent")
        self.assertIsNone(blocker["weights"]["checkpoint_count"])
        self.assertEqual(blocker["license"]["status"],
                         "blocked_rights_unrecorded")
        self.assertFalse(blocker["license"]["license_text_present"])
        self.assertFalse(blocker["license"]["use_approved"])
        self.assertFalse(blocker["license"]["redistribution_approved"])
        self.assertEqual(blocker["runtime"]["status"], "absent_unpinned")
        self.assertEqual(blocker["geometry"]["status"], "absent")
        self.assertIsNone(blocker["geometry"]["sample_rate_hz"])
        self.assertEqual(blocker["fixture"]["status"], "absent")
        self.assertFalse(blocker["fixture"]["corpus_rights"])
        self.assertEqual(blocker["rights"]["status"],
                         "blocked_rights_unrecorded")
        for key in ("pinned_revision", "source_digest", "weights_digest",
                    "runtime_digest", "geometry_digest", "fixture_digest"):
            self.assertIsNone(blocker[key])
        self.assertTrue(blocker["no_upstream_parity_claim"])

    def test_no_candidate_result_qualifies(self) -> None:
        candidate = self.report["candidates"][reference.CANDIDATE]
        self.assertEqual(
            candidate["status"],
            "blocked_source_weights_runtime_geometry_rights_and_fixture_absent")
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
        self.assertEqual(self.report["profile"]["name"], "DSP")
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
        self.assertGreaterEqual(len(checks), 15)

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

    def test_external_boundary_is_reported(self) -> None:
        external = self.report["external_boundary"]
        self.assertEqual(external, reference.EXTERNAL_BOUNDARY)
        self.assertTrue(external["documented"])
        self.assertFalse(external["host_target_eligible"])
        self.assertFalse(external["adapter_implemented"])


if __name__ == "__main__":
    unittest.main()
