# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library tests for SDK-FASTENHANCER-SMALL-REFERENCE."""

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

    def test_nonfinite_rejected(self) -> None:
        for text, code in (
                ('{"a":NaN}', "nonfinite_json_constant:NaN"),
                ('{"a":Infinity}', "nonfinite_json_constant:Infinity"),
                ('{"a":-Infinity}', "nonfinite_json_constant:-Infinity")):
            with self.assertRaises(ValueError) as caught:
                reference.loads_strict(text)
            self.assertEqual(str(caught.exception), code)

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


class BoardIdentityTests(unittest.TestCase):
    def test_board_row_projection_matches_stable_identity(self) -> None:
        board = reference.AUDIO_ROOT / reference.BOARD_TASK_ROW
        self.assertTrue(board.is_file(), "shared board task row is missing")
        self.assertEqual(reference.board_row_projection(board),
                         reference.BOARD_ROW_PROJECTION)

    def test_board_projection_contains_only_stable_fields(self) -> None:
        self.assertEqual(set(reference.BOARD_ROW_PROJECTION),
                         set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(set(reference.BOARD_ROW_PROJECTION),
                         {"id", "title", "component", "mode", "repository",
                          "depends_on"})

    def test_board_file_is_not_pinned(self) -> None:
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)

    def test_linked_rows_are_stable_identity_only(self) -> None:
        self.assertEqual(len(reference.LINKED_ROWS), 5)
        for row in reference.LINKED_ROWS:
            self.assertEqual(set(row), set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(reference.linked_rows_digest(),
                         reference.linked_rows_digest(
                             tuple(dict(row) for row in reference.LINKED_ROWS)))

    def test_linked_dependencies_match_the_task_row(self) -> None:
        self.assertEqual(reference.BOARD_ROW_PROJECTION["depends_on"],
                         ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-NN",
                          "SDK-FND-PROVIDER"])


