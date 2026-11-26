# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the Rapidly speech-denoise SDK blocker package."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *arguments],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


class JsonAndCanonicalTests(unittest.TestCase):
    def test_canonical_rejects_nonfinite(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"value": float("nan")})

    def test_parse_strict_json_rejects_duplicate_key(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text(b'{"a":1,"a":2}')

    def test_parse_strict_json_rejects_constant(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text(b'{"a":Infinity}')

    def test_parse_strict_json_rejects_non_utf8(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text(b'{"a":"\xff"}')

    def test_read_strict_json_rejects_non_object(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "value.json"
            path.write_text("[1,2]", encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_assert_no_float_recurses(self) -> None:
        with self.assertRaises(ValueError):
            reference.assert_no_float({"a": [1, 2, 3.5]})

    def test_object_digest_is_stable(self) -> None:
        self.assertEqual(reference.object_digest({"b": 2, "a": 1}),
                         reference.object_digest({"a": 1, "b": 2}))


class BoardIdentityTests(unittest.TestCase):
    def test_board_projection_matches_task(self) -> None:
        projection = reference.board_row_projection()
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["component"], reference.COMPONENT_ID)
        self.assertEqual(projection["mode"], reference.MODE)
        self.assertEqual(projection["repository"], reference.REPOSITORY)
        self.assertEqual(tuple(projection["depends_on"]),
                         reference.DEPENDS_ON)

    def test_board_projection_excludes_mutable_fields(self) -> None:
        projection = reference.board_row_projection()
        for field in ("status", "owner", "claim", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertNotIn(field, projection)

    def test_linked_rows_are_stable(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))
        self.assertEqual(reference.linked_rows_digest(rows),
                         reference.linked_rows_digest())

    def test_board_digests_are_deterministic(self) -> None:
        projection = reference.board_row_projection()
        expected = hashlib.sha256(reference.canonical_bytes(projection)).hexdigest()
        self.assertEqual(reference.board_row_digest(projection), expected)


class AbsenceTests(unittest.TestCase):
    def test_all_fixed_probes_absent(self) -> None:
        summary = reference.absence_summary()
        self.assertTrue(summary["all_probes_absent"])
        self.assertEqual(summary["present_count"], 0)
        self.assertEqual(summary["probe_count"], len(reference.all_probes()))

    def test_probe_counts_split_by_scope(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["workspace_probe_count"],
                         len(reference.WORKSPACE_PROBES))
        self.assertEqual(summary["worktree_probe_count"],
                         len(reference.WORKTREE_PROBES))
        self.assertEqual(summary["home_probe_count"],
                         len(reference.HOME_PROBES))
        self.assertTrue(summary["fixed_probe_list_only"])
        self.assertFalse(summary["recursive_workspace_walk"])


class VendorRecordTests(unittest.TestCase):
    def test_vendor_record_is_recorded_only(self) -> None:
        record = reference.vendor_record()
        self.assertEqual(record["vendor_name"], reference.VENDOR_NAME)
        self.assertIsNone(record["source_revision"])
        self.assertIsNone(record["release_version"])
        self.assertIsNone(record["artifact_sha256"])
        self.assertFalse(record["locally_verified"])
        self.assertFalse(record["admitted_as_result"])
        self.assertFalse(record["qualifies"])

    def test_recorded_identity_labels_every_fact(self) -> None:
        block = reference.recorded_identity_block()
        self.assertEqual(block["label"], "source_reported_not_locally_verified")
        self.assertIsNone(block["source_reported_scores"])
        self.assertFalse(block["locally_verified"])
        self.assertFalse(block["admitted_as_result"])
        self.assertFalse(block["candidate_matrix"]["rapidly_row_present"])
        self.assertEqual(block["candidate_store"]["trained_rate_hz"], 48000)
        self.assertTrue(block["candidate_store"]["watermarked_without_license"])

    def test_reported_geometry_facts(self) -> None:
        geometry = reference.task_geometry()
        self.assertEqual(geometry["reported_rate_hz"], 48000)
        self.assertEqual(geometry["reported_latency_variants_ms"], [11, 21, 32, 96])
        self.assertEqual(geometry["reported_model_sizes_kb"], [615, 851, 854, 925])
        self.assertEqual(geometry["reported_output_busses"], ["dialogue", "noise"])
        self.assertIsNone(geometry["vendor_rate_to_v0_mapping"])
        self.assertFalse(geometry["verified_here"])


class GeometryTests(unittest.TestCase):
    def test_v0_geometry_is_installed_fact(self) -> None:
        geometry = reference.public_v0_geometry()
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "float32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertFalse(geometry["registered"])
        self.assertFalse(geometry["vendor_mapping_verified"])

    def test_vendor_rate_differs_from_v0(self) -> None:
        self.assertNotEqual(reference.REPORTED_TRAINED_RATE_HZ,
                            reference.V0_SAMPLE_RATE_HZ)


class ArtifactTests(unittest.TestCase):
    def test_required_artifacts_all_unverified(self) -> None:
        for item in reference.required_artifacts():
            self.assertTrue(item["required"])
            self.assertIsNone(item["sha256"])
            self.assertIsNone(item["bytes"])
            self.assertIsNone(item["revision"])
            self.assertFalse(item["locally_verified"])
            self.assertFalse(item["admitted_as_result"])
            self.assertFalse(item["qualifies"])

    def test_asset_registry_has_no_rapidly_entry(self) -> None:
        registry = reference.asset_registry()
        self.assertFalse(registry["rapidly_entry_present"])
        self.assertEqual(registry["rapidly_candidate_ids"], [])
        self.assertFalse(registry["asset_identity_available_for_rapidly"])

    def test_evidence_inputs_are_not_results(self) -> None:
        for row in reference.evidence_inputs():
            self.assertFalse(row["is_vendor_result"])
            self.assertFalse(row["is_entitlement"])
            self.assertEqual(len(row["sha256"]), 64)


class ProfileAndGateTests(unittest.TestCase):
    def test_enhancement_profile_rows(self) -> None:
        profile = reference.enhancement_profile_block()
        self.assertEqual(profile["name"], "enhancement")
        self.assertEqual(len(profile["required_items"]), 8)
        self.assertTrue(all(row["satisfied_for_qualification"] is False
                            for row in profile["required_items"]))
        self.assertIsNone(profile["real_runtime_metrics"])

    def test_profile_source_row_matches_verification(self) -> None:
        check = reference.profile_row_check()
        self.assertTrue(check["row_found"])
        self.assertEqual(check["phrases_checked"],
                         len(reference.PROFILE_PHRASES))
        self.assertTrue(check["phrases_present"])

    def test_release_gates_all_blocked(self) -> None:
        gates = reference.release_gates()
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertEqual([gate["id"] for gate in gates],
                         [item[0] for item in reference.RELEASE_GATES])

    def test_blockers_have_reopen_conditions(self) -> None:
        blockers = reference.exact_blockers()
        self.assertEqual(len(blockers), 8)
        for item in blockers:
            self.assertTrue(item["reopen_condition"])
            self.assertIn(item["id"],
                          [row["blocker_id"]
                           for row in reference.build_report()["reopen_conditions"]])

    def test_qualification_guard(self) -> None:
        qualification = reference.qualification_block()
        self.assertFalse(qualification["candidate_qualified"])
        self.assertTrue(qualification["no_missing_result_qualifies_candidate"])
        self.assertEqual(qualification["blocked_gate_count"], 8)

    def test_rights_gap_is_open(self) -> None:
        for gap in reference.rights_gap():
            self.assertNotEqual(gap["state"], "cleared")


class ManifestTests(unittest.TestCase):
    def test_manifest_accepts_synthetic_shape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rapidly-accept-") as raw:
            document = reference._synthetic_manifest(Path(raw))
            result = reference.validate_manifest(document)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["runtime_executed"])
        self.assertFalse(result["vendor_library_loaded"])
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["qualifies"])

    def test_manifest_rejects_watermark_not_cleared(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rapidly-watermark-") as raw:
            document = reference._synthetic_manifest(Path(raw))
            document["geometry"]["watermark_free_entitlement"] = False
            with self.assertRaises(reference.Invalid):
                reference.validate_manifest(document)

    def test_manifest_rejects_48000_geometry(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rapidly-rate-") as raw:
            document = reference._synthetic_manifest(Path(raw))
            document["geometry"]["sample_rate_hz"] = 48000
            with self.assertRaises(reference.Invalid):
                reference.validate_manifest(document)

    def test_manifest_rejects_missing_hash(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rapidly-hash-") as raw:
            document = reference._synthetic_manifest(Path(raw))
            document["vendor"]["terms_record_sha256"] = "0" * 64
            with self.assertRaises(reference.Invalid):
                reference.validate_manifest(document)

    def test_manifest_rejects_online_runtime(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rapidly-online-") as raw:
            document = reference._synthetic_manifest(Path(raw))
            document["runtime"]["offline"] = False
            with self.assertRaises(reference.Invalid):
                reference.validate_manifest(document)

    def test_manifest_rejects_uncleared_rights(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rapidly-rights-") as raw:
            document = reference._synthetic_manifest(Path(raw))
            document["rights"]["publication"] = False
            with self.assertRaises(reference.Invalid):
                reference.validate_manifest(document)

    def test_manifest_rejects_unknown_field(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rapidly-extra-") as raw:
            document = reference._synthetic_manifest(Path(raw))
            document["license_key"] = "secret"
            with self.assertRaises(reference.Invalid):
                reference.validate_manifest(document)

    def test_manifest_rejects_float(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rapidly-float-") as raw:
            document = reference._synthetic_manifest(Path(raw))
            document["input"]["clip_count"] = 1.0
            with self.assertRaises(reference.Invalid):
                reference.validate_manifest(document)


class AdverseTests(unittest.TestCase):
    def test_adverse_controls_all_rejected(self) -> None:
        control = reference.admission_controls()
        self.assertTrue(control["all_rejected_rejected"])
        self.assertEqual(control["rejected_count"], len(control["cases"]) - 1)
        self.assertFalse(control["runtime_executed"])

    def test_synthetic_control_accepted_once(self) -> None:
        control = reference.admission_controls()
        self.assertTrue(control["synthetic_control_accepted"])
        self.assertEqual(control["accepted_count"], 1)


class ReportTests(unittest.TestCase):
    def test_report_is_defer_shape(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertIsNone(report["candidate_metrics"])
        self.assertTrue(report["scope"]["task_local_only"])
        self.assertFalse(report["scope"]["model_executed"])

    def test_report_is_canonical_json(self) -> None:
        payload = reference.canonical_report_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertIsInstance(json.loads(payload.decode("ascii")), dict)

    def test_contract_matches_report(self) -> None:
        report = reference.build_report()
        contract = reference.build_contract()
        for field in ("qualification", "exact_blockers", "release_gates",
                      "task_row_identity", "scope", "source_pins",
                      "boundary_pins", "caller_asset_contract"):
            self.assertEqual(contract[field], report[field])


class DigestTableTests(unittest.TestCase):
    def test_expected_keys_cover_all_sections(self) -> None:
        expected = reference.expected_readme_keys()
        self.assertEqual(set(expected), set(reference.README_SECTIONS))
        self.assertEqual(len(expected["source"]), len(reference.SOURCE_PINS))
        self.assertEqual(len(expected["boundary"]), len(reference.BOUNDARY_PINS))

    def test_readme_tables_validate_live(self) -> None:
        counts = reference.verify_readme_digests(
            (HERE / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(counts, {name: len(reference.expected_readme_keys()[name])
                                  for name in reference.README_SECTIONS})

    def test_readme_table_update_is_idempotent(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        updated = reference.update_readme_tables(text)
        self.assertEqual(updated, reference.update_readme_tables(updated))

    def test_parse_readme_rejects_bad_digest(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        text = text.replace("`46d09945", "`46d0994f", 1)
        with self.assertRaises(ValueError):
            reference.verify_readme_digests(text)


class ScopeTests(unittest.TestCase):
    """Regression coverage for the newest-merge-base scope comparison."""

    def _repository(self, root: Path) -> Path:
        repo = root / "audio-sdk"
        repo.mkdir()
        _git(repo, "init", "-q", "-b", "main")
        _git(repo, "config", "user.name", "scope-fixture")
        _git(repo, "config", "user.email", "scope@example.invalid")
        _git(repo, "config", "commit.gpgsign", "false")
        task = repo / reference.TASK_PREFIX
        task.mkdir(parents=True)
        (task / "README.md").write_text("task package\n", encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "task package")
        return repo

    def _add_siblings(self, repo: Path) -> None:
        for name in ("sibling-alpha", "sibling-beta"):
            sibling = repo / "docs/task-evidence" / name
            sibling.mkdir(parents=True)
            (sibling / "report.json").write_text("{}\n", encoding="utf-8")
            (sibling / "verify.py").write_text("# sibling\n", encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "unrelated sibling packages")

    def test_sibling_additions_after_base_pass_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            historical = _git(repo, "rev-parse", "HEAD")
            self._add_siblings(repo)
            head = _git(repo, "rev-parse", "HEAD")
            base = reference.scope_base(repo)
            self.assertEqual(base, head)
            self.assertEqual(reference.scope_changed_paths(repo, base), [])
            self.assertEqual(reference.scope_violations([]), [])
            historic = reference.scope_changed_paths(repo, historical)
            self.assertIn("docs/task-evidence/sibling-alpha/report.json",
                          historic)
            self.assertTrue(reference.scope_violations(historic))

    def test_branch_out_of_scope_edit_fails_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._add_siblings(repo)
            _git(repo, "checkout", "-q", "-b",
                 "swarm/SDK-RAPIDLY-scope")
            (repo / "CMakeLists.txt").write_text("changed\n", encoding="utf-8")
            _git(repo, "add", "CMakeLists.txt")
            _git(repo, "commit", "-qm", "out of scope edit")
            base = reference.scope_base(repo)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, ["CMakeLists.txt"])
            self.assertEqual(reference.scope_violations(paths),
                             ["CMakeLists.txt"])

    def test_missing_base_ref_is_not_silently_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            _git(repo, "branch", "-m", "detached-work")
            self.assertIsNone(reference.scope_base(repo))

    def test_scope_violations_flags_outside_prefix(self) -> None:
        paths = [reference.TASK_PREFIX + "README.md", "CMakeLists.txt"]
        self.assertEqual(reference.scope_violations(paths),
                         ["CMakeLists.txt"])


class PackageBoundaryTests(unittest.TestCase):
    def test_expected_files_exactly(self) -> None:
        actual = {path.name for path in HERE.iterdir() if path.is_file()}
        self.assertEqual(actual, reference.EXPECTED_DIR_FILES)
        self.assertEqual([path.name for path in HERE.iterdir()
                          if path.is_dir()], [])
        self.assertFalse(any(HERE.rglob("__pycache__")))
        self.assertFalse(any(HERE.rglob("*.pyc")))

    def test_no_forbidden_artifacts_or_symlinks(self) -> None:
        for path in sorted(HERE.iterdir()):
            self.assertNotIn(path.suffix.lower(),
                             reference.FORBIDDEN_SUFFIXES)
            self.assertFalse(path.is_symlink())


if __name__ == "__main__":
    unittest.main()
