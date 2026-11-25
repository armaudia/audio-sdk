# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the FastEnhancer source-linked wrapper evidence package."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import reference
import scorer

HERE = Path(__file__).resolve().parent
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
ADAPTER = HERE / "adapter.json"
PROVIDER = HERE / "provider.json"
REQUIRED_KEYS = {
    "schema_id", "task_id", "component_id", "reference_family", "base_commit", "profile",
    "status", "qualification_status", "decision", "evidence_status", "scope", "boundary",
    "format", "source_pins", "boundary_pins", "artifact_pins", "acceptance_profile",
    "conditions", "controls", "adverse", "repeatability", "regressions", "gates",
    "independent_timing_evidence", "rights_gap", "scorer", "missing_evidence",
    "negative_claims", "evidence_classes",
}


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.strict_json(REPORT)
        cls.contract = reference.strict_json(CONTRACT)
        cls.adapter = reference.strict_json(ADAPTER)
        cls.provider = reference.strict_json(PROVIDER)
        cls.generated = reference.canonical_report_bytes(reference.build_report())

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="utf-8"), f"{digest}  report.json\n")

    def test_03_status_and_qualification(self) -> None:
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_04_boundary_is_opt_in_and_unregistered(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration", "processor_exposure",
                    "c_public_boundary"):
            self.assertIs(boundary[key], False)
        self.assertEqual(boundary["descriptor_settings"], {})
        self.assertIs(self.provider["registered"], False)
        self.assertIs(self.provider["enabled_by_default"], False)
        self.assertIs(self.adapter["registered"], False)

    def test_05_public_v0_geometry_untouched(self) -> None:
        fmt = self.report["format"]
        expected = {"sample_rate_hz": 16000, "channels": 1, "sample_format": "f32",
                    "frame_samples": 160, "hop_samples": 160, "content_delay_samples": 0}
        for key, value in expected.items():
            self.assertEqual(fmt[key], value)
        self.assertIs(fmt["installed_v0_geometry_preserved"], True)

    def test_06_required_keys_present(self) -> None:
        self.assertFalse(REQUIRED_KEYS - set(self.report))

    def test_07_base_commit_and_identity_pinned(self) -> None:
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["reference_family"], reference.REFERENCE_FAMILY)
        self.assertEqual(self.report["component_id"], reference.COMPONENT_ID)
        source_pin = reference.SOURCE_PINS["source:cpp-library/src/stages/fastenhancer.cpp"]
        self.assertEqual(self.contract["source_identity"]["sha256"], source_pin)
        self.assertEqual(self.adapter["source_sha256"], source_pin)

    def test_08_all_conditions_scored(self) -> None:
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for value in self.report["conditions"].values():
            self.assertIn("baseline_metrics", value)
            self.assertIn("candidate_metrics", value)
            self.assertIn("frame_run", value)

    def test_09_controls_all_present(self) -> None:
        controls = self.report["controls"]
        self.assertTrue(controls["all_present"])
        for name in ("identity", "named_baseline", "candidate", "clean_speech_preservation"):
            self.assertEqual(controls[name]["status"], "measured_synthetic")
        self.assertEqual(controls["named_baseline"]["name"], "noisy_input_no_processing")

    def test_10_adverse_cases_fail_closed(self) -> None:
        adverse = self.report["adverse"]
        for value in adverse["config_rejections"].values():
            self.assertTrue(value["status"].startswith("rejected"))
            self.assertFalse(value["controller_created"])
        for name, status in adverse["frame_rejections"].items():
            if name != "dsp_state_unchanged":
                self.assertTrue(status.startswith("rejected"), name)
        self.assertIs(adverse["frame_rejections"]["dsp_state_unchanged"], True)
        self.assertTrue(all(value.startswith("rejected") for value in (
            adverse["lifecycle"]["close_then_process"],
            adverse["lifecycle"]["finish_then_process"],
            adverse["lifecycle"]["stale_reset_epoch"],
            adverse["lifecycle"]["stale_reset_position"],
        )))
        self.assertEqual(adverse["lifecycle"]["valid_reset"], "ok")

    def test_11_repeatability_is_byte_identical(self) -> None:
        repeats = self.report["repeatability"]
        self.assertEqual(repeats["count"], 3)
        self.assertTrue(repeats["byte_identical"])
        self.assertEqual(len(set(repeats["digests"])), 1)

    def test_12_regressions_recorded_verbatim(self) -> None:
        self.assertIsInstance(self.report["regressions"], list)
        for item in self.report["regressions"]:
            self.assertIn("condition", item)
            self.assertIn("candidate", item)
            self.assertIn("baseline", item)

    def test_13_gates_all_blocked(self) -> None:
        self.assertTrue(self.report["gates"])
        self.assertTrue(all(gate["status"] == "blocked" for gate in self.report["gates"]))
        names = {gate["name"] for gate in self.report["gates"]}
        self.assertIn("upstream_source_model_runtime_rights", names)

    def test_14_no_negative_zero_in_canonical_report(self) -> None:
        self.assertNotIn(b"-0.0", self.generated)
        self.assertNotIn(b"NaN", self.generated)
        self.assertNotIn(b"Infinity", self.generated)

    def test_15_manifest_covers_task_files(self) -> None:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="utf-8"))
        names = {Path(raw.split(":", 1)[-1]).name for _, raw in pins}
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.name != "SOURCES.sha256":
                self.assertIn(path.name, names)
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())

    def test_16_no_trailing_whitespace(self) -> None:
        suffix = {".py", ".json", ".md", ".sha256", ".license"}
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.suffix in suffix:
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_17_deterministic_transform(self) -> None:
        _, observed = reference.synth("identity")
        self.assertEqual(reference.candidate_transform(observed),
                         reference.candidate_transform(observed))

    def test_18_scope_is_task_local(self) -> None:
        result = subprocess.run(["git", "-C", str(reference.SDK_ROOT), "status", "--porcelain=v1",
                                 "--untracked-files=all"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(reference.TASK_REL + "/"), path)

    def test_19_pin_parser_rejects_invalid_lines(self) -> None:
        for bad in ("not-a-line", "Z" * 64 + "  docs/x", "a" * 64 + "  ../escape",
                    "a" * 64 + "  unknown/x"):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(bad)
        duplicate = "\n".join([f"{'a' * 64}  docs/x", f"{'a' * 64}  docs/x"])
        with self.assertRaises(ValueError):
            reference.parse_pin_lines(duplicate)

    def test_20_contract_and_manifests_are_consistent(self) -> None:
        self.assertEqual(self.contract["verification_profile"], "enhancement")
        self.assertEqual(self.contract["frontend_contract"]["identity"],
                         "audio-sdk/v0-f32-16k-mono-160")
        self.assertIs(self.contract["frontend_contract"]["public_api_abi_changed"], False)
        self.assertIs(self.provider["registered"], False)
        self.assertIs(self.provider["enabled_by_default"], False)
        self.assertEqual(self.provider["descriptor_settings"], {})
        for name in ("adapter", "provider"):
            path = HERE / f"{name}.json"
            self.assertEqual(path.read_bytes(),
                             reference.canonical_bytes(reference.strict_json(path)) + b"\n")

    def test_21_acceptance_profile_mapped_cases(self) -> None:
        acceptance = self.report["acceptance_profile"]
        self.assertEqual(acceptance["profile"], "enhancement")
        for case in ("identity_noisy_control", "established_task_matched_baseline",
                     "paired_si_sdr_stoi", "clean_speech_preservation",
                     "peaks_and_invalid_outputs", "unpaired_speech",
                     "alignment_state_memory_timing"):
            self.assertIn(case, acceptance["mapped_cases"])

    def test_22_rights_and_timing_gaps_are_blocked(self) -> None:
        self.assertIs(self.report["rights_gap"]["blocked"], True)
        self.assertIs(self.report["rights_gap"]["model_weight_terms_verified"], False)
        timing = self.report["independent_timing_evidence"]
        self.assertIs(timing["used_for_qualification"], False)
        self.assertIs(timing["measured_here"], False)
        self.assertEqual(len(timing["preset_references"]), 4)
        negatives = self.report["negative_claims"]
        for key in ("real_model_weights", "real_media", "device_timing", "listening_result",
                    "benchmark_claim", "release_claim", "onnx_runtime_invoked"):
            self.assertIs(negatives[key], False)

    def test_23_three_cold_start_passes(self) -> None:
        code = ("import sys; sys.path.insert(0, " + repr(str(HERE)) + "); "
                "import reference; sys.stdout.write("
                "reference.sha256(reference.canonical_report_bytes(reference.build_report())))")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        digests = []
        for _ in range(3):
            result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                    capture_output=True, text=True, check=True)
            digests.append(result.stdout.strip())
        self.assertEqual(len(set(digests)), 1)
        self.assertEqual(digests[0], hashlib.sha256(REPORT.read_bytes()).hexdigest())

    def test_24_scorer_inheritance(self) -> None:
        prior = reference.SDK_ROOT / "docs/task-evidence/online-multichannel-wpe/scorer.py"
        expected = prior.read_text(encoding="utf-8").replace(
            'SCORER_ID = "audio-sdk/online-multichannel-wpe-scoring/0.1"',
            f'SCORER_ID = "{scorer.SCORER_ID}"')
        self.assertEqual((HERE / "scorer.py").read_text(encoding="utf-8"), expected)
        self.assertFalse(self.report["scorer"]["used_as_oracle"])

    def test_25_strict_json_rejects_duplicates_and_nonfinite(self) -> None:
        for payload in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                             delete=False) as handle:
                handle.write(payload)
                path = Path(handle.name)
            try:
                with self.assertRaises(ValueError):
                    reference.strict_json(path)
            finally:
                path.unlink()

    def test_26_invalid_configs_are_rejected(self) -> None:
        for config in ({}, {"model": reference.CONFIG["model"], "extra": 1},
                       {"model": 7}, {"model": float("nan")}, {"model": "unknown"}):
            created = reference.create_controller(config)
            self.assertIsNone(created["controller"])
            self.assertTrue(created["status"].startswith("rejected"))

    def test_27_all_pins_match_bytes(self) -> None:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="utf-8"))
        for digest, raw in pins:
            self.assertEqual(reference.sha256(reference.pin_path(raw).read_bytes()), digest)


if __name__ == "__main__":
    unittest.main()
