# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest coverage for the sherpa-onnx readiness package.

No skips, no network, no runtime import, no model load, no audio and no
mutable shared-state writes. The three scope tests build disposable git
repositories in temporary directories.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class ConstantTests(unittest.TestCase):
    def test_task_identity(self) -> None:
        self.assertEqual(reference.TASK, "SDK-SHERPA-ONNX")
        self.assertEqual(reference.COMPONENT_ID, "sherpa-onnx")
        self.assertEqual(reference.MODE, "feasibility")
        self.assertEqual(reference.PROFILE, "rate")
        self.assertEqual(reference.TASK_PREFIX,
                         "docs/task-evidence/sherpa-onnx/")

    def test_disposition_is_strict(self) -> None:
        self.assertEqual(reference.DECISION, "DEFER")
        self.assertEqual(reference.STATUS, "incomplete")
        self.assertEqual(reference.EVIDENCE_STATUS, "incomplete")
        self.assertEqual(reference.QUALIFICATION_STATUS, "not_qualified")
        self.assertEqual(reference.REQUIRED_INTERPRETER, "3.12.16")

    def test_base_and_branch(self) -> None:
        self.assertEqual(reference.BASE_COMMIT,
                         "f93d25f3d455a4278030d1bf0a3338dc6f8b95fe")
        self.assertEqual(reference.BRANCH, "swarm/SDK-SHERPA-ONNX")
        self.assertEqual(reference.REVIEWER, "reviewer-SHERPA-ONNX")

    def test_no_float_in_contract_or_report(self) -> None:
        reference.assert_no_float(reference.build_contract())
        reference.assert_no_float(reference.build_report())

    def test_non_claims_are_boundary_only(self) -> None:
        self.assertEqual(len(reference.NON_CLAIMS), 8)
        text = " ".join(reference.NON_CLAIMS)
        for phrase in ("No sherpa-onnx source checkout", "No model",
                       "No streaming capability", "No provider",
                       "No download", "DEFER"):
            self.assertIn(phrase, text)


class PinTests(unittest.TestCase):
    def test_source_pin_count(self) -> None:
        self.assertEqual(len(reference.SOURCE_PINS), 23)

    def test_boundary_pin_count(self) -> None:
        self.assertEqual(len(reference.BOUNDARY_PINS), 14)

    def test_all_source_pins_are_live(self) -> None:
        rows = reference.pin_rows(reference.SOURCE_PINS,
                                  reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.SOURCE_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_all_boundary_pins_are_live(self) -> None:
        rows = reference.pin_rows(reference.BOUNDARY_PINS,
                                  reference.WORKTREE)
        self.assertEqual(len(rows), len(reference.BOUNDARY_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_model_tree_is_exact(self) -> None:
        digest, count, size = reference.tree_digest(
            reference.AUDIO_ROOT / reference.MODEL_PREFIX)
        self.assertEqual(digest, reference.MODEL_TREE_SHA256)
        self.assertEqual(count, 9)
        self.assertEqual(size, 256603197)
        self.assertEqual(sum(reference.MODEL_FILE_BYTES.values()), size)

    def test_model_files_are_pinned(self) -> None:
        for relative, size in reference.MODEL_FILE_BYTES.items():
            path = reference.AUDIO_ROOT / reference.MODEL_PREFIX / relative
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(reference.sha256_file(path),
                             reference.SOURCE_PINS[
                                 reference.MODEL_PREFIX + "/" + relative])

    def test_model_has_no_license_or_card(self) -> None:
        root = reference.AUDIO_ROOT / reference.MODEL_PREFIX
        for name in ("LICENSE", "LICENSE.txt", "NOTICE", "COPYING", "README",
                     "README.md"):
            self.assertFalse((root / name).exists(), name)

    def test_runtime_metadata_is_pinned(self) -> None:
        assets = reference.present_assets()
        runtime = assets["runtime"]
        self.assertEqual(runtime["version"], "2.0.1")
        self.assertTrue(runtime["wheel_dist_info_license_text_present"])
        self.assertFalse(runtime["wheel_archive_present"])
        self.assertFalse(runtime["lockfile_present"])
        self.assertFalse(runtime["imported_or_executed"])

    def test_absence_probes_are_all_absent(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["probe_count"], 15)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])


class StrictJsonTests(unittest.TestCase):
    def test_canonical_bytes_are_sorted_and_compact(self) -> None:
        document = {"b": 1, "a": [True, None, "x"]}
        self.assertEqual(reference.canonical_text(document),
                         '{"a":[true,null,"x"],"b":1}\n')

    def test_canonical_bytes_reject_nan(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"a": float("nan")})

    def test_no_floats_rejects_nested_float(self) -> None:
        with self.assertRaises(ValueError):
            reference.assert_no_float({"a": [{"b": 1.5}]})

    def test_strict_json_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text('{"a":1,"a":2}\n', encoding="utf-8")
            with self.assertRaises(ValueError) as raised:
                reference.read_strict_json(path)
            self.assertIn("duplicate_key", str(raised.exception))

    def test_strict_json_rejects_nonfinite_literal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "nonfinite.json"
            path.write_text('{"a":NaN}\n', encoding="utf-8")
            with self.assertRaises(ValueError) as raised:
                reference.read_strict_json(path)
            self.assertIn("nonfinite_json", str(raised.exception))

    def test_object_digest_is_stable(self) -> None:
        expected = hashlib.sha256(b'{"a":1}\n').hexdigest()
        self.assertEqual(reference.object_digest({"a": 1}), expected)


