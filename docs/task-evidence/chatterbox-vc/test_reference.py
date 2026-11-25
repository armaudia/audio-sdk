# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the SDK-CHATTERBOX-VC evidence package.

No network, model runtime, weight, audio decode, listening or inference path is
used. All checks run on standard-library data and fixed read-only inputs.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

DELIVERABLES = (
    "README.md",
    "LICENSES.md",
    "contract.json",
    "reference.py",
    "report.json",
    "report.json.sha256",
    "SOURCES.sha256",
    "verify.py",
    "test_reference.py",
    "run.py",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)

# REUSE-IgnoreStart
SPDX_LICENSE_LINE = "SPDX-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd


def control() -> dict:
    return reference._manifest_control()


class StrictJsonTests(unittest.TestCase):
    def test_canonical_text_is_sorted_compact_and_newline_terminated(self) -> None:
        text = reference.canonical_text({"b": 1, "a": [2, 3]})
        self.assertEqual(text, '{"a":[2,3],"b":1}\n')

    def test_canonical_bytes_round_trip(self) -> None:
        document = {"a": [1, 2], "b": {"c": "d"}}
        encoded = reference.canonical_bytes(document)
        self.assertEqual(reference.loads_strict(encoded.decode("utf-8")),
                         document)

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a": 1, "a": 2}')
        self.assertIn("duplicate_json_key", str(caught.exception))

    def test_nan_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a": NaN}')
        self.assertIn("nonfinite_json_constant", str(caught.exception))

    def test_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a": Infinity}')

    def test_negative_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a": -Infinity}')

    def test_root_array_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict("[]")
        self.assertEqual(str(caught.exception), "json_root_not_object")

    def test_byte_order_mark_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('\ufeff{"a": 1}')
        self.assertEqual(str(caught.exception), "json_byte_order_mark")

    def test_object_digest_is_stable(self) -> None:
        self.assertEqual(reference.object_digest({"b": 2, "a": 1}),
                         reference.object_digest({"a": 1, "b": 2}))


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

    def test_sources_manifest_never_pins_the_board(self) -> None:
        import run
        text = run.sources_bytes().decode("ascii")
        self.assertNotIn(reference.BOARD_TASK_ROW, text)
        self.assertNotIn("plan/swarm/TASKS.json", text)

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
                         ["source_code_and_apache_2_0_license"])
        self.assertIn("exact_weights_snapshot", presence["absent_components"])
        self.assertIn("chatterbox_tts_runtime", presence["absent_components"])
        self.assertFalse(
            presence["exact_source_weights_runtime_conjunction_present"])

    def test_source_license_is_pinned_and_apache(self) -> None:
        self.assertEqual(reference.SOURCE_PRESENCE["license_id"], "Apache-2.0")
        path = reference.AUDIO_ROOT / reference.SOURCE_PRESENCE["license_path"]
        self.assertTrue(path.is_file())
        self.assertEqual(reference.sha256_file(path),
                         reference.SOURCE_PRESENCE["license_sha256"])
        self.assertIn(path.relative_to(reference.AUDIO_ROOT).as_posix(),
                      reference.SOURCE_PINS)

    def test_wrapper_metadata_matches_the_pinned_contract(self) -> None:
        root = (reference.AUDIO_ROOT / "research/"
                "voice-conversion-eval-20261101/repos/chatterbox-vc")
        metadata = (root / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('name = "chatterbox-voice-conversion"', metadata)
        self.assertIn('version = "0.1.0"', metadata)
        self.assertIn("chatterbox-tts>=0.1.1", metadata)
        self.assertIn('license = {text = "Apache-2.0"}', metadata)

    def test_required_weight_names_match_the_pinned_load_path(self) -> None:
        converter = (reference.AUDIO_ROOT / "research/"
                     "voice-conversion-eval-20261101/repos/chatterbox-vc/"
                     "chatterbox_vc/convert.py")
        text = converter.read_text(encoding="utf-8")
        for name in reference.REQUIRED_WEIGHT_FILES:
            self.assertIn(name, text)
        self.assertIn("ResembleAI/chatterbox", text)
        breadth = (reference.AUDIO_ROOT / "research/"
                   "voice-conversion-eval-20261101/agent-chatterbox-breadth/"
                   "REPORT.md").read_text(encoding="utf-8")
        for name in reference.REQUIRED_WEIGHT_FILES:
            self.assertIn(name, breadth)


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
                reference.absence_probes(root, probes=("probe",),
                                         worktree=root)
            self.assertEqual(str(caught.exception),
                             "artifact_present_reopen_required:probe")

    def test_probe_list_is_fixed_and_bounded(self) -> None:
        self.assertEqual(len(reference.ABSENCE_PROBES), 22)
        self.assertEqual(len(set(reference.ABSENCE_PROBES)),
                         len(reference.ABSENCE_PROBES))
        self.assertEqual(len(reference.HOME_ABSENCE_PROBES), 4)
        self.assertIn("research/voice-conversion-eval-20261101/"
                      "models/chatterbox-vc/s3gen.safetensors",
                      reference.ABSENCE_PROBES)
        self.assertIn("research/voice-conversion-eval-20261101/"
                      "models/chatterbox-vc/conds.pt",
                      reference.ABSENCE_PROBES)
        self.assertIn("research/voice-conversion-eval-20261101/"
                      ".venv-chatterbox", reference.ABSENCE_PROBES)

    def test_hf_cache_is_reference_only(self) -> None:
        observed = reference.observed_hf_cache()
        self.assertEqual(observed["repository"], "ResembleAI/chatterbox")
        self.assertIsNone(observed["reference_revision"])
        self.assertFalse(observed["repository_directory_present"])
        self.assertFalse(observed["blobs_present"])
        self.assertFalse(observed["snapshots_present"])
        self.assertFalse(observed["weights_present"])
        self.assertFalse(observed["admitted"])
        self.assertFalse(observed["used_for_evidence"])

    def test_historical_media_hashes_are_unchanged(self) -> None:
        execution = reference.HISTORICAL_EXECUTION
        output = reference.AUDIO_ROOT / execution["output_path"]
        source = reference.AUDIO_ROOT / execution["source_audio_path"]
        target = reference.AUDIO_ROOT / execution["target_voice_path"]
        for path, digest, size in (
                (output, execution["output_sha256"],
                 execution["output_byte_count"]),
                (source, execution["source_audio_sha256"],
                 execution["source_audio_byte_count"]),
                (target, execution["target_voice_sha256"],
                 execution["target_voice_byte_count"])):
            self.assertTrue(path.is_file(), path.name)
            self.assertEqual(reference.sha256_file(path), digest)
            self.assertEqual(path.stat().st_size, size)

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
        self.assertFalse(result["accepted"], f"accepted: {document}")
        self.assertEqual(result["state_unchanged"], True)
        if code is not None:
            self.assertEqual(result["code"], code)
        if field is not None:
            self.assertEqual(result["field"], field)

    def test_schema_control_is_accepted_without_qualifying(self) -> None:
        result = reference.validate_manifest(control(), probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"], "ok")
        self.assertGreater(result["checks"], 0)
        matrix = reference.admission_controls()
        self.assertTrue(matrix["control"]["accepted"])
        self.assertEqual(matrix["control"]["evidence_class"],
                         "synthetic_schema_control_not_evidence")
        self.assertFalse(matrix["control"]["qualifies"])

    def test_path_probe_rejects_missing_artifacts(self) -> None:
        result = reference.validate_manifest(control(), probe_paths=True)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], "probe_missing")

    def test_missing_root_rejected(self) -> None:
        self.assertRejected(None, "manifest_not_object")
        self.assertRejected([], "manifest_not_object")
        self.assertRejected("x", "manifest_not_object")

    def test_missing_field_rejected(self) -> None:
        document = control()
        del document["rights"]
        self.assertRejected(document, "missing_field", "rights")

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
        document["converter"]["revision"] = "A" * 40
        self.assertRejected(document, "invalid_value", "converter.revision")

    def test_wrong_source_revision_rejected(self) -> None:
        document = control()
        document["converter"]["revision"] = "0" * 40
        self.assertRejected(document, "invalid_value", "converter.revision")

    def test_relative_path_rejected(self) -> None:
        document = control()
        document["source_audio"][0]["path"] = "src.wav"
        self.assertRejected(document, "invalid_path", "source_audio.path")

    def test_path_traversal_rejected(self) -> None:
        document = control()
        document["targets"][0]["path"] = "/caller/../target.wav"
        self.assertRejected(document, "invalid_path", "targets.path")

    def test_null_byte_path_rejected(self) -> None:
        document = control()
        document["converter"]["path"] = "/caller/src\x00"
        self.assertRejected(document, "invalid_path", "converter.path")

    def test_float_where_int_expected_rejected(self) -> None:
        document = control()
        document["outcomes"]["sample_count"] = 16000.0
        self.assertRejected(document, "invalid_value", "outcomes.sample_count")

    def test_boolean_where_int_expected_rejected(self) -> None:
        document = control()
        document["outcomes"]["alignment_samples"] = True
        self.assertRejected(document, "invalid_value",
                            "outcomes.alignment_samples")

    def test_wrong_runtime_version_rejected(self) -> None:
        document = control()
        document["runtime"]["torch_version"] = "2.5.0"
        self.assertRejected(document, "invalid_value", "runtime.torch_version")

    def test_wrong_chatterbox_version_rejected(self) -> None:
        document = control()
        document["runtime"]["chatterbox_tts_version"] = "0.1.1"
        self.assertRejected(document, "invalid_value",
                            "runtime.chatterbox_tts_version")

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
        document["weights"][0]["name"] = "../s3gen.safetensors"
        self.assertRejected(document, "invalid_value", "weights.name")

    def test_unknown_target_rejected(self) -> None:
        document = control()
        document["controls"][0]["target_id"] = "tgt-missing"
        self.assertRejected(document, "invalid_value", "controls.target_id")

    def test_matched_equals_mismatched_rejected(self) -> None:
        document = control()
        document["controls"][1]["target_id"] = "tgt-a"
        self.assertRejected(document, "invalid_value",
                            "controls.matched_vs_mismatched")

    def test_identity_control_with_target_rejected(self) -> None:
        document = control()
        document["controls"][2]["target_id"] = "tgt-a"
        self.assertRejected(document, "invalid_value", "controls.target_id")

    def test_missing_control_kind_rejected(self) -> None:
        document = control()
        document["controls"] = document["controls"][:2]
        self.assertRejected(document, "invalid_value", "controls.required")

    def test_transcript_must_be_manual(self) -> None:
        document = control()
        document["source_audio"][0]["transcript_source"] = "asr"
        self.assertRejected(document, "invalid_value",
                            "source_audio.transcript_source")

    def test_nonfinite_rejected(self) -> None:
        document = control()
        document["outcomes"]["content_wer"] = float("nan")
        self.assertRejected(document, "nonfinite_value")

    def test_infinite_rejected(self) -> None:
        document = control()
        document["outcomes"]["identity_similarity_cosine"] = float("inf")
        self.assertRejected(document, "nonfinite_value")

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
        document["rights"]["consent_reference"] = ""
        self.assertRejected(document, "invalid_value",
                            "rights.consent_reference")

    def test_adverse_matrix_is_frozen_and_all_rejected(self) -> None:
        matrix = reference.admission_controls()
        self.assertEqual(matrix["summary"]["case_count"], 158)
        self.assertEqual(matrix["summary"]["rejected_count"], 158)
        self.assertEqual(matrix["summary"]["accepted_schema_controls"], 1)
        self.assertEqual(matrix["summary"]["qualifying_results"], 0)
        for case in matrix["cases"]:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])
        for key in ("state_advanced_on_rejection", "runtime_invoked",
                    "audio_read", "weights_loaded", "model_executed",
                    "network_used"):
            self.assertFalse(matrix["summary"][key])
        ids = [case["id"] for case in matrix["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("outcome-wer-nan", ids)
        self.assertIn("source-audio-path-null", ids)


class ContractAndReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_validation(self) -> None:
        reference.validate_contract(copy.deepcopy(self.contract))

    def test_contract_is_canonical_bytes(self) -> None:
        self.assertEqual(
            reference.canonical_bytes(self.contract),
            (json.dumps(self.contract, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=True, allow_nan=False) + "\n").encode())

    def test_report_decision_and_qualification(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["proposal_only"])

    def test_disposition_is_proposal_only_not_qualified(self) -> None:
        disposition = self.report["disposition"]
        self.assertEqual(disposition["decision"], "DEFER")
        self.assertEqual(disposition["status"], "incomplete")
        self.assertEqual(disposition["qualification_status"],
                         "not_qualified")
        self.assertTrue(disposition["proposal_only"])
        self.assertFalse(disposition["registered"])
        self.assertFalse(disposition["default_enabled"])
        self.assertFalse(disposition["missing_result_qualifies"])
        self.assertEqual(disposition, self.contract["disposition"])

    def test_eight_release_gates_are_blocked(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        for index, gate in enumerate(gates, start=1):
            self.assertEqual(gate["id"], f"RG-{index:02d}")
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             reference.BOARD_ROW_PROJECTION)
        self.assertEqual(gates, self.contract["release_gates"])

    def test_required_artifacts_have_one_verified_source(self) -> None:
        artifacts = self.report["required_artifacts"]
        self.assertEqual(len(artifacts), 6)
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        self.assertFalse(artifacts[0]["blocked"])
        self.assertEqual(artifacts[0]["revision"],
                         reference.SOURCE_REVISION)
        for artifact in artifacts[1:]:
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])
        self.assertEqual(artifacts, self.contract["required_artifacts"])

    def test_exact_blockers_are_open(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 5)
        artifact_ids = {row["id"] for row in self.report["required_artifacts"]}
        gate_ids = {row["id"] for row in self.report["gates"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(blocker["required_action"])
            for gate in blocker["linked_gates"]:
                self.assertIn(gate, gate_ids)
        self.assertEqual(blockers, self.contract["exact_blockers"])

    def test_qualification_has_no_true_result(self) -> None:
        qualification = self.report["qualification"]
        self.assertTrue(qualification["all_release_gates_blocked"])
        self.assertTrue(qualification["source_present"])
        for key in ("weights_present", "runtime_present", "real_result_present",
                    "quality_result", "identity_similarity_result",
                    "naturalness_result", "listening_result",
                    "alignment_result", "first_output_or_tail_result",
                    "device_timing_result", "benchmark_result",
                    "release_claim", "missing_result_promoted"):
            self.assertFalse(qualification[key], key)
        self.assertEqual(qualification, self.contract["qualification"])

    def test_boundary_and_scope_claims_are_false(self) -> None:
        for section in ("scope", "boundary"):
            for key, value in self.report[section].items():
                if key in ("task_local_only", "source_present"):
                    self.assertTrue(value, key)
                else:
                    self.assertFalse(value, key)

    def test_public_geometry_preserved(self) -> None:
        geometry = self.report["public_v0_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertEqual(geometry["model_native_sample_rate_hz"], 24000)
        self.assertFalse(geometry["provider_created"])
        self.assertFalse(geometry["sdk_callback_invoked"])

    def test_absence_summary_blocks_shipping(self) -> None:
        summary = self.report["absence_evidence"]["summary"]
        self.assertEqual(summary["probe_count"], 26)
        self.assertEqual(summary["workspace_probe_count"], 22)
        self.assertEqual(summary["home_probe_count"], 4)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        for key in ("download_attempted", "network_used",
                    "recursive_workspace_walk", "source_or_runtime_imported",
                    "weights_loaded", "model_executed", "audio_read"):
            self.assertFalse(summary[key], key)
        media = self.report["absence_evidence"]["observed_media"]
        self.assertTrue(media["byte_hash_only"])
        for key in ("decoded", "signal_loaded", "audio_read",
                    "listening_performed", "used_for_evidence"):
            self.assertFalse(media[key], key)
        cache = self.report["absence_evidence"]["observed_hf_cache"]
        self.assertFalse(cache["weights_present"])
        self.assertFalse(cache["repository_directory_present"])

    def test_admission_summary_has_no_qualifying_result(self) -> None:
        admission = self.report["admission"]
        self.assertEqual(admission["summary"]["case_count"], 158)
        self.assertEqual(admission["summary"]["rejected_count"], 158)
        self.assertEqual(admission["summary"]["qualifying_results"], 0)
        self.assertEqual(admission["control"]["evidence_class"],
                         "synthetic_schema_control_not_evidence")
        self.assertFalse(admission["control"]["qualifies"])

    def test_voice_profile_is_blocked(self) -> None:
        voice = self.report["voice_profile"]
        self.assertEqual(voice["status"], "blocked")
        self.assertEqual(len(voice["rows"]), 8)
        for row in voice["rows"]:
            self.assertEqual(row["status"], "blocked")
        for key in ("content_preserved", "identity_similarity_measured",
                    "naturalness_measured", "alignment_measured",
                    "first_output_or_tail_measured",
                    "exact_target_condition_qualified", "consent_cleared",
                    "reference_availability_cleared", "output_use_cleared"):
            self.assertFalse(voice[key], key)

    def test_quality_and_timing_are_blocked(self) -> None:
        quality = self.report["quality_outcomes"]
        self.assertEqual(quality["status"], "blocked")
        self.assertEqual(len(quality["rows"]), 3)
        for row in quality["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
        timing = self.report["timing"]
        self.assertEqual(timing["status"], "blocked")
        self.assertEqual(len(timing["rows"]), 3)
        for row in timing["rows"]:
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
        self.assertFalse(execution["identity_similarity_measured"])
        self.assertFalse(execution["naturalness_measured"])
        self.assertFalse(execution["manual_transcript_present"])
        self.assertFalse(execution["listening_performed"])
        self.assertFalse(execution["device_timing_present"])
        self.assertFalse(execution["multi_utterance_present"])
        self.assertFalse(execution["target_voice_provenance_confirmed"])
        self.assertEqual(execution["file_rtf_decimal"],
                         "2.6309517518584022")

    def test_linked_row_identity_excludes_mutable_fields(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["mutable_fields_excluded"],
                         ["status", "owner", "claim", "review", "handoff",
                          "blocked_reason", "dispatch_priority"])
        self.assertEqual(identity["projection"],
                         reference.BOARD_ROW_PROJECTION)
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(
                             reference.BOARD_ROW_PROJECTION))

    def test_contract_digest_matches_report(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_report_has_no_floats(self) -> None:
        reference._no_floats(self.report)
        text = reference.canonical_text(self.report)
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)

    def test_report_canonical_regeneration_is_byte_identical(self) -> None:
        first = reference.canonical_report(self.report)
        second = reference.canonical_report(self.report)
        self.assertEqual(first, second)
        self.assertEqual(first[1],
                         hashlib.sha256(first[0].encode("utf-8")).hexdigest())

    def test_profile_phrases_are_exact(self) -> None:
        path = (reference.AUDIO_ROOT / "audio-benchmark-platform/plan/swarm/"
                "VERIFICATION.md")
        rows = [line for line in path.read_text(encoding="utf-8").splitlines()
                if line.startswith("| Voice |")]
        self.assertEqual(len(rows), 1)
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, rows[0])

    def test_pinned_sources_and_boundary_exist(self) -> None:
        for relative in reference.SOURCE_PINS:
            self.assertTrue((reference.AUDIO_ROOT / relative).is_file(),
                            relative)
        for relative in reference.BOUNDARY_PINS:
            self.assertTrue((reference.WORKTREE / relative).is_file(),
                            relative)

    def test_no_result_keys_are_claimed(self) -> None:
        required = self.report["required_results"]
        self.assertTrue(required["no_result_qualifies"])
        for key, value in required.items():
            if key != "no_result_qualifies":
                self.assertFalse(value, key)


class PackageArtifactTests(unittest.TestCase):
    def test_python_spdx_headers(self) -> None:
        for name in ("reference.py", "run.py", "verify.py",
                     "test_reference.py"):
            head = "\n".join((HERE / name).read_text(
                encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_LICENSE_LINE, head, name)
            self.assertIn(SPDX_COPYRIGHT_LINE, head, name)

    def test_license_sidecars(self) -> None:
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license",
                     "SOURCES.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_LICENSE_LINE, text, name)
            self.assertIn(SPDX_COPYRIGHT_LINE, text, name)

    def test_no_binary_or_vendored_license_artifacts(self) -> None:
        forbidden = {".wav", ".flac", ".mp3", ".pt", ".safetensors", ".onnx",
                     ".so", ".dylib", ".dll", ".exe", ".bin", ".pyc"}
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertFalse(path.is_symlink(), path.name)
        for name in ("LICENSE", "LICENSE.txt", "COPYING", "NOTICE"):
            self.assertFalse((HERE / name).exists(), name)

    def test_deliverables_exist(self) -> None:
        for name in DELIVERABLES:
            self.assertTrue((HERE / name).is_file(), name)

    def test_report_sidecar_digest_matches_bytes(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")


if __name__ == "__main__":
    unittest.main()
