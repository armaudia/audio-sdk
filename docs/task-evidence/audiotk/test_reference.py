# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the SDK-AUDIOTK evidence package."""

from __future__ import annotations

import json
import math
import unittest
from fractions import Fraction

import reference


class CanonicalTests(unittest.TestCase):
    def test_canonical_bytes_are_sorted_and_compact(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": [2, 3]})
        self.assertEqual(payload, b'{"a":[2,3],"b":1}')

    def test_canonical_bytes_reject_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"x": math.nan})

    def test_strict_loads_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_loads_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":Infinity}')

    def test_strict_loads_accepts_plain_object(self) -> None:
        self.assertEqual(reference.strict_loads('{"a":1}'), {"a": 1})

    def test_fraction_text(self) -> None:
        self.assertEqual(reference.fraction_text(Fraction(3, 4)), "3/4")
        self.assertEqual(reference.fraction_text(Fraction(2, 1)), "2")

    def test_rate_decimal_is_canonical(self) -> None:
        self.assertEqual(reference.rate_decimal(Fraction(1, 1)), "1")
        self.assertEqual(reference.rate_decimal(Fraction(3, 4)), "0.75")
        self.assertEqual(reference.rate_decimal(Fraction(4, 5)), "0.8")
        self.assertEqual(reference.rate_decimal(Fraction(5, 4)), "1.25")
        self.assertEqual(reference.rate_decimal(Fraction(3, 2)), "1.5")

    def test_rate_decimal_rejects_repeating(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.rate_decimal(Fraction(1, 3))

    def test_parse_rate_rejects_aliases(self) -> None:
        for value in ("0.750", "1e0", "+1", "-0", ".5", "1.", "00.5"):
            with self.subTest(value=value):
                with self.assertRaises(reference.Reject):
                    reference.parse_rate(value, "rate")


class IdentityTests(unittest.TestCase):
    def test_task_row_identity_is_linked_and_not_whole_file(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["source"],
                         "audio-benchmark-platform/plan/swarm/TASKS.json")
        self.assertFalse(identity["whole_file_hashed"])
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(identity["stable_sha256"],
                         reference.sha256(reference.canonical_bytes(
                             identity["stable_fields"])))
        self.assertEqual(set(identity["excluded_mutable_fields"]),
                         set(reference.MUTABLE_TASK_FIELDS))

    def test_claim_matches_constants(self) -> None:
        claim = reference.task_row_identity()["claim"]
        self.assertEqual(claim["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(claim["branch"], reference.BRANCH)
        self.assertEqual(claim["worktree"], reference.CLAIM_WORKTREE)
        self.assertEqual(claim["reviewer"], reference.REVIEWER)


class AuditTests(unittest.TestCase):
    def test_absence_probes_are_all_absent(self) -> None:
        probes = reference.probe_absence()
        self.assertEqual(len(probes), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(not item["exists"] for item in probes))

    def test_asset_audit_is_absent_and_not_qualified(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["source_checkout_present"])
        self.assertIsNone(audit["source_revision"])
        self.assertFalse(audit["license_file_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["runtime_lock_present"])
        self.assertFalse(audit["build_record_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["parity_manifest_present"])
        self.assertFalse(audit["supporting_dsp_plan_present"])
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertFalse(audit["weights_present"])

    def test_supporting_dsp_audit_keeps_sources_separate(self) -> None:
        audit = reference.audit_supporting_dsp()
        self.assertFalse(audit["audiotk_source_present"])
        self.assertIsNone(audit["audiotk_revision"])
        self.assertEqual(audit["recorded_license"], "BSD-3-Clause")
        self.assertEqual(audit["recorded_role"], "supporting_dsp_only")
        self.assertFalse(audit["recorded_time_stretch_stage_found"])
        self.assertTrue(audit["existing_sdk_dsp"])
        self.assertTrue(all(item["present"]
                            for item in audit["existing_sdk_dsp"]))
        self.assertTrue(all(item["pinned"] and item["matches_boundary_pin"]
                            for item in audit["existing_sdk_dsp"]
                            if item["path"] in reference.BOUNDARY_PINS))
        self.assertTrue(audit["sibling_rate_packages"])
        self.assertTrue(all(
            item["role"] == "sibling_rate_evidence_not_attributed"
            for item in audit["sibling_rate_packages"]))
        self.assertIn("no_audiotk_reuse", audit["reuse_decision"])


class RateAccountingTests(unittest.TestCase):
    def test_rate_table_is_exact(self) -> None:
        rows = reference.rate_table()
        observed = [(row["rate"], row["source_samples"],
                     row["output_samples"], row["duration_ratio"])
                    for row in rows]
        self.assertEqual(observed, [
            ("1", 48000, 48000, "1"),
            ("0.75", 48000, 64000, "4/3"),
            ("0.8", 48000, 60000, "5/4"),
            ("1.25", 48000, 38400, "4/5"),
            ("1.5", 48000, 32000, "2/3"),
        ])
        self.assertTrue(all(row["audio_produced"] is False for row in rows))

    def test_schedule_maps_half_open_intervals(self) -> None:
        schedule = reference.rate_schedule([
            (Fraction(1, 1), 8000),
            (Fraction(4, 5), 16000),
            (Fraction(5, 4), 12000),
            (Fraction(1, 1), 12000),
        ])
        self.assertEqual(schedule["source_samples"], 48000)
        self.assertEqual(schedule["output_samples"], 49600)
        self.assertEqual(schedule["output_ratio"], "31/30")
        self.assertEqual(schedule["rate_change_count"], 3)
        segments = schedule["segments"]
        self.assertEqual([segments[0]["source_start"],
                          segments[0]["source_end"]], [0, 8000])
        self.assertEqual([segment["output_end"] for segment in segments],
                         [8000, 28000, 37600, 49600])
        for previous, current in zip(segments, segments[1:]):
            self.assertEqual(previous["source_end"], current["source_start"])
            self.assertEqual(previous["output_end"], current["output_start"])

    def test_schedule_rejects_bad_length(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.rate_schedule([(Fraction(1, 1), 100)])

    def test_duration_ratios_match_expected(self) -> None:
        durations = reference.duration_accounting(reference.rate_table())
        self.assertTrue(durations["all_ratios_match"])
        self.assertFalse(durations["audio_produced"])
        for row in durations["rows"]:
            self.assertEqual(row["duration_ratio"], row["expected_ratio"])

    def test_final_partial_window_is_zero_padded(self) -> None:
        window = reference.final_partial_window()
        self.assertEqual(window["valid_samples"], 37)
        self.assertEqual(window["padded_samples"], 160)
        self.assertEqual(window["padding_samples"], 123)
        self.assertTrue(window["zero_padded"])
        self.assertFalse(window["audio_produced"])

    def test_identity_mapping_is_not_processing(self) -> None:
        identity = reference.paired_identity(reference.synthetic_pcm())
        self.assertTrue(identity["identity_mapping"])
        self.assertFalse(identity["processing_performed"])
        self.assertTrue(identity["bytes_equal"])
        self.assertFalse(identity["audio_output_claimed"])
        self.assertEqual(identity["source"]["samples"], 48000)

    def test_rate_mapping_rejects_adverse(self) -> None:
        for rate in (0, -1, math.nan, math.inf, Fraction(1, 4),
                     Fraction(5, 2), True, "fast"):
            with self.subTest(rate=rate):
                with self.assertRaises(reference.Reject):
                    reference.rate_mapping(rate, 160)

    def test_pause_policy_is_source_anchored(self) -> None:
        policy = reference.validate_pause_policy(
            list(reference.PAUSE_POLICY), reference.CONTROL_SOURCE_SAMPLES)
        self.assertEqual(policy["interval_count"], 2)
        self.assertTrue(policy["source_anchored"])
        self.assertFalse(policy["speech_preservation_measured"])
        self.assertIsNone(policy["speech_preserved"])

    def test_pause_policy_rejects_output_anchoring(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_pause_policy(
                [{"id": "x", "output_start": 0, "output_end": 10}],
                reference.CONTROL_SOURCE_SAMPLES)


class PcmTests(unittest.TestCase):
    def test_synthetic_pcm_is_finite_and_bounded(self) -> None:
        summary = reference.pcm_summary(reference.synthetic_pcm())
        self.assertEqual(summary["samples"], 48000)
        self.assertEqual(summary["sample_rate_hz"], 16000)
        self.assertEqual(summary["channels"], 1)
        self.assertLessEqual(summary["peak_abs"], 1.0)
        self.assertEqual(summary["nonfinite_samples"], 0)

    def test_pcm_rejects_invalid_inputs(self) -> None:
        cases = ([], b"\x00", None, [0.0, math.nan], [0.0, math.inf],
                 [0.0, -math.inf], [0.0, 1.5], [0.0, True], [0.0, "0.1"])
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaises(reference.Reject):
                    reference.validate_pcm(value)

    def test_pcm_rejects_wrong_geometry(self) -> None:
        good = [0.0, 0.1]
        with self.assertRaises(reference.Reject):
            reference.validate_pcm(good, 8000)
        with self.assertRaises(reference.Reject):
            reference.validate_pcm(good, 16000, 2)


class ManifestTests(unittest.TestCase):
    def test_shape_only_manifest_reaches_the_missing_asset_branch(self) -> None:
        with self.assertRaises(reference.Reject) as caught:
            reference.validate_caller_manifest(
                reference._shape_only_manifest())
        self.assertIn("directory is missing", str(caught.exception))

    def test_existing_file_manifest_is_accepted(self) -> None:
        result = reference.validate_caller_manifest(
            reference._existing_file_manifest())
        self.assertTrue(result["accepted"])
        self.assertFalse(result["audiotk_executed"])
        self.assertEqual(result["variant"], reference.CALLER_VARIANT)
        self.assertFalse(result["time_stretch_capability_claimed"])
        self.assertFalse(result["revision_pin_available"])

    def test_manifest_rejects_unknown_and_missing_fields(self) -> None:
        good = reference._shape_only_manifest()
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(dict(good, extra="x"))
        for key in reference.CALLER_ASSET_FIELDS:
            stripped = {k: v for k, v in good.items() if k != key}
            with self.subTest(key=key):
                with self.assertRaises(reference.Reject):
                    reference.validate_caller_manifest(stripped)

    def test_manifest_rejects_time_stretch_claim(self) -> None:
        good = reference._shape_only_manifest()
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(
                dict(good, claimed_time_stretch_capability=True))

    def test_manifest_rejects_noncanonical_rates(self) -> None:
        good = reference._shape_only_manifest()
        for field, value in (("rate_min", "0.750"), ("rate_max", "1e0"),
                             ("rate_min", "0"), ("rate_max", "2.5"),
                             ("rate_min", "1.5")):
            with self.subTest(field=field, value=value):
                with self.assertRaises(reference.Reject):
                    reference.validate_caller_manifest(
                        dict(good, **{field: value}))

    def test_manifest_rejects_short_revision(self) -> None:
        good = reference._shape_only_manifest()
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(
                dict(good, source_revision="7dae8a2"))


class ControlAndReportTests(unittest.TestCase):
    def test_adverse_cases_all_rejected_in_order(self) -> None:
        results = reference.run_adverse_controls()
        self.assertEqual(len(results), len(reference.ADVERSE_CASE_IDS))
        self.assertEqual([item["case"] for item in results],
                         list(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(item["result"] == "rejected"
                            for item in results))

    def test_qualification_gate_fails_closed(self) -> None:
        for evidence in (None, [], {}, {"exact_source_and_asset_identity":
                                        "passed"}):
            with self.subTest(evidence=evidence):
                with self.assertRaises(reference.Reject):
                    reference.qualification_gate(evidence)

    def test_report_disposition_and_gates(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertTrue(
            report["qualification"]["no_missing_result_qualifies_candidate"])
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in report["gates"]))
        self.assertEqual([gate["id"] for gate in report["gates"]],
                         [gate for gate, _ in reference.GATE_REQUIREMENTS])
        self.assertEqual(len(report["exact_blockers"]), 8)
        self.assertEqual([item["id"] for item in report["exact_blockers"]],
                         [item["id"] for item in reference.EXACT_BLOCKERS])
        self.assertTrue(all(gate["qualification_effect"] == "none"
                            for gate in report["rate_profile"][
                                "required_items"]))
        self.assertEqual(report["rate_profile"][
            "satisfied_for_qualification"], [])
        self.assertIsNone(report["candidate_metrics"])

    def test_report_boundary_and_scope_are_closed(self) -> None:
        report = reference.build_report()
        self.assertTrue(all(report["boundary"][flag] is False
                            for flag in reference.BOUNDARY_FALSE_FLAGS))
        self.assertEqual(report["boundary"]["descriptor_settings"], {})
        self.assertTrue(all(report["scope"][flag] is False
                            for flag in reference.SCOPE_FALSE_FLAGS))
        self.assertTrue(report["scope"]["task_local_only"])
        self.assertFalse(report["reference_protocol"][
            "geometry"]["performs_time_scale_modification"])
        self.assertFalse(report["reference_protocol"][
            "geometry"]["audio_output_produced"])
        self.assertEqual(report["reference_protocol"]["executor"], "absent")

    def test_report_absence_and_missing_artifacts(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["asset_audit"]["audit_result"], "absent")
        self.assertFalse(report["asset_audit"]["qualified"])
        self.assertIsNone(report["upstream_identity"]["revision"])
        self.assertFalse(report["upstream_identity"][
            "revision_pin_available"])
        self.assertIsNone(report["upstream_identity"]["repository_url"])
        self.assertFalse(report["format"]["task_geometry_asserted"])
        for path in (reference.MISSING_SOURCE_PATH,
                     reference.RUNTIME_ENV_PATH,
                     reference.BUILD_RECORD_PATH,
                     reference.RIGHTS_RECORD_PATH,
                     reference.COHORT_MANIFEST_PATH,
                     reference.PARITY_MANIFEST_PATH,
                     reference.SUPPORTING_DSP_PLAN_PATH):
            self.assertIn(path, report["missing_historical_artifacts"])

    def test_contract_mirrors_report_decisions(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertEqual(contract["reviewer"], reference.REVIEWER)
        self.assertEqual(contract["write_scope"], reference.TASK_PREFIX)
        self.assertEqual(len(contract["gates"]), 8)
        self.assertEqual(len(contract["exact_blockers"]), 8)
        self.assertEqual(contract["reproduction"][
            "cold_start_regenerations"], 3)
        self.assertFalse(contract["licensing"]["upstream_license_verified"])
        self.assertFalse(contract["source_checkout"]["present"])

    def test_report_and_contract_bytes_are_stable(self) -> None:
        first = reference.canonical_report_bytes(reference.build_report())
        second = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertEqual(reference.canonical_contract_bytes(),
                         reference.canonical_contract_bytes())
        self.assertTrue(reference.strict_loads(first.decode("utf-8")))

    def test_report_has_no_whole_file_task_digest(self) -> None:
        encoded = reference.canonical_bytes(
            reference.build_report()).decode("utf-8")
        self.assertNotIn('TASKS.json":"', encoded)


if __name__ == "__main__":
    unittest.main()
