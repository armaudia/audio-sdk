# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance suite for the SDK-DUAL-PATH-ECHO-NET package.

The suite is offline, stdlib-only and read-only. It exercises strict JSON,
family identity resolution and substitution rejection, the frozen synthetic
room arithmetic, caller-asset admission and the exact adverse rejection matrix.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402


class DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_disposition_is_defer_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
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
        items = profile["required_items"]
        self.assertEqual(len(items), 14)
        statuses = {row["status"] for row in items.values()}
        self.assertTrue(statuses.issubset({"synthetic_only", "blocked"}))
        blocked = sorted(name for name, row in items.items()
                         if row["status"] == "blocked")
        self.assertEqual(self.report["profile_blockers"], blocked)
        self.assertIn("echo_attenuation", blocked)
        self.assertIn("rights_cleared_room_qualification", blocked)
        self.assertIn("device_timing_resources", blocked)

    def test_no_section_is_promoted(self):
        self.assertTrue(self.report["adverse_all_rejected"])
        self.assertIs(self.report["room_harness"]["qualifies"], False)
        for case in self.report["room_harness"]["cases"]:
            self.assertIs(case["qualifies"], False)
        for section in ("baseline", "listening", "runtime_timing",
                        "state_and_memory", "nonfinite"):
            self.assertIs(self.report[section]["qualifies"], False, section)
        self.assertFalse(
            self.report["qualification"]["missing_result_promoted"])
        self.assertFalse(self.report["admission_control"]["qualifies"])
        self.assertTrue(self.report["admission_control"]["admitted"])

    def test_all_boundary_and_scope_flags_are_false(self):
        self.assertTrue(all(value is False
                            for value in self.report["boundary"].values()))
        scope = self.report["scope"]
        self.assertTrue(scope["synthetic_only"])
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key not in {"synthetic_only", "task_local_only"}:
                self.assertIs(value, False, key)

    def test_six_open_blockers(self):
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        self.assertEqual([row["id"] for row in blockers],
                         [f"BLK-{index:02d}" for index in range(1, 7)])
        self.assertTrue(all(row["status"] == "open" for row in blockers))
        self.assertTrue(all(row["qualifies"] is False for row in blockers))

    def test_required_artifacts_are_present_or_blocked(self):
        artifacts = self.report["required_artifacts"]
        self.assertEqual([row["id"] for row in artifacts],
                         [f"ART-{index:02d}" for index in range(1, 8)])
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        self.assertFalse(artifacts[0]["blocked"])
        for row in artifacts[1:]:
            self.assertFalse(row["present"], row["id"])
            self.assertTrue(row["blocked"], row["id"])

    def test_format_geometry_is_the_v0_contract_only(self):
        fmt = self.report["format"]
        self.assertEqual(fmt["sdk_v0_sample_rate_hz"], 16000)
        self.assertEqual(fmt["sdk_v0_channels"], 1)
        self.assertEqual(fmt["sdk_v0_frame_samples"], 160)
        self.assertEqual(fmt["sdk_v0_sample_format"], "float32")
        for key in ("candidate_reported_sample_rate_hz",
                    "candidate_reported_hop_samples",
                    "candidate_reported_channels",
                    "candidate_reported_lookahead_samples"):
            self.assertIsNone(fmt[key])
        self.assertFalse(fmt["candidate_geometry_documented"])


class IdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_family_identity_is_unresolved(self):
        identity = self.report["candidate_identity"]
        self.assertFalse(identity["identity_resolved"])
        self.assertEqual(identity["status"], "family_unresolved")
        self.assertEqual(identity["exact_canonical_match_count"], 0)
        for key in ("canonical_citation", "canonical_doi",
                    "canonical_arxiv_id", "canonical_repository",
                    "canonical_checkpoint_id", "canonical_paper_title"):
            self.assertIsNone(identity[key])
        self.assertEqual(identity["recorded_finding"],
                         reference.RECORDED_FINDING)

    def test_every_near_name_and_related_paper_is_rejected(self):
        identity = self.report["candidate_identity"]
        self.assertEqual(identity["substitution_probes_rejected"],
                         identity["substitution_probes_total"])
        self.assertTrue(identity["all_substitutions_rejected"])
        for row in identity["substitution_probes"]:
            self.assertEqual(row["observed_code"], row["expected_code"])
            self.assertFalse(row["substitution_accepted"])

    def test_exact_recorded_label_alone_is_insufficient(self):
        with self.assertRaises(reference.ReferenceRejection) as context:
            reference.resolve_candidate_identity("Dual-Path Echo Net")
        self.assertEqual(
            context.exception.code,
            "identity_family_unresolved_no_exact_model")

    def test_near_names_are_not_merged(self):
        for probe in ("dual-path echo net", "Dual Path Echo Net",
                      "Dual-Path-Echo-Net", "DUAL-PATH ECHO NET",
                      "Dual-Path EchoNet", "Dual-Path Echo Net (DPCTNet)"):
            with self.assertRaises(reference.ReferenceRejection) as context:
                reference.resolve_candidate_identity(probe)
            self.assertEqual(context.exception.code,
                             "identity_name_not_canonical")

    def test_related_papers_are_distinct_not_substitutes(self):
        related = self.report["candidate_identity"]["related_but_distinct"]
        self.assertEqual(len(related), 4)
        self.assertTrue(all(row["substitutable"] is False for row in related))

    def test_no_source_weights_or_runtime_is_present(self):
        status = self.report["reference_status"]
        for key, value in status.items():
            if key in {"license_identity", "pinned_revision"}:
                self.assertIsNone(value)
            elif key == "status":
                self.assertEqual(value, "blocked")
            else:
                self.assertIs(value, False, key)
        external = self.report["external_artifacts"]
        self.assertEqual(external["present_count"], 0)
        self.assertFalse(external["any_present"])
        self.assertFalse(external["recursive_walk"])


class RoomArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.room = cls.report["room_harness"]

    def _case(self, name):
        for case in self.room["cases"]:
            if case["name"] == name:
                return case
        self.fail("missing case: " + name)

    def test_three_frozen_regions(self):
        self.assertEqual([case["name"] for case in self.room["cases"]],
                         ["echo_only", "near_end_only", "double_talk"])

    def test_two_synthetic_echo_paths_are_frozen(self):
        paths = self.room["path_components"]
        self.assertEqual(paths["primary"]["delay_samples"], 240)
        self.assertEqual(paths["primary"]["tap_count"], 3)
        self.assertEqual(paths["secondary"]["delay_samples"], 560)
        self.assertEqual(paths["secondary"]["tap_count"], 2)
        self.assertFalse(paths["primary"]["qualifies"])
        self.assertFalse(paths["secondary"]["qualifies"])
        self.assertEqual(self.room["geometry"]["path_count"], 2)

    def test_echo_only_oracle_erle_is_positive_and_bounded(self):
        case = self._case("echo_only")
        value = case["echo_return_loss_enhancement_millidb"]
        self.assertEqual(value, 20709)
        self.assertIsNone(case["near_end_snr_millidb"])
        self.assertEqual(case["near_end_snr_code"], "no_near_end_reference")

    def test_near_end_only_oracle_snr_is_positive(self):
        case = self._case("near_end_only")
        self.assertIsNone(case["echo_return_loss_enhancement_millidb"])
        self.assertEqual(case["erle_code"], "no_echo_component")
        self.assertEqual(case["near_end_snr_millidb"], 23687)

    def test_double_talk_separates_near_end_and_residual(self):
        case = self._case("double_talk")
        self.assertEqual(case["erle_code"], "erle_only_on_far_end_only")
        self.assertEqual(case["near_end_snr_millidb"], 23868)
        self.assertLess(case["residual_over_capture_millidb"], 0)

    def test_delay_estimation_recovers_both_paths(self):
        delay = self.room["delay_estimation"]
        self.assertEqual(delay["nominal"]["lag_samples"], 240)
        self.assertEqual(delay["nominal"]["error_samples"], 0)
        self.assertEqual(delay["nominal"]["correlation_milli"], 932)
        self.assertEqual(delay["delayed_render"]["lag_samples"], 720)
        self.assertEqual(delay["delayed_render"]["error_samples"], 0)
        self.assertIsNone(delay["missing_render"]["lag_samples"])
        self.assertEqual(delay["missing_render"]["observed_code"],
                         "no_render_reference")
        self.assertEqual(delay["missing_render"]["status"], "not_estimable")

    def test_room_geometry_is_declared_synthetic(self):
        geometry = self.room["geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["frame_samples"], 160)
        self.assertEqual(geometry["primary_path_delay_samples"], 240)
        self.assertEqual(geometry["secondary_path_delay_samples"], 560)
        self.assertEqual(geometry["room_impulse_response"],
                         "synthetic_fixed_not_measured")
        self.assertFalse(geometry["movement_modeled"])
        self.assertFalse(geometry["recorded_audio"])
        self.assertFalse(self.room["audio_generated"])

    def test_nonfinite_and_invalid_inputs_are_rejected(self):
        fixture = reference.build_room_fixture()
        with self.assertRaises(reference.ReferenceRejection) as context:
            reference.prepare_room_case(
                [float("nan")] + fixture["render"][1:], fixture["capture"])
        self.assertEqual(context.exception.code, "nonfinite_input:render")
        with self.assertRaises(reference.ReferenceRejection) as context:
            reference.prepare_room_case(
                fixture["render"], [float("inf")] + fixture["capture"][1:])
        self.assertEqual(context.exception.code, "nonfinite_input:capture")
        self.assertEqual(self.report["nonfinite"]
                         ["rejected_nonfinite_inputs"], 2)


class AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_all_adverse_cases_reject_exactly(self):
        cases = self.report["adverse_rejections"]
        self.assertEqual(len(cases), 64)
        for case in cases:
            self.assertEqual(case["status"], "rejected", case["case_id"])
            self.assertEqual(case["expected_code"], case["observed_code"],
                             case["case_id"])
            self.assertTrue(case["state_unchanged"], case["case_id"])

    def test_schema_control_admits_without_evidence(self):
        control = self.report["admission_control"]
        self.assertTrue(control["admitted"])
        self.assertFalse(control["loaded"])
        self.assertFalse(control["executed"])
        self.assertFalse(control["audio_read"])
        self.assertFalse(control["is_real_cohort"])
        self.assertFalse(control["qualifies"])
        self.assertTrue(control["placeholder_values"])

    def test_manifest_rejects_substitution_and_claims(self):
        with self.assertRaises(reference.ReferenceRejection) as context:
            reference.validate_future_manifest(
                reference._manifest_nested("identity",
                                           canonical_name="DPCTNet"))
        self.assertEqual(context.exception.code,
                         "identity_substitution_attempt")
        with self.assertRaises(reference.ReferenceRejection) as context:
            reference.validate_future_manifest(
                reference._manifest_nested("rights",
                                           claims_qualified=True))
        self.assertEqual(context.exception.code,
                         "claims_qualified_not_allowed")

    def test_manifest_requires_echo_near_and_path_controls(self):
        kinds = set(reference.CONTROL_KINDS)
        self.assertIn("echo_only_case", kinds)
        self.assertIn("near_end_only_case", kinds)
        self.assertIn("double_talk_case", kinds)
        self.assertIn("no_render_reference_case", kinds)
        self.assertIn("delayed_render_case", kinds)
        self.assertIn("path_change_case", kinds)


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self):
        with self.assertRaises(ValueError) as context:
            reference.load_strict_json_text('{"a":1,"a":2}')
        self.assertIn("duplicate_json_key", str(context.exception))

    def test_nonfinite_constants_rejected(self):
        for text in ('{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
            with self.assertRaises(ValueError):
                reference.load_strict_json_text(text)

    def test_malformed_and_non_object_rejected(self):
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('[1,2]')


class PinsAndBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_all_provenance_phrases_present(self):
        provenance = self.report["provenance"]
        self.assertTrue(provenance["all_present"])
        self.assertFalse(provenance["is_qualification"])

    def test_board_identity_is_stable_projection_only(self):
        row = self.report["board_row"]
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertTrue(row["linked_row_identity_only"])
        self.assertFalse(row["mutable_board_fields_gate"])
        self.assertEqual(row["stable_fields"]["id"],
                         "SDK-DUAL-PATH-ECHO-NET")
        self.assertEqual(len(row["linked_rows"]), 5)
        self.assertEqual(sum(1 for path in self.report["source_pins"]
                             if path.endswith("TASKS.json")), 0)

    def test_contract_is_defer_and_self_consistent(self):
        report = self.report
        text, digest = reference.canonical_report(report)
        contract = reference.build_contract(report, digest)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["verification_profile"], "room")
        self.assertEqual(contract["release_gates"], report["release_gates"])
        self.assertEqual(contract["exact_blockers"], report["exact_blockers"])
        self.assertEqual(contract["required_artifacts"],
                         report["required_artifacts"])
        self.assertFalse(contract["admission_schema"]["qualifies"])
        self.assertNotIn(reference.TASK_PREFIX + "contract.json",
                         contract["artifact_pins"])

    def test_three_builds_are_byte_identical(self):
        texts = []
        for _ in range(3):
            text, _ = reference.canonical_report(reference.build_report())
            texts.append(text)
        self.assertEqual(len(set(texts)), 1)


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
                      "swarm/SDK-DUAL-PATH-ECHO-NET-scope")
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
