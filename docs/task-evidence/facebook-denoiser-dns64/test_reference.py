# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the SDK-FACEBOOK-DENOISER-DNS64 blocker package."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
GATE_IDS = ["RG-0" + str(number) for number in range(1, 9)]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report_json() -> dict:
    return json.loads((HERE / "report.json").read_text(encoding="utf-8"))


def contract_json() -> dict:
    return json.loads((HERE / "contract.json").read_text(encoding="utf-8"))


class ReportTests(unittest.TestCase):
    def test_report_is_canonical_and_finite(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        value = reference.strict_json_loads(payload.decode("utf-8"))
        self.assertIsInstance(value, dict)
        self.assertEqual(reference.canonical_bytes(value) + b"\n", payload)
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))
        self.assertTrue(reference.finite_json(value))

    def test_report_regeneration_is_byte_identical(self) -> None:
        committed = (HERE / "report.json").read_bytes()
        self.assertEqual(reference.report_bytes(), committed)
        self.assertEqual(reference.report_bytes(), reference.report_bytes())

    def test_identity_fields(self) -> None:
        report = report_json()
        self.assertEqual(report["task"], "SDK-FACEBOOK-DENOISER-DNS64")
        self.assertEqual(report["component"], "facebook-denoiser-dns64")
        self.assertEqual(report["mode"], "feasibility")
        self.assertEqual(report["verification_profile"], "enhancement")
        self.assertEqual(report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(report["branch"], reference.BRANCH)

    def test_decision_fields_are_defer_not_qualified(self) -> None:
        report = report_json()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertIs(report["incomplete"], True)
        self.assertIs(report["proposal_only"], True)
        self.assertEqual(report["qualification_status"], "not_qualified")
        qualification = report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["readiness"], "incomplete")
        self.assertEqual(qualification["decision"], "DEFER")
        self.assertIs(qualification["candidate_qualified"], False)
        self.assertIs(qualification["upstream_parity"], False)
        self.assertIs(qualification["all_required_results_present"], False)

    def test_candidate_never_qualifies(self) -> None:
        report = report_json()
        candidate = report["candidates"][reference.CANDIDATE]
        self.assertEqual(
            candidate["status"],
            "blocked_source_weights_runtime_license_and_fixture_absent")
        self.assertIsNone(candidate["metrics"])
        self.assertIsNone(candidate["result"])
        self.assertIs(candidate["qualifies_candidate"], False)
        self.assertIs(report["no_missing_result_qualifies_candidate"], True)

    def test_required_artifacts_are_six_and_absent(self) -> None:
        report = report_json()
        artifacts = report["required_artifacts"]
        self.assertEqual([row["id"] for row in artifacts],
                         ["A1", "A2", "A3", "A4", "A5", "A6"])
        for row in artifacts:
            self.assertEqual(row["status"], "absent")
            self.assertIsNone(row["sha256"])
            self.assertIsNone(row["byte_count"])
            self.assertIs(row["rights_reviewed"], False)
        self.assertEqual(len(report["missing_artifacts"]), 6)

    def test_eight_release_gates_blocked(self) -> None:
        report = report_json()
        gates = report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates], GATE_IDS)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(gate["reason"] for gate in gates))
        self.assertTrue(all(gate["reopen"] for gate in gates))
        self.assertEqual(report["remaining_gates"], GATE_IDS)
        self.assertEqual(report["gates"], GATE_IDS)


