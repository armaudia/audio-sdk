# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for the SDK-RVC-MLX-REALTIME readiness evidence package.

Standard library only. These tests exercise strict JSON, source identity, the
deterministic block/SOLA/queue arithmetic reference, fail-closed admission and
the canonical contract/report. They never import MLX, read audio, load weights
or execute a model.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path

import reference


class StrictJsonTests(unittest.TestCase):
    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_rejects_nonfinite_constants(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                reference.loads_strict(f'{{"a":{token}}}')

    def test_rejects_byte_order_mark(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('\ufeff{"a":1}')

    def test_rejects_non_object_root(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict("[1,2]")

    def test_canonical_bytes_are_stable(self) -> None:
        document = {"b": [3, 1, 2], "a": {"z": None, "y": True}}
        self.assertEqual(reference.canonical_text(document),
                         '{"a":{"y":true,"z":null},"b":[3,1,2]}\n')
        self.assertEqual(reference.object_digest(document),
                         hashlib.sha256(reference.canonical_bytes(
                             document)).hexdigest())

    def test_no_floats(self) -> None:
        with self.assertRaises(ValueError):
            reference._no_floats({"a": [1.5]})
        reference._no_floats({"a": ["0.5"]})


class IdentityTests(unittest.TestCase):
    def test_board_projection_matches_task(self) -> None:
        board = (reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        projection = reference.board_row_projection(board)
        self.assertEqual(projection, reference.BOARD_ROW_PROJECTION)
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["component"], reference.COMPONENT_ID)
        self.assertEqual(projection["mode"], "implementation")

    def test_board_row_digest_is_projection_only(self) -> None:
        digest = reference.board_row_digest(reference.BOARD_ROW_PROJECTION)
        self.assertEqual(len(digest), 64)
        mutated = dict(reference.BOARD_ROW_PROJECTION, status="review")
        self.assertEqual(reference.board_row_digest(
            {k: mutated[k] for k in reference.BOARD_ROW_FIELDS}), digest)

    def test_linked_rows_digest_is_stable(self) -> None:
        first = reference.linked_rows_digest()
        second = reference.linked_rows_digest()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_source_tree_matches_pin(self) -> None:
        fingerprint = reference.verify_source_tree(
            reference.AUDIO_ROOT / reference.SOURCE_ROOT)
        self.assertEqual(fingerprint["file_count"],
                         reference.SOURCE_TREE_FILE_COUNT)
        self.assertEqual(fingerprint["byte_count"],
                         reference.SOURCE_TREE_BYTE_COUNT)
        self.assertEqual(fingerprint["sha256"],
                         reference.SOURCE_TREE_SHA256)

    def test_source_has_no_license_file(self) -> None:
        root = reference.AUDIO_ROOT / reference.SOURCE_ROOT
        for name in ("LICENSE", "LICENSE.txt", "COPYING", "NOTICE"):
            self.assertFalse((root / name).exists(), name)
        self.assertFalse(reference.SOURCE_PRESENCE["license_present"])

    def test_observed_test_audio_is_hash_only(self) -> None:
        audio = reference.AUDIO_ROOT / reference.OBSERVED_TEST_AUDIO["path"]
        self.assertTrue(audio.is_file())
        self.assertEqual(reference.sha256_file(audio),
                         reference.OBSERVED_TEST_AUDIO["sha256"])
        self.assertFalse(reference.OBSERVED_TEST_AUDIO["decoded"])
        self.assertFalse(reference.OBSERVED_TEST_AUDIO["used_for_evidence"])

    def test_pins_verify(self) -> None:
        source = reference.pin_rows(reference.SOURCE_PINS,
                                    reference.AUDIO_ROOT)
        boundary = reference.pin_rows(reference.BOUNDARY_PINS,
                                      reference.WORKTREE)
        self.assertEqual(len(source), len(reference.SOURCE_PINS))
        self.assertEqual(len(boundary), len(reference.BOUNDARY_PINS))
        for row in list(source.values()) + list(boundary.values()):
            self.assertTrue(row["verified"])
            self.assertEqual(row["sha256"], row["actual"])


class AbsenceTests(unittest.TestCase):
    def test_fixed_probe_lists_are_absent(self) -> None:
        workspace = reference.absence_probes(reference.AUDIO_ROOT)
        home = reference.home_absence_probes()
        self.assertTrue(all(not row["present"] for row in workspace))
        self.assertTrue(all(not row["present"] for row in home))
        self.assertEqual(len(workspace), len(reference.ABSENCE_PROBES))
        self.assertEqual(len(home), len(reference.HOME_ABSENCE_PROBES))

    def test_present_artifact_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "present.bin").write_bytes(b"x")
            with self.assertRaises(ValueError) as caught:
                reference.absence_probes(root, ("present.bin",), worktree=root)
            self.assertIn("artifact_present_reopen_required",
                          str(caught.exception))
            rows = reference.absence_probes(root, ("absent.bin",),
                                            worktree=root)
            self.assertEqual(rows, [{"path": "absent.bin",
                                     "searched_workspace": True,
                                     "searched_sdk_worktree": True,
                                     "present": False}])

    def test_runtime_probe_is_absent(self) -> None:
        probe = reference.runtime_module_probe()
        self.assertFalse(probe["importable"])
        self.assertFalse(probe["import_attempted"])


class GeometryTests(unittest.TestCase):
    def test_geometry_constants(self) -> None:
        geometry = reference.realtime_geometry()
        self.assertEqual(geometry["block_samples"], 3200)
        self.assertEqual(geometry["crossfade_samples"], 960)
        self.assertEqual(geometry["extra_samples"], 4800)
        self.assertEqual(geometry["sola_search_samples"], 192)
        self.assertEqual(geometry["convert_samples"], 9152)
        self.assertEqual(geometry["target_block_samples"], 8000)
        self.assertEqual(geometry["target_crossfade_samples"], 2400)
        self.assertEqual(geometry["target_search_samples"], 480)
        self.assertEqual(geometry["sola_need_samples"], 10880)
        self.assertEqual(geometry["sola_candidate_count"], 481)
        self.assertEqual(geometry["declared_buffering_samples"], 4160)
        self.assertEqual(geometry["declared_buffering_seconds"], "13/50")
        self.assertEqual(geometry["ring_capacity_samples"], 32000)
        self.assertEqual(geometry["bounded_backlog_ms"], 1200)

    def test_geometry_checks_pass(self) -> None:
        result = reference.geometry_reference()
        self.assertTrue(result["all_checks_pass"])
        self.assertFalse(result["measured"])
        self.assertFalse(result["qualifies"])

    def test_non_integral_milliseconds_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference._exact_ms_samples(1, 44100)
        with self.assertRaises(ValueError):
            reference._exact_ms_samples(-1, 16000)
        with self.assertRaises(ValueError):
            reference._exact_ms_samples(True, 16000)

    def test_resampling_ratios(self) -> None:
        result = reference.resample_reference()
        self.assertTrue(result["all_checks_pass"])
        rows = {row["device_sample_rate_hz"]: row for row in result["rows"]}
        self.assertEqual(rows[44100]["input_resample_num"], 441)
        self.assertEqual(rows[44100]["input_resample_den"], 160)
        self.assertEqual(rows[44100]["device_block_samples"], 8820)
        self.assertEqual(rows[48000]["input_resample_num"], 3)
        self.assertEqual(rows[48000]["output_resample_num"], 6)
        self.assertEqual(rows[192000]["device_output_block_samples"], 38400)
        self.assertFalse(result["resampler_invoked"])

    def test_sola_recovers_known_lag(self) -> None:
        result = reference.sola_reference()
        self.assertTrue(result["all_checks_pass"])
        self.assertFalse(result["float_path_used"])
        for case in result["cases"]:
            self.assertEqual(case["recovered_lag"], case["injected_lag"])
            self.assertTrue(case["unique_match"])
            self.assertEqual(case["candidate_count"], 25)

    def test_exact_lag_search_rejects_bad_geometry(self) -> None:
        with self.assertRaises(ValueError):
            reference.exact_lag_search([1, 2], [1, 2], -1)
        with self.assertRaises(ValueError):
            reference.exact_lag_search([1, 2], [1, 2], 2)
        with self.assertRaises(ValueError):
            reference.exact_lag_search([1, 2], [0, 0, 0], 1)

    def test_bounded_backlog(self) -> None:
        result = reference.bounded_backlog_reference()
        self.assertTrue(result["all_checks_pass"])
        self.assertEqual(result["retained_bound_blocks"], 6)
        self.assertEqual(result["retained_bound_ms"], 1200)
        for row in result["rows"]:
            self.assertLessEqual(row["retained_samples"], 48000)
            self.assertEqual(row["queued_or_ring_blocks"] +
                             row["emitted_blocks"], row["produced_blocks"])
        self.assertFalse(result["threads_started"])
        self.assertFalse(result["callback_invoked"])

    def test_source_declarations(self) -> None:
        result = reference.source_declaration_checks()
        self.assertTrue(result["all_checks_pass"])
        self.assertFalse(result["source_imported"])
        self.assertFalse(result["executed"])

    def test_arithmetic_is_not_evidence(self) -> None:
        result = reference.arithmetic_reference()
        self.assertTrue(result["all_checks_pass"])
        for key in ("audio_read", "model_executed", "runtime_invoked",
                    "device_timing_measured", "qualifies"):
            self.assertFalse(result[key])
        self.assertEqual(result["kind"],
                         "standard_library_deterministic_reference")


class AdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.control = reference._synthetic_bundle()

    def test_control_is_accepted_but_not_evidence(self) -> None:
        result = reference.validate_manifest(self.control, probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertFalse(self.control["rights"]["claims_qualified"])
        summary = reference.admission_controls()
        self.assertTrue(summary["control"]["accepted"])
        self.assertTrue(
            summary["control"]["synthetic_schema_control_not_evidence"])
        self.assertFalse(summary["control"]["qualifies"])

    def test_all_mutations_rejected(self) -> None:
        controls = reference.admission_controls()
        self.assertGreaterEqual(len(controls["cases"]), 60)
        for case in controls["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])

    def test_missing_and_extra_fields_rejected(self) -> None:
        missing = copy.deepcopy(self.control)
        del missing["runtime"]
        extra = copy.deepcopy(self.control)
        extra["surprise"] = 1
        for document in (missing, extra):
            self.assertFalse(
                reference.validate_manifest(document, probe_paths=False)
                ["accepted"])

    def test_nonfinite_everywhere_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            document = copy.deepcopy(self.control)
            document["outcomes"]["naturalness_mos"] = value
            result = reference.validate_manifest(document, probe_paths=False)
            self.assertFalse(result["accepted"])
        document = copy.deepcopy(self.control)
        document["runtime"]["offline"] = float("nan")
        self.assertFalse(
            reference.validate_manifest(document, probe_paths=False)["accepted"])

    def test_claims_qualified_rejected(self) -> None:
        document = copy.deepcopy(self.control)
        document["rights"]["claims_qualified"] = True
        result = reference.validate_manifest(document, probe_paths=False)
        self.assertEqual(result["code"], "rights_claims_qualified")

    def test_wrong_weights_rejected(self) -> None:
        for mutation in ("missing", "unknown", "duplicate", "digest"):
            document = copy.deepcopy(self.control)
            if mutation == "missing":
                document["weights"] = document["weights"][:2]
            elif mutation == "unknown":
                document["weights"].append(
                    {"name": "other", "sha256": "9" * 64, "byte_count": 1,
                     "terms_sha256": "3" * 64})
            elif mutation == "duplicate":
                document["weights"][1]["name"] = "synth_weights"
            else:
                document["weights"][1]["sha256"] = \
                    document["weights"][0]["sha256"]
            result = reference.validate_manifest(document, probe_paths=False)
            self.assertFalse(result["accepted"], mutation)

    def test_realtime_derived_values_enforced(self) -> None:
        document = copy.deepcopy(self.control)
        document["realtime"]["convert_samples"] = 9151
        self.assertFalse(
            reference.validate_manifest(document, probe_paths=False)["accepted"])
        document = copy.deepcopy(self.control)
        document["realtime"]["block_samples"] = 3201
        self.assertFalse(
            reference.validate_manifest(document, probe_paths=False)["accepted"])

    def test_reference_paths_probed_only_when_requested(self) -> None:
        self.assertTrue(reference.validate_manifest(
            self.control, probe_paths=False)["accepted"])
        result = reference.validate_manifest(self.control, probe_paths=True)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], "reference_missing")

    def test_manifest_root_and_schema(self) -> None:
        self.assertFalse(reference.validate_manifest([], probe_paths=False)
                         ["accepted"])
        document = copy.deepcopy(self.control)
        document["schema_id"] = "other"
        self.assertFalse(
            reference.validate_manifest(document, probe_paths=False)["accepted"])


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()

    def test_contract_validates(self) -> None:
        reference.validate_contract(self.contract)
        reference._no_floats(self.contract)

    def test_disposition(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.contract["proposal_only"])

    def test_eight_blocked_gates(self) -> None:
        gates = self.contract["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{i:02d}" for i in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             reference.BOARD_ROW_PROJECTION)

    def test_artifacts_and_blockers(self) -> None:
        artifacts = self.contract["required_artifacts"]
        self.assertEqual(len(artifacts), 7)
        self.assertTrue(artifacts[0]["present"])
        for artifact in artifacts[1:]:
            self.assertFalse(artifact["present"])
            self.assertTrue(artifact["blocked"])
        blockers = self.contract["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"],
                          {row["id"] for row in artifacts})

    def test_profile_rows(self) -> None:
        self.assertEqual(len(self.contract["voice_profile_requirements"]), 8)
        for row in self.contract["voice_profile_requirements"]:
            self.assertEqual(row["status"], "blocked")

    def test_board_not_pinned(self) -> None:
        self.assertFalse(self.contract["board_file_pinned"])
        self.assertNotIn(reference.BOARD_TASK_ROW,
                         reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW,
                         reference.BOUNDARY_PINS)

    def test_scope_and_boundary_are_negative(self) -> None:
        for section in ("scope", "boundary"):
            for key, value in self.contract[section].items():
                if key in ("task_local_only", "source_present"):
                    self.assertTrue(value)
                else:
                    self.assertFalse(value, key)

    def test_arithmetic_reference_present(self) -> None:
        self.assertTrue(self.contract["arithmetic_reference"]
                        ["all_checks_pass"])

    def test_no_weight_names_in_report_artifacts(self) -> None:
        for artifact in self.contract["required_artifacts"][1:]:
            self.assertIsNone(artifact["sha256"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_report_disposition(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.report["proposal_only"])
        self.assertEqual(self.report["qualification"]["readiness"],
                         "incomplete")

    def test_report_has_no_floats_and_is_canonical(self) -> None:
        reference._no_floats(self.report)
        text, digest = reference.canonical_report(self.report)
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(digest,
                         hashlib.sha256(text.encode("utf-8")).hexdigest())
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)

    def test_report_matches_contract(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(contract))
        self.assertEqual(self.report["gates"], contract["release_gates"])
        self.assertEqual(self.report["exact_blockers"],
                         contract["exact_blockers"])
        self.assertEqual(self.report["disposition"],
                         contract["disposition"])

    def test_absence_summary(self) -> None:
        summary = self.report["absence_evidence"]["summary"]
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        for key in ("download_attempted", "network_used", "weights_loaded",
                    "model_executed", "audio_read"):
            self.assertFalse(summary[key])

    def test_historical_is_not_evidence(self) -> None:
        historical = self.report["historical_execution"]
        self.assertTrue(historical["not_rerun"])
        for key in ("realtime_fork_ran", "used_for_evidence", "qualifies",
                    "device_timing_present", "listening_present"):
            self.assertFalse(historical[key])
        performance = self.report["repository_performance_recorded"]
        self.assertFalse(performance["used_for_evidence"])
        self.assertFalse(performance["reproduced_here"])

    def test_admission_has_no_qualifying_result(self) -> None:
        summary = self.report["admission"]["summary"]
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertEqual(summary["rejected_count"],
                         len(self.report["admission"]["cases"]))
        self.assertFalse(summary["runtime_invoked"])

    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_report(reference.build_report())
        second = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)


class SourcePresenceTests(unittest.TestCase):
    def test_conjunction_is_false(self) -> None:
        presence = reference.SOURCE_PRESENCE
        self.assertTrue(presence["present"])
        self.assertFalse(presence["admitted"])
        self.assertFalse(presence["license_present"])
        self.assertFalse(presence["exact_source_weights_runtime_conjunction_present"])
        self.assertIsNone(presence["license_id"])

    def test_historical_metrics_pin(self) -> None:
        path = (reference.AUDIO_ROOT /
                "research/voice-conversion-eval-20261101/results/rvc/"
                "metrics.json")
        metrics = reference.read_strict_json(path)
        self.assertEqual(metrics["sample_rate"], 40000)
        self.assertIn("no Metal device", metrics["limitations"][1])
        self.assertTrue(math.isfinite(metrics["file_rtf"]))
        self.assertGreater(metrics["file_rtf"], 0.0)
        self.assertLess(metrics["file_rtf"], 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
