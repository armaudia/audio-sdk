# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for the deterministic MLX/MPS/Core ML evidence package.

The tests never download a runtime, import an accelerator package, load a
model, compile a Core ML model, read audio or measure a device. They exercise
strict JSON, stable board identity, fixed absence probes, the fail-closed
accelerator-execution admission schema and the canonical report.
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

SPDX_HEADER = "SPDX-License-" + "Identifier: Apache-2.0"
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib", ".m4a",
    ".mlmodel", ".mlpackage", ".mlmodelc", ".model", ".mp3", ".mp4", ".o",
    ".onnx", ".opus", ".pcap", ".pcapng", ".pt", ".pth", ".pyc",
    ".safetensors", ".so", ".wasm", ".wav", ".weights",
}
DELIVERABLES = (
    "LICENSES.md",
    "README.md",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a": 1, "a": 2}')

    def test_nonfinite_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                reference.loads_strict('{"value": ' + token + "}")

    def test_float_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.assert_no_float({"value": 1.5})
        with self.assertRaises(ValueError):
            reference.assert_no_float([{"nested": [2.0]}])

    def test_non_object_root_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict("[1, 2]")

    def test_canonical_bytes_are_stable(self) -> None:
        value = {"b": [2, 1], "a": "x"}
        first = reference.canonical_bytes(value)
        second = reference.canonical_bytes(copy.deepcopy(value))
        self.assertEqual(first, second)
        self.assertEqual(first, b'{"a":"x","b":[2,1]}')


class BoardIdentityTests(unittest.TestCase):
    def _write(self, document: dict) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json",
                                             delete=False, encoding="utf-8")
        json.dump(document, handle)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def _row(self) -> dict:
        return {
            "id": reference.TASK,
            "title": reference.TASK_TITLE,
            "component": reference.COMPONENT_ID,
            "mode": reference.MODE,
            "repository": reference.REPOSITORY,
            "depends_on": list(reference.DEPENDS_ON),
            "status": "in_progress",
            "owner": "agent-MLX-MPS-CORE-ML-EXECUTION",
            "claim": {"base_commit": reference.BASE_COMMIT},
            "review": None,
            "handoff": None,
            "dispatch_priority": 3,
        }

    def test_mutable_fields_do_not_change_projection(self) -> None:
        row = self._row()
        before = reference.board_row_projection(self._write({"tasks": [row]}))
        row.update({"status": "done", "owner": "someone-else",
                    "claim": {"base_commit": "0" * 40},
                    "review": {"state": "approved"}, "handoff": {"x": 1},
                    "dispatch_priority": 1})
        after = reference.board_row_projection(self._write({"tasks": [row]}))
        self.assertEqual(before, after)
        self.assertEqual(before["id"], reference.TASK)
        self.assertEqual(before["mode"], "feasibility")

    def test_stable_identity_change_changes_projection(self) -> None:
        row = self._row()
        before = reference.board_row_projection(self._write({"tasks": [row]}))
        row["title"] = "Different title"
        after = reference.board_row_projection(self._write({"tasks": [row]}))
        self.assertNotEqual(before["title"], after["title"])

    def test_mutable_board_not_pinned(self) -> None:
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)

    def test_mode_drift_rejected(self) -> None:
        row = self._row()
        row["mode"] = "implementation"
        with self.assertRaises(ValueError):
            reference.board_row_projection(self._write({"tasks": [row]}))

    def test_component_mismatch_rejected(self) -> None:
        row = self._row()
        row["component"] = "not-this-component"
        with self.assertRaises(ValueError):
            reference.board_row_projection(self._write({"tasks": [row]}))

    def test_duplicate_root_row_rejected(self) -> None:
        row = self._row()
        with self.assertRaises(ValueError):
            reference.board_row_projection(
                self._write({"tasks": [row, dict(row)]}))

    def test_linked_rows_include_dependencies(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual(rows[0]["id"], reference.TASK)
        self.assertEqual([row["id"] for row in rows[1:]],
                         list(reference.DEPENDS_ON))
        self.assertEqual(reference.linked_rows_digest(),
                         reference.object_digest([dict(row) for row in rows]))


class AbsenceTests(unittest.TestCase):
    def test_all_three_accelerators_blocked(self) -> None:
        probe = reference.runtime_probe()
        self.assertEqual(probe["status"],
                         "blocked_pinned_runtimes_absent")
        self.assertEqual(probe["required_runtime_count"], 3)
        self.assertEqual(probe["admitted_runtime_count"], 0)
        self.assertIs(probe["any_runtime_admitted"], False)
        self.assertIs(probe["imported_or_executed"], False)
        self.assertIs(probe["device_timing_measured"], False)
        self.assertEqual([row["runtime_id"] for row in probe["accelerators"]],
                         list(reference.RUNTIME_IDS))
        for row in probe["accelerators"]:
            self.assertIs(row["admitted"], False)
            self.assertIs(row["pinned_install_present"], False)
            self.assertIs(row["executed"] if "executed" in row else False,
                          False)
            self.assertIs(row["version_verified"], False)
            self.assertIs(row["lock_present"], False)
            self.assertIs(row["license_verified"], False)
            self.assertIs(row["device_timing_measured"], False)
            self.assertEqual(row["status"], "blocked_exact_runtime_absent")

    def test_host_observation_is_not_admission(self) -> None:
        host = reference.host_observation()
        self.assertIs(host["observation_is_admission"], False)
        self.assertIs(host["metal_device_query_executed"], False)
        self.assertIs(host["device_timing_measured"], False)
        self.assertIs(host["network_used"], False)
        self.assertIn(host["coreml_toolchain_observation"],
                      ("observed_not_admitted", "not_observed"))

    def test_absence_summary_zero(self) -> None:
        probes = reference.absence_probes()
        summary = reference.absence_summary(probes)
        self.assertGreater(len(probes), 0)
        self.assertEqual(summary["admitted_count"], 0)
        self.assertIs(summary["all_admitted_absent"], True)
        self.assertIs(summary["recursive_workspace_walk"], False)
        self.assertIs(summary["download_attempted"], False)
        self.assertIs(summary["runtime_imported_or_executed"], False)
        self.assertIs(summary["model_loaded"], False)

    def test_every_candidate_is_absent(self) -> None:
        for row in reference.absence_probes():
            self.assertIs(row["present"], False)
            self.assertIs(row["admitted"], False)


class ManifestTests(unittest.TestCase):
    def test_control_accepted_but_not_qualified(self) -> None:
        result = reference.validate_manifest(reference._manifest_control())
        self.assertEqual(result["status"], "accepted")
        self.assertIs(result["qualifies"], False)
        self.assertIs(result["synthetic_control"], True)
        self.assertEqual(result["runtime_id"], "mlx")
        self.assertGreater(result["checks"], 0)

    def test_control_does_not_match_real_upstream(self) -> None:
        control = reference._manifest_control()
        self.assertNotIn(control["runtime"]["revision"],
                         (reference.BASE_COMMIT,))
        self.assertTrue(control["runtime"]["provenance_url"].startswith(
            "https://example.invalid/"))

    def test_missing_required_field(self) -> None:
        manifest = reference._manifest_control()
        manifest.pop("runtime")
        result = reference.validate_manifest(manifest)
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["code"], "missing_field")

    def test_unknown_field(self) -> None:
        manifest = reference._manifest_control()
        manifest["provider"] = "x"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "unknown_field")

    def test_invalid_payload_type(self) -> None:
        result = reference.validate_manifest(["not", "an", "object"])
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["code"], "manifest_not_object")

    def test_invalid_revision_and_sha(self) -> None:
        manifest = reference._manifest_control()
        manifest["runtime"]["revision"] = "short"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "invalid_revision")
        manifest = reference._manifest_control()
        manifest["runtime"]["install_sha256"] = "xyz"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "invalid_sha256")

    def test_invalid_runtime_and_version(self) -> None:
        manifest = reference._manifest_control()
        manifest["runtime"]["runtime_id"] = "metal"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "invalid_runtime_id")
        manifest = reference._manifest_control()
        manifest["runtime"]["version"] = ">=1.0"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "invalid_version")

    def test_unsafe_paths_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["runtime"]["install_path"] = "/opt/mlx"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "unsafe_path")
        manifest = reference._manifest_control()
        manifest["model"]["files"][0]["path"] = "../model.safetensors"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "unsafe_path")

    def test_accelerator_unavailable_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["host"]["accelerator_available"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "accelerator_unavailable")

    def test_parity_not_exact_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["parity"]["exact_match"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "parity_not_exact")

    def test_availability_not_measured_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["availability"]["measured"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "availability_not_measured")

    def test_false_control_and_rights_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["controls"]["malformed_inputs"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "control_not_verified")
        manifest = reference._manifest_control()
        manifest["rights"]["output_use"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "rights_not_cleared")

    def test_unresolved_and_empty_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["model"]["model_id"] = "tbd"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "unresolved_value")
        manifest = reference._manifest_control()
        manifest["host"]["metal_version"] = ""
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "empty_text")

    def test_duplicate_and_unsorted_files_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["model"]["files"].append(
            dict(manifest["model"]["files"][0]))
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "duplicate_value")
        manifest = reference._manifest_control()
        manifest["model"]["files"] = [
            {"path": "z.safetensors", "sha256": "d" * 64, "bytes": 1},
            {"path": "a.safetensors", "sha256": "d" * 64, "bytes": 1},
        ]
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "noncanonical_order")

    def test_float_and_nonfinite_raw_cases(self) -> None:
        manifest = reference._manifest_control()
        manifest["parity"]["tolerance"] = 1.5
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "float_not_allowed")
        with self.assertRaises(ValueError) as duplicate:
            reference.loads_strict('{"a": 1, "a": 2}')
        self.assertIn("duplicate_json_key", str(duplicate.exception))
        with self.assertRaises(ValueError) as nonfinite:
            reference.loads_strict('{"a": NaN}')
        self.assertIn("nonfinite_json", str(nonfinite.exception))

    def test_all_admission_cases(self) -> None:
        block = reference.admission_controls()
        cases = block["cases"]
        accepted = [case for case in cases if case["status"] == "accepted"]
        rejected = [case for case in cases if case["status"] == "rejected"]
        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0]["id"], "accepted-schema-control")
        self.assertIs(accepted[0]["qualifies"], False)
        self.assertGreaterEqual(len(rejected), 25)
        for case in rejected:
            self.assertIs(case["qualifies"], False)
            self.assertIs(case["state_unchanged"], True)
            self.assertTrue(case["code"])
        codes = {case["code"] for case in rejected}
        for expected in (
                "manifest_not_object", "missing_field", "unknown_field",
                "schema_mismatch", "invalid_runtime_id", "invalid_version",
                "invalid_revision", "invalid_sha256", "unsafe_path",
                "invalid_url", "invalid_arch", "accelerator_unavailable",
                "invalid_boolean", "empty_text", "unresolved_value",
                "parity_not_exact", "out_of_range", "invalid_integer",
                "availability_not_measured", "control_not_verified",
                "rights_not_cleared", "duplicate_value", "noncanonical_order",
                "duplicate_json_key", "nonfinite_json", "invalid_json",
                "json_root_not_object", "float_not_allowed"):
            self.assertIn(expected, codes)
        summary = block["summary"]
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertIs(summary["accepted_control_qualifies"], False)
        self.assertIs(summary["runtime_invoked"], False)
        self.assertIs(summary["model_loaded"], False)
        self.assertIs(summary["audio_read"], False)
        self.assertIs(summary["device_timing_measured"], False)
        self.assertIs(summary["all_adverse_cases_rejected"], True)


class ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = reference.build_contract()

    def test_contract_semantics(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "proposal_only_incomplete")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertIs(self.contract["proposal_only"], True)
        self.assertIs(self.contract["incomplete"], True)
        self.assertIs(self.contract["board_file_pinned"], False)
        self.assertEqual(self.contract["branch"], reference.BRANCH)
        self.assertEqual(self.contract["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.contract["profile"], "tool")
        reference.validate_contract(self.contract)

    def test_eight_blocked_gates(self) -> None:
        gates = self.contract["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([row["id"] for row in gates],
                         ["RG-0" + str(i) for i in range(1, 9)])
        for row in gates:
            self.assertEqual(row["status"], "blocked")
            self.assertIs(row["qualifies"], False)
            self.assertTrue(row["reopen_condition"])
            self.assertEqual(row["linked_row"], reference._gate_link())

    def test_open_blockers_and_blocked_artifacts(self) -> None:
        blockers = self.contract["exact_blockers"]
        artifacts = self.contract["required_artifacts"]
        self.assertEqual(len(blockers), len(reference.EXACT_BLOCKERS))
        self.assertEqual(len(artifacts), len(reference.REQUIRED_ARTIFACTS))
        artifact_ids = {row["id"] for row in artifacts}
        for row in blockers:
            self.assertEqual(row["status"], "open")
            self.assertIs(row["qualifies"], False)
            self.assertIn(row["artifact_id"], artifact_ids)
            self.assertTrue(row["linked_gates"])
        for row in artifacts:
            self.assertIs(row["present"], False)
            self.assertIs(row["verified"], False)
            self.assertIs(row["blocked"], True)
            self.assertIsNone(row["sha256"])

    def test_tool_profile_blocked(self) -> None:
        profile = self.contract["tool_profile"]
        self.assertEqual(profile["profile"], "Tool")
        self.assertEqual(profile["status"], "blocked")
        self.assertIs(profile["qualifies"], False)
        self.assertEqual(len(profile["rows"]), len(reference.TOOL_REQUIREMENTS))
        for row in profile["rows"]:
            self.assertEqual(row["status"], "blocked")
        for key, value in profile.items():
            if key in ("profile", "rows", "status", "qualifies",
                       "cross_runtime_pooling_prohibited"):
                continue
            self.assertIs(value, False, key)
        self.assertIs(profile["cross_runtime_pooling_prohibited"], True)

    def test_upstream_record_has_no_claimed_digest(self) -> None:
        upstream = self.contract["upstream_record"]
        self.assertIs(upstream["runtime_pinned"], False)
        self.assertIsNone(upstream["runtime_lock_sha256"])
        self.assertIsNone(upstream["pinned_model_sha256"])
        self.assertIs(upstream["model_present"], False)
        self.assertIs(upstream["executed"], False)
        self.assertIs(upstream["digest_asserted"], False)
        self.assertIs(upstream["rights_cleared"], False)
        self.assertIs(upstream["reproduced_here"], False)
        self.assertIs(upstream["evidence_is_adjacent_adapter_only"], True)

    def test_boundary_all_false_except_task_local(self) -> None:
        boundary = self.contract["boundary"]
        for key, value in boundary.items():
            if key == "task_local_only":
                self.assertIs(value, True)
            else:
                self.assertIs(value, False, key)

    def test_exact_scope_is_three_runtimes(self) -> None:
        scope = self.contract["exact_scope"]
        self.assertEqual(scope["runtimes"], ["mlx", "mps", "coreml"])
        self.assertEqual(scope["runtime_count"], 3)
        self.assertIs(scope["separate_runtime_reporting_required"], True)
        self.assertIs(scope["cpu_parity_required_per_runtime"], True)
        self.assertIs(scope["availability_required_per_runtime"], True)
        self.assertIs(scope["pooled_runtime_result_permitted"], False)
        self.assertIs(scope["os_framework_observation_is_admission"], False)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_no_floats(self) -> None:
        reference.assert_no_float(self.report)

    def test_decision_status_and_qualification(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertIs(self.report["proposal_only"], True)
        self.assertIs(self.report["incomplete"], True)
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["readiness"], "incomplete")
        self.assertIs(qualification["all_release_gates_blocked"], True)
        self.assertEqual(qualification["admitted_runtime_count"], 0)
        self.assertEqual(qualification["qualifying_results"], 0)
        self.assertIs(qualification["missing_result_qualifies"], False)

    def test_runtime_probe_and_absence(self) -> None:
        self.assertEqual(self.report["runtime_probe"],
                         reference.runtime_probe())
        summary = self.report["absence_evidence"]["summary"]
        self.assertEqual(summary["admitted_count"], 0)
        self.assertIs(summary["all_admitted_absent"], True)
        self.assertIs(summary["download_attempted"], False)

    def test_runtime_geometry_blocks_all_claims(self) -> None:
        geometry = self.report["geometry"]
        for key in ("runtime_identity_pinned", "model_present",
                    "runtime_present", "executed", "version_pinned",
                    "device_timing_measured", "workload_support_measured",
                    "cpu_parity_measured", "installed_v0",
                    "provider_registered"):
            self.assertIs(geometry[key], False, key)
        self.assertIs(geometry["os_framework_observation_is_admission"], False)

    def test_historical_evidence_is_adverse_and_not_admitted(self) -> None:
        historical = self.report["historical_evidence"]
        self.assertEqual(
            historical["status"],
            "sibling_coreml_ep_trial_rejected_no_qualifying_execution")
        self.assertIs(historical["qualifies"], False)
        self.assertIs(historical["no_values_inferred_from_adjacent_tasks"],
                      True)
        entries = historical["entries"]
        self.assertEqual([row["id"] for row in entries],
                         ["HIST-01", "HIST-02", "HIST-03"])
        for row in entries:
            self.assertIs(row["admitted_as_result"], False)
            self.assertIs(row["qualifies"], False)
            self.assertIs(row["paired_cpu_baseline"], False)
        coreml = entries[0]
        self.assertIs(coreml["single_stream_clean"], True)
        self.assertIs(coreml["eight_stream_clean"], False)
        self.assertIs(coreml["sixteen_stream_clean"], False)
        self.assertIs(coreml["concurrent_use_rejected"], True)
        self.assertIs(coreml["reproducible_library_build"], False)
        self.assertEqual(coreml["recorded_failure"],
                         "GetElementType is not implemented")

    def test_peer_evidence_is_not_inherited(self) -> None:
        peers = self.report["peer_evidence"]
        self.assertEqual(peers, [dict(row) for row in
                                 reference.PEER_EVIDENCE])
        for row in peers:
            self.assertIs(row["admitted_as_result"], False)
            self.assertIs(row["inherited_metrics"], False)

    def test_admission_summary(self) -> None:
        summary = self.report["admission"]["summary"]
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertIs(summary["accepted_control_qualifies"], False)
        self.assertIs(summary["state_advanced_on_rejection"], False)

    def test_source_and_boundary_pins_verified(self) -> None:
        for block in ("source_pins", "boundary_pins"):
            for name, row in self.report[block].items():
                self.assertEqual(row["sha256"], row["actual"], name)
                self.assertIs(row["verified"], True, name)

    def test_profile_source_is_tool(self) -> None:
        profile = self.report["profile_source"]
        self.assertEqual(profile["profile"], "Tool")
        self.assertEqual(profile["key"], "tool")
        self.assertTrue(profile["row"].startswith("| Tool |"))
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, profile["row"])

    def test_canonical_report_digest_matches_sidecar(self) -> None:
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(text.encode("ascii"), reference.canonical_bytes(
            self.report))
        self.assertEqual(digest, hashlib.sha256(
            reference.canonical_bytes(self.report)).hexdigest())


class ScopeHelperTests(unittest.TestCase):
    def test_scope_violations(self) -> None:
        prefix = reference.TASK_PREFIX
        self.assertEqual(reference.scope_violations(
            [prefix + "README.md", prefix + "reference.py"]), [])
        self.assertEqual(reference.scope_violations(
            [prefix + "README.md", "CMakeLists.txt"]), ["CMakeLists.txt"])


class PackageBoundaryTests(unittest.TestCase):
    def test_required_deliverables_exist(self) -> None:
        for name in DELIVERABLES:
            self.assertTrue((HERE / name).is_file(), name)

    def test_no_forbidden_artifacts(self) -> None:
        for path in sorted(HERE.iterdir()):
            self.assertNotIn(path.suffix.lower(), FORBIDDEN_SUFFIXES)
            self.assertFalse(path.is_symlink(), path.name)

    def test_python_spdx_headers(self) -> None:
        for name in ("reference.py", "run.py", "test_reference.py",
                     "verify.py"):
            head = "\n".join((HERE / name).read_text(
                encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_HEADER, head, name)

    def test_sidecar_files(self) -> None:
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license",
                     "SOURCES.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_HEADER, text, name)
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          text, name)

    def test_markdown_spdx_headers(self) -> None:
        for name in ("README.md", "LICENSES.md"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_HEADER, text, name)


if __name__ == "__main__":
    unittest.main()