class ProbeTests(unittest.TestCase):
    def test_source_absent(self) -> None:
        probe = reference.source_probe()
        self.assertEqual(probe["status"], "blocked_source_absent")
        self.assertIs(probe["present"], False)
        self.assertEqual(probe["found"], [])
        for key in ("revision", "tree_digest", "file_count", "license"):
            self.assertIsNone(probe[key])

    def test_weights_absent(self) -> None:
        probe = reference.weights_probe()
        self.assertEqual(probe["status"], "blocked_weights_absent")
        self.assertIs(probe["present"], False)
        self.assertEqual(probe["found"], [])
        self.assertEqual(probe["variant"], "dns64")
        for key in ("artifact_path", "byte_count", "sha256",
                    "checkpoint_terms", "lineage"):
            self.assertIsNone(probe[key])

    def test_runtime_unpinned(self) -> None:
        probe = reference.runtime_probe()
        self.assertEqual(probe["status"], "blocked_runtime_unpinned")
        self.assertIs(probe["pinned"], False)
        self.assertEqual(probe["lockfiles"], [])
        self.assertTrue(all(value is False
                            for value in probe["modules"].values()))
        for key in ("framework", "framework_version", "sha256"):
            self.assertIsNone(probe[key])

    def test_license_noncommercial_not_approved(self) -> None:
        probe = reference.license_probe()
        self.assertEqual(probe["status"],
                         "blocked_noncommercial_use_not_approved")
        self.assertEqual(probe["reported_name"], "CC-BY-NC-4.0")
        self.assertIs(probe["license_text_present"], False)
        self.assertIs(probe["commercial_use_approved"], False)
        self.assertIs(probe["redistribution_approved"], False)
        self.assertIs(probe["host_target_approved"], False)
        self.assertIsNone(probe["license_text_sha256"])

    def test_fixture_absent(self) -> None:
        probe = reference.fixture_probe()
        self.assertEqual(probe["status"], "blocked_matched_fixture_absent")
        self.assertIs(probe["present"], False)
        self.assertEqual(probe["found"], [])
        self.assertIs(probe["corpus_rights"], False)
        self.assertIs(probe["paired_clean_reference"], False)
        self.assertIs(probe["scorer_pinned"], False)

    def test_geometry_is_not_invented(self) -> None:
        geometry = reference.geometry()
        for key in ("documented_sample_rate_hz", "documented_channels",
                    "documented_frame_samples", "documented_hop_samples",
                    "documented_state", "documented_lookahead_samples",
                    "documented_output_scaling",
                    "documented_content_delay_samples",
                    "v0_can_represent_declared_input"):
            self.assertIsNone(geometry[key])
        self.assertIs(geometry["candidate_geometry_in_pinned_sources"],
                      False)
        self.assertIs(geometry["verified_here"], False)
        self.assertIs(geometry["measured_here"], False)
        self.assertIs(geometry["candidate_output"], False)

    def test_external_boundary_is_closed(self) -> None:
        boundary = reference.EXTERNAL_BOUNDARY
        self.assertEqual(boundary["license_reported"], "CC-BY-NC-4.0")
        for key in ("license_text_present", "commercial_use_approved",
                    "redistribution_approved", "derived_output_approved",
                    "host_target_approved", "source_present",
                    "weights_present", "local_runtime_present",
                    "candidate_output_present", "adapter_implemented",
                    "adapter_default_registration", "automatic_discovery"):
            self.assertIs(boundary[key], False)
        self.assertEqual(boundary["fallback"], "none")


