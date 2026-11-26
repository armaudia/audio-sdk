# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local F0-contour-smoothing evidence block."""

from __future__ import annotations

import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent


def _sha(data: bytes) -> str:
    return reference.sha256_bytes(data)


def _manifest_fixture(root: Path) -> dict:
    names = (
        "license_record_path",
        "weights_path",
        "smoother_config_path",
        "target_contour_path",
        "voicing_policy_path",
        "pitch_reference_manifest_path",
        "metric_spec_path",
        "cohort_manifest_path",
        "rights_decision_path",
        "runtime_lock_path",
    )
    source = root / "source"
    runtime = root / "runtime"
    source.mkdir()
    runtime.mkdir()
    manifest = {
        "asset_storage": "external",
        "source_checkout_path": str(source),
        "source_revision": "a" * 40,
        "runtime_path": str(runtime),
        "smoother_id": "median_filter_exact",
        "task_kind": reference.TASK_KIND,
        "comparison_baseline": reference.COMPARISON_BASELINE,
        "variant": reference.CALLER_VARIANT,
        "channels": reference.CHANNELS,
        "sample_rate_input_hz": reference.SAMPLE_RATE_HZ,
        "sample_rate_output_hz": reference.SAMPLE_RATE_HZ,
    }
    for index, name in enumerate(names):
        path = root / (name + ".bin")
        path.write_bytes(("asset-%d" % index).encode("ascii"))
        manifest[name] = str(path)
        manifest[name.replace("_path", "_sha256")] = _sha(path.read_bytes())
    return manifest


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self):
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.load_strict_json_text('{"a":1,"a":2}')
        self.assertEqual(caught.exception.code, "duplicate_json_key:a")

    def test_nan_rejected(self):
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.load_strict_json_text('{"a":NaN}')
        self.assertEqual(
            caught.exception.code, "nonfinite_json_constant:NaN")

    def test_infinity_rejected(self):
        with self.assertRaises(reference.ReferenceRejection):
            reference.load_strict_json_text("[Infinity]")

    def test_bom_rejected(self):
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.load_strict_json_text('\ufeff{"a":1}')
        self.assertEqual(caught.exception.code, "json_bom")

    def test_array_root_accepted_then_object_required(self):
        self.assertEqual(reference.load_strict_json_text("[1,2]"), [1, 2])
        with self.assertRaises(reference.ReferenceRejection):
            reference.load_strict_json_object_text("[1,2]")

    def test_float_not_canonical(self):
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.canonical_text({"a": 1.5})
        self.assertTrue(caught.exception.code.startswith("noncanonical_float"))

    def test_canonical_round_trip(self):
        value = {"b": [1, True, None, "x"], "a": 2}
        text = reference.canonical_text(value)
        self.assertEqual(text, '{"a":2,"b":[1,true,null,"x"]}')
        self.assertEqual(reference.load_strict_json_text(text), value)
        self.assertEqual(reference.object_digest(value),
                         _sha(text.encode("utf-8")))


class TaskIdentityTests(unittest.TestCase):
    def test_stable_identity(self):
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK_ID)
        self.assertEqual(
            identity["stable_fields"]["component"], reference.COMPONENT)
        self.assertEqual(
            identity["stable_fields"]["repository"], reference.REPOSITORY)
        self.assertEqual(identity["stable_fields"]["mode"], reference.MODE)
        self.assertEqual(identity["stable_fields"]["title"], reference.TITLE)
        self.assertEqual(
            set(identity["stable_fields"]),
            set(reference.STABLE_TASK_FIELDS))

    def test_board_never_whole_file_hashed(self):
        identity = reference.task_row_identity()
        self.assertFalse(identity["full_tasks_json_hashed"])
        self.assertFalse(identity["whole_file_hashed"])
        self.assertIn("status", identity["excluded_mutable_fields"])
        self.assertIn("claim", identity["excluded_mutable_fields"])
        for label in reference.SOURCE_PINS:
            self.assertNotIn("TASKS.json", label)

    def test_stable_digest_recomputed(self):
        identity = reference.task_row_identity()
        expected = _sha(reference.canonical_text(
            identity["stable_fields"]).encode("utf-8"))
        self.assertEqual(identity["stable_sha256"], expected)

    def test_source_pins_pinned_here(self):
        self.assertEqual(
            reference.SOURCE_PINS[reference.CANDIDATE_RECORD_PATH],
            "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245")


