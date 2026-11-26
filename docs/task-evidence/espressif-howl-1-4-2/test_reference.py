# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for SDK-ESPRESSIF-HOWL-1-4-2 blocker evidence."""

from __future__ import annotations

import json
import unittest

import reference


def valid_request() -> dict:
    return {
        "candidate": "espressif_howl_1_4_2",
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 512,
        "samples": [0.0] * 512,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
    }


def board_with(**changes) -> dict:
    row = {
        "id": "SDK-ESPRESSIF-HOWL-1-4-2",
        "title": "Espressif HOWL 1.4.2",
        "mode": "external-adapter",
        "repository": "audio-sdk",
        "component": "espressif-howl-1-4-2",
        "status": "in_progress",
        "owner": "agent-ESPRESSIF-HOWL-1-4-2",
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
        self.assertEqual(validated["candidate"], "espressif_howl_1_4_2")
        self.assertEqual(validated["sample_rate_hz"], 16000)
        self.assertEqual(validated["frame_samples"], 512)
        self.assertEqual(len(validated["samples"]), 512)

    def test_declared_48k_frame_accepted(self) -> None:
        request = valid_request()
        request["sample_rate_hz"] = 48000
        request["frame_samples"] = 1024
        request["samples"] = [0.0] * 1024
        validated = reference.validate_request(request)
        self.assertEqual(validated["sample_rate_hz"], 48000)
        self.assertEqual(validated["frame_samples"], 1024)

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
            ("channels", 65),
            ("frame_samples", 0),
            ("frame_samples", 4097),
            ("frame_samples", 160),
            ("epoch", -1),
            ("epoch", True),
            ("first_input_sample", -512),
            ("lifecycle", "closed"),
            ("lifecycle", "drained"),
            ("execution_mode", 4),
            ("execution_mode", True),
            ("candidate", "espressif_howl"),
        )
        for key, value in cases:
            request = valid_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=str(key)):
                reference.validate_request(request)

    def test_unverified_rates_rejected_without_vendor_claim(self) -> None:
        for rate in (8000, 24000, 32000, 44100):
            request = valid_request()
            request["sample_rate_hz"] = rate
            with self.assertRaises(reference.ConfigError) as context:
                reference.validate_request(request)
            self.assertEqual(context.exception.code,
                             "UNVERIFIED_FRAME_GEOMETRY")
        self.assertIn(16000, reference.DECLARED_FRAME_SAMPLES)
        self.assertIn(48000, reference.DECLARED_FRAME_SAMPLES)
        self.assertNotIn(44100, reference.DECLARED_FRAME_SAMPLES)

    def test_wrong_sample_count_rejected(self) -> None:
        for count in (159, 160, 511, 513):
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
        self.assertIn("non_espressif_use_not_approved", admitted["blockers"])
        self.assertIn("eligible_hardware_and_toolchain_absent",
                      admitted["blockers"])
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

    def test_license_not_approved(self) -> None:
        probe = reference.license_probe()
        self.assertEqual(probe["status"],
                         "blocked_non_espressif_use_not_approved")
        self.assertFalse(probe["license_text_present"])
        self.assertIsNone(probe["license_text_sha256"])
        self.assertFalse(probe["non_espressif_use_approved"])
        self.assertFalse(probe["redistribution_approved"])
        self.assertFalse(probe["host_target_approved"])
        self.assertEqual(probe["review"], "blocked")
        self.assertIn("Espressif", probe["reported_name"])

    def test_hardware_absent(self) -> None:
        probe = reference.hardware_probe()
        self.assertEqual(probe["status"],
                         "blocked_eligible_hardware_absent")
        self.assertIsNone(probe["runner"])
        self.assertIsNone(probe["hardware_attached"])
        self.assertIsNone(probe["firmware_sha256"])
        self.assertFalse(probe["vendor_cpu_memory_figures_generalizable"])
        self.assertFalse(probe["serial_device_probed"])

    def test_runtime_unpinned(self) -> None:
        probe = reference.runtime_probe()
        self.assertFalse(probe["pinned"])
        self.assertEqual(probe["status"], "blocked_runtime_unpinned")
        self.assertEqual(probe["lockfiles"], [])
        self.assertIsNone(probe["idf_version"])
        self.assertIsNone(probe["firmware_sha256"])

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
        self.assertFalse(probe["non_espressif_use_approved"])
        self.assertFalse(probe["input_corpus_rights"])

    def test_geometry_is_not_invented(self) -> None:
        geom = reference.geometry()
        self.assertEqual(geom["component_version"], "1.4.2")
        self.assertEqual(geom["declared_sample_rates_hz"],
                         [8000, 16000, 24000, 32000, 44100, 48000])
        self.assertEqual(geom["declared_frame_samples_by_rate"],
                         {"16000": 512, "48000": 1024})
        self.assertEqual(geom["declared_frame_samples_unverified_rates"],
                         [8000, 24000, 32000, 44100])
        self.assertIsNone(geom["declared_frame_samples_other"])
        self.assertIsNone(geom["declared_channels"])
        self.assertEqual(geom["local_channel_guard"], 64)
        self.assertTrue(geom["declared_per_channel_independent"])
        self.assertFalse(geom["vendor_cpu_memory_figures_generalizable"])
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
                       {"id": "SDK-ESPRESSIF-HOWL-1-4-2",
                        "title": "Espressif HOWL 1.4.2",
                        "mode": "external-adapter", "repository": "audio-sdk",
                        "component": "espressif-howl-1-4-2"}]})
        self.assertEqual(unrelated, digest)

    def test_board_identity_change_rejected(self) -> None:
        for change in ({"title": "Espressif HOWL"},
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
        self.assertFalse(boundary["non_espressif_use_approved"])
        self.assertFalse(boundary["redistribution_approved"])
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
        self.assertFalse(block["notch_claim"])
        self.assertFalse(block["loop_margin_claim"])
        self.assertFalse(block["maximum_stable_gain_claim"])
        self.assertFalse(block["feedback_cancellation_claim"])

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
        self.assertEqual(probe["harness_geometry"]["frame_samples"], 512)
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
            "blocked_source_license_hardware_runtime_and_fixture_absent")
        self.assertEqual(blocker["source"]["status"], "absent")
        self.assertIsNone(blocker["source"]["revision"])
        self.assertIsNone(blocker["source"]["license"])
        self.assertEqual(blocker["license"]["status"],
                         "blocked_non_espressif_use_not_approved")
        self.assertFalse(blocker["license"]["license_text_present"])
        self.assertFalse(blocker["license"]["non_espressif_use_approved"])
        self.assertFalse(blocker["license"]["redistribution_approved"])
        self.assertEqual(blocker["hardware"]["status"], "absent")
        self.assertIsNone(blocker["hardware"]["runner"])
        self.assertEqual(blocker["runtime"]["status"], "absent_unpinned")
        self.assertEqual(blocker["fixture"]["status"], "absent")
        self.assertFalse(blocker["fixture"]["corpus_rights"])
        for key in ("pinned_revision", "source_digest", "license_digest",
                    "hardware_digest", "runtime_digest", "fixture_digest",
                    "config_digest"):
            self.assertIsNone(blocker[key])
        self.assertTrue(blocker["no_upstream_parity_claim"])

    def test_no_candidate_result_qualifies(self) -> None:
        candidate = self.report["candidates"][reference.CANDIDATE]
        self.assertEqual(
            candidate["status"],
            "blocked_source_license_hardware_runtime_and_fixture_absent")
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
