# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library tests for SDK-CHATTERBOX-NANO."""

from __future__ import annotations

import copy
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

# REUSE-IgnoreStart
SPDX_LICENSE_LINE = "SPDX-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd


def control() -> dict:
    return copy.deepcopy(reference._manifest_control())


class StrictJsonTests(unittest.TestCase):
    def test_canonical_text_is_sorted_compact_and_newline_terminated(self) -> None:
        text = reference.canonical_text({"b": 2, "a": 1})
        self.assertEqual(text, '{"a":1,"b":2}\n')
        self.assertTrue(text.endswith("\n"))

    def test_canonical_bytes_round_trip(self) -> None:
        value = {"z": [1, 2], "a": "x"}
        self.assertEqual(reference.loads_strict(reference.canonical_text(value)),
                         value)

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a":1,"a":2}')
        self.assertEqual(str(caught.exception), "duplicate_json_key:a")

    def test_nan_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a":NaN}')
        self.assertEqual(str(caught.exception),
                         "nonfinite_json_constant:NaN")

    def test_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a":Infinity}')
        self.assertEqual(str(caught.exception),
                         "nonfinite_json_constant:Infinity")

    def test_negative_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a":-Infinity}')
        self.assertEqual(str(caught.exception),
                         "nonfinite_json_constant:-Infinity")

    def test_root_array_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict("[]")
        self.assertEqual(str(caught.exception), "json_root_not_object")

    def test_byte_order_mark_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict("\ufeff{}")
        self.assertEqual(str(caught.exception), "json_byte_order_mark")

    def test_object_digest_is_stable(self) -> None:
        first = reference.object_digest({"a": 1})
        second = reference.object_digest({"a": 1})
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)


class SourceAndBoardTests(unittest.TestCase):
    def test_board_row_projection_matches_stable_identity(self) -> None:
        board = reference.AUDIO_ROOT / reference.BOARD_TASK_ROW
        self.assertTrue(board.is_file(), "shared board task row is missing")
        self.assertEqual(reference.board_row_projection(board),
                         reference.BOARD_ROW_PROJECTION)

    def test_board_projection_contains_only_stable_fields(self) -> None:
        self.assertEqual(set(reference.BOARD_ROW_PROJECTION),
                         set(reference.BOARD_ROW_FIELDS))
        for mutable in ("status", "owner", "claim", "review", "handoff",
                        "blocked_reason", "dispatch_priority"):
            self.assertNotIn(mutable, reference.BOARD_ROW_PROJECTION)

    def test_board_projection_digest_is_deterministic(self) -> None:
        first = reference.board_row_digest(reference.BOARD_ROW_PROJECTION)
        second = reference.board_row_digest(reference.BOARD_ROW_PROJECTION)
        self.assertEqual(first, second)

    def test_board_file_is_not_pinned(self) -> None:
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)

    def test_linked_rows_are_stable_identity_only(self) -> None:
        self.assertEqual(len(reference.LINKED_ROWS), 8)
        for row in reference.LINKED_ROWS:
            self.assertEqual(set(row), set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(reference.LINKED_ROWS[0],
                         reference.BOARD_ROW_PROJECTION)
        self.assertEqual(reference.linked_rows_digest(),
                         reference.object_digest(
                             [dict(row) for row in reference.LINKED_ROWS]))

    def test_source_repository_is_at_the_pinned_revision(self) -> None:
        repository = (reference.AUDIO_ROOT / reference.SOURCE_PRESENCE["path"])
        self.assertTrue(repository.is_dir())
        process = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.strip(), reference.SOURCE_REVISION)

    def test_source_presence_is_not_a_weights_or_runtime_claim(self) -> None:
        presence = reference.SOURCE_PRESENCE
        self.assertTrue(presence["present"])
        self.assertTrue(presence["verified"])
        self.assertFalse(presence["admitted"])
        self.assertFalse(presence["model_executed"])
        self.assertFalse(presence["weights_used"])
        self.assertEqual(presence["present_components"],
                         ["source_code_and_mit_license"])
        self.assertIn("exact_weights_snapshot", presence["absent_components"])
        self.assertIn("exact_runtime", presence["absent_components"])
        self.assertFalse(
            presence["exact_source_weights_runtime_conjunction_present"])

    def test_source_license_is_pinned_and_mit(self) -> None:
        self.assertEqual(reference.SOURCE_PRESENCE["license_id"], "MIT")
        path = reference.AUDIO_ROOT / reference.SOURCE_PRESENCE["license_path"]
        self.assertTrue(path.is_file())
        self.assertEqual(reference.sha256_file(path),
                         reference.SOURCE_PRESENCE["license_sha256"])
        self.assertIn(path.relative_to(reference.AUDIO_ROOT).as_posix(),
                      reference.SOURCE_PINS)

    def test_required_weight_names_match_the_pinned_load_path(self) -> None:
        source = (reference.AUDIO_ROOT /
                  "research/voice-conversion-eval-20261101/repos/"
                  "chatterbox-official/src/chatterbox/tts_turbo.py")
        text = source.read_text(encoding="utf-8")
        for name in ("ve.safetensors", "t3_nano_v1.safetensors",
                     "s3gen_meanflow.safetensors"):
            self.assertIn(name, text)
        self.assertIn('NANO_REPO_ID = "ResembleAI/chatterbox-nano"', text)


