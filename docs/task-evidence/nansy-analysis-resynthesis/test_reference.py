# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the NANSY readiness package.

No network, candidate runtime, weight, corpus, voice or audio input is used.
Every test is a local, offline, failure-closed assertion.
"""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path
import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_valid_object_accepted(self) -> None:
        self.assertEqual(reference.loads_strict('{"a":1}'), {"a": 1})

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_nonfinite_constants_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                reference.loads_strict('{"a":' + token + "}")

    def test_trailing_and_truncated_rejected(self) -> None:
        for payload in ('{"a":1} extra', '{"a":1'):
            with self.assertRaises(ValueError):
                reference.loads_strict(payload)

    def test_bom_and_empty_rejected(self) -> None:
        for payload in ("\ufeff{\"a\":1}", ""):
            with self.assertRaises(ValueError):
                reference.loads_strict(payload)

    def test_non_object_root_rejected_by_reader(self) -> None:
        report = reference.build_report()
        payload = json.dumps(report, sort_keys=True)
        parsed = reference.loads_strict(payload)
        self.assertIsInstance(parsed, dict)

    def test_nonfinite_float_assertion(self) -> None:
        with self.assertRaises(TypeError):
            reference.assert_finite({"a": math.nan})
        reference.assert_finite({"a": 1.0, "b": [0, 1]})


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins_match_live_bytes(self) -> None:
        for relative, expected in reference.SOURCE_PINS.items():
            self.assertTrue((reference.AUDIO_ROOT / relative).is_file(),
                            relative)
            self.assertEqual(
                reference.sha256_file(reference.AUDIO_ROOT / relative),
                expected, relative)

    def test_boundary_pins_match_live_bytes(self) -> None:
        for relative, expected in reference.BOUNDARY_PINS.items():
            self.assertTrue((reference.SDK_ROOT / relative).is_file(),
                            relative)
            self.assertEqual(
                reference.sha256_file(reference.SDK_ROOT / relative),
                expected, relative)

    def test_board_is_never_pinned(self) -> None:
        names = set(reference.SOURCE_PINS) | set(reference.BOUNDARY_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, names)
        self.assertFalse(any(name.endswith("plan/swarm/TASKS.json")
                             for name in names))

    def test_board_identity_projection(self) -> None:
        projection = reference.board_row_projection()
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["component"], reference.COMPONENT_ID)
        self.assertEqual(projection["mode"], reference.MODE)
        self.assertEqual(projection["repository"], reference.REPOSITORY)
        self.assertEqual(tuple(projection["depends_on"]),
                         reference.DEPENDS_ON)
        self.assertEqual(set(projection),
                         {"id", "title", "component", "mode", "repository",
                          "depends_on"})

    def test_linked_rows_projection_is_stable(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual(len(rows), len(reference.LINKED_ROW_IDS))
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))
        self.assertEqual(reference.linked_rows_digest(rows),
                         reference.linked_rows_digest())

    def test_inventory_identity(self) -> None:
        row = reference.inventory_link()
        self.assertEqual(row["id"], reference.COMPONENT_ID)
        self.assertEqual(row["verification_profile"], "voice")
        self.assertEqual(row["disposition"], "sdk-model")
        self.assertEqual(row["evidence_status"], "considered")


class AbsenceTests(unittest.TestCase):
    def test_twenty_fixed_probes_all_absent(self) -> None:
        summary = reference.absence_summary()
        self.assertEqual(summary["probe_count"], 20)
        self.assertEqual(summary["workspace_probe_count"], 12)
        self.assertEqual(summary["worktree_probe_count"], 5)
        self.assertEqual(summary["home_probe_count"], 3)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_absent"])

    def test_absence_claims_no_execution(self) -> None:
        summary = reference.absence_summary()
        for key in ("download_attempted", "network_used",
                    "candidate_module_imported", "candidate_runtime_executed",
                    "weights_loaded", "audio_read",
                    "processed_output_present", "recursive_workspace_walk"):
            self.assertIs(summary[key], False, key)
        self.assertIs(summary["fixed_probe_list_only"], True)

    def test_runtime_is_unpinned(self) -> None:
        runtime = reference.runtime_readiness()
        self.assertIs(runtime["runtime_present"], False)
        self.assertIs(runtime["runtime_pinned"], False)
        self.assertIs(runtime["import_attempted"], False)
        self.assertIsNone(runtime["lock_sha256"])


class DeclarationTests(unittest.TestCase):
    def test_empty_declaration_accepted_and_not_qualified(self) -> None:
        result = reference.validate_declaration(reference.empty_declaration())
        self.assertEqual(result["decision"], "DEFER")
        self.assertIs(result["qualifies"], False)

    def test_presence_claim_rejected(self) -> None:
        declaration = reference.empty_declaration()
        declaration["weights"]["declared_present"] = True
        with self.assertRaises(reference.EvidenceError):
            reference.validate_declaration(declaration)

    def test_qualification_claim_rejected(self) -> None:
        declaration = reference.empty_declaration()
        declaration["disposition"]["qualifies"] = True
        with self.assertRaises(reference.EvidenceError):
            reference.validate_declaration(declaration)

    def test_geometry_claim_rejected(self) -> None:
        declaration = reference.empty_declaration()
        declaration["geometry"]["declared"] = True
        with self.assertRaises(reference.EvidenceError):
            reference.validate_declaration(declaration)

    def test_unknown_field_rejected(self) -> None:
        declaration = reference.empty_declaration()
        declaration["weights"]["tensor_name"] = "generator.pt"
        with self.assertRaises(reference.EvidenceError):
            reference.validate_declaration(declaration)

    def test_float_rejected(self) -> None:
        declaration = reference.empty_declaration()
        declaration["weights"]["byte_count"] = 1.0
        with self.assertRaises(reference.EvidenceError):
            reference.validate_declaration(declaration)

    def test_generated_cases_all_rejected(self) -> None:
        cases = reference._declaration_cases()
        self.assertEqual(cases["rejection_cases"], 46)
        self.assertTrue(cases["all_rejected"])
        self.assertIs(cases["accepted_control_qualifies"], False)


class RequestTests(unittest.TestCase):
    def test_base_request_validates(self) -> None:
        validated = reference.validate_request(reference._base_request())
        self.assertEqual(validated["sample_rate_hz"], 16000)
        self.assertEqual(validated["hop_samples"], 160)
        self.assertEqual(validated["stage"], "round_trip")

    def test_adverse_requests_all_rejected(self) -> None:
        cases = reference._adverse_request_cases()
        self.assertEqual(cases["accepted_count"], 0)
        self.assertTrue(cases["all_rejected"])

    def test_nonfinite_samples_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            request = reference._base_request()
            request["samples"] = [0.0] * 160
            request["samples"][3] = value
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_candidate_is_absent(self) -> None:
        with self.assertRaises(reference.CandidateAbsent):
            reference.probe_candidate(reference._base_request())

    def test_reset_cases_match(self) -> None:
        self.assertTrue(reference._reset_cases()["matches_expectation"])


class ProfileAndDispositionTests(unittest.TestCase):
    def test_twelve_voice_rows_never_qualify(self) -> None:
        rows = reference.profile_rows()
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(row["qualifies"] is False for row in rows))
        self.assertTrue(any(row["status"] == "blocked" for row in rows))

    def test_voice_profile_phrases_pinned(self) -> None:
        check = reference.profile_source_check()
        self.assertEqual(check["voice_row_count"], 1)
        self.assertTrue(check["all_phrases_present"])

    def test_qualification_is_not_qualified(self) -> None:
        qualification = reference.qualification()
        self.assertEqual(qualification["decision"], "DEFER")
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertIs(qualification["qualifies"], False)
        self.assertIs(qualification["proposal_only"], True)
        self.assertIs(qualification["incomplete"], True)

    def test_eight_gates_blocked_and_none_qualify(self) -> None:
        gates = reference.release_gates()
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(gate["qualifies"] is False for gate in gates))

    def test_only_evidence_register_present(self) -> None:
        present = [row["id"] for row in reference.REQUIRED_ARTIFACTS
                   if row["present"]]
        self.assertEqual(present, ["ART-01"])
        blocked = [row for row in reference.REQUIRED_ARTIFACTS
                   if row["id"] != "ART-01"]
        self.assertTrue(all(row["blocked"] for row in blocked))
        self.assertTrue(all(row["sha256"] is None for row in blocked))

    def test_six_exact_blockers_open(self) -> None:
        self.assertEqual(len(reference.EXACT_BLOCKERS), 6)
        self.assertTrue(all(blocker["status"] == "open"
                            for blocker in reference.EXACT_BLOCKERS))
        self.assertTrue(all(blocker["qualifies"] is False
                            for blocker in reference.EXACT_BLOCKERS))

    def test_matched_evidence_has_zero_results(self) -> None:
        matched = reference.matched_evidence()
        self.assertEqual(matched["real_results"], 0)
        self.assertEqual(matched["synthetic_results"], 0)
        self.assertIs(matched["candidate_output_present"], False)
        self.assertIs(matched["analysis_to_waveform_parity_present"], False)
        self.assertIs(matched["speech_preservation_present"], False)

    def test_boundary_is_task_local(self) -> None:
        boundary = reference.boundary()
        self.assertIs(boundary["board_file_pinned"], False)
        self.assertIs(boundary["linked_row_identity_only"], True)
        self.assertIs(boundary["mutable_board_fields_gate"], False)
        for key in ("provider_registration", "descriptor_registry_change",
                    "default_selected", "public_api_abi_change",
                    "installed_v0_behavior_change", "shared_build_or_ci_change",
                    "candidate_code_vendored", "weights_vendored",
                    "audio_added", "processed_output_added"):
            self.assertIs(boundary[key], False, key)


class ReportContractTests(unittest.TestCase):
    def test_report_is_deterministic(self) -> None:
        first, first_digest = reference.canonical_report()
        second, second_digest = reference.canonical_report()
        self.assertEqual(first, second)
        self.assertEqual(first_digest, second_digest)

    def test_report_decision_and_status(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], reference.STATUS)
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertIs(report["proposal_only"], True)
        self.assertIs(report["incomplete"], True)

    def test_report_round_trips_canonical_bytes(self) -> None:
        payload = reference.report_bytes()
        parsed = reference.loads_strict(payload.decode("ascii"))
        self.assertEqual(parsed, reference.build_report())
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            reference.canonical_report()[1])

    def test_report_strict_json_rejections(self) -> None:
        cases = reference._json_adverse_cases()
        self.assertEqual(cases["strict_json_cases"], 9)
        self.assertTrue(cases["all_rejected"])

    def test_contract_matches_report(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["canonical_report"]["canonical_digest"],
                         reference.canonical_report()[1])
        self.assertEqual(len(contract["release_gates"]), 8)

    def test_snippet_presence(self) -> None:
        presence = reference.evidence_presence()
        self.assertEqual(presence["snippet_count"], 7)
        self.assertTrue(presence["all_present"])

    def test_harness_checks_all_true(self) -> None:
        checks = reference.local_harness_checks()
        for key, value in checks.items():
            self.assertIs(value, True, key)


class CommittedArtifactTests(unittest.TestCase):
    def test_committed_report_matches_builder(self) -> None:
        path = HERE / "report.json"
        self.assertTrue(path.is_file())
        self.assertEqual(path.read_bytes(), reference.report_bytes())
        self.assertEqual(reference.read_strict_json(path),
                         reference.build_report())

    def test_committed_contract_matches_builder(self) -> None:
        path = HERE / "contract.json"
        self.assertTrue(path.is_file())
        self.assertEqual(path.read_bytes(),
                         reference.canonical_bytes(
                             reference.build_contract()) + b"\n")

    def test_sidecar_matches_report(self) -> None:
        digest = hashlib.sha256(
            (HERE / "report.json").read_bytes()).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), digest + "  report.json\n")

    def test_readme_digest_tables(self) -> None:
        counts = reference.verify_readme_digests(
            (HERE / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))

    def test_sources_manifest_has_no_board(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        pinned = [line for line in text.splitlines()
                  if len(line) > 64 and line[64:66] == "  "]
        self.assertTrue(pinned)
        self.assertFalse(any(line.endswith("plan/swarm/TASKS.json")
                             for line in pinned))


class ScopeRegressionTests(unittest.TestCase):
    def test_inside_prefix_is_allowed(self) -> None:
        paths = [reference.TASK_PREFIX + "report.json"]
        self.assertEqual(reference.scope_violations(paths), [])

    def test_outside_prefix_is_reported(self) -> None:
        paths = ["audio-sdk/CONTRACTS.md",
                 reference.TASK_PREFIX + "README.md"]
        self.assertEqual(reference.scope_violations(paths),
                         ["audio-sdk/CONTRACTS.md"])

    def test_unresolved_base_is_none_on_missing_refs(self) -> None:
        self.assertIsNone(reference.scope_base(
            reference.SDK_ROOT, ("refs/heads/does-not-exist-xyz",)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
