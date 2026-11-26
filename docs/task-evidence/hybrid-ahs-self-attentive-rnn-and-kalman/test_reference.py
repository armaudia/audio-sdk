# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the Hybrid AHS self-attentive RNN/Kalman gate."""

from __future__ import annotations

import unittest

import reference


def valid_request() -> dict:
    return {
        "candidate": "hybrid_ahs_self_attentive_rnn_and_kalman",
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "samples": [0.0] * 160,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
        "checkpoint_sha256": None,
        "runtime_lock_sha256": None,
        "asset_bytes": 0,
    }


def board_with(**changes) -> dict:
    row = {
        "id": "SDK-HYBRID-AHS-SELF-ATTENTIVE-RNN-AND-KALMAN",
        "title": "Hybrid AHS self-attentive RNN and Kalman",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "component": "hybrid-ahs-self-attentive-rnn-and-kalman",
        "status": "in_progress",
        "owner": "agent-HYBRID-AHS-SELF-ATTENTIVE-RNN-AND-KALMAN",
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
                         "hybrid_ahs_self_attentive_rnn_and_kalman")
        self.assertEqual(validated["sample_rate_hz"], 16000)
        self.assertEqual(validated["frame_samples"], 160)
        self.assertEqual(len(validated["samples"]), 160)
        self.assertIsNone(validated["checkpoint_sha256"])
        self.assertIsNone(validated["runtime_lock_sha256"])
        self.assertEqual(validated["asset_bytes"], 0)

    def test_valid_asset_manifest_accepted(self) -> None:
        request = valid_request()
        request["checkpoint_sha256"] = "a" * 64
        request["runtime_lock_sha256"] = "b" * 64
        request["asset_bytes"] = 4096
        validated = reference.validate_request(request)
        self.assertEqual(validated["checkpoint_sha256"], "a" * 64)
        self.assertEqual(validated["runtime_lock_sha256"], "b" * 64)
        self.assertEqual(validated["asset_bytes"], 4096)

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
            ("sample_rate_hz", 8000),
            ("channels", 0),
            ("channels", -1),
            ("channels", True),
            ("channels", 2),
            ("frame_samples", 0),
            ("frame_samples", -160),
            ("frame_samples", True),
            ("frame_samples", 4097),
            ("frame_samples", 512),
            ("frame_samples", 1024),
            ("epoch", -1),
            ("epoch", True),
            ("first_input_sample", -160),
            ("first_input_sample", True),
            ("lifecycle", "closed"),
            ("lifecycle", "drained"),
            ("execution_mode", 4),
            ("execution_mode", True),
            ("candidate", "hybrid_ahs"),
        )
        for key, value in cases:
            request = valid_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=str(key)):
                reference.validate_request(request)

    def test_asset_manifest_fields_rejected(self) -> None:
        cases = (
            {"checkpoint_sha256": "a" * 63,
             "runtime_lock_sha256": "b" * 64, "asset_bytes": 1},
            {"checkpoint_sha256": "A" * 64,
             "runtime_lock_sha256": "b" * 64, "asset_bytes": 1},
            {"checkpoint_sha256": "g" * 64,
             "runtime_lock_sha256": "b" * 64, "asset_bytes": 1},
            {"checkpoint_sha256": True,
             "runtime_lock_sha256": "b" * 64, "asset_bytes": 1},
            {"checkpoint_sha256": "a" * 64,
             "runtime_lock_sha256": "b" * 63, "asset_bytes": 1},
            {"checkpoint_sha256": "a" * 64,
             "runtime_lock_sha256": None, "asset_bytes": 1},
            {"checkpoint_sha256": "a" * 64,
             "runtime_lock_sha256": "b" * 64, "asset_bytes": 0},
            {"checkpoint_sha256": None,
             "runtime_lock_sha256": None, "asset_bytes": 1},
            {"checkpoint_sha256": None,
             "runtime_lock_sha256": None, "asset_bytes": -1},
            {"checkpoint_sha256": None,
             "runtime_lock_sha256": None, "asset_bytes": True},
            {"checkpoint_sha256": None,
             "runtime_lock_sha256": None, "asset_bytes": 536870913},
        )
        for change in cases:
            request = valid_request()
            request.update(change)
            with self.assertRaises(reference.EvidenceError, msg=str(change)):
                reference.validate_request(request)

    def test_wrong_sample_count_rejected(self) -> None:
        for count in (159, 161, 320):
            request = valid_request()
            request["samples"] = [0.0] * count
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_adverse_cases_all_rejected(self) -> None:
        data = reference._adverse_cases()
        self.assertTrue(data["all_rejected"])
        self.assertEqual(data["accepted_count"], 0)
        self.assertIsNone(data["metrics"])
        self.assertGreaterEqual(data["case_count"], 40)
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
        self.assertIn("runtime_unpinned", admitted["blockers"])
        self.assertIn("matched_closed_loop_cohort_absent",
                      admitted["blockers"])
        self.assertIn("rights_unrecorded", admitted["blockers"])
        self.assertIn("author_reported_results_only", admitted["blockers"])


