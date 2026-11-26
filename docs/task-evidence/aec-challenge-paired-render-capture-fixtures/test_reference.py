# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the AEC paired render/capture fixture gate.

Run from this directory::

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py

Every test is deterministic, stdlib-only and metadata-only.  No licensed audio,
model, runtime, device or network is used.  Caller-owned temporary bytes are
used only to exercise the digest gate and are never committed or reported as a
fixture result.
"""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import reference


def _dummy_declaration() -> dict:
    groups = {"group-a": reference.SYNTHETIC_ROLES}
    items = []
    payloads = {}
    for group, roles in groups.items():
        for index, role in enumerate(sorted(roles)):
            payload = ("RIFF-" + group + "-" + role + "-" + str(index)).encode()
            payload = payload + b"\x00" * (64 - len(payload))
            name = f"{group}_{role}.wav"
            items.append({
                "group": group,
                "role": role,
                "name": name,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "sample_rate_hz": 16000,
                "channels": 1,
                "frames": 32,
            })
            payloads[name] = (payload, hashlib.sha256(payload).hexdigest())
    return {
        "schema_id": reference.DECLARATION_SCHEMA,
        "subset": "synthetic_train",
        "source_revision": reference.SOURCE_REVISION,
        "split": "train",
        "items": items,
        "_payloads": payloads,
    }


def _lookup(payloads):
    return lambda name: payloads.get(name)


class FixturePartitionTests(unittest.TestCase):
    def test_synthetic_partition_counts(self):
        manifest = reference.synthetic_manifest()
        self.assertEqual(len(manifest["items"]), 48)
        self.assertEqual(len(manifest["scenarios"]), 12)
        self.assertEqual(manifest["role_counts"], {
            "echo_component": 12,
            "far_end_reference": 12,
            "near_end_target": 12,
            "microphone_capture": 12,
        })
        self.assertEqual(manifest["declared_total_bytes"], 15_362_072)
        self.assertTrue(all(scenario["roles_complete"]
                            for scenario in manifest["scenarios"]))
        self.assertEqual(max(scenario["declared_byte_spread"]
                             for scenario in manifest["scenarios"]), 0)

    def test_synthetic_strata_and_ser(self):
        selection = reference.synthetic_selection()
        self.assertEqual(selection["strata"],
                         {"linear_clean": 4, "nonlinear_clean": 4,
                          "farend_noisy": 4})
        self.assertEqual(selection["ser_values"], [-8, -3, 2, 7])
        self.assertAlmostEqual(selection["scale_min"],
                               0.5554605135214555)
        self.assertAlmostEqual(selection["scale_max"],
                               0.8347643515788602)

    def test_recorded_partition_counts(self):
        manifest = reference.recorded_manifest()
        self.assertEqual(len(manifest["items"]), 108)
        self.assertEqual(len(manifest["groups"]), 12)
        self.assertEqual(manifest["role_counts"],
                         {"far_end_reference": 48,
                          "microphone_capture": 60})
        self.assertEqual(manifest["declared_total_frames"], 19_547_568)
        self.assertFalse(manifest["blind_test_data_used"])
        self.assertFalse(manifest["local_audio_directory_recorded"])

    def test_recorded_pair_declared_lengths(self):
        manifest = reference.recorded_manifest()
        self.assertEqual(len(manifest["pairs"]), 48)
        self.assertEqual(manifest["unequal_pair_count"], 33)
        self.assertEqual(manifest["max_pair_delta_frames"], 1760)
        self.assertEqual(sum(1 for pair in manifest["pairs"]
                             if pair["equal_length"]), 15)

    def test_partition_ledgers(self):
        synthetic = reference.synthetic_manifest()
        recorded = reference.recorded_manifest()
        self.assertEqual(
            synthetic["ledger_sha256"],
            "53e8ff695566da7a3539a291baa9c5367e8553639641fc67f087fa1385e46fc1")
        self.assertEqual(
            recorded["ledger_sha256"],
            "c938c4dfa437ad88760ec9259f74a9fb9c1de7390424dcf16aab8088a5581f84")
        self.assertNotEqual(synthetic["ledger_sha256"],
                            recorded["ledger_sha256"])
        self.assertTrue(set(item["name"] for item in synthetic["items"]).isdisjoint(
            set(item["name"] for item in recorded["items"])))

    def test_source_revision_is_frozen(self):
        self.assertEqual(len(reference.SOURCE_REVISION), 40)
        self.assertEqual(reference.synthetic_manifest()["source_revision"],
                         reference.SOURCE_REVISION)
        self.assertEqual(reference.recorded_manifest()["source_revision"],
                         reference.SOURCE_REVISION)

    def test_manifests_do_not_claim_approval(self):
        synthetic = reference.synthetic_manifest()
        self.assertIn("provisional",
                      synthetic["rights_review_status"].lower())
        self.assertIn("not rights approval",
                      synthetic["rights_review_status"].lower())
        self.assertNotIn("approved",
                         synthetic["license_note"].lower())


class PresenceAndRightsTests(unittest.TestCase):
    def test_presence_probe_is_closed(self):
        synthetic = reference.synthetic_manifest()
        recorded = reference.recorded_manifest()
        probe = reference.presence_probe(synthetic, recorded)
        self.assertTrue(probe["bounded"])
        self.assertFalse(probe["synthetic"]["directory_present"])
        self.assertEqual(probe["synthetic"]["declared_files_present"], 0)
        self.assertEqual(probe["recorded"]["declared_files_present"], 0)
        self.assertFalse(probe["upstream_source_metadata"]["present"])
        self.assertFalse(probe["upstream_source_metadata"]["verified"])
        self.assertTrue(all(not entry["present"]
                            for entry in probe["probed_paths"]))

    def test_rights_block_is_not_approved(self):
        report = reference.build_report()
        rights = report["rights"]
        self.assertEqual(rights["status"], "not_approved")
        self.assertFalse(rights["synthetic_subset"]["approval"])
        self.assertFalse(rights["recorded_subset"]["approval"])
        self.assertFalse(rights["acceptance_use"])
        self.assertFalse(rights["redistribution"])
        self.assertIsNone(rights["approval_record"])

    def test_qualification_never_passes(self):
        report = reference.build_report()
        qualification = report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["decision"], "DEFER")
        self.assertFalse(qualification["qualifies"])
        self.assertFalse(qualification["all_required_results_present"])
        self.assertFalse(qualification["missing_result_promoted"])
        self.assertTrue(qualification["invalid_or_missing_control"])
        text = reference.canonical_text(report)
        self.assertNotIn('"qualifies":true', text)
        self.assertNotIn('"status":"qualified"', text)


class AdmissionGateTests(unittest.TestCase):
    def test_missing_bytes_defer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            declaration = _dummy_declaration()
            payloads = declaration.pop("_payloads")
            decision = reference.admission_decision(
                declaration, _lookup({}), False)
            self.assertEqual(decision["decision"], "DEFER")
            self.assertEqual(decision["reason"],
                             "declared_fixture_bytes_unverified")
            self.assertEqual(decision["missing_count"], 4)
            self.assertFalse(decision["bytes_verified"])
            self.assertFalse(root.exists() and any(root.iterdir()))
            self.assertTrue(payloads)

    def test_verified_bytes_without_rights_defer(self):
        declaration = _dummy_declaration()
        payloads = declaration.pop("_payloads")
        decision = reference.admission_decision(
            declaration, _lookup(payloads), False)
        self.assertEqual(decision["decision"], "DEFER")
        self.assertEqual(decision["reason"], "rights_not_approved")
        self.assertTrue(decision["bytes_verified"])
        self.assertEqual(decision["verified"], 4)

    def test_verified_bytes_and_rights_still_defer(self):
        declaration = _dummy_declaration()
        payloads = declaration.pop("_payloads")
        decision = reference.admission_decision(
            declaration, _lookup(payloads), True)
        self.assertEqual(decision["decision"], "DEFER")
        self.assertEqual(decision["reason"],
                         "no_approved_cohort_or_independent_result")
        self.assertFalse(decision["qualifies"])

    def test_size_and_digest_mismatch_rejected(self):
        declaration = _dummy_declaration()
        payloads = declaration.pop("_payloads")
        first = declaration["items"][0]["name"]
        payload, digest = payloads[first]
        sized = dict(payloads)
        sized[first] = (payload + b"\x00", digest)
        result = reference.verify_declared_files(
            reference.validate_declaration(declaration), _lookup(sized))
        self.assertEqual(result["size_mismatch"], [first])
        self.assertEqual(result["verified"], 3)
        wrong = dict(payloads)
        wrong[first] = (payload, "0" * 64)
        result = reference.verify_declared_files(
            reference.validate_declaration(declaration), _lookup(wrong))
        self.assertEqual(result["digest_mismatch"], [first])

    def test_live_recorded_control(self):
        report = reference.build_report()
        live = report["admission_controls"]["recorded_declaration_live"]
        self.assertEqual(live["decision"], "DEFER")
        self.assertEqual(live["item_count"], 108)
        self.assertEqual(live["missing_count"], 108)
        self.assertEqual(live["verified"], 0)
        self.assertFalse(live["bytes_verified"])
        gap = report["admission_controls"]["synthetic_declaration_gap"]
        self.assertEqual(gap["status"], "rejected")
        self.assertEqual(gap["rejected_code"], "unsupported_sample_rate")

    def test_declaration_rejections(self):
        base = _dummy_declaration()
        base.pop("_payloads")
        invalid = []
        mutated = copy.deepcopy(base)
        mutated["items"][0]["channels"] = 2
        invalid.append((mutated, "unsupported_channels"))
        mutated = copy.deepcopy(base)
        mutated["items"][0]["frames"] = 0
        invalid.append((mutated, "invalid_frames"))
        mutated = copy.deepcopy(base)
        mutated["items"][0]["sample_rate_hz"] = 44100
        invalid.append((mutated, "unsupported_sample_rate"))
        mutated = copy.deepcopy(base)
        mutated["items"][0]["name"] = "blind_case.wav"
        invalid.append((mutated, "blind_test_fixture_rejected"))
        mutated = copy.deepcopy(base)
        mutated["items"].pop()
        invalid.append((mutated, "group_roles_incomplete"))
        for value, code in invalid:
            with self.assertRaises(reference.Reject) as raised:
                reference.validate_declaration(value)
            self.assertEqual(raised.exception.code, code)


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.parse_strict_json('{"a":1,"a":2}')
        self.assertEqual(raised.exception.code, "duplicate_json_key:a")

    def test_nonfinite_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(reference.Reject) as raised:
                reference.parse_strict_json('{"x":' + token + "}")
            self.assertTrue(raised.exception.code.startswith(
                "nonfinite_json_constant:"))

    def test_invalid_json_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.parse_strict_json("{")
        self.assertEqual(raised.exception.code, "invalid_json")


class EvidenceTests(unittest.TestCase):
    def test_adverse_rejections_all_rejected(self):
        cases = reference.adverse_rejections()
        self.assertGreaterEqual(len(cases), 40)
        for case in cases:
            self.assertEqual(case["status"], "rejected", case)
            self.assertTrue(case["state_unchanged"], case)
            self.assertEqual(case["expected_code"], case["observed_code"])

    def test_release_gates_eight_blocked(self):
        gates = reference.release_gates()
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_exact_blockers_present(self):
        blockers = reference.exact_blockers()
        ids = {blocker["id"] for blocker in blockers}
        self.assertIn("licensed_audio_fixtures_absent", ids)
        self.assertIn("upstream_source_metadata_absent", ids)
        self.assertIn("rights_not_approved", ids)
        self.assertIn("paired_cohort_holdout_and_scoring_absent", ids)
        self.assertIn("evidence_adapter_exposure_undecided", ids)
        for blocker in blockers:
            self.assertTrue(blocker["requirement"])
            self.assertTrue(blocker["state"])

    def test_board_row_is_stable_only(self):
        row = reference.board_row()
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         row["stable_sha256"])
        self.assertNotIn("TASKS.json", reference.canonical_text(
            reference.build_report()["source_pins"]))

    def test_pins_match_live_files(self):
        for path, expected in reference.SOURCE_PINS.items():
            self.assertTrue((reference.SOURCE_ROOT / path).is_file(), path)
            self.assertEqual(
                reference.file_digest(reference.SOURCE_ROOT / path),
                expected, path)
        for path, expected in reference.BOUNDARY_PINS.items():
            self.assertTrue((reference.SDK_ROOT / path).is_file(), path)
            self.assertEqual(
                reference.file_digest(reference.SDK_ROOT / path),
                expected, path)

    def test_report_is_repeatable(self):
        texts = [reference.canonical_report(reference.build_report())[0]
                 for _ in range(3)]
        self.assertEqual(len(set(texts)), 1)

    def test_committed_report_matches_build(self):
        report_path = Path(__file__).resolve().parent / "report.json"
        text, digest = reference.canonical_report(reference.build_report())
        self.assertTrue(report_path.is_file())
        self.assertEqual(report_path.read_text(encoding="utf-8"), text)
        sidecar = report_path.with_name("report.json.sha256")
        self.assertEqual(sidecar.read_text(encoding="ascii"), digest + "\n")

    def test_boundary_is_all_false(self):
        report = reference.build_report()
        self.assertTrue(report["boundary"])
        self.assertTrue(all(value is False
                            for value in report["boundary"].values()))
        contract = reference.build_contract()
        self.assertTrue(all(value is False for key, value
                            in contract["public_boundary"].items()
                            if isinstance(value, bool)))


if __name__ == "__main__":
    unittest.main()
