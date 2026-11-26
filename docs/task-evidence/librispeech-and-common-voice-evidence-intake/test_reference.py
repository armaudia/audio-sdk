# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the LibriSpeech / Common Voice intake gate."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

import reference


def valid_librispeech_request() -> dict:
    return reference._base_request(reference.LIBRISPEECH_CORPUS_ID)


def valid_common_voice_request() -> dict:
    return reference._base_request(reference.COMMON_VOICE_CORPUS_ID)


def board_with(**changes) -> dict:
    row = {
        "id": reference.TASK,
        "title": reference.TITLE,
        "mode": reference.MODE,
        "repository": reference.REPOSITORY,
        "component": reference.COMPONENT,
        "status": "in_progress",
        "owner": "agent-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE",
        "history": ["mutable"],
        "blocked_reason": None,
    }
    row.update(changes)
    return {"tasks": [{"id": "SDK-OTHER", "title": "Other",
                       "mode": "implementation", "status": "done"}, row]}


class StrictJsonTests(unittest.TestCase):
    def test_valid_object(self) -> None:
        self.assertEqual(reference.strict_json_loads('{"a":1}'), {"a": 1})

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.JsonError):
            reference.strict_json_loads('{"a":1,"a":2}')

    def test_nan_and_infinity_rejected(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)

    def test_trailing_and_syntax_rejected(self) -> None:
        for text in ('{"a":1} extra', '{"a":} '):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)


