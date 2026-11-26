# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the BIC speaker-segmentation evidence package."""

from __future__ import annotations

import copy
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

import reference
import run

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


class StrictJsonTests(unittest.TestCase):
    def test_canonical_bytes_are_order_independent(self):
        self.assertEqual(
            reference.canonical_bytes({"b": 1, "a": [2, 3]}),
            reference.canonical_bytes({"a": [2, 3], "b": 1}),
        )

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_nonfinite_json_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(reference.Reject):
                    reference.strict_loads('{"a":%s}' % token)

    def test_noncanonical_python_value_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"a": float("nan")})

    def test_missing_json_file_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.strict_load(HERE / "missing.json")


class BicMathTests(unittest.TestCase):
    def test_planted_split_has_positive_bic_delta(self):
        stream = reference.synthetic_feature_stream()
        score = reference.bic_delta(stream[15:30], stream[30:45])
        self.assertGreater(score, 0)

    def test_same_distribution_has_negative_bic_delta(self):
        stream = reference.synthetic_feature_stream()
        score = reference.bic_delta(stream[30:45], stream[45:60])
        self.assertLess(score, 0)

    def test_detector_finds_exact_planted_boundaries(self):
        result = reference.detect_change_points(
            reference.synthetic_feature_stream()
        )
        self.assertEqual(result["change_points"], [30, 60])
        self.assertFalse(result["causal"])
        self.assertEqual(result["lookahead_frames"], 15)
        self.assertEqual(
            result["segments"],
            [
                {
                    "start_frame": 0,
                    "end_frame": 30,
                    "start_sample": 0,
                    "end_sample": 4800,
                },
                {
                    "start_frame": 30,
                    "end_frame": 60,
                    "start_sample": 4800,
                    "end_sample": 9600,
                },
                {
                    "start_frame": 60,
                    "end_frame": 90,
                    "start_sample": 9600,
                    "end_sample": 14400,
                },
            ],
        )

    def test_detector_is_deterministic(self):
        first = reference.detect_change_points(
            reference.synthetic_feature_stream()
        )
        second = reference.detect_change_points(
            reference.synthetic_feature_stream()
        )
        self.assertEqual(first, second)

    def test_constant_stream_has_no_change(self):
        result = reference.detect_change_points(
            reference.constant_feature_stream()
        )
        self.assertEqual(result["change_points"], [])

    def test_singular_covariance_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.detect_change_points(
                tuple((reference.Fraction(0), reference.Fraction(0))
                      for _ in range(40))
            )

    def test_score_text_is_bounded_and_canonical(self):
        text = reference.score_text(reference.Decimal("1.2300000000004"))
        self.assertEqual(text, "1.23")
        self.assertEqual(reference.score_text(reference.Decimal("-0")), "0")
        self.assertNotIn("e", text)

    def test_geometry_validation(self):
        cases = (
            {"window_frames": 1},
            {"window_frames": 15.5},
            {"hop_frames": 0},
            {"min_segment_frames": 5},
            {"penalty_weight": -1},
            {"penalty_weight": float("inf")},
            {"threshold": float("nan")},
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(reference.Reject):
                    reference.detect_change_points(
                        reference.synthetic_feature_stream(), **kwargs
                    )

    def test_nonfinite_and_bool_features_rejected(self):
        cases = (
            [(0.0, float("nan"))] * 40,
            [(0.0, float("inf"))] * 40,
            [(True, 0)] * 40,
            [("0", 0)] * 40,
            [(10 ** 9, 0)] * 40,
        )
        for stream in cases:
            with self.subTest(stream=stream[:1]):
                with self.assertRaises(reference.Reject):
                    reference.detect_change_points(stream)


class SyntheticControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_control_is_explicitly_non_qualifying(self):
        control = self.report["synthetic_control"]
        self.assertIs(control["qualifies_candidate"], False)
        self.assertIs(control["not_audio"], True)
        self.assertIs(control["not_speaker_evidence"], True)
        self.assertEqual(
            control["metric_scope"],
            "synthetic_feature_domain_not_a_segmentation_result",
        )
        self.assertEqual(control["detected_boundaries"], [30, 60])
        self.assertEqual(control["false_alarms"], [])
        self.assertEqual(control["misses"], [])
        self.assertEqual(control["matched_boundary_offsets_frames"], [0, 0])

    def test_negative_and_singular_controls(self):
        control = self.report["synthetic_control"]
        self.assertEqual(control["negative_control"]["result"], "no_change")
        self.assertIs(
            control["negative_control"]["qualifies_candidate"], False
        )
        self.assertEqual(
            control["singular_control"]["result"], "rejected"
        )

    def test_candidate_metrics_are_all_null(self):
        metrics = self.report["candidate_metrics"]
        self.assertIs(metrics["derived_from_synthetic_control"], False)
        for name in (
            "boundary_precision",
            "boundary_recall",
            "false_alarm_rate",
            "miss_rate",
            "boundary_deviation_ms",
            "segment_purity",
        ):
            self.assertIsNone(metrics[name]["value"], name)
            self.assertIs(metrics[name]["measured"], False, name)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.raw = reference.canonical_report_bytes(cls.report)

    def test_disposition_is_defer_incomplete_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertIn("incomplete", self.report["status"])
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertIs(self.report["proposal_only"], True)
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["qualification_status"], "not_qualified")
        self.assertIs(qualification["candidate_qualified"], False)
        self.assertIs(qualification["proposal_only"], True)
        self.assertIs(
            qualification["no_missing_result_qualifies_candidate"], True
        )
        self.assertIs(
            qualification["synthetic_control_is_not_candidate_evidence"], True
        )

    def test_eight_blocked_release_gates(self):
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["blocked"] is True for gate in gates))
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertEqual(
            [gate["id"] for gate in gates],
            [gate_id for gate_id, _ in reference.GATE_REQUIREMENTS],
        )

    def test_eight_exact_blockers_align_with_gates(self):
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 8)
        self.assertEqual(
            {row["id"] for row in blockers},
            {
                "source_checkout_absent",
                "upstream_identity_unpinned",
                "runtime_and_build_record_absent",
                "source_license_and_rights_unverified",
                "speaker_change_corpus_and_rights_absent",
                "task_geometry_and_adapter_absent",
                "exact_reference_parity_absent",
                "benchmark_and_release_absent",
            },
        )
        self.assertEqual(len(self.report["reopen_conditions"]), 8)

    def test_boundary_and_scope_are_closed(self):
        self.assertTrue(self.report["boundary"])
        for key, value in self.report["boundary"].items():
            self.assertIs(value, False, key)
        for key in (
            "real_audio",
            "real_corpus",
            "annotated_meeting_corpus",
            "speaker_change_execution",
            "false_alarm_rate_measured",
            "segment_purity_measured",
            "numeric_parity_claim",
            "device_timing",
            "benchmark_claim",
            "release_claim",
        ):
            self.assertIs(self.report["scope"][key], False, key)
        for key in (
            "task_local_only",
            "proposal_only",
            "feature_domain_synthetic_control",
        ):
            self.assertIs(self.report["scope"][key], True, key)

    def test_task_row_identity_is_stable_and_not_whole_file(self):
        identity = self.report["task_row_identity"]
        self.assertEqual(
            identity["stable_fields"]["id"],
            "SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION",
        )
        self.assertEqual(
            identity["stable_fields"]["component"],
            "bayesian-information-criterion-speaker-segmentation",
        )
        self.assertEqual(identity["stable_fields"]["mode"], "feasibility")
        self.assertIs(identity["whole_file_hashed"], False)
        self.assertEqual(len(identity["stable_sha256"]), 64)
        self.assertIn("status", identity["excluded_mutable_fields"])
        self.assertEqual(identity["claim"]["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(identity["claim"]["branch"], reference.BRANCH)
        self.assertEqual(identity["claim"]["worktree"], reference.CLAIM_WORKTREE)
        self.assertEqual(identity["claim"]["reviewer"], reference.REVIEWER)

    def test_board_status_and_owner_edits_do_not_change_report(self):
        original = reference.strict_load

        def mutated(path):
            data = original(path)
            if Path(path).name == "TASKS.json":
                data = copy.deepcopy(data)
                for task in data["tasks"]:
                    task["status"] = "blocked"
                    task["owner"] = "another-agent"
                    task["dispatch_priority"] = 99
            return data

        with mock.patch.object(reference, "strict_load", mutated):
            rebuilt = reference.build_report()
        self.assertEqual(
            reference.canonical_report_bytes(rebuilt),
            reference.canonical_report_bytes(self.report),
        )

    def test_mutable_board_is_never_pinned(self):
        self.assertNotIn(reference.BOARD_PATH, self.report["source_pins"])
        self.assertNotIn(reference.BOARD_PATH, self.report["boundary_pins"])
        self.assertIs(self.report["mutable_provenance"]["gate"], False)

    def test_source_and_boundary_pins_are_exact(self):
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.report["boundary_pins"], reference.BOUNDARY_PINS)
        reference.verify_document_pins()
        for relative in reference.SOURCE_PINS:
            self.assertTrue((reference.SOURCE_ROOT / relative).is_file())
        for relative in reference.BOUNDARY_PINS:
            self.assertTrue((reference.SDK_ROOT / relative).is_file())

    def test_absence_probes_are_all_absent(self):
        probes = self.report["controls"]["absence_probes"]
        self.assertTrue(probes)
        self.assertTrue(all(row["exists"] is False for row in probes))
        self.assertIs(
            self.report["asset_audit"]["all_absence_probes_absent"], True
        )
        self.assertIs(
            self.report["upstream_identity"]["implementation_present"], False
        )
        self.assertIs(
            self.report["upstream_identity"]["source_checkout_present"], False
        )

    def test_adverse_controls_are_all_rejected(self):
        adverse = self.report["controls"]["adverse"]
        self.assertGreaterEqual(len(adverse), 30)
        self.assertTrue(all(row["result"] == "rejected" for row in adverse))
        cases = {row["case"] for row in adverse}
        for required in (
            "feature_nan",
            "feature_pos_inf",
            "feature_neg_inf",
            "feature_bool",
            "feature_string",
            "singular_covariance",
            "negative_penalty",
            "nonfinite_threshold",
            "manifest_missing_field",
            "manifest_extra_field",
            "manifest_relative_path",
            "manifest_bad_sha",
            "manifest_short_revision",
            "manifest_wrong_variant",
            "json_duplicate_key",
            "json_nan",
            "json_infinity",
        ):
            self.assertIn(required, cases)

    def test_merged_sibling_evidence_is_not_attributed(self):
        sibling = self.report["merged_sibling_evidence"]
        self.assertIs(sibling["not_pooled"], True)
        self.assertIs(sibling["speaker_change_execution_present"], False)
        self.assertIs(sibling["bic_execution_present"], False)
        self.assertIs(sibling["diarization_execution_present"], False)
        self.assertTrue(sibling["packages"])
        for row in sibling["packages"]:
            self.assertIs(row["attributed_to_this_task"], False)
            self.assertTrue(
                (reference.SDK_ROOT / row["path"]).is_file(), row["path"]
            )

    def test_upstream_identity_has_no_invented_pin(self):
        upstream = self.report["upstream_identity"]
        self.assertIsNone(upstream["repository_url"])
        self.assertIsNone(upstream["revision"])
        self.assertIsNone(upstream["release_or_tag"])
        self.assertIsNone(upstream["recorded_license"])
        self.assertIs(upstream["revision_pin_available"], False)
        self.assertIs(upstream["license_verified"], False)

    def test_task_geometry_is_unestablished(self):
        geometry = self.report["task_geometry"]
        self.assertEqual(geometry["status"], "unestablished")
        for key in (
            "upstream_feature_front_end",
            "upstream_window_frames",
            "upstream_hop_frames",
            "upstream_lookahead_frames",
            "upstream_penalty_weight",
            "upstream_threshold",
            "upstream_min_segment_frames",
            "upstream_merge_policy",
            "annotation_schema",
            "availability_policy",
        ):
            self.assertIsNone(geometry[key], key)
        self.assertIs(geometry["control_geometry"]["causal"], False)

    def test_canonical_report_is_stable_across_builds(self):
        self.assertEqual(
            reference.canonical_report_bytes(reference.build_report()),
            self.raw,
        )

    def test_report_file_and_sidecar_match(self):
        self.assertEqual((HERE / "report.json").read_bytes(), self.raw)
        digest = reference.sha256(self.raw)
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            digest + "  report.json\n",
        )

    def test_sources_manifest_is_sorted_and_complete(self):
        raw = (HERE / "SOURCES.sha256").read_bytes()
        self.assertEqual(raw, run.sources_bytes())
        labels = [line.split("  ", 1)[1]
                  for line in raw.decode("ascii").splitlines()]
        self.assertEqual(labels, sorted(labels))
        self.assertEqual(len(labels), len(set(labels)))
        self.assertNotIn("local:SOURCES.sha256", labels)
        self.assertIn("local:contract.json", labels)
        self.assertIn("local:reference.py", labels)
        self.assertIn("source:research/category_registry.json", labels)
        self.assertIn("worktree:api/include/audio_sdk/provider_v0.h", labels)
        self.assertNotIn("source:" + reference.BOARD_PATH, labels)
        self.assertNotIn("worktree:" + reference.BOARD_PATH, labels)

    def test_three_fresh_processes_are_byte_identical(self):
        script = (
            "import sys; sys.path.insert(0, %r); import reference; "
            "sys.stdout.buffer.write(reference.canonical_report_bytes("
            "reference.build_report()))" % str(HERE)
        )
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        outputs = []
        for _ in range(3):
            process = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                env=env,
                check=True,
            )
            outputs.append(process.stdout)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[1], outputs[2])
        self.assertEqual(outputs[0], self.raw)


