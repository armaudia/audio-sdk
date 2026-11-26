# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for SDK-MICROSOFT-NSNET2-BASELINE evidence."""

from __future__ import annotations

import unittest

import reference


def valid_request() -> dict:
    return {
        "candidate": "microsoft_nsnet2",
        "sample_rate_hz": 48000,
        "channels": 1,
        "frame_samples": 960,
        "samples": [0.0] * 960,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
    }


def board_with(**changes) -> dict:
    row = {
        "id": "SDK-MICROSOFT-NSNET2-BASELINE",
        "title": "Microsoft NSNet2 baseline",
        "mode": "feasibility",
        "repository": "audio-sdk",
        "component": "microsoft-nsnet2-baseline",
        "status": "in_progress",
        "owner": "agent-MICROSOFT-NSNET2-BASELINE",
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
        self.assertEqual(validated["candidate"], "microsoft_nsnet2")
        self.assertEqual(validated["sample_rate_hz"], 48000)
        self.assertEqual(validated["frame_samples"], 960)
        self.assertNotIn("hop_samples", validated)
        self.assertEqual(len(validated["samples"]), 960)

    def test_unknown_and_missing_fields_rejected(self) -> None:
        request = valid_request()
        request["extra"] = True
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(request)
        request = valid_request()
        del request["epoch"]
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(request)
        request = valid_request()
        request["hop_samples"] = 480
        with self.assertRaises(reference.ConfigError) as context:
            reference.validate_request(request)
        self.assertEqual(context.exception.code, "UNKNOWN_FIELD")

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
            ("sample_rate_hz", -48000),
            ("sample_rate_hz", True),
            ("sample_rate_hz", 8000),
            ("sample_rate_hz", 16000),
            ("sample_rate_hz", 44100),
            ("channels", 0),
            ("channels", -1),
            ("channels", True),
            ("channels", 2),
            ("channels", 65),
            ("frame_samples", 0),
            ("frame_samples", 4097),
            ("frame_samples", 160),
            ("frame_samples", 512),
            ("epoch", -1),
            ("epoch", True),
            ("first_input_sample", -960),
            ("lifecycle", "closed"),
            ("lifecycle", "drained"),
            ("execution_mode", 4),
            ("execution_mode", True),
            ("candidate", "microsoft_nsnet3"),
        )
        for key, value in cases:
            request = valid_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=str(key)):
                reference.validate_request(request)

    def test_unrecorded_rates_rejected_without_vendor_claim(self) -> None:
        for rate in (8000, 16000, 22050, 44100):
            request = valid_request()
            request["sample_rate_hz"] = rate
            with self.assertRaises(reference.ConfigError) as context:
                reference.validate_request(request)
            self.assertEqual(context.exception.code, "RATE_NOT_RECORDED")
        self.assertEqual(reference.DECLARED_SAMPLE_RATES_HZ, (48000,))

    def test_wrong_sample_count_rejected(self) -> None:
        for count in (159, 160, 512, 959, 961):
            request = valid_request()
            request["samples"] = [0.0] * count
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_adverse_cases_all_rejected(self) -> None:
        data = reference._adverse_cases()
        self.assertTrue(data["all_rejected"])
        self.assertEqual(data["accepted_count"], 0)
        self.assertIsNone(data["metrics"])
        self.assertGreaterEqual(data["case_count"], 35)
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
        for expected in ("official_source_absent",
                         "official_model_artifact_absent",
                         "model_terms_not_recorded", "runtime_unpinned",
                         "portable_host_runtime_absent",
                         "eligible_runner_absent",
                         "matched_cohort_absent", "scorer_unapproved",
                         "rights_unrecorded"):
            self.assertIn(expected, admitted["blockers"])
        if reference.third_party_probe()["present"]:
            self.assertIn("third_party_reimplementation_not_accepted",
                          admitted["blockers"])


