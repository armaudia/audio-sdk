# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the SDK-STSM-FILM-NEURAL-TSM evidence package."""

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

SPDX_LICENSE = "SPDX-" "License-Identifier: Apache-2.0"


class StrictJsonTests(unittest.TestCase):
    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_rejects_nonfinite_constants(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                reference.loads_strict('{"a":' + token + "}")

    def test_rejects_trailing_data_bom_and_non_object(self) -> None:
        for payload in ('{"a":1}x', '\ufeff{"a":1}', "[1,2]", "  "):
            with self.assertRaises(ValueError):
                reference.loads_strict(payload)

    def test_canonical_roundtrip_and_digest(self) -> None:
        document = {"b": [1, True, None], "a": {"z": "x"}}
        payload = reference.canonical_bytes(document)
        self.assertEqual(payload, b'{"a":{"z":"x"},"b":[1,true,null]}')
        self.assertEqual(reference.object_digest(document),
                         hashlib.sha256(payload).hexdigest())

    def test_rejects_floats_in_canonical_evidence(self) -> None:
        with self.assertRaises(TypeError):
            reference.assert_no_float({"value": 0.5})


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins_match(self) -> None:
        for relative, expected in reference.SOURCE_PINS.items():
            path = reference.AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), expected, relative)

    def test_boundary_pins_match(self) -> None:
        for relative, expected in reference.BOUNDARY_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), expected, relative)

    def test_evidence_snippets_are_present(self) -> None:
        result = reference.evidence_snippet_check()
        self.assertEqual(result["count"], 8)
        self.assertTrue(result["all_present"], result["checks"])

    def test_inventory_record_is_the_linked_row(self) -> None:
        record = reference.inventory_record()
        self.assertEqual(record["id"], "stsm-film-neural-tsm")
        self.assertEqual(record["name"], "STSM-FiLM neural TSM")
        self.assertEqual(record["area"], "Rate and content")
        self.assertEqual(record["evidence_status"], "blocked")
        self.assertEqual(record["repository"], "audio-sdk")
        self.assertEqual(record["disposition"], "sdk-model")
        self.assertEqual(record["verification_profile"], "rate")
        self.assertEqual(record["task"], reference.TASK)
        self.assertEqual(record["evidence"][0]["record"], 42)

    def test_linked_row_identity_only(self) -> None:
        boundary = reference.boundary_block()
        self.assertFalse(boundary["board_file_pinned"])
        self.assertTrue(boundary["linked_row_identity_only"])
        self.assertFalse(boundary["mutable_board_fields_gate"])
        self.assertNotIn("status", boundary["linked_row"])
        self.assertEqual(boundary["linked_row_sha256"],
                         reference.board_row_digest(boundary["linked_row"]))
        self.assertEqual(len(boundary["linked_row_sha256"]), 64)
        self.assertNotEqual(
            boundary["linked_rows_sha256"],
            reference.sha256_file(
                reference.AUDIO_ROOT / reference.BOARD_TASK_ROW))


class AbsenceTests(unittest.TestCase):
    def test_all_candidate_artifacts_are_absent(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["probe_count"], 20)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_absent"])

    def test_no_candidate_runtime_is_available(self) -> None:
        readiness = reference.runtime_readiness()
        self.assertFalse(readiness["runtime_present"])
        self.assertFalse(readiness["runtime_pinned"])
        self.assertFalse(readiness["candidate_module_available"])
        self.assertFalse(readiness["import_attempted"])
        self.assertFalse(readiness.get("text_frontend_present", False))


