# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the SDK-CLEARSCALE blocker package."""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from fractions import Fraction
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class JsonAndCanonicalTests(unittest.TestCase):
    def test_canonical_json_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"value": math.nan})
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"value": math.inf})

    def test_strict_json_rejects_duplicate_key(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_rejects_infinity_constant(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":Infinity}')

    def test_strict_json_requires_object(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads("[1,2]")

    def test_canonical_normalizes_negative_zero(self) -> None:
        self.assertEqual(reference.canonical_bytes({"x": -0.0}),
                         b'{"x":0.0}')

    def test_fraction_text(self) -> None:
        self.assertEqual(reference.fraction_text(Fraction(4, 2)), "2")
        self.assertEqual(reference.fraction_text(Fraction(3, 2)), "3/2")


class SourceAuditTests(unittest.TestCase):
    def test_source_checkout_is_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["source_checkout_present"])
        self.assertIsNone(audit["source_revision"])
        self.assertFalse(audit["source_revision_pin_available"])

    def test_no_license_implementation_or_runtime(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["license_file_present"])
        self.assertFalse(audit["implementation_artifact_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["runtime_lock_present"])

    def test_no_rights_cohort_or_parity(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["license_record_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["output_use_grant_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["parity_manifest_present"])

    def test_absence_probes_are_all_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertTrue(audit["all_absence_probes_absent"])
        for probe in audit["absence_probes"]:
            self.assertFalse(probe["exists"], probe["path"])

    def test_geometry_is_unestablished(self) -> None:
        audit = reference.audit_assets()
        requested = audit["requested_config"]
        self.assertEqual(requested["geometry_status"], "unestablished")
        self.assertFalse(requested["pinned_candidate_source"])
        self.assertFalse(requested["neural_weights_applicable"])


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        stable = identity["stable_fields"]
        self.assertEqual(stable["id"], "SDK-CLEARSCALE")
        self.assertEqual(stable["component"], "clearscale")
        self.assertEqual(stable["repository"], "audio-sdk")
        self.assertEqual(stable["mode"], "research-control")
        self.assertEqual(identity["claim"]["base_commit"],
                         reference.BASE_COMMIT)

    def test_mutable_fields_excluded(self) -> None:
        identity = reference.task_row_identity()
        for field in ("owner", "status", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertIn(field, identity["excluded_mutable_fields"])
            self.assertNotIn(field, identity["stable_fields"])

    def test_commits_are_full_hex(self) -> None:
        self.assertRegex(reference.BASE_COMMIT, r"^[0-9a-f]{40}$")
        self.assertEqual(len(reference.BASE_COMMIT), 40)

    def test_whole_board_is_not_hashed(self) -> None:
        identity = reference.task_row_identity()
        self.assertFalse(identity["whole_file_hashed"])


class PcmTests(unittest.TestCase):
    def test_synthetic_pcm_is_deterministic(self) -> None:
        self.assertEqual(reference.synthetic_input_pcm(),
                         reference.synthetic_input_pcm())

    def test_synthetic_pcm_is_finite_and_bounded(self) -> None:
        signal = reference.synthetic_input_pcm()
        self.assertEqual(len(signal), reference.CONTROL_SOURCE_SAMPLES)
        self.assertTrue(all(math.isfinite(value) for value in signal))
        self.assertTrue(all(-1.0 <= value <= 1.0 for value in signal))

    def test_pcm_summary_is_deterministic(self) -> None:
        signal = reference.synthetic_input_pcm()
        first = reference.pcm_summary(signal, 16000)
        second = reference.pcm_summary(signal, 16000)
        self.assertEqual(first, second)
        self.assertEqual(first["sample_count"], reference.CONTROL_SOURCE_SAMPLES)

    def test_validate_pcm_accepts_integers(self) -> None:
        self.assertEqual(reference.validate_pcm([0, 1, -1]),
                         [0.0, 1.0, -1.0])

    def test_validate_pcm_rejects_invalid(self) -> None:
        for value in ([], None, b"\x00", [math.nan], [math.inf],
                      [-math.inf], [1.5], [True], ["0.1"]):
            with self.assertRaises(reference.Reject):
                reference.validate_pcm(value)
        with self.assertRaises(reference.Reject):
            reference.validate_pcm([0.0], 8000)
        with self.assertRaises(reference.Reject):
            reference.validate_pcm([0.0], 16000, 2)
        with self.assertRaises(reference.Reject):
            reference.validate_pcm([0.0], expected_samples=2)


class RateTests(unittest.TestCase):
    def test_parse_rate_accepts_rationals(self) -> None:
        self.assertEqual(reference.parse_rate("1"), Fraction(1, 1))
        self.assertEqual(reference.parse_rate("3/2"), Fraction(3, 2))
        self.assertEqual(reference.parse_rate(2), Fraction(2, 1))

    def test_parse_rate_rejects_invalid(self) -> None:
        for value in (None, True, 0, -1, math.nan, math.inf, "NaN", "inf",
                      "1/0", "fast", "5/2", "1/4", 1.25):
            with self.assertRaises(reference.Reject):
                reference.parse_rate(value)

    def test_identity_mapping_is_exact(self) -> None:
        mapping = reference.rate_mapping(
            [{"start": 0, "end": 48000, "rate": "1"}])
        self.assertEqual(mapping["output_duration"], "48000")
        self.assertEqual(mapping["output_samples_floor"], 48000)
        self.assertEqual(mapping["output_samples_ceil"], 48000)
        self.assertTrue(mapping["duration_identity"])
        self.assertFalse(mapping["final_partial_window"]["partial"])

    def test_faster_and_slower_mapping(self) -> None:
        faster = reference.rate_mapping(
            [{"start": 0, "end": 48000, "rate": "3/2"}])
        slower = reference.rate_mapping(
            [{"start": 0, "end": 48000, "rate": "2/3"}])
        self.assertEqual(faster["output_duration"], "32000")
        self.assertEqual(slower["output_duration"], "72000")
        self.assertTrue(faster["duration_identity"])
        self.assertTrue(slower["duration_identity"])

    def test_rate_change_mapping_is_contiguous(self) -> None:
        mapping = reference.rate_mapping([
            {"start": 0, "end": 16000, "rate": "1"},
            {"start": 16000, "end": 32000, "rate": "3/2"},
            {"start": 32000, "end": 48000, "rate": "2/3"},
        ])
        self.assertEqual(mapping["output_duration"], "152000/3")
        self.assertEqual(mapping["output_samples_floor"], 50666)
        self.assertEqual(mapping["output_samples_ceil"], 50667)
        self.assertTrue(mapping["source_mapping_contiguous"])
        self.assertEqual(len(mapping["records"]), 3)
        self.assertEqual(mapping["records"][1]["output_duration"], "32000/3")

    def test_fractional_final_partial_window(self) -> None:
        mapping = reference.rate_mapping(
            [{"start": 0, "end": 48000, "rate": "7/4"}])
        self.assertEqual(mapping["output_duration"], "192000/7")
        self.assertEqual(mapping["output_samples_floor"], 27428)
        self.assertEqual(mapping["output_samples_ceil"], 27429)
        self.assertTrue(mapping["final_partial_window"]["partial"])
        self.assertEqual(mapping["final_partial_window"]["fractional_output"],
                         "4/7")
        self.assertFalse(mapping["duration_identity"])

    def test_schedule_validation_rejects_bad_shapes(self) -> None:
        bad = [
            None, b"\x00", [], [1],
            [{"start": 0, "end": 48000}],
            [{"start": 0, "end": 48000, "rate": "1", "extra": 1}],
            [{"start": True, "end": 48000, "rate": "1"}],
            [{"start": 0.0, "end": 48000, "rate": "1"}],
            [{"start": -1, "end": 48000, "rate": "1"}],
            [{"start": 10, "end": 10, "rate": "1"}],
            [{"start": 10, "end": 9, "rate": "1"}],
            [{"start": 0, "end": 48001, "rate": "1"}],
            [{"start": 0, "end": 10, "rate": "1"},
             {"start": 11, "end": 48000, "rate": "1"}],
            [{"start": 0, "end": 20, "rate": "1"},
             {"start": 10, "end": 48000, "rate": "1"}],
            [{"start": 10, "end": 48000, "rate": "1"},
             {"start": 0, "end": 10, "rate": "1"}],
            [{"start": 0, "end": 47999, "rate": "1"}],
        ]
        for value in bad:
            with self.assertRaises(reference.Reject):
                reference.validate_rate_schedule(value)

    def test_mapping_is_not_candidate_audio(self) -> None:
        mapping = reference.rate_mapping(
            [{"start": 0, "end": 48000, "rate": "3/2"}])
        self.assertFalse(mapping["performs_time_stretch"])
        self.assertFalse(mapping["output_is_candidate_audio"])
        self.assertFalse(mapping["qualifies"])
        self.assertEqual(mapping["evidence_class"],
                         "synthetic_contract_control_not_evidence")


class ManifestTests(unittest.TestCase):
    def test_manifest_accepts_complete_asset_set(self) -> None:
        result = reference.validate_caller_manifest(
            reference._existing_file_manifest())
        self.assertTrue(result["accepted"])
        self.assertFalse(result["implementation_executed"])
        self.assertFalse(result["neural_weights_applicable"])
        self.assertEqual(result["files_checked"], 8)
        self.assertEqual(result["directories_checked"], 2)

    def test_manifest_rejects_missing_asset(self) -> None:
        manifest = reference._existing_file_manifest()
        manifest["implementation_path"] = "/nonexistent/clearscale/x.bin"
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_hash_mismatch(self) -> None:
        manifest = reference._existing_file_manifest()
        manifest["implementation_sha256"] = "0" * 64
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_missing_directory(self) -> None:
        manifest = reference._existing_file_manifest()
        manifest["runtime_path"] = "/nonexistent/clearscale/no-runtime"
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_relative_path(self) -> None:
        manifest = reference._existing_file_manifest()
        manifest["implementation_path"] = "implementation.bin"
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_short_or_nonhex_revision(self) -> None:
        manifest = reference._existing_file_manifest()
        manifest["source_revision"] = "7dae8a2"
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(manifest)
        manifest["source_revision"] = "g" * 40
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_wrong_variant(self) -> None:
        manifest = reference._existing_file_manifest()
        manifest["variant"] = "offline_batch_stretch"
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_float_geometry(self) -> None:
        manifest = reference._existing_file_manifest()
        manifest["sample_rate_hz"] = 16000.0
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_wrong_geometry(self) -> None:
        for field, value in (("sample_rate_hz", 48000),
                             ("channels", 2),
                             ("frame_samples", 512)):
            manifest = reference._existing_file_manifest()
            manifest[field] = value
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)


class AdverseControlTests(unittest.TestCase):
    def test_all_adverse_cases_are_invoked_and_rejected(self) -> None:
        results = reference.run_adverse_controls()
        self.assertEqual(len(results), len(reference.ADVERSE_CASE_IDS))
        self.assertEqual([item["case"] for item in results],
                         list(reference.ADVERSE_CASE_IDS))
        for item in results:
            self.assertEqual(item["result"], "rejected", item)

    def test_control_is_labelled_synthetic(self) -> None:
        control = reference.build_control()
        self.assertFalse(control["implementation_executed"])
        self.assertFalse(control["model_executed"])
        self.assertEqual(control["geometry"]["task_geometry_status"],
                         "unestablished")
        for schedule in control["rate_schedules"]:
            mapping = schedule["mapping"]
            self.assertFalse(mapping["qualifies"])
            self.assertFalse(mapping["output_is_candidate_audio"])

    def test_acceptance_outcomes_are_all_unmeasured(self) -> None:
        claims = reference.build_control()["control_claims"]
        for key in ("pitch_measured", "transient_audibility_measured",
                    "speech_preservation_measured",
                    "playback_buffering_measured", "device_timing_measured",
                    "listening_conducted", "candidate_audio_produced"):
            self.assertFalse(claims[key], key)
        self.assertEqual(claims["qualification_effect"], "none")

    def test_rate_profile_has_no_satisfied_item(self) -> None:
        report = reference.build_report()
        profile = report["rate_profile"]
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertEqual(len(profile["unsatisfied_for_qualification"]),
                         len(reference.RATE_REQUIREMENTS))
        for item in profile["required_items"]:
            self.assertFalse(item["satisfied_for_qualification"])
            self.assertEqual(item["qualification_effect"], "none")


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_top_level_decision(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertTrue(self.report["proposal_only"])
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual(
            [gate["id"] for gate in gates],
            [gate for gate, _ in reference.GATE_REQUIREMENTS])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])

    def test_eight_exact_blockers(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 8)
        for blocker in blockers:
            self.assertEqual(blocker["state"], "absent")

    def test_qualification_blocked(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertTrue(
            qualification["no_missing_result_qualifies_candidate"])
        self.assertEqual(qualification["blocked_gate_count"], 8)
        self.assertEqual(qualification["decision"], "DEFER")

    def test_boundary_is_closed(self) -> None:
        for key, value in self.report["boundary"].items():
            if key == "descriptor_settings":
                self.assertEqual(value, {})
            else:
                self.assertFalse(value, key)

    def test_scope_is_closed(self) -> None:
        for key, value in self.report["scope"].items():
            if key == "task_local_only":
                self.assertTrue(value)
            else:
                self.assertFalse(value, key)

    def test_no_fabricated_identity(self) -> None:
        upstream = self.report["upstream_identity"]
        self.assertIsNone(upstream["project_url"])
        self.assertIsNone(upstream["repository_url"])
        self.assertIsNone(upstream["revision"])
        self.assertFalse(upstream["revision_pin_available"])
        self.assertFalse(upstream["pinned_candidate_source_present"])
        self.assertFalse(upstream["neural_weights_applicable"])

    def test_audit_is_absent_and_not_qualified(self) -> None:
        audit = self.report["asset_audit"]
        self.assertEqual(audit["audit_result"], "absent")
        self.assertFalse(audit["qualified"])
        self.assertFalse(audit["source_present"])
        self.assertFalse(audit["implementation_artifact_present"])
        self.assertFalse(audit["runtime_lock_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertTrue(audit["all_absence_probes_absent"])

    def test_no_whole_file_tasks_hash(self) -> None:
        identity = self.report["task_row_identity"]
        self.assertFalse(identity["whole_file_hashed"])
        self.assertNotIn("TASKS.json", self.report["source_pins"])
        self.assertNotIn("TASKS.json", self.report["boundary_pins"])

    def test_source_reported_context_is_adjacent_only(self) -> None:
        context = self.report["source_reported_context"]
        self.assertFalse(context["is_benchmark_report"])
        self.assertTrue(context["source_reported_not_reexecuted"])
        self.assertIn("abandoned", context["candidate_status_quote"])
        self.assertIn("no usable current licence/status",
                      context["candidate_status_quote"])

    def test_sibling_evidence_is_not_candidate_evidence(self) -> None:
        siblings = self.report["sibling_evidence"]
        self.assertGreaterEqual(len(siblings), 6)
        ids = {item["id"] for item in siblings}
        self.assertIn("audiosr", ids)
        self.assertIn("gtcrn-dns3-offline", ids)
        self.assertIn("soundtouch", ids)
        for item in siblings:
            self.assertNotEqual(item["id"], "clearscale")
            self.assertTrue(item["role"])

    def test_missing_artifacts_recorded(self) -> None:
        for path in self.report["missing_historical_artifacts"]:
            self.assertFalse((reference.SOURCE_ROOT / path).exists(), path)

    def test_report_is_deterministic(self) -> None:
        self.assertEqual(reference.canonical_report_bytes(self.report),
                         reference.canonical_report_bytes(
                             reference.build_report()))

    def test_on_disk_report_matches_generator(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        self.assertEqual(payload,
                         reference.canonical_report_bytes(self.report))

    def test_sidecar_matches_report(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        sidecar = (HERE / "report.json.sha256").read_text(
            encoding="utf-8")
        self.assertEqual(sidecar, f"{sha256(payload)}  report.json\n")

    def test_on_disk_contract_matches_generator(self) -> None:
        self.assertEqual((HERE / "contract.json").read_bytes(),
                         reference.canonical_contract_bytes())

    def test_contract_matches_report(self) -> None:
        contract = json.loads((HERE / "contract.json").read_text(
            encoding="utf-8"))
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "proposal_only_incomplete")
        self.assertEqual(contract["qualification"]["status"],
                         "not_qualified")
        self.assertEqual(len(contract["gates"]), 8)
        self.assertEqual(len(contract["exact_blockers"]), 8)
        self.assertEqual(contract["write_scope"],
                         "docs/task-evidence/clearscale/")

    def test_sources_manifest_has_no_tasks_json(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        pin_lines = [line for line in text.splitlines()
                     if line and not line.startswith("#")]
        for line in pin_lines:
            self.assertNotIn("TASKS.json", line)
        self.assertIn("source:cpp-library/pipeline-validation/"
                      "playback-speed-candidates.md", text)
        self.assertIn("sibling:docs/task-evidence/soundtouch/report.json",
                      text)


if __name__ == "__main__":
    unittest.main()
