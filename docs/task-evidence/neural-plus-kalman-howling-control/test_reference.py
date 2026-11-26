# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance and scope regression tests for the hybrid readiness package."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

SPDX_LICENSE = "SPDX-License-" + "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"


class ProfileAndPinTests(unittest.TestCase):
    def test_profile_is_dsp_and_plan_note_matches(self) -> None:
        profile = reference.profile_source()
        self.assertEqual(profile["profile"], "DSP")
        self.assertEqual(profile["key"], "dsp")
        self.assertEqual(profile["plan_note"], reference.PLAN_NOTE)
        self.assertTrue(profile["row"].startswith("| DSP |"))

    def test_source_pins_are_live(self) -> None:
        for relative, expected in reference.SOURCE_PINS.items():
            self.assertEqual(
                reference.sha256_file(reference.SOURCE_ROOT / relative),
                expected, relative)

    def test_boundary_pins_are_live(self) -> None:
        for relative, expected in reference.BOUNDARY_PINS.items():
            self.assertEqual(
                reference.sha256_file(reference.WORKTREE / relative),
                expected, relative)

    def test_boundary_pins_include_merged_sibling_evidence(self) -> None:
        for name in (
                "docs/task-evidence/fixed-feedback-gain-margin/report.json",
                "docs/task-evidence/kalman-afc/report.json",
                "docs/task-evidence/afc-spex/report.json",
                "docs/task-evidence/adaptive-notch-with-gain-margin/"
                "report.json"):
            self.assertIn(name, reference.BOUNDARY_PINS)

    def test_mutable_board_fields_never_enter_identity(self) -> None:
        projection = reference.board_row_projection()
        self.assertEqual(set(projection), set(reference.STABLE_TASK_FIELDS))
        for field in reference.MUTABLE_FIELDS_EXCLUDED:
            self.assertNotIn(field, projection)
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["component"], reference.COMPONENT_ID)

    def test_linked_rows_are_stable_and_unique(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual(len(rows), 1 + len(reference.DEPENDS_ON))
        self.assertEqual(rows[0]["id"], reference.TASK)
        self.assertEqual([row["id"] for row in rows[1:]],
                         list(reference.DEPENDS_ON))
        self.assertRegex(reference.linked_rows_digest(rows), r"^[0-9a-f]{64}$")


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            reference.loads_strict('{"a":1,"a":2}')

    def test_nonfinite_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaisesRegex(ValueError, "nonfinite_json"):
                reference.loads_strict('{"a":' + token + "}")

    def test_float_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "float_not_allowed"):
            reference.loads_strict('{"a":1.5}')

    def test_root_must_be_object(self) -> None:
        with self.assertRaisesRegex(ValueError, "json_root_not_object"):
            reference.loads_strict("[]")

    def test_canonical_text_is_sorted_compact_ascii(self) -> None:
        self.assertEqual(
            reference.canonical_text({"b": 1, "a": [2, 3]}),
            '{"a":[2,3],"b":1}')

    def test_strictness_controls_fail_closed(self) -> None:
        controls = reference.strictness_controls()
        self.assertEqual(controls["json_rejected"], controls["json_cases"])
        self.assertEqual(controls["pin_rejected"], controls["pin_cases"])
        self.assertEqual(controls["readme_rejected"],
                         controls["readme_cases"])
        self.assertTrue(controls["all_adverse_parsers_rejected"])