class CallerManifestTests(unittest.TestCase):
    def setUp(self):
        self.base = reference._base_manifest()

    def test_valid_shape_is_accepted_but_never_qualified(self):
        validated = reference.validate_caller_asset_manifest(self.base)
        self.assertIs(validated["accepted"], True)
        self.assertEqual(validated["qualification"], "not_qualified")
        gate = reference.qualification_gate(self.base)
        self.assertIs(gate["qualifies"], False)
        self.assertEqual(gate["qualification"], "not_qualified")

    def test_missing_manifest_never_qualifies(self):
        gate = reference.qualification_gate(None)
        self.assertIs(gate["qualifies"], False)
        self.assertEqual(gate["qualification"], "not_qualified")

    def test_malformed_manifests_rejected(self):
        mutations = {
            "not_object": [],
            "missing": {key: value for key, value in self.base.items()
                        if key != "runtime_path"},
            "extra": dict(self.base, extra="value"),
            "relative_path": dict(self.base, runtime_path="relative"),
            "bad_sha": dict(self.base, build_record_sha256="x" * 64),
            "short_revision": dict(self.base, source_revision="a" * 12),
            "wrong_variant": dict(self.base, variant="diarization"),
            "capability_false": dict(
                self.base, claimed_bic_segmentation_capability=False
            ),
            "channels": dict(self.base, channels=2),
            "sample_rate": dict(self.base, sample_rate_hz=8000),
            "frame_samples": dict(self.base, frame_samples=320),
            "window_float": dict(self.base, window_frames=15.5),
            "min_segment_zero": dict(self.base, min_segment_frames=0),
            "penalty_exponent": dict(self.base, penalty_weight="1e0"),
            "penalty_zero": dict(self.base, penalty_weight="0"),
            "threshold_exponent": dict(self.base, threshold="0e0"),
            "bool_integer": dict(self.base, hop_frames=True),
        }
        for name, manifest in mutations.items():
            with self.subTest(name=name):
                with self.assertRaises(reference.Reject):
                    reference.validate_caller_asset_manifest(manifest)

    def test_qualification_gate_rejects_bad_manifest(self):
        gate = reference.qualification_gate(dict(self.base, channels=2))
        self.assertIs(gate["qualifies"], False)
        self.assertIn("rejected", gate["reason"])


