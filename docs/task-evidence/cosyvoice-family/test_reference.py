# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the task-local SDK-COSYVOICE-FAMILY evidence package."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate_key"):
            reference.parse_strict_json_text(b'{"a":1,"a":2}')

    def test_nan_and_infinity_rejected(self) -> None:
        for payload in (b'{"a":NaN}', b'{"a":Infinity}',
                        b'{"a":-Infinity}'):
            with self.assertRaisesRegex(ValueError, "nonfinite_json"):
                reference.parse_strict_json_text(payload)

    def test_bom_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "bom_rejected"):
            reference.parse_strict_json_text(b'\xef\xbb\xbf{"a":1}')

    def test_non_object_root_rejected(self) -> None:
        for payload in (b"[]", b"null", b"1", b'"x"'):
            with self.assertRaisesRegex(ValueError, "json_root_not_object"):
                reference.parse_strict_json_text(payload)

    def test_trailing_data_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid_json"):
            reference.parse_strict_json_text(b'{"a":1} trailing')

    def test_canonical_bytes(self) -> None:
        value = {"b": [3, 2, 1], "a": {"z": True, "y": None}}
        payload = reference.canonical_bytes(value)
        self.assertTrue(payload.endswith(b"\n"))
        self.assertEqual(payload.count(b"\n"), 1)
        self.assertNotIn(b" ", payload)
        self.assertEqual(payload, reference.canonical_bytes(value))
        self.assertEqual(json.loads(payload), value)

    def test_canonical_rejects_float(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"value": 1.5})

    def test_object_digest_stable(self) -> None:
        first = reference.object_digest({"a": 1, "b": [2]})
        second = reference.object_digest({"b": [2], "a": 1})
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)


class AdmissionTests(unittest.TestCase):
    def test_valid_schema_control_is_not_evidence(self) -> None:
        controls = reference.admission_controls()
        self.assertEqual(len(controls["controls"]), 1)
        control = controls["controls"][0]
        self.assertEqual(control["status"], "accepted")
        self.assertIs(control["qualifies"], False)
        self.assertEqual(control["evidence_class"],
                         "synthetic_schema_control_not_evidence")
        self.assertIs(control["weights_loaded"], False)
        self.assertIs(control["conversion_performed"], False)

    def test_all_admission_cases_rejected(self) -> None:
        cases = reference.admission_controls()["cases"]
        self.assertGreaterEqual(len(cases), 60)
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        for case in cases:
            self.assertEqual(case["status"], "rejected")
            self.assertIs(case["qualifies"], False)
            self.assertIs(case["state_unchanged"], True)
            self.assertTrue(case["code"])

    def test_tts_only_adapter_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["adapter"]["converts_input_speech"] = False
        self.assertEqual(reference.admit_manifest(manifest)["code"],
                         "adapter_not_a_converter")
        manifest = reference._base_manifest()
        manifest["adapter"]["text_only_output"] = True
        self.assertEqual(reference.admit_manifest(manifest)["code"],
                         "adapter_text_only_rejected")

    def test_adverse_codes_present(self) -> None:
        codes = {case["code"] for case in
                 reference.admission_controls()["cases"]}
        for expected in (
                "manifest_not_object",
                "missing_field:manifest.source",
                "adapter_files_count",
                "adapter_file_sha256_invalid",
                "adapter_file_byte_count_invalid",
                "adapter_file_byte_count_nonfinite",
                "adapter_weight_terms_unresolved",
                "adapter_not_a_converter",
                "adapter_text_only_rejected",
                "format_sample_rate_nonfinite",
                "format_frame_samples_nonfinite",
                "reference_pair_sample_count_nonfinite",
                "reference_pair_target_consent_missing",
                "cohort_items_nonfinite",
                "cohort_source_target_pairs_missing",
                "rights_consent_missing",
                "rights_output_use_missing",
                "duplicate_key",
                "nonfinite_json",
                "bom_rejected",
                "json_root_not_object"):
            self.assertIn(expected, codes)

    def test_admission_is_pure(self) -> None:
        manifest = reference._base_manifest()
        first = reference.admit_manifest(copy.deepcopy(manifest))
        second = reference.admit_manifest(copy.deepcopy(manifest))
        self.assertEqual(first, second)
        self.assertEqual(first, {"status": "accepted", "code": "ok"})
        broken = copy.deepcopy(manifest)
        broken["format"]["sample_rate_hz"] = 24000
        self.assertEqual(reference.admit_manifest(broken)["status"],
                         "rejected")
        self.assertEqual(manifest, reference._base_manifest())


