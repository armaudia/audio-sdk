# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit checks for the RVC FAISS retrieval evidence package.

No network, no FAISS, no Torch, no audio, no checkpoint and no index is used.
Every check is standard-library only.
"""

from __future__ import annotations

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
            reference.loads_strict('[1,2]')

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
            ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"])

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
        self.assertNotIn("status", reference.BOARD_ROW_FIELDS)
        self.assertNotIn("owner", reference.BOARD_ROW_FIELDS)
        self.assertNotIn("claim", reference.BOARD_ROW_FIELDS)

    def test_pin_mismatch_raises(self) -> None:
        with self.assertRaises(ValueError):
            reference.pin_rows({"missing.file": "0" * 64},
                               reference.AUDIO_ROOT)


class SourceFactTests(unittest.TestCase):
    FACTS = (
        ("research/voice-conversion-eval-20261101/repos/rvc/infer/vc/"
         "pipeline.py", 186, "score, ix = index.search(npy, k=8)"),
        ("research/voice-conversion-eval-20261101/repos/rvc/infer/vc/"
         "pipeline.py", 187, "np.square(1 / score)"),
        ("research/voice-conversion-eval-20261101/repos/rvc/infer/rtrvc.py",
         253, "score, ix = self.index.search(npy, k=8)"),
        ("research/voice-conversion-eval-20261101/repos/rvc/train/"
         "train_index.py", 209, "index = faiss.index_factory("),
        ("research/voice-conversion-eval-20261101/repos/rvc/infer/cli.py",
         141, "if index_rate == 0:"),
    )

    def test_pinned_lines(self) -> None:
        for relative, line_number, fragment in self.FACTS:
            lines = (reference.AUDIO_ROOT / relative).read_text(
                encoding="utf-8").splitlines()
            self.assertIn(fragment, lines[line_number - 1], relative)

    def test_search_call_is_unique(self) -> None:
        pipeline = (reference.AUDIO_ROOT /
                    "research/voice-conversion-eval-20261101/repos/rvc/"
                    "infer/vc/pipeline.py").read_text(encoding="utf-8")
        self.assertEqual(pipeline.count("index.search(npy, k=8)"), 1)

    def test_isolation_constants(self) -> None:
        offline = reference.RETRIEVAL_ISOLATION["offline_path"]
        self.assertEqual(offline["search_k"], 8)
        self.assertEqual(offline["search_line"], 186)
        self.assertEqual(offline["search_exception_handling"],
                         "none_at_call_site")
        crash = reference.RETRIEVAL_ISOLATION["crash_observation"]
        self.assertFalse(crash["reproduced"])
        self.assertEqual(crash["root_cause"], "unlocalized")
        self.assertFalse(crash["original_traceback_retained"])


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

    def test_runtime_probe_absent(self) -> None:
        probe = reference.runtime_probe()
        self.assertTrue(probe["all_runtime_modules_absent"])
        self.assertFalse(probe["import_performed"])
        self.assertEqual(set(probe["modules"]),
                         set(reference.RUNTIME_PROBE_MODULES))
        self.assertFalse(any(probe["modules"].values()))


class QueryContractTests(unittest.TestCase):
    def arguments(self, **overrides):
        arguments = dict(index_rate=0.5, dimension=768, frame_count=950,
                         dtype="float32", all_finite=True, index_dimension=768,
                         ntotal=4096, nlist=1161, nprobe=1)
        arguments.update(overrides)
        return arguments

    def test_zero_rate_is_control(self) -> None:
        result = reference.evaluate_query_contract(
            **self.arguments(index_rate=0.0))
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"], "control_skipped")
        self.assertFalse(result["retrieval_attempted"])
        self.assertFalse(result["qualifies"])

    def test_retrieval_accepted(self) -> None:
        result = reference.evaluate_query_contract(**self.arguments())
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"], "accepted_for_reproducer")
        self.assertTrue(result["retrieval_attempted"])
        self.assertEqual(result["search_k"], 8)

    def test_rejections(self) -> None:
        cases = (
            ({"index_rate": float("nan")}, "invalid_index_rate"),
            ({"index_rate": -0.1}, "invalid_index_rate"),
            ({"index_rate": 1.1}, "invalid_index_rate"),
            ({"index_dimension": 256}, "dimension_mismatch"),
            ({"dimension": 512}, "invalid_dimension"),
            ({"frame_count": 0}, "frame_count_out_of_range"),
            ({"frame_count": True}, "frame_count_out_of_range"),
            ({"dtype": "float64"}, "invalid_dtype"),
            ({"all_finite": False}, "nonfinite_query"),
            ({"nprobe": 0}, "nprobe_out_of_range"),
            ({"nprobe": 1162}, "nprobe_out_of_range"),
            ({"nlist": 5000}, "nlist_exceeds_ntotal"),
            ({"search_k": 4}, "invalid_search_k"),
        )
        for override, code in cases:
            result = reference.evaluate_query_contract(
                **self.arguments(**override))
            self.assertFalse(result["accepted"], override)
            self.assertEqual(result["code"], code, override)
            self.assertFalse(result["retrieval_attempted"], override)


class ManifestValidationTests(unittest.TestCase):
    def test_schema_control_accepted(self) -> None:
        result = reference.validate_manifest(
            reference._manifest_control(), probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"], "ok")
        self.assertGreater(result["checks"], 80)

    def test_schema_control_rejected_when_paths_probed(self) -> None:
        result = reference.validate_manifest(
            reference._manifest_control(), probe_paths=True)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], "probe_missing")

    def test_nonfinite_document_rejected(self) -> None:
        document = reference._manifest_control()
        document["index"]["ntotal"] = float("inf")
        result = reference.validate_manifest(document, probe_paths=False)
        self.assertEqual(result["code"], "nonfinite_value")
        self.assertIn("index.ntotal", result["field"])

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
        self.assertEqual(matrix["summary"]["case_count"], 120)
        self.assertEqual(matrix["summary"]["rejected_count"], 120)
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
                ("A026-speaker-info", "invalid_value"),
                ("A038-index-dimension", "invalid_value"),
                ("A044-index-read-text", "invalid_value"),
                ("A053-faiss-old", "invalid_value"),
                ("A075-all-finite", "invalid_value"),
                ("A086-native-exit-mismatch", "invalid_value"),
                ("A090-native-result-sha", "invalid_value"),
                ("A104-control-paired", "invalid_value"),
                ("A114-exit-code-float", "invalid_value")):
            self.assertEqual(codes[expected_id], expected_code, expected_id)

    def test_exact_identity_requirements(self) -> None:
        self.assertEqual(reference.CHECKPOINT_NAME, "Mp226rmvpe.pth")
        self.assertEqual(reference.INDEX_NAME,
                         "added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index")
        self.assertEqual(reference.INDEX_DIMENSION, 768)
        self.assertEqual(reference.INDEX_NLIST, 1161)
        self.assertEqual(reference.INDEX_NPROBE, 1)
        self.assertEqual(reference.INDEX_SPEAKERS, 109)
        self.assertEqual(reference.SEARCH_K, 8)

    def test_admission_contract_is_metadata_only(self) -> None:
        block = reference.admission_contract_block()
        self.assertEqual(block["scope"],
                         "task_local_retrieval_reproducer_metadata_only")
        self.assertEqual(block["required_index_type"], "IndexIVFFlat")
        self.assertEqual(block["required_search_k"], 8)
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
        self.assertEqual(self.report["retrieval_isolation"],
                         reference.RETRIEVAL_ISOLATION)
        self.assertEqual(self.report["failure_and_control"],
                         reference.FAILURE_AND_CONTROL)

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
        self.assertEqual(admission["summary"]["case_count"], 120)
        self.assertEqual(admission["summary"]["rejected_count"], 120)
        self.assertEqual(admission["summary"]["accepted_schema_controls"], 1)
        self.assertTrue(admission["control"]["accepted"])
        self.assertFalse(admission["control"]["qualifies"])
        self.assertEqual(len(admission["cases"]), 120)

    def test_historical_and_failure_control(self) -> None:
        execution = self.report["historical_execution"]
        self.assertTrue(execution["not_rerun"])
        self.assertFalse(execution["qualifies"])
        self.assertFalse(execution["crash_reproduced"])
        self.assertTrue(execution["retrieval_crash_observed"])
        failure = self.report["failure_and_control"]["failure"]
        control = self.report["failure_and_control"]["control"]
        self.assertEqual(failure["status"], "not_reproduced")
        self.assertEqual(failure["root_cause"], "unlocalized")
        self.assertFalse(failure["qualifies"])
        self.assertFalse(control["paired_with_failure"])
        self.assertEqual(control["status"], "unpaired_historical_control")
        self.assertFalse(control["qualifies"])

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
