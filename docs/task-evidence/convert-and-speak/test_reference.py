# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance suite for the SDK-CONVERT-AND-SPEAK package.

The suite is offline, stdlib-only and read-only. It exercises strict JSON,
fixed-path audit, synthetic PCM arithmetic, surrogate reset, caller-asset
identity validation and the exact adverse rejection matrix.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import reference

HERE = Path(__file__).resolve().parent


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest_fixture(root: Path) -> dict:
    runtime = root / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    files = {
        "source_archive_path": b"convert-and-speak-source",
        "weights_path": b"convert-and-speak-weights",
        "runtime_lock_path": b"numpy==0.0.0\n",
        "config_path": b'{"variant":"offline_whole_utterance"}\n',
        "license_record_path": b"license-record",
        "consent_record_path": b"consent-record",
        "source_reference_path": b"RIFF-source-reference",
        "target_reference_path": b"RIFF-target-reference",
    }
    manifest = {
        "channels": reference.SURROGATE_CHANNELS,
        "runtime_path": str(runtime),
        "sample_rate_input_hz": reference.SURROGATE_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": reference.SURROGATE_SAMPLE_RATE_HZ,
        "source_revision": "0" * 40,
        "variant": reference.CALLER_VARIANT,
    }
    for field, data in files.items():
        path = root / (field.replace("_path", "") + ".bin")
        path.write_bytes(data)
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = _sha(data)
    return manifest


