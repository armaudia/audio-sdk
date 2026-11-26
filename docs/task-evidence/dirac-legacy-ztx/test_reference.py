# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the SDK-DIRAC-LEGACY-ZTX evidence package.

Run from this directory::

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
"""

from __future__ import annotations

import sys
import unittest

sys.dont_write_bytecode = True

import reference  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceRejection):
            reference.load_strict_json_text('{"a":1,"a":2}')

    def test_nonfinite_constant_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(reference.ReferenceRejection, msg=token):
                reference.load_strict_json_text('{"a":' + token + "}")

    def test_bom_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceRejection):
            reference.load_strict_json_text('\ufeff{"a":1}')

    def test_root_array_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceRejection):
            reference.load_strict_json_object_text("[1,2,3]")

    def test_canonical_text_rejects_float(self) -> None:
        with self.assertRaises(reference.ReferenceRejection):
            reference.canonical_text({"a": 0.5})

    def test_canonical_roundtrip_is_stable(self) -> None:
        payload = {"b": [1, 2], "a": {"z": True, "y": None}}
        text = reference.canonical_text(payload)
        self.assertEqual(reference.load_strict_json_text(text), payload)


class ValidationTests(unittest.TestCase):
    def test_samples_accept_valid(self) -> None:
        values = reference.validate_samples([0.0, -0.5, 0.99])
        self.assertEqual(len(values), 3)

    def test_samples_reject_adverse(self) -> None:
        cases = (
            [],
            [float("nan")],
            [float("inf")],
            [1.5],
            [True],
            ["x"],
            [0.0] * (reference.MAX_SAMPLES + 1),
        )
        for samples in cases:
            with self.assertRaises(reference.ReferenceRejection, msg=str(samples[:2])):
                reference.validate_samples(samples)

    def test_schedule_accepts_constant_and_change(self) -> None:
        self.assertEqual(
            reference.validate_schedule([(1000000, 0)], 800),
            [{"rate_ppm": 1000000, "source_sample": 0}])
        self.assertEqual(
            reference.validate_schedule(
                [(1000000, 0), (1500000, 6400)], 800),
            [{"rate_ppm": 1000000, "source_sample": 0},
             {"rate_ppm": 1500000, "source_sample": 6400}])

    def test_schedule_rejects_adverse(self) -> None:
        cases = (
            (None, 800),
            ([], 800),
            ([(0, 0)], 800),
            ([(2000000, 0)], 800),
            ([(700000, 0)], 800),
            ([(float("nan"), 0)], 800),
            ([(1000000, 0), (1200000, 0)], 800),
            ([(1000000, 160)], 800),
            ([(1000000, 0), (1200000, -160)], 800),
            ([(1000000, 0)], -1),
            ([(1000000, 0)], 20000),
        )
        for schedule, ramp in cases:
            with self.assertRaises(reference.ReferenceRejection,
                                   msg=str(schedule)):
                reference.validate_schedule(schedule, ramp)

    def test_unknown_case_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_case_request({
                "case_id": "not_a_case",
                "samples": [0.0] * 320,
                "schedule": [(1000000, 0)],
                "ramp_samples": 800,
            })

    def test_caller_manifest_shape_only(self) -> None:
        manifest = {
            "archive_sha256": "1" * 64,
            "artifact_id": "ztx",
            "license_id": "caller-declared",
            "platform": "macos-arm64",
            "product_id": "caller-product",
            "runtime_id": "ztx.pro.v0",
            "sla_reference": "caller-sla",
            "vendor_id": "zynaptiq",
            "vendor_version": "caller-version",
        }
        result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["loaded"])
        self.assertFalse(result["executed"])
        self.assertFalse(result["verified"])

    def test_caller_manifest_adverse(self) -> None:
        manifest = {
            "archive_sha256": "1" * 64,
            "artifact_id": "ztx",
            "license_id": "caller-declared",
            "platform": "macos-arm64",
            "product_id": "caller-product",
            "runtime_id": "ztx.pro.v0",
            "sla_reference": "caller-sla",
            "vendor_id": "zynaptiq",
            "vendor_version": "caller-version",
        }
        for update in ({"archive_sha256": "zz"},
                       {"artifact_id": "other"},
                       {"vendor_id": "unknown"},
                       {"platform": ""},
                       {"extra": 1}):
            candidate = dict(manifest)
            candidate.update(update)
            with self.assertRaises(reference.ReferenceRejection, msg=update):
                reference.validate_caller_manifest(candidate)


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixtures = reference.build_fixtures()

    def test_fixture_is_deterministic(self) -> None:
        again = reference.build_fixtures()
        self.assertEqual(reference.fixture_digest(self.fixtures),
                         reference.fixture_digest(again))
        for name, fixture in self.fixtures.items():
            self.assertEqual(fixture["digest"], again[name]["digest"], name)

    def test_declared_lengths(self) -> None:
        self.assertEqual(self.fixtures["tonal"]["length"], 9600)
        self.assertEqual(self.fixtures["speech_unfamiliar"]["length"], 19200)
        self.assertEqual(self.fixtures["music"]["length"], 19200)
        self.assertEqual(self.fixtures["silence"]["length"], 9600)
        self.assertEqual(self.fixtures["transient"]["length"], 16000)
        self.assertEqual(self.fixtures["final_partial"]["length"], 12485)

    def test_silence_is_exact_zero(self) -> None:
        self.assertTrue(all(value == 0.0
                            for value in self.fixtures["silence"]["samples"]))

    def test_all_samples_finite_and_bounded(self) -> None:
        for name, fixture in self.fixtures.items():
            self.assertLessEqual(fixture["peak_micro"], 980000, name)
            self.assertLessEqual(fixture["peak_micro"], 1000000, name)

    def test_speech_labels_are_source_timestamped(self) -> None:
        labels = self.fixtures["speech_unfamiliar"]["labels"]
        self.assertEqual(len(labels), 5)
        self.assertEqual([item["decision"] for item in labels],
                         ["protect", "flex", "protect", "flex", "protect"])
        self.assertEqual(labels[-1]["source_end"], 19200)


class TransformationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixtures = reference.build_fixtures()
        cls.cases = {case["case_id"]: reference.run_case(case, cls.fixtures)
                     for case in reference.CASES}

    def test_identity_is_byte_exact(self) -> None:
        case = self.cases["identity_1x"]
        self.assertTrue(case["surrogate_checks"]["duration"])
        self.assertEqual(case["duration"]["error_samples"], 0)
        self.assertEqual(case["duration"]["actual_output_samples"], 9600)
        self.assertEqual(case["signal"]["output_digest"],
                         self.fixtures["tonal"]["digest"])

    def test_duration_is_exact(self) -> None:
        expected = {
            "speed_up_125": 7680,
            "speed_up_150": 6400,
            "speed_down_080": 12000,
            "unfamiliar_speech": 16000,
            "music_material": 13714,
            "silence_case": 7680,
            "final_partial_window": 9988,
        }
        for case_id, length in expected.items():
            case = self.cases[case_id]
            self.assertEqual(case["duration"]["error_samples"], 0, case_id)
            self.assertEqual(case["duration"]["actual_output_samples"], length,
                             case_id)

    def test_mapping_is_monotone_and_covered(self) -> None:
        for case_id, case in self.cases.items():
            mapping = case["mapping"]
            self.assertEqual(mapping["nonmonotone_window_count"], 0, case_id)
            self.assertTrue(mapping["source_interval_covered"], case_id)
            self.assertEqual(mapping["uncovered_samples"], 0, case_id)

    def test_pitch_proxy_preserved_for_strict_path(self) -> None:
        for case_id in ("identity_1x", "speed_up_125", "speed_up_150",
                        "speed_down_080"):
            pitch = self.cases[case_id]["pitch_proxy"]
            self.assertTrue(pitch["applicable"], case_id)
            self.assertTrue(pitch["pitch_preserved_proxy"], case_id)
            self.assertLessEqual(abs(pitch["scale_ppm"] - reference.MICRO),
                                 reference.PITCH_TOLERANCE_PPM, case_id)

    def test_varispeed_adverse_shifts_pitch(self) -> None:
        case = self.cases["varispeed_adverse"]
        pitch = case["pitch_proxy"]
        self.assertTrue(pitch["applicable"])
        self.assertFalse(pitch["pitch_preserved_proxy"])
        self.assertGreater(pitch["scale_ppm"], 1200000)
        self.assertFalse(case["surrogate_checks_pass"])
        self.assertTrue(case["adverse_control"])

    def test_speech_pitch_is_withheld(self) -> None:
        for case_id in ("unfamiliar_speech", "music_material", "silence_case"):
            pitch = self.cases[case_id]["pitch_proxy"]
            self.assertFalse(pitch["applicable"], case_id)
            self.assertIsNone(pitch["scale_ppm"], case_id)
            self.assertFalse(pitch["pitch_preserved_proxy"], case_id)

    def test_final_partial_window(self) -> None:
        case = self.cases["final_partial_window"]
        self.assertEqual(case["duration"]["input_samples"], 12485)
        self.assertEqual(case["playback_buffering"]["output_partial_samples"],
                         68)
        self.assertEqual(
            case["playback_buffering"]["final_partial_window_valid_samples"],
            260)

    def test_rebuffer_deficit_is_not_compensated(self) -> None:
        event = self.cases["rebuffer_case"]["playback_buffering"]["rebuffer"]
        self.assertIsNotNone(event)
        self.assertEqual(event["deficit_samples"], 1600)
        self.assertFalse(event["compensated"])
        self.assertFalse(event["device_timing_measured"])

    def test_speech_preservation_is_source_timestamped(self) -> None:
        preservation = self.cases["unfamiliar_speech"]["speech_preservation"]
        self.assertIsNotNone(preservation)
        self.assertEqual(preservation["protect_interval_count"], 3)
        for entry in preservation["entries"]:
            self.assertTrue(entry["source_timestamped"])
            if entry["decision"] == "protect":
                self.assertIsNotNone(entry["rms_ratio_db_milli"])
        self.assertFalse(preservation["qualifies_intelligibility"])

    def test_every_case_is_not_qualified(self) -> None:
        for case_id, case in self.cases.items():
            self.assertFalse(case["candidate_qualified"], case_id)
            self.assertFalse(case["qualifies"], case_id)
            self.assertFalse(case["missing_result_promoted"], case_id)

    def test_adverse_controls_never_pass(self) -> None:
        for case_id in ("varispeed_adverse", "rate_step_unsmoothed_adverse"):
            self.assertFalse(self.cases[case_id]["surrogate_checks_pass"],
                             case_id)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.digest = reference.canonical_report(cls.report)[1]
        cls.contract = reference.build_contract(cls.report, cls.digest)

    def test_report_invariants(self) -> None:
        report = self.report
        self.assertEqual(report["schema_id"], reference.REPORT_SCHEMA)
        self.assertEqual(report["status"], reference.STATUS)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["defer_before"], "opt_in_adapter_exposure")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["profile"], "rate")

    def test_qualification_not_promoted(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        for key, value in qualification.items():
            if key == "status":
                continue
            self.assertIs(value, False, key)

    def test_eight_blocked_release_gates(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-0" + str(index) for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_eight_blocked_exact_requirements(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 8)
        self.assertTrue(all(blocker["status"] == "blocked"
                            and blocker["present"] is False
                            for blocker in blockers))

    def test_candidate_is_absent(self) -> None:
        candidate = self.report["candidate"]
        for key in ("legacy_artifact_present", "ztx_sdk_present",
                    "evaluation_kit_present", "signed_sla_present",
                    "source_present", "headers_present", "runtime_present",
                    "adapter_present", "exact_geometry_documented",
                    "exact_numeric_output_present", "implemented_here"):
            self.assertIs(candidate[key], False, key)
        self.assertFalse(candidate["vendor_reported"]["locally_verified"])
        self.assertFalse(candidate["vendor_reported"]["local_run"])

    def test_format_does_not_invent_candidate_geometry(self) -> None:
        fmt = self.report["format"]
        self.assertEqual(fmt["sdk_v0_sample_rate_hz"], 16000)
        self.assertEqual(fmt["sdk_v0_channels"], 1)
        self.assertEqual(fmt["sdk_v0_frame_samples"], 160)
        for key in ("candidate_reported_sample_rate_hz",
                    "candidate_reported_block_samples",
                    "candidate_reported_channel_limit"):
            self.assertIsNone(fmt[key], key)
        self.assertFalse(fmt["candidate_geometry_documented"])

    def test_rate_profile_items_synthetic_only(self) -> None:
        items = self.report["acceptance_profile"]["required_items"]
        self.assertEqual(len(items), 15)
        self.assertTrue(all(item["status"] == "synthetic_only"
                            for item in items.values()))
        self.assertEqual(self.report["profile_blockers"], [])
        coverage = self.report["rate_profile"]["coverage"]
        self.assertTrue(all(coverage.values()))
        self.assertFalse(self.report["rate_profile"]["candidate_measured"])

    def test_results_never_qualify(self) -> None:
        cases = self.report["results"]["cases"]
        self.assertEqual(len(cases), len(reference.CASES))
        for case_id, case in cases.items():
            self.assertFalse(case["candidate_qualified"], case_id)
            self.assertFalse(case["qualifies"], case_id)
        self.assertEqual(self.report["results"]["candidate_qualified_count"], 0)

    def test_adverse_controls_present(self) -> None:
        records = self.report["adverse_rejections"]
        ids = {record["case_id"] for record in records}
        self.assertTrue(set(reference.REQUIRED_ADVERSE) <= ids)
        for record in records:
            self.assertFalse(record["candidate_qualified"])
            self.assertTrue(record["state_unchanged"])
        for case_id in reference.WITHHELD_ADVERSE:
            record = next(item for item in records
                          if item["case_id"] == case_id)
            self.assertEqual(record["status"], "metric_withheld", case_id)

    def test_external_artifacts_blocked(self) -> None:
        external = self.report["external_artifacts"]
        self.assertEqual(external["status"], "blocked")
        for key, value in external.items():
            if key in ("status", "note"):
                continue
            self.assertIs(value, False, key)

    def test_boundary_and_scope_are_clean(self) -> None:
        for key, value in self.report["boundary"].items():
            self.assertIs(value, False, key)
        scope = self.report["scope"]
        self.assertEqual(scope["write_scope"],
                         "docs/task-evidence/dirac-legacy-ztx/ only")
        for key, value in scope.items():
            if key == "write_scope":
                continue
            self.assertIs(value, False, key)

    def test_board_row_is_stable_identity_only(self) -> None:
        row = self.report["board_row"]
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(row["stable_fields"]["id"],
                         reference.TASK_ID)
        self.assertEqual(row["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(row["stable_fields"]["mode"], "external-adapter")
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         row["stable_sha256"])
        self.assertNotIn("TASKS.json", reference.canonical_text(
            self.report["source_pins"]))
        self.assertNotIn("TASKS.json", reference.canonical_text(
            self.report["boundary_pins"]))

    def test_contract_matches_report_invariants(self) -> None:
        contract = self.contract
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], reference.STATUS)
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["profile"], "rate")
        self.assertEqual(contract["release_gates"],
                         self.report["release_gates"])
        self.assertEqual(contract["exact_blockers"],
                         self.report["exact_blockers"])
        self.assertGreaterEqual(len(contract["invariants"]), 8)
        self.assertEqual(
            contract["artifact_pins"],
            reference.artifact_pins(self.digest,
                                    reference.sha256_bytes(
                                        (self.digest + "\n").encode("ascii"))))

    def test_three_rounds_are_identical(self) -> None:
        payloads = []
        for _ in range(3):
            report = reference.build_report()
            payloads.append(reference.canonical_report(report))
        self.assertEqual(payloads[0], payloads[1])
        self.assertEqual(payloads[1], payloads[2])


if __name__ == "__main__":
    unittest.main()
