# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local tests for SDK-LACO-SENET evidence, including scope regressions."""

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
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

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
        with self.assertRaises(ValueError):
            reference.loads_strict('[1,2]')

    def test_canonical_bytes_are_stable(self) -> None:
        value = {"b": [1, 2], "a": {"d": True, "c": None}}
        self.assertEqual(reference.canonical_bytes(value),
                         b'{"a":{"c":null,"d":true},"b":[1,2]}')
        self.assertEqual(reference.object_digest(value),
                         hashlib.sha256(reference.canonical_bytes(value))
                         .hexdigest())


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
        changed["blocked_reason"] = "changed"
        self.assertEqual(reference._project(row, True),
                         reference._project(changed, True))

    def test_stable_identity_change_changes_projection(self) -> None:
        projection = reference.board_row_projection()
        changed = copy.deepcopy(projection)
        changed["title"] = "LaCo-SENet changed"
        self.assertNotEqual(reference.board_row_digest(projection),
                            reference.board_row_digest(changed))

    def test_mutable_board_not_pinned(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        self.assertNotIn(reference.BOARD_TASK_ROW, text)
        self.assertNotIn("source:" + reference.BOARD_TASK_ROW, text)


class AbsenceTests(unittest.TestCase):
    def test_all_fixed_probes_absent(self) -> None:
        probes = reference.all_probes()
        self.assertEqual(len(probes), 24)
        self.assertEqual([row["path"] for row in probes
                          if row["present"]], [])
        summary = reference.absence_summary(probes)
        self.assertTrue(summary["all_probes_absent"])
        self.assertEqual(summary["present_count"], 0)
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["network_used"])
        self.assertFalse(summary["weights_loaded"])
        self.assertFalse(summary["model_executed"])

    def test_absence_summary_counts(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["probe_count"], 24)
        self.assertEqual(summary["workspace_probe_count"], 15)
        self.assertEqual(summary["worktree_probe_count"], 5)
        self.assertEqual(summary["home_probe_count"], 4)

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


class AssetRegistryTests(unittest.TestCase):
    def test_register_has_no_laco_entry(self) -> None:
        registry = reference.asset_registry()
        self.assertEqual(registry["candidate_count"], 20)
        self.assertFalse(registry["laco_entry_present"])
        self.assertEqual(registry["laco_candidate_ids"], [])
        self.assertFalse(registry["asset_identity_available_for_laco"])

    def test_evidence_inputs_are_real_and_ordered(self) -> None:
        rows = reference.evidence_inputs()
        self.assertEqual(len(rows), 8)
        self.assertEqual([row["path"] for row in rows],
                         list(reference.EVIDENCE_INPUT_PATHS))
        mentions = {row["path"]: row["mentions_laco"] for row in rows}
        self.assertTrue(mentions[reference.RECORDED_READINESS_REPORT])
        self.assertTrue(
            mentions["research/noise_suppression_candidate_census.md"])
        self.assertTrue(
            mentions["research/voice-enhancement-20261101/"
                     "candidate_matrix.csv"])
        self.assertFalse(
            mentions["research/noise_suppression_assets_20261027.json"])

    def test_every_input_is_not_a_result(self) -> None:
        for row in reference.evidence_inputs():
            self.assertFalse(row["is_result"], row["path"])


