# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the non-stationary Gabor TSM evidence package."""

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
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"


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
        self.assertEqual(result["count"], 12)
        self.assertTrue(result["all_present"], result["checks"])

    def test_inventory_record_is_the_linked_row(self) -> None:
        record = reference.inventory_record()
        self.assertEqual(record["id"], "non-stationary-gabor-tsm")
        self.assertEqual(record["name"], "Non-stationary Gabor TSM")
        self.assertEqual(record["area"], "Rate and content")
        self.assertEqual(record["evidence_status"], "considered")
        self.assertEqual(record["repository"], "audio-sdk")
        self.assertEqual(record["disposition"], "sdk-reference")
        self.assertEqual(record["verification_profile"], "rate")
        self.assertEqual(record["task"], reference.TASK)
        self.assertEqual(
            record["plan_note"],
            "Reproduce the chosen technique on exact rate ratios before a "
            "streaming API claim.")
        self.assertEqual(record["evidence"][0]["path"],
                         "cpp-library/pipeline-validation/"
                         "playback-speed-candidates.md")

    def test_linked_row_identity_only(self) -> None:
        boundary = reference.boundary_block()
        self.assertEqual(
            set(boundary["linked_row"]),
            {"id", "title", "component", "mode", "repository", "depends_on"})
        for field in ("status", "owner", "claim", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertNotIn(field, boundary["linked_row"])
        self.assertFalse(boundary["board_file_pinned"])
        self.assertFalse(boundary["mutable_board_fields_gate"])
        self.assertEqual(
            [row["id"] for row in boundary["linked_rows"]],
            list(reference.LINKED_ROW_IDS))


class AbsenceTests(unittest.TestCase):
    def test_all_candidate_artifacts_are_absent(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["probe_count"], 20)
        self.assertEqual(summary["workspace_probe_count"], 12)
        self.assertEqual(summary["worktree_probe_count"], 6)
        self.assertEqual(summary["home_probe_count"], 2)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_absent"])
        self.assertFalse(summary["network_used"])
        self.assertFalse(summary["download_attempted"])

    def test_no_candidate_runtime_is_available(self) -> None:
        runtime = reference.runtime_readiness()
        self.assertFalse(runtime["runtime_present"])
        self.assertFalse(runtime["runtime_pinned"])
        self.assertFalse(runtime["candidate_module_available"])
        self.assertFalse(runtime["import_attempted"])
        self.assertFalse(runtime["nsgt_reference_present"])
        self.assertFalse(runtime["ltfat_reference_present"])
        self.assertEqual(runtime["ltfat_license_reported"], "GPL-3.0")
        self.assertIsNone(runtime["lock_sha256"])


class DeclarationTests(unittest.TestCase):
    def test_unpopulated_declaration_is_accepted_without_qualifying(
            self) -> None:
        result = reference.validate_asset_declaration(
            reference.declaration_control())
        self.assertEqual(result["status"], "accepted_unpopulated")
        self.assertFalse(result["qualifies"])
        self.assertFalse(result["assets_loaded"])
        self.assertGreater(result["checks"], 20)

    def test_presence_claim_is_rejected(self) -> None:
        document = copy.deepcopy(reference.declaration_control())
        document["source"]["declared_present"] = True
        with self.assertRaises(reference.DeclarationError) as caught:
            reference.validate_asset_declaration(document)
        self.assertEqual(caught.exception.code, "unverified_claim")

    def test_reference_digest_claim_is_rejected(self) -> None:
        document = copy.deepcopy(reference.declaration_control())
        document["reference"]["license_id"] = "GPL-3.0"
        with self.assertRaises(reference.DeclarationError):
            reference.validate_asset_declaration(document)

    def test_qualification_claim_is_rejected(self) -> None:
        document = copy.deepcopy(reference.declaration_control())
        document["disposition"]["qualifies"] = True
        with self.assertRaises(reference.DeclarationError) as caught:
            reference.validate_asset_declaration(document)
        self.assertEqual(caught.exception.code, "unverified_claim")

    def test_wrong_candidate_is_rejected(self) -> None:
        document = copy.deepcopy(reference.declaration_control())
        document["candidate"]["name"] = "Granular TSM"
        with self.assertRaises(reference.DeclarationError):
            reference.validate_asset_declaration(document)

    def test_mutation_suite_rejects_every_case(self) -> None:
        result = reference.declaration_rejections()
        self.assertEqual(result["cases"], 43)
        self.assertTrue(result["all_rejected"])

    def test_strict_json_suite_rejects_every_case(self) -> None:
        result = reference.strict_json_rejections()
        self.assertEqual(result["cases"], 9)
        self.assertTrue(result["all_rejected"])

    def test_no_state_after_rejection(self) -> None:
        document = copy.deepcopy(reference.declaration_control())
        document["geometry"]["declared"] = True
        for _ in range(2):
            with self.assertRaises(reference.DeclarationError):
                reference.validate_asset_declaration(document)
        self.assertEqual(
            reference.validate_asset_declaration(
                reference.declaration_control())["status"],
            "accepted_unpopulated")


class RateRequestTests(unittest.TestCase):
    def test_valid_control_defers_without_executing(self) -> None:
        result = reference.validate_rate_request(
            reference.rate_request_control())
        self.assertEqual(result["status"], "deferred_missing_reference")
        self.assertFalse(result["executed"])
        self.assertFalse(result["audio_read"])
        self.assertFalse(result["transform_applied"])
        self.assertFalse(result["qualifies"])
        self.assertEqual(result["ratio_units"], 2)

    def test_nonfinite_ratios_are_rejected(self) -> None:
        for token in ("nan", "NaN", "Infinity", "-Infinity", "inf"):
            document = copy.deepcopy(reference.rate_request_control())
            document["rate"]["ratio"] = token
            with self.assertRaises(reference.RateRequestError) as caught:
                reference.validate_rate_request(document)
            self.assertIn(caught.exception.code,
                          ("nonfinite_rate", "rate_not_canonical"))

    def test_non_string_ratio_is_rejected(self) -> None:
        for value in (1, 1.0, True, None):
            document = copy.deepcopy(reference.rate_request_control())
            document["rate"]["ratio"] = value
            with self.assertRaises(reference.RateRequestError):
                reference.validate_rate_request(document)

    def test_out_of_range_and_noncanonical_are_rejected(self) -> None:
        for token in ("0", "0.25", "2.5", "3", "1e0", "+1", "01", "1.00"):
            document = copy.deepcopy(reference.rate_request_control())
            document["rate"]["ratio"] = token
            with self.assertRaises(reference.RateRequestError):
                reference.validate_rate_request(document)

    def test_input_presence_and_bad_schedule_are_rejected(self) -> None:
        document = copy.deepcopy(reference.rate_request_control())
        document["input"]["declared_present"] = True
        with self.assertRaises(reference.RateRequestError):
            reference.validate_rate_request(document)
        document = copy.deepcopy(reference.rate_request_control())
        document["rate"]["schedule"] = [{"at_source_sample": 1,
                                        "ratio": "1"}]
        with self.assertRaises(reference.RateRequestError):
            reference.validate_rate_request(document)

    def test_mutation_suite_rejects_every_case(self) -> None:
        result = reference.rate_request_rejections()
        self.assertEqual(result["cases"], 58)
        self.assertTrue(result["all_rejected"])
        self.assertGreaterEqual(result["cases"], 50)


class ContractReportTests(unittest.TestCase):
    def test_contract_state(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(contract["schema_id"], reference.CONTRACT_ID)
        self.assertEqual(contract["task"], reference.TASK)
        self.assertEqual(contract["component"], reference.COMPONENT_ID)
        self.assertEqual(contract["mode"], "feasibility")
        self.assertEqual(contract["profile"], "rate")
        self.assertEqual(contract["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(contract["branch"], reference.BRANCH)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "incomplete")
        self.assertTrue(contract["proposal_only"])
        self.assertEqual(contract["qualification_status"], "not_qualified")

    def test_report_state(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["schema_id"], reference.REPORT_SCHEMA_ID)
        self.assertEqual(report["decision"], "DEFER")
        self.assertIn(report["status"], ("incomplete", "proposal_only") )
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertTrue(report["incomplete"])
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(reference.build_contract()))

    def test_eight_blocked_release_gates(self) -> None:
        gates = reference.build_report()["gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-%02d" % index for index in range(1, 9)])
        self.assertEqual(len(gates), 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertEqual(gate["linked_row"],
                             reference.board_row_projection())
            self.assertTrue(gate["reopen_condition"])

    def test_blockers_and_artifacts(self) -> None:
        report = reference.build_report()
        blockers = report["exact_blockers"]
        self.assertEqual([row["id"] for row in blockers],
                         ["BLK-%02d" % index for index in range(1, 7)])
        for row in blockers:
            self.assertEqual(row["status"], "open")
            self.assertFalse(row["qualifies"])
        artifacts = report["required_artifacts"]
        self.assertEqual([row["id"] for row in artifacts],
                         ["ART-%02d" % index for index in range(1, 8)])
        self.assertTrue(artifacts[0]["present"])
        for row in artifacts[1:]:
            self.assertFalse(row["present"])
            self.assertTrue(row["blocked"])
            self.assertIsNone(row["sha256"])
            self.assertIsNone(row["revision"])
            self.assertIsNone(row["bytes"])

    def test_rate_profile_is_not_satisfied(self) -> None:
        profile = reference.build_report()["rate_profile"]
        self.assertEqual(profile["profile"], "rate")
        self.assertFalse(profile["profile_satisfied"])
        self.assertEqual(profile["real_results"], 0)
        self.assertEqual(profile["synthetic_results"], 0)
        self.assertFalse(profile["surrogate_present"])
        rows = profile["requirement_rows"]
        self.assertEqual(len(rows), 13)
        self.assertEqual(sum(1 for row in rows
                             if row["status"] == "blocked"), 12)
        self.assertTrue(all(row["qualifies"] is False for row in rows))
        self.assertTrue(profile["profile_source_check"]
                        ["all_phrases_present"])

    def test_geometry_is_plausible_but_unverified(self) -> None:
        geometry = reference.build_report()["task_geometry"]
        self.assertEqual(geometry["state"],
                         reference.TASK_GEOMETRY_STATE)
        self.assertEqual(geometry["rate_profile_fit"],
                         "plausible_unverified")
        self.assertEqual(geometry["source_reported_input"],
                         "audio waveform")
        for key in ("audio_input_path_verified", "audio_output_path_verified",
                    "geometry_documented", "geometry_verified"):
            self.assertFalse(geometry[key])
        for key in ("sample_rate_hz", "frame_samples", "hop_samples",
                    "channels", "analysis_window_schedule",
                    "synthesis_window", "dual_window_rule",
                    "transform_length", "latency_ms",
                    "reset_and_drain_policy"):
            self.assertIsNone(geometry[key])

    def test_matched_evidence_is_separated(self) -> None:
        matched = reference.build_report()["matched_evidence"]
        self.assertEqual(matched["candidate_profile_fit"],
                         "plausible_unverified")
        self.assertFalse(matched["classes_pooled"])
        for key in ("matched_cohort_present", "matched_baseline_present",
                    "source_output_mapping_present",
                    "same_condition_control_present",
                    "listening_or_labeled_screen_present"):
            self.assertFalse(matched[key])

    def test_declaration_and_absence(self) -> None:
        report = reference.build_report()
        declaration = report["asset_declaration"]
        self.assertTrue(declaration["all_rejected"])
        self.assertFalse(declaration["accepted_control_qualifies"])
        self.assertFalse(declaration["assets_loaded"])
        self.assertTrue(report["absence_evidence"]["all_absent"])
        self.assertEqual(report["absence_evidence"]["present_count"], 0)
        self.assertEqual(report["runtime_readiness"]["interpreter_pin"],
                         reference.REQUIRED_INTERPRETER)

    def test_scope_and_geometry(self) -> None:
        report = reference.build_report()
        self.assertTrue(report["scope"]["task_local_only"])
        self.assertFalse(report["scope"]["network_access"])
        self.assertFalse(report["scope"]["candidate_runtime_executed"])
        self.assertFalse(report["scope"]["provider_registration"])
        self.assertEqual(report["public_v0_geometry"],
                         reference.public_v0_geometry())
        self.assertEqual(report["public_v0_geometry"]["sample_rate_hz"],
                         16000)

    def test_report_has_no_floats_and_is_deterministic(self) -> None:
        first = reference.canonical_bytes(reference.build_report())
        second = reference.canonical_bytes(reference.build_report())
        self.assertEqual(first, second)
        self.assertNotIn(b"NaN", first)
        self.assertNotIn(b"Infinity", first)
        reference.assert_no_float(reference.build_report())


class CommittedArtifactTests(unittest.TestCase):
    def test_committed_contract_and_report_are_canonical(self) -> None:
        contract = HERE / "contract.json"
        report = HERE / "report.json"
        sidecar = HERE / "report.json.sha256"
        self.assertEqual(contract.read_bytes(),
                         reference.canonical_bytes(
                             reference.build_contract()))
        payload, digest = reference.canonical_report(
            reference.build_report())
        self.assertEqual(report.read_bytes(), payload.encode("ascii"))
        self.assertEqual(sidecar.read_text(encoding="ascii"),
                         digest + "  report.json\n")

    def test_readme_digest_tables_are_live(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        rows = reference.verify_readme_digests(text)
        self.assertEqual(rows["source"], len(reference.SOURCE_PINS))
        self.assertEqual(rows["boundary"], len(reference.BOUNDARY_PINS))

    def test_sources_manifest_covers_every_file(self) -> None:
        manifest = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        rows = {}
        for line in manifest.splitlines():
            if not line or line.startswith("#"):
                continue
            digest, name = line.split("  ", 1)
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
            rows[name] = digest
        for name in reference.EXPECTED_DIR_FILES:
            if name == "SOURCES.sha256":
                continue
            self.assertIn(reference.TASK_PREFIX + name, rows)
        for name, digest in rows.items():
            if name.startswith("source:"):
                path = reference.AUDIO_ROOT / name[len("source:"):]
            elif name.startswith("sdk:"):
                path = reference.WORKTREE / name[len("sdk:"):]
            else:
                path = reference.WORKTREE / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(reference.sha256_file(path), digest, name)
        self.assertNotIn(reference.BOARD_TASK_ROW, rows)

    def test_spdx_sidecars_and_headers(self) -> None:
        sidecar_text = SPDX_COPYRIGHT + "\n" + SPDX_LICENSE + "\n"
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license",
                     "SOURCES.sha256.license"):
            self.assertEqual((HERE / name).read_text(encoding="utf-8"),
                             sidecar_text, name)
        for name in ("README.md", "LICENSES.md"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_COPYRIGHT, text)
            self.assertIn(SPDX_LICENSE, text)
        for name in ("reference.py", "run.py", "test_reference.py",
                     "verify.py"):
            head = "\n".join(
                (HERE / name).read_text(encoding="utf-8").splitlines()[:5])
            self.assertIn(SPDX_COPYRIGHT, head)
            self.assertIn(SPDX_LICENSE, head)

    def test_json_artifacts_are_strict(self) -> None:
        for name in ("contract.json", "report.json"):
            reference.read_strict_json(HERE / name)


class ScopeRegressionTests(unittest.TestCase):
    """Regression coverage for the merge-base scope comparison."""

    def _git(self, repo: Path, *arguments: str) -> str:
        result = subprocess.run(["git", "-C", str(repo), *arguments],
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def _repo(self) -> Path:
        temporary = tempfile.TemporaryDirectory(prefix="nsgt-scope-")
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
        self._git(repo, "switch", "-q", "main")
        sibling = repo / "docs/task-evidence/sibling-tsm/report.json"
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