class BoardAndProfileTests(unittest.TestCase):
    def test_board_row_projection_is_stable(self) -> None:
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(row["id"], reference.TASK)
        self.assertEqual(tuple(row), reference.BOARD_ROW_FIELDS)
        self.assertEqual(row["component"], reference.COMPONENT_ID)

    def test_linked_rows(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual(len(rows), 4)
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))

    def test_profile_row_phrases(self) -> None:
        check = reference.profile_row_check()
        self.assertEqual(check["row_count"], 1)
        self.assertTrue(check["phrases_present"])
        self.assertEqual(check["sha256"],
                         reference.SOURCE_PINS[
                             reference.PROFILE_SOURCE_REL])

    def test_rate_profile_rows_are_all_blocked(self) -> None:
        profile = reference.rate_profile()
        self.assertEqual(len(profile["requirement_rows"]), 8)
        self.assertTrue(all(row["status"] == "blocked"
                            and row["qualifies"] is False
                            for row in profile["requirement_rows"]))
        self.assertFalse(profile["row_summary"]["profile_satisfied"])


class BlockersAndGatesTests(unittest.TestCase):
    def test_gate_count_and_status(self) -> None:
        gates = reference.release_gates()
        self.assertEqual([row["id"] for row in gates],
                         ["RG-%02d" % number for number in range(1, 9)])
        self.assertTrue(all(row["status"] == "blocked"
                            and row["qualifies"] is False
                            and row["reopen_condition"]
                            for row in gates))

    def test_blocker_count_and_links(self) -> None:
        blockers = reference.exact_blockers()
        artifacts = {row["id"] for row in reference.required_artifacts()}
        gates = {row["id"] for row in reference.release_gates()}
        self.assertEqual(len(blockers), 6)
        for row in blockers:
            self.assertEqual(row["status"], "open")
            self.assertFalse(row["qualifies"])
            self.assertIn(row["artifact_id"], artifacts)
            self.assertTrue(row["reopen_condition"])
            self.assertTrue(all(gate in gates for gate in row["linked_gates"]))

    def test_artifacts_have_no_invented_identity(self) -> None:
        for row in reference.required_artifacts():
            self.assertTrue(row["blocked"])
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertIsNone(row["sha256"])
            self.assertIsNone(row["bytes"])
            self.assertIsNone(row["revision"])

    def test_qualification_is_not_qualified(self) -> None:
        qualification = reference.qualification()
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertTrue(qualification["all_release_gates_blocked"])
        for key in ("real_result_present", "source_present",
                    "token_timestamps_verified", "benchmark_result",
                    "release_claim", "missing_result_promoted"):
            self.assertIs(qualification[key], False)

    def test_installed_geometry_is_unchanged(self) -> None:
        geometry = reference.public_v0_geometry()
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertEqual(geometry["nanoseconds_per_sample"], 62500)
        self.assertTrue(geometry["preserved"])
        self.assertFalse(geometry["sherpa_onnx_mapping_present"])


class AdmissionTests(unittest.TestCase):
    def test_control_manifest_is_accepted(self) -> None:
        self.assertEqual(reference.validate_manifest(
            reference.control_manifest())["task_id"], reference.TASK)

    def test_all_negative_cases_are_rejected(self) -> None:
        cases = reference.admission_cases()["cases"]
        self.assertEqual(len(cases), 44)
        self.assertEqual(cases[0]["status"], "accepted")
        self.assertEqual(cases[0]["class"],
                         "synthetic_schema_control_not_evidence")
        self.assertFalse(cases[0]["qualifies"])
        for case in cases[1:]:
            self.assertEqual(case["status"], "rejected")
            self.assertTrue(case["code"])
            self.assertTrue(case["state_unchanged"])
            self.assertFalse(case["qualifies"])

    def test_admission_summary_is_fail_closed(self) -> None:
        summary = reference.admission_cases()["summary"]
        self.assertEqual(summary["case_count"], 44)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["rejected_count"], 43)
        self.assertEqual(summary["qualifying_results"], 0)
        for key in ("runtime_invoked", "weights_loaded", "model_executed",
                    "audio_read", "network_used",
                    "state_advanced_on_rejection"):
            self.assertIs(summary[key], False)

    def test_embedded_asset_rejected(self) -> None:
        manifest = reference._mutate(reference.control_manifest(),
                                     ("assets", 0, "storage"), "embedded")
        with self.assertRaises(ValueError) as raised:
            reference.validate_manifest(manifest)
        self.assertIn("asset_storage", str(raised.exception))

    def test_no_audio_or_model_in_manifest(self) -> None:
        text = json.dumps(reference.control_manifest())
        for token in (".wav", ".onnx", "audio_bytes", "model_bytes",
                      "weights", "waveform"):
            self.assertNotIn(token, text)