class RecordedIdentityTests(unittest.TestCase):
    def test_checkpoint_identity_is_recorded_not_verified(self) -> None:
        recorded = reference.recorded_identity_block()
        self.assertEqual(recorded["checkpoint_bytes"], 5707759)
        self.assertEqual(recorded["checkpoint_sha256"],
                         reference.RECORDED_CHECKPOINT_SHA256)
        self.assertEqual(len(recorded["checkpoint_sha256"]), 64)
        self.assertEqual(recorded["model_revision"],
                         reference.MODEL_REVISION)
        self.assertFalse(recorded["locally_present"])
        self.assertFalse(recorded["locally_verified"])
        self.assertFalse(recorded["digest_verified_locally"])
        self.assertFalse(recorded["admitted_as_result"])
        self.assertFalse(recorded["qualifies"])

    def test_checkpoint_bytes_are_not_in_the_package(self) -> None:
        for path in HERE.iterdir():
            self.assertNotEqual(path.suffix.lower(), ".th", path.name)
            self.assertNotIn(path.suffix.lower(),
                             reference.FORBIDDEN_SUFFIXES, path.name)

    def test_reported_metrics_are_labelled(self) -> None:
        metrics = reference.reported_metrics_block()
        self.assertEqual(metrics["status"],
                         "source_reported_not_measured_here")
        self.assertEqual(metrics["pesq"], "3.3286")
        self.assertEqual(metrics["stoi"], "0.9522")
        self.assertFalse(metrics["admitted_as_result"])
        self.assertFalse(metrics["qualifies"])

    def test_source_license_is_unresolved(self) -> None:
        upstream = reference.upstream_record()
        self.assertIsNone(upstream["source_license_spdx"])
        self.assertEqual(upstream["source_license_status"],
                         "unresolved_no_license_entry")
        self.assertFalse(upstream["model_card_license_verified_locally"])
        self.assertIsNone(upstream["source_immutable_revision"])

    def test_geometry_does_not_invent_streaming_parameters(self) -> None:
        geometry = reference.task_geometry()
        self.assertEqual(geometry["reported_channels"], 1)
        self.assertEqual(geometry["reported_sample_rate_hz"], 16000)
        self.assertEqual(geometry["reported_latency_setting_count"], 9)
        self.assertEqual(geometry["reported_checkpoint_count"], 27)
        for key in ("frame_samples", "hop_samples", "chunk_samples",
                    "stft_window_samples", "lookahead_samples",
                    "state_reset_policy", "pacing_policy",
                    "reported_latency_settings_ms"):
            self.assertIsNone(geometry[key], key)
        self.assertFalse(geometry["exact_geometry_verified"])


class ManifestTests(unittest.TestCase):
    def test_control_accepted_but_not_qualified(self) -> None:
        result = reference.validate_manifest(reference._manifest_control())
        self.assertEqual(result["status"], "accepted")
        self.assertFalse(result["qualifies"])
        self.assertGreater(result["checks"], 50)

    def test_every_admission_case_is_accounted(self) -> None:
        admission = reference.admission_controls()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], len(admission["cases"]))
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["rejected_count"],
                         summary["case_count"] - 1)
        self.assertTrue(summary["all_adverse_cases_rejected"])
        for case in admission["cases"]:
            self.assertFalse(case["qualifies"], case["id"])
            if case["status"] == "rejected":
                self.assertTrue(case["state_unchanged"])
                self.assertTrue(case["code"])
                self.assertTrue(case["synthetic_schema_control"])

    def test_missing_and_unknown_fields(self) -> None:
        manifest = reference._manifest_control()
        manifest.pop("source")
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "missing_field")
        manifest = reference._manifest_control()
        manifest["extra"] = True
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "unknown_field")

    def test_stereo_geometry_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["geometry"]["channels"] = 2
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "invalid_channels")

    def test_wrong_rate_and_mode_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["geometry"]["sample_rate_hz"] = 48000
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "invalid_sample_rate")
        manifest = reference._manifest_control()
        manifest["geometry"]["mode"] = "offline_whole_utterance"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "scope_mismatch")

    def test_wrong_interpreter_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["runtime"]["python_version"] = "3.12.15"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "wrong_python_version")

    def test_rate_mismatch_and_false_rights_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["input"]["sample_rate_hz"] = 8000
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "rate_mismatch")
        manifest = reference._manifest_control()
        manifest["rights"]["output_use"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "rights_not_cleared")

    def test_unconsented_input_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["input"]["consent"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "rights_not_cleared")

    def test_unresolved_source_license_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["source"]["license_spdx"] = "NOASSERTION"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "unresolved_value")

    def test_missing_state_reset_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["geometry"]["state_reset"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "missing_state_reset")

    def test_float_and_raw_cases_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["geometry"]["lookahead_samples"] = 200.0
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "float_not_allowed")
        for raw, code in (
                ('{"a":1,"a":2}', "duplicate_json_key"),
                ('{"a":NaN}', "nonfinite_json"),
                ('{"a":Infinity}', "nonfinite_json")):
            with self.subTest(code=code):
                with self.assertRaises(ValueError) as caught:
                    reference.loads_strict(raw)
                self.assertEqual(str(caught.exception).split(":", 1)[0],
                                 code)

    def test_manifest_contract_flags(self) -> None:
        value = reference.admission_contract_block()
        self.assertEqual(value["exact_interpreter"], "3.12.16")
        self.assertEqual(value["required_channels"], 1)
        self.assertEqual(value["required_sample_rate_hz"], 16000)
        self.assertEqual(value["required_mode"], "streaming_lookahead")
        self.assertFalse(value["accepted_control_qualifies"])
        self.assertFalse(value["runtime_or_weights_invoked"])
        self.assertTrue(value["manifest_validation_only"])