class DeclarationTests(unittest.TestCase):
    def test_unpopulated_declaration_is_accepted_without_qualifying(self) -> None:
        accepted = reference.validate_asset_declaration(
            reference.declaration_control())
        self.assertEqual(accepted["status"], "accepted_unpopulated")
        self.assertFalse(accepted["qualifies"])
        self.assertFalse(accepted["assets_loaded"])

    def test_presence_claim_is_rejected(self) -> None:
        document = reference.declaration_control()
        document["source"]["declared_present"] = True
        with self.assertRaises(reference.DeclarationError) as caught:
            reference.validate_asset_declaration(document)
        self.assertEqual(caught.exception.code, "unverified_claim")

    def test_weight_digest_claim_is_rejected(self) -> None:
        document = reference.declaration_control()
        document["weights"]["weights_sha256"] = "a" * 64
        with self.assertRaises(reference.DeclarationError) as caught:
            reference.validate_asset_declaration(document)
        self.assertEqual(caught.exception.code, "unverified_claim")

    def test_qualification_claim_is_rejected(self) -> None:
        document = reference.declaration_control()
        document["disposition"]["qualifies"] = True
        with self.assertRaises(reference.DeclarationError) as caught:
            reference.validate_asset_declaration(document)
        self.assertEqual(caught.exception.code, "unverified_claim")

    def test_wrong_candidate_is_rejected(self) -> None:
        for name in ("DiffATSM", "Neural ATSM"):
            document = reference.declaration_control()
            document["candidate"]["name"] = name
            with self.assertRaises(reference.DeclarationError):
                reference.validate_asset_declaration(document)

    def test_mutation_suite_rejects_every_case(self) -> None:
        result = reference.declaration_rejections()
        self.assertGreaterEqual(result["cases"], 40)
        self.assertTrue(result["all_rejected"])
        self.assertEqual(len({row["id"] for row in result["rejections"]}), result["cases"])

    def test_strict_json_suite_rejects_every_case(self) -> None:
        result = reference.strict_json_rejections()
        self.assertEqual(result["cases"], 9)
        self.assertTrue(result["all_rejected"])

    def test_no_state_after_rejection(self) -> None:
        document = reference.declaration_control()
        before = copy.deepcopy(document)
        document["geometry"]["declared"] = True
        with self.assertRaises(reference.DeclarationError):
            reference.validate_asset_declaration(document)
        self.assertEqual(
            reference.validate_asset_declaration(before)["status"],
            "accepted_unpopulated")


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_state(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertEqual(self.contract["profile"], "rate")
        self.assertEqual(self.contract["base_commit"],
                         reference.BASE_COMMIT)
        self.assertEqual(len(self.contract["release_gates"]), 8)
        self.assertTrue(all(
            gate["status"] == "blocked" and gate["qualifies"] is False
            for gate in self.contract["release_gates"]))
        identity = self.contract["source_reported_identity"]
        self.assertFalse(identity["runnable_as_released"])
        self.assertFalse(identity["rate_only_estimator"])
        self.assertFalse(identity["official_code_found"])

    def test_report_state(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertTrue(self.report["proposal_only"])
        self.assertTrue(self.report["incomplete"])
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))
        self.assertTrue(self.report["qualification"]["not_qualified"])
        self.assertTrue(
            self.report["qualification"]["all_release_gates_blocked"])
        for key, value in self.report["qualification"].items():
            if key in ("status", "readiness", "not_qualified",
                       "all_release_gates_blocked", "reason"):
                continue
            self.assertIs(value, False, key)

    def test_eight_blocked_release_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-%02d" % index for index in range(1, 9)])
        self.assertEqual(len({gate["title"] for gate in gates}), 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             self.report["boundary"]["linked_row"])

    def test_blockers_and_artifacts(self) -> None:
        self.assertEqual([row["id"] for row in self.report["exact_blockers"]],
                         ["BLK-%02d" % index for index in range(1, 7)])
        self.assertEqual(
            [row["id"] for row in self.report["required_artifacts"]],
            ["ART-%02d" % index for index in range(1, 8)])
        for blocker in self.report["exact_blockers"]:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
        first = self.report["required_artifacts"][0]
        self.assertTrue(first["present"])
        self.assertTrue(first["verified"])
        for artifact in self.report["required_artifacts"][1:]:
            self.assertFalse(artifact["present"])
            self.assertTrue(artifact["blocked"])

    def test_rate_profile_is_not_satisfied(self) -> None:
        profile = self.report["rate_profile"]
        self.assertEqual(profile["profile"], "rate")
        self.assertFalse(profile["profile_satisfied"])
        self.assertEqual(profile["real_results"], 0)
        self.assertEqual(profile["synthetic_results"], 0)
        self.assertFalse(profile["surrogate_present"])
        self.assertFalse(profile["synthetic_envelope_only"])
        self.assertIsNone(profile["candidate_geometry"])
        self.assertEqual(len(profile["requirement_rows"]), 13)
        blocked = [row for row in profile["requirement_rows"]
                   if row["status"] == "blocked"]
        self.assertEqual(len(blocked), 12)
        self.assertTrue(profile["profile_source_check"]
                        ["all_phrases_present"])

    def test_geometry_is_text_conditioned_and_unverified(self) -> None:
        geometry = self.report["task_geometry"]
        self.assertEqual(geometry["state"],
                         reference.TASK_GEOMETRY_STATE)
        self.assertFalse(geometry["audio_input_path_verified"])
        self.assertFalse(geometry["rate_only_estimator"])
        self.assertFalse(geometry["geometry_verified"])
        for key in ("sample_rate_hz", "frame_samples", "hop_samples",
                    "channels"):
            self.assertIsNone(geometry[key])

    def test_matched_evidence_is_separated(self) -> None:
        matched = self.report["matched_evidence"]
        self.assertEqual(matched["candidate_profile_fit"], "unknown_blocked")
        self.assertFalse(matched["classes_pooled"])
        self.assertFalse(matched["matched_cohort_present"])
        self.assertFalse(matched["synthetic_schema_control_counted_as_result"])
        for row in self.report["historical_evidence"]:
            self.assertFalse(row["admitted_as_result"])
        for row in self.report["peer_separation"]:
            self.assertFalse(row["admitted_as_result"])
            self.assertFalse(row["inherited_metrics"])

    def test_declaration_and_absence(self) -> None:
        declaration = self.report["asset_declaration"]
        self.assertGreaterEqual(declaration["rejection_cases"], 40)
        self.assertTrue(declaration["all_rejected"])
        self.assertTrue(declaration["strict_json_all_rejected"])
        self.assertTrue(declaration["presence_claims_rejected"])
        self.assertFalse(declaration["assets_loaded"])
        self.assertFalse(declaration["accepted_control_qualifies"])
        self.assertTrue(self.report["absence_evidence"]["all_absent"])
        self.assertEqual(
            self.report["absence_evidence"]["present_count"], 0)

    def test_scope_and_geometry(self) -> None:
        scope = self.report["scope"]
        self.assertTrue(scope["task_local_only"])
        self.assertEqual(scope["write_scope"], reference.WRITE_SCOPE)
        for key, value in scope.items():
            if key in ("task_local_only", "write_scope"):
                continue
            self.assertIs(value, False, key)
        self.assertEqual(self.report["public_v0_geometry"],
                         reference.public_v0_geometry())

    def test_report_has_no_floats_and_is_deterministic(self) -> None:
        reference.assert_no_float(self.report)
        first = reference.canonical_report(self.report)
        second = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)
        self.assertEqual(len(first[1]), 64)


class CommittedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report_bytes = (HERE / "report.json").read_bytes()
        cls.contract_bytes = (HERE / "contract.json").read_bytes()

    def test_committed_contract_and_report_are_canonical(self) -> None:
        self.assertEqual(
            self.contract_bytes,
            reference.canonical_bytes(reference.build_contract()))
        payload, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(self.report_bytes, payload.encode("ascii"))
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            digest + "  report.json\n")

    def test_readme_digest_tables_are_live(self) -> None:
        counts = reference.verify_readme_digests(
            (HERE / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"],
                         len(reference.BOUNDARY_PINS))

    def test_sources_manifest_covers_every_file(self) -> None:
        rows = {}
        for line in (HERE / "SOURCES.sha256").read_text(
                encoding="ascii").splitlines():
            if not line or line.startswith("#"):
                continue
            digest, name = line.split("  ", 1)
            rows[name] = digest
        self.assertNotIn(reference.BOARD_TASK_ROW, rows)
        for name in reference.LOCAL_FILES:
            if name == "SOURCES.sha256":
                continue
            key = reference.TASK_PREFIX + name
            self.assertIn(key, rows)
            self.assertEqual(reference.sha256_file(HERE / name), rows[key])
        for relative in reference.SOURCE_PINS:
            self.assertIn("source:" + relative, rows)
        for relative in reference.BOUNDARY_PINS:
            self.assertIn("sdk:" + relative, rows)

    def test_spdx_sidecars_and_headers(self) -> None:
        expected = (
            "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
            + SPDX_LICENSE + "\n")
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license",
                     "SOURCES.sha256.license"):
            self.assertEqual((HERE / name).read_text(encoding="utf-8"),
                             expected)
        for name in ("reference.py", "run.py", "verify.py",
                     "test_reference.py"):
            head = "\n".join((HERE / name).read_text(
                encoding="utf-8").splitlines()[:5])
            self.assertIn(SPDX_LICENSE, head)
            self.assertIn("SPDX-FileCopyrightText: 2026", head)

    def test_json_artifacts_are_strict(self) -> None:
        for path in (HERE / "contract.json", HERE / "report.json"):
            document = reference.read_strict_json(path)
            self.assertIsInstance(document, dict)
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')


