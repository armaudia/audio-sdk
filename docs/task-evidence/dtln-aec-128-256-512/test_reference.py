# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance suite for the SDK-DTLN-AEC-128-256-512 package.

The suite is offline, stdlib-only and read-only. It exercises strict JSON,
fixture arithmetic, paired echo/near-end processing at the 512/128 frame clock,
block invariance, reset, caller-asset identity validation and the exact adverse
rejection matrix.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402


class ReportIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_disposition_is_defer_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification"]["status"],
                         "not_qualified")
        self.assertFalse(self.report["qualification"]["qualifies"])

    def test_eight_blocked_release_gates(self):
        gates = self.report["release_gates"]
        self.assertEqual([row["id"] for row in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(row["status"] == "blocked" for row in gates))

    def test_room_profile_items_are_synthetic_or_blocked(self):
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "room")
        self.assertEqual(len(profile["required_items"]), 11)
        statuses = {row["status"] for row in profile["required_items"].values()}
        self.assertTrue(statuses.issubset({"synthetic_only", "blocked"}))
        blocked = sorted(name for name, row in profile["required_items"].items()
                         if row["status"] == "blocked")
        self.assertEqual(self.report["profile_blockers"], blocked)

    def test_documented_io_geometry_does_not_invent_delay_or_state(self):
        candidate = self.report["candidate"]
        self.assertEqual(candidate["reported_input_sample_rate_hz"], 16000)
        self.assertEqual(candidate["reported_block_samples"], 512)
        self.assertEqual(candidate["reported_hop_samples"], 128)
        self.assertEqual(candidate["reported_unit_variants"], [128, 256, 512])
        self.assertIsNone(candidate["reported_content_delay_samples"])
        self.assertIsNone(candidate["reported_parameter_count"])
        self.assertTrue(candidate["io_geometry_documented"])
        self.assertFalse(candidate["model_delay_documented"])
        self.assertFalse(candidate["state_shapes_documented"])
        self.assertFalse(candidate["source_present"])
        self.assertFalse(candidate["weights_present"])
        self.assertFalse(candidate["runtime_present"])
        self.assertFalse(candidate["exact_numeric_output_present"])

    def test_all_boundary_and_scope_flags_are_false(self):
        self.assertTrue(all(value is False
                            for value in self.report["boundary"].values()))
        scope = self.report["scope"]
        self.assertTrue(scope["synthetic_only"])
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key not in {"synthetic_only", "task_local_only"}:
                self.assertIs(value, False, key)

    def test_no_result_is_promoted(self):
        self.assertTrue(self.report["adverse_all_rejected"])
        for case in self.report["adverse_rejections"]:
            self.assertEqual(case["status"], "rejected")
            self.assertTrue(case["state_unchanged"])
        for section in ("echo_attenuation", "near_end_preservation",
                        "overlap_double_talk", "no_reference_comparison",
                        "alignment", "nonfinite", "movement_path_change",
                        "final_partial", "streaming", "reset"):
            self.assertIs(self.report[section]["qualifies"], False, section)
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])

    def test_six_exact_blockers(self):
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        identifiers = {row["id"] for row in blockers}
        self.assertIn("pinned_dtln_aec_source_weights_runtime_absent",
                      identifiers)
        self.assertIn("candidate_model_delay_state_and_parity_unverified",
                      identifiers)
        self.assertIn("rights_cleared_paired_cohort_absent", identifiers)

    def test_generic_dtln_weights_are_rejected_as_candidate(self):
        external = self.report["external_artifacts"]
        self.assertFalse(external["generic_dtln_is_candidate"])
        self.assertTrue(external["present"]["generic_dtln_checkout"])
        self.assertFalse(external["present"]["weights"])
        self.assertFalse(external["any_present"])
        licensing = self.report["licensing"]
        self.assertTrue(licensing["generic_dtln_mit_not_accepted"])
        self.assertIsNone(licensing["reported_upstream_license"])


class EchoNearTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_echo_only_attenuation(self):
        attenuation = self.report["echo_attenuation"]
        self.assertEqual(len(attenuation["regions"]), 2)
        for region in attenuation["regions"]:
            self.assertIs(region["qualifies"], False)
            self.assertGreater(region["erle_millidb"], 20000)
        self.assertEqual(attenuation["min_erle_millidb"],
                         min(row["erle_millidb"]
                             for row in attenuation["regions"]))

    def test_near_end_preservation(self):
        near = self.report["near_end_preservation"]
        self.assertEqual(len(near["regions"]), 2)
        for region in near["regions"]:
            self.assertIs(region["qualifies"], False)
            self.assertGreater(region["near_reference_snr_millidb"], 12000)
            self.assertLess(abs(region["level_change_millidb"]), 500)
            self.assertLess(region["peak_milli"], 1000)
        self.assertEqual(near["nonfinite_output_count"], 0)

    def test_overlap_double_talk(self):
        overlap = self.report["overlap_double_talk"]
        self.assertIs(overlap["qualifies"], False)
        self.assertGreater(overlap["near_reference_snr_millidb"], 0)
        self.assertLess(overlap["peak_milli"], 1000)

    def test_no_reference_control_is_independent(self):
        control = self.report["no_reference_comparison"]
        self.assertIs(control["qualifies"], False)
        self.assertGreater(control["aec_echo_gain_over_control_millidb"],
                           10000)
        self.assertGreater(control["aec_near_reference_snr_millidb"],
                           control["control_near_reference_snr_millidb"])
        self.assertEqual(control["nonfinite_output_count"], 0)

    def test_delayed_and_missing_render_are_detected(self):
        alignment = self.report["alignment"]
        self.assertIs(alignment["qualifies"], False)
        self.assertTrue(alignment["delayed_render_detected"])
        self.assertTrue(alignment["missing_render_detected"])
        self.assertTrue(alignment["missing_render_hop_rejected"])
        self.assertFalse(alignment["candidate_model_delay_measured"])
        self.assertEqual(alignment["surrogate_framing_delay_samples"], 384)
        self.assertGreater(alignment["aligned_erle_millidb"],
                           alignment["delayed_render_erle_millidb"] + 6000)
        self.assertGreater(alignment["aligned_erle_millidb"],
                           alignment["missing_render_erle_millidb"] + 6000)

    def test_final_partial_hop(self):
        partial = self.report["final_partial"]
        self.assertEqual(partial["valid_count"], 100)
        self.assertEqual(partial["output_samples"], 128)
        self.assertEqual(partial["advanced_samples"], 100)
        self.assertTrue(partial["padding_zero"])
        self.assertTrue(partial["tail_zero"])
        self.assertEqual(partial["nonfinite_output_count"], 0)

    def test_streaming_and_reset(self):
        streaming = self.report["streaming"]
        self.assertTrue(streaming["all_match"])
        self.assertEqual(streaming["accepted_samples"], 8192)
        self.assertEqual(streaming["output_samples"], 8576)
        self.assertEqual(sum(streaming["chunks"]), 8576)
        self.assertFalse(streaming["scheduler_measured"])
        self.assertTrue(self.report["reset"]["matches_fresh"])
        self.assertEqual(self.report["reset"]["epoch"], 2)


