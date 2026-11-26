# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local tests for SDK-PYROOMACOUSTICS evidence, including scope regressions."""

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


def report() -> dict:
    return reference.build_report()


def contract() -> dict:
    return reference.build_contract()


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a":1,"a":2}')
        self.assertEqual(str(caught.exception), "duplicate_json_key:a")

    def test_nonfinite_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(ValueError):
                    reference.loads_strict('{"a":' + token + "}")

    def test_float_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict('{"a":1.5}')
        self.assertEqual(str(caught.exception), "float_not_allowed")

    def test_non_object_root_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.loads_strict("[1,2]")
        self.assertEqual(str(caught.exception), "json_root_not_object")

    def test_canonical_bytes_are_stable(self) -> None:
        value = {"b": [1, 2], "a": {"d": True, "c": None}}
        self.assertEqual(reference.canonical_bytes(value),
                         b'{"a":{"c":null,"d":true},"b":[1,2]}')
        self.assertEqual(reference.object_digest(value),
                         hashlib.sha256(reference.canonical_bytes(value))
                         .hexdigest())


class PinAndAbsenceTests(unittest.TestCase):
    def test_source_pins_are_current(self) -> None:
        rows = reference.pin_rows(reference.SOURCE_PINS,
                                  reference.AUDIO_ROOT)
        self.assertEqual(len(rows), 10)
        self.assertTrue(all(row["verified"] for row in rows), rows)

    def test_boundary_pins_are_current(self) -> None:
        rows = reference.pin_rows(reference.BOUNDARY_PINS,
                                  reference.WORKTREE)
        self.assertEqual(len(rows), 9)
        self.assertTrue(all(row["verified"] for row in rows), rows)

    def test_all_fixed_probes_absent(self) -> None:
        probes = reference.all_probes()
        self.assertEqual(len(probes), 17)
        self.assertEqual([row["path"] for row in probes
                          if row["present"]], [])
        summary = reference.absence_summary(probes)
        self.assertTrue(summary["all_probes_absent"])
        self.assertEqual(summary["present_count"], 0)
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["candidate_source_imported"])
        self.assertFalse(summary["room_simulation_executed"])

    def test_absence_summary_counts(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["probe_count"], 17)
        self.assertEqual(summary["workspace_probe_count"], 9)
        self.assertEqual(summary["worktree_probe_count"], 5)
        self.assertEqual(summary["home_probe_count"], 3)

    def test_present_probe_would_fail_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "present"
            marker.write_text("x", encoding="utf-8")
            probes = [{"path": str(marker), "present": marker.exists(),
                       "searched_workspace": True,
                       "searched_sdk_worktree": False,
                       "searched_home_cache": False}]
            self.assertEqual(reference.absence_summary(probes)["present_count"],
                             1)
            self.assertFalse(reference.absence_summary(
                probes)["all_probes_absent"])

    def test_evidence_inputs_are_pinned_and_labelled(self) -> None:
        rows = reference.evidence_inputs()
        self.assertEqual(len(rows), len(reference.EVIDENCE_INPUT_PATHS))
        self.assertTrue(any(row["mentions_pyroomacoustics"] for row in rows))
        self.assertTrue(all(row["is_result"] is False for row in rows))
        for row in rows:
            self.assertEqual(row["sha256"],
                             reference.SOURCE_PINS[row["path"]])

    def test_mutable_board_not_pinned(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        self.assertNotIn(reference.BOARD_TASK_ROW, text)
        self.assertNotIn("source:" + reference.BOARD_TASK_ROW, text)

    def test_pin_lines_are_strict(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        rows = reference.parse_pin_lines(text)
        self.assertGreater(len(rows), 20)
        with self.assertRaises(ValueError):
            reference.parse_pin_lines("deadbeef  source:x\n")


class BoardIdentityTests(unittest.TestCase):
    def test_projection_fields(self) -> None:
        projection = reference.board_row_projection()
        self.assertEqual(set(projection), set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["component"], reference.COMPONENT_ID)
        self.assertEqual(projection["mode"], "feasibility")

    def test_linked_rows_cover_task_and_dependencies(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))
        self.assertEqual(rows[0]["component"], reference.COMPONENT_ID)

    def test_mutable_fields_do_not_change_projection(self) -> None:
        document = reference.read_strict_json(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        row = next(item for item in document["tasks"]
                   if item.get("id") == reference.TASK)
        changed = copy.deepcopy(row)
        changed["status"] = "done"
        changed["owner"] = "someone-else"
        changed["review"] = {"decision": "approved"}
        changed["handoff"] = {"closed": True}
        changed["blocked_reason"] = "changed"
        self.assertEqual(reference._project(row, True),
                         reference._project(changed, True))

    def test_stable_identity_change_changes_projection(self) -> None:
        projection = reference.board_row_projection()
        changed = copy.deepcopy(projection)
        changed["title"] = "PyRoomAcoustics changed"
        self.assertNotEqual(reference.board_row_digest(projection),
                            reference.board_row_digest(changed))


class RegistryAndProfileTests(unittest.TestCase):
    def test_three_registry_leads_are_recorded_not_verified(self) -> None:
        value = reference.registry_leads()
        self.assertEqual(value["lead_count"], 3)
        self.assertEqual([row["source_id"] for row in value["leads"]],
                         ["S16", "S24", "S26"])
        self.assertFalse(value["revision_or_license_present"])
        self.assertTrue(all(row["qualifies"] is False
                            for row in value["leads"]))

    def test_registry_categories_remain_not_started(self) -> None:
        registry = reference.read_strict_json(
            reference.AUDIO_ROOT / "research/category_registry.json")
        by_id = {row["id"]: row for row in registry["categories"]}
        for category_id in reference.registry_leads()["category_ids"]:
            self.assertEqual(by_id[category_id]["discovery_status"],
                             "catalogued")
            self.assertEqual(by_id[category_id]["candidate_census_status"],
                             "not_started")
            self.assertEqual(by_id[category_id]["benchmark_status"],
                             "not_started")

    def test_inventory_row_is_considered_tool_candidate(self) -> None:
        row = reference.inventory_row()
        self.assertEqual(row["id"], reference.COMPONENT_ID)
        self.assertEqual(row["evidence_status"], "considered")
        self.assertEqual(row["verification_profile"], "tool")
        self.assertEqual(row["disposition"], "sdk-tool")

    def test_profile_phrases_present_for_all_profiles(self) -> None:
        check = reference.profile_row_check()
        self.assertTrue(check["phrases_all_present"])
        self.assertEqual(set(check["rows"]), {"Tool", "Room", "Spatial"})
        for row in check["rows"].values():
            self.assertEqual(row["row_count"], 1)
            self.assertTrue(row["phrases_present"])

    def test_profile_row_check_fails_on_missing_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "verification.md"
            path.write_text("| Tool | different text |\n", encoding="utf-8")
            original = reference.PROFILE_SOURCE_REL
            reference.PROFILE_SOURCE_REL = str(path)
            try:
                self.assertFalse(reference.profile_row_check()[
                    "phrases_all_present"])
            finally:
                reference.PROFILE_SOURCE_REL = original


class AdmissionTests(unittest.TestCase):
    def test_control_accepted_but_not_qualified(self) -> None:
        result = reference.validate_manifest(reference._manifest_control())
        self.assertEqual(result["status"], "accepted")
        self.assertFalse(result["qualifies"])
        self.assertTrue(result["synthetic_schema_control"])
        self.assertTrue(result["not_real_rir_evidence"])
        self.assertFalse(result["runtime_invoked"])

    def test_every_admission_case_is_accounted(self) -> None:
        admission = reference.admission_controls()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], len(admission["cases"]))
        self.assertEqual(summary["case_count"], 19)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertEqual(summary["rejected_count"], 18)
        self.assertTrue(summary["all_cases_match_expected"])
        self.assertTrue(summary["all_rejected_state_unchanged"])
        for case in admission["cases"]:
            self.assertFalse(case["qualifies"], case["id"])
            if case["status"] == "rejected":
                self.assertTrue(case["state_unchanged"])
                self.assertTrue(case["code"])

    def test_missing_and_unknown_fields(self) -> None:
        manifest = reference._manifest_control()
        manifest.pop("geometry")
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "root_fields")
        manifest = reference._manifest_control()
        manifest["extra"] = True
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "root_fields")

    def test_wrong_interpreter_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["tool"]["interpreter"] = "3.11.5"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "interpreter_mismatch")

    def test_mono_geometry_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["geometry"]["channels"] = 1
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "channels_out_of_range")

    def test_missing_rir_identity_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["evidence"]["rir_sha256"] = None
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "rir_sha256_invalid_text")

    def test_promoted_simulation_claim_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["evidence"]["simulation_not_real_rir_evidence"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "simulation_claim_promoted")

    def test_false_controls_and_rights_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["controls"]["geometry_mismatch_rejection"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "control_false:geometry_mismatch_rejection")
        manifest = reference._manifest_control()
        manifest["rights"]["output_use_permitted"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "rights_unverified:output_use_permitted")

    def test_raw_json_cases_fail_closed(self) -> None:
        for raw, code in (
                ('{"a":1,"a":2}', "duplicate_json_key"),
                ('{"a":NaN}', "nonfinite_json"),
                ('{"a":Infinity}', "nonfinite_json"),
                ('[]', "json_root_not_object")):
            with self.subTest(code=code):
                with self.assertRaises(ValueError) as caught:
                    reference.loads_strict(raw)
                self.assertEqual(str(caught.exception).split(":", 1)[0],
                                 code)

    def test_admission_contract_flags(self) -> None:
        value = reference._admission_contract_block()
        self.assertEqual(value["required_interpreter"], "3.12.16")
        self.assertEqual(value["required_channels_min"], 2)
        self.assertEqual(value["required_sample_rate_hz"], 16000)
        self.assertTrue(value["validation_only"])
        self.assertTrue(value["synthetic_control_is_not_real_rir_evidence"])
        self.assertFalse(value["synthetic_control_qualifies"])