class ValidationTests(unittest.TestCase):
    def test_structural_request_is_valid_but_unverified(self) -> None:
        parsed = reference.validate_request(reference._base_request())
        self.assertIs(parsed["geometry_verified"], False)
        self.assertIs(parsed["candidate_processing"], False)
        self.assertEqual(parsed["candidate"], reference.CANDIDATE)

    def test_adverse_requests_all_rejected(self) -> None:
        cases = reference._adverse_cases()
        self.assertTrue(cases["all_requests_rejected"])
        self.assertEqual(cases["request_accepted_count"], 0)
        self.assertGreaterEqual(cases["request_case_count"], 30)
        for case in cases["request_cases"]:
            self.assertIs(case["accepted"], False, case["id"])
            self.assertNotEqual(case["error"], "NOT_REJECTED", case["id"])

    def test_adverse_manifests_all_rejected(self) -> None:
        cases = reference._adverse_cases()
        self.assertTrue(cases["all_manifests_rejected"])
        self.assertEqual(cases["manifest_accepted_count"], 0)
        self.assertGreaterEqual(cases["manifest_case_count"], 20)
        identifiers = {case["id"] for case in cases["manifest_cases"]}
        self.assertIn("sibling_variant_dns48", identifiers)
        self.assertIn("nonbool_commercial", identifiers)

    def test_nonfinite_request_samples_rejected(self) -> None:
        cases = reference._adverse_cases()
        nonfinite = [case for case in cases["request_cases"]
                     if case["id"].startswith("nonfinite")]
        self.assertEqual(len(nonfinite), 3)
        self.assertTrue(all(not case["accepted"] for case in nonfinite))

    def test_valid_manifest_is_still_deferred(self) -> None:
        manifest = reference._base_manifest()
        parsed = reference.validate_asset_manifest(manifest)
        self.assertEqual(parsed["variant"], "dns64")
        result = reference.admit_asset(manifest)
        self.assertEqual(result["status"], "DEFER")
        self.assertIs(result["admissible"], False)
        self.assertIs(result["manifest_validated"], True)
        self.assertIs(result["artifact_opened"], False)
        self.assertIs(result["artifact_hashed"], False)
        self.assertIs(result["artifact_loaded"], False)
        self.assertIs(result["qualifies_candidate"], False)
        self.assertIs(result["caller_declaration_is_not_review"], True)
        self.assertIn("weights_absent", result["blockers"])
        self.assertIn("license_noncommercial_use_not_approved",
                      result["blockers"])

    def test_sibling_variant_is_rejected_for_this_task(self) -> None:
        manifest = reference._base_manifest()
        manifest["variant"] = "dns48"
        with self.assertRaises(reference.ConfigError):
            reference.validate_asset_manifest(manifest)

    def test_admit_is_defer(self) -> None:
        result = reference.admit(reference._base_request())
        self.assertEqual(result["status"], "DEFER")
        self.assertIs(result["admissible"], False)
        self.assertIs(result["input_validated"], True)
        self.assertIs(result["geometry_verified"], False)
        self.assertIs(result["qualifies_candidate"], False)
        self.assertIn("source_absent", result["blockers"])
        self.assertIn("candidate_geometry_unverified", result["blockers"])

    def test_probe_candidate_fails_closed(self) -> None:
        with self.assertRaises(reference.ArtifactsAbsent):
            reference.probe_candidate(reference._base_request())

    def test_strict_json_rejects_duplicate_key(self) -> None:
        with self.assertRaises(reference.JsonError):
            reference.strict_json_loads('{"a":1,"a":2}')

    def test_strict_json_rejects_nonfinite(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads('{"a":' + token + '}')

    def test_strict_json_rejects_trailing_data(self) -> None:
        with self.assertRaises(reference.JsonError):
            reference.strict_json_loads('{"a":1} extra')


class ScorerTests(unittest.TestCase):
    def test_si_sdr_is_finite_and_deterministic(self) -> None:
        control = reference.paired_harness_control()
        self.assertTrue(math.isfinite(control["identity_si_sdr_db"]))
        self.assertTrue(math.isfinite(control["snr_db"]))
        self.assertEqual(control, reference.paired_harness_control())

    def test_paired_control_is_not_candidate_output(self) -> None:
        control = reference.paired_harness_control()
        self.assertIs(control["candidate_processing"], False)
        self.assertIs(control["qualifies_candidate"], False)
        self.assertIs(control["identity_output_equals_noisy"], True)
        self.assertEqual(set(control["shift_si_sdr_db"]),
                         {"-8", "0", "8"})

    def test_si_sdr_rejects_silent_reference(self) -> None:
        with self.assertRaises(reference.InputError):
            reference.si_sdr([0.0] * 8, [1.0] * 8)

    def test_si_sdr_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.InputError):
            reference.si_sdr([1.0, float("nan")], [1.0, 1.0])

    def test_stimulus_identity_is_bit_exact(self) -> None:
        probe = reference.stimulus_probe()
        self.assertIs(probe["candidate_processing"], False)
        for item in probe["identity_control"].values():
            self.assertIs(item["byte_identical"], True)
        self.assertEqual(probe, reference.stimulus_probe())


