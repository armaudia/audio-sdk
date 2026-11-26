# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Tests for the deterministic SDK-FSMN-VAD evidence package.

The tests never import FunASR, load a checkpoint, read audio or invoke a model.
They exercise strict JSON, stable board identity, absence probes, the
fail-closed caller-asset schema, README digest tables, canonical report bytes
and the merge-base scope comparison.
"""

from __future__ import annotations

import copy
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

SPDX_HEADER = "SPDX-License-" + "Identifier: Apache-2.0"
LOCAL_PINS = (
    "LICENSES.md",
    "README.md",
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


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a": 1, "a": 2}')

    def test_nonfinite_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                reference.loads_strict('{"value": ' + token + "}")

    def test_float_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.assert_no_float({"value": 1.5})
        with self.assertRaises(ValueError):
            reference.assert_no_float([{"nested": [2.0]}])

    def test_non_object_root_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict("[1, 2]")

    def test_canonical_bytes_are_stable(self) -> None:
        value = {"b": [2, 1], "a": "x"}
        first = reference.canonical_bytes(value)
        second = reference.canonical_bytes(copy.deepcopy(value))
        self.assertEqual(first, second)
        self.assertEqual(first, b'{"a":"x","b":[2,1]}')


class BoardIdentityTests(unittest.TestCase):
    def _write(self, document: dict) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json",
                                             delete=False, encoding="utf-8")
        json.dump(document, handle)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def _row(self) -> dict:
        return {
            "id": reference.TASK,
            "title": reference.TITLE,
            "component": reference.COMPONENT,
            "mode": reference.MODE,
            "repository": reference.REPOSITORY,
            "depends_on": list(reference.DEPENDS_ON),
            "status": "in_progress",
            "owner": "agent-FSMN-VAD",
            "claim": {"base_commit": reference.BASE_COMMIT},
            "review": None,
            "handoff": None,
            "dispatch_priority": 3,
        }

    def test_mutable_fields_do_not_change_projection(self) -> None:
        row = self._row()
        before = reference.board_row_projection(self._write({"tasks": [row]}))
        row.update({"status": "done", "owner": "someone-else",
                    "claim": {"base_commit": "0" * 40},
                    "review": {"state": "approved"}, "handoff": {"x": 1},
                    "dispatch_priority": 1})
        after = reference.board_row_projection(self._write({"tasks": [row]}))
        self.assertEqual(before, after)
        self.assertEqual(before["id"], reference.TASK)
        self.assertEqual(before["mode"], "feasibility")

    def test_stable_identity_change_changes_projection(self) -> None:
        row = self._row()
        before = reference.board_row_projection(self._write({"tasks": [row]}))
        row["title"] = "Different title"
        after = reference.board_row_projection(self._write({"tasks": [row]}))
        self.assertNotEqual(before["title"], after["title"])

    def test_mode_drift_rejected(self) -> None:
        row = self._row()
        row["mode"] = "implementation"
        with self.assertRaises(ValueError):
            reference.board_row_projection(self._write({"tasks": [row]}))

    def test_component_drift_rejected(self) -> None:
        row = self._row()
        row["component"] = "not-fsmn"
        with self.assertRaises(ValueError):
            reference.board_row_projection(self._write({"tasks": [row]}))

    def test_mutable_board_not_pinned(self) -> None:
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)


class AbsenceTests(unittest.TestCase):
    def test_source_weights_runtime_absent(self) -> None:
        source = reference.source_probe()
        weights = reference.weights_probe()
        runtime = reference.runtime_probe()
        self.assertEqual(source["status"], "blocked_exact_source_absent")
        self.assertIs(source["present"], False)
        self.assertIs(source["executed"], False)
        self.assertEqual(weights["status"],
                         "blocked_exact_checkpoint_absent")
        self.assertIs(weights["pinned_model_present"], False)
        self.assertIsNone(weights["admitted_model"])
        self.assertEqual(weights["present_file_count"], 0)
        self.assertEqual(runtime["status"],
                         "blocked_pinned_runtime_absent")
        self.assertIs(runtime["pinned_runtime_present"], False)
        self.assertIs(runtime["imported_or_executed"], False)

    def test_absence_summary_zero(self) -> None:
        probes = reference.absence_probes()
        summary = reference.absence_summary(probes)
        self.assertGreater(len(probes), 0)
        self.assertEqual(summary["present_count"], 0)
        self.assertIs(summary["all_probes_absent"], True)
        self.assertIs(summary["recursive_workspace_walk"], False)
        self.assertIs(summary["download_attempted"], False)

    def test_every_weight_file_absent(self) -> None:
        for row in reference.weights_probe()["files"]:
            self.assertIs(row["present"], False)
            self.assertIs(row["admitted"], False)


class BundleAdmissionTests(unittest.TestCase):
    def test_control_accepted_but_not_qualified(self) -> None:
        result = reference.validate_bundle(reference._bundle_control())
        self.assertEqual(result["status"], "accepted")
        self.assertIs(result["qualifies"], False)
        self.assertGreater(result["checks"], 0)

    def test_missing_required_field(self) -> None:
        bundle = reference._bundle_control()
        bundle.pop("source")
        result = reference.validate_bundle(bundle)
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["code"], "missing_field")

    def test_invalid_payload_type(self) -> None:
        result = reference.validate_bundle(["not", "an", "object"])
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["code"], "manifest_not_object")

    def test_invalid_revision_and_sha(self) -> None:
        bundle = reference._bundle_control()
        bundle["source"]["revision"] = "short"
        self.assertEqual(reference.validate_bundle(bundle)["code"],
                         "invalid_revision")
        bundle = reference._bundle_control()
        bundle["source"]["license_sha256"] = "xyz"
        self.assertEqual(reference.validate_bundle(bundle)["code"],
                         "invalid_sha256")

    def test_nonfinite_and_duplicate_raw_cases(self) -> None:
        with self.assertRaises(ValueError) as duplicate:
            reference.loads_strict('{"a": 1, "a": 2}')
        self.assertIn("duplicate_json_key", str(duplicate.exception))
        with self.assertRaises(ValueError) as nonfinite:
            reference.loads_strict('{"a": NaN}')
        self.assertIn("nonfinite_json", str(nonfinite.exception))

    def test_geometry_rejections(self) -> None:
        bundle = reference._bundle_control()
        bundle["geometry"]["channels"] = 2
        self.assertEqual(reference.validate_bundle(bundle)["code"],
                         "invalid_geometry")
        bundle = reference._bundle_control()
        bundle["geometry"]["streaming"] = False
        self.assertEqual(reference.validate_bundle(bundle)["code"],
                         "non_streaming_bundle")
        bundle = reference._bundle_control()
        bundle["geometry"]["chunk_finalization"] = False
        self.assertEqual(reference.validate_bundle(bundle)["code"],
                         "chunk_finalization_not_declared")
        bundle = reference._bundle_control()
        bundle["geometry"]["sample_rate_hz"] = 44100
        self.assertEqual(reference.validate_bundle(bundle)["code"],
                         "out_of_range")

    def test_all_admission_cases(self) -> None:
        block = reference.admission_controls()
        cases = block["cases"]
        accepted = [case for case in cases if case["status"] == "accepted"]
        rejected = [case for case in cases if case["status"] == "rejected"]
        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0]["id"], "accepted-schema-control")
        self.assertIs(accepted[0]["qualifies"], False)
        self.assertGreater(len(rejected), 30)
        for case in rejected:
            self.assertIs(case["qualifies"], False)
            self.assertIs(case["state_unchanged"], True)
            self.assertTrue(case["code"])
        codes = {case["code"] for case in rejected}
        for expected in ("manifest_not_object", "missing_field", "unknown_field",
                         "invalid_revision", "invalid_sha256", "unsafe_path",
                         "invalid_integer", "out_of_range", "rights_not_cleared",
                         "non_offline_runtime", "duplicate_json_key",
                         "nonfinite_json", "noncanonical_order",
                         "duplicate_value", "invalid_split", "empty_text",
                         "invalid_geometry", "invalid_condition",
                         "non_streaming_bundle",
                         "chunk_finalization_not_declared"):
            self.assertIn(expected, codes)
        summary = block["summary"]
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertIs(summary["accepted_control_qualifies"], False)
        self.assertIs(summary["runtime_invoked"], False)
        self.assertIs(summary["weights_loaded"], False)
        self.assertIs(summary["audio_read"], False)
        self.assertIs(summary["inference_performed"], False)

    def test_unconsented_and_false_rights_rejected(self) -> None:
        bundle = reference._bundle_control()
        bundle["cohort"][0]["consent"] = False
        self.assertEqual(reference.validate_bundle(bundle)["code"],
                         "rights_not_cleared")
        bundle = reference._bundle_control()
        bundle["rights"]["output_use"] = False
        self.assertEqual(reference.validate_bundle(bundle)["code"],
                         "rights_not_cleared")

    def test_false_condition_rejected(self) -> None:
        bundle = reference._bundle_control()
        bundle["conditions"]["cross_hop_behavior"] = False
        self.assertEqual(reference.validate_bundle(bundle)["code"],
                         "missing_required_value")
        bundle = reference._bundle_control()
        bundle["outcomes"]["detections"] = False
        self.assertEqual(reference.validate_bundle(bundle)["code"],
                         "missing_required_value")


class ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = reference.build_contract()

    def test_contract_semantics(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "proposal_only_incomplete")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertIs(self.contract["proposal_only"], True)
        self.assertIs(self.contract["incomplete"], True)
        self.assertIs(self.contract["board_file_pinned"], False)
        self.assertEqual(self.contract["branch"], reference.BRANCH)
        self.assertEqual(self.contract["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.contract["worktree"], reference.CLAIM_WORKTREE)
        self.assertEqual(self.contract["reviewer"], reference.REVIEWER)
        self.assertEqual(self.contract["profile"], "analysis")
        reference.validate_contract(self.contract)

    def test_eight_blocked_gates(self) -> None:
        gates = self.contract["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([row["id"] for row in gates],
                         ["RG-0" + str(i) for i in range(1, 9)])
        for row in gates:
            self.assertEqual(row["status"], "blocked")
            self.assertIs(row["qualifies"], False)
            self.assertTrue(row["reopen_condition"])
            self.assertEqual(row["linked_row"], reference._gate_link())

    def test_six_open_blockers_and_artifacts(self) -> None:
        blockers = self.contract["exact_blockers"]
        artifacts = self.contract["required_artifacts"]
        self.assertEqual(len(blockers), 6)
        self.assertEqual(len(artifacts), 6)
        artifact_ids = {row["id"] for row in artifacts}
        for row in blockers:
            self.assertEqual(row["status"], "open")
            self.assertIs(row["qualifies"], False)
            self.assertIn(row["artifact_id"], artifact_ids)
        for row in artifacts:
            self.assertIs(row["present"], False)
            self.assertIs(row["verified"], False)
            self.assertIs(row["blocked"], True)
            self.assertIsNone(row["sha256"])

    def test_analysis_profile_blocked(self) -> None:
        profile = self.contract["analysis_profile"]
        self.assertEqual(profile["name"], "analysis")
        self.assertEqual(profile["status"], "blocked")
        self.assertEqual(tuple(row["id"] for row in profile["required_items"]),
                         tuple("ANA-%02d" % i for i in range(1, 13)))
        for row in profile["required_items"]:
            self.assertEqual(row["status"], "blocked")
            self.assertEqual(row["qualification_effect"], "none")
            self.assertIs(row["satisfied_for_qualification"], False)
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_model_metrics"])
        for key, value in profile.items():
            if key in ("name", "profile", "status", "source_path", "plan_note",
                       "required_items", "satisfied_for_qualification",
                       "real_model_metrics", "qualifies"):
                continue
            self.assertIs(value, False, key)

    def test_upstream_has_no_claimed_digest(self) -> None:
        upstream = self.contract["upstream_record"]
        self.assertEqual(upstream["toolkit_repository"],
                         "https://github.com/modelscope/FunASR")
        self.assertEqual(upstream["model_id"], reference.MODEL_ID)
        self.assertIsNone(upstream["source_revision"])
        self.assertIsNone(upstream["model_revision"])
        self.assertIs(upstream["present"], False)
        self.assertIs(upstream["digest_asserted"], False)
        self.assertEqual(upstream["declared_sample_rate_hz"], 16_000)
        self.assertEqual(upstream["checkpoint_rights_status"], "unresolved")

    def test_boundary_all_false_except_task_local(self) -> None:
        boundary = self.contract["boundary"]
        for key, value in boundary.items():
            if key == "task_local_only":
                self.assertIs(value, True)
            else:
                self.assertIs(value, False, key)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_no_floats(self) -> None:
        reference.assert_no_float(self.report)

    def test_decision_status_and_qualification(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertIs(self.report["proposal_only"], True)
        self.assertIs(self.report["incomplete"], True)
        self.assertEqual(self.report["qualification"]["status"],
                         "not_qualified")
        self.assertEqual(self.report["qualification"]["readiness"],
                         "incomplete")
        self.assertIs(self.report["qualification"]["all_release_gates_blocked"],
                      True)
        self.assertIs(self.report["qualification"]["candidate_qualified"],
                      False)
        self.assertIs(self.report["qualification"]["not_qualified"], True)

    def test_eight_blocked_gates_and_remaining(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual(self.report["remaining_gates"],
                         [row["id"] for row in gates])
        for row in gates:
            self.assertEqual(row["status"], "blocked")
            self.assertIs(row["qualifies"], False)

    def test_contract_digest_and_copies(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(contract))
        for key in ("disposition", "boundary", "scope", "public_v0_geometry",
                    "exact_scope", "qualification", "upstream_record",
                    "geometry", "required_artifacts", "exact_blockers",
                    "profile_source", "historical_evidence", "rights_gap",
                    "analysis_profile"):
            self.assertEqual(self.report[key], contract[key], key)
        self.assertEqual(self.report["gates"], contract["release_gates"])
        self.assertEqual(self.report["prohibited_claims"],
                         contract["non_claims"])

    def test_linked_identity(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["projection"],
                         reference.board_row_projection())
        self.assertEqual(identity["sha256"],
                         reference.board_row_digest(identity["projection"]))
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertIs(identity["board_file_pinned"], False)
        self.assertIs(identity["board_status_gates_anything"], False)
        self.assertEqual(identity["linked_rows"],
                         [dict(row) for row in reference.linked_rows()])
        self.assertEqual(identity["linked_rows_sha256"],
                         reference.linked_rows_digest())
        row_identity = self.report["task_row_identity"]
        self.assertIs(row_identity["whole_file_hashed"], False)
        self.assertEqual(row_identity["stable_sha256"], identity["sha256"])

    def test_source_and_boundary_pins(self) -> None:
        for path, digest in reference.SOURCE_PINS.items():
            row = self.report["source_pins"][path]
            self.assertEqual(row["sha256"], digest)
            self.assertEqual(row["actual"], digest)
            self.assertIs(row["verified"], True)
        for path, digest in reference.BOUNDARY_PINS.items():
            row = self.report["boundary_pins"][path]
            self.assertEqual(row["sha256"], digest)
            self.assertIs(row["verified"], True)

    def test_historical_and_peer_evidence(self) -> None:
        historical = self.report["historical_evidence"]
        self.assertEqual(historical["status"],
                         "no_local_historical_execution_found")
        self.assertEqual(historical["entries"], [])
        self.assertIs(historical["qualifies"], False)
        self.assertIs(
            historical["source_reported_context"]["reproduced_here"], False)
        self.assertIs(
            historical["source_reported_context"]["admitted_as_result"], False)
        self.assertGreater(len(self.report["peer_evidence"]), 0)
        for row in self.report["peer_evidence"]:
            self.assertIs(row["admitted_as_result"], False)
            self.assertIs(row["inherited_metrics"], False)

    def test_canonical_roundtrip(self) -> None:
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(hashlib.sha256(text.encode("ascii")).hexdigest(),
                         digest)
        self.assertEqual(json.loads(text), self.report)
        self.assertEqual(reference.canonical_bytes(self.report),
                         text.encode("ascii"))

    def test_geometry(self) -> None:
        geometry = self.report["geometry"]
        self.assertEqual(geometry["task_kind"], reference.TASK_KIND)
        self.assertEqual(geometry["declared_sample_rate_hz"], 16_000)
        self.assertIs(geometry["sample_rate_verified"], False)
        self.assertIs(geometry["streaming_endpoint_detector"], True)
        self.assertIs(geometry["chunk_finalization_adds_buffering"], True)
        self.assertIsNone(geometry["hop_samples"])
        self.assertIs(geometry["installed_v0"], False)
        self.assertIs(geometry["provider_registered"], False)

    def test_admission_and_strictness(self) -> None:
        admission = self.report["admission"]
        self.assertEqual(admission["summary"]["accepted_schema_controls"], 1)
        self.assertEqual(admission["summary"]["qualifying_results"], 0)
        self.assertIs(admission["summary"]["all_adverse_cases_rejected"], True)
        strictness = self.report["strictness"]
        self.assertIs(strictness["all_adverse_parsers_rejected"], True)

    def test_profile_source(self) -> None:
        source = self.report["profile_source"]
        self.assertEqual(source["profile"], "Analysis")
        self.assertEqual(source["key"], "analysis")
        self.assertTrue(source["row"].startswith("| Analysis |"))
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, source["row"])


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
                      "swarm/SDK-FSMN-VAD-correction")
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

    def test_python_spdx_headers(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(SPDX_HEADER, head, path.name)

    def test_non_claims(self) -> None:
        self.assertEqual(len(reference.NON_CLAIMS), 8)
        text = " ".join(reference.NON_CLAIMS)
        for phrase in ("No model inference", "No benchmark", "DEFER",
                       "No network access", "No provider"):
            self.assertIn(phrase, text)

    def test_no_provider_or_audio_claims(self) -> None:
        scope = reference.scope_block()
        for key, value in scope.items():
            if key == "task_local_evidence_only":
                self.assertIs(value, True)
            else:
                self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
