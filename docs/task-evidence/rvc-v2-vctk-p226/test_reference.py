# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit checks for the RVC v2 VCTK p226 evidence package.

No network, no Torch, no checkpoint, no base weight, no audio and no index is
used. Every check is standard-library only.
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_nan_constant_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":NaN}')

    def test_infinity_constant_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":Infinity}')

    def test_byte_order_mark_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('\ufeff{"a":1}')

    def test_non_object_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict("[1,2]")

    def test_canonical_roundtrip(self) -> None:
        document = {"b": [1, 2], "a": {"z": None, "y": True}}
        text = reference.canonical_text(document)
        self.assertEqual(text, '{"a":{"y":true,"z":null},"b":[1,2]}\n')
        self.assertEqual(reference.loads_strict(text), document)
        self.assertEqual(reference.object_digest(document),
                         hashlib.sha256(text.encode("utf-8")).hexdigest())

    def test_float_rejected_in_canonical_report(self) -> None:
        with self.assertRaises(ValueError):
            reference._no_floats({"a": 1.0})

    def test_bool_is_not_int(self) -> None:
        self.assertFalse(reference._is_int(True))
        self.assertTrue(reference._is_int(1))


class PinTests(unittest.TestCase):
    def test_all_source_pins_verify(self) -> None:
        rows = reference.pin_rows(reference.SOURCE_PINS, reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.SOURCE_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_all_boundary_pins_verify(self) -> None:
        rows = reference.pin_rows(reference.BOUNDARY_PINS, reference.WORKTREE)
        self.assertEqual(len(rows), len(reference.BOUNDARY_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_board_projection_matches_constant(self) -> None:
        projection = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(projection, reference.BOARD_ROW_PROJECTION)
        self.assertEqual(
            projection["depends_on"],
            ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
             "SDK-FND-PROVIDER"])

    def test_board_status_is_not_projected(self) -> None:
        path = reference.AUDIO_ROOT / reference.BOARD_TASK_ROW
        board = reference.read_strict_json(path)
        row = next(item for item in board["tasks"]
                   if item.get("id") == reference.TASK)
        baseline = reference.board_row_digest(
            {field: row.get(field) for field in reference.BOARD_ROW_FIELDS})
        for field, value in (("status", "done"), ("owner", "someone-else"),
                             ("review", {"status": "approved"}),
                             ("blocked_reason", "none")):
            mutated = dict(row, **{field: value})
            digest = reference.board_row_digest(
                {field: mutated.get(field)
                 for field in reference.BOARD_ROW_FIELDS})
            self.assertEqual(digest, baseline, field)
        for field in ("status", "owner", "claim", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertNotIn(field, reference.BOARD_ROW_FIELDS)

    def test_pin_mismatch_raises(self) -> None:
        with self.assertRaises(ValueError):
            reference.pin_rows({"missing.file": "0" * 64},
                               reference.AUDIO_ROOT)


class SourceDeclarationTests(unittest.TestCase):
    def test_pinned_lines(self) -> None:
        for name, block in reference.SOURCE_DECLARATIONS.items():
            lines = (reference.AUDIO_ROOT / block["path"]).read_text(
                encoding="utf-8").splitlines()
            for key, value in block.items():
                if not key.endswith("_line"):
                    continue
                prefix = key[:-5]
                fragment = block.get(prefix + "_fragment")
                if fragment is None:
                    continue
                self.assertIn(fragment, lines[value - 1], name + ":" + prefix)

    def test_declared_geometry(self) -> None:
        geometry = reference.pipeline_geometry()
        self.assertEqual(geometry["declared_source_samples_16k"], 154480)
        self.assertEqual(geometry["declared_source_frames_floor"], 965)
        self.assertEqual(geometry["declared_source_remainder_samples"], 80)
        self.assertEqual(geometry["rmvpe_frame_rate_hz"], 100)
        self.assertEqual(geometry["declared_output_samples_40k"], 385600)
        self.assertEqual(geometry["declared_output_frames"], 2410)
        self.assertFalse(geometry["exact_decoded_sample_counts_asserted"])
        self.assertEqual(geometry["upsample_ratio_decimal"], "2.5")
        self.assertEqual(geometry["pad_samples_16k"], 16000)
        self.assertEqual(geometry["query_samples_16k"], 96000)
        self.assertEqual(geometry["center_samples_16k"], 608000)
        self.assertEqual(geometry["max_samples_16k"], 656000)
        self.assertEqual(geometry["pad_samples_40k"], 40000)
        self.assertFalse(geometry["measured"])
        self.assertFalse(geometry["model_executed"])


class AbsenceTests(unittest.TestCase):
    def test_probe_counts(self) -> None:
        self.assertEqual(len(reference.ABSENCE_PROBES), 26)
        self.assertEqual(len(reference.HOME_ABSENCE_PROBES), 4)
        summary = reference.absence_summary(
            reference.absence_probes(reference.AUDIO_ROOT),
            reference.home_absence_probes())
        self.assertEqual(summary["probe_count"], 30)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])

    def test_present_probe_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            present = Path(temporary) / "present.bin"
            present.write_bytes(b"x")
            with self.assertRaises(ValueError):
                reference.absence_probes(
                    Path(temporary), probes=("present.bin",),
                    worktree=Path(temporary) / "empty")
            with self.assertRaises(ValueError):
                reference.absence_probes(
                    Path(temporary) / "empty", probes=("present.bin",),
                    worktree=Path(temporary))

    def test_observed_incomplete_paths(self) -> None:
        rows = reference.observed_incomplete_paths(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["entry_count"], 0)
        self.assertEqual(rows[1]["entry_count"], 2)
        self.assertFalse(rows[0]["usable_weights_present"])
        self.assertFalse(rows[1]["usable_weights_present"])

    def test_observed_unusable_reference(self) -> None:
        rows = reference.observed_unusable_references(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertFalse(row["eligible_for_target"])
        self.assertFalse(row["decoded"])
        self.assertFalse(row["target_match"])
        self.assertTrue(row["verified"])

    def test_runtime_probe_absent(self) -> None:
        probe = reference.runtime_probe()
        self.assertTrue(probe["all_runtime_modules_absent"])
        self.assertFalse(probe["import_performed"])
        self.assertFalse(probe["weights_loaded"])
        self.assertEqual(set(probe["modules"]),
                         set(reference.RUNTIME_PROBE_MODULES))
        self.assertFalse(any(probe["modules"].values()))


class AssetContractTests(unittest.TestCase):
    def arguments(self, **overrides):
        arguments = dict(version="v2", f0=1, tgt_sr=40000,
                         hubert_hidden_size=768, speaker_count=109,
                         speaker_id=1, speaker_info_present=False,
                         speaker_map_verified=True, hubert_model_present=True,
                         rmvpe_model_present=True, terms_reviewed=True)
        arguments.update(overrides)
        return arguments

    def test_structurally_accepted(self) -> None:
        result = reference.evaluate_asset_contract(**self.arguments())
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"],
                         "structurally_admissible_for_reproducer")
        self.assertFalse(result["qualifies"])
        self.assertFalse(result["weights_loaded"])
        self.assertFalse(result["runtime_invoked"])

    def test_rejections(self) -> None:
        cases = (
            ({"version": "v1"}, "invalid_version"),
            ({"version": "v3"}, "invalid_version"),
            ({"f0": 0}, "invalid_f0"),
            ({"f0": True}, "invalid_f0"),
            ({"tgt_sr": 48000}, "invalid_target_rate"),
            ({"tgt_sr": 40000.0}, "invalid_target_rate"),
            ({"hubert_hidden_size": 256}, "invalid_hubert_dimension"),
            ({"speaker_count": 108}, "invalid_speaker_count"),
            ({"speaker_id": -1}, "speaker_id_out_of_range"),
            ({"speaker_id": 109}, "speaker_id_out_of_range"),
            ({"speaker_id": True}, "speaker_id_out_of_range"),
            ({"speaker_info_present": True}, "unexpected_speaker_info"),
            ({"speaker_map_verified": False}, "unverified_speaker_map"),
            ({"hubert_model_present": False}, "missing_hubert_model"),
            ({"rmvpe_model_present": False}, "missing_rmvpe_model"),
            ({"terms_reviewed": False}, "unreviewed_terms"),
        )
        for override, code in cases:
            result = reference.evaluate_asset_contract(
                **self.arguments(**override))
            self.assertFalse(result["accepted"], override)
            self.assertEqual(result["code"], code, override)
            self.assertFalse(result["qualifies"], override)


class ManifestValidationTests(unittest.TestCase):
    def test_schema_control_accepted(self) -> None:
        result = reference.validate_manifest(
            reference._manifest_control(), probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"], "ok")
        self.assertGreater(result["checks"], 70)

    def test_schema_control_rejected_when_paths_probed(self) -> None:
        result = reference.validate_manifest(
            reference._manifest_control(), probe_paths=True)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], "probe_missing")

    def test_nonfinite_document_rejected(self) -> None:
        document = reference._manifest_control()
        document["outcomes"]["naturalness_mos_decimal"] = float("inf")
        result = reference.validate_manifest(document, probe_paths=False)
        self.assertEqual(result["code"], "nonfinite_value")
        self.assertIn("outcomes.naturalness_mos_decimal", result["field"])

    def test_missing_and_unknown_top_fields(self) -> None:
        document = reference._manifest_control()
        del document["rights"]
        self.assertEqual(reference.validate_manifest(
            document, probe_paths=False)["code"], "missing_field")
        document = reference._manifest_control()
        document["extra"] = 1
        self.assertEqual(reference.validate_manifest(
            document, probe_paths=False)["code"], "unknown_field")

    def test_all_admission_cases_rejected(self) -> None:
        matrix = reference.admission_controls()
        self.assertEqual(matrix["summary"]["case_count"], 100)
        self.assertEqual(matrix["summary"]["rejected_count"], 100)
        self.assertEqual(matrix["summary"]["accepted_schema_controls"], 1)
        self.assertEqual(matrix["summary"]["qualifying_results"], 0)
        for case in matrix["cases"]:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertFalse(case["qualifies"], case["id"])
            self.assertTrue(case["state_unchanged"], case["id"])
            self.assertTrue(case["code"], case["id"])

    def test_all_mutations_produce_rejection_codes(self) -> None:
        codes = {case["id"]: case["code"]
                 for case in reference.admission_controls()["cases"]}
        for expected_id, expected_code in (
                ("A001-schema-missing", "missing_field"),
                ("A002-schema-unknown", "unknown_field"),
                ("A011-revision-wrong", "invalid_value"),
                ("A025-checkpoint-version", "invalid_value"),
                ("A027-checkpoint-f0-bool", "invalid_value"),
                ("A031-speaker-info", "invalid_value"),
                ("A042-asset-path", "invalid_path"),
                ("A047-assets-duplicate", "invalid_value"),
                ("A058-faiss-old", "invalid_value"),
                ("A073-source-duration", "invalid_value"),
                ("A095-claims-qualified", "invalid_value"),
                ("A100-nonfinite-json", "invalid_value")):
            self.assertEqual(codes[expected_id], expected_code, expected_id)

    def test_exact_identity_requirements(self) -> None:
        self.assertEqual(reference.CHECKPOINT_NAME, "Mp226rmvpe.pth")
        self.assertEqual(reference.HUBERT_MODEL_NAME, "pytorch_model.bin")
        self.assertEqual(reference.RMVPE_MODEL_NAME, "rmvpe.pt")
        self.assertEqual(reference.HUBERT_HIDDEN_SIZE, 768)
        self.assertEqual(reference.SPEAKER_COUNT, 109)
        self.assertEqual(reference.SELECTED_SPEAKER_ID, 1)
        self.assertEqual(reference.OUTPUT_SAMPLE_RATE_HZ, 40000)
        self.assertEqual(reference.FEATURE_VERSION, "v2")

    def test_admission_contract_is_metadata_only(self) -> None:
        block = reference.admission_contract_block()
        self.assertEqual(block["scope"],
                         "task_local_reproduction_metadata_only")
        self.assertEqual(block["required_feature_version"], "v2")
        self.assertEqual(block["required_target_rate_hz"], 40000)
        self.assertNotIn("model_executed", block)


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_identity_and_decision(self) -> None:
        reference.validate_contract(self.contract)
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")

    def test_eight_blocked_gates(self) -> None:
        gates = self.contract["release_gates"]
        self.assertEqual(len(gates), 8)
        for index, gate in enumerate(gates, start=1):
            self.assertEqual(gate["id"], f"RG-{index:02d}")
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertEqual(gate["linked_row"],
                             reference.BOARD_ROW_PROJECTION)
            self.assertTrue(gate["reopen_condition"])

    def test_artifacts_and_blockers(self) -> None:
        artifacts = self.contract["required_artifacts"]
        self.assertEqual(len(artifacts), 7)
        self.assertTrue(artifacts[0]["present"])
        self.assertFalse(artifacts[0]["blocked"])
        for artifact in artifacts[1:]:
            self.assertFalse(artifact["present"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])
        blockers = self.contract["exact_blockers"]
        self.assertEqual(len(blockers), 7)
        artifact_ids = {row["id"] for row in artifacts}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)

    def test_voice_quality_timing_rows(self) -> None:
        self.assertEqual(len(self.contract["voice_profile_requirements"]), 8)
        self.assertEqual(len(self.contract["quality_outcomes"]), 3)
        self.assertEqual(len(self.contract["timing_requirements"]), 3)
        for row in self.contract["voice_profile_requirements"]:
            self.assertEqual(row["status"], "blocked")
        for row in self.contract["quality_outcomes"] + \
                self.contract["timing_requirements"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])

    def test_report_is_canonical_and_float_free(self) -> None:
        payload = reference.canonical_bytes(self.report)
        self.assertEqual(payload, reference.canonical_bytes(
            reference.loads_strict(payload.decode("utf-8"))))
        reference._no_floats(self.report)
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(),
                         digest)

    def test_report_copies_contract_blocks(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))
        self.assertEqual(self.report["gates"],
                         self.contract["release_gates"])
        self.assertEqual(self.report["disposition"],
                         self.contract["disposition"])
        self.assertEqual(self.report["qualification"],
                         self.contract["qualification"])
        self.assertEqual(self.report["pipeline_geometry"],
                         reference.pipeline_geometry())
        self.assertEqual(self.report["asset_contract"],
                         self.contract["asset_contract"])

    def test_report_flags(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.report["proposal_only"])
        for key, value in self.report["scope"].items():
            if key in {"task_local_only", "source_present"}:
                self.assertTrue(value, key)
            else:
                self.assertFalse(value, key)
        for key, value in self.report["boundary"].items():
            if key in {"task_local_only", "source_present"}:
                self.assertTrue(value, key)
            else:
                self.assertFalse(value, key)

    def test_absence_and_runtime(self) -> None:
        summary = self.report["absence_evidence"]["summary"]
        self.assertEqual(summary["probe_count"], 30)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertTrue(self.report["runtime_probe"]
                        ["all_runtime_modules_absent"])

    def test_admission_report(self) -> None:
        admission = self.report["admission"]
        self.assertEqual(admission["summary"]["case_count"], 100)
        self.assertEqual(admission["summary"]["rejected_count"], 100)
        self.assertEqual(admission["summary"]["accepted_schema_controls"], 1)
        self.assertTrue(admission["control"]["accepted"])
        self.assertFalse(admission["control"]["qualifies"])
        self.assertEqual(len(admission["cases"]), 100)

    def test_historical(self) -> None:
        execution = self.report["historical_execution"]
        self.assertTrue(execution["not_rerun"])
        self.assertFalse(execution["qualifies"])
        self.assertFalse(execution["checkpoint_present"])
        self.assertFalse(execution["hubert_base_present"])
        self.assertFalse(execution["rmvpe_base_present"])
        self.assertFalse(execution["speaker_map_verified"])
        self.assertEqual(execution["output_sha256"], reference.OUTPUT_SHA256)

    def test_linked_row_identity(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(
                             reference.BOARD_ROW_PROJECTION))

    def test_sources_manifest(self) -> None:
        text = run.sources_bytes().decode("ascii")
        lines = [line for line in text.splitlines()
                 if line and not line.startswith("#")]
        self.assertEqual(len(lines),
                         len(reference.SOURCE_PINS) +
                         len(reference.BOUNDARY_PINS) +
                         len(run.LOCAL_PIN_FILES))
        for relative in reference.SOURCE_PINS:
            self.assertIn("  source:" + relative, text)
        self.assertNotIn("TASKS.json", text)

    def test_committed_report_matches_regeneration(self) -> None:
        payload = reference.canonical_bytes(self.report)
        report_path = HERE / "report.json"
        sidecar = HERE / "report.json.sha256"
        if report_path.is_file():
            self.assertEqual(report_path.read_bytes(), payload)
        if sidecar.is_file():
            self.assertEqual(
                sidecar.read_text(encoding="ascii"),
                f"{hashlib.sha256(payload).hexdigest()}  report.json\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