class AbsenceTests(unittest.TestCase):
    def test_all_absence_probes_absent(self):
        probes = reference.probe_absence()
        self.assertEqual(len(probes), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(item["exists"] is False for item in probes))

    def test_audit_has_no_candidate_artifact(self):
        audit = reference.audit_assets()
        self.assertFalse(audit["source_checkout_present"])
        self.assertFalse(audit["weights_present"])
        self.assertFalse(audit["smoother_config_present"])
        self.assertFalse(audit["target_contour_present"])
        self.assertFalse(audit["voicing_policy_present"])
        self.assertFalse(audit["pitch_reference_present"])
        self.assertFalse(audit["metric_spec_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["parity_manifest_present"])
        self.assertTrue(audit["all_absence_probes_absent"])

    def test_present_artifact_fails_closed(self):
        probes = [{"path": "x", "exists": True}]
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.assert_no_candidate_artifacts(probes)
        self.assertTrue(
            caught.exception.code.startswith("candidate_artifact_present"))

    def test_probe_count_mismatch_fails_closed(self):
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.assert_no_candidate_artifacts([])
        self.assertEqual(
            caught.exception.code, "absence_probe_count_mismatch")


class PcmTests(unittest.TestCase):
    def test_stimulus_length_and_determinism(self):
        first = reference.synthetic_source_pcm()
        second = reference.synthetic_source_pcm()
        self.assertEqual(len(first), reference.CONTROL_SOURCE_SAMPLES)
        self.assertEqual(first, second)

    def test_stimulus_segments(self):
        segments = reference._segment_map()
        self.assertEqual(segments[0][0], "silence_lead")
        self.assertEqual(segments[-1][2], reference.CONTROL_SOURCE_SAMPLES)
        for index in range(1, len(segments)):
            self.assertEqual(segments[index - 1][2], segments[index][1])

    def test_stimulus_values_finite_and_bounded(self):
        for value in reference.synthetic_source_pcm():
            self.assertTrue(math.isfinite(value))
            self.assertLessEqual(abs(value), 1.0)

    def test_validate_pcm_rejects_nonfinite(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_pcm([0.0, value])

    def test_validate_pcm_rejects_shape_and_type(self):
        for case in ([], None, b"\x00", [True], ["0.1"], [1.5]):
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_pcm(case)

    def test_validate_pcm_accepts_control(self):
        pcm = reference.validate_pcm(reference.synthetic_source_pcm())
        self.assertEqual(len(pcm), reference.CONTROL_SOURCE_SAMPLES)

    def test_pcm_summary_is_integer_only(self):
        summary = reference.pcm_summary(reference.synthetic_source_pcm())
        for key, value in summary.items():
            if key != "sha256":
                self.assertIsInstance(value, int)
        self.assertEqual(summary["samples"], reference.CONTROL_SOURCE_SAMPLES)
        self.assertEqual(
            summary["duration_ns"],
            reference.CONTROL_SOURCE_SAMPLES * reference.SAMPLE_PERIOD_NS)
        self.assertLessEqual(summary["peak_micro"], reference.MICRO_SCALE)

    def test_identity_transform_is_exact(self):
        source = reference.synthetic_source_pcm()
        output = reference.identity_transform(source)
        self.assertEqual(output, source)
        self.assertEqual(reference.pcm_summary(source)["sha256"],
                         reference.pcm_summary(output)["sha256"])


class RequestAdmissionTests(unittest.TestCase):
    def test_identity_request_admitted(self):
        result = reference.admit_request(reference.identity_request())
        self.assertTrue(result["accepted"])
        self.assertTrue(result["identity_control"])
        self.assertFalse(result["candidate_smoother_used"])
        self.assertEqual(result["qualification_effect"], "none")

    def test_smoothing_target_rejected(self):
        request = reference.identity_request()
        request["target"] = reference.SMOOTHING_TARGET
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.admit_request(request)
        self.assertEqual(caught.exception.code, "absent_candidate_smoother")

    def test_fixed_contour_target_rejected(self):
        request = reference.identity_request()
        request["target"] = reference.FIXED_CONTOUR_BASELINE
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.admit_request(request)
        self.assertEqual(
            caught.exception.code, "absent_exact_target_contour")

    def test_unknown_target_rejected(self):
        request = reference.identity_request()
        request["target"] = "magic"
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.admit_request(request)
        self.assertEqual(caught.exception.code, "unknown_target")

    def test_nonidentity_baseline_rejected(self):
        request = reference.identity_request()
        request["comparison_baseline"] = reference.FIXED_CONTOUR_BASELINE
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.admit_request(request)
        self.assertEqual(caught.exception.code, "baseline_not_identity")

    def test_streaming_variant_rejected(self):
        request = reference.identity_request()
        request["variant"] = "incremental_streaming"
        with self.assertRaises(reference.ReferenceRejection):
            reference.admit_request(request)

    def test_noncontrol_geometry_rejected(self):
        for key, value in (("sample_rate_hz", 8000),
                           ("channels", 2),
                           ("frame_samples", 320)):
            request = reference.identity_request()
            request[key] = value
            with self.assertRaises(reference.ReferenceRejection) as caught:
                reference.admit_request(request)
            self.assertTrue(
                caught.exception.code.startswith("unsupported_control_geometry"))

    def test_missing_and_extra_fields_rejected(self):
        request = reference.identity_request()
        request.pop("pcm")
        with self.assertRaises(reference.ReferenceRejection):
            reference.admit_request(request)
        request = reference.identity_request()
        request["extra"] = 1
        with self.assertRaises(reference.ReferenceRejection):
            reference.admit_request(request)


class ManifestTests(unittest.TestCase):
    def test_valid_manifest_accepted_without_execution(self):
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["audio_read"])
        self.assertEqual(result["files_checked"], len(
            reference.CALLER_FILE_PAIRS))

    def test_missing_and_extra_fields(self):
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            dropped = dict(manifest)
            dropped.pop("weights_sha256")
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(dropped)
            extra = dict(manifest)
            extra["extra"] = 1
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(extra)

    def test_relative_path_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["weights_path"] = "weights.bin"
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["weights_sha256"] = "0" * 64
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_placeholder_smoother_id_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["smoother_id"] = "unspecified"
            with self.assertRaises(reference.ReferenceRejection) as caught:
                reference.validate_caller_manifest(manifest)
            self.assertIn("placeholder", caught.exception.code)

    def test_non_duration_preserving_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["sample_rate_output_hz"] = 48000
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_directory_missing_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["runtime_path"] = str(Path(raw) / "absent")
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_package_shape_probe_is_not_a_candidate(self):
        manifest = reference._existing_file_manifest()
        result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["model_executed"])

    def test_manifest_fields_are_exact(self):
        self.assertEqual(
            len(reference.CALLER_ASSET_FIELDS),
            len(set(reference.CALLER_ASSET_FIELDS)))
        for path, sha in reference.CALLER_FILE_PAIRS:
            self.assertIn(path, reference.CALLER_ASSET_FIELDS)
            self.assertIn(sha, reference.CALLER_ASSET_FIELDS)


class SmootherSpecTests(unittest.TestCase):
    def test_complete_spec_admitted_without_execution(self):
        result = reference.admit_smoother_specification(
            reference.synthetic_complete_spec())
        self.assertTrue(result["accepted"])
        self.assertFalse(result["candidate_executed"])
        self.assertEqual(result["qualification_effect"], "none")

    def test_placeholder_and_missing_parts_rejected(self):
        cases = (
            {"smoother_id": "unspecified"},
            {"algorithm_family": "default"},
            {"target_contour_defined": False},
            {"voicing_policy_defined": False},
            {"parameters": {}},
            {"metric_ids": []},
        )
        for override in cases:
            spec = dict(reference.synthetic_complete_spec(), **override)
            with self.assertRaises(reference.ReferenceRejection):
                reference.admit_smoother_specification(spec)

    def test_float_and_zero_parameters_rejected(self):
        for value in (1.0, 0):
            spec = dict(reference.synthetic_complete_spec())
            spec["parameters"] = {"window_frames": value}
            with self.assertRaises(reference.ReferenceRejection):
                reference.admit_smoother_specification(spec)

    def test_duplicate_metrics_rejected(self):
        spec = dict(reference.synthetic_complete_spec())
        spec["metric_ids"] = ["pitch_rmse_cents", "pitch_rmse_cents"]
        with self.assertRaises(reference.ReferenceRejection):
            reference.admit_smoother_specification(spec)

    def test_extra_field_rejected(self):
        spec = dict(reference.synthetic_complete_spec(), extra=1)
        with self.assertRaises(reference.ReferenceRejection):
            reference.admit_smoother_specification(spec)


class AdverseTests(unittest.TestCase):
    def test_all_adverse_cases_rejected(self):
        results = reference.run_adverse_controls()
        self.assertEqual(len(results), len(reference.ADVERSE_CASE_IDS))
        self.assertEqual([item["case"] for item in results],
                         list(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(item["result"] == "rejected"
                            for item in results))
        self.assertTrue(all(item["reason"] for item in results))

    def test_more_than_forty_adverse_cases(self):
        self.assertGreaterEqual(len(reference.ADVERSE_CASE_IDS), 40)

    def test_adverse_ids_unique(self):
        self.assertEqual(len(reference.ADVERSE_CASE_IDS),
                         len(set(reference.ADVERSE_CASE_IDS)))


class ControlTests(unittest.TestCase):
    def test_control_is_identity_only(self):
        control = reference.build_control()
        self.assertFalse(control["model_executed"])
        self.assertEqual(control["executor"], "absent")
        baseline = control["identity_baseline"]
        self.assertTrue(baseline["sample_count_equal"])
        self.assertTrue(baseline["duration_equal"])
        self.assertTrue(baseline["digest_equal"])
        self.assertTrue(baseline["peak_bounded"])
        self.assertEqual(baseline["content_delay_samples"], 0)
        self.assertEqual(baseline["qualification_effect"], "none")

    def test_candidate_targets_rejected(self):
        control = reference.build_control()
        rejected = control["request_admission"]["rejected_targets"]
        self.assertEqual(
            [item["target"] for item in rejected],
            [reference.SMOOTHING_TARGET, reference.FIXED_CONTOUR_BASELINE])
        self.assertEqual(
            [item["reason"] for item in rejected],
            ["absent_candidate_smoother", "absent_exact_target_contour"])

    def test_voice_outcomes_unmeasured(self):
        control = reference.build_control()
        self.assertEqual(len(control["acceptance_outcomes"]), 8)
        self.assertTrue(all(item["measured"] is False
                            for item in control["acceptance_outcomes"]))
        self.assertTrue(all(item["value"] is None
                            for item in control["acceptance_outcomes"]))

    def test_control_geometry_is_control_only(self):
        control = reference.build_control()
        geometry = control["geometry"]
        self.assertFalse(geometry["candidate_geometry_asserted"])
        self.assertEqual(geometry["candidate_geometry_status"],
                         "unestablished")
        self.assertEqual(geometry["target_contour_status"],
                         "unestablished")


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.report = reference.build_report()
        self.text, self.digest = reference.canonical_report(self.report)

    def test_report_is_deterministic(self):
        again = reference.build_report()
        self.assertEqual(reference.canonical_report(again)[0], self.text)
        self.assertEqual(_sha(self.text.encode("utf-8")), self.digest)

    def test_report_has_no_json_floats(self):
        def scan(value):
            if isinstance(value, float):
                raise AssertionError("float found in canonical report")
            if isinstance(value, list):
                for item in value:
                    scan(item)
            elif isinstance(value, dict):
                for item in value.values():
                    scan(item)

        scan(reference.load_strict_json_text(self.text))
        reference._check_canonical_value(self.report, "root")

    def test_decision_and_qualification(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertFalse(
            self.report["qualification"]["candidate_qualified"])
        self.assertIsNone(self.report["candidate_metrics"])

    def test_eight_blocked_gates(self):
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual(len({gate["id"] for gate in gates}), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertEqual(self.report["qualification"]["blocked_gate_count"], 8)

    def test_eight_exact_blockers(self):
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 8)
        self.assertEqual([item["id"] for item in blockers],
                         ["B%d" % index for index in range(1, 9)])
        self.assertEqual([item["gate"] for item in blockers],
                         [item[0] for item in reference.GATE_REQUIREMENTS])

    def test_candidate_is_absent(self):
        candidate = self.report["candidate"]
        self.assertEqual(candidate["record_status"], "unavailable/blocked")
        self.assertEqual(candidate["candidate_kind"],
                         "unspecified_algorithm_family")
        for field in ("source_present", "weights_present",
                      "smoother_parameters_present", "target_contour_present",
                      "voicing_policy_present", "pitch_reference_present",
                      "metric_spec_present", "runtime_present",
                      "implemented_here", "adapter_present",
                      "exact_numeric_output_present"):
            self.assertIs(candidate[field], False, field)

    def test_voice_profile_unsatisfied(self):
        profile = self.report["voice_profile"]
        self.assertEqual(len(profile["required_items"]), 8)
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_model_metrics"])
        self.assertTrue(all(
            not item["satisfied_for_qualification"]
            for item in profile["required_items"]))

    def test_controls_all_rejected(self):
        controls = self.report["controls"]
        self.assertTrue(controls["adverse_all_rejected"])
        self.assertEqual(controls["adverse_case_count"],
                         len(reference.ADVERSE_CASE_IDS))
        self.assertTrue(controls["absence_probes_all_absent"])

    def test_boundary_is_task_local(self):
        boundary = self.report["boundary"]
        for field in ("provider_registered", "registry_changed",
                      "shared_cmake_changed", "ci_changed",
                      "public_api_abi_changed", "real_corpus_or_weights",
                      "release_claim"):
            self.assertIs(boundary[field], False, field)
        self.assertIs(boundary["installed_v0_unchanged"], True)
        self.assertEqual(boundary["format"]["sample_rate_hz"], 16000)
        self.assertEqual(boundary["format"]["frame_samples"], 160)
        self.assertEqual(self.report["scope"]["write_scope"],
                         [reference.TASK_PREFIX])


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.report = reference.build_report()
        self.text, self.digest = reference.canonical_report(self.report)
        self.contract = reference.build_contract(self.report, self.digest)

    def test_contract_is_deterministic(self):
        again = reference.build_contract(self.report, self.digest)
        self.assertEqual(reference.canonical_text(again),
                         reference.canonical_text(self.contract))

    def test_contract_semantics(self):
        self.assertEqual(self.contract["task"], reference.TASK_ID)
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["evidence_status"], "incomplete")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertEqual(self.contract["blocked_release_gate_count"], 8)
        self.assertEqual(self.contract["task_prefix"], reference.TASK_PREFIX)
        self.assertEqual(self.contract["write_scope"], reference.TASK_PREFIX)

    def test_artifact_pins_cover_files(self):
        pins = self.contract["artifact_pins"]
        for name in reference.ARTIFACT_FILES:
            self.assertIn(reference.TASK_PREFIX + name, pins)
        self.assertEqual(
            pins[reference.TASK_PREFIX + "report.json"], self.digest)
        self.assertEqual(
            pins[reference.TASK_PREFIX + "reference.py"],
            reference.file_digest(HERE / "reference.py"))

    def test_contract_contains_eight_gates(self):
        self.assertEqual(len(self.contract["gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in self.contract["gates"]))
        self.assertEqual(self.contract["gates"], self.report["gates"])

    def test_contract_spdx_fields(self):
        self.assertEqual(self.contract["SPDX-License-Identifier"],
                         "Apache-2.0")
        self.assertEqual(self.contract["SPDX-FileCopyrightText"],
                         "2026 Tsakanyan Hovhannes")


class SourceManifestTests(unittest.TestCase):
    def test_sources_bytes_pins_every_authored_file(self):
        text = reference.sources_bytes().decode("utf-8")
        lines = [line for line in text.splitlines()
                 if line and not line.startswith("#")]
        labels = [line.split("  ", 1)[1] for line in lines]
        for name in reference.PIN_FILES:
            self.assertIn("pkg:" + name, labels)
        self.assertNotIn("pkg:SOURCES.sha256", labels)
        self.assertFalse(any("TASKS.json" in label for label in labels))

    def test_sources_bytes_grouped_and_sorted_by_label(self):
        text = reference.sources_bytes().decode("utf-8")
        lines = [line for line in text.splitlines()
                 if line and not line.startswith("#")]
        labels = [line.split("  ", 1)[1] for line in lines]
        for prefix in ("source:", "worktree:", "pkg:"):
            group = [label for label in labels if label.startswith(prefix)]
            self.assertEqual(group, sorted(group), prefix)
        index = {"source:": 0, "worktree:": 1, "pkg:": 2}
        order = [index[label.split(":", 1)[0] + ":"] for label in labels]
        self.assertEqual(order, sorted(order))

    def test_every_pinned_local_file_exists(self):
        for name in reference.PIN_FILES:
            self.assertTrue((HERE / name).is_file(), name)


class ScopeTests(unittest.TestCase):
    """Regression coverage for the merge-base scope comparison."""

    def _git(self, repo: Path, *arguments: str) -> str:
        result = subprocess.run(["git", "-C", str(repo), *arguments],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def _repository(self, root: Path) -> Path:
        repo = root / "audio-sdk"
        repo.mkdir()
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.name", "scope-fixture")
        self._git(repo, "config", "user.email", "scope@example.invalid")
        self._git(repo, "config", "commit.gpgsign", "false")
        task = repo / reference.TASK_PREFIX
        task.mkdir(parents=True)
        (task / "README.md").write_text("task package\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "task package")
        return repo

    def _add_siblings(self, repo: Path) -> None:
        # Later main merges land unrelated task packages beside this one.
        for name in ("sibling-alpha", "sibling-beta"):
            sibling = repo / "docs/task-evidence" / name
            sibling.mkdir(parents=True)
            (sibling / "report.json").write_text("{}\n", encoding="utf-8")
            (sibling / "verify.py").write_text("# sibling\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "unrelated sibling packages")

    def test_sibling_additions_after_base_pass_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            historical = self._git(repo, "rev-parse", "HEAD")
            self._add_siblings(repo)
            head = self._git(repo, "rev-parse", "HEAD")

            base = reference.scope_base(repo)
            self.assertEqual(base, head)
            self.assertEqual(reference.scope_changed_paths(repo, base), [])
            self.assertEqual(reference.scope_violations([]), [])

            # The old fixed base would have reported the siblings; the
            # merge-base comparison must not.
            historic = reference.scope_changed_paths(repo, historical)
            self.assertIn("docs/task-evidence/sibling-alpha/report.json",
                          historic)
            self.assertTrue(reference.scope_violations(historic))

    def test_branch_out_of_scope_edit_fails_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._add_siblings(repo)
            self._git(repo, "checkout", "-q", "-b",
                      "swarm/SDK-F0-CONTOUR-SMOOTHING-scope")
            (repo / "CMakeLists.txt").write_text("changed\n", encoding="utf-8")
            self._git(repo, "add", "CMakeLists.txt")
            self._git(repo, "commit", "-qm", "out of scope edit")

            base = reference.scope_base(repo)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, ["CMakeLists.txt"])
            self.assertEqual(reference.scope_violations(paths),
                             ["CMakeLists.txt"])

    def test_missing_base_ref_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "branch", "-m", "detached-work")
            self.assertIsNone(reference.scope_base(repo))


if __name__ == "__main__":
    unittest.main()