class AdmissionTests(unittest.TestCase):
    def test_structurally_valid_bundle_is_still_deferred(self) -> None:
        admission = reference.admit_bundle(reference._base_bundle())
        self.assertEqual(admission["status"],
                         "deferred_required_artifacts_absent")
        self.assertFalse(admission["qualifies"])
        self.assertEqual(admission["present_artifacts"], [])
        self.assertFalse(admission["checkpoint_opened"])
        self.assertFalse(admission["runtime_invoked"])
        self.assertFalse(admission["audio_read"])
        self.assertFalse(admission["inference_performed"])

    def test_valid_bundle_requires_held_out_paths_and_terms(self) -> None:
        validated = reference.validate_bundle(reference._base_bundle())
        self.assertEqual(validated["held_out_paths"], 4)
        self.assertEqual(validated["path_split"],
                         "held_out_physical_paths")
        self.assertEqual(validated["update_order"],
                         reference.UPDATE_ORDER)
        self.assertEqual(validated["checkpoint_sha256"], "1" * 64)

    def test_admission_cases_all_fail_closed(self) -> None:
        cases = reference.admission_controls()["cases"]
        self.assertEqual(len(cases), 19)
        self.assertEqual(cases[0]["id"], "CASE-01")
        self.assertTrue(cases[0]["accepted_by_schema"])
        for case in cases:
            self.assertFalse(case["qualifies"], case["id"])
            self.assertFalse(case["state_advanced"], case["id"])
            self.assertFalse(case["runtime_invoked"], case["id"])
            self.assertFalse(case["checkpoint_opened"], case["id"])
            self.assertFalse(case["audio_read"], case["id"])

    def test_required_adverse_codes_present(self) -> None:
        cases = reference.admission_controls()["cases"]
        codes = {case["code"] for case in cases}
        for code in (
                "invalid_json", "duplicate_json_key", "nonfinite_json",
                "unsafe_path_revision", "invalid_algorithm",
                "invalid_update_order", "invalid_algorithm_geometry",
                "invalid_algorithm_type", "invalid_checkpoint",
                "checkpoint_terms_unrecorded", "invalid_fixture_geometry",
                "fixture_class_not_matched", "held_out_paths_missing",
                "rights_not_cleared", "unknown_field", "invalid_runtime",
                "invalid_comparison"):
            self.assertIn(code, codes)

    def test_synthetic_proxy_is_not_admitted(self) -> None:
        bundle = reference._base_bundle()
        bundle = copy.deepcopy(bundle)
        bundle["fixture"]["class"] = "synthetic_proxy"
        with self.assertRaisesRegex(ValueError, "fixture_class_not_matched"):
            reference.validate_bundle(bundle)

    def test_nonfinite_checkpoint_byte_count_rejected(self) -> None:
        bundle = copy.deepcopy(reference._base_bundle())
        bundle["checkpoint"]["byte_count"] = 0
        with self.assertRaisesRegex(ValueError, "invalid_checkpoint"):
            reference.validate_bundle(bundle)

    def test_float_parameter_rejected(self) -> None:
        bundle = copy.deepcopy(reference._base_bundle())
        bundle["algorithm"]["forgetting_micro"] = 0.99
        with self.assertRaisesRegex(ValueError, "invalid_algorithm_type"):
            reference.validate_bundle(bundle)

    def test_unknown_field_rejected(self) -> None:
        bundle = copy.deepcopy(reference._base_bundle())
        bundle["checkpoint"]["url"] = "https://example.invalid"
        with self.assertRaisesRegex(ValueError, "unknown_field"):
            reference.validate_bundle(bundle)

    def test_wrong_rate_and_channels_rejected(self) -> None:
        for key, value in (("sample_rate_hz", 48000), ("channels", 2),
                           ("frame_samples", 512)):
            bundle = copy.deepcopy(reference._base_bundle())
            bundle["fixture"][key] = value
            with self.assertRaisesRegex(ValueError,
                                        "invalid_fixture_geometry"):
                reference.validate_bundle(bundle)


