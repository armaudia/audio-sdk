# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the CrisperWhisper package.

No network, no model, no CrisperWhisper runtime, no audio and no external
service is used. Every check is standard-library only.
"""

from __future__ import annotations

import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".joblib", ".lib",
    ".m4a", ".model", ".mp3", ".mp4", ".npz", ".o", ".onnx", ".opus",
    ".pcap", ".pcapng", ".pt", ".pth", ".pyc", ".safetensors", ".so",
    ".wasm", ".wav", ".weights", ".zip", ".dict", ".TextGrid",
}


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "dup.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_nan_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "nan.json"
            path.write_text('{"a":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_infinity_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "inf.json"
            path.write_text('{"a":Infinity}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_non_object_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "list.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)

    def test_canonical_bytes_are_stable(self) -> None:
        document = {"b": 2, "a": [3, 1]}
        self.assertEqual(reference.canonical_bytes(document),
                         reference.canonical_bytes(copy.deepcopy(document)))
        self.assertTrue(reference.canonical_text(document).endswith("\n"))


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_validates(self) -> None:
        reference.validate_contract(self.contract)

    def test_machine_readable_disposition(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertEqual(self.contract["mode"], "research-control")

    def test_eight_blocked_release_gates(self) -> None:
        gates = self.contract["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             self.contract["boundary"]["linked_row"])

    def test_required_artifacts(self) -> None:
        artifacts = self.contract["required_artifacts"]
        self.assertEqual(len(artifacts), 7)
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        self.assertFalse(artifacts[0]["blocked"])
        for artifact in artifacts[1:]:
            self.assertFalse(artifact["present"])
            self.assertFalse(artifact["verified"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])
            self.assertIsNone(artifact["revision"])

    def test_exact_blockers(self) -> None:
        blockers = self.contract["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        artifact_ids = {row["id"] for row in
                        self.contract["required_artifacts"]}
        gate_ids = {row["id"] for row in self.contract["release_gates"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(blocker["required_action"])
            for gate in blocker["linked_gates"]:
                self.assertIn(gate, gate_ids)

    def test_qualification_flags(self) -> None:
        qualification = self.contract["qualification"]
        self.assertTrue(qualification["not_qualified"])
        self.assertTrue(qualification["all_release_gates_blocked"])
        for key in ("real_result_present", "crisperwhisper_source_present",
                    "weights_present", "runtime_present",
                    "model_card_present", "commercial_license_granted",
                    "verbatim_result", "filler_result", "lexical_wer_result",
                    "boundary_result", "finite_output_result",
                    "baseline_result", "device_timing_result",
                    "rate_profile_result", "listening_result",
                    "benchmark_result", "release_claim",
                    "missing_result_promoted"):
            self.assertFalse(qualification[key], key)

    def test_sections_are_blocked(self) -> None:
        for key, expected in (
                ("rate_profile_requirements", 8),
                ("quality_outcomes", 5),
                ("timing_requirements", 4)):
            rows = self.contract[key]
            self.assertEqual(len(rows), expected)
            for row in rows:
                self.assertEqual(row["status"], "blocked")

    def test_models_are_absent_and_noncommercial(self) -> None:
        models = self.contract["exact_models"]
        crisp = models["crisperwhisper"]
        self.assertFalse(crisp["source_present"])
        self.assertFalse(crisp["weights_present"])
        self.assertFalse(crisp["digest_verified"])
        self.assertFalse(crisp["model_card_present"])
        self.assertFalse(crisp["commercial_use_granted"])
        self.assertFalse(crisp["downloaded_or_reconstructed"])
        self.assertEqual(crisp["code_license_recorded"], "MIT")
        self.assertEqual(crisp["weights_license_recorded"], "CC-BY-NC-4.0")
        self.assertEqual(crisp["verbatim_tags_recorded"],
                         ["[um]", "[uh]", "[laughter]"])
        self.assertIsNone(crisp["weights_model_id"])
        self.assertIsNone(crisp["weights_sha256"])
        self.assertFalse(models["runtime"]["present"])
        self.assertFalse(models["reference_transcript"]["present"])

    def test_report_contract_digest(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_report_copies_contract(self) -> None:
        for field in ("disposition", "qualification", "required_artifacts",
                      "exact_blockers", "scope", "boundary",
                      "public_v0_geometry", "non_claims", "required_results",
                      "exact_models", "historical_recipe"):
            self.assertEqual(self.report[field], self.contract[field], field)
        self.assertEqual(self.report["gates"],
                         self.contract["release_gates"])
        self.assertEqual(self.report["rate_profile"]["rows"],
                         self.contract["rate_profile_requirements"])
        self.assertEqual(self.report["quality_outcomes"]["rows"],
                         self.contract["quality_outcomes"])
        self.assertEqual(self.report["timing"]["rows"],
                         self.contract["timing_requirements"])

    def test_report_has_no_floats(self) -> None:
        reference._no_floats(self.report)

    def test_report_is_canonical(self) -> None:
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), digest)
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")

    def test_scope_is_task_local(self) -> None:
        scope = self.contract["scope"]
        self.assertEqual(scope["write_scope"], reference.WRITE_SCOPE)
        self.assertTrue(scope["task_local_only"])
        for key in ("provider_registered", "adapter_implemented",
                    "processor_exposed", "public_abi_changed",
                    "registry_or_default_changed",
                    "shared_build_or_ci_changed", "real_assets_used",
                    "weights_used", "network_used", "listening_performed",
                    "device_timing_measured", "benchmark_run",
                    "release_claim"):
            self.assertFalse(scope[key], key)

    def test_public_v0_geometry_unchanged(self) -> None:
        geometry = self.contract["public_v0_geometry"]
        self.assertEqual(geometry, {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "float32",
            "frame_samples": 160,
            "changed": False,
        })

    def test_licensing_blocks_commercial_use(self) -> None:
        licensing = self.contract["licensing"]
        self.assertFalse(licensing["code_terms_reviewed"])
        self.assertFalse(licensing["weights_terms_reviewed"])
        self.assertFalse(licensing["commercial_use_granted"])
        self.assertFalse(licensing["output_use_defined"])
        self.assertFalse(licensing["vendored_third_party_bytes"])


class AdmissionTests(unittest.TestCase):
    def test_control_is_accepted_and_unchanged(self) -> None:
        manifest = reference.control_manifest()
        before = copy.deepcopy(manifest)
        reference.validate_manifest(manifest)
        self.assertEqual(manifest, before)

    def test_every_adverse_case_is_rejected(self) -> None:
        cases = reference.admission_cases()
        self.assertEqual(len(cases), 70)
        names = [case["id"] for case in cases]
        self.assertEqual(len(set(names)), len(names))
        for case in cases:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])
            self.assertNotIn("unexpected:", case["code"])

    def test_admission_summary(self) -> None:
        admission = reference.build_admission()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], 70)
        self.assertEqual(summary["rejected_count"], 70)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        for key in ("state_advanced_on_rejection", "runtime_invoked",
                    "audio_read", "weights_loaded", "model_executed",
                    "network_used"):
            self.assertFalse(summary[key], key)
        self.assertFalse(admission["control"]["qualifies"])
        self.assertEqual(admission["control"]["label"],
                         "synthetic_schema_control_not_evidence")

    def test_nonfinite_values_rejected(self) -> None:
        for key in ("lexical_wer", "filler_recall", "laughter_recall",
                    "boundary_mae_ms", "boundary_median_abs_error_ms",
                    "boundary_within_50ms_fraction"):
            manifest = reference.control_manifest()
            manifest["outcomes"][key] = float("nan")
            with self.assertRaises(ValueError):
                reference.validate_manifest(manifest)

    def test_commercial_grant_and_claim_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["crisperwhisper"]["commercial_use_granted"] = True
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)
        manifest = reference.control_manifest()
        manifest["rights"]["claims_qualified"] = True
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_single_annotator_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["reference"]["annotator_count"] = 1
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)


class ScorerControlTests(unittest.TestCase):
    def test_synthetic_scorer_exact(self) -> None:
        control = reference.scorer_control()
        self.assertEqual(control["result"], {
            "reference_tokens": 10,
            "hypothesis_tokens": 10,
            "matched_tokens": 9,
            "substitutions": 0,
            "deletions": 1,
            "insertions": 1,
            "lexical_reference": 6,
            "lexical_substitutions": 0,
            "lexical_deletions": 0,
            "lexical_insertions": 1,
            "lexical_wer": "0.166667",
            "filler_reference": 3,
            "filler_matched": 2,
            "filler_recall": "0.666667",
            "laughter_reference": 1,
            "laughter_matched": 1,
            "laughter_recall": "1.000000",
            "tag_reference": 4,
            "tag_matched": 3,
            "tag_recall": "0.750000",
            "boundary_error_count": 18,
            "boundary_mae_ms": "6.388889",
            "boundary_median_abs_error_ms": "5.000000",
            "boundary_within_50ms_fraction": "1.000000",
        })
        self.assertTrue(control["synthetic"])
        self.assertFalse(control["qualifies"])
        self.assertFalse(control["model_invoked"])
        self.assertFalse(control["audio_read"])
        self.assertEqual(control["label"],
                         "synthetic_verbatim_control_not_evidence")

    def test_substitution_does_not_shift_later_matches(self) -> None:
        reference_words = [
            {"text": "a", "kind": "lexical", "start_ms": 0, "end_ms": 100},
            {"text": "b", "kind": "lexical", "start_ms": 100, "end_ms": 200},
            {"text": "c", "kind": "lexical", "start_ms": 200, "end_ms": 300},
        ]
        hypothesis = [
            {"text": "a", "kind": "lexical", "start_ms": 10, "end_ms": 110},
            {"text": "x", "kind": "lexical", "start_ms": 120, "end_ms": 220},
            {"text": "c", "kind": "lexical", "start_ms": 210, "end_ms": 310},
        ]
        operations = reference.align_verbatim(reference_words, hypothesis)
        matches = [operation["reference"]["text"] for operation in operations
                   if operation["op"] == "M"]
        self.assertEqual(matches, ["a", "c"])
        result = reference.score_verbatim(reference_words, hypothesis)
        self.assertEqual(result["substitutions"], 1)
        self.assertEqual(result["matched_tokens"], 2)

    def test_filler_replacement_is_delete_plus_insert(self) -> None:
        reference_words = [
            {"text": "[um]", "kind": "filler", "start_ms": 0, "end_ms": 100},
        ]
        hypothesis = [
            {"text": "so", "kind": "lexical", "start_ms": 0, "end_ms": 100},
        ]
        result = reference.score_verbatim(reference_words, hypothesis)
        self.assertEqual(result["substitutions"], 0)
        self.assertEqual(result["deletions"], 1)
        self.assertEqual(result["insertions"], 1)
        self.assertEqual(result["matched_tokens"], 0)

    def test_empty_alignment_is_zero(self) -> None:
        result = reference.score_verbatim([], [])
        self.assertEqual(result["matched_tokens"], 0)
        self.assertEqual(result["boundary_error_count"], 0)
        self.assertEqual(result["boundary_mae_ms"], "0.000000")

    def test_token_normalisation_rejects_non_ascii(self) -> None:
        with self.assertRaises(ValueError):
            reference.normalize_token("caf\u00e9")
        with self.assertRaises(ValueError):
            reference.normalize_token("")
        with self.assertRaises(ValueError):
            reference.normalize_token("...")
        self.assertEqual(reference.normalize_token("Hello,"), "hello")

    def test_invalid_token_time_rejected(self) -> None:
        for start, end in ((-1, 10), (20, 10), (0, 60001)):
            row = {"text": "a", "kind": "lexical", "start_ms": start,
                   "end_ms": end}
            with self.assertRaises(ValueError):
                reference.align_verbatim([row], [])


class ProvenanceTests(unittest.TestCase):
    def test_source_pins(self) -> None:
        rows = reference.pin_rows(reference.SOURCE_PINS,
                                  reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.SOURCE_PINS))
        for relative, row in rows.items():
            self.assertTrue(row["verified"], relative)
            self.assertEqual(row["sha256"], row["actual"])

    def test_boundary_pins(self) -> None:
        rows = reference.pin_rows(reference.BOUNDARY_PINS,
                                  reference.WORKTREE)
        self.assertEqual(len(rows), len(reference.BOUNDARY_PINS))
        for relative, row in rows.items():
            self.assertTrue(row["verified"], relative)

    def test_board_projection_excludes_mutable_fields(self) -> None:
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(set(row), set(reference.BOARD_ROW_FIELDS))
        for forbidden in ("status", "owner", "claim", "review", "handoff",
                          "blocked_reason", "dispatch_priority"):
            self.assertNotIn(forbidden, row)
        self.assertEqual(row["id"], reference.TASK)
        self.assertEqual(row["component"], reference.COMPONENT_ID)
        self.assertEqual(row["mode"], reference.MODE)
        self.assertEqual(row["depends_on"],
                         ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"])

    def test_linked_rows(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))
        self.assertEqual(reference.linked_rows_digest(rows),
                         reference.linked_rows_digest())

    def test_sources_manifest_excludes_mutable_board(self) -> None:
        payload = run.sources_bytes().decode("ascii")
        self.assertNotIn("plan/swarm/TASKS.json", payload)
        self.assertIn(
            "source:cpp-library/pipeline-validation/"
            "playback-speed-candidates.md", payload)
        self.assertIn("CONTRACTS.md", payload)
        self.assertNotIn("SOURCES.sha256  ", payload)

    def test_absence_probes_are_fixed_and_absent(self) -> None:
        workspace = reference.absence_probes()
        external = reference.external_absence_probes()
        self.assertEqual(len(workspace), 6)
        self.assertEqual(len(external), 6)
        summary = reference.absence_summary(workspace, external)
        self.assertEqual(summary["probe_count"], 12)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        for key in ("recursive_workspace_walk", "download_attempted",
                    "network_used", "source_or_runtime_imported",
                    "weights_loaded", "model_executed", "audio_read"):
            self.assertFalse(summary[key], key)

    def test_source_presence(self) -> None:
        presence = reference.source_presence()
        self.assertTrue(presence["candidate_note_and_inventory_present"])
        self.assertFalse(presence["source_repository_present"])
        self.assertFalse(presence["weights_present"])
        self.assertFalse(presence["weights_model_id_recorded"])
        self.assertFalse(presence["weights_digest_recorded"])
        self.assertFalse(presence["runtime_present"])
        self.assertFalse(presence["run_artifacts_present"])
        self.assertFalse(
            presence["exact_source_weights_runtime_conjunction_present"])
        for key in ("weights_used", "runtime_imported", "audio_read",
                    "model_executed"):
            self.assertFalse(presence[key], key)

    def test_recipe_provenance(self) -> None:
        recipe = reference.recipe_provenance()
        self.assertEqual(recipe["checks_present"],
                         recipe["checks_required"])
        self.assertFalse(recipe["executed_here"])
        self.assertFalse(recipe["saved_run_artifacts"])
        historical = reference.historical_recipe()
        self.assertFalse(historical["crop_recipe_recorded"])
        self.assertFalse(historical["runtime_recipe_recorded"])
        self.assertFalse(historical["scoring_recipe_recorded"])
        self.assertFalse(historical["executed_here"])

    def test_documented_claims_are_provenance_only(self) -> None:
        claims = reference.documented_claims()
        self.assertEqual(claims["code_license_recorded"], "MIT")
        self.assertEqual(claims["weights_license_recorded"],
                         "CC-BY-NC-4.0")
        self.assertEqual(claims["verbatim_tags_recorded"],
                         ["[um]", "[uh]", "[laughter]"])
        self.assertEqual(claims["word_boundary_range_ms_recorded"], "30-41")
        self.assertFalse(claims["commercial_use_permitted"])
        self.assertFalse(claims["source_revision_recorded"])
        self.assertFalse(claims["weights_model_id_recorded"])
        self.assertFalse(claims["weights_digest_recorded"])
        self.assertFalse(claims["runtime_version_recorded"])
        self.assertFalse(claims["measured_result_recorded"])
        self.assertFalse(claims["reproduced_here"])
        self.assertFalse(claims["used_for_evidence"])
        self.assertFalse(claims["qualifies"])


class ArtifactTests(unittest.TestCase):
    def test_committed_report_and_sidecar(self) -> None:
        report_path = HERE / "report.json"
        sidecar_path = HERE / "report.json.sha256"
        if not report_path.is_file() or not sidecar_path.is_file():
            self.skipTest("generated artifacts not present yet")
        payload = report_path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual(sidecar_path.read_text(encoding="ascii"),
                         f"{digest}  report.json\n")
        report = reference.read_strict_json(report_path)
        self.assertEqual(payload, reference.canonical_bytes(report))
        self.assertFalse(sidecar_path.is_symlink())

    def test_no_forbidden_assets(self) -> None:
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), FORBIDDEN_SUFFIXES,
                             path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name, {"provider.json", "adapter.json",
                                         "CMakeLists.txt"})

    def test_python_spdx(self) -> None:
        license_tag = "SPDX-License-" + "Identifier: Apache-2.0"
        copyright_tag = "SPDX-FileCopyrightText: " + \
            "2026 Tsakanyan Hovhannes"
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(license_tag, head)
            self.assertIn(copyright_tag, head)

    def test_license_sidecars(self) -> None:
        license_tag = "SPDX-License-" + "Identifier: Apache-2.0"
        copyright_tag = "SPDX-FileCopyrightText: " + \
            "2026 Tsakanyan Hovhannes"
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "report.json.license", "report.json.sha256.license"):
            path = HERE / name
            self.assertTrue(path.is_file(), name)
            text = path.read_text(encoding="utf-8")
            self.assertIn(license_tag, text)
            self.assertIn(copyright_tag, text)

    def test_readme_expected_digest(self) -> None:
        readme = HERE / "README.md"
        report = HERE / "report.json"
        if not readme.is_file() or not report.is_file():
            self.skipTest("generated artifacts not present yet")
        digest = hashlib.sha256(report.read_bytes()).hexdigest()
        self.assertIn(digest, readme.read_text(encoding="utf-8"))

    def test_json_files_are_strict(self) -> None:
        for name in ("contract.json", "report.json"):
            path = HERE / name
            if path.is_file():
                reference.read_strict_json(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