class IntakeValidationTests(unittest.TestCase):
    def test_valid_librispeech_structure_accepted(self) -> None:
        validated = reference.validate_intake(valid_librispeech_request())
        self.assertEqual(validated["corpus_id"],
                         reference.LIBRISPEECH_CORPUS_ID)
        self.assertEqual(validated["archive"]["checksum"],
                         reference.LIBRISPEECH_REPORTED_MD5)
        self.assertTrue(validated["manifest"]["speaker_disjoint"])
        self.assertEqual(validated["model"]["id"], "speexdsp")

    def test_valid_common_voice_structure_accepted(self) -> None:
        validated = reference.validate_intake(valid_common_voice_request())
        self.assertEqual(validated["corpus_id"],
                         reference.COMMON_VOICE_CORPUS_ID)
        self.assertFalse(validated["rights"]["redistribution_approved"])
        self.assertEqual(validated["rights"]["listed_license"], "CC0-1.0")

    def test_unknown_and_missing_fields_rejected(self) -> None:
        request = valid_librispeech_request()
        request["extra"] = True
        with self.assertRaises(reference.ConfigError):
            reference.validate_intake(request)
        request = valid_librispeech_request()
        del request["manifest"]
        with self.assertRaises(reference.ConfigError):
            reference.validate_intake(request)

    def test_corpus_identity_rejected(self) -> None:
        cases = (
            ("corpus_id", "librispeech"),
            ("subset", "dev-clean"),
            ("source_revision", "librispeech-test-clean"),
            ("schema_id", "audio-sdk/other/0.1"),
        )
        for key, value in cases:
            request = valid_librispeech_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=str(key)):
                reference.validate_intake(request)

    def test_archive_rejections(self) -> None:
        cases = (
            {"archive": "test-clean.tar.gz"},
            {"archive.filename": "../test-clean.tar.gz"},
            {"archive.filename": "/tmp/test-clean.tar.gz"},
            {"archive.filename": "dir\\test-clean.tar.gz"},
            {"archive.filename": ".test-clean.tar.gz"},
            {"archive.filename": "dev-clean.tar.gz"},
            {"archive.checksum": "0" * 32},
            {"archive.checksum": "A" * 32},
            {"archive.checksum_kind": "sha256"},
            {"archive.checksum_kind": "crc32"},
            {"archive.checksum": None},
            {"archive.present": False},
            {"archive.byte_count": 0},
            {"archive.byte_count": -1},
            {"archive.byte_count": True},
            {"archive.present": "yes"},
        )
        for change in cases:
            request = reference._variant(valid_librispeech_request(), **change)
            with self.assertRaises(reference.EvidenceError, msg=str(change)):
                reference.validate_intake(request)

    def test_manifest_rejections(self) -> None:
        absent = reference._variant(
            valid_librispeech_request(),
            **{
                "manifest.present": False,
                "manifest.sha256": None,
                "manifest.item_count": None,
                "manifest.duration_seconds": None,
                "manifest.transcript_bound": False,
                "manifest.speaker_disjoint": False,
                "manifest.hashed_speaker_ids_only": False,
                "manifest.split_version": None,
            })
        cases = (
            {"manifest": "manifest.json"},
            {"manifest.extra": True},
            {"manifest.sha256": None},
            {"manifest.sha256": "c" * 63},
            {"manifest.sha256": "C" * 64},
            {"manifest.sha256": "g" * 64},
            {"manifest.item_count": 0},
            {"manifest.item_count": -1},
            {"manifest.item_count": True},
            {"manifest.duration_seconds": float("nan")},
            {"manifest.duration_seconds": float("inf")},
            {"manifest.duration_seconds": float("-inf")},
            {"manifest.duration_seconds": 0.0},
            {"manifest.duration_seconds": -1.0},
            {"manifest.duration_seconds": True},
            {"manifest.duration_seconds": "1.0"},
            {"manifest.transcript_bound": False},
            {"manifest.speaker_disjoint": False},
            {"manifest.hashed_speaker_ids_only": False},
            {"manifest.split_version": "Split-V1"},
            {"manifest.split_version": "split-v1-\u00e9"},
            {"manifest.split_version": "../split"},
        )
        for change in cases:
            request = reference._variant(valid_librispeech_request(), **change)
            with self.assertRaises(reference.EvidenceError, msg=str(change)):
                reference.validate_intake(request)
        for change in (
                {"manifest.sha256": "c" * 64},
                {"manifest.split_version": "split-v1"},
                {"manifest.item_count": 1}):
            request = reference._variant(absent, **change)
            with self.assertRaises(reference.EvidenceError, msg=str(change)):
                reference.validate_intake(request)

    def test_rights_rejections(self) -> None:
        cases = (
            {"rights.listed_license": "CC0-1.0"},
            {"rights.license_text_sha256": None},
            {"rights.license_text_present": False},
            {"rights.license_text_present": False,
             "rights.license_text_sha256": None},
            {"rights.download_terms_reviewed": False},
            {"rights.attribution_recorded": False},
            {"rights.use_approved": False},
            {"rights.license_text_present": 1},
            {"rights.extra": True},
        )
        for change in cases:
            request = reference._variant(valid_librispeech_request(), **change)
            with self.assertRaises(reference.EvidenceError, msg=str(change)):
                reference.validate_intake(request)
        cv_cases = (
            {"rights.redistribution_approved": True},
            {"rights.speaker_identification_forbidden_ack": False},
            {"rights.no_rehosting_ack": False},
            {"rights.listed_license": "CC BY 4.0"},
        )
        for change in cv_cases:
            request = reference._variant(valid_common_voice_request(), **change)
            with self.assertRaises(reference.EvidenceError, msg=str(change)):
                reference.validate_intake(request)

    def test_model_rejections(self) -> None:
        cases = (
            {"model": "speexdsp"},
            {"model.id": "rnnoise"},
            {"model.id": True},
            {"model.extra": True},
            {"model.overlap_status": "probably_clean"},
            {"model.overlap_status": "exact_overlap_excluded"},
            {"model.overlap_audit_sha256": "d" * 64},
            {"model.id": "other_learned",
             "model.overlap_status": "not_applicable_no_training_corpus"},
            {"model.id": "dpdfnet",
             "model.overlap_status": "exact_overlap_excluded"},
            {"model.id": "dpdfnet",
             "model.overlap_audit_sha256": "d" * 64},
            {"model.id": "dpdfnet",
             "model.overlap_status": "exact_overlap_excluded",
             "model.overlap_audit_sha256": "d" * 63},
            {"model.id": "dpdfnet",
             "model.overlap_status": "exact_overlap_excluded",
             "model.overlap_audit_sha256": "D" * 64},
        )
        for change in cases:
            request = reference._variant(valid_librispeech_request(), **change)
            with self.assertRaises(reference.EvidenceError, msg=str(change)):
                reference.validate_intake(request)

    def test_adverse_cases_all_rejected(self) -> None:
        adverse = reference._adverse_intake_cases()
        self.assertTrue(adverse["all_rejected"])
        self.assertEqual(adverse["accepted_count"], 0)
        self.assertGreaterEqual(adverse["case_count"], 60)
        self.assertIsNone(adverse["metrics"])

    def test_invalid_json_cases_all_rejected(self) -> None:
        adverse = reference._json_adverse_cases()
        self.assertTrue(adverse["all_rejected"])
        self.assertEqual(adverse["accepted_count"], 0)

    def test_valid_structure_fails_closed(self) -> None:
        decision = reference.admit(valid_librispeech_request())
        self.assertEqual(decision["status"], "DEFER")
        self.assertFalse(decision["admissible"])
        self.assertFalse(decision["qualifies"])
        self.assertIsNone(decision["metrics"])
        self.assertIsNone(decision["result"])
        self.assertIn("librispeech_archive_and_manifest_absent",
                      decision["blockers"])
        self.assertIn("common_voice_archive_and_manifest_absent",
                      decision["blockers"])
        self.assertIn("frozen_cohort_and_scorer_absent",
                      decision["blockers"])

    def test_common_voice_admission_also_deferred(self) -> None:
        decision = reference.admit(valid_common_voice_request())
        self.assertEqual(decision["status"], "DEFER")
        self.assertFalse(decision["qualifies"])
        self.assertIn("common_voice_archive_and_manifest_absent",
                      decision["blockers"])

    def test_no_admitting_branch_is_recorded(self) -> None:
        self.assertIn("no_admitting_branch", reference.collect_blockers())