class ContractAndReportTests(unittest.TestCase):
    def test_contract_validates(self) -> None:
        value = contract()
        reference.validate_contract(value)
        self.assertEqual(value["schema_id"], reference.CONTRACT_SCHEMA_ID)
        self.assertEqual(value["qualification"]["evidence_status"],
                         reference.EVIDENCE_STATUS)
        self.assertEqual(value["qualification"]["decision"], "DEFER")
        self.assertEqual(value["qualification"]["qualification_status"],
                         "not_qualified")

    def test_eight_blocked_gates(self) -> None:
        gates = contract()["release_gates"]
        self.assertEqual([row["id"] for row in gates],
                         ["RG-%02d" % index for index in range(1, 9)])
        self.assertTrue(all(row["status"] == "blocked" for row in gates))
        self.assertTrue(all(row["qualifies"] is False for row in gates))
        self.assertTrue(all(row["reopen_condition"] for row in gates))

    def test_six_blockers_link_valid_ids(self) -> None:
        value = contract()
        blockers = value["exact_blockers"]
        artifact_ids = {row["id"] for row in value["required_artifacts"]}
        gate_ids = {row["id"] for row in value["release_gates"]}
        self.assertEqual(len(blockers), 6)
        for row in blockers:
            self.assertEqual(row["status"], "open")
            self.assertFalse(row["qualifies"])
            self.assertIn(row["artifact_id"], artifact_ids)
            self.assertTrue(set(row["linked_gates"]) <= gate_ids)

    def test_eight_artifacts_absent(self) -> None:
        rows = contract()["required_artifacts"]
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertIs(row["present"], False)
            self.assertIs(row["verified"], False)
            self.assertIs(row["blocked"], True)
            self.assertIsNone(row["sha256"])
            self.assertIsNone(row["revision"])
            self.assertIsNone(row["bytes"])

    def test_qualification_has_no_positive_claim(self) -> None:
        value = contract()["qualification"]
        for key, expected in value.items():
            if key in ("decision", "evidence_status", "qualification_status"):
                continue
            if isinstance(expected, bool):
                self.assertEqual(expected, (key in (
                    "all_release_gates_blocked", "recorded_identity_only",
                    "schema_control_only")), key)

    def test_task_geometry_labels_synthetic_control(self) -> None:
        value = reference.task_geometry()
        self.assertEqual(value["channels_min"], 2)
        self.assertEqual(value["sample_rate_hz"], 16000)
        self.assertFalse(value["exact_geometry_verified"])
        self.assertFalse(value["sdk_v0_adapter_mapping_present"])
        self.assertEqual(value["synthetic_control_label"],
                         "synthetic_geometry_control")
        self.assertFalse(value["synthetic_control_is_real_rir_evidence"])

    def test_matched_evidence_does_not_promote_peers(self) -> None:
        value = reference.matched_evidence_boundary()
        self.assertFalse(value["results_promoted"])
        self.assertTrue(value["synthetic_controls_not_real_rir_evidence"])
        self.assertEqual(len(value["adjacent_components"]), 6)

    def test_non_claims_are_present(self) -> None:
        self.assertEqual(len(reference.NON_CLAIMS), 8)
        self.assertEqual(report()["prohibited_claims"],
                         list(reference.NON_CLAIMS))

    def test_report_is_canonical(self) -> None:
        value = report()
        text, digest = reference.canonical_report(value)
        self.assertEqual(text.encode("ascii"),
                         reference.canonical_bytes(value))
        self.assertEqual(digest, hashlib.sha256(
            reference.canonical_bytes(value)).hexdigest())
        reference.assert_no_float(value)

    def test_report_copies_match_contract(self) -> None:
        value = report()
        value_contract = contract()
        self.assertEqual(value["contract_sha256"],
                         reference.object_digest(value_contract))
        for report_key, contract_key in (
                ("disposition", "disposition"), ("boundary", "boundary"),
                ("scope", "scope"), ("exact_scope", "exact_scope"),
                ("public_v0_geometry", "public_v0_geometry"),
                ("task_geometry", "task_geometry"),
                ("upstream_record", "reported_source_leads"),
                ("matched_evidence_boundary", "matched_evidence_boundary"),
                ("required_artifacts", "required_artifacts"),
                ("exact_blockers", "exact_blockers"),
                ("gates", "release_gates"), ("rights_gap", "rights_gap"),
                ("qualification", "qualification")):
            self.assertEqual(value[report_key], value_contract[contract_key],
                             report_key)

    def test_scope_block_has_no_external_change(self) -> None:
        value = reference.scope_block()
        for key, expected in value.items():
            if key in ("task_local_only", "write_prefix"):
                continue
            self.assertIs(expected, False, key)
        self.assertEqual(value["write_prefix"], reference.TASK_PREFIX)