class ContractTests(unittest.TestCase):
    def test_contract_validates(self) -> None:
        value = contract()
        reference.validate_contract(value)
        self.assertEqual(value["decision"], "DEFER")
        self.assertEqual(value["status"], reference.STATUS)
        self.assertEqual(value["qualification_status"], "not_qualified")

    def test_eight_blocked_gates(self) -> None:
        gates = contract()["release_gates"]
        self.assertEqual(len(gates), 8)
        for index, gate in enumerate(gates, 1):
            self.assertEqual(gate["id"], "RG-%02d" % index)
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertEqual(gate["linked_row"], reference.TASK)
            self.assertTrue(gate["reopen_condition"])

    def test_six_open_blockers_and_seven_artifacts(self) -> None:
        value = contract()
        self.assertEqual(len(value["exact_blockers"]), 6)
        self.assertEqual(len(value["required_artifacts"]), 7)
        artifact_ids = {row["id"] for row in value["required_artifacts"]}
        gate_ids = {row["id"] for row in value["release_gates"]}
        for blocker in value["exact_blockers"]:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(set(blocker["linked_gates"]) <= gate_ids)

    def test_artifacts_are_absent_without_invented_identity(self) -> None:
        for row in contract()["required_artifacts"]:
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertTrue(row["blocked"])
            self.assertIsNone(row["sha256"])
            self.assertIsNone(row["revision"])
            self.assertIsNone(row["bytes"])

    def test_upstream_record_keeps_license_unresolved(self) -> None:
        upstream = contract()["upstream_record"]
        self.assertEqual(upstream["source_repository"],
                         "https://github.com/yskim3271/LaCo-SENet")
        self.assertEqual(upstream["model_repository"],
                         reference.MODEL_REPOSITORY)
        self.assertEqual(upstream["model_revision"],
                         reference.MODEL_REVISION)
        self.assertIsNone(upstream["source_immutable_revision"])
        self.assertFalse(upstream["source_revision_pin_available"])
        self.assertFalse(upstream["model_revision_locally_verified"])
        self.assertEqual(upstream["checkpoint_count_reported"], 27)

    def test_boundary_all_false_except_task_local(self) -> None:
        scope = contract()["scope"]
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key != "task_local_only":
                self.assertFalse(value, key)
        boundary = contract()["boundary"]
        self.assertTrue(all(value is False for value in boundary.values()))


class ReportTests(unittest.TestCase):
    def test_no_floats(self) -> None:
        reference.assert_no_float(report())

    def test_decision_status_and_qualification(self) -> None:
        value = report()
        self.assertEqual(value["decision"], "DEFER")
        self.assertEqual(value["status"], "proposal_only_incomplete")
        self.assertEqual(value["evidence_status"], "incomplete")
        self.assertEqual(value["qualification_status"], "not_qualified")
        self.assertTrue(value["proposal_only"])
        self.assertTrue(value["incomplete"])
        qualification = value["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertTrue(qualification["all_release_gates_blocked"])
        self.assertTrue(qualification["recorded_identity_only"])
        self.assertFalse(qualification["missing_result_promoted"])
        self.assertFalse(qualification["peer_result_inherited"])
        for key in ("source_present", "exact_source_identity",
                    "source_license_verified", "runtime_present",
                    "weights_present_locally", "weights_identity_verified",
                    "rights_cleared_cohort", "streaming_geometry_verified",
                    "implementation_present",
                    "reference_execution_result",
                    "enhancement_profile_result", "listening_result",
                    "device_timing_result", "benchmark_result",
                    "release_claim"):
            self.assertFalse(qualification[key], key)

    def test_contract_digest_and_copies(self) -> None:
        value = report()
        self.assertEqual(value["contract_sha256"],
                         reference.object_digest(contract()))
        for report_key, contract_key in (
                ("disposition", "disposition"),
                ("boundary", "boundary"),
                ("scope", "scope"),
                ("exact_scope", "exact_scope"),
                ("task_geometry", "task_geometry"),
                ("upstream_record", "upstream_record"),
                ("recorded_identity", "recorded_identity"),
                ("reported_metrics", "reported_metrics"),
                ("asset_registry", "asset_registry"),
                ("required_artifacts", "required_artifacts"),
                ("exact_blockers", "exact_blockers"),
                ("gates", "release_gates"),
                ("qualification", "qualification"),
                ("enhancement_profile", "enhancement_profile"),
                ("rights_gap", "rights_gap")):
            self.assertEqual(value[report_key], contract()[contract_key],
                             report_key)

    def test_linked_identity(self) -> None:
        identity = report()["linked_row_identity"]
        self.assertEqual(identity["projection"],
                         reference.board_row_projection())
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest())
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["linked_rows_sha256"],
                         reference.linked_rows_digest())

    def test_profile_rows_blocked(self) -> None:
        profile = report()["enhancement_profile"]
        rows = profile["requirement_rows"]
        self.assertEqual(len(rows), 8)
        self.assertEqual(profile["row_summary"]["real_result_count"], 0)
        self.assertFalse(profile["row_summary"]["profile_satisfied"])
        self.assertEqual(profile["row_summary"]["blocked_count"], 7)
        self.assertEqual(profile["row_summary"]["documented_count"], 1)
        self.assertTrue(profile["profile_source_check"][
            "all_phrases_present"])
        for row in rows:
            self.assertIn(row["status"], ("blocked", "documented"))

    def test_canonical_roundtrip(self) -> None:
        text, digest = reference.canonical_report()
        self.assertEqual(text.encode("ascii"),
                         reference.canonical_bytes(report()))
        self.assertEqual(digest,
                         hashlib.sha256(text.encode("ascii")).hexdigest())
        parsed = reference.parse_strict_json_text(text.encode("ascii"))
        self.assertEqual(parsed, report())

    def test_absence_and_no_peer_promotion(self) -> None:
        value = report()
        self.assertEqual(value["absence_evidence"]["summary"]["present_count"],
                         0)
        for row in value["peer_evidence"]:
            self.assertFalse(row["admitted_as_result"])
            self.assertFalse(row["inherited_metrics"])
        for row in value["historical_evidence"]:
            self.assertFalse(row["admitted_as_result"])

    def test_source_and_boundary_pins_verified(self) -> None:
        value = report()
        for row in value["source_pins"] + value["boundary_pins"]:
            self.assertTrue(row["verified"], row["path"])
            self.assertEqual(row["sha256"], row["actual"])


