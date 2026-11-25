# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance checks for the evidence package."""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import unittest
from pathlib import Path

import reference
import run as cli
import verify

HERE = Path(__file__).resolve().parent
SDK_ROOT = reference.SDK_ROOT
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
TASK_PREFIX = f"docs/task-evidence/{reference.SLUG}/"


def strict_json(path: Path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise AssertionError(f"duplicate JSON key in {path.name}: {key}")
            result[key] = value
        return result

    def constant(token):
        raise AssertionError(f"nonfinite JSON constant in {path.name}: {token}")

    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=constant)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = strict_json(REPORT)
        cls.contract = strict_json(HERE / "contract.json")
        cls.adapter = strict_json(HERE / "adapter.json")
        cls.provider = strict_json(HERE / "provider.json")
        cls.generated = reference.canonical_report_bytes(reference.build_report())
        cls.digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()

    def test_01_report_regenerates_byte_identically(self):
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self):
        self.assertEqual(SIDECAR.read_text(encoding="utf-8").strip(),
                         f"{self.digest}  report.json")

    def test_03_manifest_regenerates_byte_identically(self):
        self.assertEqual(PINS.read_bytes(), cli.manifest_bytes())

    def test_04_manifest_is_fail_closed(self):
        manifest = verify.read_manifest()
        self.assertEqual(set(manifest), verify.manifest_expected_paths())
        self.assertNotIn("worktree:" + TASK_PREFIX + "SOURCES.sha256", manifest)

    def test_05_all_json_is_strict(self):
        for path in sorted(HERE.glob("*.json")):
            self.assertIsInstance(strict_json(path), dict)

    def test_06_status_qualification_and_decision(self):
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_07_boundary_is_unregistered_and_default_off(self):
        boundary = self.report["boundary"]
        for key, value in reference.BOUNDARY.items():
            self.assertEqual(boundary[key], value, key)

    def test_08_public_v0_geometry_is_unchanged(self):
        self.assertEqual(self.report["format"], reference.FORMAT)
        self.assertEqual(self.report["format"]["sample_rate_hz"], 16000)
        self.assertEqual(self.report["format"]["channels"], 1)
        self.assertEqual(self.report["format"]["sample_format"], "f32")
        self.assertEqual(self.report["format"]["frame_samples"], 160)

    def test_09_required_report_keys_present(self):
        for key in ("schema_id", "task_id", "base_commit", "branch", "profile",
                    "conditions", "controls", "ablations", "regressions", "adverse",
                    "repeatability", "pipeline_profile", "gates", "missing_evidence",
                    "scope", "tool_provenance", "claims", "extra"):
            self.assertIn(key, self.report)

    def test_10_base_commit_and_branch_pinned(self):
        self.assertEqual(self.report["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(self.report["branch"], reference.BRANCH)

    def test_11_all_conditions_and_variants_scored(self):
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for condition in self.report["conditions"].values():
            self.assertEqual(set(condition["variants"]), set(reference.STAGE_CHAINS))
            for variant in condition["variants"].values():
                for name in ("mean_abs_error", "max_abs_error", "rmse", "peak_abs_output"):
                    self.assertTrue(math.isfinite(variant["metrics"][name]))
                self.assertFalse(variant["metrics"]["clipped"])

    def test_12_matched_controls_present(self):
        controls = self.report["controls"]
        self.assertTrue(controls["all_present"])
        self.assertTrue(controls["identity"]["exact_passthrough"])
        self.assertEqual(controls["named_baseline"]["name"], "noisy_input_no_processing")
        self.assertEqual(controls["candidate"]["name"], "full_chain_surrogate")

    def test_13_stage_removed_ablations_present(self):
        for condition, ablation in self.report["ablations"].items():
            self.assertEqual(set(ablation["stage_removed"]), set(reference.ABLATIONS), condition)

    def test_14_adverse_config_cases_fail_closed(self):
        rejections = self.report["adverse"]["config_rejections"]
        self.assertTrue(all(case["status"].startswith("rejected") for case in rejections.values()))
        self.assertTrue(all(case["controller_created"] is False for case in rejections.values()))

    def test_15_adverse_frame_lifecycle_validity_fail_closed(self):
        adverse = self.report["adverse"]
        self.assertTrue(adverse["frame_rejections"]["dsp_state_unchanged"])
        self.assertTrue(all(status == "rejected_session"
                            for status in adverse["lifecycle"].values()))
        self.assertTrue(all(adverse["validity"].values()))
        self.assertTrue(all(adverse["failure_policy"].values()))

    def test_16_repeatability_is_byte_identical(self):
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)

    def test_17_regressions_recorded_verbatim(self):
        self.assertTrue(self.report["regressions"])
        for item in self.report["regressions"]:
            self.assertEqual(item["metric"], "mean_abs_error")
            self.assertGreater(item["candidate"], item["noisy_control"])

    def test_18_all_gates_remain_blocked(self):
        self.assertTrue(self.report["gates"])
        self.assertTrue(all(gate["status"] == "blocked" for gate in self.report["gates"]))
        names = {gate["name"] for gate in self.report["gates"]}
        self.assertIn("checkpoint_config_rights", names)
        self.assertIn("exact_reference_parity", names)

    def test_19_no_negative_zero_in_canonical_report(self):
        self.assertNotIn(b"-0.0", self.generated)

    def test_20_no_trailing_whitespace(self):
        for path in sorted(HERE.iterdir()):
            if not path.is_file() or path.suffix not in {".py", ".json", ".md", ".sha256", ".license"}:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")

    def test_21_deterministic_transform(self):
        _, observed = reference.synth("fan_hum")
        first = reference.apply_chain("full_chain_surrogate", observed)
        second = reference.apply_chain("full_chain_surrogate", observed)
        self.assertEqual(first, second)
        self.assertEqual(len(first), reference.SAMPLE_COUNT)

    def test_22_documented_chain_and_pin_paths(self):
        self.assertEqual(self.report["profile"], "pipeline")
        self.assertEqual(self.report["extra"]["documented_owner_preference_date"], "2026-10-31")
        self.assertEqual(self.report["extra"]["dated_prototype_choice"], "2026-11-24-local-only")
        self.assertFalse(self.report["extra"]["live_default"])
        self.assertFalse(self.report["extra"]["task_board_handoff_written"])
        self.assertEqual(set(self.report["source_pin_paths"]), set(reference.SOURCE_PIN_PATHS))

    def test_23_pipeline_profile_complete(self):
        profile = self.report["pipeline_profile"]
        self.assertEqual(set(profile), verify.PIPELINE_KEYS)
        self.assertEqual(profile["stage_order"], list(reference.STAGE_ORDER))
        self.assertEqual(set(profile["matched_controls"]), set(reference.MATCHED_CONTROLS))
        self.assertEqual(set(profile["stage_removed_ablations"]), set(reference.ABLATIONS))
        self.assertEqual(len(profile["documented_comparison_order"]["reverberant_room"]), 7)

    def test_24_timing_and_workload_are_unmeasured(self):
        profile = self.report["pipeline_profile"]
        for key in ("end_to_end_clock", "paced_workload", "stage_timing_independent"):
            self.assertTrue(profile[key]["status"].startswith("blocked"))
            self.assertFalse(profile[key]["measured"])

    def test_25_exact_checkpoint_and_rights_blockers(self):
        chain = self.contract["documented_chain"]
        self.assertEqual(chain["artifact_identity"]["checkpoint_sha256"],
                         "23b92884f63ccf54bb026014604625ab231657b6480df65db4095c4c171e6003")
        self.assertEqual(chain["artifact_identity"]["config_sha256"],
                         "415eb925d44990d938fb739f514aa3662c1ec0ea836cff044fa1291b82cb4290")
        self.assertEqual(chain["artifact_identity"]["checkpoint_terms"],
                         "unclear; see upstream issue #712")
        text = " ".join(chain["checkpoint_blockers"])
        self.assertIn("SDK-DEEPFILTERNET3-V0-5-6 remains blocked", text)
        self.assertIn("no weights accessed", text)

    def test_26_contract_adapter_provider_key_sets(self):
        self.assertEqual(set(self.contract), verify.CONTRACT_KEYS)
        self.assertEqual(set(self.adapter), verify.ADAPTER_KEYS)
        self.assertEqual(set(self.provider), verify.PROVIDER_KEYS)

    def test_27_disposition_files_are_defer_and_off(self):
        for document in (self.contract, self.adapter, self.provider):
            self.assertEqual(document["decision"], "DEFER")
        self.assertFalse(self.adapter["registered"])
        self.assertFalse(self.adapter["enabled_by_default"])
        self.assertFalse(self.provider["registered"])
        self.assertFalse(self.provider["enabled_by_default"])
        self.assertTrue(self.provider["opt_in_required"])
        self.assertFalse(self.contract["qualification"]["qualifies"])

    def test_28_no_real_world_claims(self):
        self.assertTrue(all(value is False for value in self.report["claims"].values()))
        profile = self.report["pipeline_profile"]
        self.assertFalse(profile["asset_scope"]["weights_accessed"])
        self.assertFalse(profile["asset_scope"]["vendor_runtime_invoked"])
        self.assertFalse(profile["asset_scope"]["model_downloaded"])

    def test_29_external_pins_match_contract(self):
        manifest = verify.read_manifest()
        source_pins = {key: value for key, value in manifest.items() if key.startswith("source:")}
        boundary_pins = {key: value for key, value in manifest.items()
                         if key in reference.BOUNDARY_PIN_PATHS}
        self.assertEqual(self.contract["source_pins"], source_pins)
        self.assertEqual(self.contract["boundary_pins"], boundary_pins)

    def test_30_three_cold_starts_are_byte_identical(self):
        code = ("import hashlib,reference; print(hashlib.sha256("
                "reference.canonical_report_bytes(reference.build_report())).hexdigest())")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        digests = []
        for _ in range(3):
            result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            digests.append(result.stdout.strip())
        self.assertEqual(set(digests), {self.digest})

    def test_31_licensing_check_passes(self):
        result = subprocess.run([sys.executable, "check_licensing.py"], cwd=HERE,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_32_verify_passes(self):
        result = subprocess.run([sys.executable, "verify.py"], cwd=HERE,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_33_scope_is_task_local(self):
        result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                                 "--untracked-files=all"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            path = line[3:] if len(line) > 3 else ""
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path:
                self.assertTrue(path.startswith(TASK_PREFIX), path)


if __name__ == "__main__":
    unittest.main()