class ReportTests(unittest.TestCase):
    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_report(reference.build_report())
        second = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)
        self.assertRegex(first[1], r"^[0-9a-f]{64}$")

    def test_contract_and_report_decisions(self) -> None:
        contract = reference.build_contract()
        report = reference.build_report()
        reference.validate_contract(contract)
        for value in (contract, report):
            self.assertEqual(value["decision"], "DEFER")
            self.assertEqual(value["status"],
                             "proposal_only_not_qualified")
            self.assertEqual(value["evidence_status"], "incomplete")
            self.assertEqual(value["qualification_status"],
                             "not_qualified")
            self.assertTrue(value["proposal_only"])
            self.assertTrue(value["incomplete"])
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))

    def test_eight_gates_blocked(self) -> None:
        gates = reference.build_report()["gates"]
        self.assertEqual(tuple(row["id"] for row in gates),
                         reference.GATE_IDS)
        self.assertEqual(len(gates), 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"], reference._gate_link())

    def test_artifacts_and_blockers_are_absent(self) -> None:
        report = reference.build_report()
        self.assertEqual(tuple(row["id"] for row in
                               report["required_artifacts"]),
                         reference.ARTIFACT_IDS)
        self.assertEqual(tuple(row["id"] for row in
                               report["exact_blockers"]),
                         reference.BLOCKER_IDS)
        artifact_ids = {row["id"] for row in report["required_artifacts"]}
        for artifact in report["required_artifacts"]:
            self.assertFalse(artifact["present"])
            self.assertFalse(artifact["verified"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])
        for blocker in report["exact_blockers"]:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)

    def test_no_result_qualifies_anywhere(self) -> None:
        report = reference.build_report()

        def walk(value: object) -> None:
            if isinstance(value, dict):
                if "qualifies" in value:
                    self.assertFalse(value["qualifies"])
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(report)
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)

    def test_probes_are_blocked_and_absent(self) -> None:
        report = reference.build_report()
        for key in ("source_probe", "algorithm_probe", "checkpoint_probe",
                    "fixture_probe", "runtime_probe", "rights_probe"):
            self.assertTrue(report[key]["status"].startswith("blocked"), key)
        self.assertFalse(report["source_probe"]["executed"])
        self.assertIsNone(report["checkpoint_probe"]["admitted_model"])
        self.assertFalse(report["checkpoint_probe"]["opened_or_loaded"])
        self.assertFalse(report["fixture_probe"]["read"])
        self.assertFalse(report["runtime_probe"]["imported_or_executed"])
        self.assertEqual(report["rights_probe"]["review"], "blocked")
        self.assertEqual(report["absence_evidence"]["summary"][
            "present_count"], 0)
        self.assertTrue(report["absence_evidence"]["summary"][
            "all_probes_absent"])

    def test_report_never_hashes_whole_board(self) -> None:
        report = reference.build_report()
        self.assertFalse(report["task_row_identity"]["whole_file_hashed"])
        self.assertFalse(report["linked_row_identity"]["board_file_pinned"])
        text = reference.canonical_text(report)
        self.assertNotIn('"plan/swarm/TASKS.json":"' + "0" * 64, text)
        self.assertNotIn(reference.BOARD_TASK_ROW + '":"', text)
        for key in reference.allowed_pin_keys():
            self.assertNotIn(reference.BOARD_TASK_ROW, key)

    def test_historical_evidence_is_not_inherited(self) -> None:
        historical = reference.historical_pilot_match()
        self.assertFalse(historical["neural_kalman_result_row_present"])
        self.assertFalse(historical["matched_execution"])
        self.assertFalse(historical["admitted_as_result"])
        self.assertFalse(historical["inherited_metrics"])
        literature = historical["source_reported_literature"]
        self.assertFalse(literature["admitted_as_result"])
        self.assertFalse(literature["reproduced_here"])
        self.assertFalse(literature["comparable_here"])
        for row in historical["controller_rows"]:
            self.assertNotIn("neural", row.lower())

    def test_stimulus_is_harness_only(self) -> None:
        stimulus = reference.stimulus_probe()
        self.assertFalse(stimulus["candidate_processing"])
        self.assertTrue(stimulus["identity_control"]["bit_exact"])
        self.assertEqual(
            stimulus["closed_loop_proxy"]["status"],
            "blocked_no_fixture_and_no_candidate_output")
        self.assertFalse(stimulus["ablation_comparison"][
            "fixed_margin_equal_gain_compared"])

    def test_report_has_no_float(self) -> None:
        reference.assert_no_float(reference.build_report())

    def test_committed_report_matches_generation_when_present(self) -> None:
        path = HERE / "report.json"
        if not path.is_file():
            self.skipTest("report.json not generated yet")
        report = reference.read_strict_json(path)
        self.assertEqual(path.read_bytes(),
                         reference.canonical_bytes(report))
        self.assertEqual(report, reference.build_report())


class LicensingAndScopeTests(unittest.TestCase):
    def test_python_files_have_spdx_headers(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(
                path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_LICENSE, head, path.name)
            self.assertIn(SPDX_COPYRIGHT, head, path.name)

    def test_markdown_files_have_spdx_headers(self) -> None:
        for name in ("README.md", "LICENSES.md"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_LICENSE, text, name)
            self.assertIn(SPDX_COPYRIGHT, text, name)

    def test_no_forbidden_artifacts_or_symlinks(self) -> None:
        forbidden = {
            ".wav", ".flac", ".pt", ".pth", ".onnx", ".safetensors", ".so",
            ".dylib", ".dll", ".a", ".o", ".bin", ".weights", ".pyc",
        }
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name,
                             {"CMakeLists.txt", "provider.json",
                              "adapter.json", "LICENSE", "COPYING", "NOTICE"})

    def test_readme_tables_verify_when_generated(self) -> None:
        readme = HERE / "README.md"
        text = readme.read_text(encoding="utf-8")
        if "| Path | SHA-256 | Bytes |" not in text:
            self.skipTest("artifact table not generated yet")
        counts = reference.verify_readme_digests(text)
        self.assertGreater(counts["source"], 0)
        self.assertGreater(counts["boundary"], 0)
        self.assertGreater(counts["artifacts"], 0)

    def test_sidecars_are_spdx_licensed(self) -> None:
        for name in reference.LOCAL_PIN_FILES:
            if not name.endswith(".license"):
                continue
            path = HERE / name
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            self.assertIn(SPDX_LICENSE, text, name)
            self.assertIn(SPDX_COPYRIGHT, text, name)

    def test_scope_is_task_local(self) -> None:
        self.assertEqual(reference.TASK_PREFIX,
                         "docs/task-evidence/"
                         "neural-plus-kalman-howling-control/")
        report = reference.build_report()
        self.assertTrue(report["scope"]["task_local_evidence_only"])
        for key, value in report["scope"].items():
            if key != "task_local_evidence_only":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
