# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local SDK-IRCAM-SUPERVP evidence package."""

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
            self.assertEqual(document["mode"], "external-adapter")
            self.assertEqual(document["profile"], "rate")
            self.assertEqual(document["status"], "proposal_only_incomplete")
            self.assertEqual(document["evidence_status"], "incomplete")
            self.assertEqual(document["decision"], "DEFER")
            self.assertEqual(document["defer_before"],
                             "opt_in_external_adapter_exposure")
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

    def test_upstream_blocker(self) -> None:
        upstream = self.report["upstream_record"]
        self.assertEqual(upstream["name"], "IRCAM SuperVP")
        self.assertEqual(upstream["product_url"], reference.PRODUCT_URL)
        self.assertIsNone(upstream["revision"])
        self.assertIs(upstream["revision_pin_available"], False)
        self.assertIs(upstream["public_source_available"], False)
        self.assertIs(upstream["public_binary_available"], False)
        self.assertIs(upstream["embedding_requires_separate_agreement"], True)
        self.assertEqual(upstream["commercial_license_status"],
                         "unresolved_requires_ircam_agreement")
        self.assertIs(upstream["price_recorded"], False)
        self.assertIs(upstream["current_sdk_availability_verified"], False)
        self.assertEqual(upstream["geometry_status"], "unestablished")

    def test_geometry_is_not_asserted(self) -> None:
        geometry = self.report["geometry"]
        self.assertEqual(geometry["supervp_geometry_status"], "unestablished")
        self.assertIs(geometry["supervp_geometry_asserted"], False)
        for key in ("sample_rate_hz", "channels", "hop_samples",
                    "latency_samples", "streaming_supported",
                    "final_partial_window_policy"):
            self.assertIsNone(geometry[key], key)
        self.assertIs(geometry["rate_semantics_verified"], False)
        self.assertIs(geometry["reset_flush_verified"], False)

    def test_rate_profile_is_blocked(self) -> None:
        profile = self.report["rate_profile"]
        self.assertEqual(profile["name"], "rate")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_engine_metrics"])
        self.assertEqual(len(profile["required_items"]),
                         len(reference.RATE_REQUIREMENTS))
        for item in profile["required_items"]:
            self.assertIs(item["satisfied_for_qualification"], False)
            self.assertEqual(item["qualification_effect"], "none")
            self.assertIn(item["package_status"], {"blocked", "not_measured"})

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

    def test_asset_requirements_are_absent(self) -> None:
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        for identifier in (
                "licensed_vendor_sdk_or_runtime",
                "vendor_version_and_build_pin",
                "commercial_license_and_terms",
                "api_reference_and_geometry",
                "runtime_and_platform_lock",
                "rate_cohort_and_references",
                "parity_vector",
                "redistribution_and_output_rights"):
            self.assertEqual(requirements[identifier]["status"], "absent")
        self.assertIsNone(
            requirements["vendor_version_and_build_pin"]["revision"])
        self.assertIsNone(
            requirements["licensed_vendor_sdk_or_runtime"]["sha256"])

    def test_rights_gap_is_explicit(self) -> None:
        rights = self.report["rights_gap"]
        self.assertEqual(rights["status"], "blocked")
        self.assertIs(rights["commercial_license_verified"], False)
        self.assertIs(rights["redistribution_grant"], False)
        self.assertIs(rights["output_use_grant"], False)
        self.assertIs(rights["forum_entitlement_present"], False)

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

    def test_profile_source_is_rate(self) -> None:
        source = reference.profile_source()
        self.assertEqual(source["profile"], "Rate")
        self.assertEqual(source["key"], "rate")
        self.assertTrue(source["row"].startswith("| Rate |"))
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, source["row"])

    def test_source_reported_context_is_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"],
                         "source_reported_not_measured_here")
        self.assertEqual(context["evidence_line"], reference.RECORD_LINE)
        self.assertIn("commercial/research access", context["recorded_licence"])
        self.assertIn("separate agreement with IRCAM",
                      context["recorded_limits"])
        self.assertIsNone(self.report["candidate_metrics"])


