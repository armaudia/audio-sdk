# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library tests for SDK-OPENVOICE-V2."""

from __future__ import annotations

import copy
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

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

    def test_source_tree_digest_matches_the_pinned_values(self) -> None:
        repository = (reference.AUDIO_ROOT / reference.SOURCE_PRESENCE["path"])
        observed = reference.verify_source_tree(repository)
        self.assertEqual(observed["sha256"], reference.SOURCE_TREE_SHA256)
        self.assertEqual(observed["file_count"],
                         reference.SOURCE_TREE_FILE_COUNT)
        self.assertEqual(observed["byte_count"],
                         reference.SOURCE_TREE_BYTE_COUNT)
        self.assertEqual(observed["sha256"],
                         reference.SOURCE_PRESENCE["tree_sha256"])

    def test_source_presence_is_not_a_weights_or_runtime_claim(self) -> None:
        presence = reference.SOURCE_PRESENCE
        self.assertTrue(presence["present"])
        self.assertTrue(presence["verified"])
        self.assertFalse(presence["admitted"])
        self.assertFalse(presence["model_executed"])
        self.assertFalse(presence["weights_used"])
        self.assertEqual(presence["present_components"],
                         ["source_code_and_mit_license"])
        self.assertIn("verified_v2_weight_archive",
                      presence["absent_components"])
        self.assertIn("converter_checkpoint", presence["absent_components"])
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
        demo = (reference.AUDIO_ROOT /
                "research/voice-conversion-eval-20261101/repos/openvoice/"
                "demo_part3.ipynb").read_text(encoding="utf-8")
        self.assertIn("checkpoints_v2/converter", demo)
        self.assertIn("checkpoint.pth", demo)
        self.assertIn("config.json", demo)
        api = (reference.AUDIO_ROOT /
               "research/voice-conversion-eval-20261101/repos/openvoice/"
               "openvoice/api.py").read_text(encoding="utf-8")
        self.assertIn("class ToneColorConverter", api)
        self.assertIn("def load_ckpt", api)
        for name in reference.REQUIRED_WEIGHTS:
            self.assertIn(name, reference.REQUIRED_WEIGHTS)

    def test_observed_config_copy_is_pinned_but_not_admitted(self) -> None:
        observed = reference.observed_config_copy()
        record = reference.OBSERVED_CONFIG_COPY
        self.assertTrue(observed["present"])
        self.assertEqual(observed["observed_sha256"], record["sha256"])
        self.assertEqual(observed["observed_byte_count"], record["byte_count"])
        self.assertFalse(record["admitted"])
        self.assertFalse(record["exact_release_archive_member"])
        self.assertFalse(record["companion_checkpoint_present"])
        self.assertFalse(record["used_for_evidence"])
        self.assertEqual(reference.REQUIRED_WEIGHT_FILES,
                         reference.REQUIRED_WEIGHTS)


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
        self.assertEqual(len(reference.ABSENCE_PROBES), 30)
        self.assertEqual(len(set(reference.ABSENCE_PROBES)),
                         len(reference.ABSENCE_PROBES))
        self.assertEqual(len(reference.HOME_ABSENCE_PROBES), 3)
        self.assertIn("research/voice-conversion-eval-20261101/"
                      "repos/openvoice/checkpoints_v2/converter/"
                      "checkpoint.pth",
                      reference.ABSENCE_PROBES)
        self.assertIn("research/voice-conversion-eval-20261101/"
                      "checkpoints_v2_0417.zip",
                      reference.ABSENCE_PROBES)

    def test_observed_cache_paths_are_absent(self) -> None:
        rows = reference.observed_cache_paths()
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertFalse(row["present"], row["path"])

    def test_historical_media_hashes_are_unchanged(self) -> None:
        execution = reference.HISTORICAL_EXECUTION
        output = reference.AUDIO_ROOT / execution["output_path"]
        metrics = reference.AUDIO_ROOT / execution["metrics_path"]
        asr = reference.AUDIO_ROOT / execution["asr_path"]
        source = reference.AUDIO_ROOT / execution["source_audio_path"]
        target = reference.AUDIO_ROOT / execution["target_audio_path"]
        for path in (output, metrics, asr, source, target):
            self.assertTrue(path.is_file(), path)
        self.assertEqual(reference.sha256_file(output),
                         execution["output_sha256"])
        self.assertEqual(reference.sha256_file(metrics),
                         execution["metrics_sha256"])
        self.assertEqual(reference.sha256_file(asr),
                         execution["asr_sha256"])
        self.assertEqual(reference.sha256_file(source),
                         execution["source_audio_sha256"])
        self.assertEqual(reference.sha256_file(target),
                         execution["target_audio_sha256"])
        self.assertEqual(output.stat().st_size,
                         execution["output_byte_count"])
        self.assertEqual(source.stat().st_size,
                         execution["source_audio_byte_count"])
        self.assertEqual(target.stat().st_size,
                         execution["target_audio_byte_count"])

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
        document["references"][0]["path"] = "/caller/ref\x00.pt"
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
        document["runtime"]["torch_version"] = "2.6.0"
        self.assertRejected(document, "invalid_value", "runtime.torch_version")

    def test_wrong_python_minor_rejected(self) -> None:
        document = control()
        document["runtime"]["python_version"] = "3.12.16"
        self.assertRejected(document, "invalid_value",
                            "runtime.python_version")

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
        document["weights"] = [document["weights"][1]]
        self.assertRejected(document, "invalid_value", "weights.required")

    def test_duplicate_weight_rejected(self) -> None:
        document = control()
        document["weights"].append(dict(document["weights"][0]))
        self.assertRejected(document, "invalid_value", "weights.name")

    def test_weight_name_traversal_rejected(self) -> None:
        document = control()
        document["weights"][0]["name"] = "../config.json"
        self.assertRejected(document, "invalid_value", "weights.name")

    def test_weight_name_absolute_rejected(self) -> None:
        document = control()
        document["weights"][0]["name"] = "/config.json"
        self.assertRejected(document, "invalid_value", "weights.name")

    def test_same_source_and_target_rejected(self) -> None:
        document = control()
        document["pairs"][0]["target_reference_id"] = "source-a"
        self.assertRejected(document, "invalid_value",
                            "pairs.target_reference_id")

    def test_unknown_reference_rejected(self) -> None:
        document = control()
        document["pairs"][0]["target_reference_id"] = "missing"
        self.assertRejected(document, "invalid_value",
                            "pairs.target_reference_id")

    def test_reference_digest_mismatch_rejected(self) -> None:
        document = control()
        document["pairs"][0]["target_reference_sha256"] = "0" * 64
        self.assertRejected(document, "invalid_value",
                            "pairs.target_reference_sha256")

    def test_missing_control_kind_rejected(self) -> None:
        document = control()
        document["controls"] = [row for row in document["controls"]
                                if row["kind"] != "alternate_target"]
        self.assertRejected(document, "invalid_value", "controls.required")

    def test_control_reference_mismatch_rejected(self) -> None:
        document = control()
        document["controls"][1]["reference_id"] = "missing"
        self.assertRejected(document, "invalid_value",
                            "controls.reference_id")

    def test_alternate_target_must_differ_rejected(self) -> None:
        document = control()
        document["controls"][2]["reference_id"] = "target-b"
        self.assertRejected(document, "invalid_value",
                            "controls.alternate_target")

    def test_nonfinite_rejected(self) -> None:
        document = control()
        document["outcomes"]["content_wer"] = float("nan")
        self.assertRejected(document, "nonfinite_value",
                            "outcomes.content_wer")

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
        self.assertRejected(document, "invalid_value",
                            "outcomes.naturalness_mos")

    def test_empty_rights_rejected(self) -> None:
        document = control()
        document["rights"]["output_use"] = ""
        self.assertRejected(document, "invalid_value", "rights.output_use")

    def test_adverse_matrix_is_frozen_and_all_rejected(self) -> None:
        built = reference.admission_controls()
        self.assertGreater(len(built["cases"]), 120)
        self.assertEqual(len(built["control"]), 6)
        for case in built["cases"]:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])
        summary = built["summary"]
        self.assertEqual(summary["case_count"], len(built["cases"]))
        self.assertEqual(summary["rejected_count"], len(built["cases"]))
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
        self.assertEqual(summary["probe_count"],
                         len(reference.ABSENCE_PROBES)
                         + len(reference.HOME_ABSENCE_PROBES))
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["network_used"])
        self.assertFalse(summary["recursive_workspace_walk"])
        media = evidence["observed_media"]
        self.assertTrue(media["byte_hash_only"])
        self.assertFalse(media["decoded"])
        self.assertFalse(media["signal_loaded"])
        self.assertFalse(media["audio_read"])
        self.assertFalse(media["listening_performed"])
        self.assertFalse(media["used_for_evidence"])

    def test_observed_config_copy_is_non_admitted(self) -> None:
        copy = self.report["absence_evidence"]["observed_config_copy"]
        self.assertTrue(copy["present"])
        self.assertFalse(copy["admitted"])
        self.assertFalse(copy["exact_release_archive_member"])
        self.assertFalse(copy["companion_checkpoint_present"])
        self.assertFalse(copy["used_for_evidence"])
        self.assertEqual(copy["observed_sha256"],
                         reference.OBSERVED_CONFIG_COPY["sha256"])

    def test_admission_summary_has_no_qualifying_result(self) -> None:
        admission = self.report["admission"]
        self.assertEqual(admission["summary"]["qualifying_results"], 0)
        self.assertEqual(admission["summary"]["accepted_schema_controls"], 1)
        self.assertTrue(admission["control"]["accepted"])
        self.assertFalse(admission["control"]["qualifies"])
        self.assertGreater(len(admission["cases"]), 120)
        for case in admission["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])

    def test_voice_profile_is_blocked(self) -> None:
        voice = self.report["voice_profile"]
        self.assertEqual(voice["status"], "blocked")
        self.assertEqual(len(voice["rows"]), 8)
        for row in voice["rows"]:
            self.assertEqual(row["status"], "blocked")
        for key, value in voice.items():
            if key in ("profile", "status", "rows"):
                continue
            self.assertFalse(value, key)

    def test_quality_and_timing_are_blocked(self) -> None:
        quality = self.report["quality_outcomes"]
        timing = self.report["timing"]
        self.assertEqual(quality["status"], "blocked")
        self.assertEqual(len(quality["rows"]), 3)
        self.assertEqual(timing["status"], "blocked")
        self.assertEqual(len(timing["rows"]), 3)
        for row in quality["rows"] + timing["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])

    def test_historical_execution_is_provenance_only(self) -> None:
        execution = self.report["historical_execution"]
        self.assertTrue(execution["not_rerun"])
        self.assertFalse(execution["merged_task_evidence"])
        self.assertFalse(execution["used_for_evidence"])
        self.assertFalse(execution["qualifies"])
        self.assertFalse(execution["first_audio_latency_present"])
        self.assertFalse(execution["streaming_chunks_present"])
        self.assertFalse(execution["causal_path_present"])
        self.assertFalse(execution["naturalness_measured"])
        self.assertFalse(execution["independent_identity_measured"])
        self.assertFalse(execution["in_model_cosine_is_perceptual"])
        self.assertEqual(execution["sample_rate_hz"], 22050)
        self.assertEqual(execution["target_reference"], "p360")

    def test_linked_row_identity_excludes_mutable_fields(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["projection"],
                         reference.BOARD_ROW_PROJECTION)
        self.assertIn("status", identity["mutable_fields_excluded"])

    def test_contract_digest_matches_report(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_report_has_no_floats(self) -> None:
        reference._no_floats(self.report)

    def test_report_canonical_regeneration_is_byte_identical(self) -> None:
        text, digest = reference.canonical_report(self.report)
        self.assertEqual((HERE / "report.json").read_bytes(),
                         text.encode("utf-8"))
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")

    def test_profile_phrases_are_exact(self) -> None:
        profile = (reference.AUDIO_ROOT /
                   "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
        row = [line for line in profile.read_text(encoding="utf-8").splitlines()
               if line.startswith("| Voice |")]
        self.assertEqual(len(row), 1)
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, row[0])
        self.assertEqual(self.report["profile"], "Voice")
        self.assertEqual(self.report["profile_key"], "voice")

    def test_pinned_sources_and_boundary_exist(self) -> None:
        for relative, digest in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest, relative)
        for relative, digest in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest, relative)

    def test_no_result_keys_are_claimed(self) -> None:
        forbidden = {"score", "mos", "wer", "similarity", "latency_ms",
                     "rtf", "si_sdr", "stoi", "passed"}
        def walk(value: Any) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    self.assertNotIn(key, forbidden)
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
        walk(self.report)


class PackageArtifactTests(unittest.TestCase):
    def test_python_spdx_headers(self) -> None:
        for name in ("reference.py", "run.py", "test_reference.py",
                     "verify.py"):
            head = "\n".join((HERE / name).read_text(
                encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_LICENSE_LINE, head, name)
            self.assertIn(SPDX_COPYRIGHT_LINE, head, name)

    def test_license_sidecars(self) -> None:
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "report.json.license", "report.json.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_LICENSE_LINE, text)
            self.assertIn(SPDX_COPYRIGHT_LINE, text)

    def test_no_binary_or_vendored_license_artifacts(self) -> None:
        forbidden = {".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib",
                     ".m4a", ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus",
                     ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".so",
                     ".wasm", ".wav", ".weights"}
        for path in sorted(HERE.iterdir()):
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name,
                             {"LICENSE", "LICENSE.txt", "COPYING", "NOTICE"})

    def test_deliverables_exist(self) -> None:
        for name in ("README.md", "LICENSES.md", "contract.json",
                     "reference.py", "report.json", "report.json.sha256",
                     "SOURCES.sha256", "verify.py", "test_reference.py",
                     "run.py", "SOURCES.sha256.license",
                     "contract.json.license", "report.json.license",
                     "report.json.sha256.license"):
            self.assertTrue((HERE / name).is_file(), name)

    def test_report_sidecar_digest_matches_bytes(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"),
            f"{hashlib.sha256(payload).hexdigest()}  report.json\n")


if __name__ == "__main__":
    unittest.main()
