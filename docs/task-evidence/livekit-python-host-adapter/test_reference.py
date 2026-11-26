# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local LiveKit Python host-adapter package."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

TASK_PREFIX = reference.TASK_PREFIX
LOCAL_PINS = (
    "LICENSES.md",
    "README.md",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib", ".m4a",
    ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus", ".pcap", ".pcapng",
    ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wasm", ".wav", ".weights",
    ".whl",
}


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.read_strict_json(HERE / "report.json")
        cls.contract = reference.read_strict_json(HERE / "contract.json")

    def test_identity_and_disposition(self) -> None:
        for document in (self.report, self.contract):
            self.assertEqual(document["task"], reference.TASK)
            self.assertEqual(document["component"], reference.COMPONENT)
            self.assertEqual(document["repository"], "audio-sdk")
            self.assertEqual(document["mode"], "feasibility")
            self.assertEqual(document["profile"], "tool")
            self.assertEqual(document["status"], "proposal_only_incomplete")
            self.assertEqual(document["evidence_status"], "incomplete")
            self.assertEqual(document["decision"], "DEFER")
            self.assertEqual(document["defer_before"],
                             "any_livekit_host_adapter_exposure")
            self.assertEqual(document["qualification_status"],
                             "not_qualified")
            self.assertEqual(document["base_commit"], reference.BASE_COMMIT)
            self.assertEqual(document["branch"], reference.BRANCH)
            self.assertEqual(document["worktree"], reference.CLAIM_WORKTREE)
            self.assertEqual(document["reviewer"], reference.REVIEWER)
            self.assertEqual(document["write_scope"], reference.WRITE_SCOPE)
            self.assertIs(document["proposal_only"], True)
            self.assertIs(document["incomplete"], True)

    def test_no_floats_in_canonical_artifacts(self) -> None:
        reference.assert_no_float(self.report)
        reference.assert_no_float(self.contract)

    def test_host_source_blocker(self) -> None:
        host = self.report["host_source"]
        self.assertEqual(host["name"], "LiveKit Python host")
        self.assertIs(host["host_package_pair_pinned"], False)
        self.assertIsNone(host["host_package_version"])
        self.assertIsNone(host["host_package_sha256"])
        self.assertIs(host["host_package_imported"], False)
        self.assertIs(host["sdk_library_loaded"], False)
        self.assertEqual(host["host_geometry_status"], "unestablished")
        self.assertEqual(host["host_api_status"],
                         "unverified_no_pinned_package_or_api_record")
        self.assertEqual(host["host_license_status"],
                         "unverified_no_license_record_present")

    def test_geometry_is_not_asserted(self) -> None:
        geometry = self.report["geometry"]
        self.assertEqual(geometry["host_geometry_status"], "unestablished")
        self.assertIs(geometry["host_geometry_asserted"], False)
        self.assertIs(geometry["livekit_execution"], False)
        for key in ("livekit_frame_size_verified",
                    "livekit_sample_rate_verified",
                    "livekit_sample_format_verified",
                    "livekit_channel_count_verified",
                    "livekit_pacing_verified",
                    "event_loop_wait_verified"):
            self.assertIs(geometry[key], False, key)
        self.assertEqual(geometry["sdk_sample_rate_hz"], 16000)
        self.assertEqual(geometry["sdk_channels"], 1)
        self.assertEqual(geometry["sdk_frame_samples"], 160)
        self.assertEqual(geometry["host_shift_samples"], 480)
        self.assertEqual(geometry["startup_invalid_frames"], 3)
        self.assertEqual(geometry["wrong_lengths_rejected"], [161, 320, 800])
        self.assertIs(geometry["modeled_only"], True)

    def test_tool_profile_is_blocked(self) -> None:
        profile = self.report["tool_profile"]
        self.assertEqual(profile["name"], "tool")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["measured_workload_result"])
        self.assertEqual(len(profile["required_items"]),
                         len(reference.TOOL_REQUIREMENTS))
        for item in profile["required_items"]:
            self.assertIs(item["satisfied_for_qualification"], False)
            self.assertEqual(item["qualification_effect"], "none")
            self.assertIn(item["package_status"], {
                "blocked", "not_measured", "partial_synthetic",
                "separated_in_package_only"})

    def test_eight_blocked_gates_and_blockers(self) -> None:
        self.assertEqual([gate["id"] for gate in self.report["gates"]],
                         [f"RG-0{index}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in self.report["gates"]))
        self.assertEqual(
            [item["id"] for item in self.report["exact_blockers"]],
            [f"BLK-0{index}" for index in range(1, 9)])
        self.assertTrue(all(item["state"] == "open"
                            for item in self.report["exact_blockers"]))
        qualification = self.report["qualification"]
        self.assertEqual(qualification["blocked_gate_count"], 8)
        self.assertIs(qualification["candidate_qualified"], False)
        self.assertIs(qualification["no_missing_result_qualifies_candidate"],
                      True)

    def test_boundary_and_scope_flags(self) -> None:
        for document in (self.report, self.contract):
            for key, value in document["boundary"].items():
                if key == "descriptor_settings":
                    self.assertEqual(value, {})
                else:
                    self.assertIs(value, False, key)
            self.assertIs(document["scope"]["task_local_only"], True)
            for key, value in document["scope"].items():
                if key != "task_local_only":
                    self.assertIs(value, False, key)

    def test_absence_probes_all_absent(self) -> None:
        probes = self.report["absence_probes"]
        self.assertEqual(len(probes), len(reference.ABSENCE_PROBE_PATHS))
        self.assertTrue(all(item["present"] is False for item in probes))
        self.assertIs(self.report["absence_evidence"]["all_probes_absent"],
                      True)
        self.assertIs(self.report["asset_audit"]["qualified"], False)
        self.assertEqual(self.report["asset_audit"]["audit_result"], "absent")

    def test_module_absence_probes(self) -> None:
        modules = self.report["module_probes"]
        self.assertEqual(len(modules), len(reference.MODULE_PROBES))
        self.assertTrue(all(item["spec_present"] is False
                            for item in modules))
        self.assertIs(self.report["module_absence"]["all_modules_absent"],
                      True)

    def test_asset_requirements_are_absent(self) -> None:
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        for identifier in (
                "pinned_livekit_host_package_pair",
                "installed_sdk_python_binding",
                "host_api_and_geometry_record",
                "rights_cleared_host_audio",
                "host_adapter_evidence",
                "tool_acceptance_evidence",
                "independent_review"):
            self.assertEqual(requirements[identifier]["status"], "absent")
        self.assertIsNone(
            requirements["pinned_livekit_host_package_pair"]["revision"])
        self.assertIsNone(
            requirements["installed_sdk_python_binding"]["sha256"])

    def test_rights_gap_is_explicit(self) -> None:
        rights = self.report["rights_gap"]
        self.assertEqual(rights["status"], "blocked")
        self.assertIs(rights["rights_cleared_audio_present"], False)
        self.assertIs(rights["participant_media_scope_present"], False)
        self.assertIs(rights["room_or_token_present"], False)
        self.assertIs(rights["output_use_grant"], False)
        self.assertIs(rights["redistribution_grant"], False)

    def test_board_identity_is_stable_and_never_whole_file(self) -> None:
        projection = reference.board_row_projection()
        for document in (self.report, self.contract):
            identity = document["task_row_identity"]
            self.assertEqual(identity["stable_sha256"],
                             projection["stable_sha256"])
            self.assertEqual(identity["stable_fields"],
                             projection["stable_fields"])
            self.assertIs(identity["whole_file_hashed"], False)
        encoded = reference.canonical_text(self.report)
        self.assertNotRegex(encoded, r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"')

    def test_profile_source_is_tool(self) -> None:
        source = reference.profile_source()
        self.assertEqual(source["profile"], "Tool")
        self.assertEqual(source["key"], "tool")
        self.assertTrue(source["row"].startswith("| Tool |"))
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, source["row"])

    def test_acceptance_matrix_evidence(self) -> None:
        matrix = self.report["acceptance_matrix_evidence"]
        self.assertEqual(matrix["path"], reference.ACCEPTANCE_SOURCE_REL)
        self.assertIn("No pinned/tested LiveKit host package pair",
                      matrix["s09_row"])
        self.assertIn("S09 blocked", matrix["st11_row"])
        self.assertEqual(matrix["evidence_status"],
                         "recorded_absence_not_runtime_evidence")

    def test_source_reported_context_is_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"],
                         "source_reported_not_measured_here")
        self.assertIn("S09 LiveKit host", context["recorded_gap"])
        self.assertIsNone(self.report["candidate_metrics"])

    def test_feasibility_verification_records_blockers(self) -> None:
        feasibility = self.report["feasibility_verification"]
        self.assertEqual(feasibility["runnable_source"]["status"], "absent")
        self.assertEqual(feasibility["exact_assets"]["status"], "absent")
        self.assertEqual(feasibility["permitted_scope"]["status"],
                         "task_local_evidence_only")
        self.assertEqual(feasibility["permitted_scope"]["write_scope"],
                         reference.TASK_PREFIX)
        self.assertEqual(
            feasibility["host_adapter_geometry"]["sdk_status"],
            "source_verified")
        self.assertEqual(
            feasibility["host_adapter_geometry"]["host_status"],
            "unestablished")
        self.assertIs(
            feasibility["host_adapter_geometry"]["livekit_execution"], False)
        self.assertEqual(feasibility["matched_evidence"]["status"], "absent")
        self.assertIs(feasibility["matched_evidence"]["measured_workload"],
                      False)
        self.assertEqual(feasibility["conclusion"],
                         "defer_external_blocker")

    def test_caller_contract_is_strict(self) -> None:
        contract = self.report["caller_asset_contract"]
        self.assertEqual(contract["absent_behavior"],
                         "reject_before_processing")
        self.assertIs(contract["asset_is_vendored"], False)
        self.assertEqual(contract["required_python_version"], "3.12.16")
        self.assertEqual(contract["required_host_shift_samples"], 480)
        self.assertEqual(contract["required_sdk_contract_version"], "0.1")
        self.assertIs(
            contract["required_rights_cleared_audio_acknowledged"], True)
        self.assertEqual(contract["required_scope"],
                         "livekit_python_host_audio_adapter")
        self.assertEqual(contract["required_variant"],
                         "caller_clocked_paced_streaming")


class ConversionTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(reference.CONTROL_HOST_FRAME_SAMPLES, 480)
        self.assertEqual(reference.CONTROL_DECIMATION, 3)
        self.assertEqual(reference.CONTROL_SDK_FRAME_SAMPLES, 160)
        self.assertEqual(reference.HOST_SHIFT_SAMPLES, 480)
        self.assertEqual(reference.STARTUP_INVALID_SAMPLES, 480)

    def test_s16_frame_validation(self) -> None:
        good = reference.synthetic_host_frame()
        self.assertEqual(len(good), 480)
        self.assertEqual(reference.validate_s16_frame(good), good)
        for bad in (b"\x00\x00", [], None, [0] * 479 + [True],
                    [0] * 479 + [0.5], [0] * 479 + [32768],
                    [0] * 479 + [-32769], [0] * 161):
            with self.assertRaises(reference.InvalidInput):
                reference.validate_s16_frame(bad)

    def test_conversion_is_finite_and_160_samples(self) -> None:
        converted = reference.convert_host_frame(
            reference.synthetic_host_frame())
        self.assertEqual(len(converted), 160)
        self.assertTrue(all(math.isfinite(value) for value in converted))
        self.assertTrue(all(-1.0 <= value < 1.0 for value in converted))
        self.assertEqual(converted[0],
                         reference.synthetic_host_frame()[0] / 32768.0)

    def test_packing_is_exact(self) -> None:
        for frames in reference.CONTROL_FRAMES:
            row = reference.packing_accounting(frames)
            self.assertIs(row["exact"], True)
            self.assertEqual(row["host_samples"], frames * 480)
            self.assertEqual(row["sdk_samples"], frames * 160)
            self.assertEqual(row["host_duration_ms"], frames * 10)

    def test_shift_model(self) -> None:
        highpass = reference.shift_model("dsp.highpass80.v0")
        speex = reference.shift_model("speex.ns.v0")
        self.assertEqual(highpass["modeled_invalid_prefix_samples"], 960)
        self.assertEqual(speex["modeled_invalid_prefix_samples"], 1120)
        self.assertEqual(highpass["host_shift_ms"], 30)
        self.assertIs(highpass["measured"], False)
        with self.assertRaises(reference.InvalidInput):
            reference.shift_model("unknown.provider.v0")

    def test_wrong_lengths(self) -> None:
        decisions = {length: reference.wrong_length_decision(length)
                     for length in reference.WRONG_LENGTH_VECTORS}
        self.assertIs(decisions[160]["accepted"], True)
        for length in (159, 161, 320, 480, 800):
            self.assertIs(decisions[length]["accepted"], False, length)
        for length in reference.REQUIRED_REJECTED_LENGTHS:
            self.assertIs(decisions[length]["accepted"], False, length)
        with self.assertRaises(reference.InvalidInput):
            reference.wrong_length_decision(True)

    def test_packing_rejects_bad_counts(self) -> None:
        for value in (0, -1, True, 1.5, "3"):
            with self.assertRaises(reference.InvalidInput):
                reference.packing_accounting(value)

    def test_conversion_control_in_report(self) -> None:
        protocol = reference.read_strict_json(HERE / "report.json")[
            "reference_protocol"]
        self.assertEqual(protocol["conversion"]["sdk_output_samples"], 160)
        self.assertEqual(protocol["conversion"]["nonfinite_output_count"], 0)
        self.assertIs(
            protocol["conversion"]["float_values_retained_in_report"], False)
        self.assertIs(protocol["required_rejected_lengths_all_rejected"], True)


class AdmissionTests(unittest.TestCase):
    def test_positive_structural_control(self) -> None:
        result = reference.validate_caller_manifest(
            reference._existing_file_manifest())
        self.assertIs(result["accepted"], True)
        self.assertIs(result["host_package_imported"], False)
        self.assertIs(result["sdk_library_loaded"], False)
        self.assertIs(result["audio_read"], False)
        self.assertEqual(result["files_checked"],
                         len(reference.CALLER_FILE_PAIRS))
        self.assertEqual(result["directories_checked"],
                         len(reference.CALLER_DIR_FIELDS))
        self.assertEqual(result["integer_decimation"], 3)

    def test_adverse_cases_all_rejected(self) -> None:
        rows = reference.run_adverse_controls()
        self.assertEqual(len(rows), len(reference.ADVERSE_CASE_IDS))
        for row in rows:
            self.assertEqual(row["result"], "rejected", row)
        self.assertEqual(reference.ADVERSE_CASE_IDS,
                         tuple(row["case"] for row in rows))

    def test_missing_asset_rejected_before_processing(self) -> None:
        manifest = dict(reference._shape_only_manifest())
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(manifest)

    def test_wrong_scope_and_variant_rejected(self) -> None:
        base = reference._existing_file_manifest()
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(
                dict(base, scope="voice_conversion"))
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(
                dict(base, variant="offline_whole_clip"))

    def test_python_version_must_be_pinned(self) -> None:
        base = reference._existing_file_manifest()
        for value in ("3.11.5", "3.12", "", "3.12.16rc1"):
            with self.assertRaises(reference.InvalidInput):
                reference.validate_caller_manifest(
                    dict(base, python_version=value))

    def test_geometry_must_match(self) -> None:
        base = reference._existing_file_manifest()
        for field, value in (
                ("sample_rate_host_hz", 44100),
                ("frame_samples_host", 441),
                ("sample_rate_sdk_hz", 48000),
                ("channels_sdk", 2),
                ("frame_samples_sdk", 480),
                ("host_shift_samples", 160),
                ("channels_host", 0),
                ("sample_format_host", "f32")):
            with self.assertRaises(reference.InvalidInput):
                reference.validate_caller_manifest(
                    dict(base, **{field: value}))

    def test_provider_delay_must_match(self) -> None:
        base = reference._existing_file_manifest()
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(
                dict(base, provider_delay_samples=160))
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(
                dict(base, provider_id="unknown.provider.v0"))
        speex = dict(base, provider_id="speex.ns.v0",
                     provider_delay_samples=160)
        self.assertEqual(
            reference.validate_caller_manifest(speex)["provider_id"],
            "speex.ns.v0")

    def test_rights_must_be_acknowledged(self) -> None:
        base = reference._existing_file_manifest()
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(
                dict(base, rights_cleared_audio_acknowledged=False))

    def test_duplicate_json_keys_rejected(self) -> None:
        with self.assertRaises(reference.InvalidInput):
            reference.loads_strict('{"a":1,"a":2}')

    def test_relative_paths_rejected(self) -> None:
        base = reference._existing_file_manifest()
        for field in reference.CALLER_DIR_FIELDS:
            with self.assertRaises(reference.InvalidInput):
                reference.validate_caller_manifest(
                    dict(base, **{field: "relative/path"}))
        for field, _ in reference.CALLER_FILE_PAIRS:
            with self.assertRaises(reference.InvalidInput):
                reference.validate_caller_manifest(
                    dict(base, **{field: "relative/file"}))

    def test_unknown_and_missing_fields_rejected(self) -> None:
        base = reference._existing_file_manifest()
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(dict(base, extra="x"))
        for field in reference.CALLER_ASSET_FIELDS:
            reduced = {key: value for key, value in base.items()
                       if key != field}
            with self.assertRaises(reference.InvalidInput):
                reference.validate_caller_manifest(reduced)


class ReadmeDigestTableTests(unittest.TestCase):
    def test_committed_readme_tables_verify(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
        self.assertEqual(set(counts), {"source", "boundary", "artifacts"})
        self.assertGreater(counts["source"], 0)
        self.assertGreater(counts["boundary"], 0)
        self.assertGreater(counts["artifacts"], 0)

    def test_tampered_digest_rejected(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        digest = reference.BOUNDARY_PINS["CMakeLists.txt"]
        tampered = text.replace(digest, "0" * 64, 1)
        with self.assertRaises(ValueError):
            reference.verify_readme_digests(tampered)

    def test_marker_and_row_validation(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_readme_digest_tables("# no tables")
        with self.assertRaises(ValueError):
            reference.parse_readme_digest_tables(
                "<!-- digest-table: source -->\n| `source:x` | `zz` |\n"
                "<!-- digest-table: end -->")
        with self.assertRaises(ValueError):
            reference.parse_readme_digest_tables(
                "<!-- DIGEST_TABLE_ARTIFACTS_START -->\n"
                "| `a` | `" + "0" * 64 + "` |\n"
                "<!-- DIGEST_TABLE_ARTIFACTS_END -->")

    def test_artifact_table_is_deterministic(self) -> None:
        first = reference.render_artifact_table()
        second = reference.render_artifact_table()
        self.assertEqual(first, second)
        text = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertIn(first, text)


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
        # Later main merges land unrelated task packages beside this one.
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

            # The old fixed base would have reported the siblings; the
            # merge-base comparison must not.
            historic = reference.scope_changed_paths(repo, historical)
            self.assertIn("docs/task-evidence/sibling-alpha/report.json",
                          historic)
            self.assertTrue(reference.scope_violations(historic))

    def test_branch_out_of_scope_edit_fails_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._add_siblings(repo)
            self._git(repo, "checkout", "-q", "-b",
                      "swarm/SDK-LIVEKIT-PYTHON-HOST-ADAPTER-correction")
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

    def test_task_prefix_and_out_of_scope_paths(self) -> None:
        paths = [reference.TASK_PREFIX + "README.md", "CONTRACTS.md"]
        self.assertEqual(reference.scope_violations(paths), ["CONTRACTS.md"])


class PackageBoundaryTests(unittest.TestCase):
    def test_local_pins_exist(self) -> None:
        for name in LOCAL_PINS:
            self.assertTrue((HERE / name).is_file(), name)

    def test_pin_manifest_covers_allowed_keys(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        rows = reference.parse_pin_lines(text)
        paths = {path for _, path in rows}
        self.assertEqual(paths, reference.allowed_pin_keys())
        for line in text.splitlines():
            if line and not line.startswith("#"):
                self.assertNotIn("TASKS.json", line)

    def test_no_forbidden_artifacts_or_symlinks(self) -> None:
        for path in sorted(HERE.iterdir()):
            self.assertNotIn(path.suffix.lower(), FORBIDDEN_SUFFIXES,
                             path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name, {"CMakeLists.txt", "provider.json",
                                         "adapter.json"})

    def test_reproduction_check(self) -> None:
        environment = {"PYTHONDONTWRITEBYTECODE": "1",
                       "PYTHONHASHSEED": "0",
                       "SOURCE_ROOT": str(reference.SOURCE_ROOT),
                       "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}
        result = subprocess.run(
            [sys.executable, str(HERE / "run.py"), "--check"],
            cwd=str(HERE), capture_output=True, text=True, env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("byte_identical=true", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