class PinAndProbeTests(unittest.TestCase):
    def test_board_projection_uses_stable_identity_only(self) -> None:
        projection = reference.board_row_projection()
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["component"], reference.COMPONENT_ID)
        self.assertEqual(projection["mode"], "research-control")
        self.assertEqual(set(projection), set(reference.BOARD_ROW_FIELDS))
        self.assertEqual(projection["depends_on"],
                         ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"])
        for field in ("status", "owner", "claim", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertNotIn(field, projection)

    def test_mutable_board_fields_do_not_change_projection(self) -> None:
        row = {
            "id": reference.TASK,
            "title": reference.TASK_TITLE,
            "component": reference.COMPONENT_ID,
            "mode": "research-control",
            "repository": "audio-sdk",
            "depends_on": ["SDK-FND-AUDIT"],
            "status": "queued",
            "owner": "nobody",
            "claim": None,
            "review": None,
            "handoff": None,
            "blocked_reason": None,
            "dispatch_priority": 9,
        }
        base = reference._project(row)
        mutated = dict(row, status="done", owner="someone",
                       dispatch_priority=0, blocked_reason="x")
        self.assertEqual(base, reference._project(mutated))
        mutated["title"] = "Different stable title"
        self.assertNotEqual(base, reference._project(mutated))

    def test_board_file_not_pinned(self) -> None:
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.PEER_PINS)
        text = reference.canonical_bytes(reference.build_contract())
        self.assertNotIn(b"TASKS.json", text)

    def test_source_present_and_pinned(self) -> None:
        probe = reference.source_probe()
        self.assertEqual(probe["status"], "present_pinned")
        self.assertIs(probe["present"], True)
        self.assertIs(probe["executed"], False)
        self.assertIs(probe["source_speech_conversion_checkpoint_included"],
                      False)
        self.assertEqual(probe["revision"], reference.SOURCE_REVISION)
        self.assertEqual(probe["license"], "Apache-2.0")
        self.assertEqual(probe["submodule"]["revision"],
                         reference.SUBMODULE_REVISION)

    def test_conversion_artifact_absent(self) -> None:
        probe = reference.conversion_artifact_probe()
        self.assertEqual(probe["status"],
                         "blocked_conversion_artifact_absent")
        self.assertEqual(probe["present_count"], 0)
        self.assertIs(probe["required_artifact_names_known"], False)
        self.assertEqual(probe["candidate_artifact_pins"], [])
        self.assertEqual(probe["bytes_read"], 0)
        self.assertEqual(probe["downloads_attempted"], 0)
        for row in probe["probes"]:
            self.assertIs(row["present"], False)
            self.assertIs(row["recursive_walk"], False)

    def test_pinned_runtime_absent(self) -> None:
        probe = reference.runtime_probe()
        self.assertEqual(probe["status"], "blocked_pinned_runtime_absent")
        self.assertIs(probe["pinned_runtime_present"], False)
        self.assertIs(probe["pinned_runtime_complete"], False)
        self.assertIs(probe["imported_or_executed"], False)
        self.assertEqual(probe["pinned_environment_paths_found"], [])

    def test_absence_probes_all_absent(self) -> None:
        probes = reference.conversion_artifact_probe()["probes"]
        self.assertEqual(len(probes), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(not row["present"] for row in probes))
        summary = reference.absence_summary(probes)
        self.assertEqual(summary["present_count"], 0)
        self.assertIs(summary["all_probes_absent"], True)
        self.assertIs(summary["download_attempted"], False)
        self.assertIs(summary["recursive_workspace_walk"], False)

    def test_peer_pins_exist_and_verify(self) -> None:
        self.assertEqual(len(reference.PEER_PINS), 3)
        for relative, digest in reference.PEER_PINS.items():
            path = reference.WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(reference.sha256_file(path), digest, relative)


class RoutingTests(unittest.TestCase):
    def test_six_members_and_digest(self) -> None:
        routing = reference.family_routing()
        entries = routing["entries"]
        self.assertEqual([row["id"] for row in entries],
                         ["FAM-0%d" % index for index in range(1, 7)])
        self.assertEqual(routing["ledger_sha256"],
                         reference.object_digest(entries))
        self.assertEqual(routing["entry_count"], 6)
        self.assertIs(routing["conversion_result_present"], False)
        self.assertIs(routing["tts_promoted_to_conversion"], False)
        for row in entries:
            self.assertIs(row["qualifies"], False)

    def test_tts_is_routed_not_promoted(self) -> None:
        entries = {row["id"]: row for row in
                   reference.family_routing()["entries"]}
        tts = entries["FAM-02"]
        self.assertEqual(tts["task_route"], "SDK-COSYVOICE-2-0-5B")
        self.assertEqual(tts["route"]["merge_commit"],
                         reference.TTS_MERGE_COMMIT)
        self.assertEqual(tts["route"]["sibling_report_sha256"],
                         reference.TTS_SIBLING_REPORT_SHA256)
        self.assertIs(tts["converts_input_speech"], False)
        self.assertIs(tts["route"]["is_source_speech_conversion"], False)

    def test_blocked_members_are_absent(self) -> None:
        entries = {row["id"]: row for row in
                   reference.family_routing()["entries"]}
        for member in ("FAM-03", "FAM-04", "FAM-05", "FAM-06"):
            self.assertEqual(entries[member]["status"], "absent_blocked")
            self.assertIs(entries[member]["present"], False)
            self.assertIs(entries[member]["converts_input_speech"], True)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = reference.build_contract()

    def test_disposition(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["defer_before"],
                         "opt_in_adapter_exposure")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertIs(self.report["proposal_only"], True)
        self.assertIs(self.report["incomplete"], True)
        disposition = self.report["disposition"]
        self.assertEqual(disposition["promotion"], "defer")
        self.assertEqual(disposition["production_exposure"], "DEFER")
        self.assertIs(disposition["missing_result_qualifies"], False)
        self.assertIs(disposition["registered"], False)
        self.assertIs(disposition["expose_as_processor"], False)

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([row["id"] for row in gates],
                         ["RG-0%d" % index for index in range(1, 9)])
        for row in gates:
            self.assertEqual(row["status"], "blocked")
            self.assertIs(row["qualifies"], False)
            self.assertEqual(row["linked_row"], reference._gate_link())
            self.assertTrue(row["reopen_condition"])
        self.assertEqual(self.report["remaining_gates"],
                         [row["id"] for row in gates])

    def test_six_artifacts_and_blockers(self) -> None:
        artifacts = self.report["required_artifacts"]
        blockers = self.report["exact_blockers"]
        self.assertEqual([row["id"] for row in artifacts],
                         ["ART-0%d" % index for index in range(1, 7)])
        self.assertEqual([row["id"] for row in blockers],
                         ["BLK-0%d" % index for index in range(1, 7)])
        for row in artifacts:
            self.assertIs(row["present"], False)
            self.assertIs(row["verified"], False)
            self.assertIs(row["blocked"], True)
        for row in blockers:
            self.assertEqual(row["status"], "open")
            self.assertIs(row["qualifies"], False)

    def test_qualification_all_blocked(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["readiness"], "incomplete")
        self.assertIs(qualification["not_qualified"], True)
        self.assertIs(qualification["all_release_gates_blocked"], True)
        self.assertIs(qualification["exact_source_present"], True)
        for key in ("exact_conversion_artifact_present",
                    "exact_runtime_present", "weight_rights_cleared",
                    "real_corpus_present", "real_result_present",
                    "reference_parity_result", "quality_result",
                    "listening_result", "timing_or_peak_result",
                    "benchmark_result", "missing_result_promoted"):
            self.assertIs(qualification[key], False)

    def test_voice_profile_blocked(self) -> None:
        profile = self.report["voice_profile"]
        self.assertEqual(profile["profile"], "voice")
        self.assertEqual(profile["status"], "blocked")
        self.assertEqual([row["id"] for row in profile["rows"]],
                         ["VOI-0%d" % index for index in range(1, 8)])
        for row in profile["rows"]:
            self.assertEqual(row["status"], "blocked")
            self.assertIs(row["qualifies"], False)
        for key, value in profile.items():
            if key in ("profile", "rows", "status"):
                continue
            self.assertIs(value, False)

    def test_public_v0_geometry_preserved(self) -> None:
        geometry = self.report["public_v0_geometry"]
        self.assertEqual(geometry, {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
            "preserved": True,
            "sdk_callback_invoked": False,
        })

    def test_boundary_claims_false(self) -> None:
        boundary = self.report["boundary"]
        self.assertIs(boundary["task_local_only"], True)
        for key, value in boundary.items():
            if key == "task_local_only":
                continue
            self.assertIs(value, False)

    def test_family_scope_decision(self) -> None:
        decision = self.report["family_scope_decision"]
        self.assertEqual(decision["decision"], "DEFER")
        self.assertEqual(decision["proceed_requirements"],
                         [row["id"] for row in self.report["gates"]])
        for key in ("processor_exposure", "developer_adapter_exposure",
                    "bench_adapter_exposure", "registered",
                    "default_enabled"):
            self.assertIs(decision[key], False)

    def test_routed_tts_not_admitted(self) -> None:
        routed = self.report["routed_tts_evidence"]
        self.assertEqual(
            routed["status"],
            "routed_to_sibling_task_not_reproduced_not_qualified")
        self.assertIs(routed["qualifies"], False)
        self.assertEqual(routed["task_route"], "SDK-COSYVOICE-2-0-5B")
        self.assertEqual(routed["task_kind"],
                         "text_to_speech_not_source_speech_conversion")
        self.assertEqual(routed["merge_commit"],
                         reference.TTS_MERGE_COMMIT)
        self.assertEqual(len(routed["entries"]), 3)
        self.assertIs(routed["artifact"]["admitted_as_result"], False)
        self.assertIs(routed["artifact"]["regenerable"], False)
        self.assertEqual(routed["artifact"]["sha256"],
                         reference.HISTORICAL_OUTPUT_SHA256)

    def test_no_float_anywhere(self) -> None:
        def walk(value, path="root"):
            if isinstance(value, float):
                self.fail("float at " + path)
            if isinstance(value, dict):
                for key, item in value.items():
                    walk(item, path + "." + key)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    walk(item, path + "." + str(index))
        walk(self.report)
        reference.assert_no_float(self.report)

    def test_committed_bytes_and_sidecar(self) -> None:
        report_payload = (HERE / "report.json").read_bytes()
        contract_payload = (HERE / "contract.json").read_bytes()
        self.assertEqual(report_payload,
                         reference.canonical_bytes(self.report))
        self.assertEqual(contract_payload,
                         reference.canonical_bytes(self.contract))
        digest = hashlib.sha256(report_payload).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text("ascii"),
                         f"{digest}  report.json\n")
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_contract_validation(self) -> None:
        reference.validate_contract(self.contract)
        broken = copy.deepcopy(self.contract)
        broken["release_gates"] = []
        with self.assertRaises(ValueError):
            reference.validate_contract(broken)

    def test_three_builds_byte_identical(self) -> None:
        observed = []
        for _ in range(3):
            text, digest = reference.canonical_report(reference.build_report())
            observed.append((text, digest, run.sources_bytes()))
        self.assertEqual(len({item[0] for item in observed}), 1)
        self.assertEqual(len({item[1] for item in observed}), 1)
        self.assertEqual(len({item[2] for item in observed}), 1)

    def test_sources_manifest_verifies(self) -> None:
        payload = (HERE / "SOURCES.sha256").read_bytes()
        self.assertEqual(payload, run.sources_bytes())
        for line in payload.decode("ascii").splitlines():
            if not line or line.startswith("#"):
                continue
            digest, name = line.split("  ", 1)
            path = (reference.AUDIO_ROOT / name.split(":", 1)[1]
                    if name.startswith("source:") else reference.WORKTREE / name)
            self.assertTrue(path.is_file(), name)
            self.assertEqual(reference.sha256_file(path), digest, name)


class ScopeTests(unittest.TestCase):
    def test_non_claims(self) -> None:
        text = " ".join(reference.NON_CLAIMS)
        for token in ("No source-speech conversion checkpoint",
                      "routed to SDK-COSYVOICE-2-0-5B",
                      "No listening",
                      "No provider or developer/evidence adapter"):
            self.assertIn(token, text)

    def test_write_scope(self) -> None:
        self.assertEqual(reference.WRITE_SCOPE,
                         "docs/task-evidence/cosyvoice-family/ only")

    def test_peer_evidence_paths_exist(self) -> None:
        for relative in reference.PEER_PINS:
            self.assertTrue((reference.WORKTREE / relative).is_file(),
                            relative)

    def test_forbidden_artifacts_absent(self) -> None:
        forbidden = (".pt", ".pth", ".onnx", ".wav", ".flac", ".so", ".dylib",
                     ".pyc", ".safetensors")
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden)


if __name__ == "__main__":
    unittest.main()
