# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the SDK-SAMPLESUMO-TS evidence package."""

from __future__ import annotations

import copy
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

import reference
import verify


HERE = Path(__file__).resolve().parent


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=Evidence Test",
         "-c", "user.email=test@example.invalid", *arguments],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError("git " + " ".join(arguments) + ": " +
                             result.stderr.strip())
    return result.stdout.strip()


def _scope_repo(root: Path, *, origin_main: bool, local_main: bool) -> tuple[Path, str]:
    repo = root / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "checkout", "-q", "-b", "main")
    _git(repo, "commit", "-q", "--allow-empty", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-q", "-b", "swarm/SDK-SAMPLESUMO-TS")
    task_file = repo / reference.TASK_PREFIX / "notes.txt"
    task_file.parent.mkdir(parents=True)
    task_file.write_text("task-local evidence\n", encoding="ascii")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "task local")
    if local_main:
        _git(repo, "checkout", "-q", "main")
        sibling = repo / "docs/task-evidence/sibling/README.md"
        sibling.parent.mkdir(parents=True)
        sibling.write_text("later sibling merge\n", encoding="ascii")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "sibling merge")
        if origin_main:
            _git(repo, "update-ref", "refs/remotes/origin/main", "main")
    _git(repo, "checkout", "-q", "swarm/SDK-SAMPLESUMO-TS")
    return repo, base


class ScopeGateTests(unittest.TestCase):
    """Regression tests for the newest-merge-base task-local scope gate."""

    def test_scope_base_newest_merge_base_and_out_of_scope_change(self) -> None:
        with tempfile.TemporaryDirectory(prefix="samplesumo-scope-1-") as folder:
            repo, base = _scope_repo(Path(folder), origin_main=True,
                                     local_main=True)
            self.assertEqual(reference.scope_base(repo), base)
            self.assertEqual(verify.scope_error_codes(repo), [])
            out_of_scope = repo / "CONTRACTS.md"
            out_of_scope.write_text("changed\n", encoding="ascii")
            _git(repo, "add", "-A")
            _git(repo, "commit", "-q", "-m", "out of scope")
            self.assertEqual(verify.scope_error_codes(repo),
                             ["base_out_of_scope_change:CONTRACTS.md"])
            self.assertNotIn("docs/task-evidence/sibling/README.md",
                             reference.scope_changed_paths(repo, base))

    def test_scope_base_falls_back_to_main(self) -> None:
        with tempfile.TemporaryDirectory(prefix="samplesumo-scope-2-") as folder:
            repo, base = _scope_repo(Path(folder), origin_main=False,
                                     local_main=True)
            self.assertIsNone(reference.git_commit(repo, "origin/main"))
            self.assertEqual(reference.scope_base(repo), base)
            self.assertEqual(verify.scope_error_codes(repo), [])

    def test_scope_base_unavailable_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="samplesumo-scope-3-") as folder:
            repo, _base = _scope_repo(Path(folder), origin_main=False,
                                      local_main=True)
            _git(repo, "branch", "-D", "main")
            self.assertIsNone(reference.scope_base(repo))
            self.assertEqual(verify.scope_error_codes(repo),
                             ["scope_base_unavailable"])
            (repo / "README.md").write_text("outside\n", encoding="ascii")
            _git(repo, "add", "-A")
            _git(repo, "commit", "-q", "-m", "further out of scope")
            self.assertEqual(verify.scope_error_codes(repo),
                             ["scope_base_unavailable"])


class ScopeHelperTests(unittest.TestCase):

    def test_scope_violations_filters_task_prefix(self) -> None:
        paths = [reference.TASK_PREFIX + "report.json", "README.md",
                 "docs/task-evidence/other/reference.py", ""]
        self.assertEqual(reference.scope_violations(paths),
                         ["README.md", "docs/task-evidence/other/reference.py"])

    def test_scope_refs_order(self) -> None:
        self.assertEqual(reference.SCOPE_BASE_REFS, ("origin/main", "main"))

    def test_no_fixed_base_fallback(self) -> None:
        with tempfile.TemporaryDirectory(prefix="samplesumo-scope-4-") as folder:
            repo = Path(folder)
            _git(repo, "init", "-q")
            self.assertIsNone(reference.scope_base(repo))