class JsonAndCanonicalTests(unittest.TestCase):
    def test_canonical_json_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"value": math.nan})

    def test_strict_json_rejects_duplicate_key(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_rejects_infinity_constant(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":Infinity}')

    def test_strict_json_requires_object(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads("[1,2]")

    def test_canonical_normalizes_negative_zero(self) -> None:
        payload = reference.canonical_bytes({"z": -0.0})
        self.assertEqual(payload, b'{"z":0.0}')

    def test_fraction_text(self) -> None:
        from fractions import Fraction
        self.assertEqual(reference.fraction_text(Fraction(2, 3)), "2/3")
        self.assertEqual(reference.fraction_text(Fraction(6, 3)), "2")


class AuditTests(unittest.TestCase):
    def test_audit_observes_absence(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["source_present"])
        self.assertFalse(audit["weights_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["runtime_lock_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["consent_record_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertIsNone(audit["candidate_revision"])
        self.assertIsNone(audit["candidate_weights_sha256"])
        self.assertFalse(audit["candidate_geometry_documented"])

    def test_shared_sample_clips_are_only_samples(self) -> None:
        audit = reference.audit_assets()
        self.assertEqual(audit["sample_clip_count"], 3)
        self.assertEqual(len(audit["sample_clips"]), 3)
        self.assertIn("not Convert and Speak", audit["sample_clip_role"])

    def test_no_approved_identity_is_fabricated(self) -> None:
        self.assertIsNone(reference.APPROVED_SOURCE_REVISION)
        self.assertIsNone(reference.APPROVED_WEIGHTS_SHA256)


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "feasibility")
        self.assertFalse(identity["whole_file_hashed"])
        self.assertEqual(identity["claim"]["base_commit"],
                         reference.BASE_COMMIT)
        self.assertEqual(identity["claim"]["branch"], reference.BRANCH)
        expected = _sha(reference.canonical_bytes(identity["stable_fields"]))
        self.assertEqual(identity["stable_sha256"], expected)

    def test_mutable_fields_excluded(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(set(identity["excluded_mutable_fields"]),
                         set(reference.MUTABLE_TASK_FIELDS))
        for field in reference.MUTABLE_TASK_FIELDS:
            self.assertNotIn(field, identity["stable_fields"])

    def test_commits_are_full_hex(self) -> None:
        self.assertRegex(reference.BASE_COMMIT, r"^[0-9a-f]{40}$")


class PcmAndSurrogateTests(unittest.TestCase):
    def test_synthetic_pcm_is_deterministic(self) -> None:
        first = reference.synthetic_source_pcm()
        second = reference.synthetic_source_pcm()
        self.assertEqual(first, second)
        self.assertEqual(len(first), reference.SURROGATE_SOURCE_SAMPLES)
        self.assertEqual(
            len(reference.synthetic_target_reference_pcm()),
            reference.SURROGATE_TARGET_SAMPLES)

    def test_synthetic_pcm_is_finite_and_bounded(self) -> None:
        source = reference.validate_pcm(reference.synthetic_source_pcm())
        target = reference.validate_pcm(
            reference.synthetic_target_reference_pcm())
        self.assertTrue(all(math.isfinite(value) for value in source))
        self.assertTrue(all(math.isfinite(value) for value in target))
        self.assertLessEqual(max(abs(v) for v in source), 1.0)
        self.assertLessEqual(max(abs(v) for v in target), 1.0)

    def test_pcm_summary_is_deterministic(self) -> None:
        signal = reference.synthetic_source_pcm()
        first = reference.pcm_summary(signal, reference.SURROGATE_SAMPLE_RATE_HZ)
        second = reference.pcm_summary(
            signal, reference.SURROGATE_SAMPLE_RATE_HZ)
        self.assertEqual(first, second)
        self.assertEqual(first["duration_s"], "3")
        self.assertEqual(first["channels"], 1)

    def test_validate_pcm_accepts_integers(self) -> None:
        self.assertEqual(reference.validate_pcm([0, 0.5, -1]),
                         [0.0, 0.5, -1.0])

    def test_surrogate_transform_is_deterministic_and_bounded(self) -> None:
        values = reference.synthetic_source_pcm()
        first = reference.surrogate_transform(values)
        second = reference.surrogate_transform(values)
        self.assertEqual(first, second)
        self.assertEqual(len(first), len(values))
        self.assertLessEqual(max(abs(v) for v in first), 1.0)

    def test_surrogate_reset_matches_fresh(self) -> None:
        surrogate = reference.AccentSurrogate(epoch=1)
        surrogate.process(reference.synthetic_source_pcm()[:320])
        before = surrogate.state_digest
        surrogate.reset(2, 0)
        fresh = reference.AccentSurrogate(epoch=2)
        self.assertEqual(surrogate.state_digest, fresh.state_digest)
        self.assertNotEqual(before, surrogate.state_digest)

    def test_surrogate_rejection_leaves_state_unchanged(self) -> None:
        surrogate = reference.AccentSurrogate(epoch=1)
        surrogate.process([0.1, 0.2, 0.3])
        before = surrogate.state_digest
        with self.assertRaises(reference.Reject):
            surrogate.process([0.0, math.nan])
        self.assertEqual(before, surrogate.state_digest)
        with self.assertRaises(reference.Reject):
            surrogate.reset(1, 0)
        self.assertEqual(before, surrogate.state_digest)

    def test_duration_accounting_exact(self) -> None:
        result = reference.duration_accounting(
            reference.SURROGATE_SOURCE_SAMPLES,
            reference.SURROGATE_SOURCE_SAMPLES)
        self.assertEqual(result["source_duration_s"], "3")
        self.assertEqual(result["output_duration_s"], "3")
        self.assertEqual(result["duration_ratio"], "1")

    def test_duration_accounting_rejects_bad_counts(self) -> None:
        for value in (0, -1, True, 1.5, "4"):
            with self.assertRaises(reference.Reject):
                reference.duration_accounting(value, 1)
            with self.assertRaises(reference.Reject):
                reference.duration_accounting(1, value)

    def test_alignment_is_structural_offline(self) -> None:
        alignment = reference.alignment_accounting(48000)
        self.assertEqual(alignment["mode"], "offline_whole_utterance")
        self.assertFalse(alignment["streaming_supported"])
        self.assertFalse(alignment["candidate_alignment_asserted"])
        self.assertTrue(alignment["whole_clip_required"])
        self.assertEqual(alignment["tail_samples"], 48000)


class ManifestTests(unittest.TestCase):
    def test_manifest_identity_accepts_complete_local_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            result = reference.validate_manifest_identity(manifest)
        self.assertTrue(result["identity_valid"])
        self.assertEqual(result["files_checked"],
                         len(reference.CALLER_FILE_PAIRS))
        self.assertFalse(result["model_executed"])

    def test_manifest_admission_always_rejects_unapproved_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            with self.assertRaises(reference.Reject) as caught:
                reference.validate_caller_manifest(manifest)
        self.assertIn("no approved immutable source revision", str(caught.exception))

    def test_manifest_rejects_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["weights_path"]).unlink()
            with self.assertRaises(reference.Reject):
                reference.validate_manifest_identity(manifest)

    def test_manifest_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["weights_path"]).write_bytes(b"tampered")
            with self.assertRaises(reference.Reject):
                reference.validate_manifest_identity(manifest)

    def test_manifest_rejects_missing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["runtime_path"]).rmdir()
            with self.assertRaises(reference.Reject):
                reference.validate_manifest_identity(manifest)

    def test_manifest_rejects_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["config_path"] = "config.json"
            with self.assertRaises(reference.Reject):
                reference.validate_manifest_identity(manifest)

    def test_manifest_rejects_wrong_geometry_and_variant(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            for field, value in (("sample_rate_input_hz", 22050),
                                 ("sample_rate_output_hz", 24000),
                                 ("channels", 2),
                                 ("variant", "incremental_streaming")):
                broken = dict(manifest)
                broken[field] = value
                with self.assertRaises(reference.Reject):
                    reference.validate_manifest_identity(broken)


class AdverseControlTests(unittest.TestCase):
    def test_all_adverse_cases_are_invoked_and_rejected(self) -> None:
        results = reference.run_adverse_controls()
        self.assertEqual(len(results), len(reference.ADVERSE_CASE_IDS))
        self.assertEqual([item["case_id"] for item in results],
                         list(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(item["status"] == "rejected" for item in results))
        self.assertTrue(all(item["state_unchanged"] is True
                            for item in results))

    def test_control_is_labelled_synthetic(self) -> None:
        control = reference.build_control()
        self.assertEqual(control["plan_source"],
                         reference.CONTROL_PLAN_PROVENANCE)
        self.assertFalse(control["model_executed"])
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(control["duration"]["duration_ratio"], "1")
        self.assertFalse(control["alignment"]["streaming_supported"])
        self.assertFalse(control["surrogate"]["uses_target_reference"])
        self.assertFalse(control["fixtures"]["target_reference_used_for_scoring"])

    def test_acceptance_outcomes_are_all_unmeasured(self) -> None:
        control = reference.build_control()
        self.assertEqual(len(control["acceptance_outcomes"]), 4)
        self.assertTrue(all(item["measured"] is False
                            and item["value"] is None
                            for item in control["acceptance_outcomes"]))

    def test_fixture_validation_rejects_bad_specs(self) -> None:
        spec = reference.fixture_spec()
        self.assertEqual(reference.validate_fixture(spec), spec)
        for field, value in (("source_samples", 1), ("target_samples", 1),
                             ("sample_rate_hz", 8000), ("qh15_scale", 1)):
            broken = dict(spec)
            broken[field] = value
            with self.assertRaises(reference.Reject):
                reference.validate_fixture(broken)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = json.loads((HERE / "contract.json").read_text())

    def test_top_level_decision(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["profile"], "voice")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertIsNone(report["candidate_metrics"])

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])

    def test_eight_exact_blockers(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 8)
        self.assertTrue(all(item["state"] == "absent" for item in blockers))
        identifiers = {item["id"] for item in blockers}
        self.assertIn("pinned_source_absent", identifiers)
        self.assertIn("weights_and_checkpoint_identity_absent", identifiers)
        self.assertIn("voice_cohort_and_reference_pairs_absent", identifiers)

    def test_qualification_blocks_everything(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertTrue(qualification["no_missing_result_qualifies_candidate"])
        self.assertFalse(qualification["missing_result_promoted"])
        self.assertEqual(qualification["blocked_gate_count"], 8)
        self.assertEqual(qualification["blocked_gate_ids"],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        for key in ("exact_source_present", "exact_weights_present",
                    "exact_runtime_outputs_present", "rights_cleared_cohort",
                    "geometry_documented", "parity_measured", "timing_measured",
                    "listening", "real_corpus_used"):
            self.assertIs(qualification[key], False, key)

    def test_candidate_geometry_is_not_fabricated(self) -> None:
        candidate = self.report["candidate"]
        self.assertIsNone(candidate["reported_input_sample_rate_hz"])
        self.assertIsNone(candidate["reported_output_sample_rate_hz"])
        self.assertIsNone(candidate["reported_hop_samples"])
        self.assertIsNone(candidate["reported_parameter_count"])
        self.assertFalse(candidate["geometry_documented"])
        self.assertFalse(candidate["source_present"])
        self.assertFalse(candidate["weights_present"])
        self.assertFalse(candidate["runtime_present"])

    def test_voice_profile_has_no_satisfied_item(self) -> None:
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "voice")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertEqual(len(profile["required_items"]), 7)
        for item in profile["required_items"].values():
            self.assertIn(item["status"],
                          {"absent", "not_measured", "structural_only"})
            self.assertEqual(item["qualification_effect"], "none")
        self.assertEqual(
            profile["blocked_items"],
            sorted(name for name, item in profile["required_items"].items()
                   if item["status"] in {"absent", "not_measured"}))

    def test_all_boundary_and_scope_flags_are_false(self) -> None:
        boundary = self.report["boundary"]
        self.assertTrue(all(value is False for value in boundary.values()))
        scope = self.report["scope"]
        self.assertTrue(scope["synthetic_only"])
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key not in {"synthetic_only", "task_local_only"}:
                self.assertIs(value, False, key)

    def test_asset_audit_and_requirements_are_unqualified(self) -> None:
        audit = self.report["asset_audit"]
        self.assertFalse(audit["qualified"])
        self.assertEqual(audit["audit_result"], "absent")
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        self.assertIsNone(requirements["candidate_source"]["sha256"])
        self.assertIsNone(requirements["candidate_weights"]["sha256"])
        self.assertIsNone(
            requirements["exact_runtime"]["runtime_lock_sha256"])
        self.assertIsNone(
            requirements["approved_reference_parity_vector"]["sha256"])

    def test_controls_are_fail_closed(self) -> None:
        controls = self.report["controls"]
        self.assertTrue(controls["adverse_all_rejected"])
        self.assertEqual(controls["adverse_case_count"],
                         len(reference.ADVERSE_CASE_IDS))
        self.assertTrue(controls["nonfinite_rejected"])
        self.assertTrue(controls["missing_asset_rejected_before_processing"])
        self.assertTrue(controls["missing_result_never_qualifies"])
        self.assertFalse(
            self.report["caller_asset_contract"]["positive_admission_possible"])

    def test_source_reported_context_is_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"], "source_reported_not_measured_here")
        self.assertEqual(context["record_name"], "Convert and Speak")
        self.assertEqual(context["source_line"], 172)
        self.assertEqual(context["local_checkpoint"], "absent")
        self.assertEqual(context["local_run"], "not_run")
        self.assertIsNone(context["reported_latency"])
        self.assertIn("convert-and-speak.github.io", context["paper_demo_url"])

    def test_missing_artifacts_recorded(self) -> None:
        missing = self.report["missing_historical_artifacts"]
        self.assertIn(reference.SOURCE_CANDIDATES[0], missing)
        self.assertIn(reference.WEIGHTS_CANDIDATES[0], missing)
        self.assertIn(reference.COHORT_MANIFEST_PATH, missing)

    def test_no_whole_file_tasks_hash(self) -> None:
        encoded = reference.canonical_bytes(self.report).decode("utf-8")
        self.assertNotIn('TASKS.json":"', encoded)
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_report(reference.build_report())
        second = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)

    def test_on_disk_report_matches_generator(self) -> None:
        text, digest = reference.canonical_report(reference.build_report())
        self.assertEqual((HERE / "report.json").read_bytes(),
                         text.encode("utf-8"))
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")

    def test_contract_matches_report(self) -> None:
        contract = self.contract
        report = self.report
        self.assertEqual(contract["task"], report["task_id"])
        self.assertEqual(contract["decision"], report["decision"])
        self.assertEqual(contract["status"], report["status"])
        self.assertEqual(contract["evidence_status"], report["evidence_status"])
        self.assertEqual(contract["qualification_status"],
                         report["qualification_status"])
        self.assertEqual(contract["source_pins"], report["source_pins"])
        self.assertEqual(contract["boundary_pins"], report["boundary_pins"])
        self.assertEqual(contract["release_gates"], report["release_gates"])
        self.assertEqual(contract["exact_blockers"], report["exact_blockers"])
        self.assertEqual(contract["acceptance_profile"],
                         report["acceptance_profile"])
        self.assertEqual(contract["board_row"],
                         report["task_row_identity"])
        self.assertEqual(contract["qualification"], report["qualification"])

    def test_sources_manifest_has_no_tasks_json(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line and not line.startswith("#"):
                self.assertNotIn("TASKS.json", line)


if __name__ == "__main__":
    unittest.main()