class StrictInputTests(unittest.TestCase):
    def test_strict_json_rejects_duplicate_and_nonfinite(self):
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":1,"a":2}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":NaN}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":Infinity}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":')

    def test_config_rejects_wrong_geometry(self):
        config = {"sample_rate_hz": 8000, "channels": 1,
                  "block_samples": 512, "hop_samples": 128,
                  "sample_format": "float32", "clock_ppm": 0,
                  "resampling": "none", "render_delay_samples": 16,
                  "algorithmic_latency_samples": 0}
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.validate_config(config)
        self.assertEqual(caught.exception.code, "unsupported_sample_rate")

    def test_nonfinite_hop_is_rejected_without_state_change(self):
        surrogate = reference.StreamingSurrogate()
        signals = reference.build_fixture()
        surrogate.process_hop(list(signals["mic"][:128]),
                              list(signals["render"][:128]))
        before = surrogate.state_digest
        with self.assertRaises(reference.ReferenceRejection):
            surrogate.process_hop(
                [float("nan")] + list(signals["mic"][129:256]),
                list(signals["render"][128:256]))
        self.assertEqual(before, surrogate.state_digest)

    def test_nonzero_padding_is_rejected(self):
        surrogate = reference.StreamingSurrogate()
        signals = reference.build_fixture()
        mic = list(signals["mic"][:100]) + [1.0] + list(signals["mic"][101:127])
        render = list(signals["render"][:128])
        with self.assertRaises(reference.ReferenceRejection):
            surrogate.process_hop(mic, render, valid_count=100)

    def test_missing_render_is_rejected(self):
        surrogate = reference.StreamingSurrogate()
        signals = reference.build_fixture()
        with self.assertRaises(reference.ReferenceRejection) as caught:
            surrogate.process_hop(list(signals["mic"][:128]), None)
        self.assertEqual(caught.exception.code, "missing_render")

    def test_epoch_zero_and_negative_are_rejected(self):
        surrogate = reference.StreamingSurrogate(epoch=1)
        for epoch in (0, -1):
            with self.assertRaises(reference.ReferenceRejection):
                surrogate.reset(epoch, 0)

    def test_adverse_matrix_is_complete(self):
        cases = reference.adverse_rejections()
        self.assertEqual(len(cases), 57)
        self.assertTrue(all(case["status"] == "rejected" for case in cases))
        self.assertTrue(all(case["state_unchanged"] for case in cases))
        identifiers = {case["case_id"] for case in cases}
        self.assertIn("config_stereo", identifiers)
        self.assertIn("hop_nonfinite_render", identifiers)
        self.assertIn("hop_missing_render", identifiers)
        self.assertIn("caller_manifest_bad_stage1_hash", identifiers)
        self.assertIn("caller_manifest_unsupported_variant", identifiers)

    def test_fixture_validation_rejects_bad_specs(self):
        spec = reference.fixture_spec()
        spec["length_samples"] = 8191
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)
        spec = reference.fixture_spec()
        spec["echo_taps_before"] = [[4, 1], [0, 1]]
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)
        spec = reference.fixture_spec()
        spec["render_delay_samples"] = 0
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)

    def test_caller_manifest_is_identity_only(self):
        manifest = {
            "block_samples": 512,
            "channels": 1,
            "declared_content_delay_samples": 0,
            "hop_samples": 128,
            "input_format": "float32",
            "runtime": "tflite_runtime",
            "runtime_version": "2.14.0",
            "sample_rate_hz": 16000,
            "source_commit": "0" * 40,
            "source_sha256": "1" * 64,
            "stage1_bytes": 1000,
            "stage1_path":
                "/caller-assets/dtln-aec/dtln_aec_128_1.tflite",
            "stage1_sha256": "2" * 64,
            "stage2_bytes": 2000,
            "stage2_path":
                "/caller-assets/dtln-aec/dtln_aec_128_2.tflite",
            "stage2_sha256": "3" * 64,
            "variant": "dtln_aec_128",
        }
        result = reference.validate_caller_manifest(manifest)
        self.assertEqual(result, {"validated": True, "loaded": False,
                                  "executed": False, "imported": False})
        gate = reference.gate_caller_assets(manifest)
        self.assertEqual(gate["status"], "blocked_asset_absent")
        self.assertFalse(gate["loaded"])
        self.assertFalse(gate["executed"])

    def test_three_variants_are_declared(self):
        caller = reference.build_report()["caller_asset"]
        self.assertEqual(caller["variants"],
                         ["dtln_aec_128", "dtln_aec_256", "dtln_aec_512"])
        self.assertEqual(caller["variant_unit_counts"], [128, 256, 512])
        self.assertEqual(caller["stage_files_per_variant"], 2)
        self.assertEqual(caller["probe_gate"]["status"],
                         "blocked_asset_absent")

    def test_canonical_json_is_stable(self):
        value = {"b": [1, 2], "a": {"z": "x"}}
        text = reference.canonical_text(value)
        self.assertEqual(text, '{"a":{"z":"x"},"b":[1,2]}')
        self.assertEqual(reference.object_digest(value),
                         reference.sha256_bytes(text.encode("utf-8")))


class DeterminismTests(unittest.TestCase):
    def test_three_builds_are_byte_identical(self):
        texts = [reference.canonical_report(reference.build_report())[0]
                 for _ in range(3)]
        self.assertEqual(len(set(texts)), 1)
        self.assertEqual(reference.sha256_bytes(texts[0].encode("utf-8")),
                         reference.sha256_bytes(texts[1].encode("utf-8")))

    def test_stable_board_identity(self):
        row = reference.board_row()
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         reference.BOARD_ROW_STABLE_SHA256)

    def test_contract_matches_report(self):
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        contract = reference.build_contract(report, digest)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["release_gates"], report["release_gates"])
        self.assertEqual(contract["exact_blockers"], report["exact_blockers"])
        self.assertEqual(contract["source_pins"], report["source_pins"])
        self.assertEqual(contract["boundary_pins"], report["boundary_pins"])
        self.assertIn(reference.TASK_PREFIX + "reference.py",
                      contract["artifact_pins"])


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
                      "swarm/SDK-DTLN-AEC-128-256-512-correction")
            (repo / "SCOPE_PROBE.md").write_text("probe\n", encoding="utf-8")
            sibling = repo / "docs/task-evidence/sibling-alpha/probe.md"
            sibling.write_text("probe\n", encoding="utf-8")
            self._git(repo, "add", "-A")
            self._git(repo, "commit", "-qm", "out of scope edit")

            base = reference.scope_base(repo)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, [
                "SCOPE_PROBE.md",
                "docs/task-evidence/sibling-alpha/probe.md",
            ])
            self.assertEqual(reference.scope_violations(paths), paths)

    def test_missing_base_ref_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "branch", "-m", "detached-work")
            self.assertIsNone(reference.scope_base(repo))


if __name__ == "__main__":
    unittest.main()
