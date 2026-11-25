# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library tests for the SDK-ATENNUATE-0-1-1 package."""

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

    def test_board_projection_digest_is_deterministic(self) -> None:
        digest = reference.board_row_digest(reference.BOARD_ROW_PROJECTION)
        self.assertEqual(digest,
                         reference.board_row_digest(
                             dict(reference.BOARD_ROW_PROJECTION)))
        self.assertEqual(len(digest), 64)

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


class AbsenceTests(unittest.TestCase):
    def test_fixed_probes_are_all_absent(self) -> None:
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(row["present"] is False for row in rows))
        summary = reference.absence_summary(rows)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["source_or_runtime_imported"])

    def test_present_probe_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "present").write_text("x", encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                reference.absence_probes(root, probes=("present",),
                                         worktree=root)
            self.assertIn("artifact_present_reopen_required", str(caught.exception))

    def test_probe_list_is_fixed_bounded_and_unique(self) -> None:
        self.assertGreaterEqual(len(reference.ABSENCE_PROBES), 15)
        self.assertEqual(len(set(reference.ABSENCE_PROBES)),
                         len(reference.ABSENCE_PROBES))
        self.assertNotIn("**", reference.ABSENCE_PROBES)
        self.assertIn("data/models/atennuate/weights.pt",
                      reference.ABSENCE_PROBES)

    def test_checkpoint_and_runtime_paths_are_absent(self) -> None:
        self.assertFalse((reference.AUDIO_ROOT / reference.CHECKPOINT_PATH)
                         .exists())
        self.assertFalse((reference.AUDIO_ROOT / "data/envs/atennuate")
                         .exists())

    def test_runtime_modules_are_absent_in_the_evidence_interpreter(self) -> None:
        probe = reference.runtime_probe()
        self.assertEqual(probe["modules"], ["attenuate", "torch", "torchaudio"])
        self.assertFalse(probe["any_present"])
        self.assertFalse(probe["imported_or_executed"])
        self.assertTrue(all(value is False
                            for value in probe["present"].values()))


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
        self.assertTrue(result["state_unchanged"])
        controls = reference.admission_controls()["controls"]
        self.assertEqual(len(controls), 1)
        self.assertFalse(controls[0]["qualifies"])
        self.assertEqual(controls[0]["evidence_class"],
                         "synthetic_schema_control_not_evidence")

    def test_path_probe_rejects_missing_artifacts(self) -> None:
        self.assert_rejected(
            reference.validate_manifest(control(), probe_paths=True),
            "probe_missing", "checkpoint.path")

    def test_missing_root_rejected(self) -> None:
        self.assert_rejected(reference.validate_manifest(None,
                                                         probe_paths=False),
                             "manifest_not_object")

    def test_missing_field_rejected(self) -> None:
        document = control()
        del document["checkpoint"]
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "missing_field", "checkpoint")

    def test_unknown_field_rejected(self) -> None:
        document = control()
        document["extra"] = 1
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "unknown_field", "extra")

    def test_wrong_checkpoint_digest_rejected(self) -> None:
        document = control()
        document["checkpoint"]["sha256"] = "0" * 64
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "checkpoint.sha256")

    def test_wrong_checkpoint_bytes_rejected(self) -> None:
        document = control()
        document["checkpoint"]["byte_count"] = reference.CHECKPOINT_BYTES + 1
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "checkpoint.byte_count")

    def test_nonfinite_checkpoint_bytes_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            document = control()
            document["checkpoint"]["byte_count"] = value
            self.assert_rejected(reference.validate_manifest(
                document, probe_paths=False),
                "invalid_value", "checkpoint.byte_count")

    def test_boolean_is_not_an_integer(self) -> None:
        document = control()
        document["checkpoint"]["byte_count"] = True
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "checkpoint.byte_count")

    def test_wrong_runtime_rejected(self) -> None:
        document = control()
        document["runtime"]["package_version"] = "0.1.0"
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "runtime.package_version")

    def test_wrong_wheel_digest_rejected(self) -> None:
        document = control()
        document["runtime"]["wheel_sha256"] = "0" * 64
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "runtime.wheel_sha256")

    def test_wrong_python_and_torch_versions_rejected(self) -> None:
        document = control()
        document["runtime"]["python_version"] = "3.12"
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "runtime.python_version")
        document = control()
        document["runtime"]["torch_version"] = "2.4.1"
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "runtime.torch_version")

    def test_relative_and_traversal_paths_rejected(self) -> None:
        for value, code in (("weights.pt", "invalid_path"),
                            ("/caller/../weights.pt", "invalid_path"),
                            ("/caller/\x00weights.pt", "invalid_path")):
            document = control()
            document["checkpoint"]["path"] = value
            self.assert_rejected(reference.validate_manifest(
                document, probe_paths=False), code, "checkpoint.path")

    def test_rights_rejected_when_unknown(self) -> None:
        document = control()
        document["rights"]["redistribution_decision_reference"] = ""
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value",
                             "rights.redistribution_decision_reference")

    def test_streaming_or_unknown_geometry_rejected(self) -> None:
        for field, value, expected in (
                ("sample_rate_hz", 48000, "invalid_value"),
                ("channels", 2, "invalid_value"),
                ("sample_format", "i16", "invalid_value"),
                ("frame_samples", 320, "invalid_value"),
                ("output_length", "streaming", "invalid_value"),
                ("source_time_mapping", "guessed", "invalid_value"),
                ("delay_compensation_samples", 160, "invalid_value")):
            document = control()
            document["format"][field] = value
            self.assert_rejected(reference.validate_manifest(
                document, probe_paths=False), expected, "format." + field)

    def test_nonfinite_reference_rejected(self) -> None:
        document = control()
        document["reference_output"]["finite"] = False
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value", "reference_output.finite")
        document = control()
        document["reference_output"]["sample_count"] = float("nan")
        self.assert_rejected(reference.validate_manifest(document,
                                                         probe_paths=False),
                             "invalid_value",
                             "reference_output.sample_count")

    def test_admission_matrix_is_rejected_and_frozen(self) -> None:
        matrix = reference.admission_controls()
        cases = matrix["cases"]
        self.assertGreaterEqual(len(cases), 49)
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        for case in cases:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertTrue(case["state_unchanged"], case["id"])
            self.assertFalse(case["qualifies"], case["id"])
            self.assertTrue(case["code"], case["id"])
        kinds = {case["kind"] for case in cases}
        self.assertEqual(kinds, {"manifest", "strict_json"})
        ids = {case["id"] for case in cases}
        for required in ("MISS-01", "INV-13", "INV-14", "INV-41", "PRS-01",
                         "JSON-01", "JSON-02", "JSON-03", "JSON-04"):
            self.assertIn(required, ids)
        for case in cases:
            if case["id"].startswith("JSON-"):
                self.assertTrue(case["message_matches"], case["id"])

    def test_schema_control_digest_mismatch_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "reference.wav"
            path.write_bytes(b"not-a-reference")
            document = control()
            document["checkpoint"]["path"] = str(path)
            document["checkpoint"]["sha256"] = reference.CHECKPOINT_SHA256
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
        self.assertFalse(report["scope"]["weights_read"])

    def test_report_blockers_are_open_and_exact(self) -> None:
        report = reference.build_report()
        self.assertEqual([row["id"] for row in report["exact_blockers"]],
                         ["BLK-01", "BLK-02", "BLK-03", "BLK-04", "BLK-05",
                          "BLK-06"])
        text = " ".join(row["statement"] + " " + row["required_action"]
                        for row in report["exact_blockers"])
        for token in (reference.CHECKPOINT_REVISION,
                      reference.CHECKPOINT_SHA256, "3,414,586",
                      reference.WHEEL_SHA256, "attenuate 0.1.1",
                      "torch 2.5.1", "Apache-2.0", "streaming",
                      "rights-cleared"):
            self.assertIn(token, text)
        for row in report["exact_blockers"]:
            self.assertEqual(row["status"], "open")
            self.assertFalse(row["qualifies"])

    def test_report_absence_summary(self) -> None:
        report = reference.build_report()
        summary = report["absence_evidence"]["summary"]
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertEqual(len(report["absence_evidence"]["probes"]),
                         len(reference.ABSENCE_PROBES))

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
        for field in ("status", "owner", "claim", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertIn(field, identity["mutable_fields_excluded"])
            self.assertNotIn(field, identity["projection"])

    def test_report_contract_digest_matches_committed_contract(self) -> None:
        contract = reference.read_strict_json(HERE / "contract.json")
        report = reference.build_report()
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))


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
               if item["id"] == "aTENNuate-PyPI-0.1.1"]
        self.assertEqual(len(row), 1)
        artifacts = row[0]["artifacts"]
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["path"], reference.CHECKPOINT_PATH)
        self.assertEqual(artifacts[0]["bytes"], reference.CHECKPOINT_BYTES)
        self.assertEqual(artifacts[0]["sha256"], reference.CHECKPOINT_SHA256)
        self.assertEqual(row[0]["model_revision"],
                         reference.CHECKPOINT_REVISION)
        self.assertEqual(row[0]["source_revision"],
                         "attenuate-" + reference.PACKAGE_VERSION)


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