class SourceTests(unittest.TestCase):
    def test_pinned_source_checkout_is_present_and_verified(self) -> None:
        probe = reference.source_probe()
        self.assertEqual(probe["status"], "present_pinned")
        self.assertTrue(probe["present"])
        self.assertEqual(probe["revision"], reference.SOURCE_REVISION)
        self.assertEqual(probe["tree_digest"], reference.SOURCE_TREE_DIGEST)
        self.assertEqual(probe["file_count"], reference.SOURCE_FILE_COUNT)
        self.assertEqual(probe["license"], "MIT")
        self.assertEqual(probe["license_sha256"],
                         reference.SOURCE_LICENSE_SHA256)
        self.assertFalse(probe["executed"])

    def test_missing_source_is_reported_not_invented(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            probe = reference.source_probe(Path(temporary))
        self.assertEqual(probe["status"], "source_absent")
        self.assertFalse(probe["present"])


class WeightsTests(unittest.TestCase):
    def test_exact_16khz_small_graph_is_absent(self) -> None:
        probe = reference.weights_probe()
        self.assertEqual(probe["status"],
                         "blocked_exact_pinned_model_absent")
        self.assertFalse(probe["pinned_model_present"])
        self.assertIsNone(probe["admitted_model"])
        exact = [row for row in probe["candidates"]
                 if row["path"] == reference.MODEL_PATH][0]
        self.assertFalse(exact["present"])
        self.assertFalse(exact["admitted"])

    def test_local_small_candidate_is_not_admitted(self) -> None:
        probe = reference.weights_probe()
        row = [item for item in probe["candidates"]
               if item["path"] == "cpp-library/.deps/fastenhancer_s.onnx"][0]
        self.assertTrue(row["present"])
        self.assertEqual(
            row["sha256"],
            "f04ece2beed330da367264c54cedded62f65a117fbde5c005d3a88fc796d0ba3")
        self.assertEqual(row["byte_count"], 875885)
        self.assertFalse(row["matches_pinned_exact"])
        self.assertFalse(row["admitted"])
        self.assertEqual(row["graph_metadata"]["producer"], "pytorch")
        self.assertEqual(row["graph_metadata"]["wav_in_shape"], [1, 512])
        self.assertEqual(row["variant_hint"],
                         "shape_consistent_with_48khz_512_sample_chunk")
        self.assertFalse(row["loaded_into_runtime"])
        self.assertFalse(row["inference_performed"])

    def test_local_tiny_16khz_is_not_the_small_component(self) -> None:
        probe = reference.weights_probe()
        row = [item for item in probe["candidates"]
               if item["path"] ==
               "cpp-library/.deps/fastenhancer_t_16k.onnx"][0]
        self.assertTrue(row["present"])
        self.assertEqual(
            row["sha256"],
            "a64663672b31bd1445502ee23328d291af13fb312e11bb574c010e7261a5ee7d")
        self.assertFalse(row["matches_pinned_exact"])
        self.assertFalse(row["admitted"])
        self.assertEqual(row["admission_reason"],
                         "different_model_size_tiny_not_small")

    def test_onnx_summary_rejects_malformed_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.onnx"
            path.write_bytes(b"\x0a\xff")
            summary = reference.onnx_summary(path)
        self.assertFalse(summary["parsed"])
        self.assertEqual(summary["reason"], "malformed_onnx_protobuf")


class RuntimeTests(unittest.TestCase):
    def test_pinned_runtime_module_is_absent(self) -> None:
        probe = reference.runtime_probe()
        self.assertEqual(probe["status"], "blocked_pinned_runtime_absent")
        self.assertFalse(probe["modules"]["onnxruntime"])
        self.assertFalse(probe["pinned_runtime_present"])
        self.assertFalse(probe["pinned_runtime_version_verified"])
        self.assertFalse(probe["pinned_runtime_complete"])
        self.assertFalse(probe["imported_or_executed"])
        self.assertEqual(probe["pinned_environment_paths_found"], [])

    def test_local_cpp_runtime_is_present_but_not_admitted(self) -> None:
        probe = reference.runtime_probe()
        local = probe["local_cpp_runtime"]
        self.assertIsNotNone(local)
        self.assertEqual(local["version"], "1.31.1")
        self.assertEqual(local["git_commit"],
                         "41d4d61f14b9c1dd0b2ccda1e9b85dd415fd0496")
        self.assertFalse(local["pinned_python_runtime_match"])
        self.assertFalse(local["admitted"])
        self.assertFalse(local["imported_or_executed"])
        archive = probe["local_runtime_archive"]
        self.assertIsNotNone(archive)
        self.assertEqual(archive["byte_count"], 36_936_435)
        self.assertFalse(archive["opened"])
        self.assertFalse(archive["admitted"])


class AbsenceTests(unittest.TestCase):
    def test_fixed_probes_are_all_absent(self) -> None:
        rows = reference.absence_probes()
        self.assertEqual(len(rows), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(row["present"] is False for row in rows))
        summary = reference.absence_summary(rows)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["source_or_runtime_imported"])

    def test_present_probe_is_reported_not_hidden(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "present").write_text("x", encoding="utf-8")
            rows = reference.absence_probes(root, probes=("present",),
                                            worktree=root)
        self.assertTrue(rows[0]["present"])
        self.assertFalse(reference.absence_summary(rows)["all_probes_absent"])

    def test_probe_list_is_fixed_bounded_and_unique(self) -> None:
        self.assertGreaterEqual(len(reference.ABSENCE_PROBES), 8)
        self.assertEqual(len(set(reference.ABSENCE_PROBES)),
                         len(reference.ABSENCE_PROBES))
        self.assertNotIn("**", reference.ABSENCE_PROBES)
        self.assertIn(reference.MODEL_PATH, reference.ABSENCE_PROBES)


class FramePlanTests(unittest.TestCase):
    def test_declared_adapter_arithmetic(self) -> None:
        plan = reference.frame_plan(1600)
        self.assertEqual(plan["calls"], 8)
        self.assertEqual(plan["padded_input_samples"], 2112)
        self.assertEqual(plan["consumed_samples"], 2048)
        self.assertEqual(plan["leading_samples_discarded"], 256)
        self.assertEqual(plan["output_samples"], 1600)
        self.assertEqual(plan["output_length"], "identity")
        self.assertFalse(plan["measured"])

    def test_single_chunk_is_two_calls(self) -> None:
        self.assertEqual(reference.frame_plan(256)["calls"], 2)

    def test_invalid_sample_counts_rejected(self) -> None:
        for value in (0, -1, True, 1.5, "1600",
                      reference.MAX_FRAME_SAMPLE_COUNT + 1):
            with self.assertRaises(ValueError):
                reference.frame_plan(value)