class StrictJsonTests(unittest.TestCase):

    def test_accepts_canonical_object(self) -> None:
        self.assertEqual(reference.strict_json(b'{"a":1}'), {"a": 1})

    def test_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_json(b'{"a":1,"a":2}')

    def test_rejects_nan(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_json(b'{"a":NaN}')

    def test_rejects_infinity(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_json(b'{"a":Infinity}')

    def test_rejects_trailing_data(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_json(b'{"a":1} junk')

    def test_rejects_non_object_root(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_json(b'[1]')

    def test_rejects_byte_order_mark(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_json(b'\xef\xbb\xbf{}')

    def test_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_json(b'')

    def test_rejects_invalid_utf8(self) -> None:
        with self.assertRaises(UnicodeDecodeError):
            reference.strict_json(b'{"a":"\xff"}')

    def test_strict_json_rejection_record(self) -> None:
        record = reference.strict_json_rejections()
        self.assertTrue(record["all_rejected"])
        self.assertEqual(record["cases"], len(record["rejections"]))


class ManifestTests(unittest.TestCase):

    def test_baseline_accepted_shape_only(self) -> None:
        ok, code = reference.validate_manifest(reference.baseline_manifest())
        self.assertTrue(ok)
        self.assertEqual(code, "accepted_shape_only")

    def test_baseline_does_not_qualify(self) -> None:
        self.assertFalse(reference.baseline_manifest()["qualifies"])

    def test_wrong_schema_rejected(self) -> None:
        document = copy.deepcopy(reference.baseline_manifest())
        document["schema_id"] = "audio-sdk/other/0.1"
        self.assertEqual(reference.validate_manifest(document)[1],
                         "manifest_schema_id")

    def test_candidate_presence_claim_rejected(self) -> None:
        document = copy.deepcopy(reference.baseline_manifest())
        document["candidate"]["runtime_present"] = True
        self.assertEqual(reference.validate_manifest(document)[1],
                         "candidate_runtime_present")

    def test_stereo_rejected(self) -> None:
        document = copy.deepcopy(reference.baseline_manifest())
        document["format"]["channels"] = 2
        self.assertEqual(reference.validate_manifest(document)[1],
                         "format_channels")

    def test_download_permitted_rejected(self) -> None:
        document = copy.deepcopy(reference.baseline_manifest())
        document["tool"]["no_download"] = False
        self.assertEqual(reference.validate_manifest(document)[1],
                         "tool_disclosure_or_download")

    def test_traversal_install_root_rejected(self) -> None:
        document = copy.deepcopy(reference.baseline_manifest())
        document["tool"]["install_root"] = "/opt/../etc"
        self.assertEqual(reference.validate_manifest(document)[1],
                         "tool_install_root_invalid")

    def test_claims_qualified_rejected(self) -> None:
        document = copy.deepcopy(reference.baseline_manifest())
        document["rights"]["claims_qualified"] = True
        self.assertEqual(reference.validate_manifest(document)[1],
                         "rights_claims_qualified")

    def test_all_admission_cases_rejected(self) -> None:
        record = reference.admission_rejections()
        self.assertTrue(record["all_rejected"])
        self.assertGreaterEqual(record["cases"], 40)
        self.assertTrue(record["assets_never_loaded"])

    def test_admission_case_ids_unique(self) -> None:
        cases = reference.admission_cases()
        names = [name for name, _document in cases]
        self.assertEqual(len(names), len(set(names)))

    def test_control_accepted_but_unqualified(self) -> None:
        record = reference.admission_rejections()
        self.assertTrue(record["control_accepted"])
        self.assertFalse(record["control_qualifies"])


class EnvelopeTests(unittest.TestCase):

    def test_identity_mapping_is_exact(self) -> None:
        record = reference.mapping_record(19200, 1, 1)
        self.assertEqual(record["target_samples"], 19200)
        self.assertTrue(record["identity_exact"])

    def test_speed_up_mapping(self) -> None:
        record = reference.mapping_record(19200, 5, 4)
        self.assertEqual(record["target_samples"], 15360)

    def test_speed_down_mapping(self) -> None:
        record = reference.mapping_record(19200, 9, 10)
        self.assertEqual(record["target_samples"], 21333)

    def test_mapping_is_bounded(self) -> None:
        record = reference.mapping_record(19200, 4, 5)
        self.assertTrue(record["bounded"])
        self.assertTrue(record["monotone"])

    def test_mapping_digest_is_stable(self) -> None:
        first = reference.mapping_record(19200, 3, 2)
        second = reference.mapping_record(19200, 3, 2)
        self.assertEqual(first["mapping_sha256"], second["mapping_sha256"])
        self.assertEqual(len(first["mapping_sha256"]), 64)

    def test_envelope_is_not_audio(self) -> None:
        record = reference.envelope()
        self.assertFalse(record["synthesizes_audio"])
        self.assertTrue(record["not_candidate"])
        self.assertEqual(record["case_count"], 5)


class EvidenceTests(unittest.TestCase):

    def test_absence_probes_all_absent(self) -> None:
        summary = reference.absence_summary()
        self.assertTrue(summary["summary"]["all_absent"])
        self.assertEqual(summary["summary"]["present_count"], 0)

    def test_absence_probe_count(self) -> None:
        self.assertEqual(reference.absence_summary()["summary"]["probe_count"],
                         len(reference.ABSENCE_PROBES))

    def test_source_phrases_present(self) -> None:
        self.assertTrue(reference.snippet_summary()["all_present"])

    def test_geometry_is_installed_v0(self) -> None:
        self.assertEqual(reference.build_contract()["public_v0_geometry"], {
            "sample_rate_hz": 16000, "channels": 1, "frame_samples": 160,
            "sample_format": "float32", "unchanged": True})

    def test_candidate_geometry_not_verified(self) -> None:
        self.assertFalse(reference.build_report()["candidate_geometry_verified"])

    def test_board_row_is_identity_projection(self) -> None:
        row = reference.board_row_projection()
        self.assertEqual(set(row), set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(row["id"], reference.TASK)

    def test_linked_rows_cover_dependencies(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))

    def test_board_bytes_not_pinned(self) -> None:
        self.assertFalse(reference.boundary_record()["board_file_pinned"])

    def test_source_pin_digest_is_stable(self) -> None:
        for relative, expected in reference.SOURCE_PINS.items():
            self.assertEqual(reference.sha256_file(
                reference.AUDIO_ROOT / relative), expected)

    def test_boundary_pin_digest_is_stable(self) -> None:
        for relative, expected in reference.BOUNDARY_PINS.items():
            self.assertEqual(reference.sha256_file(
                reference.WORKTREE / relative), expected)


class ArtifactTests(unittest.TestCase):

    def test_contract_canonical_bytes(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(contract, reference.read_strict_json(
            HERE / "contract.json"))

    def test_report_canonical_bytes(self) -> None:
        payload, digest = reference.canonical_report(reference.build_report())
        self.assertEqual((HERE / "report.json").read_bytes(),
                         payload.encode("ascii"))
        self.assertEqual((HERE / "report.json.sha256").read_text(),
                         digest + "  report.json\n")

    def test_contract_and_report_have_no_floats(self) -> None:
        reference.assert_no_float(reference.build_contract())
        reference.assert_no_float(reference.build_report())

    def test_report_is_defer_incomplete_unqualified(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")

    def test_all_release_gates_blocked(self) -> None:
        gates = reference.build_report()["release_gates"]
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(not gate["qualifies"] for gate in gates))

    def test_readme_tables_match_live_bytes(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertEqual(reference.readme_table_errors(text), [])

    def test_reopen_condition_is_recorded(self) -> None:
        self.assertIn("OFF-by-default", reference.REOPEN_CONDITION)
        self.assertEqual(reference.build_report()["reopen_condition"],
                         reference.REOPEN_CONDITION)

    def test_expected_file_set(self) -> None:
        observed = {path.name for path in HERE.iterdir() if path.is_file()}
        self.assertEqual(observed, set(reference.EXPECTED_DIR_FILES))

    def test_sources_manifest_has_no_board_bytes(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        self.assertNotIn("plan/swarm/TASKS.json", text)

    def test_scope_regression_tests_present(self) -> None:
        for name in verify.SCOPE_REGRESSION_TESTS:
            self.assertTrue(hasattr(ScopeGateTests, name))


if __name__ == "__main__":
    unittest.main()