class ScopeRegressionTests(unittest.TestCase):
    """Regression coverage for the merge-base scope comparison."""

    def _git(self, repo: Path, *arguments: str) -> str:
        result = subprocess.run(["git", "-C", str(repo), *arguments],
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def _repo(self) -> Path:
        temporary = tempfile.TemporaryDirectory(prefix="stsm-film-neural-tsm-scope-")
        self.addCleanup(temporary.cleanup)
        repo = Path(temporary.name)
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.name", "scope-fixture")
        self._git(repo, "config", "user.email", "scope@example.invalid")
        self._git(repo, "config", "commit.gpgsign", "false")
        (repo / "README.md").write_text("base\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-qm", "base")
        return repo

    def test_sibling_additions_after_base_pass_scope(self) -> None:
        repo = self._repo()
        self._git(repo, "switch", "-q", "-c", reference.BRANCH)
        task_file = repo / reference.TASK_PREFIX / "report.json"
        task_file.parent.mkdir(parents=True)
        task_file.write_text("{}\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-qm", "task evidence")
        # A later sibling merge lands beside this package on main.
        self._git(repo, "switch", "-q", "main")
        sibling = repo / "docs/task-evidence/sibling-atsm/report.json"
        sibling.parent.mkdir(parents=True)
        sibling.write_text("{}\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-qm", "sibling evidence")
        self._git(repo, "switch", "-q", reference.BRANCH)
        base = reference.scope_base(repo)
        self.assertIsNotNone(base)
        paths = reference.scope_changed_paths(repo, base)
        self.assertEqual(paths,
                         [reference.TASK_PREFIX + "report.json"])
        self.assertEqual(reference.scope_violations(paths), [])
        self.assertEqual(reference.scope_violations([]), [])
        # A fixed historical base would wrongly include the sibling merge.
        historical = self._git(repo, "rev-parse", "main")
        historic = reference.scope_changed_paths(repo, historical)
        self.assertTrue(reference.scope_violations(historic))

    def test_branch_out_of_scope_edit_fails_scope(self) -> None:
        repo = self._repo()
        self._git(repo, "switch", "-q", "-c", reference.BRANCH)
        task_file = repo / reference.TASK_PREFIX / "report.json"
        task_file.parent.mkdir(parents=True)
        task_file.write_text("{}\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-qm", "task evidence")
        (repo / "CMakeLists.txt").write_text("# out of scope\n",
                                            encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-qm", "out of scope edit")
        base = reference.scope_base(repo)
        self.assertIsNotNone(base)
        paths = reference.scope_changed_paths(repo, base)
        self.assertEqual(reference.scope_violations(paths),
                         ["CMakeLists.txt"])

    def test_unresolved_base_and_outside_prefix_are_flagged(self) -> None:
        repo = self._repo()
        self._git(repo, "switch", "-q", "-c", "detached-work")
        self._git(repo, "branch", "-D", "main")
        self.assertIsNone(reference.scope_base(repo))
        self.assertEqual(
            reference.scope_violations(
                [reference.TASK_PREFIX + "report.json",
                 "docs/task-evidence/other/report.json"]),
            ["docs/task-evidence/other/report.json"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