class AdmissionTests(unittest.TestCase):
    def assert_rejected(self, result: dict, code: str, field: str = "") -> None:
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], code)
        if field:
            self.assertEqual(result["field"], field)
        self.assertTrue(result["state_unchanged"])

    def test_schema_control_is_accepted_without_qualifying(self) -> None:
        result = reference.validate_manifest(control(), probe_paths=False)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["code"], "ok")
        self.assertGreater(result["checks"], 0)
        controls = reference.admission_controls()["controls"]
        self.assertEqual(len(controls), 1)
        self.assertFalse(controls[0]["qualifies"])
        self.assertEqual(controls[0]["evidence_class"],
                         "synthetic_schema_control_not_evidence")

    def test_path_probe_rejects_missing_artifacts(self) -> None:
        self.assert_rejected(
            reference.validate_manifest(control(), probe_paths=True),
            "probe_missing", "model.path")

    def test_missing_root_rejected(self) -> None:
        self.assert_rejected(reference.validate_manifest(None,
                                                         probe_paths=False),
                             "manifest_not_object")

    def test_missing_and_unknown_fields_rejected(self) -> None:
        document = control()
        del document["model"]
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "missing_field", "model")
        document = control()
        document["extra"] = 1
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "unknown_field", "extra")

    def test_wrong_model_digest_and_bytes_rejected(self) -> None:
        document = control()
        document["model"]["sha256"] = "0" * 64
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "model.sha256")
        document = control()
        document["model"]["byte_count"] = reference.MODEL_BYTES + 1
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "model.byte_count")

    def test_nonfinite_and_boolean_bytes_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf"), True):
            document = control()
            document["model"]["byte_count"] = value
            self.assert_rejected(reference.validate_manifest(
                document, probe_paths=False),
                "invalid_value", "model.byte_count")

    def test_wrong_runtime_rejected(self) -> None:
        for field, value in (
                ("python_version", "3.12"),
                ("onnxruntime_version", "1.21.0"),
                ("onnxruntime_wheel_sha256", "0" * 64),
                ("numpy_version", "2.0.0"),
                ("soundfile_version", "0.12.1")):
            document = control()
            document["runtime"][field] = value
            self.assert_rejected(reference.validate_manifest(
                document, probe_paths=False),
                "invalid_value", "runtime." + field)

    def test_relative_and_traversal_paths_rejected(self) -> None:
        for value in ("fastenhancer_s.onnx",
                      "/caller/../fastenhancer_s.onnx",
                      "/caller/\x00fastenhancer_s.onnx"):
            document = control()
            document["model"]["path"] = value
            self.assert_rejected(reference.validate_manifest(
                document, probe_paths=False), "invalid_path", "model.path")

    def test_unresolved_rights_rejected(self) -> None:
        for value in ("", "unresolved", "unknown", "none"):
            document = control()
            document["rights"]["model_license"] = value
            self.assert_rejected(reference.validate_manifest(
                document, probe_paths=False),
                "invalid_value", "rights.model_license")
        document = control()
        document["rights"]["code_license"] = "Apache-2.0"
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "rights.code_license")

    def test_wrong_geometry_rejected(self) -> None:
        for field, value in (
                ("sample_rate_hz", 48000),
                ("channels", 2),
                ("sample_format", "i16"),
                ("n_fft", 256),
                ("hop_size", 512),
                ("output_length", "streaming"),
                ("source_time_mapping", "guessed"),
                ("delay_compensation_samples", 160)):
            document = control()
            document["format"][field] = value
            self.assert_rejected(reference.validate_manifest(
                document, probe_paths=False), "invalid_value",
                "format." + field)

    def test_nonfinite_reference_rejected(self) -> None:
        document = control()
        document["reference_output"]["finite"] = False
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "reference_output.finite")
        document = control()
        document["reference_output"]["sample_count"] = float("nan")
        self.assert_rejected(reference.validate_manifest(
            document, probe_paths=False),
            "invalid_value", "reference_output.sample_count")

    def test_admission_matrix_is_rejected_and_frozen(self) -> None:
        matrix = reference.admission_controls()
        cases = matrix["cases"]
        self.assertGreaterEqual(len(cases), 55)
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        for case in cases:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertTrue(case["state_unchanged"], case["id"])
            self.assertFalse(case["qualifies"], case["id"])
            self.assertTrue(case["code"], case["id"])
        kinds = {case["kind"] for case in cases}
        self.assertEqual(kinds, {"manifest", "strict_json"})
        ids = {case["id"] for case in cases}
        for required in ("MISS-01", "INV-13", "INV-14", "INV-44", "PRS-01",
                         "JSON-01", "JSON-02", "JSON-03", "JSON-04",
                         "JSON-05", "JSON-06"):
            self.assertIn(required, ids)
        for case in cases:
            if case["id"].startswith("JSON-"):
                self.assertTrue(case["message_matches"], case["id"])

    def test_digest_mismatch_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "reference.wav"
            path.write_bytes(b"not-a-reference")
            document = control()
            document["model"]["path"] = str(path)
            document["model"]["sha256"] = reference.MODEL_SHA256
            result = reference.validate_manifest(document, probe_paths=True)
            self.assertFalse(result["accepted"])
            self.assertEqual(result["code"], "probe_digest_mismatch")


