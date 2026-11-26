# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local NARA-WPE readiness package."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import unittest

import reference

HERE = Path(__file__).resolve().parent


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class JsonTests(unittest.TestCase):
    def test_canonical_rejects_nonfinite(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"value": math.nan})

    def test_strict_rejects_duplicate_key(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_rejects_infinity(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a":Infinity}')

    def test_strict_requires_object(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_loads("[1,2]")

    def test_strict_rejects_trailing_data(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a":1} trailing')

    def test_signal_digest_is_deterministic(self) -> None:
        signal = [0.0, 0.5, -0.5]
        self.assertEqual(reference.signal_digest(signal),
                         reference.signal_digest(list(signal)))
        self.assertEqual(len(reference.signal_digest(signal)), 64)


class IdentityTests(unittest.TestCase):
    def test_stable_board_digest(self) -> None:
        self.assertEqual(reference.board_row_digest(),
                         reference.BOARD_ROW_STABLE_SHA256)
        raw = json.dumps(reference.BOARD_ROW_STABLE_FIELDS, sort_keys=True,
                         separators=(",", ":")).encode()
        self.assertEqual(_sha(raw), reference.BOARD_ROW_STABLE_SHA256)

    def test_stable_fields_are_exactly_the_linked_row(self) -> None:
        self.assertEqual(reference.BOARD_ROW_STABLE_FIELDS, {
            "component": "nara-wpe-reference-tools",
            "depends_on": [
                "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
            "id": "SDK-NARA-WPE-REFERENCE-TOOLS",
            "mode": "feasibility",
            "repository": "audio-sdk",
            "title": "NARA-WPE reference tools",
        })

    def test_mutable_fields_are_excluded(self) -> None:
        for field in reference.MUTABLE_TASK_FIELDS:
            self.assertNotIn(field, reference.BOARD_ROW_STABLE_FIELDS)
        self.assertFalse("TASKS.json" in reference.BOARD_ROW_STABLE_FIELDS)

    def test_claim_identity(self) -> None:
        self.assertEqual(reference.BOARD_ROW_CLAIM["base_commit"],
                         reference.BASE_COMMIT)
        self.assertEqual(reference.BOARD_ROW_CLAIM["branch"],
                         reference.BRANCH)
        self.assertIsNone(reference.UPSTREAM_REVISION)
        self.assertIsNone(reference.UPSTREAM_LICENSE)
        self.assertFalse(reference.SOURCE_REVISION_PIN_AVAILABLE)


class ContractTests(unittest.TestCase):
    def test_contract_validates(self) -> None:
        contract = reference.build_contract()
        reference.validate_contract(contract)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "proposal_only_incomplete")
        self.assertEqual(contract["evidence_status"], "incomplete")
        self.assertEqual(contract["verification_profile"], "Room")
        self.assertEqual(contract["qualification"]["status"],
                         "not_qualified")
        self.assertFalse(contract["qualification"]["candidate_qualified"])

    def test_eight_gates_and_blockers_are_blocked(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(len(contract["gates"]), 8)
        self.assertEqual(len(contract["exact_blockers"]), 8)
        self.assertEqual(tuple(row["id"] for row in contract["gates"]),
                         reference.GATE_IDS)
        self.assertEqual(tuple(row["id"] for row in contract["exact_blockers"]),
                         reference.BLOCKER_IDS)
        self.assertTrue(all(row["status"] == "blocked"
                            for row in contract["gates"]))
        self.assertTrue(all(row["qualifies"] is False
                            for row in contract["exact_blockers"]))

    def test_scope_flags_are_false(self) -> None:
        scope = reference.build_contract()["exact_scope"]
        for key in reference.SCOPE_FALSE_FLAGS:
            self.assertIs(scope[key], False, key)
        self.assertEqual(scope["write_scope"], reference.TASK_PREFIX + " only")
        self.assertIs(scope["task_local_only"], True)

    def test_absence_audit_is_absent(self) -> None:
        audit = reference.build_contract()["asset_audit"]
        self.assertEqual(audit["probe_count"],
                         len(reference.ABSENCE_PROBES))
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertFalse(any(row["present"] for row in audit["probes"]))

    def test_contract_bytes_are_canonical(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(reference.canonical_contract_bytes(),
                         reference.canonical_bytes(contract))


class ReportTests(unittest.TestCase):
    def test_report_is_canonical_and_matches_sidecar(self) -> None:
        payload = reference.canonical_report_bytes()
        report = reference.strict_loads(payload.decode("utf-8"))
        reference.validate_report(report)
        self.assertEqual(payload, reference.canonical_bytes(report))
        digest = _sha(payload)
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")

    def test_report_contract_digest(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(reference.build_contract()))

    def test_report_pins_match_constants(self) -> None:
        report = reference.build_report()
        self.assertEqual(
            report["source_pins"],
            {path: {"sha256": digest, "verified": True}
             for path, digest in reference.SOURCE_PINS.items()})
        self.assertEqual(
            report["boundary_pins"],
            {path: {"sha256": digest, "verified": True}
             for path, digest in reference.BOUNDARY_PINS.items()})

    def test_report_is_not_qualified(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["qualification"]["status"],
                         "not_qualified")
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)
        self.assertTrue(report["qualification"]["all_release_gates_blocked"])
        self.assertFalse(report["qualification"]["release_results_present"])
        self.assertFalse(report["scope"]["provider_registered"])
        self.assertFalse(report["scope"]["default_selected"])

    def test_all_profile_checks_pass(self) -> None:
        scoring = reference.build_report()["profile_scoring"]
        self.assertTrue(scoring["passed"])
        self.assertEqual(scoring["failed_checks"], [])
        self.assertEqual(
            tuple(row["id"] for row in scoring["checks"]),
            ("source_absence_audited", "upstream_revision_not_fabricated",
             "upstream_license_not_fabricated",
             "upstream_geometry_not_asserted", "project_geometry_pinned",
             "matched_config_required",
             "caller_schema_accepts_structural_control",
             "caller_manifest_rejections_fail_closed",
             "pinned_admission_blocked", "identity_control_bit_exact",
             "frame_grid_half_open", "early_window_50ms_exact",
             "declared_latency_80ms_exact", "final_partial_37",
             "nonfinite_rejected", "config_mismatch_rejected",
             "no_real_audio", "no_listening_or_device_timing",
             "no_benchmark_or_release_claim", "no_downloads",
             "no_provider_or_default_change", "sibling_evidence_not_pooled",
             "room_profile_applied", "all_eight_gates_blocked",
             "candidate_not_qualified"))

    def test_matched_evidence_not_pooled(self) -> None:
        matched = reference.build_report()["matched_evidence"]
        self.assertFalse(matched["upstream_nara_wpe_outputs_present"])
        self.assertEqual(matched["matched_comparison_status"], "blocked")
        self.assertFalse(matched["pooling_allowed"])


class GeometryTests(unittest.TestCase):
    def test_control_values_are_exact(self) -> None:
        control = reference.geometry_control()
        self.assertEqual(control["source_samples"], 64037)
        self.assertEqual(control["frame_count"], 501)
        self.assertEqual(control["final_frame_source_valid"], 37)
        self.assertEqual(control["early_target_window_samples"], 800)
        self.assertEqual(control["stft_lookahead_samples"], 256)
        self.assertEqual(control["predictor_delay_samples"], 1024)
        self.assertEqual(control["declared_algorithmic_latency_samples"], 1280)
        self.assertEqual(control["declared_algorithmic_latency_ms"], 80)
        self.assertEqual(control["config_rejections"], 20)
        self.assertEqual(control["nonfinite_rejections"], 3)
        self.assertTrue(control["contiguous_half_open_intervals"])
        self.assertTrue(control["identity_bit_exact"])
        self.assertTrue(control["partial_tail_matches_prefix"])
        self.assertFalse(control["not_nara_wpe"] is False)
        self.assertFalse(control["dereverberation_performed"])
        self.assertFalse(control["qualifies"])

    def test_frame_grid_is_half_open_and_contiguous(self) -> None:
        intervals = reference.frame_intervals(64037, 128)
        self.assertEqual(len(intervals), 501)
        self.assertEqual(intervals[0], (0, 128))
        self.assertEqual(intervals[-1], (64000, 64037))
        for index, (start, end) in enumerate(intervals):
            self.assertEqual(start, index * 128)
            self.assertGreater(end, start)
        self.assertEqual(sum(end - start for start, end in intervals), 64037)

    def test_identity_is_bit_exact(self) -> None:
        signal = reference.control_signal(1000)
        self.assertEqual(reference.identity_control(signal), signal)

    def test_nonfinite_is_rejected(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                reference.identity_control([value])

    def test_matched_geometry_accepts_exact_project_values(self) -> None:
        reference.validate_matched_geometry(
            dict(reference.PROJECT_GEOMETRY, stft_window="hann"))

    def test_matched_geometry_rejects_mismatches(self) -> None:
        for key, value in (
            ("sample_rate_hz", 48000), ("channels", 2), ("fft_size", 256),
            ("hop_size", 256), ("taps", 10),
            ("prediction_delay_frames", 3), ("early_window_ms", 100),
            ("stft_window", "kaiser"),
        ):
            bad = dict(reference.PROJECT_GEOMETRY, stft_window="hann")
            bad[key] = value
            with self.assertRaises(ValueError, msg=key):
                reference.validate_matched_geometry(bad)

    def test_geometry_rejects_booleans_and_extra_keys(self) -> None:
        for bad in (
            dict(reference.PROJECT_GEOMETRY, stft_window="hann", taps=True),
            dict(reference.PROJECT_GEOMETRY, stft_window="hann", channels=False),
            dict(reference.PROJECT_GEOMETRY, stft_window="hann", extra=1),
        ):
            with self.assertRaises(ValueError):
                reference.validate_matched_geometry(bad)


class ManifestTests(unittest.TestCase):
    def test_structural_control_is_accepted(self) -> None:
        result = reference.manifest_rejection_examples()
        self.assertEqual(result["accepted"], 1)
        self.assertTrue(result["accepted_is_synthetic_not_evidence"])
        self.assertEqual(result["rejected"], result["rejected_total"])
        self.assertTrue(result["all_rejections_fail_closed"])
        self.assertTrue(result["pinned_admission_blocked"])

    def test_pinned_admission_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = reference._synthetic_manifest(root)
            with self.assertRaises(ValueError) as context:
                reference.local_pinned_admission(manifest)
            self.assertIn("upstream_source_absent", str(context.exception))

    def test_missing_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = reference._synthetic_manifest(root)
            (root / "nara_wpe/parity.json").unlink()
            with self.assertRaises(ValueError):
                reference.validate_caller_manifest(
                    manifest, caller_root=root, require_files=True)

    def test_wrong_digest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = reference._synthetic_manifest(root)
            manifest["package"]["wheel_sha256"] = "a" * 64
            with self.assertRaises(ValueError):
                reference.validate_caller_manifest(
                    manifest, caller_root=root, require_files=True)

    def test_path_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = reference._synthetic_manifest(root)
            manifest["source"]["license_text_path"] = "../license.txt"
            with self.assertRaises(ValueError):
                reference.validate_caller_manifest(
                    manifest, caller_root=root, require_files=True)

    def test_qualification_claim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = reference._synthetic_manifest(root)
            manifest["qualification_claim"] = True
            with self.assertRaises(ValueError):
                reference.validate_caller_manifest(
                    manifest, caller_root=root, require_files=True)

    def test_duplicate_json_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = reference._synthetic_manifest(root)
            text = json.dumps(manifest)
            duplicated = text[:-1] + ', "schema_id": "x"}'
            with self.assertRaises(ValueError):
                reference.strict_loads(duplicated)

    def test_geometry_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = reference._synthetic_manifest(root)
            manifest["geometry"]["fft_size"] = 256
            with self.assertRaises(ValueError):
                reference.validate_caller_manifest(
                    manifest, caller_root=root, require_files=True)


class ReadmeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = (HERE / "README.md").read_text(encoding="utf-8")

    def test_sections_parse_and_verify(self) -> None:
        counts = reference.verify_readme_digests(self.text)
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))

    def test_artifact_table_is_fresh(self) -> None:
        self.assertEqual(reference.update_readme_artifact_table(self.text),
                         self.text)

    def test_tampered_digest_is_rejected(self) -> None:
        tampered = self.text.replace(
            reference.SOURCE_PINS["research/category_registry.json"],
            "0" * 64, 1)
        with self.assertRaises(ValueError):
            reference.verify_readme_digests(tampered)

    def test_stale_artifact_digest_is_rejected(self) -> None:
        stale = self.text.replace(
            reference.sha256_file(HERE / "contract.json"), "0" * 64, 1)
        with self.assertRaises(ValueError):
            reference.verify_readme_digests(stale)

    def test_duplicate_row_is_rejected(self) -> None:
        text = self.text.replace(
            "<!-- digest-table: end -->",
            "| `source:research/category_registry.json` | `" + "0" * 64 +
            "` |\n<!-- digest-table: end -->", 1)
        with self.assertRaises(ValueError):
            reference.parse_readme_digest_tables(text)

    def test_missing_marker_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_readme_digest_tables("# no tables")

    def test_readme_has_spdx_header(self) -> None:
        head = "\n".join(self.text.splitlines()[:4])
        self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes", head)
        self.assertIn("SPDX-License-" "Identifier: Apache-2.0", head)


class PinTests(unittest.TestCase):
    def test_manifest_round_trip(self) -> None:
        data = (HERE / "SOURCES.sha256").read_bytes()
        self.assertEqual(data, reference.sources_bytes())
        pins = reference.parse_pin_lines(data.decode("ascii"))
        self.assertEqual({path for _, path in pins},
                         reference.allowed_pin_keys())

    def test_bad_pins_are_rejected(self) -> None:
        for text in (
            "not-a-pin",
            "0" * 64 + " source:one",
            "0" * 64 + "  other:one",
            "\n".join(["0" * 64 + "  source:one",
                       "0" * 64 + "  source:one"]),
        ):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(text)

    def test_pinned_files_exist(self) -> None:
        for relative in reference.SOURCE_PINS:
            self.assertTrue(reference._resolve_source_path(relative).is_file(),
                            relative)
        for relative in reference.BOUNDARY_PINS:
            self.assertTrue((reference.SDK_ROOT / relative).is_file(),
                            relative)


class LicensingTests(unittest.TestCase):
    def test_expected_files_exist(self) -> None:
        for name in reference.EXPECTED_DIR_FILES:
            self.assertTrue((HERE / name).is_file(), name)

    def test_no_forbidden_artifacts(self) -> None:
        forbidden = {".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".h5",
                     ".mat", ".model", ".mp3", ".npy", ".npz", ".o", ".ogg",
                     ".onnx", ".pkl", ".pt", ".pth", ".pyc", ".so", ".wasm",
                     ".wav", ".weights"}
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertFalse(path.name.startswith("LICENSE"), path.name)
            self.assertNotIn(path.name,
                             {"CMakeLists.txt", "provider.json",
                              "adapter.json"})

    def test_python_spdx_headers(self) -> None:
        for path in HERE.glob("*.py"):
            head = "\n".join(
                path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn("SPDX-License-" "Identifier: Apache-2.0", head)
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          head)

    def test_license_sidecars(self) -> None:
        for name in ("SOURCES.sha256.license", "contract.json.license",
                     "report.json.license", "report.json.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn("SPDX-License-" "Identifier: Apache-2.0", text)
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          text)


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
        for name in ("sibling-alpha", "sibling-beta"):
            sibling = repo / "docs/task-evidence" / name
            sibling.mkdir(parents=True)
            (sibling / "report.json").write_text("{}\n", encoding="utf-8")
            (sibling / "verify.py").write_text("# sibling\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "unrelated sibling packages")

    def test_sibling_additions_after_base_pass_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            historical = self._git(repo, "rev-parse", "HEAD")
            self._add_siblings(repo)
            head = self._git(repo, "rev-parse", "HEAD")

            base = reference.scope_base(repo)
            self.assertEqual(base, head)
            self.assertEqual(reference.scope_changed_paths(repo, base), [])
            self.assertEqual(reference.scope_violations([]), [])

            historic = reference.scope_changed_paths(repo, historical)
            self.assertIn("docs/task-evidence/sibling-alpha/report.json",
                          historic)
            self.assertTrue(reference.scope_violations(historic))

    def test_branch_out_of_scope_edit_fails_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._add_siblings(repo)
            self._git(repo, "checkout", "-q", "-b",
                      "swarm/SDK-NARA-WPE-REFERENCE-TOOLS-correction")
            (repo / "CMakeLists.txt").write_text("changed\n", encoding="utf-8")
            self._git(repo, "add", "CMakeLists.txt")
            self._git(repo, "commit", "-qm", "out of scope edit")

            base = reference.scope_base(repo)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, ["CMakeLists.txt"])
            self.assertEqual(reference.scope_violations(paths),
                             ["CMakeLists.txt"])

    def test_missing_base_ref_is_not_silently_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self._repository(Path(temporary))
            self._git(repo, "branch", "-m", "detached-work")
            self.assertIsNone(reference.scope_base(repo))

    def test_live_branch_changes_stay_inside_task_prefix(self) -> None:
        base = reference.scope_base(reference.SDK_ROOT)
        self.assertIsNotNone(base)
        paths = reference.scope_changed_paths(reference.SDK_ROOT, base)
        self.assertEqual(reference.scope_violations(paths), [])
        for path in paths:
            self.assertTrue(path.startswith(reference.TASK_PREFIX), path)


if __name__ == "__main__":
    unittest.main()