class RateAccountingTests(unittest.TestCase):
    def test_exact_mappings(self) -> None:
        source_samples = reference.CONTROL_SOURCE_SAMPLES
        expected = {7500: 64000, 10000: 48000, 12500: 38400, 15000: 32000}
        for rate_bp, output in expected.items():
            self.assertEqual(
                reference.output_samples_for_rate(source_samples, rate_bp),
                output)
        unity = reference.rate_mapping(source_samples, 10000)
        self.assertEqual(unity["duration_ratio"], "1")
        faster = reference.rate_mapping(source_samples, 12500)
        self.assertEqual(faster["duration_ratio"], "4/5")
        slower = reference.rate_mapping(source_samples, 7500)
        self.assertEqual(slower["duration_ratio"], "4/3")

    def test_chunked_accounting_has_no_drift(self) -> None:
        for rate_bp in reference.CONTROL_RATES_BP:
            row = reference.chunked_accounting(
                reference.CONTROL_SOURCE_SAMPLES, rate_bp,
                reference.CONTROL_CHUNK_SAMPLES)
            self.assertEqual(row["drift_samples"], 0)
            self.assertGreater(row["chunks"], 0)

    def test_final_partial_window(self) -> None:
        for rate_bp in reference.CONTROL_RATES_BP:
            row = reference.final_partial_window_accounting(rate_bp)
            self.assertEqual(row["partial_tail_samples"], 37)
            self.assertGreater(row["output_samples"], 0)
            self.assertIs(row["measured"], False)

    def test_invalid_rate_rejected(self) -> None:
        for value in (0, -1, True, 2499, 40001, "10000"):
            with self.assertRaises(reference.InvalidInput):
                reference.output_samples_for_rate(1000, value)

    def test_pcm_validity(self) -> None:
        good = reference.synthetic_source_pcm()
        summary = reference.pcm_summary(good, reference.CONTROL_SAMPLE_RATE_HZ)
        self.assertEqual(summary["samples"],
                         reference.CONTROL_SOURCE_SAMPLES)
        self.assertEqual(summary["duration_s"], "3")
        self.assertGreater(summary["peak_abs_scaled_1e6"], 0)
        for bad in ([], [0.0, math.nan], [0.0, math.inf], [0.0, -math.inf],
                    [0.0, 1.5], [0.0, True], [0.0, "0.1"]):
            with self.assertRaises(reference.InvalidInput):
                reference.validate_pcm(bad)


class AdmissionTests(unittest.TestCase):
    def test_positive_structural_control(self) -> None:
        result = reference.validate_caller_manifest(
            reference._existing_file_manifest())
        self.assertIs(result["accepted"], True)
        self.assertIs(result["engine_executed"], False)
        self.assertEqual(result["files_checked"],
                         len(reference.CALLER_FILE_PAIRS))
        self.assertEqual(result["directories_checked"],
                         len(reference.CALLER_DIR_FIELDS))

    def test_adverse_cases_all_rejected(self) -> None:
        rows = reference.run_adverse_controls()
        self.assertEqual(len(rows), len(reference.ADVERSE_CASE_IDS))
        for row in rows:
            self.assertEqual(row["result"], "rejected", row)
        self.assertEqual(reference.ADVERSE_CASE_IDS,
                         tuple(row["case"] for row in rows))

    def test_missing_asset_rejected_before_processing(self) -> None:
        manifest = dict(reference._shape_only_manifest(),
                        channels=1,
                        sample_rate_output_hz=16000)
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(manifest)

    def test_wrong_scope_and_variant_rejected(self) -> None:
        base = reference._existing_file_manifest()
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(
                dict(base, scope="voice_conversion"))
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(
                dict(base, variant="caller_clocked_streaming"))

    def test_commercial_terms_must_be_acknowledged(self) -> None:
        base = reference._existing_file_manifest()
        with self.assertRaises(reference.InvalidInput):
            reference.validate_caller_manifest(
                dict(base, commercial_terms_acknowledged=False))

    def test_relative_paths_rejected(self) -> None:
        base = reference._existing_file_manifest()
        for field in reference.CALLER_DIR_FIELDS:
            with self.assertRaises(reference.InvalidInput):
                reference.validate_caller_manifest(
                    dict(base, **{field: "relative/path"}))

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
                      "swarm/SDK-IRCAM-SUPERVP-correction")
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