class ReadmeDigestTests(unittest.TestCase):
    def test_readme_tables_verify(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))
        self.assertEqual(counts["artifacts"],
                         len(reference.expected_readme_keys()["artifacts"]))

    def test_readme_table_update_idempotent(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        once = reference.update_readme_tables(text)
        twice = reference.update_readme_tables(once)
        self.assertEqual(once, twice)

    def test_stale_and_malformed_rows_rejected(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        key, digest = reference.parse_readme_digest_tables(text)["source"][0]
        stale = text.replace(f"| `{key}` | `{digest}` |",
                             f"| `{key}` | `{'0' * 64}` |", 1)
        with self.assertRaises(ValueError):
            reference.verify_readme_digests(stale)
        malformed = text.replace(
            f"| `{key}` | `{digest}` |", f"| `{key}` | `short` |", 1)
        with self.assertRaises(ValueError):
            reference.parse_readme_digest_tables(malformed)


class ScopeTests(unittest.TestCase):
    """Regression coverage for the merge-base scope comparison."""

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
            (sibling / "verify.py").write_text("# sibling\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "unrelated sibling packages")

    def test_sibling_additions_after_base_pass_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            historical = self._git(repo, "rev-parse", "HEAD")
            self._add_siblings(repo)
            head = self._git(repo, "rev-parse", "HEAD")

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
            self._git(repo, "checkout", "-q", "-b",
                      "swarm/SDK-LACO-SENET-scope")
            (repo / "CMakeLists.txt").write_text("changed\n", encoding="utf-8")
            self._git(repo, "add", "CMakeLists.txt")
            self._git(repo, "commit", "-qm", "out of scope edit")

            base = reference.scope_base(repo)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, ["CMakeLists.txt"])
            self.assertEqual(reference.scope_violations(paths),
                             ["CMakeLists.txt"])

    def test_missing_base_ref_is_not_silently_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "branch", "-m", "detached-work")
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
                             reference.FORBIDDEN_SUFFIXES, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name,
                             {"CMakeLists.txt", "provider.json",
                              "adapter.json", "asset.json"})

    def test_python_spdx_headers(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
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
        rows = reference.parse_pin_lines(text)
        paths = {path for _, path in rows}
        for name in reference.LOCAL_FILES:
            self.assertIn(reference.TASK_PREFIX + name, paths)
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", paths)
        self.assertEqual(len(rows), len(paths))

    def test_non_claims(self) -> None:
        self.assertEqual(len(reference.NON_CLAIMS), 8)
        text = " ".join(reference.NON_CLAIMS)
        for phrase in ("No model inference", "No benchmark", "DEFER",
                       "No network access", "No provider"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