class GeometryControlTests(unittest.TestCase):
    def test_final_partial_windows_are_conserved(self) -> None:
        control = reference.geometry_control()
        self.assertEqual(control["case_count"], 160)
        self.assertTrue(all(row["conserved"] for row in control["cases"]))
        self.assertFalse(control["qualifies"])

    def test_geometry_has_no_audio(self) -> None:
        control = reference.geometry_control()
        self.assertEqual(control["sample_format"], "f32")
        self.assertEqual(control["nanoseconds_per_frame"], 10000000)
        self.assertEqual(control["assumed_buffering_delay_samples"], 0)


class ReadmeTableTests(unittest.TestCase):
    def test_readme_tables_are_present(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))
        self.assertEqual(counts["artifacts"],
                         len(reference.LOCAL_FILES) - 1)

    def test_readme_tables_are_up_to_date(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertEqual(text, reference.update_readme_tables(text))

    def test_malformed_digest_table_rejected(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        original = reference.SOURCE_PINS[
            "audio-benchmark-platform/plan/INVENTORY.json"]
        malformed = text.replace(original, "A" * 64, 1)
        with self.assertRaises(ValueError) as raised:
            reference.parse_readme_digest_tables(malformed)
        self.assertIn("malformed_digest", str(raised.exception))


class ScopeTests(unittest.TestCase):
    """Three regression tests for newest-merge-base scope enforcement."""

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
        (task / "README.md").write_text("task package\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "task package")
        return repo

    def _add_siblings(self, repo: Path) -> None:
        for name in ("sibling-alpha", "sibling-beta"):
            sibling = repo / "docs/task-evidence" / name
            sibling.mkdir(parents=True)
            (sibling / "report.json").write_text("{}\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "unrelated sibling packages")

    def test_sibling_merges_after_base_pass_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            historical = self._git(repo, "rev-parse", "HEAD")
            self._add_siblings(repo)
            head = self._git(repo, "rev-parse", "HEAD")
            self.assertEqual(reference.scope_base(repo), head)
            self.assertEqual(reference.scope_changed_paths(repo, head), [])
            self.assertEqual(reference.scope_error_codes(repo), [])
            older = reference.scope_changed_paths(repo, historical)
            self.assertIn("docs/task-evidence/sibling-alpha/report.json",
                          older)
            self.assertTrue(reference.scope_violations(older))

    def test_out_of_scope_branch_edit_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._add_siblings(repo)
            self._git(repo, "checkout", "-q", "-b",
                      "swarm/SDK-SHERPA-ONNX-scope")
            (repo / "CMakeLists.txt").write_text("changed\n", encoding="utf-8")
            self._git(repo, "add", "CMakeLists.txt")
            self._git(repo, "commit", "-qm", "out of scope edit")
            base = reference.scope_base(repo)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, ["CMakeLists.txt"])
            self.assertEqual(reference.scope_violations(paths),
                             ["CMakeLists.txt"])
            self.assertEqual(reference.scope_error_codes(repo),
                             ["base_out_of_scope_change:CMakeLists.txt"])

    def test_missing_base_ref_emits_scope_base_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "branch", "-m", "detached-work")
            self.assertIsNone(reference.scope_base(repo))
            self.assertEqual(reference.scope_error_codes(repo),
                             ["scope_base_unavailable"])

    def test_scope_violations_uses_task_prefix(self) -> None:
        paths = [reference.TASK_PREFIX + "README.md", "CONTRACTS.md"]
        self.assertEqual(reference.scope_violations(paths),
                         ["CONTRACTS.md"])


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
                             reference.FORBIDDEN_SUFFIXES, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name,
                             {"CMakeLists.txt", "provider.json",
                              "adapter.json", "asset.json"})

    def test_python_spdx_headers(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8")
                             .splitlines()[:4])
            # REUSE-IgnoreStart
            self.assertIn("SPDX-License-Identifier: Apache-2.0", head)
            # REUSE-IgnoreEnd
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          head)

    def test_license_sidecars(self) -> None:
        for name in ("contract.json", "report.json", "report.json.sha256",
                     "SOURCES.sha256"):
            sidecar = HERE / (name + ".license")
            self.assertTrue(sidecar.is_file(), name)
            text = sidecar.read_text(encoding="utf-8")
            # REUSE-IgnoreStart
            self.assertIn("SPDX-License-Identifier: Apache-2.0", text)
            # REUSE-IgnoreEnd
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          text)

    def test_local_pins_cover_every_file(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        paths = {path for _, path in reference.parse_pin_lines(text)}
        for name in reference.LOCAL_FILES:
            self.assertIn(reference.TASK_PREFIX + name, paths)
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", paths)
        self.assertEqual(len(paths), len(reference.parse_pin_lines(text)))


if __name__ == "__main__":
    unittest.main()