class ContractReportTests(unittest.TestCase):
    def test_contract_is_valid_and_has_eight_blocked_gates(self) -> None:
        contract = reference.build_contract()
        reference.validate_contract(contract)
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertEqual([gate["id"] for gate in contract["release_gates"]],
                         ["RG-01", "RG-02", "RG-03", "RG-04", "RG-05",
                          "RG-06", "RG-07", "RG-08"])
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in contract["release_gates"]))

    def test_contract_disposition_is_defer_incomplete_not_qualified(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "proposal_only_incomplete")
        self.assertEqual(contract["evidence_status"], "incomplete")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertTrue(contract["proposal_only"])
        self.assertTrue(contract["incomplete"])
        self.assertTrue(contract["qualification"]["not_qualified"])
        self.assertFalse(contract["qualification"]["missing_result_promoted"])
        for key, value in contract["boundary"].items():
            if key == "task_local_only":
                self.assertTrue(value)
            else:
                self.assertFalse(value, key)

    def test_report_is_canonical_and_reproducible(self) -> None:
        first_text, first_digest = reference.canonical_report(
            reference.build_report())
        second_text, second_digest = reference.canonical_report(
            reference.build_report())
        self.assertEqual(first_text, second_text)
        self.assertEqual(first_digest, second_digest)
        self.assertTrue(first_text.endswith("\n"))
        self.assertEqual(len(first_digest), 64)

    def test_report_has_eight_blocked_gates(self) -> None:
        report = reference.build_report()
        self.assertEqual(len(report["gates"]), 8)
        self.assertEqual(report["remaining_gates"],
                         ["RG-01", "RG-02", "RG-03", "RG-04", "RG-05",
                          "RG-06", "RG-07", "RG-08"])
        for gate in report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])

    def test_report_qualification_and_disposition(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertTrue(report["incomplete"])
        self.assertEqual(report["qualification"]["status"],
                         "not_qualified")
        self.assertEqual(report["qualification"]["readiness"], "incomplete")
        self.assertFalse(report["qualification"]["missing_result_promoted"])
        self.assertEqual(report["disposition"]["promotion"], "defer")
        self.assertFalse(report["disposition"]["expose_as_processor"])
        self.assertFalse(report["disposition"]["registered"])
        self.assertFalse(report["disposition"]["default_enabled"])

    def test_report_contains_no_float(self) -> None:
        def walk(value):
            if isinstance(value, dict):
                for item in value.values():
                    yield from walk(item)
            elif isinstance(value, list):
                for item in value:
                    yield from walk(item)
            else:
                yield value

        for value in walk(reference.build_report()):
            self.assertNotIsInstance(value, float)

    def test_report_has_no_result_sections(self) -> None:
        report = reference.build_report()
        for key in ("metrics", "scores", "quality", "si_sdr", "stoi",
                    "pesq", "listening_result"):
            self.assertNotIn(key, report)
        self.assertFalse(report["scope"]["quality_scored"])
        self.assertFalse(report["scope"]["denoising_performed"])
        self.assertFalse(report["scope"]["pinned_weights_read"])
        self.assertFalse(report["scope"]["inference_performed"])

    def test_report_blockers_are_open_and_exact(self) -> None:
        report = reference.build_report()
        self.assertEqual([row["id"] for row in report["exact_blockers"]],
                         ["BLK-01", "BLK-02", "BLK-03", "BLK-04", "BLK-05",
                          "BLK-06"])
        text = " ".join(row["statement"] + " " + row["required_action"]
                        for row in report["exact_blockers"])
        for token in (reference.SOURCE_REVISION, reference.MODEL_SHA256,
                      "832,813", reference.PINNED_ONNXRUNTIME_WHEEL_SHA256,
                      "onnxruntime 1.20.1", "MIT", "not specified separately",
                      "rights-cleared", "256-sample"):
            self.assertIn(token, text)
        for row in report["exact_blockers"]:
            self.assertEqual(row["status"], "open")
            self.assertFalse(row["qualifies"])

    def test_report_pin_rows_are_verified(self) -> None:
        report = reference.build_report()
        self.assertEqual(set(report["source_pins"]),
                         set(reference.SOURCE_PINS))
        self.assertEqual(set(report["boundary_pins"]),
                         set(reference.BOUNDARY_PINS))
        for row in report["source_pins"].values():
            self.assertTrue(row["verified"])
        for row in report["boundary_pins"].values():
            self.assertTrue(row["verified"])

    def test_linked_row_identity_excludes_mutable_fields(self) -> None:
        identity = reference.linked_row_identity()
        self.assertEqual(identity["projection"],
                         reference.BOARD_ROW_PROJECTION)
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        for field in ("status", "owner", "history", "claim", "review",
                      "handoff", "blocked_reason", "dispatch_priority"):
            self.assertIn(field, identity["mutable_fields_excluded"])
            self.assertNotIn(field, identity["projection"])

    def test_report_contract_digest_matches_committed_contract(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        report = reference.build_report()
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))

    def test_historical_values_are_strings_and_not_qualified(self) -> None:
        report = reference.build_report()
        evidence = report["historical_evidence"]
        self.assertEqual(evidence["status"],
                         "historical_research_not_reproduced_not_qualified")
        self.assertFalse(evidence["qualifies"])
        for entry in evidence["entries"]:
            for value in entry["values"]:
                self.assertIsInstance(value, str)


