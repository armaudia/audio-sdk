# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Standard-library tests for the CCF AATC DEFER evidence package."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"


def _walk(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)
    else:
        yield value


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        path = HERE / "_duplicate_test.json"
        try:
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)
        finally:
            path.unlink(missing_ok=True)

    def test_nonfinite_constant_rejected(self) -> None:
        path = HERE / "_nonfinite_test.json"
        try:
            path.write_text('{"a":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)
        finally:
            path.unlink(missing_ok=True)

    def test_float_rejected(self) -> None:
        path = HERE / "_float_test.json"
        try:
            path.write_text('{"a":1.5}', encoding="utf-8")
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)
        finally:
            path.unlink(missing_ok=True)

    def test_canonical_is_sorted_ascii_with_newline(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": 2})
        self.assertEqual(payload, b'{"a":2,"b":1}\n')
        self.assertTrue(payload.endswith(b"\n"))
        self.assertTrue(payload.isascii())

    def test_no_floats_rejects_nested(self) -> None:
        with self.assertRaises(ValueError):
            reference._no_floats({"a": [{"b": 0.5}]})


class BoardIdentityTests(unittest.TestCase):
    def test_projection_has_only_stable_fields(self) -> None:
        projection = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(set(projection),
                         set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["mode"], "research-control")
        self.assertEqual(projection["component"], reference.COMPONENT_ID)

    def test_projection_digest_deterministic(self) -> None:
        first = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        second = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(reference.board_row_digest(first),
                         reference.board_row_digest(second))

    def test_mutable_board_never_pinned(self) -> None:
        for pins in (reference.SOURCE_PINS, reference.BOUNDARY_PINS,
                     reference.SIBLING_PINS):
            self.assertNotIn(reference.BOARD_TASK_ROW, pins)
        self.assertFalse(reference.documented_challenge_envelope()[
            "semantics_verified_here"])

    def test_linked_rows_digest_deterministic(self) -> None:
        self.assertEqual(reference.linked_rows_digest(),
                         reference.linked_rows_digest())
        self.assertEqual(len(reference.LINKED_ROWS), 15)


class PinTests(unittest.TestCase):
    def test_all_pins_verify(self) -> None:
        source, boundary, sibling = reference.verify_pins()
        for group in (source, boundary, sibling):
            for relative, row in group.items():
                self.assertTrue(row["verified"], relative)
                self.assertIsNotNone(row["actual"], relative)

    def test_research_note_is_pinned(self) -> None:
        self.assertIn(reference.RESEARCH_NOTE, reference.SOURCE_PINS)
        self.assertIn(reference.BASELINE_IMPLEMENTATION,
                      reference.SOURCE_PINS)
        self.assertIn(reference.BASELINE_REPORT, reference.SOURCE_PINS)

    def test_research_note_provenance(self) -> None:
        probe = reference.research_note_probe()
        self.assertTrue(probe["present"])
        self.assertTrue(probe["records_registration_required"])
        self.assertTrue(probe["records_dataset_larger_than_pilot"])
        self.assertTrue(probe["records_universal_next_benchmark"])
        self.assertTrue(probe["records_no_single_universal_model"])
        self.assertTrue(probe["records_no_neural_checkpoint"])
        self.assertTrue(probe["records_no_local_paired_set"])
        self.assertIsInstance(probe["challenge_line"], int)
        self.assertIsInstance(probe["limits_line"], int)
        self.assertFalse(probe["qualifies"])

    def test_source_presence_fails_closed(self) -> None:
        presence = reference.source_presence()
        for key in ("registration_acceptance_present",
                    "participant_agreement_present",
                    "challenge_dataset_present",
                    "organizer_pairing_present",
                    "official_baseline_present",
                    "official_scorer_present",
                    "rights_cleared_cohort_present",
                    "exact_challenge_artifact_present",
                    "network_used", "download_attempted",
                    "challenge_data_read", "audio_read", "audio_played",
                    "qualifies"):
            self.assertFalse(presence[key], key)
        self.assertTrue(presence["presence_is_not_admission"])

    def test_license_findings_fail_closed(self) -> None:
        findings = reference.license_findings()
        self.assertTrue(findings["registration_required_recorded"])
        for key, value in findings.items():
            if key == "registration_required_recorded":
                self.assertTrue(value)
            else:
                self.assertFalse(value, key)

    def test_classical_baseline_is_not_a_substitute(self) -> None:
        guard = reference.classical_baseline_guard()
        self.assertTrue(guard["present"])
        self.assertFalse(guard["is_unified_restorer"])
        self.assertFalse(guard["is_ccf_aatc_baseline"])
        self.assertFalse(guard["is_ccf_aatc_submission"])
        self.assertFalse(guard["can_substitute"])
        self.assertFalse(guard["uses_registered_challenge_data"])
        self.assertFalse(guard["qualifies"])

    def test_profile_phrases_exist_in_evidence_row(self) -> None:
        path = (reference.AUDIO_ROOT /
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
        rows = [line for line in path.read_text(encoding="utf-8").splitlines()
                if line.startswith("| Evidence |")]
        self.assertEqual(len(rows), 1)
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, rows[0], phrase)


class FamilyControlTests(unittest.TestCase):
    def test_accepted_families(self) -> None:
        control = reference.family_control()
        accepted = [case["id"] for case in control["cases"]
                    if case["status"] == "accepted"]
        self.assertEqual(accepted, ["C01", "C02", "C03", "C04"])

    def test_cross_family_substitutions_rejected(self) -> None:
        cases = {case["id"]: case for case in reference.family_control()["cases"]}
        self.assertEqual(cases["C05"]["observed_code"],
                         "cross_family_substitution")
        self.assertEqual(cases["C06"]["observed_code"],
                         "cross_family_substitution")
        self.assertEqual(cases["C07"]["observed_code"],
                         "decoder_context_required")
        self.assertEqual(cases["C08"]["observed_code"],
                         "decoder_context_required")
        self.assertEqual(cases["C11"]["observed_code"],
                         "unified_claim_requires_strata")

    def test_summary(self) -> None:
        summary = reference.family_control()["summary"]
        self.assertEqual(summary["case_count"], 18)
        self.assertEqual(summary["accepted_count"], 4)
        self.assertEqual(summary["rejected_count"], 14)
        self.assertTrue(summary["all_codes_match"])
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertFalse(summary["qualifies"])


class DegradationControlTests(unittest.TestCase):
    def test_declared_parameters(self) -> None:
        low = reference.clip_degradation("7/20")
        high = reference.clip_degradation("11/20")
        self.assertEqual(low["threshold"], "7/20")
        self.assertEqual(high["threshold"], "11/20")
        self.assertEqual(reference.clip_degradation("35/100")["threshold"],
                         "7/20")
        bwe = reference.bwe_degradation(3500, 16000)
        self.assertEqual(bwe["cutoff_fraction"], "7/32")
        self.assertTrue(bwe["below_nyquist"])
        self.assertEqual(reference.codec_degradation(8, 8000)["levels"], 256)
        self.assertEqual(reference.codec_degradation(4, 8000)["levels"], 16)
        self.assertTrue(reference.codec_degradation(4, 8000)["stress_proxy"])
        self.assertEqual(reference.plc_degradation("1/10")["loss_rate"],
                         "1/10")
        self.assertEqual(reference.plc_degradation("17/100")["loss_rate"],
                         "17/100")

    def test_rejections(self) -> None:
        with self.assertRaises(ValueError):
            reference.clip_degradation("0")
        with self.assertRaises(ValueError):
            reference.clip_degradation("1")
        with self.assertRaises(ValueError):
            reference.bwe_degradation(8000, 16000)
        with self.assertRaises(ValueError):
            reference.codec_degradation(0, 8000)
        with self.assertRaises(ValueError):
            reference.codec_degradation(True, 8000)
        with self.assertRaises(ValueError):
            reference.plc_degradation("3/2")
        with self.assertRaises(ValueError):
            reference.bwe_degradation(float("inf"), 16000)

    def test_summary(self) -> None:
        summary = reference.degradation_control()["summary"]
        self.assertEqual(summary["case_count"], 14)
        self.assertEqual(summary["accepted_count"], 7)
        self.assertEqual(summary["rejected_count"], 7)
        self.assertTrue(summary["all_codes_match"])
        self.assertEqual(summary["clip_thresholds"], ["7/20", "11/20"])
        self.assertEqual(summary["bwe_cutoff_fraction"], "7/32")
        self.assertEqual(summary["codec_levels"], [256, 16])
        self.assertEqual(summary["loss_rates"], ["1/10", "17/100"])
        self.assertFalse(summary["qualifies"])


class PairControlTests(unittest.TestCase):
    def test_canonical_order_is_invariant(self) -> None:
        self.assertEqual(reference.canonicalize_pair("RST-02+RST-01"),
                         "RST-01+RST-02")
        self.assertEqual(reference.canonicalize_pair("RST-04+RST-03"),
                         "RST-03+RST-04")
        self.assertEqual(reference.canonicalize_pair("RST-01"), "RST-01")

    def test_pair_rejections(self) -> None:
        for value, code in (
                ("RST-01+RST-01", "invalid_pair"),
                ("RST-01+RST-02+RST-03", "invalid_pair"),
                ("RST-09", "unknown_family"),
                ("", "invalid_pair"),
                ("rst-01", "invalid_pair"),
                (1, "invalid_type")):
            with self.assertRaises(ValueError) as context:
                reference.canonicalize_pair(value)
            self.assertEqual(str(context.exception), code)

    def test_synthetic_table_permits_nothing(self) -> None:
        control = reference.pair_control()
        self.assertEqual(control["summary"]["pair_count"], 6)
        self.assertEqual(control["summary"]["single_count"], 4)
        self.assertEqual(control["summary"]["organizer_permitted_count"], 0)
        for row in control["pairs"] + control["singles"]:
            self.assertFalse(row["organizer_verified"])
            self.assertFalse(row["permitted_for_qualification"])
            self.assertFalse(row["qualifies"])
        self.assertEqual(control["summary"]["qualifying_results"], 0)

    def test_summary(self) -> None:
        summary = reference.pair_control()["summary"]
        self.assertEqual(summary["case_count"], 10)
        self.assertEqual(summary["accepted_count"], 4)
        self.assertEqual(summary["rejected_count"], 6)
        self.assertTrue(summary["all_codes_match"])
        self.assertTrue(summary["canonical_order_invariant"])
        self.assertFalse(summary["qualifies"])


class AggregationControlTests(unittest.TestCase):
    def test_exact_stratum_mean(self) -> None:
        result = reference._aggregate_rows(reference._aggregation_rows())
        first = result["strata"][0]
        self.assertEqual(first["family"], "RST-01")
        self.assertEqual(first["metrics"]["si_sdr_db"], "31/2")
        self.assertEqual(first["metrics"]["rmse"], "3/20")
        self.assertEqual(result["strata_complete"], True)

    def test_unified_score_forbidden(self) -> None:
        result = reference._aggregate_rows(reference._aggregation_rows())
        self.assertEqual(result["unified"]["status"], "forbidden")
        self.assertIsNone(result["unified"]["value"])
        self.assertEqual(result["unified"]["reason"],
                         "organizer_pairing_list_absent")
        self.assertEqual(result["pair_mode"],
                         "single_distortion_control_only")

    def test_multi_pair_marks_unverified(self) -> None:
        rows = reference._aggregation_rows()
        rows[0]["pair"] = "RST-01+RST-02"
        result = reference._aggregate_rows(rows)
        self.assertEqual(result["pair_mode"],
                         "multi_distortion_pair_unverified")
        self.assertEqual(result["unified"]["status"], "forbidden")

    def test_rejections(self) -> None:
        base = reference._aggregation_rows()
        cases = {
            "A02": "strata_incomplete",
            "A03": "unknown_family",
            "A04": "unknown_metric",
            "A05": "duplicate_row",
            "A06": "invalid_value",
            "A07": "invalid_value",
            "A10": "pair_family_mismatch",
            "A11": "aggregation_empty",
            "A12": "invalid_item_id",
        }
        observed = {case["id"]: case["observed_code"]
                    for case in reference.aggregation_control()["cases"]}
        for case_id, code in cases.items():
            self.assertEqual(observed[case_id], code, case_id)
        with self.assertRaises(ValueError):
            rows = [dict(row) for row in base]
            rows[0]["value"] = float("inf")
            reference._aggregate_rows(rows)

    def test_summary(self) -> None:
        summary = reference.aggregation_control()["summary"]
        self.assertEqual(summary["case_count"], 12)
        self.assertEqual(summary["accepted_count"], 2)
        self.assertEqual(summary["rejected_count"], 10)
        self.assertTrue(summary["all_codes_match"])
        self.assertTrue(summary["unified_score_forbidden"])
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertFalse(summary["qualifies"])


class AdmissionTests(unittest.TestCase):
    def test_base_manifest_is_schema_valid_not_admitted(self) -> None:
        control = reference.assess_manifest(reference._base_manifest())
        self.assertTrue(control["schema_valid"])
        self.assertFalse(control["admitted"])
        self.assertFalse(control["qualifies"])
        self.assertFalse(control["challenge_artifact_present"])
        self.assertFalse(control["organizer_pairing_present"])
        self.assertIn("organizer_pairing_list_absent", control["reasons"])

    def test_all_mutations_rejected_with_exact_codes(self) -> None:
        base = reference._base_manifest()
        for case_id, mutator, expected in reference.mutations():
            candidate = json.loads(json.dumps(base))
            mutator(candidate)
            with self.assertRaises(ValueError) as context:
                reference.validate_manifest(candidate)
            self.assertEqual(str(context.exception), expected, case_id)

    def test_admission_summary(self) -> None:
        admission = reference.admission_controls()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], 37)
        self.assertEqual(summary["rejected_count"], 37)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertTrue(summary["all_codes_match"])
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertEqual(summary["qualifying_results"], 0)
        for case in admission["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])


class ContractAndReportTests(unittest.TestCase):
    def test_contract_is_canonical_and_strict(self) -> None:
        contract = reference.read_strict_json(CONTRACT)
        reference.validate_contract(contract)
        self.assertEqual(CONTRACT.read_bytes(),
                         reference.canonical_bytes(contract))

    def test_report_is_canonical_and_strict(self) -> None:
        report = reference.read_strict_json(REPORT)
        self.assertEqual(REPORT.read_bytes(), reference.canonical_bytes(report))
        self.assertFalse(any(isinstance(value, float)
                             for value in _walk(report)))

    def test_report_sidecar(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="ascii"),
                         f"{digest}  report.json\n")

    def test_contract_digest_in_report(self) -> None:
        contract = reference.read_strict_json(CONTRACT)
        report = reference.read_strict_json(REPORT)
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))
        for key in ("disposition", "qualification", "scope", "boundary",
                    "public_v0_geometry", "non_claims", "observed_provenance",
                    "documented_challenge_envelope",
                    "synthetic_pairing_envelope", "required_artifacts",
                    "exact_blockers", "required_results", "reproduction",
                    "classical_baseline_guard", "challenge_record"):
            self.assertEqual(report[key], contract[key], key)
        self.assertEqual(report["gates"], contract["release_gates"])

    def test_report_disposition_and_gates(self) -> None:
        report = reference.read_strict_json(REPORT)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["qualification"]["qualifying_results"], 0)
        self.assertEqual(len(report["gates"]), 8)
        self.assertEqual(len(report["exact_blockers"]), 6)
        self.assertEqual(len(report["required_artifacts"]), 10)
        for index, gate in enumerate(report["gates"], start=1):
            self.assertEqual(gate["id"], f"RG-{index:02d}")
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
        for row in report["evidence_profile"]["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertFalse(row["qualifies"])
        for row in report["evidence_outcomes"]["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
            self.assertFalse(row["qualifies"])
        required = dict(report["required_results"])
        self.assertTrue(required.pop("no_result_qualifies"))
        self.assertFalse(any(required.values()))

    def test_documented_envelope_is_not_a_spec(self) -> None:
        report = reference.read_strict_json(REPORT)
        envelope = report["documented_challenge_envelope"]
        self.assertTrue(envelope["challenge_named"])
        self.assertTrue(envelope["registration_required_recorded"])
        self.assertFalse(envelope["organizer_pairing_list_recorded"])
        self.assertFalse(envelope["dataset_identity_recorded"])
        self.assertFalse(envelope["official_baseline_identity_recorded"])
        self.assertFalse(envelope["semantics_verified_here"])
        self.assertFalse(envelope["local_evaluation_recorded"])
        self.assertFalse(envelope["qualifies"])
        synthetic = report["synthetic_pairing_envelope"]
        self.assertEqual(synthetic["multi_distortion_pairs"], 6)
        self.assertEqual(synthetic["organizer_permitted"], 0)
        self.assertFalse(synthetic["permitted_for_qualification"])
        self.assertFalse(synthetic["qualifies"])

    def test_sample_manifest_is_schema_only(self) -> None:
        report = reference.read_strict_json(REPORT)
        control = report["admission"]["control"]
        self.assertTrue(control["schema_valid"])
        self.assertFalse(control["admitted"])
        self.assertFalse(control["qualifies"])

    def test_sources_manifest_rebuilds(self) -> None:
        payload = PINS.read_bytes()
        reference.verify_sources_manifest(payload)
        self.assertEqual(payload, run.sources_bytes())
        names = {
            line.split("  ", 1)[1]
            for line in payload.decode("ascii").splitlines()
            if line and not line.startswith("#")
        }
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", names)
        self.assertNotIn(reference.BOARD_TASK_ROW, payload.decode("ascii"))

    def test_report_and_contract_regenerate(self) -> None:
        payload, digest = run.canonical_report_bytes()
        self.assertEqual(payload, REPORT.read_bytes())
        self.assertEqual(digest, hashlib.sha256(payload).hexdigest())
        self.assertEqual(run.contract_bytes(), CONTRACT.read_bytes())


if __name__ == "__main__":
    unittest.main()