class AtomicRejectionTests(unittest.TestCase):
    def setUp(self):
        self.builder = reference.EvidenceReport()
        self.builder.build()
        self.snapshot = self.builder.snapshot()

    def _unchanged(self):
        self.assertEqual(self.builder.snapshot(), self.snapshot)

    def test_invalid_payload_type_rejected_atomically(self):
        with self.assertRaises(reference.Reject):
            self.builder.build(payload={"bad": object()})
        self._unchanged()

    def test_nonfinite_payload_rejected_atomically(self):
        with self.assertRaises(reference.Reject):
            self.builder.build(payload={"bad": float("nan")})
        self._unchanged()

    def test_oversized_payload_integer_rejected_atomically(self):
        with self.assertRaises(reference.Reject):
            self.builder.build(payload={"bad": 2 ** 54})
        self._unchanged()

    def test_tampered_pin_rejected(self):
        bad = dict(reference.SOURCE_PINS)
        first = sorted(bad)[0]
        bad[first] = "0" * 64
        with mock.patch.object(reference, "SOURCE_PINS", bad):
            with self.assertRaises(reference.Reject):
                reference.verify_document_pins()

    def test_missing_pinned_file_rejected(self):
        bad = dict(reference.SOURCE_PINS)
        bad["research/does-not-exist.md"] = "0" * 64
        with mock.patch.object(reference, "SOURCE_PINS", bad):
            with self.assertRaises(reference.Reject):
                reference.verify_document_pins()

    def test_unexpected_artifact_presence_rejected(self):
        with mock.patch.object(
            reference, "ABSENCE_PROBES",
            reference.ABSENCE_PROBES + ("docs",),
        ):
            with self.assertRaises(reference.Reject):
                reference.build_report()

    def test_open_release_gate_rejected(self):
        original = reference._gate_rows

        def opened():
            rows = original()
            rows[0]["blocked"] = False
            return rows

        with mock.patch.object(reference, "_gate_rows", opened):
            with self.assertRaises(reference.Reject):
                reference.build_report()

    def test_synthetic_audio_claim_rejected(self):
        original = reference.synthetic_control

        def claimed():
            data = original()
            data["not_audio"] = False
            return data

        with mock.patch.object(reference, "synthetic_control", claimed):
            with self.assertRaises(reference.Reject):
                reference.build_report()

    def test_non_null_candidate_metric_rejected(self):
        original = reference._candidate_metrics

        def promoted():
            data = original()
            data["boundary_precision"]["value"] = 1.0
            data["boundary_precision"]["measured"] = True
            return data

        with mock.patch.object(reference, "_candidate_metrics", promoted):
            with self.assertRaises(reference.Reject):
                reference.build_report()

    def test_qualification_claim_rejected(self):
        data = copy.deepcopy(self.snapshot)
        data["qualification"]["candidate_qualified"] = True
        with self.assertRaises(reference.Reject):
            reference._finalize_report(data)
        self.assertIs(
            reference.qualification_gate(reference._base_manifest())[
                "qualifies"
            ],
            False,
        )


if __name__ == "__main__":
    unittest.main()