class ProbeTests(unittest.TestCase):
    def test_librispeech_absent(self) -> None:
        probe = reference.librispeech_probe()
        self.assertEqual(probe["status"],
                         "blocked_archive_tree_manifest_absent")
        self.assertFalse(probe["present"])
        self.assertFalse(probe["archive_present"])
        self.assertFalse(probe["source_tree_present"])
        self.assertFalse(probe["prepared_manifest_present"])
        for key in ("archive_md5", "archive_sha256", "archive_byte_count",
                    "manifest_sha256", "item_count", "duration_seconds"):
            self.assertIsNone(probe["local"][key])
        self.assertEqual(probe["reported"]["reported_archive_md5"],
                         reference.LIBRISPEECH_REPORTED_MD5)

    def test_common_voice_absent(self) -> None:
        probe = reference.common_voice_probe()
        self.assertEqual(probe["status"],
                         "blocked_archive_metadata_manifest_absent")
        self.assertFalse(probe["present"])
        self.assertFalse(probe["archive_present"])
        self.assertFalse(probe["source_metadata_present"])
        self.assertFalse(probe["prepared_manifest_present"])
        for key in ("archive_sha256", "archive_byte_count", "manifest_sha256",
                    "item_count", "duration_seconds"):
            self.assertIsNone(probe["local"][key])
        reported = probe["reported"]
        self.assertEqual(reported["dataset_id"],
                         "cmu5nqn1h00vwmi07b4dbk085")
        self.assertEqual(reported["release"], "sps-corpus-5.0-2026-09-11")
        self.assertEqual(reported["reported_clips"], 5898)
        self.assertEqual(reported["reported_speakers"], 642)
        self.assertIsNone(reported["native_sample_rate_hz"])

    def test_presence_probe_is_bounded_and_absent(self) -> None:
        probe = reference.presence_probe()
        self.assertTrue(probe["bounded"])
        self.assertFalse(probe["present"])
        self.assertGreater(probe["probed_path_count"], 10)
        self.assertFalse(probe["librispeech"]["present"])
        self.assertFalse(probe["common_voice"]["present"])

    def test_rights_blocked_and_dataset_scoped(self) -> None:
        rights = reference.rights_probe()
        self.assertEqual(rights["status"], "blocked_rights_unrecorded")
        self.assertFalse(rights["use_approved"])
        self.assertFalse(rights["listening_approved"])
        self.assertFalse(rights["librispeech"]["privacy_or_publicity_grant"])
        self.assertFalse(
            rights["common_voice"]["download_terms_reviewed"])
        self.assertFalse(
            rights["common_voice"]["enhancement_use_confirmed"])
        self.assertEqual(rights["librispeech"]["reported_license"],
                         "CC BY 4.0")
        self.assertEqual(rights["common_voice"]["reported_license"],
                         "CC0-1.0")

    def test_overlap_matrix_keeps_models_and_datasets_distinct(self) -> None:
        matrix = reference.overlap_matrix()
        self.assertEqual(len(matrix), 6)
        keys = {(row["dataset"], row["model"]) for row in matrix}
        for dataset in (reference.LIBRISPEECH_CORPUS_ID,
                        reference.COMMON_VOICE_CORPUS_ID):
            for model in reference.MODEL_IDS:
                self.assertIn((dataset, model), keys)
        dpdfnet = [row for row in matrix
                   if row["dataset"] == reference.LIBRISPEECH_CORPUS_ID and
                   row["model"] == "dpdfnet"][0]
        self.assertIn("LibriVox", dpdfnet["reason"])
        self.assertIn("MLS", dpdfnet["reason"])
        self.assertFalse(dpdfnet["exact_audit_present"])
        speex = [row for row in matrix
                 if row["model"] == "speexdsp"]
        for row in speex:
            self.assertEqual(row["status"],
                             "not_applicable_no_training_corpus")

    def test_required_artifacts_all_absent(self) -> None:
        self.assertEqual(len(reference.REQUIRED_ARTIFACTS), 8)
        self.assertEqual([row["id"] for row in reference.REQUIRED_ARTIFACTS],
                         ["A" + str(number) for number in range(1, 9)])
        for row in reference.REQUIRED_ARTIFACTS:
            self.assertEqual(row["status"], "absent")
            self.assertIsNone(row["sha256"])
            self.assertIsNone(row["byte_count"])
            self.assertFalse(row["rights_reviewed"])

    def test_eight_gates_are_blocked(self) -> None:
        self.assertEqual(len(reference.GATES), 8)
        self.assertEqual([gate["id"] for gate in reference.GATES],
                         ["RG-0" + str(number) for number in range(1, 9)])
        for gate in reference.GATES:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reason"])
            self.assertTrue(gate["reopen"])

    def test_control_is_structural_only(self) -> None:
        control = reference.control_probe()
        self.assertTrue(control["byte_identical"])
        self.assertTrue(control["datasets_separate"])
        self.assertFalse(control["candidate_processing"])
        self.assertFalse(control["real_corpus_read"])
        self.assertFalse(control["ledger"]["pooled"])
        self.assertEqual(control["ledger"]["datasets"][0]["items_verified"], 0)

    def test_evidence_profile_is_blocked_or_declared(self) -> None:
        profile = reference.acceptance_profile()
        self.assertEqual(profile["profile"], "evidence")
        for name, item in profile["required_items"].items():
            self.assertIn(item["status"],
                          {"blocked", "recorded", "declared_only"})
        self.assertEqual(
            profile["required_items"][
                "representative_valid_result_validated"]["status"], "blocked")
        self.assertEqual(
            profile["required_items"][
                "invalid_or_missing_case_validated"]["status"], "recorded")

    def test_evidence_kinds_are_separated(self) -> None:
        separation = reference.evidence_separation()
        self.assertFalse(separation["pooling"])
        self.assertEqual(separation["paired"]["status"], "absent")
        self.assertEqual(separation["unpaired"]["status"], "absent")
        self.assertEqual(separation["synthetic"]["status"],
                         "declared_only_not_run")
        self.assertFalse(separation["human"]["listening"])
        self.assertEqual(separation["source_reported"]["status"],
                         "retained_not_reproduced")

    def test_board_projection_uses_stable_identity_only(self) -> None:
        links, digest = reference._board_projection(board_with())
        expected = {
            "task_id": reference.TASK,
            "title": reference.TITLE,
            "mode": reference.MODE,
            "repository": reference.REPOSITORY,
            "component": reference.COMPONENT,
        }
        self.assertEqual(links, [expected])
        self.assertEqual(digest,
                         reference.sha256_bytes(
                             reference.canonical_bytes([expected])))
        changed = board_with(status="done", owner="other", history=[])
        self.assertEqual(reference._board_projection(changed)[0], [expected])

    def test_board_identity_change_rejected(self) -> None:
        for change in ({"title": "Different"},
                       {"mode": "implementation"},
                       {"component": "other"},
                       {"repository": "audio-bench"},
                       {"id": "SDK-OTHER"}):
            with self.assertRaises(reference.ConfigError, msg=str(change)):
                reference._board_projection(board_with(**change))
        with self.assertRaises(reference.ConfigError):
            reference._board_projection({"tasks": []})


