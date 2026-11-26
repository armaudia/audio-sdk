# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance checks for the task-local Loudness.ai blocker evidence package."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CanonicalJsonTests(unittest.TestCase):
    def test_canonical_is_sorted_and_compact(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": [2, 3]})
        self.assertEqual(payload, b'{"a":[2,3],"b":1}')

    def test_canonical_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"a": math.nan})
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"a": math.inf})

    def test_strict_loads_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_loads_rejects_nonfinite_constants(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
            with self.assertRaises(reference.Reject):
                reference.strict_loads(text)

    def test_strict_loads_rejects_non_object(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads("[]")

    def test_strict_loads_accepts_object(self) -> None:
        self.assertEqual(reference.strict_loads('{"a":1}'), {"a": 1})


class PcmTests(unittest.TestCase):
    def test_synthetic_source_is_bounded_and_finite(self) -> None:
        signal = reference.synthetic_noisy_pcm()
        self.assertEqual(len(signal), reference.CONTROL_SOURCE_SAMPLES)
        self.assertTrue(all(math.isfinite(value) for value in signal))
        self.assertLessEqual(max(abs(value) for value in signal), 1.0)

    def test_identity_control_is_exact(self) -> None:
        source = reference.synthetic_noisy_pcm()
        output = reference.identity_control_pcm()
        self.assertEqual(source, output)
        accounting = reference.identity_accounting(source, output)
        self.assertTrue(accounting["identity_exact"])
        self.assertEqual(accounting["max_abs_difference"], 0.0)

    def test_identity_rejects_length_mismatch(self) -> None:
        source = reference.synthetic_noisy_pcm()
        with self.assertRaises(reference.Reject):
            reference.identity_accounting(source, source[:-1])

    def test_frames_partition_exactly(self) -> None:
        frames = reference.split_frames(reference.identity_control_pcm())
        self.assertEqual(len(frames), reference.CONTROL_FRAME_COUNT)
        self.assertEqual(len(frames), 300)
        self.assertTrue(all(len(frame) == 160 for frame in frames))
        self.assertEqual(sum(len(frame) for frame in frames),
                         reference.CONTROL_SOURCE_SAMPLES)

    def test_validate_pcm_rejects_adverse(self) -> None:
        cases = (
            [],
            None,
            b"\x00",
            [0.0, math.nan],
            [0.0, math.inf],
            [0.0, -math.inf],
            [0.0, 1.5],
            [0.0, True],
            [0.0, "0.1"],
        )
        for value in cases:
            with self.assertRaises(reference.Reject, msg=repr(value)):
                reference.validate_pcm(value)

    def test_validate_pcm_rejects_wrong_rate_and_channels(self) -> None:
        signal = [0.0, 0.1]
        with self.assertRaises(reference.Reject):
            reference.validate_pcm(signal, 8000)
        with self.assertRaises(reference.Reject):
            reference.validate_pcm(signal, 16000, 2)

    def test_frame_length_is_exact(self) -> None:
        good = [0.0] * 160
        self.assertEqual(len(reference.validate_frame(good)), 160)
        for bad in ([0.0] * 159, [0.0] * 161, [math.nan] * 160):
            with self.assertRaises(reference.Reject):
                reference.validate_frame(bad)

    def test_split_frames_rejects_partial_frame(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.split_frames([0.0] * 161)


class AuditTests(unittest.TestCase):
    def test_audit_records_absence(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["vendor_source_present"])
        self.assertFalse(audit["vendor_runtime_present"])
        self.assertIsNone(audit["vendor_runtime_version"])
        self.assertFalse(audit["speech_engine_assets_present"])
        self.assertFalse(audit["component_licenses_present"])
        self.assertFalse(audit["vendor_license_present"])
        self.assertFalse(audit["documentation_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["runtime_lock_present"])
        self.assertFalse(audit["cohort_present"])
        self.assertFalse(audit["baseline_present"])
        self.assertFalse(audit["scorer_lock_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["comparison_manifest_present"])
        self.assertFalse(audit["parity_manifest_present"])
        self.assertTrue(audit["all_absence_probes_absent"])

    def test_every_probe_is_absent(self) -> None:
        probes = reference.probe_absence()
        self.assertEqual(len(probes), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(item["exists"] is False for item in probes))


class ManifestTests(unittest.TestCase):
    def test_shape_only_manifest_is_rejected_at_missing_assets(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(
                reference._shape_only_manifest())

    def test_existing_file_manifest_is_accepted_but_not_qualified(self) -> None:
        result = reference.validate_caller_manifest(
            reference._existing_file_manifest())
        self.assertTrue(result["accepted"])
        self.assertFalse(result["accepted_for_qualification"])
        self.assertFalse(result["vendor_runtime_approved"])
        self.assertFalse(result["asset_license_approved"])
        self.assertEqual(result["qualification_effect"], "none")
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["vendor_runtime_imported"])
        self.assertFalse(result["scorer_executed"])

    def test_manifest_field_set_is_exactly_declared(self) -> None:
        manifest = reference._existing_file_manifest()
        self.assertEqual(set(manifest), set(reference.CALLER_ASSET_FIELDS))
        self.assertEqual(len(manifest), 31)

    def test_manifest_rejects_adverse_cases(self) -> None:
        good = reference._existing_file_manifest()
        for field, value in (
                ("channels", 2),
                ("channels", True),
                ("sample_rate_hz", 4000),
                ("sample_rate_hz", True),
                ("sample_format", "pcm16"),
                ("scope", "denoise_plus_normalization"),
                ("variant", "incremental_streaming"),
                ("processing_stage_scope", "denoise_and_loudness"),
                ("vendor_runtime_version", "1.0"),
                ("vendor_entitlement_id", ""),
                ("platform", "macOS ARM64"),
                ("config_path", "relative/config.json"),
                ("config_sha256", "ABC")):
            manifest = dict(good)
            manifest[field] = value
            with self.assertRaises(reference.Reject, msg=field):
                reference.validate_caller_manifest(manifest)
        for field in ("config_sha256", "model_assets_path"):
            manifest = dict(good)
            del manifest[field]
            with self.assertRaises(reference.Reject, msg=field):
                reference.validate_caller_manifest(manifest)
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(
                dict(good, extra_field="x"))
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(
                dict(good, config_path="/nonexistent/config.json"))
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(
                dict(good, vendor_runtime_path="/nonexistent/runtime"))
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(
                dict(good, config_sha256="0" * 64))


class ControlTests(unittest.TestCase):
    def test_adverse_controls_all_reject(self) -> None:
        results = reference.run_adverse_controls()
        self.assertEqual(len(results), len(reference.ADVERSE_CASE_IDS))
        self.assertEqual(len(results), 39)
        self.assertEqual([item["case"] for item in results],
                         list(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(item["result"] == "rejected"
                            for item in results))

    def test_control_report_is_labeled(self) -> None:
        control = reference.build_control()
        self.assertFalse(control["model_executed"])
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["scorer"], "absent")
        self.assertEqual(control["plan_source"],
                         reference.CONTROL_PLAN_PROVENANCE)
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(control["duration"]["duration_ratio"], "1")
        self.assertTrue(control["identity"]["identity_exact"])
        self.assertEqual(control["frame_accounting"]["frame_count"], 300)
        self.assertTrue(control["frame_accounting"]["exact_partition"])
        self.assertFalse(control["alignment"]["streaming_supported"])
        self.assertFalse(
            control["alignment"]["vendor_content_delay_measured"])
        self.assertTrue(all(item["measured"] is False
                            for item in control["acceptance_outcomes"]))


class ReportContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.strict_loads(
            (HERE / "report.json").read_text(encoding="utf-8"))
        cls.contract = reference.strict_loads(
            (HERE / "contract.json").read_text(encoding="utf-8"))

    def test_report_disposition(self) -> None:
        self.assertEqual(self.report["task_id"], reference.TASK)
        self.assertEqual(self.report["component"], reference.COMPONENT)
        self.assertEqual(self.report["profile"], "enhancement")
        self.assertEqual(self.report["mode"], "external-adapter")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertTrue(self.report["proposal_only"])
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertIsNone(self.report["candidate_metrics"])

    def test_report_has_exactly_eight_blocked_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertEqual(
            [gate["id"] for gate in gates],
            [name for name, _ in reference.GATE_REQUIREMENTS])
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertEqual(qualification["blocked_gate_count"], 8)
        self.assertEqual(qualification["blocked_gate_ids"],
                         [gate["id"] for gate in gates])

    def test_all_enhancement_requirements_unsatisfied(self) -> None:
        profile = self.report["enhancement_profile"]
        self.assertEqual(profile["name"], "enhancement")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_enhancement_metrics"])
        self.assertEqual(len(profile["required_items"]),
                         len(reference.ENHANCEMENT_REQUIREMENTS))
        self.assertTrue(all(
            item["satisfied_for_qualification"] is False
            and item["qualification_effect"] == "none"
            for item in profile["required_items"]))

    def test_no_measured_acceptance_outcome(self) -> None:
        outcomes = self.report["reference_protocol"]["acceptance_outcomes"]
        self.assertTrue(outcomes)
        self.assertTrue(all(item["measured"] is False for item in outcomes))
        self.assertTrue(all(item["value"] is None for item in outcomes))

    def test_source_reported_context_is_labeled_and_empty(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"],
                         "source_reported_not_reproduced_here")
        self.assertEqual(context["reported_numeric_results"], [])
        self.assertIsNone(context["runtime_version"])
        self.assertIsNone(context["release_id"])
        self.assertIsNone(context["artifact_digest"])

    def test_boundary_and_scope_are_closed(self) -> None:
        for key, value in self.report["boundary"].items():
            if key == "descriptor_settings":
                self.assertEqual(value, {})
            else:
                self.assertIs(value, False, key)
        for key, value in self.report["scope"].items():
            if key == "task_local_only":
                self.assertIs(value, True)
            else:
                self.assertIs(value, False, key)

    def test_contract_disposition(self) -> None:
        self.assertEqual(self.contract[reference.SPDX_COPYRIGHT_KEY],
                         "2026 Tsakanyan Hovhannes")
        self.assertEqual(self.contract[reference.SPDX_LICENSE_KEY],
                         "Apache-2.0")
        self.assertEqual(self.contract["task"], reference.TASK)
        self.assertEqual(self.contract["profile"], "enhancement")
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"],
                         "proposal_only_incomplete")
        self.assertEqual(self.contract["write_scope"],
                         reference.TASK_PREFIX)
        self.assertEqual(len(self.contract["gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in self.contract["gates"]))
        self.assertEqual(self.contract["qualification"]["status"],
                         "not_qualified")

    def test_task_row_identity_is_stable_and_not_whole_file(self) -> None:
        for document in (self.report, self.contract):
            identity = document["task_row_identity"]
            self.assertFalse(identity["whole_file_hashed"])
            stable = identity["stable_fields"]
            digest = hashlib.sha256(
                reference.canonical_bytes(stable)).hexdigest()
            self.assertEqual(identity["stable_sha256"], digest)
            self.assertEqual(set(identity["excluded_mutable_fields"]),
                             set(reference.MUTABLE_TASK_FIELDS))
            encoded = reference.canonical_bytes(document).decode("utf-8")
            self.assertIsNone(re.search(
                r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', encoded))

    def test_report_bytes_regenerate(self) -> None:
        committed = (HERE / "report.json").read_bytes()
        rebuilt = reference.canonical_report_bytes(
            reference.build_report())
        self.assertEqual(committed, rebuilt)

    def test_sidecar_matches_report(self) -> None:
        digest = sha256_file(HERE / "report.json")
        sidecar = (HERE / "report.json.sha256").read_text(
            encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")


class SourcesTests(unittest.TestCase):
    def test_sources_manifest_pins_expected_prefixes(self) -> None:
        lines = (HERE / "SOURCES.sha256").read_text(
            encoding="utf-8").splitlines()
        pins = [line for line in lines
                if line and not line.startswith("#")]
        self.assertTrue(pins)
        labels = [line.split("  ", 1)[1] for line in pins]
        self.assertTrue(any(label.startswith("source:")
                            for label in labels))
        self.assertTrue(any(label.startswith("worktree:")
                            for label in labels))
        self.assertIn("pkg:README.md", labels)
        self.assertIn("pkg:reference.py", labels)
        self.assertIn("pkg:report.json", labels)
        self.assertTrue(all("TASKS.json" not in label for label in labels))

    def test_sources_manifest_has_no_duplicate_labels(self) -> None:
        lines = (HERE / "SOURCES.sha256").read_text(
            encoding="utf-8").splitlines()
        labels = [line.split("  ", 1)[1] for line in lines
                  if line and not line.startswith("#")]
        self.assertEqual(len(labels), len(set(labels)))

    def test_package_files_are_pinned(self) -> None:
        lines = (HERE / "SOURCES.sha256").read_text(
            encoding="utf-8").splitlines()
        pinned = {line.split("  ", 1)[1] for line in lines
                  if line and not line.startswith("#")}
        for name in reference.LOCAL_PIN_PATHS:
            self.assertIn("pkg:" + name, pinned)
        self.assertNotIn("pkg:SOURCES.sha256", pinned)


class LicenseTests(unittest.TestCase):
    def test_headers_and_sidecars(self) -> None:
        copyright_line = "SPDX-" "FileCopyrightText: 2026 Tsakanyan Hovhannes"
        license_line = "SPDX-" "License-Identifier: Apache-2.0"
        for name in ("README.md", "reference.py", "run.py",
                     "verify.py", "test_reference.py"):
            head = "\n".join((HERE / name).read_text(
                encoding="utf-8").splitlines()[:8])
            self.assertIn(copyright_line, head, name)
            self.assertIn(license_line, head, name)
        for name in ("contract.json", "report.json", "report.json.sha256",
                     "SOURCES.sha256"):
            sidecar = (HERE / (name + ".license")).read_text(
                encoding="utf-8")
            self.assertIn(copyright_line, sidecar, name)
            self.assertIn(license_line, sidecar, name)

    def test_json_rejects_nonfinite_constants(self) -> None:
        for name in ("contract.json", "report.json"):
            text = (HERE / name).read_text(encoding="utf-8")
            loaded = reference.strict_loads(text)
            self.assertIsInstance(loaded, dict)


if __name__ == "__main__":
    unittest.main()
