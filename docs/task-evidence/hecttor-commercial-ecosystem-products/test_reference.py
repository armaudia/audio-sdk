# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local tests for SDK-HECTTOR-... evidence, including scope regressions."""

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
        self.assertEqual(projection["mode"], "external-adapter")

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
        changed["title"] = "Hecttor changed"
        self.assertNotEqual(reference.board_row_digest(projection),
                            reference.board_row_digest(changed))

    def test_mutable_board_not_pinned(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        self.assertNotIn(reference.BOARD_TASK_ROW, text)
        self.assertNotIn("source:" + reference.BOARD_TASK_ROW, text)


class AbsenceTests(unittest.TestCase):
    def test_all_fixed_probes_absent(self) -> None:
        probes = reference.all_probes()
        self.assertEqual(len(probes), 20)
        self.assertEqual([row["path"] for row in probes
                          if row["present"]], [])
        summary = reference.absence_summary(probes)
        self.assertTrue(summary["all_probes_absent"])
        self.assertEqual(summary["present_count"], 0)
        self.assertFalse(summary["recursive_workspace_walk"])
        self.assertFalse(summary["download_attempted"])
        self.assertFalse(summary["network_used"])
        self.assertFalse(summary["vendor_runtime_executed"])

    def test_absence_summary_counts(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["probe_count"], 20)
        self.assertEqual(summary["workspace_probe_count"], 11)
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
    def test_register_has_no_hecttor_entry(self) -> None:
        registry = reference.asset_registry()
        self.assertEqual(registry["candidate_count"], 20)
        self.assertFalse(registry["hecttor_entry_present"])
        self.assertEqual(registry["hecttor_candidate_ids"], [])
        self.assertFalse(registry["asset_identity_available_for_hecttor"])

    def test_evidence_inputs_are_real_and_ordered(self) -> None:
        rows = reference.evidence_inputs()
        self.assertEqual(len(rows), 8)
        self.assertEqual({row["path"] for row in rows}, {
            "research/noise_suppression_candidate_census.md",
            "research/noise_suppression_assets_20261027.json",
            "research/voice-enhancement-20261101/candidate_matrix.csv",
            "research/selected_audio_enhancement_candidates.md",
            "audio-benchmark-platform/plan/INVENTORY.json",
            "audio-benchmark-platform/plan/INVENTORY.md",
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "audio-benchmark-platform/plan/audio-sdk/README.md",
        })
        mentions = {row["path"]: row["mentions_hecttor"] for row in rows}
        self.assertTrue(
            mentions["research/noise_suppression_candidate_census.md"])
        self.assertTrue(
            mentions["audio-benchmark-platform/plan/INVENTORY.json"])
        self.assertFalse(
            mentions["research/noise_suppression_assets_20261027.json"])


class VendorRecordTests(unittest.TestCase):
    def test_vendor_record_identity(self) -> None:
        vendor = contract()["vendor_record"]
        self.assertEqual(vendor["vendor_name"], "Hecttor")
        self.assertEqual(vendor["product_named"],
                         "Hermes noise cancellation")
        self.assertEqual(vendor["product_count_named_by_source"], 1)
        self.assertEqual(vendor["sdk_languages_platforms_reported"], 6)
        self.assertEqual(vendor["denoising_model_families_reported"], 2)

    def test_vendor_access_is_unverified(self) -> None:
        vendor = contract()["vendor_record"]
        self.assertFalse(vendor["onboarding_approved"])
        self.assertIsNone(vendor["immutable_release_version"])
        self.assertIsNone(vendor["artifact_sha256"])
        self.assertFalse(vendor["license_identity_verified"])
        self.assertFalse(vendor["vendor_claim_verified"])

    def test_task_boundary_does_not_invent_geometry(self) -> None:
        boundary = contract()["task_boundary"]
        self.assertEqual(boundary["reported_product"],
                         "Hermes noise cancellation")
        for key in ("reported_sample_rate_hz", "reported_frame_samples",
                    "reported_hop_samples", "reported_reset_contract",
                    "reported_drain_contract", "reported_channel_layout",
                    "reported_latency_ms", "reported_telemetry_terms"):
            self.assertIsNone(boundary[key], key)
        self.assertFalse(boundary["source_or_model_portability_claim"])


class ManifestTests(unittest.TestCase):
    def test_control_accepted_but_not_qualified(self) -> None:
        result = reference.validate_manifest(reference._manifest_control())
        self.assertEqual(result["status"], "accepted")
        self.assertFalse(result["qualifies"])
        self.assertGreater(result["checks"], 40)

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
        manifest.pop("vendor")
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "missing_field")
        manifest = reference._manifest_control()
        manifest["extra"] = True
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "unknown_field")

    def test_access_and_telemetry_gates(self) -> None:
        manifest = reference._manifest_control()
        manifest["vendor"]["onboarding_approved"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "access_not_approved")
        manifest = reference._manifest_control()
        manifest["sdk"]["telemetry_disclosure"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "telemetry_not_disclosed")

    def test_denoise_only_isolation_rejected(self) -> None:
        for name, code in (
                ("denoise_only", "denoise_not_isolated"),
                ("voice_boost_disabled", "voice_boost_enabled"),
                ("speed_control_disabled", "speed_control_enabled")):
            manifest = reference._manifest_control()
            manifest["sdk"][name] = False
            with self.subTest(name=name):
                self.assertEqual(reference.validate_manifest(manifest)["code"],
                                 code)

    def test_wrong_interpreter_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["runtime"]["python_version"] = "3.12.15"
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "wrong_python_version")

    def test_rate_and_false_rights_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["input"]["sample_rate_hz"] = 44100
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "unsupported_sample_rate")
        manifest = reference._manifest_control()
        manifest["rights"]["output_use"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "rights_not_cleared")

    def test_unconsented_input_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["input"]["consent"] = False
        self.assertEqual(reference.validate_manifest(manifest)["code"],
                         "rights_not_cleared")

    def test_unsafe_install_root_rejected(self) -> None:
        for value in ("opt/hecttor", "/opt/../etc/hecttor", "/opt/a/./b"):
            manifest = reference._manifest_control()
            manifest["sdk"]["install_root"] = value
            with self.subTest(value=value):
                self.assertEqual(reference.validate_manifest(manifest)["code"],
                                 "unsafe_path")

    def test_float_and_raw_cases_rejected(self) -> None:
        manifest = reference._manifest_control()
        manifest["input"]["clip_count"] = 1.0
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

    def test_output_bundle_control_accepted_not_scored(self) -> None:
        result = reference.validate_output_bundle(reference._output_control())
        self.assertEqual(result["status"], "accepted")
        self.assertFalse(result["qualifies"])
        admission = reference.admission_controls()
        self.assertEqual(admission["output_control"]["status"], "accepted")
        self.assertFalse(admission["output_control"]["qualifies"])
        self.assertFalse(admission["output_summary"]["vendor_output_present"])

    def test_output_bundle_adverse_cases(self) -> None:
        bundle = reference._output_control()
        bundle["outputs"][0]["finite"] = False
        self.assertEqual(reference.validate_output_bundle(bundle)["code"],
                         "nonfinite_output")
        bundle = reference._output_control()
        bundle["clip_count"] = 2
        self.assertEqual(reference.validate_output_bundle(bundle)["code"],
                         "clip_count_mismatch")
        bundle = reference._output_control()
        bundle["rights"]["publication"] = False
        self.assertEqual(reference.validate_output_bundle(bundle)["code"],
                         "rights_not_cleared")

    def test_manifest_contract_flags(self) -> None:
        value = reference.admission_contract_block()
        self.assertEqual(value["exact_interpreter"], "3.12.16")
        self.assertEqual(value["required_channels"], 1)
        self.assertFalse(value["accepted_control_qualifies"])
        self.assertFalse(value["runtime_or_vendor_sdk_invoked"])
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

    def test_boundary_all_false_except_task_local(self) -> None:
        scope = contract()["scope"]
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key != "task_local_only":
                self.assertFalse(value, key)
        boundary = contract()["boundary"]
        self.assertTrue(all(value is False for value in boundary.values()))

    def test_external_profile_rows(self) -> None:
        profile = contract()["external_profile"]
        rows = profile["requirement_rows"]
        self.assertEqual(len(rows), 8)
        self.assertEqual(profile["row_summary"]["blocked_count"], 6)
        self.assertEqual(profile["row_summary"]["documented_count"], 2)
        self.assertEqual(profile["row_summary"]["real_result_count"], 0)
        self.assertFalse(profile["row_summary"]["profile_satisfied"])
        self.assertTrue(profile["profile_source_check"][
            "all_phrases_present"])
        self.assertTrue(profile["fallback_disclosure_documented"])


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
        self.assertFalse(qualification["missing_result_promoted"])
        self.assertFalse(qualification["peer_result_inherited"])
        for key in ("real_result_present", "allowed_access_approved",
                    "vendor_terms_reviewed", "exact_product_release",
                    "sdk_artifact_present", "runtime_present",
                    "vendor_output_present", "vendor_output_scored",
                    "local_runtime_result", "external_profile_result",
                    "implementation_present", "reference_execution_result",
                    "listening_result", "device_timing_result",
                    "benchmark_result", "release_claim"):
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
                ("task_boundary", "task_boundary"),
                ("vendor_record", "vendor_record"),
                ("asset_registry", "asset_registry"),
                ("required_artifacts", "required_artifacts"),
                ("exact_blockers", "exact_blockers"),
                ("gates", "release_gates"),
                ("qualification", "qualification"),
                ("external_profile", "external_profile"),
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

    def test_admission_output_summary(self) -> None:
        admission = report()["admission"]
        self.assertEqual(admission["output_control"]["status"], "accepted")
        self.assertFalse(admission["output_control"]["qualifies"])
        self.assertFalse(admission["output_summary"]["scored_locally"])
        self.assertFalse(admission["output_summary"]["audio_read"])


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
                      "swarm/SDK-HECTTOR-scope")
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
        # REUSE-IgnoreStart
        token = "SPDX-License-" "Identifier: Apache-2.0"
        # REUSE-IgnoreEnd
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(token, head)
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          head)

    def test_license_sidecars(self) -> None:
        # REUSE-IgnoreStart
        token = "SPDX-License-" "Identifier: Apache-2.0"
        # REUSE-IgnoreEnd
        for name in ("contract.json", "report.json", "report.json.sha256",
                     "SOURCES.sha256"):
            sidecar = HERE / (name + ".license")
            self.assertTrue(sidecar.is_file(), name)
            text = sidecar.read_text(encoding="utf-8")
            self.assertIn(token, text)
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

    def test_mutable_board_absent_from_pins(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        self.assertNotIn("source:" + reference.BOARD_TASK_ROW, text)
        self.assertNotIn("sdk:" + reference.BOARD_TASK_ROW, text)


if __name__ == "__main__":
    unittest.main()
