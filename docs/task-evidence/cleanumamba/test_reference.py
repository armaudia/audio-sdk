# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib tests for the SDK-CLEANUMAMBA evidence package.

No network, audio, checkpoint, runtime, model or device is used.
"""

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


class StrictJsonTests(unittest.TestCase):
    def test_canonical_roundtrip(self) -> None:
        value = {"b": [1, 2], "a": "x"}
        self.assertEqual(
            reference.parse_strict_json_text(
                reference.canonical_bytes(value).decode("ascii")), value)

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            reference.parse_strict_json_text('{"a":1,"a":2}')

    def test_float_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non_integer_number"):
            reference.parse_strict_json_text('{"a":1.5}')

    def test_nonfinite_constant_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "nonfinite_constant"):
            reference.parse_strict_json_text('{"a":NaN}')

    def test_malformed_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "malformed_json"):
            reference.parse_strict_json_text("{")


class ManifestControlTests(unittest.TestCase):
    def test_control_is_schema_valid_but_not_admitted(self) -> None:
        control = reference.manifest_control()["control"]
        self.assertTrue(control["schema_valid"])
        self.assertFalse(control["licensed"])
        self.assertFalse(control["attested"])
        self.assertFalse(control["admitted"])
        self.assertFalse(control["qualifies"])

    def test_all_mutations_reject_with_exact_codes(self) -> None:
        result = reference.manifest_control()
        self.assertEqual(result["summary"]["case_count"], 30)
        self.assertEqual(result["summary"]["rejected_count"], 30)
        self.assertEqual(result["summary"]["admitted_count"], 0)
        self.assertEqual(result["summary"]["qualifying_results"], 0)
        self.assertTrue(result["summary"]["all_codes_match"])
        for case in result["cases"]:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertEqual(case["observed_code"], case["expected_code"],
                             case["id"])
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])

    def test_missing_field_rejected(self) -> None:
        value = reference._base_manifest()
        del value["schema_id"]
        with self.assertRaisesRegex(ValueError, "missing_field"):
            reference.validate_asset_manifest(value)

    def test_unknown_field_rejected(self) -> None:
        value = reference._base_manifest()
        value["extra"] = True
        with self.assertRaisesRegex(ValueError, "unknown_field"):
            reference.validate_asset_manifest(value)

    def test_wrong_geometry_rejected(self) -> None:
        value = reference._base_manifest()
        value["sample_rate_hz"] = 48000
        with self.assertRaisesRegex(ValueError, "sample_rate_mismatch"):
            reference.validate_asset_manifest(value)

    def test_absent_license_rejects_license_fields(self) -> None:
        value = reference._base_manifest()
        value["license_evidence"]["spdx"] = "MIT"
        with self.assertRaisesRegex(ValueError, "license_absent_fields"):
            reference.validate_asset_manifest(value)

    def test_manifest_never_marks_admitted(self) -> None:
        value = reference._base_manifest()
        value["license_evidence"] = {
            "status": "present",
            "spdx": "MIT",
            "terms_sha256": "0" * 64,
        }
        value["caller_attestation"] = True
        value["checkpoint_sha256"] = "1" * 64
        result = reference.validate_asset_manifest(value)
        self.assertTrue(result["admissible_for_intake"])
        self.assertFalse(result["admitted"])
        self.assertFalse(result["qualifies"])


class LedgerTests(unittest.TestCase):
    def test_manifest_constants(self) -> None:
        manifest = reference.load_upstream_manifest()
        self.assertEqual(manifest["commit"], reference.UPSTREAM_HEAD)
        self.assertEqual(manifest["tree_sha1"], reference.UPSTREAM_TREE)
        self.assertEqual(manifest["blob_count"], 62)
        self.assertEqual(manifest["directory_count"], 18)
        self.assertEqual(manifest["license_metadata_field"], None)

    def test_checkpoint_ledger_counts(self) -> None:
        ledger = reference.checkpoint_ledger_control()
        self.assertEqual(ledger["checkpoint_count"], 18)
        self.assertEqual(ledger["checkpoint_bytes"], 261837694)
        self.assertEqual(ledger["family_counts"],
                         {"E6": 6, "E8": 7, "experiments": 5})
        self.assertEqual(ledger["checkpoints_with_published_sha256"], 0)
        self.assertFalse(ledger["all_checkpoints_have_published_sha256"])
        self.assertFalse(ledger["license_blob_present"])
        self.assertFalse(ledger["qualifies"])

    def test_duplicate_size_pair_is_not_identity(self) -> None:
        pairs = reference.checkpoint_ledger_control()["duplicate_size_pairs"]
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["bytes"], 82788482)
        self.assertEqual(len(pairs[0]["paths"]), 2)
        self.assertTrue(pairs[0]["distinct_blob_shas"])

    def test_license_contradiction_recorded(self) -> None:
        findings = reference.license_findings()
        self.assertTrue(findings["readme_license_badge_claims_mit"])
        self.assertFalse(findings["license_file_present_at_pinned_commit"])
        self.assertEqual(findings["license_path_http_status_observed"], 404)
        self.assertFalse(findings["qualifies"])


class GeometryAndFrameTests(unittest.TestCase):
    def test_geometry_arithmetic(self) -> None:
        control = reference.geometry_control()
        self.assertEqual(control["arithmetic"]["e6_lookahead_samples"], 192)
        self.assertEqual(control["arithmetic"]["e8_lookahead_samples"], 768)
        self.assertEqual(
            control["arithmetic"]["demo_chunk_mod_frame_samples"], 96)
        self.assertEqual(
            control["arithmetic"]["e6_lookahead_mod_frame_samples"], 32)
        self.assertEqual(
            control["arithmetic"]["e8_lookahead_mod_frame_samples"], 128)
        self.assertFalse(control["checks"]["v0_frame_aligned_chunk"])
        self.assertFalse(control["checks"]["lookahead_measured"])
        self.assertFalse(control["qualifies"])

    def test_frame_control(self) -> None:
        result = reference.frame_control()
        self.assertEqual(result["summary"]["case_count"], 13)
        self.assertEqual(result["summary"]["accepted_count"], 2)
        self.assertEqual(result["summary"]["rejected_count"], 11)
        self.assertTrue(result["summary"]["all_codes_match"])
        self.assertFalse(result["qualifies"])


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report(cls.contract)

    def test_disposition(self) -> None:
        for payload in (self.contract, self.report):
            self.assertEqual(payload["decision"], "DEFER")
            self.assertEqual(payload["status"], "incomplete")
            self.assertEqual(payload["qualification_status"],
                             "not_qualified")
            self.assertTrue(payload["proposal_only"])

    def test_contract_digest(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_gates_blocked(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        for index, gate in enumerate(gates, start=1):
            self.assertEqual(gate["id"], f"RG-{index:02d}")
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             self.report["linked_row_identity"]["projection"])

    def test_blockers_open(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        artifact_ids = {row["id"] for row in
                        self.report["required_artifacts"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(blocker["required_action"])

    def test_artifacts_absent(self) -> None:
        rows = self.report["required_artifacts"]
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertFalse(row["licensed"])
            self.assertFalse(row["admitted"])
            self.assertTrue(row["blocked"])
            self.assertIsNone(row["sha256"])

    def test_required_results(self) -> None:
        results = self.report["required_results"]
        for key, value in results.items():
            if key == "no_result_qualifies":
                self.assertTrue(value)
            else:
                self.assertFalse(value, key)

    def test_enhancement_rows_blocked(self) -> None:
        rows = self.report["enhancement_profile_requirements"]
        self.assertEqual(len(rows), 9)
        for row in rows:
            self.assertEqual(row["status"], "blocked")
            self.assertFalse(row["qualifies"])
        outcomes = self.report["enhancement_outcomes"]
        self.assertEqual(len(outcomes), 9)
        for row in outcomes:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
            self.assertFalse(row["qualifies"])

    def test_no_floats_and_canonical(self) -> None:
        reference._no_floats(self.report)
        self.assertEqual(reference.canonical_bytes(self.contract),
                         reference.canonical_bytes(self.contract))
        self.assertTrue(reference.canonical_bytes(self.report).endswith(
            b"\n"))

    def test_scope_and_boundary(self) -> None:
        self.assertTrue(self.report["scope"]["task_local_only"])
        self.assertFalse(self.report["scope"]["network_used"])
        self.assertFalse(self.report["scope"]["runtime_invoked"])
        self.assertFalse(self.report["scope"]["audio_read"])
        self.assertTrue(self.report["boundary"]["task_local_only"])
        self.assertFalse(self.report["boundary"]["provider_registration"])
        self.assertFalse(self.report["boundary"]["public_api_abi_change"])
        self.assertFalse(self.report["boundary"]["shared_build_or_ci_change"])
        self.assertEqual(
            self.report["boundary"]["installed_v0_geometry"],
            {"sample_rate_hz": 16000, "channels": 1, "frame_samples": 160,
             "sample_format": "f32", "unchanged": True})
        self.assertEqual(
            self.report["public_v0_geometry"],
            {"sample_rate_hz": 16000, "channels": 1, "frame_samples": 160,
             "sample_format": "f32"})

    def test_source_reported_metrics_do_not_qualify(self) -> None:
        metrics = self.report["upstream_observation"][
            "source_reported_metrics"]
        self.assertFalse(metrics["qualifies"])
        self.assertEqual(metrics["pesq_wb"], "2.42")
        self.assertEqual(metrics["stoi_percent"], "95.1")


class ReadmeAndManifestTests(unittest.TestCase):
    def test_readme_digest_tables(self) -> None:
        counts = reference.verify_readme_digests(
            (HERE / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))
        self.assertEqual(counts["upstream"], 9)
        self.assertEqual(counts["artifacts"],
                         len(reference.artifact_table_names()))

    def test_sources_manifest(self) -> None:
        path = HERE / "SOURCES.sha256"
        self.assertTrue(path.is_file())
        counts = reference.verify_sources_manifest(path.read_bytes())
        self.assertGreater(counts, 20)

    def test_committed_report_sidecar(self) -> None:
        report = (HERE / "report.json").read_bytes()
        digest = hashlib.sha256(report).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")

    def test_committed_report_matches_regeneration(self) -> None:
        contract = reference.build_contract()
        self.assertEqual((HERE / "contract.json").read_bytes(),
                         reference.canonical_bytes(contract))
        self.assertEqual((HERE / "report.json").read_bytes(),
                         reference.report_bytes(contract))

    def test_local_pins_exist(self) -> None:
        for name in reference.LOCAL_PIN_FILES:
            self.assertTrue((HERE / name).is_file(), name)

    def test_forbidden_artifacts_absent(self) -> None:
        for path in HERE.iterdir():
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.suffix.lower(),
                             reference.FORBIDDEN_SUFFIXES, path.name)


if __name__ == "__main__":
    unittest.main()
