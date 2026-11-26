# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance and scope regression tests for the NeuralKalmanAHS blocker."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class CanonicalAndStrictJsonTests(unittest.TestCase):
    def test_report_is_canonical_and_deterministic(self):
        first, first_digest = reference.canonical_report()
        second, second_digest = reference.canonical_report()
        third, third_digest = reference.canonical_report()
        self.assertEqual(first, second)
        self.assertEqual(second, third)
        self.assertEqual({first_digest, second_digest, third_digest},
                         {sha256(first.encode("ascii"))})
        self.assertEqual(first, reference.canonical_text(
            json.loads(first, object_pairs_hook=dict)))
        self.assertFalse(first.endswith("\n"))

    def test_report_contains_no_floats(self):
        report = reference.build_report()
        reference.assert_no_float(report)

    def test_strict_json_rejects_duplicate_key(self):
        with self.assertRaises(reference.EvidenceError) as caught:
            reference.loads_strict('{"a":1,"a":2}')
        self.assertEqual(caught.exception.code, "DUPLICATE_KEY")

    def test_strict_json_rejects_nonfinite(self):
        for payload in ('{"a":NaN}', '{"a":Infinity}',
                        '{"a":-Infinity}'):
            with self.assertRaises(reference.EvidenceError) as caught:
                reference.loads_strict(payload)
            self.assertEqual(caught.exception.code, "NONFINITE_CONSTANT")

    def test_strict_json_rejects_floats_and_trailing_data(self):
        with self.assertRaises(reference.EvidenceError) as caught:
            reference.loads_strict('{"a":1.5}')
        self.assertEqual(caught.exception.code, "FLOAT_NOT_ALLOWED")
        with self.assertRaises(reference.EvidenceError):
            reference.loads_strict('{"a":1} extra')

    def test_strict_json_rejects_non_object_root(self):
        with self.assertRaises(reference.EvidenceError) as caught:
            reference.loads_strict("[1,2,3]")
        self.assertEqual(caught.exception.code, "JSON_NOT_OBJECT")


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.report = reference.build_report()
        self.contract = reference.build_contract()

    def test_decision_and_qualification(self):
        for document in (self.report, self.contract):
            self.assertEqual(document["decision"], "DEFER")
            self.assertEqual(document["status"],
                             "proposal_only_not_qualified")
            self.assertIs(document["incomplete"], True)
            self.assertIs(document["proposal_only"], True)
            self.assertEqual(document["qualification_status"],
                             "not_qualified")
        self.assertEqual(self.report["qualification"]["status"],
                         "not_qualified")
        self.assertIs(
            self.report["qualification"]["candidate_qualified"], False)
        self.assertIs(self.report["no_missing_result_qualifies_candidate"],
                      True)

    def test_eight_release_gates_all_blocked(self):
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         list(reference.GATE_IDS))
        self.assertEqual(len(gates), 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertIs(gate["qualifies"], False)
            self.assertEqual(gate["linked_row"]["task_id"],
                             reference.TASK)
            self.assertEqual(gate["linked_row"]["component"],
                             reference.COMPONENT_ID)
        self.assertEqual(self.report["remaining_gates"],
                         list(reference.GATE_IDS))
        self.assertEqual(self.contract["release_gates"], gates)

    def test_required_artifacts_and_blockers(self):
        artifacts = self.report["required_artifacts"]
        self.assertEqual([row["id"] for row in artifacts],
                         list(reference.ARTIFACT_IDS))
        self.assertEqual(len(artifacts), 7)
        for row in artifacts:
            self.assertEqual(row["status"], "absent")
            self.assertIs(row["present"], False)
            self.assertIs(row["verified"], False)
            self.assertIs(row["blocked"], True)
            self.assertIsNone(row["sha256"])
        self.assertEqual(self.report["missing_artifacts"],
                         list(reference.ARTIFACT_IDS))
        blockers = self.report["exact_blockers"]
        self.assertEqual([row["id"] for row in blockers],
                         list(reference.BLOCKER_IDS))
        self.assertEqual(len(blockers), 6)
        for row in blockers:
            self.assertEqual(row["status"], "open")
            self.assertIs(row["qualifies"], False)
            self.assertTrue(row["linked_gates"])

    def test_integration_variants_stay_separate(self):
        variants = self.report["integration_variants"]
        self.assertEqual(variants["variant_count"], 2)
        self.assertEqual(sorted(variants["variants"]),
                         sorted(reference.VARIANT_IDS))
        self.assertEqual(
            variants["variants"]["covariance"]["integration_point"],
            "kalman_covariance_or_process_noise")
        self.assertEqual(
            variants["variants"]["reference"]["integration_point"],
            "kalman_reference_estimate")
        for variant in variants["variants"].values():
            self.assertIs(variant["present"], False)
            self.assertIs(variant["implemented_here"], False)
            self.assertIs(variant["measured_here"], False)
            self.assertIs(variant["qualifies_candidate"], False)
            self.assertIsNone(variant["result"])
            self.assertIsNone(variant["metrics"])
        distinction = variants["distinction"]
        self.assertIs(distinction["distinct_integration_points"], True)
        self.assertIs(distinction["exact_variant_identity_recorded"], False)
        self.assertIs(variants["qualifies_candidate"], False)

    def test_author_reported_results_are_not_reproduced(self):
        results = self.report["author_reported_results"]
        self.assertIs(results["reproduced_here"], False)
        self.assertIs(results["qualifies_candidate"], False)
        self.assertIsNone(results["local_metrics"])
        self.assertEqual(results["neuralkalmanahs"]["sdr_db"],
                         ["2.65", "1.98", "1.45"])
        self.assertEqual(results["neuralkalmanahs"]["pesq"],
                         ["2.33", "2.17", "2.04"])
        self.assertEqual(results["neuralkalmanahs"]["variant_attribution"],
                         "not_disambiguated_in_note")

    def test_prior_pilot_is_not_candidate_evidence(self):
        controls = self.report["research_controls"]
        self.assertIs(controls["rerun_here"], False)
        self.assertIs(controls["qualifies_candidate"], False)
        self.assertEqual(controls["candidate"],
                         "none: classical feedback controls, not NeuralKalmanAHS")
        for table in ("synthetic_proxy", "measured_path"):
            for row in controls[table]["rows"]:
                self.assertEqual(len(row), 3 if table == "synthetic_proxy"
                                 else 4)


class ProbeAndAdmissionTests(unittest.TestCase):
    def test_absence_probes(self):
        self.assertIs(reference.source_probe()["present"], False)
        self.assertIs(reference.checkpoint_probe()["present"], False)
        self.assertIs(reference.runtime_probe()["pinned"], False)
        self.assertIs(reference.cohort_probe()["present"], False)
        self.assertIs(
            reference.license_probe()["license_text_present"], False)
        self.assertEqual(reference.license_probe()["review"], "blocked")
        self.assertIs(reference.rights_probe()["use_approved"], False)

    def test_geometry_is_not_inferred(self):
        geometry = reference.geometry()
        self.assertIs(geometry["declared_candidate_geometry_recorded"], False)
        self.assertEqual(geometry["declared_sample_rates_hz"], [])
        self.assertIsNone(geometry["declared_kalman_state_dimension"])
        self.assertIsNone(geometry["declared_covariance_parameterisation"])
        self.assertIs(geometry["local_harness_is_candidate_geometry"], False)
        self.assertIs(geometry["candidate_output"], False)

    def test_base_requests_validate_but_admit_defers(self):
        for variant in reference.VARIANT_IDS:
            request = reference.base_request(variant)
            validated = reference.validate_request(request)
            self.assertEqual(validated["integration_variant"], variant)
            admitted = reference.admit(request)
            self.assertEqual(admitted["status"], "DEFER")
            self.assertIs(admitted["admissible"], False)
            self.assertIs(admitted["qualifies_candidate"], False)
            self.assertIsNone(admitted["metrics"])
            self.assertIn("source_absent", admitted["blockers"])

    def test_probe_candidate_fails_closed(self):
        with self.assertRaises(reference.EvidenceError) as caught:
            reference.probe_candidate(reference.base_request())
        self.assertEqual(caught.exception.code, "ARTIFACTS_ABSENT")

    def test_adverse_requests_all_rejected(self):
        cases = reference.adverse_cases()
        self.assertTrue(cases["all_rejected"])
        self.assertEqual(cases["accepted_count"], 0)
        self.assertGreaterEqual(cases["case_count"], 50)
        ids = {case["id"] for case in cases["cases"]}
        for required in ("unknown_variant", "missing_variant",
                         "bool_variant", "nonfinite_nan", "nonfinite_inf",
                         "out_of_range", "bool_sample", "wrong_1024_frame",
                         "incomplete_asset_manifest"):
            self.assertIn(required, ids)

    def test_json_adverse_all_rejected(self):
        cases = reference.json_adverse_cases()
        self.assertTrue(cases["all_rejected"])
        self.assertEqual(cases["accepted_count"], 0)
        self.assertIn("float_value", {case["id"] for case in cases["cases"]})

    def test_missing_result_is_blocked(self):
        result = reference.missing_result("placeholder")
        self.assertEqual(result["status"], "blocked")
        self.assertIs(result["qualifies_candidate"], False)
        self.assertIsNone(result["metrics"])


class BoardAndPinTests(unittest.TestCase):
    def test_board_identity_is_stable_and_mutable_fields_excluded(self):
        report = reference.build_report()
        row = report["board_row"]
        self.assertEqual(row["id"], reference.TASK)
        self.assertEqual(row["component"], reference.COMPONENT_ID)
        self.assertEqual(row["mode"], reference.MODE)
        self.assertEqual(row["repository"], reference.REPOSITORY)
        self.assertEqual(row["depends_on"], list(reference.DEPENDS_ON))
        self.assertIs(report["board_full_file_hashed"], False)
        board_digest = reference.sha256_file(
            reference.SOURCE_ROOT / reference.BOARD_TASK_ROW)
        for key, value in report.items():
            if isinstance(value, str):
                self.assertNotEqual(value, board_digest,
                                    "full board digest leaked into " + key)
        linked = report["board_links"]
        self.assertEqual([item["id"] for item in linked],
                         [reference.TASK] + list(reference.DEPENDS_ON))
        self.assertEqual(report["board_link_projection_sha256"],
                         reference.object_digest(linked))

    def test_contract_matches_report_identity_and_gates(self):
        report = reference.build_report()
        contract = reference.build_contract()
        reference.validate_contract(contract)
        for key in ("task", "title", "component", "mode", "repository",
                    "base_commit", "branch", "decision", "status",
                    "qualification_status"):
            self.assertEqual(report[key], contract[key])
        self.assertEqual(report["release_gates"],
                         contract["release_gates"])
        self.assertEqual(report["required_artifacts"],
                         contract["required_artifacts"])
        self.assertEqual(report["board_link_projection_sha256"],
                         contract["board_link_projection_sha256"])

    def test_sources_manifest_is_exact(self):
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        rows = reference.parse_pin_lines(text)
        keys = {path for _, path in rows}
        self.assertEqual(keys, reference.allowed_pin_keys())
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", keys)
        self.assertNotIn(reference.TASK_PREFIX + "README.md", keys)
        for digest, path in rows:
            if path.startswith("source:"):
                target = reference.SOURCE_ROOT / path[len("source:"):]
            elif path.startswith("sdk:"):
                target = reference.WORKTREE / path[len("sdk:"):]
            else:
                target = reference.WORKTREE / path
            self.assertEqual(digest, reference.sha256_file(target), path)

    def test_readme_tables_are_exact(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        counts = reference.verify_readme_digests(text)
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"],
                         len(reference.BOUNDARY_PINS))
        self.assertEqual(counts["artifacts"],
                         len(reference.local_manifest_paths()))

    def test_artifacts_are_canonical_and_match_sidecar(self):
        report_bytes = (HERE / "report.json").read_bytes()
        report = reference.loads_strict(report_bytes.decode("ascii"))
        text, digest = reference.canonical_report(report)
        self.assertEqual(report_bytes.decode("ascii"), text)
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, digest + "  report.json\n")
        contract_bytes = (HERE / "contract.json").read_bytes()
        contract = reference.loads_strict(contract_bytes.decode("ascii"))
        self.assertEqual(contract_bytes.decode("ascii"),
                         reference.canonical_text(contract))
        reference.validate_contract(contract)

    def test_no_prohibited_files(self):
        prohibited = {".wav", ".flac", ".mp3", ".ogg", ".opus", ".onnx",
                      ".pt", ".pth", ".ckpt", ".safetensors", ".bin", ".so",
                      ".dylib", ".a", ".o", ".zip", ".tar", ".gz", ".whl",
                      ".npy", ".pyc", ".wasm"}
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), prohibited, path.name)
            self.assertFalse(path.is_symlink(), path.name)