class ReportTests(unittest.TestCase):
    def test_report_is_deterministic_and_canonical(self) -> None:
        first = reference.report_bytes()
        second = reference.report_bytes()
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertFalse(first.endswith(b"\n\n"))
        report = reference.strict_json_loads(first.decode("utf-8"))
        self.assertEqual(reference.canonical_bytes(report) + b"\n", first)

    def test_blocker_semantics(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["schema_id"], reference.SCHEMA_ID)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["incomplete"])
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["comparison_status"],
                         reference.COMPARISON_STATUS)
        qualification = report["qualification"]
        self.assertFalse(qualification["all_required_results_present"])
        self.assertFalse(qualification["dataset_qualified"])
        self.assertFalse(qualification["rights_approved"])
        self.assertFalse(qualification["representative_valid_result"])
        self.assertTrue(qualification["invalid_or_missing_control"])
        self.assertEqual(qualification["status"], "not_qualified")

    def test_datasets_are_distinct_and_absent(self) -> None:
        report = reference.build_report()
        datasets = report["datasets"]
        self.assertEqual(set(datasets), set(reference.CORPORA))
        libri = datasets[reference.LIBRISPEECH_CORPUS_ID]
        common = datasets[reference.COMMON_VOICE_CORPUS_ID]
        self.assertFalse(libri["archive_present"])
        self.assertFalse(libri["prepared_manifest_present"])
        self.assertFalse(common["archive_present"])
        self.assertFalse(common["prepared_manifest_present"])
        self.assertFalse(libri["local"]["speaker_split_verified"])
        self.assertFalse(common["local"]["speaker_split_verified"])
        self.assertIsNone(libri["local"]["archive_sha256"])
        self.assertIsNone(common["local"]["archive_sha256"])
        self.assertNotEqual(libri["reported"]["source"],
                            common["reported"]["source"])

    def test_eight_gates_and_admission(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["remaining_gates"],
                         ["RG-0" + str(number) for number in range(1, 9)])
        self.assertEqual(report["gates"], report["remaining_gates"])
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in report["release_gates"]))
        controls = report["admission_controls"]
        self.assertFalse(
            controls["admission_policy"]["admitting_branch_exists"])
        self.assertTrue(controls["admission_policy"]["always_defer"])
        self.assertEqual(controls["recorded_declaration_live"]["decision"],
                         "DEFER")
        self.assertFalse(controls["representative_valid_result"]["present"])

    def test_no_fabricated_identity(self) -> None:
        report = reference.build_report()
        for dataset in report["datasets"].values():
            for key in ("archive_sha256", "archive_byte_count",
                        "manifest_sha256", "item_count", "duration_seconds",
                        "rights_record"):
                self.assertIsNone(dataset["local"][key])
        blocker = report["blocker"]
        self.assertIsNone(blocker["librispeech"]["archive_md5"])
        self.assertIsNone(blocker["librispeech"]["archive_sha256"])
        self.assertIsNone(blocker["common_voice"]["archive_sha256"])
        self.assertTrue(blocker["no_fabricated_identity"])
        self.assertEqual(blocker["status"], reference.COMPARISON_STATUS)

    def test_adverse_and_json_rejections_are_reported(self) -> None:
        report = reference.build_report()
        adverse = report["adverse"]
        self.assertTrue(adverse["invalid_declarations"]["all_rejected"])
        self.assertEqual(
            adverse["invalid_declarations"]["accepted_count"], 0)
        self.assertTrue(
            adverse["invalid_json_numeric_fields"]["all_rejected"])
        self.assertIsNone(adverse["missing_result"]["metrics"])
        self.assertFalse(adverse["missing_result"]["qualifies"])

    def test_local_checks_all_true(self) -> None:
        report = reference.build_report()
        checks = report["local_harness_checks"]
        self.assertGreaterEqual(len(checks), 15)
        self.assertTrue(all(value is True for value in checks.values()))
        self.assertTrue(report["no_missing_result_qualifies"])
        self.assertTrue(report["no_result_qualifies"])

    def test_boundary_is_closed(self) -> None:
        report = reference.build_report()
        boundary = report["boundary"]
        for key in ("installed_v0_behavior_change", "public_api_abi_change",
                    "provider_registration", "descriptor_registry_change",
                    "enabled_by_default", "default_selected",
                    "shared_build_or_ci_change", "board_or_handoff_changed",
                    "network_used", "audio_loaded", "audio_executed",
                    "asset_bundled", "weights_vendored", "sdk_data_dir_added",
                    "listening_run", "device_timing_claim", "benchmark_claim",
                    "release_claim", "adapter_added", "processor_exposure",
                    "real_corpus_read"):
            self.assertFalse(boundary[key], msg=key)
        self.assertEqual(boundary["format"], {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "sample_format": "float32",
        })

    def test_external_boundary_is_closed(self) -> None:
        report = reference.build_report()
        external = report["external_boundary"]
        self.assertTrue(external["documented"])
        self.assertFalse(external["librispeech_source_present"])
        self.assertFalse(external["librispeech_manifest_present"])
        self.assertFalse(external["common_voice_source_present"])
        self.assertFalse(external["common_voice_manifest_present"])
        self.assertFalse(external["license_text_present"])
        self.assertFalse(external["rights_approved"])
        self.assertFalse(external["scorer_present"])
        self.assertFalse(external["cohort_present"])
        self.assertFalse(external["representative_result_present"])
        self.assertFalse(external["adapter_implemented"])
        self.assertFalse(external["automatic_discovery"])
        self.assertEqual(external["fallback"], "none")

    def test_board_projection_reported_without_full_hash(self) -> None:
        report = reference.build_report()
        links, digest = reference.board_link_projection()
        self.assertEqual(report["board_links"], links)
        self.assertEqual(report["board_link_projection_sha256"], digest)
        self.assertFalse(report["board_full_file_hashed"])
        self.assertNotIn("status", links[0])
        self.assertIn("status", report["board_mutable_fields_excluded"])

    def test_profile_and_statements(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["profile"]["name"], "evidence")
        self.assertEqual(report["profile_mapping"]
                         ["representative_valid_result"],
                         "blocked_no_valid_result")
        statements = " ".join(report["source_evidence_statements"]).lower()
        for phrase in ("librispeech", "common voice", "cc by 4.0",
                       "cc0-1.0", "librivox", "evidence profile"):
            self.assertIn(phrase, statements)
        self.assertTrue(report["non_claims"])
        self.assertTrue(report["invariants"])


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

    def test_sibling_additions_on_main_pass_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            historical = self._git(repo, "rev-parse", "HEAD")
            self._add_siblings(repo)
            head = self._git(repo, "rev-parse", "HEAD")

            # This package is already merged on main and later main merges
            # added unrelated siblings; the merge-base is HEAD, so nothing in
            # this branch is out of scope.
            base = reference.scope_base(repo)
            self.assertEqual(base, head)
            self.assertEqual(reference.scope_changed_paths(repo, base), [])
            self.assertEqual(reference.scope_violations([]), [])

            # A fixed pre-merge base would have reported the siblings; the
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
                      "swarm/SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE"
                      "-correction")
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