class ProfileTests(unittest.TestCase):
    def test_profile_phrases_are_exact(self) -> None:
        source = (reference.AUDIO_ROOT
                  / "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
        text = source.read_text(encoding="utf-8")
        rows = [line for line in text.splitlines()
                if line.startswith("| Enhancement |")]
        self.assertEqual(len(rows), 1)
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, rows[0])

    def test_enhancement_rows_are_all_blocked(self) -> None:
        report = reference.build_report()
        profile = report["enhancement_profile"]
        self.assertEqual(profile["status"], "blocked")
        self.assertEqual([row["id"] for row in profile["rows"]],
                         ["ENH-01", "ENH-02", "ENH-03", "ENH-04", "ENH-05",
                          "ENH-06"])
        for row in profile["rows"]:
            self.assertEqual(row["status"], "blocked")
        for key, value in profile.items():
            if key in ("profile", "rows", "status"):
                continue
            self.assertFalse(value, key)


class PinnedInputTests(unittest.TestCase):
    def test_pinned_sources_and_boundary_exist(self) -> None:
        for relative, digest in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest, relative)
        for relative, digest in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest, relative)

    def test_candidate_pins_match_the_ledger(self) -> None:
        ledger = json.loads((reference.AUDIO_ROOT /
                             "research/noise_suppression_assets_20261027.json")
                            .read_text(encoding="utf-8"))
        row = [item for item in ledger["candidates"]
               if item["id"] == "FastEnhancer-DNS-16k-Tiny+Small"]
        self.assertEqual(len(row), 1)
        small = [artifact for artifact in row[0]["artifacts"]
                 if artifact["path"] == reference.MODEL_PATH]
        self.assertEqual(len(small), 1)
        self.assertEqual(small[0]["bytes"], reference.MODEL_BYTES)
        self.assertEqual(small[0]["sha256"], reference.MODEL_SHA256)
        self.assertEqual(row[0]["source_revision"],
                         reference.SOURCE_REVISION)


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
        forbidden = {
            ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib", ".m4a",
            ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus", ".pcap",
            ".pcapng", ".pt", ".pth", ".so", ".wav", ".weights",
        }
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertNotIn(path.name, {"LICENSE", "LICENSE.txt", "COPYING",
                                         "NOTICE"})
            self.assertFalse(path.is_symlink(), path.name)

    def test_deliverables_exist(self) -> None:
        expected = {
            "README.md", "LICENSES.md", "contract.json", "reference.py",
            "report.json", "report.json.sha256", "SOURCES.sha256", "run.py",
            "test_reference.py", "verify.py", "SOURCES.sha256.license",
            "contract.json.license", "report.json.license",
            "report.json.sha256.license",
        }
        present = {path.name for path in HERE.iterdir() if path.is_file()}
        self.assertTrue(expected <= present, expected - present)

    def test_report_sidecar_matches_bytes(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")


if __name__ == "__main__":
    unittest.main()