class ScopeTests(unittest.TestCase):
    def test_installed_v0_unchanged(self):
        boundary = reference.boundary()
        self.assertIs(boundary["installed_v0_unchanged"], True)
        self.assertEqual(boundary["format"]["sample_rate_hz"], 16000)
        self.assertEqual(boundary["format"]["channels"], 1)
        self.assertEqual(boundary["format"]["frame_samples"], 160)
        self.assertEqual(boundary["format"]["sample_format"], "f32")
        self.assertIs(boundary["provider_registered"], False)
        self.assertIs(boundary["public_api_abi_changed"], False)
        self.assertIs(boundary["shared_cmake_changed"], False)
        self.assertIs(boundary["ci_changed"], False)
        self.assertIs(boundary["real_corpus_or_weights"], False)
        self.assertIs(boundary["release_claim"], False)

    def test_external_boundary_closed(self):
        external = reference.external_boundary()
        self.assertIs(external["adapter_implemented"], False)
        self.assertIs(external["adapter_default_registration"], False)
        self.assertIs(external["automatic_discovery"], False)
        self.assertEqual(external["fallback"], "none")
        self.assertIs(external["source_present"], False)
        self.assertIs(external["checkpoint_present"], False)

    def test_non_claims_cover_required_limits(self):
        text = " ".join(reference.NON_CLAIMS).lower()
        for phrase in ("no neuralkalmanahs source", "no installed v0",
                       "no provider is registered", "no real corpus",
                       "no device timing", "no missing, rejected"):
            self.assertIn(phrase, text)

    def test_license_sidecars(self):
        needle = "SPDX-License-" "Identifier: Apache-2.0"
        copyright_line = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license",
                     "SOURCES.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(needle, text)
            self.assertIn(copyright_line, text)


if __name__ == "__main__":
    unittest.main()