class ProbeTests(unittest.TestCase):
    def test_source_absent(self) -> None:
        probe = reference.source_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_official_source_absent")
        self.assertIsNone(probe["revision"])
        self.assertIsNone(probe["tree_digest"])
        self.assertIsNone(probe["license"])
        self.assertFalse(probe["official_download_path_available"])
        self.assertEqual(probe["documented_addition_commit"],
                         reference.ADDITION_COMMIT)
        self.assertEqual(probe["documented_removal_commit"],
                         reference.REMOVAL_COMMIT)
        self.assertEqual(probe["found"], [])

    def test_model_artifact_absent(self) -> None:
        probe = reference.weights_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"],
                         "blocked_official_model_artifact_absent")
        for key in ("path", "sha256", "byte_count", "conversion_recipe",
                    "precision", "quantization", "operator_set"):
            self.assertIsNone(probe[key])
        self.assertEqual(probe["found"], [])

    def test_terms_not_recorded(self) -> None:
        probe = reference.license_probe()
        self.assertEqual(probe["status"],
                         "blocked_model_terms_not_recorded")
        self.assertIsNone(probe["reported_name"])
        self.assertTrue(probe["general_repository_notice_recorded"])
        self.assertFalse(
            probe["artifact_specific_model_terms_recorded"])
        self.assertFalse(
            probe["reported_terms_recorded_in_pinned_evidence"])
        self.assertFalse(probe["license_text_present"])
        self.assertIsNone(probe["license_text_sha256"])
        self.assertFalse(probe["model_terms_present"])
        self.assertFalse(probe["use_approved"])
        self.assertFalse(probe["redistribution_approved"])
        self.assertFalse(probe["host_target_approved"])
        self.assertEqual(probe["review"], "blocked")
        self.assertIn("MIT", probe["reported_code_license"])
        self.assertIn("CC BY 4.0", probe["reported_documentation_license"])

    def test_runner_absent(self) -> None:
        probe = reference.hardware_probe()
        self.assertEqual(probe["status"],
                         "blocked_eligible_runner_absent")
        self.assertIsNone(probe["runner"])
        self.assertIsNone(probe["hardware_attached"])
        self.assertIsNone(probe["firmware_sha256"])
        self.assertFalse(probe["vendor_resource_figures_generalizable"])
        self.assertFalse(probe["serial_device_probed"])
        self.assertIsInstance(probe["toolchain_commands"], dict)

    def test_runtime_unpinned(self) -> None:
        probe = reference.runtime_probe()
        self.assertFalse(probe["pinned"])
        self.assertEqual(probe["status"], "blocked_runtime_unpinned")
        self.assertEqual(probe["lockfiles"], [])
        self.assertIsNone(probe["onnxruntime_version"])
        self.assertIsNone(probe["python_version"])
        self.assertIsNone(probe["portable_host_runtime"])

    def test_cohort_absent(self) -> None:
        probe = reference.cohort_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"],
                         "blocked_matched_cohort_absent")
        self.assertFalse(probe["corpus_rights"])
        self.assertFalse(probe["clean_references_present"])

    def test_scorer_unapproved(self) -> None:
        probe = reference.scorer_probe()
        self.assertEqual(probe["status"],
                         "unapproved_no_scorer_implemented")
        self.assertFalse(probe["approved_si_sdr"])
        self.assertFalse(probe["approved_stoi"])
        self.assertFalse(probe["authorized_listening"])
        self.assertFalse(probe["predictive_screen_labeled"])
        self.assertFalse(probe["calibrated_here"])
        self.assertIsNone(probe["sha256"])

    def test_rights_blocked(self) -> None:
        probe = reference.rights_probe()
        self.assertEqual(probe["status"], "blocked_rights_unrecorded")
        self.assertEqual(probe["review"], "blocked")
        self.assertIsNone(probe["source_license"])
        self.assertFalse(probe["use_approved"])
        self.assertFalse(probe["input_corpus_rights"])

    def test_third_party_is_not_official_and_not_substituted(self) -> None:
        probe = reference.third_party_probe()
        self.assertEqual(probe["path"], reference.THIRD_PARTY_PATH)
        self.assertFalse(probe["official_microsoft_nsnet2"])
        self.assertFalse(probe["accepted_as_official_artifact"])
        self.assertFalse(probe["accepted_as_substitute"])
        self.assertFalse(probe["weights_present_locally"])
        self.assertEqual(probe["weight_candidates"], [])
        self.assertIn(probe["status"],
                      ("third_party_reimplementation_present_not_official",
                       "third_party_reimplementation_absent"))

    def test_geometry_is_not_invented(self) -> None:
        geom = reference.geometry()
        self.assertEqual(geom["component"], "Microsoft NSNet2 baseline")
        self.assertEqual(geom["declared_sample_rates_hz"], [48000])
        self.assertEqual(geom["declared_frame_ms"], 20)
        self.assertIsNone(geom["declared_hop_ms"])
        self.assertEqual(geom["derived_frame_samples_at_48k"], 960)
        self.assertIsNone(geom["derived_hop_samples_at_48k"])
        self.assertFalse(geom["derived_sample_counts_are_api_constants"])
        self.assertIsNone(geom["reported_parameter_count"])
        self.assertIsNone(geom["declared_channels"])
        self.assertEqual(geom["local_channel_guard"], 64)
        self.assertIsNone(geom["declared_feature_extraction"])
        self.assertIsNone(geom["declared_output_mapping"])
        self.assertIsNone(geom["declared_buffering_delay_samples"])
        self.assertIsNone(geom["declared_quantization"])
        self.assertFalse(geom["official_download_path_available"])
        self.assertFalse(geom["vendor_resource_figures_generalizable"])
        self.assertFalse(geom["verified_here"])
        self.assertFalse(geom["measured_here"])
        self.assertFalse(geom["candidate_output"])
        self.assertFalse(geom["v0_can_represent_declared_input"])

    def test_required_artifacts_all_absent(self) -> None:
        rows = reference.REQUIRED_ARTIFACTS
        self.assertEqual([row["id"] for row in rows],
                         ["A" + str(number) for number in range(1, 9)])
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
                       {"id": "SDK-MICROSOFT-NSNET2-BASELINE",
                        "title": "Microsoft NSNet2 baseline",
                        "mode": "feasibility", "repository": "audio-sdk",
                        "component": "microsoft-nsnet2-baseline"}]})
        self.assertEqual(unrelated, digest)

    def test_board_identity_change_rejected(self) -> None:
        for change in ({"title": "Microsoft NS-Net 2"},
                       {"mode": "external-adapter"},
                       {"repository": "audio-pro"},
                       {"component": "other"}):
            with self.assertRaises(reference.ConfigError):
                reference._board_projection(board_with(**change))
        with self.assertRaises(reference.ConfigError):
            reference._board_projection({"tasks": []})

    def test_model_boundary_is_closed(self) -> None:
        boundary = reference.MODEL_BOUNDARY
        self.assertTrue(boundary["documented"])
        self.assertEqual(boundary["sdk_disposition"], "sdk-model")
        self.assertFalse(boundary["host_target_eligible"])
        self.assertFalse(boundary["portable_adapter_present"])
        self.assertFalse(boundary["license_text_present"])
        self.assertFalse(boundary["model_terms_present"])
        self.assertFalse(boundary["use_approved"])
        self.assertFalse(boundary["redistribution_approved"])
        self.assertFalse(boundary["weights_present"])
        self.assertFalse(boundary["official_download_path_available"])
        self.assertFalse(boundary["third_party_accepted_as_official"])
        self.assertFalse(boundary["adapter_implemented"])
        self.assertFalse(boundary["adapter_default_registration"])
        self.assertFalse(boundary["automatic_discovery"])
        self.assertEqual(boundary["fallback"], "none")
        self.assertTrue(
            boundary["vendor_claims_separate_from_local_measurements"])

    def test_enhancement_control_is_unmeasured(self) -> None:
        block = reference.ENHANCEMENT_CONTROL
        self.assertEqual(block["status"], "not_evaluated_by_this_task")
        for key in ("identity_noisy_control",
                    "established_task_matched_baseline",
                    "paired_si_sdr_db", "paired_stoi",
                    "clean_speech_preservation", "peak_and_invalid_outputs",
                    "alignment_and_content_delay", "state_and_reset", "memory",
                    "measured_availability_timing", "metrics", "result"):
            self.assertIsNone(block[key], msg=key)
        self.assertFalse(block["qualifies_candidate"])
        self.assertFalse(block["quality_claim"])
        self.assertFalse(block["intelligibility_claim"])
        self.assertFalse(block["listening_claim"])
        self.assertFalse(block["timing_claim"])

    def test_scorer_block_is_unapproved(self) -> None:
        block = reference.SCORER_PROBE_BLOCK
        self.assertEqual(block["status"],
                         "unapproved_no_scorer_implemented")
        for key in ("si_sdr", "stoi", "dnsmos", "pesq", "listening_panel",
                    "approved_scorer_sha256"):
            self.assertIsNone(block[key], msg=key)
        self.assertFalse(block["calibrated_here"])

    def test_stimulus_probe_reports_no_candidate_processing(self) -> None:
        probe = reference.stimulus_probe()
        self.assertFalse(probe["candidate_processing"])
        self.assertEqual(set(probe["stimuli"]),
                         {"silence", "impulse", "step", "sweep",
                          "speech_like", "noise_like"})
        self.assertTrue(all(item["nonfinite_count"] == 0
                            for item in probe["stimuli"].values()))
        self.assertTrue(all(item["byte_identical"]
                            for item in probe["identity_control"].values()))
        self.assertEqual(probe["harness_geometry"]["channels"], 1)
        self.assertEqual(probe["harness_geometry"]["frame_samples"], 960)
        self.assertIsNone(probe["harness_geometry"]["hop_samples"])
        self.assertEqual(probe["harness_geometry"]["sample_rate_hz"], 48000)
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
            "blocked_official_artifact_terms_runtime_and_matched_cohort_absent")
        self.assertEqual(blocker["source"]["status"], "absent")
        self.assertIsNone(blocker["source"]["revision"])
        self.assertIsNone(blocker["source"]["license"])
        self.assertFalse(
            blocker["source"]["official_download_path_available"])
        self.assertEqual(blocker["weights"]["status"], "absent")
        self.assertIsNone(blocker["weights"]["sha256"])
        self.assertIsNone(blocker["weights"]["byte_count"])
        self.assertEqual(blocker["license"]["status"],
                         "blocked_model_terms_not_recorded")
        self.assertTrue(
            blocker["license"]["general_repository_notice_recorded"])
        self.assertFalse(
            blocker["license"]["artifact_specific_model_terms_recorded"])
        self.assertFalse(blocker["license"]["license_text_present"])
        self.assertFalse(blocker["license"]["model_terms_present"])
        self.assertFalse(blocker["license"]["use_approved"])
        self.assertFalse(blocker["license"]["redistribution_approved"])
        self.assertEqual(blocker["hardware"]["status"], "absent")
        self.assertIsNone(blocker["hardware"]["runner"])
        self.assertEqual(blocker["runtime"]["status"], "absent_unpinned")
        self.assertEqual(blocker["cohort"]["status"], "absent")
        self.assertFalse(blocker["cohort"]["corpus_rights"])
        self.assertEqual(blocker["scorer"]["status"], "unapproved")
        self.assertFalse(
            blocker["third_party"]["accepted_as_official_artifact"])
        self.assertFalse(
            blocker["third_party"]["accepted_as_substitute"])
        for key in ("pinned_revision", "source_digest", "weights_digest",
                    "license_digest", "hardware_digest", "runtime_digest",
                    "config_digest", "cohort_digest", "scorer_digest"):
            self.assertIsNone(blocker[key], msg=key)
        self.assertTrue(blocker["no_upstream_parity_claim"])

    def test_no_candidate_result_qualifies(self) -> None:
        candidate = self.report["candidates"][reference.CANDIDATE]
        self.assertEqual(
            candidate["status"],
            "blocked_official_artifact_terms_runtime_and_matched_cohort_absent")
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
        self.assertEqual(self.report["verification_profile"], "Enhancement")
        self.assertEqual(self.report["profile"]["name"], "Enhancement")
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
        self.assertGreaterEqual(len(checks), 20)

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

    def test_model_boundary_is_reported(self) -> None:
        external = self.report["model_boundary"]
        self.assertEqual(external, reference.MODEL_BOUNDARY)
        self.assertTrue(external["documented"])
        self.assertFalse(external["host_target_eligible"])
        self.assertFalse(external["adapter_implemented"])

    def test_third_party_is_reported_but_rejected(self) -> None:
        probe = self.report["third_party_probe"]
        self.assertEqual(probe, reference.third_party_probe())
        self.assertFalse(probe["accepted_as_official_artifact"])
        self.assertFalse(probe["accepted_as_substitute"])

    def test_evidence_classes_are_proposal_only(self) -> None:
        classes = self.report["evidence_classes"]
        self.assertIn("no_quality_or_timing_measurement", classes)
        self.assertIn("explicit_missing_official_artifact_and_rights_blocker",
                      classes)
        self.assertIn("third_party_substitute_rejected", classes)


if __name__ == "__main__":
    unittest.main()
