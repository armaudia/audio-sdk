# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit checks for the FastConformer streaming-ASR package.

No network, no skips, no checkpoint, no runtime, no audio and no recognition
result. These tests exercise only the stdlib scheduler surrogate, the
fail-closed admission boundary, canonical serialization and package metadata.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

LICENSE_TOKEN = "SPDX-License-" "Identifier: Apache-2.0"
COPYRIGHT_TOKEN = "SPDX-FileCopyrightText:"


class PackageMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_task_constants(self) -> None:
        self.assertEqual(reference.TASK, "SDK-FASTCONFORMER-STREAMING-ASR")
        self.assertEqual(reference.COMPONENT_ID, "fastconformer-streaming-asr")
        self.assertEqual(reference.PROFILE, "rate")
        self.assertEqual(reference.MODE, "feasibility")
        self.assertEqual(reference.DECISION, "DEFER")
        self.assertEqual(reference.STATUS, "proposal_only_synthetic_incomplete")
        self.assertEqual(reference.QUALIFICATION_STATUS, "not_qualified")
        self.assertEqual(reference.FRAME_SAMPLES, 160)
        self.assertEqual(reference.CHUNK_SAMPLES, 1280)

    def test_source_pins_verify(self) -> None:
        for relative, expected in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), expected, relative)

    def test_boundary_pins_verify(self) -> None:
        for relative, expected in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), expected, relative)

    def test_board_projection_uses_stable_fields_only(self) -> None:
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(tuple(row), reference.BOARD_ROW_FIELDS)
        self.assertEqual(row["id"], reference.TASK)
        self.assertEqual(row["component"], reference.COMPONENT_ID)
        self.assertEqual(row["repository"], "audio-sdk")
        self.assertEqual(row["mode"], "feasibility")
        self.assertNotIn("status", row)
        self.assertNotIn("claim", row)
        self.assertNotIn("owner", row)

    def test_linked_rows_are_stable_identity_only(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))
        for row in rows:
            self.assertEqual(tuple(row), reference.BOARD_ROW_FIELDS)
        self.assertEqual(reference.linked_rows_digest(rows),
                         reference.object_digest(rows))

    def test_contract_is_defer_incomplete_and_proposal_only(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], reference.STATUS)
        self.assertEqual(self.contract["evidence_status"], "incomplete")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertIs(self.contract["proposal_only"], True)

    def test_contract_has_eight_blocked_linked_gates(self) -> None:
        gates = self.contract["release_gates"]
        self.assertEqual(len(gates), 8)
        projection = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        for index, gate in enumerate(gates, start=1):
            self.assertEqual(gate["id"], f"RG-{index:02d}")
            self.assertEqual(gate["status"], "blocked")
            self.assertIs(gate["qualifies"], False)
            self.assertEqual(gate["linked_row"], projection)
            self.assertTrue(gate["reopen_condition"])

    def test_contract_artifacts_are_fail_closed(self) -> None:
        artifacts = self.contract["required_artifacts"]
        self.assertEqual(len(artifacts), len(reference.REQUIRED_ARTIFACTS))
        first = artifacts[0]
        self.assertIs(first["present"], True)
        self.assertIs(first["verified"], True)
        self.assertIs(first["blocked"], False)
        for artifact in artifacts[1:]:
            self.assertIs(artifact["present"], False)
            self.assertIs(artifact["verified"], False)
            self.assertIs(artifact["blocked"], True)
            self.assertIsNone(artifact["sha256"])

    def test_contract_blockers_are_open(self) -> None:
        blockers = self.contract["exact_blockers"]
        self.assertEqual(len(blockers), len(reference.EXACT_BLOCKERS))
        artifact_ids = {row["id"] for row in self.contract["required_artifacts"]}
        gate_ids = {row["id"] for row in self.contract["release_gates"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertIs(blocker["qualifies"], False)
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(set(blocker["linked_gates"]) <= gate_ids)

    def test_rate_rows_are_blocked(self) -> None:
        rows = self.contract["rate_profile_requirements"]
        self.assertEqual(len(rows), len(reference.RATE_PROFILE_ROWS))
        for row in rows:
            self.assertEqual(row["status"], "blocked")
        required = {"RATE-01", "RATE-02", "RATE-03", "RATE-04", "RATE-05",
                    "RATE-06", "RATE-07", "RATE-08"}
        self.assertEqual({row["id"] for row in rows}, required)

    def test_asr_and_timing_rows_have_no_values(self) -> None:
        for name in ("asr_outcome_requirements", "timing_requirements"):
            rows = self.contract[name]
            self.assertTrue(rows)
            for row in rows:
                self.assertEqual(row["status"], "blocked")
                self.assertIsNone(row["value"])

    def test_qualification_claims_nothing(self) -> None:
        row = self.contract["qualification"]
        self.assertIs(row["not_qualified"], True)
        self.assertIs(row["all_release_gates_blocked"], True)
        self.assertIs(row["incomplete"], True)
        self.assertIs(row["proposal_only"], True)
        self.assertIs(row["qualifies"], False)
        for key in ("exact_candidate_identity_present", "checkpoint_bytes_present",
                    "weights_present", "runtime_present", "asr_result",
                    "wer_result", "transcript_result",
                    "streaming_latency_result", "device_timing_result",
                    "rate_profile_result", "listening_result",
                    "benchmark_result", "release_claim",
                    "missing_result_promoted"):
            self.assertIs(row[key], False, key)

    def test_claims_are_all_false(self) -> None:
        for key, value in self.contract["claims"].items():
            self.assertIs(value, False, key)
        for key, value in self.contract["boundary"].items():
            if key in {"descriptor_settings"}:
                self.assertEqual(value, {})
            elif key == "installed_v0_geometry_preserved":
                self.assertIs(value, True)
            else:
                self.assertIs(value, False, key)

    def test_report_copies_contract_rows(self) -> None:
        for field in ("disposition", "qualification", "required_artifacts",
                      "exact_blockers", "scope", "boundary",
                      "public_v0_geometry", "non_claims", "required_results",
                      "candidate_record", "documented_context",
                      "linked_row_identity"):
            self.assertEqual(self.report[field], self.contract[field], field)
        self.assertEqual(self.report["gates"], self.contract["release_gates"])
        self.assertEqual(self.report["rate_profile"]["rows"],
                         self.contract["rate_profile_requirements"])
        self.assertEqual(self.report["asr_outcomes"]["rows"],
                         self.contract["asr_outcome_requirements"])
        self.assertEqual(self.report["timing"]["rows"],
                         self.contract["timing_requirements"])

    def test_report_is_canonical_and_float_free(self) -> None:
        text, digest = reference.canonical_report(self.report)
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(hashlib.sha256(text.encode("ascii")).hexdigest(),
                         digest)
        parsed = json.loads(text)
        self.assertEqual(parsed, self.report)
        reference._no_floats(self.report)
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_report_linked_identity_is_not_a_board_pin(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertIs(identity["board_file_pinned"], False)
        self.assertIs(identity["board_status_gates_anything"], False)
        self.assertEqual(identity["projection"],
                         reference.board_row_projection(
                             reference.AUDIO_ROOT /
                             reference.BOARD_TASK_ROW))

    def test_absence_probes_are_all_absent(self) -> None:
        summary = self.report["absence_evidence"]["summary"]
        self.assertEqual(summary["present_count"], 0)
        self.assertIs(summary["all_probes_absent"], True)
        for key in ("download_attempted", "network_used",
                    "recursive_workspace_walk", "source_or_runtime_imported",
                    "weights_loaded", "model_executed", "audio_read"):
            self.assertIs(summary[key], False, key)

    def test_no_nemo_runtime_is_imported(self) -> None:
        runtime = self.report["runtime_presence"]
        self.assertIs(runtime["import_attempted"], False)
        self.assertIs(runtime["nemo_present"], False)
        self.assertIs(runtime["runtime_present"], False)
        self.assertIs(runtime["exact_runtime_artifact_present"], False)
        self.assertIs(runtime["cuda_runtime_present"], False)
        for row in runtime["modules"]:
            if row["module"] in {"nemo", "nemo_toolkit"}:
                self.assertIs(row["available"], False)

    def test_source_presence_is_not_qualification(self) -> None:
        presence = self.report["source_presence"]
        self.assertIs(presence["research_report_and_matrix_present"], True)
        self.assertIs(presence["exact_source_weights_runtime_conjunction_present"],
                      False)
        self.assertIs(presence["weights_used"], False)
        self.assertIs(presence["runtime_imported"], False)
        self.assertIs(presence["model_executed"], False)

    def test_sources_manifest_excludes_mutable_board(self) -> None:
        payload = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        self.assertTrue(payload.startswith(
            "# SHA-256 pins for SDK-FASTCONFORMER-STREAMING-ASR readiness evidence."))
        self.assertNotIn("plan/swarm/TASKS.json", payload)
        for name in ("reference.py", "report.json", "contract.json",
                     "test_reference.py", "verify.py", "run.py"):
            self.assertIn(reference.TASK_PREFIX + name, payload)

    def test_readme_and_license_have_spdx(self) -> None:
        for name in ("README.md", "LICENSES.md"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(LICENSE_TOKEN, text, name)
            self.assertIn(COPYRIGHT_TOKEN, text, name)

    def test_no_forbidden_payload_in_package(self) -> None:
        forbidden = {".wav", ".flac", ".pt", ".pth", ".bin", ".onnx", ".so",
                     ".dylib", ".nemo", ".ckpt", ".zip", ".pyc"}
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertNotIn(path.name, {"provider.json", "adapter.json"},
                             path.name)


class SchedulerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.control = reference.scheduler_control()

    def test_chunk_and_partial_accounting(self) -> None:
        rows = {row["id"]: row for row in self.control["conditions"]}
        for condition in ("SIL-32000", "RAMP-32000", "IMP-32000"):
            row = rows[condition]
            self.assertEqual(row["completed_chunk_count"], 25, condition)
            self.assertEqual(row["final_partial_chunk_count"], 0, condition)
            self.assertEqual(row["internal_padding_samples"], 0, condition)
            self.assertEqual(row["valid_source_samples"], 32000, condition)
            self.assertEqual(row["scheduled_chunk_samples"], 32000, condition)
        partial = rows["PARTIAL-32037"]
        self.assertEqual(partial["completed_chunk_count"], 25)
        self.assertEqual(partial["final_partial_chunk_count"], 1)
        self.assertEqual(partial["final_partial_real_samples"], 37)
        self.assertEqual(partial["internal_padding_samples"], 1243)
        self.assertEqual(partial["valid_source_samples"], 32037)
        self.assertEqual(partial["scheduled_chunk_samples"], 33280)

    def test_chunk_size_does_not_change_event_boundaries(self) -> None:
        row = self.control["chunk_independence"]
        self.assertEqual(row["chunk_sizes"],
                         [1, 7, 80, 159, 160, 161, 320, 1280, 32000])
        self.assertIs(row["all_equal"], True)
        self.assertEqual(len(set(row["digests"])), 1)
        self.assertEqual(row["caller_chunks_total"], 37699)

    def test_lifecycle_reset_flush_and_close(self) -> None:
        row = self.control["lifecycle"]
        self.assertIs(row["reset_restores_initial_fingerprint"], True)
        self.assertIs(row["pre_reset_fingerprint_differs"], True)
        self.assertIs(row["replay_event_digest_matches"], True)
        self.assertIs(row["second_flush_is_empty"], True)
        self.assertIs(row["close_is_idempotent"], True)
        self.assertEqual(row["fresh_cache_epoch"], 0)
        self.assertEqual(row["reset_cache_epoch"], 1)

    def test_adverse_inputs_are_rejected_without_state_change(self) -> None:
        for row in self.control["adverse"]:
            self.assertIs(row["rejected"], True, row["id"])
            self.assertIs(row["state_unchanged"], True, row["id"])
            self.assertEqual(row["observed_code"], row["expected_code"])
            self.assertIs(row["qualifies"], False)

    def test_invalid_push_leaves_state_unchanged(self) -> None:
        scheduler = reference.StreamingScheduler()
        scheduler.push([0.0] * 100)
        before = scheduler.state_digest()
        for value in (None, "abc", [True], [float("nan")], [float("inf")],
                      [1.5], {"x": 1}):
            with self.assertRaises(reference.SchedulerError):
                scheduler.push(value)
            self.assertEqual(scheduler.state_digest(), before)
        scheduler.push([0.0] * 10)
        self.assertNotEqual(scheduler.state_digest(), before)

    def test_closed_and_flushed_rejections(self) -> None:
        scheduler = reference.StreamingScheduler()
        scheduler.push([0.0] * 10)
        scheduler.flush()
        with self.assertRaises(reference.SchedulerError) as caught:
            scheduler.push([0.0])
        self.assertEqual(caught.exception.code, "scheduler_flushed")
        scheduler.close()
        scheduler.close()
        for call in (lambda: scheduler.push([0.0]),
                     scheduler.flush,
                     scheduler.reset):
            with self.assertRaises(reference.SchedulerError) as caught:
                call()
            self.assertEqual(caught.exception.code, "scheduler_closed")

    def test_reset_replay_is_structurally_identical(self) -> None:
        signal = reference.synthetic_signal("ramp", 4097)
        first = reference.StreamingScheduler()
        first_events = first.push(signal)
        first_events += first.flush()
        first.reset()
        second_events = first.push(signal)
        second_events += first.flush()
        self.assertEqual(reference.structural_event_digest(first_events),
                         reference.structural_event_digest(second_events))

    def test_invalid_geometry_is_rejected(self) -> None:
        for chunk, frame in ((1281, 160), (1280, 159), (0, 160), (True, 160)):
            with self.assertRaises(reference.SchedulerError):
                reference.StreamingScheduler(chunk_samples=chunk,
                                             frame_samples=frame)

    def test_synthetic_signal_bounds(self) -> None:
        for kind in ("zeros", "ramp", "impulse"):
            values = reference.synthetic_signal(kind, 5000)
            self.assertEqual(len(values), 5000)
            self.assertTrue(all(-1.0 <= value <= 1.0 for value in values))
        with self.assertRaises(reference.SchedulerError):
            reference.synthetic_signal("speech", 10)


class AdmissionTests(unittest.TestCase):
    def test_schema_control_is_accepted_but_never_qualifies(self) -> None:
        control = reference.admission_control()
        self.assertIs(control["accepted"], True)
        self.assertIs(control["qualifies"], False)
        self.assertIs(control["schema_only"], True)
        self.assertIs(control["candidate_is_real"], False)
        self.assertIs(control["weights_loaded"], False)

    def test_all_admission_cases_reject(self) -> None:
        cases = reference.admission_cases()
        self.assertEqual(len(cases), len(reference.ADMISSION_CASES))
        for case in cases:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertEqual(case["observed_code"], case["expected_code"],
                             case["id"])
            self.assertIs(case["qualifies"], False)
            self.assertIs(case["state_unchanged"], True)

    def test_control_manifest_survives_a_copy(self) -> None:
        manifest = reference.control_manifest()
        clone = copy.deepcopy(manifest)
        reference.validate_manifest(clone)
        clone["candidate"]["checkpoint_files"][0]["sha256"] = "x"
        with self.assertRaises(reference.AdmissionError) as caught:
            reference.validate_manifest(clone)
        self.assertEqual(caught.exception.code, "checkpoint_sha256")

    def test_mutable_revision_and_missing_rights_reject(self) -> None:
        for path, value, code in (
                (("candidate", "source_revision"), "main",
                 "source_revision_mutable"),
                (("candidate", "license", "terms_reviewed"), False,
                 "license_terms"),
                (("assets", "download_permitted"), True, "asset_download"),
                (("provider", "registered"), True, "provider_registered")):
            manifest = copy.deepcopy(reference.control_manifest())
            target = manifest
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.assertRaises(reference.AdmissionError) as caught:
                reference.validate_manifest(manifest)
            self.assertEqual(caught.exception.code, code)

    def test_nonfinite_and_boolean_numbers_reject(self) -> None:
        for value, code in ((float("nan"), "streaming_chunk_ms"),
                            (float("inf"), "streaming_chunk_ms"),
                            (True, "streaming_chunk_ms"),
                            (-1, "streaming_lookahead_ms")):
            manifest = copy.deepcopy(reference.control_manifest())
            if code == "streaming_lookahead_ms":
                manifest["streaming"]["lookahead_ms"] = value
            else:
                manifest["streaming"]["chunk_ms"] = value
            with self.assertRaises(reference.AdmissionError) as caught:
                reference.validate_manifest(manifest)
            self.assertEqual(caught.exception.code, code)

    def test_admission_summary_counts(self) -> None:
        admission = reference.build_admission()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], len(reference.ADMISSION_CASES))
        self.assertEqual(summary["rejected_count"],
                         len(reference.ADMISSION_CASES))
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertIs(summary["runtime_invoked"], False)


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_keys_reject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_nonfinite_constants_reject(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "nonfinite.json"
                path.write_text('{"a":' + token + '}', encoding="utf-8")
                with self.assertRaises(ValueError):
                    reference.read_strict_json(path)

    def test_canonical_json_is_sorted_and_compact(self) -> None:
        self.assertEqual(reference.canonical_text({"b": 1, "a": [2, 3]}),
                         '{"a":[2,3],"b":1}')
        with self.assertRaises(ValueError):
            reference.canonical_text({"a": float("nan")})


if __name__ == "__main__":
    unittest.main(verbosity=2)
