# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance and regression tests for the SDK-NEURAL-KALMAN-FILTERING-NKF
evidence package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

LOCAL_PINS = reference.LOCAL_PIN_FILES
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib", ".m4a",
    ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus", ".pcap", ".pcapng",
    ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wasm", ".wav", ".weights",
}
SPDX_LICENSE = "SPDX-License-" + "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"


class CanonicalReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = reference.build_contract()

    def test_report_is_canonical_and_float_free(self) -> None:
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(text, reference.canonical_text(self.report))
        self.assertEqual(digest, hashlib.sha256(text.encode("ascii")).hexdigest())
        self.assertEqual((HERE / "report.json").read_bytes(),
                         text.encode("ascii"))
        reference.assert_no_float(self.report)

    def test_contract_and_sidecar(self) -> None:
        payload = reference.canonical_bytes(self.contract)
        self.assertEqual((HERE / "contract.json").read_bytes(), payload)
        report_payload = (HERE / "report.json").read_bytes()
        expected = (hashlib.sha256(report_payload).hexdigest() +
                    "  report.json\n").encode("ascii")
        self.assertEqual((HERE / "report.json.sha256").read_bytes(), expected)
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_identity_and_disposition(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], "SDK-NEURAL-KALMAN-FILTERING-NKF")
        self.assertEqual(report["component_id"],
                         "neural-kalman-filtering-nkf")
        self.assertEqual(report["mode"], "feasibility")
        self.assertEqual(report["profile"], "room")
        self.assertEqual(report["verification_profile"], "Room")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertIs(report["proposal_only"], True)
        self.assertIs(report["incomplete"], True)
        self.assertEqual(report["base_commit"], reference.BASE_COMMIT)
        disposition = report["disposition"]
        self.assertEqual(disposition["promotion"], "defer")
        self.assertEqual(disposition["production_exposure"], "DEFER")
        self.assertIs(disposition["expose_as_processor"], False)
        self.assertIs(disposition["registered"], False)
        self.assertIs(disposition["default_enabled"], False)
        self.assertIs(disposition["missing_result_qualifies"], False)

    def test_profile_source(self) -> None:
        source = self.report["profile_source"]
        self.assertEqual(source["profile"], "Room")
        self.assertEqual(source["key"], "room")
        self.assertTrue(source["row"].startswith("| Room |"))
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, source["row"])
        self.assertEqual(source["plan_note"], reference.PLAN_NOTE)

    def test_geometry_and_public_baseline(self) -> None:
        report = self.report
        geometry = report["public_v0_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertIs(geometry["preserved"], True)
        self.assertIs(geometry["sdk_callback_invoked"], False)
        model = report["geometry"]
        self.assertEqual(model["task_kind"],
                         "acoustic_echo_cancellation_with_paired_reference")
        self.assertIs(model["requires_paired_far_end_reference"], True)
        self.assertIs(model["requires_synchronized_reference_and_microphone"],
                      True)
        self.assertIs(model["requires_learned_model_weights"], True)
        self.assertIs(model["stateful_recursive"], True)
        self.assertIs(model["geometry_verified"], False)
        self.assertIs(model["candidate_output_measured"], False)
        self.assertIsNone(model["declared_state_dimension"])
        self.assertIsNone(model["declared_checkpoint_sha256"])
        self.assertIs(model["provider_registered"], False)

    def test_probes_are_absent(self) -> None:
        report = self.report
        self.assertEqual(report["source_probe"], reference.source_probe())
        self.assertEqual(report["parameter_probe"],
                         reference.parameter_probe())
        self.assertEqual(report["checkpoint_probe"],
                         reference.checkpoint_probe())
        self.assertEqual(report["fixture_probe"],
                         reference.fixture_probe())
        self.assertEqual(report["runtime_probe"],
                         reference.runtime_probe())
        self.assertEqual(report["rights_probe"], reference.rights_probe())
        self.assertEqual(report["absence_evidence"]["probes"],
                         reference.absence_probes())
        summary = report["absence_evidence"]["summary"]
        self.assertEqual(summary["present_count"], 0)
        self.assertIs(summary["all_probes_absent"], True)
        self.assertIs(summary["download_attempted"], False)
        self.assertIs(summary["recursive_workspace_walk"], False)
        for key in ("source_probe", "parameter_probe", "checkpoint_probe",
                    "fixture_probe", "runtime_probe", "rights_probe"):
            self.assertIsNotNone(report[key]["status"])
        checkpoint = report["checkpoint_probe"]
        self.assertIs(checkpoint["pinned_model_present"], False)
        self.assertIs(checkpoint["opened_or_loaded"], False)
        self.assertIsNone(checkpoint["admitted_model"])

    def test_artifacts_blockers_and_gates(self) -> None:
        report = self.report
        self.assertEqual(tuple(row["id"] for row in report["required_artifacts"]),
                         reference.ARTIFACT_IDS)
        for row in report["required_artifacts"]:
            self.assertIs(row["present"], False)
            self.assertIs(row["verified"], False)
            self.assertIs(row["blocked"], True)
            self.assertIsNone(row["sha256"])
        self.assertEqual(tuple(row["id"] for row in report["exact_blockers"]),
                         reference.BLOCKER_IDS)
        text = " ".join(row["statement"] + " " + row["required_action"]
                        for row in report["exact_blockers"])
        for token in reference.BLOCKER_TOKENS:
            self.assertIn(token, text)
        self.assertEqual(tuple(row["id"] for row in report["gates"]),
                         reference.GATE_IDS)
        for row in report["gates"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIs(row["qualifies"], False)
            self.assertTrue(row["reopen_condition"])
        self.assertEqual(len(report["gates"]), 8)
        self.assertEqual(report["remaining_gates"],
                         list(reference.GATE_IDS))
        qualification = report["qualification"]
        self.assertEqual(qualification["blocked_gate_count"], 8)
        self.assertIs(qualification["all_release_gates_blocked"], True)
        self.assertIs(qualification["candidate_qualified"], False)

    def test_room_profile_is_blocked(self) -> None:
        profile = self.report["room_profile"]
        self.assertEqual(profile["name"], "room")
        self.assertEqual(profile["profile"], "Room")
        self.assertEqual(tuple(row["id"] for row in profile["required_items"]),
                         reference.ROOM_ITEM_IDS)
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIs(profile["qualifies"], False)
        self.assertIsNone(profile["real_candidate_metrics"])
        for row in profile["required_items"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIs(row["satisfied_for_qualification"], False)
        for key, value in profile.items():
            if key in ("name", "profile", "status", "source_path", "plan_note",
                       "required_items", "satisfied_for_qualification",
                       "real_candidate_metrics", "qualifies"):
                continue
            self.assertIs(value, False, key)

    def test_task_requirement_is_blocked(self) -> None:
        requirement = self.report["task_requirement"]
        self.assertEqual(requirement["plan_note"], reference.PLAN_NOTE)
        self.assertIs(requirement["model_pinned"], False)
        self.assertIs(requirement["reset_measured"], False)
        self.assertIs(requirement["reconvergence_measured"], False)
        self.assertIs(requirement["double_talk_measured"], False)
        self.assertIs(requirement["reference_timing_measured"], False)
        self.assertIs(requirement["echo_attenuation_measured"], False)
        self.assertIs(requirement["near_end_preservation_measured"], False)
        self.assertEqual(requirement["status"],
                         "blocked_no_pinned_model_and_no_matched_room_fixture")

    def test_historical_pilot_has_no_nkf_row(self) -> None:
        historical = self.report["historical_evidence"]
        self.assertEqual(historical["status"],
                         "present_unmatched_no_nkf_result")
        self.assertIs(historical["nkf_candidate_listed"], True)
        self.assertIs(historical["nkf_result_row_present"], False)
        self.assertIs(historical["matched_execution"], False)
        self.assertIs(historical["admitted_as_result"], False)
        self.assertIs(historical["inherited_metrics"], False)
        self.assertEqual(
            historical["controller_rows"],
            ["NLMS, 128 taps", "NLMS, 192 taps", "NLMS, 256 taps",
             "NLMS, 512 taps", "SpeexDSP MDF, 4,000-sample tail (250 ms)"])

    def test_admission_is_fail_closed(self) -> None:
        admission = self.report["admission"]
        cases = admission["cases"]
        self.assertEqual(len(cases), 14)
        self.assertEqual(cases[0]["id"], "CASE-01")
        self.assertIs(cases[0]["accepted_by_schema"], True)
        self.assertEqual(cases[0]["admission"],
                         "deferred_required_artifacts_absent")
        self.assertIs(cases[0]["qualifies"], False)
        for case in cases[1:]:
            self.assertIs(case["accepted_by_schema"], False)
            self.assertIsNone(case["admission"])
            self.assertIs(case["qualifies"], False)
            self.assertTrue(case["code"])
        codes = {case["code"] for case in cases}
        for code in ("invalid_json", "duplicate_json_key", "nonfinite_json",
                     "unsafe_path_revision", "invalid_model_geometry",
                     "invalid_model_type", "invalid_fixture_geometry",
                     "fixture_class_not_matched", "rights_not_cleared",
                     "unknown_field", "invalid_runtime",
                     "invalid_comparison"):
            self.assertIn(code, codes)
        summary = admission["controls"]
        self.assertEqual(summary["schema_control_admission"],
                         "deferred_required_artifacts_absent")
        self.assertIs(summary["schema_control_qualifies"], False)
        self.assertIs(summary["runtime_invoked"], False)
        self.assertIs(summary["audio_read"], False)
        self.assertIs(summary["inference_performed"], False)

    def test_rejection_of_missing_invalid_and_nonfinite_bundles(self) -> None:
        base = reference._base_bundle()
        missing = json.loads(json.dumps(base))
        missing["model"].pop("weights_sha256")
        with self.assertRaises(ValueError):
            reference.validate_bundle(missing)
        missing_fixture = json.loads(json.dumps(base))
        missing_fixture["fixture"].pop("mic_sha256")
        with self.assertRaises(ValueError):
            reference.validate_bundle(missing_fixture)
        huge = json.loads(json.dumps(base))
        huge["model"]["weights_bytes"] = reference.MAX_WEIGHT_BYTES + 1
        with self.assertRaises(ValueError):
            reference.validate_bundle(huge)
        with self.assertRaises(ValueError):
            reference.validate_bundle(
                reference.loads_strict('{"schema":NaN}'))

    def test_strictness_is_fail_closed(self) -> None:
        strictness = self.report["strictness"]
        self.assertEqual(strictness, reference.strictness_controls())
        self.assertEqual(strictness["json_cases"],
                         strictness["json_rejected"])
        self.assertEqual(strictness["pin_cases"],
                         strictness["pin_rejected"])
        self.assertEqual(strictness["readme_cases"],
                         strictness["readme_rejected"])
        self.assertIs(strictness["all_adverse_parsers_rejected"], True)

    def test_stimulus_probe_is_not_candidate_output(self) -> None:
        stimulus = self.report["stimulus_probe"]
        self.assertIs(stimulus["candidate_processing"], False)
        self.assertEqual(set(stimulus["stimuli"]),
                         {"silence", "impulse", "step", "sweep",
                          "speech_like"})
        self.assertIs(stimulus["identity_control"]["bit_exact"], True)
        self.assertEqual(stimulus["identity_control"]["changed_values"], 0)
        comparison = stimulus["room_comparison"]
        self.assertEqual(comparison["status"],
                         "blocked_no_candidate_output")
        self.assertIs(comparison["model_pinned"], False)

    def test_pins_and_boundaries(self) -> None:
        report = self.report
        for path, digest in reference.SOURCE_PINS.items():
            self.assertEqual(reference.sha256_file(
                reference.SOURCE_ROOT / path), digest)
            self.assertIs(report["source_pins"][path]["verified"], True)
        for path, digest in reference.BOUNDARY_PINS.items():
            self.assertEqual(reference.sha256_file(
                reference.WORKTREE / path), digest)
            self.assertIs(report["boundary_pins"][path]["verified"], True)
        identity = report["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertIs(identity["board_file_pinned"], False)
        self.assertIs(identity["board_status_gates_anything"], False)
        self.assertEqual(report["task_row_identity"]["source"],
                         reference.BOARD_TASK_ROW)
        self.assertIs(report["task_row_identity"]["whole_file_hashed"], False)

    def test_prohibited_claims_and_scope(self) -> None:
        report = self.report
        self.assertEqual(report["prohibited_claims"],
                         list(reference.NON_CLAIMS))
        self.assertEqual(report["write_scope"], reference.TASK_PREFIX)
        for key, value in report["boundary"].items():
            if key in ("task_local_only", "installed_v0_unchanged"):
                self.assertIs(value, True)
            else:
                self.assertIs(value, False)
        for key, value in report["scope"].items():
            if key == "task_local_evidence_only":
                self.assertIs(value, True)
            else:
                self.assertIs(value, False)


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
        digest = reference.BOUNDARY_PINS["CONTRACTS.md"]
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
                      "swarm/SDK-NEURAL-KALMAN-FILTERING-NKF")
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


class PackageBoundaryTests(unittest.TestCase):
    def test_local_pins_exist(self) -> None:
        for name in LOCAL_PINS:
            self.assertTrue((HERE / name).is_file(), name)

    def test_no_forbidden_artifacts_or_symlinks(self) -> None:
        for path in sorted(HERE.iterdir()):
            self.assertNotIn(path.suffix.lower(), FORBIDDEN_SUFFIXES,
                             path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name, {"CMakeLists.txt", "provider.json",
                                         "adapter.json"})

    def test_python_spdx_and_license_sidecars(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_LICENSE, head, path.name)
            self.assertIn(SPDX_COPYRIGHT, head, path.name)
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "report.json.license", "report.json.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_LICENSE, text, name)
            self.assertIn(SPDX_COPYRIGHT, text, name)


if __name__ == "__main__":
    unittest.main()