class BoardTests(unittest.TestCase):
    def test_stable_board_projection(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertEqual(
            digest,
            hashlib.sha256(reference.canonical_bytes(links)).hexdigest())
        report = report_json()
        self.assertEqual(report["board_links"], links)
        self.assertEqual(report["board_link_projection_sha256"], digest)
        self.assertIs(report["board_full_file_hashed"], False)

    def test_mutable_board_fields_are_excluded(self) -> None:
        excluded = set(report_json()["board_mutable_fields_excluded"])
        for name in ("status", "owner", "review", "handoff", "claim",
                     "history", "blocked_reason", "dispatch_priority"):
            self.assertIn(name, excluded)
        self.assertEqual(set(report_json()["board_link_fields"]),
                         set(reference.LINK_FIELDS))

    def test_full_board_path_never_enters_canonical_artifacts(self) -> None:
        full = "audio-benchmark-platform/plan/swarm/TASKS.json"
        for name in ("report.json", "contract.json", "SOURCES.sha256"):
            self.assertNotIn(full, (HERE / name).read_text(encoding="utf-8"))


class ArtifactTests(unittest.TestCase):
    def test_report_sidecar_matches(self) -> None:
        digest = sha256_file(HERE / "report.json")
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            digest + "  report.json\n")

    def test_report_artifact_pins_match(self) -> None:
        report = report_json()
        for name, digest in report["artifact_pins"].items():
            self.assertEqual(sha256_file(HERE / name), digest, name)
        self.assertEqual(set(report["artifact_pins"]),
                         set(reference.SOURCE_ARTIFACT_FILES))

    def test_contract_artifact_pins_match(self) -> None:
        contract = contract_json()
        for name, digest in contract["artifact_pins"].items():
            self.assertEqual(sha256_file(HERE / name), digest, name)
        expected = set(run.CONTRACT_ARTIFACTS) - {"contract.json"}
        self.assertEqual(set(contract["artifact_pins"]), expected)

    def test_contract_decision_fields(self) -> None:
        contract = contract_json()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "proposal_only_not_qualified")
        self.assertIs(contract["incomplete"], True)
        self.assertIs(contract["proposal_only"], True)
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(
            contract["comparison_status"],
            "blocked_source_weights_runtime_license_and_fixture_absent")
        self.assertEqual([gate["id"] for gate in contract["release_gates"]],
                         GATE_IDS)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in contract["release_gates"]))

    def test_sources_manifest_is_deterministic(self) -> None:
        report_payload = (HERE / "report.json").read_bytes()
        sidecar_payload = (HERE / "report.json.sha256").read_bytes()
        expected = run.build_sources_bytes(report_payload, sidecar_payload)
        self.assertEqual((HERE / "SOURCES.sha256").read_bytes(), expected)
        self.assertNotIn(
            b"audio-benchmark-platform/plan/swarm/TASKS.json", expected)

    def test_sources_manifest_pins_every_manifest_file(self) -> None:
        sources = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        for name in run.MANIFEST_FILES:
            if name == "report.json":
                digest = sha256_file(HERE / "report.json")
            elif name == "report.json.sha256":
                digest = sha256_file(HERE / "report.json.sha256")
            else:
                digest = sha256_file(HERE / name)
            self.assertIn(digest + "  " + reference.TASK_PREFIX + name,
                          sources, name)

    def test_spdx_sidecars_present(self) -> None:
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license",
                     "SOURCES.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_NEEDLE, text, name)

    def test_no_contiguous_spdx_token_in_python_strings(self) -> None:
        for name in ("reference.py", "run.py", "test_reference.py",
                     "verify.py"):
            for number, line in enumerate(
                    (HERE / name).read_text(encoding="utf-8").splitlines(), 1):
                if SPDX_NEEDLE in line:
                    self.assertTrue(
                        line.lstrip().startswith("#"),
                        name + ":" + str(number) + " has an SPDX string "
                        "literal")

    def test_readme_states_defer_and_rights(self) -> None:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        for token in ("DEFER", "incomplete", "not_qualified",
                      "CC-BY-NC-4.0", "RG-08", "not_qualified"):
            self.assertIn(token, text)


class ProfileTests(unittest.TestCase):
    def test_profile_mapping_is_blocked_or_partial(self) -> None:
        mapping = report_json()["profile_mapping"]
        self.assertTrue(mapping)
        for value in mapping.values():
            self.assertTrue(value.startswith("blocked_") or
                            value.startswith("partial_"), value)
        self.assertIn("identity_noisy_control", mapping)
        self.assertIn("paired_stoi", mapping)
        self.assertIn("clean_speech_preservation", mapping)
        self.assertIn("alignment_and_content_delay", mapping)

    def test_required_results_are_blocked_or_partial(self) -> None:
        results = report_json()["required_results"]
        self.assertTrue(results)
        for value in results.values():
            self.assertTrue(value.startswith("blocked_") or
                            value.startswith("partial_"), value)

    def test_local_harness_checks_all_true(self) -> None:
        checks = report_json()["local_harness_checks"]
        self.assertGreaterEqual(len(checks), 20)
        for name, value in checks.items():
            self.assertIs(value, True, name)


if __name__ == "__main__":
    unittest.main()