class ScopeTests(unittest.TestCase):
    """Regression coverage for the newest-merge-base scope comparison."""

    def _git(self, repo: Path, *arguments: str) -> str:
        result = subprocess.run(["git", "-C", str(repo), *arguments],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def _repository(self, root: Path) -> Path:
        repo = root / "audio-sdk"
        repo.mkdir()
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.name", "scope-fixture")
        self._git(repo, "config", "user.email", "scope@example.invalid")
        self._git(repo, "config", "commit.gpgsign", "false")
        task = repo / reference.TASK_PREFIX
        task.mkdir(parents=True)
        (task / "README.md").write_text("task", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-q", "-m", "base")
        return repo

    def _commit_task_change(self, repo: Path, label: str) -> None:
        path = repo / reference.TASK_PREFIX / "evidence.txt"
        path.write_text(label, encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-q", "-m", label)

    def test_sibling_merge_excluded_from_newest_merge_base(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            sibling = repo / "docs/task-evidence/laco-senet/README.md"
            sibling.parent.mkdir(parents=True)
            sibling.write_text("sibling", encoding="utf-8")
            self._git(repo, "add", ".")
            self._git(repo, "commit", "-q", "-m", "sibling merge")
            self._git(repo, "checkout", "-q", "-b", "swarm-task")
            self._commit_task_change(repo, "task evidence")
            base = reference.scope_base(repo, ("main",))
            self.assertEqual(base, self._git(repo, "rev-parse", "main"))
            self.assertNotEqual(base, self._git(repo, "rev-parse",
                                                "main~1"))
            self.assertEqual(reference.scope_changed_paths(repo, base),
                             [reference.TASK_PREFIX + "evidence.txt"])
            self.assertEqual(reference.scope_violations(
                reference.scope_changed_paths(repo, base)), [])

    def test_out_of_scope_branch_change_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "checkout", "-q", "-b", "swarm-task")
            self._commit_task_change(repo, "task evidence")
            outside = repo / "docs/task-evidence/other/README.md"
            outside.parent.mkdir(parents=True)
            outside.write_text("outside", encoding="utf-8")
            self._git(repo, "add", ".")
            self._git(repo, "commit", "-q", "-m", "outside change")
            base = reference.scope_base(repo, ("main",))
            violations = reference.scope_violations(
                reference.scope_changed_paths(repo, base))
            self.assertEqual(violations,
                             ["docs/task-evidence/other/README.md"])
            self.assertTrue(all(not path.startswith(reference.TASK_PREFIX)
                                for path in violations))

    def test_missing_base_ref_emits_scope_base_unavailable_signal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "checkout", "-q", "-b", "swarm-task")
            self._commit_task_change(repo, "task evidence")
            self._git(repo, "branch", "-D", "main")
            self.assertIsNone(reference.scope_base(
                repo, ("origin/main", "main")))
            self.assertEqual(reference.git_commit(repo, "origin/main"), None)
            verifier = (HERE / "verify.py").read_text(encoding="utf-8")
            self.assertIn("scope_base_unavailable", verifier)
            self.assertIn("base_out_of_scope_change", verifier)


if __name__ == "__main__":
    unittest.main()