class ProbeTests(unittest.TestCase):
    def test_source_absent(self) -> None:
        probe = reference.source_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_source_absent")
        self.assertIsNone(probe["revision"])
        self.assertIsNone(probe["tree_digest"])
        self.assertIsNone(probe["license"])
        self.assertEqual(probe["found"], [])
        self.assertFalse(probe["runnable_implementation_present"])
        self.assertTrue(probe["demo_materials_only_reported"])

    def test_checkpoint_absent(self) -> None:
        probe = reference.checkpoint_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_checkpoint_absent")
        self.assertEqual(probe["found"], [])
        self.assertIsNone(probe["sha256"])
        self.assertIsNone(probe["byte_count"])
        self.assertIsNone(probe["model_revision"])
        self.assertIsNone(probe["parameter_count"])
        self.assertIsNone(probe["model_card"])

    def test_runtime_unpinned(self) -> None:
        probe = reference.runtime_probe()
        self.assertFalse(probe["pinned"])
        self.assertEqual(probe["status"], "blocked_runtime_unpinned")
        self.assertEqual(probe["lockfiles"], [])
        self.assertIsNone(probe["interpreter"])
        self.assertIsNone(probe["framework"])
        self.assertIsNone(probe["sha256"])
        self.assertIsNone(probe["offline_path"])

    def test_license_not_approved(self) -> None:
        probe = reference.license_probe()
        self.assertEqual(probe["status"], "blocked_rights_unrecorded")
        self.assertIsNone(probe["reported_name"])
        self.assertFalse(probe["license_text_present"])
        self.assertIsNone(probe["license_text_sha256"])
        self.assertFalse(probe["use_approved"])
        self.assertFalse(probe["redistribution_approved"])
        self.assertFalse(probe["derived_output_approved"])
        self.assertEqual(probe["review"], "blocked")
        self.assertTrue(probe["required"])

    def test_cohort_absent(self) -> None:
        probe = reference.cohort_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"],
                         "blocked_matched_cohort_absent")
        self.assertFalse(probe["corpus_rights"])
        self.assertFalse(probe["loop_gain_measured"])
        self.assertFalse(probe["delay_measured"])
        self.assertFalse(probe["held_out_paths"])

    def test_rights_blocked(self) -> None:
        probe = reference.rights_probe()
        self.assertEqual(probe["status"], "blocked_rights_unrecorded")
        self.assertEqual(probe["review"], "blocked")
        self.assertIsNone(probe["source_license"])
        self.assertFalse(probe["use_approved"])
        self.assertFalse(probe["input_corpus_rights"])

    def test_geometry_is_not_invented(self) -> None:
        geom = reference.geometry()
        self.assertFalse(geom["declared_candidate_geometry_recorded"])
        self.assertEqual(geom["declared_sample_rates_hz"], [])
        for key in ("declared_frame_samples", "declared_channels",
                    "declared_stft_size", "declared_hop_samples",
                    "declared_kalman_state_dimension", "declared_rnn_layers",
                    "declared_parameter_count", "v0_can_represent_declared_input"):
            self.assertIsNone(geom[key], msg=key)
        self.assertEqual(geom["local_harness_geometry"], {
            "sample_rate_hz": 16000, "channels": 1,
            "frame_samples": 160, "sample_format": "float32",
        })
        self.assertFalse(geom["local_harness_is_candidate_geometry"])
        self.assertFalse(geom["verified_here"])
        self.assertFalse(geom["measured_here"])
        self.assertFalse(geom["candidate_output"])

    def test_required_artifacts_all_absent(self) -> None:
        rows = reference.REQUIRED_ARTIFACTS
        self.assertEqual([row["id"] for row in rows],
                         ["A1", "A2", "A3", "A4", "A5", "A6"])
        for row in rows:
            self.assertEqual(row["status"], "absent")
            self.assertIsNone(row["sha256"])
            self.assertIsNone(row["byte_count"])
            self.assertFalse(row["rights_reviewed"])

    def test_author_reported_results_are_provenance_only(self) -> None:
        block = reference.AUTHOR_REPORTED_RESULTS
        self.assertEqual(block["status"],
                         "retained_author_reported_not_reproduced")
        self.assertEqual(block["evidence_class"],
                         "author_reported_not_reproduced")
        self.assertEqual(block["cohort"]["utterances"], 200)
        self.assertEqual(block["cohort"]["loop_gains"], [2.0, 2.5, 3.0])
        self.assertEqual(block["neuralkalmanahs"]["sdr_db"],
                         [2.65, 1.98, 1.45])
        self.assertEqual(block["neuralkalmanahs"]["pesq"],
                         [2.33, 2.17, 2.04])
        self.assertIsNone(block["local_metrics"])
        self.assertFalse(block["reproduced_here"])
        self.assertFalse(block["qualifies_candidate"])

    def test_method_provenance_is_source_reported_only(self) -> None:
        method = reference.METHOD_PROVENANCE
        self.assertEqual(method["status"],
                         "source_reported_only_not_reproduced")
        self.assertIn("frequency-domain Kalman filter", method["components"])
        self.assertIn("self-attentive recurrent neural network",
                      method["components"])
        self.assertFalse(method["exact_checkpoint_present"])
        self.assertFalse(method["reproduced_here"])
        self.assertTrue(method["source_reported_only"])
        self.assertFalse(method["qualifies_candidate"])

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
                       {"id": "SDK-HYBRID-AHS-SELF-ATTENTIVE-RNN-AND-KALMAN",
                        "title": "Hybrid AHS self-attentive RNN and Kalman",
                        "mode": "feasibility", "repository": "audio-sdk",
                        "component":
                            "hybrid-ahs-self-attentive-rnn-and-kalman"}]})
        self.assertEqual(unrelated, digest)

    def test_board_identity_change_rejected(self) -> None:
        for change in ({"title": "Hybrid AHS"},
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
        self.assertFalse(boundary["source_present"])
        self.assertFalse(boundary["runnable_implementation_present"])
        self.assertFalse(boundary["checkpoint_present"])
        self.assertFalse(boundary["runtime_present"])
        self.assertFalse(boundary["host_target_approved"])
        self.assertFalse(boundary["license_text_present"])
        self.assertFalse(boundary["use_approved"])
        self.assertFalse(boundary["redistribution_approved"])
        self.assertFalse(boundary["derived_output_approved"])
        self.assertFalse(boundary["adapter_implemented"])
        self.assertFalse(boundary["adapter_default_registration"])
        self.assertFalse(boundary["automatic_discovery"])
        self.assertEqual(boundary["fallback"], "none")
        self.assertTrue(
            boundary["author_claims_separate_from_local_measurements"])

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
            "blocked_source_checkpoint_runtime_rights_and_cohort_absent")
        self.assertEqual(blocker["source"]["status"], "absent")
        self.assertIsNone(blocker["source"]["revision"])
        self.assertIsNone(blocker["source"]["license"])
        self.assertFalse(
            blocker["source"]["runnable_implementation_present"])
        self.assertEqual(blocker["checkpoint"]["status"], "absent")
        self.assertIsNone(blocker["checkpoint"]["sha256"])
        self.assertFalse(blocker["checkpoint"]["trained_state_present"])
        self.assertEqual(blocker["runtime"]["status"], "absent_unpinned")
        self.assertEqual(blocker["license"]["status"],
                         "blocked_rights_unrecorded")
        self.assertFalse(blocker["license"]["license_text_present"])
        self.assertFalse(blocker["license"]["use_approved"])
        self.assertFalse(blocker["license"]["redistribution_approved"])
        self.assertEqual(blocker["cohort"]["status"], "absent")
        self.assertFalse(blocker["cohort"]["corpus_rights"])
        for key in ("pinned_revision", "source_digest", "checkpoint_digest",
                    "runtime_digest", "license_digest", "cohort_digest",
                    "config_digest"):
            self.assertIsNone(blocker[key])
        self.assertTrue(blocker["no_upstream_parity_claim"])

    def test_no_candidate_result_qualifies(self) -> None:
        candidate = self.report["candidates"][reference.CANDIDATE]
        self.assertEqual(
            candidate["status"],
            "blocked_source_checkpoint_runtime_rights_and_cohort_absent")
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
        self.assertFalse(external["adapter_implemented"])
        self.assertFalse(external["checkpoint_present"])

    def test_author_reported_results_are_reported_as_provenance(self) -> None:
        block = self.report["author_reported_results"]
        self.assertEqual(block, reference.AUTHOR_REPORTED_RESULTS)
        self.assertEqual(block["neuralkalmanahs"]["sdr_db"],
                         [2.65, 1.98, 1.45])
        self.assertIsNone(block["local_metrics"])
        self.assertFalse(block["reproduced_here"])
        self.assertFalse(block["qualifies_candidate"])
        self.assertEqual(self.report["method_provenance"],
                         reference.METHOD_PROVENANCE)


if __name__ == "__main__":
    unittest.main()
