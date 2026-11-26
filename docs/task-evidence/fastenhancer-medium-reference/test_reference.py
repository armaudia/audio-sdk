# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the FastEnhancer Medium reference evidence package."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
REQUIRED_KEYS = {
    "schema_id", "task", "title", "component", "reference_family", "repository",
    "base_commit", "branch", "profile", "status", "evidence_status",
    "qualification_status", "decision", "defer_before",
    "no_missing_result_qualifies_candidate", "qualification", "boundary",
    "format", "task_geometry", "source_pins", "boundary_pins", "artifact_pins",
    "board_link_fields", "board_links", "board_link_projection_sha256",
    "board_mutable_fields_excluded", "acceptance_profile", "required_results",
    "asset", "asset_identity", "asset_admission", "sdk_worktree_asset_probe",
    "runtime", "feasibility", "reference", "candidates", "controls", "harness",
    "adverse", "missing_result", "repeatability", "regressions", "gates",
    "remaining_gates", "independent_timing_evidence", "rights_gap",
    "missing_evidence", "non_claims", "negative_claims", "evidence_classes",
}


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.strict_json(REPORT)
        cls.contract = reference.strict_json(CONTRACT)
        cls.generated = reference.canonical_report_bytes(reference.build_report())

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="utf-8"), f"{digest}  report.json\n")

    def test_03_contract_is_current_canonical_bytes(self) -> None:
        self.assertEqual(CONTRACT.read_bytes(), reference.contract_bytes())
        self.assertEqual(CONTRACT.read_bytes(), reference.canonical_bytes(self.contract) + b"\n")

    def test_04_status_qualification_and_decision(self) -> None:
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertIs(self.report["qualification"]["qualifies_candidate"], False)
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["defer_before"], "processor_exposure")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_05_required_keys_present(self) -> None:
        self.assertFalse(REQUIRED_KEYS - set(self.report))

    def test_06_boundary_is_opt_in_and_unregistered(self) -> None:
        boundary = self.report["boundary"]
        for key in (
            "registered", "enabled_by_default", "default_selected", "public_api_abi_change",
            "provider_registration", "processor_exposure", "c_public_boundary",
            "installed_v0_behavior_changed", "descriptor_or_registry_change",
            "shared_build_or_ci_change", "task_board_or_handoff_change",
            "real_corpus_or_weights_included",
        ):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})
        self.assertIs(boundary["installed_v0_geometry_preserved"], True)

    def test_07_public_v0_geometry_untouched(self) -> None:
        fmt = self.report["format"]
        expected = {
            "sample_rate_hz": 16000, "channels": 1, "sample_format": "f32",
            "frame_samples": 160, "hop_samples": 160, "content_delay_samples": 0,
        }
        for key, value in expected.items():
            self.assertEqual(fmt[key], value)
        self.assertIs(fmt["installed_v0_geometry_preserved"], True)

    def test_08_task_geometry_is_pinned(self) -> None:
        geometry = self.report["task_geometry"]
        self.assertEqual(geometry["native"]["sample_rate_hz"], 48000)
        self.assertEqual(geometry["native"]["analysis_chunk_samples"], 480)
        self.assertEqual(geometry["native"]["native_hop_samples"], 320)
        self.assertEqual(geometry["delay"]["sdk_declared_samples"], 235)
        self.assertEqual(geometry["delay"]["native_samples"], 704)
        self.assertEqual(geometry["execution_modes"], [2, 3])
        self.assertIs(geometry["callback_safe"], False)

    def test_09_base_commit_and_family_pinned(self) -> None:
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["branch"], reference.BRANCH)
        self.assertEqual(self.report["reference_family"], reference.REFERENCE_FAMILY)
        self.assertEqual(self.report["component"], reference.COMPONENT)

    def test_10_board_projection_is_stable_only(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertEqual(self.report["board_links"], links)
        self.assertEqual(self.report["board_link_projection_sha256"], digest)
        self.assertEqual(self.report["board_link_fields"], list(reference.LINK_FIELDS))
        self.assertEqual(
            self.report["board_mutable_fields_excluded"],
            list(reference.MUTABLE_FIELDS_EXCLUDED),
        )
        pinned = [raw for _, raw in reference.parse_pin_lines(PINS.read_text(encoding="utf-8"))]
        self.assertFalse(any("TASKS.json" in raw for raw in pinned))

    def test_11_asset_identity_and_presence(self) -> None:
        asset = self.report["asset"]
        self.assertEqual(asset["asset_id"], "fe.q8")
        self.assertEqual(asset["byte_count"], 565108)
        self.assertEqual(
            asset["sha256"],
            "d6f98e186bee6ed655b52a2edf5f707ccf761c755bb69de8de7f68cad42d7837",
        )
        self.assertEqual(asset["git_blob"], "ab6f8c711d3e23ace911c5e1e11203fadd43ca19")
        self.assertEqual(
            asset["source_revision"], "3e2446fc58886fc02b099b54651adc9a10a65454"
        )
        self.assertIs(asset["present_in_sdk_worktree"], False)
        self.assertIs(asset["bytes_read_by_this_package"], False)
        self.assertIs(asset["download_attempted"], False)
        self.assertEqual(asset["redistribution"], "unknown")
        self.assertEqual(self.report["sdk_worktree_asset_probe"]["found"], [])
        self.assertIs(self.report["sdk_worktree_asset_probe"]["present"], False)

    def test_12_runtime_is_absent_and_not_invoked(self) -> None:
        runtime = self.report["runtime"]
        for key in (
            "present_in_sdk_worktree", "sdk_consumable_runtime_present",
            "onnx_medium_model_present", "native_simd_backend_present_in_sdk_worktree",
            "scalar_runtime_tier_available", "vendor_runtime_invoked",
        ):
            self.assertIs(runtime[key], False, key)

    def test_13_feasibility_and_reference_are_blocked(self) -> None:
        feasibility = self.report["feasibility"]
        self.assertEqual(feasibility["verdict"], "blocked")
        self.assertEqual(feasibility["decision"], "DEFER")
        self.assertIs(feasibility["can_produce_exact_sdk_reference"], False)
        reference_record = self.report["reference"]
        for key in (
            "model_weights", "real_model_inference", "upstream_parity",
            "runtime_invoked", "candidate_output_produced", "downloads",
        ):
            self.assertIs(reference_record[key], False, key)
        self.assertIs(reference_record["deterministic"], True)

    def test_14_candidate_and_missing_result_never_qualify(self) -> None:
        candidate = self.report["candidates"]["fastenhancer_medium"]
        self.assertEqual(candidate["status"], "blocked_assets_and_runtime_absent")
        self.assertIsNone(candidate["metrics"])
        self.assertIs(candidate["qualifies_candidate"], False)
        missing = self.report["missing_result"]
        self.assertEqual(missing["status"], "blocked")
        self.assertIsNone(missing["metrics"])
        self.assertIs(missing["qualifies_candidate"], False)
        self.assertEqual(self.report["regressions"], [])

    def test_15_exactly_eight_blocked_release_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates], reference_gate_ids())
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertEqual(self.report["remaining_gates"], reference_gate_ids())

    def test_16_harness_identity_is_bit_exact_and_passive(self) -> None:
        identity = self.report["harness"]["identity_control"]
        self.assertIs(identity["candidate_processing"], False)
        self.assertIs(identity["all_byte_identical"], True)
        for name in reference.STIMULUS_NAMES:
            self.assertIs(identity["stimuli"][name]["byte_identical"], True, name)
        stimuli = self.report["harness"]["stimuli"]
        self.assertEqual(set(stimuli), set(reference.STIMULUS_NAMES))
        for name, item in stimuli.items():
            self.assertGreater(item["sample_count"], 0, name)
            self.assertEqual(item["nonfinite_count"], 0, name)
            self.assertLessEqual(item["peak_abs"], reference.MAX_ABS_INPUT, name)

    def test_17_invalid_requests_fail_closed(self) -> None:
        cases = self.report["adverse"]["invalid_requests"]
        self.assertGreaterEqual(cases["case_count"], 18)
        self.assertEqual(cases["accepted_count"], 0)
        self.assertIs(cases["all_rejected"], True)
        for item in cases["cases"]:
            self.assertIs(item["accepted"], False, item["id"])
            self.assertIs(item["matches"], True, item["id"])

    def test_18_invalid_json_fails_closed(self) -> None:
        cases = self.report["adverse"]["invalid_json"]
        self.assertEqual(cases["accepted_count"], 0)
        self.assertIs(cases["all_rejected"], True)
        for item in cases["cases"]:
            self.assertIs(item["accepted"], False, item["id"])
        for payload in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '[1,]'):
            with self.assertRaises(ValueError):
                reference.strict_json_loads(payload)

    def test_19_lifecycle_rejections(self) -> None:
        lifecycle = self.report["adverse"]["lifecycle"]
        for key in (
            "closed_process", "finished_process", "stale_reset_epoch",
            "stale_reset_position",
        ):
            self.assertTrue(lifecycle[key].startswith("rejected"), key)
        self.assertEqual(lifecycle["valid_reset"], "ok")
        self.assertIs(lifecycle["invalid_never_advances_state"], True)

    def test_20_asset_admission_rejects_and_mechanism_works(self) -> None:
        admission = self.report["asset_admission"]
        self.assertEqual(admission["status"], "blocked")
        self.assertIs(admission["asset_bytes_read"], False)
        self.assertIs(admission["download_attempted"], False)
        self.assertIs(admission["all_rejections_fail_closed"], True)
        self.assertIs(admission["admission_mechanism_verified_with_synthetic_spec"], True)
        self.assertEqual(reference.admit_asset(None), "ASSET_MISSING")
        self.assertEqual(reference.admit_asset(b""), "ASSET_SIZE_MISMATCH")
        self.assertEqual(reference.admit_asset(b"\x00" * reference.ASSET["byte_count"]),
                         "ASSET_DIGEST_MISMATCH")
        spec = {"byte_count": 4, "sha256": hashlib.sha256(b"abcd").hexdigest()}
        self.assertEqual(reference.admit_asset(b"abcd", spec), "ASSET_ADMITTED")

    def test_21_repeatability_is_byte_identical(self) -> None:
        repeats = self.report["repeatability"]
        self.assertEqual(repeats["count"], 3)
        self.assertIs(repeats["byte_identical"], True)
        self.assertEqual(len(set(repeats["digests"])), 1)

    def test_22_acceptance_profile_mapped(self) -> None:
        acceptance = self.report["acceptance_profile"]
        self.assertEqual(acceptance["profile"], "enhancement")
        for case in (
            "identity_noisy_control", "established_task_matched_baseline",
            "paired_si_sdr_stoi", "clean_speech_preservation",
            "peaks_and_invalid_outputs", "unpaired_speech",
            "alignment_state_memory_timing",
        ):
            self.assertIn(case, acceptance["mapped_cases"])
        self.assertEqual(
            acceptance["mapped_cases"]["paired_si_sdr_stoi"]["status"],
            "blocked_no_candidate_output",
        )
        self.assertFalse(any(
            item.get("candidate_scored") for item in acceptance["mapped_cases"].values()
            if isinstance(item, dict)
        ))

    def test_23_rights_and_timing_gaps_are_blocked(self) -> None:
        rights = self.report["rights_gap"]
        self.assertIs(rights["blocked"], True)
        self.assertIs(rights["redistribution_cleared"], False)
        self.assertIs(rights["model_weight_terms_verified"], False)
        timing = self.report["independent_timing_evidence"]
        self.assertIs(timing["used_for_qualification"], False)
        self.assertIs(timing["measured_here"], False)
        self.assertIs(timing["target_device"], False)
        for key, value in self.report["negative_claims"].items():
            self.assertIs(value, False, key)

    def test_24_no_negative_zero_or_nonfinite_in_report(self) -> None:
        for token in (b"-0.0", b"NaN", b"Infinity"):
            self.assertNotIn(token, self.generated)

    def test_25_pin_parser_rejects_invalid_lines(self) -> None:
        for bad in (
            "not-a-line",
            "Z" * 64 + "  docs/task-evidence/fastenhancer-medium-reference/x",
            "a" * 64 + "  source:../escape",
            "a" * 64 + "  worktree:../escape",
            "a" * 64 + "  unknown/x",
            "a" * 64 + "  audio-benchmark-platform/plan/swarm/TASKS.json",
        ):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(bad)
        duplicate = "\n".join([
            "a" * 64 + "  docs/task-evidence/fastenhancer-medium-reference/x",
            "a" * 64 + "  docs/task-evidence/fastenhancer-medium-reference/x",
        ])
        with self.assertRaises(ValueError):
            reference.parse_pin_lines(duplicate)

    def test_26_all_pins_match_bytes(self) -> None:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="utf-8"))
        self.assertTrue(pins)
        for digest, raw in pins:
            self.assertEqual(reference.sha256(reference.pin_path(raw).read_bytes()), digest, raw)
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())

    def test_27_manifest_covers_every_package_file(self) -> None:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="utf-8"))
        names = {Path(raw).name for _, raw in pins}
        for name in reference.EXPECTED_FILES:
            if name != "SOURCES.sha256":
                self.assertIn(name, names, name)

    def test_28_license_headers_and_sidecars(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn(reference.SPDX_LICENSE_LINE, head, path.name)
            self.assertIn(reference.SPDX_COPYRIGHT_LINE, head, path.name)
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"<!-- {reference.SPDX_COPYRIGHT_LINE} -->", readme)
        self.assertIn(f"<!-- {reference.SPDX_LICENSE_LINE} -->", readme)
        for name in (
            "contract.json.license", "report.json.license",
            "report.json.sha256.license", "SOURCES.sha256.license",
        ):
            self.assertEqual((HERE / name).read_text(encoding="utf-8"), reference.LICENSE_TEXT)

    def test_29_no_trailing_whitespace(self) -> None:
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.suffix in {".py", ".json", ".md", ".sha256", ".license"}:
                for number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), 1
                ):
                    self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_30_scope_is_task_local(self) -> None:
        result = subprocess.run(
            ["git", "-C", str(reference.SDK_ROOT), "status", "--porcelain=v1",
             "--untracked-files=all"],
            capture_output=True, text=True, check=True,
        )
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(reference.TASK_PREFIX + "/"), path)

    def test_31_three_cold_start_passes(self) -> None:
        code = (
            "import sys; sys.path.insert(0, " + repr(str(HERE)) + "); "
            "import reference; sys.stdout.write(reference.sha256("
            "reference.canonical_report_bytes(reference.build_report())))"
        )
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        digests = []
        for _ in range(3):
            result = subprocess.run(
                [sys.executable, "-c", code], cwd=HERE, env=env,
                capture_output=True, text=True, check=True,
            )
            digests.append(result.stdout.strip())
        self.assertEqual(len(set(digests)), 1)
        self.assertEqual(digests[0], hashlib.sha256(REPORT.read_bytes()).hexdigest())

    def test_32_strict_json_rejects_duplicates_and_nonfinite(self) -> None:
        for payload in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with tempfile.NamedTemporaryFile(
                "w", suffix=".json", encoding="utf-8", delete=False
            ) as handle:
                handle.write(payload)
                path = Path(handle.name)
            try:
                with self.assertRaises(ValueError):
                    reference.strict_json(path)
            finally:
                path.unlink()

    def test_33_file_set_is_exact(self) -> None:
        actual = sorted(path.name for path in HERE.iterdir() if path.is_file())
        self.assertEqual(actual, sorted(reference.EXPECTED_FILES))


def reference_gate_ids() -> list[str]:
    return ["RG-0" + str(number) for number in range(1, 9)]


if __name__ == "__main__":
    unittest.main()