class AbsenceTests(unittest.TestCase):
    def test_fixed_probes_are_all_absent(self) -> None:
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(not row["present"] for row in rows))
        home_rows = reference.home_absence_probes()
        self.assertEqual(len(home_rows), len(reference.HOME_ABSENCE_PROBES))
        summary = reference.absence_summary(rows, home_rows)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["network_used"])
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["weights_loaded"])
        self.assertFalse(summary["model_executed"])

    def test_present_probe_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "probe").write_text("x", encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                reference.absence_probes(root, probes=("probe",), worktree=root)
            self.assertEqual(str(caught.exception),
                             "artifact_present_reopen_required:probe")

    def test_probe_list_is_fixed_and_bounded(self) -> None:
        self.assertEqual(len(reference.ABSENCE_PROBES), 27)
        self.assertEqual(len(set(reference.ABSENCE_PROBES)),
                         len(reference.ABSENCE_PROBES))
        self.assertEqual(len(reference.HOME_ABSENCE_PROBES), 2)
        self.assertIn("research/voice-conversion-eval-20261101/"
                      "models/chatterbox-nano/ve.safetensors",
                      reference.ABSENCE_PROBES)
        self.assertIn("research/voice-conversion-eval-20261101/"
                      "models/chatterbox-nano/t3_nano_v1.safetensors",
                      reference.ABSENCE_PROBES)
        self.assertIn("research/voice-conversion-eval-20261101/"
                      "models/chatterbox-nano/s3gen_meanflow.safetensors",
                      reference.ABSENCE_PROBES)

    def test_hf_cache_is_reference_only(self) -> None:
        observed = reference.observed_hf_cache()
        self.assertEqual(observed["repository"], "ResembleAI/chatterbox-nano")
        self.assertEqual(observed["reference_revision"],
                         reference.HF_REFERENCE_REVISION)
        self.assertFalse(observed["blobs_present"])
        self.assertFalse(observed["snapshots_present"])
        self.assertFalse(observed["weights_present"])
        self.assertFalse(observed["admitted"])
        self.assertFalse(observed["used_for_evidence"])

    def test_historical_media_hashes_are_unchanged(self) -> None:
        execution = reference.HISTORICAL_EXECUTION
        output = reference.AUDIO_ROOT / execution["output_path"]
        prompt = reference.AUDIO_ROOT / execution["reference_prompt_path"]
        self.assertTrue(output.is_file())
        self.assertTrue(prompt.is_file())
        self.assertEqual(reference.sha256_file(output),
                         execution["output_sha256"])
        self.assertEqual(reference.sha256_file(prompt),
                         execution["reference_prompt_sha256"])
        self.assertEqual(output.stat().st_size,
                         execution["output_byte_count"])
        self.assertEqual(prompt.stat().st_size,
                         execution["reference_prompt_byte_count"])

    def test_required_artifacts_are_honest(self) -> None:
        artifacts = reference.REQUIRED_ARTIFACTS
        self.assertEqual(len(artifacts), 6)
        self.assertEqual(artifacts[0]["id"], "ART-01")
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        self.assertFalse(artifacts[0]["blocked"])
        for artifact in artifacts[1:]:
            self.assertFalse(artifact["present"])
            self.assertFalse(artifact["verified"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])


class AdmissionTests(unittest.TestCase):
    def assertRejected(self, document: dict, code: str | None = None,
                       field: str | None = None) -> None:
        result = reference.validate_manifest(document, probe_paths=False)
        self.assertFalse(result["accepted"])
        if code is not None:
            self.assertEqual(result["code"], code)
        if field is not None:
            self.assertEqual(result["field"], field)
        self.assertTrue(result["state_unchanged"])

    def test_schema_control_is_accepted_without_qualifying(self) -> None:
        result = reference.validate_manifest(control(), probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertGreater(result["checks"], 0)
        built = reference.admission_controls()
        self.assertEqual(len(built["control"]), 6)
        self.assertEqual(built["control"]["status"],
                         "accepted_schema_control")
        self.assertFalse(built["control"]["qualifies"])
        self.assertEqual(built["control"]["evidence_class"],
                         "synthetic_schema_control_not_evidence")

    def test_path_probe_rejects_missing_artifacts(self) -> None:
        result = reference.validate_manifest(control(), probe_paths=True)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], "probe_missing")

    def test_missing_root_rejected(self) -> None:
        self.assertRejected(None, "manifest_not_object")  # type: ignore[arg-type]

    def test_missing_field_rejected(self) -> None:
        document = control()
        del document["source"]
        self.assertRejected(document, "missing_field", "source")

    def test_unknown_field_rejected(self) -> None:
        document = control()
        document["extra"] = "value"
        self.assertRejected(document, "unknown_field", "extra")

    def test_wrong_schema_rejected(self) -> None:
        document = control()
        document["schema_id"] = "wrong"
        self.assertRejected(document, "invalid_schema", "schema_id")

    def test_uppercase_revision_rejected(self) -> None:
        document = control()
        document["source"]["revision"] = "A" * 40
        self.assertRejected(document, "invalid_value", "source.revision")

    def test_wrong_source_revision_rejected(self) -> None:
        document = control()
        document["source"]["revision"] = "0" * 40
        self.assertRejected(document, "invalid_value", "source.revision")

    def test_relative_path_rejected(self) -> None:
        document = control()
        document["source"]["path"] = "relative/src"
        self.assertRejected(document, "invalid_path", "source.path")

    def test_path_traversal_rejected(self) -> None:
        document = control()
        document["source"]["license_path"] = "/caller/../LICENSE"
        self.assertRejected(document, "invalid_path", "source.license_path")

    def test_null_byte_path_rejected(self) -> None:
        document = control()
        document["references"][0]["path"] = "/caller/ref\x00.wav"
        self.assertRejected(document, "invalid_path", "references.path")

    def test_float_where_int_expected_rejected(self) -> None:
        document = control()
        document["runtime"]["threads"] = 1.5
        self.assertRejected(document, "invalid_value", "runtime.threads")

    def test_boolean_where_int_expected_rejected(self) -> None:
        document = control()
        document["outcomes"]["sample_count"] = True
        self.assertRejected(document, "invalid_value", "outcomes.sample_count")

    def test_wrong_runtime_version_rejected(self) -> None:
        document = control()
        document["runtime"]["torch_version"] = "2.5.0"
        self.assertRejected(document, "invalid_value", "runtime.torch_version")

    def test_cuda_device_rejected(self) -> None:
        document = control()
        document["runtime"]["device"] = "cuda"
        self.assertRejected(document, "invalid_value", "runtime.device")

    def test_non_deterministic_rejected(self) -> None:
        document = control()
        document["runtime"]["deterministic_algorithms"] = False
        self.assertRejected(document, "invalid_value",
                            "runtime.deterministic_algorithms")

    def test_missing_required_weight_rejected(self) -> None:
        document = control()
        document["weights"] = [document["weights"][0]]
        self.assertRejected(document, "invalid_value", "weights.required")

    def test_duplicate_weight_rejected(self) -> None:
        document = control()
        document["weights"].append(dict(document["weights"][0]))
        self.assertRejected(document, "invalid_value", "weights.name")

    def test_weight_name_traversal_rejected(self) -> None:
        document = control()
        document["weights"][0]["name"] = "../ve.safetensors"
        self.assertRejected(document, "invalid_value", "weights.name")

    def test_unknown_reference_rejected(self) -> None:
        document = control()
        document["texts"][0]["reference_id"] = "ref-missing"
        self.assertRejected(document, "invalid_value", "texts.reference_id")

    def test_reference_digest_mismatch_rejected(self) -> None:
        document = control()
        document["texts"][0]["reference_sha256"] = "0" * 64
        self.assertRejected(document, "invalid_value",
                            "texts.reference_sha256")

    def test_missing_control_kind_rejected(self) -> None:
        document = control()
        document["controls"] = [row for row in document["controls"]
                                if row["kind"] != "ignore_reference"]
        self.assertRejected(document, "invalid_value", "controls.required")

    def test_control_reference_mismatch_rejected(self) -> None:
        document = control()
        document["controls"][1]["reference_id"] = "ref-missing"
        self.assertRejected(document, "invalid_value",
                            "controls.reference_id")

    def test_nonfinite_rejected(self) -> None:
        document = control()
        document["outcomes"]["text_semantic_wer"] = float("nan")
        self.assertRejected(document, "nonfinite_value",
                            "outcomes.text_semantic_wer")

    def test_infinite_rejected(self) -> None:
        document = control()
        document["outcomes"]["first_output_ms"] = float("inf")
        self.assertRejected(document, "nonfinite_value",
                            "outcomes.first_output_ms")

    def test_nonfinite_count_rejected(self) -> None:
        document = control()
        document["outcomes"]["nonfinite_count"] = 1
        self.assertRejected(document, "invalid_value",
                            "outcomes.nonfinite_count")

    def test_out_of_range_mos_rejected(self) -> None:
        document = control()
        document["outcomes"]["naturalness_mos"] = 5.1
        self.assertRejected(document, "invalid_value", "outcomes.naturalness_mos")

    def test_empty_rights_rejected(self) -> None:
        document = control()
        document["rights"]["output_use"] = ""
        self.assertRejected(document, "invalid_value", "rights.output_use")

    def test_adverse_matrix_is_frozen_and_all_rejected(self) -> None:
        built = reference.admission_controls()
        self.assertEqual(len(built["cases"]), 153)
        self.assertEqual(len(built["control"]), 6)
        for case in built["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])
        summary = built["summary"]
        self.assertEqual(summary["case_count"], 153)
        self.assertEqual(summary["rejected_count"], 153)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["runtime_invoked"])
        self.assertFalse(summary["audio_read"])
        self.assertFalse(summary["weights_loaded"])
        self.assertFalse(summary["model_executed"])


class ContractAndReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.read_strict_json(HERE / "contract.json")
        cls.report = reference.read_strict_json(HERE / "report.json")

    def test_contract_validation(self) -> None:
        reference.validate_contract(self.contract)

    def test_contract_is_canonical_bytes(self) -> None:
        self.assertEqual(
            (HERE / "contract.json").read_bytes(),
            reference.canonical_bytes(reference.build_contract()))

    def test_report_decision_and_qualification(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.report["proposal_only"])

    def test_disposition_is_proposal_only_not_qualified(self) -> None:
        disposition = self.report["disposition"]
        self.assertEqual(disposition["decision"], "DEFER")
        self.assertEqual(disposition["status"], "incomplete")
        self.assertEqual(disposition["qualification_status"],
                         "not_qualified")
        self.assertEqual(disposition["promotion"], "defer")
        self.assertEqual(disposition["production_exposure"], "DEFER")
        for key in ("proposal_only", "incomplete", "not_qualified"):
            self.assertTrue(disposition[key])
        for key in ("expose_as_processor", "registered", "default_enabled",
                    "missing_result_qualifies"):
            self.assertFalse(disposition[key])

    def test_eight_release_gates_are_blocked(self) -> None:
        self.assertEqual(len(self.report["gates"]), 8)
        self.assertEqual([row["id"] for row in self.report["gates"]],
                         ["RG-0%d" % index for index in range(1, 9)])
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             reference.BOARD_ROW_PROJECTION)

    def test_required_artifacts_have_one_verified_source(self) -> None:
        artifacts = self.report["required_artifacts"]
        self.assertEqual(len(artifacts), 6)
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        self.assertFalse(artifacts[0]["blocked"])
        for row in artifacts[1:]:
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertTrue(row["blocked"])
            self.assertIsNone(row["sha256"])

    def test_exact_blockers_are_open(self) -> None:
        self.assertEqual(len(self.report["exact_blockers"]), 5)
        artifact_ids = {row["id"]
                        for row in self.report["required_artifacts"]}
        for row in self.report["exact_blockers"]:
            self.assertEqual(row["status"], "open")
            self.assertFalse(row["qualifies"])
            self.assertIn(row["artifact_id"], artifact_ids)
            self.assertTrue(row["required_action"])

    def test_qualification_has_no_true_result(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["readiness"], "incomplete")
        self.assertTrue(qualification["all_release_gates_blocked"])
        self.assertTrue(qualification["not_qualified"])
        self.assertTrue(qualification["source_present"])
        for key, value in qualification.items():
            if key in ("status", "readiness", "all_release_gates_blocked",
                       "not_qualified", "source_present"):
                continue
            self.assertFalse(value, key)

    def test_boundary_and_scope_claims_are_false(self) -> None:
        for section in ("boundary", "scope"):
            for key, value in self.report[section].items():
                if key in ("task_local_only", "source_present"):
                    self.assertTrue(value)
                else:
                    self.assertFalse(value, section + "." + key)

    def test_public_geometry_preserved(self) -> None:
        geometry = self.report["public_v0_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertTrue(geometry["preserved"])
        self.assertFalse(geometry["sdk_callback_invoked"])

    def test_absence_summary_blocks_shipping(self) -> None:
        evidence = self.report["absence_evidence"]
        summary = evidence["summary"]
        self.assertEqual(summary["probe_count"], 29)
        self.assertEqual(summary["workspace_probe_count"], 27)
        self.assertEqual(summary["home_probe_count"], 2)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["network_used"])
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["source_or_runtime_imported"])
        self.assertFalse(summary["weights_loaded"])
        self.assertFalse(summary["model_executed"])
        self.assertFalse(summary["audio_read"])
        cache = evidence["observed_hf_cache"]
        self.assertFalse(cache["blobs_present"])
        self.assertFalse(cache["snapshots_present"])
        self.assertFalse(cache["weights_present"])
        self.assertFalse(cache["admitted"])
        media = evidence["observed_media"]
        self.assertFalse(media["audio_read"])
        self.assertFalse(media["listening_performed"])
        self.assertFalse(media["used_for_evidence"])
        self.assertTrue(media["byte_hash_only"])
        self.assertFalse(media["decoded"])
        self.assertFalse(media["signal_loaded"])

    def test_admission_summary_has_no_qualifying_result(self) -> None:
        summary = self.report["admission"]["summary"]
        self.assertEqual(summary["case_count"], 153)
        self.assertEqual(summary["rejected_count"], 153)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["runtime_invoked"])
        self.assertFalse(summary["audio_read"])
        self.assertFalse(summary["weights_loaded"])
        self.assertFalse(summary["model_executed"])
        self.assertFalse(summary["network_used"])

    def test_voice_profile_is_blocked(self) -> None:
        profile = self.report["voice_profile"]
        self.assertEqual(profile["status"], "blocked")
        self.assertEqual([row["id"] for row in profile["rows"]],
                         ["V-0%d" % index for index in range(1, 9)])
        for row in profile["rows"]:
            self.assertEqual(row["status"], "blocked")
        for key, value in profile.items():
            if key in ("profile", "rows", "status"):
                continue
            self.assertFalse(value, key)

    def test_quality_and_timing_are_blocked(self) -> None:
        quality = self.report["quality_outcomes"]
        self.assertEqual(quality["status"], "blocked")
        self.assertEqual([row["id"] for row in quality["rows"]],
                         ["QO-0%d" % index for index in range(1, 4)])
        for row in quality["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
        timing = self.report["timing"]
        self.assertEqual(timing["status"], "blocked")
        self.assertEqual([row["id"] for row in timing["rows"]],
                         ["TM-0%d" % index for index in range(1, 4)])
        for row in timing["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
        for section in (quality, timing):
            for key, value in section.items():
                if key in ("status", "rows"):
                    continue
                self.assertFalse(value, key)

    def test_historical_execution_is_provenance_only(self) -> None:
        execution = self.report["historical_execution"]
        self.assertTrue(execution["not_rerun"])
        self.assertFalse(execution["merged_task_evidence"])
        self.assertFalse(execution["used_for_evidence"])
        self.assertFalse(execution["qualifies"])
        self.assertFalse(execution["first_audio_latency_present"])
        self.assertFalse(execution["streaming_chunks_present"])
        self.assertFalse(execution["naturalness_measured"])
        self.assertFalse(execution["identity_similarity_measured"])
        self.assertFalse(execution["manual_transcript_present"])
        self.assertFalse(execution["device_timing_present"])
        self.assertEqual(execution["metrics_sha256"],
                         reference.SOURCE_PINS[
                             "research/voice-conversion-eval-20261101/"
                             "results/chatterbox-nano/metrics.json"])
        self.assertEqual(execution["asr_sha256"],
                         reference.SOURCE_PINS[
                             "research/voice-conversion-eval-20261101/"
                             "results/chatterbox-nano/asr.json"])

    def test_linked_row_identity_excludes_mutable_fields(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["projection"],
                         reference.BOARD_ROW_PROJECTION)
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(
                             reference.BOARD_ROW_PROJECTION))
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        for mutable in identity["mutable_fields_excluded"]:
            self.assertNotIn(mutable, identity["projection"])
        self.assertEqual(identity["linked_rows"],
                         [dict(row) for row in reference.LINKED_ROWS])

    def test_contract_digest_matches_report(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_report_has_no_floats(self) -> None:
        def walk(value):
            if isinstance(value, dict):
                for item in value.values():
                    yield from walk(item)
            elif isinstance(value, list):
                for item in value:
                    yield from walk(item)
            else:
                yield value

        self.assertFalse(any(isinstance(value, float)
                             for value in walk(self.report)))

    def test_report_canonical_regeneration_is_byte_identical(self) -> None:
        first, digest = reference.canonical_report(reference.build_report())
        second, second_digest = reference.canonical_report(
            reference.build_report())
        self.assertEqual(first, second)
        self.assertEqual(digest, second_digest)
        self.assertEqual(first.encode("utf-8"),
                         (HERE / "report.json").read_bytes())
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")

    def test_profile_phrases_are_exact(self) -> None:
        source = (reference.AUDIO_ROOT
                  / "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
        text = source.read_text(encoding="utf-8")
        rows = [line for line in text.splitlines()
                if line.startswith("| Voice |")]
        self.assertEqual(len(rows), 1)
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, rows[0])

    def test_pinned_sources_and_boundary_exist(self) -> None:
        for relative, digest in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest)
        for relative, digest in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest)

    def test_no_result_keys_are_claimed(self) -> None:
        text = (HERE / "report.json").read_text(encoding="utf-8")
        for forbidden in ('"identity_similarity_value":',
                          '"naturalness_value":', '"alignment_value":',
                          '"first_output_value":', '"tail_value":',
                          '"device_timing_value":'):
            self.assertNotIn(forbidden, text)


class PackageArtifactTests(unittest.TestCase):
    def test_python_spdx_headers(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_LICENSE_LINE, head, path.name)
            self.assertIn(SPDX_COPYRIGHT_LINE, head, path.name)

    def test_license_sidecars(self) -> None:
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "report.json.license", "report.json.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_LICENSE_LINE, text)
            self.assertIn(SPDX_COPYRIGHT_LINE, text)

    def test_no_binary_or_vendored_license_artifacts(self) -> None:
        forbidden = {".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib",
                     ".m4a", ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus",
                     ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".so", ".wasm",
                     ".wav", ".weights"}
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name,
                             {"CMakeLists.txt", "provider.json",
                              "adapter.json", "COPYING", "NOTICE", "LICENSE",
                              "LICENSE.txt"})

    def test_deliverables_exist(self) -> None:
        for name in ("README.md", "LICENSES.md", "contract.json",
                     "reference.py", "report.json", "report.json.sha256",
                     "SOURCES.sha256", "verify.py", "test_reference.py",
                     "run.py"):
            self.assertTrue((HERE / name).is_file(), name)

    def test_report_sidecar_digest_matches_bytes(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")


if __name__ == "__main__":
    unittest.main()
